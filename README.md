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
> Antwort: *„Du hast schon selbst eine genutzt — Folie 18, FINAL BO KI Webinar: ein Reh im Scheinwerferlicht. Für ein Risiko das der Forecast nicht gesehen hat."*
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

```powershell
# 1. Repository klonen
git clone <repo-url> knowledge-wiki
cd knowledge-wiki

# 2. Azure-Credentials eintragen
cp .env.example .env
# .env oeffnen und Werte setzen (siehe unten)

# 3. Watcher starten — ueberwacht raw/ auf neue Dateien
powershell -ExecutionPolicy Bypass -File .\watch.ps1

# Oder: als Windows Scheduled Task installieren (startet automatisch bei Login)
powershell -ExecutionPolicy Bypass -File .\install-watcher.ps1
```

### Konfiguration (`.env`)

```env
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2025-04-01-preview   # optional, neueste Version empfohlen
```

### Erste Dokumente verarbeiten

```powershell
# Einzelnes Dokument
python ingest.py raw/pdfs/mein-paper.pdf

# Alle Dateien in raw/ auf einmal (Batch-Extraktion + Ingest)
.\extract-all.ps1
```

---

## Skript-Referenz

| Skript | Beschreibung |
|--------|-------------|
| `watch.ps1` | Watcher: pollt `raw/` alle 5s, loest automatisch Ingest aus (1 paralleler Job) |
| `install-watcher.ps1` | Installiert Watcher als Windows Scheduled Task (startet bei Login) |
| `extract.py` | Extraktion: Text + Vision-API-Bildbeschreibung + PyMuPDF-Fallback |
| `ingest.py` | Haupt-Pipeline: Dokument → strukturiertes JSON → Wiki-Seiten |
| `extract-all.ps1` | Batch-Extraktion aller Dateien in `raw/` |
| `check-unseen.ps1` | Zeigt noch nicht ingested Dateien in `raw/` |
| `retry-failed.ps1` | Wiederholt fehlgeschlagene Ingests |
| `reextract-failed.ps1` | Re-extrahiert Slides mit Vision-Fehlern im Cache |
| `reextract-slides.ps1` | Komplett-Re-Extraktion aller Slide-Decks |

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

## Lizenz

MIT — siehe [LICENSE](LICENSE)
