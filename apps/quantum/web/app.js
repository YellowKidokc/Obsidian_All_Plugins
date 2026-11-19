// Quantum Papers GUI. Every server action comes from GET /api/actions, the same
// list the CLI uses (python quantum.py --actions), so the palette never drifts.
const $ = id => document.getElementById(id);
let library, actions = [], current = null, original = '', mode = 'read', tab = 'links';
const collapsed = new Set(JSON.parse(safeGet('qp.collapsed') || '[]'));

function safeGet(k) { try { return localStorage.getItem(k); } catch { return null; } }
function safeSet(k, v) { try { localStorage.setItem(k, v); } catch {} }
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fileName = p => p.split('/').pop().replace(/\.md$/i, '');
const vaultName = id => library.vaults.find(v => v.id === id)?.name ?? id;

async function api(path, data) {
  const r = await fetch('/api/' + path, data === undefined ? {} :
    {method: 'POST', headers: {'Content-Type': 'application/json', 'X-QP-Actor': 'gui'}, body: JSON.stringify(data)});
  const v = await r.json();
  if (!r.ok) throw Error(v.error);
  return v;
}

// ── toast ──────────────────────────────────────────────
let toastTimer;
function toast(text, undo = false) {
  $('toastText').textContent = text; $('toastUndo').hidden = !undo; $('toast').hidden = false;
  clearTimeout(toastTimer); toastTimer = setTimeout(() => $('toast').hidden = true, undo ? 8000 : 4000);
}
const fail = e => toast('⚠ ' + e.message);
async function undo() {
  try { const r = await api('run/undo', {}); await refresh(); if (current?.id === r.paper) await openPaper(r.paper, true);
        toast('Moved back to ' + r.back_to); } catch (e) { fail(e); }
}
$('toastUndo').onclick = undo; $('undoBtn').onclick = undo;

// ── tree ───────────────────────────────────────────────
function papersIn(vault, folder) {
  const out = [];
  for (const p of library.papers) {
    const here = p.vault === vault && p.path.split('/').slice(0, -1).join('/') === folder;
    const also = library.locations.some(l => l.paper === p.id && l.vault === vault && l.folder === folder);
    if (here || also) out.push({p, also: also && !here});
  }
  return out.sort((a, b) => a.p.path.localeCompare(b.p.path));
}
function drawTree() {
  let h = '';
  for (const v of library.vaults) {
    h += `<div class="vault">${esc(v.name)}</div>`;
    for (const f of v.folders) {
      const key = v.id + '|' + f, items = papersIn(v.id, f);
      const depth = f ? f.split('/').length : 0;
      const hiddenByParent = f && [...collapsed].some(k => k.startsWith(v.id + '|') && (f + '/').startsWith(k.split('|')[1] + '/') && k !== key && k.split('|')[1] !== '');
      if (hiddenByParent) continue;
      h += `<div class="folder" data-key="${esc(key)}" style="padding-left:${8 + depth * 14}px">${collapsed.has(key) ? '▸' : '▾'} 📁 ${esc(f.split('/').pop() || 'root')}</div>`;
      if (collapsed.has(key)) continue;
      for (const {p, also} of items)
        h += `<div class="paper ${current?.id === p.id ? 'sel' : ''} " data-id="${p.id}" style="padding-left:${24 + depth * 14}px" title="${esc(vaultName(p.vault) + ' / ' + p.path)}">📄 ${esc(fileName(p.path))}${also ? '<span class="tag">↗ shown here</span>' : ''}${p.status === 'stale' ? '<span class="tag">⚠ stale</span>' : ''}</div>`;
    }
  }
  const stale = library.papers.filter(p => p.status === 'stale').length;
  h += `<div class="vault">Queues</div><div class="queue" data-q="stale">⚠ Stale papers <span class="count">${stale}</span></div>
        <div class="queue" data-q="tangents">↳ Tangents <span class="count">${library.tangents?.length ?? 0}</span></div>`;
  $('tree').innerHTML = h || '<p class="mute">No vaults yet. Start with <code>--vault PATH</code> or <code>--demo</code>.</p>';
}
$('tree').onclick = e => {
  const f = e.target.closest('.folder'), p = e.target.closest('.paper'), q = e.target.closest('.queue');
  if (f) { const k = f.dataset.key; collapsed.has(k) ? collapsed.delete(k) : collapsed.add(k); safeSet('qp.collapsed', JSON.stringify([...collapsed])); drawTree(); }
  if (p) openPaper(p.dataset.id).catch(fail);
  if (q) openPalette(q.dataset.q === 'stale' ? 'stale' : 'tangent');
};
$('tree').oncontextmenu = e => {
  const p = e.target.closest('.paper'); if (!p) return;
  e.preventDefault(); openPaper(p.dataset.id).then(() => showMenu(e.clientX, e.clientY)).catch(fail);
};

// ── paper view ─────────────────────────────────────────
async function openPaper(id, force = false) {
  if (!force && !safeToLeave()) return;
  current = await api('paper/' + encodeURIComponent(id)); original = current.content;
  $('empty').hidden = true; $('paperView').hidden = false;
  $('title').textContent = fileName(current.path);
  $('origin').textContent = `Original: ${vaultName(current.vault)} / ${current.path}`;
  $('editor').value = current.content;
  history.replaceState(null, '', '#paper=' + current.id);
  setMode(mode); drawTree(); drawSide();
}
function safeToLeave() { return !current || $('editor').value === original || confirm('Discard unsaved edits?'); }
function setMode(m) {
  mode = m; $('mRead').classList.toggle('on', m === 'read'); $('mEdit').classList.toggle('on', m === 'edit');
  $('read').hidden = m !== 'read'; $('editor').hidden = m !== 'edit'; $('save').hidden = m !== 'edit';
  if (m === 'read') $('read').innerHTML = render($('editor').value);
}
$('mRead').onclick = () => setMode('read'); $('mEdit').onclick = () => setMode('edit');
$('save').onclick = async () => { try { await api('save', {paper: current.id, content: $('editor').value}); original = $('editor').value; toast('Saved. Every place this paper shows opens the same file.'); } catch (e) { fail(e); } };
$('editor').oninput = () => drawSide();
$('moreBtn').onclick = e => { const r = e.target.getBoundingClientRect(); showMenu(r.left - 150, r.bottom + 4); };

// Markdown → HTML with CriticMarkup colors, so AI suggestions are visible in Read mode.
function inline(s) {
  return esc(s)
    .replace(/\{\+\+(.+?)\+\+\}/g, '<ins class="cm">$1</ins>')
    .replace(/\{--(.+?)--\}/g, '<del class="cm">$1</del>')
    .replace(/\{~~(.+?)~&gt;(.+?)~~\}/g, '<del class="cm">$1</del><ins class="cm">$2</ins>')
    .replace(/\{==(.+?)==\}/g, '<mark class="cm">$1</mark>')
    .replace(/\{&gt;&gt;(.+?)&lt;&lt;\}/g, '<span class="cm-com">💬 $1</span>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/\*(.+?)\*/g, '<em>$1</em>').replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/\[([^\]]+)\]\(#paper=([\w-]+)\)/g, '<a data-paper="$2">$1</a>')
    .replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (m, t, l) => `<a data-wiki="${t}">${l || t}</a>`);
}
function render(src) {
  return src.replace(/^---\n[\s\S]*?\n---\n/, '').split(/\n{2,}/).map(b => {
    const h = b.match(/^(#{1,6}) (.*)/); if (h) return `<h${h[1].length}>${inline(h[2])}</h${h[1].length}>`;
    if (/^[-*] /.test(b)) return '<ul>' + b.split('\n').map(l => `<li>${inline(l.replace(/^[-*] /, ''))}</li>`).join('') + '</ul>';
    if (/^> /.test(b)) return `<blockquote>${inline(b.replace(/^> /gm, ''))}</blockquote>`;
    return `<p>${inline(b).replace(/\n/g, '<br>')}</p>`;
  }).join('');
}
$('read').onclick = e => {
  const a = e.target.closest('a'); if (!a) return;
  if (a.dataset.paper) openPaper(a.dataset.paper).catch(fail);
  if (a.dataset.wiki) { const p = library.papers.find(p => fileName(p.path).toLowerCase() === a.dataset.wiki.toLowerCase()); p ? openPaper(p.id).catch(fail) : toast('No registered paper named ' + a.dataset.wiki); }
};

// ── side panel ─────────────────────────────────────────
document.querySelectorAll('.tabs button').forEach(b => b.onclick = () => { tab = b.dataset.tab; document.querySelectorAll('.tabs button').forEach(x => x.classList.toggle('on', x === b)); drawSide(); });
async function drawSide() {
  if (!current) return;
  const body = $('sideBody');
  if (tab === 'links') {
    const text = $('editor').value, out = [];
    for (const m of text.matchAll(/\[([^\]]+)\]\(#paper=([\w-]+)\)/g)) out.push(`<div class="item"><a data-paper="${m[2]}">${esc(m[1])}</a></div>`);
    for (const m of text.matchAll(/\[\[([^\]|]+)/g)) out.push(`<div class="item"><a data-wiki="${esc(m[1])}">${esc(m[1])}</a> <span class="mute">wiki link</span></div>`);
    const shown = library.locations.filter(l => l.paper === current.id);
    body.innerHTML = '<b>Links out</b>' + (out.join('') || '<p class="mute">No links.</p>') +
      '<b>Also shown in</b>' + (shown.map(l => `<div class="item">📁 ${esc(vaultName(l.vault))} / ${esc(l.folder || 'root')}</div>`).join('') || '<p class="mute">Only its home folder.</p>');
  } else if (tab === 'history') {
    const {events} = await api('history/' + current.id);
    body.innerHTML = events.map(e => `<div class="item"><b>${esc(e.action)}</b> · ${esc(e.actor)}<br><span class="when">${esc(e.at.replace('T', ' '))}</span>${e.source ? `<br>${esc(e.source)} → ${esc(e.target)}` : e.target ? `<br>${esc(e.target)}` : ''}</div>`).join('') || '<p class="mute">No history yet.</p>';
  } else {
    const t = current.tangents ?? [];
    body.innerHTML = (Array.isArray(t) ? t : []).map(x => `<div class="item"><b>${esc(x.title)}</b><br><span class="mute">${esc(x.scope)} · ${esc(x.status)}</span></div>`).join('') || '<p class="mute">No tangents. Use ⋯ → Make a tangent.</p>';
  }
}
$('sideBody').onclick = e => $('read').onclick(e);

// ── run an action (shared by palette, menu, ⋯ button) ──
function pickFolder(title) {
  return new Promise(resolve => {
    $('pickTitle').textContent = title; $('pickSel').innerHTML = '';
    for (const v of library.vaults) for (const f of v.folders)
      $('pickSel').add(new Option(`${v.name} / ${f || '(root)'}`, JSON.stringify({vault: v.id, folder: f})));
    $('picker').onclose = () => resolve($('picker').returnValue === 'ok' ? JSON.parse($('pickSel').value) : null);
    $('picker').returnValue = ''; $('picker').showModal();
  });
}
async function run(a) {
  const args = {};
  if (a.args.includes('paper')) { if (!current) return toast('Open a paper first'); args.paper = current.id; }
  if (a.needs === 'paper+folder') { const d = await pickFolder(a.label); if (!d) return; Object.assign(args, d); }
  if (a.needs === 'folder+folder') {
    const s = await pickFolder('Folder to move'); if (!s) return;
    const d = await pickFolder('Move it into…'); if (!d) return;
    Object.assign(args, s, {dest_vault: d.vault, dest_folder: d.folder});
  }
  if (a.needs === 'path') { const v = library.vaults[0]; const p = prompt('Markdown path inside ' + v.name + ':'); if (!p) return; Object.assign(args, {vault: v.id, path: p}); }
  if (a.needs === 'file') { const f = prompt('Save backup as (full path):', 'quantum-backup.json'); if (!f) return; args.file = f; }
  if (a.name === 'move' && !safeToLeave()) return;
  try {
    const r = await api('run/' + a.name, args);
    if (a.name === 'history') { tab = 'history'; document.querySelector('[data-tab=history]').click(); return; }
    await refresh();
    if (current) await openPaper(r.id && a.name === 'tangent' ? r.id : current.id, true);
    toast(`✓ ${a.label}` + (r.moved ? ` (${r.moved.length} papers)` : ''), a.name === 'move' || a.name === 'move-folder');
  } catch (e) { fail(e); }
}

// ── command palette ────────────────────────────────────
let options = [], sel = 0;
const local = [
  {label: 'Copy permanent link', group: 'Connect', go: async () => { if (!current) return; const url = location.origin + '/#paper=' + current.id; try { await navigator.clipboard.writeText(url); toast('Link copied'); } catch { toast(url); } }},
  {label: 'Switch Read / Edit', group: 'Write', go: () => current && setMode(mode === 'read' ? 'edit' : 'read')},
  {label: 'Open in Obsidian', group: 'Connect', go: () => { if (!current) return; location.href = `obsidian://open?vault=${encodeURIComponent(vaultName(current.vault))}&file=${encodeURIComponent(current.path)}`; }},
];
function openPalette(q = '') { $('pq').value = q; $('palette').showModal(); fill(); $('pq').focus(); }
function fill() {
  const q = $('pq').value.toLowerCase().trim();
  const acts = [...actions.map(a => ({label: a.label, group: a.group, go: () => run(a)})), ...local];
  const papers = library.papers.map(p => ({label: fileName(p.path), group: (p.status === 'stale' ? 'stale · ' : '') + vaultName(p.vault), paper: p.id, go: () => openPaper(p.id).catch(fail)}));
  const match = o => !q || (o.label + ' ' + o.group).toLowerCase().includes(q);
  options = [...acts.filter(match), ...papers.filter(match)].slice(0, 60); sel = 0; drawOptions();
}
function drawOptions() {
  $('plist').innerHTML = options.map((o, i) => `<div class="opt ${i === sel ? 'on' : ''}" data-i="${i}">${o.paper ? '📄' : '⚡'} ${esc(o.label)}<small>${esc(o.group)}</small></div>`).join('') || '<p class="mute" style="padding:10px">Nothing matches.</p>';
  $('plist').children[sel]?.scrollIntoView({block: 'nearest'});
}
function choose(i) { const o = options[i]; $('palette').close(); o?.go(); }
$('pq').oninput = fill;
$('pq').onkeydown = e => {
  if (e.key === 'ArrowDown') { sel = Math.min(sel + 1, options.length - 1); drawOptions(); e.preventDefault(); }
  if (e.key === 'ArrowUp') { sel = Math.max(sel - 1, 0); drawOptions(); e.preventDefault(); }
  if (e.key === 'Enter') choose(sel);
};
$('plist').onclick = e => { const o = e.target.closest('.opt'); if (o) choose(+o.dataset.i); };
$('paletteOpen').onclick = () => openPalette();
document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); openPalette(); }
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's' && current && mode === 'edit') { e.preventDefault(); $('save').click(); }
  if (e.key === 'Escape') $('menu').hidden = true;
});

// ── right-click / ⋯ menu ───────────────────────────────
function showMenu(x, y) {
  const items = [...actions.filter(a => a.args.includes('paper') || a.name === 'history'), ...local];
  $('menu').innerHTML = items.map((a, i) => `<div data-i="${i}">${esc(a.label)}</div>`).join('');
  $('menu').style.left = Math.max(8, Math.min(x, innerWidth - 230)) + 'px'; $('menu').style.top = Math.min(y, innerHeight - 300) + 'px'; $('menu').hidden = false;
  $('menu').onclick = e => { const d = e.target.closest('[data-i]'); if (!d) return; $('menu').hidden = true; const a = items[+d.dataset.i]; a.go ? a.go() : run(a); };
}
document.addEventListener('click', e => { if (!e.target.closest('#menu') && e.target.id !== 'moreBtn') $('menu').hidden = true; });

// ── start ──────────────────────────────────────────────
async function refresh() { library = await api('library'); drawTree(); }
window.addEventListener('beforeunload', e => { if (current && $('editor').value !== original) { e.preventDefault(); e.returnValue = ''; } });
try {
  [{actions}] = await Promise.all([api('actions'), refresh()]);
  if (location.hash.startsWith('#paper=')) await openPaper(location.hash.slice(7));
} catch (e) { fail(e); }
