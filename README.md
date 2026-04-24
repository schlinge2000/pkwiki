# Knowledge Tree

Hierarchisches Multi-User Knowledge OS. Mehrere Vault-Ebenen (Company, Team,
Personal) werden automatisch durch LLM-Pipelines befüllt und nach oben
aggregiert.

Für Architektur, Ingest-Workflow und Domänen-Modell → [`CLAUDE.md`](CLAUDE.md).

## Quickstart

```powershell
# Einmalige Einrichtung
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

Das Skript prüft Voraussetzungen (uv, git), legt `.env` an, erstellt die
Vault-Struktur, testet die Azure-OpenAI-Verbindung und registriert die
Scheduled Tasks.

## Skripte

| Skript | Beschreibung |
|--------|-------------|
| `ingest.py` | Node-aware Dokument-Ingest |
| `code-extract.py` | GitHub Commit-Diff → CommitDigest |
| `code-ingest.py` | CommitDigest → code-wiki/ |
| `code-watch.py` | GitHub API Poller (Single-Poll pro Scheduled-Task-Tick) |
| `manual-ingest.py` | PDF-Handbücher → agent-optimierte Wiki-Seiten |
| `pm-synthesize.py` | Team-/PM-View-Aggregation |
| `wiki-sync.py` | Wiki-MD → `knowledge-wiki-archive` (GitHub) |
| `rebuild-index.py` | Vollständiger Index-Rebuild |
| `setup.ps1` | Ersteinrichtung + MetaSync-Task |
| `sync-watchers.ps1` | Syncht `watchers.json` → Windows Scheduled Tasks |
| `scan-raw.py` | Generischer File-Watcher (scannt Verzeichnis, triggert Ingest pro Datei) |

## Watcher-System

Scheduled Tasks (`KnowledgeTree-*`) werden aus einer deklarativen Config im
Vault verwaltet. Neue Watcher hinzufügen = JSON-Eintrag anhängen, ohne
`setup.ps1` neu laufen zu lassen.

### Dateien

| Pfad | Rolle |
|------|-------|
| `watchers.json` (Repo) | Template, wird beim ersten Setup in den Vault kopiert |
| `$VAULT_ROOT/watchers.json` | **Aktive Config** — hier editieren |
| `sync-watchers.ps1` | Syncht Config → Scheduled Tasks |
| `setup.ps1` | Kopiert Template, registriert MetaSync-Task |

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

Änderungen wirken binnen 15 Min. Manuell sofort triggern:

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

**1. Projekt hat eigenen FileSystemWatcher-Daemon** (z.B. pkwiki's `watch.ps1`
— Echtzeit-Reaktion auf `Created`-Events, Startup-Catchup inklusive).
Einfach als PowerShell-Skript mit `at_logon`-Trigger eintragen:

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

Der Task startet beim Login und läuft unbegrenzt. Kein Polling, kein
`interval_minutes`. Migration aus vorhandenem `register-task.ps1`: alten
Task unregistern, Eintrag hier ergänzen, MetaSync manuell triggern.

**2. Projekt hat nur einen Per-Datei-Ingest-Aufruf** (kein eigener Watcher)
— dann `scan-raw.py` als generischer Wrapper:

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

`scan-raw.py` scannt periodisch, pflegt einen State (`path → mtime`) und
ruft den Ingest-Befehl pro neuer/geänderter Datei auf. `interval_minutes: 1`
ist das Windows-Task-Scheduler-Minimum — für File-Ingest reicht das, weil
die Verarbeitung selbst länger dauert.

Faustregel: **Muster 1 bevorzugen, wenn das Projekt schon einen eigenen
Watcher-Daemon mitbringt** (bessere Reaktionszeit, geringerer Overhead).

### Konvention: Single-Poll statt Loop

Watcher-Skripte führen **einen** Durchlauf aus und beenden sich. Der Task
Scheduler taktet das Intervall (analog zu cron). `code-watch.py` wird ohne
`--loop` aufgerufen — der `--loop`-Modus existiert nur noch für manuelles
Debuggen.

## Basis

Baut konzeptuell auf [pkwiki](https://github.com/schlinge2000/pkwiki)
(Single-User Knowledge Wiki, MIT) auf und erweitert um hierarchische
Vault-Struktur, Sharded Domain Index, Code-Repository-Monitoring und
team-übergreifende Synthese.
