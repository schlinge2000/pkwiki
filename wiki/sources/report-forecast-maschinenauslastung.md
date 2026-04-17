---
title: Forecast-Studie zur Maschinenauslastung
type: source
source_file: raw/pdfs/Report_Forecast_Maschinenauslastung.pdf
source_type: paper
date: 2015-11-12
key_concepts: ["[[maschinenauslastungsprognose]]", "[[aggregationsniveau-prognosen]]", "[[mittelwert-baseline-prognose]]", "[[datenhistorie-mustererkennung]]", "[[maschinenstunden-normalisierung]]", "[[sporadische-nachfrage-prognose]]"]
last_updated: 2026-04-17
---

Die Studie untersucht Methoden zur Prognose der Maschinenauslastung in der Produktion eines Unternehmens (FST, Werk Weinheim). Ziel ist es, eine planerische Sicht auf Kapazitätsbedarf zu entwickeln, um taktische und strategische Entscheidungen zu unterstützen, etwa für Investitionen, Personalplanung oder Schulungen.

Die Produktion umfasst 18 verschiedene Maschinentypen. Historische Warenausgänge einzelner Artikel werden im Bestandsoptimierungssystem ADD*ONE erfasst. Eine direkte Planung der Maschinenauslastung ist dort jedoch nicht vorgesehen, da Prognosen nur auf Ebene Artikel/Werk berechnet werden können.

Ein zentrales Problem besteht darin, dass Artikelverbräuche stark sporadisch sind. Einzelzeitreihen zeigen daher hohe Varianz und sind schwer prognostizierbar. Die Studie untersucht deshalb, ob Aggregation auf höheren Ebenen stabilere Muster offenlegt.

Untersuchte Dimensionen:
- Aggregationsebenen: Artikel, Kundensegment, Maschinengruppe, Gesamtproduktion
- Zielgrößen: Stückzahlen und Maschinenstunden

Maschinenstunden wurden aus Stückzahlen über durchschnittliche Bearbeitungszeiten pro Maschinengruppe berechnet. Fehlende Zeiten wurden über vergleichbare Produkte imputiert.

Die Datenbasis besteht aus:
- historischen Warenausgängen aus ADD*ONE
- Kundensegment-Zuordnung (z. B. Automotive, Robotics)
- Artikel-Maschinen-Zuordnung

Zur Vergleichbarkeit der Modelle wurden alle Zeitreihen nach der Prognoseberechnung mittels MinMax-Normierung auf das Intervall [0,1] skaliert.

Wichtige Ergebnisse:
- Einzelprognosen pro Artikel mit anschließender Aggregation erzielten die besten SPEC-Werte.
- Aggregationen auf Segmentebene führten häufiger zu Überschätzungen.
- Saisonale Muster der Maschinenauslastung werden erst auf Maschinenaggregation sichtbar.
- Ein einfacher historischer Durchschnitt lieferte überraschend robuste Prognosen.

Die Studie diskutiert das sogenannte "Mittelwert-Paradoxon": Bei stark verrauschten oder kurzen Zeitreihen konvergieren selbst komplexe neuronale Modelle häufig zu einer Mittelwertstrategie, da keine stabilen Muster erkennbar sind.

Mit längeren Datenhistorien (typischerweise ≥3 Jahre monatlicher Daten) steigt jedoch die Fähigkeit moderner Modelle, Trends, Saisonalität und strukturelle Muster zu erkennen und vom Mittelwert abzuweichen.

Die Studie zeigt damit, dass robuste Baselines weiterhin eine wichtige Referenz darstellen und dass die Qualität datengetriebener Prognosen stark von Datenhistorie und Aggregationsniveau abhängt.
