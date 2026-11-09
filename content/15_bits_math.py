"""Track 15: Bits & Number Theory."""
import random

TRACK = dict(
    id="bits-math",
    title="Bits & Number Theory",
    order=15,
    icon="⊕",
    blurb="Two's complement, masks and shifts, XOR tricks, sieves, fast exponentiation and modular arithmetic.",
    intro=r"""
Every integer your program touches is a row of bits. Most of the time the language hides
that; this track is about the problems where looking at the bits (or at the arithmetic
that sits under them) turns an O(n) or O(n log n) idea into an O(1) or O(log n) one.

## Two's complement

A fixed-width signed integer of `w` bits stores `x` as `x mod 2^w`. With `w = 8`:

```text
  value   bits        how to read it
     5    0000 0101   4 + 1
     1    0000 0001
     0    0000 0000
    -1    1111 1111   -128 + 64 + 32 + 16 + 8 + 4 + 2 + 1
    -5    1111 1011   -128 + 123
  -128    1000 0000   the most negative value has no positive twin
   127    0111 1111   the most positive value
```

The top bit has weight `-2^(w-1)` instead of `+2^(w-1)`; every other bit keeps its
usual weight. Two consequences you will use all the time:

* **Negation is `~x + 1`.** Flip every bit, add one: `5 = 0000 0101 → 1111 1010 → 1111 1011 = -5`.
* **Addition does not care about signedness.** The adder that computes `3 + 250` for
  unsigned bytes computes `3 + (-6)` for signed bytes with exactly the same bits. That is
  why the "sum without `+`" problem works for negative numbers too.

## Operators

| op | meaning | example (8-bit) |
|---|---|---|
| `a & b` | 1 where both are 1 | `1100 & 1010 = 1000` |
| `a \| b` | 1 where either is 1 | `1100 \| 1010 = 1110` |
| `a ^ b` | 1 where they differ | `1100 ^ 1010 = 0110` |
| `~a` | flip every bit | `~0000 0101 = 1111 1010` |
| `a << k` | shift left, fill with 0 (×2ᵏ) | `0000 0011 << 2 = 0000 1100` |
| `a >> k` | shift right (÷2ᵏ, rounds toward −∞ for signed) | `1111 1000 >> 1 = 1111 1100` |

Right shifts of negative numbers are *arithmetic* (the sign bit is copied in) in Python,
Rust (`i64`) and every compiler you will meet for C/C++ (guaranteed since C++20). Shift an
**unsigned** type when you want zeros shifted in (`u32` in Rust, `uint32_t` in C).

## Masks and the classic tricks

```text
bit k is set?        (x >> k) & 1
set bit k            x | (1 << k)
clear bit k          x & ~(1 << k)
toggle bit k         x ^ (1 << k)
low k bits           x & ((1 << k) - 1)
```

Two tricks are worth memorising because they show up everywhere:

```text
x         = 0101 1000
x - 1     = 0101 0111    borrowing flips the lowest 1 and everything below it
x & (x-1) = 0101 0000    → clears the lowest set bit
-x        = 1010 1000    (~x + 1)
x & -x    = 0000 1000    → isolates the lowest set bit
```

* `x & (x - 1) == 0` (and `x > 0`) means "x is a power of two". Repeating `x &= x - 1`
  counts set bits in as many steps as there are ones (Kernighan's trick).
* `x & -x` is the heart of the Fenwick tree in the next track.
* XOR is its own inverse: `a ^ a = 0`, `a ^ 0 = a`, and it is commutative and associative,
  so XOR-ing a whole list cancels every value that appears an even number of times.

## Integer widths and overflow, language by language

| language | `int` here | on overflow |
|---|---|---|
| Python | arbitrary precision | never overflows; `~x` is `-x-1`, `-1 >> 5` is `-1` forever |
| C / C++ | `long long` (64-bit) | **signed overflow is undefined behaviour**; unsigned wraps mod 2⁶⁴ |
| Rust | `i64` | panics in debug builds, wraps in release; say what you mean with `wrapping_add`, `checked_mul`, `overflowing_sub` |
| ESPresso | numbers exact only up to ~2²⁴ | no bitwise operators at all, so bit problems here use arithmetic |

Python's bigints are a trap for bit problems that assume a width. `~5` is `-6`, which is
correct, but if a problem says "32-bit unsigned" you must mask yourself:

```python
MASK = 0xFFFFFFFF
x = (~5) & MASK          # 4294967290, the 32-bit pattern 1111...1010
signed = x - (1 << 32) if x >> 31 else x   # reinterpret as signed int32 → -6
```

In C, *undefined* means the optimiser may assume overflow never happens and delete your
overflow check. Do the risky arithmetic in an unsigned type (`uint32_t`, `uint64_t`),
which is defined to wrap, and convert at the end. In Rust, plain `+` that overflows is a
bug the compiler will catch in debug mode; the explicit methods document intent:

```rust
let a: i32 = i32::MAX;
let w = a.wrapping_add(1);        // i32::MIN, on purpose
let c = a.checked_add(1);         // None
let m = (a as i64) * (a as i64);  // widen before multiplying
```

## Modular arithmetic

When answers get astronomically large, problems ask for them "mod M" (usually
`M = 1_000_000_007`, a prime that fits in 30 bits). The rules:

```text
(a + b) mod M = ((a mod M) + (b mod M)) mod M
(a · b) mod M = ((a mod M) · (b mod M)) mod M
```

Reduce after **every** operation so values stay below `M`. Then a product of two reduced
values is below `M² ≈ 10¹⁸`, which still fits in a signed 64-bit integer (max ≈ 9.2·10¹⁸).
Subtraction needs care because `%` in C, C++ and Rust keeps the sign of the dividend:
write `((a - b) % M + M) % M`. Python's `%` always returns a non-negative result for a
positive modulus.

Division does not distribute. To divide by `b` mod a prime `M`, multiply by `b^(M-2)`
(Fermat's little theorem), which you compute with **fast exponentiation**: square the base,
halve the exponent, multiply into the answer when the current exponent bit is 1. That takes
O(log e) multiplications instead of e, and the same idea raises a 2×2 matrix to the
n-th power to get Fibonacci numbers in O(log n).

## Number theory toolbox

* **Sieve of Eratosthenes**: cross out multiples of each prime starting at p², O(n log log n).
* **Positional systems**: `n = Σ dᵢ·bⁱ`; peel digits with `n % b`, `n / b`. Excel columns are
  the odd one out: a *bijective* base 26 with digits 1..26 and no zero.
* **Binomial coefficients**: Pascal's rule `C(n,k) = C(n-1,k-1) + C(n-1,k)` builds a row in
  place if you sweep right to left.

Watch for the clue words: "without using `+`", "appears twice", "power of", "32-bit",
"mod 10⁹+7", "n up to 10¹⁵". Each one is pointing at a tool on this page.
""",
)



def _rng(seed):
    return random.Random(seed)


# ----------------------------------------------------------------- single number
def _single_tests():
    r = _rng(1501)
    big = []
    vals = r.sample(range(-10**9, 10**9), 2001)
    for v in vals[:-1]:
        big += [v, v]
    big.append(vals[-1])
    r.shuffle(big)
    return [
        [[2, 2, 1]],
        [[4, 1, 2, 1, 2]],
        [[1]],
        [[-1, -1, -2]],
        [[0, 7, 7]],
        [[-7, 3, -7, 0, 0]],
        [[1000000000, -1000000000, 1000000000]],
        [big],
    ]


P_SINGLE = dict(
    id="single-number-xor",
    title="Single Number",
    difficulty=1,
    tags=["bits", "xor"],
    fn="single_number",
    params=[["nums", "int[]"]],
    returns="int",
    espresso=False,
    statement=r"""
Every value in `nums` appears **exactly twice**, except for one value that appears exactly
once. Return that lonely value.

Aim for **O(n) time and O(1) extra space**: no hash set, no sorting.
""",
    constraints=["1 ≤ len(nums) ≤ 4001, and len(nums) is odd",
                 "-10⁹ ≤ nums[i] ≤ 10⁹"],
    example_notes=["`2` appears twice and cancels; `1` is left.",
                   "The pairs `1,1` and `2,2` cancel no matter where they sit; `4` survives."],
    hints=[
        "Is there an operation where combining a value with itself gives a neutral element?",
        "`a ^ a == 0` and `a ^ 0 == a`. XOR is also commutative and associative, so order does not matter.",
        "XOR every element together. Each pair cancels to 0 and the single value is what remains.",
    ],
    explanation=r"""
## Intuition

"Every element appears twice except one" is the classic XOR clue. We want an operation
that *cancels* a value when it is applied twice, regardless of what happened in between.
XOR is exactly that: `a ^ a = 0`, `a ^ 0 = a`, and because it is commutative and
associative, `4 ^ 1 ^ 2 ^ 1 ^ 2` can be regrouped as `4 ^ (1 ^ 1) ^ (2 ^ 2) = 4 ^ 0 ^ 0 = 4`.

Think of XOR bit by bit: each bit of the running result is the *parity* of how many
inputs had that bit set. Pairs contribute an even count to every bit, so only the single
value's bits survive.

## Approach

1. `acc = 0`.
2. For each `x`, `acc ^= x`.
3. Return `acc`.

Trace for `[4, 1, 2, 1, 2]` (4-bit view):

| x | x bits | acc after |
|---|---|---|
| 4 | 0100 | 0100 |
| 1 | 0001 | 0101 |
| 2 | 0010 | 0111 |
| 1 | 0001 | 0110 |
| 2 | 0010 | 0100 = 4 |

Negative numbers work identically: their two's complement bit patterns pair up and cancel
just like positive ones. In Python, `-7 ^ -7 == 0` even though ints are unbounded, because
Python's XOR behaves as if negative numbers had infinitely many leading 1 bits.

## Complexity

* **Time:** O(n), one XOR per element.
* **Space:** O(1), one accumulator.

A hash set (O(n) space) or sorting (O(n log n)) also work but miss the point.

## Common mistakes

* Starting the accumulator at something other than 0 (0 is XOR's identity).
* Using `+`/`-` tricks like `2·sum(set) - sum(nums)`: correct but uses O(n) space and can
  overflow in C.
* Confusing `^` with exponentiation. In C, C++, Rust and Python, `^` is XOR; `**`/`pow` is power.

## Going further

* **Single Number II**: every value appears *three* times except one. Count each bit
  position mod 3, or use the two-mask state machine `ones = (ones ^ x) & ~twos; twos = (twos ^ x) & ~ones`.
* **Single Number III**: two values appear once. XOR everything to get `a ^ b`, take its
  lowest set bit `d = s & -s`, and split the array into "bit d set" and "bit d clear";
  each half contains exactly one of the singles.
""",
    solution=r'''def single_number(nums):
    # XOR is its own inverse: x ^ x == 0 and x ^ 0 == x.
    # It is also commutative and associative, so the order of the array is
    # irrelevant: every value that appears twice cancels itself out.
    acc = 0                      # 0 is the identity element for XOR
    for x in nums:
        acc ^= x                 # each bit of acc = parity of that bit so far
    # Only the value that appeared an odd number of times (once) survives.
    return acc
''',
    refs={
        "c": r"""long long single_number(long long* nums, int numsSize) {
    // XOR all values: pairs cancel (x ^ x == 0), the single value remains.
    long long acc = 0;
    for (int i = 0; i < numsSize; i++) acc ^= nums[i];
    return acc;
}""",
        "cpp": r"""long long singleNumber(vector<long long>& nums) {
    // std::accumulate with bit_xor folds the whole array with ^.
    // Pairs cancel, the unique value survives.
    return accumulate(nums.begin(), nums.end(), 0LL, bit_xor<long long>());
}""",
        "rust": r"""pub fn single_number(nums: Vec<i64>) -> i64 {
    // fold with XOR: 0 is the identity, every duplicated value cancels.
    nums.iter().fold(0, |acc, &x| acc ^ x)
}""",
    },
    tests=_single_tests(),
)


# ----------------------------------------------------------------- popcount
P_POPCOUNT = dict(
    id="number-of-one-bits",
    title="Number of 1 Bits",
    difficulty=1,
    tags=["bits", "popcount"],
    fn="hamming_weight",
    params=[["n", "int"]],
    returns="int",
    statement=r"""
Return the number of `1` bits in the binary representation of the non-negative integer
`n` (its *Hamming weight* or *population count*).

Try to do it without converting `n` to a string.
""",
    constraints=["0 ≤ n < 2²⁴ = 16 777 216"],
    example_notes=["`11 = 1011₂` has three 1 bits.", "`128 = 1000 0000₂` has a single 1 bit."],
    hints=[
        "You can inspect the lowest bit with `n & 1` (or `n % 2`) and then discard it with `n >> 1` (or `n // 2`).",
        "That loop runs once per bit position. Can you make it run once per *set* bit instead?",
        "`n & (n - 1)` clears the lowest set bit. Count how many times you can do that before `n` becomes 0.",
    ],
    explanation=r"""
## Intuition

Counting ones is a loop over bits. The plain version looks at every bit position; the
clever version (Brian Kernighan's) jumps straight from one set bit to the next using the
fact that subtracting 1 flips the lowest set bit and every zero below it:

```text
n         = 1011 0100
n - 1     = 1011 0011
n & (n-1) = 1011 0000     lowest 1 is gone, everything else unchanged
```

## Approach

**Shift and test** (works in any language, even with only `%` and `/`):

```python
count = 0
while n:
    count += n & 1     # or n % 2
    n >>= 1            # or n // 2
```

**Kernighan** (what the reference uses):

1. `count = 0`.
2. While `n != 0`: `n &= n - 1`, `count += 1`.

Trace for `n = 11`:

| step | n (binary) | n & (n−1) | count |
|---|---|---|---|
| 1 | 1011 | 1010 | 1 |
| 2 | 1010 | 1000 | 2 |
| 3 | 1000 | 0000 | 3 |

## Complexity

* **Time:** O(number of set bits) for Kernighan, O(number of bits) ≤ 24 here for shifting. Both are O(1) for fixed width.
* **Space:** O(1).

Hardware has a single instruction for this (`popcnt` on x86, `cnt` on ARM64 NEON).
`__builtin_popcountll` (C/C++), `std::popcount` (C++20), `u64::count_ones` (Rust) and
`int.bit_count()` (Python 3.10+) compile to it or to an equally fast bit-twiddling formula.

## Common mistakes

* **Negative inputs in Python.** `n >>= 1` on a negative Python int never reaches 0
  (`-1 >> 1 == -1`), so the loop never ends. This problem keeps `n ≥ 0`; for a fixed-width
  count of a negative value, mask first: `n & 0xFFFFFFFF`.
* **Signed shifts in C.** Right-shifting a negative `long long` copies the sign bit in;
  cast to `unsigned long long` before shifting if negatives are possible.
* Using `n / 2` in a language where `/` is floating-point division (JavaScript, Python 3 `/`).

## Going further

* **SWAR popcount**: `x - ((x >> 1) & 0x55555555)` then sum adjacent 2-bit, 4-bit, 8-bit
  fields with masks `0x33333333`, `0x0F0F0F0F`, and multiply by `0x01010101`; branch-free and constant time.
* **Hamming distance** between `a` and `b` is `popcount(a ^ b)`.
""",
    solution=r'''def hamming_weight(n):
    # Brian Kernighan's trick: n & (n - 1) clears the lowest set bit.
    # Subtracting 1 turns the lowest 1 into 0 and all the 0s below it into 1s;
    # AND-ing with the original wipes out exactly that lowest 1.
    # So the loop body runs once per set bit, not once per bit position.
    count = 0
    while n:                 # n >= 0 here, so this terminates
        n &= n - 1           # drop the lowest 1 bit
        count += 1
    return count
''',
    refs={
        "c": r"""long long hamming_weight(long long n) {
    // Work on an unsigned copy: shifting/masking unsigned values is always well defined.
    unsigned long long x = (unsigned long long)n;
    long long count = 0;
    while (x) {
        x &= x - 1;   // clear the lowest set bit
        count++;
    }
    return count;
}""",
        "cpp": r"""long long hammingWeight(long long n) {
    // Kernighan: one iteration per set bit.
    // (std::popcount((unsigned long long)n) from <bit> does the same in one instruction.)
    long long count = 0;
    for (unsigned long long x = n; x; x &= x - 1) count++;
    return count;
}""",
        "rust": r"""pub fn hamming_weight(n: i64) -> i64 {
    // Kernighan's loop. The idiomatic one-liner is (n as u64).count_ones() as i64.
    let mut x = n as u64;   // unsigned: no sign bit surprises
    let mut count = 0;
    while x != 0 {
        x &= x - 1;         // clear lowest set bit; x > 0 so x - 1 never underflows
        count += 1;
    }
    count
}""",
        "espresso": r"""// ESPresso has no bitwise operators, so peel bits off arithmetically:
// the lowest bit is n mod 2, and integer division by 2 shifts right.
fn hammingWeight(n) {
  var x = n
  var count = 0
  while x > 0 {
    count += x - (x / 2) * 2   // x mod 2 (no % operator in ESPresso)
    x = x / 2                  // drop the lowest bit
  }
  return count
}""",
    },
    tests=[[11], [128], [0], [1], [16777215], [16777213], [5592405], [255], [1 << 23], [9876543], [10000000]],
)


# ----------------------------------------------------------------- counting bits
P_COUNTBITS = dict(
    id="counting-bits-table",
    title="Counting Bits",
    difficulty=1,
    tags=["bits", "dynamic programming"],
    fn="count_bits",
    params=[["n", "int"]],
    returns="int[]",
    statement=r"""
Given `n`, return an array `ans` of length `n + 1` where `ans[i]` is the number of `1`
bits in the binary representation of `i`, for every `0 ≤ i ≤ n`.

Can you do it in a single O(n) pass, without calling a popcount function on each number?
""",
    constraints=["0 ≤ n ≤ 10⁴"],
    example_notes=["`0 → 0`, `1 → 1`, `10₂ → 1`.", "`3 = 11₂` and `5 = 101₂` both have two 1 bits."],
    hints=[
        "Calling a popcount on each number is O(n log n). Can `ans[i]` be built from an answer you already have?",
        "`i >> 1` is `i` with its lowest bit removed, and it is smaller than `i`.",
        "`ans[i] = ans[i >> 1] + (i & 1)`. Alternatively `ans[i] = ans[i & (i - 1)] + 1`.",
    ],
    explanation=r"""
## Intuition

The answers for small numbers already contain the answers for big numbers. Dropping the
last bit of `i` gives `i >> 1`, a smaller number whose count we computed earlier; we only
need to add back the bit we dropped. This is dynamic programming where the "subproblem" is
literally a prefix of the bit string.

```text
i = 13 = 1101
i >> 1 =  110 = 6   (ans[6] = 2)
i & 1  =    1
ans[13] = 2 + 1 = 3
```

## Approach

1. `ans = [0] * (n + 1)`.
2. For `i` from 1 to `n`: `ans[i] = ans[i >> 1] + (i & 1)`.

Trace up to 7:

| i | binary | i>>1 | ans[i>>1] | i&1 | ans[i] |
|---|---|---|---|---|---|
| 1 | 1 | 0 | 0 | 1 | 1 |
| 2 | 10 | 1 | 1 | 0 | 1 |
| 3 | 11 | 1 | 1 | 1 | 2 |
| 4 | 100 | 2 | 1 | 0 | 1 |
| 5 | 101 | 2 | 1 | 1 | 2 |
| 6 | 110 | 3 | 2 | 0 | 2 |
| 7 | 111 | 3 | 2 | 1 | 3 |

Equivalent recurrences: `ans[i] = ans[i & (i - 1)] + 1` (remove the lowest set bit) or
`ans[i] = ans[i - highest_power_of_two_≤_i] + 1`.

## Complexity

* **Time:** O(n), constant work per entry.
* **Space:** O(n) for the output (no extra beyond it).

## Common mistakes

* Allocating `n` entries instead of `n + 1` (the range is inclusive).
* `n = 0` must return `[0]`, not `[]`.
* In C, forgetting to set `*returnSize` or returning a stack array.

## Going further

The same "build from a smaller index" idea powers subset DP over bitmasks:
`dp[mask]` is often computed from `dp[mask & (mask - 1)]` or `dp[mask ^ (1 << j)]`,
as you will see in the traveling-salesman problem of the next track.
""",
    solution=r'''def count_bits(n):
    ans = [0] * (n + 1)          # inclusive range 0..n, and ans[0] = 0
    for i in range(1, n + 1):
        # i >> 1 drops the lowest bit; that number is smaller, so its answer
        # is already known. Add back the dropped bit (i & 1).
        ans[i] = ans[i >> 1] + (i & 1)
    return ans
''',
    refs={
        "c": r"""long long* count_bits(long long n, int* returnSize) {
    long long* ans = malloc(sizeof(long long) * (n + 1));   // caller frees
    ans[0] = 0;
    for (long long i = 1; i <= n; i++)
        ans[i] = ans[i >> 1] + (i & 1);   // reuse the answer for i without its last bit
    *returnSize = (int)(n + 1);
    return ans;
}""",
        "cpp": r"""vector<long long> countBits(long long n) {
    vector<long long> ans(n + 1, 0);
    // Remove the lowest SET bit this time: i & (i - 1) < i, plus one for that bit.
    for (long long i = 1; i <= n; i++) ans[i] = ans[i & (i - 1)] + 1;
    return ans;
}""",
        "rust": r"""pub fn count_bits(n: i64) -> Vec<i64> {
    let n = n as usize;
    let mut ans = vec![0i64; n + 1];
    for i in 1..=n {
        ans[i] = ans[i >> 1] + (i & 1) as i64;   // drop last bit, add it back
    }
    ans
}""",
    },
    tests=[[2], [5], [0], [1], [16], [31], [1000], [10000]],
)


# ----------------------------------------------------------------- reverse bits
P_REVBITS = dict(
    id="reverse-bits-32",
    title="Reverse Bits",
    difficulty=1,
    tags=["bits", "shifts"],
    fn="reverse_bits",
    params=[["n", "int"]],
    returns="int",
    espresso=False,
    statement=r"""
`n` is a **32-bit unsigned** integer (given as an ordinary int in the range `0 … 2³² − 1`).
Reverse the order of its 32 bits, so bit 0 becomes bit 31, bit 1 becomes bit 30, and so on,
and return the result as an unsigned value in the same range.

All 32 positions count, including leading zeros: `1` becomes `2³¹`.
""",
    constraints=["0 ≤ n ≤ 2³² − 1"],
    example_notes=[
        "`00000010100101000001111010011100` reversed is `00111001011110000010100101000000` = 964176192.",
        "`11111111111111111111111111111101` reversed is `10111111111111111111111111111111` = 3221225471.",
    ],
    hints=[
        "Build the answer one bit at a time: take the lowest bit of `n`, append it to the right of the result.",
        "Appending bit `b` to `res` is `res = (res << 1) | b`; taking the lowest bit of `n` is `n & 1`, then `n >>= 1`.",
        "Do exactly 32 iterations (not 'while n'), otherwise leading zeros get lost. Keep the result within 32 bits.",
    ],
    explanation=r"""
## Intuition

Reversing bits is reversing a 32-character string, except the "characters" are pulled off
with `& 1` and `>> 1` and pushed on with `<< 1` and `| bit`. It is the same as reversing
the decimal digits of a number with `% 10` and `* 10`, in base 2 and with a **fixed** length.

## Approach

```text
res = 0
repeat 32 times:
    res = (res << 1) | (n & 1)   # push n's lowest bit onto res
    n >>= 1                      # pop it from n
```

Trace on an 8-bit version, `n = 0000 1101`:

| step | n & 1 | res | n after |
|---|---|---|---|
| 1 | 1 | 1 | 0000 0110 |
| 2 | 0 | 10 | 0000 0011 |
| 3 | 1 | 101 | 0000 0001 |
| 4 | 1 | 1011 | 0000 0000 |
| 5–8 | 0 | 1011 0000 | 0 |

The last four iterations matter: they shift the answer into the high half.

## Complexity

* **Time:** O(32) = O(1).
* **Space:** O(1).

## Common mistakes

* **Stopping when `n` hits 0.** Then `1` would reverse to `1`, not `2³¹`.
* **Signed types.** In C, shifting a 1 into bit 31 of an `int` overflows; in Java the
  result would look negative. Use `uint32_t` / `u32`, or 64-bit arithmetic as Python does.
* **Python width.** Python ints are unbounded, so nothing truncates for you. The loop above
  produces at most 32 bits, but if you use `~` or shift left first you must mask with
  `0xFFFFFFFF`.

## Going further

* **Divide and conquer**: swap halves, then quarters, then bytes, nibbles, pairs, bits with masks
  (`(x >> 16) | (x << 16)`, then `((x & 0xFF00FF00) >> 8) | ((x & 0x00FF00FF) << 8)`, …). Five
  steps instead of 32; this is what `u32::reverse_bits` and ARM64's single `rbit`
  instruction give you.
* If the function is called millions of times, a 256-entry byte lookup table reverses 8 bits
  per step.
""",
    solution=r'''def reverse_bits(n):
    res = 0
    # Exactly 32 iterations: every position counts, including leading zeros
    # that will become trailing... and trailing zeros that become leading.
    for _ in range(32):
        res = (res << 1) | (n & 1)   # push n's lowest bit onto the right of res
        n >>= 1                       # discard that bit from n
    # res is built from 32 pushes, so it is always < 2**32: no masking needed.
    return res
''',
    refs={
        "c": r"""long long reverse_bits(long long n) {
    uint32_t x = (uint32_t)n, res = 0;   // unsigned 32-bit: shifts are well defined
    for (int i = 0; i < 32; i++) {
        res = (res << 1) | (x & 1u);   // append lowest bit of x
        x >>= 1;
    }
    return (long long)res;             // zero-extends: stays in 0..2^32-1
}""",
        "cpp": r"""long long reverseBits(long long n) {
    // Divide and conquer: swap 16-bit halves, then bytes, nibbles, pairs, single bits.
    uint32_t x = (uint32_t)n;
    x = (x >> 16) | (x << 16);
    x = ((x & 0xFF00FF00u) >> 8) | ((x & 0x00FF00FFu) << 8);
    x = ((x & 0xF0F0F0F0u) >> 4) | ((x & 0x0F0F0F0Fu) << 4);
    x = ((x & 0xCCCCCCCCu) >> 2) | ((x & 0x33333333u) << 2);
    x = ((x & 0xAAAAAAAAu) >> 1) | ((x & 0x55555555u) << 1);
    return (long long)x;
}""",
        "rust": r"""pub fn reverse_bits(n: i64) -> i64 {
    // Explicit loop on u32; the built-in equivalent is (n as u32).reverse_bits().
    let mut x = n as u32;
    let mut res: u32 = 0;
    for _ in 0..32 {
        res = (res << 1) | (x & 1);
        x >>= 1;
    }
    res as i64   // u32 -> i64 is a zero-extension, never negative
}""",
    },
    tests=[[43261596], [4294967293], [0], [1], [4294967295], [2147483648], [2863311530], [305419896], [65535]]
    + [[_rng(1504).randrange(0, 2**32)] for _ in range(1)],
)


# ----------------------------------------------------------------- power of four
P_POW4 = dict(
    id="power-of-four-bits",
    title="Power of Four",
    difficulty=1,
    tags=["bits", "math"],
    fn="is_power_of_four",
    params=[["n", "int"]],
    returns="bool",
    statement=r"""
Return `true` if `n` is a power of four, i.e. `n = 4ᵏ` for some integer `k ≥ 0`, and
`false` otherwise. Note that `1 = 4⁰` counts, and zero and negative numbers never do.

Bonus: answer in O(1) without loops or recursion.
""",
    constraints=["-2²⁴ < n < 2²⁴ (the 32-bit mask in the reference also works for any int32)"],
    example_notes=["`16 = 4²`.", "`5` is not a power of anything useful here."],
    hints=[
        "First, when is `n` a power of **two**? Look at how many 1 bits it has.",
        "`n > 0 and n & (n - 1) == 0` tests power of two. Powers of four are the powers of two whose single bit sits at an **even** position (0, 2, 4, …).",
        "Mask the even positions with `0x55555555` (binary `0101…0101`), or use the fact that `4ᵏ − 1` is always divisible by 3.",
    ],
    explanation=r"""
## Intuition

Start with the easier question: **power of two** means exactly one set bit.
`n & (n - 1)` clears the lowest set bit, so the result is 0 exactly when there was only one.

```text
 16 = 0001 0000    16 & 15 = 0001 0000 & 0000 1111 = 0   ✔ power of two
 20 = 0001 0100    20 & 19 = 0001 0000              ≠ 0  ✘
```

A power of four `4ᵏ = 2²ᵏ` is a power of two whose single bit is at an even position:

```text
 1 = 0000 0001   bit 0  ✔
 4 = 0000 0100   bit 2  ✔
 8 = 0000 1000   bit 3  ✘ (power of two, not four)
16 = 0001 0000   bit 4  ✔
```

## Approach

1. `n > 0`: zero and negatives are out (and `0 & -1 == 0` would fool step 2).
2. `n & (n - 1) == 0`: exactly one bit.
3. `n & 0x55555555 != 0`: that bit is at an even position. `0x5` is `0101`, so the mask
   has ones exactly at positions 0, 2, 4, …, 30.

Alternative for step 3: `(n - 1) % 3 == 0`, because `4ᵏ − 1 = (4 − 1)(4ᵏ⁻¹ + … + 1)` while
`2·4ᵏ − 1 ≡ 1 (mod 3)`.

Without bitwise operators (ESPresso), loop: while `n` is divisible by 4, divide by 4; the
answer is whether you end at exactly 1. That is O(log n).

## Complexity

* **Time:** O(1) with the mask; O(log₄ n) with the loop.
* **Space:** O(1).

## Common mistakes

* Forgetting `n > 0`: `0 & (0 - 1) == 0` claims zero is a power of two, and
  `-2³¹` is `1000…0` in 32-bit two's complement, a single set bit.
* Using the 32-bit mask on 64-bit values: for inputs above 2³² you need `0x5555555555555555`.
* Floating-point `log(n) / log(4)` checks: rounding makes `log(243)/log(3)` come out as
  `4.999999…`. Avoid floats for exactness questions.
* In C, `n & n - 1` parses as `n & (n - 1)` but `n & (n - 1) == 0` parses as
  `n & ((n - 1) == 0)` since `==` binds tighter than `&`. Always parenthesise.

## Going further

* **Power of three** has no bit trick, but `1162261467 % n == 0` (the largest power of 3
  in an `int32`) works because 3 is prime.
* `n & -n` isolates the lowest set bit; `n == (n & -n)` is another power-of-two test.
""",
    solution=r'''def is_power_of_four(n):
    # 1) Must be positive: 0 and negatives are never 4**k.
    # 2) Exactly one bit set  <=>  n & (n - 1) == 0  (clearing the lowest bit leaves 0).
    # 3) That bit must be at an even position (bit 0, 2, 4, ...): 0x55555555 is
    #    0101...0101 in binary, i.e. ones at exactly the even positions of a 32-bit word.
    return n > 0 and (n & (n - 1)) == 0 and (n & 0x55555555) != 0
''',
    refs={
        "c": r"""bool is_power_of_four(long long n) {
    // Parenthesise: == binds tighter than & in C.
    return n > 0 && (n & (n - 1)) == 0 && (n & 0x5555555555555555LL) != 0;
}""",
        "cpp": r"""bool isPowerOfFour(long long n) {
    // Power of two, and (4^k - 1) is a multiple of 3 while (2*4^k - 1) is not.
    return n > 0 && (n & (n - 1)) == 0 && (n - 1) % 3 == 0;
}""",
        "rust": r"""pub fn is_power_of_four(n: i64) -> bool {
    // Exactly one set bit (count_ones) and it sits at an even position (trailing_zeros).
    n > 0 && n.count_ones() == 1 && n.trailing_zeros() % 2 == 0
}""",
        "espresso": r"""// No bitwise operators in ESPresso: divide by 4 while it divides evenly.
fn isPowerOfFour(n) {
  if n <= 0 { return false }
  var x = n
  while x - (x / 4) * 4 == 0 {   // x mod 4 == 0
    x = x / 4
  }
  return x == 1                   // only 4^k reduces all the way to 1
}""",
    },
    tests=[[16], [5], [1], [0], [-4], [-16], [64], [8], [2], [4194304], [1048576],
           [8388608], [-4194304], [12582912], [16777215], [4], [12]],
)


# ----------------------------------------------------------------- missing number
def _missing_tests():
    r = _rng(1506)
    # Kept modest: ESPresso compiles every test literal into one chunk (<= 256 constants).
    big = list(range(61))
    big.remove(37)
    r.shuffle(big)
    big2 = list(range(50))     # missing the top value 50
    r.shuffle(big2)
    return [[[3, 0, 1]], [[0, 1]], [[9, 6, 4, 2, 3, 5, 7, 0, 1]], [[0]], [[1]], [[1, 2]], [big], [big2]]


P_MISSING = dict(
    id="missing-number-range",
    title="Missing Number",
    difficulty=1,
    tags=["bits", "math", "xor"],
    fn="missing_number",
    params=[["nums", "int[]"]],
    returns="int",
    statement=r"""
`nums` contains `n` **distinct** numbers taken from the range `0, 1, …, n` (that range has
`n + 1` values, so exactly one is missing). Return the missing number.

Use O(1) extra space.
""",
    constraints=["1 ≤ n = len(nums) ≤ 10⁴", "0 ≤ nums[i] ≤ n, all distinct"],
    example_notes=["`n = 3`, the range is `0..3`; `2` is absent.",
                   "`n = 2`, the range is `0..2`; the missing value is the top one, `2`."],
    hints=[
        "You know exactly which numbers *should* be there. What can you compute about the full set cheaply?",
        "The sum `0 + 1 + … + n` is `n(n+1)/2`. Subtract what you actually have.",
        "Or XOR all indices `0..n` with all values: every present number cancels with its index, the missing one survives.",
    ],
    explanation=r"""
## Intuition

Comparing "what should be here" with "what is here" is a one-number subtraction if you
summarise both sides with an operation that can be undone. Two choices:

* **Sum**: `expected = n(n+1)/2`, `missing = expected - sum(nums)`.
* **XOR**: `(0 ^ 1 ^ … ^ n) ^ (nums[0] ^ … ^ nums[n-1])`; every value present on both sides cancels.

## Approach (XOR version)

1. `acc = n` (the index `n` has no slot in the array, so seed with it).
2. For each index `i`, `acc ^= i ^ nums[i]`.
3. Return `acc`.

Trace `nums = [3, 0, 1]`, `n = 3`:

| i | nums[i] | acc |
|---|---|---|
| start | | 3 |
| 0 | 3 | 3 ^ 0 ^ 3 = 0 |
| 1 | 0 | 0 ^ 1 ^ 0 = 1 |
| 2 | 1 | 1 ^ 2 ^ 1 = 2 |

Answer `2`. The sum version: `6 - (3 + 0 + 1) = 2`.

## Complexity

* **Time:** O(n).
* **Space:** O(1).

## Common mistakes

* **Overflow in the sum version.** `n(n+1)/2` overflows a 32-bit int once `n > 65535`.
  Here it fits, and in C/C++/Rust we use 64-bit anyway, but XOR never overflows at all.
  A safe sum variant subtracts as it goes: `acc += i + 1 - nums[i]`.
* Forgetting that `n` itself can be the missing value (example 2).
* Sorting first: O(n log n) and mutates the input.

## Going further

* **Find the duplicate and the missing** (one value repeated, one missing): XOR gives
  `dup ^ miss`; split by its lowest set bit as in *Single Number III*.
* **Cyclic sort**: place each value at its own index by swapping; the first index where
  `nums[i] != i` is missing. O(n), O(1) extra, and generalises to "first missing positive".
""",
    solution=r'''def missing_number(nums):
    n = len(nums)
    # XOR every index 0..n together with every value. A number that is present
    # appears twice (once as an index, once as a value) and cancels to 0.
    # The missing number appears only as an index, so it is what survives.
    acc = n                      # index n has no array slot; seed it up front
    for i, x in enumerate(nums):
        acc ^= i ^ x
    return acc
''',
    refs={
        "c": r"""long long missing_number(long long* nums, int numsSize) {
    // Sum version in 64-bit: n(n+1)/2 cannot overflow for these sizes.
    long long n = numsSize, expected = n * (n + 1) / 2, actual = 0;
    for (int i = 0; i < numsSize; i++) actual += nums[i];
    return expected - actual;
}""",
        "cpp": r"""long long missingNumber(vector<long long>& nums) {
    long long acc = (long long)nums.size();   // seed with index n
    for (size_t i = 0; i < nums.size(); i++) acc ^= (long long)i ^ nums[i];
    return acc;
}""",
        "rust": r"""pub fn missing_number(nums: Vec<i64>) -> i64 {
    // XOR indices 0..n with values; pairs cancel.
    let n = nums.len() as i64;
    nums.iter().enumerate().fold(n, |acc, (i, &x)| acc ^ i as i64 ^ x)
}""",
        "espresso": r"""// ESPresso lacks XOR, so use the running-difference form of the sum trick:
// sum over i of ((i + 1) - nums[i]) = n(n+1)/2 - sum(nums) without a big intermediate.
fn missingNumber(nums) {
  var acc = 0
  for var i in 0..len(nums) {
    acc += (i + 1) - nums[i]
  }
  return acc
}""",
    },
    tests=_missing_tests(),
)


# ----------------------------------------------------------------- sum without +
def _sum_tests():
    r = _rng(1507)
    t = [[1, 2], [2, 3], [-1, 1], [-2, -3], [2147483647, 1], [-2147483648, -1], [0, 0], [-5, 12],
         [2147483647, 2147483647], [-2147483648, -2147483648], [123, -123]]
    for _ in range(3):
        t.append([r.randint(-2**31, 2**31 - 1), r.randint(-2**31, 2**31 - 1)])
    return t


P_SUM = dict(
    id="sum-without-plus-32bit",
    title="Sum of Two Integers Without +",
    difficulty=2,
    tags=["bits", "two's complement"],
    fn="get_sum",
    params=[["a", "int"], ["b", "int"]],
    returns="int",
    espresso=False,
    statement=r"""
Add two **32-bit signed** integers `a` and `b` **without using the `+` or `-` operators**
on them (you may still use `+=` on a loop counter if you really need one).

The result follows 32-bit two's complement semantics: if the true sum does not fit in
`[-2³¹, 2³¹ − 1]` it **wraps around**, exactly as hardware addition of `int32` would.
For example `2147483647 + 1` returns `-2147483648`.
""",
    constraints=["-2³¹ ≤ a, b ≤ 2³¹ − 1"],
    example_notes=["`1 + 2 = 3`: no carries collide.", "`2 + 3 = 5`: `10 + 11` produces one carry."],
    hints=[
        "Add in binary by hand. What is the sum bit when you ignore carries? Which positions produce a carry?",
        "Sum without carry = `a ^ b`. Carry = `(a & b) << 1`. Now you need to add those two numbers… repeat until the carry is 0.",
        "In Python, ints never overflow and negative numbers have infinite leading 1s, so the loop may never end. Keep everything masked to 32 bits with `& 0xFFFFFFFF`, then convert back to signed at the end.",
    ],
    explanation=r"""
## Intuition

A hardware adder is built from XOR and AND gates. For one bit column:

| a | b | sum bit (a ^ b) | carry (a & b) |
|---|---|---|---|
| 0 | 0 | 0 | 0 |
| 0 | 1 | 1 | 0 |
| 1 | 0 | 1 | 0 |
| 1 | 1 | 0 | 1 |

So `a + b = (a ^ b) + ((a & b) << 1)`: the partial sum plus the carries moved one column
left. That is another addition, but the carry has at least one more trailing zero each
round, so after at most 32 rounds it vanishes.

## Approach

```text
mask = 0xFFFFFFFF
a, b = a & mask, b & mask          # view both as 32-bit patterns
while b != 0:
    a, b = (a ^ b) & mask, ((a & b) << 1) & mask
# a is the 32-bit pattern of the sum; reinterpret as signed:
return a if a < 2**31 else a - 2**32
```

Trace for `2 + 3`:

| round | a | b (carry) |
|---|---|---|
| start | 010 | 011 |
| 1 | 001 | 100 |
| 2 | 101 | 000 |

Result `101₂ = 5`. For `-1 + 1`, the pattern `0xFFFFFFFF` plus `1` carries all the way
to bit 32, where the mask drops it: the answer is `0`, as two's complement promises.

### Why masking is essential in Python

Python ints are unbounded. `-1 & 1` is `1`, shifted carry is `2`, then `4`, `8`, … and
`-1 ^ …` keeps an infinite run of leading ones, so without a mask the loop never ends.
Masking with `0xFFFFFFFF` simulates a 32-bit register; the final `- 2**32` reinterprets
bit 31 as the sign bit (its weight is `-2³¹`, not `+2³¹`).

The final conversion uses `-`. That is fine: the restriction is on *adding a and b*; the
reinterpretation is a fixed type conversion (in C it is just a cast).

## Complexity

* **Time:** O(32) iterations at most, O(1).
* **Space:** O(1).

## Common mistakes

* **Infinite loop with negatives in Python** (no mask).
* **Forgetting the signed conversion**: returning `4294967295` instead of `-1`.
* **Signed overflow in C/C++**: `(a & b) << 1` on a signed int whose bit 30 is set is
  undefined behaviour, and `-fsanitize=undefined` will catch it. Do the work in `uint32_t`.
* **Rust debug panics**: `<<` on `i32` is fine, but use `u32` for the loop and `as i32` at the end.

## Going further

* **Subtraction**: `a - b = a + (~b + 1)`, i.e. add the two's complement negation.
* **Multiplication** by shift-and-add: for each set bit `k` of `b`, add `a << k`.
* The carry-propagation loop is a *ripple-carry adder*; real CPUs use *carry-lookahead*
  to compute all carries in O(log w) gate depth.
""",
    solution=r'''def get_sum(a, b):
    MASK = 0xFFFFFFFF            # keep exactly 32 bits, like a hardware register
    SIGN = 0x80000000            # bit 31: the sign bit of an int32

    # Python ints are unbounded, so map both inputs to their 32-bit patterns first.
    a &= MASK
    b &= MASK
    while b:
        # a ^ b      : column-wise sum ignoring carries
        # (a & b)<<1 : the carries, moved one column left
        # Masking drops anything that carries out of bit 31 (wrap-around).
        a, b = (a ^ b) & MASK, ((a & b) << 1) & MASK

    # a is now the unsigned 32-bit pattern of the sum. Bit 31 has weight -2**31 in
    # two's complement, so if it is set, reinterpret: pattern - 2**32.
    return a if a < SIGN else a - (1 << 32)
''',
    refs={
        "c": r"""long long get_sum(long long a, long long b) {
    // Unsigned 32-bit arithmetic wraps by definition: no undefined behaviour.
    uint32_t x = (uint32_t)a, y = (uint32_t)b;
    while (y) {
        uint32_t carry = (x & y) << 1;   // carries, shifted to the next column
        x ^= y;                          // sum without carries
        y = carry;
    }
    return (int32_t)x;   // reinterpret the bit pattern as signed, widen to long long
}""",
        "cpp": r"""long long getSum(long long a, long long b) {
    uint32_t x = static_cast<uint32_t>(a), y = static_cast<uint32_t>(b);
    while (y != 0) {
        uint32_t carry = (x & y) << 1;
        x ^= y;
        y = carry;
    }
    // Since C++20, unsigned -> signed conversion is defined as modular (two's complement).
    return static_cast<int32_t>(x);
}""",
        "rust": r"""pub fn get_sum(a: i64, b: i64) -> i64 {
    // u32 shifts discard bits that leave the word; no overflow panic possible.
    let (mut x, mut y) = (a as u32, b as u32);
    while y != 0 {
        let carry = (x & y) << 1;
        x ^= y;
        y = carry;
    }
    x as i32 as i64   // reinterpret as signed 32-bit, then sign-extend
}""",
    },
    tests=_sum_tests(),
)


# ----------------------------------------------------------------- sieve
P_SIEVE = dict(
    id="count-primes-sieve",
    title="Count Primes (Sieve of Eratosthenes)",
    difficulty=2,
    tags=["math", "primes", "sieve"],
    fn="count_primes",
    params=[["n", "int"]],
    returns="int",
    espresso=False,
    statement=r"""
Return the number of prime numbers **strictly less than** `n`.

A prime is an integer greater than 1 whose only positive divisors are 1 and itself.
The largest tests make trial division too slow, so think about sieving.
""",
    constraints=["0 ≤ n ≤ 5·10⁶"],
    example_notes=["The primes below 10 are 2, 3, 5, 7.", "There are no primes below 0."],
    hints=[
        "Testing each number by trial division up to √k costs about n√n operations. Instead of asking 'is k prime?', ask 'which numbers does each prime rule out?'.",
        "Keep a boolean array `is_prime[0..n-1]`. For each prime `p`, mark `2p, 3p, …` as composite.",
        "Start crossing out at `p·p` (smaller multiples were already crossed out by smaller primes), and stop the outer loop once `p·p ≥ n`.",
    ],
    explanation=r"""
## Intuition

Primality tests one number at a time repeat a lot of work. The sieve turns the question
around: every composite number has a prime factor ≤ its square root, so if each prime
"crosses out" its multiples, whatever survives is prime. Crossing out is a simple stride
through an array, which is extremely cache friendly.

## Approach

1. If `n < 3`, return 0 (no primes below 2).
2. `is_prime = [True] * n`, then `is_prime[0] = is_prime[1] = False`.
3. For `p = 2, 3, …` while `p * p < n`: if `is_prime[p]`, mark `p*p, p*p + p, …` as `False`.
4. Count the `True` entries.

Trace for `n = 30` (only primes p with p² < 30 do work: 2, 3, 5):

```text
p=2: cross 4 6 8 10 12 14 16 18 20 22 24 26 28
p=3: cross 9 (12) 15 (18) 21 (24) 27         (already-crossed in parentheses)
p=5: cross 25
left: 2 3 5 7 11 13 17 19 23 29   → 10 primes
```

Why start at `p²`? Any `k·p` with `k < p` has a prime factor smaller than `p`, so an
earlier pass already crossed it out.

## Complexity

* **Time:** O(n log log n). Prime `p` crosses out about `n/p` numbers, and
  `Σ_{p ≤ n} 1/p ≈ ln ln n`, which is about 3 for `n = 5·10⁶`. Effectively linear.
* **Space:** O(n) bytes (use a byte or bit array, not 8-byte integers).

## Common mistakes

* "Less than n" vs "at most n": `count_primes(7)` is 3 (2, 3, 5), not 4.
* Not handling `n = 0, 1, 2` before indexing `is_prime[1]`.
* Overflow of `p * p` in 32-bit for large `n` (use 64-bit or `p <= n / p`).
* In Python, a nested `for` loop that sets one element at a time is ~50× slower than the
  slice assignment `is_prime[p*p::p] = bytes(len(range(p*p, n, p)))`.

## Going further

* **Odd-only sieve** halves memory and time; a **segmented sieve** handles ranges like
  `[10¹², 10¹² + 10⁶]` with O(√hi) memory.
* The **linear sieve** (Euler's sieve) visits each composite exactly once and also records
  each number's smallest prime factor, giving O(log n) factorisation afterwards.
""",
    solution=r'''def count_primes(n):
    if n < 3:
        return 0                     # no primes below 2 (and below 3 there is just none < 2)
    # bytearray: one byte per number, fast slice assignment, 1 = "still possibly prime".
    is_prime = bytearray([1]) * n
    is_prime[0] = is_prime[1] = 0    # 0 and 1 are not prime by definition
    p = 2
    while p * p < n:                 # a composite < n has a prime factor < sqrt(n)
        if is_prime[p]:
            # Multiples below p*p were crossed out by smaller primes already.
            # Slice assignment crosses out p*p, p*p+p, ... in one C-speed operation.
            start = p * p
            is_prime[start::p] = bytes(len(range(start, n, p)))
        p += 1
    return sum(is_prime)             # every surviving 1 is a prime
''',
    refs={
        "c": r"""long long count_primes(long long n) {
    if (n < 3) return 0;
    char* composite = calloc((size_t)n, 1);   // zero-initialised: nothing crossed out yet
    for (long long p = 2; p * p < n; p++)
        if (!composite[p])
            for (long long m = p * p; m < n; m += p) composite[m] = 1;
    long long count = 0;
    for (long long k = 2; k < n; k++) count += !composite[k];
    free(composite);
    return count;
}""",
        "cpp": r"""long long countPrimes(long long n) {
    if (n < 3) return 0;
    // Odd-only sieve: index i stands for the odd number 2i+1. Halves memory and work.
    long long half = n / 2;                // odd numbers below n: 1, 3, ..., (count = n/2)
    vector<char> composite(half, 0);
    for (long long i = 1; ; i++) {
        long long p = 2 * i + 1;
        if (p * p >= n) break;
        if (composite[i]) continue;
        // p*p is odd; step 2p keeps us on odd numbers, i.e. index step p.
        for (long long m = p * p / 2; m < half; m += p) composite[m] = 1;
    }
    long long count = 1;                   // the prime 2
    for (long long i = 1; i < half; i++) count += !composite[i];   // skip index 0 (=1)
    return count;
}""",
        "rust": r"""pub fn count_primes(n: i64) -> i64 {
    if n < 3 {
        return 0;
    }
    let n = n as usize;
    let mut is_prime = vec![true; n];
    is_prime[0] = false;
    is_prime[1] = false;
    let mut p = 2;
    while p * p < n {
        if is_prime[p] {
            // step_by gives the stride p*p, p*p+p, ...
            for m in (p * p..n).step_by(p) {
                is_prime[m] = false;
            }
        }
        p += 1;
    }
    is_prime.iter().filter(|&&b| b).count() as i64
}""",
    },
    tests=[[10], [0], [1], [2], [3], [100], [30], [999983], [1000000], [5000000]],
)


# ----------------------------------------------------------------- mod pow
def _modpow_tests():
    r = _rng(1509)
    t = [[2, 10, 1000], [3, 0, 7], [0, 0, 5], [5, 3, 1], [0, 5, 13], [2, 10**15, 10**9 + 7],
         [10**15, 10**15 - 1, 2147483647], [7, 1, 2], [123456789, 987654321, 1000000007],
         [2, 62, 2147483647], [4, 13, 497]]
    for _ in range(3):
        t.append([r.randrange(0, 10**15), r.randrange(0, 10**15), r.randrange(1, 2**31)])
    return t


P_MODPOW = dict(
    id="modular-exponentiation",
    title="Modular Exponentiation",
    difficulty=2,
    tags=["math", "modular arithmetic", "divide and conquer"],
    fn="mod_pow",
    params=[["base", "int"], ["exponent", "int"], ["modulus", "int"]],
    returns="int",
    espresso=False,
    statement=r"""
Compute `base^exponent mod modulus`. The result must lie in `[0, modulus − 1]`.

Exponents go up to 10¹⁵, so multiplying `exponent` times is far too slow, and the true
power has quadrillions of digits. By convention `0⁰ = 1`, so `mod_pow(0, 0, m) = 1 mod m`.

(In Python, the built-in `pow(b, e, m)` does this. Implement it yourself.)
""",
    constraints=["0 ≤ base ≤ 10¹⁵", "0 ≤ exponent ≤ 10¹⁵", "1 ≤ modulus ≤ 2³¹ − 1"],
    example_notes=["`2¹⁰ = 1024`, and `1024 mod 1000 = 24`.", "Anything to the power 0 is 1."],
    hints=[
        "`b^e = (b^(e/2))²` when `e` is even. How many halvings until `e` reaches 0?",
        "Look at the binary digits of `e`: `b^13 = b^8 · b^4 · b^1`. Keep squaring `b` and multiply it in when the current bit is 1.",
        "Reduce mod `m` after every multiplication. With `m < 2³¹`, a product of two reduced values is `< 2⁶²` and fits in a 64-bit integer. Reduce `base` first, it can be bigger than `m`! And `m = 1` must give 0.",
    ],
    explanation=r"""
## Intuition

Write the exponent in binary. `13 = 1101₂ = 8 + 4 + 1`, so `b¹³ = b⁸ · b⁴ · b¹`. The
powers `b¹, b², b⁴, b⁸, …` come from repeated squaring, one squaring per bit. So we need
about `2 log₂ e` multiplications, roughly 100 for `e = 10¹⁵`, instead of 10¹⁵.

Taking `mod m` after every multiplication keeps numbers small, because
`(x · y) mod m = ((x mod m)(y mod m)) mod m`.

## Approach (right-to-left binary exponentiation)

```text
result = 1 % m          # handles m == 1
b = base % m
while e > 0:
    if e & 1: result = result * b % m
    b = b * b % m
    e >>= 1
```

Trace `2^10 mod 1000` (`10 = 1010₂`):

| e (binary) | bit | result | b after squaring |
|---|---|---|---|
| 1010 | 0 | 1 | 4 |
| 101 | 1 | 4 | 16 |
| 10 | 0 | 4 | 256 |
| 1 | 1 | 4·256 = 1024 → 24 | 65536 → 536 |

## Complexity

* **Time:** O(log e) multiplications.
* **Space:** O(1) iterative (the recursive version `pow(b, e) = pow(b, e/2)²·…` uses O(log e) stack).

## Common mistakes

* **Not reducing `base` first.** `base` can be 10¹⁵; `base * base` overflows 64 bits.
* **`m = 1`.** Starting with `result = 1` returns 1 when `e = 0`, but everything mod 1 is 0.
  Start with `1 % m`.
* **Overflow.** The product of two values `< m` is `< m²`. With `m < 2³¹` that is `< 2⁶²`,
  fine in `long long`/`i64`. For `m` near 2⁶³ you would need 128-bit (`__int128`, `u128`)
  intermediates or "mulmod" via doubling.
* Shifting a signed negative exponent: not an issue here (`e ≥ 0`), but in general define what `b^(-e)` means first (a modular inverse).

## Going further

* **Modular inverse** for prime `m`: `a⁻¹ ≡ a^(m−2) (mod m)` (Fermat). This is how
  "n choose k mod 10⁹+7" divides by `k!`.
* The same squaring trick works for anything associative: matrices (next problems:
  Fibonacci in O(log n)), permutations, or composing functions.
* **Miller–Rabin** primality testing is built on modular exponentiation.
""",
    solution=r'''def mod_pow(base, exponent, modulus):
    # result starts at 1 mod m (so m == 1 correctly yields 0 even when exponent == 0).
    result = 1 % modulus
    # Reduce the base first: it may be far larger than the modulus.
    b = base % modulus
    e = exponent
    while e > 0:
        # Invariant: answer == result * b**e  (mod m)
        if e & 1:                    # current lowest bit of e is set:
            result = result * b % modulus   # ...so this power of b is part of the product
        b = b * b % modulus          # b, b^2, b^4, b^8, ... one squaring per bit
        e >>= 1                      # move to the next bit of the exponent
    return result
''',
    refs={
        "c": r"""long long mod_pow(long long base, long long exponent, long long modulus) {
    // modulus < 2^31, so every product below is < 2^62: no signed overflow.
    long long result = 1 % modulus, b = base % modulus, e = exponent;
    while (e > 0) {
        if (e & 1) result = result * b % modulus;
        b = b * b % modulus;
        e >>= 1;
    }
    return result;
}""",
        "cpp": r"""// Recursive divide and conquer: b^e = (b^(e/2))^2 * (b if e is odd).
long long modPowRec(long long b, long long e, long long m) {
    if (e == 0) return 1 % m;
    long long half = modPowRec(b, e / 2, m);
    long long sq = half * half % m;
    return (e & 1) ? sq * b % m : sq;
}
long long modPow(long long base, long long exponent, long long modulus) {
    return modPowRec(base % modulus, exponent, modulus);   // depth ~ 50 for e ~ 10^15
}""",
        "rust": r"""pub fn mod_pow(base: i64, exponent: i64, modulus: i64) -> i64 {
    // u64 throughout; products of two values < 2^31 fit easily.
    let m = modulus as u64;
    let (mut result, mut b, mut e) = (1 % m, base as u64 % m, exponent as u64);
    while e > 0 {
        if e & 1 == 1 {
            result = result * b % m;
        }
        b = b * b % m;
        e >>= 1;
    }
    result as i64
}""",
    },
    tests=_modpow_tests(),
)


# ----------------------------------------------------------------- pascal row
P_PASCAL = dict(
    id="pascal-triangle-row",
    title="Pascal's Triangle Row",
    difficulty=1,
    tags=["math", "combinatorics", "dynamic programming"],
    fn="pascal_row",
    params=[["row_index", "int"]],
    returns="int[]",
    statement=r"""
Return row `row_index` (0-indexed) of Pascal's triangle: the list
`C(k, 0), C(k, 1), …, C(k, k)` for `k = row_index`.

```text
row 0:        1
row 1:       1 1
row 2:      1 2 1
row 3:     1 3 3 1
row 4:    1 4 6 4 1
```

Use only O(k) extra space.
""",
    constraints=["0 ≤ row_index ≤ 50"],
    example_notes=["Row 3 is `1 3 3 1`.", "Row 0 is just `1`."],
    hints=[
        "Each entry is the sum of the two entries above it: `row[j] = prev[j-1] + prev[j]`.",
        "You can update a single array in place if you sweep `j` from right to left, so `row[j-1]` is still the old value when you read it.",
        "Alternatively, use the closed form `C(k, j) = C(k, j-1) · (k − j + 1) / j`; multiply before dividing so it stays exact.",
    ],
    explanation=r"""
## Intuition

Pascal's rule `C(n, k) = C(n−1, k−1) + C(n−1, k)` says every row is computed from the row
above. We only ever need the previous row, so one array of length `k + 1` suffices, if we
are careful about the order of updates.

## Approach (in place, right to left)

1. `row = [1] * (k + 1)`.
2. For `i` from 2 to `k` (rows that have interior entries):
   for `j` from `i − 1` down to 1: `row[j] += row[j − 1]`.

Why right to left? `row[j]` needs the **old** `row[j−1]`. Sweeping leftwards, we overwrite
`row[j]` before touching `row[j−1]`.

Trace up to row 4 (only the meaningful prefix is shown):

| after row | row |
|---|---|
| 1 | 1 1 |
| 2 | 1 2 1 |
| 3 | 1 3 3 1 |
| 4 | 1 4 6 4 1 |

Sweeping left to right instead would compute `1 2 3 4 …` (each new value feeding the next).

**Multiplicative formula** (O(k) time): `C(k, j) = C(k, j−1) · (k − j + 1) / j`. The
product `C(k, j−1) · (k − j + 1)` is always divisible by `j`, so the division is exact as
long as you multiply first.

## Complexity

* **Time:** O(k²) for the additive version, O(k) for the multiplicative one.
* **Space:** O(k) for the output row.

## Common mistakes

* Sweeping left to right in place (reads already-updated values).
* **Overflow.** `C(50, 25) ≈ 1.26·10¹⁴` fits in 64 bits, but the multiplicative formula's
  intermediate `C(k, j−1) · (k − j + 1)` is up to ~50× larger: still fine at k = 50,
  but for k ≈ 62 it overflows `i64` while the additive version (whose values never exceed
  the answer) does not.
* Dividing first: `C(k, j−1) / j * (k−j+1)` truncates.

## Going further

* Row `k` summed is `2ᵏ`; the alternating sum is 0.
* `C(n, k) mod p` for big `n`: precompute factorials and inverse factorials (with modular
  exponentiation for the inverse), or use Lucas's theorem when `p` is small.
""",
    solution=r'''def pascal_row(row_index):
    k = row_index
    row = [1] * (k + 1)              # the two edges of every row are 1
    for i in range(2, k + 1):        # rows 0 and 1 have no interior entries
        # Sweep right-to-left so row[j - 1] still holds the PREVIOUS row's value
        # when we read it: new row[j] = old row[j - 1] + old row[j].
        for j in range(i - 1, 0, -1):
            row[j] += row[j - 1]
    return row
''',
    refs={
        "c": r"""long long* pascal_row(long long row_index, int* returnSize) {
    int k = (int)row_index;
    long long* row = malloc(sizeof(long long) * (k + 1));
    row[0] = 1;
    // Multiplicative formula: C(k, j) = C(k, j-1) * (k - j + 1) / j. Multiply first: exact.
    for (int j = 1; j <= k; j++) row[j] = row[j - 1] * (k - j + 1) / j;
    *returnSize = k + 1;
    return row;
}""",
        "cpp": r"""vector<long long> pascalRow(long long rowIndex) {
    vector<long long> row(rowIndex + 1, 1);
    for (long long i = 2; i <= rowIndex; i++)
        for (long long j = i - 1; j >= 1; j--)   // right to left: read old row[j-1]
            row[j] += row[j - 1];
    return row;
}""",
        "rust": r"""pub fn pascal_row(row_index: i64) -> Vec<i64> {
    let k = row_index as usize;
    let mut row = vec![1i64; k + 1];
    for i in 2..=k {
        for j in (1..i).rev() {      // right to left
            row[j] += row[j - 1];
        }
    }
    row
}""",
    },
    tests=[[3], [0], [1], [2], [4], [10], [33], [50]],
)


# ----------------------------------------------------------------- excel
def _excel_title(n):
    s = []
    while n:
        n -= 1
        s.append(chr(65 + n % 26))
        n //= 26
    return "".join(reversed(s))


def _excel_tests():
    r = _rng(1511)
    mixed = []
    for _ in range(20):
        n = r.randint(1, 2**31 - 1) if r.random() < 0.5 else r.randint(1, 20000)
        mixed.append(str(n) if r.random() < 0.5 else _excel_title(n))
    return [
        [["A", "AB", "ZY"]],
        [["1", "28", "701"]],
        [["Z", "26", "AZ", "52", "BA", "53"]],
        [["ZZ", "702", "AAA", "703"]],
        [["FXSHRXW", "2147483647"]],
        [["YZ", "675", "ZA", "677", "XFD", "16384"]],
        [["A"]],
        [mixed],
    ]


P_EXCEL = dict(
    id="excel-columns-both-ways",
    title="Excel Columns Both Ways",
    difficulty=2,
    tags=["math", "base conversion", "string"],
    fn="convert_excel",
    params=[["queries", "str[]"]],
    returns="str[]",
    statement=r"""
Spreadsheet columns are labelled `A, B, …, Z, AA, AB, …, AZ, BA, …, ZZ, AAA, …`, so
`A = 1`, `Z = 26`, `AA = 27`, `ZZ = 702`, `AAA = 703`.

Each query is either a **column title** (only uppercase letters) or a **column number**
written in decimal (only digits). Convert each query to the other form and return the
results in order: titles become their number (as a decimal string), numbers become their title.
""",
    constraints=["1 ≤ len(queries) ≤ 100",
                 "every number is in `1 … 2³¹ − 1`; every title denotes a number in that range"],
    example_notes=["`AB = 1·26 + 2 = 28`, `ZY = 26·26 + 25 = 701`.",
                   "The reverse direction of example 1."],
    hints=[
        "Title → number is like reading a base-26 numeral: `value = value * 26 + digit`. What are the digit values?",
        "The digits are `A = 1 … Z = 26`; there is **no zero digit**. That is a *bijective* base-26 system.",
        "For number → title, subtract 1 before taking `% 26`: `n -= 1; letter = 'A' + n % 26; n //= 26`. Without the `-1`, multiples of 26 come out wrong (`26` must be `Z`, not `A@`).",
    ],
    explanation=r"""
## Intuition

Column titles look like base 26, and reading them is exactly base 26 with digits 1..26:

```text
"ZY" = 26·26¹ + 25·26⁰ = 676 + 25 = 701
```

Writing them is where people trip: ordinary base 26 has digits 0..25 and the number 26 is
written "10". Here there is **no zero**; 26 is a single digit `Z`. This is *bijective
numeration*: every positive integer has exactly one representation and the empty string
is 0. The fix is to shift each digit down by one before extracting it.

## Approach

**Title → number** (Horner's rule):

```text
value = 0
for ch in title: value = value * 26 + (ord(ch) - ord('A') + 1)
```

**Number → title**:

```text
while n > 0:
    n -= 1                      # map digits 1..26 onto 0..25
    letters.append('A' + n % 26)
    n //= 26
reverse(letters)
```

Trace `n = 52`:

| n before | n − 1 | (n−1) % 26 | letter | (n−1) // 26 |
|---|---|---|---|---|
| 52 | 51 | 25 | Z | 1 |
| 1 | 0 | 0 | A | 0 |

Reversed: `AZ`. Check: `A·26 + Z = 26 + 26 = 52`. ✔

Why does `n − 1` work? If `n = d₀ + 26·m` with `d₀ ∈ 1..26`, then `n − 1 = (d₀ − 1) + 26·m`
with `d₀ − 1 ∈ 0..25`, so `%` and `//` recover `d₀ − 1` and `m` exactly.

Dispatch each query on its first character: a digit means "number".

## Complexity

* **Time:** O(L) per query, where L ≤ 7 letters or 10 digits.
* **Space:** O(L) per result.

## Common mistakes

* Plain base-26 for number → title: `26 → "A@"` or `"BA"`-style off-by-one errors near multiples of 26.
* Building the title and forgetting to reverse it (digits come out least significant first).
* Overflow while parsing titles in 32-bit code: `FXSHRXW` is exactly `2³¹ − 1`; one letter more overflows `int`.
* In C, returning a pointer to a local buffer instead of `malloc`'d memory.

## Going further

* Any base `b ≥ 2` works with the same `n −= 1` trick for bijective numerals.
* A spreadsheet cell like `XFD1048576` mixes both systems: the letters are bijective base 26,
  the row is ordinary decimal.
""",
    solution=r'''def convert_excel(queries):
    def title_to_number(title):
        value = 0
        for ch in title:
            # Horner's rule; digits are A=1 .. Z=26 (no zero digit).
            value = value * 26 + (ord(ch) - ord("A") + 1)
        return value

    def number_to_title(n):
        letters = []
        while n > 0:
            n -= 1                   # shift digit range 1..26 down to 0..25
            letters.append(chr(ord("A") + n % 26))
            n //= 26                 # remove that digit
        return "".join(reversed(letters))   # we produced least-significant first

    out = []
    for q in queries:
        if q[0].isdigit():           # a decimal column number -> title
            out.append(number_to_title(int(q)))
        else:                        # letters -> decimal string
            out.append(str(title_to_number(q)))
    return out
''',
    refs={
        "cpp": r"""vector<string> convertExcel(vector<string>& queries) {
    vector<string> out;
    for (const string& q : queries) {
        if (isdigit((unsigned char)q[0])) {
            long long n = stoll(q);
            string s;
            while (n > 0) {
                n--;                         // bijective: digits 1..26 -> 0..25
                s += char('A' + n % 26);
                n /= 26;
            }
            reverse(s.begin(), s.end());
            out.push_back(s);
        } else {
            long long v = 0;
            for (char c : q) v = v * 26 + (c - 'A' + 1);
            out.push_back(to_string(v));
        }
    }
    return out;
}""",
        "rust": r"""pub fn convert_excel(queries: Vec<String>) -> Vec<String> {
    queries
        .iter()
        .map(|q| {
            if q.as_bytes()[0].is_ascii_digit() {
                let mut n: u64 = q.parse().unwrap();
                let mut bytes = Vec::new();
                while n > 0 {
                    n -= 1;                          // shift to 0..25
                    bytes.push(b'A' + (n % 26) as u8);
                    n /= 26;
                }
                bytes.reverse();
                String::from_utf8(bytes).unwrap()
            } else {
                q.bytes()
                    .fold(0u64, |v, c| v * 26 + (c - b'A' + 1) as u64)
                    .to_string()
            }
        })
        .collect()
}""",
    },
    tests=_excel_tests(),
)


# ----------------------------------------------------------------- fib matrix
P_FIB = dict(
    id="fibonacci-matrix-power",
    title="Fibonacci via Matrix Power",
    difficulty=3,
    tags=["math", "matrix exponentiation", "modular arithmetic"],
    fn="fib_mod",
    params=[["n", "int"]],
    returns="int",
    espresso=False,
    statement=r"""
The Fibonacci numbers are `F(0) = 0`, `F(1) = 1`, `F(k) = F(k−1) + F(k−2)`.

Return `F(n) mod 1 000 000 007` for `n` as large as 10¹⁵. A loop of `n` steps would take
days; you need O(log n).
""",
    constraints=["0 ≤ n ≤ 10¹⁵"],
    example_notes=["`F(0) = 0`.", "`F(10) = 55`."],
    hints=[
        "The step `(F(k+1), F(k)) → (F(k+2), F(k+1))` is linear. Write it as a 2×2 matrix times a vector.",
        "`[[1,1],[1,0]]ⁿ = [[F(n+1), F(n)], [F(n), F(n−1)]]`. So you only need a matrix power.",
        "Raise the matrix to the n-th power by repeated squaring, exactly like modular exponentiation of numbers, reducing every entry mod 10⁹+7.",
    ],
    explanation=r"""
## Intuition

A linear recurrence is a matrix multiplication in disguise:

```text
| F(k+2) |   | 1 1 |   | F(k+1) |
| F(k+1) | = | 1 0 | · | F(k)   |
```

Applying the step `n` times is multiplying by `Q = [[1,1],[1,0]]` `n` times, i.e. by `Qⁿ`.
Matrix multiplication is associative, so the fast exponentiation from *Modular
Exponentiation* applies unchanged: O(log n) matrix products. In fact

```text
Qⁿ = | F(n+1)  F(n)   |
     | F(n)    F(n−1) |
```

so `F(n)` is the top-right entry.

## Approach

1. `R = I` (identity), `B = Q`, `e = n`.
2. While `e > 0`: if `e` is odd, `R = R·B`; `B = B·B`; `e >>= 1`. Reduce every entry mod `M`.
3. Return `R[0][1]`.

Trace for `n = 5` (`101₂`):

| e | bit | R | B after squaring |
|---|---|---|---|
| 101 | 1 | Q¹ = [[1,1],[1,0]] | Q² = [[2,1],[1,1]] |
| 10 | 0 | Q¹ | Q⁴ = [[5,3],[3,2]] |
| 1 | 1 | Q⁵ = [[8,5],[5,3]] | … |

`F(5) = 5`. ✔

A 2×2 product modulo `M`:

```python
def mul(A, B):
    return [[(A[0][0]*B[0][0] + A[0][1]*B[1][0]) % M, (A[0][0]*B[0][1] + A[0][1]*B[1][1]) % M],
            [(A[1][0]*B[0][0] + A[1][1]*B[1][0]) % M, (A[1][0]*B[0][1] + A[1][1]*B[1][1]) % M]]
```

## Complexity

* **Time:** O(log n) matrix products, each 8 multiplications: about 400 multiplications for n = 10¹⁵.
* **Space:** O(1).

## Common mistakes

* **Overflow in C/C++/Rust.** Entries are `< M ≈ 10⁹`, so each product is `< 10¹⁸` and the
  sum of two products is `< 2·10¹⁸ < 9.2·10¹⁸`. Safe in signed 64-bit, but only if you
  reduce after every product-sum. Three terms would also fit; a 3×3 matrix with
  `M ≈ 4·10⁹` would not.
* **Off by one.** `Qⁿ` holds `F(n)` at `[0][1]`, `F(n+1)` at `[0][0]`. Check `n = 0`
  (identity → `F(0) = 0`) and `n = 1`.
* Using floating-point Binet's formula `φⁿ/√5`: exact only up to about `n = 70` in doubles.

## Going further

* **Fast doubling** avoids matrices: `F(2k) = F(k)·(2F(k+1) − F(k))`,
  `F(2k+1) = F(k)² + F(k+1)²`. Same O(log n), fewer multiplications.
* Any linear recurrence of order `d` (tribonacci, counting tilings, paths of length n in a
  graph) becomes a `d×d` matrix power in O(d³ log n).
* Fibonacci mod `M` is periodic (the Pisano period); for `M = 10` it is 60.
""",
    solution=r'''def fib_mod(n):
    M = 1_000_000_007

    def mul(A, B):
        # 2x2 matrix product, every entry reduced mod M so numbers stay < M.
        return [
            [(A[0][0] * B[0][0] + A[0][1] * B[1][0]) % M,
             (A[0][0] * B[0][1] + A[0][1] * B[1][1]) % M],
            [(A[1][0] * B[0][0] + A[1][1] * B[1][0]) % M,
             (A[1][0] * B[0][1] + A[1][1] * B[1][1]) % M],
        ]

    # Q^n = [[F(n+1), F(n)], [F(n), F(n-1)]], so F(n) is the top-right entry.
    result = [[1, 0], [0, 1]]        # identity = Q^0
    base = [[1, 1], [1, 0]]          # Q = one Fibonacci step
    e = n
    while e > 0:                     # binary exponentiation, as with numbers
        if e & 1:
            result = mul(result, base)
        base = mul(base, base)       # Q, Q^2, Q^4, Q^8, ...
        e >>= 1
    return result[0][1]
''',
    refs={
        "c": r"""#define FIB_MOD 1000000007LL
// 2x2 matrices as long long[4] in row-major order: {a, b, c, d} = [[a, b], [c, d]].
static void mat_mul(long long* r, const long long* x, const long long* y) {
    // Each entry: two products < 1e18 summed < 2e18, fits in signed 64-bit.
    long long t[4] = {
        (x[0] * y[0] + x[1] * y[2]) % FIB_MOD, (x[0] * y[1] + x[1] * y[3]) % FIB_MOD,
        (x[2] * y[0] + x[3] * y[2]) % FIB_MOD, (x[2] * y[1] + x[3] * y[3]) % FIB_MOD,
    };
    memcpy(r, t, sizeof t);   // via temp so r may alias x or y
}
long long fib_mod(long long n) {
    long long res[4] = {1, 0, 0, 1}, b[4] = {1, 1, 1, 0};
    for (long long e = n; e > 0; e >>= 1) {
        if (e & 1) mat_mul(res, res, b);
        mat_mul(b, b, b);
    }
    return res[1];
}""",
        "cpp": r"""// Fast doubling: from (F(k), F(k+1)) get (F(2k), F(2k+1)) directly.
//   F(2k)   = F(k) * (2*F(k+1) - F(k))
//   F(2k+1) = F(k)^2 + F(k+1)^2
static const long long MODF = 1000000007LL;
pair<long long, long long> fibPair(long long n) {      // returns (F(n), F(n+1))
    if (n == 0) return {0, 1};
    auto [a, b] = fibPair(n >> 1);                      // a = F(k), b = F(k+1), k = n/2
    long long c = a * ((2 * b - a + MODF) % MODF) % MODF;   // +MODF: keep it non-negative
    long long d = (a * a + b * b) % MODF;
    return (n & 1) ? make_pair(d, (c + d) % MODF) : make_pair(c, d);
}
long long fibMod(long long n) { return fibPair(n).first; }""",
        "rust": r"""const M: u64 = 1_000_000_007;
type Mat = [[u64; 2]; 2];

fn mul(a: &Mat, b: &Mat) -> Mat {
    let mut r = [[0u64; 2]; 2];
    for i in 0..2 {
        for j in 0..2 {
            // two products < 1e18 each; their sum < 2e18 < u64::MAX
            r[i][j] = (a[i][0] * b[0][j] + a[i][1] * b[1][j]) % M;
        }
    }
    r
}

pub fn fib_mod(n: i64) -> i64 {
    let (mut res, mut base): (Mat, Mat) = ([[1, 0], [0, 1]], [[1, 1], [1, 0]]);
    let mut e = n as u64;
    while e > 0 {
        if e & 1 == 1 {
            res = mul(&res, &base);
        }
        base = mul(&base, &base);
        e >>= 1;
    }
    res[0][1] as i64
}""",
    },
    tests=[[0], [10], [1], [2], [50], [90], [1000], [1000000007], [10**15], [123456789012345]],
)


# ----------------------------------------------------------------- base conversion
def _base_tests():
    r = _rng(1513)
    t = [[10, 2], [0, 2], [-5, 2], [255, 16], [1, 2], [-1, 2], [35, 36], [100, 7],
         [2**53 - 1, 2], [-(2**53 - 1), 36], [4096, 8], [-255, 16]]
    for _ in range(4):
        t.append([r.randint(-10**15, 10**15), r.randint(2, 36)])
    return t


P_BASE = dict(
    id="convert-to-base-b",
    title="Convert to Base B",
    difficulty=1,
    tags=["math", "base conversion", "string"],
    fn="to_base",
    params=[["n", "int"], ["base", "int"]],
    returns="str",
    statement=r"""
Write the integer `n` in base `base` (2 ≤ base ≤ 36) and return it as a string.

* Digits are `0–9` followed by **uppercase** `A–Z` (so base 16 uses `0123456789ABCDEF`).
* Negative numbers are written as a `-` followed by the representation of `|n|`
  (sign-magnitude, not two's complement).
* No leading zeros, and zero is `"0"`.

The most common case, `base = 2`, gives the binary string of `n`.
""",
    constraints=["|n| ≤ 2⁵³ − 1", "2 ≤ base ≤ 36"],
    example_notes=["`10 = 8 + 2 = 1010₂`.", "Zero is the one number whose representation is not produced by the division loop."],
    hints=[
        "The last digit of `n` in base `b` is `n % b`. What does `n // b` give you?",
        "Repeatedly take `n % b` (a digit) and set `n //= b`. The digits come out least significant first, so reverse at the end.",
        "Handle the sign separately (work on `|n|`) and special-case `n = 0`, for which the loop produces nothing.",
    ],
    explanation=r"""
## Intuition

A base-`b` numeral `dₖ…d₁d₀` means `Σ dᵢ·bⁱ`. Division by `b` peels off digits from the
right: `n % b = d₀` and `n // b = dₖ…d₁`. Repeat until nothing is left. This is the same
loop as reversing digits or summing digits, just with a digit alphabet.

## Approach

1. If `n == 0`, return `"0"`.
2. Remember the sign; set `m = |n|`.
3. While `m > 0`: append `DIGITS[m % b]`, `m //= b`.
4. Append `-` if negative, reverse, join.

Trace `n = -5`, `b = 2`:

| m | m % 2 | digits so far | m // 2 |
|---|---|---|---|
| 5 | 1 | "1" | 2 |
| 2 | 0 | "10" | 1 |
| 1 | 1 | "101" | 0 |

Reverse "101" → "101", prefix the sign: `"-101"`.

For base 2 you can also read bits directly: `(m >> i) & 1` from the top set bit down.
For bases that are powers of two (2, 4, 8, 16, 32) each digit is a fixed-size bit group,
which is why hex is so convenient: one hex digit = 4 bits.

## Complexity

* **Time:** O(log_b |n|) digits.
* **Space:** O(log_b |n|) for the string (at most 53 characters + sign).

## Common mistakes

* **Negative numbers with `%`.** In C, C++ and Rust, `-5 % 2 == -1`, so `DIGITS[n % b]`
  indexes out of bounds. In Python, `-5 % 2 == 1` and `-5 // 2 == -3`, so the loop gives
  garbage instead. Take the absolute value first.
* **`abs(LLONG_MIN)` overflows** in C. It cannot happen here (|n| < 2⁵³), but in general
  convert to `unsigned long long` and negate there.
* Forgetting `n = 0`.
* Returning digits in the order produced (reversed).

## Going further

* **Two's complement binary** of a negative number in w bits: `n & ((1 << w) - 1)`, then
  convert that non-negative number.
* **Negative bases**: in base −2 every integer has a sign-free representation; the loop
  needs a fix-up when the remainder is negative.
* Parsing is the reverse, Horner's rule: `value = value * b + digit`.
""",
    solution=r'''def to_base(n, base):
    DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if n == 0:
        return "0"                   # the loop below would produce an empty string
    negative = n < 0
    m = -n if negative else n        # work on |n|: % and // on negatives would misbehave
    out = []
    while m > 0:
        m, d = divmod(m, base)       # d is the current least-significant digit
        out.append(DIGITS[d])
    if negative:
        out.append("-")              # appended last, ends up first after reversing
    return "".join(reversed(out))    # digits were produced right to left
''',
    refs={
        "c": r"""char* to_base(long long n, long long base) {
    const char* DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    char buf[72];                       // 64 binary digits + sign + NUL is plenty
    int pos = 71;
    buf[pos] = '\0';
    // unsigned magnitude: avoids % on negatives and the abs(LLONG_MIN) overflow
    unsigned long long m = n < 0 ? 0ULL - (unsigned long long)n : (unsigned long long)n;
    do {                                // do-while handles n == 0 -> "0"
        buf[--pos] = DIGITS[m % (unsigned long long)base];
        m /= (unsigned long long)base;
    } while (m > 0);
    if (n < 0) buf[--pos] = '-';
    char* out = malloc((size_t)(72 - pos));
    memcpy(out, buf + pos, (size_t)(72 - pos));   // copy including the NUL
    return out;
}""",
        "cpp": r"""string toBase(long long n, long long base) {
    static const char* DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    if (n == 0) return "0";
    unsigned long long m = n < 0 ? 0ULL - (unsigned long long)n : (unsigned long long)n;
    string s;
    while (m > 0) { s += DIGITS[m % base]; m /= base; }
    if (n < 0) s += '-';
    reverse(s.begin(), s.end());
    return s;
}""",
        "rust": r"""pub fn to_base(n: i64, base: i64) -> String {
    const DIGITS: &[u8] = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    if n == 0 {
        return "0".to_string();
    }
    let (mut m, b) = (n.unsigned_abs(), base as u64);   // unsigned_abs never overflows
    let mut out = Vec::new();
    while m > 0 {
        out.push(DIGITS[(m % b) as usize]);
        m /= b;
    }
    if n < 0 {
        out.push(b'-');
    }
    out.reverse();
    String::from_utf8(out).unwrap()
}""",
    },
    tests=_base_tests(),
)


PROBLEMS = [
    P_SINGLE,
    P_POPCOUNT,
    P_COUNTBITS,
    P_REVBITS,
    P_POW4,
    P_MISSING,
    P_SUM,
    P_BASE,
    P_PASCAL,
    P_SIEVE,
    P_MODPOW,
    P_EXCEL,
    P_FIB,
]
