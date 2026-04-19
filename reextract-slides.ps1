# Re-Extraktion aller Slides mit Vision-API
# Sucht nach Bildinhalten (z.B. Reh) und erstellt reichhaltigere Extrakte

$wikiRoot  = $PSScriptRoot
$slidesDir = Join-Path $wikiRoot "raw\slides"

$slides = Get-ChildItem $slidesDir -Filter "*.pptx" | Sort-Object Name
$total  = $slides.Count
$i      = 0
$rehFound = @()

foreach ($slide in $slides) {
    $i++
    Write-Host ""
    Write-Host "[$i/$total] $($slide.Name)" -ForegroundColor Cyan
    Set-Location $wikiRoot
    uv run "$wikiRoot\extract.py" $slide.FullName

    # Direkt nach Reh/Hirsch/Tier suchen im frischen Extrakt
    $cacheFile = Join-Path $wikiRoot "raw\.cache\slides\$($slide.BaseName).md"
    if (Test-Path $cacheFile) {
        $matches = Select-String -Path $cacheFile -Pattern "\bReh\b|Hirsch|Reh |Deer|Rehkitz" -CaseSensitive:$false
        if ($matches) {
            Write-Host "  *** REH GEFUNDEN in: $($slide.Name) ***" -ForegroundColor Green
            $matches | ForEach-Object { Write-Host "  -> $($_.Line.Trim())" -ForegroundColor Yellow }
            $rehFound += $slide.Name
        }
    }
}

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Green
Write-Host "Re-Extraktion abgeschlossen: $total Praesentationen"
if ($rehFound.Count -gt 0) {
    Write-Host "Reh gefunden in:" -ForegroundColor Green
    $rehFound | ForEach-Object { Write-Host "  - $_" -ForegroundColor Green }
} else {
    Write-Host "Kein Reh-Bild im Text gefunden (evtl. Bildbeschreibung anders formuliert)" -ForegroundColor Yellow
}
