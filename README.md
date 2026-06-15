# Knowledge Wiki

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> Dokument ablegen. Fertig. Das LLM kompiliert den Rest.

Statt Notizen zu tippen, werden PDFs, Präsentationen und Word-Dokumente in einen Ordner gelegt.
Ein Watcher erkennt neue Dateien automatisch, extrahiert den Inhalt — inklusive Bilder via
Azure OpenAI Vision API — und lässt ein LLM daraus strukturierte, verlinkte Wiki-Seiten schreiben.
Das Ergebnis ist eine navigierbare Wissensbasis in Obsidian, die mit jeder neuen Quelle wächst.

Inspiriert von [Andrej Karpathys LLM-Wiki-Idee](https://x.com/karpathy/status/1751350002281300461):
Das LLM als "Compiler" — Rohdokumente rein, Wissensbasis raus.

---

> **Demo:** Ich habe Claude gefragt: *„Kennst du eine Metapher für einen unpräzisen Forecast?"*
>
> Antwort: *„Du hast schon selbst eine genutzt: Folie 17–18, FINAL BO KI Webinar — zuerst eine nach links ausgeleuchtete Straße, dann ein Reh im Scheinwerferlicht. Für ein Risiko das der Forecast als wenig wahrscheinliches Szenario zeigt."*
>
> Das Reh stand auf keiner Textzeile. Nur ein Bild. Gefunden weil die Pipeline Bilder wirklich liest.

![Reh im Scheinwerferlicht — Metapher für einen Forecast der in die falsche Richtung leuchtet](assets/deer.png)

---

## Warum nicht RAG?

RAG (Retrieval-Augmented Generation) ist die Standardantwort auf "Fragen über eigene Dokumente".
Dieses System verfolgt einen grundlegend anderen Ansatz — und löst dabei Probleme, die RAG
strukturell nicht lösen kann:

| Problem mit RAG | Dieser Ansatz |
|-----------------|---------------|
| Chunking zerschneidet Sinnzusammenhänge | Vollständiges Dokument wird einmalig kompiliert |
| Bilder werden ignoriert oder als Platzhalter behandelt | Vision-API beschreibt jedes Bild im Kontext |
| Einmal indexiert — statisch bis zum nächsten Rebuild | Neue Quellen revidieren und erweitern bestehende Seiten |
| Antworten entstehen zur Laufzeit, unkontrolliert | Wiki-Seiten sind deterministisch, menschenprüfbar |
| Funktioniert nur mit KI | Ergebnis ist Markdown — ohne KI lesbar und navigierbar |
| Vektordatenbank + Embedding-Infrastruktur nötig | Keine Infrastruktur, kein Index, kein Server |

Das Kernprinzip: Wissen wird **einmalig kompiliert** statt bei jeder Anfrage neu zusammengesetzt.
Neue Quellen legen keine parallelen Chunks ab — sie **revidieren bestehende Seiten** und
**akkumulieren Wissen über Zeit**.

---

## Pipeline

```
raw/dokument.pdf
raw/slides/vortrag.pptx
raw/docs/analyse.docx
        │
        ▼
┌───────────────────────────────────────────────────────┐
│  extract.py                                           │
│                                                       │
│  PPTX  ──► Slide-Bilder (PIL)                         │
│              └─► Azure OpenAI Vision API              │
│                    └─► Bildbeschreibung auf Folie      │
│  PDF   ──► PyMuPDF (Fallback bei kaputten PDFs)       │
│  DOCX  ──► python-docx                                │
│                                                       │
│  Ergebnis: raw/.cache/dokument.md                     │
└───────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────┐
│  ingest.py                                            │
│                                                       │
│  .cache/dokument.md ──► Azure OpenAI (GPT-4o)         │
│                           └─► strukturiertes JSON     │
│                                 ├─ concepts[]         │
│                                 ├─ entities[]         │
│                                 ├─ source_summary     │
│                                 └─ suggested_links[]  │
│                                                       │
│  JSON ──► Wiki-Seiten schreiben / aktualisieren       │
└───────────────────────────────────────────────────────┘
        │
        ├──► wiki/concepts/konzept-a.md   (neu oder aktualisiert)
        ├──► wiki/concepts/konzept-b.md
        ├──► wiki/entities/person-x.md
        ├──► wiki/sources/dokument.md     (Quellenübersicht + Autor)
        └──► wiki/index.md               (automatisch aktualisiert)
```

Der Watcher (`watch.ps1`) pollt `raw/` alle 5 Sekunden, erkennt neue Dateien und startet
die Pipeline vollautomatisch im Hintergrund — ein paralleler Job zur Zeit.

---

## Wiki-Seitentypen

### `concepts/` — Konzept- und Technologieseiten

Eine Seite pro Konzept. Wird beim Ingest mehrerer Quellen zum selben Thema angereichert,
nicht dupliziert. Mit explizitem Confidence-Level:

```yaml
---
title: Foundation Models für Zeitreihenprognose
type: concept
domain: ai
sources: [raw/slides/FINAL BO KI Webinar.pptx]
related: ["[[demand-forecasting]]", "[[timemoe]]", "[[transformer-zeitreihen]]"]
confidence: high
last_updated: 2025-04-19
---

Foundation Models für Zeitreihenprognosen sind vortrainierte Modelle, die ohne
aufgabenspezifisches Fine-Tuning auf neue Zeitreihen angewendet werden können...
```

### `entities/` — Personen, Unternehmen, Produkte

Für alle benannten Akteure, die in mehreren Kontexten auftauchen.

### `sources/` — Quellenübersicht je Dokument

Zusammenfassung mit Autor, Kontext und Kernaussagen — als Einstiegspunkt pro Dokument.

### `syntheses/` — Themenübergreifende Analysen

Vom LLM erkannte Muster und Verbindungen über mehrere Quellen hinweg.

### `index.md` + `log.md` — immer automatisch aktualisiert

`index.md` listet alle Wiki-Seiten. `log.md` ist ein Append-only-Aktivitätslog jeder
Ingest-Operation mit Zeitstempel, Quelle und erstellten/aktualisierten Seiten.

---

## Voraussetzungen

- [`uv`](https://docs.astral.sh/uv/) — Python-Paketmanager (`winget install astral-sh.uv`)
- Azure OpenAI Ressource mit einem **leistungsstarken Modell** (Vision-fähig, für PPTX-Bildanalyse)
- [Obsidian](https://obsidian.md) als lokaler Viewer (optional, empfohlen)

### Modell-Empfehlung

Die Qualität der Wissensbasis hängt direkt vom verwendeten Modell ab. Der Ingest-Schritt ist keine einfache Zusammenfassung — das Modell muss Konzepte erkennen, bestehende Seiten sinnvoll erweitern, Verbindungen zwischen Quellen herstellen und Widersprüche markieren. Ein schwächeres Modell produziert generische, schlecht verlinkte Seiten.

**Empfohlen: GPT-4.1 oder neuer** (z.B. GPT-5-class Modelle sobald verfügbar)

`gpt-4o` funktioniert, aber neuere Modelle liefern deutlich bessere Vernetzung und Synthesequalität. Der Unterschied ist bei komplexen, mehrere Quellen übergreifenden Konzepten deutlich spürbar.

---

## Einrichtung

Die Architektur trennt **Code** (dieses Repo, lokal geklont) von **Daten** (Vault in
OneDrive / SharePoint, automatisch zwischen Maschinen synchron). Credentials,
`watchers.json` und `code-repos.yaml` liegen kanonisch im **Vault** — neue Maschine =
nur klonen + `VAULT_ROOT` setzen, der Rest kommt über OneDrive mit.

### Voraussetzungen (einmalig pro Maschine)

- [`uv`](https://docs.astral.sh/uv/) — `winget install astral-sh.uv`
- `git`
- Azure OpenAI Ressource (Vision-fähig, GPT-4.1+)
- OneDrive/SharePoint-Pfad als Vault (z.B. `C:\Users\<user>\OneDrive - <Firma>\knowledge-wiki`)

### Schritt 1 — Repo klonen und `VAULT_ROOT` setzen

```powershell
git clone <repo-url> C:\Code\knowledge-wiki
cd C:\Code\knowledge-wiki

# Persistente Windows-User-Env-Variable — alle Skripte lesen daraus die Vault-.env:
setx VAULT_ROOT "C:\Users\<user>\OneDrive - <Firma>\knowledge-wiki"
# Neue Shell öffnen, damit setx greift.
```

### Schritt 2 — Vault-`.env` anlegen

Im **Vault**-Verzeichnis (nicht im Code-Verzeichnis!) eine `.env` aus der
[Vorlage](.env.example) anlegen. So liegt sie in OneDrive und ist automatisch auf
allen Maschinen verfügbar.

```powershell
New-Item -ItemType Directory -Force "$env:VAULT_ROOT" | Out-Null
Copy-Item .env.example "$env:VAULT_ROOT\.env"
notepad "$env:VAULT_ROOT\.env"
```

```env
# Pflicht — Dokument-Ingest
AZURE_OPENAI_ENDPOINT=https://<resource>.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=<key>
AZURE_OPENAI_DEPLOYMENT=gpt-4.1
AZURE_OPENAI_API_VERSION=2025-04-01-preview

# Vault-Pfad (redundant zur Windows-Env, aber explizit dokumentiert)
VAULT_ROOT=C:\Users\<user>\OneDrive - <Firma>\knowledge-wiki

# Optional — Code-Wiki (code-watch.py pollt GitHub-Repos)
GITHUB_PAT=<personal-access-token>          # Scope: repo:read

# Optional — Wiki-Archiv-Sync (wiki-sync.py)
WIKI_ARCHIVE_PAT=<personal-access-token>    # Scope: repo
WIKI_ARCHIVE_REPO=<owner>/<archive-repo>
```

**Load-Order der Skripte** (erste gefundene Quelle gewinnt, `override=False`):
1. OS-Umgebungsvariablen (z.B. via `setx`)
2. `$VAULT_ROOT/.env` — **kanonisch, OneDrive-synced**
3. `<repo>/.env` — optional, lokaler Override pro Maschine

### Schritt 3 — `setup.ps1` ausführen

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

Idempotent — kann beliebig oft laufen. `setup.ps1`:

1. Prüft `uv` und `git`
2. Legt die Vault-Verzeichnisstruktur an (`wiki/`, `raw/`, `assets/`, `logs/`)
3. Testet die Azure-OpenAI-Verbindung via `test-connection.py`
4. Kopiert `watchers.json` und `code-repos.yaml.example` ins Vault (falls noch nicht da)
5. Registriert den Bootstrap-Task `KnowledgeTree-MetaSync` (läuft alle 15 Min,
   syncht `$VAULT_ROOT/watchers.json` mit den Windows Scheduled Tasks)
6. Führt MetaSync einmal sofort aus → alle `KnowledgeTree-*`-Tasks werden registriert

Danach laufen die Watcher (`PkwikiWatch`, `WikiSync`, `WikiPull`, `CodeWatch`) automatisch.
Verifizieren:

```powershell
Get-ScheduledTask -TaskName 'KnowledgeTree-*' | Format-Table TaskName, State
uv run test-connection.py    # erwartet: "OK — <deployment> antwortet: OK"
```

### Schritt 4 — Erstes Dokument verarbeiten

```powershell
# Datei nach raw/ legen — der at_logon-Watcher PkwikiWatch ingestet sie automatisch
Copy-Item mein-paper.pdf "$env:VAULT_ROOT\raw\pdfs\"

# Oder explizit:
uv run ingest.py "$env:VAULT_ROOT\raw\pdfs\mein-paper.pdf"

# Massen-Ingest aller bisher unverarbeiteten Dateien:
.\batch-ingest.ps1
```

### Code-Wiki aktivieren (optional)

`setup.ps1` hat `code-repos.yaml` im Vault aus dem Template angelegt. Vor dem ersten
Run die zu überwachenden Repos eintragen (Owner/Name, Branch, Sprache, Ticket-Pattern):

```powershell
notepad "$env:VAULT_ROOT\code-repos.yaml"
uv run code-watch.py    # Single-Poll-Test (kein --loop)
```

Sobald die YAML steht, ingested `KnowledgeTree-CodeWatch` alle 15 Min neue Commits und
scannt zusätzlich `raw/manuals/` auf neue PDF-Handbücher.

### Zweite Maschine aufsetzen

Da Vault, `.env`, `watchers.json` und `code-repos.yaml` alle in OneDrive liegen,
reichen vier Befehle:

```powershell
git clone <repo-url> C:\Code\knowledge-wiki
cd C:\Code\knowledge-wiki
setx VAULT_ROOT "C:\Users\<user>\OneDrive - <Firma>\knowledge-wiki"
# Neue Shell:
.\setup.ps1
```

`setup.ps1` erkennt die vorhandenen Vault-Dateien (überschreibt nichts) und registriert
nur die Scheduled Tasks lokal.

### Watcher-Status prüfen

```powershell
# Übersicht aller Tasks:
Get-ScheduledTask -TaskName 'KnowledgeTree-*' | Format-Table TaskName, State

# Detailliert (Last-Run, Last-Result, Working-Dir):
.\watcher-status.ps1

# MetaSync sofort triggern (nach watchers.json-Änderung):
Start-ScheduledTask -TaskName KnowledgeTree-MetaSync
```

### Troubleshooting

| Symptom | Ursache | Fix |
|---|---|---|
| `GITHUB_PAT muss in .env oder als Umgebungsvariable gesetzt sein` | `VAULT_ROOT` nicht in der Shell, in der der Scheduled Task läuft | `setx VAULT_ROOT "..."` ausführen, Shell neu starten, Tasks neu registrieren via `.\setup.ps1` |
| `KnowledgeTree-*` Task `LastResult: 0x1` | Working-Directory zeigt auf nicht-existierenden Pfad | `Get-ScheduledTask 'KnowledgeTree-*'` prüfen; `setup.ps1` re-registriert mit korrektem Pfad |
| `code-repos.yaml nicht gefunden` | Datei noch nicht im Vault | `setup.ps1` legt sie aus dem Template an; ggf. manuell `Copy-Item code-repos.yaml.example "$env:VAULT_ROOT\code-repos.yaml"` |
| Vision-API gibt nur `[Vision-Fehler]` zurück | Azure-Deployment fehlt Vision-Fähigkeit | In `.env` ein Vision-fähiges Deployment setzen (GPT-4.1+) |

---

## Skript-Referenz

### Ingest-Pipeline

| Skript | Beschreibung |
|--------|-------------|
| `watch.ps1` | FileSystemWatcher: pollt `raw/` alle 5s, löst automatisch Ingest aus |
| `extract.py` | Text + Vision-API-Bildbeschreibung + PyMuPDF-Fallback |
| `ingest.py` | Haupt-Pipeline: Dokument → strukturiertes JSON → Wiki-Seiten |
| `extract-images.py` | Batch-Vision für alle Bilder aus PPTX/PDF/DOCX |
| `synthesize.py` / `generate.py` | LLM-Synthese & PPTX-Generierung aus Wiki-Seiten |
| `manual-ingest.py` | PDF-Handbücher → Kapitelseiten mit Bild-Index |

### Code-Wiki (GitHub-Monitoring)

| Skript | Beschreibung |
|--------|-------------|
| `code-watch.py` | Pollt GitHub-Repos auf neue Commits + scannt `raw/manuals/` |
| `code-extract.py` | Commit-Diff → CommitDigest-JSON |
| `code-ingest.py` | CommitDigest → `wiki/code-wiki/<projekt>/` |
| `pm-synthesize.py` | Team-/PM-View-Aggregation |
| `wiki-sync.py` | Wiki-MD → `knowledge-wiki-archive` (GitHub-Backup) |

### Watcher-Infrastruktur

| Skript | Beschreibung |
|--------|-------------|
| `setup.ps1` | Ersteinrichtung: Templates kopieren, MetaSync-Task registrieren |
| `sync-watchers.ps1` | Syncht `watchers.json` → Windows Scheduled Tasks |
| `scan-raw.py` | Generischer Polling-Watcher für Projekte ohne eigenen Daemon |
| `test-connection.py` | Smoke-Test Azure-OpenAI- + GitHub-Verbindung |
| `watcher-status.ps1` | Status aller registrierten Watcher anzeigen |
| `install-watcher.ps1` / `register-task.ps1` | Legacy: einzelnen Watcher als Scheduled Task registrieren |

### Wartung & Recovery

| Skript | Beschreibung |
|--------|-------------|
| `batch-ingest.ps1` | Massen-Ingest aller bisher unverarbeiteten Dateien |
| `check-unseen.ps1` | Zeigt noch nicht ingested Dateien in `raw/` |
| `retry-failed.ps1` | Wiederholt fehlgeschlagene Ingests |
| `reextract-failed.ps1` / `reextract-missing.ps1` / `reextract-slides.ps1` | Re-Extraktion einzelner Kategorien |
| `rebuild-index.py` | Regeneriert `wiki/index.md` aus YAML-Frontmatter |
| `rebuild-code-wiki-index.py` | Patcht Obsidian-Wikilinks in `wiki/code-wiki/` |

---

## Watcher-System (Scheduled Tasks)

Windows Scheduled Tasks werden aus einer deklarativen Config im Vault verwaltet.
Neue Watcher hinzufügen = JSON-Eintrag in `$VAULT_ROOT/watchers.json` anhängen — kein
erneutes `setup.ps1` nötig. Ein Bootstrap-Task `KnowledgeTree-MetaSync` syncht alle 15 Min
die Config nach Windows (CREATE/UPDATE/DELETE der entsprechenden `KnowledgeTree-*`-Tasks).

```json
{
  "watchers": [
    {
      "name": "PkwikiWatch",
      "cwd": "C:\\code\\knowledge-wiki",
      "script": "watch.ps1",
      "runner": "powershell",
      "trigger": "at_logon",
      "description": "FileSystemWatcher (Echtzeit raw/-Ingest)"
    },
    {
      "name": "CodeWatch",
      "cwd": "C:\\code\\knowledge-wiki",
      "script": "code-watch.py",
      "runner": "uv",
      "trigger": "interval",
      "interval_minutes": 15,
      "timeout_minutes": 10,
      "description": "GitHub-Commits + Manuals-Pipeline"
    }
  ]
}
```

Details, Config-Schema und beide Watcher-Muster (`at_logon`-Daemon vs.
`scan-raw.py`-Polling): siehe [`CLAUDE.md`](CLAUDE.md#watcher-system-scheduled-tasks).

---

## Obsidian

1. [Obsidian](https://obsidian.md) herunterladen und installieren
2. **"Open folder as vault"** → `wiki/` auswählen
3. **Graph View** (`Ctrl+G`) — zeigt die Vernetzung aller Seiten als interaktiven Graphen

Obsidian erkennt Dateiänderungen live — neue Wiki-Seiten erscheinen direkt nach dem Ingest,
ohne Neustart. Cluster im Graph View entsprechen Kernthemen.

**Shortcuts:**
- `Ctrl+O` — Schnellsuche über alle Seiten
- `Ctrl+G` — Graph View (Vernetzung sichtbar machen)
- `[[` tippen — Verlinkungsdialog für manuelle Ergänzungen

---

## Verzeichnisstruktur

```
raw/               # Rohdokumente — hierhin neue Dateien ablegen
  pdfs/            # Papers, Reports, Whitepapers
  slides/          # Präsentationen (PPTX)
  docs/            # Word-Dokumente
  links/           # Web-Artikel als .md-Dateien
  inbox/           # Temporärer Eingang
  .cache/          # Auto-generierte Extrakte (nicht in Git)

Clippings/         # Obsidian-Web-Clipper-Ablage (.md) — Pipeline: clippings-ingest.py

wiki/              # Die Wissensbasis — nur lokal + OneDrive-Sync
  index.md         # Inhaltsverzeichnis aller Seiten
  log.md           # Append-only Aktivitätslog
  concepts/        # Konzept- und Technologieseiten
  entities/        # Personen, Unternehmen, Produkte
  sources/         # Zusammenfassung je Quelldokument
  syntheses/       # Themenübergreifende Analysen

ingest.py          # Haupt-Pipeline: Dokument → Wiki-Seiten
extract.py         # Extraktion: PPTX/DOCX/PDF → Markdown + Vision
watch.ps1          # Watcher: neue Dateien in raw/ → automatischer Ingest
clippings-ingest.py # Pipeline: Obsidian-Web-Clipper-Clips (Clippings/*.md) → Wiki
CLAUDE.md          # Schema & Regeln für den LLM-Maintainer
.env.example       # Vorlage fur Azure-Credentials
```

---

## Git-Strategie

| In Git | Nicht in Git |
|--------|-------------|
| `*.py`, `*.ps1` — Automation-Code | `wiki/` — Vault (OneDrive-Sync genügt) |
| `CLAUDE.md` — LLM-Schema | `raw/` — Rohdokumente (zu groß, persönlich) |
| `README.md`, `.env.example`, `.gitignore` | `.env` — API-Keys |

Der Vault (`wiki/`) wird über OneDrive synchronisiert und wächst kontinuierlich.
Er enthalt keine Logik — nur generierten Inhalt — und muss nicht versioniert werden.

---

## Bekannte Limitierungen

- **EMF/WMF-Vektorgrafiken in PPTX** können nicht via Vision analysiert werden — PIL unterstützt
  diese Windows-Metafile-Formate nicht. Betroffene Folien werden mit einem Hinweis markiert.
- **Sehr lange PDFs** werden auf 60.000 Zeichen gekürzt, bevor sie ans LLM gehen.
  Bei sehr dichten Dokumenten gehen Inhalte aus dem letzten Drittel verloren.
- **Vision-API-Kosten** sind höher als reine Textextraktion — bei vielen großen Slide-Decks
  summieren sich die API-Kosten. Reine Text-PDFs laufen kostengünstig über PyMuPDF.

---

## CLAUDE.md — das LLM-Schema

`CLAUDE.md` ist die zentrale Betriebsanleitung für das LLM. Sie definiert Seitentypen,
Frontmatter-Format, Wikilink-Konventionen, Qualitätsstandards und die drei Hauptoperationen:

- **INGEST** — Dokument zu Wiki-Seiten kompilieren
- **QUERY** — Wissensbasis befragen (ohne RAG-Infrastruktur)
- **LINT** — Wiki auf Widersprüche, Waisen und veraltete Einträge prüfen

Wenn Claude Code im Projektverzeichnis geöffnet wird, liest er `CLAUDE.md` automatisch
und weiß damit exakt, wie die Wiki gepflegt werden soll.

---

## GitHub Copilot Integration

Die Wiki kann als persistente Wissensbasis für **GitHub Copilot in VS Code** genutzt werden —
in jedem Workspace, nicht nur in diesem Repo.

### Strategie

Copilot liest `.instructions.md`-Dateien automatisch als Kontext ein. Durch eine globale
User-Level-Instruction wird Copilot bei jeder Session darauf hingewiesen, dass die Wiki
existiert und bei inhaltlichen Fragen konsultiert werden soll. Das ist kein RAG — Copilot
liest die Wiki-Seiten direkt als Dateien, sobald eine Frage gestellt wird.

**Wenn du fragst:** *„Was weiß ich über Foundation Models für Zeitreihen?"*  
Copilot liest `wiki/index.md`, identifiziert relevante Seiten und antwortet auf Basis
der bereits kompilierten Konzepte, Quellen und Synthesen — mit Verweisen auf konkrete Seiten.

### Installation (einmalig)

Die Instructions-Datei muss in den VS Code User-Prompts-Ordner kopiert werden.
Dieser Ordner ist workspace-unabhängig und wird mit VS Code Settings Sync synchronisiert.

```powershell
# Pfad zum VS Code User-Prompts-Ordner ermitteln
# Standard: C:\Users\<Name>\AppData\Roaming\Code\User\prompts\

# Datei kopieren
Copy-Item .github\copilot-user-instructions.md `
  "$env:APPDATA\Code\User\prompts\knowledge-wiki.instructions.md"
```

Die Datei `.github\copilot-user-instructions.md` in diesem Repo dient als Vorlage.
Nach dem Kopieren muss der Pfad in der Datei ggf. an den eigenen Benutzernamen angepasst werden.

### Enthaltene Dateien

| Datei | Zweck |
|-------|-------|
| `.github/copilot-instructions.md` | Workspace-Instruction: gilt nur in diesem Repo (automatisch) |
| `.github/copilot-user-instructions.md` | Vorlage für User-Level-Instruction: muss einmalig in den User-Prompts-Ordner kopiert werden |

### Nutzung

Nach der Installation kann Copilot in jedem VS Code-Workspace auf die Wiki zugreifen:

- **Inhaltliche Fragen** stellen — Copilot liest `wiki/index.md` und relevante Seiten
- **INGEST** — neue Dokumente einlesen: *„Ingest raw/pdfs/neues-paper.pdf"*
- **QUERY** — Wissensbasis befragen: *„Was weiß ich über Supply Chain Forecasting?"*
- **LINT** — Wiki auf Lücken und Widersprüche prüfen: *„Lint die Wiki"*

---

## Lizenz

MIT — siehe [LICENSE](LICENSE)
