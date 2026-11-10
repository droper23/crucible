// Crucible app: router + pages.
import { store, dayKey } from './store.js';
import { detectCompanion, onCompanion, companionInfo, execute, unavailableReason, warmPython, connectBridge, bridgeNeeded } from './runner.js';
import { LANGS, languagesFor, starterCode, buildRun, parseRun, signature, formatValue, camel } from './harness.js';
import { createEditor, monacoTheme, loadMonaco } from './editor.js';
import { md, renderMd, enhance, esc } from './md.js';
import { mountCoach } from './coach.js';
import { setIdeContext, introducedEntries, entryCard, parseDiagnostics, showDiagnostics, clearDiagnostics, trackDiagnosticEdits } from './ide.js';

const DIFF = ['First Steps', 'Easy', 'Medium', 'Hard', 'Expert'];
const hintsFor = (p, lang) => (lang === 'x86' && p.x86_hints?.length ? p.x86_hints : p.hints);
const LANG_SHORT = { python: 'PY', c: 'C', cpp: 'C++', rust: 'RS', espresso: 'ESP', asm: 'ARM', x86: 'x86' };
const $app = document.getElementById('app');
let DATA = null;
let byId = new Map();
let cleanup = [];

// ------------------------------------------------------------------ utils
const h = (html) => { const t = document.createElement('template'); t.innerHTML = html.trim(); return t.content.firstElementChild; };
const diffPill = (d) => `<span class="pill diff diff-${d}">${DIFF[d]}</span>`;
const fmtDate = (t) => new Date(t).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });

export function toast(msg, ms = 2400) {
  const el = h(`<div class="toast">${esc(msg)}</div>`);
  document.getElementById('toast-root').append(el);
  setTimeout(() => el.remove(), ms);
}

function modal(html, { onMount } = {}) {
  const root = document.getElementById('modal-root');
  const el = h(`<div class="modal-backdrop"><div class="modal card">${html}</div></div>`);
  const close = () => el.remove();
  el.addEventListener('click', (e) => { if (e.target === el || e.target.closest('[data-close]')) close(); });
  root.append(el);
  onMount?.(el, close);
  return close;
}

function applyTheme() {
  const t = store.settings().theme;
  const dark = t === 'dark' || (t === 'system' && matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  window.monaco?.editor.setTheme(monacoTheme());
}
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme);

function trackOf(p) { return DATA.tracks.find((t) => t.id === p.track); }
function trackProgress(t) {
  const solved = t.problems.filter((id) => store.isSolved(id)).length;
  return { solved, total: t.problems.length, pct: t.problems.length ? Math.round((solved / t.problems.length) * 100) : 0 };
}
function nextProblem() {
  const last = store.get().lastProblem && byId.get(store.get().lastProblem);
  if (last && !store.isSolved(last.id)) return last;
  if (last) {
    const t = trackOf(last);
    const i = t.problems.indexOf(last.id);
    const after = t.problems.slice(i + 1).find((id) => !store.isSolved(id));
    if (after) return byId.get(after);
  }
  return DATA.problems.find((p) => !store.isSolved(p.id)) || DATA.problems[0];
}

// ------------------------------------------------------------------ router
const routes = [
  [/^#?\/?$/, pageHome],
  [/^#\/problems$/, pageProblems],
  [/^#\/track\/([\w-]+)$/, pageTrack],
  [/^#\/p\/([\w-]+)$/, pageProblem],
  [/^#\/cheatsheets(?:\/([\w-]+))?$/, pageCheatsheets],
  [/^#\/settings$/, pageSettings],
];

async function route() {
  cleanup.forEach((f) => { try { f(); } catch {} });
  cleanup = [];
  $app.classList.remove('workspace-mode');
  const hash = location.hash || '#/';
  document.querySelectorAll('[data-nav]').forEach((a) => {
    const n = a.dataset.nav;
    a.classList.toggle('active', (n === 'home' && hash === '#/') || (n !== 'home' && hash.startsWith(`#/${n}`)) || (n === 'problems' && (hash.startsWith('#/p/') || hash.startsWith('#/track/'))));
  });
  for (const [re, fn] of routes) {
    const m = re.exec(hash);
    if (m) { await fn(...m.slice(1)); $app.focus({ preventScroll: true }); return; }
  }
  $app.innerHTML = `<div class="page"><div class="empty">Page not found. <a href="#/">Go home</a></div></div>`;
}

// ------------------------------------------------------------------ home
function pageHome() {
  document.title = 'Crucible';
  const solved = DATA.problems.filter((p) => store.isSolved(p.id));
  const total = DATA.problems.length;
  const streak = store.streak();
  const next = nextProblem();
  const byDiff = [0, 1, 2, 3, 4].map((d) => ({ d, total: DATA.problems.filter((p) => p.difficulty === d).length, solved: solved.filter((p) => p.difficulty === d).length }));
  const subsCount = Object.values(store.get().subs).reduce((a, l) => a + l.length, 0);
  const langsUsed = new Set(Object.values(store.get().solved).flatMap((s) => s.langs));
  const hour = new Date().getHours();
  const greet = hour < 5 ? 'Burning the midnight oil' : hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';
  const nt = trackOf(next);

  $app.innerHTML = `
  <div class="page">
    <section class="hero">
      <div class="hero-grid">
        <div>
          <h1>${greet}. <span class="grad">Let's forge something.</span></h1>
          <p class="sub">${solved.length ? `You've solved ${solved.length} of ${total} problems${streak ? ` and you're on a ${streak}-day streak 🔥` : ''}.` : `${total} problems across ${DATA.tracks.length} tracks, from your very first program to expert algorithms. Start at the top of the path, or jump anywhere.`}</p>
        </div>
        <a class="continue-card" href="#/p/${next.id}">
          <div class="eyebrow">${store.isAttempted(next.id) ? 'Continue where you left off' : solved.length ? 'Up next' : 'Start here'}</div>
          <div class="title">${esc(next.title)}</div>
          <div class="row" style="display:flex;gap:6px;align-items:center">${diffPill(next.difficulty)}<span class="pill">${esc(nt.icon || '')} ${esc(nt.title)}</span><span style="margin-left:auto;color:var(--accent);font-weight:700">Open →</span></div>
        </a>
      </div>
    </section>

    <div class="stats">
      <div class="card stat"><div class="v">${solved.length}<span style="font-size:15px;color:var(--muted);font-weight:600"> / ${total}</span></div><div class="k">Problems solved</div>
        <div class="bar">${byDiff.map((x) => `<span style="width:${(x.solved / total) * 100}%;background:var(--d${x.d})"></span>`).join('')}</div></div>
      <div class="card stat"><div class="v">${streak}<span style="font-size:15px;color:var(--muted);font-weight:600"> day${streak === 1 ? '' : 's'}</span></div><div class="k">Current streak</div></div>
      <div class="card stat"><div class="v">${subsCount}</div><div class="k">Submissions</div></div>
      <div class="card stat"><div class="v">${langsUsed.size}<span style="font-size:15px;color:var(--muted);font-weight:600"> / 6</span></div><div class="k">Languages used</div></div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1.4fr;gap:14px;margin-top:14px" class="home-2">
      <div class="card diff-breakdown">
        ${byDiff.map((x) => `<div class="diff-row"><span style="color:var(--d${x.d});font-weight:600">${DIFF[x.d]}</span><div class="track"><span style="width:${x.total ? (x.solved / x.total) * 100 : 0}%;background:var(--d${x.d})"></span></div><span class="n">${x.solved}/${x.total}</span></div>`).join('')}
      </div>
      <div class="card heatmap-wrap">
        <div style="font-size:13px;font-weight:600;margin-bottom:10px">Activity <span style="color:var(--muted);font-weight:500">· last 26 weeks</span></div>
        ${heatmap()}
      </div>
    </div>

    <div class="section-title"><h2>Learning path</h2><a href="#/problems">Browse all problems →</a></div>
    <div class="path">
      ${DATA.tracks.map((t, i) => { const pr = trackProgress(t); return `
        <a class="card track-card ${pr.solved === pr.total && pr.total ? 'done' : ''}" href="#/track/${t.id}">
          <div class="head"><div class="track-icon">${esc(t.icon || '◆')}</div><div><div class="num">TRACK ${i + 1}</div><h3>${esc(t.title)}</h3></div></div>
          <p>${esc(t.blurb)}</p>
          <div class="progress"><span style="width:${pr.pct}%"></span></div>
          <div class="meta"><span>${pr.solved}/${pr.total} solved</span><span>${diffRange(t)}</span></div>
        </a>`; }).join('')}
    </div>
  </div>`;
  if (innerWidth < 900) $app.querySelector('.home-2').style.gridTemplateColumns = '1fr';
}

function diffRange(t) {
  const ds = t.problems.map((id) => byId.get(id).difficulty);
  const lo = Math.min(...ds), hi = Math.max(...ds);
  return lo === hi ? DIFF[lo] : `${DIFF[lo]} → ${DIFF[hi]}`;
}

function heatmap() {
  const act = store.get().activity;
  const days = 26 * 7;
  const end = new Date();
  const start = new Date(end);
  start.setDate(end.getDate() - days + 1 - end.getDay() + 6 - 6); // align
  start.setDate(start.getDate() - start.getDay());
  const cells = [];
  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    const n = act[dayKey(d)] || 0;
    const l = n === 0 ? 0 : n === 1 ? 1 : n <= 3 ? 2 : n <= 5 ? 3 : 4;
    cells.push(`<i data-l="${l}" title="${d.toDateString()}: ${n} solved"></i>`);
  }
  return `<div class="heatmap">${cells.join('')}</div><div class="heat-legend">Less <i style="background:var(--surface-3)"></i><i style="background:color-mix(in srgb,var(--accent) 35%,var(--surface-3))"></i><i style="background:color-mix(in srgb,var(--accent) 60%,var(--surface-3))"></i><i style="background:color-mix(in srgb,var(--accent) 85%,var(--surface-3))"></i><i style="background:var(--accent-2)"></i> More</div>`;
}

// ------------------------------------------------------------------ problems list
const listState = { q: '', diff: -1, track: '', status: 'all', lang: '' };

function pageProblems() {
  document.title = 'Problems · Crucible';
  $app.innerHTML = `
  <div class="page">
    <h1 class="h-xl">Problems</h1>
    <p class="sub">${DATA.problems.length} problems. Filter by track, difficulty, status or language.</p>
    <div class="filters">
      <input class="input search" placeholder="Search titles and tags…" value="${esc(listState.q)}" data-f="q">
      <select class="input" data-f="track"><option value="">All tracks</option>${DATA.tracks.map((t) => `<option value="${t.id}" ${listState.track === t.id ? 'selected' : ''}>${esc(t.title)}</option>`).join('')}</select>
      <select class="input" data-f="lang"><option value="">Any language</option>${Object.values(LANGS).map((l) => `<option value="${l.id}" ${listState.lang === l.id ? 'selected' : ''}>${l.label}</option>`).join('')}</select>
      <div class="seg" data-seg="diff">${['All', ...DIFF].map((d, i) => `<button data-v="${i - 1}" class="${listState.diff === i - 1 ? 'on' : ''}">${d}</button>`).join('')}</div>
      <div class="seg" data-seg="status">${['all', 'todo', 'solved'].map((s) => `<button data-v="${s}" class="${listState.status === s ? 'on' : ''}">${s[0].toUpperCase() + s.slice(1)}</button>`).join('')}</div>
    </div>
    <div class="card" style="overflow:hidden"><table class="ptable"><thead><tr><th></th><th>#</th><th>Title</th><th class="hide-sm">Track</th><th>Difficulty</th><th class="hide-sm">Languages</th></tr></thead><tbody data-rows></tbody></table></div>
  </div>`;
  const rows = $app.querySelector('[data-rows]');
  const draw = () => {
    const q = listState.q.toLowerCase();
    const list = DATA.problems.filter((p) =>
      (!q || p.title.toLowerCase().includes(q) || p.tags.some((t) => t.toLowerCase().includes(q)) || String(p.num) === q) &&
      (listState.diff < 0 || p.difficulty === listState.diff) &&
      (!listState.track || p.track === listState.track) &&
      (!listState.lang || languagesFor(p).includes(listState.lang)) &&
      (listState.status === 'all' || (listState.status === 'solved') === store.isSolved(p.id)));
    rows.innerHTML = list.length ? list.map((p) => `
      <tr data-id="${p.id}">
        <td style="width:34px">${statusIcon(p.id)}</td>
        <td class="num">${p.num}</td>
        <td><span class="title">${esc(p.title)}</span></td>
        <td class="hide-sm" style="color:var(--muted);font-size:13px">${esc(trackOf(p).title)}</td>
        <td>${diffPill(p.difficulty)}</td>
        <td class="hide-sm"><div class="langs">${languagesFor(p).map((l) => `<span class="lang-dot">${LANG_SHORT[l]}</span>`).join('')}</div></td>
      </tr>`).join('') : `<tr><td colspan="6"><div class="empty">No problems match these filters.</div></td></tr>`;
  };
  rows.onclick = (e) => { const tr = e.target.closest('tr[data-id]'); if (tr) location.hash = `#/p/${tr.dataset.id}`; };
  $app.querySelectorAll('[data-f]').forEach((el) => el.addEventListener('input', () => { listState[el.dataset.f] = el.value; draw(); }));
  $app.querySelectorAll('[data-seg]').forEach((seg) => seg.addEventListener('click', (e) => {
    const b = e.target.closest('button'); if (!b) return;
    const k = seg.dataset.seg;
    listState[k] = k === 'diff' ? Number(b.dataset.v) : b.dataset.v;
    seg.querySelectorAll('button').forEach((x) => x.classList.toggle('on', x === b));
    draw();
  }));
  draw();
}

function statusIcon(id) {
  if (store.isSolved(id)) return `<span class="status-icon solved" title="Solved"><svg width="11" height="11" viewBox="0 0 12 12"><path d="M2 6.5l2.5 2.5L10 3.5" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/></svg></span>`;
  if (store.isAttempted(id)) return `<span class="status-icon tried" title="Attempted"><svg width="12" height="12" viewBox="0 0 12 12"><circle cx="6" cy="6" r="4.2" stroke="currentColor" stroke-width="1.8" fill="none" stroke-dasharray="3 2"/></svg></span>`;
  return `<span class="status-icon"></span>`;
}

// ------------------------------------------------------------------ track
function pageTrack(id) {
  const t = DATA.tracks.find((x) => x.id === id);
  if (!t) { $app.innerHTML = `<div class="page"><div class="empty">Unknown track.</div></div>`; return; }
  document.title = `${t.title} · Crucible`;
  const pr = trackProgress(t);
  const idx = DATA.tracks.indexOf(t);
  const lessonOpen = pr.solved === 0;
  $app.innerHTML = `
  <div class="page page-narrow">
    <div class="track-hero">
      <div class="track-icon">${esc(t.icon || '◆')}</div>
      <div style="flex:1"><div style="font-size:12px;color:var(--muted);font-weight:600;letter-spacing:.06em">TRACK ${idx + 1} OF ${DATA.tracks.length}</div><h1 class="h-xl" style="margin:0">${esc(t.title)}</h1><p class="sub">${esc(t.blurb)}</p></div>
      <div style="text-align:right;min-width:120px"><div style="font-size:24px;font-weight:800">${pr.pct}%</div><div class="progress" style="margin-top:6px"><span style="width:${pr.pct}%"></span></div><div style="font-size:12px;color:var(--muted);margin-top:4px">${pr.solved}/${pr.total} solved</div></div>
    </div>
    <div class="card lesson ${lessonOpen ? '' : 'collapsed'}">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px"><div style="font-weight:700">📖 Lesson</div><button class="btn sm" data-toggle>${lessonOpen ? 'Collapse' : 'Read the lesson'}</button></div>
      <div class="md" data-lesson></div>
    </div>
    <div class="card track-list">
      ${t.problems.map((pid, i) => { const p = byId.get(pid); return `
        <a class="track-row" href="#/p/${p.id}">
          <span>${statusIcon(p.id)}</span>
          <div><div class="t">${i + 1}. ${esc(p.title)}</div><div class="tags">${p.tags.slice(0, 4).map(esc).join(' · ')}</div></div>
          ${diffPill(p.difficulty)}
          <span style="color:var(--muted)">→</span>
        </a>`; }).join('')}
    </div>
    <div style="display:flex;justify-content:space-between;margin-top:22px">
      ${idx > 0 ? `<a class="btn" href="#/track/${DATA.tracks[idx - 1].id}">← ${esc(DATA.tracks[idx - 1].title)}</a>` : '<span></span>'}
      ${idx < DATA.tracks.length - 1 ? `<a class="btn" href="#/track/${DATA.tracks[idx + 1].id}">${esc(DATA.tracks[idx + 1].title)} →</a>` : ''}
    </div>
  </div>`;
  renderMd($app.querySelector('[data-lesson]'), t.intro);
  const lesson = $app.querySelector('.lesson');
  $app.querySelector('[data-toggle]').onclick = (e) => {
    lesson.classList.toggle('collapsed');
    e.target.textContent = lesson.classList.contains('collapsed') ? 'Read the lesson' : 'Collapse';
  };
}

// ------------------------------------------------------------------ workspace
async function pageProblem(id) {
  const p = byId.get(id);
  if (!p) { $app.innerHTML = `<div class="page"><div class="empty">Unknown problem.</div></div>`; return; }
  document.title = `${p.num}. ${p.title} · Crucible`;
  store.setLastProblem(p.id);
  $app.classList.add('workspace-mode');
  const langs = languagesFor(p);
  let lang = langs.includes(store.get().lastLang) ? store.get().lastLang : langs[0];
  const t = trackOf(p);
  const idx = DATA.problems.indexOf(p);
  const prev = DATA.problems[idx - 1], next = DATA.problems[idx + 1];
  let lastRun = null;
  let running = false;
  let leftTab = 'desc';

  $app.innerHTML = `
  <div class="ws">
    <section class="pane ws-left" data-left>
      <div class="tabs" data-ltabs>
        <button class="tab on" data-tab="desc">Description</button>
        <button class="tab" data-tab="hints">Hints <span class="badge">${hintsFor(p, lang).length}</span></button>
        <button class="tab" data-tab="solution">Solution</button>
        <button class="tab" data-tab="coach">✦ Coach</button>
        <button class="tab" data-tab="subs">Submissions</button>
      </div>
      <div class="tab-body" data-lbody></div>
    </section>
    <div class="gutter v" data-gv></div>
    <section class="ws-right">
      <div class="pane ws-editor">
        <div class="toolbar">
          <select class="lang-select" data-langsel>${langs.map((l) => `<option value="${l}" ${l === lang ? 'selected' : ''}>${LANGS[l].label}</option>`).join('')}</select>
          <button class="btn sm ghost" data-cheat title="Open the cheat sheet for this language">📘 Cheat sheet</button>
          <span class="saved-ind" data-saved></span>
          <span class="spacer"></span>
          <span class="cursor-pos" data-cursor title="Hover a name for docs · ⌃Space completions · ⌘⇧Space parameter hints · F12 / ⌘-click go to definition · ⌘⇧O outline · F8 next error · F1 command palette"></span>
          <button class="btn sm ghost" data-reset title="Reset to starter code">↺ Reset</button>
        </div>
        <div class="editor-host" data-editor><div class="loading"><div class="spinner"></div></div></div>
      </div>
      <div class="gutter h" data-gh></div>
      <div class="pane ws-console">
        <div class="console-bar">
          <div class="tabs" data-ctabs>
            <button class="tab on" data-ctab="cases">Testcases</button>
            <button class="tab" data-ctab="result">Result</button>
            <button class="tab" data-ctab="output">Output</button>
          </div>
          <div class="actions">
            <span class="hint-line" data-why></span>
            <button class="btn sm" data-run title="Run example tests (⌘')">▶ Run <span class="kbd-hint">⌘'</span></button>
            <button class="btn sm primary" data-submit title="Run all tests (⌘↵)">Submit <span class="kbd-hint">⌘↵</span></button>
          </div>
        </div>
        <div class="tab-body tab-pad" data-cbody></div>
      </div>
    </section>
  </div>`;

  const $l = (s) => $app.querySelector(s);
  const lbody = $l('[data-lbody]');
  const cbody = $l('[data-cbody]');

  // ---------- left tabs
  let coach = null;
  const coachHost = document.createElement('div');
  coachHost.style.height = '100%';
  const getCtx = () => ({ problem: p, lang, code: editor ? editor.getValue() : '', lastRun });

  function showLeft(tab) {
    leftTab = tab;
    $app.querySelectorAll('[data-ltabs] .tab').forEach((b) => b.classList.toggle('on', b.dataset.tab === tab));
    lbody.classList.toggle('tab-pad', tab !== 'coach');
    if (tab === 'coach') {
      lbody.innerHTML = '';
      lbody.append(coachHost);
      if (!coach) coach = mountCoach(coachHost, getCtx);
      return;
    }
    if (tab === 'desc') renderDescription();
    if (tab === 'hints') renderHints();
    if (tab === 'solution') renderSolution();
    if (tab === 'subs') renderSubs();
  }
  $l('[data-ltabs]').onclick = (e) => { const b = e.target.closest('[data-tab]'); if (b) showLeft(b.dataset.tab); };
  cleanup.push(() => coach?.destroy());

  function exampleHTML(test, i) {
    const note = p.example_notes?.[i];
    if (p.kind === 'io') {
      return `<div class="example"><h4>Example ${i + 1}</h4>
        <div class="kv"><b>Input (stdin)</b>\n${esc(test.stdin || '(empty)')}</div>
        <div class="kv" style="margin-top:8px"><b>Output</b>\n${esc(test.expected)}</div>${note ? `<div class="note md">${md(note)}</div>` : ''}</div>`;
    }
    const args = p.params.map(([n], j) => `${langName(n)} = ${formatValue(test.args[j])}`).join(', ');
    return `<div class="example"><h4>Example ${i + 1}</h4>
      <div class="kv"><b>Input: </b>${esc(args)}</div>
      <div class="kv"><b>Output: </b>${esc(formatValue(test.expected))}</div>${note ? `<div class="note md">${md(note)}</div>` : ''}</div>`;
  }
  const langName = (n) => (lang === 'cpp' || lang === 'espresso' ? camel(n) : n);

  function renderDescription() {
    const sig = signature(p, lang);
    lbody.innerHTML = `
      <div class="p-head">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:10px">
          <h1>${p.num}. ${esc(p.title)}</h1>
          <div class="p-nav">
            ${prev ? `<a class="icon-btn" href="#/p/${prev.id}" title="Previous: ${esc(prev.title)}">‹</a>` : ''}
            ${next ? `<a class="icon-btn" href="#/p/${next.id}" title="Next: ${esc(next.title)}">›</a>` : ''}
          </div>
        </div>
        <div class="row">${diffPill(p.difficulty)}<a class="pill" href="#/track/${t.id}">${esc(t.icon || '')} ${esc(t.title)}</a>${store.isSolved(p.id) ? '<span class="pill" style="color:var(--ok)">✓ Solved</span>' : ''}${p.tags.map((x) => `<span class="pill tag">${esc(x)}</span>`).join('')}</div>
      </div>
      <div class="md" data-st></div>
      ${lang === 'x86' && p.lang_notes?.x86 ? `<div class="example" style="border-color:var(--accent)"><h4>x86-64 version</h4><div class="md">${md(p.lang_notes.x86)}</div></div>` : ''}
      ${sig ? `<div class="sig">${esc(sig)}</div>` : ''}
      ${p.tests.slice(0, p.examples).map(exampleHTML).join('')}
      ${p.constraints.length ? `<h4 style="margin:20px 0 6px">Constraints</h4><ul class="md constraints">${p.constraints.map((c) => `<li>${md(c).replace(/^<p>|<\/p>\n?$/g, '')}</li>`).join('')}</ul>` : ''}
      ${p.lang_notes?.[lang] && lang !== 'x86' ? `<div class="example" style="margin-top:18px"><h4>${LANGS[lang].label} notes</h4><div class="md">${md(p.lang_notes[lang])}</div></div>` : ''}
      <div data-intro></div>
      <div style="margin-top:22px;font-size:12.5px;color:var(--muted)">Available in: ${langs.map((l) => LANGS[l].label).join(' · ')}</div>`;
    renderMd(lbody.querySelector('[data-st]'), p.statement);
    enhance(lbody);
    const intro = lbody.querySelector('[data-intro]');
    const forLang = lang;
    introducedEntries(DATA.problems, p, lang, (q, l) => (languagesFor(q).includes(l) ? `${starterCode(q, l)}\n${q.lang_notes?.[l] || ''}` : '')).then((es) => {
      if (!es.length || forLang !== lang || !intro.isConnected) return;
      intro.innerHTML = `<div class="example intro" style="margin-top:18px"><h4>New in this problem · ${LANGS[lang].label}</h4>${es.map((e) => `<div class="md intro-card">${md(entryCard(lang, e))}</div>`).join('')}</div>`;
      enhance(intro);
    }).catch(() => {});
  }

  function renderHints() {
    const opened = store.hintsOpened(p.id);
    lbody.innerHTML = `<p class="sub" style="margin-bottom:12px">Hints get progressively more specific. Open one at a time and give it a real try in between.</p>` +
      hintsFor(p, lang).map((x, i) => `<details class="hint" ${i < opened ? 'open' : ''} data-h="${i}"><summary>Hint ${i + 1}</summary><div class="md">${md(x)}</div></details>`).join('');
    lbody.querySelectorAll('details').forEach((d) => d.addEventListener('toggle', () => { if (d.open) store.openHint(p.id, Number(d.dataset.h) + 1); }));
    enhance(lbody);
  }

  function renderSolution() {
    if (!store.isRevealed(p.id)) {
      lbody.innerHTML = `<div class="gate"><div class="big">🔒</div><h3>Solve it first?</h3><p>The full explanation and reference solutions unlock when you pass all tests. Struggle is where the learning happens; try the hints or ask the Coach first.</p><button class="btn" data-reveal>Reveal anyway</button></div>`;
      lbody.querySelector('[data-reveal]').onclick = () => { store.reveal(p.id); renderSolution(); };
      return;
    }
    const sols = [['python', p.kind === 'asm' ? null : p.solution], ...Object.entries(p.refs || {})].filter(([, c]) => c);
    if (p.kind === 'asm') sols.unshift(['asm', p.asm_solution], ...(p.x86_solution ? [['x86', p.x86_solution]] : []));
    let cur = sols.find(([l]) => l === lang)?.[0] || sols[0][0];
    lbody.innerHTML = `<div class="md" data-ex></div><h2 style="font-size:18px;margin:28px 0 8px">Reference solution</h2><div class="sol-langs" data-sl></div><div class="md" data-code></div>`;
    renderMd(lbody.querySelector('[data-ex]'), lang === 'x86' && p.x86_explanation ? p.x86_explanation : p.explanation);
    const drawSol = () => {
      lbody.querySelector('[data-sl]').innerHTML = sols.map(([l]) => `<button class="chip ${l === cur ? '' : ''}" style="${l === cur ? 'border-color:var(--accent);color:var(--text)' : ''}" data-l="${l}">${LANGS[l].label}</button>`).join('');
      const code = sols.find(([l]) => l === cur)[1];
      renderMd(lbody.querySelector('[data-code]'), '```' + ({ asm: 'asm', x86: 'x86', espresso: 'javascript' }[cur] || cur) + '\n' + code + '\n```');
    };
    lbody.querySelector('[data-sl]').onclick = (e) => { const b = e.target.closest('[data-l]'); if (b) { cur = b.dataset.l; drawSol(); } };
    drawSol();
  }

  function renderSubs() {
    const subs = store.submissions(p.id);
    lbody.innerHTML = subs.length ? `<table class="ptable"><thead><tr><th>Status</th><th>Language</th><th>Tests</th><th>When</th></tr></thead><tbody>${subs.map((s, i) => `
      <tr data-i="${i}"><td style="font-weight:700;color:${s.status === 'accepted' ? 'var(--ok)' : 'var(--bad)'}">${s.status === 'accepted' ? 'Accepted' : s.status === 'compile' ? 'Compile Error' : 'Wrong Answer'}</td><td>${LANGS[s.lang]?.label}</td><td>${s.passed}/${s.total}</td><td style="color:var(--muted)">${fmtDate(s.at)}</td></tr>`).join('')}</tbody></table><p class="hint-line" style="margin-top:10px">Click a submission to load its code into the editor.</p>`
      : `<div class="empty">No submissions yet. Press <kbd>⌘</kbd> <kbd>↵</kbd> to submit.</div>`;
    lbody.querySelectorAll('tr[data-i]').forEach((tr) => tr.onclick = () => {
      const s = subs[Number(tr.dataset.i)];
      if (s.code && confirmReplace()) { if (s.lang !== lang) switchLang(s.lang, s.code); else editor.setValue(s.code); }
    });
  }
  const confirmReplace = () => true;

  // ---------- editor
  let editor = null, monaco = null;
  const host = $l('[data-editor]');
  const initial = store.draft(p.id, lang) ?? starterCode(p, lang);
  let savedTimer = null;
  const savedInd = $l('[data-saved]');
  setIdeContext(p, lang);
  createEditor(host, {
    value: initial,
    language: LANGS[lang].monaco,
    settings: store.settings(),
    onChange: (v) => {
      store.saveDraft(p.id, lang, v);
      savedInd.textContent = 'Saved';
      clearTimeout(savedTimer);
      savedTimer = setTimeout(() => (savedInd.textContent = ''), 1200);
    },
    onRun: () => run(false),
    onSubmit: () => run(true),
  }).then((r) => {
    host.querySelector('.loading')?.remove();
    editor = r.editor; monaco = r.monaco;
    const diagSub = trackDiagnosticEdits(monaco, editor);
    const curEl = $l('[data-cursor]');
    const showCursor = () => {
      const pos = editor.getPosition();
      const n = monaco.editor.getModelMarkers({ owner: 'crucible', resource: editor.getModel().uri }).length;
      if (curEl) curEl.innerHTML = `${n ? `<span class="diag-count">● ${n} problem${n > 1 ? 's' : ''}</span> · ` : ''}Ln ${pos.lineNumber}, Col ${pos.column}`;
    };
    editor.onDidChangeCursorPosition(showCursor);
    const markSub = monaco.editor.onDidChangeMarkers(showCursor);
    cleanup.push(() => markSub.dispose());
    showCursor();
    cleanup.push(() => { diagSub.dispose(); clearDiagnostics(monaco, editor); editor.dispose(); });
  }).catch(() => { host.innerHTML = `<div class="empty">Couldn't load the code editor. Check your internet connection (Monaco loads from a CDN).</div>`; });

  function switchLang(l, code) {
    lang = l;
    store.setLastLang(l);
    $l('[data-langsel]').value = l;
    const val = code ?? store.draft(p.id, l) ?? starterCode(p, l);
    setIdeContext(p, l);
    if (editor) {
      clearDiagnostics(monaco, editor);
      const model = editor.getModel();
      monaco.editor.setModelLanguage(model, LANGS[l].monaco);
      editor.setValue(val);
    }
    updateRunState();
    if (leftTab === 'desc') renderDescription();
    renderCases();
  }
  $l('[data-langsel]').onchange = (e) => switchLang(e.target.value);
  $l('[data-reset]').onclick = () => {
    modal(`<h2>Reset code?</h2><p class="sub">This replaces your ${LANGS[lang].label} code with the starter template. Your submissions history keeps earlier versions.</p><div class="actions"><button class="btn" data-close>Cancel</button><button class="btn primary" data-ok>Reset</button></div>`, {
      onMount: (el, close) => { el.querySelector('[data-ok]').onclick = () => { store.clearDraft(p.id, lang); editor?.setValue(starterCode(p, lang)); close(); }; },
    });
  };
  $l('[data-cheat]').onclick = () => openCheatDrawer(lang);

  // ---------- splitters
  splitter($l('[data-gv]'), $l('[data-left]'), 'x');
  splitter($l('[data-gh]'), $app.querySelector('.ws-editor'), 'y');

  // ---------- console
  let ctab = 'cases';
  let caseSel = 0;
  function showConsole(tab) {
    ctab = tab;
    $app.querySelectorAll('[data-ctabs] .tab').forEach((b) => b.classList.toggle('on', b.dataset.ctab === tab));
    if (tab === 'cases') renderCases();
    if (tab === 'result') renderResult();
    if (tab === 'output') renderOutput();
  }
  $l('[data-ctabs]').onclick = (e) => { const b = e.target.closest('[data-ctab]'); if (b) showConsole(b.dataset.ctab); };

  const inputText = (test) => p.kind === 'io' ? (test.stdin || '(empty)') : p.params.map(([n], j) => `${langName(n)} = ${formatValue(test.args[j])}`).join('\n');

  function renderCases() {
    if (ctab !== 'cases') return;
    const ex = p.tests.slice(0, p.examples);
    caseSel = Math.min(caseSel, ex.length - 1);
    cbody.innerHTML = `<div class="case-tabs">${ex.map((_, i) => `<button class="case-tab ${i === caseSel ? 'on' : ''}" data-c="${i}">Case ${i + 1}</button>`).join('')}</div>
      <div class="field"><label>${p.kind === 'io' ? 'stdin' : 'Input'}</label><div class="box">${esc(inputText(ex[caseSel]))}</div></div>
      <div class="field"><label>Expected ${p.kind === 'io' ? 'stdout' : 'output'}</label><div class="box">${esc(p.kind === 'io' ? ex[caseSel].expected : formatValue(ex[caseSel].expected))}</div></div>
      <p class="hint-line">Run checks these ${ex.length} examples. Submit runs all ${p.tests.length} tests, including hidden edge cases.</p>`;
    cbody.querySelectorAll('[data-c]').forEach((b) => (b.onclick = () => { caseSel = Number(b.dataset.c); renderCases(); }));
  }

  function renderResult() {
    if (ctab !== 'result') return;
    if (running) { cbody.innerHTML = `<div class="running"><div class="spinner"></div><span data-rs>${esc(running)}</span></div>`; return; }
    if (!lastRun) { cbody.innerHTML = `<div class="empty">Run your code to see results here.</div>`; return; }
    if (lastRun.error) { cbody.innerHTML = `<div class="verdict fail"><h3>Couldn't run</h3></div><pre class="term err">${esc(lastRun.error)}</pre>`; return; }
    if (lastRun.compileError) {
      cbody.innerHTML = `<div class="verdict fail"><h3>Compile Error</h3><button class="btn sm" data-ask style="margin-left:auto">✦ Ask Coach</button></div><pre class="term err">${esc(lastRun.compileError)}</pre>`;
      cbody.querySelector('[data-ask]').onclick = askCoach;
      return;
    }
    const res = lastRun.results;
    const passed = res.filter((r) => r.status === 'pass').length;
    const allPass = passed === res.length;
    const firstBad = res.findIndex((r) => r.status !== 'pass');
    let sel = Math.min(lastRun.sel ?? (firstBad >= 0 ? firstBad : 0), res.length - 1);
    const label = allPass ? (lastRun.submit ? 'Accepted' : 'All examples pass') : res.some((r) => r.status === 'timeout') ? 'Time Limit Exceeded' : res.some((r) => r.status === 'error') ? 'Runtime Error' : 'Wrong Answer';
    const ms = res.reduce((a, r) => Math.max(a, r.timeMs || 0), 0);
    const showCases = lastRun.submit && !allPass ? res.filter((r) => r.status !== 'pass').slice(0, 1).concat(res.slice(0, p.examples)) : res;
    const visible = lastRun.submit ? [...new Map(showCases.map((r) => [r.index, r])).values()].sort((a, b) => a.index - b.index) : res;
    if (!visible.some((r) => r.index === sel)) sel = visible[0]?.index ?? 0;
    const r = res[sel];
    cbody.innerHTML = `
      <div class="verdict ${allPass ? 'pass' : 'fail'}"><h3>${label}</h3><span class="meta">${passed} / ${res.length} tests passed${ms ? ` · ${ms} ms` : ''}</span>
        ${!allPass ? '<button class="btn sm" data-ask style="margin-left:auto">✦ Ask Coach why</button>' : lastRun.submit && next ? `<a class="btn sm primary" style="margin-left:auto" href="#/p/${next.id}">Next problem →</a>` : ''}</div>
      ${lastRun.submit && !allPass ? `<p class="hint-line" style="margin:-6px 0 12px">Showing the first failing test${r.index >= p.examples ? ' (a hidden test)' : ''} and the examples.</p>` : ''}
      <div class="case-tabs">${visible.map((x) => `<button class="case-tab ${x.status} ${x.index === sel ? 'on' : ''}" data-c="${x.index}"><span class="d"></span>${x.index < p.examples ? `Case ${x.index + 1}` : `Test ${x.index + 1}`}</button>`).join('')}</div>
      <div class="field"><label>${p.kind === 'io' ? 'stdin' : 'Input'}</label><div class="box">${esc(inputText(p.tests[r.index]))}</div></div>
      ${r.error ? `<div class="field"><label>Error</label><pre class="term err" style="margin:0">${esc(String(r.error))}</pre></div>` : ''}
      ${r.got !== undefined ? `<div class="field"><label>Your output</label><div class="box ${r.status === 'pass' ? 'good' : 'bad'}">${esc(p.kind === 'io' ? r.got : formatValue(r.got))}</div></div>` : ''}
      <div class="field"><label>Expected</label><div class="box">${esc(p.kind === 'io' ? r.expected : formatValue(r.expected))}</div></div>
      ${r.stdout ? `<div class="field"><label>Your prints (stdout)</label><div class="box">${esc(r.stdout)}</div></div>` : ''}
      ${(r.stderr || (r.status !== 'pass' && lastRun.stderr)) ? `<div class="field"><label>stderr</label><pre class="term err" style="margin:0;max-height:240px;overflow:auto">${esc(r.stderr || lastRun.stderr)}</pre></div>` : ''}`;
    cbody.querySelectorAll('[data-c]').forEach((b) => (b.onclick = () => { lastRun.sel = Number(b.dataset.c); renderResult(); }));
    cbody.querySelector('[data-ask]')?.addEventListener('click', askCoach);
  }

  function renderOutput() {
    if (ctab !== 'output') return;
    if (!lastRun) { cbody.innerHTML = `<div class="empty">Compiler messages, prints and stderr appear here.</div>`; return; }
    const parts = [];
    if (lastRun.compileOutput) parts.push(`<div class="field"><label>Compiler</label><pre class="term ${lastRun.compileError ? 'err' : ''}">${esc(lastRun.compileOutput)}</pre></div>`);
    const prints = (lastRun.results || []).filter((r) => r.stdout).map((r) => `── test ${r.index + 1} ──\n${r.stdout}`).join('\n');
    if (prints) parts.push(`<div class="field"><label>Your prints (stdout)</label><pre class="term">${esc(prints)}</pre></div>`);
    if (lastRun.stderr) parts.push(`<div class="field"><label>stderr</label><pre class="term err">${esc(lastRun.stderr)}</pre></div>`);
    cbody.innerHTML = parts.join('') || `<div class="empty">No output. Use print / printf / println! to debug; your prints show up here.</div>`;
  }

  function askCoach() {
    showLeft('coach');
    coach.askDebug();
  }

  function updateRunState() {
    const why = unavailableReason(lang);
    $l('[data-run]').disabled = !!why || !!running;
    $l('[data-submit]').disabled = !!why || !!running;
    $l('[data-why]').textContent = why ? why : '';
    $l('[data-why]').title = why || '';
  }
  cleanup.push(onCompanion(updateRunState));

  async function run(submit) {
    if (running || !editor) return;
    const why = unavailableReason(lang);
    if (why) { toast(why); return; }
    const code = editor.getValue();
    const tests = submit ? p.tests : p.tests.slice(0, p.examples);
    running = 'Preparing…';
    clearDiagnostics(monaco, editor);
    updateRunState();
    showConsole('result');
    const setStatus = (s) => { running = s; const n = cbody.querySelector('[data-rs]'); if (n) n.textContent = s; };
    let out;
    try {
      const req = buildRun(p, lang, code, tests);
      const raw = await execute(req, setStatus);
      const parsed = parseRun(p, lang, tests, raw);
      out = { ...parsed, submit, compileOutput: raw.compile?.output || '' };
      out.results?.forEach((r) => { r.inputText = inputText(p.tests[r.index]); });
    } catch (e) {
      out = { error: e.message, submit, results: [] };
    }
    running = false;
    lastRun = out;
    {
      const text = [out.compileOutput, out.compileError, out.stderr, out.error, ...(out.results || []).map((r) => r.error)].filter(Boolean).join('\n');
      const diags = parseDiagnostics(lang, text, code.split('\n').length, p.kind === 'io');
      if (diags.length) showDiagnostics(monaco, editor, diags);
    }
    updateRunState();
    renderResult();
    const tabs = $app.querySelector('[data-ctabs] [data-ctab="result"]');
    tabs.innerHTML = `Result ${out.results?.length ? `<span class="badge ${out.results.every((r) => r.status === 'pass') ? 'ok' : 'bad'}">${out.results.filter((r) => r.status === 'pass').length}/${out.results.length}</span>` : out.compileError || out.error ? '<span class="badge bad">!</span>' : ''}`;
    if (submit && !out.error) {
      const passed = out.results.filter((r) => r.status === 'pass').length;
      const accepted = !out.compileError && passed === tests.length;
      const first = store.recordSubmission(p.id, { at: Date.now(), lang, status: accepted ? 'accepted' : out.compileError ? 'compile' : 'wrong', passed, total: tests.length, code });
      if (accepted) {
        celebrate(first);
        if (leftTab === 'subs') renderSubs();
        if (leftTab === 'desc') renderDescription();
        if (first) toast('Solved! The explanation is now unlocked in the Solution tab.', 3500);
      } else if (leftTab === 'subs') renderSubs();
    }
  }
  $l('[data-run]').onclick = () => run(false);
  $l('[data-submit]').onclick = () => run(true);

  const keyHandler = (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') { e.preventDefault(); run(true); }
    else if ((e.metaKey || e.ctrlKey) && e.key === "'") { e.preventDefault(); run(false); }
  };
  document.addEventListener('keydown', keyHandler);
  cleanup.push(() => document.removeEventListener('keydown', keyHandler));

  showLeft('desc');
  showConsole('cases');
  updateRunState();
  if (lang === 'python' && companionInfo().status !== 'connected') warmPython().catch(() => {});
}

function splitter(gutter, target, axis) {
  const key = `crucible.split.${axis}`;
  const saved = Number(localStorage.getItem(key));
  if (saved) target.style.flex = `0 0 ${saved}px`;
  gutter.addEventListener('pointerdown', (e) => {
    e.preventDefault();
    gutter.setPointerCapture(e.pointerId);
    gutter.classList.add('drag');
    document.body.classList.add('resizing');
    const start = axis === 'x' ? e.clientX : e.clientY;
    const rect = target.getBoundingClientRect();
    const base = axis === 'x' ? rect.width : rect.height;
    const parent = target.parentElement.getBoundingClientRect();
    const max = (axis === 'x' ? parent.width : parent.height) - 180;
    const move = (ev) => {
      const d = (axis === 'x' ? ev.clientX : ev.clientY) - start;
      const size = Math.max(160, Math.min(max, base + d));
      target.style.flex = `0 0 ${size}px`;
    };
    const up = () => {
      gutter.classList.remove('drag');
      document.body.classList.remove('resizing');
      gutter.removeEventListener('pointermove', move);
      const r = target.getBoundingClientRect();
      try { localStorage.setItem(key, String(Math.round(axis === 'x' ? r.width : r.height))); } catch {}
    };
    gutter.addEventListener('pointermove', move);
    gutter.addEventListener('pointerup', up, { once: true });
  });
}

function celebrate(big) {
  const c = document.createElement('canvas');
  c.className = 'confetti';
  c.width = innerWidth * devicePixelRatio; c.height = innerHeight * devicePixelRatio;
  document.body.append(c);
  const ctx = c.getContext('2d');
  ctx.scale(devicePixelRatio, devicePixelRatio);
  const colors = ['#ffb347', '#ff5e3a', '#4ade80', '#a78bfa', '#2dd4bf', '#fbbf24'];
  const n = big ? 160 : 70;
  const parts = Array.from({ length: n }, () => ({
    x: innerWidth * (0.55 + Math.random() * 0.3), y: innerHeight * 0.75,
    vx: (Math.random() - 0.5) * 9, vy: -(Math.random() * 11 + 6), r: Math.random() * 6 + 3,
    c: colors[(Math.random() * colors.length) | 0], a: Math.random() * Math.PI, va: (Math.random() - 0.5) * 0.3,
  }));
  let frame = 0;
  const tick = () => {
    ctx.clearRect(0, 0, innerWidth, innerHeight);
    for (const q of parts) {
      q.vy += 0.32; q.vx *= 0.99; q.x += q.vx; q.y += q.vy; q.a += q.va;
      ctx.save(); ctx.translate(q.x, q.y); ctx.rotate(q.a); ctx.fillStyle = q.c;
      ctx.globalAlpha = Math.max(0, 1 - frame / 110);
      ctx.fillRect(-q.r / 2, -q.r / 4, q.r, q.r / 2); ctx.restore();
    }
    if (++frame < 110) requestAnimationFrame(tick); else c.remove();
  };
  if (!matchMedia('(prefers-reduced-motion: reduce)').matches) tick(); else c.remove();
}

// ------------------------------------------------------------------ cheat sheets
const CS_ORDER = ['python', 'c', 'cpp', 'rust', 'espresso', 'asm', 'x86'];
const csCache = new Map();
async function loadCheat(lang) {
  if (!csCache.has(lang)) {
    csCache.set(lang, fetch(`data/cheatsheets/${lang}.md`).then((r) => (r.ok ? r.text() : `# ${LANGS[lang].label}\n\nCheat sheet coming soon.`)));
  }
  return csCache.get(lang);
}

async function pageCheatsheets(lang) {
  lang = CS_ORDER.includes(lang) ? lang : (CS_ORDER.includes(store.get().lastLang) ? store.get().lastLang : 'python');
  document.title = `${LANGS[lang].label} cheat sheet · Crucible`;
  $app.innerHTML = `
    <div class="page">
      <div class="cs-layout">
        <nav class="cs-nav">
          <div style="font-size:12px;color:var(--muted);font-weight:700;letter-spacing:.06em;padding:0 12px 6px">CHEAT SHEETS</div>
          ${CS_ORDER.map((l) => `<a href="#/cheatsheets/${l}" class="${l === lang ? 'on' : ''}"><span class="lang-dot">${LANG_SHORT[l]}</span>${LANGS[l].label}</a>`).join('')}
          <div class="cs-toc" data-toc></div>
        </nav>
        <article class="card cs-body"><div class="md" data-md><div class="spinner"></div></div></article>
      </div>
    </div>`;
  const text = await loadCheat(lang);
  const el = $app.querySelector('[data-md]');
  if (!el) return;
  renderMd(el, text);
  const toc = $app.querySelector('[data-toc]');
  el.querySelectorAll('h2').forEach((hd, i) => {
    hd.id = `cs-${i}`;
    const a = document.createElement('a');
    a.textContent = hd.textContent;
    a.href = 'javascript:void 0';
    a.onclick = () => hd.scrollIntoView({ behavior: 'smooth', block: 'start' });
    toc.append(a);
  });
}

async function openCheatDrawer(lang) {
  const root = document.getElementById('modal-root');
  const back = h(`<div class="drawer-backdrop"></div>`);
  const dr = h(`<aside class="drawer"><div class="drawer-head"><span class="lang-dot">${LANG_SHORT[lang]}</span><h3>${LANGS[lang].label} cheat sheet</h3><a class="btn sm ghost" style="margin-left:auto" href="#/cheatsheets/${lang}" target="_blank">Open full page ↗</a><button class="icon-btn" data-x>✕</button></div><div class="drawer-body"><div class="md" data-md><div class="spinner"></div></div></div></aside>`);
  const close = () => { back.remove(); dr.remove(); document.removeEventListener('keydown', esc_); };
  const esc_ = (e) => { if (e.key === 'Escape') close(); };
  back.onclick = close;
  dr.querySelector('[data-x]').onclick = close;
  document.addEventListener('keydown', esc_);
  root.append(back, dr);
  renderMd(dr.querySelector('[data-md]'), await loadCheat(lang));
}

// ------------------------------------------------------------------ settings
function pageSettings() {
  document.title = 'Settings · Crucible';
  const s = store.settings();
  const c = companionInfo();
  $app.innerHTML = `
  <div class="page page-narrow">
    <h1 class="h-xl">Settings</h1>
    <p class="sub" style="margin-bottom:22px">Everything is stored locally in this browser.</p>

    <div class="card settings-group">
      <div class="setting"><div class="l"><b>Theme</b><span>Match your system, or pick one.</span></div>
        <div class="r"><div class="seg" data-s="theme">${['system', 'dark', 'light'].map((t) => `<button data-v="${t}" class="${s.theme === t ? 'on' : ''}">${t[0].toUpperCase() + t.slice(1)}</button>`).join('')}</div></div></div>
      <div class="setting"><div class="l"><b>Editor font size</b><span>Applies to newly opened problems.</span></div>
        <div class="r"><input class="input" type="number" min="10" max="24" value="${s.fontSize}" style="width:80px" data-i="fontSize"></div></div>
      <div class="setting"><div class="l"><b>Minimap</b><span>Code overview on the right edge of the editor.</span></div>
        <div class="r"><div class="seg" data-s="minimap">${[['Off', false], ['On', true]].map(([l, v]) => `<button data-v="${v}" class="${s.minimap === v ? 'on' : ''}">${l}</button>`).join('')}</div></div></div>
    </div>

    <div class="card settings-group">
      <div class="setting"><div class="l"><b>Local companion</b><span>${c.status === 'connected' ? `Connected${c.base ? ` at ${esc(c.base)}` : ' (serving this page)'} · v${esc(c.health.version)}` : 'Not connected. Run <code>./crucible</code> in the project folder.'}</span></div>
        <div class="r"><button class="btn sm" data-recheck>Re-check</button></div></div>
      <div class="setting"><div class="l"><b>Companion URL</b><span>Used when this page is hosted elsewhere (GitHub Pages / Vercel).</span></div>
        <div class="r"><input class="input" value="${esc(s.companionUrl)}" style="width:230px" data-i="companionUrl"></div></div>
      <div class="setting"><div class="l"><b>Python runtime</b><span>Auto uses your Mac's Python when the companion is running, otherwise Pyodide in the browser.</span></div>
        <div class="r"><div class="seg" data-s="pythonRuntime">${['auto', 'browser', 'local'].map((t) => `<button data-v="${t}" class="${s.pythonRuntime === t ? 'on' : ''}">${t[0].toUpperCase() + t.slice(1)}</button>`).join('')}</div></div></div>
      <div class="setting"><div class="l"><b>Coach may show full code</b><span>Off: the Coach explains and nudges but won't write your solution.</span></div>
        <div class="r"><div class="seg" data-s="coachSpoilers">${[['Off', false], ['On', true]].map(([l, v]) => `<button data-v="${v}" class="${s.coachSpoilers === v ? 'on' : ''}">${l}</button>`).join('')}</div></div></div>
      ${c.status === 'connected' ? `<div class="lang-status">${Object.entries(c.health.langs).map(([l, v]) => `<div><span class="${v ? 'ok' : 'no'}">${v ? '●' : '○'}</span>${LANGS[l]?.label || l}</div>`).join('')}<div><span class="${c.health.ai?.available ? 'ok' : 'no'}">${c.health.ai?.available ? '●' : '○'}</span>Apple Intelligence</div></div>` : ''}
    </div>

    <div class="card settings-group">
      <div class="setting"><div class="l"><b>Back up progress</b><span>Download solved problems, drafts and history as JSON.</span></div>
        <div class="r"><button class="btn sm" data-export>Export</button><label class="btn sm">Import<input type="file" accept="application/json" hidden data-import></label></div></div>
      <div class="setting"><div class="l"><b style="color:var(--bad)">Reset everything</b><span>Erase all progress and drafts in this browser.</span></div>
        <div class="r"><button class="btn sm" data-reset>Reset…</button></div></div>
    </div>
  </div>`;
  $app.querySelectorAll('[data-s]').forEach((seg) => seg.addEventListener('click', (e) => {
    const b = e.target.closest('button'); if (!b) return;
    const k = seg.dataset.s;
    let v = b.dataset.v; if (v === 'true') v = true; if (v === 'false') v = false;
    store.setSetting(k, v);
    seg.querySelectorAll('button').forEach((x) => x.classList.toggle('on', x === b));
    if (k === 'theme') applyTheme();
  }));
  $app.querySelectorAll('[data-i]').forEach((inp) => inp.addEventListener('change', () => {
    store.setSetting(inp.dataset.i, inp.type === 'number' ? Number(inp.value) : inp.value.trim());
    if (inp.dataset.i === 'companionUrl') detectCompanion().then(() => pageSettings());
  }));
  $app.querySelector('[data-recheck]').onclick = async () => { await detectCompanion(); pageSettings(); toast(companionInfo().status === 'connected' ? 'Companion connected' : 'Companion not found'); };
  $app.querySelector('[data-export]').onclick = () => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([store.exportJSON()], { type: 'application/json' }));
    a.download = `crucible-progress-${dayKey(new Date())}.json`;
    a.click();
  };
  $app.querySelector('[data-import]').onchange = async (e) => {
    try { store.importJSON(await e.target.files[0].text()); toast('Progress imported'); pageSettings(); } catch (err) { toast(`Import failed: ${err.message}`); }
  };
  $app.querySelector('[data-reset]').onclick = () => modal(`<h2>Reset all progress?</h2><p class="sub">This permanently erases solved problems, drafts, and history in this browser. Consider exporting a backup first.</p><div class="actions"><button class="btn" data-close>Cancel</button><button class="btn primary" data-ok>Erase everything</button></div>`, {
    onMount: (el, close) => { el.querySelector('[data-ok]').onclick = () => { store.reset(); close(); toast('Progress reset'); location.hash = '#/'; }; },
  });
}

// ------------------------------------------------------------------ companion pill
function companionPill() {
  const pill = document.getElementById('companion-pill');
  onCompanion((c) => {
    pill.classList.remove('ok', 'partial');
    if (c.status === 'unknown') { pill.querySelector('.label').textContent = 'Checking…'; return; }
    if (c.status === 'connected') {
      const ai = c.health?.ai?.available;
      pill.classList.add(ai ? 'ok' : 'partial');
      pill.querySelector('.label').textContent = ai ? 'Local · All languages + Coach' : 'Local · Coach unavailable';
    } else pill.querySelector('.label').textContent = 'Browser · Python only';
  });
  pill.onclick = () => {
    const c = companionInfo();
    modal(`<h2>${c.status === 'connected' ? 'Local companion connected' : 'Unlock every language and the Coach'}</h2>
      ${c.status === 'connected'
        ? `<p class="sub">Crucible is talking to the companion running on your Mac${c.mode === 'bridge' ? ' through the bridge window (keep it open)' : ''}.</p><div class="lang-status">${Object.entries(c.health.langs).map(([l, v]) => `<div title="${esc(v || 'not found')}"><span class="${v ? 'ok' : 'no'}">${v ? '●' : '○'}</span>${LANGS[l]?.label || l}</div>`).join('')}<div title="${esc(c.health.ai?.reason || '')}"><span class="${c.health.ai?.available ? 'ok' : 'no'}">${c.health.ai?.available ? '●' : '○'}</span>Coach (Apple Intelligence)</div></div>${c.health.ai?.available ? '' : `<p class="sub">${esc(c.health.ai?.reason || '')}</p>`}`
        : `<div class="md"><p>Right now Crucible runs <strong>Python</strong> in your browser. C, C++, Rust, ESPresso and ARM64 assembly need real compilers, and the Coach runs on Apple Intelligence, so those live in a tiny local companion.</p><p>From the Crucible folder, run:</p><pre><code data-lang="bash">./crucible</code></pre>${bridgeNeeded()
          ? `<p>Then click <strong>Connect</strong>. Crucible opens a small bridge window from the companion (Safari won't let a web page talk to <code>localhost</code> directly); keep it open while you practise. Chrome may instead ask to allow access to devices on your local network: allow it and press Re-check.</p><p class="sub">Started the companion some other way? It must allow this site: <code>CRUCIBLE_ORIGINS=${esc(location.origin)} ./crucible</code></p>`
          : `<p>Then open <a href="http://localhost:4747">http://localhost:4747</a>.</p>`}</div>`}
      <div class="actions"><button class="btn" data-recheck>Re-check</button>${c.status !== 'connected' && bridgeNeeded() ? '<button class="btn primary" data-connect>Connect</button>' : '<button class="btn primary" data-close>Done</button>'}</div>`, {
      onMount: (el, close) => {
        el.querySelector('[data-recheck]').onclick = async () => { close(); await detectCompanion(); pill.click(); };
        const cb = el.querySelector('[data-connect]');
        if (cb) cb.onclick = async () => {
          cb.disabled = true; cb.textContent = 'Connecting…';
          const ok = await connectBridge();
          close();
          if (ok) toast('Companion connected'); else toast("Couldn't reach the companion. Is ./crucible running?");
          pill.click();
        };
        enhance(el);
      },
    });
  };
}

// ------------------------------------------------------------------ boot
async function boot() {
  companionPill();
  detectCompanion();
  try {
    const r = await fetch('data/problems.json', { cache: 'no-cache' });
    DATA = await r.json();
  } catch (e) {
    $app.innerHTML = `<div class="page"><div class="empty">Couldn't load problems: ${esc(e.message)}</div></div>`;
    return;
  }
  byId = new Map(DATA.problems.map((p) => [p.id, p]));
  window.addEventListener('hashchange', route);
  store.onChange((what) => { if (what === 'settings') applyTheme(); });
  setInterval(() => { if (companionInfo().status !== 'connected') detectCompanion(); }, 15000);
  route();
  // Warm Monaco in the background so the first problem opens instantly.
  setTimeout(() => loadMonaco().catch(() => {}), 800);
}
boot();
