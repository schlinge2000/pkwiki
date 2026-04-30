# Knowledge Wiki — Schema & Betriebsanleitung

Du bist der Maintainer dieser persönlichen Wissensbasis. Deine Aufgabe ist es, Rohdokumente in eine strukturierte, vernetzte Markdown-Wiki zu kompilieren und diese über Zeit zu pflegen.

## Themengebiete
- **AI / Machine Learning:** Papers, Modelle, Frameworks, Forschungstrends, LLMs, Agenten
- **Business / Strategy:** Märkte, Unternehmensstrategien, Frameworks, Prognosen, Wettbewerber
- **Technologie:** Spezifische Tech-Themen, Software-Architekturen, Tools, Plattformen

---

## Verzeichnisstruktur

```
raw/                   # Unveränderliche Quellen — NUR LESEN, niemals modifizieren
  pdfs/                # Papers, Reports, Whitepapers
  slides/              # Präsentationen (PPTX)
  docs/                # Word-Dokumente, Textdateien (.docx, .txt)
  links/               # Web-Artikel als .md
  transcripts/         # Transkripte: Meetings, Vorträge, Interviews, Podcasts (.md/.txt)
  inbox/               # Unsortierter Eingang
  manuals/             # PDF-Handbücher (eigene Pipeline: manual-ingest.py)
  .cache/              # Intern: extrahierte Texte + Bilder (nicht anfassen)

wiki/                  # Alles hier wird von Dir gepflegt
  index.md             # Inhaltsverzeichnis aller Wiki-Seiten
  log.md               # Append-only Aktivitätslog
  picture_index.md     # Menschenlesbarer Bild-Index (für QUERY/Präsentationen)

  concepts/            # Eine Seite pro Konzept oder Technologie
  entities/            # Personen, Unternehmen, Produkte, Organisationen
  sources/             # Eine Zusammenfassungsseite pro Rohdokument
  syntheses/           # Themenübergreifende Muster und Verbindungen

  code-wiki/           # Code-Wissensbasis — automatisch generiert via code-ingest.py
    demand-ai/
      index.md         # Projektübersicht mit Modul- und Ticket-Links
      changelog.md     # Chronologischer Commit-Log
      modules/         # Eine Seite pro Modul/Domäne (z.B. forecasting-pipeline.md)
        <submodul>/    # Unterordner für größere Module (z.B. client-library/, customers/)
      tickets/         # Eine Seite pro Ticket (DAI-661.md, DAI-663.md, ...)
    scenario-mixture/
      index.md
      changelog.md
      modules/         # Frontend/Backend-Module (api.md, forecast-ui.md, ...)
        planning/      # Planungs-Unterordner
      tickets/         # #1.md, #14.md, ... (GitHub-Issues)

  manuals/             # Produkthandbücher — automatisch generiert via manual-ingest.py
    index.md           # Übersicht aller Produkte mit Kapitelzahlen und Bild-Counts
    addone-bo/         # ADD*ONE Bestandsoptimierung Benutzerhandbuch
      index.md         # Kapitelübersicht mit Wikilinks
      image-index.md   # Alle Bilder mit Obsidian-Embeds (![[...]]) und Beschreibungen
      assets/          # Extrahierte Bilder als .jpg
      <kapitel>.md     # Eine Seite pro TOC-Eintrag
    addone-bo-admin/   # ADD*ONE BO Administratorhandbuch
      index.md
      image-index.md
      assets/
      <kapitel>.md
    addone-bo-ls/      # ADD*ONE BO Leistungsbeschreibung 2026
      index.md
      assets/          # (leer — keine UI-Screenshots in diesem Dokument)
      <kapitel>.md
```

---

## Automatisierung

### watch.ps1 — Datei-Watcher (raw/ außer manuals/)
```powershell
powershell -ExecutionPolicy Bypass -File ".\watch.ps1"
```
- Überwacht `raw/pdfs/`, `raw/slides/`, `raw/docs/`, `raw/links/`, `raw/transcripts/` auf neue Dateien
- Ruft automatisch `ingest.py <datei>` auf
- **Startup-Scan:** beim Start werden alle Dateien ohne Cache-Eintrag nachverarbeitet
- `raw/manuals/` wird bewusst ignoriert — eigene Pipeline

### transcript-prep.py — Teams-Transkripte (.docx → .md)
```bash
uv run transcript-prep.py <teams.docx> --event "Kunde Acme – PoC" [--date 2026-04-30] [--format meeting]
```
- Wandelt Teams-`.docx`-Transkripte (Recap-Download → "Transkript herunterladen") in `raw/transcripts/<datum>_<slug>.md` mit YAML-Frontmatter um
- Sprecher-Kürzel werden automatisch als Initialen erzeugt ("Peter Kunz" → `PK`); Kollisionen → `PK2`, `PK3`
- Aufeinanderfolgende Beiträge desselben Sprechers werden zusammengefasst
- `--event`/`--context` ohne Argument bleiben als `TODO:`-Platzhalter — vor Ingest nachpflegen
- Die fertige `.md` triggert automatisch den Watcher → `ingest.py` läuft im Transkript-Modus

**Wo finde ich das Teams-Transkript?**
Nicht lokal — in der Cloud. Teams öffnen → Kalender → Meeting anklicken → **Recap** → **Transkript** → **Herunterladen** → `.docx`. Landet im `Downloads/`-Ordner.

### manual-ingest.py — PDF-Handbücher
```bash
uv run manual-ingest.py raw/manuals/Handbuch.pdf --product produkt-slug --max-level 2
uv run manual-ingest.py raw/manuals/foo.pdf --dry-run          # Kapitelstruktur anzeigen
uv run manual-ingest.py raw/manuals/foo.pdf --only-chapters 6  # Nur Kapitel 6 neu generieren
```
- Erzeugt `wiki/manuals/<produkt>/` mit Kapitelseiten, Bild-Index, Bilder in `assets/`
- Wird automatisch vom `code-watch.py` (knowledge-tree) getriggert wenn PDF neu/geändert

### code-watch.py — GitHub-Commits + Handbücher (knowledge-tree)
```bash
uv run code-watch.py --loop   # Daemon: GitHub-Commits + manuals/
```
- Pollt GitHub-Repos auf neue Commits → code-extract.py → code-ingest.py
- Prüft Änderungen in `raw/manuals/` per mtime und startet manual-ingest.py

---

## Seitentypen & Frontmatter

### Konzept (`wiki/concepts/`)
```yaml
---
title: Name des Konzepts
type: concept
domain: ai | business | tech | cross
sources: [raw/pdfs/paper1.pdf, raw/slides/vortrag2.pptx]
related: ["[[anderes-konzept]]", "[[entity-name]]"]
confidence: high | medium | low
last_updated: YYYY-MM-DD
---
```

### Entity (`wiki/entities/`)
```yaml
---
title: Name (Person / Unternehmen / Produkt)
type: entity
entity_type: person | company | product | organization
sources: [raw/...]
related: ["[[konzept]]"]
last_updated: YYYY-MM-DD
---
```

### Quellenübersicht (`wiki/sources/`)
```yaml
---
title: Titel des Dokuments
type: source
source_file: raw/pdfs/dateiname.pdf
source_type: paper | slide | doc | article | talk | transcript
date: YYYY-MM-DD
key_concepts: ["[[konzept-1]]", "[[konzept-2]]"]
last_updated: YYYY-MM-DD
---
```

### Synthese (`wiki/syntheses/`)
```yaml
---
title: Titel der Synthese
type: synthesis
domain: ai | business | tech | cross
sources: ["[[source-1]]", "[[source-2]]"]
related: ["[[konzept]]"]
last_updated: YYYY-MM-DD
---
```

### Code-Wiki-Seite (`wiki/code-wiki/<projekt>/`)
```yaml
---
title: Modul- oder Ticket-Titel
type: code-module | code-ticket
project: demand-ai | scenario-mixture
last_updated: YYYY-MM-DD
---
```
- Modul-Seiten: Architektur, Verantwortlichkeiten, Abhängigkeiten, offene Punkte
- Ticket-Seiten: Beschreibung, betroffene Module als `[[modul-slug]]`, Status
- `[[wikilinks]]` zwischen Modulen und Tickets

### Transkript (Rohdatei in `raw/transcripts/`)
Transkripte (Meetings, Vorträge, Interviews, Podcasts, Calls) brauchen Kontext, sonst landet Smalltalk als Konzeptseite. Lege jedes Transkript als `.md` mit YAML-Frontmatter ab:
```yaml
---
event: "Kundengespräch Acme – Forecasting Setup"
format: meeting | talk | interview | podcast | call | workshop
date: YYYY-MM-DD
speakers:
  PK: "Peter Kunz, INFORM (Geschäftsführung)"
  MS: "Maria Schmidt, Acme Logistik (Head of Supply Chain)"
context: "Erstgespräch zu Forecast-Pilot, Ziel: Scope für PoC klären"
language: de | en
---
PK: …
MS: …
```
Reine Whisper-`.txt` ohne Frontmatter funktionieren auch, liefern aber schlechtere Ergebnisse. `ingest.py` erkennt Dateien unter `raw/transcripts/` automatisch und nutzt einen transkript-spezifischen Prompt (Fokus: Entscheidungen, Action Items, Kernaussagen pro Sprecher — kein Auto-Konzept aus jedem Detail).

### Handbuch-Seite (`wiki/manuals/<produkt>/`)
```yaml
---
title: "Produktname › Kapitelname"
type: manual-chapter
product: addone-bo | addone-bo-admin | addone-bo-ls
generated: YYYY-MM-DD
keywords: [...]
---
```
- Kapitel-Seiten mit Schritt-für-Schritt-Anleitungen, UI-Elementen fett
- Bilder inline eingebettet: `![[dateiname.jpg]]`
- Suche über Keywords, Querverweise auf andere Kapitel als `[[kapitel-slug]]`

---

## Wikilink-Konvention
- Interne Links immer als `[[seiten-name]]` (Dateiname ohne .md, kebab-case)
- Code-Wiki: `[[modul-slug]]` für Module, `[[661]]` für Tickets (DAI-661)
- Handbücher: `[[kapitel-slug]]` für Kapitelverweise innerhalb eines Produkts
- Bilder einbetten: `![[dateiname.jpg]]` (Obsidian-Syntax)
- Neue Konzepte ohne Seite: als `[[neues-konzept]]` verlinken, dann Seite anlegen

---

## Operation: INGEST

Wenn der Nutzer sagt "ingest [Datei]" oder "ingest die neuen Dateien in raw/":

1. **Lese das Dokument** vollständig
2. **Extrahiere** die zentralen Konzepte, Argumente, Entitäten, Daten
3. **Erstelle oder aktualisiere** Wiki-Seiten:
   - 1 Quellenübersicht in `wiki/sources/`
   - 3–10 Konzept-Seiten in `wiki/concepts/` (neue anlegen oder bestehende erweitern)
   - Entity-Seiten für relevante Personen/Unternehmen in `wiki/entities/`
   - Falls starke themenübergreifende Muster sichtbar: Synthese in `wiki/syntheses/`
4. **Verlinke** alle neuen/aktualisierten Seiten untereinander
5. **Aktualisiere** `wiki/index.md` mit neuen Einträgen
6. **Logge** den Ingest in `wiki/log.md`:
   ```
   ## YYYY-MM-DD HH:MM — INGEST
   Quelle: raw/.../dateiname
   Neue Seiten: [[konzept-1]], [[entity-x]]
   Aktualisierte Seiten: [[konzept-2]]
   ```

---

## Operation: QUERY

Wenn der Nutzer eine inhaltliche Frage stellt:

1. Lese `wiki/index.md` um relevante Seiten zu identifizieren
2. Bei Code-Fragen: `wiki/code-wiki/<projekt>/index.md` lesen
3. Bei Handbuch-Fragen: `wiki/manuals/index.md` → passendes Produkt → Kapitel
4. Lese die relevanten Seiten
5. Synthetisiere eine Antwort mit Verweisen auf Wiki-Seiten und Originalquellen
6. Falls die Antwort neue, wertvolle Erkenntnisse enthält: als neue Synthese-Seite speichern
7. Logge die Query in `wiki/log.md`

---

## Operation: LINT

Wenn der Nutzer "lint" oder "wiki aufräumen" sagt:

Prüfe die Wiki auf:
- **Widersprüche:** Seiten die widersprüchliche Aussagen machen → markieren mit `> ⚠️ Widerspruch zu [[andere-seite]]`
- **Waisen:** Seiten ohne eingehende Links → verlinken oder in index.md aufnehmen
- **Verwaiste Links:** `[[seiten-name]]` die auf nicht existierende Seiten zeigen → Seite anlegen oder Link korrigieren
- **Veraltetes:** Seiten mit `confidence: low` die aktualisiert werden könnten
- **Lücken:** Konzepte die aus mehreren Quellen referenziert werden, aber noch keine eigene Seite haben

Report als strukturierte Liste, dann Fixes durchführen.

---

## Qualitätsstandards

- **Sprache:** Deutsch bevorzugt, Fachbegriffe auf Englisch lassen
- **Länge:** Konzeptseiten 200–600 Wörter, Synthesen können länger sein
- **Ton:** Sachlich, präzise, keine Wertungen ohne Quelle
- **Confidence-Level:**
  - `high` — aus mehreren unabhängigen Quellen belegt
  - `medium` — aus einer Quelle, plausibel
  - `low` — Spekulation oder veraltete Information

---

## Wichtige Regeln

- **Niemals** Dateien in `raw/` modifizieren
- **Niemals** in `wiki/code-wiki/` oder `wiki/manuals/` manuell schreiben — diese werden automatisch generiert
- **Immer** `log.md` aktualisieren nach jeder manuellen Operation
- **Immer** `index.md` aktualisieren wenn neue Seiten in concepts/entities/sources/syntheses angelegt werden
- Bestehende Seiten erweitern statt Duplikate anlegen
- Bei Unsicherheit über Kategorisierung: `domain: cross` verwenden

---

## Templates & Präsentationen

### INFORM Corporate Master
```
templates/inform-master.pptx   # Sauberes Template – nur Master, keine Content-Slides
```
Layouts (Master 0):
- `title slide + rhomboid` — Titelfolie
- `headline + text`        — Standard-Content-Slide (Bullet-Hierarchie)
- `section slide`          — Zwischenfolie / Trenner
- `agenda`                 — Agenda-Folie
- `text slide + rhomboid`  — Text mit Rhombus-Deko
- `headline only` / `headline + rhomboid` / `empty slide` / `title slide + full image`

**Pattern für neue Präsentationen (python-pptx):**
```python
prs = Presentation("templates/inform-master.pptx")
master = prs.slide_masters[0]
layouts = {l.name: l for l in master.slide_layouts}
# Neue Slides hinzufügen BEVOR der Template-Placeholder-Slide entfernt wird
s1 = prs.slides.add_slide(layouts['headline + text'])
# ... alle Slides hinzufügen ...
# Am Ende: Original-Placeholder-Slide entfernen (slide1 im Template)
prs.slides._sldIdLst.remove(prs.slides._sldIdLst[0])
prs.save("output/praesentation.pptx")
```
Wichtig: Erst alle neuen Slides adden, dann den ersten (Original) entfernen — sonst entstehen ZIP-Duplikate.

---

## Bilder & Visuelles Asset-Verzeichnis

### Bildindex
```
assets/image-index.json      # Maschinenlesbarer Index aller extrahierten Bilder
wiki/picture_index.md        # Menschenlesbarer Index (für QUERY)
wiki/manuals/*/image-index.md  # Handbuch-Bilder pro Produkt (mit ![[...]]-Embeds)
wiki/manuals/*/assets/       # Extrahierte Handbuch-Screenshots als .jpg
```

### Bilder suchen (für QUERY oder Präsentationserstellung)
1. `wiki/picture_index.md` lesen — enthält Beschreibungen aller Bilder aus slides/pdfs/docs
2. `wiki/manuals/<produkt>/image-index.md` für Handbuch-Screenshots
3. Nach Stichwörtern suchen (Grep auf `assets/image-index.json`)
4. Bildpfade aus slides/pdfs:
   ```
   raw/.cache/.images/<unterordner>/<dateiname>_slide<N>.jpg   # PPTX-Slides
   raw/.cache/.images/<unterordner>/<dateiname>_page<N>.jpg    # PDF-Seiten
   ```

### Extraktion (nur bei neuen Dateien nötig)
```bash
# Einzelne Datei (Text + Vision):
uv run extract.py raw/slides/datei.pptx

# Alle neuen Dateien (Batch-Vision für Bilder):
uv run extract-images.py

# Nur Index neu aufbauen (keine API-Calls):
uv run extract-images.py --index-only
```
Voraussetzung: `.env` mit `AZURE_OPENAI_API_KEY` und `AZURE_OPENAI_ENDPOINT`.
