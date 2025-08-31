# Demo Service Setup for Render

This document outlines how to set up a separate demo service on Render for UltrAI.

## Overview

The demo service provides a standalone instance of UltrAI that can run without real API keys, allowing users to experience the full interface and workflow.

## Demo Mode Features

1. **Manual Toggle**: Users click "🎮 Try Demo Mode" button on the intro screen
2. **Pre-filled Data**: 
   - Query: "What are the best strategies for sustainable urban transportation?"
   - Selected models: GPT-4, Claude 3, Gemini Pro
   - Selected goals: Creative ideas, Deep analysis
3. **Simulated Processing**: 8-second delay showing all processing steps
4. **Realistic Response**: Multi-model analysis with key findings and recommendations

## Setting Up Demo Service on Render

### Option 1: Mock API Responses (Recommended)

1. Create a new web service on Render
2. Set environment variables:
   ```
   VITE_API_MODE=mock
   ENABLE_MOCK_RESPONSES=true
   ```
3. The frontend will use mock API interceptors defined in `frontend/src/services/api.ts`

### Option 2: Demo Backend Service

1. Create a separate backend service with demo endpoints
2. Configure environment variables:
   ```
   DEMO_MODE=true
   MINIMUM_MODELS_REQUIRED=0
   ENABLE_SINGLE_MODEL_FALLBACK=true
   ```
3. Implement demo endpoints that return predefined responses

### Option 3: Lightweight Demo API

Create a minimal Express server that returns demo responses:

```javascript
app.post('/api/orchestrator/analyze', (req, res) => {
  setTimeout(() => {
    res.json({
      success: true,
      processing_time: 4.73,
      results: {
        ultra_synthesis: {
          output: {
            synthesis: "Demo analysis results..."
          }
        }
      },
      models_used: ["gpt-4", "claude-3", "gemini-pro"]
    });
  }, 3000);
});
```

## Frontend Configuration

The demo mode is already implemented in the CyberWizard component:

- Toggle button on intro screen
- Pre-fills query and selections when activated
- Simulates 8-second processing time
- Shows realistic multi-model response

## Deployment Steps

1. Fork/branch the repository for demo
2. Configure demo-specific environment variables
3. Deploy to Render as a separate service
4. Update demo URL in documentation

## Benefits

- No API keys required
- Consistent demo experience
- Isolated from production
- Easy to maintain and update