import { defineConfig, splitVendorChunkPlugin } from 'vite'
import reactSWC from '@vitejs/plugin-react-swc'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const isProduction = mode === 'production'
  
  return {
    plugins: [
      reactSWC({
        jsxImportSource: '@emotion/react',
        plugins: [['@swc/plugin-emotion', {}]],
      }),
      splitVendorChunkPlugin(),
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      port: 3000,
      open: true,
      hmr: {
        overlay: true,
      },
      watch: {
        usePolling: true,
      },
    },
    build: {
      outDir: 'dist',
      minify: 'terser',
      sourcemap: !isProduction,
      terserOptions: {
        compress: {
          drop_console: isProduction,
          drop_debugger: isProduction,
        },
      },
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor': ['react', 'react-dom'],
            'ui': [
              '@radix-ui/react-checkbox',
              '@radix-ui/react-label',
              '@radix-ui/react-tabs',
              '@radix-ui/react-progress',
              'lucide-react',
            ],
          },
        },
      },
    },
    optimizeDeps: {
      include: ['react', 'react-dom', 'axios'],
      exclude: [],
    },
    css: {
      devSourcemap: true,
    },
  }
}) 