---
title: Syntetos–Boylan Demand Classification
type: concept
domain: ai
sources: [raw/pdfs/Forecast Error Measures Intermittent Demand by Manu Joseph Towards Data Science.pdf]
related: ["[[intermittent-demand]]", "[[average-demand-interval-adi]]", "[[coefficient-of-variation-squared-demand]]"]
confidence: medium
last_updated: 2026-04-17
---

Die **Syntetos–Boylan Demand Classification** ist eine Methode zur Einteilung von Nachfrage-Zeitreihen anhand ihrer Struktur. Sie wurde von Syntetos und Boylan (2005) vorgeschlagen und wird häufig bei der Analyse von [[intermittent-demand]] verwendet.

Die Klassifikation basiert auf zwei Kennzahlen:

1. [[average-demand-interval-adi]] — misst die Intermittency der Nachfrage
2. [[coefficient-of-variation-squared-demand]] — misst die Variabilität der Nachfrage

Syntetos und Boylan leiteten Schwellenwerte ab, bei denen sich das Verhalten der Zeitreihe deutlich ändert:

- ADI-Grenzwert: **1.32**
- COV²-Grenzwert: **0.49**

Die Kombination dieser beiden Dimensionen ergibt vier Klassen von Nachfrageverhalten:

- **Smooth** – niedrige Intermittency und geringe Variabilität
- **Erratic** – häufige Nachfrage, aber hohe Variabilität
- **Intermittent** – seltene Nachfrage, aber relativ stabile Mengen
- **Lumpy** – seltene Nachfrage und hohe Variabilität

Diese Klassifikation wird häufig verwendet, um geeignete **Forecast-Methoden und Evaluationsmetriken** auszuwählen. Viele klassische Forecast-Metriken funktionieren gut bei Smooth oder Erratic Serien, sind jedoch problematisch für Intermittent oder Lumpy Serien.
