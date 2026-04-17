---
title: Ensemble Batch Prediction Intervals (EnbPI)
type: concept
domain: ai
sources: [raw/pdfs/Conformal Prediction in Time Series Methods and Interpretability.pdf]
related: ["[[conformal-prediction]]", "[[conformal-prediction-time-series]]"]
confidence: medium
last_updated: 2026-04-17
---

**Ensemble Batch Prediction Intervals (EnbPI)** ist eine Methode zur Erzeugung von Vorhersageintervallen für Zeitreihen mithilfe von Conformal Prediction.

Der Ansatz wurde 2020 vorgeschlagen und adressiert ein zentrales Problem klassischer conformal Methoden: die Annahme der **Exchangeability** von Daten.

## Kernidee

EnbPI kombiniert:

- Ensemble‑Modelle
- Batch‑basierte Kalibrierung
- conformal inference

Dadurch können zuverlässige Vorhersageintervalle erzeugt werden, auch wenn Daten zeitliche Abhängigkeiten besitzen.

## Vorteile

- funktioniert besser mit Zeitreihendaten
- reduziert Probleme durch Verteilungsänderungen
- liefert stabile Prediction Intervals

Die Methode ist ein Beispiel für neuere Ansätze, die Conformal Prediction auf reale Forecasting‑Probleme anpassen.
