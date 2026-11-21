const assert = require('node:assert/strict');
const test = require('node:test');
const Module = require('node:module');
const { readFileSync } = require('node:fs');
const { webcrypto } = require('node:crypto');
const { resolve } = require('node:path');

if (!globalThis.crypto) globalThis.crypto = webcrypto;

class File { constructor(path) { this.path = path; } }
class Folder {}
class Plugin {}
class Widget {}
const runtime = new Module(resolve(__dirname, 'main.js'));
runtime.require = name => {
  if (name === 'obsidian') return {
    TFile: File, TFolder: Folder, Plugin, Notice: class {}, ItemView: class {}, PluginSettingTab: class {},
    requestUrl() { throw new Error('Network access is forbidden in the offline pilot'); }
  };
  if (name === '@codemirror/state') return { StateEffect: { define: () => ({}) } };
  if (name === '@codemirror/view') return { WidgetType: Widget };
  throw new Error('Unexpected runtime dependency: ' + name);
};
runtime._compile(readFileSync(runtime.id, 'utf8'), runtime.id);
const Workspace = runtime.exports.default;

function fixture() {
  const plugin = new Workspace();
  const file = new File('source.md');
  let text = 'Synthetic axiom.\nSecond line.\n';
  const files = new Map([[file.path, file]]);
  const writes = new Map();
  plugin.app = {
    workspace: { getLeavesOfType: () => [] },
    vault: {
      getAbstractFileByPath: path => files.get(path),
      readBinary: async () => new TextEncoder().encode(text).buffer,
      createFolder: async path => { files.set(path, new Folder()); },
      create: async (path, contents) => {
        assert(!files.has(path));
        files.set(path, new File(path));
        writes.set(path, contents);
      }
    }
  };
  plugin.open = async () => {};
  plugin.saveData = async () => {};
  return { plugin, file, writes, getText: () => text, setText: value => { text = value; } };
}

test('preview checks exact bytes, makes no writes, and captures only the selected provider', async () => {
  const { plugin, file, writes, getText } = fixture();
  await plugin.settings({ provider: 'openrouter', models: { openrouter: 'vendor/example' } });
  await plugin.prepare(file, getText(), 0, 16);
  assert.equal(plugin.draft.source.quote, 'Synthetic axiom.');
  assert.equal(plugin.draft.provider.endpoint, 'https://openrouter.ai/api/v1/chat/completions');
  assert.equal(plugin.draft.provider.model, 'vendor/example');
  assert.equal(plugin.draft.mode, 'preview');
  await assert.rejects(plugin.saveOutput(plugin.draft, 'json', 'Review sidebar'), /writable output/);
  assert.equal(writes.size, 0);
  assert.equal(plugin.data.results.length, 0);
  assert.equal(getText(), 'Synthetic axiom.\nSecond line.\n');
});

test('annotation is idempotent and becomes stale after any change to the exact edition', async () => {
  const { plugin, file, writes, getText, setText } = fixture();
  await plugin.prepare(file, getText(), 0, 16);
  const draft = { ...plugin.draft, mode: 'annotation' };
  await Promise.all([plugin.saveOutput(draft, 'json', ''), plugin.saveOutput(draft, 'json', '')]);
  assert.equal(plugin.data.results.length, 1);
  assert.equal(writes.size, 0);
  await plugin.feedback(plugin.data.results[0], 'comment', 'Verify the wording.');
  assert.equal(plugin.data.results[0].history.length, 1);
  setText(getText() + 'Additional context.\n');
  assert.equal(await plugin.isCurrent(draft.source), false);
  await assert.rejects(plugin.feedback(plugin.data.results[0], 'accept', 'Test'), /stale/);
  await assert.rejects(plugin.saveOutput(draft, 'json', ''), /edition has changed/);
});

test('exports preserve the existing file on repeats and reject changed or invalid destinations', async () => {
  const { plugin, file, writes, getText } = fixture();
  await plugin.prepare(file, getText(), 0, 16);
  const draft = { ...plugin.draft, mode: 'export' };
  const path = plugin.destination(draft, 'json');
  await assert.rejects(plugin.saveOutput(draft, 'json', file.path), /updated destination/);
  await plugin.saveOutput(draft, 'json', path);
  const original = writes.get(path);
  assert.equal(JSON.parse(original).source.quote, 'Synthetic axiom.');
  await assert.rejects(plugin.saveOutput(draft, 'json', path), /already exists/);
  assert.equal(writes.get(path), original);
  await plugin.settings({ outputFolder: '../outside' });
  assert.throws(() => plugin.destination(draft, 'json'), /relative vault folder/);
  assert.equal(getText(), 'Synthetic axiom.\nSecond line.\n');
});

test('CRLF files preserve exact raw quotes and offsets', async () => {
  const { plugin, file, setText } = fixture();
  setText('first\r\nsecond\r\n');
  await plugin.prepare(file, 'first\nsecond\n', 6, 12);
  assert.equal(plugin.draft.source.start, 7);
  assert.equal(plugin.draft.source.end, 13);
  assert.equal(plugin.draft.source.quote, 'second');
  assert.equal(plugin.draft.source.firstLine, 2);
});
