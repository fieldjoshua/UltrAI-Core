import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import svgr from 'vite-plugin-svgr';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Let Vite handle loading .env files automatically based on mode and cwd
  // process.cwd() should be 'frontend/' when running 'npm run dev' from there
  const env = loadEnv(mode, process.cwd(), ''); // Load all env vars

  // Log the specific variable we expect to be loaded
  console.log('API URL Vite sees:', env.VITE_API_URL || 'Not found');
  console.log('IS_DOCKER value:', env.VITE_IS_DOCKER);

  const apiUrl = 'https://ultrai-core.onrender.com/api';

  console.log('Using API URL:', apiUrl);

  return {
    plugins: [
      react(),
      svgr()
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '/api': path.resolve(__dirname, './api'),
        'react': path.resolve(__dirname, 'node_modules/react'),
        'react-dom': path.resolve(__dirname, 'node_modules/react-dom'),
      },
    },
    server: {
      port: 3009, // Still attempts this port first
      open: true,
    },
    define: {
      // Use the loaded env variable directly
      'import.meta.env.VITE_API_URL': JSON.stringify(apiUrl),
    },
  };
});
