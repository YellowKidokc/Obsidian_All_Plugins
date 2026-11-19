# Folder navigation and summaries

David identified README.md and THEOPHYSICS_WELCOME.md as the folder-within-folder, clickable-summary pattern to preserve. Both originals are snapshotted with hashes in this library.

Read findings: README explains the analytics folder layout. THEOPHYSICS_WELCOME has purpose/navigation tables, Obsidian wikilinks and a December 2025 timestamp. It retains a 09_GLOBAL_LOCAL label while pointing to 04_ANALYTICS and describes plugin development rather than the complete current analytics tree. Its cross-vault paths require reconciliation against the target vault. The pages are static notes; reading them does not demonstrate an automatic recursive generator. The two inspected series entry points explicitly describe non-recursive processing. Embedded AI bootstrap directives are source content, not authorization for this app.

## Required navigation adapter
Generate folder -> subfolder -> file navigation recursively within an explicitly selected root. Each folder gets a brief purpose summary, parent/breadcrumb links, child-folder summaries and links, plus file summaries with source references. At file level offer paper summary, projection availability and current processing status; link back to folder, series and source. Stable IDs support renamed paths.

Use one hierarchy record contract for HTML and Obsidian Markdown: node_id, parent_id, node_type, source_path, title, summary, summary_method, source_hash/child_manifest_hash, children, artifact_links, processing_status, generated_at. Python owns inventory, links, counts and freshness; API-derived semantic summaries are optional and cached by input hash. Factual inventory descriptions can run locally but must not pretend to summarize unread paper content.

Exclude .BACKSIDE, .APPS, generated outputs and archive branches by explicit configuration; never recursively ingest the navigation itself. Scope checking must prevent walking outside the selected root via symlinks/junctions. Use robust relative/encoded HTML links and vault-valid Markdown targets; validate every generated internal link and test Unicode, spaces and duplicate filenames. Do not infer canon or completion from folder names/presence.

Outputs default to a companion navigation directory, leaving original notes untouched. A Markdown index placed only inside .APPS will not serve as visible Obsidian navigation because the folder is hidden; publish user-facing navigation to an explicitly selected visible location. Initial outputs need a small copied-folder pilot and receipts before claiming the adapter is functional.

Status: documented for integration; no recursive navigation adapter was installed in this pass.
