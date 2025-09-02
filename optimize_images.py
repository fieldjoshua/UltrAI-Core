#!/usr/bin/env python3
"""
Optimize background images for the demo
Requires: pip install pillow
"""

import os
from PIL import Image
import glob

def optimize_image(input_path, max_width=1920, max_height=1080, quality=85):
    """Optimize a single image"""
    print(f"Processing {input_path}...")
    
    # Open image
    img = Image.open(input_path)
    original_size = os.path.getsize(input_path)
    
    # Convert RGBA to RGB if needed (for JPEG)
    if img.mode in ('RGBA', 'LA'):
        background = Image.new('RGB', img.size, (0, 0, 0))
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    
    # Calculate new size while maintaining aspect ratio
    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    
    # Save optimized version
    output_path = input_path.replace('.png', '_optimized.png')
    img.save(output_path, 'PNG', optimize=True, quality=quality)
    
    # Also save as JPEG for even smaller size
    jpeg_path = input_path.replace('.png', '.jpg')
    img.save(jpeg_path, 'JPEG', quality=quality, optimize=True)
    
    new_size_png = os.path.getsize(output_path)
    new_size_jpg = os.path.getsize(jpeg_path)
    
    print(f"  Original: {original_size / 1024 / 1024:.1f}MB")
    print(f"  PNG: {new_size_png / 1024 / 1024:.1f}MB ({(1 - new_size_png/original_size)*100:.0f}% reduction)")
    print(f"  JPEG: {new_size_jpg / 1024 / 1024:.1f}MB ({(1 - new_size_jpg/original_size)*100:.0f}% reduction)")
    
    return output_path, jpeg_path

def main():
    # Change to public directory
    os.chdir('frontend/public')
    
    # Find all background images
    images = glob.glob('bg-*.png')
    
    if not images:
        print("No background images found!")
        return
    
    print(f"Found {len(images)} images to optimize\n")
    
    # Create backup directory
    os.makedirs('original-images', exist_ok=True)
    
    for img_path in images:
        # Backup original
        backup_path = os.path.join('original-images', img_path)
        if not os.path.exists(backup_path):
            os.rename(img_path, backup_path)
            os.system(f'cp "{backup_path}" "{img_path}"')
        
        # Optimize
        try:
            png_path, jpg_path = optimize_image(img_path)
            print(f"✅ Created {png_path} and {jpg_path}\n")
        except Exception as e:
            print(f"❌ Error processing {img_path}: {e}\n")
    
    print("\n🎉 Done! Original images are backed up in original-images/")
    print("You can now use either the _optimized.png or .jpg versions")

if __name__ == "__main__":
    # Check if Pillow is installed
    try:
        from PIL import Image
    except ImportError:
        print("Pillow not installed. Run: pip install pillow")
        exit(1)
    
    main()