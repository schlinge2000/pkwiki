---
title: Prognose-as-a-Service
type: concept
domain: business
sources: [raw/slides/Technisches Konzept Foundation Model Prognoseservice.pptx, raw/docs/Business Model Canvas Demand AI.docx, raw/docs/FAQ zu Foundation Models.docx]
related: ["[[foundation-models]]", "[[demand-ai]]", "[[addone]]", "[[saas-geschaeftsmodell]]"]
confidence: high
last_updated: 2026-04-17
---

# Prognose-as-a-Service

Cloud-basiertes, nutzungsabhängiges Vertragsmodell für INFORM Foundation Model Prognosen. Analogie zu ChatGPT: leistungsfähige KI als Service, nicht als On-Prem-Software.

## Geschäftsmodell

**Zwei Kundensegmente:**

| Segment | Beschreibung | Kanal |
|---|---|---|
| Direktkunden | Einzelhändler, Großhändler, Hersteller | Direkt / Vertrieb |
| Softwareanbieter | ERP/CRM-Anbieter (z. B. SAP-Partner) | B2B-Integration / API |

**Einnahmequellen:**
- Abonnements für Direktkunden (monatlich / jährlich)
- Lizenzgebühren für Softwareanbieter (nach Endnutzern oder Datenmenge)
- Beratung und maßgeschneiderte Anpassungen

## Kundenprozess (Self-Service)

1. Kunde bucht Service selbst → automatisiertes Payment
2. Token wird bereitgestellt (HTTPS-Request-Authentifizierung)
3. Kunde ruft `fit` oder `predict` Route auf
4. Subscription jederzeit änderbar

## Wertversprechen vs. Wettbewerb

- Flexibles SaaS-Modell ermöglicht Integration in Partner-Ökosysteme
- Fortschrittliche Algorithmen mit kontinuierlicher Weiterentwicklung
- INFORM-Datenschatz aus unzähligen Geschäftsprozessen als Differenzierungsmerkmal

## Risiken

- Marktanteilsverlust an konkurrierende SaaS-Anbieter
- Schwierigkeit, in wettbewerbsintensivem Umfeld relevant zu bleiben
- Hohe initiale Infrastruktur- und Entwicklungskosten

## Megatrends

- Wachsende Nachfrage nach SaaS und Cloud-Diensten
- Anstieg datengestützter Prognosen in Einzelhandel und Fertigung
