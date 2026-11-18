# Series Folder Structure Standard — Draft

Status: PILOT STANDARD — not a canon or registry ruling  
Authority for permanent document IDs and canon admission: David Lowe only

## Goal

Keep each series readable as one visible ordered list while retaining HTML, web assets, metadata, receipts, and competing render versions on a hidden backside.

## Standard Layout

```text
SERIES_NAME/
  00_SERIES_INDEX.md
  01_PAPER_TITLE/
  02_PAPER_TITLE/
  ...
  .backside/
    01_PAPER_TITLE/
      article.html
      article.site.html
      assets/
      metadata.json
      receipts/
    02_PAPER_TITLE/
      ...
```

The visible series root should not accumulate separate HTML, media, metadata, audit, and version trees. Those technical artifacts belong under the single `.backside` folder.

## Media Rule

Media is placed according to its role:

1. Original evidence, source diagrams, scans, and images required to understand the Markdown or paper remain with that paper on the visible side.
2. Web-only or optimized derivatives—WebP renditions, thumbnails, social cards, CSS, JavaScript, and player assets—belong in that paper's `.backside` mirror under `assets/`.
3. The source media object and its web derivative are connected through hashes and lineage. They are not treated as two unrelated originals.
4. Do not duplicate original media merely for organizational symmetry. Create a derivative only when a render or publication workflow requires one.

## Version Rule

Keep render versions in the same backside paper folder using descriptive filenames:

```text
article.blue.v1.html
article.blue.v2.html
article.site.v1.html
```

Do not create additional version folders unless a paper has enough artifacts that filenames become unmanageable.

## Identity and Safety

- Preserve every original filename, path, hash, and move receipt.
- Do not assign or alter a permanent document ID without the approval ledger and David's approval.
- Do not infer canon admission.
- Do not overwrite competing HTML or media; retain each as a separately named artifact.
- Moving or reformatting does not change document identity.
- If the central claim materially changes, hold for an identity-displacement ruling.
- The visible Markdown/source side remains authoritative for authoring; `.backside` stores derived and publication artifacts.

## Matching Order

For each incoming HTML artifact:

1. Approved `document_id`, when present.
2. Exact source hash or recorded lineage.
3. Exact normalized title and series position.
4. Strong content match between HTML text and Markdown text.
5. Filename-only similarity is a proposal, never a final identity match.
6. Unresolved matches go to HOLD and are not inserted into a paper folder.

## Pilot Gate

Apply this structure to one representative series first. Confirm:

- Obsidian ignores `.backside` as expected.
- HTML still resolves its assets.
- Markdown links and embeds remain valid.
- Competing versions remain distinguishable.
- The structure is understandable without a database.

Only after the pilot passes should the layout be copied across all series.
