# Re-Extraktion aller Slides mit Vision-Fehlern im Cache
$wikiRoot  = $PSScriptRoot
$slidesDir = Join-Path $wikiRoot "raw\slides"
$cacheDir  = Join-Path $wikiRoot "raw\.cache\slides"

$failed = Get-ChildItem $cacheDir -Filter "*.md" |
    Where-Object { (Get-Content $_.FullName -Raw) -match "Vision-Fehler" } |
    Select-Object -ExpandProperty BaseName

Write-Host "$($failed.Count) Praesentationen mit Vision-Fehlern gefunden" -ForegroundColor Yellow

foreach ($name in $failed) {
    $src = Get-ChildItem $slidesDir | Where-Object { $_.BaseName -eq $name } | Select-Object -First 1
    if (-not $src) {
        Write-Host "NICHT GEFUNDEN: $name" -ForegroundColor Red
        continue
    }
    # Cache loeschen
    Remove-Item (Join-Path $cacheDir "$name.md") -Force -ErrorAction SilentlyContinue
    Write-Host ""
    Write-Host "Re-extrahiere: $($src.Name)" -ForegroundColor Cyan
    Set-Location $wikiRoot
    uv run "$wikiRoot\extract.py" $src.FullName
}

Write-Host ""
Write-Host "Fertig." -ForegroundColor Green
