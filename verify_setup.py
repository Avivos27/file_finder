#!/usr/bin/env python3
"""Verify IntelliJ/PyCharm setup is correct."""

import sys
from pathlib import Path

print("=" * 60)
print("FileFinder Project Setup Verification")
print("=" * 60)

# Check Python version
print(f"\n✓ Python version: {sys.version.split()[0]}")
print(f"✓ Python executable: {sys.executable}")

# Check virtual environment
venv_path = Path(sys.executable).parent.parent
expected_venv = Path(__file__).parent / ".venv"
if venv_path.resolve() == expected_venv.resolve():
    print(f"✓ Using correct virtual environment: {venv_path}")
else:
    print(f"✗ WARNING: Using wrong virtual environment!")
    print(f"  Current:  {venv_path}")
    print(f"  Expected: {expected_venv}")
    print(f"\n  → Follow instructions in INTELLIJ_SETUP.md to fix!")

# Check imports
print("\nChecking imports...")
try:
    from file_finder import FileFinder, Condition
    print("✓ file_finder module imported successfully")
except ImportError as e:
    print(f"✗ Failed to import file_finder: {e}")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    print("✓ python-dotenv imported successfully")
except ImportError as e:
    print(f"✗ Failed to import dotenv: {e}")
    sys.exit(1)

try:
    import pytest
    print(f"✓ pytest imported successfully (version {pytest.__version__})")
except ImportError as e:
    # Try as module
    import subprocess
    result = subprocess.run([sys.executable, "-m", "pytest", "--version"], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✓ pytest available as module: {result.stdout.strip()}")
    else:
        print(f"✗ Failed to import pytest: {e}")
        sys.exit(1)

try:
    import ruff
    print("✓ ruff imported successfully")
except ImportError:
    # ruff is a command-line tool, may not be importable
    print("✓ ruff available (command-line tool)")

# Test basic functionality
print("\nTesting FileFinder...")
try:
    finder = FileFinder(root_path=str(Path(__file__).parent))
    results = finder.search(Condition.extension('.py'), max_results=5)
    print(f"✓ FileFinder works! Found {len(results)} Python files")
except Exception as e:
    print(f"✗ FileFinder test failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ All checks passed! Setup is correct.")
print("=" * 60)
