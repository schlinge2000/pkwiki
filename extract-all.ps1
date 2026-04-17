# Extrahiert alle PPTX/DOCX/PDF in raw/ nach Markdown
$wikiRoot = $PSScriptRoot
$rawPath = Join-Path $wikiRoot "raw"

$files = Get-ChildItem -Path $rawPath -Recurse -Include "*.pptx","*.docx","*.pdf"

Write-Host "$($files.Count) Dateien gefunden.`n" -ForegroundColor Cyan

foreach ($file in $files) {
    $rel = $file.FullName.Substring($wikiRoot.Length + 1)
    $md = [System.IO.Path]::ChangeExtension($file.FullName, ".md")

    if (Test-Path $md) {
        Write-Host "[SKIP] $($file.Name) (bereits extrahiert)" -ForegroundColor DarkGray
        continue
    }

    Write-Host "[EXTRACT] $($file.Name)" -ForegroundColor Yellow
    uv run "$wikiRoot\extract.py" $file.FullName
}

Write-Host "`nFertig." -ForegroundColor Green
