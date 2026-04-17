---
title: Prognose sporadischer Nachfrage
type: concept
domain: ai
sources: [raw/pdfs/Report_Forecast_Maschinenauslastung.pdf]
related: ["[[intermittent-demand]]", "[[aggregationsniveau-prognosen]]", "[[mean-arctangent-absolute-percentage-error-maape]]"]
confidence: medium
last_updated: 2026-04-17
---

Sporadische Nachfrage bezeichnet Zeitreihen, bei denen Nachfrageereignisse unregelmäßig auftreten und häufig durch längere Nullperioden getrennt sind.

Solche Zeitreihen sind in vielen industriellen Anwendungen verbreitet, beispielsweise bei Ersatzteilen oder Spezialprodukten mit niedriger Absatzfrequenz.

Die Prognose sporadischer Nachfrage ist schwierig, da:
- hohe Varianz zwischen einzelnen Perioden besteht
- viele Beobachtungen den Wert Null aufweisen
- klassische Trend- oder Saisonmodelle oft keine stabilen Muster erkennen

In der untersuchten Studie zur Maschinenauslastung waren viele Artikelverbräuche stark sporadisch. Einzelzeitreihen lieferten daher nur begrenzt belastbare Prognosen.

Eine mögliche Strategie besteht darin, Prognosen auf Einzelartikelbasis zu erstellen und anschließend zu aggregieren. Durch die Kombination vieler unabhängiger Zeitreihen können zufällige Schwankungen teilweise ausgeglichen werden.

Diese Eigenschaft steht im Zusammenhang mit dem Gesetz der großen Zahlen und erklärt, warum aggregierte Prognosen häufig stabiler sind als Prognosen einzelner sporadischer Reihen.
