---
title: Intermittent Demand
type: concept
domain: business
sources: [raw/pdfs/foresight.pdf]
related: ["[[forecast-accuracy-metrics]]", "[[mean-absolute-scaled-error-mase]]", "[[croston-method]]", "[[demand-forecasting]]"]
confidence: medium
last_updated: 2026-04-17
---

Intermittent Demand bezeichnet Nachfragezeitreihen, bei denen **Nachfrage unregelmäßig auftritt und häufig Nullwerte enthalten sind**. Solche Muster treten häufig bei Ersatzteilen, Wartungskomponenten oder selten bestellten Produkten auf.

Typische Eigenschaften:

- viele Perioden mit Nachfrage = 0
- sporadische Bestellungen
- große Varianz zwischen Nachfrageereignissen

Diese Struktur erzeugt besondere Herausforderungen für [[demand-forecasting]]. Viele klassische Prognosemethoden und insbesondere deren Bewertungsmetriken funktionieren unter diesen Bedingungen schlecht.

## Problem für Forecast-Metriken

Viele gängige Kennzahlen zur Bewertung der Prognosequalität basieren auf Divisionen durch tatsächliche Nachfragewerte oder Benchmark-Fehler. Bei Nullwerten entstehen daher:

- unendliche Werte
- undefinierte Kennzahlen

Besonders betroffen sind:

- [[mape]]
- [[relative-error-metrics]]

## Spezialisierte Methoden

Für intermittierende Nachfrage wurden spezielle Prognosemethoden entwickelt, darunter:

- [[croston-method]]

## Bewertung von Prognosen

Für die Bewertung von Prognosen empfiehlt [[rob-j-hyndman]] die Kennzahl [[mean-absolute-scaled-error-mase]], da sie auch bei häufigen Nullwerten stabile Ergebnisse liefert.
