---
title: OptiGuide Framework
type: concept
domain: ai
sources: [raw/pdfs/LLMs_SCM_Optim 1 1.pdf]
related: ["[[llms-supply-chain-optimization]]", "[[explainable-optimization]]", "[[what-if-analysis-optimization]]", "[[microsoft-azure]]", "[[gurobi-optimizer]]"]
confidence: medium
last_updated: 2026-04-17
---

Das **OptiGuide Framework** ist eine Architektur zur Integration von [[large-language-models]] in Optimierungsbasierte Entscheidungsprozesse, insbesondere in der [[supply-chain-optimization]].

Das zentrale Ziel ist nicht, klassische Optimierungsalgorithmen zu ersetzen, sondern die Interaktion zwischen Menschen und Optimierungssystemen zu verbessern.

### Grundidee

LLMs dienen als Übersetzungs‑ und Interpretationsschicht zwischen menschlicher Sprache und mathematischen Optimierungsmodellen.

Der Prozess läuft typischerweise in mehreren Schritten ab:

1. Ein Nutzer stellt eine Frage in natürlicher Sprache.
2. Ein LLM erzeugt daraus Code oder Modellmodifikationen.
3. Ein Optimierungssolver (z. B. [[gurobi-optimizer]]) berechnet eine Lösung.
4. Die Solver-Ausgabe wird wieder vom LLM interpretiert.
5. Das Ergebnis wird als verständliche Erklärung an den Nutzer zurückgegeben.

### Systemkomponenten

Das Framework besteht aus mehreren Komponenten:

**Agents**
- Coder: übersetzt Nutzerfragen in Code
- Safeguard: prüft Code auf Fehler oder Risiken
- Interpreter: übersetzt Ergebnisse zurück in natürliche Sprache

**Application Components**
- Datenbanken
- Optimierungssolver
- Dokumentationen
- Helper-Funktionen

### Wichtige Eigenschaften

- Kombination von LLM reasoning und klassischer Optimierung
- Unterstützung von **What-if Analysen**
- Schutz sensibler Daten (Optimierungsdaten bleiben lokal)
- Möglichkeit zur Visualisierung von Optimierungsergebnissen

### Anwendungsbeispiel

Das Framework wurde in der Supply Chain von [[microsoft-azure]] getestet, wo es Planern ermöglicht, Fragen zu Serverbereitstellung, Lieferkettenentscheidungen und Szenarioanalysen direkt in natürlicher Sprache zu stellen.

Die Evaluation zeigt eine durchschnittliche Genauigkeit von etwa 93 % bei der Beantwortung von Fragen über Optimierungsmodelle.