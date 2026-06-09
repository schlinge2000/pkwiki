# /// script
# dependencies = ["openai", "python-dotenv", "pydantic"]
# ///
"""
Knowledge Tree — PM-Synthese: Taeglich aktualiserter Cross-Repo PM-Digest.

Liest alle code-wiki/<projekt>/tickets/*.md und generiert:
  wiki/meta/pm-overview.md   -- Ticket-Status, Repo-Aktivitaet, Momentum
  wiki/meta/patterns.md      -- Cross-Repo Muster die generalisierbar sind

Usage:
  uv run pm-synthesize.py                    # alle Repos
  uv run pm-synthesize.py --repo demand-ai   # nur ein Repo
  uv run pm-synthesize.py --days 14          # Zeitfenster in Tagen (default: 14)
"""

from __future__ import annotations

import argparse
import io
import logging
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Literal

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    from dotenv import load_dotenv
    # Order: OS env > Vault .env (kanonisch, OneDrive-synced) > Script-local .env (Fallback)
    _vault = os.environ.get("VAULT_ROOT")
    if _vault:
        load_dotenv(Path(_vault) / ".env", override=False)
    load_dotenv(Path(__file__).parent / ".env", override=False)
except ImportError:
    pass

from openai import AzureOpenAI
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

SCRIPT_ROOT = Path(__file__).parent
VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", str(SCRIPT_ROOT)))
LOG_DIR = VAULT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[logging.FileHandler(LOG_DIR / "pm-synthesize.log", encoding="utf-8")],
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s", "%Y-%m-%d %H:%M:%S"))
logging.getLogger().addHandler(console)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------


class TicketStatus(BaseModel):
    ticket_id: str
    project: str
    commit_count: int
    last_commit_date: str
    inferred_status: Literal["active", "stagnant", "done", "unknown"]
    summary: str                         # 1 Satz: was wurde an diesem Ticket gebaut


class HotModule(BaseModel):
    module: str
    project: str
    commit_count: int
    signal: str                          # z.B. "in Flux — moeglicherweise technische Schulden"


class CrossPattern(BaseModel):
    pattern: str                         # z.B. "Retry mit Exponential Backoff"
    projects: list[str]                  # in welchen Projekten gesehen
    recommendation: str                  # z.B. "shared library kandidat"


class PMDigest(BaseModel):
    period: str                          # z.B. "2026-W16 (14 Tage)"
    open_tickets: list[TicketStatus]
    hot_modules: list[HotModule]
    cross_patterns: list[CrossPattern]
    executive_summary: str               # 3-5 Saetze fuer Fuehrungsebene
    pm_overview_md: str                  # fertiges Markdown fuer wiki/meta/pm-overview.md
    patterns_md: str                     # fertiges Markdown fuer wiki/meta/patterns.md


# ---------------------------------------------------------------------------
# Code-Wiki Daten laden
# ---------------------------------------------------------------------------


def find_code_wiki_dirs(wiki_dir: Path, repo_filter: str = "") -> list[tuple[str, Path]]:
    """Findet alle code-wiki/<projekt>/ Verzeichnisse."""
    code_wiki_root = wiki_dir / "code-wiki"
    if not code_wiki_root.exists():
        log.warning("code-wiki/ Verzeichnis nicht gefunden: %s", code_wiki_root)
        return []

    dirs = []
    for d in sorted(code_wiki_root.iterdir()):
        if d.is_dir() and not d.name.startswith("."):
            if repo_filter and d.name != repo_filter:
                continue
            dirs.append((d.name, d))

    return dirs


def load_ticket_pages(project_dir: Path, since_date: datetime) -> list[dict]:
    """Laedt alle Ticket-Seiten eines Projekts."""
    tickets_dir = project_dir / "tickets"
    if not tickets_dir.exists():
        return []

    tickets = []
    for md_file in sorted(tickets_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        stat = md_file.stat()
        last_modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

        # Commit-Anzahl aus Content schaetzen (Zeilen mit SHA-Pattern)
        commit_count = len(re.findall(r"\b[0-9a-f]{7,8}\b", content))

        tickets.append({
            "ticket_id": md_file.stem,
            "content": content[:2000],          # gekuerzt fuer LLM-Kontext
            "last_modified": last_modified.strftime("%Y-%m-%d"),
            "commit_count": max(1, commit_count),
            "days_since_update": (datetime.now(timezone.utc) - last_modified).days,
        })

    return tickets


def load_module_pages(project_dir: Path) -> list[dict]:
    """Laedt alle Modul-Seiten eines Projekts."""
    modules_dir = project_dir / "modules"
    if not modules_dir.exists():
        return []

    modules = []
    for md_file in sorted(modules_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        stat = md_file.stat()
        last_modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        commit_count = len(re.findall(r"\b[0-9a-f]{7,8}\b", content))

        modules.append({
            "module": md_file.stem,
            "content": content[:1000],
            "last_modified": last_modified.strftime("%Y-%m-%d"),
            "commit_count": max(1, commit_count),
        })

    return modules


def load_changelog(project_dir: Path, max_lines: int = 30) -> str:
    """Laedt die letzten N Zeilen des Changelogs."""
    changelog = project_dir / "changelog.md"
    if not changelog.exists():
        return ""
    lines = changelog.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[:max_lines])


def build_context(repos: list[tuple[str, Path]], since_date: datetime) -> str:
    """Baut den vollstaendigen LLM-Kontext aus allen Repo-Daten."""
    parts = []

    for repo_name, project_dir in repos:
        parts.append(f"# Projekt: {repo_name}")

        # Changelog
        changelog = load_changelog(project_dir)
        if changelog:
            parts.append(f"## Changelog (letzte Aktivitaet)\n{changelog}")

        # Tickets
        tickets = load_ticket_pages(project_dir, since_date)
        if tickets:
            parts.append(f"## Tickets ({len(tickets)} gefunden)")
            for t in tickets:
                parts.append(
                    f"### {t['ticket_id']}\n"
                    f"- Letztes Update: {t['last_modified']} ({t['days_since_update']} Tage)\n"
                    f"- Commits (ca.): {t['commit_count']}\n"
                    f"{t['content']}"
                )

        # Module
        modules = load_module_pages(project_dir)
        if modules:
            parts.append(f"## Module ({len(modules)} gefunden)")
            for m in modules:
                parts.append(
                    f"### {m['module']} (Commits: {m['commit_count']}, "
                    f"zuletzt: {m['last_modified']})\n{m['content']}"
                )

        parts.append("---")

    total = "\n\n".join(parts)

    # Auf 60k Zeichen kuerzen falls noetig
    if len(total) > 60_000:
        log.warning("Kontext zu lang (%d Zeichen) -- kuerze auf 60k", len(total))
        total = total[:60_000] + "\n\n[... gekuerzt ...]"

    return total


# ---------------------------------------------------------------------------
# LLM-Aufruf
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
Du bist ein erfahrener Product Manager der Code-Aktivitaet analysiert und
daraus strukturierte PM-Reports erstellt.

Du erhaeelst eine Zusammenfassung der Code-Aktivitaet aus mehreren Projekten
der letzten Wochen (Ticket-Seiten, Modul-Seiten, Changelogs).

Erstelle einen PM-Digest mit folgenden Schwerpunkten:

1. **Ticket-Status** -- Inferiere den Status aus Commit-Frequenz:
   - active: Commits in den letzten 7 Tagen
   - stagnant: Letzter Commit > 14 Tage, aber Ticket offen
   - done: Explizit als abgeschlossen markiert oder keine Aktivitaet > 30 Tage
   - unknown: Zu wenig Information

2. **Heisse Module** -- Welche Module wurden haeufig angefasst?
   Signal: > 3 Commits in 2 Wochen = "in Flux"

3. **Cross-Projekt-Muster** -- Gleiche Muster in mehreren Projekten:
   z.B. Retry-Logik, Auth-Handling, Azure OpenAI Integration

4. **pm_overview_md** -- Fertiges Markdown fuer wiki/meta/pm-overview.md:
   - Tabelle mit Ticket-Status
   - Repo-Momentum (Commits letzte 7 Tage)
   - Datum ganz oben

5. **patterns_md** -- Fertiges Markdown fuer wiki/meta/patterns.md:
   - Jedes Muster als eigener Abschnitt
   - Empfehlung (shared library? dokumentieren? ignorieren?)

Regeln:
- Kein Code in den Ausgaben, nur semantische Beschreibungen
- Sprache: Deutsch
- executive_summary: 3-5 Saetze fuer einen CTO oder CPO
- pm_overview_md und patterns_md: vollstaendige, fertige Markdown-Dokumente
"""


def call_llm(context: str, period: str, client: AzureOpenAI, deployment: str) -> PMDigest:
    user_message = f"## Analysezeitraum: {period}\n\n{context}"

    log.info("LLM-Aufruf -- Deployment: %s | Kontext: %d Zeichen", deployment, len(context))

    completion = client.beta.chat.completions.parse(
        model=deployment,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format=PMDigest,
        max_completion_tokens=8_000,
    )

    result = completion.choices[0].message.parsed
    if result is None:
        raise ValueError("LLM gab kein valides PMDigest zurueck")

    log.info(
        "PMDigest erstellt -- %d Tickets, %d heisse Module, %d Muster",
        len(result.open_tickets),
        len(result.hot_modules),
        len(result.cross_patterns),
    )
    return result


# ---------------------------------------------------------------------------
# Output schreiben
# ---------------------------------------------------------------------------


def write_outputs(digest: PMDigest, wiki_dir: Path) -> None:
    meta_dir = wiki_dir / "meta"
    meta_dir.mkdir(parents=True, exist_ok=True)

    # pm-overview.md (taegliche Ueberschreibung)
    overview_path = meta_dir / "pm-overview.md"
    overview_path.write_text(digest.pm_overview_md, encoding="utf-8")
    log.info("Geschrieben: wiki/meta/pm-overview.md")

    # patterns.md (taegliche Ueberschreibung)
    patterns_path = meta_dir / "patterns.md"
    patterns_path.write_text(digest.patterns_md, encoding="utf-8")
    log.info("Geschrieben: wiki/meta/patterns.md")

    # Executive Summary auf stdout
    print("\n" + "=" * 60)
    print(f"PM-Digest — {digest.period}")
    print("=" * 60)
    print(f"\n{digest.executive_summary}\n")

    if digest.open_tickets:
        print(f"Tickets: {len(digest.open_tickets)}")
        for t in digest.open_tickets:
            status_icon = {"active": "✓", "stagnant": "!", "done": "✓✓", "unknown": "?"}.get(t.inferred_status, "?")
            print(f"  [{status_icon}] {t.ticket_id} ({t.project}) — {t.summary}")

    if digest.cross_patterns:
        print(f"\nCross-Projekt-Muster: {len(digest.cross_patterns)}")
        for p in digest.cross_patterns:
            print(f"  • {p.pattern} ({', '.join(p.projects)})")
    print()


# ---------------------------------------------------------------------------
# Azure OpenAI Client
# ---------------------------------------------------------------------------


def build_client() -> tuple[AzureOpenAI, str]:
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")

    if not endpoint or not api_key:
        raise EnvironmentError("AZURE_OPENAI_ENDPOINT und AZURE_OPENAI_API_KEY in .env setzen")

    return AzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version=api_version), deployment


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cross-Repo PM-Digest aus code-wiki/ generieren.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  uv run pm-synthesize.py                      # alle Repos, letzte 14 Tage
  uv run pm-synthesize.py --repo demand-ai     # nur ein Repo
  uv run pm-synthesize.py --days 7             # letzte 7 Tage
""",
    )
    parser.add_argument("--repo", default="", help="Nur dieses Repo analysieren")
    parser.add_argument("--days", type=int, default=14, help="Analysezeitraum in Tagen (default: 14)")
    parser.add_argument(
        "--wiki-dir",
        type=Path,
        default=VAULT_ROOT / "wiki",
        help=f"Pfad zum wiki/-Verzeichnis (default: {VAULT_ROOT / 'wiki'})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    wiki_dir: Path = args.wiki_dir
    since_date = datetime.now(timezone.utc) - timedelta(days=args.days)
    period = f"{since_date.strftime('%Y-%m-%d')} bis {datetime.now(timezone.utc).strftime('%Y-%m-%d')} ({args.days} Tage)"

    log.info("=" * 60)
    log.info("PM-SYNTHESIZE -- Zeitraum: %s", period)
    log.info("=" * 60)

    # Repos finden
    repos = find_code_wiki_dirs(wiki_dir, args.repo)
    if not repos:
        log.error("Keine code-wiki/ Verzeichnisse gefunden in: %s", wiki_dir / "code-wiki")
        log.error("Stelle sicher dass code-watch.py bereits Commits ingested hat.")
        sys.exit(1)

    log.info("Repos gefunden: %s", [r[0] for r in repos])

    # Kontext aufbauen
    context = build_context(repos, since_date)
    log.info("Kontext: %d Zeichen", len(context))

    # LLM
    client, deployment = build_client()
    digest = call_llm(context, period, client, deployment)

    # Schreiben
    write_outputs(digest, wiki_dir)

    log.info("=" * 60)
    log.info("FERTIG -- pm-overview.md + patterns.md aktualisiert")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
