---
title: Channel-Independence in Time Series Models
type: concept
domain: ai
sources: [raw/pdfs/PatchTST_ A Breakthrough in Time Series Forecasting _ by Marco Peixeiro _ Towards Data Science.pdf]
related: ["[[patchtst]]", "[[transformer-time-series-forecasting]]"]
confidence: medium
last_updated: 2026-04-17
---

**Channel-Independence** ist ein Designprinzip für Modelle, die **multivariate Zeitreihen** verarbeiten.

Dabei wird jede einzelne Zeitreihe als **separater Kanal** betrachtet. Statt mehrere Variablen gemeinsam als einen Input zu modellieren, verarbeitet das Modell jede Serie unabhängig im Transformer.

Im Kontext von [[patchtst]] bedeutet das:

- Eine multivariate Zeitreihe wird in mehrere Einzelserien zerlegt
- Jede Serie wird separat gepatcht
- Jeder Patch wird als Token in den Transformer eingespeist
- Die Vorhersagen für alle Kanäle werden anschließend kombiniert

Dieser Ansatz reduziert Modellkomplexität und ermöglicht es dem Modell, **spezifische Muster pro Zeitreihe** zu lernen.
