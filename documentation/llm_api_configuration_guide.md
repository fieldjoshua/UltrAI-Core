# LLM API Configuration Guide for UltraAI
*Version: 1.0*
*Last Updated: 2025-06-04*

## 🔑 Overview

UltraAI's sophisticated 4-stage Feather orchestration system integrates with three major LLM providers. This guide explains how to obtain and configure the required API keys.

## 🚀 Quick Start

### Required API Keys
1. **Anthropic (Claude)** - For nuanced analysis
2. **OpenAI (GPT-4)** - For comprehensive reasoning
3. **Google (Gemini)** - For multimodal capabilities

### Configuration Location
Add these to Render Dashboard → ultrai-core → Environment:
```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
```

## 📋 Step-by-Step Setup

### 1. Anthropic API Key (Claude)

**Getting the Key:**
1. Visit https://console.anthropic.com
2. Sign up or log in
3. Navigate to API Keys section
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-`)

**Configuration:**
```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
```

**Pricing:** ~$15/million tokens (Claude 3 Opus)

### 2. OpenAI API Key (GPT-4)

**Getting the Key:**
1. Visit https://platform.openai.com
2. Sign up or log in
3. Go to API Keys section
4. Click "Create new secret key"
5. Copy the key (starts with `sk-`)

**Configuration:**
```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

**Pricing:** ~$30/million tokens (GPT-4 Turbo)

### 3. Google API Key (Gemini)

**Getting the Key:**
1. Visit https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Select or create a project
5. Copy the key (starts with `AIza`)

**Configuration:**
```bash
GOOGLE_API_KEY=AIzaXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Pricing:** ~$7/million tokens (Gemini Pro)

## ⚙️ Configuration in Render

### Step 1: Access Environment Variables
1. Log into [Render Dashboard](https://dashboard.render.com)
2. Select `ultrai-core` service
3. Click "Environment" in left sidebar

### Step 2: Add API Keys
1. Click "Add Environment Variable"
2. Add each key:
   - Key: `ANTHROPIC_API_KEY`
   - Value: Your Anthropic API key
3. Repeat for OpenAI and Google keys
4. Click "Save Changes"

### Step 3: Restart Service
- Service will automatically redeploy
- Monitor logs for successful initialization

## 🧪 Testing Configuration

### Test Individual Providers
```bash
# Test Claude
curl -X POST https://ultrai-core.onrender.com/api/test/claude \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, Claude"}'

# Test GPT-4
curl -X POST https://ultrai-core.onrender.com/api/test/openai \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, GPT-4"}'

# Test Gemini
curl -X POST https://ultrai-core.onrender.com/api/test/gemini \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, Gemini"}'
```

### Test Full Orchestration
```bash
curl -X POST https://ultrai-core.onrender.com/api/orchestrator/feather \
  -H "Content-Type: application/json" \
  -d '{
    "pattern": "gut",
    "prompt": "Analyze the potential of AI in healthcare",
    "models": ["claude-3-opus", "gpt-4-turbo", "gemini-pro"]
  }'
```

## 💰 Cost Management

### Estimated Monthly Costs
Based on typical usage patterns:
- **Low Usage** (1K requests/month): ~$50
- **Medium Usage** (10K requests/month): ~$300
- **High Usage** (100K requests/month): ~$2,000

### Cost Optimization Tips
1. **Use Model Selection Wisely**
   - Claude for nuanced analysis
   - GPT-4 for complex reasoning
   - Gemini for cost-effective tasks

2. **Implement Caching**
   - Redis cache already configured
   - Reduces duplicate API calls

3. **Set Usage Limits**
   ```bash
   DAILY_REQUEST_LIMIT=1000
   MAX_TOKENS_PER_REQUEST=2000
   ```

## 🔒 Security Best Practices

### Key Management
1. **Never commit API keys to Git**
2. **Rotate keys regularly** (monthly recommended)
3. **Use separate keys** for dev/staging/production
4. **Monitor usage** for anomalies

### Access Control
```bash
# Restrict API key usage by IP (where supported)
ALLOWED_IPS=35.123.45.67,35.123.45.68

# Implement rate limiting
RATE_LIMIT_PER_USER=100/hour
```

## 🐛 Troubleshooting

### Common Issues

#### "Invalid API Key" Error
- Verify key is correctly copied (no extra spaces)
- Check key hasn't expired
- Ensure billing is active on provider account

#### "Rate Limit Exceeded"
- Implement exponential backoff
- Check current usage on provider dashboard
- Consider upgrading plan

#### "Model Not Found"
- Verify model names match exactly:
  - `claude-3-opus-20240229`
  - `gpt-4-turbo-preview`
  - `gemini-pro`

### Debug Mode
Enable detailed logging:
```bash
LLM_DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

## 📊 Monitoring Usage

### Provider Dashboards
- **Anthropic**: https://console.anthropic.com/usage
- **OpenAI**: https://platform.openai.com/usage
- **Google**: https://console.cloud.google.com/apis

### Internal Metrics
Monitor via Render logs:
```bash
# View recent LLM calls
grep "LLM_CALL" /var/log/ultrai/app.log

# Check error rates
grep "LLM_ERROR" /var/log/ultrai/app.log | wc -l
```

## 🔄 Migration & Backup

### Backup API Keys
1. Store encrypted copies in password manager
2. Document which keys are used where
3. Keep previous key active during rotation

### Key Rotation Process
1. Generate new key from provider
2. Add new key to Render environment
3. Deploy and test
4. Revoke old key after verification

## 📝 Configuration Checklist

Before going live:
- [ ] All three API keys configured in Render
- [ ] Keys tested individually
- [ ] Full orchestration tested
- [ ] Usage limits configured
- [ ] Monitoring alerts set up
- [ ] Backup keys documented
- [ ] Cost alerts configured
- [ ] Security review completed

## 🆘 Support Resources

### Provider Support
- **Anthropic**: support@anthropic.com
- **OpenAI**: https://help.openai.com
- **Google**: https://cloud.google.com/support

### UltraAI Integration
- Check logs: Render Dashboard → Logs
- Test endpoints: See testing section above
- Community: [GitHub Issues]

---

Remember: API keys are sensitive credentials. Treat them like passwords and never share them publicly!