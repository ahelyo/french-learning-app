@echo off
cd /d "%~dp0"
echo Starting French Learning App...
start "French Learning App - Backend" "%~dp0venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
timeout /t 3 /nobreak >nul
start "French Learning App - Frontend" "%~dp0venv\Scripts\python.exe" -m streamlit run "%~dp0frontend\app.py"
