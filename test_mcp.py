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


def make_flat_vault() -> Path:
    """Flaches Vault: ein einziges <vault>/wiki, KEINE Pro-Node-Ordner (Realfall)."""
    root = Path(tempfile.mkdtemp())

    def page(rel, visibility, title, body="Inhalt."):
        p = root / "wiki" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            f"---\ntitle: {title}\ntype: concept\nvisibility: {visibility}\n---\n\n{body}\n",
            encoding="utf-8",
        )

    page("concepts/public.md", "public", "Public")
    page("concepts/internal.md", "internal", "Internal")
    page("concepts/team.md", "team", "Team")
    page("concepts/private.md", "personal", "Private")
    return root


# Wurzel-Node 'company' (parent-los), 'team-x' als Kind — Pfade existieren im flachen Vault nicht.
FLAT_TREE = {
    "tree": [
        {"node": "company", "path": "_company/",
         "rights": {"clearance": "internal", "default_visibility": "internal"}},
        {"node": "team-x", "path": "_team-x/", "parent": "company",
         "rights": {"clearance": "team", "default_visibility": "team"}},
    ]
}


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


class FlatVaultFallbackTests(unittest.TestCase):
    """Fallback: ein flaches <vault>/wiki wird dem Wurzel-Node zugeordnet."""

    def setUp(self):
        self.vault = make_flat_vault()

    def test_flat_wiki_maps_to_root_node(self):
        dirs = core.node_wiki_dirs(self.vault, FLAT_TREE)
        self.assertEqual(dirs, {"company": self.vault / "wiki"})

    def test_team_agent_sees_up_to_team_but_not_personal(self):
        a = agent("team", ["company"])
        refs = {h["ref"] for h in core.list_index(self.vault, FLAT_TREE, a)}
        self.assertEqual(refs, {"company:concepts/public.md",
                                "company:concepts/internal.md",
                                "company:concepts/team.md"})  # personal verborgen

    def test_customer_agent_sees_only_public(self):
        a = agent("customer", ["company"])
        refs = {h["ref"] for h in core.list_index(self.vault, FLAT_TREE, a)}
        self.assertEqual(refs, {"company:concepts/public.md"})

    def test_per_node_layout_still_wins_when_present(self):
        # Regression: existieren echte Pro-Node-Ordner, bleibt das alte Verhalten.
        multi = make_vault()
        dirs = core.node_wiki_dirs(multi, TREE)
        self.assertEqual(set(dirs), {"company", "team-x"})
        self.assertEqual(dirs["company"], multi / "_company" / "wiki")


class BundleVisibilityTests(unittest.TestCase):
    """Auto-generierte Bundles ohne visibility-Frontmatter erben eine Bundle-Sichtbarkeit."""

    def _vault(self) -> Path:
        root = Path(tempfile.mkdtemp())
        man = root / "wiki" / "manuals" / "addone-bo" / "kap.md"
        man.parent.mkdir(parents=True, exist_ok=True)
        man.write_text("---\ntitle: Kapitel\ntype: manual-chapter\n---\n\nAnleitung.\n",
                       encoding="utf-8")
        code = root / "wiki" / "code-wiki" / "demand-ai" / "mod.md"
        code.parent.mkdir(parents=True, exist_ok=True)
        code.write_text("---\ntitle: Modul\ntype: code-module\n---\n\nArchitektur.\n",
                        encoding="utf-8")
        return root

    def test_manuals_visible_to_customer_but_codewiki_hidden(self):
        v = self._vault()
        a = agent("customer", ["company"])
        refs = {h["ref"] for h in core.list_index(v, FLAT_TREE, a)}
        self.assertIn("company:manuals/addone-bo/kap.md", refs)        # → customer geerbt
        self.assertNotIn("company:code-wiki/demand-ai/mod.md", refs)   # kein Default → personal

    def test_explicit_label_overrides_bundle_default(self):
        v = self._vault()
        (v / "wiki" / "manuals" / "addone-bo" / "kap.md").write_text(
            "---\ntitle: Kapitel\nvisibility: internal\n---\n\nx\n", encoding="utf-8")
        a = agent("customer", ["company"])
        refs = {h["ref"] for h in core.list_index(v, FLAT_TREE, a)}
        self.assertNotIn("company:manuals/addone-bo/kap.md", refs)     # internal > customer

    def test_tree_override_changes_bundle_visibility(self):
        v = self._vault()
        tree = {**FLAT_TREE, "bundle_visibility": {"manuals": "internal"}}
        cust = {h["ref"] for h in core.list_index(v, tree, agent("customer", ["company"]))}
        self.assertNotIn("company:manuals/addone-bo/kap.md", cust)     # jetzt internal
        intr = {h["ref"] for h in core.list_index(v, tree, agent("internal", ["company"]))}
        self.assertIn("company:manuals/addone-bo/kap.md", intr)


PERSONAL_TREE = {
    "tree": [
        {"node": "company", "path": "_company/",
         "rights": {"clearance": "internal", "default_visibility": "internal"}},
        {"node": "pers", "path": "_pers/", "parent": "company",
         "rights": {"clearance": "personal", "default_visibility": "personal"}},
    ]
}


class PersonalMemoryTests(unittest.TestCase):
    """Persönlicher Agent (clearance=personal) schreibt in seinen Node UND liest zurück,
    während die geteilte flache Wiki (company) weiter sichtbar bleibt."""

    def setUp(self):
        self.vault = make_flat_vault()   # flaches <vault>/wiki = company-Node

    def test_writes_to_personal_node_not_session(self):
        a = agent("personal", ["pers", "company"], write="pers")
        res = core.save_note(self.vault, PERSONAL_TREE, a, "Mein Merksatz", "Inhalt")
        self.assertTrue(res["ok"])
        self.assertEqual(res["node"], "pers")
        self.assertEqual(res["visibility"], "personal")
        self.assertNotIn(".sessions", res["path"])
        self.assertTrue((self.vault / "_pers" / "wiki" / "concepts").exists())

    def test_personal_agent_reads_its_note_back_and_shared_wiki(self):
        a = agent("personal", ["pers", "company"], write="pers")
        core.save_note(self.vault, PERSONAL_TREE, a, "Mein Merksatz", "Inhalt")
        refs = {h["ref"] for h in core.list_index(self.vault, PERSONAL_TREE, a)}
        self.assertIn("pers:concepts/mein-merksatz.md", refs)   # eigenes zurücklesbar
        self.assertIn("company:concepts/public.md", refs)       # geteilte Wiki weiter da

    def test_team_agent_cannot_see_personal_note(self):
        pa = agent("personal", ["pers", "company"], write="pers")
        core.save_note(self.vault, PERSONAL_TREE, pa, "Geheim", "privat")
        ta = agent("team", ["company"])   # pers nicht im scope, clearance < personal
        refs = {h["ref"] for h in core.list_index(self.vault, PERSONAL_TREE, ta)}
        self.assertNotIn("pers:concepts/geheim.md", refs)


if __name__ == "__main__":
    unittest.main()
