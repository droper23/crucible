#!/usr/bin/env node
// Validate every problem in every language through the real companion runner.
//   - Python reference solution must pass all tests via the generated harness.
//   - refs[lang] (optional C/C++/Rust/ESPresso references) must pass all tests.
//   - Otherwise the generated starter must compile and report a result for every test.
//   - Assembly problems: asm_solution must pass all tests.
//
// usage: node tools/check.mjs [problems.json] [--track ID] [--problem ID] [--langs python,c,...] [-j N]
import { spawn } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildRun, parseRun, starterCode, languagesFor } from '../site/js/harness.js';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const file = argv[0] && !argv[0].startsWith('-') ? argv[0] : join(ROOT, 'site/data/problems.json');
const data = JSON.parse(readFileSync(file, 'utf8'));
const onlyTrack = opt('--track');
const onlyProblem = opt('--problem');
const onlyLangs = opt('--langs')?.split(',');
const jobs = Number(opt('-j', '6'));
const port = 47000 + Math.floor(Math.random() * 900);

const server = spawn('python3', [join(ROOT, 'companion/server.py')], { env: { ...process.env, CRUCIBLE_PORT: String(port) }, stdio: ['ignore', 'pipe', 'inherit'] });
await new Promise((res) => server.stdout.once('data', res));

async function run(req) {
  const r = await fetch(`http://127.0.0.1:${port}/api/run`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Crucible': '1' }, body: JSON.stringify(req) });
  const j = await r.json();
  if (j.error) throw new Error(j.error);
  return j;
}

const tasks = [];
for (const p of data.problems) {
  if (onlyTrack && p.track !== onlyTrack) continue;
  if (onlyProblem && p.id !== onlyProblem) continue;
  for (const lang of languagesFor(p)) {
    if (onlyLangs && !onlyLangs.includes(lang)) continue;
    let code, mustPass;
    if (lang === 'python') { code = p.solution; mustPass = true; }
    else if (lang === 'asm') { code = p.asm_solution; mustPass = true; }
    else if (lang === 'x86') { code = p.x86_solution; mustPass = true; }
    else if (p.refs?.[lang]) { code = p.refs[lang]; mustPass = true; }
    else { code = starterCode(p, lang); mustPass = false; }
    if (!code) { tasks.push({ p, lang, skip: 'no code' }); continue; }
    if (!mustPass && p.kind === 'io') continue; // io starters print nothing; nothing to check
    tasks.push({ p, lang, code, mustPass });
  }
}

let fails = 0, done = 0;
const failures = [];
async function check(t) {
  if (t.skip) { failures.push(`${t.p.id} [${t.lang}]: ${t.skip}`); fails++; return; }
  const req = buildRun(t.p, t.lang, t.code, t.p.tests);
  const res = await run(req);
  const parsed = parseRun(t.p, t.lang, t.p.tests, res);
  let problem = null;
  if (parsed.compileError) problem = `compile error:\n${parsed.compileError.slice(0, 1500)}`;
  else {
    const bad = parsed.results.filter((r) => (t.mustPass ? r.status !== 'pass' : !['pass', 'fail'].includes(r.status)));
    if (bad.length) {
      const b = bad[0];
      problem = `${bad.length}/${parsed.results.length} tests ${t.mustPass ? 'not passing' : 'without a result'}; first: #${b.index} ${b.status} got=${JSON.stringify(b.got)?.slice(0, 200)} expected=${JSON.stringify(b.expected)?.slice(0, 200)} ${b.error ? 'error=' + String(b.error).slice(0, 400) : ''}\nstderr: ${(parsed.stderr || '').slice(0, 800)}`;
    }
  }
  done++;
  if (problem) { fails++; failures.push(`${t.p.id} [${t.lang}${t.mustPass ? ' ref' : ' starter'}]: ${problem}`); process.stdout.write('x'); }
  else process.stdout.write('.');
}

const queue = tasks.slice();
await Promise.all(Array.from({ length: jobs }, async () => { while (queue.length) { const t = queue.shift(); await check(t).catch((e) => { fails++; failures.push(`${t.p.id} [${t.lang}]: ${e}`); }); } }));
server.kill();
console.log(`\n${tasks.length} checks, ${fails} failed`);
for (const f of failures) console.log(' ✗', f);
process.exit(fails ? 1 : 0);
