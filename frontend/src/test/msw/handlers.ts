import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/health', () =>
    HttpResponse.json({ status: 'ok', services: {} })
  ),
  http.get('/api/available-models', ({ request }) => {
    const url = new URL(request.url);
    const healthyOnly = url.searchParams.get('healthy_only') === 'true';
    
    const allModels = [
      { name: 'gpt-4', provider: 'openai', is_available: true, cost_per_1k_tokens: 0.03 },
      { name: 'claude-3-opus', provider: 'anthropic', is_available: true, cost_per_1k_tokens: 0.04 },
      { name: 'gemini-1.5-pro', provider: 'google', is_available: false, cost_per_1k_tokens: 0.02 }
    ];
    
    const models = healthyOnly 
      ? allModels.filter(m => m.is_available)
      : allModels;
      
    return HttpResponse.json({ models });
  }),
  http.get('/api/orchestrator/health', () => new HttpResponse(null, { status: 200 })),
  http.get('/api/models/health', () =>
    HttpResponse.json({
      models: {
        'gpt-4': { status: 'healthy', latency_ms: 234, success_rate: 0.99 },
        'claude-3-opus': { status: 'healthy', latency_ms: 345, success_rate: 0.98 },
        'gemini-1.5-pro': { status: 'degraded', latency_ms: 1200, success_rate: 0.85 }
      },
      overall_health: 'healthy',
      healthy_models: 2,
      total_models: 3
    })
  ),
  http.get('/api/orchestrator/status', () =>
    HttpResponse.json({ 
      state: 'idle', 
      queueDepth: 0,
      models: {
        available: [
          { name: 'gpt-4', provider: 'openai', is_available: true },
          { name: 'claude-3-opus', provider: 'anthropic', is_available: true }
        ]
      }
    })
  ),
  http.post('/api/orchestrator/analyze', async ({ request }) => {
    const auth = request.headers.get('authorization');
    if (!auth) {
      return HttpResponse.json({ message: 'Unauthorized' }, { status: 401 });
    }
    return HttpResponse.json({
      results: {
        ultra_synthesis: { content: 'This is the synthesized response from multiple models.' },
        models_used: ['gpt-4', 'claude-3-opus', 'gemini-1.5-pro'],
        initial_responses: {},
        meta_analysis: {},
      },
      processing_time: 1.2,
    }, { status: 200 });
  }),
];


