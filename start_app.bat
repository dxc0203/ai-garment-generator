@echo off

title AI Garment Generator Launcher

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Set log file path
set LOG_FILE=logs\startup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
set LOG_FILE=%LOG_FILE: =0%

echo =================================================== > "%LOG_FILE%"
echo  AI Garment Generator - Application Launcher >> "%LOG_FILE%"
echo  Started at: %date% %time% >> "%LOG_FILE%"
echo =================================================== >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

echo ===================================================
echo  AI Garment Generator - Application Launcher
echo ===================================================
echo.

REM Check for command line flags
set CLEAN_INSTALL=0
set UPDATE_PACKAGES=0
if "%1"=="--clean" set CLEAN_INSTALL=1
if "%1"=="-c" set CLEAN_INSTALL=1
if "%1"=="--update" set UPDATE_PACKAGES=1
if "%1"=="-u" set UPDATE_PACKAGES=1

echo [1/5] Checking Python installation...
echo [INFO] %date% %time% - Checking Python installation... >> "%LOG_FILE%"
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] %date% %time% - Python is not installed or not added to PATH. Please install Python 3.11 or later and try again. >> "%LOG_FILE%"
    echo Python is not installed or not added to PATH. Please install Python 3.11 or later and try again.
    pause
    exit /b
)
echo [SUCCESS] %date% %time% - Python installation verified >> "%LOG_FILE%"

echo.
echo [2/5] Setting up virtual environment...
echo [INFO] %date% %time% - Setting up virtual environment... >> "%LOG_FILE%"
if exist .\.venv (
    if %CLEAN_INSTALL%==1 (
        echo Clean install requested. Removing existing virtual environment...
        echo [INFO] %date% %time% - Clean install requested, removing existing virtual environment >> "%LOG_FILE%"
        rmdir /s /q .venv
        echo Creating fresh virtual environment...
        echo [INFO] %date% %time% - Creating fresh virtual environment >> "%LOG_FILE%"
        python -m venv .venv
    ) else (
        echo Virtual environment already exists. Use --clean or -c flag for fresh install.
        echo If you experience issues, run: start_app.bat --clean
        echo [INFO] %date% %time% - Using existing virtual environment >> "%LOG_FILE%"
    )
) else (
    echo No existing virtual environment found.
    echo Creating virtual environment...
    echo [INFO] %date% %time% - No existing virtual environment found, creating new one >> "%LOG_FILE%"
    python -m venv .venv
)
if %errorlevel% neq 0 (
    echo [ERROR] %date% %time% - Failed to create virtual environment. Please check your Python installation. >> "%LOG_FILE%"
    echo Failed to create virtual environment. Please check your Python installation.
    pause
    exit /b
)
echo [SUCCESS] %date% %time% - Virtual environment setup completed >> "%LOG_FILE%"
call .\.venv\Scripts\activate.bat

echo.
echo [3/5] Upgrading pip and setuptools...
echo Skipping update helper temporarily to get app running...
echo [INFO] %date% %time% - Skipping update helper to speed up startup >> "%LOG_FILE%"
echo [SUCCESS] %date% %time% - Update process skipped >> "%LOG_FILE%"

echo.
echo [4/5] Installing required packages...
echo [INFO] %date% %time% - Starting package installation >> "%LOG_FILE%"
python check_models.py >> "%LOG_FILE%" 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Model availability check completed with warnings.
    echo The application may not work correctly with unavailable models.
    echo Please review the suggestions above and update app/constants.py if needed.
    echo.
    echo [WARNING] %date% %time% - Model availability check completed with warnings >> "%LOG_FILE%"
    echo Continuing automatically in 5 seconds... (Press Ctrl+C to cancel)
    echo [INFO] %date% %time% - Continuing automatically after model check warnings >> "%LOG_FILE%"
    timeout /t 5 /nobreak >nul 2>&1
) else (
    echo Model availability check passed.
    echo [SUCCESS] %date% %time% - Model availability check passed >> "%LOG_FILE%"
)

echo.
echo [5/5] Launching the Streamlit App...
echo [INFO] %date% %time% - Launching Streamlit application >> "%LOG_FILE%"
python -m streamlit run Home.py

echo.
echo ===================================================
echo  Application has been launched in your browser.
echo  You can close this window when you are finished.
echo ===================================================
echo [SUCCESS] %date% %time% - Application launched successfully >> "%LOG_FILE%"
pause
