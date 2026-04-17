# Knowledge Wiki - Auto-Ingest Watcher
# Startet: .\watch.ps1 (im knowledge-wiki Ordner)
# Stoppt:  Strg+C
# Logs:    logs\watcher.log

$wikiRoot = $PSScriptRoot
$rawPath  = Join-Path $wikiRoot "raw"
$logsDir  = Join-Path $wikiRoot "logs"
$logFile  = Join-Path $logsDir "watcher.log"

# Logs-Ordner anlegen falls nicht vorhanden
if (-not (Test-Path $logsDir)) { New-Item -ItemType Directory -Path $logsDir | Out-Null }

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $ts   = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "$ts  $($Level.PadRight(8))  $Message"
    Add-Content -Path $logFile -Value $line -Encoding UTF8
    switch ($Level) {
        "ERROR" { Write-Host $line -ForegroundColor Red    }
        "WARN"  { Write-Host $line -ForegroundColor Yellow }
        "INFO"  { Write-Host $line -ForegroundColor Cyan   }
        default { Write-Host $line                         }
    }
}

Write-Log "Watcher gestartet - ueberwache: $rawPath"
Write-Log "Log-Datei: $logFile"
Write-Host "Press Ctrl+C to stop." -ForegroundColor DarkGray

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $rawPath
$watcher.Filter = "*.*"
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

$action = {
    $path       = $Event.SourceEventArgs.FullPath
    $name       = $Event.SourceEventArgs.Name
    $changeType = $Event.SourceEventArgs.ChangeType

    # Ignoriere temp-Dateien, .cache-Ordner
    if ($name -match '~\$' -or $name -match '\.tmp$' -or $name -match 'README' -or $path -match '\\\.cache\\') {
        return
    }

    if ($changeType -eq "Created") {
        $relativePath = $path.Substring($using:wikiRoot.Length + 1)
        $logF = $using:logFile
        $wRoot = $using:wikiRoot

        $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Add-Content -Path $logF -Value "$ts  INFO      Neue Datei erkannt: $relativePath" -Encoding UTF8
        Write-Host "$ts  INFO      Neue Datei erkannt: $relativePath" -ForegroundColor Yellow

        # Kurz warten bis Datei vollstaendig geschrieben ist
        Start-Sleep -Seconds 2

        $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Add-Content -Path $logF -Value "$ts  INFO      Starte Ingest: $relativePath" -Encoding UTF8
        Write-Host "$ts  INFO      Starte Ingest: $relativePath" -ForegroundColor Green

        Set-Location $wRoot

        # Output von ingest.py in Log schreiben
        $result = uv run "$wRoot\ingest.py" $path 2>&1
        $exitCode = $LASTEXITCODE

        foreach ($line in $result) {
            Add-Content -Path $logF -Value $line -Encoding UTF8
            Write-Host $line
        }

        $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        if ($exitCode -eq 0) {
            Add-Content -Path $logF -Value "$ts  INFO      Ingest abgeschlossen: $relativePath" -Encoding UTF8
            Write-Host "$ts  INFO      Ingest abgeschlossen: $relativePath" -ForegroundColor Green
        } else {
            Add-Content -Path $logF -Value "$ts  ERROR     Ingest FEHLGESCHLAGEN (Exit $exitCode): $relativePath" -Encoding UTF8
            Write-Host "$ts  ERROR     Ingest FEHLGESCHLAGEN (Exit $exitCode): $relativePath" -ForegroundColor Red
        }
    }
}

Register-ObjectEvent $watcher "Created" -Action $action | Out-Null

try {
    while ($true) { Start-Sleep -Seconds 1 }
} finally {
    $watcher.EnableRaisingEvents = $false
    $watcher.Dispose()
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logFile -Value "$ts  INFO      Watcher gestoppt." -Encoding UTF8
    Write-Host "Watcher gestoppt." -ForegroundColor DarkGray
}
