# Keeps the last $Days days of ATEN's events.jsonl. Runs weekly as SYSTEM.
# The service is stopped while the file is rewritten so no events are lost
# mid-write, then started again. The new file is built beside the old one and
# swapped in, so a crash never leaves a half-trimmed log.
param(
    [string]$Path = "$env:ProgramData\aten\events.jsonl",
    [int]$Days = 30,
    [switch]$NoService          # for testing on a copy
)
$ErrorActionPreference = 'Stop'
$cutoff = [DateTime]::UtcNow.AddDays(-$Days).ToString('yyyy-MM-ddTHH:mm:ss')
$stamp  = [regex]'"timestamp":"([0-9T:\-]{19})'
$log    = Join-Path (Split-Path $Path) 'trim.log'

if (-not (Test-Path $Path)) { exit 0 }
if (-not $NoService) { Stop-Service atensvc -Force }
try {
    $temp = "$Path.trimming"
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    $reader = New-Object System.IO.StreamReader($Path, $utf8)
    $writer = New-Object System.IO.StreamWriter($temp, $false, $utf8)
    $kept = 0; $dropped = 0
    try {
        while ($null -ne ($line = $reader.ReadLine())) {
            $m = $stamp.Match($line)
            # Keep lines that are recent, or whose time can't be read (never lose data by guessing).
            if (-not $m.Success -or [string]::CompareOrdinal($m.Groups[1].Value, $cutoff) -ge 0) {
                $writer.WriteLine($line); $kept++
            } else { $dropped++ }
        }
    } finally { $reader.Close(); $writer.Close() }
    Move-Item $temp $Path -Force
    Add-Content $log "$(Get-Date -Format s)  kept $kept, removed $dropped older than $Days days" -Encoding utf8
} catch {
    Remove-Item "$Path.trimming" -ErrorAction SilentlyContinue
    Add-Content $log "$(Get-Date -Format s)  FAILED: $($_.Exception.Message)" -Encoding utf8
    throw
} finally {
    if (-not $NoService) { Start-Service atensvc }
}
