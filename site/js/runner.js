// Executes code: Python in the browser (Pyodide) or anything via the local companion.
import { store } from './store.js';

const RUN_TIMEOUT_MS = 15000;
let companion = { status: 'unknown', health: null, base: '' };
const subs = new Set();

export function onCompanion(f) { subs.add(f); f(companion); return () => subs.delete(f); }
export const companionInfo = () => companion;

function candidates() {
  const out = [];
  // When served by the companion itself, use same-origin.
  if (/^(localhost|127\.0\.0\.1)$/.test(location.hostname)) out.push('');
  const url = (store.settings().companionUrl || '').replace(/\/$/, '');
  if (url && !out.includes(url)) out.push(url);
  return out;
}

export async function detectCompanion() {
  for (const base of candidates()) {
    try {
      const ctl = new AbortController();
      const t = setTimeout(() => ctl.abort(), 2500);
      const r = await fetch(`${base}/api/health`, { headers: { 'X-Crucible': '1' }, signal: ctl.signal });
      clearTimeout(t);
      if (r.ok) {
        const health = await r.json();
        companion = { status: 'connected', health, base };
        subs.forEach((f) => f(companion));
        return companion;
      }
    } catch { /* try next */ }
  }
  companion = { status: 'offline', health: null, base: '' };
  subs.forEach((f) => f(companion));
  return companion;
}

/** Can this language run right now? Returns null if yes, or a reason string. */
export function unavailableReason(lang) {
  if (lang === 'python') return null;
  if (companion.status !== 'connected') return 'Start the local companion (./crucible) to run this language.';
  const v = companion.health?.langs?.[lang];
  if (!v) {
    if (lang === 'espresso') return 'ESPresso binary not found. Build ESPresso or set CRUCIBLE_ESPRESSO, then restart the companion.';
    if (lang === 'asm') return 'ARM64 assembly needs an Apple Silicon Mac with clang.';
    return `The companion couldn't find a ${lang} toolchain.`;
  }
  return null;
}

function usePyodide() {
  const pref = store.settings().pythonRuntime;
  if (pref === 'browser') return true;
  if (pref === 'local') return companion.status !== 'connected';
  return companion.status !== 'connected'; // auto: local is faster and has full CPython when available
}

// ------------------------------------------------------------ Pyodide worker
let worker = null;
let workerReady = null;
let seq = 0;
const pending = new Map();

function startWorker() {
  worker = new Worker(new URL('./pyworker.js', import.meta.url));
  workerReady = new Promise((resolve, reject) => {
    worker.onmessage = (ev) => {
      const m = ev.data;
      if (m.type === 'ready') resolve();
      else if (m.type === 'fatal') reject(new Error(m.error));
      else if (m.type === 'result') {
        const p = pending.get(m.id);
        if (p) { pending.delete(m.id); clearTimeout(p.timer); p.resolve(m.result); }
      }
    };
    worker.onerror = (e) => reject(new Error(e.message || 'Python worker failed to start'));
  });
}

export function warmPython() {
  if (!worker) startWorker();
  return workerReady;
}

async function runPyodide(req, onStatus) {
  if (!worker) startWorker();
  onStatus?.('Loading Python (first run downloads ~10 MB)…');
  await workerReady;
  onStatus?.('Running…');
  const id = ++seq;
  return new Promise((resolve) => {
    const timer = setTimeout(() => {
      pending.delete(id);
      worker.terminate();
      worker = null;
      startWorker();
      resolve({ compile: { ok: true }, runs: req.stdins.map(() => ({ stdout: '', stderr: '', exitCode: null, timedOut: true, timeMs: RUN_TIMEOUT_MS })) });
    }, RUN_TIMEOUT_MS);
    pending.set(id, { resolve, timer });
    worker.postMessage({ id, source: req.source, stdins: req.stdins });
  });
}

async function runCompanion(req, onStatus) {
  onStatus?.(['c', 'cpp', 'rust', 'asm'].includes(req.lang) ? 'Compiling & running…' : 'Running…');
  const r = await fetch(`${companion.base}/api/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Crucible': '1' },
    body: JSON.stringify(req),
  });
  const j = await r.json();
  if (j.error) throw new Error(j.error);
  return j;
}

export async function execute(req, onStatus) {
  if (req.lang === 'python' && usePyodide()) return runPyodide(req, onStatus);
  const why = unavailableReason(req.lang);
  if (why) throw new Error(why);
  try {
    return await runCompanion(req, onStatus);
  } catch (e) {
    if (e instanceof TypeError) { // network failure: companion went away
      await detectCompanion();
      if (req.lang === 'python') return runPyodide(req, onStatus);
      throw new Error('Lost connection to the local companion. Is ./crucible still running?');
    }
    throw e;
  }
}

// ------------------------------------------------------------ AI coach

export function aiStatus() {
  if (companion.status !== 'connected') return { available: false, reason: 'The Coach runs on Apple Intelligence through the local companion. Start ./crucible to enable it.' };
  return companion.health?.ai || { available: false, reason: 'Unknown' };
}

/** Stream a completion; calls onDelta(text) as chunks arrive. Returns full text. */
export async function streamAI({ instructions, prompt, temperature = 0.3, signal }, onDelta) {
  const r = await fetch(`${companion.base}/api/ai`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Crucible': '1' },
    body: JSON.stringify({ instructions, prompt, temperature }),
    signal,
  });
  if (!r.ok) {
    let msg = `HTTP ${r.status}`;
    try { msg = (await r.json()).error || msg; } catch {}
    throw new Error(msg);
  }
  const reader = r.body.getReader();
  const dec = new TextDecoder();
  let full = '';
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    const t = dec.decode(value, { stream: true });
    full += t;
    onDelta(t, full);
  }
  return full;
}
