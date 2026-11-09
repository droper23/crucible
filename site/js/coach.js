// The Coach: an on-device Apple Intelligence tutor that sees the problem, the
// learner's code and their latest test results.
import { aiStatus, streamAI, onCompanion } from './runner.js';
import { md, enhance, esc } from './md.js';
import { store } from './store.js';
import { LANGS, signature, formatValue } from './harness.js';

// The on-device model has an ~8K-token window shared by prompt and answer, so
// every section is trimmed to a budget.
const BUDGET = { statement: 1600, code: 5200, run: 1400, history: 1200 };

const trim = (s, n) => (s.length > n ? s.slice(0, n) + '\n…[trimmed]' : s);
const numbered = (code) => code.split('\n').map((l, i) => `${String(i + 1).padStart(3)}| ${l}`).join('\n');

const ACTIONS = [
  { id: 'debug', label: 'Why is it failing?', needsRun: true },
  { id: 'review', label: 'Review my code' },
  { id: 'explain', label: 'Explain how it works' },
  { id: 'complexity', label: 'Time & space complexity' },
  { id: 'hint', label: 'Nudge me (no spoilers)' },
];

const TASKS = {
  debug: 'My code is not passing. Using the latest run results, find the most likely cause. Point to the exact line(s), explain WHY it produces the wrong result (trace the failing input if it helps), and describe the fix.',
  review: 'Review my code like a senior engineer: correctness (including edge cases from the constraints), complexity, readability, and idiomatic use of the language. Use a short bulleted list, most important first.',
  explain: 'Explain how my code works, step by step, as if teaching it back to me. Walk through it on the first example input. Mention why each key part is needed.',
  complexity: 'Analyze the time and space complexity of my code in Big-O, explain where the cost comes from (which loops/calls), and say whether a better complexity is possible for this problem (without giving the full solution).',
  hint: 'Give me ONE small hint that moves me forward from where my code is now. Do not reveal the full approach or write the solution.',
};

function instructions(lang) {
  const spoil = store.settings().coachSpoilers;
  return [
    'You are Crucible Coach, a patient, precise programming tutor.',
    `The learner is solving a coding practice problem in ${LANGS[lang]?.label || lang}.`,
    'Reference code by line number like "line 7". Use Markdown with short paragraphs or bullets. Keep answers under 250 words unless asked for more.',
    'Wrap code in fenced blocks with a language tag.',
    spoil
      ? 'You may show corrected code when it helps.'
      : 'Never write a complete solution. Show at most 3 lines of code to illustrate a fix.',
    'If you are not sure about something, say so plainly instead of guessing.',
  ].join(' ');
}

function runSummary(run) {
  if (!run) return 'Not run yet.';
  if (run.error) return `Runner error: ${run.error}`;
  if (run.compileError) return `COMPILE ERROR:\n${trim(run.compileError, BUDGET.run)}`;
  const res = run.results || [];
  const passed = res.filter((r) => r.status === 'pass').length;
  let s = `${passed}/${res.length} tests passed.`;
  const f = res.find((r) => r.status !== 'pass');
  if (f) {
    s += `\nFIRST FAILING TEST:\n  input: ${trim(f.inputText || '', 400)}\n  expected: ${trim(formatValue(f.expected), 300)}`;
    if (f.got !== undefined) s += `\n  got: ${trim(formatValue(f.got), 300)}`;
    if (f.error) s += `\n  error: ${trim(String(f.error), 500)}`;
    if (f.stdout) s += `\n  printed: ${trim(f.stdout, 200)}`;
  }
  if (run.stderr) s += `\nSTDERR:\n${trim(run.stderr, 500)}`;
  return trim(s, BUDGET.run);
}

function buildPrompt(ctx, task, history) {
  const { problem, lang, code, lastRun } = ctx;
  const sig = signature(problem, lang);
  const parts = [
    `PROBLEM: ${problem.title}`,
    trim(problem.statement, BUDGET.statement),
    sig ? `REQUIRED SIGNATURE: ${sig}` : 'This is a stdin → stdout program.',
    `\nMY CODE (${LANGS[lang]?.label}):\n${trim(numbered(code), BUDGET.code)}`,
    `\nLATEST RUN: ${runSummary(lastRun)}`,
  ];
  if (history.length) {
    let h = history.map((m) => `${m.role === 'user' ? 'ME' : 'COACH'}: ${m.text}`).join('\n');
    parts.push(`\nEARLIER IN THIS CHAT:\n${trim(h, BUDGET.history)}`);
  }
  parts.push(`\nTASK: ${task}`);
  return parts.join('\n');
}

export function mountCoach(el, getCtx) {
  const pid = getCtx().problem.id;
  const log = [];
  let busy = false;
  let abort = null;

  el.innerHTML = `
    <div class="coach">
      <div class="coach-head">
        <div class="who"><div class="avatar">✦</div><div><div>Coach</div><div class="st" data-st></div></div></div>
        <div class="chips">${ACTIONS.map((a) => `<button class="chip" data-act="${a.id}">${a.label}</button>`).join('')}</div>
      </div>
      <div class="coach-log" data-log></div>
      <form class="coach-input">
        <textarea class="input" rows="1" placeholder="Ask anything about this problem or your code…" data-q></textarea>
        <button class="btn primary" data-send>Ask</button>
      </form>
    </div>`;
  const $log = el.querySelector('[data-log]');
  const $st = el.querySelector('[data-st]');
  const $q = el.querySelector('[data-q]');
  const $form = el.querySelector('form');

  const refresh = () => {
    const s = aiStatus();
    $st.textContent = s.available ? 'Apple Intelligence · on-device · private' : 'Unavailable';
    el.querySelectorAll('.chip, [data-send]').forEach((b) => (b.disabled = !s.available || busy));
    if (!log.length) {
      $log.innerHTML = s.available
        ? `<div class="coach-empty">Stuck, curious, or want a second opinion? Pick an action above or ask a question.<br><br>The Coach sees the problem, your current code and your latest test run. It runs entirely on this Mac, so it's private, but it's a small model: double-check what it says against the tests.</div>`
        : `<div class="coach-empty">${esc(s.reason)}</div>`;
    }
  };
  const unsub = onCompanion(refresh);

  const render = () => {
    $log.innerHTML = log.map((m, i) => m.role === 'user'
      ? `<div class="msg user">${esc(m.text)}</div>`
      : `<div class="msg ai"><div class="label">✦ Coach</div><div class="md ${m.streaming ? 'cursor' : ''}" data-i="${i}">${md(m.text || '')}</div></div>`).join('');
    $log.querySelectorAll('.md').forEach((n) => enhance(n));
    $log.scrollTop = $log.scrollHeight;
  };

  async function ask(task, shown) {
    if (busy) return;
    const s = aiStatus();
    if (!s.available) return;
    busy = true; refresh();
    const ctx = getCtx();
    const history = log.slice(-4).map((m) => ({ role: m.role, text: m.text.slice(0, 600) }));
    log.push({ role: 'user', text: shown });
    const reply = { role: 'ai', text: '', streaming: true };
    log.push(reply);
    render();
    abort = new AbortController();
    let lastPaint = 0;
    try {
      await streamAI({ instructions: instructions(ctx.lang), prompt: buildPrompt(ctx, task, history), signal: abort.signal }, (_, full) => {
        reply.text = full;
        const now = performance.now();
        if (now - lastPaint > 60) {
          lastPaint = now;
          const node = $log.querySelector(`[data-i="${log.length - 1}"]`);
          if (node) { node.innerHTML = md(full); $log.scrollTop = $log.scrollHeight; }
        }
      });
    } catch (e) {
      if (e.name !== 'AbortError') reply.text += `\n\n**Coach error:** ${e.message}`;
    } finally {
      reply.streaming = false;
      busy = false;
      render();
      refresh();
    }
  }

  el.querySelectorAll('[data-act]').forEach((b) => {
    b.onclick = () => ask(TASKS[b.dataset.act], b.textContent);
  });
  $form.onsubmit = (e) => {
    e.preventDefault();
    const q = $q.value.trim();
    if (!q) return;
    $q.value = '';
    ask(`Answer my question: ${q}`, q);
  };
  $q.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); $form.requestSubmit(); }
  });
  $q.addEventListener('input', () => { $q.style.height = 'auto'; $q.style.height = Math.min(140, $q.scrollHeight) + 'px'; });

  refresh();
  return {
    askDebug: () => ask(TASKS.debug, 'Why is it failing?'),
    destroy: () => { unsub(); abort?.abort(); },
    pid,
  };
}
