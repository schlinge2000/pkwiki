---
title: Hybrid-Parallelisierung (MPI + OpenMP)
type: concept
domain: tech
sources: [raw/slides/Berechnugslauf.pptx]
related: ["[[berechnungslauf]]", "[[artikelgruppierung]]", "[[hpc-cluster]]"]
confidence: medium
last_updated: 2026-04-17
---

Hybrid-Parallelisierung kombiniert zwei Ebenen:

- Distributed-Memory-Prozessparallelisierung mit MPI
- Shared-Memory-Threadparallelisierung mit OpenMP

Im Kontext des [[berechnungslauf]] ergibt sich:

- MPI-Prozesse arbeiten auf Artikelgruppen
- jeder MPI-Prozess nutzt OpenMP mit einem Thread pro physischem Kern
- Vermeidung von NUMA-Effekten

Dies ermöglicht eine skalierbare Berechnung über große Datenmengen, insbesondere im [[hpc-cluster]].
