"""Track 2: Logic & Math. Conditionals, integer arithmetic, modulo, digits, divisibility."""

import random

_rng = random.Random(202)

TRACK = dict(
    id="logic-math",
    title="Logic & Math",
    order=2,
    icon="∑",
    blurb="Make decisions with if/else and bend integers to your will: division, remainders, digits, divisibility and primes.",
    intro=r"""
In First Steps you learned to read input, return values, and loop. This track is about the two tools that turn those mechanics into real problem solving: **decisions** (conditionals and boolean logic) and **integer arithmetic** (division, remainders, digits). These ideas appear in nearly every algorithm you will ever write, so it pays to know their sharp edges well.

## Decisions: if / else if / else

A chain of conditions is checked **top to bottom**, and only the **first** true branch runs:

```python
if score >= 90:
    grade = "A"
elif score >= 80:      # only reached when score < 90
    grade = "B"
else:
    grade = "F"
```

```c
if (score >= 90)      grade = 'A';
else if (score >= 80) grade = 'B';   /* implicitly also score < 90 */
else                  grade = 'F';
```

```rust
let grade = if score >= 90 { 'A' } else if score >= 80 { 'B' } else { 'F' };
```

Because earlier branches have already been ruled out, later conditions can be simpler. Order your checks from **most specific to least specific**: in FizzBuzz, "divisible by 15" must come before "divisible by 3", or it will never be reached.

## Boolean logic

Conditions combine with **AND**, **OR** and **NOT** (`and`/`or`/`not` in Python, `&&`/`||`/`!` elsewhere). Two laws worth memorising:

* `not (A and B)` equals `(not A) or (not B)`
* `not (A or B)` equals `(not A) and (not B)`

These **De Morgan's laws** let you flip a condition cleanly, e.g. "not inside the range" is `x < lo or x > hi`.

Both operators **short-circuit**: in `A && B`, if `A` is false, `B` is never evaluated. Use this to guard risky checks: `b != 0 && a % b == 0`.

## Integer division and remainder

For integers `a` and `b`, division produces a **quotient** `q` and a **remainder** `r` with

```text
a = q × b + r
```

`17 / 5` gives quotient 3, remainder 2, since 17 = 3 × 5 + 2. The remainder operator is `%`. It answers the most common question in this track: **is `a` divisible by `b`?** Exactly when `a % b == 0`.

| expression | meaning |
|---|---|
| `n % 2 == 0` | n is even |
| `n % 10` | last decimal digit of n (for n ≥ 0) |
| `n / 10` (integer) | n with its last digit removed |
| `s / 60`, `s % 60` | whole minutes and leftover seconds |

### The negative-number trap

Languages **disagree** about integer division with negative numbers:

| | `-7 / 2` | `-7 % 2` |
|---|---|---|
| Python (`//`, `%`) | **-4** (rounds down, toward -∞) | **1** |
| C, C++, Rust, ESPresso | **-3** (truncates toward 0) | **-1** |

Both satisfy `a = q × b + r`; they just choose different `q`. Python's remainder takes the sign of the divisor; C's takes the sign of the dividend. Consequences:

* `n % 2 == 1` is **wrong** for negative odd numbers in C (`-7 % 2` is `-1`). Test `n % 2 != 0` instead.
* "Round down" in C needs care for negatives; plain `/` rounds toward zero.
* When extracting digits, work on the absolute value.

ESPresso has **no `%` operator** at all. Use the identity directly: `a - (a / b) * b` is the remainder.

## Peeling off digits

The standard loop to walk the digits of a non-negative integer, from the last to the first:

```python
while n > 0:
    d = n % 10      # the last digit
    n //= 10        # drop it
```

```c
while (n > 0) {
    long long d = n % 10;
    n /= 10;
}
```

`1234 → (d=4) 123 → (d=3) 12 → (d=2) 1 → (d=1) 0`. Digit sums, reversing numbers, palindromic numbers and base conversion all build on this.

## Divisibility, GCD and primes

* The **greatest common divisor** of two numbers can be found in a handful of steps with **Euclid's algorithm**: `gcd(a, b) = gcd(b, a % b)`, and `gcd(a, 0) = a`.
* A number `n` is **prime** if it is at least 2 and no number from 2 up to √n divides it. Checking only up to √n turns a billion steps into about thirty thousand, because divisors come in pairs `d × (n / d)` and one of each pair is at most √n.

## Overflow and types

C, C++ and Rust integers have fixed sizes. Crucible gives you 64-bit integers (`long long`, `i64`, up to about 9.2 × 10¹⁸), but intermediate results can still overflow: `a * b` before dividing by a gcd, or `i * i` in a loop condition. Python never overflows. ESPresso integers are 32-bit (up to about 2.1 × 10⁹), so problems that offer it keep values in that range.

## How to approach this track

1. **List the cases** before coding. Most bugs in conditional code are missing cases, not wrong ones.
2. **Test the boundaries** by hand: 0, negatives, the exact cut-off values (89, 90, 91), the largest input.
3. **Watch the order** of your `if` chain.
4. **Know your language's `/` and `%`** for negative numbers.

The problems ramp from single decisions to small loops over digits and divisors. By the end you will have the arithmetic toolkit that later tracks assume.
""",
)

PROBLEMS = []

# ----------------------------------------------------------------------------
# 1. Even or odd
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="even-or-odd-word",
    title="Even or Odd",
    difficulty=0,
    tags=["modulo", "conditionals", "strings"],
    fn="parity_word",
    params=[["n", "int"]],
    returns="str",
    statement=r"""
Return the string `"even"` if `n` is even and `"odd"` if it is odd.

`n` may be negative. Zero is even.
""",
    constraints=["-10¹⁵ ≤ n ≤ 10¹⁵"],
    example_notes=["4 = 2 × 2, so it is even.", "-7 is odd. Careful: in C, C++ and Rust, -7 % 2 is -1, not 1."],
    hints=[
        "A number is even when dividing it by 2 leaves no remainder.",
        "The remainder operator is `%`. Check `n % 2 == 0`.",
        "Do not test `n % 2 == 1` for odd: for negative odd numbers C, C++ and Rust give `-1`. Compare with 0 instead.",
    ],
    explanation=r"""
## Intuition

"Even" means divisible by 2, and divisibility is a question about the **remainder**: `n` is even exactly when `n % 2 == 0`. Everything else is odd. There are only two outcomes, so a single `if/else` decides which string to return.

## Approach

```python
def parity_word(n):
    return "even" if n % 2 == 0 else "odd"
```

```c
char* parity_word(long long n) {
    const char* w = (n % 2 == 0) ? "even" : "odd";
    char* out = malloc(strlen(w) + 1);   // returned strings must be malloc-ed
    strcpy(out, w);
    return out;
}
```

```cpp
string parityWord(long long n) {
    return n % 2 == 0 ? "even" : "odd";
}
```

```rust
pub fn parity_word(n: i64) -> String {
    if n % 2 == 0 { "even".to_string() } else { "odd".to_string() }
}
```

Trace:

| n | Python `n % 2` | C/C++/Rust `n % 2` | answer |
|---|---|---|---|
| 4 | 0 | 0 | even |
| 7 | 1 | 1 | odd |
| -7 | **1** | **-1** | odd |
| 0 | 0 | 0 | even |
| -4 | 0 | 0 | even |

### Why `n % 2 == 1` is a bug

The remainder's sign follows Python's rule (sign of the divisor) or C's rule (sign of the dividend). For `-7`, Python gives `1` and C gives `-1`. Code that checks `n % 2 == 1` therefore calls -7 *even* in C, C++ and Rust. Comparing with zero is correct everywhere because an even number's remainder is 0 under both rules.

A bitwise alternative is `n & 1`: the lowest binary digit is 1 for odd numbers, including negative ones in two's complement. It is the same answer, slightly more cryptic.

### Returning strings

Python, C++ and Rust return string values directly. Rust string literals like `"even"` are borrowed `&str`; `.to_string()` makes the owned `String` the signature promises. C has to allocate: a string literal lives in read-only memory and the harness frees what you return, so we copy it into `malloc`-ed memory.

## Complexity

O(1).

## Common mistakes

* **`n % 2 == 1`** for odd (fails on negatives outside Python).
* **Returning `"Even"`** or other capitalisation: strings must match exactly.
* **In C, returning the literal `"even"` directly**: the caller would try to `free` read-only memory.

## Going further

Classify by remainder mod 3 (`"zero"`, `"one"`, `"two"`). For negative inputs in C you will need to normalise: `((n % 3) + 3) % 3` always lands in 0..2.
""",
    solution=r'''def parity_word(n: int) -> str:
    # A number is even exactly when 2 divides it, i.e. the remainder is 0.
    # Comparing with 0 (rather than checking "== 1" for odd) is also correct
    # in C, C++ and Rust, where -7 % 2 is -1 instead of Python's 1.
    if n % 2 == 0:
        return "even"
    return "odd"
''',
    refs={
        "c": r'''char* parity_word(long long n) {
    // Compare the remainder with 0: for negative odd n, C gives n % 2 == -1.
    const char* word = (n % 2 == 0) ? "even" : "odd";
    // The harness frees the result, so return a heap copy, not the literal.
    char* out = malloc(strlen(word) + 1);
    strcpy(out, word);
    return out;
}
''',
        "cpp": r'''string parityWord(long long n) {
    // The string literal converts to std::string on return.
    return n % 2 == 0 ? "even" : "odd";
}
''',
        "rust": r'''pub fn parity_word(n: i64) -> String {
    // % in Rust truncates like C: -7 % 2 == -1, so test against 0.
    if n % 2 == 0 { "even".to_string() } else { "odd".to_string() }
}
''',
    },
    tests=[[4], [7], [-7], [0], [-4], [1], [-1], [10**15], [-(10**15) + 1], [123456789]],
))

# ----------------------------------------------------------------------------
# 2. Quadrant of a point
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="point-quadrant",
    title="Quadrant of a Point",
    difficulty=0,
    tags=["conditionals", "geometry"],
    fn="quadrant",
    params=[["x", "int"], ["y", "int"]],
    returns="int",
    statement=r"""
The two axes split the plane into four **quadrants**, numbered counter-clockwise starting from the top right:

```text
        y
   2    |    1
  ------+------ x
   3    |    4
```

Return the quadrant (1, 2, 3 or 4) that contains the point `(x, y)`. If the point lies **on an axis** (`x == 0` or `y == 0`), it belongs to no quadrant: return `0`.
""",
    constraints=["-10⁹ ≤ x, y ≤ 10⁹"],
    hints=[
        "Handle the special case first: if either coordinate is 0, the answer is 0.",
        "After that, each quadrant is one combination of signs: (+,+), (-,+), (-,-), (+,-).",
        "Check `x > 0` first, then decide between 1 and 4 by the sign of y; otherwise decide between 2 and 3.",
    ],
    explanation=r"""
## Intuition

With both coordinates non-zero, a point is identified purely by the **signs** of x and y. Two yes/no questions give four combinations, which map to the four quadrants:

| x | y | quadrant |
|---|---|---|
| + | + | 1 |
| − | + | 2 |
| − | − | 3 |
| + | − | 4 |

The only other case is a zero coordinate, which must be handled **first**: otherwise `(0, 5)` would fall into whichever branch treats 0 as "not positive".

## Approach

1. If `x == 0` or `y == 0`, return 0.
2. If `x > 0`: return 1 when `y > 0`, else 4.
3. Otherwise (`x < 0`): return 2 when `y > 0`, else 3.

```python
def quadrant(x, y):
    if x == 0 or y == 0:
        return 0
    if x > 0:
        return 1 if y > 0 else 4
    return 2 if y > 0 else 3
```

```c
long long quadrant(long long x, long long y) {
    if (x == 0 || y == 0) return 0;
    if (x > 0) return y > 0 ? 1 : 4;
    return y > 0 ? 2 : 3;
}
```

```rust
pub fn quadrant(x: i64, y: i64) -> i64 {
    if x == 0 || y == 0 { return 0; }
    match (x > 0, y > 0) {           // a tuple of two bools, matched against the table
        (true, true) => 1,
        (false, true) => 2,
        (false, false) => 3,
        (true, false) => 4,
    }
}
```

The Rust `match` mirrors the truth table directly, and the compiler checks that all four combinations are covered.

### Nested decisions

Step 2 and 3 form a **decision tree**: the first question splits the plane in half, the second splits each half again. This is more efficient and more readable than four independent conditions like `if x > 0 and y > 0`, though both are correct.

## Complexity

O(1).

## Common mistakes

* **Forgetting the axis case**: `(0, 5)` or `(3, 0)` must return 0.
* **Using `>=`**, which silently puts axis points into a quadrant.
* **Mixing up 2 and 4.** Quadrants go counter-clockwise: top right, top left, bottom left, bottom right.
* **Using `x * y > 0`** to test "same sign": it overflows a 32-bit int for large coordinates.

## Going further

Return which **axis** a point lies on (`"x-axis"`, `"y-axis"`, `"origin"`) when it is on one. Or, given two points, decide whether they are in the same quadrant.
""",
    solution=r'''def quadrant(x: int, y: int) -> int:
    # Points on an axis belong to no quadrant. This must be checked first,
    # because 0 is neither positive nor negative and would otherwise slip
    # into whichever branch treats it as "not > 0".
    if x == 0 or y == 0:
        return 0
    # Now both coordinates are non-zero: the two signs decide everything.
    if x > 0:
        # Right half: above the x-axis is quadrant 1, below is quadrant 4.
        return 1 if y > 0 else 4
    # Left half: above is quadrant 2, below is quadrant 3.
    return 2 if y > 0 else 3
''',
    refs={
        "c": r'''long long quadrant(long long x, long long y) {
    if (x == 0 || y == 0) return 0;   // on an axis
    if (x > 0) return y > 0 ? 1 : 4;  // right half
    return y > 0 ? 2 : 3;             // left half
}
''',
        "cpp": r'''long long quadrant(long long x, long long y) {
    if (x == 0 || y == 0) return 0;
    if (x > 0) return y > 0 ? 1 : 4;
    return y > 0 ? 2 : 3;
}
''',
        "rust": r'''pub fn quadrant(x: i64, y: i64) -> i64 {
    if x == 0 || y == 0 {
        return 0;
    }
    // Match on the pair of signs; the compiler verifies all 4 cases exist.
    match (x > 0, y > 0) {
        (true, true) => 1,
        (false, true) => 2,
        (false, false) => 3,
        (true, false) => 4,
    }
}
''',
        "espresso": r'''fn quadrant(x, y) {
    if x == 0 {
        return 0
    }
    if y == 0 {
        return 0
    }
    if x > 0 {
        if y > 0 { return 1 }
        return 4
    }
    if y > 0 { return 2 }
    return 3
}
''',
    },
    tests=[[3, 5], [-3, 5], [-3, -5], [3, -5], [0, 5], [7, 0], [0, 0], [1000000000, -1000000000], [-1, 1], [1, 1]],
))

# ----------------------------------------------------------------------------
# 3. Clamp
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="clamp-to-range",
    title="Clamp to a Range",
    difficulty=0,
    tags=["conditionals"],
    fn="clamp",
    params=[["x", "int"], ["lo", "int"], ["hi", "int"]],
    returns="int",
    statement=r"""
**Clamping** forces a value into a range: values below the range are raised to its lower end, values above are lowered to its upper end, and values inside are left alone.

Return `x` clamped to the inclusive range `[lo, hi]`. It is guaranteed that `lo ≤ hi`.
""",
    constraints=["-10⁹ ≤ lo ≤ hi ≤ 10⁹", "-10⁹ ≤ x ≤ 10⁹"],
    example_notes=["15 is above the range [0, 10], so it becomes 10.", "-3 is below the range, so it becomes 0."],
    hints=[
        "There are three cases: below the range, above the range, inside it.",
        "If `x < lo` return `lo`; if `x > hi` return `hi`; otherwise return `x`.",
        "As a one-liner: `max(lo, min(x, hi))`.",
    ],
    explanation=r"""
## Intuition

Picture the range as a fence on the number line. A value outside the fence is pulled to the nearest fence post; a value inside stays where it is. Clamping is everywhere in real code: keeping a volume between 0 and 100, a character on screen, a colour channel between 0 and 255.

```text
      lo                hi
 ●────[==================]────●
 x<lo → lo      x stays      x>hi → hi
```

## Approach

Check the two "outside" cases; anything left is inside.

```python
def clamp(x, lo, hi):
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x
```

```c
long long clamp(long long x, long long lo, long long hi) {
    if (x < lo) return lo;
    if (x > hi) return hi;
    return x;
}
```

```cpp
long long clamp(long long x, long long lo, long long hi) {
    return std::clamp(x, lo, hi);   // C++17 has it built in
}
```

```rust
pub fn clamp(x: i64, lo: i64, hi: i64) -> i64 {
    x.clamp(lo, hi)                 // so does Rust
}
```

### The min/max formulation

`min(x, hi)` caps the value from above; `max(lo, ...)` then lifts it from below:

| x | `min(x, 10)` | `max(0, that)` |
|---|---|---|
| 15 | 10 | 10 |
| -3 | -3 | 0 |
| 7 | 7 | 7 |

Composing small functions like this is a useful habit. The order matters only when `lo > hi`, which is ruled out here.

### Early returns

Each `if` that returns removes a case. By the time execution reaches the final `return x`, both `x < lo` and `x > hi` are known to be false, so `lo ≤ x ≤ hi`. This "guard clause" style keeps conditional code flat and readable instead of deeply nested.

## Complexity

O(1).

## Common mistakes

* **Swapping lo and hi** in the returns.
* **Using `<=`/`>=`** is harmless here (returning `lo` when `x == lo` is the same value), but be deliberate about it.
* **Name collision in C++**: with `using namespace std;`, your function `clamp` and `std::clamp` coexist because they are in different namespaces; calling `std::clamp` explicitly avoids ambiguity.

## Going further

Wrap-around instead of clamping: map `x` into `[0, n)` so that `n` becomes 0 and `-1` becomes `n - 1` (like a clock). That is a modulo problem: `((x % n) + n) % n` in C.
""",
    solution=r'''def clamp(x: int, lo: int, hi: int) -> int:
    # Guard clauses: handle each "outside the range" case and return early.
    if x < lo:
        return lo       # below the fence: pull up to the lower end
    if x > hi:
        return hi       # above the fence: pull down to the upper end
    # Both guards failed, so lo <= x <= hi: the value is already in range.
    return x
''',
    refs={
        "c": r'''long long clamp(long long x, long long lo, long long hi) {
    if (x < lo) return lo;
    if (x > hi) return hi;
    return x;            // lo <= x <= hi
}
''',
        "cpp": r'''long long clamp(long long x, long long lo, long long hi) {
    // std::clamp (C++17, <algorithm>) does exactly this.
    return std::clamp(x, lo, hi);
}
''',
        "rust": r'''pub fn clamp(x: i64, lo: i64, hi: i64) -> i64 {
    // Ord::clamp panics if lo > hi; the constraints guarantee lo <= hi.
    x.clamp(lo, hi)
}
''',
        "espresso": r'''fn clamp(x, lo, hi) {
    if x < lo { return lo }
    if x > hi { return hi }
    return x
}
''',
    },
    tests=[[15, 0, 10], [-3, 0, 10], [7, 0, 10], [0, 0, 10], [10, 0, 10], [5, 5, 5], [-1000000000, -5, 5], [1000000000, -1000000000, 900000000], [-7, -10, -5]],
))

# ----------------------------------------------------------------------------
# 4. Letter grade
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="letter-grade",
    title="Letter Grade",
    difficulty=0,
    tags=["conditionals", "strings"],
    fn="letter_grade",
    params=[["score", "int"]],
    returns="str",
    statement=r"""
Convert a test score from 0 to 100 into a letter grade:

| score | grade |
|---|---|
| 90 – 100 | `"A"` |
| 80 – 89 | `"B"` |
| 70 – 79 | `"C"` |
| 60 – 69 | `"D"` |
| 0 – 59 | `"F"` |

Return the grade as a one-letter string.
""",
    constraints=["0 ≤ score ≤ 100"],
    hints=[
        "Use an if / else-if chain. The conditions are checked in order and only the first true one runs.",
        "Start from the top: `if score >= 90` is an A. Because that case has been handled, the next test only needs `score >= 80`.",
        "`if s >= 90: A elif s >= 80: B elif s >= 70: C elif s >= 60: D else: F`.",
    ],
    explanation=r"""
## Intuition

The grade boundaries split 0–100 into five **non-overlapping bands**. An `if / else if` chain checks conditions top to bottom and stops at the first match, which means each later condition implicitly includes "and none of the earlier ones". That lets us write each band with a **single** comparison.

## Approach

Check from the highest band down.

```python
def letter_grade(score):
    if score >= 90:
        return "A"
    elif score >= 80:     # here we already know score < 90
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"
```

```cpp
string letterGrade(long long score) {
    if (score >= 90) return "A";
    if (score >= 80) return "B";
    if (score >= 70) return "C";
    if (score >= 60) return "D";
    return "F";
}
```

```rust
pub fn letter_grade(score: i64) -> String {
    let g = match score {
        90..=100 => "A",
        80..=89 => "B",
        70..=79 => "C",
        60..=69 => "D",
        _ => "F",
    };
    g.to_string()
}
```

```c
char* letter_grade(long long score) {
    char g = score >= 90 ? 'A' : score >= 80 ? 'B' : score >= 70 ? 'C'
           : score >= 60 ? 'D' : 'F';
    char* out = malloc(2);
    out[0] = g; out[1] = '\0';
    return out;
}
```

Trace for the boundary values:

| score | first true test | grade |
|---|---|---|
| 100 | `>= 90` | A |
| 90 | `>= 90` | A |
| 89 | `>= 80` | B |
| 60 | `>= 60` | D |
| 59 | none | F |
| 0 | none | F |

### Order matters

If you wrote the chain bottom-up (`if score >= 60: D` first), a score of 95 would stop at the first true test and receive a D. A chain of `>=` tests must go from **highest threshold to lowest**. (A chain of `<` tests would go lowest to highest.)

### Rust range patterns

`match` can test ranges directly: `80..=89` matches 80 through 89 inclusive. `_` is the catch-all. The compiler would even warn if a later arm could never match.

## Complexity

O(1): at most four comparisons.

## Common mistakes

* **Wrong order** of the chain (see above).
* **Off-by-one at the boundaries**: `score > 90` makes 90 a B. Always test the exact cut-offs.
* **Separate `if`s without returns or `elif`**: each later `if` would overwrite the earlier grade.
* **Returning a `char` instead of a string** in C++/Rust/C.

## Going further

Add `+` and `-` modifiers: within a band, the top 3 points get `+` and the bottom 3 get `-` (so 97–100 is `A+`, 80–82 is `B-`). Use `score % 10` to find the position inside the band, and decide what to do about 100.
""",
    solution=r'''def letter_grade(score: int) -> str:
    # Check bands from the highest threshold down. Each elif is only reached
    # when every previous test failed, so "score >= 80" really means
    # "80 <= score < 90" without having to say so.
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    # Everything that fell through all thresholds (0..59) fails.
    return "F"
''',
    refs={
        "c": r'''char* letter_grade(long long score) {
    char g;
    if (score >= 90)      g = 'A';
    else if (score >= 80) g = 'B';   // already known: score < 90
    else if (score >= 70) g = 'C';
    else if (score >= 60) g = 'D';
    else                  g = 'F';
    // A one-character C string: the letter plus the '\0' terminator.
    char* out = malloc(2);
    out[0] = g;
    out[1] = '\0';
    return out;
}
''',
        "cpp": r'''string letterGrade(long long score) {
    // Highest threshold first; each return ends the chain.
    if (score >= 90) return "A";
    if (score >= 80) return "B";
    if (score >= 70) return "C";
    if (score >= 60) return "D";
    return "F";
}
''',
        "rust": r'''pub fn letter_grade(score: i64) -> String {
    // Range patterns make each band explicit; `_` catches 0..=59.
    let g = match score {
        90..=100 => "A",
        80..=89 => "B",
        70..=79 => "C",
        60..=69 => "D",
        _ => "F",
    };
    g.to_string()
}
''',
    },
    tests=[[95], [85], [100], [90], [89], [80], [79], [70], [69], [60], [59], [0], [73]],
))

# ----------------------------------------------------------------------------
# 5. Leap year
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="leap-year-check",
    title="Leap Year",
    difficulty=0,
    tags=["modulo", "boolean logic"],
    fn="is_leap_year",
    params=[["year", "int"]],
    returns="bool",
    statement=r"""
In the Gregorian calendar a year is a **leap year** if:

* it is divisible by 4,
* **except** years divisible by 100, which are not leap years,
* **except** years divisible by 400, which are leap years after all.

So 2024 is a leap year, 1900 is not, and 2000 is. Return whether `year` is a leap year.
""",
    constraints=["1 ≤ year ≤ 10⁶"],
    example_notes=["Divisible by 4 and not by 100.", "Divisible by 100 but not by 400: not a leap year."],
    hints=[
        "\"Divisible by k\" is `year % k == 0`.",
        "The rules are exceptions to exceptions. Check the most specific rule (400) first, then 100, then 4.",
        "`if year % 400 == 0: True; elif year % 100 == 0: False; else: year % 4 == 0`. Or as one expression: `(y % 4 == 0 and y % 100 != 0) or y % 400 == 0`.",
    ],
    explanation=r"""
## Intuition

The rule is a chain of exceptions, and exceptions are easiest to code **from the most specific case to the most general**. A year divisible by 400 is always a leap year, no matter what the other rules say, so check it first. Then a year divisible by 100 (but not 400) is never one. Only after those two special cases does the general "divisible by 4" rule apply.

## Approach

```python
def is_leap_year(year):
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0
```

The same logic as a single boolean expression:

```c
bool is_leap_year(long long y) {
    return (y % 4 == 0 && y % 100 != 0) || y % 400 == 0;
}
```

```cpp
bool isLeapYear(long long y) {
    return (y % 4 == 0 && y % 100 != 0) || y % 400 == 0;
}
```

```rust
pub fn is_leap_year(y: i64) -> bool {
    (y % 4 == 0 && y % 100 != 0) || y % 400 == 0
}
```

Read it as: "divisible by 4 but not a century year, **or** a multiple of 400".

| year | %4 | %100 | %400 | leap? | reason |
|---|---|---|---|---|---|
| 2024 | 0 | 24 | 24 | yes | divisible by 4, not a century |
| 2023 | 3 | 23 | 23 | no | not divisible by 4 |
| 1900 | 0 | 0 | 300 | no | century, not a multiple of 400 |
| 2000 | 0 | 0 | 0 | yes | multiple of 400 |

### Why the order of checks matters

If you check `% 4` first and return `True`, 1900 is a leap year (wrong). If you check `% 100` before `% 400`, 2000 is not (wrong). The guard-clause version only works with 400 → 100 → 4. The one-expression version avoids ordering issues because each clause carries its own conditions.

### Precedence of `&&` and `||`

`&&` binds tighter than `||` (like `*` versus `+`), so `a && b || c` means `(a && b) || c`. The parentheses in the expression above are not strictly necessary, but they make the intent obvious and silence compiler warnings.

## Complexity

O(1).

## Common mistakes

* **Only checking `% 4`**: wrong for 1900, 2100.
* **Checking 100 before 400**: wrong for 2000, 2400.
* **`y % 100 == 0` where `!= 0` was meant** (or vice versa). Read the expression aloud.

## Going further

The Gregorian calendar repeats every 400 years: count the leap years in one cycle (97). From that, the average year length is 365 + 97/400 = 365.2425 days. Next problem: use this function to compute the number of days in a month.
""",
    solution=r'''def is_leap_year(year: int) -> bool:
    # Exceptions to exceptions: test the most specific rule first.
    # 1) Multiples of 400 are always leap years (e.g. 2000).
    if year % 400 == 0:
        return True
    # 2) Other century years are never leap years (e.g. 1900, 2100).
    if year % 100 == 0:
        return False
    # 3) Everything else follows the basic rule: divisible by 4.
    return year % 4 == 0
''',
    refs={
        "c": r'''bool is_leap_year(long long year) {
    // "divisible by 4 but not a century" OR "a multiple of 400"
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}
''',
        "cpp": r'''bool isLeapYear(long long year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}
''',
        "rust": r'''pub fn is_leap_year(year: i64) -> bool {
    (year % 4 == 0 && year % 100 != 0) || year % 400 == 0
}
''',
        "espresso": r'''// ESPresso has no % operator: a - (a / b) * b is the remainder.
fn divisible(a, b) {
    return a - (a / b) * b == 0
}

fn isLeapYear(year) {
    if divisible(year, 400) { return true }    // most specific rule first
    if divisible(year, 100) { return false }
    return divisible(year, 4)
}
''',
    },
    tests=[[2024], [2023], [1900], [2000], [2100], [2400], [1], [4], [100], [400], [1996], [999999], [1000000]],
))

# ----------------------------------------------------------------------------
# 6. Days in month
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="days-in-month",
    title="Days in a Month",
    difficulty=1,
    tags=["conditionals", "calendar"],
    fn="days_in_month",
    params=[["month", "int"], ["year", "int"]],
    returns="int",
    statement=r"""
Return the number of days in the given `month` (1 = January, ..., 12 = December) of the given `year`, using the Gregorian calendar.

* April, June, September and November have 30 days.
* February has 29 days in a leap year and 28 otherwise.
* All other months have 31 days.

Leap years follow the usual rule: divisible by 4, except centuries, except multiples of 400.
""",
    constraints=["1 ≤ month ≤ 12", "1 ≤ year ≤ 10⁶"],
    hints=[
        "February is the only month whose length depends on the year. Handle it separately.",
        "For the other months, either list the 30-day months in a condition, or store all twelve lengths in an array and index it with `month - 1`.",
        "Write (or reuse) a leap year helper: `(y % 4 == 0 and y % 100 != 0) or y % 400 == 0`. Then February is `29 if leap else 28`.",
    ],
    explanation=r"""
## Intuition

Eleven months have a fixed length; only February depends on the year. So the problem splits cleanly into "special case February" and "look up the rest". This is also a good place to practise two habits: **writing a helper function** (the leap-year test) and **replacing a long if-chain with a table**.

## Approach

Store the lengths in an array (a **lookup table**) indexed by `month - 1`, then patch February.

```python
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def is_leap(y):
    return (y % 4 == 0 and y % 100 != 0) or y % 400 == 0

def days_in_month(month, year):
    if month == 2 and is_leap(year):
        return 29
    return DAYS[month - 1]
```

```c
static bool is_leap(long long y) { return (y % 4 == 0 && y % 100 != 0) || y % 400 == 0; }

long long days_in_month(long long month, long long year) {
    static const long long days[12] = {31,28,31,30,31,30,31,31,30,31,30,31};
    if (month == 2 && is_leap(year)) return 29;
    return days[month - 1];
}
```

```cpp
long long daysInMonth(long long month, long long year) {
    static const array<long long, 12> days{31,28,31,30,31,30,31,31,30,31,30,31};
    bool leap = (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
    return (month == 2 && leap) ? 29 : days[month - 1];
}
```

```rust
pub fn days_in_month(month: i64, year: i64) -> i64 {
    let leap = (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
    match month {
        2 => if leap { 29 } else { 28 },
        4 | 6 | 9 | 11 => 30,
        _ => 31,
    }
}
```

The Rust version shows the other style: a `match` with `|` to list several values in one arm.

### Why `month - 1`?

Months are numbered from 1, arrays from 0. January (1) lives at index 0, December (12) at index 11. Forgetting the `- 1` shifts every month by one and reads past the end for December.

### Helpers

Pulling the leap-year rule into its own function gives it a **name**, makes it testable on its own, and keeps `days_in_month` readable. In C, `static` on a helper means "only visible in this file", a good default for internal helpers.

| month, year | February? | leap? | answer |
|---|---|---|---|
| 2, 2024 | yes | yes | 29 |
| 2, 1900 | yes | no | 28 |
| 4, 2023 | no | - | 30 |
| 12, 1 | no | - | 31 |

## Complexity

O(1).

## Common mistakes

* **Off-by-one indexing**: `days[month]` instead of `days[month - 1]`.
* **Using a simplified leap rule** (`year % 4 == 0`): 1900 gets 29 days.
* **Mis-remembering the 30-day months.** The rhyme: "Thirty days hath September, April, June and November".

## Going further

Compute the **day of the year** for a date (`day_of_year(day, month, year)`): sum `days_in_month` for the months before, then add the day. Then the number of days between two dates.
""",
    solution=r'''# Month lengths in a non-leap year. Index 0 is January, so a month number
# m (1..12) lives at index m - 1.
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def is_leap(year: int) -> bool:
    # Divisible by 4 but not a century, or a multiple of 400.
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0


def days_in_month(month: int, year: int) -> int:
    # February is the only month whose length depends on the year.
    if month == 2 and is_leap(year):
        return 29
    # Every other case (including February in a common year) is a table
    # lookup, which is shorter and less error-prone than a 12-way if chain.
    return DAYS[month - 1]
''',
    refs={
        "c": r'''static bool is_leap(long long y) {
    return (y % 4 == 0 && y % 100 != 0) || y % 400 == 0;
}

long long days_in_month(long long month, long long year) {
    // Lookup table for a common year; index = month - 1.
    static const long long days[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    if (month == 2 && is_leap(year)) return 29;
    return days[month - 1];
}
''',
        "cpp": r'''long long daysInMonth(long long month, long long year) {
    static const array<long long, 12> days{31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    bool leap = (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
    return (month == 2 && leap) ? 29 : days[month - 1];
}
''',
        "rust": r'''pub fn days_in_month(month: i64, year: i64) -> i64 {
    let leap = (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
    match month {
        2 => if leap { 29 } else { 28 },
        4 | 6 | 9 | 11 => 30,   // "thirty days hath September, April, June and November"
        _ => 31,
    }
}
''',
        "espresso": r'''fn rem(a, b) {
    return a - (a / b) * b     // no % operator in ESPresso
}

fn isLeap(y) {
    if rem(y, 400) == 0 { return true }
    if rem(y, 100) == 0 { return false }
    return rem(y, 4) == 0
}

fn daysInMonth(month, year) {
    if month == 2 {
        if isLeap(year) { return 29 }
        return 28
    }
    if month == 4 { return 30 }
    if month == 6 { return 30 }
    if month == 9 { return 30 }
    if month == 11 { return 30 }
    return 31
}
''',
    },
    tests=[[2, 2024], [2, 2023], [2, 1900], [2, 2000], [1, 2023], [4, 2023], [6, 1], [9, 1999], [11, 2024], [12, 1], [7, 1000000], [8, 2021]],
))

# ----------------------------------------------------------------------------
# 7. FizzBuzz word
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="fizzbuzz-word",
    title="FizzBuzz Word",
    difficulty=0,
    tags=["modulo", "conditionals", "strings"],
    fn="fizzbuzz_word",
    params=[["n", "int"]],
    returns="str",
    statement=r"""
The classic interview warm-up, one number at a time. Return:

* `"FizzBuzz"` if `n` is divisible by both 3 and 5,
* `"Fizz"` if `n` is divisible by 3 (only),
* `"Buzz"` if `n` is divisible by 5 (only),
* otherwise, `n` itself written as a decimal string (e.g. `"7"`).
""",
    constraints=["1 ≤ n ≤ 10⁹"],
    hints=[
        "Divisible by k means `n % k == 0`.",
        "The order of your checks matters. What happens to 15 if you test \"divisible by 3\" first?",
        "Check 15 (both) first, then 3, then 5, else convert the number: `str(n)`, `to_string(n)`, `n.to_string()`, or `snprintf` in C.",
    ],
    explanation=r"""
## Intuition

Four outcomes, three of them based on divisibility. The single real trap is **ordering**: 15 is divisible by 3, by 5, and by both, so it matches three of the rules. An `if / else if` chain picks the first match, so the most specific rule (both) must be checked first.

## Approach

```python
def fizzbuzz_word(n):
    if n % 15 == 0:        # divisible by 3 AND 5 <=> divisible by 15
        return "FizzBuzz"
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    return str(n)
```

```cpp
string fizzbuzzWord(long long n) {
    if (n % 15 == 0) return "FizzBuzz";
    if (n % 3 == 0) return "Fizz";
    if (n % 5 == 0) return "Buzz";
    return to_string(n);
}
```

```rust
pub fn fizzbuzz_word(n: i64) -> String {
    match (n % 3, n % 5) {
        (0, 0) => "FizzBuzz".to_string(),
        (0, _) => "Fizz".to_string(),
        (_, 0) => "Buzz".to_string(),
        _ => n.to_string(),
    }
}
```

```c
char* fizzbuzz_word(long long n) {
    char* out = malloc(32);              // enough for any 64-bit number
    if (n % 15 == 0)     strcpy(out, "FizzBuzz");
    else if (n % 3 == 0) strcpy(out, "Fizz");
    else if (n % 5 == 0) strcpy(out, "Buzz");
    else snprintf(out, 32, "%lld", n);   // printf, but into a buffer
    return out;
}
```

| n | %3 | %5 | result |
|---|---|---|---|
| 9 | 0 | 4 | Fizz |
| 10 | 1 | 0 | Buzz |
| 15 | 0 | 0 | FizzBuzz |
| 7 | 1 | 2 | "7" |

### Why 15?

"Divisible by 3 and by 5" is the same as "divisible by 15" because 3 and 5 share no common factor (15 is their least common multiple). For 4 and 6 that shortcut would be wrong: their LCM is 12, not 24. Writing `n % 3 == 0 && n % 5 == 0` is always safe.

### Numbers to strings

Converting an integer to its decimal text is called **formatting**: `str(n)` in Python, `to_string(n)` in C++, `n.to_string()` or `format!("{}", n)` in Rust. In C, `snprintf(buf, size, "%lld", n)` works exactly like `printf` but writes into `buf`, never more than `size` bytes.

## Complexity

O(1) (formatting a number takes time proportional to its number of digits, at most 19).

## Common mistakes

* **Checking 3 before 15**: 15 returns `"Fizz"`.
* **Returning the number itself** (an int) in the default case instead of a string.
* **Capitalisation**: `"Fizzbuzz"` is not `"FizzBuzz"`.
* **C: `sprintf` without a size**: use `snprintf` so it can never overflow the buffer.

## Going further

Build the string instead of branching four ways: start with `""`, append `"Fizz"` if divisible by 3, append `"Buzz"` if divisible by 5, and if it is still empty, use the number. This version extends to new rules ("Bazz" for 7) without a combinatorial explosion of cases.
""",
    solution=r'''def fizzbuzz_word(n: int) -> str:
    # The most specific rule must come first: 15 matches the 3-rule, the
    # 5-rule and the both-rule, and an if-chain stops at the first match.
    # Because 3 and 5 are coprime, "divisible by both" equals "divisible by 15".
    if n % 15 == 0:
        return "FizzBuzz"
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    # The fallback must still be a string, so convert the number to text.
    return str(n)
''',
    refs={
        "c": r'''char* fizzbuzz_word(long long n) {
    // 32 bytes is plenty for "FizzBuzz" or any 64-bit decimal number.
    char* out = malloc(32);
    if (n % 15 == 0)      strcpy(out, "FizzBuzz");   // most specific first
    else if (n % 3 == 0)  strcpy(out, "Fizz");
    else if (n % 5 == 0)  strcpy(out, "Buzz");
    else snprintf(out, 32, "%lld", n);               // format the number into the buffer
    return out;
}
''',
        "cpp": r'''string fizzbuzzWord(long long n) {
    if (n % 15 == 0) return "FizzBuzz";
    if (n % 3 == 0) return "Fizz";
    if (n % 5 == 0) return "Buzz";
    return to_string(n);
}
''',
        "rust": r'''pub fn fizzbuzz_word(n: i64) -> String {
    // Matching on both remainders at once lists the four cases explicitly;
    // arms are tried top to bottom, so (0, 0) must come first.
    match (n % 3, n % 5) {
        (0, 0) => "FizzBuzz".to_string(),
        (0, _) => "Fizz".to_string(),
        (_, 0) => "Buzz".to_string(),
        _ => n.to_string(),
    }
}
''',
    },
    tests=[[15], [9], [10], [7], [1], [3], [5], [30], [98], [1000000000], [999999999], [14]],
))

# ----------------------------------------------------------------------------
# 8. Triangle type
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="triangle-type",
    title="Triangle Type",
    difficulty=1,
    tags=["conditionals", "geometry"],
    fn="triangle_type",
    params=[["a", "int"], ["b", "int"], ["c", "int"]],
    returns="str",
    statement=r"""
Three integers `a`, `b`, `c` are proposed as the side lengths of a triangle. Return:

* `"invalid"` if they cannot form a real triangle: any side is ≤ 0, or some side is **greater than or equal to** the sum of the other two (a flat, zero-area "triangle" counts as invalid),
* `"equilateral"` if all three sides are equal,
* `"isosceles"` if exactly two sides are equal,
* `"scalene"` if all three sides are different.
""",
    constraints=["-10⁹ ≤ a, b, c ≤ 10⁹"],
    example_notes=["All sides equal.", "1 + 2 = 3, so these three sides lie flat on a line: invalid."],
    hints=[
        "Validity first: no point classifying something that is not a triangle.",
        "The **triangle inequality**: each side must be strictly less than the sum of the other two. You need all three checks (or one check against the largest side).",
        "After validity: if `a == b == c` → equilateral; else if `a == b or b == c or a == c` → isosceles; else scalene.",
    ],
    explanation=r"""
## Intuition

Two separate questions hide in this problem: **is it a triangle at all?** and **what kind is it?** Answer them in that order. Classifying invalid input is meaningless, so validity acts as a gate.

The geometry fact you need is the **triangle inequality**: any side of a triangle is shorter than the other two combined. Picture two short sticks and one long one: if the short ones add up to less than the long one, their ends cannot meet. If they add up to exactly the long one, the "triangle" collapses into a line.

```text
 a + b > c        a + b == c         a + b < c
    /\
   /  \          ___________        ___     ___
  /____\              (flat)          (gap)
```

## Approach

1. If any side is ≤ 0, return `"invalid"`.
2. If `a + b <= c` or `a + c <= b` or `b + c <= a`, return `"invalid"`.
3. If `a == b and b == c`, return `"equilateral"`.
4. If any two are equal, return `"isosceles"`.
5. Otherwise `"scalene"`.

```python
def triangle_type(a, b, c):
    if a <= 0 or b <= 0 or c <= 0:
        return "invalid"
    if a + b <= c or a + c <= b or b + c <= a:
        return "invalid"
    if a == b == c:
        return "equilateral"
    if a == b or b == c or a == c:
        return "isosceles"
    return "scalene"
```

```cpp
string triangleType(long long a, long long b, long long c) {
    if (a <= 0 || b <= 0 || c <= 0) return "invalid";
    if (a + b <= c || a + c <= b || b + c <= a) return "invalid";
    if (a == b && b == c) return "equilateral";
    if (a == b || b == c || a == c) return "isosceles";
    return "scalene";
}
```

```rust
pub fn triangle_type(a: i64, b: i64, c: i64) -> String {
    let kind = if a <= 0 || b <= 0 || c <= 0 || a + b <= c || a + c <= b || b + c <= a {
        "invalid"
    } else if a == b && b == c {
        "equilateral"
    } else if a == b || b == c || a == c {
        "isosceles"
    } else {
        "scalene"
    };
    kind.to_string()
}
```

| a, b, c | check that decides | result |
|---|---|---|
| 3, 3, 3 | all equal | equilateral |
| 1, 2, 3 | 1 + 2 ≤ 3 | invalid |
| 5, 5, 8 | a == b | isosceles |
| 3, 4, 5 | none equal | scalene |
| 0, 4, 4 | side ≤ 0 | invalid |

### Order of the classification

Equilateral must be tested **before** isosceles, because an equilateral triangle also has "two equal sides" and would otherwise be reported as isosceles. Same principle as FizzBuzz: specific before general.

### `a == b == c`

Python allows chained comparisons: `a == b == c` means `a == b and b == c`. In C, C++ and Rust, `a == b == c` is **not** that: it compares the boolean result of `a == b` (0 or 1) with `c`. Always write `a == b && b == c` there.

## Complexity

O(1).

## Common mistakes

* **Using `<` instead of `<=`** in the inequality: accepts flat triangles like (1, 2, 3).
* **Checking only one inequality** (e.g. `a + b > c`): (10, 1, 1) slips through.
* **Ignoring zero or negative sides.**
* **Testing isosceles before equilateral.**
* **Overflow with 32-bit ints**: `a + b` with sides near 10⁹ is 2 × 10⁹, beyond a 32-bit `int`. 64-bit types are safe.

## Going further

Sort the sides first (`a ≤ b ≤ c`); then validity is the single check `a + b > c`, and isosceles is `a == b or b == c`. Also try detecting **right** triangles with `a² + b² == c²` (after sorting).
""",
    solution=r'''def triangle_type(a: int, b: int, c: int) -> str:
    # Gate 1: lengths must be positive.
    if a <= 0 or b <= 0 or c <= 0:
        return "invalid"
    # Gate 2: the triangle inequality, strictly. Each side must be shorter
    # than the other two combined; equality would give a flat line. All three
    # checks are needed because we do not know which side is the longest.
    if a + b <= c or a + c <= b or b + c <= a:
        return "invalid"
    # Classify, most specific first: an equilateral triangle also has
    # "two equal sides", so it must be caught before the isosceles test.
    if a == b == c:            # Python chained comparison: a == b and b == c
        return "equilateral"
    if a == b or b == c or a == c:
        return "isosceles"
    return "scalene"
''',
    refs={
        "c": r'''static char* dup_str(const char* s) {
    // Copy a literal into heap memory so the caller can free it.
    char* out = malloc(strlen(s) + 1);
    strcpy(out, s);
    return out;
}

char* triangle_type(long long a, long long b, long long c) {
    if (a <= 0 || b <= 0 || c <= 0) return dup_str("invalid");
    if (a + b <= c || a + c <= b || b + c <= a) return dup_str("invalid");
    // NB: in C, a == b == c would compare (a == b), i.e. 0 or 1, with c.
    if (a == b && b == c) return dup_str("equilateral");
    if (a == b || b == c || a == c) return dup_str("isosceles");
    return dup_str("scalene");
}
''',
        "cpp": r'''string triangleType(long long a, long long b, long long c) {
    if (a <= 0 || b <= 0 || c <= 0) return "invalid";
    if (a + b <= c || a + c <= b || b + c <= a) return "invalid";
    if (a == b && b == c) return "equilateral";
    if (a == b || b == c || a == c) return "isosceles";
    return "scalene";
}
''',
        "rust": r'''pub fn triangle_type(a: i64, b: i64, c: i64) -> String {
    // Sort the sides so the triangle inequality is a single check.
    let mut s = [a, b, c];
    s.sort();
    let kind = if s[0] <= 0 || s[0] + s[1] <= s[2] {
        "invalid"
    } else if s[0] == s[2] {
        "equilateral"            // smallest == largest: all equal
    } else if s[0] == s[1] || s[1] == s[2] {
        "isosceles"              // after sorting, equal sides are adjacent
    } else {
        "scalene"
    };
    kind.to_string()
}
''',
    },
    tests=[[3, 3, 3], [1, 2, 3], [5, 5, 8], [3, 4, 5], [0, 4, 4], [-3, 4, 5], [10, 1, 1], [1, 10, 1], [1, 1, 10],
           [8, 5, 5], [5, 8, 5], [2, 2, 3], [1000000000, 1000000000, 1000000000], [1000000000, 999999999, 1], [7, 10, 5]],
))

# ----------------------------------------------------------------------------
# 9. Seconds to clock
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="seconds-to-clock",
    title="Seconds to Clock Time",
    difficulty=1,
    tags=["integer division", "modulo", "formatting"],
    fn="format_clock",
    params=[["total_seconds", "int"]],
    returns="str",
    statement=r"""
Convert a duration given in seconds into the format `H:MM:SS`:

* `H` is the number of whole hours, written **without** leading zeros (it may be larger than 23, and it is `0` for durations under an hour),
* `MM` is the remaining minutes, always two digits,
* `SS` is the remaining seconds, always two digits.

For example, `3725` seconds is 1 hour, 2 minutes and 5 seconds: `"1:02:05"`.
""",
    constraints=["0 ≤ total_seconds ≤ 10¹²"],
    hints=[
        "There are 3600 seconds in an hour and 60 in a minute. Integer division tells you how many whole units fit; the remainder tells you what is left over.",
        "`h = t // 3600`, `m = (t % 3600) // 60`, `s = t % 60`.",
        "Zero-padding: Python `f\"{h}:{m:02d}:{s:02d}\"`, C `\"%lld:%02lld:%02lld\"`, Rust `format!(\"{}:{:02}:{:02}\", h, m, s)`.",
    ],
    explanation=r"""
## Intuition

Converting seconds to hours, minutes and seconds is a **mixed-radix** conversion, just like writing a number in decimal, except the "digits" have different sizes: 60 seconds make a minute, 60 minutes make an hour. Integer division `//` asks "how many whole units fit?", and the remainder `%` asks "what is left over?".

## Approach

1. `h = t // 3600`: whole hours.
2. `m = (t % 3600) // 60`: whole minutes in the leftover part.
3. `s = t % 60`: leftover seconds.
4. Format with two-digit, zero-padded minutes and seconds.

Trace for `t = 3725`:

| step | expression | value |
|---|---|---|
| hours | `3725 // 3600` | 1 |
| leftover | `3725 % 3600` | 125 |
| minutes | `125 // 60` | 2 |
| seconds | `3725 % 60` | 5 |
| text | `"1" ":" "02" ":" "05"` | `1:02:05` |

Notice `t % 60` gives the seconds directly: removing whole hours (multiples of 3600) does not change the remainder mod 60, since 3600 is itself a multiple of 60.

```python
def format_clock(t):
    h, m, s = t // 3600, (t % 3600) // 60, t % 60
    return f"{h}:{m:02d}:{s:02d}"
```

```c
char* format_clock(long long t) {
    char* out = malloc(40);
    snprintf(out, 40, "%lld:%02lld:%02lld", t / 3600, (t % 3600) / 60, t % 60);
    return out;
}
```

```cpp
string formatClock(long long t) {
    ostringstream os;
    os << t / 3600 << ':' << setw(2) << setfill('0') << (t % 3600) / 60
       << ':' << setw(2) << setfill('0') << t % 60;
    return os.str();
}
```

```rust
pub fn format_clock(t: i64) -> String {
    format!("{}:{:02}:{:02}", t / 3600, (t % 3600) / 60, t % 60)
}
```

### Format specs for zero padding

| language | spec | meaning |
|---|---|---|
| Python | `{m:02d}` | integer, width 2, pad with `0` |
| C / C++ printf | `%02lld` | same, for a `long long` |
| C++ streams | `setw(2) << setfill('0')` | width applies to the **next** value only |
| Rust | `{:02}` | width 2, zero padded |

Without the `0`, the width pads with spaces (`" 5"`), and without any width, `5` prints as `5`, giving `1:2:5`.

### `divmod`

Python's `divmod(a, b)` returns `(a // b, a % b)` in one call: `h, rest = divmod(t, 3600); m, s = divmod(rest, 60)`. It reads exactly like the idea.

## Complexity

O(1).

## Common mistakes

* **`m = t // 60`**: that is *total* minutes (62 for 3725), not minutes within the hour.
* **No zero padding**: `1:2:5`.
* **Padding the hours** (`01:02:05`): the statement says no leading zeros for H.
* **C++ `setw` only applies once**: you must repeat it before each padded value.
* **32-bit overflow**: 10¹² seconds does not fit in an `int`.

## Going further

Parse the other way: given `"H:MM:SS"`, return the total seconds (`h * 3600 + m * 60 + s`). Then add days: `D days, H:MM:SS`.
""",
    solution=r'''def format_clock(total_seconds: int) -> str:
    # Mixed-radix conversion. divmod(a, b) returns (a // b, a % b):
    # how many whole units fit, and what is left over.
    hours, rest = divmod(total_seconds, 3600)   # 3600 seconds per hour
    minutes, seconds = divmod(rest, 60)         # 60 seconds per minute
    # Hours are printed as-is (no padding, may exceed 23).
    # :02d pads minutes and seconds to two digits with leading zeros.
    return f"{hours}:{minutes:02d}:{seconds:02d}"
''',
    refs={
        "c": r'''char* format_clock(long long total_seconds) {
    long long h = total_seconds / 3600;          // whole hours
    long long m = (total_seconds % 3600) / 60;   // whole minutes left over
    long long s = total_seconds % 60;            // seconds left over
    // 40 bytes comfortably fits a 13-digit hour count plus ":MM:SS".
    char* out = malloc(40);
    // %02lld: a long long, at least 2 characters wide, padded with '0'.
    snprintf(out, 40, "%lld:%02lld:%02lld", h, m, s);
    return out;
}
''',
        "cpp": r'''string formatClock(long long totalSeconds) {
    long long h = totalSeconds / 3600;
    long long m = (totalSeconds % 3600) / 60;
    long long s = totalSeconds % 60;
    ostringstream os;
    // setw applies only to the next value written, so repeat it.
    os << h << ':' << setw(2) << setfill('0') << m
       << ':' << setw(2) << setfill('0') << s;
    return os.str();
}
''',
        "rust": r'''pub fn format_clock(total_seconds: i64) -> String {
    let h = total_seconds / 3600;
    let m = (total_seconds % 3600) / 60;
    let s = total_seconds % 60;
    // {:02} = minimum width 2, zero padded.
    format!("{}:{:02}:{:02}", h, m, s)
}
''',
    },
    tests=[[3725], [0], [59], [60], [3599], [3600], [86399], [86400], [45296], [10**12], [7322]],
))

# ----------------------------------------------------------------------------
# 10. Round to nearest ten
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="round-to-nearest-ten",
    title="Round to the Nearest Ten",
    difficulty=1,
    tags=["integer division", "rounding", "negative numbers"],
    fn="round_to_ten",
    params=[["n", "int"]],
    returns="int",
    statement=r"""
Round the integer `n` to the nearest multiple of 10.

When `n` is exactly halfway between two multiples (its last digit is 5), round **up**, toward positive infinity. So `15 → 20`, `-15 → -10`, and `-16 → -20`.
""",
    constraints=["-10⁹ ≤ n ≤ 10⁹"],
    example_notes=["44 is closer to 40 than to 50.", "45 is exactly halfway, so it rounds up to 50."],
    hints=[
        "Adding 5 and then rounding *down* to a multiple of 10 rounds to the nearest, with ties going up.",
        "\"Round down to a multiple of 10\" is `floor(x / 10) * 10`. Python's `//` is a floor division; C, C++ and Rust's `/` is not (it truncates toward zero).",
        "In C/C++/Rust compute `q = (n + 5) / 10` and if `(n + 5) % 10 < 0`, subtract 1 from `q` (that converts truncation into floor). Rust also has `(n + 5).div_euclid(10)`.",
    ],
    explanation=r"""
## Intuition

Rounding to the nearest ten with ties going up is the same as **adding 5 and then rounding down** to a multiple of ten:

```text
 44 + 5 = 49  → down to 40
 45 + 5 = 50  → down to 50
 46 + 5 = 51  → down to 50
-15 + 5 = -10 → down to -10
-16 + 5 = -11 → down to -20
```

"Round down to a multiple of 10" is `floor(x / 10) * 10`. All the difficulty is in getting a true **floor** division for negative numbers.

## Approach

### Python: `//` is floor division

```python
def round_to_ten(n):
    return (n + 5) // 10 * 10
```

`-11 // 10` is `-2` in Python (floor rounds toward −∞), so `-16 → -20`. Correct.

### C, C++, Rust: `/` truncates toward zero

In these languages `-11 / 10` is `-1`, because truncation simply drops the fraction (−1.1 → −1). That would round `-16` to `-10`: wrong. We must convert truncation into floor. The two differ exactly when the division is inexact and the result is negative, which is precisely when the remainder is negative:

```c
long long round_to_ten(long long n) {
    long long x = n + 5;
    long long q = x / 10;
    if (x % 10 < 0) q -= 1;     // truncated toward zero; step down to the floor
    return q * 10;
}
```

```cpp
long long roundToTen(long long n) {
    long long x = n + 5, q = x / 10;
    if (x % 10 < 0) --q;
    return q * 10;
}
```

```rust
pub fn round_to_ten(n: i64) -> i64 {
    (n + 5).div_euclid(10) * 10   // Euclidean division = floor for a positive divisor
}
```

Trace for `n = -16`:

| step | Python | C (naive) | C (fixed) |
|---|---|---|---|
| `x = n + 5` | -11 | -11 | -11 |
| quotient | `-11 // 10 = -2` | `-11 / 10 = -1` | -1, remainder -1 < 0 → -2 |
| `× 10` | **-20** | -10 ✗ | **-20** |

### Truncation vs floor, summarised

| | 7 / 2 | -7 / 2 | -7 % 2 |
|---|---|---|---|
| truncation (C, C++, Rust, ESPresso `/`) | 3 | -3 | -1 |
| floor (Python `//`, `%`) | 3 | -4 | 1 |
| Rust `div_euclid` / `rem_euclid` | 3 | -4 | 1 |

Whenever negative numbers meet division, ask which one you need.

### Why not use floating point?

`round(n / 10) * 10` looks tempting, but Python's `round` uses **banker's rounding** (ties to even: `round(2.5) == 2`), C's `round` sends ties *away from zero* (`-1.5 → -2`), and floats lose precision for big values. Integer arithmetic is exact and states the tie rule explicitly.

## Complexity

O(1).

## Common mistakes

* **Truncating division for negatives** (the trap above).
* **Rounding ties away from zero** (`-15 → -20`): the statement says ties go up, toward +∞.
* **Using float `round`**, with its language-specific tie rules.

## Going further

Generalise to `round_to(n, k)` for any positive `k`: `floor((n + k/2) / k) * k` works when `k` is even; think about what "halfway" means when `k` is odd. Banker's rounding (ties to the even multiple) is a nice challenge too.
""",
    solution=r'''def round_to_ten(n: int) -> int:
    # Nearest multiple of 10 with ties going up == add 5, then round DOWN.
    # Python's // is FLOOR division (toward -infinity), even for negatives:
    #   -16 + 5 = -11, and -11 // 10 == -2, so the result is -20 (correct).
    # In C, C++ and Rust, / truncates toward zero instead (-11 / 10 == -1),
    # which is why their versions need an extra correction step.
    return (n + 5) // 10 * 10
''',
    refs={
        "c": r'''long long round_to_ten(long long n) {
    long long x = n + 5;       // ties (last digit 5) now land on a multiple of 10
    long long q = x / 10;      // C truncates toward zero...
    if (x % 10 < 0) q -= 1;    // ...so for negative inexact results, step down to the floor
    return q * 10;
}
''',
        "cpp": r'''long long roundToTen(long long n) {
    long long x = n + 5;
    long long q = x / 10;      // truncation toward zero
    if (x % 10 < 0) --q;       // convert to floor division
    return q * 10;
}
''',
        "rust": r'''pub fn round_to_ten(n: i64) -> i64 {
    // div_euclid rounds toward -infinity when the divisor is positive,
    // which is exactly the floor division we need.
    (n + 5).div_euclid(10) * 10
}
''',
        "espresso": r'''fn roundToTen(n) {
    var x = n + 5
    var q = x / 10              // integer / truncates toward zero
    if x - q * 10 < 0 {         // negative remainder: truncation went up, so step down
        q = q - 1
    }
    return q * 10
}
''',
    },
    tests=[[44], [45], [46], [-15], [-16], [-14], [0], [5], [-5], [-4], [-6], [16777205], [-1000000000], [1000000000], [123]],
))

# ----------------------------------------------------------------------------
# 11. Digit sum
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="digit-sum",
    title="Digit Sum",
    difficulty=0,
    tags=["digits", "modulo", "loops"],
    fn="digit_sum",
    params=[["n", "int"]],
    returns="int",
    statement=r"""
Return the sum of the decimal digits of `n`. The sign is ignored: the digit sum of `-472` is `4 + 7 + 2 = 13`.

The digit sum of `0` is `0`. Solve it with arithmetic (`%` and `/`), not by converting to a string.
""",
    constraints=["-2 × 10⁹ ≤ n ≤ 2 × 10⁹"],
    hints=[
        "`n % 10` is the last digit of a non-negative number, and `n / 10` (integer division) removes it.",
        "Make `n` non-negative first, then loop: add the last digit, drop it, repeat until nothing is left.",
        "`n = abs(n); total = 0; while n > 0: total += n % 10; n //= 10`.",
    ],
    explanation=r"""
## Intuition

In base 10, the last digit of a number is its remainder when divided by 10, and dividing by 10 (discarding the fraction) shifts every digit one place to the right, dropping the last. Repeating those two operations peels the digits off one at a time, from right to left.

```text
 n      n % 10   n / 10
 472      2        47
 47       7        4
 4        4        0     ← stop: nothing left
```

## Approach

1. Replace `n` by its absolute value.
2. While `n > 0`: add `n % 10` to the total, then `n = n / 10`.
3. Return the total. (For `n = 0` the loop never runs, giving 0.)

```python
def digit_sum(n):
    n = abs(n)
    total = 0
    while n > 0:
        total += n % 10
        n //= 10
    return total
```

```c
long long digit_sum(long long n) {
    if (n < 0) n = -n;
    long long total = 0;
    while (n > 0) {
        total += n % 10;
        n /= 10;
    }
    return total;
}
```

```cpp
long long digitSum(long long n) {
    n = llabs(n);
    long long total = 0;
    for (; n > 0; n /= 10) total += n % 10;
    return total;
}
```

```rust
pub fn digit_sum(n: i64) -> i64 {
    let mut n = n.abs();
    let mut total = 0;
    while n > 0 {
        total += n % 10;
        n /= 10;
    }
    total
}
```

### Why take the absolute value first?

With a negative `n`, the remainder trap strikes. In C, `-472 % 10` is `-2` and the loop condition `n > 0` is false from the start, so you get 0. In Python, `-472 % 10` is `8` (floor semantics) and `-472 // 10` is `-48`; the loop never ends because `n` heads toward −1, not 0. Making `n` non-negative sidesteps both.

### `while` loops

A `while` loop repeats as long as its condition is true. Unlike `for i in range(...)`, you do not know in advance how many iterations there will be: it is the number of digits, which depends on `n`. Make sure something in the body moves toward the exit (`n /= 10`), or the loop runs forever.

## Complexity

O(d) where d is the number of digits, about log₁₀(n). For 2 × 10⁹ that is 10 iterations.

## Common mistakes

* **Not handling negatives** (wrong answer in C, infinite loop in Python).
* **Using `/` in Python** instead of `//`: `n / 10` produces a float, and the loop misbehaves.
* **Loop condition `n > 9`**: forgets to add the final digit.

## Going further

Repeat the digit sum until a single digit remains (the **digital root**: 472 → 13 → 4). There is a closed form: for positive n it is `1 + (n - 1) % 9`. Can you see why multiples of 9 relate to digit sums?
""",
    solution=r'''def digit_sum(n: int) -> int:
    # Work with the absolute value: the sign is not a digit, and Python's
    # floor-based // and % would otherwise walk a negative n toward -1
    # instead of 0, looping forever.
    n = abs(n)
    total = 0
    # Each iteration peels off the last digit: n % 10 reads it and n // 10
    # removes it. When n reaches 0 there are no digits left. For n == 0 the
    # loop never runs and the answer is correctly 0.
    while n > 0:
        total += n % 10
        n //= 10
    return total
''',
    refs={
        "c": r'''long long digit_sum(long long n) {
    if (n < 0) n = -n;          // C's % keeps the sign of n, so strip it first
    long long total = 0;
    while (n > 0) {
        total += n % 10;        // last digit
        n /= 10;                // drop it
    }
    return total;
}
''',
        "cpp": r'''long long digitSum(long long n) {
    n = llabs(n);               // llabs: absolute value of a long long
    long long total = 0;
    for (; n > 0; n /= 10) total += n % 10;
    return total;
}
''',
        "rust": r'''pub fn digit_sum(n: i64) -> i64 {
    let mut n = n.abs();        // shadow the parameter with a mutable copy
    let mut total = 0;
    while n > 0 {
        total += n % 10;
        n /= 10;
    }
    total
}
''',
        "espresso": r'''fn digitSum(n) {
    var m = n
    if m < 0 { m = -m }
    var total = 0
    while m > 0 {
        const q = m / 10
        total += m - q * 10     // m % 10, written without the % operator
        m = q
    }
    return total
}
''',
    },
    tests=[[472], [-472], [0], [7], [-9], [1000000000], [16777215], [-2000000000], [9876543], [10], [99999], [-1999999]],
))

# ----------------------------------------------------------------------------
# 12. Reverse an integer
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="reverse-integer-digits",
    title="Reverse an Integer",
    difficulty=1,
    tags=["digits", "modulo", "loops"],
    fn="reverse_digits",
    params=[["n", "int"]],
    returns="int",
    statement=r"""
Return the integer formed by reversing the decimal digits of `n`, keeping its sign. Leading zeros of the result disappear: reversing `120` gives `21`.

Examples: `1234 → 4321`, `-560 → -65`, `0 → 0`. Use arithmetic, not strings.
""",
    constraints=["-10⁹ < n < 10⁹"],
    hints=[
        "Peel digits off the end with `% 10` and `/ 10`, as in Digit Sum. Each digit you peel must go onto the end of the result.",
        "To append digit d to a number r, compute `r * 10 + d` (shifts r left one place, then fills the units).",
        "Remember the sign, work on `abs(n)`: `r = 0; while m > 0: r = r * 10 + m % 10; m //= 10`. Then restore the sign.",
    ],
    explanation=r"""
## Intuition

Two digit operations, used in opposite directions:

* **Remove** the last digit of `m`: `d = m % 10`, `m = m / 10`.
* **Append** a digit `d` to the end of `r`: `r = r * 10 + d`.

Taking digits off the back of `m` and pushing them onto the back of `r` reverses their order, like moving a stack of plates one at a time.

## Approach

1. Remember whether `n` is negative, and set `m = |n|`.
2. `r = 0`. While `m > 0`: `r = r * 10 + m % 10`, then `m = m / 10`.
3. Return `-r` if `n` was negative, else `r`.

Trace for `n = 1230`:

| m | digit | r after |
|---|---|---|
| 1230 | 0 | 0 |
| 123 | 3 | 3 |
| 12 | 2 | 32 |
| 1 | 1 | 321 |
| 0 | - | stop |

The trailing zero of 1230 becomes a leading zero of r, which simply disappears (0 × 10 + 0 = 0). No special handling needed.

```python
def reverse_digits(n):
    sign = -1 if n < 0 else 1
    m, r = abs(n), 0
    while m > 0:
        r = r * 10 + m % 10
        m //= 10
    return sign * r
```

```c
long long reverse_digits(long long n) {
    long long m = n < 0 ? -n : n, r = 0;
    while (m > 0) {
        r = r * 10 + m % 10;
        m /= 10;
    }
    return n < 0 ? -r : r;
}
```

```cpp
long long reverseDigits(long long n) {
    long long r = 0;
    for (long long m = llabs(n); m > 0; m /= 10) r = r * 10 + m % 10;
    return n < 0 ? -r : r;
}
```

```rust
pub fn reverse_digits(n: i64) -> i64 {
    let (mut m, mut r) = (n.abs(), 0i64);
    while m > 0 {
        r = r * 10 + m % 10;
        m /= 10;
    }
    if n < 0 { -r } else { r }
}
```

### A note on C's remainder

Because C's `%` and `/` truncate toward zero, the loop would actually work on a negative `n` directly in C, C++ and Rust: `-123 % 10 = -3`, and `r` builds up as `-3, -32, -321`, provided the loop condition is `m != 0` instead of `m > 0`. It does not work in Python (floor semantics). Working on the absolute value is the portable choice.

### Overflow

Reversing can make a number bigger: `1000000009` reversed is `9000000001`. With the constraint `|n| < 10⁹` every result has at most 9 digits, so it fits easily in 64 bits, and even in 32. The famous LeetCode variant asks you to detect 32-bit overflow before it happens; that requires checking `r > (INT_MAX - d) / 10` before each step.

## Complexity

O(d), the number of digits.

## Common mistakes

* **Building the result in the wrong order** (`r = r + d * 10`).
* **Losing the sign** of negative inputs.
* **Converting to a string** and back: works, but misses the point (and `-560` reversed as a string is `"065-"`).
* **Python `/`** instead of `//`.

## Going further

A number is a **palindrome** if it equals its reversal (`12321`). Use this function to test it. Then: how many digits does a number have? (Count iterations of the same loop.)
""",
    solution=r'''def reverse_digits(n: int) -> int:
    # Handle the sign separately: reverse the magnitude, then reapply it.
    sign = -1 if n < 0 else 1
    m = abs(n)
    r = 0
    while m > 0:
        # Move the last digit of m onto the end of r:
        #   m % 10   reads m's last digit
        #   r * 10   shifts r one place left, leaving room in the units
        r = r * 10 + m % 10
        m //= 10   # drop the digit we just used
    # Trailing zeros of n become leading zeros of r, which vanish naturally.
    return sign * r
''',
    refs={
        "c": r'''long long reverse_digits(long long n) {
    long long m = n < 0 ? -n : n;   // reverse the magnitude
    long long r = 0;
    while (m > 0) {
        r = r * 10 + m % 10;        // append m's last digit to r
        m /= 10;                    // and remove it from m
    }
    return n < 0 ? -r : r;          // restore the sign
}
''',
        "cpp": r'''long long reverseDigits(long long n) {
    long long r = 0;
    for (long long m = llabs(n); m > 0; m /= 10) r = r * 10 + m % 10;
    return n < 0 ? -r : r;
}
''',
        "rust": r'''pub fn reverse_digits(n: i64) -> i64 {
    let mut m = n.abs();
    let mut r: i64 = 0;
    while m > 0 {
        r = r * 10 + m % 10;
        m /= 10;
    }
    if n < 0 { -r } else { r }
}
''',
        "espresso": r'''fn reverseDigits(n) {
    var m = n
    if m < 0 { m = -m }
    var r = 0
    while m > 0 {
        const q = m / 10
        r = r * 10 + (m - q * 10)   // m - q*10 is the last digit (no % in ESPresso)
        m = q
    }
    if n < 0 { return -r }
    return r
}
''',
    },
    tests=[[1234], [-560], [0], [1230], [7], [-1], [100000], [9876543], [-1234567], [120], [-9000001], [10], [16000000]],
))

# ----------------------------------------------------------------------------
# 13. Greatest common divisor
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="greatest-common-divisor",
    title="Greatest Common Divisor",
    difficulty=1,
    tags=["gcd", "euclid", "loops", "number theory"],
    fn="gcd",
    params=[["a", "int"], ["b", "int"]],
    returns="int",
    statement=r"""
Return the **greatest common divisor** of `a` and `b`: the largest positive integer that divides both of them exactly.

By convention `gcd(a, 0) = a`. The inputs are never both zero.
""",
    constraints=["0 ≤ a, b ≤ 10⁹", "a + b > 0"],
    example_notes=["Divisors of 12: 1 2 3 4 6 12. Divisors of 18: 1 2 3 6 9 18. The largest common one is 6.", "Every number divides 0, so gcd(7, 0) = 7."],
    hints=[
        "A brute-force loop from min(a, b) downward works but can take a billion steps. There is a much faster idea.",
        "Any number that divides both a and b also divides a − b, and therefore also `a % b`. So gcd(a, b) = gcd(b, a % b).",
        "Euclid's algorithm: `while b != 0: a, b = b, a % b`; then `a` is the answer.",
    ],
    explanation=r"""
## Intuition

The obvious method, trying every candidate from `min(a, b)` down to 1, is correct but can take up to a billion steps. **Euclid's algorithm**, more than 2000 years old, does it in a few dozen.

The key fact: if `d` divides both `a` and `b`, it also divides `a - b`, `a - 2b`, ..., and in particular `a % b` (which is `a` minus some multiple of `b`). The reverse also holds. So the pair `(a, b)` and the pair `(b, a % b)` have **exactly the same common divisors**, and therefore the same gcd. Each step makes the numbers smaller, and when the second one reaches 0 we use `gcd(a, 0) = a`.

## Approach

```python
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a
```

Trace for `gcd(48, 18)`:

| a | b | a % b |
|---|---|---|
| 48 | 18 | 12 |
| 18 | 12 | 6 |
| 12 | 6 | 0 |
| 6 | 0 | stop: answer 6 |

If `a < b`, the first step just swaps them: `gcd(18, 48)` → `(48, 18 % 48 = 18)`.

```c
long long gcd(long long a, long long b) {
    while (b != 0) {
        long long t = a % b;    // C has no tuple assignment: use a temporary
        a = b;
        b = t;
    }
    return a;
}
```

```cpp
long long gcd(long long a, long long b) {
    return b == 0 ? a : gcd(b, a % b);     // the recursive form
}
```

```rust
pub fn gcd(a: i64, b: i64) -> i64 {
    let (mut a, mut b) = (a, b);
    while b != 0 {
        (a, b) = (b, a % b);    // destructuring assignment
    }
    a
}
```

### Simultaneous assignment

`a, b = b, a % b` evaluates **both** right-hand values first, then assigns. Writing `a = b; b = a % b;` is a bug: by the second line `a` already holds the new value, so you compute `b % b = 0`. In C you need a temporary variable.

### Recursion

The C++ version is **recursive**: the function calls itself with smaller arguments until reaching the base case `b == 0`. It is a direct transcription of the mathematical rule. Euclid's recursion is shallow (dozens of levels at most), so there is no stack risk.

### LCM for free

The **least common multiple** follows from the gcd: `lcm(a, b) = a / gcd(a, b) * b`. Divide **before** multiplying: `a * b` first could overflow even when the final LCM fits.

## Complexity

O(log(min(a, b))) iterations: the remainder at least halves every two steps. For values near 10⁹ that is at most about 45 iterations. The worst case is consecutive Fibonacci numbers. O(1) space.

## Common mistakes

* **Sequential assignment** instead of simultaneous (see above).
* **Dividing by zero**: `a % b` with `b == 0`. The loop condition protects you; a brute-force version starting from `min(a, b)` would return 0 for `gcd(7, 0)`.
* **Brute force** on large inputs: correct but slow.

## Going further

Built-ins: Python `math.gcd`, C++17 `std::gcd`. The **extended** Euclidean algorithm also finds integers x, y with `a·x + b·y = gcd(a, b)`, the basis of modular inverses and RSA.
""",
    solution=r'''def gcd(a: int, b: int) -> int:
    # Euclid's algorithm. Any common divisor of a and b also divides
    # a % b (which is a minus a multiple of b), and vice versa, so
    # gcd(a, b) == gcd(b, a % b). The numbers shrink quickly, and once the
    # second one is 0 we use gcd(a, 0) == a.
    while b != 0:
        # Simultaneous assignment: both right-hand values are computed from
        # the OLD a and b before either variable changes.
        a, b = b, a % b
    return a
''',
    refs={
        "c": r'''long long gcd(long long a, long long b) {
    while (b != 0) {
        long long t = a % b;   // compute from the old values first
        a = b;
        b = t;
    }
    return a;                  // gcd(a, 0) == a
}
''',
        "cpp": r'''long long gcd(long long a, long long b) {
    // Recursive form: the base case b == 0 ends the recursion.
    return b == 0 ? a : gcd(b, a % b);
}
''',
        "rust": r'''pub fn gcd(a: i64, b: i64) -> i64 {
    let (mut a, mut b) = (a, b);
    while b != 0 {
        (a, b) = (b, a % b);   // destructuring assignment (Rust 1.59+)
    }
    a
}
''',
        "espresso": r'''fn gcd(a, b) {
    var x = a
    var y = b
    while y != 0 {
        const r = x - (x / y) * y   // x % y without the % operator
        x = y
        y = r
    }
    return x
}
''',
    },
    tests=[[48, 18], [18, 48], [7, 0], [0, 9], [17, 5], [100, 100], [1, 1000000000], [16777215, 16777214],
           [832040, 514229], [14348907, 9565938], [12, 8], [1000000000, 500000000]],
))

# ----------------------------------------------------------------------------
# 14. Is prime
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="is-prime-number",
    title="Is It Prime?",
    difficulty=1,
    tags=["primes", "loops", "number theory"],
    # The large-prime tests (~10^9) are essential here, and ESPresso parses
    # integer literals through a float, so they would arrive corrupted.
    espresso=False,
    fn="is_prime",
    params=[["n", "int"]],
    returns="bool",
    statement=r"""
A **prime** is an integer greater than 1 whose only positive divisors are 1 and itself: 2, 3, 5, 7, 11, ...

Return whether `n` is prime. Note that 0, 1 and negative numbers are not prime.

`n` can be close to a billion, so checking every possible divisor up to `n` is too slow.
""",
    constraints=["-10⁹ ≤ n ≤ 10⁹"],
    hints=[
        "Handle n < 2 first: those are never prime.",
        "Divisors come in pairs: if d divides n, so does n / d, and one of the two is at most √n. So you only need to test d up to √n.",
        "Loop `d = 2, 3, 4, ...` while `d * d <= n`; if `n % d == 0` return false. If the loop finishes, return true.",
    ],
    explanation=r"""
## Intuition

To prove `n` is **not** prime you only need one divisor between 2 and n − 1. The naive search tries all of them: up to a billion checks. But divisors come in **pairs**: if `d × e = n`, then one of `d` and `e` is at most √n (if both were bigger, their product would exceed n). So if `n` has any divisor other than 1 and itself, it has one **no larger than √n**. For n ≈ 10⁹, √n ≈ 31623: thirty thousand checks instead of a billion.

```text
 n = 36:   1×36  2×18  3×12  4×9  6×6 | 9×4  12×3 ...
                                     √36 = 6: the pairs mirror after this
```

## Approach

1. If `n < 2`, return false.
2. For `d = 2, 3, ...` while `d * d <= n`: if `n % d == 0`, return false.
3. Return true.

```python
def is_prime(n):
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True
```

```c
bool is_prime(long long n) {
    if (n < 2) return false;
    for (long long d = 2; d * d <= n; d++)
        if (n % d == 0) return false;
    return true;
}
```

```cpp
bool isPrime(long long n) {
    if (n < 2) return false;
    if (n % 2 == 0) return n == 2;              // even: only 2 is prime
    for (long long d = 3; d * d <= n; d += 2)   // then odd divisors only
        if (n % d == 0) return false;
    return true;
}
```

```rust
pub fn is_prime(n: i64) -> bool {
    if n < 2 { return false; }
    let mut d = 2;
    while d * d <= n {
        if n % d == 0 { return false; }
        d += 1;
    }
    true
}
```

Trace for `n = 91`:

| d | d² ≤ 91? | 91 % d |
|---|---|---|
| 2 | yes | 1 |
| 3 | yes | 1 |
| ... | | |
| 7 | yes | **0** → not prime (91 = 7 × 13) |

For `n = 97`, d goes 2..9 (since 10² = 100 > 97), nothing divides, so 97 is prime.

### `d * d <= n` instead of `d <= sqrt(n)`

Both express the same bound, but `sqrt` works in floating point and can be off by a tiny amount for large perfect squares, missing the divisor exactly at √n. Squaring an integer is exact. (In a language with 32-bit integers, `d * d` could itself overflow near 46341², which is why the bound is safe only because n ≤ 10⁹ here.)

### Skipping even numbers

After checking 2, no other even number can be a divisor (they would all be multiples of 2), so the C++ version tests only odd `d`, halving the work.

## Complexity

O(√n) time, O(1) space. For n ≤ 10⁹, about 31,623 iterations at worst (or half that with the odd-only trick).

## Common mistakes

* **Calling 1 (or 0, or negatives) prime.**
* **Looping to `n` or `n/2`**: correct but far too slow for large primes like 999,999,937.
* **`d * d < n`** (strict): misses perfect squares like 49 = 7 × 7.
* **Starting at `d = 1`**: everything is divisible by 1.

## Going further

To find **all** primes up to N, testing each number separately costs O(N√N). The **Sieve of Eratosthenes** crosses out multiples of each prime and runs in O(N log log N). It appears in a later track.
""",
    solution=r'''def is_prime(n: int) -> bool:
    # By definition primes are > 1, so 1, 0 and negatives are excluded.
    if n < 2:
        return False
    # Divisors pair up as d * (n // d); the smaller of each pair is <= sqrt(n).
    # So if no d with d*d <= n divides n, nothing (other than 1 and n) does.
    # Using d * d <= n avoids floating-point sqrt and its rounding issues.
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False      # found a divisor: definitely not prime
        d += 1
    return True
''',
    refs={
        "c": r'''bool is_prime(long long n) {
    if (n < 2) return false;
    if (n % 2 == 0) return n == 2;         // the only even prime
    // Only odd candidates up to sqrt(n); d * d is exact, unlike sqrt().
    for (long long d = 3; d * d <= n; d += 2) {
        if (n % d == 0) return false;
    }
    return true;
}
''',
        "cpp": r'''bool isPrime(long long n) {
    if (n < 2) return false;
    if (n % 2 == 0) return n == 2;
    for (long long d = 3; d * d <= n; d += 2)
        if (n % d == 0) return false;
    return true;
}
''',
        "rust": r'''pub fn is_prime(n: i64) -> bool {
    if n < 2 {
        return false;
    }
    let mut d: i64 = 2;
    while d * d <= n {
        if n % d == 0 {
            return false;
        }
        d += 1;
    }
    true
}
''',
    },
    tests=[[2], [3], [4], [1], [0], [-7], [97], [91], [49], [999999937], [1000000000], [7919], [25], [999999929]],
))

# ----------------------------------------------------------------------------
# 15. Power by loop
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="power-by-loop",
    title="Power with a Loop",
    difficulty=0,
    tags=["loops", "accumulator", "arithmetic"],
    fn="power",
    params=[["base", "int"], ["exponent", "int"]],
    returns="int",
    statement=r"""
Return `base` raised to the power `exponent` (`base` multiplied by itself `exponent` times), computed with a loop rather than a built-in power function.

Any number to the power 0 is 1, including `0⁰ = 1` by convention.
""",
    constraints=["-100 ≤ base ≤ 100", "0 ≤ exponent ≤ 30", "|baseᵉˣᵖᵒⁿᵉⁿᵗ| < 2³¹"],
    example_notes=["2 × 2 × 2 × 2 × 2 × 2 × 2 × 2 × 2 × 2 = 1024.", "Anything to the power 0 is 1."],
    hints=[
        "This is the accumulator pattern with multiplication instead of addition.",
        "What should the accumulator start at? For sums it was 0. For products, the neutral value is 1.",
        "`result = 1`, then repeat `exponent` times: `result *= base`. Return `result`.",
    ],
    explanation=r"""
## Intuition

Exponentiation is repeated multiplication, just as multiplication is repeated addition. So the solution is the accumulator pattern you used for sums, with two changes: the operation is `*`, and the starting value is **1**, the neutral element of multiplication (multiplying by 1 changes nothing, just as adding 0 changes nothing).

Starting from 1 also gives the right answer for `exponent = 0` for free: the loop runs zero times and 1 is returned.

## Approach

```python
def power(base, exponent):
    result = 1
    for _ in range(exponent):   # _ : a loop variable we do not need
        result *= base
    return result
```

```c
long long power(long long base, long long exponent) {
    long long result = 1;
    for (long long i = 0; i < exponent; i++) result *= base;
    return result;
}
```

```cpp
long long power(long long base, long long exponent) {
    long long result = 1;
    while (exponent-- > 0) result *= base;   // count down to zero
    return result;
}
```

```rust
pub fn power(base: i64, exponent: i64) -> i64 {
    let mut result = 1;
    for _ in 0..exponent {
        result *= base;
    }
    result
}
```

Trace for `power(-3, 3)`:

| iteration | result |
|---|---|
| start | 1 |
| 1 | -3 |
| 2 | 9 |
| 3 | -27 |

A negative base alternates sign: odd exponents give negative results, even give positive.

### Why not `pow`?

C's `pow` (and C++'s `std::pow`) works with **doubles**. For large results a double cannot represent every integer exactly (beyond 2⁵³), and converting back to an integer can be off by one. Integer powers should be computed with integer arithmetic. Python's `**` and Rust's `base.pow(exp)` are integer-exact and fine to use in real code.

### Faster: exponentiation by squaring

The loop does `exponent` multiplications. Squaring does it in about log₂(exponent):

```python
def fast_power(b, e):
    result = 1
    while e > 0:
        if e % 2 == 1:     # odd exponent: peel off one factor of b
            result *= b
        b *= b             # square the base
        e //= 2            # halve the exponent
    return result
```

For exponent 30 that is 5 rounds instead of 30 multiplications. It is the standard technique for modular exponentiation with huge exponents, and you will meet it again.

## Complexity

O(exponent) multiplications with the simple loop; O(log exponent) with squaring. O(1) space.

## Common mistakes

* **Starting at 0**: everything becomes 0.
* **Looping `exponent + 1` times** (e.g. `range(exponent + 1)` or `i <= exponent`): one factor too many.
* **Using `^`**: that is XOR, not power.
* **Floating-point `pow`** for integer results.

## Going further

Implement `fast_power` above and verify it against the loop. Then compute the last 9 digits of 2¹⁰⁰⁰ by taking `% 1000000000` after each multiplication: this is **modular exponentiation**, which keeps numbers small no matter how big the exponent is.
""",
    solution=r'''def power(base: int, exponent: int) -> int:
    # Repeated multiplication: an accumulator that starts at 1, the neutral
    # element for *, just as 0 is the neutral element for +.
    # With exponent == 0 the loop never runs and 1 is returned, which also
    # covers the 0 ** 0 == 1 convention.
    result = 1
    for _ in range(exponent):      # exactly `exponent` multiplications
        result *= base
    return result
''',
    refs={
        "c": r'''long long power(long long base, long long exponent) {
    // Integer loop instead of pow(): pow works with doubles and can
    // round large results to the wrong integer.
    long long result = 1;
    for (long long i = 0; i < exponent; i++) {
        result *= base;
    }
    return result;
}
''',
        "cpp": r'''long long power(long long base, long long exponent) {
    // Exponentiation by squaring: O(log exponent) multiplications.
    long long result = 1;
    while (exponent > 0) {
        if (exponent & 1) result *= base;   // odd: use one factor of base
        exponent >>= 1;                     // halve the exponent
        if (exponent > 0) base *= base;     // square (skipped after the last bit)
    }
    return result;
}
''',
        "rust": r'''pub fn power(base: i64, exponent: i64) -> i64 {
    let mut result: i64 = 1;
    for _ in 0..exponent {
        result *= base;
    }
    result
}
''',
        "espresso": r'''fn power(base, exponent) {
    var result = 1
    for var i in 0..exponent {
        result *= base
    }
    return result
}
''',
    },
    tests=[[2, 10], [3, 0], [0, 0], [0, 5], [-3, 3], [-2, 30], [1, 30], [-1, 29], [10, 9], [7, 11], [5, 1], [-100, 4], [2, 30]],
))
