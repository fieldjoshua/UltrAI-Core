#!/bin/bash

# Force Render to rebuild by updating cache bust arg
TIMESTAMP=$(date +%s)
sed -i.bak "s/ARG CACHE_BUST=.*/ARG CACHE_BUST=$TIMESTAMP/" Dockerfile
rm Dockerfile.bak

echo "Updated CACHE_BUST to $TIMESTAMP"
echo "Now commit and push to force rebuild:"
echo "  git add Dockerfile"
echo "  git commit -m 'Force Render rebuild'"
echo "  git push"
