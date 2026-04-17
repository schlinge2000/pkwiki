---
title: ADD*ONE Bedarfsprognose
type: concept
domain: ai
sources: [raw/pdfs/ADDONE Bestandsoptimierung DE 2512.pdf]
related: ["[[addone-bestandsoptimierung-de-2512]]", "[[kostenoptimiertes-losgroessenverfahren-addone]]", "[[addone-kreuztabellen]]"]
confidence: medium
last_updated: 2026-04-17
---

Die **ADD*ONE Bedarfsprognose** ist das Prognosemodul von [[addone-bo]], das zukünftige Nachfrage auf Basis historischer Verbrauchsdaten berechnet.

Der Prognoseprozess umfasst mehrere Schritte:

1. Analyse der historischen Abgänge
2. Erkennung von Mustern wie
   - Trend
   - Saison
   - Ausreißer
   - Strukturbrüche
3. Test verschiedener Prognoseverfahren
4. Auswahl des Parametersatzes mit der geringsten Prognoseabweichung

ADD*ONE verwendet verschiedene Prognoseverfahren, darunter:

- exponentielle Glättung
- Holt‑Verfahren
- Holt‑Winters
- Theta‑Methode
- Croston‑Verfahren (für sporadische Nachfrage)

Die Prognose wird häufig als **„Blackbox“** genutzt:

- Verfahren und Parameter werden automatisch bestimmt
- Prognosen werden täglich aktualisiert

Artikel werden nach Prognosequalität klassifiziert (XYZ‑Analyse):

- X: sehr gut prognostizierbar
- Y: mittel
- Z: unsicher
- C/K/N: spezielle Fälle (sporadisch oder zu wenig Historie)

Diese Klassifizierung wird in [[addone-kreuztabellen]] verwendet, um kritische Artikel zu identifizieren.
