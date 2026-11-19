const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const body = fs.readFileSync(path.join(__dirname, 'template-body.js'), 'utf8');
const kinds = {page_template:'General', page_template_paper:'Paper', page_template_axiom:'Axiom', page_template_dt_unit:'DT-Unit', page_template_dataview:'Dataview'};
for (const [name, kind] of Object.entries(kinds)) {
    const text = '<%*\nconst templateKind = ' + JSON.stringify(kind) + ';\n' + body + '\n%>\n';
    fs.writeFileSync(path.join(root, '_templates', name + '.md'), text, 'utf8');
}
console.log('Built five standalone Templater templates.');
