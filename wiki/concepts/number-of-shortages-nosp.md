---
title: Number of Shortages (NOS / NOSp)
type: concept
domain: ai
sources: [raw/pdfs/Forecast Error Measures Intermittent Demand by Manu Joseph Towards Data Science.pdf]
related: ["[[intermittent-demand]]", "[[cumulative-forecast-error-cfe]]"]
confidence: medium
last_updated: 2026-04-17
---

Die **Number of Shortages (NOS)** bzw. **Percentage of Number of Shortages (NOSp)** misst, wie häufig eine Prognose zu **Stockouts** führt.

Definition:

Die Metrik zählt alle Perioden, in denen

Forecast < tatsächliche Nachfrage

Ein hoher Wert bedeutet, dass Prognosen systematisch zu niedrig sind und dadurch häufig Lieferengpässe entstehen.

Die prozentuale Variante **NOSp** normiert diese Anzahl auf die Gesamtzahl der Perioden.

Die Metrik wird als Alternative zu klassischen Bias-Detektoren wie dem **Tracking Signal** vorgeschlagen, da dieses auf der Annahme einer normalverteilten Nachfrage basiert. Diese Annahme ist bei [[intermittent-demand]] häufig verletzt.

NOS bzw. NOSp eignet sich daher besser zur Identifikation von **systematischer Unterprognose bei sporadischer Nachfrage**.
