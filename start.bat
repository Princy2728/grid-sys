@echo off
title GRIDWISE AI Launcher
echo ========================================================
echo   GRIDWISE AI - Starting Backend and Frontend Services
echo ========================================================

cd /d "%~dp0"

echo [1/2] Starting Backend (FastAPI on http://127.0.0.1:8000)...
start "GRIDWISE-Backend" cmd /k "cd /d "%~dp0" && .\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend (Vite on http://localhost:3000)...
start "GRIDWISE-Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

timeout /t 2 /nobreak >nul

echo ========================================================
echo   GRIDWISE AI is online!
echo   Dashboard UI: http://localhost:3000 (or http://127.0.0.1:3000)
echo   API Docs:     http://127.0.0.1:8000/docs
echo ========================================================
echo Services are running in their dedicated terminal windows.
pause
