# Pipeline desktop prototype: useful candidate, separate from Obsidian plugins

Source: YellowKidokc/LOWES-OBS-DONE-RIGHT-. Imported under apps/pipeline-desktop with history. The original source repository was not changed.

Two startup repairs were made in this imported copy:
- Define refreshFiles before a createNewFile callback includes it in the dependency array. The original failed TypeScript and would hit a JavaScript temporal-dead-zone error during provider initialization.
- Delegate environment detection to the installed @tauri-apps/api/core isTauri helper rather than requiring the optional __TAURI__ global.

Checks: npm ci from the existing lockfile; npm run build passed; five tests pass with node --test tools/test-startup.cjs; cargo check --offline passed. Cargo.lock was generated and retained for reproducibility. The tests cover actual provider rendering and installed-runtime detection; no real vault or file-writing action was exercised.

Assessment: worthwhile black/gold editor and navigation prototype. It is a Tauri desktop app, not an installable Obsidian plugin. Keep it as an optional shell/UI reference while Dashboard Navigator remains David's preferred native Obsidian surface.

Not cleared for live-vault operation: existing code still has direct overwrite/removal functions, automatic frontmatter serialization/ID generation, no shared Quantum history/undo wiring, and no native file-picker/read/write acceptance test. A web-only launch intentionally cannot open the desktop file picker. A compile check does not certify runtime scope configuration. Do not deploy it against the corpus until those behaviors are reconciled with this repository's preservation/identity rules and tested on copies.
