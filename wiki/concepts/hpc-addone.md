---
title: HPC für add*ONE
type: concept
domain: tech
sources: ["raw/slides/HPC Übergabe.pptx"]
related: ["[[rbpt-anforderungen]]", "[[verteilte-systeme]]", "[[microsoft-hpc-pack]]", "[[mpi]]", "[[aufgabenverteilung-hpc]]"]
confidence: medium
last_updated: 2026-04-17
---
Dieses Konzept beschreibt die Einführung von HPC (High Performance Computing) für die add*ONE Plattform. Hintergrund sind wachsende Datenmengen und Skalierungsprobleme der bisherigen Architektur.

Kernprobleme:
- steigende Datenmengen durch Konsolidierung zu einem globalen System
- fehlende Skalierbarkeit der bestehenden add*ONE-Architektur
- technische Beschränkung der Artikelmenge
- keine zusätzliche Beschleunigung ab ca. 12 Threads
- bisherige Downtime des Nachtlaufs ca. 12 Stunden

Ziele der Umstellung:
- Downtime-Reduktion auf <4h
- verteilte Berechnungsarchitektur
- optimale Nutzung von Multi-Core- und Multi-Node-Umgebungen

Der Ansatz basiert auf Distributed Computing, dem Einsatz von Microsoft HPC Pack und der Einführung von MPI für die Prozessverteilung.
