"""test_mcp.py — Tests für die pkwiki-MCP-Kernlogik (pkwiki_server.py).

Schwerpunkt: der Server leakt nichts über die Agenten-clearance/read_scope hinaus
und schreibt nur in den write_scope. Lauf:
    python3 -m unittest test_mcp     (kein mcp/yaml nötig)
"""

import tempfile
import unittest
from pathlib import Path

import pkwiki_server as core
from access import AgentProfile, SESSION


def make_vault() -> Path:
    """Temporäres Vault mit zwei Nodes (company, team-x) und gemischter visibility."""
    root = Path(tempfile.mkdtemp())

    def page(node_path, rel, visibility, title, body="Inhalt."):
        p = root / node_path / "wiki" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            f"---\ntitle: {title}\ntype: concept\nvisibility: {visibility}\n---\n\n{body}\n",
            encoding="utf-8",
        )

    page("_company", "concepts/public-thing.md", "public", "Public Thing")
    page("_company", "concepts/internal-thing.md", "internal", "Internal Thing")
    page("_team-x", "concepts/team-secret.md", "team", "Team Secret")
    return root


TREE = {
    "tree": [
        {"node": "company", "path": "_company/",
         "rights": {"clearance": "internal", "default_visibility": "internal"}},
        {"node": "team-x", "path": "_team-x/",
         "rights": {"clearance": "team", "default_visibility": "team"}},
    ]
}


def agent(clearance, read, write=SESSION):
    return AgentProfile(id="a", clearance=clearance,
                        read_scope=frozenset(read), write_scope=write)


class ReadGatingTests(unittest.TestCase):
    def setUp(self):
        self.vault = make_vault()

    def test_customer_agent_sees_only_public_in_company(self):
        a = agent("customer", ["company"])
        refs = {h["ref"] for h in core.list_index(self.vault, TREE, a)}
        self.assertEqual(refs, {"company:concepts/public-thing.md"})

    def test_internal_agent_sees_public_and_internal(self):
        a = agent("internal", ["company"])
        refs = {h["ref"] for h in core.list_index(self.vault, TREE, a)}
        self.assertEqual(refs, {"company:concepts/public-thing.md",
                                "company:concepts/internal-thing.md"})

    def test_node_outside_read_scope_is_invisible(self):
        # clearance reicht für team, aber team-x ist nicht im read_scope
        a = agent("team", ["company"])
        refs = {h["ref"] for h in core.list_index(self.vault, TREE, a)}
        self.assertNotIn("team-x:concepts/team-secret.md", refs)

    def test_read_page_denies_too_sensitive(self):
        a = agent("internal", ["company"])
        res = core.read_page(self.vault, TREE, a, "company:concepts/internal-thing.md")
        self.assertTrue(res["ok"])
        # team-secret nicht im scope → verweigert
        a2 = agent("internal", ["company"])
        res2 = core.read_page(self.vault, TREE, a2, "team-x:concepts/team-secret.md")
        self.assertFalse(res2["ok"])

    def test_search_only_returns_readable(self):
        a = agent("customer", ["company"])
        hits = core.search(self.vault, TREE, a, "thing")
        refs = {h["ref"] for h in hits}
        self.assertEqual(refs, {"company:concepts/public-thing.md"})


class WriteTests(unittest.TestCase):
    def setUp(self):
        self.vault = make_vault()

    def test_session_write_goes_to_ephemeral_sandbox(self):
        a = agent("customer", ["company"], write=SESSION)
        res = core.save_note(self.vault, TREE, a, "My Note", "body")
        self.assertTrue(res["ok"])
        self.assertEqual(res["node"], SESSION)
        self.assertEqual(res["visibility"], "personal")   # session → restriktiv
        self.assertTrue((self.vault / ".sessions" / "a" / "wiki").exists())

    def test_persistent_write_uses_node_default_visibility(self):
        a = agent("team", ["team-x", "company"], write="team-x")
        res = core.save_note(self.vault, TREE, a, "Team Note", "body")
        self.assertTrue(res["ok"])
        self.assertEqual(res["node"], "team-x")
        self.assertEqual(res["visibility"], "team")

    def test_remember_appends_log(self):
        a = agent("team", ["team-x"], write="team-x")
        core.remember(self.vault, TREE, a, "etwas passiert")
        log = self.vault / "_team-x" / "wiki" / "log.md"
        self.assertIn("etwas passiert", log.read_text(encoding="utf-8"))

    def test_unknown_write_scope_falls_back_to_session(self):
        a = agent("internal", ["company"], write="ghost-node")
        res = core.save_note(self.vault, TREE, a, "X", "y")
        self.assertEqual(res["node"], SESSION)


if __name__ == "__main__":
    unittest.main()
