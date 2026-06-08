# /// script
# dependencies = ["python-dotenv"]
# ///
"""
Knowledge Tree — Rebuild Index & Wikilinks.

Läuft einmalig über bereits generierte code-wiki/-Seiten und:
  1. Patcht Obsidian-Wikilinks in "Betroffene Module"-Sektionen (Ticket-Seiten)
  2. Patcht Ticket-Referenzen (#123 → [[123]]) in Modul-Seiten
  3. Patcht Changelog-Tabelle (Ticket-Spalte → Wikilinks)
  4. Generiert/aktualisiert index.md pro Repo

Usage:
  uv run rebuild-index.py
  uv run rebuild-index.py --dry-run        # zeigt nur was geändert würde
  uv run rebuild-index.py --repo demand-ai # nur ein Repo
"""

from __future__ import annotations

import argparse
import io
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

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_DIR / "rebuild-index.log", encoding="utf-8"),
        logging.StreamHandler(sys.stderr),
    ],
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

SCRIPT_ROOT = Path(__file__).parent
VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", str(SCRIPT_ROOT)))
WIKI_DIR = VAULT_ROOT / "wiki"
CODE_WIKI_DIR = WIKI_DIR / "code-wiki"

# ---------------------------------------------------------------------------
# Slug-Helfer
# ---------------------------------------------------------------------------


def module_slug(name: str) -> str:
    """Konvertiert Modulnamen in Datei-Slug."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def ticket_slug(ticket_id: str) -> str:
    """Konvertiert Ticket-ID in Datei-Slug."""
    # #123 → issue-123, DAI-42 → dai-42, 661 → 661
    t = ticket_id.strip()
    if t.startswith("#"):
        return f"issue-{t[1:]}"
    return t.lower()


# ---------------------------------------------------------------------------
# 1. Ticket-Seiten: "Betroffene Module" → Wikilinks
# ---------------------------------------------------------------------------


def patch_ticket_page(path: Path, dry_run: bool) -> bool:
    """Ersetzt plain-text Modulnamen in ## Betroffene Module durch [[wikilinks]]."""
    content = path.read_text(encoding="utf-8")
    original = content

    lines = content.splitlines(keepends=True)
    result_lines: list[str] = []
    in_module_section = False

    for line in lines:
        if re.match(r"^##\s+Betroffene Module", line):
            in_module_section = True
            result_lines.append(line)
            continue

        if in_module_section:
            # Neue ## Sektion beendet den Block
            if line.startswith("##"):
                in_module_section = False
                result_lines.append(line)
                continue

            # Listenpunkt ohne Wikilink → patchen
            m = re.match(r"^(- )([^\[].+?)(\s*)$", line.rstrip("\n"))
            if m:
                prefix, name, _ = m.groups()
                slug = module_slug(name.strip("* "))
                new_line = f"{prefix}[[{slug}]]\n"
                result_lines.append(new_line)
                continue

        result_lines.append(line)

    new_content = "".join(result_lines)
    if new_content != original:
        if not dry_run:
            path.write_text(new_content, encoding="utf-8")
        log.info("PATCH ticket  %s", path.name)
        return True
    return False


# ---------------------------------------------------------------------------
# 2. Modul-Seiten: Ticket-Referenzen (#123, DAI-42) → [[slug]]
# ---------------------------------------------------------------------------

TICKET_PATTERN = re.compile(r"(?<!\[)(?<!\[)([A-Z]+-\d+|#\d+)(?!\])")


def patch_module_page(path: Path, dry_run: bool) -> bool:
    """Ersetzt Ticket-Referenzen in Modul-Seiten durch Wikilinks."""
    content = path.read_text(encoding="utf-8")
    original = content

    def replace_ticket(m: re.Match) -> str:
        tid = m.group(1)
        slug = ticket_slug(tid)
        return f"[[{slug}]]"

    # Nur außerhalb von Frontmatter und Codeblöcken patchen
    parts = content.split("---", 2)
    if len(parts) >= 3:
        frontmatter = "---" + parts[1] + "---"
        body = parts[2]
        new_body = TICKET_PATTERN.sub(replace_ticket, body)
        new_content = frontmatter + new_body
    else:
        new_content = TICKET_PATTERN.sub(replace_ticket, content)

    if new_content != original:
        if not dry_run:
            path.write_text(new_content, encoding="utf-8")
        log.info("PATCH module  %s", path.name)
        return True
    return False


# ---------------------------------------------------------------------------
# 3. Changelog: Ticket-Spalte → Wikilinks
# ---------------------------------------------------------------------------

CHANGELOG_TICKET_RE = re.compile(r"\|\s*([A-Z]+-\d+|#\d+|\d+)\s*\|")


def patch_changelog(path: Path, dry_run: bool) -> bool:
    """Ersetzt Ticket-Referenzen in changelog.md Tabellenzellen durch Wikilinks."""
    if not path.exists():
        return False

    content = path.read_text(encoding="utf-8")
    original = content

    def replace_in_cell(m: re.Match) -> str:
        tid = m.group(1)
        slug = ticket_slug(tid)
        return f"| [[{slug}]] |"

    new_content = CHANGELOG_TICKET_RE.sub(replace_in_cell, content)

    # Auch mehrere Tickets in einer Zelle (| #661 #662 |)
    multi_re = re.compile(r"(?<!\[)([A-Z]+-\d+|#\d+|\d+)(?!\])")
    # Nur in Tabellenzeilen, nicht in Headers
    lines = new_content.splitlines(keepends=True)
    result = []
    for line in lines:
        if line.startswith("|") and "[[" not in line and re.search(r"[A-Z]+-\d+|#\d+", line):
            # Letzte Spalte vor dem | hat Ticket-IDs
            line = multi_re.sub(lambda m: f"[[{ticket_slug(m.group(1))}]]", line)
        result.append(line)
    new_content = "".join(result)

    if new_content != original:
        if not dry_run:
            path.write_text(new_content, encoding="utf-8")
        log.info("PATCH changelog  %s", path.parent.name)
        return True
    return False


# ---------------------------------------------------------------------------
# 4. Index generieren
# ---------------------------------------------------------------------------


def write_repo_index(code_wiki_dir: Path, repo_name: str, dry_run: bool) -> None:
    """Erstellt index.md mit Wikilinks auf alle Tickets und Module."""
    tickets_dir = code_wiki_dir / "tickets"
    modules_dir = code_wiki_dir / "modules"

    ticket_links: list[tuple[str, str]] = []
    module_links: list[tuple[str, str]] = []

    if tickets_dir.exists():
        for f in sorted(tickets_dir.glob("*.md")):
            slug = f.stem
            title = slug
            try:
                for line in f.read_text(encoding="utf-8").splitlines():
                    if line.startswith("title:"):
                        title = line.split(":", 1)[1].strip().strip('"')
                        break
            except Exception:
                pass
            ticket_links.append((slug, title))

    if modules_dir.exists():
        for f in sorted(modules_dir.glob("**/*.md")):
            rel = f.relative_to(modules_dir)
            slug = f.stem
            title = slug
            try:
                for line in f.read_text(encoding="utf-8").splitlines():
                    if line.startswith("title:"):
                        title = line.split(":", 1)[1].strip().strip('"')
                        break
            except Exception:
                pass
            module_links.append((slug, title))

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        f"# Code-Wiki: {repo_name}",
        f"\n_Automatisch generiert — {today}_\n",
        f"\n## Tickets ({len(ticket_links)})\n",
    ]
    for slug, title in ticket_links:
        lines.append(f"- [[{slug}]] — {title}")

    lines.append(f"\n## Module ({len(module_links)})\n")
    for slug, title in module_links:
        lines.append(f"- [[{slug}]] — {title}")

    lines.append("\n## Changelog\n\n→ [[changelog]]")

    index_path = code_wiki_dir / "index.md"
    new_content = "\n".join(lines) + "\n"

    if not dry_run:
        index_path.write_text(new_content, encoding="utf-8")
    log.info(
        "INDEX   %s (%d tickets, %d module)%s",
        repo_name,
        len(ticket_links),
        len(module_links),
        "  [dry-run]" if dry_run else "",
    )


# ---------------------------------------------------------------------------
# Haupt-Loop
# ---------------------------------------------------------------------------


def process_repo(repo_dir: Path, dry_run: bool) -> None:
    repo_name = repo_dir.name
    log.info("=" * 60)
    log.info("REPO: %s", repo_name)
    log.info("=" * 60)

    changed = 0

    # Ticket-Seiten patchen
    tickets_dir = repo_dir / "tickets"
    if tickets_dir.exists():
        for f in sorted(tickets_dir.glob("*.md")):
            if patch_ticket_page(f, dry_run):
                changed += 1

    # Modul-Seiten patchen
    modules_dir = repo_dir / "modules"
    if modules_dir.exists():
        for f in sorted(modules_dir.glob("**/*.md")):
            if patch_module_page(f, dry_run):
                changed += 1

    # Changelog patchen
    if patch_changelog(repo_dir / "changelog.md", dry_run):
        changed += 1

    # Index generieren
    write_repo_index(repo_dir, repo_name, dry_run)

    log.info("Fertig: %d Seiten gepatcht%s", changed, "  [dry-run]" if dry_run else "")


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebuild Obsidian Wikilinks & Index für code-wiki/")
    parser.add_argument("--dry-run", action="store_true", help="Nur anzeigen, nichts schreiben")
    parser.add_argument("--repo", help="Nur dieses Repo verarbeiten (z.B. demand-ai)")
    args = parser.parse_args()

    if not CODE_WIKI_DIR.exists():
        log.error("code-wiki/ nicht gefunden: %s", CODE_WIKI_DIR)
        sys.exit(1)

    repos = [CODE_WIKI_DIR / args.repo] if args.repo else sorted(CODE_WIKI_DIR.iterdir())

    for repo_dir in repos:
        if repo_dir.is_dir():
            process_repo(repo_dir, args.dry_run)

    log.info("Alle Repos verarbeitet.")


if __name__ == "__main__":
    main()
