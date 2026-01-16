"""
FileFinder - A flexible file search library with complex condition support.

This library provides a fluent API for searching files based on various conditions
such as extension, size, location, name patterns, and modification time.
"""

import os
import re
from collections.abc import Callable, Generator
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

from file_finder.config import get_logger

logger = get_logger(__name__)


class ConditionOperator(Enum):
    """Operators for combining conditions."""

    AND = "AND"
    OR = "OR"


class Condition:
    """
    Represents a search condition that can be chained with AND/OR operators.

    Example:
        Condition.extension('.png').AND(Condition.size_greater_than(1000))
    """

    def __init__(
        self,
        predicate: Callable[[Path, os.DirEntry | None], bool],
        description: str = "",
    ):
        """
        Initialize a condition.

        Args:
            predicate: Function that takes a Path and DirEntry and returns True if condition is met
            description: Human-readable description of the condition
        """
        self.predicate = predicate
        self.description = description
        self.operator = None
        self.next_condition = None
        logger.debug(f"Created condition: {description}")

    def AND(self, other: "Condition") -> "Condition":
        """Combine this condition with another using AND logic."""
        self.operator = ConditionOperator.AND
        self.next_condition = other
        logger.debug(f"Combined conditions with AND: {self.description} AND {other.description}")
        return self

    def OR(self, other: "Condition") -> "Condition":
        """Combine this condition with another using OR logic."""
        self.operator = ConditionOperator.OR
        self.next_condition = other
        logger.debug(f"Combined conditions with OR: {self.description} OR {other.description}")
        return self

    def evaluate(self, path: Path, entry: os.DirEntry | None = None) -> bool:
        """
        Evaluate this condition and any chained conditions.

        Args:
            path: Path object to evaluate
            entry: Optional DirEntry for performance (avoids extra stat calls)

        Returns:
            True if all conditions are met, False otherwise
        """
        # Evaluate current condition
        current_result = self.predicate(path, entry)

        # If no chained conditions, return current result
        if self.next_condition is None:
            return current_result

        # Apply operator logic
        if self.operator == ConditionOperator.AND:
            return current_result and self.next_condition.evaluate(path, entry)
        if self.operator == ConditionOperator.OR:
            return current_result or self.next_condition.evaluate(path, entry)

        return current_result

    # ===== Extension Conditions =====

    @staticmethod
    def extension(*extensions: str) -> "Condition":
        """
        Match files with specific extensions.

        Args:
            *extensions: One or more extensions (e.g., '.png', '.pdf')

        Example:
            Condition.extension('.png', '.jpg', '.gif')
        """
        # Normalize extensions to lowercase and ensure they start with a dot
        normalized = set()
        for ext in extensions:
            ext = ext.lower()
            if not ext.startswith("."):
                ext = "." + ext
            normalized.add(ext)

        def predicate(path: Path, entry: os.DirEntry | None) -> bool:
            return path.suffix.lower() in normalized

        return Condition(predicate, f"extension in {extensions}")

    # ===== Size Conditions =====

    @staticmethod
    def size_greater_than(size_bytes: int) -> "Condition":
        """
        Match files larger than specified size.

        Args:
            size_bytes: Minimum file size in bytes

        Example:
            Condition.size_greater_than(5 * 1024 * 1024)  # > 5MB
        """

        def predicate(path: Path, entry: os.DirEntry | None) -> bool:
            try:
                if entry and hasattr(entry, "stat"):
                    return entry.stat(follow_symlinks=False).st_size > size_bytes
                return path.stat().st_size > size_bytes
            except (OSError, PermissionError):
                return False

        return Condition(predicate, f"size > {size_bytes} bytes")

    @staticmethod
    def size_less_than(size_bytes: int) -> "Condition":
        """
        Match files smaller than specified size.

        Args:
            size_bytes: Maximum file size in bytes

        Example:
            Condition.size_less_than(1024)  # < 1KB
        """

        def predicate(path: Path, entry: os.DirEntry | None) -> bool:
            try:
                if entry and hasattr(entry, "stat"):
                    return entry.stat(follow_symlinks=False).st_size < size_bytes
                return path.stat().st_size < size_bytes
            except (OSError, PermissionError):
                return False

        return Condition(predicate, f"size < {size_bytes} bytes")

    @staticmethod
    def size_between(min_bytes: int, max_bytes: int) -> "Condition":
        """
        Match files with size in specified range (inclusive).

        Args:
            min_bytes: Minimum file size in bytes
            max_bytes: Maximum file size in bytes

        Example:
            Condition.size_between(1024, 5 * 1024 * 1024)  # 1KB to 5MB
        """

        def predicate(path: Path, entry: os.DirEntry | None) -> bool:
            try:
                if entry and hasattr(entry, "stat"):
                    size = entry.stat(follow_symlinks=False).st_size
                else:
                    size = path.stat().st_size
                return min_bytes <= size <= max_bytes
            except (OSError, PermissionError):
                return False

        return Condition(predicate, f"size between {min_bytes} and {max_bytes} bytes")

    # ===== Location Conditions =====

    @staticmethod
    def in_directory(*directories: str) -> "Condition":
        """
        Match files within specified directories (searches recursively within them).

        Args:
            *directories: One or more directory paths or directory names

        Example:
            Condition.in_directory('/path/to/folder', 'images')
        """
        # Convert to Path objects and resolve
        dir_paths = set()
        dir_names = set()

        for d in directories:
            d_path = Path(d)
            if d_path.is_absolute():
                dir_paths.add(d_path.resolve())
            else:
                # Treat as directory name to match anywhere in path
                dir_names.add(d)

        def predicate(path: Path, entry: os.DirEntry | None) -> bool:
            # Resolve path to handle symlinks and normalize
            resolved_path = path.resolve()

            # Check if file is within any specified absolute path
            for dir_path in dir_paths:
                try:
                    resolved_path.relative_to(dir_path)
                    return True
                except ValueError:
                    continue

            # Check if any parent directory name matches
            return any(parent.name in dir_names for parent in resolved_path.parents)

        return Condition(predicate, f"in directory {directories}")

    @staticmethod
    def not_in_directory(*directories: str) -> "Condition":
        """
        Match files NOT in specified directories.

        Args:
            *directories: One or more directory paths or names to exclude

        Example:
            Condition.not_in_directory('node_modules', '.git', '__pycache__')
        """
        # Reuse in_directory logic and invert
        in_dir_condition = Condition.in_directory(*directories)

        def predicate(path: Path, entry: os.DirEntry | None) -> bool:
            return not in_dir_condition.predicate(path, entry)

        return Condition(predicate, f"not in directory {directories}")

    @staticmethod
    def path_matches(pattern: str) -> "Condition":
        r"""
        Match files where the full path matches a regex pattern.

        Args:
            pattern: Regular expression pattern

        Example:
            Condition.path_matches(r'/images/\d{4}/.*\.png')
        """
        compiled_pattern = re.compile(pattern)

        def predicate(path: Path, entry: os.DirEntry | None) -> bool:
            return compiled_pattern.search(str(path)) is not None

        return Condition(predicate, f"path matches '{pattern}'")

    # ===== Name Conditions =====

    @staticmethod
    def name_contains(substring: str, case_sensitive: bool = False) -> "Condition":
        """
        Match files whose name contains a substring.

        Args:
            substring: Substring to search for
            case_sensitive: Whether to perform case-sensitive matching

        Example:
            Condition.name_contains('backup')
        """
        if not case_sensitive:
            substring = substring.lower()

        def predicate(path: Path, entry: os.DirEntry | None) -> bool:
            name = path.name if case_sensitive else path.name.lower()
            return substring in name

        return Condition(predicate, f"name contains '{substring}'")

    @staticmethod
    def name_matches(pattern: str) -> "Condition":
        r"""
        Match files whose name matches a regex pattern.

        Args:
            pattern: Regular expression pattern

        Example:
            Condition.name_matches(r'^test_.*\.py$')
        """
        compiled_pattern = re.compile(pattern)

        def predicate(path: Path, entry: os.DirEntry | None) -> bool:
            return compiled_pattern.search(path.name) is not None

        return Condition(predicate, f"name matches '{pattern}'")

    @staticmethod
    def name_equals(name: str, case_sensitive: bool = False) -> "Condition":
        """
        Match files with exact name.

        Args:
            name: Exact filename to match
            case_sensitive: Whether to perform case-sensitive matching

        Example:
            Condition.name_equals('README.md')
        """
        if not case_sensitive:
            name = name.lower()

        def predicate(path: Path, entry: os.DirEntry | None) -> bool:
            file_name = path.name if case_sensitive else path.name.lower()
            return file_name == name

        return Condition(predicate, f"name equals '{name}'")

    # ===== Time Conditions =====

    @staticmethod
    def modified_within_days(days: int) -> "Condition":
        """
        Match files modified within the last N days.

        Args:
            days: Number of days

        Example:
            Condition.modified_within_days(7)  # Modified in last week
        """
        cutoff_time = datetime.now() - timedelta(days=days)

        def predicate(path: Path, entry: os.DirEntry | None) -> bool:
            try:
                if entry and hasattr(entry, "stat"):
                    mtime = entry.stat(follow_symlinks=False).st_mtime
                else:
                    mtime = path.stat().st_mtime
                mod_time = datetime.fromtimestamp(mtime)
                return mod_time >= cutoff_time
            except (OSError, PermissionError):
                return False

        return Condition(predicate, f"modified within {days} days")

    @staticmethod
    def created_within_days(days: int) -> "Condition":
        """
        Match files created within the last N days.

        Args:
            days: Number of days

        Example:
            Condition.created_within_days(30)  # Created in last month
        """
        cutoff_time = datetime.now() - timedelta(days=days)

        def predicate(path: Path, entry: os.DirEntry | None) -> bool:
            try:
                if entry and hasattr(entry, "stat"):
                    ctime = entry.stat(follow_symlinks=False).st_ctime
                else:
                    ctime = path.stat().st_ctime
                create_time = datetime.fromtimestamp(ctime)
                return create_time >= cutoff_time
            except (OSError, PermissionError):
                return False

        return Condition(predicate, f"created within {days} days")

    # ===== File Type Detection =====

    @staticmethod
    def is_image() -> "Condition":
        """Match common image file types."""
        return Condition.extension(
            ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".ico"
        )

    @staticmethod
    def is_video() -> "Condition":
        """Match common video file types."""
        return Condition.extension(
            ".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm", ".m4v", ".mpg", ".mpeg"
        )

    @staticmethod
    def is_audio() -> "Condition":
        """Match common audio file types."""
        return Condition.extension(".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus")

    @staticmethod
    def is_document() -> "Condition":
        """Match common document file types."""
        return Condition.extension(
            ".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf", ".md", ".markdown"
        )

    @staticmethod
    def is_archive() -> "Condition":
        """Match common archive file types."""
        return Condition.extension(".zip", ".tar", ".gz", ".bz2", ".7z", ".rar", ".xz", ".tgz")


class FileFinder:
    """
    Main class for searching files based on complex conditions.

    Example:
        finder = FileFinder(root_path='/path/to/search')
        results = finder.search(
            Condition.extension('.png').AND(Condition.size_greater_than(1024))
        )
    """

    def __init__(
        self,
        root_path: str | None = None,
        follow_symlinks: bool = False,
        max_depth: int | None = None,
    ):
        """
        Initialize FileFinder.

        Args:
            root_path: Root directory to search from (default: current directory)
            follow_symlinks: Whether to follow symbolic links
            max_depth: Maximum directory depth to search (None = unlimited)
        """
        self.root_path = Path(root_path) if root_path else Path.cwd()
        self.follow_symlinks = follow_symlinks
        self.max_depth = max_depth

        logger.info(
            f"Initialized FileFinder: root={self.root_path}, "
            f"follow_symlinks={follow_symlinks}, max_depth={max_depth}"
        )

    def search(
        self,
        condition: Condition,
        recursive: bool = True,
        lazy: bool = False,
        max_results: int | None = None,
    ) -> list[Path] | Generator[Path]:
        """
        Search for files matching the given condition.

        Args:
            condition: Condition object defining the search criteria
            recursive: Whether to search subdirectories
            lazy: If True, returns a generator; if False, returns a list
            max_results: Maximum number of results to return (None = unlimited)

        Returns:
            List of Path objects or generator yielding Path objects

        Example:
            results = finder.search(
                Condition.extension('.png').AND(Condition.size_greater_than(1024)),
                lazy=True,
                max_results=100
            )
        """
        logger.info(
            f"Starting search: recursive={recursive}, lazy={lazy}, max_results={max_results}"
        )

        if lazy:
            return self._search_generator(condition, recursive, max_results)
        results = list(self._search_generator(condition, recursive, max_results))
        logger.info(f"Search completed: found {len(results)} files")
        return results

    def _search_generator(
        self,
        condition: Condition,
        recursive: bool,
        max_results: int | None,
    ) -> Generator[Path]:
        """Internal generator for file searching."""
        count = 0

        for file_path in self._walk_directory(self.root_path, recursive, current_depth=0):
            # Check if we've reached max results
            if max_results is not None and count >= max_results:
                logger.debug(f"Reached max_results limit: {max_results}")
                break

            # Evaluate condition
            if condition.evaluate(file_path):
                logger.debug(f"Match found: {file_path}")
                yield file_path
                count += 1

    def _walk_directory(
        self,
        directory: Path,
        recursive: bool,
        current_depth: int,
    ) -> Generator[Path]:
        """
        Walk directory tree efficiently using os.scandir.

        Args:
            directory: Directory to walk
            recursive: Whether to recurse into subdirectories
            current_depth: Current recursion depth

        Yields:
            Path objects for each file found
        """
        # Check depth limit
        if self.max_depth is not None and current_depth > self.max_depth:
            logger.debug(f"Reached max_depth at: {directory}")
            return

        logger.debug(f"Scanning directory: {directory} (depth={current_depth})")

        try:
            with os.scandir(directory) as entries:
                # Separate files and directories for efficient processing
                files = []
                dirs = []

                for entry in entries:
                    try:
                        # Skip symlinks if not following them
                        if entry.is_symlink() and not self.follow_symlinks:
                            continue

                        if entry.is_file(follow_symlinks=self.follow_symlinks):
                            files.append(entry)
                        elif entry.is_dir(follow_symlinks=self.follow_symlinks) and recursive:
                            dirs.append(entry)
                    except (OSError, PermissionError):
                        # Skip files/directories we can't access
                        continue

                # Yield all files in current directory
                for entry in files:
                    yield Path(entry.path)

                # Recurse into subdirectories
                for entry in dirs:
                    yield from self._walk_directory(
                        Path(entry.path), recursive=True, current_depth=current_depth + 1
                    )

        except (OSError, PermissionError) as e:
            # Skip directories we can't access
            logger.warning(f"Cannot access directory {directory}: {e}")
