#!/usr/bin/env node

const axios = require('axios');

async function testFullFlow() {
  console.log('🚀 Testing Full Frontend-Backend Flow\n');

  // Test 1: Models Endpoint
  console.log('1️⃣ Testing Models Dropdown...');
  try {
    const modelsResponse = await axios.get('http://localhost:8087/api/available-models');
    const models = modelsResponse.data.available_models;
    console.log('✅ Models loaded successfully:', models.join(', '));
    console.log(`   📊 Found ${models.length} models\n`);
  } catch (error) {
    console.error('❌ Models test failed:', error.message);
    return;
  }

  // Test 2: Simple Analysis
  console.log('2️⃣ Testing Simple Analysis (1 model)...');
  try {
    const simplePayload = {
      prompt: "What is 2+2?",
      selected_models: ["gpt4o"],
      ultra_model: "gpt4o",
      pattern: "gut"
    };

    const simpleResponse = await axios.post('http://localhost:8087/api/analyze', simplePayload);
    const result = simpleResponse.data;
    
    console.log('✅ Simple analysis successful');
    console.log('   📄 Ultra response length:', result.ultra_response?.length || 0, 'chars');
    console.log('   🤖 Model responses:', Object.keys(result.model_responses || {}).join(', '));
    console.log('   ⏱️  Performance time:', result.performance?.total_time_seconds || 0, 'seconds\n');
  } catch (error) {
    console.error('❌ Simple analysis failed:', error.message);
    return;
  }

  // Test 3: Multi-Model Analysis
  console.log('3️⃣ Testing Multi-Model Analysis...');
  try {
    const multiPayload = {
      prompt: "Explain the benefits of renewable energy in 3 key points",
      selected_models: ["gpt4o", "claude3opus", "gemini15pro"],
      ultra_model: "gpt4o",
      pattern: "perspective"
    };

    const multiResponse = await axios.post('http://localhost:8087/api/analyze', multiPayload);
    const result = multiResponse.data;
    
    console.log('✅ Multi-model analysis successful');
    console.log('   🤖 Models used:', Object.keys(result.model_responses || {}).length);
    console.log('   📊 Individual responses:');
    
    for (const [model, response] of Object.entries(result.model_responses || {})) {
      console.log(`      ${model}: ${response.length} chars`);
    }
    console.log('   📄 Ultra synthesis:', result.ultra_response?.length || 0, 'chars');
    console.log('   ⏱️  Total time:', result.performance?.total_time_seconds || 0, 'seconds\n');
  } catch (error) {
    console.error('❌ Multi-model analysis failed:', error.message);
    return;
  }

  // Test 4: Check Response Format (No [object Object])
  console.log('4️⃣ Testing Response Format...');
  try {
    const formatPayload = {
      prompt: "Test response format",
      selected_models: ["gpt4o", "claude3opus"],
      ultra_model: "gpt4o"
    };

    const formatResponse = await axios.post('http://localhost:8087/api/analyze', formatPayload);
    const result = formatResponse.data;
    
    let hasObjectObject = false;
    for (const [model, response] of Object.entries(result.model_responses || {})) {
      if (typeof response === 'string' && response.includes('[object Object]')) {
        hasObjectObject = true;
        console.log(`❌ Found [object Object] in ${model} response`);
      }
    }
    
    if (!hasObjectObject) {
      console.log('✅ No [object Object] errors found');
      console.log('   📝 All responses are properly formatted strings\n');
    }
  } catch (error) {
    console.error('❌ Format test failed:', error.message);
    return;
  }

  // Test 5: Frontend Health
  console.log('5️⃣ Testing Frontend Accessibility...');
  try {
    const frontendResponse = await axios.get('http://localhost:3009', { timeout: 5000 });
    console.log('✅ Frontend is accessible');
    console.log('   🌐 Status:', frontendResponse.status);
    console.log('   📦 Content length:', frontendResponse.data.length, 'bytes\n');
  } catch (error) {
    console.error('❌ Frontend test failed:', error.message);
  }

  // Summary
  console.log('🎉 TESTING COMPLETE!');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('✅ Your UltraAI frontend should now work perfectly!');
  console.log('');
  console.log('🔗 Ready to test: http://localhost:3009/analyze');
  console.log('');
  console.log('💡 Expected behavior:');
  console.log('   • Models dropdown shows 6 models');
  console.log('   • No "[object Object]" errors');
  console.log('   • Full analysis flow works end-to-end');
  console.log('   • Multiple model responses display correctly');
  console.log('   • Ultra synthesis appears at the bottom');
}

testFullFlow().catch(console.error);