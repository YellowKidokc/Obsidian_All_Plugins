@echo off
setlocal
set "WORKBENCH=%~dp0apps\workbench\workbench.py"
if "%~1"=="" (
  set /p "VAULT=Path to the copied Markdown workspace: "
) else (
  set "VAULT=%~1"
)
if not defined VAULT exit /b 1
if not exist "%VAULT%\." exit /b 1
:menu
echo.
echo 1. Refresh workbench index
echo 2. Start local workbench
echo 3. Export HTML, Excel and FIS
echo 4. Preview folder index changes
echo 5. Exit
choice /c 12345 /n /m "Choose an action: "
if errorlevel 5 exit /b 0
if errorlevel 4 goto nav
if errorlevel 3 goto export
if errorlevel 2 goto serve
python "%WORKBENCH%" --root "%VAULT%" scan
goto menu
:serve
python "%WORKBENCH%" --root "%VAULT%" serve
goto menu
:export
python "%WORKBENCH%" --root "%VAULT%" export
goto menu
:nav
python "%WORKBENCH%" --root "%VAULT%" navigation
goto menu
