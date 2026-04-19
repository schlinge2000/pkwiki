# batch-ingest.ps1
# Ingestiert alle Quelldateien in raw/ neu.
# Extraktion wird uebersprungen wenn .cache bereits vorhanden.
# Usage: .\batch-ingest.ps1 [-Reset] [-OnlyDir "slides"] [-DryRun]

param(
    [switch]$Reset,
    [string]$OnlyDir = "",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$wikiRoot = $PSScriptRoot
$rawPath  = Join-Path $wikiRoot "raw"
$wikiPath = Join-Path $wikiRoot "wiki"
$logsDir  = Join-Path $wikiRoot "logs"
$logPath  = Join-Path $logsDir "batch-ingest.log"

New-Item -ItemType Directory -Force -Path $logsDir | Out-Null

function Write-Log {
    param([string]$Msg, [string]$Color = "White")
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "$ts  $Msg"
    Add-Content -Path $logPath -Value $line -Encoding UTF8
    Write-Host $line -ForegroundColor $Color
}

# Reset: wiki/ leeren und Basis anlegen
if ($Reset) {
    Write-Log "RESET: wiki/ wird geleert" "Yellow"
    if (-not $DryRun) {
        Get-ChildItem $wikiPath -Recurse -File -Include "*.md" -ErrorAction SilentlyContinue | Remove-Item -Force

        @("concepts","entities","sources","syntheses","meta") | ForEach-Object {
            New-Item -ItemType Directory -Force -Path (Join-Path $wikiPath $_) | Out-Null
        }

        $indexContent = "# Knowledge Wiki - Index`n`n> Automatisch generiert.`n`n## Konzepte`n(wird befuellt)`n`n## Quellen`n(wird befuellt)`n"
        Set-Content -Path (Join-Path $wikiPath "index.md") -Value $indexContent -Encoding UTF8

        $logContent = "# Aktivitaetslog`n`n> Append-only. Neueste Eintraege oben.`n`n"
        Set-Content -Path (Join-Path $wikiPath "log.md") -Value $logContent -Encoding UTF8

        Write-Log "wiki/ zurueckgesetzt" "Green"
    }
}

# Dateien sammeln
$searchRoot = if ($OnlyDir) { Join-Path $rawPath $OnlyDir } else { $rawPath }

$files = Get-ChildItem -Path $searchRoot -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Extension -in @(".pptx", ".pdf", ".docx") `
        -and $_.FullName -notmatch "\\.cache" `
        -and $_.FullName -notmatch "\\.potx"
    } |
    Sort-Object FullName

Write-Log "===================================================" "Cyan"
Write-Log "BATCH INGEST START -- $($files.Count) Dateien" "Cyan"
Write-Log "Reset: $Reset | DryRun: $DryRun" "Cyan"
Write-Log "===================================================" "Cyan"

$ok = 0
$failed = 0
$idx = 0

foreach ($file in $files) {
    $idx++
    $rel = $file.FullName.Substring($wikiRoot.Length + 1)
    $progress = "[$idx/$($files.Count)]"

    Write-Log "$progress  $rel" "Yellow"

    if ($DryRun) {
        Write-Log "  -> DryRun: uebersprungen" "DarkGray"
        continue
    }

    try {
        $proc = Start-Process -FilePath "uv" `
            -ArgumentList "run", "`"$wikiRoot\ingest.py`"", "`"$($file.FullName)`"" `
            -WorkingDirectory $wikiRoot `
            -Wait -PassThru -NoNewWindow `
            -RedirectStandardOutput "$logsDir\ingest_stdout.tmp" `
            -RedirectStandardError  "$logsDir\ingest_stderr.tmp"

        if ($proc.ExitCode -ne 0) {
            $err = Get-Content "$logsDir\ingest_stderr.tmp" -Raw -ErrorAction SilentlyContinue
            Write-Log "  FEHLER (exit $($proc.ExitCode)): $err" "Red"
            $failed++
        } else {
            Write-Log "  OK" "Green"
            $ok++
        }
    }
    catch {
        Write-Log "  FEHLER: $_" "Red"
        $failed++
    }

    Start-Sleep -Seconds 2
}

Write-Log "===================================================" "Cyan"
Write-Log "FERTIG -- OK: $ok | Fehler: $failed" $(if ($failed -gt 0) { "Red" } else { "Green" })
Write-Log "===================================================" "Cyan"
