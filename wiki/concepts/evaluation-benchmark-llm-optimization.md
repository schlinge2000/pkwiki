---
title: Evaluation Benchmark for LLM-Based Optimization Interfaces
type: concept
domain: ai
sources: [raw/pdfs/LLMs_SCM_Optim 1 1.pdf]
related: ["[[optiguide-framework]]", "[[llms-supply-chain-optimization]]"]
confidence: medium
last_updated: 2026-04-17
---

Das Paper entwickelt einen **Benchmark zur Evaluation von LLMs in Optimierungsinterfaces**.

Der Benchmark misst, wie gut ein LLM Fragen über Optimierungsmodelle beantworten kann, insbesondere wenn es Code generieren muss, der ein Modell modifiziert oder analysiert.

### Szenarien

Der Benchmark umfasst mehrere Optimierungsprobleme, darunter:

- Facility Location
- Multi-Commodity Network Flow
- Workforce Assignment
- Traveling Salesman Problem
- Coffee Distribution Beispiel

Die Modelle werden typischerweise mit dem [[gurobi-optimizer]] gelöst.

### Methodik

Die Evaluation basiert auf einer Reihe von Frage-Sets.

Ein Modell besteht einen Test nur dann, wenn **alle Fragen eines Sets korrekt beantwortet werden**. Dies verhindert, dass ein Modell teilweise richtige Antworten erhält, obwohl einzelne entscheidende Schritte falsch sind.

### Metrik

Die Accuracy wird über Szenarien, Experimente und Frage-Sets gemittelt.

### Ergebnisse

Die Experimente zeigen:

- GPT‑4 erreicht durchschnittlich etwa **93 % Genauigkeit** in In‑Distribution Tests
- Leistung sinkt bei Out‑of‑Distribution Fragen
- mehr Beispiele im Prompt verbessern die Performance

Die Autoren schlagen den Benchmark als Grundlage für zukünftige Forschung zu LLM‑gestützten Optimierungssystemen vor.