# /// script
# dependencies = ["python-docx", "python-dotenv", "openai", "pydantic"]
# ///
"""
transcript-ingest.py — Eigene Pipeline für Teams-Transkripte (.docx).

Analog zu manual-ingest.py: parst die .docx mit Sprecher-Awareness,
schreibt eine strukturierte .md mit YAML-Frontmatter in den Cache und
ruft anschließend den regulären ingest.py-Flow auf — der erkennt den
Pfad raw/transcripts/ automatisch und nutzt den transkript-spezifischen
Prompt.

Usage:
  uv run transcript-ingest.py raw/transcripts/<datei.docx> \\
      [--event "Kunde Acme – PoC Setup"] \\
      [--date 2026-04-30] \\
      [--format meeting|talk|interview|podcast|call|workshop] \\
      [--language de|en] \\
      [--context "Kontext / Ziel"] \\
      [--force]                # Cache überschreiben

Output:
  raw/.cache/transcripts/<stem>.md   (Zwischenprodukt, wird von ingest.py gelesen)
  wiki/sources/<…>.md                (LLM-generierte Quellenübersicht)
  wiki/concepts/, wiki/entities/     (sparsam — nur bei substantiellen Aussagen)
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

from docx import Document

WIKI_ROOT = Path(__file__).parent
RAW_DIR = WIKI_ROOT / "raw"
TRANSCRIPTS_DIR = RAW_DIR / "transcripts"
CACHE_DIR = RAW_DIR / ".cache" / "transcripts"

# Sprecher-Header: "Vorname Nachname 0:00" / "Name HH:MM:SS"
SPEAKER_HEADER = re.compile(
    r"^\s*"
    r"(?P<name>[A-Za-zÄÖÜäöüßéèêëàâçñóúíÉÈÊËÀÂÇÑÓÚÍ][A-Za-zÄÖÜäöüßéèêëàâçñóúíÉÈÊËÀÂÇÑÓÚÍ\s\.\-']{1,80}?)"
    r"[\s ]+"
    r"(?P<ts>\d{1,2}:\d{2}(?::\d{2})?)"
    r"\s*$"
)


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    value = re.sub(r"[-\s]+", "-", value)
    return value or "transcript"


def initials(name: str, taken: set[str]) -> str:
    parts = [p for p in re.split(r"\s+", name.strip()) if p and p[0].isalpha()]
    if not parts:
        base = "X"
    elif len(parts) == 1:
        base = parts[0][:2].upper()
    else:
        base = (parts[0][0] + parts[-1][0]).upper()
    base = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode("ascii") or "X"
    if base not in taken:
        return base
    n = 2
    while f"{base}{n}" in taken:
        n += 1
    return f"{base}{n}"


def parse_docx(path: Path) -> list[tuple[str, str]]:
    """Liest .docx, gibt Liste [(sprecher_name, aussage), ...] zurück.
    Aufeinanderfolgende Beiträge desselben Sprechers werden zusammengefasst."""
    doc = Document(str(path))
    paragraphs = [p.text.strip() for p in doc.paragraphs]

    segments: list[tuple[str, list[str]]] = []
    current_speaker: str | None = None
    buffer: list[str] = []

    def flush():
        if current_speaker and buffer:
            text = " ".join(b for b in buffer if b).strip()
            if text:
                if segments and segments[-1][0] == current_speaker:
                    segments[-1][1].append(text)
                else:
                    segments.append((current_speaker, [text]))

    for para in paragraphs:
        if not para:
            continue
        m = SPEAKER_HEADER.match(para)
        if m:
            flush()
            current_speaker = m.group("name").strip()
            buffer = []
        else:
            buffer.append(para)
    flush()

    return [(name, " ".join(parts).strip()) for name, parts in segments]


def build_markdown(
    segments: list[tuple[str, str]],
    event: str,
    date_str: str,
    fmt: str,
    language: str,
    context: str,
) -> str:
    unique_names: list[str] = []
    seen = set()
    for name, _ in segments:
        if name not in seen:
            seen.add(name)
            unique_names.append(name)

    code_by_name: dict[str, str] = {}
    taken: set[str] = set()
    for name in unique_names:
        code = initials(name, taken)
        code_by_name[name] = code
        taken.add(code)

    speaker_lines = "\n".join(
        f'  {code}: "{name}"' for name, code in code_by_name.items()
    )
    frontmatter = (
        "---\n"
        f'event: "{event}"\n'
        f"format: {fmt}\n"
        f"date: {date_str}\n"
        f"language: {language}\n"
        "speakers:\n"
        f"{speaker_lines}\n"
        f'context: "{context}"\n'
        "---\n"
    )

    body_lines: list[str] = []
    for name, text in segments:
        body_lines.append(f"**{code_by_name[name]}:** {text}")
        body_lines.append("")
    body = "\n".join(body_lines).rstrip() + "\n"

    return frontmatter + "\n" + body


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("docx", help="Pfad zur Teams-Transkript-.docx (idealerweise unter raw/transcripts/)")
    ap.add_argument("--event", default="TODO: Anlass / Titel")
    ap.add_argument("--date", default=None, help="YYYY-MM-DD; default: Datei-mtime")
    ap.add_argument("--format", default="meeting",
                    choices=["meeting", "talk", "interview", "podcast", "call", "workshop"])
    ap.add_argument("--language", default="de", choices=["de", "en"])
    ap.add_argument("--context", default="TODO: Kontext / Ziel des Gesprächs in 1-2 Sätzen")
    ap.add_argument("--force", action="store_true",
                    help="Cache-.md überschreiben falls schon vorhanden")
    ap.add_argument("--no-ingest", action="store_true",
                    help="Nur die .md im Cache erzeugen, kein LLM-Ingest")
    args = ap.parse_args()

    src = Path(args.docx).resolve()
    if not src.exists():
        print(f"FEHLER: Datei nicht gefunden: {src}", file=sys.stderr)
        return 1
    if src.suffix.lower() != ".docx":
        print(f"FEHLER: nur .docx unterstützt (bekam: {src.suffix})", file=sys.stderr)
        return 1

    # Warnung wenn die .docx nicht in raw/transcripts/ liegt — Pfad-basierte
    # Transkript-Erkennung in ingest.py greift sonst nicht.
    try:
        rel = src.relative_to(RAW_DIR.resolve())
        in_transcripts = rel.parts and rel.parts[0] == "transcripts"
    except ValueError:
        in_transcripts = False
    if not in_transcripts:
        print(f"WARNUNG: {src} liegt nicht unter raw/transcripts/ — der Ingest "
              f"wird sie nicht als Transkript erkennen.", file=sys.stderr)

    if args.date:
        try:
            date_obj = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print(f"FEHLER: --date muss YYYY-MM-DD sein (bekam: {args.date})", file=sys.stderr)
            return 1
    else:
        date_obj = date.fromtimestamp(src.stat().st_mtime)
    date_str = date_obj.isoformat()

    segments = parse_docx(src)
    if not segments:
        print("FEHLER: keine Sprecher-Segmente erkannt — ist das wirklich ein "
              "Teams-Transkript?", file=sys.stderr)
        print("Erwartetes Format pro Sprecher: 'Vorname Nachname 0:00' gefolgt "
              "von Aussage-Absätzen.", file=sys.stderr)
        return 1

    md_content = build_markdown(
        segments=segments, event=args.event, date_str=date_str,
        fmt=args.format, language=args.language, context=args.context,
    )

    # Cache-Pfad analog extract.py: raw/.cache/transcripts/<stem>.md
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / f"{src.stem}.md"
    if cache_path.exists() and not args.force:
        print(f"FEHLER: Cache existiert bereits: {cache_path}\n"
              f"Nutze --force zum Überschreiben.", file=sys.stderr)
        return 1
    cache_path.write_text(md_content, encoding="utf-8")

    n_speakers = len({n for n, _ in segments})
    print(f"OK  Cache geschrieben: {cache_path}")
    print(f"    Sprecher: {n_speakers} | Beiträge: {len(segments)}")
    if args.event.startswith("TODO") or args.context.startswith("TODO"):
        print("    Hinweis: --event und/oder --context sind TODO-Platzhalter.")

    if args.no_ingest:
        return 0

    # Regulären Ingest aufrufen — ingest.py liest unseren Cache, erkennt
    # raw/transcripts/ und schaltet auf den transkript-spezifischen Prompt.
    print(f"--- Starte Ingest: {src.name}")
    from ingest import ingest as run_ingest
    run_ingest(str(src))
    return 0


if __name__ == "__main__":
    sys.exit(main())
