# /// script
# dependencies = ["pymupdf", "openai", "python-dotenv", "Pillow", "pydantic"]
# ///
"""
Knowledge Tree — Manual Ingest: PDF-Handbuch → wiki/manuals/<produkt>/

Liest ein PDF-Handbuch mit Inhaltsverzeichnis und erstellt:
  wiki/manuals/<produkt>/index.md             ← Kapitelübersicht mit Wikilinks
  wiki/manuals/<produkt>/<kapitel-slug>.md    ← Eine Seite pro Kapitel
  wiki/manuals/<produkt>/image-index.md       ← Alle Bilder mit Kontext

Features:
  - TOC-basiertes Chunken (Level 1 oder 2)
  - Bilder per Vision-API (GPT-4o) beschrieben und inline eingebettet
  - Agent-optimiert: Keywords, Schritt-für-Schritt, strukturierte Inhalte
  - Obsidian-Wikilinks zwischen Kapiteln und zur index.md

Usage:
  uv run manual-ingest.py raw/manuals/Administratorhandbuch_addone_bo_ger.pdf --product addone-bo-admin
  uv run manual-ingest.py raw/manuals/Leistungsbeschreibung.pdf --product addone-bo-ls --max-level 2
  uv run manual-ingest.py raw/manuals/foo.pdf --dry-run      # nur Kapitelstruktur anzeigen
"""

from __future__ import annotations

import argparse
import base64
import io
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

import fitz  # PyMuPDF
from PIL import Image
from openai import AzureOpenAI
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_DIR / "manual-ingest.log", encoding="utf-8"),
        logging.StreamHandler(sys.stderr),
    ],
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------

SCRIPT_ROOT = Path(__file__).parent
VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", str(SCRIPT_ROOT)))
WIKI_DIR = VAULT_ROOT / "wiki"
MANUALS_DIR = WIKI_DIR / "manuals"

MAX_TEXT_CHARS = 10_000   # Pro Kapitel ans LLM
MAX_IMAGES_PER_CHAPTER = 4
IMAGE_MAX_PX = 1024       # Resize vor Vision-API

# ---------------------------------------------------------------------------
# Pydantic-Schema
# ---------------------------------------------------------------------------


class ChapterWikiPage(BaseModel):
    title: str          # z.B. "ADD*ONE BO › 2 Installation"
    slug: str           # dateiname ohne .md
    summary: str        # 2-3 Sätze Kurzübersicht
    content: str        # vollständiger Markdown-Body
    keywords: list[str] # für Agentensuche


# ---------------------------------------------------------------------------
# LLM-Client
# ---------------------------------------------------------------------------


def build_client() -> tuple[AzureOpenAI, str, str]:
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")
    vision_deployment = os.environ.get("AZURE_OPENAI_VISION_DEPLOYMENT", deployment)
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")

    if not endpoint or not api_key:
        raise EnvironmentError("AZURE_OPENAI_ENDPOINT und AZURE_OPENAI_API_KEY müssen gesetzt sein")

    client = AzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version=api_version)
    return client, deployment, vision_deployment


# ---------------------------------------------------------------------------
# PDF-Helfer
# ---------------------------------------------------------------------------


def slugify(text: str) -> str:
    """Konvertiert Text in URL-sicheren Slug."""
    text = text.lower().strip()
    text = re.sub(r"[äáàâ]", "a", text)
    text = re.sub(r"[öóòô]", "o", text)
    text = re.sub(r"[üúùû]", "u", text)
    text = re.sub(r"ß", "ss", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text[:60]


def get_chapters(doc: fitz.Document, max_level: int) -> list[dict]:
    """Liest TOC und berechnet Seitenbereiche pro Kapitel."""
    toc = doc.get_toc()
    if not toc:
        # Kein TOC: gesamtes Dokument als ein Kapitel
        return [{"level": 1, "title": "Inhalt", "start": 0, "end": doc.page_count}]

    # Nur bis max_level
    filtered = [(lvl, title, page - 1) for lvl, title, page in toc if lvl <= max_level]

    chapters = []
    for i, (lvl, title, start) in enumerate(filtered):
        end = filtered[i + 1][2] if i + 1 < len(filtered) else doc.page_count
        chapters.append({
            "level": lvl,
            "title": title,
            "start": start,
            "end": end,
            "slug": slugify(title),
            "pages": end - start,
        })

    return chapters


def extract_text(doc: fitz.Document, start: int, end: int, max_chars: int = MAX_TEXT_CHARS) -> str:
    """Extrahiert Text aus Seitenbereich, gekürzt auf max_chars."""
    parts = []
    total = 0
    for page_num in range(start, min(end, doc.page_count)):
        text = doc[page_num].get_text()
        parts.append(f"[Seite {page_num + 1}]\n{text}")
        total += len(text)
        if total >= max_chars:
            parts.append(f"\n[... Inhalt von Seite {page_num + 2} bis {end} gekürzt ...]")
            break
    return "\n".join(parts)[:max_chars + 200]


def extract_images_from_chapter(
    doc: fitz.Document,
    start: int,
    end: int,
    client: AzureOpenAI,
    vision_deployment: str,
    assets_dir: Path,
    chapter_slug: str,
    max_images: int = MAX_IMAGES_PER_CHAPTER,
    chapter_title: str = "",
) -> list[tuple[str, str]]:
    """Extrahiert Bilder, speichert sie in assets/ und beschreibt sie per Vision-API.

    Returns: list of (filename, description) — filename ist der gespeicherte Dateiname
    """
    results: list[tuple[str, str]] = []
    count = 0
    assets_dir.mkdir(parents=True, exist_ok=True)

    seen_xrefs: set[int] = set()  # Duplikate überspringen

    for page_num in range(start, min(end, doc.page_count)):
        if count >= max_images:
            break
        page = doc[page_num]
        image_list = page.get_images(full=True)

        for img_info in image_list:
            if count >= max_images:
                break
            xref = img_info[0]
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)

            try:
                base_image = doc.extract_image(xref)
                img_bytes = base_image["image"]

                # Mindestgröße prüfen (kleine Icons ignorieren)
                img = Image.open(io.BytesIO(img_bytes))
                w, h = img.size
                if w < 80 or h < 80:
                    continue

                # RGBA / Palette → RGB
                if img.mode in ("RGBA", "P"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    mask = img.split()[3] if img.mode == "RGBA" else None
                    background.paste(img, mask=mask)
                    img = background
                elif img.mode != "RGB":
                    img = img.convert("RGB")

                # Resize für Speicherung (max 1600px)
                save_img = img.copy()
                if max(save_img.size) > 1600:
                    ratio = 1600 / max(save_img.size)
                    save_img = save_img.resize(
                        (int(save_img.width * ratio), int(save_img.height * ratio)),
                        Image.LANCZOS,
                    )

                # Datei speichern
                filename = f"{chapter_slug}-p{page_num + 1}-{count + 1}.jpg"
                save_path = assets_dir / filename
                save_img.save(save_path, format="JPEG", quality=85)

                # Resize für Vision-API (max IMAGE_MAX_PX)
                vis_img = img.copy()
                if max(vis_img.size) > IMAGE_MAX_PX:
                    ratio = IMAGE_MAX_PX / max(vis_img.size)
                    vis_img = vis_img.resize(
                        (int(vis_img.width * ratio), int(vis_img.height * ratio)),
                        Image.LANCZOS,
                    )
                buf = io.BytesIO()
                vis_img.save(buf, format="JPEG", quality=85)
                b64 = base64.b64encode(buf.getvalue()).decode()

                # Vision-API
                desc = describe_image(client, vision_deployment, b64, chapter_title, page_num + 1)
                if desc:
                    results.append((filename, desc))
                    count += 1
                    log.debug("  Bild S.%d gespeichert: %s (%dx%d)", page_num + 1, filename, w, h)

            except Exception as e:
                log.debug("  Bild übersprungen: %s", e)
                continue

    return results


def describe_image(
    client: AzureOpenAI,
    deployment: str,
    b64_image: str,
    chapter_context: str,
    page_num: int,
) -> str:
    """Beschreibt ein Bild per Vision-API."""
    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"Du analysierst ein Bild aus einem Software-Handbuch (Kapitel: {chapter_context}, Seite {page_num}).\n"
                                "Beschreibe präzise auf Deutsch:\n"
                                "- Was zeigt das Bild (Screenshot, Diagramm, Tabelle, Icon)?\n"
                                "- Welche UI-Elemente, Felder, Buttons, Menüs sind sichtbar?\n"
                                "- Was ist der funktionale Kontext (welcher Schritt/Vorgang wird gezeigt)?\n"
                                "Maximal 150 Wörter. Keine Einleitung."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64_image}", "detail": "high"},
                        },
                    ],
                }
            ],
            max_completion_tokens=300,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        log.warning("Vision-API Fehler: %s", e)
        return ""


# ---------------------------------------------------------------------------
# LLM: Kapitel → Wiki-Seite
# ---------------------------------------------------------------------------

CHAPTER_SYSTEM = """\
Du bist ein technischer Redakteur der Benutzerhandbücher in agent-optimierte Wiki-Seiten umwandelt.

Dein Ziel: Ein KI-Agent der nach einer Antwort sucht, findet auf dieser Seite sofort was er braucht.

Regeln:
- Klarer Titel mit Produkt-Pfad (z.B. "ADD*ONE BO › 2 Installation › 2.1 Voraussetzungen")
- Kurze Zusammenfassung (summary): 2-3 Sätze, was dieser Abschnitt beschreibt
- Content als gut strukturiertes Markdown:
  - Schritt-für-Schritt-Anleitungen als nummerierte Liste
  - UI-Elemente fett: **Button-Name**, **Feldname**
  - Wichtige Hinweise als > Blockquote
  - Bilder-Beschreibungen inline einbetten mit Kontext-Satz davor
- Keywords: 8-15 Suchbegriffe (Fachbegriffe, Funktionsnamen, UI-Bezeichnungen)
- Sprache: Deutsch
- Kein Code, kein Lorem ipsum, nur echten Inhalt aus dem Text
- slug: Dateiname (lowercase, Bindestriche, max 60 Zeichen)
"""


def generate_chapter_page(
    chapter: dict,
    text: str,
    images: list[tuple[str, str]],  # (filename, description)
    product_name: str,
    client: AzureOpenAI,
    deployment: str,
) -> ChapterWikiPage:
    """Generiert eine Wiki-Seite für ein Kapitel."""
    images_block = ""
    if images:
        images_block = "\n\n## Bilder in diesem Abschnitt (für LLM-Kontext)\n" + "\n".join(
            f"- {desc}" for _, desc in images
        )

    user_msg = (
        f"## Produkt: {product_name}\n"
        f"## Kapitel: {chapter['title']} (S. {chapter['start']+1}–{chapter['end']})\n\n"
        f"### Extrahierter Text\n{text}"
        + images_block
    )

    completion = client.beta.chat.completions.parse(
        model=deployment,
        messages=[
            {"role": "system", "content": CHAPTER_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        response_format=ChapterWikiPage,
        max_completion_tokens=8_000,
    )

    result = completion.choices[0].message.parsed
    if result is None:
        raise ValueError(f"LLM gab kein valides ChapterWikiPage zurück für: {chapter['title']}")

    # Slug aus TOC-Titel wenn LLM anderen genommen hat
    if not result.slug:
        result.slug = chapter["slug"]

    return result


# ---------------------------------------------------------------------------
# Seiten schreiben
# ---------------------------------------------------------------------------


def render_page(
    page: ChapterWikiPage,
    product_name: str,
    today: str,
    images: list[tuple[str, str]] | None = None,
) -> str:
    """Rendert eine ChapterWikiPage als Markdown-Datei mit eingebetteten Bildern."""
    keywords_str = ", ".join(page.keywords)

    body = (
        f"---\n"
        f"title: \"{page.title}\"\n"
        f"type: manual-chapter\n"
        f"product: {product_name}\n"
        f"generated: {today}\n"
        f"keywords: [{keywords_str}]\n"
        f"---\n\n"
        f"# {page.title}\n\n"
        f"> {page.summary}\n\n"
        f"{page.content}\n"
    )

    if images:
        body += "\n\n## Abbildungen\n\n"
        for filename, desc in images:
            body += f"![[{filename}]]\n"
            body += f"*{desc.strip()}*\n\n"

    return body


def write_manuals_root_index(manuals_dir: Path, today: str) -> None:
    """Erstellt/aktualisiert wiki/manuals/index.md mit allen Produkten."""
    products = sorted([d for d in manuals_dir.iterdir() if d.is_dir()])
    if not products:
        return

    lines = [
        "# Handbuch-Übersicht",
        f"\n_Automatisch generiert — {today}_\n",
    ]

    for product_dir in products:
        product_name = product_dir.name
        # Titel aus product-index.md lesen falls vorhanden
        index_path = product_dir / "index.md"
        title = product_name
        chapter_count = 0
        image_count = 0
        source_file = ""

        import re

        if index_path.exists():
            content = index_path.read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
            m2 = re.search(r"Quelle: (.+?) —", content)
            if m2:
                source_file = m2.group(1).strip()

        # Kapitel direkt aus Dateisystem zählen (robust gegen Partial-Runs)
        chapter_count = len(list(product_dir.glob("*.md"))) - 2  # minus index.md + image-index.md
        chapter_count = max(0, chapter_count)

        # Bilder direkt aus assets/ zählen
        assets_dir = product_dir / "assets"
        if assets_dir.exists():
            image_count = len(list(assets_dir.glob("*.jpg")))

        lines.append(f"\n## [[{product_name}/index|{title}]]\n")
        if source_file:
            lines.append(f"Quelle: `{source_file}`  ")
        meta_parts = []
        if chapter_count:
            meta_parts.append(f"{chapter_count} Kapitel")
        if image_count:
            meta_parts.append(f"{image_count} Bilder mit Beschreibung")
        if meta_parts:
            lines.append(", ".join(meta_parts) + "  ")
        lines.append(f"\n→ [[{product_name}/index|Inhaltsverzeichnis]] · [[{product_name}/image-index|Bilder]]")

    root_index = manuals_dir / "index.md"
    root_index.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log.info("ROOT-INDEX  wiki/manuals/index.md (%d Produkte)", len(products))


def write_index(
    chapters_with_pages: list[tuple[dict, ChapterWikiPage]],
    product_name: str,
    product_dir: Path,
    pdf_name: str,
    today: str,
) -> None:
    """Schreibt index.md mit Wikilinks auf alle Kapitel."""
    lines = [
        f"# Handbuch: {product_name}",
        f"\n_Quelle: {pdf_name} — generiert {today}_\n",
        f"\n## Kapitel ({len(chapters_with_pages)})\n",
    ]

    for chapter, page in chapters_with_pages:
        indent = "  " * (chapter["level"] - 1)
        lines.append(f"{indent}- [[{page.slug}]] — {page.summary[:100]}")

    lines.append("\n## Bilder\n\n→ [[image-index]]")

    (product_dir / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    log.info("INDEX   %s/index.md", product_name)


def write_image_index(
    all_images: list[tuple[str, str, str]],  # (kapitel_slug, filename, description)
    product_name: str,
    product_dir: Path,
    today: str,
) -> None:
    """Schreibt image-index.md mit Obsidian-Embeds (![[...]]) und Beschreibungen."""
    if not all_images:
        return

    lines = [
        f"# Bild-Index: {product_name}",
        f"\n_Generiert {today} — {len(all_images)} Bilder_\n",
    ]

    current_slug = None
    for slug, filename, desc in all_images:
        if slug != current_slug:
            lines.append(f"\n## [[{slug}]]\n")
            current_slug = slug
        lines.append(f"![[{filename}]]")
        lines.append(f"*{desc.strip()}*\n")

    (product_dir / "image-index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    log.info("IMAGE-INDEX  %d Bilder mit Obsidian-Embeds", len(all_images))


# ---------------------------------------------------------------------------
# Haupt-Pipeline
# ---------------------------------------------------------------------------


def ingest_pdf(
    pdf_path: Path,
    product_name: str,
    max_level: int,
    dry_run: bool,
    skip_images: bool,
    client: AzureOpenAI,
    deployment: str,
    vision_deployment: str,
    only_chapters: set[int] | None = None,
) -> None:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    log.info("=" * 60)
    log.info("MANUAL-INGEST  %s", pdf_path.name)
    log.info("Produkt: %s | max-level: %d | dry-run: %s", product_name, max_level, dry_run)
    log.info("=" * 60)

    doc = fitz.open(str(pdf_path))
    chapters = get_chapters(doc, max_level)

    log.info("%d Kapitel gefunden (level <= %d, %d Seiten total)", len(chapters), max_level, doc.page_count)

    if dry_run:
        print(f"\n{'='*60}")
        print(f"Kapitelstruktur: {pdf_path.name}")
        print(f"{'='*60}")
        for ch in chapters:
            indent = "  " * (ch["level"] - 1)
            print(f"{indent}[L{ch['level']}] {ch['title']} (S.{ch['start']+1}–{ch['end']}, {ch['pages']} Seiten) → {ch['slug']}.md")
        print(f"\nGesamt: {len(chapters)} Seiten werden zu Wiki-Seiten")
        doc.close()
        return

    product_dir = MANUALS_DIR / product_name
    product_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = product_dir / "assets"

    chapters_with_pages: list[tuple[dict, ChapterWikiPage]] = []
    all_images: list[tuple[str, str, str]] = []  # (kapitel_slug, filename, description)
    error_count = 0
    consecutive_errors = 0
    MAX_CONSECUTIVE_ERRORS = 3  # Abbruch bei Konnektivitätsverlust

    for i, chapter in enumerate(chapters, 1):
        if only_chapters and i not in only_chapters:
            log.debug("SKIP [%d/%d] %s", i, len(chapters), chapter["title"])
            continue
        log.info("[%d/%d] %s (S.%d–%d)", i, len(chapters), chapter["title"], chapter["start"]+1, chapter["end"])

        # Text extrahieren
        text = extract_text(doc, chapter["start"], chapter["end"])

        # Bilder extrahieren + beschreiben
        images: list[tuple[str, str]] = []  # (filename, description)
        if not skip_images and chapter["pages"] <= 80:
            images = extract_images_from_chapter(
                doc, chapter["start"], chapter["end"],
                client, vision_deployment,
                assets_dir=assets_dir,
                chapter_slug=chapter["slug"],
                chapter_title=chapter["title"],
            )
            for filename, desc in images:
                all_images.append((chapter["slug"], filename, desc))

        # LLM: Kapitel → Wiki-Seite
        try:
            page = generate_chapter_page(chapter, text, images, product_name, client, deployment)
            consecutive_errors = 0  # Erfolg: Zähler zurücksetzen
        except Exception as e:
            error_count += 1
            consecutive_errors += 1
            log.error("Fehler bei Kapitel '%s': %s", chapter["title"], e)
            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                log.error(
                    "ABBRUCH — %d Fehler in Folge. Konnektivitätsproblem? "
                    "Bisher verarbeitet: %d/%d Kapitel.",
                    consecutive_errors, len(chapters_with_pages), len(chapters),
                )
                doc.close()
                sys.exit(1)
            continue

        # Datei schreiben (mit eingebetteten ![[...]] Bildern)
        out_path = product_dir / f"{page.slug}.md"
        out_path.write_text(render_page(page, product_name, today, images), encoding="utf-8")
        log.info("  → %s.md (%d Keywords, %d Bilder)", page.slug, len(page.keywords), len(images))

        chapters_with_pages.append((chapter, page))

    # Index + Bild-Index
    # write_index nur bei Vollläufen überschreiben — Partial-Runs (--only-chapters) würden sonst
    # den vollständigen Index mit nur den neu generierten Kapiteln überschreiben
    if not only_chapters:
        write_index(chapters_with_pages, product_name, product_dir, pdf_path.name, today)
    write_image_index(all_images, product_name, product_dir, today)

    # Root-Index über alle Produkte aktualisieren
    write_manuals_root_index(MANUALS_DIR, today)

    doc.close()

    if error_count > 0:
        log.warning(
            "FERTIG MIT FEHLERN — %d/%d Kapitel verarbeitet, %d Fehler, %d Bilder",
            len(chapters_with_pages), len(chapters), error_count, len(all_images),
        )
        log.info("Output: %s", product_dir)
        sys.exit(1)

    log.info("=" * 60)
    log.info("FERTIG — %d Kapitel-Seiten, %d Bilder beschrieben", len(chapters_with_pages), len(all_images))
    log.info("Output: %s", product_dir)
    log.info("=" * 60)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PDF-Handbuch → agent-optimierte Wiki-Seiten",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  uv run manual-ingest.py raw/manuals/Administratorhandbuch_addone_bo_ger.pdf --product addone-bo-admin
  uv run manual-ingest.py raw/manuals/Leistungsbeschreibung.pdf --product addone-bo-ls --max-level 2
  uv run manual-ingest.py raw/manuals/foo.pdf --dry-run
""",
    )
    parser.add_argument("pdf", type=Path, help="Pfad zur PDF-Datei")
    parser.add_argument("--product", "-p", help="Produkt-Slug (default: aus Dateiname)")
    parser.add_argument("--max-level", type=int, default=1, help="TOC-Tiefe (default: 1)")
    parser.add_argument("--dry-run", action="store_true", help="Nur Kapitelstruktur anzeigen")
    parser.add_argument("--skip-images", action="store_true", help="Vision-API überspringen")
    parser.add_argument(
        "--only-chapters",
        help="Nur diese Kapitelnummern verarbeiten, kommagetrennt (z.B. '6,22')",
    )
    args = parser.parse_args()

    # PDF-Pfad auflösen
    pdf_path = args.pdf
    if not pdf_path.is_absolute():
        pdf_path = SCRIPT_ROOT / pdf_path
    if not pdf_path.exists():
        log.error("PDF nicht gefunden: %s", pdf_path)
        sys.exit(1)

    # Produkt-Name
    product_name = args.product or slugify(pdf_path.stem)

    if args.dry_run:
        doc = fitz.open(str(pdf_path))
        chapters = get_chapters(doc, args.max_level)
        print(f"\n{'='*60}")
        print(f"Kapitelstruktur: {pdf_path.name}")
        print(f"{'='*60}")
        for ch in chapters:
            indent = "  " * (ch["level"] - 1)
            print(f"{indent}[L{ch['level']}] {ch['title']} (S.{ch['start']+1}–{ch['end']}, {ch['pages']} Seiten) → {ch['slug']}.md")
        print(f"\nGesamt: {len(chapters)} Kapitel → wiki/manuals/{product_name}/")
        doc.close()
        return

    only_chapters: set[int] | None = None
    if args.only_chapters:
        only_chapters = {int(x.strip()) for x in args.only_chapters.split(",")}

    client, deployment, vision_deployment = build_client()

    ingest_pdf(
        pdf_path=pdf_path,
        product_name=product_name,
        max_level=args.max_level,
        dry_run=args.dry_run,
        skip_images=args.skip_images,
        only_chapters=only_chapters,
        client=client,
        deployment=deployment,
        vision_deployment=vision_deployment,
    )


if __name__ == "__main__":
    main()
