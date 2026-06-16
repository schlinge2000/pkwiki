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
  transcripts/         # Teams-Transkripte (.docx) — eigene Pipeline: transcript-ingest.py
  inbox/               # Unsortierter Eingang
  manuals/             # PDF-Handbücher (eigene Pipeline: manual-ingest.py)
  .cache/              # Intern: extrahierte Texte + Bilder (nicht anfassen)

Clippings/             # Obsidian-Web-Clipper-Ablage (.md) — eigene Pipeline: clippings-ingest.py
                       #   liegt im Vault-Root (Obsidian-Default), NICHT unter raw/

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

### watch.ps1 — FileSystemWatcher (raw/ außer manuals/)
```powershell
powershell -ExecutionPolicy Bypass -File ".\watch.ps1"
```
- Überwacht `raw/pdfs/`, `raw/slides/`, `raw/docs/`, `raw/links/` auf neue Dateien
- Ruft automatisch `ingest.py <datei>` auf
- **Startup-Scan:** beim Start werden alle Dateien ohne Cache-Eintrag nachverarbeitet
- `raw/manuals/` und `raw/transcripts/` werden bewusst ignoriert — eigene Pipelines
- Läuft als `at_logon`-Daemon (unbegrenzt) — siehe Watcher-System unten

### transcript-ingest.py — Teams-Transkripte (eigene Pipeline)
```bash
uv run transcript-ingest.py raw/transcripts/<datei.docx> \
    --event "Kunde Acme – PoC Setup" [--date 2026-04-30] [--format meeting] \
    [--language de] [--context "Erstgespräch zu Forecast-Pilot"] [--force]
uv run transcript-ingest.py raw/transcripts/foo.docx --no-ingest   # Nur Cache, kein LLM
```
- Parst die `.docx` mit Sprecher-Awareness (Teams-Header `Vorname Nachname H:MM[:SS]`)
- Generiert eine strukturierte `.md` mit Frontmatter (auto-Initialen `Peter Kunz` → `PK`, Kollisionen → `PK2`/`PK3`) in `raw/.cache/transcripts/<stem>.md`
- Ruft anschließend den regulären `ingest.py`-Flow auf — der erkennt den Pfad `raw/transcripts/` und schaltet auf den transkript-spezifischen Prompt (siehe Frontmatter unten)
- `--event`/`--context` als TODO-Platzhalter erlaubt; das LLM markiert sie dann als unklar
- Wird `raw/transcripts/` von `watch.ps1` bewusst ignoriert — Trigger erfolgt manuell oder über externen Daemon (z.B. `code-watch.py` in knowledge-tree, analog zur manuals-Pipeline)

**Wo finde ich das Teams-Transkript?**
Nicht lokal — in der Cloud. Teams öffnen → Kalender → Meeting → **Recap** → **Transkript** → **Herunterladen** als `.docx`. Datei dann nach `raw/transcripts/` legen und `transcript-ingest.py` aufrufen.

### clippings-ingest.py — Obsidian-Web-Clipper-Clips (eigene Pipeline)
```bash
uv run clippings-ingest.py              # Single-Poll: neue/geänderte Clips ingesten
uv run clippings-ingest.py --force      # alle Clips erneut ingesten
uv run clippings-ingest.py --dry-run    # nur anzeigen, kein LLM-Aufruf
uv run clippings-ingest.py --clippings-dir <pfad>   # abweichender Ordner
```
- Der **Obsidian Web Clipper** speichert geclippte Web-Seiten als `.md` im Vault-Ordner `Clippings/` — **außerhalb von `raw/`**, daher sieht `watch.ps1` sie nicht. Diese Pipeline schließt die Lücke.
- Scannt `Clippings/**/*.md` und ruft für jede neue/geänderte Datei den regulären `ingest.py`-Flow auf — fachlich wie eine `raw/links`-Quelle (Web-Artikel → Quellenübersicht + Konzepte + `index.md`/`log.md`).
- Eigener State (`path → mtime`) in `.clippings-state.json`, weil `ingest.py` für `.md`-Inputs keinen `raw/.cache`-Eintrag schreibt (Dedup wie bei `scan-raw.py`).
- Läuft als Scheduled Task `WikiClippings` (Single-Poll alle 15 Min, siehe `watchers.json`). `cwd` defaultet auf den Repo-Root, daher keine Pfad-Argumente nötig.
- **Alternativ** kann man den Web-Clipper-Zielordner direkt auf `raw/links/` umstellen — dann übernimmt der reguläre Watcher. Default-Clippings + diese Pipeline ist aber der wartungsärmere Weg (kein Obsidian-Reconfig).

### manual-ingest.py — PDF-Handbücher
```bash
uv run manual-ingest.py raw/manuals/Handbuch.pdf --product produkt-slug --max-level 2
uv run manual-ingest.py raw/manuals/foo.pdf --dry-run          # Kapitelstruktur anzeigen
uv run manual-ingest.py raw/manuals/foo.pdf --only-chapters 6  # Nur Kapitel 6 neu generieren
```
- Erzeugt `wiki/manuals/<produkt>/` mit Kapitelseiten, Bild-Index, Bilder in `assets/`
- Wird automatisch von `code-watch.py` getriggert wenn PDF neu/geändert
- Auto-Discovery: alle PDFs in `raw/manuals/*.pdf` werden erfasst — `products:`-Liste in
  `code-repos.yaml` ist optional und wirkt als Slug-Override pro Datei

### code-watch.py — GitHub-Commits + Handbücher
```bash
uv run code-watch.py            # Single-Poll (für Scheduled Task)
uv run code-watch.py --loop     # Daemon-Modus (nur für Debugging)
```
- Pollt GitHub-Repos auf neue Commits → `code-extract.py` → `code-ingest.py`
- Prüft Änderungen in `raw/manuals/` per mtime und startet `manual-ingest.py`
- Config: `$VAULT_ROOT/code-repos.yaml` (Multi-Machine via OneDrive), Fallback auf
  Repo-internen Pfad. Template: `code-repos.yaml.example`

### Sonstige Pipeline-Skripte

| Skript | Zweck |
|--------|-------|
| `clippings-ingest.py` | Obsidian-Web-Clipper-Clips (`Clippings/*.md`) → regulärer `ingest.py`-Flow |
| `code-extract.py` | GitHub-Commit-Diff → CommitDigest-JSON |
| `code-ingest.py` | CommitDigest → `wiki/code-wiki/<projekt>/` |
| `extract-images.py` | Batch-Vision für Bilder aus PPTX/PDF |
| `synthesize.py` | LLM-Synthese aus mehreren Quellen |
| `generate.py` | PPTX aus Konzept-/Synthese-Seiten erzeugen |
| `pm-synthesize.py` | Team-/PM-View-Aggregation |
| `wiki-sync.py` | Wiki-MD → `knowledge-wiki-archive` (GitHub) |
| `scan-raw.py` | Generischer File-Watcher (Polling-Wrapper für Projekte ohne eigenen Watcher) |
| `rebuild-index.py` | Regeneriert `wiki/index.md` aus YAML-Frontmatter |
| `rebuild-code-wiki-index.py` | Patcht Obsidian-Wikilinks in `wiki/code-wiki/` (Ticket-↔-Modul-Verlinkung) |
| `lint-links.py` | Graceful Link-Checker: löst `[[wikilinks]]` + bundle-relative Links auf, meldet Broken Links & Waisen; prüft `visibility` |
| `lint-tree.py` | Konsistenz-Check der Node-Rechte in `vault-tree.yaml` (read/write-Zonen vs. Hierarchie) |
| `test-connection.py` | Smoke-Test der Azure-OpenAI- und GitHub-Verbindung |

---

## Watcher-System (Scheduled Tasks)

Windows Scheduled Tasks werden aus einer deklarativen Config im Vault verwaltet.
Neue Watcher hinzufügen = JSON-Eintrag anhängen, ohne `setup.ps1` neu laufen zu lassen.

### Dateien

| Pfad | Rolle |
|------|-------|
| `watchers.json` (Repo) | Template, wird beim ersten Setup in den Vault kopiert |
| `$VAULT_ROOT/watchers.json` | **Aktive Watcher-Config** — hier editieren |
| `code-repos.yaml.example` (Repo) | Template für `code-watch.py` |
| `$VAULT_ROOT/code-repos.yaml` | **Aktive Repo-Liste** — hier editieren (OneDrive multi-machine-synchron) |
| `sync-watchers.ps1` | Syncht Config → Scheduled Tasks (CREATE/UPDATE/DELETE) |
| `setup.ps1` | Ersteinrichtung: Templates kopieren, MetaSync-Task registrieren |

### Config-Schema (`watchers.json`)

```json
{
  "watchers": [
    {
      "name": "WikiSync",
      "cwd": "C:\\code\\knowledge-wiki",
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

- `name` → Task wird als `KnowledgeTree-<name>` registriert
- `cwd` → Script-Wurzel (pro Eintrag separat, damit weitere Code-Projekte ihre Watcher anhängen können)
- `script` → Datei relativ zu `cwd` (Python oder `.ps1`)
- `runner` → `"uv"` (default, ruft `uv run <script>`) oder `"powershell"` (für `.ps1`-Watcher)
- `trigger` → `"interval"` (Single-Poll alle N Min) oder `"at_logon"` (Daemon, startet beim Login — für langlaufende `FileSystemWatcher`-Skripte)
- `interval_minutes` / `timeout_minutes` → nur bei `trigger: "interval"`; `at_logon`-Daemons laufen unbegrenzt

### MetaSync (Live-Reload)

`setup.ps1` registriert **einen** Bootstrap-Task `KnowledgeTree-MetaSync`, der alle 15 Min
`sync-watchers.ps1` ausführt. Änderungen an `watchers.json` wirken binnen 15 Min;
sofort triggern via:

```powershell
Start-ScheduledTask -TaskName KnowledgeTree-MetaSync
# oder direkt:
powershell -ExecutionPolicy Bypass -File .\sync-watchers.ps1
```

### File-Watcher: zwei Muster

**1. Projekt hat eigenen Daemon** (z.B. `watch.ps1` mit nativem `FileSystemWatcher`):
per `runner: "powershell"` + `trigger: "at_logon"` direkt einbinden — Echtzeit-Reaktion,
kein Polling.

**2. Projekt hat nur Per-Datei-Ingest** (kein eigener Watcher): `scan-raw.py` als
generischer Polling-Wrapper. Scannt periodisch, pflegt State (`path → mtime`), ruft den
Ingest-Befehl pro neuer/geänderter Datei. `interval_minutes: 1` ist das Windows-Minimum.

### Konvention: Single-Poll statt Loop

Watcher-Skripte führen **einen** Durchlauf aus und beenden sich. Der Task Scheduler
taktet das Intervall (analog zu cron). `--loop`-Modi existieren nur noch für Debugging.

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
visibility: public | customer | internal | team | personal
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
visibility: public | customer | internal | team | personal
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
visibility: public | customer | internal | team | personal
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
visibility: public | customer | internal | team | personal
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

### Transkript (Rohdatei in `raw/transcripts/` als `.docx`)
Transkripte (Meetings, Vorträge, Interviews, Podcasts, Calls) brauchen Kontext, sonst landet Smalltalk als Konzeptseite. Eingang ist das **Teams-`.docx`** wie aus dem Recap heruntergeladen — `transcript-ingest.py` erzeugt die strukturierte `.md` mit Frontmatter:
```yaml
---
event: "Kundengespräch Acme – Forecasting Setup"
format: meeting | talk | interview | podcast | call | workshop
date: YYYY-MM-DD
language: de | en
speakers:
  PK: "Peter Kunz"
  MS: "Maria Schmidt"
context: "Erstgespräch zu Forecast-Pilot, Ziel: Scope für PoC klären"
---
**PK:** Guten Tag …
**MS:** Hallo …
```
`event` und `context` werden aus den CLI-Flags übernommen (oder bleiben als TODO-Platzhalter). Sprecher-Initialen werden automatisch generiert (`Peter Kunz` → `PK`, Kollisionen → `PK2`). Das LLM erhält im Anschluss einen transkript-spezifischen Prompt (Fokus: Quellenübersicht mit Kontext / Kernaussagen je Sprecher / Entscheidungen / Action Items / Zitate; max. 0–3 Konzeptseiten; kein Smalltalk).

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

## Sichtbarkeit & Wissensschichten

Jede kuratierte Seite (`concepts/`, `entities/`, `sources/`, `syntheses/`) trägt ein
`visibility:`-Feld, das die **Wissensschicht** klassifiziert — von offen nach restriktiv:

| Stufe | Wer darf lesen |
|-------|----------------|
| `public`   | extern sichtbar, keine Einschränkung |
| `customer` | Kunden / externe Software-User eines Produkts |
| `internal` | alle Firmenmitarbeiter |
| `team`     | nur das jeweilige Team (Node) |
| `personal` | nur der Eigentümer-Node |

- **Default (Feld fehlt) = `personal`** — *safe by default*: lieber zu restriktiv als
  versehentlich geleakt. Ein fehlendes Feld ist kein Fehler, nur ein Lint-Hinweis.
- **OKF-kompatibel:** `visibility` ist ein Custom-Key; Consumer, die es nicht kennen,
  dürfen die Seite nicht verwerfen (graceful degradation).
- Die Stufe ist eine **Klassifizierung, keine Sicherheitsgrenze** — die Durchsetzung
  („`visibility ≤ clearance`" vor der Kontextbefüllung) gehört in den Retrieval-Layer
  (siehe Epic #28, T3), nicht in die Markdown-Datei.
- **Auto-generierte Bundles** (`code-wiki/`, `manuals/`) tragen *kein* Feld pro Seite —
  sie erben die Sichtbarkeit ihres Nodes (siehe T5). `lint-links.py` prüft sie daher nicht.
- Prüfung: `uv run lint-links.py` meldet ungültige Werte und (mit
  `--show-missing-visibility`) Seiten ohne Feld.

### Node-Rechte (`vault-tree.yaml`)

Der Wissensbaum (`company → team → personal`) trägt pro Node ein `rights`-Block, das die
Read-/Write-Zonen explizit macht (vorher implizit über SharePoint/OneDrive-ACL):

```yaml
rights:
  clearance: internal           # höchste (restriktivste) Stufe, die der Node LESEN darf
  default_visibility: internal  # Default-visibility für hier erzeugte Seiten (<= clearance)
  read:  [self, <vorfahren>]    # nur nach oben lesen — keine seitlichen Leaks
  write: [self, <nachfahren>]   # nach oben schreiben = Promotion (Review-Gate, T4)
```

- **Read nur nach oben:** ein Node liest sich selbst + Vorfahren, nie Geschwister-/Fremd-Nodes.
- **Write nur nach unten:** Hochstufen in einen Eltern-Layer ist Promotion (T4), kein Default.
- **`clearance` nimmt nach unten nicht ab** — sonst könnte ein Kind den Eltern-Layer nicht lesen.
- Prüfung: `uv run lint-tree.py [--strict]` validiert diese Regeln gegen die Hierarchie.

### Agenten-Capabilities (`vault-tree.yaml` › `agents:`)

Ein Agent erhält ein Capability-Profil, das `clearance` (Lese-Obergrenze) mit Read-/Write-Scope
verbindet. **Effektiver Lesezugriff** auf eine Seite:

> `rank(visibility) <= rank(clearance)`  **und**  `node(seite) ∈ read_scope`

```yaml
agents:
  - id: <slug>
    clearance: <stufe>          # höchste visibility, die der Agent lesen darf
    read_scope:  [<node>, ...]  # Nodes, deren Inhalt sichtbar ist
    write_scope: <node> | session   # 'session' = ephemerer Sandbox-Node (kein Persist)
```

Zwei Referenz-Profile (in `vault-tree.yaml.example`):

| Profil | clearance | read_scope | write_scope |
|--------|-----------|------------|-------------|
| **Produkt-Agent** (externe Software-User) | `customer` | freigegebene Nodes (z.B. `company`) | `session` (Sandbox) |
| **Interner Team-Copilot** | `team` | eigener Team-Node + `company` | eigener Team-Node |

Regeln (von `lint-tree.py` geprüft): `read_scope`/`write_scope` müssen existierende Nodes
referenzieren; ein Agent darf nicht in einen Node schreiben, dessen Default-Sichtbarkeit über
seiner `clearance` liegt (er könnte die Seite nicht zurücklesen); Low-Trust-Agenten
(`clearance ≤ customer`) sollten in einen `session`-Sandbox schreiben statt in einen
persistenten Node (Promotion → T4). **Durchsetzung** des Filters erfolgt im Retrieval-Layer (T3).

---

## Wikilink-Konvention
- Interne Links immer als `[[seiten-name]]` (Dateiname ohne .md, kebab-case)
- Code-Wiki: `[[modul-slug]]` für Module, `[[661]]` für Tickets (DAI-661)
- Handbücher: `[[kapitel-slug]]` für Kapitelverweise innerhalb eines Produkts
- Bilder einbetten: `![[dateiname.jpg]]` (Obsidian-Syntax)
- Neue Konzepte ohne Seite: als `[[neues-konzept]]` verlinken, dann Seite anlegen

### Portable Links (bundle-relativ) — optional
`[[wikilinks]]` sind die Obsidian-native Default-Form und bleiben es. Wo ein Link
**außerhalb von Obsidian** stabil bleiben muss (GitHub-Rendering, Archiv-Repo, fremde
Tools), ist zusätzlich die **bundle-relative** Form erlaubt — angelehnt an das
[Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf):
ein Markdown-Link, dessen Pfad mit `/` ab dem `wiki/`-Root beginnt.

```markdown
[OpenAI](/entities/openai.md)        # bundle-relativ, ab wiki/ — portabel
[[openai]]                            # Obsidian-Wikilink — Default
```

- `lint-links.py` löst **beide** Formen auf und prüft sie (siehe Operation: LINT).
- Regel wie bei OKF: Links sind gerichtete Kanten; ein kaputtes Ziel ist **kein Fehler,
  der etwas abbricht**, sondern ein Lint-Befund (Ziel ggf. noch anzulegen).

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

Erst **deterministisch** vorprüfen, dann inhaltlich:
```bash
uv run lint-links.py                          # Broken Links + Waisen + ungültige visibility
uv run lint-links.py --show-missing-visibility # zusätzlich: Seiten ohne visibility-Feld
uv run lint-links.py --strict                 # Exit 1 bei Broken Links / ungültiger visibility
```

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
- **Graceful degradation** (OKF-Prinzip „tolerate, don't reject"): Pipeline-Skripte, die über
  viele Seiten iterieren, dürfen an einer fehlerhaften Einzelseite **nie den ganzen Lauf
  abbrechen** — Seite überspringen, Warnung loggen, weitermachen. Unbekannte Frontmatter-Felder,
  unbekannte `type`-Werte und kaputte Links werden toleriert, nicht verworfen.

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
