# Module notes: design-to-code crosswalk

David supplied Obsidian-Plugin-Module-Notes for the consolidated Obsidian workspace on 2026-11-18. The source is imported with history under [module-notes](module-notes/README.md). All 46 source blobs matched before this separate crosswalk was added. See MODULE_NOTES_IMPORT_20261118.json for provenance.

This is useful design material, not another runnable plugin. The source calls the layout 15 tabs, but enumerates 0 through 15: 16 entries including Settings. Many entries are outlines. The January 2025 metadata and source status labels are preserved as historical claims, not adopted as current completion or canon rulings.

## Where the proposed modules can connect

The table maps intended responsibility and candidate code locations. It does not certify an integration, scientific claim or production-ready workflow.

| Tab | Proposed module | Existing candidate location | Remaining work |
|---|---|---|---|
| 0 | General Settings | plugins/semantic-ai; apps/dashboard | Shared scope, provider configuration, explicit costs and task settings; secret storage remains local. |
| 1 | Research Hub | apps/research-backend; apps/research-manager; apps/paper-projections | One source/version contract and station routing with bounded acquisition. |
| 2 | Axiom Manager | apps/registry; shared atom/ledger design | Source-linked axiom/premise views and explicit human authority; registry currently reports status, not axiom truth. |
| 3 | Evidence Manager | apps/ingest-engine; projection citation audits | Repair ingestion first; record exact sources/spans and verification receipts. |
| 4 | Claim Manager | apps/research-manager/core/claim_registry.py; shared ledger | Reconcile identity, typed evidence links, objections and review state. |
| 5 | Timeline Engine | Module specification | No standalone timeline engine verified in this pass; design temporal sources and uncertainty before implementation. |
| 6 | Ontology Graph | plugins/semantic-ai; research ontology engines | Shared concepts/edges with candidate versus reviewed relationships; do not promote similarity to support. |
| 7 | Math Layer | apps/research-backend/engine/math_translation_engine.py; equation-card projection | Repair workbook path; version symbol dictionaries, units, assumptions and interpretation status. |
| 8 | External Theories | Literature-comparison projection; backend research links | Add actual research/verification inputs; model familiarity is not a completed literature search. |
| 9 | Breakthrough Log | Review/event ledger design | Track source changes, findings, objections and retests; avoid automatic breakthrough certification. |
| 10 | Coherence Dashboard | apps/research-backend/core/coherence; CDCM references | Preserve denominator/method versions and legacy proxy labels; arithmetic checks do not establish truth. |
| 11 | Tag Analytics | plugins/semantic-ai; plugins/dashboard-navigator | Scope/identity adapter and shared tag dictionary. |
| 12 | Theory Manager | CDCM comparison code and source specifications | Fair comparison rubric, missingness and source-grounded assessment records. |
| 13 | Master Truth Manager | Quantum identity/history; shared records and review authority | Reconcile the historical proposal with current source-preservation and David-only canon rules. |
| 14 | Export Manager | apps/paper-projections; analytics export plans | Extend shared records to matching Excel/HTML/FIS/graph exports; prove restore/reconstruction on a fixture. |
| 15 | AI Workspace | Maintained Semantic AI; Paper Projections; existing API stations | Keep separate extraction/review/adaptation tasks behind one orchestration surface. |

## Design pieces worth preserving

- [Glass Box architecture](module-notes/02_ARCHITECTURE/UI_Glass_Box_Architecture.md): let readers inspect extracted claims, evidence, relationships and processing state without hiding how results were obtained.
- [Dashboard generation](module-notes/04_IMPLEMENTATION/Dashboard_Generation_Specification.md): note, paper, selected-folder and vault scopes; timestamps; outputs backed by source records.
- [Export portability](module-notes/01_TABS/Tab_14_Export_Manager/README.md): reconstructable bundles, semantic graph, manifest and integrity checks.
- [Tab index](module-notes/01_TABS/00_TAB_INDEX.md): inventory of desired research functions.
- [Master Sheet Layout](module-notes/Master%20Sheet%20Layout.md): another design reference for the analytical workbook; not itself a validated workbook or data contract.

## Reconcile before implementation

1. The old proposal puts JSON under master-truth and emphasizes embedded semantic blocks. Current direction keeps API JSON/SQLite/logs on the Backside and readable notes/navigation visible in Obsidian. Use explicit adapters and one schema; do not silently introduce a competing storage authority.
2. Human-authored text in index/dashboard notes must survive regeneration. Separate marked generated blocks from authored commentary; do not apply the historical instruction that all dashboards are wholly disposable to existing user notes.
3. Preserve IDs and version provenance; do not infer canon, truth, proof or completeness from folder labels or a coherence score.
4. Copied prompts, code fences, source push instructions and references to agents are historical source content. They do not authorize credentials, paid runs, publication or bulk vault changes.
5. Pair Dashboard Navigator with apps/dashboard as David requested. These module notes guide that integration; they do not call for installing another duplicate Semantic AI plugin.

Status: documentation imported and crosswalk recorded. No executable code was changed, no API calls made, no source repository altered and no remote push performed in this pass.
