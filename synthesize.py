# /// script
# dependencies = ["openai", "python-dotenv", "pydantic"]
# ///
"""
Knowledge Wiki — Story-Outline-Generator für Präsentationen.
Liest die Wiki als Kontext und synthetisiert eine neue, strukturierte
Präsentations-Outline — keine Copy-Paste aus Einzelfolien, sondern
eine eigenständige Narration die Verbindungen quer durch das Wiki zieht.

Usage:
  uv run synthesize.py --thema "Demand AI für Supply Chain Manager" --folien 20
  uv run synthesize.py --thema "Foundation Models" --folien 15 --sprache en --zielgruppe "CTO"

Benötigt in .env (gleiche Datei wie ingest.py):
  AZURE_OPENAI_API_KEY=...
  AZURE_OPENAI_ENDPOINT=https://<dein-resource>.openai.azure.com/
  AZURE_OPENAI_DEPLOYMENT=gpt-4o   (oder dein Deployment-Name)
  AZURE_OPENAI_API_VERSION=2025-04-01-preview  (optional)
"""

import sys
import os
import json
import re
import logging
import argparse
from pathlib import Path
from typing import Literal

# UTF-8 für stdout/stderr erzwingen (Windows-Kompatibilität)
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

from pydantic import BaseModel

# .env laden falls vorhanden — gleiche Konvention wie ingest.py
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

from openai import AzureOpenAI

# ---------------------------------------------------------------------------
# Pfade
# ---------------------------------------------------------------------------

WIKI_ROOT = Path(__file__).parent
WIKI_DIR = WIKI_ROOT / "wiki"
ASSETS_DIR = WIKI_ROOT / "assets"
OUTPUT_DIR = WIKI_ROOT / "output"
LOGS_DIR = WIKI_ROOT / "logs"

# ---------------------------------------------------------------------------
# Response-Schema (Pydantic) — garantiert valides, typgeprüftes LLM-Output
# ---------------------------------------------------------------------------


class SlideOutline(BaseModel):
    nummer: int
    typ: Literal["title", "agenda", "content", "visual", "closing"]
    titel: str                   # max 60 Zeichen
    kernaussage: str             # 1 Satz
    bullet_points: list[str]    # max 7 Items, je max 60 Zeichen
    sprecher_notiz: str          # vollständiger Satz für Vortragenden
    quellen: list[str]           # Wiki-Links z.B. ["[[konzept-a]]"]
    bild_vorschlag: str          # Stichwort für Bild-Recycling, leer wenn nicht nötig


class PresentationOutline(BaseModel):
    titel: str
    zielgruppe: str
    sprache: Literal["de", "en"]
    folien: list[SlideOutline]
    narrative_arc: str           # Gesamtbogen in 3-5 Sätzen


# ---------------------------------------------------------------------------
# Logging einrichten
# ---------------------------------------------------------------------------


def setup_logging(thema: str) -> logging.Logger:
    """Richtet Console + File Logging ein."""
    LOGS_DIR.mkdir(exist_ok=True)

    logger = logging.getLogger("synthesize")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    fmt = logging.Formatter(
        fmt="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Konsole — INFO und höher
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # Log-Datei — alles (DEBUG+)
    fh = logging.FileHandler(LOGS_DIR / "synthesize.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger


# ---------------------------------------------------------------------------
# Wiki-Kontext laden
# ---------------------------------------------------------------------------


def lade_wiki_kontext(log: logging.Logger) -> tuple[str, str, str, str]:
    """
    Lädt den relevanten Wiki-Kontext:
    - index.md (Inhaltsverzeichnis)
    - alle concepts/*.md
    - alle syntheses/*.md
    Gibt (index_md, concepts_text, syntheses_text, schema_md) zurück.
    """
    # Wiki-Index
    index_path = WIKI_DIR / "index.md"
    index_md = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
    log.info("index.md geladen (%d Zeichen)", len(index_md))

    # Konzept-Seiten
    concepts_dir = WIKI_DIR / "concepts"
    concepts_parts: list[str] = []
    if concepts_dir.exists():
        concept_files = sorted(concepts_dir.glob("*.md"))
        for f in concept_files:
            try:
                inhalt = f.read_text(encoding="utf-8")
                concepts_parts.append(f"### [[{f.stem}]]\n{inhalt}")
            except Exception as e:
                log.warning("Konnte %s nicht lesen: %s", f.name, e)
        log.info("%d Konzept-Seiten geladen", len(concept_files))
    concepts_text = "\n\n---\n\n".join(concepts_parts)

    # Synthese-Seiten
    syntheses_dir = WIKI_DIR / "syntheses"
    syntheses_parts: list[str] = []
    if syntheses_dir.exists():
        synthesis_files = sorted(syntheses_dir.glob("*.md"))
        for f in synthesis_files:
            try:
                inhalt = f.read_text(encoding="utf-8")
                syntheses_parts.append(f"### [[{f.stem}]]\n{inhalt}")
            except Exception as e:
                log.warning("Konnte %s nicht lesen: %s", f.name, e)
        log.info("%d Synthese-Seiten geladen", len(synthesis_files))
    syntheses_text = "\n\n---\n\n".join(syntheses_parts)

    # Wiki-Schema aus CLAUDE.md
    schema_path = WIKI_ROOT / "CLAUDE.md"
    schema_md = schema_path.read_text(encoding="utf-8") if schema_path.exists() else ""

    return index_md, concepts_text, syntheses_text, schema_md


def lade_image_index(log: logging.Logger) -> str:
    """Lädt assets/image-index.json falls vorhanden. Gibt JSON-String oder '' zurück."""
    image_index_path = ASSETS_DIR / "image-index.json"
    if not image_index_path.exists():
        log.debug("image-index.json nicht gefunden — Bild-Vorschläge ohne Index")
        return ""

    try:
        with open(image_index_path, encoding="utf-8") as f:
            data = json.load(f)
        # Komprimiert als String übergeben um Tokens zu sparen
        komprimiert = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        log.info("image-index.json geladen (%d Einträge)", len(data) if isinstance(data, list) else 1)
        return komprimiert
    except Exception as e:
        log.warning("Konnte image-index.json nicht laden: %s", e)
        return ""


# ---------------------------------------------------------------------------
# Slug-Generierung
# ---------------------------------------------------------------------------


def thema_zu_slug(thema: str) -> str:
    """Konvertiert Thema-String in einen dateisystem-freundlichen Slug."""
    slug = thema.lower()
    # Umlaute ersetzen
    for alt, neu in [("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")]:
        slug = slug.replace(alt, neu)
    # Alles außer Buchstaben und Ziffern durch Bindestrich ersetzen
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug[:80]  # Maximale Länge begrenzen


# ---------------------------------------------------------------------------
# System-Prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
Du bist ein erfahrener Storyteller und Präsentationsdesigner mit tiefem Fachwissen \
in AI, Supply Chain und Business Strategy.

Deine Aufgabe: Aus dem Knowledge Wiki eine NEUE, eigenständige Präsentations-Outline entwickeln.
Das ist KEINE Kompilation von Einzelfolien — du entwickelst einen neuen narrativen Bogen \
der Verbindungen zieht, die in keiner Einzelpräsentation so stehen.

## Prinzipien

1. **Neue Synthese**: Verbinde Konzepte quer durch das Wiki auf eine Weise, \
die überraschend und aufschlussreich ist. Nicht wiederholen was einzelne Quellen sagen, \
sondern eine neue Perspektive entwickeln.

2. **Narrative Sequenz**: Aufeinanderfolgende Folien bauen ein Argument auf. \
Nutze These → Spannung → Auflösung als dramaturgisches Prinzip.

3. **Narrative Sequences aus Sources**: Die Wiki enthält in sources/*.md Abschnitte \
über narrative Sequenzen aus Original-Präsentationen. Diese erprobten Erzählmuster \
können als Bausteine dienen — aber in neuen Kombinationen.

4. **Bild-Vorschläge**: Wenn ein image-index vorhanden ist, wähle Bilder die \
semantisch zur Folie passen. Wenn kein Index vorhanden ist, nenne Stichworte für \
Bildmotive (z.B. "Scheinwerfer im Nebel", "Supply Chain Netz").

5. **Sprache**: Deutsch als Standard, Fachbegriffe auf Englisch lassen. \
Bei --sprache en: vollständig auf Englisch.

6. **Feldlängen strikt einhalten**:
   - titel: max 60 Zeichen
   - bullet_points: max 7 Items, je max 60 Zeichen
   - kernaussage: 1 Satz
   - sprecher_notiz: vollständiger, ausformulierter Satz für den Vortragenden

7. **Folientypen**:
   - "title": Eröffnungsfolie, Titel der Präsentation
   - "agenda": Übersichtsfolie, Struktur des Vortrags
   - "content": Hauptinhalt, Argumente, Daten
   - "visual": Folie die primär durch ein Bild/Grafik kommuniziert
   - "closing": Abschluss, Call-to-Action, Zusammenfassung

8. **quellen**: Nur existierende Wiki-Seiten als [[wikilink]] angeben.

Gib exakt das angeforderte JSON-Schema zurück — kein Markdown drum herum.
"""


# ---------------------------------------------------------------------------
# LLM-Aufruf
# ---------------------------------------------------------------------------


def rufe_llm_auf(
    thema: str,
    anzahl_folien: int,
    sprache: str,
    zielgruppe: str,
    index_md: str,
    concepts_text: str,
    syntheses_text: str,
    schema_md: str,
    image_index: str,
    log: logging.Logger,
) -> PresentationOutline:
    """Ruft Azure OpenAI auf und gibt validiertes PresentationOutline-Objekt zurück."""
    client = AzureOpenAI(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2025-04-01-preview"),
    )
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

    # Kontext zusammenstellen — Tokens schonen durch sinnvolle Kürzungen
    max_concepts_chars = 80_000
    max_syntheses_chars = 20_000

    if len(concepts_text) > max_concepts_chars:
        log.warning(
            "Konzepte zu lang (%d Zeichen) — kürze auf %d",
            len(concepts_text),
            max_concepts_chars,
        )
        concepts_text = concepts_text[:max_concepts_chars] + "\n\n[... gekürzt ...]"

    if len(syntheses_text) > max_syntheses_chars:
        log.warning(
            "Synthesen zu lang (%d Zeichen) — kürze auf %d",
            len(syntheses_text),
            max_syntheses_chars,
        )
        syntheses_text = syntheses_text[:max_syntheses_chars] + "\n\n[... gekürzt ...]"

    # Bild-Index-Abschnitt nur wenn vorhanden
    bild_abschnitt = ""
    if image_index:
        bild_abschnitt = f"\n---\n# Verfügbarer Bild-Index (assets/image-index.json)\n{image_index}\n"

    user_message = f"""\
# Auftrag

Thema der Präsentation: {thema}
Zielgruppe: {zielgruppe}
Anzahl Folien: {anzahl_folien}
Sprache: {sprache}

---
# Wiki-Schema (CLAUDE.md)
{schema_md}

---
# Wiki-Index (index.md)
{index_md}

---
# Konzept-Seiten (wiki/concepts/)
{concepts_text}

---
# Synthese-Seiten (wiki/syntheses/)
{syntheses_text}
{bild_abschnitt}
---

Entwickle nun eine vollständige Präsentations-Outline mit exakt {anzahl_folien} Folien.
Denke in Narrativen — was ist die überraschende Einsicht die diese Präsentation einzigartig macht?
"""

    gesamtzeichen = len(user_message)
    log.info(
        "Azure OpenAI Anfrage — Deployment: %s | Thema: %s | Folien: %d | Kontext: %d Zeichen",
        deployment,
        thema,
        anzahl_folien,
        gesamtzeichen,
    )

    completion = client.beta.chat.completions.parse(
        model=deployment,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format=PresentationOutline,
        # Großzügige Token-Limits für umfangreiche Outlines
        max_tokens=8192,
    )

    result = completion.choices[0].message.parsed
    if result is None:
        raise ValueError("LLM hat kein valides PresentationOutline zurückgegeben")

    log.info(
        "Outline erhalten: %d Folien | narrative_arc: %d Zeichen",
        len(result.folien),
        len(result.narrative_arc),
    )
    return result


# ---------------------------------------------------------------------------
# Ausgabe speichern
# ---------------------------------------------------------------------------


def speichere_outline(outline: PresentationOutline, slug: str, log: logging.Logger) -> Path:
    """Speichert die Outline als JSON in output/<slug>.json. Gibt den Pfad zurück."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / f"{slug}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(outline.model_dump(), f, ensure_ascii=False, indent=2)

    log.info("Outline gespeichert: %s", output_path)
    return output_path


# ---------------------------------------------------------------------------
# Zusammenfassung ausgeben
# ---------------------------------------------------------------------------


def gib_zusammenfassung_aus(outline: PresentationOutline, output_path: Path) -> None:
    """Gibt eine lesbare Zusammenfassung der Outline auf stdout aus."""
    print()
    print("=" * 70)
    print(f"  {outline.titel}")
    print(f"  Zielgruppe: {outline.zielgruppe} | Sprache: {outline.sprache}")
    print("=" * 70)
    print()
    print(f"Narrative Gesamtbogen:\n{outline.narrative_arc}")
    print()
    print(f"{'Nr':>3}  {'Typ':<8}  Titel")
    print("-" * 70)
    for folie in outline.folien:
        print(f"{folie.nummer:>3}  {folie.typ:<8}  {folie.titel}")
    print()
    print(f"Gespeichert: {output_path}")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    """Parst CLI-Argumente."""
    parser = argparse.ArgumentParser(
        description="Generiert eine strukturierte Präsentations-Outline aus dem Knowledge Wiki.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Beispiele:
  uv run synthesize.py --thema "Demand AI für Supply Chain Manager" --folien 20
  uv run synthesize.py --thema "Foundation Models" --folien 15 --sprache en --zielgruppe "CTO"
""",
    )
    parser.add_argument(
        "--thema",
        required=True,
        help="Thema der Präsentation (wird auch als Dateiname-Slug verwendet)",
    )
    parser.add_argument(
        "--folien",
        type=int,
        default=15,
        help="Anzahl der Folien (default: 15)",
    )
    parser.add_argument(
        "--sprache",
        choices=["de", "en"],
        default="de",
        help="Sprache der Outline (default: de)",
    )
    parser.add_argument(
        "--zielgruppe",
        default="Entscheidungsträger",
        help="Zielgruppe der Präsentation (default: Entscheidungsträger)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    log = setup_logging(args.thema)

    log.info("synthesize.py gestartet — Thema: %s | Folien: %d", args.thema, args.folien)

    # Pflichtumgebungsvariablen prüfen
    fehlende_vars = [v for v in ("AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT") if not os.environ.get(v)]
    if fehlende_vars:
        log.error(
            "Fehlende Umgebungsvariablen: %s — bitte in .env setzen",
            ", ".join(fehlende_vars),
        )
        sys.exit(1)

    # Wiki-Kontext laden
    index_md, concepts_text, syntheses_text, schema_md = lade_wiki_kontext(log)

    # Bild-Index laden (optional)
    image_index = lade_image_index(log)

    # LLM aufrufen
    outline = rufe_llm_auf(
        thema=args.thema,
        anzahl_folien=args.folien,
        sprache=args.sprache,
        zielgruppe=args.zielgruppe,
        index_md=index_md,
        concepts_text=concepts_text,
        syntheses_text=syntheses_text,
        schema_md=schema_md,
        image_index=image_index,
        log=log,
    )

    # Outline speichern
    slug = thema_zu_slug(args.thema)
    output_path = speichere_outline(outline, slug, log)

    # Zusammenfassung ausgeben
    gib_zusammenfassung_aus(outline, output_path)


if __name__ == "__main__":
    main()
