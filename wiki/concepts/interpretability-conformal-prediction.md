---
title: Interpretability in Conformal Prediction
type: concept
domain: ai
sources: [raw/pdfs/Conformal Prediction in Time Series Methods and Interpretability.pdf]
related: ["[[conformal-prediction]]", "[[uncertainty-quantification-forecasting]]"]
confidence: medium
last_updated: 2026-04-17
---

**Interpretability in Conformal Prediction** bezieht sich auf die Fähigkeit von Nutzern, Vorhersageintervalle und Prediction Sets zu verstehen und in Entscheidungsprozesse einzubeziehen.

Ein Vorteil von Conformal Prediction ist, dass Unsicherheit explizit sichtbar gemacht wird.

## Rolle der Intervallgröße

Die Größe eines Prediction Sets kann Hinweise auf die Schwierigkeit einer Vorhersage geben:

- kleine Intervalle → hohe Sicherheit
- große Intervalle → hohe Unsicherheit

Diese Information hilft Anwendern, Prognosen kritisch zu bewerten.

## Unterstützung menschlicher Entscheidungen

Studien zeigen, dass Prediction Sets die Entscheidungsqualität verbessern können, wenn Nutzer erkennen, wann ein Modell besonders sicher ist.

Insbesondere **Singleton Sets** (ein einzig möglicher Wert oder sehr kleines Intervall) signalisieren hohe Modellzuverlässigkeit.

## Offene Forschungsfragen

Noch wenig erforscht sind die **kognitiven Mechanismen**, mit denen Menschen Unsicherheitsinformationen interpretieren.

Mögliche Einflussfaktoren:

- individuelle Unterschiede
- Kontext der Entscheidung
- Darstellung der Unsicherheit

Weitere Forschung soll untersuchen, wie solche Systeme benutzerfreundlicher gestaltet werden können.
