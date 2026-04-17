---
title: Absolute Percentage Error (APE)
type: concept
domain: ai
sources: [raw/pdfs/MAAPE_ScienceDirectPaper.pdf]
related: ["[[mape]]", "[[mean-arctangent-absolute-percentage-error-maape]]", "[[forecast-accuracy-metrics]]"]
confidence: medium
last_updated: 2026-04-17
---

Der **Absolute Percentage Error (APE)** ist die elementare Fehlerkomponente der Metrik [[mape]].

Für eine einzelne Beobachtung mit

- tatsächlichem Wert A
- Prognosewert F

wird der Fehler berechnet als

|A − F| / |A|

APE misst also den **absoluten Prognosefehler relativ zum tatsächlichen Wert**.

Eigenschaften:

- **skalierungsunabhängig** (scale‑independent)
- leicht interpretierbar als prozentualer Fehler
- Grundlage vieler Forecast‑Accuracy‑Metriken

Der **Mean Absolute Percentage Error (MAPE)** ist einfach der Durchschnitt aller APE‑Werte über eine Zeitreihe.

Problematisch ist jedoch, dass der Ausdruck eine **Division durch A** enthält. Wenn A sehr klein oder gleich Null ist, entstehen:

- extrem große Fehlerwerte
- unendliche oder undefinierte Werte

Diese Problematik tritt häufig bei [[intermittent-demand]] auf.

Das Paper zu [[mean-arctangent-absolute-percentage-error-maape]] interpretiert APE geometrisch als **Steigung eines Dreiecks** zwischen Forecast‑ und Actual‑Wert. Diese Interpretation ermöglicht die Transformation in einen Winkel (arctan), aus der MAAPE entsteht.
