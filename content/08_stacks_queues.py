"""Track 8: Stacks, Queues & Sliding Window."""
import random
import string

TRACK = dict(
    id="stacks-queues",
    title="Stacks, Queues & Sliding Window",
    order=8,
    icon="☰",
    blurb="LIFO and FIFO in every language, then the two patterns they unlock: monotonic stacks and sliding windows.",
    intro=r"""
A **stack** and a **queue** are both "a list where you only touch the ends", and that
restriction is exactly what makes them powerful. Each operation is O(1), and the order
in which things come out tells you something about the problem's structure.

## LIFO and FIFO

```
STACK (last in, first out)          QUEUE (first in, first out)

   push 3 →  │ 3 │  ← pop           enqueue →  [ 1 | 2 | 3 ]  → dequeue
             │ 2 │                              back      front
             │ 1 │
             └───┘
```

- **Stack:** `push` onto the top, `pop` from the top, `peek`/`top` to look. Use it when
  the *most recent unfinished thing* must be handled first: matching brackets, undo,
  nested structures, depth-first search, function calls themselves.
- **Queue:** `push` at the back, `pop` from the front. Use it when things must be handled
  *in arrival order*: breadth-first search, scheduling, buffering a stream.
- **Deque** (double-ended queue): O(1) push and pop at **both** ends. It's both of the
  above, and the engine behind sliding-window maximum.

## Getting one in each language

| | stack | queue / deque |
|---|---|---|
| Python | `list`: `append`, `pop()`, `st[-1]` | `collections.deque`: `append`, `popleft`, `appendleft`, `pop` |
| C++ | `vector` (`push_back`, `pop_back`, `back`) or `std::stack` | `std::deque` (`push_back`, `pop_front`, `front`, `back`) or `std::queue` |
| Rust | `Vec` (`push`, `pop() -> Option`, `last()`) | `std::collections::VecDeque` (`push_back`, `pop_front`, `front`, `back`) |
| C | an array plus a `top` index | a circular array with `head` / `tail` indices |

Two traps worth memorising:

- **Python `list.pop(0)` is O(n)** (every other element shifts). Use `deque.popleft()`.
- In Rust, `pop()` and `last()` return `Option`. Pattern match or `unwrap` only when you
  *know* the stack is non-empty.

A stack in C is just an array and an integer:

```c
long long st[1000];
int top = 0;                 // number of elements; st[top-1] is the top
st[top++] = x;               // push
long long y = st[--top];     // pop
if (top > 0) { /* peek: st[top - 1] */ }
```

## Pattern 1: matching and nesting

Whenever input has **nested** structure (brackets, `3[a2[c]]`, directory paths with
`..`), a stack holds "the context I'll return to when the current level closes". Push on
open, pop on close; the stack depth equals the current nesting depth.

## Pattern 2: the monotonic stack

Question shape: *for each element, find the nearest element to the right (or left) that
is greater (or smaller).* Brute force checks every pair: O(n²). A **monotonic stack**
keeps indices of elements that are still *waiting* for their answer, in decreasing
order of value. When a new element arrives, it is the answer for every waiting element
smaller than it, so pop those and record.

Trace for "next greater element" on `[2, 1, 5, 3, 4]` (stack shows values, bottom→top):

| i | x | pops (answer = x) | stack after |
|---|---|---|---|
| 0 | 2 | | `[2]` |
| 1 | 1 | | `[2, 1]` |
| 2 | 5 | 1→5, 2→5 | `[5]` |
| 3 | 3 | | `[5, 3]` |
| 4 | 4 | 3→4 | `[5, 4]` |
| end | | 5, 4 have no greater → -1 | |

Result: `[5, 5, -1, 4, -1]`. Each index is pushed once and popped at most once, so the
total work is **O(n)** even though there's a loop inside a loop.

## Pattern 3: the sliding window

Question shape: *something about every contiguous subarray/substring of size k*, or *the
shortest/longest window satisfying a condition*. Instead of recomputing each window
from scratch (O(n·k)), slide it: add the element entering on the right, remove the one
leaving on the left.

Fixed size `k = 3` over `[1, 3, -1, -3, 5]`:

```
[1  3 -1] -3  5      sum = 3
 1 [3 -1 -3] 5       sum = 3 - 1 + (-3) = -1      (drop 1, add -3)
 1  3 [-1 -3  5]     sum = -1 - 3 + 5   = 1       (drop 3, add 5)
```

**Variable size** windows use two pointers: grow `right` until the window is valid,
then shrink `left` while it stays valid, recording the best. Both pointers only move
forward, so the total work is O(n).

```python
left = 0
for right, x in enumerate(s):
    add(x)
    while window_is_valid():
        record(left, right)
        remove(s[left]); left += 1
```

Some windows need more than a running sum. "Maximum of each window" needs a **monotonic
deque**: the front holds the current maximum, and elements that can never be a maximum
again are dropped from the back.

## Designing with stacks

Two problems here are *design* problems (Min Stack, Queue from Stacks), written as a
function that replays a list of operations and returns the outputs. The interesting part
is the class you'd write: what extra state makes each operation O(1) (or amortised
O(1))? **Amortised** means: one operation may occasionally be expensive, but any sequence
of m operations costs O(m) in total.
""",
)


def _nested_parens(r, n):
    out, st = [], []
    pairs = {"(": ")", "[": "]", "{": "}"}
    while len(out) < n:
        if st and (r.random() < 0.45 or len(out) + len(st) >= n):
            out.append(pairs[st.pop()])
        else:
            c = r.choice("([{")
            st.append(c)
            out.append(c)
    while st:
        out.append(pairs[st.pop()])
    return "".join(out)


_PR = random.Random(101)
_GOOD = _nested_parens(_PR, 2000)

VALID_PARENS = dict(
    id="valid-parentheses-stack",
    title="Valid Parentheses",
    difficulty=1,
    tags=["stack", "string", "matching"],
    fn="is_valid_parentheses",
    params=[["s", "str"]],
    returns="bool",
    statement="""`s` consists only of the characters `(`, `)`, `[`, `]`, `{`, `}`. Return `true` if
it is **balanced**:

- every opening bracket is closed by the same type of bracket,
- brackets close in the correct order (the most recently opened one closes first),
- every closing bracket has a matching opening bracket.

The empty string is balanced.""",
    constraints=["0 ≤ len(s) ≤ 10⁴"],
    hints=[
        "When you see a closing bracket, which opening bracket must it match? The first one? The most recent one that's still open?",
        "\"Most recent unclosed\" is exactly what a stack gives you. Push each opening bracket; on a closing bracket, the top of the stack must be its partner.",
        "Two more failure cases: a closing bracket when the stack is empty, and opening brackets left on the stack at the end.",
    ],
    explanation=r"""
## Intuition

In `{ [ ( ) ] }`, the `)` must match the `(` opened just before it, the *latest* bracket
still waiting. After it closes, the `[` becomes the latest again. "Latest still open"
is last-in-first-out: a **stack**.

## Approach

1. For each character `c`:
   - opening bracket → push it;
   - closing bracket → if the stack is empty or its top isn't the matching opener,
     return false; otherwise pop.
2. At the end, the string is valid exactly when the stack is empty.

Trace on `"{[()]}("`:

| char | action | stack |
|---|---|---|
| `{` | push | `{` |
| `[` | push | `{ [` |
| `(` | push | `{ [ (` |
| `)` | top `(` matches, pop | `{ [` |
| `]` | top `[` matches, pop | `{` |
| `}` | top `{` matches, pop | (empty) |
| `(` | push | `(` |
| end | stack not empty → **false** | |

A small lookup table `closer → opener` keeps the code tidy:

```python
match = {")": "(", "]": "[", "}": "{"}
```

**Language mechanics.** In Python, `st[-1]` reads the top without popping, and `if not
st` checks emptiness. In C, a `char` array with an integer `top` is a perfect stack, and
the string ends at the `'\0'` byte, so loop `for (i = 0; s[i]; i++)`. In C++,
`std::string` itself has `push_back`, `pop_back` and `back`, so it can serve as a stack of
chars. In Rust, iterate bytes with `s.bytes()` and use `Vec<u8>`; `st.pop() != Some(b'(')`
neatly handles both "empty" and "wrong type" in one comparison.

## Complexity

- **Time:** O(n): each character is pushed and popped at most once.
- **Space:** O(n) in the worst case (`"(((((("`).

## Common mistakes

- **Counting instead of stacking.** Three counters (one per type) accept `"([)]"`, which
  is invalid: the types interleave wrongly. Order matters, so you need a stack.
- **Popping an empty stack** on input like `")"`. Python raises `IndexError`; C reads
  `st[-1]`.
- **Forgetting the final emptiness check**: `"(("` has no mismatches but is unbalanced.
- **Odd length shortcut.** An odd-length string can't be valid; it's a nice early exit,
  but not a substitute for the real check.

## Going further

- With only one bracket type, a single counter suffices (it never goes negative, ends at
  0). That's the "stack depth" without the stack.
- **Minimum additions to make valid**, **longest valid parentheses** (stack of indices),
  and **remove invalid parentheses** (BFS) build on this.
""",
    solution='''def is_valid_parentheses(s):
    # Map each closer to the opener it must match.
    match = {")": "(", "]": "[", "}": "{"}
    st = []                     # opening brackets still waiting to be closed
    for c in s:
        if c in match:
            # A closer must match the MOST RECENT unclosed opener: the stack top.
            # An empty stack means there is nothing to close.
            if not st or st[-1] != match[c]:
                return False
            st.pop()
        else:
            st.append(c)
    # Anything left over was opened but never closed.
    return not st
''',
    refs={
        "c": '''bool is_valid_parentheses(char* s) {
    size_t n = strlen(s);
    char* st = malloc(n + 1);          // at most n openers can be waiting
    int top = 0;                       // st[top - 1] is the top
    bool ok = true;
    for (size_t i = 0; i < n && ok; i++) {
        char c = s[i];
        if (c == '(' || c == '[' || c == '{') {
            st[top++] = c;
        } else {
            char want = c == ')' ? '(' : c == ']' ? '[' : '{';
            if (top == 0 || st[top - 1] != want) ok = false;
            else top--;
        }
    }
    if (top != 0) ok = false;          // unclosed openers
    free(st);
    return ok;
}''',
        "cpp": '''bool isValidParentheses(string s) {
    string st;                         // std::string works fine as a char stack
    for (char c : s) {
        if (c == '(' || c == '[' || c == '{') { st.push_back(c); continue; }
        char want = c == ')' ? '(' : c == ']' ? '[' : '{';
        if (st.empty() || st.back() != want) return false;
        st.pop_back();
    }
    return st.empty();
}''',
        "rust": '''pub fn is_valid_parentheses(s: String) -> bool {
    let mut st: Vec<u8> = Vec::new();
    for c in s.bytes() {
        let want = match c {
            b')' => b'(',
            b']' => b'[',
            b'}' => b'{',
            _ => { st.push(c); continue; }
        };
        // pop() returns None on an empty stack, which also fails the comparison.
        if st.pop() != Some(want) {
            return false;
        }
    }
    st.is_empty()
}''',
    },
    tests=[
        ["()"], ["()[]{}"], ["(]"], ["([)]"], ["{[]}"], [""], ["("], [")"],
        ["(((("], ["){"], ["[({})]{}()"], [_GOOD], [_GOOD + "]"], [_GOOD[:-1]],
    ],
)


def _minstack_ops(seed, n):
    r = random.Random(seed)
    ops, vals, size = [], [], 0
    for _ in range(n):
        choice = r.random()
        if size == 0 or choice < 0.4:
            ops.append("push"); vals.append(r.randint(-1000, 1000)); size += 1
        elif choice < 0.6:
            ops.append("pop"); vals.append(0); size -= 1
        elif choice < 0.8:
            ops.append("top"); vals.append(0)
        else:
            ops.append("getMin"); vals.append(0)
    return [ops, vals]


MIN_STACK = dict(
    id="min-stack-design",
    title="Min Stack",
    difficulty=2,
    tags=["stack", "design"],
    fn="min_stack",
    params=[["ops", "str[]"], ["vals", "int[]"]],
    returns="int[]",
    statement="""Design a stack that supports, all in **O(1)** time:

- `push x`: push `x` onto the stack,
- `pop`: remove the top element,
- `top`: return the top element,
- `getMin`: return the minimum element currently in the stack.

You receive the operations as two parallel arrays: `ops[i]` is one of `"push"`, `"pop"`,
`"top"`, `"getMin"`, and `vals[i]` is the value for a `push` (it is `0` and should be
ignored for the other operations). Simulate them in order and return the results of
every `top` and `getMin`, in order. `pop`, `top` and `getMin` are only called on a
non-empty stack.""",
    constraints=["1 ≤ len(ops) ≤ 10⁴", "len(vals) == len(ops)", "-10⁹ ≤ vals[i] ≤ 10⁹"],
    hints=[
        "Pushing is easy to handle for the minimum: `min = min(min, x)`. The hard part is `pop`: if you pop the current minimum, what's the new minimum?",
        "The minimum after a pop is the minimum *at the time the element below was the top*. So remember the minimum for every stack level.",
        "Store pairs `(value, min_so_far)` on the stack, where `min_so_far = min(x, previous top's min_so_far)`. Then `getMin` is just the top pair's second field.",
    ],
    explanation=r"""
## Intuition

A single `current_min` variable breaks on `pop`: when the minimum leaves, you'd have to
scan the whole stack to find the next one. But a stack only ever *returns to an earlier
state*: after popping, the stack is exactly what it was before the matching push. So if
each level remembers "what was the minimum when I was the top?", popping restores the
old minimum for free.

## Approach

Each stack entry is a pair `(value, min_of_this_level_and_below)`:

| operation | stack (bottom → top) | getMin |
|---|---|---|
| push 5 | `(5,5)` | 5 |
| push 3 | `(5,5) (3,3)` | 3 |
| push 7 | `(5,5) (3,3) (7,3)` | 3 |
| push 2 | `(5,5) (3,3) (7,3) (2,2)` | 2 |
| pop | `(5,5) (3,3) (7,3)` | 3 ← restored automatically |
| pop | `(5,5) (3,3)` | 3 |
| pop | `(5,5)` | 5 |

The class you'd write:

```python
class MinStack:
    def __init__(self):
        self.st = []                  # (value, min up to here)
    def push(self, x):
        m = min(x, self.st[-1][1]) if self.st else x
        self.st.append((x, m))
    def pop(self):
        self.st.pop()
    def top(self):
        return self.st[-1][0]
    def get_min(self):
        return self.st[-1][1]
```

The function `min_stack(ops, vals)` just creates one instance, replays the operations,
and collects outputs, a common way to test a class with plain inputs and outputs.

**Space-saving variant:** keep a second stack that only receives `x` when
`x <= current minimum`, and pop it when the popped value equals its top. Use `<=`, not
`<`, so duplicate minimums are tracked: with `<`, pushing `2, 2` then popping once would
lose the minimum.

## Complexity

- **Time:** O(1) per operation. No loops anywhere.
- **Space:** O(n): one extra number per element (or fewer with the second-stack variant).

## Common mistakes

- **Recomputing the min on `pop`** by scanning: O(n) per pop.
- **Second-stack variant with `<`** loses duplicate minimums (see above).
- **Collecting outputs for `push`/`pop`.** Only `top` and `getMin` produce output here.
- **Rust:** `last()` returns `Option<&(i64, i64)>`; `.unwrap()` is fine because the
  problem guarantees non-empty, but in real code handle `None`.

## Going further

- **Max stack** with `popMax` needs more (a balanced tree or heap with lazy deletion).
- **Min queue**: build a queue from two min-stacks (see "Queue Using Two Stacks"); the
  minimum is the min of both stacks' minimums. That's an alternative way to solve
  sliding-window minimum.
- Store the *difference* `x - min` to use O(1) extra space total: a classic trick that
  needs care with overflow.
""",
    solution='''def min_stack(ops, vals):
    class MinStack:
        def __init__(self):
            # Each entry is (value, minimum of this entry and everything below it).
            # Popping an entry automatically "restores" the previous minimum,
            # because the entry below remembers it.
            self.st = []

        def push(self, x):
            m = min(x, self.st[-1][1]) if self.st else x
            self.st.append((x, m))

        def pop(self):
            self.st.pop()

        def top(self):
            return self.st[-1][0]

        def get_min(self):
            return self.st[-1][1]

    s = MinStack()
    out = []
    # Replay the operations; only top/getMin produce output.
    for op, v in zip(ops, vals):
        if op == "push":
            s.push(v)
        elif op == "pop":
            s.pop()
        elif op == "top":
            out.append(s.top())
        else:  # "getMin"
            out.append(s.get_min())
    return out
''',
    refs={
        "cpp": '''class MinStack {
    vector<pair<long long, long long>> st;   // (value, min so far)
public:
    void push(long long x) { st.push_back({x, st.empty() ? x : min(x, st.back().second)}); }
    void pop() { st.pop_back(); }
    long long top() const { return st.back().first; }
    long long getMin() const { return st.back().second; }
};

vector<long long> minStack(vector<string>& ops, vector<long long>& vals) {
    MinStack s;
    vector<long long> out;
    for (size_t i = 0; i < ops.size(); i++) {
        if (ops[i] == "push") s.push(vals[i]);
        else if (ops[i] == "pop") s.pop();
        else if (ops[i] == "top") out.push_back(s.top());
        else out.push_back(s.getMin());
    }
    return out;
}''',
        "rust": '''struct MinStack {
    st: Vec<(i64, i64)>, // (value, min so far)
}

impl MinStack {
    fn new() -> Self { MinStack { st: Vec::new() } }
    fn push(&mut self, x: i64) {
        let m = match self.st.last() {
            Some(&(_, m)) => m.min(x),
            None => x,
        };
        self.st.push((x, m));
    }
    fn pop(&mut self) { self.st.pop(); }
    fn top(&self) -> i64 { self.st.last().unwrap().0 }
    fn get_min(&self) -> i64 { self.st.last().unwrap().1 }
}

pub fn min_stack(ops: Vec<String>, vals: Vec<i64>) -> Vec<i64> {
    let mut s = MinStack::new();
    let mut out = Vec::new();
    for (op, &v) in ops.iter().zip(vals.iter()) {
        match op.as_str() {
            "push" => s.push(v),
            "pop" => s.pop(),
            "top" => out.push(s.top()),
            _ => out.push(s.get_min()),
        }
    }
    out
}''',
        "c": '''// Two parallel arrays act as a stack of (value, min-so-far) pairs.
long long* min_stack(char** ops, int opsSize, long long* vals, int valsSize, int* returnSize) {
    (void)valsSize;
    long long* val = malloc(sizeof(long long) * (opsSize + 1));
    long long* mn  = malloc(sizeof(long long) * (opsSize + 1));
    long long* out = malloc(sizeof(long long) * (opsSize + 1));
    int top = 0, k = 0;
    for (int i = 0; i < opsSize; i++) {
        if (strcmp(ops[i], "push") == 0) {
            long long x = vals[i];
            val[top] = x;
            mn[top] = (top > 0 && mn[top - 1] < x) ? mn[top - 1] : x;
            top++;
        } else if (strcmp(ops[i], "pop") == 0) {
            top--;
        } else if (strcmp(ops[i], "top") == 0) {
            out[k++] = val[top - 1];
        } else {
            out[k++] = mn[top - 1];
        }
    }
    free(val); free(mn);
    *returnSize = k;
    return out;
}''',
    },
    tests=[
        [["push", "push", "push", "getMin", "pop", "top", "getMin"], [-2, 0, -3, 0, 0, 0, 0]],
        [["push", "push", "push", "push", "getMin", "pop", "getMin", "pop", "getMin", "pop", "getMin"], [5, 3, 7, 2, 0, 0, 0, 0, 0, 0, 0]],
        [["push", "push", "getMin", "pop", "getMin"], [2, 2, 0, 0, 0]],
        [["push", "top", "getMin"], [42, 0, 0]],
        [["push", "push", "push", "getMin", "top"], [1, 2, 3, 0, 0]],
        [["push", "push", "push", "getMin", "pop", "getMin", "pop", "getMin"], [3, 2, 1, 0, 0, 0, 0, 0]],
        _minstack_ops(102, 800),
    ],
)


def _rpn_random(seed, n_ops):
    """Build a random RPN expression whose intermediate values stay small."""
    r = random.Random(seed)

    def trunc_div(a, b):
        q = abs(a) // abs(b)
        return q if (a >= 0) == (b > 0) else -q

    stack_toks, stack_vals = [], []
    tokens = []
    while n_ops > 0 or len(stack_vals) > 1:
        if len(stack_vals) < 2 or (n_ops > 0 and r.random() < 0.45):
            v = r.randint(-20, 20)
            tokens.append(str(v)); stack_vals.append(v)
            n_ops -= 1
            continue
        b = stack_vals.pop(); a = stack_vals.pop()
        ops = ["+", "-"]
        if abs(a * b) < 10**6:
            ops.append("*")
        if b != 0:
            ops.append("/")
        op = r.choice(ops)
        tokens.append(op)
        stack_vals.append({"+": a + b, "-": a - b, "*": a * b, "/": trunc_div(a, b) if b else 0}[op])
        assert abs(stack_vals[-1]) < 2**31
    return tokens


EVAL_RPN = dict(
    id="evaluate-rpn",
    title="Evaluate Reverse Polish Notation",
    difficulty=2,
    tags=["stack", "parsing"],
    fn="eval_rpn",
    params=[["tokens", "str[]"]],
    returns="int",
    statement="""Evaluate an arithmetic expression written in **Reverse Polish Notation** (postfix):
each operator comes *after* its two operands. `["2", "1", "+", "3", "*"]` means
`(2 + 1) * 3 = 9`.

Tokens are integers (possibly negative, like `"-11"`) or one of `+ - * /`. Division
between integers **truncates toward zero** (`7 / -2 = -3`). The expression is always
valid, there is no division by zero, and every intermediate result fits in a 32-bit
signed integer.""",
    constraints=["1 ≤ len(tokens) ≤ 10⁴", "the answer and all intermediate values fit in 32 bits"],
    hints=[
        "Read the tokens left to right. When you reach an operator, which two numbers does it apply to?",
        "Push numbers onto a stack. On an operator, pop **b** (the top) and then **a**, and push `a op b`. Order matters for `-` and `/`.",
        "Careful with `/`: Python's `//` floors (`-7 // 2 == -4`), but the problem wants truncation (`-3`). `int(a / b)` works for these sizes; a pure-integer version uses `abs` and fixes the sign.",
    ],
    explanation=r"""
## Intuition

Postfix notation was designed for stacks: no parentheses, no precedence rules. An
operator always applies to the **two most recent values not yet consumed**, which are
exactly the top two items of a stack. Old HP calculators and the JVM bytecode work this
way.

## Approach

```
for tok in tokens:
    if tok is an operator:
        b = pop(); a = pop()     # b was pushed last → right operand
        push(a op b)
    else:
        push(int(tok))
return pop()
```

Trace on `["4", "13", "5", "/", "+"]` (which is `4 + 13 / 5`):

| token | action | stack |
|---|---|---|
| 4 | push | `4` |
| 13 | push | `4 13` |
| 5 | push | `4 13 5` |
| / | b=5, a=13, push 13/5 = 2 | `4 2` |
| + | b=2, a=4, push 6 | `6` |

**Telling numbers from operators.** `"-"` is an operator but `"-11"` is a number. Test
"is the token exactly one of `+ - * /`?" rather than "does it start with `-`?".

**Truncating division.** C, C++, Rust and Java truncate toward zero natively. Python's
`//` floors. Two safe options in Python:

```python
int(a / b)                 # float division then truncate; fine for 32-bit values
q = abs(a) // abs(b)       # exact for any size
q = q if (a >= 0) == (b > 0) else -q
```

## Complexity

- **Time:** O(n): each token is pushed/popped a constant number of times.
- **Space:** O(n) for the stack.

## Common mistakes

- **Operand order:** popping `a` first gives `b - a` instead of `a - b`.
- **Floor vs truncate** in Python (see above): `["-7", "2", "/"]` must give `-3`.
- **Detecting negatives as operators** with `tok[0] == '-'`.
- **C:** `atoll` parses `"-11"` correctly; comparing strings needs `strcmp`, not `==`.

## Going further

- **Shunting-yard** (Dijkstra) converts infix `3 + 4 * 2` to postfix with an operator
  stack, honoring precedence and parentheses. Combined with this problem it's a complete
  calculator.
- **Basic Calculator I/II/III** (LeetCode 224/227/772) evaluate infix directly with one
  or two stacks.
""",
    solution='''def eval_rpn(tokens):
    def trunc_div(a, b):
        # Python's // floors toward -infinity; the problem wants truncation toward 0.
        q = abs(a) // abs(b)
        return q if (a >= 0) == (b > 0) else -q

    st = []
    for tok in tokens:
        # Compare against the full operator set: "-11" is a number, "-" is an operator.
        if tok in ("+", "-", "*", "/"):
            b = st.pop()        # right operand was pushed last
            a = st.pop()
            if tok == "+":
                st.append(a + b)
            elif tok == "-":
                st.append(a - b)
            elif tok == "*":
                st.append(a * b)
            else:
                st.append(trunc_div(a, b))
        else:
            st.append(int(tok))
    # A valid expression leaves exactly one value.
    return st[-1]
''',
    refs={
        "c": '''long long eval_rpn(char** tokens, int tokensSize) {
    long long* st = malloc(sizeof(long long) * (tokensSize + 1));
    int top = 0;
    for (int i = 0; i < tokensSize; i++) {
        char* t = tokens[i];
        // An operator is a single character from "+-*/"; "-11" has length 3.
        if (t[1] == '\\0' && strchr("+-*/", t[0])) {
            long long b = st[--top], a = st[--top];
            switch (t[0]) {
                case '+': st[top++] = a + b; break;
                case '-': st[top++] = a - b; break;
                case '*': st[top++] = a * b; break;
                default:  st[top++] = a / b; break;   // C truncates toward zero
            }
        } else {
            st[top++] = atoll(t);
        }
    }
    long long ans = st[top - 1];
    free(st);
    return ans;
}''',
        "cpp": '''long long evalRpn(vector<string>& tokens) {
    vector<long long> st;
    for (const string& t : tokens) {
        if (t == "+" || t == "-" || t == "*" || t == "/") {
            long long b = st.back(); st.pop_back();
            long long a = st.back(); st.pop_back();
            if (t == "+") st.push_back(a + b);
            else if (t == "-") st.push_back(a - b);
            else if (t == "*") st.push_back(a * b);
            else st.push_back(a / b);            // truncates toward zero
        } else {
            st.push_back(stoll(t));
        }
    }
    return st.back();
}''',
        "rust": '''pub fn eval_rpn(tokens: Vec<String>) -> i64 {
    let mut st: Vec<i64> = Vec::new();
    for t in &tokens {
        match t.as_str() {
            "+" | "-" | "*" | "/" => {
                let b = st.pop().unwrap();
                let a = st.pop().unwrap();
                st.push(match t.as_str() {
                    "+" => a + b,
                    "-" => a - b,
                    "*" => a * b,
                    _ => a / b, // integer division truncates toward zero in Rust
                });
            }
            num => st.push(num.parse().unwrap()),
        }
    }
    st[0]
}''',
    },
    tests=[
        [["2", "1", "+", "3", "*"]],
        [["4", "13", "5", "/", "+"]],
        [["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]],
        [["42"]],
        [["-7", "2", "/"]],
        [["7", "-2", "/"]],
        [["3", "-4", "-"]],
        [["0", "5", "/"]],
        [_rpn_random(103, 40)],
        [_rpn_random(104, 600)],
    ],
)


def _temps(seed, n):
    r = random.Random(seed)
    return [r.randint(30, 100) for _ in range(n)]


DAILY_TEMPS = dict(
    id="daily-temperatures",
    title="Daily Temperatures",
    difficulty=2,
    tags=["stack", "monotonic stack"],
    fn="daily_temperatures",
    params=[["temperatures", "int[]"]],
    returns="int[]",
    statement="""Given daily temperatures, return an array `answer` where `answer[i]` is the number of
days you have to wait after day `i` to get a **strictly warmer** temperature. If no
future day is warmer, `answer[i] = 0`.

An O(n²) scan will time out on the largest tests; aim for O(n).""",
    constraints=["1 ≤ len(temperatures) ≤ 10⁵", "30 ≤ temperatures[i] ≤ 100"],
    hints=[
        "Brute force: for each day, scan forward until a warmer day. Which days get scanned over and over?",
        "Keep a stack of *indices of days still waiting* for a warmer day. Their temperatures are non-increasing from bottom to top. Why?",
        "When day `i` arrives, pop every waiting day `j` with `temperatures[j] < temperatures[i]` and set `answer[j] = i - j`. Then push `i`.",
    ],
    explanation=r"""
## Intuition

"For each element, the next element to the right that is greater": the textbook
**monotonic stack** question. Days that haven't found a warmer day yet form a queue of
"waiting" days, and the waiting days are always in **non-increasing** temperature order:
if a warmer day had arrived after a cooler one, it would have resolved it. So the coolest
waiting day is on top, and a new day resolves waiting days from the top down until it
hits one at least as warm.

## Approach

```
answer = [0] * n
stack = []                          # indices, temperatures non-increasing
for i, t in enumerate(temps):
    while stack and temps[stack[-1]] < t:
        j = stack.pop()
        answer[j] = i - j           # day i is j's first warmer day
    stack.append(i)
# indices left on the stack never got a warmer day: answer stays 0
```

Trace on `[73, 74, 75, 71, 69, 72, 76, 73]`:

| i | t | popped (answer) | stack (temps) |
|---|---|---|---|
| 0 | 73 | | `73` |
| 1 | 74 | 0 → 1 | `74` |
| 2 | 75 | 1 → 1 | `75` |
| 3 | 71 | | `75 71` |
| 4 | 69 | | `75 71 69` |
| 5 | 72 | 4 → 1, 3 → 2 | `75 72` |
| 6 | 76 | 5 → 1, 2 → 4 | `76` |
| 7 | 73 | | `76 73` |

Answer: `[1, 1, 4, 2, 1, 1, 0, 0]`.

**Store indices, not temperatures.** You need the index to compute the distance, and
the index lets you look up the temperature anyway.

## Complexity

- **Time:** O(n). The `while` loop looks nested, but every index is pushed exactly once
  and popped at most once, so the total number of pops across the whole run is ≤ n.
  This "count the total work, not the per-iteration work" argument is called
  **amortised analysis**.
- **Space:** O(n) for the stack (a strictly decreasing input keeps everything).

## Common mistakes

- **`<=` instead of `<`** pops days of *equal* temperature, but equal isn't warmer.
- **Pushing temperatures** instead of indices, then having no way to compute `i - j`.
- **Forgetting the default 0** for days left on the stack (C: initialise the output
  array; `malloc` doesn't zero it).

## Going further

- **Backward variant:** iterate right-to-left keeping a stack of candidate warmer days;
  pop everything `<=` the current day, and the top (if any) is the answer.
- With temperatures limited to 30..100, there's also an O(n·71) approach: scan backwards
  remembering the next index of each temperature value.
- **Stock span** (consecutive previous days with price ≤ today) is the same pattern
  facing left.
""",
    solution='''def daily_temperatures(temperatures):
    n = len(temperatures)
    answer = [0] * n           # default 0: "no warmer day ever comes"
    # Indices of days still waiting for a warmer day. Their temperatures are
    # non-increasing from bottom to top, so the coolest waiting day is on top.
    stack = []
    for i, t in enumerate(temperatures):
        # Day i resolves every waiting day that is strictly cooler.
        # Each index is popped at most once overall, so this is O(n) in total.
        while stack and temperatures[stack[-1]] < t:
            j = stack.pop()
            answer[j] = i - j
        stack.append(i)
    return answer
''',
    refs={
        "c": '''long long* daily_temperatures(long long* temperatures, int temperaturesSize, int* returnSize) {
    int n = temperaturesSize;
    long long* ans = calloc(n > 0 ? n : 1, sizeof(long long));   // zero = no warmer day
    int* st = malloc(sizeof(int) * (n > 0 ? n : 1));             // stack of indices
    int top = 0;
    for (int i = 0; i < n; i++) {
        while (top > 0 && temperatures[st[top - 1]] < temperatures[i]) {
            int j = st[--top];
            ans[j] = i - j;
        }
        st[top++] = i;
    }
    free(st);
    *returnSize = n;
    return ans;
}''',
        "cpp": '''vector<long long> dailyTemperatures(vector<long long>& temperatures) {
    int n = temperatures.size();
    vector<long long> ans(n, 0);
    vector<int> st;                       // indices; temps non-increasing
    for (int i = 0; i < n; i++) {
        while (!st.empty() && temperatures[st.back()] < temperatures[i]) {
            ans[st.back()] = i - st.back();
            st.pop_back();
        }
        st.push_back(i);
    }
    return ans;
}''',
        "rust": '''pub fn daily_temperatures(temperatures: Vec<i64>) -> Vec<i64> {
    let n = temperatures.len();
    let mut ans = vec![0i64; n];
    let mut st: Vec<usize> = Vec::new();
    for i in 0..n {
        // while-let pops as long as the top is strictly cooler than today
        while let Some(&j) = st.last() {
            if temperatures[j] >= temperatures[i] {
                break;
            }
            st.pop();
            ans[j] = (i - j) as i64;
        }
        st.push(i);
    }
    ans
}''',
    },
    tests=[
        [[73, 74, 75, 71, 69, 72, 76, 73]],
        [[30, 40, 50, 60]],
        [[30, 60, 90]],
        [[50]],
        [[100, 90, 80, 70]],
        [[70, 70, 70, 71]],
        [_temps(105, 200)],
        [list(range(100, 30, -1)) * 30 + [100]],
        [_temps(106, 4000)],
    ],
)


def _ng_rand(seed, n, lo, hi):
    r = random.Random(seed)
    return [r.randint(lo, hi) for _ in range(n)]


NEXT_GREATER = dict(
    id="next-greater-element-circular",
    title="Next Greater Element (Circular)",
    difficulty=2,
    tags=["stack", "monotonic stack", "circular array"],
    fn="next_greater_circular",
    params=[["nums", "int[]"]],
    returns="int[]",
    statement="""`nums` is a **circular** array: after the last element comes the first one again.

For each index `i`, return the first value **strictly greater** than `nums[i]` that you
meet walking forward from `i` (wrapping around past the end). If no such value exists,
use `-1`.""",
    constraints=["1 ≤ len(nums) ≤ 10⁴", "-10⁹ ≤ nums[i] ≤ 10⁹"],
    hints=[
        "First solve the non-circular version with a monotonic stack: a stack of indices still waiting for a greater value.",
        "Circularity means an element near the end may find its answer near the beginning. What if you walked the array twice?",
        "Loop `i` from `0` to `2n - 1` and use `nums[i % n]`. Resolve waiting indices as usual, but only *push* indices during the first lap.",
    ],
    explanation=r"""
## Intuition

Without wrap-around this is the plain monotonic-stack pattern from the intro. With
wrap-around, an element near the end can be answered by something at the start. The
cleanest trick: **pretend the array is written twice**, `nums + nums`. Walking forward
from any `i` for up to `n − 1` steps in the circle is the same as walking forward in the
doubled array, so a second lap gives every waiting element the chance to see the
elements before it.

## Approach

```
ans = [-1] * n
stack = []                         # indices waiting for a greater value
for i in range(2 * n):
    x = nums[i % n]
    while stack and nums[stack[-1]] < x:
        ans[stack.pop()] = x
    if i < n:
        stack.append(i)            # second lap only resolves, never adds
```

Trace on `[1, 2, 1]` (n = 3):

| i | i % n | x | resolved | stack (indices) |
|---|---|---|---|---|
| 0 | 0 | 1 | | `0` |
| 1 | 1 | 2 | 0 → 2 | `1` |
| 2 | 2 | 1 | | `1 2` |
| 3 | 0 | 1 | | `1 2` |
| 4 | 1 | 2 | 2 → 2 | `1` |
| 5 | 2 | 1 | | `1` |

Index 1 (value 2) is the maximum, so nothing is ever greater: `-1`. Result `[2, -1, 2]`.

Why push only in the first lap? Every index already got pushed once; pushing again
would duplicate entries (harmless for correctness but wasteful).

**Language mechanics.** `%` (remainder) maps a growing index back into `0..n-1`. In C,
C++, and Rust `%` on a negative left operand gives a negative result, but `i` here is
never negative, so it's safe.

## Complexity

- **Time:** O(n): 2n iterations, each index pushed once and popped at most once.
- **Space:** O(n).

## Common mistakes

- **Only one lap**: elements near the end that are answered by early elements stay `-1`.
- **More than two laps**: unnecessary; one extra lap covers every distance up to n − 1.
- **`<=` when popping**: equal is not greater (`[5, 5]` → `[-1, -1]`).
- **Writing indices instead of values** into the answer. This problem wants the value.

## Going further

- Return the *distance* instead of the value (like Daily Temperatures, but circular):
  record `(i - j) mod n` when popping.
- **Next Greater Element I** (LeetCode 496) asks the question for a subset of values,
  answered by mapping value → next greater with one stack pass and a hash map.
""",
    solution='''def next_greater_circular(nums):
    n = len(nums)
    ans = [-1] * n            # default: nothing greater anywhere in the circle
    stack = []                # indices waiting for a strictly greater value
    # Two laps over the array simulate walking around the circle: any index can
    # see every other element within the second lap.
    for i in range(2 * n):
        x = nums[i % n]
        while stack and nums[stack[-1]] < x:
            ans[stack.pop()] = x
        if i < n:
            # Each index enters the stack once, during the first lap.
            stack.append(i)
    return ans
''',
    refs={
        "cpp": '''vector<long long> nextGreaterCircular(vector<long long>& nums) {
    int n = nums.size();
    vector<long long> ans(n, -1);
    vector<int> st;
    for (int i = 0; i < 2 * n; i++) {
        long long x = nums[i % n];
        while (!st.empty() && nums[st.back()] < x) {
            ans[st.back()] = x;
            st.pop_back();
        }
        if (i < n) st.push_back(i);
    }
    return ans;
}''',
        "rust": '''pub fn next_greater_circular(nums: Vec<i64>) -> Vec<i64> {
    let n = nums.len();
    let mut ans = vec![-1i64; n];
    let mut st: Vec<usize> = Vec::new();
    for i in 0..2 * n {
        let x = nums[i % n];
        while let Some(&j) = st.last() {
            if nums[j] >= x {
                break;
            }
            ans[j] = x;
            st.pop();
        }
        if i < n {
            st.push(i);
        }
    }
    ans
}''',
        "c": '''long long* next_greater_circular(long long* nums, int numsSize, int* returnSize) {
    int n = numsSize;
    long long* ans = malloc(sizeof(long long) * n);
    int* st = malloc(sizeof(int) * n);
    int top = 0;
    for (int i = 0; i < n; i++) ans[i] = -1;
    for (int i = 0; i < 2 * n; i++) {
        long long x = nums[i % n];
        while (top > 0 && nums[st[top - 1]] < x) ans[st[--top]] = x;
        if (i < n) st[top++] = i;
    }
    free(st);
    *returnSize = n;
    return ans;
}''',
    },
    tests=[
        [[1, 2, 1]],
        [[1, 2, 3, 4, 3]],
        [[7]],
        [[5, 5, 5]],
        [[5, 4, 3, 2, 1]],
        [[-1, -2, -3, 0]],
        [[3, 8, 4, 1, 2]],
        [_ng_rand(107, 300, -50, 50)],
        [_ng_rand(108, 3000, -10**9, 10**9)],
    ],
)


def _hist(seed, n, hi):
    r = random.Random(seed)
    return [r.randint(0, hi) for _ in range(n)]


LARGEST_RECT = dict(
    id="largest-rectangle-histogram",
    title="Largest Rectangle in Histogram",
    difficulty=3,
    tags=["stack", "monotonic stack"],
    fn="largest_rectangle_area",
    params=[["heights", "int[]"]],
    returns="int",
    espresso=False,
    statement="""`heights[i]` is the height of bar `i` in a histogram where every bar has width 1.
Return the area of the **largest rectangle** that fits entirely inside the histogram
(axis-aligned, spanning one or more adjacent bars, as tall as the shortest bar it spans).

The largest tests have thousands of bars, so aim for O(n) rather than O(n²).""",
    constraints=["1 ≤ len(heights) ≤ 3·10⁴", "0 ≤ heights[i] ≤ 10⁴"],
    hints=[
        "Every candidate rectangle is limited by its *shortest* bar. Flip it around: for each bar `i`, what's the widest rectangle whose height is exactly `heights[i]`?",
        "That rectangle extends left and right until it meets a bar **shorter** than `heights[i]`. So you need, for each bar, the nearest shorter bar on each side: a monotonic-stack job.",
        "Keep a stack of indices with increasing heights. When bar `i` is shorter than the top, pop the top `t`: its right limit is `i`, its left limit is the new top (or -1). Area = `heights[t] * (i - left - 1)`.",
        "Append a sentinel bar of height 0 at the end so every remaining bar gets popped and measured.",
    ],
    explanation=r"""
## Intuition

Brute force tries every pair `(l, r)`: O(n²) pairs (O(n³) if you recompute minima). The
key reframing: the optimal rectangle has *some* bar as its shortest bar, and given that
bar `i`, the best rectangle of height `heights[i]` stretches as far as possible in both
directions, stopping at the first strictly shorter bar on each side.

```
heights:  2  1  5  6  2  3
                ┌──┐
             ┌──┤  │
             │  │  │     ┌──┐
          ┌──┤  │  ├──┬──┤  │
          │  │  │  │  │  │  │
          ├──┼──┼──┼──┼──┼──┤
idx:        0  1  2  3  4  5
bar 2 (h=5): shorter on the left at 1, on the right at 4 → width 4-1-1 = 2 → area 10
```

So we need **previous smaller** and **next smaller** for every bar, both of which a
monotonic stack provides in one pass.

## Approach

Keep a stack of indices whose heights are **strictly increasing** bottom to top. Process
bars left to right, plus a sentinel height 0 at position `n`:

```
for i in 0..n (inclusive, h = 0 at i == n):
    while stack and heights[stack.top] >= h:
        t = pop()
        left = stack.top if stack else -1      # previous smaller bar
        width = i - left - 1                   # i is the next smaller bar
        best = max(best, heights[t] * width)
    push(i)
```

When `t` is popped, `i` is the first bar to its right that's not taller (the right wall),
and the element now below it on the stack is the last bar to its left that's shorter (the
left wall); everything in between is at least as tall as `heights[t]`.

Trace on `[2, 1, 5, 6, 2, 3]`:

| i | h | popped t (h_t) | left | width | area | stack after |
|---|---|---|---|---|---|---|
| 0 | 2 | | | | | `0` |
| 1 | 1 | 0 (2) | -1 | 1 | 2 | `1` |
| 2 | 5 | | | | | `1 2` |
| 3 | 6 | | | | | `1 2 3` |
| 4 | 2 | 3 (6) | 2 | 1 | 6 | |
| | | 2 (5) | 1 | 2 | **10** | `1 4` |
| 5 | 3 | | | | | `1 4 5` |
| 6 | 0 | 5 (3) | 4 | 1 | 3 | |
| | | 4 (2) | 1 | 4 | 8 | |
| | | 1 (1) | -1 | 6 | 6 | `6` |

Best = 10.

**Equal heights.** Popping on `>=` means that among equal bars, the earlier one gets
measured with a too-short width, but the *last* one of the run gets the full width, so
the maximum is still found.

## Complexity

- **Time:** O(n): each index is pushed and popped once.
- **Space:** O(n) for the stack.
- Areas reach 10⁴ · 3·10⁴ = 3·10⁸, which fits in 32 bits, but use 64-bit anyway.

## Common mistakes

- **Forgetting the sentinel**: bars left on the stack at the end (an increasing
  histogram!) never get measured. Either append a 0 or drain the stack afterwards with
  right wall `n`.
- **Width off by one**: the walls are *exclusive*, so the width is `i - left - 1`.
- **Using the popped bar's own index as the left wall**: the left wall is the *new* top
  after popping.
- **Mutating the input** to add the sentinel in C/C++/Rust: fine if allowed, but
  handling `i == n` with `h = 0` is cleaner.

## Going further

- **Maximal rectangle in a binary matrix**: build histogram heights row by row (count of
  consecutive 1s above) and run this algorithm on each row: O(rows · cols).
- **Divide and conquer** (split at the minimum bar) is O(n log n) with a segment tree,
  a good exercise in comparing approaches.
""",
    solution='''def largest_rectangle_area(heights):
    # Stack of indices with strictly increasing heights. For any index in it, the
    # element below is its nearest shorter bar to the left.
    stack = []
    best = 0
    n = len(heights)
    for i in range(n + 1):
        # A sentinel bar of height 0 at position n forces every bar to be popped.
        h = heights[i] if i < n else 0
        # Bar i is the first bar to the right of the top that's not taller, so it
        # is the right wall for every taller bar we pop.
        while stack and heights[stack[-1]] >= h:
            t = stack.pop()
            left = stack[-1] if stack else -1      # nearest shorter bar on the left
            width = i - left - 1                   # walls are exclusive
            best = max(best, heights[t] * width)
        stack.append(i)
    return best
''',
    refs={
        "c": '''long long largest_rectangle_area(long long* heights, int heightsSize) {
    int n = heightsSize;
    int* st = malloc(sizeof(int) * (n + 1));
    int top = 0;
    long long best = 0;
    for (int i = 0; i <= n; i++) {
        long long h = (i < n) ? heights[i] : 0;    // sentinel
        while (top > 0 && heights[st[top - 1]] >= h) {
            int t = st[--top];
            int left = top > 0 ? st[top - 1] : -1;
            long long area = heights[t] * (long long)(i - left - 1);
            if (area > best) best = area;
        }
        st[top++] = i;
    }
    free(st);
    return best;
}''',
        "cpp": '''long long largestRectangleArea(vector<long long>& heights) {
    int n = heights.size();
    vector<int> st;
    long long best = 0;
    for (int i = 0; i <= n; i++) {
        long long h = i < n ? heights[i] : 0;
        while (!st.empty() && heights[st.back()] >= h) {
            int t = st.back(); st.pop_back();
            int left = st.empty() ? -1 : st.back();
            best = max(best, heights[t] * (i - left - 1));
        }
        st.push_back(i);
    }
    return best;
}''',
        "rust": '''pub fn largest_rectangle_area(heights: Vec<i64>) -> i64 {
    let n = heights.len();
    let mut st: Vec<usize> = Vec::new();
    let mut best = 0i64;
    for i in 0..=n {
        let h = if i < n { heights[i] } else { 0 };
        while let Some(&t) = st.last() {
            if heights[t] < h {
                break;
            }
            st.pop();
            // Use i64 for the left wall so "no wall" can be -1.
            let left = st.last().map(|&l| l as i64).unwrap_or(-1);
            best = best.max(heights[t] * (i as i64 - left - 1));
        }
        st.push(i);
    }
    best
}''',
    },
    tests=[
        [[2, 1, 5, 6, 2, 3]],
        [[2, 4]],
        [[0]],
        [[7]],
        [[3, 3, 3, 3]],
        [[1, 2, 3, 4, 5]],
        [[5, 4, 3, 2, 1]],
        [[0, 0, 9, 0, 0]],
        [_hist(109, 100, 20)],
        [_hist(110, 4000, 10**4)],
        [list(range(1, 4001))],
    ],
)


def _queue_ops(seed, n):
    r = random.Random(seed)
    ops, vals, size = [], [], 0
    for _ in range(n):
        c = r.random()
        if size == 0 and c >= 0.85:
            ops.append("empty"); vals.append(0)
        elif size == 0 or c < 0.4:
            ops.append("push"); vals.append(r.randint(1, 1000)); size += 1
        elif c < 0.65:
            ops.append("pop"); vals.append(0); size -= 1
        elif c < 0.85:
            ops.append("peek"); vals.append(0)
        else:
            ops.append("empty"); vals.append(0)
    return [ops, vals]


QUEUE_STACKS = dict(
    id="queue-using-two-stacks",
    title="Implement Queue Using Stacks",
    difficulty=1,
    tags=["stack", "queue", "design", "amortized"],
    fn="queue_via_stacks",
    params=[["ops", "str[]"], ["vals", "int[]"]],
    returns="int[]",
    statement="""Implement a FIFO **queue** using only **stacks** (push to top, pop from top, peek top,
size/empty). Support:

- `push x`: add `x` to the back of the queue,
- `pop`: remove and **return** the front element,
- `peek`: return the front element without removing it,
- `empty`: return whether the queue is empty.

Operations come as parallel arrays `ops` / `vals` (`vals[i]` is the pushed value for
`push`, else `0`). Return the outputs of every `pop`, `peek` and `empty` in order, with
`empty` reported as `1` (true) or `0` (false). `pop` and `peek` are only called on a
non-empty queue. Every operation should be **amortised O(1)**.""",
    constraints=["1 ≤ len(ops) ≤ 10⁴", "1 ≤ vals[i] ≤ 10⁹ for pushes"],
    hints=[
        "A stack reverses order. What do you get if you reverse something twice?",
        "Use an `in` stack for pushes and an `out` stack for pops. Pouring `in` into `out` reverses it, so the oldest element ends up on top of `out`.",
        "Only pour when `out` is empty. Then each element is moved at most once in its lifetime, which makes every operation amortised O(1).",
    ],
    explanation=r"""
## Intuition

Popping everything off a stack and pushing it onto another **reverses** the order: the
bottom (oldest) element ends up on top. That's exactly the element a queue should return
next. The subtle part is *when* to move elements so that the total work stays linear.

## Approach

Two stacks:

- `inbox`: every `push` goes here.
- `outbox`: `pop`/`peek` read from here. If it's empty, first pour **all** of `inbox`
  into it.

```
push 1, push 2, push 3        inbox: [1 2 3]   outbox: []
peek → outbox empty, pour     inbox: []        outbox: [3 2 1]   top = 1 ✓
pop  → 1                      inbox: []        outbox: [3 2]
push 4                        inbox: [4]       outbox: [3 2]
pop  → 2 (outbox not empty,   inbox: [4]       outbox: [3]
        no pour!)
pop  → 3                      inbox: [4]       outbox: []
pop  → outbox empty, pour     inbox: []        outbox: [4]       → 4
```

Why not pour when `outbox` still has elements? Those elements are *older* than anything
in `inbox`; pouring on top of them would put newer elements in front. Pouring only into
an empty `outbox` preserves FIFO order.

`empty` is true exactly when both stacks are empty.

## Complexity

- **Amortised O(1) per operation.** A single `pop` may pour n elements (O(n)), but
  follow one element through its life: pushed onto `inbox` once, moved to `outbox` once,
  popped once. Three O(1) steps per element, so m operations cost O(m) in total.
- **Space:** O(n).

This is the classic example of **amortised analysis**: individual operations can be
slow, but the average over any sequence is constant. (Compare with dynamic arrays
doubling their capacity.)

## Common mistakes

- **Pouring on every pop** and pouring back on every push: correct but O(n) per
  operation.
- **Pouring into a non-empty `outbox`**: breaks FIFO order.
- **`empty` checking only one stack.**
- **Outputs:** `push` produces nothing; `empty` must be reported as 1/0.

## Going further

- The reverse puzzle, **stack from queues**, needs O(n) per push or per pop: rotate the
  queue after each push so the newest element is at the front.
- Functional languages implement persistent queues exactly this way (the "banker's
  queue"): two immutable lists, front and reversed back.
- With two *min-stacks* you get a queue with O(1) `getMin`, which solves sliding-window
  minimum.
""",
    solution='''def queue_via_stacks(ops, vals):
    class MyQueue:
        def __init__(self):
            self.inbox = []     # newest on top; receives every push
            self.outbox = []    # oldest on top; serves pop/peek

        def _shift(self):
            # Pour only when outbox is empty: its contents are older than anything
            # in inbox, so pouring on top of them would break FIFO order.
            # Each element is moved at most once in its lifetime -> amortised O(1).
            if not self.outbox:
                while self.inbox:
                    self.outbox.append(self.inbox.pop())

        def push(self, x):
            self.inbox.append(x)

        def pop(self):
            self._shift()
            return self.outbox.pop()

        def peek(self):
            self._shift()
            return self.outbox[-1]

        def empty(self):
            return not self.inbox and not self.outbox

    q = MyQueue()
    out = []
    for op, v in zip(ops, vals):
        if op == "push":
            q.push(v)
        elif op == "pop":
            out.append(q.pop())
        elif op == "peek":
            out.append(q.peek())
        else:  # "empty"
            out.append(1 if q.empty() else 0)
    return out
''',
    refs={
        "cpp": '''class MyQueue {
    vector<long long> in, out;     // two stacks
    void shift() {
        if (out.empty())
            while (!in.empty()) { out.push_back(in.back()); in.pop_back(); }
    }
public:
    void push(long long x) { in.push_back(x); }
    long long pop() { shift(); long long x = out.back(); out.pop_back(); return x; }
    long long peek() { shift(); return out.back(); }
    bool empty() const { return in.empty() && out.empty(); }
};

vector<long long> queueViaStacks(vector<string>& ops, vector<long long>& vals) {
    MyQueue q;
    vector<long long> res;
    for (size_t i = 0; i < ops.size(); i++) {
        if (ops[i] == "push") q.push(vals[i]);
        else if (ops[i] == "pop") res.push_back(q.pop());
        else if (ops[i] == "peek") res.push_back(q.peek());
        else res.push_back(q.empty() ? 1 : 0);
    }
    return res;
}''',
        "rust": '''struct MyQueue {
    inbox: Vec<i64>,
    outbox: Vec<i64>,
}

impl MyQueue {
    fn new() -> Self { MyQueue { inbox: Vec::new(), outbox: Vec::new() } }
    fn shift(&mut self) {
        if self.outbox.is_empty() {
            while let Some(x) = self.inbox.pop() {
                self.outbox.push(x);
            }
        }
    }
    fn push(&mut self, x: i64) { self.inbox.push(x); }
    fn pop(&mut self) -> i64 { self.shift(); self.outbox.pop().unwrap() }
    fn peek(&mut self) -> i64 { self.shift(); *self.outbox.last().unwrap() }
    fn empty(&self) -> bool { self.inbox.is_empty() && self.outbox.is_empty() }
}

pub fn queue_via_stacks(ops: Vec<String>, vals: Vec<i64>) -> Vec<i64> {
    let mut q = MyQueue::new();
    let mut res = Vec::new();
    for (op, &v) in ops.iter().zip(vals.iter()) {
        match op.as_str() {
            "push" => q.push(v),
            "pop" => res.push(q.pop()),
            "peek" => res.push(q.peek()),
            _ => res.push(if q.empty() { 1 } else { 0 }),
        }
    }
    res
}''',
    },
    tests=[
        [["push", "push", "peek", "pop", "empty"], [1, 2, 0, 0, 0]],
        [["push", "push", "push", "peek", "pop", "push", "pop", "pop", "pop", "empty"], [1, 2, 3, 0, 0, 4, 0, 0, 0, 0]],
        [["empty"], [0]],
        [["push", "pop", "empty", "push", "peek"], [9, 0, 0, 8, 0]],
        [["push", "push", "pop", "push", "push", "pop", "pop", "pop", "empty"], [10, 20, 0, 30, 40, 0, 0, 0, 0]],
        [["push", "empty", "peek", "peek", "pop", "empty"], [5, 0, 0, 0, 0, 0]],
        _queue_ops(111, 800),
    ],
)

SIMPLIFY_PATH = dict(
    id="simplify-unix-path",
    title="Simplify Path",
    difficulty=2,
    tags=["stack", "string"],
    fn="simplify_path",
    params=[["path", "str"]],
    returns="str",
    statement="""Given an **absolute** Unix-style path (it starts with `/`), return its simplified
**canonical** form:

- `.` means the current directory and is dropped.
- `..` moves up one directory; at the root it stays at the root.
- Multiple consecutive slashes count as one.
- Any other name (including things like `...` or `a.b`) is a normal directory name.

The canonical path starts with a single `/`, separates directories with single `/`, and
has no trailing `/` (except the root itself, `"/"`).""",
    constraints=["1 ≤ len(path) ≤ 3000", "path consists of letters, digits, `.`, `/`, `_`", "path starts with `/`"],
    hints=[
        "Split the path on `/`. What do the empty pieces correspond to?",
        "Walk the pieces with a stack of directory names: skip empty pieces and `.`; on `..` pop (if non-empty); otherwise push.",
        "Join the stack with `/` and put a `/` in front. An empty stack gives `/`.",
    ],
    explanation=r"""
## Intuition

Walking into directories and back out with `..` is exactly push and pop: the current
location *is* a stack of directory names from the root. So split the path into pieces
and replay them on a stack.

## Approach

1. `parts = path.split("/")`. Splitting `"/a//b/./../c/"` yields
   `["", "a", "", "b", ".", "..", "c", ""]`; empty strings come from leading,
   doubled or trailing slashes.
2. For each part:
   - `""` or `"."` → ignore;
   - `".."` → pop if the stack isn't empty;
   - anything else → push.
3. Return `"/" + "/".join(stack)`.

Trace on `"/home//user/./docs/../pics/"`:

| part | action | stack |
|---|---|---|
| `""` | skip | |
| `home` | push | `home` |
| `""` | skip | `home` |
| `user` | push | `home user` |
| `.` | skip | `home user` |
| `docs` | push | `home user docs` |
| `..` | pop | `home user` |
| `pics` | push | `home user pics` |
| `""` | skip | `home user pics` |

Result: `/home/user/pics`.

**Language mechanics.** Python's `split` and `join` make this short. In C++,
`std::stringstream` with `getline(ss, part, '/')` splits a string. Rust's
`path.split('/')` returns an iterator of `&str` slices without allocating, and
`stack.join("/")` concatenates. In C, scan manually: find each segment between slashes
with two indices and compare with `strncmp`.

## Complexity

- **Time:** O(n) to split, process and join.
- **Space:** O(n) for the pieces and the stack.

## Common mistakes

- **Treating `...` as special.** Only exactly `.` and `..` are special; `...` is a name.
- **Popping an empty stack** on `/../`: at the root, `..` stays at the root.
- **Returning `""` instead of `"/"`** for an empty stack.
- **Trailing slash** in the result: joining with a separator avoids it naturally.

## Going further

- **Relative paths** (no leading `/`) must keep leading `..` components because there's
  no root to stop at.
- Real path resolution also follows **symbolic links**, which can point anywhere, so
  `a/../b` is not always `b` on a real filesystem. That's why tools like `realpath` touch
  the disk.
""",
    solution='''def simplify_path(path):
    stack = []                       # directory names from the root downward
    # Splitting on "/" turns repeated, leading and trailing slashes into "" parts.
    for part in path.split("/"):
        if part == "" or part == ".":
            continue                 # no-op: extra slash or "current directory"
        if part == "..":
            if stack:                # ".." at the root stays at the root
                stack.pop()
        else:
            stack.append(part)       # any other name, including "...", is a directory
    # Join with single slashes; an empty stack is the root "/".
    return "/" + "/".join(stack)
''',
    refs={
        "cpp": '''string simplifyPath(string path) {
    vector<string> st;
    stringstream ss(path);
    string part;
    while (getline(ss, part, '/')) {           // splits on '/', yields "" for "//"
        if (part.empty() || part == ".") continue;
        if (part == "..") { if (!st.empty()) st.pop_back(); }
        else st.push_back(part);
    }
    string out;
    for (auto& d : st) out += "/" + d;
    return out.empty() ? "/" : out;
}''',
        "rust": '''pub fn simplify_path(path: String) -> String {
    let mut st: Vec<&str> = Vec::new();     // slices borrow from `path`, no copies
    for part in path.split('/') {
        match part {
            "" | "." => {}
            ".." => { st.pop(); }           // pop on empty is a harmless None
            name => st.push(name),
        }
    }
    format!("/{}", st.join("/"))
}''',
        "c": '''char* simplify_path(char* path) {
    size_t n = strlen(path);
    // Stack of (start, length) segments pointing into `path`.
    int* start = malloc(sizeof(int) * (n + 1));
    int* len = malloc(sizeof(int) * (n + 1));
    int top = 0;
    size_t i = 0;
    while (i < n) {
        while (i < n && path[i] == '/') i++;           // skip slashes
        size_t j = i;
        while (j < n && path[j] != '/') j++;           // segment is path[i..j)
        int L = (int)(j - i);
        if (L == 0 || (L == 1 && path[i] == '.')) { /* skip */ }
        else if (L == 2 && path[i] == '.' && path[i + 1] == '.') { if (top > 0) top--; }
        else { start[top] = (int)i; len[top] = L; top++; }
        i = j;
    }
    char* out = malloc(n + 2);
    size_t k = 0;
    for (int t = 0; t < top; t++) {
        out[k++] = '/';
        memcpy(out + k, path + start[t], len[t]);
        k += len[t];
    }
    if (k == 0) out[k++] = '/';
    out[k] = '\\0';
    free(start); free(len);
    return out;
}''',
    },
    tests=[
        ["/home/"],
        ["/../"],
        ["/home//foo/"],
        ["/a/./b/../../c/"],
        ["/"],
        ["/..."],
        ["/a/../../b/../c//.//"],
        ["/.../a/../b/c/../d/./"],
        ["/home//user/./docs/../pics/"],
        ["/" + "/".join(random.Random(112).choice(["a", "bb", ".", "..", "", "x_1", "..."]) for _ in range(400))],
    ],
)


def _encode_nested(r, depth):
    parts = []
    for _ in range(r.randint(1, 3)):
        if depth > 0 and r.random() < 0.6:
            parts.append(f"{r.randint(1, 3)}[{_encode_nested(r, depth - 1)}]")
        else:
            parts.append("".join(r.choice("xyz") for _ in range(r.randint(1, 3))))
    return "".join(parts)


DECODE_STRING = dict(
    id="decode-nested-string",
    title="Decode String",
    difficulty=2,
    tags=["stack", "string", "parsing", "recursion"],
    fn="decode_string",
    params=[["s", "str"]],
    returns="str",
    statement="""An encoded string uses the rule `k[encoded]`: the part inside the brackets is repeated
exactly `k` times. Encodings nest. Return the decoded string.

- `"3[a]2[bc]"` → `"aaabcbc"`
- `"3[a2[c]]"` → `"accaccacc"`

`k` is a positive integer that may have several digits. The input is always valid,
contains no other digits, and letters are lowercase. The decoded output has at most
10⁵ characters.""",
    constraints=["1 ≤ len(s) ≤ 30", "1 ≤ k ≤ 300", "len(output) ≤ 10⁵"],
    hints=[
        "When you hit `]`, you need to know two things about the matching `[`: the repeat count before it, and the text that was being built *before* it started.",
        "Use a stack of `(prefix_so_far, k)` pairs. On `[` push the current string and the number you just read, then start a fresh current string.",
        "On `]`, pop `(prefix, k)` and set `current = prefix + current * k`. Accumulate multi-digit numbers with `k = k * 10 + digit`.",
    ],
    explanation=r"""
## Intuition

Brackets nest, and the innermost bracket must be expanded before its parent can be.
When the scanner enters `[`, it must *suspend* the outer work (the text built so far and
the multiplier) and resume it at the matching `]`. "Suspend and resume later, most
recent first" is a stack, the same thing the call stack does in a recursive solution.

## Approach

State while scanning: `cur` (the string being built at the current depth) and `num`
(the number being read).

- digit → `num = num * 10 + digit`
- `[` → push `(cur, num)`, reset `cur = ""`, `num = 0`
- `]` → pop `(prev, k)`, set `cur = prev + cur * k`
- letter → `cur += letter`

Trace on `"3[a2[c]]"`:

| char | action | stack | cur |
|---|---|---|---|
| 3 | num = 3 | | `""` |
| [ | push ("", 3) | `("",3)` | `""` |
| a | append | `("",3)` | `a` |
| 2 | num = 2 | `("",3)` | `a` |
| [ | push ("a", 2) | `("",3) ("a",2)` | `""` |
| c | append | … | `c` |
| ] | pop ("a",2): cur = "a" + "c"·2 | `("",3)` | `acc` |
| ] | pop ("",3): cur = "" + "acc"·3 | | `accaccacc` |

**Recursive alternative.** `parse(i)` reads letters and `k[...]` groups until it meets
`]` or the end, recursing on each `[`, and returns the decoded string plus the index
after it. Same logic, with the call stack doing the bookkeeping.

**Language mechanics.** Repeating a string: Python `s * k`, Rust `s.repeat(k)`; in C++
loop `k` times appending (there's no `string * int`). Building strings with repeated
`+=` in a loop is fine here; in Python a list of pieces plus `"".join` is the idiom for
very long outputs.

## Complexity

- **Time:** O(output length), since every output character is written a bounded number of
  times per nesting level (strictly, O(depth · output) for pathological nesting).
- **Space:** O(output) plus the stack of depth ≤ nesting depth.

## Common mistakes

- **Single-digit numbers only**: `"10[a]"` must give ten `a`s.
- **Forgetting to reset `num`** after pushing it.
- **Concatenation order** on `]`: it's `prev + cur * k`, not `cur * k + prev`.
- **Letters after a group** (`"2[a]bc"`) must be appended to the outer `cur`, which
  works naturally when `cur` was restored by the pop.

## Going further

- **Encode** a string into the shortest such form: an interval-DP problem (LeetCode 471).
- The same stack pattern parses **chemical formulas** like `Mg(OH)2` (count atoms) and
  **nested lists** like `[1,[2,[3]]]`.
""",
    solution='''def decode_string(s):
    stack = []        # suspended outer contexts: (text built before '[', repeat count)
    cur = ""          # text being built at the current nesting level
    num = 0           # repeat count being read (may span several digits)
    for c in s:
        if c.isdigit():
            num = num * 10 + int(c)
        elif c == "[":
            # Entering a group: save the outer state, start fresh inside.
            stack.append((cur, num))
            cur, num = "", 0
        elif c == "]":
            # Group finished: expand it and glue it onto the saved outer text.
            prev, k = stack.pop()
            cur = prev + cur * k
        else:
            cur += c
    return cur
''',
    refs={
        "cpp": '''string decodeString(string s) {
    vector<pair<string, int>> st;     // (outer text, repeat count)
    string cur;
    int num = 0;
    for (char c : s) {
        if (isdigit(c)) num = num * 10 + (c - '0');
        else if (c == '[') { st.push_back({cur, num}); cur.clear(); num = 0; }
        else if (c == ']') {
            auto [prev, k] = st.back(); st.pop_back();
            string rep;
            rep.reserve(cur.size() * k);
            for (int i = 0; i < k; i++) rep += cur;   // no string * int in C++
            cur = prev + rep;
        } else cur += c;
    }
    return cur;
}''',
        "rust": '''pub fn decode_string(s: String) -> String {
    let mut st: Vec<(String, usize)> = Vec::new();
    let mut cur = String::new();
    let mut num = 0usize;
    for c in s.chars() {
        if let Some(d) = c.to_digit(10) {
            num = num * 10 + d as usize;
        } else if c == '[' {
            // std::mem::take moves cur out and leaves an empty String behind
            st.push((std::mem::take(&mut cur), num));
            num = 0;
        } else if c == ']' {
            let (prev, k) = st.pop().unwrap();
            cur = prev + &cur.repeat(k);
        } else {
            cur.push(c);
        }
    }
    cur
}''',
    },
    tests=[
        ["3[a]2[bc]"],
        ["3[a2[c]]"],
        ["2[abc]3[cd]ef"],
        ["abc"],
        ["10[a]"],
        ["1[z]"],
        ["2[a]bc2[d]"],
        ["3[z2[y1[x]]]q"],
        ["100[ab]"],
        ["2[3[4[5[q]]]]"],
        [_encode_nested(random.Random(113), 3)],
        [_encode_nested(random.Random(122), 4)],
    ],
)


def _swm_tests():
    r = random.Random(114)
    big = [r.randint(-10**4, 10**4) for _ in range(2000)]
    return [
        [[1, 3, -1, -3, 5, 3, 6, 7], 3],
        [[1], 1],
        [[4, 2], 2],
        [[9, 8, 7, 6, 5], 2],
        [[1, 2, 3, 4, 5], 2],
        [[5, 5, 5, 5], 3],
        [[1, -1], 1],
        [[r.randint(-9, 9) for _ in range(60)], 7],
        [big, 1],
        [big, 1000],
        [list(range(2000, 0, -1)), 700],
    ]


SLIDING_MAX = dict(
    id="sliding-window-maximum",
    title="Sliding Window Maximum",
    difficulty=3,
    tags=["deque", "monotonic queue", "sliding window"],
    fn="max_sliding_window",
    params=[["nums", "int[]"], ["k", "int"]],
    returns="int[]",
    statement="""A window of size `k` slides over `nums` from left to right, one step at a time. Return
the **maximum of each window**: an array of length `len(nums) - k + 1` whose `i`-th
entry is `max(nums[i : i + k])`.

The largest tests use big `n` and big `k`, so O(n·k) is too slow; aim for O(n).""",
    constraints=["1 ≤ k ≤ len(nums) ≤ 10⁵", "-10⁴ ≤ nums[i] ≤ 10⁴"],
    hints=[
        "A running sum handles add/remove in O(1), but a running max can't: when the max leaves the window, what's the new max?",
        "If a newer element is ≥ an older one, the older one can **never** be a window maximum again: it leaves the window first and is dominated until then. Throw it away.",
        "Keep a deque of indices whose values are decreasing front to back. For each `i`: pop from the back while `nums[back] <= nums[i]`; push `i`; pop from the front if it fell out of the window (`front <= i - k`); once `i >= k - 1`, the front is the max.",
    ],
    explanation=r"""
## Intuition

Think of the window as a line of candidates for "maximum". When a new element `x`
arrives, every older element smaller than or equal to `x` is **hopeless**: it will leave
the window before `x` does, and while both are inside, `x` beats it. So drop them. The
survivors form a **decreasing** sequence, and the front of that sequence is the current
maximum. Elements also leave from the front when they slide out of the window. Removal
from both ends calls for a **deque**.

## Approach

Store **indices** (to know when they expire):

```
dq = deque()
for i, x in enumerate(nums):
    while dq and nums[dq[-1]] <= x:   # drop hopeless candidates from the back
        dq.pop()
    dq.append(i)
    if dq[0] <= i - k:                # front slid out of the window
        dq.popleft()
    if i >= k - 1:                    # first full window ends at index k-1
        out.append(nums[dq[0]])
```

Trace on `[1, 3, -1, -3, 5, 3, 6, 7]`, `k = 3` (deque shows values):

| i | x | drop back | expire front | deque | window max |
|---|---|---|---|---|---|
| 0 | 1 | | | `1` | |
| 1 | 3 | 1 | | `3` | |
| 2 | -1 | | | `3 -1` | 3 |
| 3 | -3 | | | `3 -1 -3` | 3 |
| 4 | 5 | -3, -1, 3 | | `5` | 5 |
| 5 | 3 | | | `5 3` | 5 |
| 6 | 6 | 3, 5 | | `6` | 6 |
| 7 | 7 | 6 | | `7` | 7 |

Output `[3, 3, 5, 5, 6, 7]`. The "expire" step never fired here because big values
kept clearing the deque. Try `[9, 1, 1, 1]` with `k = 2` to see it fire.

Only one front element can expire per step, because indices enter one per step, so an
`if` suffices (a `while` is also fine).

## Complexity

- **Time:** O(n): each index enters and leaves the deque at most once.
- **Space:** O(k) for the deque, plus the output.

## Common mistakes

- **Storing values instead of indices**: you can't tell when the front expires (values
  can repeat).
- **`<` instead of `<=` when dropping from the back** still works but keeps redundant
  equal elements; both are correct here.
- **Emitting before the first window is full**: output starts at `i = k - 1`.
- **Python `list.pop(0)`** for the front is O(n); use `collections.deque`.
- **Rust:** `VecDeque::front()` returns `Option<&usize>`; copy with `*` or `.copied()`.

## Going further

- **Sliding window minimum**: flip the comparison.
- **Sparse table** answers arbitrary range-max queries in O(1) after O(n log n)
  preprocessing; the deque wins when windows slide monotonically.
- **Shortest subarray with sum ≥ K** (with negatives) uses a monotonic deque over prefix
  sums: a hard but beautiful application of the same idea.
""",
    solution='''from collections import deque

def max_sliding_window(nums, k):
    dq = deque()      # indices; their values strictly decrease from front to back
    out = []
    for i, x in enumerate(nums):
        # Any older element <= x can never be a window maximum again: it expires
        # before x does and is dominated by x until then.
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        # The front is the oldest survivor; drop it once it leaves [i-k+1, i].
        if dq[0] <= i - k:
            dq.popleft()
        # The first complete window ends at index k-1.
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out
''',
    refs={
        "cpp": '''vector<long long> maxSlidingWindow(vector<long long>& nums, long long k) {
    deque<int> dq;                         // indices, decreasing values
    vector<long long> out;
    for (int i = 0; i < (int)nums.size(); i++) {
        while (!dq.empty() && nums[dq.back()] <= nums[i]) dq.pop_back();
        dq.push_back(i);
        if (dq.front() <= i - k) dq.pop_front();
        if (i >= k - 1) out.push_back(nums[dq.front()]);
    }
    return out;
}''',
        "rust": '''use std::collections::VecDeque;

pub fn max_sliding_window(nums: Vec<i64>, k: i64) -> Vec<i64> {
    let k = k as usize;
    let mut dq: VecDeque<usize> = VecDeque::new();
    let mut out = Vec::with_capacity(nums.len() + 1 - k);
    for i in 0..nums.len() {
        while let Some(&b) = dq.back() {
            if nums[b] > nums[i] {
                break;
            }
            dq.pop_back();
        }
        dq.push_back(i);
        // i + 1 >= k + front  <=>  front <= i - k, written without usize underflow
        if dq[0] + k <= i {
            dq.pop_front();
        }
        if i + 1 >= k {
            out.push(nums[dq[0]]);
        }
    }
    out
}''',
        "c": '''long long* max_sliding_window(long long* nums, int numsSize, long long k, int* returnSize) {
    // A deque as an array with head/tail indices; every index enters once,
    // so a buffer of numsSize slots never wraps.
    int* dq = malloc(sizeof(int) * numsSize);
    int head = 0, tail = 0;                        // live elements: dq[head..tail)
    long long* out = malloc(sizeof(long long) * (numsSize - k + 1));
    int m = 0;
    for (int i = 0; i < numsSize; i++) {
        while (tail > head && nums[dq[tail - 1]] <= nums[i]) tail--;
        dq[tail++] = i;
        if (dq[head] <= i - k) head++;
        if (i >= k - 1) out[m++] = nums[dq[head]];
    }
    free(dq);
    *returnSize = m;
    return out;
}''',
    },
    tests=_swm_tests(),
)


def _msk_rand(seed, n, k):
    r = random.Random(seed)
    return [[r.randint(-1000, 1000) for _ in range(n)], k]


MAX_SUM_K = dict(
    id="max-sum-subarray-size-k",
    title="Maximum Sum Subarray of Size K",
    difficulty=1,
    tags=["sliding window", "array"],
    fn="max_sum_subarray_k",
    params=[["nums", "int[]"], ["k", "int"]],
    returns="int",
    statement="""Return the largest sum of any **contiguous** subarray of `nums` with exactly `k`
elements. Values can be negative.

Instead of re-adding all `k` elements for every window, update the sum as the window
slides: O(n) total.""",
    constraints=["1 ≤ k ≤ len(nums) ≤ 10⁵", "-10⁴ ≤ nums[i] ≤ 10⁴"],
    hints=[
        "Compute the sum of the first window `nums[0..k-1]`. How does the sum change when the window moves one step right?",
        "Moving right adds `nums[i]` and removes `nums[i - k]`. That's two operations per step regardless of `k`.",
        "Initialise the best with the first window's sum, **not** 0: with all-negative values the answer is negative.",
    ],
    explanation=r"""
## Intuition

Consecutive windows overlap in `k − 1` elements. Recomputing those shared elements for
every window is wasted work. Keep a running sum and adjust it by what enters and what
leaves.

## Approach

1. `window = sum(nums[0:k])`, `best = window`.
2. For `i` from `k` to `n − 1`: `window += nums[i] - nums[i - k]`; `best = max(best,
   window)`.

Trace on `[2, 1, 5, 1, 3, 2]`, `k = 3`:

```
i   enters  leaves  window          best
-   -       -       2+1+5 = 8        8
3   1       2       8 + 1 - 2 = 7    8
4   3       1       7 + 3 - 1 = 9    9
5   2       5       9 + 2 - 5 = 6    9
```

Answer: 9 (`[5, 1, 3]`).

**Language mechanics.** A `for` loop with a range like `range(k, n)` (Python), `for i in
k..n` (Rust, ESPresso), or `for (int i = k; i < n; i++)` (C) visits `k, k+1, …, n−1`; the
upper bound is excluded in all of them. `nums[i - k]` is the element that just slid out:
when `i = k`, that's index 0. ESPresso has no `max` built-in in this setting, so write
`if window > best { best = window }`.

## Complexity

- **Time:** O(n): k additions to start, then O(1) per step.
- **Space:** O(1).
- The naive double loop is O(n·k): with n = 10⁵ and k = 5·10⁴ that's billions of steps.

## Common mistakes

- **`best = 0` initially**: wrong for all-negative arrays.
- **Off-by-one in the leaving index**: it's `i - k`, not `i - k + 1` (that one is still
  inside the new window).
- **`k == n`**: only one window; the loop over `i` doesn't run, and that's correct.
- **Overflow**: sums reach 10⁴ · 10⁵ = 10⁹, close to the 32-bit limit (2.1·10⁹). Fine
  for i64; in a 32-bit language keep an eye on it.

## Going further

- **Maximum subarray of *any* length** is Kadane's algorithm: a different idea (drop the
  prefix when it goes negative).
- **Prefix sums** answer every window sum as `P[i + k] − P[i]`, a more general tool for
  arbitrary range-sum queries.
- **Variable-size windows** (shortest subarray with sum ≥ target, for non-negative
  values) use two pointers, as in Minimum Window Substring.
""",
    solution='''def max_sum_subarray_k(nums, k):
    # Sum of the first window nums[0 .. k-1].
    window = sum(nums[:k])
    # Start from a real window sum, not 0: all-negative inputs have negative answers.
    best = window
    for i in range(k, len(nums)):
        # Slide right by one: nums[i] enters, nums[i - k] leaves. O(1) per step.
        window += nums[i] - nums[i - k]
        if window > best:
            best = window
    return best
''',
    refs={
        "c": '''long long max_sum_subarray_k(long long* nums, int numsSize, long long k) {
    long long window = 0;
    for (int i = 0; i < k; i++) window += nums[i];
    long long best = window;
    for (int i = (int)k; i < numsSize; i++) {
        window += nums[i] - nums[i - k];     // enter right, leave left
        if (window > best) best = window;
    }
    return best;
}''',
        "cpp": '''long long maxSumSubarrayK(vector<long long>& nums, long long k) {
    long long window = accumulate(nums.begin(), nums.begin() + k, 0LL);
    long long best = window;
    for (size_t i = k; i < nums.size(); i++) {
        window += nums[i] - nums[i - k];
        best = max(best, window);
    }
    return best;
}''',
        "rust": '''pub fn max_sum_subarray_k(nums: Vec<i64>, k: i64) -> i64 {
    let k = k as usize;
    let mut window: i64 = nums[..k].iter().sum();
    let mut best = window;
    for i in k..nums.len() {
        window += nums[i] - nums[i - k];
        best = best.max(window);
    }
    best
}''',
        "espresso": '''fn maxSumSubarrayK(nums, k) {
  var window = 0
  for var i in 0..k {
    window += nums[i]
  }
  var best = window
  for var i in k..len(nums) {
    // nums[i] enters on the right, nums[i - k] leaves on the left
    window += nums[i] - nums[i - k]
    if window > best { best = window }
  }
  return best
}''',
    },
    tests=[
        [[2, 1, 5, 1, 3, 2], 3],
        [[2, 3, 4, 1, 5], 2],
        [[-3, -1, -2], 1],
        [[-3, -1, -2], 3],
        [[7], 1],
        [[1, 2, 3, 4], 4],
        [[0, 0, 0, 0, 5], 2],
        _msk_rand(115, 60, 7),
        _msk_rand(116, 40, 39),
    ],
)


def _mws_tests():
    r = random.Random(117)
    letters = "abcdeABC"
    big_s = "".join(r.choice(letters) for _ in range(20000))
    return [
        ["ADOBECODEBANC", "ABC"],
        ["a", "a"],
        ["a", "aa"],
        ["ab", "b"],
        ["abc", "d"],
        ["aaflslflsldkalskaaa", "aaa"],
        ["cabwefgewcwaefgcf", "cae"],
        ["bba", "ab"],
        ["abab", "ab"],
        [big_s, "AAbBC"],
        [big_s, "".join(r.choice(letters) for _ in range(40))],
        ["x" * 5000 + "y" + "x" * 5000 + "z", "zy"],
    ]


MIN_WINDOW = dict(
    id="minimum-window-substring",
    title="Minimum Window Substring",
    difficulty=3,
    tags=["sliding window", "two pointers", "hash map", "string"],
    fn="min_window",
    params=[["s", "str"], ["t", "str"]],
    returns="str",
    statement="""Return the **shortest substring** of `s` that contains every character of `t`
**including duplicates** (if `t = "aab"`, the window needs at least two `a`s and one
`b`). If several shortest windows exist, return the **leftmost** one. If no window
exists, return the empty string `""`.

Characters are ASCII letters; case matters. Aim for O(len(s) + len(t)).""",
    constraints=["1 ≤ len(s), len(t) ≤ 2·10⁴", "s and t consist of English letters"],
    hints=[
        "Use two pointers `left` and `right` delimiting a window. Grow `right` until the window contains everything in `t`. Then what can you do with `left`?",
        "Once the window is valid, shrink from the left as long as it *stays* valid, recording the length each time. When it becomes invalid, go back to growing.",
        "Track `need[c]` (count still required from `t`) and a single integer `missing` = total characters still needed. Adding `c` decreases `missing` only if `need[c] > 0` before decrementing; removing `c` increases it only if `need[c]` becomes positive.",
        "Update the best window only when the length is **strictly** smaller, which keeps the leftmost of equal-length answers.",
    ],
    explanation=r"""
## Intuition

Brute force checks all O(n²) substrings. But windows have a monotone structure: if
`s[l..r]` contains `t`, so does every bigger window around it, and if it doesn't, no
smaller window inside it does. That's the signature of the **variable-size sliding
window**: for each right end, find the *largest* left end that keeps the window valid.
Both pointers only move forward, so the whole scan is linear.

## Approach

1. `need = Counter(t)`, `missing = len(t)`.
2. For each `right`, add `c = s[right]`: if `need[c] > 0`, this character was actually
   required, so `missing -= 1`. Then `need[c] -= 1` (it can go negative, meaning
   "surplus").
3. While `missing == 0` (window valid):
   - record `[left, right]` if it's strictly shorter than the best so far;
   - remove `s[left]`: `need[s[left]] += 1`; if it became positive, the window now lacks
     that character, so `missing += 1`; then `left += 1`.

Trace on `s = "ADOBECODEBANC"`, `t = "ABC"` (showing only when the window is valid):

| right | char | window when it first becomes valid | shrinks to | length |
|---|---|---|---|---|
| 5 | C | `ADOBEC` | `ADOBEC` (A needed) | 6 |
| 10 | A | `DOBECODEBA` | `CODEBA` (C needed) | 6 |
| 12 | C | `ODEBANC` | `BANC` (B needed) | **4** |

Answer: `"BANC"`.

**Why the leftmost wins.** For each right end we record the shortest window ending
there. Among equally short windows, the one with the smaller right end also has the
smaller left end, and it's encountered first; strict `<` keeps it.

**Language mechanics.** A `Counter`/`dict` works in Python. In C, C++ and Rust a fixed
array `int need[128]` indexed by the character code is faster and simpler, since the
characters are ASCII. In Rust, iterate bytes (`s.as_bytes()`) so indices are `u8`
values and slicing `&s[l..r]` is valid (ASCII only, so byte indices are char boundaries).

## Complexity

- **Time:** O(|s| + |t|): `right` and `left` each advance at most |s| times; each step
  is O(1).
- **Space:** O(alphabet) for the counts.

## Common mistakes

- **Ignoring duplicates in `t`**: a set of required characters fails `t = "aa"`.
- **Recomputing "is the window valid?"** by comparing whole count tables each step:
  O(alphabet) per step. Fine for 52 letters, but the `missing` counter is the clean O(1)
  way.
- **Decrementing `missing` for surplus characters**: only decrement when the character
  was still needed (`need[c] > 0` *before* decrementing).
- **Returning a window of length 0** or garbage when none exists: track "best = none".

## Going further

- **Longest substring without repeating characters**: same two pointers, opposite goal
  (maximise while valid).
- **Find all anagrams of p in s**: a *fixed*-size window with the same count table.
- **Substring with concatenation of all words**: the window moves in word-sized steps.
""",
    solution='''from collections import Counter

def min_window(s, t):
    need = Counter(t)        # how many more of each char the window requires
    missing = len(t)         # total chars still required (counting duplicates)
    left = 0
    best_start, best_len = 0, float("inf")
    for right, c in enumerate(s):
        # Adding c only helps if the window still needed a c.
        if need[c] > 0:
            missing -= 1
        need[c] -= 1         # may go negative: surplus copies of c
        # Window s[left..right] is valid: shrink it as far as it stays valid.
        while missing == 0:
            # Strict < keeps the leftmost window among equal lengths.
            if right - left + 1 < best_len:
                best_start, best_len = left, right - left + 1
            d = s[left]
            need[d] += 1
            if need[d] > 0:  # we just removed a required copy: window now invalid
                missing += 1
            left += 1
    return "" if best_len == float("inf") else s[best_start:best_start + best_len]
''',
    refs={
        "cpp": '''string minWindow(string s, string t) {
    int need[128] = {0};                 // ASCII-indexed counts
    for (char c : t) need[(unsigned char)c]++;
    int missing = t.size(), left = 0, bestStart = 0, bestLen = INT_MAX;
    for (int right = 0; right < (int)s.size(); right++) {
        if (need[(unsigned char)s[right]]-- > 0) missing--;   // test, then decrement
        while (missing == 0) {
            if (right - left + 1 < bestLen) { bestLen = right - left + 1; bestStart = left; }
            if (++need[(unsigned char)s[left]] > 0) missing++;
            left++;
        }
    }
    return bestLen == INT_MAX ? "" : s.substr(bestStart, bestLen);
}''',
        "rust": '''pub fn min_window(s: String, t: String) -> String {
    let sb = s.as_bytes();
    let mut need = [0i32; 128];
    for &c in t.as_bytes() {
        need[c as usize] += 1;
    }
    let mut missing = t.len();
    let mut left = 0usize;
    let mut best: Option<(usize, usize)> = None;   // (start, len)
    for right in 0..sb.len() {
        let c = sb[right] as usize;
        if need[c] > 0 {
            missing -= 1;
        }
        need[c] -= 1;
        while missing == 0 {
            let len = right - left + 1;
            if best.map_or(true, |(_, l)| len < l) {
                best = Some((left, len));
            }
            let d = sb[left] as usize;
            need[d] += 1;
            if need[d] > 0 {
                missing += 1;
            }
            left += 1;
        }
    }
    match best {
        Some((st, len)) => s[st..st + len].to_string(),
        None => String::new(),
    }
}''',
    },
    tests=_mws_tests(),
)


def _asteroids(seed, n):
    r = random.Random(seed)
    out = []
    while len(out) < n:
        v = r.randint(1, 1000)
        out.append(v if r.random() < 0.5 else -v)
    return out


ASTEROIDS = dict(
    id="asteroid-collision",
    title="Asteroid Collision",
    difficulty=2,
    tags=["stack", "simulation"],
    fn="asteroid_collision",
    params=[["asteroids", "int[]"]],
    returns="int[]",
    statement="""Asteroids sit in a row, listed left to right. For each one, the absolute value is its
size and the sign is its direction (positive = moving right, negative = moving left).
All move at the same speed.

When a right-mover meets a left-mover, the smaller one explodes; if they're the same
size, both explode. Asteroids moving in the same direction never meet, and a
left-mover on the left never meets a right-mover on its right.

Return the asteroids that remain after all collisions, in left-to-right order.""",
    constraints=["2 ≤ len(asteroids) ≤ 10⁴", "1 ≤ |asteroids[i]| ≤ 1000", "asteroids[i] ≠ 0"],
    hints=[
        "Which pairs can ever collide? Only a positive asteroid that is somewhere to the left of a negative one.",
        "Process asteroids left to right, keeping the survivors so far on a stack. A new right-mover can't hit anything yet: push it. A new left-mover may crash into right-movers at the top of the stack.",
        "For a left-mover `x`: while the top is a positive `t` smaller than `|x|`, pop it. Then if the top is a positive equal to `|x|`, pop it and drop `x`; if the top is a bigger positive, drop `x`; otherwise push `x`.",
    ],
    explanation=r"""
## Intuition

Collisions only happen between a `→` asteroid and a `←` asteroid somewhere to its right.
Scanning left to right, the survivors so far look like `[← ← ← → → →]`: any left-movers
first (they escaped), then right-movers waiting to see what comes. A new left-mover will
hit the **nearest** right-mover first, the most recently added survivor: the top of a
stack.

## Approach

```
for x in asteroids:
    alive = True
    while alive and x < 0 and stack and stack[-1] > 0:
        top = stack[-1]
        if top < -x:   stack.pop()            # top explodes, x keeps going
        elif top == -x: stack.pop(); alive = False   # both explode
        else:          alive = False          # x explodes
    if alive:
        stack.append(x)
```

Trace on `[10, 2, -5, 6, -6, -12]`:

| x | collisions | stack after |
|---|---|---|
| 10 | | `10` |
| 2 | | `10 2` |
| -5 | 2 vs 5: 2 explodes; 10 vs 5: -5 explodes | `10` |
| 6 | | `10 6` |
| -6 | 6 vs 6: both explode | `10` |
| -12 | 10 vs 12: 10 explodes; stack empty → push | `-12` |

Result `[-12]`.

**Language mechanics.** In Rust, borrowing `stack.last()` while also wanting to
`stack.pop()` inside the same expression upsets the borrow checker; copy the value out
first: `let top = *stack.last().unwrap();`. In C, the stack array doubles as the result
array: the surviving prefix `st[0..top)` is already in left-to-right order.

## Complexity

- **Time:** O(n): each asteroid is pushed at most once and popped at most once.
- **Space:** O(n) for the stack (which is also the answer).

## Common mistakes

- **Colliding a left-mover with a left-mover on the stack**, or a right-mover arriving
  with a left-mover on top: `[-2, 1]` produces no collision.
- **Forgetting the equal-size case**: both must disappear.
- **Stopping after one collision**: a big left-mover can destroy several right-movers in
  a row.
- **Reversed output**: the stack bottom is the leftmost survivor; don't reverse it.

## Going further

- **Robot collisions** (LeetCode 2751) adds health that decreases after each collision
  and asks you to keep original indices: the same stack plus bookkeeping.
- The same "resolve against the top until stable" loop appears in **remove adjacent
  duplicates** and in **car fleet**.
""",
    solution='''def asteroid_collision(asteroids):
    stack = []   # survivors so far, left to right: [left-movers..., right-movers...]
    for x in asteroids:
        alive = True
        # Only a left-mover (x < 0) can hit something: the nearest right-mover,
        # which is the top of the stack.
        while alive and x < 0 and stack and stack[-1] > 0:
            top = stack[-1]
            if top < -x:
                stack.pop()          # top is smaller: it explodes, x continues
            elif top == -x:
                stack.pop()          # same size: both explode
                alive = False
            else:
                alive = False        # top is bigger: x explodes
        if alive:
            stack.append(x)
    return stack
''',
    refs={
        "c": '''long long* asteroid_collision(long long* asteroids, int asteroidsSize, int* returnSize) {
    long long* st = malloc(sizeof(long long) * asteroidsSize);  // also the answer
    int top = 0;
    for (int i = 0; i < asteroidsSize; i++) {
        long long x = asteroids[i];
        bool alive = true;
        while (alive && x < 0 && top > 0 && st[top - 1] > 0) {
            long long t = st[top - 1];
            if (t < -x) top--;                       // t explodes
            else { if (t == -x) top--; alive = false; }   // tie: both; else x
        }
        if (alive) st[top++] = x;
    }
    *returnSize = top;
    return st;
}''',
        "cpp": '''vector<long long> asteroidCollision(vector<long long>& asteroids) {
    vector<long long> st;
    for (long long x : asteroids) {
        bool alive = true;
        while (alive && x < 0 && !st.empty() && st.back() > 0) {
            long long t = st.back();
            if (t < -x) st.pop_back();
            else { if (t == -x) st.pop_back(); alive = false; }
        }
        if (alive) st.push_back(x);
    }
    return st;
}''',
        "rust": '''pub fn asteroid_collision(asteroids: Vec<i64>) -> Vec<i64> {
    let mut st: Vec<i64> = Vec::new();
    for x in asteroids {
        let mut alive = true;
        while alive && x < 0 {
            // Copy the top out so we can pop without fighting the borrow checker.
            let top = match st.last() {
                Some(&t) if t > 0 => t,
                _ => break,
            };
            if top < -x {
                st.pop();
            } else {
                if top == -x {
                    st.pop();
                }
                alive = false;
            }
        }
        if alive {
            st.push(x);
        }
    }
    st
}''',
    },
    tests=[
        [[5, 10, -5]],
        [[8, -8]],
        [[10, 2, -5]],
        [[-2, -1, 1, 2]],
        [[1, -2, -2, -2]],
        [[10, 2, -5, 6, -6, -12]],
        [[-5, 5]],
        [[3, 3, 3, -9, 4, -4]],
        [_asteroids(118, 100)],
        [_asteroids(119, 4000)],
    ],
)


def _baseball(seed, n):
    r = random.Random(seed)
    ops, st = [], []
    for _ in range(n):
        c = r.random()
        # Keep every recorded score small so all values fit comfortably in 32 bits.
        if len(st) >= 2 and c < 0.15 and abs(st[-1] + st[-2]) < 10**5:
            ops.append("+"); st.append(st[-1] + st[-2])
        elif st and c < 0.3 and abs(st[-1]) < 10**5:
            ops.append("D"); st.append(2 * st[-1])
        elif st and c < 0.45:
            ops.append("C"); st.pop()
        else:
            v = r.randint(-300, 300)
            ops.append(str(v)); st.append(v)
    return ops


BASEBALL = dict(
    id="baseball-game-scores",
    title="Baseball Game",
    difficulty=1,
    tags=["stack", "simulation"],
    fn="baseball_score",
    params=[["operations", "str[]"]],
    returns="int",
    statement="""You keep score for a game with unusual rules. Start with an empty record and apply
each operation in order:

- an integer `x` (like `"5"` or `"-2"`): record a new score `x`;
- `"+"`: record the sum of the previous two scores;
- `"D"`: record double the previous score;
- `"C"`: invalidate (remove) the previous score.

Return the sum of all scores remaining in the record. Every operation is valid: `"+"`
always has two previous scores, `"D"` and `"C"` always have at least one.""",
    constraints=["1 ≤ len(operations) ≤ 1000", "integers are in [-3·10⁴, 3·10⁴]", "all intermediate values fit in 32 bits"],
    hints=[
        "\"Previous score\" means the most recently recorded score that hasn't been removed. Which data structure gives you the most recent item and lets you remove it?",
        "Keep the record as a stack. `C` is `pop`, `D` pushes `2 * top`, `+` pushes the sum of the top two.",
        "At the end, return the sum of the stack.",
    ],
    explanation=r"""
## Intuition

Every operation talks about "the previous" score(s), and `C` *removes* the previous
score so the one before it becomes "previous" again. Most recent first, with removal:
that's a stack, and the record of scores *is* the stack.

## Approach

```
for op in operations:
    "+" → push(st[-1] + st[-2])
    "D" → push(2 * st[-1])
    "C" → pop()
    else → push(int(op))
return sum(st)
```

Trace on `["5", "2", "C", "D", "+"]`:

| op | action | record |
|---|---|---|
| 5 | push 5 | `5` |
| 2 | push 2 | `5 2` |
| C | pop | `5` |
| D | push 2·5 | `5 10` |
| + | push 5 + 10 | `5 10 15` |

Sum = 30.

**Language mechanics.**
- Python: `st[-1]` is the last element, `st[-2]` the one before; `int("-2")` parses
  negatives.
- C: strings are `char*`; compare the first character (`op[0] == '+'`) and make sure it
  isn't the start of a number: `"-2"` begins with `-`, but none of `+`, `D`, `C` can start
  a number, so checking `op[0]` against those three is safe. Parse numbers with
  `atoll`.
- C++: `stoll(op)` parses; `op == "+"` compares `std::string` contents.
- Rust: `op.as_str()` lets you `match` on string literals, and `op.parse::<i64>()`
  returns a `Result`, unwrapped here because input is guaranteed valid.

## Complexity

- **Time:** O(n).
- **Space:** O(n) for the record.

## Common mistakes

- **`"+"` uses the top two *without removing them*.** It adds a third score.
- **Detecting numbers by "first char is a digit"**: misses negatives like `"-2"`.
- **Summing as you go and forgetting that `C` must subtract** the removed score. A
  running total can work (subtract on `C`), but the stack is still needed to know what
  to subtract.

## Going further

- Add an **undo** for `C` (bring back the last removed score): keep a second stack of
  removed values.
- This is a tiny **interpreter**: a stack machine with four instructions. Compare with
  Evaluate Reverse Polish Notation, where operators *consume* their operands.
""",
    solution='''def baseball_score(operations):
    record = []          # stack of valid scores; the top is "the previous score"
    for op in operations:
        if op == "+":
            # Sum of the previous two; they stay in the record.
            record.append(record[-1] + record[-2])
        elif op == "D":
            record.append(2 * record[-1])
        elif op == "C":
            record.pop()             # the score before it becomes "previous" again
        else:
            record.append(int(op))   # int() handles negative numbers like "-2"
    return sum(record)
''',
    refs={
        "c": '''long long baseball_score(char** operations, int operationsSize) {
    long long* st = malloc(sizeof(long long) * (operationsSize + 1));
    int top = 0;
    for (int i = 0; i < operationsSize; i++) {
        char c = operations[i][0];   // '+', 'D', 'C' never start a number
        if (c == '+')      { st[top] = st[top - 1] + st[top - 2]; top++; }
        else if (c == 'D') { st[top] = 2 * st[top - 1]; top++; }
        else if (c == 'C') { top--; }
        else               { st[top++] = atoll(operations[i]); }
    }
    long long sum = 0;
    for (int i = 0; i < top; i++) sum += st[i];
    free(st);
    return sum;
}''',
        "cpp": '''long long baseballScore(vector<string>& operations) {
    vector<long long> st;
    for (const string& op : operations) {
        if (op == "+") st.push_back(st[st.size() - 1] + st[st.size() - 2]);
        else if (op == "D") st.push_back(2 * st.back());
        else if (op == "C") st.pop_back();
        else st.push_back(stoll(op));
    }
    return accumulate(st.begin(), st.end(), 0LL);
}''',
        "rust": '''pub fn baseball_score(operations: Vec<String>) -> i64 {
    let mut st: Vec<i64> = Vec::new();
    for op in &operations {
        match op.as_str() {
            "+" => {
                let n = st.len();
                st.push(st[n - 1] + st[n - 2]);
            }
            "D" => st.push(2 * st[st.len() - 1]),
            "C" => { st.pop(); }
            num => st.push(num.parse::<i64>().unwrap()),
        }
    }
    st.iter().sum()
}''',
    },
    tests=[
        [["5", "2", "C", "D", "+"]],
        [["5", "-2", "4", "C", "D", "9", "+", "+"]],
        [["1", "C"]],
        [["7"]],
        [["-3", "D", "D"]],
        [["1", "2", "+", "+", "+"]],
        [["0", "0", "+", "C", "C"]],
        [_baseball(120, 60)],
        [_baseball(121, 1000)],
    ],
)

PROBLEMS = [
    VALID_PARENS,
    MIN_STACK,
    EVAL_RPN,
    BASEBALL,
    QUEUE_STACKS,
    SIMPLIFY_PATH,
    DECODE_STRING,
    DAILY_TEMPS,
    NEXT_GREATER,
    ASTEROIDS,
    LARGEST_RECT,
    MAX_SUM_K,
    SLIDING_MAX,
    MIN_WINDOW,
]
