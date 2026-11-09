"""Track 13: Dynamic Programming."""
import random

TRACK = dict(
    id="dp",
    title="Dynamic Programming",
    order=13,
    icon="▤",
    blurb="Turn exponential recursion into polynomial tables: find the state, write the recurrence, fill it in the right order.",
    intro=r"""Dynamic programming (DP) is not an algorithm, it is a *way of making a slow
recursive solution fast*. Every DP solution in this track starts life as a brute-force
recursion that is correct but exponential. We then notice that it keeps solving the same
small problems over and over, remember those answers, and the exponential blow-up collapses
into a table we can fill in polynomial time.

## The two properties that make DP work

**Optimal substructure.** The answer to the big problem can be assembled from answers to
smaller problems of the *same shape*. The cheapest way to reach stair 10 is the cheapest
way to reach stair 9 or 8, plus one more step. The longest common subsequence of two strings
is built from the LCS of their prefixes.

**Overlapping subproblems.** The naive recursion asks for the same small answer many times.
Computing Fibonacci recursively calls `fib(3)` dozens of times on the way to `fib(10)`:

```text
                    fib(5)
              /               \
          fib(4)              fib(3)        <- fib(3) computed twice,
         /      \            /      \          fib(2) three times...
     fib(3)    fib(2)    fib(2)    fib(1)
     /    \
 fib(2) fib(1)
```

If the subproblems did *not* overlap (merge sort's halves are disjoint), remembering answers
would not help, and the technique is called divide and conquer instead.

## From brute force to tabulation: the four steps

Take "how many ways can you climb `n` stairs taking 1 or 2 steps at a time".

**1. Brute-force recursion.** Describe the answer in terms of smaller answers.

```python
def ways(n):
    if n <= 1:
        return 1
    return ways(n - 1) + ways(n - 2)      # O(2^n): the tree above
```

**2. Memoization (top-down).** Same code, but cache every result. Each distinct argument is
now computed once, so the cost is *(number of states) × (work per state)* = O(n).

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def ways(n):
    if n <= 1:
        return 1
    return ways(n - 1) + ways(n - 2)
```

**3. Tabulation (bottom-up).** Replace recursion with a loop that fills a table in an order
where every dependency is already computed. No recursion depth limits, no call overhead.

```python
dp = [1] * (n + 1)
for i in range(2, n + 1):
    dp[i] = dp[i - 1] + dp[i - 2]
```

**4. Space optimization.** Look at which cells the recurrence actually reads. Here only the
previous two, so two variables replace the whole array. For 2-D tables that read only the
previous row, a single row (or two) suffices.

Top-down is often easier to *write* (you only describe the recurrence; the cache figures out
the order). Bottom-up is easier to *optimize* and never overflows the call stack: Python's
default recursion limit is 1000, and ESPresso's call depth is far smaller, so in this track
the ESPresso reference solutions are always iterative.

## How to find the state

The state is the *minimum information you need to describe a subproblem* so that its answer
does not depend on how you got there. Ask:

- **What changes between recursive calls?** Usually an index (`i`), a pair of indices
  (`i, j`), a remaining budget (`capacity`, `amount`), or a small flag (`holding a stock?`).
- **Is the future independent of the past, given the state?** If two paths reach state
  `(i, holding=True)` the best you can do from there must be the same. If it is not, the state
  is missing information.
- **Write the definition down in one sentence.** "`dp[i]` = the most money I can rob from
  houses `0..i`." Most DP bugs are a fuzzy definition, not a fuzzy loop.

Then the **recurrence** comes from considering the *last decision*: rob house `i` or not;
take coin `c` last; match the last characters or not. The **base cases** are the states with
no decision left (empty prefix, amount 0, the start cell). The **answer** is some particular
state (often the last one) or the best over all states.

## Common DP shapes

| shape | state | typical recurrence | examples here |
|---|---|---|---|
| 1-D linear | `dp[i]` over a prefix | `dp[i]` from `dp[i-1]`, `dp[i-2]` | stairs, house robber, decode ways |
| 1-D over all earlier | `dp[i]` | best over every `j < i` | LIS, word break |
| 2-D grid | `dp[r][c]` | from top and left neighbours | unique paths, min path sum, maximal square |
| string pair | `dp[i][j]` over prefixes of `a`, `b` | match last chars or drop one | LCS, edit distance, regex, distinct subsequences |
| knapsack | `dp[i][cap]` or `dp[cap]` | take item or skip it | 0/1 knapsack, partition, coin change |
| interval | `dp[l][r]` over a subarray | split at some `k` in `(l, r)` | burst balloons, palindromes |
| state machine | `dp[i][state]` | transitions between a few modes | stock with cooldown |

Two classic traps in the knapsack shape are worth memorising now. In a 1-D knapsack array,
iterating capacity **downwards** uses each item at most once (0/1 knapsack), while iterating
**upwards** lets an item be reused (unbounded / coin change). And for "count the ways", put the
loop over *items* outside to count **combinations**; put it inside to count **permutations**.

## Complexity

The cost of a DP is almost always

```text
time  = (number of states) × (transitions per state)
space = (number of states), often reducible to one row or a few variables
```

`n` states with O(1) transitions is O(n); an `n × m` string-pair table is O(n·m); an interval
DP with a split point is O(n³). When you see constraints like `n ≤ 1000` with two strings,
think O(n·m); `n ≤ 300` with a split point, think O(n³).

## Working the problems

For every problem, before coding, write down: the **state** in one sentence, the
**recurrence**, the **base cases**, the **fill order**, and where the **answer** lives. Then
fill a tiny table by hand. If the hand table is right, the code almost writes itself.
""",
)

PROBLEMS = []

# ---------------------------------------------------------------------------
# 1. Climbing stairs
# ---------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="climbing-stairs",
    title="Climbing Stairs",
    difficulty=1,
    tags=["dp", "1-D", "fibonacci"],
    fn="climb_stairs",
    params=[["n", "int"]],
    returns="int",
    statement=r"""You are at the bottom of a staircase with `n` steps. Each move you climb
either **1** or **2** steps. In how many distinct sequences of moves can you reach the top
(exactly step `n`)?

Two sequences are different if they differ in at least one move: `1+2` and `2+1` count as
two ways.""",
    example_notes=[
        "Two ways: `1+1` or `2`.",
        "Three ways: `1+1+1`, `1+2`, `2+1`.",
    ],
    constraints=["1 ≤ n ≤ 45 (the answer fits in a signed 32-bit integer)"],
    hints=[
        "Think about your *last* move. To stand on step `n`, where were you just before?",
        "You were either on step `n-1` (then took 1) or on step `n-2` (then took 2). Those two groups of sequences never overlap.",
        "So `ways(n) = ways(n-1) + ways(n-2)` with `ways(0) = ways(1) = 1`. Compute it with a loop, keeping only the last two values.",
    ],
    explanation=r"""## Intuition

The question asks you to *count* sequences, and every sequence ends with a last move of
either 1 or 2. Splitting by the last move is the core DP idea: the set of all ways to reach
step `n` is the disjoint union of "ways to reach `n-1`, then a 1" and "ways to reach `n-2`,
then a 2". Counting each group is the same problem on a smaller `n`.

## Approach

**State.** `dp[i]` = number of distinct move sequences that end exactly on step `i`.

**Recurrence.** `dp[i] = dp[i-1] + dp[i-2]` for `i ≥ 2`.

**Base cases.** `dp[0] = 1` (the empty sequence: you are already there) and `dp[1] = 1`
(just `1`). Defining `dp[0] = 1` is not a trick: there really is exactly one way to climb zero
stairs, doing nothing, and it makes `dp[2] = 2` fall out naturally.

**Table for `n = 5`:**

| i | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| dp[i] | 1 | 1 | 2 | 3 | 5 | 8 |

These are the Fibonacci numbers shifted by one.

**Top-down (memoized).** Direct transcription of the recurrence, with a cache so each `i` is
computed once:

```python
from functools import lru_cache

def climb_stairs(n):
    @lru_cache(maxsize=None)
    def ways(i):
        if i <= 1:
            return 1
        return ways(i - 1) + ways(i - 2)
    return ways(n)
```

Without `lru_cache` this is the exponential Fibonacci tree: `ways(45)` makes over a billion
calls.

**Bottom-up.** Fill `dp[0..n]` left to right; each cell only needs cells to its left.

```python
dp = [1] * (n + 1)
for i in range(2, n + 1):
    dp[i] = dp[i - 1] + dp[i - 2]
return dp[n]
```

**Space-optimized.** `dp[i]` reads only the two previous cells, so keep two variables and
slide them forward. That is the reference solution.

## Complexity

O(n) time: one addition per step. O(1) extra space for the rolling version (O(n) for the
table or the memo, plus O(n) call stack for the top-down version).

## Common mistakes

- **Wrong base case.** Starting with `dp[1] = 1, dp[2] = 2` works but then `n = 1` needs a
  special case; starting from `dp[0] = dp[1] = 1` avoids it.
- **Off-by-one in the loop.** The loop must produce `dp[n]`, so in Python it runs over
  `range(2, n + 1)`; in C, `for (i = 2; i <= n; i++)`.
- **Overflow.** `dp[45] = 1836311903`, just under 2³¹. In C use `long long` anyway; at
  `n = 46` a 32-bit `int` silently wraps negative.
- **Rolling variables updated in the wrong order.** `a = b; b = a + b` loses the old `a`.
  Use a temporary or simultaneous assignment `a, b = b, a + b`.

## Going further

- If you may take 1, 2 *or 3* steps, the recurrence gains a third term. With an arbitrary
  step set `S`, `dp[i] = Σ dp[i-s]` for `s ∈ S`: that is exactly "Coin Change II" but counting
  *ordered* sequences (permutations), so the loop over `S` goes *inside* the loop over `i`.
- Fibonacci numbers satisfy `[[1,1],[1,0]]^n`; matrix fast exponentiation gives the answer in
  O(log n) multiplications, useful when `n` is huge and the answer is taken modulo a prime.
""",
    solution=r"""def climb_stairs(n):
    # prev2 = ways to reach step i-2, prev1 = ways to reach step i-1.
    # We start at i = 2 with dp[0] = 1 (do nothing) and dp[1] = 1 (a single 1-step).
    prev2, prev1 = 1, 1
    for _ in range(2, n + 1):
        # Every way to reach step i ends with a 1-step (from i-1) or a 2-step (from i-2).
        # The two groups are disjoint, so the counts simply add.
        prev2, prev1 = prev1, prev1 + prev2
    # After the loop prev1 holds dp[n]. For n = 1 the loop never runs and dp[1] = 1.
    return prev1
""",
    refs={
        "c": r"""long long climb_stairs(long long n) {
    /* prev2 = dp[i-2], prev1 = dp[i-1]; dp[0] = dp[1] = 1. */
    long long prev2 = 1, prev1 = 1;
    for (long long i = 2; i <= n; i++) {
        long long cur = prev1 + prev2;   /* last move was a 1-step or a 2-step */
        prev2 = prev1;                   /* slide the window one step to the right */
        prev1 = cur;
    }
    return prev1;
}""",
        "cpp": r"""long long climbStairs(long long n) {
    // Rolling pair (dp[i-2], dp[i-1]) starting from dp[0] = dp[1] = 1.
    long long prev2 = 1, prev1 = 1;
    for (long long i = 2; i <= n; ++i) {
        long long cur = prev1 + prev2;
        prev2 = prev1;
        prev1 = cur;
    }
    return prev1;
}""",
        "rust": r"""pub fn climb_stairs(n: i64) -> i64 {
    // (dp[i-2], dp[i-1]) as a tuple we slide forward.
    let (mut prev2, mut prev1) = (1i64, 1i64);
    for _ in 2..=n {
        // Tuple assignment reads both old values before writing either.
        (prev2, prev1) = (prev1, prev1 + prev2);
    }
    prev1
}""",
        "espresso": r"""fn climbStairs(n) {
  // prev2 = dp[i-2], prev1 = dp[i-1]; dp[0] = dp[1] = 1
  var prev2 = 1
  var prev1 = 1
  for var i in 2..n + 1 {
    var cur = prev1 + prev2   // last move was 1 step (from i-1) or 2 steps (from i-2)
    prev2 = prev1
    prev1 = cur
  }
  return prev1
}""",
    },
    tests=[[2], [3], [1], [4], [5], [10], [20], [38], [44], [45]],
))

# ---------------------------------------------------------------------------
# 2. Min cost climbing stairs
# ---------------------------------------------------------------------------
def _mcs_tests():
    r = random.Random(1302)
    t = [[[10, 15, 20]], [[1, 100, 1, 1, 1, 100, 1, 1, 100, 1]], [[0, 0]], [[5, 3]],
         [[7, 1, 7]], [[0, 1, 2, 2]], [[999, 999, 999, 999, 999]]]
    t.append([[r.randint(0, 999) for _ in range(25)]])
    t.append([[r.randint(0, 50) for _ in range(40)]])
    return t


PROBLEMS.append(dict(
    id="min-cost-climbing-stairs",
    title="Min Cost Climbing Stairs",
    difficulty=1,
    tags=["dp", "1-D"],
    fn="min_cost_climbing_stairs",
    params=[["cost", "int[]"]],
    returns="int",
    statement=r"""A staircase has steps `0 … n-1`, and stepping **off** step `i` costs `cost[i]`.
You may start on step `0` or step `1` for free. From step `i` you pay `cost[i]` and move to
`i + 1` or `i + 2`. The **top** is the position `n`, just past the last step.

Return the minimum total cost to reach the top.""",
    example_notes=[
        "Start on step 1, pay 15 and jump two steps to the top.",
        "Pay the 1s and hop over every 100: start at 0, then 2, 3, 4, 6, 7, 9 → top, total 6.",
    ],
    constraints=["2 ≤ len(cost) ≤ 1000", "0 ≤ cost[i] ≤ 999"],
    hints=[
        "Define `dp[i]` as the cheapest way to *stand on* position `i` (with `i = n` being the top).",
        "You arrive at `i` either from `i-1` (paying `cost[i-1]`) or from `i-2` (paying `cost[i-2]`).",
        "`dp[0] = dp[1] = 0` because you may start there for free. Answer: `dp[n]`. Only the last two values are ever read.",
    ],
    explanation=r"""## Intuition

"Minimum total cost" with moves of 1 or 2 is Climbing Stairs with `min` instead of `+`.
Instead of counting all paths to a step, we keep only the cheapest one: if two paths reach
step `i`, the more expensive one can never become part of an optimal route afterwards
(optimal substructure).

## Approach

**State.** `dp[i]` = minimum cost to *stand on* position `i`, for `0 ≤ i ≤ n`, where
position `n` is the top.

**Recurrence.** To stand on `i` you came from `i-1` and paid `cost[i-1]`, or from `i-2` and
paid `cost[i-2]`:

```text
dp[i] = min(dp[i-1] + cost[i-1], dp[i-2] + cost[i-2])
```

**Base cases.** `dp[0] = dp[1] = 0`: you may start on either for free.

**Answer.** `dp[n]`.

**Table for `cost = [1,100,1,1,1,100,1,1,100,1]`:**

| i | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cost[i] | 1 | 100 | 1 | 1 | 1 | 100 | 1 | 1 | 100 | 1 | top |
| dp[i] | 0 | 0 | 1 | 2 | 2 | 3 | 3 | 4 | 4 | 5 | 6 |

Look at `dp[6] = 3`: coming from 5 would cost `3 + 100`, coming from 4 costs `2 + 1`. The
table quietly routes around every 100.

**Top-down.**

```python
from functools import lru_cache

def min_cost_climbing_stairs(cost):
    n = len(cost)
    @lru_cache(maxsize=None)
    def best(i):                      # cheapest way to stand on i
        if i <= 1:
            return 0
        return min(best(i - 1) + cost[i - 1], best(i - 2) + cost[i - 2])
    return best(n)
```

**Bottom-up.** Allocate `dp = [0] * (n + 1)` and fill `i = 2 … n` with the recurrence.

**Space-optimized.** Only `dp[i-1]` and `dp[i-2]` are read, so two variables suffice; that
is the reference solution.

## Complexity

O(n) time, one `min` per position. O(1) extra space for the rolling version.

## Common mistakes

- **Returning `dp[n-1]`.** The top is *past* the last step. Equivalent formulation: the
  answer is `min(f[n-1], f[n-2])` where `f[i]` is the cost *including* `cost[i]`, and
  mixing the two definitions is the usual bug. Pick one sentence and stick to it.
- **Charging the starting step.** Starting on step 0 or 1 is free; you pay a step's cost
  only when you leave it.
- **Forgetting `n = 2`.** The loop runs once, `dp[2] = min(cost[0], cost[1])`. Good: no
  special case needed.

## Going further

If you could jump up to `k` steps, the recurrence becomes `dp[i] = min over 1 ≤ s ≤ k of
dp[i-s] + cost[i-s]`, which is O(n·k). A **monotonic deque** holding the window minimum
brings it back to O(n): a sliding-window minimum is the standard optimisation for
"min over the last `k` DP values".
""",
    solution=r"""def min_cost_climbing_stairs(cost):
    n = len(cost)
    # Rolling window over dp[i-2], dp[i-1], where dp[i] = cheapest way to STAND on i.
    # Starting on step 0 or 1 is free, so dp[0] = dp[1] = 0.
    two_back, one_back = 0, 0
    for i in range(2, n + 1):
        # Arrive at i from i-1 (paying to leave i-1) or from i-2 (paying to leave i-2).
        cur = min(one_back + cost[i - 1], two_back + cost[i - 2])
        two_back, one_back = one_back, cur
    # Position n is the top (one past the last step).
    return one_back
""",
    refs={
        "cpp": r"""long long minCostClimbingStairs(vector<long long>& cost) {
    int n = cost.size();
    long long twoBack = 0, oneBack = 0;      // dp[i-2], dp[i-1]
    for (int i = 2; i <= n; ++i) {
        long long cur = min(oneBack + cost[i - 1], twoBack + cost[i - 2]);
        twoBack = oneBack;
        oneBack = cur;
    }
    return oneBack;                          // dp[n]: the top
}""",
        "rust": r"""pub fn min_cost_climbing_stairs(cost: Vec<i64>) -> i64 {
    let n = cost.len();
    let (mut two_back, mut one_back) = (0i64, 0i64);   // dp[i-2], dp[i-1]
    for i in 2..=n {
        let cur = (one_back + cost[i - 1]).min(two_back + cost[i - 2]);
        two_back = one_back;
        one_back = cur;
    }
    one_back
}""",
        "espresso": r"""fn minCostClimbingStairs(cost) {
  var n = len(cost)
  var twoBack = 0     // dp[i-2]
  var oneBack = 0     // dp[i-1]
  for var i in 2..n + 1 {
    var a = oneBack + cost[i - 1]   // arrive from i-1
    var b = twoBack + cost[i - 2]   // arrive from i-2
    var cur = a
    if b < a { cur = b }
    twoBack = oneBack
    oneBack = cur
  }
  return oneBack
}""",
    },
    tests=_mcs_tests(),
))

# ---------------------------------------------------------------------------
# 3. House robber
# ---------------------------------------------------------------------------
def _rob_tests():
    r = random.Random(1303)
    t = [[[1, 2, 3, 1]], [[2, 7, 9, 3, 1]], [[5]], [[0]], [[2, 1]], [[1, 3, 1]],
         [[2, 1, 1, 2]], [[0, 0, 0, 0]], [[400, 400, 400, 400, 400]]]
    t.append([[r.randint(0, 400) for _ in range(30)]])
    t.append([[r.randint(0, 20) for _ in range(40)]])
    return t


PROBLEMS.append(dict(
    id="house-robber",
    title="House Robber",
    difficulty=2,
    tags=["dp", "1-D", "take or skip"],
    fn="rob_houses",
    params=[["nums", "int[]"]],
    returns="int",
    statement=r"""Houses stand in a row and `nums[i]` is the cash in house `i`. Adjacent
houses share an alarm: robbing **two neighbouring houses** sets it off.

Return the largest total you can rob without robbing any two adjacent houses.""",
    example_notes=[
        "Rob houses 0 and 2: `1 + 3 = 4`.",
        "Rob houses 0, 2 and 4: `2 + 9 + 1 = 12`.",
    ],
    constraints=["1 ≤ len(nums) ≤ 100", "0 ≤ nums[i] ≤ 400"],
    hints=[
        "Greedy (take the biggest, skip its neighbours) fails on `[2, 3, 2]`... and many others. Think about the last house instead.",
        "For house `i` there are only two choices: rob it (then house `i-1` is off limits) or skip it.",
        "`dp[i] = max(dp[i-1], dp[i-2] + nums[i])`, where `dp[i]` is the best using houses `0..i`. Two rolling variables are enough.",
    ],
    explanation=r"""## Intuition

The "no two adjacent" rule means a decision about house `i` only constrains house `i-1`.
That locality is what makes a 1-D DP work: if we know the best loot from the first `i-1`
houses and the first `i-2` houses, the choice at house `i` is fully determined.

Greedy ideas (take the largest, or take all even/odd indices) all fail somewhere: on
`[2, 1, 1, 2]` the best is `2 + 2` using houses 0 and 3, which is neither parity class.

## Approach

**State.** `dp[i]` = maximum loot using only houses `0..i` (house `i` may or may not be
robbed).

**Recurrence.** Decide house `i`:

- skip it: `dp[i-1]`
- rob it: then `i-1` is skipped, so `dp[i-2] + nums[i]`

```text
dp[i] = max(dp[i-1], dp[i-2] + nums[i])
```

**Base cases.** Treat `dp[-1] = dp[-2] = 0` (no houses, no money). Then `dp[0] = nums[0]`
and `dp[1] = max(nums[0], nums[1])` come out of the recurrence.

**Table for `[2, 7, 9, 3, 1]`:**

| i | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| nums | 2 | 7 | 9 | 3 | 1 |
| dp | 2 | 7 | 11 | 11 | 12 |

At `i = 2`: skip gives 7, rob gives `dp[0] + 9 = 11`. At `i = 3`: rob gives `7 + 3 = 10 <
11`, so we skip. At `i = 4`: rob gives `11 + 1 = 12`.

**Top-down.**

```python
from functools import lru_cache

def rob_houses(nums):
    @lru_cache(maxsize=None)
    def best(i):                 # best using houses 0..i
        if i < 0:
            return 0
        return max(best(i - 1), best(i - 2) + nums[i])
    return best(len(nums) - 1)
```

**Bottom-up.** `dp = [0] * (n + 2)` with an offset of 2 so `dp[i + 2]` stores the value for
house `i` and the two leading zeros play the role of `dp[-2]`, `dp[-1]`.

**Space-optimized.** Only the last two values are read: keep `prev2` (best through `i-2`) and
`prev1` (best through `i-1`). Reference solution below.

## Complexity

O(n) time, O(1) extra space.

## Common mistakes

- **Index errors for `n = 1` or `n = 2`.** Writing `dp[0] = nums[0]; dp[1] = max(nums[0],
  nums[1])` crashes on a single house. The virtual zeros before the array avoid special cases.
- **Defining `dp[i]` as "best when house `i` is robbed".** That definition works but then the
  recurrence is `nums[i] + max(dp[i-2], dp[i-3])` and the answer is `max(dp[n-1], dp[n-2])`.
  Easy to get subtly wrong; the "using houses `0..i`" definition is cleaner.
- **Updating rolling variables in the wrong order.** Compute the new value into a temporary
  first, then shift.

## Going further

- Houses in a **circle** (first and last adjacent): see House Robber II.
- Houses in a **tree** (parent and child adjacent): return a pair `(rob_this, skip_this)` from
  each subtree in a post-order DFS. Same take-or-skip recurrence, different shape.
- "Delete and earn": pick a value `v`, earn `v` per occurrence, delete all `v-1` and `v+1`.
  Bucket the totals by value and it *is* house robber.
""",
    solution=r"""def rob_houses(nums):
    # prev2 = best loot using houses up to i-2, prev1 = best using houses up to i-1.
    # Before any house both are 0 (virtual empty prefixes), so no special cases for n = 1.
    prev2, prev1 = 0, 0
    for x in nums:
        # Either skip this house (keep prev1) or rob it, which forces skipping the
        # previous house, so we add x to the best loot ending two houses back.
        cur = max(prev1, prev2 + x)
        prev2, prev1 = prev1, cur
    return prev1
""",
    refs={
        "c": r"""long long rob_houses(long long* nums, int numsSize) {
    long long prev2 = 0, prev1 = 0;          /* best through i-2, best through i-1 */
    for (int i = 0; i < numsSize; i++) {
        long long take = prev2 + nums[i];    /* rob house i: neighbour i-1 is skipped */
        long long cur = take > prev1 ? take : prev1;
        prev2 = prev1;
        prev1 = cur;
    }
    return prev1;
}""",
        "cpp": r"""long long robHouses(vector<long long>& nums) {
    long long prev2 = 0, prev1 = 0;          // best through i-2, best through i-1
    for (long long x : nums) {
        long long cur = max(prev1, prev2 + x);
        prev2 = prev1;
        prev1 = cur;
    }
    return prev1;
}""",
        "rust": r"""pub fn rob_houses(nums: Vec<i64>) -> i64 {
    // fold carries the pair (best through i-2, best through i-1).
    let (_, best) = nums.iter().fold((0i64, 0i64), |(prev2, prev1), &x| {
        (prev1, prev1.max(prev2 + x))
    });
    best
}""",
        "espresso": r"""fn robHouses(nums) {
  var prev2 = 0   // best using houses up to i-2
  var prev1 = 0   // best using houses up to i-1
  for var i in 0..len(nums) {
    var cur = prev1                 // skip house i
    if prev2 + nums[i] > cur {      // or rob it (house i-1 must then be skipped)
      cur = prev2 + nums[i]
    }
    prev2 = prev1
    prev1 = cur
  }
  return prev1
}""",
    },
    tests=_rob_tests(),
))

# ---------------------------------------------------------------------------
# 4. House robber II (circular)
# ---------------------------------------------------------------------------
def _rob2_tests():
    r = random.Random(1304)
    t = [[[2, 3, 2]], [[1, 2, 3, 1]], [[1, 2, 3]], [[7]], [[4, 9]], [[5, 1, 1, 5]],
         [[0, 0]], [[200, 3, 140, 20, 10]], [[1, 3, 1, 3, 100]]]
    t.append([[r.randint(0, 1000) for _ in range(30)]])
    t.append([[r.randint(0, 30) for _ in range(35)]])
    return t


PROBLEMS.append(dict(
    id="house-robber-circular",
    title="House Robber II (Circle)",
    difficulty=2,
    tags=["dp", "1-D", "circular"],
    fn="rob_circle",
    params=[["nums", "int[]"]],
    returns="int",
    statement=r"""Same rules as House Robber, but the houses stand in a **circle**: house `0`
and house `n-1` are neighbours too. `nums[i]` is the cash in house `i`.

Return the maximum you can rob without robbing two adjacent houses. A single house is not
adjacent to itself.""",
    example_notes=[
        "Houses 0 and 2 are neighbours in the circle, so the best is house 1 alone.",
        "Rob houses 0 and 2: `1 + 3 = 4`.",
    ],
    constraints=["1 ≤ len(nums) ≤ 100", "0 ≤ nums[i] ≤ 1000"],
    hints=[
        "The circle only adds one constraint: you cannot rob *both* house 0 and house `n-1`.",
        "So at least one of them is skipped. Which subproblems does that give you?",
        "Answer = `max(rob_line(nums[0 : n-1]), rob_line(nums[1 : n]))`, using the linear House Robber. Handle `n = 1` separately.",
    ],
    explanation=r"""## Intuition

A circle breaks the left-to-right order that the linear DP relies on: the decision at the
last house depends on the decision at the first. The standard trick is to **break the cycle
by case analysis** on the one problematic edge. Any valid plan skips house `0` or skips house
`n-1` (or both). So:

- plans that skip house `n-1` are exactly the linear problem on `nums[0 .. n-2]`;
- plans that skip house `0` are exactly the linear problem on `nums[1 .. n-1]`.

The best plan is in one of these two families, so the answer is the larger of the two linear
answers. Plans that skip both are counted in both families, which is harmless for a `max`.

## Approach

**Linear state** (reused from House Robber). For a range `lo..hi`, `dp[i]` = best loot from
houses `lo..i`, with `dp[i] = max(dp[i-1], dp[i-2] + nums[i])` and zeros before `lo`.

**Combine.** `answer = max(line(0, n-2), line(1, n-1))`, with `n = 1` returning `nums[0]`
(the only house has no neighbour, and both ranges would be empty).

**Tables for `[1, 2, 3, 1]`:**

| range | houses | dp values | best |
|---|---|---|---|
| skip last: `0..2` | 1, 2, 3 | 1, 2, 4 | 4 |
| skip first: `1..3` | 2, 3, 1 | 2, 3, 3 | 3 |

Answer `max(4, 3) = 4`. For `[2, 3, 2]` the two ranges give `max(2, 3) = 3` and `max(3, 2) =
3`, so the answer is 3: the plan "houses 0 and 2" that the linear version would pick is never
considered.

**Top-down.** Memoize `best(i, lo)` = best from houses `lo..i`; call it with `(n-2, 0)` and
`(n-1, 1)`. The extra `lo` parameter just marks which of the two subproblems you are in.

**Bottom-up / space-optimized.** Write the rolling two-variable linear robber as a helper
taking a range, call it twice. That is the reference solution.

## Complexity

Two linear passes: O(n) time, O(1) space.

## Common mistakes

- **`n = 1`.** Both ranges are empty and would return 0, but the answer is `nums[0]`.
- **Trying to track "was house 0 robbed" inside a single pass.** It works (a DP with an extra
  flag), but it doubles the state and is easy to get wrong; two clean passes are simpler.
- **Slicing in a hot loop.** In Python `nums[1:]` copies the list; harmless here, but in C or
  Rust pass index bounds instead of building new arrays.

## Going further

The same "cut the cycle at one edge and try both cases" idea works for many circular
problems: maximum circular subarray sum (`max(kadane, total - min_subarray)`), circular
gas stations, and painting a circular fence with no two neighbours the same colour.
""",
    solution=r"""def rob_circle(nums):
    n = len(nums)
    # One house: it has no neighbour, take it.
    if n == 1:
        return nums[0]

    def rob_line(lo, hi):
        # Linear House Robber on nums[lo..hi] inclusive, with rolling variables.
        prev2, prev1 = 0, 0
        for i in range(lo, hi + 1):
            prev2, prev1 = prev1, max(prev1, prev2 + nums[i])
        return prev1

    # Houses 0 and n-1 are neighbours, so some optimal plan skips at least one of them.
    # Case A: house n-1 is skipped -> linear problem on 0..n-2.
    # Case B: house 0 is skipped   -> linear problem on 1..n-1.
    return max(rob_line(0, n - 2), rob_line(1, n - 1))
""",
    refs={
        "cpp": r"""long long robLine(const vector<long long>& a, int lo, int hi) {
    long long prev2 = 0, prev1 = 0;            // best through i-2, i-1
    for (int i = lo; i <= hi; ++i) {
        long long cur = max(prev1, prev2 + a[i]);
        prev2 = prev1;
        prev1 = cur;
    }
    return prev1;
}

long long robCircle(vector<long long>& nums) {
    int n = nums.size();
    if (n == 1) return nums[0];
    // Skip the last house, or skip the first: the circle's extra edge can't be violated.
    return max(robLine(nums, 0, n - 2), robLine(nums, 1, n - 1));
}""",
        "rust": r"""fn rob_line(a: &[i64]) -> i64 {
    let (mut prev2, mut prev1) = (0i64, 0i64);
    for &x in a {
        let cur = prev1.max(prev2 + x);
        prev2 = prev1;
        prev1 = cur;
    }
    prev1
}

pub fn rob_circle(nums: Vec<i64>) -> i64 {
    let n = nums.len();
    if n == 1 {
        return nums[0];
    }
    // Slices borrow without copying: [0, n-1) skips the last house, [1, n) skips the first.
    rob_line(&nums[..n - 1]).max(rob_line(&nums[1..]))
}""",
        "espresso": r"""fn robLine(nums, lo, hi) {
  var prev2 = 0
  var prev1 = 0
  var i = lo
  while i <= hi {
    var cur = prev1
    if prev2 + nums[i] > cur { cur = prev2 + nums[i] }
    prev2 = prev1
    prev1 = cur
    i += 1
  }
  return prev1
}

fn robCircle(nums) {
  var n = len(nums)
  if n == 1 { return nums[0] }
  var a = robLine(nums, 0, n - 2)   // house n-1 skipped
  var b = robLine(nums, 1, n - 1)   // house 0 skipped
  if a > b { return a }
  return b
}""",
    },
    tests=_rob2_tests(),
))

# ---------------------------------------------------------------------------
# 5. Coin change (min coins)
# ---------------------------------------------------------------------------
def _coin_tests():
    r = random.Random(1305)
    t = [[[1, 2, 5], 11], [[2], 3], [[1], 0], [[1], 7], [[2, 5, 10, 1], 27], [[186, 419, 83, 408], 6249],
         [[3, 7], 5], [[5, 3], 7], [[1, 3, 4], 6], [[7, 13], 1]]
    t.append([[r.randint(5, 60) for _ in range(5)], 3000])
    t.append([[1, 7, 23, 89, 233], 10000])
    t.append([[9973], 10000])
    return t


PROBLEMS.append(dict(
    id="coin-change-min-coins",
    title="Coin Change (Fewest Coins)",
    difficulty=2,
    tags=["dp", "unbounded knapsack"],
    fn="coin_change",
    params=[["coins", "int[]"], ["amount", "int"]],
    returns="int",
    statement=r"""You have an unlimited supply of coins of each denomination in `coins`.
Return the **fewest** coins needed to make exactly `amount`, or `-1` if it cannot be made.

Making `amount = 0` needs zero coins.""",
    example_notes=[
        "`11 = 5 + 5 + 1`, three coins.",
        "Only 2s: every total is even, so 3 is impossible.",
    ],
    constraints=["1 ≤ len(coins) ≤ 12", "1 ≤ coins[i] ≤ 10⁴, all distinct", "0 ≤ amount ≤ 10⁴"],
    hints=[
        "Greedy (always take the largest coin that fits) fails for `coins = [1, 3, 4]`, `amount = 6`: it gives `4+1+1` but `3+3` is better.",
        "Think about the *last* coin used. If it was `c`, the rest is an optimal solution for `amount - c`.",
        "`dp[a] = 1 + min(dp[a - c])` over coins `c ≤ a`, with `dp[0] = 0` and 'infinity' meaning unreachable. Fill `a = 1 … amount`.",
    ],
    explanation=r"""## Intuition

The amount shrinks every time you pick a coin, and the best way to finish from a given
remaining amount does not depend on which coins got you there. So the state is just the
remaining amount, and the decision is "which coin do I use last?". This is the
**unbounded knapsack** shape: items (coins) can be reused.

Greedy is tempting because it works for real currencies, but those are specially designed
("canonical") coin systems. For `[1, 3, 4]` and 6, greedy takes `4, 1, 1` while `3, 3` is
optimal.

## Approach

**State.** `dp[a]` = fewest coins summing to exactly `a`, or ∞ if impossible.

**Recurrence.** For each coin `c ≤ a`: use `c` last, and make `a - c` optimally.

```text
dp[a] = 1 + min(dp[a - c] for c in coins if c ≤ a)
```

**Base case.** `dp[0] = 0`. Everything else starts at ∞.

**Answer.** `dp[amount]`, or `-1` if it is still ∞.

**Table for `coins = [1, 2, 5]`, `amount = 11`:**

| amount | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dp | 0 | 1 | 1 | 2 | 2 | 1 | 2 | 2 | 3 | 3 | 2 | 3 |

`dp[11] = 1 + min(dp[10], dp[9], dp[6]) = 1 + min(2, 3, 2) = 3`.

**Top-down.**

```python
from functools import lru_cache

def coin_change(coins, amount):
    @lru_cache(maxsize=None)
    def best(a):
        if a == 0:
            return 0
        res = float("inf")
        for c in coins:
            if c <= a:
                res = min(res, best(a - c) + 1)
        return res
    ans = best(amount)
    return -1 if ans == float("inf") else ans
```

With `amount = 10⁴` and coin `1`, the recursion is 10⁴ deep: past Python's default limit.
This is exactly when bottom-up wins.

**Bottom-up.** Fill `dp[1..amount]` in increasing order (each cell reads smaller amounts).
This *is* already the space-optimal form: the state is 1-D and every earlier cell may be read,
so there is nothing to roll away. An equivalent and slightly faster loop order puts coins
outside: `for c in coins: for a in range(c, amount+1): dp[a] = min(dp[a], dp[a-c] + 1)`. For a
`min` either order is correct (unlike counting, see Coin Change II).

## Complexity

O(amount × len(coins)) time, O(amount) space. Here at most 1.2 × 10⁵ steps.

## Common mistakes

- **Using `-1` as the "impossible" marker inside the DP.** `min` then prefers it. Use a
  sentinel bigger than any answer (`amount + 1` works: you never need more than `amount` coins
  when every coin is ≥ 1) and convert at the end.
- **Overflow with `INT_MAX + 1`.** In C, `dp[a - c] + 1` on an `INT_MAX` sentinel wraps
  negative. Use `amount + 1` as the sentinel, or check before adding.
- **Forgetting `amount = 0` → 0.**
- **Greedy.** See above.

## Going further

- To return the actual coins, store `choice[a] = c` for the coin that achieved the minimum,
  then walk back from `amount`.
- BFS from 0 over the graph "a → a + c" finds the same answer level by level and can stop
  early when `amount` is reached.
- Counting the number of ways instead of the minimum: Coin Change II.
""",
    solution=r"""def coin_change(coins, amount):
    # Sentinel for "impossible": you never need more than `amount` coins (every coin >= 1),
    # so amount + 1 behaves like infinity but stays a small int (safe to add 1 to).
    INF = amount + 1
    # dp[a] = fewest coins summing to exactly a. dp[0] = 0: no coins for nothing.
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            # Use coin c last; the rest (a - c) must itself be made optimally.
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    # Still at the sentinel means no combination reaches `amount`.
    return dp[amount] if dp[amount] <= amount else -1
""",
    refs={
        "c": r"""long long coin_change(long long* coins, int coinsSize, long long amount) {
    long long INF = amount + 1;                 /* never more than `amount` coins */
    long long* dp = malloc(sizeof(long long) * (amount + 1));
    dp[0] = 0;
    for (long long a = 1; a <= amount; a++) {
        dp[a] = INF;
        for (int k = 0; k < coinsSize; k++) {
            long long c = coins[k];
            if (c <= a && dp[a - c] + 1 < dp[a]) dp[a] = dp[a - c] + 1;   /* c used last */
        }
    }
    long long ans = dp[amount] <= amount ? dp[amount] : -1;
    free(dp);
    return ans;
}""",
        "cpp": r"""long long coinChange(vector<long long>& coins, long long amount) {
    const long long INF = amount + 1;
    vector<long long> dp(amount + 1, INF);
    dp[0] = 0;
    // Coins outside, amounts inside, increasing: each coin may be reused (unbounded).
    for (long long c : coins)
        for (long long a = c; a <= amount; ++a)
            dp[a] = min(dp[a], dp[a - c] + 1);
    return dp[amount] > amount ? -1 : dp[amount];
}""",
        "rust": r"""pub fn coin_change(coins: Vec<i64>, amount: i64) -> i64 {
    let amt = amount as usize;
    let inf = amount + 1;                       // safe "infinity"
    let mut dp = vec![inf; amt + 1];
    dp[0] = 0;
    for a in 1..=amt {
        for &c in &coins {
            let c = c as usize;
            if c <= a {
                dp[a] = dp[a].min(dp[a - c] + 1);
            }
        }
    }
    if dp[amt] > amount { -1 } else { dp[amt] }
}""",
    },
    espresso=False,
    tests=_coin_tests(),
))

# ---------------------------------------------------------------------------
# 6. Coin change II (number of combinations)
# ---------------------------------------------------------------------------
def _coin2_tests():
    r = random.Random(1306)
    t = [[5, [1, 2, 5]], [3, [2]], [10, [10]], [0, [7]], [4, [1, 2, 3]], [100, [1, 5, 10, 25, 50]],
         [7, [2, 4]], [500, [3, 5, 7, 8, 9, 10, 11]], [1000, [1, 2, 5, 10, 20, 50, 100, 200, 500]]]
    t.append([1500, sorted(r.sample(range(5, 80), 6))])
    return t


PROBLEMS.append(dict(
    id="coin-change-combinations",
    title="Coin Change II (Count Combinations)",
    difficulty=2,
    tags=["dp", "unbounded knapsack", "counting"],
    fn="count_coin_combinations",
    params=[["amount", "int"], ["coins", "int[]"]],
    returns="int",
    statement=r"""With an unlimited supply of each coin in `coins`, count the number of
**combinations** that sum to exactly `amount`.

Combinations ignore order: `1+2+2` and `2+1+2` are the same combination. Making `0` has
exactly one combination (use no coins).""",
    example_notes=[
        "`5`, `2+2+1`, `2+1+1+1`, `1+1+1+1+1`: four combinations.",
        "Only 2s cannot make an odd amount.",
    ],
    constraints=["0 ≤ amount ≤ 5000", "1 ≤ len(coins) ≤ 300, coins distinct, 1 ≤ coins[i] ≤ 5000",
                 "the answer is below 2⁵³"],
    hints=[
        "If you count `dp[a] = Σ dp[a - c]` over all coins, you count `1+2` and `2+1` separately. You need a way to fix an order.",
        "Fix the order by deciding coin *types* one at a time: first how many of coin 0, then coin 1, and so on.",
        "`dp[a]` = ways using only the coins processed so far. For each coin `c` (outer loop), for `a` from `c` up to `amount`: `dp[a] += dp[a - c]`.",
    ],
    explanation=r"""## Intuition

Counting is fragile: every combination must be counted **exactly once**. The naive
recurrence "last coin is `c`" counts *sequences* (`1+2` and `2+1` both end differently), so it
over-counts. To count combinations we impose a canonical order: write each combination with
its coins sorted by denomination index. Then we can build combinations coin type by coin type
and never generate the same multiset twice.

## Approach

**State.** `dp[i][a]` = number of combinations making `a` using only the first `i` coin types.

**Recurrence.** For coin type `i` with value `c`, either use none of it, or use at least one
(take one and stay on the same row, since more may follow):

```text
dp[i][a] = dp[i-1][a] + dp[i][a - c]      (second term only if c ≤ a)
```

**Base cases.** `dp[i][0] = 1` (the empty combination), `dp[0][a > 0] = 0`.

**Table for `amount = 5`, `coins = [1, 2, 5]`** (each row is the 1-D array after processing
that coin):

| coins \ amt | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| (none) | 1 | 0 | 0 | 0 | 0 | 0 |
| after 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| after 2 | 1 | 1 | 2 | 2 | 3 | 3 |
| after 5 | 1 | 1 | 2 | 2 | 3 | 4 |

`dp[2][4] = dp[1][4] + dp[2][2] = 1 + 2 = 3`: `{1,1,1,1}`, `{1,1,2}`, `{2,2}`.

**Top-down.**

```python
from functools import lru_cache

def count_coin_combinations(amount, coins):
    @lru_cache(maxsize=None)
    def ways(i, a):              # combinations of a using coins[i:]
        if a == 0:
            return 1
        if i == len(coins):
            return 0
        skip = ways(i + 1, a)
        take = ways(i, a - coins[i]) if coins[i] <= a else 0
        return skip + take
    return ways(0, amount)
```

**Bottom-up 2-D.** Fill rows `i = 1 … n`, columns `a = 0 … amount` left to right.

**Space-optimized 1-D.** Row `i` reads row `i-1` at the *same* column and row `i` at a
*smaller* column. With one array updated in place, left to right, `dp[a]` still holds the old
row value when read and `dp[a - c]` already holds the new one. Exactly what we need:

```python
dp = [1] + [0] * amount
for c in coins:                 # coin types OUTSIDE: combinations
    for a in range(c, amount + 1):
        dp[a] += dp[a - c]
```

## Complexity

O(amount × len(coins)) time, O(amount) space.

## Common mistakes

- **Swapping the loops.** `for a: for c: dp[a] += dp[a - c]` counts **permutations** (it is
  the "climbing stairs with step set `coins`" problem): for `amount = 3`, `coins = [1, 2]` it
  returns 3 instead of 2.
- **Iterating `a` downward.** That turns the unbounded knapsack into 0/1 (each coin at most
  once).
- **`dp[0] = 0`.** Then nothing is ever counted. The empty combination is real.
- **Overflow.** Counts grow fast. Use 64-bit integers; the statement keeps the answer
  below 2⁵³.

## Going further

- Counting with each coin at most once: iterate `a` downward (0/1 knapsack counting).
- Counting modulo `10⁹ + 7` is the usual competitive-programming form: just reduce after each
  addition.
- Generating functions: the answer is the coefficient of `x^amount` in `Π 1/(1 - x^c)`. The DP
  above is exactly multiplying those series one factor at a time.
""",
    solution=r"""def count_coin_combinations(amount, coins):
    # dp[a] = number of combinations making a using the coin types processed so far.
    # Initially (no coin types) only amount 0 is reachable, by the empty combination.
    dp = [1] + [0] * amount
    # Coin types in the OUTER loop: each combination is built in a fixed order of types,
    # so {1, 2} is generated once, never also as {2, 1}.
    for c in coins:
        # Increasing a: dp[a - c] already includes uses of coin c, so c can be reused
        # any number of times (unbounded knapsack).
        for a in range(c, amount + 1):
            # Ways without any more c (old dp[a]) + ways that use at least one more c.
            dp[a] += dp[a - c]
    return dp[amount]
""",
    refs={
        "cpp": r"""long long countCoinCombinations(long long amount, vector<long long>& coins) {
    vector<long long> dp(amount + 1, 0);
    dp[0] = 1;                                // the empty combination
    for (long long c : coins)                 // coin types outside -> combinations
        for (long long a = c; a <= amount; ++a)
            dp[a] += dp[a - c];               // a upward -> unlimited copies of c
    return dp[amount];
}""",
        "rust": r"""pub fn count_coin_combinations(amount: i64, coins: Vec<i64>) -> i64 {
    let amt = amount as usize;
    let mut dp = vec![0i64; amt + 1];
    dp[0] = 1;
    for &c in &coins {
        let c = c as usize;
        for a in c..=amt {
            dp[a] += dp[a - c];
        }
    }
    dp[amt]
}""",
    },
    espresso=False,
    tests=_coin2_tests(),
))

# ---------------------------------------------------------------------------
# 7. Unique paths
# ---------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="unique-paths-grid",
    title="Unique Paths",
    difficulty=2,
    tags=["dp", "2-D grid", "combinatorics"],
    fn="unique_paths",
    params=[["m", "int"], ["n", "int"]],
    returns="int",
    statement=r"""A robot starts in the top-left cell of an `m × n` grid and wants to reach the
bottom-right cell. It can only move **right** or **down**, one cell at a time.

Return the number of distinct paths.""",
    example_notes=[
        "3 rows, 7 columns: 28 paths.",
        "3 rows, 2 columns: right-down-down, down-right-down, down-down-right.",
    ],
    constraints=["1 ≤ m, n ≤ 100", "the answer is at most 2 · 10⁹"],
    hints=[
        "How can the robot arrive at cell `(r, c)`? Only from above or from the left.",
        "`paths(r, c) = paths(r-1, c) + paths(r, c-1)`. What is `paths` for any cell in the first row or first column?",
        "Each row only reads the row above, so a single array of length `n` updated left to right is enough: `row[c] += row[c-1]`.",
    ],
    explanation=r"""## Intuition

Every path into cell `(r, c)` makes its final move either *down* from `(r-1, c)` or *right*
from `(r, c-1)`, and those two groups of paths are disjoint. So the count for a cell is the
sum of the counts of its top and left neighbours. That is the 2-D grid DP shape: the state is
the cell, and the dependencies point up and left, so a row-major sweep always has them ready.

## Approach

**State.** `dp[r][c]` = number of monotone paths from `(0, 0)` to `(r, c)`.

**Recurrence.** `dp[r][c] = dp[r-1][c] + dp[r][c-1]` for `r, c ≥ 1`.

**Base cases.** First row and first column are all `1`: there is exactly one way to walk
straight along an edge.

**Table for a 3 × 4 grid:**

| | c0 | c1 | c2 | c3 |
|---|---|---|---|---|
| r0 | 1 | 1 | 1 | 1 |
| r1 | 1 | 2 | 3 | 4 |
| r2 | 1 | 3 | 6 | 10 |

The answer is the bottom-right cell, 10. (Rotate the table 45° and you are looking at
Pascal's triangle.)

**Top-down.**

```python
from functools import lru_cache

def unique_paths(m, n):
    @lru_cache(maxsize=None)
    def paths(r, c):
        if r == 0 or c == 0:
            return 1
        return paths(r - 1, c) + paths(r, c - 1)
    return paths(m - 1, n - 1)
```

**Bottom-up 2-D.** Allocate `m × n`, set the edges to 1, sweep row by row.

**Space-optimized 1-D.** Keep one row. Before the update, `row[c]` still holds the value from
the row above; `row[c-1]` has already been updated to the current row. So `row[c] +=
row[c-1]` is exactly `up + left`:

```text
row after r0: 1 1 1 1
row after r1: 1 2 3 4
row after r2: 1 3 6 10
```

## Complexity

O(m · n) time, O(n) space for the rolling row (O(m · n) for the full table or the memo).

## Common mistakes

- **Initialising the edges to 0.** Then every cell is 0. The edges have exactly one path.
- **Swapping `m` and `n`.** The answer is symmetric, so tests won't catch it, but the next
  grid problem (with obstacles) will.
- **Overflow in the closed form.** `C(m+n-2, m-1)` computed as `(m+n-2)! / ...` overflows
  64 bits long before the answer does. Multiply and divide incrementally instead (see below).

## Going further

**Combinatorics.** A path is a sequence of `m-1` downs and `n-1` rights in some order, so
the answer is the binomial coefficient `C(m+n-2, m-1)`. Compute it as

```python
res = 1
for i in range(1, m):
    res = res * (n - 1 + i) // i      # exact at every step
```

Each partial product is itself a binomial coefficient, so the division is always exact.
O(min(m, n)) time, O(1) space. The DP is still the version to learn, because it survives
obstacles, costs, and other twists that break the formula.
""",
    solution=r"""def unique_paths(m, n):
    # row[c] = number of paths to cell (r, c) for the row r we are currently on.
    # Row 0: one way to reach each cell (keep moving right).
    row = [1] * n
    for _ in range(1, m):
        # Column 0 stays 1 (keep moving down). For c >= 1:
        #   row[c] (before the update) = paths to the cell ABOVE,
        #   row[c-1] (already updated) = paths to the cell on the LEFT.
        for c in range(1, n):
            row[c] += row[c - 1]
    return row[n - 1]
""",
    refs={
        "cpp": r"""long long uniquePaths(long long m, long long n) {
    vector<long long> row(n, 1);            // row 0: all ones
    for (long long r = 1; r < m; ++r)
        for (long long c = 1; c < n; ++c)
            row[c] += row[c - 1];           // above (old value) + left (new value)
    return row[n - 1];
}""",
        "rust": r"""pub fn unique_paths(m: i64, n: i64) -> i64 {
    let n = n as usize;
    let mut row = vec![1i64; n];
    for _ in 1..m {
        for c in 1..n {
            row[c] += row[c - 1];
        }
    }
    row[n - 1]
}""",
    },
    espresso=False,
    tests=[[3, 7], [3, 2], [1, 1], [1, 100], [100, 1], [2, 2], [10, 10], [7, 3], [23, 12], [17, 17], [2, 100]],
))

# ---------------------------------------------------------------------------
# 8. Unique paths with obstacles
# ---------------------------------------------------------------------------
def _obs_tests():
    r = random.Random(1308)
    t = [[[[0, 0, 0], [0, 1, 0], [0, 0, 0]]], [[[0, 1], [0, 0]]], [[[0]]], [[[1]]],
         [[[1, 0], [0, 0]]], [[[0, 0], [0, 1]]], [[[0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [1, 0, 0, 0]]],
         [[[0, 0, 1, 0, 0]]], [[[0], [0], [0]]], [[[0, 0, 0], [1, 1, 0], [0, 0, 0]]]]
    g = [[1 if r.random() < 0.2 else 0 for _ in range(8)] for _ in range(7)]
    g[0][0] = g[-1][-1] = 0
    t.append([g])
    return t


PROBLEMS.append(dict(
    id="unique-paths-with-obstacles",
    title="Unique Paths with Obstacles",
    difficulty=2,
    tags=["dp", "2-D grid"],
    fn="unique_paths_with_obstacles",
    params=[["grid", "int[][]"]],
    returns="int",
    statement=r"""A robot starts at the top-left cell of `grid` and wants to reach the
bottom-right cell, moving only **right** or **down**. `grid[r][c] == 1` marks an obstacle the
robot cannot enter; `0` is free.

Return the number of distinct paths. If the start or the end is an obstacle, the answer is
`0`.""",
    example_notes=[
        "The rock in the centre leaves two paths: around the top-right or around the bottom-left.",
        "Down then right is the only way around the rock.",
    ],
    constraints=["1 ≤ rows, cols ≤ 100", "grid[r][c] is 0 or 1", "the answer is below 2³¹"],
    hints=[
        "Same recurrence as Unique Paths, `up + left`. What is the count for an obstacle cell?",
        "An obstacle cell has 0 paths into it, which automatically cuts off every path through it.",
        "Careful with the first row and column: they are no longer all 1. Once an obstacle appears on the edge, every cell after it on that edge is 0. Starting the sweep with `dp[0][0] = 1` and using `up + left` (with missing neighbours as 0) handles that for free.",
    ],
    explanation=r"""## Intuition

Obstacles do not change the structure of the problem, only the values: a blocked cell is a
cell with **zero** ways to stand on it. Because counts propagate by addition, a zero there
removes every path through that cell from everything downstream. No special path-tracking
logic is needed.

## Approach

**State.** `dp[r][c]` = number of paths from `(0, 0)` to `(r, c)` avoiding obstacles.

**Recurrence.**

```text
dp[r][c] = 0                              if grid[r][c] == 1
dp[r][c] = dp[r-1][c] + dp[r][c-1]        otherwise (missing neighbours count as 0)
```

**Base case.** `dp[0][0] = 1` if the start is free, else 0. Do *not* pre-fill the edges with
1s: an obstacle on the top row must zero out everything to its right. Letting the recurrence
handle edges (with out-of-grid neighbours treated as 0) gets this right automatically.

**Table** (`#` = obstacle) for

```text
0 0 0 0
0 1 0 0
0 0 0 1
1 0 0 0
```

| | c0 | c1 | c2 | c3 |
|---|---|---|---|---|
| r0 | 1 | 1 | 1 | 1 |
| r1 | 1 | # | 1 | 2 |
| r2 | 1 | 1 | 2 | # |
| r3 | # | 1 | 3 | 3 |

Answer: 3. Note `dp[1][2] = 1`: the only way in is from above, because its left neighbour is a
rock.

**Top-down.**

```python
from functools import lru_cache

def unique_paths_with_obstacles(grid):
    @lru_cache(maxsize=None)
    def paths(r, c):
        if r < 0 or c < 0 or grid[r][c] == 1:
            return 0
        if r == 0 and c == 0:
            return 1
        return paths(r - 1, c) + paths(r, c - 1)
    return paths(len(grid) - 1, len(grid[0]) - 1)
```

**Bottom-up.** Sweep row-major filling `dp`. **Space-optimized:** one row `row[c]`, where an
obstacle sets `row[c] = 0` and otherwise `row[c] += row[c-1]` (for `c ≥ 1`). That is the
reference solution.

**In place.** If you are allowed to destroy the input, the grid itself can be the table:
visit cells row-major, and when you reach `(r, c)` its own value is still the original 0/1
while its top and left neighbours have already been overwritten with counts. The ESPresso
reference does exactly that, since ESPresso cannot allocate an array of runtime size.

## Complexity

O(rows · cols) time. O(cols) extra space for the rolling row, O(1) for the in-place version.

## Common mistakes

- **Filling edges with 1** as in the obstacle-free version.
- **Forgetting the blocked start or end.** The recurrence handles both if the obstacle check
  comes *before* the `dp[0][0] = 1` base case.
- **In-place confusion.** If you overwrite the grid, a count of `1` and an obstacle `1` look
  the same. Read the cell's original value *before* writing, and only ever read already
  converted cells from the neighbours.

## Going further

- **Minimum path sum** replaces `+` of counts with `min` of costs (next problem).
- Allowing moves in all four directions creates cycles, and the DP order no longer exists.
  Counting simple paths becomes exponential; shortest paths become BFS/Dijkstra.
""",
    solution=r"""def unique_paths_with_obstacles(grid):
    rows, cols = len(grid), len(grid[0])
    # row[c] = number of paths to (r, c) for the current row r.
    # Before row 0 we pretend there is a row of zeros above, except that we seed the
    # start: the very first cell gets exactly one path if it is free.
    row = [0] * cols
    row[0] = 1
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                # A rock: nobody can stand here, so it contributes nothing downstream.
                row[c] = 0
            elif c > 0:
                # row[c] still holds the count from the row above; row[c-1] is the
                # freshly computed cell to the left.
                row[c] += row[c - 1]
            # c == 0 and free: only the cell above feeds it, and row[0] already holds that.
    return row[cols - 1]
""",
    refs={
        "cpp": r"""long long uniquePathsWithObstacles(vector<vector<long long>>& grid) {
    int R = grid.size(), C = grid[0].size();
    vector<long long> row(C, 0);
    row[0] = 1;                                   // seed the start (zeroed below if blocked)
    for (int r = 0; r < R; ++r)
        for (int c = 0; c < C; ++c) {
            if (grid[r][c] == 1) row[c] = 0;      // obstacle: no paths through here
            else if (c > 0) row[c] += row[c - 1]; // above + left
        }
    return row[C - 1];
}""",
        "rust": r"""pub fn unique_paths_with_obstacles(grid: Vec<Vec<i64>>) -> i64 {
    let cols = grid[0].len();
    let mut row = vec![0i64; cols];
    row[0] = 1;
    for line in &grid {
        for c in 0..cols {
            if line[c] == 1 {
                row[c] = 0;
            } else if c > 0 {
                row[c] += row[c - 1];
            }
        }
    }
    row[cols - 1]
}""",
        "espresso": r"""fn uniquePathsWithObstacles(grid) {
  // The grid itself becomes the DP table. When we reach (r, c) its value is still the
  // original 0/1, while (r-1, c) and (r, c-1) already hold path counts.
  var rows = len(grid)
  var cols = len(grid[0])
  for var r in 0..rows {
    for var c in 0..cols {
      if grid[r][c] == 1 {
        grid[r][c] = 0                    // rock: zero paths
      } else if r == 0 and c == 0 {
        grid[r][c] = 1                    // free start
      } else {
        var ways = 0
        if r > 0 { ways += grid[r - 1][c] }
        if c > 0 { ways += grid[r][c - 1] }
        grid[r][c] = ways
      }
    }
  }
  return grid[rows - 1][cols - 1]
}""",
    },
    tests=_obs_tests(),
))

# ---------------------------------------------------------------------------
# 9. Minimum path sum
# ---------------------------------------------------------------------------
def _mps_tests():
    r = random.Random(1309)
    t = [[[[1, 3, 1], [1, 5, 1], [4, 2, 1]]], [[[1, 2, 3], [4, 5, 6]]], [[[7]]], [[[0, 0], [0, 0]]],
         [[[1, 2, 3, 4]]], [[[1], [9], [1]]], [[[1, 9, 9], [1, 9, 9], [1, 1, 1]]],
         [[[5, 1, 1], [1, 9, 1], [1, 1, 1]]]]
    t.append([[[r.randint(0, 200) for _ in range(9)] for _ in range(8)]])
    t.append([[[r.randint(0, 9) for _ in range(12)] for _ in range(4)]])
    return t


PROBLEMS.append(dict(
    id="minimum-path-sum-grid",
    title="Minimum Path Sum",
    difficulty=2,
    tags=["dp", "2-D grid"],
    fn="min_path_sum",
    params=[["grid", "int[][]"]],
    returns="int",
    statement=r"""`grid` is filled with non-negative numbers. Walk from the top-left cell to the
bottom-right cell moving only **right** or **down**. The cost of a path is the sum of all
cells it visits, including both endpoints.

Return the minimum cost.""",
    example_notes=[
        "The path `1 → 3 → 1 → 1 → 1` costs 7.",
        "`1 → 2 → 3 → 6` costs 12.",
    ],
    constraints=["1 ≤ rows, cols ≤ 200", "0 ≤ grid[r][c] ≤ 200"],
    hints=[
        "The cheapest path to `(r, c)` arrives from the top or from the left, and the part before that must itself be the cheapest path to that neighbour.",
        "`best[r][c] = grid[r][c] + min(best[r-1][c], best[r][c-1])`. Edges have only one neighbour.",
        "One row of length `cols` is enough; or overwrite the grid itself in row-major order.",
    ],
    explanation=r"""## Intuition

This is Unique Paths with `min` instead of `+`. Optimal substructure holds because costs are
additive and non-negative: if the cheapest path to the corner passes through `(r-1, c)`, its
prefix must be a cheapest path to `(r-1, c)`; otherwise swapping in the cheaper prefix would
give a cheaper overall path.

## Approach

**State.** `best[r][c]` = minimum sum of a path from `(0, 0)` to `(r, c)`, including both.

**Recurrence.**

```text
best[r][c] = grid[r][c] + min(best[r-1][c], best[r][c-1])
```

where a neighbour outside the grid is ∞ (it cannot be used).

**Base case.** `best[0][0] = grid[0][0]`. The first row is a running sum to the right; the
first column a running sum downward.

**Table for `[[1,3,1],[1,5,1],[4,2,1]]`:**

| | c0 | c1 | c2 |
|---|---|---|---|
| r0 | 1 | 4 | 5 |
| r1 | 2 | 7 | 6 |
| r2 | 6 | 8 | 7 |

`best[2][2] = 1 + min(6, 8) = 7`; following the minima backwards recovers the path
`(0,0) → (0,1) → (0,2) → (1,2) → (2,2)`.

**Top-down.**

```python
from functools import lru_cache

def min_path_sum(grid):
    @lru_cache(maxsize=None)
    def best(r, c):
        if r == 0 and c == 0:
            return grid[0][0]
        up = best(r - 1, c) if r > 0 else float("inf")
        left = best(r, c - 1) if c > 0 else float("inf")
        return grid[r][c] + min(up, left)
    return best(len(grid) - 1, len(grid[0]) - 1)
```

For a 200 × 200 grid the recursion goes 400 deep: fine for Python, too deep for some
embedded interpreters.

**Bottom-up.** Fill a `rows × cols` table row by row.

**Space-optimized.** Keep one row: `row[c] = grid[r][c] + min(row[c], row[c-1])` where
`row[c]` (old) is the cell above and `row[c-1]` (new) the cell to the left. The reference
solution does this; the ESPresso reference instead overwrites the grid in place.

## Complexity

O(rows · cols) time, O(cols) extra space (O(1) in place).

## Common mistakes

- **Treating out-of-grid neighbours as 0.** That makes the edges look free. They must be ∞
  (or handled by separate edge loops).
- **Forgetting to add `grid[0][0]`** or the final cell.
- **Greedy (step to the cheaper neighbour).** On `[[1,2,9],[3,9,9],[1,1,1]]` it steps right
  onto the 2 and is then trapped between 9s (total 22), while going down first costs 7. The
  DP compares *whole prefixes*, not single steps.

## Going further

- **Recover the path** by walking back from the corner, at each cell moving to whichever of
  top/left has the smaller `best`.
- With moves in **four directions** and non-negative weights the DP order disappears (cycles);
  use **Dijkstra**. With negative weights, Bellman-Ford.
- **Triangle** (LeetCode 120) is the same idea on a triangular grid, and is easiest bottom-up
  from the last row.
""",
    solution=r"""def min_path_sum(grid):
    rows, cols = len(grid), len(grid[0])
    INF = float("inf")
    # row[c] = cheapest cost to reach (r, c) for the current row r.
    # Before row 0, every "cell above" is unreachable (INF)...
    row = [INF] * cols
    # ...except we let the start inherit cost 0 so that row 0, col 0 becomes grid[0][0].
    row[0] = 0
    for r in range(rows):
        for c in range(cols):
            # Old row[c] is the cell above; row[c-1] was just updated, so it's the cell
            # to the left. Pick the cheaper way in, then pay for this cell.
            left = row[c - 1] if c > 0 else INF
            row[c] = grid[r][c] + min(row[c], left)
    return row[cols - 1]
""",
    refs={
        "cpp": r"""long long minPathSum(vector<vector<long long>>& grid) {
    int R = grid.size(), C = grid[0].size();
    const long long INF = LLONG_MAX / 4;
    vector<long long> row(C, INF);
    row[0] = 0;                                   // so that best[0][0] = grid[0][0]
    for (int r = 0; r < R; ++r)
        for (int c = 0; c < C; ++c) {
            long long left = c > 0 ? row[c - 1] : INF;
            row[c] = grid[r][c] + min(row[c], left);   // row[c] is "above" before the write
        }
    return row[C - 1];
}""",
        "rust": r"""pub fn min_path_sum(grid: Vec<Vec<i64>>) -> i64 {
    let cols = grid[0].len();
    let inf = i64::MAX / 4;
    let mut row = vec![inf; cols];
    row[0] = 0;
    for line in &grid {
        for c in 0..cols {
            let left = if c > 0 { row[c - 1] } else { inf };
            row[c] = line[c] + row[c].min(left);
        }
    }
    row[cols - 1]
}""",
        "espresso": r"""fn minPathSum(grid) {
  // Overwrite the grid in row-major order: each cell becomes the cheapest cost to reach it.
  var rows = len(grid)
  var cols = len(grid[0])
  for var r in 0..rows {
    for var c in 0..cols {
      if r == 0 and c == 0 {
        // start: cost is just the cell itself
      } else if r == 0 {
        grid[r][c] += grid[r][c - 1]          // top row: only from the left
      } else if c == 0 {
        grid[r][c] += grid[r - 1][c]          // left column: only from above
      } else {
        var up = grid[r - 1][c]
        var left = grid[r][c - 1]
        if up < left { grid[r][c] += up } else { grid[r][c] += left }
      }
    }
  }
  return grid[rows - 1][cols - 1]
}""",
    },
    tests=_mps_tests(),
))

# ---------------------------------------------------------------------------
# 10. Longest increasing subsequence
# ---------------------------------------------------------------------------
def _lis_tests():
    r = random.Random(1310)
    t = [[[10, 9, 2, 5, 3, 7, 101, 18]], [[0, 1, 0, 3, 2, 3]], [[7, 7, 7, 7, 7, 7, 7]], [[5]],
         [[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]], [[4, 10, 4, 3, 8, 9]], [[-2, -1]],
         [[3, 5, 6, 2, 5, 4, 19, 5, 6, 7, 12]]]
    t.append([[r.randint(-100, 100) for _ in range(40)]])
    t.append([[r.randint(0, 30) for _ in range(50)]])
    return t


PROBLEMS.append(dict(
    id="longest-increasing-subsequence",
    title="Longest Increasing Subsequence",
    difficulty=2,
    tags=["dp", "1-D", "binary search", "patience sorting"],
    fn="length_of_lis",
    params=[["nums", "int[]"]],
    returns="int",
    statement=r"""Return the length of the longest **strictly increasing subsequence** of
`nums`.

A subsequence keeps the original order but may skip elements: `[3, 6, 2, 7]` has `[3, 6, 7]`
as a subsequence. Strictly increasing means each element is greater than the previous one
(equal values do not count).""",
    example_notes=[
        "`[2, 3, 7, 101]` (or `[2, 5, 7, 18]` and others) has length 4.",
        "`[0, 1, 2, 3]` has length 4.",
    ],
    constraints=["1 ≤ len(nums) ≤ 2500", "-10⁴ ≤ nums[i] ≤ 10⁴"],
    hints=[
        "Define the state around where a subsequence *ends*: `dp[i]` = length of the longest increasing subsequence that ends exactly at index `i`.",
        "To end at `i`, the previous element is some `j < i` with `nums[j] < nums[i]`. So `dp[i] = 1 + max(dp[j])` over those `j` (or 1 if there are none).",
        "The answer is `max(dp)`, not `dp[n-1]`: the best subsequence need not end at the last element. O(n²) is fine here; an O(n log n) method exists (see the explanation).",
    ],
    explanation=r"""## Intuition

"Longest subsequence" problems need a state that pins down enough about the subsequence to
extend it. What matters for extending an increasing subsequence is **its last element**. So
we index subproblems by where the subsequence ends: if we know the best length ending at every
earlier position, the best length ending at `i` is one more than the best among those whose
last value is smaller than `nums[i]`.

This is the "1-D over all earlier" shape: each state looks back at *every* previous state,
not just the previous one or two.

## Approach

**State.** `dp[i]` = length of the longest strictly increasing subsequence that **ends at
index `i`** (it must include `nums[i]`).

**Recurrence.**

```text
dp[i] = 1 + max(dp[j] for j < i if nums[j] < nums[i])     (or 1 if no such j)
```

**Base case.** Each element alone is an increasing subsequence: `dp[i] ≥ 1`.

**Answer.** `max(dp[0..n-1])`.

**Table for `[10, 9, 2, 5, 3, 7, 101, 18]`:**

| i | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| nums | 10 | 9 | 2 | 5 | 3 | 7 | 101 | 18 |
| dp | 1 | 1 | 1 | 2 | 2 | 3 | 4 | 4 |

`dp[5]` (value 7) looks back at values `2, 5, 3` (all smaller), whose best `dp` is 2, so 3.

**Top-down.**

```python
from functools import lru_cache

def length_of_lis(nums):
    @lru_cache(maxsize=None)
    def ending_at(i):
        best = 1
        for j in range(i):
            if nums[j] < nums[i]:
                best = max(best, ending_at(j) + 1)
        return best
    return max(ending_at(i) for i in range(len(nums)))
```

**Bottom-up.** Fill `dp` left to right with a double loop. That is the reference solution:
O(n²), about 3 million steps for n = 2500.

**Space.** No rolling trick here: every `dp[j]` may be read later. But a smarter state removes
the inner loop entirely, see *Going further*.

## Complexity

O(n²) time, O(n) space.

## Common mistakes

- **Returning `dp[-1]`.** In `[1, 2, 3, 0]` the best subsequence ends at index 2, not 3.
- **`<=` instead of `<`.** Equal values are not strictly increasing: `[7, 7, 7]` has LIS 1.
- **Confusing subsequence with subarray.** A subarray must be contiguous; then a single pass
  with a running counter suffices.

## Going further: O(n log n) with patience sorting

Keep an array `tails` where `tails[k]` = the **smallest possible last value** of an increasing
subsequence of length `k + 1` seen so far. `tails` is always strictly increasing (a longer
subsequence can't end lower than a shorter one's best ending). For each `x`:

- find the first position `p` with `tails[p] ≥ x` (binary search, `bisect_left`);
- if `p == len(tails)`, `x` extends the longest subsequence: append it;
- otherwise set `tails[p] = x`: we found a length-`(p+1)` subsequence with a smaller ending.

```text
x=10  tails=[10]
x=9   tails=[9]
x=2   tails=[2]
x=5   tails=[2, 5]
x=3   tails=[2, 3]
x=7   tails=[2, 3, 7]
x=101 tails=[2, 3, 7, 101]
x=18  tails=[2, 3, 7, 18]      -> length 4
```

`tails` is *not* an actual subsequence, but its length is the answer. O(n log n) time, O(n)
space. The ESPresso reference does this **in place**: at step `i` the tails occupy
`nums[0..len)` with `len ≤ i`, so writing `tails[p]` (`p ≤ len ≤ i`) never clobbers an
element we haven't read yet.

Using `bisect_right` (first `> x`) instead gives the longest **non-decreasing** subsequence.
""",
    solution=r"""def length_of_lis(nums):
    n = len(nums)
    # dp[i] = length of the longest strictly increasing subsequence that ENDS at index i.
    # Every element on its own is such a subsequence, so start at 1.
    dp = [1] * n
    for i in range(n):
        for j in range(i):
            # nums[i] can extend any increasing subsequence ending at j with a smaller value.
            if nums[j] < nums[i] and dp[j] + 1 > dp[i]:
                dp[i] = dp[j] + 1
    # The best subsequence can end anywhere, not necessarily at the last index.
    return max(dp)
""",
    refs={
        "cpp": r"""long long lengthOfLis(vector<long long>& nums) {
    // O(n log n) patience sorting: tails[k] = smallest tail of an increasing
    // subsequence of length k+1. lower_bound finds the first tail >= x.
    vector<long long> tails;
    for (long long x : nums) {
        auto it = lower_bound(tails.begin(), tails.end(), x);
        if (it == tails.end()) tails.push_back(x);   // extends the longest one
        else *it = x;                                // better (smaller) tail for that length
    }
    return tails.size();
}""",
        "rust": r"""pub fn length_of_lis(nums: Vec<i64>) -> i64 {
    // O(n^2) DP: dp[i] = longest increasing subsequence ending at i.
    let n = nums.len();
    let mut dp = vec![1i64; n];
    for i in 0..n {
        for j in 0..i {
            if nums[j] < nums[i] {
                dp[i] = dp[i].max(dp[j] + 1);
            }
        }
    }
    *dp.iter().max().unwrap()
}""",
        "espresso": r"""fn lengthOfLis(nums) {
  // Patience sorting in place: tails live in nums[0..size). At step i, size <= i,
  // so writing nums[pos] (pos <= size) never overwrites an unread element.
  var size = 0
  for var i in 0..len(nums) {
    var x = nums[i]
    // binary search: first pos in [0, size) with nums[pos] >= x
    var lo = 0
    var hi = size
    while lo < hi {
      var mid = (lo + hi) / 2
      if nums[mid] < x { lo = mid + 1 } else { hi = mid }
    }
    nums[lo] = x
    if lo == size { size += 1 }     // x extended the longest subsequence
  }
  return size
}""",
    },
    tests=_lis_tests(),
))

# ---------------------------------------------------------------------------
# 11. Longest common subsequence
# ---------------------------------------------------------------------------
def _lcs_tests():
    r = random.Random(1311)
    t = [["abcde", "ace"], ["abc", "abc"], ["abc", "def"], ["a", "a"], ["a", "b"],
         ["bsbininm", "jmjkbkjkv"], ["ezupkr", "ubmrapg"], ["oxcpqrsvwf", "shmtulqrypy"],
         ["aaaa", "aa"]]
    t.append(["".join(r.choice("abcd") for _ in range(300)), "".join(r.choice("abcd") for _ in range(400))])
    t.append(["".join(r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(500)),
              "".join(r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(450))])
    return t


PROBLEMS.append(dict(
    id="longest-common-subsequence",
    title="Longest Common Subsequence",
    difficulty=2,
    tags=["dp", "string pair", "2-D"],
    fn="longest_common_subsequence",
    params=[["text1", "str"], ["text2", "str"]],
    returns="int",
    statement=r"""Return the length of the longest **common subsequence** of `text1` and
`text2`, or 0 if they share no characters.

A subsequence deletes zero or more characters without reordering the rest (`"ace"` is a
subsequence of `"abcde"`). A common subsequence is a subsequence of both strings.""",
    example_notes=[
        "`\"ace\"` appears in both.",
        "Identical strings: the whole string.",
    ],
    constraints=["1 ≤ len(text1), len(text2) ≤ 1000", "lowercase English letters only"],
    hints=[
        "Work with prefixes: let `dp[i][j]` be the LCS of the first `i` characters of `text1` and the first `j` of `text2`.",
        "Compare the last characters of those prefixes. If they are equal, they can be matched together. If not, at least one of them is not in the LCS.",
        "Equal: `dp[i][j] = dp[i-1][j-1] + 1`. Different: `dp[i][j] = max(dp[i-1][j], dp[i][j-1])`. Row 0 and column 0 are 0. Two rows (or one row plus a variable) are enough.",
    ],
    explanation=r"""## Intuition

Two sequences, and we want something optimal about how they line up: that's the
**string-pair** DP shape. The state is a pair of prefix lengths `(i, j)`, and the decision is
about the **last characters** `text1[i-1]` and `text2[j-1]`:

- If they are equal, matching them together is always safe: any common subsequence that
  doesn't use both can be modified to use them without getting shorter.
- If they differ, they can't both be the last character of the common subsequence, so drop
  one of them and take the better result.

## Approach

**State.** `dp[i][j]` = LCS length of `text1[:i]` and `text2[:j]`.

**Recurrence.**

```text
dp[i][j] = dp[i-1][j-1] + 1                   if text1[i-1] == text2[j-1]
         = max(dp[i-1][j], dp[i][j-1])        otherwise
```

**Base cases.** `dp[0][j] = dp[i][0] = 0`: an empty prefix shares nothing.

**Table for `"abcde"` vs `"ace"`:**

| | "" | a | c | e |
|---|---|---|---|---|
| "" | 0 | 0 | 0 | 0 |
| a | 0 | 1 | 1 | 1 |
| b | 0 | 1 | 1 | 1 |
| c | 0 | 1 | 2 | 2 |
| d | 0 | 1 | 2 | 2 |
| e | 0 | 1 | 2 | 3 |

Diagonal steps (`+1`) happen at the matching pairs `a/a`, `c/c`, `e/e`; everything else copies
the larger of up/left.

**Top-down.**

```python
from functools import lru_cache

def longest_common_subsequence(a, b):
    @lru_cache(maxsize=None)
    def lcs(i, j):
        if i == 0 or j == 0:
            return 0
        if a[i - 1] == b[j - 1]:
            return lcs(i - 1, j - 1) + 1
        return max(lcs(i - 1, j), lcs(i, j - 1))
    return lcs(len(a), len(b))
```

With 1000 × 1000 states that is a million cache entries and 2000-deep recursion; bottom-up is
far more practical.

**Bottom-up.** `(n+1) × (m+1)` table, filled row by row, left to right.

**Space-optimized.** Row `i` reads row `i-1` (up, diagonal) and row `i` (left). Keep `prev`
and `cur` rows and swap; or a single row plus a variable `diag` holding the old `dp[j-1]`
before it was overwritten. The reference solution uses two rows.

## Complexity

O(n · m) time, O(min(n, m)) space with rolling rows (put the shorter string on the columns).

## Common mistakes

- **Off-by-one between string index and table index.** Table index `i` means "first `i`
  characters", so the character is `text1[i-1]`.
- **Adding 1 in the mismatch case**, or taking `max` of all three including the diagonal
  `+1` without checking the match.
- **Single-row update losing the diagonal.** When overwriting `row[j]` in place you need the
  *old* `row[j-1]`, which you already overwrote: save it in a temporary first.

## Going further

- **Reconstruct the subsequence** by walking back from `dp[n][m]`: on a match move
  diagonally and emit the character, otherwise move toward the larger neighbour.
- **Shortest common supersequence** length is `n + m - LCS`.
- **Minimum deletions to make two strings equal** is `n + m - 2·LCS`.
- **Edit distance** (next problem) adds substitutions and costs to the same table.
- LCS of a permutation against another reduces to LIS, giving O(n log n).
""",
    solution=r"""def longest_common_subsequence(text1, text2):
    n, m = len(text1), len(text2)
    # prev[j] = LCS of text1[:i-1] and text2[:j]   (the row above)
    # cur[j]  = LCS of text1[:i]   and text2[:j]   (the row being filled)
    # Row 0 (empty prefix of text1) is all zeros.
    prev = [0] * (m + 1)
    for i in range(1, n + 1):
        cur = [0] * (m + 1)          # cur[0] = 0: empty prefix of text2
        for j in range(1, m + 1):
            if text1[i - 1] == text2[j - 1]:
                # Last characters match: pair them up, extend the LCS of both shorter prefixes.
                cur[j] = prev[j - 1] + 1
            else:
                # They can't both end the LCS: drop the last char of one string or the other.
                cur[j] = max(prev[j], cur[j - 1])
        prev = cur
    return prev[m]
""",
    refs={
        "c": r"""long long longest_common_subsequence(char* text1, char* text2) {
    int n = strlen(text1), m = strlen(text2);
    /* Single row + `diag` holding the old dp[i-1][j-1] before it is overwritten. */
    long long* row = calloc(m + 1, sizeof(long long));
    for (int i = 1; i <= n; i++) {
        long long diag = 0;                  /* dp[i-1][0] */
        for (int j = 1; j <= m; j++) {
            long long up = row[j];           /* dp[i-1][j] before overwrite */
            if (text1[i - 1] == text2[j - 1]) row[j] = diag + 1;
            else row[j] = up > row[j - 1] ? up : row[j - 1];
            diag = up;                       /* becomes dp[i-1][j-1] for the next j */
        }
    }
    long long ans = row[m];
    free(row);
    return ans;
}""",
        "cpp": r"""long long longestCommonSubsequence(string text1, string text2) {
    int n = text1.size(), m = text2.size();
    vector<long long> prev(m + 1, 0), cur(m + 1, 0);
    for (int i = 1; i <= n; ++i) {
        for (int j = 1; j <= m; ++j)
            cur[j] = text1[i - 1] == text2[j - 1] ? prev[j - 1] + 1 : max(prev[j], cur[j - 1]);
        swap(prev, cur);                      // O(1): swaps buffers, not contents
    }
    return prev[m];
}""",
        "rust": r"""pub fn longest_common_subsequence(text1: String, text2: String) -> i64 {
    let (a, b) = (text1.as_bytes(), text2.as_bytes());
    let m = b.len();
    let mut prev = vec![0i64; m + 1];
    let mut cur = vec![0i64; m + 1];
    for &ca in a {
        for j in 1..=m {
            cur[j] = if ca == b[j - 1] { prev[j - 1] + 1 } else { prev[j].max(cur[j - 1]) };
        }
        std::mem::swap(&mut prev, &mut cur);
    }
    prev[m]
}""",
    },
    tests=_lcs_tests(),
))

# ---------------------------------------------------------------------------
# 12. Edit distance
# ---------------------------------------------------------------------------
def _ed_tests():
    r = random.Random(1312)
    t = [["horse", "ros"], ["intention", "execution"], ["", ""], ["", "abc"], ["abc", ""],
         ["a", "a"], ["kitten", "sitting"], ["abc", "cba"], ["sunday", "saturday"], ["aaaa", "bbbb"]]
    t.append(["".join(r.choice("abc") for _ in range(250)), "".join(r.choice("abc") for _ in range(300))])
    t.append(["".join(r.choice("acgt") for _ in range(400)), "".join(r.choice("acgt") for _ in range(380))])
    return t


PROBLEMS.append(dict(
    id="edit-distance",
    title="Edit Distance",
    difficulty=3,
    tags=["dp", "string pair", "2-D", "levenshtein"],
    fn="min_edit_distance",
    params=[["word1", "str"], ["word2", "str"]],
    returns="int",
    statement=r"""Return the minimum number of operations to turn `word1` into `word2`, where
one operation is:

- **insert** a character,
- **delete** a character, or
- **replace** a character with another.

This is the Levenshtein distance.""",
    example_notes=[
        "`horse → rorse` (replace h) `→ rose` (delete r) `→ ros` (delete e).",
        "`intention → inention → enention → exention → exection → execution`.",
    ],
    constraints=["0 ≤ len(word1), len(word2) ≤ 500", "lowercase English letters"],
    hints=[
        "Use prefixes again: `dp[i][j]` = edits to turn `word1[:i]` into `word2[:j]`. What are `dp[i][0]` and `dp[0][j]`?",
        "If the last characters are equal, no edit is needed for them: `dp[i-1][j-1]`.",
        "Otherwise the last operation was a replace (`dp[i-1][j-1]`), a delete of `word1[i-1]` (`dp[i-1][j]`) or an insert of `word2[j-1]` (`dp[i][j-1]`), each plus 1. Take the minimum.",
    ],
    explanation=r"""## Intuition

As with LCS, focus on the **last characters** of the two prefixes. Consider an optimal edit
script from `word1[:i]` to `word2[:j]`. What happens to `word1[i-1]` and how is `word2[j-1]`
produced? Only four possibilities:

- the two last characters are equal and simply kept: cost of the shorter prefixes;
- `word1[i-1]` is **replaced** by `word2[j-1]`: 1 + cost of `(i-1, j-1)`;
- `word1[i-1]` is **deleted**: 1 + cost of `(i-1, j)`;
- `word2[j-1]` is **inserted** at the end: 1 + cost of `(i, j-1)`.

Each case leaves a smaller instance of the same problem: textbook optimal substructure.

## Approach

**State.** `dp[i][j]` = minimum edits to turn `word1[:i]` into `word2[:j]`.

**Recurrence.**

```text
dp[i][j] = dp[i-1][j-1]                                    if word1[i-1] == word2[j-1]
         = 1 + min(dp[i-1][j-1],   # replace
                   dp[i-1][j],     # delete word1[i-1]
                   dp[i][j-1])     # insert word2[j-1]       otherwise
```

**Base cases.** `dp[i][0] = i` (delete everything), `dp[0][j] = j` (insert everything).

**Table for `"horse"` → `"ros"`:**

| | "" | r | o | s |
|---|---|---|---|---|
| "" | 0 | 1 | 2 | 3 |
| h | 1 | 1 | 2 | 3 |
| o | 2 | 2 | 1 | 2 |
| r | 3 | 2 | 2 | 2 |
| s | 4 | 3 | 3 | 2 |
| e | 5 | 4 | 4 | 3 |

At `(o, o)` the characters match, so it copies the diagonal `1`. At the bottom-right,
`e ≠ s`, and the best neighbour is `dp[4][3] = 2` (delete `e`), giving 3.

**Top-down.**

```python
from functools import lru_cache

def min_edit_distance(a, b):
    @lru_cache(maxsize=None)
    def d(i, j):
        if i == 0:
            return j
        if j == 0:
            return i
        if a[i - 1] == b[j - 1]:
            return d(i - 1, j - 1)
        return 1 + min(d(i - 1, j - 1), d(i - 1, j), d(i, j - 1))
    return d(len(a), len(b))
```

**Bottom-up.** Fill the `(n+1) × (m+1)` table row by row after setting row 0 and column 0.

**Space-optimized.** Rows `i-1` and `i` only; the reference keeps `prev` and `cur`. Note
`cur[0] = i` must be set at the start of each row, which is the left-column base case.

## Complexity

O(n · m) time, O(m) space with two rows.

## Common mistakes

- **Base row/column of zeros** (copied from LCS). Here they are `0, 1, 2, …`: turning a
  prefix into the empty string costs its length.
- **Mixing up insert and delete directions.** It doesn't change the answer (both cost 1), but
  it matters as soon as costs differ or you reconstruct the script.
- **Always adding 1**, even on a match. On a match the best option is the free diagonal (it is
  provably never worse than the other options).
- **Empty strings.** Both empty → 0; the base cases handle it if the table has size
  `(n+1) × (m+1)`.

## Going further

- **Weighted edits** (different costs for insert/delete/replace) just change the `+1`s.
- **Damerau-Levenshtein** adds transposition of adjacent characters: one more case reading
  `dp[i-2][j-2]`.
- If you only need to know whether the distance is ≤ `k`, only cells with `|i - j| ≤ k` can
  matter, so a **diagonal band** gives O(n · k).
- Hirschberg's algorithm recovers the actual alignment in O(n · m) time and O(m) space.
""",
    solution=r"""def min_edit_distance(word1, word2):
    n, m = len(word1), len(word2)
    # prev[j] = edits to turn word1[:i-1] into word2[:j]. Row 0: build word2[:j] from
    # nothing with j inserts.
    prev = list(range(m + 1))
    for i in range(1, n + 1):
        # cur[0] = edits to turn word1[:i] into "" = i deletes.
        cur = [i] + [0] * m
        for j in range(1, m + 1):
            if word1[i - 1] == word2[j - 1]:
                # Same last character: keep it for free, solve the shorter prefixes.
                cur[j] = prev[j - 1]
            else:
                cur[j] = 1 + min(
                    prev[j - 1],   # replace word1[i-1] with word2[j-1]
                    prev[j],       # delete word1[i-1]
                    cur[j - 1],    # insert word2[j-1] at the end
                )
        prev = cur
    return prev[m]
""",
    refs={
        "c": r"""long long min_edit_distance(char* word1, char* word2) {
    int n = strlen(word1), m = strlen(word2);
    long long* prev = malloc(sizeof(long long) * (m + 1));
    long long* cur = malloc(sizeof(long long) * (m + 1));
    for (int j = 0; j <= m; j++) prev[j] = j;            /* "" -> word2[:j]: j inserts */
    for (int i = 1; i <= n; i++) {
        cur[0] = i;                                      /* word1[:i] -> "": i deletes */
        for (int j = 1; j <= m; j++) {
            if (word1[i - 1] == word2[j - 1]) { cur[j] = prev[j - 1]; continue; }
            long long best = prev[j - 1];                /* replace */
            if (prev[j] < best) best = prev[j];          /* delete  */
            if (cur[j - 1] < best) best = cur[j - 1];    /* insert  */
            cur[j] = best + 1;
        }
        long long* t = prev; prev = cur; cur = t;        /* swap row buffers */
    }
    long long ans = prev[m];
    free(prev); free(cur);
    return ans;
}""",
        "cpp": r"""long long minEditDistance(string word1, string word2) {
    int n = word1.size(), m = word2.size();
    vector<long long> prev(m + 1), cur(m + 1);
    iota(prev.begin(), prev.end(), 0);                   // 0, 1, 2, ..., m
    for (int i = 1; i <= n; ++i) {
        cur[0] = i;
        for (int j = 1; j <= m; ++j)
            cur[j] = word1[i - 1] == word2[j - 1]
                       ? prev[j - 1]
                       : 1 + min({prev[j - 1], prev[j], cur[j - 1]});
        swap(prev, cur);
    }
    return prev[m];
}""",
        "rust": r"""pub fn min_edit_distance(word1: String, word2: String) -> i64 {
    let (a, b) = (word1.as_bytes(), word2.as_bytes());
    let m = b.len();
    let mut prev: Vec<i64> = (0..=m as i64).collect();
    let mut cur = vec![0i64; m + 1];
    for (i, &ca) in a.iter().enumerate() {
        cur[0] = i as i64 + 1;
        for j in 1..=m {
            cur[j] = if ca == b[j - 1] {
                prev[j - 1]
            } else {
                1 + prev[j - 1].min(prev[j]).min(cur[j - 1])
            };
        }
        std::mem::swap(&mut prev, &mut cur);
    }
    prev[m]
}""",
    },
    tests=_ed_tests(),
))

# ---------------------------------------------------------------------------
# 13. Word break
# ---------------------------------------------------------------------------
def _wb_tests():
    r = random.Random(1313)
    t = [["leetcode", ["leet", "code"]], ["applepenapple", ["apple", "pen"]],
         ["catsandog", ["cats", "dog", "sand", "and", "cat"]], ["a", ["a"]], ["a", ["b"]],
         ["aaaaaaa", ["aaaa", "aaa"]], ["cars", ["car", "ca", "rs"]], ["bb", ["a", "b", "bbb", "bbbb"]],
         ["a" * 60 + "b", ["a", "aa", "aaa", "aaaa", "aaaaa"]], ["goalspecial", ["go", "goal", "goals", "special"]]]
    words = ["".join(r.choice("ab") for _ in range(r.randint(1, 5))) for _ in range(12)]
    s = "".join(r.choice(words) for _ in range(40))
    t.append([s, words])
    t.append([s + "c", words])
    t.append(["a" * 299 + "b", ["a" * k for k in range(1, 21)]])
    return t


PROBLEMS.append(dict(
    id="word-break",
    title="Word Break",
    difficulty=2,
    tags=["dp", "1-D", "strings", "hash set"],
    fn="word_break",
    params=[["s", "str"], ["words", "str[]"]],
    returns="bool",
    statement=r"""Given a string `s` and a dictionary `words`, return `true` if `s` can be split
into a sequence of one or more dictionary words (concatenated with no separators), and
`false` otherwise.

Each dictionary word may be used any number of times.""",
    example_notes=[
        "`\"leet\" + \"code\"`.",
        "`\"apple\" + \"pen\" + \"apple\"`: `\"apple\"` is reused.",
    ],
    constraints=["1 ≤ len(s) ≤ 300", "1 ≤ len(words) ≤ 1000", "1 ≤ len(words[i]) ≤ 20",
                 "lowercase English letters; words are distinct"],
    hints=[
        "Plain backtracking (try every word as the next piece) explodes on inputs like `\"aaaa…ab\"`. What is it recomputing?",
        "Whether the *suffix* (or prefix) starting at some index can be segmented doesn't depend on how you got there. One boolean per index.",
        "`dp[i]` = the prefix `s[:i]` can be segmented. `dp[0] = true`; `dp[i]` is true if some `j < i` has `dp[j]` true and `s[j:i]` in the dictionary (only `j ≥ i - 20` matter).",
    ],
    explanation=r"""## Intuition

A segmentation is a sequence of cut positions. Backtracking tries every first word, then
every second word, and so on, which is exponential on `"aaaa…ab"`: every split of the `a`s
is explored before discovering the `b` can't be covered. But the question "can `s[j:]` be
segmented?" has the same answer no matter which cuts produced `j`. That's overlapping
subproblems with a tiny state: **one index**.

## Approach

**State.** `dp[i]` = `True` if the prefix `s[:i]` can be split into dictionary words.

**Recurrence.** Look at the **last word** of the split. It is `s[j:i]` for some `j < i`, and
everything before it must be splittable:

```text
dp[i] = any(dp[j] and s[j:i] in words for j in range(i))
```

Since words are at most 20 characters, only `j ≥ i - 20` can work.

**Base case.** `dp[0] = True`: the empty prefix is trivially split (zero words).

**Answer.** `dp[len(s)]`.

**Table for `s = "applepenapple"`, `words = ["apple", "pen"]`:**

| i | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| prefix end | | a | p | p | l | e | p | e | n | a | p | p | l | e |
| dp | T | F | F | F | F | T | F | F | T | F | F | F | F | T |

`dp[5]` via `"apple"` from `dp[0]`; `dp[8]` via `"pen"` from `dp[5]`; `dp[13]` via `"apple"`
from `dp[8]`.

**Top-down.** Memoize on the start index of the remaining suffix:

```python
from functools import lru_cache

def word_break(s, words):
    dictionary = set(words)
    @lru_cache(maxsize=None)
    def can(start):                    # can s[start:] be segmented?
        if start == len(s):
            return True
        for end in range(start + 1, min(len(s), start + 20) + 1):
            if s[start:end] in dictionary and can(end):
                return True
        return False
    return can(0)
```

The memo is what turns the exponential backtracking into O(n · L) calls. Note the early
`return True`: the top-down form naturally stops at the first success.

**Bottom-up.** Fill `dp[1..n]` left to right as in the recurrence (reference solution).

**Space.** Any earlier `dp[j]` within 20 positions may be read, so a ring buffer of 21
booleans would work, but O(n) booleans is already tiny.

## Complexity

O(n · L) substring checks, where `L ≤ 20` is the longest word; each check hashes a substring
of length ≤ L, so O(n · L²) character work. O(n + total dictionary size) space.

## Common mistakes

- **Greedy longest match.** `"goalspecial"` with `["go", "goal", "goals", "special"]`: taking
  `"goals"` first leaves `"pecial"`, a dead end. The DP considers all cut points.
- **Searching the list instead of a set.** `s[j:i] in words` on a Python *list* is O(len(words))
  per check.
- **`dp[0] = False`.** Then nothing is ever reachable.
- **Off-by-one in slices.** `s[j:i]` is characters `j … i-1`, which is exactly the word that
  ends right before prefix length `i`.

## Going further

- **Return all segmentations** (Word Break II): memoize the *list* of sentences for each
  start index. The output itself can be exponential, so prune with this boolean DP first.
- A **trie** of the dictionary lets you walk forward from `j` and discover every matching word
  in one pass, without hashing substrings.
- This is reachability on a DAG whose nodes are positions `0..n` and whose edges are
  dictionary words: BFS from 0 works too.
""",
    solution=r"""def word_break(s, words):
    dictionary = set(words)                      # O(1) average membership checks
    longest = max(len(w) for w in words)         # no word is longer, so no cut is further back
    n = len(s)
    # dp[i] = True if the prefix s[:i] can be split into dictionary words.
    dp = [False] * (n + 1)
    dp[0] = True                                 # the empty prefix: zero words
    for i in range(1, n + 1):
        # Try every possible last word s[j:i] (only lengths up to `longest` can match).
        for j in range(max(0, i - longest), i):
            if dp[j] and s[j:i] in dictionary:
                dp[i] = True
                break                            # one valid split is enough
    return dp[n]
""",
    refs={
        "cpp": r"""bool wordBreak(string s, vector<string>& words) {
    unordered_set<string> dict(words.begin(), words.end());
    size_t longest = 0;
    for (auto& w : words) longest = max(longest, w.size());
    int n = s.size();
    vector<char> dp(n + 1, 0);          // vector<char>, not vector<bool>: plain bytes
    dp[0] = 1;
    for (int i = 1; i <= n; ++i)
        for (int j = max(0, i - (int)longest); j < i && !dp[i]; ++j)
            if (dp[j] && dict.count(s.substr(j, i - j))) dp[i] = 1;
    return dp[n];
}""",
        "rust": r"""use std::collections::HashSet;

pub fn word_break(s: String, words: Vec<String>) -> bool {
    let dict: HashSet<&str> = words.iter().map(|w| w.as_str()).collect();
    let longest = words.iter().map(|w| w.len()).max().unwrap_or(0);
    let n = s.len();
    let mut dp = vec![false; n + 1];
    dp[0] = true;
    for i in 1..=n {
        // ASCII input, so byte slicing &s[j..i] is always on a char boundary.
        dp[i] = (i.saturating_sub(longest)..i).any(|j| dp[j] && dict.contains(&s[j..i]));
    }
    dp[n]
}""",
    },
    tests=_wb_tests(),
))

# ---------------------------------------------------------------------------
# 14. Partition equal subset sum
# ---------------------------------------------------------------------------
def _part_tests():
    r = random.Random(1314)
    t = [[[1, 5, 11, 5]], [[1, 2, 3, 5]], [[1]], [[2, 2]], [[1, 2, 5]], [[3, 3, 3, 4, 5]],
         [[1, 1]], [[100, 100, 100, 100, 100, 100, 100, 100]], [[2, 2, 3, 5]], [[23, 13, 11, 7, 6, 5, 5]]]
    a = [r.randint(1, 100) for _ in range(200)]
    if sum(a) % 2:
        a[0] += 1
    t.append([a])
    b = [r.choice([2, 4, 6, 98]) for _ in range(150)] + [1, 1]
    t.append([b])
    t.append([[2 * r.randint(1, 50) for _ in range(30)] + [1, 3]])
    t.append([[97, 89, 83, 79, 73, 71, 67, 61, 59, 53, 47, 43, 41, 37, 31, 29, 23, 19, 17, 13, 11, 7, 5, 3, 2]])
    return t


PROBLEMS.append(dict(
    id="partition-equal-subset-sum",
    title="Partition Equal Subset Sum",
    difficulty=2,
    tags=["dp", "0/1 knapsack", "subset sum"],
    fn="can_partition",
    params=[["nums", "int[]"]],
    returns="bool",
    statement=r"""Return `true` if the multiset `nums` can be split into two groups with **equal
sums** (every element goes into exactly one group), and `false` otherwise.""",
    example_notes=[
        "`[1, 5, 5]` and `[11]` both sum to 11.",
        "The total is 11, which is odd, so no equal split exists.",
    ],
    constraints=["1 ≤ len(nums) ≤ 200", "1 ≤ nums[i] ≤ 100"],
    hints=[
        "If the total is odd, the answer is immediately false. Otherwise, what sum must one of the groups have?",
        "The question becomes: is there a subset summing to `total / 2`? That's subset sum, a 0/1 knapsack where each number is used at most once.",
        "`can[s]` = some subset of the numbers seen so far sums to `s`. For each number `x`, for `s` from `target` *down* to `x`: `can[s] |= can[s - x]`.",
    ],
    explanation=r"""## Intuition

Two groups with equal sums means each group sums to `total / 2`. Pick one group: the other is
whatever is left. So the problem is exactly **subset sum**: does some subset hit `target =
total / 2`? Brute force tries 2ⁿ subsets, but the *sum so far* is small (at most 10 000 here),
so many subsets collide on the same sum. The state is "which sums are reachable", and each
number is a take-it-or-leave-it choice: the **0/1 knapsack** shape.

## Approach

**State.** `can[i][s]` = some subset of the first `i` numbers sums to exactly `s`.

**Recurrence.** Number `x = nums[i-1]` is either left out or used once:

```text
can[i][s] = can[i-1][s]  or  (s ≥ x and can[i-1][s - x])
```

**Base cases.** `can[0][0] = True` (empty subset), `can[0][s > 0] = False`.

**Answer.** `can[n][target]` (and `False` immediately if `total` is odd).

**Table for `[1, 5, 11, 5]`, target 11** (each row is the reachable set after that number;
`·` = unreachable):

| sum | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| start | T | · | · | · | · | · | · | · | · | · | · | · |
| after 1 | T | T | · | · | · | · | · | · | · | · | · | · |
| after 5 | T | T | · | · | · | T | T | · | · | · | · | · |
| after 11 | T | T | · | · | · | T | T | · | · | · | · | T |
| after 5 | T | T | · | · | · | T | T | · | · | · | T | T |

11 becomes reachable as soon as the `11` itself is processed.

**Top-down.**

```python
from functools import lru_cache

def can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False
    @lru_cache(maxsize=None)
    def can(i, s):                  # subset of nums[i:] summing to s?
        if s == 0:
            return True
        if i == len(nums) or s < 0:
            return False
        return can(i + 1, s - nums[i]) or can(i + 1, s)
    return can(0, total // 2)
```

**Bottom-up 2-D.** `(n+1) × (target+1)` booleans, row by row.

**Space-optimized 1-D.** Row `i` reads row `i-1` at `s` and at `s - x`, i.e. at a *smaller*
index. If we update a single array from **high `s` to low `s`**, `can[s - x]` has not been
touched yet in this round, so it still holds the previous row's value: each number is used at
most once. (Going upward would let `x` be reused, turning this into unbounded knapsack.) That
is the reference solution.

## Complexity

O(n · target) time = at most 200 × 10 000 = 2 · 10⁶ steps. O(target) space.

## Common mistakes

- **Iterating sums upward** in the 1-D version: `[3]` with target 6 would then "reach" 6 by
  using the 3 twice.
- **Forgetting the odd-total check**, then asking for `total // 2` which rounds down.
- **Greedy** (sort descending, put each number in the lighter bin) fails on `[3, 3, 2, 2, 2]`:
  it gives `{3, 2, 2}` vs `{3, 2}`, while `{3, 3}` vs `{2, 2, 2}` is equal.

## Going further

- **Bitset trick.** Represent the reachable set as one big integer: `bits |= bits << x` for
  each `x`, then test bit `target`. In Python this is a one-liner and very fast, because the
  shift-or runs over machine words: O(n · target / 64).
- **Partition into k equal subsets** needs a different state (bitmask of used numbers) and is
  NP-hard in general.
- **Minimum difference partition**: compute the same reachable set, then take the reachable
  `s ≤ total/2` closest to `total/2`.
""",
    solution=r"""def can_partition(nums):
    total = sum(nums)
    # Two equal halves need an even total.
    if total % 2 == 1:
        return False
    target = total // 2
    # can[s] = True if some subset of the numbers processed so far sums to exactly s.
    can = [False] * (target + 1)
    can[0] = True                       # the empty subset
    for x in nums:
        # Go DOWNWARD so can[s - x] still reflects the subsets *without* x:
        # each number is used at most once (0/1 knapsack).
        for s in range(target, x - 1, -1):
            if can[s - x]:
                can[s] = True
        if can[target]:
            return True                 # early exit: one half found
    return can[target]
""",
    refs={
        "cpp": r"""bool canPartition(vector<long long>& nums) {
    long long total = accumulate(nums.begin(), nums.end(), 0LL);
    if (total % 2) return false;
    int target = total / 2;
    // bitset: bit s set <=> some subset sums to s. Shifting left by x adds x to every
    // reachable sum at once; OR keeps the old sums (subsets without x).
    bitset<10001> bits;
    bits[0] = 1;
    for (long long x : nums) bits |= bits << x;
    return bits[target];
}""",
        "rust": r"""pub fn can_partition(nums: Vec<i64>) -> bool {
    let total: i64 = nums.iter().sum();
    if total % 2 == 1 {
        return false;
    }
    let target = (total / 2) as usize;
    let mut can = vec![false; target + 1];
    can[0] = true;
    for &x in &nums {
        let x = x as usize;
        // Downward so each number is used at most once.
        for s in (x..=target).rev() {
            if can[s - x] {
                can[s] = true;
            }
        }
    }
    can[target]
}""",
    },
    espresso=False,
    tests=_part_tests(),
))

# ---------------------------------------------------------------------------
# 15. 0/1 knapsack
# ---------------------------------------------------------------------------
def _knap_tests():
    r = random.Random(1315)
    t = [[[1, 3, 4, 5], [1, 4, 5, 7], 7], [[10, 20, 30], [60, 100, 120], 50], [[5], [10], 4],
         [[5], [10], 5], [[1, 2, 3], [10, 15, 40], 0], [[1, 1, 1], [5, 6, 7], 10],
         [[4, 5, 1], [1, 2, 3], 4], [[3, 4, 5, 9, 4], [3, 4, 4, 10, 4], 11], [[2, 2, 2], [0, 0, 0], 6]]
    n = 60
    t.append([[r.randint(1, 300) for _ in range(n)], [r.randint(0, 1000) for _ in range(n)], 4000])
    n = 100
    t.append([[r.randint(10, 100) for _ in range(n)], [r.randint(1, 100) for _ in range(n)], 1000])
    return t


PROBLEMS.append(dict(
    id="zero-one-knapsack",
    title="0/1 Knapsack",
    difficulty=2,
    tags=["dp", "0/1 knapsack", "2-D"],
    fn="knapsack",
    params=[["weights", "int[]"], ["values", "int[]"], ["capacity", "int"]],
    returns="int",
    statement=r"""There are `n` items; item `i` weighs `weights[i]` and is worth `values[i]`.
Choose a subset whose total weight is **at most** `capacity` and whose total value is as
large as possible. Each item can be taken at most once and cannot be split.

Return that maximum value.""",
    example_notes=[
        "Take the items of weight 3 and 4: weight 7, value `4 + 5 = 9`.",
        "Take the 20 kg and 30 kg items for 220. Greedy by value per kg would take the 10 kg item first and end at 160.",
    ],
    constraints=["1 ≤ n ≤ 100", "1 ≤ weights[i] ≤ 1000", "0 ≤ values[i] ≤ 1000", "0 ≤ capacity ≤ 10⁴"],
    hints=[
        "Decide the items one at a time. After deciding the first `i` items, what is the only thing about the past that matters for the future?",
        "Only the weight used so far (equivalently, the capacity left). State: `best[i][c]` = best value from the first `i` items with capacity `c`.",
        "`best[i][c] = max(best[i-1][c], best[i-1][c - w] + v)` when `w ≤ c`. In 1-D, loop `c` from `capacity` *down* to `w`.",
    ],
    explanation=r"""## Intuition

Brute force considers all 2ⁿ subsets. But two different partial selections that use the same
total weight are interchangeable for the future: only the **remaining capacity** constrains
what can still be added. So the state is `(items decided so far, capacity)`, and there are
only `n × (capacity + 1)` of them. Each item is a binary choice: take or skip.

Greedy by value density fails because items are indivisible (see example 2). Greedy is
optimal only for the *fractional* knapsack.

## Approach

**State.** `best[i][c]` = maximum value using only the first `i` items with total weight
≤ `c`.

**Recurrence.** Item `i-1` (weight `w`, value `v`) is skipped or taken:

```text
best[i][c] = max(best[i-1][c],                  # skip
                 best[i-1][c - w] + v)          # take (only if w ≤ c)
```

**Base cases.** `best[0][c] = 0` for all `c` (no items, no value).

**Answer.** `best[n][capacity]`.

**Table for weights `[1, 3, 4, 5]`, values `[1, 4, 5, 7]`, capacity 7:**

| items \ cap | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| none | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| +(w=1,v=1) | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| +(w=3,v=4) | 0 | 1 | 1 | 4 | 5 | 5 | 5 | 5 |
| +(w=4,v=5) | 0 | 1 | 1 | 4 | 5 | 6 | 6 | 9 |
| +(w=5,v=7) | 0 | 1 | 1 | 4 | 5 | 7 | 8 | 9 |

`best[3][7] = max(best[2][7], best[2][3] + 5) = max(5, 9) = 9`. The last item can't improve
capacity 7: `best[3][2] + 7 = 8 < 9`.

**Top-down.**

```python
from functools import lru_cache

def knapsack(weights, values, capacity):
    @lru_cache(maxsize=None)
    def best(i, c):                  # items i.. with capacity c
        if i == len(weights):
            return 0
        res = best(i + 1, c)                                  # skip
        if weights[i] <= c:
            res = max(res, best(i + 1, c - weights[i]) + values[i])  # take
        return res
    return best(0, capacity)
```

Top-down only visits *reachable* `(i, c)` pairs, which can be far fewer than the full table
when weights are large.

**Bottom-up.** Fill the `(n+1) × (capacity+1)` table row by row.

**Space-optimized.** Row `i` reads row `i-1` at `c` and at `c - w` (smaller). Iterate `c`
**downward** in one array so `dp[c - w]` is still the previous row's value: the reference
solution.

## Complexity

O(n · capacity) time (10⁶ here), O(capacity) space for the 1-D version. This is
*pseudo-polynomial*: polynomial in the numeric value of `capacity`, exponential in its number
of bits. 0/1 knapsack is NP-hard; the DP is fast only because capacities are small.

## Common mistakes

- **Iterating capacity upward** in 1-D: items get reused (that's unbounded knapsack).
- **Defining the state as "exactly weight `c`"** but initialising everything to 0: that
  silently means "at most `c`". Both definitions work, but the initialisation must match
  (exactly-`c` needs `-∞` everywhere except `dp[0] = 0`, and the answer is `max(dp)`).
- **Capacity 0.** Answer 0, no special case needed.

## Going further

- **Recover the chosen items** from the 2-D table: walk back from `(n, capacity)`; if
  `best[i][c] != best[i-1][c]`, item `i-1` was taken.
- **Large capacities, small values:** swap the roles. `minWeight[v]` = lightest subset with
  value exactly `v`; answer = largest `v` with `minWeight[v] ≤ capacity`.
- **Bounded knapsack** (item `i` available `k_i` times): binary-split each item into copies
  of size 1, 2, 4, … and run 0/1.
""",
    solution=r"""def knapsack(weights, values, capacity):
    # dp[c] = best value achievable with total weight <= c using the items seen so far.
    # With no items, every capacity is worth 0.
    dp = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        # DOWNWARD: dp[c - w] has not been updated for this item yet, so it describes
        # subsets WITHOUT this item. Each item is taken at most once.
        for c in range(capacity, w - 1, -1):
            take = dp[c - w] + v         # put this item in, fill the rest optimally
            if take > dp[c]:             # otherwise skipping it is at least as good
                dp[c] = take
    return dp[capacity]
""",
    refs={
        "cpp": r"""long long knapsack(vector<long long>& weights, vector<long long>& values, long long capacity) {
    vector<long long> dp(capacity + 1, 0);
    for (size_t i = 0; i < weights.size(); ++i) {
        long long w = weights[i], v = values[i];
        for (long long c = capacity; c >= w; --c)       // downward: 0/1
            dp[c] = max(dp[c], dp[c - w] + v);
    }
    return dp[capacity];
}""",
        "rust": r"""pub fn knapsack(weights: Vec<i64>, values: Vec<i64>, capacity: i64) -> i64 {
    let cap = capacity as usize;
    // Full 2-D table: best[i][c] with the first i items.
    let n = weights.len();
    let mut best = vec![vec![0i64; cap + 1]; n + 1];
    for i in 1..=n {
        let (w, v) = (weights[i - 1] as usize, values[i - 1]);
        for c in 0..=cap {
            best[i][c] = best[i - 1][c];                       // skip item i-1
            if w <= c {
                best[i][c] = best[i][c].max(best[i - 1][c - w] + v);   // take it
            }
        }
    }
    best[n][cap]
}""",
    },
    espresso=False,
    tests=_knap_tests(),
))

# ---------------------------------------------------------------------------
# 16. Decode ways
# ---------------------------------------------------------------------------
def _dw_tests():
    r = random.Random(1316)
    t = [["12"], ["226"], ["06"], ["0"], ["10"], ["11106"], ["100"], ["2101"], ["27"], ["1"],
         ["1" * 70], ["301"], ["1201234"]]
    t.append(["".join(r.choice("1234567891") for _ in range(60))])
    t.append(["".join(r.choice("12") for _ in range(50)) + "0" + "".join(r.choice("12") for _ in range(20))])
    return t


PROBLEMS.append(dict(
    id="decode-ways",
    title="Decode Ways",
    difficulty=2,
    tags=["dp", "1-D", "strings"],
    fn="num_decodings",
    params=[["s", "str"]],
    returns="int",
    statement=r"""A message of letters was encoded with `A → "1"`, `B → "2"`, …, `Z → "26"` and
the codes were concatenated. Given the digit string `s`, return the number of ways to decode
it back into letters.

A code never has a leading zero: `"06"` is not a valid code for `F`. If `s` cannot be
decoded at all, return `0`.""",
    example_notes=[
        "`\"AB\"` (1 2) or `\"L\"` (12).",
        "`\"BZ\"` (2 26), `\"VF\"` (22 6), `\"BBF\"` (2 2 6).",
    ],
    constraints=["1 ≤ len(s) ≤ 100", "`s` contains only digits", "the answer is below 2⁵³"],
    hints=[
        "Look at the end of the prefix `s[:i]`: the last letter came from either the last digit alone or the last two digits.",
        "One digit is valid if it isn't `'0'`. Two digits are valid if they form a number from 10 to 26.",
        "`dp[i] = (s[i-1] != '0' ? dp[i-1] : 0) + (10 ≤ int(s[i-2:i]) ≤ 26 ? dp[i-2] : 0)`, with `dp[0] = 1`. Only two previous values are needed.",
    ],
    explanation=r"""## Intuition

This is Climbing Stairs with **conditions on each step**: the last letter of a decoding
consumes either one digit or two. Splitting by the last letter partitions the decodings into
two disjoint groups, so their counts add, but each group exists only if that last piece is a
valid code. Zeros are what make the problem interesting: a `'0'` can never stand alone, so it
*must* be glued to a preceding `1` or `2`.

## Approach

**State.** `dp[i]` = number of ways to decode the prefix `s[:i]`.

**Recurrence.**

```text
dp[i] = (dp[i-1]  if s[i-1] != '0')                       one-digit code
      + (dp[i-2]  if i ≥ 2 and "10" ≤ s[i-2:i] ≤ "26")    two-digit code
```

**Base case.** `dp[0] = 1`: the empty prefix has exactly one decoding (the empty message). It
makes the formula work for `i = 1` and `i = 2` without special cases.

**Answer.** `dp[n]`.

**Tables.** `"226"`:

| i | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| char | | 2 | 2 | 6 |
| dp | 1 | 1 | 2 | 3 |

`"11106"`:

| i | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| char | | 1 | 1 | 1 | 0 | 6 |
| dp | 1 | 1 | 2 | 3 | 2 | 2 |

At `i = 4` the `'0'` can't stand alone, so only the pair `"10"` counts: `dp[4] = dp[2] = 2`.
At `i = 5`, `"6"` alone gives `dp[4] = 2`, and `"06"` is not a valid pair, so `dp[5] = 2`.

**Top-down.**

```python
from functools import lru_cache

def num_decodings(s):
    @lru_cache(maxsize=None)
    def ways(i):                 # decodings of s[i:]
        if i == len(s):
            return 1
        if s[i] == '0':
            return 0             # no code starts with 0
        res = ways(i + 1)
        if i + 1 < len(s) and int(s[i:i + 2]) <= 26:
            res += ways(i + 2)
        return res
    return ways(0)
```

This version reads left to right (suffixes) and puts the zero check at the *start* of a code,
which some people find more natural. Both are correct.

**Bottom-up.** `dp` array of length `n + 1`.

**Space-optimized.** Two variables, as in Climbing Stairs: the reference solution.

## Complexity

O(n) time, O(1) space.

## Common mistakes

- **Treating `"0"` as a letter.** `"0"` → 0 ways, `"100"` → 0 ways (the second zero has
  nothing to attach to).
- **Accepting `"06"` as a two-digit code.** A two-digit code must be between 10 and 26.
  Checking only `≤ 26` lets `"06"` through.
- **Early return on the first zero.** A zero kills only the one-digit option at that
  position; `"10"` is fine.
- **Overflow** for long strings of `1`s and `2`s: the count grows like Fibonacci.

## Going further

- **Decode Ways II** adds a `'*'` wildcard for digits 1–9: same DP, but each case
  contributes a *multiplier* (e.g. `"*"` alone has 9 options, `"1*"` has 9 two-digit options).
  Take results modulo 10⁹ + 7.
- The structure is a tiny automaton; problems like "count strings of length n avoiding a
  pattern" use the same DP-over-positions idea with a state per automaton node.
""",
    solution=r"""def num_decodings(s):
    n = len(s)
    # prev2 = dp[i-2], prev1 = dp[i-1], where dp[i] = ways to decode the prefix s[:i].
    # dp[0] = 1 (the empty message). We also use dp[-1] = 0 so i = 1 needs no special case.
    prev2, prev1 = 0, 1
    for i in range(1, n + 1):
        cur = 0
        # Last letter uses one digit: allowed unless that digit is '0'.
        if s[i - 1] != '0':
            cur += prev1
        # Last letter uses two digits: must be "10".."26" (a leading '0' is not allowed).
        if i >= 2 and (s[i - 2] == '1' or (s[i - 2] == '2' and s[i - 1] <= '6')):
            cur += prev2
        prev2, prev1 = prev1, cur
    return prev1
""",
    refs={
        "c": r"""long long num_decodings(char* s) {
    int n = strlen(s);
    long long prev2 = 0, prev1 = 1;          /* dp[i-2], dp[i-1]; dp[0] = 1 */
    for (int i = 1; i <= n; i++) {
        long long cur = 0;
        if (s[i - 1] != '0') cur += prev1;   /* single digit 1..9 */
        if (i >= 2) {
            int two = (s[i - 2] - '0') * 10 + (s[i - 1] - '0');
            if (two >= 10 && two <= 26) cur += prev2;   /* two digits 10..26 */
        }
        prev2 = prev1;
        prev1 = cur;
    }
    return prev1;
}""",
        "cpp": r"""long long numDecodings(string s) {
    long long prev2 = 0, prev1 = 1;
    for (size_t i = 1; i <= s.size(); ++i) {
        long long cur = s[i - 1] != '0' ? prev1 : 0;
        if (i >= 2) {
            int two = (s[i - 2] - '0') * 10 + (s[i - 1] - '0');
            if (two >= 10 && two <= 26) cur += prev2;
        }
        prev2 = prev1;
        prev1 = cur;
    }
    return prev1;
}""",
        "rust": r"""pub fn num_decodings(s: String) -> i64 {
    let b = s.as_bytes();
    let (mut prev2, mut prev1) = (0i64, 1i64);
    for i in 1..=b.len() {
        let mut cur = if b[i - 1] != b'0' { prev1 } else { 0 };
        if i >= 2 {
            let two = (b[i - 2] - b'0') as i64 * 10 + (b[i - 1] - b'0') as i64;
            if (10..=26).contains(&two) {
                cur += prev2;
            }
        }
        prev2 = prev1;
        prev1 = cur;
    }
    prev1
}""",
    },
    tests=_dw_tests(),
))

# ---------------------------------------------------------------------------
# 17. Longest palindromic substring
# ---------------------------------------------------------------------------
def _lps_tests():
    r = random.Random(1317)
    t = [["babad"], ["cbbd"], ["a"], ["ac"], ["racecar"], ["abacdfgdcaba"], ["aaaa"],
         ["forgeeksskeegfor"], ["abcba_xyzzyx"], ["abcd"]]
    t.append(["".join(r.choice("ab") for _ in range(1000))])
    t.append(["".join(r.choice("abc") for _ in range(700))])
    t.append(["x" * 999])
    return t


PROBLEMS.append(dict(
    id="longest-palindromic-substring",
    title="Longest Palindromic Substring",
    difficulty=2,
    tags=["dp", "interval", "strings", "expand around center"],
    fn="longest_palindrome",
    params=[["s", "str"]],
    returns="str",
    statement=r"""Return the longest **contiguous substring** of `s` that reads the same forwards
and backwards.

If several palindromic substrings share the maximum length, return the **leftmost** one (the
one with the smallest starting index).""",
    example_notes=[
        "`\"bab\"` and `\"aba\"` both have length 3; `\"bab\"` starts first.",
        "`\"bb\"`.",
    ],
    constraints=["1 ≤ len(s) ≤ 1000", "`s` consists of printable ASCII characters"],
    hints=[
        "A substring `s[i..j]` is a palindrome iff its end characters match *and* the inside `s[i+1..j-1]` is a palindrome. That's an interval DP.",
        "Every palindrome has a center: a single character (odd length) or a gap between two characters (even length). Expanding outward from a center finds the longest palindrome around it.",
        "Try all `2n - 1` centers from left to right, and replace your best only when you find something *strictly* longer: that keeps the leftmost on ties.",
    ],
    explanation=r"""## Intuition

The palindrome property is defined from the outside in: `s[i..j]` is a palindrome when
`s[i] == s[j]` and `s[i+1..j-1]` is a palindrome. That is an **interval DP**: the state is a
pair of endpoints, and each interval depends on the interval strictly inside it. Read in the
other direction it suggests an even simpler algorithm: grow palindromes **outward from their
centers**.

## Approach

**State.** `pal[i][j]` = `s[i..j]` (inclusive) is a palindrome.

**Recurrence.**

```text
pal[i][j] = s[i] == s[j] and (j - i < 2 or pal[i+1][j-1])
```

**Base cases.** Length 1 is always a palindrome; length 2 needs `s[i] == s[i+1]` (both
covered by `j - i < 2`).

**Fill order.** `pal[i][j]` reads `pal[i+1][j-1]`, a *shorter* interval. So fill by
increasing length, or by `i` from `n-1` down to 0 with `j` increasing.

**Table for `"babad"`** (row `i`, column `j`, only `j ≥ i` is meaningful):

| i\j | 0:b | 1:a | 2:b | 3:a | 4:d |
|---|---|---|---|---|---|
| 0:b | T | F | T | F | F |
| 1:a | | T | F | T | F |
| 2:b | | | T | F | F |
| 3:a | | | | T | F |
| 4:d | | | | | T |

The longest `T` intervals are `[0,2]` = `"bab"` and `[1,3]` = `"aba"`; leftmost wins.

**Top-down.**

```python
from functools import lru_cache

def is_pal(s):
    @lru_cache(maxsize=None)
    def pal(i, j):
        if i >= j:
            return True
        return s[i] == s[j] and pal(i + 1, j - 1)
    return pal
```

then scan all `(i, j)` pairs. This works but is the least natural way to use the recurrence.

**Bottom-up.** Fill `pal` for `i` from `n-1` down to 0 and `j` from `i` up; track the best
interval. O(n²) time and O(n²) booleans (a million cells for n = 1000).

**Space-optimized: expand around center.** Each palindrome is determined by its center and
its radius, and the DP chain `pal[i][j] ← pal[i+1][j-1]` is exactly a walk *outward* from a
center. So for each of the `2n - 1` centers, expand while the ends match. Same O(n²) worst
case, O(1) extra space, and far faster in practice (most expansions stop immediately). That
is the reference solution.

**Leftmost on ties.** Two palindromes of equal length have their centers in the same order
as their starts, so scanning centers left to right and only updating on a *strictly* longer
palindrome returns the leftmost.

## Complexity

O(n²) time for both the table and the expansion (worst case `"aaaa…"`). O(n²) space for the
table, O(1) for expansion.

## Common mistakes

- **Forgetting even-length palindromes** (`"cbbd"` → `"bb"`): expand from gaps too.
- **Updating on `>=`**: returns the rightmost on ties.
- **Filling the table in the wrong order** (`i` increasing): `pal[i+1][j-1]` isn't computed
  yet.
- **Confusing with longest palindromic *subsequence***, which allows gaps and has the
  recurrence `dp[i][j] = dp[i+1][j-1] + 2` or `max(dp[i+1][j], dp[i][j-1])`.

## Going further

- **Manacher's algorithm** finds the longest palindrome around every center in O(n) total by
  reusing mirror information inside the rightmost palindrome found so far.
- **Count palindromic substrings**: same expansion, add one per successful step.
- **Palindrome partitioning** (minimum cuts) combines this `pal` table with a 1-D DP over
  prefixes, like Word Break.
""",
    solution=r"""def longest_palindrome(s):
    n = len(s)
    best_start, best_len = 0, 1          # any single character is a palindrome

    def expand(lo, hi):
        # Grow the window while both ends match. The window [lo, hi] starts as a center:
        # a single char (lo == hi) for odd lengths or a pair (hi == lo + 1) for even ones.
        while lo >= 0 and hi < n and s[lo] == s[hi]:
            lo -= 1
            hi += 1
        # The loop overshot by one on each side; the palindrome is s[lo+1 .. hi-1].
        return lo + 1, hi - lo - 1

    for center in range(n):
        # Try the odd center at `center`, then the even center between center and center+1.
        # Centers are visited left to right and we only replace on STRICTLY longer, so on
        # ties the earliest-starting palindrome is kept.
        for lo, hi in ((center, center), (center, center + 1)):
            start, length = expand(lo, hi)
            if length > best_len:
                best_start, best_len = start, length
    return s[best_start:best_start + best_len]
""",
    refs={
        "cpp": r"""string longestPalindrome(string s) {
    int n = s.size(), bestStart = 0, bestLen = 1;
    auto expand = [&](int lo, int hi) {
        while (lo >= 0 && hi < n && s[lo] == s[hi]) { --lo; ++hi; }
        int len = hi - lo - 1;                   // overshoot by one on each side
        if (len > bestLen) { bestLen = len; bestStart = lo + 1; }   // strictly longer only
    };
    for (int c = 0; c < n; ++c) {
        expand(c, c);         // odd length
        expand(c, c + 1);     // even length
    }
    return s.substr(bestStart, bestLen);
}""",
        "rust": r"""pub fn longest_palindrome(s: String) -> String {
    // Bottom-up interval table: pal[i][j] for i from n-1 down to 0, j from i up.
    let b = s.as_bytes();
    let n = b.len();
    let mut pal = vec![vec![false; n]; n];
    let (mut best_start, mut best_len) = (0usize, 1usize);
    for i in (0..n).rev() {
        for j in i..n {
            pal[i][j] = b[i] == b[j] && (j - i < 2 || pal[i + 1][j - 1]);
            let len = j - i + 1;
            // Rows are visited right to left, so prefer a smaller start on equal length.
            if pal[i][j] && (len > best_len || (len == best_len && i < best_start)) {
                best_start = i;
                best_len = len;
            }
        }
    }
    s[best_start..best_start + best_len].to_string()
}""",
    },
    tests=_lps_tests(),
))

# ---------------------------------------------------------------------------
# 18. Maximal square
# ---------------------------------------------------------------------------
def _msq_tests():
    r = random.Random(1318)
    t = [[[[1, 0, 1, 0, 0], [1, 0, 1, 1, 1], [1, 1, 1, 1, 1], [1, 0, 0, 1, 0]]], [[[0, 1], [1, 0]]],
         [[[0]]], [[[1]]], [[[1, 1], [1, 1]]], [[[1, 1, 1, 1]]], [[[0, 0], [0, 0]]],
         [[[1, 1, 1], [1, 1, 1], [1, 1, 0]]], [[[1, 1, 0, 1], [1, 1, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]]]
    t.append([[[1 if r.random() < 0.8 else 0 for _ in range(10)] for _ in range(8)]])
    return t


PROBLEMS.append(dict(
    id="maximal-square",
    title="Maximal Square",
    difficulty=2,
    tags=["dp", "2-D grid"],
    fn="maximal_square",
    params=[["matrix", "int[][]"]],
    returns="int",
    statement=r"""`matrix` is a grid of `0`s and `1`s. Find the largest **square** sub-grid that
contains only `1`s and return its **area**.""",
    example_notes=[
        "A 2 × 2 block of ones sits in rows 1–2, columns 2–3 (also columns 3–4): area 4.",
        "Only single cells: area 1.",
    ],
    constraints=["1 ≤ rows, cols ≤ 300", "matrix[r][c] is 0 or 1"],
    hints=[
        "Instead of asking about squares anywhere, ask about squares with a fixed **bottom-right corner** `(r, c)`.",
        "If `(r, c)` is 1, the largest all-ones square ending there is limited by the squares ending at its top, left and top-left neighbours.",
        "`side[r][c] = 1 + min(side[r-1][c], side[r][c-1], side[r-1][c-1])` for a 1-cell, 0 otherwise. Return `max(side)²`.",
    ],
    explanation=r"""## Intuition

"Largest square anywhere" has too many candidates (position × size). Anchoring each
square at its **bottom-right corner** gives one subproblem per cell, and the neighbours
of that corner tell us everything: a `k × k` square of ones ending at `(r, c)` exists exactly
when `(r, c)` is 1 and `(k-1) × (k-1)` squares end at the top, left and top-left neighbours.
Those three squares overlap to cover the whole `k × k` block except the corner itself.

```text
 T T T .        T = square ending at (r-1, c)
 L D D T        L = square ending at (r, c-1)
 L D D T        D = square ending at (r-1, c-1)  (overlaps both)
 L L L X        X = (r, c)
```

The smallest of the three limits the side.

## Approach

**State.** `side[r][c]` = side of the largest all-ones square whose bottom-right corner is
`(r, c)`.

**Recurrence.**

```text
side[r][c] = 0                                                          if matrix[r][c] == 0
           = 1 + min(side[r-1][c], side[r][c-1], side[r-1][c-1])        otherwise
```

**Base cases.** On the first row or column a 1-cell has `side = 1` (no room for more).

**Answer.** `(max side)²`.

**Table for the first example:**

```text
matrix          side
1 0 1 0 0       1 0 1 0 0
1 0 1 1 1       1 0 1 1 1
1 1 1 1 1       1 1 1 2 2
1 0 0 1 0       1 0 0 1 0
```

| | c0 | c1 | c2 | c3 | c4 |
|---|---|---|---|---|---|
| r0 | 1 | 0 | 1 | 0 | 0 |
| r1 | 1 | 0 | 1 | 1 | 1 |
| r2 | 1 | 1 | 1 | 2 | 2 |
| r3 | 1 | 0 | 0 | 1 | 0 |

`side[2][3] = 1 + min(1, 1, 1) = 2`. The maximum side is 2, area 4.

**Top-down.** `side(r, c)` memoized, recursing to the three neighbours; you still need to take
the max over all cells, so you end up calling it everywhere anyway.

**Bottom-up.** Row-major fill of a `rows × cols` table.

**Space-optimized.** One row `row[c]` plus a variable for the old `row[c-1]` (the diagonal),
saved before it is overwritten: the reference solution. The ESPresso reference overwrites
the matrix in place instead: when `(r, c)` is reached, its own value is still the original
0/1 and the three neighbours already hold side lengths.

## Complexity

O(rows · cols) time, O(cols) extra space (O(1) in place).

## Common mistakes

- **Returning the side** instead of the area.
- **Using only two neighbours** (top and left): a ring of ones around a 0 at the top-left
  diagonal would wrongly extend the square.
- **Losing the diagonal** in the single-row version: `row[c-1]` has been overwritten for the
  current row, so stash the old value first.

## Going further

- **Count all square sub-matrices of ones**: the answer is `Σ side[r][c]`, since a cell with
  side `k` is the corner of exactly `k` squares (sizes 1…k).
- **Maximal rectangle** of ones is harder: treat each row as the base of a histogram of
  heights and run "largest rectangle in histogram" (monotonic stack) per row, O(rows · cols).
""",
    solution=r"""def maximal_square(matrix):
    rows, cols = len(matrix), len(matrix[0])
    # row[c] = side of the largest all-ones square with bottom-right corner (r, c),
    # for the current row r. Before row 0 it's all zeros (no squares above the grid).
    row = [0] * (cols + 1)               # 1-based columns: row[0] is a permanent 0 border
    best = 0
    for r in range(rows):
        diag = 0                         # old row[c-1], i.e. side at (r-1, c-1)
        for c in range(1, cols + 1):
            up = row[c]                  # side at (r-1, c), about to be overwritten
            if matrix[r][c - 1] == 1:
                # The three neighbouring squares together cover everything but the corner;
                # the smallest of them limits how far this square can grow.
                row[c] = 1 + min(up, row[c - 1], diag)
                best = max(best, row[c])
            else:
                row[c] = 0               # a zero corner ends every square
            diag = up
    return best * best                   # area, not side
""",
    refs={
        "cpp": r"""long long maximalSquare(vector<vector<long long>>& matrix) {
    int R = matrix.size(), C = matrix[0].size();
    vector<vector<int>> side(R + 1, vector<int>(C + 1, 0));   // 1-based with a zero border
    int best = 0;
    for (int r = 1; r <= R; ++r)
        for (int c = 1; c <= C; ++c)
            if (matrix[r - 1][c - 1] == 1) {
                side[r][c] = 1 + min({side[r - 1][c], side[r][c - 1], side[r - 1][c - 1]});
                best = max(best, side[r][c]);
            }
    return (long long)best * best;
}""",
        "rust": r"""pub fn maximal_square(matrix: Vec<Vec<i64>>) -> i64 {
    let cols = matrix[0].len();
    let mut row = vec![0i64; cols + 1];
    let mut best = 0i64;
    for line in &matrix {
        let mut diag = 0i64;
        for c in 1..=cols {
            let up = row[c];
            row[c] = if line[c - 1] == 1 { 1 + up.min(row[c - 1]).min(diag) } else { 0 };
            best = best.max(row[c]);
            diag = up;
        }
    }
    best * best
}""",
        "espresso": r"""fn maximalSquare(matrix) {
  // In place: matrix[r][c] becomes the side of the largest square ending at (r, c).
  var rows = len(matrix)
  var cols = len(matrix[0])
  var best = 0
  for var r in 0..rows {
    for var c in 0..cols {
      if matrix[r][c] == 1 and r > 0 and c > 0 {
        var m = matrix[r - 1][c]
        if matrix[r][c - 1] < m { m = matrix[r][c - 1] }
        if matrix[r - 1][c - 1] < m { m = matrix[r - 1][c - 1] }
        matrix[r][c] = m + 1
      }
      // edge cells and zeros keep their value (1 or 0)
      if matrix[r][c] > best { best = matrix[r][c] }
    }
  }
  return best * best
}""",
    },
    tests=_msq_tests(),
))

# @@MORE@@
