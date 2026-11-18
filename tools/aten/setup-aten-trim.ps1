# One-time setup. Run in PowerShell opened with "Run as administrator".
#  - copies the rotation script into Program Files (admin-only, so nothing else can
#    change a script that runs as SYSTEM)
#  - schedules it MONTHLY: the 1st of every month at 3:00 AM (catches up if the PC was off)
#  - older-than-30-days entries are archived as .jsonl.gz in C:\ProgramData\aten\archive
#  - caps the ATEN Event Viewer log at 100 MB (oldest entries roll off)
# Safe to run again: it replaces the task (removes any older weekly version).
$ErrorActionPreference = 'Stop'
$src  = Join-Path $PSScriptRoot 'trim-aten-log.ps1'
$dest = "$env:ProgramFiles\ATEN\trim-aten-log.ps1"
Copy-Item $src $dest -Force

$start = (Get-Date -Day 1).AddMonths(1).ToString('yyyy-MM-dd') + 'T03:00:00'
$xml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo><Description>Monthly ATEN log rotation: archive entries older than 30 days.</Description></RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>$start</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByMonth>
        <DaysOfMonth><Day>1</Day></DaysOfMonth>
        <Months><January/><February/><March/><April/><May/><June/><July/><August/><September/><October/><November/><December/></Months>
      </ScheduleByMonth>
    </CalendarTrigger>
  </Triggers>
  <Principals><Principal id="Author"><UserId>S-1-5-18</UserId><RunLevel>HighestAvailable</RunLevel></Principal></Principals>
  <Settings>
    <StartWhenAvailable>true</StartWhenAvailable>
    <ExecutionTimeLimit>PT2H</ExecutionTimeLimit>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <Enabled>true</Enabled>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>powershell.exe</Command>
      <Arguments>-NoProfile -ExecutionPolicy Bypass -File "$dest" -Days 30</Arguments>
    </Exec>
  </Actions>
</Task>
"@
Register-ScheduledTask -TaskName 'ATEN log trim' -Xml $xml -Force | Out-Null

wevtutil sl "ATEN/Operational" /ms:104857600

Write-Host "Done. Monthly rotation scheduled (task 'ATEN log trim', 1st of each month, 3 AM)."
Write-Host "Old entries go to C:\ProgramData\aten\archive as .jsonl.gz. Event Viewer log capped at 100 MB."
Write-Host "Run it now with:  Start-ScheduledTask 'ATEN log trim'"
