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

## Hosted copy (GitHub Pages / Vercel)

`site/` is a static site. On a hosted copy, Python runs in the browser. To light up
the other languages and the Coach from the hosted page, run the companion with that
origin allowed:

```bash
CRUCIBLE_ORIGINS=https://<you>.github.io ./crucible
```

(Chrome will ask permission for the page to reach `localhost`. Safari blocks it, so use
the local URL there.) Progress lives in each origin's `localStorage`; use
**Settings → Export/Import** to move it.

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
content/         problem sources (Python modules) + AUTHORING.md
companion/       local runner + Apple Intelligence bridge (Swift)
tools/           build.py (content → JSON), check.mjs (cross-language validation)
```
