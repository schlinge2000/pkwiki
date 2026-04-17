---
title: N-HiTS
type: concept
domain: ai
sources: [raw/pdfs/PatchTST_ A Breakthrough in Time Series Forecasting _ by Marco Peixeiro _ Towards Data Science.pdf]
related: ["[[n-beats]]", "[[patchtst]]", "[[transformer-time-series-forecasting]]"]
confidence: medium
last_updated: 2026-04-17
---

**N-HiTS (Neural Hierarchical Interpolation for Time Series)** ist ein Deep‑Learning-Modell für Zeitreihenprognosen und gehört zur Familie der **MLP-basierten Forecasting-Modelle**.

Das Modell wurde entwickelt, um besonders gute Ergebnisse bei **Long-Horizon Forecasting** zu erzielen. Es nutzt hierarchische Interpolationsmechanismen, um Prognosen über längere Zeiträume zu generieren.

Im Artikel über [[patchtst]] wird N-HiTS zusammen mit [[n-beats]] als Vergleichsmodell eingesetzt. Beide Modelle gelten als leistungsfähige MLP-basierte Alternativen zu Transformer-Ansätzen.

In einem Beispielversuch mit dem Exchange-Datensatz zeigt PatchTST niedrigere Fehlerwerte (MAE und MSE) als N-HiTS und N-BEATS, wobei das Experiment nur ein einzelnes Dataset und einen Forecast-Horizont betrachtet.
