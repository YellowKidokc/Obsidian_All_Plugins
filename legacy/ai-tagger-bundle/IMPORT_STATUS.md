# Legacy tagging bundle

Kept separate from plugins/semantic-ai because both manifests identify semantic-ai. Do not install both into a single vault. This bundle is useful for prompts, taxonomy references and requested paragraph/invisible-tag output. Its README's claims of working behavior are historical, not a new acceptance test.

plugin/data.json was excluded from imported history as runtime settings. The source copy had a blank API key at inspection; it still belongs outside Git. Original source remains unchanged. Compiled main.js passed node --check; no live AI or vault-write test was run. Port needed prompt/format features into the selected maintained plugin after reviewing differences.
