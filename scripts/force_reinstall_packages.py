#!/usr/bin/env python3
"""
Force Reinstall Critical Packages for AI Garment Generator
Uninstalls and reinstalls critical packages to resolve any issues
"""

import sys
import subprocess
import os

def force_reinstall_packages():
    """Force reinstall critical packages"""
    critical_packages = [
        'streamlit',
        'protobuf',
        'openai',
        'pandas',
        'pillow'  # PIL is from pillow
    ]

    print("Force reinstalling critical packages...")

    # First uninstall
    print("Uninstalling packages...")
    uninstall_cmd = [sys.executable, '-m', 'pip', 'uninstall', '-y'] + critical_packages
    try:
        result = subprocess.run(uninstall_cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"Warning: Uninstall had issues: {result.stderr}")
        else:
            print("Packages uninstalled successfully")
    except subprocess.TimeoutExpired:
        print("ERROR: Uninstall timed out")
        return False
    except Exception as e:
        print(f"ERROR: Uninstall failed: {e}")
        return False

    # Then reinstall
    print("Reinstalling packages...")
    reinstall_cmd = [sys.executable, '-m', 'pip', 'install'] + critical_packages
    try:
        result = subprocess.run(reinstall_cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            print(f"ERROR: Reinstall failed: {result.stderr}")
            return False
        else:
            print("Packages reinstalled successfully")
            return True
    except subprocess.TimeoutExpired:
        print("ERROR: Reinstall timed out")
        return False
    except Exception as e:
        print(f"ERROR: Reinstall failed: {e}")
        return False

if __name__ == "__main__":
    if force_reinstall_packages():
        print("Force reinstall completed successfully")
        sys.exit(0)
    else:
        print("Force reinstall failed")
        sys.exit(1)