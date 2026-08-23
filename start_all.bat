@echo off
title RecruitAI - AI-Driven Recruitment Ecosystem
color 0A

echo ===============================================================================
echo                RECRUITAI - MASTER 1-CLICK SYSTEM LAUNCHER
echo ===============================================================================
echo Starting all 5 Backend Microservices + Frontend Dev Server...
echo.

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PY_CMD=.venv\Scripts\python.exe"
) else if exist ".venv312\Scripts\python.exe" (
    set "PY_CMD=.venv312\Scripts\python.exe"
) else (
    set "PY_CMD=python"
)

"%PY_CMD%" start_all.py

pause
