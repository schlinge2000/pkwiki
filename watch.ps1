# Knowledge Wiki — Auto-Ingest Watcher
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

Write-Log "Watcher gestartet — überwache: $rawPath"
Write-Log "Log-Datei: $logFile"
Write-Host "Press Ctrl+C to stop.`n" -ForegroundColor DarkGray

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $rawPath
$watcher.Filter = "*.*"
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

$action = {
    $path       = $Event.SourceEventArgs.FullPath
    $name       = $Event.SourceEventArgs.Name
    $changeType = $Event.SourceEventArgs.ChangeType

    # Ignoriere temp-Dateien, .cache-Ordner, .md-Extrakte im cache
    if ($name -match '~\$' -or $name -match '\.tmp$' -or $name -match 'README' -or $path -match '\\\.cache\\') {
        return
    }

    if ($changeType -eq "Created") {
        $relativePath = $path.Substring($using:wikiRoot.Length + 1)

        & $using:function:Write-Log "Neue Datei erkannt: $relativePath"

        # Kurz warten bis Datei vollständig geschrieben ist
        Start-Sleep -Seconds 2

        & $using:function:Write-Log "Starte Ingest: $relativePath"

        Set-Location $using:wikiRoot

        # Output von ingest.py direkt in Konsole + watcher.log schreiben
        $result = uv run "$using:wikiRoot\ingest.py" $path 2>&1
        $exitCode = $LASTEXITCODE

        foreach ($line in $result) {
            Add-Content -Path $using:logFile -Value $line -Encoding UTF8
        }

        if ($exitCode -eq 0) {
            & $using:function:Write-Log "Ingest abgeschlossen: $relativePath"
        } else {
            & $using:function:Write-Log "Ingest FEHLGESCHLAGEN (Exit $exitCode): $relativePath" "ERROR"
        }
    }
}

Register-ObjectEvent $watcher "Created" -Action $action | Out-Null

try {
    while ($true) { Start-Sleep -Seconds 1 }
} finally {
    $watcher.EnableRaisingEvents = $false
    $watcher.Dispose()
    Write-Log "Watcher gestoppt."
}
