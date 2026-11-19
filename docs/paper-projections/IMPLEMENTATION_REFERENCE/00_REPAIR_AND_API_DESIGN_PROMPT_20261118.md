# IMPLEMENTATION PROMPT: repair Breakthrough Vault and unify Paper Intelligence

Prepared November 18, 2026. This is a repair specification, not a claim that the toolkit has been repaired.

## Mission
Build on the existing system to produce a reliable paper/series research instrument. Excel must have the analytical depth of HTML. SQLite, HTML, Excel and FIS must consume the same versioned records. Inspect existing code and local instructions; check shared ownership before edits. Implement and verify a small local pilot in a separate working copy. Preserve original manuscripts, databases, historical outputs and reviewer decisions. Do not run paid APIs as part of this design/pilot.

## Exact discovery perimeter
Start in this toolkit, especially Scripts/vault_refresh.py, auto_linker.py, validation_scaffold.py, duplicate_finder.py, cooccurrence_analyzer.py, concept_hub_generator.py, paper_compare.py, toolkit_manager.py and config.yaml.
Outside this toolkit, inside 02_Python_Engine:
- scripts/dashboard_generator.py and chi_computation.py
- docs/ANALYTICS_ARCHITECTURE.md, UNIFIED_MEASUREMENT_MATRIX.md and COHERENCE_ANALYSIS_OVERVIEW.md
- theophysics_complete SQL schemas, database files, variable maps, integration guides and sync_to_postgres.py. Inspect databases read-only; historical documentation counts require verification.
Also inspect the parent 04_ANALYTICS entry points run_series_analytics.py and run_full_series_suite.py and its 03_Dashboards, 04_Custom_Modules, Data_Analytics and Obsidian-Definitions-Manager for reusable parts. These are discovery candidates, not approved production dependencies.
At the engine root inspect 00_ORCHESTRATOR/run_pipeline.py, 03_THEOPHYSICS_METRICS/theophysics_scorer.py, 06_TRUTH_ENGINE and OUTPUT/Convergence_1_Story_Run.
CDCM reference: \\192.168.2.50\h_hp\Desktop\Folders\Folders\Master EXCEL (1)\CDCM.xlsx.
Inventory: .BACKSIDE/REPAIR_DESIGN_20261118/source_inventory.json. This covers 02_Python_Engine, not every surrounding folder. AST parsing is syntax inspection only.

## Confirmed problems to repair
1. vault_refresh.add_concepts increments global totals every scan. Derive totals from per-note occurrences or transactional deltas. Identical rescans must preserve counts.
2. Fallback note IDs strip/truncate path segments; distinct names can collide and renaming changes identity. Preserve explicit IDs; detect duplicate IDs; use a persistent identity/path-history registry. Hashes identify source versions, not all identical copies as one paper.
3. Exclude generated hubs/reports, .BACKSIDE and .obsidian from source scans. Track missing sources without deleting history. Verify config consumption: current config references an old user's OneDrive; toolkit_manager assumes an obsolete Global_Analytics layout.
4. auto_linker promotes tag overlap to supports and title cues to contradicts, with reciprocal links. These are candidate discovery signals only. Reviewed support/contradiction needs proposition-level source spans, rationale and direction. Support is not automatically reciprocal.
5. Regeneration deletes all edges/metrics. Preserve reviewed edges and run history; replace only run-owned generated partitions transactionally.
6. Optional auto-link writing appends repeated blocks into source notes. Default to generated companion notes. Any future source-write mode must be explicit, idempotent and reversible.
7. validation_scaffold SIS is tag-neighbor Jaccard similarity, LCS is an edge-count ratio with a perfect default when no edges exist, and SRI is a support/contradiction ratio rather than tracked repair. Retain legacy values with honest proxy labels. Unassessed logical consistency must be null/unassessed. Real repair needs issue -> change -> retest -> receipt records.
8. All-pairs linking needs candidate retrieval/blocking for scale. Report actual scope, candidates and exclusions.
9. Master Equation meanings differ across historical integration guides and the current engine. Version the variable dictionary and explicitly map legacy meanings. Preserve unresolved conflicts. Also distinguish differing fruit vocabularies.
10. CDCM's ideas are useful but its formulas need correction: Advanced_Metrics!B5 multiplies coverage booleans; Global_Metrics!B10 checks only one constraint column; XDTI_Score uses SUMIF on text yes values. Review all formulas/denominators and validate with known-answer fixtures. Several advanced metrics are instructions, not implemented computations.

## Shared records and epistemic boundaries
Model series -> paper -> version -> passage -> atom, plus typed ledger items: claims, premises, derivations, proofs, evidence, objections, boundaries, counterexamples and audits.
Declared theological commitments are allowed. Explicitly record derived consequences, added premises, empirical evidence, correspondences and proposals. Formal validity, semantic similarity, evidence and David's canon decisions remain separate fields.
Define JSON schemas first, then SQLite import and exporters. Do not reconstruct primary data by scraping HTML.
Entities: series, papers, versions, passages, atoms, ledger_items, relationships, media, metric_definitions, metric_observations, runs, artifacts, issues, reviews and processing_tasks.
Metric observations include entity_id, metric_id, definition_version, value, unit/scale, numerator, denominator, method, assessment_status, source_refs, source_hash, run_id and observed_at. Distinguish zero, unknown, not_applicable, failed and stale.
Relationships include source/target IDs, direction, type, candidate/review status, exact evidence spans, rationale and origin.
Runs include station alias, input hashes, schema/prompt/engine versions, model if used, timestamps, output hashes, validation, errors and cost when available. Never store credentials in these records.

## Required analytical coverage
Series overview: all papers and distinct contributions; precursor/derivation links; series summaries; named TTS, debate, deep dive, critique, podcasts, video, images and exports; ownership, completeness, issues and next actions.
Paper view: readable source, how/why questions, asks/answers/does-not-answer, standalone passages, short sentence, original/high-school/PhD versions, atoms, evidence ledger, MTL, Master Equation mappings and API progress.
Locate the authoritative Master Equation Namer and preserve its paragraph-level naming and scoring rules. Do not invent replacement keyword rules. Preserve the paper -> sentence -> series paragraph compression and source retrieval index, including failures and the build/test pivot.
Text/academic metrics: words, sentences, paragraphs, readability, vocabulary, citations/density, theory references and source diversity, with methods and denominators.
CDCM-inspired review: nine-constraint matrix with explicit rubrics and evidence; weaknesses, dependencies, boundaries, falsifiers, unresolved objections, cross-domain mappings and translation loss.
Graph diagnostics: typed neighbors, components, clusters and centrality with algorithm/scope. Centrality is not truth.
Sensitivity: explicit weight/premise variations with changed outcomes. Rival theories use matched rubrics and disclosed missingness.
YouTube discovery, relevance review and transcript acquisition remain separate tasks.
Processing/FIS distinguishes done, present_unverified, missing, broken, stale, conflict, blocked and not_applicable. Done requires valid current receipts and is separate from argument approval.

## Excel/HTML parity
Build a full Excel companion: dashboard, papers, passages/atoms, ledger, constraints, cross-domain mappings, dependencies, objections/repair, media, processing matrix, metric dictionary, raw observations and run/provenance sheets. Include tables, filters, frozen panes, internal/source hyperlinks, charts, documented formulas and populated weakness/comparison/sensitivity views.
Every dashboard number must trace to its underlying records. Exporters must match for the same snapshot. Link long Markdown sources rather than silently truncating them in cells. No fabricated statistics or unsupported blanket quality grades.

## API changes
Produce a station-by-station matrix: current alias and path, current fields, missing fields, exact JSON schema, source-span rules, locally computed fields, model judgments, dependencies, compatibility adapter and bounded cost scope.
Reuse the existing shortcut registry and relevant CPEL, AT, ARG, LN, DA, OA.MTL, DA.MEQ, YT and FIS stations. Local counts/hashes/joins/totals/graphs remain local. Models supply source-grounded summaries, questions, candidate mappings, review assessments and visualization proposals.
Deliver exact revised prompts and schemas before API execution. Validate passage IDs, literal quotes, required keys, scope and truncation. Invalid/incomplete output cannot be marked done. Preserve legacy artifacts and label their provenance. No corpus-wide calls, retries or new dependencies merely to finish a design task.

## Folder organization and acceptance
Offer a clean entry point with batch launchers, INBOX, OUTBOX and .BACKSIDE; implementation/JSON/SQLite/logs go on .BACKSIDE. Keep dossiers, drafts and human navigation visible in Obsidian. Do not silently rearrange existing files. Any later migration needs source/destination mapping and an undo path.
Pilot copied sources only. Verify: unchanged rescan, edit, missing source, identical copies at distinct paths, collision-prone names, malformed metadata, Unicode/NAS paths, unresolved contradiction and no assessed edges. Require stable identities/counts, unchanged source hashes, preserved reviewed history, honest unknown values and matching Excel/HTML/FIS totals. Test real calculations against expected values.

Deliver: reuse/adapt/legacy/blocked inventory; repair implementation and tested pilot; schemas/metric dictionary/version mappings; API change matrix and exact prompts; matched exports and receipts; known limits and remaining work. Do not report all functionality repaired from a syntax check.
