---
title: Self-Attention Mechanismus
type: concept
domain: ai
sources: [raw/slides/Sprache_vs_Wirtschaftprozesse.pptx]
related: ["[[transformer-modelle]]", "[[embeddings-semantik]]"]
confidence: medium
last_updated: 2026-04-17
---
Self-Attention ist der Kernbaustein moderner Transformer-Architekturen. Jedes Wort wird über drei Vektoren repräsentiert (Query, Key, Value). Dadurch bewertet ein Modell, welche anderen Wörter für das aktuelle Wort relevant sind.

Funktionen:
- Query: fragt die Relevanz anderer Token ab.
- Key: bestimmt, wie relevant ein Token für andere ist.
- Value: überträgt die eigentliche Information.

Self-Attention erklärt, warum Transformer lange Abhängigkeiten verstehen können, im Gegensatz zu RNN/LSTM.
