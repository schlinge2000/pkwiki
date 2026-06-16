# /// script
# dependencies = ["pyyaml", "python-dotenv"]
# ///
"""
promote.py — Promotion-Planner für den Wissensbaum (Epic #28 / T4).

Promotion = eine Seite aus einem eigenen/engeren Node in einen **Vorfahr-Node** heben und
damit einem breiteren Publikum sichtbar machen (z.B. personal → team, team → company).

Bewusst **kein Auto-Mover**: Hochstufen verbreitert die Sichtbarkeit und ist daher ein
Review-pflichtiger Kurations-Schritt (T4-Gate). Dieses Tool *plant und validiert* die
Promotion (permissibel? Ziel-Sichtbarkeit?), führt sie aber nicht selbst aus — der
eigentliche Move + Review bleibt ein menschlicher Schritt.

Regeln (gegen vault-tree.yaml geprüft):
  - Ziel-Node muss ein Vorfahr der Quelle sein (nur nach oben).
  - Ziel-Sichtbarkeit = default_visibility des Ziel-Nodes; muss das Publikum verbreitern
    (rank(neu) <= rank(alt)), sonst ist es keine Promotion.

Usage:
    uv run promote.py --from personal-christian --to team-demand-ai --visibility personal
    uv run promote.py --from personal-christian --to company --visibility team --file vault-tree.yaml
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from access import VISIBILITY_LEVELS, normalize_visibility, rank

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


@dataclass(frozen=True)
class PromotionPlan:
    allowed: bool
    reason: str
    source_node: str = ""
    target_node: str = ""
    old_visibility: str = ""
    new_visibility: str = ""


def ancestors(name: str, parent_of: dict[str, str | None]) -> set[str]:
    seen: set[str] = set()
    cur = parent_of.get(name)
    while cur and cur not in seen:
        seen.add(cur)
        cur = parent_of.get(cur)
    return seen


def plan_promotion(source_node: str, source_visibility: str | None, target_node: str, *,
                   parent_of: dict[str, str | None],
                   rights_of: dict[str, dict]) -> PromotionPlan:
    """Validiert eine geplante Promotion. allowed=True heißt *permissibel* — Review bleibt nötig."""
    old_vis = normalize_visibility(source_visibility)

    if target_node == source_node:
        return PromotionPlan(False, "Ziel-Node ist die Quelle — keine Promotion")
    if source_node not in parent_of:
        return PromotionPlan(False, f"Quell-Node '{source_node}' existiert nicht im Baum")
    if target_node not in parent_of:
        return PromotionPlan(False, f"Ziel-Node '{target_node}' existiert nicht im Baum")
    if target_node not in ancestors(source_node, parent_of):
        return PromotionPlan(False, f"Ziel-Node '{target_node}' ist kein Vorfahr — "
                                    f"Promotion nur nach oben")

    tr = rights_of.get(target_node) or {}
    new_vis = tr.get("default_visibility")
    if new_vis not in VISIBILITY_LEVELS:
        return PromotionPlan(False, f"Ziel-Node '{target_node}' hat keine gültige "
                                    f"default_visibility")

    if rank(new_vis) > rank(old_vis):
        return PromotionPlan(False, f"verbreitert das Publikum nicht: Ziel '{new_vis}' "
                                    f"restriktiver als Quelle '{old_vis}'")

    return PromotionPlan(True, "permissibel — Review/Move erforderlich (T4-Gate)",
                         source_node, target_node, old_vis, new_vis)


def _load_tree(arg_file: str | None) -> dict:
    if arg_file:
        path = Path(arg_file)
    else:
        path = next((c for c in (VAULT_ROOT / "vault-tree.yaml", SCRIPT_ROOT / "vault-tree.yaml")
                     if c.is_file()), SCRIPT_ROOT / "vault-tree.yaml.example")
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML nicht installiert: uv add pyyaml", file=sys.stderr)
        sys.exit(2)
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Promotion-Planner für den Wissensbaum (T4)")
    parser.add_argument("--from", dest="src", required=True, help="Quell-Node")
    parser.add_argument("--to", dest="dst", required=True, help="Ziel-Node (muss Vorfahr sein)")
    parser.add_argument("--visibility", help="aktuelle visibility der Seite (Default: personal)")
    parser.add_argument("--file", help="vault-tree.yaml (Default: $VAULT_ROOT, dann Repo-Pfad)")
    args = parser.parse_args()

    data = _load_tree(args.file)
    nodes = data.get("tree", []) or []
    parent_of = {n["node"]: n.get("parent") for n in nodes if isinstance(n, dict) and n.get("node")}
    rights_of = {n["node"]: n.get("rights") or {} for n in nodes
                 if isinstance(n, dict) and n.get("node")}

    plan = plan_promotion(args.src, args.visibility, args.dst,
                          parent_of=parent_of, rights_of=rights_of)

    if plan.allowed:
        print(f"✓ Promotion permissibel: {plan.source_node} → {plan.target_node}")
        print(f"  visibility: {plan.old_visibility} → {plan.new_visibility}")
        print(f"  {plan.reason}")
        print("  Nächster Schritt (manuell, mit Review): Seite in den Ziel-Node verschieben,")
        print("  visibility-Frontmatter anpassen, Promotion in log.md vermerken.")
        return 0

    print(f"✗ Promotion abgelehnt: {plan.reason}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
