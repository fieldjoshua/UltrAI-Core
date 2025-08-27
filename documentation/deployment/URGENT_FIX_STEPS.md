# 🚨 URGENT: Two Simple Fixes to Make UltraAI Work

## Fix #1: Vercel (2 minutes)
1. Go to: https://vercel.com/dashboard
2. Click on your "ultr-ai-core" project
3. Go to Settings → General
4. Find "Root Directory"
5. Change it to: `frontend`
6. Click Save
7. Vercel will auto-redeploy ✅

## Fix #2: Render (3 minutes)
1. Go to: https://dashboard.render.com
2. Click on "ultrai-core" service
3. Go to "Environment" tab
4. Add these variables:
   ```
   JWT_SECRET = anysecurerandomstringover32characters
   OPENAI_API_KEY = sk-[your-openai-key-here]
   ```
5. Click "Save Changes"
6. Render will auto-redeploy ✅

## That's It! 🎉

After both fixes (5 minutes total):
- Frontend: https://ultr-ai-core.vercel.app
- Backend: https://ultrai-core-4lut.onrender.com

The sophisticated 4-stage Feather orchestration will be live!