import {
  ItemView, MarkdownView, Notice, Plugin, PluginSettingTab, Setting, TFile, TFolder, WorkspaceLeaf
} from 'obsidian';
import { StateEffect } from '@codemirror/state';
import { Decoration, DecorationSet, EditorView, ViewPlugin, ViewUpdate, WidgetType } from '@codemirror/view';
import { activeProvider, PROVIDERS } from '../../semantic-shared/providers';
import { Mode, modes, orbits, outputs, pending, rigor, roles, tasks } from './catalog';
import { Draft, Feedback, matchesPassage, Passage, pluginId, requestEnvelope, SavedResult, sha256 } from './records';

const viewType = pluginId + '-review';
const providerIds = ['openai', 'anthropic', 'deepseek', 'ollama', 'openrouter'] as const;
type SeriesProvider = typeof providerIds[number];
const labels: Record<Mode, string> = {
  preview: 'Preview only', annotation: 'Passage annotation', record: 'Managed result record',
  'generated-note': 'Generated note', export: 'Export', callout: 'New note with callout'
};
const refreshAnnotations = StateEffect.define<void>();
const feedbackActions: Feedback[] = ['comment', 'reply', 'accept', 'reject', 'request-change'];

interface SeriesData {
  provider: SeriesProvider;
  models: Partial<Record<SeriesProvider, string>>;
  outputFolder: string;
  results: SavedResult[];
}

function checkedFolder(input: string): string {
  const parts = input.trim().split('/');
  if (parts.some(part => !part || part.startsWith('.') || /[\\:*?"<>|\x00-\x1f]/.test(part) || part !== part.trim())) {
    throw new Error('Enter a relative vault folder with valid names.');
  }
  return parts.join('/');
}

class Marker extends WidgetType {
  constructor(private open: () => void, private id: string) { super(); }
  eq(other: Marker) { return this.id === other.id; }
  toDOM(view: EditorView) {
    return markerButton(view.dom.ownerDocument, this.open);
  }
}

function markerButton(doc: Document, open: () => void): HTMLButtonElement {
  const button = doc.createElement('button');
  button.className = 'semantic-series-workspace-marker';
  button.textContent = 'Review';
  button.setAttribute('aria-label', 'Open Series Workspace passage review');
  button.onclick = open;
  return button;
}

export default class SeriesWorkspace extends Plugin {
  data: SeriesData = { provider: 'openai', models: {}, outputFolder: 'Series Workspace Outputs', results: [] };
  draft?: Draft;
  selected?: string;
  private writes = Promise.resolve();
  private editorViews = new Set<EditorView>();

  async onload() {
    const saved = await this.loadData() as Partial<SeriesData> | null;
    if (saved) this.data = {
      ...this.data, ...saved,
      provider: providerIds.includes(saved.provider as SeriesProvider) ? saved.provider! : 'openai',
      models: saved.models ?? {},
      results: saved.results ?? []
    };
    this.registerView(viewType, leaf => new SeriesView(leaf, this));
    this.addSettingTab(new SeriesSettings(this.app, this));
    this.addCommand({ id: 'open-review', name: 'Open Series Workspace', callback: () => this.run(() => this.open()) });
    this.addCommand({
      id: 'preview-selection', name: 'Preview selected passage',
      editorCallback: (editor, view) => this.run(async () => {
        if (!(view.file instanceof TFile)) throw new Error('Open a Markdown source first.');
        const start = editor.posToOffset(editor.getCursor('from'));
        const end = editor.posToOffset(editor.getCursor('to'));
        await this.prepare(view.file, editor.getValue(), start, end);
      })
    });
    this.addCommand({
      id: 'preview-reading-selection', name: 'Preview passage selected in Reading view',
      callback: () => this.run(async () => {
        const view = this.app.workspace.getActiveViewOfType(MarkdownView);
        const selection = view?.contentEl.ownerDocument.getSelection();
        if (!view?.file || view.getMode() !== 'preview' || !selection?.anchorNode ||
            !selection.focusNode || !view.contentEl.contains(selection.anchorNode) ||
            !view.contentEl.contains(selection.focusNode)) throw new Error('Select text in the active Reading view.');
        const quote = selection.toString();
        const text = await this.app.vault.read(view.file);
        const start = text.indexOf(quote);
        if (!quote || start < 0 || start !== text.lastIndexOf(quote)) {
          throw new Error('The selected text does not identify a unique literal source span. Select it in the editor.');
        }
        await this.prepare(view.file, text, start, start + quote.length);
      })
    });
    this.registerEvent(this.app.vault.on('modify', file => {
      if (this.data.results.some(result => result.draft.source.path === file.path) || this.draft?.source.path === file.path) {
        this.refresh();
      }
    }));
    this.registerEvent(this.app.workspace.on('file-open', () => this.refresh()));
    this.registerEvent(this.app.vault.on('rename', () => this.refresh()));
    this.registerEvent(this.app.vault.on('delete', () => this.refresh()));
    this.registerMarkdownPostProcessor(async (el, context) => {
      const file = this.app.vault.getAbstractFileByPath(context.sourcePath);
      const section = context.getSectionInfo(el);
      if (!(file instanceof TFile) || !section) return;
      const candidates = this.annotations(file.path).filter(({ draft: { source } }) =>
        source.firstLine >= section.lineStart + 1 && source.firstLine <= section.lineEnd + 1);
      if (!candidates.length) return;
      const current = await this.readSource(file);
      for (const { draft } of candidates) {
        if (matchesPassage(draft.source, current.text, current.hash)) {
          el.appendChild(markerButton(el.ownerDocument, () => this.run(() => this.open(draft.id))));
        }
      }
    });

    const plugin = this;
    this.registerEditorExtension(ViewPlugin.fromClass(class {
      decorations: DecorationSet = Decoration.none;
      private revision = 0;

      constructor(private view: EditorView) {
        plugin.editorViews.add(view);
        this.rebuild();
      }
      update(update: ViewUpdate) {
        for (const transaction of update.transactions) {
          for (const effect of transaction.effects) {
            if (effect.is(setDecorations) && effect.value.owner === this.view) this.decorations = effect.value.ranges;
          }
        }
        if (update.docChanged || update.transactions.some(tr => tr.effects.some(effect => effect.is(refreshAnnotations)))) {
          this.decorations = Decoration.none;
          this.rebuild();
        }
      }
      destroy() {
        this.revision++;
        plugin.editorViews.delete(this.view);
      }
      private rebuild() {
        const revision = ++this.revision;
        const doc = this.view.state.doc;
        const leaf = plugin.app.workspace.getLeavesOfType('markdown').find(leaf => leaf.view.containerEl.contains(this.view.dom));
        const file = leaf?.view instanceof MarkdownView ? leaf.view.file : null;
        if (!file || !plugin.annotations(file.path).length) return;
        void plugin.readSource(file).then(({ text, hash }) => {
          if (revision !== this.revision || doc !== this.view.state.doc || text.replace(/\r\n/g, '\n') !== doc.toString()) return;
          const ranges = plugin.annotations(file.path).filter(({ draft }) => matchesPassage(draft.source, text, hash))
            .map(({ draft }) => {
              const end = text.slice(0, draft.source.end).replace(/\r\n/g, '\n').length;
              return Decoration.widget({ widget: new Marker(() => plugin.run(() => plugin.open(draft.id)), draft.id), side: 1 }).range(end);
            });
          this.view.dispatch({ effects: setDecorations.of({ owner: this.view, ranges: Decoration.set(ranges, true) }) });
        }).catch(() => { /* The file may have been closed or removed. */ });
      }
    }, {
      decorations: instance => instance.decorations
    }));
  }

  onunload() {
    this.app.workspace.detachLeavesOfType(viewType);
  }

  private annotations(path: string) {
    return this.data.results.filter(result => result.draft.mode === 'annotation' && result.draft.source.path === path);
  }

  run(fn: () => Promise<unknown>) {
    void fn().catch(error => new Notice('Series Workspace: ' + (error instanceof Error ? error.message : String(error))));
  }

  async open(id?: string) {
    if (id) this.selected = id;
    let leaf = this.app.workspace.getLeavesOfType(viewType)[0];
    if (!leaf) {
      const next = this.app.workspace.getRightLeaf(false);
      if (!next) throw new Error('Could not open the review sidebar.');
      leaf = next;
      await leaf.setViewState({ type: viewType, active: true });
    }
    await this.app.workspace.revealLeaf(leaf);
    if (leaf.view instanceof SeriesView) await leaf.view.draw();
  }

  refresh() {
    for (const leaf of this.app.workspace.getLeavesOfType(viewType)) {
      if (leaf.view instanceof SeriesView) this.run(() => (leaf.view as SeriesView).draw());
    }
    for (const editor of this.editorViews) editor.dispatch({ effects: refreshAnnotations.of() });
  }

  private async readSource(file: TFile) {
    const bytes = await this.app.vault.readBinary(file);
    return { text: new TextDecoder('utf-8', { fatal: true }).decode(bytes), hash: await sha256(bytes) };
  }

  async isCurrent(source: Passage) {
    const file = this.app.vault.getAbstractFileByPath(source.path);
    if (!(file instanceof TFile)) return false;
    const { text, hash } = await this.readSource(file);
    return matchesPassage(source, text, hash);
  }

  private async prepare(file: TFile, displayed: string, start: number, end: number) {
    const { text, hash } = await this.readSource(file);
    if (displayed !== text) {
      if (displayed !== text.replace(/\r\n/g, '\n')) throw new Error('Save the note, then select the passage again.');
      const offsets = [...text.matchAll(/\r\n/g)].map(match => match.index!);
      const toRaw = (offset: number) => {
        for (const cr of offsets) { if (cr >= offset) break; offset++; }
        return offset;
      };
      start = toRaw(start);
      end = toRaw(end);
    }
    const quote = text.slice(start, end);
    if (!quote.trim()) throw new Error('Select a passage first.');
    const line = (offset: number) => text.slice(0, offset).split('\n').length;
    this.draft = this.changeDraft({
      start, end, quote, path: file.path, sha256: hash, firstLine: line(start), lastLine: line(end - 1)
    }, tasks[0], 'preview');
    this.selected = undefined;
    await this.open();
  }

  changeDraft(source: Passage, task: Draft['task'], mode: Mode): Draft {
    const id = this.data.provider;
    const provider = activeProvider({ provider: id, providers: {
      [id]: { apiKey: '', endpoint: '', model: this.data.models[id] ?? '' }
    } });
    return {
      id: crypto.randomUUID(), task, source, mode,
      provider: { id, model: provider.model, endpoint: provider.endpoint },
      createdAt: new Date().toISOString(), privacy: 'vault-local', state: 'dry-request',
      evidence: 'unreviewed', proposer: 'local-operator', sourceRecordId: null, editionId: null, receiptRefs: []
    };
  }

  private serialize(fn: () => Promise<void>) {
    const operation = this.writes.then(fn);
    this.writes = operation.catch(() => {});
    return operation;
  }

  settings(patch: Partial<Omit<SeriesData, 'results'>>) {
    return this.serialize(async () => {
      const next = { ...this.data, ...patch };
      await this.saveData(next);
      this.data = next;
      if (this.draft) this.draft = this.changeDraft(this.draft.source, this.draft.task, this.draft.mode);
      this.refresh();
    });
  }

  saveOutput(draft: Draft, format: 'json' | 'md' | 'html', destination: string, record?: SavedResult) {
    return this.serialize(async () => {
      if (!draft.task.allowedModes.includes(draft.mode) || draft.mode === 'preview') throw new Error('Select a writable output mode.');
      if (!await this.isCurrent(draft.source)) throw new Error('The exact source edition has changed.');
      if (draft.mode === 'annotation' || draft.mode === 'record') {
        if (this.data.results.some(result => result.draft.id === draft.id)) return;
        const next = { ...this.data, results: [...this.data.results, { draft, history: [] }] };
        await this.saveData(next);
        this.data = next;
        this.selected = draft.id;
        this.refresh();
        if (draft.mode === 'annotation') this.app.workspace.getLeavesOfType('markdown').forEach(leaf => {
          if (leaf.view instanceof MarkdownView && leaf.view.file?.path === draft.source.path) leaf.view.previewMode.rerender(true);
        });
        return;
      }
      if (destination !== this.destination(draft, format)) throw new Error('Review the updated destination before writing.');
      const folder = checkedFolder(this.data.outputFolder);
      let directory = '';
      for (const part of folder.split('/')) {
        directory = directory ? directory + '/' + part : part;
        const entry = this.app.vault.getAbstractFileByPath(directory);
        if (!entry) await this.app.vault.createFolder(directory);
        else if (!(entry instanceof TFolder)) throw new Error('The destination contains a file in place of a folder.');
      }
      if (this.app.vault.getAbstractFileByPath(destination)) throw new Error('An output already exists at this destination.');
      const saved = record && this.data.results.find(item => item.draft.id === record.draft.id);
      const json = JSON.stringify(saved
        ? { request: requestEnvelope(saved.draft), reviewHistory: saved.history }
        : requestEnvelope(draft), null, 2);
      const escaped = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      const text = destination.endsWith('.json') ? json + '\n' : destination.endsWith('.html')
        ? '<!doctype html><meta charset="utf-8"><title>Series Workspace dry request</title><pre>' + escaped + '</pre>'
        : '# Series Workspace dry request\n\n' +
          (draft.mode === 'callout' ? '> [!note] Pending human review\n\n' : '') +
          '<pre>' + escaped + '</pre>\n';
      await this.app.vault.create(destination, text);
      new Notice('Series Workspace saved ' + destination);
    });
  }

  destination(draft: Draft, format: 'json' | 'md' | 'html') {
    if (draft.mode === 'preview') return 'Review sidebar';
    if (draft.mode === 'annotation' || draft.mode === 'record') return 'Series Workspace plugin data';
    return checkedFolder(this.data.outputFolder) + '/' + draft.id + '.' + (draft.mode === 'export' ? format : 'md');
  }

  feedback(result: SavedResult, action: Feedback, note: string, replyTo?: string) {
    return this.serialize(async () => {
      const current = this.data.results.find(item => item.draft.id === result.draft.id);
      if (!current || !await this.isCurrent(current.draft.source)) throw new Error('This review belongs to a stale source version.');
      if (!note.trim()) throw new Error('Enter a review note.');
      if (action === 'reply' && !current.history.some(event => event.id === replyTo)) throw new Error('Choose the review event to reply to.');
      const updated: SavedResult = { ...current, history: [...current.history, {
        id: crypto.randomUUID(), action, note: note.trim(), actor: 'local-operator', at: new Date().toISOString(),
        ...(action === 'reply' ? { replyTo } : {})
      }] };
      const next = { ...this.data, results: this.data.results.map(item => item === current ? updated : item) };
      await this.saveData(next);
      this.data = next;
      this.refresh();
    });
  }
}

const setDecorations = StateEffect.define<{ owner: EditorView; ranges: DecorationSet }>();

class SeriesView extends ItemView {
  private generation = 0;
  private format: 'json' | 'md' | 'html' = 'json';
  private role = '';
  private version = '';
  private task = '';
  private standing = '';

  constructor(leaf: WorkspaceLeaf, private plugin: SeriesWorkspace) { super(leaf); }
  getViewType() { return viewType; }
  getDisplayText() { return 'Series Workspace'; }
  async onOpen() { await this.draw(); }
  async onClose() { this.generation++; }

  async draw() {
    const generation = ++this.generation;
    const root = this.contentEl;
    root.empty();
    root.addClass('semantic-series-workspace');
    root.createEl('h2', { text: 'Series Workspace' });
    root.createEl('p', { text: 'Offline pilot. Provider execution is disabled.' });

    const draft = this.plugin.draft;
    if (draft) await this.drawDraft(root, draft, generation);
    else root.createEl('p', { text: 'Select a passage and run a Series Workspace preview command.' });
    if (generation !== this.generation) return;

    const saved = this.plugin.data.results;
    if (saved.length) {
      root.createEl('h3', { text: 'Saved reviews and records' });
      new Setting(root).setName('Filter by task').addDropdown(dropdown => {
        dropdown.addOption('', 'All tasks');
        for (const task of tasks) dropdown.addOption(task.id, task.title + ' / ' + task.taskClass);
        dropdown.setValue(this.task).onChange(value => { this.task = value; this.plugin.run(() => this.draw()); });
      });
      new Setting(root).setName('Filter by role').addDropdown(dropdown => {
        dropdown.addOption('', 'All roles');
        for (const role of roles.roles) dropdown.addOption(role.code, role.title);
        dropdown.setValue(this.role).onChange(value => { this.role = value; this.plugin.run(() => this.draw()); });
      });
      new Setting(root).setName('Filter by source version').addDropdown(dropdown => {
        dropdown.addOption('', 'All versions');
        for (const hash of new Set(saved.map(result => result.draft.source.sha256))) dropdown.addOption(hash, hash.slice(0, 12));
        dropdown.setValue(this.version).onChange(value => { this.version = value; this.plugin.run(() => this.draw()); });
      });
      new Setting(root).setName('Filter by review standing').addDropdown(dropdown => {
        dropdown.addOption('', 'All standings').addOption('unreviewed', 'Unreviewed');
        for (const action of ['accept', 'reject', 'request-change']) dropdown.addOption(action, action);
        dropdown.setValue(this.standing).onChange(value => { this.standing = value; this.plugin.run(() => this.draw()); });
      });
      const filtered = saved.filter(({ draft, history }) => (!this.standing || this.standing ===
        ([...history].reverse().find(event => ['accept', 'reject', 'request-change'].includes(event.action))?.action ?? 'unreviewed')) &&
        (!this.role || draft.task.roles.includes(this.role)) &&
        (!this.task || draft.task.id === this.task) && (!this.version || draft.source.sha256 === this.version));
      for (const result of filtered) {
        const { draft } = result;
        const button = root.createEl('button', { text: draft.source.path + ' · ' + draft.task.title });
        button.onclick = () => { this.plugin.selected = draft.id; this.plugin.run(() => this.draw()); };
      }
      const selected = saved.find(item => item.draft.id === this.plugin.selected);
      if (selected) await this.drawRecord(root, selected, generation);
    }
    if (generation !== this.generation) return;
    const catalog = root.createEl('details');
    catalog.createEl('summary', { text: 'Roles, tasks, rigor, outputs and ORBITS reference' });
    for (const [title, value] of Object.entries({ Roles: roles, Tasks: tasks, Rigor: rigor, Outputs: outputs, 'Pending proposals': pending, ORBITS: orbits })) {
      const section = catalog.createEl('details');
      section.createEl('summary', { text: title });
      section.createEl('pre', { text: JSON.stringify(value, null, 2) });
    }
  }

  private async drawDraft(root: HTMLElement, draft: Draft, generation: number) {
    const current = await this.plugin.isCurrent(draft.source);
    if (generation !== this.generation) return;
    root.createEl('h3', { text: 'Passage preview' });
    root.createEl('p', { text: draft.source.path + ' · lines ' + draft.source.firstLine + '–' + draft.source.lastLine });
    root.createEl('blockquote', { text: draft.source.quote });
    root.createEl('p', { text: current ? 'Exact source hash and passage verified.' : 'Stale source. Select the passage again.' });
    root.createEl('p', { text: 'Permitted context is the selected passage. Identity and supporting evidence are unresolved.' });
    root.createEl('p', { text: 'Configured model: ' + PROVIDERS[draft.provider.id as SeriesProvider].name +
      ' / ' + (draft.provider.model || 'Select a model in settings') + '. Dry run cost: $0. Human review required.' });
    new Setting(root).setName('Task').addDropdown(dropdown => {
      for (const task of tasks) dropdown.addOption(task.id, task.title + ' / ' + task.taskClass);
      dropdown.setValue(draft.task.id).onChange(id => {
        this.plugin.draft = this.plugin.changeDraft(draft.source, tasks.find(task => task.id === id)!, draft.mode);
        this.plugin.run(() => this.draw());
      });
    });
    new Setting(root).setName('Output').addDropdown(dropdown => {
      for (const mode of modes) dropdown.addOption(mode, labels[mode]);
      dropdown.setValue(draft.mode).onChange(mode => {
        this.plugin.draft = this.plugin.changeDraft(draft.source, draft.task, mode as Mode);
        this.plugin.run(() => this.draw());
      });
    });
    if (draft.mode === 'export') new Setting(root).setName('Export format').addDropdown(dropdown => {
      dropdown.addOption('json', 'JSON').addOption('md', 'Markdown').addOption('html', 'HTML');
      dropdown.setValue(this.format).onChange(value => {
        this.format = value as typeof this.format;
        this.plugin.run(() => this.draw());
      });
    });
    let destination = '';
    try { destination = this.plugin.destination(draft, this.format); }
    catch (error) { root.createEl('p', { text: String(error) }); }
    root.createEl('p', { text: 'Destination: ' + destination });
    const preview = root.createEl('details');
    preview.createEl('summary', { text: 'Inspect dry request' });
    preview.createEl('pre', { text: JSON.stringify(requestEnvelope(draft), null, 2) });
    if (current && destination && draft.mode !== 'preview') {
      const button = root.createEl('button', { text: 'Save ' + labels[draft.mode].toLowerCase() });
      const format = this.format;
      button.onclick = () => {
        button.disabled = true;
        this.plugin.run(async () => {
          try { await this.plugin.saveOutput(draft, format, destination); }
          catch (error) { button.disabled = false; throw error; }
        });
      };
    }
  }

  private async drawRecord(root: HTMLElement, record: SavedResult, generation: number) {
    const { draft, history } = record;
    const current = await this.plugin.isCurrent(draft.source);
    if (generation !== this.generation) return;
    const section = root.createEl('section');
    section.createEl('h4', { text: draft.task.title + ' / ' + draft.task.taskClass });
    section.createEl('p', { text: draft.source.path + ' · ' + draft.source.sha256 });
    section.createEl('blockquote', { text: draft.source.quote });
    section.createEl('p', { text: current ? 'Exact source edition' : 'Stale source edition' });
    const details = section.createEl('details');
    details.createEl('summary', { text: 'Saved dry request' });
    details.createEl('pre', { text: JSON.stringify(requestEnvelope(draft), null, 2) });
    for (const event of history) {
      section.createEl('p', { text: event.at + ' · ' + event.actor + ' · ' + event.action + ' · ' + event.note });
    }
    if (!current) return;
    const exportDraft: Draft = { ...draft, mode: 'export' };
    let format: 'json' | 'md' | 'html' = 'json';
    const destination = section.createEl('p');
    const updateDestination = () => { destination.textContent = this.plugin.destination(exportDraft, format); };
    updateDestination();
    new Setting(section).setName('Export saved record').addDropdown(dropdown => {
      dropdown.addOption('json', 'JSON').addOption('md', 'Markdown').addOption('html', 'HTML');
      dropdown.onChange(value => { format = value as typeof format; updateDestination(); });
    }).addButton(button => button.setButtonText('Export').onClick(() => this.plugin.run(() =>
      this.plugin.saveOutput(exportDraft, format, destination.textContent ?? '', record))));
    let action: Feedback = 'comment';
    let replyTo = '';
    let note = '';
    new Setting(section).setName('Review action').addDropdown(dropdown => {
      for (const item of feedbackActions) dropdown.addOption(item, item);
      dropdown.onChange(value => { action = value as Feedback; });
    });
    if (history.length) new Setting(section).setName('Reply to').addDropdown(dropdown => {
      dropdown.addOption('', 'Choose an event');
      for (const event of history) dropdown.addOption(event.id, event.action + ' · ' + event.note.slice(0, 70));
      dropdown.onChange(value => { replyTo = value; });
    });
    new Setting(section).setName('Review note').addTextArea(input => input.onChange(value => { note = value; }));
    const button = section.createEl('button', { text: 'Record review action' });
    button.onclick = () => {
      button.disabled = true;
      this.plugin.run(async () => {
        try { await this.plugin.feedback(record, action, note, replyTo); }
        catch (error) { button.disabled = false; throw error; }
      });
    };
  }
}

class SeriesSettings extends PluginSettingTab {
  constructor(app: SeriesWorkspace['app'], private plugin: SeriesWorkspace) { super(app, plugin); }

  display() {
    this.containerEl.empty();
    this.containerEl.createEl('p', { text: 'The selected provider and model are recorded in dry requests. This build makes no provider requests.' });
    const { provider, models, outputFolder } = this.plugin.data;
    new Setting(this.containerEl).setName('Research provider').addDropdown(dropdown => {
      for (const id of providerIds) dropdown.addOption(id, PROVIDERS[id].name);
      dropdown.setValue(provider).onChange(id => this.plugin.run(async () => {
        await this.plugin.settings({ provider: id as SeriesProvider });
        this.display();
      }));
    });
    new Setting(this.containerEl).setName('Model').addText(input => {
      input.setPlaceholder(PROVIDERS[provider].defaultModel || 'provider/model').setValue(models[provider] ?? '');
      input.inputEl.addEventListener('change', () => this.plugin.run(() =>
        this.plugin.settings({ models: { ...this.plugin.data.models, [provider]: input.getValue().trim() } })));
    });
    new Setting(this.containerEl).setName('Output folder')
      .setDesc('Vault-relative destination for explicitly saved notes and exports.')
      .addText(input => {
        input.setValue(outputFolder);
        input.inputEl.addEventListener('change', () => this.plugin.run(async () => {
          await this.plugin.settings({ outputFolder: checkedFolder(input.getValue()) });
        }));
      });
  }
}
