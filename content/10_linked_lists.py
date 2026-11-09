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
