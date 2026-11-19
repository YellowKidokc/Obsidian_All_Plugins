# Paper Projection Workbench

Double-click **START_PROJECTIONS.bat**. Requires Python 3.10+ with Tkinter. No pip installation required.

1. Choose one UTF-8 Markdown/text paper. It can stay in its original folder.
2. Select any of the 21 projections using Ctrl/Shift, or select all.
3. Click **Prepare prompts / package (FREE)**. Every run has its own directory in OUTBOX.
4. Choose either path:
   - Give the source/prompt package to Claude or another AI, then import its JSON through **Import AI JSON**. The system prompt is in manifest.json; individual prompts contain the required return format and numbered source.
   - Set DEEPSEEK_API_KEY in your Windows environment and relaunch. Click **Run prepared API tasks (PAID)** and confirm the displayed number of calls, model and token cap.
5. Open the run folder and its index.html status dashboard. Results are saved as structured JSON plus readable Markdown.

The selection applies when preparing a package. The paid button runs remaining PREPARED API tasks in that package, not a new selection in the list. Prepare a smaller package to run fewer tasks. All 21 selected means 19 potential API calls; preservation and AI packaging run locally.

## Why Python and APIs work together

Python manages source identity, exact preservation, numbered passages, prompt export, output checks, run receipts and the dashboard. Model calls produce adaptations, extraction proposals and review drafts. One source snapshot feeds separate projections; adapting the paper does not overwrite it.

The default model is deepseek-flash. Override using the model field or PROJECTION_MODEL environment variable. The adapter uses DeepSeek's documented HTTPS chat-completions endpoint: https://api-docs.deepseek.com/ . Credentials are read from the environment and never saved by this app.

## Scope and honest statuses

- Preservation copies exact source bytes including BOM and newlines, with SHA-256. Adaptations are inherently selective; only the original snapshot is lossless.
- Each run is immutable in source identity. Editing the original later requires preparing a new run; previous projections refer to their preserved source version. There is no automatic live-vault freshness scanner yet.
- PREPARED means a prompt exists. GENERATED_UNREVIEWED means structural checks passed, not that a conclusion is correct. Source reference checks establish line bounds, not semantic support.
- Citation/literature tasks cannot browse inside this adapter. They identify gaps and source-internal comparisons; external source verification remains a separate task.
- Theorem extraction and proof explorer are candidates, not Lean compiler results. TTS is narration text; audio, rendered video and images require additional production stations.
- One selected task uses one API call with no retries. Each call repeats the source input. Token caps limit output, not dollar cost. The app does not estimate prices or enforce a dollar budget.
- Paid execution persists SUBMITTED before sending. Timeouts/failures become FAILED_OR_UNCERTAIN and stop the run. Inspect raw responses and receipts; failed/submitted calls are not automatically resubmitted. Successful tasks are skipped on later execution.
- Prompts over 100,000 characters are refused by this adapter instead of silently truncating. It is not a general long-document chunk/merge pipeline yet.
- Import requires the exact source hash, projection code, content, items, limitations and valid line references. Existing results cannot be overwritten; use a new run for a new version.

## Layout

Root: this note, batch launcher, INBOX, OUTBOX and BACKSIDE. Python, tests and the projection catalog live in BACKSIDE. OUTBOX runs contain SOURCE, PROMPTS, RESULTS, RECEIPTS, manifest.json and index.html. AI_PACKAGE.zip is a handoff snapshot created during preparation, before generated results arrive.

This is the projection preparation/execution layer. Existing station aliases and the full Excel/HTML/SQLite/FIS system still need adapters; this app does not claim those integrations are complete. No publishing or manuscript rewriting happens here.


## Existing analytics library

Double-click OPEN_ANALYTICS_LIBRARY.bat for the six legacy analytics locations, selected source snapshots and the integration handoff. These are reference materials, not enabled execution adapters.
