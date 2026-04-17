---
title: Foundation Model Prognoseservice
type: concept
domain: ai
sources: ["raw/slides/Technisches Konzept Foundation Model Prognoseservice.pptx"]
related: ["[[kundenprozess-prognoseservice]]", "[[technische-anforderungen-prognoseservice]]", "[[inform]]"]
confidence: medium
last_updated: 2026-04-17
---

Das Foundation Model Prognoseservice-Konzept beschreibt einen von INFORM trainierten Forecasting-Service. Kernidee ist ein mandantenfähiges Modell, das per API von Kunden genutzt werden kann. Der Service bietet zwei Hauptfunktionen:

- **Fit**: Training eines kundenspezifischen Modells auf Basis historischer Daten (unique_id, ds, y, ext. data). Das Modell wird zentral gespeichert und verwaltet.
- **Predict**: Nutzung eines vorhandenen Modells zur Generierung neuer Prognosen.

Der Zugriff erfolgt über HTTPS und ein Auth-Token. Ziel ist eine skalierbare, automatisierte Bereitstellung von Forecasting-Funktionalität.
