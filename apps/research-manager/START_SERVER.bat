@echo off
REM Start Theophysics Backend Server
REM This script starts the Flask API server

echo ========================================
echo THEOPHYSICS BACKEND SERVER
echo ========================================
echo.

REM Check if virtual environment exists
if exist venv\ (
    echo Activating virtual environment...
    call venv\Scripts\activate
) else (
    echo No virtual environment found.
    echo Run SETUP.bat first to create one.
    echo.
    pause
    exit /b
)

REM Check if dependencies are installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Flask not installed. Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting server...
echo Server will be available at: http://localhost:5000
echo.
echo Press CTRL+C to stop the server
echo.

REM Start the Flask app
python app.py

pause
