#!/usr/bin/env python3
"""
Image optimization script for Web Speed Hackathon 2024
Optimizes images by converting to modern formats and reducing file sizes
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

import click
from PIL import Image
from tqdm import tqdm

# Enable AVIF support
import pillow_avif_plugin

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
IMAGES_DIR = PROJECT_ROOT / "workspaces" / "server" / "seeds" / "images"
OUTPUT_DIR = PROJECT_ROOT / "python" / "output"


def get_image_files(directory: Path) -> List[Path]:
    """Get all image files from directory"""
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    return [f for f in directory.rglob("*") if f.suffix.lower() in image_extensions]


def optimize_image(
    input_path: Path,
    output_dir: Path,
    max_width: int = 2048,
    max_height: int = 2048,
    quality: int = 85,
    formats: List[str] = None
) -> List[Tuple[Path, int]]:
    """
    Optimize a single image
    Returns list of (output_path, file_size) tuples
    """
    if formats is None:
        formats = ['webp', 'avif', 'original']
    
    results = []
    
    try:
        # Open image
        img = Image.open(input_path)
        
        # Convert RGBA to RGB if needed for JPEG output
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        
        # Calculate new dimensions while maintaining aspect ratio
        width, height = img.size
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create output directory
        relative_path = input_path.relative_to(IMAGES_DIR)
        file_output_dir = output_dir / relative_path.parent
        file_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save in different formats
        base_name = relative_path.stem
        
        for fmt in formats:
            if fmt == 'webp':
                output_path = file_output_dir / f"{base_name}.webp"
                img.save(output_path, 'WEBP', quality=quality, method=6)
                results.append((output_path, output_path.stat().st_size))
            
            elif fmt == 'avif':
                output_path = file_output_dir / f"{base_name}.avif"
                img.save(output_path, 'AVIF', quality=quality)
                results.append((output_path, output_path.stat().st_size))
            
            elif fmt == 'original':
                # Save optimized version in original format
                output_path = file_output_dir / relative_path.name
                if input_path.suffix.lower() in ['.jpg', '.jpeg']:
                    img.save(output_path, 'JPEG', quality=quality, optimize=True)
                elif input_path.suffix.lower() == '.png':
                    img.save(output_path, 'PNG', optimize=True)
                else:
                    img.save(output_path)
                results.append((output_path, output_path.stat().st_size))
    
    except Exception as e:
        click.echo(f"Error processing {input_path}: {e}", err=True)
    
    return results


@click.command()
@click.option('--input-dir', type=click.Path(exists=True), default=None,
              help='Input directory (default: workspaces/server/seeds/images)')
@click.option('--output-dir', type=click.Path(), default=None,
              help='Output directory (default: python/output)')
@click.option('--max-width', default=2048, help='Maximum width in pixels')
@click.option('--max-height', default=2048, help='Maximum height in pixels')
@click.option('--quality', default=85, help='JPEG/WebP quality (1-100)')
@click.option('--formats', multiple=True, default=['webp', 'avif', 'original'],
              help='Output formats (webp, avif, original)')
def main(input_dir, output_dir, max_width, max_height, quality, formats):
    """Optimize images for Web Speed Hackathon 2024"""
    
    # Set directories
    images_dir = Path(input_dir) if input_dir else IMAGES_DIR
    output_dir = Path(output_dir) if output_dir else OUTPUT_DIR
    
    if not images_dir.exists():
        click.echo(f"Error: Input directory {images_dir} does not exist", err=True)
        sys.exit(1)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all image files
    image_files = get_image_files(images_dir)
    if not image_files:
        click.echo("No image files found")
        return
    
    click.echo(f"Found {len(image_files)} images to optimize")
    click.echo(f"Output directory: {output_dir}")
    click.echo(f"Formats: {', '.join(formats)}")
    
    # Process images
    total_original_size = 0
    total_optimized_size = 0
    
    with tqdm(image_files, desc="Optimizing images") as pbar:
        for img_path in pbar:
            pbar.set_description(f"Processing {img_path.name}")
            
            # Get original size
            original_size = img_path.stat().st_size
            total_original_size += original_size
            
            # Optimize image
            results = optimize_image(
                img_path, output_dir,
                max_width=max_width,
                max_height=max_height,
                quality=quality,
                formats=list(formats)
            )
            
            # Track optimized sizes
            for output_path, size in results:
                if output_path.suffix == img_path.suffix:
                    total_optimized_size += size
    
    # Print summary
    click.echo("\n" + "="*50)
    click.echo("Optimization Summary:")
    click.echo(f"Total original size: {total_original_size / 1024 / 1024:.2f} MB")
    click.echo(f"Total optimized size: {total_optimized_size / 1024 / 1024:.2f} MB")
    click.echo(f"Size reduction: {(1 - total_optimized_size/total_original_size) * 100:.1f}%")
    click.echo(f"Output directory: {output_dir}")


if __name__ == "__main__":
    main()