"""access.py — Wiederverwendbarer Retrieval-Filter für Wissensschichten (Epic #28 / T3).

Single source of truth für die visibility-Leiter (importiert von lint-links.py & lint-tree.py)
und Durchsetzung des Sichtbarkeitsmodells *vor* der Kontextbefüllung:

    Eine Seite ist für einen Agenten lesbar  ⇔
        rank(visibility) <= rank(clearance)   UND   node(seite) ∈ read_scope

Wichtig (OKF / safe by default): unbekannte/fehlende Werte **fail closed**:
  - fehlende/ungültige Seiten-`visibility`  → restriktivste Stufe (`personal`)  → eher verbergen
  - fehlende/ungültige Agenten-`clearance`   → niedrigste Stufe (`public`)        → weniger Zugriff

Reine Standardbibliothek — ohne Abhängigkeiten importierbar und testbar.
"""

from __future__ import annotations

from dataclasses import dataclass

# Sichtbarkeits-Schichten, von offen (Index 0) nach restriktiv (Index -1).
VISIBILITY_LEVELS = ["public", "customer", "internal", "team", "personal"]

DEFAULT_VISIBILITY = VISIBILITY_LEVELS[-1]   # fehlende Seiten-visibility → restriktivste Stufe
LEAST_CLEARANCE = VISIBILITY_LEVELS[0]       # fehlende Agenten-clearance → geringster Zugriff
SESSION = "session"                          # ephemerer Sandbox-Node (kein Persist im Baum)


def rank(level: str) -> int:
    """Sensitivitäts-Rang einer visibility-Stufe (höher = restriktiver)."""
    return VISIBILITY_LEVELS.index(level)


def _clean(value: str) -> str:
    return value.strip().strip('"').strip("'").lower()


def normalize_visibility(value: str | None) -> str:
    """Seiten-visibility normalisieren. Unbekannt/fehlend → restriktivster Default (verbergen)."""
    if value is None:
        return DEFAULT_VISIBILITY
    v = _clean(value)
    return v if v in VISIBILITY_LEVELS else DEFAULT_VISIBILITY


def normalize_clearance(value: str | None) -> str:
    """Agenten-clearance normalisieren. Unbekannt/fehlend → geringster Zugriff (fail closed)."""
    if value is None:
        return LEAST_CLEARANCE
    v = _clean(value)
    return v if v in VISIBILITY_LEVELS else LEAST_CLEARANCE


@dataclass(frozen=True)
class AgentProfile:
    """Capability eines Agenten (T2): clearance + read/write-Scope."""
    id: str
    clearance: str
    read_scope: frozenset[str]
    write_scope: str = SESSION

    @property
    def clearance_rank(self) -> int:
        return rank(self.clearance)


@dataclass(frozen=True)
class Page:
    """Minimal-Sicht auf eine Wiki-Seite für die Zugriffsprüfung."""
    node: str
    visibility: str
    ref: str = ""    # optional: Pfad/ID für Reporting


def can_read(page: Page, agent: AgentProfile) -> bool:
    """True, wenn der Agent die Seite lesen darf. Fail closed bei unbekannten Werten."""
    if page.node not in agent.read_scope:
        return False
    return rank(normalize_visibility(page.visibility)) <= rank(normalize_clearance(agent.clearance))


def filter_readable(pages, agent: AgentProfile) -> list[Page]:
    """Filtert eine Seiten-Sequenz auf die für den Agenten lesbaren Seiten (Retrieval-Gate)."""
    return [p for p in pages if can_read(p, agent)]


def can_write(agent: AgentProfile, node: str) -> bool:
    """True, wenn der Agent in `node` schreiben darf (nur in den eigenen write_scope)."""
    return node == agent.write_scope


def load_agents(tree_data: dict) -> dict[str, AgentProfile]:
    """Baut AgentProfile-Objekte aus einem geparsten vault-tree.yaml (Schlüssel: agent-id)."""
    out: dict[str, AgentProfile] = {}
    for a in tree_data.get("agents", []) or []:
        if not isinstance(a, dict) or not a.get("id"):
            continue
        out[a["id"]] = AgentProfile(
            id=a["id"],
            clearance=normalize_clearance(a.get("clearance")),
            read_scope=frozenset(a.get("read_scope", []) or []),
            write_scope=a.get("write_scope", SESSION),
        )
    return out
