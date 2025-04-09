# UltraAI Analysis Troubleshooting

You mentioned that the analyses aren't being run in the updated UI. Here are some common issues and solutions to check.

## Common Issues

### 1. API Connection Issues

The most likely problem is that the UI components aren't properly connecting to the backend API. Check:

```typescript
// UltraWithDocuments.tsx - this should match your backend
const API_URL = 'http://localhost:8080'
```

### 2. API Endpoint Changes

The current UI expects these endpoints:
- `/api/upload-files` - For document upload
- `/api/analyze` - For running analyses

Make sure your backend is exposing these endpoints and they match what the UI is calling.

### 3. Missing or Changed Data Structure

Check the request format in `UltraWithDocuments.tsx`:

```typescript
// Example structure expected by the backend
const requestData = {
  prompt: prompt,
  models: selectedLLMs,
  ultra_model: ultraLLM,
  pattern: pattern,
  documents: processedDocuments.map(doc => doc.id),
  addons: selectedAddons,
  output_format: outputFormat,
  perspective: includePerspective ? perspective : null,
  include_fact_check: includeFactCheck
};
```

### 4. CORS Issues

If the backend is running on a different port, you might have CORS issues. Check your browser console for errors like:
```
Access to fetch at 'http://localhost:8080/api/analyze' from origin 'http://localhost:3000' has been blocked by CORS policy
```

### 5. Verify the Backend Is Running

Make sure your Python backend is running and responding to requests:

```bash
cd /Users/joshuafield/Documents/Ultra
source .venv/bin/activate
python backend/main.py
```

## Debugging Steps

1. Open your browser's Developer Tools (F12)
2. Go to the Network tab
3. Try to run an analysis
4. Look for API calls that fail (they'll be red)
5. Check the Response tab for any error messages

## Quick Fixes

### Fix 1: Update API URL

If your API is running on a different port, update the API_URL constant:

```typescript
// In UltraWithDocuments.tsx
const API_URL = 'http://localhost:YOUR_PORT'
```

### Fix 2: Add Console Logging

Add console logs to see what's happening:

```typescript
const handleRunAnalysis = async () => {
  console.log("Running analysis with data:", requestData);
  try {
    // Existing code...
    const response = await axios.post(`${API_URL}/api/analyze`, requestData);
    console.log("Analysis response:", response.data);
    // Rest of the code...
  } catch (error) {
    console.error("Analysis error:", error);
    // Error handling...
  }
};
```

### Fix 3: Check Network Requests

In your browser's developer tools, verify:
1. The request data is what you expect
2. The backend endpoint is being hit
3. The response comes back with expected data

### Fix 4: Backend Mock/Stub

If you want to verify the frontend works while fixing the backend:

```typescript
// Temporary mock function
const handleRunAnalysis = async () => {
  setIsProcessing(true);
  setCurrentStep(0);
  setError(null);
  
  // Simulate steps
  for (let i = 0; i < steps.length; i++) {
    setCurrentStep(i);
    await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second between steps
  }
  
  setOutput("This is a simulated response to verify the UI is working correctly.");
  setIsProcessing(false);
  setIsComplete(true);
};
```

## Next Steps

1. Check the browser console for errors
2. Verify API endpoints in the backend code
3. Use the Network tab to see requests/responses
4. Add temporary console logs to trace the flow

Let me know if you need more specific troubleshooting guidance! 