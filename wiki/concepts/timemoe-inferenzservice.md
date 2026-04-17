---
title: TimeMoE-Inferenzservice
type: concept
domain: ai
sources: [raw/docs/Demand_AI_GB10_final_UAT_fachlich.docx]
related: ["[[demand-ai-roadmap-phasen]]", "[[ml-ops-infrastruktur-gb10]]", "[[demand-ai-preismodell]]", "[[febi]]", "[[weiling]]", "[[durst]]", "[[schaeffler-tech]]"]
confidence: medium
last_updated: 2026-04-17
---

Der TimeMoE-Inferenzservice stellt die erste produktive Phase von Demand AI dar. Er ist ein mandantenfähiger AWS-basierter Forecasting-Service für univariate Zeitreihen. Er erlaubt das Erzeugen von Prognosen für Artikel mit regelmäßigem Bedarf, insbesondere C‑Teile.

Kernpunkte:
- Aggregation auf Tag, Woche oder Monat
- Konfiguration durch Einschränkung der Historie (z. B. 4‑Wochen-Forecast basierend auf 8 Wochen)
- Integration in bestehende Systeme wie BO und AP
- Basis für interne und externe POCs

Einschränkungen:
- Keine Self-Service-Funktionen
- Kein Produktlayer
- Manuelle Betreuung

Preisrahmen: 500–2.000 EUR/Monat als Zusatz-SaaS zu bestehenden ADDONE-Verträgen.
