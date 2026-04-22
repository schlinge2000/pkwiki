# setup.ps1 - Knowledge Tree Ersteinrichtung
#
# Fuehrt folgende Schritte aus:
#   1. Prueft Voraussetzungen (uv, git)
#   2. .env aus .env.example erstellen (interaktiv)
#   3. Vault-Verzeichnisstruktur anlegen
#   4. Verbindung testen (Azure OpenAI Ping)
#
# Usage: .\setup.ps1
# Usage: .\setup.ps1 -VaultRoot "C:\MeinVault" -NonInteractive

param(
    [string]$VaultRoot = "",
    [switch]$NonInteractive
)

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot

Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "  Knowledge Tree Setup" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# -- 1. Voraussetzungen ----------------------------------------------------

Write-Host "[1/4] Pruefe Voraussetzungen..." -ForegroundColor Yellow

$missing = @()
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { $missing += "uv (winget install astral-sh.uv)" }
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { $missing += "git" }

if ($missing.Count -gt 0) {
    Write-Host "Fehlende Tools:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}
Write-Host "  OK (uv + git vorhanden)" -ForegroundColor Green

# -- 2. .env erstellen -----------------------------------------------------

Write-Host ""
Write-Host "[2/4] Konfiguration (.env)..." -ForegroundColor Yellow

$envFile = Join-Path $ScriptRoot ".env"
$envExample = Join-Path $ScriptRoot ".env.example"

if (Test-Path $envFile) {
    Write-Host "  .env bereits vorhanden - wird nicht ueberschrieben." -ForegroundColor DarkGray
    $existingEnv = Get-Content $envFile -Raw
} else {
    if (-not (Test-Path $envExample)) {
        Write-Host "  .env.example nicht gefunden!" -ForegroundColor Red
        exit 1
    }
    Copy-Item $envExample $envFile
    Write-Host "  .env aus .env.example erstellt." -ForegroundColor Green
    $existingEnv = ""
}

# VaultRoot bestimmen
if (-not $VaultRoot) {
    # Aus .env lesen falls schon gesetzt
    if ($existingEnv -match 'VAULT_ROOT=(.+)') {
        $VaultRoot = $Matches[1].Trim()
    }
}

if (-not $VaultRoot -and -not $NonInteractive) {
    Write-Host ""
    Write-Host "  Wo sollen die Vault-Daten liegen (wiki/, raw/, assets/)?" -ForegroundColor Cyan
    Write-Host "  Empfehlung: OneDrive-Ordner fuer automatische Synchronisation" -ForegroundColor DarkGray
    Write-Host ""
    $default = "C:\Users\$env:USERNAME\OneDrive - INFORM GmbH\knowledge-wiki"
    $input = Read-Host "  Vault-Pfad [$default]"
    $VaultRoot = if ($input.Trim()) { $input.Trim() } else { $default }
}

if (-not $VaultRoot) {
    Write-Host "  Kein Vault-Pfad gesetzt. Verwende Skript-Verzeichnis als Fallback." -ForegroundColor Yellow
    $VaultRoot = $ScriptRoot
}

# VAULT_ROOT in .env eintragen
$envContent = Get-Content $envFile -Raw
if ($envContent -match 'VAULT_ROOT=<user>') {
    $envContent = $envContent -replace 'VAULT_ROOT=.*', "VAULT_ROOT=$VaultRoot"
    Set-Content $envFile -Value $envContent -Encoding UTF8 -NoNewline
    Write-Host "  VAULT_ROOT=$VaultRoot eingetragen." -ForegroundColor Green
} elseif (-not ($envContent -match 'VAULT_ROOT=')) {
    Add-Content $envFile "`nVAULT_ROOT=$VaultRoot"
    Write-Host "  VAULT_ROOT=$VaultRoot ergaenzt." -ForegroundColor Green
} else {
    Write-Host "  VAULT_ROOT bereits gesetzt: $VaultRoot" -ForegroundColor DarkGray
}

# -- 3. Vault-Struktur anlegen ---------------------------------------------

Write-Host ""
Write-Host "[3/4] Vault-Verzeichnisstruktur anlegen..." -ForegroundColor Yellow

$dirs = @(
    "wiki",
    "wiki\concepts",
    "wiki\entities",
    "wiki\sources",
    "wiki\syntheses",
    "wiki\meta",
    "raw\slides",
    "raw\docs",
    "raw\pdfs",
    "raw\.cache",
    "assets",
    "output",
    "logs"
)

foreach ($dir in $dirs) {
    $fullPath = Join-Path $VaultRoot $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Force -Path $fullPath | Out-Null
        Write-Host "  Erstellt: $dir" -ForegroundColor DarkGray
    }
}

# Basis wiki/index.md anlegen falls nicht vorhanden
$indexPath = Join-Path $VaultRoot "wiki\index.md"
if (-not (Test-Path $indexPath)) {
    Set-Content $indexPath -Value @"
# Knowledge Tree -- Index

> Automatisch generiert. Stand: $(Get-Date -Format 'yyyy-MM-dd')

| Domain | Beschreibung | Seiten | Zuletzt aktualisiert |
|--------|--------------|--------|---------------------|
"@ -Encoding UTF8
    Write-Host "  wiki\index.md angelegt." -ForegroundColor DarkGray
}

# wiki/log.md anlegen falls nicht vorhanden
$logPath = Join-Path $VaultRoot "wiki\log.md"
if (-not (Test-Path $logPath)) {
    Set-Content $logPath -Value @"
# Aktivitaetslog

> Append-only. Neueste Eintraege oben.

"@ -Encoding UTF8
    Write-Host "  wiki\log.md angelegt." -ForegroundColor DarkGray
}

Write-Host "  Vault-Struktur OK." -ForegroundColor Green

# -- 4. Verbindungstest ----------------------------------------------------

Write-Host ""
Write-Host "[4/4] Verbindung testen..." -ForegroundColor Yellow

# uv schreibt Download-Fortschritt nach stderr. Unter ErrorActionPreference=Stop
# wuerde das als terminierender Fehler interpretiert, obwohl uv sauber laeuft.
$prevEAP = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$testResult = & uv run --with openai --with python-dotenv "$ScriptRoot\test-connection.py" 2>&1
$ErrorActionPreference = $prevEAP
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Azure OpenAI: OK" -ForegroundColor Green
} else {
    Write-Host "  Azure OpenAI: FEHLER" -ForegroundColor Red
    Write-Host "  $testResult" -ForegroundColor Red
    Write-Host "  Bitte AZURE_OPENAI_ENDPOINT und AZURE_OPENAI_API_KEY in .env pruefen." -ForegroundColor Yellow
}

# -- Zusammenfassung -------------------------------------------------------

Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "  Setup abgeschlossen!" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Code:   $ScriptRoot" -ForegroundColor White
Write-Host "  Vault:  $VaultRoot" -ForegroundColor White
Write-Host ""
Write-Host "  Naechste Schritte:" -ForegroundColor Cyan
Write-Host "  1. Dokument ingestieren:" -ForegroundColor White
Write-Host "     uv run `"$ScriptRoot\ingest.py`" `"$VaultRoot\raw\slides\Meine-Praesentation.pptx`"" -ForegroundColor DarkGray
Write-Host "  2. Code-Monitoring starten (GITHUB_PAT in .env setzen):" -ForegroundColor White
Write-Host "     uv run `"$ScriptRoot\code-watch.py`" --loop" -ForegroundColor DarkGray
Write-Host ""
