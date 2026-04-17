---
title: N-BEATS
type: concept
domain: ai
sources: [raw/pdfs/PatchTST_ A Breakthrough in Time Series Forecasting _ by Marco Peixeiro _ Towards Data Science.pdf]
related: ["[[n-hits]]", "[[patchtst]]", "[[transformer-time-series-forecasting]]"]
confidence: medium
last_updated: 2026-04-17
---

**N-BEATS** ist ein Deep-Learning-Modell für Zeitreihenprognosen, das auf **Multilayer Perceptrons (MLPs)** basiert.

Das Modell wurde entwickelt, um hohe Prognosegenauigkeit ohne komplexe rekurrente oder attention-basierte Strukturen zu erreichen. In vielen Benchmark-Studien hat N-BEATS sehr gute Ergebnisse bei **Long-Horizon Forecasting** erzielt.

Im Kontext des Artikels über [[patchtst]] wird N-BEATS als Referenzmodell verwendet, um Transformer-basierte Ansätze mit leistungsfähigen MLP-Modellen zu vergleichen.

In einem Beispiel-Experiment mit Wechselkursdaten wird N-BEATS gemeinsam mit [[n-hits]] und PatchTST trainiert und anhand von Fehlermaßen wie MAE und MSE bewertet.
