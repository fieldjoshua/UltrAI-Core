import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { store } from './store';
import App from './App';
import './styles/index.css';
import './styles/theme.css';
import { ThemeRegistry } from './theme/ThemeRegistry';
import ErrorBoundary from './components/ErrorBoundary';
import { config } from './config';

function Root() {
  const [skin, setSkin] = useState(config.defaultSkin);

  return (
    <Provider store={store}>
      <ThemeRegistry skin={skin} setSkin={setSkin}>
        <ErrorBoundary>
          <App />
        </ErrorBoundary>
      </ThemeRegistry>
    </Provider>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
);
