# Codex handoff: Paper Projection Architecture

David's request: one preserved paper should support many projections and analyses. Python manages source/version identity, processing, validation and exports. Model API stations produce source-grounded adaptations and review proposals. Existing tools should be reused after inspection.

## Start here
1. Read PAPER_PROJECTIONS/READ_ME_FIRST.md.
2. Launch PAPER_PROJECTIONS/START_PROJECTIONS.bat on Windows with Python 3.10+ and Tkinter, or inspect BACKSIDE/projections.py.
3. Run: python -m unittest discover -s PAPER_PROJECTIONS/BACKSIDE -p test_projections.py -v
4. Open PAPER_PROJECTIONS/OPEN_ANALYTICS_LIBRARY.bat. Read BACKSIDE/EXISTING_ANALYTICS_LIBRARY/INTEGRATION_HANDOFF.md and FOLDER_NAVIGATION_SPEC.md.
5. Read IMPLEMENTATION_REFERENCE/00_REPAIR_AND_API_DESIGN_PROMPT_20261118.md for the larger repair/data/API specification.

## Implemented and checked
21 selectable projection definitions; UTF-8 Markdown/text source input; exact original-byte preservation with SHA-256; numbered source lines; local prompt export; local AI handoff ZIP; JSON result import; readable Markdown plus JSON results; status dashboard; explicit DeepSeek execution with environment-held key and model/output-token selection; saved submission before request; raw response/usage receipts; no automatic retries; stop after current call; output structural and source-line-bound validation. No paid calls were made while building or packaging.
55 selected analytics-reference snapshots from seven groups, including the later folder-navigation addition. They are source copies for inspection, not enabled legacy executable adapters. Consult registry.json for actual counts and scope.

## What is not yet implemented
No existing-station routing, full SQLite/Excel/FIS integration, recursive navigation generator, live vault freshness scanner, authentic claim-support verification, external citation/literature lookup, Lean compiler run, audio synthesis, image generation, video rendering or publication. Markdown/HTML adaptation output does not imply those production steps happened. UI construction and backend tests were checked; full mouse-driven acceptance and live paid-provider testing remain open.

## Next bounded implementation
First inspect this repository's instructions and ownership; do not overwrite other agents' work. Stabilize versioned records/schemas and the API output matrix before broad rewrites. Start a small copied-source pilot that unifies paper/source/passage IDs, metric definitions and observations, projection results, media and processing receipts. Then add adapters for existing API aliases, SQLite ingestion, matching Excel/HTML/FIS exports, and recursive folder summaries in visible Obsidian Markdown plus HTML. Follow the detailed acceptance checks in the repair prompt. Each layer should pass its local fixture tests before corpus rollout.

## Preserve key distinctions
An exact source snapshot is lossless; a summary is not. Generated, reviewed, compiled, empirically supported and canonical are distinct statuses. Declared theological commitments are legitimate inputs; preserve what was assumed versus derived. Keyword similarity and graph centrality are not proof or canon. Grace/love/truth and historical Master Equation meanings must not be silently merged across dictionary versions.

## Files and portability
The runnable app uses Python's standard library; no pip packages are required. Legacy snapshots may require other packages, old paths or external services and must not be executed blindly. Original NAS paths in reference records are provenance; not all will resolve on another computer. No source database binaries, corpus papers, live run results, API keys or environments are included. Empty INBOX/OUTBOX folders are intentionally included. Source originals were not moved or modified.

## Repository work
Repository destination was not specified at packaging time. This ZIP is an unpackable handoff, not a git commit or push. Once the destination is supplied, inspect it and place the app/reference files in a suitable new subtree without changing unrelated content. No deployment or remote publication is implied.
