# /// script
# dependencies = ["openai", "python-dotenv", "pydantic"]
# ///
"""
reorganise.py — Bestehendes Wiki-Wissen sortieren & Rechte labeln (Epic #28 / T1 nachträglich).

Legacy-Seiten (vor #37 ingestet) tragen meist kein `visibility:`-Feld → Default `personal`.
Dieses Skript klassifiziert jede kuratierte Seite (concepts/entities/sources/syntheses) per
Azure OpenAI in die Wissensschicht-Leiter und schreibt das Label ins Frontmatter:

    public < customer < internal < team < personal          (access.py = single source of truth)

Private Inhalte (`visibility: personal`) werden aus der **aktiven** Wiki entfernt — nicht hart
gelöscht, sondern nach `wiki/.trash/<relpfad>` verschoben (rückholbar, gitignored).

Sicher per Default:
  - **Dry-run**: ohne `--apply` wird nur ein Plan ausgegeben, nichts verändert.
  - **Graceful** (OKF „tolerate, don't reject"): eine fehlerhafte Einzelseite bricht den Lauf
    nie ab — Seite überspringen, warnen, weitermachen.
  - **Bestehende gültige Labels werden respektiert** (kein Override) außer mit `--reclassify`.

Usage:
    uv run reorganise.py                       # Dry-run über $VAULT_ROOT/wiki
    uv run reorganise.py --wiki-dir PATH       # abweichendes Wiki-Verzeichnis
    uv run reorganise.py --apply               # Labels schreiben + personal → .trash verschieben
    uv run reorganise.py --reclassify --apply  # auch bereits gelabelte Seiten neu einstufen
    uv run reorganise.py --limit 5             # nur die ersten 5 Seiten (zum Antesten)

Benötigt in .env (wie ingest.py):
    AZURE_OPENAI_API_KEY=...
    AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
    AZURE_OPENAI_DEPLOYMENT=gpt-4o
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    _vault = os.environ.get("VAULT_ROOT")
    if _vault:
        load_dotenv(Path(_vault) / ".env", override=False)
    load_dotenv(Path(__file__).parent / ".env", override=False)
except ImportError:
    pass

# access.py = single source of truth der visibility-Leiter (reine stdlib, testbar)
from access import VISIBILITY_LEVELS, normalize_visibility

SCRIPT_ROOT = Path(__file__).parent
VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", str(SCRIPT_ROOT)))

# Kuratierte Seitentypen tragen visibility. code-wiki/ & manuals/ erben Node-Sichtbarkeit (T5).
CURATED = ("concepts", "entities", "sources", "syntheses")
# Reservierte/generierte Dateien nie klassifizieren oder verschieben.
RESERVED = {"index.md", "log.md", "picture_index.md", "changelog.md", "image-index.md"}
TRASH_DIRNAME = ".trash"
PRIVATE = "personal"   # = VISIBILITY_LEVELS[-1]; diese Stufe wird aus der aktiven Wiki entfernt

# ---------------------------------------------------------------------------
# Reine Funktionen (stdlib) — ohne Netz testbar (uv run --no-project python -m unittest)
# ---------------------------------------------------------------------------

# Frontmatter-Block am Dateianfang: ---\n ... \n---\n
FM_RE = re.compile(r"^(---\s*\n)(.*?)(\n---\s*(?:\n|$))", re.DOTALL)


def iter_curated_pages(wiki_dir: Path):
    """Alle kuratierten .md-Seiten (concepts/entities/sources/syntheses), ohne .trash & RESERVED."""
    for top in CURATED:
        base = wiki_dir / top
        if not base.is_dir():
            continue
        for f in sorted(base.rglob("*.md")):
            if TRASH_DIRNAME in f.parts or f.name in RESERVED:
                continue
            yield f


def current_visibility(text: str) -> str | None:
    """visibility aus dem Frontmatter lesen. None = kein Frontmatter oder Feld fehlt."""
    m = FM_RE.match(text)
    if not m:
        return None
    vm = re.search(r"^visibility:\s*(.+)$", m.group(2), re.MULTILINE)
    if not vm:
        return None
    return vm.group(1).strip().strip('"').strip("'").lower()


def has_frontmatter(text: str) -> bool:
    return FM_RE.match(text) is not None


def _upsert_field(fm_body: str, key: str, value: str) -> str:
    """Setzt `key: value` im Frontmatter-Body — ersetzt vorhandene Zeile oder hängt an."""
    line = f"{key}: {value}"
    pattern = re.compile(rf"^{re.escape(key)}:.*$", re.MULTILINE)
    if pattern.search(fm_body):
        return pattern.sub(line, fm_body, count=1)
    return fm_body.rstrip("\n") + "\n" + line


def set_visibility(text: str, visibility: str, today: str) -> str | None:
    """Schreibt visibility (+ last_updated) ins Frontmatter. None, wenn kein Frontmatter da ist."""
    m = FM_RE.match(text)
    if not m:
        return None
    body = _upsert_field(m.group(2), "visibility", visibility)
    body = _upsert_field(body, "last_updated", today)
    return m.group(1) + body + m.group(3) + text[m.end():]


def is_private(visibility: str | None) -> bool:
    """True, wenn die Seite als privat gilt (→ aus aktiver Wiki entfernen)."""
    return normalize_visibility(visibility) == PRIVATE


def trash_destination(page: Path, wiki_dir: Path, trash_dir: Path) -> Path:
    """Ziel-Pfad in .trash unter Erhalt des relativen Pfads (kollisionssicher)."""
    rel = page.relative_to(wiki_dir)
    dest = trash_dir / rel
    if dest.exists():
        stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        dest = dest.with_name(f"{dest.stem}.{stamp}{dest.suffix}")
    return dest


def prepend_log(existing: str, entry: str) -> str:
    """Neuen Log-Eintrag oben einfügen (nach einer evtl. vorhandenen Top-Überschrift)."""
    entry = entry.rstrip() + "\n"
    if not existing.strip():
        return f"# Aktivitätslog\n\n> Append-only. Neueste Einträge oben.\n\n{entry}"
    lines = existing.splitlines(keepends=True)
    # Nach einer führenden "# ..."-Überschrift (+ Leerzeilen/Blockquote) einsetzen
    insert_at = 0
    if lines and lines[0].lstrip().startswith("# "):
        insert_at = 1
        while insert_at < len(lines) and (
            not lines[insert_at].strip() or lines[insert_at].lstrip().startswith(">")
        ):
            insert_at += 1
    return "".join(lines[:insert_at]) + entry + "\n" + "".join(lines[insert_at:])


# ---------------------------------------------------------------------------
# LLM-Klassifizierung (deferred imports — Modul bleibt ohne openai/pydantic importierbar)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """Du bist der Maintainer einer Knowledge Wiki und klassifizierst die \
SICHTBARKEIT (Wissensschicht) EINER einzelnen Seite anhand ihres Inhalts.

Sichtbarkeits-Leiter (offen → restriktiv):
- public:   extern teilbar, keine Einschränkung — allgemein bekanntes Fachwissen, öffentliche \
Paper/Artikel/Vorträge, publizierte Frameworks.
- customer: für Kunden / externe Software-User bestimmt — Produktdoku, Release-Infos, \
kundengerichtete Erklärungen.
- internal: für alle Firmenmitarbeiter — interne Strategie, interne Tools/Prozesse, \
nicht-öffentliche Markt- oder Wettbewerbseinschätzungen.
- team:     nur das jeweilige Team — teaminterne Projektdetails, Tickets, interne Diskussionen, \
Code-Interna.
- personal: NUR der Eigentümer — private Notizen, persönliche Gedanken/Meinungen, Tagebuch, \
private Kontakte/Termine, Gesundheitliches, Finanzielles, alles Vertrauliche/Private.

Regeln:
- "safe by default": im Zweifel die RESTRIKTIVERE Stufe wählen.
- `personal` ist ausschließlich für PRIVATE Inhalte — solche Seiten werden anschließend aus der \
aktiven Wiki entfernt. Stufe NUR dann als personal ein, wenn der Inhalt wirklich privat/persönlich \
ist; nicht bloß, weil eine Quelle fehlt oder das Thema speziell ist.
- Bewerte den INHALT der Seite, nicht das Fehlen von Metadaten.

Antworte strukturiert: visibility, confidence (high/medium/low), reason (genau 1 kurzer Satz, \
deutsch)."""


def _classification_schema():
    """Pydantic-Schema lazy bauen (Import erst hier, damit das Modul stdlib-importierbar bleibt)."""
    from typing import Literal

    from pydantic import BaseModel

    class Classification(BaseModel):
        visibility: Literal["public", "customer", "internal", "team", "personal"]
        confidence: Literal["high", "medium", "low"]
        reason: str

    return Classification


def build_client():
    """Azure-OpenAI-Client + Deployment-Name. Wirft KeyError, wenn Creds fehlen."""
    from openai import AzureOpenAI

    client = AzureOpenAI(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2025-04-01-preview"),
    )
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    return client, deployment


def classify_page(client, deployment: str, rel: str, content: str):
    """Klassifiziert eine Seite. Gibt (visibility, confidence, reason) zurück."""
    schema = _classification_schema()
    snippet = content[:12_000]
    user_message = f"# Seite: {rel}\n\n{snippet}"

    response = client.beta.chat.completions.parse(
        model=deployment,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_completion_tokens=300,
        response_format=schema,
    )
    parsed = response.choices[0].message.parsed
    if parsed is None:
        raise RuntimeError("LLM lieferte keine valide Klassifizierung (parsed=None)")
    return parsed.visibility, parsed.confidence, parsed.reason


# ---------------------------------------------------------------------------
# Hauptlauf
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Wiki-Wissen sortieren & visibility labeln; personal → .trash (Epic #28)")
    parser.add_argument("--wiki-dir", help="Wiki-Verzeichnis (Default: $VAULT_ROOT/wiki)")
    parser.add_argument("--apply", action="store_true",
                        help="Änderungen schreiben (sonst Dry-run/Plan)")
    parser.add_argument("--reclassify", action="store_true",
                        help="auch Seiten mit bereits gültigem visibility-Label neu einstufen")
    parser.add_argument("--limit", type=int, default=0,
                        help="nur die ersten N Seiten verarbeiten (0 = alle)")
    args = parser.parse_args()

    wiki_dir = Path(args.wiki_dir) if args.wiki_dir else VAULT_ROOT / "wiki"
    if not wiki_dir.is_dir():
        print(f"ERROR: Wiki-Verzeichnis nicht gefunden: {wiki_dir}", file=sys.stderr)
        return 2

    pages = list(iter_curated_pages(wiki_dir))
    if args.limit > 0:
        pages = pages[: args.limit]
    if not pages:
        print(f"Keine kuratierten Seiten in {wiki_dir} gefunden.")
        return 0

    # Client erst aufbauen, wenn klassifiziert werden muss — aber Creds früh prüfen.
    try:
        client, deployment = build_client()
    except KeyError as exc:
        print(f"ERROR: Azure-OpenAI-Zugang fehlt ({exc}). In .env setzen: "
              f"AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT.", file=sys.stderr)
        return 2

    today = datetime.now().strftime("%Y-%m-%d")
    trash_dir = wiki_dir / TRASH_DIRNAME

    plan: list[tuple[str, str, str, str, str]] = []  # (rel, action, visibility, prev, note)
    to_trash: list[tuple[Path, str, str]] = []       # (page, visibility, reason)
    to_label: list[tuple[Path, str]] = []            # (page, visibility)
    skipped = 0

    print(f"Wiki: {wiki_dir}  ({len(pages)} kuratierte Seiten)  "
          f"{'— APPLY' if args.apply else '— DRY-RUN'}\n")

    for page in pages:
        rel = page.relative_to(wiki_dir).as_posix()
        try:
            text = page.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            skipped += 1
            print(f"  ! SKIP {rel} — {type(exc).__name__}: {exc}", file=sys.stderr)
            continue

        prev = current_visibility(text)
        prev_valid = prev in VISIBILITY_LEVELS

        # Bestehende gültige Labels respektieren, außer --reclassify.
        if prev_valid and not args.reclassify:
            visibility, note = prev, "vorhandenes Label"
        else:
            try:
                visibility, confidence, reason = classify_page(client, deployment, rel, text)
                note = f"LLM/{confidence}: {reason}"
            except Exception as exc:  # graceful: eine Seite darf den Lauf nicht abbrechen
                skipped += 1
                print(f"  ! SKIP {rel} — Klassifizierung fehlgeschlagen: {exc}", file=sys.stderr)
                continue

        if is_private(visibility):
            plan.append((rel, "TRASH", "personal", prev or "—", note))
            to_trash.append((page, "personal", note))
        elif prev == visibility and prev_valid:
            plan.append((rel, "keep", visibility, prev or "—", note))
        else:
            plan.append((rel, "label", visibility, prev or "—", note))
            to_label.append((page, visibility))

    # --- Plan ausgeben ----------------------------------------------------
    width = max((len(r) for r, *_ in plan), default=10)
    for rel, action, visibility, prev, note in plan:
        mark = {"TRASH": "🗑", "label": "→", "keep": "·"}.get(action, " ")
        change = f"{prev} → {visibility}" if action != "keep" else visibility
        print(f"  {mark} {rel:<{width}}  {change:<22} {note}")

    print(f"\n## Plan")
    print(f"  Labels setzen/ändern : {len(to_label)}")
    print(f"  → .trash (personal)  : {len(to_trash)}")
    print(f"  unverändert          : {sum(1 for p in plan if p[1] == 'keep')}")
    print(f"  übersprungen         : {skipped}")

    if not args.apply:
        print("\n(Dry-run — mit --apply ausführen, um Labels zu schreiben und personal-Seiten "
              "nach .trash zu verschieben.)")
        return 0

    # --- Anwenden ---------------------------------------------------------
    labeled, trashed, label_warns = 0, 0, 0
    for page, visibility in to_label:
        rel = page.relative_to(wiki_dir).as_posix()
        try:
            text = page.read_text(encoding="utf-8")
            new_text = set_visibility(text, visibility, today)
            if new_text is None:
                label_warns += 1
                print(f"  ⚠ kein Frontmatter, Label nicht gesetzt: {rel}", file=sys.stderr)
                continue
            page.write_text(new_text, encoding="utf-8")
            labeled += 1
        except OSError as exc:
            label_warns += 1
            print(f"  ⚠ Label fehlgeschlagen: {rel} — {exc}", file=sys.stderr)

    trashed_rels: list[str] = []
    for page, _vis, _note in to_trash:
        rel = page.relative_to(wiki_dir).as_posix()
        try:
            dest = trash_destination(page, wiki_dir, trash_dir)
            dest.parent.mkdir(parents=True, exist_ok=True)
            page.rename(dest)
            trashed += 1
            trashed_rels.append(rel)
        except OSError as exc:
            print(f"  ⚠ Verschieben nach .trash fehlgeschlagen: {rel} — {exc}", file=sys.stderr)

    # --- log.md fortschreiben (Pflicht nach manueller Operation) ----------
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    trash_links = ", ".join(f"[[{Path(r).stem}]]" for r in trashed_rels) or "—"
    entry = (f"## {stamp} — REORGANISE\n"
             f"Klassifiziert: {len(plan)} Seiten (Azure OpenAI)\n"
             f"Labels gesetzt/geändert: {labeled}"
             f"{f' (+{label_warns} ohne Frontmatter übersprungen)' if label_warns else ''}\n"
             f"Nach .trash verschoben (personal): {trashed} — {trash_links}\n")
    log_path = wiki_dir / "log.md"
    try:
        existing = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
        log_path.write_text(prepend_log(existing, entry), encoding="utf-8")
    except OSError as exc:
        print(f"  ⚠ log.md nicht aktualisiert: {exc}", file=sys.stderr)

    print(f"\n✓ Angewendet: {labeled} gelabelt, {trashed} nach .trash verschoben.")
    if trashed:
        print(f"  Verschobene Seiten liegen in {trash_dir} (rückholbar).")
    print("  Empfehlung: 'uv run rebuild-index.py' und 'uv run lint-links.py' nachziehen "
          "(index/Backlinks aktualisieren, verwaiste Links zu .trash-Seiten finden).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
