# Authoring Crucible problems

Each file `content/NN_track.py` is a Python module that defines `TRACK` and `PROBLEMS`.
Files are plain Python, so tests can be generated with code (always use a seeded
`random.Random(seed)` so output is deterministic).

Build and validate one track:

```bash
python3 tools/build.py --only <track_id> --out /tmp/x.json   # schema + Python reference → expected outputs
node tools/check.mjs /tmp/x.json                              # every language through the real runner
```

Both must finish with zero errors. Expected outputs are **computed from your Python
`solution`**. Never write expected values by hand, so make sure the solution is correct.

## TRACK

```python
TRACK = dict(
    id="arrays",                 # kebab-case
    title="Arrays & Two Pointers",
    order=5,                     # position on the learning path
    icon="▦",                    # one glyph
    blurb="One sentence for the track card.",
    intro="""Markdown lesson (600–1200 words) taught before the problems: the core
ideas, diagrams in ASCII where helpful, the patterns to recognise, complexity, and
small code snippets in Python (and C/Rust where the language matters).""",
)
```

## Problem fields

| field | required | notes |
|---|---|---|
| `id` | ✓ | kebab-case, globally unique. Prefix ids with nothing; just make them descriptive |
| `title` | ✓ | |
| `difficulty` | ✓ | 0 First Steps · 1 Easy · 2 Medium · 3 Hard · 4 Expert |
| `kind` | | `"function"` (default), `"io"` (stdin → stdout program) or `"asm"` |
| `tags` | | list of short strings, e.g. `["array", "two pointers"]` |
| `fn` | function | snake_case function name. C++ and ESPresso get camelCase automatically |
| `params` | function | `[["nums", "int[]"], ["target", "int"]]`, names snake_case |
| `returns` | function | a type, or `"void"` together with `mutates="nums"` (output = that param after the call) |
| `statement` | ✓ | Markdown. Clear story + precise spec. Don't include examples; they are rendered from tests |
| `example_notes` | | list of markdown strings explaining example 1, 2, … |
| `examples` | | how many leading tests are shown as examples (default 2) |
| `constraints` | | list of markdown strings, e.g. `"1 ≤ len(nums) ≤ 10⁴"` |
| `hints` | ✓ | 2–4 progressive hints, from a gentle nudge to nearly the answer |
| `explanation` | ✓ | Markdown deep-dive, shown after solving. See below |
| `solution` | ✓ | Python reference, **heavily commented** (it is shown to the learner) |
| `refs` | | `{"c": ..., "cpp": ..., "rust": ..., "espresso": ...}` extra commented reference solutions (validated!) |
| `lang_notes` | | `{"c": "...", "rust": "..."}` markdown notes specific to a language |
| `tests` | ✓ | function: list of argument lists. io: list of stdin strings. ≥ 6 tests, include edge cases |
| `compare` | | `exact` (default; floats compared with 1e-6 tolerance), `unordered` (order of top-level list ignored), `unordered_deep` (order ignored at every level) |
| `espresso` | | `True/False` to force ESPresso availability (default: automatic, see below) |
| `langs` | | restrict languages, e.g. `["python", "cpp"]` (rarely needed) |
| `starters` | | `{"python": "...", ...}` override the generated starter (great for First Steps: guided TODOs) |

### Types

`int float bool str`, 1-D arrays `int[] float[] bool[] str[]`, 2-D arrays `int[][] float[][] str[][]`,
`list` (linked list of ints, JSON `[1,2,3]`), `tree` (binary tree, LeetCode level order `[1,null,2]`,
use Python `None`). Language mappings:

| type | Python | C | C++ | Rust |
|---|---|---|---|---|
| int | int | long long | long long | i64 |
| float | float | double | double | f64 |
| str | str | char* (return malloc-ed) | string | String |
| int[] | List[int] | `long long* a, int aSize` (+`int* returnSize` when returned) | vector<long long>& | Vec<i64> (`&mut` if mutated) |
| int[][] | List[List[int]] | `long long** a, int aSize, int* aColSize` | vector<vector<long long>>& | Vec<Vec<i64>> |
| list | ListNode | struct ListNode* | ListNode* | Option<Box<ListNode>> |
| tree | TreeNode | struct TreeNode* | TreeNode* | Option<Rc<RefCell<TreeNode>>> |

Keep ints within ±2⁵³. Results must be **deterministic and unique**. If several answers
are valid, either specify a tie-break in the statement (e.g. "return the lexicographically
smallest", "return indices in increasing order") or use a `compare` mode. There are no custom checkers.

"Design" problems (LRU cache, MinStack…) are written as a function that receives a list
of operations and returns the list of outputs, e.g.
`lru_cache(capacity: int, ops: str[], args: int[][]) -> int[]` with `-1` for "no output".
The explanation should still teach the class design.

Avoid huge tests: keep each problem's tests under ~60 KB of JSON, and make the largest
inputs big enough to punish an O(n²) solution only when the problem is *about*
complexity (n ≈ 10⁴–10⁵). Tests run in browsers via Pyodide too.

### ESPresso

ESPresso (the user's own embedded scripting language) is offered automatically when every
param is `int | float | bool | int[] | float[] | int[][]` and the return is `int | float | bool`
(or `void` + `mutates` an int array). io problems qualify only if no test has stdin.
ESPresso facts: `var`/`const`, `fn name(a, b) { ... }`, `if/else if/else`, `while`,
`for var i in 0..n` (exclusive), `len(x)`, `print(...)`, integer `/` truncates, **no `%`
operator** (use `a - (a / b) * b`), arrays are fixed-size (no push, no concatenation),
strings can't be indexed, **numbers are only exact up to ~2²⁴** (problems whose test values exceed ±16,777,215 automatically lose ESPresso), recursion depth < ~4000, no `+=` on strings needed. Set
`espresso=False` when the natural solution needs growing arrays, hash maps, or deep recursion.
An `refs["espresso"]` solution is very welcome for ESPresso-eligible problems.

### Assembly (`kind="asm"`)

Target: **ARM64 macOS** (Apple Silicon), assembled with clang. Function symbol is
`_<fn>`. Params arrive in x0–x7 in order; `int[]` takes two registers (pointer, count as
64-bit), `str` is a `const char*`. Return a 64-bit int in x0 (or `returns="void"`,
`mutates=...` for in-place array work). Provide:

- `asm_solution`: complete working `.s` (validated by check.mjs)
- `asm_starter`: the same file with a few key instructions replaced by
  `// TODO(n): <what this line must do>` lines. The learner fills in the blanks. Keep all the
  scaffolding (directives, labels, prologue/epilogue) and comment every line.
- `solution` is still a Python function computing the same result (used for expected outputs).

### The explanation (this is the heart of Crucible)

Markdown, roughly 300–900 words depending on difficulty, with these sections:

1. `## Intuition`: how to *think* about it; what clue in the statement points at the technique.
2. `## Approach`: step by step; include a worked trace on a small input (a table or ASCII is great).
3. `## Complexity`: time and space, with the reasoning.
4. `## Common mistakes`: off-by-ones, overflow, empty input, aliasing, language traps.
5. `## Going further`: a follow-up variant or related idea (optional for First Steps).

For First Steps/Easy, explain the *language mechanics* too (what `for`, `return`,
indexing, or `printf` actually do). Code fences must specify a language (```python, ```c, ```cpp, ```rust).

The Python `solution` must be thoroughly commented, explaining *why* each step exists, not
narrating syntax.
