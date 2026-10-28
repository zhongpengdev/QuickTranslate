#!/usr/bin/env python3
"""Launcher for QuickTranslate."""
import sys
import os

# Ensure package is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from quick_translate.app import main

if __name__ == "__main__":
    main()
