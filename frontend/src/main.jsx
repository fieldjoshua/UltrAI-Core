import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { store } from './store';
import App from './App';
import './styles/index.css';

// IMPORTANT: Force API URL to use port 8000 for development
window.OVERRIDE_API_URL = 'http://localhost:8000/api';
console.log('API URL forced to:', window.OVERRIDE_API_URL);

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <Provider store={store}>
            <App />
        </Provider>
    </React.StrictMode>
);
