# Publication sanitization

GitHub push protection rejected the first consolidation push because an imported historical dashboard inventory contained two OpenAI-key-shaped tokens. A scan of all 2,377 reachable objects found one matching blob: the dashboard ENGINE_INVENTORY.csv report. Key values are never reproduced in this note.

The report is excluded from the published consolidation history at both its original reports/phase1/windows/ENGINE_INVENTORY.csv path and imported apps/dashboard/reports/phase1/windows/ENGINE_INVENTORY.csv path. The supplied source repositories remain unchanged. A local copy of the report is retained only under the ignored .venv/security-hold directory. No push-protection bypass was used.

Removing a file from earlier unpublished commits rewrites affected commit IDs. Import receipts retain pre-sanitization import IDs as historical provenance; use their original source revisions and source-blob verification records when tracing the import. No remote shared history is force-pushed or rewritten: publication extends the existing integration branch from its unchanged base.

If these keys are still active, revoke/rotate them. Removing the report from this new repository does not remove copies from original source repositories or earlier exposures.
