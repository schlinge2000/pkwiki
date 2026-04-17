---
title: SOFTS: The Latest Innovation in Time Series Forecasting
type: source
source_file: raw/pdfs/SOFTS_ The Latest Innovation in Time Series Forecasting _ by Marco Peixeiro _ Towards Data Science.pdf
source_type: article
date: 2024-06-11
key_concepts: ["[[softs-model]]", "[[stad-module]]", "[[series-core-fusion]]", "[[reversible-instance-normalization-revin]]", "[[multivariate-long-horizon-forecasting]]"]
last_updated: 2026-04-17
---

Der Artikel beschreibt das Forecasting‑Modell **SOFTS (Series‑cOre Fused Time Series)** und erklärt dessen Architektur sowie den Einsatz in Experimenten mit Zeitreihen‑Datensätzen.

Zentrale Inhalte:

- Einführung des [[softs-model]] als neues Deep‑Learning‑Modell für Zeitreihenprognosen
- Vorstellung des [[stad-module]] (STar Aggregate‑Dispatch) zur Modellierung von Interaktionen zwischen Zeitreihen
- Nutzung eines zentralisierten Ansatzes ([[series-core-fusion]]) zur Aggregation und Verteilung von Serieninformationen
- Verwendung von [[reversible-instance-normalization-revin]] zur Normalisierung der Eingabedaten
- Anwendung auf [[multivariate-long-horizon-forecasting]]

Der Artikel positioniert SOFTS im Kontext moderner Deep‑Learning‑Forecasting‑Modelle wie [[patchtst]], [[n-beats]], [[n-hits]] und Transformer‑basierter Ansätze.

Für Experimente wird das [[electricity-transformer-temperature-dataset-ett]] verwendet und das Modell mit [[patchtst]], [[tsmixer]] und [[itransformer]] verglichen.

Die Implementierung erfolgt über die Python‑Bibliothek [[neuralforecast]].

Ergebnis der Demonstration:

- In einem **univariaten Szenario** erzielt [[patchtst]] die besten MAE‑Werte.
- In einem **multivariaten Szenario** kann [[tsmixer]] bessere Ergebnisse liefern.

Der Artikel weist darauf hin, dass diese Ergebnisse **kein vollständiger Benchmark** sind, da nur ein Datensatz und ein einzelner Forecast‑Horizont verwendet wurden.

Die zentrale Idee des SOFTS‑Ansatzes ist die Kombination aus:

- schneller **MLP‑basierter Architektur**
- effizientem Lernen von **Interaktionen zwischen Serien** ohne quadratische Attention‑Komplexität.
