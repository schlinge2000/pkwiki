# /// script
# dependencies = ["openai", "python-pptx", "python-docx", "pdfplumber", "python-dotenv"]
# ///
"""
Knowledge Wiki — Automatischer Ingest via Azure OpenAI.
Usage: uv run ingest.py <quelldatei>   (PPTX/DOCX/PDF oder bereits extrahierte .md)

Benötigt in .env:
  AZURE_OPENAI_API_KEY=...
  AZURE_OPENAI_ENDPOINT=https://<dein-resource>.openai.azure.com/
  AZURE_OPENAI_DEPLOYMENT=gpt-4o   (oder dein Deployment-Name)
"""

import json
import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# .env laden falls vorhanden
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

from openai import AzureOpenAI

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

Du gibst eine JSON-Antwort zurück mit allen Wiki-Seiten die erstellt oder aktualisiert werden sollen.

Format:
{
  "pages": [
    {
      "path": "concepts/mein-konzept.md",
      "action": "create" | "update",
      "content": "--- vollständiger Markdown-Inhalt der Seite ---"
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
"""


def extract_if_needed(source_path: Path, log: logging.Logger) -> Path:
    """Extrahiert PPTX/DOCX/PDF zu .md falls nötig. Gibt .md-Pfad zurück."""
    suffix = source_path.suffix.lower()
    if suffix == ".md":
        return source_path

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
             log: logging.Logger) -> dict:
    """Ruft Azure OpenAI auf und gibt geparste JSON-Antwort zurück."""
    client = AzureOpenAI(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2025-04-01-preview"),
    )
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

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
Erstelle nun die Wiki-Seiten für diese Quelle. Antworte ausschließlich mit validem JSON gemäß dem beschriebenen Format."""

    log.info("Azure OpenAI Anfrage — Deployment: %s | Quelle: %s | Textlänge: %d Zeichen",
             deployment, source_name, len(source_content))

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_completion_tokens=8000,
        response_format={"type": "json_object"},
    )

    usage = response.usage
    if usage:
        log.info("Token-Verbrauch — Prompt: %d | Completion: %d | Gesamt: %d",
                 usage.prompt_tokens, usage.completion_tokens, usage.total_tokens)

    raw = response.choices[0].message.content.strip()

    # JSON aus Markdown-Codeblock extrahieren falls nötig
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1])

    return json.loads(raw)


def write_pages(pages: list[dict], log_entry: str, log: logging.Logger):
    """Schreibt alle Wiki-Seiten und aktualisiert log.md."""
    created, updated = [], []

    for page in pages:
        # LLM gibt manchmal "wiki/concepts/foo.md" zurück obwohl WIKI_DIR schon wiki/ ist
        page_path = page["path"].lstrip("/")
        if page_path.startswith("wiki/"):
            page_path = page_path[len("wiki/"):]
        path = WIKI_DIR / page_path
        path.parent.mkdir(parents=True, exist_ok=True)

        action = page.get("action", "create")

        if page_path in ("log.md",):
            # Log: neuen Eintrag prependen
            existing = path.read_text(encoding="utf-8") if path.exists() else ""
            header = existing.split("---")[0] if "---" in existing else "# Aktivitätslog\n\n> Append-only. Neueste Einträge oben.\n\n"
            rest = existing[len(header):] if existing.startswith(header) else existing
            new_content = header + "---\n\n" + log_entry.strip() + "\n\n" + rest.lstrip("---\n")
            path.write_text(new_content, encoding="utf-8")
            log.debug("wiki/log.md aktualisiert")
            continue

        path.write_text(page["content"], encoding="utf-8")
        if action == "update":
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

        # 3. LLM aufrufen
        result = call_llm(
            source_name=source_path.name,
            source_content=source_content,
            claude_md=claude_md,
            index_md=index_md,
            log_md=log_md,
            log=log,
        )

        # 4. Seiten schreiben
        pages = result.get("pages", [])
        log_entry = result.get(
            "log_entry",
            f"## {datetime.now().strftime('%Y-%m-%d %H:%M')} — INGEST\nQuelle: {source_path.name}"
        )

        created, updated = write_pages(pages, log_entry, log)

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
