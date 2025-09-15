import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/index.css';
import { ThemeRegistry } from './theme';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeRegistry>
      <App />
    </ThemeRegistry>
  </React.StrictMode>
);
