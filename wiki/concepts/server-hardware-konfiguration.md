---
title: Server-Hardware-Konfiguration (BOXX)
type: concept
domain: tech
sources: [raw/slides/Boxx architecture.pptx]
related: ["[[boxx-systemarchitektur]]", "[[infiniband-netzwerk]]", "[[intel-xeon-gold-6128]]", "[[dell]]"]
confidence: medium
last_updated: 2026-04-17
---

Die Architektur umfasst zwei zentrale Servertypen:

1. **Dell R640**
- 2× Intel Xeon Gold 6128 @ 3,4 GHz
- 6 Cores / 6 Memory Ports pro CPU
- 12×16 GB RDIMM 2667 MT/s

2. **Dell R740**
- 2× Intel Xeon Gold 6128
- 12×64 GB LRDIMM 2667 MT/s
- Dell 3,2 TB NVMe PCIe SSD

Die Systeme sind über 10Gbit Ethernet und Infiniband verbunden. Fokus ist hohe Rechenleistung kombiniert mit schnellem Speicher.
