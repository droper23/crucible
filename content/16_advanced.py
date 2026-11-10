"""Track 16: Advanced Structures & Algorithms."""
import random
import string

TRACK = dict(
    id="advanced",
    title="Advanced Structures & Algorithms",
    order=16,
    icon="◈",
    blurb="Tries, segment and Fenwick trees, string matching, heaps in pairs, bitmask DP, shortest paths and max flow.",
    intro=r"""
The earlier tracks gave you arrays, hash maps, stacks, heaps, trees and graphs. This track
is about the structures and algorithms you reach for when those are *almost* fast enough:
the query is O(n) and you need O(log n), the search is exponential and you need 2ⁿ·n²
instead of n!, the string match is O(n·m) and you need O(n + m).

## Amortized analysis

Several structures here have operations whose *individual* cost varies wildly but whose
*total* cost over a sequence is small. That is amortized analysis.

* **KMP's failure pointer** can fall back many steps on one character, but it can only
  fall back as far as it previously advanced, and it advances at most once per character.
  Total work over the text: at most 2n steps, so O(1) amortized per character.
* **Lazy deletion in heaps** (sliding-window median): a removal just records "this value is
  dead"; the real pop happens later when the value reaches the top. Every element is pushed
  once and popped at most once, so the total is O(n log n) even though a single operation
  may pop many dead entries.
* **Dynamic arrays** (`append`) double their capacity; copying is O(n) occasionally but
  O(1) amortized.

The *potential method* makes this precise: define a potential Φ (e.g. "current KMP state
length" or "dead entries in the heap"); cheap operations raise Φ by O(1), expensive ones
pay for themselves by lowering it.

## When to reach for what

```text
"prefix" / "starts with" / many words on a grid ......... Trie
range query + point update (sum, min, max, gcd) ........... Segment tree
prefix sums with updates, counting "smaller before me" .... Fenwick (binary indexed) tree
find a pattern in a text, all occurrences ................. KMP / Z-function
compare many substrings of a fixed length ................. Rolling hash (Rabin–Karp)
longest increasing anything, n up to 10⁵ .................. Patience sorting + binary search
running median, k-th element in a stream .................. Two heaps (max-heap | min-heap)
"visit every node once", n ≤ 20 ........................... Bitmask DP over subsets
weighted shortest path, non-negative weights .............. Dijkstra with a heap
"how much can flow", bipartite matching, min cut .......... Max flow (Edmonds–Karp / Dinic)
```

## Complexity table

| structure / algorithm | build | query | update | space |
|---|---|---|---|---|
| Trie (alphabet Σ, word length L) | O(total chars) | O(L) | O(L) insert | O(total chars · Σ) |
| Segment tree | O(n) | O(log n) range | O(log n) point | O(2n)–O(4n) |
| Fenwick tree | O(n) or O(n log n) | O(log n) prefix | O(log n) point | O(n) |
| KMP | O(m) failure table | O(n) scan | — | O(m) |
| Rabin–Karp | O(L) first hash | O(1) roll | — | O(n) for the set |
| LIS (patience) | — | O(n log n) total | — | O(n) |
| Two-heap median | — | O(1) median | O(log n) insert | O(n) |
| Held–Karp TSP | — | O(2ⁿ · n²) | — | O(2ⁿ · n) |
| Dijkstra (binary heap) | — | O((V + E) log V) | — | O(V + E) |
| Edmonds–Karp | — | O(V · E²) | — | O(V + E) |

## Two shapes of tree you will build by hand

A **segment tree** stores, for each node, the answer for a contiguous range; the root covers
everything, children split the range in half. With `n` leaves stored at positions
`n … 2n−1` of an array, the parent of `i` is `i // 2`:

```text
            [1] sum(0..7)
        [2] 0..3        [3] 4..7
      [4]0..1 [5]2..3 [6]4..5 [7]6..7
      8  9    10 11   12 13   14 15      ← leaves = nums
```

A **Fenwick tree** is a leaner cousin for prefix sums. Index `i` (1-based) stores the sum of
the `i & -i` elements ending at `i`. Walking `i -= i & -i` visits O(log n) disjoint blocks that
tile the prefix `1..i`; walking `i += i & -i` visits every block that contains `i`.

```text
i:      1   2   3   4   5   6   7   8
covers: 1  1-2  3  1-4  5  5-6  7  1-8
```

## Design problems as op lists

Some problems here are classes (`Trie`, `MedianFinder`, a segment tree). As elsewhere in
Crucible they are tested through a function that receives a list of operation names and
their arguments, and returns the outputs. Write the class first, then a tiny driver loop;
in an interview you would be asked for the class.

## Language notes

* **Python**: `heapq` is a min-heap only; push negated values for a max-heap. Recursion is
  slow and capped, so prefer iterative segment trees and explicit stacks for deep searches.
* **C++**: `priority_queue` is a max-heap; use `greater<>` for a min-heap. `multiset` gives an
  ordered multiset (erase one copy with `s.erase(s.find(x))`, not `s.erase(x)`, which removes all).
* **Rust**: `BinaryHeap` is a max-heap; wrap in `std::cmp::Reverse` for a min-heap.
  `BTreeMap<K, count>` is the idiomatic ordered multiset. Index arrays with `usize` and
  convert at the boundaries.
""",
)


def _rng(seed):
    return random.Random(seed)


# ======================================================================== Trie
def _trie_tests():
    def gen(seed, nops, alpha, maxlen):
        r = _rng(seed)
        ops, args, words = [], [], []
        for _ in range(nops):
            op = r.choice(["insert", "insert", "search", "startsWith"])
            if words and r.random() < 0.5:
                w = r.choice(words)
                if op == "startsWith" or r.random() < 0.3:
                    w = w[: r.randint(1, len(w))]
            else:
                w = "".join(r.choice(alpha) for _ in range(r.randint(1, maxlen)))
            if op == "insert":
                words.append(w)
            ops.append(op)
            args.append(w)
        return [ops, args]

    return [
        [["insert", "search", "search", "startsWith", "insert", "search"],
         ["apple", "apple", "app", "app", "app", "app"]],
        [["insert", "insert", "search", "startsWith", "startsWith"],
         ["a", "a", "a", "a", "b"]],
        [["search", "startsWith"], ["x", "x"]],
        [["insert", "insert", "insert", "search", "search", "startsWith", "startsWith", "search"],
         ["car", "cart", "care", "ca", "cart", "ca", "carts", "care"]],
        [["insert", "startsWith", "search", "insert", "search"],
         ["abcdefghij", "abcdefghij", "abcdefghi", "abcdefghi", "abcdefghi"]],
        gen(1601, 60, "ab", 4),
        gen(1602, 150, "abc", 6),
        gen(1603, 500, string.ascii_lowercase[:6], 8),
    ]


P_TRIE = dict(
    id="implement-trie-ops",
    title="Implement a Trie",
    difficulty=3,
    tags=["trie", "design", "string"],
    fn="trie_ops",
    params=[["ops", "str[]"], ["args", "str[]"]],
    returns="bool[]",
    statement=r"""
Implement a **trie** (prefix tree) supporting three operations, then replay a list of
operations against an initially empty trie.

* `insert(word)`: add `word`. Returns `true` if the word was **not** already present, `false` if it was (the trie is unchanged in that case).
* `search(word)`: `true` if `word` was inserted before.
* `startsWith(prefix)`: `true` if some inserted word starts with `prefix` (a word is a prefix of itself).

`ops[i]` is the operation name and `args[i]` its string argument. Return the list of
results, one boolean per operation.
""",
    constraints=["1 ≤ len(ops) = len(args) ≤ 500",
                 "1 ≤ len(args[i]) ≤ 10, lowercase English letters"],
    example_notes=[
        "After inserting `apple`, `app` is a prefix but not a word, until it is inserted too.",
        "Inserting `a` twice: the second insert returns `false`.",
    ],
    hints=[
        "Each node represents a prefix. It needs children (one per next letter) and a flag saying whether a word ends exactly here.",
        "`search` and `startsWith` both walk the same path letter by letter; they differ only in what they check at the end.",
        "`insert` returns whether the end node's `is_end` flag was false before you set it.",
    ],
    explanation=r"""
## Intuition

A hash set answers "is this word present?" in O(L), but "does any word start with `ca`?"
would need a scan of every word. A trie shares prefixes: all words starting with `ca` live
under a single node, so prefix questions cost O(L) too.

```text
insert car, cart, care

 (root)
   └─ c
      └─ a
         └─ r*          * = is_end (a word ends here)
            ├─ t*
            └─ e*
```

## Approach

**The class** (this is what an interviewer wants to see):

```python
class TrieNode:
    def __init__(self):
        self.children = {}      # letter -> TrieNode (or a fixed array of 26)
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
    def insert(self, word):
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        was_new = not node.is_end
        node.is_end = True
        return was_new
    def _walk(self, s):          # node for prefix s, or None
        node = self.root
        for ch in s:
            node = node.children.get(ch)
            if node is None:
                return None
        return node
    def search(self, word):
        node = self._walk(word)
        return node is not None and node.is_end
    def starts_with(self, prefix):
        return self._walk(prefix) is not None
```

The driver loops over `ops`, calls the matching method and collects results.

Trace of example 1:

| op | arg | result | why |
|---|---|---|---|
| insert | apple | true | new |
| search | apple | true | path exists, end flag set |
| search | app | false | path exists, `p` node has no end flag |
| startsWith | app | true | path exists |
| insert | app | true | flag on `p` was false |
| search | app | true | now flagged |

## Complexity

* **Time:** O(L) per operation, independent of how many words are stored.
* **Space:** O(total characters inserted) nodes. With a 26-slot array per node, that is
  26 pointers per node: fast but memory hungry; a hash map per node is compact but slower.

## Common mistakes

* Treating "path exists" as "word exists": `search("app")` after only `apple` must be false.
* Forgetting that a node can be both an end and an interior node (`car` and `cart`).
* In C/C++: leaking nodes, or using `char - 'a'` on characters outside `a–z`.
* Rust ownership pain with recursive `Box<Node>` children: store all nodes in a `Vec` and
  use indices instead (the arena pattern in the Rust reference).

## Going further

* **Delete** a word: unset `is_end`, then prune nodes that have no children and no flag on the way back up.
* Store a **count** per node to answer "how many words start with p?" in O(L).
* Tries power autocomplete, IP routing (binary tries over address bits), and the
  "maximum XOR pair" trick (insert numbers bit by bit, greedily walk the opposite bit).
""",
    solution=r'''def trie_ops(ops, args):
    class TrieNode:
        __slots__ = ("children", "is_end")

        def __init__(self):
            self.children = {}       # next letter -> child node
            self.is_end = False      # does an inserted word end exactly at this node?

    root = TrieNode()                # represents the empty prefix

    def walk(s):
        """Follow s from the root; return the node for that prefix, or None."""
        node = root
        for ch in s:
            node = node.children.get(ch)
            if node is None:         # path breaks: no word has this prefix
                return None
        return node

    def insert(word):
        node = root
        for ch in word:
            # Create missing nodes as we go; shared prefixes reuse existing ones.
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        was_new = not node.is_end    # report whether this is a new word
        node.is_end = True
        return was_new

    out = []
    for op, s in zip(ops, args):
        if op == "insert":
            out.append(insert(s))
        elif op == "search":
            node = walk(s)
            out.append(node is not None and node.is_end)   # path AND end flag
        else:                        # "startsWith": the path existing is enough
            out.append(walk(s) is not None)
    return out
''',
    refs={
        "c": r"""// Arena trie: every node lives in one calloc-ed array and children are indices.
// Index 0 is the root, and nothing ever points back at the root, so a child
// index of 0 can safely mean "no child" (and calloc gives us that for free).
typedef struct { int next[26]; bool end; } TrieNode;

// Follow `s` from the root. Returns the node reached, or -1 if the path breaks.
static int trie_walk(const TrieNode* t, const char* s) {
    int cur = 0;
    for (; *s; s++) {
        cur = t[cur].next[*s - 'a'];
        if (cur == 0) return -1;
    }
    return cur;
}

bool* trie_ops(char** ops, int opsSize, char** args, int argsSize, int* returnSize) {
    // Worst case every inserted letter creates a node: 1 (root) + total letters.
    // Sizing the arena up front means no realloc, so no pointers can go stale.
    int cap = 1;
    for (int i = 0; i < argsSize; i++) cap += (int)strlen(args[i]);
    TrieNode* t = calloc((size_t)cap, sizeof *t);
    int used = 1;

    bool* out = malloc(sizeof(bool) * (size_t)(opsSize > 0 ? opsSize : 1));
    for (int i = 0; i < opsSize; i++) {
        const char* w = args[i];
        if (strcmp(ops[i], "insert") == 0) {
            int cur = 0;
            for (const char* p = w; *p; p++) {
                int c = *p - 'a';
                if (t[cur].next[c] == 0) t[cur].next[c] = used++;   // grow a new branch
                cur = t[cur].next[c];
            }
            out[i] = !t[cur].end;     // true only if this word is new
            t[cur].end = true;
        } else if (strcmp(ops[i], "search") == 0) {
            int n = trie_walk(t, w);
            out[i] = n >= 0 && t[n].end;   // the path exists AND a word ends here
        } else {                            // "startsWith"
            out[i] = trie_walk(t, w) >= 0;  // the path existing is enough
        }
    }
    free(t);
    *returnSize = opsSize;
    return out;
}""",
        "cpp": r"""class Trie {
    // Arena of nodes: children[c] is an index into `nodes` (0 = none, since root is 0
    // and nothing ever points back to the root).
    struct Node { int next[26] = {}; bool end = false; };
    vector<Node> nodes{1};
    int walk(const string& s) const {
        int cur = 0;
        for (char ch : s) { cur = nodes[cur].next[ch - 'a']; if (!cur) return -1; }
        return cur;
    }
public:
    bool insert(const string& w) {
        int cur = 0;
        for (char ch : w) {
            int c = ch - 'a';
            if (!nodes[cur].next[c]) { nodes[cur].next[c] = nodes.size(); nodes.emplace_back(); }
            cur = nodes[cur].next[c];   // re-index after emplace_back: references may dangle
        }
        bool fresh = !nodes[cur].end;
        nodes[cur].end = true;
        return fresh;
    }
    bool search(const string& w) const { int n = walk(w); return n >= 0 && nodes[n].end; }
    bool startsWith(const string& p) const { return walk(p) >= 0; }
};

vector<bool> trieOps(vector<string>& ops, vector<string>& args) {
    Trie t;
    vector<bool> out;
    for (size_t i = 0; i < ops.size(); i++) {
        if (ops[i] == "insert") out.push_back(t.insert(args[i]));
        else if (ops[i] == "search") out.push_back(t.search(args[i]));
        else out.push_back(t.startsWith(args[i]));
    }
    return out;
}""",
        "rust": r"""// Arena-allocated trie: nodes live in a Vec and refer to each other by index.
// This sidesteps Box<Option<...>> ownership juggling entirely.
struct Trie {
    next: Vec<[usize; 26]>, // 0 means "no child" (the root, index 0, is never a child)
    end: Vec<bool>,
}

impl Trie {
    fn new() -> Self {
        Trie { next: vec![[0; 26]], end: vec![false] }
    }
    fn insert(&mut self, w: &str) -> bool {
        let mut cur = 0;
        for b in w.bytes() {
            let c = (b - b'a') as usize;
            if self.next[cur][c] == 0 {
                self.next.push([0; 26]);
                self.end.push(false);
                self.next[cur][c] = self.next.len() - 1;
            }
            cur = self.next[cur][c];
        }
        let fresh = !self.end[cur];
        self.end[cur] = true;
        fresh
    }
    fn walk(&self, s: &str) -> Option<usize> {
        let mut cur = 0;
        for b in s.bytes() {
            cur = self.next[cur][(b - b'a') as usize];
            if cur == 0 {
                return None;
            }
        }
        Some(cur)
    }
}

pub fn trie_ops(ops: Vec<String>, args: Vec<String>) -> Vec<bool> {
    let mut t = Trie::new();
    ops.iter()
        .zip(args.iter())
        .map(|(op, s)| match op.as_str() {
            "insert" => t.insert(s),
            "search" => t.walk(s).map_or(false, |n| t.end[n]),
            _ => t.walk(s).is_some(),
        })
        .collect()
}""",
    },
    tests=_trie_tests(),
)


# ======================================================================== Word search II
def _ws_board(r, R, C, alpha):
    return [[r.choice(alpha) for _ in range(C)] for _ in range(R)]


def _ws_tests():
    out = [
        [[["o", "a", "a", "n"], ["e", "t", "a", "e"], ["i", "h", "k", "r"], ["i", "f", "l", "v"]],
         ["oath", "pea", "eat", "rain"]],
        [[["a", "b"], ["c", "d"]], ["abcb"]],
        [[["a"]], ["a", "b", "aa"]],
        [[["a", "b"], ["c", "d"]], ["ab", "ac", "abdc", "acdb", "ad", "dcba", "bd"]],
        [[["a", "a"], ["a", "a"]], ["aaaa", "aaaaa", "aaa", "a"]],
    ]
    r = _rng(1611)
    for seed_r, R, C, alpha, nw in [(1, 6, 6, "abcde", 120), (2, 12, 12, "abcdefgh", 600)]:
        rr = _rng(1611 + seed_r)
        board = _ws_board(rr, R, C, alpha)
        words = set()
        # half the words are real paths on the board, half are random strings
        while len(words) < nw:
            if rr.random() < 0.5:
                i, j = rr.randrange(R), rr.randrange(C)
                seen = {(i, j)}
                w = board[i][j]
                for _ in range(rr.randint(0, 7)):
                    nb = [(i + di, j + dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))
                          if 0 <= i + di < R and 0 <= j + dj < C and (i + di, j + dj) not in seen]
                    if not nb:
                        break
                    i, j = rr.choice(nb)
                    seen.add((i, j))
                    w += board[i][j]
                words.add(w)
            else:
                words.add("".join(rr.choice(alpha) for _ in range(rr.randint(1, 8))))
        words = sorted(words)
        rr.shuffle(words)
        out.append([board, words])
    del r
    return out


P_WORDSEARCH = dict(
    id="word-search-ii-trie",
    title="Word Search II",
    difficulty=4,
    tags=["trie", "backtracking", "grid"],
    fn="find_words",
    params=[["board", "str[][]"], ["words", "str[]"]],
    returns="str[]",
    statement=r"""
`board` is a grid of single lowercase letters. A word can be **traced** on the board by
starting at any cell and repeatedly stepping to a horizontally or vertically adjacent cell;
the same cell may not be used twice within one word.

Return every word from `words` that can be traced, **sorted** in ascending (lexicographic)
order. `words` contains no duplicates.
""",
    constraints=["1 ≤ rows, cols ≤ 12", "1 ≤ len(words) ≤ 600, distinct",
                 "1 ≤ len(words[i]) ≤ 10, lowercase letters"],
    example_notes=["`oath` and `eat` can be traced; `pea` has no `p`, `rain` has no path.",
                   "`abcb` would need to reuse the `b` cell."],
    hints=[
        "Running a separate grid search per word repeats the same exploration over and over. Can all words be searched at once?",
        "Put the words in a trie. DFS from every cell, moving down the trie as you move across the board; stop as soon as the current path is not a prefix of any word.",
        "Store the complete word at its end node and remove it once found (so it is reported once). Prune trie nodes that become empty so dead branches stop being explored.",
    ],
    explanation=r"""
## Intuition

Searching each word separately costs `words × cells × 4^L`. But the searches overlap: every
word starting with `oa` explores the same `o → a` paths. A trie of all words lets one DFS
explore the board **once**, following the trie in lockstep: a board path is extended only
while it spells a prefix of some word. The trie is the pruning oracle.

## Approach

1. Build a trie from `words`; at each word's last node store the word itself.
2. For every cell whose letter is a child of the root, DFS(cell, root):
   * `node = parent.children[letter]`; if `node` holds a word, record it and clear it
     (so it is reported once).
   * Mark the cell visited (overwrite with `#`), recurse into the four neighbours whose
     letters are children of `node`, then restore the cell.
   * If `node` has no children and no word left, delete it from `parent`: future
     searches will not walk into this exhausted branch.
3. Sort the found words.

Trace on example 1 (only the successful branches):

```text
o(0,0) → a(0,1) → t(1,1) → h(2,1)     "oath" found, node removed
e(1,0)? root has 'e' → a? (1,0) neighbours: o,t,i  → no 'a' next to it
e(1,3) → a(1,2) → t(1,1)               "eat" found
```

## Complexity

* **Time:** O(R·C·4·3^(L−1)) in the worst case (first step has 4 directions, later ones 3
  because you can't go back), with L ≤ 10, plus O(total word length) to build the trie.
  In practice pruning makes it far smaller.
* **Space:** O(total word length) for the trie, O(L) recursion depth.

## Common mistakes

* Reporting a word twice when it can be traced along two different paths (remove it on first find).
* Forgetting to restore the cell after backtracking.
* Checking `visited` with a separate set per path: correct, but a cell overwrite is O(1) and allocation-free.
* Mutating the trie (pruning) while iterating over a node's children in a language that forbids it.
* Not sorting the result (the problem demands sorted output).

## Going further

* For a single word, plain backtracking is fine (**Word Search I**).
* **Boggle solvers** use exactly this algorithm with a dictionary of 10⁵ words.
* A DAWG (directed acyclic word graph) compresses the trie by also sharing *suffixes*.
""",
    solution=r'''def find_words(board, words):
    END = "$"                        # key under which a node stores the complete word
    root = {}
    for w in words:                  # trie as nested dicts: letter -> child dict
        node = root
        for ch in w:
            node = node.setdefault(ch, {})
        node[END] = w

    R, C = len(board), len(board[0])
    found = []

    def dfs(r, c, parent):
        ch = board[r][c]
        node = parent[ch]            # the trie node for the path ending at (r, c)
        if END in node:
            found.append(node.pop(END))   # pop: report each word once
        board[r][c] = "#"            # mark visited for the rest of this path
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            # Only step where the next letter continues some word's prefix.
            if 0 <= nr < R and 0 <= nc < C and board[nr][nc] in node:
                dfs(nr, nc, node)
        board[r][c] = ch             # backtrack: restore the cell
        if not node:                 # nothing left below: prune this branch for good
            parent.pop(ch)

    for r in range(R):
        for c in range(C):
            if board[r][c] in root:
                dfs(r, c, root)
    return sorted(found)
''',
    refs={
        "c": r"""// Trie of the words, then one DFS from every cell that walks the board and the
// trie in lockstep. Finished branches are pruned so later searches skip them.
typedef struct { int next[26]; int word; int kids; } WNode;   // word = index or -1

typedef struct {               // everything the recursive DFS needs, in one place
    WNode* t;
    char* g;                   // the board as a flat char grid, R*C
    int R, C;
    char** words;
    char** found;
    int nfound;
} Search;

// Returns true when `node` has become useless (no word, no children):
// the caller then unlinks it.
static bool dfs(Search* S, int r, int c, int node) {
    WNode* t = S->t;
    if (t[node].word >= 0) {                        // a word ends here: copy it out once
        const char* w = S->words[t[node].word];
        size_t len = strlen(w);
        char* copy = malloc(len + 1);
        memcpy(copy, w, len + 1);
        S->found[S->nfound++] = copy;
        t[node].word = -1;
    }
    char saved = S->g[r * S->C + c];
    S->g[r * S->C + c] = '#';                       // mark visited for this path
    static const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1};
    for (int k = 0; k < 4; k++) {
        int nr = r + dr[k], nc = c + dc[k];
        if (nr < 0 || nr >= S->R || nc < 0 || nc >= S->C) continue;
        char ch = S->g[nr * S->C + nc];
        if (ch == '#') continue;
        int child = t[node].next[ch - 'a'];
        if (child >= 0 && dfs(S, nr, nc, child)) {
            t[node].next[ch - 'a'] = -1;
            t[node].kids--;
        }
    }
    S->g[r * S->C + c] = saved;                     // backtrack
    return t[node].kids == 0 && t[node].word < 0;
}

static int cmp_str(const void* a, const void* b) {
    return strcmp(*(char* const*)a, *(char* const*)b);
}

static int new_node(WNode* t, int* used) {         // take the next arena slot
    WNode* x = &t[*used];
    for (int c = 0; c < 26; c++) x->next[c] = -1;
    x->word = -1;
    x->kids = 0;
    return (*used)++;
}

char** find_words(char*** board, int boardSize, int* boardColSize,
                  char** words, int wordsSize, int* returnSize) {
    // Arena sized for the worst case (every letter a new node), so no realloc.
    int cap = 1;
    for (int i = 0; i < wordsSize; i++) cap += (int)strlen(words[i]);
    WNode* t = malloc(sizeof(WNode) * (size_t)cap);
    int used = 0;
    new_node(t, &used);                             // root = 0
    for (int w = 0; w < wordsSize; w++) {
        int cur = 0;
        for (const char* p = words[w]; *p; p++) {
            int c = *p - 'a';
            if (t[cur].next[c] < 0) { t[cur].next[c] = new_node(t, &used); t[cur].kids++; }
            cur = t[cur].next[c];
        }
        t[cur].word = w;
    }

    int R = boardSize, C = boardColSize[0];
    char* g = malloc((size_t)(R * C));
    for (int i = 0; i < R; i++)
        for (int j = 0; j < C; j++) g[i * C + j] = board[i][j][0];   // "a" -> 'a'

    Search S = { t, g, R, C, words, malloc(sizeof(char*) * (size_t)(wordsSize + 1)), 0 };
    for (int i = 0; i < R; i++)
        for (int j = 0; j < C; j++) {
            int c = g[i * C + j] - 'a', child = t[0].next[c];
            if (child >= 0 && dfs(&S, i, j, child)) { t[0].next[c] = -1; t[0].kids--; }
        }
    free(t);
    free(g);
    qsort(S.found, (size_t)S.nfound, sizeof(char*), cmp_str);
    *returnSize = S.nfound;
    return S.found;
}""",
        "cpp": r"""struct WNode { int next[26]; int word = -1; int kids = 0;
                WNode() { for (int& x : next) x = -1; } };

vector<string> findWords(vector<vector<string>>& board, vector<string>& words) {
    vector<WNode> t(1);                        // trie arena, node 0 = root
    for (int w = 0; w < (int)words.size(); w++) {
        int cur = 0;
        for (char ch : words[w]) {
            int c = ch - 'a';
            if (t[cur].next[c] < 0) { t[cur].next[c] = t.size(); t[cur].kids++; t.emplace_back(); }
            cur = t[cur].next[c];
        }
        t[cur].word = w;
    }
    int R = board.size(), C = board[0].size();
    vector<string> g(R);                       // copy to a char grid for speed
    for (int i = 0; i < R; i++) for (int j = 0; j < C; j++) g[i] += board[i][j][0];
    vector<string> found;
    // returns true if the child node became empty and should be unlinked by the caller
    function<bool(int, int, int)> dfs = [&](int r, int c, int node) -> bool {
        if (t[node].word >= 0) { found.push_back(words[t[node].word]); t[node].word = -1; }
        char saved = g[r][c];
        g[r][c] = '#';
        const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1};
        for (int d = 0; d < 4; d++) {
            int nr = r + dr[d], nc = c + dc[d];
            if (nr < 0 || nr >= R || nc < 0 || nc >= C || g[nr][nc] == '#') continue;
            int ci = g[nr][nc] - 'a', child = t[node].next[ci];
            if (child >= 0 && dfs(nr, nc, child)) { t[node].next[ci] = -1; t[node].kids--; }
        }
        g[r][c] = saved;
        return t[node].kids == 0 && t[node].word < 0;   // exhausted: prune
    };
    for (int i = 0; i < R; i++)
        for (int j = 0; j < C; j++) {
            int ci = g[i][j] - 'a', child = t[0].next[ci];
            if (child >= 0 && dfs(i, j, child)) { t[0].next[ci] = -1; t[0].kids--; }
        }
    sort(found.begin(), found.end());
    return found;
}""",
        "rust": r"""struct Node {
    next: [i32; 26], // -1 = no child
    word: i32,       // index into `words`, or -1
    kids: u32,
}

fn dfs(r: usize, c: usize, node: usize, g: &mut Vec<Vec<u8>>, t: &mut Vec<Node>,
       words: &Vec<String>, found: &mut Vec<String>) -> bool {
    if t[node].word >= 0 {
        found.push(words[t[node].word as usize].clone());
        t[node].word = -1;
    }
    let saved = g[r][c];
    g[r][c] = b'#';
    let (rows, cols) = (g.len() as i64, g[0].len() as i64);
    for (dr, dc) in [(1i64, 0i64), (-1, 0), (0, 1), (0, -1)] {
        let (nr, nc) = (r as i64 + dr, c as i64 + dc);
        if nr < 0 || nr >= rows || nc < 0 || nc >= cols {
            continue;
        }
        let (nr, nc) = (nr as usize, nc as usize);
        if g[nr][nc] == b'#' {
            continue;
        }
        let ci = (g[nr][nc] - b'a') as usize;
        let child = t[node].next[ci];
        if child >= 0 && dfs(nr, nc, child as usize, g, t, words, found) {
            t[node].next[ci] = -1; // prune the exhausted branch
            t[node].kids -= 1;
        }
    }
    g[r][c] = saved;
    t[node].kids == 0 && t[node].word < 0
}

pub fn find_words(board: Vec<Vec<String>>, words: Vec<String>) -> Vec<String> {
    let mut t = vec![Node { next: [-1; 26], word: -1, kids: 0 }];
    for (wi, w) in words.iter().enumerate() {
        let mut cur = 0;
        for b in w.bytes() {
            let ci = (b - b'a') as usize;
            if t[cur].next[ci] < 0 {
                t.push(Node { next: [-1; 26], word: -1, kids: 0 });
                let id = (t.len() - 1) as i32;
                t[cur].next[ci] = id;
                t[cur].kids += 1;
            }
            cur = t[cur].next[ci] as usize;
        }
        t[cur].word = wi as i32;
    }
    let mut g: Vec<Vec<u8>> = board.iter().map(|row| row.iter().map(|s| s.as_bytes()[0]).collect()).collect();
    let mut found = Vec::new();
    for i in 0..g.len() {
        for j in 0..g[0].len() {
            let ci = (g[i][j] - b'a') as usize;
            let child = t[0].next[ci];
            if child >= 0 && dfs(i, j, child as usize, &mut g, &mut t, &words, &mut found) {
                t[0].next[ci] = -1;
                t[0].kids -= 1;
            }
        }
    }
    found.sort();
    found
}""",
    },
    tests=_ws_tests(),
)


# ======================================================================== Segment tree
def _seg_tests():
    def gen(seed, n, q, lo, hi):
        r = _rng(seed)
        nums = [r.randint(lo, hi) for _ in range(n)]
        ops, args = [], []
        for _ in range(q):
            if r.random() < 0.5:
                ops.append("update")
                args.append([r.randrange(n), r.randint(lo, hi)])
            else:
                a, b = sorted((r.randrange(n), r.randrange(n)))
                ops.append("sum")
                args.append([a, b])
        return [nums, ops, args]

    return [
        [[1, 3, 5], ["sum", "update", "sum"], [[0, 2], [1, 2], [0, 2]]],
        [[7], ["sum", "update", "sum", "sum"], [[0, 0], [0, -4], [0, 0], [0, 0]]],
        [[-1, -2, -3, -4, -5], ["sum", "sum", "sum", "update", "sum"], [[0, 4], [1, 3], [4, 4], [2, 100], [0, 4]]],
        [[0, 0, 0, 0, 0, 0, 0], ["update", "update", "sum", "sum", "sum"], [[0, 5], [6, 9], [0, 6], [1, 5], [6, 6]]],
        gen(1621, 10, 30, -10, 10),
        gen(1622, 100, 300, -1000, 1000),
        gen(1623, 600, 800, -10**9, 10**9),
    ]


P_SEGTREE = dict(
    id="segment-tree-range-sum",
    title="Range Sum with Point Updates (Segment Tree)",
    difficulty=3,
    tags=["segment tree", "design", "range query"],
    fn="range_sum_queries",
    params=[["nums", "int[]"], ["ops", "str[]"], ["args", "int[][]"]],
    returns="int[]",
    statement=r"""
Maintain an integer array under two operations, applied in order:

* `"update"` with `args[i] = [index, value]`: set `nums[index] = value`.
* `"sum"` with `args[i] = [left, right]`: report `nums[left] + … + nums[right]` (inclusive).

Return the results of the `"sum"` operations, in order.

Both operations should run in **O(log n)**. Prefix sums make queries O(1) but updates O(n);
a plain array is the other way round. A segment tree (or Fenwick tree) balances both.
""",
    constraints=["1 ≤ len(nums) ≤ 600", "1 ≤ len(ops) ≤ 800", "0 ≤ left ≤ right < len(nums)",
                 "-10⁹ ≤ nums[i], value ≤ 10⁹ (sums fit in 64 bits)"],
    example_notes=["`1+3+5 = 9`; after `nums[1] = 2` the sum is `1+2+5 = 8`.",
                   "A one-element array: update replaces the value."],
    hints=[
        "Precompute sums of blocks so that any range is a union of O(log n) precomputed blocks, and any single index lies in O(log n) blocks.",
        "A binary tree where each node stores the sum of its range: the root covers everything, children split the range in half. Updating a leaf only changes its ancestors.",
        "Array layout: leaves at `n … 2n−1`, `tree[i] = tree[2i] + tree[2i+1]`. Query with two pointers `l = left + n`, `r = right + n + 1` climbing towards the root.",
    ],
    explanation=r"""
## Intuition

Look at the two naive options:

| structure | update | range sum |
|---|---|---|
| plain array | O(1) | O(n) |
| prefix sums | O(n) | O(1) |

A segment tree stores sums of *dyadic* blocks (halves, quarters, eighths…). Any range
`[l, r]` is a disjoint union of at most ~2 log n such blocks, and any index belongs to
exactly one block per level, log n in total. Both operations become O(log n).

## Approach

**Recursive view** (easiest to reason about):

```text
build(node, lo, hi):   if lo == hi: tree[node] = nums[lo]
                       else build children on halves; tree[node] = left + right
query(node, lo, hi, l, r):
    if r < lo or hi < l: return 0            # disjoint
    if l <= lo and hi <= r: return tree[node] # fully covered: use the block
    return query(left half) + query(right half)
update(node, lo, hi, i, v): descend to the leaf, set it, recompute sums on the way up
```

**Iterative bottom-up** (the Python reference): put leaves at `tree[n + i]`, internal
node `i` has children `2i` and `2i+1`.

* Update: set the leaf, then `i //= 2` and recompute until the root.
* Query on the half-open `[l, r)`, with `l += n`, `r += n`: while `l < r`, if `l` is a right
  child (odd) it is a block that belongs to the answer but its parent doesn't fit: take it
  and step `l += 1`. Symmetrically, if `r` is odd, take `tree[r − 1]`. Then move both up a level.

Trace for `nums = [1, 3, 5]` (n = 3; this layout works for any n, not just powers of two):

```text
index: 1   2   3   4   5
tree:  9   8   1   3   5        tree[3] = leaf 0 (=1), tree[4] = 3, tree[5] = 5
                               tree[2] = tree[4] + tree[5] = 8, tree[1] = tree[2] + tree[3] = 9
sum(0,2): l=3, r=6
  l odd → take tree[3]=1, l=4;  r even
  l=2, r=3 → l even; r odd → take tree[2]=8, r=2
  l=1, r=1 → stop.   total 9
```

## Complexity

* **Build:** O(n). **Update / query:** O(log n). Total O(n + q log n).
* **Space:** 2n integers (iterative) or up to 4n (recursive with `node, 2node, 2node+1` numbering).

## Common mistakes

* Inclusive vs half-open ranges: the query here is inclusive, so pass `right + 1`.
* Updating with `+= value` instead of setting (`=`); a Fenwick tree needs `+= value − old`.
* Recursive trees sized `2n` instead of `4n` overflow when n isn't a power of two.
* 32-bit overflow: sums of 600 values up to 10⁹ need 64-bit integers.

## Going further

* Swap `+` for `min`, `max`, `gcd` or any associative operation (a *monoid*).
* **Lazy propagation** adds range updates ("add 5 to `[l, r]`") in O(log n).
* A **Fenwick tree** does point-update/prefix-sum in less code; see the next problem.
""",
    solution=r'''def range_sum_queries(nums, ops, args):
    n = len(nums)
    # Iterative segment tree: leaves live at tree[n .. 2n-1]; internal node i
    # has children 2i and 2i+1, so its parent is i // 2. tree[0] is unused.
    tree = [0] * (2 * n)
    tree[n:] = nums
    for i in range(n - 1, 0, -1):          # build parents after their children
        tree[i] = tree[2 * i] + tree[2 * i + 1]

    out = []
    for op, (a, b) in zip(ops, args):
        if op == "update":
            i = a + n
            tree[i] = b                    # set the leaf...
            i //= 2
            while i >= 1:                  # ...then fix every ancestor's sum
                tree[i] = tree[2 * i] + tree[2 * i + 1]
                i //= 2
        else:
            # Half-open [l, r) over leaf positions.
            l, r = a + n, b + n + 1
            total = 0
            while l < r:
                if l & 1:                  # l is a right child: its parent would
                    total += tree[l]       # stick out to the left, so take l alone
                    l += 1
                if r & 1:                  # r - 1 is a left child: take it alone
                    r -= 1
                    total += tree[r]
                l //= 2                    # climb one level
                r //= 2
            out.append(total)
    return out
''',
    refs={
        "c": r"""// Iterative (bottom-up) segment tree: leaves live at t[n .. 2n-1] and the
// parent of node i is i/2, so t[i] = t[2i] + t[2i+1]. No recursion, 2n longs.
long long* range_sum_queries(long long* nums, int numsSize, char** ops, int opsSize,
                             long long** args, int argsSize, int* argsColSize, int* returnSize) {
    (void)argsSize; (void)argsColSize;
    int n = numsSize;
    long long* t = malloc(sizeof(long long) * 2 * (size_t)n);
    for (int i = 0; i < n; i++) t[n + i] = nums[i];
    for (int i = n - 1; i >= 1; i--) t[i] = t[2 * i] + t[2 * i + 1];   // build: O(n)

    long long* out = malloc(sizeof(long long) * (size_t)(opsSize > 0 ? opsSize : 1));
    int k = 0;
    for (int q = 0; q < opsSize; q++) {
        if (strcmp(ops[q], "update") == 0) {
            // Overwrite the leaf, then refresh every ancestor on the way to the root.
            int i = (int)args[q][0] + n;
            t[i] = args[q][1];
            for (i /= 2; i >= 1; i /= 2) t[i] = t[2 * i] + t[2 * i + 1];
        } else {
            // Half-open [l, r). Climb both borders: a border node that is a right
            // child (l odd) or whose left neighbour is wanted (r odd) is fully
            // inside the range, so take it and step inward. O(log n).
            long long s = 0;
            int l = (int)args[q][0] + n, r = (int)args[q][1] + n + 1;
            for (; l < r; l /= 2, r /= 2) {
                if (l & 1) s += t[l++];
                if (r & 1) s += t[--r];
            }
            out[k++] = s;
        }
    }
    free(t);
    *returnSize = k;
    return out;
}""",
        "cpp": r"""// Classic recursive segment tree (4n nodes), node 1 covers [0, n-1].
struct SegTree {
    int n; vector<long long> t;
    SegTree(const vector<long long>& a) : n(a.size()), t(4 * a.size()) { build(a, 1, 0, n - 1); }
    void build(const vector<long long>& a, int node, int lo, int hi) {
        if (lo == hi) { t[node] = a[lo]; return; }
        int mid = (lo + hi) / 2;
        build(a, 2 * node, lo, mid);
        build(a, 2 * node + 1, mid + 1, hi);
        t[node] = t[2 * node] + t[2 * node + 1];
    }
    void update(int node, int lo, int hi, int i, long long v) {
        if (lo == hi) { t[node] = v; return; }
        int mid = (lo + hi) / 2;
        if (i <= mid) update(2 * node, lo, mid, i, v);
        else update(2 * node + 1, mid + 1, hi, i, v);
        t[node] = t[2 * node] + t[2 * node + 1];
    }
    long long query(int node, int lo, int hi, int l, int r) const {
        if (r < lo || hi < l) return 0;              // disjoint
        if (l <= lo && hi <= r) return t[node];      // fully covered
        int mid = (lo + hi) / 2;
        return query(2 * node, lo, mid, l, r) + query(2 * node + 1, mid + 1, hi, l, r);
    }
};

vector<long long> rangeSumQueries(vector<long long>& nums, vector<string>& ops, vector<vector<long long>>& args) {
    SegTree st(nums);
    int n = nums.size();
    vector<long long> out;
    for (size_t i = 0; i < ops.size(); i++) {
        if (ops[i] == "update") st.update(1, 0, n - 1, args[i][0], args[i][1]);
        else out.push_back(st.query(1, 0, n - 1, args[i][0], args[i][1]));
    }
    return out;
}""",
        "rust": r"""pub fn range_sum_queries(nums: Vec<i64>, ops: Vec<String>, args: Vec<Vec<i64>>) -> Vec<i64> {
    let n = nums.len();
    let mut tree = vec![0i64; 2 * n];
    tree[n..].copy_from_slice(&nums);
    for i in (1..n).rev() {
        tree[i] = tree[2 * i] + tree[2 * i + 1];
    }
    let mut out = Vec::new();
    for (op, a) in ops.iter().zip(args.iter()) {
        if op == "update" {
            let mut i = a[0] as usize + n;
            tree[i] = a[1];
            while i > 1 {
                i /= 2;
                tree[i] = tree[2 * i] + tree[2 * i + 1];
            }
        } else {
            let (mut l, mut r) = (a[0] as usize + n, a[1] as usize + n + 1);
            let mut total = 0;
            while l < r {
                if l & 1 == 1 {
                    total += tree[l];
                    l += 1;
                }
                if r & 1 == 1 {
                    r -= 1;
                    total += tree[r];
                }
                l /= 2;
                r /= 2;
            }
            out.push(total);
        }
    }
    out
}""",
    },
    tests=_seg_tests(),
)


# ======================================================================== Fenwick: count smaller
def _cs_tests():
    r = _rng(1631)
    return [
        [[5, 2, 6, 1]],
        [[-1]],
        [[-1, -1]],
        [[1, 2, 3, 4, 5]],
        [[5, 4, 3, 2, 1]],
        [[2, 0, 1, 0, 2, 1]],
        [[r.randint(-10, 10) for _ in range(40)]],
        [[r.randint(-10**4, 10**4) for _ in range(4000)]],
    ]


P_FENWICK = dict(
    id="fenwick-count-smaller-after-self",
    title="Count of Smaller Numbers After Self",
    difficulty=3,
    tags=["fenwick tree", "binary indexed tree", "coordinate compression"],
    fn="count_smaller",
    params=[["nums", "int[]"]],
    returns="int[]",
    statement=r"""
For each index `i`, count how many elements **to its right** are **strictly smaller**
than `nums[i]`. Return those counts as an array.

The naive double loop is O(n²); aim for O(n log n).
""",
    constraints=["1 ≤ len(nums) ≤ 4000", "-10⁴ ≤ nums[i] ≤ 10⁴"],
    example_notes=["Right of `5` are `2, 6, 1`: two are smaller. Right of `2`: only `1`. Right of `6`: `1`. Nothing is right of `1`.",
                   "Equal values do not count."],
    hints=[
        "Scan from right to left. Then 'elements to my right' are exactly the elements you have already seen.",
        "You need a structure over values that supports 'add value v' and 'how many added values are < v?'. That's a point update and a prefix sum.",
        "Compress values to ranks 1..m, then use a Fenwick tree: `add(rank, 1)` and `prefix(rank − 1)`.",
    ],
    explanation=r"""
## Intuition

Process the array right to left. At index `i`, everything already processed is exactly
"to the right of `i`". So we need a multiset of seen values that answers *how many are
smaller than `x`?* and supports *insert `x`*. Over a value domain, that is a frequency
array with **prefix sums**, and a **Fenwick tree** gives both operations in O(log m).

## Approach

1. **Coordinate compression**: map each distinct value to its rank `1..m` in sorted order
   (Fenwick trees are 1-indexed and want a compact domain).
2. For `i` from `n−1` down to 0, with `r = rank(nums[i])`:
   * `ans[i] = prefix(r − 1)` (seen values with smaller rank, i.e. strictly smaller).
   * `add(r, 1)`.

The Fenwick tree in five lines:

```python
def add(i, delta):          # point update
    while i <= m:
        bit[i] += delta
        i += i & -i         # next block that also covers i
def prefix(i):              # sum of counts for ranks 1..i
    s = 0
    while i > 0:
        s += bit[i]
        i -= i & -i         # jump to the block just before this one
    return s
```

`i & -i` is the lowest set bit of `i` (see the bits track), and `bit[i]` stores the sum of
the last `i & -i` positions ending at `i`. Climbing removes one set bit per step, so both
loops run O(log m) times.

Trace for `[5, 2, 6, 1]` (ranks: 1→1, 2→2, 5→3, 6→4):

| i | value | rank | prefix(rank−1) | counts after add |
|---|---|---|---|---|
| 3 | 1 | 1 | 0 | {1} |
| 2 | 6 | 4 | 1 | {1, 6} |
| 1 | 2 | 2 | 1 | {1, 2, 6} |
| 0 | 5 | 3 | 2 | {1, 2, 5, 6} |

Answer `[2, 1, 1, 0]`.

## Complexity

* **Time:** O(n log n): sorting for compression plus n Fenwick operations of O(log n).
* **Space:** O(n).

## Common mistakes

* Counting `≤` instead of `<`: query `prefix(rank − 1)`, not `prefix(rank)`.
* Querying *after* adding the current element (it would count itself when using `≤`).
* 0-based Fenwick indexing: `i & -i` is 0 for `i = 0`, so `add(0, …)` loops forever.
* Skipping compression with negative values (negative indices).

## Going further

* **Merge sort** solves it too: while merging, every element from the right half that is
  placed before an element of the left half is "smaller and to its right". Same O(n log n).
* Counting **inversions** is the sum of this array.
* A Fenwick tree over a 2-D grid answers rectangle sums with point updates in O(log² n).
""",
    solution=r'''def count_smaller(nums):
    # Coordinate compression: Fenwick trees index a dense domain 1..m.
    rank = {v: i + 1 for i, v in enumerate(sorted(set(nums)))}
    m = len(rank)
    bit = [0] * (m + 1)              # bit[i] = count of values whose rank lies in
                                     # the block (i - (i & -i), i]

    def add(i):
        while i <= m:
            bit[i] += 1
            i += i & -i              # move to the next block that contains i

    def prefix(i):
        s = 0
        while i > 0:
            s += bit[i]
            i -= i & -i              # strip the lowest set bit: previous disjoint block
        return s

    out = [0] * len(nums)
    # Right to left: everything already added is to the right of index i.
    for i in range(len(nums) - 1, -1, -1):
        r = rank[nums[i]]
        out[i] = prefix(r - 1)       # strictly smaller => ranks 1 .. r-1
        add(r)                       # now nums[i] is "to the right" of later indices
    return out
''',
    refs={
        "c": r"""static int cmp_ll(const void* a, const void* b) {
    long long x = *(const long long*)a, y = *(const long long*)b;
    return (x > y) - (x < y);              // never "return x - y": it can overflow
}

long long* count_smaller(long long* nums, int numsSize, int* returnSize) {
    int n = numsSize;
    // 1. Coordinate compression: sort a copy, drop duplicates. Value v then has
    //    rank (its index in `vals`) + 1, in 1..m: Fenwick trees are 1-indexed.
    long long* vals = malloc(sizeof(long long) * (size_t)n);
    memcpy(vals, nums, sizeof(long long) * (size_t)n);
    qsort(vals, (size_t)n, sizeof(long long), cmp_ll);
    int m = 0;
    for (int i = 0; i < n; i++)
        if (m == 0 || vals[m - 1] != vals[i]) vals[m++] = vals[i];

    // 2. bit[] counts how many values of each rank we've seen so far.
    int* bit = calloc((size_t)m + 1, sizeof(int));
    long long* out = malloc(sizeof(long long) * (size_t)n);

    // 3. Walk right to left: everything already in the tree is to our right.
    for (int i = n - 1; i >= 0; i--) {
        int lo = 0, hi = m;                   // binary search for the rank
        while (lo < hi) {
            int mid = (lo + hi) / 2;
            if (vals[mid] < nums[i]) lo = mid + 1; else hi = mid;
        }
        int r = lo + 1;
        int s = 0;                            // prefix(r - 1): strictly smaller ranks
        for (int j = r - 1; j > 0; j -= j & -j) s += bit[j];
        out[i] = s;
        for (int j = r; j <= m; j += j & -j) bit[j]++;   // add this value
    }
    free(vals);
    free(bit);
    *returnSize = n;
    return out;
}""",
        "cpp": r"""vector<long long> countSmaller(vector<long long>& nums) {
    // Compress values to ranks 1..m.
    vector<long long> vals(nums);
    sort(vals.begin(), vals.end());
    vals.erase(unique(vals.begin(), vals.end()), vals.end());
    int m = vals.size();
    vector<int> bit(m + 1, 0);
    auto add = [&](int i) { for (; i <= m; i += i & -i) bit[i]++; };
    auto prefix = [&](int i) { int s = 0; for (; i > 0; i -= i & -i) s += bit[i]; return s; };
    vector<long long> out(nums.size());
    for (int i = (int)nums.size() - 1; i >= 0; i--) {
        int r = lower_bound(vals.begin(), vals.end(), nums[i]) - vals.begin() + 1;
        out[i] = prefix(r - 1);
        add(r);
    }
    return out;
}""",
        "rust": r"""pub fn count_smaller(nums: Vec<i64>) -> Vec<i64> {
    let mut vals = nums.clone();
    vals.sort_unstable();
    vals.dedup();
    let m = vals.len();
    let mut bit = vec![0i64; m + 1];
    let mut out = vec![0i64; nums.len()];
    for i in (0..nums.len()).rev() {
        // binary_search on the deduplicated values gives the 0-based rank
        let r = vals.binary_search(&nums[i]).unwrap() + 1;
        let (mut j, mut s) = (r - 1, 0);
        while j > 0 {
            s += bit[j];
            j &= j - 1; // same as j -= j & -j for unsigned: clear lowest set bit
        }
        out[i] = s;
        let mut j = r;
        while j <= m {
            bit[j] += 1;
            j += j & j.wrapping_neg(); // lowest set bit of a usize
        }
    }
    out
}""",
    },
    tests=_cs_tests(),
)


# ======================================================================== KMP
def _kmp_tests():
    r = _rng(1641)
    t = "".join(r.choice("ab") for _ in range(3000))
    return [
        ["abababcab", "ab"],
        ["aaaa", "aa"],
        ["hello", "world"],
        ["", "a"],
        ["a", "a"],
        ["abc", "abcd"],
        ["aabaacaadaabaaba", "aaba"],
        [t, "abaab"],
        ["a" * 3000, "a" * 1500],
        ["a" * 20000 + "b", "a" * 300 + "b"],
    ]


P_KMP = dict(
    id="kmp-find-all-occurrences",
    title="All Occurrences (KMP)",
    difficulty=3,
    tags=["string", "kmp", "string matching"],
    fn="find_all_occurrences",
    params=[["text", "str"], ["pattern", "str"]],
    returns="int[]",
    statement=r"""
Return the starting indices of **every** occurrence of `pattern` in `text`, in increasing
order. Occurrences may overlap (`"aa"` occurs in `"aaaa"` at 0, 1 and 2).

Aim for O(len(text) + len(pattern)) time, which rules out comparing the pattern at every
position from scratch.
""",
    constraints=["0 ≤ len(text) ≤ 2·10⁴", "1 ≤ len(pattern) ≤ 2·10⁴", "lowercase ASCII letters"],
    example_notes=["`ab` starts at 0, 2 and 7.", "Overlapping matches all count."],
    hints=[
        "After a mismatch, the naive algorithm throws away everything it learned about the text. What does the matched part tell you about where the next possible match could start?",
        "If you matched `k` characters and then fail, the next candidate alignment keeps the longest proper prefix of `pattern[:k]` that is also its suffix.",
        "Precompute `fail[i]` = length of the longest proper prefix of `pattern[:i+1]` that is also a suffix of it. While scanning, on mismatch set `k = fail[k−1]`; after a full match record it and also set `k = fail[k−1]`.",
    ],
    explanation=r"""
## Intuition

Naive matching restarts at the next text position after a mismatch, re-reading characters
it has already seen: O(n·m) on inputs like `aaaa…ab` vs `aaab`. KMP never moves backwards in
the text. When `k` pattern characters matched and the next one fails, the text's last `k`
characters *are* `pattern[:k]`. The best fallback is the longest proper **border** of
`pattern[:k]` (a prefix that is also a suffix): we can keep that many characters matched
and continue.

```text
pattern = a a b a a b a a a
fail    = 0 1 0 1 2 3 4 5 2
```

`fail[5] = 3`: `aabaab` ends with `aab`, which is also how it starts.

## Approach

**Failure table** (the pattern matched against itself):

```text
k = 0
for i in 1..m-1:
    while k > 0 and p[i] != p[k]: k = fail[k-1]
    if p[i] == p[k]: k += 1
    fail[i] = k
```

**Scan**: same loop over the text; when `k == m`, record `i − m + 1`, then `k = fail[m−1]`
so overlapping matches are found.

Trace: text `abababcab`, pattern `ab` (`fail = [0, 0]`):

| i | ch | k before | action | k after | match? |
|---|---|---|---|---|---|
| 0 | a | 0 | p[0]=a ✔ | 1 | |
| 1 | b | 1 | p[1]=b ✔ | 2 | at 0, k=fail[1]=0 |
| 2 | a | 0 | ✔ | 1 | |
| 3 | b | 1 | ✔ | 2 | at 2 |
| 4 | a | 0 | ✔ | 1 | |
| 5 | b | 1 | ✔ | 2 | at 4 |
| 6 | c | 0 | ✘ | 0 | |
| 7 | a | 0 | ✔ | 1 | |
| 8 | b | 1 | ✔ | 2 | at 7 |

## Complexity

* **Time:** O(n + m). Amortized argument: `k` rises by at most 1 per character, each
  fallback lowers it by at least 1, and it never goes below 0, so total fallbacks ≤ total rises ≤ n.
* **Space:** O(m) for the failure table.

## Common mistakes

* Setting `k = 0` after a full match: misses overlapping occurrences (`aa` in `aaaa`).
* Using `if` instead of `while` for the fallback: one fallback may not be enough.
* Off-by-one in `fail[k − 1]` vs `fail[k]` (the table is indexed by the *last* matched position).
* Pattern longer than text: return `[]` (the scan simply never reaches `k = m`).

## Going further

* **Z-function**: `z[i]` = longest common prefix of `s` and `s[i:]`. Matching = Z on
  `pattern + "#" + text`. Equivalent power, often easier to remember.
* **Aho–Corasick** generalises KMP's failure links to a trie of many patterns.
* The failure table alone answers "shortest period of a string": `m − fail[m−1]`.
""",
    solution=r'''def find_all_occurrences(text, pattern):
    m = len(pattern)
    # fail[i] = length of the longest proper prefix of pattern[:i+1]
    #           that is also a suffix of it (its longest "border").
    fail = [0] * m
    k = 0
    for i in range(1, m):
        while k > 0 and pattern[i] != pattern[k]:
            k = fail[k - 1]          # fall back to the next-shorter border
        if pattern[i] == pattern[k]:
            k += 1
        fail[i] = k

    out = []
    k = 0                            # how many pattern chars are currently matched
    for i, ch in enumerate(text):
        while k > 0 and ch != pattern[k]:
            k = fail[k - 1]          # keep the longest still-valid partial match
        if ch == pattern[k]:
            k += 1
        if k == m:                   # full match ending at i
            out.append(i - m + 1)
            k = fail[k - 1]          # continue: overlapping matches are allowed
    return out
''',
    refs={
        "c": r"""long long* find_all_occurrences(char* text, char* pattern, int* returnSize) {
    int n = (int)strlen(text), m = (int)strlen(pattern);
    // fail[i] = length of the longest proper prefix of pattern[0..i] that is
    // also a suffix of it: where to resume after a mismatch.
    int* fail = malloc(sizeof(int) * (size_t)m);
    fail[0] = 0;
    for (int i = 1, k = 0; i < m; i++) {
        while (k > 0 && pattern[i] != pattern[k]) k = fail[k - 1];
        if (pattern[i] == pattern[k]) k++;
        fail[i] = k;
    }
    // At most n - m + 1 matches; +1 keeps malloc(0) out of the picture.
    long long* out = malloc(sizeof(long long) * (size_t)(n + 1));
    int cnt = 0;
    // k = how many pattern characters currently match. It never moves backwards
    // in the text, so the scan is O(n + m) in total.
    for (int i = 0, k = 0; i < n; i++) {
        while (k > 0 && text[i] != pattern[k]) k = fail[k - 1];
        if (text[i] == pattern[k]) k++;
        if (k == m) {
            out[cnt++] = i - m + 1;
            k = fail[k - 1];          // keep the overlap: allows "aa" in "aaaa" 3 times
        }
    }
    free(fail);
    *returnSize = cnt;
    return out;
}""",
        "cpp": r"""vector<long long> findAllOccurrences(string text, string pattern) {
    int m = pattern.size(), n = text.size();
    vector<int> fail(m, 0);
    for (int i = 1, k = 0; i < m; i++) {
        while (k > 0 && pattern[i] != pattern[k]) k = fail[k - 1];
        if (pattern[i] == pattern[k]) k++;
        fail[i] = k;
    }
    vector<long long> out;
    for (int i = 0, k = 0; i < n; i++) {
        while (k > 0 && text[i] != pattern[k]) k = fail[k - 1];
        if (text[i] == pattern[k]) k++;
        if (k == m) { out.push_back(i - m + 1); k = fail[k - 1]; }
    }
    return out;
}""",
        "rust": r"""pub fn find_all_occurrences(text: String, pattern: String) -> Vec<i64> {
    // Work on bytes: O(1) indexing, and the input is ASCII.
    let (t, p) = (text.as_bytes(), pattern.as_bytes());
    let m = p.len();
    let mut fail = vec![0usize; m];
    let mut k = 0;
    for i in 1..m {
        while k > 0 && p[i] != p[k] {
            k = fail[k - 1];
        }
        if p[i] == p[k] {
            k += 1;
        }
        fail[i] = k;
    }
    let mut out = Vec::new();
    k = 0;
    for (i, &ch) in t.iter().enumerate() {
        while k > 0 && ch != p[k] {
            k = fail[k - 1];
        }
        if ch == p[k] {
            k += 1;
        }
        if k == m {
            out.push((i + 1 - m) as i64);
            k = fail[k - 1];
        }
    }
    out
}""",
    },
    tests=_kmp_tests(),
)


# ======================================================================== Rabin-Karp DNA
def _dna_tests():
    r = _rng(1651)
    big = "".join(r.choice("ACGT") for _ in range(10000))
    low = "".join(r.choice("AC") for _ in range(400))
    return [
        ["AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT"],
        ["AAAAAAAAAAAAA"],
        ["AAAAAAAAAA"],
        ["ACGT"],
        ["AAAAAAAAAAA"],
        ["ACGTACGTACGTACGTACGT"],
        [low],
        [big],
    ]


P_DNA = dict(
    id="rabin-karp-repeated-dna",
    title="Repeated DNA Sequences (Rolling Hash)",
    difficulty=3,
    tags=["rolling hash", "rabin-karp", "string", "hash set"],
    fn="find_repeated_dna",
    params=[["s", "str"]],
    returns="str[]",
    statement=r"""
A DNA string consists of the letters `A`, `C`, `G`, `T`. Return every **10-letter**
substring that occurs **more than once** in `s` (occurrences may overlap). Each such
sequence is reported once, and the result is **sorted** lexicographically.

Hashing every 10-letter slice as a string costs O(10) per position; do it with a
**rolling hash** in O(1) per position.
""",
    constraints=["1 ≤ len(s) ≤ 10⁴", "`s[i]` ∈ {A, C, G, T}"],
    example_notes=["`AAAAACCCCC` and `CCCCCAAAAA` each occur twice.",
                   "13 `A`s contain the 10-letter window `AAAAAAAAAA` four times (overlapping)."],
    hints=[
        "Slide a window of length 10 and remember which windows you have already seen. The question is how to represent a window cheaply.",
        "With 4 letters, each letter is a base-4 digit (2 bits). A 10-letter window is a 20-bit number.",
        "Roll it: `h = (h * 4 + code(new_char)) mod 4¹⁰`. The `mod 4¹⁰` drops the digit that left the window. Track hashes seen once and those seen twice or more.",
    ],
    explanation=r"""
## Intuition

Rabin–Karp's idea: treat a string as a number in some base, so that sliding the window by
one is O(1) arithmetic instead of rebuilding a substring:

```text
hash("c₀c₁…c₉") = c₀·B⁹ + c₁·B⁸ + … + c₉
slide right:  h' = (h − c₀·B⁹)·B + c₁₀
```

Usually `B` is a large-ish base and the hash is reduced modulo a big prime, so different
strings can collide and a match must be verified. Here the alphabet has only 4 letters, so
base `B = 4` with digits `A=0, C=1, G=2, T=3` gives a **perfect** hash: a 10-letter window
is exactly a 20-bit number, different windows give different numbers, no verification needed.

## Approach

1. `h = 0`. For each position `i`:
   * `h = (h · 4 + code(s[i])) mod 4¹⁰`. Multiplying by 4 shifts every digit up; the
     modulus discards the digit that left the window. (In bit terms: `((h << 2) | code) & 0xFFFFF`.)
   * Once `i ≥ 9`, `h` encodes `s[i−9 .. i]`. If `h` was seen before, add that substring to
     the answer set; otherwise mark it seen.
2. Sort the answers.

Trace on `AAAAAAAAAAA` (11 A's): the hash is 0 at `i = 9` (first window, new) and 0 again
at `i = 10` (repeat!) → `["AAAAAAAAAA"]`.

## Complexity

* **Time:** O(n) rolling plus O(k log k · 10) to sort `k` answers.
* **Space:** O(n) for the set of seen hashes (at most n integers, or a 4¹⁰ = 1M bitset).

Compare with storing 10-character strings in a hash set: O(10·n) time to slice and hash,
and 10× more memory. With window length L in general, rolling saves a factor L.

## Common mistakes

* Reporting a sequence once per extra occurrence (use a set for the answers, or a count that triggers only when it hits exactly 2).
* Starting to check before the first full window (`i < 9`).
* With a modular polynomial hash (general alphabets), forgetting that collisions exist:
  compare the actual substrings when hashes match, or use two moduli.
* In C/C++/Rust: negative intermediate values when subtracting the outgoing digit in the
  `(h − c₀·B⁹)` form; add the modulus before taking `%`.

## Going further

* **Longest duplicate substring**: binary search the length L, and for each L use a
  Rabin–Karp rolling hash to test whether any length-L substring repeats: O(n log n).
* **Polynomial hashing** of all prefixes lets you compare any two substrings in O(1),
  a workhorse for string problems (palindromes, suffix comparisons).
""",
    solution=r'''def find_repeated_dna(s):
    L = 10
    code = {"A": 0, "C": 1, "G": 2, "T": 3}   # each letter is one base-4 digit
    WINDOW = 4 ** L                  # 4^10 = 2^20: hashes are exact 20-bit numbers
    h = 0
    seen = set()                     # hashes of windows seen at least once
    repeated = set()                 # substrings seen at least twice
    for i, ch in enumerate(s):
        # Shift the base-4 number left by one digit and append the new letter;
        # "mod 4^10" removes the digit of the letter that just left the window.
        h = (h * 4 + code[ch]) % WINDOW
        if i >= L - 1:               # h now encodes exactly s[i-9 .. i]
            if h in seen:
                repeated.add(s[i - L + 1:i + 1])   # a set: report each sequence once
            else:
                seen.add(h)
    return sorted(repeated)
''',
    refs={
        "c": r"""static int cmp_str(const void* a, const void* b) {
    return strcmp(*(char* const*)a, *(char* const*)b);
}

char** find_repeated_dna(char* s, int* returnSize) {
    enum { L = 10, MASK = (1 << 20) - 1 };   // 10 letters x 2 bits = 20-bit key
    int n = (int)strlen(s);
    // Direct-address table indexed by the 20-bit code: 1 MiB of byte counters.
    // The "hash" is exact (a perfect encoding), so there are no collisions to check.
    unsigned char* seen = calloc(1u << 20, 1);
    char** out = malloc(sizeof(char*) * (size_t)(n + 1));
    int cnt = 0;
    unsigned h = 0;
    for (int i = 0; i < n; i++) {
        unsigned code = s[i] == 'A' ? 0 : s[i] == 'C' ? 1 : s[i] == 'G' ? 2 : 3;
        h = ((h << 2) | code) & MASK;          // roll: shift in 2 bits, drop the top 2
        if (i < L - 1) continue;               // window not full yet
        if (seen[h] < 2 && ++seen[h] == 2) {   // report exactly on the second sighting
            char* w = malloc(L + 1);
            memcpy(w, s + i - L + 1, L);
            w[L] = '\0';
            out[cnt++] = w;
        }
    }
    free(seen);
    qsort(out, (size_t)cnt, sizeof(char*), cmp_str);
    *returnSize = cnt;
    return out;
}""",
        "cpp": r"""vector<string> findRepeatedDna(string s) {
    const int L = 10, MASK = (1 << 20) - 1;   // 10 letters x 2 bits
    auto code = [](char c) { return c == 'A' ? 0 : c == 'C' ? 1 : c == 'G' ? 2 : 3; };
    vector<unsigned char> count(1 << 20, 0);   // direct-address table: 1 MB, no hashing at all
    vector<string> out;
    int h = 0;
    for (int i = 0; i < (int)s.size(); i++) {
        h = ((h << 2) | code(s[i])) & MASK;    // roll: shift in 2 bits, drop the top 2
        if (i >= L - 1 && ++count[h] == 2)     // exactly on the second sighting
            out.push_back(s.substr(i - L + 1, L));
        if (count[h] > 2) count[h] = 2;        // saturate so the byte never wraps
    }
    sort(out.begin(), out.end());
    return out;
}""",
        "rust": r"""use std::collections::HashMap;

pub fn find_repeated_dna(s: String) -> Vec<String> {
    const L: usize = 10;
    let b = s.as_bytes();
    let mut counts: HashMap<u32, u8> = HashMap::new();
    let mut out = Vec::new();
    let mut h: u32 = 0;
    for (i, &c) in b.iter().enumerate() {
        let code = match c { b'A' => 0, b'C' => 1, b'G' => 2, _ => 3 };
        h = ((h << 2) | code) & 0xF_FFFF; // keep the low 20 bits = last 10 letters
        if i + 1 >= L {
            let e = counts.entry(h).or_insert(0);
            *e = (*e).saturating_add(1);
            if *e == 2 {
                out.push(s[i + 1 - L..=i].to_string());
            }
        }
    }
    out.sort();
    out
}""",
    },
    tests=_dna_tests(),
)


# ======================================================================== LIS reconstruct
def _lis_tests():
    r = _rng(1661)
    return [
        [[10, 9, 2, 5, 3, 7, 101, 18]],
        [[0, 1, 0, 3, 2, 3]],
        [[7, 7, 7, 7]],
        [[5]],
        [[3, 4, 1, 2, 9, 5]],
        [[1, 5, 2, 6, 3, 7]],
        [[5, 4, 3, 2, 1]],
        [[2, 2, 1, 3, 3, 0, 4]],
        [[r.randint(0, 6) for _ in range(30)]],
        [[r.randint(-50, 50) for _ in range(200)]],
        [[r.randint(-10**9, 10**9) for _ in range(3000)]],
    ]


P_LIS = dict(
    id="lis-reconstruct-lexicographic",
    title="Longest Increasing Subsequence, Reconstructed",
    difficulty=4,
    tags=["dynamic programming", "binary search", "patience sorting"],
    fn="longest_increasing_subsequence",
    params=[["nums", "int[]"]],
    returns="int[]",
    statement=r"""
Return a **longest strictly increasing subsequence** of `nums` (elements in their original
order, each strictly greater than the previous).

Many sequences can tie for the maximum length. Return the one whose list of values is
**lexicographically smallest** (compare first values; if equal, second values; and so on).

`n` goes up to 3000 in the tests, but aim for **O(n log n)**.
""",
    constraints=["1 ≤ len(nums) ≤ 3000", "-10⁹ ≤ nums[i] ≤ 10⁹"],
    example_notes=["Length 4. Candidates include `2,5,7,101`, `2,3,7,18`, `2,3,7,101`; the smallest is `2,3,7,18`.",
                   "`0,1,2,3` beats `0,1,3,…`."],
    hints=[
        "Classic O(n log n) LIS (patience sorting) keeps `tails[k]` = the smallest possible last value of an increasing subsequence of length k+1. That gives the length, but the tie-break needs more.",
        "Compute `L[i]` = length of the longest increasing subsequence **starting** at `i` (run patience from the right on negated values). Then build the answer greedily from the front: at each step pick the smallest value that still allows the remaining length.",
        "Among indices with the same `L`, values never increase as the index grows (otherwise the earlier one could be extended). So the feasible candidates for each step form a contiguous block you can find with binary search; pick the smallest value, and its earliest index.",
    ],
    explanation=r"""
## Intuition

Two separate ideas meet here.

**Length in O(n log n): patience sorting.** Keep `tails[k]`, the smallest tail of any
increasing subsequence of length `k+1` seen so far. `tails` is strictly increasing, so for
each new `x`, `bisect_left(tails, x)` finds the first tail `≥ x`; replace it (or append).
The final `len(tails)` is the LIS length.

**Lexicographic reconstruction: decide from the front.** The lexicographically smallest
answer is built greedily: choose the smallest possible first value such that a full-length
sequence can still start there, then the smallest second value that keeps going, etc. To
know "can a sequence of length k start at i?", compute `L[i]`, the LIS length *starting* at
`i`, which is patience sorting run from the right with negated values.

## Approach

1. **Suffix lengths.** For `i = n−1 … 0`, run patience on `−nums[i]`:
   `pos = bisect_left(tails, −nums[i])`, `L[i] = pos + 1`, `tails[pos] = −nums[i]`.
2. **Group by level.** `level[k]` = indices with `L[i] = k`, in increasing index order.
   Key fact: along `level[k]`, values are **non-increasing**. (If `i < j`, `L[i] = L[j]`
   and `nums[i] < nums[j]`, then `i` could precede `j`'s sequence, so `L[i] > L[j]`.)
3. **Greedy.** Let `p` = last chosen index (start −1), `prev` = last chosen value (start −∞).
   For `k = best … 1`, within `level[k]`:
   * candidates must have index `> p` → a suffix of the list (binary search on indices);
   * and value `> prev` → a prefix of the list (values are non-increasing; binary search);
   * the smallest value in the intersection is at its **right end**; among equal values,
     take the **leftmost** (earliest index), which leaves the most room for later steps.

Trace for `[10, 9, 2, 5, 3, 7, 101, 18]`:

```text
i:      0   1   2   3   4   5   6    7
nums:  10   9   2   5   3   7  101  18
L[i]:   3   3   4   3   3   2   1    1

level 4: [2]            values 2           → pick 2 (idx 2)
level 3: [0,1,3,4]      values 10,9,5,3    → idx > 2 and value > 2: {5,3} → pick 3 (idx 4)
level 2: [5]            values 7           → pick 7 (idx 5)
level 1: [6,7]          values 101,18      → pick 18 (idx 7)
answer: 2 3 7 18
```

## Complexity

* **Time:** O(n log n): two patience passes of n binary searches, plus O(log n) per greedy step.
* **Space:** O(n).

## Common mistakes

* **`bisect_right` vs `bisect_left`.** Strictly increasing needs `bisect_left` (an equal
  value replaces, it does not extend). `bisect_right` computes the longest *non-decreasing* subsequence.
* **Thinking `tails` is an LIS.** It is not a subsequence at all (`[1, 5, 2]` → tails `[1, 2]`
  happens to be one, but `[3, 4, 1]` → tails `[1, 4]` is not in order).
* Reconstructing from the back with parent pointers gives *some* LIS, but not necessarily
  the lexicographically smallest.
* Picking the latest index among equal smallest values can strand you with too few elements later.

## Going further

* **Count** the LISs: a Fenwick tree over compressed values storing (best length, ways) pairs, O(n log n).
* **Russian doll envelopes**: sort by width ascending and height *descending*, then LIS on heights.
* The O(n²) DP `dp[i] = 1 + max(dp[j] for j < i if nums[j] < nums[i])` is the right first
  answer in an interview; mention patience sorting as the upgrade.
""",
    solution=r'''def longest_increasing_subsequence(nums):
    n = len(nums)
    # --- 1. L[i] = length of the longest strictly increasing subsequence STARTING at i.
    # Scanning right-to-left, a sequence that starts at i and goes right with increasing
    # values is a decreasing sequence in scan order; negate values to reuse the classic
    # "patience sorting" LIS. tails[k] = smallest (negated) tail of length k+1.
    tails = []
    L = [0] * n
    for i in range(n - 1, -1, -1):
        x = -nums[i]
        pos = bisect_left(tails, x)  # bisect_left => STRICTLY increasing
        if pos == len(tails):
            tails.append(x)
        else:
            tails[pos] = x
        L[i] = pos + 1
    best = len(tails)

    # --- 2. Group indices by L. Within one group, as the index grows the value never
    # increases (an earlier smaller value could otherwise be prepended, raising its L).
    level_idx = [[] for _ in range(best + 1)]
    level_neg = [[] for _ in range(best + 1)]   # negated values: non-decreasing lists
    for i in range(n):
        level_idx[L[i]].append(i)
        level_neg[L[i]].append(-nums[i])

    # --- 3. Greedy from the front: at each step take the smallest value that can still
    # start a sequence of the remaining length, using its earliest occurrence.
    result = []
    last_idx = -1
    for k in range(best, 0, -1):
        idx, neg = level_idx[k], level_neg[k]
        lo = bisect_right(idx, last_idx)          # first position with index > last_idx
        if result:
            # values > prev  <=>  -value < -prev: a prefix of the list ends here
            hi = bisect_left(neg, -result[-1]) - 1
        else:
            hi = len(idx) - 1
        v = -neg[hi]                              # smallest admissible value (right end)
        pos = max(lo, bisect_left(neg, -v))       # leftmost position holding that value
        result.append(v)
        last_idx = idx[pos]
    return result
''',
    refs={
        "c": r"""// first index in a[0..n) with a[i] >= x (C has no std::lower_bound)
static int lower_ll(const long long* a, int n, long long x) {
    int lo = 0, hi = n;
    while (lo < hi) { int m = (lo + hi) / 2; if (a[m] < x) lo = m + 1; else hi = m; }
    return lo;
}
// first index in a[0..n) with a[i] > x
static int upper_int(const int* a, int n, int x) {
    int lo = 0, hi = n;
    while (lo < hi) { int m = (lo + hi) / 2; if (a[m] <= x) lo = m + 1; else hi = m; }
    return lo;
}

long long* longest_increasing_subsequence(long long* nums, int numsSize, int* returnSize) {
    int n = numsSize;
    // 1. L[i] = length of the longest increasing subsequence STARTING at i.
    //    Scan right to left with patience sorting on negated values (an increasing
    //    run read backwards is a decreasing run, i.e. increasing in -x).
    long long* tails = malloc(sizeof(long long) * (size_t)n);
    int* L = malloc(sizeof(int) * (size_t)n);
    int best = 0;
    for (int i = n - 1; i >= 0; i--) {
        int p = lower_ll(tails, best, -nums[i]);
        tails[p] = -nums[i];
        if (p == best) best++;
        L[i] = p + 1;
    }

    // 2. Bucket indices by level L (counting sort keeps them in index order).
    //    Within one level values are non-increasing left to right (otherwise the
    //    left one could extend the right one and would have a higher level), so
    //    neg[] (= -value) is sorted and we can binary search it.
    int* start = calloc((size_t)best + 2, sizeof(int));
    for (int i = 0; i < n; i++) start[L[i] + 1]++;
    for (int k = 1; k <= best + 1; k++) start[k] += start[k - 1];
    int* fill = malloc(sizeof(int) * (size_t)(best + 1));
    memcpy(fill, start, sizeof(int) * (size_t)(best + 1));
    int* idx = malloc(sizeof(int) * (size_t)n);
    long long* neg = malloc(sizeof(long long) * (size_t)n);
    for (int i = 0; i < n; i++) { int p = fill[L[i]]++; idx[p] = i; neg[p] = -nums[i]; }

    // 3. Greedy: for slot k (needing a level-k element), the candidates are the
    //    level-k indices after the previous pick AND with value above it. That is
    //    a contiguous range [lo, hi]; the smallest value sits at hi. Among equal
    //    values take the leftmost allowed one, leaving the most room afterwards.
    long long* res = malloc(sizeof(long long) * (size_t)best);
    int cnt = 0, last = -1;
    for (int k = best; k >= 1; k--) {
        int* I = idx + start[k];
        long long* N = neg + start[k];
        int m = start[k + 1] - start[k];
        int lo = upper_int(I, m, last);
        int hi = cnt == 0 ? m - 1 : lower_ll(N, m, -res[cnt - 1]) - 1;
        long long v = -N[hi];
        int pos = lower_ll(N, m, -v);
        if (pos < lo) pos = lo;
        res[cnt++] = v;
        last = I[pos];
    }
    free(tails); free(L); free(start); free(fill); free(idx); free(neg);
    *returnSize = cnt;
    return res;
}""",
        "cpp": r"""vector<long long> longestIncreasingSubsequence(vector<long long>& nums) {
    int n = nums.size();
    vector<long long> tails;
    vector<int> L(n);
    for (int i = n - 1; i >= 0; i--) {                // LIS starting at i (negated patience)
        long long x = -nums[i];
        auto it = lower_bound(tails.begin(), tails.end(), x);
        L[i] = (it - tails.begin()) + 1;
        if (it == tails.end()) tails.push_back(x); else *it = x;
    }
    int best = tails.size();
    vector<vector<int>> idx(best + 1);
    vector<vector<long long>> neg(best + 1);          // non-decreasing within a level
    for (int i = 0; i < n; i++) { idx[L[i]].push_back(i); neg[L[i]].push_back(-nums[i]); }
    vector<long long> res;
    int last = -1;
    for (int k = best; k >= 1; k--) {
        auto& I = idx[k]; auto& N = neg[k];
        int lo = upper_bound(I.begin(), I.end(), last) - I.begin();
        int hi = res.empty() ? (int)I.size() - 1
                             : int(lower_bound(N.begin(), N.end(), -res.back()) - N.begin()) - 1;
        long long v = -N[hi];
        int pos = max(lo, int(lower_bound(N.begin(), N.end(), -v) - N.begin()));
        res.push_back(v);
        last = I[pos];
    }
    return res;
}""",
        "rust": r"""pub fn longest_increasing_subsequence(nums: Vec<i64>) -> Vec<i64> {
    let n = nums.len();
    let mut tails: Vec<i64> = Vec::new();
    let mut l = vec![0usize; n];
    for i in (0..n).rev() {
        let x = -nums[i];
        let pos = tails.partition_point(|&t| t < x); // bisect_left
        if pos == tails.len() { tails.push(x); } else { tails[pos] = x; }
        l[i] = pos + 1;
    }
    let best = tails.len();
    let mut idx: Vec<Vec<usize>> = vec![Vec::new(); best + 1];
    let mut neg: Vec<Vec<i64>> = vec![Vec::new(); best + 1];
    for i in 0..n {
        idx[l[i]].push(i);
        neg[l[i]].push(-nums[i]);
    }
    let mut res: Vec<i64> = Vec::new();
    let mut last: i64 = -1;
    for k in (1..=best).rev() {
        let (iv, nv) = (&idx[k], &neg[k]);
        let lo = iv.partition_point(|&j| (j as i64) <= last); // bisect_right
        let hi = match res.last() {
            Some(&prev) => nv.partition_point(|&t| t < -prev) - 1,
            None => iv.len() - 1,
        };
        let v = -nv[hi];
        let pos = lo.max(nv.partition_point(|&t| t < -v));
        res.push(v);
        last = iv[pos] as i64;
    }
    res
}""",
    },
    tests=_lis_tests(),
)


# ======================================================================== sliding window median
def _swm_tests():
    r = _rng(1671)
    return [
        [[1, 3, -1, -3, 5, 3, 6, 7], 3],
        [[1, 2, 3, 4, 2, 3, 1, 4, 2], 3],
        [[5], 1],
        [[1, 4], 2],
        [[2147483647, 2147483647], 2],
        [[-2147483648, -2147483648, 2147483647], 2],
        [[r.randint(0, 3) for _ in range(60)], 4],
        [[r.randint(-100, 100) for _ in range(300)], 7],
        [[r.randint(-2**31, 2**31 - 1) for _ in range(2000)], 700],
        [[r.randint(0, 5) for _ in range(1500)], 1500],
    ]


P_SWMEDIAN = dict(
    id="sliding-window-median",
    title="Sliding Window Median",
    difficulty=4,
    tags=["heap", "sliding window", "lazy deletion"],
    fn="median_sliding_window",
    params=[["nums", "int[]"], ["k", "int"]],
    returns="float[]",
    statement=r"""
A window of size `k` slides over `nums` from left to right, one position at a time. Return
the **median** of each of the `n − k + 1` windows, in order.

The median of an odd-sized window is its middle element when sorted; of an even-sized
window, the average of the two middle elements (which may be a `.5` value).
""",
    constraints=["1 ≤ k ≤ len(nums) ≤ 2000", "-2³¹ ≤ nums[i] ≤ 2³¹ − 1"],
    example_notes=["Windows `[1,3,-1]→1`, `[3,-1,-3]→-1`, `[-1,-3,5]→-1`, `[-3,5,3]→3`, `[5,3,6]→5`, `[3,6,7]→6`.",
                   "Duplicates are fine: each copy is a separate element."],
    hints=[
        "Sorting every window is O(n·k log k). What structure gives the median of a changing multiset quickly?",
        "Split the window into a max-heap of the smaller half and a min-heap of the larger half, sizes differing by at most one. The median is at the tops.",
        "Heaps can't delete arbitrary elements. Instead record the outgoing value in a 'to delete' counter and only pop it when it reaches a heap's top (lazy deletion). Track the *logical* sizes of the halves separately from the physical heap lengths.",
    ],
    explanation=r"""
## Intuition

For a **growing** stream (next problem) two heaps suffice: `lo` (max-heap) holds the
smaller half, `hi` (min-heap) the larger half, and the median sits at their tops. A
sliding window also **removes** elements, and binary heaps only remove the top. The trick
is **lazy deletion**: remember that a value is dead (`delayed[x] += 1`), adjust the
logical size of the half it lived in, and physically pop it only when it surfaces at a top.

```text
lo (max-heap)        hi (min-heap)
[ -3, -1, 1 ]  | 3 | [ 5, 6 ]          median = top of lo (odd k) or average of tops
     smaller half         larger half
```

## Approach

Invariants: every live value in `lo` ≤ every live value in `hi`; `size_lo` equals
`size_hi` or `size_hi + 1`; the **tops of both heaps are live** (pruned).

* **add(x)**: push into `lo` if `x ≤ top(lo)`, else into `hi`; rebalance.
* **remove(x)**: `delayed[x] += 1`; if `x ≤ top(lo)` it lives in `lo` (decrement `size_lo`),
  else in `hi`; prune tops; rebalance.
* **rebalance**: move a top across if the sizes are off; prune the heap you popped from.
* **prune(heap)**: while its top is in `delayed`, pop it and decrement the counter.
* **median**: `top(lo)` if `k` is odd, else `(top(lo) + top(hi)) / 2`.

Why is `x ≤ top(lo)` the right test for removal? If `x < top(lo)`, `x` can't be in `hi`
(everything there is ≥ `top(lo)`). If `x == top(lo)`, `lo` certainly holds a copy. Values
are interchangeable, so removing *a* copy from `lo` is correct.

Trace (`k = 3`) on `1 3 -1 -3 5`:

| step | lo | hi | median |
|---|---|---|---|
| add 1, 3, −1 | {1, −1} | {3} | 1 |
| remove 1, add −3 | {−1, −3} | {3} | −1 |
| remove 3, add 5 | {−1, −3} | {5} | −1 |

## Complexity

* **Time:** O(n log n): each element is pushed once and popped at most once (amortized), heaps hold O(n) entries.
* **Space:** O(n) for heaps that may contain dead entries plus the `delayed` counter.

## Common mistakes

* **Overflow** when averaging: `(a + b) / 2` with two values near 2³¹ overflows 32-bit
  ints. Use 64-bit or `a / 2.0 + b / 2.0`. (Here C/C++/Rust ints are 64-bit already.)
* **Integer division** for the even case: `(1 + 4) / 2` must be `2.5`.
* Comparing the heap's *physical* length instead of the logical size (dead entries inflate it).
* In C++, `multiset::erase(x)` erases **all** copies; use `erase(find(x))`.

## Going further

* Ordered multisets (`std::multiset`, Rust `BTreeMap<value, count>`, a sorted list with
  `bisect` in Python) give a simpler O(n log k) solution: insert, erase one, read the middle.
  The C++ and Rust references use that approach.
* An **order-statistic tree** or a Fenwick tree over compressed values answers the
  k-th smallest in O(log n), generalising to any percentile.
""",
    solution=r'''def median_sliding_window(nums, k):
    lo, hi = [], []                  # lo: max-heap via negation; hi: min-heap
    delayed = defaultdict(int)       # value -> how many dead copies are still in a heap
    size_lo = size_hi = 0            # LOGICAL sizes (live elements only)

    def prune(heap, sign):
        # Pop dead values sitting on top. sign converts stored keys back to values.
        while heap and delayed[sign * heap[0]]:
            delayed[sign * heap[0]] -= 1
            heappop(heap)

    def rebalance():
        nonlocal size_lo, size_hi
        if size_lo > size_hi + 1:    # lo too big: move its max to hi
            heappush(hi, -heappop(lo))
            size_lo -= 1
            size_hi += 1
            prune(lo, -1)            # a dead value may now be exposed on lo's top
        elif size_lo < size_hi:      # hi too big: move its min to lo
            heappush(lo, -heappop(hi))
            size_hi -= 1
            size_lo += 1
            prune(hi, 1)

    def add(x):
        nonlocal size_lo, size_hi
        if not lo or x <= -lo[0]:
            heappush(lo, -x)
            size_lo += 1
        else:
            heappush(hi, x)
            size_hi += 1
        rebalance()

    def remove(x):
        nonlocal size_lo, size_hi
        delayed[x] += 1              # it will be popped once it reaches a top
        if x <= -lo[0]:              # it lives in the lower half
            size_lo -= 1
        else:
            size_hi -= 1
        prune(lo, -1)                # keep both tops live
        prune(hi, 1)
        rebalance()

    out = []
    for i, x in enumerate(nums):
        add(x)
        if i >= k:
            remove(nums[i - k])      # the element that just left the window
        if i >= k - 1:
            if k % 2:
                out.append(float(-lo[0]))
            else:
                out.append((-lo[0] + hi[0]) / 2)   # true division: may be x.5
    return out
''',
    refs={
        "c": r"""// Keep the current window as a SORTED array. Each slide removes one value and
// inserts one value with memmove: O(k) per step, O(n·k) overall. That is the
// classic embedded answer (no heaps, no allocation per step, cache-friendly),
// and with n <= 2000 it is ~4 million moved longs in the worst case.

// first index in a[0..n) with a[i] >= x
static int lower_ll(const long long* a, int n, long long x) {
    int lo = 0, hi = n;
    while (lo < hi) { int m = (lo + hi) / 2; if (a[m] < x) lo = m + 1; else hi = m; }
    return lo;
}

double* median_sliding_window(long long* nums, int numsSize, long long k, int* returnSize) {
    int n = numsSize, K = (int)k;
    long long* w = malloc(sizeof(long long) * (size_t)K);
    double* out = malloc(sizeof(double) * (size_t)(n - K + 1));
    int size = 0, cnt = 0;
    for (int i = 0; i < n; i++) {
        if (i >= K) {                              // evict nums[i-K]: any copy will do
            int p = lower_ll(w, size, nums[i - K]);
            memmove(w + p, w + p + 1, sizeof(long long) * (size_t)(size - p - 1));
            size--;
        }
        int p = lower_ll(w, size, nums[i]);        // insert nums[i] in order
        memmove(w + p + 1, w + p, sizeof(long long) * (size_t)(size - p));
        w[p] = nums[i];
        size++;
        if (size == K) {
            // Convert to double BEFORE adding: two values near 2^31 are fine in a
            // long long, but averaging in double avoids any integer-rounding trap.
            out[cnt++] = (K & 1) ? (double)w[K / 2]
                                 : ((double)w[K / 2 - 1] + (double)w[K / 2]) / 2.0;
        }
    }
    free(w);
    *returnSize = cnt;
    return out;
}""",
        "cpp": r"""vector<double> medianSlidingWindow(vector<long long>& nums, long long k) {
    // Two ordered multisets: lo = smaller half (size ceil(k/2)), hi = larger half.
    multiset<long long> lo, hi;
    auto rebalance = [&] {
        while (lo.size() > hi.size() + 1) { hi.insert(*prev(lo.end())); lo.erase(prev(lo.end())); }
        while (lo.size() < hi.size()) { lo.insert(*hi.begin()); hi.erase(hi.begin()); }
    };
    vector<double> out;
    for (size_t i = 0; i < nums.size(); i++) {
        long long x = nums[i];
        if (lo.empty() || x <= *prev(lo.end())) lo.insert(x); else hi.insert(x);
        rebalance();
        if (i >= (size_t)k) {
            long long y = nums[i - k];
            // erase ONE copy: erase(find(y)), never erase(y)
            if (y <= *prev(lo.end())) lo.erase(lo.find(y)); else hi.erase(hi.find(y));
            rebalance();
        }
        if (i + 1 >= (size_t)k) {
            if (k & 1) out.push_back((double)*prev(lo.end()));
            else out.push_back(((double)*prev(lo.end()) + (double)*hi.begin()) / 2.0);
        }
    }
    return out;
}""",
        "rust": r"""use std::collections::BTreeMap;

// Ordered multiset on top of BTreeMap<value, count>.
struct Multi { m: BTreeMap<i64, usize>, len: usize }
impl Multi {
    fn new() -> Self { Multi { m: BTreeMap::new(), len: 0 } }
    fn insert(&mut self, x: i64) { *self.m.entry(x).or_insert(0) += 1; self.len += 1; }
    fn remove(&mut self, x: i64) {
        let c = self.m.get_mut(&x).unwrap();
        *c -= 1;
        if *c == 0 { self.m.remove(&x); }
        self.len -= 1;
    }
    fn max(&self) -> i64 { *self.m.keys().next_back().unwrap() }
    fn min(&self) -> i64 { *self.m.keys().next().unwrap() }
}

pub fn median_sliding_window(nums: Vec<i64>, k: i64) -> Vec<f64> {
    let k = k as usize;
    let (mut lo, mut hi) = (Multi::new(), Multi::new());
    let rebalance = |lo: &mut Multi, hi: &mut Multi| {
        while lo.len > hi.len + 1 { let v = lo.max(); lo.remove(v); hi.insert(v); }
        while lo.len < hi.len { let v = hi.min(); hi.remove(v); lo.insert(v); }
    };
    let mut out = Vec::new();
    for i in 0..nums.len() {
        let x = nums[i];
        if lo.len == 0 || x <= lo.max() { lo.insert(x); } else { hi.insert(x); }
        rebalance(&mut lo, &mut hi);
        if i >= k {
            let y = nums[i - k];
            if y <= lo.max() { lo.remove(y); } else { hi.remove(y); }
            rebalance(&mut lo, &mut hi);
        }
        if i + 1 >= k {
            out.push(if k % 2 == 1 { lo.max() as f64 } else { (lo.max() as f64 + hi.min() as f64) / 2.0 });
        }
    }
    out
}""",
    },
    tests=_swm_tests(),
)


# ======================================================================== TSP bitmask
def _tsp_matrix(r, n, sym):
    d = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                d[i][j] = r.randint(1, 1000)
    if sym:
        for i in range(n):
            for j in range(i):
                d[i][j] = d[j][i]
    return d


def _tsp_tests():
    r = _rng(1681)
    return [
        [[[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]]],
        [[[0]]],
        [[[0, 5], [7, 0]]],
        [[[0, 1, 9], [9, 0, 1], [1, 9, 0]]],
        [_tsp_matrix(r, 5, True)],
        [_tsp_matrix(r, 8, False)],
        [_tsp_matrix(r, 12, True)],
        [_tsp_matrix(r, 12, False)],
    ]


P_TSP = dict(
    id="tsp-bitmask-dp",
    title="Traveling Salesman (Bitmask DP)",
    difficulty=4,
    tags=["dynamic programming", "bitmask", "graph"],
    fn="shortest_tour",
    params=[["dist", "int[][]"]],
    returns="int",
    espresso=False,
    statement=r"""
There are `n` cities, numbered `0 … n−1`. `dist[i][j]` is the cost of travelling directly
from city `i` to city `j` (it may differ from `dist[j][i]`; `dist[i][i] = 0`).

Starting at city `0`, visit every other city **exactly once** and return to city `0`.
Return the minimum total cost of such a tour. For `n = 1` the answer is `0`.
""",
    constraints=["1 ≤ n ≤ 12", "1 ≤ dist[i][j] ≤ 1000 for i ≠ j"],
    example_notes=["Tour `0 → 1 → 3 → 2 → 0` costs `10 + 25 + 30 + 15 = 80`.",
                   "One city: nothing to visit."],
    hints=[
        "Trying all (n−1)! orders is 39 916 800 tours for n = 12, each O(n). Which information about a partial tour actually matters for the rest of it?",
        "Only *which* cities have been visited and *where you are now* matter, not the order. That's 2ⁿ · n states.",
        "`dp[mask][j]` = cheapest way to start at 0, visit exactly the cities in `mask`, and end at `j`. Extend to every unvisited `k`: `dp[mask | 1<<k][k] = min(…, dp[mask][j] + dist[j][k])`. The answer closes the loop: `min_j dp[full][j] + dist[j][0]`.",
    ],
    explanation=r"""
## Intuition

TSP is NP-hard, so no polynomial algorithm is expected, but we can still beat brute force
dramatically. The future cost of a partial tour depends only on **the set of visited
cities** and **the current city**, not the order in which they were visited. Collapse all
orders with the same (set, last) into one DP state: 2ⁿ·n states instead of n! paths. This is
the **Held–Karp** algorithm; sets are represented as bitmasks.

```text
n = 12:   (n−1)! ≈ 4·10⁷ orders × 12        vs   2¹² · 12 · 12 ≈ 5.9·10⁵ transitions
```

## Approach

1. `dp[mask][j] = ∞`, except `dp[1][0] = 0` (only city 0 visited, standing at 0).
2. Iterate masks in increasing numeric order (a superset is always numerically larger, so
   every state is final before it is extended). For each `j` in `mask` with finite `dp`,
   for each `k` not in `mask`:
   `dp[mask | 1<<k][k] = min(dp[mask | 1<<k][k], dp[mask][j] + dist[j][k])`.
3. Answer: `min over j ≠ 0 of dp[full][j] + dist[j][0]`, where `full = 2ⁿ − 1`.

Small trace on the 3-city example `dist = [[0,1,9],[9,0,1],[1,9,0]]`:

| mask (cities) | end | cost |
|---|---|---|
| {0} | 0 | 0 |
| {0,1} | 1 | 1 |
| {0,2} | 2 | 9 |
| {0,1,2} | 2 | 1 + 1 = 2 (via 1) |
| {0,1,2} | 1 | 9 + 9 = 18 (via 2) |

Close the loop: `min(2 + dist[2][0], 18 + dist[1][0]) = min(3, 27) = 3`.

## Complexity

* **Time:** O(2ⁿ · n²) ≈ 5.9·10⁵ for n = 12 (fine even in Python), and still OK up to n ≈ 20 in C++.
* **Space:** O(2ⁿ · n).

## Common mistakes

* Forgetting to return to city 0 (that is the "Hamiltonian path" variant).
* Starting with `dp[0][0] = 0` and then "visiting" 0 again.
* Iterating masks that don't contain city 0, wasting half the work (harmless but slow).
* `1 << k` precedence in C: `mask & 1 << k` is `mask & (1 << k)`, but `mask & 1 << k == 0`
  is `mask & ((1 << k) == 0)`. Parenthesise.
* n = 1: there is no `j ≠ 0`; return 0.

## Going further

* **Reconstruct the tour** by storing the argmin predecessor for each state.
* Other subset DPs with the same shape: assignment problems ("n workers, n jobs"),
  "minimum cost to cover all skills", counting Hamiltonian paths.
* For large n, practical solvers use branch and bound, 2-opt local search, or Christofides'
  1.5-approximation for metric (symmetric, triangle-inequality) instances.
""",
    solution=r'''def shortest_tour(dist):
    n = len(dist)
    if n == 1:
        return 0                     # nothing to visit, no edge to take
    INF = float("inf")
    FULL = (1 << n) - 1
    # dp[mask][j]: cheapest path that starts at city 0, visits exactly the cities
    # whose bits are set in mask, and currently stands at city j (j in mask).
    dp = [[INF] * n for _ in range(1 << n)]
    dp[1][0] = 0                     # only city 0 visited, standing on it

    for mask in range(1, 1 << n):
        if not mask & 1:
            continue                 # every useful state contains the start city
        row = dp[mask]
        for j in range(n):
            cost = row[j]
            if cost == INF:          # unreachable state (also covers j not in mask)
                continue
            for k in range(n):
                if mask & (1 << k):
                    continue         # k already visited
                nxt = mask | (1 << k)    # numerically larger => processed later
                c = cost + dist[j][k]
                if c < dp[nxt][k]:
                    dp[nxt][k] = c

    # Close the cycle: from the last city back to 0.
    return min(dp[FULL][j] + dist[j][0] for j in range(1, n))
''',
    refs={
        "c": r"""// Held–Karp: dp[mask][j] = cheapest path that starts at city 0, visits exactly
// the cities in `mask` (always including 0), and currently stands at city j.
// Flattened into one array: dp[mask * n + j]. 2^12 * 12 longs = 384 KiB.
long long shortest_tour(long long** dist, int distSize, int* distColSize) {
    (void)distColSize;
    int n = distSize;
    if (n == 1) return 0;
    const long long INF = LLONG_MAX / 4;          // big, but INF + cost can't overflow
    int full = (1 << n) - 1;
    long long* dp = malloc(sizeof(long long) * ((size_t)1 << n) * (size_t)n);
    for (size_t i = 0; i < ((size_t)1 << n) * (size_t)n; i++) dp[i] = INF;
    dp[1 * n + 0] = 0;                             // only city 0 visited, standing on it
    // Masks only grow, so increasing numeric order is a valid topological order.
    for (int mask = 1; mask <= full; mask += 2) {  // odd masks: those containing city 0
        for (int j = 0; j < n; j++) {
            long long cur = dp[mask * n + j];
            if (cur >= INF) continue;
            for (int k = 0; k < n; k++) {
                if (mask & (1 << k)) continue;     // already visited
                long long* slot = &dp[(mask | (1 << k)) * n + k];
                if (cur + dist[j][k] < *slot) *slot = cur + dist[j][k];
            }
        }
    }
    long long best = INF;
    for (int j = 1; j < n; j++)                    // close the loop back to city 0
        if (dp[full * n + j] + dist[j][0] < best) best = dp[full * n + j] + dist[j][0];
    free(dp);
    return best;
}""",
        "cpp": r"""long long shortestTour(vector<vector<long long>>& dist) {
    int n = dist.size();
    if (n == 1) return 0;
    const long long INF = LLONG_MAX / 4;
    int full = (1 << n) - 1;
    vector<vector<long long>> dp(1 << n, vector<long long>(n, INF));
    dp[1][0] = 0;
    for (int mask = 1; mask <= full; mask += 2)          // odd masks contain city 0
        for (int j = 0; j < n; j++) {
            long long cur = dp[mask][j];
            if (cur >= INF) continue;
            for (int k = 0; k < n; k++) {
                if (mask & (1 << k)) continue;
                int nxt = mask | (1 << k);
                dp[nxt][k] = min(dp[nxt][k], cur + dist[j][k]);
            }
        }
    long long best = INF;
    for (int j = 1; j < n; j++) best = min(best, dp[full][j] + dist[j][0]);
    return best;
}""",
        "rust": r"""pub fn shortest_tour(dist: Vec<Vec<i64>>) -> i64 {
    let n = dist.len();
    if n == 1 {
        return 0;
    }
    const INF: i64 = i64::MAX / 4; // headroom: INF + cost never overflows
    let full = (1usize << n) - 1;
    let mut dp = vec![vec![INF; n]; 1 << n];
    dp[1][0] = 0;
    for mask in (1..=full).step_by(2) { // odd masks = contain city 0
        for j in 0..n {
            let cur = dp[mask][j];
            if cur >= INF {
                continue;
            }
            for k in 0..n {
                if mask & (1 << k) != 0 {
                    continue;
                }
                let nxt = mask | (1 << k);
                dp[nxt][k] = dp[nxt][k].min(cur + dist[j][k]);
            }
        }
    }
    (1..n).map(|j| dp[full][j] + dist[j][0]).min().unwrap()
}""",
    },
    tests=_tsp_tests(),
)


# ======================================================================== Dijkstra lex path
def _dij_graph(r, n, m, wmax):
    edges = []
    for _ in range(m):
        u, v = r.randrange(n), r.randrange(n)
        if u != v:
            edges.append([u, v, r.randint(1, wmax)])
    return edges


def _dij_tests():
    t = [
        [5, [[0, 1, 2], [0, 2, 1], [1, 3, 1], [2, 3, 2], [3, 4, 1]], 0, 4],
        [3, [[0, 1, 1]], 0, 2],
        [1, [], 0, 0],
        [4, [[0, 2, 1], [2, 3, 1], [0, 1, 1], [1, 3, 1]], 0, 3],
        [4, [[0, 1, 5], [0, 1, 2], [1, 0, 1], [1, 2, 2], [2, 3, 2], [1, 3, 4]], 0, 3],
        [3, [[1, 0, 1], [2, 1, 1]], 0, 2],
    ]
    for seed, n, m, w in [(1, 8, 20, 3), (2, 30, 120, 4), (3, 300, 1200, 5), (4, 600, 1500, 1000)]:
        r = _rng(1690 + seed)
        t.append([n, _dij_graph(r, n, m, w), 0, n - 1])
    return t


P_DIJKSTRA = dict(
    id="dijkstra-lexicographic-path",
    title="Shortest Path with Reconstruction (Dijkstra)",
    difficulty=3,
    tags=["graph", "dijkstra", "shortest path", "heap"],
    fn="shortest_path_lex",
    params=[["n", "int"], ["edges", "int[][]"], ["src", "int"], ["dst", "int"]],
    returns="int[]",
    statement=r"""
A **directed** graph has `n` nodes `0 … n−1`; `edges[i] = [u, v, w]` is an edge from `u`
to `v` with positive weight `w` (parallel edges may exist).

Return a **shortest path** from `src` to `dst` as the list of nodes visited, starting with
`src` and ending with `dst`. If several shortest paths exist, return the one whose node
sequence is **lexicographically smallest**. If `dst` is unreachable, return an empty list.
If `src == dst`, return `[src]`.
""",
    constraints=["1 ≤ n ≤ 600", "0 ≤ len(edges) ≤ 1500", "1 ≤ w ≤ 1000", "0 ≤ src, dst < n"],
    example_notes=["Both `0→1→3→4` and `0→2→3→4` cost 4; `[0,1,3,4]` is lexicographically smaller.",
                   "Node 2 has no incoming edge: unreachable."],
    hints=[
        "Plain Dijkstra with parent pointers gives *a* shortest path, but which one depends on heap order. You need a rule for ties.",
        "Building the path from the **front** is what lexicographic order rewards: at each node, step to the smallest neighbour that keeps you on *some* shortest path. How do you know a neighbour is still on a shortest path to `dst`?",
        "Run Dijkstra **from `dst` on the reversed graph** to get `d[v]` = distance from `v` to `dst`. Edge `u→v` lies on a shortest path iff `w + d[v] == d[u]`. Walk from `src`, always taking the smallest such `v`.",
    ],
    explanation=r"""
## Intuition

Dijkstra settles nodes in order of distance using a min-heap; a parent pointer per node
lets you rebuild *one* shortest path by walking back from `dst`. That path's tie-breaking is
an accident of heap order. To make the answer unique we want the **lexicographically
smallest** node sequence, which is decided from the *front*: the second node should be as
small as possible, then the third, etc.

Greedy from the front works if we can test, at each node `u`, which outgoing edges keep us
on a shortest path to `dst`. Distances **to** `dst` give exactly that test:

```text
edge u → v (weight w) is "tight"  ⇔  w + dist(v → dst) == dist(u → dst)
```

So compute `dist(· → dst)` with Dijkstra on the **reversed** graph, then walk.

## Approach

1. Build `adj` (forward) and `radj` (reversed) lists.
2. Dijkstra from `dst` over `radj`: `d[v]` = shortest distance from `v` to `dst`.
3. If `d[src] = ∞`, return `[]`.
4. `u = src`; while `u ≠ dst`: among forward edges `u → v` with `w + d[v] == d[u]`, move to
   the smallest `v`. Since `w ≥ 1`, `d` strictly decreases, so the walk terminates and
   never revisits a node.

Dijkstra itself (lazy version):

```python
d = [inf] * n; d[dst] = 0; pq = [(0, dst)]
while pq:
    du, u = heappop(pq)
    if du > d[u]: continue        # stale entry: u was already settled cheaper
    for v, w in radj[u]:
        if du + w < d[v]:
            d[v] = du + w
            heappush(pq, (d[v], v))
```

Trace on example 1 (edges 0→1:2, 0→2:1, 1→3:1, 2→3:2, 3→4:1, dst = 4):

```text
d to dst: d[4]=0, d[3]=1, d[1]=2, d[2]=3, d[0]=4
walk: at 0, tight edges: 0→1 (2+2=4 ✔), 0→2 (1+3=4 ✔) → take 1
      at 1: 1→3 (1+1=2 ✔) → 3;   at 3: 3→4 ✔ → 4
path [0, 1, 3, 4]
```

## Complexity

* **Time:** O((V + E) log V) for Dijkstra, plus O(E) for the walk (each edge inspected at most once).
* **Space:** O(V + E).

## Common mistakes

* **Negative or zero weights.** Dijkstra requires `w ≥ 0`; with `w = 0` cycles the greedy
  walk could loop. (Bellman–Ford handles negatives.)
* Not skipping stale heap entries (`du > d[u]`): still correct, but can blow up the running time.
* Running forward Dijkstra and choosing the smallest *parent*: that minimises the sequence
  read from the back, not from the front.
* Unreachable `dst`: return `[]`, not `[src]`.
* In C++, `priority_queue` is a max-heap: use `greater<>` or push negated distances.

## Going further

* **Parent pointers** (the usual reconstruction): `parent[v] = u` whenever `d[v]` improves;
  then follow parents from `dst` and reverse. O(V) extra, and fine when any shortest path will do.
* **0-1 BFS** (deque) for weights in {0, 1}; **A\*** adds a heuristic to aim towards the target.
* "Count shortest paths" is a DP over the same tight-edge DAG.
""",
    solution=r'''def shortest_path_lex(n, edges, src, dst):
    adj = [[] for _ in range(n)]     # forward edges, used for the final walk
    radj = [[] for _ in range(n)]    # reversed edges, for distances TO dst
    for u, v, w in edges:
        adj[u].append((v, w))
        radj[v].append((u, w))

    # Dijkstra from dst on the reversed graph: d[v] = shortest distance v -> dst.
    INF = float("inf")
    d = [INF] * n
    d[dst] = 0
    pq = [(0, dst)]
    while pq:
        du, u = heappop(pq)
        if du > d[u]:
            continue                 # stale heap entry, u already settled cheaper
        for v, w in radj[u]:         # original edge v -> u with weight w
            if du + w < d[v]:
                d[v] = du + w
                heappush(pq, (d[v], v))

    if d[src] == INF:
        return []                    # dst unreachable from src

    # Greedy walk from the front. An edge u -> v keeps us on a shortest path iff
    # w + d[v] == d[u]. Choosing the smallest such v at every step yields the
    # lexicographically smallest shortest path. w >= 1 makes d strictly decrease,
    # so the walk always ends at dst.
    path = [src]
    u = src
    while u != dst:
        u = min(v for v, w in adj[u] if w + d[v] == d[u])
        path.append(u)
    return path
''',
    refs={
        "c": r"""// Plan: run Dijkstra BACKWARDS from dst, so d[v] = shortest distance v -> dst.
// Then walk forward from src, always taking the smallest-numbered neighbour v
// that stays on a shortest path (w + d[v] == d[u]). Greedy on the first
// differing node is exactly what "lexicographically smallest" asks for.
long long* shortest_path_lex(long long n, long long** edges, int edgesSize, int* edgesColSize,
                             long long src, long long dst, int* returnSize) {
    (void)edgesColSize;
    int N = (int)n, E = edgesSize;
    // CSR (compressed sparse row) adjacency, out- and in-edges, from edge indices:
    // count per node, prefix-sum into start offsets, then scatter.
    int* ostart = calloc((size_t)N + 1, sizeof(int));
    int* istart = calloc((size_t)N + 1, sizeof(int));
    for (int e = 0; e < E; e++) { ostart[edges[e][0] + 1]++; istart[edges[e][1] + 1]++; }
    for (int i = 0; i < N; i++) { ostart[i + 1] += ostart[i]; istart[i + 1] += istart[i]; }
    int* oadj = malloc(sizeof(int) * (size_t)(E + 1));
    int* iadj = malloc(sizeof(int) * (size_t)(E + 1));
    int* ofill = malloc(sizeof(int) * (size_t)N);
    int* ifill = malloc(sizeof(int) * (size_t)N);
    memcpy(ofill, ostart, sizeof(int) * (size_t)N);
    memcpy(ifill, istart, sizeof(int) * (size_t)N);
    for (int e = 0; e < E; e++) {
        oadj[ofill[edges[e][0]]++] = e;
        iadj[ifill[edges[e][1]]++] = e;
    }

    // Array-based Dijkstra: O(V^2 + E). With V <= 600 that is simpler (and just as
    // fast in practice) as a binary heap, and it needs no extra data structure.
    const long long INF = LLONG_MAX / 4;
    long long* d = malloc(sizeof(long long) * (size_t)N);
    bool* done = calloc((size_t)N, sizeof(bool));
    for (int i = 0; i < N; i++) d[i] = INF;
    d[dst] = 0;
    for (;;) {
        int u = -1;
        for (int i = 0; i < N; i++)               // closest unfinished node
            if (!done[i] && d[i] < INF && (u < 0 || d[i] < d[u])) u = i;
        if (u < 0) break;
        done[u] = true;
        for (int j = istart[u]; j < istart[u + 1]; j++) {   // relax edges INTO u
            long long* e = edges[iadj[j]];
            int v = (int)e[0];
            if (d[u] + e[2] < d[v]) d[v] = d[u] + e[2];
        }
    }

    long long* path = NULL;
    int len = 0;
    if (d[src] < INF) {
        path = malloc(sizeof(long long) * (size_t)N);   // a shortest path is simple
        int u = (int)src;
        path[len++] = u;
        while (u != dst) {
            int best = INT_MAX;
            for (int j = ostart[u]; j < ostart[u + 1]; j++) {
                long long* e = edges[oadj[j]];
                int v = (int)e[1];
                if (e[2] + d[v] == d[u] && v < best) best = v;
            }
            u = best;                     // exists: d[u] was achieved by some edge
            path[len++] = u;
        }
    }
    free(ostart); free(istart); free(oadj); free(iadj); free(ofill); free(ifill);
    free(d); free(done);
    *returnSize = len;
    return path;
}""",
        "cpp": r"""vector<long long> shortestPathLex(long long n, vector<vector<long long>>& edges, long long src, long long dst) {
    vector<vector<pair<int, long long>>> adj(n), radj(n);
    for (auto& e : edges) { adj[e[0]].push_back({(int)e[1], e[2]}); radj[e[1]].push_back({(int)e[0], e[2]}); }
    const long long INF = LLONG_MAX / 4;
    vector<long long> d(n, INF);
    // min-heap of (distance, node)
    priority_queue<pair<long long, int>, vector<pair<long long, int>>, greater<>> pq;
    d[dst] = 0; pq.push({0, (int)dst});
    while (!pq.empty()) {
        auto [du, u] = pq.top(); pq.pop();
        if (du > d[u]) continue;
        for (auto [v, w] : radj[u])
            if (du + w < d[v]) { d[v] = du + w; pq.push({d[v], v}); }
    }
    if (d[src] >= INF) return {};
    vector<long long> path{src};
    for (int u = src; u != dst;) {
        int best = INT_MAX;
        for (auto [v, w] : adj[u]) if (w + d[v] == d[u]) best = min(best, v);
        u = best;
        path.push_back(u);
    }
    return path;
}""",
        "rust": r"""use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn shortest_path_lex(n: i64, edges: Vec<Vec<i64>>, src: i64, dst: i64) -> Vec<i64> {
    let n = n as usize;
    let (src, dst) = (src as usize, dst as usize);
    let mut adj: Vec<Vec<(usize, i64)>> = vec![Vec::new(); n];
    let mut radj: Vec<Vec<(usize, i64)>> = vec![Vec::new(); n];
    for e in &edges {
        adj[e[0] as usize].push((e[1] as usize, e[2]));
        radj[e[1] as usize].push((e[0] as usize, e[2]));
    }
    let mut d = vec![i64::MAX; n];
    let mut pq = BinaryHeap::new(); // max-heap; Reverse turns it into a min-heap
    d[dst] = 0;
    pq.push(Reverse((0i64, dst)));
    while let Some(Reverse((du, u))) = pq.pop() {
        if du > d[u] {
            continue;
        }
        for &(v, w) in &radj[u] {
            if du + w < d[v] {
                d[v] = du + w;
                pq.push(Reverse((d[v], v)));
            }
        }
    }
    if d[src] == i64::MAX {
        return vec![];
    }
    let mut path = vec![src as i64];
    let mut u = src;
    while u != dst {
        // d[v] != MAX guards the addition against overflow
        u = adj[u].iter()
            .filter(|&&(v, w)| d[v] != i64::MAX && w + d[v] == d[u])
            .map(|&(v, _)| v)
            .min()
            .unwrap();
        path.push(u as i64);
    }
    path
}""",
    },
    tests=_dij_tests(),
)


# ======================================================================== Max flow
def _mf_tests():
    t = [
        [4, [[0, 1, 3], [0, 2, 2], [1, 2, 5], [1, 3, 2], [2, 3, 3]], 0, 3],
        [2, [[0, 1, 7], [0, 1, 4]], 0, 1],
        [3, [[0, 1, 5]], 0, 2],
        [4, [[0, 1, 1000000], [0, 2, 1000000], [1, 2, 1], [1, 3, 1000000], [2, 3, 1000000]], 0, 3],
        [6, [[0, 1, 16], [0, 2, 13], [1, 2, 10], [2, 1, 4], [1, 3, 12], [3, 2, 9], [2, 4, 14], [4, 3, 7], [3, 5, 20], [4, 5, 4]], 0, 5],
        [3, [[0, 1, 4], [1, 0, 4], [1, 2, 3], [2, 1, 9]], 2, 0],
    ]
    for seed, n, m, c in [(1, 6, 15, 10), (2, 30, 150, 100), (3, 120, 1500, 10**6)]:
        r = _rng(1700 + seed)
        edges = []
        for _ in range(m):
            u, v = r.randrange(n), r.randrange(n)
            if u != v:
                edges.append([u, v, r.randint(1, c)])
        t.append([n, edges, 0, n - 1])
    return t


P_MAXFLOW = dict(
    id="max-flow-edmonds-karp",
    title="Maximum Flow (Edmonds–Karp)",
    difficulty=4,
    tags=["graph", "max flow", "bfs", "min cut"],
    fn="max_flow",
    params=[["n", "int"], ["edges", "int[][]"], ["source", "int"], ["sink", "int"]],
    returns="int",
    espresso=False,
    statement=r"""
A network has `n` nodes and directed pipes `edges[i] = [u, v, capacity]`: up to `capacity`
units per second can flow from `u` to `v`. Parallel pipes and pipes in both directions
between the same pair may exist.

Return the **maximum flow** from `source` to `sink`: the largest total rate that can leave
the source, respecting every capacity, with flow conserved at every other node (in = out).
""",
    constraints=["2 ≤ n ≤ 120", "0 ≤ len(edges) ≤ 1500", "1 ≤ capacity ≤ 10⁶", "source ≠ sink"],
    example_notes=["Send 2 along `0→1→3`, 2 along `0→2→3`, and 1 along `0→1→2→3`: total 5, which equals the cut `{0}` vs rest (3 + 2).",
                   "Parallel pipes add up."],
    hints=[
        "Repeatedly find a path from source to sink with spare capacity and push as much as its tightest edge allows. Why can a greedy choice get stuck?",
        "Allow 'undoing' flow: every edge `u→v` carrying `f` units gives a **residual** edge `v→u` with capacity `f`. Search for augmenting paths in this residual graph.",
        "Edmonds–Karp: find each augmenting path with **BFS** (fewest edges). Store edges in pairs so the reverse of edge `e` is `e ^ 1`; augment by the bottleneck, subtract on `e`, add on `e ^ 1`.",
    ],
    explanation=r"""
## Intuition

Pushing flow along any path with room left (an *augmenting path*) is the obvious greedy
idea, and it can get stuck: an early path may use an edge in a way that blocks better
routes. The fix is to let later paths **cancel** earlier decisions. For every unit sent
along `u → v`, add capacity to a *residual* reverse edge `v → u`; a later path that uses
`v → u` is effectively rerouting that unit. With residual edges, "no augmenting path left"
**guarantees** optimality (Ford–Fulkerson).

**Max-flow min-cut theorem**: the maximum flow equals the minimum total capacity of edges
you must cut to separate source from sink. When the algorithm stops, the nodes reachable
from the source in the residual graph form exactly such a minimum cut.

## Approach (Edmonds–Karp)

Edge list representation: edge `e` goes to `to[e]` with remaining capacity `cap[e]`; it is
created together with its reverse `e ^ 1` (capacity 0). Then:

1. BFS from `source` in the residual graph (edges with `cap > 0`), remembering the edge
   used to reach each node.
2. If `sink` was not reached, stop: the current flow is maximum.
3. Walk back from `sink` to find the bottleneck `b` (minimum `cap` on the path).
4. For every edge `e` on the path: `cap[e] -= b`, `cap[e ^ 1] += b`. Add `b` to the flow.

Trace on example 1 (edges `0→1:3, 0→2:2, 1→2:5, 1→3:2, 2→3:3`):

| BFS path | bottleneck | total |
|---|---|---|
| 0→1→3 | 2 | 2 |
| 0→2→3 | 2 | 4 |
| 0→1→2→3 | min(1, 5, 1) = 1 | 5 |
| none (0's edges are saturated) | | **5** |

## Complexity

* **Time:** O(V · E²). BFS picks the *shortest* augmenting path, which guarantees at most
  O(V·E) augmentations, each costing O(E). With plain DFS (Ford–Fulkerson) the number of
  augmentations can be proportional to the flow value: 2·10⁶ in example 4!
* **Space:** O(V + E).

## Common mistakes

* **Forgetting residual edges**: then greedy paths get stuck below the optimum.
* **Merging antiparallel edges** `u→v` and `v→u` into one capacity: keep them as separate
  edge pairs (the `e ^ 1` scheme handles this automatically).
* Using an adjacency matrix with `cap[u][v] = c` for parallel edges overwrites instead of adding.
* Overflow: total flow can exceed 2³¹ with large capacities (64-bit ints here).

## Going further

* **Dinic's algorithm**: BFS levels + blocking flow by DFS, O(V²·E), much faster in practice;
  O(E·√V) on unit-capacity bipartite graphs (**Hopcroft–Karp** matching).
* **Bipartite matching**: source → left nodes → right nodes → sink, all capacity 1.
* **Min-cost max-flow** replaces BFS with shortest paths by cost (Bellman–Ford/SPFA or Dijkstra with potentials).
""",
    solution=r'''def max_flow(n, edges, source, sink):
    # Edge-list residual graph. Edge e and its reverse are stored at e and e ^ 1
    # (they are appended in pairs, so pairs are (0,1), (2,3), ...).
    to, cap = [], []
    adj = [[] for _ in range(n)]
    for u, v, c in edges:
        adj[u].append(len(to)); to.append(v); cap.append(c)    # forward: capacity c
        adj[v].append(len(to)); to.append(u); cap.append(0)    # residual: starts empty

    flow = 0
    while True:
        # BFS for the SHORTEST augmenting path (this is what makes it Edmonds-Karp).
        via = [-1] * n               # via[x] = edge used to reach x
        via[source] = -2             # mark source as visited
        q = deque([source])
        while q and via[sink] == -1:
            u = q.popleft()
            for e in adj[u]:
                if cap[e] > 0 and via[to[e]] == -1:
                    via[to[e]] = e
                    q.append(to[e])
        if via[sink] == -1:
            return flow              # no augmenting path: flow is maximum (= min cut)

        # Bottleneck along the path, walking back from the sink.
        b = float("inf")
        x = sink
        while x != source:
            e = via[x]
            b = min(b, cap[e])
            x = to[e ^ 1]            # the reverse edge points back to the previous node
        # Push b units: use up forward capacity, create the same amount of "undo" room.
        x = sink
        while x != source:
            e = via[x]
            cap[e] -= b
            cap[e ^ 1] += b
            x = to[e ^ 1]
        flow += b
''',
    refs={
        "c": r"""// Residual graph as an edge list in the classic C style: edge e and its reverse
// are stored at e and e^1 (indices 2i and 2i+1), so "the other direction" is a
// single XOR. head[u] / nxt[e] form a linked list of the edges leaving u.
long long max_flow(long long n, long long** edges, int edgesSize, int* edgesColSize,
                   long long source, long long sink) {
    (void)edgesColSize;
    int N = (int)n, M = 2 * edgesSize;
    int* to = malloc(sizeof(int) * (size_t)(M + 1));
    int* nxt = malloc(sizeof(int) * (size_t)(M + 1));
    long long* cap = malloc(sizeof(long long) * (size_t)(M + 1));
    int* head = malloc(sizeof(int) * (size_t)N);
    for (int u = 0; u < N; u++) head[u] = -1;
    for (int i = 0; i < edgesSize; i++) {
        int u = (int)edges[i][0], v = (int)edges[i][1];
        int e = 2 * i;
        to[e] = v;     cap[e] = edges[i][2]; nxt[e] = head[u];     head[u] = e;
        to[e + 1] = u; cap[e + 1] = 0;       nxt[e + 1] = head[v]; head[v] = e + 1;
    }

    int* via = malloc(sizeof(int) * (size_t)N);    // edge used to reach each node
    int* queue = malloc(sizeof(int) * (size_t)N);
    long long flow = 0;
    for (;;) {
        // BFS finds the SHORTEST augmenting path (fewest edges). That choice is
        // what bounds Edmonds-Karp to O(V·E) augmentations.
        for (int u = 0; u < N; u++) via[u] = -1;
        via[source] = -2;                          // "visited, no incoming edge"
        int qh = 0, qt = 0;
        queue[qt++] = (int)source;
        while (qh < qt && via[sink] == -1) {
            int u = queue[qh++];
            for (int e = head[u]; e != -1; e = nxt[e])
                if (cap[e] > 0 && via[to[e]] == -1) { via[to[e]] = e; queue[qt++] = to[e]; }
        }
        if (via[sink] == -1) break;                // no path left: flow is maximum

        long long b = LLONG_MAX;                   // bottleneck along the path
        for (int x = (int)sink; x != source; x = to[via[x] ^ 1])
            if (cap[via[x]] < b) b = cap[via[x]];
        for (int x = (int)sink; x != source; x = to[via[x] ^ 1]) {
            cap[via[x]] -= b;                      // use forward capacity
            cap[via[x] ^ 1] += b;                  // allow undoing it later
        }
        flow += b;
    }
    free(to); free(nxt); free(cap); free(head); free(via); free(queue);
    return flow;
}""",
        "cpp": r"""long long maxFlow(long long n, vector<vector<long long>>& edges, long long source, long long sink) {
    vector<int> to; vector<long long> cap; vector<vector<int>> adj(n);
    for (auto& e : edges) {
        adj[e[0]].push_back(to.size()); to.push_back(e[1]); cap.push_back(e[2]);
        adj[e[1]].push_back(to.size()); to.push_back(e[0]); cap.push_back(0);
    }
    long long flow = 0;
    while (true) {
        vector<int> via(n, -1);
        via[source] = -2;
        queue<int> q; q.push(source);
        while (!q.empty() && via[sink] == -1) {
            int u = q.front(); q.pop();
            for (int e : adj[u]) if (cap[e] > 0 && via[to[e]] == -1) { via[to[e]] = e; q.push(to[e]); }
        }
        if (via[sink] == -1) return flow;
        long long b = LLONG_MAX;
        for (int x = sink; x != source; x = to[via[x] ^ 1]) b = min(b, cap[via[x]]);
        for (int x = sink; x != source; x = to[via[x] ^ 1]) { cap[via[x]] -= b; cap[via[x] ^ 1] += b; }
        flow += b;
    }
}""",
        "rust": r"""use std::collections::VecDeque;

pub fn max_flow(n: i64, edges: Vec<Vec<i64>>, source: i64, sink: i64) -> i64 {
    let n = n as usize;
    let (s, t) = (source as usize, sink as usize);
    let mut to: Vec<usize> = Vec::new();
    let mut cap: Vec<i64> = Vec::new();
    let mut adj: Vec<Vec<usize>> = vec![Vec::new(); n];
    for e in &edges {
        let (u, v) = (e[0] as usize, e[1] as usize);
        adj[u].push(to.len()); to.push(v); cap.push(e[2]);
        adj[v].push(to.len()); to.push(u); cap.push(0);
    }
    let mut flow = 0;
    loop {
        // via[x] = Some(edge) used to reach x
        let mut via: Vec<Option<usize>> = vec![None; n];
        let mut seen = vec![false; n];
        seen[s] = true;
        let mut q = VecDeque::from([s]);
        while let Some(u) = q.pop_front() {
            if seen[t] { break; }
            for &e in &adj[u] {
                if cap[e] > 0 && !seen[to[e]] {
                    seen[to[e]] = true;
                    via[to[e]] = Some(e);
                    q.push_back(to[e]);
                }
            }
        }
        if !seen[t] {
            return flow;
        }
        let mut b = i64::MAX;
        let mut x = t;
        while x != s {
            let e = via[x].unwrap();
            b = b.min(cap[e]);
            x = to[e ^ 1];
        }
        x = t;
        while x != s {
            let e = via[x].unwrap();
            cap[e] -= b;
            cap[e ^ 1] += b;
            x = to[e ^ 1];
        }
        flow += b;
    }
}""",
    },
    tests=_mf_tests(),
)


# ======================================================================== Median finder
def _mfind_tests():
    def gen(seed, nops, lo, hi):
        r = _rng(seed)
        ops, args = ["addNum"], [r.randint(lo, hi)]
        for _ in range(nops - 1):
            if r.random() < 0.6:
                ops.append("addNum")
                args.append(r.randint(lo, hi))
            else:
                ops.append("findMedian")
                args.append(0)
        return [ops, args]

    return [
        [["addNum", "addNum", "findMedian", "addNum", "findMedian"], [1, 2, 0, 3, 0]],
        [["addNum", "findMedian"], [-7, 0]],
        [["addNum", "addNum", "addNum", "addNum", "findMedian", "findMedian"], [5, 5, 5, 5, 0, 0]],
        [["addNum", "findMedian", "addNum", "findMedian", "addNum", "findMedian", "addNum", "findMedian"],
         [6, 0, 10, 0, 2, 0, 6, 0]],
        [["addNum", "addNum", "findMedian"], [2147483647, 2147483646, 0]],
        [["addNum", "addNum", "findMedian"], [-1, -2, 0]],
        gen(1711, 50, 0, 5),
        gen(1712, 700, -10**6, 10**6),
    ]


P_MEDIANFINDER = dict(
    id="median-finder-two-heaps",
    title="Find Median from Data Stream",
    difficulty=3,
    tags=["heap", "design", "two heaps"],
    fn="median_finder",
    params=[["ops", "str[]"], ["args", "int[]"]],
    returns="float[]",
    statement=r"""
Design a `MedianFinder` that supports:

* `addNum(x)`: add the integer `x` to the data structure.
* `findMedian()`: return the median of all numbers added so far (the middle value, or the
  average of the two middle values when the count is even).

`ops[i]` is `"addNum"` or `"findMedian"`; for `addNum`, `args[i]` is the number to add (for
`findMedian` it is `0` and ignored). Return the results of the `findMedian` calls in order.
`findMedian` is only called after at least one `addNum`.

Aim for O(log n) per `addNum` and O(1) per `findMedian`.
""",
    constraints=["1 ≤ len(ops) ≤ 700", "-2³¹ ≤ x ≤ 2³¹ − 1"],
    example_notes=["After `1, 2` the median is `1.5`; after `1, 2, 3` it is `2`.",
                   "A single number is its own median."],
    hints=[
        "Keeping a sorted list makes `findMedian` O(1) but each insert O(n). You only ever need the *middle*, not full order.",
        "Split the numbers into a lower half and an upper half. Which element of each half do you need to see?",
        "Max-heap for the lower half, min-heap for the upper half, sizes equal or the lower one bigger by one. Insert via `lo`, move `lo`'s max to `hi`, then move `hi`'s min back if `hi` got bigger.",
    ],
    explanation=r"""
## Intuition

The median only depends on the boundary between the smaller half and the larger half.
Keep each half in a heap oriented towards that boundary:

```text
    lo: max-heap           hi: min-heap
  [ 1  2  5  6 ]  ← 6 | 10 →  [ 10  14  20 ]
```

* odd count: `lo` holds one extra, median = `max(lo)`;
* even count: median = `(max(lo) + min(hi)) / 2`.

## Approach

**The class:**

```python
class MedianFinder:
    def __init__(self):
        self.lo = []   # max-heap (store negatives)
        self.hi = []   # min-heap
    def add_num(self, x):
        heappush(self.lo, -x)                         # 1. tentatively into lower half
        heappush(self.hi, -heappop(self.lo))          # 2. its max goes up: order fixed
        if len(self.hi) > len(self.lo):               # 3. sizes: lo may have one extra
            heappush(self.lo, -heappop(self.hi))
    def find_median(self):
        if len(self.lo) > len(self.hi):
            return float(-self.lo[0])
        return (-self.lo[0] + self.hi[0]) / 2
```

Steps 1–2 guarantee every element of `lo` ≤ every element of `hi` without comparing
anything explicitly; step 3 restores the size invariant.

Trace for `6, 10, 2, 6`:

| add | lo | hi | median |
|---|---|---|---|
| 6 | {6} | {} | 6 |
| 10 | {6} | {10} | 8 |
| 2 | {2, 6} | {10} | 6 |
| 6 | {2, 6} | {6, 10} | 6 |

## Complexity

* **addNum:** O(log n), a constant number of heap operations.
* **findMedian:** O(1), peek at the tops.
* **Space:** O(n).

## Common mistakes

* **Integer division** for the even case (`(1 + 2) / 2` must be `1.5`; in C/C++ use `/ 2.0`).
* **Overflow** when averaging two values near 2³¹ in 32-bit arithmetic.
* Python's `heapq` is a min-heap only: forgetting to negate on *both* push and pop for `lo`.
* Letting the sizes drift by more than one.

## Going further

* If all numbers are in `0..100`, a counting array answers in O(100), no heaps needed.
  If 99% are in that range, keep counts for it and handle outliers separately.
* With deletions, you need lazy deletion or ordered multisets: see **Sliding Window Median**.
* Percentiles other than 50%: keep `lo` at size `⌈p·n⌉` instead of `⌈n/2⌉`.
""",
    solution=r'''def median_finder(ops, args):
    lo = []                          # lower half as a MAX-heap (store -x)
    hi = []                          # upper half as a min-heap
    out = []
    for op, x in zip(ops, args):
        if op == "addNum":
            # Route x through lo and then hi: whatever ends up on hi is >= all of lo,
            # so the halves stay ordered without explicit comparisons.
            heappush(lo, -x)
            heappush(hi, -heappop(lo))
            # Size invariant: len(lo) == len(hi) or len(lo) == len(hi) + 1.
            if len(hi) > len(lo):
                heappush(lo, -heappop(hi))
        else:  # "findMedian"
            if len(lo) > len(hi):
                out.append(float(-lo[0]))          # odd count: max of lower half
            else:
                out.append((-lo[0] + hi[0]) / 2)   # even: average of the two middles
    return out
''',
    refs={
        "c": r"""// C has no priority_queue, so we write the one heap we need: a binary MAX-heap
// stored in an array (children of i are 2i+1 and 2i+2).
// The upper half needs a MIN-heap; we get one for free by storing negated values
// in a max-heap (values fit in 32 bits, so negating a long long is safe).
typedef struct { long long* a; int n; } Heap;

static void heap_push(Heap* h, long long x) {
    int i = h->n++;
    h->a[i] = x;
    while (i > 0) {                         // sift up while bigger than the parent
        int p = (i - 1) / 2;
        if (h->a[p] >= h->a[i]) break;
        long long tmp = h->a[p]; h->a[p] = h->a[i]; h->a[i] = tmp;
        i = p;
    }
}

static long long heap_pop(Heap* h) {
    long long top = h->a[0];
    h->a[0] = h->a[--h->n];                 // move the last leaf to the root...
    int i = 0;
    for (;;) {                              // ...and sift it down
        int l = 2 * i + 1, r = l + 1, m = i;
        if (l < h->n && h->a[l] > h->a[m]) m = l;
        if (r < h->n && h->a[r] > h->a[m]) m = r;
        if (m == i) break;
        long long tmp = h->a[m]; h->a[m] = h->a[i]; h->a[i] = tmp;
        i = m;
    }
    return top;
}

double* median_finder(char** ops, int opsSize, long long* args, int argsSize, int* returnSize) {
    (void)argsSize;
    // lo = max-heap of the smaller half, hi = max-heap of NEGATED larger half.
    // Invariant: lo.n == hi.n or lo.n == hi.n + 1, so the median is at the tops.
    Heap lo = { malloc(sizeof(long long) * (size_t)opsSize), 0 };
    Heap hi = { malloc(sizeof(long long) * (size_t)opsSize), 0 };
    double* out = malloc(sizeof(double) * (size_t)opsSize);
    int k = 0;
    for (int i = 0; i < opsSize; i++) {
        if (strcmp(ops[i], "addNum") == 0) {
            // Route through lo so the largest of the small half moves up to hi,
            // then rebalance sizes. Two pushes and a pop or two: O(log n).
            heap_push(&lo, args[i]);
            heap_push(&hi, -heap_pop(&lo));
            if (hi.n > lo.n) heap_push(&lo, -heap_pop(&hi));
        } else if (lo.n > hi.n) {
            out[k++] = (double)lo.a[0];                       // odd count: middle
        } else {
            // Average in double: the sum of two 32-bit values could overflow an int.
            out[k++] = ((double)lo.a[0] + (double)(-hi.a[0])) / 2.0;
        }
    }
    free(lo.a);
    free(hi.a);
    *returnSize = k;
    return out;
}""",
        "cpp": r"""class MedianFinder {
    priority_queue<long long> lo;                                     // max-heap
    priority_queue<long long, vector<long long>, greater<long long>> hi;  // min-heap
public:
    void addNum(long long x) {
        lo.push(x);
        hi.push(lo.top()); lo.pop();
        if (hi.size() > lo.size()) { lo.push(hi.top()); hi.pop(); }
    }
    double findMedian() const {
        if (lo.size() > hi.size()) return (double)lo.top();
        return ((double)lo.top() + (double)hi.top()) / 2.0;   // doubles: no int overflow
    }
};

vector<double> medianFinder(vector<string>& ops, vector<long long>& args) {
    MedianFinder mf;
    vector<double> out;
    for (size_t i = 0; i < ops.size(); i++) {
        if (ops[i] == "addNum") mf.addNum(args[i]);
        else out.push_back(mf.findMedian());
    }
    return out;
}""",
        "rust": r"""use std::cmp::Reverse;
use std::collections::BinaryHeap;

struct MedianFinder {
    lo: BinaryHeap<i64>,          // max-heap: lower half
    hi: BinaryHeap<Reverse<i64>>, // min-heap: upper half
}

impl MedianFinder {
    fn new() -> Self {
        MedianFinder { lo: BinaryHeap::new(), hi: BinaryHeap::new() }
    }
    fn add_num(&mut self, x: i64) {
        self.lo.push(x);
        let top = self.lo.pop().unwrap();
        self.hi.push(Reverse(top));
        if self.hi.len() > self.lo.len() {
            let Reverse(m) = self.hi.pop().unwrap();
            self.lo.push(m);
        }
    }
    fn find_median(&self) -> f64 {
        let a = *self.lo.peek().unwrap() as f64;
        if self.lo.len() > self.hi.len() {
            a
        } else {
            (a + self.hi.peek().unwrap().0 as f64) / 2.0
        }
    }
}

pub fn median_finder(ops: Vec<String>, args: Vec<i64>) -> Vec<f64> {
    let mut mf = MedianFinder::new();
    let mut out = Vec::new();
    for (op, &x) in ops.iter().zip(args.iter()) {
        if op == "addNum" {
            mf.add_num(x);
        } else {
            out.push(mf.find_median());
        }
    }
    out
}""",
    },
    tests=_mfind_tests(),
)


PROBLEMS = [
    P_TRIE,
    P_MEDIANFINDER,
    P_SEGTREE,
    P_FENWICK,
    P_KMP,
    P_DNA,
    P_DIJKSTRA,
    P_WORDSEARCH,
    P_LIS,
    P_SWMEDIAN,
    P_TSP,
    P_MAXFLOW,
]
