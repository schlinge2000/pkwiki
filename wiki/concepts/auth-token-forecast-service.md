---
title: Authentifizierungs-Token im Forecast Service
type: concept
domain: tech
sources: ["raw/slides/Technisches Konzept Foundation Model Prognoseservice.pptx"]
related: ["[[kundenprozess-prognoseservice]]", "[[technische-anforderungen-prognoseservice]]"]
confidence: medium
last_updated: 2026-04-17
---

Der Prognoseservice nutzt Token-basierte Authentifizierung. Das Token dient:

- der Autorisierung von HTTPS-Anfragen,
- der Verknüpfung zum Kundenaccount zur Abrechnung,
- der Absicherung der Fit- und Predict-Routen.

Die Auth-Ebene validiert das Token und kommuniziert mit dem Accounting-System.
