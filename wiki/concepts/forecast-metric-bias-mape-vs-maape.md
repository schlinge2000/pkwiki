---
title: Bias von Forecast-Metriken (MAPE vs MAAPE)
type: concept
domain: ai
sources: [raw/pdfs/MAAPE_ScienceDirectPaper.pdf]
related: ["[[mape]]", "[[mean-arctangent-absolute-percentage-error-maape]]", "[[forecast-accuracy-metrics]]"]
confidence: medium
last_updated: 2026-04-17
---

Das Paper zeigt, dass [[mape]] systematische **Bias‑Effekte bei der Optimierung von Prognosen** erzeugen kann.

Grund: Die Verlustfunktion von MAPE bestraft **positive Fehler (F > A)** stärker als negative Fehler (F < A). Dadurch entstehen asymmetrische Kostenstrukturen.

Folge:

- Optimierungsverfahren, die MAPE minimieren, tendieren zu **systematisch niedrigeren Forecasts**.
- Die resultierenden Punktprognosen liegen oft **unter dem Mittelwert der tatsächlichen Nachfrage**.

Die Autoren vergleichen dieses Verhalten mit der neuen Metrik [[mean-arctangent-absolute-percentage-error-maape]].

Ergebnisse der Analyse:

- Sowohl MAPE als auch MAAPE erzeugen tendenziell leicht nach unten verzerrte Forecasts
- Der Bias ist jedoch **deutlich geringer bei MAAPE**

Grund dafür ist die Form der Verlustfunktion:

- MAPE wächst stark und unbeschränkt
- MAAPE besitzt eine **abgeflachte, begrenzte Kurve** durch die arctan‑Transformation

Simulationen mit verschiedenen Nachfrageverteilungen zeigen, dass Prognosen unter MAAPE **näher am Mittelwert oder Median der Nachfrageverteilung** liegen als Prognosen unter MAPE.
