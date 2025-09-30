#!/bin/bash

RENDER_API_KEY="rnd_NfrFXrFHdSs0kU2LfFfaWPkN6lzH"

SERVICES="ultrai-prod-api:srv-d2qdi27diees73cscfb0
ultrai-staging-api:srv-d2qkdaadbo4c73c876rg
ultrai-prod-ui:srv-d2qdepje5dus73btqt10
ultrai-demo:srv-d2qcrifdiees73crqpkg
ultrai-staging-ui:srv-d2qkelp5pdvs738aq6mg"

echo "Checking deploy status for all services..."
echo ""

echo "$SERVICES" | while IFS=: read -r SERVICE_NAME SERVICE_ID; do
  RESPONSE=$(curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
    "https://api.render.com/v1/services/$SERVICE_ID/deploys?limit=1")
  
  STATUS=$(echo "$RESPONSE" | jq -r '.[0].deploy.status // "unknown"')
  CREATED=$(echo "$RESPONSE" | jq -r '.[0].deploy.createdAt // "unknown"' | cut -d'T' -f1,2 | tr 'T' ' ')
  BRANCH=$(curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
    "https://api.render.com/v1/services/$SERVICE_ID" | jq -r '.branch')
  
  echo "[$SERVICE_NAME] $STATUS on $BRANCH (started: $CREATED)"
done