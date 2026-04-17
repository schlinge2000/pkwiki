---
title: Conformal Prediction in Time Series
type: concept
domain: ai
sources: [raw/pdfs/Conformal Prediction in Time Series Methods and Interpretability.pdf]
related: ["[[conformal-prediction]]", "[[prediction-intervals-coverage-guarantees]]", "[[adaptive-conformal-inference]]", "[[ensemble-batch-prediction-intervals-enbpi]]", "[[time-series-forecasting]]"]
confidence: medium
last_updated: 2026-04-17
---

Die Anwendung von **Conformal Prediction auf Zeitreihen** erweitert klassische Forecasting‑Modelle um zuverlässige Unsicherheitsabschätzungen.

Statt nur eine Punktprognose zu liefern, erzeugt das Verfahren **Prediction Intervals**, die den möglichen Wertebereich zukünftiger Beobachtungen beschreiben.

## Problem klassischer Zeitreihenmodelle

Viele traditionelle Methoden liefern nur Punktprognosen, etwa:

- ARIMA
- exponentielle Glättung
- Regressionsmodelle

Diese Prognosen enthalten jedoch oft keine zuverlässige Aussage darüber, wie unsicher die Vorhersage ist.

## Rolle von Conformal Prediction

Conformal Prediction ergänzt bestehende Modelle um eine **kalibrierte Unsicherheitsabschätzung**.

Dabei wird:

1. ein Basismodell trainiert
2. ein Non‑Conformity‑Score berechnet
3. daraus ein Vorhersageintervall konstruiert

Dieses Intervall besitzt eine definierte **Coverage Probability**, etwa 80 % oder 95 %.

## Herausforderungen

Zeitreihen verletzen häufig klassische Annahmen der Statistik:

- Daten sind zeitlich abhängig
- Distributionen verändern sich
- nicht‑stationäre Prozesse treten auf

Daher wurden spezialisierte Verfahren entwickelt, etwa:

- [[adaptive-conformal-inference]]
- [[ensemble-batch-prediction-intervals-enbpi]]

Diese Methoden versuchen, robuste Unsicherheitsintervalle trotz dynamischer Daten zu erzeugen.

## Anwendungsfelder

Typische Einsatzbereiche:

- Call‑Center‑Volumenprognosen
- Energiemarkt‑Forecasts
- Umwelt‑ und Klimamodelle
- Finanzmarktanalysen
