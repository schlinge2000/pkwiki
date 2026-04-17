---
title: Self-Supervised Representation Learning für Zeitreihen
type: concept
domain: ai
sources: [raw/pdfs/PatchTST_ A Breakthrough in Time Series Forecasting _ by Marco Peixeiro _ Towards Data Science.pdf]
related: ["[[patchtst]]", "[[patching-time-series]]"]
confidence: medium
last_updated: 2026-04-17
---

**Self-Supervised Representation Learning** ist eine Trainingsstrategie, bei der ein Modell ohne explizite Labels aus den Daten selbst Lernsignale erzeugt.

Im Kontext von [[patchtst]] wird dazu ein **Masking-Verfahren** verwendet:

- Zufällige Patches einer Zeitreihe werden maskiert (z. B. auf 0 gesetzt).
- Das Modell wird trainiert, die ursprünglichen Werte dieser Patches zu rekonstruieren.

Dieser Ansatz zwingt das Modell dazu, **abstrakte Repräsentationen der Zeitreihe** zu lernen, die strukturelle Muster und Zusammenhänge enthalten.

Die Autoren schlagen vor, dass diese Repräsentationen anschließend für Forecasting-Aufgaben genutzt werden können und so die Prognoseleistung verbessern.
