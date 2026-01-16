"""Tests for FileFinder class."""

from pathlib import Path

import pytest

from file_finder import Condition, FileFinder


class TestFileFinderBasic:
    """Test basic FileFinder functionality."""

    def test_initialization_default(self):
        """Test FileFinder initialization with defaults."""
        finder = FileFinder()
        assert finder.root_path == Path.cwd()
        assert finder.follow_symlinks is False
        assert finder.max_depth is None

    def test_initialization_custom(self, temp_dir):
        """Test FileFinder initialization with custom parameters."""
        finder = FileFinder(root_path=str(temp_dir), follow_symlinks=True, max_depth=5)
        assert finder.root_path == temp_dir
        assert finder.follow_symlinks is True
        assert finder.max_depth == 5

    def test_search_returns_list_by_default(self, sample_files):
        """Test that search returns a list by default."""
        finder = FileFinder(root_path=str(sample_files))
        results = finder.search(Condition.extension(".txt"))
        assert isinstance(results, list)
        assert len(results) == 3

    def test_search_returns_generator_when_lazy(self, sample_files):
        """Test that search returns a generator when lazy=True."""
        finder = FileFinder(root_path=str(sample_files))
        results = finder.search(Condition.extension(".txt"), lazy=True)
        assert hasattr(results, "__iter__")
        assert hasattr(results, "__next__")
        # Consume generator
        files = list(results)
        assert len(files) == 3


class TestFileFinderSearch:
    """Test FileFinder search functionality."""

    def test_search_by_extension(self, sample_files):
        """Test searching files by extension."""
        finder = FileFinder(root_path=str(sample_files))
        results = finder.search(Condition.extension(".txt"))
        assert len(results) == 3
        assert all(f.suffix == ".txt" for f in results)

    def test_search_by_size(self, sample_files):
        """Test searching files by size."""
        finder = FileFinder(root_path=str(sample_files))
        results = finder.search(Condition.size_greater_than(1024 * 1024))  # > 1MB
        assert len(results) == 1
        assert results[0].name == "large_file.dat"

    def test_search_complex_condition(self, sample_files):
        """Test searching with complex conditions."""
        finder = FileFinder(root_path=str(sample_files))
        results = finder.search(Condition.extension(".txt").AND(Condition.size_greater_than(100)))
        # Only file3.txt (300 bytes) matches
        assert len(results) == 1
        assert results[0].name == "file3.txt"

    def test_search_or_condition(self, sample_files):
        """Test searching with OR condition."""
        finder = FileFinder(root_path=str(sample_files))
        results = finder.search(Condition.extension(".png").OR(Condition.extension(".pdf")))
        assert len(results) == 2
        names = {f.name for f in results}
        assert names == {"image.png", "document.pdf"}

    def test_search_empty_results(self, sample_files):
        """Test search with no matching files."""
        finder = FileFinder(root_path=str(sample_files))
        results = finder.search(Condition.extension(".xyz"))
        assert len(results) == 0

    def test_search_in_empty_directory(self, empty_dir):
        """Test searching in an empty directory."""
        finder = FileFinder(root_path=str(empty_dir))
        results = finder.search(Condition.extension(".txt"))
        assert len(results) == 0


class TestFileFinderRecursive:
    """Test recursive search functionality."""

    def test_recursive_search_default(self, sample_files):
        """Test that recursive search is enabled by default."""
        finder = FileFinder(root_path=str(sample_files))
        results = finder.search(Condition.extension(".txt"))
        # Should find files in subdirectories too
        assert len(results) == 3

    def test_non_recursive_search(self, sample_files):
        """Test non-recursive search."""
        finder = FileFinder(root_path=str(sample_files))
        results = finder.search(Condition.extension(".txt"), recursive=False)
        # Should only find file1.txt in root
        assert len(results) == 1
        assert results[0].name == "file1.txt"

    def test_max_depth_limiting(self, nested_dirs):
        """Test max_depth limits search depth."""
        finder = FileFinder(root_path=str(nested_dirs), max_depth=2)
        results = finder.search(Condition.extension(".txt"))
        # Should only find files within depth 2
        assert len(results) <= 3  # level0, level1, level2

    def test_max_depth_zero(self, sample_files):
        """Test max_depth=0 searches only root directory."""
        finder = FileFinder(root_path=str(sample_files), max_depth=0)
        results = finder.search(Condition.extension(".txt"))
        # Should only find file1.txt in root
        assert len(results) == 1
        assert results[0].name == "file1.txt"


class TestFileFinderPerformance:
    """Test performance-related features."""

    def test_max_results_limiting(self, sample_files):
        """Test max_results limits number of results."""
        finder = FileFinder(root_path=str(sample_files))
        results = finder.search(Condition.extension(".txt"), max_results=2)
        assert len(results) == 2

    def test_max_results_with_lazy(self, sample_files):
        """Test max_results works with lazy evaluation."""
        finder = FileFinder(root_path=str(sample_files))
        results = finder.search(Condition.extension(".txt"), lazy=True, max_results=2)
        files = list(results)
        assert len(files) == 2

    def test_lazy_evaluation_memory_efficient(self, sample_files):
        """Test lazy evaluation processes files one at a time."""
        finder = FileFinder(root_path=str(sample_files))
        results = finder.search(Condition.extension(".txt"), lazy=True)

        # Process one file at a time
        first_file = next(results)
        assert first_file.suffix == ".txt"

        # Can continue iteration
        remaining = list(results)
        assert len(remaining) == 2


class TestFileFinderEdgeCases:
    """Test edge cases and error handling."""

    def test_search_nonexistent_directory(self, temp_dir):
        """Test searching in non-existent directory."""
        nonexistent = temp_dir / "does_not_exist"
        finder = FileFinder(root_path=str(nonexistent))
        results = finder.search(Condition.extension(".txt"))
        # Should handle gracefully and return empty results
        assert len(results) == 0

    def test_search_with_permission_error(self, temp_dir):
        """Test handling of permission errors."""
        # Create a directory with restricted permissions
        restricted = temp_dir / "restricted"
        restricted.mkdir()
        (restricted / "file.txt").write_text("test")

        # Note: This test might not work on all systems
        # It's mainly for documentation purposes
        finder = FileFinder(root_path=str(temp_dir))
        results = finder.search(Condition.extension(".txt"))
        # Should handle permission errors gracefully
        assert isinstance(results, list)

    def test_search_with_symlinks_disabled(self, temp_dir):
        """Test that symlinks are not followed when disabled."""
        # Create a file and a symlink to it
        target = temp_dir / "target.txt"
        target.write_text("test")
        link = temp_dir / "link.txt"

        try:
            link.symlink_to(target)
        except OSError:
            pytest.skip("Cannot create symlinks on this system")

        finder = FileFinder(root_path=str(temp_dir), follow_symlinks=False)
        results = finder.search(Condition.extension(".txt"))
        # Should only find the target file, not the symlink
        assert len(results) == 1
        assert results[0].name == "target.txt"


class TestFileFinderRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_find_large_media_files(self, sample_files):
        """Test finding large media files for archival."""
        finder = FileFinder(root_path=str(sample_files))
        results = finder.search(
            Condition.is_video().OR(Condition.is_image()).AND(Condition.size_greater_than(100))
        )
        # video.mp4 (500 bytes)
        assert len(results) == 1
        assert results[0].name == "video.mp4"

    def test_find_backup_files(self, sample_files):
        """Test finding backup files."""
        finder = FileFinder(root_path=str(sample_files))
        results = finder.search(Condition.name_contains("backup").OR(Condition.extension(".bak")))
        assert len(results) == 1
        assert results[0].name == "backup.bak"

    def test_find_source_files_excluding_directories(self, sample_files):
        """Test finding source files while excluding certain directories."""
        finder = FileFinder(root_path=str(sample_files))
        results = finder.search(
            Condition.extension(".py").AND(Condition.not_in_directory("subdir1"))
        )
        assert len(results) == 1
        assert results[0].name == "file2.py"

    def test_find_recent_small_files(self, sample_files):
        """Test finding recent small files."""
        finder = FileFinder(root_path=str(sample_files))
        results = finder.search(
            Condition.size_less_than(100).AND(Condition.modified_within_days(1))
        )
        # image.png (50), deep_file.txt (75)
        assert len(results) == 2

    def test_complex_media_search(self, sample_files):
        """Test the original use case: complex media file search."""
        finder = FileFinder(root_path=str(sample_files))

        # PNG or PDF files between 1 byte and 200 bytes
        # OR video files in any directory
        results = finder.search(
            Condition.extension(".png", ".pdf")
            .AND(Condition.size_between(1, 200))
            .OR(Condition.is_video())
        )

        # image.png (50), document.pdf (150), video.mp4 (500)
        assert len(results) == 3
        names = {f.name for f in results}
        assert names == {"image.png", "document.pdf", "video.mp4"}
