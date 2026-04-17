---
title: MRP / SAP-Integration
type: concept
domain: tech
sources: [raw/slides/demand ai strategie.pptx]
related: ["[[demand-ai]]", "[[absatzprognose]]", "[[addone]]"]
confidence: medium
last_updated: 2026-04-17
---

# MRP / SAP-Integration

Material Requirements Planning (MRP) im SAP-Ökosystem als Zielsystem für Demand AI Prognosen.

## SAP MRP Lauf

- Bestellt die Summe aller Planbedarfe (PIR) im Planungshorizont
- Planungshorizont hängt am Werk oder am Materialstamm
- Mehrwert des Forecasts abhängig von Planungshorizont und Bestellstrategie

## Demand AI als MRP-Zulieferer

Demand AI positioniert sich als vorgelagerter Prognoseservice für SAP:
- Prognose-Angebot für SAP mit MRP-Lauf
- Launch Copilot für SAP mit MRP (Erstbevorratungslos)
- Stammdatenpflege im SAP: WBZ, optimales Los etc.

## BTP Connection

SAP Business Technology Platform (BTP) als technische Brücke zwischen Demand AI App und SAP-Ökosystem — in Entwicklung.
