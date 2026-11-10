@echo off
setlocal EnableExtensions

set "WORKFLOW_LAUNCHER=D:\GitHub\pipeline-workflows\workflows\FolderResearchIntake\RUN_FOLDER_RESEARCH.bat"
if not exist "%WORKFLOW_LAUNCHER%" (
    echo Folder Research Intake workflow was not found:
    echo %WORKFLOW_LAUNCHER%
    pause
    exit /b 2
)

call "%WORKFLOW_LAUNCHER%"
exit /b %ERRORLEVEL%
