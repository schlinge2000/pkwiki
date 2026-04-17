---
title: LLM-Zeitreihen-Tokenisierung
type: concept
domain: ai
sources: [raw/pdfs/2409.17515v3.pdf]
related: ["[[news-integrierte-zeitreihenprognose]]", "[[kontextuelle-daten-zeitreihenprognose]]", "[[llama2]]"]
confidence: medium
last_updated: 2026-04-17
---

Die **LLM-Zeitreihen-Tokenisierung** beschreibt einen Ansatz, bei dem numerische Zeitreihen als Token-Sequenzen dargestellt werden, sodass sie von Large Language Models verarbeitet werden können.

Die Grundidee ist, Zeitreihenforecasting als **Next-Token-Prediction** zu formulieren – analog zur Textgenerierung.

Beispiel:

Eine Zahlenreihe

123, 456

wird tokenisiert als

"1" "2" "3" "," "4" "5" "6"

Das Modell berechnet anschließend die Wahrscheinlichkeit der nächsten Tokens:

P(x_{t+1} | x_{0:t})

## Vorteile

Durch diese Darstellung können LLMs ihre bestehenden Fähigkeiten nutzen:

- Sequenzmodellierung
- Self-Attention
- Kontextintegration

Dadurch können sie sowohl

- numerische Zeitreihen
- Textinformationen

in einem gemeinsamen Modell verarbeiten.

## Erweiterung mit Kontext

Im Framework aus [[from-news-to-forecast-llm-event-analysis]] wird die Eingabe erweitert um:

- Nachrichtenereignisse
- Wetterdaten
- Kalenderinformationen
- ökonomische Indikatoren

Diese Informationen werden ebenfalls als Text in den Prompt integriert.

## Training

Das Modell wird mittels **Instruction-Finetuning** trainiert.

Zur effizienten Anpassung wird [[lora]] (Low-Rank Adaptation) eingesetzt, wodurch nur ein kleiner Teil der Modellparameter aktualisiert wird.
