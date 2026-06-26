# MCP Knowledge System — Übernahme-Blueprint

Self-contained Anleitung, um das pkwiki-System (MCP-Server + Zugriffsmodell + optionale
Knowledge-Pipeline) in **ein anderes Projekt** zu übernehmen und dort
**Multi-User-Knowledge-Management aus einem Copilot als Teil einer App** zu betreiben.

> Kurz: Jeder App-User bekommt einen Copilot mit eigenem, zugriffsgefiltertem
> Langzeitgedächtnis. Geteiltes Wissen (Produktdoku etc.) ist gemeinsam sichtbar,
> privates Wissen bleibt pro User isoliert. Durchsetzung passiert **vor** der
> Kontextbefüllung, deterministisch, fail-closed.

---

## 1. Architektur in drei Schichten

```
┌─ Zugriffsmodell ──────────────────────────────────────────────┐
│ access.py  — Leiter public<customer<internal<team<personal     │
│   lesbar ⇔ rank(visibility) ≤ rank(clearance) UND node∈read_scope
│   schreiben ⇔ node == write_scope ; fail closed                │
└───────────────────────────────────────────────────────────────┘
┌─ Server ──────────────────────────────────────────────────────┐
│ pkwiki_server.py  — Kernlogik (nur stdlib + access.py)         │
│ pkwiki-mcp.py     — dünner FastMCP-stdio-Entrypoint           │
│   Tools: search_wiki, read_page, list_index, remember, save_note
└───────────────────────────────────────────────────────────────┘
┌─ Daten ───────────────────────────────────────────────────────┐
│ vault-tree.yaml   — Nodes (rights) + Agenten-Profile          │
│ <vault>/wiki/ + <vault>/<node-path>/wiki/  — Markdown-Seiten   │
└───────────────────────────────────────────────────────────────┘
```

## 2. Was kopieren (portabel)

| Datei | Rolle | Abhängigkeiten |
|-------|-------|----------------|
| `access.py` | Zugriffslogik, *single source of truth* | **keine** (reine stdlib) |
| `pkwiki_server.py` | Kernlogik (Tools, Seiten-Erfassung, Schreibziel) | stdlib + `access.py` |
| `pkwiki-mcp.py` | MCP-stdio-Entrypoint | `mcp`, `pyyaml`, `python-dotenv` (PEP-723-inline) |
| `test_mcp.py`, `test_access.py` | Tests (netzfrei) | stdlib |
| `vault-tree.yaml(.example)` | Nodes + Agentenprofile | — |
| `lint-tree.py`, `promote.py` | Rechte-Lint + Promotion-Planer | stdlib (+pyyaml) |

`access.py` und `pkwiki_server.py` sind bewusst importierbar **ohne** `mcp`/`yaml`, damit die
Tests ohne Netz/externe Deps laufen.

## 3. Zugriffsmodell (`access.py`)

```python
from access import AgentProfile, Page, can_read, filter_readable
agent = AgentProfile(id="user-123", clearance="personal",
                     read_scope=frozenset({"user-123", "company"}),
                     write_scope="user-123")
visible = filter_readable(candidate_pages, agent)   # Gate VOR dem Kontextfenster
```

- **Leiter:** `public < customer < internal < team < personal` (Index = Sensitivitäts-Rang).
- **Lesbar** ⇔ `rank(visibility) ≤ rank(clearance)` **und** `node ∈ read_scope`.
- **Schreibbar** ⇔ `node == write_scope`.
- **Fail closed:** fehlende/ungültige Seiten-`visibility` → `personal` (verbergen);
  fehlende/ungültige Agenten-`clearance` → `public` (geringster Zugriff). Unbekanntes leakt nie.

## 4. Wissensbaum & Agenten (`vault-tree.yaml`)

```yaml
tree:
  - node: company
    path: _company/
    rights: { clearance: internal, default_visibility: internal, read: [company], write: [company] }
  - node: user-123                       # ein Node PRO USER
    path: _users/_user-123/
    parent: company
    rights: { clearance: personal, default_visibility: personal,
              read: [user-123, company], write: [user-123] }

agents:
  - id: copilot-user-123                 # ein Profil PRO USER
    clearance: personal
    read_scope: [user-123, company]      # eigener Node + geteilte Vorfahren
    write_scope: user-123                # schreibt nur in den eigenen Node

bundle_visibility:                       # auto-generierte Bundles erben Sichtbarkeit
  manuals: customer                      # Produktdoku ist für customer-Agenten lesbar
```

- **Read nach oben, Write nach unten/self.** Hochstufen ins Geteilte = Promotion
  (`promote.py`, Review-Gate) — nie automatisch.
- `vault-tree.yaml` liegt **außerhalb** der Schreibzone jedes Agenten → ein Copilot kann
  seine eigenen Rechte nicht ändern. `lint-tree.py` validiert die Konsistenz.

## 5. Schreibzonen & Memory-Schichten

- `write_scope: session` → ephemerer Sandbox `<vault>/.sessions/<agent>/` (gitignored).
  **Default für Low-Trust-/Produkt-Agenten** — externer Input vergiftet das geteilte
  Gedächtnis nie.
- persistenter Node → schreibt **und** liest `<vault>/<node-path>/wiki/`. Pro-User-Node
  (`clearance: personal`) = privates Langzeitgedächtnis.
- Memory-Schichten: **episodisch** = `log.md` (`remember`), **semantisch** = `concepts/` +
  `entities/` (`save_note`), **prozedural/Quelle** = `sources/`.
- Layout-Flexibilität: flaches `<vault>/wiki/` (= Wurzel-Node) und Pro-Node-Ordner
  koexistieren (`node_wiki_dirs`); `_write_target` schreibt ins Lese-Verzeichnis des Nodes
  (read = write) und legt es bei erstem Schreiben an.

## 6. Multi-User-Muster (Kern für den App-Betrieb)

Pro Software-User:
1. **Node** im `tree:` mit eigenem `path` (z.B. `_users/_<userid>/`).
2. **Agentenprofil** im `agents:` (clearance `personal`, write = sein Node,
   read = sein Node + geteilte Vorfahren).
3. **Server-Instanz** mit `PKWIKI_AGENT_ID=copilot-<userid>`.

> **Identität kommt immer vom Host (App-Backend), nie vom Agenten.** Der User bestimmt nicht,
> wer er ist — das App-Backend setzt `PKWIKI_AGENT_ID` beim Spawn.

**Noch zu bauen:** Provisioning-Automatik, die Node + Agentenprofil pro neuem User erzeugt
(statt handgepflegt) — der offene Baustein Richtung produktivem App-Betrieb.

## 7. App-Integration

Statt eines Desktop-/CLI-Clients bettet die App einen **MCP-Client ins Backend** ein und
**spawnt den Server je User-Session** über stdio:

```
command: <absoluter uv-Pfad>            # GUI/Server-Prozesse haben uv oft nicht auf PATH
args:    ["run", "--directory", "<repo>", "pkwiki-mcp.py"]
env:     { PKWIKI_AGENT_ID: "copilot-<userid>", VAULT_ROOT: "<vault>" }
```

Der App-Copilot ruft dann `search_wiki`/`read_page` (Kontext holen) und `remember`/`save_note`
(Gedächtnis schreiben) auf — alles bereits durch `access.py` auf den User gefiltert.

### Dev-Registrierung (Claude-Clients)
- Claude Code (alle Projekte): `claude mcp add pkwiki -s user -e PKWIKI_AGENT_ID=<id> -e VAULT_ROOT="<vault>" -- uv run --directory <repo> pkwiki-mcp.py`
- Claude Desktop: `%APPDATA%\Claude\claude_desktop_config.json` → `mcpServers.pkwiki` (absoluter uv-Pfad). Danach Client neu starten.

## 8. Knowledge-Pipeline (optional, falls Inhalte automatisch entstehen sollen)

`extract.py` (Text + Vision) → `ingest.py` (LLM → strukturierte Wiki-Seiten). Spezial-Pipelines:
`code-watch/extract/ingest.py` (GitHub-Commits → code-wiki), `manual-ingest.py`
(PDF-Handbücher, customer-sichtbar), `transcript-ingest.py` (Teams-`.docx`),
`clippings-ingest.py` (Web-Clipper). Wartung: `reorganise.py` (LLM-Klassifizierung der
visibility, mit Klassifizierungs-Cache), `rebuild-index.py`, `lint-links.py`, `wiki-sync.py`.
Benötigt Azure OpenAI (`.env`: `AZURE_OPENAI_*`).

## 9. Sicherheit / Härtung

- Identität & Rechte (`vault-tree.yaml`, `access.py`) liegen außerhalb der Agenten-Schreibzone
  → Self-Escalation über die Tools nicht möglich.
- **Offen (empfohlen vor Produktivbetrieb):** (a) Schreibpfad-Containment-Guard im Server
  (auflösen + prüfen, dass das Ziel innerhalb der erlaubten Wiki-Dir bleibt), (b) `vault-tree.yaml`
  + `access.py` per OS-ACL **read-only** für den Account, der die Agenten ausführt — bzw. den
  Server unter einem niedrig-privilegierten Account laufen lassen.

## 10. Gotchas (real aufgetreten)

- **Windows cp1252:** Skripte, die Unicode (`→ ✓ ✗ ○ ⚠`) drucken, früh
  `sys.stdout/stderr.reconfigure(encoding="utf-8")` setzen — sonst `UnicodeEncodeError`.
- Skripte, die Vault-Daten anfassen, müssen `VAULT_ROOT` respektieren (nicht repo-relativ).
- Teure LLM-Läufe (z.B. Klassifizierung) **je Call** persistieren, nicht erst am Ende.

## Referenz-PRs (`schlinge2000/pkwiki`)

#34 (visibility/T1–T5) · #38 (MCP-Server) · #40/#42 (Windows-Robustheit + reorganise-Cache) ·
#44 (MCP→main) · #46 (Flat-Fallback + Bundle-Vererbung) · #47 (persönliches Langzeitgedächtnis) ·
#48 (README-MCP-Sektion).
