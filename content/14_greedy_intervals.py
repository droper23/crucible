"""Track 14: Greedy & Intervals."""
import random

TRACK = dict(
    id="greedy",
    title="Greedy & Intervals",
    order=14,
    icon="⇥",
    blurb="Make the locally best choice and prove it never hurts: exchange arguments, earliest-finish ordering and sweep lines.",
    intro=r"""A **greedy algorithm** builds a solution one irrevocable choice at a time, always
taking the option that looks best *right now*, and never revisits a decision. When it works
it is usually the simplest and fastest solution available: often one sort plus one linear
pass. The catch is that it *often doesn't work*, and the code looks just as plausible when
it's wrong. Greedy is a technique where the proof matters more than the code.

## Greedy vs dynamic programming

Dynamic programming considers *every* choice at each step and keeps the best result for each
subproblem. Greedy commits to *one* choice and solves a single remaining subproblem. So
greedy is valid exactly when you can show that some optimal solution makes the greedy choice
first (the **greedy-choice property**), and that what's left is a smaller instance of the same
problem (**optimal substructure**, which DP needs too).

Coin change shows the difference. With coins `[1, 5, 10, 25]`, "take the biggest coin that
fits" is optimal. With `[1, 3, 4]` and amount 6 it picks `4+1+1` while `3+3` is better.
Same code, different inputs, different correctness. Whenever you write a greedy, try to break
it on small inputs before trusting it.

## Proof technique 1: the exchange argument

Take any optimal solution `OPT` that disagrees with the greedy choice. Show you can **swap**
part of `OPT` for the greedy choice without making it worse. Repeat until `OPT` *is* the
greedy solution; since it never got worse, greedy is optimal.

Example: *schedule the most non-overlapping intervals.* Greedy: repeatedly take the interval
that **ends earliest**, discard everything overlapping it.

```text
greedy pick g:   [==g==]
OPT's first o:   [=====o=====]
rest of OPT:                     [===]  [====]
```

`g` ends no later than `o` (it ends earliest of all). Every other interval in `OPT` starts
after `o` ends, hence after `g` ends. So replacing `o` with `g` keeps `OPT` valid and the same
size. Now both agree on the first interval; recurse on what's left.

## Proof technique 2: greedy stays ahead

Define a measure of progress and show by induction that after each step, greedy is **at
least as far along** as any other solution. Then greedy can't finish behind.

Example: *Jump Game II, fewest jumps.* After `k` jumps, let `reach_k` be the furthest index
reachable. Greedy explores every index reachable with `k` jumps and computes the furthest
reachable with `k + 1`. No strategy using `k + 1` jumps can be further than that, so the
first `k` with `reach_k ≥ n - 1` is optimal.

## Sorting is half the algorithm

Most greedy algorithms start by sorting, and **which key** you sort by *is* the greedy
choice:

| goal | sort by | why |
|---|---|---|
| max non-overlapping intervals / min removals | **end** time | finishing early leaves the most room |
| merge overlapping intervals | **start** time | overlapping intervals become adjacent |
| assign smallest-sufficient resources | both sides ascending | don't waste big resources on small demands |
| minimise lateness (deadlines) | deadline | exchange argument on inversions |

Sorting by start time for interval scheduling is a classic wrong turn: one long interval that
starts first can block many short ones.

## Intervals: conventions first

Before coding any interval problem, pin down:

- **Closed or half-open?** Do `[1, 2]` and `[2, 3]` overlap? For merging, the problems here
  say yes (they touch). For meetings, `[1, 2)` and `[2, 3)` don't conflict.
- **Overlap test.** Two intervals `[a, b]` and `[c, d]` overlap iff `a ≤ d and c ≤ b`
  (closed) or `a < d and c < b` (half-open). After sorting by start you only compare the next
  start with the current end.

## Sweep line

Turn every interval into two **events**, `(start, +1)` and `(end, -1)`, sort the events by
position, and walk through them keeping a running count. The maximum running count is the
maximum number of simultaneously active intervals (e.g. meeting rooms needed).

```text
meetings: [0,30) [5,10) [15,20)
events:   0:+1  5:+1  10:-1  15:+1  20:-1  30:-1
active:     1     2      1      2      1      0     -> max 2 rooms
```

Ties matter: with half-open intervals, process `-1` before `+1` at the same position so a
meeting that ends at 10 frees its room for one starting at 10.

An equivalent formulation sorts starts and ends separately and walks two pointers; another
keeps a **min-heap of end times** for the rooms in use.

## Other greedy shapes in this track

- **Running balance / reset:** Gas Station drops every candidate start at which the tank goes
  negative, because nothing in between can work either.
- **Two passes:** Candy satisfies the left-neighbour constraints in one sweep and the
  right-neighbour ones in a second sweep, taking the max.
- **Counting the bottleneck:** Task Scheduler's answer is dictated by the most frequent task;
  the rest fill the gaps.
- **Last occurrence:** Partition Labels extends the current part until it reaches the last
  occurrence of every letter inside it.

## Complexity

Typical greedy solutions are O(n log n) for the sort plus O(n) for the pass, with O(1) or
O(n) extra space. When you find yourself needing to look ahead or undo choices, you're
probably in DP (or backtracking) territory instead.
""",
)

PROBLEMS = []


# ---------------------------------------------------------------------------
# 1. Jump game
# ---------------------------------------------------------------------------
def _jg_tests():
    r = random.Random(1401)
    t = [[[2, 3, 1, 1, 4]], [[3, 2, 1, 0, 4]], [[0]], [[1, 0]], [[0, 1]], [[2, 0, 0]],
         [[1, 1, 0, 1]], [[5, 0, 0, 0, 0, 0]], [[2, 5, 0, 0]], [[1, 2, 0, 1, 0, 2, 0]]]
    t.append([[r.randint(0, 4) if i % 3 else r.randint(2, 4) for i in range(40)]])
    a = [r.randint(1, 4) for _ in range(40)]
    a[20] = 0; a[19] = 1; a[18] = 2; a[17] = 3; a[16] = 1
    t.append([a])
    return t


PROBLEMS.append(dict(
    id="jump-game",
    title="Jump Game",
    difficulty=2,
    tags=["greedy", "array", "reachability"],
    fn="can_jump",
    params=[["nums", "int[]"]],
    returns="bool",
    statement=r"""You start at index `0` of `nums`. From index `i` you may jump forward by any
distance from `1` to `nums[i]` (a `0` means you're stuck there).

Return `true` if you can reach the **last index**.""",
    example_notes=[
        "Jump 1 step to index 1, then 3 steps to the end.",
        "Every route lands on index 3, whose value is 0, and nothing jumps over it.",
    ],
    constraints=["1 ≤ len(nums) ≤ 10⁴", "0 ≤ nums[i] ≤ 10⁵"],
    hints=[
        "You don't need to know *how* you reach an index, only *whether* you can.",
        "If you can reach index `i`, you can reach every index before it too. So the set of reachable indices is always a prefix `0 … furthest`.",
        "Scan left to right keeping `furthest = max(furthest, i + nums[i])`. If you ever stand at an `i > furthest`, you're stuck.",
    ],
    explanation=r"""## Intuition

A DP would ask, for every index, "can I get here?", looking back at all earlier indices:
O(n²). But reachability here has a special structure: if index `j` is reachable and you can
jump up to `nums[j]`, *every* index between `j` and `j + nums[j]` is reachable. So the
reachable set is always a contiguous **prefix** `[0, furthest]`, and one number describes it
completely. That's the greedy insight: instead of tracking every option, track only the best
frontier.

## Approach

Walk `i` from left to right while `i ≤ furthest`:

1. `i` is reachable (it's inside the prefix), so extend `furthest = max(furthest, i + nums[i])`.
2. If `furthest ≥ n - 1`, the last index is reachable: return `true`.

If the loop reaches an `i > furthest`, there is a gap nothing can cross: return `false`.

**Trace for `[3, 2, 1, 0, 4]`:**

| i | nums[i] | i + nums[i] | furthest |
|---|---|---|---|
| 0 | 3 | 3 | 3 |
| 1 | 2 | 3 | 3 |
| 2 | 1 | 3 | 3 |
| 3 | 0 | 3 | 3 |
| 4 | | | 4 > 3: stuck |

Every route funnels into index 3, and nothing jumps past it.

**Why it's correct (stays ahead).** By induction, after processing indices `0 … i`,
`furthest` equals the largest index reachable using jumps that start at `0 … i`. Any jump
sequence to the end starts each jump from a reachable index, so if the end is reachable at
all, the scan will see `furthest ≥ n-1` before running out.

**Alternative (backward greedy).** Walk from the end keeping `goal` = leftmost index known to
reach the end. If `i + nums[i] ≥ goal`, set `goal = i`. Answer: `goal == 0`.

## Complexity

O(n) time, one pass. O(1) space.

## Common mistakes

- **Always jumping the maximum distance.** `[2, 5, 0, 0]`: jumping 2 from index 0 lands on a
  0; jumping 1 reaches the 5 and the end. Greedy here is about the *frontier*, not about
  which jump to take.
- **Continuing past a gap.** Without the `i ≤ furthest` check, the loop happily "reaches"
  indices it can't actually stand on.
- **Single element.** `[0]` is already at the end: `true`.

## Going further

- **Fewest jumps**: Jump Game II (next problem) extends the frontier idea to BFS levels.
- **Jumps in both directions** (`i ± nums[i]`) break the prefix structure; use BFS/DFS on the
  implicit graph.
- The same "furthest reach" scan solves **minimum taps to water a garden** and **video
  stitching** after converting each item to an interval.
""",
    solution=r"""def can_jump(nums):
    n = len(nums)
    furthest = 0                      # every index in [0, furthest] is reachable
    for i in range(n):
        if i > furthest:
            # A gap: no reachable index can jump to i, so nothing beyond is reachable.
            return False
        # From i we can land anywhere up to i + nums[i]; the prefix only ever grows.
        furthest = max(furthest, i + nums[i])
        if furthest >= n - 1:
            return True
    return True
""",
    refs={
        "c": r"""bool can_jump(long long* nums, int numsSize) {
    long long furthest = 0;                     /* reachable prefix is [0, furthest] */
    for (int i = 0; i < numsSize; i++) {
        if (i > furthest) return false;         /* gap: index i can't be reached */
        if (i + nums[i] > furthest) furthest = i + nums[i];
        if (furthest >= numsSize - 1) return true;
    }
    return true;
}""",
        "cpp": r"""bool canJump(vector<long long>& nums) {
    // Backward greedy: goal = leftmost index known to reach the end.
    long long goal = nums.size() - 1;
    for (long long i = goal; i >= 0; --i)
        if (i + nums[i] >= goal) goal = i;      // i can jump to a winning index
    return goal == 0;
}""",
        "rust": r"""pub fn can_jump(nums: Vec<i64>) -> bool {
    let mut furthest = 0usize;
    for (i, &x) in nums.iter().enumerate() {
        if i > furthest {
            return false;
        }
        furthest = furthest.max(i + x as usize);
    }
    true
}""",
        "espresso": r"""fn canJump(nums) {
  var n = len(nums)
  var furthest = 0                 // reachable prefix is [0, furthest]
  for var i in 0..n {
    if i > furthest { return false }
    if i + nums[i] > furthest { furthest = i + nums[i] }
    if furthest >= n - 1 { return true }
  }
  return true
}""",
    },
    tests=_jg_tests(),
))


# ---------------------------------------------------------------------------
# 2. Jump game II
# ---------------------------------------------------------------------------
def _jg2_tests():
    r = random.Random(1402)
    t = [[[2, 3, 1, 1, 4]], [[2, 3, 0, 1, 4]], [[0]], [[1, 2]], [[1, 1, 1, 1, 1]], [[10, 1, 1, 1]],
         [[1, 2, 1, 1, 1]], [[2, 1]], [[3, 4, 3, 2, 5, 4, 3]], [[1, 2, 3]]]
    t.append([[r.randint(1, 5) for _ in range(50)]])
    t.append([[1] * 30])
    return t


PROBLEMS.append(dict(
    id="jump-game-min-jumps",
    title="Jump Game II (Fewest Jumps)",
    difficulty=2,
    tags=["greedy", "array", "bfs levels"],
    fn="min_jumps",
    params=[["nums", "int[]"]],
    returns="int",
    statement=r"""You start at index `0` of `nums`; from index `i` you may jump forward by any
distance from `1` to `nums[i]`. The last index is guaranteed to be reachable.

Return the **minimum number of jumps** to reach the last index.""",
    example_notes=[
        "Jump 1 step to index 1 (value 3), then 3 steps to the end.",
        "Same answer: index 1 still reaches the end.",
    ],
    constraints=["1 ≤ len(nums) ≤ 10⁴", "0 ≤ nums[i] ≤ 1000", "the last index is reachable"],
    hints=[
        "Group indices by how many jumps it takes to reach them. Which indices need 0 jumps? 1 jump?",
        "The indices reachable in exactly `k` jumps form a contiguous window, and the window for `k + 1` jumps ends at the furthest `i + nums[i]` over the current window.",
        "Scan once with `end` (edge of the current window) and `furthest`. When `i` reaches `end`, you must jump: `jumps += 1; end = furthest`.",
    ],
    explanation=r"""## Intuition

"Fewest steps" usually means BFS: level `k` is the set of positions reachable in exactly
`k` jumps. As in Jump Game, reachable sets here are contiguous, so each BFS level is a
**window** of indices, and the next window is everything up to the furthest jump from the
current one. No queue is needed: two numbers describe a level.

## Approach

Maintain:

- `end` = last index reachable with `jumps` jumps (the edge of the current level),
- `furthest` = furthest index reachable with `jumps + 1` jumps (from any index seen so far).

Scan `i` from `0` to `n - 2` (we never need to jump *from* the last index):

1. `furthest = max(furthest, i + nums[i])`.
2. If `i == end`, the current level is exhausted, so one more jump is required:
   `jumps += 1`, `end = furthest`.

**Trace for `[2, 3, 1, 1, 4]`:**

| i | nums[i] | furthest | i == end? | jumps | end |
|---|---|---|---|---|---|
| start | | 0 | | 0 | 0 |
| 0 | 2 | 2 | yes | 1 | 2 |
| 1 | 3 | 4 | | 1 | 2 |
| 2 | 1 | 4 | yes | 2 | 4 |
| 3 | 1 | 4 | | 2 | 4 |

Stop before `i = 4` (the last index): 2 jumps. Level 0 = `{0}`, level 1 = `{1, 2}`, level 2 =
`{3, 4}`.

**Why it's correct (stays ahead).** By induction, after `k` jumps *no* strategy can be beyond
index `end_k`, because `end_{k+1}` is computed as the maximum over every index any `k`-jump
strategy can occupy. So the first `k` whose window contains `n-1` is the minimum.

**Contrast with DP.** `dp[i] = 1 + min(dp[j])` over `j` that can reach `i` is O(n²) (or
O(n · max jump)). The greedy exploits that `dp` is non-decreasing in `i`.

## Complexity

O(n) time, O(1) space.

## Common mistakes

- **Iterating up to `n - 1` inclusive.** If `end` happens to equal `n - 1` you'd count a
  useless extra jump. Stop at `n - 2`.
- **Jumping to the index with the biggest value** in range, rather than the one with the
  biggest `i + nums[i]`.
- **`n = 1`**: zero jumps, loop body never runs.

## Going further

- If reachability isn't guaranteed, return `-1` when `furthest` fails to move past `end`
  at a level boundary.
- **Jump Game III / IV** (jumps to equal values, both directions) need a real BFS with a
  visited set.
- **Minimum number of refuelling stops** is the "fuel" version: a max-heap of passed
  stations replaces the window.
""",
    solution=r"""def min_jumps(nums):
    n = len(nums)
    jumps = 0
    end = 0          # furthest index reachable with `jumps` jumps (edge of the BFS level)
    furthest = 0     # furthest index reachable with `jumps + 1` jumps
    # We never jump FROM the last index, so stop at n - 2.
    for i in range(n - 1):
        # Every i <= end is reachable with `jumps` jumps; see how far it gets us.
        furthest = max(furthest, i + nums[i])
        if i == end:
            # We've explored the whole current level; one more jump is unavoidable,
            # and the best it can do is land anywhere up to `furthest`.
            jumps += 1
            end = furthest
    return jumps
""",
    refs={
        "cpp": r"""long long minJumps(vector<long long>& nums) {
    long long jumps = 0, end = 0, furthest = 0;
    for (size_t i = 0; i + 1 < nums.size(); ++i) {
        furthest = max(furthest, (long long)i + nums[i]);
        if ((long long)i == end) {          // current BFS level exhausted
            ++jumps;
            end = furthest;
        }
    }
    return jumps;
}""",
        "rust": r"""pub fn min_jumps(nums: Vec<i64>) -> i64 {
    let n = nums.len();
    let (mut jumps, mut end, mut furthest) = (0i64, 0usize, 0usize);
    for i in 0..n.saturating_sub(1) {
        furthest = furthest.max(i + nums[i] as usize);
        if i == end {
            jumps += 1;
            end = furthest;
        }
    }
    jumps
}""",
        "espresso": r"""fn minJumps(nums) {
  var n = len(nums)
  var jumps = 0
  var end = 0          // edge of the current level
  var furthest = 0     // edge of the next level
  for var i in 0..n - 1 {
    if i + nums[i] > furthest { furthest = i + nums[i] }
    if i == end {
      jumps += 1
      end = furthest
    }
  }
  return jumps
}""",
    },
    tests=_jg2_tests(),
))


# ---------------------------------------------------------------------------
# 3. Gas station
# ---------------------------------------------------------------------------
def _gas_valid_starts(gas, cost):
    n = len(gas)
    res = []
    for s in range(n):
        tank, ok = 0, True
        for k in range(n):
            i = (s + k) % n
            tank += gas[i] - cost[i]
            if tank < 0:
                ok = False
                break
        if ok:
            res.append(s)
    return res


def _gas_tests():
    r = random.Random(1403)
    t = [[[1, 2, 3, 4, 5], [3, 4, 5, 1, 2]], [[2, 3, 4], [3, 4, 3]], [[5], [4]], [[1], [2]],
         [[3, 3, 4], [3, 4, 4]], [[4, 0], [3, 1]], [[0, 0, 9], [2, 2, 1]], [[5, 1, 2, 3, 4], [4, 4, 1, 5, 1]],
         [[1, 1, 1, 1], [1, 1, 1, 2]]]
    while len(t) < 13:
        n = r.randint(8, 25)
        gas = [r.randint(0, 10) for _ in range(n)]
        cost = [r.randint(0, 10) for _ in range(n)]
        v = _gas_valid_starts(gas, cost)
        if len(v) <= 1 and (len(v) == 1 or len(t) == 12):
            t.append([gas, cost])
    return t


PROBLEMS.append(dict(
    id="gas-station",
    title="Gas Station",
    difficulty=2,
    tags=["greedy", "array", "circular"],
    fn="can_complete_circuit",
    params=[["gas", "int[]"], ["cost", "int[]"]],
    returns="int",
    statement=r"""`n` gas stations sit on a circular road. Station `i` provides `gas[i]` units of
fuel, and driving from station `i` to station `(i + 1) mod n` burns `cost[i]` units.

Your car has an unlimited tank and starts **empty** at a station of your choice. Return the
index of the station from which you can drive once around the whole circuit (back to the
start), or `-1` if no such station exists. If a solution exists, it is guaranteed to be
unique.""",
    example_notes=[
        "Start at 3 with 4 fuel: 4-1+5-2+1-3+2-4+3-5 never goes negative.",
        "Total gas 9 < total cost 10: impossible from anywhere.",
    ],
    constraints=["1 ≤ n ≤ 10⁵", "0 ≤ gas[i], cost[i] ≤ 10⁴"],
    hints=[
        "If `sum(gas) < sum(cost)` it's clearly impossible. Surprisingly, if `sum(gas) ≥ sum(cost)` it's always possible.",
        "Simulate from start `s`. Suppose the tank first goes negative when leaving station `j`. Could any station between `s` and `j` be a valid start?",
        "No: each of them would arrive at `j` with *less* fuel than you did. So reset the start to `j + 1` and the tank to 0. One pass suffices.",
    ],
    explanation=r"""## Intuition

Brute force tries each start and simulates a full lap: O(n²). The greedy observation is
about **what a failure tells you**. Let `diff[i] = gas[i] - cost[i]`. Starting at `s` with an
empty tank, suppose the running sum first drops below zero after station `j`. Consider any
`k` strictly between `s` and `j`. When we passed `k` coming from `s`, our tank was `≥ 0`
(the sum hadn't gone negative yet). Starting fresh at `k` means arriving at `k` with exactly
0, which is no better. So starting from `k` also fails at or before `j`. **Every station in
`[s, j]` is ruled out at once**, and the next candidate is `j + 1`.

## Approach

1. Keep `total = Σ diff` over the whole circle and a running `tank` from the current
   candidate `start`.
2. For each `i`: add `diff[i]` to both. If `tank < 0`, set `start = i + 1`, `tank = 0`.
3. At the end, if `total < 0` return `-1`; otherwise return `start`.

**Why `total ≥ 0` guarantees `start` works.** Let `P(i) = diff[0] + … + diff[i-1]` be the
prefix sums. During the pass, `tank = P(i+1) - P(start)`, so a reset happens exactly when the
prefix sum hits a new strict minimum. Hence the final `start` is the index right after the
**minimum prefix sum**. Driving from `start`, the fuel on arrival at any later station `j` is
`P(j) - P(start) ≥ 0` (nothing is below the minimum), and after wrapping past the end it is
`total + P(j) - P(start) ≥ 0` as well, provided `total ≥ 0`. The tank never goes negative.

**Trace for `gas = [1,2,3,4,5]`, `cost = [3,4,5,1,2]`:**

| i | diff | tank (after) | action | start |
|---|---|---|---|---|
| 0 | -2 | -2 | reset | 1 |
| 1 | -2 | -2 | reset | 2 |
| 2 | -2 | -2 | reset | 3 |
| 3 | +3 | 3 | | 3 |
| 4 | +3 | 6 | | 3 |

`total = 0 ≥ 0`, answer 3.

## Complexity

O(n) time, single pass. O(1) space.

## Common mistakes

- **Restarting the simulation** from `j + 1` *and* re-scanning the circle: O(n²) again. The
  whole point is that the pass never backs up.
- **Resetting `start = i`** instead of `i + 1`. Station `i` itself was just shown to fail.
- **Forgetting the global check.** Without `total ≥ 0`, the final `start` might fail when
  wrapping around.
- **Simulating with `% n`** past the end is unnecessary: the total check covers the wrap.

## Going further

- The same "start after the minimum prefix sum" idea finds the rotation of a circular
  sequence whose every prefix is non-negative, e.g. balancing a circular bracket string.
- If the tank has a **capacity limit**, the greedy no longer works directly; simulate with a
  monotonic deque or DP.
""",
    solution=r"""def can_complete_circuit(gas, cost):
    total = 0     # net fuel over the whole circle: decides whether ANY start works
    tank = 0      # fuel left when driving from the current candidate `start`
    start = 0
    for i in range(len(gas)):
        diff = gas[i] - cost[i]
        total += diff
        tank += diff
        if tank < 0:
            # We can't leave station i starting from `start`. Every station between
            # start and i would reach i with even less fuel, so they all fail too.
            # The next possible start is i + 1, with an empty tank.
            start = i + 1
            tank = 0
    # If the circle as a whole has enough fuel, the last surviving candidate works.
    return start if total >= 0 else -1
""",
    refs={
        "c": r"""long long can_complete_circuit(long long* gas, int gasSize, long long* cost, int costSize) {
    long long total = 0, tank = 0;
    int start = 0;
    for (int i = 0; i < gasSize; i++) {
        long long diff = gas[i] - cost[i];
        total += diff;
        tank += diff;
        if (tank < 0) {            /* stations start..i all fail: skip past them */
            start = i + 1;
            tank = 0;
        }
    }
    return total >= 0 ? start : -1;
}""",
        "cpp": r"""long long canCompleteCircuit(vector<long long>& gas, vector<long long>& cost) {
    // Start right after the minimum prefix sum of diff; valid iff the total is >= 0.
    long long prefix = 0, minPrefix = 0;
    int start = 0;
    for (size_t i = 0; i < gas.size(); ++i) {
        prefix += gas[i] - cost[i];
        if (prefix < minPrefix) {
            minPrefix = prefix;
            start = i + 1;
        }
    }
    if (prefix < 0) return -1;
    return start % gas.size();
}""",
        "rust": r"""pub fn can_complete_circuit(gas: Vec<i64>, cost: Vec<i64>) -> i64 {
    let (mut total, mut tank, mut start) = (0i64, 0i64, 0usize);
    for i in 0..gas.len() {
        let diff = gas[i] - cost[i];
        total += diff;
        tank += diff;
        if tank < 0 {
            start = i + 1;
            tank = 0;
        }
    }
    if total >= 0 { start as i64 } else { -1 }
}""",
        "espresso": r"""fn canCompleteCircuit(gas, cost) {
  var total = 0
  var tank = 0
  var start = 0
  for var i in 0..len(gas) {
    var diff = gas[i] - cost[i]
    total += diff
    tank += diff
    if tank < 0 {       // start..i all fail; try i + 1 with an empty tank
      start = i + 1
      tank = 0
    }
  }
  if total < 0 { return -1 }
  return start
}""",
    },
    tests=_gas_tests(),
))


# ---------------------------------------------------------------------------
# 4. Merge intervals
# ---------------------------------------------------------------------------
def _mi_tests():
    r = random.Random(1404)
    t = [[[[1, 3], [2, 6], [8, 10], [15, 18]]], [[[1, 4], [4, 5]]], [[[1, 4]]], [[[1, 4], [0, 4]]],
         [[[1, 4], [2, 3]]], [[[5, 6], [1, 2], [3, 4]]], [[[1, 10], [2, 3], [4, 5], [6, 7]]],
         [[[2, 3], [4, 5], [6, 7], [8, 9], [1, 10]]], [[[0, 0], [0, 0]]], [[[1, 2], [3, 5], [5, 5], [6, 6]]]]
    iv = []
    for _ in range(40):
        a = r.randint(0, 200)
        iv.append([a, a + r.randint(0, 8)])
    t.append([iv])
    iv = []
    for _ in range(2000):
        a = r.randint(0, 10 ** 6)
        iv.append([a, a + r.randint(0, 300)])
    t.append([iv])
    return t


PROBLEMS.append(dict(
    id="merge-intervals",
    title="Merge Intervals",
    difficulty=2,
    tags=["intervals", "sorting"],
    fn="merge_intervals",
    params=[["intervals", "int[][]"]],
    returns="int[][]",
    statement=r"""`intervals[i] = [start_i, end_i]` describes a closed interval. Merge all
overlapping intervals and return the resulting non-overlapping intervals, **sorted by start**.

Intervals that merely touch (`[1, 4]` and `[4, 5]`) count as overlapping and are merged.""",
    example_notes=[
        "`[1,3]` and `[2,6]` overlap and become `[1,6]`.",
        "They touch at 4, so they merge.",
    ],
    constraints=["1 ≤ len(intervals) ≤ 10⁴", "0 ≤ start_i ≤ end_i ≤ 10⁷", "the input is in no particular order"],
    hints=[
        "If the intervals were sorted by start, where would overlapping ones be relative to each other?",
        "After sorting by start, an interval overlaps the merged block being built iff its start is ≤ the block's current end.",
        "Keep a result list. For each interval in start order: if it starts after the last block's end, append it; otherwise extend the last block's end to `max(end, interval_end)`.",
    ],
    explanation=r"""## Intuition

Unsorted, any interval might overlap any other: O(n²) comparisons, plus merges that cascade.
**Sort by start** and the structure becomes linear: an interval can only overlap the block
of intervals immediately before it. If the next interval starts after the current block ends,
then every later interval starts even later (sorted!), so the current block is final.

## Approach

1. Sort intervals by start.
2. Walk through them, keeping the result list; its last element is the *open block*.
3. For interval `[s, e]`:
   - if the result is empty or `s > last_end`: start a new block `[s, e]`;
   - else: it overlaps (or touches) the block; set `last_end = max(last_end, e)`.

**Trace for `[[1,3],[2,6],[8,10],[15,18]]`** (already sorted):

| interval | last block before | overlap? | result |
|---|---|---|---|
| [1,3] | none | | [[1,3]] |
| [2,6] | [1,3] | 2 ≤ 3 | [[1,6]] |
| [8,10] | [1,6] | 8 > 6 | [[1,6],[8,10]] |
| [15,18] | [8,10] | 15 > 10 | [[1,6],[8,10],[15,18]] |

**Why `max` matters.** In `[[1,10],[2,3]]` the second interval is *contained* in the first.
Setting `last_end = e` would shrink the block to `[1,3]`.

**Why sorting by start is enough.** The open block covers `[block_start, last_end]`. An
interval with `s ≤ last_end` starts inside that range (its start is ≥ `block_start` by the
sort), so it overlaps the interval that achieved `last_end`: it belongs to the block. An
interval with `s > last_end` is disjoint from every interval in the block, and every later
interval starts even later, so the block is complete. Each block is exactly one connected
group of mutually overlapping intervals.

## Complexity

O(n log n) for the sort, O(n) for the scan. O(n) for the output (plus the sort's memory).

## Common mistakes

- **`s < last_end` instead of `≤`**: touching intervals stay separate. Read the spec for
  closed vs half-open intervals.
- **`last_end = e`** instead of `max`: breaks on contained intervals.
- **Mutating the input's inner lists** in languages with reference semantics (Python): if you
  append the input list object and then modify its end, you've also modified the caller's
  data. Copy (`[s, e]`) when starting a block.
- **Forgetting to sort**, or sorting by end.

## Going further

- **Insert Interval** (next problem): the input is already sorted and disjoint, so one new
  interval can be merged in O(n) without sorting.
- **Interval List Intersections**: two sorted lists, two pointers, emit
  `[max(starts), min(ends)]` when non-empty, advance the one that ends first.
- For a stream of intervals, keep blocks in a balanced BST / sorted map keyed by start
  (C++ `std::map`, Java `TreeMap`) to merge each new interval in O(log n) amortised.
""",
    solution=r"""def merge_intervals(intervals):
    # Sorting by start puts every group of overlapping intervals next to each other.
    ordered = sorted(intervals, key=lambda iv: iv[0])
    merged = []
    for start, end in ordered:
        if not merged or start > merged[-1][1]:
            # Starts after the open block ends: nothing later can reach back into that
            # block (later starts are even larger), so it's final. Open a new block.
            # Use a fresh list so we never mutate the caller's intervals.
            merged.append([start, end])
        else:
            # Overlaps or touches the open block: extend it. `max` handles intervals that
            # are entirely contained in the block.
            merged[-1][1] = max(merged[-1][1], end)
    return merged
""",
    refs={
        "c": r"""static int cmp_start(const void* a, const void* b) {
    long long x = (*(long long* const*)a)[0], y = (*(long long* const*)b)[0];
    return (x > y) - (x < y);
}

long long** merge_intervals(long long** intervals, int intervalsSize, int* intervalsColSize,
                            int* returnSize, int** returnColumnSizes) {
    /* Sort the array of row pointers by each row's start. */
    qsort(intervals, intervalsSize, sizeof(long long*), cmp_start);
    long long** out = malloc(sizeof(long long*) * intervalsSize);
    *returnColumnSizes = malloc(sizeof(int) * intervalsSize);
    int k = 0;
    for (int i = 0; i < intervalsSize; i++) {
        long long s = intervals[i][0], e = intervals[i][1];
        if (k == 0 || s > out[k - 1][1]) {          /* new block */
            out[k] = malloc(sizeof(long long) * 2);
            out[k][0] = s;
            out[k][1] = e;
            (*returnColumnSizes)[k] = 2;
            k++;
        } else if (e > out[k - 1][1]) {
            out[k - 1][1] = e;                      /* extend the open block */
        }
    }
    *returnSize = k;
    return out;
}""",
        "cpp": r"""vector<vector<long long>> mergeIntervals(vector<vector<long long>>& intervals) {
    sort(intervals.begin(), intervals.end());          // lexicographic: by start, then end
    vector<vector<long long>> merged;
    for (auto& iv : intervals) {
        if (merged.empty() || iv[0] > merged.back()[1]) merged.push_back(iv);
        else merged.back()[1] = max(merged.back()[1], iv[1]);
    }
    return merged;
}""",
        "rust": r"""pub fn merge_intervals(intervals: Vec<Vec<i64>>) -> Vec<Vec<i64>> {
    let mut ordered = intervals;
    ordered.sort_unstable_by_key(|iv| iv[0]);
    let mut merged: Vec<Vec<i64>> = Vec::new();
    for iv in ordered {
        match merged.last_mut() {
            Some(last) if iv[0] <= last[1] => last[1] = last[1].max(iv[1]),
            _ => merged.push(iv),
        }
    }
    merged
}""",
    },
    tests=_mi_tests(),
))


# ---------------------------------------------------------------------------
# 5. Insert interval
# ---------------------------------------------------------------------------
def _ii_tests():
    r = random.Random(1405)
    t = [[[[1, 3], [6, 9]], [2, 5]], [[[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]],
         [[], [5, 7]], [[[1, 5]], [2, 3]], [[[1, 5]], [6, 8]], [[[3, 5]], [0, 1]], [[[1, 5]], [0, 9]],
         [[[1, 2], [5, 6]], [3, 4]], [[[1, 2], [5, 6]], [2, 5]], [[[1, 2], [4, 6]], [7, 7]]]
    iv, x = [], 0
    for _ in range(1500):
        x += r.randint(1, 50)
        a = x
        x += r.randint(0, 30)
        iv.append([a, x])
    t.append([iv, [iv[300][1] + 1, iv[700][0] + 3]])
    t.append([iv, [iv[1499][1] + 5, iv[1499][1] + 9]])
    return t


PROBLEMS.append(dict(
    id="insert-interval",
    title="Insert Interval",
    difficulty=2,
    tags=["intervals", "array"],
    fn="insert_interval",
    params=[["intervals", "int[][]"], ["new_interval", "int[]"]],
    returns="int[][]",
    statement=r"""`intervals` is a list of **non-overlapping** closed intervals sorted by start.
Insert `new_interval = [start, end]`, merging wherever it overlaps or touches existing
intervals, and return the resulting sorted, non-overlapping list.""",
    example_notes=[
        "`[2,5]` overlaps `[1,3]`, giving `[1,5]`.",
        "`[4,8]` swallows `[3,5]`, `[6,7]` and `[8,10]`.",
    ],
    constraints=["0 ≤ len(intervals) ≤ 10⁴", "intervals are sorted by start and pairwise disjoint (not touching)",
                 "0 ≤ start ≤ end ≤ 10⁷ for every interval"],
    hints=[
        "The input is already sorted and disjoint, so you don't need to sort. Split the list into three groups relative to the new interval.",
        "Group 1: intervals ending before the new one starts. Group 3: intervals starting after the new one ends. Group 2: everything in between overlaps it.",
        "Copy group 1, then fold group 2 into the new interval with `min` of starts and `max` of ends, append it, then copy group 3. One pass, no sort.",
    ],
    explanation=r"""## Intuition

You could append the new interval and run Merge Intervals, paying O(n log n) for a sort that
undoes work the input already did. Since the list is sorted and disjoint, the intervals fall
into **three contiguous runs** relative to `new = [ns, ne]`:

```text
 [==]  [===]     [====new====]       [==]  [===]
 entirely left   overlapping run     entirely right
 (end < ns)      (merge into new)    (start > ne)
```

Because the list is sorted, these runs appear in this order, so one left-to-right scan with
an index handles all three.

## Approach

1. **Left run:** while `intervals[i].end < ns`, copy the interval to the output.
2. **Overlap run:** while `intervals[i].start ≤ ne`, absorb it:
   `ns = min(ns, start)`, `ne = max(ne, end)`. Then append `[ns, ne]`.
3. **Right run:** copy everything that remains.

**Trace for `[[1,2],[3,5],[6,7],[8,10],[12,16]]`, new `[4,8]`:**

| interval | phase | test | new so far | output |
|---|---|---|---|---|
| [1,2] | left | 2 < 4 | [4,8] | [1,2] |
| [3,5] | overlap | 3 ≤ 8 | [3,8] | |
| [6,7] | overlap | 6 ≤ 8 | [3,8] | |
| [8,10] | overlap | 8 ≤ 8 (touch) | [3,10] | |
| [12,16] | right | 12 > 10 | | [1,2],[3,10],[12,16] |

Note the overlap test uses the *growing* `ne`: after absorbing `[8,10]`, `ne = 10`, so an
interval starting at 9 would also have been absorbed.

**Correctness.** An interval with `end < ns` is disjoint from `new` and from everything that
will be merged into it (those all end ≥ ns, start ≥ its start). An interval with
`start > ne` (final `ne`) is likewise disjoint. Everything in between intersects the growing
merged interval.

## Complexity

O(n) time, O(n) output. With binary search you can *locate* the overlap run in O(log n), but
building the output list is still O(n) (unless you edit a balanced tree in place).

## Common mistakes

- **Strict vs non-strict comparisons.** Touching intervals merge here, so the left run
  needs `end < ns` (strict) and the overlap run `start ≤ ne`.
- **Forgetting to append the merged interval** when the overlap run is empty (the new
  interval falls into a gap, or the list is empty).
- **Using the original `ne`** in the overlap test instead of the updated one.

## Going further

- **Remove Interval**: subtract `[a, b]` from a sorted disjoint list, possibly splitting one
  interval into two.
- A **range module** (add / remove / query ranges online) keeps the disjoint intervals in a
  sorted map and applies exactly this logic around the affected keys.
""",
    solution=r"""def insert_interval(intervals, new_interval):
    ns, ne = new_interval
    out = []
    i, n = 0, len(intervals)
    # 1) Intervals that end strictly before the new one starts are untouched.
    while i < n and intervals[i][1] < ns:
        out.append(list(intervals[i]))
        i += 1
    # 2) Everything that starts no later than the (growing) new end overlaps or touches it:
    #    fold it into the new interval.
    while i < n and intervals[i][0] <= ne:
        ns = min(ns, intervals[i][0])
        ne = max(ne, intervals[i][1])
        i += 1
    out.append([ns, ne])
    # 3) The rest start after the merged interval ends: copy them unchanged.
    while i < n:
        out.append(list(intervals[i]))
        i += 1
    return out
""",
    refs={
        "cpp": r"""vector<vector<long long>> insertInterval(vector<vector<long long>>& intervals, vector<long long>& newInterval) {
    long long ns = newInterval[0], ne = newInterval[1];
    vector<vector<long long>> out;
    size_t i = 0, n = intervals.size();
    while (i < n && intervals[i][1] < ns) out.push_back(intervals[i++]);   // left run
    while (i < n && intervals[i][0] <= ne) {                               // overlap run
        ns = min(ns, intervals[i][0]);
        ne = max(ne, intervals[i][1]);
        ++i;
    }
    out.push_back({ns, ne});
    while (i < n) out.push_back(intervals[i++]);                           // right run
    return out;
}""",
        "rust": r"""pub fn insert_interval(intervals: Vec<Vec<i64>>, new_interval: Vec<i64>) -> Vec<Vec<i64>> {
    let (mut ns, mut ne) = (new_interval[0], new_interval[1]);
    let mut out = Vec::with_capacity(intervals.len() + 1);
    let mut it = intervals.into_iter().peekable();
    // Left run: ends before the new interval starts.
    while let Some(iv) = it.next_if(|iv| iv[1] < ns) {
        out.push(iv);
    }
    // Overlap run: starts no later than the growing end.
    while let Some(iv) = it.next_if(|iv| iv[0] <= ne) {
        ns = ns.min(iv[0]);
        ne = ne.max(iv[1]);
    }
    out.push(vec![ns, ne]);
    out.extend(it);                                   // right run
    out
}""",
    },
    tests=_ii_tests(),
))


# ---------------------------------------------------------------------------
# 6. Non-overlapping intervals (min removals)
# ---------------------------------------------------------------------------
def _no_tests():
    r = random.Random(1406)
    t = [[[[1, 2], [2, 3], [3, 4], [1, 3]]], [[[1, 2], [1, 2], [1, 2]]], [[[1, 2], [2, 3]]], [[[5, 9]]],
         [[[1, 100], [11, 22], [1, 11], [2, 12]]], [[[0, 2], [1, 3], [2, 4], [3, 5], [4, 6]]],
         [[[-5, -1], [-3, 0], [0, 4]]], [[[1, 10], [2, 3], [4, 5], [6, 7], [8, 9]]]]
    iv = []
    for _ in range(25):
        a = r.randint(0, 60)
        iv.append([a, a + r.randint(1, 12)])
    t.append([iv])
    iv = []
    for _ in range(25):
        a = r.randint(0, 200)
        iv.append([a, a + r.randint(1, 5)])
    t.append([iv])
    return t


PROBLEMS.append(dict(
    id="non-overlapping-intervals",
    title="Non-overlapping Intervals",
    difficulty=2,
    tags=["greedy", "intervals", "sorting", "exchange argument"],
    fn="erase_overlap_intervals",
    params=[["intervals", "int[][]"]],
    returns="int",
    statement=r"""Return the **minimum number of intervals to remove** from `intervals` so that
the remaining ones do not overlap.

Intervals `[a, b]` with `a < b` are half-open for this problem: two intervals that only touch
at an endpoint (`[1, 2]` and `[2, 3]`) do **not** overlap.""",
    example_notes=[
        "Remove `[1,3]`; the rest touch but don't overlap.",
        "Keep one copy, remove two.",
    ],
    constraints=["1 ≤ len(intervals) ≤ 10⁵", "-5·10⁴ ≤ start < end ≤ 5·10⁴"],
    hints=[
        "Removing the fewest is the same as *keeping the most*: find the largest set of pairwise non-overlapping intervals.",
        "Which interval should the kept set start with? Think about which one leaves the most room for the rest.",
        "Sort by **end**. Keep an interval if it starts at or after the end of the last kept one; otherwise remove it. Answer = removed count.",
    ],
    explanation=r"""## Intuition

Minimum removals = `n` − (maximum number of intervals you can keep with no overlaps). The
second quantity is the classic **activity selection** problem, and its greedy solution is to
always keep the interval that **finishes first**: it uses up the least of the timeline, so it
leaves the most room for everything else.

Other "natural" rules fail:

- *earliest start*: `[[1,100],[2,3],[4,5]]` keeps the long `[1,100]` and nothing else;
- *shortest first*: `[[1,5],[4,7],[6,10]]` keeps only `[4,7]` (it overlaps both others), but
  `[1,5]` and `[6,10]` can coexist.

## Approach

1. Sort by end.
2. `last_end = -∞`, `removed = 0`.
3. For each `[s, e]` in order: if `s ≥ last_end`, keep it (`last_end = e`); else remove it
   (`removed += 1`).

**Trace for `[[1,2],[2,3],[3,4],[1,3]]`**, sorted by end: `[1,2], [2,3], [1,3], [3,4]`.

| interval | last_end | s ≥ last_end? | action | removed |
|---|---|---|---|---|
| [1,2] | -∞ | yes | keep | 0 |
| [2,3] | 2 | yes (touch) | keep | 0 |
| [1,3] | 3 | no | remove | 1 |
| [3,4] | 3 | yes | keep | 1 |

**Proof (exchange argument).** Let `g` be the interval with the earliest end, and `OPT` a
maximum non-overlapping set whose first interval (by end) is `o ≠ g`. Since `end(g) ≤
end(o)`, and every other interval of `OPT` starts at or after `end(o)`, it also starts at or
after `end(g)`. So `OPT - {o} + {g}` is still valid and has the same size. Now `OPT` agrees
with greedy on the first choice; discard everything overlapping `g` and repeat the argument on
the rest. Greedy keeps as many intervals as `OPT`, so it removes as few.

## Complexity

O(n log n) for sorting, O(n) for the scan, O(1) extra (beyond the sort).

## Common mistakes

- **Sorting by start** without the "keep the one with smaller end on conflict" fix. (Sorting by
  start *can* work if, on overlap, you keep whichever ends first: `last_end = min(last_end,
  e)`. Same exchange argument.)
- **`s > last_end`** instead of `≥`: touching intervals would be treated as overlapping.
- **Initialising `last_end = 0`**: wrong with negative coordinates. Use the first interval or
  `-∞`.

## Going further

- **Minimum arrows to burst balloons** is the same greedy with *closed* intervals (touching
  balloons share an arrow): count kept intervals using `s > last_end`.
- **Weighted** interval scheduling (each interval has a value, maximise total value) breaks the
  greedy; sort by end and use DP with binary search: `dp[i] = max(dp[i-1], w_i + dp[p(i)])`.
- **Interval partitioning** (minimum rooms to hold *all* intervals) is the next problem.
""",
    solution=r"""def erase_overlap_intervals(intervals):
    # Keep as many intervals as possible; everything else is removed.
    # Earliest-finishing interval first: it leaves the most room for the rest
    # (exchange argument: it can replace the first interval of any optimal set).
    ordered = sorted(intervals, key=lambda iv: iv[1])
    removed = 0
    last_end = float("-inf")             # end of the last KEPT interval
    for start, end in ordered:
        if start >= last_end:
            # Compatible (touching is fine): keep it.
            last_end = end
        else:
            # Overlaps the last kept interval, which ends no later than this one.
            # Dropping this one is never worse.
            removed += 1
    return removed
""",
    refs={
        "cpp": r"""long long eraseOverlapIntervals(vector<vector<long long>>& intervals) {
    sort(intervals.begin(), intervals.end(),
         [](const vector<long long>& a, const vector<long long>& b) { return a[1] < b[1]; });
    long long removed = 0, lastEnd = LLONG_MIN;
    for (auto& iv : intervals) {
        if (iv[0] >= lastEnd) lastEnd = iv[1];   // keep
        else ++removed;                          // overlaps the last kept one
    }
    return removed;
}""",
        "rust": r"""pub fn erase_overlap_intervals(intervals: Vec<Vec<i64>>) -> i64 {
    // Variant: sort by START, and on a conflict keep whichever interval ends first.
    let mut iv = intervals;
    iv.sort_unstable_by_key(|x| x[0]);
    let mut removed = 0i64;
    let mut last_end = iv[0][1];
    for x in iv.iter().skip(1) {
        if x[0] >= last_end {
            last_end = x[1];
        } else {
            removed += 1;
            last_end = last_end.min(x[1]);   // keep the one that frees the timeline sooner
        }
    }
    removed
}""",
        "espresso": r"""fn eraseOverlapIntervals(intervals) {
  var n = len(intervals)
  // Insertion sort by end time. Swap the two numbers of each row individually:
  // plain values, so there are no aliasing surprises with row references.
  for var i in 1..n {
    var j = i
    while j > 0 and intervals[j - 1][1] > intervals[j][1] {
      var s = intervals[j][0]
      var e = intervals[j][1]
      intervals[j][0] = intervals[j - 1][0]
      intervals[j][1] = intervals[j - 1][1]
      intervals[j - 1][0] = s
      intervals[j - 1][1] = e
      j -= 1
    }
  }
  var removed = 0
  var lastEnd = intervals[0][1]          // always keep the earliest-ending interval
  for var i in 1..n {
    if intervals[i][0] >= lastEnd {
      lastEnd = intervals[i][1]          // compatible: keep
    } else {
      removed += 1                       // overlaps: drop it
    }
  }
  return removed
}""",
    },
    tests=_no_tests(),
))


# ---------------------------------------------------------------------------
# 7. Meeting rooms II
# ---------------------------------------------------------------------------
def _mr_tests():
    r = random.Random(1407)
    t = [[[[0, 30], [5, 10], [15, 20]]], [[[7, 10], [2, 4]]], [[[1, 5]]], [[[1, 5], [5, 10]]],
         [[[1, 10], [2, 9], [3, 8], [4, 7]]], [[[1, 2], [1, 2], [1, 2]]], [[[9, 10], [4, 9], [4, 17]]],
         [[[0, 5], [1, 2], [2, 3], [3, 4], [4, 6]]]]
    iv = []
    for _ in range(30):
        a = r.randint(0, 100)
        iv.append([a, a + r.randint(1, 20)])
    t.append([iv])
    iv = []
    for _ in range(25):
        a = r.randint(0, 50)
        iv.append([a, a + r.randint(1, 40)])
    t.append([iv])
    return t


PROBLEMS.append(dict(
    id="meeting-rooms-min-rooms",
    title="Meeting Rooms II",
    difficulty=2,
    tags=["intervals", "sweep line", "heap", "sorting"],
    fn="min_meeting_rooms",
    params=[["intervals", "int[][]"]],
    returns="int",
    statement=r"""Each meeting `[start, end]` occupies a room during the half-open time range
`[start, end)`. A meeting ending at time `t` frees its room for another starting at `t`.

Return the **minimum number of rooms** needed to hold all meetings.""",
    example_notes=[
        "`[0,30]` overlaps both others, but `[5,10]` and `[15,20]` can share: 2 rooms.",
        "No overlap: 1 room.",
    ],
    constraints=["1 ≤ len(intervals) ≤ 10⁴", "0 ≤ start < end ≤ 10⁶"],
    hints=[
        "The answer is the maximum number of meetings running at the same instant. Why can't it be less, and why is that many enough?",
        "Sweep through time. Each start is `+1` active meeting, each end is `-1`. Track the running count.",
        "Sort the starts and the ends separately. Walk through the starts; before counting a start, release every meeting whose end ≤ this start. Or keep a min-heap of end times.",
    ],
    explanation=r"""## Intuition

At any instant, the meetings in progress all need different rooms, so the answer is **at
least** the maximum overlap depth. It is also **enough**: process meetings by start time and
give each one any room that is free; a new room is opened only when every room is busy, i.e.
when the overlap depth increases. So the problem reduces to *maximum number of intervals
covering one point*, which a **sweep line** answers.

## Approach

**Sweep with two sorted arrays.** Sort all starts, sort all ends. Walk through the starts in
order with a pointer `j` into the ends:

1. Before placing meeting with start `s`, free every room whose meeting ended at or before
   `s` (`while ends[j] <= s: j += 1; active -= 1`).
2. Place the meeting: `active += 1`, `rooms = max(rooms, active)`.

The `<=` implements the half-open rule: an end at `t` is processed before a start at `t`.

**Trace for `[[0,30],[5,10],[15,20]]`:** starts `0, 5, 15`, ends `10, 20, 30`.

| start | ends released | active | rooms |
|---|---|---|---|
| 0 | | 1 | 1 |
| 5 | | 2 | 2 |
| 15 | 10 | 2 | 2 |

**Equivalent: min-heap of end times.** Sort meetings by start; the heap holds the end time of
each occupied room. For each meeting, if the earliest-ending room is free (`heap[0] ≤ s`),
reuse it (pop); push this meeting's end. The heap size at the end is the room count. This
version also tells you *which* room each meeting gets.

**Why the greedy assignment is optimal.** When a meeting starting at `s` forces a new room,
all existing rooms are busy at `s`, so `rooms` meetings (including the new one) overlap at
time `s`: no schedule can do with fewer.

## Complexity

O(n log n) for sorting (or heap operations), O(n) extra space for the two arrays / heap.

## Common mistakes

- **`<` instead of `<=`** when releasing ends: back-to-back meetings would need two rooms.
- **Counting overlaps pairwise** (O(n²)) and taking the max *degree*: a meeting can
  overlap three others that don't overlap each other; degree ≠ depth.
- **Sorting events without a tie-break**: with a single list of `(time, ±1)` events, sort
  ends (`-1`) before starts (`+1`) at equal times.

## Going further

- **Meeting Rooms I** (can one person attend all?) = "is the max depth 1?": sort by start,
  check `start[i] ≥ end[i-1]`.
- **Car pooling / max concurrent load**: the same sweep with weights instead of `±1`; with
  small coordinates, a **difference array** replaces the sort.
- The ESPresso reference uses the depth characterisation directly: the max overlap is attained
  at some meeting's start, so it counts, for each start `s`, the meetings with
  `start ≤ s < end`. That is O(n²) but needs no extra arrays.
""",
    solution=r"""def min_meeting_rooms(intervals):
    # Max number of meetings in progress at once = rooms needed (and rooms sufficient).
    starts = sorted(iv[0] for iv in intervals)
    ends = sorted(iv[1] for iv in intervals)
    active = rooms = 0
    j = 0                                  # next end time not yet released
    for s in starts:
        # Release every meeting that has ended by time s. `<=` because a room freed at s
        # can be reused by a meeting starting at s (half-open intervals).
        while ends[j] <= s:
            active -= 1
            j += 1
        active += 1                        # this meeting occupies a room
        rooms = max(rooms, active)
    return rooms
""",
    refs={
        "cpp": r"""long long minMeetingRooms(vector<vector<long long>>& intervals) {
    // Min-heap of end times of the rooms currently in use.
    sort(intervals.begin(), intervals.end());
    priority_queue<long long, vector<long long>, greater<long long>> ends;
    for (auto& iv : intervals) {
        if (!ends.empty() && ends.top() <= iv[0]) ends.pop();   // reuse the room freed first
        ends.push(iv[1]);
    }
    return ends.size();
}""",
        "rust": r"""pub fn min_meeting_rooms(intervals: Vec<Vec<i64>>) -> i64 {
    // Sweep over events: (time, delta). Ends (-1) sort before starts (+1) at equal times.
    let mut events: Vec<(i64, i64)> = Vec::with_capacity(intervals.len() * 2);
    for iv in &intervals {
        events.push((iv[0], 1));
        events.push((iv[1], -1));
    }
    events.sort_unstable();                 // (t, -1) < (t, 1)
    let (mut active, mut rooms) = (0i64, 0i64);
    for (_, d) in events {
        active += d;
        rooms = rooms.max(active);
    }
    rooms
}""",
        "espresso": r"""fn minMeetingRooms(intervals) {
  // Max overlap depth is reached at some meeting's start time s:
  // count meetings with start <= s < end, for every s. O(n^2), no extra arrays.
  var n = len(intervals)
  var rooms = 0
  for var i in 0..n {
    var s = intervals[i][0]
    var depth = 0
    for var j in 0..n {
      if intervals[j][0] <= s and s < intervals[j][1] { depth += 1 }
    }
    if depth > rooms { rooms = depth }
  }
  return rooms
}""",
    },
    tests=_mr_tests(),
))


# ---------------------------------------------------------------------------
# 8. Assign cookies
# ---------------------------------------------------------------------------
def _ac_tests():
    r = random.Random(1408)
    t = [[[1, 2, 3], [1, 1]], [[1, 2], [1, 2, 3]], [[1], []], [[5, 5], [1, 2, 3]], [[1, 1, 1], [1, 1, 1]],
         [[10, 9, 8, 7], [5, 6, 7, 8]], [[2, 3], [3, 1, 1]], [[7], [8]]]
    t.append([[r.randint(1, 20) for _ in range(30)], [r.randint(1, 20) for _ in range(25)]])
    t.append([[r.randint(1, 50) for _ in range(20)], [r.randint(1, 50) for _ in range(30)]])
    return t


PROBLEMS.append(dict(
    id="assign-cookies",
    title="Assign Cookies",
    difficulty=1,
    tags=["greedy", "sorting", "two pointers"],
    fn="find_content_children",
    params=[["greed", "int[]"], ["sizes", "int[]"]],
    returns="int",
    statement=r"""Child `i` is content if given a cookie of size at least `greed[i]`. Cookie `j`
has size `sizes[j]`. Each child gets at most one cookie and each cookie goes to at most one
child.

Return the maximum number of content children.""",
    example_notes=[
        "Both cookies have size 1; only the child with greed 1 can be satisfied.",
        "Cookies 1 and 2 satisfy both children.",
    ],
    constraints=["1 ≤ len(greed) ≤ 3·10⁴", "0 ≤ len(sizes) ≤ 3·10⁴", "1 ≤ greed[i], sizes[j] ≤ 2³¹ - 1"],
    hints=[
        "Which child is the easiest to satisfy, and which cookie should you spend on them?",
        "Give the least greedy child the *smallest* cookie that satisfies them. Bigger cookies are more valuable later.",
        "Sort both arrays. Two pointers: walk the cookies in increasing size; if the current cookie satisfies the current (least greedy unsatisfied) child, count it and move to the next child.",
    ],
    explanation=r"""## Intuition

This is a matching problem: pair children with cookies big enough for them, maximising pairs.
Two greedy principles together solve it:

1. **Serve the easiest child first.** If any child can be satisfied, the least greedy one
   can.
2. **Spend the smallest sufficient cookie.** Using a bigger cookie than necessary can only
   hurt the children who come later.

After sorting both arrays, these become a simple two-pointer walk.

## Approach

Sort `greed` and `sizes` ascending. Pointer `child = 0`. For each cookie in increasing size:
if `cookie ≥ greed[child]`, the child is content (`child += 1`); otherwise this cookie is too
small for this child, and therefore for every remaining child, so skip it. Stop when all
children are content. The answer is `child`.

**Trace for `greed = [1, 2, 3]`, `sizes = [1, 1]`:**

| cookie | child (greed) | fits? | content |
|---|---|---|---|
| 1 | 0 (1) | yes | 1 |
| 1 | 1 (2) | no | 1 |

**Exchange argument.** Let `c₀` be the least greedy child and `b` the smallest cookie with
`b ≥ greed[c₀]`. Take any optimal assignment where `c₀` does not get `b`:

- `b` is unused: give `b` to `c₀` (returning `c₀`'s old cookie, if any). The count can only
  stay the same or grow.
- `b` went to another child `c`, and `c₀` has cookie `B`: then `B ≥ b` (b is the smallest
  that fits `c₀`), so swapping is fine: `c₀` is content with `b`, `c` is content with
  `B ≥ b ≥ greed[c]`.
- `b` went to `c`, and `c₀` has nothing: move `b` from `c` to `c₀`. The count is unchanged.

So some optimal solution makes the greedy's first choice; recurse on the rest.

**Language note.** In C, `qsort` needs a comparator: return `(a > b) - (a < b)` rather than
`a - b`, which overflows for large values. In C++ and Rust, `sort` on integers just works.

## Complexity

O(n log n + m log m) for the sorts, O(n + m) for the walk. O(1) extra space if sorting in
place.

## Common mistakes

- **Giving the biggest cookie to the greediest child first** works too (it's the mirror
  greedy), but mixing directions (biggest cookie to least greedy child) wastes big cookies.
- **Advancing the child pointer when the cookie doesn't fit.** A cookie too small for the
  current child is too small for all later children; it's the *cookie* that should be skipped.
- **Empty `sizes`**: answer 0, loop never runs.

## Going further

- When each item has a different *value* and compatibility isn't a simple threshold, you need
  **bipartite matching** (Hopcroft-Karp) or min-cost flow.
- **Boats to save people** (two per boat, weight limit) is a related two-pointer greedy: pair
  the heaviest with the lightest when possible.
""",
    solution=r"""def find_content_children(greed, sizes):
    # Sorted ascending: the least greedy child and the smallest cookie come first.
    greed = sorted(greed)
    sizes = sorted(sizes)
    child = 0                                  # least greedy child still waiting
    for cookie in sizes:
        if child == len(greed):
            break                              # everyone is content
        if cookie >= greed[child]:
            # Smallest cookie that satisfies this child: never wasteful to use it here.
            child += 1
        # Otherwise the cookie is too small for this child and for everyone after them
        # (they are greedier), so it's simply skipped.
    return child
""",
    refs={
        "c": r"""static int cmp_ll(const void* a, const void* b) {
    long long x = *(const long long*)a, y = *(const long long*)b;
    return (x > y) - (x < y);               /* never `x - y`: that can overflow int */
}

long long find_content_children(long long* greed, int greedSize, long long* sizes, int sizesSize) {
    qsort(greed, greedSize, sizeof(long long), cmp_ll);
    qsort(sizes, sizesSize, sizeof(long long), cmp_ll);
    int child = 0;
    for (int j = 0; j < sizesSize && child < greedSize; j++)
        if (sizes[j] >= greed[child]) child++;   /* smallest sufficient cookie */
    return child;
}""",
        "cpp": r"""long long findContentChildren(vector<long long>& greed, vector<long long>& sizes) {
    sort(greed.begin(), greed.end());
    sort(sizes.begin(), sizes.end());
    size_t child = 0;
    for (long long cookie : sizes)
        if (child < greed.size() && cookie >= greed[child]) ++child;
    return child;
}""",
        "rust": r"""pub fn find_content_children(greed: Vec<i64>, sizes: Vec<i64>) -> i64 {
    let (mut g, mut s) = (greed, sizes);
    g.sort_unstable();
    s.sort_unstable();
    let mut child = 0usize;
    for cookie in s {
        if child < g.len() && cookie >= g[child] {
            child += 1;
        }
    }
    child as i64
}""",
        "espresso": r"""fn sortInPlace(a) {
  // insertion sort: fine for small inputs, and needs no extra arrays
  for var i in 1..len(a) {
    var x = a[i]
    var j = i - 1
    while j >= 0 and a[j] > x {
      a[j + 1] = a[j]
      j -= 1
    }
    a[j + 1] = x
  }
}

fn findContentChildren(greed, sizes) {
  sortInPlace(greed)
  sortInPlace(sizes)
  var child = 0
  for var j in 0..len(sizes) {
    if child < len(greed) and sizes[j] >= greed[child] { child += 1 }
  }
  return child
}""",
    },
    tests=_ac_tests(),
))


# ---------------------------------------------------------------------------
# 9. Partition labels
# ---------------------------------------------------------------------------
def _pl_tests():
    r = random.Random(1409)
    t = [["ababcbacadefegdehijhklij"], ["eccbbbbdec"], ["a"], ["abc"], ["aaaa"], ["abca"],
         ["caedbdedda"], ["qiejxqfnqceocmy"]]
    t.append(["".join(r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(60))])
    blocks = ["".join(r.choice(chr(97 + 3 * k) + chr(98 + 3 * k) + chr(99 + 3 * k)) for _ in range(r.randint(1, 30))) for k in range(8)]
    t.append(["".join(blocks)])
    return t


PROBLEMS.append(dict(
    id="partition-labels",
    title="Partition Labels",
    difficulty=2,
    tags=["greedy", "strings", "intervals"],
    fn="partition_labels",
    params=[["s", "str"]],
    returns="int[]",
    statement=r"""Split `s` into as **many** contiguous parts as possible so that each letter
appears in at most one part. Concatenating the parts in order must give back `s`.

Return the **sizes** of the parts, in order.""",
    example_notes=[
        "`\"ababcbaca\"`, `\"defegde\"`, `\"hijhklij\"`: no letter appears in two parts.",
        "Everything is tied together by `e` and `c`: one part.",
    ],
    constraints=["1 ≤ len(s) ≤ 500", "lowercase English letters"],
    hints=[
        "If a part contains a letter, it must extend at least to that letter's **last occurrence** in `s`.",
        "Precompute `last[c]` for every letter. Starting a part at `start`, its end must be at least `last[s[start]]`, and grows as you meet letters whose last occurrence is further.",
        "Scan with `end = max(end, last[s[i]])`. When `i == end`, nothing inside reaches further: close the part (size `end - start + 1`) and start a new one.",
    ],
    explanation=r"""## Intuition

Each letter `c` spans an interval `[first[c], last[c]]` of positions, and that whole interval
must lie in a single part. Parts are therefore unions of **overlapping letter intervals**:
this is Merge Intervals in disguise. The greedy says: close a part as soon as you legally can.
Closing early can never hurt, because the remainder of the string is an independent instance
of the same problem.

## Approach

1. One pass to record `last[c]`, the last index of each letter.
2. Second pass with `start` (current part's beginning) and `end` (how far it must extend):
   - `end = max(end, last[s[i]])`;
   - if `i == end`: every letter seen in `[start, i]` finishes by `i`, so close the part, record
     `i - start + 1`, set `start = i + 1`.

**Trace for `"eccbbbbdec"`** (`last`: e→8, c→9, b→6, d→7):

| i | char | last[char] | end | close? |
|---|---|---|---|---|
| 0 | e | 8 | 8 | |
| 1 | c | 9 | 9 | |
| 2–6 | c, b… | ≤ 9 | 9 | |
| 7 | d | 7 | 9 | |
| 8 | e | 8 | 9 | |
| 9 | c | 9 | 9 | yes → size 10 |

**Why maximal.** A cut at position `i` is legal exactly when no letter spans across it, i.e.
`end == i` at that moment. The greedy cuts at *every* legal position, and cuts at different
positions are independent (any subset of legal cuts is legal), so taking all of them gives the
most parts.

## Complexity

O(n) time (two passes), O(Σ) = O(26) extra space for `last`.

## Common mistakes

- **Closing when the current letter's last occurrence is `i`**, ignoring earlier letters in
  the part that extend further. You need the running `max`.
- **Returning the parts instead of their sizes**, or forgetting the final part.
- **Using a dict/hash map** when a 26-element array indexed by `ord(c) - ord('a')` is simpler
  and faster (especially in C).

## Going further

- Build the letter intervals explicitly and run Merge Intervals: same answer, more code;
  useful when the "spans" come from something other than first/last occurrence.
- **Max chunks to make sorted**: cut where the running max of the prefix equals the index:
  the same "close when nothing reaches further" idea.
""",
    solution=r"""def partition_labels(s):
    # last[c] = the last index where letter c appears; a part containing c must reach it.
    last = {c: i for i, c in enumerate(s)}
    sizes = []
    start = end = 0
    for i, c in enumerate(s):
        # The current part must stretch to cover every letter it already contains.
        end = max(end, last[c])
        if i == end:
            # No letter inside [start, i] appears later: cutting here is legal, and cutting
            # as early as possible maximises the number of parts.
            sizes.append(i - start + 1)
            start = i + 1
    return sizes
""",
    refs={
        "c": r"""long long* partition_labels(char* s, int* returnSize) {
    int n = strlen(s);
    int last[26];
    for (int i = 0; i < n; i++) last[s[i] - 'a'] = i;     /* last occurrence of each letter */
    long long* out = malloc(sizeof(long long) * (n > 0 ? n : 1));
    int k = 0, start = 0, end = 0;
    for (int i = 0; i < n; i++) {
        if (last[s[i] - 'a'] > end) end = last[s[i] - 'a'];
        if (i == end) {                                   /* nothing inside reaches further */
            out[k++] = i - start + 1;
            start = i + 1;
        }
    }
    *returnSize = k;
    return out;
}""",
        "cpp": r"""vector<long long> partitionLabels(string s) {
    array<int, 26> last{};
    for (int i = 0; i < (int)s.size(); ++i) last[s[i] - 'a'] = i;
    vector<long long> sizes;
    int start = 0, end = 0;
    for (int i = 0; i < (int)s.size(); ++i) {
        end = max(end, last[s[i] - 'a']);
        if (i == end) {
            sizes.push_back(i - start + 1);
            start = i + 1;
        }
    }
    return sizes;
}""",
        "rust": r"""pub fn partition_labels(s: String) -> Vec<i64> {
    let b = s.as_bytes();
    let mut last = [0usize; 26];
    for (i, &c) in b.iter().enumerate() {
        last[(c - b'a') as usize] = i;
    }
    let (mut sizes, mut start, mut end) = (Vec::new(), 0usize, 0usize);
    for (i, &c) in b.iter().enumerate() {
        end = end.max(last[(c - b'a') as usize]);
        if i == end {
            sizes.push((i - start + 1) as i64);
            start = i + 1;
        }
    }
    sizes
}""",
    },
    tests=_pl_tests(),
))


# ---------------------------------------------------------------------------
# 10. Candy
# ---------------------------------------------------------------------------
def _candy_tests():
    r = random.Random(1410)
    t = [[[1, 0, 2]], [[1, 2, 2]], [[5]], [[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]], [[2, 2, 2]],
         [[1, 3, 2, 2, 1]], [[1, 2, 87, 87, 87, 2, 1]], [[1, 3, 4, 5, 2]], [[1, 6, 10, 8, 7, 3, 2]],
         [[0, 1, 2, 5, 3, 2, 7]]]
    t.append([[r.randint(0, 6) for _ in range(40)]])
    t.append([[r.randint(0, 100) for _ in range(40)]])
    return t


PROBLEMS.append(dict(
    id="candy-distribution",
    title="Candy",
    difficulty=3,
    tags=["greedy", "array", "two passes"],
    fn="min_candies",
    params=[["ratings", "int[]"]],
    returns="int",
    statement=r"""Children stand in a line; child `i` has rating `ratings[i]`. Hand out candies
so that:

- every child gets **at least one** candy;
- a child with a **strictly higher** rating than an adjacent neighbour gets **more** candies
  than that neighbour.

Return the minimum total number of candies. (Equal neighbours have no constraint between
them.)""",
    example_notes=[
        "Give `2, 1, 2`.",
        "Give `1, 2, 1`: the third child only needs to beat nobody (equal rating imposes nothing).",
    ],
    constraints=["1 ≤ len(ratings) ≤ 2·10⁴", "0 ≤ ratings[i] ≤ 2·10⁴"],
    hints=[
        "Split the rule into two independent families of constraints: 'beat my left neighbour' and 'beat my right neighbour'.",
        "A left-to-right pass can satisfy all left constraints minimally: `left[i] = left[i-1] + 1` if rated higher than `i-1`, else 1. Symmetrically, right to left.",
        "Each child needs `max(left[i], right[i])`, which satisfies both families and is the least that does. Sum them.",
    ],
    explanation=r"""## Intuition

Each child faces up to two constraints, one per neighbour, and fixing one side can break the
other, which is why a single pass gets tangled. Separate them:

- `left[i]` = the minimum candies child `i` needs considering only **left** neighbours:
  `left[i] = left[i-1] + 1` if `ratings[i] > ratings[i-1]`, else 1. This is exactly the
  length of the increasing run ending at `i`.
- `right[i]` similarly from the right: the length of the decreasing run starting at `i`.

Each value is a **lower bound** that any valid assignment must respect (by induction along
the run). Taking `cand[i] = max(left[i], right[i])` meets both bounds, and it is valid: if
`ratings[i] > ratings[i-1]`, then `ratings[i-1]` does not beat its right neighbour, so
`right[i-1] = 1` and `cand[i-1] = left[i-1] < left[i] ≤ cand[i]`. The mirror argument covers
right neighbours. Every child gets exactly its largest lower bound, so the total is minimal.

## Approach

1. `left` pass, left to right.
2. `right` pass, right to left; accumulate `max(left[i], right[i])`.

**Trace for `[1, 0, 2]`:**

| i | 0 | 1 | 2 |
|---|---|---|---|
| ratings | 1 | 0 | 2 |
| left | 1 | 1 | 2 |
| right | 2 | 1 | 1 |
| candies | 2 | 1 | 2 |

Total 5.

**Trace for `[1, 3, 4, 5, 2]`:** `left = [1,2,3,4,1]`, `right = [1,1,1,2,1]`, candies
`[1,2,3,4,1]` = 11. The peak 5 needs 4 because of the long climb on its left.

## Complexity

O(n) time. O(n) space for `left` (the right pass can use a running variable).

**O(1) space.** Walk the ratings as a sequence of *mountains*. Track the length of the current
`up` slope, the current `down` slope, and the `peak` height reached by the last up slope.
Each step up adds `up + 1`; each equal step resets everything and adds 1; each step down adds
`down` (everyone already on the down slope gets one more) plus 1 for the new child, and if the
down slope becomes as long as the up slope, the peak must grow too (one extra). The C and
ESPresso references use this; it avoids any extra array.

## Common mistakes

- **One pass only.** `[1, 3, 2, 2, 1]`: the left pass gives the 4th child 1 candy, but it beats
  its right neighbour.
- **Treating equal ratings as a constraint**: `[1, 2, 2]` needs `1 + 2 + 1 = 4`, not
  `1 + 2 + 3`.
- **Summing `left + right - 1`** (that's the mountain count, not the requirement) instead of
  `max`.

## Going further

- **Circular** lines break the two-pass trick: start the passes at a local minimum.
- The two-pass "constraints from each side, then combine" pattern also solves **trapping rain
  water** (`min(maxLeft, maxRight) - height`) and **product of array except self**.
""",
    solution=r"""def min_candies(ratings):
    n = len(ratings)
    # left[i]: candies needed to satisfy only the "beat my LEFT neighbour" rule.
    # It's the length of the strictly increasing run ending at i.
    left = [1] * n
    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            left[i] = left[i - 1] + 1
    # Right-to-left: `right` is the length of the strictly decreasing run starting at i,
    # i.e. what the "beat my RIGHT neighbour" rule alone requires.
    total = left[n - 1]                 # right[n-1] = 1, so max(left, right) = left there
    right = 1
    for i in range(n - 2, -1, -1):
        right = right + 1 if ratings[i] > ratings[i + 1] else 1
        # Both rules are lower bounds; the larger one satisfies both and is minimal.
        total += max(left[i], right)
    return total
""",
    refs={
        "c": r"""long long min_candies(long long* ratings, int ratingsSize) {
    /* O(1)-space "mountain" walk: up = length of current up slope, down = length of
       current down slope, peak = height of the last peak's up slope. */
    long long total = 1, up = 0, down = 0, peak = 0;
    for (int i = 1; i < ratingsSize; i++) {
        if (ratings[i] > ratings[i - 1]) {
            up++; peak = up; down = 0;
            total += up + 1;                  /* one more than the previous child */
        } else if (ratings[i] == ratings[i - 1]) {
            up = down = peak = 0;
            total += 1;                       /* no constraint: back to 1 */
        } else {
            up = 0; down++;
            /* new child gets 1, every child already on the down slope gets +1;
               when the slope gets as long as the climb, the peak must grow too */
            total += down + (peak >= down ? 0 : 1);
        }
    }
    return total;
}""",
        "cpp": r"""long long minCandies(vector<long long>& ratings) {
    int n = ratings.size();
    vector<long long> cand(n, 1);
    for (int i = 1; i < n; ++i)                 // satisfy left neighbours
        if (ratings[i] > ratings[i - 1]) cand[i] = cand[i - 1] + 1;
    for (int i = n - 2; i >= 0; --i)            // then right neighbours, keeping the max
        if (ratings[i] > ratings[i + 1]) cand[i] = max(cand[i], cand[i + 1] + 1);
    return accumulate(cand.begin(), cand.end(), 0LL);
}""",
        "rust": r"""pub fn min_candies(ratings: Vec<i64>) -> i64 {
    let n = ratings.len();
    let mut cand = vec![1i64; n];
    for i in 1..n {
        if ratings[i] > ratings[i - 1] {
            cand[i] = cand[i - 1] + 1;
        }
    }
    for i in (0..n.saturating_sub(1)).rev() {
        if ratings[i] > ratings[i + 1] {
            cand[i] = cand[i].max(cand[i + 1] + 1);
        }
    }
    cand.iter().sum()
}""",
        "espresso": r"""fn minCandies(ratings) {
  // O(1)-space mountain walk (no extra arrays needed).
  var total = 1
  var up = 0
  var down = 0
  var peak = 0
  for var i in 1..len(ratings) {
    if ratings[i] > ratings[i - 1] {
      up += 1
      peak = up
      down = 0
      total += up + 1
    } else if ratings[i] == ratings[i - 1] {
      up = 0
      down = 0
      peak = 0
      total += 1
    } else {
      up = 0
      down += 1
      total += down
      if peak < down { total += 1 }     // the peak must stay above the down slope
    }
  }
  return total
}""",
    },
    tests=_candy_tests(),
))


# ---------------------------------------------------------------------------
# 11. Task scheduler
# ---------------------------------------------------------------------------
def _ts_tests():
    r = random.Random(1411)
    t = [["AAABBB", 2], ["AAABBB", 0], ["AAAAAABCDEFG", 2], ["A", 5], ["ABCDE", 4], ["AAABBBCCC", 2],
         ["AAABBBCCCDD", 2], ["AAAA", 3], ["ABAB", 1], ["AAABBBCCCDDDEEE", 1]]
    t.append(["".join(r.choice("ABCDEFGHIJ") for _ in range(300)), 7])
    t.append(["".join(r.choice("AAAAABCD") for _ in range(500)), 3])
    t.append(["".join(r.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(2000)), 30])
    return t


PROBLEMS.append(dict(
    id="task-scheduler",
    title="Task Scheduler",
    difficulty=2,
    tags=["greedy", "counting", "math"],
    fn="least_interval",
    params=[["tasks", "str"], ["n", "int"]],
    returns="int",
    statement=r"""A CPU must run the tasks in `tasks`, a string of uppercase letters where each
letter is one unit-time task of that type. Tasks may run in any order. In each time unit the
CPU either runs one task or stays **idle**. Two tasks of the **same** type must be separated
by at least `n` time units (other tasks or idles).

Return the minimum number of time units needed to finish all tasks.""",
    example_notes=[
        "`A B idle A B idle A B`: 8 units.",
        "No cooldown: just run all 6 tasks.",
    ],
    constraints=["1 ≤ len(tasks) ≤ 10⁴", "tasks contains uppercase English letters", "0 ≤ n ≤ 100"],
    hints=[
        "The most frequent task type is the bottleneck. If `A` appears `f` times, how long is the schedule at least?",
        "Lay the `A`s out as `f - 1` frames of length `n + 1`, followed by a final partial frame. Other tasks fill the gaps in the frames.",
        "Answer = `max(len(tasks), (f - 1) * (n + 1) + k)`, where `k` is how many task types share the maximum frequency `f`.",
    ],
    explanation=r"""## Intuition

Only counts matter, not the letters themselves. The type with the highest count `f` is the
bottleneck: its instances must be at least `n + 1` apart, so the schedule is at least
`(f - 1)(n + 1) + 1` long. Picture `f - 1` **frames** of width `n + 1`, each starting with the
bottleneck task, plus a final frame:

```text
n = 2, tasks = AAABBC        f = 3 (A), k = 1
frame:  | A B C | A B _ | A
           ^ fills gaps        length = (3-1)*(2+1) + 1 = 7
```

Every other type has count `≤ f`, so it can be placed one instance per frame without
violating its own cooldown (instances of one type land in different frames, `n + 1` apart).
Types that also have count `f` need a slot in the final frame too, so the final frame has
length `k` (number of types with the max count).

If there are more tasks than gaps, the frames simply widen: then no idles are needed at all
and the answer is `len(tasks)`.

## Approach

1. Count each letter; let `f` = the max count, `k` = number of letters with count `f`.
2. Return `max(len(tasks), (f - 1) * (n + 1) + k)`.

**Trace for `"AAABBB"`, `n = 2`:** `f = 3`, `k = 2` → `(3-1)·3 + 2 = 8`; `len = 6`; answer 8:
`A B _ | A B _ | A B`.

**Trace for `"AAABBBCCCDD"`, `n = 2`:** `f = 3`, `k = 3` → `2·3 + 3 = 9 < 11 = len`.
Answer 11: e.g. `A B C D | A B C D | A B C`, frames widened, no idles.

**Why the bound is achievable when tasks overflow the frames.** Fill frames round-robin in
decreasing order of count; extra tasks just extend frames beyond `n + 1`, which only *increases*
separation. So no idle is ever needed, and `len(tasks)` is clearly a lower bound.

**Simulation alternative.** A greedy simulation with a max-heap of remaining counts: each
round of `n + 1` slots, run the `n + 1` most frequent available types, then push back the
decremented counts. It gives the same answer in O(len · log 26) and also produces an actual
schedule.

## Complexity

O(len(tasks)) to count, O(26) for the rest. O(26) space.

## Common mistakes

- **Forgetting `k`** (several types tied at the max count): `"AAABBB"`, `n = 2` gives 7
  instead of 8.
- **Forgetting the `max` with `len(tasks)`**: `"AAABBBCCCDD"` would return 9.
- **`n = 0`**: the formula gives `(f-1) + k ≤ len`, so the `max` returns `len`. Good.

## Going further

- **Rearrange string k distance apart** asks for the actual arrangement (or "impossible"):
  use the heap simulation with a cooldown queue.
- **Task scheduler II** keeps tasks in a *fixed* order; then you just simulate, tracking the
  next allowed day per type in a hash map.
""",
    solution=r"""def least_interval(tasks, n):
    counts = {}
    for t in tasks:
        counts[t] = counts.get(t, 0) + 1
    f = max(counts.values())                            # the bottleneck frequency
    k = sum(1 for c in counts.values() if c == f)       # types tied at that frequency
    # f - 1 full frames of width n + 1 (each opened by a bottleneck task), plus a last
    # frame holding one instance of every type with count f.
    framed = (f - 1) * (n + 1) + k
    # If there are more tasks than slots, frames stretch and no idling is needed at all.
    return max(len(tasks), framed)
""",
    refs={
        "cpp": r"""long long leastInterval(string tasks, long long n) {
    array<long long, 26> cnt{};
    for (char c : tasks) cnt[c - 'A']++;
    long long f = *max_element(cnt.begin(), cnt.end());
    long long k = count(cnt.begin(), cnt.end(), f);
    return max((long long)tasks.size(), (f - 1) * (n + 1) + k);
}""",
        "rust": r"""use std::collections::BinaryHeap;

pub fn least_interval(tasks: String, n: i64) -> i64 {
    // Simulation with a max-heap: each round fills up to n + 1 slots with the most
    // frequent remaining task types.
    let mut cnt = [0i64; 26];
    for b in tasks.bytes() {
        cnt[(b - b'A') as usize] += 1;
    }
    let mut heap: BinaryHeap<i64> = cnt.iter().copied().filter(|&c| c > 0).collect();
    let mut time = 0i64;
    while !heap.is_empty() {
        let mut used = Vec::new();
        let mut slots = 0i64;
        while slots <= n {
            match heap.pop() {
                Some(c) => {
                    if c > 1 {
                        used.push(c - 1);
                    }
                    slots += 1;
                }
                None => break,
            }
        }
        heap.extend(used);
        // A full round costs n + 1 (idles included) unless it was the last one.
        time += if heap.is_empty() { slots } else { n + 1 };
    }
    time
}""",
    },
    tests=_ts_tests(),
))
