---
title: Adaptive Conformal Inference (ACI)
type: concept
domain: ai
sources: [raw/pdfs/Conformal Prediction in Time Series Methods and Interpretability.pdf]
related: ["[[conformal-prediction]]", "[[conformal-prediction-time-series]]"]
confidence: medium
last_updated: 2026-04-17
---

**Adaptive Conformal Inference (ACI)** ist eine Weiterentwicklung von Conformal Prediction für dynamische Datenumgebungen, insbesondere für Zeitreihen.

Das Framework wurde unter anderem von Gibbs und Candès (2021) vorgeschlagen.

## Grundidee

Bei klassischen Conformal‑Methoden bleibt das Konfidenzniveau während der Vorhersage konstant. In realen Zeitreihen ändern sich jedoch Datenverteilungen häufig.

ACI passt die Größe der Prediction Sets dynamisch an.

Dies geschieht durch:

- kontinuierliche Bewertung von Non‑Conformity Scores
- Anpassung eines Konfidenzparameters über die Zeit

## Vorteile

Adaptive Verfahren ermöglichen:

- bessere Kalibrierung von Vorhersageintervallen
- robustere Performance bei **Distribution Shifts**
- Anwendung auf sequenziell eintreffende Daten

Damit eignet sich ACI besonders für:

- Finanzmärkte
- Energieverbrauchsprognosen
- operative Forecasting‑Systeme
