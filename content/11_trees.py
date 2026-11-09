"""Track 11: Trees & BSTs."""
import random

TRACK = dict(
    id="trees",
    title="Trees & BSTs",
    order=11,
    icon="🌳",
    blurb="Recursion's natural habitat: traversals, depth, paths, and binary search trees.",
    intro=r"""
A **binary tree** is a set of nodes where each node holds a value and at most two
children, `left` and `right`. Exactly one node, the **root**, has no parent. A node with
no children is a **leaf**. Every problem in this track hands you a root (possibly
`None`/`NULL`) and asks you to compute something about the whole structure.

```text
              1            depth 0  (root)
            /   \
           2     3         depth 1
          / \     \
         4   5     6       depth 2  (4, 5, 6 are leaves)
```

## Vocabulary

| term | meaning (in the tree above) |
|---|---|
| **depth** of a node | edges from the root to it: depth(5) = 2 |
| **height** of a tree | number of *nodes* on the longest root-to-leaf path: 3 (some books count edges, read each statement carefully) |
| **subtree** | a node plus all its descendants: the subtree at 2 is {2, 4, 5} |
| **balanced** | at every node, left and right heights differ by at most 1 |
| **level order** | the serialization used by the tests: `[1,2,3,4,5,null,6]` |

In the level-order format `null` marks a missing child, so `[1,null,2]` is a root `1`
whose only child is a *right* child `2`. Trailing `null`s are dropped.

## Recursion is the default tool

A tree is defined recursively (a node plus two smaller trees), so most answers are too.
The recipe is always the same:

1. **Base case**: what is the answer for the empty tree (`None`)?
2. **Trust the recursion**: assume `f(left)` and `f(right)` are already correct.
3. **Combine** them with the current node's value.

```python
def size(node):
    if node is None:            # base case: an empty tree has 0 nodes
        return 0
    return 1 + size(node.left) + size(node.right)   # combine
```

Each node is visited once, so this is **O(n) time**. The call stack holds one frame per
level, so space is **O(h)** where `h` is the height: O(log n) for a balanced tree but
O(n) for a degenerate "linked list" tree. That is why some problems want an iterative
version with an explicit stack.

A powerful variant is **"return one thing, record another"**: the helper returns what
the *parent* needs (e.g. a height) while updating a global best (e.g. a diameter or path
sum) that may bend through the current node. You will use it in Diameter, Balanced, and
Maximum Path Sum.

## Depth-first orders

DFS goes as deep as possible before backing up. The three classic orders differ only
in *when* you record the current node relative to its subtrees:

```text
              1
            /   \           preorder  (node, L, R): 1 2 4 5 3 6
           2     3          inorder   (L, node, R): 4 2 5 1 3 6
          / \     \         postorder (L, R, node): 4 5 2 6 3 1
         4   5     6
```

- **Preorder** sees a node *before* its children: good for copying or serializing.
- **Inorder** of a BST yields the values **sorted**.
- **Postorder** sees a node *after* its children: good for anything that needs the
  children's answers first (heights, deleting a tree, evaluating an expression tree).

The iterative form replaces the call stack with your own:

```python
def inorder(root):
    out, stack, cur = [], [], root
    while cur or stack:
        while cur:                 # dive left, remembering the path
            stack.append(cur); cur = cur.left
        cur = stack.pop()          # leftmost unvisited node
        out.append(cur.val)
        cur = cur.right            # then do its right subtree
    return out
```

## Breadth-first: level by level with a queue

BFS visits nodes in order of depth. Put the root in a FIFO queue; repeatedly pop a node
and push its children. To know where one level ends, **snapshot the queue length** at
the start of each round:

```text
queue: [1]          -> level [1]       push 2, 3
queue: [2, 3]       -> level [2, 3]    push 4, 5, 6
queue: [4, 5, 6]    -> level [4, 5, 6]
```

```python
from collections import deque
q = deque([root])
while q:
    for _ in range(len(q)):      # exactly the nodes of the current level
        node = q.popleft()
        ...
        if node.left:  q.append(node.left)
        if node.right: q.append(node.right)
```

Use `deque` in Python (`list.pop(0)` is O(n)), `std::queue` in C++, `VecDeque` in Rust.

## Binary search trees

A **BST** adds an ordering invariant: for every node, *all* values in its left subtree
are smaller and *all* values in its right subtree are larger. (Not just the immediate
children; that is the classic trap in "Validate BST".)

```text
            8
          /   \          search 6:  8 -> go left -> 3 -> go right -> 6  found
         3     10        each step discards a whole subtree,
        / \      \       so search costs O(h)
       1   6      14
```

Consequences you will exploit: search, insert and LCA cost O(h); the inorder traversal
is sorted, so "k-th smallest" is "k-th node of an inorder walk".

## Language mechanics

**C** gives you `struct TreeNode { long long val; struct TreeNode* left, *right; }`.
Allocate new nodes with `malloc` and remember that `NULL` is the empty tree.
**C++** has the same shape with a constructor: `new TreeNode(5)`.

**Rust** is the interesting one. A child is `Option<Rc<RefCell<TreeNode>>>`:

- `Option` because the child may be absent.
- `Rc` (reference counted pointer) so the harness and your code can share nodes.
  `Rc::clone(&rc)` or `rc.clone()` copies the **pointer**, not the subtree: it is O(1).
- `RefCell` moves borrow checking to runtime: `rc.borrow()` gives a shared `Ref`,
  `rc.borrow_mut()` a mutable `RefMut`. Holding a `borrow_mut` while someone else
  borrows the same node panics.

Idioms that keep the code readable:

```rust
use std::rc::Rc;
use std::cell::RefCell;

// Take the child by reference so you never move out of the tree.
fn height(node: &Option<Rc<RefCell<TreeNode>>>) -> i64 {
    match node {
        None => 0,
        Some(rc) => {
            let n = rc.borrow();                  // Ref<TreeNode>, read-only
            1 + height(&n.left).max(height(&n.right))
        }
    }
}
// node.as_ref() turns &Option<Rc<..>> into Option<&Rc<..>>, handy with map/and_then:
// let left_val = n.left.as_ref().map(|l| l.borrow().val);
```

Write helpers that take `&Option<...>`; clone an `Rc` only when you must store it (a
queue or stack). Build a new node with `Rc::new(RefCell::new(TreeNode::new(v)))`.
""",
)

# ---------------------------------------------------------------- test helpers


class _N:
    __slots__ = ("val", "left", "right")

    def __init__(self, v, left=None, right=None):
        self.val, self.left, self.right = v, left, right


def _ser(root):
    """Node structure -> LeetCode level order list."""
    out, q, i = [], [root], 0
    while i < len(q):
        n = q[i]
        i += 1
        if n is None:
            out.append(None)
        else:
            out.append(n.val)
            q.append(n.left)
            q.append(n.right)
    while out and out[-1] is None:
        out.pop()
    return out


def _de(a):
    """Level order list -> node structure."""
    if not a or a[0] is None:
        return None
    root = _N(a[0])
    q, qi, i = [root], 0, 1
    while i < len(a):
        node = q[qi]
        qi += 1
        if a[i] is not None:
            node.left = _N(a[i])
            q.append(node.left)
        i += 1
        if i < len(a) and a[i] is not None:
            node.right = _N(a[i])
            q.append(node.right)
        i += 1
    return root


def _rand_root(rng, vals):
    """Random shape: each new node takes a random free child slot."""
    if not vals:
        return None
    root = _N(vals[0])
    slots = [(root, 0), (root, 1)]
    for v in vals[1:]:
        i = rng.randrange(len(slots))
        node, side = slots[i]
        slots[i] = slots[-1]
        slots.pop()
        c = _N(v)
        if side == 0:
            node.left = c
        else:
            node.right = c
        slots += [(c, 0), (c, 1)]
    return root


def _rand_tree(rng, n, lo=-100, hi=100):
    return _ser(_rand_root(rng, [rng.randint(lo, hi) for _ in range(n)]))


def _bst_root(vals):
    root = None
    for v in vals:
        if root is None:
            root = _N(v)
            continue
        cur = root
        while True:
            if v < cur.val:
                if cur.left is None:
                    cur.left = _N(v)
                    break
                cur = cur.left
            else:
                if cur.right is None:
                    cur.right = _N(v)
                    break
                cur = cur.right
    return root


def _rand_bst(rng, n, lo=-1000, hi=1000):
    vals = rng.sample(range(lo, hi + 1), n)
    return _ser(_bst_root(vals))


def _balanced_root(vals):
    if not vals:
        return None
    m = len(vals) // 2
    return _N(vals[m], _balanced_root(vals[:m]), _balanced_root(vals[m + 1:]))


def _chain(vals, side):
    """Degenerate tree. side: 'L', 'R' or 'Z' (zig-zag)."""
    root = None
    for i, v in enumerate(reversed(vals)):
        s = side if side != "Z" else ("L" if i % 2 else "R")
        root = _N(v, root, None) if s == "L" else _N(v, None, root)
    return _ser(root)


def _copy(n):
    return None if n is None else _N(n.val, _copy(n.left), _copy(n.right))


def _mirror(n):
    return None if n is None else _N(n.val, _mirror(n.right), _mirror(n.left))


def _nodes(n):
    out, st = [], [n] if n else []
    while st:
        x = st.pop()
        out.append(x)
        if x.left:
            st.append(x.left)
        if x.right:
            st.append(x.right)
    return out


def _leaf_sums(n, acc=0):
    if n is None:
        return []
    acc += n.val
    if not n.left and not n.right:
        return [acc]
    return _leaf_sums(n.left, acc) + _leaf_sums(n.right, acc)


_R = random.Random(1111)
_EX = [1, 2, 3, 4, 5, None, 6]  # the intro tree

RS = "use std::rc::Rc;\nuse std::cell::RefCell;\n"

PROBLEMS = []

# ---------------------------------------------------------------- 1. max depth

PROBLEMS.append(dict(
    id="tree-max-depth",
    title="Maximum Depth of Binary Tree",
    difficulty=1,
    tags=["tree", "recursion", "dfs"],
    fn="max_depth",
    params=[["root", "tree"]],
    returns="int",
    statement=r"""
Given the `root` of a binary tree, return its **maximum depth**: the number of nodes on
the longest path from the root down to any leaf.

The empty tree has depth `0`; a single node has depth `1`.
""",
    constraints=["0 ≤ number of nodes ≤ 800", "-100 ≤ node.val ≤ 100"],
    example_notes=[
        "The longest root-to-leaf paths are 1→2→4, 1→2→5 and 1→3→6, each with 3 nodes.",
        "A root with only a right child: two nodes on the path.",
    ],
    hints=[
        "What is the depth of an empty tree? Of a tree whose subtrees have depths 2 and 5?",
        "depth(node) = 1 + max(depth(node.left), depth(node.right)).",
        "Alternatively, BFS level by level and count the levels.",
    ],
    explanation=r"""
## Intuition

"Longest path from root to a leaf" sounds like a search, but think recursively: the
longest path through the root must continue into whichever subtree is *deeper*. So the
depth of a tree is one (for the root) plus the larger of its two subtree depths. That is
the whole algorithm.

## Approach

1. If `root` is `None`, return 0. This base case also handles single-child nodes: the
   missing side contributes 0 and the other side wins the `max`.
2. Otherwise recurse on both children and return `1 + max(left, right)`.

Trace on `[1,2,3,4,5,null,6]`:

```text
depth(4)=1  depth(5)=1  depth(6)=1          (leaves: 1 + max(0, 0))
depth(2)=1+max(1,1)=2   depth(3)=1+max(0,1)=2
depth(1)=1+max(2,2)=3
```

The answers flow **up** the tree: this is a postorder computation, because a node needs
its children's answers before it can produce its own.

The iterative BFS alternative counts levels: each pass of the `for _ in range(len(q))`
loop consumes exactly one level, so the number of passes is the depth.

## Complexity

- **Time O(n)**: each node is visited exactly once and does O(1) work.
- **Space O(h)** for the recursion stack, where `h` is the height. That is O(log n) for a
  balanced tree and O(n) for a chain (one of the tests is an 800-node chain). BFS uses
  O(w) where `w` is the widest level instead.

## Common mistakes

- **Counting edges instead of nodes.** This problem counts nodes; a single node has depth 1.
  If you return `-1` for the empty tree you are computing height in edges.
- **Forgetting the empty tree.** `root.left` on `None` crashes; check first.
- **Recursing only when a child exists** and then returning 0 for a leaf: the leaf must
  contribute 1.
- **C**: writing `max` as a macro `#define MAX(a,b) ((a)>(b)?(a):(b))` and passing the
  recursive calls into it evaluates them twice, turning O(n) into exponential time. Store
  the results in variables first.

## Going further

*Minimum* depth looks symmetric but is not: a node with one child is **not** a leaf, so
`1 + min(left, right)` returns the wrong answer when one side is empty. Try handling that
case explicitly, or use BFS and stop at the first leaf you meet.
""",
    solution=r'''
def max_depth(root):
    # Base case: an empty tree contributes no nodes to any path.
    if root is None:
        return 0
    # Trust the recursion: these are the depths of the two subtrees.
    left = max_depth(root.left)
    right = max_depth(root.right)
    # The longest path through this node continues into the deeper subtree,
    # and this node itself adds one more to the count.
    return 1 + max(left, right)
''',
    refs={
        "c": r'''
long long max_depth(struct TreeNode* root) {
    if (root == NULL) return 0;              /* empty tree */
    /* Evaluate each side once; a MAX macro would recurse twice per side. */
    long long l = max_depth(root->left);
    long long r = max_depth(root->right);
    return 1 + (l > r ? l : r);
}
''',
        "cpp": r'''
long long maxDepth(TreeNode* root) {
    if (!root) return 0;                     // empty tree has depth 0
    return 1 + max(maxDepth(root->left), maxDepth(root->right));
}
''',
        "rust": RS + r'''
// Borrow the child slot instead of moving it out of the tree.
fn depth(node: &Option<Rc<RefCell<TreeNode>>>) -> i64 {
    match node {
        None => 0,
        Some(rc) => {
            let n = rc.borrow();             // runtime-checked shared borrow
            1 + depth(&n.left).max(depth(&n.right))
        }
    }
}

pub fn max_depth(root: Option<Rc<RefCell<TreeNode>>>) -> i64 {
    depth(&root)
}
''',
    },
    tests=[
        [_EX], [[1, None, 2]], [[]], [[0]],
        [_chain(list(range(800)), "L")],
        [_chain(list(range(50)), "Z")],
        [_ser(_balanced_root(list(range(255))))],
        [_rand_tree(_R, 300)], [_rand_tree(_R, 600)],
    ],
))

# ---------------------------------------------------------------- 2-4. traversals

_TRAV_TESTS = [
    [_EX], [[]], [[1, None, 2, 3]], [[7]],
    [_chain([1, 2, 3, 4, 5], "L")], [_chain([1, 2, 3, 4, 5], "R")],
    [[5, 3, 8, 1, 4, 7, 9, None, 2, None, None, 6]],
    [_rand_tree(_R, 25)], [_rand_tree(_R, 500)],
]

PROBLEMS.append(dict(
    id="tree-inorder-traversal",
    title="Binary Tree Inorder Traversal",
    difficulty=1,
    tags=["tree", "dfs", "stack"],
    fn="inorder_traversal",
    params=[["root", "tree"]],
    returns="int[]",
    statement=r"""
Return the values of a binary tree in **inorder**: for every node, first its whole left
subtree, then the node itself, then its whole right subtree.

The recursive version is three lines; once it works, try the **iterative** version with
an explicit stack (it is the one interviewers ask for).
""",
    constraints=["0 ≤ number of nodes ≤ 500", "-100 ≤ node.val ≤ 100"],
    example_notes=[
        "Left subtree of 1 gives 4 2 5, then 1, then the right subtree gives 3 6.",
        "The empty tree has an empty traversal.",
    ],
    hints=[
        "Recursive: visit(left); record(node); visit(right).",
        "Iteratively, the stack must remember the nodes whose left subtree you are still exploring.",
        "Loop: push nodes while walking left; pop one, record it, then move to its right child and repeat.",
    ],
    explanation=r"""
## Intuition

"Inorder" literally means *the node goes in the middle*: left, node, right. The
recursive definition maps one-to-one onto code. The iterative version is about
simulating what the call stack does for you.

## Approach

**Recursive.** `go(node)`: if `node` is empty return; `go(node.left)`; append
`node.val`; `go(node.right)`.

**Iterative.** Keep a pointer `cur` and a stack of "nodes I have descended past but not
yet recorded".

1. While `cur` exists: push it and move to `cur.left` (dive left).
2. Pop the top: it has no unvisited left subtree, so record it.
3. Set `cur` to its right child and go back to step 1.
4. Stop when `cur` is empty *and* the stack is empty.

Trace on the intro tree:

```text
              1
            /   \
           2     3
          / \     \
         4   5     6

action               stack      out
dive 1,2,4           [1,2,4]
pop 4, cur=None      [1,2]      4
pop 2, cur=5         [1]        4 2
dive 5; pop 5        [1]        4 2 5
pop 1, cur=3         []         4 2 5 1
dive 3; pop 3, cur=6 []         4 2 5 1 3
dive 6; pop 6        []         4 2 5 1 3 6
```

## Complexity

- **Time O(n)**: each node is pushed and popped exactly once.
- **Space O(h)** for the stack (explicit or implicit), O(n) worst case for a chain.

## Common mistakes

- **Loop condition `while stack`** alone: at the start the stack is empty but `cur` is
  the root, and after popping the root the stack can be empty while its right subtree is
  still pending. You need `while cur or stack`.
- **Pushing the right child onto the stack** (that is the preorder trick). In inorder you
  *move* to the right child and dive from there.
- **C**: you return a malloc-ed array and must set `*returnSize`. Either count the nodes
  first or grow with `realloc`; never return a pointer to a local array.

## Going further

*Morris traversal* achieves O(1) extra space by temporarily threading each node's
inorder predecessor's `right` pointer back to the node, then undoing it. It is a
beautiful trick that mutates the tree during the walk and restores it afterwards.
""",
    solution=r'''
def inorder_traversal(root):
    out = []
    stack = []        # nodes whose left subtree we are exploring; not yet recorded
    cur = root
    # Keep going while there is a subtree to dive into OR a pending ancestor.
    while cur is not None or stack:
        # Dive as far left as possible, remembering the path back up.
        while cur is not None:
            stack.append(cur)
            cur = cur.left
        # The top of the stack has no unvisited left subtree: its turn now.
        node = stack.pop()
        out.append(node.val)
        # Its right subtree comes next, after which we resume with ancestors.
        cur = node.right
    return out
''',
    refs={
        "c": r'''
static void walk(struct TreeNode* n, long long** out, int* len, int* cap) {
    if (!n) return;
    walk(n->left, out, len, cap);
    if (*len == *cap) {                      /* grow the output like a vector */
        *cap *= 2;
        *out = realloc(*out, sizeof(long long) * (size_t)*cap);
    }
    (*out)[(*len)++] = n->val;
    walk(n->right, out, len, cap);
}

long long* inorder_traversal(struct TreeNode* root, int* returnSize) {
    int cap = 16, len = 0;
    long long* out = malloc(sizeof(long long) * (size_t)cap);
    walk(root, &out, &len, &cap);
    *returnSize = len;                       /* the caller needs the length */
    return out;
}
''',
        "cpp": r'''
vector<long long> inorderTraversal(TreeNode* root) {
    vector<long long> out;
    stack<TreeNode*> st;                     // ancestors waiting for their turn
    TreeNode* cur = root;
    while (cur || !st.empty()) {
        while (cur) { st.push(cur); cur = cur->left; }   // dive left
        cur = st.top(); st.pop();
        out.push_back(cur->val);             // left subtree done: record node
        cur = cur->right;                    // then handle the right subtree
    }
    return out;
}
''',
        "rust": RS + r'''
pub fn inorder_traversal(root: Option<Rc<RefCell<TreeNode>>>) -> Vec<i64> {
    let mut out = Vec::new();
    // The stack owns Rc clones (cheap pointer copies), not whole subtrees.
    let mut stack: Vec<Rc<RefCell<TreeNode>>> = Vec::new();
    let mut cur = root;
    while cur.is_some() || !stack.is_empty() {
        while let Some(node) = cur {
            cur = node.borrow().left.clone();    // step left first...
            stack.push(node);                    // ...then remember the node
        }
        let node = stack.pop().unwrap();
        out.push(node.borrow().val);
        cur = node.borrow().right.clone();
    }
    out
}
''',
    },
    tests=_TRAV_TESTS,
))

PROBLEMS.append(dict(
    id="tree-preorder-traversal",
    title="Binary Tree Preorder Traversal",
    difficulty=1,
    tags=["tree", "dfs", "stack"],
    fn="preorder_traversal",
    params=[["root", "tree"]],
    returns="int[]",
    statement=r"""
Return the values of a binary tree in **preorder**: for every node, first the node
itself, then its whole left subtree, then its whole right subtree.
""",
    constraints=["0 ≤ number of nodes ≤ 500", "-100 ≤ node.val ≤ 100"],
    example_notes=[
        "1 first, then the left subtree (2 4 5), then the right subtree (3 6).",
        "Nothing to visit.",
    ],
    hints=[
        "Recursive: record(node); visit(left); visit(right).",
        "Iteratively, a stack works if you pop a node, record it, then push its children.",
        "A stack is last-in-first-out: push the right child *before* the left one so the left is processed first.",
    ],
    explanation=r"""
## Intuition

Preorder records a node the moment you *arrive* at it, before looking at its children.
That makes it the order you would use to copy or serialize a tree: a parent always
appears before its descendants, so whoever reads the list can rebuild top-down.

## Approach

Recursively it is `out.append(node.val); go(left); go(right)`.

Iteratively it is even simpler than inorder, because a node is finished the moment it
is popped:

1. Push the root (if any).
2. Pop a node, record it.
3. Push its **right** child, then its **left** child. The left is on top, so it is
   processed next, and the entire left subtree is exhausted before the right child
   surfaces again.

```text
stack        pop  out             push
[1]          1    1               3, 2
[3, 2]       2    1 2             5, 4
[3, 5, 4]    4    1 2 4           -
[3, 5]       5    1 2 4 5         -
[3]          3    1 2 4 5 3       6
[6]          6    1 2 4 5 3 6     -
```

## Complexity

- **Time O(n)**: one push and one pop per node.
- **Space O(h)** for recursion; the explicit stack holds at most about `h + (pending
  right siblings)` entries, which is O(n) in the worst case and O(log n) for balanced trees.

## Common mistakes

- **Pushing left before right**: you get node, right, left (a "reverse postorder" order).
- **Pushing `None` children**: in Python it works if you skip them when popped, but in
  C/C++ dereferencing a null pointer crashes. Check before pushing.
- **Rust**: you cannot push `n.left` (that would move out of a borrowed node); push
  `Rc::clone(l)` from `if let Some(l) = &n.left`.

## Going further

Preorder plus the `null` markers is a complete serialization: `1,2,4,#,#,5,#,#,3,#,6,#,#`
can be decoded back into the tree by a recursive reader that consumes one token per call.
Try writing `serialize`/`deserialize` with that format.
""",
    solution=r'''
def preorder_traversal(root):
    if root is None:
        return []
    out = []
    stack = [root]
    while stack:
        node = stack.pop()
        # Preorder: a node is recorded as soon as we reach it.
        out.append(node.val)
        # LIFO: push right first so the left child is popped (visited) next,
        # which makes us finish the whole left subtree before the right one.
        if node.right is not None:
            stack.append(node.right)
        if node.left is not None:
            stack.append(node.left)
    return out
''',
    refs={
        "cpp": r'''
vector<long long> preorderTraversal(TreeNode* root) {
    vector<long long> out;
    if (!root) return out;
    stack<TreeNode*> st;
    st.push(root);
    while (!st.empty()) {
        TreeNode* n = st.top(); st.pop();
        out.push_back(n->val);               // record on arrival
        if (n->right) st.push(n->right);     // right first...
        if (n->left) st.push(n->left);       // ...so left is on top
    }
    return out;
}
''',
        "rust": RS + r'''
fn go(node: &Option<Rc<RefCell<TreeNode>>>, out: &mut Vec<i64>) {
    if let Some(rc) = node {
        let n = rc.borrow();
        out.push(n.val);                     // node first
        go(&n.left, out);                    // then left subtree
        go(&n.right, out);                   // then right subtree
    }
}

pub fn preorder_traversal(root: Option<Rc<RefCell<TreeNode>>>) -> Vec<i64> {
    let mut out = Vec::new();
    go(&root, &mut out);
    out
}
''',
    },
    tests=_TRAV_TESTS,
))

PROBLEMS.append(dict(
    id="tree-postorder-traversal",
    title="Binary Tree Postorder Traversal",
    difficulty=1,
    tags=["tree", "dfs", "stack"],
    fn="postorder_traversal",
    params=[["root", "tree"]],
    returns="int[]",
    statement=r"""
Return the values of a binary tree in **postorder**: for every node, first its whole
left subtree, then its whole right subtree, and the node itself **last**.
""",
    constraints=["0 ≤ number of nodes ≤ 500", "-100 ≤ node.val ≤ 100"],
    example_notes=[
        "4 5 2 finishes the left subtree, 6 3 the right one, and the root 1 comes last.",
        "Nothing to visit.",
    ],
    hints=[
        "Recursive: visit(left); visit(right); record(node).",
        "Postorder reversed is node, right, left. That looks a lot like preorder...",
        "Run the iterative preorder but push left before right, then reverse the output.",
    ],
    explanation=r"""
## Intuition

Postorder is the order in which a recursive function *returns* from nodes: a node is
done only after both children are done. That is exactly the order any "combine the
children's answers" computation uses (heights, sizes, freeing memory), which is why
postorder matters even if you rarely print it.

## Approach

The recursive version is the definition. For an iterative one, there is a neat trick:

- Postorder is `L, R, node`.
- Reverse it: `node, R, L`. That is preorder with the children swapped.
- So run iterative preorder pushing **left then right** (right pops first), collect
  `node, R, L`, and reverse at the end.

```text
modified preorder (node, R, L) on the intro tree:  1 3 6 2 5 4
reversed:                                          4 5 2 6 3 1   = postorder
```

The "true" single-stack postorder (tracking the last visited node to know whether you
are coming back up from the right child) also exists; it avoids the reverse but is easy
to get wrong. Try it once the simple version works.

## Complexity

- **Time O(n)**: each node pushed and popped once, plus an O(n) reverse.
- **Space O(n)** for the output, O(h) for the stack in the recursive form.

## Common mistakes

- **Reversing the wrong thing**: reverse the *output list*, not the order of pushes.
- **Forgetting the reverse** entirely gives `node, R, L`.
- **C++**: `std::reverse(out.begin(), out.end())` mutates in place and returns nothing.

## Going further

Freeing a tree in C must be postorder: if you `free(node)` before visiting its children,
reading `node->left` afterwards is a use-after-free. Write `void free_tree(struct
TreeNode*)` and you will have written postorder for real.
""",
    solution=r'''
def postorder_traversal(root):
    if root is None:
        return []
    out = []
    stack = [root]
    while stack:
        node = stack.pop()
        # Produce node, RIGHT, LEFT (a mirrored preorder)...
        out.append(node.val)
        # ...so push left first: right ends up on top and is handled first.
        if node.left is not None:
            stack.append(node.left)
        if node.right is not None:
            stack.append(node.right)
    # Reversing (node, R, L) yields (L, R, node): exactly postorder.
    out.reverse()
    return out
''',
    refs={
        "cpp": r'''
static void go(TreeNode* n, vector<long long>& out) {
    if (!n) return;
    go(n->left, out);
    go(n->right, out);
    out.push_back(n->val);                   // the node only after both children
}

vector<long long> postorderTraversal(TreeNode* root) {
    vector<long long> out;
    go(root, out);
    return out;
}
''',
        "rust": RS + r'''
pub fn postorder_traversal(root: Option<Rc<RefCell<TreeNode>>>) -> Vec<i64> {
    let mut out = Vec::new();
    let mut stack = Vec::new();
    if let Some(r) = root { stack.push(r); }
    while let Some(rc) = stack.pop() {
        let n = rc.borrow();
        out.push(n.val);                                   // node, R, L ...
        if let Some(l) = &n.left { stack.push(Rc::clone(l)); }
        if let Some(r) = &n.right { stack.push(Rc::clone(r)); }
    }
    out.reverse();                                         // ... reversed = L, R, node
    out
}
''',
    },
    tests=_TRAV_TESTS,
))

# ---------------------------------------------------------------- 5. level order

PROBLEMS.append(dict(
    id="tree-level-order",
    title="Binary Tree Level Order Traversal",
    difficulty=2,
    tags=["tree", "bfs", "queue"],
    fn="level_order",
    params=[["root", "tree"]],
    returns="int[][]",
    statement=r"""
Return the values of a binary tree **level by level**: one list per depth, from the root
level downwards, each list ordered left to right.
""",
    constraints=["0 ≤ number of nodes ≤ 800", "-1000 ≤ node.val ≤ 1000"],
    example_notes=[
        "Depth 0 holds 1, depth 1 holds 2 and 3, depth 2 holds 4, 5 and 6.",
        "No nodes, no levels.",
    ],
    hints=[
        "Which data structure hands out nodes in the order they were discovered?",
        "BFS with a queue visits nodes in depth order. The difficulty is knowing where a level ends.",
        "At the start of each round, the queue contains exactly one whole level: record `len(queue)` and pop that many.",
    ],
    explanation=r"""
## Intuition

"Level by level" is breadth-first search. A FIFO queue guarantees that every node at
depth `d` comes out before any node at depth `d + 1`, because the children of depth-`d`
nodes are appended *behind* all of depth `d`.

## Approach

1. If the tree is empty return `[]`. Otherwise start the queue with the root.
2. Each round: `size = len(queue)`. Pop exactly `size` nodes into a new list, pushing
   their children to the back. Those children form the *next* level and are untouched
   this round.
3. Append the list to the result; repeat while the queue is non-empty.

```text
round  queue at start   size  level      queue at end
1      [1]              1     [1]        [2, 3]
2      [2, 3]           2     [2, 3]     [4, 5, 6]
3      [4, 5, 6]        3     [4, 5, 6]  []
```

A DFS also works: carry `depth` down, and append `node.val` to `result[depth]`
(creating the list when `depth == len(result)`). Preorder visits the left side first, so
each level's list is still left to right.

## Complexity

- **Time O(n)**: each node enqueued and dequeued once.
- **Space O(w)** for the queue, where `w` is the maximum width; a complete tree has
  about n/2 leaves on the last level, so O(n) worst case.

## Common mistakes

- **Using `len(queue)` inside the loop condition** (`while i < len(q)`) instead of a
  snapshot: newly pushed children get mixed into the current level.
- **Python `list.pop(0)`** is O(n) per pop, giving O(n²) total. Use `collections.deque`.
- **Returning `[[]]` for the empty tree**: the expected answer is `[]`.
- **Rust**: hold the `Ref` from `borrow()` only while you read the node; push
  `Rc::clone(child)` into the `VecDeque`.

## Going further

Small twists on the same loop: zigzag order (reverse every other level), averages per
level, the right side view (last element of each level, a later problem), or connecting
each node to its right neighbour on the same level.
""",
    solution=r'''
def level_order(root):
    if root is None:
        return []
    result = []
    queue = deque([root])          # FIFO: nodes come out in depth order
    while queue:
        # Snapshot: right now the queue holds exactly one complete level.
        size = len(queue)
        level = []
        for _ in range(size):
            node = queue.popleft()
            level.append(node.val)
            # Children belong to the next level; they wait behind this one.
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
        result.append(level)
    return result
''',
    refs={
        "cpp": r'''
vector<vector<long long>> levelOrder(TreeNode* root) {
    vector<vector<long long>> res;
    if (!root) return res;
    queue<TreeNode*> q;
    q.push(root);
    while (!q.empty()) {
        size_t sz = q.size();                // one complete level
        vector<long long> level;
        level.reserve(sz);
        for (size_t i = 0; i < sz; i++) {
            TreeNode* n = q.front(); q.pop();
            level.push_back(n->val);
            if (n->left) q.push(n->left);
            if (n->right) q.push(n->right);
        }
        res.push_back(move(level));
    }
    return res;
}
''',
        "rust": RS + r'''
use std::collections::VecDeque;

pub fn level_order(root: Option<Rc<RefCell<TreeNode>>>) -> Vec<Vec<i64>> {
    let mut res = Vec::new();
    let mut q = VecDeque::new();
    if let Some(r) = root { q.push_back(r); }
    while !q.is_empty() {
        let size = q.len();                  // snapshot of this level
        let mut level = Vec::with_capacity(size);
        for _ in 0..size {
            let rc = q.pop_front().unwrap();
            let n = rc.borrow();
            level.push(n.val);
            if let Some(l) = &n.left { q.push_back(Rc::clone(l)); }
            if let Some(r) = &n.right { q.push_back(Rc::clone(r)); }
        }
        res.push(level);
    }
    res
}
''',
    },
    tests=[
        [_EX], [[]], [[3, 9, 20, None, None, 15, 7]], [[1]],
        [_chain([1, 2, 3, 4], "Z")],
        [_ser(_balanced_root(list(range(1, 32))))],
        [_rand_tree(_R, 40, -1000, 1000)], [_rand_tree(_R, 800, -1000, 1000)],
    ],
))

# ---------------------------------------------------------------- 6. invert

PROBLEMS.append(dict(
    id="tree-invert",
    title="Invert Binary Tree",
    difficulty=1,
    tags=["tree", "recursion"],
    fn="invert_tree",
    params=[["root", "tree"]],
    returns="tree",
    statement=r"""
**Invert** a binary tree: produce its mirror image, where every node's left and right
children are swapped (at every level, not just the root). Return the root of the
inverted tree. Modifying the input in place is fine.
""",
    constraints=["0 ≤ number of nodes ≤ 500", "-100 ≤ node.val ≤ 100"],
    example_notes=[
        "Every pair of children is swapped: 2 and 3 trade places, and so do 4 and 5; 6 moves from 3's right to its left.",
        "A root with a right child becomes a root with a left child.",
    ],
    hints=[
        "What does inverting do to a single node? What remains to be done afterwards?",
        "Swap the two children, then invert each of them (or invert them first and then swap; both work).",
        "Careful in languages with explicit pointers: save one child in a temporary before overwriting it.",
    ],
    explanation=r"""
## Intuition

The mirror of a tree is: the same root, with the *mirror of the right subtree* on the
left and the *mirror of the left subtree* on the right. That sentence is the recursion.

```text
       1                1
     /   \            /   \
    2     3    =>    3     2
   / \     \        /     / \
  4   5     6      6     5   4
```

## Approach

1. Empty tree: return it unchanged.
2. Recursively invert both children.
3. Assign the inverted right subtree to `left` and the inverted left one to `right`.
4. Return the node.

In Python the tuple assignment
`root.left, root.right = invert(root.right), invert(root.left)` evaluates the whole
right-hand side before assigning anything, so no temporary is needed. In C you must save
`root->left` before overwriting it.

An iterative BFS/DFS works equally well: pop a node, swap its children, push them. The
order in which you swap does not matter, because each swap is local to one node.

## Complexity

- **Time O(n)**: each node swaps its children once.
- **Space O(h)** for the recursion stack (O(n) for a chain).

## Common mistakes

- **Swapping only the root's children**: the deeper levels stay unmirrored.
- **Overwriting before saving** in C/C++: `root->left = invert(root->right);
  root->right = invert(root->left);` inverts the *new* left (the old right) twice and
  loses the old left entirely.
- **Rust**: you cannot take `n.left` out of a borrowed node by value; use
  `left.take()` on a `borrow_mut()` to move it out, leaving `None` behind, then assign.
  Drop the `RefMut` before recursing into the same node (here we recurse on the
  children, which are separate `RefCell`s, so it is fine).

## Going further

This problem is famous for a tweet about a candidate who could not solve it at a big
company interview. A related check, "is this tree symmetric?", asks whether a tree equals
its own mirror; it appears later in this track.
""",
    solution=r'''
def invert_tree(root):
    if root is None:
        return None
    # The right-hand side is fully evaluated before assignment, so both
    # recursive calls see the ORIGINAL children; no temporary is needed.
    root.left, root.right = invert_tree(root.right), invert_tree(root.left)
    return root
''',
    refs={
        "c": r'''
struct TreeNode* invert_tree(struct TreeNode* root) {
    if (!root) return NULL;
    struct TreeNode* oldLeft = root->left;     /* save before overwriting */
    root->left = invert_tree(root->right);
    root->right = invert_tree(oldLeft);
    return root;
}
''',
        "cpp": r'''
TreeNode* invertTree(TreeNode* root) {
    if (!root) return nullptr;
    swap(root->left, root->right);           // mirror this node...
    invertTree(root->left);                  // ...then both subtrees
    invertTree(root->right);
    return root;
}
''',
        "rust": RS + r'''
pub fn invert_tree(root: Option<Rc<RefCell<TreeNode>>>) -> Option<Rc<RefCell<TreeNode>>> {
    if let Some(rc) = &root {
        let mut n = rc.borrow_mut();
        // take() moves each child out, leaving None, so we own them.
        let l = n.left.take();
        let r = n.right.take();
        n.left = invert_tree(r);
        n.right = invert_tree(l);
    }
    root
}
''',
    },
    tests=[
        [[1, 2, 3, 4, 5, None, 6]], [[2, 1]], [[]], [[1]], [[4, 2, 7, 1, 3, 6, 9]],
        [_chain([1, 2, 3, 4, 5, 6], "Z")],
        [_rand_tree(_R, 30)], [_rand_tree(_R, 500)],
    ],
))

# ---------------------------------------------------------------- 7. same tree


def _same_tests():
    rng = random.Random(77)
    t = []
    base = _rand_root(rng, [rng.randint(-50, 50) for _ in range(60)])
    t.append([_ser(base), _ser(_copy(base))])
    changed = _copy(base)
    nodes = _nodes(changed)
    rng.choice(nodes).val += 1
    t.append([_ser(base), _ser(changed)])
    pruned = _copy(base)
    for nd in _nodes(pruned):
        if nd.left and not nd.left.left and not nd.left.right:
            nd.left = None
            break
    t.append([_ser(base), _ser(pruned)])
    big = _rand_root(rng, [rng.randint(-50, 50) for _ in range(400)])
    t.append([_ser(big), _ser(_copy(big))])
    return t


PROBLEMS.append(dict(
    id="tree-same",
    title="Same Tree",
    difficulty=1,
    tags=["tree", "recursion"],
    fn="is_same_tree",
    params=[["p", "tree"], ["q", "tree"]],
    returns="bool",
    statement=r"""
Given the roots of two binary trees `p` and `q`, return `true` if they are **the same**:
structurally identical, with equal values in corresponding nodes.
""",
    constraints=["0 ≤ number of nodes in each tree ≤ 400", "-100 ≤ node.val ≤ 100"],
    example_notes=[
        "Same shape and same values everywhere.",
        "Same values, different shape: 2 is a left child in one tree and a right child in the other.",
    ],
    hints=[
        "Compare the roots first. When are two trees trivially equal? Trivially different?",
        "Two empty trees are the same; one empty and one non-empty are not.",
        "same(p, q) = p.val == q.val and same(p.left, q.left) and same(p.right, q.right).",
    ],
    explanation=r"""
## Intuition

Walk both trees in lockstep. At each pair of positions there are only three cases:
both empty (fine), exactly one empty (shapes differ), or both present (values must
match and both pairs of children must be the same).

## Approach

```text
same(p, q):
  both None        -> True
  one None         -> False
  p.val != q.val   -> False
  otherwise        -> same(p.left, q.left) and same(p.right, q.right)
```

Trace for `[1,2]` vs `[1,null,2]`:

```text
same(1, 1): values equal -> same(2, None) -> one empty -> False   (stop: `and` short-circuits)
```

Note that comparing the traversals is **not** enough: `[1,2]` and `[1,null,2]` have the
same preorder (`1 2`). You would need the `null` markers too, which is precisely a
serialization.

## Complexity

- **Time O(min(n, m))**: we stop at the first mismatch, and never descend further than
  the smaller tree.
- **Space O(min(h_p, h_q))** for the recursion.

## Common mistakes

- **Checking `p.val` before checking for `None`** crashes on empty inputs.
- **Using `or` when one side is empty**: `if not p or not q: return p is q` is a compact,
  correct way to fold both base cases together, but `return False` alone is wrong when
  both are empty.
- **Rust**: `TreeNode` derives `PartialEq`, so `p == q` actually compares the whole
  structure for you. It is worth writing the recursion yourself once to see how
  `match (a, b)` on a tuple of `&Option`s reads.

## Going further

*Subtree of another tree* asks whether `q` appears as a subtree anywhere in `p`: call
`same` from every node of `p` for O(n·m), or serialize both with null markers and use a
string-matching algorithm for O(n + m).
""",
    solution=r'''
def is_same_tree(p, q):
    # Both positions empty: identical so far.
    if p is None and q is None:
        return True
    # Exactly one empty: the shapes differ here.
    if p is None or q is None:
        return False
    # Both present: values must match, and so must both pairs of children.
    # `and` short-circuits, so we stop at the first difference.
    return (p.val == q.val
            and is_same_tree(p.left, q.left)
            and is_same_tree(p.right, q.right))
''',
    refs={
        "c": r'''
bool is_same_tree(struct TreeNode* p, struct TreeNode* q) {
    if (!p || !q) return p == q;             /* both NULL -> true, one NULL -> false */
    return p->val == q->val
        && is_same_tree(p->left, q->left)
        && is_same_tree(p->right, q->right);
}
''',
        "cpp": r'''
bool isSameTree(TreeNode* p, TreeNode* q) {
    if (!p || !q) return p == q;
    return p->val == q->val && isSameTree(p->left, q->left) && isSameTree(p->right, q->right);
}
''',
        "rust": RS + r'''
fn same(a: &Option<Rc<RefCell<TreeNode>>>, b: &Option<Rc<RefCell<TreeNode>>>) -> bool {
    match (a, b) {
        (None, None) => true,
        (Some(x), Some(y)) => {
            let (x, y) = (x.borrow(), y.borrow());
            x.val == y.val && same(&x.left, &y.left) && same(&x.right, &y.right)
        }
        _ => false,                          // exactly one side is empty
    }
}

pub fn is_same_tree(p: Option<Rc<RefCell<TreeNode>>>, q: Option<Rc<RefCell<TreeNode>>>) -> bool {
    same(&p, &q)
}
''',
    },
    tests=[
        [[1, 2, 3], [1, 2, 3]], [[1, 2], [1, None, 2]], [[], []], [[1], []],
        [[1, 2, 1], [1, 1, 2]], [[5], [5]],
    ] + _same_tests(),
))

# ---------------------------------------------------------------- 8. symmetric


def _sym_tests():
    rng = random.Random(88)
    t = []
    for n in (6, 200):
        half = _rand_root(rng, [rng.randint(-9, 9) for _ in range(n)])
        t.append([_ser(_N(0, half, _mirror(_copy(half))))])
    half = _rand_root(rng, [rng.randint(-9, 9) for _ in range(40)])
    other = _mirror(_copy(half))
    nd = _nodes(other)[-1]
    nd.val += 100
    t.append([_ser(_N(0, half, other))])
    half = _rand_root(rng, [rng.randint(-9, 9) for _ in range(40)])
    t.append([_ser(_N(0, half, _copy(half)))])  # copy, not mirror: usually asymmetric
    return t


PROBLEMS.append(dict(
    id="tree-symmetric",
    title="Symmetric Tree",
    difficulty=1,
    tags=["tree", "recursion"],
    fn="is_symmetric",
    params=[["root", "tree"]],
    returns="bool",
    statement=r"""
Return `true` if the binary tree is a **mirror of itself** (symmetric around its centre
line). The empty tree is symmetric.
""",
    constraints=["0 ≤ number of nodes ≤ 500", "-200 ≤ node.val ≤ 200"],
    example_notes=[
        "The left half 2,(3,4) mirrors the right half 2,(4,3).",
        "Both 2s have a 3 on their right, so the halves are copies, not mirrors.",
    ],
    hints=[
        "Symmetric means the left subtree is the mirror image of the right subtree.",
        "Write a helper `mirror(a, b)` that checks two trees against each other, similar to Same Tree.",
        "a and b mirror each other when a.val == b.val, a.left mirrors b.right, and a.right mirrors b.left.",
    ],
    explanation=r"""
## Intuition

Fold the tree along the vertical line through the root. Each node on the left must land
on an equal node on the right. Comparing *one* tree with itself is awkward; comparing
*two* trees (left half vs right half) is the Same Tree problem with the children crossed.

```text
          1
        /   \
       2  |  2          outer pair: 3 (left.left)  vs 3 (right.right)
      / \ | / \         inner pair: 4 (left.right) vs 4 (right.left)
     3  4 | 4  3
```

## Approach

`mirror(a, b)`:

1. Both empty: true. One empty: false.
2. Values differ: false.
3. Otherwise `mirror(a.left, b.right) and mirror(a.right, b.left)`: outer with outer,
   inner with inner.

The answer is `mirror(root.left, root.right)` (true for the empty tree).

Iteratively, push the *pair* `(left, right)` onto a queue and, for each popped pair,
push `(a.left, b.right)` and `(a.right, b.left)`.

## Complexity

- **Time O(n)**: each node is compared once (as part of exactly one pair).
- **Space O(h)** recursion.

## Common mistakes

- **Comparing `a.left` with `b.left`**: that tests whether the halves are *equal*, not
  mirrored. One of the tests is exactly a tree whose halves are copies.
- **Checking only that each level reads as a palindrome of values**: that ignores
  `null` positions. `[1,2,2,null,3,null,3]` has palindromic value levels but is not
  symmetric.
- **Rust**: borrowing both halves at once is fine (`borrow()` is shared), even though
  they come from the same root.

## Going further

You could also invert a copy of the left subtree and run Same Tree against the right
subtree. That takes O(n) extra space; the paired recursion does it in place.
""",
    solution=r'''
def is_symmetric(root):
    def mirror(a, b):
        # Both missing: the positions match.
        if a is None and b is None:
            return True
        # One missing: the shape is not symmetric here.
        if a is None or b is None:
            return False
        # Mirror images: equal values, and the OUTER children match each other
        # (a.left with b.right) while the INNER ones do too (a.right with b.left).
        return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)

    return root is None or mirror(root.left, root.right)
''',
    refs={
        "c": r'''
static bool mirror(struct TreeNode* a, struct TreeNode* b) {
    if (!a || !b) return a == b;
    return a->val == b->val && mirror(a->left, b->right) && mirror(a->right, b->left);
}

bool is_symmetric(struct TreeNode* root) {
    return root == NULL || mirror(root->left, root->right);
}
''',
        "cpp": r'''
bool isSymmetric(TreeNode* root) {
    if (!root) return true;
    // Iterative: a queue of pairs that must mirror each other.
    queue<pair<TreeNode*, TreeNode*>> q;
    q.push({root->left, root->right});
    while (!q.empty()) {
        auto [a, b] = q.front(); q.pop();
        if (!a && !b) continue;
        if (!a || !b || a->val != b->val) return false;
        q.push({a->left, b->right});          // outer pair
        q.push({a->right, b->left});          // inner pair
    }
    return true;
}
''',
        "rust": RS + r'''
fn mirror(a: &Option<Rc<RefCell<TreeNode>>>, b: &Option<Rc<RefCell<TreeNode>>>) -> bool {
    match (a, b) {
        (None, None) => true,
        (Some(x), Some(y)) => {
            let (x, y) = (x.borrow(), y.borrow());
            x.val == y.val && mirror(&x.left, &y.right) && mirror(&x.right, &y.left)
        }
        _ => false,
    }
}

pub fn is_symmetric(root: Option<Rc<RefCell<TreeNode>>>) -> bool {
    match &root {
        None => true,
        Some(rc) => {
            let n = rc.borrow();
            mirror(&n.left, &n.right)
        }
    }
}
''',
    },
    tests=[
        [[1, 2, 2, 3, 4, 4, 3]], [[1, 2, 2, None, 3, None, 3]], [[]], [[1]],
        [[1, 2, 2, 2, None, 2]], [[1, 2, 3]],
    ] + _sym_tests(),
))

# ---------------------------------------------------------------- 9. path sum


def _path_tests():
    rng = random.Random(99)
    t = []
    for n in (15, 120, 400):
        a = _rand_tree(rng, n, -20, 20)
        sums = _leaf_sums(_de(a))
        t.append([a, rng.choice(sums)])
        miss = max(sums) + 1
        t.append([a, miss])
    return t


PROBLEMS.append(dict(
    id="tree-path-sum",
    title="Path Sum",
    difficulty=1,
    tags=["tree", "dfs"],
    fn="has_path_sum",
    params=[["root", "tree"], ["target_sum", "int"]],
    returns="bool",
    statement=r"""
Return `true` if the tree has a **root-to-leaf** path whose values add up to
`target_sum`. A leaf is a node with no children. The empty tree has no paths, so the
answer for it is always `false`.
""",
    constraints=["0 ≤ number of nodes ≤ 400", "-1000 ≤ node.val ≤ 1000", "-10⁶ ≤ target_sum ≤ 10⁶"],
    example_notes=[
        "5 → 4 → 11 → 2 adds up to 22.",
        "The paths are 1→2 (sum 3) and 1→3 (sum 4); neither is 5.",
    ],
    hints=[
        "Instead of summing on the way down, subtract: what sum must the rest of the path have?",
        "has(node, t) = has(node.left, t - node.val) or has(node.right, t - node.val).",
        "Only a LEAF may end a path. Check `remaining == 0` exactly when both children are missing.",
    ],
    explanation=r"""
## Intuition

A path is a sequence of choices (left or right) starting at the root. Rather than
building every path and summing it, carry the **remaining** target down: after visiting a
node with value `v`, the rest of the path must sum to `target - v`. At a leaf, the path
works if the remainder is exactly zero.

## Approach

```text
has(node, t):
  node is None             -> False      (no path here)
  r = t - node.val
  node is a leaf           -> r == 0
  otherwise                -> has(left, r) or has(right, r)
```

Trace on the example with target 22:

```text
          5           t=22  -> r=17
         / \
        4   8         4: r=13           8: r=9
       /   / \
      11  13  4       11: r=2           13: r=-4 (leaf, no)  4: r=5
     /  \      \
    7    2      1     7: r=-5 (leaf, no)   2: r=0 (leaf) -> True
```

## Complexity

- **Time O(n)** in the worst case (no path matches), each node visited once.
- **Space O(h)**.

## Common mistakes

- **Accepting a non-leaf**: in `[1,2]` with target 1, the root alone sums to 1 but is not
  a leaf (it has a child), so the answer is `false`. Testing `remaining == 0` on reaching
  `None` gets this wrong, because the empty right child of 1 would "complete" a path.
- **Empty tree with target 0**: the answer is `false`; there is no path at all.
- **Pruning when the running sum exceeds the target**: values can be negative, so a
  path can come back down.

## Going further

*Path Sum II* returns every matching path (backtracking with a shared list you append to
and pop from). *Path Sum III* counts downward paths that may start and end anywhere; the
trick there is prefix sums along the current root path in a hash map.
""",
    solution=r'''
def has_path_sum(root, target_sum):
    # No node, no path (this also makes the empty tree return False).
    if root is None:
        return False
    # What the rest of the path below this node must add up to.
    remaining = target_sum - root.val
    # A path may only END at a leaf.
    if root.left is None and root.right is None:
        return remaining == 0
    # Otherwise try both directions; `or` stops at the first success.
    return has_path_sum(root.left, remaining) or has_path_sum(root.right, remaining)
''',
    refs={
        "c": r'''
bool has_path_sum(struct TreeNode* root, long long target_sum) {
    if (!root) return false;
    long long rem = target_sum - root->val;
    if (!root->left && !root->right) return rem == 0;     /* leaf: path ends here */
    return has_path_sum(root->left, rem) || has_path_sum(root->right, rem);
}
''',
        "cpp": r'''
bool hasPathSum(TreeNode* root, long long targetSum) {
    if (!root) return false;
    long long rem = targetSum - root->val;
    if (!root->left && !root->right) return rem == 0;
    return hasPathSum(root->left, rem) || hasPathSum(root->right, rem);
}
''',
        "rust": RS + r'''
fn go(node: &Option<Rc<RefCell<TreeNode>>>, remaining: i64) -> bool {
    match node {
        None => false,
        Some(rc) => {
            let n = rc.borrow();
            let rem = remaining - n.val;
            if n.left.is_none() && n.right.is_none() {
                return rem == 0;                 // leaf: the path must end exactly here
            }
            go(&n.left, rem) || go(&n.right, rem)
        }
    }
}

pub fn has_path_sum(root: Option<Rc<RefCell<TreeNode>>>, target_sum: i64) -> bool {
    go(&root, target_sum)
}
''',
    },
    tests=[
        [[5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1], 22], [[1, 2, 3], 5],
        [[], 0], [[1, 2], 1], [[1, 2], 3], [[-2, None, -3], -5], [[7], 7],
    ] + _path_tests(),
))

# ---------------------------------------------------------------- 10. diameter

PROBLEMS.append(dict(
    id="tree-diameter",
    title="Diameter of Binary Tree",
    difficulty=2,
    tags=["tree", "dfs", "postorder"],
    fn="diameter_of_binary_tree",
    params=[["root", "tree"]],
    returns="int",
    statement=r"""
The **diameter** of a binary tree is the number of **edges** on the longest path between
any two nodes. The path does not have to pass through the root. Return the diameter
(`0` for an empty tree or a single node).
""",
    constraints=["0 ≤ number of nodes ≤ 800", "-100 ≤ node.val ≤ 100"],
    example_notes=[
        "The path 4 → 2 → 1 → 3 → 6 (or 5 → 2 → 1 → 3 → 6) has 4 edges.",
        "Two nodes, one edge.",
    ],
    hints=[
        "Every path has a single highest node where it 'bends'. What is the longest path bending at a given node?",
        "Longest path bending at node = height(left) + height(right), counting edges.",
        "One postorder pass: return the height to the parent, and update a global best with left + right on the way.",
    ],
    explanation=r"""
## Intuition

Any path in a tree climbs up to a single topmost node and then goes down. So consider
each node as the potential **bend point**: the longest path bending there goes as deep as
possible into the left subtree and as deep as possible into the right one. Its length in
edges is `height(left) + height(right)` where height counts nodes (each subtree adds one
edge per node on its side).

The diameter is the maximum of that quantity over all nodes. Computing `height` from
scratch at every node would be O(n²); instead compute all heights in **one postorder
pass** and evaluate the bend at each node while you are there.

## Approach

`height(node)` returns the number of nodes on the longest downward path, and as a side
effect updates `best`:

```text
height(None) = 0
l = height(left); r = height(right)
best = max(best, l + r)          # path bending here, in edges
return 1 + max(l, r)             # what the parent needs
```

This is the "return one thing, record another" pattern from the intro: the parent can
only *extend* one branch of yours, but the best path might use both.

```text
          1            node  l  r  bend l+r  returns
        /   \          4     0  0  0         1
       2     3         5     0  0  0         1
      / \     \        2     1  1  2         2
     4   5     6       6     0  0  0         1
                       3     0  1  1         2
                       1     2  2  4  <-     3      diameter = 4
```

## Complexity

- **Time O(n)**, one visit per node.
- **Space O(h)** for recursion.

## Common mistakes

- **Assuming the path goes through the root.** Test 5 has a big left subtree with a
  long path and a short right side; the best bend is deep inside.
- **Mixing node and edge counts.** With heights in nodes, `l + r` is already the number
  of edges (each side contributes `height` edges including the edge to the bend node).
- **Recomputing heights** inside a loop over nodes: O(n²), which an 800-node chain makes
  visible.
- **Python closures**: assigning `best = ...` inside a nested function creates a local
  unless you write `nonlocal best` (or store it in a list/attribute).

## Going further

For a general (non-binary) tree the same idea keeps the *two largest* child heights. The
classic alternative for any tree is "double BFS": BFS from any node to find the farthest
node `u`, then BFS from `u`; the farthest distance is the diameter.
""",
    solution=r'''
def diameter_of_binary_tree(root):
    best = 0

    def height(node):
        """Nodes on the longest downward path from `node`; records the best bend."""
        nonlocal best
        if node is None:
            return 0
        l = height(node.left)
        r = height(node.right)
        # Longest path that BENDS at this node: down the left, down the right.
        # With heights in nodes, l + r is exactly that path's edge count.
        best = max(best, l + r)
        # The parent can only extend ONE of our branches, so report the taller.
        return 1 + max(l, r)

    height(root)
    return best
''',
    refs={
        "cpp": r'''
static long long heightAndBest(TreeNode* n, long long& best) {
    if (!n) return 0;
    long long l = heightAndBest(n->left, best);
    long long r = heightAndBest(n->right, best);
    best = max(best, l + r);                 // path bending at n
    return 1 + max(l, r);                    // height reported to the parent
}

long long diameterOfBinaryTree(TreeNode* root) {
    long long best = 0;
    heightAndBest(root, best);
    return best;
}
''',
        "rust": RS + r'''
fn height(node: &Option<Rc<RefCell<TreeNode>>>, best: &mut i64) -> i64 {
    match node {
        None => 0,
        Some(rc) => {
            let n = rc.borrow();
            let l = height(&n.left, best);
            let r = height(&n.right, best);
            *best = (*best).max(l + r);
            1 + l.max(r)
        }
    }
}

pub fn diameter_of_binary_tree(root: Option<Rc<RefCell<TreeNode>>>) -> i64 {
    let mut best = 0;
    height(&root, &mut best);
    best
}
''',
    },
    tests=[
        [_EX], [[1, 2]], [[]], [[1]],
        [[1, 2, 3, 4, 5, None, None, 6, None, None, 7, 8, None, None, 9, 10]],
        [_chain(list(range(800)), "L")],
        [_ser(_balanced_root(list(range(127))))],
        [_rand_tree(_R, 60)], [_rand_tree(_R, 600)],
    ],
))

# ---------------------------------------------------------------- 11. balanced


def _bal_tests():
    t = [[_ser(_balanced_root(list(range(n))))] for n in (100, 500)]
    # Fibonacci-like (AVL worst case) trees: balanced but lopsided.
    def fib_tree(h):
        if h <= 0:
            return None
        if h == 1:
            return _N(0)
        return _N(0, fib_tree(h - 1), fib_tree(h - 2))
    t.append([_ser(fib_tree(10))])
    bad = fib_tree(8)
    cur = bad
    while cur.left:
        cur = cur.left
    cur.left = _N(1, _N(2))  # deepens the leftmost branch by 2
    t.append([_ser(bad)])
    return t


PROBLEMS.append(dict(
    id="tree-balanced",
    title="Balanced Binary Tree",
    difficulty=1,
    tags=["tree", "dfs", "postorder"],
    fn="is_balanced",
    params=[["root", "tree"]],
    returns="bool",
    statement=r"""
A binary tree is **height-balanced** if, at **every** node, the heights of the left and
right subtrees differ by at most one. Return whether the given tree is height-balanced.
The empty tree is balanced.
""",
    constraints=["0 ≤ number of nodes ≤ 500", "-10⁴ ≤ node.val ≤ 10⁴"],
    example_notes=[
        "Heights at the root are 1 (left) and 2 (right); every deeper node is balanced too.",
        "The root's subtrees have heights 3 and 1.",
    ],
    hints=[
        "Checking only the root's two heights is not enough: the condition holds at every node.",
        "Calling a separate height() function from every node works but is O(n²) on a chain.",
        "Return the height from a postorder helper, and use a sentinel such as -1 to mean 'already unbalanced below'.",
    ],
    explanation=r"""
## Intuition

Balance is a property that every node must satisfy, and checking it needs the two
subtree heights. Heights are computed bottom-up, so do both jobs in **one postorder
pass**: return the height if the subtree is balanced, and a sentinel (`-1`) as soon as
any node fails. Once `-1` appears it propagates straight to the root.

## Approach

```text
check(None) = 0
l = check(left);  if l == -1: return -1
r = check(right); if r == -1: return -1
if |l - r| > 1:   return -1
return 1 + max(l, r)
```

The tree is balanced iff `check(root) != -1`.

```text
        1             check(4)=1 check(4')=1 -> check(3)=2
       / \            check(3')=1             -> check(2)=1+max(2,1)=3   |2-1|<=1
      2   2           check(2')=1             -> root: l=3, r=1, |3-1|=2 -> -1
     / \
    3   3              unbalanced
   / \
  4   4
```

## Complexity

- **Time O(n)**: each node is visited once; early exit can make it faster.
- **Space O(h)**.

The naive version (`abs(height(l) - height(r)) <= 1 and balanced(l) and balanced(r)`)
recomputes heights at every level: O(n log n) on balanced trees but **O(n²)** on a chain.

## Common mistakes

- **Only checking the root**: a tree can have equal heights on both sides of the root
  and be badly unbalanced inside (two long chains, one left and one right).
- **Comparing min depth with max depth** of the whole tree: that is a stricter notion
  ("nearly complete") and rejects valid AVL-style trees like the Fibonacci tree in the tests.
- **Ignoring the sentinel**: computing `1 + max(-1, 5)` hides the failure. Check for
  `-1` before using a child's value.

## Going further

AVL trees maintain exactly this invariant after every insertion with rotations, which
guarantees height ≤ about 1.44·log₂(n). The worst-case AVL shape is the "Fibonacci tree"
used in one of the tests: each node's left subtree is one taller than its right.
""",
    solution=r'''
def is_balanced(root):
    def check(node):
        """Height of `node` if its subtree is balanced, otherwise -1."""
        if node is None:
            return 0
        l = check(node.left)
        if l == -1:            # imbalance below: no point looking further
            return -1
        r = check(node.right)
        if r == -1:
            return -1
        if abs(l - r) > 1:     # this node itself violates the rule
            return -1
        return 1 + max(l, r)

    return check(root) != -1
''',
    refs={
        "c": r'''
static long long check(struct TreeNode* n) {
    if (!n) return 0;
    long long l = check(n->left);
    if (l < 0) return -1;
    long long r = check(n->right);
    if (r < 0) return -1;
    if (l - r > 1 || r - l > 1) return -1;
    return 1 + (l > r ? l : r);
}

bool is_balanced(struct TreeNode* root) {
    return check(root) >= 0;
}
''',
        "cpp": r'''
static int check(TreeNode* n) {
    if (!n) return 0;
    int l = check(n->left);
    if (l < 0) return -1;
    int r = check(n->right);
    if (r < 0) return -1;
    if (abs(l - r) > 1) return -1;
    return 1 + max(l, r);
}

bool isBalanced(TreeNode* root) { return check(root) >= 0; }
''',
        "rust": RS + r'''
// Some(height) when balanced, None as soon as any node fails.
fn check(node: &Option<Rc<RefCell<TreeNode>>>) -> Option<i64> {
    match node {
        None => Some(0),
        Some(rc) => {
            let n = rc.borrow();
            let l = check(&n.left)?;         // `?` propagates None upwards
            let r = check(&n.right)?;
            if (l - r).abs() > 1 { None } else { Some(1 + l.max(r)) }
        }
    }
}

pub fn is_balanced(root: Option<Rc<RefCell<TreeNode>>>) -> bool {
    check(&root).is_some()
}
''',
    },
    tests=[
        [[3, 9, 20, None, None, 15, 7]], [[1, 2, 2, 3, 3, None, None, 4, 4]], [[]], [[1]],
        [[1, 2, 2, 3, None, None, 3, 4, None, None, 4]],
        [[1, 2, None, 3]], [[1, 2, 3, 4]],
    ] + _bal_tests(),
))

# ---------------------------------------------------------------- 12. LCA in BST


def _lca_tests():
    rng = random.Random(1212)
    t = []
    for n in (30, 500):
        a = _rand_bst(rng, n)
        vals = [x for x in a if x is not None]
        for _ in range(2):
            p, q = rng.sample(vals, 2)
            t.append([a, p, q])
    a = _ser(_bst_root(list(range(1, 501))))  # right chain
    t.append([a, 250, 500])
    return t


PROBLEMS.append(dict(
    id="bst-lowest-common-ancestor",
    title="Lowest Common Ancestor of a BST",
    difficulty=2,
    tags=["bst", "tree"],
    fn="lowest_common_ancestor",
    params=[["root", "tree"], ["p", "int"], ["q", "int"]],
    returns="int",
    statement=r"""
You are given a **binary search tree** with distinct values and two values `p` and `q`
that are both present in it (they may be equal). Return the **value** of their *lowest
common ancestor*: the deepest node that has both `p` and `q` in its subtree. A node counts
as an ancestor of itself.
""",
    constraints=["2 ≤ number of nodes ≤ 500", "values are distinct", "`p` and `q` exist in the tree"],
    example_notes=[
        "2 and 8 are on different sides of the root 6, so they split at 6.",
        "4 lies in the subtree of 2, so 2 is its own lowest ancestor shared with 4.",
    ],
    hints=[
        "Use the ordering. If both p and q are smaller than the current node, where must their LCA be?",
        "Walk down from the root: go left while both are smaller, right while both are larger.",
        "The first node where they are not on the same side (or where one of them equals the node) is the answer.",
    ],
    explanation=r"""
## Intuition

In a general binary tree you would search both subtrees. In a **BST** the values tell
you where everything is: if both `p` and `q` are smaller than a node, both live in its
left subtree, so their LCA is down there too. The moment they **split** (one on each
side, or one equals the current node), the current node is the lowest point that still
contains both.

## Approach

```text
cur = root
loop:
  if p < cur.val and q < cur.val: cur = cur.left
  elif p > cur.val and q > cur.val: cur = cur.right
  else: return cur.val          # split point
```

```text
            6            p=2, q=4
          /   \          at 6: both smaller -> left
         2     8         at 2: p == 2, so not "both smaller" -> answer 2
        / \   / \
       0   4 7   9       p=2, q=8 at 6: one each side -> answer 6
          / \
         3   5
```

No recursion is needed: it is a single walk down one path.

## Complexity

- **Time O(h)**: one step per level. O(log n) if balanced, O(n) for a chain (one test).
- **Space O(1)** iteratively.

## Common mistakes

- **Using `<=`/`>=` in the "go left/right" tests**: when `p == cur.val` the current node
  *is* the answer; moving on loses it.
- **Treating it as a general binary tree** and searching both subtrees: correct but
  O(n) and ignores the hint the statement gives you ("binary search tree").
- **Assuming p < q**: the inputs can come in either order, which the both-sides tests
  handle naturally.

## Going further

For a general binary tree, LCA is a postorder recursion: return the node if it is `p`
or `q`; otherwise recurse both ways; if both sides return something, this node is the
LCA, else pass up whichever side is non-empty. With many queries on a static tree, binary
lifting answers each in O(log n).
""",
    solution=r'''
def lowest_common_ancestor(root, p, q):
    cur = root
    while cur is not None:
        if p < cur.val and q < cur.val:
            # Both targets are in the left subtree, so their LCA is too.
            cur = cur.left
        elif p > cur.val and q > cur.val:
            # Both are in the right subtree.
            cur = cur.right
        else:
            # They split here (or one of them IS this node): nothing lower
            # can contain both.
            return cur.val
    return -1  # unreachable when p and q are guaranteed to exist
''',
    refs={
        "c": r'''
long long lowest_common_ancestor(struct TreeNode* root, long long p, long long q) {
    struct TreeNode* cur = root;
    while (cur) {
        if (p < cur->val && q < cur->val) cur = cur->left;
        else if (p > cur->val && q > cur->val) cur = cur->right;
        else return cur->val;                /* split point */
    }
    return -1;
}
''',
        "cpp": r'''
long long lowestCommonAncestor(TreeNode* root, long long p, long long q) {
    TreeNode* cur = root;
    while (cur) {
        if (p < cur->val && q < cur->val) cur = cur->left;
        else if (p > cur->val && q > cur->val) cur = cur->right;
        else return cur->val;
    }
    return -1;
}
''',
        "rust": RS + r'''
pub fn lowest_common_ancestor(root: Option<Rc<RefCell<TreeNode>>>, p: i64, q: i64) -> i64 {
    let mut cur = root;
    while let Some(rc) = cur {
        let n = rc.borrow();
        if p < n.val && q < n.val {
            cur = n.left.clone();            // clone the Rc pointer, not the subtree
        } else if p > n.val && q > n.val {
            cur = n.right.clone();
        } else {
            return n.val;
        }
    }
    -1
}
''',
    },
    tests=[
        [[6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], 2, 8],
        [[6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], 2, 4],
        [[2, 1], 2, 1], [[2, 1, 3], 3, 1], [[6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], 5, 5],
        [[6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], 3, 5],
    ] + _lca_tests(),
))

# ---------------------------------------------------------------- 13. validate BST


def _vbst_tests():
    rng = random.Random(1313)
    t = []
    good = _rand_bst(rng, 300)
    t.append([good])
    # break it deep inside: swap two values (keeps local parent/child order often)
    root = _de(good)
    nodes = sorted(_nodes(root), key=lambda n: n.val)
    a, b = nodes[100], nodes[250]
    a.val, b.val = b.val, a.val
    t.append([_ser(root)])
    root = _de(_rand_bst(rng, 500, -10**9, 10**9))
    t.append([_ser(root)])
    # duplicate value
    root = _de(_rand_bst(rng, 50))
    n = _nodes(root)[10]
    if n.left is None:
        n.left = _N(n.val)
    else:
        n.right = _N(n.val) if n.right is None else n.right
        if n.right.val != n.val:
            n.left.left = _N(n.val)
    t.append([_ser(root)])
    return t


PROBLEMS.append(dict(
    id="bst-validate",
    title="Validate Binary Search Tree",
    difficulty=2,
    tags=["bst", "tree", "dfs"],
    fn="is_valid_bst",
    params=[["root", "tree"]],
    returns="bool",
    statement=r"""
Return whether the binary tree is a valid **binary search tree**:

- every value in a node's **left** subtree is **strictly less** than the node's value,
- every value in its **right** subtree is **strictly greater**,
- and both subtrees are themselves valid BSTs.

Duplicates are therefore not allowed. The empty tree is a valid BST. Values may be as
large as ±2⁵⁰, so be careful with sentinel "infinities".
""",
    constraints=["0 ≤ number of nodes ≤ 500", "-2⁵⁰ ≤ node.val ≤ 2⁵⁰"],
    example_notes=[
        "1 < 2 < 3.",
        "4 is the right child of 5 but smaller than 5, so the root's rule is violated.",
    ],
    hints=[
        "Checking `left.val < node.val < right.val` at every node is not enough. Why?",
        "Each node must lie in an open interval (low, high) inherited from all its ancestors.",
        "Recurse with bounds: left child gets (low, node.val), right child gets (node.val, high). Alternatively, the inorder walk must be strictly increasing.",
    ],
    explanation=r"""
## Intuition

The BST rule is about whole subtrees, not immediate children:

```text
        5
       / \
      1   4          4 > 5? no -> invalid at the root's right child
         / \
        3   6        3 is a fine left child of 4, but it sits in 5's RIGHT subtree
```

Each ancestor you turn **left** at imposes an upper bound; each one you turn **right** at
imposes a lower bound. Together they give every node an open interval it must lie in.

## Approach

**Bounds recursion.** `ok(node, low, high)`:

1. Empty: true.
2. If `low` exists and `node.val <= low`, or `high` exists and `node.val >= high`: false.
3. `ok(left, low, node.val) and ok(right, node.val, high)`.

Start with no bounds: `ok(root, None, None)`.

```text
ok(5, -, -) -> ok(1, -, 5) ok   ok(4, 5, -) -> 4 <= 5 -> False
```

**Inorder alternative.** An inorder walk of a valid BST is strictly increasing. Walk it
(recursively or with a stack), remember the previous value, and fail if
`cur <= prev`. Same complexity, and no bounds to pass around.

## Complexity

- **Time O(n)**, each node checked once.
- **Space O(h)**.

## Common mistakes

- **Local checks only** (compare with children): fails on the example and on the test
  where two deep values are swapped.
- **Sentinels that collide with real values**: using `INT_MIN`/`INT_MAX` (or even
  `LLONG_MIN`) as "no bound" breaks when a node actually holds that value. The tests use
  values up to ±2⁵⁰ to catch 32-bit sentinels. Use `None`/`Option`/a separate flag, or
  pass pointers to the bounding nodes (`NULL` meaning no bound).
- **Non-strict comparisons**: `<=` accepts duplicates, which this problem forbids.

## Going further

*Recover a BST* where exactly two nodes were swapped: in the inorder sequence there are
one or two "descents" (`prev > cur`); the first descent's `prev` and the last descent's
`cur` are the swapped pair. That is the scenario in one of the tests.
""",
    solution=r'''
def is_valid_bst(root):
    def ok(node, low, high):
        """Is every value in this subtree strictly inside (low, high)?
        None means 'no bound', which avoids sentinel collisions."""
        if node is None:
            return True
        v = node.val
        if (low is not None and v <= low) or (high is not None and v >= high):
            return False
        # Going left, this node becomes the new upper bound;
        # going right, it becomes the new lower bound. Older bounds still apply.
        return ok(node.left, low, v) and ok(node.right, v, high)

    return ok(root, None, None)
''',
    refs={
        "cpp": r'''
// Bounds are passed as pointers to nodes; nullptr means "unbounded",
// so no numeric sentinel can ever collide with a real value.
static bool ok(TreeNode* n, TreeNode* lo, TreeNode* hi) {
    if (!n) return true;
    if (lo && n->val <= lo->val) return false;
    if (hi && n->val >= hi->val) return false;
    return ok(n->left, lo, n) && ok(n->right, n, hi);
}

bool isValidBst(TreeNode* root) { return ok(root, nullptr, nullptr); }
''',
        "rust": RS + r'''
// Inorder walk with an explicit stack: values must strictly increase.
pub fn is_valid_bst(root: Option<Rc<RefCell<TreeNode>>>) -> bool {
    let mut stack: Vec<Rc<RefCell<TreeNode>>> = Vec::new();
    let mut prev: Option<i64> = None;        // None: nothing seen yet
    let mut cur = root;
    while cur.is_some() || !stack.is_empty() {
        while let Some(node) = cur {
            cur = node.borrow().left.clone();
            stack.push(node);
        }
        let node = stack.pop().unwrap();
        let v = node.borrow().val;
        if let Some(p) = prev {
            if v <= p { return false; }      // not strictly increasing
        }
        prev = Some(v);
        cur = node.borrow().right.clone();
    }
    true
}
''',
    },
    tests=[
        [[2, 1, 3]], [[5, 1, 4, None, None, 3, 6]], [[]], [[1]], [[1, 1]],
        [[5, 4, 6, None, None, 3, 7]],
        [[-2**50, None, 2**50]], [[2**50, -2**50]], [[0, None, -1]],
    ] + _vbst_tests(),
))

# ---------------------------------------------------------------- 14. kth smallest


def _kth_tests():
    rng = random.Random(1414)
    t = []
    for n in (20, 500):
        a = _rand_bst(rng, n)
        t.append([a, 1])
        t.append([a, n])
        t.append([a, rng.randint(1, n)])
    return t


PROBLEMS.append(dict(
    id="bst-kth-smallest",
    title="Kth Smallest Element in a BST",
    difficulty=2,
    tags=["bst", "inorder", "stack"],
    fn="kth_smallest",
    params=[["root", "tree"], ["k", "int"]],
    returns="int",
    statement=r"""
Given the root of a binary search tree with distinct values and an integer `k`, return
the **k-th smallest** value in the tree (1-indexed).
""",
    constraints=["1 ≤ k ≤ number of nodes ≤ 500", "values are distinct"],
    example_notes=[
        "Sorted values are 1, 2, 3, 4; the first is 1.",
        "Sorted values are 1, 2, 3, 4, 5, 6; the third is 3.",
    ],
    hints=[
        "Which traversal of a BST produces the values in sorted order?",
        "You do not need the whole sorted list. Can you stop early?",
        "Iterative inorder with a stack: count nodes as you pop them and return at the k-th pop.",
    ],
    explanation=r"""
## Intuition

Inorder (left, node, right) of a BST visits values in increasing order, because every
node's smaller values are in its left subtree (visited before it) and larger ones in its
right subtree (visited after). So the answer is simply the k-th node an inorder walk
pops. An **iterative** walk makes stopping early trivial.

## Approach

1. Run the standard iterative inorder (dive left pushing nodes, pop, go right).
2. Decrement `k` on every pop; when it hits 0, return that node's value.

```text
            5            k = 3
           / \
          3   6          dive 5,3,2,1     stack [5,3,2,1]
         / \             pop 1 (k=2), pop 2 (k=1), pop 3 (k=0) -> answer 3
        2   4
       /
      1
```

## Complexity

- **Time O(h + k)**: diving to the minimum costs `h`, and then each of the `k` pops does
  amortised O(1) work. Collecting the full inorder list first would be O(n).
- **Space O(h)** for the stack.

## Common mistakes

- **Off-by-one**: k is 1-indexed. Returning after `k` decrements to `0` (not `-1`) is
  right if you decrement *before* checking.
- **Building the whole list** works, but wastes time and memory when `k` is small.
- **Counting during a recursive walk** without a way to stop: you keep traversing after
  finding the answer. Return a sentinel or use a mutable counter plus an early return.

## Going further

If the tree is modified often and k-th queries are frequent, store in each node the size
of its left subtree (an *order statistic tree*). Then at each node compare `k` with
`left_size + 1` and go left, return, or go right with `k -= left_size + 1`: O(h) per query.
""",
    solution=r'''
def kth_smallest(root, k):
    stack = []
    cur = root
    while cur is not None or stack:
        # Dive left: the smallest unvisited value is at the bottom of this path.
        while cur is not None:
            stack.append(cur)
            cur = cur.left
        node = stack.pop()
        # Inorder pops come out in increasing order; this is the next smallest.
        k -= 1
        if k == 0:
            return node.val
        cur = node.right
    return -1  # unreachable for valid k
''',
    refs={
        "cpp": r'''
long long kthSmallest(TreeNode* root, long long k) {
    stack<TreeNode*> st;
    TreeNode* cur = root;
    while (cur || !st.empty()) {
        while (cur) { st.push(cur); cur = cur->left; }
        cur = st.top(); st.pop();
        if (--k == 0) return cur->val;       // k-th inorder pop
        cur = cur->right;
    }
    return -1;
}
''',
        "rust": RS + r'''
pub fn kth_smallest(root: Option<Rc<RefCell<TreeNode>>>, k: i64) -> i64 {
    let mut k = k;
    let mut stack: Vec<Rc<RefCell<TreeNode>>> = Vec::new();
    let mut cur = root;
    while cur.is_some() || !stack.is_empty() {
        while let Some(node) = cur {
            cur = node.borrow().left.clone();
            stack.push(node);
        }
        let node = stack.pop().unwrap();
        k -= 1;
        if k == 0 { return node.borrow().val; }
        cur = node.borrow().right.clone();
    }
    -1
}
''',
    },
    tests=[
        [[3, 1, 4, None, 2], 1], [[5, 3, 6, 2, 4, None, None, 1], 3], [[1], 1],
        [[2, 1, 3], 3], [_chain(list(range(10, 0, -1)), "L"), 7],
    ] + _kth_tests(),
))

# ---------------------------------------------------------------- 15. build tree


def _orders(root):
    pre, ino = [], []

    def go(n):
        if n is None:
            return
        pre.append(n.val)
        go(n.left)
        ino.append(n.val)
        go(n.right)
    go(root)
    return [pre, ino]


def _build_tests():
    rng = random.Random(1515)
    t = []
    for n in (12, 300, 600):
        vals = rng.sample(range(-3000, 3001), n)
        t.append(_orders(_rand_root(rng, vals)))
    return t


PROBLEMS.append(dict(
    id="tree-from-preorder-inorder",
    title="Construct Binary Tree from Preorder and Inorder",
    difficulty=2,
    tags=["tree", "divide and conquer", "hash map"],
    fn="build_tree",
    params=[["preorder", "int[]"], ["inorder", "int[]"]],
    returns="tree",
    statement=r"""
`preorder` and `inorder` are the preorder and inorder traversals of the same binary tree
whose values are all **distinct**. Rebuild the tree and return its root (an empty tree
for empty inputs).
""",
    constraints=["0 ≤ n ≤ 600", "values are distinct", "both arrays describe the same tree"],
    example_notes=[
        "3 is the root (first in preorder); in the inorder list 9 is to its left and 15, 20, 7 to its right.",
        "A single node.",
    ],
    hints=[
        "Which array tells you the root immediately? Where is the root in the other one?",
        "In inorder, everything left of the root belongs to the left subtree, everything right of it to the right subtree. That also tells you the subtree sizes.",
        "Recurse with index ranges instead of slicing, consume preorder left to right with a moving pointer, and find inorder positions with a hash map.",
    ],
    explanation=r"""
## Intuition

Preorder starts with the root. Inorder puts the root *between* its left and right
subtrees. So one lookup splits the problem into two smaller identical problems:

```text
preorder: [3 | 9 | 20 15 7]         inorder: [9 | 3 | 15 20 7]
           ^root                                  ^root at index 1
           left subtree size = 1 (one value left of 3 in inorder)
left : pre [9]          in [9]
right: pre [20 15 7]    in [15 20 7]  -> root 20, left [15], right [7]
```

Distinct values guarantee the root's position in `inorder` is unambiguous.

## Approach

1. Build `pos[value] = index in inorder` (O(n) once, instead of searching each time).
2. Keep a pointer `i` into `preorder`. Preorder lists root, then the entire left subtree,
   then the entire right subtree, so if you build left before right, the next unused
   preorder value is always the root of the subtree you are building.
3. `build(lo, hi)` builds the subtree whose inorder range is `[lo, hi)`:
   - empty range: return `None`;
   - `root = preorder[i]; i += 1; m = pos[root]`;
   - `root.left = build(lo, m)`, then `root.right = build(m + 1, hi)`.

```text
build(0,5): root 3 (m=1)
  build(0,1): root 9 (m=0) -> build(0,0)=None, build(1,1)=None
  build(2,5): root 20 (m=3)
    build(2,3): root 15
    build(4,5): root 7
```

## Complexity

- **Time O(n)**: each value becomes a node exactly once, and each `pos` lookup is O(1).
  Searching inorder linearly each time, or slicing arrays, makes it O(n²).
- **Space O(n)** for the map plus O(h) recursion.

## Common mistakes

- **Building the right subtree first** while consuming preorder from the front: the next
  preorder value belongs to the left subtree, so the tree comes out scrambled.
- **Slicing** (`preorder[1:m+1]`) in every call copies O(n) per level: correct but
  quadratic on a chain.
- **Off-by-one in ranges**: use half-open `[lo, hi)` consistently; the left range ends at
  `m`, the right starts at `m + 1`.
- **Rust**: build bottom-up and create the node last with
  `Rc::new(RefCell::new(TreeNode { val, left, right }))`; no `borrow_mut` needed.

## Going further

The same split works for postorder + inorder (the root is the *last* postorder value;
build the right subtree first while consuming from the back). Preorder + postorder alone
do not determine a tree uniquely unless every node has 0 or 2 children.
""",
    solution=r'''
def build_tree(preorder, inorder):
    # Where each value sits in the inorder list: O(1) root lookups.
    pos = {v: i for i, v in enumerate(inorder)}
    nxt = 0  # next unused preorder index = root of the subtree being built

    def build(lo, hi):
        """Build the subtree whose values are inorder[lo:hi]."""
        nonlocal nxt
        if lo >= hi:
            return None
        val = preorder[nxt]
        nxt += 1
        m = pos[val]
        node = TreeNode(val)
        # Order matters: preorder lists the whole LEFT subtree before the right,
        # so the left must consume preorder values first.
        node.left = build(lo, m)
        node.right = build(m + 1, hi)
        return node

    return build(0, len(inorder))
''',
    refs={
        "c": r'''
/* Values may be negative, so map value -> inorder index with a small
   open-addressing hash table instead of a direct array. */
typedef struct { long long key; int val; bool used; } Slot;
static Slot* tbl; static int cap;
static void put(long long k, int v) {
    unsigned long long h = (unsigned long long)k * 11400714819323198485ull;
    int i = (int)(h % (unsigned)cap);
    while (tbl[i].used) i = (i + 1) % cap;
    tbl[i].key = k; tbl[i].val = v; tbl[i].used = true;
}
static int get(long long k) {
    unsigned long long h = (unsigned long long)k * 11400714819323198485ull;
    int i = (int)(h % (unsigned)cap);
    while (!(tbl[i].used && tbl[i].key == k)) i = (i + 1) % cap;
    return tbl[i].val;
}

static long long* pre; static int nxt;
static struct TreeNode* build(int lo, int hi) {
    if (lo >= hi) return NULL;
    struct TreeNode* n = malloc(sizeof *n);
    n->val = pre[nxt++];
    int m = get(n->val);
    n->left = build(lo, m);                  /* left first: preorder order */
    n->right = build(m + 1, hi);
    return n;
}

struct TreeNode* build_tree(long long* preorder, int preorderSize, long long* inorder, int inorderSize) {
    (void)preorderSize;
    cap = 2 * inorderSize + 1;
    tbl = calloc((size_t)cap, sizeof(Slot));
    for (int i = 0; i < inorderSize; i++) put(inorder[i], i);
    pre = preorder; nxt = 0;
    struct TreeNode* root = build(0, inorderSize);
    free(tbl);
    return root;
}
''',
        "cpp": r'''
static TreeNode* buildRange(const vector<long long>& pre, int& nxt, int lo, int hi,
                            unordered_map<long long, int>& pos) {
    if (lo >= hi) return nullptr;
    long long v = pre[nxt++];
    int m = pos[v];
    TreeNode* n = new TreeNode(v);
    n->left = buildRange(pre, nxt, lo, m, pos);
    n->right = buildRange(pre, nxt, m + 1, hi, pos);
    return n;
}

TreeNode* buildTree(vector<long long>& preorder, vector<long long>& inorder) {
    unordered_map<long long, int> pos;
    for (int i = 0; i < (int)inorder.size(); i++) pos[inorder[i]] = i;
    int nxt = 0;
    return buildRange(preorder, nxt, 0, (int)inorder.size(), pos);
}
''',
        "rust": RS + r'''
use std::collections::HashMap;

fn build(pre: &[i64], nxt: &mut usize, lo: usize, hi: usize,
         pos: &HashMap<i64, usize>) -> Option<Rc<RefCell<TreeNode>>> {
    if lo >= hi { return None; }
    let val = pre[*nxt];
    *nxt += 1;
    let m = pos[&val];
    let left = build(pre, nxt, lo, m, pos);      // left subtree first
    let right = build(pre, nxt, m + 1, hi, pos);
    Some(Rc::new(RefCell::new(TreeNode { val, left, right })))
}

pub fn build_tree(preorder: Vec<i64>, inorder: Vec<i64>) -> Option<Rc<RefCell<TreeNode>>> {
    let pos: HashMap<i64, usize> = inorder.iter().enumerate().map(|(i, &v)| (v, i)).collect();
    let mut nxt = 0;
    build(&preorder, &mut nxt, 0, inorder.len(), &pos)
}
''',
    },
    tests=[
        [[3, 9, 20, 15, 7], [9, 3, 15, 20, 7]], [[-1], [-1]], [[], []],
        [[1, 2, 3], [3, 2, 1]], [[1, 2, 3], [1, 2, 3]], [[1, 2, 4, 5, 3, 6], [4, 2, 5, 1, 3, 6]],
        _orders(_de(_chain(list(range(300)), "Z"))),
    ] + _build_tests(),
))

# ---------------------------------------------------------------- 16. right side view

PROBLEMS.append(dict(
    id="tree-right-side-view",
    title="Binary Tree Right Side View",
    difficulty=2,
    tags=["tree", "bfs", "dfs"],
    fn="right_side_view",
    params=[["root", "tree"]],
    returns="int[]",
    statement=r"""
Imagine standing to the right of a binary tree. Return the values you can see, from top
to bottom: for each depth, the **rightmost** node at that depth.
""",
    constraints=["0 ≤ number of nodes ≤ 800", "-100 ≤ node.val ≤ 100"],
    example_notes=[
        "Depth 0: 1, depth 1: 3, depth 2: 4 (the 5 under 2 is hidden behind 4).",
        "Node 4 hangs on the LEFT branch, but it is the only node at depth 2, so it is visible.",
    ],
    hints=[
        "You see exactly one node per depth. Which one?",
        "Level order BFS: the last node of each level is visible.",
        "Or DFS visiting right before left, recording a node when its depth equals the number of values seen so far.",
    ],
    explanation=r"""
## Intuition

The view shows one node per level: the last one when the level is read left to right.
The trap is believing it is "the right spine": a deep left subtree peeks out below a
short right one.

```text
         1        <- see 1
        / \
       2   3      <- see 3
        \
         5        <- see 5 (nothing further right at this depth)
```

## Approach

**BFS:** run level order and keep the last value of every level.

**DFS (right first):** visit `node, right, left`, passing `depth`. The first node you meet
at any depth is the rightmost one, because you always try the right side first. Record
it when `depth == len(result)` (that depth has not been seen yet).

```text
visit 1 d0 -> result [1]
visit 3 d1 -> result [1,3]
visit 2 d1 -> depth 1 already seen
visit 5 d2 -> result [1,3,5]
```

## Complexity

- **Time O(n)** either way.
- **Space**: BFS O(w) (widest level), DFS O(h) (height).

## Common mistakes

- **Walking only `.right` pointers** misses levels that exist only on the left (example 2).
- **DFS left-first with "first seen" recording** gives the *left* view instead; with left
  first you would need to *overwrite* `result[depth]` every time.
- **Empty tree**: return `[]`.

## Going further

The left view, the bottom view and the top view (by horizontal distance from the root)
are all variations; the latter two need a map from column offset to node, filled by BFS so
that ties break by depth.
""",
    solution=r'''
def right_side_view(root):
    result = []

    def dfs(node, depth):
        if node is None:
            return
        # Right subtree is explored before left, so the FIRST node we reach
        # at each depth is the rightmost one: record it only then.
        if depth == len(result):
            result.append(node.val)
        dfs(node.right, depth + 1)
        dfs(node.left, depth + 1)

    dfs(root, 0)
    return result
''',
    refs={
        "cpp": r'''
vector<long long> rightSideView(TreeNode* root) {
    vector<long long> res;
    if (!root) return res;
    queue<TreeNode*> q;
    q.push(root);
    while (!q.empty()) {
        size_t sz = q.size();
        for (size_t i = 0; i < sz; i++) {
            TreeNode* n = q.front(); q.pop();
            if (i + 1 == sz) res.push_back(n->val);   // last node of the level
            if (n->left) q.push(n->left);
            if (n->right) q.push(n->right);
        }
    }
    return res;
}
''',
        "rust": RS + r'''
fn dfs(node: &Option<Rc<RefCell<TreeNode>>>, depth: usize, out: &mut Vec<i64>) {
    if let Some(rc) = node {
        let n = rc.borrow();
        if depth == out.len() { out.push(n.val); }   // first visit at this depth
        dfs(&n.right, depth + 1, out);               // right side first
        dfs(&n.left, depth + 1, out);
    }
}

pub fn right_side_view(root: Option<Rc<RefCell<TreeNode>>>) -> Vec<i64> {
    let mut out = Vec::new();
    dfs(&root, 0, &mut out);
    out
}
''',
    },
    tests=[
        [[1, 2, 3, None, 5, None, 4]], [[1, 2, 3, 4]], [[]], [[1, None, 3]],
        [[1, 2, 3, None, 5]], [_chain(list(range(1, 30)), "L")],
        [_rand_tree(_R, 50)], [_rand_tree(_R, 800)],
    ],
))

# ---------------------------------------------------------------- 17. max path sum

PROBLEMS.append(dict(
    id="tree-max-path-sum",
    title="Binary Tree Maximum Path Sum",
    difficulty=3,
    tags=["tree", "dfs", "dynamic programming"],
    fn="max_path_sum",
    params=[["root", "tree"]],
    returns="int",
    statement=r"""
A **path** is a sequence of nodes where each adjacent pair is connected by an edge; a
node appears at most once, and the path need not pass through the root. It contains
**at least one** node. The path sum is the sum of its values.

Given a non-empty binary tree, return the **maximum** path sum.
""",
    constraints=["1 ≤ number of nodes ≤ 500", "-1000 ≤ node.val ≤ 1000"],
    example_notes=[
        "The path 2 → 1 → 3 sums to 6.",
        "The best path is 15 → 20 → 7 = 42; including -10 or 9 would only lower it.",
    ],
    hints=[
        "Like the diameter: every path has one highest node where it bends. What is the best path bending at a node?",
        "Define gain(node) = best sum of a DOWNWARD path starting at node. A child's gain is only worth taking if it is positive.",
        "At each node: best = max(best, val + max(0, gain(L)) + max(0, gain(R))); return val + max(0, gain(L), gain(R)).",
    ],
    explanation=r"""
## Intuition

This is the Diameter problem with weights, and negative weights at that. Every path has
a topmost node (its **bend**). The best path bending at node `x` is
`x.val` plus the best downward path into the left (if that helps) plus the best downward
path into the right (if that helps).

So we need, for every node, its **gain**: the best sum of a path that *starts* at the node
and goes *down* one side. A parent can extend only one branch of the child's path (a path
cannot fork), which is why the gain uses `max(left, right)` while the bend uses both.

## Approach

Postorder helper `gain(node)`:

```text
gain(None) = 0
l = max(0, gain(left))        # a negative branch is better left out
r = max(0, gain(right))
best = max(best, node.val + l + r)   # path bending here
return node.val + max(l, r)          # path continuing up to the parent
```

Initialize `best` to negative infinity (or the root's value), **not 0**: if every value is
negative the answer is the single largest value, e.g. `[-3]` → `-3`.

Trace on `[-10,9,20,null,null,15,7]`:

```text
          -10          node  l   r   bend         gain returned
          /  \         9     0   0   9            9
         9    20       15    0   0   15           15
             /  \      7     0   0   7            7
            15   7     20    15  7   42  <- best  35
                       -10   9   35  34           25
```

## Complexity

- **Time O(n)**: one postorder pass.
- **Space O(h)** for recursion.

## Common mistakes

- **`best = 0` initially**: wrong for all-negative trees (two tests).
- **Returning `val + l + r` to the parent**: that path forks at this node, and the parent
  would add a third branch. Return only one side.
- **Clamping the node's own value at 0**: the path must contain at least one node, and the
  node itself is mandatory once you are at its bend. Only *children's* gains are clamped.
- **Python closures**: `nonlocal best` is required to rebind the outer variable.

## Going further

The same "gain vs bend" decomposition solves many tree-path questions: longest path with
the same value (*longest univalue path*), longest path where consecutive values differ by
one, or maximum product variants. Identify what the parent can extend (return it) and
what can only be completed here (record it).
""",
    solution=r'''
def max_path_sum(root):
    best = -math.inf   # NOT 0: all-negative trees must return their largest value

    def gain(node):
        """Best sum of a downward path that starts at `node` (one branch only)."""
        nonlocal best
        if node is None:
            return 0
        # A branch with a negative total only hurts; we may simply not take it.
        l = max(0, gain(node.left))
        r = max(0, gain(node.right))
        # Best path whose highest node is this one: it may use both branches.
        best = max(best, node.val + l + r)
        # The parent can extend only one of our branches (paths do not fork).
        return node.val + max(l, r)

    gain(root)
    return best
''',
    refs={
        "c": r'''
static long long best;

static long long gain(struct TreeNode* n) {
    if (!n) return 0;
    long long l = gain(n->left);  if (l < 0) l = 0;    /* drop harmful branches */
    long long r = gain(n->right); if (r < 0) r = 0;
    if (n->val + l + r > best) best = n->val + l + r;  /* path bending at n */
    return n->val + (l > r ? l : r);                   /* one branch upward */
}

long long max_path_sum(struct TreeNode* root) {
    best = LLONG_MIN;          /* reset: globals persist between calls */
    gain(root);
    return best;
}
''',
        "cpp": r'''
static long long gainOf(TreeNode* n, long long& best) {
    if (!n) return 0;
    long long l = max(0LL, gainOf(n->left, best));
    long long r = max(0LL, gainOf(n->right, best));
    best = max(best, n->val + l + r);
    return n->val + max(l, r);
}

long long maxPathSum(TreeNode* root) {
    long long best = LLONG_MIN;
    gainOf(root, best);
    return best;
}
''',
        "rust": RS + r'''
fn gain(node: &Option<Rc<RefCell<TreeNode>>>, best: &mut i64) -> i64 {
    match node {
        None => 0,
        Some(rc) => {
            let n = rc.borrow();
            let l = gain(&n.left, best).max(0);
            let r = gain(&n.right, best).max(0);
            *best = (*best).max(n.val + l + r);
            n.val + l.max(r)
        }
    }
}

pub fn max_path_sum(root: Option<Rc<RefCell<TreeNode>>>) -> i64 {
    let mut best = i64::MIN;
    gain(&root, &mut best);
    best
}
''',
    },
    tests=[
        [[1, 2, 3]], [[-10, 9, 20, None, None, 15, 7]], [[-3]], [[-2, -1, -5]],
        [[2, -1]], [[5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1]],
        [[1, -2, 3, 4, None, None, -6, -1, 8]],
        [_chain([(-1) ** i * (i % 37) for i in range(600)], "Z")],
        [_rand_tree(_R, 100, -1000, 1000)], [_rand_tree(_R, 500, -1000, 1000)],
        [_rand_tree(_R, 200, -1000, -1)],
    ],
))
