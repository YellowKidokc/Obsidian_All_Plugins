<%*
const templateKind = "Dataview";
// Embedded into each template by build-templates.cjs. Runs inside Templater.
const cleanPath = value => String(value || '').replace(/\\/g, '/').replace(/^\/+|\/+$/g, '');
const escapeHtml = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const folderPath = cleanPath(tp.file.folder(true));
const currentPath = cleanPath(tp.file.path(true));
const folderLabel = folderPath.split('/').pop() || 'Vault';
const join = name => folderPath ? folderPath + '/' + name : name;
const warnings = [];
let config = {};
const configPath = '_templates/navigation.config.json';
if (app.vault.adapter && await app.vault.adapter.exists(configPath)) {
    try {
        config = JSON.parse(await app.vault.adapter.read(configPath));
        if (!config || Array.isArray(config) || typeof config !== 'object') throw new Error('Expected a JSON object');
    } catch (error) {
        config = {};
        warnings.push('Navigation configuration could not be read; using folder links only.');
    }
}
const allNotes = app.vault.getFiles().filter(file => file.extension === 'md');
const find = value => {
    if (typeof value !== 'string' || !value.trim()) return null;
    const path = cleanPath(value);
    if (path.split('/').some(part => part === '..' || part === '.')) return null;
    return allNotes.find(file => file.path === path || file.path === path + '.md') || null;
};
const link = (file, label) => {
    if (!file) return '';
    const href = file.path.split('/').map(encodeURIComponent).join('/');
    return '<a class="internal-link" data-href="' + escapeHtml(file.path) + '" href="' + escapeHtml(href) + '">' + escapeHtml(label || file.basename) + '</a>';
};
const indexes = ['00_INDEX', '_INDEX', 'index', 'README'];
const home = indexes.map(name => find(join(name))).find(Boolean) || null;
const vaultHome = find(config.vaultHome) || indexes.map(find).find(Boolean) || null;
const recent = find(config.recent);
const inFolder = allNotes.filter(file => cleanPath(file.path.split('/').slice(0, -1).join('/')) === folderPath);
const siblings = inFolder.filter(file => !indexes.some(name => file.basename === name))
    .sort((a, b) => a.name.localeCompare(b.name));
const currentIdx = siblings.findIndex(file => file.path === currentPath);
const previous = currentIdx > 0 ? siblings[currentIdx - 1] : null;
const next = currentIdx >= 0 && currentIdx + 1 < siblings.length ? siblings[currentIdx + 1] : null;
let noteType = templateKind;
let domain = '';
if (templateKind === 'General' || templateKind === 'Dataview') {
    noteType = await tp.system.suggester(['Paper','Axiom','Theorem','Claim','Note','Index'], ['Paper','Axiom','Theorem','Claim','Note','Index']) || 'Note';
}
if (templateKind !== 'Axiom' && templateKind !== 'DT-Unit') {
    domain = await tp.system.suggester(['Physics','Theology','Consciousness','Information','Mathematics','Multiple'], ['Physics','Theology','Consciousness','Information','Mathematics','Multiple']) || '';
}
const navLinks = (Array.isArray(config.links) ? config.links : [])
    .filter(item => item && typeof item === 'object')
    .map(item => link(find(item.path), typeof item.label === 'string' ? item.label : undefined)).filter(Boolean);
const footerLinks = [link(home, 'Folder home'), link(previous, 'Previous note'), link(next, 'Next note'), link(recent, 'Recent'), link(vaultHome, 'Vault home')].filter(Boolean);
const summary = [noteType, domain, 'Created from template: ' + tp.date.now('YYYY-MM-DD')].filter(Boolean).map(escapeHtml).join(' · ');
const stats = templateKind === 'Dataview' ? '<div class="banner-row">' + inFolder.length + ' Markdown notes in this folder at creation</div>\n' : '';
tR += '<div class="dashboard-banner">\n<div class="banner-title">THEOPHYSICS · ' + escapeHtml(folderLabel) + '</div>\n';
if (navLinks.length) tR += '<div class="banner-nav">' + navLinks.join(' · ') + '</div>\n';
tR += '<div class="banner-row"><span class="banner-status draft">Draft</span> ' + summary + '</div>\n' + stats + '</div>\n\n---\n\n[YOUR CONTENT HERE]\n\n---\n\n';
if (footerLinks.length) tR += '<div class="nav-footer nav-footer-sticky">\n' + footerLinks.join(' · ') + '\n</div>\n';
if (warnings.length) tR += '\n> ' + warnings.map(escapeHtml).join(' ') + '\n';

%>
