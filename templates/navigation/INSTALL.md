# Install the navigation template kit on a copied test vault first

1. Enable the Templater community plugin in a copied test vault. Dataview is no longer required for these repaired templates.
2. Copy the five Markdown files from _templates into that vault's _templates folder. Configure Templater to use that folder.
3. Copy .obsidian/snippets/page-template-system.css into the test vault's CSS snippets folder. Enable it in Appearance.
4. Optionally copy navigation.config.example.json to _templates/navigation.config.json in the test vault and edit vaultHome, recent and links to actual vault-relative note paths. Missing targets are omitted. Leave the example file alone in this repository.
5. Create a new/copied note using Templater. These are authoring templates, not a whole-vault wrapper/rewriter. Do not apply them across existing manuscripts.
6. Test both Reading view and Live Preview: actual folder home, previous/next note, root files, duplicate basenames, spaces/Unicode and the configured links.

Home looks for 00_INDEX, _INDEX, index or README in the note's own folder. Vault home uses the configured target or a real root index. The kit does not create indexes; a recursive index generator is separate work. Previous/next means alphabetical note order, not browser history. Stats and links are captured at creation and do not refresh automatically.

The footer uses best-effort sticky CSS. Obsidian's block structure and themes can constrain it; a reliable always-visible toolbar needs a real plugin view. No active-vault installation was performed during import.

Regenerate templates after changing tools/template-body.js with node tools/build-templates.cjs, then run node --test tools/test-navigation.cjs.
