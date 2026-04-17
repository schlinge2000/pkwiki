---
title: Interview Zusammenfassung – Erstbevorratung Jungheinrich
type: source
source_file: raw/pdfs/Interview_Zusammenfassung_Jungheinrich.pdf
source_type: doc
date: 2026-04-17
key_concepts: ["[[erstbevorratung-ersatzteile]]", "[[aehnlichkeitsanalyse-ersatzteile]]", "[[wahrscheinlichkeitsbasierte-prognosen]]", "[[anlaufphase-ersatzteile-prognose]]", "[[datenbasis-after-sales-forecasting]]"]
last_updated: 2026-04-17
---

## Überblick

Die Quelle fasst ein Interview mit [[jungheinrich]] zur aktuellen Praxis der **Erstbevorratung von Ersatzteilen** für neue Fahrzeugmodelle zusammen. Der Schwerpunkt liegt auf den bestehenden Entscheidungsprozessen, deren Schwächen sowie einem möglichen Lösungsansatz durch eine KI‑basierte Analyseplattform (Demand AI / [[inform-institut-fuer-operations-research-und-management]]).

## Ausgangssituation

- Jungheinrich beschäftigt sich intensiv mit der Planung der Erstbevorratung von Ersatzteilen für neue Fahrzeuge.
- Ziel ist primär die **Sicherstellung der Verfügbarkeit**, selbst wenn dadurch höhere Lagerkosten entstehen.
- Entscheidungen erfolgen heute überwiegend **erfahrungsbasiert** ohne systematische Modelle oder klar definierte Regeln.

## Aktueller Prozess

1. Neue Baugruppen oder Teile entstehen in der Entwicklung.
2. Diese werden an den After Sales übergeben.
3. Die Einheit *Technical Information* entscheidet, welche Teile grundsätzlich als Ersatzteil verfügbar sein sollen.
4. Disponenten entscheiden anschließend, ob und in welcher Menge ein Teil bevorratet wird.

Berücksichtigte Kriterien:
- Kritikalität
- Lieferzeit
- Preis

Diese Kriterien sind jedoch **nicht formalisiert**. Mengen werden überwiegend auf Basis von Erfahrung festgelegt.

Jährlich müssen etwa **5.000 neue Teile** bewertet werden.

## Datenlage

- Verbrauchsdaten: ca. **12 Jahre Historie im BW-System**
- Stammdaten: im **SAP-System**, jedoch heterogene Qualität
- Marktbesatz- und Absatzplandaten existieren, sind aber für Disponenten nicht zugänglich

## Hauptprobleme

- Keine objektiven Kriterien für Erstbevorratung
- Hoher manueller Aufwand
- Fehlende Transparenz über die Qualität früherer Entscheidungen
- Markt- und Absatzdaten werden nicht operational genutzt
- Ähnlichkeitslogiken werden kaum eingesetzt
- Stammdatenqualität im After Sales teilweise schwach

## Vorgestellter Ansatz (Demand AI / INFORM)

Ein Mockup einer Softwarelösung wurde vorgestellt mit folgenden Funktionen:

- automatisches Einlesen von Stammdaten
- Nutzung von **Ähnlichkeitsanalysen** zwischen Teilen
- Risikoabschätzung für neue Ersatzteile
- Vorschläge für initiale Bevorratungsmengen
- Prognosen als **Wahrscheinlichkeitsbereiche statt Punktwerte**
- Training auf Basis historischer **Anlaufphasen alter Teile**

Ziele:
- Entlastung der Disponenten
- objektivere Entscheidungen
- Zeitersparnis

## Nächste Schritte

Kurzfristig:
- Sichtung der Stammdaten
- Diskussion über Datenabzug

Mittelfristig:
- PoC mit realen Daten
- begrenzter Umfang (z. B. ein Fahrzeugmodell)

Langfristig:
- Aufbau einer Softwarelösung für **automatisierte Bevorratungsvorschläge**
