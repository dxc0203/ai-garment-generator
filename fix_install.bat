@echo off
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
python check_models.py
echo Installation complete. Press any key to exit.
pause >nul