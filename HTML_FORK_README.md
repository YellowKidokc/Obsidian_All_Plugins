# HTML Dashboard Fork

Forked from `O:\999_IGNORE\Python_Backend_Dashboards` for MDA HTML site output.

## What Was Stripped
- Obsidian vault sync (`engine/vault_engine.py` disabled)
- Obsidian markdown formatting
- Obsidian plugin hooks
- `.obsidian/` config references

## What Was Added
- `engine/html_export_engine.py` — exports definitions to MDA glossary-terms.json
- `engine/mda_bridge.py` — bridges dashboard data to MDA site structure
- UTF-8 enforcement on all file I/O

## Output Targets
```
\\dlowenas\HPWorkstation\Desktop\Master HTMl\____ MDA WORKFLOW\shared\data\glossary-terms.json
\\dlowenas\HPWorkstation\Desktop\Master HTMl\____ MDA WORKFLOW\shared\js\glossary-layer.js
\\dlowenas\HPWorkstation\Desktop\Master HTMl\____ MDA WORKFLOW\site-lib\html\mda\dashboards\
```

## Usage
```bash
python engine/html_export_engine.py --output-mda
```
