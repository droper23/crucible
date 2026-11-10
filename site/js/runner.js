// Executes code: Python in the browser (Pyodide) or anything via the local companion.
import { store } from './store.js';

const RUN_TIMEOUT_MS = 15000;
let companion = { status: 'unknown', health: null, base: '' };
const subs = new Set();

export function onCompanion(f) { subs.add(f); f(companion); return () => subs.delete(f); }
export const companionInfo = () => companion;
const publish = (c) => { companion = c; subs.forEach((f) => f(companion)); };

// ------------------------------------------------------------ bridge transport
// Safari (and Chrome without the local-network permission) won't let an https page fetch
// http://localhost. The companion serves /bridge: a popup on its own origin that relays
// API calls over postMessage, after checking our origin against its allow-list.
const isHosted = () => location.protocol === 'https:' && !/^(localhost|127\.0\.0\.1)$/.test(location.hostname);
const companionUrl = () => (store.settings().companionUrl || 'http://localhost:4747').replace(/\/$/, '');
let bridge = null;            // { win, origin }
let bseq = 0;
const bpending = new Map();   // id -> { resolve, reject, onChunk }

window.addEventListener('message', (ev) => {
  const m = ev.data;
  if (!m || typeof m !== 'object' || typeof m.type !== 'string' || !m.type.startsWith('crucible-')) return;
  let expected;
  try { expected = new URL(companionUrl()).origin; } catch { return; }
  if (ev.origin !== expected) return;
  if (m.type === 'crucible-bridge-ready') {
    const fresh = !bridge || bridge.win !== ev.source;
    bridge = { win: ev.source, origin: ev.origin };
    if (fresh) {
      ev.source.postMessage({ type: 'crucible-hello' }, ev.origin);
      if (companion.status !== 'connected') detectCompanion();
    }
    return;
  }
  const p = bpending.get(m.id);
  if (!p) return;
  if (m.type === 'crucible-chunk') p.onChunk?.(m.text);
  else if (m.type === 'crucible-res') { bpending.delete(m.id); p.resolve(m); }
});

function bridgeAlive() { return !!bridge && !bridge.win.closed; }

function viaBridge(path, { method = 'GET', body, stream = false, onChunk, signal, timeout = 0 } = {}) {
  if (!bridgeAlive()) return Promise.reject(new TypeError('bridge closed'));
  const id = ++bseq;
  return new Promise((resolve, reject) => {
    let timer = null;
    const done = () => { clearTimeout(timer); clearInterval(watch); };
    bpending.set(id, { resolve: (m) => { done(); resolve(m); }, reject, onChunk });
    // Notice the popup being closed mid-request.
    const watch = setInterval(() => { if (!bridgeAlive()) { done(); bpending.delete(id); reject(new TypeError('bridge closed')); } }, 1000);
    if (timeout) timer = setTimeout(() => { done(); bpending.delete(id); reject(new TypeError('bridge timeout')); }, timeout);
    signal?.addEventListener('abort', () => { bridge?.win.postMessage({ type: 'crucible-abort', id }, bridge.origin); done(); bpending.delete(id); reject(new DOMException('Aborted', 'AbortError')); });
    bridge.win.postMessage({ type: 'crucible-req', id, path, method, body, stream }, bridge.origin);
  });
}

/** Open the bridge popup (must be called from a click). Resolves once connected or after a timeout. */
export function connectBridge() {
  const win = window.open(`${companionUrl()}/bridge`, 'crucible-bridge', 'popup,width=420,height=260');
  if (!win) return Promise.resolve(false);
  return new Promise((resolve) => {
    const t0 = Date.now();
    const iv = setInterval(() => {
      if (companion.status === 'connected' && companion.mode === 'bridge') { clearInterval(iv); resolve(true); }
      else if (Date.now() - t0 > 6000 || win.closed) { clearInterval(iv); resolve(false); }
    }, 200);
  });
}
export const bridgeNeeded = () => isHosted() && companion.status !== 'connected';

/** JSON API call through whichever transport is connected. */
async function api(path, body) {
  if (companion.mode === 'bridge') {
    const m = await viaBridge(path, { method: body ? 'POST' : 'GET', body: body && JSON.stringify(body) });
    if (m.error) throw new TypeError(m.error);
    return JSON.parse(m.text);
  }
  const r = await fetch(`${companion.base}${path}`, body
    ? { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Crucible': '1' }, body: JSON.stringify(body) }
    : { headers: { 'X-Crucible': '1' } });
  return r.json();
}

function candidates() {
  const out = [];
  // When served by the companion itself, use same-origin.
  if (/^(localhost|127\.0\.0\.1)$/.test(location.hostname)) out.push('');
  const url = (store.settings().companionUrl || '').replace(/\/$/, '');
  if (url && !out.includes(url)) out.push(url);
  return out;
}

export async function detectCompanion() {
  if (bridgeAlive()) {
    try {
      const m = await viaBridge('/api/health', { timeout: 4000 });
      if (m.ok) { publish({ status: 'connected', health: JSON.parse(m.text), base: bridge.origin, mode: 'bridge' }); return companion; }
    } catch { /* fall through */ }
  }
  for (const base of candidates()) {
    try {
      const ctl = new AbortController();
      const t = setTimeout(() => ctl.abort(), 2500);
      const r = await fetch(`${base}/api/health`, { headers: { 'X-Crucible': '1' }, signal: ctl.signal });
      clearTimeout(t);
      if (r.ok) {
        const health = await r.json();
        publish({ status: 'connected', health, base, mode: 'direct' });
        return companion;
      }
    } catch { /* try next */ }
  }
  publish({ status: 'offline', health: null, base: '', mode: null });
  return companion;
}

/** Can this language run right now? Returns null if yes, or a reason string. */
export function unavailableReason(lang) {
  if (lang === 'python') return null;
  if (companion.status !== 'connected') return isHosted() ? 'Start ./crucible on your Mac, then click the status pill (top right) to connect.' : 'Start the local companion (./crucible) to run this language.';
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
  const j = await api('/api/run', req);
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
  if (companion.status !== 'connected') return { available: false, reason: `The Coach runs on Apple Intelligence through the local companion. Start ./crucible to enable it${isHosted() ? ', then click the status pill (top right) to connect' : ''}.` };
  return companion.health?.ai || { available: false, reason: 'Unknown' };
}

/** Stream a completion; calls onDelta(text) as chunks arrive. Returns full text. */
export async function streamAI({ instructions, prompt, temperature = 0.3, signal }, onDelta) {
  if (companion.mode === 'bridge') {
    let full = '';
    const m = await viaBridge('/api/ai', { method: 'POST', body: JSON.stringify({ instructions, prompt, temperature }), stream: true, signal, onChunk: (t) => { full += t; onDelta(t, full); } });
    if (m.error) throw new Error(m.error);
    if (!m.ok) { let msg = `HTTP ${m.status}`; try { msg = JSON.parse(m.text).error || msg; } catch {} throw new Error(msg); }
    return full;
  }
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
