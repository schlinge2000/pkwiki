# /// script
# dependencies = ["python-dotenv"]
# ///
"""
wiki-sync.py — Synchronisiert alle Wiki-MD-Dateien mit dem GitHub-Archiv-Repo.

Default (Push): Liest alle wiki/-Ordner aus VAULT_ROOT (alle Nodes) und pusht
geänderte Dateien in das Archiv-Repo (schlinge2000/knowledge-wiki-archive).

Pull-Modus (--pull): Kopiert Dateien, die im Archive existieren aber im Vault
fehlen, additiv in den Vault. Lokal abweichende Dateien werden NICHT
überschrieben (Konflikt-Report). Brauchbar nach PR-Merges im Archive.

Usage:
    uv run wiki-sync.py                  # Vault → Archive (push)
    uv run wiki-sync.py --pull           # Archive → Vault (pull, additiv)
    uv run wiki-sync.py --dry-run
    uv run wiki-sync.py --verbose

Benötigt in .env:
    VAULT_ROOT=C:\\Pfad\\zum\\Vault
    WIKI_ARCHIVE_PAT=ghp_...                         # GitHub PAT mit repo-Schreibrecht
    WIKI_ARCHIVE_REPO=schlinge2000/knowledge-wiki-archive  # optional, das ist der Default
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------

SCRIPT_ROOT = Path(__file__).parent
VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", os.environ.get("KNOWLEDGE_TREE_ROOT", str(SCRIPT_ROOT))))
WIKI_ARCHIVE_REPO = os.environ.get("WIKI_ARCHIVE_REPO", "schlinge2000/knowledge-wiki-archive")
WIKI_ARCHIVE_PAT = os.environ.get("WIKI_ARCHIVE_PAT", "")

# ---------------------------------------------------------------------------
# Wiki-Dateien sammeln
# ---------------------------------------------------------------------------

def collect_wiki_files(vault_root: Path) -> dict[str, Path]:
    """
    Sammelt alle *.md-Dateien aus allen wiki/-Ordnern im Vault.
    Gibt archive_path → abs_path zurück.

    Struktur im Archiv-Repo spiegelt die Vault-Struktur:
      _company/wiki/concepts/foo.md
      _team-demand-ai/wiki/sources/bar.md
      wiki/log.md  (Root-Node)
    """
    files: dict[str, Path] = {}

    def add_wiki_dir(wiki_dir: Path) -> None:
        if not wiki_dir.exists():
            return
        for f in wiki_dir.rglob("*.md"):
            archive_path = str(f.relative_to(vault_root)).replace("\\", "/")
            files[archive_path] = f

    # Root-Node
    add_wiki_dir(vault_root / "wiki")

    # Company-Node
    add_wiki_dir(vault_root / "_company" / "wiki")

    # Team-Nodes (inkl. verschachtelter Personal-Nodes)
    for team_dir in sorted(vault_root.glob("_team-*")):
        add_wiki_dir(team_dir / "wiki")
        for personal_dir in sorted(team_dir.glob("_personal-*")):
            add_wiki_dir(personal_dir / "wiki")

    # Personal-Nodes direkt unter VAULT_ROOT
    for personal_dir in sorted(vault_root.glob("_personal-*")):
        add_wiki_dir(personal_dir / "wiki")

    return files

# ---------------------------------------------------------------------------
# Git-Helfer
# ---------------------------------------------------------------------------

def git(args: list[str], cwd: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, check=check)


def clone_archive(tmpdir: str) -> None:
    if not WIKI_ARCHIVE_PAT:
        print("ERROR: WIKI_ARCHIVE_PAT nicht gesetzt (.env oder Umgebungsvariable)", file=sys.stderr)
        sys.exit(1)

    clone_url = f"https://x-access-token:{WIKI_ARCHIVE_PAT}@github.com/{WIKI_ARCHIVE_REPO}.git"
    result = subprocess.run(
        ["git", "clone", "--depth=1", clone_url, tmpdir],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: Klonen fehlgeschlagen:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------
# Sync
# ---------------------------------------------------------------------------

def sync(dry_run: bool = False, verbose: bool = False) -> None:
    files = collect_wiki_files(VAULT_ROOT)

    if not files:
        print(f"Keine Wiki-Dateien gefunden in: {VAULT_ROOT}")
        return

    print(f"Wiki-Dateien gefunden: {len(files)}  (VAULT_ROOT: {VAULT_ROOT})")

    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Klone {WIKI_ARCHIVE_REPO}...")
        clone_archive(tmpdir)

        changed: list[str] = []
        for archive_path, abs_path in sorted(files.items()):
            dest = Path(tmpdir) / archive_path
            dest.parent.mkdir(parents=True, exist_ok=True)

            content = abs_path.read_bytes()
            if dest.exists() and dest.read_bytes() == content:
                if verbose:
                    print(f"  = {archive_path}")
                continue

            if not dry_run:
                dest.write_bytes(content)

            prefix = "[DRY] " if dry_run else ""
            print(f"  {prefix}→ {archive_path}")
            changed.append(archive_path)

        if not changed:
            print("Keine Änderungen — nichts zu pushen.")
            return

        print(f"\n{len(changed)} Datei(en) geändert.")

        if dry_run:
            return

        git(["config", "user.email", "wiki-sync@knowledge-tree"], cwd=tmpdir)
        git(["config", "user.name", "wiki-sync"], cwd=tmpdir)
        git(["add", "-A"], cwd=tmpdir)

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        commit_msg = f"wiki: sync {timestamp} ({len(changed)} Datei(en))"
        result = git(["commit", "-m", commit_msg], cwd=tmpdir, check=False)
        if result.returncode != 0:
            print("Nichts zu committen.")
            return

        result = git(["push"], cwd=tmpdir, check=False)
        if result.returncode != 0:
            print(f"ERROR: Push fehlgeschlagen:\n{result.stderr}", file=sys.stderr)
            sys.exit(1)

        print(f"Erfolgreich gepusht → github.com/{WIKI_ARCHIVE_REPO}")

# ---------------------------------------------------------------------------
# Pull (Archive → Vault, additiv)
# ---------------------------------------------------------------------------

def pull(dry_run: bool = False, verbose: bool = False) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Klone {WIKI_ARCHIVE_REPO}...")
        clone_archive(tmpdir)

        tmppath = Path(tmpdir)
        archive_files: list[tuple[str, Path]] = []
        for f in tmppath.rglob("*.md"):
            if ".git" in f.parts:
                continue
            rel = str(f.relative_to(tmppath)).replace("\\", "/")
            archive_files.append((rel, f))

        print(f"Wiki-Dateien im Archive: {len(archive_files)}  (Vault: {VAULT_ROOT})")

        added: list[str] = []
        conflicts: list[str] = []
        for archive_path, src in sorted(archive_files):
            dest = VAULT_ROOT / archive_path
            content = src.read_bytes()

            if dest.exists():
                if dest.read_bytes() == content:
                    if verbose:
                        print(f"  = {archive_path}")
                else:
                    print(f"  ! KONFLIKT (lokal abweichend, übersprungen): {archive_path}")
                    conflicts.append(archive_path)
                continue

            prefix = "[DRY] " if dry_run else ""
            print(f"  {prefix}+ {archive_path}")
            if not dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(content)
            added.append(archive_path)

        unchanged = len(archive_files) - len(added) - len(conflicts)
        print(f"\nHinzugefügt: {len(added)}, Konflikte: {len(conflicts)}, Unverändert: {unchanged}")
        if conflicts:
            print("Konflikte müssen manuell aufgelöst werden (Vault-Datei prüfen, ggf. mergen).")

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Wiki-Sync: OneDrive-Vault ↔ GitHub Archive Repo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  uv run wiki-sync.py                  Push: Vault → Archive
  uv run wiki-sync.py --pull           Pull: Archive → Vault (additiv)
  uv run wiki-sync.py --dry-run        Nur anzeigen
  uv run wiki-sync.py --verbose        Auch unveränderte Dateien anzeigen
        """,
    )
    parser.add_argument("--pull", action="store_true", help="Archive → Vault: fehlende Dateien aus Archive in den Vault kopieren")
    parser.add_argument("--dry-run", action="store_true", help="Nur anzeigen, keine Schreibvorgänge")
    parser.add_argument("--verbose", "-v", action="store_true", help="Unveränderte Dateien auch anzeigen")

    args = parser.parse_args()
    if args.pull:
        pull(dry_run=args.dry_run, verbose=args.verbose)
    else:
        sync(dry_run=args.dry_run, verbose=args.verbose)
