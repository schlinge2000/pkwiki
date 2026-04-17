---
title: Sekundärbedarfsplanung
type: concept
domain: tech
sources: [raw/pdfs/Leistungsbeschreibung BO 2024.pdf]
related: ["[[bestandsoptimierung-addone-bo]]", "[[kapazitaetsvisualisierung-produktion]]"]
confidence: medium
last_updated: 2026-04-18
---

Die **Sekundärbedarfsplanung** erweitert die Bestandsoptimierung auf mehrstufige Produktionsstrukturen.

Hierzu werden Stücklisten aus dem ERP-System importiert und innerhalb von ADD*ONE BO aufgelöst. Ziel ist es, Bedarfe für Komponenten und Zukaufteile frühzeitig zu erkennen.

Eigenschaften des Verfahrens:

- tägliche Bestimmung von Dispositionsstufen
- Unterstützung beliebig tiefer Fertigungsstrukturen
- Berücksichtigung von Gültigkeitszeiträumen von Stücklisten

Während der Planung werden alle Sekundärbedarfe aus übergeordneten Produktionsstufen berücksichtigt. Dadurch kann die Beschaffung von Komponenten rechtzeitig erfolgen.

Das System prüft außerdem die **Machbarkeit von Planaufträgen**. Falls benötigte Komponenten nicht rechtzeitig verfügbar sind, werden entsprechende Warnungen ausgegeben und problemverursachende Materialien identifiziert.

confidence: medium
