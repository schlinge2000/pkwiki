---
title: Technisches Konzept Foundation Model Prognoseservice
type: source
source_file: raw/slides/Technisches Konzept Foundation Model Prognoseservice.pptx
source_type: slide
key_concepts: ["[[foundation-models]]", "[[prognose-as-a-service]]", "[[addone]]"]
last_updated: 2026-04-17
---

# Technisches Konzept Foundation Model Prognoseservice

Technische Spezifikation des Prognose-Services: Architekturschichten, Aufwandsschätzungen, Rollout-Stufen und Kundenprozess.

**Kernaussagen:**
- 5-Schichten-Architektur: Billing → Auth → Skalierung → Fachlich → Archivierung
- Aufwand Gesamtarchitektur: Monate (Billing) bis Wochen (fachliche Ebene)
- 3-Stufen-Rollout: exe → Einzelservice → mandantenfähiger GB10-Service
- Self-Service-Modell: Kunde bucht, zahlt, erhält Token, ruft API auf
