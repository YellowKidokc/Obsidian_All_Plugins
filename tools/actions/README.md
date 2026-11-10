# File actions

## One front door

Open `ACTION_HUB.bat`. Put files or folders in `INBOX`, select one from the
numbered list, browse directly for a folder or file, or paste a path from anywhere
on the desktop, attached drives, or reachable network shares. Choose an action, then keep running other
actions until you select Done. New reports and conversions are placed in dated
folders under `OUTBOX`.

The layout is:

- `INBOX` — optional drop point for work you want listed automatically.
- `OUTBOX` — dated results and reports.
- `BACKSIDE` — Python engines; normally you do not open this folder.
- `ACTION_HUB.bat` — interactive action menu.

The individual launchers remain available. Shortcuts to `ACTION_HUB.bat` can be
placed anywhere, but keep the real launcher with this folder structure.

Drag a file or folder onto any `.bat`. Every action shows a preview first and changes nothing until you type `YES`.

| Launcher | What it does | Safety |
|---|---|---|
| `FLATTEN_FOLDER.bat` | Moves files up from all subfolders, then removes folders left empty | Reversible (manifest + `UNDO_FLATTEN.bat`) |
| `EXCEL_TO_CSV.bat` | Each workbook becomes a book folder: one CSV per sheet, in order, plus `_book.json` | Creates new files only |
| `CSV_TO_EXCEL.bat` | A book folder rebuilds the **same workbook** (sheet names, order, hidden state). A plain folder of CSVs becomes one workbook with a sheet per CSV | Creates new files only |
| `ANY_TO_MARKDOWN.bat` | Word, PowerPoint, Excel, PDF, HTML, EPUB, CSV, JSON, Outlook .msg, ZIP… → `.md` (Microsoft MarkItDown). Adds provenance frontmatter | Creates new files only |
| `MARKDOWN_TO.bat` | `.md` → Word, HTML, PDF, PowerPoint, ODT, RTF, EPUB, plain text (pandoc) | Creates new files only |
| `FOLDER_SEARCH_REPORT.bat` | Inventories names, created-date groups, similar titles, folder counts, possible spelling/name issues, exact duplicates, near-text matches, and one-file/two-file folder candidates | Read-only source scan; writes a separate report only |

Conversions write to a new `_converted\<action>_<time>\` folder next to the source, or to the in-house workspace if you choose option 2. Each run writes a `_receipt.json` with input and output hashes. To undo a conversion, delete its output folder.

First time: run `SETUP_CONVERTERS.bat`.

## Folder Search Report

Drag a folder onto `FOLDER_SEARCH_REPORT.bat`, or double-click it and paste a
folder path. Reports are written beneath `_folder_reports` in the selected
folder. The report includes CSV evidence plus Markdown, HTML, and JSON summaries.

SHA-256 identifies byte-for-byte duplicates. It does not measure how close two
documents are, so the action also calculates a separate near-text fingerprint
for readable text files. Near matches, similar titles, spelling warnings, and
small-folder lists are review candidates only. This action never deletes,
moves, renames, merges, or canonizes anything.

## What does not survive a conversion

- **Excel → CSV:** values only. Formulas, formatting, charts, merged cells and comments are not kept, and you get a warning when a workbook has formulas. CSV → Excel restores values, types and sheet structure.
- **Number-like text is kept as text:** codes with leading zeros (`00123`) and long IDs stay text so nothing gets rounded.
- **Markdown → Word/PDF and back:** Obsidian `[[wikilinks]]` become ordinary links, and callouts or plugin syntax are flattened.
- **Scanned PDFs or images → Markdown:** these give empty output unless OCR is added, and you get a warning when that happens.
