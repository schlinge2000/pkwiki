---
title: A new metric of absolute percentage error for intermittent demand forecasts
type: source
source_file: raw/pdfs/MAAPE_ScienceDirectPaper.pdf
source_type: paper
date: 2016-01-01
key_concepts: ["[[mean-arctangent-absolute-percentage-error-maape]]", "[[absolute-percentage-error-ape]]", "[[mape-limitations-zero-values]]", "[[outlier-robustness-maape]]", "[[forecast-metric-bias-mape-vs-maape]]"]
last_updated: 2026-04-17
---

Diese Arbeit von [[sungil-kim]] und [[heeyoung-kim]] (International Journal of Forecasting, 2016) führt eine neue Kennzahl zur Bewertung von Prognosegenauigkeit ein: **MAAPE (Mean Arctangent Absolute Percentage Error)**.

Das Ziel der Arbeit ist es, ein zentrales Problem der weit verbreiteten Metrik [[mape]] zu lösen: MAPE wird **unendlich oder undefiniert**, wenn tatsächliche Werte (Actuals) nahe Null oder gleich Null sind. Dieses Problem tritt besonders häufig bei [[intermittent-demand]] auf, z. B. bei Ersatzteilen oder unregelmäßigen Verkaufsdaten.

Die Autoren schlagen MAAPE vor, eine Transformation des klassischen **Absolute Percentage Error (APE)** mittels der **arctan‑Funktion**. Dadurch wird der Fehlerwert begrenzt und extrem große Fehler (Outlier) dominieren die Gesamtbewertung nicht mehr.

Kernideen des Papers:

- Neuinterpretation von APE als **Steigung eines Dreiecks** zwischen Forecast und Actual
- Transformation der Steigung von einem **Ratio** zu einem **Winkel (arctan)**
- dadurch begrenzter Wertebereich und robustere Fehleraggregation

Verglichene Metriken im Paper:

- [[mape]]
- [[smape]]
- [[mean-absolute-scaled-error-mase]]
- MAE/Mean Ratio

Die Autoren evaluieren MAAPE anhand:

- theoretischer Eigenschaften
- Simulationen
- realer Retail‑ und Verkaufsdaten

Zentrale Ergebnisse:

- MAAPE vermeidet **Division‑by‑zero‑Probleme** von MAPE
- MAAPE ist **robuster gegenüber Ausreißern**
- MAAPE erzeugt **weniger verzerrte Prognoseentscheidungen** als MAPE

Eine Einschränkung bleibt: Wenn extreme Fehler tatsächlich wichtige Business‑Signale darstellen (statt Messfehler), kann die Begrenzung durch MAAPE diese Informationen abschwächen.

Die Arbeit positioniert MAAPE als besonders geeignet für Datensätze mit:

- häufigen Nullwerten
- [[intermittent-demand]]
- stark schwankenden Forecast‑Fehlern
