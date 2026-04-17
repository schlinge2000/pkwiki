---
title: Series-Core Fusion
type: concept
domain: ai
sources: [raw/pdfs/SOFTS_ The Latest Innovation in Time Series Forecasting _ by Marco Peixeiro _ Towards Data Science.pdf]
related: ["[[softs-model]]", "[[stad-module]]", "[[multivariate-long-horizon-forecasting]]"]
confidence: medium
last_updated: 2026-04-17
---

**Series‑Core Fusion** ist das zentrale Architekturprinzip des [[softs-model]].

Die Idee besteht darin, Informationen aus mehreren Zeitreihen zunächst **in einer zentralen Repräsentation (Core)** zu bündeln und diese anschließend wieder **auf die einzelnen Serien zurückzuverteilen**.

### Ablauf

1. Jede Zeitreihe wird zunächst separat **embedded**.
2. Die Repräsentationen werden im [[stad-module]] **aggregiert**, wodurch ein gemeinsamer Core entsteht.
3. Der Core wird anschließend **für jede Serie repliziert** und mit deren ursprünglicher Repräsentation kombiniert.
4. Eine weitere MLP‑Schicht führt die **Fusion der Informationen** durch.

### Ziel

Durch dieses Verfahren können Modelle:

- **Interaktionen zwischen Zeitreihen lernen**
- gemeinsame Muster über mehrere Serien hinweg erfassen
- gleichzeitig eine **effiziente Modellstruktur** beibehalten.

Series‑Core Fusion ist damit eine Alternative zu Attention‑Mechanismen, die typischerweise in [[transformer-time-series-forecasting]] eingesetzt werden.
