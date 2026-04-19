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
