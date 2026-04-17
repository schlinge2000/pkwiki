---
title: ADD*ONE Beschaffungslogistik
type: concept
domain: business
sources: [raw/docs/doku.pdf]
related: ["[[add-one-bestandsoptimierung]]"]
confidence: medium
last_updated: 2026-04-17
---

Die **ADD*ONE Beschaffungslogistik** ist eine Funktionskomponente von [[add-one-bestandsoptimierung]].

Sie dient der **Zusammenfassung einzelner Bestellpositionen zu Bestellungen** und der Übertragung dieser Bestellungen an ein ERP-System.

## Prozess

1. ADD*ONE generiert Bestellvorschläge
2. Bestellpositionen werden freigegeben
3. Positionen werden zu Bestellungen zusammengeführt
4. Bestellungen werden an das ERP-System übertragen

## Kriterien für Zusammenfassung

Bestellpositionen werden nur dann zu einer Bestellung zusammengeführt, wenn bestimmte Kriterien erfüllt sind:

- gleicher Lieferant
- gleiche organisatorische Struktur (z. B. Werk)
- gleicher Zusammenfassungszeitraum

Zusätzlich werden Lieferantenbedingungen berücksichtigt, z. B.

- Mindestbestellwert
- Mindestgewicht
- maximale Bestellgröße

## Ziel

Die Beschaffungslogistik reduziert operative Komplexität und ermöglicht eine strukturierte Übergabe von Bestellungen an das ERP-System.
