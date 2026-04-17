---
title: Average Demand Interval (ADI)
type: concept
domain: ai
sources: [raw/pdfs/Forecast Error Measures Intermittent Demand by Manu Joseph Towards Data Science.pdf]
related: ["[[syntetos-boylan-demand-classification]]", "[[intermittent-demand]]"]
confidence: medium
last_updated: 2026-04-17
---

Das **Average Demand Interval (ADI)** misst, wie häufig Nachfrage in einer Zeitreihe auftritt. Es ist definiert als der durchschnittliche Abstand in Perioden zwischen zwei Zeitpunkten mit **nicht‑null Nachfrage**.

Beispiel:

Ein ADI von **1.9** bedeutet, dass im Durchschnitt alle 1.9 Perioden eine Nachfrage größer als Null auftritt.

Interpretation:

- **niedriger ADI** → häufige Nachfrage
- **hoher ADI** → seltene bzw. intermittierende Nachfrage

ADI wird gemeinsam mit [[coefficient-of-variation-squared-demand]] verwendet, um Zeitreihen nach der [[syntetos-boylan-demand-classification]] zu kategorisieren.

Der theoretische Schwellenwert für intermittierende Nachfrage liegt bei **ADI = 1.32**. Werte oberhalb dieses Schwellenwerts deuten auf eine intermittierende Struktur der Zeitreihe hin.
