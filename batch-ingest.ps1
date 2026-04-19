# batch-ingest.ps1
# Ingestiert alle Quelldateien in raw/ neu.
# Extraktion wird übersprungen wenn .cache bereits vorhanden.
# Usage: .\batch-ingest.ps1 [-Reset] [-Filter "*.pptx"]

param(
    [switch]$Reset,                        # wiki/ leeren und neu aufbauen
    [string]$Filter = "*.pptx,*.pdf,*.docx",  # Dateiarten
    [string]$OnlyDir = "",                 # Nur bestimmtes Unterverzeichnis (z.B. "slides")
    [switch]$DryRun                        # Nur zeigen, was verarbeitet würde
)

$ErrorActionPreference = "Stop"
$wikiRoot = $PSScriptRoot
$rawPath  = Join-Path $wikiRoot "raw"
$wikiPath = Join-Path $wikiRoot "wiki"
$logPath  = Join-Path $wikiRoot "logs\batch-ingest.log"

# Log-Verzeichnis sicherstellen
New-Item -ItemType Directory -Force -Path (Split-Path $logPath) | Out-Null

function Write-Log {
    param([string]$Msg, [string]$Color = "White")
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "$ts  $Msg"
    Add-Content -Path $logPath -Value $line -Encoding UTF8
    Write-Host $line -ForegroundColor $Color
}

# ── Optionales Reset ────────────────────────────────────────────────────────
if ($Reset) {
    Write-Log "RESET: wiki/ wird geleert (index.md + log.md werden neu angelegt)" "Yellow"
    if (-not $DryRun) {
        # Alle Seiten löschen außer .obsidian/, pictures, etc.
        Get-ChildItem $wikiPath -Recurse -File -Include "*.md" | Remove-Item -Force

        # Leere Basis-Struktur anlegen
        @("concepts","entities","sources","syntheses","meta") | ForEach-Object {
            New-Item -ItemType Directory -Force -Path (Join-Path $wikiPath $_) | Out-Null
        }

        # Minimales index.md
        Set-Content -Path (Join-Path $wikiPath "index.md") -Value @"
# Knowledge Wiki — Index

> Automatisch generiert. Nicht manuell bearbeiten.

## Konzepte
(wird befüllt)

## Quellen
(wird befüllt)
"@ -Encoding UTF8

        # Minimales log.md
        Set-Content -Path (Join-Path $wikiPath "log.md") -Value @"
# Aktivitätslog

> Append-only. Neueste Einträge oben.

"@ -Encoding UTF8

        Write-Log "wiki/ zurückgesetzt." "Green"
    }
}

# ── Dateien sammeln ─────────────────────────────────────────────────────────
$extensions = $Filter -split "," | ForEach-Object { $_.Trim() }
$searchRoot = if ($OnlyDir) { Join-Path $rawPath $OnlyDir } else { $rawPath }

$files = Get-ChildItem -Path $searchRoot -Recurse -File |
    Where-Object {
        $ext = "*$($_.Extension)"
        ($extensions | Where-Object { $_ -like $ext }).Count -gt 0 `
        -and $_.FullName -notmatch "\\.cache" `
        -and $_.Extension -ne ".potx"        # Templates ausschließen
    } |
    Sort-Object FullName

Write-Log "═══════════════════════════════════════════════════════" "Cyan"
Write-Log "BATCH INGEST START — $($files.Count) Dateien" "Cyan"
Write-Log "Reset: $Reset | DryRun: $DryRun | Filter: $Filter" "Cyan"
Write-Log "═══════════════════════════════════════════════════════" "Cyan"

# ── Ingest-Loop ─────────────────────────────────────────────────────────────
$ok = 0; $failed = 0; $idx = 0

foreach ($file in $files) {
    $idx++
    $rel = $file.FullName.Substring($wikiRoot.Length + 1)
    $progress = "[$idx/$($files.Count)]"

    Write-Log "$progress  $rel" "Yellow"

    if ($DryRun) {
        Write-Log "  → DryRun: übersprungen" "DarkGray"
        continue
    }

    try {
        $result = & uv run "$wikiRoot\ingest.py" $file.FullName 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw $result
        }
        Write-Log "  ✓ OK" "Green"
        $ok++
    }
    catch {
        Write-Log "  ✗ FEHLER: $_" "Red"
        $failed++
    }

    # Kurze Pause damit Azure OpenAI Rate-Limits greifen können
    Start-Sleep -Seconds 2
}

# ── Zusammenfassung ──────────────────────────────────────────────────────────
Write-Log "═══════════════════════════════════════════════════════" "Cyan"
Write-Log "BATCH INGEST FERTIG — OK: $ok | Fehler: $failed" $(if ($failed -gt 0) {"Red"} else {"Green"})
Write-Log "═══════════════════════════════════════════════════════" "Cyan"
