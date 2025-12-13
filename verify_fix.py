#!/usr/bin/env python3
"""Verification script for the logging module name collision fix.

This script verifies the acceptance criteria:
1. python -m wanvidgen runs without ModuleNotFoundError
2. Application starts and loads
3. Standard library logging works correctly
"""

import sys
import subprocess
from pathlib import Path

def test_no_module_not_found_error():
    """Test that python -m wanvidgen runs without ModuleNotFoundError."""
    print("Testing: python -m wanvidgen runs without ModuleNotFoundError...")
    
    result = subprocess.run(
        [sys.executable, "-m", "wanvidgen", "--help"],
        env={"PYTHONPATH": str(Path(__file__).parent / "src")},
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )
    
    if "ModuleNotFoundError" in result.stderr or "ModuleNotFoundError" in result.stdout:
        print("✗ FAILED: ModuleNotFoundError detected")
        print(result.stderr)
        return False
    
    if result.returncode == 0:
        print("✓ PASSED: No ModuleNotFoundError, application runs successfully")
        return True
    else:
        print(f"✗ FAILED: Application exited with code {result.returncode}")
        return False


def test_application_loads():
    """Test that application starts and loads."""
    print("\nTesting: Application starts and loads...")
    
    result = subprocess.run(
        [sys.executable, "-m", "wanvidgen", "--check-system"],
        env={"PYTHONPATH": str(Path(__file__).parent / "src")},
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )
    
    if "System Compatibility Check" in result.stdout:
        print("✓ PASSED: Application loads and runs check-system command")
        return True
    else:
        print("✗ FAILED: Application did not load properly")
        print(result.stdout)
        print(result.stderr)
        return False


def test_standard_logging_works():
    """Test that standard library logging import works."""
    print("\nTesting: Standard library logging works correctly...")
    
    test_code = """
import sys
sys.path.insert(0, 'src')
import logging
from wanvidgen.log_config import configure_logging, LogConfig
logger = logging.getLogger('test')
logger.info('Standard logging works')
print('SUCCESS')
"""
    
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )
    
    if "SUCCESS" in result.stdout and "ModuleNotFoundError" not in result.stderr:
        print("✓ PASSED: Both standard library logging and log_config work together")
        return True
    else:
        print("✗ FAILED: Logging import failed")
        print(result.stderr)
        return False


def main():
    print("=" * 70)
    print("VERIFICATION: Fix Logging Module Name Collision")
    print("=" * 70)
    print()
    
    tests = [
        test_no_module_not_found_error,
        test_application_loads,
        test_standard_logging_works,
    ]
    
    results = [test() for test in tests]
    
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✓ ALL ACCEPTANCE CRITERIA MET")
        print("✓ python -m wanvidgen runs without ModuleNotFoundError")
        print("✓ Application starts and loads")
        print("✓ Standard library logging works correctly")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
