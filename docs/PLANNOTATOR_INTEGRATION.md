# Plannotator review adapter

Upstream: https://github.com/backnotprop/plannotator . Pinned revision: `951857cfffc191c3c62c0547342e394bbb8f8898`.

Plannotator is registered as `vendor/plannotator`, an external review dependency. Initialize it in a fresh checkout with `git submodule update --init --recursive vendor/plannotator`. It is not another Obsidian plugin or a forked replacement for its review UI.

This packaging pass did not complete a local checkout/build: the first shallow clone stalled and was stopped. The pinned commit was resolved from upstream HEAD; a successful dependency checkout and its upstream build/tests remain Codex tasks. Do not claim the local dependency has been installed or tested. The partial local Git checkout has been left intact; no manual removal of Git lock/metadata files was performed.

The supplied download at `\\192.168.2.50\h_hp\Downloads\Compressed\plannotator-main` has 1,206 files but lacks its root `package.json` and shared `packages` directory. Keep it as an incomplete source reference. No download files were changed.

Use a separate adapter to annotate paper/projection Markdown and rendered HTML. Carry source/version hash, target span, author, timestamp and review status into paper AI Review Logs and processing receipts. Plan approval does not confer canon approval. Start with manual launch/import and copied fixtures; do not globally install agent hooks or modify a real Inbox/config as part of a build.

Follow upstream AGENTS.md and focused guides after checkout. Keep tests under a temporary PLANNOTATOR_DATA_DIR, using its documented browser/Inbox test helpers. Native Windows Codex hooks may be experimental; distinguish manual review from automatic feedback delivery.

No Plannotator installer, provider call, hook configuration or live vault review ran during consolidation.
