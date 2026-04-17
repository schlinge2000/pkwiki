---
title: ADD*ONE Bedarfsprognose
type: concept
domain: ai
sources: [raw/docs/doku.pdf]
related: ["[[add-one-bestandsoptimierung]]"]
confidence: medium
last_updated: 2026-04-17
---

Die **ADD*ONE Bedarfsprognose** ist die Prognosekomponente von [[add-one-bestandsoptimierung]].

Sie berechnet zukünftige Nachfrage auf Basis historischer Abgangsdaten.

## Analyse der Nachfrage

Das System analysiert automatisch die Struktur der Nachfrage und erkennt:

- konstanten Bedarf
- Trends
- saisonale Muster
- Ausreißer
- Strukturbrüche
- sporadische Nachfrage

## Auswahl des Prognosemodells

Mehrere Prognoseverfahren und Parametersätze werden getestet.

Für jedes Modell wird die Prognoseabweichung gegenüber historischen Daten berechnet. Das Modell mit der geringsten Abweichung wird ausgewählt.

## Prognosegüte

Artikel werden nach Prognosequalität klassifiziert:

- X‑Artikel – sehr gut prognostizierbar
- Y‑Artikel – mittel prognostizierbar
- Z‑Artikel – unsicher prognostizierbar

Weitere Kategorien sind z. B.

- C‑Artikel (Croston‑Verfahren)
- K‑Artikel (Kurzzeitprognose)

## Nutzung

Die Prognose bildet die Grundlage für:

- Bestellvorschläge
- Bestandsplanung
- Produktionsplanung
