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


def extract_if_needed(source_path: Path) -> Path:
    """Extrahiert PPTX/DOCX/PDF zu .md falls nötig. Gibt .md-Pfad zurück."""
    suffix = source_path.suffix.lower()
    if suffix == ".md":
        return source_path

    if suffix not in (".pptx", ".docx", ".pdf"):
        print(f"[WARN] Unbekannter Dateityp: {suffix} — überspringe")
        sys.exit(0)

    # Cache-Pfad berechnen
    try:
        rel = source_path.relative_to(RAW_DIR)
    except ValueError:
        rel = Path(source_path.name)

    cache_path = CACHE_DIR / rel.with_suffix(".md")

    if not cache_path.exists():
        print(f"[EXTRACT] {source_path.name}")
        import subprocess
        result = subprocess.run(
            ["uv", "run", str(WIKI_ROOT / "extract.py"), str(source_path)],
            cwd=str(WIKI_ROOT),
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"[ERROR] Extraktion fehlgeschlagen: {result.stderr}")
            sys.exit(1)
        print(result.stdout.strip())
    else:
        print(f"[CACHE] {cache_path.name} bereits vorhanden")

    return cache_path


def read_wiki_context() -> tuple[str, str, str]:
    """Liest CLAUDE.md, index.md und log.md."""
    claude_md = (WIKI_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    index_md = (WIKI_DIR / "index.md").read_text(encoding="utf-8")
    log_md = (WIKI_DIR / "log.md").read_text(encoding="utf-8")
    return claude_md, index_md, log_md


def call_llm(source_name: str, source_content: str,
             claude_md: str, index_md: str, log_md: str) -> dict:
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

    print(f"[API] Sende Anfrage an Azure OpenAI (Deployment: {deployment}, Quelle: {source_name})...")

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_completion_tokens=8000,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content.strip()

    # JSON aus Markdown-Codeblock extrahieren falls nötig
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1])

    return json.loads(raw)


def write_pages(pages: list[dict], log_entry: str):
    """Schreibt alle Wiki-Seiten und aktualisiert log.md."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    created, updated = [], []

    for page in pages:
        path = WIKI_DIR / page["path"]
        path.parent.mkdir(parents=True, exist_ok=True)

        action = page.get("action", "create")

        if page["path"] in ("log.md",):
            # Log: neuen Eintrag prependen
            existing = path.read_text(encoding="utf-8") if path.exists() else ""
            header = existing.split("---")[0] if "---" in existing else "# Aktivitätslog\n\n> Append-only. Neueste Einträge oben.\n\n"
            rest = existing[len(header):] if existing.startswith(header) else existing
            new_content = header + "---\n\n" + log_entry.strip() + "\n\n" + rest.lstrip("---\n")
            path.write_text(new_content, encoding="utf-8")
            print(f"[LOG] log.md aktualisiert")
            continue

        path.write_text(page["content"], encoding="utf-8")
        if action == "update":
            updated.append(page["path"])
            print(f"[UPDATE] {page['path']}")
        else:
            created.append(page["path"])
            print(f"[CREATE] {page['path']}")

    return created, updated


def ingest(source_file: str):
    source_path = Path(source_file).resolve()

    if not source_path.exists():
        print(f"[ERROR] Datei nicht gefunden: {source_path}")
        sys.exit(1)

    # 1. Extrahieren
    md_path = extract_if_needed(source_path)
    source_content = md_path.read_text(encoding="utf-8")

    if len(source_content.strip()) < 50:
        print(f"[WARN] Datei scheint leer — überspringe")
        sys.exit(0)

    # 2. Wiki-Kontext laden
    claude_md, index_md, log_md = read_wiki_context()

    # 3. LLM aufrufen
    result = call_llm(
        source_name=source_path.name,
        source_content=source_content,
        claude_md=claude_md,
        index_md=index_md,
        log_md=log_md
    )

    # 4. Seiten schreiben
    pages = result.get("pages", [])
    log_entry = result.get("log_entry", f"## {datetime.now().strftime('%Y-%m-%d %H:%M')} — INGEST\nQuelle: {source_path.name}")

    created, updated = write_pages(pages, log_entry)

    print(f"\n✓ Ingest abgeschlossen: {len(created)} neue Seiten, {len(updated)} aktualisiert")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run ingest.py <quelldatei>")
        sys.exit(1)
    ingest(sys.argv[1])
