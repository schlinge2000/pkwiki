---
title: Relative Error Metrics
type: concept
domain: ai
sources: [raw/pdfs/foresight.pdf]
related: ["[[forecast-accuracy-metrics]]", "[[intermittent-demand]]"]
confidence: medium
last_updated: 2026-04-17
---

Relative Error Metrics bewerten Prognosefehler relativ zu einem **Benchmark-Forecasting-Modell**.

Typischerweise wird der Fehler eines Modells durch den Fehler einer Referenzmethode geteilt, häufig durch eine Naïve‑Prognose.

Beispiel:

r_t = e_t / e*_t

wobei e*_t der Fehler der Benchmark-Prognose ist.

Typische Kennzahlen:

- MdRAE (Median Relative Absolute Error)
- GMRAE (Geometric Mean Relative Absolute Error)

## Vorteile

- skalenunabhängig
- geeignet für Vergleich zwischen unterschiedlichen Zeitreihen

## Problem bei intermittierenden Daten

Bei [[intermittent-demand]] können Benchmark-Fehler sehr klein oder Null sein. Dadurch entsteht:

- Division durch Null
- unendliche oder undefinierte Werte

Aus diesem Grund gelten relative Fehlermaße als problematisch für solche Zeitreihen.
