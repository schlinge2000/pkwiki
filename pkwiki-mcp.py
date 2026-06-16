# /// script
# dependencies = ["mcp", "pyyaml", "python-dotenv"]
# ///
"""pkwiki-mcp.py — MCP-Server, der das Wiki als Agenten-Gedächtnis bereitstellt.

Der Server *ist* die Sicht genau eines Agenten: er lädt dessen AgentProfile aus
vault-tree.yaml (via PKWIKI_AGENT_ID) und setzt Lese-/Schreibrechte über access.py
durch — kein Tool umgeht den Filter.

Tools:
    search_wiki(query)         — Volltext-/Titelsuche über lesbare Seiten
    read_page(ref)             — Seiteninhalt (nur wenn lesbar)
    list_index()               — lesbare Seiten nach Node
    remember(text)             — episodisch: an log.md im write_scope anhängen
    save_note(title, content)  — semantisch: Konzeptseite im write_scope anlegen

Start (stdio):
    PKWIKI_AGENT_ID=internal-demand-ai-copilot VAULT_ROOT=/pfad uv run pkwiki-mcp.py

Kernlogik + Tests: pkwiki_server.py / test_mcp.py (ohne mcp-Dependency lauffähig).
"""

from __future__ import annotations

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

import pkwiki_server as core

SCRIPT_ROOT = Path(__file__).parent
VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", str(SCRIPT_ROOT)))
AGENT_ID = os.environ.get("PKWIKI_AGENT_ID", "")


def _load_tree() -> dict:
    import yaml
    for cand in (VAULT_ROOT / "vault-tree.yaml", SCRIPT_ROOT / "vault-tree.yaml",
                 SCRIPT_ROOT / "vault-tree.yaml.example"):
        if cand.is_file():
            with cand.open(encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    return {}


def main() -> None:
    if not AGENT_ID:
        print("ERROR: PKWIKI_AGENT_ID nicht gesetzt — Server kennt keine Agenten-Identität.",
              file=sys.stderr)
        sys.exit(2)

    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        print("ERROR: 'mcp' nicht installiert — `uv run pkwiki-mcp.py` (inline deps) verwenden.",
              file=sys.stderr)
        sys.exit(2)

    tree = _load_tree()
    agent = core.get_agent(tree, AGENT_ID)

    mcp = FastMCP("pkwiki")

    @mcp.tool()
    def search_wiki(query: str, limit: int = 20) -> list[dict]:
        """Durchsucht das Wiki (Titel + Volltext) und liefert nur lesbare Treffer."""
        return core.search(VAULT_ROOT, tree, agent, query, limit)

    @mcp.tool()
    def read_page(ref: str) -> dict:
        """Liefert den Inhalt einer Seite (ref = 'node:pfad.md'), wenn lesbar."""
        return core.read_page(VAULT_ROOT, tree, agent, ref)

    @mcp.tool()
    def list_index() -> list[dict]:
        """Listet alle für diesen Agenten lesbaren Seiten (nach Node)."""
        return core.list_index(VAULT_ROOT, tree, agent)

    @mcp.tool()
    def remember(text: str) -> dict:
        """Hängt einen Eintrag an das log.md des write_scope (episodisches Gedächtnis)."""
        return core.remember(VAULT_ROOT, tree, agent, text)

    @mcp.tool()
    def save_note(title: str, content: str) -> dict:
        """Legt eine Konzeptseite im write_scope an (semantisches Gedächtnis)."""
        return core.save_note(VAULT_ROOT, tree, agent, title, content)

    mcp.run()


if __name__ == "__main__":
    main()
