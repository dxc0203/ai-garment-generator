# File: pages/7_Startup_Logs.py

import streamlit as st
import os
import sys
import subprocess
import json
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Page Config ---
st.set_page_config(page_title="Startup Logs & Diagnostics", layout="wide")
st.title("🔧 Startup Logs & Diagnostics")
st.markdown("Monitor application startup issues and apply automatic fixes.")

# --- Initialize State ---
# Note: Logs are now read from log files instead of session state

# --- Functions ---
def get_latest_log_file():
    """Get the most recent startup log file."""
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if not os.path.exists(logs_dir):
        return None

    log_files = [f for f in os.listdir(logs_dir) if f.startswith('startup_') and f.endswith('.log')]
    if not log_files:
        return None

    # Sort by modification time, get the latest
    log_files.sort(key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)), reverse=True)
    return os.path.join(logs_dir, log_files[0])

def parse_log_file(log_path):
    """Parse a log file and return structured log entries."""
    if not log_path or not os.path.exists(log_path):
        return []

    logs = []
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Parse log lines: [LEVEL] date time - message
                if line.startswith('[') and ' - ' in line:
                    level_end = line.find(']')
                    if level_end > 0:
                        level = line[1:level_end]
                        timestamp_and_message = line[level_end + 2:]
                        if ' - ' in timestamp_and_message:
                            timestamp, message = timestamp_and_message.split(' - ', 1)
                            logs.append((timestamp.strip(), level.strip(), message.strip()))
                        else:
                            logs.append(("", "INFO", line))
                    else:
                        logs.append(("", "INFO", line))
                else:
                    logs.append(("", "INFO", line))
    except Exception as e:
        logs.append(("", "ERROR", f"Failed to read log file: {str(e)}"))

    return logs
def run_diagnostic_check():
    """Run diagnostic checks and return results."""
    results = {
        'python_version': None,
        'venv_exists': False,
        'pip_version': None,
        'packages_status': {},
        'openai_key': False,
        'database_connection': False,
        'errors': []
    }

    try:
        # Check Python version
        result = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            results['python_version'] = result.stdout.strip()
        else:
            results['errors'].append("Python not found")

        # Check virtual environment
        venv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.venv')
        results['venv_exists'] = os.path.exists(venv_path)

        # Check pip version
        if results['venv_exists']:
            pip_exe = os.path.join(venv_path, 'Scripts', 'pip.exe')
            if os.path.exists(pip_exe):
                result = subprocess.run([pip_exe, '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    results['pip_version'] = result.stdout.strip()

        # Check OpenAI key
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        results['openai_key'] = bool(api_key and api_key.startswith('sk-'))

        # Check database connection
        try:
            from app.database import crud
            tasks = crud.get_all_tasks()
            results['database_connection'] = True
        except Exception as e:
            results['errors'].append(f"Database connection failed: {str(e)}")

        # Check critical packages
        critical_packages = ['streamlit', 'openai', 'pillow', 'requests']
        for package in critical_packages:
            try:
                if results['venv_exists']:
                    result = subprocess.run([
                        os.path.join(venv_path, 'Scripts', 'python.exe'),
                        '-c', f'import {package}; print("OK")'
                    ], capture_output=True, text=True, timeout=10)
                    results['packages_status'][package] = result.returncode == 0
                else:
                    results['packages_status'][package] = False
            except:
                results['packages_status'][package] = False

    except Exception as e:
        results['errors'].append(f"Diagnostic check failed: {str(e)}")

    return results

def apply_fix(fix_type):
    """Apply a specific fix for common issues."""
    success = False
    message = ""

    try:
        if fix_type == 'clean_venv':
            venv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.venv')
            if os.path.exists(venv_path):
                import shutil
                shutil.rmtree(venv_path)
                message = "Virtual environment removed. Please restart the application with --clean flag."
                success = True
            else:
                message = "No virtual environment found to clean."

        elif fix_type == 'fix_corrupted_packages':
            venv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.venv')
            if os.path.exists(venv_path):
                python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
                result = subprocess.run([python_exe, 'fix_corrupted_packages.py'],
                                      capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
                if result.returncode == 0:
                    message = "Corrupted packages check completed."
                    success = True
                else:
                    message = f"Failed to check corrupted packages: {result.stderr}"
            else:
                message = "Virtual environment not found."

        elif fix_type == 'upgrade_pip':
            venv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.venv')
            if os.path.exists(venv_path):
                python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
                result = subprocess.run([python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    message = "Pip upgraded successfully."
                    success = True
                else:
                    message = f"Failed to upgrade pip: {result.stderr}"
            else:
                message = "Virtual environment not found."

        elif fix_type == 'reinstall_requirements':
            venv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.venv')
            if os.path.exists(venv_path):
                python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
                req_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'requirements.txt')
                result = subprocess.run([python_exe, '-m', 'pip', 'install', '-r', req_file],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    message = "Requirements reinstalled successfully."
                    success = True
                else:
                    message = f"Failed to reinstall requirements: {result.stderr}"
            else:
                message = "Virtual environment not found."

    except Exception as e:
        message = f"Error applying fix: {str(e)}"
        success = False

    return success, message

# --- Main Content ---
st.subheader("📊 System Diagnostics")

# Run diagnostics button
if st.button("🔍 Run System Diagnostics", type="primary"):
    with st.spinner("Running diagnostics..."):
        diagnostics = run_diagnostic_check()

    # Display results
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ✅ System Status")
        st.info(f"**Python Version:** {diagnostics['python_version'] or 'Not found'}")
        st.info(f"**Virtual Environment:** {'✅ Exists' if diagnostics['venv_exists'] else '❌ Missing'}")
        st.info(f"**Pip Version:** {diagnostics['pip_version'] or 'Not found'}")
        st.info(f"**OpenAI API Key:** {'✅ Configured' if diagnostics['openai_key'] else '❌ Missing'}")
        st.info(f"**Database Connection:** {'✅ Working' if diagnostics['database_connection'] else '❌ Failed'}")

    with col2:
        st.markdown("### 📦 Package Status")
        for package, status in diagnostics['packages_status'].items():
            st.info(f"**{package}:** {'✅ OK' if status else '❌ Failed'}")

        if diagnostics['errors']:
            st.markdown("### ⚠️ Issues Found")
            for error in diagnostics['errors']:
                st.error(error)

# --- Quick Fixes Section ---
st.markdown("---")
st.subheader("🔧 Quick Fixes")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🧹 Clean Virtual Environment", help="Remove and recreate the virtual environment"):
        with st.spinner("Cleaning virtual environment..."):
            success, message = apply_fix('clean_venv')
        if success:
            st.success(message)
        else:
            st.error(message)
        st.rerun()

with col2:
    if st.button("🔧 Fix Corrupted Packages", help="Detect and remove corrupted packages"):
        with st.spinner("Checking for corrupted packages..."):
            success, message = apply_fix('fix_corrupted_packages')
        if success:
            st.success(message)
        else:
            st.error(message)
        st.rerun()

with col3:
    if st.button("⬆️ Upgrade Pip", help="Upgrade pip to the latest version"):
        with st.spinner("Upgrading pip..."):
            success, message = apply_fix('upgrade_pip')
        if success:
            st.success(message)
        else:
            st.error(message)
        st.rerun()

with col4:
    if st.button("📦 Reinstall Requirements", help="Reinstall all required packages"):
        with st.spinner("Reinstalling requirements..."):
            success, message = apply_fix('reinstall_requirements')
        if success:
            st.success(message)
        else:
            st.error(message)
        st.rerun()

# --- Startup Logs Section ---
st.markdown("---")
st.subheader("📋 Startup Logs")

# Get latest log file
latest_log = get_latest_log_file()
log_entries = []

if latest_log:
    log_entries = parse_log_file(latest_log)
    st.info(f"📄 Showing logs from: {os.path.basename(latest_log)}")
else:
    st.warning("No startup log files found. Run the application launcher to generate logs.")

# Log display area
log_container = st.container()

with log_container:
    if log_entries:
        # Add a filter for log levels
        log_levels = list(set(entry[1] for entry in log_entries if entry[1]))
        selected_levels = st.multiselect(
            "Filter by log level:",
            options=sorted(log_levels),
            default=log_levels,
            key="log_level_filter"
        )

        filtered_entries = [entry for entry in log_entries if entry[1] in selected_levels]

        # Display logs (most recent first, limit to last 50)
        for timestamp, level, message in reversed(filtered_entries[-50:]):
            if level == "ERROR":
                st.error(f"**{timestamp}** - {message}")
            elif level == "WARNING":
                st.warning(f"**{timestamp}** - {message}")
            elif level == "SUCCESS":
                st.success(f"**{timestamp}** - {message}")
            elif level == "INFO":
                st.info(f"**{timestamp}** - {message}")
            else:
                st.text(f"**{timestamp}** - {message}")
    else:
        st.info("No log entries found in the latest startup log.")

# Log file management
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Refresh Logs"):
        st.rerun()

with col2:
    if latest_log and st.button("� Open Logs Folder"):
        import subprocess
        logs_dir = os.path.dirname(latest_log)
        try:
            subprocess.run(['explorer', logs_dir])  # Windows
        except:
            st.info(f"Logs are located at: {logs_dir}")

# --- Instructions ---
st.markdown("---")
st.subheader("📖 Troubleshooting Guide")

with st.expander("Common Issues & Solutions"):
    st.markdown("""
    ### 🚫 "Python is not installed" Error
    - **Cause**: Python is not installed or not in PATH
    - **Solution**: Install Python 3.11+ from python.org and ensure it's added to PATH

    ### 🚫 "Virtual environment creation failed" Error
    - **Cause**: Permission issues or corrupted virtual environment
    - **Solution**: Use the "Clean Virtual Environment" button above, then restart with `--clean` flag

    ### 🚫 "Corrupted packages" Warnings
    - **Cause**: Package installations got corrupted
    - **Solution**: Use the "Fix Corrupted Packages" button above

    ### 🚫 "OpenAI API Key Missing" Error
    - **Cause**: API key not configured in .env file
    - **Solution**: Add your OpenAI API key to the .env file as `OPENAI_API_KEY=sk-...`

    ### 🚫 "Database connection failed" Error
    - **Cause**: SQLite database file corrupted or missing
    - **Solution**: The database will be recreated automatically on next startup

    ### 🚫 "Pip upgrade failed" Warning
    - **Cause**: Network issues or corrupted pip installation
    - **Solution**: Use the "Upgrade Pip" button above or restart the application
    """)

# --- Footer ---
st.markdown("---")
st.caption("💡 Tip: If issues persist, try running `start_app.bat --clean` from the command line to do a complete fresh install.")