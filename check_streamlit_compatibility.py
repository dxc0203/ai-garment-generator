#!/usr/bin/env python3
"""
Streamlit Compatibility Checker for AI Garment Generator
Checks for deprecated features and potential compatibility issues.
"""
import subprocess
import sys
import re
import os
from pathlib import Path

def run_command(cmd, capture_output=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result
    except Exception as e:
        print(f"[ERROR] Failed to run command: {e}")
        return None

def check_streamlit_version():
    """Check current Streamlit version and compatibility."""
    print("=== Streamlit Version Check ===")

    try:
        import streamlit as st
        version = st.__version__
        print(f"Current Streamlit version: {version}")

        # Parse version
        major, minor, patch = map(int, version.split('.')[:3])

        # Check compatibility ranges
        if major >= 2:
            print("⚠️  WARNING: Streamlit 2.x detected - major version change may have breaking changes")
            return False
        elif major == 1 and minor >= 28:
            print("✅ Compatible: Using Streamlit 1.28+ (recommended)")
            return True
        else:
            print(f"⚠️  WARNING: Using older Streamlit {version} - consider updating to 1.28+")
            return True

    except ImportError:
        print("❌ ERROR: Streamlit not found")
        return False

def scan_for_deprecated_features():
    """Scan Python files for potentially deprecated Streamlit features."""
    print("\n=== Deprecated Features Scan ===")

    deprecated_patterns = {
        r'st\.cache\(': 'st.cache is deprecated, use @st.cache_data or @st.cache_resource',
        r'st\.experimental_memo\(': 'st.experimental_memo is deprecated',
        r'st\.experimental_singleton\(': 'st.experimental_singleton is deprecated',
        r'st\.beta_': 'st.beta_ functions are deprecated',
        r'st\.echo\(': 'st.echo is deprecated',
        r'st\.empty\(': 'st.empty is deprecated',
        r'st\.progress\(': 'st.progress may have changed behavior',
    }

    project_root = Path(__file__).parent
    # Only scan project files, exclude virtual environment and common library directories
    python_files = []
    for file_path in project_root.rglob("*.py"):
        # Skip virtual environment files
        if ".venv" in str(file_path) or "venv" in str(file_path):
            continue
        # Skip common library directories that might be in the project
        if any(skip_dir in str(file_path) for skip_dir in ["__pycache__", ".git", "node_modules"]):
            continue
        python_files.append(file_path)

    found_deprecated = []

    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            for pattern, warning in deprecated_patterns.items():
                if re.search(pattern, content):
                    found_deprecated.append(f"{file_path.relative_to(project_root)}: {warning}")

        except Exception as e:
            print(f"[WARNING] Could not scan {file_path}: {e}")

    if found_deprecated:
        print("⚠️  Found potentially deprecated features:")
        for item in found_deprecated:
            print(f"  - {item}")
        return False
    else:
        print("✅ No deprecated features found")
        return True

def check_streamlit_api_changes():
    """Check for API changes that might affect the app."""
    print("\n=== API Compatibility Check ===")

    # Test key Streamlit APIs used in the app
    test_code = '''
import streamlit as st
import sys

# Test basic APIs
try:
    # Page config
    st.set_page_config(page_title="Test", layout="wide")

    # Basic UI elements
    st.title("Test")
    st.markdown("Test")
    st.button("Test")

    # Layout
    col1, col2 = st.columns(2)
    with col1:
        st.write("Test")

    # State management
    if "test" not in st.session_state:
        st.session_state.test = True

    # Navigation (if available)
    if hasattr(st, "switch_page"):
        print("switch_page available")
    else:
        print("switch_page not available - may need alternative")

    print("All basic APIs working")

except Exception as e:
    print(f"API Error: {e}")
    sys.exit(1)
'''

    try:
        result = run_command(f'python -c "{test_code}"')
        if result and result.returncode == 0:
            print("✅ Basic Streamlit APIs are compatible")
            return True
        else:
            print("❌ API compatibility issues detected")
            if result and result.stderr:
                print(f"Error details: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to test APIs: {e}")
        return False

def suggest_version_constraints():
    """Suggest version constraints for requirements.txt."""
    print("\n=== Version Constraint Recommendations ===")

    recommendations = """
# Recommended version constraints for requirements.txt:

# Allow patch updates but prevent major version changes
streamlit>=1.28.0,<2.0.0

# For other packages, consider similar constraints:
# requests>=2.31.0,<3.0.0
# pandas>=2.2.1,<3.0.0

# Benefits:
# ✅ Gets bug fixes and security updates
# ✅ Prevents breaking changes from major versions
# ✅ Allows controlled updates via your update helper
"""

    print(recommendations)

def main():
    """Main compatibility check function."""
    print("=== AI Garment Generator - Streamlit Compatibility Checker ===")
    print("Checking compatibility with current Streamlit installation\n")

    checks = [
        ("Version Check", check_streamlit_version),
        ("Deprecated Features", scan_for_deprecated_features),
        ("API Compatibility", check_streamlit_api_changes),
    ]

    passed = 0
    total = len(checks)

    for name, check_func in checks:
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"[ERROR] {name} failed: {e}")

    print("\n=== Compatibility Summary ===")
    print(f"Passed: {passed}/{total} checks")

    if passed == total:
        print("🎉 All compatibility checks passed!")
        print("Your app should work with the current Streamlit version.")
    else:
        print("⚠️  Some compatibility issues detected.")
        print("Review the warnings above and consider updating your code.")

    suggest_version_constraints()

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)