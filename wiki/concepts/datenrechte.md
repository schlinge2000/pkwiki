---
title: Datenrechte & KI-Training (Rechtlicher Rahmen)
type: concept
domain: business
sources: [raw/docs/2024-12-09 Nutzung von Kundendaten im KI-Training - Leitfaden (003).docx, raw/docs/2024-12-09 Datenlizenzvertrag_DRAFT.docx]
related: ["[[demand-ai]]", "[[foundation-models]]", "[[strategiegefaehrdung]]", "[[datenstrategie]]"]
confidence: high
last_updated: 2026-04-17
---

# Datenrechte & KI-Training (Rechtlicher Rahmen)

Leitfaden von Jörg Herbers (09.12.2024) zu rechtlichen und vertraglichen Grundlagen für die Nutzung von Kundendaten im KI-Training. Kritisch für die Skalierbarkeit von [[foundation-models]].

## Datenkategorien und Rechtsrahmen

| Kategorie | Regelwerk | INFORM-Relevanz |
|---|---|---|
| Personenbezogene Daten | DSGVO | Hoch — Anonymisierung in INFORM-Systemen oft nicht möglich |
| Geschäftsgeheimnisse | Geschäftsgeheimnisgesetz (EU 2016/943) | Hoch — Zeitreihen ohne Artikel-/Firmenbezug meist unkritisch |
| IoT/Prozessdaten | EU Data Act (ab Sep 2025) | Mittel — eröffnet Zugang zu Maschinendaten |
| Hochrisiko-KI | EU AI Act | Abhängig vom Use Case |

## Kern-Problem bei INFORM

DSGVO-Anonymisierung reicht oft nicht aus: INFORM ist häufig selbst Betreiber der Cloud-Systeme, in denen personenbezogene Daten liegen. Selbst nach Entfernung direkter Kennungen (Namen, IDs) kann der Personenbezug über Datenkombinationen wiederhergestellt werden → datenschutzrechtlich weiterhin pseudonym, nicht anonym.

## Was ist erlaubt (ohne großen Aufwand)

- Zeitreihen **ohne** Unternehmens- und Artikelbezug → keine Geschäftsgeheimnisse
- Aggregierte Daten → Geschäftsgeheimnisschutz entfällt
- Daten mit expliziter Datennutzungsvereinbarung → rechtlich sauber

## Lösungsansätze für problematische Daten

- **Föderiertes Lernen:** Teilmodelle dezentral auf Kundendaten trainieren, auf Modellebene zusammenführen
- **Synthetic Data:** Generative Modelle erstellen Simulationsdaten → "großes" Modell auf simulierten Daten trainieren
- **Datenaggregation:** So aggregieren, dass Einzelgeheimnisse nicht wiederherstellbar

## Anforderungen an Datennutzungsvereinbarungen

1. Explizit vereinbart (nicht in AGBs versteckt)
2. Dokumentiert, dass Kunde Recht zur Lizenzierung hat
3. NDA für Geschäftsgeheimnisse
4. Auftragsverarbeitungsvereinbarung für personenbezogene Daten
5. Zweck des KI-Trainings explizit genannt

## Geschäftsmodell-Optionen

- Verpflichtende Datennutzung als Lizenzvoraussetzung
- Bezahlung für Daten durch INFORM (gegen Lizenzgebühren verrechnet)
- Opt-In Modell mit klaren Mehrwerten für den Kunden
