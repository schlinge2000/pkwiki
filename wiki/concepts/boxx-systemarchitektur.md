---
title: BOXX Systemarchitektur
type: concept
domain: tech
sources: [raw/slides/Boxx architecture.pptx]
related: ["[[server-hardware-konfiguration]]", "[[infiniband-netzwerk]]", "[[sap-import-integration]]", "[[dell]]", "[[mellanox]]"]
confidence: medium
last_updated: 2026-04-17
---

Die BOXX-Architektur beschreibt ein Hardware- und Netzwerk-Setup bestehend aus:

- Zwei Application Servern
- Einer dedizierten Datenbankebene
- Mehreren Servern (u.a. Dell R640 und R740 Modelle)
- 10Gbit-Ethernet-Verbindungen
- Infiniband-FDR-Struktur über Mellanox-Komponenten
- SAP-Import-Pipeline über das Netzwerk

Im Zentrum steht ein Hochgeschwindigkeits-Infrastrukturlayout für rechenintensive Anwendungen, das CPU-starke Server, NVMe-Speicher und eine Infiniband-Fabric kombiniert. Die Architektur optimiert Durchsatz, Latenz und Verfügbarkeit.
