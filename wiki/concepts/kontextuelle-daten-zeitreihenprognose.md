---
title: Kontextuelle Daten in der Zeitreihenprognose
type: concept
domain: ai
sources: [raw/pdfs/2409.17515v3.pdf]
related: ["[[news-integrierte-zeitreihenprognose]]", "[[llm-zeitreihen-tokenisierung]]"]
confidence: medium
last_updated: 2026-04-17
---

**Kontextuelle Daten in der Zeitreihenprognose** bezeichnen zusätzliche Informationsquellen, die über historische Zeitreihen hinausgehen und die Prognosegenauigkeit verbessern können.

In der Arbeit [[from-news-to-forecast-llm-event-analysis]] werden mehrere Kontextarten integriert.

## Beispiele für Kontextdaten

- Nachrichten über politische oder wirtschaftliche Ereignisse
- Wetterinformationen
- Kalender- und Feiertagsdaten
- ökonomische Indikatoren

Diese Daten liefern Erklärungen für Veränderungen in Zeitreihen.

Beispiel Stromverbrauch:

Ein Anstieg der Nachfrage kann verursacht werden durch

- Hitzewellen
- große Veranstaltungen
- Infrastrukturprobleme

## Integration in LLMs

Die Kontextdaten werden als Text in Prompts integriert.

Beispiel:

"Weather on historical dates: the lowest temperature is 292.01; the highest temperature is 298.07; the humidity is 94." 

Damit kann das Modell mehrere Informationsquellen gleichzeitig berücksichtigen.

## Vorteil

Die Kombination aus

- numerischen Daten
- Textinformationen

ermöglicht ein **kontextbewusstes Forecasting**, das besser auf reale Ereignisse reagieren kann.
