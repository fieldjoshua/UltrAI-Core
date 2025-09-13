# Render Backend Environment Variables

## Required Environment Variables for UltraAI Backend

The backend deployment on Render requires these environment variables to function properly:

### Production Requirements (MINIMUM 2 PROVIDERS)

**⚠️ IMPORTANT**: Production deployments require at least 2 LLM provider API keys to ensure multi-model orchestration capabilities. The service will fail to start if this requirement is not met.

### Essential Variables

1. **JWT_SECRET** (Required)
   - Description: Secret key for JWT token generation
   - Example: Generate with: `openssl rand -base64 32`
   - Value: Any secure random string (32+ characters)

2. **At least 2 of the following LLM Provider Keys** (Required for Production):
   
   **OPENAI_API_KEY**
   - Description: OpenAI API key for GPT models
   - Format: `sk-...`
   - Get from: https://platform.openai.com/api-keys
   
   **ANTHROPIC_API_KEY**
   - Description: Anthropic API key for Claude models
   - Format: `sk-ant-...`
   - Get from: https://console.anthropic.com/
   
   **GOOGLE_API_KEY**
   - Description: Google API key for Gemini models
   - Get from: Google AI Studio
   
   **HUGGINGFACE_API_KEY**
   - Description: HuggingFace API token
   - Get from: https://huggingface.co/settings/tokens

3. **CORS_ORIGINS** (Already set)
   - Current Value: `*`
   - Description: Allows all origins for demo access

4. **MINIMUM_MODELS_REQUIRED** (Default: 2)
   - Description: Minimum number of models required for orchestration
   - Production value: Must be 2 or higher
   - Example: `2`

### Optional but Recommended

5. **ENABLE_SINGLE_MODEL_FALLBACK** (Default: false)
   - Description: Allow fallback to single model operation
   - Production recommendation: Keep as `false`
   - Example: `false`

6. **REDIS_URL**
   - Description: Redis connection for caching
   - Example: `redis://default:password@host:port`

7. **DATABASE_URL** 
   - Description: PostgreSQL connection string
   - Example: `postgresql://user:password@host:port/dbname`

### How to Add in Render

1. Go to your Render dashboard
2. Select the "ultrai-core" service
3. Go to "Environment" tab
4. Click "Add Environment Variable"
5. Add each variable with its value
6. Save changes - service will auto-redeploy

### Quick Start

#### For Development/Testing:
```
JWT_SECRET=your-super-secret-key-here-make-it-long
OPENAI_API_KEY=sk-your-openai-api-key-here
ENVIRONMENT=development
```

#### For Production (Minimum Requirements):
```
JWT_SECRET=your-super-secret-key-here-make-it-long
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
ENVIRONMENT=production
MINIMUM_MODELS_REQUIRED=2
ENABLE_SINGLE_MODEL_FALLBACK=false
```

**Note**: Production requires at least 2 provider API keys. The service will not start without them!