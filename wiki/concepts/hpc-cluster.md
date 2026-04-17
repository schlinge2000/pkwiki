---
title: High-Performance-Cluster (HPC)
type: concept
domain: tech
sources: [raw/slides/Berechnugslauf.pptx]
related: ["[[berechnungslauf]]", "[[hybrid-parallelisierung]]", "[[weltsystem-architektur]]"]
confidence: medium
last_updated: 2026-04-17
---

Der HPC-Cluster ist die technische Basis des neuen Berechnungslaufs.

Wesentliche Merkmale:

- verteilte Ausführung mit MPI
- Threadparallelisierung pro Prozess mit OpenMP
- InfiniBand-Netzwerk mit hoher Bandbreite
- parallele Lese- und Schreibzugriffe auf Datenbanken

Die Architektur ermöglicht die geforderte Skalierbarkeit im Kontext eines globalen [[weltsystem-architektur]].
