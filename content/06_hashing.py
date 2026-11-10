"""Track 6: Hash Maps & Sets."""
import random
import textwrap


def _d(s):
    return textwrap.dedent(s).lstrip("\n")


TRACK = dict(
    id="hashing",
    title="Hash Maps & Sets",
    order=6,
    icon="#",
    blurb="Trade memory for speed: O(1) average lookups turn quadratic searches into single passes.",
    intro=_d(r"""
## The problem hash tables solve

Arrays give O(1) access *by position*. Very often we want O(1) access *by value*:
"have I seen 42 before?", "where is the word `cat`?", "how many times did `x` occur?".
Searching an unsorted array is O(n); a balanced search tree is O(log n). A **hash
table** gets the *average* cost down to **O(1)**.

## How it works

1. A **hash function** turns a key into a big integer: `h("cat") = 8273648123...`.
2. Reduce it to a slot index in an array of **buckets**: `i = h(key) mod capacity`
   (or `h & (capacity - 1)` when the capacity is a power of two).
3. Store the key (and its value) in that bucket.

```
  key      hash          bucket = hash mod 8
  "cat" -> 8273648123 -> 3
  "dog" -> 1928374650 -> 2
  "owl" -> 5551112227 -> 3     <- collision with "cat"!

  buckets: 0 [ ]
           1 [ ]
           2 [ dog ]
           3 [ cat ] -> [ owl ]      (chaining)
           4 [ ]
           ...
```

A lookup recomputes the hash, jumps to the bucket, and compares keys only there. If the
hash spreads keys evenly, each bucket holds about one key, so lookups, inserts and
deletes cost O(1) on average.

### Collisions

Different keys can land in the same bucket (there are far more possible keys than
buckets). Two classic strategies:

- **Separate chaining**: each bucket is a small list. C++'s `std::unordered_map` and
  Java's `HashMap` work this way.
- **Open addressing**: everything lives in one flat array; on a collision, probe the
  next slot (`i+1, i+2, ...` for *linear probing*) until you find the key or an empty
  slot. Python's `dict`, Rust's `HashMap` (SwissTable) and most hand-written C tables
  use this. It is very cache-friendly.

```
  open addressing, linear probing, capacity 8:
  insert "owl" (bucket 3): slot 3 taken by "cat" -> try 4: empty -> store at 4
  [ _ | _ | dog | cat | owl | _ | _ | _ ]
```

### Load factor and resizing

The **load factor** is `entries / capacity`. As it grows, collisions multiply and
probe sequences lengthen. Implementations keep it bounded (Python ~2/3, Rust ~7/8,
C++ 1.0 by default) by **doubling the capacity and re-inserting everything** when the
threshold is crossed. A single resize is O(n), but it happens so rarely that the
*amortised* cost per insert stays O(1), the same argument as dynamic-array appends.

### What "O(1)" hides

- It's an **average**. A bad hash function (or an adversary who knows yours) can put
  every key in one bucket: O(n) per operation. That's why Python and Rust randomise
  their string hashing per process.
- Hashing a string of length L costs O(L), so a lookup keyed by a string is O(L), not
  O(1).
- Hash tables have **no order**. If you need keys sorted, use a sorted structure
  (`std::map`, Rust `BTreeMap`) or sort at the end.
- Keys must be **immutable** (or at least never change while stored): if a key's hash
  changes, the table can no longer find it. This is why Python lists can't be dict keys
  but tuples can.

## What to use in each language

```python
seen = set()                    # membership
seen.add(x); x in seen
pos = {}                        # key -> value
pos[x] = i; pos.get(x, -1)
from collections import Counter, defaultdict
cnt = Counter(nums)             # value -> frequency
groups = defaultdict(list)      # missing keys start as []
groups[key].append(item)
```

```cpp
unordered_set<long long> seen;          // seen.count(x), seen.insert(x)
unordered_map<long long, int> pos;      // pos[x] = i  (operator[] inserts a default!)
auto it = pos.find(x);                  // use find() to test without inserting
if (it != pos.end()) { /* it->second */ }
```

```rust
use std::collections::{HashMap, HashSet};
let mut cnt: HashMap<i64, usize> = HashMap::new();
*cnt.entry(x).or_insert(0) += 1;        // the entry API: one lookup, insert-or-update
if let Some(&i) = pos.get(&x) { /* found */ }
let mut seen = HashSet::new();
if !seen.insert(x) { /* x was already present */ }
```

**C has no hash map in its standard library.** You have three options:

1. **Sort first** (`qsort`) and use adjacent comparisons or binary search. O(n log n),
   often perfectly good.
2. **Direct addressing** when keys are small: `int count[256]` indexed by a byte is a
   perfect hash table.
3. **Write a tiny open-addressing table** (about 20 lines, see the C notes in Two Sum).
   For interview-style problems you know `n` up front, so you can allocate a
   power-of-two capacity ≥ 2n and never resize.

## Patterns to recognise

- **"Have I seen the complement?"** One pass, look up `target - x` before inserting `x`
  (Two Sum).
- **Counting**: frequencies of values, characters or prefix sums (Top K, Subarray Sum).
- **Grouping by a canonical key**: anagrams share their sorted letters (Group Anagrams).
- **Bijections**: two maps, one in each direction (Isomorphic Strings, Word Pattern).
- **Prefix sum + hash map**: "how many earlier prefixes equal `P - k`?" counts subarrays
  with sum k in O(n).
- **Hash map + another structure**: map for O(1) lookup, linked list for O(1) ordering
  (LRU cache).
"""),
)

PROBLEMS = []

_C_TABLE_NOTE = _d(r"""
**C has no built-in hash map**, so here's a minimal open-addressing table with linear
probing. Since `n` is known up front, choose a power-of-two capacity at least twice
`n` (load factor ≤ 0.5 keeps probe sequences short) and never resize.

```c
typedef struct { long long *keys; int *vals; bool *used; size_t mask; } Map;

static size_t hash64(long long k) {           // mix the bits (splitmix64 finaliser)
    unsigned long long x = (unsigned long long)k;
    x ^= x >> 30; x *= 0xbf58476d1ce4e5b9ULL;
    x ^= x >> 27; x *= 0x94d049bb133111ebULL;
    return (size_t)(x ^ (x >> 31));
}
static Map map_new(int n) {
    size_t cap = 4; while (cap < 2 * (size_t)n) cap <<= 1;
    return (Map){ malloc(cap * sizeof(long long)), malloc(cap * sizeof(int)),
                  calloc(cap, sizeof(bool)), cap - 1 };
}
// Returns the slot holding `k`, or the empty slot where it would go.
static size_t map_slot(Map *m, long long k) {
    size_t i = hash64(k) & m->mask;
    while (m->used[i] && m->keys[i] != k) i = (i + 1) & m->mask;   // probe
    return i;
}
```

Lookup: `size_t s = map_slot(&m, key); if (m.used[s]) ... m.vals[s] ...`.
Insert: `m.used[s] = true; m.keys[s] = key; m.vals[s] = value;`.
Don't forget to `free` the three arrays. Why mix the bits? With `key & mask` alone,
keys that differ only in their high bits (or are all multiples of 1024) would pile into
the same few slots.
""")

# ----------------------------------------------------------------------------- 1
def _two_sum_big(r, n):
    # Distinct even values plus a single odd one; an odd target forces the pair
    # to include the odd element, and its partner value is unique.
    vals = [2 * x for x in r.sample(range(-10**6, 10**6), n)]
    i, j = r.sample(range(n), 2)
    vals[i] += 1
    return [vals, vals[i] + vals[j]]


_r = random.Random(601)
PROBLEMS.append(dict(
    id="two-sum-hash-map",
    title="Two Sum",
    difficulty=1,
    tags=["hash map", "array"],
    fn="two_sum",
    params=[["nums", "int[]"], ["target", "int"]],
    returns="int[]",
    statement=_d(r"""
Given an integer array `nums` (not sorted) and an integer `target`, return the indices
`[i, j]` of the two elements with `nums[i] + nums[j] == target`.

- Use two **different** positions (`i != j`); the values may be equal.
- Return the indices in **increasing order** (`i < j`).
- Every input has **exactly one** valid pair.

Aim for better than O(n²).
"""),
    example_notes=[
        "`nums[0] + nums[1] = 2 + 7 = 9`.",
        "`2 + 4 = 6`. Index 0 (`3`) can't be used twice.",
    ],
    constraints=["2 ≤ len(nums) ≤ 10⁴", "-10⁹ ≤ nums[i], target ≤ 10⁹", "exactly one answer exists"],
    hints=[
        "For a fixed `nums[j]`, which value would you need to have seen earlier?",
        "You need `target - nums[j]`. Checking all earlier elements is O(n) per `j`. What structure answers \"have I seen value v, and where?\" in O(1)?",
        "Sweep once with a dict `value → index`. For each `j`, look up `target - nums[j]` *before* inserting `nums[j]`; if found at `i`, return `[i, j]`.",
    ],
    explanation=_d(r"""
## Intuition

The brute force checks every pair: O(n²). Flip the question: as you scan, for the
current element `x` you need its **complement** `target - x`. "Have I already seen
this value, and where?" is exactly what a hash map answers in O(1).

## Approach

```
seen = {}                       # value -> index where we saw it
for j, x in enumerate(nums):
    if target - x in seen:
        return [seen[target - x], j]
    seen[x] = j
```

Two details matter:

1. **Look up before inserting.** Otherwise, with `x = target / 2`, `x` finds itself and
   you'd return `[j, j]`.
2. **Indices come out ordered for free.** The partner was seen earlier, so its index is
   smaller than `j`.

Trace on `nums = [3, 2, 4]`, target 6:

| j | x | need | seen before | result |
|---|---|---|---|---|
| 0 | 3 | 3 | {} | insert 3→0 |
| 1 | 2 | 4 | {3:0} | insert 2→1 |
| 2 | 4 | 2 | {3:0, 2:1} | found at 1 → `[1, 2]` |

Duplicates work naturally: in `[3, 3]`, the second `3` finds the first.

## Complexity

- **Time:** O(n) average: n lookups and inserts at O(1) each.
- **Space:** O(n) for the map.

Compare with sorting + two pointers (Two Sum II in the arrays track): O(n log n) time,
and sorting loses the original indices unless you sort `(value, index)` pairs.

## Common mistakes

- **Inserting first, then looking up**, which can pair an element with itself.
- **Building the full map first** (`{v: i for i, v in enumerate(nums)}`) and then
  scanning: with duplicates the map keeps the *last* index, which is fine, but you
  must check `i != j` explicitly.
- **C++:** `seen[x]` with `operator[]` *inserts* a default 0 if `x` is missing, which
  creates fake entries. Use `find` or `count`.
- **Overflow:** `target - x` can exceed 32 bits when both are near ±10⁹. Use 64-bit.

## Going further

- **Count the pairs** instead of finding one: keep a count per value and add
  `count[target - x]` at each step.
- **3Sum / 4Sum** are usually solved with sorting + two pointers, but 4Sum II (later in
  this track) uses a hash map of pair sums.
"""),
    solution=_d(r"""
def two_sum(nums, target):
    # value -> index of an earlier occurrence. Only elements *before* j are in
    # here, which guarantees i != j and i < j.
    seen = {}
    for j, x in enumerate(nums):
        need = target - x
        # Look up before inserting x, so x can't be paired with itself.
        if need in seen:
            return [seen[need], j]
        seen[x] = j
    return []  # unreachable: exactly one answer is guaranteed
"""),
    lang_notes={"c": _C_TABLE_NOTE},
    refs={
        "c": _d(r"""
            // Open-addressing hash map: value -> index (see the C notes for the design).
            static size_t mix64(long long k) {
                unsigned long long x = (unsigned long long)k;
                x ^= x >> 30; x *= 0xbf58476d1ce4e5b9ULL;
                x ^= x >> 27; x *= 0x94d049bb133111ebULL;
                return (size_t)(x ^ (x >> 31));
            }

            long long* two_sum(long long* nums, int numsSize, long long target, int* returnSize) {
                size_t cap = 4;
                while (cap < 2 * (size_t)numsSize) cap <<= 1;   // load factor <= 0.5
                size_t mask = cap - 1;
                long long* keys = malloc(cap * sizeof(long long));
                int* vals = malloc(cap * sizeof(int));
                bool* used = calloc(cap, sizeof(bool));
                long long* out = malloc(2 * sizeof(long long));
                *returnSize = 2;
                out[0] = out[1] = -1;
                for (int j = 0; j < numsSize; j++) {
                    long long need = target - nums[j];
                    size_t s = mix64(need) & mask;
                    while (used[s] && keys[s] != need) s = (s + 1) & mask;   // probe
                    if (used[s]) { out[0] = vals[s]; out[1] = j; break; }    // found complement
                    s = mix64(nums[j]) & mask;
                    while (used[s] && keys[s] != nums[j]) s = (s + 1) & mask;
                    if (!used[s]) { used[s] = true; keys[s] = nums[j]; vals[s] = j; }
                }
                free(keys); free(vals); free(used);
                return out;
            }
        """),
        "cpp": _d(r"""
            vector<long long> twoSum(vector<long long>& nums, long long target) {
                unordered_map<long long, long long> seen;   // value -> index
                seen.reserve(nums.size() * 2);
                for (long long j = 0; j < (long long)nums.size(); j++) {
                    auto it = seen.find(target - nums[j]);  // find(): no accidental insert
                    if (it != seen.end()) return {it->second, j};
                    seen[nums[j]] = j;
                }
                return {};
            }
        """),
        "rust": _d(r"""
            use std::collections::HashMap;

            pub fn two_sum(nums: Vec<i64>, target: i64) -> Vec<i64> {
                let mut seen: HashMap<i64, usize> = HashMap::with_capacity(nums.len());
                for (j, &x) in nums.iter().enumerate() {
                    if let Some(&i) = seen.get(&(target - x)) {
                        return vec![i as i64, j as i64];
                    }
                    seen.insert(x, j);
                }
                vec![]
            }
        """),
    },
    tests=[
        [[2, 7, 11, 15], 9],
        [[3, 2, 4], 6],
        [[3, 3], 6],
        [[-1, -2, -3, -4, -5], -8],
        [[0, 4, 3, 0], 0],
        [[1000000000, -1000000000, 5], 0],
        [[5, 75, 25], 100],
        [[1, 6, 2, 9, 4, 3], 13],
        _two_sum_big(_r, 5000),
    ],
))

# ----------------------------------------------------------------------------- 2
_r = random.Random(602)
_cd_distinct = _r.sample(range(-10**6, 10**6), 3500)
_cd_dup = _r.sample(range(-10**6, 10**6), 3500)
_cd_dup.append(_cd_dup[0])
PROBLEMS.append(dict(
    id="contains-duplicate",
    title="Contains Duplicate",
    difficulty=1,
    tags=["hash set", "array", "sorting"],
    espresso=False,
    fn="contains_duplicate",
    params=[["nums", "int[]"]],
    returns="bool",
    statement=_d(r"""
Return `true` if any value appears **at least twice** in `nums`, and `false` if every
element is distinct.
"""),
    example_notes=["`1` appears twice.", "All four values are different."],
    constraints=["0 ≤ len(nums) ≤ 10⁵", "-10⁹ ≤ nums[i] ≤ 10⁹"],
    hints=[
        "Comparing every pair is O(n²). What would let you answer \"have I seen this before?\" instantly?",
        "Keep a set of values seen so far. If the current value is already in it, you're done.",
        "Alternative without hashing: after sorting, duplicates are adjacent.",
    ],
    explanation=_d(r"""
## Intuition

"Is there a repeat?" = "while scanning, do I ever meet a value I've already seen?". A
**hash set** answers "seen it?" in O(1) average, so one pass suffices.

## Approach

```python
seen = set()
for x in nums:
    if x in seen: return True    # second occurrence found
    seen.add(x)
return False
```

Trace on `[1, 2, 3, 1]`: `seen` grows `{1}`, `{1,2}`, `{1,2,3}`, then `1 in seen` →
`True`. We stop at the first repeat without looking further.

Two alternatives worth knowing:

- **Size comparison:** `len(set(nums)) < len(nums)`. Same complexity, a one-liner, but
  it always processes the whole array.
- **Sort and scan neighbours:** after sorting, equal values are adjacent, so check
  `nums[i] == nums[i-1]`. O(n log n) time but O(1) extra memory if you may sort in
  place. This is the natural choice in **C**, which has `qsort` but no hash set.

## Complexity

| approach | time | extra space |
|---|---|---|
| all pairs | O(n²) | O(1) |
| sort + scan | O(n log n) | O(1) (in-place sort) |
| hash set | O(n) average | O(n) |

## Common mistakes

- **Using a list for `seen`.** `x in some_list` is a linear scan, giving O(n²) again.
- **C `qsort` comparator:** `return a - b;` overflows for `long long` values (and
  truncates to `int`). Return `(a > b) - (a < b)` instead.
- **Empty and single-element arrays** have no duplicates.

## Going further

- **Contains Duplicate II:** is there a repeat within distance `k`? Keep a map
  `value → last index`, or a sliding-window set of the last `k` values.
- **Contains Duplicate III:** values within `t` and indices within `k`: bucket the values
  into buckets of width `t + 1`, a neat use of hashing with a custom key.
"""),
    solution=_d(r"""
def contains_duplicate(nums):
    seen = set()  # every value met so far; membership test is O(1) on average
    for x in nums:
        if x in seen:
            # Second occurrence: we can stop immediately.
            return True
        seen.add(x)
    return False
"""),
    lang_notes={"c": _d(r"""
No hash set in C? **Sort instead.** After `qsort`, duplicates are neighbours:

```c
static int cmp_ll(const void* a, const void* b) {
    long long x = *(const long long*)a, y = *(const long long*)b;
    return (x > y) - (x < y);          // never `x - y`: it can overflow / truncate
}
qsort(nums, numsSize, sizeof(long long), cmp_ll);
for (int i = 1; i < numsSize; i++) if (nums[i] == nums[i - 1]) return true;
```

That's O(n log n) and O(1) extra memory. For O(n), use the open-addressing table shown in
Two Sum's C notes, storing only keys.
""")},
    refs={
        "c": _d(r"""
            static int cmp_ll(const void* a, const void* b) {
                long long x = *(const long long*)a, y = *(const long long*)b;
                return (x > y) - (x < y);
            }

            bool contains_duplicate(long long* nums, int numsSize) {
                // Sorting makes equal values adjacent; then one scan finds repeats.
                qsort(nums, numsSize, sizeof(long long), cmp_ll);
                for (int i = 1; i < numsSize; i++)
                    if (nums[i] == nums[i - 1]) return true;
                return false;
            }
        """),
        "cpp": _d(r"""
            bool containsDuplicate(vector<long long>& nums) {
                unordered_set<long long> seen;
                seen.reserve(nums.size());
                for (long long x : nums)
                    if (!seen.insert(x).second) return true;   // insert() reports "already there"
                return false;
            }
        """),
        "rust": _d(r"""
            use std::collections::HashSet;

            pub fn contains_duplicate(nums: Vec<i64>) -> bool {
                let mut seen = HashSet::with_capacity(nums.len());
                // HashSet::insert returns false when the value was already present.
                nums.into_iter().any(|x| !seen.insert(x))
            }
        """),
    },
    tests=[
        [[1, 2, 3, 1]],
        [[1, 2, 3, 4]],
        [[]],
        [[7]],
        [[1, 1, 1, 3, 3, 4, 3, 2, 4, 2]],
        [[-1000000000, 1000000000]],
        [[0, -0, 5]],
        [_cd_distinct],
        [_cd_dup],
    ],
))

# ----------------------------------------------------------------------------- 3
def _anagram_words(r, groups, max_size):
    words = []
    for _ in range(groups):
        base = "".join(r.choice("abcdefgh") for _ in range(r.randint(1, 6)))
        for _ in range(r.randint(1, max_size)):
            w = list(base)
            r.shuffle(w)
            words.append("".join(w))
    r.shuffle(words)
    return [words]


_r = random.Random(603)
PROBLEMS.append(dict(
    id="group-anagrams",
    title="Group Anagrams",
    difficulty=2,
    tags=["hash map", "string", "sorting"],
    fn="group_anagrams",
    params=[["strs", "str[]"]],
    returns="str[][]",
    compare="unordered_deep",
    statement=_d(r"""
Group the strings in `strs` so that each group contains exactly the strings that are
**anagrams** of each other (same letters with the same multiplicities, in any order).

Return the list of groups. The order of the groups and the order of the strings inside
each group don't matter. If a string occurs several times, every occurrence goes into
its group.
"""),
    example_notes=[
        "`eat`, `tea` and `ate` share the letters a, e, t; `tan` and `nat` share a, n, t; `bat` is alone.",
        "The empty string is an anagram of itself.",
    ],
    constraints=["0 ≤ len(strs) ≤ 10⁴", "0 ≤ len(strs[i]) ≤ 100", "only lowercase English letters"],
    hints=[
        "Two strings are anagrams exactly when they look the same after some normalisation. Which one?",
        "Sorting the letters gives a canonical form: `sorted('tea') == sorted('eat') == 'aet'`.",
        "Use a hash map from canonical key to the list of strings with that key. In Python the key must be hashable: `''.join(sorted(s))` or a `tuple` of 26 letter counts.",
    ],
    explanation=_d(r"""
## Intuition

Comparing every pair of strings is O(n²·L). Instead, give each string a **canonical
key** such that two strings are anagrams *if and only if* their keys are equal. Then
grouping is just "bucket by key" with a hash map.

Two good keys:

1. **Sorted letters:** `"tea" → "aet"`. Costs O(L log L) per string.
2. **Letter counts:** a 26-tuple `(1,0,0,0,1,...,1,...)`. Costs O(L) per string; better
   for long strings.

## Approach

```
groups = defaultdict(list)
for s in strs:
    groups[key(s)].append(s)
return list(groups.values())
```

Trace on `["eat","tea","tan","ate","nat","bat"]` with the sorted-letters key:

| s | key | groups |
|---|---|---|
| eat | aet | aet: [eat] |
| tea | aet | aet: [eat, tea] |
| tan | ant | …, ant: [tan] |
| ate | aet | aet: [eat, tea, ate] |
| nat | ant | ant: [tan, nat] |
| bat | abt | abt: [bat] |

## Complexity

With n strings of length at most L:

- **Sorted key:** O(n · L log L) time.
- **Count key:** O(n · (L + 26)) time.
- **Space:** O(n · L) for the keys and groups.

## Common mistakes

- **Unhashable keys.** In Python, `sorted(s)` returns a *list*, which can't be a dict key.
  Join it into a string or convert to a tuple.
- **Using the sum or product of letter codes** as the key: different multisets can
  collide (`"ad"` and `"bc"` have the same sum). The key must be *exact*.
- **Dropping duplicates:** if `"abc"` appears twice, both copies belong in the group.
- **C++:** `unordered_map<string, vector<string>>` works; the sorted copy of the
  string is a perfect key. Rust: `HashMap<[u8; 26], Vec<String>>` works since arrays
  implement `Hash`.

## Going further

- **Valid Anagram** (two strings) is the same idea with a single count array.
- **Find All Anagrams in a String:** a sliding window of counts compared against the
  pattern's counts, updating O(1) per step.
- Canonical keys are a general hashing trick: group points by slope (reduced fraction),
  shapes by normalised coordinates, and so on.
"""),
    solution=_d(r"""
from collections import defaultdict

def group_anagrams(strs):
    # canonical key -> all strings with that key. Anagrams (and only anagrams)
    # share a key, so each bucket is exactly one group.
    groups = defaultdict(list)
    for s in strs:
        # Letter counts make an exact key in O(len(s)); a list isn't hashable,
        # so freeze it into a tuple. (''.join(sorted(s)) also works.)
        counts = [0] * 26
        for ch in s:
            counts[ord(ch) - ord("a")] += 1
        groups[tuple(counts)].append(s)
    return list(groups.values())
"""),
    refs={
        "c": _d(r"""
            // C has no hash map of strings, so we group by *sorting* instead: give every word its
            // canonical key (its letters sorted), sort the word indices by key, and equal keys end
            // up adjacent. Each run of equal keys is one group.
            static char** g_keys;                      // qsort's comparator can't take extra arguments

            static int cmp_idx(const void* a, const void* b) {
                int i = *(const int*)a, j = *(const int*)b;
                int c = strcmp(g_keys[i], g_keys[j]);
                return c ? c : (i > j) - (i < j);      // tie-break on index: deterministic order
            }

            // Canonical key: counting sort of the bytes, O(len) instead of O(len log len).
            static char* sorted_key(const char* s) {
                int cnt[256] = {0};
                size_t n = strlen(s);
                for (size_t i = 0; i < n; i++) cnt[(unsigned char)s[i]]++;
                char* k = malloc(n + 1);
                size_t p = 0;
                for (int c = 0; c < 256; c++)
                    while (cnt[c]--) k[p++] = (char)c;
                k[n] = '\0';
                return k;
            }

            static char* dup_str(const char* s) {
                size_t n = strlen(s) + 1;
                return memcpy(malloc(n), s, n);        // the caller owns every string we return
            }

            char*** group_anagrams(char** strs, int strsSize, int* returnSize, int** returnColumnSizes) {
                g_keys = malloc((strsSize ? strsSize : 1) * sizeof(char*));
                int* order = malloc((strsSize ? strsSize : 1) * sizeof(int));
                for (int i = 0; i < strsSize; i++) { g_keys[i] = sorted_key(strs[i]); order[i] = i; }
                qsort(order, strsSize, sizeof(int), cmp_idx);

                // At most strsSize groups; allocate for the worst case.
                char*** res = malloc((strsSize ? strsSize : 1) * sizeof(char**));
                int* cols = malloc((strsSize ? strsSize : 1) * sizeof(int));
                int groups = 0;
                for (int i = 0; i < strsSize;) {
                    int j = i;
                    while (j < strsSize && strcmp(g_keys[order[i]], g_keys[order[j]]) == 0) j++;
                    // order[i..j) all share one key: that's one group of j - i words.
                    res[groups] = malloc((j - i) * sizeof(char*));
                    for (int t = i; t < j; t++) res[groups][t - i] = dup_str(strs[order[t]]);
                    cols[groups++] = j - i;
                    i = j;
                }

                for (int i = 0; i < strsSize; i++) free(g_keys[i]);
                free(g_keys); free(order);
                *returnSize = groups;
                *returnColumnSizes = cols;
                return res;
            }
        """),
        "cpp": _d(r"""
            vector<vector<string>> groupAnagrams(vector<string>& strs) {
                unordered_map<string, vector<string>> groups;
                for (auto& s : strs) {
                    string key = s;
                    sort(key.begin(), key.end());   // canonical form: sorted letters
                    groups[key].push_back(s);       // operator[] creates the group on first use
                }
                vector<vector<string>> out;
                for (auto& [key, g] : groups) out.push_back(move(g));
                return out;
            }
        """),
        "rust": _d(r"""
            use std::collections::HashMap;

            pub fn group_anagrams(strs: Vec<String>) -> Vec<Vec<String>> {
                let mut groups: HashMap<[u8; 26], Vec<String>> = HashMap::new();
                for s in strs {
                    let mut key = [0u8; 26]; // letter counts (≤ 100 per letter fits in u8)
                    for b in s.bytes() {
                        key[(b - b'a') as usize] += 1;
                    }
                    groups.entry(key).or_default().push(s);
                }
                groups.into_values().collect()
            }
        """),
    },
    tests=[
        [["eat", "tea", "tan", "ate", "nat", "bat"]],
        [[""]],
        [["a"]],
        [[]],
        [["", "", "b"]],
        [["abc", "abc", "cba", "ab"]],
        [["ab", "ba", "aab", "aba", "baa", "abb"]],
        [["listen", "silent", "enlist", "google", "gogole", "cat", "act", "tac", "dog"]],
        _anagram_words(_r, 150, 6),
    ],
))

# ----------------------------------------------------------------------------- 4
def _topk_case(r, n, lo, hi, k):
    return [[r.randint(lo, hi) for _ in range(n)], k]


_r = random.Random(604)
PROBLEMS.append(dict(
    id="top-k-frequent-elements",
    title="Top K Frequent Elements",
    difficulty=2,
    tags=["hash map", "counting", "sorting", "heap"],
    fn="top_k_frequent",
    params=[["nums", "int[]"], ["k", "int"]],
    returns="int[]",
    statement=_d(r"""
Return the `k` most frequent values in `nums`.

To make the answer unique, rank the **distinct** values by:

1. frequency, **highest first**;
2. on equal frequency, by value, **smallest first**.

Return the first `k` values of that ranking, in ranking order. `k` is at most the
number of distinct values.
"""),
    example_notes=[
        "`1` appears 3 times, `2` twice, `3` once.",
        "`1` and `4` both appear twice; the tie is broken by value, so `1` comes first.",
    ],
    constraints=["1 ≤ len(nums) ≤ 10⁵", "-10⁴ ≤ nums[i] ≤ 10⁴", "1 ≤ k ≤ number of distinct values"],
    hints=[
        "First, how often does each value occur? One pass with a hash map.",
        "Now you have `m` distinct (value, count) pairs. Sort them by the ranking: key `(-count, value)`.",
        "For large `m` and small `k`, a heap of size `k` (O(m log k)) or bucket sort by count (O(n)) avoid the full sort.",
    ],
    explanation=_d(r"""
## Intuition

Two independent steps:

1. **Count** with a hash map: value → frequency. O(n).
2. **Select** the top k of the `m` distinct values by the given ranking.

The tie-break makes the ranking a *total order*, so the answer is unique. In Python,
sorting by the tuple `(-count, value)` encodes "count descending, then value ascending"
in one key.

## Approach

```python
cnt = Counter(nums)
ranked = sorted(cnt, key=lambda v: (-cnt[v], v))
return ranked[:k]
```

Trace on `[4, 4, 1, 1, 2]`, k = 2:

| value | count | sort key |
|---|---|---|
| 4 | 2 | (-2, 4) |
| 1 | 2 | (-2, 1) |
| 2 | 1 | (-1, 2) |

Sorted keys: `(-2,1) < (-2,4) < (-1,2)` → `[1, 4, 2]` → first two: `[1, 4]`.

### Faster selections

- **Heap:** keep a heap of the best `k` so far, O(m log k). Python's
  `heapq.nsmallest(k, cnt, key=lambda v: (-cnt[v], v))` does exactly this.
- **Bucket sort:** frequencies are between 1 and n, so put values into
  `buckets[count]` and walk from `n` down to 1. O(n + m) plus sorting each bucket for
  the tie-break.

## Complexity

- Counting: O(n) time, O(m) space.
- Full sort: O(m log m). Heap: O(m log k). Buckets: O(n) (+ tie-break sorting).

## Common mistakes

- **Ignoring ties.** Without a tie-break, "the" top-k isn't well defined; your output
  might differ from someone else's and both be "correct".
- **Wrong direction in a combined key.** In C++, a comparator
  `a.count != b.count ? a.count > b.count : a.value < b.value` is the equivalent.
  Mixing up `<`/`>` silently produces another order.
- **Heap direction:** to keep the k *largest*, use a *min*-heap of size k and pop the
  smallest when it overflows.
- **Rust:** `HashMap` iteration order is random; always sort explicitly.

## Going further

- **Top K Frequent Words** is the same with string ties broken lexicographically.
- **Quickselect** on the (value, count) array gets O(m) average for the selection step.
- Streaming version (can't store all counts): Count-Min Sketch + heap, or Misra–Gries.
"""),
    solution=_d(r"""
from collections import Counter

def top_k_frequent(nums, k):
    # Step 1: frequency of every distinct value, O(n).
    cnt = Counter(nums)
    # Step 2: rank distinct values by (count descending, value ascending).
    # Negating the count turns "descending" into the default ascending sort,
    # and the tuple's second component breaks ties by value.
    ranked = sorted(cnt, key=lambda v: (-cnt[v], v))
    return ranked[:k]
"""),
    refs={
        "c": _d(r"""
            typedef struct { long long val, cnt; } Item;

            static int cmp_ll(const void* a, const void* b) {
                long long x = *(const long long*)a, y = *(const long long*)b;
                return (x > y) - (x < y);
            }

            // Ranking order: higher count first, then smaller value first.
            static int cmp_item(const void* a, const void* b) {
                const Item *x = a, *y = b;
                if (x->cnt != y->cnt) return (x->cnt < y->cnt) - (x->cnt > y->cnt);   // descending
                return (x->val > y->val) - (x->val < y->val);                          // ascending
            }

            long long* top_k_frequent(long long* nums, int numsSize, long long k, int* returnSize) {
                // Without a built-in hash map, counting by sorting is simplest: after qsort, equal
                // values are adjacent, so one scan turns runs into (value, count) pairs.
                long long* a = malloc((numsSize ? numsSize : 1) * sizeof(long long));
                memcpy(a, nums, numsSize * sizeof(long long));      // don't reorder the caller's data
                qsort(a, numsSize, sizeof(long long), cmp_ll);

                Item* items = malloc((numsSize ? numsSize : 1) * sizeof(Item));
                int m = 0;
                for (int i = 0; i < numsSize;) {
                    int j = i;
                    while (j < numsSize && a[j] == a[i]) j++;
                    items[m++] = (Item){ a[i], j - i };
                    i = j;
                }
                qsort(items, m, sizeof(Item), cmp_item);

                long long* out = malloc((k ? k : 1) * sizeof(long long));
                for (long long i = 0; i < k; i++) out[i] = items[i].val;
                *returnSize = (int)k;
                free(a); free(items);
                return out;
            }
        """),
        "cpp": _d(r"""
            vector<long long> topKFrequent(vector<long long>& nums, long long k) {
                unordered_map<long long, long long> cnt;
                for (long long x : nums) cnt[x]++;           // operator[] starts at 0
                vector<pair<long long, long long>> items(cnt.begin(), cnt.end());   // (value, count)
                // partial_sort only orders the first k positions: O(m log k)
                partial_sort(items.begin(), items.begin() + k, items.end(),
                             [](const auto& a, const auto& b) {
                                 if (a.second != b.second) return a.second > b.second;  // more frequent first
                                 return a.first < b.first;                              // then smaller value
                             });
                vector<long long> out;
                for (long long i = 0; i < k; i++) out.push_back(items[i].first);
                return out;
            }
        """),
        "rust": _d(r"""
            use std::collections::HashMap;

            pub fn top_k_frequent(nums: Vec<i64>, k: i64) -> Vec<i64> {
                let mut cnt: HashMap<i64, usize> = HashMap::new();
                for x in nums {
                    *cnt.entry(x).or_insert(0) += 1; // entry API: one lookup per element
                }
                let mut items: Vec<(i64, usize)> = cnt.into_iter().collect();
                // count descending, then value ascending
                items.sort_unstable_by(|a, b| b.1.cmp(&a.1).then(a.0.cmp(&b.0)));
                items.into_iter().take(k as usize).map(|(v, _)| v).collect()
            }
        """),
    },
    tests=[
        [[1, 1, 1, 2, 2, 3], 2],
        [[4, 4, 1, 1, 2], 2],
        [[1], 1],
        [[-1, -1, 5, 5, 5, 0], 3],
        [[9, 8, 7, 6], 3],
        [[3, 3, 2, 2, 1, 1], 1],
        [[5, -5, 5, -5, 5, 0, 0, 0, 0], 2],
        _topk_case(_r, 300, -20, 20, 10),
        _topk_case(_r, 8000, -10**4, 10**4, 25),
    ],
))

# ----------------------------------------------------------------------------- 5
_r = random.Random(605)
PROBLEMS.append(dict(
    id="longest-consecutive-sequence",
    title="Longest Consecutive Sequence",
    difficulty=2,
    tags=["hash set", "array"],
    espresso=False,
    fn="longest_consecutive",
    params=[["nums", "int[]"]],
    returns="int",
    statement=_d(r"""
Given an unsorted array `nums`, return the length of the longest run of **consecutive
integers** `x, x+1, x+2, ..., x+L-1` whose values all appear in `nums` (in any
positions; duplicates count once).

Your algorithm should run in O(n) time.
"""),
    example_notes=[
        "`1, 2, 3, 4` are all present: length 4.",
        "`0` through `8` are present: length 9 (the duplicate `0` doesn't matter).",
    ],
    constraints=["0 ≤ len(nums) ≤ 10⁵", "-10⁹ ≤ nums[i] ≤ 10⁹"],
    hints=[
        "Sorting gives O(n log n). For O(n), you need O(1) answers to \"is `x + 1` present?\".",
        "Put everything in a set. From each value you could walk `x, x+1, x+2, ...`, but starting a walk from every value can be O(n²).",
        "Only start walking from values `x` where `x - 1` is **not** in the set: those are the starts of runs. Each value is then visited by at most one walk.",
    ],
    explanation=_d(r"""
## Intuition

Sorting and scanning works in O(n log n). The O(n) idea: put all values in a **hash
set**, then grow runs by asking "is the next integer there?" in O(1).

The danger is redundant work: walking from `1`, then again from `2`, then from `3`
in `[1, 2, 3, ..., n]` costs O(n²). The fix: **only start a run at its beginning**. A
value `x` begins a run exactly when `x - 1` is *not* in the set.

## Approach

```python
s = set(nums)
best = 0
for x in s:
    if x - 1 not in s:          # x is the start of a run
        y = x
        while y + 1 in s:
            y += 1
        best = max(best, y - x + 1)
```

Trace on `[100, 4, 200, 1, 3, 2]`:

| x | x-1 in set? | walk | length |
|---|---|---|---|
| 100 | no | 100 | 1 |
| 4 | yes (3) | skip | |
| 200 | no | 200 | 1 |
| 1 | no | 1→2→3→4 | **4** |
| 3 | yes | skip | |
| 2 | yes | skip | |

## Complexity

- **Time:** O(n) average. The `for` loop is O(n), and the inner `while` steps through
  each value **at most once over the whole algorithm**, because each value belongs to
  exactly one run and only that run's start walks through it.
- **Space:** O(n) for the set.

## Common mistakes

- **Iterating over `nums` instead of the set.** With many duplicates of a run start
  (`[1, 1, 1, ..., 2, 3, ...]`), you'd walk the same run once per duplicate. Iterate the
  set.
- **Forgetting the empty array** (answer 0).
- **Overflow in C/C++:** `x + 1` for `x` near the type's maximum. With 64-bit and the
  constraints here it's fine; with 32-bit `int` and `INT_MAX` it's undefined behaviour.

## Going further

- **Union-Find** solves it too: union `x` with `x+1` when both exist; the answer is the
  largest component.
- A sort-based solution is simpler and often faster in practice for moderate n: sort,
  then count runs while skipping equal neighbours. Good in **C**, which lacks a set.
"""),
    solution=_d(r"""
def longest_consecutive(nums):
    present = set(nums)  # O(1) "is v here?" and duplicates collapse for free
    best = 0
    for x in present:
        # Only start counting at the beginning of a run; otherwise this run
        # will be (or was) counted from its true start. This is what keeps the
        # total work linear.
        if x - 1 not in present:
            end = x
            while end + 1 in present:
                end += 1
            best = max(best, end - x + 1)
    return best
"""),
    refs={
        "c": _d(r"""
            static int cmp_ll(const void* a, const void* b) {
                long long x = *(const long long*)a, y = *(const long long*)b;
                return (x > y) - (x < y);
            }

            long long longest_consecutive(long long* nums, int numsSize) {
                // No hash set in C: sort (O(n log n)) and count runs of +1 steps.
                if (numsSize == 0) return 0;
                qsort(nums, numsSize, sizeof(long long), cmp_ll);
                long long best = 1, run = 1;
                for (int i = 1; i < numsSize; i++) {
                    if (nums[i] == nums[i - 1]) continue;           // duplicate: run unchanged
                    if (nums[i] == nums[i - 1] + 1) run++;           // extends the run
                    else run = 1;                                    // gap: new run
                    if (run > best) best = run;
                }
                return best;
            }
        """),
        "cpp": _d(r"""
            long long longestConsecutive(vector<long long>& nums) {
                unordered_set<long long> present(nums.begin(), nums.end());
                long long best = 0;
                for (long long x : present) {
                    if (present.count(x - 1)) continue;   // not the start of a run
                    long long end = x;
                    while (present.count(end + 1)) end++;
                    best = max(best, end - x + 1);
                }
                return best;
            }
        """),
        "rust": _d(r"""
            use std::collections::HashSet;

            pub fn longest_consecutive(nums: Vec<i64>) -> i64 {
                let present: HashSet<i64> = nums.into_iter().collect();
                let mut best = 0;
                for &x in &present {
                    if present.contains(&(x - 1)) {
                        continue; // x is inside a run, not at its start
                    }
                    let mut end = x;
                    while present.contains(&(end + 1)) {
                        end += 1;
                    }
                    best = best.max(end - x + 1);
                }
                best
            }
        """),
    },
    tests=[
        [[100, 4, 200, 1, 3, 2]],
        [[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]],
        [[]],
        [[42]],
        [[1, 2, 0, 1]],
        [[-3, -2, -1, 10, 11]],
        [[1, 1, 1, 1]],
        [[9, 1, 4, 7, 3, -1, 0, 5, 8, -1, 6]],
        [[_r.randint(-5000, 5000) for _ in range(4000)]],
        [list(range(0, 4000, 2)) + list(range(10**6, 10**6 + 1500))[::-1]],
    ],
))

# ----------------------------------------------------------------------------- 6
_r = random.Random(606)
PROBLEMS.append(dict(
    id="subarray-sum-equals-k",
    title="Subarray Sum Equals K",
    difficulty=2,
    tags=["hash map", "prefix sums"],
    espresso=False,
    fn="subarray_sum",
    params=[["nums", "int[]"], ["k", "int"]],
    returns="int",
    statement=_d(r"""
Return the number of **contiguous, non-empty** subarrays of `nums` whose elements sum to
exactly `k`. Elements may be negative or zero.
"""),
    example_notes=[
        "`[1,1]` at positions 0–1 and `[1,1]` at positions 1–2.",
        "`[1,2]` and `[3]`.",
    ],
    constraints=["1 ≤ len(nums) ≤ 2·10⁴", "-1000 ≤ nums[i] ≤ 1000", "-10⁷ ≤ k ≤ 10⁷"],
    hints=[
        "With prefix sums, `sum(nums[i..j]) = P[j+1] - P[i]`. Rewrite \"subarray sums to k\" in terms of two prefix sums.",
        "For each end position, you need the number of earlier prefix sums equal to `P[j+1] - k`.",
        "Sweep once, keeping a hash map `prefix sum → how many times seen`. Start it with `{0: 1}` (the empty prefix).",
    ],
    explanation=_d(r"""
## Intuition

A sliding window doesn't work here: with negative numbers, growing the window can
*decrease* the sum, so there's no monotonic rule for moving the pointers.

Use **prefix sums** instead. With `P[0] = 0` and `P[t] = nums[0] + ... + nums[t-1]`:

```
sum(nums[i..j]) = P[j+1] - P[i] = k      <=>      P[i] = P[j+1] - k
```

So for each end position, the number of good subarrays ending there equals **the number
of earlier prefix sums equal to `current - k`**. Counting earlier values in O(1) is a
job for a hash map.

## Approach

```python
count = {0: 1}     # the empty prefix P[0] = 0 has been "seen" once
cur = ans = 0
for x in nums:
    cur += x                        # cur = P[j+1]
    ans += count.get(cur - k, 0)    # earlier prefixes that complete a sum-k subarray
    count[cur] = count.get(cur, 0) + 1
```

Trace on `nums = [1, 2, 3]`, k = 3:

| x | cur | need cur-k | count before | +ans | count after |
|---|---|---|---|---|---|
| 1 | 1 | -2 | {0:1} | 0 | {0:1, 1:1} |
| 2 | 3 | 0 | {0:1, 1:1} | 1 (`[1,2]`) | {…, 3:1} |
| 3 | 6 | 3 | {0:1, 1:1, 3:1} | 1 (`[3]`) | {…, 6:1} |

Answer 2.

## Complexity

- **Time:** O(n) average, one pass with O(1) map operations.
- **Space:** O(n) for the map of prefix sums.

## Common mistakes

- **Forgetting `{0: 1}`.** Without it, subarrays that start at index 0 are never
  counted (their "earlier prefix" is the empty one).
- **Inserting `cur` before the lookup.** With `k = 0` you'd count the empty subarray at
  every position.
- **Using a set instead of counts.** Equal prefix sums can occur many times (zeros, or
  `+1, -1` patterns), and each occurrence is a distinct subarray.
- **Two pointers / sliding window:** only valid when all numbers are positive.

## Going further

- **Longest subarray with sum k:** store the *first* index of each prefix sum instead of
  a count.
- **Subarray sums divisible by k:** key the map by `cur mod k` (careful with negative
  remainders in C/C++/Rust: use `((cur % k) + k) % k`).
- **2-D:** count submatrices with sum k by fixing a pair of rows and running this
  algorithm on column sums: O(R² · C).
"""),
    solution=_d(r"""
def subarray_sum(nums, k):
    # count[s] = how many prefixes seen so far have sum s.
    # The empty prefix (sum 0) exists before we read anything; it's what lets
    # subarrays starting at index 0 be counted.
    count = {0: 1}
    cur = 0   # sum of nums[0..j]
    ans = 0
    for x in nums:
        cur += x
        # Each earlier prefix with sum cur - k marks a start i such that
        # nums[i..j] sums to exactly k.
        ans += count.get(cur - k, 0)
        # Record this prefix only *after* the lookup, so we never pair a prefix
        # with itself (which would be an empty subarray).
        count[cur] = count.get(cur, 0) + 1
    return ans
"""),
    lang_notes={"c": _d(r"""
In C, implement the `prefix sum → count` map with open addressing (see the table in Two
Sum's C notes; store a count instead of an index). There are at most `n + 1` distinct
prefix sums, so a capacity of the next power of two ≥ `2(n + 1)` never needs resizing.
The reference solution below does exactly that.
""")},
    refs={
        "c": _d(r"""
            static size_t mix64(long long k) {
                unsigned long long x = (unsigned long long)k;
                x ^= x >> 30; x *= 0xbf58476d1ce4e5b9ULL;
                x ^= x >> 27; x *= 0x94d049bb133111ebULL;
                return (size_t)(x ^ (x >> 31));
            }

            long long subarray_sum(long long* nums, int numsSize, long long k) {
                size_t cap = 4;
                while (cap < 2 * (size_t)(numsSize + 1)) cap <<= 1;
                size_t mask = cap - 1;
                long long* keys = malloc(cap * sizeof(long long));
                long long* cnt = calloc(cap, sizeof(long long));   // cnt == 0 means "empty slot"
                // Probe for key: returns its slot, or the empty slot where it belongs.
                #define SLOT(key, out) do { size_t s_ = mix64(key) & mask; \
                    while (cnt[s_] && keys[s_] != (key)) s_ = (s_ + 1) & mask; out = s_; } while (0)
                size_t s;
                SLOT(0LL, s); keys[s] = 0; cnt[s] = 1;             // the empty prefix
                long long cur = 0, ans = 0;
                for (int i = 0; i < numsSize; i++) {
                    cur += nums[i];
                    SLOT(cur - k, s);
                    ans += cnt[s];                                 // 0 if the slot is empty
                    SLOT(cur, s);
                    keys[s] = cur; cnt[s]++;
                }
                #undef SLOT
                free(keys); free(cnt);
                return ans;
            }
        """),
        "cpp": _d(r"""
            long long subarraySum(vector<long long>& nums, long long k) {
                unordered_map<long long, long long> count{{0, 1}};   // empty prefix
                long long cur = 0, ans = 0;
                for (long long x : nums) {
                    cur += x;
                    auto it = count.find(cur - k);
                    if (it != count.end()) ans += it->second;
                    count[cur]++;
                }
                return ans;
            }
        """),
        "rust": _d(r"""
            use std::collections::HashMap;

            pub fn subarray_sum(nums: Vec<i64>, k: i64) -> i64 {
                let mut count: HashMap<i64, i64> = HashMap::new();
                count.insert(0, 1); // the empty prefix
                let (mut cur, mut ans) = (0i64, 0i64);
                for x in nums {
                    cur += x;
                    ans += count.get(&(cur - k)).copied().unwrap_or(0);
                    *count.entry(cur).or_insert(0) += 1;
                }
                ans
            }
        """),
    },
    tests=[
        [[1, 1, 1], 2],
        [[1, 2, 3], 3],
        [[1], 0],
        [[0, 0, 0], 0],
        [[1, -1, 0], 0],
        [[3, 4, 7, 2, -3, 1, 4, 2], 7],
        [[-1, -1, 1], 0],
        [[5], 5],
        [[_r.randint(-3, 3) for _ in range(100)], 2],
        [[_r.randint(-10, 10) for _ in range(12000)], 7],
    ],
))

# ----------------------------------------------------------------------------- 7
_r = random.Random(607)
_iso_s = "".join(_r.choice("abcdefghij") for _ in range(3000))
_iso_t = _iso_s.translate(str.maketrans("abcdefghij", "QWERTYUIOP"))  # a true bijection
_iso_s2 = "".join(_r.choice("pqrstu") for _ in range(3000))
_iso_t2 = _iso_s2.translate(str.maketrans("pqrstu", "123456"))
_iso_t2 = _iso_t2[:-1] + ("1" if _iso_s2[-1] != "p" else "2")  # break it at the very end
PROBLEMS.append(dict(
    id="isomorphic-strings",
    title="Isomorphic Strings",
    difficulty=1,
    tags=["hash map", "string", "bijection"],
    fn="is_isomorphic",
    params=[["s", "str"], ["t", "str"]],
    returns="bool",
    statement=_d(r"""
Two strings `s` and `t` of the **same length** are *isomorphic* if the characters of `s`
can be replaced to get `t`, where:

- every occurrence of a character is replaced by the **same** character, and
- **no two different** characters map to the same character (a character may map to
  itself).

Return whether `s` and `t` are isomorphic. Strings consist of printable ASCII characters.
"""),
    example_notes=[
        "`e → a`, `g → d`.",
        "`o` would have to map to both `a` and `r`.",
    ],
    constraints=["0 ≤ len(s) = len(t) ≤ 5·10⁴", "printable ASCII characters"],
    hints=[
        "Record, for each character of `s`, which character of `t` it maps to. When can that go wrong?",
        "A map `s → t` catches \"one character mapped two ways\" (`foo`/`bar`). But it misses \"two characters mapped to the same one\" (`ab`/`aa`).",
        "Keep **two** maps, `s → t` and `t → s`, and check both at every position. Or: compare the first-occurrence index of `s[i]` in `s` with that of `t[i]` in `t`.",
    ],
    explanation=_d(r"""
## Intuition

"Each character maps consistently" is a **function** `s → t`. "No two characters map to
the same one" makes it **injective**. A function that's injective (and, since the
strings have equal length, onto the used characters) is a **bijection**. To check a
bijection, check the mapping in **both** directions.

One map isn't enough:

```
s = "ab", t = "aa"
s->t:  a->a, b->a        consistent!   but a and b both map to a.
t->s:  a->a, then a->b   conflict      <- caught only by the reverse map
```

## Approach

```python
fwd, back = {}, {}
for a, b in zip(s, t):
    if fwd.get(a, b) != b or back.get(b, a) != a:
        return False
    fwd[a] = b
    back[b] = a
return True
```

`fwd.get(a, b)` returns the existing mapping, or `b` itself if there is none, a compact
way to say "unmapped or already mapped to `b`".

Trace on `s = "paper"`, `t = "title"`:

| a | b | fwd | back | ok? |
|---|---|---|---|---|
| p | t | p→t | t→p | ✓ |
| a | i | a→i | i→a | ✓ |
| p | t | (p→t) | (t→p) | ✓ |
| e | l | e→l | l→e | ✓ |
| r | e | r→e | e→r | ✓ |

**Alternative:** two strings are isomorphic iff their *patterns of first occurrences*
agree: `"paper" → [0,1,0,3,4]`, `"title" → [0,1,0,3,4]`.

**Language mechanics.** Characters are bytes here, so in C a pair of `int map[256]`
arrays (initialised to -1) is a perfect, collision-free "hash table": the byte value
*is* the index. This direct addressing is the fastest option whenever keys are small
integers.

## Complexity

- **Time:** O(n).
- **Space:** O(Σ) where Σ is the alphabet size (at most 95 printable ASCII characters),
  so O(1) in practice.

## Common mistakes

- **Only checking `s → t`.** Fails `ab` / `aa`.
- **Checking only that the number of distinct characters matches.** `ab`/`ba`-style
  counts can match while the positions disagree (`"aab"` vs `"abb"`).
- **C:** `char` may be signed; index with `(unsigned char)s[i]`.

## Going further

Word Pattern (next problem) is the same bijection check with words instead of
characters on one side. Canonical "first-occurrence" signatures also let you *group*
isomorphic strings with a hash map, like Group Anagrams.
"""),
    solution=_d(r"""
def is_isomorphic(s, t):
    # A valid replacement is a bijection between the characters used, so we
    # track the mapping in both directions.
    fwd = {}   # char of s -> char of t
    back = {}  # char of t -> char of s
    for a, b in zip(s, t):
        # fwd.get(a, b) is b when a is unmapped, so this only fails when a was
        # previously mapped to something else; likewise for the reverse map.
        if fwd.get(a, b) != b or back.get(b, a) != a:
            return False
        fwd[a] = b
        back[b] = a
    return True
"""),
    refs={
        "c": _d(r"""
            bool is_isomorphic(char* s, char* t) {
                // Bytes are small integers, so plain arrays act as perfect hash tables.
                int fwd[256], back[256];
                for (int i = 0; i < 256; i++) fwd[i] = back[i] = -1;
                for (size_t i = 0; s[i]; i++) {
                    unsigned char a = (unsigned char)s[i], b = (unsigned char)t[i];
                    if (fwd[a] == -1 && back[b] == -1) { fwd[a] = b; back[b] = a; }
                    else if (fwd[a] != b || back[b] != a) return false;
                }
                return true;
            }
        """),
        "cpp": _d(r"""
            bool isIsomorphic(string s, string t) {
                // Compare "first seen at" positions: isomorphic iff they match everywhere.
                array<int, 256> firstS, firstT;
                firstS.fill(-1); firstT.fill(-1);
                for (int i = 0; i < (int)s.size(); i++) {
                    unsigned char a = s[i], b = t[i];
                    if (firstS[a] != firstT[b]) return false;
                    firstS[a] = firstT[b] = i;   // "last seen at" works the same way
                }
                return true;
            }
        """),
        "rust": _d(r"""
            use std::collections::HashMap;

            pub fn is_isomorphic(s: String, t: String) -> bool {
                let mut fwd: HashMap<u8, u8> = HashMap::new();
                let mut back: HashMap<u8, u8> = HashMap::new();
                for (a, b) in s.bytes().zip(t.bytes()) {
                    // entry().or_insert() returns the existing value, or inserts ours
                    if *fwd.entry(a).or_insert(b) != b || *back.entry(b).or_insert(a) != a {
                        return false;
                    }
                }
                true
            }
        """),
    },
    tests=[
        ["egg", "add"],
        ["foo", "bar"],
        ["paper", "title"],
        ["badc", "baba"],
        ["", ""],
        ["a", "a"],
        ["ab", "aa"],
        ["aab", "abb"],
        ["13", "42"],
        ["a b!", "x?yz"],
        [_iso_s, _iso_t],
        [_iso_s2, _iso_t2],
    ],
))

# ----------------------------------------------------------------------------- 8
PROBLEMS.append(dict(
    id="word-pattern",
    title="Word Pattern",
    difficulty=1,
    tags=["hash map", "string", "bijection"],
    fn="word_pattern",
    params=[["pattern", "str"], ["s", "str"]],
    returns="bool",
    statement=_d(r"""
`pattern` is a string of lowercase letters; `s` is a sequence of lowercase words
separated by **single spaces** (no leading or trailing spaces).

`s` *follows* `pattern` if there is a **bijection** between letters of `pattern` and
words of `s`: the k-th letter corresponds to the k-th word, equal letters always
correspond to equal words, and different letters always correspond to different words.

Return whether `s` follows `pattern`.
"""),
    example_notes=[
        "`a ↔ dog`, `b ↔ cat`.",
        "`a` would have to be both `dog` and `fish`.",
    ],
    constraints=["1 ≤ len(pattern) ≤ 300", "1 ≤ len(s) ≤ 3000", "`s` has no leading/trailing or double spaces"],
    hints=[
        "Split `s` into words first. What if the number of words differs from the pattern's length?",
        "This is Isomorphic Strings with words on one side. A single letter→word map is not enough: why?",
        "Keep `letter → word` and `word → letter` maps and check both at each position.",
    ],
    explanation=_d(r"""
## Intuition

Exactly like Isomorphic Strings: we need a **bijection**, so we check the mapping in
both directions. The only differences are parsing (split `s` into words) and that one
side's keys are whole words, which hash in O(length of the word).

Why both directions? With `pattern = "ab"`, `s = "dog dog"`, the map `a→dog, b→dog` is
perfectly consistent, yet `a` and `b` share a word. Only `word → letter` catches it.

## Approach

1. `words = s.split(" ")`. If `len(words) != len(pattern)`, return `False`.
2. Walk the pairs `(letter, word)`:
   - if `letter` is mapped to a different word → `False`;
   - if `word` is mapped to a different letter → `False`;
   - otherwise record both mappings.
3. Return `True`.

Trace: `pattern = "abba"`, `s = "dog cat cat dog"`:

| letter | word | letter→word | word→letter |
|---|---|---|---|
| a | dog | a→dog | dog→a |
| b | cat | b→cat | cat→b |
| b | cat | ✓ | ✓ |
| a | dog | ✓ | ✓ |

**Language mechanics.** Splitting is easy in Python (`split`), C++ (`istringstream` and
`>>`) and Rust (`split(' ')` / `split_whitespace()`). In C you'd walk the string with
`strtok` (which *modifies* its input: copy it first) or manual pointer scanning.

## Complexity

- **Time:** O(len(pattern) + len(s)): splitting and hashing touch each character a
  constant number of times.
- **Space:** O(len(s)) for the words and maps.

## Common mistakes

- **Not checking the lengths.** `zip` silently stops at the shorter input, so
  `"aaa"` vs `"dog dog"` would wrongly return `True`.
- **Only one map**, which misses two letters mapping to the same word.
- **Comparing word *lengths* or first letters** instead of whole words.

## Going further

- **Word Pattern II:** no spaces in `s`; you must *choose* how to split it. That
  needs backtracking, with the same two-map consistency check at each step.
- The two-map bijection check is the general tool whenever a problem says "one-to-one".
"""),
    solution=_d(r"""
def word_pattern(pattern, s):
    words = s.split(" ")
    # Different counts can never correspond one-to-one. (zip() would silently
    # truncate, so this check is essential.)
    if len(words) != len(pattern):
        return False
    to_word = {}    # letter -> word
    to_letter = {}  # word -> letter
    for ch, w in zip(pattern, words):
        # Each direction catches a different violation:
        #   to_word catches one letter used for two words,
        #   to_letter catches two letters used for one word.
        if to_word.get(ch, w) != w or to_letter.get(w, ch) != ch:
            return False
        to_word[ch] = w
        to_letter[w] = ch
    return True
"""),
    refs={
        "c": _d(r"""
            bool word_pattern(char* pattern, char* s) {
                // Split s into words without copying: record where each word starts and its length.
                size_t plen = strlen(pattern), slen = strlen(s);
                const char** start = malloc((slen + 1) * sizeof(char*));
                size_t* len = malloc((slen + 1) * sizeof(size_t));
                size_t nw = 0;
                for (size_t i = 0; i < slen;) {
                    size_t j = i;
                    while (j < slen && s[j] != ' ') j++;
                    start[nw] = s + i; len[nw] = j - i; nw++;
                    i = j + 1;                                     // skip the single space
                }
                bool ok = nw == plen;                              // one word per letter

                // firstWord[c] = index of the word letter c maps to, or -1 if c is unseen.
                // Letters are only 'a'..'z', so a 26-slot array is our "hash map".
                int firstWord[26];
                for (int c = 0; c < 26; c++) firstWord[c] = -1;
                for (size_t i = 0; ok && i < plen; i++) {
                    int c = pattern[i] - 'a';
                    if (firstWord[c] >= 0) {
                        // Letter seen before: this word must equal the one it already maps to.
                        int w = firstWord[c];
                        ok = len[w] == len[i] && memcmp(start[w], start[i], len[i]) == 0;
                    } else {
                        // New letter: its word must not already belong to a *different* letter.
                        // At most 26 letters are mapped, so this check is O(26).
                        for (int d = 0; d < 26 && ok; d++) {
                            int w = firstWord[d];
                            if (w >= 0 && len[w] == len[i] && memcmp(start[w], start[i], len[i]) == 0) ok = false;
                        }
                        firstWord[c] = (int)i;
                    }
                }
                free(start); free(len);
                return ok;
            }
        """),
        "cpp": _d(r"""
            bool wordPattern(string pattern, string s) {
                istringstream in(s);
                vector<string> words;
                for (string w; in >> w;) words.push_back(w);
                if (words.size() != pattern.size()) return false;
                unordered_map<char, string> toWord;
                unordered_map<string, char> toLetter;
                for (size_t i = 0; i < words.size(); i++) {
                    char c = pattern[i];
                    auto a = toWord.find(c);
                    auto b = toLetter.find(words[i]);
                    if (a != toWord.end() && a->second != words[i]) return false;
                    if (b != toLetter.end() && b->second != c) return false;
                    toWord[c] = words[i];
                    toLetter[words[i]] = c;
                }
                return true;
            }
        """),
        "rust": _d(r"""
            use std::collections::HashMap;

            pub fn word_pattern(pattern: String, s: String) -> bool {
                let words: Vec<&str> = s.split(' ').collect();
                if words.len() != pattern.len() {
                    return false;
                }
                let mut to_word: HashMap<u8, &str> = HashMap::new();
                let mut to_letter: HashMap<&str, u8> = HashMap::new();
                for (c, w) in pattern.bytes().zip(words.iter().copied()) {
                    if *to_word.entry(c).or_insert(w) != w || *to_letter.entry(w).or_insert(c) != c {
                        return false;
                    }
                }
                true
            }
        """),
    },
    tests=[
        ["abba", "dog cat cat dog"],
        ["abba", "dog cat cat fish"],
        ["aaaa", "dog cat cat dog"],
        ["abba", "dog dog dog dog"],
        ["a", "x"],
        ["aaa", "x x"],
        ["ab", "x y z"],
        ["abc", "b c a"],
        ["aa", "dog dogs"],
        ["abcabc", "one two three one two three"],
        ["abcdefghij" * 20, " ".join(["w" + str(i % 10) for i in range(200)])],
        ["abcdefghij" * 20, " ".join(["w" + str(i % 10) for i in range(199)] + ["w1"])],
    ],
))

# ----------------------------------------------------------------------------- 9
PROBLEMS.append(dict(
    id="happy-number",
    title="Happy Number",
    difficulty=1,
    tags=["hash set", "math", "cycle detection"],
    fn="is_happy",
    params=[["n", "int"]],
    returns="bool",
    statement=_d(r"""
Start from a positive integer `n` and repeatedly replace it with the **sum of the
squares of its decimal digits**. If this process reaches `1`, `n` is *happy*. Otherwise
it loops forever in a cycle that doesn't contain 1.

Return whether `n` is happy.
"""),
    example_notes=[
        "19 → 1² + 9² = 82 → 68 → 100 → 1.",
        "2 → 4 → 16 → 37 → 58 → 89 → 145 → 42 → 20 → 4 → … (a cycle without 1).",
    ],
    constraints=["1 ≤ n ≤ 10⁷"],
    hints=[
        "Write the digit-square-sum step first: peel off digits with `% 10` and `// 10`.",
        "The sequence either hits 1 or repeats a value. How do you notice a repeat?",
        "Store every value you've seen in a set and stop when you see one again. For O(1) memory, run a slow and a fast pointer (Floyd's cycle detection).",
    ],
    explanation=_d(r"""
## Intuition

Each number has exactly one successor, so the sequence `n, f(n), f(f(n)), ...` is a
path in a "functional graph". Such a path either reaches 1 (and stays there, since
`f(1) = 1`) or eventually **repeats** a value, after which it cycles forever.

Why must it repeat or reach 1, rather than grow forever? A number with `d` digits has
`f(x) ≤ 81·d`, which is much smaller than `x` once `x` has 4+ digits. So values quickly
fall below 1000 and stay there, and a sequence confined to finitely many values must
repeat.

So the question is **cycle detection**, and the hash-set answer is: remember every
value; if one comes back, we're in a loop.

## Approach

```python
seen = set()
while n != 1 and n not in seen:
    seen.add(n)
    n = digit_square_sum(n)
return n == 1
```

**Digit extraction** is the language-mechanics core: `n % 10` is the last digit and
`n // 10` drops it. Loop until `n` is 0.

```
digit_square_sum(82): 82 % 10 = 2 -> 4;  82 // 10 = 8
                       8 % 10 = 8 -> 64;  8 // 10 = 0   => 68
```

### O(1) memory: Floyd's tortoise and hare

Move `slow` one step and `fast` two steps at a time. If there's a cycle, `fast` laps
`slow` and they meet; if the sequence reaches 1, `fast` gets there first (and 1 is a
cycle of length 1, so they also meet *at 1*). Either way, check whether the meeting
point is 1. This is the same algorithm as detecting a cycle in a linked list.

## Complexity

- **Time:** O(log n) for the first few steps (digits of n), then a bounded number of
  steps among values below ~1000: effectively O(log n).
- **Space:** O(log n) for the set version (a bounded number of distinct values), O(1)
  for Floyd.

## Common mistakes

- **Looping without cycle detection.** Unhappy numbers loop forever.
- **Hard-coding "stop after 100 steps".** It happens to work, but it's a guess, not an
  argument.
- **ESPresso:** there's no `%` operator; compute the last digit as `n - (n / 10) * 10`.

## Going further

- Every unhappy number falls into the single cycle `4 → 16 → 37 → 58 → 89 → 145 → 42 →
  20 → 4`, so checking `n == 4` also works. Fun, but not something you'd know in an
  interview.
- Floyd's algorithm can also find the *start* of the cycle: reset one pointer to the
  start and advance both one step at a time until they meet (Linked List Cycle II, Find
  the Duplicate Number).
"""),
    solution=_d(r"""
def is_happy(n):
    def step(x):
        # Sum of squared decimal digits: x % 10 is the last digit,
        # x // 10 removes it.
        total = 0
        while x > 0:
            d = x % 10
            total += d * d
            x //= 10
        return total

    # Every value has a single successor, so the sequence either reaches 1 or
    # revisits a value and cycles forever. A set detects the revisit.
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = step(n)
    return n == 1
"""),
    refs={
        "c": _d(r"""
            static long long step(long long x) {
                long long total = 0;
                while (x > 0) { long long d = x % 10; total += d * d; x /= 10; }
                return total;
            }

            bool is_happy(long long n) {
                // Floyd's cycle detection: no set needed.
                long long slow = n, fast = step(n);
                while (fast != 1 && slow != fast) {
                    slow = step(slow);
                    fast = step(step(fast));
                }
                return fast == 1;
            }
        """),
        "cpp": _d(r"""
            long long digitSquareSum(long long x) {
                long long t = 0;
                for (; x > 0; x /= 10) t += (x % 10) * (x % 10);
                return t;
            }
            bool isHappy(long long n) {
                unordered_set<long long> seen;
                while (n != 1 && seen.insert(n).second)   // insert fails => repeat => cycle
                    n = digitSquareSum(n);
                return n == 1;
            }
        """),
        "rust": _d(r"""
            fn step(mut x: i64) -> i64 {
                let mut t = 0;
                while x > 0 {
                    let d = x % 10;
                    t += d * d;
                    x /= 10;
                }
                t
            }

            pub fn is_happy(n: i64) -> bool {
                // Floyd: slow moves 1 step, fast moves 2; they meet inside any cycle.
                let (mut slow, mut fast) = (n, step(n));
                while fast != 1 && slow != fast {
                    slow = step(slow);
                    fast = step(step(fast));
                }
                fast == 1
            }
        """),
        "espresso": _d(r"""
            fn step(x) {
              var t = 0
              while x > 0 {
                var d = x - (x / 10) * 10   // x mod 10 (no % operator)
                t += d * d
                x = x / 10                  // integer division truncates
              }
              return t
            }

            fn isHappy(n) {
              // Floyd's tortoise and hare: no hash set required
              var slow = n
              var fast = step(n)
              while fast != 1 and slow != fast {
                slow = step(slow)
                fast = step(step(fast))
              }
              return fast == 1
            }
        """),
    },
    tests=[[19], [2], [1], [7], [4], [100], [1111111], [9999999], [3], [10000000], [7777777]],
))

# ---------------------------------------------------------------------------- 10
_r = random.Random(610)
PROBLEMS.append(dict(
    id="intersection-of-two-arrays",
    title="Intersection of Two Arrays",
    difficulty=1,
    tags=["hash set", "sorting", "two pointers"],
    fn="intersection",
    params=[["nums1", "int[]"], ["nums2", "int[]"]],
    returns="int[]",
    statement=_d(r"""
Return the **distinct** values that appear in both `nums1` and `nums2`, sorted in
**increasing** order.
"""),
    example_notes=["Only `2` is in both arrays (reported once).", "`4` and `9`, sorted."],
    constraints=["0 ≤ len(nums1), len(nums2) ≤ 10⁴", "-10⁹ ≤ values ≤ 10⁹"],
    hints=[
        "For each value of one array, you need a fast \"is it in the other array?\".",
        "Build a set from `nums1`, then collect the values of `nums2` that are in it (into another set, to drop duplicates). Sort at the end.",
        "Without hashing: sort both arrays and walk them with two pointers, like merging, emitting equal values once.",
    ],
    explanation=_d(r"""
## Intuition

Membership tests against a list are O(n) each, so a double loop is O(n·m). Turning one
array into a **hash set** makes each test O(1). Python even has set intersection built in:
`set(nums1) & set(nums2)`.

Because hash sets are unordered, the result must be **sorted at the end** to match the
required output.

## Approach

```python
common = set(nums1) & set(nums2)    # distinct values in both
return sorted(common)
```

Under the hood, `&` iterates over the smaller set and keeps the elements found in the
larger one: O(min(n, m)) average.

### Sort + two pointers (no hashing)

Sort both arrays. Walk `i` over `nums1` and `j` over `nums2`:

- `a[i] < b[j]`: `i += 1`; `a[i] > b[j]`: `j += 1`;
- equal: emit it (unless it equals the last value emitted), advance both.

The output is produced already sorted. This is the natural approach in **C**.

```
a = [1 1 2 2]     b = [2 2]
     i                 j      1 < 2   i++
       i               j      1 < 2   i++
         i             j      2 = 2   emit 2, i++, j++
           i             j    2 = 2   same as last emitted, skip
```

## Complexity

| approach | time | extra space |
|---|---|---|
| sets | O(n + m + k log k) average (k = result size) | O(n + m) |
| sort + two pointers | O(n log n + m log m) | O(1) beyond sorting |

## Common mistakes

- **Forgetting to deduplicate** (`[1,2,2,1]` and `[2,2]` must give `[2]`, not `[2,2]`).
- **Forgetting to sort** the set result; set iteration order is arbitrary.
- **C:** comparator overflow (`return a - b` on `long long`); use `(a > b) - (a < b)`.

## Going further

- **Intersection II** keeps multiplicities (`[2, 2]` in the example above): use a
  `Counter` and decrement, or the same two-pointer walk without the dedupe check.
- If one array is tiny and the other huge and sorted, binary-search each small element
  in the big one: O(small · log big).
"""),
    solution=_d(r"""
def intersection(nums1, nums2):
    # Sets drop duplicates and give O(1) average membership tests; the &
    # operator keeps values present in both.
    common = set(nums1) & set(nums2)
    # Hash sets have no order, so sort to produce the required output.
    return sorted(common)
"""),
    refs={
        "c": _d(r"""
            static int cmp_ll(const void* a, const void* b) {
                long long x = *(const long long*)a, y = *(const long long*)b;
                return (x > y) - (x < y);
            }

            long long* intersection(long long* nums1, int nums1Size, long long* nums2, int nums2Size, int* returnSize) {
                qsort(nums1, nums1Size, sizeof(long long), cmp_ll);
                qsort(nums2, nums2Size, sizeof(long long), cmp_ll);
                int cap = nums1Size < nums2Size ? nums1Size : nums2Size;
                long long* out = malloc(sizeof(long long) * (cap > 0 ? cap : 1));
                int i = 0, j = 0, k = 0;
                while (i < nums1Size && j < nums2Size) {
                    if (nums1[i] < nums2[j]) i++;
                    else if (nums1[i] > nums2[j]) j++;
                    else {
                        if (k == 0 || out[k - 1] != nums1[i]) out[k++] = nums1[i];  // emit once
                        i++; j++;
                    }
                }
                *returnSize = k;
                return out;
            }
        """),
        "cpp": _d(r"""
            vector<long long> intersection(vector<long long>& nums1, vector<long long>& nums2) {
                unordered_set<long long> a(nums1.begin(), nums1.end());
                unordered_set<long long> both;
                for (long long x : nums2)
                    if (a.count(x)) both.insert(x);
                vector<long long> out(both.begin(), both.end());
                sort(out.begin(), out.end());
                return out;
            }
        """),
        "rust": _d(r"""
            use std::collections::HashSet;

            pub fn intersection(nums1: Vec<i64>, nums2: Vec<i64>) -> Vec<i64> {
                let a: HashSet<i64> = nums1.into_iter().collect();
                let b: HashSet<i64> = nums2.into_iter().collect();
                let mut out: Vec<i64> = a.intersection(&b).copied().collect();
                out.sort_unstable();
                out
            }
        """),
    },
    tests=[
        [[1, 2, 2, 1], [2, 2]],
        [[4, 9, 5], [9, 4, 9, 8, 4]],
        [[], [1, 2]],
        [[1, 2, 3], [4, 5, 6]],
        [[-1, -1, 0, 7], [7, -1, 3]],
        [[5, 5, 5], [5]],
        [[3, 1, 2], [2, 3, 1]],
        [[_r.randint(-3000, 3000) for _ in range(3000)], [_r.randint(-3000, 3000) for _ in range(2000)]],
    ],
))

# ---------------------------------------------------------------------------- 11
def _fsc_case(r, n, lo, hi):
    return [[r.randint(lo, hi) for _ in range(n)] for _ in range(4)]


_r = random.Random(611)
PROBLEMS.append(dict(
    id="four-sum-count",
    title="4Sum II",
    difficulty=2,
    tags=["hash map", "meet in the middle"],
    espresso=False,
    fn="four_sum_count",
    params=[["nums1", "int[]"], ["nums2", "int[]"], ["nums3", "int[]"], ["nums4", "int[]"]],
    returns="int",
    statement=_d(r"""
You are given four integer arrays of the same length `n`. Count the tuples of indices
`(i, j, k, l)` such that

```
nums1[i] + nums2[j] + nums3[k] + nums4[l] == 0
```

Different index tuples count separately even if the values are the same.
"""),
    example_notes=[
        "`(0,0,0,1)`: 1 + (-2) + (-1) + 2 = 0 and `(1,1,0,0)`: 2 + (-1) + (-1) + 0 = 0.",
        "The single tuple `(0,0,0,0)` sums to zero.",
    ],
    constraints=["1 ≤ n ≤ 200", "-2²⁸ ≤ values ≤ 2²⁸"],
    hints=[
        "Four nested loops are O(n⁴): 1.6·10⁹ for n = 200. Can you split the four arrays into two halves?",
        "`a + b + c + d = 0` means `a + b = -(c + d)`. Compute all `n²` sums `a + b` first.",
        "Store the sums `a + b` in a hash map with their counts. Then for every `c + d`, add `count[-(c + d)]`.",
    ],
    explanation=_d(r"""
## Intuition

Brute force tries all n⁴ tuples. The trick is **meet in the middle**: split the
equation down the middle.

```
nums1[i] + nums2[j]  =  -(nums3[k] + nums4[l])
\_______ left _____/     \________ right ______/
```

There are only n² possible left sums and n² right sums. If we **count** the left sums
in a hash map, each right sum can look up how many left sums cancel it in O(1).

## Approach

```python
left = Counter(a + b for a in nums1 for b in nums2)       # n^2 entries
return sum(left[-(c + d)] for c in nums3 for d in nums4)  # n^2 lookups
```

Trace on `nums1 = [1, 2]`, `nums2 = [-2, -1]`, `nums3 = [-1, 2]`, `nums4 = [0, 2]`:

```
left sums a+b: 1-2=-1, 1-1=0, 2-2=0, 2-1=1      => {-1:1, 0:2, 1:1}
right sums c+d and lookups of -(c+d):
  -1+0 = -1 -> left[1]  = 1
  -1+2 =  1 -> left[-1] = 1
   2+0 =  2 -> left[-2] = 0
   2+2 =  4 -> left[-4] = 0
total = 2
```

Note that `left` stores *counts*, not just presence: `0` arises from two different
`(i, j)` pairs, and each one forms a separate tuple.

## Complexity

- **Time:** O(n²) average: n² inserts plus n² lookups.
- **Space:** O(n²) for the map (up to 40 000 entries here).

## Common mistakes

- **Using a set** instead of counts, which undercounts when a sum repeats.
- **Three-and-one split** (`a+b+c` vs `d`): O(n³), which is still slow; the balanced 2+2
  split is what makes it O(n²).
- **C++:** `left[-(c + d)]` with `operator[]` inserts zero entries for every miss,
  doubling memory; use `find`.
- **Overflow:** sums of four values up to 2²⁸ fit in 32 bits only barely; use 64-bit.

## Going further

Meet in the middle is a general technique: it turns O(2ⁿ) subset-sum searches into
O(2^(n/2)) by enumerating each half and matching with hashing or sorting. Here the
"halves" are pairs of arrays.
"""),
    solution=_d(r"""
from collections import Counter

def four_sum_count(nums1, nums2, nums3, nums4):
    # Meet in the middle: a + b + c + d == 0  <=>  a + b == -(c + d).
    # Count every possible left half sum. Counts (not just presence) matter:
    # each distinct (i, j) pair is a different tuple.
    left = Counter(a + b for a in nums1 for b in nums2)
    total = 0
    for c in nums3:
        for d in nums4:
            # How many (i, j) pairs cancel this (k, l) pair? Counter returns 0
            # for missing keys without inserting them.
            total += left[-(c + d)]
    return total
"""),
    refs={
        "c": _d(r"""
            // Open-addressing hash map: pair sum -> how many (i, j) produce it (see the Two Sum C notes).
            static size_t mix64(long long k) {
                unsigned long long x = (unsigned long long)k;
                x ^= x >> 30; x *= 0xbf58476d1ce4e5b9ULL;
                x ^= x >> 27; x *= 0x94d049bb133111ebULL;
                return (size_t)(x ^ (x >> 31));
            }

            long long four_sum_count(long long* nums1, int nums1Size, long long* nums2, int nums2Size,
                                     long long* nums3, int nums3Size, long long* nums4, int nums4Size) {
                // Meet in the middle: n^2 sums of the left half go into the table, then each of the
                // n^2 right-half sums looks up its negation. O(n^2) instead of O(n^4).
                size_t pairs = (size_t)nums1Size * nums2Size;
                size_t cap = 4;
                while (cap < 2 * pairs) cap <<= 1;                 // load factor <= 0.5
                size_t mask = cap - 1;
                long long* keys = malloc(cap * sizeof(long long));
                long long* cnt = malloc(cap * sizeof(long long));
                bool* used = calloc(cap, sizeof(bool));

                for (int i = 0; i < nums1Size; i++)
                    for (int j = 0; j < nums2Size; j++) {
                        long long s = nums1[i] + nums2[j];
                        size_t h = mix64(s) & mask;
                        while (used[h] && keys[h] != s) h = (h + 1) & mask;    // probe
                        if (!used[h]) { used[h] = true; keys[h] = s; cnt[h] = 0; }
                        cnt[h]++;
                    }

                long long total = 0;
                for (int k = 0; k < nums3Size; k++)
                    for (int l = 0; l < nums4Size; l++) {
                        long long need = -(nums3[k] + nums4[l]);
                        size_t h = mix64(need) & mask;
                        while (used[h] && keys[h] != need) h = (h + 1) & mask;
                        if (used[h]) total += cnt[h];              // every matching left pair counts
                    }

                free(keys); free(cnt); free(used);
                return total;
            }
        """),
        "cpp": _d(r"""
            long long fourSumCount(vector<long long>& nums1, vector<long long>& nums2,
                                   vector<long long>& nums3, vector<long long>& nums4) {
                unordered_map<long long, long long> left;
                left.reserve(nums1.size() * nums2.size() * 2);
                for (long long a : nums1)
                    for (long long b : nums2) left[a + b]++;
                long long total = 0;
                for (long long c : nums3)
                    for (long long d : nums4) {
                        auto it = left.find(-(c + d));       // find: don't insert misses
                        if (it != left.end()) total += it->second;
                    }
                return total;
            }
        """),
        "rust": _d(r"""
            use std::collections::HashMap;

            pub fn four_sum_count(nums1: Vec<i64>, nums2: Vec<i64>, nums3: Vec<i64>, nums4: Vec<i64>) -> i64 {
                let mut left: HashMap<i64, i64> = HashMap::with_capacity(nums1.len() * nums2.len());
                for &a in &nums1 {
                    for &b in &nums2 {
                        *left.entry(a + b).or_insert(0) += 1;
                    }
                }
                let mut total = 0;
                for &c in &nums3 {
                    for &d in &nums4 {
                        total += left.get(&-(c + d)).copied().unwrap_or(0);
                    }
                }
                total
            }
        """),
    },
    tests=[
        [[1, 2], [-2, -1], [-1, 2], [0, 2]],
        [[0], [0], [0], [0]],
        [[1], [1], [1], [1]],
        [[0, 0], [0, 0], [0, 0], [0, 0]],
        [[-1, -1], [-1, 1], [-1, 1], [1, -1]],
        [[2**28, -(2**28)], [2**28, -(2**28)], [2**28, 0], [-(2**28), 0]],
        _fsc_case(_r, 10, -3, 3),
        _fsc_case(_r, 60, -50, 50),
        _fsc_case(_r, 200, -1000, 1000),
    ],
))

# ---------------------------------------------------------------------------- 12
def _lru_case(r, n_ops, key_range, cap):
    ops, args = [], []
    for _ in range(n_ops):
        if r.random() < 0.5:
            ops.append("get")
            args.append([r.randrange(key_range)])
        else:
            ops.append("put")
            args.append([r.randrange(key_range), r.randrange(1000)])
    return [cap, ops, args]


_r = random.Random(612)
PROBLEMS.append(dict(
    id="lru-cache-simulation",
    title="LRU Cache",
    difficulty=3,
    tags=["hash map", "linked list", "design"],
    fn="lru_cache",
    params=[["capacity", "int"], ["ops", "str[]"], ["args", "int[][]"]],
    returns="int[]",
    statement=_d(r"""
Design a **Least Recently Used (LRU) cache** holding at most `capacity` key–value pairs,
then run a sequence of operations on it.

- `get(key)`: if `key` is present, return its value and mark it as **most recently
  used**. Otherwise return `-1`.
- `put(key, value)`: if `key` is present, update its value and mark it most recently
  used; the result is `-1`. Otherwise insert it as most recently used; if that makes
  the cache exceed `capacity`, first **evict the least recently used** key. The result
  is the **evicted key**, or `-1` if nothing was evicted.

Both operations must run in **O(1)** average time.

**Input format.** `ops[i]` is `"get"` or `"put"`; `args[i]` is `[key]` for a get and
`[key, value]` for a put. Return the list of results, one per operation. (In a real
program you'd write a class with `get`/`put` methods; the function just drives it.)

Keys and values are non-negative integers.
"""),
    example_notes=[
        "Capacity 2. `get(1)` makes 1 recent, so `put(3)` evicts 2. Then `put(4)` evicts 1. Gets after that see 3 and 4 only.",
        "Capacity 1: every new key evicts the previous one; updating the same key evicts nothing.",
    ],
    constraints=["1 ≤ capacity ≤ 3000", "1 ≤ len(ops) ≤ 2·10⁴", "0 ≤ key ≤ 10⁴", "0 ≤ value ≤ 10⁵"],
    hints=[
        "A hash map gives O(1) lookup by key, but no notion of \"least recently used\". What structure keeps an order and lets you move any element to the front in O(1)?",
        "A **doubly linked list** ordered by recency: most recent at the head, least recent at the tail. Removing a node you hold a pointer to is O(1).",
        "Combine them: `key → node` in the hash map, nodes in the list. `get` = look up node, unlink it, relink at the head. Eviction = remove the tail node and delete its key from the map. Sentinel head/tail nodes remove edge cases. (Python's `OrderedDict` packages exactly this.)",
    ],
    explanation=_d(r"""
## Intuition

We need two things at once:

1. **Find by key** in O(1) → a hash map.
2. **Order by recency**, with "move this item to the front" and "remove the oldest" in
   O(1) → a doubly linked list.

Neither does both. Together they do: the map stores `key → pointer to list node`, and
the list keeps nodes from most to least recently used.

```
 map:  { 1: ●, 3: ●, 7: ● }
             |     |     |
             v     v     v
 HEAD <-> [7:70] <-> [1:10] <-> [3:30] <-> TAIL
          most recent              least recent (evicted next)
```

A **doubly** linked list matters: to unlink a node in O(1) you need its predecessor,
and a singly linked list would have to search for it.

**Sentinels.** Dummy `HEAD` and `TAIL` nodes mean every real node always has a
neighbour on both sides, so unlink/insert never special-case an empty list or the ends.

## Approach (class design)

```python
class Node:
    __slots__ = ("key", "val", "prev", "next")

class LRUCache:
    def __init__(self, capacity):
        self.cap, self.map = capacity, {}
        self.head, self.tail = Node(), Node()      # sentinels
        self.head.next, self.tail.prev = self.tail, self.head

    def _unlink(self, node):
        node.prev.next, node.next.prev = node.next, node.prev

    def _push_front(self, node):
        node.prev, node.next = self.head, self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        node = self.map.get(key)
        if node is None: return -1
        self._unlink(node); self._push_front(node)     # now most recent
        return node.val

    def put(self, key, val):
        if key in self.map:                            # update + refresh
            node = self.map[key]; node.val = val
            self._unlink(node); self._push_front(node)
            return -1
        evicted = -1
        if len(self.map) == self.cap:                  # full: drop the LRU node
            lru = self.tail.prev
            self._unlink(lru); del self.map[lru.key]
            evicted = lru.key
        node = Node(); node.key, node.val = key, val
        self.map[key] = node; self._push_front(node)
        return evicted
```

The node stores its **key** too: when we evict the tail node we must also delete it from
the map, and the node is the only place we can learn which key that is.

The reference solution below uses `collections.OrderedDict`, which is precisely a hash
map threaded through a doubly linked list: `move_to_end(key)` is "push to the
most-recent end" and `popitem(last=False)` removes the oldest.

Trace (capacity 2): `put(1,1)` `put(2,2)` `get(1)` `put(3,3)` `get(2)`:

```
put(1,1)  [1]            -> -1
put(2,2)  [2, 1]         -> -1
get(1)    [1, 2]         -> 1     (1 moves to the front)
put(3,3)  [3, 1]         -> 2     (evict tail = 2)
get(2)    [3, 1]         -> -1
```

## Complexity

- **Time:** O(1) average per operation: one hash lookup and a constant number of
  pointer updates.
- **Space:** O(capacity).

## Common mistakes

- **Evicting before checking for an update.** `put` on an existing key must never
  evict, even when the cache is full.
- **Forgetting to refresh recency on `get`** or on an update.
- **Not deleting the evicted key from the map**, leaving a dangling entry.
- **O(n) recency tracking:** a list/array with `remove(key)` or a timestamp scan for the
  minimum makes every eviction O(n).
- **C++:** `std::list::splice` moves a node to the front without invalidating
  iterators, so storing `list<...>::iterator` in the map is safe. **Rust:** a linked list
  with `Rc<RefCell<..>>` is painful; the idiomatic route is an index-based list inside a
  `Vec` (an "arena"), as in the reference.

## Going further

- **LFU cache** (least *frequently* used): a map of frequency → LRU list, plus the
  current minimum frequency, still O(1).
- Real caches (CPU caches, databases, CDNs) often use approximations like CLOCK or
  segmented LRU because strict LRU bookkeeping costs a pointer write on every hit.
- Python's `functools.lru_cache` decorator memoises a function with exactly this policy.
"""),
    solution=_d(r"""
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        # OrderedDict = hash map + doubly linked list in insertion order.
        # We keep it ordered from least recently used (front) to most recent (end).
        self.data = OrderedDict()

    def get(self, key):
        if key not in self.data:
            return -1
        # Reading counts as a use: move to the most-recent end in O(1).
        self.data.move_to_end(key)
        return self.data[key]

    def put(self, key, value):
        if key in self.data:
            # Update in place and refresh recency; an update never evicts.
            self.data[key] = value
            self.data.move_to_end(key)
            return -1
        evicted = -1
        if len(self.data) == self.capacity:
            # Full: the front of the order is the least recently used key.
            evicted, _ = self.data.popitem(last=False)
        self.data[key] = value  # new keys go to the most-recent end
        return evicted


def lru_cache(capacity, ops, args):
    # Drive the class with the scripted operations and collect each result.
    cache = LRUCache(capacity)
    out = []
    for op, a in zip(ops, args):
        if op == "get":
            out.append(cache.get(a[0]))
        else:
            out.append(cache.put(a[0], a[1]))
    return out
"""),
    refs={
        "c": _d(r"""
            // The classic design: a doubly linked list ordered by recency (head = most recent,
            // tail = least recent) plus a hash map key -> list node. Both give O(1) operations.
            // Nodes live in one array and link by index; -1 plays the role of NULL.
            typedef struct {
                long long key, val;
                int prev, next;      // recency list
                int hnext;           // next node in the same hash bucket (separate chaining)
            } Node;

            typedef struct {
                Node* nodes; int used;          // node pool; slots are recycled on eviction
                int* bucket; size_t mask;       // bucket[h] = first node index in chain h, or -1
                int head, tail, size;
                long long cap;
            } LRU;

            static size_t mix64(long long k) {
                unsigned long long x = (unsigned long long)k;
                x ^= x >> 30; x *= 0xbf58476d1ce4e5b9ULL;
                x ^= x >> 27; x *= 0x94d049bb133111ebULL;
                return (size_t)(x ^ (x >> 31));
            }

            static int find(LRU* c, long long key) {
                for (int i = c->bucket[mix64(key) & c->mask]; i >= 0; i = c->nodes[i].hnext)
                    if (c->nodes[i].key == key) return i;
                return -1;
            }

            static void unlink_node(LRU* c, int i) {           // remove i from the recency list
                Node* n = &c->nodes[i];
                if (n->prev >= 0) c->nodes[n->prev].next = n->next; else c->head = n->next;
                if (n->next >= 0) c->nodes[n->next].prev = n->prev; else c->tail = n->prev;
            }

            static void push_front(LRU* c, int i) {            // make i the most recent
                c->nodes[i].prev = -1;
                c->nodes[i].next = c->head;
                if (c->head >= 0) c->nodes[c->head].prev = i; else c->tail = i;
                c->head = i;
            }

            static void bucket_remove(LRU* c, int i) {          // unlink i from its hash chain
                int* p = &c->bucket[mix64(c->nodes[i].key) & c->mask];
                while (*p != i) p = &c->nodes[*p].hnext;
                *p = c->nodes[i].hnext;
            }

            static long long lru_get(LRU* c, long long key) {
                int i = find(c, key);
                if (i < 0) return -1;
                unlink_node(c, i); push_front(c, i);            // touched: now most recent
                return c->nodes[i].val;
            }

            static long long lru_put(LRU* c, long long key, long long val) {
                int i = find(c, key);
                if (i >= 0) {                                   // update in place
                    c->nodes[i].val = val;
                    unlink_node(c, i); push_front(c, i);
                    return -1;
                }
                long long evicted = -1;
                if (c->size == c->cap) {                        // full: drop the tail, reuse its slot
                    i = c->tail;
                    evicted = c->nodes[i].key;
                    unlink_node(c, i);
                    bucket_remove(c, i);
                    c->size--;
                } else {
                    i = c->used++;                              // fresh slot from the pool
                }
                c->nodes[i].key = key; c->nodes[i].val = val;
                size_t h = mix64(key) & c->mask;
                c->nodes[i].hnext = c->bucket[h];               // insert at the chain's head
                c->bucket[h] = i;
                push_front(c, i);
                c->size++;
                return evicted;
            }

            long long* lru_cache(long long capacity, char** ops, int opsSize, long long** args, int argsSize,
                                 int* argsColSize, int* returnSize) {
                (void)argsSize; (void)argsColSize;
                // The cache never holds more than min(capacity, #ops) entries, so size the pool to that.
                long long slots = capacity < opsSize ? capacity : opsSize;
                LRU c = { .used = 0, .head = -1, .tail = -1, .size = 0, .cap = capacity };
                c.nodes = malloc((slots + 1) * sizeof(Node));
                size_t nb = 4;
                while (nb < 2 * (size_t)(slots + 1)) nb <<= 1;
                c.mask = nb - 1;
                c.bucket = malloc(nb * sizeof(int));
                for (size_t b = 0; b < nb; b++) c.bucket[b] = -1;

                long long* out = malloc((opsSize ? opsSize : 1) * sizeof(long long));
                for (int i = 0; i < opsSize; i++)
                    out[i] = strcmp(ops[i], "get") == 0 ? lru_get(&c, args[i][0])
                                                        : lru_put(&c, args[i][0], args[i][1]);
                *returnSize = opsSize;
                free(c.nodes); free(c.bucket);
                return out;
            }
        """),
        "cpp": _d(r"""
            class LRUCache {
                size_t cap;
                list<pair<long long, long long>> items;   // (key, value); front = most recent
                unordered_map<long long, list<pair<long long, long long>>::iterator> pos;
            public:
                explicit LRUCache(size_t c) : cap(c) {}
                long long get(long long key) {
                    auto it = pos.find(key);
                    if (it == pos.end()) return -1;
                    items.splice(items.begin(), items, it->second);  // O(1) move to front
                    return it->second->second;
                }
                long long put(long long key, long long value) {
                    auto it = pos.find(key);
                    if (it != pos.end()) {
                        it->second->second = value;
                        items.splice(items.begin(), items, it->second);
                        return -1;
                    }
                    long long evicted = -1;
                    if (items.size() == cap) {                       // evict least recent (back)
                        evicted = items.back().first;
                        pos.erase(evicted);
                        items.pop_back();
                    }
                    items.emplace_front(key, value);
                    pos[key] = items.begin();
                    return evicted;
                }
            };

            vector<long long> lruCache(long long capacity, vector<string>& ops, vector<vector<long long>>& args) {
                LRUCache cache(capacity);
                vector<long long> out;
                for (size_t i = 0; i < ops.size(); i++)
                    out.push_back(ops[i] == "get" ? cache.get(args[i][0]) : cache.put(args[i][0], args[i][1]));
                return out;
            }
        """),
        "rust": _d(r"""
            use std::collections::HashMap;

            // Doubly linked list stored in a Vec ("arena"): links are indices, not pointers.
            // nodes[0] is the HEAD sentinel (most-recent side), nodes[1] the TAIL sentinel.
            struct Node { key: i64, val: i64, prev: usize, next: usize }

            struct Lru { cap: usize, map: HashMap<i64, usize>, nodes: Vec<Node> }

            impl Lru {
                fn new(cap: usize) -> Self {
                    let nodes = vec![
                        Node { key: 0, val: 0, prev: 0, next: 1 },
                        Node { key: 0, val: 0, prev: 0, next: 1 },
                    ];
                    Lru { cap, map: HashMap::new(), nodes }
                }
                fn unlink(&mut self, i: usize) {
                    let (p, n) = (self.nodes[i].prev, self.nodes[i].next);
                    self.nodes[p].next = n;
                    self.nodes[n].prev = p;
                }
                fn push_front(&mut self, i: usize) {
                    let first = self.nodes[0].next;
                    self.nodes[i].prev = 0;
                    self.nodes[i].next = first;
                    self.nodes[first].prev = i;
                    self.nodes[0].next = i;
                }
                fn get(&mut self, key: i64) -> i64 {
                    match self.map.get(&key).copied() {
                        Some(i) => {
                            self.unlink(i);
                            self.push_front(i);
                            self.nodes[i].val
                        }
                        None => -1,
                    }
                }
                fn put(&mut self, key: i64, val: i64) -> i64 {
                    if let Some(&i) = self.map.get(&key) {
                        self.nodes[i].val = val;
                        self.unlink(i);
                        self.push_front(i);
                        return -1;
                    }
                    let mut evicted = -1;
                    let idx = if self.map.len() == self.cap {
                        let lru = self.nodes[1].prev; // least recent real node
                        self.unlink(lru);
                        evicted = self.nodes[lru].key;
                        self.map.remove(&evicted);
                        self.nodes[lru].key = key; // recycle the slot
                        self.nodes[lru].val = val;
                        lru
                    } else {
                        self.nodes.push(Node { key, val, prev: 0, next: 0 });
                        self.nodes.len() - 1
                    };
                    self.map.insert(key, idx);
                    self.push_front(idx);
                    evicted
                }
            }

            pub fn lru_cache(capacity: i64, ops: Vec<String>, args: Vec<Vec<i64>>) -> Vec<i64> {
                let mut cache = Lru::new(capacity as usize);
                ops.iter()
                    .zip(args.iter())
                    .map(|(op, a)| if op == "get" { cache.get(a[0]) } else { cache.put(a[0], a[1]) })
                    .collect()
            }
        """),
    },
    tests=[
        [2, ["put", "put", "get", "put", "get", "put", "get", "get", "get"],
         [[1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]],
        [1, ["put", "put", "get", "get", "put", "put", "get"],
         [[1, 10], [2, 20], [1], [2], [2, 25], [3, 30], [2]]],
        [2, ["get", "put", "get"], [[5], [5, 0], [5]]],
        [2, ["put", "put", "put", "put", "get", "get"], [[2, 1], [1, 1], [2, 3], [4, 1], [1], [2]]],
        [3, ["put", "put", "put", "get", "put", "get", "get", "get", "get"],
         [[1, 1], [2, 2], [3, 3], [1], [4, 4], [2], [3], [1], [4]]],
        [2, ["put", "get", "put", "get", "get"], [[2, 1], [2], [3, 2], [2], [3]]],
        _lru_case(_r, 60, 8, 3),
        _lru_case(_r, 1500, 200, 50),
        _lru_case(_r, 1500, 5000, 400),
    ],
))
