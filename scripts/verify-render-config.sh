#\!/bin/bash

echo "🔍 Verifying Render Configuration..."
echo "===================================="

# Check for configuration files
echo -e "\n📄 Configuration Files:"
for file in render.yaml render-staging.yaml render-production.yaml render-frontend-staging.yaml render-frontend-production.yaml render-frontend-demo.yaml; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
    fi
done

# Check for required files
echo -e "\n📦 Required Files:"
for file in app_production.py requirements-production.txt; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
    fi
done

# Check frontend directory
echo -e "\n🎨 Frontend:"
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    echo "✅ Frontend directory exists with package.json"
else
    echo "❌ Frontend directory or package.json missing"
fi

# Check for port hardcoding issues
echo -e "\n🔌 Port Configuration:"
for file in render*.yaml; do
    if [ -f "$file" ]; then
        if grep -q "PORT.*10000" "$file"; then
            echo "❌ $file has hardcoded PORT (will fail on Render)"
        else
            echo "✅ $file has no hardcoded PORT"
        fi
    fi
done

# Check build commands
echo -e "\n🔨 Build Commands:"
for file in render*.yaml; do
    if [ -f "$file" ]; then
        echo -e "\n$file:"
        if grep -q "npm" "$file"; then
            echo "  ✅ Includes frontend build"
        else
            echo "  ⚠️  No frontend build step"
        fi
        if grep -q "pip install\|poetry install" "$file"; then
            echo "  ✅ Includes Python dependencies"
        else
            echo "  ❌ No Python dependency installation"
        fi
    fi
done

# Check environment variables
echo -e "\n🔐 API Keys Configuration:"
for file in render*.yaml; do
    if [ -f "$file" ]; then
        # Skip frontend configs for API key check
        if [[ ! "$file" =~ "frontend" ]]; then
            echo -e "\n$file:"
            for key in OPENAI_API_KEY ANTHROPIC_API_KEY GOOGLE_API_KEY; do
                if grep -q "$key" "$file"; then
                    echo "  ✅ $key configured"
                else
                    echo "  ❌ $key missing"
                fi
            done
        fi
    fi
done

# Check service architecture
echo -e "\n🏗️  Service Architecture:"
backend_count=$(ls render*-api.yaml 2>/dev/null | wc -l)
frontend_count=$(ls render-frontend*.yaml 2>/dev/null | wc -l)
echo "Backend services: $backend_count"
echo "Frontend services: $frontend_count"

# Summary
echo -e "\n📊 Summary:"
echo "==========="
echo "1. Backend services (staging/production) use pip with requirements-production.txt"
echo "2. Frontend services are separate static deployments"
echo "3. All services should NOT hardcode PORT in environment variables"
echo "4. Set API keys in Render dashboard, not in YAML files"
echo "5. Frontend services build with npm, backend services with pip"

echo -e "\n✨ Configuration verification complete!"