# FIS / Obsidian split — build order and naming ladder

David, 2026-11-11. This adds to `HANDOFF_REGISTRY_INTEGRATION.md`. Where they disagree, this one wins.

## 1. Two lanes, one generator

| Lane | Where it applies | Page it writes | What it covers |
|---|---|---|---|
| **Obsidian** | Any folder inside the Obsidian vault (has a `.obsidian` ancestor) | `OBSIDIAN_REGISTRY.html` | Notes: identity, progress boxes, relations, links between notes |
| **FIS** | Every other folder | `FIS.html` (unchanged) | Files: names, keywords, address, proposed rename |

- Both pages come from **one generator** (the FIS engine, `fis_folder_memory.py`). It picks the lane per folder.
  A folder gets one page, never both. That settles objection 5.
- `registry_scan.py` + `registry_template.html` become the Obsidian lane's renderer, not a second tool.
- Machine-data dot folder name: **`.data`**. Math Is Moral already uses it and the scanner already reads receipts there.
- Publication-artifact dot folder name: **`.backside`**. Article HTML, web media, render variants, and publication derivatives live here. They do not go in `.data`.
- Generated pages (`OBSIDIAN_REGISTRY.html`, `FIS.html`) stay in the folder. They never move to `.data`.

## 2. Build order: gates 1–5 before any indexing

Nothing indexes the whole campus until all five are done and tested on one small and one large folder.

1. **Disk-space gate.** Check free space before every write and stop cleanly if it's short. C: had 0 GB free.
2. **Built-set exclusion.** Linked HTML sets (Kimi axiom series, `50_PRODUCTION_AND_PUBLICATION`, site builds)
   are skipped, or moved only as a whole set. Frontmatter paths (`card:`, `receipt:`) are rewritten or checked so they still resolve.
3. **Obsidian files are off-limits.** `.obsidian/`, `*.base` and `*.canvas` are never moved or rewritten.
4. **Simulate → receipt → move → undo.** A dry run writes a receipt (source, destination, SHA-256).
   David approves it. The move then writes an undo file. Nothing is deleted.
5. **One page per folder.** Lane detection is in place, and an old second page found in a folder is reported (not deleted).

6. *Only then:* full index. Cap listings in big folders (MIM.06 has 22,240 transcripts). Hash or classify only new or changed files, tracked by mtime and size.
7. *Then:* linking. Obsidian lane shows note-to-note relations and "Also shown in". FIS lane links files to the notes that cite them.

## 3. Naming ladder (who gets to name a file)

Each rung only runs if the rung above it couldn't decide.

1. **Excel lexicon.** Look the file's terms up in `.data/classification/LEXICON_MASTER_v2_UNIFIED.xlsx`
   (the one source; the other workbooks merge into it or are retired). A clear match names the file.
2. **Local inference.** Rules plus the learned vocabulary (folder context, sibling names, frontmatter). Free, offline.
3. **DeepSeek.** A cheap model suggests the name, with a confidence score.
4. **Council.** For low confidence or files that matter most (canon, published, cited papers), send it to all
   the models (Claude, DeepSeek, Kimi, GPT…). A name is accepted if they agree.
5. **David.** Anything still unsettled goes to a review queue. His ruling is final, and new terms go
   back into the Excel so rung 1 catches them next time.

**Sidecar.** Every naming decision writes `.data/<file>.fis.json` with: the name, the rung that decided it,
the confidence, each model's vote, and the time. You can always see why a file has its name, and undo it.

## 4. Ruled by David (2026-11-11)

- Page name `OBSIDIAN_REGISTRY.html` is accepted.
- "Matters most" (goes straight to the council): **canon, new work, published, cited by others**.
- Rungs 3–4 go through David's API job handoff (`hub/api`). Each naming question is a small job, and they add
  up to the big rename. Wiring this is a later step, after gates 1–5.

## 5. Obsidian is not the website lane

`OBSIDIAN_REGISTRY.html` is an operational page for a human working inside an Obsidian vault. It is not the
article HTML, the public website, or the FIS rename report.

Each concern has one home:

| Concern | Home | Meaning |
|---|---|---|
| Markdown papers and original evidence | visible paper/series folder | Human-authoring source and evidence |
| `OBSIDIAN_REGISTRY.html` | visible folder root | Generated progress, identity, gaps, and next-action page |
| FIS JSON, classification, receipts, ledgers, approval records | `.data/` | Machine state and audit trail |
| Article HTML, render variants, web-only media, CSS/JS, optimized images | `.backside/` | Publication artifacts hidden from ordinary Obsidian browsing |
| `FIS.html` | non-Obsidian folder root only | File-intelligence and proposed-name page |

Original media follows the paper it evidences. Web-only or optimized derivatives follow the HTML into
`.backside`. A derivative must retain its source hash/lineage; it is not a second original.

## 6. What the Obsidian page must answer

The Obsidian page is a folder-level work order. Without opening ten subfolders, David must be able to see:

1. **What is this folder?** Series title, physical path, scan time, applicable completion profile, and whether
   the folder is a series, a paper, a research dossier, or an operations folder.
2. **What knowledge objects are here?** Approved document ID when one exists, current title, series position,
   version, hash, and the source note that carries the record.
3. **How far has each object progressed?** A compact progression row backed by artifacts and receipts on disk.
4. **What is missing?** Missing required artifact, missing receipt, receipt pointing to a missing output,
   stale output, conflicting versions, or an expected folder that is empty.
5. **What is merely present?** A folder or filename may be present without proving completion.
6. **What is next?** One computed next action per paper, plus a folder-level bottleneck summary.
7. **Where are the relationships?** Wikilinks, cross-series relationships, source/derivative relationships,
   supersession, and “also shown in” virtual views.
8. **What is on the backside?** Matched HTML, render variants, media dependencies, broken relative assets,
   and whether the HTML is current for the present Markdown hash.
9. **What has authority?** Canon and permanent identity must show the ruling/approval record. Inference or a
   confident classifier must never light those boxes.
10. **Can this be undone or reproduced?** Receipts, run IDs, pipeline versions, hashes, and move undo records.

The page should lead with the work state. Detailed FIS vectors, raw frontmatter, and machine context stay in
collapsed sections so the page remains readable.

## 7. Evidence-backed status model

Folder names alone never count as completion. In particular, an `API_CALLS`, `API_RUNS`, `AI_REVIEW`, `LEAN`,
`HTML`, or `media` folder can exist and still be empty, partial, stale, or disconnected from the paper.

Use these states:

| State | Rule | Display |
|---|---|---|
| `DONE` | Required artifact exists, its receipt exists, referenced outputs exist, and recorded hashes match | Green |
| `PRESENT_UNVERIFIED` | Artifact or folder exists, but no valid receipt proves the run/output | Amber |
| `MISSING` | Step applies but its required artifact is absent | Red |
| `BROKEN` | Receipt exists but its named artifact is absent, unreadable, or hash-mismatched | Red with error |
| `STALE` | Artifact was valid for an older source hash/version but the source has changed | Purple or amber warning |
| `CONFLICT` | Multiple competing artifacts exist and no ruling selects one | Split/conflict marker |
| `NOT_APPLICABLE` | A profile or explicit ruling says the step does not apply | Dashed gray |
| `BLOCKED` | Required authority, dependency, or human ruling is missing | Red/amber lock |

The current word `claimed` should be rendered to humans as **Present, not verified**. It must never be counted
as done.

### API/AI completion rule

An API or AI step is `DONE` only when all required pieces are present:

1. request/prompt or job identity;
2. run receipt with `run_id`, provider/model or local engine, timestamps, and completion status;
3. response artifact named by that receipt;
4. parent `document_id` or an explicit unresolved-match marker;
5. source-version or source-hash reference;
6. response hash; and
7. no truncation/failure status.

If the folder exists but the receipt or response is absent, the page must say **API/AI folder present — run not
complete**. If a receipt names a response that is missing, show `BROKEN`, not `DONE`.

## 8. Proposed Obsidian progression

These are implementation defaults, not new canon rulings. Applicability comes from a completion profile; not every
paper requires Lean, audio, podcast, or video.

### Main knowledge progression

1. **Identity** — approved registry ID and version/lineage sidecar, or visibly “unassigned.”
2. **Source** — substantive Markdown/source exists; stubs are distinguished from drafts.
3. **Research** — research dossier/source registry exists when required.
4. **API/AI work** — required analysis runs have complete receipts and responses.
5. **Audit** — structural, argument, citation, or lawyer audit required by the profile is present.
6. **Claims and evidence** — extracted claims/evidence link back to source spans.
7. **Knowledge graph** — graph receipt/edges exist when required.
8. **Formalization** — Lean stub/result, compilation status, and theorem receipt when applicable.
9. **Human review** — attributed review ruling exists; AI review alone does not satisfy it.
10. **Canon ruling** — David-only admission record exists. Never infer this from a folder or filename.
11. **Backside package** — matched HTML and required web media exist, dependencies resolve, and source hash is current.
12. **Published** — publication receipt and live/current location exist.

### Output tracks, shown separately

Narration, podcast, video, social cards, and other media outputs should not distort the main epistemic progression.
Show them as an **Output tracks** row with their own `DONE / PRESENT_UNVERIFIED / MISSING / NOT_APPLICABLE` states.

## 9. Completion profiles prevent too many or too few requirements

Do not hard-code every possible step as required for every note. The scanner assigns or proposes a profile such as:

- `series_index`
- `principal_paper`
- `companion_paper`
- `research_dossier`
- `formalization_packet`
- `source_registry`
- `operations_governance`
- `publication_page`

Each profile defines required, optional, and not-applicable artifacts. The selected profile and the evidence for it
must appear on the page. A classifier may propose the profile; a profile affecting identity, canon, or movement
requires the applicable approval/ruling.

A suggested configuration file is `.data/obsidian_completion_profiles.yaml`. Per-document overrides belong in an
approved sidecar, not in generated HTML.

## 10. Folder and paper health checks

At the top of `OBSIDIAN_REGISTRY.html`, show counts and direct links for:

- papers with no approved identity;
- duplicate IDs or the same ID attached to differing content;
- source notes without sidecars;
- required steps missing;
- present-but-unverified API/AI runs;
- broken or truncated runs;
- stale artifacts whose recorded source hash is old;
- competing versions awaiting a ruling;
- backside HTML with no matched source paper;
- source papers with no required backside HTML;
- HTML with missing local images, CSS, JavaScript, audio, or relative links;
- original media versus derived web media whose lineage is unknown;
- receipts that point outside the scanned root;
- review and canon fields lacking an authority record;
- old `FIS.html`/`OBSIDIAN_REGISTRY.html` lane collisions;
- folders so large that listing was capped.

Health findings are observations, not automatic permission to move, rename, delete, admit, or supersede.

## 11. Three-address and document-identity display

For every knowledge object, show the three addresses independently:

- **Physical:** current path, proposed path if any, and whether a move is authorized.
- **Canonical:** argument/build role, law links, epistemic role, canon status, authority, and ruling evidence.
- **Navigation:** series, position, subjects, people, worldviews, document type, and lifecycle.

Use the permanent registry-issued `SERIES.POSITION.SLUG` document ID when approved. Moving, renaming, rendering,
or revising does not change it. Derived artifacts display their root identity and role, for example
`DLAY.05.WATER::render.site`, but the scanner only reports or proposes identity; it does not issue one.

## 12. Backside matching rules

The Obsidian page should show a backside match only when supported in this order:

1. approved `document_id` embedded in both records;
2. explicit lineage/receipt;
3. source hash recorded by the derivative;
4. exact normalized series position and title;
5. strong Markdown-to-HTML text similarity, marked as a proposal;
6. filename similarity, marked `HOLD` until reviewed.

For each match show artifact role, file path, artifact hash, source hash/version, render date, pipeline/run ID,
dependency health, and whether a newer source has made the HTML stale. Competing HTML files remain separate artifacts;
the page must not overwrite one or silently choose the newest timestamp.

## 13. Generator contract for the next coder

The implementation should emit one JSON record per knowledge object and keep presentation logic in
`registry_template.html`. At minimum, add:

```json
{
  "document_id": null,
  "identity_state": "UNASSIGNED",
  "completion_profile": "principal_paper",
  "source_sha256": "...",
  "steps": {
    "api_ai": {
      "state": "PRESENT_UNVERIFIED",
      "artifacts": [],
      "receipts": [],
      "reason": "API_RUNS exists but no completed response receipt was found"
    }
  },
  "output_tracks": {},
  "backside_artifacts": [],
  "three_address": {
    "physical": {},
    "canonical": {},
    "navigation": {}
  },
  "next_action": "Verify or rerun the required API analysis",
  "findings": []
}
```

Required implementation behavior:

- scan notes at any depth, while excluding `.obsidian`, generated pages, caches, and configured large-data roots;
- discover `.data` receipts and `.backside` artifacts without treating either folder's existence as completion;
- hash only new or changed files using cached size/mtime and content hash;
- keep one record per permanent document ID, with unresolved no-ID notes shown separately;
- never merge differing content merely because filenames or IDs collide;
- cap huge listings while retaining aggregate counts and direct paths;
- generate a deterministic page from scan JSON;
- perform no rename, move, deletion, canon admission, or ID assignment;
- write a scan receipt stating roots, exclusions, counts, warnings, generator version, and output hash.

## 14. Pilot acceptance tests

Before campus-wide generation, test one small series and one large series. The pilot passes only if:

1. `.obsidian`, `*.base`, and `*.canvas` are untouched;
2. the same scan produces the same registry JSON/page when nothing changed;
3. an empty `API_RUNS` folder displays `PRESENT_UNVERIFIED`, not `DONE`;
4. a receipt pointing to a missing response displays `BROKEN`;
5. a source edit makes an older HTML artifact display `STALE`;
6. a valid receipt plus matching response and hashes displays `DONE`;
7. an explicitly inapplicable Lean/media step displays `NOT_APPLICABLE`;
8. competing HTML versions remain visible and separate;
9. a duplicate ID with different content displays `CONFLICT`;
10. the page is understandable without opening the database;
11. no scanned source file is modified; and
12. the scan receipt and generated-page hash are written successfully.

## 16. Obsidian additions (2026-11-18)

Added after the Moral Decline pilot (`B_series/_SERIES_STRUCTURE_STANDARD_DRAFT_2026-11-18.md`) and the
Obsidian tooling consolidation (`YellowKidokc/Obsidian_All_Plugins`). Same rules as above: observe and report,
never move, rename, assign IDs or admit canon.

### 16.1 Vault roll-up page (the "grid")

The vault root (e.g. `B_series/`) gets one `OBSIDIAN_REGISTRY.html` that shows **every series as a tile**, about
6×7 for B_series. Each tile: series title, paper count, a thin progression bar (share of papers per state from
section 7), structure-conformance badge (16.2), worst open finding, last change. Clicking a tile opens that series'
own page; the roll-up never lists individual files. This is the "what's done, what isn't" view across all series.

### 16.2 Series structure conformance

Check each series against the Series Folder Structure Standard. Moral Decline is the reference template.

| Check | Rule |
|---|---|
| Index | `00_SERIES_INDEX.md` exists and is substantive (not a stub) |
| Ordered papers | visible children are numbered `NN_TITLE/` folders, no stray loose HTML/media/metadata trees at the series root |
| Backside exists | one `.backside/` at the series root, no second backside elsewhere in the series |
| Mirrored sections | every `NN_` paper folder has a matching `.backside/NN_` folder, and no backside folder lacks a visible paper |
| Backside contents | each mirror has at least one `article*.html`; `assets/` only holds derivatives; receipts present |
| Provenance | `.backside/BACKSIDE_PROVENANCE.md` exists and its SHA-256 list matches disk |
| Original media | evidence media sits with the paper, not only in `.backside` |
| Competing versions | `.bak-shell` / `vN` variants kept side by side, none silently dropped |
| HOLD | unmatched incoming HTML is listed as HOLD, never placed |

Series state: `CONFORMS` (all checks pass), `PARTIAL` (some), `NOT_STARTED` (no backside, no index),
`HOLD` (unresolved matches waiting for David). An empty `.backside/NN_` folder counts as `PRESENT_UNVERIFIED`,
the same rule as an empty `API_RUNS` folder.

### 16.3 Paper registry (Quantum Papers) on the page

When the vault has a `.quantum/` registry:

- **Also shown in:** the folders a paper is listed in without being copied there.
- **Who moved what:** the last moves/saves for each paper (actor, time, from → to). Agent moves and right-click
  moves stay distinguishable.
- **Registry health:** stale papers (file vanished), ambiguous external moves, unregistered new files, from
  `quantum.py --reconcile`.
- Registry IDs are internal record keys, not document IDs. Permanent `SERIES.POSITION.SLUG` identity still comes only
  from the approved registry (Document Identity Standard v1.0).

### 16.4 Navigation inside Obsidian too

The HTML page is for overview; Obsidian itself needs the same navigation. Each folder gets an `_INDEX.md` with a
generated block (`<!-- nav:start -->` … `<!-- nav:end -->`): breadcrumb up, one-line folder purpose (taken from
the folder's index/README, never invented), wikilinks to every child index and every note. Hand-written text
outside the block is kept. The HTML page and `_INDEX.md` are generated from the same scan JSON, so they never disagree.

### 16.5 Axiom-chain governance view

Folders whose notes carry axiom-chain IDs (`A1.1`, `BC6`, `T3.1`, `D19.4`, `LN5.1`, `EV15.2`, `FALS18.1` …) get a
governance panel built from frontmatter, matching the existing read-only governance ledger:

- table: ID, mode (`AX_CORE`, `AX_DERIVED`, `AX_SCAFFOLD`, `FW_EXTENDED`, `HY_EVIDENCE`), status, atlas type,
  domain, depends-on, claim species, warrant class, bridge, flags;
- **dependency integrity:** depends-on an ID that does not exist → `BROKEN`; cycles → `CONFLICT`;
- **layering check:** a record depending on a record from a later layer is flagged for review, e.g. in the
  pre-v2.3 ledger `E6.2` (AX_SCAFFOLD) depends on `A6.2` (FW_EXTENDED), and `D19.3/5/7/9` depend on
  `A8.2`, `P3.2`, `LN5.1`, `A9.2`;
- **review queue:** count and list of flagged records (pre-v2.3: 102 of 191, mostly "statement contains em-dash"
  and possible two-clause bundles) with a link to each source note;
- bridges with fewer than two dependencies shown as incomplete mappings;
- DeepSeek / council runs shown with the API/AI completion rule (section 7). Governance must be confirmed before
  a run counts as `DONE`.

### 16.6 Editorial review state

Count CriticMarkup marks per paper (`{~~ ~>~~}`, `{++ ++}`, `{-- --}`, `{== ==}{>> <<}`) by type tag
(`[grammar]`, `[clarity]`, `[fact]`, `[style]`, `[note]`). A paper with open suggestions shows **Editorial review:
N open** in its output tracks. Zero marks plus a review receipt = `DONE`; zero marks with no receipt = not reviewed.

### 16.7 Where the code lives

- FIS engine and the FIS lane stay in `David-OSv3`.
- The Obsidian lane renderer (`registry_scan.py` + `registry_template.html`, extended per sections 5–16) moves to
  `Obsidian_All_Plugins/apps/registry`, importing the shared lane detection and scan JSON contract so the two
  lanes cannot drift.
- `OBSIDIAN_REGISTRY.html` and `FIS.html` stay different pages for different jobs: notes and progress versus
  files and proposed names.

## 15. Still open for David's ruling

- Exact completion-profile requirements for each document type.
- Final labels/colors for `STALE`, `CONFLICT`, `BROKEN`, and `BLOCKED`.
- Whether `OBSIDIAN_REGISTRY.html` remains in every folder or only series/paper roots with inherited child status.
- Whether the main progression has exactly twelve boxes after the pilot, or whether some become grouped substeps.
- Which existing sidecar schema becomes the authoritative home for per-document profile overrides.
