---
title: Large Language Models for Supply Chain Optimization

type: source
source_file: raw/pdfs/LLMs_SCM_Optim 1 1.pdf
source_type: paper
date: 2023-07-13
key_concepts: ["[[optiguide-framework]]", "[[llms-supply-chain-optimization]]", "[[explainable-optimization]]", "[[what-if-analysis-optimization]]", "[[in-context-learning-optimization-interfaces]]", "[[evaluation-benchmark-llm-optimization]]"]
last_updated: 2026-04-17
---

Dieses Paper untersucht, wie [[large-language-models]] eingesetzt werden können, um Entscheidungsprozesse in der [[supply-chain-optimization]] verständlicher und zugänglicher zu machen. Die Autoren schlagen ein Framework namens [[optiguide-framework]] vor, das natürliche Sprache nutzt, um komplexe Optimierungssysteme zu erklären und interaktive Analysen zu ermöglichen.

Zentrales Problem: Moderne Supply-Chain-Systeme verwenden komplexe mathematische Optimierungsmodelle (z. B. Mixed Integer Programming). Die resultierenden Entscheidungen sind für Business-Operatoren schwer nachvollziehbar, was zu Kommunikationsaufwand zwischen Planern, Data Scientists und Engineers führt.

Der vorgeschlagene Ansatz kombiniert LLMs mit klassischen Optimierungssolvern. Statt Optimierungsprobleme direkt mit LLMs zu lösen, werden LLMs als Schnittstelle verwendet:

- Übersetzen von Nutzerfragen in Code
- Modifizieren von Optimierungsmodellen für What-if-Analysen
- Interpretieren der Solver-Ergebnisse
- Generieren verständlicher Antworten

Das System wird anhand eines Frameworks namens [[optiguide-framework]] implementiert und auf verschiedene Optimierungsprobleme getestet. Die Evaluation zeigt eine durchschnittliche Genauigkeit von etwa 93 % bei Nutzung von GPT‑4.

Ein reales Deployment wurde im Kontext der [[microsoft-azure]] Supply Chain durchgeführt, insbesondere für die Serverbereitstellung in Rechenzentren.

Wichtige Beiträge des Papers:

- Architektur für LLM-gestützte Erklärung von Optimierungsentscheidungen
- Integration von LLM-Codegenerierung mit Optimierungssolvern
- Benchmark zur Evaluation von LLM‑gestützten Optimierungsinterfaces
- Praxisbeispiel aus der Cloud-Infrastrukturplanung

Das Paper argumentiert, dass LLMs kurzfristig besonders wertvoll für Explainability und Interaktion sind, während eine direkte Optimierung durch LLMs aktuell nicht praktikabel ist.