"""Track 9: Recursion & Backtracking."""
import random

TRACK = dict(
    id="recursion",
    title="Recursion & Backtracking",
    order=9,
    icon="↻",
    blurb="Solve a problem by trusting a smaller copy of itself, then explore choice trees with choose / explore / un-choose.",
    intro=r"""
A **recursive** function solves a problem by calling itself on a *smaller* version of
the same problem. It has exactly two kinds of path through it:

- the **base case**: an input so small the answer is known directly (no further calls);
- the **recursive case**: shrink the input, call yourself, and combine the result.

```python
def fact(n):
    if n <= 1:              # base case: stops the descent
        return 1
    return n * fact(n - 1)  # recursive case: smaller input, then combine
```

If any path through the function fails to make progress toward a base case, the
recursion never stops and you run out of stack.

## What actually happens: the call stack

Every call gets a fresh **stack frame** holding its parameters, local variables and the
address to return to. Calling `fact(3)` pushes frames until the base case, then pops
them one by one as each `return` hands its value to the waiting caller:

```text
 push phase (descending)                     pop phase (returning)

 ┌────────────────┐                          ┌────────────────┐
 │ fact(1) n=1    │ ← top, returns 1         │                │
 ├────────────────┤                          ├────────────────┤
 │ fact(2) n=2    │ waiting: 2 * ?           │ fact(2): 2*1=2 │ ← top, returns 2
 ├────────────────┤                          ├────────────────┤
 │ fact(3) n=3    │ waiting: 3 * ?           │ fact(3): 3*2=6 │ then returns 6
 └────────────────┘                          └────────────────┘
```

Two consequences matter constantly:

1. **Locals are per frame.** The `n` in `fact(3)` and the `n` in `fact(2)` are different
   variables. This is what lets backtracking "remember" where each level was.
2. **Depth costs memory.** A recursion `d` levels deep holds `d` frames at once, so its
   space is O(d) even if it allocates nothing on the heap.

## The leap of faith

The trick to *writing* recursion is to not trace it in your head. Assume the call on the
smaller input already returns the right answer, and ask only: *how do I build my answer
from that?* Then check that the base case is correct and that every call shrinks the
input. That is just induction: base case + inductive step.

## Overlapping subproblems → memoisation

Naive `fib(n) = fib(n-1) + fib(n-2)` recomputes the same values exponentially often.
Caching results by argument (**memoisation**) collapses the call tree into a call *chain*.
Whenever the same arguments recur, think "cache".

## Backtracking: exploring a tree of choices

Many problems ask for *all* arrangements: every subset, every permutation, every
placement of queens. Picture a **decision tree**: each level makes one choice, each
leaf is a complete candidate. Backtracking is a depth-first walk of that tree that keeps
a single mutable "path" and undoes each choice on the way back up:

```python
def backtrack(path, choices):
    if is_complete(path):
        results.append(path.copy())   # copy! path keeps changing after this
        return
    for c in choices:
        if not valid(path, c):        # pruning: skip dead branches early
            continue
        path.append(c)                # 1. choose
        backtrack(path, next_choices(c))  # 2. explore
        path.pop()                    # 3. un-choose (restore the state)
```

The decision tree for subsets of `[1, 2, 3]` ("take it or leave it" at each element):

```text
                    []
            /take 1        \skip 1
          [1]               []
        /     \           /    \
     [1,2]    [1]       [2]     []
     /  \     / \       / \     / \
 [1,2,3][1,2][1,3][1][2,3][2] [3] []      ← 8 leaves = 2³ subsets
```

**Choose / explore / un-choose** is the whole template. Getting the un-choose exactly
right is the most common source of bugs: whatever you mark, append, or place before the
recursive call must be unmarked, popped, or removed after it.

## Pruning

The size of a decision tree is usually exponential, so the real skill is cutting
branches *before* walking them: stop a combination sum once the running total exceeds
the target, skip a queen square already attacked, refuse to close a parenthesis that has
no partner. Good pruning routinely turns "hopeless" into "instant" without changing the
worst-case big-O.

## Complexity of recursive algorithms

Count **(number of calls) × (work per call)**, and space as **max depth × frame size**
plus whatever you store. Useful shapes:

| shape | example | time |
|---|---|---|
| one call, n − 1 | factorial, digit sum | O(n) |
| one call, n / 2 | fast power | O(log n) |
| two calls, n − 1 | Hanoi | O(2ⁿ) |
| branch per element | subsets | O(2ⁿ · n) |
| shrinking branching | permutations | O(n! · n) |

## Recursion depth limits, per language

Recursion depth is limited by the call stack, and each language fails differently:

- **Python**: CPython stops at `sys.getrecursionlimit()` (default **1000**) with a
  `RecursionError`. You can raise it with `sys.setrecursionlimit` (Crucible's harness uses
  20000), but CPython frames still consume the real C stack, so very large limits can crash
  the interpreter outright. For depth in the tens of thousands, convert to a loop with an
  explicit stack.
- **C / C++**: no limit check at all. The main thread's stack is typically **8 MB**
  (macOS/Linux; 1 MB on Windows). Overflowing it is a segmentation fault with no message.
  Small frames survive ~10⁵ levels; big local arrays in each frame cut that sharply.
- **Rust**: the main thread also gets the OS default (~8 MB) and spawned threads get
  **2 MB**. Overflow aborts with `thread '…' has overflowed its stack`. Watch out for
  implicit recursion too: dropping a long `Box`-linked chain recurses once per node.
- **ESPresso**: the interpreter caps depth at roughly **4000** frames. All problems in this
  track that offer ESPresso stay well below that.

Rule of thumb: recursion depth equal to the *log* of the input or to a small search
depth (≤ a few hundred) is always safe. Depth proportional to a large input `n` is a
design smell outside of Python-sized toy inputs.

```c
// C: each frame holds n plus a return address, a few dozen bytes. Fine for n = 10^5,
// a crash (SIGSEGV) somewhere around a few hundred thousand on an 8 MB stack.
long long sum_to(long long n) { return n == 0 ? 0 : n + sum_to(n - 1); }
```

## Patterns to recognise in this track

- "Compute f(n) from f(smaller n)": plain recursion (power, digit sum, Hanoi).
- "Same arguments keep coming back": memoise (Fibonacci).
- "Return all …": backtracking with a path (subsets, permutations, combinations).
- "Does any arrangement exist / count them": backtracking that returns a bool or a
  count, with aggressive pruning (word search, N-Queens, Sudoku).
""",
)

PROBLEMS = []

# ---------------------------------------------------------------- 1. fast power
_rng = random.Random(901)
_pow_tests = [
    [2, 10, 1000],
    [3, 0, 7],
    [0, 0, 5],
    [5, 3, 1],
    [2, 1000000000, 1000000007],
    [123456789, 987654321, 1000000007],
    [999999999, 999999999, 999999937],
    [7, 1, 13],
    [0, 5, 10],
    [10, 18, 9973],
] + [[_rng.randint(0, 10**9), _rng.randint(0, 10**9), _rng.randint(1, 10**9 + 7)] for _ in range(5)]

PROBLEMS.append(dict(
    id="fast-power-mod",
    title="Fast Power (Modular Exponentiation)",
    difficulty=1,
    tags=["recursion", "divide and conquer", "math"],
    fn="pow_mod",
    params=[["base", "int"], ["exponent", "int"], ["modulus", "int"]],
    returns="int",
    statement=r"""
Computing `base^exponent` by multiplying `base` into an accumulator `exponent` times works,
but when the exponent is a billion that is a billion multiplications. Recursion gives a much
faster route.

Return **`base^exponent mod modulus`**, i.e. the remainder of `base` raised to `exponent`
when divided by `modulus`. By convention `x^0 = 1` for every `x` (including `0^0`), so the
answer for `exponent = 0` is `1 mod modulus`.

Your solution must run in **O(log exponent)** multiplications: the largest tests have
exponents near 10⁹.
""",
    constraints=["0 ≤ base ≤ 10⁹", "0 ≤ exponent ≤ 10⁹", "1 ≤ modulus ≤ 10⁹ + 7"],
    example_notes=[
        "2¹⁰ = 1024, and 1024 mod 1000 = 24.",
        "Anything to the power 0 is 1, and 1 mod 7 = 1.",
    ],
    hints=[
        "How does `x^10` relate to `x^5`? How does `x^11` relate to `x^5`?",
        "`x^e = (x^(e/2))²` when `e` is even, and `x · (x^(e/2))²` when it is odd (integer division). That halves the exponent each call.",
        "Compute the half power **once**, store it in a variable, then square it. Calling the function twice for the two halves throws away the whole speed-up. Reduce modulo `modulus` after every multiplication so numbers stay small.",
    ],
    explanation=r"""
## Intuition

The clue is the size of the exponent: 10⁹ multiplications is far too many, so we need to
shrink the exponent faster than by one each step. Exponents add when you multiply powers:
`x^a · x^a = x^(2a)`. So if we know `x^(e/2)`, one squaring gives us `x^e` (plus one
extra factor of `x` when `e` is odd). Each recursive call **halves** the exponent, so the
recursion is only about log₂(10⁹) ≈ 30 levels deep.

This is the simplest example of *divide and conquer*: split the problem into a half-size
copy, solve it recursively, and combine with O(1) work.

## Approach

1. **Base case:** `exponent == 0` → return `1 % modulus` (the `%` handles `modulus = 1`,
   where every answer is 0).
2. **Recursive case:** `half = pow_mod(base, exponent // 2, modulus)`.
3. `result = half * half % modulus`.
4. If `exponent` is odd, multiply in one more `base % modulus` and reduce again.

Trace for `pow_mod(2, 10, 1000)`:

| call | exponent | half returned | squared | odd? | returns |
|---|---|---|---|---|---|
| 1 | 10 | 32 | 1024 → 24 | no | 24 |
| 2 | 5 | 4 | 16 | yes → 32 | 32 |
| 3 | 2 | 2 | 4 | no | 4 |
| 4 | 1 | 1 | 1 | yes → 2 | 2 |
| 5 | 0 | – | – | – | 1 (base case) |

Read the table bottom-up: that is the order in which the frames return.

**Why reducing modulo every step is legal:** `(a · b) mod m = ((a mod m) · (b mod m)) mod m`.
Remainders can be taken at any point without changing the final remainder, and keeping
every intermediate below `m` means a product is below `m² ≈ 10¹⁸`, which fits in a
signed 64-bit integer (max ≈ 9.2 · 10¹⁸) but **not** in 32 bits.

## Complexity

- **Time:** O(log exponent). Each call does O(1) work and halves the exponent.
- **Space:** O(log exponent) stack frames, about 30 for the largest input. An iterative
  version (scan the bits of the exponent, squaring as you go) uses O(1) space.

## Common mistakes

- **Two recursive calls:** `pow(b, e//2) * pow(b, e//2)` recomputes the half, giving
  T(e) = 2T(e/2) + 1 = **O(e)**. Store the half in a variable.
- **Forgetting `1 % modulus`** in the base case: with `modulus = 1` the answer must be 0.
- **Overflow:** without reducing, `base^exponent` explodes immediately. Even with
  reduction, `half * half` can reach ≈ 10¹⁸: use `long long` in C/C++ and `i64` in Rust,
  never `int`/`i32`. With a modulus near 10¹⁸ even 64 bits is not enough and you would need
  `__int128` (C/C++) or `u128` (Rust) for the product.
- **Not reducing `base` first:** `base` can be 10⁹ while the running result is near
  10⁹ too; reducing `base % modulus` keeps the product bounded by `modulus²`.

## Going further

- The same squaring idea computes **matrix powers**, which yields Fibonacci numbers in
  O(log n) and solves linear recurrences quickly.
- Python's built-in `pow(base, exponent, modulus)` is exactly this algorithm.
- Fermat's little theorem uses fast power to compute modular inverses:
  `a⁻¹ ≡ a^(p−2) (mod p)` for prime `p`.
""",
    solution=r'''def pow_mod(base, exponent, modulus):
    # Base case: x^0 = 1. Taking "% modulus" makes modulus = 1 give 0, as it must.
    if exponent == 0:
        return 1 % modulus

    # Recursive case: solve the half-size problem ONCE.
    # exponent // 2 rounds down, so for odd exponents we owe one extra factor of base.
    half = pow_mod(base, exponent // 2, modulus)

    # x^e = (x^(e//2))^2 for even e. Reduce right away so numbers stay below modulus^2
    # (Python ints never overflow, but in C/Rust this keeps the product inside 64 bits).
    result = half * half % modulus

    # For odd e: x^e = x * (x^(e//2))^2. Reduce base first; it may be much larger
    # than modulus.
    if exponent % 2 == 1:
        result = result * (base % modulus) % modulus

    return result
''',
    refs={
        "c": r"""// Recursive fast exponentiation: O(log exponent) calls, each O(1).
long long pow_mod(long long base, long long exponent, long long modulus) {
    if (exponent == 0) return 1 % modulus;          // x^0 = 1 (and 0 when modulus == 1)

    // Compute the half power exactly once and keep it in a local variable.
    // Each frame has its own `half`; the call stack is only ~30 frames deep.
    long long half = pow_mod(base, exponent / 2, modulus);
    long long result = half * half % modulus;       // < modulus^2 ~ 1e18 < 2^63: fits

    if (exponent % 2 == 1)                          // odd: one extra factor of base
        result = result * (base % modulus) % modulus;
    return result;
}
""",
        "cpp": r"""// Same algorithm as the Python reference. long long keeps every product exact.
long long powMod(long long base, long long exponent, long long modulus) {
    if (exponent == 0) return 1 % modulus;
    long long half = powMod(base, exponent / 2, modulus);   // one recursive call only
    long long result = half * half % modulus;
    if (exponent & 1) result = result * (base % modulus) % modulus;  // odd exponent
    return result;
}
""",
        "rust": r"""/// Fast modular exponentiation by repeated squaring.
pub fn pow_mod(base: i64, exponent: i64, modulus: i64) -> i64 {
    if exponent == 0 {
        return 1 % modulus; // x^0 = 1, reduced (modulus 1 -> 0)
    }
    // Halve the exponent; the recursion depth is about log2(exponent) <= 30.
    let half = pow_mod(base, exponent / 2, modulus);
    let mut result = half * half % modulus;
    if exponent % 2 == 1 {
        // Odd exponent: multiply in the factor lost by integer division.
        result = result * (base % modulus) % modulus;
    }
    result
}
""",
    },
    # ESPresso divides integers through 32-bit floats (exact only below 2^24), so
    # exponents near 1e9 cannot be halved reliably there: disable it for this problem.
    espresso=False,
    tests=_pow_tests,
))

# ---------------------------------------------------------------- 2. fibonacci memo
PROBLEMS.append(dict(
    id="fibonacci-memoized",
    title="Fibonacci with Memoization",
    difficulty=1,
    tags=["recursion", "memoization", "dynamic programming"],
    fn="fib",
    params=[["n", "int"]],
    returns="int",
    statement=r"""
The Fibonacci numbers are defined by

- `F(0) = 0`, `F(1) = 1`
- `F(n) = F(n − 1) + F(n − 2)` for `n ≥ 2`

so the sequence begins `0, 1, 1, 2, 3, 5, 8, 13, …`.

Return **`F(n)`**. The definition is already a recursive program, but the direct
translation makes billions of calls for `n = 46`. Keep the recursive shape and make it
fast by remembering answers you have already computed.
""",
    constraints=["0 ≤ n ≤ 46 (so F(n) < 2³¹)"],
    example_notes=[
        "F(10) = 55: the sequence runs 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55.",
        "F(0) = 0 is a base case.",
    ],
    hints=[
        "Draw the call tree of the naive recursion for `fib(5)`. How many times is `fib(2)` computed?",
        "There are only `n + 1` distinct arguments, yet the naive tree has ~1.6ⁿ nodes. Store each answer the first time you compute it.",
        "Keep a cache (dict or array indexed by `n`). At the top of the function: if `n` is cached, return it. Otherwise compute `fib(n-1) + fib(n-2)`, store it, and return it.",
    ],
    explanation=r"""
## Intuition

The naive recursion is correct but catastrophically slow. Look at its call tree:

```text
                 fib(5)
              /          \
         fib(4)          fib(3)
        /     \          /    \
    fib(3)   fib(2)   fib(2)  fib(1)
    /   \     /  \     /  \
 fib(2) fib(1) ...
```

`fib(3)` appears twice, `fib(2)` three times, and the duplication compounds: the tree for
`fib(n)` has about φⁿ ≈ 1.618ⁿ nodes, around **3 billion** for `n = 46`. Yet there are only
47 different questions being asked. That is the signature of **overlapping
subproblems**, and the cure is **memoisation**: cache each answer by its argument and
look it up before recomputing.

## Approach

1. Keep a cache mapping `n → F(n)`.
2. Base cases: `n < 2` returns `n`.
3. If `n` is in the cache, return the cached value immediately.
4. Otherwise compute `fib(n-1) + fib(n-2)`, store it, return it.

With the cache, the first call descends `fib(46) → fib(45) → … → fib(1)` along the left
spine. Every right-hand call `fib(n-2)` then finds its answer already cached:

| call | cache before | action | stored |
|---|---|---|---|
| fib(4) | {} | recurse fib(3) | |
| fib(3) | {} | recurse fib(2) | |
| fib(2) | {} | fib(1)+fib(0)=1 | 2→1 |
| fib(3) | {2:1} | fib(2)+**fib(1)**=2 | 3→2 |
| fib(4) | {2:1,3:2} | fib(3)+**fib(2) (cached)**=3 | 4→3 |

The tree collapses into a chain of `n` frames plus `n` instant lookups.

In Python the cache can be a dict, or simply the `functools.lru_cache` decorator. In C,
Rust and ESPresso, an array indexed by `n` is natural, using a sentinel like 0 or −1 for
"not computed yet" (F(n) > 0 for every n ≥ 1, so 0 works once the base cases are handled).

## Complexity

- **Time:** O(n). Each `fib(k)` is computed once; every other request is an O(1) lookup.
- **Space:** O(n) for the cache plus O(n) recursion depth.

The **bottom-up** version (iterate `a, b = b, a + b`) is O(n) time and O(1) space with no
recursion at all. Memoised recursion (top-down) and tabulation (bottom-up) are the two
faces of dynamic programming. Top-down is easier to derive from a recursive definition;
bottom-up avoids the stack.

## Common mistakes

- **Caching after the recursive calls but checking nowhere**: the lookup must come
  *before* recursing, or the cache never saves work.
- **A cache local to each call**: `def fib(n): memo = {}` creates a new, empty cache in every
  frame. It must be shared: a global, a closure variable, or a parameter passed down.
- **Overflow:** F(47) exceeds 2³¹ − 1 and F(93) exceeds 2⁶³ − 1. That is why `n ≤ 46` here.
- **Sentinel collisions:** using 0 as "unknown" is only safe because F(n) ≠ 0 for n ≥ 1
  and `n = 0` is handled as a base case first.

## Going further

- **Fast doubling** computes F(n) in O(log n) using
  F(2k) = F(k)·(2F(k+1) − F(k)) and F(2k+1) = F(k)² + F(k+1)², the same halving idea
  as fast power.
- Memoisation applies to any pure recursive function with repeated arguments: counting
  paths in a grid, climbing stairs, edit distance. It is the bridge into the DP track.
""",
    solution=r'''from functools import lru_cache


def fib(n):
    # The cache lives OUTSIDE the recursive helper so every frame shares it.
    # (A dict created inside the recursive function would be empty in each call.)
    memo = {}

    def go(k):
        # Base cases: F(0) = 0, F(1) = 1. They stop the descent.
        if k < 2:
            return k
        # Already answered? Return immediately: this is what kills the exponential blow-up.
        if k in memo:
            return memo[k]
        # First time we see k: compute it from the two smaller answers, then remember it.
        memo[k] = go(k - 1) + go(k - 2)
        return memo[k]

    return go(n)

# Equivalent one-liner in idiomatic Python:
#   @lru_cache(maxsize=None)
#   def fib(n): return n if n < 2 else fib(n - 1) + fib(n - 2)
''',
    refs={
        "c": r"""// memo[k] == 0 means "not computed yet". Safe because F(k) > 0 for every k >= 1,
// and k = 0 is handled by the base case before we ever look at the memo.
static long long memo[64];

static long long go(int k) {
    if (k < 2) return k;                    // base cases
    if (memo[k]) return memo[k];            // cached: O(1)
    memo[k] = go(k - 1) + go(k - 2);        // compute once, store
    return memo[k];
}

long long fib(long long n) {
    // The memo can safely persist between calls: F(k) never changes.
    return go((int)n);
}
""",
        "cpp": r"""// A vector cache indexed by k, shared by every frame through a reference.
static long long go(int k, vector<long long>& memo) {
    if (k < 2) return k;                       // base cases
    if (memo[k] != -1) return memo[k];         // -1 = unknown
    return memo[k] = go(k - 1, memo) + go(k - 2, memo);
}

long long fib(long long n) {
    vector<long long> memo(n + 1, -1);
    return go((int)n, memo);
}
""",
        "rust": r"""/// Top-down Fibonacci. The memo is a `Vec<Option<i64>>`: `None` means "not yet computed",
/// which is clearer than a magic sentinel value.
pub fn fib(n: i64) -> i64 {
    fn go(k: usize, memo: &mut Vec<Option<i64>>) -> i64 {
        if k < 2 {
            return k as i64; // base cases
        }
        if let Some(v) = memo[k] {
            return v; // cached
        }
        // `memo` is a &mut borrow passed down; each call releases it before the next.
        let v = go(k - 1, memo) + go(k - 2, memo);
        memo[k] = Some(v);
        v
    }
    let n = n as usize;
    let mut memo = vec![None; n + 1];
    go(n, &mut memo)
}
""",
        "espresso": r"""// ESPresso arrays are fixed-size, so the memo is a literal with room for n <= 46.
// 0 means "unknown" (F(k) > 0 for k >= 1, and k < 2 is a base case).
var memo = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

fn fib(n) {
  if n < 2 {
    return n
  }
  if memo[n] != 0 {
    return memo[n]
  }
  memo[n] = fib(n - 1) + fib(n - 2)
  return memo[n]
}
""",
    },
    tests=[[10], [0], [1], [2], [5], [20], [30], [40], [45], [46]],
))

# ---------------------------------------------------------------- 3. digit sum
_rng = random.Random(903)
PROBLEMS.append(dict(
    id="sum-of-digits-recursive",
    title="Sum of Digits (Recursive)",
    difficulty=1,
    tags=["recursion", "math"],
    fn="digit_sum",
    params=[["n", "int"]],
    returns="int",
    statement=r"""
Given a non-negative integer `n`, return the **sum of its decimal digits**.

Solve it recursively: a number's digit sum is its last digit plus the digit sum of the
number with that last digit removed. Use arithmetic (`% 10` and `/ 10`), not string
conversion.
""",
    constraints=["0 ≤ n ≤ 10⁷"],
    example_notes=["1 + 2 + 3 + 4 = 10.", "A single digit is its own digit sum."],
    hints=[
        "What are `n % 10` and `n / 10` (integer division) for `n = 1234`?",
        "`digit_sum(1234) = 4 + digit_sum(123)`. When do you stop?",
        "Base case: `n < 10` returns `n` itself (this also covers `n = 0`). Otherwise return `n % 10 + digit_sum(n / 10)`.",
    ],
    explanation=r"""
## Intuition

Decimal notation is itself recursive: `1234` is `123` followed by the digit `4`, and
`123 · 10 + 4 = 1234`. Two arithmetic operations peel that structure apart:

- `n % 10` is the **last digit** (the remainder after dividing by 10);
- `n / 10` with integer division **drops the last digit**.

So the digit sum of `n` is `last digit + digit sum of the rest`, a problem of the same
shape on a number with one fewer digit. That shrinking is what guarantees termination.

## Approach

1. **Base case:** if `n < 10`, it is a single digit; return `n`.
2. **Recursive case:** return `n % 10 + digit_sum(n / 10)`.

Trace for `digit_sum(1234)`; frames are pushed top to bottom and return bottom to top:

```text
digit_sum(1234) = 4 + digit_sum(123)        → 4 + 6 = 10
  digit_sum(123) = 3 + digit_sum(12)        → 3 + 3 = 6
    digit_sum(12) = 2 + digit_sum(1)        → 2 + 1 = 3
      digit_sum(1) = 1   (base case)
```

**Language mechanics.** In Python, `//` is integer (floor) division and `/` produces a
float, so `n // 10` is the right operator. In C, C++, Rust and ESPresso, dividing two
integers with `/` already truncates toward zero. ESPresso has no `%` operator, so the last
digit is `n - (n / 10) * 10`, which is exactly what `%` computes for non-negative `n`.

The `return` statement does two jobs: it ends the current frame *and* hands its value
to the expression that was waiting in the caller (`4 + ?` above). Nothing is added until
the base case returns and the frames unwind.

## Complexity

- **Time:** O(d) where d = number of digits = ⌊log₁₀ n⌋ + 1, at most 8 here.
- **Space:** O(d) stack frames. Tiny, but an iterative loop would use O(1).

## Common mistakes

- **Base case `n == 0` only:** works, but makes one extra call per number. `n < 10` is
  cleaner. Forgetting the base case entirely recurses forever on 0, since `0 / 10 = 0`.
- **Float division in Python:** `n / 10` gives `123.4`, and the recursion never reaches an
  integer base case. Use `//`.
- **Negative inputs:** in C, `-7 % 10` is `-7`, but in Python `-7 % 10` is `3`. The problem
  says `n ≥ 0`; if you ever generalise, take the absolute value first.
- **String conversion:** `sum(map(int, str(n)))` works in Python but skips the point of the
  exercise and allocates a string.

## Going further

- **Digital root:** repeat the digit sum until one digit remains (`38 → 11 → 2`). There is
  a closed form: `1 + (n − 1) % 9` for `n > 0`, because a number is congruent to its digit
  sum modulo 9. That fact is also the classic "casting out nines" checksum.
- The same peel-a-digit recursion converts a number to any base, reverses digits, or
  checks whether a number is a palindrome without strings.
""",
    solution=r'''def digit_sum(n):
    # Base case: a single digit is its own digit sum. This also covers n == 0,
    # and it guarantees termination because every call strips one digit.
    if n < 10:
        return n
    # n % 10 is the last digit; n // 10 (integer division) is "n without its last digit".
    # The recursive call trusts that the smaller problem is solved correctly.
    return n % 10 + digit_sum(n // 10)
''',
    refs={
        "c": r"""// Integer division in C truncates, so n / 10 drops the last digit.
long long digit_sum(long long n) {
    if (n < 10) return n;                 // single digit: base case
    return n % 10 + digit_sum(n / 10);    // last digit + digit sum of the rest
}
""",
        "cpp": r"""long long digitSum(long long n) {
    // Base case first, then one smaller recursive call. Depth <= 8 for n <= 10^7.
    return n < 10 ? n : n % 10 + digitSum(n / 10);
}
""",
        "rust": r"""pub fn digit_sum(n: i64) -> i64 {
    if n < 10 {
        n // base case: a single digit (an `if` is an expression, so this is the value)
    } else {
        n % 10 + digit_sum(n / 10)
    }
}
""",
        "espresso": r"""fn digitSum(n) {
  if n < 10 {
    return n
  }
  // No % in ESPresso: the last digit is n minus the largest multiple of 10 <= n.
  const last = n - (n / 10) * 10
  return last + digitSum(n / 10)
}
""",
    },
    tests=[[1234], [7], [0], [10], [99999], [10000000], [9999999], [9090909]]
    + [[_rng.randint(0, 10**7)] for _ in range(4)],
))

# ---------------------------------------------------------------- 4. hanoi
PROBLEMS.append(dict(
    id="towers-of-hanoi-moves",
    title="Towers of Hanoi",
    difficulty=2,
    tags=["recursion", "divide and conquer"],
    fn="hanoi_moves",
    params=[["n", "int"]],
    returns="int[][]",
    statement=r"""
Three pegs are numbered **1**, **2** and **3**. Peg 1 holds `n` disks of distinct sizes,
stacked largest at the bottom to smallest at the top. Move the whole tower to **peg 3**
obeying the rules:

- move one disk at a time (the top disk of some peg);
- never place a larger disk on top of a smaller one.

Return the **shortest** sequence of moves as a list of `[from, to]` pairs. The shortest
sequence has exactly `2ⁿ − 1` moves and is unique, so there is only one correct answer.
For `n = 0` return an empty list.
""",
    constraints=["0 ≤ n ≤ 10"],
    example_notes=[
        "Small disk to peg 2, big disk to peg 3, small disk on top of it.",
        "One disk goes straight across.",
    ],
    examples=2,
    hints=[
        "Focus on the largest disk. Before it can move from peg 1 to peg 3, where must all the other `n − 1` disks be?",
        "To move `n` disks from A to C: move `n − 1` disks from A to B (using C as spare), move the biggest disk A → C, then move the `n − 1` disks from B to C (using A as spare).",
        "Write a helper `solve(k, src, dst, spare, moves)`. Base case `k == 0` does nothing. Otherwise `solve(k-1, src, spare, dst)`, append `[src, dst]`, `solve(k-1, spare, dst, src)`.",
    ],
    explanation=r"""
## Intuition

Trying to plan the moves forward is hopeless; thinking recursively makes it almost
trivial. Look only at the **largest disk**. It can move from peg 1 to peg 3 only when
peg 3 is empty and nothing is on top of it, so at that moment all other `n − 1` disks
must be stacked on peg 2. Hence every solution has the shape:

1. move the top `n − 1` disks from 1 to 2 (a smaller Hanoi problem, with 3 as spare);
2. move the largest disk from 1 to 3;
3. move the `n − 1` disks from 2 to 3 (again smaller, with 1 as spare).

The largest disk never gets in the way of the smaller disks, since anything may sit on
it, so the two subproblems really are independent `n − 1` disk puzzles. Trust them to the
recursion: that is the leap of faith.

## Approach

```python
def solve(k, src, dst, spare):
    if k == 0: return
    solve(k - 1, src, spare, dst)
    moves.append([src, dst])
    solve(k - 1, spare, dst, src)
```

Note how the **roles of the pegs rotate** in the recursive calls: the destination of the
outer call is the spare of the first inner call.

Trace for `n = 2` (call `solve(2, 1, 3, 2)`):

```text
solve(2, 1→3, spare 2)
├─ solve(1, 1→2, spare 3)
│  ├─ solve(0, …)            (nothing)
│  ├─ move [1, 2]            small disk to the middle
│  └─ solve(0, …)
├─ move [1, 3]               big disk to the target
└─ solve(1, 2→3, spare 1)
   └─ move [2, 3]            small disk on top
```

Result: `[[1,2],[1,3],[2,3]]`.

**Why it's optimal (and unique):** let M(n) be the minimum. The largest disk must move at
least once, and before its first move the other n − 1 disks must all be cleared onto the
spare peg (≥ M(n−1) moves); after its last move they must all be brought on top of it
(≥ M(n−1) moves). So M(n) ≥ 2M(n−1) + 1, which our algorithm achieves, giving
M(n) = 2ⁿ − 1. Induction on the same argument shows the optimal sequence is forced.

## Complexity

- **Time:** T(n) = 2T(n−1) + O(1) = **O(2ⁿ)**, which is optimal since the output itself
  has 2ⁿ − 1 moves.
- **Space:** O(n) recursion depth, plus the O(2ⁿ) output.

## Common mistakes

- **Mixing up the peg roles** in the two recursive calls. Write the signature as
  `(k, src, dst, spare)` and double-check: first call is `(src → spare)`, second is
  `(spare → dst)`.
- **Using `n == 1` as the only base case**: then `n = 0` recurses forever (or to −1, −2, …).
  Base case `k == 0` handles every input.
- **C memory:** return `2ⁿ − 1` separately malloc-ed rows of length 2, and fill
  `*returnColumnSizes` with 2s. With `n = 0`, return a valid pointer and `*returnSize = 0`.

## Going further

- Return only the **count** and you get M(n) = 2ⁿ − 1 without recursion.
- An **iterative** solution exists: on odd moves, move the smallest disk cyclically
  (1→3→2→1 for even n, 1→2→3→1 for odd n); on even moves, make the only legal move not
  involving the smallest disk.
- The k-th move can be computed directly from the binary representation of k: the disk
  moved is the number of trailing zeros of k, plus 1.
""",
    solution=r'''def hanoi_moves(n):
    moves = []

    def solve(k, src, dst, spare):
        # Base case: moving zero disks takes zero moves. Using 0 (not 1) as the base
        # case means n = 0 needs no special handling.
        if k == 0:
            return
        # 1. Park the k-1 smaller disks on the spare peg. For this subproblem the
        #    original destination is the free peg.
        solve(k - 1, src, spare, dst)
        # 2. The largest of the k disks is now alone and the destination is empty
        #    (or holds only larger disks): move it.
        moves.append([src, dst])
        # 3. Bring the k-1 disks from the spare onto it; now src is the free peg.
        solve(k - 1, spare, dst, src)

    solve(n, 1, 3, 2)
    return moves
''',
    refs={
        "c": r"""// Append the moves for k disks src -> dst (via spare) into out[*count ...].
static void solve(int k, long long src, long long dst, long long spare, long long** out, int* count) {
    if (k == 0) return;                                  // nothing to move
    solve(k - 1, src, spare, dst, out, count);           // clear the smaller disks away
    long long* mv = malloc(2 * sizeof(long long));       // each row is its own allocation
    mv[0] = src;
    mv[1] = dst;
    out[(*count)++] = mv;                                // move the largest disk
    solve(k - 1, spare, dst, src, out, count);           // stack the smaller disks back on
}

long long** hanoi_moves(long long n, int* returnSize, int** returnColumnSizes) {
    int total = (1 << n) - 1;                            // exactly 2^n - 1 moves
    // +1 so malloc never gets 0 bytes when n == 0 (malloc(0) may return NULL).
    long long** out = malloc(sizeof(long long*) * (total + 1));
    *returnColumnSizes = malloc(sizeof(int) * (total + 1));
    for (int i = 0; i < total; i++) (*returnColumnSizes)[i] = 2;   // every row is [from, to]
    int count = 0;
    solve((int)n, 1, 3, 2, out, &count);
    *returnSize = count;
    return out;
}
""",
        "cpp": r"""// Recursive helper; `moves` is passed by reference so all frames append to one vector.
static void solve(int k, long long src, long long dst, long long spare,
                  vector<vector<long long>>& moves) {
    if (k == 0) return;
    solve(k - 1, src, spare, dst, moves);   // n-1 disks out of the way
    moves.push_back({src, dst});            // largest disk
    solve(k - 1, spare, dst, src, moves);   // n-1 disks back on top
}

vector<vector<long long>> hanoiMoves(long long n) {
    vector<vector<long long>> moves;
    moves.reserve((1u << n) - 1);           // we know the exact size: 2^n - 1
    solve((int)n, 1, 3, 2, moves);
    return moves;
}
""",
        "rust": r"""pub fn hanoi_moves(n: i64) -> Vec<Vec<i64>> {
    // A nested fn can't capture locals, so the output vector is passed as &mut.
    fn solve(k: i64, src: i64, dst: i64, spare: i64, out: &mut Vec<Vec<i64>>) {
        if k == 0 {
            return;
        }
        solve(k - 1, src, spare, dst, out); // park k-1 disks on the spare
        out.push(vec![src, dst]);           // move the largest disk
        solve(k - 1, spare, dst, src, out); // bring the k-1 disks over
    }
    let mut out = Vec::with_capacity((1usize << n) - 1);
    solve(n, 1, 3, 2, &mut out);
    out
}
""",
    },
    tests=[[2], [1], [0], [3], [4], [5], [10]],
))

# ---------------------------------------------------------------- 5. subsets
PROBLEMS.append(dict(
    id="all-subsets-power-set",
    title="Subsets (Power Set)",
    difficulty=2,
    tags=["backtracking", "recursion"],
    fn="subsets",
    params=[["nums", "int[]"]],
    returns="int[][]",
    compare="unordered_deep",
    statement=r"""
Given an array of **distinct** integers `nums`, return **every subset** of it (the power
set), including the empty subset and `nums` itself.

Each subset must appear exactly once. Order does not matter: neither the order of the
subsets in the result nor the order of numbers inside a subset.
""",
    constraints=["0 ≤ len(nums) ≤ 10", "−10 ≤ nums[i] ≤ 10", "all values in `nums` are distinct"],
    example_notes=[
        "3 elements, so 2³ = 8 subsets.",
        "The empty array has exactly one subset: the empty one.",
    ],
    hints=[
        "For each element you make one yes/no decision: is it in the subset or not? How many leaves does that decision tree have?",
        "Recurse on the index `i`: either skip `nums[i]` or include it, then move on to `i + 1`. When `i == len(nums)` you have one complete subset.",
        "Keep one shared `path` list. Append `nums[i]`, recurse, then pop it (un-choose) and recurse again without it. Append a **copy** of `path` at the leaves.",
    ],
    explanation=r"""
## Intuition

"Return all subsets" means enumerating a space of size 2ⁿ, with n ≤ 10 (1024 subsets),
so no cleverness is needed in *what* we produce, only a systematic way to produce each one
exactly once. Every subset corresponds to one sequence of n independent yes/no decisions
("is `nums[0]` in? is `nums[1]` in? …"). A sequence of decisions is a path in a binary
**decision tree**, and walking a decision tree depth-first is backtracking.

## Approach

**Include / exclude recursion** on index `i` with a shared `path`:

1. If `i == len(nums)`: record a copy of `path` (a leaf) and return.
2. **Choose:** append `nums[i]`; **explore:** recurse with `i + 1`; **un-choose:** pop.
3. Explore again with `i + 1` without `nums[i]`.

Trace on `[1, 2]`:

```text
go(0, [])
├─ take 1 → go(1, [1])
│   ├─ take 2 → go(2, [1,2])   record [1,2]
│   └─ skip 2 → go(2, [1])     record [1]
└─ skip 1 → go(1, [])
    ├─ take 2 → go(2, [2])     record [2]
    └─ skip 2 → go(2, [])      record []
```

**Alternative formulation (the "for-loop" template):** every node of the tree is itself a
subset. At each call record `path`, then for each `j ≥ start` append `nums[j]`, recurse with
`start = j + 1`, pop. Using `start` ensures elements are only added in index order, so
`[1,2]` and `[2,1]` cannot both be generated. This form generalises directly to
combinations (stop at size k) and combination sum.

**Iterative alternative:** start with `[[]]`; for each number, append a copy of every
existing subset with that number added. Or loop a bitmask `m` from 0 to 2ⁿ − 1 and include
`nums[j]` when bit `j` is set.

## Complexity

- **Time:** O(n · 2ⁿ): 2ⁿ leaves, and copying each subset costs up to n.
- **Space:** O(n) recursion depth and path, plus the O(n · 2ⁿ) output.

## Common mistakes

- **Appending `path` instead of a copy.** In Python, `res.append(path)` stores a
  reference to the same list that you keep mutating; at the end every entry is `[]`. Use
  `path[:]` / `list(path)`. In C++ `res.push_back(path)` copies (value semantics), and in
  Rust `path.clone()` is required anyway, since `path` is still borrowed.
- **Forgetting to pop** after the "take" branch: the "skip" branch then still contains the
  element, producing duplicates and missing subsets.
- **Missing the empty subset**, or returning `[]` instead of `[[]]` for empty input.

## Going further

- **Subsets II** (input with duplicates): sort first, and in the for-loop template skip
  `nums[j]` when `j > start` and `nums[j] == nums[j-1]`.
- **Gray code** order lists subsets so consecutive ones differ by a single element.
- Counting subsets with a property (sum = target, etc.) is the gateway to DP over subsets
  and meet-in-the-middle for n ≈ 40.
""",
    solution=r'''def subsets(nums):
    res = []
    path = []          # the subset currently being built; shared by all frames

    def go(i):
        # Leaf: we have decided in/out for every element, so path is one subset.
        if i == len(nums):
            res.append(path[:])      # COPY: path will keep changing after this
            return
        # Branch 1: include nums[i]   (choose -> explore -> un-choose)
        path.append(nums[i])
        go(i + 1)
        path.pop()                   # restore path exactly as our caller left it
        # Branch 2: exclude nums[i]
        go(i + 1)

    go(0)
    return res
''',
    refs={
        "cpp": r"""// Include/exclude backtracking. `path` and `res` are shared via references.
static void go(const vector<long long>& nums, size_t i, vector<long long>& path,
               vector<vector<long long>>& res) {
    if (i == nums.size()) { res.push_back(path); return; }   // push_back copies path
    path.push_back(nums[i]);       // choose
    go(nums, i + 1, path, res);    // explore with nums[i]
    path.pop_back();               // un-choose
    go(nums, i + 1, path, res);    // explore without nums[i]
}

vector<vector<long long>> subsets(vector<long long>& nums) {
    vector<vector<long long>> res;
    vector<long long> path;
    go(nums, 0, path, res);
    return res;
}
""",
        "rust": r"""pub fn subsets(nums: Vec<i64>) -> Vec<Vec<i64>> {
    // `nums` is read-only (&[i64]); `path` and `res` are mutably borrowed by each call
    // in turn. The borrow checker is happy because no two calls run at the same time.
    fn go(nums: &[i64], i: usize, path: &mut Vec<i64>, res: &mut Vec<Vec<i64>>) {
        if i == nums.len() {
            res.push(path.clone()); // clone: res must own its own copy
            return;
        }
        path.push(nums[i]);      // choose
        go(nums, i + 1, path, res);
        path.pop();              // un-choose
        go(nums, i + 1, path, res);
    }
    let mut res = Vec::with_capacity(1 << nums.len());
    go(&nums, 0, &mut Vec::new(), &mut res);
    res
}
""",
    },
    tests=[[[1, 2, 3]], [[]], [[0]], [[5, -1]], [[4, 1, 7, 2]],
           [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]], [[-10, 10, 0, 3, -3]]],
))

# ---------------------------------------------------------------- 6. permutations
PROBLEMS.append(dict(
    id="all-permutations-distinct",
    title="Permutations",
    difficulty=2,
    tags=["backtracking", "recursion"],
    fn="permute",
    params=[["nums", "int[]"]],
    returns="int[][]",
    compare="unordered",
    statement=r"""
Given an array `nums` of **distinct** integers, return **all possible orderings**
(permutations) of its elements.

The permutations may be listed in any order, but each permutation is an ordered list and
must appear exactly once.
""",
    constraints=["1 ≤ len(nums) ≤ 6", "−10 ≤ nums[i] ≤ 10", "all values are distinct"],
    example_notes=["3! = 6 orderings.", "A single element has exactly one ordering."],
    hints=[
        "Fill the positions left to right. How many choices are there for position 0? For position 1, once position 0 is fixed?",
        "Recurse on the current position; try every element that hasn't been used yet. Track usage with a boolean array `used`.",
        "Choose: mark `used[j] = True` and append `nums[j]`. Explore. Un-choose: pop and set `used[j] = False`. Record a copy of `path` when its length is n.",
    ],
    explanation=r"""
## Intuition

A permutation is built one position at a time: n choices for the first slot, n − 1 for
the second, …, 1 for the last, giving n! leaves. Unlike subsets (where position in the
array decides the order), here *any* unused element can go next, so we need to remember
**which elements are already used**. That piece of state, together with the partial
path, is exactly what backtracking maintains and restores.

## Approach

State: `path` (the prefix built so far) and `used[j]` (is `nums[j]` in the prefix?).

1. If `len(path) == n`: record a copy.
2. For each `j` with `not used[j]`: choose (`used[j] = True`, append), explore, un-choose
   (pop, `used[j] = False`).

Trace on `[1, 2, 3]` (first two branches):

```text
[]
├─ 1 → [1]
│      ├─ 2 → [1,2] ─ 3 → [1,2,3] ✓
│      └─ 3 → [1,3] ─ 2 → [1,3,2] ✓
├─ 2 → [2]
│      ├─ 1 → [2,1] ─ 3 → [2,1,3] ✓
│      └─ 3 → [2,3] ─ 1 → [2,3,1] ✓
└─ 3 → …  [3,1,2] ✓  [3,2,1] ✓
```

**Swap-based alternative:** recurse on position `k`; for each `j ≥ k`, swap `nums[k]` and
`nums[j]`, recurse on `k + 1`, then swap back. The array itself is the path, and the
prefix `nums[0..k)` is fixed while the suffix holds the unused elements, so no `used`
array is needed. The un-choose step is the second swap.

## Complexity

- **Time:** O(n · n!): n! leaves, each copied in O(n). The internal nodes add only a
  constant factor (n!/1! + n!/2! + … < e · n!).
- **Space:** O(n) for the path, `used` and recursion depth, plus the O(n · n!) output.

n! grows brutally: 10! = 3.6 million and 13! exceeds 6 billion. Generating all
permutations is only feasible for small n, which is why the constraint is n ≤ 6 here.

## Common mistakes

- **Forgetting to reset `used[j]`** after the recursive call: later branches think the
  element is still taken and you get far fewer than n! results.
- **Recording the path by reference** (Python) instead of copying.
- **Using `x in path` to test usage**: correct for distinct values but O(n) per check, and
  wrong as soon as values can repeat. Index-based `used` is both faster and robust.
- **Swap version without swapping back:** the array no longer matches what the caller
  expects, and some permutations are duplicated or skipped.

## Going further

- **Permutations II** (duplicates allowed): sort, then skip `nums[j]` if
  `j > 0 and nums[j] == nums[j-1] and not used[j-1]`, so equal values are always used in
  left-to-right order.
- **Next permutation** produces permutations in lexicographic order iteratively in O(n)
  each; C++ has it built in as `std::next_permutation`.
- The k-th permutation can be computed directly using the factorial number system.
""",
    solution=r'''def permute(nums):
    n = len(nums)
    res = []
    path = []
    used = [False] * n      # used[j]: is nums[j] already somewhere in path?

    def go():
        # All positions filled: path is one complete permutation.
        if len(path) == n:
            res.append(path[:])          # copy, since path is reused
            return
        for j in range(n):
            if used[j]:
                continue                 # each element appears once per permutation
            # choose
            used[j] = True
            path.append(nums[j])
            # explore: fill the remaining positions
            go()
            # un-choose: restore both pieces of state for the next j
            path.pop()
            used[j] = False

    go()
    return res
''',
    refs={
        "cpp": r"""// Swap-based backtracking: positions [0, k) are fixed; [k, n) are the unused elements.
static void go(vector<long long>& a, size_t k, vector<vector<long long>>& res) {
    if (k == a.size()) { res.push_back(a); return; }
    for (size_t j = k; j < a.size(); j++) {
        swap(a[k], a[j]);      // choose a[j] for position k
        go(a, k + 1, res);     // explore the rest
        swap(a[k], a[j]);      // un-choose: restore the original order
    }
}

vector<vector<long long>> permute(vector<long long>& nums) {
    vector<vector<long long>> res;
    vector<long long> a = nums;   // work on a copy so the caller's vector is untouched
    go(a, 0, res);
    return res;
}
""",
        "rust": r"""pub fn permute(nums: Vec<i64>) -> Vec<Vec<i64>> {
    // used[j] marks which elements are already in `path`.
    fn go(nums: &[i64], used: &mut Vec<bool>, path: &mut Vec<i64>, res: &mut Vec<Vec<i64>>) {
        if path.len() == nums.len() {
            res.push(path.clone());
            return;
        }
        for j in 0..nums.len() {
            if used[j] {
                continue;
            }
            used[j] = true;          // choose
            path.push(nums[j]);
            go(nums, used, path, res); // explore
            path.pop();              // un-choose
            used[j] = false;
        }
    }
    let mut res = Vec::new();
    go(&nums, &mut vec![false; nums.len()], &mut Vec::new(), &mut res);
    res
}
""",
    },
    tests=[[[1, 2, 3]], [[7]], [[0, 1]], [[3, -2, 5, 0]], [[1, 2, 3, 4, 5]], [[6, 5, 4, 3, 2, 1]], [[-10, 10]]],
))

# ---------------------------------------------------------------- 7. combinations
PROBLEMS.append(dict(
    id="combinations-n-choose-k",
    title="Combinations",
    difficulty=2,
    tags=["backtracking", "recursion", "pruning"],
    fn="combine",
    params=[["n", "int"], ["k", "int"]],
    returns="int[][]",
    compare="unordered_deep",
    statement=r"""
Return **all ways to choose `k` distinct numbers** from the range `1 … n`.

A combination is a set: `[1, 2]` and `[2, 1]` are the same combination and must appear
only once. The combinations and the numbers inside them may be listed in any order. If
`k = 0`, the only combination is the empty one.
""",
    constraints=["1 ≤ n ≤ 12", "0 ≤ k ≤ n"],
    example_notes=["C(4, 2) = 6 pairs.", "Choosing all of them: only one way."],
    hints=[
        "To avoid generating both `[1,2]` and `[2,1]`, only ever add numbers in increasing order.",
        "Recurse with a `start` value: the next number you add must be ≥ `start`. When the path has `k` numbers, record it.",
        "Prune: if you still need `need = k - len(path)` numbers, the next number can be at most `n - need + 1`; otherwise there aren't enough numbers left to finish.",
    ],
    explanation=r"""
## Intuition

Combinations are subsets of a fixed size, so the subset decision tree works, but it
wastes time exploring subsets of the wrong size. The **for-loop backtracking template**
fits better: at each level pick the *next* element, always larger than the previous one.
Increasing order gives every set exactly one canonical spelling, which is what kills
duplicates.

## Approach

`go(start)` with a shared `path`:

1. If `len(path) == k`: record a copy, return.
2. Let `need = k - len(path)`. For `x` from `start` to `n - need + 1`: append `x`, call
   `go(x + 1)`, pop.

The upper bound `n - need + 1` is **pruning**: if we put `x` in now, the remaining
`need − 1` numbers must come from `x+1 … n`, which requires `n − x ≥ need − 1`.

Trace for `n = 4, k = 2`:

```text
go(1) path=[]           need 2 → x ∈ 1..3
├─ x=1 → go(2) [1]      need 1 → x ∈ 2..4 → [1,2] [1,3] [1,4]
├─ x=2 → go(3) [2]      need 1 → x ∈ 3..4 → [2,3] [2,4]
└─ x=3 → go(4) [3]      need 1 → x ∈ 4..4 → [3,4]
   (x=4 never tried at the top: nothing would be left to pair with it)
```

Six combinations, `C(4,2) = 6`, with no dead branches.

## Complexity

- **Time:** O(k · C(n, k)): each combination is copied in O(k), and thanks to pruning
  every internal node leads to at least one leaf, so internal nodes don't dominate.
- **Space:** O(k) recursion depth and path, plus the output.

Without the pruning bound, the tree still produces the right answer but explores many
branches that can never reach size k (e.g. starting with `x = n` when `k = 5`).

## Common mistakes

- **Restarting the loop from 1** at every level instead of from `start`: generates
  permutations, i.e. every combination k! times (plus things like `[1,1]`).
- **Recursing with `start + 1` instead of `x + 1`:** the next element must be larger than
  the one just chosen, not larger than where this loop began.
- **Off-by-one in the pruning bound:** the last valid start is `n - need + 1` *inclusive*.
  In Python that is `range(start, n - need + 2)`.
- **`k = 0`:** the answer is `[[]]` (one empty combination), not `[]`. The template handles
  it naturally since the first call immediately records the empty path.

## Going further

- **Pascal's rule** `C(n,k) = C(n−1,k−1) + C(n−1,k)` is the same recursion as "include n or
  not", and memoising its *count* gives Pascal's triangle.
- Gosper's hack enumerates all k-bit masks in increasing order with pure bit tricks.
- Combination sum (next problem) is this template with repetition allowed and a sum
  constraint for pruning.
""",
    solution=r'''def combine(n, k):
    res = []
    path = []

    def go(start):
        # Enough numbers chosen: record a copy of this combination.
        if len(path) == k:
            res.append(path[:])
            return
        need = k - len(path)
        # Numbers are added in increasing order, so each set has exactly one spelling.
        # Pruning: if we pick x now we still need (need - 1) numbers from x+1..n,
        # so x can be at most n - need + 1. range() excludes its end, hence +2.
        for x in range(start, n - need + 2):
            path.append(x)        # choose
            go(x + 1)             # explore: the next number must be larger than x
            path.pop()            # un-choose

    go(1)
    return res
''',
    refs={
        "cpp": r"""static void go(int n, int k, int start, vector<long long>& path, vector<vector<long long>>& res) {
    if ((int)path.size() == k) { res.push_back(path); return; }
    int need = k - (int)path.size();
    for (int x = start; x <= n - need + 1; x++) {   // pruned upper bound (inclusive)
        path.push_back(x);         // choose
        go(n, k, x + 1, path, res);// explore strictly larger numbers
        path.pop_back();           // un-choose
    }
}

vector<vector<long long>> combine(long long n, long long k) {
    vector<vector<long long>> res;
    vector<long long> path;
    go((int)n, (int)k, 1, path, res);
    return res;
}
""",
        "rust": r"""pub fn combine(n: i64, k: i64) -> Vec<Vec<i64>> {
    fn go(n: i64, k: usize, start: i64, path: &mut Vec<i64>, res: &mut Vec<Vec<i64>>) {
        if path.len() == k {
            res.push(path.clone());
            return;
        }
        let need = (k - path.len()) as i64;
        // `..=` is an inclusive range: x runs up to n - need + 1.
        for x in start..=n - need + 1 {
            path.push(x);
            go(n, k, x + 1, path, res);
            path.pop();
        }
    }
    let mut res = Vec::new();
    go(n, k as usize, 1, &mut Vec::new(), &mut res);
    res
}
""",
    },
    tests=[[4, 2], [1, 1], [5, 5], [5, 0], [10, 3], [12, 6], [6, 1], [7, 4]],
))

# ---------------------------------------------------------------- 8. combination sum
PROBLEMS.append(dict(
    id="combination-sum-reuse",
    title="Combination Sum",
    difficulty=2,
    tags=["backtracking", "recursion", "pruning"],
    fn="combination_sum",
    params=[["candidates", "int[]"], ["target", "int"]],
    returns="int[][]",
    compare="unordered_deep",
    statement=r"""
Given an array of **distinct positive** integers `candidates` and a positive `target`,
return every **combination** of candidates whose sum equals `target`. Each candidate may
be used **any number of times**.

Two combinations are the same if they use each number the same number of times, so
`[2,2,3]` and `[3,2,2]` count once. Combinations (and the numbers inside each) may be in
any order. If no combination works, return an empty list.
""",
    constraints=["1 ≤ len(candidates) ≤ 30", "1 ≤ candidates[i] ≤ 40, all distinct", "1 ≤ target ≤ 40"],
    example_notes=["`2+2+3 = 7` and `7 = 7`.", "`2+2+2+2`, `2+3+3` and `3+5` all make 8."],
    hints=[
        "This is the combinations template, except that after choosing `candidates[i]` you may choose it again.",
        "Recurse with `(start, remaining)`. Loop `i` from `start`; after choosing `candidates[i]`, recurse with `start = i` (not `i + 1`) so it can be reused, and never look back at smaller indices.",
        "Sort the candidates first. Then as soon as `candidates[i] > remaining`, every later candidate is too big as well: `break` out of the loop.",
    ],
    explanation=r"""
## Intuition

"Find every combination meeting a constraint" means backtracking. Two details are new
compared with plain combinations:

1. **Reuse.** After picking a number we may pick it again, so the recursive call keeps
   the same `start` index instead of advancing past it.
2. **Uniqueness.** Restricting each level to indices `≥ start` means numbers are always
   taken in non-decreasing index order, so `[2,2,3]` can be built but `[3,2,2]` cannot.

The running sum gives us a natural **pruning** rule: once the remainder is negative the
branch is dead, and with sorted candidates we can stop even earlier.

## Approach

Sort `candidates`. Then `go(start, remaining)`:

1. If `remaining == 0`: record a copy of `path`.
2. For `i` from `start`: if `candidates[i] > remaining`, **break** (sorted, so all later
   ones are too large). Otherwise choose it, call `go(i, remaining - candidates[i])`, pop.

Trace for `[2, 3, 6, 7]`, target 7 (sorted already):

```text
go(0, 7) []
├─ 2 → go(0, 5) [2]
│   ├─ 2 → go(0, 3) [2,2]
│   │   ├─ 2 → go(0, 1) [2,2,2]   2 > 1: break (dead end)
│   │   └─ 3 → go(1, 0) [2,2,3]   ✓ record
│   ├─ 3 → go(1, 2) [2,3]         3 > 2: break
│   └─ 6 > 5: break
├─ 3 → go(1, 4) [3]
│   ├─ 3 → go(1, 1) [3,3]         3 > 1: break
│   └─ 6 > 4: break
├─ 6 → go(2, 1) [6]               6 > 1: break
└─ 7 → go(3, 0) [7]               ✓ record
```

## Complexity

Exponential in general. With T = target and m = smallest candidate, the tree depth is at
most T/m, and each level branches up to n ways, so a loose bound is O(n^(T/m) · T/m).
In practice pruning and the small target keep it fast. Space is O(T/m) for the recursion
and path, plus the output.

## Common mistakes

- **Recursing with `i + 1`** prevents reuse: you would miss `[2,2,3]`.
- **Recursing with `0` (restarting the loop)**: produces every ordering of each combination
  (`[2,2,3]`, `[2,3,2]`, `[3,2,2]`).
- **`return` instead of `break`/`continue` without sorting:** with unsorted candidates a
  too-large value doesn't mean later values are too large too. Either sort and `break`, or
  don't sort and `continue`.
- **Copying:** record `path[:]` in Python, not `path`.

## Going further

- **Combination Sum II**: each candidate used at most once and the input may contain
  duplicates. Recurse with `i + 1`, and skip `candidates[i] == candidates[i-1]` when
  `i > start`.
- **Counting** combinations instead of listing them is the classic "coin change ways" DP:
  `ways[s] += ways[s - c]` looping coins in the outer loop, which yields O(n · T).
""",
    solution=r'''def combination_sum(candidates, target):
    cands = sorted(candidates)   # sorted, so we can stop at the first value that is too big
    res = []
    path = []

    def go(start, remaining):
        if remaining == 0:
            res.append(path[:])          # path sums exactly to target
            return
        # Only indices >= start: numbers are taken in non-decreasing order, so each
        # multiset is generated exactly once.
        for i in range(start, len(cands)):
            c = cands[i]
            if c > remaining:
                break                    # every later candidate is even larger: prune
            path.append(c)               # choose
            go(i, remaining - c)         # explore; i (not i+1) because c may be reused
            path.pop()                   # un-choose

    go(0, target)
    return res
''',
    refs={
        "cpp": r"""static void go(const vector<long long>& c, size_t start, long long remaining,
               vector<long long>& path, vector<vector<long long>>& res) {
    if (remaining == 0) { res.push_back(path); return; }
    for (size_t i = start; i < c.size() && c[i] <= remaining; i++) {  // sorted: stop early
        path.push_back(c[i]);
        go(c, i, remaining - c[i], path, res);   // same i: reuse allowed
        path.pop_back();
    }
}

vector<vector<long long>> combinationSum(vector<long long>& candidates, long long target) {
    vector<long long> c = candidates;
    sort(c.begin(), c.end());
    vector<vector<long long>> res;
    vector<long long> path;
    go(c, 0, target, path, res);
    return res;
}
""",
        "rust": r"""pub fn combination_sum(mut candidates: Vec<i64>, target: i64) -> Vec<Vec<i64>> {
    // We own `candidates`, so we may sort it in place (the binding just needs `mut`).
    candidates.sort_unstable();
    fn go(c: &[i64], start: usize, remaining: i64, path: &mut Vec<i64>, res: &mut Vec<Vec<i64>>) {
        if remaining == 0 {
            res.push(path.clone());
            return;
        }
        for i in start..c.len() {
            if c[i] > remaining {
                break; // sorted: nothing later can fit either
            }
            path.push(c[i]);
            go(c, i, remaining - c[i], path, res); // reuse c[i]
            path.pop();
        }
    }
    let mut res = Vec::new();
    go(&candidates, 0, target, &mut Vec::new(), &mut res);
    res
}
""",
    },
    tests=[[[2, 3, 6, 7], 7], [[2, 3, 5], 8], [[2], 1], [[1], 1], [[7, 3, 2], 18],
           [[8, 7, 4, 3], 11], [[2, 4, 6], 9], [[1, 2], 4], [[40, 1, 39], 40]],
))

# ---------------------------------------------------------------- 9. letter combinations
PROBLEMS.append(dict(
    id="phone-letter-combinations",
    title="Letter Combinations of a Phone Number",
    difficulty=2,
    tags=["backtracking", "recursion", "string"],
    fn="letter_combinations",
    params=[["digits", "str"]],
    returns="str[]",
    compare="unordered",
    statement=r"""
On an old phone keypad each digit from 2 to 9 maps to some letters:

```text
2: abc   3: def   4: ghi   5: jkl
6: mno   7: pqrs  8: tuv   9: wxyz
```

Given a string `digits` containing only `2`–`9`, return **every string of letters** that
the digits could spell (one letter per digit, in order). Return them in any order. If
`digits` is empty, return an **empty list**.
""",
    constraints=["0 ≤ len(digits) ≤ 5", "each character is in `'2'..'9'`"],
    example_notes=["3 letters × 3 letters = 9 strings.", "No digits, no strings (not even the empty string)."],
    hints=[
        "Each position in the output string is an independent choice among 3 or 4 letters.",
        "Recurse on the index `i` into `digits`: for each letter of `digits[i]`, append it to the current prefix and recurse on `i + 1`.",
        "When `i == len(digits)`, record the prefix. Handle empty input separately so you don't return `[\"\"]`.",
    ],
    explanation=r"""
## Intuition

This is a **Cartesian product**: position 0 picks one letter from the first digit's
letters, position 1 one from the second's, and so on. A product of unknown length can't be
written as a fixed number of nested loops, but recursion is exactly "a loop nested as
deep as the input is long": each call is one more loop level.

## Approach

`go(i, prefix)`:

1. If `i == len(digits)`: record `prefix`.
2. Otherwise for each letter `ch` in `KEYS[digits[i]]`: `go(i + 1, prefix + ch)`.

Trace for `"23"`:

```text
go(0, "")
├─ a → go(1, "a")  → "ad" "ae" "af"
├─ b → go(1, "b")  → "bd" "be" "bf"
└─ c → go(1, "c")  → "cd" "ce" "cf"
```

**Passing `prefix + ch`** builds a new string for each call, so there is no explicit
un-choose step: each frame owns its own immutable prefix. The alternative is one shared
character buffer: write `buf[i] = ch`, recurse, and let the next iteration overwrite it.
Overwriting a fixed slot *is* the un-choose, which is why it is the efficient version in
C/C++.

An **iterative** version works too: start with `[""]`, and for each digit replace the list
with every existing string extended by every letter of that digit.

## Complexity

- **Time:** O(4ⁿ · n): up to 4ⁿ outputs, each of length n. (Building `prefix + ch` costs
  O(n) per call, still within this bound.)
- **Space:** O(n) recursion depth, plus the output.

## Common mistakes

- **Empty input:** the natural recursion records the empty prefix and returns `[""]`.
  The spec says `[]`; check for it up front.
- **Wrong keypad table:** 7 and 9 have **four** letters (`pqrs`, `wxyz`). Indexing with
  `digit - '2'` into an 8-entry array is the cleanest mapping.
- **Mutating a shared string in Python:** Python strings are immutable, so `prefix + ch`
  is a new object. In C++, if you pass `string&` and `push_back`, remember to `pop_back`.

## Going further

- Real T9 input reverses this: given a dictionary, find the words matching a digit
  sequence. Build a trie of the dictionary and walk it in parallel with the digit choices,
  pruning branches no word continues.
- `itertools.product(*(KEYS[d] for d in digits))` is the one-line Python version.
""",
    solution=r'''KEYS = {
    "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
    "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz",
}


def letter_combinations(digits):
    # Spec: no digits means no combinations (not one empty combination).
    if not digits:
        return []
    res = []

    def go(i, prefix):
        # Every digit has contributed a letter: prefix is complete.
        if i == len(digits):
            res.append(prefix)
            return
        # One loop level per digit. prefix + ch is a new string, so each frame keeps
        # its own prefix and there's nothing to undo afterwards.
        for ch in KEYS[digits[i]]:
            go(i + 1, prefix + ch)

    go(0, "")
    return res
''',
    refs={
        "c": r"""static const char* KEYS[] = {"abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"};

// buf[0..i) is the current prefix. Writing buf[i] in the loop overwrites the previous
// choice, which is the "un-choose" step for free.
static void go(const char* digits, int n, int i, char* buf, char** res, int* count) {
    if (i == n) {
        res[*count] = malloc(n + 1);
        memcpy(res[*count], buf, n);
        res[*count][n] = '\0';
        (*count)++;
        return;
    }
    for (const char* p = KEYS[digits[i] - '2']; *p; p++) {
        buf[i] = *p;                          // choose
        go(digits, n, i + 1, buf, res, count);// explore
    }
}

char** letter_combinations(char* digits, int* returnSize) {
    int n = strlen(digits);
    *returnSize = 0;
    if (n == 0) return malloc(sizeof(char*));          // empty list
    int total = 1;
    for (int i = 0; i < n; i++) total *= strlen(KEYS[digits[i] - '2']);
    char** res = malloc(sizeof(char*) * total);
    char buf[8];
    go(digits, n, 0, buf, res, returnSize);
    return res;
}
""",
        "cpp": r"""static const string KEYS[] = {"abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"};

static void go(const string& digits, size_t i, string& cur, vector<string>& res) {
    if (i == digits.size()) { res.push_back(cur); return; }
    for (char ch : KEYS[digits[i] - '2']) {
        cur.push_back(ch);          // choose
        go(digits, i + 1, cur, res);
        cur.pop_back();             // un-choose: cur is shared, so restore it
    }
}

vector<string> letterCombinations(string digits) {
    vector<string> res;
    if (digits.empty()) return res;
    string cur;
    go(digits, 0, cur, res);
    return res;
}
""",
        "rust": r"""const KEYS: [&str; 8] = ["abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"];

pub fn letter_combinations(digits: String) -> Vec<String> {
    fn go(d: &[u8], i: usize, cur: &mut String, res: &mut Vec<String>) {
        if i == d.len() {
            res.push(cur.clone());
            return;
        }
        for ch in KEYS[(d[i] - b'2') as usize].chars() {
            cur.push(ch);        // choose
            go(d, i + 1, cur, res);
            cur.pop();           // un-choose
        }
    }
    let mut res = Vec::new();
    if digits.is_empty() {
        return res;
    }
    // Work on bytes: the input is ASCII digits, so indexing bytes is safe and cheap.
    go(digits.as_bytes(), 0, &mut String::new(), &mut res);
    res
}
""",
    },
    tests=[["23"], [""], ["2"], ["79"], ["234"], ["9999"], ["27358"]],
))

# ---------------------------------------------------------------- 10. generate parentheses
PROBLEMS.append(dict(
    id="generate-balanced-parentheses",
    title="Generate Parentheses",
    difficulty=2,
    tags=["backtracking", "recursion", "string"],
    fn="generate_parenthesis",
    params=[["n", "int"]],
    returns="str[]",
    statement=r"""
Return **every well-formed string** made of `n` pairs of parentheses. A string is
well-formed when every `(` is closed by a later matching `)`, and no `)` appears without an
open partner before it.

Return the strings in **lexicographically sorted order** (by character code, `(` sorts
before `)`).
""",
    constraints=["1 ≤ n ≤ 8"],
    example_notes=["The five balanced strings of three pairs, sorted.", "One pair: only `()`."],
    hints=[
        "Generating all 2²ⁿ strings and filtering works but wastes time. Can you avoid ever building an invalid prefix?",
        "Track how many `(` and `)` you've placed. When is adding `(` legal? When is adding `)` legal?",
        "Add `(` if `open < n`; add `)` if `close < open`. Record when the length is `2n`. Trying `(` before `)` makes the output come out already sorted.",
    ],
    explanation=r"""
## Intuition

A prefix of parentheses can still be completed to a balanced string exactly when

1. it uses at most `n` opening brackets, and
2. at every point, the number of `)` never exceeds the number of `(`.

Both conditions can be checked *while building*, so instead of generating all 2²ⁿ
strings and filtering, we only ever extend a prefix in valid ways. This is backtracking
where the pruning is so complete that **every branch ends in a valid answer**.

## Approach

`go(prefix, open, close)`:

1. If `len(prefix) == 2n`: record it.
2. If `open < n`: try `go(prefix + "(", open + 1, close)`.
3. If `close < open`: try `go(prefix + ")", open, close + 1)`.

Because `(` (code 40) sorts before `)` (code 41) and we always try `(` first, the leaves
are visited in lexicographic order: the output is sorted with no extra work.

Trace for `n = 2` (o = open, c = close):

```text
""        o0 c0
└─ "("    o1 c0
   ├─ "(("   o2 c0   (can't open more)
   │  └─ "(()"  o2 c1
   │     └─ "(())" ✓
   └─ "()"   o1 c1   (close == open, can't close)
      └─ "()("  o2 c1
         └─ "()()" ✓
```

## Complexity

The number of results is the n-th **Catalan number** Cₙ = C(2n, n) / (n + 1) ≈
4ⁿ / (n^1.5 · √π): 1, 2, 5, 14, 42, 132, 429, 1430 for n = 1..8. Since no branch dies,
the tree has O(n · Cₙ) nodes, and each output costs O(n) to build.

- **Time:** O(n · Cₙ) ≈ O(4ⁿ / √n).
- **Space:** O(n) recursion depth plus the output.

## Common mistakes

- **Condition `close < n`** instead of `close < open`: allows `)(` and other invalid
  prefixes.
- **Trying `)` before `(`**: the set is right but the order is reversed; this problem
  demands sorted output.
- **Shared buffer without undo (C++):** if you `push_back` into one `string&`, you must
  `pop_back` after each recursive call.
- **Sorting at the end** is correct but unnecessary once you see why the generation order
  is already sorted.

## Going further

- **Counting** only: Catalan numbers satisfy C₀ = 1, Cₙ₊₁ = Σ CᵢCₙ₋ᵢ, which you can memoise.
  They also count binary trees with n nodes, triangulations of polygons, and monotone
  lattice paths below the diagonal.
- **Valid parentheses checking** (a stack, or a single counter for one bracket type) is the
  verification counterpart of this generator.
""",
    solution=r'''def generate_parenthesis(n):
    res = []

    def go(prefix, open_, close):
        # A full-length prefix built under our rules is always balanced.
        if len(prefix) == 2 * n:
            res.append(prefix)
            return
        # '(' first: '(' < ')' in ASCII, so leaves are produced in sorted order.
        if open_ < n:              # still have opening brackets left to place
            go(prefix + "(", open_ + 1, close)
        if close < open_:          # only close a bracket that is currently open
            go(prefix + ")", open_, close + 1)

    go("", 0, 0)
    return res
''',
    refs={
        "cpp": r"""static void go(int n, int open, int close, string& cur, vector<string>& res) {
    if ((int)cur.size() == 2 * n) { res.push_back(cur); return; }
    if (open < n) {                 // '(' first keeps the output sorted
        cur.push_back('(');
        go(n, open + 1, close, cur, res);
        cur.pop_back();
    }
    if (close < open) {             // never close more than we've opened
        cur.push_back(')');
        go(n, open, close + 1, cur, res);
        cur.pop_back();
    }
}

vector<string> generateParenthesis(long long n) {
    vector<string> res;
    string cur;
    go((int)n, 0, 0, cur, res);
    return res;
}
""",
        "rust": r"""pub fn generate_parenthesis(n: i64) -> Vec<String> {
    fn go(n: usize, open: usize, close: usize, cur: &mut String, res: &mut Vec<String>) {
        if cur.len() == 2 * n {
            res.push(cur.clone());
            return;
        }
        if open < n {
            cur.push('(');
            go(n, open + 1, close, cur, res);
            cur.pop();
        }
        if close < open {
            cur.push(')');
            go(n, open, close + 1, cur, res);
            cur.pop();
        }
    }
    let mut res = Vec::new();
    go(n as usize, 0, 0, &mut String::with_capacity(2 * n as usize), &mut res);
    res
}
""",
    },
    tests=[[3], [1], [2], [4], [5], [6], [8]],
))

# ---------------------------------------------------------------- 11. n-queens
PROBLEMS.append(dict(
    id="n-queens-count",
    title="N-Queens (Count Solutions)",
    difficulty=3,
    tags=["backtracking", "recursion", "pruning"],
    fn="total_n_queens",
    params=[["n", "int"]],
    returns="int",
    statement=r"""
Place `n` chess queens on an `n × n` board so that **no two queens attack each other**:
no two share a row, a column, or a diagonal (in either direction).

Return the **number of distinct placements**. Two placements are different if some square
holds a queen in one and not in the other (rotations and reflections count separately).
""",
    constraints=["1 ≤ n ≤ 9"],
    example_notes=["The two solutions on a 4×4 board are mirror images of each other.", "A single queen on a 1×1 board."],
    hints=[
        "Every row contains exactly one queen. So decide row by row: in which column does this row's queen go?",
        "Backtrack over rows. Before placing at `(row, col)`, check that no earlier queen shares its column or diagonal.",
        "Checks in O(1): squares on the same `\\` diagonal share `row - col`, squares on the same `/` diagonal share `row + col`. Keep three boolean arrays: `cols[c]`, `diag1[row + c]`, `diag2[row - c + n - 1]`.",
    ],
    explanation=r"""
## Intuition

Brute force over all ways to place n queens on n² squares is astronomical. But a
constraint in the statement collapses the search space: queens can't share a row, and
there are n queens and n rows, so **each row holds exactly one queen**. The problem
becomes: for row 0, 1, …, n − 1 in turn, choose a column. That's a decision tree of depth
n where we prune any column already attacked.

## Approach

Represent attacked lines with three boolean arrays:

- `cols[c]`: column c is taken;
- `d1[r + c]`: the `/` anti-diagonal (constant `r + c`, values 0 … 2n−2) is taken;
- `d2[r − c + n − 1]`: the `\` diagonal (constant `r − c`, shifted to be ≥ 0) is taken.

`place(row)`:

1. If `row == n`: all queens placed, return 1.
2. Sum over every column `c` that is free in all three arrays: mark the three entries
   (choose), add `place(row + 1)` (explore), unmark them (un-choose).

Trace for `n = 4` (columns chosen per row; ✗ = every column attacked):

```text
row0 c0 → row1 c2 → row2 ✗
        → row1 c3 → row2 c1 → row3 ✗
row0 c1 → row1 c3 → row2 c0 → row3 c2  ✓  . Q . .
                                           . . . Q
                                           Q . . .
                                           . . Q .
row0 c2 → row1 c0 → row2 c3 → row3 c1  ✓  (mirror image)
row0 c3 → row1 c0 → row2 c2 → row3 ✗
        → row1 c1 → row2 ✗
```

Result: 2.

## Complexity

- **Time:** at most n · (n−1) · (n−2) ⋯ = O(n!) leaves, and pruning on diagonals cuts far
  deeper than that in practice (n = 9 explores only a few tens of thousands of nodes).
  Each node does O(n) work scanning columns.
- **Space:** O(n) for the arrays and the recursion depth.

Results by n: 1, 0, 0, 2, 10, 4, 40, 92, 352.

## Common mistakes

- **Diagonal indices out of range:** `r − c` is negative for c > r; shift it by `n − 1`.
  Arrays for diagonals need size `2n − 1`.
- **Mixing up which diagonal is which** only matters if you use one array for both: they
  must be separate.
- **Not unmarking** after the recursive call: later branches see phantom queens and the
  count collapses to 0 or 1.
- **Checking all previous queens** with a loop (O(n) per check) is correct but slower; the
  arrays make it O(1).

## Going further

- **Bitmask version:** represent `cols`, `d1`, `d2` as integers, shifting the diagonal
  masks by one each row. Available squares are `~(cols | d1 | d2) & ((1 << n) − 1)`, and
  `x & −x` extracts the lowest free column. This is the fastest known simple solver.
- **Symmetry:** count only placements with the first queen in the left half and double
  them (fix up the middle column for odd n) to halve the work.
- Returning the actual boards (N-Queens I) is the same search with a path of columns.
""",
    solution=r'''def total_n_queens(n):
    # One queen per row, so we only choose a column for each row in turn.
    cols = [False] * n             # column already holds a queen
    d1 = [False] * (2 * n - 1)     # '/' diagonals: r + c is constant along each
    d2 = [False] * (2 * n - 1)     # '\' diagonals: r - c is constant; shift by n-1 to be >= 0

    def place(row):
        # Every row has a queen: this is one complete, non-attacking placement.
        if row == n:
            return 1
        count = 0
        for c in range(n):
            if cols[c] or d1[row + c] or d2[row - c + n - 1]:
                continue                                  # attacked: prune this branch
            cols[c] = d1[row + c] = d2[row - c + n - 1] = True     # choose
            count += place(row + 1)                                # explore
            cols[c] = d1[row + c] = d2[row - c + n - 1] = False    # un-choose
        return count

    return place(0)
''',
    refs={
        "c": r"""// Three "is this line taken?" arrays, sized for n <= 9 (2n - 1 <= 17 diagonals).
static bool cols[16], d1[32], d2[32];

static long long place(int row, int n) {
    if (row == n) return 1;                       // every row filled: one solution
    long long count = 0;
    for (int c = 0; c < n; c++) {
        if (cols[c] || d1[row + c] || d2[row - c + n - 1]) continue;   // attacked
        cols[c] = d1[row + c] = d2[row - c + n - 1] = true;    // choose
        count += place(row + 1, n);                            // explore
        cols[c] = d1[row + c] = d2[row - c + n - 1] = false;   // un-choose
    }
    return count;
}

long long total_n_queens(long long n) {
    // The arrays are all false again after each search (every mark was undone),
    // so repeated calls are safe.
    return place(0, (int)n);
}
""",
        "cpp": r"""// Bitmask variant: bit c of `cols` = column c taken. The diagonal masks are stored
// *relative to the current row*: shifting them by one per row moves each attacked
// diagonal square to the column it hits in the next row.
static long long place(int n, int row, unsigned cols, unsigned d1, unsigned d2) {
    if (row == n) return 1;
    unsigned full = (1u << n) - 1;
    unsigned free_ = ~(cols | d1 | d2) & full;   // columns safe in this row
    long long count = 0;
    while (free_) {
        unsigned bit = free_ & -free_;             // lowest free column
        free_ ^= bit;                              // remove it from the candidates
        // Passing new masks by value means there's nothing to un-choose afterwards.
        count += place(n, row + 1, cols | bit, (d1 | bit) << 1, (d2 | bit) >> 1);
    }
    return count;
}

long long totalNQueens(long long n) { return place((int)n, 0, 0, 0, 0); }
""",
        "rust": r"""pub fn total_n_queens(n: i64) -> i64 {
    let n = n as usize;
    // A small struct keeps the three marker arrays together and lets the recursive
    // method borrow them mutably through &mut self.
    struct Board { n: usize, cols: Vec<bool>, d1: Vec<bool>, d2: Vec<bool> }
    impl Board {
        fn place(&mut self, row: usize) -> i64 {
            if row == self.n {
                return 1;
            }
            let mut count = 0;
            for c in 0..self.n {
                let (a, b) = (row + c, row + self.n - 1 - c); // b is r - c shifted, never negative
                if self.cols[c] || self.d1[a] || self.d2[b] {
                    continue;
                }
                self.cols[c] = true; self.d1[a] = true; self.d2[b] = true;     // choose
                count += self.place(row + 1);                                  // explore
                self.cols[c] = false; self.d1[a] = false; self.d2[b] = false;  // un-choose
            }
            count
        }
    }
    let mut b = Board { n, cols: vec![false; n], d1: vec![false; 2 * n], d2: vec![false; 2 * n] };
    b.place(0)
}
""",
        "espresso": r"""// Arrays are fixed-size literals, large enough for n <= 9 (17 diagonals).
// 0 = free, 1 = taken. Arrays are passed by reference, so marks are shared.
fn place(row, n, cols, d1, d2) {
  if row == n {
    return 1
  }
  var count = 0
  // A while loop with a local counter: each recursive frame needs its own `c`.
  var c = 0
  while c < n {
    var a = row + c
    var b = row - c + n - 1
    if cols[c] == 0 and d1[a] == 0 and d2[b] == 0 {
      cols[c] = 1
      d1[a] = 1
      d2[b] = 1
      count += place(row + 1, n, cols, d1, d2)
      cols[c] = 0
      d1[a] = 0
      d2[b] = 0
    }
    c += 1
  }
  return count
}

fn totalNQueens(n) {
  var cols = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  var d1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  var d2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  return place(0, n, cols, d1, d2)
}
""",
    },
    tests=[[4], [1], [2], [3], [5], [6], [7], [8], [9]],
))

# ---------------------------------------------------------------- 12. word search
PROBLEMS.append(dict(
    id="word-search-grid",
    title="Word Search",
    difficulty=2,
    tags=["backtracking", "dfs", "grid"],
    fn="exist",
    params=[["board", "str[]"], ["word", "str"]],
    returns="bool",
    statement=r"""
A letter grid is given as `board`, a list of equal-length strings (one per row). Return
`true` if `word` can be traced through the grid, and `false` otherwise.

The word is traced by starting at any cell and stepping to a **horizontally or vertically
adjacent** cell for each next letter. A cell may be used **at most once** in a single
trace. Letters are case-sensitive.
""",
    constraints=["1 ≤ rows, cols ≤ 6", "1 ≤ len(word) ≤ 15", "board and word contain only English letters"],
    example_notes=[
        "A→B→C→C→E→D snakes along the top row, down, and back left.",
        "S→E→E: the S on the right edge, the E below it, then the E to its left.",
    ],
    examples=3,
    hints=[
        "Try every cell as a starting point. From a cell matching `word[i]`, the rest of the word must continue from one of its four neighbours.",
        "Write `dfs(r, c, i)`: does `word[i:]` start at `(r, c)`? Fail fast on bounds, mismatches, and already-used cells.",
        "Mark the cell as used before exploring neighbours (e.g. overwrite it with `#`) and restore it afterwards: that is the un-choose step. Return as soon as one neighbour succeeds.",
    ],
    explanation=r"""
## Intuition

From a given cell, the word can continue in up to 4 directions, and from there in up to 3
new ones, a branching search with a **"no revisits"** rule. That rule is path-dependent
state: a cell blocked in one attempt must be free again in another attempt. Backtracking
handles exactly that: mark the cell when we step on it, unmark it when we step back.

## Approach

`dfs(r, c, i)` returns whether `word[i:]` can be traced starting at `(r, c)`:

1. If `i == len(word)`: return true (everything matched).
2. If `(r, c)` is off the grid, already used, or `grid[r][c] != word[i]`: return false.
3. **Choose:** mark `(r, c)` used (overwrite with `#`, which matches no letter).
4. **Explore:** `found = dfs` on the four neighbours with `i + 1`, stopping at the first success.
5. **Un-choose:** restore the letter. Return `found`.

Call `dfs(r, c, 0)` from every cell; return true if any call succeeds.

Trace for `ABCCED` on the classic board:

```text
A B C E      start (0,0)=A → (0,1)=B → (0,2)=C → (1,2)=C
S F C S                     → (2,2)=E → (2,1)=D  ✓
A D E E
```

When searching `ABCB`, the path reaches `A→B→C` and the only neighbouring `B` is the one
already used, so the `#` marker blocks it and the search correctly fails.

**Cheap pruning that pays off:**
- If the word has more of some letter than the whole board, return false before searching.
- If the word's last letter is rarer on the board than its first, search for the reversed
  word: fewer starting points survive the first step.

## Complexity

- **Time:** O(R · C · 3^L) in the worst case for word length L: R·C starts, the first step
  has 4 options and every later step at most 3 (you can't go back the way you came).
- **Space:** O(L) recursion depth, plus O(R·C) if you copy the board to mutate it.

## Common mistakes

- **Forgetting to restore the cell** after exploring: later starting points see a board
  full of `#` and miss valid paths.
- **Restoring inside the loop only on failure:** restore unconditionally before returning,
  or the board stays corrupted after a success too (bad if the caller reuses it).
- **Checking `i == len(word)` after the bounds check:** a word that ends exactly at the
  board edge would then be rejected when the recursion steps off the grid.
- **Mutating the input:** in C the row strings may live in read-only memory. Use a
  separate `visited` array or copy the board first.

## Going further

- **Word Search II** (find many words at once): build a trie of the words and run one DFS
  per cell that walks the trie alongside the grid, pruning when no word continues.
- Boggle solvers, maze path-finding with "visit once" rules, and Hamiltonian path search
  all use this mark/explore/unmark DFS.
""",
    solution=r'''from collections import Counter


def exist(board, word):
    rows, cols = len(board), len(board[0])
    # Pruning 1: the board must contain enough copies of every letter in the word.
    have = Counter("".join(board))
    if any(have[ch] < k for ch, k in Counter(word).items()):
        return False
    # Pruning 2: start from the rarer end. Reversing doesn't change whether a path exists.
    if have[word[-1]] < have[word[0]]:
        word = word[::-1]

    grid = [list(row) for row in board]   # mutable copy: strings can't be changed in place

    def dfs(r, c, i):
        if i == len(word):
            return True                          # matched every letter
        if not (0 <= r < rows and 0 <= c < cols) or grid[r][c] != word[i]:
            return False                         # off-grid, used ('#'), or wrong letter
        saved = grid[r][c]
        grid[r][c] = "#"                         # choose: mark as used on this path
        found = (dfs(r + 1, c, i + 1) or dfs(r - 1, c, i + 1) or
                 dfs(r, c + 1, i + 1) or dfs(r, c - 1, i + 1))   # 'or' stops at first success
        grid[r][c] = saved                       # un-choose: free it for other paths
        return found

    return any(dfs(r, c, 0) for r in range(rows) for c in range(cols))
''',
    refs={
        "cpp": r"""// We take `board` by reference but work on a copy so the caller's data is untouched.
static bool dfs(vector<string>& g, const string& w, int r, int c, size_t i) {
    if (i == w.size()) return true;
    if (r < 0 || c < 0 || r >= (int)g.size() || c >= (int)g[0].size() || g[r][c] != w[i])
        return false;
    char saved = g[r][c];
    g[r][c] = '#';                                   // choose
    bool found = dfs(g, w, r + 1, c, i + 1) || dfs(g, w, r - 1, c, i + 1) ||
                 dfs(g, w, r, c + 1, i + 1) || dfs(g, w, r, c - 1, i + 1);
    g[r][c] = saved;                                 // un-choose
    return found;
}

bool exist(vector<string>& board, string word) {
    vector<string> g = board;
    for (int r = 0; r < (int)g.size(); r++)
        for (int c = 0; c < (int)g[0].size(); c++)
            if (dfs(g, word, r, c, 0)) return true;
    return false;
}
""",
        "rust": r"""pub fn exist(board: Vec<String>, word: String) -> bool {
    // Strings can't be indexed by position in Rust (they're UTF-8), so convert each row
    // into a Vec<u8>. The input is ASCII letters, so one byte = one letter.
    let mut g: Vec<Vec<u8>> = board.into_iter().map(|s| s.into_bytes()).collect();
    let w = word.as_bytes();

    fn dfs(g: &mut Vec<Vec<u8>>, w: &[u8], r: i32, c: i32, i: usize) -> bool {
        if i == w.len() {
            return true;
        }
        // Signed coordinates let us step to -1 and then reject it here.
        if r < 0 || c < 0 || r as usize >= g.len() || c as usize >= g[0].len() {
            return false;
        }
        let (ru, cu) = (r as usize, c as usize);
        if g[ru][cu] != w[i] {
            return false;
        }
        let saved = g[ru][cu];
        g[ru][cu] = b'#'; // choose
        let found = dfs(g, w, r + 1, c, i + 1)
            || dfs(g, w, r - 1, c, i + 1)
            || dfs(g, w, r, c + 1, i + 1)
            || dfs(g, w, r, c - 1, i + 1);
        g[ru][cu] = saved; // un-choose
        found
    }

    for r in 0..g.len() {
        for c in 0..g[0].len() {
            if dfs(&mut g, w, r as i32, c as i32, 0) {
                return true;
            }
        }
    }
    false
}
""",
    },
    tests=[
        [["ABCE", "SFCS", "ADEE"], "ABCCED"],
        [["ABCE", "SFCS", "ADEE"], "SEE"],
        [["ABCE", "SFCS", "ADEE"], "ABCB"],
        [["a"], "a"],
        [["a"], "b"],
        [["ab", "cd"], "abdc"],
        [["ab", "cd"], "abcd"],
        [["ab"], "abab"],
        [["AAAA", "AAAA", "AAAA"], "AAAAAAAAAAAA"],
        [["AAAA", "AAAA", "AAAA"], "AAAAAAAAAAAB"],
        [["aA", "Aa"], "aAaA"],
        [["CAA", "AAA", "BCD"], "AAB"],
        [["ABCDEF", "LKJIHG", "MNOPQR", "XWVUTS", "YZabcd", "jihgfe"], "ABCDEFGHIJKLMNO"],
    ],
))

# ---------------------------------------------------------------- 13. palindrome partitioning
PROBLEMS.append(dict(
    id="palindrome-partitioning-all",
    title="Palindrome Partitioning",
    difficulty=2,
    tags=["backtracking", "recursion", "string"],
    fn="palindrome_partitions",
    params=[["s", "str"]],
    returns="str[][]",
    compare="unordered",
    statement=r"""
Split the string `s` into consecutive pieces so that **every piece is a palindrome** (reads
the same forwards and backwards). Return **every** such partition.

Each partition is a list of pieces in left-to-right order (concatenating them gives `s`).
The partitions themselves may be returned in any order.
""",
    constraints=["1 ≤ len(s) ≤ 10", "`s` contains only lowercase English letters"],
    example_notes=["`a|a|b` and `aa|b` work; `aab` itself is not a palindrome.", "A single character is always a palindrome."],
    hints=[
        "The first piece must be some prefix `s[0:end]`. Which prefixes are allowed?",
        "For every palindromic prefix, recursively partition the remainder of the string, and prepend the prefix to each result.",
        "Backtrack on a `start` index: for each `end > start` with `s[start:end]` a palindrome, append that piece to the path, recurse from `end`, pop. When `start == len(s)`, record a copy of the path.",
    ],
    explanation=r"""
## Intuition

Every partition is a sequence of cut decisions: "where does the first piece end? then
where does the next piece end?" The first piece is some prefix of `s`; once it's chosen,
the rest is the same problem on a shorter string. Only palindromic prefixes are allowed,
which is the pruning rule. That is the for-loop backtracking template with the loop
running over **piece end positions** instead of elements.

## Approach

`go(start)` with a shared `path` of pieces:

1. If `start == len(s)`: the pieces cover the whole string, so record a copy of `path`.
2. For `end` from `start + 1` to `len(s)`: if `s[start:end]` is a palindrome, append it,
   call `go(end)`, pop.

Trace for `aab`:

```text
go(0) []
├─ "a"   palindrome → go(1) [a]
│   ├─ "a"  palindrome → go(2) [a,a]
│   │   └─ "b" palindrome → go(3) [a,a,b] ✓
│   └─ "ab" not a palindrome ✗
├─ "aa"  palindrome → go(2) [aa]
│   └─ "b" palindrome → go(3) [aa,b] ✓
└─ "aab" not a palindrome ✗
```

**Speeding up the palindrome test:** checking `s[i:j]` directly costs O(n) each time.
Precompute a table `pal[i][j]` (is `s[i..j]` a palindrome?) bottom-up:
`pal[i][j] = s[i] == s[j] and (j − i < 2 or pal[i+1][j−1])`. That makes every check O(1)
for an O(n²) setup cost. For n ≤ 10 either is fine; for longer strings the table matters.

## Complexity

- **Time:** O(n · 2ⁿ) in the worst case. A string of identical letters makes every one of
  the 2ⁿ⁻¹ ways to cut it valid, and each result takes O(n) to copy.
- **Space:** O(n) recursion depth and path (plus O(n²) for the optional table), excluding
  the output.

## Common mistakes

- **Off-by-one on `end`:** `end` must reach `len(s)` *inclusive* so the last piece can run
  to the end of the string. In Python that's `range(start + 1, len(s) + 1)`.
- **Recording the path by reference** instead of copying.
- **Sorting pieces inside a partition:** order within a partition matters (it must
  concatenate back to `s`); only the order *between* partitions is free.

## Going further

- **Minimum cuts** (Palindrome Partitioning II): instead of listing partitions, find the
  fewest cuts. That is DP: `cuts[j] = min(cuts[i] + 1)` over palindromic `s[i..j]`,
  O(n²) with the `pal` table.
- The same "choose a valid prefix, recurse on the rest" pattern solves word break
  (prefixes from a dictionary) and restoring IP addresses (prefixes that are valid octets).
""",
    solution=r'''def palindrome_partitions(s):
    n = len(s)
    res = []
    path = []

    def is_pal(i, j):
        # Is s[i:j] (j exclusive) a palindrome? Compare from both ends inward.
        j -= 1
        while i < j:
            if s[i] != s[j]:
                return False
            i += 1
            j -= 1
        return True

    def go(start):
        # The pieces in path cover s[0:start]. If that's all of s, we have a partition.
        if start == n:
            res.append(path[:])
            return
        # The next piece is s[start:end] for some end; only palindromes are allowed.
        for end in range(start + 1, n + 1):
            if is_pal(start, end):
                path.append(s[start:end])   # choose this piece
                go(end)                     # partition the rest
                path.pop()                  # un-choose

    go(0)
    return res
''',
    refs={
        "cpp": r"""// pal[i][j] precomputed so every palindrome check is O(1).
static void go(const string& s, size_t start, const vector<vector<bool>>& pal,
               vector<string>& path, vector<vector<string>>& res) {
    if (start == s.size()) { res.push_back(path); return; }
    for (size_t end = start; end < s.size(); end++) {        // piece = s[start..end] inclusive
        if (!pal[start][end]) continue;
        path.push_back(s.substr(start, end - start + 1));    // choose
        go(s, end + 1, pal, path, res);                      // explore
        path.pop_back();                                     // un-choose
    }
}

vector<vector<string>> palindromePartitions(string s) {
    int n = s.size();
    vector<vector<bool>> pal(n, vector<bool>(n, false));
    // Fill by increasing i from the right so pal[i+1][j-1] is ready when we need it.
    for (int i = n - 1; i >= 0; i--)
        for (int j = i; j < n; j++)
            pal[i][j] = s[i] == s[j] && (j - i < 2 || pal[i + 1][j - 1]);
    vector<vector<string>> res;
    vector<string> path;
    go(s, 0, pal, path, res);
    return res;
}
""",
        "rust": r"""pub fn palindrome_partitions(s: String) -> Vec<Vec<String>> {
    fn is_pal(b: &[u8]) -> bool {
        // Compare the slice with its reverse lazily, no allocation.
        b.iter().eq(b.iter().rev())
    }
    fn go(s: &str, start: usize, path: &mut Vec<String>, res: &mut Vec<Vec<String>>) {
        if start == s.len() {
            res.push(path.clone());
            return;
        }
        for end in start + 1..=s.len() {
            // Slicing by byte index is fine: the input is ASCII lowercase.
            if is_pal(&s.as_bytes()[start..end]) {
                path.push(s[start..end].to_string()); // choose
                go(s, end, path, res);
                path.pop();                           // un-choose
            }
        }
    }
    let mut res = Vec::new();
    go(&s, 0, &mut Vec::new(), &mut res);
    res
}
""",
    },
    tests=[["aab"], ["a"], ["ab"], ["aaaa"], ["racecar"], ["abba"], ["aaaaaaaa"], ["abcbaxyzzy"], ["noonabbad"]],
))

# ---------------------------------------------------------------- 14. sudoku solver
def _sudoku_count(grid, limit=2):
    """Count solutions of an 81-cell grid (0 = empty), stopping at `limit`."""
    rows, cols, boxes = [0] * 9, [0] * 9, [0] * 9
    for i, v in enumerate(grid):
        if v:
            r, c = divmod(i, 9)
            rows[r] |= 1 << v; cols[c] |= 1 << v; boxes[r // 3 * 3 + c // 3] |= 1 << v
    count = 0

    def go():
        nonlocal count
        best, best_mask, best_n = -1, 0, 10
        for i in range(81):
            if grid[i] == 0:
                r, c = divmod(i, 9)
                m = ~(rows[r] | cols[c] | boxes[r // 3 * 3 + c // 3]) & 0x3FE
                k = bin(m).count("1")
                if k < best_n:
                    best, best_mask, best_n = i, m, k
                if k == 0:
                    return
        if best < 0:
            count += 1
            return
        r, c = divmod(best, 9); b = r // 3 * 3 + c // 3
        m = best_mask
        while m and count < limit:
            bit = m & -m; m ^= bit
            grid[best] = bit.bit_length() - 1
            rows[r] |= bit; cols[c] |= bit; boxes[b] |= bit
            go()
            rows[r] ^= bit; cols[c] ^= bit; boxes[b] ^= bit
            grid[best] = 0

    go()
    return count


def _sudoku_puzzle(seed, blanks):
    rng = random.Random(seed)
    # A valid solved grid from a pattern, then randomised by symmetry-preserving shuffles.
    digits = list(range(1, 10)); rng.shuffle(digits)
    def perm3():
        bands = [0, 1, 2]; rng.shuffle(bands)
        out = []
        for b in bands:
            inner = [0, 1, 2]; rng.shuffle(inner)
            out += [b * 3 + x for x in inner]
        return out
    rs, cs = perm3(), perm3()
    sol = [digits[(3 * (r % 3) + r // 3 + c) % 9] for r in rs for c in cs]
    grid = sol[:]
    cells = list(range(81)); rng.shuffle(cells)
    removed = 0
    for i in cells:
        if removed >= blanks:
            break
        v = grid[i]; grid[i] = 0
        if _sudoku_count(grid[:]) == 1:
            removed += 1
        else:
            grid[i] = v
    return ["".join(str(v) if v else "." for v in grid[r * 9:r * 9 + 9]) for r in range(9)]


_classic = ["53..7....", "6..195...", ".98....6.", "8...6...3", "4..8.3..1",
            "7...2...6", ".6....28.", "...419..5", "....8..79"]
_solved = [
    "534678912", "672195348", "198342567", "859761423", "426853791",
    "713924856", "961537284", "287419635", "345286179",
]
_one_blank = ["534678912", "672195348", "198342567", "859761423", "426.53791",
              "713924856", "961537284", "287419635", "345286179"]

PROBLEMS.append(dict(
    id="sudoku-solver-backtracking",
    title="Sudoku Solver",
    difficulty=3,
    tags=["backtracking", "recursion", "constraint propagation", "bitmask"],
    fn="solve_sudoku",
    params=[["board", "str[]"]],
    returns="str[]",
    statement=r"""
Solve a Sudoku. `board` has 9 strings of 9 characters each: a digit `1`–`9` is a given
clue and `.` is an empty cell. Fill every empty cell so that each **row**, each
**column** and each of the nine **3 × 3 boxes** contains every digit 1–9 exactly once.

Every puzzle has **exactly one** solution. Return the solved board in the same format
(9 strings of 9 digits).
""",
    constraints=["`board` is 9 strings of length 9", "characters are `1`–`9` or `.`", "the puzzle has exactly one solution"],
    example_notes=["The classic puzzle; 51 cells to fill.", "Already solved: return it unchanged."],
    examples=2,
    hints=[
        "Find an empty cell, try each digit that doesn't already appear in its row, column or box, and recurse. If you get stuck, undo and try the next digit.",
        "Keep `rows[r]`, `cols[c]`, `boxes[b]` as sets (or 9-bit masks) of used digits so the legality check is O(1). Box index: `b = (r // 3) * 3 + c // 3`.",
        "Return `True` from the recursion as soon as the board is full, and stop trying digits once a call succeeds, so the solved board isn't undone on the way back up.",
        "Big speed-up: instead of the first empty cell, branch on the empty cell with the **fewest** legal digits (often exactly one). Dead ends are discovered much earlier.",
    ],
    explanation=r"""
## Intuition

Sudoku is the textbook **constraint satisfaction** problem: variables (the empty cells),
domains (digits 1–9), and constraints (all-different in each row, column, box).
Backtracking solves any such problem: assign a value consistent with the constraints so
far, recurse, and undo the assignment when the recursion reports failure. The search
tree is deep (up to ~60 levels) but very narrow, because constraints rule out most
digits immediately.

## Approach

**State.** Three arrays of 9-bit masks: bit `d` of `rows[r]` means digit `d` is already in
row `r`; likewise `cols[c]` and `boxes[b]` with `b = (r // 3) * 3 + c // 3`. The digits
legal in cell `(r, c)` are the bits **not** set in `rows[r] | cols[c] | boxes[b]`.

**Search.** `solve()`:

1. Scan the empty cells and pick the one with the **fewest legal digits** (the
   "minimum remaining values" heuristic). If some empty cell has 0 options, this branch
   is dead: return false. If no empty cell is left, return true.
2. For each legal digit: place it and set its bit in the three masks (choose), recurse
   (explore); if the recursion returned true, return true immediately; otherwise clear the
   bits and the cell (un-choose).
3. All digits failed: return false.

The "return true immediately" is what preserves the solution: once the board is
complete, every frame returns straight up *without* running its un-choose code.

A peek at the classic puzzle's first decision:

```text
row 4: "4..8.3..1"     cell (4,4): row has {1,3,4,8}, column 4 has {1,2,6,7,8,9},
                        box 4 has {2,3,6,8}  →  used {1,2,3,4,6,7,8,9}
                        legal = {5}: a forced move, no branching at all.
```

With MRV, the solver keeps finding cells like this one, so most easy and medium puzzles
are solved with no wrong guesses at all.

**Bit tricks used in the references.** `free = ~(rows[r] | cols[c] | boxes[b]) & 0x3FE`
keeps bits 1..9. `free & -free` isolates the lowest set bit (the smallest legal digit);
`free ^= bit` removes it; the digit is that bit's index. Counting set bits
(`popcount`) gives the number of options for MRV.

## Complexity

- **Time:** exponential in the worst case (Sudoku generalised to n² × n² is NP-complete),
  but for 9 × 9 puzzles with constraint checks in O(1) and MRV ordering, real puzzles take
  from microseconds to a few milliseconds. Each node costs O(81) to find the best cell.
- **Space:** O(81) recursion depth at most, plus the 27 masks.

Without MRV (always taking the first empty cell), the solver is still correct but can
explore millions of nodes on puzzles designed to defeat left-to-right search.

## Common mistakes

- **Wrong box index:** `(r // 3) * 3 + c // 3`, not `r // 3 + c // 3` (that maps different
  boxes to the same number).
- **Undoing the solution:** if the recursion doesn't propagate "solved" up and stop, the
  un-choose steps erase every digit and you return the original puzzle.
- **Forgetting to mark the given clues** in the masks before searching: the solver then
  happily places duplicates of the clues.
- **Strings are immutable** in Python and Rust: convert rows to lists / byte vectors,
  solve, then join them back into strings.

## Going further

- **Constraint propagation:** after each placement, repeatedly fill every cell that has a
  single option ("naked singles") and every digit that fits only one place in a unit
  ("hidden singles"). Most newspaper puzzles fall to propagation alone.
- **Dancing Links (Algorithm X)** solves Sudoku as an exact-cover problem, the elegant
  general method by Knuth.
- **Counting solutions** (stop at 2) checks that a puzzle is valid, and it's how the test
  puzzles for this problem were generated: remove clues one at a time while the solution
  stays unique.
""",
    solution=r'''def solve_sudoku(board):
    grid = [list(row) for row in board]      # strings are immutable: work on lists
    # Bit d of rows[r] / cols[c] / boxes[b] set  <=>  digit d already used there.
    rows, cols, boxes = [0] * 9, [0] * 9, [0] * 9
    empties = []
    for r in range(9):
        for c in range(9):
            ch = grid[r][c]
            if ch == ".":
                empties.append((r, c))
            else:
                bit = 1 << int(ch)
                rows[r] |= bit; cols[c] |= bit; boxes[r // 3 * 3 + c // 3] |= bit

    def solve():
        # Minimum remaining values: branch on the empty cell with the fewest options.
        best, best_free, best_count = None, 0, 10
        for r, c in empties:
            if grid[r][c] != ".":
                continue
            free = ~(rows[r] | cols[c] | boxes[r // 3 * 3 + c // 3]) & 0x3FE  # bits 1..9
            count = bin(free).count("1")
            if count == 0:
                return False             # a cell with no legal digit: dead end, backtrack
            if count < best_count:
                best, best_free, best_count = (r, c), free, count
        if best is None:
            return True                  # no empty cell left: solved

        r, c = best
        b = r // 3 * 3 + c // 3
        free = best_free
        while free:
            bit = free & -free           # lowest legal digit as a single bit
            free ^= bit
            d = bit.bit_length() - 1     # bit index = the digit
            grid[r][c] = str(d)          # choose
            rows[r] |= bit; cols[c] |= bit; boxes[b] |= bit
            if solve():                  # explore; success propagates straight up,
                return True              # skipping the undo so the solution survives
            rows[r] ^= bit; cols[c] ^= bit; boxes[b] ^= bit   # un-choose
            grid[r][c] = "."
        return False                     # every digit failed here: the caller must retry

    solve()
    return ["".join(row) for row in grid]
''',
    refs={
        "c": r"""static int rowsM[9], colsM[9], boxesM[9];
static char g[9][10];

static int box_of(int r, int c) { return r / 3 * 3 + c / 3; }

static bool solve(void) {
    // Find the empty cell with the fewest legal digits (MRV).
    int br = -1, bc = -1, bfree = 0, bcount = 10;
    for (int r = 0; r < 9; r++)
        for (int c = 0; c < 9; c++) {
            if (g[r][c] != '.') continue;
            int free_ = ~(rowsM[r] | colsM[c] | boxesM[box_of(r, c)]) & 0x3FE;
            int cnt = __builtin_popcount(free_);
            if (cnt == 0) return false;                    // dead end
            if (cnt < bcount) { br = r; bc = c; bfree = free_; bcount = cnt; }
        }
    if (br < 0) return true;                               // board full
    int b = box_of(br, bc);
    while (bfree) {
        int bit = bfree & -bfree;                          // lowest legal digit
        bfree ^= bit;
        g[br][bc] = (char)('0' + __builtin_ctz(bit));      // choose
        rowsM[br] |= bit; colsM[bc] |= bit; boxesM[b] |= bit;
        if (solve()) return true;                          // keep the solution
        rowsM[br] ^= bit; colsM[bc] ^= bit; boxesM[b] ^= bit;   // un-choose
        g[br][bc] = '.';
    }
    return false;
}

char** solve_sudoku(char** board, int boardSize, int* returnSize) {
    // Reset the global state: the function may be called several times.
    memset(rowsM, 0, sizeof rowsM); memset(colsM, 0, sizeof colsM); memset(boxesM, 0, sizeof boxesM);
    for (int r = 0; r < 9; r++) {
        memcpy(g[r], board[r], 9); g[r][9] = '\0';         // copy: don't write into the input
        for (int c = 0; c < 9; c++)
            if (g[r][c] != '.') {
                int bit = 1 << (g[r][c] - '0');
                rowsM[r] |= bit; colsM[c] |= bit; boxesM[box_of(r, c)] |= bit;
            }
    }
    solve();
    char** out = malloc(sizeof(char*) * 9);
    for (int r = 0; r < 9; r++) { out[r] = malloc(10); memcpy(out[r], g[r], 10); }
    *returnSize = 9;
    (void)boardSize;
    return out;
}
""",
        "cpp": r"""struct Sudoku {
    vector<string> g;
    array<int, 9> rows{}, cols{}, boxes{};          // bit d set = digit d used

    static int box(int r, int c) { return r / 3 * 3 + c / 3; }

    bool solve() {
        int br = -1, bc = -1, bfree = 0, bcount = 10;
        for (int r = 0; r < 9; r++)
            for (int c = 0; c < 9; c++) {
                if (g[r][c] != '.') continue;
                int f = ~(rows[r] | cols[c] | boxes[box(r, c)]) & 0x3FE;
                int cnt = __builtin_popcount(f);
                if (cnt == 0) return false;          // contradiction: backtrack
                if (cnt < bcount) { br = r; bc = c; bfree = f; bcount = cnt; }
            }
        if (br < 0) return true;                     // nothing left to fill
        int b = box(br, bc);
        for (int f = bfree; f; f &= f - 1) {         // f &= f-1 clears the lowest bit
            int bit = f & -f;
            g[br][bc] = char('0' + __builtin_ctz(bit));
            rows[br] |= bit; cols[bc] |= bit; boxes[b] |= bit;
            if (solve()) return true;
            rows[br] ^= bit; cols[bc] ^= bit; boxes[b] ^= bit;
        }
        g[br][bc] = '.';
        return false;
    }
};

vector<string> solveSudoku(vector<string>& board) {
    Sudoku s;
    s.g = board;                                     // our own mutable copy
    for (int r = 0; r < 9; r++)
        for (int c = 0; c < 9; c++)
            if (board[r][c] != '.') {
                int bit = 1 << (board[r][c] - '0');
                s.rows[r] |= bit; s.cols[c] |= bit; s.boxes[Sudoku::box(r, c)] |= bit;
            }
    s.solve();
    return s.g;
}
""",
        "rust": r"""struct Sudoku {
    g: [[u8; 9]; 9],       // b'.' or b'1'..=b'9'
    rows: [u16; 9],
    cols: [u16; 9],
    boxes: [u16; 9],
}

impl Sudoku {
    fn bx(r: usize, c: usize) -> usize { r / 3 * 3 + c / 3 }

    fn solve(&mut self) -> bool {
        // MRV: (row, col, legal-digit mask) of the most constrained empty cell.
        let mut best: Option<(usize, usize, u16)> = None;
        for r in 0..9 {
            for c in 0..9 {
                if self.g[r][c] != b'.' { continue; }
                let free = !(self.rows[r] | self.cols[c] | self.boxes[Self::bx(r, c)]) & 0x3FE;
                if free == 0 { return false; }           // dead end
                if best.map_or(true, |(_, _, f)| free.count_ones() < f.count_ones()) {
                    best = Some((r, c, free));
                }
            }
        }
        let Some((r, c, mut free)) = best else { return true }; // no empty cell: solved
        let b = Self::bx(r, c);
        while free != 0 {
            let bit = free & free.wrapping_neg();       // lowest set bit (x & -x for unsigned)
            free ^= bit;
            self.g[r][c] = b'0' + bit.trailing_zeros() as u8; // choose
            self.rows[r] |= bit; self.cols[c] |= bit; self.boxes[b] |= bit;
            if self.solve() { return true; }            // explore; keep the solution
            self.rows[r] ^= bit; self.cols[c] ^= bit; self.boxes[b] ^= bit; // un-choose
        }
        self.g[r][c] = b'.';
        false
    }
}

pub fn solve_sudoku(board: Vec<String>) -> Vec<String> {
    let mut s = Sudoku { g: [[b'.'; 9]; 9], rows: [0; 9], cols: [0; 9], boxes: [0; 9] };
    for (r, row) in board.iter().enumerate() {
        for (c, ch) in row.bytes().enumerate() {
            s.g[r][c] = ch;
            if ch != b'.' {
                let bit = 1u16 << (ch - b'0');
                s.rows[r] |= bit; s.cols[c] |= bit; s.boxes[Sudoku::bx(r, c)] |= bit;
            }
        }
    }
    s.solve();
    // Each row is ASCII, so from_utf8 can't fail.
    s.g.iter().map(|row| String::from_utf8(row.to_vec()).unwrap()).collect()
}
""",
    },
    tests=[[_classic], [_solved], [_one_blank],
           [_sudoku_puzzle(9141, 45)], [_sudoku_puzzle(9142, 52)],
           [_sudoku_puzzle(9143, 56)], [_sudoku_puzzle(9144, 64)]],
))
