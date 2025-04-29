import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';

// Simple test component
function SimpleApp() {
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
      <h1>Simple Test App</h1>
      <p>If you can see this, React is rendering correctly.</p>
      <p>The main application may have an error in the components.</p>
      
      <div style={{ marginTop: '2rem' }}>
        <p>Try these steps to troubleshoot:</p>
        <ol>
          <li>Check the browser console for errors</li>
          <li>Try clearing browser cache</li>
          <li>Ensure all required packages are installed</li>
        </ol>
      </div>
    </div>
  );
}

// Render to the DOM
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <SimpleApp />
  </React.StrictMode>
); 