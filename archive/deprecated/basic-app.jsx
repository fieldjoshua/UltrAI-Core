import React from 'react';
import ReactDOM from 'react-dom/client';

// The most basic React component possible
function App() {
  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Basic React App</h1>
      <p>This is a minimal React app with no dependencies.</p>
      <button 
        onClick={() => alert('React is working!')}
        style={{ 
          padding: '8px 16px', 
          background: 'blue', 
          color: 'white', 
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        Click me
      </button>
    </div>
  );
}

// Plain vanilla React rendering - no StrictMode, no extra wrappers
ReactDOM.createRoot(document.getElementById('root')).render(<App />); 