const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const esbuild = require('esbuild');
const root = path.resolve(__dirname, '..');
function bundle(source) {
  const output = esbuild.buildSync({stdin:{contents:source,resolveDir:root,sourcefile:'startup-test.tsx',loader:'tsx'},bundle:true,platform:'node',format:'cjs',write:false,jsx:'automatic'}).outputFiles[0].text;
  const mod = {exports:{}};
  new Function('require','module','exports',output)(require,mod,mod.exports);
  return mod.exports;
}
const runtime = bundle('export { isTauri } from "./src/lib/filesystem";');
test('runtime detection is false outside a browser', () => {
  delete global.window;
  assert.equal(runtime.isTauri(),false);
});
test('runtime detection is false in an ordinary browser', () => {
  global.window = {};
  try { assert.equal(runtime.isTauri(),false); } finally { delete global.window; }
});
test('the installed Tauri API runtime marker works without the legacy global API', () => {
  global.window = {};
  global.isTauri = true;
  try { assert.equal(runtime.isTauri(),true); } finally { delete global.window; delete global.isTauri; }
});
test('a legacy global alone is not mistaken for initialized Tauri v2', () => {
  global.window = {__TAURI__:{}};
  try { assert.equal(runtime.isTauri(),false); } finally { delete global.window; }
});
test('the actual app provider renders without a callback declaration error', () => {
  const result = bundle('import { createElement } from "react"; import { renderToString } from "react-dom/server"; import { AppProvider } from "./src/store/AppContext"; export const html = renderToString(createElement(AppProvider, null, createElement("span", null, "startup ok")));');
  assert.match(result.html,/startup ok/);
});
