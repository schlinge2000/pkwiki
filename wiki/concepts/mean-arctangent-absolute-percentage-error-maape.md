---
title: Mean Arctangent Absolute Percentage Error (MAAPE)
type: concept
domain: ai
sources: [raw/pdfs/MAAPE_ScienceDirectPaper.pdf]
related: ["[[absolute-percentage-error-ape]]", "[[mape]]", "[[smape]]", "[[mean-absolute-scaled-error-mase]]", "[[intermittent-demand]]", "[[forecast-accuracy-metrics]]"]
confidence: medium
last_updated: 2026-04-17
---

Der **Mean Arctangent Absolute Percentage Error (MAAPE)** ist eine Metrik zur Bewertung von Prognosegenauigkeit. Sie wurde von [[sungil-kim]] und [[heeyoung-kim]] vorgeschlagen, um die bekannten Probleme von [[mape]] bei Null‑ oder sehr kleinen Istwerten zu lösen.

MAAPE basiert auf einer Transformation des **Absolute Percentage Error (APE)** mithilfe der **Arctangent‑Funktion**.

Grundidee:

Statt den Fehler als Verhältnis

|A − F| / |A|

zu interpretieren (wie bei MAPE), wird dieses Verhältnis als **Tangens eines Winkels** betrachtet. Der Fehlerwert wird daher berechnet als

AAPE = arctan(|A − F| / |A|)

Der MAAPE ist anschließend der Durchschnitt dieser Werte über alle Beobachtungen.

Wichtige Eigenschaften:

- **Begrenzter Wertebereich**: Die arctan‑Funktion konvergiert gegen π/2
- **keine Division‑by‑zero‑Explosion** bei kleinen oder null Actuals
- **robust gegenüber Ausreißern**
- weiterhin **interpretierbar als prozentualer Fehler**

Der zentrale Unterschied zu [[mape]] liegt darin, dass extreme Fehler nicht unbeschränkt wachsen. Während MAPE gegen unendlich gehen kann, konvergiert MAAPE gegen π/2.

Die Autoren zeigen außerdem in Simulationen und realen Datensätzen, dass MAAPE in vielen Fällen stabilere Bewertungen von Forecast‑Methoden liefert, insbesondere bei Datensätzen mit [[intermittent-demand]].

Eine Einschränkung besteht darin, dass MAAPE sehr große Fehler weniger stark gewichtet. Wenn solche Fehler tatsächlich wichtige Ereignisse darstellen, kann diese Eigenschaft unerwünscht sein.
