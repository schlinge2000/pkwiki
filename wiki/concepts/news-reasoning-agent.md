---
title: News Reasoning Agent
type: concept
domain: ai
sources: [raw/pdfs/2409.17515v3.pdf]
related: ["[[news-integrierte-zeitreihenprognose]]", "[[evaluation-agent-reflexion]]"]
confidence: medium
last_updated: 2026-04-17
---

Der **News Reasoning Agent** ist eine LLM-basierte Komponente zur automatischen Auswahl relevanter Nachrichten für Zeitreihenprognosen.

Das Problem: Internet-News enthalten enorme Mengen irrelevanter Informationen. Ungefilterte News verschlechtern Prognosen, weil sie Rauschen und falsche Kausalitäten einführen.

Der Reasoning-Agent analysiert daher Nachrichten und wählt nur solche aus, die plausibel Einfluss auf die Zielzeitreihe haben.

## Aufgaben

Der Agent führt mehrere Schritte aus:

1. Analyse möglicher Einflussfaktoren einer Zeitreihe
2. Bewertung von Nachrichten nach Relevanz
3. Klassifikation der Wirkung

Die Wirkung wird kategorisiert als:

- kurzfristige Effekte
- langfristige Effekte
- unmittelbare Echtzeit-Effekte

## Methodik

Der Agent nutzt mehrere LLM-Techniken:

- Few-Shot Prompting
- [[chain-of-thought]]-Reasoning
- strukturierte JSON-Ausgaben

Damit kann der Agent komplexe Zusammenhänge zwischen Ereignissen und Zeitreihen analysieren.

## Beispiele relevanter News

Für Stromnachfrage können relevante Ereignisse sein:

- extreme Wetterlagen
- Infrastrukturstörungen
- Großveranstaltungen
- politische Entscheidungen

Für Finanzmärkte z. B.:

- Zinsentscheidungen
- geopolitische Ereignisse
- wirtschaftliche Indikatoren
