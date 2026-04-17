---
title: Outlier-Robustheit von MAAPE
type: concept
domain: ai
sources: [raw/pdfs/MAAPE_ScienceDirectPaper.pdf]
related: ["[[mean-arctangent-absolute-percentage-error-maape]]", "[[mape]]", "[[forecast-accuracy-metrics]]"]
confidence: medium
last_updated: 2026-04-17
---

Ein wesentliches Merkmal von [[mean-arctangent-absolute-percentage-error-maape]] ist seine **Robustheit gegenüber extrem großen Prognosefehlern (Outliers)**.

Beim klassischen [[mape]] wächst der Fehler unbegrenzt, wenn der Forecast stark vom Actual abweicht oder wenn der Actual‑Wert sehr klein ist. Dadurch können einzelne extreme Fehler den Durchschnitt stark verzerren.

MAAPE verwendet stattdessen die Funktion

arctan(|A − F| / |A|)

Die arctan‑Funktion besitzt eine wichtige Eigenschaft:

- für große Werte konvergiert sie gegen **π/2**

Dadurch wird der Einfluss sehr großer Fehler automatisch begrenzt.

Konsequenzen:

- extreme Forecast‑Fehler dominieren die Gesamtmetrik nicht
- die Metrik wird stabiler gegenüber Messfehlern oder Ausreißern
- besonders nützlich bei realen Business‑Daten mit starken Schwankungen

Die Autoren zeigen, dass diese Eigenschaft MAAPE besonders geeignet für Datensätze mit unregelmäßiger Nachfrage oder vielen Nullwerten macht.

Eine mögliche Einschränkung besteht darin, dass extrem große Fehler weniger stark bestraft werden. Wenn solche Fehler wichtige betriebliche Ereignisse widerspiegeln, kann diese Dämpfung unerwünscht sein.
