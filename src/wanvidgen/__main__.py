"""
WanVidGen package main entry point.

This module allows the wanvidgen package to be executed as a module
using `python -m wanvidgen`.
"""

from .main import main

if __name__ == "__main__":
    import sys
    sys.exit(main())