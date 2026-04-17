---
title: ADD*ONE (Produktfamilie)
type: concept
domain: tech
sources: [raw/slides/demand ai strategie.pptx, raw/docs/FAQ zu Foundation Models.docx, raw/slides/Technisches Konzept Foundation Model Prognoseservice.pptx]
related: ["[[demand-ai]]", "[[foundation-models]]", "[[prognose-as-a-service]]", "[[mrp-sap]]", "[[inform-gmbh]]"]
confidence: high
last_updated: 2026-04-17
---

# ADD*ONE (Produktfamilie)

INFORM-Produktfamilie für Supply-Chain-Optimierung. Bestehende Software-Suite die durch [[demand-ai]] und [[foundation-models]] erweitert wird.

## Module

| Modul | Kürzel | Beschreibung |
|---|---|---|
| Bestandsoptimierung | BO / BOWEB+ | Lageroptimierung, Bestellmengenplanung |
| Absatzplanung | AP | Demand Planning, S&OP |

## Integration mit Foundation Models

- BOWEB+ bekommt Forecast Service als Standard-Feature
- Auch Bestandskunden erhalten ein Angebot
- Verfügbar für BO und AP
- On-Prem-Systeme über Connectoren an Cloud-Service anbindbar

## Strategische Rolle

ADD*ONE ist der "Zulieferer" für Demand AI:
- Liefert historische Daten für das Foundation Model Training
- Erhält im Gegenzug moderne AI-Prognosen (Win-Win)
- BO Web+ braucht eine moderne Forecast Engine → treibt Demand AI-Entwicklung

## Rollout-Pfad für Forecast Service

1. **Stufe 1:** Client-Erweiterung ("exe") — Akzeptanz verproben
2. **Stufe 2:** Einzelner Service je Kunde — Online-Kunden
3. **Stufe 3:** GB10-Service (mandantenfähig) — alle Kunden
