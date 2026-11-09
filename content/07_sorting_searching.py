"""Track 7: Sorting & Binary Search."""
import random

TRACK = dict(
    id="sorting-searching",
    title="Sorting & Binary Search",
    order=7,
    icon="⇅",
    blurb="Build the classic sorts by hand, then master the binary-search invariant that solves half of all interview problems.",
    intro=r"""
Sorting and searching are where algorithm design gets *honest*. Every idea in this track
(loop invariants, divide and conquer, lower bounds) shows up again in harder problems, so
it pays to understand them exactly, not approximately.

## Part 1: Sorting

### Comparison sorts

A **comparison sort** learns about the data only by asking "is `a < b`?". Bubble,
insertion, merge, quick and heap sort are all comparison sorts. They differ in *how many*
questions they ask and *how much extra memory* they need:

| algorithm | best | average | worst | extra space | stable? |
|---|---|---|---|---|---|
| bubble | n (early exit) | n² | n² | 1 | yes |
| insertion | n | n² | n² | 1 | yes |
| merge | n log n | n log n | n log n | n | yes |
| quick | n log n | n log n | n² | log n (stack) | no |
| heap | n log n | n log n | n log n | 1 | no |
| counting | n + k | n + k | n + k | n + k | yes |

### Why n log n is a floor

Any comparison sort can be drawn as a binary **decision tree**: each internal node is one
comparison, each leaf one possible output ordering. There are `n!` orderings, so the tree
needs at least `n!` leaves, and a binary tree with `n!` leaves has height at least
`log₂(n!) ≈ n log₂ n − 1.44 n`. The height is the worst-case number of comparisons.
So **no comparison sort can beat Θ(n log n) in the worst case.**

```
                a<b?
              /      \
          b<c?        a<c?          3 elements → 3! = 6 leaves
         /    \       /    \        → height ≥ ⌈log₂ 6⌉ = 3 comparisons
     [a b c] a<c?  [b a c] b<c?
            /  \          /  \
      [a c b] [c a b] [b c a] [c b a]
```

Counting sort escapes the bound because it never compares: it uses the *values* as array
indices. That only works when the values come from a small known range `k`.

### Stability

A sort is **stable** if equal keys keep their original relative order. It matters when
you sort records by one field after another: sort by first name, then *stably* by last
name, and people with the same last name stay ordered by first name. Merge sort is
stable as long as the merge takes from the **left** half on ties (`<=`, not `<`).
Quicksort's long-distance swaps destroy stability.

### In place vs out of place

"In place" means O(1) (or O(log n)) extra memory. Several problems here use
`mutates`: your function receives the array and must rearrange *that* array.

```python
def sort_in_place(nums):     # caller sees the change
    nums.sort()
def sort_copy(nums):         # caller's list untouched
    return sorted(nums)
```

In C you get `long long* nums, int numsSize` and write through the pointer. In Rust you
get `&mut Vec<i64>`. In ESPresso arrays are passed by reference, so assigning
`nums[i] = ...` inside the function is visible to the caller.

## Part 2: Binary search

Binary search finds things in **sorted** (more generally, *monotone*) data in O(log n)
by halving the candidate range every step. It is famously easy to get *almost* right.
The cure is to pick one convention and reason with an **invariant**.

### The half-open convention `[lo, hi)`

```
index:   0   1   2   3   4   5   6
nums:  [ 1,  3,  3,  5,  8,  9, 12 ]
         lo                          hi = len(nums)   (one past the end)
```

**Invariant:** the answer lies in `[lo, hi)`. Everything left of `lo` is "too small",
everything at or right of `hi` is "big enough".

```python
def lower_bound(nums, target):
    lo, hi = 0, len(nums)            # answer in [lo, hi)
    while lo < hi:                   # range non-empty
        mid = (lo + hi) // 2         # lo <= mid < hi, always a valid index
        if nums[mid] < target:
            lo = mid + 1             # mid is too small, and so is everything left of it
        else:
            hi = mid                 # mid might be the answer: keep it (hi is exclusive)
    return lo                        # lo == hi: first index with nums[i] >= target
```

Rules that make this correct:

1. `mid` is strictly less than `hi`, so it is always a real index.
2. Each step **strictly shrinks** the range: `lo = mid + 1 > lo` or `hi = mid < hi`.
   No infinite loops.
3. When `lo == hi` the range is empty and `lo` is the boundary.

Trace for `target = 5` in the array above:

| lo | hi | mid | nums[mid] | action |
|---|---|---|---|---|
| 0 | 7 | 3 | 5 | `5 < 5`? no → hi = 3 |
| 0 | 3 | 1 | 3 | yes → lo = 2 |
| 2 | 3 | 2 | 3 | yes → lo = 3 |
| 3 | 3 | | | stop: answer 3 |

### The closed convention `[lo, hi]`

Also common: `lo, hi = 0, n - 1`, `while lo <= hi`, and updates `lo = mid + 1`,
`hi = mid - 1`. It is natural for "find exactly this value or report -1". Mixing the two
conventions (e.g. `hi = n` with `hi = mid - 1`) is the number-one source of binary-search
bugs.

### Binary search on the answer

The real power move: the "array" doesn't need to exist. If a predicate `ok(x)` is
**monotone** (false, false, …, false, true, true, …) you can binary search for the first
`x` where it flips. "What is the smallest eating speed that finishes in time?" is exactly
this shape. So is integer square root, and so is finding the peak of a mountain.

```
x:      1  2  3  4  5  6  7  8
ok(x):  F  F  F  T  T  T  T  T
                 ^ first true = lower_bound on the predicate
```

### Overflow

`(lo + hi) / 2` can overflow in C, C++, Rust and ESPresso (32-bit ints!) when `lo + hi`
exceeds the type's range. `lo + (hi - lo) / 2` is equivalent and safe. In Rust, indices
are `usize`, so `hi = mid - 1` with `mid == 0` panics. The half-open style avoids
ever computing `mid - 1`.

## How to work this track

The first five problems are the classic sorts: trace them on paper before coding. Then
come binary-search variants that each add one twist: exact match, insertion point, range,
answer-space search, rotated arrays, peaks. The track ends with quickselect, binary search
on the answer, and the notorious median of two sorted arrays.
""",
)


# ---------------------------------------------------------------- test helpers

def _sort_tests(seed, big_n, lo=-1000, hi=1000):
    r = random.Random(seed)
    t = [
        [[5, 2, 4, 6, 1, 3]],
        [[3, -1, 2, -1, 0]],
        [[]],
        [[42]],
        [[2, 1]],
        [[7, 7, 7, 7]],
        [list(range(1, 13))],
        [list(range(12, 0, -1))],
        [[r.randint(-5, 5) for _ in range(25)]],
        [[r.randint(lo, hi) for _ in range(big_n)]],
    ]
    return t


# ---------------------------------------------------------------- problems

BUBBLE = dict(
    id="sort-bubble",
    title="Bubble Sort",
    difficulty=1,
    tags=["sorting", "in place"],
    fn="bubble_sort",
    params=[["nums", "int[]"]],
    returns="void",
    mutates="nums",
    statement="""Sort `nums` into **non-decreasing** order, in place, using **bubble sort**.

Bubble sort makes repeated passes over the array. In each pass it walks left to right and
swaps every adjacent pair that is out of order (`nums[i] > nums[i + 1]`). After pass *p*,
the *p* largest values have "bubbled" to the end and are in their final positions. Stop
as soon as a pass makes no swaps.

Your function returns nothing; the tester inspects `nums` after the call.""",
    constraints=["0 ≤ len(nums) ≤ 300", "-10⁴ ≤ nums[i] ≤ 10⁴"],
    hints=[
        "Write one pass first: a single loop over `i` that swaps `nums[i]` and `nums[i + 1]` when they are out of order. What does the array look like after one pass?",
        "After the first pass the maximum is at the last index. After the second pass the two largest are in place. So pass `p` only needs to look at the first `n - p` elements.",
        "Keep a `swapped` flag per pass. If a full pass swaps nothing, the array is sorted and you can stop early, which makes already-sorted input O(n).",
    ],
    explanation=r"""
## Intuition

Bubble sort is the algorithm you'd invent if you could only ever look at two neighbours at
a time. If every adjacent pair is in order, the whole array is in order. So keep fixing
adjacent pairs until there is nothing left to fix. Large values travel right quickly (one
swap per step), like bubbles rising.

## Approach

1. Repeat passes `p = 0, 1, 2, …`.
2. In pass `p`, for `i` from `0` to `n - p - 2`, swap `nums[i]` and `nums[i+1]` if
   `nums[i] > nums[i+1]`.
3. Track whether any swap happened. If none did, stop.

Trace on `[5, 2, 4, 6, 1, 3]`:

| pass | array after the pass | settled suffix |
|---|---|---|
| 0 | `[2, 4, 5, 1, 3, │6]` | `6` |
| 1 | `[2, 4, 1, 3, │5, 6]` | `5 6` |
| 2 | `[2, 1, 3, │4, 5, 6]` | `4 5 6` |
| 3 | `[1, 2, │3, 4, 5, 6]` | `3 4 5 6` |
| 4 | no swaps → stop | |

Inside pass 0, the `6` doesn't move until it reaches index 3, then it carries on to the end
in one step: `5,2 → 2,5`, `5,4 → 4,5`, `5,6` (ok), `6,1 → 1,6`, `6,3 → 3,6`.

**Language mechanics.** Swapping two elements is `a, b = b, a` in Python (the right side is
built as a tuple first, so no temporary is needed), `std::swap(a[i], a[j])` in C++,
`nums.swap(i, j)` in Rust, and a three-line dance with a temporary in C and ESPresso:

```c
long long tmp = nums[i];
nums[i] = nums[i + 1];
nums[i + 1] = tmp;
```

## Complexity

- **Time:** worst case (reverse order) does `(n−1) + (n−2) + … + 1 = n(n−1)/2`
  comparisons, i.e. O(n²). With the early-exit flag, an already-sorted array costs one
  pass: O(n).
- **Space:** O(1); only a couple of loop variables.
- **Stable:** yes. We only swap on *strictly* greater, so equal neighbours never cross.

## Common mistakes

- **Reading past the end.** The inner loop compares `nums[i]` with `nums[i+1]`, so `i` must
  stop at `n - 2` (range `0..n-1` exclusive), not `n - 1`.
- **Using `>=` in the comparison.** It still sorts, but swaps equal elements, which costs
  time and breaks stability.
- **Empty array in C/Rust.** `numsSize - 1` is `-1` for an empty array; in Rust
  `nums.len() - 1` underflows a `usize` and panics. Write loops so they don't compute it,
  e.g. `for i in 1..n - p` style bounds or guard `n < 2`.
- **Forgetting it's in place.** Returning a new sorted list in Python does nothing; the
  tester reads `nums`.

## Going further

- **Cocktail shaker sort** alternates left-to-right and right-to-left passes, so small
  values near the end ("turtles") move fast too.
- Count the swaps bubble sort makes: it equals the number of **inversions** (pairs
  `i < j` with `nums[i] > nums[j]`). Merge sort can count inversions in O(n log n).
""",
    solution='''def bubble_sort(nums):
    n = len(nums)
    # After pass p, the last p elements hold the p largest values in final order,
    # so each pass can stop one position earlier than the previous one.
    for p in range(n):
        swapped = False
        # Compare each neighbour pair in the unsettled prefix nums[0 .. n-p-1].
        for i in range(n - p - 1):
            # Strictly greater: equal values never swap, which keeps the sort stable.
            if nums[i] > nums[i + 1]:
                nums[i], nums[i + 1] = nums[i + 1], nums[i]
                swapped = True
        # No swaps means every adjacent pair is ordered, so the whole array is sorted.
        if not swapped:
            break
''',
    refs={
        "c": '''void bubble_sort(long long* nums, int numsSize) {
    // Pass p settles the p-th largest value at index n-1-p.
    for (int p = 0; p < numsSize; p++) {
        bool swapped = false;
        // i + 1 < numsSize - p  keeps nums[i + 1] inside the unsettled prefix.
        for (int i = 0; i + 1 < numsSize - p; i++) {
            if (nums[i] > nums[i + 1]) {          // strictly greater: stable
                long long tmp = nums[i];          // C has no swap; use a temporary
                nums[i] = nums[i + 1];
                nums[i + 1] = tmp;
                swapped = true;
            }
        }
        if (!swapped) break;                      // already sorted: stop early
    }
}''',
        "cpp": '''void bubbleSort(vector<long long>& nums) {
    int n = nums.size();
    for (int p = 0; p < n; p++) {
        bool swapped = false;
        // Compare neighbours inside the unsettled prefix [0, n - p).
        for (int i = 0; i + 1 < n - p; i++) {
            if (nums[i] > nums[i + 1]) {
                swap(nums[i], nums[i + 1]);
                swapped = true;
            }
        }
        if (!swapped) break;   // a clean pass proves the array is sorted
    }
}''',
        "rust": '''pub fn bubble_sort(nums: &mut Vec<i64>) {
    let n = nums.len();
    for p in 0..n {
        let mut swapped = false;
        // 1..n - p never underflows because p < n; compare (i-1, i) pairs.
        for i in 1..n - p {
            if nums[i - 1] > nums[i] {
                nums.swap(i - 1, i); // Vec::swap exchanges two slots in place
                swapped = true;
            }
        }
        if !swapped {
            break;
        }
    }
}''',
        "espresso": '''fn bubbleSort(nums) {
  var n = len(nums)
  var p = 0
  var swapped = true
  // Keep making passes while the previous pass changed something.
  while swapped {
    swapped = false
    // Unsettled prefix is nums[0 .. n-p-1]; the tail is already final.
    for var i in 1..n - p {
      if nums[i - 1] > nums[i] {
        var tmp = nums[i - 1]
        nums[i - 1] = nums[i]
        nums[i] = tmp
        swapped = true
      }
    }
    p += 1
  }
}''',
    },
    tests=_sort_tests(71, 60),
)

INSERTION = dict(
    id="sort-insertion",
    title="Insertion Sort",
    difficulty=1,
    tags=["sorting", "in place"],
    fn="insertion_sort",
    params=[["nums", "int[]"]],
    returns="void",
    mutates="nums",
    statement="""Sort `nums` into non-decreasing order, in place, using **insertion sort**.

Insertion sort grows a sorted prefix one element at a time. For `i = 1, 2, …, n-1`, take
`key = nums[i]`, shift every element of the sorted prefix `nums[0..i-1]` that is
**greater than** `key` one step to the right, and drop `key` into the gap.

The tester inspects `nums` after your function returns.""",
    constraints=["0 ≤ len(nums) ≤ 300", "-10⁴ ≤ nums[i] ≤ 10⁴"],
    hints=[
        "Think of sorting a hand of playing cards: you pick up one card at a time and slide it left into place among the cards you already hold.",
        "Save `key = nums[i]` first, because shifting will overwrite `nums[i]`.",
        "Walk `j` leftwards from `i - 1` while `j >= 0` and `nums[j] > key`, copying `nums[j]` into `nums[j + 1]`. When the loop stops, the gap is at `j + 1`.",
    ],
    explanation=r"""
## Intuition

Insertion sort keeps an invariant: **the prefix `nums[0..i)` is sorted**. Initially the
prefix is one element long, which is trivially sorted. Each step takes the next element
and inserts it into the right spot in the prefix, extending it by one. When `i` reaches
`n`, the whole array is the prefix.

## Approach

```
i = 3:   [ 2  4  5 | 1  6  3 ]     key = 1
          sorted     rest
shift:   [ 2  4  5  5  6  3 ]      5 > 1, move right
         [ 2  4  4  5  6  3 ]      4 > 1, move right
         [ 2  2  4  5  6  3 ]      2 > 1, move right
drop:    [ 1  2  4  5 | 6  3 ]     j = -1, so key goes to index 0
```

Full trace on `[5, 2, 4, 6, 1, 3]` (bar = end of sorted prefix):

| i | key | after insertion |
|---|---|---|
| 1 | 2 | `[2, 5, │4, 6, 1, 3]` |
| 2 | 4 | `[2, 4, 5, │6, 1, 3]` |
| 3 | 6 | `[2, 4, 5, 6, │1, 3]` (no shifts) |
| 4 | 1 | `[1, 2, 4, 5, 6, │3]` |
| 5 | 3 | `[1, 2, 3, 4, 5, 6]` |

Shifting (copying each bigger element one slot right) is cheaper than repeated swapping:
one write per step instead of three.

**Language mechanics.** The inner loop condition `j >= 0 and nums[j] > key` relies on
**short-circuit evaluation**: when `j` is `-1`, the left test is false and `nums[-1]` is
never evaluated. In Python `nums[-1]` would silently read the *last* element, and in C it
would read out of bounds, so the order of the two tests matters. In Rust, use a `usize`
`j` that represents "the gap" and loop `while j > 0 && nums[j - 1] > key`, which never
goes negative.

## Complexity

- **Time:** O(n²) worst case (reverse-sorted: every key slides all the way left), but
  O(n + inversions) in general. On nearly sorted data it's close to linear, which is why
  real-world sorts (Timsort, introsort) switch to insertion sort for small or nearly
  sorted chunks.
- **Space:** O(1).
- **Stable:** yes, because we stop shifting at an element that is *equal* to `key`
  (`>` not `>=`), so `key` lands to the right of equal earlier elements.

## Common mistakes

- **Not saving `key`.** The first shift overwrites `nums[i]`.
- **Off-by-one on the drop.** The loop exits with `j` pointing at the first element
  that is `<= key` (or `-1`); the key goes at `j + 1`, not `j`.
- **Signed/unsigned in C.** If `j` is `size_t` the check `j >= 0` is always true. Use
  `int`.

## Going further

- **Binary insertion sort** finds the drop position with binary search: O(n log n)
  comparisons, though shifting still costs O(n²) moves.
- **Shell sort** runs insertion sort on elements `gap` apart for shrinking gaps, letting
  far-away elements move quickly; with good gap sequences it runs around O(n^1.3).
""",
    solution='''def insertion_sort(nums):
    # Invariant: nums[0:i] is sorted at the start of every iteration.
    for i in range(1, len(nums)):
        key = nums[i]          # save it: shifting below overwrites nums[i]
        j = i - 1
        # Slide every prefix element that is strictly greater than key one slot right.
        # Checking j >= 0 first stops us before nums[-1] (Python would wrap around!).
        # Stopping at equal elements keeps the sort stable.
        while j >= 0 and nums[j] > key:
            nums[j + 1] = nums[j]
            j -= 1
        # nums[j] <= key (or j == -1), so the gap left for key is at j + 1.
        nums[j + 1] = key
''',
    refs={
        "c": '''void insertion_sort(long long* nums, int numsSize) {
    for (int i = 1; i < numsSize; i++) {
        long long key = nums[i];
        int j = i - 1;                 // int, not size_t: we need j to reach -1
        // && short-circuits, so nums[-1] is never read.
        while (j >= 0 && nums[j] > key) {
            nums[j + 1] = nums[j];     // shift right, opening a gap at j
            j--;
        }
        nums[j + 1] = key;
    }
}''',
        "cpp": '''void insertionSort(vector<long long>& nums) {
    for (size_t i = 1; i < nums.size(); i++) {
        long long key = nums[i];
        size_t gap = i;                // gap = where key would go right now
        while (gap > 0 && nums[gap - 1] > key) {
            nums[gap] = nums[gap - 1]; // move the bigger element into the gap
            gap--;
        }
        nums[gap] = key;
    }
}''',
        "rust": '''pub fn insertion_sort(nums: &mut Vec<i64>) {
    for i in 1..nums.len() {
        let key = nums[i];
        // Track the gap as a usize that never goes below 0 (no underflow panic).
        let mut gap = i;
        while gap > 0 && nums[gap - 1] > key {
            nums[gap] = nums[gap - 1];
            gap -= 1;
        }
        nums[gap] = key;
    }
}''',
        "espresso": '''fn insertionSort(nums) {
  for var i in 1..len(nums) {
    var key = nums[i]
    var gap = i
    // Shift larger elements right until the gap reaches key's position.
    while gap > 0 and nums[gap - 1] > key {
      nums[gap] = nums[gap - 1]
      gap -= 1
    }
    nums[gap] = key
  }
}''',
    },
    tests=_sort_tests(72, 60),
)

MERGE = dict(
    id="sort-merge",
    title="Merge Sort",
    difficulty=2,
    tags=["sorting", "divide and conquer", "recursion"],
    fn="merge_sort",
    params=[["nums", "int[]"]],
    returns="int[]",
    statement="""Return a **new** array containing the elements of `nums` in non-decreasing order,
using **merge sort**:

1. An array of length 0 or 1 is already sorted.
2. Otherwise split it into a left half and a right half, sort each half recursively,
   and **merge** the two sorted halves into one sorted array.

Don't call your language's built-in sort; the point is to write the merge yourself.""",
    constraints=["0 ≤ len(nums) ≤ 5000", "-10⁶ ≤ nums[i] ≤ 10⁶"],
    hints=[
        "Start with `merge(a, b)`: given two *sorted* arrays, produce one sorted array. Two indices, one into each array; repeatedly take the smaller front element.",
        "When one array runs out, append everything left in the other: it's already sorted and all ≥ what you've taken.",
        "Now `merge_sort(x)` is three lines: base case, recurse on `x[:mid]` and `x[mid:]`, merge. Take from the left array on ties (`<=`) to keep the sort stable.",
    ],
    explanation=r"""
## Intuition

Merging two sorted lists is easy and linear: compare the fronts, take the smaller,
repeat. Merge sort turns sorting into merging by **divide and conquer**: split until the
pieces are trivially sorted (size 1), then merge back up.

## Approach

```
               [5 2 4 6 1 3]
              /             \
         [5 2 4]           [6 1 3]          split
         /     \           /     \
       [5]   [2 4]       [6]   [1 3]
             /   \             /   \
           [2]   [4]         [1]   [3]
             \   /             \   /
       [5]   [2 4]       [6]   [1 3]        merge
         \     /           \     /
         [2 4 5]           [1 3 6]
              \             /
               [1 2 3 4 5 6]
```

The final merge of `[2 4 5]` and `[1 3 6]`:

| i (left) | j (right) | compare | take | output |
|---|---|---|---|---|
| 2 | 1 | 2 vs 1 | 1 | `1` |
| 2 | 3 | 2 vs 3 | 2 | `1 2` |
| 4 | 3 | 4 vs 3 | 3 | `1 2 3` |
| 4 | 6 | 4 vs 6 | 4 | `1 2 3 4` |
| 5 | 6 | 5 vs 6 | 5 | `1 2 3 4 5` |
| — | 6 | left empty | 6 | `1 2 3 4 5 6` |

In C, pass a scratch buffer around instead of allocating at every level: copy the
range into the buffer, merge back into the original. That keeps allocation to one
`malloc` of size `n`.

## Complexity

- **Time:** the recursion tree has `log₂ n` levels; each level merges a total of `n`
  elements. O(n log n) in **every** case, with no bad inputs. Recurrence:
  `T(n) = 2T(n/2) + n`.
- **Space:** O(n) for the merge buffer plus O(log n) recursion depth.
- **Stable:** yes, if ties are taken from the left half (`a[i] <= b[j]`).

## Common mistakes

- **`<` instead of `<=` in the merge.** Still sorted, but no longer stable.
- **Forgetting the leftovers.** When one side runs out you must copy the rest of the
  other side.
- **Infinite recursion.** With `mid = n // 2`, an array of length 1 would split into
  `[]` and `[x]` forever if the base case is `n == 0` only. Use `n <= 1`.
- **Allocation in a hot loop (C).** `malloc` per merge is correct but slow; a single
  scratch buffer is the idiomatic fix. Remember the caller owns the returned buffer.

## Going further

- **Bottom-up merge sort** skips recursion: merge runs of width 1, 2, 4, … iteratively.
- **Counting inversions**: during the merge, each time you take from the right half,
  every element still waiting on the left is greater, so add `len(left) - i`.
- **Timsort** (Python's `sorted`, Java's object sort) is a merge sort that detects
  existing sorted runs and uses insertion sort on small runs.
- **External sorting**: when data doesn't fit in memory, sort chunks and k-way merge
  them, exactly this algorithm on disk.
""",
    solution='''def merge_sort(nums):
    # Base case: 0 or 1 elements are sorted. Returning a copy keeps the
    # contract "always return a new list" without aliasing the input.
    if len(nums) <= 1:
        return list(nums)

    # Divide: sort each half independently (this is where the log n levels come from).
    mid = len(nums) // 2
    left = merge_sort(nums[:mid])
    right = merge_sort(nums[mid:])

    # Conquer: merge two sorted lists by repeatedly taking the smaller front element.
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        # <= takes from the left on ties, so equal values keep their original order
        # (stability).
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    # Exactly one side may have leftovers; they are sorted and >= everything taken.
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged
''',
    refs={
        "c": '''// Sort a[lo, hi) using tmp as scratch space of the same size as a.
static void ms(long long* a, long long* tmp, int lo, int hi) {
    if (hi - lo <= 1) return;                 // 0 or 1 element: sorted
    int mid = lo + (hi - lo) / 2;
    ms(a, tmp, lo, mid);
    ms(a, tmp, mid, hi);
    // Merge a[lo, mid) and a[mid, hi) into tmp[lo, hi), then copy back.
    int i = lo, j = mid, k = lo;
    while (i < mid && j < hi) tmp[k++] = (a[i] <= a[j]) ? a[i++] : a[j++];
    while (i < mid) tmp[k++] = a[i++];        // left leftovers
    while (j < hi)  tmp[k++] = a[j++];        // right leftovers
    memcpy(a + lo, tmp + lo, (size_t)(hi - lo) * sizeof(long long));
}

long long* merge_sort(long long* nums, int numsSize, int* returnSize) {
    // The result is a fresh malloc-ed copy; the caller frees it.
    long long* out = malloc(sizeof(long long) * (numsSize > 0 ? numsSize : 1));
    long long* tmp = malloc(sizeof(long long) * (numsSize > 0 ? numsSize : 1));
    memcpy(out, nums, sizeof(long long) * numsSize);
    ms(out, tmp, 0, numsSize);
    free(tmp);                                // one scratch buffer for the whole sort
    *returnSize = numsSize;
    return out;
}''',
        "cpp": '''// Sort a[lo, hi) using tmp as scratch.
static void ms(vector<long long>& a, vector<long long>& tmp, size_t lo, size_t hi) {
    if (hi - lo <= 1) return;
    size_t mid = lo + (hi - lo) / 2;
    ms(a, tmp, lo, mid);
    ms(a, tmp, mid, hi);
    size_t i = lo, j = mid, k = lo;
    while (i < mid && j < hi) tmp[k++] = (a[i] <= a[j]) ? a[i++] : a[j++];
    while (i < mid) tmp[k++] = a[i++];
    while (j < hi) tmp[k++] = a[j++];
    copy(tmp.begin() + lo, tmp.begin() + hi, a.begin() + lo);
}

vector<long long> mergeSort(vector<long long>& nums) {
    vector<long long> out = nums, tmp(nums.size());   // sort a copy, not the input
    ms(out, tmp, 0, out.size());
    return out;
}''',
        "rust": '''pub fn merge_sort(nums: Vec<i64>) -> Vec<i64> {
    // Base case: we own `nums`, so we can just hand it back.
    if nums.len() <= 1 {
        return nums;
    }
    let mid = nums.len() / 2;
    let left = merge_sort(nums[..mid].to_vec());
    let right = merge_sort(nums[mid..].to_vec());

    let mut out = Vec::with_capacity(left.len() + right.len());
    let (mut i, mut j) = (0, 0);
    while i < left.len() && j < right.len() {
        if left[i] <= right[j] {      // <= keeps it stable
            out.push(left[i]);
            i += 1;
        } else {
            out.push(right[j]);
            j += 1;
        }
    }
    out.extend_from_slice(&left[i..]);  // at most one of these is non-empty
    out.extend_from_slice(&right[j..]);
    out
}''',
    },
    tests=_sort_tests(73, 60, -10**6, 10**6) + [
        [[random.Random(88).randint(-10**6, 10**6) for _ in range(3000)]],
        [[i // 7 for i in range(1500, 0, -1)]],
    ],
)

QUICK = dict(
    id="sort-quick",
    title="Quicksort",
    difficulty=2,
    tags=["sorting", "divide and conquer", "in place", "partition"],
    fn="quick_sort",
    params=[["nums", "int[]"]],
    returns="void",
    mutates="nums",
    statement="""Sort `nums` into non-decreasing order, **in place**, using **quicksort**.

Quicksort picks a *pivot* value, **partitions** the array so that everything in a left
part is `≤ pivot` and everything in a right part is `≥ pivot`, then sorts the two parts
recursively. Don't call a built-in sort.

The tests include already-sorted arrays, reverse-sorted arrays and arrays where every
value is the same: a careless pivot or partition scheme turns those into O(n²) work or
blows the call stack.""",
    constraints=["0 ≤ len(nums) ≤ 5000", "-10⁶ ≤ nums[i] ≤ 10⁶"],
    hints=[
        "Pick the **middle** element's value as pivot. Choosing the first or last element is O(n²) on sorted input.",
        "Hoare partition: `i` starts left of the range and moves right while `nums[i] < pivot`; `j` starts right of the range and moves left while `nums[j] > pivot`. If `i < j`, swap and continue; otherwise `j` is the split point: `[lo..j]` and `[j+1..hi]`.",
        "Hoare stops *on* elements equal to the pivot and swaps them, so an all-equal array splits in half instead of degenerating.",
        "To bound the recursion depth to O(log n), recurse only into the **smaller** part and loop on the larger one.",
    ],
    explanation=r"""
## Intuition

Merge sort does its work *after* the recursive calls (merging). Quicksort does it
*before*: once the array is partitioned around a pivot, the left part and right part
never need to interact again, so they can be sorted independently, with no merge step and
no extra array.

## Approach

**Hoare partition** of `nums[lo..hi]` (inclusive) with `pivot = nums[(lo+hi)//2]`:

```
i = lo - 1, j = hi + 1
loop:
    do i++ while nums[i] < pivot      # stop at something >= pivot
    do j-- while nums[j] > pivot      # stop at something <= pivot
    if i >= j: return j               # pointers crossed: split after j
    swap(nums[i], nums[j])            # both were on the wrong side
```

When it returns, every element of `nums[lo..j]` is `≤` every element of `nums[j+1..hi]`.
The pivot itself may land in either part; that's fine.

Trace on `[5, 2, 4, 6, 1, 3]`, `pivot = nums[2] = 4`:

| step | i stops at | j stops at | action | array |
|---|---|---|---|---|
| 1 | 0 (`5 ≥ 4`) | 5 (`3 ≤ 4`) | swap | `[3, 2, 4, 6, 1, 5]` |
| 2 | 2 (`4 ≥ 4`) | 4 (`1 ≤ 4`) | swap | `[3, 2, 1, 6, 4, 5]` |
| 3 | 3 (`6 ≥ 4`) | 2 (`1 ≤ 4`) | crossed → return 2 | |

Left part `[3, 2, 1]`, right part `[6, 4, 5]`: every left value ≤ every right value.

**Why the middle pivot is safe here:** with `pivot` at index `⌊(lo+hi)/2⌋ < hi`, the
returned `j` is always `< hi`, so both parts are non-empty and recursion makes progress.
(If you choose `nums[hi]` as a Hoare pivot you can get `j == hi` and loop forever.)

**Bounding the stack:** after partitioning, recurse into the smaller part and `while`-loop
on the larger. The smaller part is at most half the range, so the depth is ≤ log₂ n
even in the worst case. This matters a lot for ESPresso, whose call stack is shallow.

## Complexity

- **Time:** O(n log n) on average: a reasonable pivot splits the range into
  constant fractions, giving `log n` levels of O(n) partitioning. Worst case O(n²) if
  every pivot is extreme; random or median-of-three pivots make that vanishingly rare.
- **Space:** O(log n) stack with the smaller-side trick; no auxiliary array.
- **Stable:** no. Swaps move elements past equal ones.

In practice quicksort is usually the fastest comparison sort thanks to tight inner loops
and cache-friendly sequential scans. `std::sort` in C++ is *introsort*: quicksort that
switches to heapsort if recursion gets too deep, and to insertion sort for tiny ranges.

## Common mistakes

- **Lomuto partition on duplicates.** The textbook "last element pivot, single `i`
  pointer" scheme puts all equal elements on one side: an all-equal array becomes
  O(n²) with depth n. Hoare (or three-way partitioning) avoids it.
- **Recursing on `[lo..j-1]` and `[j+1..hi]` with Hoare.** That's the Lomuto split. Hoare
  doesn't put the pivot at `j`; you must recurse on `[lo..j]` and `[j+1..hi]`.
- **`<=`/`>=` in the scanning loops.** Then the pointers can run off the end of the range
  (nothing stops them) and equal elements no longer split evenly.
- **Unsigned indices.** `j = hi + 1` then `j--` is fine, but `i = lo - 1` with `lo = 0`
  underflows a `usize`. Use signed types (`i64`/`isize`) for the pointers in Rust.

## Going further

- **Three-way partitioning** (Dutch national flag) splits into `< pivot`, `= pivot`,
  `> pivot`, making arrays with many duplicates linear.
- **Quickselect** reuses the partition step but recurses into only *one* side to find
  the k-th smallest element in O(n) average time. You'll use it later in this track.
""",
    solution='''def quick_sort(nums):
    def partition(lo, hi):
        # Hoare partition of nums[lo..hi] (inclusive). The middle element's value is
        # the pivot: sorted and reverse-sorted inputs then split evenly.
        pivot = nums[(lo + hi) // 2]
        i, j = lo - 1, hi + 1
        while True:
            # Advance i to the first element that belongs on the right (>= pivot).
            i += 1
            while nums[i] < pivot:
                i += 1
            # Retreat j to the first element that belongs on the left (<= pivot).
            j -= 1
            while nums[j] > pivot:
                j -= 1
            # Crossed: everything in [lo..j] <= everything in [j+1..hi].
            if i >= j:
                return j
            # Both are on the wrong side; swapping fixes both at once.
            # Elements equal to the pivot get swapped too, which is what keeps
            # all-equal arrays balanced.
            nums[i], nums[j] = nums[j], nums[i]

    def sort(lo, hi):
        # Loop on the larger part and recurse on the smaller one, so the recursion
        # depth is at most log2(n) even when pivots are unlucky.
        while lo < hi:
            p = partition(lo, hi)
            if p - lo < hi - p:
                sort(lo, p)
                lo = p + 1
            else:
                sort(p + 1, hi)
                hi = p

    sort(0, len(nums) - 1)
''',
    refs={
        "c": '''// Hoare partition of a[lo..hi] inclusive; returns j with a[lo..j] <= a[j+1..hi].
static int partition(long long* a, int lo, int hi) {
    long long pivot = a[lo + (hi - lo) / 2];
    int i = lo - 1, j = hi + 1;
    for (;;) {
        do i++; while (a[i] < pivot);
        do j--; while (a[j] > pivot);
        if (i >= j) return j;
        long long t = a[i]; a[i] = a[j]; a[j] = t;
    }
}

static void qs(long long* a, int lo, int hi) {
    while (lo < hi) {
        int p = partition(a, lo, hi);
        // Recurse on the smaller side, iterate on the larger: depth <= log2(n).
        if (p - lo < hi - p) { qs(a, lo, p); lo = p + 1; }
        else                 { qs(a, p + 1, hi); hi = p; }
    }
}

void quick_sort(long long* nums, int numsSize) {
    qs(nums, 0, numsSize - 1);   // empty array: lo=0 > hi=-1, nothing happens
}''',
        "cpp": '''static long long hoare(vector<long long>& a, long long lo, long long hi) {
    long long pivot = a[lo + (hi - lo) / 2];
    long long i = lo - 1, j = hi + 1;
    while (true) {
        do i++; while (a[i] < pivot);
        do j--; while (a[j] > pivot);
        if (i >= j) return j;
        swap(a[i], a[j]);
    }
}

static void qs(vector<long long>& a, long long lo, long long hi) {
    while (lo < hi) {
        long long p = hoare(a, lo, hi);
        if (p - lo < hi - p) { qs(a, lo, p); lo = p + 1; }
        else                 { qs(a, p + 1, hi); hi = p; }
    }
}

void quickSort(vector<long long>& nums) {
    qs(nums, 0, (long long)nums.size() - 1);
}''',
        "rust": '''// Signed indices: Hoare starts i at lo - 1, which would underflow a usize.
fn partition(a: &mut Vec<i64>, lo: i64, hi: i64) -> i64 {
    let pivot = a[((lo + hi) / 2) as usize];
    let (mut i, mut j) = (lo - 1, hi + 1);
    loop {
        i += 1;
        while a[i as usize] < pivot { i += 1; }
        j -= 1;
        while a[j as usize] > pivot { j -= 1; }
        if i >= j {
            return j;
        }
        a.swap(i as usize, j as usize);
    }
}

fn sort(a: &mut Vec<i64>, mut lo: i64, mut hi: i64) {
    while lo < hi {
        let p = partition(a, lo, hi);
        if p - lo < hi - p {
            sort(a, lo, p);
            lo = p + 1;
        } else {
            sort(a, p + 1, hi);
            hi = p;
        }
    }
}

pub fn quick_sort(nums: &mut Vec<i64>) {
    let n = nums.len() as i64;
    sort(nums, 0, n - 1);
}''',
        "espresso": '''// Hoare partition; returns j such that a[lo..j] <= a[j+1..hi].
fn partition(a, lo, hi) {
  var pivot = a[lo + (hi - lo) / 2]
  var i = lo - 1
  var j = hi + 1
  while true {
    i += 1
    while a[i] < pivot { i += 1 }
    j -= 1
    while a[j] > pivot { j -= 1 }
    if i >= j { return j }
    var t = a[i]
    a[i] = a[j]
    a[j] = t
  }
}

// ESPresso's call stack is shallow, so recurse only into the smaller part.
fn qs(a, lo, hi) {
  while lo < hi {
    var p = partition(a, lo, hi)
    if p - lo < hi - p {
      qs(a, lo, p)
      lo = p + 1
    } else {
      qs(a, p + 1, hi)
      hi = p
    }
  }
}

fn quickSort(nums) {
  qs(nums, 0, len(nums) - 1)
}''',
    },
    tests=_sort_tests(74, 30, -10**6, 10**6) + [
        [list(range(40))],
        [[5] * 30],
        [[(i * 37) % 11 for i in range(30)]],
    ],
)

COUNTING = dict(
    id="sort-counting",
    title="Counting Sort",
    difficulty=1,
    tags=["sorting", "counting", "non-comparison"],
    fn="counting_sort",
    params=[["nums", "int[]"]],
    returns="int[]",
    statement="""Return the elements of `nums` sorted in non-decreasing order using **counting sort**.

Every value is guaranteed to lie in the small range **-1000 ≤ value ≤ 1000**. Instead of
comparing elements, count how many times each value occurs, then write the values out in
order according to their counts.

Your solution should run in O(n + k) time where k = 2001 is the size of the value range.""",
    constraints=["0 ≤ len(nums) ≤ 10⁴", "-1000 ≤ nums[i] ≤ 1000"],
    hints=[
        "Make an array `count` with one slot per possible value. Values can be negative, so you need an offset to turn a value into an index.",
        "`count[v + 1000] += 1` for each `v`. Index 0 now means value -1000 and index 2000 means value 1000.",
        "Walk the count array from index 0 to 2000 and emit `index - 1000` exactly `count[index]` times.",
    ],
    explanation=r"""
## Intuition

The n log n lower bound only applies to algorithms that learn the order by *comparing*.
When values are small integers, we can use each value directly as an **array index**: a
"bucket" for that exact value. Counting needs no comparisons at all.

## Approach

1. Allocate `count[0..2000]` (2001 zeros).
2. For each `v` in `nums`: `count[v + OFFSET] += 1`, where `OFFSET = 1000` shifts
   `-1000..1000` to `0..2000`.
3. Sweep `idx` from 0 to 2000 and append `idx - OFFSET` to the output `count[idx]` times.

Trace on `[3, -1, 2, -1, 0]` (showing only non-zero counts):

```
value:   -1   0   2   3
count:    2   1   1   1
output:  -1 -1   0   2   3
```

**Language mechanics.** In C, `calloc(2001, sizeof(int))` gives a zero-initialised
array; `malloc` does not (its contents are garbage). In Rust, `vec![0usize; 2001]` and
index with `(v + 1000) as usize`; the cast is required because indices must be
`usize`. In C++, `vector<int> cnt(2001)` value-initialises to zeros.

### The stable version (prefix sums)

When you sort *records* by a key (not bare integers), you can't just regenerate values
from counts; you must move the actual records. The stable variant turns counts into
starting positions with a prefix sum:

```python
pos = [0] * K
for k in range(1, K):
    pos[k] = pos[k - 1] + count[k - 1]   # first output slot for key k
for x in records:                         # left to right ⇒ stable
    out[pos[key(x)]] = x
    pos[key(x)] += 1
```

That stable pass is the building block of **radix sort**, which sorts multi-digit
numbers digit by digit, least significant first.

## Complexity

- **Time:** O(n + k): one pass to count, one sweep over the `k = 2001` buckets.
- **Space:** O(k) for the counts plus the O(n) output.
- When `k` is much larger than `n` (say values up to 10⁹), counting sort is terrible:
  the count array alone is gigabytes. Then use a comparison sort or radix sort.

## Common mistakes

- **Forgetting the offset** and indexing with a negative number: Python silently
  counts into the wrong bucket (`count[-1]` is the last slot!), C reads out of bounds.
- **Sizing the array 2000 instead of 2001.** The range `-1000..1000` has 2001 values.
- **Uninitialised memory in C** (`malloc` without zeroing).
- **Empty input.** `malloc(0)` may return `NULL` in C; still set `*returnSize = 0`.

## Going further

- **Radix sort** (LSD): run a stable counting sort on each base-256 digit; sorts 64-bit
  integers in 8 linear passes.
- **Bucket sort** generalises to real numbers spread evenly over a range: drop them into
  `n` buckets, sort each tiny bucket, concatenate.
""",
    solution='''def counting_sort(nums):
    OFFSET = 1000            # maps value -1000 to index 0 and value 1000 to index 2000
    K = 2001                 # number of distinct possible values
    count = [0] * K
    # One pass: tally each value in its own bucket. No comparisons at all.
    for v in nums:
        count[v + OFFSET] += 1
    # Sweep buckets in increasing value order; each bucket emits its value count times.
    out = []
    for idx in range(K):
        if count[idx]:
            out.extend([idx - OFFSET] * count[idx])
    return out
''',
    refs={
        "c": '''long long* counting_sort(long long* nums, int numsSize, int* returnSize) {
    enum { OFFSET = 1000, K = 2001 };
    int* count = calloc(K, sizeof(int));          // calloc zero-fills; malloc doesn't
    for (int i = 0; i < numsSize; i++) count[nums[i] + OFFSET]++;
    long long* out = malloc(sizeof(long long) * (numsSize > 0 ? numsSize : 1));
    int k = 0;
    for (int idx = 0; idx < K; idx++)
        for (int c = 0; c < count[idx]; c++) out[k++] = idx - OFFSET;
    free(count);
    *returnSize = numsSize;
    return out;
}''',
        "cpp": '''vector<long long> countingSort(vector<long long>& nums) {
    const int OFFSET = 1000, K = 2001;
    vector<int> cnt(K);                     // value-initialised to zeros
    for (long long v : nums) cnt[v + OFFSET]++;
    vector<long long> out;
    out.reserve(nums.size());
    for (int idx = 0; idx < K; idx++)
        out.insert(out.end(), cnt[idx], idx - OFFSET);   // cnt[idx] copies
    return out;
}''',
        "rust": '''pub fn counting_sort(nums: Vec<i64>) -> Vec<i64> {
    const OFFSET: i64 = 1000;
    let mut count = vec![0usize; 2001];
    for &v in &nums {
        count[(v + OFFSET) as usize] += 1;   // indices must be usize
    }
    let mut out = Vec::with_capacity(nums.len());
    for (idx, &c) in count.iter().enumerate() {
        for _ in 0..c {
            out.push(idx as i64 - OFFSET);
        }
    }
    out
}''',
    },
    tests=[
        [[3, -1, 2, -1, 0]],
        [[1000, -1000, 0]],
        [[]],
        [[7]],
        [[5, 5, 5, 5, 5]],
        [list(range(10, -11, -1))],
        [[random.Random(75).randint(-1000, 1000) for _ in range(5000)]],
        [[random.Random(76).randint(-3, 3) for _ in range(500)]],
    ],
)

BINSEARCH = dict(
    id="binary-search-classic",
    title="Binary Search",
    difficulty=1,
    tags=["binary search"],
    fn="binary_search",
    params=[["nums", "int[]"], ["target", "int"]],
    returns="int",
    statement="""`nums` is sorted in **strictly increasing** order (all values distinct). Return the
index of `target` in `nums`, or `-1` if it isn't there.

Your algorithm must run in O(log n) time.""",
    constraints=["0 ≤ len(nums) ≤ 10⁴", "-10⁴ ≤ nums[i], target ≤ 10⁴", "values in `nums` are distinct and sorted ascending"],
    hints=[
        "Look at the middle element. If it's bigger than the target, can the target be anywhere to its right?",
        "Keep a range `[lo, hi]` that still might contain the target. Each step, compare with `nums[mid]` and throw away the half that can't contain it.",
        "With the closed range: `while lo <= hi`, `mid = lo + (hi - lo) // 2`; equal → return mid; less → `lo = mid + 1`; greater → `hi = mid - 1`. Loop ends with `lo > hi`: not found.",
    ],
    explanation=r"""
## Intuition

"Sorted" plus "O(log n)" is a neon sign for binary search. One comparison against the
middle element tells you which half the target must be in (if anywhere), so you can
discard the other half without looking at it. Halving 10⁴ elements reaches 1 in about 14
steps.

## Approach

Use the **closed** interval `[lo, hi]`. Invariant: *if `target` is in `nums`, its index
is in `[lo, hi]`*.

```
lo, hi = 0, n - 1
while lo <= hi:                  # range non-empty
    mid = lo + (hi - lo) // 2
    if nums[mid] == target: return mid
    if nums[mid] < target:  lo = mid + 1   # target is right of mid
    else:                   hi = mid - 1   # target is left of mid
return -1                         # range empty
```

Trace: `nums = [-1, 0, 3, 5, 9, 12]`, `target = 9`

| lo | hi | mid | nums[mid] | action |
|---|---|---|---|---|
| 0 | 5 | 2 | 3 | 3 < 9 → lo = 3 |
| 3 | 5 | 4 | 9 | found → return 4 |

With `target = 2`:

| lo | hi | mid | nums[mid] | action |
|---|---|---|---|---|
| 0 | 5 | 2 | 3 | 3 > 2 → hi = 1 |
| 0 | 1 | 0 | -1 | -1 < 2 → lo = 1 |
| 1 | 1 | 1 | 0 | 0 < 2 → lo = 2 |
| 2 | 1 | | | lo > hi → return -1 |

**Language mechanics.** `//` in Python is floor division; `/` on two integers in C, C++,
Rust and ESPresso truncates, which is the same thing for non-negative numbers. In Rust,
`hi = mid - 1` is a trap: indices are `usize`, and when `mid == 0` it underflows and
panics in debug builds. The Rust reference uses the half-open range `[lo, hi)` (with
`hi = mid`) to sidestep it.

## Complexity

- **Time:** O(log n); the range halves each step.
- **Space:** O(1).

## Common mistakes

- **`while lo < hi` with a closed range** misses the last candidate when `lo == hi`.
- **`lo = mid` or `hi = mid` with a closed range** can loop forever when `hi = lo + 1`
  (mid equals lo, nothing changes).
- **`(lo + hi) / 2` overflow** in fixed-width integers. Here the numbers are small, but
  the habit `lo + (hi - lo) / 2` is free.
- **Empty array.** `hi = -1`, the loop never runs, answer `-1`. Make sure your language
  doesn't choke computing `n - 1` (Rust `usize`!).

## Going further

- Python's `bisect.bisect_left` and C++'s `std::lower_bound` implement the half-open
  variant; `std::binary_search` only tells you *whether* a value exists.
- **Exponential search** for unbounded/infinite sorted data: probe indices 1, 2, 4, 8, …
  until you overshoot, then binary search inside the last gap.
""",
    solution='''def binary_search(nums, target):
    # Closed interval [lo, hi]: if target exists, its index is somewhere in here.
    lo, hi = 0, len(nums) - 1
    while lo <= hi:                      # non-empty while lo <= hi
        mid = lo + (hi - lo) // 2        # overflow-safe midpoint habit
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            # nums[mid] and everything left of it are too small.
            lo = mid + 1
        else:
            # nums[mid] and everything right of it are too large.
            hi = mid - 1
    # The interval became empty: target is not in the array.
    return -1
''',
    refs={
        "c": '''long long binary_search(long long* nums, int numsSize, long long target) {
    int lo = 0, hi = numsSize - 1;          // closed interval [lo, hi]
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] == target) return mid;
        if (nums[mid] < target) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}''',
        "cpp": '''long long binarySearch(vector<long long>& nums, long long target) {
    // std::lower_bound is the half-open search; check whether it landed on target.
    auto it = lower_bound(nums.begin(), nums.end(), target);
    if (it != nums.end() && *it == target) return it - nums.begin();
    return -1;
}''',
        "rust": '''pub fn binary_search(nums: Vec<i64>, target: i64) -> i64 {
    // Half-open [lo, hi): never computes mid - 1, so no usize underflow.
    let (mut lo, mut hi) = (0usize, nums.len());
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        if nums[mid] == target {
            return mid as i64;
        } else if nums[mid] < target {
            lo = mid + 1;
        } else {
            hi = mid;          // exclusive bound: mid is excluded
        }
    }
    -1
}''',
        "espresso": '''fn binarySearch(nums, target) {
  var lo = 0
  var hi = len(nums) - 1
  while lo <= hi {
    var mid = lo + (hi - lo) / 2
    if nums[mid] == target {
      return mid
    } else if nums[mid] < target {
      lo = mid + 1
    } else {
      hi = mid - 1
    }
  }
  return -1
}''',
    },
    tests=[
        [[-1, 0, 3, 5, 9, 12], 9],
        [[-1, 0, 3, 5, 9, 12], 2],
        [[], 5],
        [[5], 5],
        [[5], -5],
        [[1, 3, 5, 7], 1],
        [[1, 3, 5, 7], 7],
        [[1, 3, 5, 7], 8],
        [[1, 3, 5, 7], 0],
        [list(range(-100, 100, 3)), 98],
        [list(range(-100, 40, 3)), 99],
    ],
)

SEARCH_INSERT = dict(
    id="search-insert-position",
    title="Search Insert Position",
    difficulty=1,
    tags=["binary search", "lower bound"],
    fn="search_insert",
    params=[["nums", "int[]"], ["target", "int"]],
    returns="int",
    statement="""`nums` is sorted in strictly increasing order. Return the index of `target` if it is
present; otherwise return the index where it **would be inserted** to keep the array
sorted.

Equivalently: return the number of elements strictly less than `target`. Run in
O(log n).""",
    constraints=["0 ≤ len(nums) ≤ 10⁴", "-10⁴ ≤ nums[i], target ≤ 10⁴", "values distinct, ascending"],
    hints=[
        "The answer is the first index `i` with `nums[i] >= target`, or `len(nums)` if there is none.",
        "Use the half-open range `[lo, hi)` with `hi = len(nums)`. The answer can be `len(nums)`, which is exactly why `hi` starts one past the end.",
        "`nums[mid] < target` → `lo = mid + 1`; otherwise `hi = mid`. Return `lo` when the loop ends.",
    ],
    explanation=r"""
## Intuition

"Where would it go?" is the **lower bound** question: find the boundary between
"elements smaller than target" and "elements at least target". The predicate
`nums[i] >= target` is monotone across a sorted array, `F F F T T T`, and we want the
first `T`. If the target is present, the first `T` *is* the target; if absent, it's the
slot where the target belongs.

## Approach

```
lo, hi = 0, len(nums)        # answer in [lo, hi], hi may itself be the answer
while lo < hi:
    mid = (lo + hi) // 2
    if nums[mid] < target:   # F region: answer is right of mid
        lo = mid + 1
    else:                    # T region: mid could be the answer
        hi = mid
return lo
```

Trace: `nums = [1, 3, 5, 6]`, `target = 2`

| lo | hi | mid | nums[mid] < 2? | action |
|---|---|---|---|---|
| 0 | 4 | 2 | 5: no | hi = 2 |
| 0 | 2 | 1 | 3: no | hi = 1 |
| 0 | 1 | 0 | 1: yes | lo = 1 |
| 1 | 1 | | | return 1 |

`target = 7`: every comparison says "yes", `lo` climbs to 4 = `len(nums)`: append at the
end. `target = 0`: every comparison says "no", `hi` falls to 0.

Why `hi = mid` and not `mid - 1`? Because `mid` passed the test `nums[mid] >= target`,
so it's a *candidate*. Throwing it away could discard the answer.

## Complexity

- **Time:** O(log n).
- **Space:** O(1).

## Common mistakes

- **Starting with `hi = len(nums) - 1`.** Then the answer `len(nums)` (insert at the
  end) can never be returned.
- **Mixing conventions**: `while lo <= hi` with `hi = mid` loops forever once `lo == hi`.
- **Linear scan.** Passes small tests, but it's the O(n) solution to an O(log n) problem.

## Going further

- `bisect.bisect_left(nums, target)` in Python and `lower_bound` in C++ return exactly
  this. `bisect_right`/`upper_bound` return the first index with `nums[i] > target`.
  With duplicates, the pair gives the full range of equal elements, which is the next
  problem.
- Inserting via `list.insert` is still O(n) because of shifting; balanced trees or skip
  lists give O(log n) insertion *and* search.
""",
    solution='''def search_insert(nums, target):
    # Half-open search for the first index whose value is >= target.
    # hi starts at len(nums) because "insert at the very end" is a valid answer.
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2           # lo <= mid < hi, always a real index
        if nums[mid] < target:
            lo = mid + 1               # mid and everything left of it are too small
        else:
            hi = mid                   # mid is a candidate; keep it in range
    # lo == hi is the boundary: count of elements smaller than target.
    return lo
''',
    refs={
        "c": '''long long search_insert(long long* nums, int numsSize, long long target) {
    int lo = 0, hi = numsSize;               // [lo, hi), hi may be the answer
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] < target) lo = mid + 1;
        else hi = mid;
    }
    return lo;
}''',
        "cpp": '''long long searchInsert(vector<long long>& nums, long long target) {
    return lower_bound(nums.begin(), nums.end(), target) - nums.begin();
}''',
        "rust": '''pub fn search_insert(nums: Vec<i64>, target: i64) -> i64 {
    // partition_point returns the first index where the predicate turns false.
    nums.partition_point(|&x| x < target) as i64
}''',
        "espresso": '''fn searchInsert(nums, target) {
  var lo = 0
  var hi = len(nums)
  while lo < hi {
    var mid = lo + (hi - lo) / 2
    if nums[mid] < target {
      lo = mid + 1
    } else {
      hi = mid
    }
  }
  return lo
}''',
    },
    tests=[
        [[1, 3, 5, 6], 5],
        [[1, 3, 5, 6], 2],
        [[1, 3, 5, 6], 7],
        [[1, 3, 5, 6], 0],
        [[], 3],
        [[4], 4],
        [[4], 9],
        [list(range(0, 120, 2)), 59],
        [list(range(0, 80, 2)), 40],
    ],
)


def _range_tests():
    r = random.Random(77)
    big = sorted(r.randint(0, 300) for _ in range(5000))
    return [
        [[5, 7, 7, 8, 8, 10], 8],
        [[5, 7, 7, 8, 8, 10], 6],
        [[], 0],
        [[1], 1],
        [[2, 2, 2, 2], 2],
        [[1, 2, 3], 4],
        [[1, 2, 3], 1],
        [[1, 2, 3], 3],
        [big, big[2500]],
        [big, 301],
        [big, 0],
    ]


FIRST_LAST = dict(
    id="first-last-position-sorted",
    title="First and Last Position in Sorted Array",
    difficulty=2,
    tags=["binary search", "lower bound", "upper bound"],
    fn="search_range",
    params=[["nums", "int[]"], ["target", "int"]],
    returns="int[]",
    statement="""`nums` is sorted in non-decreasing order and **may contain duplicates**. Return
`[first, last]`: the smallest and largest indices `i` with `nums[i] == target`. If
`target` does not occur, return `[-1, -1]`.

Run in O(log n), even when the array is one long run of `target`.""",
    constraints=["0 ≤ len(nums) ≤ 10⁵", "-10⁹ ≤ nums[i], target ≤ 10⁹"],
    hints=[
        "Finding *some* occurrence and then walking left and right is O(n) in the worst case (all elements equal).",
        "Two separate binary searches: the first index with `nums[i] >= target`, and the first index with `nums[i] > target`.",
        "If the first search lands at `n` or at a value other than `target`, it's absent. Otherwise the answer is `[lower, upper - 1]`.",
    ],
    explanation=r"""
## Intuition

A run of equal values in a sorted array has two edges. Each edge is a **boundary
between a false and a true region** of a monotone predicate:

```
nums:          5  7  7  8  8  10
>= 8 ?         F  F  F  T  T  T     first T = 3   (lower bound)
>  8 ?         F  F  F  F  F  T     first T = 5   (upper bound)
range of 8:          [3, 5 - 1] = [3, 4]
```

So you need just one routine, "first index where predicate flips", called twice.

## Approach

Write `lower_bound(x)` = first `i` with `nums[i] >= x` (half-open search). Then:

- `lo = lower_bound(target)`
- if `lo == n` or `nums[lo] != target` → `[-1, -1]`
- `hi = lower_bound(target + 1)` (for integers, `>= target + 1` is the same as
  `> target`)
- answer `[lo, hi - 1]`

Using `target + 1` is a neat integer trick; the more general way is a second routine
`upper_bound` with `<=` in place of `<`. Both appear in the references.

Trace `lower_bound(8)` on `[5, 7, 7, 8, 8, 10]`:

| lo | hi | mid | nums[mid] < 8? | |
|---|---|---|---|---|
| 0 | 6 | 3 | 8: no | hi = 3 |
| 0 | 3 | 1 | 7: yes | lo = 2 |
| 2 | 3 | 2 | 7: yes | lo = 3 |
| 3 | 3 | | | → 3 |

`lower_bound(9)` walks to 5, so the answer is `[3, 4]`.

## Complexity

- **Time:** O(log n): two binary searches, regardless of how long the run is.
- **Space:** O(1).

## Common mistakes

- **Find-then-expand** is O(n) on `[2, 2, 2, …, 2]`. That test exists.
- **Returning `[lo, hi]` instead of `[lo, hi - 1]`.** `hi` is one past the last match.
- **Checking `nums[lo]` without checking `lo < n`** first: out-of-bounds when the target
  is bigger than everything.
- **`target + 1` overflow** in fixed-width types when target is the max value. Not an
  issue with i64 and these constraints, but `upper_bound` with `<=` avoids it entirely.
- **C return arrays:** allocate 2 slots with `malloc` and set `*returnSize = 2`.

## Going further

- Count occurrences of `target` in O(log n): `upper - lower`.
- C++ `std::equal_range` returns both bounds in one call; Python has `bisect_left` /
  `bisect_right`; Rust has `partition_point`.
""",
    solution='''def search_range(nums, target):
    def first_at_least(x):
        # Half-open lower bound: first index with nums[i] >= x (or len(nums)).
        lo, hi = 0, len(nums)
        while lo < hi:
            mid = (lo + hi) // 2
            if nums[mid] < x:
                lo = mid + 1
            else:
                hi = mid
        return lo

    first = first_at_least(target)
    # Absent if the boundary is past the end or lands on a different value.
    if first == len(nums) or nums[first] != target:
        return [-1, -1]
    # For integers, "first index >= target + 1" is "first index > target",
    # i.e. one past the last copy of target.
    last = first_at_least(target + 1) - 1
    return [first, last]
''',
    refs={
        "c": '''// First index in [0, n) with nums[i] >= x (strict == false) or nums[i] > x (strict == true).
static int bound(long long* nums, int n, long long x, bool strict) {
    int lo = 0, hi = n;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        bool go_right = strict ? (nums[mid] <= x) : (nums[mid] < x);
        if (go_right) lo = mid + 1; else hi = mid;
    }
    return lo;
}

long long* search_range(long long* nums, int numsSize, long long target, int* returnSize) {
    long long* out = malloc(2 * sizeof(long long));
    *returnSize = 2;
    int lo = bound(nums, numsSize, target, false);
    if (lo == numsSize || nums[lo] != target) { out[0] = out[1] = -1; return out; }
    out[0] = lo;
    out[1] = bound(nums, numsSize, target, true) - 1;   // last copy = upper bound - 1
    return out;
}''',
        "cpp": '''vector<long long> searchRange(vector<long long>& nums, long long target) {
    // equal_range = {lower_bound, upper_bound} in one call.
    auto [lo, hi] = equal_range(nums.begin(), nums.end(), target);
    if (lo == hi) return {-1, -1};                 // empty range: not present
    return {lo - nums.begin(), (hi - nums.begin()) - 1};
}''',
        "rust": '''pub fn search_range(nums: Vec<i64>, target: i64) -> Vec<i64> {
    let lo = nums.partition_point(|&x| x < target);   // first >= target
    let hi = nums.partition_point(|&x| x <= target);  // first >  target
    if lo == hi {
        vec![-1, -1]
    } else {
        vec![lo as i64, hi as i64 - 1]
    }
}''',
    },
    tests=_range_tests(),
)

SQRT = dict(
    id="integer-sqrt-binary-search",
    title="Integer Square Root",
    difficulty=1,
    tags=["binary search", "math", "binary search on answer"],
    fn="my_sqrt",
    params=[["x", "int"]],
    returns="int",
    statement="""Given a non-negative integer `x`, return `⌊√x⌋`, the largest integer `r` with
`r * r ≤ x`.

Don't use any built-in square-root or power function. Watch out: `x` can be as large as
2³¹ − 1, so `r * r` for a careless `r` can overflow a 32-bit integer.""",
    constraints=["0 ≤ x ≤ 2³¹ − 1"],
    hints=[
        "The predicate `r * r ≤ x` is true for small `r` and false for large `r`. You're looking for the last `r` where it's true.",
        "The answer is never larger than `x / 2 + 1`, which gives you a safe upper bound.",
        "Search `[lo, hi]` with `mid = lo + (hi - lo + 1) / 2` (round **up**). If `mid <= x / mid`, set `lo = mid`; else `hi = mid - 1`. Comparing with `x / mid` avoids computing `mid * mid`.",
    ],
    explanation=r"""
## Intuition

There's no array here, yet this is a binary search. The candidates `0, 1, 2, …` with
the test "is `r² ≤ x`?" form a monotone sequence:

```
x = 8
r:        0  1  2  3  4  5
r*r <= 8: T  T  T  F  F  F
                ^ last true = 2
```

Binary searching over a **range of possible answers** (not an array) is called *binary
search on the answer*, a pattern you'll use again for Koko and many optimisation problems.

## Approach

Search for the **last true**, so the update rules mirror lower bound:

```
lo, hi = 0, x // 2 + 1        # answer is inside [lo, hi]
while lo < hi:
    mid = lo + (hi - lo + 1) // 2   # round UP
    if mid <= x // mid:  lo = mid   # mid works; answer is mid or bigger
    else:                hi = mid - 1
return lo
```

**Why round up?** With `lo = mid` as an update, if `hi = lo + 1` and `mid` rounded down to
`lo`, then `lo = mid` changes nothing and the loop never ends. Rounding up makes
`mid > lo`, so both branches shrink the range. Rule of thumb: *whichever side assigns
`= mid`, round the midpoint toward the other side.*

**Why `mid <= x // mid`?** For positive integers, `mid ≤ ⌊x / mid⌋ ⇔ mid² ≤ x`, and the
division can't overflow. `mid ≥ 1` inside the loop because it's rounded up from
`lo ≥ 0`, so there's no division by zero.

Trace, `x = 8`, starting `lo = 0, hi = 5`:

| lo | hi | mid | 8 // mid | mid ≤ ? | action |
|---|---|---|---|---|---|
| 0 | 5 | 3 | 2 | no | hi = 2 |
| 0 | 2 | 1 | 8 | yes | lo = 1 |
| 1 | 2 | 2 | 4 | yes | lo = 2 |
| 2 | 2 | | | | return 2 |

**Upper bound.** `√x ≤ x/2 + 1` for all `x ≥ 0` (since `(√x − 1)² ≥ 0`). It keeps
`hi − lo + 1` small enough for 32-bit arithmetic, which matters in ESPresso.

## Complexity

- **Time:** O(log x), about 31 iterations for the largest input.
- **Space:** O(1).

## Common mistakes

- **Overflow.** `mid * mid` with `mid ≈ 10⁹` overflows 32-bit ints (ESPresso, C `int`).
  Either compare `mid <= x / mid` or use 64-bit arithmetic.
- **Infinite loop** from rounding the midpoint down while using `lo = mid`.
- **`x = 0` and `x = 1`.** Check that your bounds handle them (division by `mid = 0`).
- **Floating point** `int(x ** 0.5)` can be off by one for large perfect squares
  (rounding error), and it's not allowed here anyway.

## Going further

- **Newton's method** `r ← (r + x / r) / 2` converges quadratically: about 5 iterations
  for 32-bit inputs. With integer division it converges to `⌊√x⌋` if you start above the
  root and stop when `r * r <= x`.
- Generalise to `⌊x^(1/k)⌋`: same binary search, just a different monotone test.
""",
    solution='''def my_sqrt(x):
    # The answer r satisfies r*r <= x < (r+1)*(r+1). Since sqrt(x) <= x/2 + 1 for
    # every x >= 0, [0, x//2 + 1] is guaranteed to contain it.
    lo, hi = 0, x // 2 + 1
    # Invariant: the answer is in [lo, hi]. Stop when one candidate remains.
    while lo < hi:
        # Round the midpoint UP: the "yes" branch assigns lo = mid, and rounding
        # down could leave lo unchanged forever when hi == lo + 1.
        mid = lo + (hi - lo + 1) // 2
        # mid >= 1 here, so dividing is safe. mid <= x // mid  <=>  mid*mid <= x,
        # and it never forms the big product (matters in 32/64-bit languages).
        if mid <= x // mid:
            lo = mid           # mid is feasible; the answer is mid or larger
        else:
            hi = mid - 1       # mid is too big; so is everything above it
    return lo
''',
    refs={
        "c": '''long long my_sqrt(long long x) {
    long long lo = 0, hi = x / 2 + 1;
    while (lo < hi) {
        long long mid = lo + (hi - lo + 1) / 2;   // round up: lo = mid must make progress
        if (mid <= x / mid) lo = mid;              // mid*mid <= x without overflow
        else hi = mid - 1;
    }
    return lo;
}''',
        "cpp": '''long long mySqrt(long long x) {
    long long lo = 0, hi = x / 2 + 1;
    while (lo < hi) {
        long long mid = lo + (hi - lo + 1) / 2;
        if (mid <= x / mid) lo = mid;
        else hi = mid - 1;
    }
    return lo;
}''',
        "rust": '''pub fn my_sqrt(x: i64) -> i64 {
    let (mut lo, mut hi) = (0i64, x / 2 + 1);
    while lo < hi {
        let mid = lo + (hi - lo + 1) / 2;
        if mid <= x / mid {
            lo = mid;
        } else {
            hi = mid - 1;
        }
    }
    lo
}''',
        "espresso": '''fn mySqrt(x) {
  // ESPresso ints are 32-bit: never form mid * mid, and keep hi small.
  var lo = 0
  var hi = x / 2 + 1
  while lo < hi {
    var mid = lo + (hi - lo + 1) / 2
    if mid <= x / mid {
      lo = mid
    } else {
      hi = mid - 1
    }
  }
  return lo
}''',
    },
    tests=[[8], [4], [0], [1], [2], [3], [15], [16], [17], [2147395599], [2147395600], [2147483647], [1000000]],
)


def _rotated(seed, n, k):
    r = random.Random(seed)
    base = sorted(r.sample(range(-10**4, 10**4), n))
    return base[k:] + base[:k]


ROTATED_SEARCH = dict(
    id="search-rotated-sorted-array",
    title="Search in Rotated Sorted Array",
    difficulty=2,
    tags=["binary search", "rotated array"],
    fn="search_rotated",
    params=[["nums", "int[]"], ["target", "int"]],
    returns="int",
    statement="""An array of **distinct** integers was sorted ascending and then **rotated** at an
unknown pivot: `[0, 1, 2, 4, 5, 6, 7]` might have become `[4, 5, 6, 7, 0, 1, 2]`. (It may
also not be rotated at all.)

Given the rotated array `nums` and a `target`, return the index of `target` or `-1` if
absent. Run in O(log n).""",
    constraints=["1 ≤ len(nums) ≤ 5000", "-10⁴ ≤ nums[i], target ≤ 10⁴", "all values distinct"],
    hints=[
        "Pick any `mid`. At least one of the halves `[lo..mid]` and `[mid..hi]` is sorted normally. How can you tell which one by looking at just two values?",
        "If `nums[lo] <= nums[mid]`, the left half is sorted. Then the target is in the left half exactly when `nums[lo] <= target < nums[mid]`.",
        "Otherwise the right half is sorted, and the target is in it exactly when `nums[mid] < target <= nums[hi]`. Discard the other half.",
    ],
    explanation=r"""
## Intuition

A rotated sorted array is two sorted runs glued together, with a single "drop" where the
largest value is followed by the smallest:

```
index:  0  1  2  3  4  5  6
nums:   4  5  6  7  0  1  2
        └─ run A ─┘  └ run B ┘
```

Ordinary binary search fails because "target > nums[mid]" no longer means "go right".
But cut at any `mid`, and the drop is on *at most one* side, so **one half is always a
normal sorted range**. For a sorted range you *can* answer "is the target inside?" with
two comparisons. If yes, go there; if no, it must be in the other half.

## Approach

Closed interval `[lo, hi]`:

1. `mid = (lo + hi) // 2`; if `nums[mid] == target`, done.
2. If `nums[lo] <= nums[mid]`: left half `[lo..mid]` is sorted.
   - If `nums[lo] <= target < nums[mid]`: `hi = mid - 1`; else `lo = mid + 1`.
3. Else the right half `[mid..hi]` is sorted.
   - If `nums[mid] < target <= nums[hi]`: `lo = mid + 1`; else `hi = mid - 1`.

Trace: `nums = [4, 5, 6, 7, 0, 1, 2]`, `target = 0`

| lo | hi | mid | nums[mid] | sorted half | target inside? | action |
|---|---|---|---|---|---|---|
| 0 | 6 | 3 | 7 | left `4..7` | 0 in [4, 7)? no | lo = 4 |
| 4 | 6 | 5 | 1 | left `0..1` | 0 in [0, 1)? yes | hi = 4 |
| 4 | 4 | 4 | 0 | | found | return 4 |

The `<=` in `nums[lo] <= nums[mid]` matters: when `lo == mid` (two elements left), the
"left half" is the single element `nums[lo]`, which is trivially sorted.

## Complexity

- **Time:** O(log n): constant work per halving.
- **Space:** O(1).

## Common mistakes

- **Strict `<` in `nums[lo] < nums[mid]`.** With `lo == mid` it wrongly declares the left
  side unsorted and then tests the right half's bounds, which can skip the answer.
- **Half-open bounds on the sorted side.** The range check must exclude `nums[mid]`
  (already compared) and include the far endpoint: `nums[lo] <= target < nums[mid]`.
- **Two-step approach done carelessly.** Finding the rotation point first, then searching
  the right run, is a fine alternative, but it's easy to mishandle the "not rotated"
  case.
- **Duplicates.** With duplicates (`[1, 1, 1, 0, 1]`), `nums[lo] == nums[mid]` tells you
  nothing and the worst case becomes O(n). This problem promises distinct values.

## Going further

- **Search in Rotated Sorted Array II** allows duplicates: when `nums[lo] == nums[mid]
  == nums[hi]`, shrink both ends by one and continue.
- The next problem finds the rotation point itself (the minimum).
""",
    solution='''def search_rotated(nums, target):
    lo, hi = 0, len(nums) - 1          # closed interval [lo, hi]
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        # The "drop" (where the rotation happened) is on at most one side of mid,
        # so at least one half is an ordinary sorted range.
        if nums[lo] <= nums[mid]:
            # Left half nums[lo..mid] is sorted (<= covers lo == mid).
            # For a sorted range, membership is just a bounds check.
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            # Right half nums[mid..hi] is sorted.
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1
''',
    refs={
        "cpp": '''long long searchRotated(vector<long long>& nums, long long target) {
    long long lo = 0, hi = (long long)nums.size() - 1;
    while (lo <= hi) {
        long long mid = lo + (hi - lo) / 2;
        if (nums[mid] == target) return mid;
        if (nums[lo] <= nums[mid]) {                        // left half sorted
            if (nums[lo] <= target && target < nums[mid]) hi = mid - 1;
            else lo = mid + 1;
        } else {                                            // right half sorted
            if (nums[mid] < target && target <= nums[hi]) lo = mid + 1;
            else hi = mid - 1;
        }
    }
    return -1;
}''',
        "rust": '''pub fn search_rotated(nums: Vec<i64>, target: i64) -> i64 {
    // Signed bounds so hi = mid - 1 can safely reach -1.
    let (mut lo, mut hi) = (0i64, nums.len() as i64 - 1);
    while lo <= hi {
        let mid = lo + (hi - lo) / 2;
        let (l, m, h) = (nums[lo as usize], nums[mid as usize], nums[hi as usize]);
        if m == target {
            return mid;
        }
        if l <= m {
            if l <= target && target < m { hi = mid - 1; } else { lo = mid + 1; }
        } else {
            if m < target && target <= h { lo = mid + 1; } else { hi = mid - 1; }
        }
    }
    -1
}''',
        "espresso": '''fn searchRotated(nums, target) {
  var lo = 0
  var hi = len(nums) - 1
  while lo <= hi {
    var mid = lo + (hi - lo) / 2
    if nums[mid] == target { return mid }
    if nums[lo] <= nums[mid] {
      // left half sorted
      if nums[lo] <= target and target < nums[mid] {
        hi = mid - 1
      } else {
        lo = mid + 1
      }
    } else {
      // right half sorted
      if nums[mid] < target and target <= nums[hi] {
        lo = mid + 1
      } else {
        hi = mid - 1
      }
    }
  }
  return -1
}''',
    },
    tests=[
        [[4, 5, 6, 7, 0, 1, 2], 0],
        [[4, 5, 6, 7, 0, 1, 2], 3],
        [[1], 0],
        [[1], 1],
        [[3, 1], 1],
        [[1, 3], 3],
        [[5, 1, 3], 5],
        [[1, 2, 3, 4, 5, 6], 4],
        [[6, 1, 2, 3, 4, 5], 6],
        [_rotated(78, 40, 13), _rotated(78, 40, 13)[39]],
        [_rotated(78, 40, 13), _rotated(78, 40, 13)[0]],
        [_rotated(79, 31, 29), 10001],
    ],
)

ROTATED_MIN = dict(
    id="min-in-rotated-sorted-array",
    title="Find Minimum in Rotated Sorted Array",
    difficulty=2,
    tags=["binary search", "rotated array"],
    fn="find_min_rotated",
    params=[["nums", "int[]"]],
    returns="int",
    statement="""A sorted array of **distinct** integers was rotated some number of times (possibly
zero). Return its **minimum** element in O(log n) time.""",
    constraints=["1 ≤ len(nums) ≤ 5000", "-10⁴ ≤ nums[i] ≤ 10⁴", "all values distinct"],
    hints=[
        "The minimum is the first element of the second sorted run, right after the 'drop'. Compare `nums[mid]` with something that tells you which run `mid` is in.",
        "Compare with the **last** element of the current range, `nums[hi]`. If `nums[mid] > nums[hi]`, the drop is to the right of `mid`.",
        "`nums[mid] > nums[hi]` → `lo = mid + 1`; otherwise `hi = mid` (mid could be the minimum). Loop while `lo < hi`; return `nums[lo]`.",
    ],
    explanation=r"""
## Intuition

Define the predicate `P(i) = nums[i] <= nums[n-1]`. Every element of the first run (the
big values) is greater than the last element; every element of the second run is at most
the last element:

```
nums:          4  5  6  7  0  1  2
<= last (2)?   F  F  F  F  T  T  T
                           ^ first true = the minimum
```

Monotone predicate, first true ⇒ half-open-style binary search. For the not-rotated
array every `P(i)` is true and the answer is index 0. It just works.

## Approach

```
lo, hi = 0, n - 1
while lo < hi:
    mid = (lo + hi) // 2
    if nums[mid] > nums[hi]:   # mid in the high run: minimum strictly right
        lo = mid + 1
    else:                      # mid in the low run: minimum at mid or left
        hi = mid
return nums[lo]
```

Comparing with `nums[hi]` (the current range's end) rather than the fixed `nums[n-1]` is
equivalent and slightly more robust.

Trace on `[4, 5, 6, 7, 0, 1, 2]`:

| lo | hi | mid | nums[mid] vs nums[hi] | action |
|---|---|---|---|---|
| 0 | 6 | 3 | 7 > 2 | lo = 4 |
| 4 | 6 | 5 | 1 ≤ 2 | hi = 5 |
| 4 | 5 | 4 | 0 ≤ 1 | hi = 4 |
| 4 | 4 | | | return 0 |

**Why not compare with `nums[lo]`?** If `nums[mid] > nums[lo]`, the left part is sorted,
but the minimum could be `nums[lo]` itself (array not rotated) *or* far to the right.
Comparing with `nums[lo]` doesn't separate the cases; comparing with `nums[hi]` does.

## Complexity

- **Time:** O(log n).
- **Space:** O(1).

## Common mistakes

- **`hi = mid - 1` in the else-branch.** `mid` might *be* the minimum.
- **`while lo <= hi`** with `hi = mid` loops forever when `lo == hi`.
- **Comparing with `nums[0]`.** Breaks on unrotated input unless special-cased.
- **Linear scan** works but defeats the purpose.

## Going further

- The index of the minimum equals the **rotation count**: how many times the array was
  rotated right.
- With duplicates, `nums[mid] == nums[hi]` is ambiguous: `hi -= 1` is the safe move,
  making the worst case O(n) (e.g. `[1, 1, 1, 0, 1, 1]`).
- Once you know the rotation point, a rotated array can be searched with an index map
  `real = (i + k) % n` and plain binary search.
""",
    solution='''def find_min_rotated(nums):
    lo, hi = 0, len(nums) - 1
    # Invariant: the minimum's index is in [lo, hi].
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            # mid is in the high run: the drop (and the minimum) is strictly
            # to the right of mid.
            lo = mid + 1
        else:
            # nums[mid..hi] is ascending, so the minimum is at mid or left of it.
            hi = mid
    return nums[lo]
''',
    refs={
        "c": '''long long find_min_rotated(long long* nums, int numsSize) {
    int lo = 0, hi = numsSize - 1;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] > nums[hi]) lo = mid + 1;   // drop is right of mid
        else hi = mid;                            // mid may be the minimum
    }
    return nums[lo];
}''',
        "cpp": '''long long findMinRotated(vector<long long>& nums) {
    size_t lo = 0, hi = nums.size() - 1;
    while (lo < hi) {
        size_t mid = lo + (hi - lo) / 2;
        if (nums[mid] > nums[hi]) lo = mid + 1;
        else hi = mid;
    }
    return nums[lo];
}''',
        "rust": '''pub fn find_min_rotated(nums: Vec<i64>) -> i64 {
    let last = *nums.last().unwrap();
    // First index whose value is <= the last element: start of the low run.
    let i = nums.partition_point(|&x| x > last);
    nums[i]
}''',
        "espresso": '''fn findMinRotated(nums) {
  var lo = 0
  var hi = len(nums) - 1
  while lo < hi {
    var mid = lo + (hi - lo) / 2
    if nums[mid] > nums[hi] {
      lo = mid + 1
    } else {
      hi = mid
    }
  }
  return nums[lo]
}''',
    },
    tests=[
        [[3, 4, 5, 1, 2]],
        [[4, 5, 6, 7, 0, 1, 2]],
        [[11, 13, 15, 17]],
        [[1]],
        [[2, 1]],
        [[1, 2]],
        [[5, 1, 2, 3, 4]],
        [[2, 3, 4, 5, 1]],
        [_rotated(80, 50, 27)],
        [_rotated(81, 49, 48)],
    ],
)


def _mountain(seed, up, down):
    r = random.Random(seed)
    vals = r.sample(range(-10**4, 10**4), up + down + 1)
    peak = max(vals)
    vals.remove(peak)
    left = sorted(vals[:up])
    right = sorted(vals[up:], reverse=True)
    return left + [peak] + right


PEAK = dict(
    id="find-peak-element-unimodal",
    title="Find the Peak of a Mountain",
    difficulty=2,
    tags=["binary search", "binary search on answer"],
    fn="find_peak",
    params=[["nums", "int[]"]],
    returns="int",
    statement="""`nums` is **unimodal**: it strictly increases up to a single maximum and then strictly
decreases. Either side may be empty, so a strictly increasing array (peak at the last
index) or a strictly decreasing array (peak at index 0) are both allowed.

Return the **index** of the maximum in O(log n) time. Because there is exactly one peak,
the answer is unique.""",
    constraints=["1 ≤ len(nums) ≤ 10⁴", "-10⁴ ≤ nums[i] ≤ 10⁴", "nums[i] ≠ nums[i+1]"],
    hints=[
        "The array isn't sorted, so what can one comparison tell you? Try comparing `nums[mid]` with its right neighbour `nums[mid + 1]`.",
        "If `nums[mid] < nums[mid + 1]`, you're on the uphill slope: the peak is strictly to the right. Otherwise you're on the downhill (or at the peak): it's at `mid` or to the left.",
        "That's a monotone predicate `nums[i] > nums[i + 1]` (F F F T T T), and the peak is its first true. Use `lo < hi`, `lo = mid + 1` / `hi = mid`.",
    ],
    explanation=r"""
## Intuition

Binary search needs a *monotone yes/no question*, not a sorted array. Walk along a
mountain and ask at each step "does the path go **down** from here?":

```
index:              0   1   2   3   4   5
nums:               1   3   8  12   4   2
nums[i] > nums[i+1]? F  F   F   T   T   (T)   ← last index treated as true
                                ^ first true = the peak (index 3)
```

On the uphill slope the answer is always "no", from the peak on it's always "yes". So the
peak is the first "yes", which binary search finds in O(log n).

## Approach

```
lo, hi = 0, n - 1
while lo < hi:                 # at least two candidates
    mid = (lo + hi) // 2       # mid < hi, so mid + 1 is a valid index
    if nums[mid] < nums[mid + 1]:
        lo = mid + 1           # uphill: peak strictly right
    else:
        hi = mid               # downhill or peak: peak at mid or left
return lo
```

Note `mid + 1` never goes out of bounds: `mid ≤ hi − 1` whenever `lo < hi`.

Trace on `[1, 3, 8, 12, 4, 2]`:

| lo | hi | mid | nums[mid], nums[mid+1] | action |
|---|---|---|---|---|
| 0 | 5 | 2 | 8 < 12 | lo = 3 |
| 3 | 5 | 4 | 4 > 2 | hi = 4 |
| 3 | 4 | 3 | 12 > 4 | hi = 3 |
| 3 | 3 | | | return 3 |

## Complexity

- **Time:** O(log n).
- **Space:** O(1).

## Common mistakes

- **Reading `nums[mid + 1]` with a closed `while lo <= hi` loop**: when `lo == hi == n-1`
  this is out of bounds.
- **Comparing with `nums[mid - 1]`** while rounding `mid` down: `mid` can equal `lo = 0`,
  so `mid - 1` is `-1`.
- **Forgetting monotone edge cases**: strictly increasing (answer `n - 1`) and strictly
  decreasing (answer `0`). Both are in the tests.
- **Linear scan for the max** is O(n). Correct, but not what's asked.

## Going further

- **LeetCode 162 "Find Peak Element"** drops the single-peak guarantee: any local
  maximum counts. The *same* algorithm still returns a valid peak, because if
  `nums[mid] < nums[mid+1]` there must be a peak on the right (the values can't rise
  forever). It just isn't unique, which is why this version guarantees one peak.
- **Ternary search** finds the maximum of a unimodal *function over the reals* by
  comparing two interior points.
- **Search in a mountain array**: find the peak, then binary search the ascending side,
  then the descending side (with reversed comparisons).
""",
    solution='''def find_peak(nums):
    # The predicate "nums[i] > nums[i+1]" (downhill from i) is False on the uphill
    # slope and True from the peak onward. The peak is its first True.
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2          # mid < hi, so mid + 1 is always in bounds
        if nums[mid] < nums[mid + 1]:
            # Still climbing: the peak is strictly to the right of mid.
            lo = mid + 1
        else:
            # Descending (or at the top): the peak is mid or somewhere left.
            hi = mid
    return lo
''',
    refs={
        "cpp": '''long long findPeak(vector<long long>& nums) {
    size_t lo = 0, hi = nums.size() - 1;
    while (lo < hi) {
        size_t mid = lo + (hi - lo) / 2;
        if (nums[mid] < nums[mid + 1]) lo = mid + 1;  // uphill
        else hi = mid;                                // downhill or the peak
    }
    return lo;
}''',
        "rust": '''pub fn find_peak(nums: Vec<i64>) -> i64 {
    let (mut lo, mut hi) = (0usize, nums.len() - 1);
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        if nums[mid] < nums[mid + 1] {
            lo = mid + 1;
        } else {
            hi = mid;
        }
    }
    lo as i64
}''',
        "espresso": '''fn findPeak(nums) {
  var lo = 0
  var hi = len(nums) - 1
  while lo < hi {
    var mid = lo + (hi - lo) / 2
    if nums[mid] < nums[mid + 1] {
      lo = mid + 1
    } else {
      hi = mid
    }
  }
  return lo
}''',
    },
    tests=[
        [[1, 3, 8, 12, 4, 2]],
        [[0, 10, 5, 2]],
        [[7]],
        [[1, 2]],
        [[2, 1]],
        [list(range(-15, 15))],
        [list(range(15, -15, -1))],
        [_mountain(82, 30, 19)],
        [_mountain(83, 3, 25)],
        [_mountain(84, 30, 1)],
    ],
)


def _kth_tests():
    r = random.Random(85)
    big = [r.randint(-10**4, 10**4) for _ in range(50)]
    return [
        [[3, 2, 1, 5, 6, 4], 2],
        [[3, 2, 3, 1, 2, 4, 5, 5, 6], 4],
        [[1], 1],
        [[2, 1], 2],
        [[7, 7, 7, 7], 3],
        [[-1, -5, 3, 0], 4],
        [big, 1],
        [big, 25],
        [big, 50],
        [list(range(30)), 17],
        [[9] * 20, 10],
    ]


KTH = dict(
    id="kth-largest-element-quickselect",
    title="Kth Largest Element",
    difficulty=2,
    tags=["quickselect", "heap", "partition"],
    fn="find_kth_largest",
    params=[["nums", "int[]"], ["k", "int"]],
    returns="int",
    statement="""Return the **k-th largest** element of `nums` (counting duplicates: in
`[3, 3, 2]` the 1st and 2nd largest are both `3`).

Aim for better than sorting: O(n) average with **quickselect**, or O(n log k) with a
heap. You may rearrange `nums`.""",
    constraints=["1 ≤ k ≤ len(nums) ≤ 10⁴", "-10⁴ ≤ nums[i] ≤ 10⁴"],
    hints=[
        "The k-th largest is the element that would sit at index `n - k` if the array were sorted ascending.",
        "Heap option: keep a min-heap of the k largest seen so far; whenever it grows past k, pop the smallest. The root at the end is the answer.",
        "Quickselect: partition around a pivot (as in quicksort). Only one side can contain index `n - k`; continue in that side only, iteratively.",
        "With Hoare partition returning `p` (so `[lo..p] <= [p+1..hi]`): if `n - k <= p` set `hi = p`, else `lo = p + 1`. Stop when `lo == hi`.",
    ],
    explanation=r"""
## Intuition

Sorting answers *every* order question at once, which is overkill when you want one
order statistic. Quicksort's partition step already tells you which side of the pivot
each element belongs on, so after one partition you know whether the target position
`n - k` is on the left or the right, and the other side can be **ignored forever**. That's
quickselect: quicksort that recurses into only one side.

## Approach

### Quickselect (Hoare partition, iterative)

```
target = n - k                   # index in ascending order
lo, hi = 0, n - 1
while lo < hi:
    p = partition(lo, hi)        # nums[lo..p] <= nums[p+1..hi]
    if target <= p: hi = p       # answer lies in the left block
    else:           lo = p + 1   # answer lies in the right block
return nums[lo]
```

When the range shrinks to one slot, that slot is position `target`, and everything to its
left is ≤ it and everything to its right is ≥ it, so it holds the right value.

Trace: `nums = [3, 2, 1, 5, 6, 4]`, `k = 2` → `target = 4`

| lo | hi | pivot | after partition | p | action |
|---|---|---|---|---|---|
| 0 | 5 | 1 (index 2) | `[1, 2, 3, 5, 6, 4]` | 0 | 4 > 0 → lo = 1 |
| 1 | 5 | 5 (index 3) | `[1, 2, 3, 4, 6, 5]` | 3 | 4 > 3 → lo = 4 |
| 4 | 5 | 6 (index 4) | `[1, 2, 3, 4, 5, 6]` | 4 | 4 ≤ 4 → hi = 4 |
| 4 | 4 | | | | return `nums[4] = 5` |

### Heap alternative

```python
import heapq
heap = []
for x in nums:
    heapq.heappush(heap, x)
    if len(heap) > k:
        heapq.heappop(heap)     # drop the smallest: it can't be in the top k
return heap[0]                  # smallest of the k largest = k-th largest
```

O(n log k) time, O(k) space, and it doesn't modify the input. It also works on a
*stream* where you can't hold everything in memory.

## Complexity

- **Quickselect:** each partition costs O(size of range), and on average the range
  shrinks by a constant factor: `n + n/2 + n/4 + … = 2n`, so **O(n) average**. Worst case
  O(n²) with consistently terrible pivots (rare with a middle or random pivot). O(1)
  extra space iteratively.
- **Heap:** O(n log k) time, O(k) space.
- **Sort:** O(n log n), simplest and often fine in practice.

## Common mistakes

- **Off by one on the target index.** k-th *largest* is index `n - k` ascending, not
  `k` or `k - 1`.
- **Lomuto partition with many duplicates** (`[9, 9, 9, …]`) degrades to O(n²). Hoare
  splits equal elements evenly; that test is included.
- **Using a max-heap of everything** and popping k times: O(n + k log n). That's actually
  fine, but the min-heap-of-size-k trick is the one to remember.
- **C++ `priority_queue`** is a *max*-heap by default; use `greater<>` for a min-heap.

## Going further

- **Median of medians** picks a pivot guaranteed to be in the middle 30–70%, making
  quickselect **O(n) worst case**. It's mostly of theoretical interest.
- `std::nth_element` in C++ is quickselect (introselect) and leaves `nums[n-k]` in its
  sorted position.
- **Top-k frequent elements** combines a hash map with exactly this heap pattern.
""",
    solution='''def find_kth_largest(nums, k):
    # k-th largest == the value at index n - k once sorted ascending.
    target = len(nums) - k

    def partition(lo, hi):
        # Hoare partition (see Quicksort): afterwards nums[lo..j] <= nums[j+1..hi].
        pivot = nums[(lo + hi) // 2]
        i, j = lo - 1, hi + 1
        while True:
            i += 1
            while nums[i] < pivot:
                i += 1
            j -= 1
            while nums[j] > pivot:
                j -= 1
            if i >= j:
                return j
            nums[i], nums[j] = nums[j], nums[i]

    lo, hi = 0, len(nums) - 1
    # Invariant: position `target` lies in [lo, hi], everything left of lo is <=
    # everything in range, and everything right of hi is >= it.
    while lo < hi:
        p = partition(lo, hi)
        # Keep only the block that contains the target position; the other block
        # never needs to be looked at again. That is the whole saving over sorting.
        if target <= p:
            hi = p
        else:
            lo = p + 1
    return nums[lo]
''',
    refs={
        "cpp": '''long long findKthLargest(vector<long long>& nums, long long k) {
    // Min-heap holding the k largest values seen so far.
    priority_queue<long long, vector<long long>, greater<long long>> heap;
    for (long long x : nums) {
        heap.push(x);
        if ((long long)heap.size() > k) heap.pop();   // evict the smallest
    }
    return heap.top();   // smallest of the top k = k-th largest
}''',
        "rust": '''use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn find_kth_largest(nums: Vec<i64>, k: i64) -> i64 {
    // BinaryHeap is a max-heap; wrapping values in Reverse turns it into a min-heap.
    let mut heap = BinaryHeap::new();
    for x in nums {
        heap.push(Reverse(x));
        if heap.len() as i64 > k {
            heap.pop();
        }
    }
    heap.peek().unwrap().0
}''',
        "c": '''// Quickselect with Hoare partition, iterative (no recursion needed).
long long find_kth_largest(long long* nums, int numsSize, long long k) {
    int target = numsSize - (int)k, lo = 0, hi = numsSize - 1;
    while (lo < hi) {
        long long pivot = nums[lo + (hi - lo) / 2];
        int i = lo - 1, j = hi + 1;
        for (;;) {
            do i++; while (nums[i] < pivot);
            do j--; while (nums[j] > pivot);
            if (i >= j) break;
            long long t = nums[i]; nums[i] = nums[j]; nums[j] = t;
        }
        // nums[lo..j] <= nums[j+1..hi]: keep the side holding `target`.
        if (target <= j) hi = j; else lo = j + 1;
    }
    return nums[lo];
}''',
        "espresso": '''fn findKthLargest(nums, k) {
  var target = len(nums) - k
  var lo = 0
  var hi = len(nums) - 1
  while lo < hi {
    // Hoare partition of nums[lo..hi]
    var pivot = nums[lo + (hi - lo) / 2]
    var i = lo - 1
    var j = hi + 1
    var crossed = false
    while !crossed {
      i += 1
      while nums[i] < pivot { i += 1 }
      j -= 1
      while nums[j] > pivot { j -= 1 }
      if i >= j {
        crossed = true
      } else {
        var t = nums[i]
        nums[i] = nums[j]
        nums[j] = t
      }
    }
    if target <= j {
      hi = j
    } else {
      lo = j + 1
    }
  }
  return nums[lo]
}''',
    },
    tests=_kth_tests(),
)


def _koko_tests():
    r = random.Random(86)
    big = [r.randint(1, 10**9) for _ in range(30)]
    return [
        [[3, 6, 7, 11], 8],
        [[30, 11, 23, 4, 20], 5],
        [[30, 11, 23, 4, 20], 6],
        [[1], 1],
        [[1000000000], 2],
        [[1000000000], 1000000000],
        [[5, 5, 5], 3],
        [[5, 5, 5], 1000],
        [big, 30],
        [big, 10**9],
        [big, 123456],
    ]


KOKO = dict(
    id="koko-eating-bananas",
    title="Koko Eating Bananas",
    difficulty=2,
    tags=["binary search", "binary search on answer"],
    fn="min_eating_speed",
    params=[["piles", "int[]"], ["h", "int"]],
    returns="int",
    statement="""Koko has `piles[i]` bananas in pile `i` and the guards return in `h` hours.

She picks an integer eating speed `k ≥ 1` (bananas per hour). Each hour she chooses one
pile and eats `k` bananas from it; if the pile has fewer than `k`, she finishes that
pile and does nothing else that hour. So pile `p` takes `⌈p / k⌉` hours.

Return the **minimum** `k` that lets her finish every pile within `h` hours. It is
guaranteed that `len(piles) ≤ h`, so an answer always exists.""",
    constraints=["1 ≤ len(piles) ≤ 10⁴", "len(piles) ≤ h ≤ 10⁹", "1 ≤ piles[i] ≤ 10⁹"],
    hints=[
        "If speed `k` is fast enough, is `k + 1` also fast enough? What does that tell you about the set of good speeds?",
        "The answer lies in `[1, max(piles)]`: at speed `max(piles)` every pile takes exactly one hour, which fits because `len(piles) ≤ h`.",
        "Binary search for the first `k` with `hours(k) <= h`, where `hours(k) = Σ ⌈p / k⌉`. Compute the ceiling with integer arithmetic: `(p + k - 1) // k`, or `(p - 1) // k + 1` to dodge overflow.",
    ],
    explanation=r"""
## Intuition

We're not searching *in* an array; we're searching the **space of possible answers**.
The key observation: eating faster never takes longer. `hours(k)` is non-increasing in
`k`, so the predicate `hours(k) ≤ h` looks like

```
k:            1  2  3  4  5  6  7 ...
hours(k)<=8?  F  F  F  T  T  T  T      (piles = [3, 6, 7, 11])
                       ^ minimum good speed = 4
```

Any time a problem says "find the minimum X such that something is achievable", and
feasibility is monotone in X, think **binary search on the answer**.

## Approach

1. `lo = 1`, `hi = max(piles)`. `hi` is always feasible.
2. While `lo < hi`: `mid = (lo + hi) // 2`. If `hours(mid) <= h`, `hi = mid` (feasible,
   maybe there's slower); else `lo = mid + 1`.
3. Return `lo`.

`hours(k)` costs O(n). Trace for `piles = [3, 6, 7, 11]`, `h = 8`:

| lo | hi | mid | hours = ⌈3/m⌉+⌈6/m⌉+⌈7/m⌉+⌈11/m⌉ | ≤ 8? | action |
|---|---|---|---|---|---|
| 1 | 11 | 6 | 1+1+2+2 = 6 | yes | hi = 6 |
| 1 | 6 | 3 | 1+2+3+4 = 10 | no | lo = 4 |
| 4 | 6 | 5 | 1+2+2+3 = 8 | yes | hi = 5 |
| 4 | 5 | 4 | 1+2+2+3 = 8 | yes | hi = 4 |
| 4 | 4 | | | | return 4 |

**Integer ceiling.** `⌈p / k⌉ = (p + k − 1) // k` for positive integers. In 32-bit
arithmetic `p + k − 1` can overflow (both up to 10⁹), so `(p − 1) // k + 1` is the safe
form (valid since `p ≥ 1`).

**Early exit.** The total hours can reach 10⁴ · 10⁹ = 10¹³, beyond 32 bits. Since we only
need to know whether it exceeds `h`, stop summing as soon as it does. ESPresso's 32-bit
ints rely on that.

## Complexity

- **Time:** O(n log M) where M = max(piles): about 30 feasibility checks of O(n) each.
- **Space:** O(1).

## Common mistakes

- **`lo = 0`**: then `mid` can be 0 and you divide by zero.
- **Floating-point ceil** `math.ceil(p / k)` is fine in Python for these sizes but can
  misround in languages with 53-bit doubles on bigger inputs; integer ceiling is exact.
- **Overflow** of the hours sum in 32-bit types; use 64-bit or early-exit.
- **Off by one in the search**: using `while lo <= hi` with `hi = mid` loops forever.

## Going further

The same template solves a whole family:
- **Capacity to ship packages within D days** (min capacity, feasibility = greedy
  packing).
- **Split array largest sum** (min possible max-sum over m pieces).
- **Minimum days to make m bouquets**, **aggressive cows** (maximise the minimum
  distance: search for the *last* feasible value).
""",
    solution='''def min_eating_speed(piles, h):
    def hours_needed(k):
        # Each pile p takes ceil(p / k) hours. (p - 1) // k + 1 is an integer
        # ceiling that avoids floats (and the p + k - 1 overflow in other languages).
        total = 0
        for p in piles:
            total += (p - 1) // k + 1
            if total > h:          # already too slow: no need to finish summing
                break
        return total

    # Speed max(piles) always works (one hour per pile and len(piles) <= h),
    # and speed 1 is the slowest allowed. Answer is in [lo, hi].
    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        if hours_needed(mid) <= h:
            hi = mid               # feasible: the minimum is mid or slower
        else:
            lo = mid + 1           # too slow: every speed <= mid is too slow too
    return lo
''',
    refs={
        "c": '''long long min_eating_speed(long long* piles, int pilesSize, long long h) {
    long long lo = 1, hi = 1;
    for (int i = 0; i < pilesSize; i++) if (piles[i] > hi) hi = piles[i];
    while (lo < hi) {
        long long mid = lo + (hi - lo) / 2, hours = 0;
        for (int i = 0; i < pilesSize && hours <= h; i++)
            hours += (piles[i] - 1) / mid + 1;      // integer ceil(p / mid)
        if (hours <= h) hi = mid; else lo = mid + 1;
    }
    return lo;
}''',
        "cpp": '''long long minEatingSpeed(vector<long long>& piles, long long h) {
    auto feasible = [&](long long k) {
        long long hours = 0;
        for (long long p : piles) {
            hours += (p + k - 1) / k;              // fine in 64-bit
            if (hours > h) return false;
        }
        return true;
    };
    long long lo = 1, hi = *max_element(piles.begin(), piles.end());
    while (lo < hi) {
        long long mid = lo + (hi - lo) / 2;
        if (feasible(mid)) hi = mid; else lo = mid + 1;
    }
    return lo;
}''',
        "rust": '''pub fn min_eating_speed(piles: Vec<i64>, h: i64) -> i64 {
    let feasible = |k: i64| -> bool {
        let mut hours = 0i64;
        for &p in &piles {
            hours += (p + k - 1) / k;
            if hours > h {
                return false;
            }
        }
        true
    };
    let (mut lo, mut hi) = (1i64, *piles.iter().max().unwrap());
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        if feasible(mid) { hi = mid; } else { lo = mid + 1; }
    }
    lo
}''',
        "espresso": '''// ESPresso ints are 32-bit: use (p - 1) / k + 1 and stop summing early.
fn feasible(piles, h, k) {
  var hours = 0
  for var i in 0..len(piles) {
    hours += (piles[i] - 1) / k + 1
    if hours > h { return false }
  }
  return true
}

fn minEatingSpeed(piles, h) {
  var lo = 1
  var hi = 1
  for var i in 0..len(piles) {
    if piles[i] > hi { hi = piles[i] }
  }
  while lo < hi {
    var mid = lo + (hi - lo) / 2
    if feasible(piles, h, mid) {
      hi = mid
    } else {
      lo = mid + 1
    }
  }
  return lo
}''',
    },
    tests=_koko_tests(),
)


def _median_tests():
    r = random.Random(87)
    a = sorted(r.randint(-10**6, 10**6) for _ in range(20))
    b = sorted(r.randint(-10**6, 10**6) for _ in range(31))
    c = sorted(r.randint(-10, 10) for _ in range(17))
    d = sorted(r.randint(-10, 10) for _ in range(8))
    return [
        [[1, 3], [2]],
        [[1, 2], [3, 4]],
        [[], [1]],
        [[2], []],
        [[], [2, 3]],
        [[1, 1, 1], [1, 1, 1]],
        [[1, 2, 3], [4, 5, 6, 7, 8, 9]],
        [[100], [1, 2, 3, 4]],
        [[-5, 3, 6, 12, 15], [-12, -10, -6, -3, 4, 10]],
        [a, b],
        [b, a[:19]],
        [c, d],
    ]


MEDIAN = dict(
    id="median-of-two-sorted-arrays",
    title="Median of Two Sorted Arrays",
    difficulty=3,
    tags=["binary search", "partition", "divide and conquer"],
    fn="find_median_sorted",
    params=[["nums1", "int[]"], ["nums2", "int[]"]],
    returns="float",
    statement="""Given two sorted arrays `nums1` and `nums2` (non-decreasing, possibly empty, but not
both empty), return the **median** of all their elements combined.

The median of an odd number of values is the middle one; for an even number it's the
average of the two middle values.

Target complexity: **O(log(min(m, n)))**. Merging is O(m + n) and will pass, but the
point of this problem is the partition binary search.""",
    constraints=["0 ≤ m, n ≤ 3000", "1 ≤ m + n", "-10⁶ ≤ nums1[i], nums2[i] ≤ 10⁶"],
    hints=[
        "Warm-up: merging the two arrays until you reach the middle works in O(m + n). Make sure you can do that first.",
        "Think of cutting each array in two: `i` elements from `nums1` and `j` from `nums2` go to the 'left half', with `i + j = (m + n + 1) // 2`. Choosing `i` fixes `j`.",
        "The cut is correct when `nums1[i-1] <= nums2[j]` and `nums2[j-1] <= nums1[i]` (treat out-of-range neighbours as ±∞). If `nums1[i-1] > nums2[j]`, `i` is too big; otherwise it's too small. Binary search `i` over `[0, m]`.",
        "Search on the **shorter** array so `j` never goes negative. The median is `max(left sides)` if the total is odd, else `(max(left sides) + min(right sides)) / 2`.",
    ],
    explanation=r"""
## Intuition

The median splits the combined data into a **left half** and a **right half** where every
left element ≤ every right element. We don't need to build the combined array, just to
find *where to cut each array*.

```
nums1:   1   4   7 │ 9  12             i = 3 elements go left
nums2:   2   3 │ 8  10  11  13         j = 2 elements go left
              ↑
left half = {1, 4, 7, 2, 3}   right half = {9, 12, 8, 10, 11, 13}
```

For the halves to have the right sizes, `i + j = (m + n + 1) // 2` (the left gets the
extra element when the total is odd). So choosing `i` determines `j`: a one-dimensional
search. For the cut to be valid, the two "cross" conditions must hold:

```
L1 = nums1[i-1]   R1 = nums1[i]
L2 = nums2[j-1]   R2 = nums2[j]
valid  ⇔  L1 <= R2  and  L2 <= R1      (L1 <= R1, L2 <= R2 hold automatically)
```

If `L1 > R2`, we took too many from `nums1`: decrease `i`. If `L2 > R1`, we took too few:
increase `i`. That's monotone, so **binary search `i`**. In the example above `L1 = 7 >
R2 = 8`? No. `L2 = 3 <= R1 = 9`? Yes. Valid, so total 11 is odd → median `max(7, 3) = 7`.

## Approach

1. Swap so `nums1` is the shorter array (`m ≤ n`). Then `j = half − i` is always in
   `[0, n]`.
2. `lo, hi = 0, m`. While `lo <= hi`:
   - `i = (lo + hi) // 2`, `j = half − i`.
   - Read `L1, R1, L2, R2`, using `−∞` when the index is `-1` and `+∞` when it's past the
     end (cutting at the very edge of an array).
   - If `L1 <= R2 and L2 <= R1`: found. Odd total → `max(L1, L2)`; even →
     `(max(L1, L2) + min(R1, R2)) / 2`.
   - Elif `L1 > R2`: `hi = i − 1`. Else: `lo = i + 1`.

Trace: `nums1 = [1, 2]`, `nums2 = [3, 4]`, `half = 2`

| lo | hi | i | j | L1 | R1 | L2 | R2 | verdict |
|---|---|---|---|---|---|---|---|---|
| 0 | 2 | 1 | 1 | 1 | 2 | 3 | 4 | L2 = 3 > R1 = 2 → lo = 2 |
| 2 | 2 | 2 | 0 | 2 | +∞ | −∞ | 3 | valid |

Even total → `(max(2, −∞) + min(+∞, 3)) / 2 = (2 + 3) / 2 = 2.5`.

## Complexity

- **Time:** O(log(min(m, n))): the search runs over the shorter array's cut positions.
- **Space:** O(1).
- The merge approach (two pointers, stop at the middle) is O(m + n) time, O(1) space and
  is a perfectly good first solution.

## Common mistakes

- **Searching the longer array.** Then `j = half − i` can be negative or exceed `n`.
- **Sentinels.** You need values below/above every element. Python has
  `float('inf')`; C/C++ use `LLONG_MIN`/`LLONG_MAX` (never add them!); ESPresso can use
  ±2147483647 since values are ≤ 10⁶.
- **Integer division for the even case.** `(a + b) / 2` with ints truncates in C, Rust and
  ESPresso: `(2 + 3) / 2 = 2`. Convert to floating point first: `(a + b) / 2.0`.
- **`half = (m + n) // 2`** with the odd case reading the *right* side instead. Either
  convention works if you're consistent; mixing them is a classic bug.
- **Both cuts at an edge** (an empty array): make sure `i = 0` or `i = m` doesn't index
  out of bounds.

## Going further

- **k-th smallest of two sorted arrays**: compare `nums1[k/2 − 1]` with
  `nums2[k/2 − 1]` and discard `k/2` elements from the smaller one each step: O(log k).
  The median is a special case.
- The median of a **stream** uses two heaps (max-heap left, min-heap right), a different
  but related "keep two halves balanced" idea.
""",
    solution='''def find_median_sorted(nums1, nums2):
    # Binary search the cut position in the SHORTER array; the other cut follows.
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1
    m, n = len(nums1), len(nums2)
    half = (m + n + 1) // 2           # size of the left half (gets the extra if odd)
    NEG, POS = float("-inf"), float("inf")

    lo, hi = 0, m                     # i = how many of nums1 go to the left half
    while lo <= hi:
        i = (lo + hi) // 2
        j = half - i                  # forced: left half must have exactly `half`
        # Border values around each cut; an empty side acts like -inf / +inf so it
        # never blocks the validity checks.
        l1 = nums1[i - 1] if i > 0 else NEG
        r1 = nums1[i] if i < m else POS
        l2 = nums2[j - 1] if j > 0 else NEG
        r2 = nums2[j] if j < n else POS

        if l1 <= r2 and l2 <= r1:
            # Every left element <= every right element: this is the median cut.
            if (m + n) % 2 == 1:
                return float(max(l1, l2))
            return (max(l1, l2) + min(r1, r2)) / 2
        if l1 > r2:
            hi = i - 1                # took too many from nums1
        else:
            lo = i + 1                # took too few from nums1
    # Unreachable for sorted inputs: a valid cut always exists.
    raise ValueError("inputs not sorted")
''',
    refs={
        "c": '''double find_median_sorted(long long* nums1, int nums1Size, long long* nums2, int nums2Size) {
    // Ensure nums1 is the shorter array.
    if (nums1Size > nums2Size) {
        long long* t = nums1; nums1 = nums2; nums2 = t;
        int s = nums1Size; nums1Size = nums2Size; nums2Size = s;
    }
    int m = nums1Size, n = nums2Size, half = (m + n + 1) / 2;
    int lo = 0, hi = m;
    while (lo <= hi) {
        int i = lo + (hi - lo) / 2, j = half - i;
        long long l1 = i > 0 ? nums1[i - 1] : LLONG_MIN;
        long long r1 = i < m ? nums1[i]     : LLONG_MAX;
        long long l2 = j > 0 ? nums2[j - 1] : LLONG_MIN;
        long long r2 = j < n ? nums2[j]     : LLONG_MAX;
        if (l1 <= r2 && l2 <= r1) {
            long long left = l1 > l2 ? l1 : l2;
            if ((m + n) % 2) return (double)left;
            long long right = r1 < r2 ? r1 : r2;
            return ((double)left + (double)right) / 2.0;   // float division!
        }
        if (l1 > r2) hi = i - 1; else lo = i + 1;
    }
    return 0.0;  // unreachable for valid input
}''',
        "cpp": '''double findMedianSorted(vector<long long>& nums1, vector<long long>& nums2) {
    if (nums1.size() > nums2.size()) return findMedianSorted(nums2, nums1);
    int m = nums1.size(), n = nums2.size(), half = (m + n + 1) / 2;
    int lo = 0, hi = m;
    while (lo <= hi) {
        int i = lo + (hi - lo) / 2, j = half - i;
        long long l1 = i > 0 ? nums1[i - 1] : LLONG_MIN;
        long long r1 = i < m ? nums1[i] : LLONG_MAX;
        long long l2 = j > 0 ? nums2[j - 1] : LLONG_MIN;
        long long r2 = j < n ? nums2[j] : LLONG_MAX;
        if (l1 <= r2 && l2 <= r1) {
            if ((m + n) % 2) return (double)max(l1, l2);
            return (max(l1, l2) + min(r1, r2)) / 2.0;
        }
        if (l1 > r2) hi = i - 1; else lo = i + 1;
    }
    return 0.0;
}''',
        "rust": '''pub fn find_median_sorted(nums1: Vec<i64>, nums2: Vec<i64>) -> f64 {
    // Shadow so that `a` is the shorter array.
    let (a, b) = if nums1.len() <= nums2.len() { (nums1, nums2) } else { (nums2, nums1) };
    let (m, n) = (a.len(), b.len());
    let half = (m + n + 1) / 2;
    let (mut lo, mut hi) = (0usize, m);
    loop {
        let i = (lo + hi) / 2;
        let j = half - i;                       // never underflows since m <= n
        let l1 = if i > 0 { a[i - 1] } else { i64::MIN };
        let r1 = if i < m { a[i] } else { i64::MAX };
        let l2 = if j > 0 { b[j - 1] } else { i64::MIN };
        let r2 = if j < n { b[j] } else { i64::MAX };
        if l1 <= r2 && l2 <= r1 {
            let left = l1.max(l2) as f64;
            if (m + n) % 2 == 1 {
                return left;
            }
            return (left + r1.min(r2) as f64) / 2.0;
        } else if l1 > r2 {
            hi = i - 1;                         // i > 0 here because l1 > -inf
        } else {
            lo = i + 1;
        }
    }
}''',
        "espresso": '''// Values are within +-10^6, so +-2147483647 work as infinities.
fn medianCut(a, b) {
  var m = len(a)
  var n = len(b)
  var half = (m + n + 1) / 2
  var lo = 0
  var hi = m
  while lo <= hi {
    var i = lo + (hi - lo) / 2
    var j = half - i
    var l1 = -2147483647
    var r1 = 2147483647
    var l2 = -2147483647
    var r2 = 2147483647
    if i > 0 { l1 = a[i - 1] }
    if i < m { r1 = a[i] }
    if j > 0 { l2 = b[j - 1] }
    if j < n { r2 = b[j] }
    if l1 <= r2 and l2 <= r1 {
      var left = l1
      if l2 > left { left = l2 }
      var right = r1
      if r2 < right { right = r2 }
      var total = m + n
      // no % in ESPresso: total is odd when total - (total / 2) * 2 == 1
      if total - (total / 2) * 2 == 1 { return left * 1.0 }
      return (left + right) / 2.0
    }
    if l1 > r2 {
      hi = i - 1
    } else {
      lo = i + 1
    }
  }
  return 0.0
}

fn findMedianSorted(nums1, nums2) {
  if len(nums1) > len(nums2) { return medianCut(nums2, nums1) }
  return medianCut(nums1, nums2)
}''',
    },
    tests=_median_tests(),
)

PROBLEMS = [
    BUBBLE,
    INSERTION,
    MERGE,
    QUICK,
    COUNTING,
    BINSEARCH,
    SEARCH_INSERT,
    FIRST_LAST,
    SQRT,
    ROTATED_SEARCH,
    ROTATED_MIN,
    PEAK,
    KTH,
    KOKO,
    MEDIAN,
]
