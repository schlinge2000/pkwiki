"""
rebuild-index.py — Regeneriert wiki/index.md aus allen vorhandenen Wiki-Seiten.
Liest den 'title'-Eintrag aus dem YAML-Frontmatter jeder Seite.

Usage:
    uv run rebuild-index.py                 # $VAULT_ROOT/wiki (Fallback: Repo-Pfad)
    uv run rebuild-index.py --wiki-dir PATH
"""

import argparse
import os
import re
import sys
from pathlib import Path
from datetime import datetime

# Windows-Konsole ist per Default cp1252 — Unicode-Ausgabe würde crashen.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

SCRIPT_ROOT = Path(__file__).parent
# Wiki liegt im Vault (OneDrive), nicht im Repo — VAULT_ROOT respektieren, Fallback aufs Repo.
VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", str(SCRIPT_ROOT)))

SECTIONS = [
    ("concepts", "Konzepte"),
    ("entities", "Entitäten"),
    ("sources", "Quellen"),
    ("syntheses", "Synthesen"),
]


def extract_title(path: Path) -> str:
    """Extrahiert den Titel aus dem YAML-Frontmatter, fallback: Dateiname."""
    try:
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if match:
            fm = match.group(1)
            title_match = re.search(r"^title:\s*(.+)$", fm, re.MULTILINE)
            if title_match:
                return title_match.group(1).strip().strip('"').strip("'")
    except Exception:
        pass
    return path.stem


def build_index(wiki_dir: Path) -> str:
    lines = [
        "# Wiki Index\n",
        f"> Zuletzt generiert: {datetime.now().strftime('%Y-%m-%d %H:%M')} — nicht manuell bearbeiten.\n",
    ]

    total = 0
    for folder, label in SECTIONS:
        section_dir = wiki_dir / folder
        if not section_dir.exists():
            continue

        pages = sorted(section_dir.glob("*.md"))
        if not pages:
            continue

        lines.append(f"\n## {label}\n")
        for page in pages:
            title = extract_title(page)
            rel = f"{folder}/{page.name}"
            lines.append(f"- [[{page.stem}|{title}]]")
            total += 1

    lines.append(f"\n---\n\n*{total} Seiten indexiert.*\n")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Regeneriert wiki/index.md aus dem Frontmatter")
    parser.add_argument("--wiki-dir", help="Wiki-Verzeichnis (Default: $VAULT_ROOT/wiki)")
    args = parser.parse_args()

    wiki_dir = Path(args.wiki_dir) if args.wiki_dir else VAULT_ROOT / "wiki"
    if not wiki_dir.is_dir():
        print(f"ERROR: Wiki-Verzeichnis nicht gefunden: {wiki_dir}", file=sys.stderr)
        return 2

    print(f"Lese Wiki-Seiten aus {wiki_dir} ...")
    content = build_index(wiki_dir)

    index_path = wiki_dir / "index.md"
    index_path.write_text(content, encoding="utf-8")
    print(f"index.md neu geschrieben: {index_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
