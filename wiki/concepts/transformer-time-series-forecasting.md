---
title: Transformer-basierte Zeitreihenprognose
type: concept
domain: ai
sources: [raw/pdfs/PatchTST_ A Breakthrough in Time Series Forecasting _ by Marco Peixeiro _ Towards Data Science.pdf]
related: ["[[patchtst]]", "[[patching-time-series]]", "[[n-beats]]", "[[n-hits]]"]
confidence: medium
last_updated: 2026-04-17
---

**Transformer-basierte Modelle für Zeitreihenprognosen** übertragen die Architektur des Transformer-Netzwerks, das ursprünglich für Natural Language Processing entwickelt wurde, auf Zeitreihendaten.

Transformer nutzen den **Attention-Mechanismus**, um Beziehungen zwischen Elementen einer Sequenz zu modellieren. In NLP entspricht dies Beziehungen zwischen Wörtern in einem Satz.

Bei Zeitreihen bedeutet dies, dass ein Modell lernen kann, **Zusammenhänge zwischen vergangenen und zukünftigen Zeitpunkten** zu erkennen.

Frühe Transformer-Ansätze für Zeitreihen arbeiteten häufig mit **point-wise attention**, bei der jeder Zeitpunkt einzeln betrachtet wird. Dies kann problematisch sein, weil lokale Kontextinformationen fehlen.

Neuere Ansätze wie [[patchtst]] versuchen dieses Problem zu lösen, indem sie:

- Zeitpunkte zu **Patches** zusammenfassen
- längere Kontextfenster verwenden
- effizientere Sequenzrepräsentationen erzeugen

Transformer-basierte Modelle konkurrieren im Bereich Forecasting mit leistungsfähigen **MLP-basierten Architekturen** wie [[n-beats]] und [[n-hits]].
