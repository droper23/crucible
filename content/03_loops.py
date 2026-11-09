"""Track 3: Loops & Patterns. for/while mastery, off-by-one thinking, nested loops."""

import random

TRACK = dict(
    id="loops",
    title="Loops & Patterns",
    order=3,
    icon="↻",
    blurb="Make the machine repeat itself: counting, accumulating, nesting, and drawing with for and while.",
    intro=r"""
A loop is how a program does *more work than you wrote*. Ten lines of code can touch a
million values because a loop sends control back to the top. Almost every algorithm in
Crucible is a loop with a clever body, so this track is about getting the mechanics
completely automatic: where the loop starts, where it stops, what changes each pass,
and what is true every time you reach the top.

## Anatomy of a loop

Every loop has four parts, even when the syntax hides some of them:

```
  init ──► test ──false──► (exit)
            │ true
            ▼
          body
            │
          update ──► back to test
```

1. **Init**: set up the loop variable and any accumulators (`total = 0`).
2. **Test**: decide whether to run the body again.
3. **Body**: the actual work.
4. **Update**: move toward termination (`i += 1`, `n //= 10`).

Here is the same "add up 1..n" in every Crucible language:

```python
total = 0
for i in range(1, n + 1):      # range is half-open: 1, 2, ..., n
    total += i
```

```c
long long total = 0;
for (long long i = 1; i <= n; i++) {   // init; test; update
    total += i;
}
```

```cpp
long long total = 0;
for (long long i = 1; i <= n; ++i) total += i;
```

```rust
let mut total: i64 = 0;
for i in 1..=n {          // 1..n excludes n, 1..=n includes it
    total += i;
}
```

ESPresso uses `for var i in 0..n` (exclusive end, like Python's `range`) and `while cond { }`.
It has no `%` operator, so `a % b` is written `a - (a / b) * b`.

**`for` vs `while`.** Use `for` when you know the range up front ("each index", "1 to n").
Use `while` when you stop because of a *condition* rather than a count: "until the number
reaches 1", "while there are digits left". Any `for` can be rewritten as a `while`; the
`for` just puts init, test and update on one line where you cannot forget one.

## Off-by-one thinking

The most common loop bug is running one time too many or too few. Two habits remove most
of them:

- **Prefer half-open ranges `[lo, hi)`.** `range(lo, hi)`, `0..n` in Rust and ESPresso, and
  `for (i = 0; i < n; i++)` in C all include `lo` and exclude `hi`. The count of iterations is
  exactly `hi - lo`, empty ranges are simply `lo == hi`, and adjacent ranges `[a, b)` and `[b, c)`
  join without overlap. When the problem says "1 to n inclusive", write `range(1, n + 1)` or
  `1..=n` and say so in a comment.
- **Check the extremes by hand.** Before running, ask: what happens when `n = 0`? `n = 1`?
  When the array is empty? A loop whose body never runs must still leave the right answer in
  the accumulator, which is why `total` starts at `0` and a product starts at `1`.

A quick "fencepost" sanity check: a fence 10 metres long with a post every metre has
**11** posts. Whenever you count *boundaries* rather than *gaps*, expect a `+1`.

## Loop invariants

An **invariant** is a sentence that is true every time control reaches the loop test. It is
the most powerful tool for writing loops that are correct the first time.

```python
best = nums[0]
for i in range(1, len(nums)):
    # Invariant: best == max(nums[0..i-1])
    if nums[i] > best:
        best = nums[i]
# After the loop i has covered everything, so best == max(nums)
```

To use one, check three things: it holds **before** the first iteration (initialisation), the
body **keeps** it true (maintenance), and when the loop **stops** the invariant plus the stop
condition give you the answer (termination). You will see this reasoning in every
explanation in this track; it scales all the way up to binary search and dynamic programming.

Termination deserves its own thought for `while` loops: something must strictly move toward
the exit each pass. `n //= 10` shrinks `n`; `i += 1` approaches `len(nums)`. If you cannot name
the quantity that shrinks, you may have written an infinite loop.

## Nested loops and their cost

A loop inside a loop runs its inner body *outer × inner* times:

```python
for i in range(n):          # n times
    for j in range(i + 1, n):   # n-1, n-2, ..., 0 times
        ...                 # total: n(n-1)/2 ≈ n²/2 times
```

That is **O(n²)**. For `n = 1 000` it is half a million steps (instant); for `n = 10⁵` it is five
billion (minutes). Nested loops are the natural tool for 2-D output (rows × columns: triangles,
tables, diamonds) and for "every pair" questions, and later tracks will teach you to replace
them with hashing, sorting or two pointers when `n` gets large.

Starting the inner loop at `i + 1` instead of `0` is a classic trick: it visits each unordered
pair exactly once and never pairs an element with itself.

## Accumulator patterns

Most loop bodies are one of a handful of shapes:

| pattern | init | body |
|---|---|---|
| sum | `s = 0` | `s += x` |
| product | `p = 1` | `p *= x` |
| count | `c = 0` | `if cond: c += 1` |
| max so far | `m = first` | `m = max(m, x)` |
| digit peel | `n` | `d = n % 10; n //= 10` |

Recognise the shape, pick the right starting value, and the loop almost writes itself.

## Printing patterns

Drawing shapes with characters is pure nested-loop practice: the outer loop picks the
**row**, the inner loops print **spaces then symbols** whose counts are formulas in the row
number. Work out a table (row → spaces, stars) before coding:

```
row  spaces  stars        *
 1     2       1         ***
 2     1       3        *****
 3     0       5
```

Then `spaces = n - row`, `stars = 2*row - 1`. Getting the formula right on paper is 90% of the
problem; the code is two inner loops and a newline.

## Integer size

In C, C++ and Rust, `int` is 32-bit and overflows past about 2.1 billion; Crucible uses
`long long` / `i64` (about 9.2 × 10¹⁸) for every `int` parameter. Factorials and Fibonacci
numbers grow so fast that even 64 bits only reaches `20!` and `F(92)`. Python integers never
overflow, which is convenient but hides the problem; keep it in mind when you switch languages.
ESPresso integers are 32-bit.
""",
)


# ---------------------------------------------------------------- helpers

def _rng(seed):
    return random.Random(seed)


PROBLEMS = []

# ================================================================ 1. sum 1..n
PROBLEMS.append(dict(
    id="sum-one-to-n",
    title="Sum from 1 to n",
    difficulty=0,
    tags=["loop", "accumulator"],
    fn="sum_to_n",
    params=[["n", "int"]],
    returns="int",
    statement=r"""
Return the sum `1 + 2 + 3 + ... + n`.

If `n` is `0`, the sum is empty and the answer is `0`.

Write it with a **loop** (the point of this problem is the loop; see the explanation for the
closed-form shortcut).
""",
    constraints=["0 ≤ n ≤ 10⁴"],
    example_notes=["1 + 2 + 3 + 4 + 5 = 15.", "No terms to add, so the sum is 0."],
    hints=[
        "You need a variable that remembers the running total. What should it be before you have added anything?",
        "Loop a counter `i` over 1, 2, ..., n (inclusive!) and add each one to the total.",
        "In Python `range(1, n + 1)` stops *before* `n + 1`, so it includes `n`. In C: `for (i = 1; i <= n; i++)`.",
    ],
    explanation=r"""
## Intuition

"Add up a sequence" is the **sum accumulator** pattern: start a total at the identity value for
addition (`0`), then visit every term once and add it in. The only decisions are where the loop
starts, where it stops, and whether the end is included.

## Approach

1. `total = 0`. This is also the correct answer if the loop never runs (`n = 0`).
2. For each `i` from `1` to `n` **inclusive**, do `total += i`.
3. Return `total`.

Trace for `n = 5`:

| i | total after |
|---|---|
| (start) | 0 |
| 1 | 1 |
| 2 | 3 |
| 3 | 6 |
| 4 | 10 |
| 5 | 15 |

**Invariant:** at the top of each iteration, `total == 1 + 2 + ... + (i - 1)`. It holds at the start
(`i = 1`, empty sum = 0), each step adds `i` and advances `i`, and when the loop ends `i` has passed
`n`, so `total` is the full sum.

**Language mechanics.** Python's `range(a, b)` produces `a, a+1, ..., b-1`, so "up to n inclusive"
needs `range(1, n + 1)`. C's `for (init; test; update)` checks `test` *before* each pass, so with
`i <= n` the body runs for `i = n` and stops when `i` becomes `n + 1`. Rust's `1..=n` is the
inclusive range; `1..n` would silently miss the last term.

## Complexity

- **Time:** O(n), one addition per term.
- **Space:** O(1), two variables regardless of `n`.

## Common mistakes

- `range(1, n)` or `1..n`: stops at `n - 1`. For `n = 5` you get 10 instead of 15.
- Starting the total at `1` "because we start at 1": then `n = 0` returns 1.
- In C, declaring `int total`: fine here, but for larger `n` the sum passes 2³¹. Use `long long`.

## Going further

Young Gauss reportedly noticed that pairing the first and last terms gives `n + 1` each time,
and there are `n / 2` such pairs, so the sum is `n(n + 1) / 2`. That turns an O(n) loop into O(1)
arithmetic. Try proving it with the invariant: `1 + ... + (i-1) == (i-1)i/2`. Recognising when a
loop computes something with a closed form is a recurring optimisation.
""",
    solution=r'''def sum_to_n(n):
    # The running total starts at 0: the sum of zero terms. This also makes n = 0 correct
    # without a special case, because the loop body simply never runs.
    total = 0
    # range(1, n + 1) is 1, 2, ..., n. The +1 is needed because range excludes its end.
    for i in range(1, n + 1):
        # Invariant before this line: total == 1 + 2 + ... + (i - 1).
        total += i
    # The loop visited every i in [1, n], so total is the full sum.
    return total
''',
    refs={
        "c": r'''long long sum_to_n(long long n) {
    long long total = 0;            /* empty sum */
    for (long long i = 1; i <= n; i++) {   /* <= because n itself is included */
        total += i;
    }
    return total;
}''',
        "cpp": r'''long long sumToN(long long n) {
    long long total = 0;
    for (long long i = 1; i <= n; ++i) total += i;   // 1..n inclusive
    return total;
}''',
        "rust": r'''pub fn sum_to_n(n: i64) -> i64 {
    let mut total = 0;
    // 1..=n is inclusive; 1..n would stop at n - 1.
    for i in 1..=n {
        total += i;
    }
    total
}''',
        "espresso": r'''fn sumToN(n) {
  var total = 0
  // ESPresso ranges exclude the end, so go to n + 1 to include n.
  for var i in 1..n + 1 {
    total += i
  }
  return total
}''',
    },
    tests=[[5], [0], [1], [2], [10], [100], [9999], [10000]],
))

# ================================================================ 2. factorial
PROBLEMS.append(dict(
    id="factorial-iterative",
    title="Factorial with a Loop",
    difficulty=0,
    tags=["loop", "accumulator", "overflow"],
    fn="factorial",
    params=[["n", "int"]],
    returns="int",
    statement=r"""
Return `n!` (n factorial), the product `1 × 2 × 3 × ... × n`.

By definition `0! = 1` (the empty product).

Use a loop, not recursion.
""",
    constraints=["0 ≤ n ≤ 18"],
    example_notes=["5! = 1 × 2 × 3 × 4 × 5 = 120.", "0! is the empty product, which is 1."],
    hints=[
        "This is the sum accumulator's sibling: a *product* accumulator. What starting value leaves a product unchanged?",
        "Start `result = 1` and multiply it by each of 2, 3, ..., n.",
        "With `result = 1`, both n = 0 and n = 1 need no special case: the loop just doesn't run.",
    ],
    explanation=r"""
## Intuition

A product of many terms is the **product accumulator**: start at the multiplicative identity `1`
(starting at `0` would make everything `0`) and multiply in each term.

## Approach

1. `result = 1`.
2. For `i` in `2..=n`, `result *= i`. (Starting at 2 skips the pointless `× 1`.)
3. Return `result`.

Trace for `n = 5`:

| i | result |
|---|---|
| start | 1 |
| 2 | 2 |
| 3 | 6 |
| 4 | 24 |
| 5 | 120 |

Invariant: before multiplying by `i`, `result == (i - 1)!`.

## Complexity

- **Time:** O(n) multiplications.
- **Space:** O(1).

## Common mistakes

- **Starting at 0.** `0 × anything = 0`.
- **Overflow.** Factorials explode: `13!` already exceeds a 32-bit `int`, and `21!` exceeds a
  64-bit `long long` / `i64`. That is why this problem stops at `n = 18` (which keeps answers
  exactly representable everywhere Crucible runs). Python silently switches to big integers; C
  silently wraps around to garbage; Rust panics in debug builds and wraps in release builds.
- Forgetting `0! = 1`. A loop that starts `result = n` gets it wrong.

## Going further

- Rust has `checked_mul`, which returns `None` on overflow instead of wrapping: a good habit when
  values can grow.
- `n!` counts the orderings of `n` distinct items, which is why it appears all over combinatorics.
  Computing `C(n, k) = n! / (k!(n-k)!)` naively overflows quickly; multiplying and dividing
  alternately (`r = r * (n - i) / (i + 1)`) keeps intermediate values small.
""",
    solution=r'''def factorial(n):
    # 1 is the identity for multiplication, and it is also 0! and 1!, so starting
    # here makes both small cases fall out without any if-statement.
    result = 1
    # Multiplying by 1 changes nothing, so the loop can start at 2.
    for i in range(2, n + 1):
        # Invariant: result == (i - 1)! before this multiplication.
        result *= i
    return result
''',
    refs={
        "c": r'''long long factorial(long long n) {
    long long result = 1;                 /* 0! = 1! = 1 */
    for (long long i = 2; i <= n; i++) {
        result *= i;                      /* fits: 18! < 2^63 */
    }
    return result;
}''',
        "cpp": r'''long long factorial(long long n) {
    long long result = 1;
    for (long long i = 2; i <= n; ++i) result *= i;
    return result;
}''',
        "rust": r'''pub fn factorial(n: i64) -> i64 {
    // (2..=n).product() would also work; an explicit loop shows the accumulator.
    let mut result: i64 = 1;
    for i in 2..=n {
        result *= i;
    }
    result
}''',
    },
    tests=[[5], [0], [1], [2], [10], [12], [13], [18]],
))

# ================================================================ 3. multiplication table (io)
PROBLEMS.append(dict(
    id="multiplication-table-grid",
    title="Multiplication Table",
    difficulty=1,
    kind="io",
    tags=["nested loops", "io", "formatting"],
    statement=r"""
Read one integer `n` from standard input and print the `n × n` multiplication table.

- Print exactly `n` lines. Line `i` (for `i = 1..n`) contains the `n` products `i×1, i×2, ..., i×n`.
- Let `w` be the number of digits in `n × n` (the largest product). Every product is
  **right-aligned in a field of width `w`** (padded on the left with spaces).
- Fields on a line are separated by **one** space.

For `n = 4`, `w = 2` (because `16` has two digits), so the output is:

```
 1  2  3  4
 2  4  6  8
 3  6  9 12
 4  8 12 16
```
""",
    constraints=["1 ≤ n ≤ 20"],
    hints=[
        "Two nested loops: the outer one picks the row `i`, the inner one the column `j`.",
        "Compute the width once before the loops: the length of the string form of `n * n`.",
        "Python: `str(x).rjust(w)` or `f\"{x:>{w}}\"`. C: `printf(\"%*d\", w, x)` reads the width from an argument.",
        "Join a row's fields with single spaces and print the row; don't print a space after the last field (trailing spaces are ignored by the checker, but it's tidier).",
    ],
    explanation=r"""
## Intuition

A table is a grid, and a grid is two nested loops: **rows outside, columns inside**. The only new
idea is formatting: every cell gets the same width so the columns line up.

## Approach

1. Read `n`.
2. `w = len(str(n * n))`, the digits in the biggest product (bottom-right corner).
3. For `i` in `1..=n`:
   - build the row from `i * j` for `j` in `1..=n`, each padded to width `w`;
   - print the cells separated by single spaces.

For `n = 3`: `w = len("9") = 1`, so no padding is needed:

```
1 2 3
2 4 6
3 6 9
```

For `n = 4`, `w = 2` and single-digit products get one leading space (`" 4"`), which is what keeps
the `12` and `16` column aligned.

**Language mechanics.** Formatted output is worth learning properly here:

```python
print(" ".join(f"{i * j:>{w}}" for j in range(1, n + 1)))   # > means right-align
```

```c
printf("%*d", w, i * j);   /* '*' takes the field width from the next argument */
```

```cpp
cout << setw(w) << i * j;  // setw applies to the NEXT output only
```

```rust
print!("{:>width$}", i * j, width = w);
```

## Complexity

- **Time:** O(n²): there are `n²` cells and each is printed once.
- **Space:** O(n) if you build a row string, O(1) if you print cell by cell.

## Common mistakes

- Computing the width from `n` instead of `n * n`: for `n = 4` the width must be 2, not 1.
- Using `setw` once in C++ and expecting it to stick: it resets after every `<<` of a value.
- Off-by-one ranges (`range(1, n)`) that drop the last row and column.
- Printing an extra space or blank line at the end of rows: harmless here (trailing whitespace is
  ignored) but sloppy, and some judges reject it.

## Going further

The table is symmetric (`i × j = j × i`). Try printing only the lower triangle (`j ≤ i`), which
is the same nested loop with the inner bound tied to the outer variable. That "inner bound depends
on outer index" shape is exactly what the triangle and diamond problems use.
""",
    solution=r'''import sys

def main():
    n = int(sys.stdin.read().split()[0])
    # Every cell is padded to the width of the largest product, which is n*n in the
    # bottom-right corner. Computing it once keeps all columns aligned.
    w = len(str(n * n))
    for i in range(1, n + 1):            # one output line per row
        cells = []
        for j in range(1, n + 1):        # one cell per column
            # rjust pads on the left with spaces up to width w (right alignment).
            cells.append(str(i * j).rjust(w))
        # A single space between cells, none after the last one.
        print(" ".join(cells))

main()
''',
    refs={
        "c": r'''#include <stdio.h>

int main(void) {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    /* Width = digits of the largest product n*n. */
    int w = 0;
    for (int big = n * n; big > 0; big /= 10) w++;
    for (int i = 1; i <= n; i++) {
        for (int j = 1; j <= n; j++) {
            if (j > 1) putchar(' ');        /* separator before every cell but the first */
            printf("%*d", w, i * j);        /* '*' = width taken from the argument list */
        }
        putchar('\n');
    }
    return 0;
}''',
        "cpp": r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    int w = to_string(n * n).size();
    for (int i = 1; i <= n; ++i) {
        for (int j = 1; j <= n; ++j) {
            if (j > 1) cout << ' ';
            cout << setw(w) << i * j;   // setw only applies to the next value
        }
        cout << '\n';
    }
}''',
        "rust": r'''use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let n: i64 = input.trim().parse().unwrap();
    let w = (n * n).to_string().len();
    for i in 1..=n {
        // Build each cell right-aligned to width w, then join with single spaces.
        let row: Vec<String> = (1..=n).map(|j| format!("{:>width$}", i * j, width = w)).collect();
        println!("{}", row.join(" "));
    }
}''',
    },
    tests=["4\n", "1\n", "3\n", "5\n", "9\n", "10\n", "12\n", "20\n"],
))

# ================================================================ 4. fixed triangle (no stdin)
PROBLEMS.append(dict(
    id="star-triangle-five",
    title="Star Triangle",
    difficulty=0,
    kind="io",
    tags=["nested loops", "io", "patterns"],
    statement=r"""
Print this right triangle of asterisks, exactly 5 lines, with no input:

```
*
**
***
****
*****
```

Line `k` (counting from 1) has exactly `k` asterisks and nothing else. Your program reads
nothing from standard input.

You *could* hard-code five `print` calls. Instead, write it with **two nested loops** so that
changing a single number would make a triangle of any height.
""",
    examples=1,
    hints=[
        "The outer loop runs once per line: `k = 1, 2, 3, 4, 5`.",
        "The inner loop prints `k` asterisks on the current line. How does its bound depend on `k`?",
        "After the inner loop, end the line (print a newline). In Python you can also build the row as `\"*\" * k`.",
    ],
    explanation=r"""
## Intuition

Look at the shape as a table: **row number → how many stars**. Row 1 has 1, row 2 has 2, ...,
row k has k. Whenever the inner count is a formula in the outer variable, you have a nested loop
whose inner bound depends on the outer index.

## Approach

```
for k in 1..=5:          # which line
    for _ in 1..=k:      # k stars on this line
        print "*" (no newline)
    print newline
```

| k | inner loop runs | output line |
|---|---|---|
| 1 | 1 | `*` |
| 2 | 2 | `**` |
| 3 | 3 | `***` |
| 4 | 4 | `****` |
| 5 | 5 | `*****` |

**Language mechanics.** The trick is printing *without* a newline inside the inner loop:

- Python: `print("*", end="")`, then a bare `print()` to finish the line. Or build the string first.
- C: `putchar('*')` then `putchar('\n')`; `printf("*")` also works.
- C++: `cout << '*'` then `cout << '\n'`.
- Rust: `print!("*")` (no newline) vs `println!()` (newline).
- ESPresso: `print` always ends the line, so build the row as a string (`row = row + "*"`) and
  print it once.

## Complexity

The number of stars is `1 + 2 + ... + h = h(h+1)/2`, so printing a height-`h` triangle is O(h²).

## Common mistakes

- Inner loop with a fixed bound (`range(5)`) instead of `k`: you get a 5×5 square.
- Forgetting the newline after each row: everything ends up on one line.
- Putting the newline *inside* the inner loop: one star per line.
- Outer loop `range(5)` starting at 0 combined with inner `range(k)`: the first line is empty.
  Either use `range(1, 6)` or print `k + 1` stars.

## Going further

Change the inner bound to `6 - k` for an upside-down triangle, or print `5 - k` spaces before the
stars for a right-aligned one. The next pattern problem (the diamond) combines both ideas.
""",
    solution=r'''HEIGHT = 5  # change this one number to draw a taller or shorter triangle

for k in range(1, HEIGHT + 1):       # k = 1..HEIGHT: the line number
    row = ""
    for _ in range(k):               # the inner bound depends on the outer variable
        row += "*"
    print(row)                       # print ends the line for us
''',
    refs={
        "c": r'''#include <stdio.h>

int main(void) {
    const int height = 5;
    for (int k = 1; k <= height; k++) {      /* one iteration per line */
        for (int s = 0; s < k; s++) {        /* k stars on line k */
            putchar('*');
        }
        putchar('\n');                       /* finish the line */
    }
    return 0;
}''',
        "cpp": r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    const int height = 5;
    for (int k = 1; k <= height; ++k) {
        for (int s = 0; s < k; ++s) cout << '*';
        cout << '\n';
    }
}''',
        "rust": r'''fn main() {
    let height = 5;
    for k in 1..=height {
        for _ in 0..k {
            print!("*");     // print! does not add a newline
        }
        println!();          // println! with no arguments just ends the line
    }
}''',
        "espresso": r'''// print() always ends the line, so build each row as a string first.
const height = 5
for var k in 1..height + 1 {
  var row = ""
  for var s in 0..k {
    row = row + "*"
  }
  print(row)
}''',
    },
    tests=["", "", "", "", "", ""],
))

# ================================================================ 5. diamond (stdin n)
PROBLEMS.append(dict(
    id="star-diamond-n",
    title="Star Diamond",
    difficulty=1,
    kind="io",
    tags=["nested loops", "io", "patterns"],
    statement=r"""
Read an integer `n` and print a diamond of asterisks whose widest row has `2n − 1` stars.

The diamond has `2n − 1` lines:

- For `i = 1, 2, ..., n` (the top half including the middle row), print `n − i` spaces followed by
  `2i − 1` asterisks.
- Then for `i = n − 1, n − 2, ..., 1` (the bottom half), print the same thing again.

Do **not** print spaces after the last asterisk on a line. For `n = 3`:

```
  *
 ***
*****
 ***
  *
```
""",
    constraints=["1 ≤ n ≤ 30"],
    example_notes=["Rows have 1, 3, 5, 3, 1 stars, indented by 2, 1, 0, 1, 2 spaces.", "A single star."],
    hints=[
        "Solve the top half first (a centred pyramid). Make a table: row i → number of spaces, number of stars.",
        "Spaces = `n - i`, stars = `2*i - 1`. Each row is two inner loops (or two repeated strings) and a newline.",
        "The bottom half is the top half without its middle row, in reverse: loop `i` from `n - 1` down to `1`.",
        "To avoid duplicating code, write a helper that prints row `i`, then call it for `1..n` and `n-1..1`.",
    ],
    explanation=r"""
## Intuition

Pattern problems are solved on paper first. Write down, for every row, how many spaces and how
many stars it has, and look for formulas in the row number. Here, for `n = 4`:

```
row i  spaces  stars
  1      3       1          *
  2      2       3         ***
  3      1       5        *****
  4      0       7       *******
  3      1       5        *****
  2      2       3         ***
  1      3       1          *
```

Spaces shrink by one and stars grow by two per step, so `spaces = n - i` and `stars = 2i - 1`.
The bottom half reuses the same formulas with `i` counting back down.

## Approach

1. Read `n`.
2. Define `row(i)` = `" " * (n - i) + "*" * (2*i - 1)`.
3. Print `row(i)` for `i = 1..n`.
4. Print `row(i)` for `i = n-1` down to `1`.

Counting down is where off-by-ones love to hide:

```python
for i in range(n - 1, 0, -1):    # n-1, n-2, ..., 1   (stop value 0 is excluded)
```

```c
for (int i = n - 1; i >= 1; i--)
```

```rust
for i in (1..n).rev() { ... }    // 1..n is 1..=n-1, reversed
```

Check `n = 1`: the top half prints one star; the bottom loop runs over `range(0, 0, -1)`, which is
empty. Correct, the diamond is a single `*`.

## Complexity

- **Time:** O(n²). Total characters printed are about `2 · (1 + 3 + 5 + ...) ≈ 2n²`.
- **Space:** O(n) for one row string (O(1) if you print character by character).

## Common mistakes

- Printing the middle row twice (bottom loop starting at `n` instead of `n - 1`).
- Trailing spaces to "pad" the right side: unnecessary, and in stricter judges, wrong. Only
  *leading* spaces shape the figure.
- `range(n, 0, -1)` vs `range(n - 1, 0, -1)` vs `range(n - 1, -1, -1)`: write out the values
  for `n = 3` before trusting any of them.
- In Rust, `(n-1..0)` is an *empty* range; descending ranges need `.rev()`.

## Going further

- A **hollow** diamond prints a star only at the first and last position of each row: the inner
  loop gets an `if`.
- The same table method handles any shape: number pyramids (`1`, `121`, `12321`), Pascal's
  triangle, checkerboards. Identify per-row counts, find the formula, then loop.
""",
    solution=r'''import sys

def main():
    n = int(sys.stdin.read().split()[0])

    def row(i):
        # Row i is indented by n - i spaces and holds 2i - 1 stars. These two formulas come
        # straight from tabulating the first few rows. No trailing spaces.
        return " " * (n - i) + "*" * (2 * i - 1)

    # Top half including the widest middle row: i = 1, 2, ..., n.
    for i in range(1, n + 1):
        print(row(i))
    # Bottom half mirrors the top but must not repeat the middle row: i = n-1, ..., 1.
    # range(n - 1, 0, -1) stops before 0, and is empty when n == 1.
    for i in range(n - 1, 0, -1):
        print(row(i))

main()
''',
    refs={
        "c": r'''#include <stdio.h>

/* Print row i of the diamond: n - i spaces, then 2i - 1 stars. */
static void row(int n, int i) {
    for (int s = 0; s < n - i; s++) putchar(' ');
    for (int s = 0; s < 2 * i - 1; s++) putchar('*');
    putchar('\n');
}

int main(void) {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    for (int i = 1; i <= n; i++) row(n, i);       /* top half + middle */
    for (int i = n - 1; i >= 1; i--) row(n, i);   /* bottom half, no repeated middle */
    return 0;
}''',
        "cpp": r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    auto row = [&](int i) {
        // string(count, ch) builds a run of identical characters.
        cout << string(n - i, ' ') << string(2 * i - 1, '*') << '\n';
    };
    for (int i = 1; i <= n; ++i) row(i);
    for (int i = n - 1; i >= 1; --i) row(i);
}''',
        "rust": r'''use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let n: usize = input.trim().parse().unwrap();
    let row = |i: usize| println!("{}{}", " ".repeat(n - i), "*".repeat(2 * i - 1));
    for i in 1..=n {
        row(i);
    }
    // (1..n) is 1..=n-1; .rev() walks it downward. Empty when n == 1.
    for i in (1..n).rev() {
        row(i);
    }
}''',
    },
    tests=["3\n", "1\n", "2\n", "4\n", "5\n", "8\n", "13\n", "30\n"],
))

# ================================================================ 6. count digits
PROBLEMS.append(dict(
    id="count-digits-loop",
    title="Count the Digits",
    difficulty=0,
    tags=["while loop", "digits"],
    fn="count_digits",
    params=[["n", "int"]],
    returns="int",
    statement=r"""
Return how many decimal digits the integer `n` has.

- The sign does not count: `-305` has 3 digits.
- `0` has **1** digit.

Use arithmetic (division by 10) in a loop rather than converting to a string.
""",
    constraints=["−2³¹ < n < 2³¹"],
    example_notes=["12345 → 1234 → 123 → 12 → 1 → 0: five divisions.", "Zero is written with one digit."],
    hints=[
        "Integer division by 10 removes the last digit: 1234 // 10 == 123.",
        "Count how many times you can remove a digit before the number becomes 0. That's a `while` loop, since you don't know the count in advance.",
        "Two edge cases: negative numbers (take the absolute value first) and 0 (the loop would run zero times, but the answer is 1).",
        "A do-while shape handles 0 naturally: remove a digit and count it, *then* check whether anything is left.",
    ],
    explanation=r"""
## Intuition

"Repeat until something runs out" is the signature of a `while` loop. Each division by 10 chops
one digit off the right end, so the number of chops until the value hits 0 is the digit count.
This **digit-peeling** loop (`n % 10` to read a digit, `n / 10` to drop it) appears in dozens of
problems.

## Approach

1. Make `n` non-negative (`n = abs(n)`); the minus sign is not a digit.
2. `count = 0`.
3. Repeat: `n //= 10`, `count += 1`, until `n == 0`. Check the condition **after** the body so
   that `0` still counts as one digit.

Trace for `n = 12345`:

| n before | n after `//10` | count |
|---|---|---|
| 12345 | 1234 | 1 |
| 1234 | 123 | 2 |
| 123 | 12 | 3 |
| 12 | 1 | 4 |
| 1 | 0 | 5 |

**Termination:** `n` is a non-negative integer that strictly shrinks each pass (for `n ≥ 1`,
`n // 10 < n`), so it must reach 0.

**Language mechanics.** Python lacks a `do { } while (cond);` loop, so write `while True:` with a
`break`. C, C++ have `do-while` built in; Rust uses `loop { ...; if cond { break; } }`.

## Complexity

- **Time:** O(d) = O(log₁₀ |n|): one iteration per digit.
- **Space:** O(1).

## Common mistakes

- A plain `while n > 0` loop returns 0 for `n = 0`.
- Forgetting negatives: `while n > 0` never runs for `-42`. Worse, in C `-42 / 10 == -4`
  (truncation toward zero), but Python's `-42 // 10 == -5` (floor), so negative peeling loops
  behave differently across languages. Take the absolute value first.
- `abs()` of the most negative 32-bit int overflows in C/C++. Crucible passes `long long`, so
  it's safe here, but remember it.

## Going further

- `len(str(abs(n)))` is the string-based one-liner; `floor(log10(n)) + 1` is the math one (beware
  floating-point error near powers of 10, and `log10(0)` is undefined).
- Reuse the peel loop to compute the digit sum, reverse a number, or test whether a number is a
  palindrome without strings.
""",
    solution=r'''def count_digits(n):
    # The minus sign isn't a digit; work with the magnitude. (In Python, negative floor
    # division rounds toward -infinity, so peeling digits off a negative number misbehaves.)
    n = abs(n)
    count = 0
    # "do-while": peel one digit, count it, and only then ask whether any remain.
    # Checking afterwards is what makes n == 0 report 1 digit instead of 0.
    while True:
        n //= 10          # drop the last decimal digit
        count += 1
        if n == 0:        # n shrinks every pass, so this is guaranteed to happen
            break
    return count
''',
    refs={
        "c": r'''long long count_digits(long long n) {
    if (n < 0) n = -n;          /* sign is not a digit; safe for 64-bit inputs in range */
    long long count = 0;
    do {                        /* body runs at least once, so 0 -> 1 digit */
        n /= 10;
        count++;
    } while (n != 0);
    return count;
}''',
        "cpp": r'''long long countDigits(long long n) {
    n = llabs(n);
    long long count = 0;
    do {
        n /= 10;
        ++count;
    } while (n != 0);
    return count;
}''',
        "rust": r'''pub fn count_digits(n: i64) -> i64 {
    let mut n = n.abs();
    let mut count = 0;
    // Rust has no do-while; `loop` + `break` expresses "check at the bottom".
    loop {
        n /= 10;
        count += 1;
        if n == 0 {
            break;
        }
    }
    count
}''',
        "espresso": r'''fn countDigits(n) {
  if n < 0 { n = -n }
  var count = 0
  while true {
    n = n / 10
    count += 1
    if n == 0 { break }
  }
  return count
}''',
    },
    tests=[[12345], [0], [7], [-305], [10], [99], [100], [-1], [1000000000], [2147483647], [-2147483647]],
))

# ================================================================ 7. collatz
PROBLEMS.append(dict(
    id="collatz-steps",
    title="Collatz Steps",
    difficulty=1,
    tags=["while loop", "simulation"],
    fn="collatz_steps",
    params=[["n", "int"]],
    returns="int",
    statement=r"""
Starting from a positive integer `n`, repeatedly apply:

- if `n` is even, `n = n / 2`;
- if `n` is odd, `n = 3n + 1`.

Return the number of steps needed to reach `1`. If `n` is already `1`, the answer is `0`.

(The *Collatz conjecture* says every starting value eventually reaches 1. Nobody has proved it,
but it has been checked far beyond the inputs here.)
""",
    constraints=["1 ≤ n ≤ 10⁵"],
    example_notes=["6 → 3 → 10 → 5 → 16 → 8 → 4 → 2 → 1: eight steps.", "Already at 1: zero steps."],
    hints=[
        "You don't know how many steps it takes in advance, so use a `while` loop with the condition `n != 1`.",
        "Inside the loop, decide even/odd with `n % 2 == 0`, update `n`, and add one to a counter.",
        "The counter counts *transitions*, not values visited: for n = 1 the loop body never runs.",
    ],
    explanation=r"""
## Intuition

This is a **simulation**: the statement literally gives you the rule, and the loop applies it until
a stop condition holds. "Until `n` reaches 1" with an unknown number of iterations means `while`.

## Approach

```
steps = 0
while n != 1:
    n = n / 2 if n is even else 3n + 1
    steps += 1
return steps
```

Trace for `n = 6`:

| step | n |
|---|---|
| 0 | 6 |
| 1 | 3 |
| 2 | 10 |
| 3 | 5 |
| 4 | 16 |
| 5 | 8 |
| 6 | 4 |
| 7 | 2 |
| 8 | 1 |

Invariant: `steps` equals the number of rule applications performed so far, and `n` is the current
value. When the loop exits, `n == 1`, so `steps` is the answer.

**Termination** is the fascinating part: there is no known proof that this loop always stops! It
does for every `n` ever tested (all values up to about 2⁶⁸), so it is safe for the inputs here.
Usually you should be able to name a quantity that strictly decreases; here `n` goes up and down.

## Complexity

- **Time:** O(number of steps). For `n ≤ 10⁵` the longest chain is 350 steps (from `77031`).
- **Space:** O(1).

## Common mistakes

- Counting values visited instead of steps (off by one: answering 9 for `n = 6`).
- Using `/` in Python (`6 / 2 == 3.0`, a float). Use `//` for integer halving.
- Overflow: intermediate values climb well above `n`. Starting below 10⁵, the peak is about
  1.57 × 10⁹, which fits a signed 32-bit int with little room. For larger inputs use 64-bit
  integers.
- ESPresso has no `%`: test evenness with `n - (n / 2) * 2 == 0`.

## Going further

- Find the starting value under one million with the longest chain (Project Euler 14). A cache of
  already-computed chain lengths ("memoization") makes it dramatically faster.
- Bit tricks: `n & 1` tests oddness and `n >> 1` halves, both a single CPU instruction.
""",
    solution=r'''def collatz_steps(n):
    steps = 0
    # The loop runs until we reach 1; we cannot know how many steps that is in advance,
    # which is exactly when a while loop beats a for loop.
    while n != 1:
        if n % 2 == 0:
            n //= 2          # integer halving; '/' would produce a float in Python
        else:
            n = 3 * n + 1
        steps += 1           # one rule application = one step
    # n == 1 here, and steps counted every transition (0 if we started at 1).
    return steps
''',
    refs={
        "c": r'''long long collatz_steps(long long n) {
    long long steps = 0;
    while (n != 1) {
        if (n % 2 == 0) n /= 2;
        else n = 3 * n + 1;     /* 64-bit: no overflow for these inputs */
        steps++;
    }
    return steps;
}''',
        "cpp": r'''long long collatzSteps(long long n) {
    long long steps = 0;
    while (n != 1) {
        n = (n % 2 == 0) ? n / 2 : 3 * n + 1;
        ++steps;
    }
    return steps;
}''',
        "rust": r'''pub fn collatz_steps(mut n: i64) -> i64 {
    // `mut n` in the signature lets us reuse the parameter as the loop variable.
    let mut steps = 0;
    while n != 1 {
        n = if n % 2 == 0 { n / 2 } else { 3 * n + 1 };
        steps += 1;
    }
    steps
}''',
        "espresso": r'''fn collatzSteps(n) {
  var steps = 0
  while n != 1 {
    // No % operator: n is even exactly when n - (n / 2) * 2 == 0.
    if n - (n / 2) * 2 == 0 {
      n = n / 2
    } else {
      n = 3 * n + 1
    }
    steps += 1
  }
  return steps
}''',
    },
    tests=[[6], [1], [2], [3], [7], [27], [97], [871], [77031], [100000]],
))

# ================================================================ 8. fibonacci
PROBLEMS.append(dict(
    id="fibonacci-iterative",
    title="Nth Fibonacci Number",
    difficulty=1,
    tags=["loop", "rolling variables"],
    fn="fibonacci",
    params=[["n", "int"]],
    returns="int",
    statement=r"""
The Fibonacci sequence is `F(0) = 0`, `F(1) = 1`, and `F(k) = F(k − 1) + F(k − 2)` for `k ≥ 2`:

`0, 1, 1, 2, 3, 5, 8, 13, 21, ...`

Return `F(n)`. Use a loop that keeps only the last two values; do not use recursion.
""",
    constraints=["0 ≤ n ≤ 78"],
    example_notes=["F(10) = 55.", "F(0) = 0 by definition."],
    hints=[
        "Each term needs only the two before it. Keep two variables, `a` (the older) and `b` (the newer).",
        "One step slides the window forward: the new pair is `(b, a + b)`.",
        "Start with `a = F(0) = 0`, `b = F(1) = 1`. After `n` slides, `a` holds `F(n)`.",
        "Beware the update order in languages without tuple assignment: compute `a + b` into a temporary before overwriting `a`.",
    ],
    explanation=r"""
## Intuition

The definition is recursive, but writing it as recursion (`fib(n-1) + fib(n-2)`) recomputes the
same values exponentially many times. Notice instead that to step forward you only need the
**last two** terms. Keep them in two variables and slide that two-element window along the
sequence: this is the **rolling variables** pattern, the seed of dynamic programming.

## Approach

```
a, b = 0, 1          # (F(0), F(1))
repeat n times:
    a, b = b, a + b  # (F(k), F(k+1)) -> (F(k+1), F(k+2))
return a
```

Invariant: after `k` iterations, `a == F(k)` and `b == F(k+1)`. After `n` iterations `a == F(n)`.

Trace for `n = 6`:

| iteration | a | b |
|---|---|---|
| 0 | 0 | 1 |
| 1 | 1 | 1 |
| 2 | 1 | 2 |
| 3 | 2 | 3 |
| 4 | 3 | 5 |
| 5 | 5 | 8 |
| 6 | 8 | 13 |

`F(6) = 8`.

**Language mechanics.** Python's `a, b = b, a + b` evaluates the whole right-hand side *before*
assigning, so it is safe. In C you need a temporary:

```c
long long next = a + b;
a = b;
b = next;
```

Writing `a = b; b = a + b;` is the classic bug: by the second line `a` already changed, so you
compute `2b`.

## Complexity

- **Time:** O(n), one addition per step.
- **Space:** O(1). The naive recursion is O(φⁿ) ≈ O(1.618ⁿ) time: `fib(78)` would take longer than
  you're willing to wait.

## Common mistakes

- Returning `b` instead of `a` (gives `F(n+1)`).
- Special-casing `n = 0` and `n = 1` and getting one of them wrong. With the invariant above, no
  special cases are needed.
- Overflow: `F(47)` exceeds 32 bits and `F(93)` exceeds signed 64 bits. This problem stops at
  `F(78)`, the largest Fibonacci number below 2⁵³ (the largest integer a JavaScript double can hold
  exactly).

## Going further

- The matrix identity `[[1,1],[1,0]]ⁿ = [[F(n+1),F(n)],[F(n),F(n-1)]]` plus fast exponentiation
  computes `F(n)` in O(log n) multiplications.
- "Climbing stairs" (ways to climb `n` steps taking 1 or 2 at a time) is Fibonacci in disguise,
  and the classic first dynamic-programming problem.
""",
    solution=r'''def fibonacci(n):
    # a and b are a sliding window over the sequence: (a, b) == (F(k), F(k+1)).
    # Initially k = 0, so the window is (F(0), F(1)) = (0, 1).
    a, b = 0, 1
    for _ in range(n):
        # Slide the window one step. Python evaluates the right side completely before
        # assigning, so the old 'a' is used in 'a + b' (no temporary needed).
        a, b = b, a + b
    # After n slides, k == n, so a == F(n). No special case for n = 0 or 1.
    return a
''',
    refs={
        "c": r'''long long fibonacci(long long n) {
    long long a = 0, b = 1;            /* (F(k), F(k+1)) with k = 0 */
    for (long long i = 0; i < n; i++) {
        long long next = a + b;        /* save before overwriting a */
        a = b;
        b = next;
    }
    return a;
}''',
        "cpp": r'''long long fibonacci(long long n) {
    long long a = 0, b = 1;
    for (long long i = 0; i < n; ++i) {
        // tie(a, b) = make_pair(b, a + b); is the C++ tuple-assignment equivalent.
        long long next = a + b;
        a = b;
        b = next;
    }
    return a;
}''',
        "rust": r'''pub fn fibonacci(n: i64) -> i64 {
    let (mut a, mut b) = (0i64, 1i64);
    for _ in 0..n {
        // Tuple assignment: the right side is fully evaluated first.
        (a, b) = (b, a + b);
    }
    a
}''',
    },
    tests=[[10], [0], [1], [2], [3], [20], [46], [47], [70], [78]],
))

# ================================================================ 9. sum of evens in range
PROBLEMS.append(dict(
    id="sum-evens-in-range",
    title="Sum of Evens in a Range",
    difficulty=0,
    tags=["loop", "modulo"],
    fn="sum_evens_in_range",
    params=[["lo", "int"], ["hi", "int"]],
    returns="int",
    statement=r"""
Return the sum of all **even** integers `x` with `lo ≤ x ≤ hi` (both ends included).

Negative numbers can be even too: `-4`, `-2` and `0` are all even. If there are no even numbers in
the range, return `0`.
""",
    constraints=["−10⁴ ≤ lo ≤ hi ≤ 10⁴"],
    example_notes=["2 + 4 + 6 + 8 + 10 = 30.", "−4 + −2 + 0 + 2 = −4."],
    hints=[
        "Loop over every integer from `lo` to `hi` inclusive and add the ones that are even.",
        "`x % 2 == 0` tests evenness. In C, `-3 % 2 == -1`, so compare with `0` rather than testing `== 1` for odd.",
        "Faster: find the first even number ≥ lo, then step by 2.",
    ],
    explanation=r"""
## Intuition

"Sum the items that satisfy a condition" is the sum accumulator with a **filter**: loop over
candidates, and only add those passing the test.

## Approach

Simple version:

```python
total = 0
for x in range(lo, hi + 1):   # inclusive of hi
    if x % 2 == 0:
        total += x
```

Stepping version (half the iterations): start at the first even number `≥ lo` and go up by 2.

```python
start = lo if lo % 2 == 0 else lo + 1
for x in range(start, hi + 1, 2):
    total += x
```

Trace for `lo = -5, hi = 3`: `-5` is odd, so start at `-4`; visit `-4, -2, 0, 2`; total `-4`.

## Complexity

- **Time:** O(hi − lo), with the stepping version doing half as many iterations.
- **Space:** O(1).

## Common mistakes

- **Modulo of negatives differs by language.** Python's `%` takes the sign of the divisor
  (`-3 % 2 == 1`), C/C++/Rust take the sign of the dividend (`-3 % 2 == -1`). Testing
  `x % 2 == 1` for "odd" therefore fails for negative odds in C. Testing `x % 2 == 0` for "even"
  works everywhere, because an even number's remainder is 0 in both conventions.
- Excluding `hi`: `range(lo, hi)` misses it when `hi` is even.
- In the stepping version, starting at `lo` without checking parity sums all the odds instead.

## Going further

Closed form: if `a` is the first even ≥ lo and `b` the last even ≤ hi, the evens form an
arithmetic sequence with `k = (b - a)/2 + 1` terms, so the sum is `k(a + b)/2`, which is O(1).
""",
    solution=r'''def sum_evens_in_range(lo, hi):
    total = 0
    # Python's % never returns a negative result for a positive divisor, so lo % 2 is
    # 0 for even and 1 for odd even when lo is negative. Bump an odd lo up to the next even.
    start = lo if lo % 2 == 0 else lo + 1
    # Step by 2 through the evens only; hi + 1 because range excludes its end. If
    # start > hi (e.g. lo == hi == odd), the range is empty and total stays 0.
    for x in range(start, hi + 1, 2):
        total += x
    return total
''',
    refs={
        "c": r'''long long sum_evens_in_range(long long lo, long long hi) {
    long long total = 0;
    for (long long x = lo; x <= hi; x++) {
        /* In C, -3 % 2 == -1, but even numbers always give 0, so this test is safe. */
        if (x % 2 == 0) total += x;
    }
    return total;
}''',
        "cpp": r'''long long sumEvensInRange(long long lo, long long hi) {
    long long total = 0;
    // Round lo up to an even number. lo % 2 is 0 or +/-1 in C++, so test != 0.
    long long start = (lo % 2 == 0) ? lo : lo + 1;
    for (long long x = start; x <= hi; x += 2) total += x;
    return total;
}''',
        "rust": r'''pub fn sum_evens_in_range(lo: i64, hi: i64) -> i64 {
    // rem_euclid always returns a non-negative remainder, like Python's %.
    let start = if lo.rem_euclid(2) == 0 { lo } else { lo + 1 };
    // step_by walks the range in strides of 2; empty if start > hi.
    (start..=hi).step_by(2).sum()
}''',
        "espresso": r'''fn sumEvensInRange(lo, hi) {
  var total = 0
  for var x in lo..hi + 1 {
    // x - (x / 2) * 2 is the remainder; it is 0 for every even x, negative or not.
    if x - (x / 2) * 2 == 0 {
      total += x
    }
  }
  return total
}''',
    },
    tests=[[1, 10], [-5, 3], [3, 3], [4, 4], [-7, -7], [-10, -1], [0, 0], [-10000, 10000], [1, 10000], [-9999, -1]],
))

# ================================================================ 10. count pairs (nested)
_r = _rng(310)
_pairs_big = [_r.randint(-20, 20) for _ in range(40)]
PROBLEMS.append(dict(
    id="count-pairs-with-sum",
    title="Count Pairs with a Given Sum",
    difficulty=1,
    tags=["nested loops", "pairs"],
    fn="count_pairs_with_sum",
    params=[["nums", "int[]"], ["target", "int"]],
    returns="int",
    statement=r"""
Given an array `nums` and an integer `target`, return the number of index pairs `(i, j)` with
`i < j` and `nums[i] + nums[j] == target`.

Pairs are about **positions**, not values: if the same value appears several times, each pair of
positions counts separately. An element is never paired with itself.

Use nested loops; `n` is small.
""",
    constraints=["0 ≤ len(nums) ≤ 300", "−100 ≤ nums[i] ≤ 100", "−200 ≤ target ≤ 200"],
    example_notes=["Pairs (0,3): 1+5 and (1,2): 2+4.", "All three pairs of positions (0,1), (0,2), (1,2) sum to 4."],
    hints=[
        "Check every pair of positions. The outer loop picks `i`; what range should the inner `j` cover so each pair is seen once?",
        "Start `j` at `i + 1`. That enforces `i < j`, so you never pair an element with itself or count (i, j) and (j, i) twice.",
        "With `n` elements there are `n(n−1)/2` pairs. For n = 300 that's about 45 000 checks: fine.",
    ],
    explanation=r"""
## Intuition

"How many pairs" with small input is the textbook nested loop. The subtle part is making sure
each unordered pair is counted **exactly once**. Starting the inner loop at `i + 1` does it: it
visits only the upper triangle of the `n × n` grid of (i, j) combinations.

```
      j: 0 1 2 3
  i=0    . x x x
  i=1    . . x x        x = visited (i < j)
  i=2    . . . x
  i=3    . . . .
```

## Approach

```
count = 0
for i in 0..n:
    for j in i+1..n:
        if nums[i] + nums[j] == target:
            count += 1
```

Trace for `nums = [1, 2, 4, 5]`, `target = 6`:

| (i, j) | sum | match? |
|---|---|---|
| (0,1) | 3 | |
| (0,2) | 5 | |
| (0,3) | 6 | ✓ |
| (1,2) | 6 | ✓ |
| (1,3) | 7 | |
| (2,3) | 9 | |

Answer: 2.

## Complexity

- **Time:** O(n²): exactly `n(n−1)/2` pair checks.
- **Space:** O(1).

## Common mistakes

- Inner loop from `0`: every pair is counted twice, and `(i, i)` pairs sneak in (e.g. `3 + 3`
  for target 6 when there's only one 3).
- Inner loop from `i` instead of `i + 1`: pairs an element with itself.
- Dividing a double count by 2 to "fix" an inner loop starting at 0: still wrong because of the
  self-pairs.
- Empty or single-element arrays: the loops simply don't run, so the answer 0 falls out.

## Going further

This becomes O(n) with a hash map: scan left to right, and for each `x` add
`seen[target - x]` to the answer before recording `x` in `seen`. You'll meet this "complement
lookup" idea again in Two Sum. Recognising that nested loops compute something a hash map can
answer is one of the most valuable speed-ups in interview problems.
""",
    solution=r'''def count_pairs_with_sum(nums, target):
    n = len(nums)
    count = 0
    for i in range(n):
        # j starts at i + 1: this enforces i < j, so each unordered pair of positions is
        # examined exactly once and no element is paired with itself.
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                count += 1
    # Empty or one-element input: the inner loop never runs, count stays 0.
    return count
''',
    refs={
        "c": r'''long long count_pairs_with_sum(long long* nums, int numsSize, long long target) {
    long long count = 0;
    for (int i = 0; i < numsSize; i++) {
        for (int j = i + 1; j < numsSize; j++) {   /* upper triangle only */
            if (nums[i] + nums[j] == target) count++;
        }
    }
    return count;
}''',
        "cpp": r'''long long countPairsWithSum(vector<long long>& nums, long long target) {
    long long count = 0;
    size_t n = nums.size();
    for (size_t i = 0; i < n; ++i)
        for (size_t j = i + 1; j < n; ++j)
            if (nums[i] + nums[j] == target) ++count;
    return count;
}''',
        "rust": r'''pub fn count_pairs_with_sum(nums: Vec<i64>, target: i64) -> i64 {
    let n = nums.len();
    let mut count = 0;
    for i in 0..n {
        // i + 1..n is empty when i == n - 1, so no bounds issues.
        for j in i + 1..n {
            if nums[i] + nums[j] == target {
                count += 1;
            }
        }
    }
    count
}''',
        "espresso": r'''fn countPairsWithSum(nums, target) {
  var n = len(nums)
  var count = 0
  for var i in 0..n {
    for var j in i + 1..n {
      if nums[i] + nums[j] == target {
        count += 1
      }
    }
  }
  return count
}''',
    },
    tests=[
        [[1, 2, 4, 5], 6],
        [[2, 2, 2], 4],
        [[], 0],
        [[3], 6],
        [[3, 3], 6],
        [[1, -1, 0, 0, 2, -2], 0],
        [[5, 1, 7], 100],
        [[0] * 12, 0],
        [_pairs_big, 7],
        [_pairs_big, -15],
    ],
))

# ================================================================ 11. running max (in place)
_r = _rng(311)
PROBLEMS.append(dict(
    id="running-max-in-place",
    title="Running Maximum",
    difficulty=0,
    tags=["array", "prefix", "in-place"],
    fn="running_max",
    params=[["nums", "int[]"]],
    returns="void",
    mutates="nums",
    statement=r"""
Replace every element of `nums` **in place** with the largest value seen from the start of the
array up to and including that position:

`nums[i]` becomes `max(nums[0], nums[1], ..., nums[i])`.

The function returns nothing; the array itself is the output. An empty array stays empty.
""",
    constraints=["0 ≤ len(nums) ≤ 10⁴", "−10⁶ ≤ nums[i] ≤ 10⁶"],
    example_notes=["After 3 comes 1 (max stays 3), then 4 (new max), 1 (stays 4), 5 (new max).", "A decreasing array: the first element dominates everything."],
    hints=[
        "Keep a variable holding the maximum so far. Each element either beats it or doesn't.",
        "Walk left to right. After updating the max with `nums[i]`, write the max back into `nums[i]`.",
        "Even simpler: `nums[i] = max(nums[i], nums[i - 1])` for i ≥ 1, because `nums[i - 1]` already holds the running max.",
    ],
    explanation=r"""
## Intuition

"Something about everything up to position `i`" is a **prefix** computation. You don't need to
rescan the prefix each time: the answer at `i` is the answer at `i − 1` combined with one new
element. That turns an O(n²) idea into a single O(n) pass.

## Approach

Because we overwrite in place, once position `i − 1` is processed it already *contains* the
running max. So:

```
for i in 1..n:
    if nums[i - 1] > nums[i]:
        nums[i] = nums[i - 1]
```

Trace for `[3, 1, 4, 1, 5, 2]`:

| i | before | nums[i-1] | after |
|---|---|---|---|
| 0 | 3 | n/a | 3 |
| 1 | 1 | 3 | 3 |
| 2 | 4 | 3 | 4 |
| 3 | 1 | 4 | 4 |
| 4 | 5 | 4 | 5 |
| 5 | 2 | 5 | 5 |

Invariant: before iteration `i`, `nums[0..i-1]` already holds the running maxima of the original
values, and `nums[i..]` is untouched.

**Language mechanics.** "In place" means you modify the caller's array, not a copy. Python lists,
C pointers, C++ `vector<long long>&` (note the `&`), and Rust `&mut Vec<i64>` all let you do that.
Without the `&` in C++ you'd modify a copy and the caller would see no change.

## Complexity

- **Time:** O(n).
- **Space:** O(1) extra: we reuse the input.

## Common mistakes

- Starting at `i = 0` and reading `nums[-1]`: in Python that's the *last* element (silent bug); in
  C it's out of bounds (undefined behaviour); in Rust `0 - 1` on `usize` panics.
- Initialising a separate `best = 0`: wrong when all numbers are negative.
- Recomputing `max(nums[:i+1])` each step: correct but O(n²).

## Going further

The same one-pass prefix idea computes prefix sums (`nums[i] += nums[i-1]`), prefix minimums, and
"best time to buy and sell stock" (track the minimum price so far, compare with today's price).
""",
    solution=r'''def running_max(nums):
    # Position 0's running max is just itself, so start at 1. range(1, 0) and range(1, 1)
    # are empty, which handles empty and one-element arrays for free.
    for i in range(1, len(nums)):
        # nums[i - 1] has already been overwritten with max(original nums[0..i-1]),
        # so comparing against it alone is enough. This is the prefix invariant.
        if nums[i - 1] > nums[i]:
            nums[i] = nums[i - 1]
    # Nothing to return: the caller's list was modified in place.
''',
    refs={
        "c": r'''void running_max(long long* nums, int numsSize) {
    for (int i = 1; i < numsSize; i++) {      /* i = 1: nums[0] is already its own max */
        if (nums[i - 1] > nums[i]) nums[i] = nums[i - 1];
    }
}''',
        "cpp": r'''void runningMax(vector<long long>& nums) {   // & : modify the caller's vector
    for (size_t i = 1; i < nums.size(); ++i)
        nums[i] = max(nums[i], nums[i - 1]);
}''',
        "rust": r'''pub fn running_max(nums: &mut Vec<i64>) {
    for i in 1..nums.len() {        // 1..0 is simply empty, no underflow
        if nums[i - 1] > nums[i] {
            nums[i] = nums[i - 1];
        }
    }
}''',
        "espresso": r'''fn runningMax(nums) {
  for var i in 1..len(nums) {
    if nums[i - 1] > nums[i] {
      nums[i] = nums[i - 1]
    }
  }
}''',
    },
    tests=[
        [[3, 1, 4, 1, 5, 2]],
        [[9, 7, 5, 3]],
        [[]],
        [[42]],
        [[-5, -3, -10, -1]],
        [[1, 2, 3, 4, 5]],
        [[2, 2, 2]],
        [[_r.randint(-10**6, 10**6) for _ in range(60)]],
    ],
))

# ================================================================ 12. count occurrences
_r = _rng(312)
PROBLEMS.append(dict(
    id="count-occurrences-of-value",
    title="Count Occurrences",
    difficulty=0,
    tags=["array", "counting"],
    fn="count_occurrences",
    params=[["nums", "int[]"], ["x", "int"]],
    returns="int",
    statement=r"""
Return how many times the value `x` appears in the array `nums`.
""",
    constraints=["0 ≤ len(nums) ≤ 10⁴", "−10⁶ ≤ nums[i], x ≤ 10⁶"],
    example_notes=["2 appears at positions 1, 3 and 4.", "An empty array contains nothing."],
    hints=[
        "This is the counting pattern: a counter that starts at 0 and goes up by one whenever a condition holds.",
        "Visit each element once and compare it with `x`.",
    ],
    explanation=r"""
## Intuition

The **count accumulator**: `count = 0`, then `count += 1` for each element passing a test. It is the
sum accumulator where every qualifying element contributes `1`.

## Approach

```
count = 0
for v in nums:
    if v == x:
        count += 1
return count
```

Trace for `nums = [1, 2, 3, 2, 2]`, `x = 2`: matches at indices 1, 3, 4, so `count` goes
0 → 1 → 2 → 3.

**Language mechanics.** Python's `for v in nums` iterates over *values*; C's
`for (int i = 0; i < n; i++)` iterates over *indices* and reads `nums[i]`. Rust offers both
(`for &v in &nums` or `for i in 0..nums.len()`); iterating values avoids index bugs entirely.
In C the array arrives as a pointer plus a separate length (`numsSize`): the pointer alone does not
know how long the array is.

## Complexity

- **Time:** O(n), one comparison per element. You can't do better on unsorted data: any element
  you skip might be `x`.
- **Space:** O(1).

## Common mistakes

- In C, looping `i <= numsSize` reads one element past the end (undefined behaviour).
- Returning early on the first match (that's "contains", not "count").

## Going further

- Python's `nums.count(x)`, C++'s `std::count`, and Rust's `iter().filter(..).count()` do exactly
  this loop.
- On a **sorted** array, two binary searches (first and last position of `x`) give the count in
  O(log n).
- Counting *every* value at once is a frequency table (a hash map), a key tool in the Hashing
  track.
""",
    solution=r'''def count_occurrences(nums, x):
    count = 0
    # Iterate over values directly; we never need the index, so we can't get it wrong.
    for v in nums:
        if v == x:
            count += 1   # each match contributes exactly one
    return count
''',
    refs={
        "c": r'''long long count_occurrences(long long* nums, int numsSize, long long x) {
    long long count = 0;
    for (int i = 0; i < numsSize; i++) {   /* < not <=: valid indices are 0..numsSize-1 */
        if (nums[i] == x) count++;
    }
    return count;
}''',
        "cpp": r'''long long countOccurrences(vector<long long>& nums, long long x) {
    long long count = 0;
    for (long long v : nums)        // range-for: iterate over values
        if (v == x) ++count;
    return count;                   // or: return count(nums.begin(), nums.end(), x);
}''',
        "rust": r'''pub fn count_occurrences(nums: Vec<i64>, x: i64) -> i64 {
    let mut count = 0;
    for v in nums {                 // consumes the Vec, yielding each value
        if v == x {
            count += 1;
        }
    }
    count
}''',
        "espresso": r'''fn countOccurrences(nums, x) {
  var count = 0
  for var i in 0..len(nums) {
    if nums[i] == x { count += 1 }
  }
  return count
}''',
    },
    tests=[
        [[1, 2, 3, 2, 2], 2],
        [[], 5],
        [[5], 5],
        [[5], 6],
        [[7, 7, 7, 7], 7],
        [[-1, 1, -1, 1], -1],
        [[0, 0, 1], 2],
        [[_r.randint(0, 9) for _ in range(60)], 3],
        [[_r.randint(-10**6, 10**6) for _ in range(30)] + [123456] * 4, 123456],
    ],
))

# ================================================================ 13. power of two by loop
PROBLEMS.append(dict(
    id="power-of-two-loop",
    title="Power of Two (Loop)",
    difficulty=0,
    tags=["while loop", "math"],
    fn="is_power_of_two",
    params=[["n", "int"]],
    returns="bool",
    statement=r"""
Return `true` if `n` is a power of two, i.e. `n == 2^k` for some integer `k ≥ 0`, and `false`
otherwise.

`1 = 2⁰` is a power of two. Zero and negative numbers are not.

Solve it with a loop that repeatedly divides by 2.
""",
    constraints=["−2²⁴ ≤ n ≤ 2²⁴"],
    example_notes=["16 = 2⁴.", "6 = 2 × 3 has an odd factor 3."],
    hints=[
        "Handle `n ≤ 0` first: none of them are powers of two.",
        "While `n` is even, halve it. What must be left at the end if `n` was a power of two?",
        "A power of two halves all the way down to exactly 1. Anything else gets stuck at an odd number greater than 1.",
    ],
    explanation=r"""
## Intuition

A power of two is `2 × 2 × ... × 2`: it has no odd factor except 1. So strip out every factor of
2 by halving while the number is even. If what remains is 1, nothing else was ever in there.

## Approach

1. If `n ≤ 0`, return `false`.
2. While `n` is even, `n //= 2`.
3. Return `n == 1`.

Traces:

| n | halvings | remains | answer |
|---|---|---|---|
| 16 | 16 → 8 → 4 → 2 → 1 | 1 | true |
| 6 | 6 → 3 | 3 | false |
| 1 | (none) | 1 | true |
| 40 | 40 → 20 → 10 → 5 | 5 | false |

**Termination:** each halving strictly decreases a positive `n`, and the loop stops as soon as `n`
is odd (which includes 1). The guard `n ≤ 0` matters: `0` is even and `0 // 2 == 0`, so without
it the loop would spin forever.

## Complexity

- **Time:** O(log n): at most 24 halvings for these inputs.
- **Space:** O(1).

## Common mistakes

- **Infinite loop on 0.** The guard above is not optional.
- Returning `true` for `n = 0` or negative powers like `-8`.
- Testing `n % 2 == 1` for oddness: false for negative odds in C (`-3 % 2 == -1`). The guard rules
  out negatives here, but be wary.

## Going further

The bit trick: a positive power of two has exactly one `1` bit, and `n & (n − 1)` clears the lowest
set bit, so `n > 0 && (n & (n - 1)) == 0` decides it in O(1). For example `8 = 1000₂`,
`7 = 0111₂`, `8 & 7 = 0`. Rust has `n.count_ones() == 1` and C++20 has `std::has_single_bit`.
""",
    solution=r'''def is_power_of_two(n):
    # Zero and negatives are never 2^k. This guard also prevents an infinite loop:
    # 0 is even and 0 // 2 == 0, so the halving loop below would never end.
    if n <= 0:
        return False
    # Remove every factor of 2. Each pass strictly shrinks n, and we stop at the first odd value.
    while n % 2 == 0:
        n //= 2
    # Only a pure power of two reduces all the way to 1; anything else leaves an odd factor > 1.
    return n == 1
''',
    refs={
        "c": r'''bool is_power_of_two(long long n) {
    if (n <= 0) return false;        /* also prevents looping forever on 0 */
    while (n % 2 == 0) n /= 2;       /* strip factors of two */
    return n == 1;
}''',
        "cpp": r'''bool isPowerOfTwo(long long n) {
    if (n <= 0) return false;
    while (n % 2 == 0) n /= 2;
    return n == 1;
}''',
        "rust": r'''pub fn is_power_of_two(mut n: i64) -> bool {
    if n <= 0 {
        return false;
    }
    while n % 2 == 0 {
        n /= 2;
    }
    n == 1
}''',
        "espresso": r'''fn isPowerOfTwo(n) {
  if n <= 0 { return false }
  // Halve while even; n - (n / 2) * 2 is n mod 2.
  while n - (n / 2) * 2 == 0 {
    n = n / 2
  }
  return n == 1
}''',
    },
    tests=[[16], [6], [1], [0], [-8], [2], [3], [1024], [1023], [96], [8388608], [8388609], [16777216], [-16777216]],
))

# ================================================================ 14. steps to zero
PROBLEMS.append(dict(
    id="steps-to-reduce-to-zero",
    title="Steps to Reduce a Number to Zero",
    difficulty=0,
    tags=["while loop", "simulation"],
    fn="steps_to_zero",
    params=[["n", "int"]],
    returns="int",
    statement=r"""
Given a non-negative integer `n`, count the steps needed to reduce it to `0`, where one step is:

- if `n` is even, divide it by 2;
- if `n` is odd, subtract 1.

If `n` is already `0`, the answer is `0`.
""",
    constraints=["0 ≤ n ≤ 10⁷"],
    example_notes=["14 → 7 → 6 → 3 → 2 → 1 → 0: six steps.", "Already zero."],
    hints=[
        "Loop `while n > 0`, applying one rule per iteration and counting.",
        "Evenness: `n % 2 == 0`. Make sure you don't divide 0 (the loop condition already prevents it).",
        "Each step at least halves the number every two steps, so the loop is fast even for 10⁷.",
    ],
    explanation=r"""
## Intuition

Another direct simulation: the rule is given, the stop condition (`n == 0`) is given, and the number
of steps is unknown, so a `while` loop with a counter.

## Approach

```
steps = 0
while n > 0:
    n = n / 2 if even else n - 1
    steps += 1
```

Trace for `n = 14`:

| step | n | rule |
|---|---|---|
| 0 | 14 | |
| 1 | 7 | even → /2 |
| 2 | 6 | odd → −1 |
| 3 | 3 | even → /2 |
| 4 | 2 | odd → −1 |
| 5 | 1 | even → /2 |
| 6 | 0 | odd → −1 |

**Termination:** every step strictly decreases a positive `n` (halving a positive even number or
subtracting 1), so `n` reaches 0.

## Complexity

- **Time:** O(log n). An odd step is always followed by an even (halving) step, so the value at
  least halves every two steps: at most about `2 log₂ n` iterations (≈ 46 for 10⁷).
- **Space:** O(1).

## Common mistakes

- Counting before checking (answering 1 for `n = 0`).
- Using `/` in Python, which produces floats (`7 / 2 == 3.5`), and then the loop never hits an
  exact 0 the way you expect.

## Going further

In binary, halving is "drop the last bit" and subtracting 1 from an odd number is "clear the last
bit". So each `1` bit costs one subtraction, and every bit position except the highest costs one
halving: `steps = popcount(n) + bit_length(n) − 1` for `n > 0`. For 14 = `1110₂`: 3 + 4 − 1 = 6.
That's an O(1) answer using `bin(n).count("1")` or `__builtin_popcountll`.
""",
    solution=r'''def steps_to_zero(n):
    steps = 0
    # Stop as soon as n hits 0. For n == 0 the body never runs and we return 0.
    while n > 0:
        if n % 2 == 0:
            n //= 2      # even: halve (// keeps it an int)
        else:
            n -= 1       # odd: subtract one, which makes it even
        steps += 1       # n strictly decreased, so the loop is guaranteed to end
    return steps
''',
    refs={
        "c": r'''long long steps_to_zero(long long n) {
    long long steps = 0;
    while (n > 0) {
        if (n % 2 == 0) n /= 2;
        else n -= 1;
        steps++;
    }
    return steps;
}''',
        "cpp": r'''long long stepsToZero(long long n) {
    long long steps = 0;
    for (; n > 0; ++steps)             // a for loop with no init, just test and update
        n = (n % 2 == 0) ? n / 2 : n - 1;
    return steps;
}''',
        "rust": r'''pub fn steps_to_zero(mut n: i64) -> i64 {
    let mut steps = 0;
    while n > 0 {
        n = if n % 2 == 0 { n / 2 } else { n - 1 };
        steps += 1;
    }
    steps
}''',
        "espresso": r'''fn stepsToZero(n) {
  var steps = 0
  while n > 0 {
    if n - (n / 2) * 2 == 0 {
      n = n / 2
    } else {
      n -= 1
    }
    steps += 1
  }
  return steps
}''',
    },
    tests=[[14], [0], [1], [2], [8], [123], [1023], [1024], [8388607], [9999999], [10000000]],
))

# ================================================================ 15. digital root
PROBLEMS.append(dict(
    id="digital-root-loop",
    title="Digital Root",
    difficulty=1,
    tags=["nested loops", "digits"],
    fn="digital_root",
    params=[["n", "int"]],
    returns="int",
    statement=r"""
Given a non-negative integer `n`, repeatedly replace it with the sum of its decimal digits until
it has a single digit, and return that digit.

For example `9875 → 9+8+7+5 = 29 → 2+9 = 11 → 1+1 = 2`, so the answer is `2`.

Single-digit inputs (including `0`) are returned unchanged.
""",
    constraints=["0 ≤ n ≤ 10⁷"],
    example_notes=["9875 → 29 → 11 → 2.", "Already a single digit."],
    hints=[
        "Break it into two loops: an inner loop that computes the digit sum of a number, and an outer loop that keeps going while the number has 2+ digits.",
        "Digit sum: `while n > 0: s += n % 10; n //= 10`.",
        "The outer condition is `n >= 10`.",
        "Look up the O(1) formula afterwards: it's related to `n % 9`.",
    ],
    explanation=r"""
## Intuition

Two repetitions are nested here: *summing digits* (repeat over the digits of one number) and
*repeating the digit sum* (repeat until single-digit). Two `while` loops, one inside the other.
Neither has a known count in advance.

## Approach

```
while n >= 10:              # more than one digit left
    s = 0
    while n > 0:            # peel every digit off n
        s += n % 10
        n //= 10
    n = s
return n
```

Trace for `n = 9875`:

| outer pass | digits peeled | new n |
|---|---|---|
| 1 | 5, 7, 8, 9 | 29 |
| 2 | 9, 2 | 11 |
| 3 | 1, 1 | 2 |

`2 < 10`, stop.

**Termination:** for any `n ≥ 10`, the digit sum is strictly smaller than `n` (each digit `d` at
position `k` contributes `d` instead of `d · 10ᵏ`), so the outer loop shrinks `n` every pass.

## Complexity

- **Time:** the first pass is O(number of digits) = O(log n); afterwards the value is tiny (an
  8-digit number sums to at most 72), so the remaining passes are constant work. Overall O(log n).
- **Space:** O(1).

## Common mistakes

- Resetting `s` outside the outer loop, so sums accumulate across passes.
- Using `n > 9` vs `n >= 10` is fine; `n > 10` is a bug (returns 10 for input 10, whose root is 1).
- Writing the inner loop on `n` while still needing the old value later: here it's fine because we
  overwrite `n = s` anyway, but in general copy first.

## Going further

Because `10 ≡ 1 (mod 9)`, a number and its digit sum leave the same remainder mod 9. So the
digital root is `0` if `n == 0`, else `1 + (n − 1) % 9`. That's the "casting out nines" check
accountants used to verify arithmetic by hand, and it makes this an O(1) problem.
""",
    solution=r'''def digital_root(n):
    # Outer loop: keep collapsing while n has at least two digits.
    while n >= 10:
        s = 0                 # fresh digit sum for this pass
        # Inner loop: peel digits from the right until n runs out.
        while n > 0:
            s += n % 10       # last digit
            n //= 10          # drop it
        # The digit sum is strictly smaller than any n >= 10, so the outer loop terminates.
        n = s
    return n
''',
    refs={
        "c": r'''long long digital_root(long long n) {
    while (n >= 10) {
        long long s = 0;
        while (n > 0) {       /* sum the digits of n */
            s += n % 10;
            n /= 10;
        }
        n = s;
    }
    return n;
}''',
        "cpp": r'''long long digitalRoot(long long n) {
    while (n >= 10) {
        long long s = 0;
        for (; n > 0; n /= 10) s += n % 10;
        n = s;
    }
    return n;
}''',
        "rust": r'''pub fn digital_root(mut n: i64) -> i64 {
    while n >= 10 {
        let mut s = 0;
        while n > 0 {
            s += n % 10;
            n /= 10;
        }
        n = s;
    }
    n
}''',
        "espresso": r'''fn digitalRoot(n) {
  while n >= 10 {
    var s = 0
    while n > 0 {
      s += n - (n / 10) * 10   // n mod 10, the last digit
      n = n / 10
    }
    n = s
  }
  return n
}''',
    },
    tests=[[9875], [7], [0], [10], [9], [18], [38], [9999999], [9876543], [10000000]],
))
