#!/usr/bin/env python3
"""Crucible companion: serves the site locally and adds what a browser can't do.

  GET  /api/health   toolchain + Apple Intelligence status
  POST /api/run      compile and run code (C, C++, Rust, ARM64 asm, ESPresso, Python)
  POST /api/ai       stream a response from the on-device Apple Intelligence model
  GET  /bridge       popup that relays API calls for a hosted copy of the site via
                     postMessage (Safari blocks https pages from fetching http://localhost)

Binds to 127.0.0.1 only. Cross-origin requests are accepted only from origins
listed in CRUCIBLE_ORIGINS (comma separated) so a hosted copy of the site can
use this companion, and every API call must carry the X-Crucible header.
"""
from __future__ import annotations

import json
import os
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
AI_BIN = ROOT / "companion" / "ai" / "crucible-ai"
VERSION = "1.0.0"
MAX_OUTPUT = 512 * 1024
COMPILE_TIMEOUT = 60
RUN_TIMEOUT = float(os.environ.get("CRUCIBLE_RUN_TIMEOUT", "10"))
ORIGINS = {o.strip().rstrip("/") for o in os.environ.get("CRUCIBLE_ORIGINS", "").split(",") if o.strip()}

BRIDGE_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Crucible bridge</title>
<style>
:root { color-scheme: light dark; --bg: #f7f7f4; --fg: #1d1f24; --muted: #6b6f7b; --ok: #15803d; --bad: #c2410c; }
@media (prefers-color-scheme: dark) { :root { --bg: #15171e; --fg: #e6e7eb; --muted: #8b90a0; --ok: #4ade80; --bad: #fb923c; } }
body { margin: 0; padding: 24px; font: 14px/1.5 -apple-system, system-ui, sans-serif; background: var(--bg); color: var(--fg); }
h1 { font-size: 16px; margin: 0 0 6px; } p { margin: 6px 0; color: var(--muted); } b { color: var(--fg); }
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--muted); margin-right: 6px; }
.on .dot { background: var(--ok); } .err .dot { background: var(--bad); }
</style></head><body>
<h1>&#x1F525; Crucible bridge</h1>
<p id="st"><span class="dot"></span>Waiting for Crucible&hellip;</p>
<p>This little window lets the hosted Crucible page use the companion on your Mac. <b>Keep it open</b> (minimise it if you like); closing it disconnects.</p>
<script>
const ALLOWED = __ORIGINS__;
const st = document.getElementById('st');
const show = (cls, html) => { document.body.className = cls; st.innerHTML = '<span class="dot"></span>' + html; };
const aborts = new Map();
let peer = null;
if (!window.opener) show('err', 'Open this from the Crucible page (Connect button); it does nothing on its own.');
else if (!ALLOWED.length) show('err', 'No hosted origins allowed. Restart the companion with <code>CRUCIBLE_ORIGINS=https://&lt;you&gt;.github.io ./crucible</code>.');
// Announce ourselves to every allowed origin; postMessage only delivers to a matching one.
// Repeats so a reloaded Crucible page re-attaches without another popup.
function hello() {
  if (!window.opener || window.opener.closed) { if (peer) show('err', 'The Crucible page was closed. You can close this window.'); return; }
  for (const o of ALLOWED) { try { window.opener.postMessage({ type: 'crucible-bridge-ready' }, o); } catch (e) {} }
}
hello(); setInterval(hello, 1500);
window.addEventListener('message', async (ev) => {
  if (ev.source !== window.opener || !ALLOWED.includes(ev.origin)) return;
  const m = ev.data || {};
  const reply = (x) => ev.source.postMessage(Object.assign({ id: m.id }, x), ev.origin);
  if (m.type === 'crucible-hello') { peer = ev.origin; show('on', 'Connected to <b>' + ev.origin + '</b>'); return; }
  if (m.type === 'crucible-abort') { aborts.get(m.id)?.abort(); return; }
  if (m.type !== 'crucible-req' || typeof m.path !== 'string' || !m.path.startsWith('/api/')) return;
  const ctl = new AbortController(); aborts.set(m.id, ctl);
  try {
    const r = await fetch(m.path, { method: m.method || 'GET', headers: { 'Content-Type': 'application/json', 'X-Crucible': '1' }, body: m.body, signal: ctl.signal });
    if (m.stream && r.ok) {
      const rd = r.body.getReader(), dec = new TextDecoder();
      for (;;) { const { value, done } = await rd.read(); if (done) break; reply({ type: 'crucible-chunk', text: dec.decode(value, { stream: true }) }); }
      reply({ type: 'crucible-res', ok: true, status: r.status, text: '' });
    } else reply({ type: 'crucible-res', ok: r.ok, status: r.status, text: await r.text() });
  } catch (e) { reply({ type: 'crucible-res', ok: false, status: 0, error: String(e && e.message || e) }); }
  finally { aborts.delete(m.id); }
});
</script></body></html>
"""

DEFAULT_ESPRESSO = Path.home() / "Projects/Code/Embedded/ESPresso/build/ESPresso"


def find_espresso() -> str | None:
    cand = os.environ.get("CRUCIBLE_ESPRESSO") or str(DEFAULT_ESPRESSO)
    return cand if os.path.isfile(cand) and os.access(cand, os.X_OK) else None


def tool_version(cmd: list[str]) -> str | None:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        line = (out.stdout or out.stderr).strip().splitlines()
        return line[0] if line else "available"
    except Exception:
        return None


_health_cache: dict | None = None


def health() -> dict:
    global _health_cache
    if _health_cache is None:
        langs = {
            "python": tool_version([sys.executable, "--version"]),
            "c": tool_version(["clang", "--version"]),
            "cpp": tool_version(["clang++", "--version"]),
            "rust": tool_version(["rustc", "--version"]),
            "asm": tool_version(["clang", "--version"]) if os.uname().machine == "arm64" else None,
            "espresso": find_espresso(),
        }
        ai = {"available": False, "reason": "AI helper not built (run ./crucible build)"}
        if AI_BIN.exists():
            try:
                out = subprocess.run([str(AI_BIN), "--status"], capture_output=True, text=True, timeout=20)
                ai = json.loads(out.stdout.strip() or "{}") or ai
            except Exception as e:  # noqa: BLE001
                ai = {"available": False, "reason": f"AI helper failed: {e}"}
        _health_cache = {"ok": True, "version": VERSION, "langs": langs, "ai": ai}
    return _health_cache


# ------------------------------------------------------------------ running code

def _limits():
    os.setsid()
    resource.setrlimit(resource.RLIMIT_CPU, (int(RUN_TIMEOUT) + 2, int(RUN_TIMEOUT) + 3))
    resource.setrlimit(resource.RLIMIT_FSIZE, (16 * 1024 * 1024, 16 * 1024 * 1024))


def run_proc(cmd: list[str], cwd: str, stdin: str = "", timeout: float = RUN_TIMEOUT, env: dict | None = None) -> dict:
    start = time.monotonic()
    proc = subprocess.Popen(
        cmd, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        preexec_fn=_limits, env=env or os.environ.copy(),
    )
    timed_out = False
    try:
        out, err = proc.communicate(stdin.encode(), timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = proc.communicate()
    ms = int((time.monotonic() - start) * 1000)
    trunc = lambda b: b[:MAX_OUTPUT].decode("utf-8", "replace") + ("\n…[output truncated]" if len(b) > MAX_OUTPUT else "")
    code = proc.returncode
    if code is not None and code < 0:
        try:
            sig = signal.Signals(-code).name
        except ValueError:
            sig = str(-code)
        err += f"\n[process killed by signal {sig}]".encode()
    return {"stdout": trunc(out), "stderr": trunc(err), "exitCode": code, "timedOut": timed_out, "timeMs": ms}


def compile_step(cmd: list[str], cwd: str) -> dict:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=COMPILE_TIMEOUT)
    out = (p.stdout + p.stderr).replace(cwd + "/", "")
    return {"ok": p.returncode == 0, "output": out[:MAX_OUTPUT]}


SAN_ENV = {"ASAN_OPTIONS": "detect_leaks=0:abort_on_error=0:symbolize=1", "UBSAN_OPTIONS": "print_stacktrace=1"}


def execute(req: dict) -> dict:
    lang = req.get("lang")
    source = req.get("source", "")
    stdins = req.get("stdins") or [""]
    if len(stdins) > 200:
        raise ValueError("too many runs")
    with tempfile.TemporaryDirectory(prefix="crucible-") as d:
        env = os.environ.copy()
        if lang == "python":
            Path(d, "main.py").write_text(source)
            cmd = [sys.executable, "-I", "main.py"]
            comp = None
        elif lang in ("c", "cpp"):
            ext = "c" if lang == "c" else "cpp"
            Path(d, f"main.{ext}").write_text(source)
            for name, content in (req.get("headers") or {}).items():
                p = Path(d, "inc", name)
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content)
            compiler = ["clang", "-std=c17"] if lang == "c" else ["clang++", "-std=c++20", "-Iinc"]
            sanitize = [] if req.get("fast") else ["-fsanitize=address,undefined", "-fno-omit-frame-pointer"]
            comp = compile_step(compiler + ["-g", "-O1", *sanitize, "-Wall", "-Wno-unused-function", "-Wno-unused-variable", "-Wno-unused-parameter", f"main.{ext}", "-o", "prog", "-lm"], d)
            cmd = ["./prog"]
            env.update(SAN_ENV)
        elif lang == "rust":
            Path(d, "main.rs").write_text(source)
            comp = compile_step(["rustc", "--edition", "2021", "-C", "opt-level=1", "-C", "debuginfo=1", "-A", "unused", "-A", "dead_code", "main.rs", "-o", "prog"], d)
            cmd = ["./prog"]
            env["RUST_BACKTRACE"] = "0"
        elif lang == "asm":
            Path(d, "harness.c").write_text(source)
            Path(d, "solution.s").write_text(req.get("asm", ""))
            comp = compile_step(["clang", "-g", "-O0", "-Wno-unused-function", "harness.c", "solution.s", "-o", "prog", "-lm"], d)
            cmd = ["./prog"]
        elif lang == "espresso":
            esp = find_espresso()
            if not esp:
                return {"compile": {"ok": False, "output": "ESPresso binary not found. Build it (cmake --build build) or set CRUCIBLE_ESPRESSO."}, "runs": []}
            Path(d, "main.espr").write_text(source)
            cmd = [esp, "main.espr"]
            comp = None
        else:
            raise ValueError(f"unsupported language {lang!r}")
        if comp and not comp["ok"]:
            return {"compile": comp, "runs": []}
        runs = [run_proc(cmd, d, s, env=env) for s in stdins]
        return {"compile": comp or {"ok": True, "output": ""}, "runs": runs}


# ------------------------------------------------------------------ handler

class Handler(SimpleHTTPRequestHandler):
    server_version = f"Crucible/{VERSION}"

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(SITE), **kw)

    def log_message(self, fmt, *args):
        if os.environ.get("CRUCIBLE_VERBOSE"):
            super().log_message(fmt, *args)

    def end_headers(self):
        if self.path.startswith("/api/"):
            origin = (self.headers.get("Origin") or "").rstrip("/")
            if origin and origin in ORIGINS:
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Vary", "Origin")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Crucible")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Private-Network", "true")
        else:
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def _origin_ok(self) -> bool:
        origin = (self.headers.get("Origin") or "").rstrip("/")
        host = self.headers.get("Host", "")
        same = origin in ("", f"http://{host}")
        return (same or origin in ORIGINS) and self.headers.get("X-Crucible") == "1"

    def _json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def do_GET(self):
        if self.path.split("?")[0] == "/bridge":
            body = BRIDGE_HTML.replace("__ORIGINS__", json.dumps(sorted(ORIGINS))).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.startswith("/api/"):
            if not self._origin_ok():
                return self._json({"error": "forbidden"}, 403)
            if self.path == "/api/health":
                return self._json(health())
            return self._json({"error": "not found"}, 404)
        return super().do_GET()

    def _body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        if n > 8 * 1024 * 1024:
            raise ValueError("request too large")
        return json.loads(self.rfile.read(n) or b"{}")

    def do_POST(self):
        if not self._origin_ok():
            return self._json({"error": "forbidden"}, 403)
        try:
            req = self._body()
            if self.path == "/api/run":
                return self._json(execute(req))
            if self.path == "/api/ai":
                return self._ai(req)
            return self._json({"error": "not found"}, 404)
        except Exception as e:  # noqa: BLE001
            return self._json({"error": str(e)}, 400)

    def _ai(self, req: dict):
        if not health()["ai"].get("available"):
            return self._json({"error": health()["ai"].get("reason", "Apple Intelligence unavailable")}, 503)
        payload = json.dumps({
            "instructions": str(req.get("instructions", ""))[:6000],
            "prompt": str(req.get("prompt", ""))[:16000],
            "temperature": float(req.get("temperature", 0.3)),
        })
        proc = subprocess.Popen([str(AI_BIN)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.stdin.write(payload.encode())
        proc.stdin.close()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Accel-Buffering", "no")
        self.send_header("Connection", "close")
        self.end_headers()
        timer = threading.Timer(180, proc.kill)
        timer.start()
        try:
            while True:
                chunk = proc.stdout.read1(4096)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
            proc.wait()
            if proc.returncode:
                err = proc.stderr.read().decode("utf-8", "replace").strip()
                self.wfile.write(f"\n\n**Coach error:** {err or 'the model stopped unexpectedly'}".encode())
        except (BrokenPipeError, ConnectionResetError):
            proc.kill()
        finally:
            timer.cancel()
        self.close_connection = True


def main():
    port = int(os.environ.get("CRUCIBLE_PORT", "4747"))
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        print(json.dumps(health(), indent=2))
        return
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    srv.daemon_threads = True
    print(f"Crucible running at http://localhost:{port}  (Ctrl+C to stop)", flush=True)
    threading.Thread(target=health, daemon=True).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
