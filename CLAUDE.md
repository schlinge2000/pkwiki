# Knowledge Tree — Enterprise Knowledge Platform

Hierarchisches Multi-User Knowledge OS. Mehrere Vault-Ebenen (Company, Team, Personal)
werden automatisch durch LLM-Pipelines befüllt und nach oben aggregiert.

## Architektur

```
knowledge-tree/              ← Vault-Root (SharePoint)
  _company/                  ← Unternehmens-Ebene
  _team-<name>/              ← Team-Ebene
    _personal-<user>/        ← Persönliche Ebene
```

## Tech-Stack

- Python 3.13, uv, Pydantic (Structured Output)
- Azure OpenAI (GPT-4.1+, Vision API)
- GitHub API (Code-Monitoring via PAT)
- SharePoint / OneDrive (Vault-Storage + Distribution)
- GitHub Actions (zentraler Ingest-Service)
- Obsidian (lokaler Viewer)

## Skripte (geplant)

| Skript | Beschreibung |
|--------|-------------|
| `ingest.py` | Node-aware Dokument-Ingest (--node company\|team\|personal) |
| `extract.py` | PPTX/PDF/DOCX → Markdown + Vision API |
| `code-extract.py` | GitHub Commit-Diff → CommitDigest |
| `code-ingest.py` | CommitDigest → code-wiki/ + wiki/meta/ |
| `code-watch.py` | GitHub API Poller für Repo-Monitoring |
| `tree-synthesize.py` | Upward Aggregation Personal→Team→Company |
| `batch-ingest.ps1` | Massen-Ingest aller Quelldateien |
| `setup-vault.ps1` | OneDrive-Sync + Obsidian-Setup für neue User |

## Wissensdomänen (Sharded Domain Index)

Jedes Dokument wird vor dem Ingest klassifiziert. Der Index ist nach Domain geshardet:
`wiki/index-{domain}.md`. Der Top-Level-Index `wiki/index.md` enthält nur eine Tabelle
mit Domain-Zählern.

| Domain | Beschreibung | Index-Datei |
|--------|-------------|-------------|
| `forecasting` | Zeitreihen, Prognosemodelle, Evaluation, Metriken | `index-forecasting.md` |
| `demand-ai` | Demand AI Produkt, Features, Kunden, Roadmap | `index-demand-ai.md` |
| `supply-chain` | SCM, Disposition, Bestandsoptimierung, Logistik | `index-supply-chain.md` |
| `strategy` | Produktstrategie, Business Model, Go-to-Market, Pricing | `index-strategy.md` |
| `tech` | LLMs, APIs, Architektur, Infrastruktur, Coding | `index-tech.md` |
| `research` | Paper, Studien, akademische Quellen, Konferenzen | `index-research.md` |
| `legal` | Verträge, Datenschutz, Compliance, DSGVO | `index-legal.md` |
| `hr` | Personal, Stellenausschreibungen, Interviews, OKRs | `index-hr.md` |
| `meta` | Wiki-interne Seiten, Ingest-Logs, Schemata | `index-meta.md` |
| `general` | alles andere | `index-general.md` |

### Domain-Index-Format

```markdown
# Domain-Index: forecasting

> Zuletzt aktualisiert: 2026-04-19

## Konzepte (N)
- [[slug]] — Titel aus Frontmatter, confidence: high/medium/low

## Quellen (N)
- [[source-slug]] — Quelltitel, confidence: medium

## Entities (N)
- [[entity-slug]] — Name, confidence: high
```

### Frontmatter-Konvention

```yaml
---
title: "Titel der Seite"
type: concept | source | entity | index
domain: forecasting   # eine der obigen Domains
tags: [tag1, tag2]
confidence: high | medium | low
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

## Ingest-Workflow

1. **Klassifikation** — `classify_document()` bestimmt die Domain (günstiger Pre-Call, ~500 Tokens)
2. **Kontext laden** — nur der domain-spezifische Index wird geladen (skaliert auf 10.000+ Seiten)
3. **LLM-Hauptaufruf** — erstellt 3–10 Wiki-Seiten inkl. log.md-Eintrag
4. **Seiten schreiben** — mit Lock-Datei für parallele Ingest-Prozesse
5. **Index-Update** — `update_domain_index()` schreibt `index-{domain}.md` + `index.md`

## Basis

Dieses Projekt baut konzeptuell auf dem MIT-Projekt
[pkwiki](https://github.com/schlinge2000/pkwiki) auf —
einem persönlichen Single-User Knowledge Wiki.

Die Enterprise-Erweiterungen:
- Hierarchische Vault-Struktur (vault-tree.yaml)
- Sharded Domain Index (skaliert auf 10.000+ Seiten)
- Code-Repository-Monitoring via GitHub API
- Zentraler Ingest-Service (GitHub Actions)
- Team-übergreifende Synthese und PM-View
