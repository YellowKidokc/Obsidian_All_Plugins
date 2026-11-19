# Monthly ATEN log rotation. Runs as SYSTEM on the 1st of each month.
# Lines older than $Days days are MOVED (not deleted) into a compressed archive:
#   <log folder>\archive\events-until-YYYY-MM-DD.jsonl.gz
# so they can be loaded into another system later. Recent lines stay in events.jsonl.
# The service is paused while the file is rewritten (no events lost mid-write),
# the new files are built beside the old one and swapped in, and a line whose
# time can't be read is always kept, never guessed away.
param(
    [string]$Path = "$env:ProgramData\aten\events.jsonl",
    [int]$Days = 30,
    [switch]$NoService          # for testing on a copy
)
$ErrorActionPreference = 'Stop'
$cutoff  = [DateTime]::UtcNow.AddDays(-$Days)
$cutText = $cutoff.ToString('yyyy-MM-ddTHH:mm:ss')
$stamp   = [regex]'"timestamp":"([0-9T:\-]{19})'
$folder  = Split-Path $Path
$log     = Join-Path $folder 'trim.log'
$archDir = Join-Path $folder 'archive'

if (-not (Test-Path $Path)) { exit 0 }
New-Item -ItemType Directory -Force $archDir | Out-Null
$archive = Join-Path $archDir ("events-until-{0}.jsonl.gz" -f $cutoff.ToString('yyyy-MM-dd'))
if (Test-Path $archive) {           # never overwrite an earlier archive
    $archive = $archive -replace '\.jsonl\.gz$', ("-{0}.jsonl.gz" -f (Get-Date -Format HHmmss))
}

if (-not $NoService) { Stop-Service atensvc -Force }
$temp = "$Path.trimming"; $archTemp = "$archive.partial"
try {
    $utf8   = New-Object System.Text.UTF8Encoding($false)
    $reader = New-Object System.IO.StreamReader($Path, $utf8)
    $keep   = New-Object System.IO.StreamWriter($temp, $false, $utf8)
    $gzFile = [System.IO.File]::Create($archTemp)
    $gzip   = New-Object System.IO.Compression.GZipStream($gzFile, [System.IO.Compression.CompressionLevel]::Optimal)
    $old    = New-Object System.IO.StreamWriter($gzip, $utf8)
    $kept = 0; $moved = 0
    try {
        while ($null -ne ($line = $reader.ReadLine())) {
            $m = $stamp.Match($line)
            if ($m.Success -and [string]::CompareOrdinal($m.Groups[1].Value, $cutText) -lt 0) {
                $old.WriteLine($line); $moved++
            } else {
                $keep.WriteLine($line); $kept++
            }
        }
    } finally { $reader.Close(); $keep.Close(); $old.Close() }

    if ($moved -gt 0) { Move-Item $archTemp $archive -Force } else { Remove-Item $archTemp }
    Move-Item $temp $Path -Force
    $where = if ($moved -gt 0) { " -> $archive" } else { '' }
    Add-Content $log "$(Get-Date -Format s)  kept $kept, archived $moved older than $Days days$where" -Encoding utf8
} catch {
    Remove-Item $temp, $archTemp -ErrorAction SilentlyContinue
    Add-Content $log "$(Get-Date -Format s)  FAILED (log left unchanged): $($_.Exception.Message)" -Encoding utf8
    throw
} finally {
    if (-not $NoService) { Start-Service atensvc }
}
