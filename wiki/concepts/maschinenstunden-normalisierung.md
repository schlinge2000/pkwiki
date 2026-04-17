---
title: Maschinenstunden-Normalisierung
type: concept
domain: tech
sources: [raw/pdfs/Report_Forecast_Maschinenauslastung.pdf]
related: ["[[maschinenauslastungsprognose]]", "[[aggregationsniveau-prognosen]]"]
confidence: medium
last_updated: 2026-04-17
---

Maschinenstunden-Normalisierung bezeichnet die Transformation von Produktionsmengen (Stückzahlen) in eine kapazitätsbasierte Maßeinheit, typischerweise Maschinenstunden.

Diese Transformation ist besonders relevant, wenn unterschiedliche Produkte stark variierende Bearbeitungszeiten aufweisen. Eine reine Betrachtung von Stückzahlen kann die tatsächliche Auslastung von Maschinen daher verzerren.

In der untersuchten Studie wurden durchschnittliche Bearbeitungszeiten pro Maschinengruppe verwendet, um produzierte Stückzahlen in Maschinenstunden umzurechnen. Fehlende Bearbeitungszeiten in den Stammdaten wurden über Tabellen vergleichbarer Produkte geschätzt.

Die Analyse zeigte, dass Prognosen in Maschinenstunden teilweise robustere Ergebnisse liefern können, da sie die tatsächliche Ressourcennutzung besser widerspiegeln.

Allerdings können unterschiedliche Fehlermetriken (z. B. MAPE oder SPEC) auch gegenläufige Bewertungen ergeben, da sie verschiedene Aspekte der Prognosequalität messen.
