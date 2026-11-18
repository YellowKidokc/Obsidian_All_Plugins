# Obsidian_All_Plugins

One home for everything David uses to run his Obsidian vaults: plugins, file
actions, the paper registry, the dashboard, canonization, semantic tagging and
review. Markdown files in the vault stay the master copy; every tool here reads
and writes them safely and logs who changed what.

Status: **plan only**. Nothing has been moved in yet. The prompt for the
implementing agent (Codex) is at the bottom of this file.

---

## 1. Inventory (surveyed 2026-11-18)

| Source folder (D:\GitHub\…) | What it is | Owner | Decision |
|---|---|---|---|
| `OBS_-Quantum_Paper` | Python paper registry: one file shown in many folders, safe moves, batch moves, reconcile, tangents, who-moved-what history, right-click "Quantum Paper…" menu, Opus button | David | **Bring in** → `apps/quantum` |
| `OBS-BAT-DASHBOARD` | Dashboard specs + working read-only folder snapshot + flatten/convert/search actions | David | **Bring in** → `apps/dashboard`, `actions/` |
| `Canonizationv1\Canonization-integration-20260904` (repo YellowKidokc/Canonization, branch `feature/integrated-canonization-20260904`) | **Canonization Workbench**: FastAPI + React + Postgres, rulings, canon versions, evidence atoms, atom builder, vault importer. Working as of 2026-09-22. Backed up to GitHub 2026-11-18 | David | **Bring in** → `apps/canonization` (its `.env` stays local, never committed) |
| `YellowKidokc-Canonization` | Older Obsidian-only Canonization plugin v0.3 (`_CANONICAL` cards, IDs, aliases) | David | **Bring in as reference** → `legacy/canonization-v0.3`; port useful ideas into the Workbench plugin |
| `theophysics-semantic-ai` | Obsidian plugin: classify notes against presets, hidden UUID tags, vault index, concept graphs; OpenAI/Anthropic/DeepSeek/Ollama client | David | **Bring in** → `plugins/semantic-ai` (stays its own plugin) |
| `theophysics-axiom-chain` | Research corpus: Axiom Chain master docs + Lean 4 proofs (remote under DavidLoweOKC) | David | **Bring in as content** → `content/axiom-chain` **without** `.lake/` build output (~85k generated files) |
| `theophysics-vault-cleaner` | One script: exact/near-duplicate detection, BOM fixing, move-not-delete | David | **Bring in** → `actions/vault-cleaner` |
| `theophysics_writing_audit_scripts` | 4 scripts: style measurement + adversarial overclaim audit for one paper | David | **Bring in** → `actions/paper-audit` |
| `axiom-canon` | 9-file Python package (models/states/validate), no git | David | **Review**, likely fold into `apps/canonization` |
| `canon-backup` | Bundle backup of TextGO + canon-engine (2026-08-26) | David | **Keep as-is** (backup, not code to merge) |
| `Obsidian` | Old Python desktop backend, but a backup script nested `_BACKUPS` inside itself ~430 times (~47,800 files, paths 865 levels deep) | David | **Extract one copy** of the deepest `python_backend` → `legacy/python-backend-2024`, then delete the folder |
| `theophysics-os` | Machine services: clipboard sync, Cloudflare tunnel, organize/classify engine. **4 commits never pushed** | David | **Stays separate.** Push its commits first |
| `pipeline-workflows` | API call workflows | David | **Stays separate for now** (possible later move into `apps/api-station`) |
| `Canonizationv1` (rest of it) | 136k files, not in git: Lean, humanizer, crawler, agent router, and **a second copy of pipeline-workflows with 602 uncommitted changes** | David | **Do not delete** until the pipeline-workflows copy is compared with `D:\GitHub\pipeline-workflows` and saved |
| `obsidian-synology-sync` | Someone else's plugin (fangjing2021), untouched clone | upstream | **Delete** (re-clone any time) |
| `obsidian-synology-sync-my3rs` | Someone else's plugin (my3rs), untouched clone | upstream | **Delete** |
| `obsidian-mind` | Someone else's vault template (breferrari), untouched clone | upstream | **Delete** |
| `obsidian-project-vault-template` | Someone else's PARA template, untouched clone | upstream | **Delete** |
| `obsidian_template` | Someone else's research vault template with arXiv / Semantic Scholar MCP servers | upstream | **Keep as reference** for Quantum's paper layout, or delete and keep the link |
| `Canonization-upstream` | Fresh clone of YellowKidokc/Canonization with only a README | David | **Delete** |
| `_Canonizationv1_vendored_cocoindex_backup` | Clone of cocoindex-io/cocoindex | upstream | **Delete** |

Deletions are done by David (or on his explicit go-ahead), never by the
implementing agent.

## 2. Target layout

```text
Obsidian_All_Plugins/
  README.md                 this plan
  OBSIDIAN_ACTIONS.bat      double-click menu for all actions (section 3)
  apps/
    quantum/                paper registry, web UI, right-click menu, history
    dashboard/              the home page: folder grid, views, actions, health
    canonization/           Canonization Workbench (backend + frontend + plugin)
  plugins/
    semantic-ai/            Obsidian plugin
    review/                 CriticMarkup chapter review (section 4)
  actions/
    _lib/                   shared safe-file helpers (atomic write, UTF-8, logging)
    navigation-index/       per-folder index notes (section 3)
    vault-cleaner/
    paper-audit/
    flatten/ convert/ search-report/ snapshot/
  content/
    axiom-chain/            research docs + Lean sources (no build output)
  legacy/                   read-only references, never imported by live code
  tools/                    ATEN trim, Opus button, setup scripts
  tests/
```

## 3. Features to build

**A. One action menu (`OBSIDIAN_ACTIONS.bat`).** Double-click → numbered menu, or
drag a folder onto it. Every action: dry run first, shows what will change, asks
before writing, writes a receipt, logs to Quantum history with an actor name.
Actions: navigation index, combine markdown (merge a folder's notes into one file
in order, with headings and source links), flatten / undo flatten, convert,
vault clean (duplicates, BOM), paper audit, folder snapshot, reconcile registry.

**B. Folder navigation index.** For every folder, top to bottom, write one index
note (default name `_INDEX.md`, configurable) containing:
- a breadcrumb back up to the vault root (`Home › Series › Part`)
- one or two lines explaining what the folder is for (from an existing
  description, the folder's README, or the first lines of its notes; never invented)
- links to every subfolder's index note
- links to every note in the folder, with its title and a one-line summary
- counts and last-modified dates

Rules: regenerate only the marked generated block
(`<!-- nav:start -->` … `<!-- nav:end -->`) so hand-written text in the index is
kept; skip dot-folders and `.obsidian`; use `[[wikilinks]]` so Obsidian and HTML
export both resolve them; re-run is idempotent (no change → file untouched);
dry run lists which index files would be created or changed.

**C. Dashboard folder grid** (in `apps/dashboard`, served by Quantum's local
server). Home = grid of the vault's top-level folders (about 6×7 for B_series),
each tile with name, paper count, last change. Click → only that folder's
subfolders and papers, with breadcrumb. Select papers → Move / Also show here /
Copy / History, all through Quantum. Map comes from a cached snapshot refreshed in
the background (the vault is on a NAS; never scan live on every click).

**D. Views without renaming.** Replace Quantum's current dot-prefix renaming
views (which break every path, the registry and logs) with Obsidian's
"Excluded files" setting (`.obsidian/app.json` → `userIgnoreFilters`). A view =
a named set of excluded folders; switching rewrites only that setting.

**E. Canonization + Semantic AI share one concept registry.** Same concept ID
whether it came from a canon card or a semantic tag. Do this after both are in
the repo and working; do not merge the two plugins into one.

## 4. Chapter review (plugin `review`)

CriticMarkup in the `.md` files is the format:
`{~~old~>new~~}{>>[grammar] reason<<}`, `{++add++}`, `{--delete--}`,
`{==text==}{>>[note] comment<<}`. Types and colors: grammar orange, clarity
blue, fact red, style purple, note green.

- Short term: use the Commentator plugin (Fevol) for accept/reject. It is beta;
  test on copies first.
- This repo's `review` plugin adds what Commentator lacks: colors by `[type]` tag,
  and an "AI review this chapter" command that asks the model to return the chapter
  with changes **only** as CriticMarkup, every comment starting with its type tag.
  Verify the returned text equals the original once all markup is rejected,
  otherwise refuse to save.
- Long term: HTML export (Webpage HTML Export plugin first, Quartz later). The
  navigation index notes become the site's folder pages.

## 5. Ground rules for all code here

- Windows first. Paths with spaces, UNC paths (`\\192.168.2.50\…`), backslashes.
- UTF-8 always; never the system code page. Atomic writes (temp file + replace).
- Never delete user files: move to a dated `_trash` folder or refuse.
- Never commit secrets: `.env*`, API keys, database URLs stay out of git.
- Every mutating action logs to Quantum history with an actor
  (`--actor`, `QP_ACTOR`, or `David (right-click)`).
- Existing tests keep passing; new behaviour gets tests.

---

## Prompt for Codex

```text
You are consolidating David's Obsidian tooling into this repository
(YellowKidokc/Obsidian_All_Plugins, branch OBS-Plugin-Final-Claude). Read this
whole README first; sections 1–5 are the spec.

Work in small, separately committed phases. After each phase, run the tests and
stop with a short report (what moved, what was skipped and why, what to verify).

Phase 1 — Import, history-preserving where the source is a git repo.
  - Use `git subtree add --prefix=<target> <source-path-or-url> <branch>` for:
      OBS_-Quantum_Paper → apps/quantum
      OBS-BAT-DASHBOARD → apps/dashboard (move its tools/actions into actions/ in a later commit)
      Canonization (branch feature/integrated-canonization-20260904) → apps/canonization
      theophysics-semantic-ai → plugins/semantic-ai
      theophysics-axiom-chain → content/axiom-chain
  - Copy plain folders (no git): theophysics-vault-cleaner → actions/vault-cleaner,
    theophysics_writing_audit_scripts → actions/paper-audit,
    YellowKidokc-Canonization → legacy/canonization-v0.3.
  - Root .gitignore must exclude: .env*, node_modules/, .venv/, __pycache__/,
    .lake/, build/, dist/ outputs that are generated, *.sqlite registries,
    .fisnote, *.pyc. Check nothing secret or generated was committed; if a
    subtree brought one in, remove it in a follow-up commit and report it.
  - Do NOT delete or modify anything outside this repository.

Phase 2 — Shared library and action menu.
  - actions/_lib: atomic UTF-8 write, safe move (never overwrite), dry-run plan
    object, receipt writer, Quantum history logging (import apps/quantum).
  - OBSIDIAN_ACTIONS.bat + a Python entry point: numbered menu and drag-and-drop.
  - Port flatten/convert/search-report/snapshot, vault-cleaner and paper-audit
    onto _lib, dry run by default.

Phase 3 — Navigation index (README section 3B). Include tests for: nested
  folders, hand-written text preserved outside the nav block, idempotent re-run,
  dot-folders skipped, names with spaces and Unicode, UNC root.

Phase 4 — Combine markdown action (section 3A).

Phase 5 — Views via Obsidian excluded files (section 3D). Keep the old rename
  views behind an explicit --legacy-rename flag, off by default, with a warning.

Phase 6 — Dashboard folder grid (section 3C), served by apps/quantum's server,
  standard library only on the Python side, no build step for the page.

Phase 7 — review plugin (section 4).

Phase 8 — Shared concept registry for canonization + semantic-ai (section 3E):
  write a design note first and stop for David's approval before coding it.

Constraints: Python 3.10+ standard library for Python tools unless a component
already depends on more (the Canonization backend does). Windows paths and UNC
must work. Never print or commit secrets. If anything is ambiguous, choose the
safer option and list it in your phase report.
```
