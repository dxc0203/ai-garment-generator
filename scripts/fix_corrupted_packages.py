#!/usr/bin/env python3
"""
Script to detect and remove corrupted packages with invalid version strings.
"""
import subprocess
import sys
import json

def main():
    try:
        # Use pip list to get installed packages
        result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=json'],
                              capture_output=True, text=True, check=True)
        packages = json.loads(result.stdout)

        corrupted = []
        for pkg in packages:
            name = pkg.get('name', '')
            version = pkg.get('version', '')
            # Check if version string is valid
            try:
                from packaging.version import parse as parse_version
                parse_version(version)
            except Exception:
                corrupted.append(name)

        if corrupted:
            print(f'Found corrupted packages: {corrupted}')
            for pkg in corrupted:
                print(f'Removing corrupted package: {pkg}')
                try:
                    subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y', pkg],
                                 capture_output=True, check=True)
                    print(f'Successfully removed {pkg}')
                except Exception as e:
                    print(f'Failed to remove {pkg}: {e}')
        else:
            print('No corrupted packages found.')

    except Exception as e:
        print(f'Error checking for corrupted packages: {e}')
        print('Continuing with pip upgrade...')

if __name__ == "__main__":
    main()