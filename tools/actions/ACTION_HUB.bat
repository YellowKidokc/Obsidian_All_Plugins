@echo off
setlocal EnableExtensions
title File Action Hub

where py >nul 2>nul
if errorlevel 1 (
    set "PY=python"
) else (
    set "PY=py -3"
)

%PY% "%~dp0BACKSIDE\action_hub.py" "%~1"
if errorlevel 1 (
    echo.
    echo The Action Hub stopped with an error.
)
echo.
pause
