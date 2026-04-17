---
title: Prognose der Anlaufphase von Ersatzteilen
type: concept
domain: ai
sources: [raw/pdfs/Interview_Zusammenfassung_Jungheinrich.pdf]
related: ["[[erstbevorratung-ersatzteile]]", "[[demand-forecasting]]", "[[wahrscheinlichkeitsbasierte-prognosen]]", "[[aehnlichkeitsanalyse-ersatzteile]]"]
confidence: medium
last_updated: 2026-04-17
---

Die **Anlaufphase von Ersatzteilen** beschreibt den Zeitraum nach Einführung eines neuen Produkts oder Bauteils, in dem erstmals Ersatzteilbedarf entsteht und sich Nachfrageprofile entwickeln.

In dieser Phase existieren für das neue Teil noch **keine eigenen Verbrauchsdaten**. Prognosen müssen daher indirekt erfolgen.

## Datenbasis

Im Interview mit [[jungheinrich]] wird beschrieben, dass Prognosen für neue Teile auf Basis von:

- historischen Verbrauchsdaten alter Teile
- strukturellen Ähnlichkeiten zwischen Komponenten
- Markteinführungs- bzw. Absatzdaten

aufgebaut werden können.

Ein möglicher Ansatz besteht darin, **historische Anlaufphasen vergleichbarer Teile** als Trainingsdaten für Modelle zu nutzen.

## Ziel

Die Prognose der Anlaufphase dient insbesondere der Unterstützung von Entscheidungen zur [[erstbevorratung-ersatzteile]].

Sie ermöglicht eine erste Abschätzung von:

- erwarteter Nachfrage
- Risiko von Fehlbeständen
- notwendiger initialer Lagerbestände

Solche Modelle sind besonders relevant im After-Sales-Kontext, wo viele neue Teile regelmäßig eingeführt werden.
