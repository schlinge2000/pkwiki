---
title: Symmetric Mean Absolute Percentage Error (sMAPE)
type: concept
domain: ai
sources: [raw/pdfs/foresight.pdf]
related: ["[[forecast-accuracy-metrics]]", "[[mape]]"]
confidence: medium
last_updated: 2026-04-17
---

Der Symmetric Mean Absolute Percentage Error (sMAPE) ist eine Variante des [[mape]], die entwickelt wurde, um asymmetrische Bestrafung von Prognosefehlern zu reduzieren.

Definition:

sMAPE = mean(200 × |Y_t − F_t| / (Y_t + F_t))

Diese Metrik wurde unter anderem in der M3 Forecasting Competition verwendet.

## Ziel

sMAPE soll verhindern, dass positive und negative Fehler unterschiedlich stark gewichtet werden.

## Einschränkungen

Laut [[rob-j-hyndman]] bestehen weiterhin Probleme:

- Wenn tatsächliche Werte und Forecasts nahe Null liegen, entsteht weiterhin eine instabile Division.
- Die Kennzahl kann sogar negative Werte annehmen, wodurch die Interpretation unklar wird.

Daher wird sMAPE nicht als robuste universelle Forecast-Metrik angesehen.
