# /// script
# dependencies = ["python-pptx", "python-docx", "pdfplumber"]
# ///
"""
Extrahiert Text aus PPTX, DOCX und PDF → speichert als .md neben der Originaldatei.
Usage: uv run extract.py <dateipfad>
"""

import sys
import re
from pathlib import Path


def extract_pptx(path: Path) -> str:
    from pptx import Presentation
    from pptx.util import Pt

    prs = Presentation(path)
    lines = [f"# {path.stem}\n", f"**Quelle:** {path.name}\n"]

    for i, slide in enumerate(prs.slides, 1):
        slide_lines = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    text = para.text.strip()
                    if text:
                        slide_lines.append(text)
        if slide_lines:
            lines.append(f"\n## Folie {i}\n")
            lines.extend(slide_lines)

    return "\n".join(lines)


def extract_docx(path: Path) -> str:
    from docx import Document

    doc = Document(path)
    lines = [f"# {path.stem}\n", f"**Quelle:** {path.name}\n"]

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        style = para.style.name if para.style else ""
        if "Heading 1" in style:
            lines.append(f"\n# {text}")
        elif "Heading 2" in style:
            lines.append(f"\n## {text}")
        elif "Heading 3" in style:
            lines.append(f"\n### {text}")
        else:
            lines.append(text)

    return "\n".join(lines)


def extract_pdf(path: Path) -> str:
    import pdfplumber

    lines = [f"# {path.stem}\n", f"**Quelle:** {path.name}\n"]

    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text and text.strip():
                lines.append(f"\n## Seite {i}\n")
                lines.append(text.strip())

    return "\n".join(lines)


def extract(file_path: str) -> Path:
    path = Path(file_path).resolve()
    suffix = path.suffix.lower()

    print(f"Extrahiere: {path.name}")

    if suffix == ".pptx":
        content = extract_pptx(path)
    elif suffix == ".docx":
        content = extract_docx(path)
    elif suffix == ".pdf":
        content = extract_pdf(path)
    else:
        print(f"Kein Extraktor für {suffix} — überspringe.")
        sys.exit(0)

    # Ziel: raw/.cache/<subfolder>/<name>.md
    raw_root = path.parent
    while raw_root.name != "raw" and raw_root.parent != raw_root:
        raw_root = raw_root.parent
    rel = path.relative_to(raw_root)
    out_path = raw_root / ".cache" / rel.with_suffix(".md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"Gespeichert: {out_path.relative_to(raw_root.parent)}")
    return out_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract.py <dateipfad>")
        sys.exit(1)
    extract(sys.argv[1])
