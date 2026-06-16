# /// script
# dependencies = ["python-dotenv"]
# ///
"""
lint-links.py — Graceful Link-Checker für die Wiki (OKF-Prinzip).

Löst BEIDE internen Link-Formen auf und meldet Probleme, statt abzubrechen:
  1. Obsidian-Wikilinks      [[seiten-slug]], [[slug|alias]], [[slug#heading]], ![[bild.jpg]]
  2. Bundle-relative Links   [text](/concepts/foo.md)   — ab wiki/-Root, portable/stabile Form
     + gewöhnliche relative  [text](../entities/bar.md)

OKF-Konformität (siehe SPEC.md des knowledge-catalog/okf):
  - Links sind gerichtete Kanten; kaputte Ziele werden TOLERIERT (Report, kein Crash).
  - Eine fehlerhafte Einzelseite bricht den Lauf nie ab (graceful degradation).

Report:
  - Broken Links : [[..]]/(..) ohne existierendes Ziel
  - Waisen       : Seiten ohne eingehende Links (außer index/log/picture_index)

Usage:
    uv run lint-links.py                 # Report über $VAULT_ROOT/wiki
    uv run lint-links.py --wiki-dir PATH # abweichendes Wiki-Verzeichnis
    uv run lint-links.py --strict        # Exit-Code 1 wenn Broken Links gefunden
    uv run lint-links.py --no-orphans    # nur Broken Links prüfen
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    from dotenv import load_dotenv
    _vault = os.environ.get("VAULT_ROOT")
    if _vault:
        load_dotenv(Path(_vault) / ".env", override=False)
    load_dotenv(Path(__file__).parent / ".env", override=False)
except ImportError:
    pass

SCRIPT_ROOT = Path(__file__).parent
VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", str(SCRIPT_ROOT)))

# Reservierte Dateinamen (OKF) + generierte Indizes — nie als Waise melden.
RESERVED = {"index.md", "log.md", "picture_index.md", "changelog.md", "image-index.md"}

WIKILINK_RE = re.compile(r"!?\[\[([^\]]+?)\]\]")
MDLINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def is_external(target: str) -> bool:
    """http(s)://, mailto:, reine Anker (#...) etc. sind keine internen Seiten-Links."""
    t = target.strip()
    return (
        not t
        or t.startswith(("http://", "https://", "mailto:", "#"))
        or "://" in t.split("/", 1)[0]
    )


def normalize_wikilink(raw: str) -> str:
    """[[slug|alias]] / [[slug#heading]] / [[folder/slug]] → bloßes Ziel (vor | und #)."""
    target = raw.split("|", 1)[0]
    target = target.split("#", 1)[0]
    return target.strip()


def collect_pages(wiki_dir: Path) -> tuple[dict[str, Path], dict[str, list[Path]], list[Path]]:
    """
    Indiziert alle Dateien unter wiki/.
      rel_index : bundle-relativer Pfad (mit/ohne .md, posix) → Path
      stem_index: Dateiname-Stem → [Paths]  (Wikilink-Auflösung; Kollisionen möglich)
      md_pages  : alle .md-Seiten (für Waisen-Analyse)
    """
    rel_index: dict[str, Path] = {}
    stem_index: dict[str, list[Path]] = defaultdict(list)
    md_pages: list[Path] = []

    for f in sorted(wiki_dir.rglob("*")):
        if not f.is_file() or ".git" in f.parts:
            continue
        rel = f.relative_to(wiki_dir).as_posix()
        rel_index[rel] = f
        if f.suffix == ".md":
            rel_index[rel[: -len(".md")]] = f  # auch ohne Endung adressierbar
            md_pages.append(f)
        stem_index[f.stem].append(f)

    return rel_index, stem_index, md_pages


def resolve(target: str, src: Path, wiki_dir: Path,
            rel_index: dict[str, Path], stem_index: dict[str, list[Path]]) -> Path | None:
    """Löst ein Link-Ziel (Wikilink-Slug ODER Pfad) auf eine existierende Datei auf."""
    t = target.strip()
    if not t:
        return None

    # Bundle-relativ ("/concepts/foo.md") — ab wiki/-Root
    if t.startswith("/"):
        rel = t.lstrip("/")
        return rel_index.get(rel) or rel_index.get(rel.removesuffix(".md"))

    # Pfad-artig (enthält "/" oder ".md"-Endung) → relativ zur Quelldatei, dann bundle-relativ
    if "/" in t or t.endswith(".md"):
        cand = (src.parent / t).resolve()
        if cand.is_file():
            return cand
        return rel_index.get(t) or rel_index.get(t.removesuffix(".md"))

    # Reiner Wikilink-Slug → über Dateiname-Stem
    hits = stem_index.get(t)
    return hits[0] if hits else None


def extract_targets(text: str) -> list[str]:
    """Alle internen Link-Ziele einer Seite (Wikilinks + Markdown-Links)."""
    targets = [normalize_wikilink(m) for m in WIKILINK_RE.findall(text)]
    targets += [m for m in MDLINK_RE.findall(text) if not is_external(m)]
    return [t for t in targets if t]


def main() -> int:
    parser = argparse.ArgumentParser(description="Graceful Link-Checker für die Wiki (OKF)")
    parser.add_argument("--wiki-dir", help="Wiki-Verzeichnis (Default: $VAULT_ROOT/wiki)")
    parser.add_argument("--strict", action="store_true", help="Exit 1 bei Broken Links")
    parser.add_argument("--no-orphans", action="store_true", help="Waisen-Analyse überspringen")
    args = parser.parse_args()

    wiki_dir = Path(args.wiki_dir) if args.wiki_dir else VAULT_ROOT / "wiki"
    if not wiki_dir.is_dir():
        print(f"ERROR: Wiki-Verzeichnis nicht gefunden: {wiki_dir}", file=sys.stderr)
        return 2

    rel_index, stem_index, md_pages = collect_pages(wiki_dir)

    broken: list[tuple[str, str]] = []          # (quelle, ziel)
    incoming: set[Path] = set()                 # Seiten mit eingehendem Link
    skipped = 0

    for page in md_pages:
        try:
            text = page.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            skipped += 1
            print(f"  ! SKIP {page.relative_to(wiki_dir).as_posix()} — "
                  f"{type(exc).__name__}: {exc}", file=sys.stderr)
            continue

        for target in extract_targets(text):
            dest = resolve(target, page, wiki_dir, rel_index, stem_index)
            if dest is None:
                broken.append((page.relative_to(wiki_dir).as_posix(), target))
            elif dest != page:
                incoming.add(dest.resolve())

    # --- Report -----------------------------------------------------------
    print(f"Wiki: {wiki_dir}  ({len(md_pages)} Seiten, {skipped} übersprungen)\n")

    print(f"## Broken Links ({len(broken)})")
    for src, target in broken:
        print(f"  ✗ {src} → {target}")
    if not broken:
        print("  (keine)")

    if not args.no_orphans:
        orphans = [
            p.relative_to(wiki_dir).as_posix()
            for p in md_pages
            if p.name not in RESERVED and p.resolve() not in incoming
        ]
        print(f"\n## Waisen — ohne eingehende Links ({len(orphans)})")
        for o in sorted(orphans):
            print(f"  ○ {o}")
        if not orphans:
            print("  (keine)")

    return 1 if (args.strict and broken) else 0


if __name__ == "__main__":
    sys.exit(main())
