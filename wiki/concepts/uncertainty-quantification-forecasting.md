---
title: Uncertainty Quantification im Forecasting
type: concept
domain: ai
sources: [raw/pdfs/Conformal Prediction in Time Series Methods and Interpretability.pdf]
related: ["[[conformal-prediction]]", "[[prediction-intervals-coverage-guarantees]]", "[[demand-forecasting]]"]
confidence: medium
last_updated: 2026-04-17
---

**Uncertainty Quantification** bezeichnet Methoden zur Messung und Kommunikation der Unsicherheit von Vorhersagen.

Im Forecasting ist dies entscheidend, da viele Entscheidungen nicht nur von der erwarteten Prognose abhängen, sondern auch vom möglichen Fehlerbereich.

## Bedeutung

Unsicherheitsabschätzungen helfen Organisationen bei:

- Ressourcenplanung
- Risikomanagement
- Kapazitätsplanung

Beispielsweise können Unternehmen bei Nachfrageprognosen nicht nur eine erwartete Nachfrage, sondern auch einen möglichen Wertebereich berücksichtigen.

## Methoden

Mehrere Ansätze existieren zur Unsicherheitsquantifizierung:

- statistische Konfidenzintervalle
- Bayesianische Modelle
- Ensemble‑Methoden
- [[conformal-prediction]]

Conformal Prediction ist besonders attraktiv, da es **modellunabhängig** eingesetzt werden kann und formale Coverage‑Garantien liefert.

## Rolle in Zeitreihen

In dynamischen Systemen wie Energie‑ oder Nachfrageprognosen verbessert Uncertainty Quantification die Entscheidungsqualität erheblich, da Modelle ihre eigene Unsicherheit transparent machen.
