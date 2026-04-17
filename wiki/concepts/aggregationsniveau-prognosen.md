---
title: Aggregationsniveau in Prognosemodellen
type: concept
domain: ai
sources: [raw/pdfs/Report_Forecast_Maschinenauslastung.pdf]
related: ["[[maschinenauslastungsprognose]]", "[[sporadische-nachfrage-prognose]]", "[[intermittent-demand]]"]
confidence: medium
last_updated: 2026-04-17
---

Das Aggregationsniveau beschreibt die Ebene, auf der Zeitreihen für Prognosen modelliert werden. Typische Ebenen sind Einzelartikel, Produktgruppen, Kundensegmente oder Produktionsressourcen.

Die Wahl des Aggregationsniveaus beeinflusst maßgeblich die Stabilität und Interpretierbarkeit von Prognosen.

In der untersuchten Studie wurden drei zentrale Ebenen verglichen:
- Artikelbasis
- Kundensegmente
- Maschinengruppen

Ergebnisse der Experimente:

Artikelbasierte Prognosen mit anschließender Aggregation lieferten die besten SPEC-Werte. Obwohl die Einzelzeitreihen stark sporadisch waren, führte die Aggregation vieler unabhängiger Reihen zu stabileren Gesamtprognosen.

Segmentbasierte Prognosen zeigten dagegen häufiger systematische Überschätzungen. Dies deutet darauf hin, dass segmentbezogene Nachfragezyklen schwerer zu modellieren sind oder dass zufällige Schwankungen nicht ausreichend geglättet werden.

Prognosen auf Maschinenebene machten saisonale Produktionsmuster sichtbar, die auf niedrigeren Ebenen nicht erkennbar waren.

Die Ergebnisse unterstützen die Hypothese, dass gemäß dem Gesetz der großen Zahlen Aggregationen unabhängiger Nachfrageprozesse stabilere Muster erzeugen können.
