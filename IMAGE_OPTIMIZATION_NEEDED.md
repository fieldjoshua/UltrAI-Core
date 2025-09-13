# Background Image Optimization Needed

## Current Issue
The background images are too large, causing slow loading and potential pixelation:
- bg-night.png: 36MB
- bg-afternoon.png: 21MB  
- bg-sunset.png: 18MB
- bg-morning.png: 14MB

## Recommended Solution

### Option 1: Use an online optimizer
1. Go to https://tinypng.com/ or https://squoosh.app/
2. Upload each bg-*.png file
3. Download the optimized versions
4. Replace the files in `/public/`

### Option 2: Use sharp/imagemin locally
```bash
npm install -D sharp-cli
npx sharp -i public/bg-night.png -o public/bg-night-optimized.png resize 1920 1080 -- quality 85
```

### Option 3: Convert to WebP format
```bash
# Install cwebp
brew install webp

# Convert images
cwebp -q 80 public/bg-night.png -o public/bg-night.webp
```

## Temporary Fix Applied
I'll implement lazy loading and blur-up technique to improve perceived performance.

## Target Sizes
- Each image should be < 500KB
- Resolution: 1920x1080 max
- Format: WebP preferred, PNG fallback
- Quality: 80-85%