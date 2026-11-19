const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const AsyncFunction = Object.getPrototypeOf(async function() {}).constructor;
const root = path.resolve(__dirname, '..');
const names = ['page_template','page_template_paper','page_template_axiom','page_template_dt_unit','page_template_dataview'];
function file(p) { const name = p.split('/').pop(); return {path:p, name, basename:name.slice(0,-3), extension:'md'}; }
async function render(name, paths, current, config, cancel = false) {
    const text = fs.readFileSync(path.join(root, '_templates', name + '.md'), 'utf8');
    assert.ok(text.startsWith('<%*\n') && text.endsWith('%>\n'));
    const code = text.slice(4, -3);
    const tp = {file:{folder:()=>current.split('/').slice(0,-1).join('/'), path:()=>current}, date:{now:()=>'2026-11-18'}, system:{suggester:async()=>cancel ? null : 'Paper'}};
    const app = {vault:{getFiles:()=>paths.map(file), adapter:{exists:async()=>config !== undefined, read:async()=>typeof config === 'string' ? config : JSON.stringify(config)}}};
    return new AsyncFunction('tp','app','let tR="";\n' + code + '\nreturn tR;')(tp, app);
}
for (const name of names) {
    test(name + ': full paths and folder-local home', async () => {
        const result = await render(name, ['00_INDEX.md','Series/00_INDEX.md','Series/A.md','Series/B.md','Elsewhere/A.md'], 'Series/B.md');
        assert.match(result, /data-href="Series\/00_INDEX.md"[^>]*>Folder home/);
        assert.match(result, /data-href="Series\/A.md"[^>]*>Previous note/);
        assert.doesNotMatch(result, /Elsewhere|undefined|\[\[/);
        assert.match(result, /nav-footer nav-footer-sticky/);
    });
}
test('missing current file or links does not invent neighbors', async () => {
    const result = await render('page_template_paper', ['Series/A.md'], 'Series/New.md');
    assert.doesNotMatch(result, /href=|Previous note|Next note|00_Canonical/);
});
test('vault-root file gets root index and correct next note', async () => {
    const result = await render('page_template_paper', ['00_INDEX.md','A.md','B.md'], 'A.md');
    assert.match(result, /data-href="00_INDEX.md"/);
    assert.match(result, /data-href="B.md"[^>]*>Next note/);
});
test('configuration links resolve only existing notes and escape labels', async () => {
    const result = await render('page_template_paper', ['Series & Space/00_INDEX.md','Series & Space/A.md','Map.md'], 'Series & Space/A.md', {links:[{path:'Map',label:'<Map>'},{path:'Missing',label:'Broken'}],vaultHome:'Map'});
    assert.match(result, /&lt;Map&gt;/); assert.doesNotMatch(result, /Broken|href="Missing/);
    assert.match(result, /href="Series%20%26%20Space\/00_INDEX.md"/);
});
test('cancelled prompts and malformed config remain readable', async () => {
    const result = await render('page_template', ['A.md'], 'A.md', '{bad JSON', true);
    assert.match(result, /configuration could not be read/); assert.doesNotMatch(result, /undefined|null/);
});
test('template stats are explicitly a creation-time count', async () => {
    const result = await render('page_template_dataview', ['Series/A.md','Series/B.md','Other/C.md'], 'Series/A.md');
    assert.match(result, /2 Markdown notes in this folder at creation/);
    assert.doesNotMatch(result, /this.file.folder.files/);
});
