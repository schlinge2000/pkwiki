---
title: Mittelwert-Baseline in Prognosemodellen
type: concept
domain: ai
sources: [raw/pdfs/Report_Forecast_Maschinenauslastung.pdf]
related: ["[[forecast-accuracy-metrics]]", "[[mean-arctangent-absolute-percentage-error-maape]]", "[[stock-keeping-oriented-prediction-error-costs-spec]]"]
confidence: medium
last_updated: 2026-04-17
---

Eine Mittelwert-Baseline ist ein einfaches Prognosemodell, bei dem zukünftige Werte als Durchschnitt aller bisherigen Beobachtungen geschätzt werden.

Trotz ihrer Einfachheit kann diese Methode überraschend leistungsfähig sein, insbesondere bei stark verrauschten oder strukturlosen Zeitreihen.

In der untersuchten Studie zur Maschinenauslastung zeigte der historische Durchschnitt eine außergewöhnlich hohe Prognosegüte. In einigen Fällen übertraf er sogar komplexe KI-Modelle mit vielen Parametern.

Dieses Phänomen wird als "Mittelwert-Paradoxon" beschrieben: Wenn historische Daten keine stabilen Muster, Trends oder Saisonalitäten enthalten, ist der Mittelwert statistisch oft die stabilste Schätzung.

Neuronale Zeitreihenmodelle können unter solchen Bedingungen ebenfalls zu ähnlichen Ergebnissen konvergieren. Wenn ein Modell keine verlässlichen Muster erkennt, verteilt es Wahrscheinlichkeiten über mögliche zukünftige Werte und tendiert dabei häufig zu einem zentralen Erwartungswert.

Damit fungiert der Mittelwert faktisch als "Fallback-Strategie" moderner Modelle. Erst wenn ausreichend strukturierte Daten vorhanden sind, beginnen komplexe Modelle, systematisch von dieser Baseline abzuweichen.
