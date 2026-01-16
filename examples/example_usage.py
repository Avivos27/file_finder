#!/usr/bin/env python3
"""
Example usage of FileFinder in another project.

This demonstrates how you would import and use the FileFinder library
in your other projects.
"""

from file_finder import Condition, FileFinder


def example_1_basic_search():
    """Basic file search examples."""
    print("Example 1: Basic Searches")
    print("-" * 50)
    
    # Search from home directory
    finder = FileFinder(root_path='/Users/asulin/Desktop')
    
    # Find all Python files
    python_files = finder.search(Condition.extension('.py'))
    print(f"Found {len(python_files)} Python files")
    
    # Find all images
    images = finder.search(Condition.is_image())
    print(f"Found {len(images)} image files")
    
    print()


def example_2_your_use_case():
    """Your original use case: PNG/PDF with size constraints OR videos in folder."""
    print("Example 2: Your Original Use Case")
    print("-" * 50)
    
    finder = FileFinder(root_path='/Users/asulin/Desktop')
    
    # Files that are .png or .pdf with size between 1KB and 5MB
    # OR video files in a specific folder
    results = finder.search(
        Condition.extension('.png', '.pdf')
        .AND(Condition.size_between(1024, 5 * 1024 * 1024))
        .OR(
            Condition.is_video()
            .AND(Condition.in_directory('/Users/asulin/Desktop/videos'))
        )
    )
    
    print(f"Found {len(results)} matching files")
    for file in results[:5]:  # Show first 5
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"  - {file.name} ({size_mb:.2f} MB)")
    
    print()


def example_3_cleanup_old_files():
    """Find and potentially clean up old temporary files."""
    print("Example 3: Finding Old Temporary Files")
    print("-" * 50)
    
    finder = FileFinder(root_path='/tmp')
    
    # Find temp files older than 7 days
    old_temps = finder.search(
        Condition.name_contains('temp')
        .OR(Condition.name_contains('tmp'))
        .AND(Condition.modified_within_days(7)),
        lazy=True  # Use generator for potentially many results
    )
    
    count = 0
    for file in old_temps:
        count += 1
        if count <= 5:
            print(f"  - {file}")
    
    print(f"Found {count} old temporary files")
    print()


def example_4_media_organizer():
    """Organize media files by type and size."""
    print("Example 4: Media Organizer")
    print("-" * 50)
    
    finder = FileFinder(root_path='/Users/asulin/Desktop')
    
    # Find large videos for archival
    large_videos = finder.search(
        Condition.is_video()
        .AND(Condition.size_greater_than(100 * 1024 * 1024)),  # > 100MB
        max_results=10
    )
    
    print(f"Large videos (>100MB): {len(large_videos)}")
    
    # Find small images for quick review
    small_images = finder.search(
        Condition.is_image()
        .AND(Condition.size_less_than(100 * 1024)),  # < 100KB
        max_results=10
    )
    
    print(f"Small images (<100KB): {len(small_images)}")
    print()


def example_5_backup_finder():
    """Find recent backup files."""
    print("Example 5: Recent Backup Files")
    print("-" * 50)
    
    finder = FileFinder(root_path='/Users/asulin')
    
    # Find backup files from last week
    backups = finder.search(
        Condition.name_contains('backup')
        .OR(Condition.extension('.bak', '.backup'))
        .AND(Condition.modified_within_days(7))
        .AND(Condition.size_greater_than(1024)),  # Ignore empty files
        lazy=True
    )
    
    for i, backup in enumerate(backups, 1):
        if i <= 5:
            size_mb = backup.stat().st_size / (1024 * 1024)
            print(f"  {i}. {backup.name} ({size_mb:.2f} MB)")
    
    print()


def example_6_code_search():
    """Find source code files excluding dependencies."""
    print("Example 6: Source Code Search")
    print("-" * 50)
    
    finder = FileFinder(root_path='/Users/asulin/Desktop/dev')
    
    # Find Python files, excluding common dependency directories
    source_files = finder.search(
        Condition.extension('.py')
        .AND(Condition.not_in_directory('venv', 'node_modules', '.git', '__pycache__', 'dist'))
        .AND(Condition.size_greater_than(100)),  # Ignore tiny files
        max_results=20
    )
    
    print(f"Found {len(source_files)} Python source files")
    for file in source_files[:5]:
        print(f"  - {file}")
    
    print()


def example_7_performance_demo():
    """Demonstrate performance features."""
    print("Example 7: Performance Features")
    print("-" * 50)
    
    # Lazy evaluation for memory efficiency
    finder = FileFinder(
        root_path='/Users/asulin',
        follow_symlinks=False,  # Faster
        max_depth=3  # Only search 3 levels deep
    )
    
    # Use generator to process files as found
    results = finder.search(
        Condition.extension('.txt', '.md'),
        lazy=True,
        max_results=100  # Stop after 100 matches
    )
    
    # Process files one at a time (memory efficient)
    total_size = 0
    count = 0
    for file in results:
        total_size += file.stat().st_size
        count += 1
    
    print(f"Processed {count} files")
    print(f"Total size: {total_size / (1024 * 1024):.2f} MB")
    print()


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("FileFinder Library - Usage Examples")
    print("=" * 50 + "\n")
    
    # Run all examples
    example_1_basic_search()
    example_2_your_use_case()
    example_3_cleanup_old_files()
    example_4_media_organizer()
    example_5_backup_finder()
    example_6_code_search()
    example_7_performance_demo()
    
    print("=" * 50)
    print("All examples complete!")
    print("=" * 50 + "\n")
