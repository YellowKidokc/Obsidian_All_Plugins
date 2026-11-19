# Workbench contract and integration status

The workbench indexes one selected root. SQLite stores a history of inventory snapshots and append-only research records. The FIS export contains the current inventory and the research record history. Exact source bytes are addressed by SHA-256. Source content hashes may be shared across distinct papers. The stored source coordinate is a one-based, inclusive line range. The schema and prompt versions are local to the workbench. A frontmatter `document_id` is an observed declaration. Duplicate or malformed declarations are reported.

The [record schema](../apps/workbench/record.schema.json) documents provenance and shared record kinds. [Projection responses](../apps/workbench/projection-result.schema.json) go through the retained projection validator plus checks for incomplete responses, item text, and optional literal quotes. Import records processing success with a receipt and output hash. Missing or changed artifacts become broken, and source changes make prior processing stale after rescan. FIS scope here is the workbench projection pipeline. The existing registry scanner and its broader FIS profile remain standalone.

The metric dictionary in `index.py` describes structural metrics. Counts include source frontmatter and code because they measure the decoded input, not edited prose. CDCM uses separately named violation densities. The spreadsheet contains the measured values, numerators, denominators and methods. Exported passages cite line ranges and link to copies through the Papers sheet. The HTML dashboard and FIS JSON use the same totals. FIS JSON holds complete records alongside compact Excel previews.

## Station boundaries

| Station | Current route and output | Requirement before enabling execution |
| --- | --- | --- |
| Workbench projections | Imported `projections.CATALOG` and `prompt_for` produce exact task prompts with source hash, numbered text, item IDs and line spans. Local preservation and packaging record content hashes. | Offline only. Provider, model, budget, current station schema, and authorization must be supplied for a remote execution integration. |
| CPEL, AT, ARG, LN, DA | No verified shortcut mapping for these aliases in the selected checkout. Workbench stores manually sourced assumptions, claims, proofs, definitions, objections and candidate relationships. | Original pipeline shortcut registry and station field definitions. Lean results need compiler receipts. |
| OA.MTL | Local MTL adapter uses a supplied CSV and stores its hash. | Authoritative MATH_TRANSLATION_TABLE CSV for real terms. |
| DA.MEQ | Blocked. Historical equation map is retained as a reference. | Authoritative Master Equation Namer implementation, paragraph profiles, scoring fixtures for the name/1-to-3 distinctions, and version mapping. |
| YouTube discovery | Blocked. | Original route, account or API, result IDs and bounded retrieval. |
| YouTube relevance | Blocked. | Discovery result IDs and a source question, with a separate relevance decision. |
| YouTube transcripts | Blocked. | Authorized transcript input and segment timestamps. |
| FIS | Current-source receipt and response hashes determine workbench processing state. | Broader registry completion profiles and artifact reconciliation remain separate. |

Citation or literature verification requires real source retrieval. The theorem projection can extract candidates. Narration, video and storyboard projections produce text. Imported results remain unreviewed regardless of task completion.

Historical dictionaries stay independent. The Research Manager fruits dictionary has SHA-256 `d919a831be0f338289ccd8744234cf5553ea986b3de333f0f54440c146181980`. The `theophysics_complete/master_equation_map.json` reference has SHA-256 `65c8a42aef39ddd612cae3a3822f565733d2db0a5cc8509db501a6997191f378`. Neither establishes an authoritative Namer score.

## Remaining implementation

The pilot does not activate the ingest engine, migrate the historical analytics library or edit CDCM workbooks. It does not provide full comparison, sensitivity, graph clustering or centrality, publication FIS profiles, API shortcut routing, or the original Namer pipeline. Historical SIS/LCS/SRI outputs remain in their original locations. Obsidian desktop, real UNC/NAS behavior, pinned Plannotator UI, and the Windows menu need runtime acceptance. No live vault, paid model calls or private sharing are part of the test workflow.

## Verification

The copied-fixture suite covers idempotent indexing, UTF-8 paths, malformed and duplicate declarations, distinct identities for identical bytes, a registered Quantum move, changed or missing files, source preservation, review import, incomplete projections and broken receipts. It verifies directed graph scope, known-answer CDCM denominators, and matching HTML, Excel and FIS totals. Dashboard Navigator, Semantic AI and Second Brain Black Hole built from their locked dependencies. The Chromium fixture followed series, folder, paper and ledger links to an exact source span and prepared a projection through the browser.
