import { defineConfig, type Plugin } from 'vite';
import react from '@vitejs/plugin-react';

function ultraiMockApi(): Plugin {
  return {
    name: 'ultrai-mock-api',
    configureServer(server) {
      server.middlewares.use('/api/orchestrator/status', (_req, res) => {
        const body = JSON.stringify({
          online: true,
          pattern: 'critique → fact-check → synth',
          queueDepth: 1 + Math.floor(Math.random() * 3),
          activeModels: ['OpenAI', 'Anthropic', 'Google'],
          tokenRatePerMin: 1600 + Math.floor(Math.random() * 600),
          errorCount1h: 0,
        });
        res.setHeader('Content-Type', 'application/json');
        res.end(body);
      });
    },
  };
}

export default defineConfig({
  plugins: [react(), ultraiMockApi()],
  server: { port: 5173 },
});