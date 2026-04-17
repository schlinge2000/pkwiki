---
title: LLMs in Supply Chain Optimization
type: concept
domain: ai
sources: [raw/pdfs/LLMs_SCM_Optim 1 1.pdf]
related: ["[[optiguide-framework]]", "[[explainable-optimization]]", "[[what-if-analysis-optimization]]"]
confidence: medium
last_updated: 2026-04-17
---

Der Einsatz von [[large-language-models]] in der [[supply-chain-optimization]] zielt darauf ab, komplexe Entscheidungsmodelle verständlicher und interaktiver zu machen.

Supply-Chain-Systeme basieren häufig auf komplexen mathematischen Optimierungsproblemen, beispielsweise:

- Facility Location
- Netzwerkflussoptimierung
- Inventory Planning
- Routing

Diese Probleme werden häufig mit **Mixed Integer Programming (MIP)** oder heuristischen Verfahren gelöst.

### Problem

Obwohl Optimierungssysteme Entscheidungen automatisieren können, bleibt ihre Interpretation schwierig. Business‑Operatoren müssen häufig mit Data Scientists oder Engineers zusammenarbeiten, um zu verstehen:

- warum bestimmte Entscheidungen getroffen wurden
- welche Kostenstruktur hinter einer Lösung steckt
- wie sich Änderungen im System auswirken

### Rolle von LLMs

LLMs können als **natürliche Schnittstelle zu Optimierungsmodellen** dienen:

- Übersetzung natürlicher Fragen in Modellanpassungen
- Generierung von Analysecode
- Erklärung von Optimierungsergebnissen

Ein typisches Beispiel:

„Was passiert, wenn Nachfrage in Region X um 10 % steigt?“

Das System kann automatisch:

1. die Modellparameter ändern
2. das Optimierungsproblem neu lösen
3. die Kostenänderung erklären

### Einschränkungen

Das Paper betont, dass LLMs derzeit **nicht geeignet sind**, große kombinatorische Optimierungsprobleme selbst zu lösen. Stattdessen werden sie als Interface zu klassischen Solver-Systemen eingesetzt.