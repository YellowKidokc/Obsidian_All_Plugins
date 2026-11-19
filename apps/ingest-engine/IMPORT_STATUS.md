# Ingest engine: packaged offline preview

Source: H:/Documents/OBS-Plugin-Final-Codex, YellowKidokc/OBS-Plugin-Final-Codex. Imported with history; originals unchanged.

Despite the README's plugin-oriented specification, the actual implementation is a Python/PostgreSQL ingestion engine for Excel, HTML tables and Markdown, with source attribution and definition records. There is no built Obsidian frontend here.

12 Python files pass syntax parsing. Actual inspection found:
- config/settings.py imports BaseSettings from pydantic, but requirements declare Pydantic >=2.5.2; importing configuration raises PydanticImportError in the current environment. Migrate settings/env aliases properly or explicitly choose a supported compatibility layer.
- setup.py discovers packages under src, but orchestrator.py is a top-level module and is not declared in py_modules. The console entry point therefore needs a packaging correction and clean-environment install test. config is also outside the declared package root.
- The schema import emits a warning about the reserved SQLAlchemy metadata attribute. Review compatibility without silently changing a real database schema.
- python-frontmatter is missing in the current global environment. Dependencies belong in a dedicated environment, followed by offline parsing fixtures and explicit database integration tests.

Keep this as a candidate ETL/definition adapter, not a finished plugin or verified database synchronization path. No ingestion against user files or production database was run. Do not confuse its source enums/IDs with canon or shared document-identity authority.

## Workbench integration

The workbench pilot repairs the installed CLI, updates settings to Pydantic 2, and preserves the existing SQL column name through a compatible ORM attribute. A clean installation ran the CLI and parsed copied Markdown, HTML and Excel inputs without opening a database connection. Use `theophysics-ingest PATH --preview` or the workbench's `preview-ingest` command. PostgreSQL ingestion remains outside the workbench and requires separate runtime validation.
