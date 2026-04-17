# Knowledge Wiki

Persönliche Wissensbasis nach dem [Karpathy LLM-Wiki-Prinzip](https://x.com/karpathy/status/1751350002281300461):
Ein LLM fungiert als „Compiler" — er liest Rohdokumente und schreibt daraus eine strukturierte, verlinkte Markdown-Wiki.

## Idee

Statt RAG (Retrieval + Generierung zur Laufzeit) wird das Wissen **einmalig kompiliert**:
- Du legst PDFs, PPTX, DOCX in `raw/`
- Der Ingest-Workflow liest das Dokument und schreibt strukturierte Wiki-Seiten
- Die Wiki akkumuliert über Zeit, jede neue Quelle reichert bestehende Seiten an
- Ergebnis: Vollständig verlinkte, lesbare Wissensbasis — kein Vektor-Index, kein Embedding

## Voraussetzungen

- [`uv`](https://docs.astral.sh/uv/) installiert (`winget install astral-sh.uv` oder via Chocolatey)
- Azure OpenAI Ressource mit einem GPT-4-class Deployment
- (Optional) [Obsidian](https://obsidian.md) als lokaler Viewer

## Einrichtung

```powershell
# 1. Repository klonen
git clone <repo-url> knowledge-wiki
cd knowledge-wiki

# 2. Umgebungsvariablen setzen
cp .env.example .env
# .env öffnen und Azure-Credentials eintragen

# 3. Watcher als dauerhaften Hintergrundprozess installieren
# (startet automatisch beim Windows-Login)
powershell -ExecutionPolicy Bypass -File .\install-watcher.ps1
```

## Verzeichnisstruktur

```
raw/               # Rohdokumente — hierhin neue Dateien ablegen
  pdfs/            # Papers, Reports, Whitepapers
  slides/          # Präsentationen (PPTX, PDF)
  docs/            # Word-Dokumente
  links/           # Web-Artikel als .md
  .cache/          # Auto-generierte Extrakte (nicht in Git)

wiki/              # Die eigentliche Wissensbasis (in Git)
  index.md         # Inhaltsverzeichnis aller Seiten
  log.md           # Append-only Aktivitätslog
  concepts/        # Konzept- und Technologieseiten
  entities/        # Personen, Unternehmen, Produkte
  sources/         # Zusammenfassung je Quelldokument
  syntheses/       # Themenübergreifende Analysen

ingest.py          # Haupt-Ingest-Script (Azure OpenAI)
extract.py         # Extraktion: PPTX/DOCX/PDF → Markdown
watch.ps1          # FileSystemWatcher: neue Dateien → auto-ingest
install-watcher.ps1 # Watcher als Windows Scheduled Task einrichten
extract-all.ps1    # Batch-Extraktion aller Dateien in raw/
CLAUDE.md          # Schema & Regeln für den LLM-Maintainer
```

## Workflow

### Automatisch (empfohlen)
1. Watcher ist aktiv (nach `install-watcher.ps1`)
2. Neue Datei in `raw/` ablegen
3. Ingest läuft automatisch im Hintergrund (~1–2 Minuten)
4. Neue Wiki-Seiten erscheinen in `wiki/`

### Manuell
```powershell
# Einzelne Datei ingestieren
uv run ingest.py raw\slides\meine-praesentation.pptx

# Alle noch nicht inggestierten Dateien extrahieren
.\extract-all.ps1
```

### Mit Claude (interaktiv)
Öffne eine Claude-Session im knowledge-wiki-Verzeichnis und nutze:
- **`ingest raw/slides/datei.pptx`** — Dokument in Wiki überführen
- **`query: Was weiß ich über Foundation Models?`** — Wiki durchsuchen + synthetisieren
- **`lint`** — Wiki auf Widersprüche, Waisen und Lücken prüfen

## Obsidian einrichten

Obsidian bietet einen visuellen Graph aller Wiki-Seiten und erleichtert die Navigation.

1. [Obsidian](https://obsidian.md) herunterladen und installieren
2. **"Open folder as vault"** → `wiki/` Ordner auswählen
   - ⚠️ Den Vault auf `wiki/` setzen (nicht das Root-Verzeichnis)
3. Empfohlene Einstellungen:
   - **Settings → Files & Links → Default location for new notes:** `In the folder specified below` → `wiki/`
   - **Settings → Files & Links → Detect all file extensions:** aktivieren
   - **Settings → Core Plugins → Graph View:** aktivieren
4. **Graph View** öffnen (`Ctrl+G`) — zeigt die Vernetzung aller Seiten
5. Seiten werden automatisch aktualisiert sobald der Watcher neue Seiten schreibt (Obsidian erkennt Dateiänderungen live)

### Obsidian-Tipps
- **`Ctrl+O`** — Schnellsuche über alle Seiten
- **`[[`** tippen — öffnet Verlinkungsdialog (nützlich für manuelle Ergänzungen)
- **Graph View** — Cluster erkennen (dicht verlinkte Konzepte = Kernthemen)
- **Backlinks-Panel** — zeigt welche anderen Seiten auf die aktuelle verweisen
- Obsidian ist rein lokal, synchronisiert nichts — die Dateien liegen in deinem OneDrive

## Über `CLAUDE.md`

Die `CLAUDE.md` ist die zentrale Schema-Datei. Sie definiert:
- Seitentypen und Frontmatter-Format
- Wikilink-Konventionen
- Die drei Operationen: INGEST, QUERY, LINT
- Qualitätsstandards (Sprache, Confidence-Level, Länge)

Wenn Claude im Verzeichnis geöffnet wird, liest er `CLAUDE.md` automatisch und weiß damit wie die Wiki gepflegt werden soll.

## Git-Strategie

| Enthalten | Ausgeschlossen |
|-----------|---------------|
| `wiki/` — alle Markdown-Seiten | `raw/` — Rohdokumente (zu groß, persönlich) |
| `*.py`, `*.ps1` — Automation-Scripts | `.env` — API-Keys |
| `CLAUDE.md` — Schema | `raw/.cache/` — generierte Extrakte |
| `README.md`, `.env.example` | `wiki/.obsidian/` — Obsidian-Config |

Die `wiki/` ist vollständig versioniert — jede neue Seite, jede Aktualisierung ist nachvollziehbar.
