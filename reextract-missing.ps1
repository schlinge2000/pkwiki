# Re-Extraktion von Prasentationen mit vielen leeren Bildbeschreibungen
$wikiRoot  = $PSScriptRoot
$slidesDir = Join-Path $wikiRoot "raw\slides"
$cacheDir  = Join-Path $wikiRoot "raw\.cache\slides"

$targets = @(
    "BewertungSaisonalerVerfahren.pptx",
    "Berechnugslauf.pptx",
    "Sprache_vs_Wirtschaftprozesse_englisch.pptx",
    "Weiling_Tagesprognose Demand AI.pptx"
)

foreach ($name in $targets) {
    $src   = Join-Path $slidesDir $name
    $cache = Join-Path $cacheDir ([System.IO.Path]::GetFileNameWithoutExtension($name) + ".md")

    if (-not (Test-Path $src)) {
        Write-Host "NICHT GEFUNDEN: $name" -ForegroundColor Yellow
        continue
    }

    Remove-Item $cache -Force -ErrorAction SilentlyContinue
    Write-Host ""
    Write-Host "Re-extrahiere: $name" -ForegroundColor Cyan
    Set-Location $wikiRoot
    uv run "$wikiRoot\extract.py" $src
}

Write-Host ""
Write-Host "Fertig - suche nach Reh..." -ForegroundColor Green
Select-String -Path (Join-Path $cacheDir "*.md") -Pattern "Reh|Hirsch|Rehkitz|deer" -CaseSensitive:$false |
    ForEach-Object { Write-Host "  TREFFER: $($_.Filename) Zeile $($_.LineNumber): $($_.Line.Trim())" -ForegroundColor Green }
