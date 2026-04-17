---
title: Explainable Optimization
type: concept
domain: ai
sources: [raw/pdfs/LLMs_SCM_Optim 1 1.pdf]
related: ["[[optiguide-framework]]", "[[llms-supply-chain-optimization]]", "[[what-if-analysis-optimization]]"]
confidence: medium
last_updated: 2026-04-17
---

**Explainable Optimization** beschreibt Ansätze, die Entscheidungen aus mathematischen Optimierungsmodellen für Menschen verständlich machen.

In komplexen Systemen – etwa in der [[supply-chain-optimization]] – entstehen Entscheidungen aus großen Modellen mit vielen Variablen, Nebenbedingungen und Zielgrößen. Diese Modelle wirken für Nutzer oft wie eine „Black Box“.

Typische Fragen von Anwendern sind:

- Warum wurde ein bestimmter Lieferant gewählt?
- Wie setzen sich die Kosten einer Lösung zusammen?
- Was passiert, wenn Nachfrage oder Kapazitäten geändert werden?

### Herausforderungen

Die Erklärung solcher Entscheidungen ist schwierig, weil:

- Modelle oft sehr groß sind
- Entscheidungen aus vielen Wechselwirkungen entstehen
- Nutzer häufig keine Optimierungsexpertise besitzen

Traditionell erfordert die Analyse solcher Fragen mehrere Schritte:

1. Business‑Operator stellt eine Frage
2. Programmmanager oder Analysten interpretieren sie
3. Engineers schreiben zusätzliche Analyse‑ oder Modellcode
4. Optimierung wird erneut ausgeführt

Dieser Prozess kann zeitaufwendig sein.

### Rolle von LLMs

Frameworks wie [[optiguide-framework]] nutzen [[large-language-models]], um diesen Prozess zu automatisieren.

LLMs können:

- Nutzerfragen interpretieren
- Modellanpassungen generieren
- Ergebnisse erklären

Dadurch wird eine interaktive und verständliche Analyse von Optimierungssystemen möglich.