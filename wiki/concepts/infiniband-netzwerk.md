---
title: Infiniband-Netzwerk (FDR)
type: concept
domain: tech
sources: [raw/slides/Boxx architecture.pptx]
related: ["[[boxx-systemarchitektur]]", "[[mellanox]]", "[[server-hardware-konfiguration]]"]
confidence: medium
last_updated: 2026-04-17
---

Die BOXX-Architektur nutzt ein Infiniband-FDR-Netzwerk (56Gb/s) für Hochgeschwindigkeits-Datenverkehr zwischen den Servern. Eingesetzte Komponenten laut Quelle:

- Mellanox SX6012 SwitchX (12 Ports, FDR)
- Mellanox ConnectX-3 VPI Adapter
- QSFP-basierte FDR-Kabel (5m)

Infiniband dient als ultraschnelles Backend-Netzwerk und ermöglicht geringe Latenzen und hohen Datendurchsatz, insbesondere zwischen Rechenknoten und der Storage-Schicht.
