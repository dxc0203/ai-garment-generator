@echo off
title AI Translator
echo Activating virtual environment and starting the AI maintenance script...
call .\.venv\Scripts\activate.bat
python run_maintenance.py
echo Maintenance completed. Starting the AI translation script...
python run_ai_translation.py
pause
