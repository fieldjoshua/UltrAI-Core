import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider as ReduxProvider } from 'react-redux';
import App from './App';
import './styles/index.css';
import { ThemeRegistry } from './theme';
import { QueryProvider } from './providers/QueryProvider';
import { store } from './store';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ReduxProvider store={store}>
      <QueryProvider>
        <ThemeRegistry>
          <App />
        </ThemeRegistry>
      </QueryProvider>
    </ReduxProvider>
  </React.StrictMode>
);
