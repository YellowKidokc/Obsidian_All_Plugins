@echo off
title Theophysics Vault Sync to PostgreSQL
echo.
echo ========================================
echo   Theophysics Vault Sync to PostgreSQL
echo ========================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo No virtual environment found, creating local venv...
    python -m venv venv
    if errorlevel 1 goto sync_error
)

call venv\Scripts\activate.bat

python -c "import psycopg2, yaml" >nul 2>&1
if errorlevel 1 (
    echo Dependencies missing, installing requirements...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt -r requirements_v2.txt
    if errorlevel 1 goto sync_error
)

set "VAULT_PATH=O:\_Theophysics_v5"
if not exist "%VAULT_PATH%" (
    echo Default vault not found: %VAULT_PATH%
    set /p VAULT_PATH="Enter vault path to sync: "
)

echo Syncing vault:
echo   %VAULT_PATH%
echo.
python core\vault_sync_engine.py "%VAULT_PATH%"
if errorlevel 1 goto sync_error

echo.
echo ========================================
echo SYNC COMPLETE
echo ========================================
pause
exit /b 0

:sync_error
echo.
echo ========================================
echo ERROR: Sync exited with error
echo ========================================
pause
exit /b 1
