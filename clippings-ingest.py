# /// script
# dependencies = []
# ///
"""
clippings-ingest.py — Eigene Pipeline für Obsidian-Web-Clipper-Clips.

Der Obsidian Web Clipper legt geclippte Web-Artikel als .md im Vault-Ordner
`Clippings/` ab — außerhalb von raw/. Dadurch sieht der reguläre Watcher
(watch.ps1, der nur raw/ überwacht) sie nie, und die Clips landen nie im
Wiki-Index. Dieses Skript schließt die Lücke: es scannt `Clippings/`, ruft für
jede neue bzw. geänderte .md den regulären ingest.py-Flow auf — fachlich
identisch zu einer raw/links-Quelle (Web-Artikel) — und beendet sich.

Designed für Scheduled-Task-Betrieb: ein Durchlauf, dann Exit. Der Task
Scheduler taktet das Intervall (analog zu cron, siehe watchers.json). Den
Bearbeitungs-State (path -> mtime) hält das Skript in .clippings-state.json,
damit bereits verarbeitete Clips nicht bei jedem Lauf erneut durch das LLM
gehen. (ingest.py schreibt für .md-Inputs keinen raw/.cache-Eintrag, daher
braucht diese Pipeline einen eigenen State — wie scan-raw.py.)

Usage:
  uv run clippings-ingest.py                       # Single-Poll: neue/geänderte Clips
  uv run clippings-ingest.py --force               # alle Clips erneut ingesten
  uv run clippings-ingest.py --dry-run             # nur anzeigen, nichts ingesten
  uv run clippings-ingest.py --clippings-dir PFAD  # abweichender Clippings-Ordner
"""

from __future__ import annotations

import argparse
import io
import json
import logging
import subprocess
import sys
from pathlib import Path

WIKI_ROOT = Path(__file__).parent
DEFAULT_CLIPPINGS_DIR = WIKI_ROOT / "Clippings"
DEFAULT_STATE_FILE = WIKI_ROOT / ".clippings-state.json"

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stderr,
)
log = logging.getLogger("clippings-ingest")


def load_state(path: Path) -> dict[str, float]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            log.warning("State-Datei defekt — starte frisch: %s", path)
    return {}


def save_state(path: Path, state: dict[str, float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--clippings-dir", type=Path, default=DEFAULT_CLIPPINGS_DIR,
                    help=f"Zu scannender Ordner (default: {DEFAULT_CLIPPINGS_DIR}).")
    ap.add_argument("--state-file", type=Path, default=DEFAULT_STATE_FILE,
                    help="JSON-Datei mit verarbeiteten Clips (path -> mtime).")
    ap.add_argument("--force", action="store_true",
                    help="State ignorieren und alle Clips erneut ingesten.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Nur anzeigen, was ingestet würde — kein LLM-Aufruf.")
    ap.add_argument("--timeout", type=int, default=600,
                    help="Timeout pro Clip in Sekunden (default: 600).")
    return ap.parse_args()


def main() -> int:
    args = parse_args()

    clip_dir = args.clippings_dir.resolve()
    if not clip_dir.is_dir():
        # Kein Fehler: der Ordner existiert evtl. noch nicht, weil noch nichts
        # geclippt wurde. Sauber beenden, damit der Scheduled Task nicht failt.
        log.info("Clippings-Ordner nicht vorhanden (noch nichts geclippt?): %s", clip_dir)
        return 0

    state: dict[str, float] = {} if args.force else load_state(args.state_file)

    files = sorted(
        p for p in clip_dir.glob("**/*.md")
        if p.is_file() and not p.name.startswith(".")
    )
    log.info("Scan %s: %d .md-Dateien, State kennt %d", clip_dir, len(files), len(state))

    new_count = 0
    failed = 0

    for f in files:
        rel = str(f.relative_to(clip_dir)).replace("\\", "/")
        mtime = f.stat().st_mtime
        if not args.force and state.get(rel) == mtime:
            continue

        if args.dry_run:
            log.info("WÜRDE INGESTEN: %s", rel)
            new_count += 1
            continue

        log.info("NEU/GEÄNDERT: %s", rel)
        try:
            proc = subprocess.run(
                ["uv", "run", str(WIKI_ROOT / "ingest.py"), str(f)],
                cwd=str(WIKI_ROOT),
                timeout=args.timeout,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if proc.returncode == 0:
                state[rel] = mtime
                save_state(args.state_file, state)
                new_count += 1
                log.info("OK    %s", rel)
            else:
                failed += 1
                tail = (proc.stderr or proc.stdout or "")[-500:]
                log.error("FEHLER %s (exit %d)\n%s", rel, proc.returncode, tail)
        except subprocess.TimeoutExpired:
            failed += 1
            log.error("TIMEOUT %s nach %ds", rel, args.timeout)
        except Exception as e:  # noqa: BLE001 — Batch darf an einer Datei nicht sterben
            failed += 1
            log.error("EXCEPTION %s: %s", rel, e)

    log.info("Fertig — %d verarbeitet, %d Fehler", new_count, failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
