#!/usr/bin/env python3
"""
Cache cleanup utility for Ollama MCP Server
"""

import os
import shutil
import sys


def find_cache_directories():
    """Find all Python cache directories in the project."""
    cache_dirs = []
    cache_files = []
    
    for root, dirs, files in os.walk("."):
        # Skip .git directory
        if ".git" in root:
            continue
            
        # Check directories
        for dir_name in dirs:
            if dir_name in ["__pycache__", ".mypy_cache", ".pytest_cache"]:
                cache_dirs.append(os.path.join(root, dir_name))
        
        # Check files
        for file_name in files:
            if file_name.endswith(('.pyc', '.pyo', '.pyd')):
                cache_files.append(os.path.join(root, file_name))
    
    return cache_dirs, cache_files


def clean_cache(dry_run=True):
    """Clean up cache directories and files."""
    cache_dirs, cache_files = find_cache_directories()
    
    if not cache_dirs and not cache_files:
        print("✅ No cache files found to clean.")
        return
    
    print(f"Found {len(cache_dirs)} cache directories and "
          f"{len(cache_files)} cache files.")
    
    if dry_run:
        print("\n📋 Cache directories to remove:")
        for cache_dir in cache_dirs:
            print(f"  - {cache_dir}")
        
        print("\n📋 Cache files to remove:")
        for cache_file in cache_files:
            print(f"  - {cache_file}")
        
        print("\n💡 Run with --execute to actually remove these files.")
    else:
        print("\n🧹 Removing cache directories...")
        for cache_dir in cache_dirs:
            try:
                shutil.rmtree(cache_dir)
                print(f"  ✅ Removed: {cache_dir}")
            except Exception as e:
                print(f"  ❌ Failed to remove {cache_dir}: {e}")
        
        print("\n🧹 Removing cache files...")
        for cache_file in cache_files:
            try:
                os.remove(cache_file)
                print(f"  ✅ Removed: {cache_file}")
            except Exception as e:
                print(f"  ❌ Failed to remove {cache_file}: {e}")
        
        print("\n🎉 Cache cleanup completed!")


def main():
    """Main function."""
    print("🧹 Ollama MCP Server Cache Cleanup Utility")
    print("=" * 50)
    
    if "--execute" in sys.argv:
        confirm = input("⚠️  This will permanently delete cache files. "
                       "Continue? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ Cleanup cancelled.")
            return
        clean_cache(dry_run=False)
    else:
        clean_cache(dry_run=True)


if __name__ == "__main__":
    main() 