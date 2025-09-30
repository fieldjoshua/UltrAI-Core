#!/bin/bash

RENDER_API_KEY="rnd_NfrFXrFHdSs0kU2LfFfaWPkN6lzH"

declare -A SERVICES=(
  ["ultrai-prod-api"]="srv-ctavmajqf0us738m82v0"
  ["UltrAI"]="srv-ctavmajqf0us738m82vg"
  ["ultrai-core"]="srv-d0l9lr56ubrc73bt2bh0"
  ["demo-ultrai"]="srv-ctavmajqf0us738m82ug"
  ["ultrai-frontend"]="srv-ctavmajqf0us738m8300"
  ["ultrai-staging-api"]="srv-ctavmajqf0us738m82u0"
)

echo "Checking deploy status for all services..."
echo ""

for SERVICE_NAME in "${!SERVICES[@]}"; do
  SERVICE_ID="${SERVICES[$SERVICE_NAME]}"
  
  RESPONSE=$(curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
    "https://api.render.com/v1/services/$SERVICE_ID/deploys?limit=1")
  
  STATUS=$(echo "$RESPONSE" | jq -r '.deploys[0].status // "unknown"')
  CREATED=$(echo "$RESPONSE" | jq -r '.deploys[0].createdAt // "unknown"')
  
  echo "[$SERVICE_NAME] $STATUS (started: $CREATED)"
done