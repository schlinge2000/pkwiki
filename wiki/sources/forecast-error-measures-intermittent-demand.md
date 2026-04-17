---
title: Forecast Error Measures: Intermittent Demand
type: source
source_file: raw/pdfs/Forecast Error Measures Intermittent Demand by Manu Joseph Towards Data Science.pdf
source_type: article
date: 2020-10-07
key_concepts: ["[[intermittent-demand]]", "[[syntetos-boylan-demand-classification]]", "[[periods-in-stock-pis]]", "[[stock-keeping-oriented-prediction-error-costs-spec]]", "[[cumulative-forecast-error-cfe]]", "[[mean-arctangent-absolute-percentage-error-maape]]"]
last_updated: 2026-04-17
---

Der Artikel analysiert Forecast-Fehlermetriken speziell für **intermittierende und lumpy Nachfrage**, also Zeitreihen mit vielen Nullperioden. Viele klassische Forecast-Metriken wurden für glatte Zeitreihen entwickelt und verhalten sich bei solchen Daten instabil oder führen zu systematisch falschen Modellbewertungen.

Ein zentraler Ausgangspunkt ist die **Syntetos–Boylan-Klassifikation**, welche Zeitreihen anhand von zwei Kennzahlen kategorisiert:

- [[average-demand-interval-adi]] — durchschnittlicher Abstand zwischen zwei positiven Nachfragewerten
- [[coefficient-of-variation-squared-demand]] — Variabilität der Nachfrage

Mit den Grenzwerten ADI = 1.32 und COV² = 0.49 entstehen vier Kategorien:

- Smooth
- Erratic
- Intermittent
- Lumpy

Der Artikel argumentiert, dass klassische Metriken wie [[mape]], [[smape]], [[mean-absolute-scaled-error-mase]] oder [[relative-error-metrics]] bei intermittenter Nachfrage problematisch sind. Grund ist vor allem die große Anzahl von **Nullnachfragen**, die zu Division durch Null oder instabilen Skalierungen führen.

Experimente mit einem Retail-Datensatz aus dem UCI Machine Learning Repository zeigen zudem, dass viele dieser Metriken **Zero Forecast** als bestes Modell bewerten würden — obwohl dies in der Praxis zu massiven Stockouts führen würde.

Der Autor empfiehlt stattdessen mehrere **Supply-Chain-orientierte Fehlermetriken**:

- [[cumulative-forecast-error-cfe]] zur Messung von Forecast-Bias
- [[number-of-shortages-nosp]] zur Erkennung systematischer Unterprognosen
- [[periods-in-stock-pis]] zur Bewertung von Lagerhaltungsfolgen
- [[stock-keeping-oriented-prediction-error-costs-spec]] zur direkten Abbildung von Opportunitäts- und Lagerkosten
- [[percent-better-metric]] als robustes Vergleichsmaß

Zusätzlich wird [[mean-arctangent-absolute-percentage-error-maape]] als stabilere Alternative zu MAPE vorgestellt.

Die Analyse zeigt zwei Gruppen von Forecast-Metriken:

1. **Accuracy-orientierte Metriken** (z. B. MAE, MASE, RelRMSE)
2. **Bias- und Inventory-orientierte Metriken** (z. B. CFE, PIS, SPEC)

Keine einzelne Metrik liefert ein vollständiges Bild. Für intermittierende Nachfrage wird daher empfohlen, **mehrere komplementäre Metriken gleichzeitig zu verwenden**.
