@echo off
title AI Garment Generator Launcher

echo ===================================================
echo  AI Garment Generator - Application Launcher
echo ===================================================
echo.

REM --- Configuration ---
set LM_STUDIO_PATH="C:\Program Files\LM Studio\LM Studio.exe"
set SD_WEBUI_DIR="C:\Users\alvin\OneDrive\Work\Python\stable-diffusion-webui"
REM --- End of Configuration ---


echo [1/4] Launching LM Studio in a new window...
start "LM Studio" %LM_STUDIO_PATH%

echo [2/4] Launching Stable Diffusion WebUI in a new window...
start "Stable Diffusion WebUI" /D %SD_WEBUI_DIR% webui-user.bat

echo.
echo Waiting 5 seconds for AI servers to initialize...
timeout /t 5 /nobreak >nul

echo.
echo [3/4] Activating virtual environment and checking for maintenance...
call .\.venv\Scripts\activate.bat
REM --- THIS IS THE NEW STEP ---
REM Run the maintenance check script.
python check_maintenance.py

echo.
echo [4/4] Launching the Streamlit App...
python -m streamlit run Home.py

echo.
echo ===================================================
echo  Application has been launched in your browser.
echo  You can close this window when you are finished.
echo ===================================================
pause
