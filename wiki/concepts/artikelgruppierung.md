---
title: Artikelgruppierung und Aufgabenbildung
type: concept
domain: tech
sources: [raw/slides/Berechnugslauf.pptx]
related: ["[[berechnungslauf]]", "[[hybrid-parallelisierung]]"]
confidence: medium
last_updated: 2026-04-17
---

Die Artikelgruppierung bildet die logische und technische Grundlage für den neuen skalierbaren Berechnungslauf.

Zentrale Elemente der Gruppierung:

- Netzwerkstufe
- Stücklistenabhängigkeiten
- Berechnungszeitfenster
- weitere Prioritäten

Die Gruppen ermöglichen:

- entkoppelte Berechnungseinheiten für MPI-Prozesse
- lokal auflösbare Abhängigkeiten
- parallele Verarbeitung und Lastverteilung gemäß [[hybrid-parallelisierung]]
