@echo off

echo Starting AI Garment Generator...

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ and add it to your PATH
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

if %PYTHON_MAJOR% lss 3 (
    echo ERROR: Python 3.11+ required. Current: %PYTHON_VERSION%
    pause
    exit /b 1
)
if %PYTHON_MAJOR%==3 if %PYTHON_MINOR% lss 11 (
    echo ERROR: Python 3.11+ required. Current: %PYTHON_VERSION%
    pause
    exit /b 1
)

echo Python %PYTHON_VERSION% found

REM Create virtual environment if it doesn't exist
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call .\.venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

REM Force clean reinstall of all requirements to fix corrupted packages
echo Force reinstalling all packages...
python -m pip install --force-reinstall -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to reinstall requirements
    pause
    exit /b 1
)

REM Test critical imports
echo Testing imports...
python -c "
try:
    import streamlit
    import openai
    import pandas
    import PIL
    print('All imports successful')
except ImportError as e:
    print(f'Import error: {e}')
    exit(1)
"

if %errorlevel% neq 0 (
    echo ERROR: Critical imports failed
    pause
    exit /b 1
)

REM Launch the application
echo Launching application...
python -m streamlit run Home.py

echo Application launched. Press any key to close...
pause >nul
