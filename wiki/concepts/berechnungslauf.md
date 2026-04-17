---
title: BOXX Berechnungslauf
type: concept
domain: tech
sources: [raw/slides/Berechnugslauf.pptx]
related: ["[[rbpt-anforderungen]]", "[[weltsystem-architektur]]", "[[hybrid-parallelisierung]]", "[[artikelgruppierung]]", "[[hpc-cluster]]"]
confidence: medium
last_updated: 2026-04-17
---

Der BOXX-Berechnungslauf umfasst die tägliche, bisher stark sequentielle Verarbeitung großer Artikeldatenmengen in der +ONE-Systemlandschaft. Die Präsentation beschreibt zentrale Herausforderungen der bisherigen Architektur:

- fehlende Skalierbarkeit oberhalb von 12 Threads
- lange Downtime von ca. 12 Stunden
- technische Beschränkung der verarbeitbaren Artikelmenge
- steigende Last durch ein geplantes [[weltsystem-architektur]] (globale Datenbank)

Die Vision des neuen Berechnungslaufs ist:

- Downtime nur noch wenige Minuten pro Artikel
- hochskalierbare verteilte Architektur (Cluster)
- Kombination aus Prozess- und Threadparallelisierung ([[hybrid-parallelisierung]])
- Einsatz von Artikelgruppen zur technischen und logischen Strukturierung ([[artikelgruppierung]])

Der Berechnungslauf wird somit zu einem HPC-gestützten System ([[hpc-cluster]]), das wesentlich größere Datenvolumina bewältigt.
