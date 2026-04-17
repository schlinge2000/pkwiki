---
title: Evaluation Agent mit Reflexion
type: concept
domain: ai
sources: [raw/pdfs/2409.17515v3.pdf]
related: ["[[news-reasoning-agent]]", "[[news-integrierte-zeitreihenprognose]]"]
confidence: medium
last_updated: 2026-04-17
---

Der **Evaluation Agent mit Reflexion** ist eine Komponente zur Verbesserung der Nachrichtenlogik in LLM-basierten Forecasting-Systemen.

Er analysiert Prognosefehler und versucht zu erkennen, ob wichtige Ereignisse in den Trainingsdaten übersehen wurden.

## Motivation

Der [[news-reasoning-agent]] filtert Nachrichten basierend auf semantischer Relevanz. Dabei können dennoch wichtige Ereignisse fehlen.

Der Evaluation-Agent überprüft daher:

- Prognosefehler
- tatsächliche Zeitreihenwerte
- verwendete Nachrichten
- verfügbare historische Nachrichten

## Arbeitsweise

Der Prozess besteht aus mehreren Schritten:

1. Vergleich von Vorhersagen und realen Werten
2. Identifikation ungewöhnlicher Fehler
3. Suche nach möglicherweise übersehenen Nachrichten
4. Aktualisierung der Nachrichten-Auswahllogik

Dieser Prozess erzeugt eine **iterative Feedback-Schleife**.

## Iteratives Training

Die Pipeline funktioniert typischerweise so:

1. Reasoning-Agent wählt Nachrichten
2. Modell wird trainiert
3. Evaluation-Agent analysiert Fehler
4. Nachrichtenlogik wird aktualisiert

Dieser Zyklus wird mehrfach wiederholt, bis eine stabile Auswahlstrategie entsteht.

Experimente zeigen, dass bereits **zwei Iterationen signifikante Verbesserungen** der Prognoseleistung erzeugen können.
