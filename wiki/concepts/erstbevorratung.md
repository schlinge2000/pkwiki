---
title: Erstbevorratung / Erstbedarf
type: concept
domain: business
sources: [raw/slides/demand ai strategie.pptx, raw/docs/Strategiegefärdung.docx, raw/slides/Präsentation_Zwischenergebnis Demand AI_Durst-Group – Kopie.pptx]
related: ["[[demand-ai]]", "[[absatzprognose]]", "[[mrp-sap]]", "[[schaefer-barthold]]"]
confidence: high
last_updated: 2026-04-17
---

# Erstbevorratung / Erstbedarf

Prognose der initialen Bestellmenge für neue, noch nicht gelistete Artikel. Aktuell manuell und ineffizient — strategisch als erster fokussierter Use Case für Demand AI ausgewählt.

## Problem

- Neue Artikel haben keine Verkaufshistorie
- Entscheidung über Anfangsbevorratung erfolgt heute durch Produktmanager / menschliches Bauchgefühl
- Zu wenig → Unterbestand, Vertrauensverlust beim Kunden, keine Historie aufbaubar
- Zu viel → Überbestand, Abverkauf nötig

> "Über 50% der Mengen sind entweder zu wenig oder zu viel." (Schäfer Barthold Interview)

## Warum als erster Use Case

1. **Kein Datenrechtsproblem:** Keine laufenden Kundendaten nötig — nur Artikelattribute und Marktkontext
2. **Klarer, unbeantworteter Marktbedarf**
3. **Sofortiger operativer Nutzen** ohne große Infrastruktur
4. **Isoliert realisierbar** ohne Abhängigkeit von BO-Web Integration

## Herausforderungen (Lerneffekt Durst)

Aus der Durst-Datenstudie:
- Prognoseservice als Produkt schwer umsetzbar ohne Customizing
- Erwartungshaltung Kunden ≠ technische Möglichkeiten (18 Monate Horizont, Wochenauflösung bei sporadischen Daten)
- Bedarfsvorhersage nicht immer vom Beschaffungsproblem trennbar

## Datenquellen für Erstbedarf

- Artikelattribute (Abmessung, Gewicht, Branche, Markt)
- Vorgänger-/Nachfolgeartikel (falls existent)
- Zulassungszahlen / Marktdaten (z.B. Automotive: Fahrzeugzulassungen → Ersatzteilbedarf)
- Analogie zu ähnlichen Artikeln im Portfolio

## Nächste Schritte (Launch Copilot)

- Launch Copilot für SAP mit MRP: Erstbevorratungslos als konkretes Produkt
- BTP Connection zu SAP als technische Brücke
