"""test_reorganise.py — Tests für die reinen Funktionen von reorganise.py (Epic #28).

Nur stdlib — kein Netz/keine LLM-Calls (die Klassifizierung ist isoliert).
Lauf: uv run --no-project python -m unittest test_reorganise
"""

import tempfile
import unittest
from pathlib import Path

from reorganise import (
    content_fingerprint,
    current_visibility,
    has_frontmatter,
    is_private,
    iter_curated_pages,
    load_cache,
    prepend_log,
    save_cache,
    set_visibility,
    trash_destination,
)

FM_PAGE = """---
title: Demand Forecasting
type: concept
visibility: personal
last_updated: 2026-01-01
---

Inhalt.
"""

NO_VIS_PAGE = """---
title: Markttrends
type: concept
---

Inhalt.
"""

NO_FM_PAGE = "# Lose Notiz\n\nKein Frontmatter.\n"


class FrontmatterTests(unittest.TestCase):
    def test_reads_existing_visibility(self):
        self.assertEqual(current_visibility(FM_PAGE), "personal")

    def test_missing_visibility_field_is_none(self):
        self.assertIsNone(current_visibility(NO_VIS_PAGE))

    def test_no_frontmatter_is_none(self):
        self.assertIsNone(current_visibility(NO_FM_PAGE))
        self.assertFalse(has_frontmatter(NO_FM_PAGE))

    def test_set_visibility_replaces_existing(self):
        out = set_visibility(FM_PAGE, "internal", "2026-06-17")
        self.assertEqual(current_visibility(out), "internal")
        self.assertIn("last_updated: 2026-06-17", out)
        # body bleibt erhalten, kein doppeltes Feld
        self.assertEqual(out.count("visibility:"), 1)
        self.assertIn("Inhalt.", out)

    def test_set_visibility_adds_when_missing(self):
        out = set_visibility(NO_VIS_PAGE, "public", "2026-06-17")
        self.assertEqual(current_visibility(out), "public")
        self.assertIn("title: Markttrends", out)

    def test_set_visibility_none_without_frontmatter(self):
        self.assertIsNone(set_visibility(NO_FM_PAGE, "public", "2026-06-17"))


class PrivacyTests(unittest.TestCase):
    def test_personal_is_private(self):
        self.assertTrue(is_private("personal"))

    def test_missing_visibility_defaults_to_private(self):
        # fail closed: fehlend/ungültig → personal → privat
        self.assertTrue(is_private(None))
        self.assertTrue(is_private("bogus"))

    def test_non_personal_is_not_private(self):
        for v in ("public", "customer", "internal", "team"):
            self.assertFalse(is_private(v), v)


class TrashTests(unittest.TestCase):
    def test_preserves_relative_path(self):
        wiki = Path("/vault/wiki")
        page = wiki / "concepts" / "geheim.md"
        dest = trash_destination(page, wiki, wiki / ".trash")
        self.assertEqual(dest, wiki / ".trash" / "concepts" / "geheim.md")

    def test_collision_gets_timestamp_suffix(self):
        with tempfile.TemporaryDirectory() as d:
            wiki = Path(d)
            (wiki / "concepts").mkdir()
            page = wiki / "concepts" / "x.md"
            page.write_text("a", encoding="utf-8")
            trash = wiki / ".trash"
            (trash / "concepts").mkdir(parents=True)
            (trash / "concepts" / "x.md").write_text("alt", encoding="utf-8")
            dest = trash_destination(page, wiki, trash)
            self.assertNotEqual(dest.name, "x.md")
            self.assertTrue(dest.name.startswith("x.") and dest.suffix == ".md")


class ScopeTests(unittest.TestCase):
    def test_only_curated_dirs_no_reserved_no_trash(self):
        with tempfile.TemporaryDirectory() as d:
            wiki = Path(d)
            for rel in [
                "concepts/a.md", "entities/b.md", "sources/c.md", "syntheses/d.md",
                "concepts/index.md",                 # RESERVED → skip
                ".trash/concepts/old.md",            # trash → skip
                "code-wiki/demand-ai/modules/m.md",  # auto-bundle → skip
                "manuals/addone-bo/k.md",            # auto-bundle → skip
            ]:
                p = wiki / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("x", encoding="utf-8")
            found = {p.relative_to(wiki).as_posix() for p in iter_curated_pages(wiki)}
            self.assertEqual(found, {"concepts/a.md", "entities/b.md",
                                     "sources/c.md", "syntheses/d.md"})


class LogTests(unittest.TestCase):
    def test_prepend_keeps_heading_on_top(self):
        existing = "# Aktivitätslog\n\n> Append-only.\n\n## 2026-01-01 — INGEST\nalt\n"
        out = prepend_log(existing, "## 2026-06-17 — REORGANISE\nneu")
        self.assertTrue(out.startswith("# Aktivitätslog"))
        # neuer Eintrag steht vor dem alten
        self.assertLess(out.index("REORGANISE"), out.index("INGEST"))

    def test_prepend_into_empty_log(self):
        out = prepend_log("", "## 2026-06-17 — REORGANISE\nneu")
        self.assertIn("# Aktivitätslog", out)
        self.assertIn("REORGANISE", out)


class CacheTests(unittest.TestCase):
    def test_fingerprint_changes_with_content(self):
        self.assertEqual(content_fingerprint("abc"), content_fingerprint("abc"))
        self.assertNotEqual(content_fingerprint("abc"), content_fingerprint("abd"))

    def test_save_then_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / ".reorg-cache.json"
            cache = {"concepts/a.md": {"fingerprint": "x", "visibility": "internal",
                                       "confidence": "high", "reason": "ä → ü"}}
            save_cache(path, cache)
            self.assertEqual(load_cache(path), cache)

    def test_missing_cache_is_empty(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(load_cache(Path(d) / "nope.json"), {})

    def test_broken_cache_is_graceful(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "broken.json"
            path.write_text("{ not valid json", encoding="utf-8")
            self.assertEqual(load_cache(path), {})


if __name__ == "__main__":
    unittest.main()
