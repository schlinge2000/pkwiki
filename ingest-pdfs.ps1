# Batch-Ingest relevanter PDFs
# Usage: powershell -ExecutionPolicy Bypass -File .\ingest-pdfs.ps1

$wikiRoot = $PSScriptRoot
$pdfsDir  = Join-Path $wikiRoot "raw\pdfs"

$relevant = @(
    "demand ai.pdf",
    "datenlizenzvertrag_draft.pdf",
    "foresight.pdf",
    "Medium.pdf",
    "MAAPE_ScienceDirectPaper.pdf",
    "Pilotprojekt AI-gestützte Softwareentwicklung - Abschlussbericht.pdf",
    "Time-MoE_ The Latest Foundation Forecasting Model _ by Marco Peixeiro _ Oct, 2024 _ Towards Data Science.pdf",
    "PatchTST_ A Breakthrough in Time Series Forecasting _ by Marco Peixeiro _ Towards Data Science.pdf",
    "Influential Time-Series Forecasting Papers of 2023-2024_ Part 1 _ by Nikos Kafritsas _ TDS Archive _ Medium.pdf",
    "Influential Time-Series Forecasting Papers of 2023-2024_ Part 2 _ by Nikos Kafritsas _ The Forecaster _ Mar, 2025 _ Medium.pdf",
    "LLMs for Time Series Forecasting. Time series analysis is used for… _ by Kyle Jones _ Mar, 2025 _ Medium.pdf",
    "LLMs_SCM_Optim 1 1.pdf",
    "SOFTS_ The Latest Innovation in Time Series Forecasting _ by Marco Peixeiro _ Towards Data Science.pdf",
    "Conformal Prediction in Time Series Methods and Interpretability.pdf",
    "Forecast Error Measures Intermittent Demand by Manu Joseph Towards Data Science.pdf",
    "doku.pdf",
    "INF_CORPORATE AI WORDING-7_1 1.pdf",
    "CS01_DE_Sie_key_learnings_summary_new.pdf",
    "Interview_Zusammenfassung_Jungheinrich.pdf",
    "Report_Forecast_Maschinenauslastung.pdf",
    "151225_ Software as a Service-Vertrag_Prognoseservice.pdf",
    "Leistungsbeschreibung BO 2024.pdf",
    "ADDONE Bestandsoptimierung DE 2512.pdf",
    "2409.17515v3.pdf"
)

$total   = $relevant.Count
$current = 0
$errors  = @()

foreach ($name in $relevant) {
    $current++
    $filePath = Join-Path $pdfsDir $name

    if (-not (Test-Path $filePath)) {
        Write-Host "[$current/$total] NICHT GEFUNDEN: $name" -ForegroundColor Yellow
        $errors += $name
        continue
    }

    Write-Host ""
    Write-Host "[$current/$total] $name" -ForegroundColor Cyan
    Write-Host ("-" * 60) -ForegroundColor DarkGray

    Set-Location $wikiRoot
    uv run "$wikiRoot\ingest.py" $filePath

    if ($LASTEXITCODE -ne 0) {
        Write-Host "FEHLER bei: $name" -ForegroundColor Red
        $errors += $name
    }
}

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Green
Write-Host "Batch abgeschlossen: $total PDFs verarbeitet" -ForegroundColor Green
if ($errors.Count -gt 0) {
    Write-Host "Fehler bei $($errors.Count) Dateien:" -ForegroundColor Yellow
    $errors | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
}
