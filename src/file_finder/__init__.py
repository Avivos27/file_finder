"""
FileFinder - A flexible file search library with complex condition support.

This library provides a fluent API for searching files based on various conditions
such as extension, size, location, name patterns, and modification time.
"""

from file_finder.config import config, get_logger
from file_finder.core import Condition, ConditionOperator, FileFinder

__version__ = "0.1.0"
__all__ = ["Condition", "ConditionOperator", "FileFinder", "config", "get_logger"]
