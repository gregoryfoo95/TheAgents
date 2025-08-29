/**
 * Test the stockService streaming integration
 * This simulates how the frontend would use the new streaming method
 */

// Simulate the stockService.analyzePortfolioStream method
async function testStockServiceStreaming() {
  console.log('🧪 Testing stockService streaming integration...');
  
  // Mock portfolio data (same format as frontend)
  const portfolioData = [
    { symbol: "AAPL", allocation_percentage: 40.0 },
    { symbol: "GOOGL", allocation_percentage: 30.0 },
    { symbol: "MSFT", allocation_percentage: 20.0 },
    { symbol: "TSLA", allocation_percentage: 10.0 }
  ];
  
  const timeFrequency = "1M";
  
  // Mock user ID (would come from authService.getCurrentUser() in real app)
  const mockUserId = 123456;
  
  // Create streaming request payload
  const requestPayload = {
    user_id: mockUserId,
    portfolio_data: portfolioData.map(stock => ({
      symbol: stock.symbol,
      allocation: stock.allocation_percentage
    })),
    time_frequency: timeFrequency,
    analysis_type: 'portfolio'
  };
  
  console.log('📤 Sending request:', JSON.stringify(requestPayload, null, 2));
  
  // Create abort controller for cleanup
  const controller = new AbortController();
  
  try {
    const STOCK_AI_URL = 'http://localhost:8003';
    
    const response = await fetch(`${STOCK_AI_URL}/analyze-portfolio-stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestPayload),
      signal: controller.signal
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    if (!response.body) {
      throw new Error('No response body available for streaming');
    }
    
    console.log('📡 Connected to streaming endpoint, processing events...');
    
    // Process streaming response
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    let eventCount = 0;
    const agentStatus = {};
    
    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonData = line.slice(6); // Remove 'data: ' prefix
            
            if (jsonData.trim()) {
              try {
                const eventData = JSON.parse(jsonData);
                eventCount++;
                
                // Log event
                console.log(`📥 Event ${eventCount}: ${eventData.type}`);
                
                // Track agent progress
                if (eventData.type === 'agent_start') {
                  agentStatus[eventData.agent_id] = 'started';
                  console.log(`  🚀 ${eventData.agent_name} started`);
                } else if (eventData.type === 'agent_complete') {
                  agentStatus[eventData.agent_id] = 'completed';
                  console.log(`  ✅ ${eventData.agent_name} completed (${eventData.confidence * 100}% confidence)`);
                } else if (eventData.type === 'final_result') {
                  console.log(`  🏆 Final result: ${eventData.confidence_score * 100}% confidence`);
                }
                
              } catch (parseError) {
                console.warn('⚠️ Failed to parse JSON:', jsonData, parseError);
              }
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
    
    // Test summary
    console.log('\n📊 Test Summary:');
    console.log(`✅ Total events received: ${eventCount}`);
    console.log('🤖 Agent status:');
    Object.entries(agentStatus).forEach(([agentId, status]) => {
      console.log(`  • ${agentId}: ${status}`);
    });
    
    console.log('\n🎉 stockService streaming integration test PASSED!');
    return true;
    
  } catch (error) {
    if (error.name === 'AbortError') {
      console.log('⚠️ Test was cancelled');
      return false;
    }
    
    console.error('❌ Test failed:', error);
    return false;
  }
}

// Run the test
testStockServiceStreaming()
  .then(success => {
    process.exit(success ? 0 : 1);
  })
  .catch(error => {
    console.error('💥 Test crashed:', error);
    process.exit(1);
  });