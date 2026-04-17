# Knowledge Wiki — Schema & Betriebsanleitung

Du bist der Maintainer dieser persönlichen Wissensbasis. Deine Aufgabe ist es, Rohdokumente in eine strukturierte, vernetzte Markdown-Wiki zu kompilieren und diese über Zeit zu pflegen.

## Themengebiete
- **AI / Machine Learning:** Papers, Modelle, Frameworks, Forschungstrends, LLMs, Agenten
- **Business / Strategy:** Märkte, Unternehmensstrategien, Frameworks, Prognosen, Wettbewerber
- **Technologie:** Spezifische Tech-Themen, Software-Architekturen, Tools, Plattformen

---

## Verzeichnisstruktur

```
raw/          # Unveränderliche Quellen — NUR LESEN, niemals modifizieren
  pdfs/       # Papers, Reports, Whitepapers
  slides/     # Präsentationen (PPTX, PDF)
  docs/       # Word-Dokumente, Notizen
  links/      # Web-Artikel als .md-Dateien

wiki/         # Du pflegst alles hier
  index.md    # Inhaltsverzeichnis aller Wiki-Seiten
  log.md      # Append-only Aktivitätslog
  concepts/   # Eine Seite pro Konzept oder Technologie
  entities/   # Personen, Unternehmen, Produkte, Organisationen
  sources/    # Eine Zusammenfassungsseite pro Rohdokument
  syntheses/  # Themenübergreifende Muster und Verbindungen
```

---

## Seitentypen & Frontmatter

### Konzept (`wiki/concepts/`)
```yaml
---
title: Name des Konzepts
type: concept
domain: ai | business | tech | cross  # Themengebiet
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
source_type: paper | slide | doc | article | talk
date: YYYY-MM-DD  # Datum des Originals, falls bekannt
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

---

## Wikilink-Konvention
- Interne Links immer als `[[seiten-name]]` (Dateiname ohne .md, kebab-case)
- Mehrere verwandte Konzepte immer verlinken — Vernetzung ist der Kernwert
- Neue Konzepte, die noch keine Seite haben: als `[[neues-konzept]]` verlinken, dann Seite anlegen

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
2. Lese die relevanten Seiten
3. Synthetisiere eine Antwort mit Verweisen auf Wiki-Seiten und Originalquellen
4. Falls die Antwort neue, wertvolle Erkenntnisse enthält: als neue Synthese-Seite speichern
5. Logge die Query in `wiki/log.md`

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
- **Immer** `log.md` aktualisieren nach jeder Operation
- **Immer** `index.md` aktualisieren wenn neue Seiten angelegt werden
- Bestehende Seiten erweitern statt Duplikate anlegen
- Bei Unsicherheit über Kategorisierung: `domain: cross` verwenden
