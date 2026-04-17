---
title: Another Look at Forecast-Accuracy Metrics for Intermittent Demand
type: source
source_file: raw/pdfs/foresight.pdf
source_type: paper
date: 2006-06-01
key_concepts: ["[[forecast-accuracy-metrics]]", "[[intermittent-demand]]", "[[mean-absolute-scaled-error-mase]]", "[[mape]]", "[[smape]]", "[[relative-error-metrics]]", "[[scale-dependent-error-metrics]]"]
last_updated: 2026-04-17
---

Der Artikel von [[rob-j-hyndman]] diskutiert Probleme klassischer Kennzahlen zur Bewertung von Prognosegenauigkeit bei [[intermittent-demand]]. Viele verbreitete Metriken erzeugen bei solchen Daten **unendliche oder undefinierte Werte**, insbesondere wenn Zeitreihen häufig Nullen enthalten.

Zentrale These des Artikels ist die Einführung der Kennzahl [[mean-absolute-scaled-error-mase]] als robustere Alternative zur Bewertung von Prognosemodellen.

## Zentrale Punkte

- Klassische Forecast-Accuracy-Metriken funktionieren schlecht bei Zeitreihen mit vielen Nullwerten.
- Besonders betroffen sind Ersatzteil‑ oder Reparaturteilnachfragen mit sporadischen Bestellungen.
- Viele etablierte Metriken (z.B. [[mape]] oder relative Fehlerkennzahlen) erzeugen Divisionen durch Null.
- [[mean-absolute-scaled-error-mase]] vermeidet dieses Problem durch Skalierung anhand des In-Sample-Fehlers eines Naïve‑Forecasts.

## Kategorien von Forecast-Accuracy-Metriken

Der Artikel unterscheidet vier Klassen:

- [[scale-dependent-error-metrics]] (z.B. MAE, MSE)
- [[mape]] und andere percentage-basierte Fehler
- [[relative-error-metrics]] (Vergleich mit Benchmark‑Modell)
- scale‑free Metriken wie [[mean-absolute-scaled-error-mase]]

## Drei typische Evaluationssituationen

Forecast-Genauigkeit wird häufig in drei Szenarien bewertet:

1. Prognosen aus einem festen Ursprung für mehrere Forecast-Horizonte
2. Rolling-Origin Evaluation mit konstantem Horizont
3. Vergleich von Prognosemethoden über viele parallele Zeitreihen

Eine universelle Accuracy-Metrik sollte in allen drei Szenarien funktionieren.

## Hauptargument

Viele verbreitete Kennzahlen scheitern bei intermittierender Nachfrage:

- [[mape]] kann bei Nullwerten unendlich werden.
- Relative Fehler können Division durch Null erzeugen.
- Geometrische Fehlermaße können zu Null kollabieren.

Die vorgeschlagene Lösung ist [[mean-absolute-scaled-error-mase]], die Forecast-Fehler relativ zur durchschnittlichen Ein-Schritt-Naïve-Prognose skaliert.

## Fazit

Der Autor argumentiert, dass [[mean-absolute-scaled-error-mase]] eine **universell einsetzbare Kennzahl zur Prognosebewertung** ist, insbesondere für [[intermittent-demand]] und für Vergleiche zwischen mehreren Zeitreihen.
