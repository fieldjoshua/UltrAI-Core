import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on mode (development, production)
  // This ensures .env.local is loaded in development
  const env = loadEnv(mode, process.cwd(), 'VITE_'); // Load env from current working directory

  // Also try to load from frontend directory if we're in the project root
  const frontendPath = path.resolve(process.cwd(), 'frontend');
  const frontendEnv = loadEnv(mode, frontendPath, 'VITE_');

  // Combine environment variables, prioritizing frontend directory
  const combinedEnv = { ...env, ...frontendEnv };

  console.log('API URL from env:', combinedEnv.VITE_API_URL || 'Not found');

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      port: 3009, // Still attempts this port first
      open: true,
    },
    // Define env variables to expose to client-side code
    define: {
      'import.meta.env.VITE_API_URL': JSON.stringify(combinedEnv.VITE_API_URL || 'http://localhost:8000/api')
    }
  };
});
