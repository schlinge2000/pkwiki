"""test_promote.py — Tests für den Promotion-Planner (Epic #28 / T4).

Lauf: uv run --no-project python -m unittest test_promote
"""

import unittest

from promote import plan_promotion

# Baum: company → team-x → personal-a
PARENT_OF = {"company": None, "team-x": "company", "personal-a": "team-x"}
RIGHTS_OF = {
    "company": {"clearance": "internal", "default_visibility": "internal"},
    "team-x": {"clearance": "team", "default_visibility": "team"},
    "personal-a": {"clearance": "personal", "default_visibility": "personal"},
}


def plan(src, vis, dst):
    return plan_promotion(src, vis, dst, parent_of=PARENT_OF, rights_of=RIGHTS_OF)


class PromotionTests(unittest.TestCase):
    def test_personal_to_team_is_allowed_and_broadens(self):
        p = plan("personal-a", "personal", "team-x")
        self.assertTrue(p.allowed)
        self.assertEqual((p.old_visibility, p.new_visibility), ("personal", "team"))

    def test_team_to_company_is_allowed(self):
        p = plan("team-x", "team", "company")
        self.assertTrue(p.allowed)
        self.assertEqual(p.new_visibility, "internal")

    def test_downward_is_blocked(self):
        # company → personal-a ist nicht "nach oben"
        self.assertFalse(plan("company", "internal", "personal-a").allowed)

    def test_lateral_or_nonancestor_is_blocked(self):
        bad_parents = {"company": None, "team-x": "company", "team-y": "company"}
        rights = {"team-y": {"clearance": "team", "default_visibility": "team"}, **RIGHTS_OF}
        p = plan_promotion("team-x", "team", "team-y", parent_of=bad_parents, rights_of=rights)
        self.assertFalse(p.allowed)

    def test_same_node_is_blocked(self):
        self.assertFalse(plan("team-x", "team", "team-x").allowed)

    def test_missing_source_node_is_blocked(self):
        self.assertFalse(plan("ghost", "personal", "company").allowed)

    def test_target_more_restrictive_is_not_a_promotion(self):
        # Quelle bereits internal; Ziel team (restriktiver) verbreitert das Publikum nicht
        rights = {**RIGHTS_OF, "team-x": {"clearance": "team", "default_visibility": "team"}}
        p = plan_promotion("personal-a", "internal", "team-x", parent_of=PARENT_OF, rights_of=rights)
        self.assertFalse(p.allowed)

    def test_unknown_source_visibility_defaults_restrictive(self):
        # fehlende visibility → personal; personal → team ist eine gültige Promotion
        p = plan("personal-a", None, "team-x")
        self.assertTrue(p.allowed)
        self.assertEqual(p.old_visibility, "personal")


if __name__ == "__main__":
    unittest.main()
