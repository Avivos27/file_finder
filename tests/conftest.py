"""Pytest configuration and fixtures."""

import shutil
import sys
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def temp_dir() -> Generator[Path]:
    """Create a temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_files(temp_dir: Path) -> Path:
    """
    Create a sample file structure for testing.

    Structure:
        temp_dir/
        ├── file1.txt (100 bytes)
        ├── file2.py (200 bytes)
        ├── image.png (50 bytes)
        ├── document.pdf (150 bytes)
        ├── subdir1/
        │   ├── file3.txt (300 bytes)
        │   ├── video.mp4 (500 bytes)
        │   └── subdir2/
        │       └── deep_file.txt (75 bytes)
        └── subdir3/
            ├── large_file.dat (2MB)
            └── backup.bak (100 bytes)
    """
    # Root level files
    (temp_dir / "file1.txt").write_text("x" * 100)
    (temp_dir / "file2.py").write_text("x" * 200)
    (temp_dir / "image.png").write_text("x" * 50)
    (temp_dir / "document.pdf").write_text("x" * 150)

    # Subdirectory 1
    subdir1 = temp_dir / "subdir1"
    subdir1.mkdir()
    (subdir1 / "file3.txt").write_text("x" * 300)
    (subdir1 / "video.mp4").write_text("x" * 500)

    # Deep subdirectory
    subdir2 = subdir1 / "subdir2"
    subdir2.mkdir()
    (subdir2 / "deep_file.txt").write_text("x" * 75)

    # Subdirectory 3
    subdir3 = temp_dir / "subdir3"
    subdir3.mkdir()
    (subdir3 / "large_file.dat").write_text("x" * (2 * 1024 * 1024))  # 2MB
    (subdir3 / "backup.bak").write_text("x" * 100)

    return temp_dir


@pytest.fixture
def empty_dir(temp_dir: Path) -> Path:
    """Create an empty directory for testing."""
    return temp_dir


@pytest.fixture
def nested_dirs(temp_dir: Path) -> Path:
    """Create deeply nested directory structure."""
    current = temp_dir
    for i in range(10):
        current = current / f"level{i}"
        current.mkdir()
        (current / f"file{i}.txt").write_text(f"Level {i}")
    return temp_dir
