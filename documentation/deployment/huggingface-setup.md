# HuggingFace Models Setup Guide

## Overview
HuggingFace models are fully integrated into the Ultra AI Core system but require an API key to be activated.

## Current Status (January 2025)
- ✅ HuggingFaceAdapter fully implemented
- ✅ Model registration logic complete
- ❌ Not available in production (API key not configured)

## Available HuggingFace Models
When configured, the following models will be available:
1. `meta-llama/Llama-2-70b-chat-hf` - Llama 2 70B Chat
2. `mistralai/Mistral-7B-Instruct-v0.1` - Mistral 7B Instruct
3. `google/flan-t5-xxl` - FLAN-T5 XXL
4. `EleutherAI/gpt-j-6B` - GPT-J 6B
5. `bigscience/bloom` - BLOOM 176B
6. `facebook/opt-66b` - OPT 66B

## Setup Instructions

### 1. Get HuggingFace API Key
1. Go to https://huggingface.co/settings/tokens
2. Create an account if needed
3. Generate a new API token with "read" permissions

### 2. Configure in Render Dashboard
1. Go to https://dashboard.render.com
2. Navigate to the `ultrai-core` service
3. Go to Environment tab
4. Add new environment variable:
   - Key: `HUGGINGFACE_API_KEY`
   - Value: Your HuggingFace API token
5. Save changes (this will trigger a redeploy)

### 3. Verify Configuration
After deployment completes:
```bash
curl https://ultrai-core.onrender.com/api/available-models | jq '.models[] | select(.provider == "huggingface")'
```

## Code Integration
The HuggingFace integration is already implemented in:
- `/app/services/llm_adapters.py` - HuggingFaceAdapter class
- `/app/services/orchestration_service.py` - Model detection logic
- `/app/routes/available_models_routes.py` - API endpoint
- `/app/config.py` - Configuration class

## Troubleshooting

### Models Not Appearing
1. Check environment variable is set: `echo $HUGGINGFACE_API_KEY`
2. Verify deployment completed successfully in Render
3. Check logs for any HuggingFace-related errors

### API Rate Limits
HuggingFace has rate limits on their free tier:
- Consider upgrading to Pro account for production use
- Implement caching to reduce API calls

## Cost Considerations
- HuggingFace Inference API is free for limited usage
- Pro account ($9/month) provides higher rate limits
- Enterprise plans available for production workloads