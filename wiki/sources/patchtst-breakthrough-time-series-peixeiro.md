---
title: PatchTST: A Breakthrough in Time Series Forecasting
type: source
source_file: raw/pdfs/PatchTST_ A Breakthrough in Time Series Forecasting _ by Marco Peixeiro _ Towards Data Science.pdf
source_type: article
date: 2023-06-20
key_concepts: ["[[patchtst]]", "[[patching-time-series]]", "[[channel-independence-time-series]]", "[[transformer-time-series-forecasting]]", "[[n-beats]]", "[[n-hits]]", "[[self-supervised-representation-learning-time-series]]"]
last_updated: 2026-04-17
---

Der Artikel erklärt das Modell **PatchTST (Patch Time Series Transformer)** und demonstriert dessen Anwendung für Zeitreihenprognosen in Python. Der Fokus liegt auf einer intuitiven Erklärung der Architektur sowie einem praktischen Vergleich mit etablierten Deep‑Learning-Modellen wie [[n-beats]] und [[n-hits]].

Der Ansatz basiert auf Transformer-Architekturen, die ursprünglich aus NLP‑Modellen wie BERT oder GPT bekannt sind. Während Transformer in vielen Bereichen erfolgreich sind, wurden im Bereich Zeitreihen lange Zeit bessere Ergebnisse mit MLP‑basierten Modellen erzielt. PatchTST versucht diese Lücke zu schließen.

Zentrale Ideen des Modells:

- Nutzung von **Patching**, bei dem Zeitreihen in kleinere Segmente aufgeteilt werden
- **Channel-Independence** für multivariate Zeitreihen
- Einsatz eines klassischen **Transformer Encoders** als Backbone
- Optionales **Self-Supervised Representation Learning** durch Maskierung von Patches

Durch das Patch-Konzept wird die Anzahl der Tokens reduziert und gleichzeitig lokaler zeitlicher Kontext erfasst. Dadurch können längere Input-Sequenzen verarbeitet werden und die Trainingskomplexität sinkt.

Der Artikel demonstriert eine Beispielimplementierung mit der Python‑Bibliothek [[neuralforecast]] und dem **Exchange Dataset**, das tägliche Wechselkurse mehrerer Länder gegenüber dem US‑Dollar enthält.

In einem einfachen Experiment wird PatchTST mit [[n-beats]] und [[n-hits]] verglichen. Die Evaluation erfolgt mit den Metriken **MAE** und **MSE**. In diesem Beispiel erzielt PatchTST die besten Werte, wobei betont wird, dass dies kein umfassendes Benchmarking darstellt.

Der Artikel verweist außerdem auf das ursprüngliche Paper *"A Time Series is Worth 64 Words: Long-Term Forecasting with Transformers"* (Nie, Nguyen et al., 2023), in dem PatchTST erstmals vorgestellt wurde.
