---
title: Mean Absolute Scaled Error (MASE)
type: concept
domain: ai
sources: [raw/pdfs/foresight.pdf]
related: ["[[forecast-accuracy-metrics]]", "[[intermittent-demand]]", "[[scale-dependent-error-metrics]]", "[[relative-error-metrics]]", "[[demand-forecasting]]"]
confidence: medium
last_updated: 2026-04-17
---

Der Mean Absolute Scaled Error (MASE) ist eine Kennzahl zur Bewertung von Prognosegenauigkeit, vorgeschlagen von [[rob-j-hyndman]]. Sie wurde entwickelt, um Probleme klassischer Forecast-Metriken insbesondere bei [[intermittent-demand]] zu vermeiden.

## Grundidee

Der Forecast-Fehler wird relativ zum **durchschnittlichen Fehler eines Naïve‑Forecasts innerhalb der Trainingsdaten** skaliert.

Skalierter Fehler:

q_t = e_t / (durchschnittlicher absoluter Fehler der Naïve‑Prognose im Sample)

Der MASE ergibt sich als:

MASE = mean(|q_t|)

## Interpretation

- MASE < 1 → Prognose ist besser als die durchschnittliche Naïve‑Prognose
- MASE > 1 → Prognose ist schlechter als die Naïve‑Prognose

## Vorteile

- skalenunabhängig
- keine Division durch Null bei intermittierenden Daten
- vergleichbar zwischen unterschiedlichen Zeitreihen
- geeignet für mehrere Forecast-Horizonte

## Anwendung

MASE kann verwendet werden für:

- Vergleich verschiedener Prognosemethoden auf einer Zeitreihe
- Vergleich von Forecasting-Modellen über mehrere Zeitreihen
- Bewertung von Prognosen bei [[intermittent-demand]]

Der Artikel argumentiert, dass MASE eine **allgemeine Standardmetrik für Forecast-Evaluierung** sein könnte.
