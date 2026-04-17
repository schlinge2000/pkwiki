---
title: Forecast Accuracy Metrics
type: concept
domain: ai
sources: [raw/pdfs/foresight.pdf]
related: ["[[intermittent-demand]]", "[[mean-absolute-scaled-error-mase]]", "[[mape]]", "[[smape]]", "[[relative-error-metrics]]", "[[scale-dependent-error-metrics]]", "[[demand-forecasting]]"]
confidence: medium
last_updated: 2026-04-17
---

Forecast Accuracy Metrics sind Kennzahlen zur Bewertung der Qualität von Prognosemodellen im [[demand-forecasting]]. Sie messen den Unterschied zwischen tatsächlichen Werten und vorhergesagten Werten.

Der Forecast-Fehler wird typischerweise definiert als:

Fehler: e_t = Y_t − F_t

wobei Y_t der tatsächliche Wert und F_t die Prognose ist.

## Hauptkategorien

Der Artikel von [[rob-j-hyndman]] unterscheidet vier zentrale Klassen von Fehlermaßen:

### 1. [[scale-dependent-error-metrics]]
Fehlermaße, die auf derselben Skala wie die Daten liegen.

Beispiele:

- MAE (Mean Absolute Error)
- MSE (Mean Squared Error)

Problem: Ergebnisse sind nicht zwischen unterschiedlichen Zeitreihen vergleichbar.

### 2. Percentage Errors
Fehler relativ zum tatsächlichen Wert.

Beispiele:

- [[mape]]
- [[smape]]

Problem: Division durch Null bei Daten mit Nullwerten.

### 3. [[relative-error-metrics]]
Fehler relativ zu einem Benchmark-Modell (z.B. Naïve Forecast).

Problem: Division durch Null möglich, wenn Benchmark-Fehler sehr klein sind.

### 4. Scale-free Metrics
Fehler werden relativ zu einer Referenzskala ausgedrückt.

Wichtiges Beispiel:

- [[mean-absolute-scaled-error-mase]]

Diese Klasse ermöglicht Vergleiche zwischen verschiedenen Zeitreihen und Forecasting-Methoden.
