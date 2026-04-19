---
applyTo: "**"
---

# Persönliche Wissensdatenbank (Knowledge Wiki)

Du hast Zugriff auf eine persönliche Wissensdatenbank unter:
`c:\Users\<DEIN-USERNAME>\OneDrive - INFORM GmbH\knowledge-wiki\wiki\`

> **Hinweis:** Passe den Pfad oben an deinen eigenen Benutzernamen an, bevor du die Datei nutzt.
> Installationspfad: `%APPDATA%\Code\User\prompts\knowledge-wiki.instructions.md`

## Bei inhaltlichen Fragen (AI, Business, Technologie, Prognosen, Supply Chain)

1. Lies zuerst `wiki/index.md` um relevante Seiten zu identifizieren
2. Lies die relevanten Seiten aus `wiki/concepts/`, `wiki/entities/`, `wiki/sources/`, `wiki/syntheses/`
3. Beziehe dich in deiner Antwort auf konkrete Wiki-Seiten
4. Schlage vor, neue Erkenntnisse als Synthese-Seite zu speichern

## Wiki-Operationen

Die vollständigen Regeln für INGEST, QUERY und LINT stehen in:
`c:\Users\<DEIN-USERNAME>\OneDrive - INFORM GmbH\knowledge-wiki\CLAUDE.md`

## Regeln

- `raw/` ist read-only — niemals Dateien dort ändern
- Nach Änderungen immer `wiki/log.md` und `wiki/index.md` aktualisieren
- Wikilinks als `[[seiten-name]]` (kebab-case, ohne .md)
- Sprache: Deutsch bevorzugt, Fachbegriffe auf Englisch lassen
