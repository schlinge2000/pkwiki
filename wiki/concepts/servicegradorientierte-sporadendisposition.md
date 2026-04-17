---
title: Servicegradorientierte Sporadendisposition
type: concept
domain: business
sources: [raw/pdfs/Leistungsbeschreibung BO 2024.pdf]
related: ["[[bestandsoptimierung-addone-bo]]", "[[sicherheitsbestand-servicegrad-berechnung]]"]
confidence: medium
last_updated: 2026-04-18
---

Die **servicegradorientierte Sporadendisposition** ist ein Verfahren zur Bestandsplanung für Artikel mit unregelmäßiger oder sporadischer Nachfrage.

Das Verfahren basiert auf einem intelligenten **Meldebestandsmodell**. Dabei werden zwei zentrale Bestandsgrenzen berechnet:

- Meldebestand
- Auffüllbestand

Der Meldebestand wird so bestimmt, dass während der Wiederbeschaffungszeit ein definierter Servicegrad eingehalten werden kann. Hierzu werden historische Verkaufsdaten analysiert und in Zeitintervalle (Quantile) unterteilt.

ADD*ONE BO unterstützt verschiedene Berechnungsvarianten:

- ereignisorientierte Berechnung
- mengenorientierte Berechnung
- jeweils mit oder ohne Interpolation

Der Auffüllbestand wird kostenorientiert bestimmt. Dabei werden Lagerkosten und Bestellkosten gegeneinander abgewogen.

Sobald sich die Nachfrage stabilisiert und Prognosen ausreichend zuverlässig werden, kann das System automatisch zu einem **bedarfsorientierten, prognosebasierten Dispositionsverfahren** wechseln.

confidence: medium
