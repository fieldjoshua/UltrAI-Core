#!/bin/bash
# Image optimization script for background images

cd frontend/public

# Check if ImageMagick is installed
if ! command -v convert &> /dev/null; then
    echo "ImageMagick not found. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install imagemagick
    else
        echo "Please install ImageMagick first"
        exit 1
    fi
fi

# Create backup directory
mkdir -p original-images
cp bg-*.png original-images/

# Optimize each image
for img in bg-*.png; do
    echo "Optimizing $img..."
    
    # Get image dimensions
    dimensions=$(identify -format "%wx%h" "$img")
    echo "  Original size: $dimensions"
    
    # Resize if larger than 1920x1080 and compress
    convert "$img" \
        -resize '1920x1080>' \
        -quality 85 \
        -strip \
        -interlace Plane \
        -gaussian-blur 0.05 \
        -depth 8 \
        "${img%.png}-optimized.png"
    
    # Show size reduction
    original_size=$(ls -lh "$img" | awk '{print $5}')
    new_size=$(ls -lh "${img%.png}-optimized.png" | awk '{print $5}')
    echo "  Reduced from $original_size to $new_size"
    
    # Replace original with optimized
    mv "${img%.png}-optimized.png" "$img"
done

echo "✅ All images optimized! Original images backed up in original-images/"