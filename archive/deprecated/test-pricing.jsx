import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import { PricingDisplay } from './components/PricingDisplay';

// Minimal test component with interactive elements
function TestApp() {
  const [prompt, setPrompt] = useState('');
  const [selectedModels, setSelectedModels] = useState(['gpt-3.5-4k']);
  const [attachments, setAttachments] = useState([]);
  const [analysisType, setAnalysisType] = useState('confidence');

  // Handle file selection
  const handleFileChange = (e) => {
    if (e.target.files) {
      setAttachments(Array.from(e.target.files));
    }
  };

  // Handle model selection
  const toggleModel = (modelId) => {
    setSelectedModels(prev => 
      prev.includes(modelId) 
        ? prev.filter(id => id !== modelId) 
        : [...prev, modelId]
    );
  };

  return (
    <div style={{ 
      padding: '2rem', 
      maxWidth: '800px', 
      margin: '0 auto',
      backgroundColor: '#111',
      color: '#fff',
      minHeight: '100vh',
      fontFamily: 'monospace'
    }}>
      <h1>Dynamic Pricing Display Test</h1>
      <p>See how pricing changes in real-time based on your selections</p>
      
      <div style={{ marginTop: '2rem' }}>
        <h2>1. Select Models</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
          {[
            { id: 'gpt-3.5-4k', label: 'GPT-3.5 (Economy)' },
            { id: 'llama', label: 'Llama 3 (Economy)' },
            { id: 'claude-instant', label: 'Claude Instant (Economy)' },
            { id: 'gpt-4-8k', label: 'GPT-4 (Premium)' },
            { id: 'claude-3.5-sonnet', label: 'Claude 3.5 Sonnet (Premium)' },
            { id: 'gpt-4.5-128k', label: 'GPT-4.5 (Super Premium)' }
          ].map(model => (
            <div key={model.id} style={{ 
              padding: '10px', 
              border: `1px solid ${selectedModels.includes(model.id) ? '#0f0' : '#333'}`,
              borderRadius: '4px',
              cursor: 'pointer',
              backgroundColor: selectedModels.includes(model.id) ? '#143' : 'transparent'
            }} onClick={() => toggleModel(model.id)}>
              <input 
                type="checkbox" 
                checked={selectedModels.includes(model.id)} 
                onChange={() => {}} 
                id={`model-${model.id}`}
              />
              <label htmlFor={`model-${model.id}`}> {model.label}</label>
            </div>
          ))}
        </div>
      </div>
      
      <div style={{ marginTop: '2rem' }}>
        <h2>2. Enter Your Prompt</h2>
        <textarea 
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          style={{ 
            width: '100%', 
            height: '100px', 
            backgroundColor: '#222', 
            color: '#fff',
            border: '1px solid #333',
            borderRadius: '4px',
            padding: '8px',
            fontFamily: 'monospace'
          }}
          placeholder="Enter a prompt... Longer prompts will increase pricing"
        />
      </div>
      
      <div style={{ marginTop: '2rem' }}>
        <h2>3. Upload Attachments</h2>
        <input 
          type="file" 
          multiple 
          onChange={handleFileChange}
          style={{ marginBottom: '10px' }}
        />
        {attachments.length > 0 && (
          <div>
            <p>Selected files:</p>
            <ul>
              {attachments.map((file, index) => (
                <li key={index}>{file.name} ({Math.round(file.size / 1024)} KB)</li>
              ))}
            </ul>
          </div>
        )}
      </div>
      
      <div style={{ marginTop: '2rem' }}>
        <h2>4. Select Analysis Type</h2>
        <select 
          value={analysisType}
          onChange={(e) => setAnalysisType(e.target.value)}
          style={{ 
            padding: '8px', 
            backgroundColor: '#222',
            color: '#fff',
            border: '1px solid #333',
            borderRadius: '4px'
          }}
        >
          <option value="confidence">Confidence Analysis (Base)</option>
          <option value="critique">Critique (Moderate)</option>
          <option value="gut">Gut Check (Simple)</option>
          <option value="fact_check">Fact Check (Complex)</option>
          <option value="perspective">Perspective Analysis (Moderate)</option>
          <option value="scenario">Scenario Analysis (Complex)</option>
        </select>
      </div>
      
      <div style={{ 
        marginTop: '3rem', 
        padding: '1.5rem', 
        border: '1px solid #0af', 
        borderRadius: '8px',
        backgroundColor: 'rgba(0,100,200,0.1)'
      }}>
        <h2>Real-Time Pricing</h2>
        <PricingDisplay 
          selectedModels={selectedModels}
          promptText={prompt}
          attachments={attachments}
          analysisType={analysisType}
          showDetails={true}
        />
        <div style={{ marginTop: '1rem', fontSize: '14px', color: '#aaa' }}>
          <p>The pricing dynamically adjusts based on:</p>
          <ul style={{ marginLeft: '20px', listStyleType: 'disc' }}>
            <li>Selected models (premium models cost more)</li>
            <li>Prompt length and complexity</li>
            <li>Number and size of attachments</li>
            <li>Type of analysis selected</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

// Render to the DOM
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <TestApp />
  </React.StrictMode>
); 