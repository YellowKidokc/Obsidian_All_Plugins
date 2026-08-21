@echo off
REM Setup Script for Theophysics Backend
REM Creates virtual environment and installs dependencies

echo ========================================
echo THEOPHYSICS BACKEND SETUP
echo ========================================
echo.

REM Check Python version
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or higher
    pause
    exit /b
)

echo.
echo [1/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate

echo [3/4] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo [4/4] Setup complete!
echo.
echo ========================================
echo NEXT STEPS
echo ========================================
echo.
echo 1. Install Ollama (optional, for AI features):
echo    Visit: https://ollama.ai/
echo.
echo 2. Start the server:
echo    Run: START_SERVER.bat
echo.
echo 3. Test the API:
echo    Run: TEST_API.bat
echo.
echo ========================================
echo.
pause
