# Zeigt Dateien in raw/ die noch nicht ingested wurden
$rawPath   = Join-Path $PSScriptRoot "raw"
$seenFile  = Join-Path $PSScriptRoot "logs\seen-files.txt"
$extensions = @('.pptx','.docx','.pdf','.md')

$allFiles = Get-ChildItem -Path $rawPath -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $extensions -contains $_.Extension.ToLower() -and
        $_.FullName -notlike '*\.cache\*' -and
        $_.Name -notmatch '^\~\$'
    }

$seen = @{}
if (Test-Path $seenFile) {
    Get-Content $seenFile -Encoding UTF8 | ForEach-Object {
        if ($_.Trim()) { $seen[$_.Trim()] = 1 }
    }
}

$new = $allFiles | Where-Object { -not $seen.ContainsKey($_.FullName) }

Write-Host "Dateien in raw/:        $($allFiles.Count)"
Write-Host "In seen-files.txt:      $($seen.Count)"
Write-Host "Noch nicht ingested:    $($new.Count)"

if ($new.Count -gt 0) {
    Write-Host ""
    Write-Host "Nicht ingested:" -ForegroundColor Yellow
    $new | ForEach-Object { Write-Host "  $($_.Name)" -ForegroundColor Cyan }
}
