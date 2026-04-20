# /// script
# dependencies = ["openai", "python-pptx", "python-docx", "pdfplumber", "python-dotenv", "pydantic", "httpx"]
# ///
"""
Knowledge Tree — Automatischer Ingest mit shardiertem Domain-Index.

Usage:
    uv run ingest.py <quelldatei>                   (PPTX/DOCX/PDF oder .md)
    uv run ingest.py <quelldatei> --node company
    uv run ingest.py <quelldatei> --node team-demand-ai
    uv run ingest.py <quelldatei> --node personal-christian

Benötigt in .env (oder Umgebungsvariablen):
    AZURE_OPENAI_API_KEY=...
    AZURE_OPENAI_ENDPOINT=https://<dein-resource>.openai.azure.com/
    AZURE_OPENAI_DEPLOYMENT=gpt-4o   (oder dein Deployment-Name)
    AZURE_OPENAI_API_VERSION=2025-04-01-preview   (optional)
    VAULT_ROOT=C:\Pfad\zum\Vault   (wo wiki/, raw/, assets/ liegen — default: Skript-Verzeichnis)
"""

import sys
import os
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

# .env laden falls vorhanden
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

from openai import AzureOpenAI

# ---------------------------------------------------------------------------
# Konstanten & Pfade
# ---------------------------------------------------------------------------

SCRIPT_ROOT = Path(__file__).parent

# Vault-Root: kann per Env überschrieben werden (für GitHub Actions)
VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", os.environ.get("KNOWLEDGE_TREE_ROOT", str(SCRIPT_ROOT))))

LOGS_DIR = VAULT_ROOT / "logs"

# ---------------------------------------------------------------------------
# Response-Schema (Pydantic) — garantiert valides, typgeprüftes LLM-Output
# ---------------------------------------------------------------------------

class WikiPage(BaseModel):
    path: str                              # relativ zu wiki/, z.B. "concepts/foo.md"
    action: Literal["create", "update"]
    content: str                           # vollständiger Markdown-Inhalt

class NarrativeSequence(BaseModel):
    folien: str                            # z.B. "17-18" oder "5-7"
    titel: str                             # kurze Bezeichnung der Sequenz
    beschreibung: str                      # Argument-Bogen in 1-3 Sätzen

class IngestResponse(BaseModel):
    pages: list[WikiPage]
    narrative_sequences: list[NarrativeSequence] = []  # nur bei PPTX relevant
    log_entry: str

# ---------------------------------------------------------------------------
# Domain-Klassifikation
# ---------------------------------------------------------------------------

DOMAINS = Literal[
    "forecasting",    # Zeitreihen, Prognosemodelle, Evaluation
    "demand-ai",      # Demand AI Produkt, Features, Kunden
    "supply-chain",   # SCM, Disposition, Bestandsoptimierung
    "strategy",       # Produktstrategie, Business Model, Go-to-Market
    "tech",           # LLMs, APIs, Architektur, Infrastruktur
    "research",       # Paper, Studien, akademische Quellen
    "legal",          # Verträge, Datenschutz, Compliance
    "hr",             # Personal, Stellenausschreibungen, Interviews
    "meta",           # Wiki-interne Seiten
    "general",        # alles andere
]

DOMAIN_DESCRIPTIONS = {
    "forecasting":  "Zeitreihen, Prognosemodelle, Evaluation, Metriken",
    "demand-ai":    "Demand AI Produkt, Features, Kunden, Roadmap",
    "supply-chain": "SCM, Disposition, Bestandsoptimierung, Logistik",
    "strategy":     "Produktstrategie, Business Model, Go-to-Market, Pricing",
    "tech":         "LLMs, APIs, Architektur, Infrastruktur, Coding",
    "research":     "Paper, Studien, akademische Quellen, Konferenzen",
    "legal":        "Verträge, Datenschutz, Compliance, DSGVO",
    "hr":           "Personal, Stellenausschreibungen, Interviews, OKRs",
    "meta":         "Wiki-interne Seiten, Ingest-Logs, Schemata",
    "general":      "alles andere",
}

class DocumentClassification(BaseModel):
    domain: DOMAINS
    subdomain: str    # freitext, z.B. "foundation-models" oder "go-to-market"
    confidence: float # 0.0 – 1.0
    reason: str       # 1 Satz Begründung

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def setup_logging(source_name: str) -> logging.Logger:
    """Richtet Console + File Logging ein. Log-Datei: logs/ingest.log"""
    LOGS_DIR.mkdir(exist_ok=True)

    logger = logging.getLogger("ingest")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    fmt = logging.Formatter(
        fmt="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Konsole
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # Rolling File — alles landet in logs/ingest.log
    fh = logging.FileHandler(LOGS_DIR / "ingest.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger

# ---------------------------------------------------------------------------
# System-Prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_TEMPLATE = """Du bist der Maintainer einer unternehmensweiten Wissensbasis (Knowledge Tree).
Deine Aufgabe: Ein extrahiertes Quelldokument in strukturierte, vernetzte Wiki-Seiten überführen.

Du bekommst:
1. Das CLAUDE.md Schema (Seitentypen, Frontmatter, Konventionen)
2. Den Domain-Index der aktuellen Wissensdomäne (vollständig)
3. Einen Überblick über den Top-Level-Index (alle Domains, nur Header)
4. Das aktuelle Log (letzten Einträge für Kontext)
5. Den Inhalt des zu ingesting Dokuments

Die aktuelle Domain ist: {domain} ({domain_description}).
Erstelle Seiten die thematisch in diese Domain passen.
Verlinke auf bestehende Konzepte aus dem Domain-Index wo es semantisch sinnvoll ist.

Du gibst eine strukturierte JSON-Antwort zurück die exakt diesem Schema entspricht:

{{
  "pages": [
    {{
      "path": "concepts/mein-konzept.md",       // relativ zu wiki/
      "action": "create" | "update",
      "content": "--- vollständiger Markdown-Inhalt ---"
    }}
  ],
  "narrative_sequences": [                       // nur bei PPTX, sonst leere Liste []
    {{
      "folien": "17-18",                         // Folienbereich als String
      "titel": "Scheinwerfer und Reh",           // kurze Bezeichnung
      "beschreibung": "These auf Folie 17 ..."   // Argument-Bogen in 1-3 Sätzen
    }}
  ],
  "log_entry": "## YYYY-MM-DD HH:MM — INGEST\\nQuelle: ...\\nNeue Seiten: ...\\nAktualisierte Seiten: ..."
}}

Regeln:
- path ist immer relativ zu wiki/ (z.B. "concepts/demand-ai.md")
- Du MUSST immer log.md aktualisieren (path: "log.md") — PREPEND den neuen Eintrag oben
- Du sollst NICHT index.md oder index-{domain}.md direkt schreiben — das erledigt das Skript
- Erstelle 3-10 Konzeptseiten, 1 Quellenübersicht, relevante Entity-Seiten
- Frontmatter-Format:
    ---
    title: "Titel der Seite"
    type: concept | source | entity | index
    domain: {domain}
    tags: [tag1, tag2]
    confidence: high | medium | low
    created: YYYY-MM-DD
    updated: YYYY-MM-DD
    ---
- Verlinke alles mit [[wikilinks]] (Dateiname ohne .md, kebab-case)
- Kein Inhalt erfinden — nur was wirklich im Dokument steht
- Deutsch als Hauptsprache, Fachbegriffe auf Englisch lassen
- confidence: high nur wenn mehrfach belegt, sonst medium

Für Präsentationen (PPTX) — Folienübergänge als narrative Einheit verstehen:
- Aufeinanderfolgende Folien bauen oft ein Argument Schritt für Schritt auf — erkenne den dramaturgischen Bogen
- Wenn Bilder über mehrere Folien dasselbe Motiv weiterentwickeln (z.B. Folie A: falsch ausgerichteter Scheinwerfer → Folie B: Reh taucht im Lichtkegel auf), ist das eine zusammenhängende Aussage — erfasse sie als Einheit
- These → Konsequenz → Lösung über mehrere Folien gehört in ein Konzept, nicht in drei separate
- Bildsequenzen haben eine Kausalität: was auf Folie N gezeigt wird, ist oft die Folge oder Auflösung von Folie N-1
- Halte in der Quellenübersicht (sources/) die narrative Struktur der Präsentation fest: welche Foliengruppen bilden ein Argument?
"""

# ---------------------------------------------------------------------------
# Node-Pfad-Auflösung
# ---------------------------------------------------------------------------

def resolve_node_paths(node: str) -> tuple[Path, Path, Path]:
    """
    Gibt (node_root, wiki_dir, raw_dir) für den angegebenen Node zurück.

    node-Format:
      "default"               → VAULT_ROOT/wiki/
      "company"               → VAULT_ROOT/_company/wiki/
      "team-<name>"           → VAULT_ROOT/_team-<name>/wiki/
      "personal-<user>"       → VAULT_ROOT/_personal-<user>/wiki/
    """
    if node == "default":
        node_root = VAULT_ROOT
    elif node.startswith("personal-"):
        node_root = VAULT_ROOT / f"_{node}"
    elif node.startswith("team-"):
        node_root = VAULT_ROOT / f"_{node}"
    elif node == "company":
        node_root = VAULT_ROOT / "_company"
    else:
        node_root = VAULT_ROOT / node

    wiki_dir = node_root / "wiki"
    raw_dir = node_root / "raw"
    return node_root, wiki_dir, raw_dir

# ---------------------------------------------------------------------------
# Extraktion
# ---------------------------------------------------------------------------

def extract_if_needed(source_path: Path, raw_dir: Path, node_root: Path,
                      log: logging.Logger) -> Path:
    """Extrahiert PPTX/DOCX/PDF zu .md falls nötig. Gibt .md-Pfad zurück."""
    suffix = source_path.suffix.lower()
    if suffix == ".md":
        return source_path

    if suffix not in (".pptx", ".docx", ".pdf"):
        log.warning("Unbekannter Dateityp: %s — überspringe", suffix)
        sys.exit(0)

    # Cache-Pfad berechnen
    cache_dir = raw_dir / ".cache"
    try:
        rel = source_path.relative_to(raw_dir)
    except ValueError:
        rel = Path(source_path.name)

    cache_path = cache_dir / rel.with_suffix(".md")

    if not cache_path.exists():
        log.info("Extrahiere: %s", source_path.name)
        import subprocess
        extract_script = node_root / "extract.py"
        if not extract_script.exists():
            extract_script = SCRIPT_ROOT / "extract.py"
        result = subprocess.run(
            ["uv", "run", str(extract_script), str(source_path)],
            cwd=str(node_root),
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            log.error("Extraktion fehlgeschlagen:\n%s", result.stderr)
            sys.exit(1)
        log.debug("Extrakt-Output: %s", result.stdout.strip())
        log.info("Extrakt gespeichert: %s", cache_path.name)
    else:
        log.info("Cache-Treffer: %s", cache_path.name)

    return cache_path

# ---------------------------------------------------------------------------
# Azure OpenAI Client-Factory
# ---------------------------------------------------------------------------

def make_client() -> tuple[AzureOpenAI, str]:
    """Erstellt AzureOpenAI-Client aus Umgebungsvariablen."""
    client = AzureOpenAI(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2025-04-01-preview"),
    )
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    return client, deployment

# ---------------------------------------------------------------------------
# Schritt 1: Domain-Klassifikation (günstiger Pre-Call)
# ---------------------------------------------------------------------------

def classify_document(
    source_name: str,
    source_preview: str,
    client: AzureOpenAI,
    deployment: str,
    log: logging.Logger,
) -> DocumentClassification:
    """
    Klassifiziert das Dokument in eine Wissensdomäne.
    Günstiger Pre-Call (~500 Tokens) — sendet nur die ersten 3000 Zeichen.
    """
    domain_list = "\n".join(
        f"- {d}: {desc}" for d, desc in DOMAIN_DESCRIPTIONS.items()
    )
    preview = source_preview[:3000]

    system = (
        "Klassifiziere das folgende Dokument in eine Wissensdomäne. "
        "Antworte ausschließlich mit dem strukturierten JSON-Schema."
    )
    user = f"""Verfügbare Domains:
{domain_list}

Dokumentname: {source_name}

Dokumentvorschau (erste 3000 Zeichen):
{preview}

Klassifiziere dieses Dokument."""

    log.info("Domain-Klassifikation — Deployment: %s | Quelle: %s", deployment, source_name)

    response = client.beta.chat.completions.parse(
        model=deployment,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_completion_tokens=300,
        response_format=DocumentClassification,
    )

    result = response.choices[0].message.parsed
    if result is None:
        log.warning("Klassifikation fehlgeschlagen — verwende 'general' als Fallback")
        return DocumentClassification(
            domain="general",
            subdomain="unknown",
            confidence=0.0,
            reason="Klassifikation fehlgeschlagen",
        )

    log.info(
        "Domain: %s / %s  (confidence: %.0f%%)  — %s",
        result.domain, result.subdomain, result.confidence * 100, result.reason,
    )
    return result

# ---------------------------------------------------------------------------
# Schritt 2: Wiki-Kontext lesen (domain-spezifisch)
# ---------------------------------------------------------------------------

def get_domain_index_path(wiki_dir: Path, domain: str) -> Path:
    """Gibt den Pfad zum domain-spezifischen Index zurück."""
    return wiki_dir / f"index-{domain}.md"

def read_wiki_context(wiki_dir: Path, domain: str, node_root: Path) -> tuple[str, str, str, str]:
    """
    Liest CLAUDE.md, domain-spezifischen Index, top-level index.md (nur Header), log.md.

    Gibt zurück: (claude_md, domain_index, top_index_summary, log_md)
    """
    # CLAUDE.md: aus Node-Root oder Vault-Root
    claude_md = ""
    for candidate in [node_root / "CLAUDE.md", VAULT_ROOT / "CLAUDE.md", SCRIPT_ROOT / "CLAUDE.md"]:
        if candidate.exists():
            claude_md = candidate.read_text(encoding="utf-8")
            break

    # Top-level index: nur erste 50 Zeilen (Domains-Übersicht, nicht alle Seiten)
    top_index = ""
    top_index_path = wiki_dir / "index.md"
    if top_index_path.exists():
        lines = top_index_path.read_text(encoding="utf-8").splitlines()
        top_index = "\n".join(lines[:50])

    # Domain-spezifischer Index (vollständig)
    domain_index_path = get_domain_index_path(wiki_dir, domain)
    if domain_index_path.exists():
        domain_index = domain_index_path.read_text(encoding="utf-8")
    else:
        domain_index = f"# Domain-Index: {domain}\n\n(noch leer — erste Seiten werden jetzt erstellt)\n"

    # Log: nur letzte 2000 Zeichen (genug Kontext, spart Tokens)
    log_md = ""
    log_path = wiki_dir / "log.md"
    if log_path.exists():
        log_md = log_path.read_text(encoding="utf-8")[-2000:]

    return claude_md, domain_index, top_index, log_md

# ---------------------------------------------------------------------------
# Schritt 3: LLM-Hauptaufruf
# ---------------------------------------------------------------------------

def call_llm(
    source_name: str,
    source_content: str,
    domain: str,
    claude_md: str,
    domain_index: str,
    top_index: str,
    log_md: str,
    client: AzureOpenAI,
    deployment: str,
    log: logging.Logger,
) -> IngestResponse:
    """Ruft Azure OpenAI auf und gibt validiertes IngestResponse-Objekt zurück."""

    # Bei sehr langen Quellen kürzen damit genug Output-Tokens bleiben
    max_source_chars = 60_000
    if len(source_content) > max_source_chars:
        log.warning(
            "Quelle zu lang (%d Zeichen) — kürze auf %d", len(source_content), max_source_chars
        )
        source_content = source_content[:max_source_chars] + "\n\n[... gekürzt ...]"

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        domain=domain,
        domain_description=DOMAIN_DESCRIPTIONS.get(domain, ""),
    )

    user_message = f"""# CLAUDE.md Schema
{claude_md}

---
# Domain-Index: {domain} (vollständig)
{domain_index}

---
# Top-Level-Index (Überblick über alle Domains)
{top_index}

---
# Aktuelles Log (letzten Einträge für Kontext)
{log_md}

---
# Zu ingestierende Quelle: {source_name}
{source_content}

---
Erstelle nun die Wiki-Seiten für diese Quelle. Domain: {domain}"""

    log.info(
        "Azure OpenAI Anfrage — Deployment: %s | Domain: %s | Quelle: %s | Textlänge: %d Zeichen",
        deployment, domain, source_name, len(source_content),
    )

    response = client.beta.chat.completions.parse(
        model=deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_completion_tokens=16000,
        response_format=IngestResponse,
    )

    usage = response.usage
    if usage:
        log.info(
            "Token-Verbrauch — Prompt: %d | Completion: %d | Gesamt: %d",
            usage.prompt_tokens, usage.completion_tokens, usage.total_tokens,
        )
        if usage.completion_tokens >= 15900:
            log.warning(
                "Antwort möglicherweise abgeschnitten (Completion = %d Tokens)",
                usage.completion_tokens,
            )

    result = response.choices[0].message.parsed
    if result is None:
        raise RuntimeError("LLM hat kein valides IngestResponse geliefert (parsed=None)")

    if result.narrative_sequences:
        log.info("Narrative Sequenzen erkannt: %d", len(result.narrative_sequences))
        for seq in result.narrative_sequences:
            log.info("  Folien %s — %s", seq.folien, seq.titel)

    return result

# ---------------------------------------------------------------------------
# Schritt 4: Seiten schreiben
# ---------------------------------------------------------------------------

def write_pages(
    result: IngestResponse,
    wiki_dir: Path,
    log: logging.Logger,
) -> tuple[list[str], list[str]]:
    """Schreibt alle Wiki-Seiten aus dem validierten IngestResponse (mit Lock)."""
    lock_path = wiki_dir / ".ingest.lock"
    waited = 0
    while lock_path.exists() and waited < 300:
        time.sleep(1)
        waited += 1
    lock_path.write_text(str(os.getpid()), encoding="utf-8")
    try:
        return _do_write_pages(result, wiki_dir, log)
    finally:
        lock_path.unlink(missing_ok=True)


def _do_write_pages(
    result: IngestResponse,
    wiki_dir: Path,
    log: logging.Logger,
) -> tuple[list[str], list[str]]:
    created: list[str] = []
    updated: list[str] = []

    for page in result.pages:
        # Pfad normalisieren — LLM gibt manchmal "wiki/concepts/foo.md" zurück
        page_path = page.path.lstrip("/")
        if page_path.startswith("wiki/"):
            page_path = page_path[len("wiki/"):]
        path = wiki_dir / page_path
        path.parent.mkdir(parents=True, exist_ok=True)

        if page_path == "log.md":
            # Log: neuen Eintrag prependen
            existing = path.read_text(encoding="utf-8") if path.exists() else ""
            header = (
                existing.split("---")[0]
                if "---" in existing
                else "# Aktivitätslog\n\n> Append-only. Neueste Einträge oben.\n\n"
            )
            rest = existing[len(header):] if existing.startswith(header) else existing
            new_content = header + "---\n\n" + result.log_entry.strip() + "\n\n" + rest.lstrip("---\n")
            path.write_text(new_content, encoding="utf-8")
            log.debug("wiki/log.md aktualisiert")
            continue

        # Domain-Index und Top-Index werden vom Skript verwaltet — nicht überschreiben
        if page_path == "index.md" or page_path.startswith("index-"):
            log.debug("Überspringe LLM-generierte Index-Seite: %s (wird vom Skript verwaltet)", page_path)
            continue

        path.write_text(page.content, encoding="utf-8")
        if page.action == "update":
            updated.append(page_path)
            log.info("UPDATE  %s", page_path)
        else:
            created.append(page_path)
            log.info("CREATE  %s", page_path)

    return created, updated

# ---------------------------------------------------------------------------
# Schritt 5: Domain-Index aktualisieren
# ---------------------------------------------------------------------------

def _extract_frontmatter_field(content: str, field: str) -> str:
    """Extrahiert ein einzelnes Feld aus dem YAML-Frontmatter einer Markdown-Seite."""
    match = re.search(rf'^{re.escape(field)}:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    return match.group(1).strip() if match else ""


def _confidence_label(confidence_str: str) -> str:
    """Normalisiert Confidence-Werte auf high/medium/low."""
    c = confidence_str.lower()
    if c in ("high", "hoch"):
        return "high"
    if c in ("low", "niedrig", "gering"):
        return "low"
    return "medium"


def _parse_domain_index_entries(domain_index_content: str) -> dict[str, str]:
    """
    Parst einen bestehenden Domain-Index und gibt slug → volle Zeile zurück.
    Erkennt Einträge der Form: - [[slug]] — ...
    """
    entries: dict[str, str] = {}
    for line in domain_index_content.splitlines():
        m = re.match(r'\s*-\s*\[\[([^\]]+)\]\]', line)
        if m:
            slug = m.group(1)
            entries[slug] = line
    return entries


def _page_slug(page_path: str) -> str:
    """Extrahiert den Slug (Dateiname ohne .md) aus einem relativen Pfad."""
    return Path(page_path).stem


def _page_type_section(page_type: str) -> str:
    """Mappt page type auf die richtige Domain-Index-Sektion."""
    mapping = {
        "concept": "Konzepte",
        "source": "Quellen",
        "entity": "Entities",
        "index": "Konzepte",
    }
    return mapping.get(page_type.lower(), "Konzepte")


def _build_domain_index(
    existing_content: str,
    new_entries: dict[str, tuple[str, str, str]],  # slug → (title, page_type, confidence)
    domain: str,
) -> str:
    """
    Baut den Domain-Index neu auf.

    Strategie:
    - Bestehende Einträge werden übernommen und ggf. überschrieben
    - Neue Einträge werden an die richtige Sektion angehängt
    - Sektionen: Konzepte, Quellen, Entities

    Rückgabe: vollständiger Domain-Index als Markdown-String.
    """
    # Bestehende Einträge parsen
    existing_entries = _parse_domain_index_entries(existing_content)

    # Zusammenführen: bestehende werden durch neue überschrieben wenn slug übereinstimmt
    merged: dict[str, tuple[str, str, str]] = {}  # slug → (title, section, confidence)

    # Bestehende Einträge dekodieren
    for slug, line in existing_entries.items():
        # Versuche Titel und Confidence aus der Zeile zu extrahieren
        m = re.match(r'\s*-\s*\[\[([^\]]+)\]\]\s*—\s*(.+?)(?:,\s*confidence:\s*(\w+))?$', line)
        if m:
            existing_title = m.group(2).strip()
            existing_conf = m.group(3) or "medium"
            # Sektion aus bestehendem Index ableiten (vereinfacht: Konzepte als Default)
            merged[slug] = (existing_title, "Konzepte", existing_conf)

    # Neue Einträge einfügen / überschreiben
    for slug, (title, page_type, confidence) in new_entries.items():
        section = _page_type_section(page_type)
        merged[slug] = (title, section, _confidence_label(confidence))

    # Einträge nach Sektion gruppieren
    sections: dict[str, list[str]] = {
        "Konzepte": [],
        "Quellen": [],
        "Entities": [],
    }
    for slug, (title, section, conf) in merged.items():
        if section not in sections:
            section = "Konzepte"
        sections[section].append(f"- [[{slug}]] — {title}, confidence: {conf}")

    # Domain-Index aufbauen
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines: list[str] = [
        f"# Domain-Index: {domain}",
        "",
        f"> Zuletzt aktualisiert: {today}",
        "",
    ]

    for section_name, entries in sections.items():
        entries_sorted = sorted(entries)
        lines.append(f"## {section_name} ({len(entries_sorted)})")
        lines.append("")
        if entries_sorted:
            lines.extend(entries_sorted)
        else:
            lines.append("_(noch keine Einträge)_")
        lines.append("")

    return "\n".join(lines)


def _count_domain_pages(wiki_dir: Path) -> dict[str, int]:
    """Zählt die Einträge in jedem Domain-Index."""
    counts: dict[str, int] = {}
    for domain in DOMAIN_DESCRIPTIONS:
        index_path = get_domain_index_path(wiki_dir, domain)
        if not index_path.exists():
            counts[domain] = 0
            continue
        content = index_path.read_text(encoding="utf-8")
        # Zähle alle [[slug]]-Einträge
        counts[domain] = len(re.findall(r'\[\[[^\]]+\]\]', content))
    return counts


def _build_top_index(wiki_dir: Path) -> str:
    """Erstellt den Top-Level-Index mit Domain-Tabelle."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    counts = _count_domain_pages(wiki_dir)

    lines: list[str] = [
        "# Knowledge Tree — Index",
        "",
        f"> Automatisch generiert. Stand: {today}",
        "",
        "| Domain | Beschreibung | Seiten | Zuletzt aktualisiert |",
        "|--------|--------------|--------|---------------------|",
    ]

    for domain, desc in DOMAIN_DESCRIPTIONS.items():
        count = counts.get(domain, 0)
        index_path = get_domain_index_path(wiki_dir, domain)
        if index_path.exists():
            lines.append(f"| [[index-{domain}]] | {desc} | {count} | {today} |")
        else:
            lines.append(f"| {domain} | {desc} | — | — |")

    lines.append("")
    return "\n".join(lines)


def update_domain_index(
    result: IngestResponse,
    domain: str,
    wiki_dir: Path,
    log: logging.Logger,
) -> None:
    """
    Aktualisiert index-{domain}.md mit den neu erstellten/aktualisierten Seiten.
    Aktualisiert anschließend index.md (top-level) mit Domain-Zähler.
    """
    domain_index_path = get_domain_index_path(wiki_dir, domain)

    # Bestehenden Domain-Index lesen
    existing_content = (
        domain_index_path.read_text(encoding="utf-8")
        if domain_index_path.exists()
        else f"# Domain-Index: {domain}\n\n(noch leer)\n"
    )

    # Neue Einträge aus den geschriebenen Seiten extrahieren
    new_entries: dict[str, tuple[str, str, str]] = {}
    for page in result.pages:
        page_path = page.path.lstrip("/")
        if page_path.startswith("wiki/"):
            page_path = page_path[len("wiki/"):]

        # Interne Seiten überspringen
        if page_path in ("log.md", "index.md") or page_path.startswith("index-"):
            continue

        slug = _page_slug(page_path)
        title = _extract_frontmatter_field(page.content, "title") or slug
        page_type = _extract_frontmatter_field(page.content, "type") or "concept"
        confidence = _extract_frontmatter_field(page.content, "confidence") or "medium"

        new_entries[slug] = (title, page_type, confidence)
        log.debug("Domain-Index Eintrag: [[%s]] — %s (%s)", slug, title, confidence)

    if not new_entries:
        log.info("Keine neuen Domain-Index-Einträge")
        return

    # Domain-Index neu aufbauen
    updated_domain_index = _build_domain_index(existing_content, new_entries, domain)
    domain_index_path.write_text(updated_domain_index, encoding="utf-8")
    log.info(
        "Domain-Index aktualisiert: index-%s.md (%d neue/aktualisierte Einträge)",
        domain, len(new_entries),
    )

    # Top-Level-Index aktualisieren
    top_index_path = wiki_dir / "index.md"
    top_index_content = _build_top_index(wiki_dir)
    top_index_path.write_text(top_index_content, encoding="utf-8")
    log.info("Top-Level-Index aktualisiert: index.md")

# ---------------------------------------------------------------------------
# Haupt-Ingest-Funktion
# ---------------------------------------------------------------------------

def ingest(source_file: str, node: str = "default") -> None:
    """
    Ingestiert eine Quelldatei in den Knowledge Tree.

    Args:
        source_file: Pfad zur Quelldatei (PPTX/DOCX/PDF/.md)
        node: Vault-Node (z.B. "company", "team-demand-ai", "personal-christian").
              "default" schreibt in den Vault-Root.
    """
    source_path = Path(source_file).resolve()
    log = setup_logging(source_path.name)

    log.info("=" * 60)
    log.info("INGEST START  %s  (node: %s)", source_path.name, node)
    log.info("=" * 60)

    if not source_path.exists():
        log.error("Datei nicht gefunden: %s", source_path)
        sys.exit(1)

    # Pfade für diesen Node auflösen
    node_root, wiki_dir, raw_dir = resolve_node_paths(node)
    wiki_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    log.info("Wiki-Verzeichnis: %s", wiki_dir)

    try:
        # 1. Extrahieren (PPTX/DOCX/PDF → .md, mit Cache)
        md_path = extract_if_needed(source_path, raw_dir, node_root, log)
        source_content = md_path.read_text(encoding="utf-8")

        if len(source_content.strip()) < 50:
            log.warning(
                "Dateiinhalt zu kurz (%d Zeichen) — überspringe", len(source_content.strip())
            )
            sys.exit(0)

        log.info("Quelltextlänge: %d Zeichen", len(source_content))

        # 2. Azure OpenAI Client erstellen
        client, deployment = make_client()

        # 3. Domain-Klassifikation (günstiger Pre-Call)
        classification = classify_document(
            source_name=source_path.name,
            source_preview=source_content,
            client=client,
            deployment=deployment,
            log=log,
        )
        domain = classification.domain

        # 4. Wiki-Kontext laden (nur domain-spezifischer Index, nicht alle Seiten)
        claude_md, domain_index, top_index, log_md = read_wiki_context(wiki_dir, domain, node_root)

        # 5. LLM-Hauptaufruf — erstellt Wiki-Seiten
        result = call_llm(
            source_name=source_path.name,
            source_content=source_content,
            domain=domain,
            claude_md=claude_md,
            domain_index=domain_index,
            top_index=top_index,
            log_md=log_md,
            client=client,
            deployment=deployment,
            log=log,
        )

        # 6. Seiten schreiben (mit Lock-Schutz für parallele Ingest-Prozesse)
        created, updated = write_pages(result, wiki_dir, log)

        # 7. Domain-Index + Top-Level-Index aktualisieren
        update_domain_index(result, domain, wiki_dir, log)

        log.info("-" * 60)
        log.info(
            "INGEST OK  —  Domain: %s | %d neue Seiten, %d aktualisiert",
            domain, len(created), len(updated),
        )
        log.info("-" * 60)

    except KeyboardInterrupt:
        log.warning("Abgebrochen.")
        sys.exit(1)
    except Exception as exc:
        log.exception("INGEST FEHLER: %s", exc)
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Knowledge Tree — Automatischer Ingest via Azure OpenAI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  uv run ingest.py dokument.pptx
  uv run ingest.py paper.pdf --node research
  uv run ingest.py meeting-notes.md --node team-demand-ai
  uv run ingest.py vertrag.docx --node company
        """,
    )
    parser.add_argument("source_file", help="Quelldatei (PPTX/DOCX/PDF/.md)")
    parser.add_argument(
        "--node",
        default="default",
        help="Vault-Node: default|company|team-<name>|personal-<user> (default: 'default')",
    )

    args = parser.parse_args()
    ingest(args.source_file, node=args.node)
