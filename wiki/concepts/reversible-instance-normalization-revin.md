---
title: Reversible Instance Normalization (RevIN)
type: concept
domain: ai
sources: [raw/pdfs/SOFTS_ The Latest Innovation in Time Series Forecasting _ by Marco Peixeiro _ Towards Data Science.pdf]
related: ["[[softs-model]]", "[[multivariate-long-horizon-forecasting]]"]
confidence: medium
last_updated: 2026-04-17
---

**Reversible Instance Normalization (RevIN)** ist eine Normalisierungstechnik für Zeitreihenmodelle.

Sie wird im [[softs-model]] als erster Verarbeitungsschritt eingesetzt.

### Funktionsweise

RevIN transformiert Eingabedaten so, dass sie:

- um **Null zentriert** werden
- eine **Varianz von eins** besitzen.

Diese Normalisierung stabilisiert das Training von Deep‑Learning‑Modellen auf Zeitreihen.

Der Begriff *reversible* bedeutet, dass die Transformation nach der Modellvorhersage wieder **rückgängig gemacht werden kann**, sodass die Prognosen wieder in der ursprünglichen Skala vorliegen.

### Nutzen

- stabileres Training
- bessere Modellkonvergenz
- robustere Prognosen bei unterschiedlichen Datenverteilungen.
