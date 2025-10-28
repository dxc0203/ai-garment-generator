#!/usr/bin/env python3
"""
Comprehensive Pre-Launch Health Check for AI Garment Generator
Performs all checks and automatic recovery
"""

import sys
import subprocess
import json
import importlib
import os

def check_pip_list():
    """Check if pip list command works"""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=json'],
                              capture_output=True, text=True, check=True, timeout=30)
        packages = json.loads(result.stdout)
        return True, len(packages)
    except Exception as e:
        return False, 0

def check_package_integrity():
    """Check if critical packages can be imported"""
    critical_packages = {
        'streamlit': ['__version__'],
        'google.protobuf': ['__version__'],
        'openai': ['__version__'],
        'pandas': ['__version__'],
        'PIL': ['__version__']
    }

    issues = []
    for package_name, attributes in critical_packages.items():
        try:
            module = importlib.import_module(package_name)
            for attr in attributes:
                if not hasattr(module, attr):
                    issues.append(f"{package_name} missing attribute: {attr}")
        except ImportError as e:
            issues.append(f"{package_name} import failed: {e}")
        except Exception as e:
            issues.append(f"{package_name} error: {e}")

    return len(issues) == 0, issues

def validate_package_versions():
    """Validate critical package versions"""
    critical_packages = {
        'streamlit': {'min_version': '1.28.0', 'max_version': '2.0.0'},
        'protobuf': {'min_version': '3.0.0', 'max_version': '7.0.0'},
        'openai': {'min_version': '1.0.0', 'max_version': '2.0.0'}
    }

    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=json'],
                              capture_output=True, text=True, check=True, timeout=30)
        packages = json.loads(result.stdout)
        installed = {pkg['name'].lower(): pkg['version'] for pkg in packages}

        issues = []
        for pkg_name, version_req in critical_packages.items():
            if pkg_name in installed:
                version = installed[pkg_name]
                try:
                    from packaging.version import parse as parse_version
                    ver = parse_version(version)
                    min_ver = parse_version(version_req['min_version'])
                    max_ver = parse_version(version_req['max_version'])
                    if not (min_ver <= ver < max_ver):
                        issues.append(f'{pkg_name} {version} not in range {version_req["min_version"]}-{version_req["max_version"]}')
                except ImportError:
                    issues.append(f'{pkg_name} {version} - cannot validate version range (packaging module missing)')
                except Exception as e:
                    issues.append(f'{pkg_name} has invalid version: {version} ({e})')
            else:
                issues.append(f'{pkg_name} not installed')

        return len(issues) == 0, issues
    except Exception as e:
        return False, [f'Version validation failed: {e}']

def force_reinstall_packages():
    """Force reinstall critical packages"""
    critical_packages = [
        'streamlit',
        'protobuf',
        'openai',
        'pandas',
        'pillow'
    ]

    print("Force reinstalling critical packages...")

    # First uninstall
    print("Uninstalling packages...")
    for package in critical_packages:
        try:
            print(f"Uninstalling {package}...")
            uninstall_cmd = [sys.executable, '-m', 'pip', 'uninstall', '-y', package]
            result = subprocess.run(uninstall_cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print(f"Warning: Uninstall of {package} had issues")
        except subprocess.TimeoutExpired:
            print(f"Warning: Uninstall of {package} timed out")
        except Exception as e:
            print(f"Warning: Uninstall of {package} failed: {e}")

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
    except Exception as e:
        print(f"ERROR: Reinstall failed: {e}")
        return False

def run_health_checks():
    """Run all health checks and perform automatic recovery"""
    print("Running comprehensive pre-launch health checks...")

    # Check 1: Pip functionality
    print("\n[1/3] Checking pip functionality...")
    pip_ok, package_count = check_pip_list()
    if not pip_ok:
        print("ERROR: Pip is not working properly")
        return False
    print(f"SUCCESS: Pip working, {package_count} packages found")

    # Check 2: Package integrity
    print("\n[2/3] Checking package integrity...")
    integrity_ok, integrity_issues = check_package_integrity()
    if not integrity_ok:
        print("ERROR: Package integrity issues found:")
        for issue in integrity_issues:
            print(f"  - {issue}")
        print("\nAttempting automatic recovery...")
        if not force_reinstall_packages():
            print("ERROR: Automatic recovery failed")
            return False
        # Re-check after recovery
        print("\nRe-checking package integrity after recovery...")
        integrity_ok, integrity_issues = check_package_integrity()
        if not integrity_ok:
            print("ERROR: Package integrity still failing after recovery")
            return False
        print("SUCCESS: Package integrity restored")
    else:
        print("SUCCESS: All packages intact")

    # Check 3: Version validation
    print("\n[3/3] Validating package versions...")
    version_ok, version_issues = validate_package_versions()
    if not version_ok:
        print("ERROR: Version validation issues found:")
        for issue in version_issues:
            print(f"  - {issue}")
        print("\nAttempting automatic recovery...")
        if not force_reinstall_packages():
            print("ERROR: Automatic recovery failed")
            return False
        # Re-check after recovery
        print("\nRe-validating versions after recovery...")
        version_ok, version_issues = validate_package_versions()
        if not version_ok:
            print("ERROR: Version validation still failing after recovery")
            return False
        print("SUCCESS: Package versions validated")
    else:
        print("SUCCESS: All package versions valid")

    print("\n[SUCCESS] All pre-launch health checks passed!")
    return True

if __name__ == "__main__":
    if run_health_checks():
        print("\n[SUCCESS] System ready for launch")
        sys.exit(0)
    else:
        print("\n[ERROR] Health checks failed - manual intervention required")
        sys.exit(1)