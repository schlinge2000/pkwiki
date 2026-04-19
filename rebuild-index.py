"""
rebuild-index.py — Regeneriert wiki/index.md aus allen vorhandenen Wiki-Seiten.
Liest den 'title'-Eintrag aus dem YAML-Frontmatter jeder Seite.
"""

import re
from pathlib import Path
from datetime import datetime

WIKI_DIR = Path(__file__).parent / "wiki"

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


def build_index() -> str:
    lines = [
        "# Wiki Index\n",
        f"> Zuletzt generiert: {datetime.now().strftime('%Y-%m-%d %H:%M')} — nicht manuell bearbeiten.\n",
    ]

    total = 0
    for folder, label in SECTIONS:
        section_dir = WIKI_DIR / folder
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
    print("Lese Wiki-Seiten...")
    content = build_index()

    index_path = WIKI_DIR / "index.md"
    index_path.write_text(content, encoding="utf-8")
    print(f"index.md neu geschrieben: {index_path}")


if __name__ == "__main__":
    main()
