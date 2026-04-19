# Retry aller fehlgeschlagenen Ingests
$wikiRoot = $PSScriptRoot
$errors = @()
$i = 0

$relPaths = @(
    'raw\slides\SFS Demand AI.pptx',
    'raw\docs\Protokoll_Product_Portfolio_Weekly_2025-08-05.docx',
    'raw\docs\Aufbau_Vertragsinhalte (1).docx',
    'raw\pdfs\OpenAI Assistants API Guide_ Step-by-Step Tutorial _ Medium.pdf',
    'raw\pdfs\BO_WEB_Handout.pdf',
    'raw\pdfs\Architecting SAP Extensions with Microsoft Power Platform-1.pdf'
)

# Dateien mit Sonderzeichen im Namen per Wildcard suchen
$wildcardSearches = @(
    @{ Dir = 'raw\docs';  Pattern = '*Gespr*Sales*' },
    @{ Dir = 'raw\pdfs';  Pattern = '*Time Series Complexity*' },
    @{ Dir = 'raw\pdfs';  Pattern = '*Umfrage*Transformation*' },
    @{ Dir = 'raw\pdfs';  Pattern = '*CX25*' }
)

$allFiles = @()
foreach ($rel in $relPaths) {
    $full = Join-Path $wikiRoot $rel
    if (Test-Path $full) { $allFiles += $full }
    else { Write-Host "Nicht gefunden: $rel" -ForegroundColor Yellow }
}
foreach ($ws in $wildcardSearches) {
    $dir = Join-Path $wikiRoot $ws.Dir
    $found = Get-ChildItem $dir -Filter $ws.Pattern -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) { $allFiles += $found.FullName }
    else { Write-Host "Nicht gefunden: $($ws.Pattern)" -ForegroundColor Yellow }
}

$total = $allFiles.Count
Write-Host "$total Dateien zum Retry" -ForegroundColor Cyan

foreach ($full in $allFiles) {
    $i++
    $name = [System.IO.Path]::GetFileName($full)
    Write-Host ""
    Write-Host "[$i/$total] $name" -ForegroundColor Cyan
    Write-Host ('=' * 60) -ForegroundColor DarkGray
    Set-Location $wikiRoot
    uv run "$wikiRoot\ingest.py" $full
    if ($LASTEXITCODE -ne 0) {
        $errors += $name
        Write-Host "FEHLER" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host ('=' * 60)
Write-Host "Fertig: $($total - $errors.Count)/$total erfolgreich"
if ($errors.Count -gt 0) {
    Write-Host "Fehlgeschlagen:" -ForegroundColor Yellow
    foreach ($e in $errors) { Write-Host "  - $e" -ForegroundColor Yellow }
}
