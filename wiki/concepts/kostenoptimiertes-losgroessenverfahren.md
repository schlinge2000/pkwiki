---
title: Kostenoptimiertes Losgrößenverfahren
type: concept
domain: business
sources: [raw/docs/doku.pdf]
related: ["[[add-one-bestandsoptimierung]]", "[[meldebestandsverfahren]]", "[[reichweitenoptimierung]]"]
confidence: medium
last_updated: 2026-04-17
---

Das **kostenoptimierte Losgrößenverfahren** ist die Standard‑Optimierungsmethode in [[add-one-bestandsoptimierung]].

Ziel ist die Ermittlung optimaler Bestellmengen unter Berücksichtigung von Kosten und Servicegrad.

## Zielkonflikt

Die Methode balanciert zwei gegenläufige Kostenarten:

- **Bestellkosten** (z. B. administrative Abwicklung)
- **Lagerhaltungskosten** (Kapitalbindung und Lagerkosten)

Große Bestellmengen reduzieren Bestellkosten, erhöhen aber Lagerkosten.

Kleine Bestellmengen reduzieren Lagerkosten, erhöhen jedoch die Bestellfrequenz.

## Entscheidungslogik

ADD*ONE berechnet Bestellvorschläge auf Basis von:

- Prognosen
- Aufträgen
- Wiederbeschaffungszeiten
- Sicherheitsbeständen

Die Bestellmenge wird so gewählt, dass die **Gesamtkosten minimiert** werden.

## Wichtige Eingangsparameter

- Einkaufspreis
- fixe Abwicklungskosten
- Lagerhaltungssatz
- Rundungs‑ und Mindestbestellmengen
- Wiederbeschaffungszeit

## Ergebnis

Das System erzeugt optimierte Bestellvorschläge, die anschließend vom Disponenten freigegeben werden können.
