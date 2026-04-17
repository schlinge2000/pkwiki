---
title: News-integrierte Zeitreihenprognose
type: concept
domain: ai
sources: [raw/pdfs/2409.17515v3.pdf]
related: ["[[llm-zeitreihen-tokenisierung]]", "[[news-reasoning-agent]]", "[[evaluation-agent-reflexion]]"]
confidence: medium
last_updated: 2026-04-17
---

Die **news-integrierte Zeitreihenprognose** beschreibt einen Ansatz, bei dem externe Ereignisse aus Nachrichtenquellen systematisch in Zeitreihenmodelle integriert werden.

Traditionelle Forecasting-Modelle nutzen ausschließlich historische numerische Daten. Dadurch können sie strukturelle Veränderungen oder unerwartete Ereignisse schlecht abbilden.

Beispiele solcher Ereignisse:

- politische Entscheidungen
- wirtschaftliche Krisen
- Naturkatastrophen
- technologische Entwicklungen
- gesellschaftliche Veränderungen

Nachrichten liefern Kontextinformationen, die solche Veränderungen erklären können.

## Motivation

Zeitreihenmodelle gehen oft implizit davon aus, dass:

- zukünftige Muster ähnlich zu historischen Mustern sind
- externe Faktoren nicht explizit modelliert werden müssen

Diese Annahmen brechen bei **externen Schocks**.

News-Daten liefern dagegen:

- Echtzeitinformationen über Ereignisse
- qualitative Hinweise über Ursachen von Veränderungen
- Kontext über menschliches Verhalten

## Umsetzung mit LLMs

Die Arbeit [[from-news-to-forecast-llm-event-analysis]] nutzt **Large Language Models**, um Nachrichten automatisch zu analysieren und mit Zeitreihen zu verknüpfen.

Das Modell berechnet Forecasts als:

P(x_{t+1} | x_{0:t}, E)

wobei

- x historische Zeitreihendaten
- E Ereignisinformation aus Nachrichten

ist.

## Wichtige Herausforderung

Nicht jede Nachricht ist relevant. Zu viele oder irrelevante Nachrichten können die Prognose verschlechtern.

Daher wird ein **Agentensystem zur Nachrichtenfilterung** eingesetzt:

- [[news-reasoning-agent]] wählt relevante News
- [[evaluation-agent-reflexion]] verbessert die Auswahl iterativ
