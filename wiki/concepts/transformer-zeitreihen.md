---
title: Transformer-Modelle für Zeitreihen
type: concept
domain: ai
sources: [raw/slides/Sprache_vs_Wirtschaftprozesse.pptx, raw/slides/Sprache_vs_Wirtschaftprozesse_englisch.pptx]
related: ["[[foundation-models]]", "[[absatzprognose]]", "[[zeitreihen]]"]
confidence: high
last_updated: 2026-04-17
---

# Transformer-Modelle für Zeitreihen

Übertragung der Transformer-Architektur (bekannt aus GPT/BERT) auf die Vorhersage von Wirtschaftsprozessen und Zeitreihen. Kernthese: Sprachmodelle rechnen mit Semantik — dasselbe Prinzip lässt sich auf Nachfrageverhalten übertragen.

## Vom Sprachmodell zum Zeitreihenmodell

| Sprache | Zeitreihe |
|---|---|
| Wörter in Sätzen | Zeitpunkte in Zeitreihen |
| Semantische Ähnlichkeit | Verhaltensähnlichkeit von Artikeln |
| Attention: Welche Wörter sind relevant? | Attention: Welche historischen Muster sind relevant? |
| Training auf Milliarden Texten | Training auf Millionen Zeitreihen |

## Evolutionslinie der Prognosemodelle

```
1900s   AR (AutoRegressive)
1970s   Exponentielle Glättung, ARIMA
2000s   ARCH, LSTM/RNN, Deep Learning
2017    "Attention is All You Need" (Vaswani et al.) → Transformer
2020s   Temporal Fusion Transformers (TFT), N-BEATS
2023+   Spezialisierte Transformer-Modelle
2025+   Foundation Models für Zeitreihen (1 Modell für alle Zeitreihen)
```

Paradigmenwechsel: **1 Modell pro Zeitreihe → 1 Modell für alle Zeitreihen**

## Technische Bausteine (Transformer)

- **Self-Attention:** Abfrage (wie wichtig sind andere Wörter?), Schlüssel (Bewertungsgrundlage), Wert (Information des Wortes)
- **Parallele Verarbeitung:** Self-Attention läuft parallel → GPU-Einsatz möglich
- **Position Encoding:** Reihenfolge/Grammatik kodieren
- **Embedding:** Ähnliche Konzepte → ähnliche Vektoren

## Warum numerische Modelle allein scheitern

- **Numerische Engführung:** Nur explizit definierte Variablen, kein wirtschaftlicher Kontext
- **Modelllücke:** Kein rein numerisches Modell kann die Realität vollständig abbilden — semantisches Verständnis fehlt per Definition

## INFORM Foundation Model — Technische Stärken

- Flexibel trainierbar für verschiedene Prognosehorizonte
- Versteht exogene Variablen (temporale Effekte)
- Nutzt statische Attribute für Beziehungen zwischen Zeitreihen
- Kann markierte Sequenzen ignorieren (Stockouts, Krisen)
- Echtes Prozessverständnis → Transfer auf neue Fälle

## Ausblick: LLM + Zeitreihen

- LLMs integrieren semantischen Kontext direkt in Prognosemodelle
- Textereignisse müssen nicht in numerische Variablen übersetzt werden
- Gemischte Eingaben: numerische Daten + Kontext + News + Nutzereingaben
- Nachrichten erklären Vorhersagen → interpretierbare AI
