# Integration mit externen Watchern (knowledge-tree)

Dieses Dokument beschreibt den Vertrag zwischen `pkwiki` und externen Watchern
(insb. `code-watch.py` im **knowledge-tree** Repo), die Pipelines in pkwiki
automatisch triggern. Wer eine neue Pipeline hinzufügt oder einen Watcher
anpasst, muss hier nachsehen — und das Dokument bei Änderungen aktualisieren.

## Übersicht

In pkwiki gibt es **drei** Ingest-Pipelines mit unterschiedlichen Triggern:

| Pipeline | Eingangsformat | Drop-Ordner | Wer triggert |
|---|---|---|---|
| `ingest.py` (regulär) | .pdf / .pptx / .docx / .txt | `raw/pdfs/`, `raw/slides/`, `raw/docs/`, `raw/links/` | `watch.ps1` (lokaler PowerShell-Watcher in pkwiki) |
| `manual-ingest.py` | .pdf | `raw/manuals/` | `code-watch.py` (knowledge-tree) |
| `transcript-ingest.py` | .docx | `raw/transcripts/` | `code-watch.py` (knowledge-tree) |

`raw/manuals/` und `raw/transcripts/` werden von `watch.ps1` **bewusst ignoriert**
— sie sind extern getriggert.

## Trigger-Bedingung (für externe Watcher)

Polling per **mtime** (analog wie heute für `raw/manuals/`):
- Walke den Drop-Ordner rekursiv
- Bei jeder Datei mit passendem Glob: vergleiche `os.path.getmtime` gegen den
  letzten gesehenen Stand
- Bei Erstkontakt oder Änderung: zugehöriges Pipeline-Skript aufrufen
- mtime-Cache pro Datei persistieren (z.B. `.knowledge-tree/seen.json`)

## CLI-Verträge der Pipeline-Skripte

### `manual-ingest.py`
```
uv run manual-ingest.py raw/manuals/<datei.pdf> --product <produkt-slug> [--max-level 2]
```
- **Pflicht:** `--product <slug>` (kebab-case, z.B. `addone-bo`, `addone-bo-admin`).
  Der externe Watcher leitet den Slug aus dem Dateinamen ab (z.B. mtime-Cache
  speichert die Zuordnung) — siehe `code-watch.py`.
- **Exit:** `0` Erfolg, `1` Fehler.
- **Idempotenz:** schreibt nach `wiki/manuals/<produkt>/`. Re-Aufruf überschreibt.

### `transcript-ingest.py`
```
uv run transcript-ingest.py raw/transcripts/<datei.docx> [optionen]
```
**Optionen** (alle optional):
| Flag | Default | Bedeutung |
|---|---|---|
| `--event "<titel>"` | `"TODO: Anlass / Titel"` | Anlass / Titel des Gesprächs |
| `--date YYYY-MM-DD` | mtime der `.docx` | Datum |
| `--format <typ>` | `meeting` | `meeting`/`talk`/`interview`/`podcast`/`call`/`workshop` |
| `--language de\|en` | `de` | Sprache des Transkripts |
| `--context "<text>"` | `"TODO: Kontext / Ziel ..."` | Kurzer Kontext |
| `--force` | aus | Cache `.md` überschreiben (nötig bei Re-Ingest geänderter .docx) |
| `--no-ingest` | aus | Nur die `.md` im Cache erzeugen, kein LLM-Call |

**Exit-Codes:**
- `0` — Erfolg (Cache geschrieben + ggf. Ingest durchgelaufen)
- `1` — Fehler:
  - Datei nicht gefunden
  - Falsches Suffix (nicht `.docx`)
  - Ungültiges `--date`-Format
  - Keine Sprecher-Segmente erkannt (kein gültiges Teams-Transkript)
  - Cache existiert bereits und kein `--force`

**Idempotenz:** Bei aktualisierter `.docx` muss der Watcher `--force` setzen,
sonst bricht das Skript wegen vorhandenem Cache ab.

**Output:**
- `raw/.cache/transcripts/<stem>.md` (Zwischenprodukt; nicht committen)
- `wiki/sources/<…>.md`, ggf. `wiki/concepts/`, `wiki/entities/`,
  `wiki/index.md`, `wiki/log.md`

### `ingest.py` (regulär)
```
uv run ingest.py raw/<unterordner>/<datei>
```
- Wird ausschließlich von `watch.ps1` (in pkwiki) getriggert.
- Externe Watcher rufen `ingest.py` **nicht** direkt auf — der lokale Watcher
  deckt `raw/pdfs/`, `raw/slides/`, `raw/docs/`, `raw/links/` ab.

## Drop-in Snippet für `code-watch.py`

Spiegelbildlich zum bestehenden `check_manuals(...)`:

```python
def check_transcripts(repo_root: Path, seen: dict[str, float]) -> None:
    """Pollt raw/transcripts/ und triggert transcript-ingest.py bei Änderungen."""
    transcripts_dir = repo_root / "raw" / "transcripts"
    if not transcripts_dir.exists():
        return

    for docx in transcripts_dir.glob("*.docx"):
        # Teams-Temp-Dateien überspringen
        if docx.name.startswith("~$"):
            continue

        key = str(docx.relative_to(repo_root))
        mtime = docx.stat().st_mtime
        if seen.get(key) == mtime:
            continue

        # Re-Ingest bei aktualisierter .docx — daher --force
        cmd = [
            "uv", "run", str(repo_root / "transcript-ingest.py"),
            str(docx),
            "--force",
        ]
        result = subprocess.run(cmd, cwd=repo_root)
        if result.returncode == 0:
            seen[key] = mtime
        # Bei returncode != 0: nicht in seen aufnehmen → nächster Loop versucht's erneut
```

Im Haupt-Loop von `code-watch.py` neben `check_manuals(...)` aufrufen:
```python
while True:
    check_github_repos(...)
    check_manuals(repo_root, seen_manuals)
    check_transcripts(repo_root, seen_transcripts)
    time.sleep(POLL_INTERVAL)
```

## Hinweis zu `--event` / `--context`

Der externe Watcher kennt diese Felder nicht und ruft ohne sie auf — die
Defaults bleiben TODO-Platzhalter. Das LLM erzeugt trotzdem eine brauchbare
`wiki/sources/`-Seite, in der die Frontmatter-Felder als TODO sichtbar sind.
Den Anlass / Kontext pflegt der Nutzer **nachträglich von Hand** in der
generierten Quellenübersicht nach.

Wer `--event` / `--context` direkt sauber setzen möchte, ruft
`transcript-ingest.py` manuell statt über den Watcher auf — z.B. direkt nach
dem Drop der `.docx`. Das überschreibt den Cache (mit `--force`) und führt
denselben Ingest mit befüllten Metadaten aus.
