@echo off

title AI Garment Generator Launcher

echo ===================================================
echo  AI Garment Generator - Application Launcher
echo ===================================================
echo.

REM Check for clean install flag
set CLEAN_INSTALL=0
if "%1"=="--clean" set CLEAN_INSTALL=1
if "%1"=="-c" set CLEAN_INSTALL=1

echo.
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not added to PATH. Please install Python 3.11 or later and try again.
    pause
    exit /b
)

echo.
echo [2/5] Setting up virtual environment...
if exist .\.venv (
    if %CLEAN_INSTALL%==1 (
        echo Clean install requested. Removing existing virtual environment...
        rmdir /s /q .venv
        echo Creating fresh virtual environment...
    ) else (
        echo Virtual environment already exists. Use --clean or -c flag for fresh install.
        echo If you experience issues, run: start_app.bat --clean
    )
) else (
    echo No existing virtual environment found.
    echo Creating virtual environment...
)
python -m venv .venv
if %errorlevel% neq 0 (
    echo Failed to create virtual environment. Please check your Python installation.
    pause
    exit /b
)
call .\.venv\Scripts\activate.bat

echo.
echo [3/5] Upgrading pip and setuptools...
python -m pip install --upgrade pip setuptools wheel
pip cache purge

echo.
echo [4/5] Installing required packages...
python check_models.py
if %errorlevel% neq 0 (
    echo.
    echo Model availability check completed with warnings.
    echo The application may not work correctly with unavailable models.
    echo Please review the suggestions above and update app/constants.py if needed.
    echo.
    set /p CONTINUE="Do you want to continue anyway? (y/N): "
    if /i not "!CONTINUE!"=="y" (
        echo Application launch cancelled.
        pause
        exit /b
    )
) else (
    echo Model availability check passed.
)

echo.
echo [5/5] Launching the Streamlit App...
python -m streamlit run Home.py

echo.
echo ===================================================
echo  Application has been launched in your browser.
echo  You can close this window when you are finished.
echo ===================================================
pause
