import time
from typing import Dict, Any
from .state import StockAnalysisState, AgentAnalysis
import json
import logging
from datetime import datetime, timedelta, timezone
import yfinance as yf
import sys
import os

# Add parent directory to sys.path to import config and services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from services.llm_service import get_llm_service

logger = logging.getLogger(__name__)

class BaseStockAgent:
    """Base class for all stock analysis agents"""
    
    def __init__(self, agent_name: str, agent_type: str):
        self.agent_name = agent_name
        self.agent_type = agent_type
        try:
            self.llm_service = get_llm_service()
            logger.info(f"Initialized {agent_name} with LLM service")
        except Exception as e:
            logger.error(f"Failed to initialize LLM service for {agent_name}: {e}")
            self.llm_service = None
    
    def _parse_response(self, response_content: str) -> Dict[str, Any]:
        """Parse LLM response into structured data"""
        try:
            if "```json" in response_content:
                json_str = response_content.split("```json")[1].split("```")[0].strip()
            elif "{" in response_content and "}" in response_content:
                start = response_content.find("{")
                end = response_content.rfind("}") + 1
                json_str = response_content[start:end]
            else:
                raise ValueError("No JSON found in response")
            
            return json.loads(json_str)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return {
                "analysis": response_content,
                "confidence": 0.5,
                "key_factors": ["parsing_error"]
            }
        except Exception as e:
            logger.error(f"Unexpected error parsing response: {e}")
            return {
                "analysis": response_content,
                "confidence": 0.5,
                "key_factors": ["unknown_error"]
            }
    
    def get_stock_data(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """Fetch basic stock data for analysis"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            info = stock.info
            
            return {
                "current_price": hist['Close'].iloc[-1] if len(hist) > 0 else None,
                "price_change_1d": (hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) if len(hist) > 1 else None,
                "price_change_pct": ((hist['Close'].iloc[-1] / hist['Close'].iloc[-2]) - 1) * 100 if len(hist) > 1 else None,
                "volume": hist['Volume'].iloc[-1] if len(hist) > 0 else None,
                "market_cap": info.get('marketCap'),
                "pe_ratio": info.get('trailingPE'),
                "company_name": info.get('longName'),
                "sector": info.get('sector'),
                "industry": info.get('industry'),
                "52_week_high": info.get('fiftyTwoWeekHigh'),
                "52_week_low": info.get('fiftyTwoWeekLow'),
                "avg_volume": info.get('averageVolume'),
                "beta": info.get('beta')
            }
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return {"error": str(e)}

class FinanceGuruAgent(BaseStockAgent):
    """Finance expert agent analyzing financial metrics and market conditions"""
    
    def __init__(self):
        super().__init__("Finance Guru", "finance_guru")
    
    async def analyze(self, state: StockAnalysisState) -> StockAnalysisState:
        """Perform financial analysis"""
        start_time = time.time()
        logger.info(f"Finance Guru analyzing {state['request'].symbol}")
        
        try:
            symbol = state['request'].symbol
            stock_data = self.get_stock_data(symbol)
            
            prompt = f"""
            Analyze the stock {symbol} for investment potential.
            
            Stock Data:
            {json.dumps(stock_data, indent=2, default=str)}
            
            Time Frame: {state['request'].time_frequency}
            
            Provide a comprehensive financial analysis covering:
            1. Financial health and key metrics
            2. Valuation assessment (overvalued/undervalued)
            3. Revenue and earnings trends
            4. Competitive position
            5. Investment recommendation with reasoning
            
            Focus on fundamental analysis and financial performance indicators.
            Be specific about numbers and provide clear reasoning.
            
            Respond in JSON format:
            {{
                "analysis": "detailed financial analysis",
                "confidence": 0.85,
                "key_factors": ["factor1", "factor2", "factor3"],
                "recommendation": "buy/hold/sell",
                "price_target_reasoning": "explanation of price movement expectations"
            }}
            """
            
            system_prompt = "You are a senior financial analyst with 20+ years of experience in equity research and valuation."
            
            result = await self.llm_service.generate_analysis(
                prompt=prompt,
                system_prompt=system_prompt,
                agent_type=self.agent_type
            )
            
            analysis_data = self._parse_response(result['analysis'])
            
            processing_time = int((time.time() - start_time) * 1000)
            
            state['finance_analysis'] = AgentAnalysis(
                agent_type=self.agent_type,
                agent_name=self.agent_name,
                analysis=analysis_data['analysis'],
                confidence=analysis_data['confidence'],
                key_factors=analysis_data['key_factors'],
                processing_time_ms=processing_time
            )
            
            state['current_step'] = 'finance_complete'
            
        except Exception as e:
            logger.error(f"Finance Guru analysis failed: {e}")
            state['errors'].append(f"Finance analysis failed: {str(e)}")
        
        return state

class GeopoliticsGuruAgent(BaseStockAgent):
    """Geopolitics expert analyzing global events impact on stock"""
    
    def __init__(self):
        super().__init__("Geopolitics Guru", "geopolitics_guru")
    
    async def analyze(self, state: StockAnalysisState) -> StockAnalysisState:
        """Perform geopolitical analysis"""
        start_time = time.time()
        logger.info(f"Geopolitics Guru analyzing {state['request'].symbol}")
        
        try:
            symbol = state['request'].symbol
            stock_data = self.get_stock_data(symbol)
            
            prompt = f"""
            As a Geopolitics Guru, analyze how global events and geopolitical factors 
            might impact the stock {symbol} ({stock_data.get('company_name', 'N/A')}).
            
            Company Details:
            - Sector: {stock_data.get('sector', 'N/A')}
            - Industry: {stock_data.get('industry', 'N/A')}
            - Market Cap: {stock_data.get('market_cap', 'N/A')}
            
            Time Frame: {state['request'].time_frequency}
            
            Analyze the impact of:
            1. Current geopolitical tensions and conflicts
            2. Trade policies and international relations
            3. Regulatory changes in key markets
            4. Currency fluctuations and their effects
            5. Supply chain disruptions from global events
            6. International market access and expansion risks
            
            Consider recent global events and their potential impact on this specific company and sector.
            
            Respond in JSON format:
            {{
                "analysis": "detailed geopolitical analysis",
                "confidence": 0.75,
                "key_factors": ["factor1", "factor2", "factor3"],
                "risk_level": "low/medium/high",
                "global_events_impact": "explanation of how current events affect the stock"
            }}
            """
            
            system_prompt = "You are a geopolitical risk analyst specializing in how global events impact financial markets and individual stocks."
            
            result = await self.llm_service.generate_analysis(
                prompt=prompt,
                system_prompt=system_prompt,
                agent_type=self.agent_type
            )
            
            analysis_data = self._parse_response(result['analysis'])
            
            processing_time = int((time.time() - start_time) * 1000)
            
            state['geopolitics_analysis'] = AgentAnalysis(
                agent_type=self.agent_type,
                agent_name=self.agent_name,
                analysis=analysis_data['analysis'],
                confidence=analysis_data['confidence'],
                key_factors=analysis_data['key_factors'],
                processing_time_ms=processing_time
            )
            
            state['current_step'] = 'geopolitics_complete'
            
        except Exception as e:
            logger.error(f"Geopolitics Guru analysis failed: {e}")
            state['errors'].append(f"Geopolitics analysis failed: {str(e)}")
        
        return state

class LegalGuruAgent(BaseStockAgent):
    """Legal expert analyzing regulatory and compliance factors"""
    
    def __init__(self):
        super().__init__("Legal Guru", "legal_guru")
    
    async def analyze(self, state: StockAnalysisState) -> StockAnalysisState:
        """Perform legal and regulatory analysis"""
        start_time = time.time()
        logger.info(f"Legal Guru analyzing {state['request'].symbol}")
        
        try:
            symbol = state['request'].symbol
            stock_data = self.get_stock_data(symbol)
            
            prompt = f"""
            As a Legal Guru specializing in corporate law and regulatory compliance,
            analyze the legal and regulatory factors affecting {symbol} ({stock_data.get('company_name', 'N/A')}).
            
            Company Details:
            - Sector: {stock_data.get('sector', 'N/A')}
            - Industry: {stock_data.get('industry', 'N/A')}
            
            Time Frame: {state['request'].time_frequency}
            
            Analyze:
            1. Regulatory compliance status and upcoming changes
            2. Industry-specific legal requirements
            3. Pending or recent litigation risks
            4. Regulatory approval processes (if applicable)
            5. Intellectual property and patent considerations
            6. ESG (Environmental, Social, Governance) compliance
            7. Data privacy and cybersecurity regulations
            8. Antitrust and competition law implications
            
            Focus on legal risks and opportunities that could materially impact stock performance.
            
            Respond in JSON format:
            {{
                "analysis": "detailed legal and regulatory analysis",
                "confidence": 0.80,
                "key_factors": ["factor1", "factor2", "factor3"],
                "legal_risk_level": "low/medium/high",
                "regulatory_outlook": "positive/neutral/negative"
            }}
            """
            
            system_prompt = "You are a corporate lawyer and regulatory specialist with expertise in securities law and corporate compliance."
            
            result = await self.llm_service.generate_analysis(
                prompt=prompt,
                system_prompt=system_prompt,
                agent_type=self.agent_type
            )
            
            analysis_data = self._parse_response(result['analysis'])
            
            processing_time = int((time.time() - start_time) * 1000)
            
            state['legal_analysis'] = AgentAnalysis(
                agent_type=self.agent_type,
                agent_name=self.agent_name,
                analysis=analysis_data['analysis'],
                confidence=analysis_data['confidence'],
                key_factors=analysis_data['key_factors'],
                processing_time_ms=processing_time
            )
            
            state['current_step'] = 'legal_complete'
            
        except Exception as e:
            logger.error(f"Legal Guru analysis failed: {e}")
            state['errors'].append(f"Legal analysis failed: {str(e)}")
        
        return state

class QuantDevAgent(BaseStockAgent):
    """Quantitative developer analyzing technical indicators and patterns"""
    
    def __init__(self):
        super().__init__("Quant Dev", "quant_dev")
    
    async def analyze(self, state: StockAnalysisState) -> StockAnalysisState:
        """Perform quantitative and technical analysis"""
        start_time = time.time()
        logger.info(f"Quant Dev analyzing {state['request'].symbol}")
        
        try:
            symbol = state['request'].symbol
            stock_data = self.get_stock_data(symbol)
            
            # Get more detailed price history for technical analysis
            stock = yf.Ticker(symbol)
            hist = stock.history(period="2y")  # 2 years of data for better technical analysis
            
            prompt = f"""
            As a Quantitative Developer and Technical Analyst, analyze {symbol} using technical indicators and quantitative methods.
            
            Current Stock Data:
            - Current Price: ${stock_data.get('current_price', 'N/A'):.2f}
            - Beta: {stock_data.get('beta', 'N/A')}
            - 52W High: ${stock_data.get('52_week_high', 'N/A')}
            - 52W Low: ${stock_data.get('52_week_low', 'N/A')}
            - Average Volume: {stock_data.get('avg_volume', 'N/A')}
            
            Time Frame: {state['request'].time_frequency}
            Historical data points available: {len(hist)} days
            
            Perform technical analysis covering:
            1. Trend analysis (short, medium, long-term trends)
            2. Support and resistance levels
            3. Technical indicators (RSI, MACD, moving averages)
            4. Volume analysis and patterns
            5. Volatility analysis
            6. Price momentum and oscillators
            7. Chart patterns and their implications
            8. Risk metrics and statistical measures
            
            Provide quantitative insights and technical price targets.
            
            Respond in JSON format:
            {{
                "analysis": "detailed technical and quantitative analysis",
                "confidence": 0.78,
                "key_factors": ["factor1", "factor2", "factor3"],
                "technical_outlook": "bullish/neutral/bearish",
                "support_resistance": {{"support": price, "resistance": price}},
                "volatility_assessment": "low/medium/high"
            }}
            """
            
            system_prompt = "You are a quantitative analyst and technical analyst with expertise in statistical modeling, technical indicators, and algorithmic trading strategies."
            
            result = await self.llm_service.generate_analysis(
                prompt=prompt,
                system_prompt=system_prompt,
                agent_type=self.agent_type
            )
            
            analysis_data = self._parse_response(result['analysis'])
            
            processing_time = int((time.time() - start_time) * 1000)
            
            state['quant_analysis'] = AgentAnalysis(
                agent_type=self.agent_type,
                agent_name=self.agent_name,
                analysis=analysis_data['analysis'],
                confidence=analysis_data['confidence'],
                key_factors=analysis_data['key_factors'],
                processing_time_ms=processing_time
            )
            
            state['current_step'] = 'quant_complete'
            
        except Exception as e:
            logger.error(f"Quant Dev analysis failed: {e}")
            state['errors'].append(f"Quant analysis failed: {str(e)}")
        
        return state

class FinancialAnalystAgent(BaseStockAgent):
    """Final analyst consolidating all inputs into prediction"""
    
    def __init__(self):
        super().__init__("Financial Analyst", "financial_analyst")
    
    async def analyze(self, state: StockAnalysisState) -> StockAnalysisState:
        """Consolidate all analyses into final prediction"""
        start_time = time.time()
        logger.info(f"Financial Analyst consolidating analysis for {state['request'].symbol}")
        
        try:
            symbol = state['request'].symbol
            time_freq = state['request'].time_frequency
            
            # Gather all previous analyses
            analyses = {}
            if state.get('finance_analysis'):
                analyses['finance'] = state['finance_analysis'].analysis
            if state.get('geopolitics_analysis'):
                analyses['geopolitics'] = state['geopolitics_analysis'].analysis  
            if state.get('legal_analysis'):
                analyses['legal'] = state['legal_analysis'].analysis
            if state.get('quant_analysis'):
                analyses['quant'] = state['quant_analysis'].analysis
            
            stock_data = self.get_stock_data(symbol)
            current_price = stock_data.get('current_price', 100)
            
            prompt = f"""
            As a Senior Financial Analyst, consolidate the following expert analyses to create a comprehensive stock forecast for {symbol}.
            
            Current Price: ${current_price:.2f}
            Time Frame: {time_freq}
            
            Expert Analyses:
            {json.dumps(analyses, indent=2)}
            
            Create a consolidated forecast that:
            1. Weighs all expert opinions appropriately
            2. Identifies consensus views and conflicts
            3. Provides specific price predictions for the requested time frame
            4. Assigns overall confidence score
            5. Lists key factors driving the prediction
            
            For time frequency "{time_freq}", generate realistic price points showing progression over time.
            
            Respond in JSON format:
            {{
                "analysis": "comprehensive consolidation of all expert views",
                "confidence": 0.82,
                "key_factors": ["consolidated key factors"],
                "prediction": {{
                    "time_frequency": "{time_freq}",
                    "predictions": [
                        {{"date": "2024-01-15", "price": 105.50}},
                        {{"date": "2024-01-30", "price": 108.25}}
                    ]
                }},
                "recommendation": "buy/hold/sell",
                "risk_assessment": "detailed risk analysis"
            }}
            """
            
            system_prompt = "You are a senior financial analyst responsible for creating final investment recommendations by synthesizing input from multiple domain experts."
            
            result = await self.llm_service.generate_analysis(
                prompt=prompt,
                system_prompt=system_prompt,
                agent_type=self.agent_type
            )
            
            analysis_data = self._parse_response(result['analysis'])
            
            processing_time = int((time.time() - start_time) * 1000)
            
            state['final_analysis'] = AgentAnalysis(
                agent_type=self.agent_type,
                agent_name=self.agent_name,
                analysis=analysis_data['analysis'],
                confidence=analysis_data['confidence'],
                key_factors=analysis_data['key_factors'],
                processing_time_ms=processing_time
            )
            
            # Create final result
            agent_analyses = {}
            if state.get('finance_analysis'):
                agent_analyses['finance_guru'] = state['finance_analysis'].analysis
            if state.get('geopolitics_analysis'):
                agent_analyses['geopolitics_guru'] = state['geopolitics_analysis'].analysis
            if state.get('legal_analysis'):
                agent_analyses['legal_guru'] = state['legal_analysis'].analysis
            if state.get('quant_analysis'):
                agent_analyses['quant_dev'] = state['quant_analysis'].analysis
            agent_analyses['financial_analyst'] = analysis_data['analysis']
            
            from .state import StockAnalysisResult
            state['analysis_result'] = StockAnalysisResult(
                symbol=symbol,
                prediction=analysis_data['prediction'],
                agent_analyses=agent_analyses,
                confidence_score=analysis_data['confidence'],
                factors_considered=analysis_data['key_factors']
            )
            
            state['current_step'] = 'analysis_complete'
            state['completed_at'] = datetime.now(timezone.utc).isoformat()
            
        except Exception as e:
            logger.error(f"Financial Analyst consolidation failed: {e}")
            state['errors'].append(f"Final analysis failed: {str(e)}")
        
        return state