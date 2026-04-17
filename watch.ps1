# Knowledge Wiki — Auto-Ingest Watcher
# Startet: .\watch.ps1 (im knowledge-wiki Ordner)
# Stoppt:  Strg+C

$wikiRoot = $PSScriptRoot
$rawPath = Join-Path $wikiRoot "raw"

Write-Host "Watching $rawPath for new files..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop.`n" -ForegroundColor DarkGray

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $rawPath
$watcher.Filter = "*.*"
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

$action = {
    $path = $Event.SourceEventArgs.FullPath
    $name = $Event.SourceEventArgs.Name
    $changeType = $Event.SourceEventArgs.ChangeType

    # Ignoriere temporäre Dateien, README und .cache Ordner
    if ($name -match '~\$' -or $name -match '\.tmp$' -or $name -match 'README' -or $path -match '\\\.cache\\') {
        return
    }

    if ($changeType -eq "Created") {
        # Relativen Pfad berechnen
        $relativePath = $path.Substring($wikiRoot.Length + 1).Replace("\", "/")

        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Neue Datei: $relativePath" -ForegroundColor Yellow

        # Kurz warten bis Datei vollständig geschrieben ist
        Start-Sleep -Seconds 2

        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Starte Ingest..." -ForegroundColor Green

        # ingest.py übernimmt Extraktion + API-Aufruf in einem Schritt
        Set-Location $wikiRoot
        uv run "$wikiRoot\ingest.py" $path

        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Ingest abgeschlossen.`n" -ForegroundColor Green
    }
}

Register-ObjectEvent $watcher "Created" -Action $action | Out-Null

# Warten bis Strg+C
try {
    while ($true) { Start-Sleep -Seconds 1 }
} finally {
    $watcher.EnableRaisingEvents = $false
    $watcher.Dispose()
    Write-Host "`nWatcher gestoppt." -ForegroundColor DarkGray
}
