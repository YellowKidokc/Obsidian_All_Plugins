# Codex: build the focused Obsidian research workbench

David's instruction: consolidate the collected tools into one focused Obsidian system. Keep useful components modular, reuse existing working code, and build the missing connections. This document is the current implementation handoff; older imported plans are references, not authorization to execute every historical script or replace the current architecture.

## Begin with the actual repository

1. Read README.md, docs/COMPONENT_MAP.md, docs/MODULE_NOTES_CROSSWALK.md, docs/FIS_OBSIDIAN_SPLIT_PLAN.md, docs/DOCUMENT_IDENTITY_STANDARD_v1.0.md, docs/SERIES_STRUCTURE_STANDARD_DRAFT_2026-11-18.md and each relevant IMPORT_STATUS.md. Check local AGENTS instructions and existing ownership before edits. Preserve other agents' work.
2. Work on one new feature branch based on OBS-Plugin-Final-Claude and deliver one reviewable PR targeting that integration branch. Do not force-push, merge the PR, publish a site or activate anything against the live corpus.
3. Read docs/RESEARCH_BACKEND_COMPARISON_20261118.json before choosing backend code. apps/research-manager and apps/research-backend share 119 identical files and 13 differing shared files, plus unique modules. Do not overwrite one tree wholesale with the other.
4. If vendor/plannotator is a submodule, run git submodule update --init --recursive vendor/plannotator and use its pinned revision and instructions. A missing checkout is not an excuse to replace its UI. Keep it as an upstream review dependency and put our adapter outside its source tree.

## Product target

One research workspace with: series overview -> paper list -> paper/source inspector, named media, processing progress, claims/premises/proofs/evidence/objections, paragraph naming and retrieval, definitions, relationships, metrics, review and projections. Obsidian remains the working reading/writing environment; Markdown source stays authoritative. The same records feed HTML, Excel, FIS and graphs.

David's chosen UI pairing:
- plugins/dashboard-navigator is the preferred native Obsidian front end for navigation, search, tags and vault statistics.
- apps/dashboard supplies read-only snapshots and carefully wrapped operational actions.
- apps/quantum owns existing file registry memberships and action history. One original can be shown in several places; that must not create duplicate manuscripts.
- plugins/semantic-ai is the maintained tagging/classification plugin. legacy/ai-tagger-bundle supplies older prompts/taxonomy/output ideas; do not install both manifests with the same plugin ID.
- apps/paper-projections manages one source snapshot and 21 projections. Wire it to existing API stations rather than inventing another runner for every output.
- The two research backends supply definitions, ontology, MTL, Mermaid and analytics candidates. Select and wrap tested modules.
- apps/ingest-engine supplies candidate Excel/HTML/Markdown ingestion. Fix its documented configuration/packaging defects before enabling it.
- templates/navigation provides five repaired Templater/CSS templates; a live recursive folder-index generator is still needed.
- plugins/second-brain-black-hole is an optional read-only visual map, not evidence of truth or a replacement for the typed graph. Respect configured note limits and display actual included/excluded counts.
- Plannotator reviews papers, projections, plans and rendered HTML; return annotations to the correct source/version and paper review log.
- apps/pipeline-desktop is an optional Tauri prototype, not the primary Obsidian surface. Do not put it on a live vault: direct overwrite/removal, identity changes and history wiring remain unresolved.
- docs/external-references/PhD_NOTES_REFERENCE.md and templates/research-workflows provide workflow inspiration. PhD-notes is not a software dependency; do not bulk-import its personal vault.

## Architectural contract first, then working integration

Create a small versioned shared JSON contract and SQLite index for series, papers, source versions, passages, atoms, typed ledger rows, relationships, metric definitions/observations, media, processing tasks, runs, artifacts, issues and review events. Reuse identifiers where they exist. Internal registry handles must not silently assign document/publication IDs or canon status to manuscripts. Hashes identify source versions; identical copies do not automatically become one paper.

Each derived record needs input source/version hash, locator, producing station/engine/schema/prompt version, timestamp and validation state. Metrics need value, unit, numerator, denominator, method and definition version. Unknown is not zero. Distinguish missing, blocked, unassessed, not_applicable, present_unverified, failed, stale, conflict and validated processing completion. Generated_unreviewed is not approval or proof.

Theological commitments may be declared inputs. Preserve assumptions, formal deductions, empirical support, structural correspondences and proposals as different types. Semantic similarity, graph centrality, keyword counts and coherence grades cannot automatically certify truth, a breakthrough, a proof or canon. Human rulings must be actual recorded decisions.

## Build these connected deliverables

### 1. One entry point and native dashboard adapter

Provide OBSIDIAN_WORKBENCH.bat with a clean small menu and a local browser control surface using the existing Quantum/dashboard server where practical. Keep Python implementation on the backend and preserve the standalone component entry points. Serve only the intended local interface. The Dashboard Navigator plugin should consume the same cached inventory/status data rather than rescan a NAS vault on every click.

Navigation: select series -> folders -> paper -> exact source span. Preserve identity context while the top inspector changes with the selected bottom ledger row. Filter claims/proofs/evidence/Lean/audits and scope to current atom/paper/series/corpus. Show missing fields honestly. Link named audio/video/images/projections with ownership and versions. Do not fabricate media files.

### 2. Recursive folder navigation and summaries

Generate visible Markdown index notes and HTML navigation for an explicitly selected root. Each folder has purpose, breadcrumb, child-folder summaries/links, file summaries/links, counts and freshness. Each file links back to its folder/series and source/projections. Use existing README/purpose descriptions first. Local fallback summaries must be labeled as structural inventory; optional API semantic summaries are source-grounded and cached by input hash.

Preserve authored text outside <!-- nav:start --> / <!-- nav:end -->. Regeneration must be idempotent. Skip dot-folders, .obsidian, .APPS, generated output and explicitly excluded/archive branches. Do not follow junctions/symlinks outside scope. Test nested folders, duplicate basenames, spaces/Unicode, moved files and UNC paths. Avoid recursively indexing the generated navigation itself. JSON/logs do not belong in the visible note tree.

### 3. Research records and analytics

Implement the common source/passage ledger and integrate useful definition/ontology/MTL/CDCM code through adapters. Keep source-bound typed relationships with candidate versus reviewed status; direction matters. Tag overlap is a candidate relation, not proof of support. Fix the toolkit's rescan count inflation, collision-prone fallback IDs, generated-output ingestion, destructive edge/metric regeneration and misleading SIS/LCS/SRI labels as documented in docs/paper-projections/IMPLEMENTATION_REFERENCE/00_REPAIR_AND_API_DESIGN_PROMPT_20261118.md.

Version historical Master Equation and fruit dictionaries instead of silently merging incompatible meanings. Locate and preserve the authoritative Master Equation Namer naming/scoring rules, including paragraph profiles and the established name/1-to-3 distinctions. If the authoritative implementation is unavailable in this environment, provide an explicit unavailable adapter with its exact missing dependency; do not invent a replacement and claim parity.

Capture measured text/academic statistics, source references, claim dependencies, boundaries, falsifiers, unresolved objections, cross-domain mappings, review changes and scoped graph metrics. Correct known CDCM workbook formula defects through tested calculations; do not blindly copy cached values. The backend's violation_density is per axiom, while one workbook measure is per scored cell: retain explicit denominators. Do not claim all advertised advanced metrics implemented merely because a heading exists.

### 4. Projection and API orchestration

Preserve all 21 projection choices: executive summary, ninth-grade reader, skeptic, formal, SEO, proof explorer, citation audit, literature comparison, contradiction pass, exact preservation, AI package, Substack, theorem extraction, graph nodes, Obsidian nodes, glossary, equation cards, audio script, TTS narration, video script and storyboard.

Allow one, several or all. Python performs local counts/hashes/joins/indexing/export; model calls generate source-grounded interpretations and adaptations. Preserve the exact original bytes separately; a summary is not lossless. Prefer station adapters to duplicate model clients. Use the existing API shortcut registry if present; otherwise import an explicit versioned mapping from the original pipeline, not guessed numeric routes.

Produce an API change matrix and exact revised prompts/JSON schemas: current station/path, current fields, missing fields, dependencies, local versus model computation, source-span rules, version compatibility and cost scope. Separate YouTube discovery, relevance and transcripts. Truncated/invalid output never becomes done. Citation/literature verification needs actual source lookup; theorem extraction needs separate Lean compilation; TTS/video/storyboard text is not produced media.

No paid calls during automated development. Add explicit bounded execution in the UI, saved submissions before network calls, receipts, usage where available and no automatic retry of ambiguous timeouts. Use mocks/local fixtures for development. User authorization of one call is not permission for fan-out or repeated retries.

### 5. Full Excel / HTML / FIS parity

Generate all three from the same validated snapshot. Excel is a complete analytical companion, with dashboard, papers, passages/atoms, ledger, constraints, cross-domain mapping, dependencies, objections/repair, media, processing status, metric dictionary/observations and provenance sheets. Provide filters, freeze panes, links, charts and transparent formulas/denominators. Every summary number must trace to source records. Link long Markdown sources rather than silently truncate into cells. Keep missing/inapplicable values distinguishable from measured zero.

FIS marks a task complete only from valid current receipts. A folder's existence or old API response is present_unverified. Processing done is separate from scientific verification, approval, canon and publication.

### 6. Review bridge

Use Plannotator through an external adapter first. Pilot Markdown and rendered HTML review without globally installing hooks or rewriting agent configuration. Save feedback with original source/version hash, exact target, author, timestamp and status. Connect substantive paper feedback to its AI Review Log using the project's protocol. Preserve earlier entries and actual David rulings. Never let approval of a plan imply canon approval of a paper.

Plannotator's Codex/native Windows automatic hooks may be experimental; manual launch/import is an acceptable initial working bridge, clearly labeled. Follow upstream testing requirements with a temporary PLANNOTATOR_DATA_DIR; do not touch a real Inbox or user configuration. Do not transmit private material using sharing features by default.

## Preservation and operating rules

Work on small copied fixtures until the integrated workflow is demonstrably correct. Do not connect, scan or mutate the live B_series corpus as an automatic acceptance step. Do not run imported APPLY_*, PATCH_*, backup/restore, overnight or deployment scripts merely because they exist. Every enabled mutating operation needs the shared actor/history, dry-run, never-overwrite behavior and recovery record. Never delete user files. Never infer canon or rewrite document identities. Source media stays with its paper; website-only artifacts and API/JSON/SQLite/logs stay on the configured Backside. Honor existing casing/locations instead of creating competing stores.

Use focused shared helpers; preserve licenses and upstream attribution. No production secrets in Git or output. No speculative settings/approval gates that obstruct ordinary local work. Respect existing author contributions and preserve useful code before replacing it.

## Validation and delivery

Run component checks relevant to changes, including Quantum tests, dashboard snapshot tests, registry pytest tests, projection tests, native plugin builds, navigation template tests and known-answer CDCM fixtures. Add meaningful integration fixtures for unchanged rescan, edited source, missing source, duplicate content at different paths, ID/name collisions, Unicode/UNC paths, malformed metadata, unresolved contradiction, missing review evidence and partial/truncated API response. Prove no source-byte changes and matching HTML/Excel/FIS counts. Test cold-start launch and a copied-vault UI flow; distinguish compile, fixture, browser and live-vault acceptance.

Deliver working code, schema/metric dictionary, station adapters/change matrix, exact prompts, integrated launcher, copied-fixture demonstration outputs, source/provenance receipts, concise user instructions and one PR. List missing external dependencies precisely; do not disguise absent integrations as done. Complete the local core flow instead of stopping at another design memo. Keep optional prototype/remote-service work separate from a verified core. Do not push secrets, deploy, merge or touch the live corpus to manufacture completion.
