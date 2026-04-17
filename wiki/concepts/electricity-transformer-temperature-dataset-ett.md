---
title: Electricity Transformer Temperature Dataset (ETT)
type: concept
domain: ai
sources: [raw/pdfs/SOFTS_ The Latest Innovation in Time Series Forecasting _ by Marco Peixeiro _ Towards Data Science.pdf]
related: ["[[multivariate-long-horizon-forecasting]]", "[[softs-model]]"]
confidence: medium
last_updated: 2026-04-17
---

Das **Electricity Transformer Temperature Dataset (ETT)** ist ein Benchmark‑Datensatz für Zeitreihenprognosen.

Er enthält Messdaten zur **Öltemperatur von Elektrizitätstransformatoren** aus zwei Regionen einer chinesischen Provinz.

### Eigenschaften

- Messfrequenzen: **stündlich** und **alle 15 Minuten**
- mehrere Datensatzvarianten (z. B. ETTm1, ETTm2)
- mehrere Zeitreihen mit potenziellen Interaktionen.

Der Datensatz wird häufig für **Long‑Horizon‑Forecasting‑Benchmarks** genutzt.

Im Experiment aus der Quelle wird:

- **ETTm1** für ein **univariates Forecasting‑Szenario** verwendet
- **ETTm2** für ein **multivariates Forecasting‑Szenario**.

Die Modelle werden mit **Cross‑Validation über mehrere Forecast‑Fenster** trainiert und anschließend anhand von Metriken wie MAE und MSE bewertet.
