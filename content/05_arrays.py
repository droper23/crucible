"""Track 5: Arrays & Two Pointers."""
import random
import textwrap


def _d(s):
    return textwrap.dedent(s).lstrip("\n")


TRACK = dict(
    id="arrays",
    title="Arrays & Two Pointers",
    order=5,
    icon="▦",
    blurb="Contiguous memory, in-place rewrites, two pointers and prefix sums: the workhorse patterns behind half of all array problems.",
    intro=_d(r"""
## Why arrays are special

An array is the simplest data structure there is: a run of equally-sized slots laid
out **back to back in memory**. That one fact explains almost everything about how
arrays behave.

```
  index:      0        1        2        3        4
          +--------+--------+--------+--------+--------+
  memory: |   7    |   -2   |   9    |   4    |   0    |
          +--------+--------+--------+--------+--------+
  address: 1000     1008     1016     1024     1032       (8-byte long longs)
```

To find `a[i]` the CPU computes `base + i * sizeof(element)`: one multiply, one add,
one load. That is why indexing is **O(1)** no matter how big the array is, and why
walking an array front-to-back is extremely fast: neighbouring elements share cache
lines, so the hardware prefetcher streams them in before you ask.

The flip side: there is no room *between* slots. Inserting at the front means shifting
every element one place right, so `insert(0, x)` and `pop(0)` are **O(n)**. Appending
at the end is amortised O(1) in Python lists, `std::vector` and Rust `Vec`, because
they over-allocate and double their capacity when full.

| operation | cost | why |
|---|---|---|
| `a[i]` read/write | O(1) | address arithmetic |
| scan all elements | O(n) | cache-friendly |
| append (dynamic array) | amortised O(1) | capacity doubling |
| insert/delete in the middle | O(n) | shift the tail |
| search unsorted | O(n) | must look at everything |
| search sorted | O(log n) | binary search |

### What "array" means in each language

```python
nums = [3, 1, 4]          # Python list: an array of *pointers* to int objects
nums.append(1)            # amortised O(1)
```

```c
long long nums[3] = {3, 1, 4};             // fixed size, lives on the stack
long long *heap = malloc(n * sizeof *heap); // size chosen at runtime; you free() it
// C arrays don't know their length: every function receives (pointer, size).
```

```rust
let mut nums: Vec<i64> = vec![3, 1, 4];   // growable, owns its buffer
let view: &[i64] = &nums[1..];            // a slice: pointer + length, borrowed
```

## In place vs. copy

Many problems say "do it **in place** with O(1) extra memory". That means: overwrite the
input rather than building a second array. Copying is often simpler (and perfectly fine
when allowed), but in-place algorithms teach you to think about *which slots are still
needed* and *which are free to overwrite*. A classic trick is to keep two indices:

```
  read  ->  scans every element once
  write ->  points at the next slot of the answer we are building

  [ answer so far | already read, garbage | not yet read ]
    0        write                  read              n
```

Because `write <= read` always, we never overwrite an element we still need. Remove
Duplicates and Move Zeroes are exactly this pattern.

When the answer would overwrite unread data from the *front* (Merge Sorted Array), flip
the direction and fill **from the back**.

In C and Rust, mutating a parameter is explicit (`long long*`, `&mut Vec<i64>`); in Python
a list argument is a reference to the caller's list, so `nums[i] = x` changes it for the
caller while `nums = [...]` merely rebinds the local name. Use `nums[:] = ...` if you
really want to replace the contents.

## Pattern 1: two pointers

Two indices that move toward each other, or in the same direction, so that the pair
of them visits O(n) states instead of the O(n²) of a double loop.

**Opposite ends** (sorted input, or a "width × height" trade-off):

```
  [ 1   2   4   7  11  15 ]     target = 15
    L                   R       1 + 15 = 16 > 15  -> R--   (R can't pair with anything bigger than 1)
    L               R           1 + 11 = 12 < 15  -> L++   (L can't pair with anything smaller than 11)
        L           R           2 + 11 = 13 < 15  -> L++
            L       R           4 + 11 = 15  found!
```

The key argument is always the same: *each move discards a pointer position that
provably can't be part of a better answer*. If you can state that sentence for a
problem, two pointers will work.

**Same direction** (read/write, fast/slow): one pointer explores, the other marks the
boundary of the answer. This is how you filter, compact or deduplicate in place.

## Pattern 2: prefix sums

Precompute `P[i] = a[0] + ... + a[i-1]` (with `P[0] = 0`). Then any range sum is a
subtraction:

```
  a  =     [ 3,  1,  4,  1,  5 ]
  P  = [ 0,  3,  4,  8,  9, 14 ]

  sum(a[1..=3]) = P[4] - P[1] = 9 - 3 = 6      (1 + 4 + 1)
```

Building `P` is O(n); each query afterwards is O(1). The same idea underlies Pivot
Index (left sum vs. right sum), Product of Array Except Self (prefix *products*), and,
together with a hash map, "subarray sum equals k" in the next track.

```python
P = [0]
for x in a:
    P.append(P[-1] + x)     # P has n + 1 entries; the extra 0 kills edge cases
```

## Pattern 3: running state (Kadane & friends)

Some problems only need *one pass* and a couple of variables summarising the past:
the cheapest price so far, the best subarray ending here, the current majority
candidate. Ask: "if I knew the answer for the prefix `a[0..i)`, what tiny amount of
information would let me extend it to `a[0..i]`?" That information is your state.

## Habits that prevent bugs

- Decide whether your ranges are **half-open** `[lo, hi)` or closed `[lo, hi]` and
  stick to it. Half-open ranges make lengths (`hi - lo`) and empty ranges (`lo == hi`)
  trivial.
- Test the empty array, a single element, all-equal elements, and already
  sorted/reversed input.
- In C, C++ and Rust use 64-bit accumulators (`long long`, `i64`) for sums and
  products; in Rust, `usize` cannot go negative, so `i - 1` with `i == 0` panics.
- When mutating in place, ask "is the slot I am about to overwrite still needed?"
"""),
)

PROBLEMS = []

# ----------------------------------------------------------------------------- 1
_r = random.Random(501)
_big = sorted(_r.randint(-500, 500) for _ in range(3000))
PROBLEMS.append(dict(
    id="remove-duplicates-sorted-array",
    title="Remove Duplicates from Sorted Array",
    difficulty=1,
    tags=["array", "two pointers", "in-place"],
    fn="remove_duplicates",
    params=[["nums", "int[]"]],
    returns="int[]",
    statement=_d(r"""
You are given an array `nums` sorted in **non-decreasing** order. Some values appear
several times in a row.

Compact the array **in place** so that each distinct value appears exactly once, in the
original order, at the front of the array: after your algorithm runs, the first `k`
slots of `nums` must hold the `k` distinct values in increasing order. Whatever is left
in slots `k..n-1` does not matter.

Return those first `k` elements as an array (in Python, `nums[:k]`; in C, a `malloc`-ed
copy of the prefix with `*returnSize = k`).

The point of the exercise is the in-place compaction: aim for O(n) time and O(1) extra
memory apart from the returned copy.
"""),
    example_notes=[
        "The distinct values are 1 and 2; after compaction `nums` starts with `[1, 2, ...]`.",
        "Runs of equal values collapse to a single copy each.",
    ],
    constraints=["0 ≤ len(nums) ≤ 3·10⁴", "-10⁴ ≤ nums[i] ≤ 10⁴", "`nums` is sorted in non-decreasing order"],
    hints=[
        "Because the array is sorted, all copies of a value sit next to each other. How can you tell, looking at a single position, that it starts a new value?",
        "Keep two indices: `read` visits every element, `write` marks where the next distinct value should go.",
        "Compare `nums[read]` with the last value you *wrote* (`nums[write - 1]`). If they differ, copy it to `nums[write]` and advance `write`. The answer is `nums[:write]`.",
    ],
    explanation=_d(r"""
## Intuition

"Sorted" is the clue. In a sorted array duplicates are *adjacent*, so you never need to
remember every value you've seen (that would need a set). You only need to remember the
**last distinct value you kept**. Anything equal to it is a duplicate; anything
different is new.

Since the answer is never longer than what we've already read, we can build it in the
same array, overwriting slots we've finished with. This is the read/write two-pointer
pattern from the track intro.

## Approach

1. If the array is empty, the answer is empty.
2. `nums[0]` is always kept, so start with `write = 1`.
3. For `read` from 1 to `n - 1`:
   - if `nums[read] != nums[write - 1]`, it's a new value: `nums[write] = nums[read]`,
     `write += 1`;
   - otherwise skip it.
4. The first `write` slots are the answer.

Trace on `[0, 0, 1, 1, 1, 2]`:

| read | nums[read] | last kept `nums[write-1]` | action | array (prefix `|` rest) | write |
|---|---|---|---|---|---|
| – | – | – | start | `0 | 0 1 1 1 2` | 1 |
| 1 | 0 | 0 | skip | `0 | 0 1 1 1 2` | 1 |
| 2 | 1 | 0 | copy | `0 1 | 1 1 1 2` | 2 |
| 3 | 1 | 1 | skip | `0 1 | 1 1 1 2` | 2 |
| 4 | 1 | 1 | skip | `0 1 | 1 1 1 2` | 2 |
| 5 | 2 | 1 | copy | `0 1 2 | 1 1 2` | 3 |

Result: `[0, 1, 2]`.

Why is overwriting safe? `write ≤ read` at every step, so the slot we write into has
already been read: we never destroy information we still need.

## Complexity

- **Time:** O(n), one pass, constant work per element.
- **Space:** O(1) extra for the compaction itself (the returned copy is the output).

## Common mistakes

- **Comparing with the wrong neighbour.** Comparing `nums[read]` with `nums[read - 1]`
  also works here (the array is sorted), but comparing against the last *written* value
  generalises to variants like "allow at most two copies" (compare with `nums[write - 2]`).
- **Forgetting the empty array.** Starting with `write = 1` on an empty array returns a
  bogus one-element answer. Guard it.
- **Using a set.** `sorted(set(nums))` gives the right values but costs O(n log n) and
  O(n) memory, and ignores the in-place requirement.
- **C:** returning `nums` itself instead of a fresh `malloc` buffer; the caller owns
  `nums` and may free the returned pointer.

## Going further

- *Remove Duplicates II*: keep at most two copies of each value. Same loop, compare with
  `nums[write - 2]`.
- C++ has this built in: `nums.erase(unique(nums.begin(), nums.end()), nums.end());`
  `std::unique` is exactly this read/write loop. Rust: `nums.dedup()`.
"""),
    solution=_d(r"""
def remove_duplicates(nums):
    # An empty array has no distinct values. Handle it up front so the
    # "nums[0] is always kept" assumption below is valid.
    if not nums:
        return []
    # nums[0:write] is the compacted, duplicate-free prefix built so far.
    # The first element is always part of the answer.
    write = 1
    for read in range(1, len(nums)):
        # Sorted input => duplicates are adjacent, so it's enough to compare
        # with the last value we kept. Different means "new distinct value".
        if nums[read] != nums[write - 1]:
            # write <= read, so this slot has already been read: safe to reuse.
            nums[write] = nums[read]
            write += 1
    # Only the prefix is meaningful; the tail is leftover garbage.
    return nums[:write]
"""),
    refs={
        "cpp": _d(r"""
            vector<long long> removeDuplicates(vector<long long>& nums) {
                if (nums.empty()) return {};
                size_t write = 1;                       // nums[0..write) is the answer so far
                for (size_t read = 1; read < nums.size(); read++) {
                    if (nums[read] != nums[write - 1])  // new distinct value
                        nums[write++] = nums[read];     // write <= read: safe overwrite
                }
                nums.resize(write);                     // drop the garbage tail
                return nums;
            }
        """),
        "rust": _d(r"""
            pub fn remove_duplicates(mut nums: Vec<i64>) -> Vec<i64> {
                if nums.is_empty() {
                    return nums;
                }
                let mut write = 1; // nums[..write] is the compacted prefix
                for read in 1..nums.len() {
                    if nums[read] != nums[write - 1] {
                        nums[write] = nums[read]; // write <= read, slot already consumed
                        write += 1;
                    }
                }
                nums.truncate(write); // keep only the answer (Vec::dedup does all of this)
                nums
            }
        """),
        "c": _d(r"""
            long long* remove_duplicates(long long* nums, int numsSize, int* returnSize) {
                int write = 0;
                for (int read = 0; read < numsSize; read++) {
                    // keep nums[read] if it is the first element or differs from the last kept one
                    if (write == 0 || nums[read] != nums[write - 1])
                        nums[write++] = nums[read];
                }
                // The caller owns nums, so hand back a fresh copy of the prefix.
                long long* out = malloc(sizeof(long long) * (write > 0 ? write : 1));
                memcpy(out, nums, sizeof(long long) * write);
                *returnSize = write;
                return out;
            }
        """),
    },
    tests=[
        [[1, 1, 2]],
        [[0, 0, 1, 1, 1, 2, 2, 3, 3, 4]],
        [[]],
        [[7]],
        [[5, 5, 5, 5, 5]],
        [[-3, -1, 0, 2, 9]],
        [[-2, -2, -1, -1, -1, 0]],
        [_big],
    ],
))

# ----------------------------------------------------------------------------- 2
_r = random.Random(502)
_mz = [0 if _r.random() < 0.4 else _r.randint(-1000, 1000) for _ in range(50)]
PROBLEMS.append(dict(
    id="move-zeroes",
    title="Move Zeroes",
    difficulty=1,
    tags=["array", "two pointers", "in-place"],
    fn="move_zeroes",
    params=[["nums", "int[]"]],
    returns="void",
    mutates="nums",
    statement=_d(r"""
Given an integer array `nums`, move every `0` to the **end** of the array while keeping
the relative order of the non-zero elements unchanged.

You must modify `nums` **in place**; the function returns nothing. The checker looks at
`nums` after your function returns.
"""),
    example_notes=[
        "Non-zero values `1, 3, 12` keep their order; both zeroes end up at the back.",
        "A single zero is already in the right place.",
    ],
    constraints=["0 ≤ len(nums) ≤ 10⁴", "-2³¹ ≤ nums[i] ≤ 2³¹ - 1"],
    hints=[
        "Think of it as *filtering*: you want all the non-zeros, in order, at the front.",
        "Use a `write` index for the next slot of the non-zero prefix and a `read` index that scans everything.",
        "After copying every non-zero forward, every slot from `write` to the end must become 0. (Or swap `nums[read]` and `nums[write]` to do both in one pass.)",
    ],
    explanation=_d(r"""
## Intuition

"Keep the relative order" + "in place" is the signature of the **read/write
compaction** pattern. Stop thinking about moving zeroes *back*; think about moving
non-zeroes *forward*. Once every non-zero is packed at the front in order, the zeroes
are simply whatever is left, and we can fill those slots with 0.

## Approach

1. `write = 0`.
2. For each `read` in `0..n`: if `nums[read] != 0`, set `nums[write] = nums[read]` and
   increment `write`.
3. Fill `nums[write..n]` with zeros.

Trace on `[0, 1, 0, 3, 12]`:

| read | value | action | nums | write |
|---|---|---|---|---|
| 0 | 0 | skip | `0 1 0 3 12` | 0 |
| 1 | 1 | copy to 0 | `1 1 0 3 12` | 1 |
| 2 | 0 | skip | `1 1 0 3 12` | 1 |
| 3 | 3 | copy to 1 | `1 3 0 3 12` | 2 |
| 4 | 12 | copy to 2 | `1 3 12 3 12` | 3 |
| fill | | zero slots 3, 4 | `1 3 12 0 0` | |

**Swap variant.** Instead of copying, swap `nums[read]` with `nums[write]`. The zeros
"bubble" into the gap automatically and you skip the fill loop. It does more writes
when there are few zeros, but it's a single pass.

## Complexity

- **Time:** O(n). Each element is read once and written at most twice.
- **Space:** O(1).

## Common mistakes

- **Removing zeros with `nums.remove(0)` / `erase` in a loop.** Each removal shifts the
  tail, giving O(n²) on inputs full of zeros.
- **Rebinding instead of mutating (Python).** `nums = [x for x in nums if x] + [0]*z`
  only changes your local variable; the caller still sees the old list. Use
  `nums[:] = ...` or assign by index.
- **Forgetting the fill step.** Without it the tail keeps stale non-zero copies
  (`1 3 12 3 12` above).
- **Sorting.** Sorting by "is zero" with an unstable sort can reorder the non-zeros.

## Going further

This is `std::stable_partition` in C++ and `Vec::retain` + `resize` in Rust. The same
loop removes every occurrence of any value (`Remove Element`), and the swap version is
the partition step of quicksort, which is *not* stable in general: here it happens to
be, because one of the two groups (zeros) consists of identical values.
"""),
    solution=_d(r"""
def move_zeroes(nums):
    # nums[0:write] holds the non-zero values seen so far, in their original order.
    write = 0
    for read in range(len(nums)):
        if nums[read] != 0:
            # write <= read always, so we only overwrite slots already read.
            nums[write] = nums[read]
            write += 1
    # Everything from `write` onward is either a zero or a stale duplicate of a
    # value we already moved forward; either way it must become 0.
    for i in range(write, len(nums)):
        nums[i] = 0
    # No return value: the caller observes the mutated list.
"""),
    refs={
        "c": _d(r"""
            void move_zeroes(long long* nums, int numsSize) {
                int write = 0;
                for (int read = 0; read < numsSize; read++)
                    if (nums[read] != 0) nums[write++] = nums[read];  // pack non-zeros forward
                while (write < numsSize) nums[write++] = 0;           // zero the tail
            }
        """),
        "cpp": _d(r"""
            void moveZeroes(vector<long long>& nums) {
                // Swap variant: zeros drift into the gap between write and read.
                size_t write = 0;
                for (size_t read = 0; read < nums.size(); read++)
                    if (nums[read] != 0) swap(nums[write++], nums[read]);
            }
        """),
        "rust": _d(r"""
            pub fn move_zeroes(nums: &mut Vec<i64>) {
                let mut write = 0;
                for read in 0..nums.len() {
                    if nums[read] != 0 {
                        nums.swap(write, read); // swap keeps it to one pass
                        write += 1;
                    }
                }
            }
        """),
        "espresso": _d(r"""
            fn moveZeroes(nums) {
              // pack the non-zero values to the front, in order
              var write = 0
              for var read in 0..len(nums) {
                if nums[read] != 0 {
                  nums[write] = nums[read]
                  write += 1
                }
              }
              // whatever remains becomes zero
              while write < len(nums) {
                nums[write] = 0
                write += 1
              }
            }
        """),
    },
    tests=[
        [[0, 1, 0, 3, 12]],
        [[0]],
        [[]],
        [[1, 2, 3]],
        [[0, 0, 0, 5]],
        [[4, 0, 0, 0]],
        [[-1, 0, -2, 0, 0, 3]],
        [_mz],
    ],
))

# ----------------------------------------------------------------------------- 3
def _merge_case(r, m, n, lo=-1000, hi=1000):
    a = sorted(r.randint(lo, hi) for _ in range(m))
    b = sorted(r.randint(lo, hi) for _ in range(n))
    return [a + [0] * n, m, b, n]


_r = random.Random(503)
PROBLEMS.append(dict(
    id="merge-sorted-arrays",
    title="Merge Sorted Arrays",
    difficulty=1,
    tags=["array", "two pointers", "in-place"],
    fn="merge",
    params=[["nums1", "int[]"], ["m", "int"], ["nums2", "int[]"], ["n", "int"]],
    returns="void",
    mutates="nums1",
    statement=_d(r"""
You are given two integer arrays sorted in non-decreasing order:

- `nums1` has length `m + n`. Its first `m` elements are real data; the last `n` slots
  are padding (zeros) reserved for the merge.
- `nums2` has exactly `n` elements.

Merge `nums2` into `nums1` **in place** so that all `m + n` slots of `nums1` hold the
combined values in non-decreasing order. The function returns nothing; the checker
inspects `nums1`.
"""),
    example_notes=[
        "Merging `[1,2,3]` with `[2,5,6]` gives `[1,2,2,3,5,6]`.",
        "`nums2` is empty, so `nums1` is unchanged.",
    ],
    constraints=["0 ≤ m, n ≤ 2000", "len(nums1) = m + n", "-10⁹ ≤ values ≤ 10⁹"],
    hints=[
        "Merging from the front would overwrite elements of `nums1` you haven't placed yet. Where is there free space?",
        "The free space is at the *back*. The largest element of the result goes in slot `m + n - 1`.",
        "Keep three indices: `i = m-1` (last real value of nums1), `j = n-1` (last of nums2), `k = m+n-1` (slot to fill). Put the larger of `nums1[i]`, `nums2[j]` at `k`. Stop when `nums2` is exhausted.",
    ],
    explanation=_d(r"""
## Intuition

The textbook merge (from merge sort) walks both arrays from the front and appends the
smaller head to an output array. Here the output *is* `nums1`, and the front of
`nums1` is full of data we haven't consumed yet. Writing there would destroy it.

But the *back* of `nums1` is empty padding. If we merge **largest-first**, we always
write into a slot that is either padding or a `nums1` value we've already moved.

## Approach

```
i = m - 1          # last unplaced value in nums1's data
j = n - 1          # last unplaced value in nums2
k = m + n - 1      # next slot to fill, moving left
```

While `j >= 0` (there is still something in `nums2` to place):
- if `i >= 0` and `nums1[i] > nums2[j]`: `nums1[k] = nums1[i]`, `i -= 1`
- else: `nums1[k] = nums2[j]`, `j -= 1`
- `k -= 1`

When `nums2` runs out we can stop: whatever remains of `nums1[0..i]` is already in place.

Trace with `nums1 = [1, 2, 3, _, _, _]`, `nums2 = [2, 5, 6]`:

| i | j | k | compare | nums1 |
|---|---|---|---|---|
| 2 | 2 | 5 | 3 vs **6** | `1 2 3 _ _ 6` |
| 2 | 1 | 4 | 3 vs **5** | `1 2 3 _ 5 6` |
| 2 | 0 | 3 | **3** vs 2 | `1 2 3 3 5 6` |
| 1 | 0 | 2 | 2 vs **2** (tie → nums2) | `1 2 2 3 5 6` |
| 1 | -1 | | done | |

**Why it's safe:** the number of unfilled slots to the right of `i` is always
`k - i = j + 1 ≥ 0`, i.e. `k ≥ i`. So we never overwrite an unplaced `nums1` value.

## Complexity

- **Time:** O(m + n); each step places one element.
- **Space:** O(1).

## Common mistakes

- **Looping while `i >= 0`** instead of `j >= 0`. If `nums1`'s values are all bigger,
  you'll exhaust `i` and leave `nums2` elements unplaced.
- **Reading `nums1[i]` when `i < 0`.** In Python, `nums1[-1]` silently reads the last
  element, a nasty bug. Check `i >= 0` first.
- **Copying then sorting.** `nums1[m:] = nums2; nums1.sort()` works but is
  O((m+n) log(m+n)) and misses the point.
- **Rust:** with `usize` indices, `i - 1` when `i == 0` panics. Use signed `i64` indices
  or count "remaining" values instead.

## Going further

- Merging k sorted arrays: use a min-heap (O(N log k)).
- This back-to-front trick appears whenever an in-place transformation grows data, e.g.
  replacing every space in a string with `%20` in a buffer that has room at the end.
"""),
    solution=_d(r"""
def merge(nums1, m, nums2, n):
    # Fill nums1 from the back: the tail is free padding, so writing the
    # largest remaining value there can never clobber unplaced data.
    i = m - 1          # last unplaced real value in nums1
    j = n - 1          # last unplaced value in nums2
    k = m + n - 1      # next slot to fill
    # Only nums2 needs exhausting: once it's empty, nums1[0..i] is already
    # sitting in its final position.
    while j >= 0:
        # Check i >= 0 first; in Python nums1[-1] would silently read the end.
        if i >= 0 and nums1[i] > nums2[j]:
            nums1[k] = nums1[i]
            i -= 1
        else:
            nums1[k] = nums2[j]
            j -= 1
        k -= 1
"""),
    refs={
        "c": _d(r"""
            void merge(long long* nums1, int nums1Size, long long m, long long* nums2, int nums2Size, long long n) {
                long long i = m - 1, j = n - 1, k = m + n - 1;
                while (j >= 0) {
                    // take from nums1 only if it still has values and its tail is larger
                    if (i >= 0 && nums1[i] > nums2[j]) nums1[k--] = nums1[i--];
                    else                               nums1[k--] = nums2[j--];
                }
            }
        """),
        "cpp": _d(r"""
            void merge(vector<long long>& nums1, long long m, vector<long long>& nums2, long long n) {
                long long i = m - 1, j = n - 1, k = m + n - 1;   // signed: they go to -1
                while (j >= 0) {
                    if (i >= 0 && nums1[i] > nums2[j]) nums1[k--] = nums1[i--];
                    else                               nums1[k--] = nums2[j--];
                }
            }
        """),
        "rust": _d(r"""
            pub fn merge(nums1: &mut Vec<i64>, m: i64, nums2: Vec<i64>, n: i64) {
                // Count how many values remain instead of using indices that would underflow.
                let (mut i, mut j) = (m as usize, n as usize); // remaining in nums1 / nums2
                while j > 0 {
                    let k = i + j - 1; // slot to fill
                    if i > 0 && nums1[i - 1] > nums2[j - 1] {
                        nums1[k] = nums1[i - 1];
                        i -= 1;
                    } else {
                        nums1[k] = nums2[j - 1];
                        j -= 1;
                    }
                }
            }
        """),
        "espresso": _d(r"""
            fn merge(nums1, m, nums2, n) {
              var i = m - 1
              var j = n - 1
              var k = m + n - 1
              while j >= 0 {
                var takeLeft = false
                if i >= 0 {
                  if nums1[i] > nums2[j] { takeLeft = true }
                }
                if takeLeft {
                  nums1[k] = nums1[i]
                  i -= 1
                } else {
                  nums1[k] = nums2[j]
                  j -= 1
                }
                k -= 1
              }
            }
        """),
    },
    tests=[
        [[1, 2, 3, 0, 0, 0], 3, [2, 5, 6], 3],
        [[1], 1, [], 0],
        [[0], 0, [1], 1],
        [[4, 5, 6, 0, 0, 0], 3, [1, 2, 3], 3],
        [[1, 1, 1, 0, 0], 3, [1, 1], 2],
        [[-5, 0, 7, 0, 0, 0, 0], 3, [-6, -5, 8, 9], 4],
        [[], 0, [], 0],
        _merge_case(_r, 25, 20, -10**6, 10**6),
        _merge_case(_r, 12, 3, -5, 5),
    ],
))

# ----------------------------------------------------------------------------- 4
def _two_sum_sorted_case(r, n, lo, hi):
    while True:
        a = sorted(r.randint(lo, hi) for _ in range(n))
        i, j = sorted(r.sample(range(n), 2))
        t = a[i] + a[j]
        cnt = {}
        pairs = 0
        for x in a:
            pairs += cnt.get(t - x, 0)
            cnt[x] = cnt.get(x, 0) + 1
        if pairs == 1:
            return [a, t]


def _two_sum_sorted_big(r, n, lo, hi):
    # Distinct even values plus exactly one odd value: an odd target can only
    # be reached by pairing the odd element with one specific (distinct) value.
    a = sorted(2 * x for x in r.sample(range(lo // 2, hi // 2), n))
    i, j = sorted(r.sample(range(n), 2))
    a[i] += 1
    return [a, a[i] + a[j]]


_r = random.Random(504)
PROBLEMS.append(dict(
    id="two-sum-sorted",
    title="Two Sum II (Sorted Input)",
    difficulty=2,
    tags=["array", "two pointers"],
    fn="two_sum_sorted",
    params=[["numbers", "int[]"], ["target", "int"]],
    returns="int[]",
    statement=_d(r"""
`numbers` is sorted in non-decreasing order. Find the two positions `i < j` such that
`numbers[i] + numbers[j] == target`, and return `[i, j]` (0-based, `i < j`).

Every input has **exactly one** such pair. Use only O(1) extra memory.
"""),
    example_notes=[
        "`2 + 7 = 9`, at indices 0 and 1.",
        "Equal values at different positions are fine: `3 + 3 = 6`.",
    ],
    constraints=["2 ≤ len(numbers) ≤ 3·10⁴", "-10⁶ ≤ numbers[i] ≤ 10⁶", "exactly one valid pair exists"],
    hints=[
        "Look at the smallest and largest elements. If their sum is too big, which one can't be in the answer?",
        "If `numbers[L] + numbers[R] > target`, the largest element can't pair with anything (even the smallest is too much), so `R -= 1`. Symmetric argument for too small.",
        "Start `L = 0`, `R = n - 1` and move one pointer per step until the sum matches.",
    ],
    explanation=_d(r"""
## Intuition

Without sorting you'd reach for a hash map (that's Two Sum in the hashing track).
Sorting gives you something better: **monotonicity**. Moving the left pointer right can
only increase the sum; moving the right pointer left can only decrease it. So from any
pair `(L, R)` you always know which way to go.

## Approach

```
L, R = 0, n - 1
while L < R:
    s = numbers[L] + numbers[R]
    if s == target: return [L, R]
    if s < target:  L += 1    # need a bigger sum
    else:           R -= 1    # need a smaller sum
```

**Why it never skips the answer.** Suppose the answer is `(i, j)`. While `L ≤ i` and
`R ≥ j`, every step discards a pointer that cannot be part of the answer:
- If `s > target` then `numbers[L] + numbers[R] > target` and `numbers[L]` is the smallest
  remaining partner for `R`, so `R` pairs with nothing; dropping it is safe. If `R`
  were `j`, then `numbers[L] ≤ numbers[i]` would give `s ≤ target`, contradiction, so
  `R ≠ j`.
- Symmetrically for `s < target`.

So we can never move past `i` or `j` before reaching both.

Trace: `numbers = [2, 7, 11, 15]`, target 9:

| L | R | sum | move |
|---|---|---|---|
| 0 | 3 | 17 | R-- |
| 0 | 2 | 13 | R-- |
| 0 | 1 | 9 | found `[0, 1]` |

## Complexity

- **Time:** O(n): each step moves one pointer inward, at most n − 1 steps.
- **Space:** O(1). (A hash map would also be O(n) time but O(n) space.)

## Common mistakes

- **`while L <= R`** lets an element pair with itself.
- **Moving both pointers** at once skips candidate pairs.
- **Binary search per element** (O(n log n)) works, but two pointers is simpler and
  faster.
- **Overflow:** with 32-bit ints, `numbers[L] + numbers[R]` can overflow; the harness
  uses 64-bit types, but remember it in other settings.

## Going further

This "opposite ends" scan is the inner loop of **3Sum** (fix one element, two-pointer
the rest) and of 4Sum. It also solves "count pairs with sum < target" in O(n): when
`numbers[L] + numbers[R] < target`, *all* of `L+1..R` pair with `L`, so add `R - L`.
"""),
    solution=_d(r"""
def two_sum_sorted(numbers, target):
    lo, hi = 0, len(numbers) - 1
    # lo < hi: an element may not pair with itself.
    while lo < hi:
        s = numbers[lo] + numbers[hi]
        if s == target:
            return [lo, hi]
        if s < target:
            # Even the largest remaining value can't lift numbers[lo] to the
            # target, so numbers[lo] is useless: discard it.
            lo += 1
        else:
            # Even the smallest remaining value makes the sum too big with
            # numbers[hi], so numbers[hi] is useless: discard it.
            hi -= 1
    # Unreachable: the statement guarantees exactly one answer.
    return []
"""),
    refs={
        "c": _d(r"""
            long long* two_sum_sorted(long long* numbers, int numbersSize, long long target, int* returnSize) {
                int lo = 0, hi = numbersSize - 1;
                long long* out = malloc(2 * sizeof(long long));
                *returnSize = 2;
                while (lo < hi) {
                    long long s = numbers[lo] + numbers[hi];
                    if (s == target) break;
                    if (s < target) lo++;   // need a bigger sum
                    else hi--;              // need a smaller sum
                }
                out[0] = lo; out[1] = hi;
                return out;
            }
        """),
        "cpp": _d(r"""
            vector<long long> twoSumSorted(vector<long long>& numbers, long long target) {
                int lo = 0, hi = (int)numbers.size() - 1;
                while (lo < hi) {
                    long long s = numbers[lo] + numbers[hi];
                    if (s == target) return {lo, hi};
                    if (s < target) lo++; else hi--;
                }
                return {};
            }
        """),
        "rust": _d(r"""
            use std::cmp::Ordering;

            pub fn two_sum_sorted(numbers: Vec<i64>, target: i64) -> Vec<i64> {
                let (mut lo, mut hi) = (0usize, numbers.len() - 1);
                while lo < hi {
                    match (numbers[lo] + numbers[hi]).cmp(&target) {
                        Ordering::Equal => return vec![lo as i64, hi as i64],
                        Ordering::Less => lo += 1,    // sum too small
                        Ordering::Greater => hi -= 1, // sum too big
                    }
                }
                vec![]
            }
        """),
    },
    tests=[
        [[2, 7, 11, 15], 9],
        [[3, 3], 6],
        [[-3, -1, 0, 4, 8], 5],
        [[1, 2, 3, 4, 4, 9, 56, 90], 8],
        [[-10, -5, -2, 0], -15],
        [[0, 0, 1], 0],
        [[1, 2, 5, 9, 12], 21],
        _two_sum_sorted_big(_r, 5000, -10**6, 10**6),
        _two_sum_sorted_big(_r, 500, -1000, 1000),
    ],
))

# ----------------------------------------------------------------------------- 5
_r = random.Random(505)
PROBLEMS.append(dict(
    id="container-with-most-water",
    title="Container With Most Water",
    difficulty=2,
    # Large tests (complexity matters here) exceed the ESPresso VM constant-pool limit.
    espresso=False,
    tags=["array", "two pointers", "greedy"],
    fn="max_area",
    params=[["height", "int[]"]],
    returns="int",
    statement=_d(r"""
`height[i]` is the height of a vertical line drawn at `x = i`. Pick two lines; together
with the x-axis they form a container. The amount of water it holds is

```
(j - i) * min(height[i], height[j])
```

Return the **maximum** amount of water any pair of lines `i < j` can hold. (Lines
between them don't get in the way.)
"""),
    example_notes=[
        "Lines at x = 1 (height 8) and x = 8 (height 7): width 7 × height 7 = 49.",
        "Two lines of height 1, one unit apart: area 1.",
    ],
    constraints=["2 ≤ len(height) ≤ 10⁵", "0 ≤ height[i] ≤ 10⁴"],
    hints=[
        "Start with the widest container, lines `0` and `n-1`. Any other container is narrower; what must be true for it to be better?",
        "The area is limited by the *shorter* line. If you move the taller line inward, width shrinks and the height can't exceed the shorter line, so the area can only go down.",
        "So always move the pointer at the shorter line. Track the best area seen.",
    ],
    explanation=_d(r"""
## Intuition

Brute force checks all n(n−1)/2 pairs. To do better we need a reason to throw pairs
away in bulk.

Start with the widest pair `(L, R) = (0, n−1)`. Say `height[L] ≤ height[R]`. Consider
any pair `(L, R')` with `R' < R`: it's narrower, and its height is still capped by
`height[L]`. So **every** pair using `L` is no better than the one we just measured.
`L` is done; move it right. That one comparison eliminated `R − L − 1` pairs at once.

## Approach

```
L, R = 0, n - 1
best = 0
while L < R:
    best = max(best, (R - L) * min(h[L], h[R]))
    if h[L] < h[R]: L += 1
    else:           R -= 1
```

Trace on `[1, 8, 6, 2, 5, 4, 8, 3, 7]`:

```
L=0 (1)  R=8 (7)   area 8*1 = 8    -> L++  (1 is shorter)
L=1 (8)  R=8 (7)   area 7*7 = 49   -> R--
L=1 (8)  R=7 (3)   area 6*3 = 18   -> R--
L=1 (8)  R=6 (8)   area 5*8 = 40   -> R--  (tie: either is fine)
L=1 (8)  R=5 (4)   area 4*4 = 16   -> R--
...                                  best = 49
```

**Ties.** When `h[L] == h[R]`, any container that keeps either of them is narrower and
no taller, so you may move either pointer (or both).

## Complexity

- **Time:** O(n). Each iteration moves one pointer inward.
- **Space:** O(1).

## Common mistakes

- **Moving the taller line.** It feels like "keep the tall one" but you must move the
  *short* one; moving the tall one can never help.
- **Confusing this with Trapping Rain Water.** Here only two lines matter and the ones
  in between are ignored; in rain water every bar contributes.
- **Overflow** in languages with 32-bit int when heights and widths are large: 10⁵ × 10⁴
  = 10⁹ fits in 32 bits, but only just.

## Going further

The proof pattern ("the current pair is the best one involving the discarded pointer")
is the general correctness argument for opposite-end two pointers. Try writing it
out for Two Sum II and you'll see it's identical.
"""),
    solution=_d(r"""
def max_area(height):
    lo, hi = 0, len(height) - 1
    best = 0
    while lo < hi:
        # Water level is set by the shorter line; width is the distance.
        h = min(height[lo], height[hi])
        best = max(best, (hi - lo) * h)
        # Any other container using the shorter line would be narrower and no
        # taller, so that line can't beat what we just measured. Discard it.
        if height[lo] < height[hi]:
            lo += 1
        else:
            hi -= 1
    return best
"""),
    refs={
        "c": _d(r"""
            long long max_area(long long* height, int heightSize) {
                // Two pointers start at the widest pair and move inward.
                int lo = 0, hi = heightSize - 1;
                long long best = 0;
                while (lo < hi) {
                    long long h = height[lo] < height[hi] ? height[lo] : height[hi];   // the shorter line caps the water
                    long long area = (long long)(hi - lo) * h;
                    if (area > best) best = area;
                    // Moving the taller line can only shrink the width without raising the cap,
                    // so the shorter line can never be part of a better pair: drop it.
                    if (height[lo] < height[hi]) lo++; else hi--;
                }
                return best;
            }
        """),
        "cpp": _d(r"""
            long long maxArea(vector<long long>& height) {
                int lo = 0, hi = (int)height.size() - 1;
                long long best = 0;
                while (lo < hi) {
                    best = max(best, (hi - lo) * min(height[lo], height[hi]));
                    if (height[lo] < height[hi]) lo++; else hi--;  // drop the shorter line
                }
                return best;
            }
        """),
        "rust": _d(r"""
            pub fn max_area(height: Vec<i64>) -> i64 {
                let (mut lo, mut hi) = (0usize, height.len() - 1);
                let mut best = 0;
                while lo < hi {
                    let h = height[lo].min(height[hi]);
                    best = best.max((hi - lo) as i64 * h);
                    if height[lo] < height[hi] { lo += 1 } else { hi -= 1 }
                }
                best
            }
        """),
    },
    tests=[
        [[1, 8, 6, 2, 5, 4, 8, 3, 7]],
        [[1, 1]],
        [[0, 0]],
        [[4, 3, 2, 1, 4]],
        [[1, 2, 1]],
        [[2, 3, 10, 5, 7, 8, 9]],
        [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]],
        [[_r.randint(0, 10**4) for _ in range(10000)]],
    ],
))

# ----------------------------------------------------------------------------- 6
_r = random.Random(506)
PROBLEMS.append(dict(
    id="three-sum",
    title="3Sum",
    difficulty=2,
    tags=["array", "two pointers", "sorting"],
    fn="three_sum",
    params=[["nums", "int[]"]],
    returns="int[][]",
    compare="unordered_deep",
    statement=_d(r"""
Return every **distinct** triplet `[a, b, c]` of values taken from three different
positions of `nums` such that `a + b + c == 0`.

Two triplets are the same if they contain the same values (as a multiset). Each distinct
triplet must appear exactly once. The order of the triplets, and of the values inside a
triplet, does not matter.
"""),
    example_notes=[
        "`[-1, 0, 1]` and `[-1, -1, 2]`. The two `-1`s are at different positions, so `[-1, -1, 2]` is allowed; `[-1, 0, 1]` can be formed two ways but is reported once.",
        "No triple sums to zero.",
    ],
    constraints=["0 ≤ len(nums) ≤ 3000", "-10⁵ ≤ nums[i] ≤ 10⁵"],
    hints=[
        "Sort the array first. What does that buy you for finding pairs?",
        "Fix the smallest element `nums[i]`; you now need two elements to the right summing to `-nums[i]`. That's Two Sum II.",
        "To avoid duplicates: skip `i` when `nums[i] == nums[i-1]`, and after recording a triplet move `L` past all equal values (and `R` likewise).",
    ],
    explanation=_d(r"""
## Intuition

Three nested loops are O(n³). The standard reduction: **fix one element, solve Two Sum on
the rest**. If the array is sorted, the inner Two Sum is the O(n) two-pointer scan, giving
O(n²) overall.

Sorting also solves the *duplicates* problem: equal values become adjacent, so "skip
values equal to the previous one" ensures each distinct triplet is produced once, with
no set of tuples needed.

## Approach

1. Sort `nums`.
2. For each `i` (the smallest element of the triplet):
   - if `i > 0` and `nums[i] == nums[i-1]`, skip (same first value already handled);
   - if `nums[i] > 0`, stop: all three would be positive;
   - two pointers `L = i+1`, `R = n-1` looking for `nums[L] + nums[R] == -nums[i]`.
3. On a hit, record it, then advance `L` while `nums[L] == nums[L-1]` and retreat `R`
   while `nums[R] == nums[R+1]` so the next pair is different.

Trace on sorted `[-4, -1, -1, 0, 1, 2]`:

```
i=0 (-4): need 4.  L/R scan finds nothing (max pair 1+2 = 3).
i=1 (-1): need 1.
          L=2(-1) R=5(2): 1   hit [-1,-1,2]; L->3, R->4
          L=3(0)  R=4(1): 1   hit [-1,0,1];  L->4, R->3, stop
i=2 (-1): same as nums[1], skip.
i=3 (0):  need 0. L=4(1) R=5(2): 3 > 0, R--, L==R stop.
```

## Complexity

- **Time:** O(n log n) to sort + O(n²) for the scans = **O(n²)**.
- **Space:** O(1) beyond the output (O(log n)–O(n) for the sort, depending on the
  language).

## Common mistakes

- **Deduplicating only the first element.** Without skipping equal `L` values after a
  hit, `[-2, 0, 0, 2, 2]` reports `[-2, 0, 2]` twice.
- **Skipping with `nums[i] == nums[i+1]`** (looking ahead) throws away valid triplets
  like `[-1, -1, 2]`. Compare with the *previous* element.
- **Using a set of tuples** to dedupe works but is slower and hides the logic.
- **Off-by-one in the dedupe loops:** guard `L < R` inside them.

## Going further

- **3Sum Closest:** same loop; track the sum with minimum `|sum − target|`.
- **4Sum:** add one more outer loop, O(n³). In general k-Sum is O(n^(k−1)).
- A hash-set version of the inner loop also gives O(n²) without sorting, but the
  deduplication becomes much messier.
"""),
    solution=_d(r"""
def three_sum(nums):
    nums = sorted(nums)          # sorting enables two pointers AND easy dedupe
    n = len(nums)
    out = []
    for i in range(n - 2):
        # nums[i] is the smallest of the triplet. If it's positive, so are the
        # other two, and the sum can't be zero. Nothing further can work.
        if nums[i] > 0:
            break
        # Same first value as last time => identical triplets. Skip.
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        need = -nums[i]
        lo, hi = i + 1, n - 1
        while lo < hi:
            s = nums[lo] + nums[hi]
            if s < need:
                lo += 1
            elif s > need:
                hi -= 1
            else:
                out.append([nums[i], nums[lo], nums[hi]])
                lo += 1
                hi -= 1
                # Step past copies of the values just used so the next hit
                # (if any) is a genuinely different pair.
                while lo < hi and nums[lo] == nums[lo - 1]:
                    lo += 1
                while lo < hi and nums[hi] == nums[hi + 1]:
                    hi -= 1
    return out
"""),
    refs={
        "c": _d(r"""
            static int cmp_ll(const void* a, const void* b) {
                long long x = *(const long long*)a, y = *(const long long*)b;
                return (x > y) - (x < y);          // never `x - y`: it can overflow / truncate to int
            }

            // Appends the triplet (a, b, c) to a growable array of malloc-ed rows.
            static void push3(long long*** res, int* count, int* cap, long long a, long long b, long long c) {
                if (*count == *cap) {                              // double when full: amortised O(1)
                    *cap = *cap ? 2 * *cap : 8;
                    *res = realloc(*res, *cap * sizeof(long long*));
                }
                long long* row = malloc(3 * sizeof(long long));
                row[0] = a; row[1] = b; row[2] = c;
                (*res)[(*count)++] = row;
            }

            long long** three_sum(long long* nums, int numsSize, int* returnSize, int** returnColumnSizes) {
                // Sort a private copy so the caller's array is left untouched.
                long long* a = malloc((numsSize ? numsSize : 1) * sizeof(long long));
                memcpy(a, nums, numsSize * sizeof(long long));
                qsort(a, numsSize, sizeof(long long), cmp_ll);

                long long** res = NULL;
                int count = 0, cap = 0;
                for (int i = 0; i + 2 < numsSize; i++) {
                    if (a[i] > 0) break;                           // smallest value positive: no zero sum left
                    if (i > 0 && a[i] == a[i - 1]) continue;       // same first value -> same triplets
                    int lo = i + 1, hi = numsSize - 1;
                    while (lo < hi) {
                        long long s = a[i] + a[lo] + a[hi];
                        if (s < 0) lo++;                           // need a bigger sum
                        else if (s > 0) hi--;                      // need a smaller sum
                        else {
                            push3(&res, &count, &cap, a[i], a[lo], a[hi]);
                            lo++; hi--;
                            // Skip equal neighbours so the same (a[lo], a[hi]) pair isn't reported twice.
                            while (lo < hi && a[lo] == a[lo - 1]) lo++;
                            while (lo < hi && a[hi] == a[hi + 1]) hi--;
                        }
                    }
                }
                free(a);

                *returnSize = count;
                *returnColumnSizes = malloc((count ? count : 1) * sizeof(int));
                for (int i = 0; i < count; i++) (*returnColumnSizes)[i] = 3;
                if (!res) res = malloc(sizeof(long long*));        // empty result: still a valid pointer
                return res;
            }
        """),
        "cpp": _d(r"""
            vector<vector<long long>> threeSum(vector<long long>& nums) {
                sort(nums.begin(), nums.end());
                int n = nums.size();
                vector<vector<long long>> out;
                for (int i = 0; i + 2 < n; i++) {
                    if (nums[i] > 0) break;                          // smallest is positive
                    if (i > 0 && nums[i] == nums[i - 1]) continue;   // duplicate first value
                    int lo = i + 1, hi = n - 1;
                    while (lo < hi) {
                        long long s = nums[i] + nums[lo] + nums[hi];
                        if (s < 0) lo++;
                        else if (s > 0) hi--;
                        else {
                            out.push_back({nums[i], nums[lo], nums[hi]});
                            lo++; hi--;
                            while (lo < hi && nums[lo] == nums[lo - 1]) lo++;
                            while (lo < hi && nums[hi] == nums[hi + 1]) hi--;
                        }
                    }
                }
                return out;
            }
        """),
        "rust": _d(r"""
            pub fn three_sum(mut nums: Vec<i64>) -> Vec<Vec<i64>> {
                nums.sort_unstable();
                let n = nums.len();
                let mut out = Vec::new();
                for i in 0..n.saturating_sub(2) {
                    if nums[i] > 0 { break; }
                    if i > 0 && nums[i] == nums[i - 1] { continue; }
                    let (mut lo, mut hi) = (i + 1, n - 1);
                    while lo < hi {
                        let s = nums[i] + nums[lo] + nums[hi];
                        if s < 0 { lo += 1; }
                        else if s > 0 { hi -= 1; }
                        else {
                            out.push(vec![nums[i], nums[lo], nums[hi]]);
                            lo += 1;
                            hi -= 1;
                            while lo < hi && nums[lo] == nums[lo - 1] { lo += 1; }
                            while lo < hi && nums[hi] == nums[hi + 1] { hi -= 1; }
                        }
                    }
                }
                out
            }
        """),
    },
    tests=[
        [[-1, 0, 1, 2, -1, -4]],
        [[0, 1, 1]],
        [[0, 0, 0]],
        [[0, 0, 0, 0]],
        [[]],
        [[-2, 0, 0, 2, 2]],
        [[-4, -2, -2, -2, 0, 1, 2, 2, 2, 3, 3, 4, 4, 6, 6]],
        [[1, 2, -3]],
        [[_r.randint(-20, 20) for _ in range(60)]],
        [[_r.randint(-20000, 20000) for _ in range(400)]],
    ],
))

# ----------------------------------------------------------------------------- 7
_r = random.Random(507)
PROBLEMS.append(dict(
    id="rotate-array",
    title="Rotate Array",
    difficulty=2,
    tags=["array", "in-place", "math"],
    fn="rotate",
    params=[["nums", "int[]"], ["k", "int"]],
    returns="void",
    mutates="nums",
    statement=_d(r"""
Rotate `nums` to the **right** by `k` steps, in place. One step moves the last element
to the front: `[1, 2, 3, 4]` → `[4, 1, 2, 3]`.

`k` may be larger than the array length. Aim for O(1) extra memory.
"""),
    example_notes=[
        "Three right rotations: `[1..7]` → `[7,1..6]` → `[6,7,1..5]` → `[5,6,7,1,2,3,4]`.",
        "`k = 4` on a length-2 array is a full cycle twice: nothing changes.",
    ],
    constraints=["1 ≤ len(nums) ≤ 10⁵", "0 ≤ k ≤ 10⁹"],
    hints=[
        "Rotating by `n` gives back the original array. Reduce `k` first.",
        "After rotation, the last `k` elements are at the front (in order) followed by the first `n-k`. Can you get there by reversing things?",
        "Reverse the whole array, then reverse the first `k` elements, then reverse the remaining `n-k`.",
    ],
    explanation=_d(r"""
## Intuition

With a spare array this is easy: `out[(i + k) % n] = nums[i]`. Doing it in O(1) memory
takes a trick. Write the array as two blocks: `A` = first `n−k` elements, `B` = last
`k`. We have `A B` and want `B A`.

Reversal has a neat property: `reverse(A B) = rev(B) rev(A)`. The blocks swap places,
but each is backwards. Reverse each block individually and you're done:

```
  A B          1 2 3 4 5 | 6 7       (k = 2)
  rev all      7 6 | 5 4 3 2 1
  rev first k  6 7 | 5 4 3 2 1
  rev rest     6 7 | 1 2 3 4 5   =  B A
```

## Approach

1. `k %= n`: rotating by `n` is the identity, and huge `k` would index out of bounds.
2. `reverse(0, n-1)`, `reverse(0, k-1)`, `reverse(k, n-1)`, where `reverse(i, j)` swaps
   inward with two pointers.

## Complexity

- **Time:** O(n). Each element is swapped twice.
- **Space:** O(1).

## Common mistakes

- **Forgetting `k %= n`.** With `k = 10⁹` you either index out of range or loop forever
  if you rotate one step at a time.
- **Rotating one step k times:** O(n·k), far too slow.
- **Left vs right:** reversing the first `k` *before* the whole array gives a left
  rotation instead.
- **Python rebinding:** `nums = nums[-k:] + nums[:-k]` doesn't change the caller's list,
  and with `k == 0`, `nums[-0:]` is the *whole* list. `nums[:] = nums[n-k:] + nums[:n-k]`
  is a correct O(n)-memory one-liner.

## Going further

- **Cyclic replacements:** move each element directly to `(i+k) % n`, following cycles;
  there are `gcd(n, k)` cycles. Also O(n)/O(1) but subtler.
- C++ has `std::rotate`, Rust has `slice::rotate_right`; both are worth knowing (and both
  are O(n), in place).
- The triple-reversal trick also rotates words in a sentence: reverse the whole string,
  then reverse each word.
"""),
    solution=_d(r"""
def rotate(nums, k):
    n = len(nums)
    # Rotating by a multiple of n changes nothing; this also keeps the
    # indices below in range when k >= n.
    k %= n

    def reverse(i, j):
        # Classic two-pointer reversal of nums[i..j] (inclusive).
        while i < j:
            nums[i], nums[j] = nums[j], nums[i]
            i += 1
            j -= 1

    # [A | B] -> reverse all -> [rev B | rev A] -> fix each block -> [B | A]
    reverse(0, n - 1)
    reverse(0, k - 1)
    reverse(k, n - 1)
"""),
    refs={
        "c": _d(r"""
            static void rev(long long* a, int i, int j) {
                while (i < j) { long long t = a[i]; a[i++] = a[j]; a[j--] = t; }
            }
            void rotate(long long* nums, int numsSize, long long k) {
                int r = (int)(k % numsSize);       // reduce k first
                rev(nums, 0, numsSize - 1);        // [A B] -> [rB rA]
                rev(nums, 0, r - 1);               // -> [B rA]
                rev(nums, r, numsSize - 1);        // -> [B A]
            }
        """),
        "cpp": _d(r"""
            void rotate(vector<long long>& nums, long long k) {
                k %= (long long)nums.size();
                reverse(nums.begin(), nums.end());
                reverse(nums.begin(), nums.begin() + k);
                reverse(nums.begin() + k, nums.end());
                // or simply: std::rotate(nums.begin(), nums.end() - k, nums.end());
            }
        """),
        "rust": _d(r"""
            pub fn rotate(nums: &mut Vec<i64>, k: i64) {
                let n = nums.len();
                let k = (k as usize) % n;
                nums.reverse();
                nums[..k].reverse();
                nums[k..].reverse();
                // equivalent: nums.rotate_right(k);
            }
        """),
        "espresso": _d(r"""
            fn reverseRange(a, i, j) {
              while i < j {
                var t = a[i]
                a[i] = a[j]
                a[j] = t
                i += 1
                j -= 1
              }
            }

            fn rotate(nums, k) {
              var n = len(nums)
              var r = k - (k / n) * n   // k mod n (no % operator)
              reverseRange(nums, 0, n - 1)
              reverseRange(nums, 0, r - 1)
              reverseRange(nums, r, n - 1)
            }
        """),
    },
    tests=[
        [[1, 2, 3, 4, 5, 6, 7], 3],
        [[1, 2], 4],
        [[-1, -100, 3, 99], 2],
        [[5], 9999999],
        [[1, 2, 3], 0],
        [[1, 2, 3], 3],
        [[1, 2, 3, 4, 5, 6], 7],
        [[_r.randint(-1000, 1000) for _ in range(60)], 12345678],
    ],
))

# ----------------------------------------------------------------------------- 8
_r = random.Random(508)
PROBLEMS.append(dict(
    id="best-time-to-buy-sell-stock",
    title="Best Time to Buy and Sell Stock",
    difficulty=1,
    tags=["array", "greedy", "running state"],
    fn="max_profit",
    params=[["prices", "int[]"]],
    returns="int",
    statement=_d(r"""
`prices[i]` is a stock's price on day `i`. You may buy one share on some day and sell it
on a **later** day. Return the maximum profit you can make; if no profit is possible,
return `0` (you just don't trade).
"""),
    example_notes=[
        "Buy at 1 (day 1), sell at 6 (day 4): profit 5. Selling at 7 on day 0 isn't allowed because it's before the purchase.",
        "Prices only fall: the best move is not to trade.",
    ],
    constraints=["1 ≤ len(prices) ≤ 10⁵", "0 ≤ prices[i] ≤ 10⁴"],
    hints=[
        "If you knew you'd sell on day `j`, which day should you have bought on?",
        "The best buy day for a sale on day `j` is the cheapest day before `j`. Can you maintain that as you sweep?",
        "Keep `min_so_far`. For each price, profit candidate = `price - min_so_far`; then update `min_so_far`.",
    ],
    explanation=_d(r"""
## Intuition

The brute force tries every (buy, sell) pair: O(n²). But fix the *sell* day `j`: the
best buy day is obviously the cheapest price among days `0..j−1`. So as we sweep left to
right, the only thing we need to remember about the past is **the minimum price so
far**. That's the "running state" pattern from the intro.

## Approach

```
min_price = +infinity
best = 0
for p in prices:
    best = max(best, p - min_price)   # sell today, bought at the cheapest earlier day
    min_price = min(min_price, p)     # today might be the cheapest buy for the future
```

Order matters a little: update `best` before `min_price` so you never "buy and sell on
the same day" (which would only give profit 0 anyway, so either order happens to work
here; in variants it won't).

Trace on `[7, 1, 5, 3, 6, 4]`:

| day | price | min before | profit if sold | best |
|---|---|---|---|---|
| 0 | 7 | ∞ | – | 0 |
| 1 | 1 | 7 | -6 | 0 |
| 2 | 5 | 1 | 4 | 4 |
| 3 | 3 | 1 | 2 | 4 |
| 4 | 6 | 1 | 5 | **5** |
| 5 | 4 | 1 | 3 | 5 |

## Complexity

- **Time:** O(n), one pass.
- **Space:** O(1).

## Common mistakes

- **Taking `max(prices) - min(prices)`.** The max may come *before* the min
  (`[7, 1]` → 0, not 6).
- **Returning a negative number** when prices only fall. Start `best` at 0.
- **Initialising `min_price = 0`.** Then every price looks profitable. Use the first
  price or infinity.
- **Language mechanics:** in C/C++ use `LLONG_MAX` (from `<climits>`/`<limits.h>`) as
  infinity; in Rust, `i64::MAX`. Careful: `p - i64::MAX` is fine, but
  `i64::MAX - p` style expressions with negative `p` would overflow.

## Going further

- **Unlimited transactions** (Stock II): sum every positive day-to-day increase.
- This is Kadane's algorithm in disguise: the profit is the maximum subarray sum of
  the *differences* `prices[i] - prices[i-1]`.
- With at most k transactions or cooldowns it becomes a small dynamic programming
  state machine.
"""),
    solution=_d(r"""
def max_profit(prices):
    # The only fact about the past we need: the cheapest price seen so far.
    min_price = float("inf")
    best = 0  # not trading is always allowed, so profit never goes below 0
    for p in prices:
        # Best profit if we sell today: buy at the cheapest earlier day.
        best = max(best, p - min_price)
        # Today may be the cheapest buy day for future sales.
        min_price = min(min_price, p)
    return best
"""),
    refs={
        "c": _d(r"""
            long long max_profit(long long* prices, int pricesSize) {
                long long min_price = prices[0], best = 0;
                for (int i = 1; i < pricesSize; i++) {
                    if (prices[i] - min_price > best) best = prices[i] - min_price;
                    if (prices[i] < min_price) min_price = prices[i];
                }
                return best;
            }
        """),
        "cpp": _d(r"""
            long long maxProfit(vector<long long>& prices) {
                long long minPrice = LLONG_MAX, best = 0;
                for (long long p : prices) {
                    if (minPrice != LLONG_MAX) best = max(best, p - minPrice);
                    minPrice = min(minPrice, p);
                }
                return best;
            }
        """),
        "rust": _d(r"""
            pub fn max_profit(prices: Vec<i64>) -> i64 {
                let mut min_price = prices[0];
                let mut best = 0;
                for &p in &prices[1..] {
                    best = best.max(p - min_price);
                    min_price = min_price.min(p);
                }
                best
            }
        """),
        "espresso": _d(r"""
            fn maxProfit(prices) {
              var minPrice = prices[0]
              var best = 0
              for var i in 1..len(prices) {
                var p = prices[i]
                if p - minPrice > best { best = p - minPrice }
                if p < minPrice { minPrice = p }
              }
              return best
            }
        """),
    },
    tests=[
        [[7, 1, 5, 3, 6, 4]],
        [[7, 6, 4, 3, 1]],
        [[5]],
        [[1, 2]],
        [[2, 4, 1]],
        [[3, 3, 3, 3]],
        [[2, 1, 2, 1, 0, 1, 2]],
        [[_r.randint(0, 10**4) for _ in range(80)]],
    ],
))

# ----------------------------------------------------------------------------- 9
_r = random.Random(509)
PROBLEMS.append(dict(
    id="maximum-subarray-kadane",
    title="Maximum Subarray",
    difficulty=2,
    # Large tests (complexity matters here) exceed the ESPresso VM constant-pool limit.
    espresso=False,
    tags=["array", "dynamic programming", "kadane"],
    fn="max_subarray",
    params=[["nums", "int[]"]],
    returns="int",
    statement=_d(r"""
Return the largest possible sum of a **non-empty contiguous** subarray of `nums`.
"""),
    example_notes=[
        "`[4, -1, 2, 1]` sums to 6.",
        "All values negative: the best you can do is the single largest element.",
    ],
    constraints=["1 ≤ len(nums) ≤ 10⁵", "-10⁴ ≤ nums[i] ≤ 10⁴"],
    hints=[
        "Let `best_here` be the best sum of a subarray that **ends exactly at** index `i`. How does it relate to `best_here` at `i - 1`?",
        "A subarray ending at `i` either is just `[nums[i]]` or extends the best one ending at `i-1`. Pick whichever is larger.",
        "`cur = max(nums[i], cur + nums[i])`; `best = max(best, cur)`. Initialise both with `nums[0]`.",
    ],
    explanation=_d(r"""
## Intuition

Every subarray ends somewhere. If for each index `i` we knew `cur[i]` = the best sum of
a subarray **ending at `i`**, the answer would be `max(cur)`.

And `cur[i]` is easy to get from `cur[i-1]`: a subarray ending at `i` is either just
`nums[i]` alone, or `nums[i]` glued onto some subarray ending at `i-1`, and the best
such is `cur[i-1]`. So

```
cur[i] = max(nums[i], cur[i-1] + nums[i])
```

In words: **if the running sum has gone negative, it's dead weight; drop it and start
fresh.** That's Kadane's algorithm, a one-variable dynamic program.

## Approach

```
cur = best = nums[0]
for x in nums[1:]:
    cur = max(x, cur + x)
    best = max(best, cur)
```

Trace on `[-2, 1, -3, 4, -1, 2, 1, -5, 4]`:

| x | cur + x | cur = max(x, cur+x) | best |
|---|---|---|---|
| -2 | – | -2 | -2 |
| 1 | -1 | **1** (restart) | 1 |
| -3 | -2 | -2 | 1 |
| 4 | 2 | **4** (restart) | 4 |
| -1 | 3 | 3 | 4 |
| 2 | 5 | 5 | 5 |
| 1 | 6 | 6 | **6** |
| -5 | 1 | 1 | 6 |
| 4 | 5 | 5 | 6 |

## Complexity

- **Time:** O(n).
- **Space:** O(1): we only keep `cur[i-1]`, not the whole table.

## Common mistakes

- **Starting `best` at 0.** For an all-negative array the answer is the largest element
  (e.g. -1), not 0, because the subarray must be non-empty.
- **Resetting `cur` to 0 when negative, then comparing.** The "reset to 0" variant
  (`cur = max(0, cur + x)`) is fine only if you update `best` *before* clamping, or
  you'll lose all-negative cases.
- **Brute force** over all (i, j) with prefix sums is O(n²); without prefix sums O(n³).

## Going further

- Return the subarray's bounds too: remember where the current run started whenever you
  restart.
- **Divide and conquer** gives O(n log n): best is in the left half, the right half, or
  crosses the middle. A good exercise, and the basis of segment-tree versions that answer
  "max subarray in range [l, r]" queries.
- **Maximum circular subarray:** `max(kadane, total - min_subarray)` (careful when all
  elements are negative).
"""),
    solution=_d(r"""
def max_subarray(nums):
    # cur = best sum of a subarray that ends exactly at the current index.
    # best = best sum seen anywhere so far.
    # Both start at nums[0]: the subarray must be non-empty.
    cur = best = nums[0]
    for x in nums[1:]:
        # Either extend the best run ending at the previous index, or start a
        # new run at x. If cur < 0 it only drags x down, so we restart.
        cur = max(x, cur + x)
        best = max(best, cur)
    return best
"""),
    refs={
        "c": _d(r"""
            long long max_subarray(long long* nums, int numsSize) {
                long long cur = nums[0], best = nums[0];
                for (int i = 1; i < numsSize; i++) {
                    cur = (cur + nums[i] > nums[i]) ? cur + nums[i] : nums[i];  // extend or restart
                    if (cur > best) best = cur;
                }
                return best;
            }
        """),
        "cpp": _d(r"""
            long long maxSubarray(vector<long long>& nums) {
                long long cur = nums[0], best = nums[0];
                for (size_t i = 1; i < nums.size(); i++) {
                    cur = max(nums[i], cur + nums[i]);
                    best = max(best, cur);
                }
                return best;
            }
        """),
        "rust": _d(r"""
            pub fn max_subarray(nums: Vec<i64>) -> i64 {
                let (mut cur, mut best) = (nums[0], nums[0]);
                for &x in &nums[1..] {
                    cur = x.max(cur + x);
                    best = best.max(cur);
                }
                best
            }
        """),
    },
    tests=[
        [[-2, 1, -3, 4, -1, 2, 1, -5, 4]],
        [[-3, -1, -2]],
        [[1]],
        [[5, 4, -1, 7, 8]],
        [[-1]],
        [[0, -1, 0]],
        [[2, -1, 2, -1, 2]],
        [[-5, 10, -20, 15, -1, 6, -30, 8]],
        [[_r.randint(-10**4, 10**4) for _ in range(8000)]],
    ],
))

# ---------------------------------------------------------------------------- 10
def _prod_case(r, n):
    while True:
        a = [r.choice([1, 1, 1, -1, -1, 2, -2, 0]) if r.random() < 0.02 else r.choice([1, -1]) for _ in range(n)]
        m = 1
        for x in a:
            if x:
                m *= abs(x)
        if m < 2**30:
            return [a]


_r = random.Random(510)
PROBLEMS.append(dict(
    id="product-of-array-except-self",
    title="Product of Array Except Self",
    difficulty=2,
    tags=["array", "prefix sums"],
    fn="product_except_self",
    params=[["nums", "int[]"]],
    returns="int[]",
    statement=_d(r"""
Return an array `answer` where `answer[i]` is the product of every element of `nums`
**except** `nums[i]`.

You may **not** use division, and the algorithm should run in O(n) time. The products
(including all prefix and suffix products) are guaranteed to fit in a 32-bit signed
integer.
"""),
    example_notes=[
        "For index 0: 2·3·4 = 24; index 1: 1·3·4 = 12; and so on.",
        "A single zero makes every other product 0, while its own slot gets the product of the rest.",
    ],
    constraints=["2 ≤ len(nums) ≤ 10⁵", "-30 ≤ nums[i] ≤ 30", "all prefix/suffix products fit in 32 bits"],
    hints=[
        "`answer[i]` = (product of everything left of `i`) × (product of everything right of `i`).",
        "Compute the left products in one pass and the right products in another. That's prefix sums, but with multiplication.",
        "To use O(1) extra space, store the left products directly in `answer`, then sweep from the right with a single running variable `right` and multiply it in.",
    ],
    explanation=_d(r"""
## Intuition

With division it'd be `total / nums[i]`, but that breaks on zeros and is forbidden
anyway. Instead split the product around `i`:

```
nums    =  a0  a1  a2 [a3] a4  a5
answer3 = (a0·a1·a2) · (a4·a5)
          \_ left _/   \right/
```

"Product of everything to the left" is a **prefix product**, the multiplicative
cousin of the prefix sum from the intro. Same for the right with a suffix product.

## Approach

1. `answer[i] = left[i]` where `left[0] = 1` and `left[i] = left[i-1] * nums[i-1]`.
2. Sweep from the right with `right = 1`: `answer[i] *= right`, then `right *= nums[i]`.

Trace on `[1, 2, 3, 4]`:

| i | left product | right product | answer |
|---|---|---|---|
| 0 | 1 | 2·3·4 = 24 | 24 |
| 1 | 1 | 3·4 = 12 | 12 |
| 2 | 1·2 = 2 | 4 | 8 |
| 3 | 1·2·3 = 6 | 1 | 6 |

The empty product is 1, which is why `left[0]` and the initial `right` are 1: no special
cases for the ends.

## Complexity

- **Time:** O(n), two passes.
- **Space:** O(1) extra besides the output array (it's customary not to count the
  output).

## Common mistakes

- **Using division** and then patching zeros: one zero, two zeros and no zeros all need
  different handling. The prefix/suffix approach handles them uniformly.
- **Updating `right` before multiplying** shifts everything by one and includes
  `nums[i]` in its own product.
- **O(n²)** "multiply everything except i" loops time out at n = 10⁵.
- **Overflow:** the guarantee here keeps products small; in general you'd use 64-bit
  integers or modular arithmetic.

## Going further

The "prefix from the left, suffix from the right" decomposition shows up in Trapping Rain
Water (max-from-left and max-from-right), "maximum product subarray", and range queries
with any associative operation (min, gcd, xor).
"""),
    solution=_d(r"""
def product_except_self(nums):
    n = len(nums)
    # Pass 1: answer[i] = product of nums[0..i-1]. The empty product is 1,
    # so answer[0] = 1 and there's no special case for the left edge.
    answer = [1] * n
    for i in range(1, n):
        answer[i] = answer[i - 1] * nums[i - 1]
    # Pass 2: sweep from the right, keeping the product of nums[i+1..n-1] in a
    # single variable. Multiply it in *before* absorbing nums[i] so that
    # nums[i] itself is never included in answer[i].
    right = 1
    for i in range(n - 1, -1, -1):
        answer[i] *= right
        right *= nums[i]
    return answer
"""),
    refs={
        "c": _d(r"""
            long long* product_except_self(long long* nums, int numsSize, int* returnSize) {
                long long* ans = malloc(sizeof(long long) * numsSize);
                ans[0] = 1;
                for (int i = 1; i < numsSize; i++) ans[i] = ans[i - 1] * nums[i - 1];  // left products
                long long right = 1;
                for (int i = numsSize - 1; i >= 0; i--) {   // fold in right products
                    ans[i] *= right;
                    right *= nums[i];
                }
                *returnSize = numsSize;
                return ans;
            }
        """),
        "cpp": _d(r"""
            vector<long long> productExceptSelf(vector<long long>& nums) {
                int n = nums.size();
                vector<long long> ans(n, 1);
                for (int i = 1; i < n; i++) ans[i] = ans[i - 1] * nums[i - 1];
                long long right = 1;
                for (int i = n - 1; i >= 0; i--) { ans[i] *= right; right *= nums[i]; }
                return ans;
            }
        """),
        "rust": _d(r"""
            pub fn product_except_self(nums: Vec<i64>) -> Vec<i64> {
                let n = nums.len();
                let mut ans = vec![1i64; n];
                for i in 1..n {
                    ans[i] = ans[i - 1] * nums[i - 1];
                }
                let mut right = 1i64;
                for i in (0..n).rev() {
                    ans[i] *= right;
                    right *= nums[i];
                }
                ans
            }
        """),
    },
    tests=[
        [[1, 2, 3, 4]],
        [[-1, 1, 0, -3, 3]],
        [[0, 0]],
        [[2, 3]],
        [[0, 4, 5]],
        [[-2, -3, 4, -1]],
        [[1, 1, 1, 1, 1]],
        _prod_case(_r, 5000),
    ],
))

# ---------------------------------------------------------------------------- 11
def _range_case(r, n, q, lo, hi):
    a = [r.randint(lo, hi) for _ in range(n)]
    qs = []
    for _ in range(q):
        i, j = sorted((r.randrange(n), r.randrange(n)))
        qs.append([i, j])
    return [a, qs]


_r = random.Random(511)
PROBLEMS.append(dict(
    id="range-sum-queries",
    title="Range Sum Queries",
    difficulty=1,
    tags=["array", "prefix sums"],
    fn="range_sum_queries",
    params=[["nums", "int[]"], ["queries", "int[][]"]],
    returns="int[]",
    statement=_d(r"""
You are given an array `nums` and a list of queries. Each query is a pair `[l, r]` with
`0 ≤ l ≤ r < len(nums)`, asking for

```
nums[l] + nums[l+1] + ... + nums[r]
```

Return the answers to all queries, in order. The array doesn't change between queries,
so precompute something that makes every query O(1).
"""),
    example_notes=[
        "`[0,2]` → -2 + 0 + 3 = 1; `[2,5]` → 3 - 5 + 2 - 1 = -1; `[0,5]` → -3.",
        "A query with `l == r` is just one element.",
    ],
    constraints=["1 ≤ len(nums) ≤ 10⁴", "0 ≤ len(queries) ≤ 10⁴", "-10⁵ ≤ nums[i] ≤ 10⁵"],
    hints=[
        "Summing each range from scratch costs O(r - l). With many queries that's O(n·q).",
        "If you knew the sum of the first `r+1` elements and the sum of the first `l` elements, how would you get the range sum?",
        "Build `P` with `P[0] = 0` and `P[i+1] = P[i] + nums[i]`. Then `sum(l..r) = P[r+1] - P[l]`.",
    ],
    explanation=_d(r"""
## Intuition

The array is fixed and there are many queries: classic **precompute once, answer fast**.
A prefix-sum array `P` where `P[i]` is the sum of the first `i` elements turns every
range sum into one subtraction: the elements before `l` cancel out.

```
nums =    [-2,  0,  3, -5,  2, -1]
P    = [0, -2, -2,  1, -4, -2, -3]
          ^ P[0] = 0: sum of the first 0 elements

sum(2..5) = P[6] - P[2] = -3 - (-2) = -1
```

## Approach

1. Build `P` of length `n + 1`: `P[0] = 0`, `P[i + 1] = P[i] + nums[i]`.
2. For each query `[l, r]`: answer `P[r + 1] - P[l]`.

The extra leading zero is the important design choice. Without it you'd need
`P[r] - P[l-1]` and a special case for `l == 0`. With it, `P` is a function of
*half-open* ranges: `sum(nums[l:r+1]) = P[r+1] - P[l]`.

## Complexity

- **Time:** O(n) to build, O(1) per query: O(n + q) total, versus O(n·q) for naive
  summing.
- **Space:** O(n) for `P`.

## Common mistakes

- **Off-by-one:** `P[r] - P[l]` misses `nums[r]`. Write the definition of `P[i]` down
  ("sum of the first `i` elements") and the formula follows.
- **Overflow:** sums of 10⁴ values up to 10⁵ reach 10⁹; fine in 64-bit, borderline in
  32-bit. Use `long long` / `i64`.
- **Python:** `itertools.accumulate(nums, initial=0)` builds `P` in one line.

## Going further

- **2-D prefix sums** answer rectangle-sum queries in O(1) with inclusion-exclusion:
  `S = P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]`.
- If the array *changes* between queries, prefix sums need O(n) per update; a Fenwick
  tree or segment tree gives O(log n) for both.
- **Difference arrays** are the inverse trick: many "add v to range [l, r]" updates in
  O(1) each, then one prefix-sum pass to materialise.
"""),
    solution=_d(r"""
def range_sum_queries(nums, queries):
    # P[i] = sum of the first i elements (nums[0..i-1]). The leading 0 means
    # a range starting at index 0 needs no special case.
    P = [0] * (len(nums) + 1)
    for i, x in enumerate(nums):
        P[i + 1] = P[i] + x
    # Everything before l appears in both P[r+1] and P[l], so it cancels.
    return [P[r + 1] - P[l] for l, r in queries]
"""),
    refs={
        "c": _d(r"""
            long long* range_sum_queries(long long* nums, int numsSize, long long** queries, int queriesSize, int* queriesColSize, int* returnSize) {
                long long* P = malloc(sizeof(long long) * (numsSize + 1));
                P[0] = 0;
                for (int i = 0; i < numsSize; i++) P[i + 1] = P[i] + nums[i];
                long long* out = malloc(sizeof(long long) * (queriesSize > 0 ? queriesSize : 1));
                for (int q = 0; q < queriesSize; q++) {
                    long long l = queries[q][0], r = queries[q][1];
                    out[q] = P[r + 1] - P[l];
                }
                free(P);
                *returnSize = queriesSize;
                return out;
            }
        """),
        "cpp": _d(r"""
            vector<long long> rangeSumQueries(vector<long long>& nums, vector<vector<long long>>& queries) {
                vector<long long> P(nums.size() + 1, 0);
                partial_sum(nums.begin(), nums.end(), P.begin() + 1);   // P[i+1] = P[i] + nums[i]
                vector<long long> out;
                out.reserve(queries.size());
                for (auto& q : queries) out.push_back(P[q[1] + 1] - P[q[0]]);
                return out;
            }
        """),
        "rust": _d(r"""
            pub fn range_sum_queries(nums: Vec<i64>, queries: Vec<Vec<i64>>) -> Vec<i64> {
                let mut p = vec![0i64; nums.len() + 1];
                for (i, &x) in nums.iter().enumerate() {
                    p[i + 1] = p[i] + x;
                }
                queries
                    .iter()
                    .map(|q| p[q[1] as usize + 1] - p[q[0] as usize])
                    .collect()
            }
        """),
    },
    tests=[
        [[-2, 0, 3, -5, 2, -1], [[0, 2], [2, 5], [0, 5]]],
        [[5, 7, 9], [[1, 1], [0, 0], [2, 2]]],
        [[4], [[0, 0]]],
        [[1, 2, 3], []],
        [[100000, 100000, 100000, -100000], [[0, 3], [1, 2], [3, 3]]],
        [[0, 0, 0, 0], [[0, 3], [1, 2]]],
        _range_case(_r, 50, 30, -10, 10),
        _range_case(_r, 3000, 2000, 0, 99),
    ],
))

# ---------------------------------------------------------------------------- 12
_r = random.Random(512)
PROBLEMS.append(dict(
    id="running-sum-array",
    title="Running Sum of an Array",
    difficulty=1,
    tags=["array", "prefix sums"],
    fn="running_sum",
    params=[["nums", "int[]"]],
    returns="int[]",
    statement=_d(r"""
Return the **running sum** of `nums`: an array `out` of the same length where
`out[i] = nums[0] + nums[1] + ... + nums[i]`.
"""),
    example_notes=[
        "`[1, 1+2, 1+2+3, 1+2+3+4]`.",
        "Negative numbers simply reduce the total.",
    ],
    constraints=["0 ≤ len(nums) ≤ 10⁴", "-10⁶ ≤ nums[i] ≤ 10⁶"],
    hints=[
        "`out[i]` and `out[i-1]` differ by exactly one term.",
        "Keep a running `total`; add each element to it and append it.",
    ],
    explanation=_d(r"""
## Intuition

Recomputing `nums[0] + ... + nums[i]` for each `i` from scratch costs
1 + 2 + ... + n = O(n²) additions. But consecutive running sums overlap almost
completely:

```
out[i] = (nums[0] + ... + nums[i-1]) + nums[i] = out[i-1] + nums[i]
```

So carry one number, the total so far, through the loop. This is the simplest
example of the **running state** idea, and it *is* the prefix-sum array from the
intro (without the leading 0).

## Approach

```python
total = 0
out = []
for x in nums:
    total += x        # total is now nums[0] + ... + x
    out.append(total)
```

Trace on `[3, 1, 2, 10, 1]`:

| x | total after | out |
|---|---|---|
| 3 | 3 | [3] |
| 1 | 4 | [3, 4] |
| 2 | 6 | [3, 4, 6] |
| 10 | 16 | [3, 4, 6, 16] |
| 1 | 17 | [3, 4, 6, 16, 17] |

**Language mechanics.** In Python, `out.append` grows the list (amortised O(1)). In C you
must know the size up front: `malloc(n * sizeof(long long))`, fill it, and report the
length through `*returnSize`, because a bare pointer doesn't carry its length. In Rust,
`Vec::with_capacity(n)` avoids reallocations, and iterator adapters like `scan` express
"carry state through a loop" directly.

## Complexity

- **Time:** O(n).
- **Space:** O(n) for the output (O(1) extra if you overwrite `nums` in place).

## Common mistakes

- **Appending before adding**, which shifts everything by one and drops the last sum.
- **C:** `malloc(0)` may return `NULL` for empty input; that's fine as long as
  `*returnSize = 0`, but never dereference it.
- **Overflow:** 10⁴ values of 10⁶ reach 10¹⁰: too big for 32-bit `int`. The harness
  uses 64-bit types; keep that habit.

## Going further

Python's `itertools.accumulate(nums)` does exactly this, and C++ has
`std::partial_sum`. Once you have running sums, any range sum is a subtraction; see
Range Sum Queries.
"""),
    solution=_d(r"""
def running_sum(nums):
    out = []
    total = 0  # sum of every element processed so far
    for x in nums:
        # Each running sum is the previous one plus one new element, so we
        # never re-add earlier elements: O(n) instead of O(n^2).
        total += x
        out.append(total)
    return out
"""),
    refs={
        "c": _d(r"""
            long long* running_sum(long long* nums, int numsSize, int* returnSize) {
                // A C array doesn't know its length, so we report it via *returnSize.
                long long* out = malloc(sizeof(long long) * (numsSize > 0 ? numsSize : 1));
                long long total = 0;
                for (int i = 0; i < numsSize; i++) {
                    total += nums[i];
                    out[i] = total;
                }
                *returnSize = numsSize;
                return out;
            }
        """),
        "cpp": _d(r"""
            vector<long long> runningSum(vector<long long>& nums) {
                vector<long long> out(nums.size());
                partial_sum(nums.begin(), nums.end(), out.begin());  // <numeric>
                return out;
            }
        """),
        "rust": _d(r"""
            pub fn running_sum(nums: Vec<i64>) -> Vec<i64> {
                // scan carries `total` through the iteration and yields each running value.
                nums.iter()
                    .scan(0i64, |total, &x| {
                        *total += x;
                        Some(*total)
                    })
                    .collect()
            }
        """),
    },
    tests=[
        [[1, 2, 3, 4]],
        [[3, 1, 2, 10, 1]],
        [[]],
        [[7]],
        [[1, -1, 1, -1]],
        [[-5, -5, -5]],
        [[1000000] * 20],
        [[_r.randint(-10**6, 10**6) for _ in range(2500)]],
    ],
))

# ---------------------------------------------------------------------------- 13
_r = random.Random(513)
PROBLEMS.append(dict(
    id="squares-of-sorted-array",
    title="Squares of a Sorted Array",
    difficulty=1,
    tags=["array", "two pointers"],
    fn="sorted_squares",
    params=[["nums", "int[]"]],
    returns="int[]",
    statement=_d(r"""
`nums` is sorted in non-decreasing order and may contain negative numbers. Return the
squares of its elements, also sorted in non-decreasing order.

Squaring then sorting is O(n log n); find an O(n) approach.
"""),
    example_notes=[
        "Squares are `[16, 1, 0, 9, 100]`; sorted: `[0, 1, 9, 16, 100]`.",
        "All negative: the order of the squares is reversed.",
    ],
    constraints=["0 ≤ len(nums) ≤ 10⁴", "-10⁴ ≤ nums[i] ≤ 10⁴", "`nums` is sorted"],
    hints=[
        "Where in the array is the largest square? (It's not necessarily at the end.)",
        "The largest absolute value is at one of the two ends. Fill the output from the back.",
        "Two pointers `L = 0`, `R = n-1`; compare `|nums[L]|` and `|nums[R]|`, write the larger square at position `k` (moving from `n-1` down), and move that pointer inward.",
    ],
    explanation=_d(r"""
## Intuition

Squaring destroys the order only for negatives: `-4 < -1` but `16 > 1`. Picture the
squares as a valley:

```
nums:     -4  -1   0   3  10
squares:  16   1   0   9  100
           \       /      /
            \_ 0 _/ ... _/      largest values are at the two ends
```

The **largest** square is always at one of the two ends; the smallest is somewhere in
the middle (hard to find). So build the answer from largest to smallest, writing into
the output from the back.

## Approach

```
L, R = 0, n - 1
for k from n-1 down to 0:
    if |nums[L]| > |nums[R]|: out[k] = nums[L]^2; L += 1
    else:                      out[k] = nums[R]^2; R -= 1
```

Trace on `[-4, -1, 0, 3, 10]`:

| L | R | compare | write at k | out |
|---|---|---|---|---|
| 0 | 4 | 4 vs **10** | 4 | `_ _ _ _ 100` |
| 0 | 3 | **4** vs 3 | 3 | `_ _ _ 16 100` |
| 1 | 3 | 1 vs **3** | 2 | `_ _ 9 16 100` |
| 1 | 2 | **1** vs 0 | 1 | `_ 1 9 16 100` |
| 2 | 2 | 0 vs **0** | 0 | `0 1 9 16 100` |

This is "merge two sorted lists" in disguise: the negatives (read right-to-left) and the
non-negatives (read left-to-right) are each sorted by absolute value.

## Complexity

- **Time:** O(n).
- **Space:** O(n) for the output.

## Common mistakes

- **Filling from the front:** the smallest square isn't at either end, so a front-fill
  needs to find the zero crossing first (doable, but more code).
- **`while L < R`** misses the last element; loop over `k` or use `L <= R`.
- **Overflow:** (10⁴)² = 10⁸ fits in 32 bits; with larger values use 64-bit.

## Going further

The same two-ended merge works for any function that is decreasing then increasing
(e.g. `a·x² + b·x + c` with `a > 0`, applied to a sorted array).
"""),
    solution=_d(r"""
def sorted_squares(nums):
    n = len(nums)
    out = [0] * n
    lo, hi = 0, n - 1
    # The largest remaining square is always at one of the two ends (the
    # most negative or the most positive value), so fill `out` from the back.
    for k in range(n - 1, -1, -1):
        if abs(nums[lo]) > abs(nums[hi]):
            out[k] = nums[lo] * nums[lo]
            lo += 1
        else:
            out[k] = nums[hi] * nums[hi]
            hi -= 1
    return out
"""),
    refs={
        "c": _d(r"""
            long long* sorted_squares(long long* nums, int numsSize, int* returnSize) {
                // The largest square sits at one of the two ends (most negative or most positive),
                // so fill the output from the back, taking the bigger end each time.
                long long* out = malloc((numsSize ? numsSize : 1) * sizeof(long long));
                int lo = 0, hi = numsSize - 1;
                for (int k = numsSize - 1; k >= 0; k--) {
                    if (llabs(nums[lo]) > llabs(nums[hi])) { out[k] = nums[lo] * nums[lo]; lo++; }
                    else                                   { out[k] = nums[hi] * nums[hi]; hi--; }
                }
                *returnSize = numsSize;
                return out;
            }
        """),
        "cpp": _d(r"""
            vector<long long> sortedSquares(vector<long long>& nums) {
                int n = nums.size(), lo = 0, hi = n - 1;
                vector<long long> out(n);
                for (int k = n - 1; k >= 0; k--) {
                    if (llabs(nums[lo]) > llabs(nums[hi])) { out[k] = nums[lo] * nums[lo]; lo++; }
                    else                                   { out[k] = nums[hi] * nums[hi]; hi--; }
                }
                return out;
            }
        """),
        "rust": _d(r"""
            pub fn sorted_squares(nums: Vec<i64>) -> Vec<i64> {
                let n = nums.len();
                let mut out = vec![0i64; n];
                if n == 0 { return out; }
                let (mut lo, mut hi) = (0usize, n - 1);
                for k in (0..n).rev() {
                    if nums[lo].abs() > nums[hi].abs() {
                        out[k] = nums[lo] * nums[lo];
                        lo += 1;
                    } else {
                        out[k] = nums[hi] * nums[hi];
                        // hi can reach 0 only on the very last iteration; avoid usize underflow
                        if hi > 0 { hi -= 1; }
                    }
                }
                out
            }
        """),
    },
    tests=[
        [[-4, -1, 0, 3, 10]],
        [[-7, -3, -2, -1]],
        [[]],
        [[0]],
        [[-5]],
        [[1, 2, 3]],
        [[-3, -3, 0, 3, 3]],
        [sorted(_r.randint(-10**4, 10**4) for _ in range(3500))],
    ],
))

# ---------------------------------------------------------------------------- 14
_r = random.Random(514)
PROBLEMS.append(dict(
    id="trapping-rain-water",
    title="Trapping Rain Water",
    difficulty=3,
    # Large tests (complexity matters here) exceed the ESPresso VM constant-pool limit.
    espresso=False,
    tags=["array", "two pointers", "prefix max"],
    fn="trap",
    params=[["height", "int[]"]],
    returns="int",
    statement=_d(r"""
`height` describes an elevation map: bar `i` has width 1 and height `height[i]`. After
it rains, water collects in the dips between bars. Return the total units of water
trapped.

```
height = [0,1,0,2,1,0,1,3,2,1,2,1]

          #
      #~~~##~#
    #~##~######        # = bar, ~ = trapped water (6 units)
    ------------
    012345678901       (index mod 10)
```
"""),
    example_notes=[
        "Water above each index: `[0,0,1,0,1,2,1,0,0,1,0,0]`, total 6.",
        "Valleys of depth 2, 3, 3, 2 between the walls of height 4 and 5: total 9.",
    ],
    constraints=["0 ≤ len(height) ≤ 2·10⁴", "0 ≤ height[i] ≤ 10⁵"],
    hints=[
        "Think about a single position `i`. How high can the water above it rise?",
        "Water at `i` = `min(max height to the left, max height to the right) - height[i]` (never negative). Two prefix-max passes give an O(n) / O(n)-space solution.",
        "For O(1) space: two pointers. If `left_max < right_max`, the water at `L` is fully determined by `left_max` (the right side is at least as tall). Process `L` and move it; otherwise process `R`.",
    ],
    explanation=_d(r"""
## Intuition

Don't think about "pools"; think **one column at a time**. The water above column `i`
rises until it would spill over the lower of the two walls that bound it: the tallest
bar to its left and the tallest bar to its right.

```
water[i] = min(maxLeft[i], maxRight[i]) - height[i]      (maxLeft/Right include i itself)
```

Including `i` in both maxima makes the result automatically ≥ 0.

### Step 1: prefix maxima (O(n) time, O(n) space)

Compute `maxLeft` left-to-right and `maxRight` right-to-left (prefix/suffix "max"
instead of "sum"), then sum the formula. This is already optimal in time.

### Step 2: two pointers (O(1) space)

We don't actually need both full arrays. Keep `L`, `R`, and the running maxima
`leftMax` (over `0..L`) and `rightMax` (over `R..n-1`).

If `leftMax < rightMax`: column `L`'s true right maximum is *at least* `rightMax`, which
is bigger than `leftMax`, so `min(maxLeft[L], maxRight[L]) = leftMax`. Column `L` is
fully determined: add `leftMax - height[L]` and advance `L`. Otherwise the symmetric
argument settles column `R`.

## Approach

```
L, R = 0, n-1; leftMax = rightMax = 0; water = 0
while L <= R:
    leftMax  = max(leftMax,  height[L])
    rightMax = max(rightMax, height[R])
    if leftMax < rightMax: water += leftMax - height[L]; L += 1
    else:                  water += rightMax - height[R]; R -= 1
```

Trace on `[4, 2, 0, 3, 2, 5]`:

| L | R | leftMax | rightMax | settle | +water |
|---|---|---|---|---|---|
| 0 | 5 | 4 | 5 | L=0 | 0 |
| 1 | 5 | 4 | 5 | L=1 | 2 |
| 2 | 5 | 4 | 5 | L=2 | 4 |
| 3 | 5 | 4 | 5 | L=3 | 1 |
| 4 | 5 | 4 | 5 | L=4 | 2 |
| 5 | 5 | 5 | 5 | R=5 | 0 |

Total 9.

## Complexity

- **Time:** O(n). Every column is settled exactly once.
- **Space:** O(1) for two pointers (O(n) for the prefix-max version).

## Common mistakes

- **Using the global maximum** for both sides: water is bounded by the *nearer-side*
  walls, not the tallest bar overall.
- **Per-column scans** for left/right maxima: O(n²), too slow at 2·10⁴ when combined
  with repeated work.
- **Confusing with Container With Most Water**, where in-between bars are ignored.
- **Empty input:** `R = -1`, the loop doesn't run; make sure nothing indexes
  `height[0]` before checking.

## Going further

- **Monotonic stack** solution: process bars left to right, popping shorter bars and
  filling "layers" of water horizontally. Also O(n), and the technique reappears in
  Largest Rectangle in Histogram.
- **Trapping Rain Water II** (2-D height map) needs a min-heap flood fill from the
  border, a beautiful generalisation of the two-pointer argument.
"""),
    solution=_d(r"""
def trap(height):
    lo, hi = 0, len(height) - 1
    left_max = right_max = 0  # tallest bar in height[0..lo] / height[hi..n-1]
    water = 0
    while lo <= hi:
        # Include the current bars in the running maxima first; this makes the
        # water amounts below automatically non-negative.
        left_max = max(left_max, height[lo])
        right_max = max(right_max, height[hi])
        if left_max < right_max:
            # Column lo's right wall is at least right_max > left_max, so its
            # water level is exactly left_max. Settle it and move on.
            water += left_max - height[lo]
            lo += 1
        else:
            # Symmetric: column hi's level is exactly right_max.
            water += right_max - height[hi]
            hi -= 1
    return water
"""),
    refs={
        "c": _d(r"""
            long long trap(long long* height, int heightSize) {
                int lo = 0, hi = heightSize - 1;
                long long leftMax = 0, rightMax = 0, water = 0;
                while (lo <= hi) {
                    if (height[lo] > leftMax) leftMax = height[lo];
                    if (height[hi] > rightMax) rightMax = height[hi];
                    if (leftMax < rightMax) water += leftMax - height[lo++];   // lo is settled
                    else                    water += rightMax - height[hi--];  // hi is settled
                }
                return water;
            }
        """),
        "cpp": _d(r"""
            long long trap(vector<long long>& height) {
                // Prefix/suffix max version: easier to see, O(n) extra space.
                int n = height.size();
                if (n == 0) return 0;
                vector<long long> L(n), R(n);
                L[0] = height[0];
                for (int i = 1; i < n; i++) L[i] = max(L[i - 1], height[i]);
                R[n - 1] = height[n - 1];
                for (int i = n - 2; i >= 0; i--) R[i] = max(R[i + 1], height[i]);
                long long water = 0;
                for (int i = 0; i < n; i++) water += min(L[i], R[i]) - height[i];
                return water;
            }
        """),
        "rust": _d(r"""
            pub fn trap(height: Vec<i64>) -> i64 {
                // Two pointers over a half-open window [lo, hi) to keep usize happy.
                let (mut lo, mut hi) = (0usize, height.len());
                let (mut left_max, mut right_max, mut water) = (0i64, 0i64, 0i64);
                while lo < hi {
                    left_max = left_max.max(height[lo]);
                    right_max = right_max.max(height[hi - 1]);
                    if left_max < right_max {
                        water += left_max - height[lo];
                        lo += 1;
                    } else {
                        water += right_max - height[hi - 1];
                        hi -= 1;
                    }
                }
                water
            }
        """),
    },
    tests=[
        [[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]],
        [[4, 2, 0, 3, 2, 5]],
        [[]],
        [[5]],
        [[1, 2, 3, 4, 5]],
        [[5, 4, 3, 2, 1]],
        [[3, 0, 3]],
        [[2, 0, 2, 0, 2, 0, 2]],
        [[5, 1, 1, 1, 1, 1, 6, 0, 0, 2]],
        [[_r.randint(0, 10**5) for _ in range(5000)]],
    ],
))

# ---------------------------------------------------------------------------- 15
_r = random.Random(515)
PROBLEMS.append(dict(
    id="next-permutation",
    title="Next Permutation",
    difficulty=2,
    tags=["array", "two pointers", "math"],
    fn="next_permutation",
    params=[["nums", "int[]"]],
    returns="void",
    mutates="nums",
    statement=_d(r"""
Rearrange `nums` **in place** into the next lexicographically greater permutation of its
values. If `nums` is already the largest arrangement (sorted in non-increasing order),
rearrange it into the smallest one (sorted ascending).

Lexicographic order compares arrays element by element, like words in a dictionary:
`[1,2,3] < [1,3,2] < [2,1,3] < [2,3,1] < [3,1,2] < [3,2,1]`. Duplicates are allowed;
equal arrangements count once. Use O(1) extra memory.
"""),
    example_notes=[
        "`[1,2,3]` → `[1,3,2]`.",
        "`[3,2,1]` is the last permutation, so wrap around to `[1,2,3]`.",
    ],
    constraints=["1 ≤ len(nums) ≤ 10⁴", "0 ≤ nums[i] ≤ 100"],
    hints=[
        "To get the *next* permutation you want to change the array as far to the right as possible. Which suffix is already at its maximum arrangement?",
        "Find the longest non-increasing suffix. The element just before it (the pivot, index `i`) is the leftmost one that must grow.",
        "Swap the pivot with the smallest element in the suffix that is strictly greater than it (scan from the right), then reverse the suffix to make it as small as possible.",
    ],
    explanation=_d(r"""
## Intuition

Think about how an odometer (or counting) works: to get the next number you change the
**rightmost** digit that can still go up, and reset everything to its right to the
smallest possible value.

For permutations: a suffix that is **non-increasing** (like `5 3 1`) is already the
largest arrangement of those values; it cannot "go up" by itself. So:

1. Scan from the right for the first `i` with `nums[i] < nums[i+1]`. Everything after
   `i` is non-increasing; `nums[i]` is the **pivot**, the rightmost position that can
   increase.
2. Increase it as little as possible: swap it with the **smallest suffix element
   strictly greater** than it. Since the suffix is non-increasing, that's the rightmost
   element `> nums[i]`.
3. The suffix is still non-increasing after the swap. Make it as small as possible by
   **reversing** it (non-increasing reversed is non-decreasing).

If no pivot exists, the whole array is the largest permutation; reverse it all.

## Approach

Trace on `[1, 3, 5, 4, 2]`:

```
1 3 5 4 2      suffix 5 4 2 is non-increasing; pivot i=1 (value 3)
    ^
1 3 5 4 2      rightmost element > 3 in suffix: 4 (index 3)
      ^
1 4 5 3 2      swap
1 4 2 3 5      reverse the suffix after i  ->  answer
```

## Complexity

- **Time:** O(n). Three linear scans at most.
- **Space:** O(1).

## Common mistakes

- **Strict vs non-strict comparisons with duplicates.** Find the pivot with
  `nums[i] < nums[i+1]` (skip while `nums[i] >= nums[i+1]`) and the swap partner with
  `nums[j] > nums[i]` (skip while `nums[j] <= nums[i]`). Getting either wrong breaks
  `[1, 5, 1]` or `[2, 2, 0, 4, 3, 1]`.
- **Sorting the suffix** instead of reversing: correct but O(n log n), and unnecessary
  because the suffix is already in reverse order.
- **Forgetting the wrap-around** when no pivot exists.
- **Unsigned indices** (C++ `size_t`, Rust `usize`) going below 0 in the backwards scan.

## Going further

C++ ships this as `std::next_permutation` (it returns `false` when it wraps around).
Repeatedly calling it from the sorted array enumerates all permutations without
recursion, even with duplicates. The k-th permutation can be computed directly with the
factorial number system.
"""),
    solution=_d(r"""
def next_permutation(nums):
    n = len(nums)
    # 1. Find the pivot: the rightmost i with nums[i] < nums[i+1]. Everything
    #    to its right is non-increasing, i.e. already maximal.
    i = n - 2
    while i >= 0 and nums[i] >= nums[i + 1]:
        i -= 1
    if i >= 0:
        # 2. Find the smallest value in the suffix that's strictly bigger than
        #    the pivot. The suffix is non-increasing, so it's the rightmost one.
        j = n - 1
        while nums[j] <= nums[i]:
            j -= 1
        nums[i], nums[j] = nums[j], nums[i]
    # 3. The suffix is still non-increasing; reversing it gives the smallest
    #    arrangement. If there was no pivot (i == -1), this reverses the whole
    #    array, wrapping around to the first permutation.
    lo, hi = i + 1, n - 1
    while lo < hi:
        nums[lo], nums[hi] = nums[hi], nums[lo]
        lo += 1
        hi -= 1
"""),
    refs={
        "c": _d(r"""
            void next_permutation(long long* nums, int numsSize) {
                int i = numsSize - 2;
                while (i >= 0 && nums[i] >= nums[i + 1]) i--;      // find pivot
                if (i >= 0) {
                    int j = numsSize - 1;
                    while (nums[j] <= nums[i]) j--;                 // smallest bigger value
                    long long t = nums[i]; nums[i] = nums[j]; nums[j] = t;
                }
                for (int lo = i + 1, hi = numsSize - 1; lo < hi; lo++, hi--) {  // reverse suffix
                    long long t = nums[lo]; nums[lo] = nums[hi]; nums[hi] = t;
                }
            }
        """),
        "cpp": _d(r"""
            void nextPermutation(vector<long long>& nums) {
                int n = nums.size(), i = n - 2;
                while (i >= 0 && nums[i] >= nums[i + 1]) i--;
                if (i >= 0) {
                    int j = n - 1;
                    while (nums[j] <= nums[i]) j--;
                    swap(nums[i], nums[j]);
                }
                reverse(nums.begin() + (i + 1), nums.end());
                // The standard library does all of this: std::next_permutation(nums.begin(), nums.end());
            }
        """),
        "rust": _d(r"""
            pub fn next_permutation(nums: &mut Vec<i64>) {
                let n = nums.len();
                // Find the pivot using a "start of suffix" index so nothing goes below 0.
                let mut s = n.saturating_sub(1); // suffix nums[s..] is non-increasing
                while s > 0 && nums[s - 1] >= nums[s] {
                    s -= 1;
                }
                if s > 0 {
                    let i = s - 1; // pivot
                    let mut j = n - 1;
                    while nums[j] <= nums[i] {
                        j -= 1;
                    }
                    nums.swap(i, j);
                }
                nums[s..].reverse();
            }
        """),
        "espresso": _d(r"""
            fn nextPermutation(nums) {
              var n = len(nums)
              var i = n - 2
              // find pivot: rightmost i with nums[i] < nums[i + 1]
              while i >= 0 {
                if nums[i] < nums[i + 1] { break }
                i -= 1
              }
              if i >= 0 {
                var j = n - 1
                while nums[j] <= nums[i] { j -= 1 }
                var t = nums[i]
                nums[i] = nums[j]
                nums[j] = t
              }
              // reverse the suffix
              var lo = i + 1
              var hi = n - 1
              while lo < hi {
                var u = nums[lo]
                nums[lo] = nums[hi]
                nums[hi] = u
                lo += 1
                hi -= 1
              }
            }
        """),
    },
    tests=[
        [[1, 2, 3]],
        [[3, 2, 1]],
        [[1, 1, 5]],
        [[1]],
        [[1, 5, 1]],
        [[1, 3, 5, 4, 2]],
        [[2, 2, 0, 4, 3, 1]],
        [[5, 5, 5]],
        [[1, 2]],
        [[_r.randint(0, 100) for _ in range(40)] + list(range(20, -1, -1))],
    ],
))

# ---------------------------------------------------------------------------- 16
def _mat(r, R, C, lo=-100, hi=100):
    return [[r.randint(lo, hi) for _ in range(C)] for _ in range(R)]


_r = random.Random(516)
PROBLEMS.append(dict(
    id="spiral-matrix-order",
    title="Spiral Matrix",
    difficulty=2,
    tags=["array", "matrix", "simulation"],
    fn="spiral_order",
    params=[["matrix", "int[][]"]],
    returns="int[]",
    statement=_d(r"""
Return all elements of an `m × n` matrix in **clockwise spiral order**, starting at the
top-left corner and moving right first.

```
 1 → 2 → 3
         ↓
 4 → 5   6
 ↑       ↓
 7 ← 8 ← 9      →  [1, 2, 3, 6, 9, 8, 7, 4, 5]
```
"""),
    example_notes=[
        "Right along the top, down the right side, left along the bottom, up the left side, then the centre.",
        "A 3×4 matrix: after the outer ring, the inner ring is a single row `6, 7`.",
    ],
    constraints=["1 ≤ m, n ≤ 100", "-100 ≤ matrix[i][j] ≤ 100"],
    hints=[
        "Peel the matrix like an onion: one full ring at a time.",
        "Track four boundaries: `top`, `bottom`, `left`, `right`. Walk the top row, then shrink `top`; walk the right column, shrink `right`; and so on.",
        "After walking the top row and the right column, the remaining region may have collapsed to nothing. Check `top <= bottom` before walking the bottom row and `left <= right` before walking the left column.",
    ],
    explanation=_d(r"""
## Intuition

Simulating "turn right when you hit a wall or a visited cell" works, but needs a
`visited` matrix. Cleaner: keep the **unvisited region as a rectangle** described by four
boundaries, and peel one side at a time.

```
          left        right
   top  [  1   2   3   4 ]
        [  5   6   7   8 ]
 bottom [  9  10  11  12 ]
```

Each side you walk is removed from the rectangle by moving one boundary inward.

## Approach

```
top, bottom, left, right = 0, m-1, 0, n-1
while top <= bottom and left <= right:
    walk top row     left..right     ; top += 1
    walk right col   top..bottom     ; right -= 1
    if top <= bottom:
        walk bottom row right..left  ; bottom -= 1
    if left <= right:
        walk left col  bottom..top   ; left += 1
```

Trace on the 3×4 matrix above:

```
top row   : 1 2 3 4        top=1
right col : 8 12           right=2
bottom row: 11 10 9        bottom=1
left col  : 5              left=1
-- next ring: top=1 bottom=1 left=1 right=2
top row   : 6 7            top=2
right col : (empty, top > bottom)  right=1
bottom row: skipped (top > bottom)
left col  : left <= right, but range bottom..top is empty
```

Result: `1 2 3 4 8 12 11 10 9 5 6 7`.

## Complexity

- **Time:** O(m·n). Each element is emitted once.
- **Space:** O(1) extra beyond the output.

## Common mistakes

- **Missing the two guards.** For a single row, the "bottom row" walk would revisit the
  same row backwards: `[1, 2, 3]` becomes `[1, 2, 3, 2, 1]`. Same for a single column
  with the left-column walk.
- **Inclusive vs exclusive ranges.** Boundaries here are inclusive; in Python that means
  `range(left, right + 1)` and `range(right, left - 1, -1)`.
- **C:** the matrix arrives as `long long** matrix, int matrixSize, int* matrixColSize`;
  the column count is `matrixColSize[0]`.

## Going further

- **Spiral Matrix II:** fill an n×n matrix with 1..n² in spiral order, the same loop
  writing instead of reading.
- The direction-vector simulation (`dr, dc = dc, -dr` to turn right) generalises better
  to odd walks, such as "spiral outward from a starting cell".
"""),
    solution=_d(r"""
def spiral_order(matrix):
    out = []
    # The unvisited part of the matrix is always the rectangle
    # rows top..bottom, columns left..right (all inclusive).
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        # Top row, left to right; then that row is used up.
        for c in range(left, right + 1):
            out.append(matrix[top][c])
        top += 1
        # Right column, top to bottom; then that column is used up.
        for r in range(top, bottom + 1):
            out.append(matrix[r][right])
        right -= 1
        # The rectangle may now be empty (single remaining row): without this
        # guard we'd walk the same row again backwards.
        if top <= bottom:
            for c in range(right, left - 1, -1):
                out.append(matrix[bottom][c])
            bottom -= 1
        # Same idea for a single remaining column.
        if left <= right:
            for r in range(bottom, top - 1, -1):
                out.append(matrix[r][left])
            left += 1
    return out
"""),
    refs={
        "c": _d(r"""
            long long* spiral_order(long long** matrix, int matrixSize, int* matrixColSize, int* returnSize) {
                int m = matrixSize, n = matrixColSize[0], k = 0;
                long long* out = malloc(sizeof(long long) * m * n);
                int top = 0, bottom = m - 1, left = 0, right = n - 1;
                while (top <= bottom && left <= right) {
                    for (int c = left; c <= right; c++) out[k++] = matrix[top][c];
                    top++;
                    for (int r = top; r <= bottom; r++) out[k++] = matrix[r][right];
                    right--;
                    if (top <= bottom) {
                        for (int c = right; c >= left; c--) out[k++] = matrix[bottom][c];
                        bottom--;
                    }
                    if (left <= right) {
                        for (int r = bottom; r >= top; r--) out[k++] = matrix[r][left];
                        left++;
                    }
                }
                *returnSize = k;
                return out;
            }
        """),
        "cpp": _d(r"""
            vector<long long> spiralOrder(vector<vector<long long>>& matrix) {
                vector<long long> out;
                int top = 0, bottom = matrix.size() - 1, left = 0, right = matrix[0].size() - 1;
                while (top <= bottom && left <= right) {
                    for (int c = left; c <= right; c++) out.push_back(matrix[top][c]);
                    top++;
                    for (int r = top; r <= bottom; r++) out.push_back(matrix[r][right]);
                    right--;
                    if (top <= bottom) {
                        for (int c = right; c >= left; c--) out.push_back(matrix[bottom][c]);
                        bottom--;
                    }
                    if (left <= right) {
                        for (int r = bottom; r >= top; r--) out.push_back(matrix[r][left]);
                        left++;
                    }
                }
                return out;
            }
        """),
        "rust": _d(r"""
            pub fn spiral_order(matrix: Vec<Vec<i64>>) -> Vec<i64> {
                // Signed bounds: they legitimately cross (e.g. right = left - 1).
                let (mut top, mut bottom) = (0i64, matrix.len() as i64 - 1);
                let (mut left, mut right) = (0i64, matrix[0].len() as i64 - 1);
                let at = |r: i64, c: i64| matrix[r as usize][c as usize];
                let mut out = Vec::new();
                while top <= bottom && left <= right {
                    for c in left..=right { out.push(at(top, c)); }
                    top += 1;
                    for r in top..=bottom { out.push(at(r, right)); }
                    right -= 1;
                    if top <= bottom {
                        for c in (left..=right).rev() { out.push(at(bottom, c)); }
                        bottom -= 1;
                    }
                    if left <= right {
                        for r in (top..=bottom).rev() { out.push(at(r, left)); }
                        left += 1;
                    }
                }
                out
            }
        """),
    },
    tests=[
        [[[1, 2, 3], [4, 5, 6], [7, 8, 9]]],
        [[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]],
        [[[7]]],
        [[[1, 2, 3, 4]]],
        [[[1], [2], [3]]],
        [[[1, 2], [3, 4], [5, 6], [7, 8]]],
        [[[1, 2, 3], [4, 5, 6]]],
        [_mat(_r, 7, 5)],
        [_mat(_r, 60, 70)],
    ],
))

# ---------------------------------------------------------------------------- 17
_r = random.Random(517)
PROBLEMS.append(dict(
    id="rotate-image-matrix",
    title="Rotate Image",
    difficulty=2,
    tags=["array", "matrix", "in-place"],
    fn="rotate_image",
    params=[["matrix", "int[][]"]],
    returns="int[][]",
    statement=_d(r"""
You are given an `n × n` matrix representing an image. Rotate it **90 degrees
clockwise** and return the result.

Try to do the rotation **in place** (modify `matrix` with O(1) extra memory) and then
return `matrix`; returning a freshly built matrix is also accepted.

```
1 2 3        7 4 1
4 5 6   →    8 5 2
7 8 9        9 6 3
```
"""),
    example_notes=[
        "The first row `1 2 3` becomes the last column, read top to bottom.",
        "A 1×1 image is unchanged.",
    ],
    constraints=["1 ≤ n ≤ 100", "-1000 ≤ matrix[i][j] ≤ 1000"],
    hints=[
        "Where does element `(r, c)` end up after a clockwise rotation? Work it out on the 3×3 example.",
        "`(r, c)` moves to `(c, n-1-r)`. That's a transpose (`(r, c)` → `(c, r)`) followed by something simple.",
        "Transpose in place (swap `m[r][c]` and `m[c][r]` for `c > r`), then reverse every row.",
    ],
    explanation=_d(r"""
## Intuition

Track one element. In the 3×3 example `1` at `(0, 0)` goes to `(0, 2)`, `2` at `(0, 1)`
goes to `(1, 2)`, `4` at `(1, 0)` goes to `(0, 1)`. The rule is

```
(r, c)  →  (c, n - 1 - r)
```

That's two simple moves composed:

1. **Transpose**: `(r, c) → (c, r)` (flip across the main diagonal).
2. **Reverse each row**: `(r, c) → (r, n - 1 - c)` (flip left-right).

Both are easy to do in place with swaps.

```
1 2 3   transpose   1 4 7   reverse rows   7 4 1
4 5 6  ---------->  2 5 8  ------------->  8 5 2
7 8 9               3 6 9                  9 6 3
```

## Approach

```
for r in range(n):
    for c in range(r + 1, n):          # strictly above the diagonal
        m[r][c], m[c][r] = m[c][r], m[r][c]
for row in m:
    row.reverse()
```

Only swap pairs with `c > r`: visiting the whole matrix would swap every pair twice and
undo the transpose.

## Complexity

- **Time:** O(n²). Every element is touched a constant number of times.
- **Space:** O(1) extra.

## Common mistakes

- **Transposing the full matrix** (`c` from 0): each pair swaps twice, net effect nothing.
- **Wrong composition order / direction:** transpose + reverse rows = clockwise;
  transpose + reverse *columns* (or reverse rows first, then transpose) = counter-clockwise.
- **Writing into the same matrix with the direct formula** `m[c][n-1-r] = m[r][c]`
  overwrites values you haven't moved yet; that only works with a copy, or with the
  4-way cycle swap.
- **C:** you must still return a `long long**` with `*returnSize` and
  `*returnColumnSizes` set; allocate fresh rows rather than returning the caller's array.

## Going further

- **Four-way cycle swap:** rotate each ring by moving four elements at a time
  (`top-left → top-right → bottom-right → bottom-left`). It's one pass instead of two.
- The same "decompose into reflections" trick gives every symmetry of the square:
  180° = reverse rows + reverse each row; anti-diagonal flip = transpose + 180°.
"""),
    solution=_d(r"""
def rotate_image(matrix):
    n = len(matrix)
    # Clockwise rotation maps (r, c) -> (c, n-1-r). We get there in two
    # in-place steps: transpose, (r, c) -> (c, r), then mirror each row,
    # (r, c) -> (r, n-1-c).
    for r in range(n):
        # Only swap above the diagonal; swapping every pair would do each
        # swap twice and undo the transpose.
        for c in range(r + 1, n):
            matrix[r][c], matrix[c][r] = matrix[c][r], matrix[r][c]
    for row in matrix:
        row.reverse()
    return matrix
"""),
    refs={
        "c": _d(r"""
            long long** rotate_image(long long** matrix, int matrixSize, int* matrixColSize, int* returnSize, int** returnColumnSizes) {
                int n = matrixSize;
                // Build the answer directly with the mapping (r, c) -> (c, n-1-r).
                long long** out = malloc(sizeof(long long*) * n);
                *returnColumnSizes = malloc(sizeof(int) * n);
                for (int r = 0; r < n; r++) {
                    out[r] = malloc(sizeof(long long) * n);
                    (*returnColumnSizes)[r] = n;
                }
                for (int r = 0; r < n; r++)
                    for (int c = 0; c < n; c++)
                        out[c][n - 1 - r] = matrix[r][c];
                *returnSize = n;
                return out;
            }
        """),
        "cpp": _d(r"""
            vector<vector<long long>> rotateImage(vector<vector<long long>>& matrix) {
                int n = matrix.size();
                for (int r = 0; r < n; r++)
                    for (int c = r + 1; c < n; c++)
                        swap(matrix[r][c], matrix[c][r]);     // transpose
                for (auto& row : matrix) reverse(row.begin(), row.end());  // mirror
                return matrix;
            }
        """),
        "rust": _d(r"""
            pub fn rotate_image(mut matrix: Vec<Vec<i64>>) -> Vec<Vec<i64>> {
                let n = matrix.len();
                for r in 0..n {
                    for c in r + 1..n {
                        // Two different rows: swap via a temporary (can't borrow both mutably).
                        let t = matrix[r][c];
                        matrix[r][c] = matrix[c][r];
                        matrix[c][r] = t;
                    }
                }
                for row in matrix.iter_mut() {
                    row.reverse();
                }
                matrix
            }
        """),
    },
    tests=[
        [[[1, 2, 3], [4, 5, 6], [7, 8, 9]]],
        [[[5]]],
        [[[1, 2], [3, 4]]],
        [[[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]]],
        [[[-1, -2], [-3, -4]]],
        [_mat(_r, 5, 5, -1000, 1000)],
        [_mat(_r, 40, 40, -1000, 1000)],
    ],
))

# ---------------------------------------------------------------------------- 18
def _majority(r, n, lo, hi):
    maj = r.randint(lo, hi)
    k = n // 2 + 1 + r.randint(0, n // 10)
    a = [maj] * k + [r.randint(lo, hi) for _ in range(n - k)]
    r.shuffle(a)
    return [a]


_r = random.Random(518)
PROBLEMS.append(dict(
    id="majority-element-boyer-moore",
    title="Majority Element",
    difficulty=1,
    tags=["array", "voting", "running state"],
    fn="majority_element",
    params=[["nums", "int[]"]],
    returns="int",
    statement=_d(r"""
Return the **majority element** of `nums`: the value that appears **more than
`⌊n / 2⌋` times**. The input always has one.

Can you do it in O(n) time and O(1) extra memory?
"""),
    example_notes=[
        "`3` appears twice out of three.",
        "`2` appears 4 times out of 7 (more than 3).",
    ],
    constraints=["1 ≤ len(nums) ≤ 5·10⁴", "-10⁹ ≤ nums[i] ≤ 10⁹", "a majority element always exists"],
    hints=[
        "Sorting works (the middle element must be the majority). Can you avoid the O(n log n)?",
        "Imagine pairing up each majority element with a *different* element and cancelling both. Can the majority run out?",
        "Keep a `candidate` and a `count`. Same value as candidate: `count += 1`; different: `count -= 1`; when `count` is 0, adopt the current value as the new candidate.",
    ],
    explanation=_d(r"""
## Intuition

A hash map of counts solves this in O(n) time and O(n) space. Sorting and taking the
middle element works in O(n log n). The **Boyer-Moore voting algorithm** gets O(n) time
*and* O(1) space with a cancellation argument:

> Pair up elements with **different** values and throw both away. The majority value
> occurs more than n/2 times, so it can't be paired off entirely: it's what survives.

The algorithm performs this pairing on the fly. `candidate` is the value currently
"in the lead", and `count` is how many unpaired copies of it we're holding.

## Approach

```
count = 0
for x in nums:
    if count == 0: candidate = x       # nothing unpaired; x starts a new lead
    count += 1 if x == candidate else -1   # same: hold it; different: cancel one pair
return candidate
```

Trace on `[2, 2, 1, 1, 1, 2, 2]`:

| x | candidate | count |
|---|---|---|
| 2 | 2 | 1 |
| 2 | 2 | 2 |
| 1 | 2 | 1 |
| 1 | 2 | 0 |
| 1 | 1 | 1 |
| 2 | 1 | 0 |
| 2 | 2 | 1 |

Answer: 2. Notice the candidate changed along the way; only the final one matters.

## Complexity

- **Time:** O(n), one pass.
- **Space:** O(1).

## Common mistakes

- **Trusting the candidate when a majority isn't guaranteed.** If the problem doesn't
  promise a majority, you need a second pass to count the candidate and verify.
- **Checking `count == 0` after the update** instead of before: then the element that
  zeroed the count would wrongly become the candidate.
- **Thinking `count` is the frequency.** It's the lead over everyone else, not the
  number of occurrences.

## Going further

- **Majority Element II** (elements appearing more than n/3 times): keep *two*
  candidates and two counters; at most two such elements exist. Verify in a second pass.
- The same "cancel distinct items" idea is the Misra–Gries heavy-hitters algorithm used
  in streaming analytics.
"""),
    solution=_d(r"""
def majority_element(nums):
    candidate = None
    count = 0  # how many copies of `candidate` are currently "unpaired"
    for x in nums:
        if count == 0:
            # Everything so far has cancelled out; x takes the lead.
            candidate = x
        if x == candidate:
            count += 1
        else:
            # Pair x with one copy of the candidate and discard both.
            count -= 1
    # The majority value can't be fully cancelled, so it's what remains.
    return candidate
"""),
    refs={
        "c": _d(r"""
            long long majority_element(long long* nums, int numsSize) {
                long long cand = 0;
                int count = 0;
                for (int i = 0; i < numsSize; i++) {
                    if (count == 0) cand = nums[i];       // new leader
                    count += (nums[i] == cand) ? 1 : -1;  // vote or cancel
                }
                return cand;
            }
        """),
        "cpp": _d(r"""
            long long majorityElement(vector<long long>& nums) {
                long long cand = 0;
                int count = 0;
                for (long long x : nums) {
                    if (count == 0) cand = x;
                    count += (x == cand) ? 1 : -1;
                }
                return cand;
            }
        """),
        "rust": _d(r"""
            pub fn majority_element(nums: Vec<i64>) -> i64 {
                let (mut cand, mut count) = (0i64, 0i32);
                for x in nums {
                    if count == 0 { cand = x; }
                    count += if x == cand { 1 } else { -1 };
                }
                cand
            }
        """),
        "espresso": _d(r"""
            fn majorityElement(nums) {
              var cand = 0
              var count = 0
              for var i in 0..len(nums) {
                if count == 0 { cand = nums[i] }
                if nums[i] == cand { count += 1 } else { count -= 1 }
              }
              return cand
            }
        """),
    },
    tests=[
        [[3, 2, 3]],
        [[2, 2, 1, 1, 1, 2, 2]],
        [[7]],
        [[-1, -1, 5]],
        [[1, 2, 1, 3, 1]],
        [[4, 4, 4, 4]],
        [[5, 6, 6]],
        _majority(_r, 101, -10**6, 10**6),
        _majority(_r, 51, 0, 3),
    ],
))

# ---------------------------------------------------------------------------- 19
_r = random.Random(519)
_pv = [_r.randint(-50, 50) for _ in range(80)]
_pv2 = [_r.randint(-3, 3) for _ in range(60)]
PROBLEMS.append(dict(
    id="find-pivot-index",
    title="Find Pivot Index",
    difficulty=1,
    tags=["array", "prefix sums"],
    fn="pivot_index",
    params=[["nums", "int[]"]],
    returns="int",
    statement=_d(r"""
The **pivot index** is an index `i` where the sum of all elements strictly to its left
equals the sum of all elements strictly to its right. (At the edges, the empty side sums
to 0.)

Return the **leftmost** pivot index, or `-1` if there is none.
"""),
    example_notes=[
        "At index 3: left 1+7+3 = 11, right 5+6 = 11.",
        "No index balances the array.",
    ],
    constraints=["1 ≤ len(nums) ≤ 10⁴", "-1000 ≤ nums[i] ≤ 1000"],
    hints=[
        "Computing both sums from scratch for each index is O(n²). What do you know about `left + nums[i] + right`?",
        "`left + nums[i] + right = total`. So `right = total - left - nums[i]`.",
        "Compute `total` once, then sweep keeping `left`. Check `left == total - left - nums[i]` before adding `nums[i]` to `left`.",
    ],
    explanation=_d(r"""
## Intuition

For each index we need "sum to the left" and "sum to the right". The left sum is a
running prefix sum. The right sum looks like it needs a second array, but it doesn't:
the three parts always add up to the total.

```
 [ ... left ... ] nums[i] [ ... right ... ]
 left + nums[i] + right == total   =>   right = total - left - nums[i]
```

So one pass to compute `total`, one pass to find the pivot.

## Approach

```
total = sum(nums)
left = 0
for i, x in enumerate(nums):
    if left == total - left - x: return i
    left += x            # only now does x join the left side
return -1
```

Trace on `[1, 7, 3, 6, 5, 6]` (total 28):

| i | x | left | right = 28 - left - x | match? |
|---|---|---|---|---|
| 0 | 1 | 0 | 27 | no |
| 1 | 7 | 1 | 20 | no |
| 2 | 3 | 8 | 17 | no |
| 3 | 6 | 11 | 11 | **yes → 3** |

Because we scan left to right and return immediately, the first match is the leftmost
pivot.

**Language mechanics.** `enumerate` in Python yields `(index, value)` pairs; in C you loop
on the index and read `nums[i]`; in Rust `iter().enumerate()` gives `(usize, &i64)`, so
you'll convert the index with `as i64` to return it.

## Complexity

- **Time:** O(n), two passes.
- **Space:** O(1).

## Common mistakes

- **Adding `x` to `left` before the comparison** makes `left` include the pivot.
- **Forgetting edge pivots.** Index 0 is a pivot when the rest sums to 0
  (`[2, 1, -1]` → 0); index n−1 when everything before it sums to 0.
- **Returning the last pivot** instead of the first: return as soon as you find one.
- **Negative numbers** mean you can't stop early when `left` exceeds `total / 2`.

## Going further

"Total minus prefix" is a pattern worth recognising: it gives suffix sums for free. The
same reasoning finds the split point of an array into two parts with minimum difference,
or the equilibrium point in physics-style balance problems.
"""),
    solution=_d(r"""
def pivot_index(nums):
    total = sum(nums)
    left = 0  # sum of nums[0..i-1]
    for i, x in enumerate(nums):
        # Everything is either left of i, at i, or right of i, so the right
        # sum is whatever's left of the total. No second array needed.
        right = total - left - x
        if left == right:
            return i  # first match is the leftmost pivot
        # Only after checking does nums[i] become part of the left side.
        left += x
    return -1
"""),
    refs={
        "c": _d(r"""
            long long pivot_index(long long* nums, int numsSize) {
                long long total = 0, left = 0;
                for (int i = 0; i < numsSize; i++) total += nums[i];
                for (int i = 0; i < numsSize; i++) {
                    // right side = everything except the left side and nums[i] itself
                    if (left == total - left - nums[i]) return i;   // first hit is the leftmost
                    left += nums[i];
                }
                return -1;
            }
        """),
        "cpp": _d(r"""
            long long pivotIndex(vector<long long>& nums) {
                long long total = accumulate(nums.begin(), nums.end(), 0LL), left = 0;
                for (size_t i = 0; i < nums.size(); i++) {
                    if (left == total - left - nums[i]) return i;
                    left += nums[i];
                }
                return -1;
            }
        """),
        "rust": _d(r"""
            pub fn pivot_index(nums: Vec<i64>) -> i64 {
                let total: i64 = nums.iter().sum();
                let mut left = 0;
                for (i, &x) in nums.iter().enumerate() {
                    if left == total - left - x {
                        return i as i64;
                    }
                    left += x;
                }
                -1
            }
        """),
        "espresso": _d(r"""
            fn pivotIndex(nums) {
              var total = 0
              for var i in 0..len(nums) { total += nums[i] }
              var left = 0
              for var i in 0..len(nums) {
                if left == total - left - nums[i] { return i }
                left += nums[i]
              }
              return -1
            }
        """),
    },
    tests=[
        [[1, 7, 3, 6, 5, 6]],
        [[1, 2, 3]],
        [[2, 1, -1]],
        [[5]],
        [[-1, -1, -1, 0, 1, 1]],
        [[0, 0, 0]],
        [[1, -1, 2]],
        [[-1, -1, 0, 1, 1, 0]],
        [_pv],
        [_pv2],
    ],
))
