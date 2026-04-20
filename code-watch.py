# /// script
# dependencies = ["httpx", "python-dotenv", "pydantic", "pyyaml"]
# ///
"""
Knowledge Tree — Code-Watcher: GitHub API Poller für alle konfigurierten Repos.

Pollt alle N Minuten neue Commits und triggert code-extract.py + code-ingest.py.
State (letzte verarbeitete SHA pro Repo) wird in .code-watch-state.json gespeichert.

Usage:
  uv run code-watch.py                          # einmalig alle Repos prüfen
  uv run code-watch.py --loop                   # Endlosschleife (Daemon-Modus)
  uv run code-watch.py --repo demand-ai         # nur ein Repo
  uv run code-watch.py --since 2026-04-19T00:00:00Z  # ab Zeitstempel

Konfiguration: code-repos.yaml (nicht in git, enthält interne Repo-Namen)
"""

from __future__ import annotations

import argparse
import io
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

import httpx

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from schemas import RepoConfig, WatchConfig

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[logging.FileHandler(LOG_DIR / "code-watch.log", encoding="utf-8")],
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s", "%Y-%m-%d %H:%M:%S"))
logging.getLogger().addHandler(console)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------

SCRIPT_ROOT = Path(__file__).parent
VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", str(SCRIPT_ROOT)))
STATE_FILE = VAULT_ROOT / ".code-watch-state.json"
CONFIG_FILE = SCRIPT_ROOT / "code-repos.yaml"   # im Code-Verzeichnis, nicht im Vault
GITHUB_API = "https://api.github.com"
EXTRACT_SCRIPT = SCRIPT_ROOT / "code-extract.py"
INGEST_SCRIPT = SCRIPT_ROOT / "code-ingest.py"

# ---------------------------------------------------------------------------
# Konfiguration laden
# ---------------------------------------------------------------------------


def load_config() -> WatchConfig:
    """Lädt code-repos.yaml. Fällt auf Umgebungsvariablen zurück wenn kein YAML."""
    token = os.environ.get("GITHUB_PAT", "")
    if not token:
        raise EnvironmentError("GITHUB_PAT muss in .env oder als Umgebungsvariable gesetzt sein")

    if CONFIG_FILE.exists():
        if not HAS_YAML:
            raise ImportError("PyYAML nicht installiert: uv add pyyaml")
        with CONFIG_FILE.open(encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        raw["github_token"] = token  # aus .env überschreiben
        return WatchConfig.model_validate(raw)

    # Fallback: Minimal-Konfiguration aus Umgebungsvariablen
    log.warning("code-repos.yaml nicht gefunden — verwende WATCH_REPO env var")
    watch_repo = os.environ.get("WATCH_REPO", "")
    if not watch_repo or "/" not in watch_repo:
        raise EnvironmentError(
            "code-repos.yaml nicht gefunden und WATCH_REPO nicht gesetzt.\n"
            "Erstelle code-repos.yaml (siehe vault-tree.yaml.example) oder\n"
            "setze WATCH_REPO=owner/repo in .env"
        )
    owner, repo = watch_repo.split("/", 1)
    return WatchConfig(
        github_token=token,
        repos=[RepoConfig(name=repo, owner=owner, repo=repo)],
    )


# ---------------------------------------------------------------------------
# State-Verwaltung
# ---------------------------------------------------------------------------


def load_state() -> dict[str, str]:
    """Lädt letzten bekannten Commit-SHA pro Repo aus State-Datei."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            log.warning("State-Datei beschädigt — starte frisch")
    return {}


def save_state(state: dict[str, str]) -> None:
    """Schreibt State atomar (temp + rename)."""
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    tmp.replace(STATE_FILE)


# ---------------------------------------------------------------------------
# GitHub API
# ---------------------------------------------------------------------------


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def get_new_commits(repo: RepoConfig, token: str, since: str | None) -> list[dict]:
    """
    Holt neue Commits seit `since` (ISO 8601) oder seit dem letzten bekannten SHA.
    Gibt Commits älteste-zuerst zurück.
    """
    url = f"{GITHUB_API}/repos/{repo.owner}/{repo.repo}/commits"
    params: dict[str, str] = {"sha": repo.branch, "per_page": "50"}
    if since:
        params["since"] = since

    try:
        resp = httpx.get(url, headers=_headers(token), params=params, timeout=30)

        remaining = resp.headers.get("x-ratelimit-remaining", "?")
        if remaining != "?" and int(remaining) < 100:
            log.warning("Rate-Limit niedrig: %s verbleibend", remaining)

        if resp.status_code == 404:
            log.error("Repo nicht gefunden: %s/%s", repo.owner, repo.repo)
            return []
        if resp.status_code == 403:
            log.error("Kein Zugriff auf %s/%s (403)", repo.owner, repo.repo)
            return []
        resp.raise_for_status()

        commits = resp.json()
        # älteste zuerst
        return list(reversed(commits))

    except httpx.NetworkError as e:
        log.error("Netzwerkfehler bei %s/%s: %s", repo.owner, repo.repo, e)
        return []


# ---------------------------------------------------------------------------
# Pipeline-Ausführung
# ---------------------------------------------------------------------------


def run_pipeline(repo: RepoConfig, sha: str, token: str) -> bool:
    """
    Führt code-extract.py | code-ingest.py für einen Commit aus.
    Gibt True bei Erfolg zurück.
    """
    log.info("  Pipeline: %s/%s @%s", repo.owner, repo.repo, sha[:8])

    try:
        # code-extract.py → JSON auf stdout
        extract_proc = subprocess.run(
            ["uv", "run", str(EXTRACT_SCRIPT), f"{repo.owner}/{repo.repo}", sha,
             "--token", token, "--ticket-pattern", repo.ticket_pattern],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=VAULT_ROOT,
            timeout=120,
        )

        if extract_proc.returncode != 0:
            log.error("code-extract.py fehlgeschlagen (exit %d):\n%s",
                      extract_proc.returncode, extract_proc.stderr[-500:])
            return False

        digest_json = extract_proc.stdout

        # code-ingest.py liest JSON von stdin
        ingest_proc = subprocess.run(
            ["uv", "run", str(INGEST_SCRIPT)],
            input=digest_json,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=VAULT_ROOT,
            timeout=180,
        )

        if ingest_proc.returncode != 0:
            log.error("code-ingest.py fehlgeschlagen (exit %d):\n%s",
                      ingest_proc.returncode, ingest_proc.stderr[-500:])
            return False

        log.info("  OK — %s", sha[:8])
        return True

    except subprocess.TimeoutExpired:
        log.error("Timeout bei %s/%s @%s", repo.owner, repo.repo, sha[:8])
        return False
    except Exception as e:
        log.error("Unerwarteter Fehler: %s", e)
        return False


# ---------------------------------------------------------------------------
# Haupt-Poll-Schleife
# ---------------------------------------------------------------------------


def poll_once(config: WatchConfig, state: dict[str, str], args: argparse.Namespace) -> dict[str, str]:
    """Pollt alle Repos einmal. Gibt aktualisierten State zurück."""
    now = datetime.now(timezone.utc).isoformat()

    for repo in config.repos:
        # Filter wenn --repo gesetzt
        if args.repo and args.repo != repo.name:
            continue

        repo_key = f"{repo.owner}/{repo.repo}"
        last_sha = state.get(repo_key)

        # Since-Timestamp: entweder CLI-Arg, aus State oder letzter bekannter SHA
        since = args.since or None
        if not since and not last_sha:
            # Erstes Mal: nur letzten 24h
            from datetime import timedelta
            since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
            log.info("Repo %s: erstes Polling — letzten 24h", repo_key)

        log.info("Prüfe %s (branch: %s) ...", repo_key, repo.branch)
        commits = get_new_commits(repo, config.github_token, since)

        # Bereits verarbeitete SHAs überspringen
        new_commits = []
        found_last = last_sha is None
        for c in commits:
            sha = c["sha"]
            if not found_last:
                if sha == last_sha:
                    found_last = True
                continue
            new_commits.append(sha)

        if not new_commits:
            log.info("  Keine neuen Commits.")
            continue

        log.info("  %d neue Commits gefunden.", len(new_commits))
        last_ok_sha = last_sha

        for sha in new_commits:
            ok = run_pipeline(repo, sha, config.github_token)
            if ok:
                last_ok_sha = sha
                state[repo_key] = sha
                save_state(state)  # nach jedem Commit sichern
            else:
                log.warning("  Pipeline fehlgeschlagen für %s — überspringe", sha[:8])
                break  # bei Fehler stoppen, nächstes Mal neu versuchen

    return state


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="GitHub Repos auf neue Commits beobachten und Code-Wiki aktualisieren.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  uv run code-watch.py                      # einmalig alle Repos prüfen
  uv run code-watch.py --loop               # Daemon-Modus
  uv run code-watch.py --repo demand-ai     # nur ein Repo
  uv run code-watch.py --since 2026-04-19T00:00:00Z
""",
    )
    parser.add_argument("--loop", action="store_true", help="Endlosschleife mit poll_interval_minutes Pause")
    parser.add_argument("--repo", default="", help="Nur dieses Repo verarbeiten (name aus code-repos.yaml)")
    parser.add_argument("--since", default="", help="ISO 8601 Timestamp: Commits ab diesem Zeitpunkt")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()
    state = load_state()

    if args.loop:
        log.info("Daemon-Modus — Interval: %d Minuten", config.poll_interval_minutes)
        while True:
            log.info("=" * 60)
            log.info("POLL-RUNDE — %s", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
            log.info("=" * 60)
            try:
                state = poll_once(config, state, args)
            except Exception as e:
                log.error("Poll-Fehler: %s", e)
            log.info("Warte %d Minuten...", config.poll_interval_minutes)
            time.sleep(config.poll_interval_minutes * 60)
    else:
        log.info("=" * 60)
        log.info("EINMALIGER POLL — %s", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
        log.info("=" * 60)
        state = poll_once(config, state, args)
        log.info("Fertig.")


if __name__ == "__main__":
    main()
