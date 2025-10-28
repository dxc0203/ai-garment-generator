@echo off
REM AI Garment Generator - Quick Diagnostic Script
REM Use this script for rapid troubleshooting of common issues

echo ===================================================
echo  AI Garment Generator - Quick Diagnostics
echo ===================================================
echo.

echo [1/5] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Solution: Install Python 3.11+ and add to PATH
    goto :error
)
echo OK
echo.

echo [2/5] Checking virtual environment...
if not exist .venv (
    echo ERROR: Virtual environment not found!
    echo Solution: Run start_app.bat --clean
    goto :error
)
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Cannot activate virtual environment!
    echo Solution: Run start_app.bat --clean
    goto :error
)
echo OK
echo.

echo [3/5] Checking critical packages...
python -c "import streamlit; import google.protobuf; import openai; print('All imports OK')"
if %errorlevel% neq 0 (
    echo ERROR: Critical imports failed!
    echo Solution: Run start_app.bat --clean
    goto :error
)
echo OK
echo.

echo [4/5] Checking package integrity...
python fix_corrupted_packages.py
echo OK
echo.

echo [5/5] Testing application launch...
python -c "import streamlit; print('Streamlit version:', streamlit.__version__)"
if %errorlevel% neq 0 (
    echo ERROR: Streamlit test failed!
    goto :error
)
echo OK
echo.

echo ===================================================
echo  ALL DIAGNOSTICS PASSED - System is healthy!
echo ===================================================
echo.
echo You can now run: start_app.bat
echo.
pause
exit /b 0

:error
echo.
echo ===================================================
echo  DIAGNOSTICS FAILED - See solutions above
echo ===================================================
echo.
echo For detailed help, see SOP.md
echo.
pause
exit /b 1