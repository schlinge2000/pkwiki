# /// script
# dependencies = ["openai", "python-pptx", "python-docx", "pdfplumber", "python-dotenv", "pydantic"]
# ///
"""
Knowledge Wiki — Automatischer Ingest via Azure OpenAI.
Usage: uv run ingest.py <quelldatei>   (PPTX/DOCX/PDF oder bereits extrahierte .md)

Benötigt in .env:
  AZURE_OPENAI_API_KEY=...
  AZURE_OPENAI_ENDPOINT=https://<dein-resource>.openai.azure.com/
  AZURE_OPENAI_DEPLOYMENT=gpt-4o   (oder dein Deployment-Name)
"""

import sys
import os
import io
import logging
from pathlib import Path
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

# .env laden falls vorhanden
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

from openai import AzureOpenAI

# ---------------------------------------------------------------------------
# Response-Schema (Pydantic) — garantiert valides, typgeprüftes LLM-Output
# ---------------------------------------------------------------------------

class WikiPage(BaseModel):
    path: str                              # relativ zu wiki/, z.B. "concepts/foo.md"
    action: Literal["create", "update"]
    content: str                           # vollständiger Markdown-Inhalt

class NarrativeSequence(BaseModel):
    folien: str                            # z.B. "17-18" oder "5-7"
    titel: str                             # kurze Bezeichnung der Sequenz
    beschreibung: str                      # Argument-Bogen in 1-3 Sätzen

class IngestResponse(BaseModel):
    pages: list[WikiPage]
    narrative_sequences: list[NarrativeSequence] = []  # nur bei PPTX relevant
    log_entry: str

WIKI_ROOT = Path(__file__).parent
RAW_DIR = WIKI_ROOT / "raw"
CACHE_DIR = RAW_DIR / ".cache"
WIKI_DIR = WIKI_ROOT / "wiki"
LOGS_DIR = WIKI_ROOT / "logs"

# ---------------------------------------------------------------------------
# Protokollierung einrichten
# ---------------------------------------------------------------------------

def setup_logging(source_name: str) -> logging.Logger:
    """Richtet Console + File Logging ein. Log-Datei: logs/ingest.log"""
    LOGS_DIR.mkdir(exist_ok=True)

    logger = logging.getLogger("ingest")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    fmt = logging.Formatter(
        fmt="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Konsole
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # Rolling File — alles landet in logs/ingest.log
    fh = logging.FileHandler(LOGS_DIR / "ingest.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger


SYSTEM_PROMPT = """Du bist der Maintainer einer persönlichen Wissensbasis (Knowledge Wiki).
Deine Aufgabe: Ein extrahiertes Quelldokument in strukturierte, vernetzte Wiki-Seiten überführen.

Du bekommst:
1. Das CLAUDE.md Schema (Seitentypen, Frontmatter, Konventionen)
2. Den aktuellen Index der Wiki (vorhandene Seiten)
3. Den Inhalt des zu ingesting Dokuments

Du gibst eine strukturierte JSON-Antwort zurück die exakt diesem Schema entspricht:

{
  "pages": [
    {
      "path": "concepts/mein-konzept.md",       // relativ zu wiki/
      "action": "create" | "update",
      "content": "--- vollständiger Markdown-Inhalt ---"
    }
  ],
  "narrative_sequences": [                       // nur bei PPTX, sonst leere Liste []
    {
      "folien": "17-18",                         // Folienbereich als String
      "titel": "Scheinwerfer und Reh",           // kurze Bezeichnung
      "beschreibung": "These auf Folie 17 ..."   // Argument-Bogen in 1-3 Sätzen
    }
  ],
  "log_entry": "## YYYY-MM-DD HH:MM — INGEST\\nQuelle: ...\\nNeue Seiten: ...\\nAktualisierte Seiten: ..."
}

Regeln:
- path ist immer relativ zu wiki/ (z.B. "concepts/demand-ai.md")
- Du MUSST immer index.md aktualisieren (path: "index.md")
- Du MUSST immer log.md aktualisieren (path: "log.md") — PREPEND den neuen Eintrag oben
- Erstelle 3-10 Konzeptseiten, 1 Quellenübersicht, relevante Entity-Seiten
- Verlinke alles mit [[wikilinks]] (Dateiname ohne .md, kebab-case)
- Kein Inhalt erfinden — nur was wirklich im Dokument steht
- Deutsch als Hauptsprache, Fachbegriffe auf Englisch lassen
- confidence: high nur wenn mehrfach belegt, sonst medium

Für Präsentationen (PPTX) — Folienübergänge als narrative Einheit verstehen:
- Aufeinanderfolgende Folien bauen oft ein Argument Schritt für Schritt auf — erkenne den dramaturgischen Bogen
- Wenn Bilder über mehrere Folien dasselbe Motiv weiterentwickeln (z.B. Folie A: falsch ausgerichteter Scheinwerfer → Folie B: Reh taucht im Lichtkegel auf), ist das eine zusammenhängende Aussage — erfasse sie als Einheit
- These → Konsequenz → Lösung über mehrere Folien gehört in ein Konzept, nicht in drei separate
- Bildsequenzen haben eine Kausalität: was auf Folie N gezeigt wird, ist oft die Folge oder Auflösung von Folie N-1
- Halte in der Quellenübersicht (sources/) die narrative Struktur der Präsentation fest: welche Foliengruppen bilden ein Argument?
"""


def extract_if_needed(source_path: Path, log: logging.Logger) -> Path:
    """Extrahiert PPTX/DOCX/PDF zu .md falls nötig. Gibt .md-Pfad zurück."""
    suffix = source_path.suffix.lower()
    if suffix == ".md":
        return source_path

    if suffix == ".txt":
        # Kein Extraction-Schritt nötig — Text direkt lesen und cachen
        try:
            rel = source_path.relative_to(RAW_DIR)
        except ValueError:
            rel = Path(source_path.name)
        cache_path = CACHE_DIR / rel.with_suffix(".md")
        if not cache_path.exists():
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            text = source_path.read_text(encoding="utf-8", errors="replace")
            cache_path.write_text(f"# {source_path.stem}\n\n{text}", encoding="utf-8")
            log.info("TXT gecacht: %s", cache_path.name)
        else:
            log.info("Cache-Treffer: %s", cache_path.name)
        return cache_path

    if suffix not in (".pptx", ".docx", ".pdf"):
        log.warning("Unbekannter Dateityp: %s — überspringe", suffix)
        sys.exit(0)

    # Cache-Pfad berechnen
    try:
        rel = source_path.relative_to(RAW_DIR)
    except ValueError:
        rel = Path(source_path.name)

    cache_path = CACHE_DIR / rel.with_suffix(".md")

    if not cache_path.exists():
        log.info("Extrahiere: %s", source_path.name)
        import subprocess
        result = subprocess.run(
            ["uv", "run", str(WIKI_ROOT / "extract.py"), str(source_path)],
            cwd=str(WIKI_ROOT),
            capture_output=True, text=True
        )
        if result.returncode != 0:
            log.error("Extraktion fehlgeschlagen:\n%s", result.stderr)
            sys.exit(1)
        log.debug("Extrakt-Output: %s", result.stdout.strip())
        log.info("Extrakt gespeichert: %s", cache_path.name)
    else:
        log.info("Cache-Treffer: %s", cache_path.name)

    return cache_path


def read_wiki_context() -> tuple[str, str, str]:
    """Liest CLAUDE.md, index.md und log.md."""
    claude_md = (WIKI_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    index_md = (WIKI_DIR / "index.md").read_text(encoding="utf-8")
    log_md = (WIKI_DIR / "log.md").read_text(encoding="utf-8")
    return claude_md, index_md, log_md


def call_llm(source_name: str, source_content: str,
             claude_md: str, index_md: str, log_md: str,
             log: logging.Logger) -> IngestResponse:
    """Ruft Azure OpenAI auf und gibt validiertes IngestResponse-Objekt zurück."""
    client = AzureOpenAI(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2025-04-01-preview"),
    )
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

    # Bei sehr langen Quellen kürzen damit genug Output-Tokens bleiben
    max_source_chars = 60_000
    if len(source_content) > max_source_chars:
        log.warning("Quelle zu lang (%d Zeichen) — kürze auf %d", len(source_content), max_source_chars)
        source_content = source_content[:max_source_chars] + "\n\n[... gekürzt ...]"

    user_message = f"""# CLAUDE.md Schema
{claude_md}

---
# Aktueller Wiki-Index
{index_md}

---
# Aktuelles Log (für Kontext)
{log_md[:2000]}

---
# Zu ingestierende Quelle: {source_name}
{source_content}

---
Erstelle nun die Wiki-Seiten für diese Quelle."""

    log.info("Azure OpenAI Anfrage — Deployment: %s | Quelle: %s | Textlänge: %d Zeichen",
             deployment, source_name, len(source_content))

    # Structured Output via Pydantic — kein manuelles JSON-Parsing mehr
    response = client.beta.chat.completions.parse(
        model=deployment,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_completion_tokens=16000,
        response_format=IngestResponse,
    )

    usage = response.usage
    if usage:
        log.info("Token-Verbrauch — Prompt: %d | Completion: %d | Gesamt: %d",
                 usage.prompt_tokens, usage.completion_tokens, usage.total_tokens)
        if usage.completion_tokens >= 15900:
            log.warning("Antwort möglicherweise abgeschnitten (Completion = %d Tokens)", usage.completion_tokens)

    result = response.choices[0].message.parsed
    if result is None:
        raise RuntimeError("LLM hat kein valides IngestResponse geliefert (parsed=None)")

    # Narrative Sequenzen loggen falls vorhanden
    if result.narrative_sequences:
        log.info("Narrative Sequenzen erkannt: %d", len(result.narrative_sequences))
        for seq in result.narrative_sequences:
            log.info("  Folien %s — %s", seq.folien, seq.titel)

    return result


def write_pages(result: IngestResponse, log: logging.Logger) -> tuple[list[str], list[str]]:
    """Schreibt alle Wiki-Seiten aus dem validierten IngestResponse."""
    import time
    lock_path = WIKI_DIR / ".ingest.lock"
    waited = 0
    while lock_path.exists() and waited < 300:
        time.sleep(1)
        waited += 1
    lock_path.write_text(str(os.getpid()), encoding="utf-8")
    try:
        return _do_write_pages(result, log)
    finally:
        lock_path.unlink(missing_ok=True)


def _do_write_pages(result: IngestResponse, log: logging.Logger) -> tuple[list[str], list[str]]:
    created: list[str] = []
    updated: list[str] = []

    for page in result.pages:
        # Pfad normalisieren — LLM gibt manchmal "wiki/concepts/foo.md" zurück
        page_path = page.path.lstrip("/")
        if page_path.startswith("wiki/"):
            page_path = page_path[len("wiki/"):]
        path = WIKI_DIR / page_path
        path.parent.mkdir(parents=True, exist_ok=True)

        if page_path == "log.md":
            # Log: neuen Eintrag prependen
            existing = path.read_text(encoding="utf-8") if path.exists() else ""
            header = existing.split("---")[0] if "---" in existing else "# Aktivitätslog\n\n> Append-only. Neueste Einträge oben.\n\n"
            rest = existing[len(header):] if existing.startswith(header) else existing
            new_content = header + "---\n\n" + result.log_entry.strip() + "\n\n" + rest.lstrip("---\n")
            path.write_text(new_content, encoding="utf-8")
            log.debug("wiki/log.md aktualisiert")
            continue

        path.write_text(page.content, encoding="utf-8")
        if page.action == "update":
            updated.append(page_path)
            log.info("UPDATE  %s", page_path)
        else:
            created.append(page_path)
            log.info("CREATE  %s", page_path)

    return created, updated


def ingest(source_file: str):
    source_path = Path(source_file).resolve()
    log = setup_logging(source_path.name)

    log.info("=" * 60)
    log.info("INGEST START  %s", source_path.name)
    log.info("=" * 60)

    if not source_path.exists():
        log.error("Datei nicht gefunden: %s", source_path)
        sys.exit(1)

    try:
        # 1. Extrahieren
        md_path = extract_if_needed(source_path, log)
        source_content = md_path.read_text(encoding="utf-8")

        if len(source_content.strip()) < 50:
            log.warning("Dateiinhalt zu kurz (%d Zeichen) — überspringe", len(source_content.strip()))
            sys.exit(0)

        log.info("Quelltextlänge: %d Zeichen", len(source_content))

        # 2. Wiki-Kontext laden
        claude_md, index_md, log_md = read_wiki_context()

        # 3. LLM aufrufen — gibt validiertes IngestResponse zurück
        result = call_llm(
            source_name=source_path.name,
            source_content=source_content,
            claude_md=claude_md,
            index_md=index_md,
            log_md=log_md,
            log=log,
        )

        # 4. Seiten schreiben
        created, updated = write_pages(result, log)

        log.info("-" * 60)
        log.info("INGEST OK  —  %d neue Seiten, %d aktualisiert", len(created), len(updated))
        log.info("-" * 60)

    except KeyboardInterrupt:
        log.warning("Abgebrochen.")
        sys.exit(1)
    except Exception as exc:
        log.exception("INGEST FEHLER: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run ingest.py <quelldatei>")
        sys.exit(1)
    ingest(sys.argv[1])
