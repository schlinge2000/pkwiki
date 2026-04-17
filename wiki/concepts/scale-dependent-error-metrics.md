---
title: Scale-Dependent Error Metrics
type: concept
domain: ai
sources: [raw/pdfs/foresight.pdf]
related: ["[[forecast-accuracy-metrics]]", "[[mean-absolute-scaled-error-mase]]"]
confidence: medium
last_updated: 2026-04-17
---

Scale-Dependent Error Metrics sind Prognosekennzahlen, deren Werte auf derselben Skala wie die zugrunde liegenden Daten liegen.

Der Forecast-Fehler wird dabei direkt aus der Differenz zwischen tatsächlichem Wert und Prognose berechnet:

Fehler: e_t = Y_t − F_t

Typische Beispiele:

- MAE (Mean Absolute Error)
- MAD (Mean Absolute Deviation)
- MSE (Mean Squared Error)

## Eigenschaften

- leicht interpretierbar
- direkt aus den Prognosefehlern berechnet

## Einschränkungen

Diese Kennzahlen sind **nicht zwischen verschiedenen Zeitreihen vergleichbar**, da sie von der Skala der Daten abhängen. Ein Fehler von 10 Einheiten kann für eine Zeitreihe groß und für eine andere trivial sein.

Daher sind sie ungeeignet, wenn Prognosemethoden über mehrere Produkte oder Datensätze hinweg verglichen werden sollen.

In solchen Fällen werden skalenfreie Kennzahlen wie [[mean-absolute-scaled-error-mase]] bevorzugt.
