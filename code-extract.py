# /// script
# dependencies = ["openai", "httpx", "python-dotenv", "pydantic"]
# ///
"""
Knowledge Tree — Code-Extraktion: GitHub Commit → CommitDigest via LLM.

Usage:
  uv run code-extract.py <owner>/<repo> <sha>
  uv run code-extract.py <owner>/<repo> <sha> --token ghp_xxx

Gibt CommitDigest als JSON auf stdout aus.
GITHUB_PAT aus .env falls --token nicht gesetzt.
"""

from __future__ import annotations

import argparse
import io
import json
import logging
import os
import re
import sys
import time
from pathlib import Path

# UTF-8 erzwingen (Windows-Konsole)
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

import httpx
from openai import AzureOpenAI
from pydantic import BaseModel

from schemas import CommitDigest, FileChange, TicketRef

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_DIR / "code-extract.log", encoding="utf-8"),
    ],
)
console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s", "%Y-%m-%d %H:%M:%S"))
logging.getLogger().addHandler(console)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------

MAX_DIFF_CHARS = 8_000       # Diff wird auf diese Länge gekürzt (spart Tokens)
MAX_RETRIES = 3
RETRY_BACKOFF = [2, 5, 15]  # Sekunden

GITHUB_API = "https://api.github.com"

# ---------------------------------------------------------------------------
# GitHub API
# ---------------------------------------------------------------------------


def _github_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _request_with_retry(url: str, token: str) -> dict:
    """GET-Request mit Retry bei Netzwerkfehlern und Rate-Limit."""
    for attempt, wait in enumerate(RETRY_BACKOFF, 1):
        try:
            resp = httpx.get(url, headers=_github_headers(token), timeout=30)

            # Rate-Limit-Warning
            remaining = resp.headers.get("x-ratelimit-remaining", "?")
            if remaining != "?" and int(remaining) < 50:
                log.warning("GitHub Rate-Limit niedrig: %s Anfragen verbleibend", remaining)

            if resp.status_code == 404:
                raise ValueError(f"Nicht gefunden (404): {url}")
            if resp.status_code == 403:
                reset = resp.headers.get("x-ratelimit-reset", "?")
                raise ValueError(f"Zugriff verweigert (403) — Rate-Limit-Reset: {reset}")
            resp.raise_for_status()
            return resp.json()

        except (httpx.NetworkError, httpx.TimeoutException) as e:
            if attempt == len(RETRY_BACKOFF):
                raise
            log.warning("Netzwerkfehler (Versuch %d/%d): %s — warte %ds", attempt, len(RETRY_BACKOFF), e, wait)
            time.sleep(wait)

    raise RuntimeError("Alle Versuche ausgeschöpft")


def get_commit(owner: str, repo: str, sha: str, token: str) -> dict:
    """Holt vollständige Commit-Daten inkl. Diff-Patches via GitHub API."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/commits/{sha}"
    log.debug("GitHub API: %s", url)
    return _request_with_retry(url, token)


def get_pr_for_commit(owner: str, repo: str, sha: str, token: str) -> dict | None:
    """Gibt das erste PR-Objekt zurück das diesen Commit enthält, sonst None."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/commits/{sha}/pulls"
    try:
        prs = _request_with_retry(url, token)
        return prs[0] if prs else None
    except Exception as e:
        log.debug("Kein PR für Commit %s: %s", sha[:8], e)
        return None


def get_branch_for_commit(owner: str, repo: str, sha: str, token: str) -> str | None:
    """Sucht den Branch-Namen für einen Commit (best-effort)."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/branches"
    try:
        branches = _request_with_retry(url, token)
        for b in branches:
            if b.get("commit", {}).get("sha") == sha:
                return b["name"]
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Diff-Aufbereitung
# ---------------------------------------------------------------------------


def build_diff_text(commit_data: dict, max_chars: int = MAX_DIFF_CHARS) -> str:
    """Extrahiert und kürzt den Diff aus den Commit-Daten."""
    files = commit_data.get("files", [])
    parts: list[str] = []
    total = 0

    for f in files:
        filename = f.get("filename", "")
        status = f.get("status", "modified")
        patch = f.get("patch", "")

        header = f"--- {filename} ({status}) ---\n"
        entry = header + patch + "\n"

        if total + len(entry) > max_chars:
            remaining = max_chars - total - len(header)
            if remaining > 100:
                parts.append(header + patch[:remaining] + "\n[... gekürzt ...]")
            break

        parts.append(entry)
        total += len(entry)

    return "\n".join(parts) if parts else "(kein Diff verfügbar)"


def extract_ticket_refs(text: str, pattern: str, source: str) -> list[TicketRef]:
    """Extrahiert Ticket-Referenzen aus einem Text."""
    refs = []
    for match in set(re.findall(pattern, text)):
        refs.append(TicketRef(id=match, source=source, confidence=1.0))
    return refs


# ---------------------------------------------------------------------------
# LLM-Analyse
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
Du bist ein Code-Analyst der Git-Commits semantisch zusammenfasst für ein PM-Wissens-Wiki.

Deine Aufgabe: Analysiere Commit-Message, Diff und optional die PR-Beschreibung.
Erstelle eine strukturierte, fachlich präzise Zusammenfassung.

Regeln:
- semantic_summary: Was wurde FACHLICH erreicht (nicht "Datei X geändert", sondern
  "Retry-Logik mit Exponential Backoff für Azure OpenAI API eingebaut um transiente
  Fehler abzufangen"). 1-3 prägnante Sätze.
- impact_areas: Betroffene Fachdomänen oder Module als kurze Strings,
  z.B. ["auth", "forecasting-engine", "api-gateway"]
- complexity: small (<50 LOC), medium (<200 LOC), large (>200 LOC),
  refactor (strukturelle Änderung ohne neue Funktionalität)
- shared_concept: Nur wenn ein wiederverwendbares, projektunabhängiges Muster erkennbar ist
  (z.B. "Exponential Backoff Pattern", "Pydantic Structured Output"). Sonst null.
- files_changed[].module: Zu welchem logischen Modul/Subsystem gehört diese Datei?
- Ticket-Refs aus dem Kontext übernehmen (aus commit_message und branch_name).
- Sprache der Zusammenfassung: Deutsch.
"""


def analyse_commit(
    commit_data: dict,
    pr_data: dict | None,
    branch_name: str | None,
    ticket_refs: list[TicketRef],
    repo_name: str,
    repo_owner: str,
    client: AzureOpenAI,
    deployment: str,
) -> CommitDigest:
    """Lässt das LLM den Commit semantisch analysieren → CommitDigest."""

    commit_info = commit_data.get("commit", {})
    message = commit_info.get("message", "")
    author = commit_info.get("author", {}).get("name", "unknown")
    timestamp = commit_info.get("author", {}).get("date", "")
    sha = commit_data.get("sha", "")

    diff_text = build_diff_text(commit_data)

    # Kontext für LLM aufbauen
    context_parts = [
        f"## Commit {sha[:8]}",
        f"**Autor:** {author}",
        f"**Zeitstempel:** {timestamp}",
        f"**Message:**\n{message}",
    ]

    if branch_name:
        context_parts.append(f"**Branch:** {branch_name}")

    if pr_data:
        pr_title = pr_data.get("title", "")
        pr_body = pr_data.get("body", "") or ""
        context_parts.append(f"**PR-Titel:** {pr_title}")
        if pr_body.strip():
            context_parts.append(f"**PR-Beschreibung:**\n{pr_body[:2000]}")

    if ticket_refs:
        refs_str = ", ".join(f"{r.id} (aus {r.source})" for r in ticket_refs)
        context_parts.append(f"**Gefundene Ticket-Refs:** {refs_str}")

    context_parts.append(f"\n## Diff\n{diff_text}")

    user_message = "\n\n".join(context_parts)

    log.info(
        "LLM-Analyse — Repo: %s/%s | Commit: %s | Diff: %d Zeichen",
        repo_owner, repo_name, sha[:8], len(diff_text),
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            completion = client.beta.chat.completions.parse(
                model=deployment,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                response_format=CommitDigest,
                max_completion_tokens=4_000,
            )
            result = completion.choices[0].message.parsed
            if result is None:
                raise ValueError("LLM gab kein valides CommitDigest zurück")

            # Felder die wir selbst setzen
            result.sha = sha
            result.author = author
            result.timestamp = timestamp
            result.original_message = message
            result.repo_name = repo_name
            result.repo_owner = repo_owner

            # Ticket-Refs mergen (regex + LLM-erkannte)
            existing_ids = {r.id for r in result.ticket_refs}
            for ref in ticket_refs:
                if ref.id not in existing_ids:
                    result.ticket_refs.append(ref)

            log.info(
                "CommitDigest erstellt — Komplexität: %s | Tickets: %s | Impact: %s",
                result.complexity,
                [r.id for r in result.ticket_refs] or "keine",
                result.impact_areas,
            )
            return result

        except Exception as e:
            if attempt == MAX_RETRIES:
                raise
            wait = RETRY_BACKOFF[attempt - 1]
            log.warning("LLM-Fehler (Versuch %d/%d): %s — warte %ds", attempt, MAX_RETRIES, e, wait)
            time.sleep(wait)

    raise RuntimeError("LLM-Analyse gescheitert")


# ---------------------------------------------------------------------------
# Azure OpenAI Client
# ---------------------------------------------------------------------------


def build_client() -> tuple[AzureOpenAI, str]:
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")

    if not endpoint or not api_key:
        raise EnvironmentError(
            "AZURE_OPENAI_ENDPOINT und AZURE_OPENAI_API_KEY müssen in .env gesetzt sein"
        )

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version,
    )
    return client, deployment


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="GitHub Commit → CommitDigest via LLM. Gibt JSON auf stdout aus.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  uv run code-extract.py schlinge2000/pkwiki abc1234
  uv run code-extract.py inform-group/demand-ai HEAD --token ghp_xxx
""",
    )
    parser.add_argument("repo", help="owner/repo, z.B. schlinge2000/pkwiki")
    parser.add_argument("sha", help="Commit-SHA (vollständig oder Kurzform)")
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_PAT", ""),
        help="GitHub Personal Access Token (default: $GITHUB_PAT)",
    )
    parser.add_argument(
        "--ticket-pattern",
        default=r"[A-Z]+-\d+|#\d+",
        help="Regex für Ticket-IDs (default: '[A-Z]+-\\d+|#\\d+')",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if "/" not in args.repo:
        log.error("Ungültiges Repo-Format: '%s' — erwartet owner/repo", args.repo)
        sys.exit(1)

    if not args.token:
        log.error("Kein GitHub Token — GITHUB_PAT in .env setzen oder --token übergeben")
        sys.exit(1)

    owner, repo_name = args.repo.split("/", 1)

    log.info("=" * 60)
    log.info("CODE-EXTRACT  %s/%s  @%s", owner, repo_name, args.sha[:8])
    log.info("=" * 60)

    # GitHub-Daten holen
    commit_data = get_commit(owner, repo_name, args.sha, args.token)
    sha = commit_data["sha"]  # vollständige SHA
    message = commit_data.get("commit", {}).get("message", "")

    pr_data = get_pr_for_commit(owner, repo_name, sha, args.token)
    branch_name = get_branch_for_commit(owner, repo_name, sha, args.token)

    # Ticket-Refs via Regex
    ticket_refs: list[TicketRef] = []
    ticket_refs += extract_ticket_refs(message, args.ticket_pattern, "commit_message")
    if branch_name:
        ticket_refs += extract_ticket_refs(branch_name, args.ticket_pattern, "branch_name")
    if pr_data:
        ticket_refs += extract_ticket_refs(pr_data.get("title", ""), args.ticket_pattern, "pr_title")

    # Azure OpenAI
    client, deployment = build_client()

    # LLM-Analyse
    digest = analyse_commit(
        commit_data=commit_data,
        pr_data=pr_data,
        branch_name=branch_name,
        ticket_refs=ticket_refs,
        repo_name=repo_name,
        repo_owner=owner,
        client=client,
        deployment=deployment,
    )

    # JSON auf stdout
    print(digest.model_dump_json(indent=2))
    log.info("=" * 60)
    log.info("FERTIG — CommitDigest auf stdout ausgegeben")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
