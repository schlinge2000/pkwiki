---
title: From News to Forecast — Integrating Event Analysis in LLM-Based Time Series Forecasting with Reflection
type: source
source_file: raw/pdfs/2409.17515v3.pdf
source_type: paper
date: 2024-12-01
key_concepts: ["[[news-integrierte-zeitreihenprognose]]", "[[llm-zeitreihen-tokenisierung]]", "[[news-reasoning-agent]]", "[[evaluation-agent-reflexion]]", "[[kontextuelle-daten-zeitreihenprognose]]"]
last_updated: 2026-04-17
---

Diese Arbeit präsentiert ein Framework zur **Integration von Nachrichtenereignissen (News) in Zeitreihenprognosen mithilfe von Large Language Models (LLMs)**. Ziel ist es, externe Ereignisse wie politische Entwicklungen, Wetterereignisse oder wirtschaftliche Nachrichten systematisch mit numerischen Zeitreihen zu verknüpfen.

Der Ansatz kombiniert drei zentrale Komponenten:

- ein **LLM-basiertes Forecasting-Modul**, das Zeitreihen als Token-Sequenzen modelliert
- einen **Reasoning-Agent**, der relevante Nachrichten aus großen Datenmengen filtert
- einen **Evaluation-Agent**, der Prognosefehler analysiert und die Nachrichtenlogik iterativ verbessert

Damit wird ein Forecasting-System geschaffen, das sowohl **numerische Daten als auch unstrukturierte Textinformationen** verarbeitet.

## Zentrale Idee

Traditionelle Zeitreihenmodelle analysieren ausschließlich historische numerische Daten. Dadurch reagieren sie schlecht auf **exogene Ereignisse** wie:

- politische Entscheidungen
- Naturkatastrophen
- wirtschaftliche Schocks
- gesellschaftliche Veränderungen

Das Paper schlägt vor, solche Ereignisse über **News-Datenbanken** zu integrieren und LLMs zur semantischen Interpretation zu nutzen.

Der Forecast wird als bedingte Wahrscheinlichkeit modelliert:

P(x_{t+1} | x_{0:t}, E)

wobei **E Ereignisinformation aus Nachrichten** darstellt.

## Datenquellen

Für Experimente werden Zeitreihen aus mehreren Domänen verwendet:

- Stromnachfrage
- Wechselkurse
- Verkehrsdaten
- Bitcoinpreise

Die News stammen u.a. aus:

- [[gdelt-project]]
- Yahoo News
- NewsCorp Australia

Zusätzliche Kontextdaten:

- Wetterdaten (OpenWeatherMap)
- Kalender- und Feiertagsinformationen
- ökonomische Indikatoren

## Ergebnisse

Experimente zeigen:

- Gefilterte News verbessern Forecast-Genauigkeit signifikant
- Ungefilterte News verschlechtern Ergebnisse
- Iterative Agent-Reflexion verbessert die Auswahl relevanter Ereignisse

Die Methode erreicht bessere Ergebnisse als mehrere etablierte Modelle, darunter:

- PatchTST
- Informer
- Autoformer
- TimesNet

## Einschränkungen

Die Methode funktioniert besonders gut in Domänen mit starkem Einfluss menschlicher Aktivitäten, z. B.:

- Energieverbrauch
- Finanzmärkte

Weniger geeignet ist sie für physikalische Systeme ohne menschliche Einflussfaktoren.

Zusätzlich ist die Methode durch **Token-Limits von LLMs** begrenzt, wodurch lange Zeitreihen schwer vollständig verarbeitet werden können.

## Relevante Entitäten

- [[llama2]]
- [[gpt-4-turbo]]
- [[gdelt-project]]
