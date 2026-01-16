# FileFinder

A flexible Python library for searching files based on complex conditions.

## Features

- **Fluent API**: Chain conditions with `.AND()` and `.OR()`
- **High Performance**: Uses `os.scandir()` for efficient traversal
- **Lazy Evaluation**: Generator mode for large result sets
- **Rich Conditions**: Extension, size, location, name, time, and type detection
- **Configurable**: Environment-based configuration with logging

## Installation

```bash
# Using uv (recommended)
uv pip install file-finder

# Using pip
pip install file-finder

# From source
git clone <repo>
cd file-finder
uv sync --extra dev
```

## Quick Start

```python
from file_finder import FileFinder, Condition

# Create finder
finder = FileFinder(root_path='/path/to/search')

# Simple search
results = finder.search(Condition.extension('.py'))

# Complex search with AND/OR
results = finder.search(
    Condition.extension('.png', '.pdf')
    .AND(Condition.size_between(1024, 5 * 1024 * 1024))
    .OR(
        Condition.is_video()
        .AND(Condition.in_directory('videos'))
    )
)

# Process results
for file in results:
    print(file)
```

## Available Conditions

| Category | Methods |
|----------|---------|
| **Extension** | `extension()`, `is_image()`, `is_video()`, `is_document()`, `is_audio()`, `is_archive()` |
| **Size** | `size_greater_than()`, `size_less_than()`, `size_between()` |
| **Location** | `in_directory()`, `not_in_directory()`, `path_matches()` |
| **Name** | `name_contains()`, `name_equals()`, `name_matches()` |
| **Time** | `modified_within_days()`, `created_within_days()` |

## Configuration

Create a `.env` file (optional):

```bash
FILE_FINDER_LOG_LEVEL=INFO
FILE_FINDER_LOG_FILE=logs/finder.log
FILE_FINDER_FOLLOW_SYMLINKS=false
```

## Development

```bash
# Install dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run linting
uv run ruff check src tests

# Format code
uv run ruff format src tests
```

## Requirements

- Python 3.13+
- uv package manager

## License

MIT
