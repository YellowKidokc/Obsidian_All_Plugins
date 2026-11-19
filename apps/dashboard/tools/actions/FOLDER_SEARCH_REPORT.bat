@echo off
setlocal EnableExtensions
title Folder Search Report

set "TARGET=%~1"
if not defined TARGET (
    set /p "TARGET=Paste the folder path to inspect: "
)
if not exist "%TARGET%\" (
    echo Folder not found: %TARGET%
    pause
    exit /b 2
)

where py >nul 2>nul
if errorlevel 1 (
    set "PY=python"
) else (
    set "PY=py -3"
)

echo.
echo READ-ONLY FOLDER SEARCH REPORT
echo Source: %TARGET%
echo This inventories and reports. It does not delete, move, rename, or merge anything.
echo.
%PY% "%~dp0BACKSIDE\folder_search_report.py" "%TARGET%"
if errorlevel 1 (
    echo.
    echo The report did not complete.
    pause
    exit /b 1
)

for /f "delims=" %%D in ('dir /b /ad /o-d "%TARGET%\_folder_reports\folder_search_*" 2^>nul') do (
    start "" "%TARGET%\_folder_reports\%%D\REPORT.html"
    goto :done
)
:done
echo.
echo Finished. No source files or folders were changed.
pause
