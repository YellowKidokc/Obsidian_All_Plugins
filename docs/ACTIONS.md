# Quantum Papers: the action map

The goal: one clean tool where anyone can do everything they need with their
Markdown papers, without knowing the command line. Every action exists three ways:

1. **CLI**: `python quantum.py <verb>`, for scripts, AIs and power users
2. **API**: `POST /api/<verb>`, which the GUI and other tools call
3. **GUI**: a button, a right-click entry, or the command palette (Ctrl+K)

One engine (`quantum.py`), three front doors. Every action is logged with its actor.

## 1. Every action, grouped

| Group | Action | Exists today? | Notes |
|---|---|---|---|
| **Find** | Search papers (name, text, tags) | name only | add full-text + frontmatter search |
| | Filter by status / tag / vault / view | views only | |
| | Show orphans (no links in/out), stale, duplicates | partial (reconcile) | "Vault health" screen |
| **Organize** | Move paper / folder (all or nothing) | ✅ | |
| | Show in another folder (membership) | ✅ | |
| | Rename paper (keep ID, fix links) | ❌ | high value; Obsidian links break today |
| | Batch tag / set status (draft, canon, review) | ❌ | via frontmatter |
| | Apply a view (working, canon, 13roads…) | ✅ | |
| **Write** | Create from template (paper, definition, chapter) | ❌ | templates folder |
| | Edit + save | ✅ basic | |
| | Make a tangent of a paper | ✅ | |
| | Split / merge papers | ❌ | later |
| **Review** | AI review → CriticMarkup suggestions | ❌ | prototype: `prototype/annotate.html` |
| | Accept / reject suggestions, one or all | prototype | |
| | Add my own note on a selection | prototype | |
| | Review queue (papers with open suggestions) | ❌ | |
| **Connect** | Copy permanent link | ✅ | |
| | Show backlinks / outgoing links | partial | |
| | Fix broken links after moves | ❌ | pairs with Rename |
| **Publish** | Export paper → HTML | prototype | |
| | Export folder/vault → linked HTML site | ❌ | the "Obsidian of HTML" goal |
| **Safety** | History: who changed what | ✅ | |
| | Undo last action | ❌ | history already has from/to, so it's feasible |
| | Backup / restore registry | ✅ | |
| | Reconcile after outside changes | ✅ | |
| **Setup** | Init vault, install right-click menu | ✅ | |
| | First-run wizard (pick vault, done) | ❌ | essential for other people |

## 2. What it should look like

```
┌──────────────────────────────────────────────────────────────────────┐
│  Quantum Papers        [ Ctrl+K  search or run any action… ]   ⚙  ↶ │
├──────────────┬──────────────────────────────────────┬────────────────┤
│ VAULTS       │  Chapter 1 — Origins      [Edit|Read]│ ◉ Suggestions 4│
│ ▸ B_series   │  ──────────────────────────────────  │ ○ Links       7│
│ ▾ Book       │  The universe [doesn't begin] with   │ ○ History      │
│   📄 Ch 1 ●4 │  matter, it begins with information… │                │
│   📄 Ch 2    │                                      │ (inline pop-up │
│ ▸ Notes      │                                      │  at the mark   │
│ ─────────────│                                      │  when clicked) │
│ QUEUES       │                                      │                │
│  Review   3  │                                      │                │
│  Stale    1  │                                      │                │
├──────────────┴──────────────────────────────────────┴────────────────┤
│ ✓ Moved "Ch 2" → Book/  by David (right-click)            [Undo]     │
└──────────────────────────────────────────────────────────────────────┘
```

Principles:
- **Three panes, one job each:** where (vault tree), what (the paper), about it (tabs).
- **Command palette is the universal door:** every action in the table is searchable there.
- **Badges, not dialogs:** `●4` = 4 open suggestions. Queues show what needs attention.
- **Every change gets a toast with Undo.** That's what makes it safe for new users.
- **Right-click everywhere** (tree, paper, selection) shows the same actions in context.

## 3. Obsidian integration

- **Files stay plain Markdown + CriticMarkup**, so everything opens in Obsidian too.
- Open a paper in Obsidian: the `obsidian://open?vault=…&file=…` URI (a button in the GUI).
- Obsidian's own CLI (in recent versions) and the Advanced URI plugin can run Obsidian
  commands from scripts. Check the current Obsidian docs before relying on either.
- Later: package the same API as an Obsidian plugin (sidebar view calling the local server).

## 4. Build order

1. **Command registry**: one list of actions (name, group, args, handler) that feeds
   the CLI, API and palette at once, so nothing gets out of sync.
2. **GUI shell**: the three-pane layout + palette + toast/undo, on the current web server.
3. **Review**: move `annotate.html` in, reading and writing CriticMarkup in real files.
4. **Rename + fix links**, then **Undo**.
5. **Export linked HTML site.**
6. **First-run wizard + installer**, so other people can use it.
