#!/usr/bin/env python3
"""
Demo script for FileFinder library.

This script demonstrates various search capabilities.
Run it from any directory to see FileFinder in action.
"""

from pathlib import Path

from file_finder import Condition, FileFinder


def print_section(title):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def print_results(results, max_display=10):
    """Print search results with a limit."""
    results_list = list(results) if not isinstance(results, list) else results
    
    if not results_list:
        print("  No files found.")
        return
    
    print(f"  Found {len(results_list)} file(s):")
    for i, path in enumerate(results_list[:max_display], 1):
        size = path.stat().st_size if path.exists() else 0
        size_str = f"{size:,} bytes"
        if size > 1024 * 1024:
            size_str = f"{size / (1024 * 1024):.2f} MB"
        elif size > 1024:
            size_str = f"{size / 1024:.2f} KB"
        print(f"    {i}. {path.name} ({size_str})")
    
    if len(results_list) > max_display:
        print(f"    ... and {len(results_list) - max_display} more")


def main():
    """Run demo searches."""
    
    print("\nFileFinder Library Demo")
    print("=" * 60)
    
    # Use current directory as search root
    current_dir = Path.cwd()
    print(f"\nSearching in: {current_dir}")
    
    finder = FileFinder(root_path=str(current_dir))
    
    # Demo 1: Find all Python files
    print_section("Demo 1: All Python Files")
    results = finder.search(Condition.extension('.py'))
    print_results(results)
    
    # Demo 2: Find Python files in current directory only (not subdirs)
    print_section("Demo 2: Python Files (Current Directory Only)")
    results = finder.search(
        Condition.extension('.py'),
        recursive=False
    )
    print_results(results)
    
    # Demo 3: Find all image files
    print_section("Demo 3: All Image Files")
    results = finder.search(Condition.is_image())
    print_results(results)
    
    # Demo 4: Find files with specific name
    print_section("Demo 4: Files Named 'README.md'")
    results = finder.search(Condition.name_equals('README.md'))
    print_results(results)
    
    # Demo 5: Complex query - Python files modified recently
    print_section("Demo 5: Python Files Modified in Last 7 Days")
    results = finder.search(
        Condition.extension('.py')
        .AND(Condition.modified_within_days(7))
    )
    print_results(results)
    
    # Demo 6: Files containing 'demo' or 'test' in name
    print_section("Demo 6: Files with 'demo' OR 'test' in Name")
    results = finder.search(
        Condition.name_contains('demo')
        .OR(Condition.name_contains('test'))
    )
    print_results(results)
    
    # Demo 7: Large files (> 1MB)
    print_section("Demo 7: Files Larger Than 1MB")
    results = finder.search(Condition.size_greater_than(1 * 1024 * 1024))
    print_results(results)
    
    # Demo 8: Complex query - Your original example
    print_section("Demo 8: Complex Query Example")
    print("  Searching for: Markdown or Python files between 100 bytes and 100KB")
    print("                 OR any image files")
    results = finder.search(
        Condition.extension('.md', '.py')
        .AND(Condition.size_between(100, 100 * 1024))
        .OR(Condition.is_image())
    )
    print_results(results)
    
    # Demo 9: Lazy evaluation (generator mode)
    print_section("Demo 9: Lazy Evaluation (First 5 Results)")
    results_gen = finder.search(
        Condition.extension('.py', '.md', '.txt'),
        lazy=True,
        max_results=5
    )
    print("  Using generator mode (memory-efficient):")
    count = 0
    for path in results_gen:
        count += 1
        print(f"    {count}. {path.name}")
    
    # Demo 10: Regex pattern matching
    print_section("Demo 10: Files Matching Regex Pattern")
    print("  Pattern: Files starting with 'file' or 'demo'")
    results = finder.search(Condition.name_matches(r'^(file|demo).*'))
    print_results(results)
    
    # Demo 11: Exclude directories
    print_section("Demo 11: Python Files (Excluding Common Directories)")
    print("  Excluding: __pycache__, .git, node_modules")
    results = finder.search(
        Condition.extension('.py')
        .AND(Condition.not_in_directory('__pycache__', '.git', 'node_modules'))
    )
    print_results(results)
    
    # Demo 12: Type detection helpers
    print_section("Demo 12: Type Detection Helpers")
    print("\n  Documents:")
    docs = finder.search(Condition.is_document())
    print_results(docs, max_display=5)
    
    print("\n  Archives:")
    archives = finder.search(Condition.is_archive())
    print_results(archives, max_display=5)
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
