---
title: Leistungsbeschreibung BO 2024
type: source
source_file: raw/pdfs/Leistungsbeschreibung BO 2024.pdf
source_type: doc
date: 2024-11-01
key_concepts: ["[[bestandsoptimierung-addone-bo]]", "[[bedarfsprognose-addone-bo]]", "[[management-by-exception-disposition]]", "[[sicherheitsbestand-servicegrad-berechnung]]", "[[servicegradorientierte-sporadendisposition]]", "[[standortuebergreifende-planung-bestand]]", "[[sekundaerbedarfsplanung]]", "[[kapazitaetsvisualisierung-produktion]]"]
last_updated: 2026-04-18
---

Diese Quelle beschreibt die Leistungsbeschreibung der Software **ADD*ONE Bestandsoptimierung (ADD*ONE BO)** der [[inform-gmbh]]. Das Dokument erläutert Architektur, Kernfunktionen, zusätzliche Module sowie organisatorische Rahmenbedingungen für Betrieb und Support.

Kernidee der Software ist die **Optimierung von Beschaffung und Produktion** durch automatisierte Dispositionsentscheidungen, Prognosen und kostenbasierte Bestandsplanung.

Wesentliche Funktionsbereiche:

- Prognose und Bedarfsplanung auf Basis historischer Verbrauchsdaten
- Disposition nach dem Prinzip [[management-by-exception-disposition]]
- Kostenoptimierte Bestellvorschläge und adaptive Sicherheitsbestände
- Servicegradorientierte Verfahren für sporadische Nachfrage
- Simulation und Szenarioanalyse für dispositive Entscheidungen
- Integration in bestehende ERP-Systeme

Architektonische Eigenschaften:

- ADD*ONE BO ist ein **ERP-Add-on** und kein datenführendes System
- Daten werden regelmäßig aus dem ERP importiert (typisch: nächtlicher Lauf)
- Planungsergebnisse wie Bestellvorschläge werden wieder an das ERP exportiert

Das System umfasst eine **Basisfunktionalität** und eine Reihe optionaler Erweiterungen, darunter:

- [[standortuebergreifende-planung-bestand]]
- [[sekundaerbedarfsplanung]]
- [[kapazitaetsvisualisierung-produktion]]
- Liefervorschau und Auftragsprognosen
- Multi‑ERP‑Integration

Zusätzlich beschreibt das Dokument:

- Kennzahlensysteme und [[abc-analysen]]
- Beschaffungslogistik und Kontraktmanagement
- Support- und Betriebsprozesse
- Mitwirkungspflichten des Kunden beim Betrieb der Software

confidence: high
