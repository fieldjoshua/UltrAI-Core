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
      'react': path.resolve(__dirname, 'node_modules/react'),
      'react-dom': path.resolve(__dirname, 'node_modules/react-dom'),
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks: undefined, // Let Vite handle chunking to avoid React duplication
      },
    },
  },
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify('https://ultrai-core-4lut.onrender.com/api'),
  },
});