---
title: STAD Module (Star Aggregate-Dispatch)
type: concept
domain: ai
sources: [raw/pdfs/SOFTS_ The Latest Innovation in Time Series Forecasting _ by Marco Peixeiro _ Towards Data Science.pdf]
related: ["[[softs-model]]", "[[series-core-fusion]]", "[[multivariate-long-horizon-forecasting]]"]
confidence: medium
last_updated: 2026-04-17
---

Das **STAD‑Modul (STar Aggregate‑Dispatch)** ist die zentrale Komponente des [[softs-model]]. Es ermöglicht das Lernen von **Interaktionen zwischen mehreren Zeitreihen**.

### Grundidee

Statt wie bei Transformer‑Modellen direkte Attention zwischen allen Serien zu berechnen, nutzt STAD eine **zentralisierte Repräsentation (Core)**.

Der Ablauf besteht aus mehreren Schritten:

1. Jede eingebettete Zeitreihe wird durch eine **MLP‑Schicht und Pooling** verarbeitet.
2. Die resultierenden Repräsentationen werden **zusammengeführt (Aggregation)** und bilden den sogenannten **Core**.
3. Der Core wird anschließend **wieder an jede Zeitreihe verteilt (Dispatch)**.
4. Die Core‑Information wird mit den ursprünglichen Serien‑Features **fusioniert**.

Residualverbindungen sorgen dafür, dass Informationen, die im Aggregationsschritt verloren gehen könnten, erhalten bleiben.

### Komplexität

Ein wichtiger Vorteil ist die **lineare Komplexität** des STAD‑Moduls.

Zum Vergleich:

- Attention‑Mechanismen: quadratische Komplexität
- STAD: lineare Komplexität

Dadurch kann das Modell **große multivariate Datensätze mit vielen Serien effizienter verarbeiten**.

### Rolle im Modell

Das STAD‑Modul implementiert die Kernidee der [[series-core-fusion]] und ersetzt klassische Attention‑Mechanismen zur Modellierung von Serieninteraktionen.
