# Two Semantic AI installations and controlled output

David's direction, recorded by Codex on November 20, 2026. This is an implementation requirement, not a claim that two plugins are installed or the new output controls are built.

## Product decision

There must be two independently installable/enabled Obsidian plugins, not one plugin with a switch that makes the other disappear:

1. **Semantic AI — Theophysics.** Preserve the maintained plugin's existing identity `semantic-ai`, current settings, concept UUIDs, taxonomy and notes. Its user-facing display name may be clarified without changing its manifest ID or moving its data. Its job remains theological/research concept classification, tags, concepts and maps.
2. **Semantic AI — Series Workspace.** Use a distinct manifest ID, proposed `semantic-series-workspace`, with independent settings, commands, views and managed state. Its job is the 21 workspace roles, rigor assessments, review tasks and controlled outputs. It is not an instruction to run 21 model calls for every note.

Keep one maintained source for reusable provider transport, prompt/schema validation, source/version binding and rendering helpers. Use thin entry points/profiles and shared packages rather than cloning the entire plugin into two diverging trees or installing the legacy tagger with the same plugin ID.

## Coexistence and data isolation

Manifest IDs alone are insufficient. Namespace command/view IDs, ribbon actions, settings, registered event handlers, CSS scope and plugin-local storage. The existing concept registry uses the plugin directory supplied by the manifest, but also has a fallback path; audit that fallback and every view-type constant. Two installations must never overwrite one another's settings, provider choices, registry, task queue or results.

Do not copy credentials automatically between plugins or change the original plugin's settings to manufacture migration. Both may explicitly select the same configured provider, but provider transport is not the same as shared approval authority or a shared mutable settings file. Never commit runtime data.json, API keys, provider databases or user records.

Existing concept UUIDs are not canonical document/work IDs. Reuse existing concept references through explicit adapters where appropriate; do not create two competing authoritative concept/document registries. Unknown identities remain unresolved. The second plugin may have local job/result IDs without claiming canonical IDs.

## Prompt registry, not a wall of calls

Bundle a versioned task registry with stable task IDs, title, role codes, RIGOR-10 areas, task class (extraction/criticism/validation/canon assessment), input requirements, actual prompt text, return-schema version, output policy and review requirement. Keep prompt IDs distinct from API station numbers and role codes.

Use the reference 21-role catalog, 33 desired outputs and bounded prompt candidates supplied under `docs/series-automation-reference`. Keep the three proposed additional products explicitly pending; they are not additional folders. Include the full 28-field ORBITS reference (six core, twelve conditions, ten spiritual/moral fields) as its own contract. Missing definitions/applicability stay unknown or justified not applicable.

The source helper's thirteen prompt candidates are review inputs, not thirteen automatic calls. Extraction must not certify its own completeness; criticism must not validate its own fix. Split mixed task classes into separately attributed runs. Canon assessment recommends only. Hashes, inventory, counting, path checks and receipt checks remain local Python work.

## Output must be a first-class contract

Before a job, show the selected source/scope, task, model if any, permitted context, output mode, destination, review path and estimated cost where applicable. A template/task may have a saved output policy, but source text or a model response cannot choose an arbitrary destination or escalate permissions.

Supported modes:

- **Preview only** (default): a result panel with no source-note changes.
- **Passage annotation**: a small marker/highlight and sidebar discussion anchored to the exact source version and quoted span.
- **Managed result record**: save a typed result in the configured managed store, with a human-readable link from the relevant view.
- **Generated note/block**: only when explicitly selected; change an owned generated region or new file, preserving authored content and collision handling.
- **Export**: produce selected JSON/Markdown/HTML projections from the same owned result. Exporting does not publish.
- **Callout**: optional explicit mode, not the default and never automatically appended for every field or role.

A result identifies source record/declared ID, exact edition/hash, locator/quote, producing plugin/task/prompt/model versions, privacy, proposer/reviewer, processing state, evidence standing and receipt references. Keep model content separate from runner-stamped usage, timing, cost, hashes and validation. Invalid/truncated responses remain incomplete; raw responses may be retained in private managed state, never inserted into a paper as approved content.

## Annotations instead of oversized callouts

Select a sentence/paragraph/axiom and invoke a task. Add a small marker and open the result in a side panel. Allow filtering by task/role, source version and review standing. Each finding has its own comment/reply/accept/reject/request-change history.

Store the owned annotation/review record outside manuscript prose. The source remains readable with markers hidden. A marker or accepted review finding does not itself edit the sentence or approve canon. Source text edits require a separate exact patch preview and authority.

Anchor to source hash, quoted text and contextual locator. If the source changes, mark old findings stale. Reattachment may be proposed when the match is unambiguous; never silently attach an old comment to a similar sentence elsewhere. Preserve Reading view/Live Preview/source-editor behavior and accessibility. Use the existing Plannotator/workbench review adapter where practical; do not create a competing review ledger.

## Backend boundary

Semantic AI is the Obsidian interface/provider transport adapter, not a replacement for filesystem inventory, a Lean runner, scientific tests or the authoritative registry. Integrate with the existing workbench's common records and local Python supervisor. Reuse the current source/passage/review/export contracts; do not add a second active SQLite database on the NAS.

Automatic arrivals, queue updates and generated views can be local. Provider execution, source mutation and publishing have their own configured scope. The first coding pilot uses synthetic/temp data, preview outputs and zero provider calls; no watcher starts merely because the plugin loads.

## Acceptance before installing in a live vault

1. Both plugins load together in a copied test vault; each can be disabled/reloaded without breaking the other. Unique manifests, views and commands are verified.
2. Existing Semantic AI settings, concept UUIDs, tags and notes survive unchanged. No legacy plugin with a duplicate ID is activated.
3. Changing the second plugin's settings, taxonomy, model or result location does not affect the first. No credentials are copied or committed.
4. All 21 role definitions and prompt-task mappings are inspectable; ORBITS exposes all 28 fields with unknown/NA handling. Selecting a role does not automatically trigger all its prompts.
5. Preview mode makes zero source-byte changes. Callouts and generated-note writes occur only in their chosen mode, inside validated destinations.
6. Selecting a passage produces a correctly anchored synthetic annotation and sidebar result in editor/reading modes; source edits make it stale without silent relocation.
7. Repeated job/result imports are idempotent. Human-edited outputs and path collisions are preserved for review, never overwritten.
8. Read receipts, reviewer votes, acceptance of a finding, edits and canon rulings remain distinct exact-version events. No model self-approval.
9. Existing plugin builds/tests and workbench checks pass, plus meaningful coexistence/output-policy/annotation tests. Report unavailable live Obsidian checks honestly.

## Delivery

Produce two installable build artifacts from maintained shared source, the task registry/schema, source-bound annotation and output router, test results and copied-vault installation instructions. Keep existing entry points usable. Open a reviewable PR against `OBS-Plugin-Final-Claude`; do not merge, activate in a live vault, make paid calls or claim a spec document is the finished implementation.
