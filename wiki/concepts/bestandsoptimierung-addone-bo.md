---
title: ADD*ONE Bestandsoptimierung (BO)
type: concept
domain: tech
sources: [raw/pdfs/Leistungsbeschreibung BO 2024.pdf]
related: ["[[inform-gmbh]]", "[[bedarfsprognose-addone-bo]]", "[[management-by-exception-disposition]]", "[[sicherheitsbestand-servicegrad-berechnung]]", "[[servicegradorientierte-sporadendisposition]]"]
confidence: medium
last_updated: 2026-04-18
---

**ADD*ONE Bestandsoptimierung (ADD*ONE BO)** ist eine Dispositionssoftware zur Optimierung von Fremdbeschaffung und Eigenfertigung. Ziel ist es, Bestände, Bestellmengen und Produktionsentscheidungen datenbasiert zu steuern.

Die Software unterstützt Disponenten durch:

- automatische Prognosen zukünftiger Bedarfe
- Berechnung kostenoptimaler Bestellvorschläge
- Priorisierung von Handlungsbedarf
- Simulation alternativer Dispositionsentscheidungen

ADD*ONE BO arbeitet als **Add‑on zu einem bestehenden ERP-System**. Das ERP bleibt das datenführende System. Stamm‑, Bestands‑ und Bewegungsdaten werden regelmäßig importiert, während Planungsentscheidungen (z. B. Bestellungen oder Produktionsaufträge) wieder in das ERP exportiert werden.

Ein typischer Ablauf besteht aus:

1. Datenimport aus dem ERP
2. nächtlicher Berechnungslauf der Planung
3. Erstellung von Prognosen und Bestellvorschlägen
4. Bearbeitung durch Disponenten oder automatische Freigabe

Die Software kombiniert mehrere Planungsansätze:

- [[bedarfsprognose-addone-bo]] zur Vorhersage zukünftiger Nachfrage
- kostenbasierte Optimierung von Bestellmengen
- [[servicegradorientierte-sporadendisposition]] für unregelmäßige Nachfrage
- dispositive Unterstützung nach [[management-by-exception-disposition]]

Neben der Basiskomponente existieren optionale Erweiterungen, etwa:

- [[standortuebergreifende-planung-bestand]]
- [[sekundaerbedarfsplanung]]
- [[kapazitaetsvisualisierung-produktion]]

confidence: medium
