#!/usr/bin/env python3
"""
Update Helper Script for AI Garment Generator
Provides robust package management and update functionality.
"""
import subprocess
import sys
import json
import os
from pathlib import Path

def run_command(cmd, description="", capture_output=True, check=False):
    """Run a command and return the result."""
    try:
        print(f"[INFO] {description}")
        if capture_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        else:
            result = subprocess.run(cmd, shell=True, check=check)
        return result
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {cmd}")
        print(f"[ERROR] Return code: {e.returncode}")
        if e.stdout:
            print(f"[ERROR] STDOUT: {e.stdout}")
        if e.stderr:
            print(f"[ERROR] STDERR: {e.stderr}")
        return e
    except Exception as e:
        print(f"[ERROR] Unexpected error running command: {e}")
        return None

def check_corrupted_packages():
    """Check for corrupted packages that could cause pip failures."""
    print("\n=== Checking for Corrupted Packages ===")

    try:
        result = run_command("pip list --format=json", "Getting package list for corruption check")
        if not result or result.returncode != 0:
            print("[WARNING] Could not get package list. Skipping corruption check.")
            return []

        packages = json.loads(result.stdout)
        corrupted = []

        for pkg in packages:
            name = pkg.get('name', '')
            version = pkg.get('version', '')

            # Check for null versions or malformed version strings
            if version is None:
                corrupted.append(name)
                print(f"[CORRUPTED] {name}: version is null")
            elif not isinstance(version, str):
                corrupted.append(name)
                print(f"[CORRUPTED] {name}: version is not a string ({version})")
            elif '(' in version or ')' in version:
                # Check for malformed versions like '1.28.0(1)'
                corrupted.append(name)
                print(f"[CORRUPTED] {name}: malformed version string '{version}'")

        if corrupted:
            print(f"[FOUND] {len(corrupted)} corrupted packages: {', '.join(corrupted)}")
        else:
            print("[SUCCESS] No corrupted packages found")

        return corrupted

    except Exception as e:
        print(f"[ERROR] Failed to check for corrupted packages: {e}")
        return []

def fix_corrupted_packages(corrupted_packages):
    """Fix corrupted packages by removing and reinstalling them."""
    if not corrupted_packages:
        return True

    print(f"\n=== Fixing {len(corrupted_packages)} Corrupted Packages ===")

    # Remove corrupted packages
    for pkg in corrupted_packages:
        print(f"[INFO] Removing corrupted package: {pkg}")
        run_command(f"pip uninstall -y {pkg}", f"Uninstalling {pkg}")

    # Clear pip cache to prevent issues
    print("[INFO] Clearing pip cache...")
    run_command("pip cache purge", "Clearing pip cache")

    # Reinstall requirements
    print("[INFO] Reinstalling requirements from requirements.txt...")
    if os.path.exists("requirements.txt"):
        result = run_command("pip install -r requirements.txt", "Reinstalling requirements")
        if result and result.returncode == 0:
            print("[SUCCESS] Requirements reinstalled successfully")
            return True
        else:
            print("[ERROR] Failed to reinstall requirements")
            return False
    else:
        print("[WARNING] requirements.txt not found. Installing individually...")
        # Try to install common packages that might have been corrupted
        common_packages = ["streamlit", "protobuf", "openai", "pandas", "pillow"]
        for pkg in corrupted_packages:
            if pkg.lower() in [p.lower() for p in common_packages]:
                run_command(f"pip install --upgrade {pkg}", f"Reinstalling {pkg}")
        return True

def upgrade_pip():
    """Upgrade pip with multiple fallback methods."""
    print("\n=== Upgrading Pip ===")

    methods = [
        ("python -m pip install --upgrade pip", "Standard pip upgrade"),
        ("python -c \"import subprocess, sys; subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', '--force-reinstall', 'pip'], check=True)\"", "Force reinstall pip"),
        ("python -c \"import urllib.request, subprocess, sys; url='https://bootstrap.pypa.io/get-pip.py'; exec(urllib.request.urlopen(url).read().decode()); subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)\"", "Bootstrap pip reinstall")
    ]

    for cmd, description in methods:
        print(f"[INFO] Trying: {description}")
        result = run_command(cmd, description)
        if result and result.returncode == 0:
            print("[SUCCESS] Pip upgraded successfully")
            return True
        else:
            print(f"[WARNING] {description} failed, trying next method...")

    print("[ERROR] All pip upgrade methods failed")
    return False

def upgrade_build_tools():
    """Upgrade setuptools and wheel."""
    print("\n=== Upgrading Build Tools ===")

    result = run_command("pip install --upgrade setuptools wheel", "Upgrading setuptools and wheel")
    if result and result.returncode == 0:
        print("[SUCCESS] Build tools upgraded successfully")
        return True
    else:
        print("[WARNING] Failed to upgrade build tools (usually not critical)")
        return False

def clear_cache():
    """Clear pip cache to prevent stale data issues."""
    print("\n=== Clearing Pip Cache ===")

    result = run_command("pip cache purge", "Clearing pip cache")
    if result and result.returncode == 0:
        print("[SUCCESS] Pip cache cleared")
        return True
    else:
        print("[WARNING] Failed to clear pip cache")
        return False

def update_all_packages():
    """Update all installed packages to their latest versions."""
    print("\n=== Updating All Packages ===")

    # Get outdated packages
    result = run_command("pip list --outdated --format=json", "Checking for outdated packages")
    if not result or result.returncode != 0:
        print("[WARNING] Could not check for outdated packages")
        return False

    try:
        outdated = json.loads(result.stdout)
        if not outdated:
            print("[SUCCESS] All packages are up to date")
            return True

        print(f"[INFO] Found {len(outdated)} outdated packages")

        # Update packages
        package_names = [pkg['name'] for pkg in outdated]
        cmd = f"pip install --upgrade {' '.join(package_names)}"
        result = run_command(cmd, f"Updating {len(package_names)} packages")

        if result and result.returncode == 0:
            print("[SUCCESS] All packages updated successfully")
            return True
        else:
            print("[ERROR] Failed to update some packages")
            return False

    except Exception as e:
        print(f"[ERROR] Failed to update packages: {e}")
        return False

def main():
    """Main update helper function."""
    print("=== AI Garment Generator - Update Helper ===")
    print("Ensuring successful package management and updates\n")

    success_count = 0
    total_steps = 5

    # Step 1: Check for corrupted packages
    corrupted = check_corrupted_packages()
    if corrupted:
        if fix_corrupted_packages(corrupted):
            success_count += 1
    else:
        success_count += 1

    # Step 2: Upgrade pip
    if upgrade_pip():
        success_count += 1

    # Step 3: Upgrade build tools
    if upgrade_build_tools():
        success_count += 1

    # Step 4: Clear cache
    if clear_cache():
        success_count += 1

    # Step 5: Check if user wants to update all packages
    if len(sys.argv) > 1 and sys.argv[1] == "--update-all":
        print("\n[INFO] --update-all flag detected, updating all packages...")
        if update_all_packages():
            success_count += 1
        total_steps += 1
    else:
        success_count += 1  # Count as success since it's optional

    print("\n=== Update Summary ===")
    print(f"Completed: {success_count}/{total_steps} steps successful")

    if success_count == total_steps:
        print("🎉 All update operations completed successfully!")
        return 0
    elif success_count >= total_steps - 1:
        print("✅ Update operations mostly successful. Minor issues may exist.")
        return 0
    else:
        print("❌ Multiple update operations failed. You may need manual intervention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())