#!/usr/bin/env python3
"""
Analyze current images in the project to identify optimization opportunities
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple

import click
from PIL import Image
from tqdm import tqdm


# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
IMAGES_DIR = PROJECT_ROOT / "workspaces" / "server" / "seeds" / "images"


def get_image_info(file_path: Path) -> Dict:
    """Get information about an image file"""
    try:
        size = file_path.stat().st_size
        with Image.open(file_path) as img:
            width, height = img.size
            format = img.format
            mode = img.mode
        
        return {
            'path': file_path,
            'size': size,
            'width': width,
            'height': height,
            'format': format,
            'mode': mode,
            'size_mb': size / 1024 / 1024
        }
    except Exception as e:
        return {
            'path': file_path,
            'error': str(e)
        }


def get_all_images(directory: Path) -> List[Path]:
    """Get all image files from directory"""
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg'}
    images = []
    for ext in image_extensions:
        images.extend(directory.rglob(f"*{ext}"))
        images.extend(directory.rglob(f"*{ext.upper()}"))
    return sorted(set(images))


@click.command()
@click.option('--input-dir', type=click.Path(exists=True), default=None,
              help='Input directory to analyze')
@click.option('--min-size', default=0.5, help='Minimum file size in MB to report')
@click.option('--sort-by', type=click.Choice(['size', 'name', 'format']), 
              default='size', help='Sort results by')
def main(input_dir, min_size, sort_by):
    """Analyze images and identify optimization opportunities"""
    
    # Set directory
    images_dir = Path(input_dir) if input_dir else IMAGES_DIR
    
    if not images_dir.exists():
        click.echo(f"Error: Directory {images_dir} does not exist", err=True)
        return
    
    click.echo(f"Analyzing images in: {images_dir}")
    click.echo("="*60)
    
    # Get all images
    image_files = get_all_images(images_dir)
    if not image_files:
        click.echo("No image files found")
        return
    
    # Analyze images
    image_infos = []
    total_size = 0
    
    with tqdm(image_files, desc="Analyzing images") as pbar:
        for img_path in pbar:
            pbar.set_description(f"Analyzing {img_path.name}")
            info = get_image_info(img_path)
            if 'error' not in info:
                image_infos.append(info)
                total_size += info['size']
    
    # Sort results
    if sort_by == 'size':
        image_infos.sort(key=lambda x: x['size'], reverse=True)
    elif sort_by == 'name':
        image_infos.sort(key=lambda x: x['path'].name)
    elif sort_by == 'format':
        image_infos.sort(key=lambda x: (x['format'], x['size']), reverse=True)
    
    # Print summary
    click.echo(f"\nTotal images: {len(image_infos)}")
    click.echo(f"Total size: {total_size / 1024 / 1024:.2f} MB")
    click.echo("")
    
    # Print format distribution
    format_stats = {}
    for info in image_infos:
        fmt = info['format'] or 'Unknown'
        if fmt not in format_stats:
            format_stats[fmt] = {'count': 0, 'size': 0}
        format_stats[fmt]['count'] += 1
        format_stats[fmt]['size'] += info['size']
    
    click.echo("Format distribution:")
    click.echo("-" * 40)
    for fmt, stats in sorted(format_stats.items()):
        click.echo(f"{fmt:10} {stats['count']:4} files, {stats['size'] / 1024 / 1024:8.2f} MB")
    click.echo("")
    
    # Print large images
    large_images = [img for img in image_infos if img['size_mb'] >= min_size]
    if large_images:
        click.echo(f"\nImages larger than {min_size} MB:")
        click.echo("-" * 80)
        click.echo(f"{'Filename':<30} {'Format':<8} {'Size (MB)':<10} {'Dimensions':<15} {'Mode':<8}")
        click.echo("-" * 80)
        
        for info in large_images[:20]:  # Show top 20
            filename = info['path'].name[:29]
            dimensions = f"{info['width']}x{info['height']}"
            click.echo(f"{filename:<30} {info['format']:<8} {info['size_mb']:>9.2f} {dimensions:<15} {info['mode']:<8}")
        
        if len(large_images) > 20:
            click.echo(f"\n... and {len(large_images) - 20} more images")
    
    # Optimization opportunities
    click.echo("\n" + "="*60)
    click.echo("Optimization opportunities:")
    click.echo("-" * 60)
    
    # PNG files that could be JPEG
    png_photos = [img for img in image_infos 
                  if img.get('format') == 'PNG' and img.get('mode') in ['RGB', 'RGBA']]
    if png_photos:
        png_size = sum(img['size'] for img in png_photos) / 1024 / 1024
        click.echo(f"- {len(png_photos)} PNG files ({png_size:.1f} MB) could potentially be converted to JPEG/WebP")
    
    # Large dimensions
    oversized = [img for img in image_infos 
                 if img.get('width', 0) > 2048 or img.get('height', 0) > 2048]
    if oversized:
        click.echo(f"- {len(oversized)} images have dimensions larger than 2048px")
    
    # Old formats
    old_formats = [img for img in image_infos 
                   if img.get('format') in ['BMP', 'TIFF']]
    if old_formats:
        click.echo(f"- {len(old_formats)} images use old formats (BMP, TIFF)")
    
    click.echo("")


if __name__ == "__main__":
    main()