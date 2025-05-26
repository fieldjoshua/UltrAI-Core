#!/usr/bin/env node

const axios = require('axios');

// Configuration
const FRONTEND_BASE = 'http://localhost:3009';
const BACKEND_BASE = 'http://localhost:8085';

async function testAvailableModels() {
  console.log('🔍 Testing /api/available-models...');
  try {
    const response = await axios.get(`${BACKEND_BASE}/api/available-models`);
    console.log('✅ Available Models Response:', response.data);
    return response.data.available_models || [];
  } catch (error) {
    console.error('❌ Available Models Error:', error.response?.data || error.message);
    return [];
  }
}

async function testAnalyzeEndpoint(models) {
  console.log('\n🧠 Testing /api/analyze...');
  
  // Use first available model or fallback
  const testModels = models.length > 0 ? [models[0]] : ['gpt4o'];
  const ultraModel = testModels[0];

  const payload = {
    prompt: "What is 2+2? Give a brief answer.",
    selected_models: testModels,
    ultra_model: ultraModel,
    pattern: "gut",
    options: {}
  };

  console.log('📤 Sending payload:', JSON.stringify(payload, null, 2));

  try {
    const response = await axios.post(`${BACKEND_BASE}/api/analyze`, payload, {
      headers: { 'Content-Type': 'application/json' }
    });
    
    console.log('✅ Analysis Response Status:', response.data.status);
    console.log('📄 Ultra Response:', response.data.ultra_response || 'No ultra response');
    
    if (response.data.model_responses) {
      console.log('🤖 Model Responses Structure:');
      for (const [model, modelResponse] of Object.entries(response.data.model_responses)) {
        console.log(`  ${model}:`, typeof modelResponse, ':', 
          typeof modelResponse === 'object' ? JSON.stringify(modelResponse).substring(0, 100) + '...' : modelResponse.substring(0, 100) + '...');
      }
    }
    
    return response.data;
  } catch (error) {
    console.error('❌ Analysis Error:', error.response?.data || error.message);
    return null;
  }
}

async function testFrontendHealth() {
  console.log('\n🌐 Testing Frontend Health...');
  try {
    const response = await axios.get(`${FRONTEND_BASE}`);
    console.log('✅ Frontend is responding (status:', response.status, ')');
    return true;
  } catch (error) {
    console.error('❌ Frontend Health Error:', error.message);
    return false;
  }
}

async function runFullTest() {
  console.log('🚀 Starting Full API Test...\n');
  
  // Test frontend health
  await testFrontendHealth();
  
  // Test available models
  const models = await testAvailableModels();
  
  // Test analysis
  await testAnalyzeEndpoint(models);
  
  console.log('\n✨ Test complete! Check the output above for any issues.');
  console.log('\n📋 Next steps:');
  console.log('1. Open http://localhost:3009/analyze in your browser');
  console.log('2. Check browser console for any "[object Object]" errors');
  console.log('3. Try submitting a test prompt');
}

// Run the test
runFullTest().catch(console.error);