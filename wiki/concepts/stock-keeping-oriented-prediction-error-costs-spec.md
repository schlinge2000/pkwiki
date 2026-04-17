---
title: Stock-keeping-oriented Prediction Error Costs (SPEC)
type: concept
domain: ai
sources: [raw/pdfs/Forecast Error Measures Intermittent Demand by Manu Joseph Towards Data Science.pdf]
related: ["[[intermittent-demand]]", "[[periods-in-stock-pis]]", "[[inventory-optimization-ai]]"]
confidence: medium
last_updated: 2026-04-17
---

**Stock-keeping-oriented Prediction Error Costs (SPEC)** ist eine Forecast-Evaluationsmetrik, die Prognosefehler direkt in **wirtschaftliche Kosten der Lagerhaltung** übersetzt.

Die Metrik kombiniert zwei Arten von Kosten:

- **Opportunity Costs** durch Unterprognose (entgangene Verkäufe)
- **Stock Keeping Costs** durch Überprognose (Lagerhaltung)

Für jeden Zeitpunkt wird untersucht, wie sich kumulative Forecasts und tatsächliche Nachfrage auf Bestände und Fehlmengen auswirken. Daraus werden Kosten berechnet, die über alle Zeitpunkte aggregiert werden.

SPEC enthält zwei Gewichtungsparameter:

- α1 — Gewicht für Opportunity Costs
- α2 — Gewicht für Lagerhaltungskosten

Eine häufig verwendete Konfiguration im Retail-Kontext ist:

α1 = 0.75
α2 = 0.25

Damit wird Unterprognose stärker bestraft als Überprognose.

Im Gegensatz zu rein statistischen Fehlermetriken berücksichtigt SPEC explizit die **Supply-Chain-Auswirkungen von Forecast-Fehlern** und ist daher besonders geeignet für [[intermittent-demand]].

Ein Nachteil der Metrik ist ihre höhere **Rechenkomplexität**, da zur Berechnung mehrere verschachtelte Iterationen über die Zeitreihe notwendig sind.
