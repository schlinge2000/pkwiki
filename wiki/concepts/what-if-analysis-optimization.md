---
title: What-if Analysis in Optimization Systems
type: concept
domain: ai
sources: [raw/pdfs/LLMs_SCM_Optim 1 1.pdf]
related: ["[[optiguide-framework]]", "[[explainable-optimization]]", "[[llms-supply-chain-optimization]]"]
confidence: medium
last_updated: 2026-04-17
---

**What-if Analysis** beschreibt die Untersuchung von hypothetischen Szenarien in Optimierungsmodellen.

Nutzer verändern dabei bestimmte Parameter des Systems und analysieren die Auswirkungen auf die optimale Lösung.

Beispiele für typische Fragen:

- Was passiert, wenn Nachfrage in einer Region um 10 % steigt?
- Wie ändern sich Kosten, wenn ein anderer Lieferant gewählt wird?
- Kann eine Fabrik ihre Kapazität um 5 % reduzieren?

### Technischer Ablauf

Die Analyse erfolgt typischerweise in drei Schritten:

1. Anpassung von Modellparametern oder Nebenbedingungen
2. erneutes Lösen des Optimierungsproblems
3. Vergleich der neuen Lösung mit der ursprünglichen

In klassischen Systemen müssen Data Scientists oder Engineers diese Analysen oft manuell durchführen.

### LLM-gestützte What-if Analysen

Frameworks wie [[optiguide-framework]] ermöglichen es Nutzern, What-if Szenarien direkt in natürlicher Sprache zu formulieren.

Das System kann:

- Modellparameter automatisch ändern
- den Solver erneut ausführen
- Kostenunterschiede berechnen
- Ergebnisse verständlich erklären

Dies reduziert den Kommunikationsaufwand zwischen Business‑Planern und technischen Teams.