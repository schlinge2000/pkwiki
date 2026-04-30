# /// script
# dependencies = ["python-docx", "python-dotenv"]
# ///
"""
transcript-prep.py — Teams-.docx-Transkript → raw/transcripts/<datum>_<slug>.md

Usage:
  uv run transcript-prep.py <teams-transcript.docx> \\
      [--event "Kunde Acme – PoC Setup"] \\
      [--date 2026-04-30] \\
      [--format meeting|talk|interview|podcast|call|workshop] \\
      [--language de|en] \\
      [--output <pfad>]

Erkennt Teams-Sprecher-Header (typisch: "Name 0:00" oder "Name 00:00:00")
und fasst aufeinanderfolgende Beiträge desselben Sprechers zusammen.
Generiert YAML-Frontmatter mit auto-erzeugten Initialen-Kürzeln (Peter Kunz → PK).
Schreibt nach raw/transcripts/<YYYY-MM-DD>_<slug>.md — Watcher übernimmt von dort.
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
TRANSCRIPTS_DIR = WIKI_ROOT / "raw" / "transcripts"

# Sprecher-Header: "Vorname Nachname 0:00" / "Name HH:MM:SS"
# Akzeptiert deutsche Umlaute, Bindestriche, Apostrophe, "von", "de", etc.
SPEAKER_HEADER = re.compile(
    r"^\s*"
    r"(?P<name>[A-Za-zÄÖÜäöüßéèêëàâçñóúíÉÈÊËÀÂÇÑÓÚÍ][A-Za-zÄÖÜäöüßéèêëàâçñóúíÉÈÊËÀÂÇÑÓÚÍ\s\.\-']{1,80}?)"
    r"[\s ]+"
    r"(?P<ts>\d{1,2}:\d{2}(?::\d{2})?)"
    r"\s*$"
)


def slugify(value: str) -> str:
    """ASCII-kebab-case-Slug für Dateinamen."""
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    value = re.sub(r"[-\s]+", "-", value)
    return value or "transcript"


def initials(name: str, taken: set[str]) -> str:
    """'Peter Kunz' → 'PK'; bei Kollision PK2, PK3, ..."""
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


def build_frontmatter(
    event: str,
    date_str: str,
    fmt: str,
    language: str,
    speakers: dict[str, str],
    context: str,
) -> str:
    speaker_lines = "\n".join(f'  {code}: "{name}"' for code, name in speakers.items())
    return (
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


def render_body(segments: list[tuple[str, str]], code_by_name: dict[str, str]) -> str:
    lines: list[str] = []
    for name, text in segments:
        code = code_by_name.get(name, "??")
        lines.append(f"**{code}:** {text}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docx", help="Pfad zur Teams-Transkript-.docx")
    ap.add_argument("--event", default="TODO: Anlass / Titel", help='z.B. "Kundengespräch Acme – PoC Setup"')
    ap.add_argument("--date", default=None, help="YYYY-MM-DD; default: Datei-mtime")
    ap.add_argument("--format", default="meeting",
                    choices=["meeting", "talk", "interview", "podcast", "call", "workshop"])
    ap.add_argument("--language", default="de", choices=["de", "en"])
    ap.add_argument("--context", default="TODO: Kontext / Ziel des Gesprächs in 1-2 Sätzen",
                    help="Kurze Beschreibung des Anlasses")
    ap.add_argument("--output", default=None, help="Zielpfad; default: raw/transcripts/<datum>_<slug>.md")
    ap.add_argument("--force", action="store_true", help="Bestehende Datei überschreiben")
    args = ap.parse_args()

    src = Path(args.docx).resolve()
    if not src.exists():
        print(f"FEHLER: Datei nicht gefunden: {src}", file=sys.stderr)
        return 1
    if src.suffix.lower() != ".docx":
        print(f"FEHLER: nur .docx unterstützt (bekam: {src.suffix})", file=sys.stderr)
        return 1

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
        print("FEHLER: keine Sprecher-Segmente erkannt — ist das wirklich ein Teams-Transkript?", file=sys.stderr)
        print("Erwartetes Format pro Sprecher: 'Vorname Nachname 0:00' gefolgt von Aussage-Absätzen.", file=sys.stderr)
        return 1

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

    speakers_for_frontmatter = {code: name for name, code in code_by_name.items()}

    event_for_slug = args.event if not args.event.startswith("TODO") else src.stem
    slug = slugify(event_for_slug)
    out_path = Path(args.output).resolve() if args.output else TRANSCRIPTS_DIR / f"{date_str}_{slug}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if out_path.exists() and not args.force:
        print(f"FEHLER: Zieldatei existiert bereits: {out_path}\nNutze --force zum Überschreiben.", file=sys.stderr)
        return 1

    frontmatter = build_frontmatter(
        event=args.event, date_str=date_str, fmt=args.format,
        language=args.language, speakers=speakers_for_frontmatter, context=args.context,
    )
    body = render_body(segments, code_by_name)
    out_path.write_text(frontmatter + "\n" + body, encoding="utf-8")

    n_turns = len(segments)
    n_speakers = len(unique_names)
    print(f"OK  {out_path}")
    print(f"    Sprecher: {n_speakers} ({', '.join(f'{c}={n}' for n, c in code_by_name.items())})")
    print(f"    Beiträge: {n_turns}")
    if args.event.startswith("TODO") or args.context.startswith("TODO"):
        print("    Hinweis: --event und/oder --context sind TODO-Platzhalter — vor Ingest nachpflegen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
