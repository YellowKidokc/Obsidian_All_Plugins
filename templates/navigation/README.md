# Navigation templates: imported and repaired

This component is a Templater/CSS kit, not a standalone Obsidian plugin. It has no plugin manifest or executable main.js. The historical Readme.txt describes the original proposal; this file and INSTALL.md describe the repaired implementation.

Repairs: full vault-relative file targets, real folder-local home indexes, root-folder handling, no invented previous/next note when the current file is absent, existing-target-only configurable links, escaped HTML and encoded link paths, cancellation/config-error handling, and footer CSS matching the emitted class. The Dataview variant uses a creation-time note count rather than an invalid dynamic expression. No claims of live counts or full-time pinned navigation.

Tests: node --test tools/test-navigation.cjs (10 tests). These execute the actual embedded template code against mocked Templater/Obsidian APIs. They do not prove live-vault rendering or theme-specific sticky behavior. No production vault was modified.

The original Git history remains in this repository. Changes are confined to the imported component; the source repository is unchanged.
