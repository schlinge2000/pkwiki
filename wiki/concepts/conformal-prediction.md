---
title: Conformal Prediction
type: concept
domain: ai
sources: [raw/pdfs/Conformal Prediction in Time Series Methods and Interpretability.pdf]
related: ["[[conformal-prediction-time-series]]", "[[prediction-intervals-coverage-guarantees]]", "[[uncertainty-quantification-forecasting]]", "[[vladimir-vovk]]", "[[alex-gammerman]]", "[[vladimir-vapnik]]"]
confidence: medium
last_updated: 2026-04-17
---

**Conformal Prediction** ist ein statistisches Framework zur Quantifizierung von Unsicherheit in Machine‑Learning‑Vorhersagen. Statt nur einen Punktwert vorherzusagen, erzeugt das Verfahren **Prediction Sets oder Prediction Intervals**, die den wahren Wert mit einer vorgegebenen Wahrscheinlichkeit enthalten.

Das Konzept wurde Ende der 1990er Jahre von Forschern wie [[alex-gammerman]], [[vladimir-vovk]] und [[vladimir-vapnik]] entwickelt.

## Grundidee

Ein Modell erzeugt zunächst eine normale Vorhersage. Anschließend bewertet Conformal Prediction, wie "ungewöhnlich" ein neues Beispiel im Vergleich zu historischen Daten ist.

Auf Basis dieser **Non‑Conformity Scores** werden Vorhersageintervalle konstruiert.

Der zentrale Vorteil ist eine **statistische Garantie**:

Wenn ein 90 % Konfidenzniveau gewählt wird, enthält das erzeugte Intervall den wahren Wert in etwa 90 % der Fälle.

## Eigenschaften

Wichtige Merkmale des Frameworks:

- modellagnostisch (funktioniert mit vielen ML‑Modellen)
- keine Annahme über Normalverteilung
- liefert kalibrierte Unsicherheitsintervalle
- ermöglicht interpretiere Vorhersagen

Diese Eigenschaften machen Conformal Prediction besonders attraktiv für reale Entscheidungsprozesse.

## Einsatzgebiete

Typische Anwendungen umfassen:

- medizinische Diagnosemodelle
- Finanzprognosen
- Energie‑ und Nachfrageprognosen
- Zeitreihenanalyse

Im Bereich **Time Series Forecasting** wird Conformal Prediction zunehmend genutzt, um Unsicherheit bei Vorhersagen systematisch abzuschätzen.

Siehe auch: [[conformal-prediction-time-series]].
