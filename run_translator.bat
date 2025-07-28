@echo off
title AI Translator

echo Activating virtual environment and starting the AI translation script...

call .\.venv\Scripts\activate.bat
python run_ai_translation.py

pause
