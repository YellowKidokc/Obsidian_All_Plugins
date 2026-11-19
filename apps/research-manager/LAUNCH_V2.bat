@echo off
title Theophysics Research Manager V2
echo.
echo ========================================
echo   Theophysics Research Manager V2
echo   Sidebar Navigation Edition
echo ========================================
echo.

cd /d "%~dp0"

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo No virtual environment found, creating local venv...
    python -m venv venv
    if errorlevel 1 goto launch_error
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

python -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo PySide6 or other dependencies missing, installing requirements...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt -r requirements_v2.txt
    if errorlevel 1 goto launch_error
)

echo Starting application...
echo.

python app_v2.py

if errorlevel 1 (
:launch_error
    echo.
    echo ========================================
    echo ERROR: Application exited with error
    echo ========================================
    pause
)
