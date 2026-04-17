---
title: In-Context Learning for Optimization Interfaces
type: concept
domain: ai
sources: [raw/pdfs/LLMs_SCM_Optim 1 1.pdf]
related: ["[[optiguide-framework]]", "[[llms-supply-chain-optimization]]"]
confidence: medium
last_updated: 2026-04-17
---

**In-Context Learning (ICL)** wird im Paper als zentrale Methode genutzt, um [[large-language-models]] für Optimierungsanwendungen anzupassen.

Statt das Modell zu fine-tunen, werden Beispiele direkt im Prompt bereitgestellt. Diese Beispiele enthalten typischerweise Paare aus:

- Nutzerfrage
- zugehörigem Code oder Modellanpassung

Das LLM lernt dadurch während der Inferenz, wie ähnliche Fragen zu beantworten sind.

### Gründe für ICL

Das Paper nennt mehrere Gründe für die Wahl dieses Ansatzes:

- Fine-Tuning großer Modelle ist teuer
- Hosting erfordert GPU-Infrastruktur
- viele Anwendungen benötigen flexible Anpassungen

ICL ermöglicht es, ein Modell schnell für eine spezifische Domäne zu konfigurieren.

### Beispiel

Ein Prompt kann enthalten:

Frage → Code-Beispiel

"Ist es möglich, Roastery 1 ausschließlich für Cafe 2 zu verwenden?"

→ Code, der entsprechende Nebenbedingungen im Optimierungsmodell ergänzt.

Auf Basis dieser Beispiele generiert das LLM Code für neue Fragen.

### Einschränkungen

Die Methode ist durch die maximale Tokenlänge des Prompts begrenzt. Deshalb müssen Beispiele und Dokumentation sorgfältig ausgewählt werden.