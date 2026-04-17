---
title: Periods in Stock (PIS)
type: concept
domain: ai
sources: [raw/pdfs/Forecast Error Measures Intermittent Demand by Manu Joseph Towards Data Science.pdf]
related: ["[[cumulative-forecast-error-cfe]]", "[[intermittent-demand]]", "[[inventory-optimization-ai]]"]
confidence: medium
last_updated: 2026-04-17
---

**Periods in Stock (PIS)** ist eine Fehlermetrik für Forecasts, die speziell auf **Lagerhaltungsfolgen von Prognosen** abzielt.

Die Metrik misst, wie lange prognostizierte Artikel im Lager verbleiben oder wie lange Stockouts auftreten.

Grundidee:

- Prognosen erzeugen implizite Lagerbestände
- Nachfrage reduziert diese Bestände
- PIS summiert über die Zeit, wie viele Perioden Einheiten im Lager verbleiben

Beispiel:

Wenn täglich ein Artikel prognostiziert wird, aber mehrere Tage keine Nachfrage auftritt, akkumuliert sich ein Lagerbestand. Jede Einheit trägt für jede Periode im Lager zu PIS bei.

Interpretation:

- **positiver PIS** → Überprognose und Lageraufbau
- **negativer PIS** → Unterprognose und Stockouts

Mathematisch entspricht PIS der **kumulativen Summe des CFE**, also der Fläche unter der CFE-Kurve.

Die Metrik eignet sich besonders für [[intermittent-demand]], da sie explizit die Auswirkungen von Prognosefehlern auf **Inventar und Service-Level** berücksichtigt.
