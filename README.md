# Crucible

A personal coding-practice forge: problems from your very first program to expert
algorithms, solvable in **Python, C, C++, Rust, ESPresso and ARM64 assembly**, with
deep explanations, commented reference solutions, per-language cheat sheets, and an
on-device **Apple Intelligence Coach** that reviews your code and explains failures.

## Run it (full experience)

```bash
./crucible          # builds what's needed, starts http://localhost:4747 and opens it
```

The local companion (`companion/server.py`) serves the site and adds:

| Feature | Needs |
|---|---|
| Python | nothing (in-browser Pyodide), or local CPython when the companion runs |
| C / C++ | clang (compiled with AddressSanitizer + UBSan for clear memory-error reports) |
| Rust | rustc |
| ARM64 assembly | Apple Silicon + clang |
| ESPresso | `~/Projects/Code/Embedded/ESPresso/build/ESPresso` (or set `CRUCIBLE_ESPRESSO`) |
| Coach | macOS with Apple Intelligence enabled (Swift helper in `companion/ai/`) |

## Editor

Monaco with IDE-style help in every language (Python, C, C++, Rust, ESPresso, ARM64):
hover any library function, keyword, instruction or register for docs; completions are
type-aware (`q.` on a `deque`, `v.` on a `Vec`, `m.` on an `unordered_map`); parameter hints
appear as you type a call; F12/⌘-click jumps to your own functions, ⌘⇧O shows an outline;
compiler, sanitizer and runtime errors from a run are underlined on the offending line (F8 steps
through them). Reference data: `site/js/langdocs/<lang>.js` (schema in `SCHEMA.md`), engine in
`site/js/ide.js`.

## Hosted copy (GitHub Pages / Vercel)

`site/` is a static site. On a hosted copy, Python runs in the browser. For the other
languages and the Coach, run `./crucible` on your Mac (it automatically allows this repo's
`https://<you>.github.io` origin; set `CRUCIBLE_ORIGINS` for anything else), then click the
status pill (top right):

- **Chrome:** connects directly once you allow access to the local network.
- **Safari** (which blocks `https` pages from reaching `http://localhost`) and Chrome without
  that permission: click **Connect**. It opens a small bridge window served by the companion that
  relays requests via `postMessage`, only for allowed origins. Keep it open; reloading the
  page re-attaches automatically.

Progress lives in each origin's `localStorage`; use **Settings → Export/Import** to move it.

- **GitHub Pages:** push to `main`; `.github/workflows/pages.yml` builds and deploys `site/`.
- **Vercel:** `vercel deploy` (uses `vercel.json`, output dir `site/`). Commit
  `site/data/problems.json` first, since Vercel doesn't run the Python build.

## Content

Problems live in `content/NN_track.py` (spec: `content/AUTHORING.md`). Expected outputs
are computed from each problem's Python reference solution.

```bash
./crucible build                 # rebuild site/data/problems.json
./crucible check                 # run every problem in every language through the real runner
./crucible check --track dp -j 4 # just one track
```

## Layout

```
site/            static app (index.html, js/, css/, data/problems.json, data/cheatsheets/)
  js/harness.js  signature → starter code + test harness for every language
  js/ide.js      hover / completion / signature help / diagnostics; data in js/langdocs/
content/         problem sources (Python modules) + AUTHORING.md
companion/       local runner + Apple Intelligence bridge (Swift)
tools/           build.py (content → JSON), check.mjs (cross-language validation)
```
