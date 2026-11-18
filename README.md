# Obsidian_All_Plugins

One home for everything David uses to run his Obsidian vaults: plugins, file
actions, the paper registry, the dashboard, canonization, semantic tagging and
review. Markdown files in the vault stay the master copy; every tool here reads
and writes them safely and logs who changed what.

Status: **plan only**. Nothing has been imported yet except `apps/registry` (seeded from David-OSv3). The Codex prompt is at the bottom; it runs as one pass.
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
    registry/               OBSIDIAN_REGISTRY.html generator (progress, structure, identity; docs/FIS_OBSIDIAN_SPLIT_PLAN.md)
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

**F. Obsidian progress page (`OBSIDIAN_REGISTRY.html`).** The spec is
`docs/FIS_OBSIDIAN_SPLIT_PLAN.md`, sections 5–16. In short: a vault roll-up grid of
every series with a progress bar; per-series and per-paper progression boxes backed
by evidence on disk. A folder that exists but holds no valid receipt and response
is **Present, not verified**, never Done. It also covers series structure
conformance against `docs/SERIES_STRUCTURE_STANDARD_DRAFT_2026-11-18.md` (Moral
Decline is the reference), `.backside` matching, the axiom-chain governance panel,
Quantum "also shown in" and history, and editorial review counts. Identity follows
`docs/DOCUMENT_IDENTITY_STANDARD_v1.0.md`. The page reports; it never assigns IDs,
admits canon, moves or renames. Start from David-OSv3's `registry_scan.py` and
`registry_template.html` (copy them into `apps/registry`).

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
whole README and everything in docs/ first. They are the spec. Do the whole job
in ONE pass and open ONE pull request. Commit in logical chunks inside it so it
can be reviewed, but do not stop between parts.

1. Import (history-preserving where the source is a git repo, via git subtree):
     YellowKidokc/OBS_-Quantum_Paper (branch OBS-Plugin-Final-Claude) -> apps/quantum
     YellowKidokc/OBS-BAT-DASHBOARD (branch OBS-Plugin-Final-Claude) -> apps/dashboard
     YellowKidokc/Canonization (branch feature/integrated-canonization-20260904) -> apps/canonization
     YellowKidokc/theophysics-semantic-ai -> plugins/semantic-ai
     DavidLoweOKC/theophysics-axiom-chain -> content/axiom-chain (exclude .lake/)
   If a source is not reachable from your environment, leave a clearly marked
   placeholder folder with a README naming the source, and continue.
   apps/registry is already seeded with registry_scan.py, registry_template.html,
   fis_gates.py and its test.
   Root .gitignore: .env*, node_modules/, .venv/, __pycache__/, .lake/, generated
   build/dist output, *.sqlite registries, .fisnote, *.pyc. No secrets in git.

2. actions/_lib shared helpers: atomic UTF-8 write, never-overwrite move, dry-run
   plan, receipt writer, Quantum history logging (import apps/quantum).

3. OBSIDIAN_ACTIONS.bat + Python entry point (numbered menu, drag-and-drop)
   with every action from README section 3A, dry run by default.

4. Navigation index (section 3B and split plan 16.4) with tests: nested folders,
   hand-written text kept outside the nav block, idempotent re-run, dot-folders
   skipped, spaces/Unicode names, UNC root.

5. Combine markdown action (section 3A).

6. Views via Obsidian excluded files (section 3D); old rename views only behind
   --legacy-rename with a warning.

7. apps/registry: OBSIDIAN_REGISTRY.html per docs/FIS_OBSIDIAN_SPLIT_PLAN.md
   sections 5-16, including the vault roll-up grid, the evidence-backed status
   model, series structure conformance, backside matching, the axiom governance
   panel, Quantum also-shown-in/history, editorial review counts, and every pilot
   acceptance test in section 14 as an automated test using fixture folders.
   Same scan JSON also feeds the _INDEX.md navigation notes.

8. Dashboard folder grid (section 3C) served by apps/quantum's local server,
   linking to the registry pages.

9. plugins/review (section 4).

10. Shared concept registry for canonization + semantic-ai (section 3E): write
    docs/CONCEPT_REGISTRY_DESIGN.md only. Do not implement it; David approves first.

Hard rules: never assign document IDs, admit canon, rename or delete user
files; observe-and-report tools write nothing outside their output/receipt
paths; Windows + UNC paths must work; Python 3.10+ standard library for Python
tools unless a component already depends on more; all existing tests pass and
new behaviour has tests. If something is ambiguous, choose the safer option and
list it in the PR description under "Decisions for David".
```
