import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { store } from './store';
import App from './App';
import './styles/index.css';
import { ThemeProvider, ThemeRegistry } from './theme';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Provider store={store}>
      <ThemeProvider>
        <ThemeRegistry>
          <App />
        </ThemeRegistry>
      </ThemeProvider>
    </Provider>
  </React.StrictMode>
);
