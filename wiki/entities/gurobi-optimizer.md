---
title: Gurobi Optimizer
type: entity
entity_type: product
sources: [raw/pdfs/LLMs_SCM_Optim 1 1.pdf]
related: ["[[optiguide-framework]]", "[[supply-chain-optimization]]"]
last_updated: 2026-04-17
---

Der **Gurobi Optimizer** ist ein kommerzieller Solver für mathematische Optimierungsprobleme.

Im Paper wird Gurobi verwendet, um die zugrunde liegenden Optimierungsmodelle zu lösen, während [[large-language-models]] im [[optiguide-framework]] lediglich als Interface dienen.

Typische Problemklassen, die mit Gurobi gelöst werden:

- Linear Programming
- Mixed Integer Programming (MIP)
- Netzwerkoptimierung

Das Framework nutzt den Solver als Backend, während LLMs Code generieren, der neue Nebenbedingungen oder Szenarioanalysen in das Modell einfügt.