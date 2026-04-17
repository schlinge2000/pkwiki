---
title: PatchTST
type: concept
domain: ai
sources: [raw/pdfs/PatchTST_ A Breakthrough in Time Series Forecasting _ by Marco Peixeiro _ Towards Data Science.pdf]
related: ["[[patching-time-series]]", "[[channel-independence-time-series]]", "[[transformer-time-series-forecasting]]", "[[self-supervised-representation-learning-time-series]]", "[[n-beats]]", "[[n-hits]]"]
confidence: medium
last_updated: 2026-04-17
---

**PatchTST (Patch Time Series Transformer)** ist ein Transformer-basiertes Deep‑Learning‑Modell für **Zeitreihenprognosen mit langen Forecast-Horizonten**. Das Modell wurde 2023 im Paper *"A Time Series is Worth 64 Words: Long-Term Forecasting with Transformers"* vorgestellt.

Die Architektur kombiniert drei zentrale Ideen:

1. **Patching von Zeitreihen** – Zeitreihen werden in kurze Segmente (Patches) aufgeteilt, die als Tokens in den Transformer eingegeben werden.
2. **Channel-Independence** – bei multivariaten Zeitreihen wird jede Serie als eigener Kanal modelliert.
3. **Transformer Encoder** – ein klassischer Transformer-Encoder verarbeitet die Patch-Tokens.

Durch das Patchen reduziert sich die Anzahl der Tokens im Modell erheblich. Wenn eine Zeitreihe Länge L hat und Patches mit Länge P und Stride S verwendet werden, reduziert sich die Tokenzahl ungefähr von L auf L/S. Dadurch sinken **Rechenaufwand und Speicherbedarf**, während gleichzeitig längere Inputsequenzen möglich werden.

Ein weiterer Vorteil besteht darin, dass das Modell **lokale zeitliche Strukturen** besser erfassen kann, da ein Patch mehrere zusammenhängende Zeitpunkte enthält.

PatchTST kann außerdem **self-supervised representation learning** nutzen. Dabei werden zufällige Patches maskiert und das Modell wird trainiert, diese zu rekonstruieren. Dies soll abstraktere Repräsentationen der Zeitreihe lernen und die Prognoseleistung verbessern.

In praktischen Experimenten wurde PatchTST mit MLP-basierten Modellen wie [[n-beats]] und [[n-hits]] verglichen und zeigte in einigen Szenarien bessere Werte bei klassischen Fehlermaßen wie MAE und MSE.
