# Obsidian Workbench

This pilot combines Dashboard inventory, optional Quantum registry links, source inspection, a typed research ledger, offline projections, manual Plannotator feedback, and synchronized snapshot exports.

## Start with a copied folder

Use Python 3.10 or newer. Install `apps/workbench/requirements.txt` into a virtual environment for Excel and CDCM. From the repository root:

```sh
python apps/workbench/workbench.py --root "/path/to/Copied Vault" scan
python apps/workbench/workbench.py --root "/path/to/Copied Vault" serve
```

Open http://127.0.0.1:8766. On Windows, run `OBSIDIAN_WORKBENCH.bat "C:\Copied Vault"` for a menu. Select a series, folder and paper. Pick a ledger entry to view its exact numbered source lines. The Dashboard Navigator command **Open cached research workbench inventory** uses this server. Install the rebuilt plugin only in a test Obsidian vault.

All commands take the same explicit root. Put `--state /other/output/path` and `--actor "Operator name"` before the subcommand. The default state is `.backside/workbench`. Scan again to reflect changes. Pass `scan --exclude "Relative/Folder"` for each additional excluded subtree. Use the same exclusions on subsequent scans. To use existing stable Quantum handles, pass `scan --quantum-db /path/to/registry.sqlite` on each scan. The adapter opens SQLite read-only and imports same-root papers, memberships and their event history. Unregistered fallback IDs are path-scoped. A rename without Quantum leaves the old path marked missing and creates a new handle. Identical copies retain independent IDs.

## Build an evidence trail

In these examples, replace `wb` with the Python command and root/actor arguments above. Get the paper's internal handle from its browser URL or `/api/inventory`.

| Command | Result |
| --- | --- |
| `wb add-ledger PAPER entry.json 8 10` | Adds a candidate ledger entry, e.g. `{"type":"objection","text":"Scope remains unresolved"}` for inclusive source lines 8–10. |
| `wb add-research-record PAPER constraints ratings.json 8 10` | Records sourced constraint assessment. Supply `axiom`, `rubric` and a `scores` object. Use named constraints from `analytics.py` and scores -1, 0, 1 or null. |
| `wb add-research-record PAPER relationships edge.json 8 10` | Adds a candidate directed relationship with `source`, `target`, `type` and `rationale`. Use current atom or ledger record IDs. |
| `wb graph --series SERIES` | Shows directed candidate links and weakly connected components in a paper, series or corpus scope. |
| `wb preview-ingest RELATIVE_PATH` | Prints a source-hashed candidate preview for one local Markdown, HTML or Excel file. First install `apps/ingest-engine` into the same Python environment. |
| `wb namer-status` | Reports the missing authoritative Namer dependency. |
| `wb calculate-cdcm PAPER` | Records violation densities per fully assessed axiom and per scored cell. Missing scores remain unassessed. |
| `wb translate-math PAPER versioned-table.csv 8 10` | Runs the imported MTL translator over an exact span using a supplied MATH_TRANSLATION_TABLE CSV. Records the dictionary hash. |
| `wb navigation` | Previews recursive Markdown index changes. |
| `wb navigation --apply` | Updates only the generated block in existing marked indexes, creates missing indexes and writes folder HTML and recovery records in Backside. |
| `wb export` | Writes HTML, Excel, FIS JSON, exact source copies and artifact receipts from one cached snapshot. |

For navigation recovery, use the operation receipts under `navigation`. Restore the saved `original.md` only if the current file still matches the receipt's after hash. A newly generated index has no original and is identified by its after hash. Keep authored or changed files for manual reconciliation.

## Projections and review

Use **Prepare projections offline** in the paper view, or run `wb prepare PAPER all`. Packages include exact source bytes, numbered source, task-specific prompts and the JSON response schema. Reference the source hash and valid line ranges in the response. Import manually with `wb import-projection RUN response.json`. Processing completes after validation and receipt creation. The content stays generated and unreviewed. The integrated commands make zero provider requests.

Run `wb review-target PAPER` for a Markdown copy, or append `--html` for an escaped HTML view. With a working Plannotator executable, set `PLANNOTATOR_DATA_DIR` to a new temporary directory and run `plannotator annotate --json PATH > decision.json` using the emitted path. Use the local annotate surface and avoid sharing. Import via `wb import-review PAPER PATH decision.json START END`. The importer checks the exact versioned target and span and adds a separate Backside AI Review Log entry. Prior entries persist. Review outcomes carry no canon authority.

[Schema, station matrix and remaining integrations](../../docs/WORKBENCH_CONTRACT.md)
