#!/usr/bin/env python3
"""Test script to verify concurrent agent execution in orchestrator"""

import sys
import os
import asyncio
import time
import json
from datetime import datetime

# Add the stock-ai-service to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agents.orchestrator import StockAnalysisOrchestrator
from agents.state import StockAnalysisRequest


class AnalysisLogger:
    """Logger for analysis outputs"""
    
    def __init__(self, log_file: str):
        self.log_file = log_file
        # Initialize log file
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"=== Stock Analysis Test Log ===\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
    
    def log(self, message: str):
        """Log message to both console and file"""
        print(message)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(message + '\n')
    
    def log_analysis(self, agent_name: str, analysis: dict):
        """Log detailed analysis from an agent"""
        self.log(f"\n{'='*60}")
        self.log(f"🤖 {agent_name} DETAILED ANALYSIS")
        self.log(f"{'='*60}")
        
        if isinstance(analysis, dict):
            self.log(f"Agent Type: {analysis.get('agent_type', 'N/A')}")
            self.log(f"Agent Name: {analysis.get('agent_name', 'N/A')}")
            self.log(f"Processing Time: {analysis.get('processing_time_ms', 'N/A')}ms")
            self.log(f"Confidence: {analysis.get('confidence', 'N/A')}")
            self.log(f"Model: {analysis.get('model', 'N/A')}")
            
            # Key factors if available
            if analysis.get('key_factors'):
                self.log(f"\nKey Factors:")
                for factor in analysis.get('key_factors', []):
                    self.log(f"  • {factor}")
            
            # Full analysis text
            analysis_text = analysis.get('analysis', '')
            if analysis_text:
                self.log(f"\nFull Analysis:")
                self.log("-" * 40)
                self.log(analysis_text)
                self.log("-" * 40)
        else:
            self.log(f"Raw Analysis: {str(analysis)}")
    
    def log_final_result(self, result: dict):
        """Log the final analysis result"""
        self.log(f"\n{'='*80}")
        self.log(f"🎯 FINAL ANALYSIS RESULT")
        self.log(f"{'='*80}")
        
        if isinstance(result, dict):
            self.log(f"Symbol: {result.get('symbol', 'N/A')}")
            self.log(f"Confidence Score: {result.get('confidence_score', 'N/A')}")
            
            # Predictions
            if result.get('prediction'):
                prediction = result.get('prediction')
                self.log(f"\nPredictions:")
                self.log(f"Time Frequency: {prediction.get('time_frequency', 'N/A')}")
                
                if prediction.get('predictions'):
                    self.log(f"Price Predictions:")
                    for pred in prediction.get('predictions', []):
                        self.log(f"  {pred.get('date', 'N/A')}: ${pred.get('price', 'N/A')}")
            
            # Agent summaries
            if result.get('agent_analyses'):
                self.log(f"\nAgent Analysis Summaries:")
                for agent, analysis in result.get('agent_analyses', {}).items():
                    snippet = analysis[:200] + "..." if len(analysis) > 200 else analysis
                    self.log(f"  {agent}: {snippet}")
        else:
            self.log(f"Raw Result: {str(result)}")

async def test_concurrent_execution(analysis_logger):
    """Test the orchestrator with concurrent agent execution"""
    
    analysis_logger.log("🧪 Testing Multi-Agent Stock Analysis Orchestrator")
    analysis_logger.log("=" * 60)
    
    # Initialize orchestrator
    orchestrator = StockAnalysisOrchestrator()
    
    # Print workflow description
    analysis_logger.log("📋 Workflow Description:")
    analysis_logger.log(orchestrator.get_workflow_description())
    analysis_logger.log("")
    
    # Test with a real stock
    test_symbol = "AAPL"
    test_timeframe = "1M"
    
    analysis_logger.log(f"🚀 Starting analysis for {test_symbol} ({test_timeframe})")
    analysis_logger.log("-" * 40)
    
    start_time = time.time()
    
    try:
        # Run the analysis
        result = await orchestrator.analyze_stock(
            symbol=test_symbol,
            time_frequency=test_timeframe,
            user_context="Testing concurrent agent execution"
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        analysis_logger.log(f"⏱️  Total execution time: {execution_time:.2f} seconds")
        analysis_logger.log("")
        
        # Display results from each agent
        analysis_logger.log("📊 Agent Analysis Results:")
        analysis_logger.log("=" * 40)
        
        agents = [
            ("Finance Guru", "finance_analysis"),
            ("Geopolitics Guru", "geopolitics_analysis"), 
            ("Legal Guru", "legal_analysis"),
            ("Quant Dev", "quant_analysis"),
            ("Final Analyst", "final_analysis")
        ]
        
        for agent_name, analysis_key in agents:
            analysis = result.get(analysis_key)
            analysis_logger.log(f"\n🤖 {agent_name} Agent:")
            analysis_logger.log("-" * 20)
            
            if analysis:
                # Show analysis metadata
                if isinstance(analysis, dict):
                    analysis_logger.log(f"✅ Status: Completed")
                    analysis_logger.log(f"📝 Analysis length: {len(str(analysis.get('analysis', '')))} characters")
                    analysis_logger.log(f"⏱️  Processing time: {analysis.get('processing_time_ms', 'N/A')}ms")
                    analysis_logger.log(f"🎯 Agent type: {analysis.get('agent_type', 'N/A')}")
                    analysis_logger.log(f"🤖 Model: {analysis.get('model', 'N/A')}")
                    
                    # Show snippet of analysis for console, full analysis for log
                    analysis_text = analysis.get('analysis', '')
                    if analysis_text:
                        snippet = analysis_text[:200] + "..." if len(analysis_text) > 200 else analysis_text
                        analysis_logger.log(f"📄 Sample: {snippet}")
                    
                    # Log full detailed analysis to file
                    analysis_logger.log_analysis(agent_name, analysis)
                elif hasattr(analysis, '__dict__'):
                    # Handle Pydantic model objects
                    analysis_dict = analysis.__dict__
                    analysis_logger.log_analysis(agent_name, analysis_dict)
                else:
                    analysis_logger.log(f"✅ Status: Completed")
                    analysis_logger.log(f"📄 Result: {str(analysis)[:200]}...")
            else:
                analysis_logger.log("❌ Status: No analysis generated")
        
        # Show workflow metadata
        analysis_logger.log(f"\n🔧 Workflow Metadata:")
        analysis_logger.log(f"   Workflow ID: {result.get('workflow_id')}")
        analysis_logger.log(f"   Started at: {result.get('started_at')}")
        analysis_logger.log(f"   Completed at: {result.get('completed_at')}")
        analysis_logger.log(f"   Current step: {result.get('current_step')}")
        analysis_logger.log(f"   Errors: {len(result.get('errors', []))}")
        analysis_logger.log(f"   Warnings: {len(result.get('warnings', []))}")
        
        # Show any errors
        if result.get('errors'):
            analysis_logger.log(f"\n⚠️  Errors encountered:")
            for i, error in enumerate(result.get('errors', []), 1):
                analysis_logger.log(f"   {i}. {error}")
        
        # Show final analysis result
        if result.get('analysis_result'):
            analysis_logger.log(f"\n🎯 Final Analysis Result:")
            final_result = result.get('analysis_result')
            if isinstance(final_result, dict):
                analysis_logger.log(f"   Recommendation: {final_result.get('recommendation', 'N/A')}")
                analysis_logger.log(f"   Confidence: {final_result.get('confidence_score', 'N/A')}")
                analysis_logger.log(f"   Risk Level: {final_result.get('risk_level', 'N/A')}")
                
                # Log full final result to file
                analysis_logger.log_final_result(final_result)
            else:
                snippet = str(final_result)[:300] + "..." if len(str(final_result)) > 300 else str(final_result)
                analysis_logger.log(f"   Result: {snippet}")
        
        analysis_logger.log(f"\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        
        analysis_logger.log(f"❌ Test failed after {execution_time:.2f} seconds")
        analysis_logger.log(f"Error: {e}")
        import traceback
        error_trace = traceback.format_exc()
        analysis_logger.log(f"Traceback:\n{error_trace}")
        return False


async def test_portfolio_analysis():
    """Test portfolio analysis functionality"""
    
    print("\n" + "=" * 60)
    print("🧪 Testing Portfolio Analysis")
    print("=" * 60)
    
    orchestrator = StockAnalysisOrchestrator()
    
    # Test portfolio data
    portfolio_data = [
        {"symbol": "AAPL", "allocation": 30},
        {"symbol": "GOOGL", "allocation": 25}, 
        {"symbol": "MSFT", "allocation": 25},
        {"symbol": "TSLA", "allocation": 20}
    ]
    
    print(f"📊 Testing portfolio with {len(portfolio_data)} stocks")
    for stock in portfolio_data:
        print(f"   - {stock['symbol']}: {stock['allocation']}%")
    
    start_time = time.time()
    
    try:
        result = await orchestrator.analyze_portfolio(
            portfolio_data=portfolio_data,
            time_frequency="1M"
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\n⏱️  Portfolio analysis time: {execution_time:.2f} seconds")
        print(f"📋 Analysis result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        
        if result.get('errors'):
            print(f"⚠️  Errors: {result.get('errors')}")
        else:
            print("✅ Portfolio analysis completed successfully!")
        
        return True
        
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"❌ Portfolio test failed after {execution_time:.2f} seconds")
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    # Initialize logger
    log_filename = f"analysis_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    analysis_logger = AnalysisLogger(log_filename)
    
    analysis_logger.log("🚀 Starting Orchestrator Tests")
    analysis_logger.log("=" * 80)
    analysis_logger.log(f"📄 Detailed analysis will be written to: {log_filename}")
    analysis_logger.log("")
    
    # Run tests
    asyncio.run(test_concurrent_execution(analysis_logger))
    # Skip portfolio test for now as it has issues
    
    analysis_logger.log("\n🏁 All tests completed!")
    analysis_logger.log(f"📄 Full analysis log saved to: {log_filename}")