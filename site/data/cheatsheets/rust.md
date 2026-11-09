# Rust cheat sheet

Quick reference for solving Crucible problems in Rust (edition 2021, `rustc -C opt-level=1`).
Your code is one file with no external crates; `std` has everything you need.

## How Crucible calls your function

You write a `pub fn` with the exact snake_case name and parameters from the starter.

| Crucible type | Rust parameter | return type |
|---|---|---|
| `int` | `i64` | `i64` |
| `float` | `f64` | `f64` |
| `bool` | `bool` | `bool` |
| `str` | `String` | `String` |
| `int[]` | `Vec<i64>` (owned: yours to change) | `Vec<i64>` |
| `float[]` / `str[]` | `Vec<f64>` / `Vec<String>` | same |
| `int[][]` | `Vec<Vec<i64>>` | `Vec<Vec<i64>>` |
| `list` | `Option<Box<ListNode>>` | same |
| `tree` | `Option<Rc<RefCell<TreeNode>>>` | same |
| `void` + mutates | `&mut Vec<i64>` | nothing |

```rust
pub fn sum_array(nums: Vec<i64>) -> i64 {
    nums.iter().sum()
}
pub fn move_zeroes(nums: &mut Vec<i64>) {        // mutated parameter: &mut
    let mut k = 0;
    for i in 0..nums.len() {
        if nums[i] != 0 { nums.swap(i, k); k += 1; }
    }
}
```

`io` problems: write `fn main()`, read all of stdin, print with `println!`.

```rust
use std::io::{self, Read, Write};
fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_ascii_whitespace().map(|t| t.parse::<i64>().unwrap());
    let n = it.next().unwrap() as usize;
    let nums: Vec<i64> = it.take(n).collect();
    let out = io::stdout();
    let mut out = io::BufWriter::new(out.lock());     // fast output for many lines
    writeln!(out, "{}", nums.iter().sum::<i64>()).unwrap();
}
```

## Variables & types

```rust
let x = 5;                    // immutable by default; inferred i32 unless used as i64
let mut total: i64 = 0;       // mut to reassign
let y = 3.5_f64;
let big = 1_i64 << 40;
let ok = true;
let c = 'a';                  // char: a 4-byte Unicode scalar
let (a, b) = (1, 2);          // tuple destructuring
const MOD: i64 = 1_000_000_007;
let idx = 3_usize;            // indices and lengths are usize
let n = 3_i64 as usize;       // explicit casts with `as` (no implicit widening)
let shadow = "5"; let shadow: i64 = shadow.parse().unwrap();   // shadowing
total += x + n as i64 + a + b + big + idx as i64 + shadow;
let _ = (y, ok, c, total);
```

## Operators

| op | note |
|---|---|
| `/` | integers truncate toward zero: `-7 / 2 == -3` |
| `%` | sign of the dividend: `-7 % 3 == -1`; `(-7_i64).rem_euclid(3) == 2` |
| `pow` | `2_i64.pow(10)`, `2.0_f64.powi(3)`, `x.sqrt()` |
| overflow | panics in debug, wraps in release. Use `checked_add`, `wrapping_mul`, `saturating_sub` to be explicit |
| `abs`, `min`, `max`, `clamp` | methods: `x.abs()`, `a.min(b)`, `v.clamp(lo, hi)` |
| bits | `& \| ^ ! << >>` (`!` is bitwise NOT on ints), `x.count_ones()`, `x.trailing_zeros()` |
| logic | `&& \|\| !` on `bool` only (no truthy integers) |

Mixed types never auto-convert: `a_i64 + b_usize` is an error. Cast with `as`.

## Conditionals & loops

```rust
let x = 7;
let kind = if x % 2 == 0 { "even" } else { "odd" };   // `if` is an expression
match x {
    0 => println!("zero"),
    1..=5 => println!("small"),
    n if n < 0 => println!("negative"),
    _ => println!("big {kind}"),
}
for i in 0..5 {}                       // 0..4
for i in (0..5).rev() {}               // 4..0
for i in (0..10).step_by(3) {}         // 0, 3, 6, 9
let v = vec![10, 20, 30];
for (i, x) in v.iter().enumerate() { let _ = (i, x); }
let mut n = 10;
while n > 0 { n /= 2; }
let found = loop { n += 1; if n == 3 { break n * 2; } };   // loop with a value
'outer: for i in 0..3 { for j in 0..3 { if i * j == 2 { break 'outer; } } }
let _ = found;
```

## Functions & closures

```rust
fn gcd(a: i64, b: i64) -> i64 { if b == 0 { a } else { gcd(b, a % b) } }   // last expr = return
fn bump(x: &mut i64) { *x += 1; }
fn total(v: &[i64]) -> i64 { v.iter().sum() }   // take slices: &Vec<i64> coerces to &[i64]

let sq = |v: i64| v * v;
let base = 10;
let add_base = |v: i64| v + base;                // borrows `base`
let mut count = 0;
let mut inc = || { count += 1; };                // FnMut: mutably borrows `count`
inc(); inc();
println!("{} {} {} {}", gcd(12, 18), sq(4), add_base(1), count);
```

Recursive helpers are plain nested `fn`s (they can't capture), so pass state in as
parameters: `fn dfs(i: usize, adj: &Vec<Vec<usize>>, seen: &mut Vec<bool>)`.

## Strings

`String` is owned and growable; `&str` is a borrowed view. Both are **UTF-8**, so you
can't index them with `s[i]`.

```rust
let s = String::from("Hello, World");
let n = s.len();                                // bytes, not chars
let bytes = s.as_bytes();                       // &[u8]: O(1) indexing for ASCII
let first = bytes[0] as char;                   // 'H'
let chars: Vec<char> = s.chars().collect();     // index chars freely
let sub = &s[7..12];                            // byte-range slice: "World"
let words: Vec<&str> = s.split(", ").collect();
let parts: Vec<&str> = "a b  c".split_whitespace().collect();
let mut t = String::new();
t.push('x'); t.push_str("yz"); t += "!";
let joined = vec!["a", "b"].join("-");
let rev: String = s.chars().rev().collect();
let up = s.to_uppercase();
let has = s.contains("World"); let pos = s.find('o');     // Option<usize>
let num: i64 = "42".parse().unwrap();
let text = format!("{}-{:>4}-{:.2}-{:b}", num, 7, 3.14159, 5);
let digit = ('7' as u8 - b'0') as i64;
let is_d = '7'.is_ascii_digit();
let _ = (n, first, chars, sub, words, parts, joined, rev, up, has, pos, text, digit, is_d);
```

## Vectors & slices

```rust
let mut a: Vec<i64> = vec![5, 3, 1];
let zeros = vec![0_i64; 10];
let mut grid = vec![vec![0_i64; 4]; 3];               // 3×4, rows are independent
grid[1][2] = 7;
a.push(4); a.pop();                                   // pop returns Option<i64>
a.insert(0, 9); a.remove(0);                          // O(n)
let last = *a.last().unwrap();
a.sort(); a.sort_unstable();                          // ascending
a.sort_by(|x, y| y.cmp(x));                           // descending
a.sort_by_key(|&x| (x % 3, x));                       // by key
a.reverse();
let mn = *a.iter().min().unwrap();
let mx = *a.iter().max().unwrap();
let sum: i64 = a.iter().sum();
let part_sum: i64 = a[1..3].iter().sum();             // &a[1..3] borrows a view, no copy
let copy = a[1..3].to_vec();                          // owned copy
let pos = a.iter().position(|&x| x == 3);             // Option<usize>
let doubled: Vec<i64> = a.iter().map(|x| x * 2).collect();
let evens: Vec<i64> = a.iter().filter(|&&x| x % 2 == 0).cloned().collect();
a.sort(); a.dedup();                                  // remove adjacent duplicates
let found = a.binary_search(&3);                      // Ok(i) or Err(insert_at)
a.swap(0, 1);
a.retain(|&x| x != 4);
a.extend_from_slice(&[7, 8]);
let _ = (zeros, last, mn, mx, sum, part_sum, copy, pos, doubled, evens, found);
```

## HashMap & HashSet

```rust
use std::collections::{BTreeMap, HashMap, HashSet};
let mut cnt: HashMap<i64, i64> = HashMap::new();
*cnt.entry(7).or_insert(0) += 1;                     // the counting idiom
let seven = cnt.get(&7).copied().unwrap_or(0);
if cnt.contains_key(&7) { cnt.remove(&7); }
for (k, v) in &cnt { let _ = (k, v); }
let mut groups: HashMap<usize, Vec<String>> = HashMap::new();
groups.entry(3).or_default().push("abc".to_string());
let mut seen = HashSet::new();
if !seen.insert(5) { /* was already present */ }
let has = seen.contains(&5);
let mut ordered = BTreeMap::new();                    // sorted keys
ordered.insert("b", 2); ordered.insert("a", 1);
let (k0, v0) = ordered.iter().next().unwrap();        // ("a", 1)
let _ = (seven, has, k0, v0);
```

## Stacks, queues, heaps

```rust
use std::collections::{BinaryHeap, VecDeque};
use std::cmp::Reverse;
let mut stack = vec![1, 2];
stack.push(3);
while let Some(top) = stack.pop() { let _ = top; }
let mut q = VecDeque::new();
q.push_back(1); q.push_front(0);
let front = q.pop_front();                       // Option
let mut max_heap = BinaryHeap::new();            // max on top
max_heap.push(5); max_heap.push(9);
let top = max_heap.peek().copied();              // Some(9)
let mut min_heap = BinaryHeap::new();
min_heap.push(Reverse((4_i64, 2_usize)));        // (dist, node) for Dijkstra
if let Some(Reverse((d, node))) = min_heap.pop() { let _ = (d, node); }
let _ = (front, top);
```

## Structs, enums, Option & Result

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
struct Point { x: i64, y: i64 }
impl Point {
    fn new(x: i64, y: i64) -> Self { Point { x, y } }
    fn norm1(&self) -> i64 { self.x.abs() + self.y.abs() }
}
let p = Point::new(3, -4);
let maybe: Option<i64> = Some(3);
let val = maybe.unwrap_or(0);                    // or match / if let
if let Some(v) = maybe { let _ = v; }
let r: Result<i64, _> = "12".parse::<i64>();
let parsed = match r { Ok(v) => v, Err(_) => -1 };
let doubled = maybe.map(|v| v * 2);              // Some(6)
println!("{:?} {} {} {} {:?}", p, p.norm1(), val, parsed, doubled);
```

`?` propagates `None`/`Err` out of a function returning `Option`/`Result`.

## Ownership & borrowing (the rules that cause compile errors)

1. Each value has **one owner**. `let b = a;` *moves* a `Vec`/`String`; `a` is then
   unusable. Plain numbers, `bool` and `char` are `Copy`, so they're copied instead.
2. You may have **either** many shared borrows (`&v`) **or** one mutable borrow
   (`&mut v`) at a time.
3. A borrow can't outlive what it points to.

```rust
let v = vec![1, 2, 3];
let w = v.clone();                 // explicit deep copy when you need two owners
let total: i32 = v.iter().sum();   // iter() borrows; v is still usable
let mut m = vec![3, 1, 2];
let first = m[0];                  // copy the value out (i32 is Copy)...
m.push(first);                     // ...so this mutable use is fine
let n = m.len();
m[n - 1] += 1;                     // compute indices before mutating
for x in m.iter_mut() { *x *= 2; } // mutate in place through &mut
let moved = w;                     // w moved; using w now would not compile
let _ = (total, moved);
```

## Linked lists & trees

```rust
#[derive(Debug)]
pub struct ListNode { pub val: i64, pub next: Option<Box<ListNode>> }   // provided by the harness
fn build(vals: &[i64]) -> Option<Box<ListNode>> {
    let mut head = None;
    for &v in vals.iter().rev() { head = Some(Box::new(ListNode { val: v, next: head })); }
    head
}
fn length(mut cur: &Option<Box<ListNode>>) -> usize {
    let mut n = 0;
    while let Some(node) = cur { n += 1; cur = &node.next; }
    n
}
```

Trees are `Option<Rc<RefCell<TreeNode>>>`: clone the `Rc` to share it (cheap, it's a
refcount), `.borrow()` to read fields, `.borrow_mut()` to change them.

```rust
use std::rc::Rc;
use std::cell::RefCell;
#[derive(Debug)]
pub struct TreeNode { pub val: i64, pub left: Option<Rc<RefCell<TreeNode>>>, pub right: Option<Rc<RefCell<TreeNode>>> }
fn depth(root: &Option<Rc<RefCell<TreeNode>>>) -> i64 {
    match root {
        None => 0,
        Some(n) => { let n = n.borrow(); 1 + depth(&n.left).max(depth(&n.right)) }
    }
}
```

## Common gotchas

- `v.len() - 1` on an empty vec underflows `usize` and panics. Check `is_empty()` first.
- Index with `usize`: `v[i as usize]`. Converting back: `i as i64`.
- `i32` is the default integer type; annotate (`0_i64`, `: i64`) when values get big.
- `.iter()` yields `&T`; patterns like `|&x|` or `.copied()` get the value.
- `sort()` needs `Ord`; `f64` isn't `Ord`. Use `v.sort_by(|a, b| a.partial_cmp(b).unwrap())`.
- `String` indexing is by **bytes**: use `as_bytes()` for ASCII, `chars()` otherwise.
- Integer overflow panics in debug builds, which is great for finding bugs.
- Borrow-checker fights in loops: index with `i` instead of holding references, or `clone()`.
