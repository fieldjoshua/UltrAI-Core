import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// Production configuration
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '/api': path.resolve(__dirname, './api'),
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('react') || id.includes('react-dom')) {
              return 'react';
            }
            if (id.includes('@radix-ui')) {
              return 'radix-ui';
            }
            if (id.includes('axios')) {
              return 'axios';
            }
            return 'vendor';
          }
        },
      },
    },
  },
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify('https://ultrai-core.onrender.com'),
  },
});