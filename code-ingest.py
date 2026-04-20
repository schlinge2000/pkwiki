# /// script
# dependencies = ["openai", "python-dotenv", "pydantic"]
# ///
"""
Knowledge Tree — Code-Ingest: CommitDigest → code-wiki/ + wiki/meta/.

Liest einen CommitDigest (JSON von code-extract.py) und schreibt:
  code-wiki/<projekt>/tickets/TICKET-123.md
  code-wiki/<projekt>/modules/<modul>.md
  code-wiki/<projekt>/changelog.md
  wiki/concepts/<pattern>.md   (nur bei shared_concept)
  wiki/meta/pm-overview.md     (append)

Usage:
  uv run code-extract.py owner/repo sha | uv run code-ingest.py
  uv run code-ingest.py --file digest.json
  uv run code-ingest.py --file digest.json --wiki-dir /path/to/wiki
"""

from __future__ import annotations

import argparse
import io
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

from openai import AzureOpenAI
from pydantic import BaseModel
from typing import Literal

from schemas import CommitDigest, CodeWikiPage, CodeIngestResponse, PMUpdate

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[logging.FileHandler(LOG_DIR / "code-ingest.log", encoding="utf-8")],
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s", "%Y-%m-%d %H:%M:%S"))
logging.getLogger().addHandler(console)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------

SCRIPT_ROOT = Path(__file__).parent
VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", str(SCRIPT_ROOT)))
WIKI_DIR = VAULT_ROOT / "wiki"
LOCK_FILE = WIKI_DIR / ".code-ingest.lock"

# ---------------------------------------------------------------------------
# LLM-Prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
Du bist ein technischer Redakteur der Git-Commits in strukturierte Wiki-Seiten umwandelt.

Du erhältst einen CommitDigest und erstellst daraus Wiki-Seiten für das code-wiki.

WICHTIG — Was du erstellst/aktualisierst:

1. **Ticket-Seite** (tickets/<ticket-id>.md) — für jede Ticket-Referenz im Commit.
   Inhalt: Was wurde gebaut, warum, welche Commits, betroffene Module, Status.
   Bei UPDATE: Neuen Commit oben einfügen, bestehenden Inhalt darunter behalten.

2. **Modul-Seiten** (modules/<modul-name>.md) — für jedes impact_area.
   Inhalt: Was macht dieses Modul, wie hat es sich verändert, welche Commits haben es berührt.
   Bei UPDATE: Neuste Änderung oben, akkumuliert über Zeit.

3. **Changelog-Eintrag** (changelog.md) — eine Zeile pro Commit, neueste oben.
   Format: `| {datum} | {sha[:8]} | {complexity} | {one_liner} | {tickets} |`

Regeln:
- Kein Code in den Seiten — nur semantische Beschreibungen
- Ticket-Status inferieren: action="create" wenn erste Erwähnung, "update" wenn schon existiert
- shared_concept != null → ZUSÄTZLICH eine Konzept-Seite in wiki_concepts[]
  (abstrahiert, kein projektspezifischer Code)
- pm_update.one_liner: max 100 Zeichen, deutsch, prägnant
- Frontmatter in jeder Seite: title, type, repo, last_commit, tickets
- Sprache: Deutsch
"""


def build_user_message(digest: CommitDigest, existing_pages: dict[str, str]) -> str:
    """Baut den User-Message-Context für das LLM."""
    parts = [
        f"## CommitDigest\n```json\n{digest.model_dump_json(indent=2)}\n```",
    ]

    if existing_pages:
        parts.append("## Bereits existierende Seiten (zum Aktualisieren)")
        for path, content in existing_pages.items():
            parts.append(f"### {path}\n```markdown\n{content[:1500]}\n```")

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Existierende Seiten laden
# ---------------------------------------------------------------------------


def load_existing_pages(digest: CommitDigest, code_wiki_dir: Path) -> dict[str, str]:
    """Lädt bereits existierende Ticket- und Modul-Seiten für den LLM-Kontext."""
    existing: dict[str, str] = {}

    # Ticket-Seiten
    for ref in digest.ticket_refs:
        slug = ref.id.lower().replace("#", "issue-")
        path = code_wiki_dir / "tickets" / f"{slug}.md"
        if path.exists():
            existing[f"tickets/{slug}.md"] = path.read_text(encoding="utf-8")

    # Modul-Seiten
    for area in digest.impact_areas:
        slug = re.sub(r"[^a-z0-9]+", "-", area.lower()).strip("-")
        path = code_wiki_dir / "modules" / f"{slug}.md"
        if path.exists():
            existing[f"modules/{slug}.md"] = path.read_text(encoding="utf-8")

    # Changelog
    changelog_path = code_wiki_dir / "changelog.md"
    if changelog_path.exists():
        existing["changelog.md"] = changelog_path.read_text(encoding="utf-8")[:2000]

    return existing


# ---------------------------------------------------------------------------
# LLM-Aufruf
# ---------------------------------------------------------------------------


def call_llm(
    digest: CommitDigest,
    existing_pages: dict[str, str],
    client: AzureOpenAI,
    deployment: str,
) -> CodeIngestResponse:
    user_message = build_user_message(digest, existing_pages)

    log.info(
        "LLM-Ingest — Repo: %s | Commit: %s | Tickets: %s",
        digest.repo_name,
        digest.sha[:8],
        [r.id for r in digest.ticket_refs] or "keine",
    )

    completion = client.beta.chat.completions.parse(
        model=deployment,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format=CodeIngestResponse,
        max_completion_tokens=8_000,
    )

    result = completion.choices[0].message.parsed
    if result is None:
        raise ValueError("LLM gab kein valides CodeIngestResponse zurück")

    log.info(
        "CodeIngestResponse — %d code_pages, %d wiki_concepts",
        len(result.code_pages),
        len(result.wiki_concepts),
    )
    return result


# ---------------------------------------------------------------------------
# Seiten schreiben
# ---------------------------------------------------------------------------


def write_pages(
    result: CodeIngestResponse,
    digest: CommitDigest,
    code_wiki_dir: Path,
    wiki_dir: Path,
) -> None:
    """Schreibt alle generierten Seiten. Hält Lock-Datei während des Schreibens."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Lock
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCK_FILE.write_text(f"code-ingest locked at {today} — {digest.sha[:8]}\n")

    try:
        # Code-Wiki-Seiten
        for page in result.code_pages:
            target = code_wiki_dir / page.path
            target.parent.mkdir(parents=True, exist_ok=True)

            if page.action == "update" and target.exists():
                # Neuen Content vorne einfügen
                existing = target.read_text(encoding="utf-8")
                # Alles nach dem Frontmatter behalten
                if "---" in existing:
                    parts = existing.split("---", 2)
                    if len(parts) >= 3:
                        old_body = "---".join(parts[2:])
                        new_content = page.content.rstrip() + "\n\n---\n\n" + old_body.lstrip()
                        target.write_text(new_content, encoding="utf-8")
                        log.info("UPDATE  %s", page.path)
                        continue

            target.write_text(page.content, encoding="utf-8")
            log.info("%s  %s", page.action.upper().ljust(6), page.path)

        # Wiki-Konzept-Seiten (abstrahiert, kein Code)
        for page in result.wiki_concepts:
            target = wiki_dir / page.path
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists() or page.action == "create":
                target.write_text(page.content, encoding="utf-8")
                log.info("CONCEPT %s", page.path)

        # PM-Update: an pm-overview.md anhängen
        _append_pm_update(result.pm_update, digest, wiki_dir)

    finally:
        LOCK_FILE.unlink(missing_ok=True)


def _append_pm_update(pm: PMUpdate, digest: CommitDigest, wiki_dir: Path) -> None:
    """Hängt einen PM-Update-Eintrag an wiki/meta/pm-overview.md."""
    meta_dir = wiki_dir / "meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    overview_path = meta_dir / "pm-overview.md"

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    line = f"| {today} | {digest.repo_name} | {pm.ticket_id or '—'} | {pm.one_liner} |\n"

    if not overview_path.exists():
        overview_path.write_text(
            "# PM-Übersicht — Commit-Aktivität\n\n"
            "| Datum | Repo | Ticket | Zusammenfassung |\n"
            "|-------|------|--------|-----------------|\n"
            + line,
            encoding="utf-8",
        )
    else:
        # Neue Zeile nach der Header-Tabelle einfügen (nach 3. Zeile)
        content = overview_path.read_text(encoding="utf-8")
        lines = content.splitlines(keepends=True)
        insert_at = 3 if len(lines) >= 3 else len(lines)
        lines.insert(insert_at, line)
        overview_path.write_text("".join(lines), encoding="utf-8")

    log.info("PM-Update  →  wiki/meta/pm-overview.md")


# ---------------------------------------------------------------------------
# Azure OpenAI Client
# ---------------------------------------------------------------------------


def build_client() -> tuple[AzureOpenAI, str]:
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")

    if not endpoint or not api_key:
        raise EnvironmentError("AZURE_OPENAI_ENDPOINT und AZURE_OPENAI_API_KEY müssen in .env gesetzt sein")

    return AzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version=api_version), deployment


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CommitDigest (JSON) → code-wiki/ Wiki-Seiten.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  uv run code-extract.py schlinge2000/pkwiki abc1234 | uv run code-ingest.py
  uv run code-ingest.py --file digest.json
  uv run code-ingest.py --file digest.json --code-wiki-dir /path/to/code-wiki/demand-ai
""",
    )
    parser.add_argument(
        "--file", "-f",
        help="JSON-Datei mit CommitDigest (default: stdin)",
    )
    parser.add_argument(
        "--wiki-dir",
        type=Path,
        default=WIKI_DIR,
        help=f"Pfad zum wiki/-Verzeichnis (default: {WIKI_DIR})",
    )
    parser.add_argument(
        "--code-wiki-dir",
        type=Path,
        default=None,
        help="Pfad zum code-wiki/<projekt>/ Verzeichnis (default: wiki/code-wiki/<repo_name>/)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # CommitDigest laden
    if args.file:
        raw = Path(args.file).read_text(encoding="utf-8")
    else:
        log.info("Lese CommitDigest von stdin...")
        raw = sys.stdin.read()

    digest = CommitDigest.model_validate_json(raw)

    # Pfade bestimmen
    wiki_dir: Path = args.wiki_dir
    code_wiki_dir: Path = args.code_wiki_dir or (wiki_dir / "code-wiki" / digest.repo_name)

    log.info("=" * 60)
    log.info("CODE-INGEST  %s/%s  @%s", digest.repo_owner, digest.repo_name, digest.sha[:8])
    log.info("code-wiki → %s", code_wiki_dir)
    log.info("=" * 60)

    # Existierende Seiten laden
    existing_pages = load_existing_pages(digest, code_wiki_dir)
    if existing_pages:
        log.info("Existierende Seiten geladen: %s", list(existing_pages.keys()))

    # LLM
    client, deployment = build_client()
    result = call_llm(digest, existing_pages, client, deployment)

    # Schreiben
    write_pages(result, digest, code_wiki_dir, wiki_dir)

    log.info("=" * 60)
    log.info(
        "FERTIG — %d code-wiki Seiten, %d Konzepte, PM-Update geschrieben",
        len(result.code_pages),
        len(result.wiki_concepts),
    )
    log.info("=" * 60)


if __name__ == "__main__":
    main()
