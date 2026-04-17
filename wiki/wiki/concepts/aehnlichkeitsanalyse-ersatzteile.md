---
title: Ähnlichkeitsanalyse für Ersatzteile
type: concept
domain: ai
sources: [raw/pdfs/Interview_Zusammenfassung_Jungheinrich.pdf]
related: ["[[erstbevorratung-ersatzteile]]", "[[anlaufphase-ersatzteile-prognose]]", "[[demand-forecasting]]"]
confidence: medium
last_updated: 2026-04-17
---

Die **Ähnlichkeitsanalyse für Ersatzteile** beschreibt Methoden, mit denen neue Komponenten anhand ihrer Eigenschaften mit bestehenden Teilen verglichen werden.

Ziel ist es, aus historischen Daten ähnlicher Teile Erkenntnisse für Prognosen oder Bevorratungsentscheidungen abzuleiten.

## Anwendung im After Sales

Im Interview mit [[jungheinrich]] wird erwähnt, dass eine solche Logik bislang **kaum genutzt** wird, obwohl sie potenziell hilfreich wäre.

Mögliche Vergleichsdimensionen können sein:

- technische Eigenschaften
- Baugruppenstruktur
- Fahrzeugmodell
- Nutzungskontext

Durch die Identifikation ähnlicher Teile lassen sich beispielsweise:

- typische Nachfrageverläufe
- Anlaufphasen
- Ersatzteilbedarfe

abschätzen.

## Rolle in KI-gestützten Systemen

Im vorgestellten Demand-AI-Ansatz von [[inform-institut-fuer-operations-research-und-management]] soll eine Software:

- Stammdaten automatisch analysieren
- Ähnlichkeiten zwischen Teilen erkennen
- daraus Prognosen und Bevorratungsvorschläge ableiten

Die Methode ist besonders relevant für Situationen ohne direkte historische Nachfrage, etwa bei der [[erstbevorratung-ersatzteile]].
