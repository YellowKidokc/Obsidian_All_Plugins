# Existing analytics integration handoff

These six source locations are now indexed in this app. This is a reference/snapshot library, not installed or tested execution of legacy tools. Source originals are unchanged. The inventory is bounded; no claim of exhaustive archive review is made.

## Reuse map
- theophysics_complete -> versioned framework/variable ontology, relational schema design, gap and integration references. breakthrough_vault_schema.sql contains PostgreSQL CREATE SCHEMA, SET search_path and array types; do not run directly as a SQLite migration. Database files remain at their original paths and were not opened or copied in this pass.
- Data_Analytics -> extraction, linking, paper-management and utility candidates. Snapshots exclude nested Data/Source collections and deep trees to avoid ingesting manuscript collections or repeated backups. Inspect individual dependencies and source-writing behavior before use.
- ARCHIVE -> architecture rationale and provenance only. The directory contains import backups and conflict/difference collections; retain that historical distinction. Do not run or promote archive scripts automatically.
- 04_Custom_Modules -> optional symbolic model/equation-card adapter. engine.py imports SymPy and falls back to an empty UNSOLVED_PROBLEMS registry if problems is absent. README advertises a different analytics suite/entry points. Resolve that mismatch and required definitions. Symbolic hypotheses are not compiled proofs or empirical validation.
- 03_Dashboards -> dashboard navigation/layout references. Analytics_Hub contains a hypothetical module link and obsolete Local_Analytics locations. Data_Extraction_Dashboard points at an old Global_Analytics path and attempts to list Python through Dataview; establish a real file inventory rather than assuming non-note files are indexed.
- 01_Native_Tools -> Obsidian-only live overview, tags and tasks. These require Dataview and appropriately scoped vault paths. Check the word-count field and query syntax in the actual vault; do not assert live operation from reading a template.

## Implementing adapters
Use the existing 00_REPAIR_AND_API_DESIGN_PROMPT_20261118.md in BreakthroughVaultToolkit_v2 as the broader repair specification. Keep one shared source/version/metric contract. Do not add these as 6 more generic API projections.
Python adapters should handle counts, indexing, deduplication candidates, graph construction and export. Model stations handle source-grounded extraction, adaptations and proposed relationships. Obsidian is a view of those records. Excel and HTML should expose the same snapshot and definitions.
Every candidate adapter must declare inputs, outputs, source/version hashes, dependencies, metric meanings, read/write behavior and test receipts. Default source reads only; outputs stay under the run's backend. Reconcile historical Master Equation variable meanings before joining records.
Verify on copied fixtures before enabling any legacy script. Add application buttons only when an adapter actually works; until then these files remain reference material. Do not treat existence in this library as task completion, verified analysis, proof or canon approval.

## Scope evidence
registry.json records source paths, bounded scan depth, file sizes and hashes. SNAPSHOTS holds byte-verified copies of selected text/code files. Copy verification is not runtime verification. This pass made no paid API calls and executed no legacy tools.


## Folder navigation addition

See FOLDER_NAVIGATION_SPEC.md for David's clickable folder/subfolder/file summaries requirement and the two newly preserved root navigation references.
