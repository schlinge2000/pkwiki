---
title: Wahrscheinlichkeitsbasierte Prognosen
type: concept
domain: ai
sources: [raw/pdfs/Interview_Zusammenfassung_Jungheinrich.pdf]
related: ["[[demand-forecasting]]", "[[erstbevorratung-ersatzteile]]", "[[uncertainty-quantification-forecasting]]"]
confidence: medium
last_updated: 2026-04-17
---

**Wahrscheinlichkeitsbasierte Prognosen** beschreiben Vorhersagen, die nicht als einzelner Punktwert, sondern als **Wahrscheinlichkeitsbereich** oder Verteilung dargestellt werden.

Im Kontext der Ersatzteilplanung bedeutet dies beispielsweise:

- statt einer einzelnen Nachfrageprognose
- wird ein Bereich möglicher Nachfragewerte angegeben

Dies erlaubt eine explizite Darstellung von Unsicherheit.

## Anwendung in der Erstbevorratung

Bei neuen Ersatzteilen existieren keine historischen Nachfragewerte. Prognosen sind daher besonders unsicher.

Im Interview mit [[jungheinrich]] wird ein Ansatz beschrieben, bei dem Prognosen als **Wahrscheinlichkeitsbereiche** ausgegeben werden, um:

- Risiken besser einschätzen zu können
- Entscheidungsunsicherheit sichtbar zu machen
- Disponenten bei der Bestandsentscheidung zu unterstützen

Solche Prognosen können Grundlage für Risikoabschätzungen und initiale Bevorratungsvorschläge sein.
