#!/bin/bash
# Batch optimization script for Web Speed Hackathon 2024

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "==================================="
echo "Web Speed Hackathon 2024"
echo "Batch Image Optimization Script"
echo "==================================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
uv sync

echo ""
echo "==================================="
echo "Step 1: Analyzing current images"
echo "==================================="
python analyze_images.py

echo ""
echo "==================================="
echo "Step 2: Optimizing images"
echo "==================================="
echo "Converting to WebP format..."
python optimize_images.py --formats webp --formats original --quality 85

echo ""
echo "==================================="
echo "Step 3: Analyzing optimization results"
echo "==================================="
python analyze_images.py --input-dir output

echo ""
echo "==================================="
echo "Step 4: Copying optimized images"
echo "==================================="
echo "Would you like to copy WebP images to the server directory? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    python copy_optimized_images.py --webp-only
    echo "WebP images copied successfully!"
else
    echo "Skipped copying images."
fi

echo ""
echo "==================================="
echo "Optimization complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Commit the WebP images to your repository"
echo "2. Deploy the updated server with WebP support"
echo "3. Monitor performance improvements"
echo ""