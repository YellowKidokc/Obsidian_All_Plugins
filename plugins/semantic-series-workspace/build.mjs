import esbuild from '../semantic-ai/node_modules/esbuild/lib/main.js';

await esbuild.build({
  entryPoints: ['src/main.ts'],
  bundle: true,
  external: ['obsidian', '@codemirror/state', '@codemirror/view'],
  loader: { '.md': 'text' },
  format: 'cjs',
  target: 'es2018',
  outfile: 'main.js'
});
