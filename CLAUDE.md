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
| `code-watch.py` | GitHub API Poller für Repo-Monitoring (triggert `code-extract` + `code-ingest`) |
| `tree-synthesize.py` | Upward Aggregation Personal→Team→Company |
| `batch-ingest.ps1` | Massen-Ingest aller Quelldateien |
| `setup-vault.ps1` | OneDrive-Sync + Obsidian-Setup für neue User |
| `setup.ps1` | Ersteinrichtung: .env, Vault-Struktur, MetaSync-Task |
| `sync-watchers.ps1` | Syncht `watchers.json` → Windows Scheduled Tasks (create/update/remove) |
| `scan-raw.py` | Generischer File-Watcher: scannt ein Verzeichnis + triggert Ingest pro neuer Datei |

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

## Watcher-System

Scheduled Tasks (`KnowledgeTree-*`) werden aus einer deklarativen Config im
Vault verwaltet. Neue Watcher hinzufügen = JSON-Eintrag anhängen, ohne
`setup.ps1` neu laufen zu lassen.

### Dateien

| Pfad | Rolle |
|------|-------|
| `knowledge-tree/watchers.json` | Template, wird beim ersten Setup in den Vault kopiert |
| `$VAULT_ROOT/watchers.json` | **Aktive Config** — hier editieren |
| `knowledge-tree/sync-watchers.ps1` | Syncht Config → Scheduled Tasks |
| `knowledge-tree/setup.ps1` | Kopiert Template, registriert MetaSync-Task |

### Config-Schema

```json
{
  "watchers": [
    {
      "name": "WikiSync",
      "cwd": "C:\\code\\knowledge-tree",
      "script": "wiki-sync.py",
      "args": [],
      "runner": "uv",
      "trigger": "interval",
      "interval_minutes": 15,
      "timeout_minutes": 10,
      "description": "..."
    }
  ]
}
```

- `name` → Task wird `KnowledgeTree-<name>` registriert
- `cwd` → Script-Wurzel (pro Eintrag separat, damit weitere Code-Projekte
  ihre Watcher einfach anhängen können)
- `script` → Datei relativ zu `cwd` (Python oder `.ps1`)
- `args` → optional, zusätzliche CLI-Argumente
- `runner` → `"uv"` (default, ruft `uv run <script>`) oder `"powershell"`
  (ruft `powershell.exe -File <script>` für `.ps1`-Watcher)
- `trigger` → `"interval"` (default, Single-Poll alle N Min) oder
  `"at_logon"` (Daemon, startet beim User-Login — z.B. für langlaufende
  `FileSystemWatcher`-Skripte)
- `interval_minutes` → Trigger-Intervall (nur bei `trigger: "interval"`)
- `timeout_minutes` → Maximum pro Ausführung (nur bei `trigger: "interval"`;
  `at_logon`-Daemons laufen unbegrenzt)

### MetaSync (Live-Reload)

`setup.ps1` registriert **einen** Bootstrap-Task `KnowledgeTree-MetaSync`,
der alle 15 Min `sync-watchers.ps1` ausführt. Der Sync:

1. Liest `$VAULT_ROOT/watchers.json`
2. **CREATE** fehlende Tasks, **UPDATE** geänderte, **DELETE** Tasks deren
   Eintrag entfernt wurde (außer `MetaSync` selbst)

Änderungen wirken so binnen 15 Min. Manuell sofort triggern:

```powershell
Start-ScheduledTask -TaskName KnowledgeTree-MetaSync
# oder direkt:
powershell -ExecutionPolicy Bypass -File .\sync-watchers.ps1
```

### Watcher aus anderem Code-Projekt beisteuern

Eintrag an `$VAULT_ROOT/watchers.json` anhängen, `cwd` zeigt auf den
Projekt-Root — z.B.:

```json
{
  "name": "DemandAIAnalyzer",
  "cwd": "C:\\code\\demand-ai",
  "script": "analyze.py",
  "args": ["--watch"],
  "interval_minutes": 30,
  "timeout_minutes": 20,
  "description": "Demand AI Nightly-Analyse"
}
```

Voraussetzung: das Zielskript läuft mit `uv run` aus dem angegebenen `cwd`
und beendet sich nach einem Durchlauf (keine eigene Endlosschleife).

### File-Watcher: zwei Muster

**1. Projekt hat eigenen Daemon** (z.B. pkwiki's `watch.ps1` mit nativem
`FileSystemWatcher`): per `runner: "powershell"` + `trigger: "at_logon"`
direkt einbinden. Echtzeit-Reaktion, kein Polling.

```json
{
  "name": "PkwikiWatch",
  "cwd": "C:\\code\\knowledge-wiki",
  "script": "watch.ps1",
  "runner": "powershell",
  "trigger": "at_logon",
  "description": "pkwiki FileSystemWatcher (Echtzeit raw/-Ingest)"
}
```

`at_logon`-Tasks laufen unbegrenzt; `interval_minutes`/`timeout_minutes`
entfallen. Migration aus vorhandenem `register-task.ps1`: alten Task
unregistern, Eintrag in `watchers.json` ergänzen, MetaSync triggern.

**2. Projekt hat nur Per-Datei-Ingest** (kein eigener Watcher): `scan-raw.py`
als generischer Polling-Wrapper. Scannt periodisch, pflegt State
(`path → mtime`), ruft den Ingest-Befehl pro neuer/geänderter Datei.
Fehlschläge werden nicht im State vermerkt — nächster Tick probiert erneut,
Neustarts holen Verpasstes nach.

```json
{
  "name": "SomeProjectIngest",
  "cwd": "C:\\code\\knowledge-tree",
  "script": "scan-raw.py",
  "args": [
    "--watch-dir",  "C:\\code\\some-project\\raw",
    "--ingest-cwd", "C:\\code\\some-project",
    "--ingest-cmd", "uv run ingest.py",
    "--state-file", "C:\\code\\some-project\\.scan-state.json"
  ],
  "interval_minutes": 1,
  "timeout_minutes": 30
}
```

`interval_minutes: 1` ist das Windows-Task-Scheduler-Minimum — für
File-Ingest (PDF/PPTX/DOCX dauert ohnehin länger) reicht das.

Faustregel: Muster 1 bevorzugen, wenn das Projekt bereits einen eigenen
Watcher-Daemon mitbringt — bessere Reaktionszeit, weniger Overhead.

### Konvention: Single-Poll statt Loop

Watcher-Skripte führen **einen** Durchlauf aus und beenden sich. Der Task
Scheduler taktet das Intervall (analog zu cron). `code-watch.py` wird ohne
`--loop` aufgerufen — der `--loop`-Modus existiert nur noch für manuelles
Debuggen.

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
