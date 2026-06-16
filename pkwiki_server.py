"""pkwiki_server.py — Kernlogik des pkwiki-MCP-Servers (Epic #28, Folge-Ticket).

Reiner, testbarer Kern: lädt eine Agenten-Identität (AgentProfile aus vault-tree.yaml)
und stellt Lese-/Schreiboperationen über das Wiki bereit, die durch `access.py`
durchgesetzt werden:

    Lesen  : nur Seiten mit  rank(visibility) <= rank(clearance)  UND  node ∈ read_scope
    Schreiben: nur in den write_scope des Agenten (Node ODER 'session'-Sandbox)

Bewusst ohne `mcp`/`yaml`-Import — die werden im dünnen Entrypoint `pkwiki-mcp.py`
geladen. So laufen die Tests (test_mcp.py) ohne Netzwerk/externe Deps auf stdlib.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from access import (
    AgentProfile,
    Page,
    SESSION,
    can_read,
    can_write,
    filter_readable,
    load_agents,
    normalize_visibility,
)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
VISIBILITY_RE = re.compile(r"^visibility:\s*(.+)$", re.MULTILINE)
TITLE_RE = re.compile(r"^title:\s*(.+)$", re.MULTILINE)


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "note"


@dataclass(frozen=True)
class WikiPage:
    """Eine Wiki-Seite samt Node + Klassifizierung (für Retrieval + Reporting)."""
    node: str
    rel: str          # Pfad relativ zum wiki/-Root des Nodes (z.B. "concepts/foo.md")
    abs_path: Path
    visibility: str
    title: str

    @property
    def ref(self) -> str:
        """Stabile Referenz über Node-Grenzen: 'node:concepts/foo.md'."""
        return f"{self.node}:{self.rel}"

    def as_access_page(self) -> Page:
        return Page(node=self.node, visibility=self.visibility, ref=self.ref)


# ---------------------------------------------------------------------------
# Konfiguration / Baum
# ---------------------------------------------------------------------------

def node_wiki_dirs(vault_root: Path, tree: dict) -> dict[str, Path]:
    """node-name → dessen wiki/-Verzeichnis (mirror der wiki-sync.py-Konvention)."""
    out: dict[str, Path] = {}
    for n in tree.get("tree", []) or []:
        if isinstance(n, dict) and n.get("node") and n.get("path"):
            out[n["node"]] = vault_root / n["path"] / "wiki"
    return out


def node_default_visibility(tree: dict, node: str) -> str:
    """default_visibility eines Nodes (für neu erzeugte Seiten); Fallback restriktiv."""
    for n in tree.get("tree", []) or []:
        if isinstance(n, dict) and n.get("node") == node:
            rights = n.get("rights")
            if isinstance(rights, dict):
                return normalize_visibility(rights.get("default_visibility"))
    return normalize_visibility(None)   # personal


def get_agent(tree: dict, agent_id: str) -> AgentProfile:
    """AgentProfile aus dem Baum laden. Unbekannte id → fail closed (public/leerer Scope)."""
    agents = load_agents(tree)
    if agent_id in agents:
        return agents[agent_id]
    return AgentProfile(id=agent_id, clearance="public",
                        read_scope=frozenset(), write_scope=SESSION)


# ---------------------------------------------------------------------------
# Seiten einsammeln
# ---------------------------------------------------------------------------

def _parse_page(node: str, wiki_dir: Path, f: Path) -> WikiPage | None:
    try:
        text = f.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None   # graceful: unlesbare Seite überspringen
    fm = FRONTMATTER_RE.search(text)
    block = fm.group(1) if fm else ""
    vm = VISIBILITY_RE.search(block)
    tm = TITLE_RE.search(block)
    visibility = normalize_visibility(vm.group(1) if vm else None)
    title = (tm.group(1).strip().strip('"').strip("'") if tm else f.stem)
    return WikiPage(
        node=node,
        rel=f.relative_to(wiki_dir).as_posix(),
        abs_path=f,
        visibility=visibility,
        title=title,
    )


def collect_pages(vault_root: Path, tree: dict) -> list[WikiPage]:
    """Alle Wiki-Seiten über alle Nodes — unabhängig von Sichtbarkeit (Filter kommt später)."""
    pages: list[WikiPage] = []
    for node, wiki_dir in node_wiki_dirs(vault_root, tree).items():
        if not wiki_dir.exists():
            continue
        for f in sorted(wiki_dir.rglob("*.md")):
            page = _parse_page(node, wiki_dir, f)
            if page is not None:
                pages.append(page)
    return pages


def readable_pages(vault_root: Path, tree: dict, agent: AgentProfile) -> list[WikiPage]:
    """Nur die für den Agenten lesbaren Seiten (Gate via access.filter_readable)."""
    pages = collect_pages(vault_root, tree)
    allowed_refs = {p.ref for p in filter_readable([wp.as_access_page() for wp in pages], agent)}
    return [wp for wp in pages if wp.ref in allowed_refs]


# ---------------------------------------------------------------------------
# Lese-Operationen (durch access.py gegated)
# ---------------------------------------------------------------------------

def search(vault_root: Path, tree: dict, agent: AgentProfile, query: str,
           limit: int = 20) -> list[dict]:
    """Volltext-/Titel-Substring-Suche über die lesbaren Seiten."""
    q = query.lower().strip()
    hits: list[dict] = []
    for wp in readable_pages(vault_root, tree, agent):
        try:
            body = wp.abs_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if not q or q in wp.title.lower() or q in body.lower() or q in wp.rel.lower():
            hits.append({
                "ref": wp.ref,
                "title": wp.title,
                "node": wp.node,
                "visibility": wp.visibility,
                "snippet": _snippet(body),
            })
        if len(hits) >= limit:
            break
    return hits


def _snippet(text: str, length: int = 160) -> str:
    body = FRONTMATTER_RE.sub("", text, count=1).strip()
    body = re.sub(r"\s+", " ", body)
    return body[:length] + ("…" if len(body) > length else "")


def read_page(vault_root: Path, tree: dict, agent: AgentProfile, ref: str) -> dict:
    """Inhalt einer Seite — nur wenn der Agent sie lesen darf. Fail closed bei Unbekanntem."""
    for wp in collect_pages(vault_root, tree):
        if wp.ref == ref:
            if can_read(wp.as_access_page(), agent):
                try:
                    content = wp.abs_path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError) as exc:
                    return {"ok": False, "error": f"unlesbar: {exc}"}
                return {"ok": True, "ref": ref, "title": wp.title,
                        "visibility": wp.visibility, "content": content}
            return {"ok": False, "error": "kein Lesezugriff (visibility/scope)"}
    return {"ok": False, "error": f"Seite nicht gefunden: {ref}"}


def list_index(vault_root: Path, tree: dict, agent: AgentProfile) -> list[dict]:
    """Lesbare Seiten nach Node gruppiert (kompakter Index)."""
    out: list[dict] = []
    for wp in readable_pages(vault_root, tree, agent):
        out.append({"ref": wp.ref, "title": wp.title,
                    "node": wp.node, "visibility": wp.visibility})
    return out


# ---------------------------------------------------------------------------
# Schreib-Operationen (nur in write_scope; 'session' = ephemerer Sandbox)
# ---------------------------------------------------------------------------

def _write_target(vault_root: Path, tree: dict, agent: AgentProfile) -> tuple[str, Path, str]:
    """(node-label, wiki-dir, visibility) für Schreibvorgänge des Agenten."""
    if agent.write_scope == SESSION:
        # ephemerer, nicht-synchronisierter Sandbox-Node
        return SESSION, vault_root / ".sessions" / agent.id / "wiki", "personal"
    wiki_dir = node_wiki_dirs(vault_root, tree).get(agent.write_scope)
    if wiki_dir is None:
        # write_scope zeigt auf unbekannten Node → fail closed: in Session ausweichen
        return SESSION, vault_root / ".sessions" / agent.id / "wiki", "personal"
    return agent.write_scope, wiki_dir, node_default_visibility(tree, agent.write_scope)


def remember(vault_root: Path, tree: dict, agent: AgentProfile, text: str) -> dict:
    """Episodisches Gedächtnis: Eintrag an log.md im write_scope anhängen."""
    if not can_write(agent, agent.write_scope):
        return {"ok": False, "error": "kein Schreibzugriff"}
    label, wiki_dir, _ = _write_target(vault_root, tree, agent)
    wiki_dir.mkdir(parents=True, exist_ok=True)
    log = wiki_dir / "log.md"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    entry = f"\n## {ts} — AGENT {agent.id}\n{text.strip()}\n"
    with log.open("a", encoding="utf-8") as fh:
        fh.write(entry)
    return {"ok": True, "node": label, "path": str(log)}


def save_note(vault_root: Path, tree: dict, agent: AgentProfile,
              title: str, content: str) -> dict:
    """Semantisches Gedächtnis: Konzeptseite im write_scope anlegen/überschreiben.

    visibility = default_visibility des Ziel-Nodes (Session → personal).
    """
    if not can_write(agent, agent.write_scope):
        return {"ok": False, "error": "kein Schreibzugriff"}
    label, wiki_dir, visibility = _write_target(vault_root, tree, agent)
    concepts = wiki_dir / "concepts"
    concepts.mkdir(parents=True, exist_ok=True)
    slug = _slugify(title)
    path = concepts / f"{slug}.md"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    page = (
        f"---\ntitle: {title}\ntype: concept\nvisibility: {visibility}\n"
        f"last_updated: {today}\n---\n\n{content.strip()}\n"
    )
    path.write_text(page, encoding="utf-8")
    return {"ok": True, "node": label, "ref": f"{label}:concepts/{slug}.md",
            "visibility": visibility, "path": str(path)}
