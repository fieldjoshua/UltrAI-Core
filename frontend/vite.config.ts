import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import svgr from 'vite-plugin-svgr';
import { visualizer } from 'rollup-plugin-visualizer';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Let Vite handle loading .env files automatically based on mode and cwd
  // process.cwd() should be 'frontend/' when running 'npm run dev' from there
  const env = loadEnv(mode, process.cwd(), ''); // Load all env vars

  // Log the specific variable we expect to be loaded
  console.log('API URL Vite sees:', env.VITE_API_URL || 'Not found');
  console.log('IS_DOCKER value:', env.VITE_IS_DOCKER);

  // Prefer environment-provided API URL; fallback to sensible default
  const apiUrl = env.VITE_API_URL || '/api';
  console.log('Using API URL:', apiUrl);

  return {
    plugins: [
      react(),
      svgr(),
      // Bundle visualization - only in build mode
      mode === 'production' && visualizer({
        emitFile: true,
        filename: 'stats.html',
        open: false,
        gzipSize: true,
        brotliSize: true,
        template: 'treemap', // or 'sunburst', 'network'
      })
    ].filter(Boolean),
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@components': path.resolve(__dirname, './src/components'),
        '@api': path.resolve(__dirname, './src/api'),
        '@internal': path.resolve(__dirname, './src/internal'),
        '@skins': path.resolve(__dirname, './src/skins'),
        '/api': path.resolve(__dirname, './api'),
        react: path.resolve(__dirname, 'node_modules/react'),
        'react-dom': path.resolve(__dirname, 'node_modules/react-dom'),
      },
    },
    server: {
      port: 3009, // Still attempts this port first
      open: true,
    },
    build: {
      // Enable production sourcemaps to debug minified errors in prod
      sourcemap: true,
      // Rollup options for better code splitting
      rollupOptions: {
        output: {
          manualChunks: {
            // Split vendor chunks
            'react-vendor': ['react', 'react-dom', 'react-router-dom'],
            'ui-vendor': ['@radix-ui/react-checkbox', '@radix-ui/react-dropdown-menu', 
                          '@radix-ui/react-label', '@radix-ui/react-progress',
                          '@radix-ui/react-radio-group', '@radix-ui/react-tabs',
                          '@radix-ui/react-tooltip'],
            'state-vendor': ['@reduxjs/toolkit', 'react-redux', 'zustand', '@tanstack/react-query'],
            'utils-vendor': ['axios', 'clsx', 'tailwind-merge', 'class-variance-authority'],
          },
        },
      },
      // Chunk size warnings
      chunkSizeWarningLimit: 1000, // 1MB
    },
    define: {
      // Use the loaded env variable directly
      'import.meta.env.VITE_API_URL': JSON.stringify(apiUrl),
    },
  };
});
