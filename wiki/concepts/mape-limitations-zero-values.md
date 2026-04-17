---
title: MAPE Limitations bei Nullwerten
type: concept
domain: ai
sources: [raw/pdfs/MAAPE_ScienceDirectPaper.pdf]
related: ["[[mape]]", "[[intermittent-demand]]", "[[mean-arctangent-absolute-percentage-error-maape]]", "[[smape]]", "[[mean-absolute-scaled-error-mase]]"]
confidence: medium
last_updated: 2026-04-17
---

Eine zentrale Schwäche von [[mape]] ist das Verhalten bei **Actual‑Werten nahe Null oder gleich Null**.

Da MAPE auf dem **Absolute Percentage Error (APE)** basiert

|A − F| / |A|

führt ein kleiner oder nuller Wert von A zu:

- **unendlichen Fehlerwerten**
- **undefinierten Ergebnissen**
- extrem großen Ausreißern

Dieses Problem tritt besonders häufig bei Datensätzen mit [[intermittent-demand]] auf, beispielsweise:

- Retail‑Artikel mit seltenen Verkäufen
- Ersatzteile
- biologische oder finanzielle Zeitreihen mit vielen Nullwerten

In solchen Datensätzen können viele Perioden ohne Nachfrage auftreten. Für diese Perioden ist MAPE entweder nicht berechenbar oder dominiert die Gesamtbewertung.

In der Literatur wurden mehrere Lösungen vorgeschlagen:

- [[smape]] – modifizierter Nenner (Actual + Forecast)
- [[mean-absolute-scaled-error-mase]] – Skalierung mit Naive‑Forecast‑Fehler
- relative Error‑Maße

Das Paper zu [[mean-arctangent-absolute-percentage-error-maape]] schlägt stattdessen eine Transformation des Fehlers über die **arctan‑Funktion** vor, wodurch extreme Werte begrenzt werden.
