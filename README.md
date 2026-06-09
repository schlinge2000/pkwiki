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

## Weitere Pipelines

Neben dem Dokument-Ingest laufen drei zusätzliche Pipelines, die alle in denselben
Wiki-Vault schreiben — getriggert durch Scheduled Tasks via [`watchers.json`](#watcher-system-scheduled-tasks).

### Code-Wiki — GitHub-Commits als Wissensquelle

```
GitHub-Repos (z.B. demand-ai, scenario-mixture)
        │
        ▼ alle 15 Min via code-watch.py (GitHub API)
┌───────────────────────────────────────────────────────┐
│  code-extract.py                                      │
│  Commit-Diff + Issue-Refs ──► CommitDigest-JSON       │
└───────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────┐
│  code-ingest.py                                       │
│  CommitDigest ──► Azure OpenAI ──► Modul-/Ticket-Seiten│
└───────────────────────────────────────────────────────┘
        │
        ├──► wiki/code-wiki/<projekt>/modules/<modul>.md
        ├──► wiki/code-wiki/<projekt>/tickets/DAI-661.md
        ├──► wiki/code-wiki/<projekt>/changelog.md
        └──► wiki/code-wiki/<projekt>/index.md
```

`code-watch.py` pollt konfigurierte Repos (`$VAULT_ROOT/code-repos.yaml`, via OneDrive
multi-machine-synchron), lädt neue Commits seit dem letzten State, schickt jeden Diff
durchs LLM und erzeugt strukturierte Modul- und Ticket-Seiten. Tickets-Referenzen
(`DAI-123`, `#42`) werden als Obsidian-Wikilinks (`[[123]]`, `[[42]]`) eingebettet —
so entstehen automatisch Verbindungen zwischen Code-Änderungen und betroffenen Modulen.

**Use Case:** Du fragst Claude *„Was hat sich in der forecasting-pipeline in den letzten
zwei Wochen geändert?"* — er liest `wiki/code-wiki/demand-ai/changelog.md` plus die
verlinkten Modul- und Ticket-Seiten und gibt eine narrative Antwort statt einer
`git log`-Liste.

### Handbücher — PDF-Produkthandbücher als Wiki

```
raw/manuals/Administratorhandbuch.pdf  (300 Seiten)
        │
        ▼
┌───────────────────────────────────────────────────────┐
│  manual-ingest.py                                     │
│                                                       │
│  PyMuPDF TOC ──► Kapitelstruktur (max-level 2)        │
│  pro Kapitel:                                         │
│    Text + Screenshots ──► Vision API                  │
│    LLM ──► Schritt-für-Schritt-Wiki-Seite             │
└───────────────────────────────────────────────────────┘
        │
        ├──► wiki/manuals/<produkt>/<kapitel>.md     (mit ![[bild.jpg]])
        ├──► wiki/manuals/<produkt>/image-index.md
        ├──► wiki/manuals/<produkt>/assets/*.jpg
        └──► wiki/manuals/<produkt>/index.md
```

`code-watch.py` scannt `raw/manuals/*.pdf` per mtime — neue oder geänderte PDFs werden
automatisch ingested. Der Produkt-Slug wird aus dem Dateinamen abgeleitet
(Auto-Discovery); abweichende Slugs oder `max_level` lassen sich in
`code-repos.yaml` pro Datei overriden.

**Use Case:** Du fragst *„Wie konfiguriere ich Datenimport im ADD\*ONE BO Admin?"* —
Claude liest `wiki/manuals/addone-bo-admin/index.md`, findet das passende Kapitel und
zitiert wörtlich aus der Schritt-für-Schritt-Anleitung, inklusive eingebetteter
UI-Screenshots.

### Wiki-Archiv — versionierter Snapshot

```
$VAULT_ROOT/wiki/  ──► wiki-sync.py  ──►  github.com/schlinge2000/knowledge-wiki-archive
                          │
                          └─► alle 15 Min, optional bidirektional via --pull
```

Der lokale Vault wird über OneDrive zwischen Maschinen synchronisiert; `wiki-sync.py`
pusht zusätzlich nach GitHub. Das Archiv ist Backup, Audit-Trail und (perspektivisch)
Eingangspunkt für GitHub Actions, die ohne lokale Maschine ingesten können.

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

### `code-wiki/<projekt>/` — Code-Wissensbasis aus GitHub-Commits

Pro überwachtem Repo ein Ordner mit `index.md`, `changelog.md`, `modules/<modul>.md`
(Architektur, Abhängigkeiten, offene Punkte) und `tickets/<id>.md` (Ticket-Beschreibung
+ betroffene Module). Ticket-Referenzen in Commit-Messages (`DAI-123`, `#42`) werden
automatisch als Wikilinks verdrahtet.

### `manuals/<produkt>/` — PDF-Produkthandbücher

Eine Markdown-Seite pro Handbuchkapitel mit Schritt-für-Schritt-Anleitungen, eingebetteten
UI-Screenshots (`![[bild.jpg]]`) und Querverweisen auf andere Kapitel. `image-index.md`
listet alle Screenshots mit Vision-API-Beschreibungen — durchsuchbar und
präsentationsfähig.

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

```powershell
# 1. Repository klonen
git clone <repo-url> knowledge-wiki
cd knowledge-wiki

# 2. Credentials eintragen
cp .env.example .env
# .env oeffnen und Werte setzen (siehe unten)

# 3. Komplettes Setup (Vault, Scheduled Tasks, Connectivity-Check):
powershell -ExecutionPolicy Bypass -File .\setup.ps1

# Alternativ nur den Dokument-Watcher manuell starten:
powershell -ExecutionPolicy Bypass -File .\watch.ps1
```

`setup.ps1` registriert einen Bootstrap-Task `KnowledgeTree-MetaSync`, der alle 15 Min
`watchers.json` mit den Windows Scheduled Tasks abgleicht. Neue Watcher hinzufügen =
Eintrag in `$VAULT_ROOT/watchers.json` anhängen — kein erneutes `setup.ps1` nötig.

### Watcher-Status prüfen

```powershell
# Status aller registrierten Tasks:
powershell -ExecutionPolicy Bypass -File .\watcher-status.ps1

# MetaSync sofort triggern (nach watchers.json-Änderung):
Start-ScheduledTask -TaskName KnowledgeTree-MetaSync
```

### Konfiguration (`.env`)

```env
# Pflicht — Dokument-Ingest
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4.1
AZURE_OPENAI_API_VERSION=2025-04-01-preview

# Vault-Pfad (wo wiki/, raw/, assets/ liegen — z.B. OneDrive-Ordner)
VAULT_ROOT=C:\Users\<user>\OneDrive - <Firma>\knowledge-wiki

# Optional — Code-Wiki (GitHub-Monitoring via code-watch.py)
GITHUB_PAT=<personal-access-token>      # Scope: repo:read

# Optional — Wiki-Archiv-Sync (wiki-sync.py)
WIKI_ARCHIVE_PAT=<personal-access-token>  # Scope: repo
WIKI_ARCHIVE_REPO=<owner>/<archive-repo>
```

`VAULT_ROOT` ist neu zentral: Code (dieses Repo) und Daten (wiki/, raw/) sind getrennt.
Setz ihn auf einen OneDrive/SharePoint-Pfad — dann sind Vault, `watchers.json` und
`code-repos.yaml` automatisch zwischen Maschinen synchron.

### Erste Dokumente verarbeiten

```powershell
# Einzelnes Dokument
uv run ingest.py raw/pdfs/mein-paper.pdf

# Alle Dateien in raw/ auf einmal
.\batch-ingest.ps1
```

### Code-Wiki aktivieren (optional)

```powershell
# 1. Template ins Vault kopieren (macht setup.ps1 normalerweise automatisch)
Copy-Item code-repos.yaml.example "$env:VAULT_ROOT\code-repos.yaml"

# 2. Repos eintragen (Owner/Name, Branch, Sprache, Ticket-Pattern)
notepad "$env:VAULT_ROOT\code-repos.yaml"

# 3. Einmal manuell testen
uv run code-watch.py
```

Danach lädt `KnowledgeTree-CodeWatch` (in `watchers.json` definiert) alle 15 Min neue
Commits, ingested sie und scannt zusätzlich `raw/manuals/` auf neue PDFs.

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
raw/                # Rohdokumente — hierhin neue Dateien ablegen
  pdfs/             # Papers, Reports, Whitepapers
  slides/           # Präsentationen (PPTX)
  docs/             # Word-Dokumente
  links/            # Web-Artikel als .md-Dateien
  manuals/          # PDF-Handbücher (eigene Pipeline: manual-ingest.py)
  inbox/            # Temporärer Eingang
  .cache/           # Auto-generierte Extrakte (nicht in Git)

wiki/               # Die Wissensbasis — nur lokal + OneDrive-Sync
  index.md          # Inhaltsverzeichnis aller Seiten
  log.md            # Append-only Aktivitätslog
  picture_index.md  # Bild-Index (für QUERY/Präsentationen)
  concepts/         # Konzept- und Technologieseiten
  entities/         # Personen, Unternehmen, Produkte
  sources/          # Zusammenfassung je Quelldokument
  syntheses/        # Themenübergreifende Analysen
  code-wiki/        # Auto: GitHub-Commits → Modul- und Ticket-Seiten
    <projekt>/      # index.md, changelog.md, modules/, tickets/
  manuals/          # Auto: PDF-Handbücher → Kapitelseiten + Bilder
    <produkt>/      # index.md, image-index.md, assets/, <kapitel>.md

# Dokument-Pipeline
ingest.py           # Haupt-Pipeline: Dokument → Wiki-Seiten
extract.py          # Extraktion: PPTX/DOCX/PDF → Markdown + Vision
extract-images.py   # Batch-Vision für Bilder
watch.ps1           # FileSystemWatcher für raw/

# Code-Wiki-Pipeline
code-watch.py       # GitHub-Poller + raw/manuals/-Scanner
code-extract.py     # Commit-Diff → CommitDigest
code-ingest.py      # CommitDigest → wiki/code-wiki/
manual-ingest.py    # PDF-Handbuch → wiki/manuals/<produkt>/
wiki-sync.py        # Wiki-MD → GitHub-Archiv

# Watcher-Infrastruktur
setup.ps1           # Ersteinrichtung + MetaSync-Task
sync-watchers.ps1   # watchers.json → Scheduled Tasks
watchers.json       # Aktive Watcher-Liste (Template, Vault-Version aktiv)
code-repos.yaml.example  # Template für überwachte GitHub-Repos

CLAUDE.md           # Schema & Regeln für den LLM-Maintainer
.env.example        # Vorlage für Credentials + VAULT_ROOT
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
