# Python cheat sheet

Quick reference for solving Crucible problems in Python 3. Crucible's harness already
imports `math`, `typing`, `collections`, `functools`, `itertools`, `heapq`, `bisect`,
`re`, `string` and `random`, and raises the recursion limit to 20 000.

## How Crucible calls your function

You write one function with the exact name and parameters shown in the starter. The
harness converts each test's JSON into Python values, calls your function, and compares
the return value.

| Crucible type | Python type | notes |
|---|---|---|
| `int` | `int` | arbitrary precision: no overflow |
| `float` | `float` | 64-bit; compared with 1e-6 tolerance |
| `bool` | `bool` | |
| `str` | `str` | |
| `int[]` / `float[]` / `str[]` | `List[int]` … | a fresh list per test |
| `int[][]` | `List[List[int]]` | |
| `list` | `Optional[ListNode]` | `.val`, `.next`; `None` = empty |
| `tree` | `Optional[TreeNode]` | `.val`, `.left`, `.right` |
| `void` + mutates | return nothing | modify the list **in place** (`nums[:] = …`, `nums[i] = …`) |

`io` problems: read all of stdin, print the answer.

```python
import sys
data = sys.stdin.read().split()      # all whitespace-separated tokens
n = int(data[0])
nums = list(map(int, data[1:1 + n]))
print(sum(nums))
```

## Variables & types

```python
x = 42                 # int (unbounded)
y = 3.5                # float
ok = True              # bool (a subclass of int: True + True == 2)
s = "hi"               # str (immutable)
nothing = None
a, b = 1, 2            # tuple unpacking
a, b = b, a            # swap
INF = float("inf")     # handy sentinel; also math.inf
big = 10**18
type(x), isinstance(x, int)
int("42"), float("2.5"), str(7), bool(0)
```

## Operators

| op | meaning | example |
|---|---|---|
| `/` | true division, always float | `7 / 2 == 3.5` |
| `//` | floor division (rounds toward −∞) | `7 // 2 == 3`, `-7 // 2 == -4` |
| `%` | modulo, result has the **divisor's** sign | `-7 % 3 == 2` |
| `**` | power | `2 ** 10 == 1024`, `pow(2, 10, 1000)` = 24 (modular) |
| `divmod(a, b)` | `(a // b, a % b)` | `divmod(17, 5) == (3, 2)` |
| `& \| ^ ~ << >>` | bitwise | `~x == -x - 1` |
| `and or not` | logical, short-circuit | `x and y` returns a value, not just a bool |
| `==` / `is` | value equality / identity | use `is None` |
| `a < b < c` | chained comparison | |

C-style truncation toward zero: `int(a / b)` (small values) or
`q = abs(a) // abs(b); q = -q if (a < 0) != (b < 0) else q`.

## Conditionals

```python
x = 7
if x > 10:
    kind = "big"
elif x > 5:
    kind = "medium"
else:
    kind = "small"
label = "even" if x % 2 == 0 else "odd"     # ternary
match kind:                                  # 3.10+ structural match
    case "big" | "medium":
        pass
    case _:
        pass
```

## Loops

```python
nums = [5, 3, 8]
for i in range(len(nums)): pass        # 0 .. n-1
for i in range(10, 0, -2): pass        # 10, 8, 6, 4, 2
for x in nums: pass
for i, x in enumerate(nums): pass      # index + value
for a, b in zip([1, 2], "ab"): pass    # parallel iteration (stops at the shorter)
for x in reversed(nums): pass
i = 0
while i < 3:
    i += 1
    if i == 2:
        continue
else:
    pass          # runs if the loop wasn't broken out of
```

## Functions

```python
def add(a, b=0, *rest, **opts) -> int:     # default, varargs, kwargs
    return a + b + sum(rest)

square = lambda v: v * v

def make_counter():
    count = 0
    def inc():
        nonlocal count                     # rebind an enclosing variable
        count += 1
        return count
    return inc

from functools import lru_cache
@lru_cache(maxsize=None)                   # memoisation for recursive DP
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

Never use a mutable default (`def f(a=[])`): it's shared between calls.

## Strings

```python
s = "Hello, World"
len(s); s[0]; s[-1]; s[2:5]; s[::-1]          # index, slice, reverse
s.lower(); s.upper(); s.strip(); s.title()
s.split(", ")          # ['Hello', 'World']; .split() splits on any whitespace
"-".join(["a", "b"])   # 'a-b'
s.find("o"); s.index("o"); s.count("l")       # find returns -1 if missing
s.startswith("He"); "World" in s
s.replace("l", "L")
s.isdigit(); s.isalpha(); s.isalnum(); s.isspace()
ord("a"); chr(97)                             # 97, 'a'
f"{3.14159:.2f} {42:>5} {255:08b} {255:x}"    # formatting
chars = list(s); "".join(chars)               # strings are immutable: edit a list
```

Building a string in a loop: append to a list and `"".join(parts)` at the end (O(n)).

## Lists (arrays)

```python
a = [3, 1, 2]
grid = [[0] * 4 for _ in range(3)]   # 3x4. NOT [[0]*4]*3 (that shares rows!)
a.append(4); a.pop(); a.pop(0)        # pop(0) is O(n): use deque for queues
a.insert(0, 9); a.extend([5, 6]); a.remove(9)   # remove first occurrence
a[1:3]; a[::-1]; a[:]                 # slices are copies
a.sort(); a.sort(reverse=True)        # in place
b = sorted(a, key=lambda v: (-v, v))  # new list, custom key
a.reverse()
min(a); max(a); sum(a)
a.index(5); a.count(5); 5 in a        # O(n)
squares = [v * v for v in a if v > 2] # comprehension
total = sum(v for v in a)             # generator expression
pairs = sorted(zip([3, 1], "ab"))     # [(1, 'b'), (3, 'a')]
import bisect
pos = bisect.bisect_left(sorted(a), 5)  # binary search on a sorted list
```

## Dicts & sets

```python
from collections import defaultdict, Counter
d = {"a": 1}
d["b"] = 2; d.get("z", 0); "a" in d
del d["a"]; d.pop("b", None)
for k, v in d.items(): pass
groups = defaultdict(list); groups["x"].append(1)
cnt = Counter("banana")         # Counter({'a': 3, 'n': 2, 'b': 1})
cnt.most_common(1)              # [('a', 3)]
seen = set(); seen.add(3); seen.discard(4); 3 in seen
s1, s2 = {1, 2}, {2, 3}
s1 | s2; s1 & s2; s1 - s2; s1 ^ s2
key = tuple([1, 2])             # lists aren't hashable; tuples are
```

## Stacks, queues, deques, heaps

```python
from collections import deque
import heapq
stack = []; stack.append(1); top = stack[-1]; stack.pop()
q = deque([1, 2]); q.append(3); q.popleft(); q.appendleft(0)
window = deque(maxlen=3)        # keeps only the last 3 items
h = []
heapq.heappush(h, (2, "b")); heapq.heappush(h, (1, "a"))
heapq.heappop(h)                # (1, 'a'): min-heap
mx = []; heapq.heappush(mx, -5) # max-heap: push negatives, negate on pop
-heapq.heappop(mx)              # 5
h = [5, 1, 4]; heapq.heapify(h) # O(n)
heapq.nsmallest(2, [5, 1, 4])   # [1, 4]
```

## Classes

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
    def norm1(self) -> int:
        return abs(self.x) + abs(self.y)

class MinStack:
    def __init__(self):
        self.items = []
    def push(self, v):
        self.items.append(v)
```

## Linked lists & trees

```python
class ListNode:                         # already defined by the harness
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next

dummy = ListNode(0)                     # dummy head simplifies inserts
tail = dummy
for v in [1, 2, 3]:
    tail.next = ListNode(v)
    tail = tail.next
head = dummy.next

def depth(root):                        # TreeNode: .val .left .right
    return 0 if root is None else 1 + max(depth(root.left), depth(root.right))
```

## Common gotchas

- `[[0] * m] * n` creates n references to **one** row. Use a comprehension.
- `//` and `%` floor toward −∞; C, C++, Rust and ESPresso truncate toward 0.
- Integers never overflow, so you won't see the 32/64-bit wrap other languages hit.
- `nums = sorted(nums)` inside a function rebinds the local name; the caller's list is
  unchanged. For in-place problems use `nums.sort()` or `nums[:] = …`.
- Recursion is slow and limited; for depth > ~10⁴ use an explicit stack.
- `0.1 + 0.2 != 0.3`. Compare floats with `math.isclose` or a tolerance.
- `list.pop(0)` and `x in list` are O(n). Use a `deque` or a `set`.
- Iterating over a dict while adding or removing keys raises an error; iterate over `list(d)`.

## Complexity of common operations

| operation | cost |
|---|---|
| `list[i]`, `append`, `pop()` | O(1) |
| `insert(0, x)`, `pop(0)`, `x in list` | O(n) |
| `dict`/`set` get, set, `in` | O(1) average |
| `sort`, `sorted` | O(n log n), stable |
| `heappush` / `heappop` | O(log n) |
| `deque.append/popleft` | O(1) |
| slicing `a[i:j]` | O(j − i) (copies) |
