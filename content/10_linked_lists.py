"""Track 10: Linked Lists."""
import random

TRACK = dict(
    id="linked-lists",
    title="Linked Lists",
    order=10,
    icon="⛓",
    blurb="Nodes, pointers and ownership: rewire lists in place with dummy heads, fast/slow pointers, and Rust's take()/as_mut().",
    intro=r"""
An array stores its elements side by side in one block of memory. A **linked list**
stores each element in its own **node**, and every node holds a pointer to the next one:

```text
 head
  │
  ▼
┌─────┬───┐   ┌─────┬───┐   ┌─────┬───┐
│  1  │ ●─┼──▶│  2  │ ●─┼──▶│  3  │ ∅ │
└─────┴───┘   └─────┴───┘   └─────┴───┘
  val  next     val  next     val  next (null / None)
```

In this track the node type is:

```python
class ListNode:            # Python
    def __init__(self, val=0, next=None):
        self.val = val; self.next = next
```

```c
struct ListNode { long long val; struct ListNode* next; };      // C
```

```cpp
struct ListNode { long long val; ListNode* next; };              // C++ (with a constructor)
```

```rust
pub struct ListNode { pub val: i64, pub next: Option<Box<ListNode>> }   // Rust
```

## Trade-offs versus arrays

| operation | array | linked list |
|---|---|---|
| access k-th element | O(1) | O(k): walk from the head |
| insert/delete *given the previous node* | O(n) shifting | **O(1)** pointer rewiring |
| memory | contiguous, cache friendly | one allocation per node, scattered |

Linked list problems are rarely about speed; they are about **rewiring pointers
correctly**. Draw the boxes and arrows, and update arrows in an order that never loses a
node you still need.

## The golden rule: save `next` before you overwrite it

Reversing a list one node at a time:

```text
prev    cur     nxt
 ∅      [1]──▶[2]──▶[3]──▶∅

1. nxt = cur.next          (save the rest of the list)
2. cur.next = prev         (flip the arrow)
3. prev = cur; cur = nxt   (step forward)

 ∅◀──[1]   [2]──▶[3]──▶∅
     prev   cur
```

If step 2 ran before step 1, the rest of the list would be unreachable: lost forever
(and in C, leaked).

## The dummy head trick

Many operations treat the head specially: deleting the first node, or building a new list
where the first append has no predecessor. A **dummy** (sentinel) node placed before the
head removes the special case: every real node now has a predecessor.

```python
dummy = ListNode(0, head)   # dummy → head → ...
tail = dummy
# ... append with tail.next = node; tail = node  (no "if result is empty" branch)
return dummy.next           # the real head, whatever happened to it
```

## Fast and slow pointers

Two pointers moving at different speeds answer positional questions in one pass,
without knowing the length:

- **Middle:** `slow` moves 1 step, `fast` moves 2. When `fast` reaches the end, `slow` is
  in the middle.
- **k-th from the end:** move `fast` k steps ahead first, then move both by 1. When `fast`
  hits the end, `slow` is k nodes behind it.
- **Cycle detection** (Floyd): if there is a cycle, `fast` eventually laps `slow` and they
  meet. *This track's `list` type can't express a cycle (tests are plain arrays and the
  harness prints the list by walking it), so cycle detection isn't included as a problem.
  The technique is the same fast/slow loop with `if slow is fast: return True`.*

## Ownership: who frees a node?

**C** gives you raw `malloc`/`free`. A node you unlink is still allocated; if nothing
points to it any more, `free` it or it leaks. Never touch a node after freeing it, and
read `node->next` *before* `free(node)`.

```c
struct ListNode* dead = prev->next;
prev->next = dead->next;   // unlink first
free(dead);                // then release
```

**C++** in this track uses raw pointers too (`new` / `delete`). You *can* wrap nodes in
`std::unique_ptr`, but the harness uses raw pointers, like LeetCode. A dummy node can
simply live on the stack: `ListNode dummy(0, head);` and it disappears automatically.

**Rust** is where linked lists get famous. A node *owns* the next node through
`Option<Box<ListNode>>`:

- `Box<ListNode>` is a heap pointer that **owns** its node: when the box is dropped,
  the node (and, recursively, everything it owns) is freed. No leaks, no double frees.
- `Option<…>` encodes "maybe there is no next node" (`None` is the null pointer).

Since every node has exactly one owner, you cannot just copy a pointer to a node and
keep two handles to it as in C. You **move** ownership around instead, using a small
toolkit:

| tool | type change | what it does |
|---|---|---|
| `opt.take()` | `&mut Option<T>` → `Option<T>` | moves the value out, leaving `None` behind: "cut the link and hold the rest" |
| `opt.as_ref()` | `&Option<Box<T>>` → `Option<&Box<T>>` | a read-only peek, without moving |
| `opt.as_mut()` | `&mut Option<Box<T>>` → `Option<&mut Box<T>>` | a mutable handle to the node inside |
| `node.next = x` | | the old value of `next` is dropped (freed) here |

The canonical reversal shows `take()` in action: each node is moved out of the list,
pointed at the reversed part, and becomes the new front.

```rust
let (mut prev, mut cur) = (None, head);
while let Some(mut node) = cur {     // move the box out of `cur`
    cur = node.next.take();          // detach the rest; node.next is now None
    node.next = prev;                // point at the reversed part (moves prev in)
    prev = Some(node);               // node becomes the new front
}
prev
```

To **walk and modify in place**, hold a `&mut` to the current node and re-borrow it
forward. This is the pattern for appending to a tail:

```rust
let mut dummy = Box::new(ListNode::new(0));
let mut tail = &mut dummy;                 // &mut Box<ListNode>
for v in values {
    tail.next = Some(Box::new(ListNode::new(v)));
    tail = tail.next.as_mut().unwrap();    // move the cursor to the new last node
}
dummy.next
```

What Rust **won't** let you do is hold a `&mut` to one node while also keeping another
reference into the same list (e.g. a C-style `fast` and `slow` both pointing into the list
while you mutate through `slow`). The idiomatic workarounds, which you'll see throughout
this track:

1. **Count first, then act.** Walk with `as_ref()` (shared borrows, as many as you like)
   to find a length or a position, *then* walk again with `as_mut()` to change things.
2. **Split ownership.** Use `take()` to cut the list into separately-owned pieces, work on
   each, and splice them back together.
3. **Move instead of borrow.** `head = head.unwrap().next` walks forward by *consuming*
   nodes, handy when you want to return a suffix of the list.

One more Rust trap: dropping a `Box` chain is recursive (each node drops its `next`), so a
list of millions of nodes can overflow the stack when freed. Production code writes a
manual `Drop` that unlinks iteratively; the lists here are small enough not to care.

## Patterns in this track

- Pointer reversal: reverse, palindrome check, reorder, reverse in k-groups.
- Dummy head + tail: merge, add two numbers, remove nth, sort.
- Fast/slow: middle, nth from end, splitting for merge sort.
- Splitting and splicing: rotate, reorder, k-groups, merge sort.

Every problem has reference solutions in C, C++ and Rust: compare how the same pointer
surgery looks under manual memory, raw pointers, and ownership.
""",
)

PROBLEMS = []


def _rand_list(rng, n, lo=-1000, hi=1000):
    return [rng.randint(lo, hi) for _ in range(n)]

_rng = random.Random(1001)

# ---------------------------------------------------------------- 1. reverse
PROBLEMS.append(dict(
    id="reverse-linked-list",
    title="Reverse a Linked List",
    difficulty=1,
    tags=["linked list", "pointers"],
    fn="reverse_list",
    params=[["head", "list"]],
    returns="list",
    statement=r"""
Given the `head` of a singly linked list, **reverse** the list and return the new head.

Do it **in place** by re-pointing the existing nodes' `next` pointers. Don't allocate new
nodes. The list may be empty (`head` is null / `None`).
""",
    constraints=["0 ≤ number of nodes ≤ 5000", "−5000 ≤ node.val ≤ 5000"],
    example_notes=["Every arrow flips direction; the old tail becomes the head.", "The empty list reversed is still empty."],
    hints=[
        "Walk the list once. At each node, which way should its `next` arrow point after the reversal?",
        "You need three names: `prev` (the already-reversed part), `cur` (the node being flipped) and `nxt` (the rest of the list).",
        "Loop while `cur`: save `nxt = cur.next`, set `cur.next = prev`, then `prev = cur`, `cur = nxt`. At the end `prev` is the new head.",
    ],
    explanation=r"""
## Intuition

Reversing a list doesn't move any values; it flips every arrow. Walking from the head,
each node's `next` should point to the node that came *before* it. The only difficulty is
that flipping `cur.next` destroys our only route to the rest of the list, so we must save
that route first.

## Approach

Keep `prev` (head of the reversed part, initially null) and `cur` (initially `head`):

1. `nxt = cur.next` — save the rest.
2. `cur.next = prev` — flip the arrow.
3. `prev = cur`, `cur = nxt` — advance both.

Trace on `1 → 2 → 3`:

| step | prev | cur | reversed part | remaining |
|---|---|---|---|---|
| start | ∅ | 1 | ∅ | 1→2→3 |
| 1 | 1 | 2 | 1→∅ | 2→3 |
| 2 | 2 | 3 | 2→1→∅ | 3 |
| 3 | 3 | ∅ | 3→2→1→∅ | ∅ |

`cur` is null, so return `prev` = 3.

**Language mechanics.** In Python, `node.next` is an attribute holding a reference;
assigning it just makes it refer to a different object. In C and C++ `cur->next` is a
pointer field and `->` dereferences `cur` first. In Rust, `cur` *owns* the remaining list,
so the loop moves nodes out of it with `take()`:

```rust
while let Some(mut node) = cur {   // move the first box out of cur
    cur = node.next.take();        // cur now owns the rest; node.next = None
    node.next = prev;              // node owns the reversed part
    prev = Some(node);             // and becomes its new head
}
```

Every node has exactly one owner at every moment: the borrow checker is verifying the
"don't lose the rest of the list" rule for you.

**Recursive version:** reverse everything after the head, then hook the head onto the end:

```python
def reverse(head):
    if not head or not head.next:
        return head
    new_head = reverse(head.next)
    head.next.next = head     # the old second node now points back at head
    head.next = None
    return new_head
```

Elegant, but it uses O(n) stack depth, risky for long lists in C/C++/Rust.

## Complexity

- **Time:** O(n), one pass.
- **Space:** O(1) for the iterative version; O(n) stack for the recursive one.

## Common mistakes

- **Overwriting `cur.next` before saving it:** the rest of the list is lost.
- **Returning `head`:** after reversal the old head is the *tail*. Return `prev`.
- **Forgetting `head.next = None`** in the recursive version: the old head still points at
  the old second node, forming a 2-node cycle.
- **Rust:** `while let Some(node) = cur` moves `cur`; you must assign `cur` again in the
  loop body before the next iteration (which `cur = node.next.take()` does).

## Going further

- **Reverse between positions m and n**: walk to node m−1, reverse the sub-range with the
  same loop, then reconnect both ends.
- Reversal is a building block for palindrome checks, reorder list, adding numbers stored
  most-significant-digit first, and reversing in k-groups (all later in this track).
""",
    solution=r'''def reverse_list(head):
    prev = None          # head of the already-reversed part (empty at first)
    cur = head           # next node to flip
    while cur:
        nxt = cur.next   # save the rest of the list BEFORE we overwrite cur.next
        cur.next = prev  # flip this node's arrow to point backwards
        prev = cur       # the reversed part now starts at cur
        cur = nxt        # continue with the saved remainder
    # cur is None: every node has been flipped and prev is the old tail = new head.
    return prev
''',
    refs={
        "c": r"""struct ListNode* reverse_list(struct ListNode* head) {
    struct ListNode* prev = NULL;   // reversed part
    struct ListNode* cur = head;    // node to flip
    while (cur) {
        struct ListNode* nxt = cur->next;   // 1. save the rest
        cur->next = prev;                   // 2. flip the arrow
        prev = cur;                         // 3. advance both pointers
        cur = nxt;
    }
    return prev;                            // old tail = new head
}
""",
        "cpp": r"""ListNode* reverseList(ListNode* head) {
    ListNode* prev = nullptr;
    while (head) {
        // std::exchange(a, b) sets a = b and returns the old a. Read it as:
        // "remember head->next, point it at prev instead".
        ListNode* nxt = std::exchange(head->next, prev);
        prev = head;
        head = nxt;
    }
    return prev;
}
""",
        "rust": r"""pub fn reverse_list(head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    // `prev` owns the reversed part, `cur` owns the part still to process.
    let mut prev: Option<Box<ListNode>> = None;
    let mut cur = head;
    // `while let` moves the Box out of `cur` (leaving cur moved-from until we reassign it).
    while let Some(mut node) = cur {
        cur = node.next.take(); // take(): move the rest out, leaving node.next = None
        node.next = prev;       // node now owns the reversed part
        prev = Some(node);      // ... and becomes its head
    }
    prev
}
""",
    },
    tests=[[[1, 2, 3, 4, 5]], [[]], [[1]], [[1, 2]], [[5, 5, 5]], [[-3, 0, 3]], [_rand_list(_rng, 1000)]],
))

# ---------------------------------------------------------------- 2. middle
PROBLEMS.append(dict(
    id="middle-of-linked-list",
    title="Middle of the Linked List",
    difficulty=1,
    tags=["linked list", "fast and slow pointers"],
    fn="middle_node",
    params=[["head", "list"]],
    returns="list",
    statement=r"""
Given the `head` of a non-empty singly linked list, return the **middle node** (and so
the list from the middle to the end).

If the list has an even number of nodes there are two middle nodes; return the **second**
one. Try to do it in a single pass without counting the length first.
""",
    constraints=["1 ≤ number of nodes ≤ 1000", "−1000 ≤ node.val ≤ 1000"],
    example_notes=["5 nodes: the 3rd node is the middle.", "6 nodes: the middles are 3 and 4; return the second, 4."],
    hints=[
        "The two-pass way is easy: count the nodes, then walk `count / 2` steps. Can one pass do it?",
        "If one pointer moves twice as fast as another, where is the slow one when the fast one reaches the end?",
        "`slow = fast = head`; while `fast` and `fast.next` exist: `slow = slow.next`, `fast = fast.next.next`. Return `slow`.",
    ],
    explanation=r"""
## Intuition

We need the node at position ⌊n/2⌋ (0-indexed) but don't know n. Two runners on the
same track, one at double speed: when the fast runner finishes, the slow runner has
covered exactly half the distance. That's the **fast/slow pointer** technique.

## Approach

```python
slow = fast = head
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next
return slow
```

Trace for 5 nodes and 6 nodes (positions of `slow` / `fast`):

```text
odd: 1 → 2 → 3 → 4 → 5          even: 1 → 2 → 3 → 4 → 5 → 6
 start  s=1 f=1                    start  s=1 f=1
 step1  s=2 f=3                    step1  s=2 f=3
 step2  s=3 f=5  (f.next = ∅)      step2  s=3 f=5
 → stop, slow = 3 ✓                step3  s=4 f=∅  (stepped past 6)
                                   → stop, slow = 4 ✓
```

The loop condition decides which middle you get. `while fast and fast.next` returns the
**second** middle for even lengths. Changing it to `while fast.next and fast.next.next`
stops one step earlier and returns the **first** middle, which is what you want when
splitting a list into halves for merge sort.

**In Rust**, two pointers into one list are fine as long as both are shared borrows
(`as_ref()`), but we must *return an owned* `Option<Box<ListNode>>`. A shared reference
can't be turned into ownership. The idiomatic fix: run fast/slow with shared borrows only
to count how many steps `slow` takes, then walk the owned list forward that many steps,
dropping the first half as we go: `head = head.unwrap().next`.

## Complexity

- **Time:** O(n). The fast pointer visits about n nodes, the slow one n/2.
- **Space:** O(1).

(The two-pass "count then walk" approach is also O(n) and O(1); fast/slow simply needs
one pass, which matters for streams or when the trick is combined with other work.)

## Common mistakes

- **Checking only `fast.next`**: when `fast` itself becomes null (even length), reading
  `fast.next` crashes. Check `fast` first; `and`/`&&` short-circuits.
- **Wrong middle for even lengths**: be deliberate about which loop condition you use.
- **C:** don't free the first half: the caller (here, the harness) still owns those nodes,
  and the problem only asks for a pointer into the list.

## Going further

- **k-th node from the end:** give `fast` a head start of k nodes, then advance both.
- **Floyd's cycle detection:** the same loop, checking whether `slow` and `fast` ever meet.
- Splitting at the middle is the first step of palindrome checking, reorder list and
  merge sort on lists.
""",
    solution=r'''def middle_node(head):
    # slow moves one node per step, fast moves two. When fast runs off the end,
    # slow has covered half the distance.
    slow = fast = head
    # 'fast and fast.next': both must exist to take a double step. This condition
    # yields the SECOND middle for even lengths.
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow
''',
    refs={
        "c": r"""struct ListNode* middle_node(struct ListNode* head) {
    struct ListNode *slow = head, *fast = head;
    while (fast && fast->next) {     // && short-circuits: fast->next only read if fast != NULL
        slow = slow->next;           // 1 step
        fast = fast->next->next;     // 2 steps
    }
    return slow;                     // a pointer into the existing list, nothing freed
}
""",
        "cpp": r"""ListNode* middleNode(ListNode* head) {
    ListNode *slow = head, *fast = head;
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
    }
    return slow;
}
""",
        "rust": r"""pub fn middle_node(head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    // Phase 1: fast/slow with shared borrows. We only need to know HOW MANY steps the
    // slow pointer would take; a shared reference can't be returned as an owned list.
    let mut steps = 0;
    let mut fast = head.as_ref();
    while let Some(f) = fast {
        match f.next.as_ref() {
            Some(f2) => {
                fast = f2.next.as_ref(); // fast moves two nodes
                steps += 1;              // slow would move one
            }
            None => break,               // odd length: fast is on the last node
        }
    }
    // The borrows above have ended, so we may move `head` now.
    // Phase 2: walk the owned list forward, dropping (freeing) the first half.
    let mut cur = head;
    for _ in 0..steps {
        cur = cur.unwrap().next; // move the Box out, keep its `next`, drop the node
    }
    cur
}
""",
    },
    tests=[[[1, 2, 3, 4, 5]], [[1, 2, 3, 4, 5, 6]], [[1]], [[1, 2]], [[7, 8, 9]], [[-1, -2, -3, -4]],
           [_rand_list(_rng, 999)], [_rand_list(_rng, 1000)]],
))

# ---------------------------------------------------------------- 3. merge two sorted
def _sorted_list(rng, n, lo=-1000, hi=1000):
    return sorted(rng.randint(lo, hi) for _ in range(n))


PROBLEMS.append(dict(
    id="merge-two-sorted-lists",
    title="Merge Two Sorted Lists",
    difficulty=1,
    tags=["linked list", "dummy head", "two pointers"],
    fn="merge_two_lists",
    params=[["l1", "list"], ["l2", "list"]],
    returns="list",
    statement=r"""
You're given the heads of two linked lists `l1` and `l2`, each sorted in **non-decreasing**
order. Merge them into **one sorted list** by splicing together the existing nodes, and
return its head.

Either list may be empty.
""",
    constraints=["0 ≤ length of each list ≤ 1000", "−1000 ≤ node.val ≤ 1000", "both lists are sorted"],
    example_notes=["Interleave by always taking the smaller front node.", "Both empty: the result is empty."],
    hints=[
        "Look only at the two front nodes. Which of them must come first in the result?",
        "Repeatedly detach the smaller front node and append it to the result. Appending is easier with a pointer to the result's last node.",
        "Start the result with a dummy node so the first append isn't a special case. When one list runs out, attach the whole remainder of the other one in a single step. Return `dummy.next`.",
    ],
    explanation=r"""
## Intuition

The smallest element overall is at the front of `l1` or the front of `l2`: nowhere else
can be smaller, since both lists are sorted. Take it, and the remaining problem is the
same merge on slightly shorter lists. This is the merge step of merge sort, and with
linked lists we can do it without allocating anything: just relink nodes.

## Approach

1. Create a **dummy** node and a `tail` pointer to it.
2. While both lists are non-empty: let `small` be the front node with the smaller value
   (prefer `l1` on ties, which keeps the merge *stable*). Set `tail.next = small`, advance
   that list, and move `tail = small`.
3. One list is empty now: `tail.next = the other list` (its nodes are already sorted and
   all ≥ everything we placed).
4. Return `dummy.next`.

Trace for `[1,2,4]` and `[1,3,4]`:

| step | l1 | l2 | take | result |
|---|---|---|---|---|
| 1 | **1**,2,4 | 1,3,4 | l1's 1 (tie → l1) | 1 |
| 2 | 2,4 | **1**,3,4 | l2's 1 | 1,1 |
| 3 | **2**,4 | 3,4 | 2 | 1,1,2 |
| 4 | 4 | **3**,4 | 3 | 1,1,2,3 |
| 5 | **4** | 4 | 4 (tie) | 1,1,2,3,4 |
| 6 | ∅ | 4 | attach rest | 1,1,2,3,4,4 |

**Why the dummy?** Without it, the first append must set `head = small` while every later
append sets `tail.next = small`. The dummy gives the first real node a predecessor, so
there is only one code path. In C and C++ the dummy can be a stack variable; its address
is taken but it is never returned.

**Rust:** `tail` is a `&mut Box<ListNode>` cursor. Each iteration picks `&mut l1` or
`&mut l2` as the source, moves the front box out with `take()`, puts the source's remainder
back with `*src = node.next.take()`, hangs the node on `tail.next`, and re-borrows `tail`
forward with `tail.next.as_mut().unwrap()`.

## Complexity

- **Time:** O(n + m). Each node is appended once.
- **Space:** O(1). Only pointers are rearranged. (A recursive merge is shorter to write,
  but its stack depth is O(n + m).)

## Common mistakes

- **Losing the rest of a list:** advance `l1 = l1.next` *before* or independently of
  overwriting `tail.next`. Since we only change `tail.next`, which belongs to a node already
  in the result, this is safe here, but be careful in variants.
- **Forgetting the leftover tail:** looping `while l1 or l2` with null checks works, but
  the single `tail.next = l1 or l2` attaches everything at once in O(1).
- **Returning `dummy`** instead of `dummy.next`: the result would start with a bogus 0.
- **Using `<` for ties:** still sorted, but unstable. Stable merges matter when sorting
  records by key.

## Going further

- **Merge k sorted lists:** use a min-heap of front nodes (O(N log k)), or merge pairwise
  in rounds like bottom-up merge sort.
- This exact function is the combine step for **Sort List** at the end of this track.
""",
    solution=r'''def merge_two_lists(l1, l2):
    # The dummy node sits before the result's first real node, so appending the
    # first node needs no special case.
    dummy = ListNode(0)
    tail = dummy                    # last node of the merged list so far
    while l1 and l2:
        # The smaller front node must come next. '<=' prefers l1 on ties (stable).
        if l1.val <= l2.val:
            tail.next = l1
            l1 = l1.next            # advance the list we took from
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next            # the appended node is the new tail
    # One list is exhausted; the other is sorted and >= everything placed so far.
    tail.next = l1 if l1 else l2
    return dummy.next               # skip the dummy
''',
    refs={
        "c": r"""struct ListNode* merge_two_lists(struct ListNode* l1, struct ListNode* l2) {
    struct ListNode dummy = {0, NULL};     // lives on the stack; only dummy.next escapes
    struct ListNode* tail = &dummy;
    while (l1 && l2) {
        if (l1->val <= l2->val) { tail->next = l1; l1 = l1->next; }
        else                    { tail->next = l2; l2 = l2->next; }
        tail = tail->next;
    }
    tail->next = l1 ? l1 : l2;             // splice the leftover run in O(1)
    return dummy.next;
}
""",
        "cpp": r"""ListNode* mergeTwoLists(ListNode* l1, ListNode* l2) {
    ListNode dummy;                        // stack sentinel, destroyed automatically
    ListNode* tail = &dummy;
    while (l1 && l2) {
        // Pick a reference to whichever list pointer holds the smaller node,
        // so a single code path advances the right list.
        ListNode*& src = (l1->val <= l2->val) ? l1 : l2;
        tail->next = src;
        src = src->next;
        tail = tail->next;
    }
    tail->next = l1 ? l1 : l2;
    return dummy.next;
}
""",
        "rust": r"""pub fn merge_two_lists(
    mut l1: Option<Box<ListNode>>,
    mut l2: Option<Box<ListNode>>,
) -> Option<Box<ListNode>> {
    let mut dummy = Box::new(ListNode::new(0));
    let mut tail = &mut dummy; // &mut Box<ListNode>: a cursor at the result's last node
    while let (Some(a), Some(b)) = (l1.as_ref(), l2.as_ref()) {
        // Choose which list to take from. `src` is a &mut to l1 or l2 itself.
        let src = if a.val <= b.val { &mut l1 } else { &mut l2 };
        let mut node = src.take().unwrap(); // move the front box out of that list
        *src = node.next.take();            // the list now starts at the old second node
        tail.next = Some(node);             // append
        tail = tail.next.as_mut().unwrap(); // re-borrow the cursor onto the new last node
    }
    // At most one list is non-empty; `or` picks it (l1 if Some, else l2).
    tail.next = l1.or(l2);
    dummy.next
}
""",
    },
    tests=[
        [[1, 2, 4], [1, 3, 4]], [[], []], [[], [0]], [[5], [1, 2, 3]], [[1, 2, 3], [4, 5, 6]],
        [[-3, -1, 10], [-2, 10, 11]], [[2, 2, 2], [2, 2]],
        [_sorted_list(_rng, 300), _sorted_list(_rng, 280)],
    ],
))

# ---------------------------------------------------------------- 4. remove duplicates
PROBLEMS.append(dict(
    id="remove-duplicates-sorted-list",
    title="Remove Duplicates from Sorted List",
    difficulty=1,
    tags=["linked list", "pointers"],
    fn="delete_duplicates",
    params=[["head", "list"]],
    returns="list",
    statement=r"""
Given the `head` of a **sorted** linked list, delete nodes so that every value appears
**exactly once**, keeping the first node of each run of equal values. Return the head of
the resulting list (which stays sorted).
""",
    constraints=["0 ≤ number of nodes ≤ 1000", "−100 ≤ node.val ≤ 100", "the list is sorted in non-decreasing order"],
    example_notes=["The second 1 is unlinked.", "Each run of duplicates collapses to one node."],
    hints=[
        "In a sorted list, where are all the copies of a value?",
        "Compare each node with the node right after it. If they're equal, the next one is a duplicate.",
        "With `cur` on a node: if `cur.next.val == cur.val`, skip it with `cur.next = cur.next.next` and **don't** advance `cur` (there may be more copies). Otherwise `cur = cur.next`.",
    ],
    explanation=r"""
## Intuition

Sorting puts all copies of a value next to each other, so a duplicate is always
*immediately* after an equal node. We never need to look further than one step ahead,
and deletion in a linked list is just re-pointing one arrow around the unwanted node.

## Approach

```python
cur = head
while cur and cur.next:
    if cur.next.val == cur.val:
        cur.next = cur.next.next     # unlink the duplicate; stay on cur
    else:
        cur = cur.next               # next value is new: move on
```

Trace on `1 → 1 → 1 → 2 → 3 → 3`:

```text
cur=1(a): next 1(b) equal → 1(a) → 1(c) → 2 → 3 → 3
cur=1(a): next 1(c) equal → 1(a) → 2 → 3 → 3
cur=1(a): next 2 differs  → cur = 2
cur=2:    next 3 differs  → cur = 3(a)
cur=3(a): next 3(b) equal → 1 → 2 → 3
cur=3(a): next null       → stop
```

Note that `cur` **stays put** after a deletion, which is what handles runs of three or more.
The head never changes (the first node of each run is kept), so no dummy is needed.

**Memory per language.** In Python and Rust, an unlinked node is freed automatically
(garbage collection / the `Box` being dropped when `cur.next` is overwritten). In C you
must `free` it yourself, *after* reading its `next`:

```c
struct ListNode* dup = cur->next;
cur->next = dup->next;
free(dup);
```

In Rust, `node.next = node.next.take().unwrap().next;` reads strangely but is exactly
"cut out the next box, keep *its* next, drop the box". The loop uses the standard
cursor pattern `let mut cur = head.as_mut(); while let Some(node) = cur { …; cur = node.next.as_mut(); }`.

## Complexity

- **Time:** O(n). Each step either deletes a node or advances `cur`.
- **Space:** O(1).

## Common mistakes

- **Advancing after deleting:** with `1 → 1 → 1`, deleting the second 1 and then moving
  to the third 1 leaves `1 → 1`.
- **Reading a freed node** in C: `free(cur->next); cur->next = cur->next->next;` is
  use-after-free. Save the pointer first.
- **Null checks:** the loop needs both `cur` and `cur.next`; an empty list must return
  immediately.

## Going further

- **Remove Duplicates II:** delete *every* node whose value is duplicated (keep only values
  that appear once). Now the head itself can be deleted, so a dummy node is essential.
- For an **unsorted** list, a hash set of seen values gives O(n) time and O(n) space.
""",
    solution=r'''def delete_duplicates(head):
    cur = head
    # Need both cur and cur.next to compare a pair.
    while cur and cur.next:
        if cur.next.val == cur.val:
            # Duplicate: route around it. Stay on cur, since the new cur.next may be
            # yet another copy of the same value.
            cur.next = cur.next.next
        else:
            # A new value follows: cur's run is done.
            cur = cur.next
    # The first node of the list is always kept, so head is still the head.
    return head
''',
    refs={
        "c": r"""struct ListNode* delete_duplicates(struct ListNode* head) {
    struct ListNode* cur = head;
    while (cur && cur->next) {
        if (cur->next->val == cur->val) {
            struct ListNode* dup = cur->next;
            cur->next = dup->next;   // unlink first (we still need dup->next)...
            free(dup);               // ...then release it: nothing points to it now
        } else {
            cur = cur->next;
        }
    }
    return head;
}
""",
        "cpp": r"""ListNode* deleteDuplicates(ListNode* head) {
    for (ListNode* cur = head; cur && cur->next;) {
        if (cur->next->val == cur->val) {
            ListNode* dup = cur->next;
            cur->next = dup->next;
            delete dup;              // nodes were created with new, so release with delete
        } else {
            cur = cur->next;
        }
    }
    return head;
}
""",
        "rust": r"""pub fn delete_duplicates(mut head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    // `cur` is an Option<&mut Box<ListNode>>: a mutable cursor into the list we own.
    let mut cur = head.as_mut();
    while let Some(node) = cur {
        // Peek at the next node with a shared borrow of node.next.
        while node.next.as_ref().map_or(false, |nx| nx.val == node.val) {
            // take() moves the duplicate box out; `.unwrap().next` keeps its tail.
            // The duplicate itself is dropped (freed) at the end of this statement.
            node.next = node.next.take().unwrap().next;
        }
        cur = node.next.as_mut(); // re-borrow forward to the next distinct value
    }
    head
}
""",
    },
    tests=[[[1, 1, 2]], [[1, 1, 2, 3, 3]], [[]], [[1]], [[1, 1, 1, 1]], [[-5, -5, 0, 0, 0, 7]],
           [[1, 2, 3, 4]], [_sorted_list(_rng, 500, -100, 100)]],
))

# ---------------------------------------------------------------- 5. palindrome
_pal_half = _rand_list(_rng, 500, 0, 9)
_pal_big = _pal_half + [4] + _pal_half[::-1]
_pal_near = _pal_half + _pal_half[::-1]
_pal_near[700] = 10 if _pal_near[700] != 10 else 11

PROBLEMS.append(dict(
    id="palindrome-linked-list",
    title="Palindrome Linked List",
    difficulty=2,
    tags=["linked list", "fast and slow pointers", "reversal"],
    fn="is_palindrome",
    params=[["head", "list"]],
    returns="bool",
    statement=r"""
Given the `head` of a singly linked list, return `true` if its values read the same
forwards and backwards, and `false` otherwise. The empty list is a palindrome.

Follow-up: can you do it in **O(n) time and O(1) extra space**?
""",
    constraints=["0 ≤ number of nodes ≤ 2000", "0 ≤ node.val ≤ 11"],
    example_notes=["1 2 2 1 reads the same both ways.", "1 2 reversed is 2 1."],
    hints=[
        "The easy O(n)-space way: copy the values into an array and compare it with its reverse. What makes this harder without the array?",
        "You can't walk a singly linked list backwards… unless you reverse part of it. Which part?",
        "Find the middle with fast/slow pointers, reverse the second half in place, then walk the first half and the reversed second half together comparing values. (Optionally reverse it back to restore the input.)",
    ],
    explanation=r"""
## Intuition

A palindrome check compares the first element with the last, the second with the
second-to-last, and so on. Arrays let us index from both ends; a singly linked list only
goes forward. Copying values into an array is a perfectly good O(n)-space answer. To get
O(1) space we make the second half go *backwards* by reversing it in place, then two
forward walks compare the halves.

## Approach

1. **Find the middle** with fast/slow pointers (`while fast and fast.next`). For odd
   lengths `slow` lands on the centre node, for even lengths on the first node of the
   second half.
2. **Reverse** the list starting at `slow`.
3. **Compare** from `head` and from the reversed half's head, step by step, until the
   reversed half runs out.
4. (Good manners) reverse the second half again to restore the input.

Trace for `1 → 2 → 3 → 2 → 1`:

```text
middle:   slow = 3
reverse:  1 → 2 → 3 ← 2 ← 1        (left half still points at node 3)
                    ↓
                    ∅
compare:  left 1,2,3   right 1,2,3   → all equal → true
```

The first half's last node still points at the centre, which is also the end of the
reversed half. That's fine: we stop when the *right* side runs out, and the centre of an
odd-length list is compared with itself.

**Rust version.** Fast/slow with a `&mut` is awkward, so count the length with `as_ref()`,
walk an `as_mut()` cursor to the last node of the first half (`⌈len/2⌉` nodes), and
`take()` its `next`: now we *own* the second half as a separate list. Reverse it with the
standard loop, then compare with two `as_ref()` walks. Splitting ownership with `take()` is
the move that makes most Rust list algorithms straightforward.

## Complexity

- **Time:** O(n): find middle (n/2), reverse (n/2), compare (n/2).
- **Space:** O(1) extra. The array version is O(n); a recursive version that compares on
  the way back up the call stack is also O(n) (stack frames).

## Common mistakes

- **Comparing the whole left half against the right half** with "stop when the left runs
  out": after reversal the left half isn't cleanly terminated in C/Python (it still leads
  into the centre), so stop on the reversed half instead.
- **Modifying the input permanently:** acceptable here, but in real code restore it or
  document the mutation; callers rarely expect a "check" function to rewire their data.
- **Odd vs. even off-by-one:** test both `[1,2,1]` and `[1,2,2,1]`.

## Going further

- The same "split, reverse half, walk together" pattern solves **Reorder List**.
- A recursive variant keeps a pointer to the front in an outer variable and compares it
  with each node as the recursion unwinds from the back: elegant but O(n) stack.
""",
    solution=r'''def is_palindrome(head):
    # 1. Find the middle. For odd lengths slow lands on the centre node, for even
    #    lengths on the first node of the second half.
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    # 2. Reverse the second half in place so we can walk it from the back.
    prev, cur = None, slow
    while cur:
        nxt = cur.next
        cur.next = prev
        prev, cur = cur, nxt
    right = prev                 # head of the reversed second half (the old tail)

    # 3. Compare pairwise. Stop when the right half ends; it is never longer than
    #    the left half.
    left, r = head, right
    ok = True
    while r:
        if left.val != r.val:
            ok = False
            break
        left, r = left.next, r.next

    # 4. Restore the list (reverse the second half back) so the caller's data is intact.
    prev, cur = None, right
    while cur:
        nxt = cur.next
        cur.next = prev
        prev, cur = cur, nxt
    return ok
''',
    refs={
        "c": r"""static struct ListNode* reverse(struct ListNode* h) {
    struct ListNode* prev = NULL;
    while (h) { struct ListNode* n = h->next; h->next = prev; prev = h; h = n; }
    return prev;
}

bool is_palindrome(struct ListNode* head) {
    struct ListNode *slow = head, *fast = head;
    while (fast && fast->next) { slow = slow->next; fast = fast->next->next; }
    struct ListNode* right = reverse(slow);          // second half, back to front
    bool ok = true;
    for (struct ListNode *l = head, *r = right; r; l = l->next, r = r->next)
        if (l->val != r->val) { ok = false; break; }
    reverse(right);                                  // restore the original links
    return ok;
}
""",
        "cpp": r"""static ListNode* reverseFrom(ListNode* h) {
    ListNode* prev = nullptr;
    while (h) h = std::exchange(h->next, std::exchange(prev, h));  // flip one arrow per step
    return prev;
}

bool isPalindrome(ListNode* head) {
    ListNode *slow = head, *fast = head;
    while (fast && fast->next) { slow = slow->next; fast = fast->next->next; }
    ListNode* right = reverseFrom(slow);
    bool ok = true;
    for (ListNode *l = head, *r = right; r && ok; l = l->next, r = r->next)
        ok = l->val == r->val;
    reverseFrom(right);                              // put the list back
    return ok;
}
""",
        "rust": r"""pub fn is_palindrome(mut head: Option<Box<ListNode>>) -> bool {
    // 1. Length, via shared borrows.
    let mut len = 0;
    let mut p = head.as_ref();
    while let Some(n) = p {
        len += 1;
        p = n.next.as_ref();
    }
    if len < 2 {
        return true;
    }
    // 2. Walk a &mut cursor to the last node of the first half (ceil(len/2) nodes),
    //    then take() its `next`: we now OWN the second half as a separate list.
    let mut cur = head.as_mut().unwrap();
    for _ in 0..(len + 1) / 2 - 1 {
        cur = cur.next.as_mut().unwrap();
    }
    let mut second = cur.next.take();
    // 3. Reverse the second half (the standard take() loop).
    let mut rev: Option<Box<ListNode>> = None;
    while let Some(mut n) = second {
        second = n.next.take();
        n.next = rev;
        rev = Some(n);
    }
    // 4. Compare with two shared-borrow walks. The reversed half is never longer.
    let (mut a, mut b) = (head.as_ref(), rev.as_ref());
    while let (Some(x), Some(y)) = (a, b) {
        if x.val != y.val {
            return false;
        }
        a = x.next.as_ref();
        b = y.next.as_ref();
    }
    true
    // We own `head`, so leaving it split is harmless: both halves are dropped here.
}
""",
    },
    tests=[[[1, 2, 2, 1]], [[1, 2]], [[1]], [[]], [[1, 2, 1]], [[1, 2, 3, 1]], [[1, 1, 2, 1]],
           [[0, 0]], [_pal_big], [_pal_near]],
))

# ---------------------------------------------------------------- 6. remove nth from end
_big6 = _rand_list(_rng, 500)
PROBLEMS.append(dict(
    id="remove-nth-node-from-end",
    title="Remove Nth Node From End of List",
    difficulty=2,
    tags=["linked list", "two pointers", "dummy head"],
    fn="remove_nth_from_end",
    params=[["head", "list"], ["n", "int"]],
    returns="list",
    statement=r"""
Given the `head` of a linked list, remove the **`n`-th node from the end** (`n = 1` is
the last node) and return the head of the modified list.

`n` is always valid: `1 ≤ n ≤ length`. Try to do it in one pass.
""",
    constraints=["1 ≤ number of nodes ≤ 1000", "−1000 ≤ node.val ≤ 1000", "1 ≤ n ≤ number of nodes"],
    example_notes=["The 2nd from the end is 4.", "Removing the only node leaves an empty list."],
    hints=[
        "Two passes is fine to start: count the length L, then remove the node at index `L - n` from the front. What breaks when that's the head?",
        "A dummy node before the head means the node to delete always has a predecessor, even when it's the head.",
        "One pass: put `fast` `n + 1` steps ahead of `slow` (both starting at the dummy), then move both until `fast` is null. Now `slow.next` is the node to remove.",
    ],
    explanation=r"""
## Intuition

To delete a node from a singly linked list we need its **predecessor** (to re-point
`prev.next` around it). "n-th from the end" is a position relative to the end, which we
can't see. Two options:

- **Two passes:** count the length L, then the target's predecessor is node `L − n − 1`
  from the front.
- **One pass with a gap:** keep two pointers exactly `n + 1` nodes apart. When the leading
  one falls off the end, the trailing one is the predecessor.

Either way, the target might be the **head**, which has no predecessor. A dummy node fixes
that.

## Approach (one pass)

1. `dummy.next = head`; `fast = slow = dummy`.
2. Move `fast` forward `n + 1` times.
3. Move both until `fast` is null.
4. `slow.next = slow.next.next`. Return `dummy.next`.

Trace for `1 → 2 → 3 → 4 → 5`, `n = 2` (D = dummy):

```text
D → 1 → 2 → 3 → 4 → 5 → ∅
s           f                  after n+1 = 3 steps
            s           f      … advance together …
                s           f  fast = ∅: stop
slow = 3, slow.next = 4 (2nd from end) → unlink → 1 → 2 → 3 → 5
```

With `n = 5` (remove the head): after 6 steps `fast` is already null, `slow` is still the
dummy, and `dummy.next = head.next`. The dummy made the head case ordinary.

**Rust.** Two pointers into the same list, one of them mutable, are exactly what the
borrow checker forbids. The idiomatic Rust solution is the **two-pass** version: count with
`as_ref()`, then walk a `&mut` cursor from the dummy `len − n` steps and splice:
`cur.next = cur.next.take().and_then(|node| node.next)`. Both versions are O(n); "one
pass" is not asymptotically better.

## Complexity

- **Time:** O(L).
- **Space:** O(1).

## Common mistakes

- **No dummy:** removing the head (`n = L`) needs a special case, and forgetting it
  dereferences null or returns the deleted node.
- **Gap of `n` instead of `n + 1`:** `slow` ends on the target instead of its predecessor.
- **C memory:** unlink, then `free` the removed node. In C++ `delete` it (nodes come from
  `new`). Don't free the dummy if it's on the stack.

## Going further

- **Delete a node given only a pointer to it** (not the tail): copy the next node's value
  into it and delete the next node instead.
- The gap technique finds the k-th from end, splits a list into the last k and the rest
  (see Rotate List), and detects whether two lists intersect after aligning their lengths.
""",
    solution=r'''def remove_nth_from_end(head, n):
    # The dummy gives the head a predecessor, so deleting the head is not special.
    dummy = ListNode(0, head)
    fast = slow = dummy
    # Open a gap of n+1 nodes: when fast falls off the end, slow is the node
    # just BEFORE the one to remove.
    for _ in range(n + 1):
        fast = fast.next
    while fast:
        fast = fast.next
        slow = slow.next
    # Route around the target.
    slow.next = slow.next.next
    return dummy.next          # may differ from head if the head was removed
''',
    refs={
        "c": r"""struct ListNode* remove_nth_from_end(struct ListNode* head, long long n) {
    struct ListNode dummy = {0, head};
    struct ListNode *fast = &dummy, *slow = &dummy;
    for (long long i = 0; i <= n; i++) fast = fast->next;   // gap of n+1
    while (fast) { fast = fast->next; slow = slow->next; }
    struct ListNode* target = slow->next;
    slow->next = target->next;     // unlink
    free(target);                  // release the removed node
    return dummy.next;             // dummy is on the stack: never free it
}
""",
        "cpp": r"""ListNode* removeNthFromEnd(ListNode* head, long long n) {
    ListNode dummy(0, head);
    ListNode *fast = &dummy, *slow = &dummy;
    for (long long i = 0; i <= n; i++) fast = fast->next;
    while (fast) { fast = fast->next; slow = slow->next; }
    ListNode* target = slow->next;
    slow->next = target->next;
    delete target;
    return dummy.next;
}
""",
        "rust": r"""pub fn remove_nth_from_end(head: Option<Box<ListNode>>, n: i64) -> Option<Box<ListNode>> {
    // Pass 1: length (shared borrows only).
    let mut len = 0i64;
    let mut p = head.as_ref();
    while let Some(node) = p {
        len += 1;
        p = node.next.as_ref();
    }
    // Pass 2: a dummy owning the list, and a &mut cursor walked to the predecessor.
    let mut dummy = Box::new(ListNode { val: 0, next: head });
    let mut cur = &mut dummy;
    for _ in 0..(len - n) {
        cur = cur.next.as_mut().unwrap();
    }
    // Cut out the target: take() it, keep its `next`, and let the target box drop.
    cur.next = cur.next.take().and_then(|target| target.next);
    dummy.next
}
""",
    },
    tests=[[[1, 2, 3, 4, 5], 2], [[1], 1], [[1, 2], 1], [[1, 2], 2], [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 10],
           [[7, 7, 7], 3], [_big6, 250], [_big6, 1]],
))

# ---------------------------------------------------------------- 7. add two numbers
def _digits(rng, n):
    d = [rng.randint(0, 9) for _ in range(n)]
    d[-1] = rng.randint(1, 9)          # no leading zero (stored last)
    return d


PROBLEMS.append(dict(
    id="add-two-numbers-lists",
    title="Add Two Numbers",
    difficulty=2,
    tags=["linked list", "math", "dummy head"],
    fn="add_two_numbers",
    params=[["l1", "list"], ["l2", "list"]],
    returns="list",
    statement=r"""
Two non-negative integers are stored as linked lists of decimal digits in **reverse
order**: the head holds the ones digit, the next node the tens digit, and so on. For
example `342` is stored as `2 → 4 → 3`.

Return their **sum** as a new list in the same format. Neither input has leading zeros,
except the number 0 itself, which is the single node `0`.

The numbers can have up to 100 digits, far beyond any built-in integer type, so add them
digit by digit.
""",
    constraints=["1 ≤ length of each list ≤ 100", "0 ≤ node.val ≤ 9", "no leading zeros except for the number 0"],
    example_notes=["342 + 465 = 807, stored reversed as 7 → 0 → 8.", "0 + 0 = 0."],
    hints=[
        "This is grade-school addition. Why is the reversed order convenient?",
        "Walk both lists together, adding the two digits plus a carry. The new digit is `sum % 10`, the new carry is `sum // 10`.",
        "Keep going while **either** list has nodes **or** the carry is non-zero (a final carry adds one more digit). Append to a dummy-headed result list.",
    ],
    explanation=r"""
## Intuition

Column addition starts at the ones digit and moves left, carrying into the next column.
Storing digits in reverse puts the ones digit at the head, so walking the lists front to
back **is** column addition. No reversal, no big-integer library: just a carry.

## Approach

1. `dummy`, `tail = dummy`, `carry = 0`.
2. While `l1` or `l2` or `carry`:
   - `total = carry + (l1.val if l1) + (l2.val if l2)`, advancing each list that exists;
   - append a new node with `total % 10`;
   - `carry = total // 10` (always 0 or 1).
3. Return `dummy.next`.

Trace for 342 + 465 (lists `2→4→3` and `5→6→4`):

| column | l1 | l2 | carry in | total | digit | carry out |
|---|---|---|---|---|---|---|
| ones | 2 | 5 | 0 | 7 | 7 | 0 |
| tens | 4 | 6 | 0 | 10 | 0 | 1 |
| hundreds | 3 | 4 | 1 | 8 | 8 | 0 |

Result `7 → 0 → 8` = 807.

Lists of different lengths are handled by treating a missing digit as 0. The **carry
condition** in the loop handles sums that grow by a digit: `9999999 + 9999` ends with a
lone carry producing a final `1` node.

**Allocation per language.** The result needs new nodes: `ListNode(d)` in Python,
`malloc(sizeof(struct ListNode))` in C (set both fields!), `new ListNode(d)` in C++, and
`Some(Box::new(ListNode::new(d)))` in Rust. In Rust we consume the input lists by value,
moving forward with `if let Some(node) = a.take() { sum += node.val; a = node.next; }`.
The `take()` matters: a plain `if let Some(node) = a` would move `a` and leave it unusable
in the loop condition when it was `None`.

## Complexity

- **Time:** O(max(n, m)).
- **Space:** O(max(n, m)) for the output list (O(1) besides that).

## Common mistakes

- **Dropping the final carry:** `5 + 5` must give `0 → 1`, not `0`.
- **Converting to integers:** fine in Python (big ints), but overflows 64 bits in C/C++/Rust
  beyond 19 digits. The point is the digit-by-digit algorithm.
- **Uninitialised `next` in C:** a node from `malloc` contains garbage; set `next = NULL`.
- **Stopping when the shorter list ends:** the longer list's remaining digits (and the
  carry rippling through them, like `1 + 999`) still need processing.

## Going further

- **Add Two Numbers II** stores the most significant digit first. Reverse both lists,
  add, and reverse the result; or push digits onto two stacks and build the result by
  prepending nodes.
- The same carry loop multiplies a list-number by a small digit, or implements arbitrary
  precision arithmetic over arrays of base-10⁹ "limbs" (how real big-integer libraries do it).
""",
    solution=r'''def add_two_numbers(l1, l2):
    dummy = ListNode(0)     # result starts after the dummy: no special first node
    tail = dummy
    carry = 0
    # Continue while any digits remain OR a carry is pending (e.g. 5 + 5 = 10 needs
    # an extra node for the final carry).
    while l1 or l2 or carry:
        total = carry
        if l1:                       # a missing digit counts as 0
            total += l1.val
            l1 = l1.next
        if l2:
            total += l2.val
            l2 = l2.next
        carry = total // 10          # 0 or 1: at most 9 + 9 + 1 = 19
        tail.next = ListNode(total % 10)
        tail = tail.next
    return dummy.next
''',
    refs={
        "c": r"""struct ListNode* add_two_numbers(struct ListNode* l1, struct ListNode* l2) {
    struct ListNode dummy = {0, NULL};
    struct ListNode* tail = &dummy;
    long long carry = 0;
    while (l1 || l2 || carry) {
        long long total = carry;
        if (l1) { total += l1->val; l1 = l1->next; }
        if (l2) { total += l2->val; l2 = l2->next; }
        carry = total / 10;
        struct ListNode* node = malloc(sizeof *node);   // a brand-new result node
        node->val = total % 10;
        node->next = NULL;                               // malloc doesn't zero memory
        tail->next = node;
        tail = node;
    }
    return dummy.next;
}
""",
        "cpp": r"""ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {
    ListNode dummy;
    ListNode* tail = &dummy;
    long long carry = 0;
    while (l1 || l2 || carry) {
        long long total = carry;
        if (l1) { total += l1->val; l1 = l1->next; }
        if (l2) { total += l2->val; l2 = l2->next; }
        carry = total / 10;
        tail = tail->next = new ListNode(total % 10);   // append and advance in one step
    }
    return dummy.next;
}
""",
        "rust": r"""pub fn add_two_numbers(l1: Option<Box<ListNode>>, l2: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    let (mut a, mut b) = (l1, l2);           // we own the inputs and consume them
    let mut dummy = Box::new(ListNode::new(0));
    let mut tail = &mut dummy;
    let mut carry = 0;
    while a.is_some() || b.is_some() || carry != 0 {
        let mut total = carry;
        // take() leaves `a` as None, then we put the rest of the list back into it.
        // (Matching on `a` directly would move it and break the loop condition.)
        if let Some(node) = a.take() {
            total += node.val;
            a = node.next;                    // move the tail out of the consumed box
        }
        if let Some(node) = b.take() {
            total += node.val;
            b = node.next;
        }
        carry = total / 10;
        tail.next = Some(Box::new(ListNode::new(total % 10)));
        tail = tail.next.as_mut().unwrap();
    }
    dummy.next
}
""",
    },
    tests=[[[2, 4, 3], [5, 6, 4]], [[0], [0]], [[9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9]], [[1], [9, 9, 9]],
           [[5], [5]], [[1, 8], [0]], [_digits(_rng, 100), _digits(_rng, 100)], [_digits(_rng, 37), _digits(_rng, 90)]],
))

# ---------------------------------------------------------------- 8. rotate
_big8 = _rand_list(_rng, 300)
PROBLEMS.append(dict(
    id="rotate-list-right",
    title="Rotate List",
    difficulty=2,
    tags=["linked list", "pointers"],
    fn="rotate_right",
    params=[["head", "list"], ["k", "int"]],
    returns="list",
    statement=r"""
Rotate a linked list to the **right by `k` places**: each rotation moves the last node to
the front. Return the new head.

`k` may be much larger than the length of the list. The list may be empty.
""",
    constraints=["0 ≤ number of nodes ≤ 500", "−1000 ≤ node.val ≤ 1000", "0 ≤ k ≤ 2 · 10⁹"],
    example_notes=["Two rotations: 5 moves to the front, then 4.", "Rotating 3 nodes 4 times is the same as rotating once."],
    hints=[
        "Rotating by the list length gives back the original list. What does that tell you about large `k`?",
        "After reducing `k` modulo the length L, the last `k` nodes move to the front, in order. Which node becomes the new tail?",
        "Find L and the old tail in one walk. New tail = node at index `L - k - 1`; new head = its `next`. Cut after the new tail and attach the old tail to the old head.",
    ],
    explanation=r"""
## Intuition

Rotating one place at a time costs O(L) per rotation (find the second-to-last node), and
`k` can be two billion. But rotation is periodic: L rotations restore the list, so only
`k mod L` matters. And a rotation by `k` simply means: **the last `k` nodes, in order, move
to the front**. That's one cut and one splice.

## Approach

1. Empty list → return it. Walk once to find the length `L` and the old `tail`.
2. `k %= L`. If `k == 0` the list is unchanged.
3. Walk to the **new tail** at index `L − k − 1`. The **new head** is `new_tail.next`.
4. `new_tail.next = None` (cut), `tail.next = head` (splice). Return the new head.

Trace for `1 → 2 → 3 → 4 → 5`, `k = 2`:

```text
L = 5, k = 2, new tail index = 5 − 2 − 1 = 2  (value 3)

1 → 2 → 3 ✂ 4 → 5          cut after 3
          4 → 5 → 1 → 2 → 3 → ∅    old tail 5 now points at old head 1
```

An equivalent trick: connect the tail to the head to form a **ring**, walk `L − k` steps,
and break the ring there.

**Rust.** We need two mutable positions (the new tail and the old tail) in one list,
which a single borrow chain can't provide at once. Do it sequentially with ownership:

1. walk a `&mut` cursor to the new tail and `take()` its `next`: we now own two separate
   lists, `head` (now ending at the new tail) and `new_head`;
2. walk a fresh `&mut` cursor to the end of `new_head` and set `tail.next = head`.

Each step holds only one mutable borrow, and `take()` is what separates the two lists.

## Complexity

- **Time:** O(L): one walk for the length, at most one more to the cut point.
- **Space:** O(1).

## Common mistakes

- **Not reducing `k`:** looping `k` times with k = 2·10⁹ is far too slow.
- **Modulo by zero:** compute `k % L` only after handling the empty list.
- **Forgetting to cut** (`new_tail.next = None`): the result is a cycle, and printing it
  never terminates.
- **Off-by-one on the new tail:** it's at index `L − k − 1` (0-based), i.e. `L − k − 1` steps
  from the head.

## Going further

- **Rotate an array** in place by reversing three times (whole, first k, rest). The list
  version is easier because splicing is O(1).
- **Rotate left** by k equals rotate right by `L − k mod L`.
""",
    solution=r'''def rotate_right(head, k):
    if not head:
        return head                 # nothing to rotate (and avoids k % 0)
    # One walk to find the length and the last node.
    length, tail = 1, head
    while tail.next:
        tail = tail.next
        length += 1
    # Rotating by a multiple of the length is a no-op.
    k %= length
    if k == 0:
        return head
    # The last k nodes move to the front. The node just before them becomes the tail.
    new_tail = head
    for _ in range(length - k - 1):
        new_tail = new_tail.next
    new_head = new_tail.next
    new_tail.next = None            # cut: otherwise we'd create a cycle
    tail.next = head                # splice the old front after the old tail
    return new_head
''',
    refs={
        "c": r"""struct ListNode* rotate_right(struct ListNode* head, long long k) {
    if (!head) return head;
    long long len = 1;
    struct ListNode* tail = head;
    while (tail->next) { tail = tail->next; len++; }
    k %= len;
    if (k == 0) return head;
    tail->next = head;                         // close the ring...
    struct ListNode* new_tail = head;
    for (long long i = 0; i < len - k - 1; i++) new_tail = new_tail->next;
    struct ListNode* new_head = new_tail->next;
    new_tail->next = NULL;                     // ...and break it at the new tail
    return new_head;
}
""",
        "cpp": r"""ListNode* rotateRight(ListNode* head, long long k) {
    if (!head) return head;
    long long len = 1;
    ListNode* tail = head;
    while (tail->next) { tail = tail->next; len++; }
    if ((k %= len) == 0) return head;
    ListNode* newTail = head;
    for (long long i = 0; i < len - k - 1; i++) newTail = newTail->next;
    ListNode* newHead = newTail->next;
    newTail->next = nullptr;
    tail->next = head;
    return newHead;
}
""",
        "rust": r"""pub fn rotate_right(mut head: Option<Box<ListNode>>, k: i64) -> Option<Box<ListNode>> {
    // Length with shared borrows.
    let mut len = 0i64;
    let mut p = head.as_ref();
    while let Some(n) = p {
        len += 1;
        p = n.next.as_ref();
    }
    if len == 0 || k % len == 0 {
        return head;
    }
    let k = k % len;
    // 1. Walk a &mut cursor to the new tail and take() what follows: two owned lists now.
    let mut cur = head.as_mut().unwrap();
    for _ in 0..len - k - 1 {
        cur = cur.next.as_mut().unwrap();
    }
    let mut new_head = cur.next.take(); // `head` now ends at the new tail
    // 2. Walk to the end of new_head (a separate list, so a separate borrow) and splice.
    let mut tail = new_head.as_mut().unwrap();
    while tail.next.is_some() {
        tail = tail.next.as_mut().unwrap();
    }
    tail.next = head; // move the old front list in after the old tail
    new_head
}
""",
    },
    tests=[[[1, 2, 3, 4, 5], 2], [[0, 1, 2], 4], [[], 0], [[], 5], [[1], 99], [[1, 2], 2],
           [[1, 2, 3, 4, 5, 6, 7], 2000000000], [_big8, 12345], [[1, 2, 3], 0]],
))

# ---------------------------------------------------------------- 9. reorder
PROBLEMS.append(dict(
    id="reorder-list-interleave",
    title="Reorder List",
    difficulty=2,
    tags=["linked list", "fast and slow pointers", "reversal"],
    fn="reorder_list",
    params=[["head", "list"]],
    returns="list",
    statement=r"""
A list `L0 → L1 → … → Ln−1 → Ln` must be reordered **in place** to

`L0 → Ln → L1 → Ln−1 → L2 → Ln−2 → …`

(first, last, second, second-to-last, …). Rearrange the existing nodes; don't create new
ones or just swap values. Return the head (which stays `L0`).
""",
    constraints=["0 ≤ number of nodes ≤ 1000", "−1000 ≤ node.val ≤ 1000"],
    example_notes=["1, then 4 (last), then 2, then 3.", "With 5 nodes the middle node 3 ends up last."],
    hints=[
        "The result interleaves the first half with the second half *read backwards*.",
        "Three steps you already know: find the middle, reverse the second half, merge two lists alternately.",
        "Split so the first half gets the extra node for odd lengths. Then: `a = first half, b = reversed second half`; while `b`: save both `next`s, set `a.next = b`, `b.next = a_next`, advance both.",
    ],
    explanation=r"""
## Intuition

Look at the target order `L0, Ln, L1, Ln−1, …`: the even positions are the first half
read forwards, and the odd positions are the second half read **backwards**. A singly
linked list can't be read backwards, so we reverse the second half, and the problem
becomes "interleave two lists". This problem is a composition of three earlier ones.

## Approach

1. **Split:** find the end of the first half with `slow`/`fast`
   (`while fast.next and fast.next.next`), so the first half has ⌈n/2⌉ nodes. Set
   `second = slow.next`, `slow.next = None`.
2. **Reverse** `second`.
3. **Weave:** with `a = head`, `b = reversed second`:
   `a_next, b_next = a.next, b.next; a.next = b; b.next = a_next; a, b = a_next, b_next`.

Trace for `1 → 2 → 3 → 4 → 5`:

```text
split:    1 → 2 → 3        4 → 5
reverse:  1 → 2 → 3        5 → 4
weave:    1 → 5 → 2 → 4 → 3
          a   b   a   b   a
```

The first half is never shorter than the second, so the weave loop runs while `b` is
non-empty and the first half's last node simply stays at the end.

**Rust.** Split by length: count `n`, walk a `&mut` cursor to node ⌈n/2⌉ and `take()` the
second half. Reverse it with the take loop. For the weave, hold a `&mut` cursor `a` into
the first half and **own** the reversed half `b`: pop its front node
(`let mut nb = b.take().unwrap(); b = nb.next.take();`), insert it after `a`
(`nb.next = a.next.take(); a.next = Some(nb);`), then move `a` two nodes forward. Owning
`b` while borrowing into `head` is fine: they're different lists.

## Complexity

- **Time:** O(n): three linear passes.
- **Space:** O(1). (Pushing all nodes into an array and relinking with two indices is a
  simpler O(n)-space solution.)

## Common mistakes

- **Not cutting the first half** (`slow.next = None`): the first half still leads into the
  second, and the weave creates a cycle.
- **Wrong split point for odd n:** if the second half gets the middle node, the result
  ends wrong (`1 5 2 4 3` vs `1 5 2 3 4`).
- **Losing nodes in the weave:** save *both* `a.next` and `b.next` before re-pointing
  either one.
- **Tiny lists:** 0, 1 and 2 nodes must come out unchanged.

## Going further

- **Odd-even list:** group odd-indexed nodes followed by even-indexed ones, another
  two-cursor weave.
- **Shuffle check:** the same split/reverse/compare skeleton powers Palindrome Linked List.
""",
    solution=r'''def reorder_list(head):
    if not head or not head.next:
        return head
    # 1. Find the end of the first half. With this loop condition slow stops at node
    #    ceil(n/2), so the first half is never shorter than the second.
    slow = fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
    second = slow.next
    slow.next = None                 # cut: the halves are now separate lists

    # 2. Reverse the second half so we can read it from the end.
    prev = None
    while second:
        nxt = second.next
        second.next = prev
        prev, second = second, nxt

    # 3. Weave: a (first half) and b (reversed second half), alternating.
    a, b = head, prev
    while b:
        a_next, b_next = a.next, b.next    # save both before re-pointing anything
        a.next = b
        b.next = a_next
        a, b = a_next, b_next
    return head
''',
    refs={
        "c": r"""struct ListNode* reorder_list(struct ListNode* head) {
    if (!head || !head->next) return head;
    struct ListNode *slow = head, *fast = head;
    while (fast->next && fast->next->next) { slow = slow->next; fast = fast->next->next; }
    struct ListNode* second = slow->next;
    slow->next = NULL;                                   // split

    struct ListNode* prev = NULL;                        // reverse the second half
    while (second) { struct ListNode* n = second->next; second->next = prev; prev = second; second = n; }

    struct ListNode *a = head, *b = prev;                // weave
    while (b) {
        struct ListNode *an = a->next, *bn = b->next;
        a->next = b;
        b->next = an;
        a = an;
        b = bn;
    }
    return head;
}
""",
        "cpp": r"""ListNode* reorderList(ListNode* head) {
    if (!head || !head->next) return head;
    ListNode *slow = head, *fast = head;
    while (fast->next && fast->next->next) { slow = slow->next; fast = fast->next->next; }
    ListNode* second = std::exchange(slow->next, nullptr);   // split and take the second half
    ListNode* prev = nullptr;
    while (second) second = std::exchange(second->next, std::exchange(prev, second));
    for (ListNode *a = head, *b = prev; b;) {
        ListNode* an = a->next;
        ListNode* bn = b->next;
        a->next = b;
        b->next = an;
        a = an;
        b = bn;
    }
    return head;
}
""",
        "rust": r"""pub fn reorder_list(mut head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    let mut len = 0;
    let mut p = head.as_ref();
    while let Some(n) = p {
        len += 1;
        p = n.next.as_ref();
    }
    if len < 3 {
        return head; // 0, 1 or 2 nodes: already in order
    }
    // 1. Split after ceil(len/2) nodes; `second` becomes its own owned list.
    let mut cur = head.as_mut().unwrap();
    for _ in 0..(len + 1) / 2 - 1 {
        cur = cur.next.as_mut().unwrap();
    }
    let mut second = cur.next.take();
    // 2. Reverse the second half.
    let mut b: Option<Box<ListNode>> = None;
    while let Some(mut n) = second {
        second = n.next.take();
        n.next = b;
        b = Some(n);
    }
    // 3. Weave: `a` is a &mut cursor into the first half; we own `b`.
    let mut a = head.as_mut();
    while let Some(node_a) = a {
        let mut nb = match b.take() {
            Some(nb) => nb,
            None => break, // second half exhausted
        };
        b = nb.next.take();             // pop nb off the front of b
        nb.next = node_a.next.take();   // nb -> rest of the first half
        node_a.next = Some(nb);         // node_a -> nb
        // Skip over the inserted node to the next first-half node.
        a = node_a.next.as_mut().unwrap().next.as_mut();
    }
    head
}
""",
    },
    tests=[[[1, 2, 3, 4]], [[1, 2, 3, 4, 5]], [[1]], [[]], [[1, 2]], [[1, 2, 3]], [[9, -9, 8, -8, 7, -7]],
           [_rand_list(_rng, 501)]],
))

# ---------------------------------------------------------------- 10. reverse k-group
_big10 = _rand_list(_rng, 600)
PROBLEMS.append(dict(
    id="reverse-nodes-in-k-group",
    title="Reverse Nodes in k-Group",
    difficulty=3,
    tags=["linked list", "reversal", "dummy head"],
    fn="reverse_k_group",
    params=[["head", "list"], ["k", "int"]],
    returns="list",
    statement=r"""
Reverse the nodes of a linked list **`k` at a time** and return the new head.

Split the list into consecutive groups of `k` nodes and reverse each group. If the number
of nodes isn't a multiple of `k`, the **leftover nodes at the end stay in their original
order**. Rearrange the nodes themselves (don't swap values), using O(1) extra memory.
""",
    constraints=["1 ≤ number of nodes ≤ 1000", "−1000 ≤ node.val ≤ 1000", "1 ≤ k ≤ 1000"],
    example_notes=["Groups [1,2] and [3,4] are reversed; the lone 5 stays.", "With k = 3, only [1,2,3] is a full group."],
    hints=[
        "Before reversing a group, check that it really has `k` nodes; otherwise stop.",
        "You need to remember the node **before** the group (to attach the reversed group) and the node **after** it (to attach to the group's new tail). A dummy head gives the first group a 'before' node.",
        "Reverse the group with the usual loop but start `prev` at the node after the group, so the reversed group's tail already points onward. Then `before.next = kth node`, and the new `before` is the group's old first node.",
    ],
    explanation=r"""
## Intuition

This is "reverse a linked list" applied repeatedly to slices, plus the bookkeeping to
stitch the slices together. Each reversed group must be connected on **both** sides:

```text
before → [g1 → g2 → g3] → after        becomes        before → [g3 → g2 → g1] → after
```

So for every group we track `before` (the node preceding it) and `after` (the node
following it). A dummy node in front of the head plays `before` for the first group, which
also takes care of the head changing.

## Approach

```text
group_prev = dummy
loop:
    kth = walk k steps from group_prev; if we fall off the end → stop (short leftover group)
    group_next = kth.next
    reverse the nodes from group_prev.next up to (not including) group_next,
        starting with prev = group_next  (so the reversed tail links onward)
    first = group_prev.next     (old first node, now the group's tail)
    group_prev.next = kth       (attach the reversed group)
    group_prev = first          (it is the 'before' of the next group)
```

Trace for `1 → 2 → 3 → 4 → 5`, `k = 2`:

```text
D → 1 → 2 → 3 → 4 → 5        group_prev = D, kth = 2, group_next = 3
D → 2 → 1 → 3 → 4 → 5        reversed [1,2]; group_prev = 1
D → 2 → 1 → 4 → 3 → 5        kth = 4, group_next = 5; reversed [3,4]; group_prev = 3
                             walk 2 from 3: only node 5, then ∅ → stop
result: 2 → 1 → 4 → 3 → 5
```

Starting the reversal with `prev = group_next` is the neat trick: the first node of the
group (which becomes the last) automatically ends up pointing at the rest of the list.

**Rust.** A `&mut` cursor `tail` (initially the dummy) marks the end of the processed part.
Each round:

1. peek ahead with shared borrows (`tail.next.as_ref()`) to check that k nodes exist;
2. `let mut rest = tail.next.take();` detaches everything after `tail`;
3. pop k nodes off `rest` and push each onto a new list `rev` (the take loop, k times);
4. `tail.next = rev`, advance `tail` k steps with `as_mut()`, then `tail.next = rest`.

Ownership makes the "connect both sides" bookkeeping explicit: `rest` literally holds the
`after` part while we work.

## Complexity

- **Time:** O(n). Each node is visited a constant number of times (counted once,
  reversed once).
- **Space:** O(1). (A recursive solution, reversing the first group and recursing on the
  rest, is shorter but uses O(n/k) stack.)

## Common mistakes

- **Reversing the leftover group:** check for k nodes *before* touching anything.
- **Losing `group_next`:** compute it before reversal; afterwards `kth.next` points
  backwards.
- **Advancing `group_prev` to `kth`:** after reversal `kth` is the group's *head*; the
  next `before` is the group's new *tail*, the old first node.
- **`k = 1`:** every group is a single node; the list must come back unchanged.

## Going further

- **Swap nodes in pairs** is the `k = 2` special case.
- **Reverse alternate groups** (reverse k, skip k, …) needs only a small change: after
  reversing, walk `group_prev` an extra k nodes.
""",
    solution=r'''def reverse_k_group(head, k):
    dummy = ListNode(0, head)
    group_prev = dummy           # node just before the current group
    while True:
        # Find the k-th node of this group; if the list runs out, the remaining
        # nodes are a short group and stay as they are.
        kth = group_prev
        for _ in range(k):
            kth = kth.next
            if kth is None:
                return dummy.next
        group_next = kth.next    # first node after the group (save before reversing)

        # Reverse the group. prev starts at group_next, so the group's first node
        # (which becomes its last) ends up pointing at the rest of the list.
        prev, cur = group_next, group_prev.next
        while cur is not group_next:
            nxt = cur.next
            cur.next = prev
            prev, cur = cur, nxt

        # Stitch: before -> new group head (kth). The old first node is now the
        # group's tail and serves as 'before' for the next group.
        first = group_prev.next
        group_prev.next = kth
        group_prev = first
''',
    refs={
        "c": r"""struct ListNode* reverse_k_group(struct ListNode* head, long long k) {
    struct ListNode dummy = {0, head};
    struct ListNode* group_prev = &dummy;
    for (;;) {
        struct ListNode* kth = group_prev;
        for (long long i = 0; i < k && kth; i++) kth = kth->next;
        if (!kth) break;                                   // fewer than k nodes left
        struct ListNode* group_next = kth->next;
        struct ListNode *prev = group_next, *cur = group_prev->next;
        while (cur != group_next) {                        // reverse within the group
            struct ListNode* nxt = cur->next;
            cur->next = prev;
            prev = cur;
            cur = nxt;
        }
        struct ListNode* first = group_prev->next;         // becomes the group's tail
        group_prev->next = kth;
        group_prev = first;
    }
    return dummy.next;
}
""",
        "cpp": r"""ListNode* reverseKGroup(ListNode* head, long long k) {
    ListNode dummy(0, head);
    ListNode* groupPrev = &dummy;
    while (true) {
        ListNode* kth = groupPrev;
        for (long long i = 0; i < k && kth; i++) kth = kth->next;
        if (!kth) break;
        ListNode* groupNext = kth->next;
        ListNode *prev = groupNext, *cur = groupPrev->next;
        while (cur != groupNext) cur = std::exchange(cur->next, std::exchange(prev, cur));
        ListNode* first = std::exchange(groupPrev->next, kth);  // attach; remember old first
        groupPrev = first;
    }
    return dummy.next;
}
""",
        "rust": r"""pub fn reverse_k_group(head: Option<Box<ListNode>>, k: i64) -> Option<Box<ListNode>> {
    let k = k as usize;
    let mut dummy = Box::new(ListNode { val: 0, next: head });
    let mut tail = &mut dummy; // last node of the already-processed prefix
    loop {
        // 1. Are there k more nodes? Peek with shared borrows only.
        let mut probe = tail.next.as_ref();
        let mut count = 0;
        while count < k {
            match probe {
                Some(n) => {
                    probe = n.next.as_ref();
                    count += 1;
                }
                None => break,
            }
        }
        if count < k {
            break; // short leftover group: leave it untouched
        }
        // 2. Detach everything after `tail`; we now own it in `rest`.
        let mut rest = tail.next.take();
        // 3. Pop k nodes off `rest`, pushing each onto the front of `rev`.
        let mut rev: Option<Box<ListNode>> = None;
        for _ in 0..k {
            let mut node = rest.unwrap(); // safe: we counted k nodes
            rest = node.next.take();
            node.next = rev;
            rev = Some(node);
        }
        // 4. Attach the reversed group, move `tail` to its last node, re-attach the rest.
        tail.next = rev;
        for _ in 0..k {
            tail = tail.next.as_mut().unwrap();
        }
        tail.next = rest;
    }
    dummy.next
}
""",
    },
    tests=[[[1, 2, 3, 4, 5], 2], [[1, 2, 3, 4, 5], 3], [[1, 2, 3, 4, 5], 1], [[1, 2, 3, 4, 5], 5],
           [[1, 2], 3], [[1], 1], [list(range(1, 13)), 4], [_big10, 7], [_big10, 600]],
))

# ---------------------------------------------------------------- 11. sort list
PROBLEMS.append(dict(
    id="sort-linked-list-merge-sort",
    title="Sort List",
    difficulty=3,
    tags=["linked list", "merge sort", "divide and conquer"],
    fn="sort_list",
    params=[["head", "list"]],
    returns="list",
    statement=r"""
Sort a linked list in **ascending** order and return its head, in **O(n log n)** time.
Rearrange the nodes themselves; don't copy the values into an array.

The largest test has a few thousand nodes, so an O(n²) insertion sort will be noticeably
slow.
""",
    constraints=["0 ≤ number of nodes ≤ 5000", "−10⁵ ≤ node.val ≤ 10⁵"],
    example_notes=["Sorted ascending.", "Negative values and zero sort normally."],
    hints=[
        "Which O(n log n) sort needs no random access? Quicksort and heapsort like indices; one classic sort only ever scans forward.",
        "Merge sort: split the list into two halves, sort each recursively, merge the two sorted halves (you solved that merge earlier in this track).",
        "Split with fast/slow pointers using `while fast.next and fast.next.next` so the left half is never empty for lists of 2+ nodes, and cut with `slow.next = None`. Base case: 0 or 1 node.",
    ],
    explanation=r"""
## Intuition

Linked lists have O(1) splicing but no random access. That rules out the usual tricks of
quicksort (partitioning with indices from both ends) and heapsort (an array-shaped heap).
**Merge sort** fits perfectly: splitting is "find the middle and cut", and merging two
sorted lists is a forward-only scan that needs no extra memory, because nodes are relinked
rather than copied. On linked lists, merge sort is the natural O(n log n) sort.

## Approach

```text
sort(head):
    if head is None or head.next is None: return head      # 0 or 1 node: sorted
    mid  = end of the first half (fast/slow)
    right = mid.next; mid.next = None                       # cut into two lists
    return merge(sort(head), sort(right))
```

`merge` is exactly Merge Two Sorted Lists: a dummy head, a tail pointer, take the smaller
front node each time, attach the leftover.

Trace on `4 → 2 → 1 → 3`:

```text
            [4 2 1 3]
           /         \
       [4 2]         [1 3]          split at the middle
       /   \         /   \
     [4]   [2]     [1]   [3]        base cases
       \   /         \   /
       [2 4]         [1 3]          merge
           \         /
            [1 2 3 4]               merge
```

**The split must make progress.** Using `while fast.next and fast.next.next` with
`slow = fast = head` makes `slow` the *first* middle, so a 2-node list splits into 1 + 1.
With the other condition (`while fast and fast.next`), a 2-node list's `slow` would be the
second node; cutting after it leaves the halves as 2 + 0 and the recursion never shrinks:
infinite recursion.

**Rust.** Count the length, walk a `&mut` cursor `len/2 − 1` steps, and `take()` the
second half: two owned lists. Recurse on each (both are moved into the calls) and merge
with the take-based merge from earlier. Ownership guarantees no node ends up in both halves.

## Complexity

- **Time:** O(n log n): log n levels of splitting, O(n) total merge work per level.
- **Space:** O(log n) recursion depth; merging itself needs O(1) extra.

**Going fully O(1) space:** *bottom-up* merge sort skips recursion. Merge runs of size 1
into runs of size 2, then 4, 8, …, walking the list each round, cutting off two runs with a
helper `split(head, size)` and appending their merge to the growing result. Same O(n log n)
time, constant extra space.

## Common mistakes

- **Infinite recursion on 2-node lists** from the wrong middle (see above).
- **Forgetting the cut** (`mid.next = None`): the left half still contains the right half.
- **Recursive merge** on long lists: depth O(n) per merge, a stack overflow risk in C/C++/Rust.
  Use the iterative dummy-head merge.
- **Insertion sort** works and is fine for small n, but is O(n²): a few thousand nodes
  means millions of steps.

## Going further

- **Bottom-up merge sort** as described above.
- **Merge k sorted lists** with a heap, then "sort a list by merging k sorted runs" is the
  basis of external sorting for data that doesn't fit in memory.
- Many standard libraries sort linked lists with merge sort, e.g. `std::list::sort` in C++.
""",
    solution=r'''def sort_list(head):
    # Base case: zero or one node is already sorted.
    if head is None or head.next is None:
        return head

    # Find the end of the first half. This loop condition picks the FIRST middle,
    # so a 2-node list splits 1 + 1 and the recursion always shrinks.
    slow, fast = head, head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
    right = slow.next
    slow.next = None                  # cut into two independent lists

    left = sort_list(head)            # sort each half recursively
    right = sort_list(right)

    # Merge two sorted lists by relinking nodes (no new nodes, no recursion).
    dummy = ListNode(0)
    tail = dummy
    while left and right:
        if left.val <= right.val:     # '<=' keeps equal values in order (stable)
            tail.next, left = left, left.next
        else:
            tail.next, right = right, right.next
        tail = tail.next
    tail.next = left if left else right
    return dummy.next
''',
    refs={
        "c": r"""static struct ListNode* merge(struct ListNode* a, struct ListNode* b) {
    struct ListNode dummy = {0, NULL};
    struct ListNode* tail = &dummy;
    while (a && b) {                                  // iterative: no deep recursion
        if (a->val <= b->val) { tail->next = a; a = a->next; }
        else                  { tail->next = b; b = b->next; }
        tail = tail->next;
    }
    tail->next = a ? a : b;
    return dummy.next;
}

struct ListNode* sort_list(struct ListNode* head) {
    if (!head || !head->next) return head;
    struct ListNode *slow = head, *fast = head;
    while (fast->next && fast->next->next) { slow = slow->next; fast = fast->next->next; }
    struct ListNode* right = slow->next;
    slow->next = NULL;                                // cut
    return merge(sort_list(head), sort_list(right));  // recursion depth ~ log2(n)
}
""",
        "cpp": r"""static ListNode* merge(ListNode* a, ListNode* b) {
    ListNode dummy;
    ListNode* tail = &dummy;
    while (a && b) {
        ListNode*& src = a->val <= b->val ? a : b;   // reference to the list we take from
        tail = tail->next = src;
        src = src->next;
    }
    tail->next = a ? a : b;
    return dummy.next;
}

ListNode* sortList(ListNode* head) {
    if (!head || !head->next) return head;
    ListNode *slow = head, *fast = head;
    while (fast->next && fast->next->next) { slow = slow->next; fast = fast->next->next; }
    ListNode* right = std::exchange(slow->next, nullptr);   // cut and keep the second half
    return merge(sortList(head), sortList(right));
}
""",
        "rust": r"""fn merge(mut a: Option<Box<ListNode>>, mut b: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    let mut dummy = Box::new(ListNode::new(0));
    let mut tail = &mut dummy;
    while let (Some(x), Some(y)) = (a.as_ref(), b.as_ref()) {
        let src = if x.val <= y.val { &mut a } else { &mut b };
        let mut node = src.take().unwrap();   // detach the smaller front node
        *src = node.next.take();              // its list continues from the next node
        tail.next = Some(node);
        tail = tail.next.as_mut().unwrap();
    }
    tail.next = a.or(b);
    dummy.next
}

pub fn sort_list(mut head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    // Length with shared borrows.
    let mut len = 0;
    let mut p = head.as_ref();
    while let Some(n) = p {
        len += 1;
        p = n.next.as_ref();
    }
    if len < 2 {
        return head;
    }
    // Walk to the last node of the first half (len/2 nodes) and take() the rest:
    // head and right are now two separately-owned lists.
    let mut cur = head.as_mut().unwrap();
    for _ in 0..len / 2 - 1 {
        cur = cur.next.as_mut().unwrap();
    }
    let right = cur.next.take();
    // Both halves are moved into the recursive calls, then merged.
    merge(sort_list(head), sort_list(right))
}
""",
    },
    tests=[[[4, 2, 1, 3]], [[-1, 5, 3, 4, 0]], [[]], [[1]], [[2, 1]], [[3, 3, 1, 1, 2, 2]],
           [list(range(1, 201))], [list(range(200, 0, -1))],
           [_rand_list(_rng, 4000, -100000, 100000)]],
))
