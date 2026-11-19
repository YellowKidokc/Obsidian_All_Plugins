# One Obsidian repository, separate components

David's direction: collect the Obsidian tools in this repository, keep components separate, then integrate around a focused workflow. Additional components are expected; this is the first consolidation batch, not final replacement approval.

| Component | Repository location | Role | Verified now |
|---|---|---|---|
| Quantum Paper | apps/quantum | One original file with registry memberships, actions and movement history | 19 unit tests passed |
| Vault Operations Dashboard | apps/dashboard | Read-only folder snapshot and operational dashboard/tool references | 5 unit tests passed |
| Semantic AI | plugins/semantic-ai | Independent Obsidian classification/tagging plugin | Locked dependency install, TypeScript check and production build passed |
| Paper Projections | apps/paper-projections | 21 source-preserving adaptation/extraction/review workflows | 8 unit tests passed during its preceding import |
| FIS registry seed | apps/registry | Existing evidence-backed status gates and registry renderer | 6 pytest tests passed |

## Import provenance

See COMPONENT_IMPORTS_20261118.json for original paths, branches/commits, subtree import commits and source-blob verification. Imported code/history comes from local Git repositories. All 387 retained tracked source blobs matched their source revisions.

Quantum's original repository tracked .qp_state/registry.sqlite. Its history was filtered in an isolated temporary clone to remove .qp_state before import; original source commits are recorded but filtered commit IDs differ. The original repository was not modified. Dashboard and Semantic AI history was imported without filtering. Apparent API key values detected in the dashboard's example configurations were checked as placeholders.

No original source directories were deleted, moved, rewritten or repointed. No remote push has been performed. Collect the remaining components and verify the combined workflow before retiring duplicate originals.

## Current integration limits

These are separate imported components, not a fully merged application. Shared navigation, actors/history, identity adapters, station routing, SQLite/Excel/HTML/FIS records and canonical review interfaces remain implementation work. Semantic AI's build passing does not establish an installed-vault acceptance test or a live provider call. Legacy dashboard/projection snapshots remain reference-only until adopted.

Use the repository's rules for future implementation: preserve original Markdown, keep secrets and runtime registries out of Git, dry-run changes, log mutating actions and retain undo/provenance. No vault was connected and no paid API was called during this import.

## Reproduce local checks

Run each command from the indicated component directory:

- apps/quantum: python -m unittest discover -s tests -v
- apps/dashboard: python -m unittest discover -s tests -v
- plugins/semantic-ai: npm ci --ignore-scripts --no-audit --no-fund, then npm run build
- apps/paper-projections/BACKSIDE: python -m unittest -v test_projections.py
- repository root with pytest installed: python -m pytest apps/registry -q --basetemp .venv/test-runs/NEW_UNIQUE_DIRECTORY (create the parent first). An isolated temp root avoids this machine's inaccessible global pytest-current junction.

The build check restored the imported main.js bytes afterward so the source import stays exact. Node dependencies and the local Python test environment are ignored, not committed.


## Second collection batch

| Component | Location | Current role / evidence |
|---|---|---|
| Research Manager (DASHBOARD-Obsidian-HTML) | apps/research-manager | Full Python/PySide research manager, not merely HTML; 102 Python files parse. Further runtime acceptance remains separate. |
| AI-TAGER-OBS | legacy/ai-tagger-bundle | Prior Semantic AI bundle and taxonomy/prompt references; runtime data.json excluded; compiled JS syntax passes. |
| Dashboard Navigator | plugins/dashboard-navigator | Preferred in-Obsidian front end; TypeScript and production build pass. Pair with apps/dashboard operations through a shared adapter, not by discarding either project. |
| Navigation-Obsidian | templates/navigation | Five repaired Templater templates and CSS; 10 fixture tests pass; live Obsidian acceptance pending. |

Dashboard pairing direction from David: Dashboard Navigator supplies native vault navigation, stats and searches; apps/dashboard supplies read-only snapshots and operational actions. Shared scope/status/identity and action-history adapters remain to be built. No existing live vault or community-plugin settings were changed.
