# Model Availability Checker - Usage Example

## Frontend Integration Concept

### 1. Pre-Query Model Check

When user loads the orchestrator page:

```javascript
// Frontend code example
async function checkModelAvailability() {
  setCheckingStatus('loading');
  
  try {
    const response = await fetch('/api/models/check-availability', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        models: [
          'gpt-4', 'gpt-4-turbo', 'gpt-4o', 'o1-preview',
          'claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022',
          'gemini-1.5-pro', 'gemini-1.5-flash'
        ],
        query: userQuery || null,
        check_in_parallel: true
      })
    });
    
    const data = await response.json();
    updateModelUI(data);
  } catch (error) {
    console.error('Availability check failed:', error);
  }
}
```

### 2. API Response Example

```json
{
  "success": true,
  "models": {
    "gpt-4": {
      "model_name": "gpt-4",
      "status": "available",
      "response_time": 0.823,
      "error_message": null,
      "recommended": true,
      "performance_score": 0.85
    },
    "claude-3-5-sonnet-20241022": {
      "model_name": "claude-3-5-sonnet-20241022",
      "status": "available",
      "response_time": 0.651,
      "error_message": null,
      "recommended": true,
      "performance_score": 1.0
    },
    "gemini-1.5-pro": {
      "model_name": "gemini-1.5-pro",
      "status": "rate_limited",
      "response_time": null,
      "error_message": "Rate limited",
      "recommended": false,
      "performance_score": null
    },
    "o1-preview": {
      "model_name": "o1-preview",
      "status": "no_api_key",
      "response_time": null,
      "error_message": "No API key found for openai",
      "recommended": false,
      "performance_score": null
    }
  },
  "summary": {
    "total_models": 8,
    "available": 5,
    "rate_limited": 2,
    "no_api_key": 1,
    "errors": 0,
    "availability_rate": "62.5%",
    "average_response_time": "0.74s",
    "recommended_models": [
      "claude-3-5-sonnet-20241022",
      "gpt-4",
      "gpt-4o"
    ]
  },
  "check_duration": 2.34
}
```

### 3. UI Visualization Concept

```jsx
// React component example
function ModelSelector({ availabilityData }) {
  return (
    <div className="model-grid">
      {Object.entries(availabilityData.models).map(([model, info]) => (
        <ModelCard
          key={model}
          model={model}
          status={info.status}
          recommended={info.recommended}
          responseTime={info.response_time}
          performanceScore={info.performance_score}
        />
      ))}
    </div>
  );
}

function ModelCard({ model, status, recommended, responseTime, performanceScore }) {
  const statusColors = {
    available: 'green',
    rate_limited: 'orange',
    no_api_key: 'red',
    error: 'red',
    checking: 'blue'
  };
  
  return (
    <div className={`model-card ${status}`}>
      <div className="model-header">
        <h3>{model}</h3>
        {recommended && <span className="recommended-badge">⭐ Recommended</span>}
      </div>
      
      <div className="model-status">
        <span className={`status-indicator ${statusColors[status]}`}>
          {status === 'available' ? '✅' : status === 'rate_limited' ? '⏳' : '❌'}
        </span>
        <span className="status-text">{status.replace('_', ' ')}</span>
      </div>
      
      {status === 'available' && (
        <div className="model-metrics">
          <div>Response: {responseTime?.toFixed(2)}s</div>
          {performanceScore && (
            <div>Performance: {(performanceScore * 100).toFixed(0)}%</div>
          )}
        </div>
      )}
    </div>
  );
}
```

### 4. Animation During Check

```css
/* CSS for loading animation */
.model-card.checking {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0% {
    opacity: 0.6;
    transform: scale(0.98);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
  100% {
    opacity: 0.6;
    transform: scale(0.98);
  }
}

.status-indicator.blue {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

### 5. Quick Check Endpoint (Lightweight)

For faster, cached checks:

```bash
GET /api/models/quick-check?models=gpt-4,claude-3-5-sonnet-20241022,gemini-1.5-pro
```

Response:
```json
{
  "success": true,
  "models": {
    "gpt-4": {
      "status": "available",
      "cached": true
    },
    "claude-3-5-sonnet-20241022": {
      "status": "available",
      "cached": false
    },
    "gemini-1.5-pro": {
      "status": "rate_limited",
      "cached": true
    }
  },
  "timestamp": 1738567890.123
}
```

### 6. Recommendations Endpoint

Get model recommendations for specific queries:

```bash
GET /api/models/recommendations?query=Write%20a%20technical%20architecture%20document&limit=3
```

Response:
```json
{
  "success": true,
  "query": "Write a technical architecture document",
  "recommendations": [
    {
      "model": "gpt-4",
      "performance_score": 1.0,
      "response_time": 0.823,
      "reason": "High performance for query type"
    },
    {
      "model": "claude-3-5-sonnet-20241022",
      "performance_score": 0.7,
      "response_time": 0.651,
      "reason": "High performance for query type"
    },
    {
      "model": "gpt-4o",
      "performance_score": 0.4,
      "response_time": 0.912,
      "reason": "High performance for query type"
    }
  ],
  "total_available": 5
}
```

## Benefits

1. **User Experience**:
   - No more selecting unavailable models
   - Visual feedback during checks
   - Smart recommendations save time

2. **Performance**:
   - Parallel checking reduces wait time
   - 5-minute cache prevents redundant checks
   - Quick check endpoint for instant updates

3. **Intelligence**:
   - Query-based recommendations
   - Performance tracking improves over time
   - Automatic fallback to available models

4. **Transparency**:
   - Clear status indicators
   - Response time visibility
   - Performance scores shown