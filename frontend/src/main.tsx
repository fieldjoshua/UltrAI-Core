import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/index.css';
import { ThemeRegistry } from './theme';
import { QueryProvider } from './providers/QueryProvider';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryProvider>
      <ThemeRegistry>
        <App />
      </ThemeRegistry>
    </QueryProvider>
  </React.StrictMode>
);
