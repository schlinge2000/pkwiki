---
title: Message Passing Interface (MPI)
type: concept
domain: tech
sources: ["raw/slides/HPC Übergabe.pptx"]
related: ["[[verteilte-systeme]]", "[[hpc-addone]]"]
confidence: high
last_updated: 2026-04-17
---
MPI ist ein Standard für verteiltes Rechnen über viele Prozesse hinweg.

Wesentliche Elemente aus der Präsentation:
- Jeder Prozess führt den gleichen Code aus
- Prozesse können ihre Prozess-ID abfragen (rank)
- world_size beschreibt die Anzahl laufender Prozesse
- Synchronisierung via MPI_Barrier
- Einsatz zum parallelen Abarbeiten von Artikeln in add*ONE

Kommando zum Ausführen:
`mpiexec.exe -n 4 MultiProcessLauncher.exe --help`
