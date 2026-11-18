# Quantum Papers — local prototype

One original Markdown paper, registered in folders across multiple vaults.
Uses Python 3.10+ and its standard library; no package installation required.

## Try the isolated demo

```sh
python quantum.py --demo --state /tmp/quantum-papers-demo
```

Open the local server on port 8765 in your browser. Select Research → Papers,
open “One paper.md”, then select Writing → Ideas and open the same paper.
Edit and save from either location. “Show here too” adds a folder membership;
“Move original” physically moves the file, including between vaults.
Writing → Papers contains a linked note: its paper link still resolves after a move.

To connect existing vaults, pass `--vault /absolute/path/to/vault` for each vault.
Use “Register a Markdown file” with a vault-relative path. Registering and adding
memberships do not duplicate or modify the file. Saving and moving modify real
files; use backed-up test vaults during this prototype stage.

```sh
python -m unittest discover -s tests -v
```

## Current boundaries

- Local, single-user browser workspace, bound to loopback. No network sharing yet.
- Folder memberships live in the SQLite registry under `--state`; back it up along
  with your vaults. Keep the same server address for copied browser links.
- Links use permanent registry IDs. Moves made through this app preserve them.
  After external moves, run `--reconcile`: files are matched by name (ambiguous
  duplicates are reported, not guessed), vanished files are marked `stale`, new files
  are registered. Renames made outside the app show up as one stale + one new.

## Batch, backup and tangent commands

```sh
python quantum.py --reconcile
python quantum.py --move-folder VAULT FOLDER DEST_VAULT DEST_FOLDER   # all or nothing
python quantum.py --export-registry backup.json
python quantum.py --import-registry backup.json                      # merges
python quantum.py --portable --vault ../vaults/MyVault               # root stored relative to --state
```

### Right-click a paper

```sh
python quantum.py --init-vault "\\server\share\B_series"   # registry lives in B_series\.quantum
python quantum.py --install-menu                          # adds "Quantum Paper…" to .md right-click
```

Right-click any `.md` file → **Quantum Paper…** (Windows 11: under *Show more options*)
→ *Move it to…* / *Also show it in…* / *History* → pick a folder. Moves are logged as
`<you> (right-click)`. The registry stores the vault relative to `.quantum`, so the whole
folder can be moved or copied elsewhere. If this repo moves, run `--install-menu` again.
`--uninstall-menu` removes the entry.

### Who moved what

Every register, move, batch move, save, membership and tangent change is logged with
time, actor, from and to. Give each terminal or AI its own name:

```sh
python quantum.py --actor claude-terminal-3 --move-folder ...   # or set QP_ACTOR=gpt-agent
python quantum.py --history                                     # everything, oldest first
python quantum.py --history "Papers/One paper.md"               # one paper (path or id)
```

Web/API callers send an `X-QP-Actor` header (or `"actor"` in the JSON body);
`GET /api/history` and `/api/history/<paper id>` return the log. Moves made outside
the tool can't name their mover; `--reconcile` logs them as `external (seen by <actor>)`.

API: `/api/batch-move`, `/api/batch-register`, `/api/reconcile`, `/api/tangent/create`
(marks a registered paper as a tangent), `/api/tangent/search`. `GET /api/paper/<id>`
now includes the paper's tangents.
- Markdown source editing and internal paper-link navigation; no rich rendering yet.
- This is not yet an installable Obsidian plugin. Native Obsidian explorer entries,
  cross-device sync, automatic file discovery, external link handlers, authentication,
  concurrent editing conflict handling, and crash-safe file moves are future work.
- Existing ordinary Obsidian links are not rewritten when a file moves.

Use the existing checkout for development; cloud tasks are already isolated.
