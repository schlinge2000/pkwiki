# /// script
# dependencies = ["pyyaml", "python-dotenv"]
# ///
"""
lint-tree.py — Konsistenz-Check für die Node-Rechte in vault-tree.yaml (Epic #28 / T5).

Validiert pro Node das `rights`-Block gegen die Baum-Hierarchie:
  - clearance / default_visibility sind gültige visibility-Stufen
  - default_visibility <= clearance      (man kann nichts erzeugen, was man nicht lesen darf)
  - read  ⊆ {self} ∪ Vorfahren           (nur nach oben lesen — keine seitlichen Leaks)
  - write ⊆ {self} ∪ Nachfahren          (nach oben schreiben = Promotion/T4, kein Default-Recht)
  - parent / read / write referenzieren existierende Nodes
  - clearance nimmt nach unten nicht ab   (sonst kann ein Kind den Eltern-Layer nicht lesen) [WARN]

Graceful: ein fehlerhafter Node bricht den Lauf nie ab (OKF-Prinzip „tolerate, don't reject").

Usage:
    uv run lint-tree.py                  # $VAULT_ROOT/vault-tree.yaml (Fallback: Repo-Pfad)
    uv run lint-tree.py --file PATH
    uv run lint-tree.py --strict         # Exit 1 bei ERROR-Befunden
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    _vault = os.environ.get("VAULT_ROOT")
    if _vault:
        load_dotenv(Path(_vault) / ".env", override=False)
    load_dotenv(Path(__file__).parent / ".env", override=False)
except ImportError:
    pass

SCRIPT_ROOT = Path(__file__).parent
VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", str(SCRIPT_ROOT)))

# Sichtbarkeits-Schichten, von offen (Index 0) nach restriktiv. Muss zu lint-links.py passen.
VISIBILITY_LEVELS = ["public", "customer", "internal", "team", "personal"]


def rank(level: str) -> int:
    """Sensitivitäts-Rang einer visibility-Stufe (höher = restriktiver)."""
    return VISIBILITY_LEVELS.index(level)


def load_tree(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML nicht installiert: uv add pyyaml", file=sys.stderr)
        sys.exit(2)
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def resolve_config(arg_file: str | None) -> Path:
    if arg_file:
        return Path(arg_file)
    for cand in (VAULT_ROOT / "vault-tree.yaml", SCRIPT_ROOT / "vault-tree.yaml"):
        if cand.is_file():
            return cand
    # Letzter Fallback: Beispiel (damit der Check ohne Setup demonstrierbar ist)
    return SCRIPT_ROOT / "vault-tree.yaml.example"


def ancestors(name: str, parent_of: dict[str, str | None]) -> set[str]:
    """Alle Vorfahren von `name` (parent, grandparent, ...)."""
    seen: set[str] = set()
    cur = parent_of.get(name)
    while cur and cur not in seen:
        seen.add(cur)
        cur = parent_of.get(cur)
    return seen


def main() -> int:
    parser = argparse.ArgumentParser(description="Konsistenz-Check für Node-Rechte in vault-tree.yaml")
    parser.add_argument("--file", help="vault-tree.yaml (Default: $VAULT_ROOT, dann Repo-Pfad)")
    parser.add_argument("--strict", action="store_true", help="Exit 1 bei ERROR-Befunden")
    args = parser.parse_args()

    config = resolve_config(args.file)
    if not config.is_file():
        print(f"ERROR: vault-tree.yaml nicht gefunden: {config}", file=sys.stderr)
        return 2

    data = load_tree(config)
    nodes = data.get("tree", []) or []
    names = {n.get("node") for n in nodes if isinstance(n, dict) and n.get("node")}
    parent_of = {n["node"]: n.get("parent") for n in nodes if isinstance(n, dict) and n.get("node")}

    errors: list[str] = []
    warns: list[str] = []

    for n in nodes:
        # Graceful: kaputten Node-Eintrag überspringen
        if not isinstance(n, dict) or not n.get("node"):
            warns.append(f"Node-Eintrag ohne 'node'-Feld übersprungen: {n!r}")
            continue
        name = n["node"]

        parent = n.get("parent")
        if parent and parent not in names:
            errors.append(f"{name}: parent '{parent}' existiert nicht im Baum")

        rights = n.get("rights")
        if not isinstance(rights, dict):
            warns.append(f"{name}: kein 'rights'-Block — erbt nichts, nicht prüfbar")
            continue

        clearance = rights.get("clearance")
        default_vis = rights.get("default_visibility")

        if clearance not in VISIBILITY_LEVELS:
            errors.append(f"{name}: ungültige clearance '{clearance}' "
                          f"(erlaubt: {', '.join(VISIBILITY_LEVELS)})")
        if default_vis not in VISIBILITY_LEVELS:
            errors.append(f"{name}: ungültige default_visibility '{default_vis}' "
                          f"(erlaubt: {', '.join(VISIBILITY_LEVELS)})")

        if clearance in VISIBILITY_LEVELS and default_vis in VISIBILITY_LEVELS:
            if rank(default_vis) > rank(clearance):
                errors.append(f"{name}: default_visibility '{default_vis}' restriktiver als "
                              f"clearance '{clearance}' — erzeugt unlesbare eigene Seiten")

        anc = ancestors(name, parent_of)
        allowed_read = {name} | anc
        for r in rights.get("read", []) or []:
            if r not in names:
                errors.append(f"{name}: read-Ziel '{r}' existiert nicht im Baum")
            elif r not in allowed_read:
                errors.append(f"{name}: read-Ziel '{r}' ist weder self noch Vorfahr "
                              f"(seitlicher Zugriff verboten)")

        descendants = {m for m in names if name in ancestors(m, parent_of)}
        allowed_write = {name} | descendants
        for w in rights.get("write", []) or []:
            if w not in names:
                errors.append(f"{name}: write-Ziel '{w}' existiert nicht im Baum")
            elif w not in allowed_write:
                errors.append(f"{name}: write-Ziel '{w}' ist weder self noch Nachfahr "
                              f"(Hochstufen = Promotion/T4, kein Default-Recht)")

        # WARN: clearance darf nach unten nicht abnehmen, sonst Eltern-Layer unlesbar
        if parent and parent in names and clearance in VISIBILITY_LEVELS:
            p_rights = next((x.get("rights") for x in nodes
                             if isinstance(x, dict) and x.get("node") == parent), None)
            if isinstance(p_rights, dict) and p_rights.get("clearance") in VISIBILITY_LEVELS:
                if rank(clearance) < rank(p_rights["clearance"]):
                    warns.append(f"{name}: clearance '{clearance}' niedriger als Eltern "
                                 f"'{parent}' ({p_rights['clearance']}) — kann Eltern-Layer nicht lesen")

    # --- Agenten-Capability-Profile (T2) ----------------------------------
    rights_of = {n["node"]: n.get("rights") for n in nodes
                 if isinstance(n, dict) and n.get("node")}
    agents = data.get("agents", []) or []

    for a in agents:
        if not isinstance(a, dict) or not a.get("id"):
            warns.append(f"Agent-Eintrag ohne 'id' übersprungen: {a!r}")
            continue
        aid = a["id"]
        clearance = a.get("clearance")

        if clearance not in VISIBILITY_LEVELS:
            errors.append(f"agent {aid}: ungültige clearance '{clearance}' "
                          f"(erlaubt: {', '.join(VISIBILITY_LEVELS)})")

        for r in a.get("read_scope", []) or []:
            if r not in names:
                errors.append(f"agent {aid}: read_scope-Node '{r}' existiert nicht im Baum")

        ws = a.get("write_scope")
        if ws != "session" and ws not in names:
            errors.append(f"agent {aid}: write_scope '{ws}' ist weder 'session' noch ein Node im Baum")

        # Low-Trust-Agent (sieht nur bis customer) sollte ephemer schreiben, nicht persistent
        if clearance in VISIBILITY_LEVELS and rank(clearance) <= rank("customer") \
                and ws in names:
            warns.append(f"agent {aid}: niedrige clearance '{clearance}' schreibt in persistenten "
                         f"Node '{ws}' — Sandbox/'session' empfohlen (T4)")

        # Agent darf nicht in einen Node schreiben, dessen Seiten er nicht lesen könnte
        if ws in names and clearance in VISIBILITY_LEVELS:
            wr = rights_of.get(ws)
            if isinstance(wr, dict) and wr.get("default_visibility") in VISIBILITY_LEVELS \
                    and rank(wr["default_visibility"]) > rank(clearance):
                errors.append(f"agent {aid}: write_scope '{ws}' erzeugt Seiten (default_visibility "
                              f"'{wr['default_visibility']}') über clearance '{clearance}' — unlesbar")

    # --- Report -----------------------------------------------------------
    print(f"vault-tree: {config}  ({len(nodes)} Nodes, {len(agents)} Agenten)\n")

    print(f"## ERROR ({len(errors)})")
    for e in errors:
        print(f"  ✗ {e}")
    if not errors:
        print("  (keine)")

    print(f"\n## WARN ({len(warns)})")
    for w in warns:
        print(f"  ⚠ {w}")
    if not warns:
        print("  (keine)")

    return 1 if (args.strict and errors) else 0


if __name__ == "__main__":
    sys.exit(main())
