---
title: Coefficient of Variation Squared (COV²) in Demand Series
type: concept
domain: ai
sources: [raw/pdfs/Forecast Error Measures Intermittent Demand by Manu Joseph Towards Data Science.pdf]
related: ["[[syntetos-boylan-demand-classification]]", "[[intermittent-demand]]"]
confidence: medium
last_updated: 2026-04-17
---

Der **Coefficient of Variation Squared (COV²)** misst die relative Variabilität einer Nachfrage-Zeitreihe.

Er basiert auf dem **Coefficient of Variation (COV)**, der als Verhältnis von Standardabweichung zu Mittelwert definiert ist. Durch die Quadrierung entsteht COV².

Eigenschaften:

- normiert die Varianz relativ zum Mittelwert
- verhindert Skalierungsprobleme zwischen verschiedenen Zeitreihen
- misst die **Volatilität der Nachfrage** unabhängig von ihrer absoluten Größe

Interpretation:

- **niedriger COV²** → stabile Nachfrage
- **hoher COV²** → stark schwankende Nachfrage

In der [[syntetos-boylan-demand-classification]] wird COV² gemeinsam mit [[average-demand-interval-adi]] verwendet, um Nachfrage in die Klassen Smooth, Erratic, Intermittent oder Lumpy einzuordnen.

Der theoretische Grenzwert liegt bei **COV² = 0.49**.
