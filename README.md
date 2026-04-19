# Knowledge Wiki

> Dokument ablegen. Fertig. Das LLM macht den Rest.

Statt Notizen zu tippen, werfe ich PDFs, Präsentationen und Word-Dokumente in einen Ordner.
Ein Watcher erkennt neue Dateien, extrahiert den Inhalt (inkl. Bilder via Vision-API) und lässt
ein LLM daraus strukturierte, verlinkte Wiki-Seiten schreiben — automatisch, im Hintergrund.

Inspiriert von [Andrej Karpathys LLM-Wiki-Idee](https://x.com/karpathy/status/1751350002281300461):
Das LLM als "Compiler" — Rohdokumente rein, Wissensbasis raus.

## Warum kein RAG?

RAG (Retrieval + Generierung zur Laufzeit) beantwortet Fragen über Dokumente.
Dieses System macht etwas anderes: Es **kompiliert Wissen einmalig** in eine lesbare,
navigierbare Wissensbasis.

- Keine Vektordatenbank, kein Embedding, kein Index
- Jede neue Quelle reichert bestehende Seiten an und verlinkt sie
- Das Ergebnis ist **lesbar** — in Obsidian, im Terminal, überall

## Wie es funktioniert

```
raw/mein-dokument.pdf
        ↓  extract.py  (Text + Bildanalyse via Vision-API)
raw/.cache/mein-dokument.md
        ↓  ingest.py   (Azure OpenAI → strukturiertes JSON)
wiki/concepts/konzept-a.md
wiki/concepts/konzept-b.md
wiki/sources/mein-dokument.md
wiki/index.md  ← wird automatisch aktualisiert
```

## Voraussetzungen

- [`uv`](https://docs.astral.sh/uv/) (`winget install astral-sh.uv`)
- Azure OpenAI Ressource mit GPT-4-class Deployment (Vision-fähig für PPTX)
- [Obsidian](https://obsidian.md) als lokaler Viewer (optional, empfohlen)

## Einrichtung

```powershell
# 1. Repository klonen
git clone <repo-url> knowledge-wiki
cd knowledge-wiki

# 2. Azure-Credentials eintragen
cp .env.example .env
# .env öffnen und Werte setzen

# 3. Watcher starten (überwacht raw/ auf neue Dateien)
powershell -ExecutionPolicy Bypass -File .\watch.ps1
```

## Verzeichnisstruktur

```
raw/               # Rohdokumente — hierhin neue Dateien ablegen
  pdfs/            # Papers, Reports, Whitepapers
  slides/          # Präsentationen (PPTX)
  docs/            # Word-Dokumente
  .cache/          # Auto-generierte Extrakte (nicht in Git)

wiki/              # Die Wissensbasis — nur lokal + OneDrive-Sync
  index.md         # Inhaltsverzeichnis aller Seiten
  log.md           # Append-only Aktivitätslog
  concepts/        # Konzept- und Technologieseiten
  entities/        # Personen, Unternehmen, Produkte
  sources/         # Zusammenfassung je Quelldokument
  syntheses/       # Themenübergreifende Analysen

ingest.py          # Haupt-Pipeline: Dokument → Wiki-Seiten (Azure OpenAI)
extract.py         # Extraktion: PPTX/DOCX/PDF → Markdown + Vision
watch.ps1          # Watcher: neue Dateien in raw/ → automatischer Ingest
CLAUDE.md          # Schema & Regeln für den LLM-Maintainer
```

## Hilfsskripte

| Skript | Zweck |
|--------|-------|
| `check-unseen.ps1` | Zeigt Dateien in raw/ die noch nicht ingested wurden |
| `retry-failed.ps1` | Wiederholt fehlgeschlagene Ingests |
| `reextract-failed.ps1` | Re-extrahiert Slides mit Vision-Fehlern im Cache |
| `reextract-slides.ps1` | Komplette Re-Extraktion aller Slide-Decks |

## Obsidian einrichten

1. [Obsidian](https://obsidian.md) herunterladen
2. **"Open folder as vault"** → `wiki/` auswählen
3. **Graph View** öffnen (`Ctrl+G`) — zeigt die Vernetzung aller Seiten

Obsidian erkennt Dateiänderungen live — neue Wiki-Seiten erscheinen sofort nach dem Ingest.

**Nützliche Shortcuts:**
- `Ctrl+O` — Schnellsuche über alle Seiten
- `Ctrl+G` — Graph View (Cluster = Kernthemen)
- `[[` tippen — Verlinkungsdialog für manuelle Ergänzungen

## Git-Strategie

| In Git | Nicht in Git |
|--------|-------------|
| `*.py`, `*.ps1` — Automation-Code | `wiki/` — Vault (OneDrive-Sync reicht) |
| `CLAUDE.md` — LLM-Schema | `raw/` — Rohdokumente (zu groß, persönlich) |
| `README.md`, `.env.example` | `.env` — API-Keys |
| `.gitignore` | `raw/.cache/` — generierte Extrakte |

Der Vault (`wiki/`) wird über OneDrive synchronisiert und ist nicht versioniert —
er wächst kontinuierlich und enthält keine Logik, nur generierten Inhalt.

## CLAUDE.md

Die zentrale Schema-Datei definiert Seitentypen, Frontmatter-Format, Wikilink-Konventionen
und Qualitätsstandards. Wenn Claude im Verzeichnis geöffnet wird, liest er `CLAUDE.md`
automatisch und weiß damit wie die Wiki gepflegt werden soll.
