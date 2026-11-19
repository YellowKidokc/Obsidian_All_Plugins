@echo off
setlocal
pushd "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 BACKSIDE\projections.py
  goto finished
)
where python >nul 2>nul
if not errorlevel 1 (
  python BACKSIDE\projections.py
  goto finished
)
echo Python 3 with Tkinter is required. Python was not found.
:finished
if errorlevel 1 pause
popd
endlocal
