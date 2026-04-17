---
title: Prognosemaße & Qualitätsbewertung
type: concept
domain: ai
sources: [raw/slides/Prognosemaße.pptx, raw/slides/BewertungSaisonalerVerfahren.pptx]
related: ["[[absatzprognose]]", "[[foundation-models]]", "[[zeitreihen]]"]
confidence: high
last_updated: 2026-04-17
---

# Prognosemaße & Qualitätsbewertung

Messung der Prognosequalität bei Absatzzeitreihen ist methodisch anspruchsvoll — klassische Maße haben strukturelle Probleme bei typischen Absatzmustern.

## Typische Bedarfsmuster (GB10 Kunden)

| Muster | Anteil |
|---|---|
| Intermittent (sporadisch) | ~40% |
| Erratic (unregelmäßig) | ~30% |
| Lumpy (klumpig) | ~25% |
| Smooth (glatt) | <15% |

**Problem:** Über 75% der Artikel sind nicht "smooth" — klassische Fehlermaße funktionieren hier schlecht.

## Problemfall klassische Maße (MAPE etc.)

- Absätze auf Tagesebene sind häufig 0 (sporadisch)
- `|F - R| / R` ist **nicht definiert** für R = 0
- Klassische Maße bevorzugen systematisch die **Nullvorhersage** — für Inventory Management inakzeptabel
- Nullwerte durch Stockouts ≠ echte Null-Nachfrage → verzerrte Messung

## Alternative Metriken

**1. SPEC — Stock-Keeping Prediction Error Costs (KIT 2020)**
- Balanciert zwei Kostenfunktionale: Opportunity-Kosten + Stock-Keeping-Kosten
- Über α₁, α₂ unterschiedlich gewichtbar
- Direkt relevant für Inventory-Management-Entscheidungen

**2. MAAPE — Mean Arctangent Absolute Percent Error**
- Umgeht das Divisions-durch-Null Problem
- Robuster bei sporadischen Zeitreihen

## Handlungsempfehlung

Bewertung von Absatzprognosen sollte immer entscheidungsorientierte Metriken verwenden (SPEC), nicht rein statistische Fehlermaße (MAPE). Die Metrik muss zur Kostenfunktion des tatsächlichen Entscheidungsproblems passen.
