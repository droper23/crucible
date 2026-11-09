"""Track 12: Graphs."""
import heapq
import random

TRACK = dict(
    id="graphs",
    title="Graphs",
    order=12,
    icon="🕸",
    blurb="Grids, BFS and DFS, topological order, union-find and shortest paths.",
    intro=r"""
A **graph** is a set of *vertices* (nodes) joined by *edges*. Edges may be **directed**
(`u → v`, like "course `b` must come before course `a`") or **undirected** (a road), and
may carry a **weight** (a distance, a price). Trees are graphs without cycles; this track
drops that restriction, so you must remember where you have been.

## Representations

Problems here give you a graph in one of two shapes:

- **`n` plus an edge list**, e.g. `n = 4, edges = [[0,1],[1,2],[2,0],[2,3]]`.
- **A grid**, where each cell is a vertex and its 4 (or 8) neighbours are the edges.

```text
   0 --- 1          adjacency LIST                adjacency MATRIX
    \   /           0: [1, 2]                         0 1 2 3
     \ /            1: [0, 2]                     0 [ . 1 1 . ]
      2 --- 3       2: [1, 0, 3]                  1 [ 1 . 1 . ]
                    3: [2]                        2 [ 1 1 . 1 ]
                                                  3 [ . . 1 . ]
```

| | adjacency list | adjacency matrix |
|---|---|---|
| memory | O(V + E) | O(V²) |
| iterate neighbours of u | O(deg u) | O(V) |
| "is there an edge u–v?" | O(deg u) | O(1) |

Almost always build an **adjacency list** first:

```python
adj = [[] for _ in range(n)]
for u, v in edges:
    adj[u].append(v)
    adj[v].append(u)        # omit for a directed graph
```

In C++ that is `vector<vector<int>> adj(n)`, in Rust `vec![Vec::new(); n]`. For a grid
you do not build anything: the neighbours of `(r, c)` are `(r±1, c)` and `(r, c±1)`,
filtered by bounds.

## BFS and DFS

Both explore everything reachable from a start vertex, marking vertices **visited** so
that cycles do not loop forever. They differ in the order:

```text
graph:  A - B - D        BFS from A (queue):        DFS from A (stack/recursion):
        |   |            pop A  push B C            visit A -> B -> D -> E -> C?
        C - E            pop B  push D E                 (goes deep first, backs up
                         pop C  (E already seen)          only when stuck)
                         pop D, pop E               order: A B D E C   (one possibility)
order by distance:       A | B C | D E
```

- **BFS** (queue) visits vertices in order of distance (number of edges) from the start.
  On an **unweighted** graph, the first time BFS reaches a vertex is along a shortest
  path. Use it for "minimum number of steps" (rotting oranges, word ladder, maze).
- **DFS** (recursion or a stack) goes deep first. Use it for reachability, counting
  components, cycle detection, and anything that needs discovery/finish times (bridges).

Mark a vertex visited **when you push it**, not when you pop it; otherwise the same
vertex can enter the queue many times. For grids, a common trick is to overwrite the
cell (`'1'` → `'0'`) instead of keeping a separate visited set. Deep recursive DFS on a
large grid can overflow the stack; an explicit stack avoids that.

## Topological sort

A **DAG** (directed acyclic graph) can be ordered so every edge points forward. Kahn's
algorithm:

1. Count each vertex's **in-degree** (incoming edges).
2. Put every vertex with in-degree 0 in a queue.
3. Pop `u`, append it to the order, and decrement the in-degree of each `u → v`; when
   one reaches 0, push it.
4. If the order has fewer than `n` vertices, the leftovers lie on a **cycle**.

Use a **min-heap** instead of a queue and you get the *lexicographically smallest*
topological order.

## Union-find (disjoint set union)

Keeps a partition of `0..n-1` into groups, with near-O(1) `find(x)` (which group?) and
`union(a, b)` (merge groups):

```python
parent = list(range(n))
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]   # path halving: flatten as we climb
        x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra == rb: return False           # already connected: this edge closes a cycle
    parent[ra] = rb
    return True
```

Perfect for "how many components", "which edge creates a cycle", and Kruskal's MST.
Adding union by size/rank makes it effectively O(α(n)) per operation.

## Dijkstra: shortest paths with weights

BFS fails once edges have different (non-negative) weights. Dijkstra always expands the
**closest unfinished** vertex, which needs a **priority queue** (min-heap) keyed by
distance:

```python
dist = [inf] * n; dist[src] = 0
pq = [(0, src)]
while pq:
    d, u = heappop(pq)
    if d > dist[u]: continue          # stale entry: u was already finalised
    for v, w in adj[u]:
        if d + w < dist[v]:
            dist[v] = d + w
            heappush(pq, (dist[v], v))
```

That is O((V + E) log V). Getting a min-heap in each language:

- **Python**: `heapq` on a plain list is a min-heap; push tuples `(dist, node)`.
- **C++**: `priority_queue` is a *max*-heap by default. Use
  `priority_queue<pair<long long,int>, vector<pair<long long,int>>, greater<>>`.
- **Rust**: `BinaryHeap` is a max-heap too; wrap entries in `std::cmp::Reverse`:
  `heap.push(Reverse((d, u)))` and `while let Some(Reverse((d, u))) = heap.pop()`.
- **C**: no library heap. Write a tiny array-based one: push = append and *sift up*
  (swap with parent `(i-1)/2` while smaller), pop = move the last element to the root and
  *sift down* (swap with the smaller child `2i+1`/`2i+2`).

```c
typedef struct { long long d; int v; } Item;
static void push(Item* h, int* n, Item x) {
    int i = (*n)++;
    while (i > 0 && h[(i - 1) / 2].d > x.d) { h[i] = h[(i - 1) / 2]; i = (i - 1) / 2; }
    h[i] = x;
}
```

Every answer in this track is made unique by the statement (sorted output,
lexicographically smallest order, or a single number), so read the tie-breaking rules.
""",
)

_R = random.Random(1212)
D4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def _grid(rng, rows, cols, p):
    return [[1 if rng.random() < p else 0 for _ in range(cols)] for _ in range(rows)]


def _strgrid(g):
    return ["".join("1" if x else "0" for x in row) for row in g]


PROBLEMS = []

# ---------------------------------------------------------------- 1. islands

PROBLEMS.append(dict(
    id="grid-number-of-islands",
    title="Number of Islands",
    difficulty=2,
    tags=["graph", "grid", "dfs", "bfs"],
    fn="num_islands",
    params=[["grid", "str[]"]],
    returns="int",
    statement=r"""
A map is given as a list of equal-length strings where `'1'` is land and `'0'` is water.
An **island** is a maximal group of land cells connected **horizontally or vertically**
(not diagonally). Everything outside the grid is water. Return the number of islands.
""",
    constraints=["1 ≤ rows, cols ≤ 120", "each character is '0' or '1'"],
    example_notes=[
        "One big island in the top-left plus nothing else.",
        "Three separate islands: top-left block, the middle cell, and the bottom-right pair.",
    ],
    hints=[
        "Treat each land cell as a vertex with edges to its land neighbours. What are you counting, in graph terms?",
        "Scan the grid. Whenever you find land that has not been visited yet, you have found a new island.",
        "From that cell, flood the whole island (DFS or BFS) marking every cell visited, so it is never counted again.",
    ],
    explanation=r"""
## Intuition

Islands are **connected components** of the grid graph whose vertices are land cells.
Counting components is a classic pattern: iterate over every vertex; each time you meet
one that is not yet visited, increment the count and visit its entire component.

## Approach

1. Copy the grid into a mutable form (strings are immutable in Python and Rust).
2. For every cell `(r, c)` that is `'1'`:
   - `count += 1`;
   - flood fill from it: push it on a stack, set it to `'0'` (visited), then repeatedly
     pop a cell and push each in-bounds `'1'` neighbour, marking it `'0'` as you push.
3. Return `count`.

```text
1 1 0 0 0        scan hits (0,0): island #1, flood sinks (0,0),(0,1),(1,0),(1,1)
1 1 0 0 0        scan hits (2,2): island #2, flood sinks just (2,2)
0 0 1 0 0        scan hits (3,3): island #3, flood sinks (3,3),(3,4)
0 0 0 1 1        every other '1' was already sunk -> answer 3
```

Sinking the land *is* the visited set, so no extra memory is needed beyond the copy.

## Complexity

- **Time O(R·C)**: each cell is pushed at most once and inspects 4 neighbours.
- **Space O(R·C)** worst case for the stack (a grid full of land), plus the copy.

## Common mistakes

- **Recursive DFS on a big grid**: a 120×120 grid of land is a 14,400-deep recursion,
  which exceeds Python's default limit and can blow a thread stack in other languages.
  Use an explicit stack or a queue.
- **Marking visited on pop instead of push**: a cell can be pushed several times by
  different neighbours; correct, but the stack can grow to many times the grid size.
- **Diagonals**: they do not connect islands here.
- **Bounds checks** in C/C++: test `0 <= nr < rows` *before* indexing.

## Going further

Union-find solves the same problem: union each land cell with its right and down land
neighbours and count roots. It shines in the follow-up *Number of Islands II*, where land
appears one cell at a time and you must report the count after each addition.
""",
    solution=r'''
def num_islands(grid):
    g = [list(row) for row in grid]    # strings are immutable: make a mutable copy
    rows, cols = len(g), len(g[0])
    count = 0
    for r in range(rows):
        for c in range(cols):
            if g[r][c] != '1':
                continue
            # Unvisited land: this starts a brand new island.
            count += 1
            # Sink the whole island with an explicit stack (no recursion limits).
            g[r][c] = '0'                  # mark on push, so nothing is pushed twice
            stack = [(r, c)]
            while stack:
                cr, cc = stack.pop()
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] == '1':
                        g[nr][nc] = '0'
                        stack.append((nr, nc))
    return count
''',
    refs={
        "cpp": r'''
long long numIslands(vector<string>& grid) {
    int R = grid.size(), C = grid[0].size();
    vector<string> g = grid;                         // work on a copy
    const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1};
    long long count = 0;
    vector<pair<int, int>> st;
    for (int r = 0; r < R; r++)
        for (int c = 0; c < C; c++) {
            if (g[r][c] != '1') continue;
            count++;                                 // new island
            g[r][c] = '0';
            st.push_back({r, c});
            while (!st.empty()) {
                auto [cr, cc] = st.back(); st.pop_back();
                for (int d = 0; d < 4; d++) {
                    int nr = cr + dr[d], nc = cc + dc[d];
                    if (nr >= 0 && nr < R && nc >= 0 && nc < C && g[nr][nc] == '1') {
                        g[nr][nc] = '0';
                        st.push_back({nr, nc});
                    }
                }
            }
        }
    return count;
}
''',
        "rust": r'''
pub fn num_islands(grid: Vec<String>) -> i64 {
    // Strings cannot be indexed by position in Rust: convert to byte rows.
    let mut g: Vec<Vec<u8>> = grid.iter().map(|s| s.as_bytes().to_vec()).collect();
    let (rows, cols) = (g.len() as i64, g[0].len() as i64);
    let mut count = 0;
    for r in 0..rows {
        for c in 0..cols {
            if g[r as usize][c as usize] != b'1' { continue; }
            count += 1;
            g[r as usize][c as usize] = b'0';
            let mut stack = vec![(r, c)];
            while let Some((cr, cc)) = stack.pop() {
                for (dr, dc) in [(1, 0), (-1, 0), (0, 1), (0, -1)] {
                    let (nr, nc) = (cr + dr, cc + dc);
                    if nr >= 0 && nr < rows && nc >= 0 && nc < cols
                        && g[nr as usize][nc as usize] == b'1' {
                        g[nr as usize][nc as usize] = b'0';
                        stack.push((nr, nc));
                    }
                }
            }
        }
    }
    count
}
''',
    },
    tests=[
        [["11110", "11010", "11000", "00000"]],
        [["11000", "11000", "00100", "00011"]],
        [["0"]], [["1"]], [["101", "010", "101"]],
        [["1" * 40] * 3], [["10" * 20, "01" * 20]],
        [_strgrid(_grid(_R, 20, 30, 0.45))],
        [_strgrid(_grid(_R, 120, 120, 0.55))],
        [_strgrid([[1] * 120 for _ in range(120)])],
    ],
))

# ---------------------------------------------------------------- 2. flood fill

PROBLEMS.append(dict(
    id="grid-flood-fill",
    title="Flood Fill",
    difficulty=2,
    tags=["graph", "grid", "bfs", "dfs"],
    fn="flood_fill",
    params=[["image", "int[][]"], ["sr", "int"], ["sc", "int"], ["color", "int"]],
    returns="int[][]",
    statement=r"""
An image is a grid of integer colours. Perform the "paint bucket" operation at pixel
`(sr, sc)`: that pixel, and every pixel connected to it **4-directionally** through
pixels of the **same original colour**, is repainted with `color`. Return the resulting
image.
""",
    constraints=["1 ≤ rows, cols ≤ 50", "0 ≤ colours ≤ 2¹⁶", "(sr, sc) is inside the image"],
    example_notes=[
        "The 1s connected to the centre turn into 2; the bottom-right 1 is cut off by 0s and stays.",
        "The new colour equals the old one: nothing changes.",
    ],
    hints=[
        "Which pixels change? Exactly those reachable from the start through pixels with the start's original colour.",
        "BFS or DFS from (sr, sc), moving only into neighbours whose colour equals the original.",
        "Beware: if `color` equals the original colour, painting does not mark anything as visited.",
    ],
    explanation=r"""
## Intuition

The paint bucket recolours the **connected component** of the start pixel in the graph
where neighbours with equal colour are joined. Painting a pixel conveniently doubles as
marking it visited: once it has the new colour, it no longer matches the old one, so no
one will push it again.

## Approach

1. `old = image[sr][sc]`. If `old == color`, return the image unchanged (see mistakes).
2. Paint the start and push it on a queue.
3. Pop a pixel; for each in-bounds neighbour with colour `old`, paint it and push it.

```text
1 1 1        old = 1, start (1,1)       2 2 2
1 1 0   ->   BFS order: (1,1) (0,1)     2 2 0
1 0 1        (1,0) (0,0) (0,2) ...      2 0 1    <- (2,2) is not connected
```

## Complexity

- **Time O(R·C)**: each pixel is painted (and pushed) at most once.
- **Space O(R·C)** for the queue in the worst case.

## Common mistakes

- **`color == old`**: painting no longer acts as a visited mark, so the search revisits
  pixels forever (infinite loop or stack overflow). Return early.
- **Comparing with the start pixel's *current* colour** after painting it, instead of the
  saved `old`.
- **Recursion depth**: a 100×100 single-colour image means a 10,000-deep recursive DFS.
  Use a queue or an explicit stack.
- **C++/Rust**: the parameter is your copy of the image (C++ takes it by reference, so you
  may modify and return it).

## Going further

"Paint the border of a component", "count enclosed regions" (*Surrounded Regions*: flood
from the border, everything not reached is enclosed) and *Number of Islands* are all the
same traversal with a different action at each pixel.
""",
    solution=r'''
def flood_fill(image, sr, sc, color):
    old = image[sr][sc]
    # If nothing would change, stop now: painting would not mark pixels as
    # visited (they would still match `old`) and the search would never end.
    if old == color:
        return image
    rows, cols = len(image), len(image[0])
    image[sr][sc] = color             # painting a pixel = marking it visited
    queue = deque([(sr, sc)])
    while queue:
        r, c = queue.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and image[nr][nc] == old:
                image[nr][nc] = color
                queue.append((nr, nc))
    return image
''',
    refs={
        "cpp": r'''
vector<vector<long long>> floodFill(vector<vector<long long>>& image, long long sr, long long sc, long long color) {
    long long old = image[sr][sc];
    if (old == color) return image;                 // nothing to do (and avoids looping)
    int R = image.size(), C = image[0].size();
    const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1};
    queue<pair<int, int>> q;
    image[sr][sc] = color;
    q.push({(int)sr, (int)sc});
    while (!q.empty()) {
        auto [r, c] = q.front(); q.pop();
        for (int d = 0; d < 4; d++) {
            int nr = r + dr[d], nc = c + dc[d];
            if (nr >= 0 && nr < R && nc >= 0 && nc < C && image[nr][nc] == old) {
                image[nr][nc] = color;
                q.push({nr, nc});
            }
        }
    }
    return image;
}
''',
        "rust": r'''
use std::collections::VecDeque;

pub fn flood_fill(image: Vec<Vec<i64>>, sr: i64, sc: i64, color: i64) -> Vec<Vec<i64>> {
    let mut img = image;                             // take ownership; we may mutate it
    let old = img[sr as usize][sc as usize];
    if old == color { return img; }
    let (rows, cols) = (img.len() as i64, img[0].len() as i64);
    img[sr as usize][sc as usize] = color;
    let mut q = VecDeque::from(vec![(sr, sc)]);
    while let Some((r, c)) = q.pop_front() {
        for (dr, dc) in [(1, 0), (-1, 0), (0, 1), (0, -1)] {
            let (nr, nc) = (r + dr, c + dc);
            if nr >= 0 && nr < rows && nc >= 0 && nc < cols && img[nr as usize][nc as usize] == old {
                img[nr as usize][nc as usize] = color;
                q.push_back((nr, nc));
            }
        }
    }
    img
}
''',
    },
    tests=[
        [[[1, 1, 1], [1, 1, 0], [1, 0, 1]], 1, 1, 2],
        [[[0, 0, 0], [0, 0, 0]], 0, 0, 0],
        [[[5]], 0, 0, 9], [[[0, 1], [1, 0]], 0, 1, 3],
        [[[1, 2, 1], [2, 1, 2], [1, 2, 1]], 1, 1, 7],
        [[[_R.randint(0, 2) for _ in range(15)] for _ in range(10)], 4, 7, 9],
        [[[0] * 50 for _ in range(50)], 25, 25, 65536],
        [[[_R.randint(0, 1) for _ in range(45)] for _ in range(45)], 22, 22, 2],
    ],
))

# ---------------------------------------------------------------- 3. max area

PROBLEMS.append(dict(
    id="grid-max-area-of-island",
    title="Max Area of Island",
    difficulty=2,
    tags=["graph", "grid", "dfs"],
    fn="max_area_of_island",
    params=[["grid", "int[][]"]],
    returns="int",
    statement=r"""
`grid` contains `1` (land) and `0` (water). An island is a group of land cells connected
4-directionally; its **area** is its number of cells. Return the largest island's area,
or `0` if there is no land.
""",
    constraints=["1 ≤ rows, cols ≤ 30", "grid[r][c] ∈ {0, 1}"],
    example_notes=[
        "The island on the right side has 6 cells; no other island is larger.",
        "No land at all.",
    ],
    hints=[
        "This is Number of Islands, but each flood fill must report how many cells it covered.",
        "Make the DFS return a count: 0 for water / out of bounds, otherwise 1 + the counts of the four neighbours.",
        "Set a cell to 0 before recursing into its neighbours so it is never counted twice.",
    ],
    explanation=r"""
## Intuition

Same components as in *Number of Islands*; now we want the size of the biggest one.
A recursive DFS can **return the size** of what it explores: the area of the island
through a land cell is 1 plus the areas reached from its four neighbours, provided we
sink each cell as soon as we count it.

## Approach

```text
area(r, c):
  out of bounds or grid[r][c] == 0 -> 0
  grid[r][c] = 0                   # sink: never counted again
  return 1 + area(r+1,c) + area(r-1,c) + area(r,c+1) + area(r,c-1)
```

Call `area` from every cell and keep the maximum (water cells return 0 immediately).

```text
0 1 1          area(0,1): sink, 1 + area(0,2)[=1 + area(1,2)[=1]] + area(1,1)[=1]
0 1 1          ... total 4 for the top-right block; area(2,0) = 1
1 0 0          answer max(4, 1) = 4
```

Sinking *before* recursing is essential: otherwise `(0,1)` calls `(0,2)` which calls
`(0,1)` again, forever.

## Complexity

- **Time O(R·C)**: each cell is sunk once; each call does O(1) work besides recursing.
- **Space O(R·C)** recursion depth in the worst case (a snake-shaped island). Grids here
  are at most 30×30, so recursion is safe; for big grids use an explicit stack.

## Common mistakes

- **Marking visited after the recursive calls**: infinite mutual recursion.
- **Counting each island's area with a global counter but forgetting to reset it** for
  the next island.
- **ESPresso**: there is no `||`-style short-circuit trap here if you use `or`; put the
  bounds checks *before* the `grid[r][c]` access so you never index out of range.

## Going further

*Making a Large Island*: you may flip one `0` to `1`; what is the largest island now?
Label each island with an id and its area, then for every water cell sum the areas of
the distinct islands around it, plus one.
""",
    solution=r'''
def max_area_of_island(grid):
    rows, cols = len(grid), len(grid[0])

    def area(r, c):
        # Water and the outside world contribute nothing.
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] == 0:
            return 0
        # Sink the cell BEFORE exploring neighbours, so they cannot come back here.
        grid[r][c] = 0
        return 1 + area(r + 1, c) + area(r - 1, c) + area(r, c + 1) + area(r, c - 1)

    best = 0
    for r in range(rows):
        for c in range(cols):
            best = max(best, area(r, c))   # water cells simply return 0
    return best
''',
    refs={
        "cpp": r'''
static long long areaFrom(vector<vector<long long>>& g, int r, int c) {
    if (r < 0 || r >= (int)g.size() || c < 0 || c >= (int)g[0].size() || g[r][c] == 0) return 0;
    g[r][c] = 0;                                     // sink before recursing
    return 1 + areaFrom(g, r + 1, c) + areaFrom(g, r - 1, c) + areaFrom(g, r, c + 1) + areaFrom(g, r, c - 1);
}

long long maxAreaOfIsland(vector<vector<long long>>& grid) {
    long long best = 0;
    for (int r = 0; r < (int)grid.size(); r++)
        for (int c = 0; c < (int)grid[0].size(); c++)
            best = max(best, areaFrom(grid, r, c));
    return best;
}
''',
        "rust": r'''
fn area(g: &mut Vec<Vec<i64>>, r: i64, c: i64) -> i64 {
    if r < 0 || c < 0 || r >= g.len() as i64 || c >= g[0].len() as i64 { return 0; }
    let (ru, cu) = (r as usize, c as usize);
    if g[ru][cu] == 0 { return 0; }
    g[ru][cu] = 0;                                   // sink before recursing
    1 + area(g, r + 1, c) + area(g, r - 1, c) + area(g, r, c + 1) + area(g, r, c - 1)
}

pub fn max_area_of_island(grid: Vec<Vec<i64>>) -> i64 {
    let mut g = grid;
    let mut best = 0;
    for r in 0..g.len() {
        for c in 0..g[0].len() {
            best = best.max(area(&mut g, r as i64, c as i64));
        }
    }
    best
}
''',
        "espresso": r'''
// Returns the size of the island through (r, c), sinking it as it goes.
fn area(grid, r, c) {
  if r < 0 or c < 0 or r >= len(grid) or c >= len(grid[0]) { return 0 }
  if grid[r][c] != 1 { return 0 }
  grid[r][c] = 0
  return 1 + area(grid, r + 1, c) + area(grid, r - 1, c) + area(grid, r, c + 1) + area(grid, r, c - 1)
}

fn maxAreaOfIsland(grid) {
  var best = 0
  for var r in 0..len(grid) {
    for var c in 0..len(grid[0]) {
      var a = area(grid, r, c)
      if a > best { best = a }
    }
  }
  return best
}
''',
    },
    tests=[
        [[[0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
          [0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0],
          [0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0]]],
        [[[0, 0, 0, 0, 0, 0, 0, 0]]],
        [[[1]]], [[[0, 1, 1], [0, 1, 1], [1, 0, 0]]],
        [[[1, 0, 1], [0, 1, 0], [1, 0, 1]]],
        [[[1] * 30 for _ in range(30)]],
        [[[1 if (c % 4 != 3 or (r == 0 and c % 8 == 3) or (r == 29 and c % 8 == 7)) else 0
           for c in range(30)] for r in range(30)]],
        [_grid(_R, 25, 30, 0.5)], [_grid(_R, 30, 30, 0.6)],
    ],
))

# ---------------------------------------------------------------- 4. rotting oranges

PROBLEMS.append(dict(
    id="grid-rotting-oranges",
    title="Rotting Oranges",
    difficulty=2,
    tags=["graph", "grid", "bfs", "multi-source"],
    fn="oranges_rotting",
    params=[["grid", "int[][]"]],
    returns="int",
    statement=r"""
Each cell holds `0` (empty), `1` (fresh orange) or `2` (rotten orange). Every minute,
each fresh orange that is 4-directionally adjacent to a rotten one becomes rotten.

Return the minimum number of minutes until no fresh orange remains, or `-1` if some
fresh orange can never rot. If there are no fresh oranges at the start, the answer is `0`.
""",
    constraints=["1 ≤ rows, cols ≤ 30", "grid[r][c] ∈ {0, 1, 2}"],
    example_notes=[
        "The rot spreads from the top-left corner and reaches the last orange (bottom right) after 4 minutes.",
        "The orange in the bottom-left corner is walled off by empty cells and never rots.",
    ],
    hints=[
        "The rot spreads one step per minute from ALL rotten oranges at once. Which traversal advances in layers like that?",
        "Multi-source BFS: start the queue with every rotten orange at time 0.",
        "Process the queue level by level; each level is one minute. Count fresh oranges and check that the count reaches 0.",
    ],
    explanation=r"""
## Intuition

"Every minute, spread to the neighbours" is BFS layering: layer `t` contains the
oranges that rot at minute `t`. The twist is that there are **several sources**. Instead
of running one BFS per rotten orange, put **all** of them into the queue at the start;
BFS then computes, for every cell, the distance to the *nearest* rotten orange, which is
exactly when it rots. The answer is the largest such distance.

## Approach

1. Push every `2` into the queue; count the `1`s as `fresh`.
2. While the queue is non-empty and `fresh > 0`: process one whole level (snapshot the
   queue length), rotting each fresh neighbour (`fresh -= 1`, push it). After the level,
   `minutes += 1`.
3. Return `minutes` if `fresh == 0`, else `-1`.

```text
minute 0      minute 1      minute 2      minute 3      minute 4
2 1 1         2 2 1         2 2 2         2 2 2         2 2 2
1 1 0         2 1 0         2 2 0         2 2 0         2 2 0
0 1 1         0 1 1         0 1 1         0 2 1         0 2 2
```

The `fresh > 0` guard in the loop condition stops us from counting an extra minute
after the last orange rots.

## Complexity

- **Time O(R·C)**: each cell enters the queue at most once.
- **Space O(R·C)** for the queue.

## Common mistakes

- **Running a separate BFS from each rotten orange** and taking minima: correct but
  O((R·C)²).
- **Counting minutes per pop** instead of per level.
- **Off by one**: incrementing the minute for the final level that rots nothing new.
- **Forgetting the no-fresh case**: return 0 even if there are no rotten oranges either.

## Going further

Multi-source BFS also solves *Walls and Gates* (distance from every room to the nearest
gate) and *01 Matrix* (distance to the nearest 0). Whenever a question asks for distance
to the **nearest** of several targets, seed the queue with all of them.

The ESPresso reference shows a queue-free variant: store the minute in the cell itself
(`2 + t`) and sweep the grid once per minute. It is O((R·C)·T), fine for small grids.
""",
    solution=r'''
def oranges_rotting(grid):
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c))       # every rotten orange is a source
            elif grid[r][c] == 1:
                fresh += 1
    minutes = 0
    # Stop as soon as nothing is fresh, or we would count an empty extra minute.
    while queue and fresh > 0:
        for _ in range(len(queue)):        # exactly the oranges that rotted last minute
            r, c = queue.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    grid[nr][nc] = 2       # rot it now so it is not pushed twice
                    fresh -= 1
                    queue.append((nr, nc))
        minutes += 1
    return minutes if fresh == 0 else -1
''',
    refs={
        "cpp": r'''
long long orangesRotting(vector<vector<long long>>& grid) {
    int R = grid.size(), C = grid[0].size();
    queue<pair<int, int>> q;
    int fresh = 0;
    for (int r = 0; r < R; r++)
        for (int c = 0; c < C; c++) {
            if (grid[r][c] == 2) q.push({r, c});
            else if (grid[r][c] == 1) fresh++;
        }
    const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1};
    long long minutes = 0;
    while (!q.empty() && fresh > 0) {
        for (size_t k = q.size(); k > 0; k--) {     // one minute = one BFS level
            auto [r, c] = q.front(); q.pop();
            for (int d = 0; d < 4; d++) {
                int nr = r + dr[d], nc = c + dc[d];
                if (nr >= 0 && nr < R && nc >= 0 && nc < C && grid[nr][nc] == 1) {
                    grid[nr][nc] = 2; fresh--; q.push({nr, nc});
                }
            }
        }
        minutes++;
    }
    return fresh == 0 ? minutes : -1;
}
''',
        "rust": r'''
use std::collections::VecDeque;

pub fn oranges_rotting(grid: Vec<Vec<i64>>) -> i64 {
    let mut g = grid;
    let (rows, cols) = (g.len() as i64, g[0].len() as i64);
    let mut q = VecDeque::new();
    let mut fresh = 0;
    for r in 0..rows {
        for c in 0..cols {
            match g[r as usize][c as usize] {
                2 => q.push_back((r, c)),
                1 => fresh += 1,
                _ => {}
            }
        }
    }
    let mut minutes = 0;
    while !q.is_empty() && fresh > 0 {
        for _ in 0..q.len() {
            let (r, c) = q.pop_front().unwrap();
            for (dr, dc) in [(1, 0), (-1, 0), (0, 1), (0, -1)] {
                let (nr, nc) = (r + dr, c + dc);
                if nr >= 0 && nr < rows && nc >= 0 && nc < cols && g[nr as usize][nc as usize] == 1 {
                    g[nr as usize][nc as usize] = 2;
                    fresh -= 1;
                    q.push_back((nr, nc));
                }
            }
        }
        minutes += 1;
    }
    if fresh == 0 { minutes } else { -1 }
}
''',
        "espresso": r'''
// No queue needed: a cell holding 2 + t rotted at minute t. Each sweep
// rots the fresh neighbours of the cells that rotted during the last minute.
fn orangesRotting(grid) {
  var rows = len(grid)
  var cols = len(grid[0])
  var t = 2
  var changed = true
  while changed {
    changed = false
    for var r in 0..rows {
      for var c in 0..cols {
        if grid[r][c] == t {
          if r > 0 and grid[r - 1][c] == 1 {
            grid[r - 1][c] = t + 1
            changed = true
          }
          if r + 1 < rows and grid[r + 1][c] == 1 {
            grid[r + 1][c] = t + 1
            changed = true
          }
          if c > 0 and grid[r][c - 1] == 1 {
            grid[r][c - 1] = t + 1
            changed = true
          }
          if c + 1 < cols and grid[r][c + 1] == 1 {
            grid[r][c + 1] = t + 1
            changed = true
          }
        }
      }
    }
    if changed { t += 1 }
  }
  for var r in 0..rows {
    for var c in 0..cols {
      if grid[r][c] == 1 { return -1 }
    }
  }
  return t - 2
}
''',
    },
    tests=[
        [[[2, 1, 1], [1, 1, 0], [0, 1, 1]]],
        [[[2, 1, 1], [0, 1, 1], [1, 0, 1]]],
        [[[0, 2]]], [[[0]]], [[[1]]], [[[2, 2], [1, 1], [0, 0], [2, 0]]],
        [[[2] + [1] * 29]],
        [[[_R.choice([0, 1, 1, 1, 2]) if (r, c) != (0, 0) else 2 for c in range(20)] for r in range(15)]],
        [[[1] * 30 for _ in range(29)] + [[1] * 29 + [2]]],
        [[[2 if (r, c) in ((3, 4), (20, 25), (29, 0)) else (0 if (r * 7 + c * 3) % 11 == 0 else 1) for c in range(30)] for r in range(30)]],
    ],
))

# ---------------------------------------------------------------- 5. shortest path binary matrix


def _maze(rng, n, p):
    g = _grid(rng, n, n, p)
    g[0][0] = 0
    g[n - 1][n - 1] = 0
    return g


PROBLEMS.append(dict(
    id="grid-shortest-path-binary-matrix",
    title="Shortest Path in Binary Matrix",
    difficulty=2,
    tags=["graph", "grid", "bfs"],
    fn="shortest_path_binary_matrix",
    params=[["grid", "int[][]"]],
    returns="int",
    statement=r"""
In an `n × n` grid, `0` is an open cell and `1` is blocked. A path may move between
open cells in any of the **8 directions** (including diagonals). Return the number of
**cells** on the shortest path from the top-left cell to the bottom-right cell, or `-1`
if there is no such path (including when either end is blocked).
""",
    constraints=["1 ≤ n ≤ 40", "grid[r][c] ∈ {0, 1}"],
    example_notes=[
        "Diagonal moves allowed: (0,0) → (1,1) is a 2-cell path.",
        "(0,0) → (0,1) → (1,2) → (2,2): four cells.",
    ],
    hints=[
        "All moves cost the same. Which search finds shortest paths in that case?",
        "BFS from (0,0); the first time you reach (n-1, n-1) you have the shortest distance.",
        "Store the distance (in cells) with each queued cell, mark cells when you enqueue them, and handle blocked endpoints up front.",
    ],
    explanation=r"""
## Intuition

Every step has the same cost, so "shortest path" means "fewest steps": that is BFS.
BFS explores cells in order of distance, so the first time it pops the target, the
distance recorded with it is minimal. With 8 directions, each cell has up to 8
neighbours instead of 4; nothing else changes.

## Approach

1. If `grid[0][0]` or `grid[n-1][n-1]` is blocked, return `-1`.
2. Queue `(0, 0, 1)`: row, column, cells on the path so far. Mark `(0,0)` visited
   (here: set it to 1).
3. Pop `(r, c, d)`. If it is the target, return `d`. Otherwise push each of the 8
   neighbours that is in bounds and open with distance `d + 1`, marking it immediately.
4. Queue exhausted: return `-1`.

```text
grid       distance (cells) when first enqueued
0 0 0      1 2 3
1 1 0      # # 3        (1,2) is a diagonal neighbour of (0,1): distance 3
1 1 0      # # 4        target reached with d = 4
```

Note how the diagonal move lets `(1,2)` be reached at the same distance as `(0,2)`.

## Complexity

- **Time O(n²)**: each cell is enqueued at most once, with 8 neighbour checks.
- **Space O(n²)** for the queue/visited marks.

## Common mistakes

- **DFS**: finds *a* path, not the shortest; exploring all paths is exponential.
- **Counting edges instead of cells**: a 1×1 grid `[[0]]` has answer 1.
- **Marking visited when popping**: the same cell may be queued many times; with 8
  neighbours this blows up the queue.
- **Forgetting the blocked-start/blocked-end checks.**

## Going further

*A\** search speeds this up with a heuristic (here Chebyshev distance
`max(|dr|, |dc|)`), expanding cells by `distance + heuristic`. With weighted cells
(different costs per step) you would switch to Dijkstra, covered later in this track.
""",
    solution=r'''
def shortest_path_binary_matrix(grid):
    n = len(grid)
    if grid[0][0] == 1 or grid[n - 1][n - 1] == 1:
        return -1
    grid[0][0] = 1                       # reuse the grid as the visited set
    queue = deque([(0, 0, 1)])           # (row, col, cells on the path so far)
    while queue:
        r, c, d = queue.popleft()
        # BFS pops cells in nondecreasing distance: the first pop of the target
        # is along a shortest path.
        if r == n - 1 and c == n - 1:
            return d
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 0:
                    grid[nr][nc] = 1     # mark when enqueuing, never twice
                    queue.append((nr, nc, d + 1))
    return -1
''',
    refs={
        "cpp": r'''
long long shortestPathBinaryMatrix(vector<vector<long long>>& grid) {
    int n = grid.size();
    if (grid[0][0] || grid[n - 1][n - 1]) return -1;
    queue<array<int, 3>> q;                          // row, col, distance in cells
    grid[0][0] = 1;
    q.push({0, 0, 1});
    while (!q.empty()) {
        auto [r, c, d] = q.front(); q.pop();
        if (r == n - 1 && c == n - 1) return d;
        for (int dr = -1; dr <= 1; dr++)
            for (int dc = -1; dc <= 1; dc++) {
                int nr = r + dr, nc = c + dc;
                if (nr >= 0 && nr < n && nc >= 0 && nc < n && grid[nr][nc] == 0) {
                    grid[nr][nc] = 1;
                    q.push({nr, nc, d + 1});
                }
            }
    }
    return -1;
}
''',
        "rust": r'''
use std::collections::VecDeque;

pub fn shortest_path_binary_matrix(grid: Vec<Vec<i64>>) -> i64 {
    let mut g = grid;
    let n = g.len() as i64;
    let last = (n - 1) as usize;
    if g[0][0] == 1 || g[last][last] == 1 { return -1; }
    g[0][0] = 1;
    let mut q = VecDeque::from(vec![(0i64, 0i64, 1i64)]);
    while let Some((r, c, d)) = q.pop_front() {
        if r == n - 1 && c == n - 1 { return d; }
        for dr in -1..=1 {
            for dc in -1..=1 {
                let (nr, nc) = (r + dr, c + dc);
                if nr >= 0 && nr < n && nc >= 0 && nc < n && g[nr as usize][nc as usize] == 0 {
                    g[nr as usize][nc as usize] = 1;
                    q.push_back((nr, nc, d + 1));
                }
            }
        }
    }
    -1
}
''',
        "espresso": r'''
// Queue-free BFS: an open cell holding v means "reached with v - 1 cells".
// Each sweep extends the frontier (cells equal to d) by one step.
fn shortestPathBinaryMatrix(grid) {
  var n = len(grid)
  if grid[0][0] != 0 or grid[n - 1][n - 1] != 0 { return -1 }
  grid[0][0] = 2
  var d = 2
  var changed = true
  while changed and grid[n - 1][n - 1] == 0 {
    changed = false
    for var r in 0..n {
      for var c in 0..n {
        if grid[r][c] == d {
          for var dr in 0..3 {
            for var dc in 0..3 {
              var nr = r + dr - 1
              var nc = c + dc - 1
              if nr >= 0 and nc >= 0 and nr < n and nc < n {
                if grid[nr][nc] == 0 {
                  grid[nr][nc] = d + 1
                  changed = true
                }
              }
            }
          }
        }
      }
    }
    d += 1
  }
  if grid[n - 1][n - 1] == 0 { return -1 }
  return grid[n - 1][n - 1] - 1
}
''',
    },
    tests=[
        [[[0, 1], [1, 0]]], [[[0, 0, 0], [1, 1, 0], [1, 1, 0]]],
        [[[1, 0, 0], [1, 1, 0], [1, 1, 0]]], [[[0]]], [[[1]]], [[[0, 0], [0, 1]]],
        [[[0, 1, 0], [1, 1, 0], [0, 0, 0]]],
        [[[0] * 40 for _ in range(40)]],
        [[[1 if (c % 2 == 1 and (r != (0 if c % 4 == 1 else 39))) else 0 for c in range(40)] for r in range(40)]],
        [_maze(_R, 30, 0.3)], [_maze(_R, 40, 0.35)], [_maze(_R, 40, 0.2)],
    ],
))

# ---------------------------------------------------------------- 6/7. course schedule


def _dag(rng, n, m, cycle=False):
    order = list(range(n))
    rng.shuffle(order)
    edges = set()
    tries = 0
    while len(edges) < m and tries < m * 20:
        tries += 1
        i, j = sorted(rng.sample(range(n), 2))
        edges.add((order[j], order[i]))     # [course, prerequisite]: order[i] first
    edges = [list(e) for e in edges]
    if cycle and n >= 2:
        # Add a back edge along an existing path to force a cycle.
        a, b = edges[rng.randrange(len(edges))]
        edges.append([b, a])
    rng.shuffle(edges)
    return edges


def _course_tests():
    rng = random.Random(606)
    return [
        [8, _dag(rng, 8, 10)], [8, _dag(rng, 8, 10, True)],
        [200, _dag(rng, 200, 600)], [200, _dag(rng, 200, 600, True)],
        [1000, _dag(rng, 1000, 1500)], [1000, _dag(rng, 1000, 1500, True)],
    ]


PROBLEMS.append(dict(
    id="graph-course-schedule",
    title="Course Schedule",
    difficulty=2,
    tags=["graph", "topological sort", "cycle detection"],
    fn="can_finish",
    params=[["num_courses", "int"], ["prerequisites", "int[][]"]],
    returns="bool",
    espresso=False,
    statement=r"""
There are `num_courses` courses labelled `0 … num_courses-1`. Each pair `[a, b]` in
`prerequisites` means course `b` must be taken **before** course `a`. Return `true` if it
is possible to finish every course, i.e. if the requirements contain no cycle.
""",
    constraints=["1 ≤ num_courses ≤ 1000", "0 ≤ len(prerequisites) ≤ 1501", "pairs are distinct and a ≠ b"],
    example_notes=[
        "Take 0, then 1.",
        "0 needs 1 and 1 needs 0: a cycle, so neither can ever be taken.",
    ],
    hints=[
        "Model courses as vertices and `b → a` as a directed edge. When is a schedule impossible?",
        "A valid order exists exactly when the directed graph has no cycle.",
        "Kahn's algorithm: repeatedly take a course with no remaining prerequisites. If you manage to take all of them, there was no cycle.",
    ],
    explanation=r"""
## Intuition

Draw an arrow `b → a` for "take `b` before `a`". A schedule is an ordering in which every
arrow points forward: a **topological order**. One exists if and only if the graph is a
**DAG** (no directed cycle); with a cycle like `0 → 1 → 0`, each course waits for the
other forever.

## Approach (Kahn's algorithm)

1. Build the adjacency list `b → a` and `indeg[a]` = number of prerequisites of `a`.
2. Queue every course with `indeg == 0` (it can be taken right away).
3. Pop a course, count it as taken, and for each course that depended on it decrement
   its in-degree; when that reaches 0, it becomes available: push it.
4. Return `taken == num_courses`.

```text
n = 4, prereqs [1,0] [2,1] [3,2] [1,3]       edges 0→1, 1→2, 2→3, 3→1
indeg: 0:0 1:2 2:1 3:1
queue [0] -> take 0, indeg[1] = 1            nothing else reaches 0
taken = 1 < 4  ->  False   (1, 2, 3 form a cycle)
```

Courses on a cycle never reach in-degree 0, because each waits for another member of
the cycle. Courses that merely *depend on* a cycle are also stuck, which is fine: the
answer is already `false`.

**DFS alternative**: three colours (unvisited, in progress, done). Meeting an
*in-progress* vertex means you followed a back edge: a cycle.

## Complexity

- **Time O(V + E)**: each course and each prerequisite is processed once.
- **Space O(V + E)** for the adjacency list.

## Common mistakes

- **Reversing the edge**: `[a, b]` means `b` first. (For *this* problem the direction does
  not change the answer, since reversing all edges preserves cycles, but for Course
  Schedule II it matters.)
- **Two-colour DFS** (just visited/unvisited) reports a cycle whenever two paths
  reach the same vertex, e.g. `0→1, 0→2, 1→3, 2→3`, which is a DAG.
- **Recursive DFS depth**: a chain of 1000 courses is fine here, but Kahn's algorithm
  avoids recursion entirely.

## Going further

The next problem asks for the actual order, made unique by choosing the smallest
available course each time.
""",
    solution=r'''
def can_finish(num_courses, prerequisites):
    adj = [[] for _ in range(num_courses)]
    indeg = [0] * num_courses
    for a, b in prerequisites:
        adj[b].append(a)         # b must come before a: edge b -> a
        indeg[a] += 1            # a has one more unmet prerequisite
    # Courses with no prerequisites can be taken immediately.
    queue = deque(i for i in range(num_courses) if indeg[i] == 0)
    taken = 0
    while queue:
        b = queue.popleft()
        taken += 1
        for a in adj[b]:
            indeg[a] -= 1
            if indeg[a] == 0:    # its last prerequisite is done
                queue.append(a)
    # Courses on (or behind) a cycle never become available.
    return taken == num_courses
''',
    refs={
        "cpp": r'''
bool canFinish(long long numCourses, vector<vector<long long>>& prerequisites) {
    int n = numCourses;
    vector<vector<int>> adj(n);
    vector<int> indeg(n, 0);
    for (auto& p : prerequisites) { adj[p[1]].push_back(p[0]); indeg[p[0]]++; }
    queue<int> q;
    for (int i = 0; i < n; i++) if (indeg[i] == 0) q.push(i);
    int taken = 0;
    while (!q.empty()) {
        int b = q.front(); q.pop();
        taken++;
        for (int a : adj[b]) if (--indeg[a] == 0) q.push(a);
    }
    return taken == n;
}
''',
        "rust": r'''
use std::collections::VecDeque;

pub fn can_finish(num_courses: i64, prerequisites: Vec<Vec<i64>>) -> bool {
    let n = num_courses as usize;
    let mut adj = vec![Vec::new(); n];
    let mut indeg = vec![0usize; n];
    for p in &prerequisites {
        adj[p[1] as usize].push(p[0] as usize);
        indeg[p[0] as usize] += 1;
    }
    let mut q: VecDeque<usize> = (0..n).filter(|&i| indeg[i] == 0).collect();
    let mut taken = 0;
    while let Some(b) = q.pop_front() {
        taken += 1;
        for &a in &adj[b] {
            indeg[a] -= 1;
            if indeg[a] == 0 { q.push_back(a); }
        }
    }
    taken == n
}
''',
    },
    tests=[
        [2, [[1, 0]]], [2, [[1, 0], [0, 1]]], [1, []], [3, []],
        [4, [[1, 0], [2, 1], [3, 2], [1, 3]]], [4, [[1, 0], [2, 0], [3, 1], [3, 2]]],
    ] + _course_tests(),
))


def _order_tests():
    rng = random.Random(707)
    return [
        [10, _dag(rng, 10, 12)], [10, _dag(rng, 10, 12, True)],
        [300, _dag(rng, 300, 700)], [300, _dag(rng, 300, 700, True)],
        [1000, _dag(rng, 1000, 1500)],
    ]


PROBLEMS.append(dict(
    id="graph-course-schedule-order",
    title="Course Schedule II (Smallest Order)",
    difficulty=3,
    tags=["graph", "topological sort", "heap"],
    fn="find_order",
    params=[["num_courses", "int"], ["prerequisites", "int[][]"]],
    returns="int[]",
    espresso=False,
    statement=r"""
Same setting as *Course Schedule*: `[a, b]` means course `b` must be taken before course
`a`. Return an order in which all `num_courses` courses can be taken. Many orders may be
valid, so return the **lexicographically smallest** one: at every step, take the
smallest-numbered course whose prerequisites are all done.

If it is impossible to take every course, return an empty list.
""",
    constraints=["1 ≤ num_courses ≤ 1000", "0 ≤ len(prerequisites) ≤ 1500", "pairs are distinct and a ≠ b"],
    example_notes=[
        "0 first; then both 1 and 2 are available, and 1 is smaller; 3 needs both.",
        "A cycle between 0 and 1: no valid order.",
    ],
    hints=[
        "This is Kahn's algorithm again, but the order in which you pick available courses now matters.",
        "Always picking the smallest available course yields the lexicographically smallest order. Which data structure hands you the minimum quickly?",
        "Replace Kahn's FIFO queue with a min-heap. If the result is shorter than num_courses, return [].",
    ],
    explanation=r"""
## Intuition

Kahn's algorithm produces *some* topological order; the freedom is in which available
course you take next. The lexicographically smallest order is obtained greedily: at each
step take the **smallest** available course. (Exchange argument: if an optimal order
started with a larger available course `y` while a smaller `x` was available, swapping
to `x` first keeps the order valid, since `x` had no pending prerequisites, and makes it
lexicographically smaller.)

"Repeatedly extract the minimum of a changing set" is exactly a **min-heap**.

## Approach

1. Build `adj[b] → a` and `indeg[a]` as before.
2. Heap ← all courses with in-degree 0.
3. While the heap is non-empty: pop the smallest `b`, append it, decrement the in-degree
   of each `a` in `adj[b]`, pushing `a` when it reaches 0.
4. Return the order if it has all `num_courses` entries, else `[]`.

```text
n = 4, prereqs [1,0] [2,0] [3,1] [3,2]
heap [0]        pop 0 -> order [0]         indeg 1:0 2:0 -> push 1, 2
heap [1,2]      pop 1 -> order [0,1]       indeg 3:1
heap [2]        pop 2 -> order [0,1,2]     indeg 3:0 -> push 3
heap [3]        pop 3 -> order [0,1,2,3]
```

With a plain FIFO queue the result would depend on push order, which is why this
problem insists on the heap: it makes the answer unique.

## Complexity

- **Time O((V + E) log V)**: each course is pushed and popped once (log V each); each
  edge is relaxed once.
- **Space O(V + E)**.

## Common mistakes

- **Returning a partial order** when there is a cycle; the statement asks for `[]`.
- **C++ `priority_queue`** is a max-heap: use `priority_queue<int, vector<int>,
  greater<int>>`.
- **Rust `BinaryHeap`** is a max-heap: push `Reverse(x)`.
- **Sorting the initial zero-in-degree courses** but then using a FIFO queue: later
  courses still come out in discovery order, not smallest-first.

## Going further

The *largest* lexicographic order, or "smallest label as late as possible" (reverse the
graph and use a max-heap, then reverse the result), are classic variations and show that
greedy choices in topological sorting need care.
""",
    solution=r'''
def find_order(num_courses, prerequisites):
    adj = [[] for _ in range(num_courses)]
    indeg = [0] * num_courses
    for a, b in prerequisites:
        adj[b].append(a)              # b before a
        indeg[a] += 1
    # Min-heap of available courses: always take the smallest one next,
    # which yields the lexicographically smallest valid order.
    heap = [i for i in range(num_courses) if indeg[i] == 0]
    heapify(heap)
    order = []
    while heap:
        b = heappop(heap)
        order.append(b)
        for a in adj[b]:
            indeg[a] -= 1
            if indeg[a] == 0:
                heappush(heap, a)
    # Anything left over sits on or behind a cycle.
    return order if len(order) == num_courses else []
''',
    refs={
        "cpp": r'''
vector<long long> findOrder(long long numCourses, vector<vector<long long>>& prerequisites) {
    int n = numCourses;
    vector<vector<int>> adj(n);
    vector<int> indeg(n, 0);
    for (auto& p : prerequisites) { adj[p[1]].push_back(p[0]); indeg[p[0]]++; }
    priority_queue<int, vector<int>, greater<int>> pq;    // min-heap
    for (int i = 0; i < n; i++) if (indeg[i] == 0) pq.push(i);
    vector<long long> order;
    while (!pq.empty()) {
        int b = pq.top(); pq.pop();
        order.push_back(b);
        for (int a : adj[b]) if (--indeg[a] == 0) pq.push(a);
    }
    if ((int)order.size() != n) order.clear();
    return order;
}
''',
        "rust": r'''
use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn find_order(num_courses: i64, prerequisites: Vec<Vec<i64>>) -> Vec<i64> {
    let n = num_courses as usize;
    let mut adj = vec![Vec::new(); n];
    let mut indeg = vec![0usize; n];
    for p in &prerequisites {
        adj[p[1] as usize].push(p[0] as usize);
        indeg[p[0] as usize] += 1;
    }
    // BinaryHeap is a max-heap; Reverse flips the ordering into a min-heap.
    let mut heap: BinaryHeap<Reverse<usize>> = (0..n).filter(|&i| indeg[i] == 0).map(Reverse).collect();
    let mut order = Vec::with_capacity(n);
    while let Some(Reverse(b)) = heap.pop() {
        order.push(b as i64);
        for &a in &adj[b] {
            indeg[a] -= 1;
            if indeg[a] == 0 { heap.push(Reverse(a)); }
        }
    }
    if order.len() == n { order } else { Vec::new() }
}
''',
    },
    tests=[
        [4, [[1, 0], [2, 0], [3, 1], [3, 2]]], [2, [[1, 0], [0, 1]]], [1, []], [3, []],
        [3, [[0, 2], [1, 2]]], [6, [[0, 5], [1, 5], [2, 4], [3, 4], [0, 3]]],
    ] + _order_tests(),
))

# ---------------------------------------------------------------- 8. components


def _rand_edges(rng, n, m):
    es = set()
    while len(es) < m:
        u, v = rng.sample(range(n), 2)
        es.add((min(u, v), max(u, v)))
    es = [list(e) for e in es]
    rng.shuffle(es)
    return es


PROBLEMS.append(dict(
    id="graph-count-components",
    title="Number of Connected Components",
    difficulty=2,
    tags=["graph", "union-find"],
    fn="count_components",
    params=[["n", "int"], ["edges", "int[][]"]],
    returns="int",
    espresso=False,
    statement=r"""
An undirected graph has `n` vertices `0 … n-1` and the given `edges` (each `[u, v]`).
Return the number of **connected components**. An isolated vertex is a component by
itself.
""",
    constraints=["1 ≤ n ≤ 1500", "0 ≤ len(edges) ≤ 1500", "no self-loops or duplicate edges"],
    example_notes=["{0, 1, 2} and {3, 4}.", "All five vertices are linked in a chain."],
    hints=[
        "Start with every vertex alone: n components. What does adding an edge do to that count?",
        "An edge between two different components merges them (count - 1); an edge inside a component changes nothing.",
        "Union-find tracks which component each vertex belongs to: decrement the count whenever union actually merges.",
    ],
    explanation=r"""
## Intuition

Start with `n` singleton components. Each edge either joins two different components
(the count drops by one) or lands inside one component (no change). **Union-find** answers
"are these in the same component?" and merges components in near-constant time, so a
single pass over the edges suffices.

## Approach

```python
parent = list(range(n))           # each vertex is its own root
def find(x):                      # root of x's component, with path halving
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
```

For each edge `(u, v)`: `ru, rv = find(u), find(v)`; if `ru != rv`, attach one root under
the other and decrement `components`.

```text
n=5, edges (0,1) (1,2) (3,4)
parent   [0,1,2,3,4]   comps 5
(0,1):   [1,1,2,3,4]   comps 4
(1,2):   [1,2,2,3,4]   comps 3     find(1)=1, find(2)=2 -> merge
(3,4):   [1,2,2,4,4]   comps 2
```

BFS/DFS from each unvisited vertex (as in Number of Islands) works too; union-find
avoids building an adjacency list and handles edges arriving one at a time.

## Complexity

- **Time O(E · α(n))** with path compression and union by size (α is the inverse
  Ackermann function, ≤ 4 for any realistic n). With path halving alone it is
  O(E log n) worst case, still fast.
- **Space O(n)**.

## Common mistakes

- **`parent[u] = v`** instead of linking *roots*: merges only one vertex, not the whole
  component.
- **Comparing `parent[u] == parent[v]`** instead of `find(u) == find(v)`: parents are not
  roots in general.
- **Recursive `find`** without compression on a long chain can recurse n deep.

## Going further

Union by size (attach the smaller tree under the larger) bounds the tree height by
log₂ n even without path compression. Union-find also underpins Kruskal's minimum
spanning tree (later in this track) and offline dynamic connectivity.
""",
    solution=r'''
def count_components(n, edges):
    parent = list(range(n))     # every vertex starts as the root of its own set
    size = [1] * n

    def find(x):
        # Climb to the root, halving the path as we go so later finds are faster.
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    components = n
    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru == rv:
            continue            # already connected: edge is inside a component
        # Union by size keeps the trees shallow.
        if size[ru] < size[rv]:
            ru, rv = rv, ru
        parent[rv] = ru
        size[ru] += size[rv]
        components -= 1         # two components became one
    return components
''',
    refs={
        "cpp": r'''
long long countComponents(long long n, vector<vector<long long>>& edges) {
    vector<int> parent(n), sz(n, 1);
    iota(parent.begin(), parent.end(), 0);
    function<int(int)> find = [&](int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    };
    long long comps = n;
    for (auto& e : edges) {
        int a = find(e[0]), b = find(e[1]);
        if (a == b) continue;
        if (sz[a] < sz[b]) swap(a, b);
        parent[b] = a; sz[a] += sz[b];
        comps--;
    }
    return comps;
}
''',
        "rust": r'''
fn find(parent: &mut Vec<usize>, mut x: usize) -> usize {
    while parent[x] != x {
        parent[x] = parent[parent[x]];               // path halving
        x = parent[x];
    }
    x
}

pub fn count_components(n: i64, edges: Vec<Vec<i64>>) -> i64 {
    let n = n as usize;
    let mut parent: Vec<usize> = (0..n).collect();
    let mut size = vec![1usize; n];
    let mut comps = n as i64;
    for e in &edges {
        let (mut a, mut b) = (find(&mut parent, e[0] as usize), find(&mut parent, e[1] as usize));
        if a == b { continue; }
        if size[a] < size[b] { std::mem::swap(&mut a, &mut b); }
        parent[b] = a;
        size[a] += size[b];
        comps -= 1;
    }
    comps
}
''',
    },
    tests=[
        [5, [[0, 1], [1, 2], [3, 4]]], [5, [[0, 1], [1, 2], [2, 3], [3, 4]]],
        [1, []], [4, []], [4, [[0, 1], [1, 2], [0, 2]]], [3, [[2, 1]]],
        [100, _rand_edges(_R, 100, 60)], [1500, _rand_edges(_R, 1500, 1200)],
        [1500, [[i, i + 1] for i in range(1499)]],
    ],
))

# ---------------------------------------------------------------- 9. redundant connection


def _redundant(rng, n):
    es = set()
    for i in range(2, n + 1):
        j = rng.randint(1, i - 1)
        es.add((j, i))
    while True:
        u, v = sorted(rng.sample(range(1, n + 1), 2))
        if (u, v) not in es:
            es.add((u, v))
            break
    es = [list(e) for e in es]
    rng.shuffle(es)
    return es


PROBLEMS.append(dict(
    id="graph-redundant-connection",
    title="Redundant Connection",
    difficulty=2,
    tags=["graph", "union-find"],
    fn="find_redundant_connection",
    params=[["edges", "int[][]"]],
    returns="int[]",
    statement=r"""
A tree with `n` vertices labelled `1 … n` had **one extra edge** added, so `edges` now has
`n` entries and contains exactly one cycle. Each edge is `[u, v]` with `u < v`, with no
duplicates.

Return an edge that can be removed so that the remaining graph is a tree. If several
edges qualify, return the one that occurs **last** in `edges`.
""",
    constraints=["3 ≤ n ≤ 2000", "1 ≤ u < v ≤ n", "the graph is connected"],
    example_notes=[
        "1–2–3–1 is a cycle; [2,3] appears last among its edges.",
        "The cycle is 1–2–3–4–1; the last of its edges in the list is [1,4].",
    ],
    hints=[
        "Which edges can be removed? Exactly those on the unique cycle.",
        "Add edges one by one with union-find. The first edge whose endpoints are already connected closes the cycle.",
        "Why is that edge the LAST cycle edge in the input? The cycle cannot close until all of its edges have been added.",
    ],
    explanation=r"""
## Intuition

Removing an edge leaves a tree iff the edge lies on the cycle. Among the cycle edges we
need the one appearing last in the input. Process edges in order with union-find: an
edge whose endpoints are **already connected** closes a cycle. Since the cycle only
exists once all of its edges are present, the first such edge is precisely the
last-listed cycle edge. One pass, no explicit cycle search.

## Approach

1. `parent[i] = i` for `i = 1..n` (size the array `n + 1`; labels are 1-based).
2. For each `[u, v]` in order: if `find(u) == find(v)`, return `[u, v]`; otherwise union.

```text
edges [1,2] [1,3] [2,3]
[1,2]: union {1,2}
[1,3]: union {1,2,3}
[2,3]: find(2) == find(3) -> answer [2,3]
```

## Complexity

- **Time O(n · α(n))**, essentially linear.
- **Space O(n)**.

## Common mistakes

- **0-based arrays with 1-based labels**: `parent` needs `n + 1` slots, and `n` is
  `len(edges)` here.
- **Returning the *first* cycle edge** found by DFS rather than the last in input order.
- **Mutating `parent[u] = v`** directly instead of linking roots.

## Going further

*Redundant Connection II* makes the graph **directed** (a rooted tree plus one edge).
Now a vertex can end up with two parents, and you must combine the "two parents" case
with the cycle case; union-find still does the heavy lifting.
""",
    solution=r'''
def find_redundant_connection(edges):
    n = len(edges)                       # a tree plus one edge: n vertices, n edges
    parent = list(range(n + 1))          # labels are 1..n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru == rv:
            # u and v were already connected, so this edge closes the cycle.
            # The cycle cannot exist before its last edge arrives, so this is
            # the cycle edge that appears last in the input.
            return [u, v]
        parent[ru] = rv
    return []
''',
    refs={
        "cpp": r'''
vector<long long> findRedundantConnection(vector<vector<long long>>& edges) {
    int n = edges.size();
    vector<int> parent(n + 1);
    iota(parent.begin(), parent.end(), 0);
    auto find = [&](int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    };
    for (auto& e : edges) {
        int a = find(e[0]), b = find(e[1]);
        if (a == b) return {e[0], e[1]};             // closes the cycle
        parent[a] = b;
    }
    return {};
}
''',
        "rust": r'''
fn find(parent: &mut Vec<usize>, mut x: usize) -> usize {
    while parent[x] != x {
        parent[x] = parent[parent[x]];
        x = parent[x];
    }
    x
}

pub fn find_redundant_connection(edges: Vec<Vec<i64>>) -> Vec<i64> {
    let mut parent: Vec<usize> = (0..=edges.len()).collect();
    for e in &edges {
        let a = find(&mut parent, e[0] as usize);
        let b = find(&mut parent, e[1] as usize);
        if a == b { return vec![e[0], e[1]]; }
        parent[a] = b;
    }
    Vec::new()
}
''',
    },
    tests=[
        [[[1, 2], [1, 3], [2, 3]]], [[[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]],
        [[[2, 3], [1, 2], [1, 3]]], [[[1, 3], [3, 4], [1, 5], [3, 5], [2, 3]]],
        [[[1, 2], [2, 3], [3, 4], [4, 5], [1, 5]]],
        [_redundant(_R, 10)], [_redundant(_R, 300)], [_redundant(_R, 2000)],
    ],
))

# ---------------------------------------------------------------- 10. bipartite


def _bip(rng, n, m, odd):
    color = [rng.randint(0, 1) for _ in range(n)]
    es = set()
    tries = 0
    while len(es) < m and tries < 50 * m:
        tries += 1
        u, v = rng.sample(range(n), 2)
        if color[u] != color[v]:
            es.add((min(u, v), max(u, v)))
    if odd:
        same = [(u, v) for u in range(n) for v in range(u + 1, min(n, u + 5)) if color[u] == color[v]]
        es.add(rng.choice(same))
    es = [list(e) for e in es]
    rng.shuffle(es)
    return es


PROBLEMS.append(dict(
    id="graph-is-bipartite",
    title="Is Graph Bipartite?",
    difficulty=2,
    tags=["graph", "bfs", "coloring"],
    fn="is_bipartite",
    params=[["n", "int"], ["edges", "int[][]"]],
    returns="bool",
    espresso=False,
    statement=r"""
An undirected graph has vertices `0 … n-1` and the given `edges`. It is **bipartite** if
its vertices can be split into two groups so that every edge connects vertices from
different groups. Return whether it is bipartite. The graph may be disconnected.
""",
    constraints=["1 ≤ n ≤ 1000", "0 ≤ len(edges) ≤ 1501", "no self-loops or duplicate edges"],
    example_notes=[
        "A square 0–1–2–3–0: groups {0, 2} and {1, 3}.",
        "A triangle: any 2-colouring puts two adjacent vertices in the same group.",
    ],
    hints=[
        "Try to 2-colour the graph: once a vertex has a colour, its neighbours are forced.",
        "BFS from an uncoloured vertex, giving each newly discovered neighbour the opposite colour.",
        "A conflict (an edge between equal colours) means not bipartite. Remember to start a BFS in every component.",
    ],
    explanation=r"""
## Intuition

Bipartite = **2-colourable**. Colouring is forced: pick any vertex and make it colour 0;
its neighbours must be 1, their neighbours 0, and so on. If this forced propagation ever
asks an edge to join two vertices of the same colour, no colouring exists. Equivalently,
a graph is bipartite iff it has **no odd cycle**.

## Approach

1. `color = [-1] * n`; build the adjacency list.
2. For every vertex `s` still uncoloured (one per component), colour it 0 and BFS:
   - pop `u`; for each neighbour `v`: if uncoloured, give it `1 - color[u]` and push;
     if `color[v] == color[u]`, return `False`.
3. Return `True`.

```text
triangle 0-1-2-0:
color[0]=0, push 1 (color 1), push 2 (color 1)
pop 1: neighbour 2 has color 1 == color[1] -> not bipartite
```

## Complexity

- **Time O(V + E)**.
- **Space O(V + E)**.

## Common mistakes

- **Only searching from vertex 0**: other components go unchecked. One test is a
  bipartite component plus a separate triangle.
- **Colouring on pop instead of push**: a vertex could be pushed twice with different
  colours.
- **Assuming a tree-like input**: even cycles are fine, odd cycles are not.

## Going further

Union-find works too: for each vertex, union all its neighbours together; a conflict is
when a vertex ends up in the same set as one of its neighbours. Bipartite matching
(Hopcroft–Karp) and "split people who dislike each other into two groups" (*Possible
Bipartition*) build on this check.
""",
    solution=r'''
def is_bipartite(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    color = [-1] * n                     # -1: not coloured yet
    for s in range(n):
        if color[s] != -1:
            continue                     # already handled with its component
        color[s] = 0                     # free choice for a new component
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if color[v] == -1:
                    color[v] = 1 - color[u]   # forced: opposite of u
                    queue.append(v)
                elif color[v] == color[u]:
                    return False         # an edge inside one group: odd cycle
    return True
''',
    refs={
        "cpp": r'''
bool isBipartite(long long n, vector<vector<long long>>& edges) {
    vector<vector<int>> adj(n);
    for (auto& e : edges) { adj[e[0]].push_back(e[1]); adj[e[1]].push_back(e[0]); }
    vector<int> color(n, -1);
    for (int s = 0; s < n; s++) {
        if (color[s] != -1) continue;
        color[s] = 0;
        queue<int> q; q.push(s);
        while (!q.empty()) {
            int u = q.front(); q.pop();
            for (int v : adj[u]) {
                if (color[v] == -1) { color[v] = 1 - color[u]; q.push(v); }
                else if (color[v] == color[u]) return false;
            }
        }
    }
    return true;
}
''',
        "rust": r'''
use std::collections::VecDeque;

pub fn is_bipartite(n: i64, edges: Vec<Vec<i64>>) -> bool {
    let n = n as usize;
    let mut adj = vec![Vec::new(); n];
    for e in &edges {
        adj[e[0] as usize].push(e[1] as usize);
        adj[e[1] as usize].push(e[0] as usize);
    }
    let mut color = vec![-1i8; n];
    for s in 0..n {
        if color[s] != -1 { continue; }
        color[s] = 0;
        let mut q = VecDeque::from(vec![s]);
        while let Some(u) = q.pop_front() {
            for &v in &adj[u] {
                if color[v] == -1 { color[v] = 1 - color[u]; q.push_back(v); }
                else if color[v] == color[u] { return false; }
            }
        }
    }
    true
}
''',
    },
    tests=[
        [4, [[0, 1], [1, 2], [2, 3], [3, 0]]], [3, [[0, 1], [1, 2], [2, 0]]],
        [1, []], [2, [[0, 1]]], [7, [[0, 1], [1, 2], [2, 3], [4, 5], [5, 6], [6, 4]]],
        [5, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]], [6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]]],
        [200, _bip(_R, 200, 400, False)], [200, _bip(_R, 200, 400, True)],
        [1000, _bip(_R, 1000, 1500, False)], [1000, _bip(_R, 1000, 1500, True)],
    ],
))

# ---------------------------------------------------------------- 11. network delay


def _wdir(rng, n, m, wmax, base=1):
    es = set()
    tries = 0
    while len(es) < m and tries < 50 * m:
        tries += 1
        u, v = rng.sample(range(base, n + base), 2)
        es.add((u, v))
    return [[u, v, rng.randint(0, wmax)] for u, v in es]


def _reachable_wdir(rng, n, m, wmax, k):
    """Directed graph on 1..n where every node is reachable from k."""
    nodes = [k] + [v for v in range(1, n + 1) if v != k]
    es = {}
    for i in range(1, n):
        es[(nodes[rng.randrange(i)], nodes[i])] = rng.randint(0, wmax)
    while len(es) < m:
        u, v = rng.sample(range(1, n + 1), 2)
        es.setdefault((u, v), rng.randint(0, wmax))
    out = [[u, v, w] for (u, v), w in es.items()]
    rng.shuffle(out)
    return out


PROBLEMS.append(dict(
    id="graph-network-delay-time",
    title="Network Delay Time",
    difficulty=3,
    tags=["graph", "dijkstra", "heap", "shortest path"],
    fn="network_delay_time",
    params=[["times", "int[][]"], ["n", "int"], ["k", "int"]],
    returns="int",
    espresso=False,
    statement=r"""
A network has `n` nodes labelled `1 … n`. `times[i] = [u, v, w]` means a signal sent from
`u` reaches `v` after `w` time units (a **directed** edge, `w ≥ 0`). A signal is sent from
node `k`. Return the time it takes for **all** nodes to receive it, or `-1` if some node
never does.
""",
    constraints=["1 ≤ n ≤ 600", "0 ≤ len(times) ≤ 1500", "0 ≤ w ≤ 1000", "(u, v) pairs are distinct"],
    example_notes=[
        "From 2: node 1 at time 1, node 3 at 1, node 4 at 2 (via 3). The last one is at time 2.",
        "Node 2 sends nothing to node 1: unreachable.",
    ],
    hints=[
        "The time a node receives the signal is its shortest-path distance from k. The answer is the largest of these.",
        "Edges have different non-negative weights, so BFS is not enough: use Dijkstra.",
        "Min-heap of (distance, node). Pop the closest, skip stale entries, relax outgoing edges. Answer = max distance, or -1 if any is infinite.",
    ],
    explanation=r"""
## Intuition

The signal travels along every path simultaneously, so node `v` hears it at the length
of the **shortest** path `k → v`. All nodes have heard it once the *farthest* of them
has: the answer is `max(dist)`. Single-source shortest paths with non-negative weights
is the job description of **Dijkstra's algorithm**.

## Approach

1. Build `adj[u] = [(v, w), ...]`.
2. `dist[k] = 0`, everything else ∞; heap `[(0, k)]`.
3. Pop `(d, u)`. If `d > dist[u]`, the entry is stale (we already found a shorter way to
   `u`): skip it. Otherwise, for each `(v, w)`: if `d + w < dist[v]`, update and push.
4. If any `dist` is ∞ return `-1`, else `max(dist)`.

```text
times [[2,1,1],[2,3,1],[3,4,1]], k = 2
heap [(0,2)]          pop 2: dist1=1 dist3=1   heap [(1,1),(1,3)]
pop (1,1): no edges                            heap [(1,3)]
pop (1,3): dist4=2                             heap [(2,4)]
pop (2,4)             dist = {1:1, 2:0, 3:1, 4:2} -> answer 2
```

Why it works: when a node is popped with the smallest tentative distance, no other
route can beat it, because any other route would pass through a node that is already at
least as far away and weights are non-negative.

## Complexity

- **Time O((V + E) log V)** with a binary heap (each successful relaxation pushes once).
- **Space O(V + E)**.

## Common mistakes

- **Using BFS** (edge counts) instead of weights.
- **No stale-entry check**: still correct with lazy deletion, but re-relaxes edges from
  outdated pops and can be much slower.
- **Max-heap by accident** in C++ or Rust (see the intro for `greater<>` and `Reverse`).
- **1-based labels**: size arrays `n + 1` and ignore index 0 when taking the maximum.
- **Zero-weight edges** are allowed: Dijkstra handles them, but "mark visited on push"
  shortcuts from BFS do not.

## Going further

With negative edge weights Dijkstra breaks; Bellman-Ford (next problem's technique)
handles them in O(V·E). For all-pairs distances on small graphs, Floyd-Warshall is three
nested loops in O(V³).
""",
    solution=r'''
def network_delay_time(times, n, k):
    adj = [[] for _ in range(n + 1)]       # labels are 1..n
    for u, v, w in times:
        adj[u].append((v, w))
    INF = float('inf')
    dist = [INF] * (n + 1)
    dist[k] = 0
    heap = [(0, k)]                        # (distance so far, node), min-heap by distance
    while heap:
        d, u = heappop(heap)
        if d > dist[u]:
            continue                       # stale: u was finalised with a smaller d
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:               # found a faster route to v
                dist[v] = nd
                heappush(heap, (nd, v))
    worst = max(dist[1:])
    # The last node to hear the signal decides the answer.
    return -1 if worst == INF else worst
''',
    refs={
        "cpp": r'''
long long networkDelayTime(vector<vector<long long>>& times, long long n, long long k) {
    vector<vector<pair<int, long long>>> adj(n + 1);
    for (auto& t : times) adj[t[0]].push_back({(int)t[1], t[2]});
    const long long INF = LLONG_MAX;
    vector<long long> dist(n + 1, INF);
    // greater<> turns the default max-heap into a min-heap.
    priority_queue<pair<long long, int>, vector<pair<long long, int>>, greater<>> pq;
    dist[k] = 0;
    pq.push({0, (int)k});
    while (!pq.empty()) {
        auto [d, u] = pq.top(); pq.pop();
        if (d > dist[u]) continue;                   // stale entry
        for (auto [v, w] : adj[u])
            if (d + w < dist[v]) { dist[v] = d + w; pq.push({dist[v], v}); }
    }
    long long worst = *max_element(dist.begin() + 1, dist.end());
    return worst == INF ? -1 : worst;
}
''',
        "rust": r'''
use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn network_delay_time(times: Vec<Vec<i64>>, n: i64, k: i64) -> i64 {
    let n = n as usize;
    let mut adj: Vec<Vec<(usize, i64)>> = vec![Vec::new(); n + 1];
    for t in &times { adj[t[0] as usize].push((t[1] as usize, t[2])); }
    let mut dist = vec![i64::MAX; n + 1];
    let mut heap = BinaryHeap::new();
    dist[k as usize] = 0;
    heap.push(Reverse((0i64, k as usize)));          // Reverse => min-heap
    while let Some(Reverse((d, u))) = heap.pop() {
        if d > dist[u] { continue; }
        for &(v, w) in &adj[u] {
            if d + w < dist[v] {
                dist[v] = d + w;
                heap.push(Reverse((dist[v], v)));
            }
        }
    }
    let worst = *dist[1..].iter().max().unwrap();
    if worst == i64::MAX { -1 } else { worst }
}
''',
    },
    tests=[
        [[[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2], [[[1, 2, 1]], 2, 2], [[[1, 2, 1]], 2, 1],
        [[], 1, 1], [[[1, 2, 5], [1, 3, 1], [3, 2, 1], [2, 4, 0]], 4, 1],
        [[[1, 2, 0], [2, 3, 0], [3, 1, 0]], 3, 2],
        [_wdir(_R, 50, 200, 100), 50, 7], [_reachable_wdir(_R, 600, 1500, 1000, 1), 600, 1],
        [_wdir(_R, 600, 1200, 1000), 600, 300],
    ],
))

# ---------------------------------------------------------------- 12. cheapest flights

PROBLEMS.append(dict(
    id="graph-cheapest-flights-k-stops",
    title="Cheapest Flights Within K Stops",
    difficulty=3,
    tags=["graph", "bellman-ford", "shortest path", "dynamic programming"],
    fn="find_cheapest_price",
    params=[["n", "int"], ["flights", "int[][]"], ["src", "int"], ["dst", "int"], ["k", "int"]],
    returns="int",
    espresso=False,
    statement=r"""
There are `n` cities `0 … n-1`. `flights[i] = [from, to, price]` is a one-way flight.
Return the cheapest price from `src` to `dst` using **at most `k` stops** (intermediate
cities), i.e. at most `k + 1` flights. Return `-1` if no such route exists.
""",
    constraints=["2 ≤ n ≤ 300", "0 ≤ len(flights) ≤ 1200", "1 ≤ price ≤ 10⁴", "0 ≤ k < n", "src ≠ dst; no duplicate flights"],
    example_notes=[
        "0 → 1 → 3 costs 700 with one stop; 0 → 1 → 2 → 3 is cheaper (400) but needs two stops.",
        "With k = 0 only the direct flight 0 → 2 (500) is allowed.",
    ],
    hints=[
        "Plain Dijkstra finalises the cheapest price per city, but the cheapest route may use too many flights.",
        "Think in rounds: after round i, best[v] is the cheapest price using at most i flights.",
        "Bellman-Ford with k + 1 rounds. In each round relax every flight using the PREVIOUS round's prices (copy the array), so a round never chains two flights.",
    ],
    explanation=r"""
## Intuition

The stop limit breaks Dijkstra's key assumption: a city reached cheaply but with many
flights might be useless, while a pricier arrival with fewer flights can still continue.
Instead, think in **rounds of flights**. Let `best_i[v]` be the cheapest price to reach `v`
using at most `i` flights. Then

```text
best_{i+1}[v] = min(best_i[v],  min over flights (u→v, p) of best_i[u] + p)
```

That is exactly **Bellman-Ford**, stopped after `k + 1` rounds.

## Approach

1. `best = [∞] * n; best[src] = 0`.
2. Repeat `k + 1` times:
   - `nxt = best.copy()`;
   - for each flight `(u, v, p)` with `best[u] < ∞`: `nxt[v] = min(nxt[v], best[u] + p)`;
   - `best = nxt`.
3. Return `best[dst]` or `-1`.

```text
flights 0→1 100, 1→2 100, 2→3 200, 1→3 600, 0→2 500    src 0, dst 3, k 1
round 1 (≤1 flight):  best = [0, 100, 500, ∞]
round 2 (≤2 flights): best = [0, 100, 200, 700]   (0→1→3 = 700, 0→2→3 = 700)
answer 700  (400 would need 3 flights)
```

The **copy** is the crucial detail: reading from `best` while writing into `nxt`
guarantees each round adds at most one flight. Updating in place could relax
`0→1` and then `1→2` in the same round, sneaking in an extra flight.

## Complexity

- **Time O(k · E)**: `k + 1` rounds, each scanning every flight.
- **Space O(n)** for the two arrays.

## Common mistakes

- **In-place relaxation** (no copy): answers that use more than `k + 1` flights.
- **Off-by-one**: `k` stops means `k + 1` flights, hence `k + 1` rounds.
- **Plain Dijkstra with a visited set**: discards states that are more expensive but
  use fewer flights. (A Dijkstra over states `(city, flights used)` does work.)
- **Overflow from ∞ + price**: skip relaxations from unreachable cities.

## Going further

A BFS by levels (one level per flight, carrying prices) is the same algorithm in a
different costume. A modified Dijkstra over `(cost, city, stops)` with pruning by
"fewest stops seen so far per city" is often faster in practice.
""",
    solution=r'''
def find_cheapest_price(n, flights, src, dst, k):
    INF = float('inf')
    best = [INF] * n
    best[src] = 0                     # zero flights: only src is reachable
    # Round i computes the cheapest prices using at most i flights.
    for _ in range(k + 1):
        nxt = best[:]                 # read old prices, write new ones
        for u, v, price in flights:
            if best[u] != INF and best[u] + price < nxt[v]:
                # Using best[u] (not nxt[u]) guarantees one extra flight at most.
                nxt[v] = best[u] + price
        best = nxt
    return -1 if best[dst] == INF else best[dst]
''',
    refs={
        "cpp": r'''
long long findCheapestPrice(long long n, vector<vector<long long>>& flights, long long src, long long dst, long long k) {
    const long long INF = LLONG_MAX;
    vector<long long> best(n, INF);
    best[src] = 0;
    for (long long round = 0; round <= k; round++) {
        vector<long long> nxt = best;                // copy: one more flight per round
        for (auto& f : flights)
            if (best[f[0]] != INF && best[f[0]] + f[2] < nxt[f[1]])
                nxt[f[1]] = best[f[0]] + f[2];
        best.swap(nxt);
    }
    return best[dst] == INF ? -1 : best[dst];
}
''',
        "rust": r'''
pub fn find_cheapest_price(n: i64, flights: Vec<Vec<i64>>, src: i64, dst: i64, k: i64) -> i64 {
    let mut best = vec![i64::MAX; n as usize];
    best[src as usize] = 0;
    for _ in 0..=k {
        let mut nxt = best.clone();
        for f in &flights {
            let (u, v, p) = (f[0] as usize, f[1] as usize, f[2]);
            if best[u] != i64::MAX && best[u] + p < nxt[v] {
                nxt[v] = best[u] + p;
            }
        }
        best = nxt;
    }
    if best[dst as usize] == i64::MAX { -1 } else { best[dst as usize] }
}
''',
    },
    tests=[
        [4, [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]], 0, 3, 1],
        [3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 0],
        [3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 1],
        [3, [[0, 1, 100]], 0, 2, 2], [2, [], 0, 1, 1],
        [5, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 4, 1], [0, 4, 100]], 0, 4, 2],
        [5, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 4, 1], [0, 4, 100]], 0, 4, 3],
        [50, [[u, v, w + 1] for u, v, w in _wdir(_R, 50, 300, 500, 0)], 0, 49, 3],
        [300, [[u, v, w + 1] for u, v, w in _wdir(_R, 300, 1200, 9999, 0)], 5, 250, 4],
        [300, [[u, v, w + 1] for u, v, w in _wdir(_R, 300, 1200, 9999, 0)], 0, 299, 299],
    ],
))

# ---------------------------------------------------------------- 13. word ladder


def _ladder_tests():
    rng = random.Random(1313)
    t = []
    for L, alpha, m in ((3, "abc", 18), (4, "abcd", 120), (5, "abcde", 1500)):
        allw = ["".join(rng.choice(alpha) for _ in range(L)) for _ in range(m * 3)]
        words = sorted(set(allw))[:]
        rng.shuffle(words)
        words = words[:m]
        b = words[0]
        e = words[-1]
        t.append([b, e, words[1:]])
    return t


PROBLEMS.append(dict(
    id="graph-word-ladder",
    title="Word Ladder",
    difficulty=3,
    tags=["graph", "bfs", "strings"],
    fn="ladder_length",
    params=[["begin_word", "str"], ["end_word", "str"], ["word_list", "str[]"]],
    returns="int",
    statement=r"""
A **transformation sequence** from `begin_word` to `end_word` is a list of words where
each consecutive pair differs in **exactly one letter**, and every word after
`begin_word` belongs to `word_list`. Return the number of words in the **shortest**
such sequence (counting both ends), or `0` if none exists.

All words have the same length and consist of lowercase letters. `begin_word` need not be
in `word_list`; `begin_word ≠ end_word`.
""",
    constraints=["1 ≤ word length ≤ 5", "1 ≤ len(word_list) ≤ 1500", "words in word_list are distinct"],
    example_notes=[
        "hit → hot → dot → dog → cog: five words.",
        "`cog` is not in the list, so it can never be reached.",
    ],
    hints=[
        "Words are vertices; an edge joins two words that differ in one letter. What kind of shortest path is this?",
        "Unweighted shortest path: BFS from begin_word, counting words (levels).",
        "To find neighbours fast, try all 26 letters at every position and look the result up in a set, removing words from the set as soon as they are queued.",
    ],
    explanation=r"""
## Intuition

Each word is a vertex, and two words are adjacent if they differ in exactly one
position. Every step costs one word, so the shortest sequence is a **BFS** from
`begin_word`. The graph is implicit: generate neighbours on demand.

## Approach

1. Put `word_list` in a hash set `remaining`. If `end_word` is not in it, return 0.
2. BFS with entries `(word, length)`, starting at `(begin_word, 1)`.
3. For a popped word, for every position `i` and every letter `c`, form the candidate.
   If it is in `remaining`: if it equals `end_word` return `length + 1`; otherwise
   remove it from `remaining` (this is the visited mark) and enqueue it.
4. Queue exhausted: return 0.

```text
hit (1)
hot (2)                 h?t -> hot
dot, lot (3)            ?ot -> dot, lot
dog (4), log (4)        do? -> dog, lo? -> log
cog (5)  -> answer 5
```

**Neighbour generation trade-off.** Comparing the popped word against every remaining
word costs O(N·L) per pop, O(N²·L) total. Trying `26·L` single-letter mutations and
hashing each costs O(26·L²) per pop, which is far cheaper when N is large. Another option
is bucketing words by pattern (`h*t`, `*ot`, ...).

## Complexity

- **Time O(N · 26 · L²)** with mutations (L candidates per position, each hashed in O(L)).
- **Space O(N · L)** for the set and the queue.

## Common mistakes

- **Returning edges instead of words**: `hit → hot` is length 2.
- **Not removing words when enqueued**: the same word is re-queued from many parents,
  exploding the queue.
- **Assuming `begin_word` is in the list**: it may or may not be; it is never needed as a
  target.
- **C++/Rust strings**: mutate a copy of the word in place (`s[i] = c`), test, then
  restore the original character.

## Going further

**Bidirectional BFS** expands from both ends, always growing the smaller frontier, and
stops when they meet. The search radius roughly halves on each side, which for large
dictionaries is a dramatic speed-up. *Word Ladder II* asks for all shortest sequences.
""",
    solution=r'''
def ladder_length(begin_word, end_word, word_list):
    remaining = set(word_list)           # unvisited dictionary words
    if end_word not in remaining:
        return 0
    queue = deque([(begin_word, 1)])     # (word, words in the sequence so far)
    letters = 'abcdefghijklmnopqrstuvwxyz'
    while queue:
        word, length = queue.popleft()
        chars = list(word)
        for i in range(len(chars)):
            original = chars[i]
            for c in letters:
                if c == original:
                    continue
                chars[i] = c
                cand = ''.join(chars)
                if cand in remaining:
                    if cand == end_word:
                        return length + 1          # BFS: first arrival is shortest
                    remaining.remove(cand)         # mark visited on enqueue
                    queue.append((cand, length + 1))
            chars[i] = original                    # restore before the next position
    return 0
''',
    refs={
        "cpp": r'''
long long ladderLength(string beginWord, string endWord, vector<string>& wordList) {
    unordered_set<string> remaining(wordList.begin(), wordList.end());
    if (!remaining.count(endWord)) return 0;
    queue<pair<string, long long>> q;
    q.push({beginWord, 1});
    while (!q.empty()) {
        auto [word, len] = q.front(); q.pop();
        for (size_t i = 0; i < word.size(); i++) {
            char orig = word[i];
            for (char c = 'a'; c <= 'z'; c++) {
                if (c == orig) continue;
                word[i] = c;                         // mutate in place...
                if (remaining.count(word)) {
                    if (word == endWord) return len + 1;
                    remaining.erase(word);
                    q.push({word, len + 1});
                }
            }
            word[i] = orig;                          // ...and restore
        }
    }
    return 0;
}
''',
        "rust": r'''
use std::collections::{HashSet, VecDeque};

pub fn ladder_length(begin_word: String, end_word: String, word_list: Vec<String>) -> i64 {
    // Work with byte vectors: words are ASCII and easy to mutate this way.
    let mut remaining: HashSet<Vec<u8>> = word_list.into_iter().map(|w| w.into_bytes()).collect();
    let target = end_word.into_bytes();
    if !remaining.contains(&target) { return 0; }
    let mut q = VecDeque::from(vec![(begin_word.into_bytes(), 1i64)]);
    while let Some((mut word, len)) = q.pop_front() {
        for i in 0..word.len() {
            let orig = word[i];
            for c in b'a'..=b'z' {
                if c == orig { continue; }
                word[i] = c;
                if remaining.remove(&word) {         // true if it was unvisited
                    if word == target { return len + 1; }
                    q.push_back((word.clone(), len + 1));
                }
            }
            word[i] = orig;
        }
    }
    0
}
''',
    },
    tests=[
        ["hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]],
        ["hit", "cog", ["hot", "dot", "dog", "lot", "log"]],
        ["a", "c", ["a", "b", "c"]], ["hot", "dog", ["hot", "dog"]],
        ["hot", "dot", ["dot"]], ["abc", "xyz", ["abz", "ayz", "xyz", "abc"]],
    ] + _ladder_tests(),
))

# ---------------------------------------------------------------- 14. pacific atlantic

PROBLEMS.append(dict(
    id="grid-pacific-atlantic",
    title="Pacific Atlantic Water Flow",
    difficulty=3,
    tags=["graph", "grid", "bfs", "multi-source"],
    fn="pacific_atlantic",
    params=[["heights", "int[][]"]],
    returns="int[][]",
    statement=r"""
An island is a grid of cell heights. The **Pacific** ocean touches the top and left
edges; the **Atlantic** touches the bottom and right edges. Rain flows from a cell to a
4-directional neighbour whose height is **less than or equal** to its own, and from any
edge cell into the adjacent ocean(s).

Return the coordinates `[r, c]` of every cell from which water can reach **both**
oceans, sorted by row, then column.
""",
    constraints=["1 ≤ rows, cols ≤ 40", "0 ≤ heights[r][c] ≤ 10⁵"],
    example_notes=[
        "For instance (0,4) touches both oceans directly; (2,2) with height 5 drains down both sides.",
        "A single cell touches all four edges.",
    ],
    hints=[
        "Checking every cell with its own search costs O((R·C)²). Can you search from the oceans instead?",
        "Reverse the flow: from the ocean, water 'climbs' to neighbours with height ≥ the current cell.",
        "Multi-source BFS from all Pacific border cells, another from all Atlantic border cells; answer = cells reached by both.",
    ],
    explanation=r"""
## Intuition

Asking "where can water go from here?" for every cell repeats the same work over and
over. Flip the question: **which cells can the ocean reach going uphill?** Water flows
from `a` to a neighbour `b` when `height[b] ≤ height[a]`; so in reverse, from `b` you may
step to `a` when `height[a] ≥ height[b]`. Start a **multi-source** search from every cell
touching the Pacific, another from every cell touching the Atlantic, and intersect.

## Approach

1. `reach(starts)`: BFS from all `starts` at once, stepping to neighbours whose height is
   `≥` the current height; returns the visited set.
2. `pac = reach(top row + left column)`, `atl = reach(bottom row + right column)`.
3. Return `sorted(pac ∩ atl)` as `[r, c]` lists (row-major order).

```text
heights          pacific-reachable   atlantic-reachable   both
1 2 2 3 5        P P P P P           . . . . A            . . . . *
3 2 3 4 4        P P P P P           . . . A A            . . . * *
2 4 5 3 1        P P P . .           . . A A A            . . * . .
6 7 1 4 5        P P . . .           A A A A A            * * . . .
5 1 1 2 4        P . . . .           A A A A A            * . . . .
```

## Complexity

- **Time O(R·C)**: each search visits each cell at most once.
- **Space O(R·C)** for the two visited sets.

## Common mistakes

- **Wrong direction of the comparison**: in the reversed search you climb (`≥`), you do
  not descend.
- **Strict `>`**: equal heights let water flow (plateaus are allowed).
- **Unsorted output**: the expected answer is sorted row-major; build it by scanning
  rows and columns in order, which is sorted automatically.
- **Per-cell DFS** with a fresh visited set each time: O((R·C)²), too slow for big
  plateaus.

## Going further

The same "search from the targets" inversion solves *Surrounded Regions* (flood from the
border `O`s) and *Walls and Gates*. When each step has a cost, the inverted search
becomes a multi-source Dijkstra, as in *Trapping Rain Water II*.
""",
    solution=r'''
def pacific_atlantic(heights):
    rows, cols = len(heights), len(heights[0])

    def reach(starts):
        """Cells the ocean can 'climb' to from the given border cells."""
        seen = set(starts)
        queue = deque(starts)
        while queue:
            r, c = queue.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                # Reverse flow: water could run from (nr,nc) down to (r,c)
                # exactly when (nr,nc) is at least as high.
                if (0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen
                        and heights[nr][nc] >= heights[r][c]):
                    seen.add((nr, nc))
                    queue.append((nr, nc))
        return seen

    pacific = reach([(0, c) for c in range(cols)] + [(r, 0) for r in range(1, rows)])
    atlantic = reach([(rows - 1, c) for c in range(cols)] + [(r, cols - 1) for r in range(rows - 1)])
    # Scanning in row-major order yields the required sorted output.
    return [[r, c] for r in range(rows) for c in range(cols)
            if (r, c) in pacific and (r, c) in atlantic]
''',
    refs={
        "cpp": r'''
static vector<vector<char>> reachFrom(const vector<vector<long long>>& h, vector<pair<int, int>> starts) {
    int R = h.size(), C = h[0].size();
    vector<vector<char>> seen(R, vector<char>(C, 0));
    queue<pair<int, int>> q;
    for (auto [r, c] : starts) if (!seen[r][c]) { seen[r][c] = 1; q.push({r, c}); }
    const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1};
    while (!q.empty()) {
        auto [r, c] = q.front(); q.pop();
        for (int d = 0; d < 4; d++) {
            int nr = r + dr[d], nc = c + dc[d];
            if (nr >= 0 && nr < R && nc >= 0 && nc < C && !seen[nr][nc] && h[nr][nc] >= h[r][c]) {
                seen[nr][nc] = 1;                    // climb: reverse of downhill flow
                q.push({nr, nc});
            }
        }
    }
    return seen;
}

vector<vector<long long>> pacificAtlantic(vector<vector<long long>>& heights) {
    int R = heights.size(), C = heights[0].size();
    vector<pair<int, int>> pac, atl;
    for (int c = 0; c < C; c++) { pac.push_back({0, c}); atl.push_back({R - 1, c}); }
    for (int r = 0; r < R; r++) { pac.push_back({r, 0}); atl.push_back({r, C - 1}); }
    auto p = reachFrom(heights, pac), a = reachFrom(heights, atl);
    vector<vector<long long>> res;
    for (int r = 0; r < R; r++)
        for (int c = 0; c < C; c++)
            if (p[r][c] && a[r][c]) res.push_back({r, c});
    return res;
}
''',
        "rust": r'''
use std::collections::VecDeque;

fn reach(h: &Vec<Vec<i64>>, starts: Vec<(usize, usize)>) -> Vec<Vec<bool>> {
    let (rows, cols) = (h.len(), h[0].len());
    let mut seen = vec![vec![false; cols]; rows];
    let mut q = VecDeque::new();
    for (r, c) in starts {
        if !seen[r][c] { seen[r][c] = true; q.push_back((r, c)); }
    }
    while let Some((r, c)) = q.pop_front() {
        let mut nbrs = Vec::with_capacity(4);
        if r > 0 { nbrs.push((r - 1, c)); }
        if r + 1 < rows { nbrs.push((r + 1, c)); }
        if c > 0 { nbrs.push((r, c - 1)); }
        if c + 1 < cols { nbrs.push((r, c + 1)); }
        for (nr, nc) in nbrs {
            if !seen[nr][nc] && h[nr][nc] >= h[r][c] {
                seen[nr][nc] = true;
                q.push_back((nr, nc));
            }
        }
    }
    seen
}

pub fn pacific_atlantic(heights: Vec<Vec<i64>>) -> Vec<Vec<i64>> {
    let (rows, cols) = (heights.len(), heights[0].len());
    let mut pac = Vec::new();
    let mut atl = Vec::new();
    for c in 0..cols { pac.push((0, c)); atl.push((rows - 1, c)); }
    for r in 0..rows { pac.push((r, 0)); atl.push((r, cols - 1)); }
    let (p, a) = (reach(&heights, pac), reach(&heights, atl));
    let mut res = Vec::new();
    for r in 0..rows {
        for c in 0..cols {
            if p[r][c] && a[r][c] { res.push(vec![r as i64, c as i64]); }
        }
    }
    res
}
''',
    },
    tests=[
        [[[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], [2, 4, 5, 3, 1], [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]]],
        [[[1]]], [[[1, 2, 3]]], [[[3, 2, 1], [2, 1, 0], [1, 0, 0]]],
        [[[1, 1], [1, 1]]], [[[10, 10, 10], [10, 1, 10], [10, 10, 10]]],
        [[[_R.randint(0, 9) for _ in range(12)] for _ in range(9)]],
        [[[_R.randint(0, 100000) for _ in range(40)] for _ in range(40)]],
        [[[r + c for c in range(40)] for r in range(40)]],
        [[[5] * 40 for _ in range(40)]],
    ],
))

# ---------------------------------------------------------------- 15. MST


def _connected_weighted(rng, n, extra, wmax):
    es = {}
    for i in range(1, n):
        j = rng.randrange(i)
        es[(j, i)] = rng.randint(1, wmax)
    while len(es) < n - 1 + extra:
        u, v = sorted(rng.sample(range(n), 2))
        es.setdefault((u, v), rng.randint(1, wmax))
    out = [[u, v, w] for (u, v), w in es.items()]
    rng.shuffle(out)
    return out


PROBLEMS.append(dict(
    id="graph-minimum-spanning-tree",
    title="Minimum Spanning Tree Cost",
    difficulty=3,
    tags=["graph", "mst", "kruskal", "union-find", "greedy"],
    fn="min_spanning_tree_cost",
    params=[["n", "int"], ["edges", "int[][]"]],
    returns="int",
    espresso=False,
    statement=r"""
An undirected weighted graph has vertices `0 … n-1` and edges `[u, v, w]` (cost `w`).
Choose a subset of edges that connects **all** vertices with the minimum total cost (a
*minimum spanning tree*) and return that cost. If the graph is disconnected, return `-1`.
A single vertex costs `0`.
""",
    constraints=["1 ≤ n ≤ 600", "0 ≤ len(edges) ≤ 1500", "1 ≤ w ≤ 10⁶", "no self-loops; parallel edges may appear"],
    example_notes=[
        "Take 0–1 (1), 1–2 (2) and 2–3 (3). The 0–2 (4) and 0–3 (10) edges would only add cost.",
        "Vertex 2 has no edges: no spanning tree exists.",
    ],
    hints=[
        "A spanning tree on n vertices has exactly n - 1 edges and no cycle.",
        "Greedy works: consider edges from cheapest to most expensive and keep an edge unless it would create a cycle.",
        "Kruskal = sort by weight + union-find. Count accepted edges; fewer than n - 1 means disconnected.",
    ],
    explanation=r"""
## Intuition

Among all ways to connect everything, the cheapest never contains a cycle (drop the most
expensive cycle edge and stay connected), so it is a tree with `n - 1` edges. **Kruskal's
algorithm** builds it greedily: scan edges in increasing weight, keep an edge if it joins
two different components, skip it if both ends are already connected.

Why greedy is safe (the *cut property*): for any split of the vertices into two sides,
the cheapest edge crossing the split belongs to some MST. When Kruskal accepts an edge,
it is the cheapest edge leaving the component of one of its endpoints.

## Approach

1. Sort edges by weight.
2. Union-find over `n` vertices; `cost = 0`, `used = 0`.
3. For each `(u, v, w)`: if `union(u, v)` merges two components, `cost += w`, `used += 1`;
   stop early once `used == n - 1`.
4. Return `cost` if `used == n - 1`, else `-1`.

```text
edges sorted: (0,1,1) (1,2,2) (2,3,3) (0,2,4) (0,3,10)
(0,1,1) accept  {0,1}           cost 1
(1,2,2) accept  {0,1,2}         cost 3
(2,3,3) accept  {0,1,2,3}       cost 6   used = 3 = n-1 -> done
```

**Prim's algorithm** is the alternative: grow one tree from vertex 0, always adding the
cheapest edge leaving it (a min-heap of `(w, v)`), much like Dijkstra but keyed by the
single edge weight instead of the path length.

## Complexity

- **Kruskal: O(E log E)** for sorting; the union-find part is nearly linear.
- **Prim with a heap: O(E log V)**. Both use O(V + E) space.

## Common mistakes

- **Forgetting the disconnected case**: check that exactly `n - 1` edges were accepted.
- **Sorting by the wrong key** in C++/Rust: sort by `e[2]`, not lexicographically by `u`.
- **Parallel edges**: harmless for Kruskal, the cheaper copy is taken first and the
  other is skipped as a cycle.
- **n = 1**: zero edges needed, cost 0.

## Going further

The MST also minimises the **maximum** edge on the path between any two vertices
(*minimax paths*), which is why it shows up in clustering (stop Kruskal at k components)
and in "minimum effort path" problems.
""",
    solution=r'''
def min_spanning_tree_cost(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    cost = used = 0
    # Kruskal: cheapest edges first; keep one only if it joins two components.
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        ru, rv = find(u), find(v)
        if ru == rv:
            continue                  # would close a cycle: never needed
        parent[ru] = rv
        cost += w
        used += 1
        if used == n - 1:             # a spanning tree is complete
            break
    # Fewer than n-1 accepted edges: some vertex was never connected.
    return cost if used == n - 1 else -1
''',
    refs={
        "cpp": r'''
long long minSpanningTreeCost(long long n, vector<vector<long long>>& edges) {
    // Prim's algorithm with a min-heap of (weight, vertex).
    vector<vector<pair<int, long long>>> adj(n);
    for (auto& e : edges) {
        adj[e[0]].push_back({(int)e[1], e[2]});
        adj[e[1]].push_back({(int)e[0], e[2]});
    }
    vector<char> inTree(n, 0);
    priority_queue<pair<long long, int>, vector<pair<long long, int>>, greater<>> pq;
    pq.push({0, 0});
    long long cost = 0; int added = 0;
    while (!pq.empty() && added < n) {
        auto [w, u] = pq.top(); pq.pop();
        if (inTree[u]) continue;                     // already connected more cheaply
        inTree[u] = 1; cost += w; added++;
        for (auto [v, wv] : adj[u]) if (!inTree[v]) pq.push({wv, v});
    }
    return added == n ? cost : -1;
}
''',
        "rust": r'''
fn find(parent: &mut Vec<usize>, mut x: usize) -> usize {
    while parent[x] != x {
        parent[x] = parent[parent[x]];
        x = parent[x];
    }
    x
}

pub fn min_spanning_tree_cost(n: i64, edges: Vec<Vec<i64>>) -> i64 {
    let n = n as usize;
    let mut es = edges;
    es.sort_by_key(|e| e[2]);                        // Kruskal: cheapest first
    let mut parent: Vec<usize> = (0..n).collect();
    let (mut cost, mut used) = (0i64, 0usize);
    for e in &es {
        let (a, b) = (find(&mut parent, e[0] as usize), find(&mut parent, e[1] as usize));
        if a == b { continue; }
        parent[a] = b;
        cost += e[2];
        used += 1;
    }
    if used + 1 == n { cost } else { -1 }
}
''',
    },
    tests=[
        [4, [[0, 1, 1], [1, 2, 2], [2, 3, 3], [0, 2, 4], [0, 3, 10]]],
        [3, [[0, 1, 5]]], [1, []], [2, [[0, 1, 7], [0, 1, 3]]],
        [5, [[0, 1, 2], [0, 3, 6], [1, 2, 3], [1, 3, 8], [1, 4, 5], [2, 4, 7], [3, 4, 9]]],
        [4, [[0, 1, 1], [2, 3, 1]]],
        [60, _connected_weighted(_R, 60, 100, 50)],
        [600, _connected_weighted(_R, 600, 900, 10**6)],
        [600, _connected_weighted(_R, 599, 600, 10**6)],
    ],
))

# ---------------------------------------------------------------- 16. bridges


def _bridge_graph(rng, blocks, bsize):
    """Several cycles (with chords) linked by single bridge edges."""
    es = set()
    n = 0
    reps = []
    for _ in range(blocks):
        k = rng.randint(1, bsize)
        nodes = list(range(n, n + k))
        n += k
        if k >= 3:
            for i in range(k):
                a, b = nodes[i], nodes[(i + 1) % k]
                es.add((min(a, b), max(a, b)))
            for _ in range(k // 3):
                a, b = rng.sample(nodes, 2)
                es.add((min(a, b), max(a, b)))
        elif k == 2:
            es.add((nodes[0], nodes[1]))
        reps.append(nodes)
    for i in range(1, blocks):
        a = rng.choice(reps[i])
        b = rng.choice(reps[rng.randrange(i)])
        es.add((min(a, b), max(a, b)))
    perm = list(range(n))
    rng.shuffle(perm)
    out = [[perm[u], perm[v]] for u, v in es]
    rng.shuffle(out)
    return n, out


def _bridge_tests():
    rng = random.Random(1616)
    t = []
    for blocks, bsize in ((5, 4), (60, 8), (200, 10)):
        n, es = _bridge_graph(rng, blocks, bsize)
        t.append([n, es])
    return t


PROBLEMS.append(dict(
    id="graph-critical-connections",
    title="Critical Connections (Bridges)",
    difficulty=4,
    tags=["graph", "dfs", "tarjan", "bridges"],
    fn="critical_connections",
    params=[["n", "int"], ["connections", "int[][]"]],
    returns="int[][]",
    statement=r"""
A network has `n` servers `0 … n-1` connected by undirected `connections`. The network is
connected. A connection is **critical** (a *bridge*) if removing it disconnects some
servers from others.

Return all critical connections. Write each one as `[a, b]` with `a < b`, and sort the
list lexicographically.
""",
    constraints=["2 ≤ n ≤ 2000", "n - 1 ≤ len(connections) ≤ 3000", "no self-loops or duplicate connections; the graph is connected"],
    example_notes=[
        "0, 1, 2 form a cycle, so none of those edges is critical; 1–3 is the only way to reach 3.",
        "A simple path: every edge is a bridge.",
    ],
    hints=[
        "Removing each edge and testing connectivity is O(E·(V+E)). Think about what a DFS tree reveals instead.",
        "Non-tree (back) edges create cycles. A tree edge u→v is a bridge iff nothing in v's subtree has a back edge to u or above.",
        "Record discovery times tin[] and low[v] = the earliest tin reachable from v's subtree using one back edge. Tree edge (u, v) is a bridge iff low[v] > tin[u].",
    ],
    explanation=r"""
## Intuition

An edge is a bridge iff it lies on **no cycle**. Run a DFS: its tree edges plus the
remaining **back edges** (edges to an ancestor) describe all cycles, because every
non-tree edge in an undirected DFS goes to an ancestor. A tree edge `u → v` lies on a
cycle iff some vertex in `v`'s subtree has a back edge reaching `u` or higher.

Tarjan's trick measures "how high can the subtree reach" with timestamps:

- `tin[v]`: the time DFS first entered `v`.
- `low[v]`: the smallest `tin` reachable from `v`'s subtree using tree edges downward
  plus **at most one** back edge.

Then tree edge `(u, v)` is a bridge **iff `low[v] > tin[u]`**: the subtree of `v` cannot
reach `u` or anything above without that edge.

## Approach

```text
dfs(u, parent):
  tin[u] = low[u] = timer++
  for v in adj[u]:
    if v == parent: continue          # do not use the tree edge backwards
    if visited(v):  low[u] = min(low[u], tin[v])        # back edge
    else:
      dfs(v, u)
      low[u] = min(low[u], low[v])    # whatever v's subtree reaches, u reaches
      if low[v] > tin[u]: bridge (u, v)
```

Trace on `n = 4, [[0,1],[1,2],[2,0],[1,3]]`:

```text
       0           dfs 0 (tin 0) -> 1 (tin 1) -> 2 (tin 2)
      / \            2 sees 0 visited: low[2] = 0
     1---2           back in 1: low[1] = min(1, 0) = 0;  low[2]=0 > tin[1]=1? no
     |               1 -> 3 (tin 3): low[3] = 3 > tin[1] = 1 -> bridge (1,3)
     3               back in 0: low[1]=0 > tin[0]=0? no
```

Normalise each bridge to `[min, max]` and sort.

## Complexity

- **Time O(V + E)**: one DFS; sorting the bridges adds O(B log B).
- **Space O(V + E)** for the graph, plus recursion depth up to V.

## Common mistakes

- **Skipping the parent by vertex** works only without parallel edges (true here). With
  multi-edges, skip the parent *edge id* instead.
- **Using `low[v]` instead of `tin[v]` for back edges**: still finds bridges correctly in
  many implementations, but it is not the standard definition and breaks the closely
  related articulation-point algorithm. Use `tin[v]`.
- **`>=` instead of `>`**: `low[v] >= tin[u]` is the condition for **articulation
  points** (vertices), not bridges.
- **Recursion depth**: a long path of 1000 vertices recurses 1000 deep. Fine in C/C++/Rust
  and within the Python limit here; for much larger graphs write the DFS iteratively.

## Going further

Contract every 2-edge-connected component (vertices joined without bridges) to one node
and the bridges form a tree: the *bridge tree*. Articulation points use the same
`tin`/`low` with `low[v] >= tin[u]` (plus a special rule for the root).
""",
    solution=r'''
def critical_connections(n, connections):
    adj = [[] for _ in range(n)]
    for a, b in connections:
        adj[a].append(b)
        adj[b].append(a)
    tin = [-1] * n          # discovery time; -1 = not visited yet
    low = [0] * n           # earliest tin reachable from the subtree via one back edge
    timer = 0
    bridges = []

    def dfs(u, parent):
        nonlocal timer
        tin[u] = low[u] = timer
        timer += 1
        for v in adj[u]:
            if v == parent:
                continue                        # don't walk the tree edge backwards
            if tin[v] != -1:
                low[u] = min(low[u], tin[v])    # back edge to an ancestor
            else:
                dfs(v, u)
                low[u] = min(low[u], low[v])    # v's subtree reach counts for u
                if low[v] > tin[u]:
                    # Nothing below v climbs back to u or above: (u, v) is on no cycle.
                    bridges.append([min(u, v), max(u, v)])

    dfs(0, -1)              # the network is connected, so one DFS covers it
    bridges.sort()
    return bridges
''',
    refs={
        "cpp": r'''
static void bridgeDfs(int u, int parent, const vector<vector<int>>& adj, vector<int>& tin,
                      vector<int>& low, int& timer, vector<vector<long long>>& out) {
    tin[u] = low[u] = timer++;
    for (int v : adj[u]) {
        if (v == parent) continue;
        if (tin[v] != -1) low[u] = min(low[u], tin[v]);          // back edge
        else {
            bridgeDfs(v, u, adj, tin, low, timer, out);
            low[u] = min(low[u], low[v]);
            if (low[v] > tin[u]) out.push_back({min(u, v), max(u, v)});
        }
    }
}

vector<vector<long long>> criticalConnections(long long n, vector<vector<long long>>& connections) {
    vector<vector<int>> adj(n);
    for (auto& c : connections) { adj[c[0]].push_back(c[1]); adj[c[1]].push_back(c[0]); }
    vector<int> tin(n, -1), low(n, 0);
    int timer = 0;
    vector<vector<long long>> out;
    bridgeDfs(0, -1, adj, tin, low, timer, out);
    sort(out.begin(), out.end());
    return out;
}
''',
        "rust": r'''
struct Tarjan {
    adj: Vec<Vec<usize>>,
    tin: Vec<i64>,
    low: Vec<i64>,
    timer: i64,
    out: Vec<Vec<i64>>,
}

impl Tarjan {
    fn dfs(&mut self, u: usize, parent: usize) {
        self.tin[u] = self.timer;
        self.low[u] = self.timer;
        self.timer += 1;
        // Clone the neighbour list so `self` can be borrowed mutably inside the loop.
        let nbrs = self.adj[u].clone();
        for v in nbrs {
            if v == parent { continue; }
            if self.tin[v] != -1 {
                self.low[u] = self.low[u].min(self.tin[v]);       // back edge
            } else {
                self.dfs(v, u);
                self.low[u] = self.low[u].min(self.low[v]);
                if self.low[v] > self.tin[u] {
                    self.out.push(vec![u.min(v) as i64, u.max(v) as i64]);
                }
            }
        }
    }
}

pub fn critical_connections(n: i64, connections: Vec<Vec<i64>>) -> Vec<Vec<i64>> {
    let n = n as usize;
    let mut adj = vec![Vec::new(); n];
    for c in &connections {
        adj[c[0] as usize].push(c[1] as usize);
        adj[c[1] as usize].push(c[0] as usize);
    }
    let mut t = Tarjan { adj, tin: vec![-1; n], low: vec![0; n], timer: 0, out: Vec::new() };
    t.dfs(0, usize::MAX);
    t.out.sort();
    t.out
}
''',
    },
    tests=[
        [4, [[0, 1], [1, 2], [2, 0], [1, 3]]], [4, [[0, 1], [1, 2], [2, 3]]],
        [2, [[1, 0]]], [3, [[0, 1], [1, 2], [2, 0]]],
        [6, [[0, 1], [1, 2], [2, 0], [2, 3], [3, 4], [4, 5], [5, 3]]],
        [7, [[0, 1], [0, 2], [1, 3], [1, 4], [2, 5], [2, 6]]],
        [1000, [[i, i + 1] for i in range(999)]],
    ] + _bridge_tests(),
))
