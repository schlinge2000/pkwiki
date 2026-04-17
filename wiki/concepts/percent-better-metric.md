---
title: Percent Better Metric
type: concept
domain: ai
sources: [raw/pdfs/Forecast Error Measures Intermittent Demand by Manu Joseph Towards Data Science.pdf]
related: ["[[forecast-accuracy-metrics]]", "[[intermittent-demand]]"]
confidence: medium
last_updated: 2026-04-17
---

Die **Percent Better Metric** vergleicht zwei Forecast-Methoden, indem sie zählt, in wie vielen Perioden eine Methode einen geringeren Fehler erzielt als die andere.

Beispiele sind:

- PBMAE
- PBRMSE

Eigenschaften:

- misst **nicht die Größe der Fehler**, sondern deren Häufigkeit
- robust gegenüber numerischen Instabilitäten
- funktioniert auch bei Zeitreihen mit vielen Nullwerten

Dadurch eignet sich die Metrik besonders für [[intermittent-demand]], bei der klassische prozentuale Fehlermetriken häufig instabil werden.

Der Nachteil besteht darin, dass große und kleine Fehler gleich behandelt werden, da nur gezählt wird, welche Methode besser ist.
