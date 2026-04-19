# Nachholung der fehlgeschlagenen PDFs
$wikiRoot = $PSScriptRoot
$pdfsDir  = Join-Path $wikiRoot "raw\pdfs"

$files = Get-ChildItem $pdfsDir | Where-Object {
    $_.Name -like "*Pilotprojekt*" -or
    $_.Name -like "*Influential*" -or
    $_.Name -like "*LLMs for Time*" -or
    $_.Name -like "*Time-MoE*"
}

$total = $files.Count
$i = 0

foreach ($file in $files) {
    $i++
    Write-Host ""
    Write-Host "[$i/$total] $($file.Name)" -ForegroundColor Cyan
    Write-Host ("-" * 60) -ForegroundColor DarkGray
    Set-Location $wikiRoot
    uv run "$wikiRoot\ingest.py" $file.FullName
}

Write-Host ""
Write-Host "Fertig." -ForegroundColor Green
