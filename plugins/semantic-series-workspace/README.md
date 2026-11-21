# Semantic AI — Series Workspace

This plugin prepares source-bound dry requests for Series Workspace tasks. It runs alongside Semantic AI in Obsidian under a separate ID and writes settings and review state to its own plugin directory. Its research provider and model are independently selectable. This build makes zero provider calls and has no credential fields.

## Build both plugins

From the repository root:

```sh
npm --prefix plugins/semantic-ai ci
npm --prefix plugins/semantic-ai run build
cd plugins/semantic-series-workspace
../semantic-ai/node_modules/.bin/tsc --noEmit --skipLibCheck
node build.mjs
node --test test-offline.cjs
```

## Copied-vault test

1. In a copied test vault, back up the existing Semantic AI plugin directory. Retain its original `data.json` and any registry files. Copy each plugin's `manifest.json`, `main.js` and `styles.css` into its corresponding folder under the vault's Obsidian configuration directory, usually `.obsidian/plugins/semantic-ai/` and `.obsidian/plugins/semantic-series-workspace/`.
2. Enable the two plugins. Confirm that the original settings and index still load. Change the Series Workspace provider or model and verify that the original settings are unaffected. Disable and re-enable each plugin independently.
3. Use a synthetic Markdown note. Select a passage and run **Preview selected passage** from the Series Workspace commands. Review the source hash, allowed context, task and destination. The Reading view command accepts an unambiguous literal passage; use the editor for selections containing rendered Markdown or repeated quotes.
4. Select **Passage annotation** and save it. Open the marker in the editor and Reading view. Add a review comment in the sidebar, then edit the source and verify that the annotation becomes stale. Compare the source bytes before and after previewing and saving the annotation.
5. Save a managed record and export it to a dedicated vault folder. Verify that an existing file at the displayed destination is preserved. Outputs contain the selected passage. Use an appropriate private test vault and output folder for any later test involving sensitive inputs.

The catalog includes 21 roles, 33 reference outputs, three pending proposals, and the 28-field ORBITS reference. Task selection prepares a single dry request. Review feedback records local operator actions on that exact request and source version. The workbench remains the authority for formal receipts, identity, review-ledger imports and canon rulings. The current plugin exports dry requests and local feedback for inspection. Automated workbench ingestion and provider response processing are later phases.
