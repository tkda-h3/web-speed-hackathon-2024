#!/usr/bin/env python3
"""
Copy optimized images back to the server directory
Preserves original filenames and adds WebP variants
"""

import shutil
from pathlib import Path

import click
from tqdm import tqdm


# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "python" / "output"
TARGET_DIR = PROJECT_ROOT / "workspaces" / "server" / "seeds" / "images"


@click.command()
@click.option('--dry-run', is_flag=True, help='Show what would be copied without actually copying')
@click.option('--webp-only', is_flag=True, help='Only copy WebP files, not optimized originals')
def main(dry_run, webp_only):
    """Copy optimized images to server directory"""
    
    if not OUTPUT_DIR.exists():
        click.echo(f"Error: Output directory {OUTPUT_DIR} does not exist", err=True)
        click.echo("Run optimize_images.py first", err=True)
        return
    
    # Get all files to copy
    files_to_copy = []
    
    if webp_only:
        # Only WebP files
        webp_files = list(OUTPUT_DIR.glob("*.webp"))
        files_to_copy = [(f, TARGET_DIR / f.name) for f in webp_files]
    else:
        # All optimized files
        all_files = list(OUTPUT_DIR.glob("*.*"))
        files_to_copy = [(f, TARGET_DIR / f.name) for f in all_files]
    
    if not files_to_copy:
        click.echo("No files to copy")
        return
    
    # Show summary
    click.echo(f"Found {len(files_to_copy)} files to copy")
    click.echo(f"Target directory: {TARGET_DIR}")
    
    if dry_run:
        click.echo("\nDRY RUN - Files that would be copied:")
        for src, dst in files_to_copy[:10]:
            click.echo(f"  {src.name} -> {dst}")
        if len(files_to_copy) > 10:
            click.echo(f"  ... and {len(files_to_copy) - 10} more files")
        return
    
    # Copy files
    copied = 0
    with tqdm(files_to_copy, desc="Copying files") as pbar:
        for src, dst in pbar:
            pbar.set_description(f"Copying {src.name}")
            try:
                shutil.copy2(src, dst)
                copied += 1
            except Exception as e:
                click.echo(f"\nError copying {src.name}: {e}", err=True)
    
    click.echo(f"\nSuccessfully copied {copied} files to {TARGET_DIR}")


if __name__ == "__main__":
    main()