---
title: Patching in Time Series
type: concept
domain: ai
sources: [raw/pdfs/PatchTST_ A Breakthrough in Time Series Forecasting _ by Marco Peixeiro _ Towards Data Science.pdf]
related: ["[[patchtst]]", "[[transformer-time-series-forecasting]]"]
confidence: medium
last_updated: 2026-04-17
---

**Patching** bezeichnet eine Technik zur Verarbeitung von Zeitreihen in Transformer-Modellen. Dabei wird eine lange Zeitreihe in **kleinere Teilsequenzen (Patches)** zerlegt.

Jeder Patch besteht aus mehreren aufeinanderfolgenden Zeitpunkten. Diese Patch-Segmente werden anschließend als **Tokens** in den Transformer eingespeist.

Wichtige Parameter:

- **Patch length (P)** – Anzahl der Zeitpunkte pro Patch
- **Stride (S)** – Abstand zwischen Startpunkten aufeinanderfolgender Patches

Patches können sich überlappen (S < P) oder disjunkt sein (S = P).

Beispiel:

Eine Zeitreihe mit Länge 15 kann bei Patch-Länge 5 und Stride 5 in drei Patches zerlegt werden.

Vorteile des Patch-Ansatzes:

- Erfassung **lokaler zeitlicher Muster** statt einzelner Zeitpunkte
- **Reduktion der Token-Anzahl** für den Transformer
- geringere **Zeit- und Speicherkomplexität**
- Möglichkeit, **längere Inputsequenzen** zu verwenden

Diese Technik ist ein zentraler Bestandteil des Modells [[patchtst]].
