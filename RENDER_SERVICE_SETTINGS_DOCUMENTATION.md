# Render Service Settings Documentation

## Backend Service Configuration

### Health Check Path
- **Staging**: `/api/health` (configured in render-staging.yaml)
- **Production**: `/api/health` (configured in render-production.yaml)

### Required Environment Variables

#### Core Environment Flags
The following environment variables must be set in both staging and production services:

```yaml
# Required for all services
RAG_ENABLED: "false"
MINIMUM_MODELS_REQUIRED: "3"
ENABLE_SINGLE_MODEL_FALLBACK: "false"

# Production-specific
ALLOW_PUBLIC_ORCHESTRATION: "false"  # Only for production
```

#### Current Status
- ✅ **Health Check Path**: Both services have `/api/health` configured
- ❌ **RAG_ENABLED**: Missing from both configurations
- ❌ **MINIMUM_MODELS_REQUIRED**: Missing from both configurations  
- ❌ **ENABLE_SINGLE_MODEL_FALLBACK**: Missing from both configurations
- ❌ **ALLOW_PUBLIC_ORCHESTRATION**: Missing from production configuration

### Service Configuration Details

#### ultrai-staging-api (Staging)
- **URL**: https://ultrai-staging-api.onrender.com
- **Branch**: main
- **Auto-deploy**: Yes
- **Build Command**: `pip install -r requirements-production.txt`
- **Start Command**: `python app_production.py`
- **Health Check**: `/api/health`
- **Plan**: free

#### ultrai-prod-api (Production)
- **URL**: https://ultrai-prod-api.onrender.com
- **Branch**: main
- **Auto-deploy**: No (manual only)
- **Build Command**: `pip install -r requirements-production.txt`
- **Start Command**: `python app_production.py`
- **Health Check**: `/api/health`
- **Plan**: free

### Environment Variable Management

#### No Service-Level Secrets
- All API keys should be managed through Render's Environment Groups
- No secrets should be stored in the render.yaml files
- Use `sync: false` for sensitive variables to indicate they're set in dashboard

#### Required API Keys (set in dashboard)
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- `HUGGINGFACE_API_KEY`

### CORS Configuration
- **Staging**: Allows staging frontend and localhost development
- **Production**: Allows production domains and demo site

## Action Items

### Immediate Actions Required
1. **Add missing environment variables** to both render configurations:
   - `RAG_ENABLED=false`
   - `MINIMUM_MODELS_REQUIRED=3`
   - `ENABLE_SINGLE_MODEL_FALLBACK=false`
   - `ALLOW_PUBLIC_ORCHESTRATION=false` (production only)

2. **Verify health check endpoint** exists at `/api/health` in the application

3. **Confirm API keys** are set in Render dashboard (not in config files)

### Verification Steps
1. Check staging service health: `curl https://ultrai-staging-api.onrender.com/api/health`
2. Check production service health: `curl https://ultrai-prod-api.onrender.com/api/health`
3. Verify environment variables in Render dashboard
4. Test deployment pipeline (staging auto-deploys, production manual)

## Netlify Configuration

### Frontend Deployment
- **Base Directory**: `frontend`
- **Publish Directory**: `dist`
- **Build Command**: `npm ci && npm run build`
- **Deploy Preview**: Uses staging API (`https://ultrai-staging-api.onrender.com`)
- **SPA Redirects**: All routes redirect to `/index.html` with 200 status

The `netlify.toml` file is already correctly configured and present in the repository.