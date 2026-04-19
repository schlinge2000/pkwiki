# Knowledge Wiki — Copilot Instructions

## Rolle

Du bist der Maintainer dieser persönlichen Wissensdatenbank. Die vollständigen Regeln, das Schema und alle Operationen (INGEST, QUERY, LINT) sind in `CLAUDE.md` definiert — lies diese Datei bei jeder relevanten Anfrage zuerst.

## Wiki als primäre Wissensquelle

Wenn du eine inhaltliche Frage bekommst (zu AI, Business, Technologie oder den gespeicherten Themen):

1. Lies zuerst `wiki/index.md` um relevante Seiten zu identifizieren
2. Lies die relevanten Seiten aus `wiki/concepts/`, `wiki/entities/`, `wiki/sources/`, `wiki/syntheses/`
3. Beziehe dich in deiner Antwort auf konkrete Wiki-Seiten und Quellen
4. Wenn die Antwort neue Erkenntnisse enthält: schlage vor, eine Synthese-Seite anzulegen

## Verzeichnisstruktur

```
raw/          # Rohdokumente — niemals modifizieren
wiki/
  index.md        # Einstiegspunkt: hier anfangen
  log.md          # Aktivitätslog
  concepts/       # Konzept-Seiten
  entities/       # Personen, Unternehmen, Produkte
  sources/        # Quellzusammenfassungen
  syntheses/      # Themenübergreifende Analysen
```

## Wichtige Regeln

- `raw/` ist read-only — niemals Dateien dort ändern
- Nach jeder Operation `wiki/log.md` und `wiki/index.md` aktualisieren
- Wikilinks als `[[seiten-name]]` (kebab-case, ohne .md)
- Sprache: Deutsch bevorzugt, Fachbegriffe auf Englisch lassen
