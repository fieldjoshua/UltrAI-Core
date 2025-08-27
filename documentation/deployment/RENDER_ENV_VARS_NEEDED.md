# Render Backend Environment Variables

## Required Environment Variables for UltraAI Backend

The backend deployment on Render requires these environment variables to function properly:

### Essential Variables (Minimum for Demo)

1. **JWT_SECRET** (Required)
   - Description: Secret key for JWT token generation
   - Example: Generate with: `openssl rand -base64 32`
   - Value: Any secure random string (32+ characters)

2. **OPENAI_API_KEY** (Required for LLM functionality)
   - Description: OpenAI API key for GPT models
   - Format: `sk-...`
   - Get from: https://platform.openai.com/api-keys

3. **CORS_ORIGINS** (Already set)
   - Current Value: `*`
   - Description: Allows all origins for demo access

### Optional but Recommended

4. **ANTHROPIC_API_KEY**
   - Description: Anthropic API key for Claude models
   - Format: `sk-ant-...`
   - Get from: https://console.anthropic.com/

5. **GOOGLE_API_KEY**
   - Description: Google API key for Gemini models
   - Get from: Google AI Studio

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

### Quick Start (Minimum for Demo)

Just add these two:
```
JWT_SECRET=your-super-secret-key-here-make-it-long
OPENAI_API_KEY=sk-your-openai-api-key-here
```

The system will work in demo mode with just these variables!