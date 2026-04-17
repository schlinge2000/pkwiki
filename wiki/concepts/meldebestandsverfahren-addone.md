---
title: Meldebestandsverfahren (ADD*ONE)
type: concept
domain: business
sources: [raw/pdfs/ADDONE Bestandsoptimierung DE 2512.pdf]
related: ["[[servicegradorientierte-sporadendisposition]]", "[[wiederbeschaffungszeit-addone]]", "[[addone-bestandsoptimierung-de-2512]]"]
confidence: medium
last_updated: 2026-04-17
---

Das **Meldebestandsverfahren** ist ein Bestellpunktverfahren zur Disposition von Artikeln mit **unregelmäßigem oder sporadischem Bedarf**.

Es wird in [[addone-bo]] vor allem für Ersatzteile oder selten benötigte Artikel eingesetzt.

Grundprinzip:

- Sobald der Prüfbestand unter den **Meldebestand** fällt, wird eine Bestellung ausgelöst.

Der Prüfbestand umfasst:

- aktuellen Bestand
- geplante Zugänge
- minus bekannte Bedarfe

Die Bestellmenge wird berechnet als:

Auffüllbestand − Prüfbestand

Dabei berücksichtigt ADD*ONE zusätzlich:

- Mindestbestellmengen
- Rundungsmengen
- Wiederbeschaffungszeiten

In Kombination mit der [[servicegradorientierte-sporadendisposition]] können Meldebestände automatisch berechnet werden, basierend auf:

- historischem Verbrauch
- gewünschtem Servicegrad
- Wiederbeschaffungszeit

Das Verfahren eignet sich besonders für:

- sporadische Nachfrage
- Ersatzteilmanagement
- schwer prognostizierbare Artikel.
