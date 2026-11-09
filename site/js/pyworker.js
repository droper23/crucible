// Runs Python in the browser via Pyodide. One worker = one interpreter; the main
// thread terminates and recreates it on timeout.
importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.2/full/pyodide.js');

let py = null;
const ready = (async () => {
  py = await loadPyodide();
  postMessage({ type: 'ready', version: py.version });
})().catch((e) => postMessage({ type: 'fatal', error: String(e) }));

const enc = new TextDecoder();

onmessage = async (ev) => {
  const { id, source, stdins } = ev.data;
  await ready;
  const runs = [];
  for (const stdin of stdins) {
    let out = '';
    let err = '';
    let fed = false;
    py.setStdout({ write: (buf) => { out += enc.decode(buf); return buf.length; } });
    py.setStderr({ write: (buf) => { err += enc.decode(buf); return buf.length; } });
    py.setStdin({ stdin: () => { if (fed) return null; fed = true; return stdin; }, autoEOF: true });
    const t0 = performance.now();
    let exitCode = 0;
    try {
      // fresh globals for every run so problems don't leak state into each other
      const globals = py.toPy({});
      await py.runPythonAsync(source, { globals, filename: 'main.py' });
      globals.destroy();
    } catch (e) {
      exitCode = 1;
      err += cleanTraceback(String(e.message || e));
    }
    try { py.runPython('import sys; sys.stdout.flush(); sys.stderr.flush()'); } catch {}
    runs.push({ stdout: out, stderr: err, exitCode, timedOut: false, timeMs: Math.round(performance.now() - t0) });
  }
  postMessage({ type: 'result', id, result: { compile: { ok: true, output: '' }, runs } });
};

function cleanTraceback(msg) {
  // Drop Pyodide-internal frames; keep the learner's frames (solution.py) and the error line.
  const lines = msg.split('\n');
  const keep = [];
  let skip = false;
  for (const l of lines) {
    if (/^\s+File "\/lib\/python/.test(l) || /File "<exec>"/.test(l) || /File "main\.py"/.test(l)) { skip = true; continue; }
    if (skip && /^\s{4}/.test(l)) { continue; }
    skip = false;
    keep.push(l);
  }
  return keep.join('\n');
}
