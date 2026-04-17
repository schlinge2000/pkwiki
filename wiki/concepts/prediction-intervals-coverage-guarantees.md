---
title: Prediction Intervals mit Coverage Guarantees
type: concept
domain: ai
sources: [raw/pdfs/Conformal Prediction in Time Series Methods and Interpretability.pdf]
related: ["[[conformal-prediction]]", "[[uncertainty-quantification-forecasting]]"]
confidence: medium
last_updated: 2026-04-17
---

Ein zentrales Merkmal von **Conformal Prediction** ist die Fähigkeit, **Prediction Intervals mit statistischen Coverage Guarantees** zu erzeugen.

Ein Coverage‑Level beschreibt die Wahrscheinlichkeit, dass der wahre Wert innerhalb des vorhergesagten Intervalls liegt.

Beispiel:

Ein Modell mit einem **80 % Konfidenzintervall** erzeugt Intervalle, in denen der wahre Wert langfristig in etwa 80 % der Fälle enthalten ist.

## Bedeutung

Diese Garantie macht Vorhersagen deutlich verlässlicher als reine Punktprognosen, insbesondere in Entscheidungsprozessen mit Risiko.

Typische Anwendungen sind:

- Ressourcenplanung
- Risikoabschätzung
- Kapazitätsmanagement

## Voraussetzungen

Die theoretischen Garantien basieren oft auf Annahmen wie:

- i.i.d. Daten
- oder zumindest **exchangeable distributions**

Bei Zeitreihen sind diese Voraussetzungen häufig verletzt, weshalb spezielle Verfahren entwickelt wurden, um dennoch robuste Intervalle zu erzeugen.

Siehe auch:

- [[conformal-prediction-time-series]]
- [[adaptive-conformal-inference]]
