---
title: Kostenoptimiertes Losgrößenverfahren (ADD*ONE)
type: concept
domain: business
sources: [raw/pdfs/ADDONE Bestandsoptimierung DE 2512.pdf]
related: ["[[addone-bestandsoptimierung-de-2512]]", "[[wiederbeschaffungszeit-addone]]", "[[addone-bedarfsprognose]]", "[[sicherheitsbestand-servicegrad-berechnung]]"]
confidence: medium
last_updated: 2026-04-17
---

Das **kostenoptimierte Losgrößenverfahren** ist die Standard‑Optimierungsmethode der Software [[addone-bo]]. Ziel ist es, Bestellmengen und Bestellzeitpunkte so zu bestimmen, dass **Gesamtkosten minimiert und gleichzeitig Servicegrade eingehalten werden**.

Die Methode balanciert zwei zentrale Kostenarten:

- Lagerhaltungskosten
- Bestell- bzw. Abwicklungskosten

Ein höherer Lagerbestand reduziert Bestellfrequenz, erhöht jedoch Lagerkosten. Häufigere Bestellungen reduzieren Bestände, erhöhen jedoch Abwicklungskosten. ADD*ONE berechnet daher automatisch eine **kostenoptimale Bestellmenge**.

Grundlage der Berechnung sind:

- Prognosen aus der [[addone-bedarfsprognose]]
- Sicherheitsbestände
- Wiederbeschaffungszeiten
- Bestell- und Lagerkosten
- Mindest‑ und Rundungsmengen

Der Ablauf:

1. Prognosen bestimmen den zukünftigen Bedarf.
2. ADD*ONE simuliert Bestandsverläufe über den Planungshorizont.
3. Sobald der Bestand unter den Sicherheitsbestand sinken würde, wird ein Bestellvorschlag erzeugt.
4. Die Bestellmenge wird so optimiert, dass Gesamtkosten minimal sind.

Zusätzliche Restriktionen können berücksichtigt werden:

- [[wiederbeschaffungszeit-addone]]
- Mindestbestellmengen
- Rundungsmengen
- maximale Reichweite
- Höchstbestände

Das Verfahren eignet sich besonders für Artikel mit **regelmäßigem Bedarf und ausreichend stabilen Prognosen**.
