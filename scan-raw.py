# /// script
# dependencies = []
# ///
"""
scan-raw.py — generischer File-Watcher fuer Ingest-Pipelines.

Scannt ein Watch-Verzeichnis, ruft fuer neue bzw. geaenderte Dateien einen
konfigurierten Ingest-Befehl auf und beendet sich. Der State (welche Dateien
mit welcher mtime schon verarbeitet wurden) wird in einer JSON-Datei
persistiert — Neustarts holen Verpasstes automatisch nach.

Designed fuer Scheduled-Task-Betrieb: ein Durchlauf, dann Exit. Der Task
Scheduler taktet das Intervall (analog zu cron).

Usage:
  uv run scan-raw.py \\
    --watch-dir C:\\Code\\knowledge-wiki\\raw \\
    --ingest-cwd C:\\Code\\knowledge-wiki \\
    --ingest-cmd "uv run ingest.py" \\
    --state-file C:\\Code\\knowledge-wiki\\.scan-state.json

Der Ingest-Befehl wird pro Datei mit dem absoluten Pfad als letztem
Argument aufgerufen, z.B.:
  uv run ingest.py C:\\Code\\knowledge-wiki\\raw\\slides\\q2.pptx
"""

from __future__ import annotations

import argparse
import io
import json
import logging
import shlex
import subprocess
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stderr,
)
log = logging.getLogger(__name__)


def load_state(path: Path) -> dict[str, float]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            log.warning("State-Datei defekt - starte frisch: %s", path)
    return {}


def save_state(path: Path, state: dict[str, float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Scannt ein Verzeichnis und ruft fuer neue/geaenderte Dateien einen Ingest-Befehl auf.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--watch-dir", required=True, type=Path,
                    help="Verzeichnis, das gescannt wird.")
    ap.add_argument("--ingest-cwd", required=True, type=Path,
                    help="Working Directory fuer den Ingest-Befehl.")
    ap.add_argument("--ingest-cmd", required=True,
                    help='Ingest-Kommando, z.B. "uv run ingest.py". '
                         "Der absolute Datei-Pfad wird als letztes Argument angehaengt.")
    ap.add_argument("--state-file", required=True, type=Path,
                    help="JSON-Datei mit verarbeiteten Dateien (path -> mtime).")
    ap.add_argument("--glob", default="**/*",
                    help="Glob-Muster relativ zu --watch-dir (default: **/*).")
    ap.add_argument("--timeout", type=int, default=600,
                    help="Timeout pro Datei in Sekunden (default: 600).")
    ap.add_argument("--ignore", action="append", default=[],
                    help="Glob-Muster die ignoriert werden (mehrfach verwendbar).")
    return ap.parse_args()


def is_ignored(rel: str, patterns: list[str]) -> bool:
    from fnmatch import fnmatch
    return any(fnmatch(rel, pat) for pat in patterns)


def main() -> None:
    args = parse_args()

    if not args.watch_dir.is_dir():
        log.error("Watch-Dir nicht gefunden: %s", args.watch_dir)
        sys.exit(1)
    if not args.ingest_cwd.is_dir():
        log.error("Ingest-Cwd nicht gefunden: %s", args.ingest_cwd)
        sys.exit(1)

    state = load_state(args.state_file)
    cmd_prefix = shlex.split(args.ingest_cmd, posix=False)

    files = [p for p in args.watch_dir.glob(args.glob) if p.is_file()]
    log.info("Scan %s: %d Dateien, State kennt %d", args.watch_dir, len(files), len(state))

    new_count = 0
    failed = 0

    for f in sorted(files):
        rel = str(f.relative_to(args.watch_dir)).replace("\\", "/")
        if is_ignored(rel, args.ignore):
            continue

        mtime = f.stat().st_mtime
        if state.get(rel) == mtime:
            continue

        log.info("NEU/GEAENDERT: %s", rel)
        try:
            proc = subprocess.run(
                cmd_prefix + [str(f)],
                cwd=str(args.ingest_cwd),
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
        except Exception as e:
            failed += 1
            log.error("EXCEPTION %s: %s", rel, e)

    log.info("Fertig - %d verarbeitet, %d Fehler", new_count, failed)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
