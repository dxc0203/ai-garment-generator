@echo off

title AI Garment Generator Launcher

echo ===================================================
echo  AI Garment Generator - Application Launcher
echo ===================================================
echo.

REM --- Configuration ---
REM Removed LM Studio and Stable Diffusion paths
REM --- End of Configuration ---

echo.
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not added to PATH. Please install Python 3.11 or later and try again.
    pause
    exit /b
)

echo.
echo [2/4] Activating virtual environment...
if not exist .\.venv\Scripts\activate.bat (
    echo Virtual environment not found. Creating one...
    python -m venv .venv
)
call .\.venv\Scripts\activate.bat

echo.
echo [3/4] Updating pip...
python -m pip install --upgrade pip

echo.
echo [4/4] Checking and installing required packages...
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo requirements.txt not found. Skipping package installation.
)

echo.
echo Launching the Streamlit App...
python -m streamlit run Home.py

echo.
echo ===================================================
echo  Application has been launched in your browser.
echo  You can close this window when you are finished.
echo ===================================================
pause
