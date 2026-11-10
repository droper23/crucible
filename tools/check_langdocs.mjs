// Validate site/js/langdocs/*.js: node tools/check_langdocs.mjs [lang...]
import { readdirSync } from 'node:fs';
const dir = new URL('../site/js/langdocs/', import.meta.url);
const want = process.argv.slice(2);
const NEEDS_RET = new Set(['function', 'method', 'macro']);
let bad = 0;
for (const f of readdirSync(dir).filter((f) => f.endsWith('.js'))) {
  const lang = f.replace('.js', '');
  if (want.length && !want.includes(lang)) continue;
  const arr = (await import(new URL(f, dir))).default;
  const seen = new Set();
  const err = (e, m) => { bad++; console.log(`${lang}: ${e.owner ? e.owner + '.' : ''}${e.name}: ${m}`); };
  for (const e of arr) {
    const key = `${e.owner || ''}|${e.name}|${e.kind}`;
    if (seen.has(key)) err(e, 'duplicate');
    seen.add(key);
    if (!e.name || !e.kind || !e.sig || !e.doc) err(e, 'missing name/kind/sig/doc');
    if (!e.example) err(e, 'missing example');
    if (NEEDS_RET.has(e.kind) && !e.returns) err(e, 'missing returns');
    if (e.kind === 'method' && !e.owner) err(e, 'method without owner');
    const inner = (e.sig.match(/\((.*)\)/s) || [, ''])[1];
    for (const p of e.params || []) if (!inner.includes(p.label)) err(e, `param label "${p.label}" not in sig parens`);
  }
  console.log(`${lang}: ${arr.length} entries`);
}
console.log(bad ? `${bad} problems` : 'langdocs OK');
process.exit(bad ? 1 : 0);
