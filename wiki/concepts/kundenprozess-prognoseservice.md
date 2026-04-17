---
title: Kundenprozess im Prognoseservice
type: concept
domain: business
sources: ["raw/slides/Technisches Konzept Foundation Model Prognoseservice.pptx"]
related: ["[[foundation-model-prognoseservice]]", "[[subscription-billing-architektur]]"]
confidence: medium
last_updated: 2026-04-17
---

Der Kundenprozess für den Prognoseservice umfasst folgende Schritte:

- Selbstständige Buchung eines Subscriptionsmodells.
- Automatisiertes Payment abhängig von Lizenz/Subscription.
- Eigenständige Anpassung der Subscription durch den Kunden.
- Bereitstellung eines Auth-Tokens zur API-Nutzung.
- Nutzung zweier API-Routen: Fit (Modelltraining) und Predict (Vorhersage).

Dies ermöglicht eine vollständig autonome Nutzung des Prognoseservices durch den Kunden.
