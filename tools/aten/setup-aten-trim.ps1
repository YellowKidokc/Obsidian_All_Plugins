# One-time setup. Run in PowerShell opened with "Run as administrator".
#  - copies the trimmer into Program Files (admin-only, so nothing else can change
#    a script that runs as SYSTEM)
#  - schedules it weekly, Sunday 3:00 AM, keeping 30 days
#  - caps the ATEN Event Viewer log at 100 MB (oldest entries roll off)
$ErrorActionPreference = 'Stop'
$src  = Join-Path $PSScriptRoot 'trim-aten-log.ps1'
$dest = "$env:ProgramFiles\ATEN\trim-aten-log.ps1"
Copy-Item $src $dest -Force

$action   = New-ScheduledTaskAction -Execute 'powershell.exe' `
            -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$dest`" -Days 30"
$trigger  = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 3am
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName 'ATEN log trim' -Action $action -Trigger $trigger -Settings $settings `
    -User 'SYSTEM' -RunLevel Highest -Force | Out-Null

wevtutil sl "ATEN/Operational" /ms:104857600

Write-Host "Done. Weekly trim scheduled (task 'ATEN log trim'); Event Viewer log capped at 100 MB."
Write-Host "Run it now with:  Start-ScheduledTask 'ATEN log trim'"
