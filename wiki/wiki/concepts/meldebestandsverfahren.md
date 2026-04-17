---
title: Meldebestandsverfahren
type: concept
domain: business
sources: [raw/docs/doku.pdf]
related: ["[[add-one-bestandsoptimierung]]", "[[servicegradorientierte-sporadendisposition]]"]
confidence: medium
last_updated: 2026-04-17
---

Das **Meldebestandsverfahren** ist ein Bestellpunktverfahren zur Disposition von Artikeln mit unregelmäßigem Bedarf.

Es wird in [[add-one-bestandsoptimierung]] insbesondere für sporadisch nachgefragte Artikel eingesetzt.

## Funktionsprinzip

Eine Bestellung wird ausgelöst, sobald der sogenannte **Meldebestand** unterschritten wird.

Die Bestellmenge ergibt sich aus:

Auffüllbestand − Prüfbestand

Der Prüfbestand berücksichtigt:

- aktuellen Lagerbestand
- offene Zugänge
- bekannte Bedarfe

## Charakteristika

Typische Eigenschaften des Verfahrens:

- geeignet für Ersatzteile
- geeignet für sporadische Nachfrage
- keine kontinuierliche Prognose erforderlich

## Erweiterung

In ADD*ONE kann das Verfahren mit der
[[servicegradorientierte-sporadendisposition]] kombiniert werden.

Dabei werden Melde‑ und Auffüllbestände automatisch anhand von Servicegrad und Verbrauchshistorie berechnet.
