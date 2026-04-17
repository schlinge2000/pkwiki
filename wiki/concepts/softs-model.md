---
title: SOFTS Model
type: concept
domain: ai
sources: [raw/pdfs/SOFTS_ The Latest Innovation in Time Series Forecasting _ by Marco Peixeiro _ Towards Data Science.pdf]
related: ["[[stad-module]]", "[[series-core-fusion]]", "[[multivariate-long-horizon-forecasting]]", "[[patchtst]]", "[[itransformer]]", "[[tsmixer]]"]
confidence: medium
last_updated: 2026-04-17
---

**SOFTS (Series‑cOre Fused Time Series)** ist ein Deep‑Learning‑Modell für Zeitreihenprognosen, das speziell für **multivariate Forecasting‑Probleme mit langen Prognosehorizonten** entwickelt wurde.

Das Modell wurde 2024 im Paper *“SOFTS: Efficient Multivariate Time Series Forecasting with Series‑Core Fusion”* vorgestellt.

### Motivation

Viele moderne Forecasting‑Modelle verfolgen zwei unterschiedliche Ansätze:

- **Transformer‑basierte Modelle** wie [[patchtst]] reduzieren die Komplexität von Attention, z. B. durch Patching oder Channel Independence.
- **MLP‑basierte Modelle** sind sehr schnell zu trainieren, verlieren aber oft an Performance, wenn viele Zeitreihen gleichzeitig modelliert werden.

SOFTS kombiniert beide Ideen:

- schnelle **MLP‑Architektur**
- effizientes Lernen von **Interaktionen zwischen Zeitreihen**.

### Architektur

Der Modellaufbau besteht aus mehreren Komponenten:

1. **Normalisierung** der Eingabedaten mit [[reversible-instance-normalization-revin]].
2. **Embedding jeder Zeitreihe separat**, ähnlich wie im [[itransformer]].
3. Verarbeitung im [[stad-module]], das Interaktionen zwischen Zeitreihen lernt.
4. Fusion der Informationen und finale **lineare Prognoseschicht**.

### Zentrale Idee

Der Kernmechanismus ist eine **zentralisierte Repräsentation mehrerer Zeitreihen**, die:

- gemeinsame Muster aggregiert
- diese Information wieder an jede einzelne Serie zurückverteilt.

Dieser Mechanismus wird als [[series-core-fusion]] bezeichnet.

### Vorteile

- effizientes Lernen von **Interaktionen zwischen Zeitreihen**
- **lineare Komplexität** im STAD‑Modul
- geeignet für **große multivariate Datensätze**

Damit adressiert SOFTS ein zentrales Problem moderner Forecasting‑Systeme: Skalierbarkeit bei vielen parallelen Zeitreihen.
