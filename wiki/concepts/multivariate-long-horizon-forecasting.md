---
title: Multivariate Long-Horizon Forecasting
type: concept
domain: ai
sources: [raw/pdfs/SOFTS_ The Latest Innovation in Time Series Forecasting _ by Marco Peixeiro _ Towards Data Science.pdf]
related: ["[[softs-model]]", "[[stad-module]]", "[[patchtst]]", "[[itransformer]]"]
confidence: medium
last_updated: 2026-04-17
---

**Multivariate Long‑Horizon Forecasting** bezeichnet die Vorhersage mehrerer miteinander verbundener Zeitreihen über einen **langen Prognosehorizont**.

Diese Art von Forecasting ist besonders wichtig für **Entscheidungsunterstützung in operativen Systemen**, etwa:

- Energie‑ und Infrastrukturmonitoring
- Supply‑Chain‑Planung
- Nachfrageprognosen

### Herausforderungen

Die Aufgabe ist aus mehreren Gründen schwierig:

- viele **interagierende Zeitreihen**
- komplexe **zeitliche Abhängigkeiten**
- zunehmende **Modellkomplexität** bei klassischen Attention‑Mechanismen.

Modelle wie [[patchtst]] reduzieren Komplexität teilweise durch **Channel Independence**, behandeln Serien aber häufig getrennt.

Der Ansatz des [[softs-model]] versucht stattdessen, Interaktionen effizient über eine zentrale Repräsentation ([[series-core-fusion]]) zu modellieren.
