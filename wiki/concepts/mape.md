---
title: Mean Absolute Percentage Error (MAPE)
type: concept
domain: ai
sources: [raw/pdfs/foresight.pdf]
related: ["[[forecast-accuracy-metrics]]", "[[intermittent-demand]]", "[[smape]]"]
confidence: medium
last_updated: 2026-04-17
---

Der Mean Absolute Percentage Error (MAPE) ist eine häufig verwendete Kennzahl zur Bewertung von Prognosegenauigkeit. Sie misst den durchschnittlichen absoluten Fehler relativ zum tatsächlichen Wert.

Definition:

MAPE = mean(|(Y_t − F_t) / Y_t|)

## Vorteile

- skalenunabhängig
- leicht interpretierbar als Prozentwert
- ermöglicht Vergleich zwischen verschiedenen Zeitreihen

## Probleme

Bei [[intermittent-demand]] ist MAPE häufig ungeeignet:

- Wenn Y_t = 0, entsteht Division durch Null
- Fehlerwerte werden unendlich oder undefiniert
- Verteilung der Fehler kann stark verzerrt sein, wenn tatsächliche Werte nahe Null liegen

Aus diesen Gründen kann MAPE bei Ersatzteil‑ oder sporadischer Nachfrage nicht zuverlässig verwendet werden.
