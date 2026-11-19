# Paper projection workbench import

Imported at David's request on 2026-11-18 into apps/paper-projections. This is a source snapshot import, not a subtree of a separate git project.

Launch: apps/paper-projections/START_PROJECTIONS.bat.
Local tests: python -m unittest discover -s apps/paper-projections/BACKSIDE -p test_projections.py -v

START_HERE_CODEX.md describes implemented behavior and outstanding adapters. Its original package-relative PAPER_PROJECTIONS path now means apps/paper-projections. IMPLEMENTATION_REFERENCE lives here under docs/paper-projections. The original verified handoff ZIP is also here.

This is a standalone workbench, not an Obsidian plugin or completed integration. Source/JSON/Markdown outputs and explicit provider calls work; Quantum history hooks, shared actor helpers, station routing, SQLite/Excel/FIS adapters and recursive navigation still need implementation under the repository's rules. Legacy analytics snapshots are references only. Do not execute the README's entire consolidation prompt merely to inspect this import.

No paid calls, git commit, push or publication were performed by this import. Runtime source/results are excluded by the app-local .gitignore. Original NAS files remain unchanged.
