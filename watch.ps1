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

function Invoke-IngestFile {
    param([string]$FilePath, [string]$RelativePath)
    Write-Log "Starte Ingest: $RelativePath"
    Set-Location $wikiRoot
    $result   = uv run "$wikiRoot\ingest.py" $FilePath 2>&1
    $exitCode = $LASTEXITCODE
    foreach ($line in $result) {
        Add-Content -Path $logFile -Value $line -Encoding UTF8
        Write-Host $line
    }
    if ($exitCode -eq 0) {
        Write-Log "Ingest abgeschlossen: $RelativePath"
    } else {
        Write-Log "Ingest FEHLGESCHLAGEN (Exit $exitCode): $RelativePath" "ERROR"
    }
}

function Invoke-StartupScan {
    $cacheDir  = Join-Path $rawPath ".cache"
    Write-Log "Startup-Scan: prüfe ungeverarbeitete Dateien in raw/ ..."

    $supportedExt = @('.txt', '.pptx', '.docx', '.pdf', '.md')

    $files = Get-ChildItem $rawPath -Recurse -File | Where-Object {
        # .cache-Ordner und manuals-Ordner (eigene Pipeline) ausschliessen
        $_.FullName -notmatch '\\\.cache\\' -and
        $_.FullName -notmatch '\\manuals\\'  -and
        $_.Name     -notmatch '~\$'          -and
        $_.Name     -notmatch '\.tmp$'       -and
        $_.Name     -notmatch 'README'       -and
        $supportedExt -contains $_.Extension.ToLower()
    }

    $pending = 0
    foreach ($file in $files) {
        $rel    = $file.FullName.Substring($rawPath.Length + 1)
        $stem   = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
        $subDir = Split-Path $rel -Parent
        if ($subDir) {
            $cacheMd = Join-Path $cacheDir "$subDir\$stem.md"
        } else {
            $cacheMd = Join-Path $cacheDir "$stem.md"
        }

        if (-not (Test-Path $cacheMd)) {
            $pending++
            Write-Log "AUSSTEHEND: $rel" "WARN"
            Start-Sleep -Seconds 2   # OneDrive-Sync abwarten
            Invoke-IngestFile -FilePath $file.FullName -RelativePath $rel
        }
    }

    if ($pending -eq 0) {
        Write-Log "Startup-Scan: alle Dateien bereits verarbeitet."
    } else {
        Write-Log "Startup-Scan abgeschlossen — $pending Datei(en) nachverarbeitet."
    }
}

Write-Log "Watcher gestartet — überwache: $rawPath"
Write-Log "Log-Datei: $logFile"
Write-Host "Press Ctrl+C to stop." -ForegroundColor DarkGray

# Beim Start: bereits vorhandene, unverarbeitete Dateien nachholen
Invoke-StartupScan

# FileSystemWatcher für neue Dateien
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path                  = $rawPath
$watcher.Filter                = "*.*"
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents   = $true

$action = {
    $path       = $Event.SourceEventArgs.FullPath
    $name       = $Event.SourceEventArgs.Name
    $changeType = $Event.SourceEventArgs.ChangeType

    # Ignoriere temp-Dateien und .cache-Ordner
    if ($name  -match '~\$'         -or
        $name  -match '\.tmp$'      -or
        $name  -match 'README'      -or
        $path  -match '\\\.cache\\' -or
        $path  -match '\\manuals\\') {
        return
    }

    if ($changeType -eq "Created") {
        $relativePath = $path.Substring($using:wikiRoot.Length + 1)
        $wRoot = $using:wikiRoot
        $logF  = $using:logFile

        $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Add-Content -Path $logF -Value "$ts  INFO      Neue Datei erkannt: $relativePath" -Encoding UTF8
        Write-Host "$ts  INFO      Neue Datei erkannt: $relativePath" -ForegroundColor Yellow

        # Kurz warten bis Datei vollständig geschrieben ist
        Start-Sleep -Seconds 2

        $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Add-Content -Path $logF -Value "$ts  INFO      Starte Ingest: $relativePath" -Encoding UTF8
        Write-Host "$ts  INFO      Starte Ingest: $relativePath" -ForegroundColor Green

        Set-Location $wRoot
        $result   = uv run "$wRoot\ingest.py" $path 2>&1
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
