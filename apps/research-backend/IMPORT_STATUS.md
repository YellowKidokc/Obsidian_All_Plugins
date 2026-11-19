# Python research backend: retained for reviewed integration

This is the substantial Python-OBS-backend project, not just batch launchers. It contains definition engines, vault scanning, a database layer, math translation, Mermaid generation, CDCM analysis and a PySide research-manager interface.

Compared with apps/research-manager: 119 identical files and 13 differing shared files. Each branch also has unique modules. See docs/RESEARCH_BACKEND_COMPARISON_20261118.json. Keep both until reviewed decisions identify the retained implementation of each module; do not copy one wholesale over the other.

Checks: all 112 imported Python files parse. The main PySide window constructs with test configuration and no vault attached, with the Ollama availability probe disabled. It warns about an obsolete O: math-translation workbook path; correct that through explicit configuration, not by creating or modifying a corpus file. A generated empty test database was moved into ignored local test artifacts. Three known-answer CDCM fixture tests pass (python -m unittest discover -s tests -p test_cdcm_fixture.py -v).

Metric warning: violation_density is violations per axiom (1/4 in the test fixture), whereas one CDCM workbook statistic divides by all scored cells (1/36). Preserve the denominator/unit in the shared metric dictionary. Passing arithmetic fixtures does not verify all 26 advertised metrics or establish the argument's truth.

Old APPLY_*, PATCH_*, backup, restore, overnight and scanning scripts are imported source references; none were executed. Do not run them merely because they are here. Vault mutations still need the shared actor/history/dry-run/undo interfaces.

The imported history excludes .claude/settings.local.json as machine-local agent settings. Original source files and Git repository remain untouched.
