---
title: Transformer-Modelle
type: concept
domain: ai
sources: [raw/slides/Sprache_vs_Wirtschaftsprozesse.pptx]
related: ["[[self-attention-mechanismus]]", "[[embeddings-semantik]]", "[[zeitreihen-transformer]]", "[[llm-semantischer-kontext]]", "[[christian-miessen]]"]
confidence: medium
last_updated: 2026-04-17
---
Transformer-Modelle bilden die Grundlage moderner Large Language Models (LLMs) wie GPT-3/4 oder BERT. Laut der Präsentation sind sie erfolgreich, weil sie „mit Semantik rechnen“. Ihr zentraler Baustein ist Self-Attention, der erlaubt, semantische Zusammenhänge über große Distanzen innerhalb eines Satzes zu erfassen.

Wichtige Eigenschaften:
- Parallele Verarbeitung statt Sequenzen verarbeiten wie in RNN/LSTM.
- Nutzung von Position Encodings, um Satzstellung und Grammatik abzubilden.
- Effiziente Nutzung von GPU-Ressourcen.

Transformer bilden die Grundlage dafür, dass moderne Modelle komplexe Zusammenhänge verstehen können – auch über numerische Daten hinaus.
