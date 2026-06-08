# schemas.py — shared across code-extract.py, code-ingest.py, code-watch.py
"""
Shared Pydantic schemas for Knowledge Tree — Code-Wiki.
Importable without external deps for type checking (pydantic is the only dependency).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class RepoConfig(BaseModel):
    name: str                                          # human name, e.g. "demand-ai"
    owner: str                                         # GitHub owner, e.g. "inform-group"
    repo: str                                          # GitHub repo name, e.g. "demand-ai"
    branch: str = "main"
    language: str = ""                                 # e.g. "python" or "python,typescript"
    ticket_pattern: str = r'[A-Z]+-\d+|#\d+'          # regex for ticket refs
    privacy: Literal["internal", "personal", "public"] = "internal"
    code_wiki_path: str = ""                           # relative to vault root, auto-derived if empty


class ManualConfig(BaseModel):
    """Optionaler Override für ein einzelnes Manual.

    Ohne Eintrag wird der Slug automatisch aus dem Dateinamen abgeleitet und
    `ManualsWatchConfig.default_max_level` verwendet. Diese Klasse erlaubt
    abweichende Slugs (z.B. `addone-bo-admin` statt `administratorhandbuch-...`)
    oder File-spezifisches `max_level` / `skip_images`.
    """
    file: str                           # exakter Dateiname in watch_dir
    product: str                        # gewünschter Produkt-Slug
    max_level: int = 2                  # TOC-Tiefe
    skip_images: bool = False


class ManualsWatchConfig(BaseModel):
    watch_dir: str = "raw/manuals"      # relativ zu VAULT_ROOT
    default_max_level: int = 2          # für alle nicht-overrideten PDFs
    skip_images: bool = False
    products: list[ManualConfig] = []   # Overrides — alle PDFs im watch_dir werden
                                        # automatisch erfasst, auch wenn nicht gelistet


class WatchConfig(BaseModel):
    github_token: str
    repos: list[RepoConfig]
    poll_interval_minutes: int = 15
    last_poll_state_file: str = ".code-watch-state.json"
    manuals: ManualsWatchConfig | None = None


class TicketRef(BaseModel):
    id: str                                            # e.g. "DAI-123", "#42"
    source: str                                        # "commit_message" | "branch_name" | "pr_title"
    confidence: float = 1.0


class FileChange(BaseModel):
    path: str
    change_type: Literal["added", "modified", "deleted", "renamed"]
    module: str                                        # LLM-inferred module/domain this file belongs to


class CommitDigest(BaseModel):
    sha: str
    author: str
    timestamp: str                                     # ISO 8601
    original_message: str
    semantic_summary: str                              # LLM: what was done semantically (1-3 sentences)
    ticket_refs: list[TicketRef]
    impact_areas: list[str]                            # affected modules/domains
    files_changed: list[FileChange]
    complexity: Literal["small", "medium", "large", "refactor"]
    shared_concept: str | None                         # generalizable pattern? None if not
    repo_name: str                                     # which repo this came from
    repo_owner: str


class PMUpdate(BaseModel):
    ticket_id: str | None = None                       # primary ticket if any
    repo_name: str
    one_liner: str                                     # for pm-overview.md: "DAI-123: Added retry logic to forecasting engine"


class CodeWikiPage(BaseModel):
    path: str                                          # relativ zu code-wiki/<projekt>/
    action: Literal["create", "update"]
    content: str


class CodeIngestResponse(BaseModel):
    code_pages: list[CodeWikiPage]                     # → code-wiki/<projekt>/
    wiki_concepts: list[CodeWikiPage] = []             # → wiki/concepts/ (kein Code, nur Semantik)
    pm_update: PMUpdate
