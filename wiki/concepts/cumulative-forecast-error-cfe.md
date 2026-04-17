---
title: Cumulative Forecast Error (CFE)
type: concept
domain: ai
sources: [raw/pdfs/Forecast Error Measures Intermittent Demand by Manu Joseph Towards Data Science.pdf]
related: ["[[forecast-accuracy-metrics]]", "[[periods-in-stock-pis]]", "[[stock-keeping-oriented-prediction-error-costs-spec]]"]
confidence: medium
last_updated: 2026-04-17
---

Der **Cumulative Forecast Error (CFE)** misst den kumulierten, signierten Forecast-Fehler über einen Zeitraum.

Definition:

CFE ist die Summe aller Forecastfehler über den gesamten Prognosehorizont.

Eigenschaften:

- positive und negative Fehler können sich gegenseitig aufheben
- dient primär zur **Erkennung von Forecast-Bias** (systematische Über- oder Unterprognosen)

In Supply-Chain-Kontexten hat CFE direkte Auswirkungen auf:

- Überbevorratung
- Stockouts

Ein CFE nahe null bedeutet jedoch nicht zwingend, dass das Forecast-Modell gut ist. Positive und negative Fehler können sich zufällig ausgleichen.

Aus diesem Grund wird empfohlen, CFE gemeinsam mit anderen Metriken zu verwenden, z. B.:

- [[periods-in-stock-pis]]
- [[stock-keeping-oriented-prediction-error-costs-spec]]

Diese ergänzen CFE um Informationen über die **zeitliche Struktur von Fehlern und deren Auswirkungen auf Lagerbestände**.
