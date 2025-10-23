#!/usr/bin/env python3
"""
Script to investigate pip update failures and corrupted packages.
"""
import subprocess
import sys
import os
import json

def run_command(cmd, description=""):
    """Run a command and return the result."""
    try:
        print(f"\n=== {description} ===")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"Command: {cmd}")
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
        return result
    except Exception as e:
        print(f"Error running command: {e}")
        return None

def check_pip_list():
    """Check pip list output for corrupted packages."""
    print("\n=== Checking pip list for corrupted packages ===")
    result = run_command("pip list --format=json", "Getting package list")

    if result and result.returncode == 0:
        try:
            packages = json.loads(result.stdout)
            corrupted = []
            for pkg in packages:
                name = pkg.get('name', '')
                version = pkg.get('version', '')
                try:
                    from packaging.version import parse as parse_version
                    parse_version(version)
                except Exception as e:
                    corrupted.append((name, version, str(e)))
                    print(f"CORRUPTED: {name}={version} - Error: {e}")
            return corrupted
        except Exception as e:
            print(f"Error parsing pip list JSON: {e}")
    return []

def check_pip_debug():
    """Run pip debug to see environment info."""
    run_command("pip debug", "Pip debug information")

def check_pip_config():
    """Check pip configuration."""
    run_command("pip config list", "Pip configuration")

def check_venv_integrity():
    """Check virtual environment integrity."""
    print("\n=== Virtual Environment Check ===")
    venv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.venv')
    print(f"Virtual environment path: {venv_path}")
    print(f"Exists: {os.path.exists(venv_path)}")

    pyvenv_cfg = os.path.join(venv_path, 'pyvenv.cfg')
    if os.path.exists(pyvenv_cfg):
        print(f"pyvenv.cfg contents:")
        with open(pyvenv_cfg, 'r') as f:
            print(f.read())

def check_disk_space():
    """Check available disk space."""
    print("\n=== Disk Space Check ===")
    try:
        result = subprocess.run("dir /-C", shell=True, capture_output=True, text=True, cwd=os.path.dirname(__file__))
        if result.returncode == 0:
            # Parse the last line for free space
            lines = result.stdout.strip().split('\n')
            for line in reversed(lines):
                if 'bytes free' in line.lower():
                    print(f"Disk space info: {line}")
                    break
    except Exception as e:
        print(f"Error checking disk space: {e}")

def main():
    print("=== Pip Update Failure Investigation ===")

    # Check virtual environment
    check_venv_integrity()

    # Check disk space
    check_disk_space()

    # Check pip configuration
    check_pip_config()

    # Check pip debug info
    check_pip_debug()

    # Check for corrupted packages
    corrupted = check_pip_list()

    print("\n=== SUMMARY ===")
    print(f"Found {len(corrupted)} corrupted packages:")
    for name, version, error in corrupted:
        print(f"  - {name} {version}: {error}")

    if corrupted:
        print("\nRECOMMENDATIONS:")
        print("1. Remove corrupted packages manually:")
        for name, version, error in corrupted:
            print(f"   pip uninstall -y {name}")
        print("2. Or do a clean virtual environment reinstall:")
        print("   start_app.bat --clean")
        print("3. Check for disk space issues")
        print("4. Check for antivirus interference")

    # Try a simple pip upgrade test
    print("\n=== Testing simple pip upgrade ===")
    run_command("python -m pip install --upgrade pip", "Testing pip self-upgrade")

if __name__ == "__main__":
    main()