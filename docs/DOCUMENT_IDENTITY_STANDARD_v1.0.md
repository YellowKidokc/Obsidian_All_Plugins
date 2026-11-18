# Document Identity Standard v1.0 (summary copy)

Theophysics Research Initiative. Authority: David Lowe. Date 2026-11-07.
Full text lives with David's governance documents; this copy holds the rules code must obey.

## The one rule
Every knowledge object gets ONE permanent identity. Everything else hangs off it.

## ID format: `SERIES.POSITION.SLUG`
- SERIES: 3–5 letter code from the series registry (MEQU, JREV, DLAY, LAND, ONES, DUAL…)
- POSITION: two digits, stable within the series
  - 00 index/governing · 01–79 principal works · 80–89 companions/addenda · 90–94 appendices/reference
  - 95 concordance · 96 glossary · 97 bibliography/source registry · 98 governance/rulings · 99 archive/supersession map
- SLUG: shortest distinctive title word, permanent after assignment
- Examples: `MEQU.04.AGAPE`, `JREV.02.WORLD`, `JREV.89.AUTHORITY`, `DLAY.05.WATER`

Assignment: registry-issued, never derived on the fly. The namer PROPOSES; the registry ASSIGNS after David's
approval. Renaming, moving, reformatting, revising never change the ID. Only identity displacement (central claim
materially changed, support becomes opposition, governing model replaced, works split) gets a new ID, linked with
`SUPERSEDED_BY` / `DERIVED_FROM`.

## Derived artifacts: `ID::role[::version|::date]`
Roles: source.markdown, source.html, render.blue, render.site, classify.104, classify.105, vector.chi,
vector.namer, metadata.frontmatter, metadata.sidecar, audit.structural, audit.lawyer, extract.claims,
extract.evidence, receipt.processing, receipt.move, formal.lean_stub, formal.lean_result.
Example: `DLAY.05.WATER::classify.105::v2`.

## Version identity
document_id, version_number, content_sha256, created_at, supersedes_version, revision_status.

## Three-address sidecar
- physical: current_home, proposed_home, move_authorized (only this address may propose a move)
- canonical: build, law_ids, epistemic_roles, canon_status, admission_authority (DAVID_ONLY), claims, evidence, kill_conditions
- navigation: series_id, series_position, subjects, people, worldviews, ten_law_emphasis, chi_primary/secondary, document_type, lifecycle
- lineage: created_at/by, revision_history, cross_references (target + relationship)

## Database tables
documents, versions, artifacts, runs, series (see full standard for columns).

## Safety rules
1. Never infer ADMITTED (David only). 2. Never overwrite an artifact; new version, new artifact_id.
3. Never change a document_id because the path changed. 4. Never reuse a displaced document_id.
5. Approval ledger before applying IDs to existing files. 6. Preserve old paths, hashes, names, lineage.
7. Every change reversible. 8. Start with sidecars; do not rename source files until proven.
9. The namer proposes, the registry assigns. 10. Exports must be understandable without the database.
