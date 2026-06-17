"""test_access.py — Tests für den Retrieval-Filter (Epic #28 / T3).

Schwerpunkt: kein Leakage höher klassifizierter Seiten an niedrigeres Clearance.
Lauf: uv run --no-project python -m unittest test_access   (oder: python3 -m unittest test_access)
"""

import unittest

from access import (
    AgentProfile,
    Page,
    can_read,
    can_write,
    filter_readable,
    load_agents,
    normalize_clearance,
    normalize_visibility,
)


def agent(clearance="internal", read=("company",), write="session"):
    return AgentProfile(id="t", clearance=clearance, read_scope=frozenset(read), write_scope=write)


class NormalizeTests(unittest.TestCase):
    def test_missing_visibility_is_most_restrictive(self):
        self.assertEqual(normalize_visibility(None), "personal")

    def test_unknown_visibility_fails_closed_restrictive(self):
        self.assertEqual(normalize_visibility("secret"), "personal")

    def test_missing_clearance_is_least_access(self):
        self.assertEqual(normalize_clearance(None), "public")

    def test_unknown_clearance_fails_closed_least(self):
        self.assertEqual(normalize_clearance("topsecret"), "public")

    def test_values_are_case_and_quote_insensitive(self):
        self.assertEqual(normalize_visibility('"Internal" '), "internal")


class CanReadTests(unittest.TestCase):
    def test_reads_equal_and_lower_sensitivity(self):
        a = agent(clearance="internal")
        self.assertTrue(can_read(Page("company", "internal"), a))
        self.assertTrue(can_read(Page("company", "public"), a))

    def test_denies_higher_sensitivity(self):
        a = agent(clearance="internal")
        self.assertFalse(can_read(Page("company", "team"), a))
        self.assertFalse(can_read(Page("company", "personal"), a))

    def test_denies_node_outside_read_scope(self):
        # Sichtbarkeit ok, aber Node nicht im Scope → kein Zugriff (keine seitlichen Leaks)
        a = agent(clearance="personal", read=("company",))
        self.assertFalse(can_read(Page("team-other", "public"), a))

    def test_unknown_page_visibility_is_hidden_unless_top_clearance(self):
        page = Page("company", "bogus")           # → personal
        self.assertFalse(can_read(page, agent(clearance="internal")))
        self.assertTrue(can_read(page, agent(clearance="personal")))

    def test_unknown_clearance_only_sees_public(self):
        a = agent(clearance="bogus")              # → public
        self.assertTrue(can_read(Page("company", "public"), a))
        self.assertFalse(can_read(Page("company", "customer"), a))


class FilterTests(unittest.TestCase):
    def test_filter_excludes_leaks(self):
        a = agent(clearance="customer", read=("company",))
        pages = [
            Page("company", "public", "p1"),
            Page("company", "customer", "p2"),
            Page("company", "internal", "p3"),   # zu sensibel
            Page("team-x", "public", "p4"),       # falscher Node
        ]
        refs = {p.ref for p in filter_readable(pages, a)}
        self.assertEqual(refs, {"p1", "p2"})


class WriteTests(unittest.TestCase):
    def test_write_only_to_own_scope(self):
        a = agent(write="session")
        self.assertTrue(can_write(a, "session"))
        self.assertFalse(can_write(a, "company"))


class LoadAgentsTests(unittest.TestCase):
    def test_loads_profiles_and_fails_closed_on_bad_clearance(self):
        data = {"agents": [
            {"id": "prod", "clearance": "customer", "read_scope": ["company"], "write_scope": "session"},
            {"id": "broken", "clearance": "nope", "read_scope": ["company"]},
            {"description": "no id"},
        ]}
        agents = load_agents(data)
        self.assertEqual(set(agents), {"prod", "broken"})
        self.assertEqual(agents["broken"].clearance, "public")   # fail closed
        self.assertEqual(agents["prod"].write_scope, "session")


if __name__ == "__main__":
    unittest.main()
