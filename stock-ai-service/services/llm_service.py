"""LLM Service for unified access to different LLM providers"""

import json
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import asyncio
import time

# AWS Bedrock imports
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False

# OpenAI imports (fallback)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from config import get_llm_config

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured"""
        pass


class BedrockProvider(LLMProvider):
    """AWS Bedrock provider for Claude models"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_id = config.get("bedrock_model_id", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 4000)
        self.client = None
        
        if BEDROCK_AVAILABLE:
            try:
                # Create Bedrock client
                session_kwargs = {
                    "region_name": config.get("region_name", "ap-southeast-1")
                }
                
                # Add credentials if provided
                if config.get("aws_access_key_id") and config.get("aws_secret_access_key"):
                    session_kwargs.update({
                        "aws_access_key_id": config.get("aws_access_key_id"),
                        "aws_secret_access_key": config.get("aws_secret_access_key")
                    })
                
                session = boto3.Session(**session_kwargs)
                self.client = session.client("bedrock-runtime")
                
                logger.info(f"Initialized Bedrock client with model: {self.model_id}")
                
            except Exception as e:
                logger.error(f"Failed to initialize Bedrock client: {e}")
                self.client = None
    
    def is_available(self) -> bool:
        """Check if Bedrock is available and configured"""
        if not BEDROCK_AVAILABLE:
            logger.warning("boto3 not available, cannot use Bedrock")
            return False
        
        if not self.client:
            return False
        
        try:
            # Test the connection with a simple model info call
            # Use bedrock client (not runtime) for listing models
            session_kwargs = {
                "region_name": self.config.get("region_name", "us-east-1")
            }
            
            if self.config.get("aws_access_key_id") and self.config.get("aws_secret_access_key"):
                session_kwargs.update({
                    "aws_access_key_id": self.config.get("aws_access_key_id"),
                    "aws_secret_access_key": self.config.get("aws_secret_access_key")
                })
            
            session = boto3.Session(**session_kwargs)
            bedrock_client = session.client("bedrock")
            bedrock_client.list_foundation_models()
            return True
        except Exception as e:
            logger.error(f"Bedrock not available: {e}")
            return False
    
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate response using Bedrock Claude"""
        if not self.client:
            raise RuntimeError("Bedrock client not initialized")
        
        try:
            # Prepare messages for Claude
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user", 
                "content": prompt
            })
            
            # Prepare request body for Claude
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "messages": messages
            }
            
            # Add system prompt if provided (Claude 3 format)
            if system_prompt:
                body["system"] = system_prompt
                # Remove system message from messages array for Claude 3
                messages = [msg for msg in messages if msg["role"] != "system"]
                body["messages"] = messages
            
            logger.info(f"Making Bedrock request to {self.model_id}")
            
            # Make the request
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            if 'content' in response_body and response_body['content']:
                content = response_body['content'][0]
                if content.get('type') == 'text':
                    return content['text']
            
            # Fallback for different response formats
            if 'completion' in response_body:
                return response_body['completion']
            
            raise ValueError("Unexpected response format from Bedrock")
            
        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            raise RuntimeError(f"Bedrock API error: {e}")
        except Exception as e:
            logger.error(f"Error generating Bedrock response: {e}")
            raise RuntimeError(f"Error generating response: {e}")


class OpenAIProvider(LLMProvider):
    """OpenAI provider (fallback)"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = config.get("model", "gpt-3.5-turbo")
        self.temperature = config.get("temperature", 0.7)
        
        if OPENAI_AVAILABLE and config.get("api_key"):
            openai.api_key = config.get("api_key")
            logger.info(f"Initialized OpenAI client with model: {self.model}")
    
    def is_available(self) -> bool:
        """Check if OpenAI is available and configured"""
        if not OPENAI_AVAILABLE:
            return False
        
        return bool(self.config.get("api_key"))
    
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate response using OpenAI"""
        if not OPENAI_AVAILABLE:
            raise RuntimeError("OpenAI not available")
        
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", 4000)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            raise RuntimeError(f"Error generating response: {e}")


class LLMService:
    """Unified LLM service that manages different providers"""
    
    def __init__(self):
        self.config = get_llm_config()
        self.provider = None
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the appropriate LLM provider"""
        provider_type = self.config.get("provider", "bedrock")
        
        if provider_type == "bedrock":
            self.provider = BedrockProvider(self.config)
            if not self.provider.is_available():
                logger.warning("Bedrock not available, falling back to OpenAI")
                self.provider = OpenAIProvider(self.config)
        else:
            self.provider = OpenAIProvider(self.config)
            if not self.provider.is_available():
                logger.warning("OpenAI not available, trying Bedrock")
                self.provider = BedrockProvider(self.config)
        
        if not self.provider or not self.provider.is_available():
            raise RuntimeError("No LLM provider available")
        
        logger.info(f"Using LLM provider: {type(self.provider).__name__}")
    
    async def generate_analysis(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        agent_type: str = "general",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate analysis using the configured LLM provider"""
        
        start_time = time.time()
        
        try:
            response = await self.provider.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                **kwargs
            )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return {
                "analysis": response,
                "processing_time_ms": processing_time,
                "agent_type": agent_type,
                "model": getattr(self.provider, 'model_id', getattr(self.provider, 'model', 'unknown')),
                "provider": type(self.provider).__name__
            }
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            raise
    
    async def generate_financial_analysis(self, symbol: str, market_data: Dict, **kwargs) -> Dict[str, Any]:
        """Generate financial analysis for a stock"""
        system_prompt = """You are a senior financial analyst with 20+ years of experience in equity research. 
        Analyze the provided stock data and market information to provide comprehensive financial insights.
        Focus on:
        - Financial health and performance metrics
        - Valuation analysis
        - Revenue and earnings trends
        - Competitive positioning
        - Investment recommendation
        
        Be specific, data-driven, and provide actionable insights."""
        
        prompt = f"""
        Analyze {symbol} based on the following market data:
        
        {json.dumps(market_data, indent=2)}
        
        Provide a comprehensive financial analysis including:
        1. Financial health assessment
        2. Valuation analysis (if data available)
        3. Performance trends
        4. Key strengths and risks
        5. Investment recommendation with rationale
        """
        
        return await self.generate_analysis(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="finance_guru",
            **kwargs
        )
    
    async def generate_portfolio_analysis(self, portfolio_data: List[Dict], **kwargs) -> Dict[str, Any]:
        """Generate portfolio analysis"""
        system_prompt = """You are a portfolio management expert specializing in risk analysis and asset allocation.
        Analyze the provided portfolio composition and provide comprehensive insights on:
        - Portfolio diversification
        - Risk assessment
        - Sector allocation balance
        - Correlation analysis
        - Optimization recommendations
        
        Provide actionable recommendations for portfolio improvement."""
        
        portfolio_summary = "\n".join([
            f"- {stock['symbol']}: {stock['allocation']}% allocation"
            for stock in portfolio_data
        ])
        
        prompt = f"""
        Analyze the following portfolio composition:
        
        {portfolio_summary}
        
        Provide comprehensive portfolio analysis including:
        1. Diversification assessment
        2. Risk profile analysis
        3. Sector/geographic distribution
        4. Correlation risks
        5. Optimization recommendations
        6. Overall portfolio grade and rationale
        """
        
        return await self.generate_analysis(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="portfolio_analyst",
            **kwargs
        )


# Global LLM service instance
llm_service = None

def get_llm_service() -> LLMService:
    """Get or create the global LLM service instance"""
    global llm_service
    if llm_service is None:
        llm_service = LLMService()
    return llm_service