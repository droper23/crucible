// Rust reference for Crucible's editor (hover / completion / signature help).
const kw = (name, sig, doc, insert, example) => ({ name, kind: 'keyword', sig, doc, ...(insert ? { insert } : {}), ...(example ? { example } : {}) });
const m = (owner, name, sig, doc, extra = {}) => ({ name, owner, kind: 'method', sig, doc, ...extra });
const f = (owner, name, sig, doc, extra = {}) => ({ name, owner, kind: 'function', sig, doc, ...extra });
const mac = (name, sig, doc, extra = {}) => ({ name, kind: 'macro', sig, doc, ...extra });
const ty = (name, sig, doc, extra = {}) => ({ name, kind: 'type', sig, doc, ...extra });

const FMT = { label: 'fmt', doc: 'string literal with `{}` (Display), `{:?}` (Debug), `{:.2}`, `{:>5}`, inline `{x}`' };
const ARGS = { label: 'args', doc: 'values substituted into the `{}` placeholders, in order' };

const entries = [
  // ---------- keywords ----------
  kw('fn', 'fn name(arg: T) -> R { ... }', 'Declare a function. Crucible calls a `pub fn` with the exact snake_case name from the starter. The last expression (no `;`) is the return value.', 'fn ${1:name}(${2}) -> ${3:i64} {\n\t$0\n}', 'pub fn add(a: i64, b: i64) -> i64 {\n    a + b\n}'),
  kw('let', 'let [mut] name[: T] = expr;', 'Bind a variable. Bindings are immutable unless declared `mut`. Re-`let` with the same name *shadows* the old binding (can change its type).', 'let ${1:x} = ${2:value};', 'let n = nums.len();\nlet n = n as i64; // shadowing'),
  kw('mut', 'let mut x / &mut x', 'Marks a binding or reference as mutable. `&mut T` is an exclusive borrow: while it lives no other borrow of the same value may exist.', undefined, 'let mut count = 0;\ncount += 1;'),
  kw('if', 'if cond { ... } else { ... }', '`if` is an expression: `let y = if c { 1 } else { 2 };`. Condition must be `bool` (no truthiness: write `n != 0`). Both branches must have the same type.', 'if ${1:cond} {\n\t$0\n}', 'let sign = if x < 0 { -1 } else { 1 };'),
  kw('else', 'else { ... } / else if cond { ... }', 'Alternative branch of `if` / `if let`. Required when `if` is used as a value.', 'else {\n\t$0\n}', 'if x > 0 { pos += 1; } else if x < 0 { neg += 1; } else { zero += 1; }'),
  kw('match', 'match expr { pat => expr, _ => expr }', 'Pattern match; arms must be **exhaustive** (use `_` as catch-all). Supports ranges `1..=9`, alternatives `a | b`, guards `x if x > 0`, and bindings `n @ 1..=5`.', 'match ${1:expr} {\n\t${2:pat} => ${3:expr},\n\t_ => ${0:expr},\n}', 'match n % 3 {\n    0 => "fizz",\n    _ => "other",\n}'),
  kw('for', 'for pat in iterable { ... }', 'Loop over anything `IntoIterator`. `for x in v` **moves** `v` (consumes it); use `for x in &v` or `v.iter()` to borrow, `&mut v` to mutate in place. Ranges: `0..n` (exclusive), `0..=n` (inclusive), `(0..n).rev()`.', 'for ${1:i} in ${2:0..n} {\n\t$0\n}', 'for (i, x) in nums.iter().enumerate() { }'),
  kw('while', 'while cond { ... }', 'Loop while `cond` is true. Watch `usize` underflow: `while i >= 0` is always true for unsigned `i`.', 'while ${1:cond} {\n\t$0\n}', 'while lo < hi {\n    let mid = lo + (hi - lo) / 2;\n    if v[mid] < t { lo = mid + 1; } else { hi = mid; }\n}'),
  kw('loop', 'loop { ... }', 'Infinite loop; exit with `break`. `loop` can return a value: `let x = loop { break 5; };`.', 'loop {\n\t$0\n}', 'let mut n = 1;\nlet first = loop { n *= 2; if n > 100 { break n; } }; // 128'),
  kw('return', 'return expr;', 'Early return. Idiomatic Rust returns the final expression without `return` (and without a trailing `;`).', undefined, 'if nums.is_empty() { return 0; }'),
  kw('break', "break ['label] [value];", "Exit the innermost loop, or a labelled outer one: `'outer: for .. { for .. { break 'outer; } }`. In `loop`, `break v` yields a value.", undefined, "'outer: for i in 0..n {\n    for j in 0..m { if g[i][j] == 0 { break 'outer; } }\n}"),
  kw('continue', "continue ['label];", 'Skip to the next iteration of the innermost (or labelled) loop.', undefined, 'for &x in &v {\n    if x < 0 { continue; }\n    sum += x;\n}'),
  kw('struct', 'struct Name { field: T, ... }', 'Define a struct. Add `#[derive(Debug, Clone, PartialEq, Eq, Hash, PartialOrd, Ord)]` as needed (e.g. to print with `{:?}` or use as a HashMap key / heap element).', 'struct ${1:Name} {\n\t${2:field}: ${3:i64},\n}', '#[derive(Debug, Clone, Copy)]\nstruct Point { x: i64, y: i64 }\nlet p = Point { x: 1, y: 2 };'),
  kw('impl', 'impl Type { ... } / impl Trait for Type { ... }', 'Attach methods / associated functions to a type, or implement a trait. Methods take `&self`, `&mut self`, or `self`.', 'impl ${1:Type} {\n\t$0\n}', 'impl Point {\n    fn dist2(&self) -> i64 { self.x * self.x + self.y * self.y }\n}'),
  kw('enum', 'enum Name { A, B(T), C { x: T } }', 'Tagged union. Variants may carry data; consume with `match`.', 'enum ${1:Name} {\n\t${2:A},\n}', 'enum Op { Push(i64), Pop }\nlet op = Op::Push(3);'),
  kw('trait', 'trait Name { fn method(&self) -> T; }', 'Define shared behaviour (like an interface). Implement with `impl Name for Type`.', 'trait ${1:Name} {\n\t$0\n}', 'trait Area { fn area(&self) -> f64; }\nimpl Area for Circle { fn area(&self) -> f64 { 3.14 * self.r * self.r } }'),
  kw('use', 'use path::to::Item;', 'Bring items into scope. Common: `use std::collections::{HashMap, HashSet, VecDeque, BinaryHeap};`, `use std::cmp::{min, max, Reverse, Ordering};`.', 'use std::collections::${1:HashMap};', 'use std::collections::{HashMap, HashSet};\nuse std::cmp::Reverse;'),
  kw('pub', 'pub fn / pub struct / pub field', 'Make an item public. Crucible calls your solution function, so it must be `pub fn`.', undefined, 'pub fn solve(nums: Vec<i64>) -> i64 { nums.iter().sum() }'),
  kw('ref', 'let ref x = v; / Some(ref x) =>', 'In a pattern, bind by reference instead of moving. Usually you can instead match on a reference (`match &opt { Some(x) => .. }`).', undefined, 'if let Some(ref s) = name { println!("{}", s); } // name still usable'),
  kw('as', 'expr as Type', 'Primitive cast: `x as usize`, `c as u8`, `b as char` (u8 only), `f as i64` (truncates toward zero, saturates). **Silently wraps/truncates** for integer narrowing, and `-1i64 as usize` becomes a huge number.', undefined, "let idx = (c as u8 - b'a') as usize;"),
  kw('if let', 'if let Pat = expr { ... } else { ... }', 'Match one pattern, typically `Some(x)` / `Ok(x)`. Gotcha: in edition 2021 a temporary (e.g. a `RefCell` borrow) in the scrutinee lives until the end of the whole `if let`/`else`.', 'if let Some(${1:x}) = ${2:opt} {\n\t$0\n}', 'if let Some(&v) = map.get(&k) { total += v; }'),
  kw('while let', 'while let Pat = expr { ... }', 'Loop while the pattern matches. The classic stack/queue/heap drain loop.', 'while let Some(${1:x}) = ${2:stack}.pop() {\n\t$0\n}', 'while let Some(node) = queue.pop_front() { }'),
  kw('?', 'expr?', 'Propagate errors: on `Err(e)` / `None` return it early from the enclosing function, otherwise unwrap the value. Only usable inside a function returning `Result` (or `Option`) — not in a plain `-> i64` solution.', undefined, 'fn parse_sum(a: &str, b: &str) -> Result<i64, std::num::ParseIntError> {\n    Ok(a.trim().parse::<i64>()? + b.trim().parse::<i64>()?)\n}'),
  kw('Self', 'Self', 'Inside an `impl`, the implementing type itself: `fn new() -> Self { Self { .. } }`.', undefined, 'impl Point {\n    fn origin() -> Self { Self { x: 0, y: 0 } }\n}'),
  kw('self', '&self / &mut self / self', 'The receiver of a method. `&self` borrows, `&mut self` borrows mutably, `self` takes ownership. Also `self::` for the current module path.', undefined, 'impl Counter {\n    fn inc(&mut self) { self.n += 1; }\n}'),
  kw('move', 'move |args| body', 'Closure captures variables by value (moves them in) instead of borrowing.', undefined, 'let k = 3;\nlet add_k = move |x: i64| x + k;'),
  kw('const', 'const NAME: T = value;', 'Compile-time constant; type annotation required. Also `const fn`.', 'const ${1:MOD}: ${2:i64} = ${3:1_000_000_007};', 'const MOD: i64 = 1_000_000_007;'),
  kw('static', 'static NAME: T = value;', 'Global with a fixed address. `static mut` needs `unsafe` to access; prefer passing state explicitly.', undefined, 'static DIRS: [(i64, i64); 4] = [(0, 1), (1, 0), (0, -1), (-1, 0)];'),
  kw('unsafe', 'unsafe { ... }', 'Opt out of some compiler checks (raw pointers, `static mut`, FFI). Not needed for normal Crucible solutions.', undefined, 'let x = unsafe { *v.get_unchecked(0) };'),
  kw('true', 'true', '`bool` literal.', undefined, 'let mut found = true;'),
  kw('false', 'false', '`bool` literal.', undefined, 'let mut visited = vec![false; n];'),
  kw('mod', 'mod name { ... }', 'Declare a module (namespace).', undefined, 'mod util {\n    pub fn gcd(a: i64, b: i64) -> i64 { if b == 0 { a } else { gcd(b, a % b) } }\n}'),
  kw('type', 'type Alias = T;', 'Type alias, e.g. `type Grid = Vec<Vec<i64>>;`.', undefined, 'type Grid = Vec<Vec<i64>>;'),
  kw('where', 'fn f<T>(x: T) where T: Ord', 'Trait bounds clause for generics.', undefined, 'fn largest<T>(v: &[T]) -> &T where T: Ord {\n    v.iter().max().unwrap()\n}'),
  kw('dyn', 'Box<dyn Trait>', 'Trait object (dynamic dispatch).', undefined, 'let f: Box<dyn Fn(i64) -> i64> = Box::new(|x| x * 2);'),
  kw('in', 'for x in iter', 'Part of `for` loop syntax.', undefined, 'for i in 0..n { }'),
  { name: 'Some', owner: 'Option', kind: 'function', sig: 'Some(value: T) -> Option<T>', params: [{ label: 'value', doc: 'the contained value' }], returns: 'Option<T> — the present variant wrapping value', doc: 'The present variant of `Option`. Pattern `Some(x)` binds the inner value.', example: 'if let Some(x) = v.pop() { }' },
  { name: 'None', owner: 'Option', kind: 'constant', sig: 'None: Option<T>', doc: 'The absent variant of `Option`. Rust has no null; use `Option` instead.', example: 'let mut best: Option<i64> = None;' },
  { name: 'Ok', owner: 'Result', kind: 'function', sig: 'Ok(value: T) -> Result<T, E>', params: [{ label: 'value', doc: 'the success value' }], returns: 'Result<T, E> — the success variant wrapping value', doc: 'Success variant of `Result`.', example: 'fn half(x: i64) -> Result<i64, String> {\n    if x % 2 == 0 { Ok(x / 2) } else { Err(format!("{} is odd", x)) }\n}' },
  { name: 'Err', owner: 'Result', kind: 'function', sig: 'Err(error: E) -> Result<T, E>', params: [{ label: 'error', doc: 'the error value' }], returns: 'Result<T, E> — the error variant wrapping error', doc: 'Error variant of `Result`.', example: 'match "x".parse::<i64>() {\n    Ok(n) => println!("{}", n),\n    Err(e) => println!("bad: {}", e),\n}' },

  // ---------- macros ----------
  mac('println!', 'println!(fmt, args...)', 'Print to stdout with newline. `{}` Display, `{:?}` Debug (Vec, Option), `{:.3}` 3 decimals, `{:>5}` right-align. Inline names: `{x}`. For lots of output, use a `BufWriter` + `writeln!` instead.', { params: [FMT, ARGS], returns: '()', insert: 'println!("{}", ${1:x});', example: 'println!("{} {:?} {:.2}", n, v, f); // 3 [1, 2] 0.50', learn: {
      summary: "print a line of formatted text",
      what: "println! prints text to standard output followed by a newline. The ! means it is a macro (code that is expanded when compiling) rather than a normal function, but you call it the same way. The first argument must be a string literal; each {} in it is a placeholder filled by the next argument, and you can also put a variable name directly inside the braces, like {x}. {:?} prints the \"debug\" form, which works for vectors and Options.",
      params: {
        fmt: "a string literal with {} placeholders, e.g. \"{} + {} = {}\"",
        "args...": "the values that fill the placeholders, in order, e.g. a, b, a + b"
      },
      returns: "Nothing (the unit value ()). It is used only for its output.",
      example: "let lives = 3;                 // a value to show\nprintln!(\"lives: {}\", lives);  // lives: 3\nprintln!(\"{lives} left\");      // 3 left (variable named inside braces)\nprintln!(\"{:?}\", vec![1, 2]);  // [1, 2] (debug form)",
      watch: [
        "The first argument must be a literal: println!(s) with a String variable fails; write println!(\"{}\", s).",
        "To print a literal brace, double it: {{ or }}."
      ]
    }  }),
  mac('print!', 'print!(fmt, args...)', 'Like `println!` without the newline. Stdout is line-buffered, so flush (`io::stdout().flush()`) if needed.', { params: [FMT, ARGS], returns: '()', insert: 'print!("{} ", ${1:x});', example: 'for x in &v { print!("{} ", x); }\nprintln!();' }),
  mac('eprintln!', 'eprintln!(fmt, args...)', 'Print to stderr: good for debugging without corrupting expected output.', { params: [FMT, ARGS], returns: '()', insert: 'eprintln!("{:?}", ${1:x});', example: 'eprintln!("dp = {:?}", dp);' }),
  mac('format!', 'format!(fmt, args...) -> String', 'Build a `String` using the same syntax as `println!`.', { params: [FMT, ARGS], returns: 'String — the formatted text', insert: 'format!("{}", ${1:x})', example: 'let s = format!("{}-{}", 3, 7); // "3-7"' }),
  mac('write!', 'write!(dest, fmt, args...) -> Result', 'Format into a `String` (needs `use std::fmt::Write`) or an `io::Write` like `BufWriter` (needs `use std::io::Write`).', { params: [{ label: 'dest', doc: 'a String or io::Write (e.g. BufWriter)' }, FMT, ARGS], returns: 'fmt::Result / io::Result<()> — usually `.unwrap()`ed', insert: 'write!(${1:out}, "{}", ${2:x}).unwrap();', example: 'use std::fmt::Write;\nlet mut s = String::new();\nwrite!(s, "{} ", 42).unwrap(); // s == "42 "' }),
  mac('writeln!', 'writeln!(dest, fmt, args...) -> Result', 'Like `write!` plus newline. The fast-output idiom: `BufWriter` around a locked stdout.', { params: [{ label: 'dest', doc: 'a String or io::Write (e.g. BufWriter)' }, FMT, ARGS], returns: 'fmt::Result / io::Result<()> — usually `.unwrap()`ed', insert: 'writeln!(${1:out}, "{}", ${2:x}).unwrap();', example: 'use std::io::{self, BufWriter, Write};\nlet mut out = BufWriter::new(io::stdout().lock());\nwriteln!(out, "{}", ans).unwrap();' }),
  mac('vec!', 'vec![a, b, c] / vec![value; n]', 'Create a `Vec`. `vec![0; n]` repeats a value (cloned). 2-D: `vec![vec![0; m]; n]`.', { returns: 'Vec<T> — the new vector', insert: 'vec![${1:0}; ${2:n}]', example: 'let mut dp = vec![vec![0i64; m + 1]; n + 1];\nlet v = vec![3, 1, 2];' }),
  mac('assert!', 'assert!(cond, fmt, args...)', 'Panic if `cond` is false; the message part is optional.', { params: [{ label: 'cond', doc: 'bool that must hold' }, { label: 'fmt', doc: 'optional panic message (format string)' }, ARGS], returns: '() — or panics', insert: 'assert!(${1:cond});', example: 'assert!(lo <= hi, "bad range {}..{}", lo, hi);' }),
  mac('assert_eq!', 'assert_eq!(left, right)', 'Panic (showing both values) if `left != right`. Types must implement `PartialEq + Debug`.', { params: [{ label: 'left', doc: 'actual value' }, { label: 'right', doc: 'expected value' }], returns: '() — or panics', insert: 'assert_eq!(${1:a}, ${2:b});', example: 'assert_eq!(gcd(12, 18), 6);' }),
  mac('assert_ne!', 'assert_ne!(left, right)', 'Panic if `left == right`.', { params: [{ label: 'left', doc: 'value' }, { label: 'right', doc: 'value it must differ from' }], returns: '() — or panics', insert: 'assert_ne!(${1:a}, ${2:b});', example: 'assert_ne!(divisor, 0);' }),
  mac('panic!', 'panic!(fmt, args...)', 'Abort the current thread with a message. Return type is `!`, so it fits any branch.', { params: [FMT, ARGS], returns: '! — never returns', insert: 'panic!("${1:msg}")', example: 'if n < 0 { panic!("negative n: {}", n); }' }),
  mac('unreachable!', 'unreachable!()', 'Panic marking code that should never run; handy for exhaustive `match` arms.', { returns: '! — never returns (panics if reached)', insert: 'unreachable!()', example: 'match d { 0 => up(), 1 => down(), _ => unreachable!() }' }),
  mac('todo!', 'todo!()', 'Placeholder that panics; lets unfinished code compile.', { returns: '! — never returns (panics if reached)', insert: 'todo!()', example: 'pub fn solve(nums: Vec<i64>) -> i64 {\n    todo!()\n}' }),
  mac('dbg!', 'dbg!(expr) -> T', 'Print `file:line expr = value` to **stderr** and return the value (moves it; use `dbg!(&x)` to keep ownership).', { params: [{ label: 'expr', doc: 'expression to print and pass through' }], returns: 'T — the value of expr, unchanged', insert: 'dbg!(&${1:x})', example: 'let mid = dbg!(lo + (hi - lo) / 2);' }),
  mac('matches!', 'matches!(expr, pattern) -> bool', 'True if `expr` matches the pattern (guards allowed).', { params: [{ label: 'expr', doc: 'value to test' }, { label: 'pattern', doc: 'pattern, e.g. `\'a\'..=\'z\'` or `Some(_)`' }], returns: 'bool — whether expr matches pattern', insert: "matches!(${1:c}, ${2:'a'..='z'})", example: "if matches!(c, 'a' | 'e' | 'i' | 'o' | 'u') { }" }),

  // ---------- Vec ----------
  ty('Vec', 'Vec<T>', 'Growable array (heap-allocated). Index with `usize`: `v[i]` panics if out of bounds; `v.get(i)` returns `Option<&T>`. Derefs to a slice, so all slice methods work.', { example: 'let mut v: Vec<i64> = Vec::new();\nv.push(4);\nlet x = v[0]; // 4' }),
  f('Vec', 'new', 'Vec::new() -> Vec<T>', 'Empty vector (no allocation until first push).', { insert: 'Vec::new()', returns: 'Vec<T> — an empty vector', example: 'let mut stack: Vec<usize> = Vec::new();' }),
  f('Vec', 'with_capacity', 'Vec::with_capacity(capacity) -> Vec<T>', 'Empty vector with space for `capacity` elements: avoids reallocations. `len()` is still 0, so index with `push`, not `v[i]`.', { params: [{ label: 'capacity', doc: 'number of elements to reserve' }], returns: 'Vec<T> — empty, with reserved capacity', example: 'let mut out = Vec::with_capacity(n);\nfor i in 0..n { out.push(i * i); }' }),
  m('Vec', 'push', 'v.push(value)', 'Append to the end. **Amortised O(1)**. Needs `let mut v`.', { params: [{ label: 'value', doc: 'element to append' }], returns: '()', example: 'let mut v = vec![1, 2];\nv.push(3); // [1, 2, 3]' }),
  m('Vec', 'pop', 'v.pop() -> Option<T>', 'Remove and return the last element, or `None` if empty. O(1). Use as a stack with `while let Some(x) = st.pop()`.', { returns: 'Option<T> — Some(last element), or None if empty', example: 'let mut v = vec![1, 2, 3];\nlet top = v.pop(); // Some(3), v == [1, 2]' }),
  m('Vec', 'insert', 'v.insert(index, element)', 'Insert at `index`, shifting later elements right. **O(n)**. Panics if `index > len`.', { params: [{ label: 'index', doc: 'position (0..=len)' }, { label: 'element', doc: 'value to insert' }], returns: '()', example: 'let mut v = vec![1, 3];\nv.insert(1, 2); // [1, 2, 3]' }),
  m('Vec', 'remove', 'v.remove(index) -> T', 'Remove and return element at `index`, shifting the rest left. **O(n)**: use `swap_remove` if order does not matter, or a `VecDeque` for front removal. Panics if out of bounds.', { params: [{ label: 'index', doc: 'position to remove' }], returns: 'T — the removed element', example: 'let mut v = vec![10, 20, 30];\nlet x = v.remove(0); // 10, v == [20, 30]' }),
  m('Vec', 'swap_remove', 'v.swap_remove(index) -> T', 'Remove element at `index` by replacing it with the last one. O(1) but changes order.', { params: [{ label: 'index', doc: 'position to remove' }], returns: 'T — the removed element', example: 'let mut v = vec![1, 2, 3, 4];\nv.swap_remove(0); // v == [4, 2, 3]' }),
  m('Vec', 'clear', 'v.clear()', 'Remove all elements (keeps capacity).', { returns: '()', example: 'buf.clear(); // len 0, capacity kept' }),
  m('Vec', 'truncate', 'v.truncate(len)', 'Keep only the first `len` elements (no-op if already shorter).', { params: [{ label: 'len', doc: 'new length' }], returns: '()', example: 'let mut v = vec![1, 2, 3, 4];\nv.truncate(2); // [1, 2]' }),
  m('Vec', 'resize', 'v.resize(new_len, value)', 'Grow (filling with clones of `value`) or shrink to `new_len`.', { params: [{ label: 'new_len', doc: 'target length' }, { label: 'value', doc: 'fill value' }], returns: '()', example: 'let mut v = vec![1, 2];\nv.resize(4, 0); // [1, 2, 0, 0]' }),
  m('Vec', 'extend', 'v.extend(iter)', 'Append every item of an iterator / collection.', { params: [{ label: 'iter', doc: 'items to append' }], returns: '()', example: 'let mut v = vec![1];\nv.extend(vec![2, 3]); // [1, 2, 3]\nv.extend(0..2);      // [1, 2, 3, 0, 1]' }),
  m('Vec', 'extend_from_slice', 'v.extend_from_slice(other)', 'Append clones of all elements of a slice.', { params: [{ label: 'other', doc: 'slice to copy from' }], returns: '()', example: 'let mut v = vec![1];\nv.extend_from_slice(&[2, 3]); // [1, 2, 3]' }),
  m('Vec', 'append', 'v.append(other)', 'Move all elements of `other: &mut Vec<T>` into `v`, leaving `other` empty.', { params: [{ label: 'other', doc: '&mut Vec to drain' }], returns: '()', example: 'let mut a = vec![1];\nlet mut b = vec![2, 3];\na.append(&mut b); // a == [1, 2, 3], b == []' }),
  m('Vec', 'drain', 'v.drain(range) -> Drain<T>', 'Remove a range and iterate over the removed elements. `v.drain(..)` empties it.', { params: [{ label: 'range', doc: 'e.g. ..k or i..j' }], returns: 'Drain<T> — iterator over the removed elements (owned)', example: 'let mut v = vec![1, 2, 3, 4];\nlet front: Vec<i64> = v.drain(..2).collect(); // [1, 2], v == [3, 4]' }),
  m('Vec', 'retain', 'v.retain(f)', 'Keep only elements where `f(&x)` is true, in place. O(n).', { params: [{ label: 'f', doc: 'predicate |&x| -> bool' }], returns: '()', example: 'let mut v = vec![0, 1, 0, 2];\nv.retain(|&x| x != 0); // [1, 2]' }),
  m('Vec', 'dedup', 'v.dedup()', 'Remove **consecutive** duplicates. Sort first to remove all duplicates.', { returns: '()', example: 'let mut v = vec![3, 1, 3, 1, 1];\nv.sort();\nv.dedup(); // [1, 3]' }),
  m('Vec', 'split_off', 'v.split_off(at) -> Vec<T>', 'Split into `[0, at)` (kept) and `[at, len)` (returned).', { params: [{ label: 'at', doc: 'split index' }], returns: 'Vec<T> — the tail [at, len)', example: 'let mut v = vec![1, 2, 3, 4];\nlet tail = v.split_off(2); // v == [1, 2], tail == [3, 4]' }),
  m('Vec', 'is_empty', 'v.is_empty() -> bool', 'True if `len() == 0`.', { returns: 'bool — true if there are no elements', example: 'if stack.is_empty() { return false; }' }),
  m('Vec', 'capacity', 'v.capacity() -> usize', 'Allocated slots (>= len).', { returns: 'usize — number of elements storable without reallocating', example: 'let v: Vec<i64> = Vec::with_capacity(10);\nassert!(v.capacity() >= 10);' }),

  // ---------- slice ----------
  ty('slice', '[T] / &[T] / &mut [T]', 'A view into contiguous elements (`Vec`, array). Take one with `&v[a..b]`. Pass `&[i64]` instead of `&Vec<i64>` for flexibility.', { example: 'fn total(s: &[i64]) -> i64 { s.iter().sum() }\nlet mid = total(&v[1..3]);' }),
  m('slice', 'len', 's.len() -> usize', 'Number of elements. Returns **usize**: `s.len() - 1` panics (debug) / wraps when empty; cast to `i64` for signed math.', { returns: 'usize — number of elements', example: 'let n = v.len();\nlet last = v[n - 1]; // panics if v is empty', learn: {
      summary: "number of elements",
      what: "len is called with a dot on a slice, array or Vec (and also on strings) and tells you how many elements it holds. It is instant (O(1)) because the length is stored with the data. The answer is a usize, Rust's unsigned (never negative) integer type used for sizes and indexes, so the valid indexes are 0 through len() - 1.",
      params: {
        s: "the slice, array or vector you call it on, before the dot"
      },
      returns: "A usize: the number of elements. Use it for loop bounds (0..v.len()) and the last index, v.len() - 1.",
      example: "let marks = [70, 85, 92];           // an array of 3 numbers\nprintln!(\"{}\", marks.len());        // 3\nlet last = marks[marks.len() - 1];  // 92, the last element",
      watch: [
        "usize can't go negative: v.len() - 1 on an empty v panics (overflow). Check v.is_empty() first.",
        "Mixing with i32 needs a cast: i as usize, or v.len() as i32.",
        "On a String, len() counts bytes, not characters."
      ]
    }  }),
  m('slice', 'is_empty', 's.is_empty() -> bool', 'True if there are no elements.', { returns: 'bool — true if len() == 0', example: 'if nums.is_empty() { return 0; }' }),
  m('slice', 'sort', 's.sort()', 'Stable sort ascending, in place. **O(n log n)**. Returns `()` (not the vector). `f64` is not `Ord`: use `sort_by(|a, b| a.partial_cmp(b).unwrap())` or `total_cmp`.', { returns: '() — sorts in place', example: 'let mut v = vec![3, 1, 2];\nv.sort(); // [1, 2, 3]' }),
  m('slice', 'sort_unstable', 's.sort_unstable()', 'Faster, non-stable in-place sort (pdqsort). Usually the best default for integers.', { returns: '() — sorts in place', example: 'let mut v = vec![5, 2, 9];\nv.sort_unstable(); // [2, 5, 9]' }),
  m('slice', 'sort_by', 's.sort_by(compare)', 'Sort with a comparator returning `Ordering`. Reverse: `|a, b| b.cmp(a)`. Tie-break with `.then(...)` / `.then_with(...)`.', { params: [{ label: 'compare', doc: '|a, b| -> Ordering' }], returns: '() — sorts in place', example: 'v.sort_by(|a, b| b.1.cmp(&a.1).then(a.0.cmp(&b.0)));' }),
  m('slice', 'sort_by_key', 's.sort_by_key(key)', 'Sort by an extracted key. Descending: `|x| Reverse(x.1)`. The key can\'t borrow from the element (use `sort_by` for `&str` keys).', { params: [{ label: 'key', doc: '|x| -> K where K: Ord' }], returns: '() — sorts in place', example: 'v.sort_by_key(|p| (p.0, Reverse(p.1)));' }),
  m('slice', 'sort_unstable_by', 's.sort_unstable_by(compare)', 'Non-stable variant of `sort_by`.', { params: [{ label: 'compare', doc: '|a, b| -> Ordering' }], returns: '() — sorts in place', example: 'v.sort_unstable_by(|a, b| b.cmp(a)); // descending' }),
  m('slice', 'binary_search', 's.binary_search(x) -> Result<usize, usize>', 'Search a **sorted** slice: `Ok(i)` if found (any matching index), `Err(i)` = insertion point. Lower bound: `s.partition_point(|&v| v < x)`.', { params: [{ label: 'x', doc: '&T to find' }], returns: 'Result<usize, usize> — Ok(index) if found, Err(insertion point) otherwise', example: 'let i = match v.binary_search(&t) { Ok(i) | Err(i) => i };' }),
  m('slice', 'partition_point', 's.partition_point(pred) -> usize', 'First index where `pred` is false on a partitioned slice (binary search, O(log n)). `|&v| v < x` gives lower_bound, `|&v| v <= x` upper_bound.', { params: [{ label: 'pred', doc: '|&x| -> bool' }], returns: 'usize — first index where pred is false (len if none)', example: 'let v = vec![1, 3, 3, 5];\nlet lb = v.partition_point(|&y| y < 3); // 1' }),
  m('slice', 'contains', 's.contains(x) -> bool', 'Linear search. **O(n)**: use a `HashSet` for repeated membership tests. Takes a reference: `v.contains(&5)`.', { params: [{ label: 'x', doc: '&T' }], returns: 'bool — true if any element equals x', example: 'let v = vec![1, 2, 3];\nv.contains(&2); // true' }),
  m('slice', 'swap', 's.swap(a, b)', 'Swap elements at indices `a` and `b`. Use this instead of `std::mem::swap(&mut v[a], &mut v[b])`, which the borrow checker rejects.', { params: [{ label: 'a', doc: 'index' }, { label: 'b', doc: 'index' }], returns: '()', example: 'let mut v = vec![1, 2, 3];\nv.swap(0, 2); // [3, 2, 1]' }),
  m('slice', 'reverse', 's.reverse()', 'Reverse in place. O(n).', { returns: '() — reverses in place', example: 'let mut v = vec![1, 2, 3];\nv.reverse(); // [3, 2, 1]' }),
  m('slice', 'iter', 's.iter() -> Iter<&T>', 'Iterator over **references** `&T`. Closures then see `&x` (or `&&x` in `filter`).', { returns: 'Iter<T> — iterator yielding &T', example: 'let total: i64 = v.iter().sum();' }),
  m('slice', 'iter_mut', 's.iter_mut() -> IterMut<&mut T>', 'Iterator over `&mut T`: `for x in v.iter_mut() { *x *= 2; }`.', { returns: 'IterMut<T> — iterator yielding &mut T', example: 'for x in v.iter_mut() { *x *= 2; }' }),
  m('slice', 'windows', 's.windows(size) -> Windows<&[T]>', 'Overlapping sub-slices of length `size`: `[1,2,3].windows(2)` -> `[1,2]`, `[2,3]`. Panics if `size == 0`.', { params: [{ label: 'size', doc: 'window length (> 0)' }], returns: 'Windows<T> — iterator of &[T] windows (none if size > len)', example: 'let inc = v.windows(2).all(|w| w[0] < w[1]);' }),
  m('slice', 'chunks', 's.chunks(chunk_size) -> Chunks<&[T]>', 'Non-overlapping sub-slices of length `chunk_size` (last may be shorter). Panics if `chunk_size == 0`.', { params: [{ label: 'chunk_size', doc: 'chunk length (> 0)' }], returns: 'Chunks<T> — iterator of &[T] chunks', example: 'let v = vec![1, 2, 3, 4, 5];\nlet c: Vec<&[i64]> = v.chunks(2).collect(); // [[1, 2], [3, 4], [5]]' }),
  m('slice', 'to_vec', 's.to_vec() -> Vec<T>', 'Clone the slice into a new `Vec`.', { returns: 'Vec<T> — an owned copy', example: 'let left = v[..mid].to_vec();' }),
  m('slice', 'first', 's.first() -> Option<&T>', 'First element or `None`.', { returns: 'Option<&T> — Some(&first), or None if empty', example: 'let v = vec![4, 5];\nv.first(); // Some(&4)' }),
  m('slice', 'last', 's.last() -> Option<&T>', 'Last element or `None`. `*v.last().unwrap()` to copy it out.', { returns: 'Option<&T> — Some(&last), or None if empty', example: 'if let Some(&top) = stack.last() { }' }),
  m('slice', 'get', 's.get(index) -> Option<&T>', 'Bounds-checked access without panicking. Handy for grid neighbours.', { params: [{ label: 'index', doc: 'usize index or range' }], returns: 'Option<&T> — Some(&element) if in bounds, else None', example: 'let v = vec![1, 2];\nv.get(5); // None (no panic)' }),
  m('slice', 'concat', 's.concat() -> Vec<T> / String', 'Flatten a slice of slices/Vecs into a `Vec`, or a slice of strings into a `String`.', { returns: 'Vec<T> or String — all parts joined with no separator', example: 'let v = vec![vec![1, 2], vec![3]].concat(); // [1, 2, 3]\nlet s = ["ab", "cd"].concat();             // "abcd"' }),
  m('slice', 'join', 's.join(sep) -> String', 'Join strings with a separator: `words.join(" ")`. Numbers must be converted first: `v.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(" ")`.', { params: [{ label: 'sep', doc: 'separator &str' }], returns: 'String — the parts joined by sep', example: 'let words = vec!["a", "b", "c"];\nlet s = words.join(", "); // "a, b, c"' }),
  m('slice', 'fill', 's.fill(value)', 'Set every element to `value`.', { params: [{ label: 'value', doc: 'fill value' }], returns: '()', example: 'seen.fill(false);' }),
  m('slice', 'rotate_left', 's.rotate_left(mid)', 'Rotate in place so element `mid` becomes first. O(n).', { params: [{ label: 'mid', doc: 'rotation amount' }], returns: '()', example: 'let mut v = vec![1, 2, 3, 4, 5];\nv.rotate_left(2); // [3, 4, 5, 1, 2]' }),
  m('slice', 'split_at', 's.split_at(mid) -> (&[T], &[T])', 'Split into `[0, mid)` and `[mid, len)`. `split_at_mut` gives two disjoint `&mut` halves. Panics if `mid > len`.', { params: [{ label: 'mid', doc: 'split index' }], returns: '(&[T], &[T]) — the left and right halves', example: 'let (left, right) = v.split_at(2);' }),
  m('slice', 'starts_with', 's.starts_with(needle) -> bool', 'True if the slice begins with `needle`.', { params: [{ label: 'needle', doc: '&[T]' }], returns: 'bool — whether needle is a prefix', example: 'let v = vec![1, 2, 3];\nv.starts_with(&[1, 2]); // true' }),

  // ---------- String / str ----------
  ty('String', 'String', 'Owned, growable UTF-8 string. **Not indexable** (`s[i]` is an error): use `s.as_bytes()[i]` (u8) for ASCII or `s.chars()`. `&String` coerces to `&str`, so all `str` methods work.', { example: 'let mut s = String::from("ab");\ns.push(\'c\'); // "abc"' }),
  f('String', 'new', 'String::new() -> String', 'Empty string.', { insert: 'String::new()', returns: 'String — empty', example: 'let mut out = String::new();' }),
  f('String', 'from', 'String::from(s) -> String', 'Create an owned `String` from a `&str` (same as `"..".to_string()`).', { params: [{ label: 's', doc: '&str' }], returns: 'String — an owned copy of s', example: 'let s = String::from("hello");' }),
  f('String', 'with_capacity', 'String::with_capacity(capacity) -> String', 'Empty string with reserved bytes.', { params: [{ label: 'capacity', doc: 'bytes to reserve' }], returns: 'String — empty, with reserved capacity', example: 'let mut s = String::with_capacity(n);' }),
  f('String', 'from_utf8', 'String::from_utf8(vec) -> Result<String, _>', 'Build a String from bytes (`Vec<u8>`); `.unwrap()` for known-ASCII.', { params: [{ label: 'vec', doc: 'Vec<u8>' }], returns: 'Result<String, FromUtf8Error> — Err if the bytes are not valid UTF-8', example: 'let s = String::from_utf8(vec![b\'h\', b\'i\']).unwrap(); // "hi"' }),
  m('String', 'push', 's.push(ch)', 'Append one `char`.', { params: [{ label: 'ch', doc: 'char' }], returns: '()', example: 'let mut s = String::from("ab");\ns.push(\'c\'); // "abc"' }),
  m('String', 'push_str', 's.push_str(string)', 'Append a `&str`. `s += "x"` / `s += &other` also work.', { params: [{ label: 'string', doc: '&str' }], returns: '()', example: 'let mut s = String::from("foo");\ns.push_str("bar"); // "foobar"' }),
  m('String', 'pop', 's.pop() -> Option<char>', 'Remove and return the last char.', { returns: 'Option<char> — Some(last char), or None if empty', example: 'let mut s = String::from("ab");\ns.pop(); // Some(\'b\'), s == "a"' }),
  m('String', 'insert', 's.insert(idx, ch)', 'Insert a char at byte index `idx`. O(n). Panics if `idx` is not a char boundary.', { params: [{ label: 'idx', doc: 'byte index on a char boundary' }, { label: 'ch', doc: 'char' }], returns: '()', example: 'let mut s = String::from("bc");\ns.insert(0, \'a\'); // "abc"' }),
  m('String', 'clear', 's.clear()', 'Make the string empty.', { returns: '()', example: 'line.clear(); // reuse the buffer before read_line' }),
  m('String', 'as_str', 's.as_str() -> &str', 'Borrow as `&str` (useful in `match s.as_str() { "a" => .. }`).', { returns: '&str — a borrowed view of the whole string', example: 'match cmd.as_str() {\n    "push" => {}\n    _ => {}\n}' }),
  m('String', 'into_bytes', 's.into_bytes() -> Vec<u8>', 'Consume into a mutable byte vector: great for in-place ASCII edits, then `String::from_utf8(b).unwrap()`.', { returns: 'Vec<u8> — the string\'s bytes (s is moved)', example: 'let mut b = s.into_bytes();\nb.reverse();\nlet s = String::from_utf8(b).unwrap();' }),
  ty('str', '&str', 'Borrowed string slice. Slicing `&s[a..b]` uses **byte** indices and panics off a char boundary (fine for ASCII).', { example: 'let s: &str = "hello";\nlet head = &s[..2]; // "he"' }),
  m('str', 'len', 's.len() -> usize', 'Length in **bytes**, not chars. Use `s.chars().count()` for chars (O(n)).', { returns: 'usize — length in bytes', example: '"abc".len(); // 3\n"é".len();   // 2' }),
  m('str', 'is_empty', 's.is_empty() -> bool', 'True if length is 0.', { returns: 'bool — true if len() == 0', example: 'if s.is_empty() { return 0; }' }),
  m('str', 'chars', 's.chars() -> Chars', 'Iterator over `char`s. `.rev()`, `.enumerate()`, `.collect::<Vec<char>>()` for random access.', { returns: 'Chars — iterator yielding char', example: 'let cs: Vec<char> = s.chars().collect();', learn: {
      summary: "go through a string character by character",
      what: "chars is called with a dot on a string and returns an iterator over its characters (type char), from left to right. It decodes UTF-8 properly, so an accented letter or an emoji counts as one character. Use it in a for loop, or chain iterator methods such as .filter(), .count() or .collect().",
      params: {
        s: "the string you call it on, before the dot"
      },
      returns: "An iterator of char values. Loop over it, or collect it: let v: Vec<char> = s.chars().collect();",
      example: "let pw = \"abc123\";                                  // some text\nlet vowels = pw.chars().filter(|c| \"aeiou\".contains(*c)).count();  // 1\nlet first = pw.chars().next().unwrap();             // 'a'\nprintln!(\"{} {}\", vowels, first);                   // 1 a",
      watch: [
        "s.chars().nth(i) walks from the start every time (O(i)); for repeated indexing collect into a Vec<char> or use as_bytes.",
        "To turn chars back into text, collect into a String: .collect::<String>()."
      ]
    }  }),
  m('str', 'bytes', 's.bytes() -> Bytes', 'Iterator over `u8` bytes. Fast for ASCII; compare with byte literals `b\'a\'`.', { returns: 'Bytes — iterator yielding u8', example: 'let digits = s.bytes().filter(|b| b.is_ascii_digit()).count();' }),
  m('str', 'as_bytes', 's.as_bytes() -> &[u8]', 'View as a byte slice: O(1) random access `b[i]` for ASCII strings.', { returns: '&[u8] — borrowed bytes (no copy)', example: 'let b = s.as_bytes();\nif b[i] == b\'#\' { }', learn: {
      summary: "view a string as raw bytes",
      what: "as_bytes is called with a dot on a string and gives you its contents as a slice of bytes (&[u8]): numbers from 0 to 255, one per byte. Rust strings are UTF-8 and can't be indexed with s[i], because one character may take several bytes. For plain ASCII text (English letters, digits, punctuation) each character is exactly one byte, so b[i] gives you the i-th character instantly. Byte literals like b'a' let you compare against characters.",
      params: {
        s: "the string you call it on, before the dot"
      },
      returns: "A &[u8]: a borrowed, read-only view; nothing is copied. Index it with b[i], get its length with b.len(), and turn a byte into a char with b[i] as char.",
      example: "let word = \"Rust\";               // ASCII text\nlet b = word.as_bytes();         // [82, 117, 115, 116]\nprintln!(\"{}\", b[0] as char);    // R\nprintln!(\"{}\", b[1] == b'u');    // true: compared with a byte literal",
      watch: [
        "\"One byte = one character\" only holds for ASCII; accented letters and emoji take several bytes.",
        "The slice is read-only; for a changeable copy use s.as_bytes().to_vec() or s.into_bytes()."
      ]
    }  }),
  m('str', 'char_indices', 's.char_indices() -> CharIndices', 'Iterator of `(byte_index, char)`. Byte index equals char index only for ASCII.', { returns: 'CharIndices — iterator yielding (usize, char)', example: 'for (i, c) in "ab".char_indices() { } // (0, \'a\'), (1, \'b\')' }),
  m('str', 'split', 's.split(pat) -> Split', 'Split on a char, `&str`, or closure. Empty pieces are kept (`"a,,b"` -> `a`, ``, `b`).', { params: [{ label: 'pat', doc: 'char, &str or |c| -> bool' }], returns: 'Split — lazy iterator of &str pieces', example: 'let parts: Vec<&str> = "a,b,c".split(\',\').collect(); // ["a", "b", "c"]' }),
  m('str', 'split_whitespace', 's.split_whitespace() -> SplitWhitespace', 'Split on runs of whitespace, skipping empties. Standard for parsing input.', { returns: 'SplitWhitespace — iterator of non-empty &str tokens', example: 'let nums: Vec<i64> = line.split_whitespace().map(|t| t.parse().unwrap()).collect();', learn: {
      summary: "split text into words",
      what: "split_whitespace is called with a dot on a string (s.split_whitespace()) and breaks it into pieces wherever there are spaces, tabs or newlines, skipping extra whitespace. It doesn't build a list right away: it returns an iterator, a thing that hands out the pieces one at a time when asked, e.g. by .next() or a for loop. Each piece is a &str, a view into the original string, so nothing is copied.",
      params: {
        s: "the string you call it on, before the dot, e.g. a line or the whole input"
      },
      returns: "An iterator over the words (each a &str). Loop over it with for, take items with .next(), or gather them with .collect::<Vec<_>>().",
      example: "let sentence = \"the  quick\\tbrown fox\";  // messy spacing\nfor w in sentence.split_whitespace() {   // visits each word in turn\n    print!(\"[{}]\", w);                   // [the][quick][brown][fox]\n}                                        // end of loop",
      watch: [
        "The pieces are text (&str); call .parse() on each to get numbers.",
        "The words borrow from the original string, so that string must stay alive while you use them."
      ]
    }  }),
  m('str', 'split_ascii_whitespace', 's.split_ascii_whitespace() -> SplitAsciiWhitespace', 'Faster ASCII-only `split_whitespace`.', { returns: 'SplitAsciiWhitespace — iterator of non-empty &str tokens', example: 'let mut it = input.split_ascii_whitespace();\nlet n: usize = it.next().unwrap().parse().unwrap();' }),
  m('str', 'lines', 's.lines() -> Lines', 'Iterate lines, stripping `\\n` / `\\r\\n`.', { returns: 'Lines — iterator of &str lines (without terminators)', example: 'let grid: Vec<Vec<u8>> = input.lines().map(|l| l.bytes().collect()).collect();' }),
  m('str', 'trim', 's.trim() -> &str', 'Strip leading/trailing whitespace (also `trim_start`, `trim_end`). Always trim before `parse` on a read line.', { returns: '&str — a borrowed sub-slice (no allocation)', example: '"  hi\\n".trim(); // "hi"' }),
  m('str', 'parse', 's.parse::<F>() -> Result<F, _>', 'Parse into a number etc. Needs a type: `s.parse::<i64>().unwrap()` or an annotated binding. Fails on surrounding whitespace (e.g. the `\\n` from `read_line`).', { returns: 'Result<F, F::Err> — Ok(value) or Err if malformed', example: 'let n: usize = line.trim().parse().unwrap();', learn: {
      summary: "convert text into a number",
      what: "parse is called with a dot on a string and converts the text into another type, most often a number. Rust has many number types (i32, i64, u64, f64, ...), so you must say which one you want: either with the \"turbofish\" s.parse::<i64>() or by giving the variable a type, let x: i64 = s.parse().unwrap(). Text can be malformed, so parse returns a Result: Ok(number), or Err if the text isn't a valid number.",
      params: {
        s: "the string you call it on, before the dot, e.g. a word from split_whitespace",
        F: "the type to produce, written inside ::<...>, e.g. i64 or f64"
      },
      returns: "Result<F, _>: Ok(value) if the text was valid, Err otherwise. Usually followed by .unwrap() to get the number.",
      example: "let temp: f64 = \"21.5\".parse().unwrap();        // 21.5 as a float\nlet year = \"2024\".parse::<u32>().unwrap();      // the turbofish picks u32\nprintln!(\"{}\", year + 1);                       // 2025\nprintln!(\"{}\", \"12a\".parse::<i32>().is_err());  // true: not a number",
      watch: [
        "parse doesn't trim: \" 42\" or \"42\\n\" is an Err. Call .trim() first, or use split_whitespace.",
        "With no type given, the compiler says \"type annotations needed\".",
        "A value too big for the type (e.g. 3000000000 as i32) is also an Err."
      ]
    }  }),
  m('str', 'to_string', 's.to_string() -> String', 'Owned copy. Also works on any `Display` type: `42.to_string()`.', { returns: 'String — an owned copy', example: 'let owned: String = "abc".to_string();\nlet t = 42.to_string(); // "42"' }),
  m('str', 'to_owned', 's.to_owned() -> String', 'Owned copy of a `&str`.', { returns: 'String — an owned copy', example: 'let owned: String = word.to_owned();' }),
  m('str', 'contains', 's.contains(pat) -> bool', 'Substring / char test. O(n·m) worst case.', { params: [{ label: 'pat', doc: '&str, char or closure' }], returns: 'bool — true if pat occurs', example: '"hello".contains("ell"); // true' }),
  m('str', 'starts_with', 's.starts_with(pat) -> bool', 'Prefix test (also `ends_with`).', { params: [{ label: 'pat', doc: '&str or char' }], returns: 'bool — true if s begins with pat', example: '"prefix".starts_with("pre"); // true' }),
  m('str', 'ends_with', 's.ends_with(pat) -> bool', 'Suffix test.', { params: [{ label: 'pat', doc: '&str or char' }], returns: 'bool — true if s ends with pat', example: '"file.rs".ends_with(".rs"); // true' }),
  m('str', 'find', 's.find(pat) -> Option<usize>', 'Byte index of the first match (`rfind` for last).', { params: [{ label: 'pat', doc: '&str, char or closure' }], returns: 'Option<usize> — Some(byte index) of the first match, or None', example: '"hello".find(\'l\'); // Some(2)' }),
  m('str', 'replace', 's.replace(from, to) -> String', 'Return a new String with all matches replaced (the original is unchanged).', { params: [{ label: 'from', doc: 'pattern' }, { label: 'to', doc: '&str replacement' }], returns: 'String — a new string with every match replaced', example: '"a-b-c".replace("-", ""); // "abc"' }),
  m('str', 'to_uppercase', 's.to_uppercase() -> String', 'Unicode uppercase copy (`to_ascii_uppercase` for ASCII only).', { returns: 'String — a new uppercased string', example: '"abc".to_uppercase(); // "ABC"' }),
  m('str', 'to_lowercase', 's.to_lowercase() -> String', 'Unicode lowercase copy (`to_ascii_lowercase` for ASCII only).', { returns: 'String — a new lowercased string', example: '"AbC".to_lowercase(); // "abc"' }),
  m('str', 'repeat', 's.repeat(n) -> String', 'Concatenate `n` copies.', { params: [{ label: 'n', doc: 'count' }], returns: 'String — s repeated n times', example: '"ab".repeat(3); // "ababab"' }),
  m('str', 'split_at', 's.split_at(mid) -> (&str, &str)', 'Split at byte index `mid`. Panics off a char boundary.', { params: [{ label: 'mid', doc: 'byte index' }], returns: '(&str, &str) — [0, mid) and [mid, len)', example: 'let (a, b) = "hello".split_at(2); // ("he", "llo")' }),

  // ---------- HashMap ----------
  ty('HashMap', 'HashMap<K, V>', 'Hash table: average **O(1)** insert/lookup. Iteration order is random. Keys need `Eq + Hash` (not `f64`).', { header: 'use std::collections::HashMap;', example: 'let mut freq: HashMap<char, i64> = HashMap::new();' }),
  f('HashMap', 'new', 'HashMap::new() -> HashMap<K, V>', 'Empty map.', { header: 'use std::collections::HashMap;', insert: 'HashMap::new()', returns: 'HashMap<K, V> — an empty map', example: 'let mut seen: HashMap<i64, usize> = HashMap::new();' }),
  m('HashMap', 'insert', 'map.insert(k, v) -> Option<V>', 'Insert/overwrite; returns the old value if any.', { params: [{ label: 'k', doc: 'key (moved)' }, { label: 'v', doc: 'value (moved)' }], returns: 'Option<V> — Some(previous value) if the key existed, else None', example: 'let mut m = HashMap::new();\nm.insert("a", 1); // None\nm.insert("a", 2); // Some(1)' }),
  m('HashMap', 'get', 'map.get(k) -> Option<&V>', 'Look up by **reference**: `map.get(&key)`. Returns `Option<&V>`: copy out with `.copied()` / `*map.get(&k).unwrap_or(&0)`.', { params: [{ label: 'k', doc: '&K' }], returns: 'Option<&V> — Some(&value) if the key exists, else None', example: 'let c = *freq.get(&\'a\').unwrap_or(&0);' }),
  m('HashMap', 'get_mut', 'map.get_mut(k) -> Option<&mut V>', 'Mutable lookup: `if let Some(v) = map.get_mut(&k) { *v += 1; }`.', { params: [{ label: 'k', doc: '&K' }], returns: 'Option<&mut V> — Some(&mut value) if the key exists, else None', example: 'if let Some(v) = m.get_mut(&k) { *v += 1; }' }),
  m('HashMap', 'contains_key', 'map.contains_key(k) -> bool', 'Membership test.', { params: [{ label: 'k', doc: '&K' }], returns: 'bool — true if the key is present', example: 'if seen.contains_key(&(target - x)) { }' }),
  m('HashMap', 'remove', 'map.remove(k) -> Option<V>', 'Remove a key, returning its value.', { params: [{ label: 'k', doc: '&K' }], returns: 'Option<V> — Some(removed value), or None if absent', example: 'let old = m.remove(&k); // Some(v) or None' }),
  m('HashMap', 'entry', 'map.entry(key) -> Entry<K, V>', 'In-place insert-or-update in a single lookup. The counting idiom: `*map.entry(x).or_insert(0) += 1`. `or_default()`, `or_insert_with(Vec::new)`, `and_modify(..)` also exist.', { params: [{ label: 'key', doc: 'owned key' }], returns: 'Entry<K, V> — occupied/vacant handle; finish with or_insert / or_default', example: '*count.entry(c).or_insert(0) += 1;\nadj.entry(u).or_default().push(v);' }),
  m('HashMap', 'or_insert', 'entry.or_insert(default) -> &mut V', 'Insert `default` if the key is missing; return a mutable reference to the value.', { params: [{ label: 'default', doc: 'value used when absent' }], returns: '&mut V — reference to the existing or newly inserted value', example: 'let mut freq = HashMap::new();\nfor c in "abca".chars() { *freq.entry(c).or_insert(0) += 1; } // a: 2' }),
  m('HashMap', 'or_default', 'entry.or_default() -> &mut V', 'Like `or_insert(V::default())` (0, empty Vec, ...).', { returns: '&mut V — reference to the existing or default-inserted value', example: 'let mut adj: HashMap<usize, Vec<usize>> = HashMap::new();\nadj.entry(u).or_default().push(v);' }),
  m('HashMap', 'keys', 'map.keys() -> Keys<&K>', 'Iterator over keys (arbitrary order).', { returns: 'Keys<K, V> — iterator yielding &K', example: 'let mut ks: Vec<_> = m.keys().copied().collect();\nks.sort();' }),
  m('HashMap', 'values', 'map.values() -> Values<&V>', 'Iterator over values (`values_mut` for mutable).', { returns: 'Values<K, V> — iterator yielding &V', example: 'let best = *m.values().max().unwrap_or(&0);' }),
  m('HashMap', 'iter', 'map.iter() -> Iter<(&K, &V)>', 'Iterator of `(&k, &v)` pairs. `for (k, v) in &map` is equivalent.', { returns: 'Iter<K, V> — iterator yielding (&K, &V)', example: 'for (k, v) in m.iter() { println!("{} {}", k, v); }' }),
  m('HashMap', 'len', 'map.len() -> usize', 'Number of entries.', { returns: 'usize — number of key/value pairs', example: 'let distinct = freq.len();' }),

  // ---------- HashSet ----------
  ty('HashSet', 'HashSet<T>', 'Hash set: average **O(1)** insert/contains. Collect directly: `let s: HashSet<_> = v.into_iter().collect();`.', { header: 'use std::collections::HashSet;', example: 'let set: HashSet<i64> = nums.iter().copied().collect();' }),
  f('HashSet', 'new', 'HashSet::new() -> HashSet<T>', 'Empty set.', { header: 'use std::collections::HashSet;', insert: 'HashSet::new()', returns: 'HashSet<T> — an empty set', example: 'let mut seen = HashSet::new();' }),
  m('HashSet', 'insert', 'set.insert(value) -> bool', 'Insert; returns **false if already present** (handy for "seen" checks).', { params: [{ label: 'value', doc: 'element (moved)' }], returns: 'bool — true if newly inserted, false if already present', example: 'if !seen.insert(x) { return true; } // duplicate' }),
  m('HashSet', 'contains', 'set.contains(value) -> bool', 'Membership test; pass a reference.', { params: [{ label: 'value', doc: '&T' }], returns: 'bool — true if present', example: 'if set.contains(&(x + 1)) { }' }),
  m('HashSet', 'remove', 'set.remove(value) -> bool', 'Remove; returns whether it was present.', { params: [{ label: 'value', doc: '&T' }], returns: 'bool — true if the value was present', example: 'window.remove(&nums[l]);' }),
  m('HashSet', 'intersection', 'a.intersection(other) -> Iter<&T>', 'Lazy iterator over common elements (also `union`, `difference`, `symmetric_difference`).', { params: [{ label: 'other', doc: '&HashSet<T>' }], returns: 'Intersection<T> — iterator yielding &T in both sets', example: 'let common: Vec<_> = a.intersection(&b).copied().collect();' }),
  m('HashSet', 'len', 'set.len() -> usize', 'Number of elements.', { returns: 'usize — number of elements', example: 'let unique = set.len();' }),

  // ---------- BTreeMap / BTreeSet ----------
  ty('BTreeMap', 'BTreeMap<K, V>', 'Ordered map (B-tree): **O(log n)** ops, iterates in key order. Keys need `Ord`. Use for ordered keys, min/max, or range queries.', { header: 'use std::collections::BTreeMap;', example: 'let mut m: BTreeMap<i64, usize> = BTreeMap::new();' }),
  f('BTreeMap', 'new', 'BTreeMap::new() -> BTreeMap<K, V>', 'Empty ordered map.', { header: 'use std::collections::BTreeMap;', insert: 'BTreeMap::new()', returns: 'BTreeMap<K, V> — an empty map', example: 'let mut cnt = BTreeMap::new();\n*cnt.entry(x).or_insert(0) += 1;' }),
  m('BTreeMap', 'range', 'map.range(range) -> Range<(&K, &V)>', 'Iterate entries with keys in `range`, in order; O(log n) to start. Floor of x: `map.range(..=x).next_back()`; ceiling: `map.range(x..).next()`.', { params: [{ label: 'range', doc: 'e.g. a..b, ..=x' }], returns: 'Range<K, V> — double-ended iterator of (&K, &V)', example: 'if let Some((&k, _)) = m.range(..=x).next_back() { } // largest key <= x' }),
  m('BTreeMap', 'first_key_value', 'map.first_key_value() -> Option<(&K, &V)>', 'Smallest entry (`last_key_value` for largest). `pop_first` / `pop_last` remove them.', { returns: 'Option<(&K, &V)> — the smallest entry, or None if empty', example: 'if let Some((&lo, _)) = m.first_key_value() { }' }),
  m('BTreeMap', 'pop_first', 'map.pop_first() -> Option<(K, V)>', 'Remove and return the smallest entry (`pop_last` for largest).', { returns: 'Option<(K, V)> — the removed smallest entry, or None if empty', example: 'while let Some((k, v)) = m.pop_first() { }' }),
  ty('BTreeSet', 'BTreeSet<T>', 'Ordered set: **O(log n)**, iterates sorted. Acts like a heap that also supports deletion and `range` queries.', { header: 'use std::collections::BTreeSet;', example: 'let set: BTreeSet<i64> = vec![3, 1, 2].into_iter().collect(); // {1, 2, 3}' }),
  f('BTreeSet', 'new', 'BTreeSet::new() -> BTreeSet<T>', 'Empty ordered set.', { header: 'use std::collections::BTreeSet;', insert: 'BTreeSet::new()', returns: 'BTreeSet<T> — an empty set', example: 'let mut s = BTreeSet::new();\ns.insert(5);' }),
  m('BTreeSet', 'first', 'set.first() -> Option<&T>', 'Smallest element (`last` for largest).', { returns: 'Option<&T> — the smallest element, or None if empty', example: 'let lo = *set.first().unwrap();' }),
  m('BTreeSet', 'last', 'set.last() -> Option<&T>', 'Largest element.', { returns: 'Option<&T> — the largest element, or None if empty', example: 'let hi = *set.last().unwrap();' }),
  m('BTreeSet', 'pop_first', 'set.pop_first() -> Option<T>', 'Remove and return the smallest (`pop_last` for largest).', { returns: 'Option<T> — the removed smallest element, or None if empty', example: 'while let Some(x) = set.pop_first() { }' }),
  m('BTreeSet', 'range', 'set.range(range) -> Range<&T>', 'Iterate elements in a range. Successor of x: `set.range(x+1..).next()`.', { params: [{ label: 'range', doc: 'e.g. a..b' }], returns: 'Range<T> — double-ended iterator of &T', example: 'let next = set.range(x + 1..).next(); // Option<&i64>' }),

  // ---------- VecDeque ----------
  ty('VecDeque', 'VecDeque<T>', 'Ring-buffer double-ended queue: O(1) push/pop at both ends. Use it for BFS (not `Vec::remove(0)`, which is O(n)). Indexable with `dq[i]`.', { header: 'use std::collections::VecDeque;', example: 'let mut q: VecDeque<usize> = VecDeque::new();\nq.push_back(start);' }),
  f('VecDeque', 'new', 'VecDeque::new() -> VecDeque<T>', 'Empty deque. `VecDeque::from(vec)` converts a Vec.', { header: 'use std::collections::VecDeque;', insert: 'VecDeque::new()', returns: 'VecDeque<T> — an empty deque', example: 'let mut q = VecDeque::new();\nq.push_back((0, 0));' }),
  m('VecDeque', 'push_back', 'dq.push_back(value)', 'Append at the back. O(1).', { params: [{ label: 'value', doc: 'element' }], returns: '()', example: 'q.push_back(next);' }),
  m('VecDeque', 'push_front', 'dq.push_front(value)', 'Prepend at the front. O(1). (0-1 BFS pushes weight-0 edges here.)', { params: [{ label: 'value', doc: 'element' }], returns: '()', example: 'dq.push_front(v);' }),
  m('VecDeque', 'pop_front', 'dq.pop_front() -> Option<T>', 'Remove from the front. O(1). BFS: `while let Some(u) = q.pop_front() { .. }`.', { returns: 'Option<T> — Some(front element), or None if empty', example: 'while let Some(u) = q.pop_front() {\n    for &v in &adj[u] { q.push_back(v); }\n}' }),
  m('VecDeque', 'pop_back', 'dq.pop_back() -> Option<T>', 'Remove from the back. O(1).', { returns: 'Option<T> — Some(back element), or None if empty', example: 'while dq.back().map_or(false, |&j| v[j] <= v[i]) { dq.pop_back(); }' }),
  m('VecDeque', 'front', 'dq.front() -> Option<&T>', 'Peek at the front (`back` for the back).', { returns: 'Option<&T> — Some(&front), or None if empty', example: 'if let Some(&i) = dq.front() { }' }),
  m('VecDeque', 'back', 'dq.back() -> Option<&T>', 'Peek at the back. Monotonic-deque sliding windows use `back`/`pop_back`.', { returns: 'Option<&T> — Some(&back), or None if empty', example: 'if let Some(&j) = dq.back() { }' }),

  // ---------- BinaryHeap ----------
  ty('BinaryHeap', 'BinaryHeap<T>', '**Max**-heap priority queue. For a min-heap wrap items in `Reverse`: `heap.push(Reverse((dist, node)))`. Elements need `Ord` (so not `f64`).', { header: 'use std::collections::BinaryHeap;', example: 'let mut heap = BinaryHeap::from(vec![3, 1, 4]);\nheap.pop(); // Some(4)' }),
  f('BinaryHeap', 'new', 'BinaryHeap::new() -> BinaryHeap<T>', 'Empty max-heap. `BinaryHeap::from(vec)` heapifies in O(n).', { header: 'use std::collections::BinaryHeap;', insert: 'BinaryHeap::new()', returns: 'BinaryHeap<T> — an empty max-heap', example: 'let mut pq = BinaryHeap::new();\npq.push(Reverse((0i64, src)));' }),
  m('BinaryHeap', 'push', 'heap.push(item)', 'Insert. **O(log n)**.', { params: [{ label: 'item', doc: 'element' }], returns: '()', example: 'heap.push(Reverse((d + w, v)));' }),
  m('BinaryHeap', 'pop', 'heap.pop() -> Option<T>', 'Remove and return the **largest** item. O(log n).', { returns: 'Option<T> — Some(largest item), or None if empty', example: 'while let Some(Reverse((d, u))) = heap.pop() {\n    if d > dist[u] { continue; }\n}' }),
  m('BinaryHeap', 'peek', 'heap.peek() -> Option<&T>', 'Largest item without removing it. O(1).', { returns: 'Option<&T> — Some(&largest), or None if empty', example: 'if heap.len() > k { heap.pop(); }\nlet kth = *heap.peek().unwrap();' }),
  m('BinaryHeap', 'into_sorted_vec', 'heap.into_sorted_vec() -> Vec<T>', 'Consume into an ascending Vec. O(n log n).', { returns: 'Vec<T> — all items in ascending order', example: 'let sorted = heap.into_sorted_vec(); // ascending' }),
  { name: 'Reverse', owner: 'std::cmp', kind: 'type', sig: 'Reverse(value: T)', params: [{ label: 'value', doc: 'value whose ordering is inverted' }], doc: 'Wrapper that inverts ordering. Turns `BinaryHeap` into a min-heap and gives descending keys in `sort_by_key`. Access the inner value with `.0` or by pattern `Reverse(x)`.', header: 'use std::cmp::Reverse;', example: 'let mut h = BinaryHeap::new();\nh.push(Reverse(3));\nlet Reverse(min) = h.pop().unwrap();' },

  // ---------- Option ----------
  ty('Option', 'Option<T>', '`Some(T)` or `None`. Unpack with `match`, `if let`, `?`, or the combinators below. `.unwrap()` panics on `None`.', { example: 'let first: Option<&i64> = v.first();\nif let Some(&x) = first { }' }),
  m('Option', 'unwrap', 'opt.unwrap() -> T', 'Return the value or **panic** on `None`.', { returns: 'T — the inner value (panics on None)', example: 'let top = stack.pop().unwrap();', learn: {
      summary: "take the value out of an option",
      what: "An Option is Rust's way of saying \"maybe there is a value\": it is either Some(value) or None (nothing). Functions return one when an answer might not exist: the first item of an empty list, the next line after input has ended, a key missing from a map. unwrap, called with a dot on the Option, takes the value out of Some; if it is None, the program crashes (panics). Use it when you are sure a value is there.",
      params: {
        opt: "the Option you call it on (the part before the dot), e.g. v.first() or it.next()"
      },
      returns: "The value inside Some(...). On None the program stops with a panic instead.",
      example: "let v = vec![7, 3, 9];                   // a non-empty vector\nlet biggest = *v.iter().max().unwrap();  // max() gives Some(&9) -> 9\nprintln!(\"{}\", biggest);                 // 9\n// on an empty vector, max() is None and unwrap() would panic",
      watch: [
        "unwrap on None crashes with \"called Option::unwrap() on a None value\".",
        "Safer choices: opt.unwrap_or(default), or if let Some(x) = opt { ... }."
      ]
    }  }),
  m('Option', 'expect', 'opt.expect(msg) -> T', 'Like `unwrap` with a custom panic message.', { params: [{ label: 'msg', doc: '&str' }], returns: 'T — the inner value (panics with msg on None)', example: 'let x = v.last().expect("v must not be empty");' }),
  m('Option', 'unwrap_or', 'opt.unwrap_or(default) -> T', 'Value or `default` (evaluated eagerly; use `unwrap_or_else` for expensive defaults).', { params: [{ label: 'default', doc: 'fallback value' }], returns: 'T — the inner value, or default if None', example: 'let best = v.iter().max().copied().unwrap_or(0);' }),
  m('Option', 'unwrap_or_default', 'opt.unwrap_or_default() -> T', 'Value or `T::default()` (0, "", empty Vec).', { returns: 'T — the inner value, or T::default() if None', example: 'let c = m.get(&k).copied().unwrap_or_default();' }),
  m('Option', 'is_some', 'opt.is_some() -> bool', 'True if `Some`.', { returns: 'bool — true if Some', example: 'if s.find(\'x\').is_some() { }' }),
  m('Option', 'is_none', 'opt.is_none() -> bool', 'True if `None`.', { returns: 'bool — true if None', example: 'if head.is_none() { return None; }' }),
  m('Option', 'map', 'opt.map(f) -> Option<U>', 'Transform the inner value if present.', { params: [{ label: 'f', doc: '|x| -> U' }], returns: 'Option<U> — Some(f(x)) or None', example: 'let len = v.first().map(|s| s.len()); // Option<usize>' }),
  m('Option', 'and_then', 'opt.and_then(f) -> Option<U>', 'Chain an operation that itself returns an Option.', { params: [{ label: 'f', doc: '|x| -> Option<U>' }], returns: 'Option<U> — f(x) if Some, else None', example: 'let d = s.chars().next().and_then(|c| c.to_digit(10)); // Option<u32>' }),
  m('Option', 'copied', 'opt.copied() -> Option<T>', 'Turn `Option<&T>` into `Option<T>` for `Copy` types (e.g. after `map.get`). `cloned()` for Clone types.', { returns: 'Option<T> — the referenced value copied out', example: 'let c: i64 = m.get(&k).copied().unwrap_or(0);' }),
  m('Option', 'take', 'opt.take() -> Option<T>', 'Move the value out, leaving `None` in its place. Essential for linked lists: `let next = node.next.take();`.', { returns: 'Option<T> — the previous contents (opt becomes None)', example: 'let mut cur = head;\nwhile let Some(mut node) = cur { cur = node.next.take(); }' }),
  m('Option', 'as_ref', 'opt.as_ref() -> Option<&T>', 'Borrow the inner value without moving it: `node.as_ref().map(|n| n.val)`.', { returns: 'Option<&T> — a borrowed view; opt is left intact', example: 'let v = head.as_ref().map(|n| n.val); // head still usable' }),
  m('Option', 'as_mut', 'opt.as_mut() -> Option<&mut T>', 'Mutably borrow the inner value.', { returns: 'Option<&mut T> — a mutable borrow of the inner value', example: 'if let Some(n) = head.as_mut() { n.val += 1; }' }),
  m('Option', 'filter', 'opt.filter(pred) -> Option<T>', 'Keep `Some` only if the predicate holds.', { params: [{ label: 'pred', doc: '|&x| -> bool' }], returns: 'Option<T> — Some(x) if pred(&x), else None', example: 'Some(4).filter(|x| x % 2 == 0); // Some(4)' }),
  m('Option', 'ok_or', 'opt.ok_or(err) -> Result<T, E>', 'Convert to a `Result`, using `err` for `None`. Pairs with `?`.', { params: [{ label: 'err', doc: 'error value' }], returns: 'Result<T, E> — Ok(x) if Some, Err(err) if None', example: 'let r: Result<i64, &str> = v.pop().ok_or("empty");' }),

  // ---------- Result ----------
  ty('Result', 'Result<T, E>', '`Ok(T)` or `Err(E)`. Propagate errors with `?` inside a function that returns Result.', { example: 'let r: Result<i64, _> = "42".parse::<i64>(); // Ok(42)' }),
  m('Result', 'unwrap', 'res.unwrap() -> T', 'Value or **panic** on `Err`. Fine for parsing trusted input.', { returns: 'T — the Ok value (panics on Err)', example: 'let n: i64 = "42".parse().unwrap();', learn: {
      summary: "take the value out of a result",
      what: "Some operations can fail, so instead of returning a value directly they return a Result: a box holding either Ok(value) on success or Err(error) on failure. unwrap is a method you call with a dot on such a Result. It takes the value out of Ok; if it was an Err, it crashes the program (a \"panic\") with an error message. In small programs with trusted input that is fine and keeps the code short.",
      params: {
        res: "the Result you call it on (the part before the dot), e.g. \"42\".parse::<i32>()"
      },
      returns: "The value inside Ok(...), e.g. the number from a successful parse. On Err the program stops with a panic message instead.",
      example: "let n: i32 = \"42\".parse().unwrap();  // Ok(42) becomes 42\nprintln!(\"{}\", n + 1);               // 43\n// \"4x2\".parse::<i32>().unwrap() would panic: invalid digit",
      watch: [
        "A panic ends the program with an error: on bad input you get a runtime error, not a wrong answer.",
        ".expect(\"message\") works like unwrap but lets you choose the crash message, which helps debugging."
      ]
    }  }),
  m('Result', 'expect', 'res.expect(msg) -> T', 'Like `unwrap` but panics with `msg` (plus the error) on `Err`.', { params: [{ label: 'msg', doc: '&str' }], returns: 'T — the Ok value (panics with msg on Err)', example: 'io::stdin().read_line(&mut s).expect("read failed");' }),
  m('Result', 'is_ok', 'res.is_ok() -> bool', 'True if `Ok` (also `is_err`).', { returns: 'bool — true if Ok', example: 'let numeric = tok.parse::<i64>().is_ok();' }),
  m('Result', 'ok', 'res.ok() -> Option<T>', 'Convert to `Option`, discarding the error.', { returns: 'Option<T> — Some(value) if Ok, None if Err', example: 'let nums: Vec<i64> = toks.iter().filter_map(|t| t.parse().ok()).collect();' }),
  m('Result', 'unwrap_or', 'res.unwrap_or(default) -> T', 'Value or `default`.', { params: [{ label: 'default', doc: 'fallback value' }], returns: 'T — the Ok value, or default on Err', example: 'let n = s.parse::<i64>().unwrap_or(0);' }),
  m('Result', 'map', 'res.map(f) -> Result<U, E>', 'Transform the `Ok` value, passing `Err` through unchanged (`map_err` transforms the error).', { params: [{ label: 'f', doc: '|x| -> U' }], returns: 'Result<U, E> — Ok(f(x)) or the original Err', example: '"21".parse::<i64>().map(|x| x * 2); // Ok(42)' }),
  m('Result', 'and_then', 'res.and_then(f) -> Result<U, E>', 'Chain an operation that itself returns a `Result`; short-circuits on `Err`.', { params: [{ label: 'f', doc: '|x| -> Result<U, E>' }], returns: 'Result<U, E> — f(x) if Ok, else the original Err', example: 'let r = s.parse::<i64>().and_then(|x| t.parse::<i64>().map(|y| x + y));' }),

  // ---------- Box / Rc / RefCell ----------
  ty('Box', 'Box<T>', 'Owned heap pointer. Used for recursive types: Crucible lists are `Option<Box<ListNode>>`. Deref with `*` or auto-deref field access (`node.val`).', { example: 'let b: Box<i64> = Box::new(5);\nlet x = *b + 1; // 6' }),
  f('Box', 'new', 'Box::new(x) -> Box<T>', 'Move `x` onto the heap.', { params: [{ label: 'x', doc: 'value' }], returns: 'Box<T> — owning pointer to the heap value', example: 'let node = Some(Box::new(ListNode::new(1)));' }),
  ty('Rc', 'Rc<T>', 'Reference-counted shared ownership (single-threaded). `Rc::clone(&rc)` is cheap (bumps a counter). Contents are immutable; pair with `RefCell` for mutation. Crucible trees are `Option<Rc<RefCell<TreeNode>>>`.', { header: 'use std::rc::Rc;', example: 'let a = Rc::new(5);\nlet b = Rc::clone(&a); // strong count == 2' }),
  f('Rc', 'new', 'Rc::new(value) -> Rc<T>', 'Allocate a reference-counted value.', { header: 'use std::rc::Rc;', params: [{ label: 'value', doc: 'value' }], returns: 'Rc<T> — the first pointer (count 1)', example: 'Some(Rc::new(RefCell::new(TreeNode::new(1))))' }),
  f('Rc', 'clone', 'Rc::clone(this) -> Rc<T>', 'New pointer to the same allocation (count + 1). Not a deep copy. `opt_rc.clone()` on `Option<Rc<..>>` does the same.', { params: [{ label: 'this', doc: '&Rc<T>' }], returns: 'Rc<T> — another pointer to the same value', example: 'let left = node.borrow().left.clone(); // Option<Rc<RefCell<TreeNode>>>' }),
  f('Rc', 'ptr_eq', 'Rc::ptr_eq(this, other) -> bool', 'True if both point to the same allocation (identity, not value equality).', { params: [{ label: 'this', doc: '&Rc<T>' }, { label: 'other', doc: '&Rc<T>' }], returns: 'bool — true if same allocation', example: 'if Rc::ptr_eq(&a, &b) { } // same node' }),
  ty('RefCell', 'RefCell<T>', 'Interior mutability with borrow rules checked **at runtime**. Holding a `borrow_mut()` while another borrow is alive **panics** (`already borrowed`). Keep borrows short; copy fields out.', { header: 'use std::cell::RefCell;', example: 'let c = RefCell::new(0);\n*c.borrow_mut() += 1;' }),
  f('RefCell', 'new', 'RefCell::new(value) -> RefCell<T>', 'Wrap a value for interior mutability.', { header: 'use std::cell::RefCell;', params: [{ label: 'value', doc: 'value' }], returns: 'RefCell<T> — the wrapped value', example: 'let cell = RefCell::new(vec![1]);\ncell.borrow_mut().push(2); // [1, 2]' }),
  m('RefCell', 'borrow', 'cell.borrow() -> Ref<T>', 'Shared runtime borrow. Typical tree read: `node.borrow().val`, `node.borrow().left.clone()`. Panics if mutably borrowed.', { returns: 'Ref<T> — a guard that derefs to &T until dropped', example: 'fn depth(root: Option<Rc<RefCell<TreeNode>>>) -> i64 {\n    match root { None => 0, Some(n) => { let n = n.borrow();\n        1 + depth(n.left.clone()).max(depth(n.right.clone())) } }\n}' }),
  m('RefCell', 'borrow_mut', 'cell.borrow_mut() -> RefMut<T>', 'Exclusive runtime borrow; **panics** if any other borrow is active. E.g. swap children: `let mut n = node.borrow_mut(); let l = n.left.take(); n.left = n.right.take(); n.right = l;`.', { returns: 'RefMut<T> — a guard that derefs to &mut T until dropped', example: 'node.borrow_mut().val += 1;' }),
  m('RefCell', 'take', 'cell.take() -> T', 'Replace the contents with `T::default()` and return the old value (on the `RefCell` itself; distinct from `node.borrow_mut().left.take()` on an Option field).', { returns: 'T — the old contents (cell now holds T::default())', example: 'let c = RefCell::new(vec![1, 2]);\nlet old = c.take(); // [1, 2], c holds []' }),

  // ---------- Iterator ----------
  ty('Iterator', 'trait Iterator', 'Lazy sequence; adaptors (`map`, `filter`, ...) do nothing until consumed by `collect`, `sum`, `for`, etc. `iter()` yields `&T`, `iter_mut()` `&mut T`, `into_iter()` `T`.', { example: 'let evens: Vec<i64> = (1..=10).filter(|x| x % 2 == 0).collect(); // [2, 4, 6, 8, 10]' }),
  m('Iterator', 'iter', 'c.iter() -> Iter<&T>', 'Borrowing iterator over a collection (`&T` items).', { returns: 'Iter — iterator yielding &T (collection stays usable)', example: 'for x in v.iter() { }' }),
  m('Iterator', 'iter_mut', 'c.iter_mut() -> IterMut<&mut T>', 'Mutably borrowing iterator.', { returns: 'IterMut — iterator yielding &mut T', example: 'for row in grid.iter_mut() { row.fill(0); }' }),
  m('Iterator', 'into_iter', 'c.into_iter() -> IntoIter<T>', 'Consuming iterator: yields owned items and **moves** the collection (can\'t use it afterwards). On `&v` it yields references.', { returns: 'IntoIter — iterator yielding owned T', example: 'let set: HashSet<i64> = v.into_iter().collect(); // v is moved' }),
  m('Iterator', 'next', 'it.next() -> Option<Item>', 'Advance and return the next item.', { returns: 'Option<Item> — Some(next item), or None when exhausted', example: 'let mut it = line.split_whitespace();\nlet a = it.next().unwrap();', learn: {
      summary: "get the next item from an iterator",
      what: "An iterator is a thing that produces values one at a time: words from split_whitespace, characters from chars, numbers from a range. next() is called with a dot and asks it for the next value. Because the iterator might be used up, the answer is an Option: Some(item) if there was one, None when there are no more. Calling next moves the iterator forward, so the iterator variable must be declared let mut.",
      params: {
        it: "the iterator you call it on, before the dot; it must be mutable (let mut it = ...)"
      },
      returns: "Option<Item>: Some(value) for the next item, None when there are no more. Often followed by .unwrap() when you know an item exists.",
      example: "let mut colors = \"red green blue\".split_whitespace();  // an iterator of words\nlet first = colors.next().unwrap();                    // \"red\"\nprintln!(\"{:?}\", colors.next());                       // Some(\"green\")\nlet rest: Vec<&str> = colors.collect();                // [\"blue\"]: what was left",
      watch: [
        "\"cannot borrow as mutable\" means you forgot let mut on the iterator.",
        "Each call consumes an item; you can't go back."
      ]
    }  }),
  m('Iterator', 'map', 'it.map(f) -> Map', 'Transform each item (lazy).', { params: [{ label: 'f', doc: '|x| -> U' }], returns: 'Map — lazy iterator of f(item)', example: 'let sq: Vec<i64> = v.iter().map(|&x| x * x).collect();' }),
  m('Iterator', 'filter', 'it.filter(pred) -> Filter', 'Keep items where `pred(&item)` is true. Over `iter()` the closure sees `&&T`: write `|&&x| x > 0` or `|x| **x > 0`.', { params: [{ label: 'pred', doc: '|&item| -> bool' }], returns: 'Filter — lazy iterator of matching items', example: 'let pos = v.iter().filter(|&&x| x > 0).count();' }),
  m('Iterator', 'filter_map', 'it.filter_map(f) -> FilterMap', 'Map to `Option` and keep the `Some` values.', { params: [{ label: 'f', doc: '|x| -> Option<U>' }], returns: 'FilterMap — lazy iterator of the unwrapped Some values', example: 'let ds: Vec<u32> = s.chars().filter_map(|c| c.to_digit(10)).collect();' }),
  m('Iterator', 'enumerate', 'it.enumerate() -> Enumerate', 'Yield `(index, item)` pairs (index is `usize`).', { returns: 'Enumerate — iterator of (usize, Item)', example: 'for (i, &x) in v.iter().enumerate() { }' }),
  m('Iterator', 'zip', 'it.zip(other) -> Zip', 'Pair items with another iterator, stopping at the shorter.', { params: [{ label: 'other', doc: 'IntoIterator' }], returns: 'Zip — iterator of (a, b) pairs', example: 'let dot: i64 = a.iter().zip(&b).map(|(x, y)| x * y).sum();' }),
  m('Iterator', 'rev', 'it.rev() -> Rev', 'Reverse a double-ended iterator: `(0..n).rev()`, `s.chars().rev()`.', { returns: 'Rev — iterator in reverse order', example: 'let r: String = s.chars().rev().collect();', learn: {
      summary: "walk an iterator backwards",
      what: "rev is called with a dot on an iterator and gives back a new iterator that produces the same items in reverse order, last one first. It works on iterators that know where their end is, such as ranges (0..n), v.iter() and s.chars(). Nothing is copied or computed until you consume it with a loop or a method like collect.",
      params: {
        it: "the iterator you call it on, before the dot, e.g. (1..=5) or v.iter()"
      },
      returns: "A new iterator (type Rev) that yields the items back to front. Consume it with for, .collect(), etc.",
      example: "for i in (1..=3).rev() {  // counts 3, 2, 1\n    print!(\"{} \", i);     // prints: 3 2 1\n}                         // end of loop\nlet top: Vec<i32> = vec![4, 5, 6].into_iter().rev().take(2).collect();  // [6, 5]",
      watch: [
        "Wrap a range in parentheses: (0..n).rev(), not 0..n.rev().",
        "Some iterators (like lines read from input) can't run backwards; collect into a Vec first if the compiler complains."
      ]
    }  }),
  m('Iterator', 'sum', 'it.sum::<S>() -> S', 'Add all items. Often needs a type: `v.iter().sum::<i64>()`. Overflow panics in debug builds.', { returns: 'S — the total (0 for an empty iterator)', example: 'let total: i64 = v.iter().sum();' }),
  m('Iterator', 'product', 'it.product::<P>() -> P', 'Multiply all items. Overflows quickly; use `i128` or a modulus for big inputs.', { returns: 'P — the product (1 for an empty iterator)', example: 'let fact: i64 = (1..=10).product(); // 3628800' }),
  m('Iterator', 'max', 'it.max() -> Option<Item>', 'Largest item (last one on ties), `None` if empty. Not for `f64`: use `fold(f64::MIN, f64::max)`.', { returns: 'Option<Item> — Some(largest), or None if empty', example: 'let m = *v.iter().max().unwrap(); // v: Vec<i64>' }),
  m('Iterator', 'min', 'it.min() -> Option<Item>', 'Smallest item (first on ties), `None` if empty.', { returns: 'Option<Item> — Some(smallest), or None if empty', example: 'let lo = v.iter().copied().min().unwrap_or(0);' }),
  m('Iterator', 'max_by_key', 'it.max_by_key(f) -> Option<Item>', 'Item with the largest key (**last** on ties).', { params: [{ label: 'f', doc: '|&item| -> K' }], returns: 'Option<Item> — Some(item with max key), or None if empty', example: 'let longest = words.iter().max_by_key(|w| w.len());' }),
  m('Iterator', 'min_by_key', 'it.min_by_key(f) -> Option<Item>', 'Item with the smallest key (first on ties).', { params: [{ label: 'f', doc: '|&item| -> K' }], returns: 'Option<Item> — Some(item with min key), or None if empty', example: 'let closest = pts.iter().min_by_key(|p| p.0 * p.0 + p.1 * p.1);' }),
  m('Iterator', 'max_by', 'it.max_by(compare) -> Option<Item>', 'Max with a comparator, e.g. `|a, b| a.total_cmp(b)` for floats.', { params: [{ label: 'compare', doc: '|a, b| -> Ordering' }], returns: 'Option<Item> — Some(max item), or None if empty', example: 'let best = xs.iter().copied().max_by(|a: &f64, b| a.total_cmp(b));' }),
  m('Iterator', 'count', 'it.count() -> usize', 'Consume and count items. O(n).', { returns: 'usize — number of items', example: 'let vowels = s.chars().filter(|c| "aeiou".contains(*c)).count();' }),
  m('Iterator', 'collect', 'it.collect::<C>() -> C', 'Build a collection: `Vec`, `String`, `HashSet`, `HashMap` (from pairs). Type must be known: `collect::<Vec<_>>()` or annotate the binding.', { returns: 'C — the collection built from all items', example: 'let s: String = cs.iter().rev().collect();\nlet m: HashMap<_, _> = v.iter().map(|&x| (x, 1)).collect();' }),
  m('Iterator', 'fold', 'it.fold(init, f) -> B', 'Reduce with an accumulator.', { params: [{ label: 'init', doc: 'initial accumulator' }, { label: 'f', doc: '|acc, x| -> B' }], returns: 'B — the final accumulator', example: 'let xor = v.iter().fold(0, |a, &x| a ^ x);' }),
  m('Iterator', 'scan', 'it.scan(state, f) -> Scan', 'Stateful map, e.g. prefix sums. Stops when `f` returns `None`.', { params: [{ label: 'state', doc: 'initial state' }, { label: 'f', doc: '|st, x| -> Option<U>' }], returns: 'Scan — lazy iterator of the Some values f yields', example: 'let pre: Vec<i64> = v.iter().scan(0, |s, &x| { *s += x; Some(*s) }).collect();' }),
  m('Iterator', 'any', 'it.any(pred) -> bool', 'True if any item satisfies `pred` (short-circuits; false when empty).', { params: [{ label: 'pred', doc: '|x| -> bool' }], returns: 'bool — true if some item matches', example: 'let has_neg = v.iter().any(|&x| x < 0);' }),
  m('Iterator', 'all', 'it.all(pred) -> bool', 'True if every item satisfies `pred` (true when empty).', { params: [{ label: 'pred', doc: '|x| -> bool' }], returns: 'bool — true if every item matches', example: 'let digits = s.chars().all(|c| c.is_ascii_digit());' }),
  m('Iterator', 'position', 'it.position(pred) -> Option<usize>', 'Index of the first matching item.', { params: [{ label: 'pred', doc: '|x| -> bool' }], returns: 'Option<usize> — Some(index) of first match, or None', example: 'let i = v.iter().position(|&x| x == t); // Option<usize>' }),
  m('Iterator', 'find', 'it.find(pred) -> Option<Item>', 'First item matching `pred` (closure gets `&Item`).', { params: [{ label: 'pred', doc: '|&x| -> bool' }], returns: 'Option<Item> — Some(first match), or None', example: 'let first_even = v.iter().find(|&&x| x % 2 == 0); // Option<&i64>' }),
  m('Iterator', 'take', 'it.take(n) -> Take', 'Only the first `n` items.', { params: [{ label: 'n', doc: 'count' }], returns: 'Take — iterator of at most n items', example: 'let top3: Vec<i64> = v.iter().copied().take(3).collect();' }),
  m('Iterator', 'skip', 'it.skip(n) -> Skip', 'Skip the first `n` items.', { params: [{ label: 'n', doc: 'count' }], returns: 'Skip — iterator without the first n items', example: 'for x in v.iter().skip(1) { }' }),
  m('Iterator', 'take_while', 'it.take_while(pred) -> TakeWhile', 'Yield items while `pred` holds, then stop.', { params: [{ label: 'pred', doc: '|&x| -> bool' }], returns: 'TakeWhile — iterator of the leading matching items', example: 'let lead = s.chars().take_while(|c| c.is_ascii_digit()).count();' }),
  m('Iterator', 'chain', 'it.chain(other) -> Chain', 'Concatenate two iterators.', { params: [{ label: 'other', doc: 'IntoIterator with same Item' }], returns: 'Chain — iterator over it, then other', example: 'for x in a.iter().chain(b.iter()) { }' }),
  m('Iterator', 'peekable', 'it.peekable() -> Peekable', 'Allow `.peek()` at the next item without consuming it (useful for run-length / tokenizing).', { returns: 'Peekable — iterator with peek() -> Option<&Item>', example: 'let mut it = s.chars().peekable();\nwhile let Some(c) = it.next() {\n    if it.peek() == Some(&c) { }\n}' }),
  m('Iterator', 'flat_map', 'it.flat_map(f) -> FlatMap', 'Map each item to an iterator and flatten. `flatten()` for already-nested items.', { params: [{ label: 'f', doc: '|x| -> IntoIterator' }], returns: 'FlatMap — iterator over all inner items', example: 'let words: Vec<&str> = lines.iter().flat_map(|l| l.split_whitespace()).collect();' }),
  m('Iterator', 'flatten', 'it.flatten() -> Flatten', 'Flatten one level of nesting (also skips `None`s).', { returns: 'Flatten — iterator over the inner items', example: 'let flat: Vec<i64> = grid.into_iter().flatten().collect();' }),
  m('Iterator', 'step_by', 'it.step_by(step) -> StepBy', 'Every `step`-th item, starting with the first: `(0..n).step_by(2)`. Panics if `step == 0`.', { params: [{ label: 'step', doc: 'stride (> 0)' }], returns: 'StepBy — iterator of every step-th item', example: 'for i in (0..10).step_by(3) { } // 0, 3, 6, 9' }),
  m('Iterator', 'cloned', 'it.cloned() -> Cloned', 'Turn `&T` items into `T` by cloning (`copied()` for Copy types).', { returns: 'Cloned — iterator of owned clones', example: 'let names: Vec<String> = refs.iter().cloned().collect();' }),
  m('Iterator', 'copied', 'it.copied() -> Copied', 'Turn `&T` items into `T` for Copy types (integers, chars).', { returns: 'Copied — iterator of copied values', example: 'let v2: Vec<i64> = v.iter().copied().filter(|x| x % 2 == 0).collect();' }),
  m('Iterator', 'last', 'it.last() -> Option<Item>', 'Consume and return the final item. O(n) for most iterators; use `slice.last()` on a Vec.', { returns: 'Option<Item> — Some(final item), or None if empty', example: 'let last_word = s.split_whitespace().last();' }),
  m('Iterator', 'nth', 'it.nth(n) -> Option<Item>', 'The `n`-th item (0-based), consuming those before it. O(n) on `chars()`.', { params: [{ label: 'n', doc: 'index' }], returns: 'Option<Item> — Some(item at n), or None if too short', example: '"hello".chars().nth(1); // Some(\'e\')' }),

  // ---------- i64 / integers ----------
  ty('i64', 'i64', '64-bit signed integer (Crucible `int`). Indices must be `usize`: cast with `as usize`. Overflow **panics** in debug, wraps in release; use checked/wrapping ops intentionally. Other types: i32, u64, usize, i128.', { example: 'let x: i64 = 1_000_000_007;\nlet i = x as usize;' }),
  { name: 'MAX', owner: 'i64', kind: 'constant', sig: 'i64::MAX = 9_223_372_036_854_775_807', doc: 'Largest i64; a common "infinity" sentinel. Adding to it overflows: prefer `i64::MAX / 2` if you will add.', example: 'let mut dist = vec![i64::MAX; n];' },
  { name: 'MIN', owner: 'i64', kind: 'constant', sig: 'i64::MIN = -9_223_372_036_854_775_808', doc: 'Smallest i64. `i64::MIN.abs()` overflows.', example: 'let mut best = i64::MIN;\nfor &x in &v { best = best.max(x); }' },
  { name: 'MAX', owner: 'usize', kind: 'constant', sig: 'usize::MAX = 18_446_744_073_709_551_615 (64-bit)', doc: 'Largest usize; sentinel for "unreached" in index-typed DP/BFS arrays. Adding 1 overflows.', example: 'let mut dist = vec![usize::MAX; n];\nif dist[v] == usize::MAX { }' },
  m('i64', 'abs', 'x.abs() -> i64', 'Absolute value. Overflows for `i64::MIN`. Literal needs a type: `(-5i64).abs()`. `abs_diff` gives `|a-b|` as u64.', { returns: 'i64 — |x|', example: '(-5i64).abs(); // 5' }),
  m('i64', 'pow', 'x.pow(exp) -> i64', 'Integer power; `exp` is `u32`. Overflow panics in debug.', { params: [{ label: 'exp', doc: 'u32 exponent' }], returns: 'i64 — x raised to exp', example: '2i64.pow(10); // 1024' }),
  m('i64', 'min', 'x.min(other) -> i64', 'Smaller of the two (method form of `std::cmp::min`).', { params: [{ label: 'other', doc: 'i64' }], returns: 'i64 — the smaller value', example: 'ans = ans.min(cur);' }),
  m('i64', 'max', 'x.max(other) -> i64', 'Larger of the two. Chains nicely: `best = best.max(cur)`.', { params: [{ label: 'other', doc: 'i64' }], returns: 'i64 — the larger value', example: 'best = best.max(cur);' }),
  m('i64', 'checked_add', 'x.checked_add(rhs) -> Option<i64>', '`None` on overflow (also `checked_sub`, `checked_mul`, `checked_div`). Good for "reverse integer"-style bounds checks.', { params: [{ label: 'rhs', doc: 'i64' }], returns: 'Option<i64> — Some(sum), or None on overflow', example: 'i64::MAX.checked_add(1); // None\n2i64.checked_add(3);      // Some(5)' }),
  m('i64', 'wrapping_mul', 'x.wrapping_mul(rhs) -> i64', 'Multiply with two\'s-complement wraparound, never panics (also `wrapping_add`, `wrapping_sub`). Useful for hashes.', { params: [{ label: 'rhs', doc: 'i64' }], returns: 'i64 — the product modulo 2^64', example: 'h = h.wrapping_mul(31).wrapping_add(c as i64);' }),
  m('i64', 'saturating_sub', 'x.saturating_sub(rhs) -> i64', 'Subtract, clamping at MIN/MAX. On `usize`, `i.saturating_sub(1)` stops at 0 instead of underflowing.', { params: [{ label: 'rhs', doc: 'same type' }], returns: 'i64 — x - rhs, clamped to the type\'s range', example: 'let lo = i.saturating_sub(k); // usize: never below 0' }),
  m('i64', 'rem_euclid', 'x.rem_euclid(rhs) -> i64', 'Non-negative modulo. `%` keeps the sign of the dividend (`-7 % 3 == -1`), `(-7i64).rem_euclid(3) == 2`.', { params: [{ label: 'rhs', doc: 'modulus' }], returns: 'i64 — remainder in [0, |rhs|)', example: '(-7i64).rem_euclid(3); // 2' }),
  m('i64', 'count_ones', 'x.count_ones() -> u32', 'Population count (number of set bits). Negative values count the two\'s-complement bits.', { returns: 'u32 — number of 1 bits', example: '13i64.count_ones(); // 3 (0b1101)' }),
  m('i64', 'leading_zeros', 'x.leading_zeros() -> u32', 'Zero bits above the highest set bit. `64 - x.leading_zeros()` = bit length.', { returns: 'u32 — count of leading 0 bits (64 for 0)', example: '1i64.leading_zeros(); // 63' }),
  m('i64', 'trailing_zeros', 'x.trailing_zeros() -> u32', 'Zero bits below the lowest set bit (64 for 0).', { returns: 'u32 — count of trailing 0 bits', example: '8i64.trailing_zeros(); // 3' }),
  m('i64', 'signum', 'x.signum() -> i64', '-1, 0, or 1.', { returns: 'i64 — -1, 0 or 1 by sign', example: '(-9i64).signum(); // -1' }),
  m('i64', 'to_string', 'x.to_string() -> String', 'Decimal string.', { returns: 'String — decimal representation', example: 'let s = 123i64.to_string(); // "123"' }),

  // ---------- char ----------
  ty('char', 'char', 'A Unicode scalar value (4 bytes). `c as u8` truncates to a byte (fine for ASCII); `b as char` only works from `u8`. Letter index: `(c as u8 - b\'a\') as usize`.', { example: "let c = 'z';\nlet idx = (c as u8 - b'a') as usize; // 25\nlet back = (b'a' + 2) as char;       // 'c'" }),
  m('char', 'is_ascii_digit', 'c.is_ascii_digit() -> bool', "True for '0'..='9'.", { returns: "bool — true for '0'..='9'", example: "'7'.is_ascii_digit(); // true" }),
  m('char', 'is_alphabetic', 'c.is_alphabetic() -> bool', 'Unicode letter test (`is_ascii_alphabetic` for ASCII only).', { returns: 'bool — true for letters', example: "let letters: String = s.chars().filter(|c| c.is_alphabetic()).collect();" }),
  m('char', 'is_alphanumeric', 'c.is_alphanumeric() -> bool', 'Letter or digit (`is_ascii_alphanumeric` for ASCII).', { returns: 'bool — true for letters and digits', example: "let clean: Vec<char> = s.chars().filter(|c| c.is_alphanumeric()).collect();" }),
  m('char', 'is_whitespace', 'c.is_whitespace() -> bool', 'Whitespace test.', { returns: 'bool — true for spaces, tabs, newlines, etc.', example: "' '.is_whitespace(); // true" }),
  m('char', 'is_ascii_lowercase', 'c.is_ascii_lowercase() -> bool', "True for 'a'..='z' (also `is_ascii_uppercase`).", { returns: "bool — true for 'a'..='z'", example: "'q'.is_ascii_lowercase(); // true" }),
  m('char', 'to_ascii_lowercase', 'c.to_ascii_lowercase() -> char', 'Lowercase ASCII letter, others unchanged (also `to_ascii_uppercase`). Returns a `char`, unlike `to_lowercase()` which returns an iterator.', { returns: 'char — lowercased copy', example: "'A'.to_ascii_lowercase(); // 'a'" }),
  m('char', 'to_ascii_uppercase', 'c.to_ascii_uppercase() -> char', 'Uppercase ASCII letter, others unchanged.', { returns: 'char — uppercased copy', example: "'a'.to_ascii_uppercase(); // 'A'" }),
  m('char', 'to_digit', 'c.to_digit(radix) -> Option<u32>', "Digit value: `'7'.to_digit(10) == Some(7)`. Faster ASCII alternative: `(c as u8 - b'0') as i64`.", { params: [{ label: 'radix', doc: 'base, e.g. 10 or 16' }], returns: 'Option<u32> — Some(digit value), or None if not a digit in radix', example: "let d = '7'.to_digit(10).unwrap() as i64; // 7" }),
  f('char', 'from_digit', 'char::from_digit(num, radix) -> Option<char>', "Digit to char: `char::from_digit(7, 10) == Some('7')`.", { params: [{ label: 'num', doc: 'u32 digit' }, { label: 'radix', doc: 'base' }], returns: 'Option<char> — Some(digit char), or None if num >= radix', example: "char::from_digit(7, 10); // Some('7')" }),
  f('char', 'from_u32', 'char::from_u32(i) -> Option<char>', 'Code point to char. For ASCII prefer `(b\'a\' + k) as char`.', { params: [{ label: 'i', doc: 'u32 code point' }], returns: 'Option<char> — None for invalid code points (e.g. surrogates)', example: "char::from_u32(65); // Some('A')" }),

  // ---------- std::mem / std::cmp ----------
  f('std::mem', 'swap', 'std::mem::swap(x, y)', 'Swap two `&mut` values. Can\'t take two `&mut` into the same Vec: use `v.swap(i, j)` there.', { header: 'use std::mem;', params: [{ label: 'x', doc: '&mut T' }, { label: 'y', doc: '&mut T' }], returns: '()', example: 'std::mem::swap(&mut a, &mut b);' }),
  f('std::mem', 'replace', 'std::mem::replace(dest, src) -> T', 'Put `src` into `*dest` and return the old value. Moves out of a `&mut` without cloning.', { header: 'use std::mem;', params: [{ label: 'dest', doc: '&mut T' }, { label: 'src', doc: 'new value' }], returns: 'T — the previous value of *dest', example: 'let old = std::mem::replace(&mut cur, Vec::new());' }),
  f('std::mem', 'take', 'std::mem::take(dest) -> T', 'Take the value, leaving `T::default()` behind (empty Vec, None, 0).', { header: 'use std::mem;', params: [{ label: 'dest', doc: '&mut T' }], returns: 'T — the previous value (dest now holds T::default())', example: 'let cur = std::mem::take(&mut next_level);' }),
  f('std::cmp', 'min', 'std::cmp::min(v1, v2) -> T', 'Smaller of two `Ord` values (returns `v1` on ties).', { header: 'use std::cmp::min;', params: [{ label: 'v1', doc: 'value' }, { label: 'v2', doc: 'value' }], returns: 'T — the smaller value', example: 'let m = std::cmp::min(a, b);' }),
  f('std::cmp', 'max', 'std::cmp::max(v1, v2) -> T', 'Larger of two `Ord` values (returns `v2` on ties).', { header: 'use std::cmp::max;', params: [{ label: 'v1', doc: 'value' }, { label: 'v2', doc: 'value' }], returns: 'T — the larger value', example: 'let m = std::cmp::max(a, b);' }),
  { name: 'Ordering', owner: 'std::cmp', kind: 'type', sig: 'enum Ordering { Less, Equal, Greater }', doc: 'Result of `a.cmp(&b)`. Combine keys with `.then(..)` / `.then_with(|| ..)`; flip with `.reverse()`. Match on it for three-way binary search.', header: 'use std::cmp::Ordering;', example: 'match nums[mid].cmp(&target) {\n    Ordering::Less => lo = mid + 1,\n    Ordering::Greater => hi = mid,\n    Ordering::Equal => return mid as i64, }' },
  m('Ord', 'cmp', 'a.cmp(other) -> Ordering', 'Total-order comparison; pass a reference: `a.cmp(&b)`. Floats only have `partial_cmp` / `total_cmp`.', { params: [{ label: 'other', doc: '&Self' }], returns: 'Ordering — Less, Equal or Greater', example: '1.cmp(&2); // Ordering::Less' }),
  m('Clone', 'clone', 'x.clone() -> T', 'Deep copy (for `Rc`, just a new pointer). Often the quick fix for "use of moved value" or borrow errors, at an O(n) cost for Vec/String.', { returns: 'T — an independent copy', example: 'let backup = v.clone();\nv.push(1); // backup unchanged' }),
  { name: 'usize', kind: 'type', sig: 'usize', doc: 'Unsigned pointer-sized integer, the type of indices and `len()`. Underflow (`0usize - 1`) panics in debug: compare before subtracting or use `checked_sub` / `wrapping_sub`.', example: 'let n: usize = v.len();\nif n > 0 { let last = v[n - 1]; }' },
  { name: 'f64', kind: 'type', sig: 'f64', doc: '64-bit float. Not `Ord`/`Hash`: sort with `sort_by(|a, b| a.total_cmp(b))`. Methods: `sqrt`, `abs`, `floor`, `round`, `powi`, `max`, `min`.', example: 'let r = (x as f64).sqrt();\nprintln!("{:.2}", r);' },

  // ---------- std::io ----------
  f('std::io', 'stdin', 'std::io::stdin() -> Stdin', 'Handle to standard input. Read a line with `read_line`, iterate with `lines()`, or read everything with `io::read_to_string`.', { header: 'use std::io;', returns: 'Stdin — shared handle to standard input', example: 'let mut line = String::new();\nio::stdin().read_line(&mut line).unwrap();' }),
  m('Stdin', 'read_line', 'stdin.read_line(buf) -> io::Result<usize>', 'Append the next line **including its `\\n`** to `buf`. Trim before `parse`, and `clear()` the buffer before reusing it. Returns `Ok(0)` at EOF.', { header: 'use std::io;', params: [{ label: 'buf', doc: '&mut String to append to' }], returns: 'io::Result<usize> — Ok(bytes read), Ok(0) at EOF', example: 'let mut s = String::new();\nio::stdin().read_line(&mut s).unwrap();\nlet n: usize = s.trim().parse().unwrap();', learn: {
      summary: "read one line of input into a String",
      what: "read_line reads the next line of standard input and appends it to a String you provide. You call it with a dot on the stdin handle: std::io::stdin().read_line(&mut s). The &mut means \"lend this String to read_line and allow it to change it\". The text is added to the end of whatever s already holds, and the newline at the end of the line is kept. Reading can fail, so the answer comes wrapped in a Result, which you usually open with .unwrap().",
      params: {
        stdin: "the input handle you call it on, before the dot: std::io::stdin()",
        buf: "a mutable borrow of the String to fill, written &mut s, where s was created with let mut s = String::new();"
      },
      returns: "io::Result<usize>: Ok(number of bytes read) on success, where 0 means the input has ended, or Err on an I/O error. Usually you just add .unwrap() and ignore the number.",
      example: "let mut answer = String::new();                    // empty String we may change\nstd::io::stdin().read_line(&mut answer).unwrap();  // e.g. \"yes\\n\" is appended\nlet answer = answer.trim();                        // drop the newline and spaces\nprintln!(\"{}\", answer == \"yes\");                   // true",
      watch: [
        "The newline stays: \"yes\" arrives as \"yes\\n\". Use .trim() before comparing or parsing.",
        "It appends: when reusing the same String in a loop, call s.clear() first.",
        "The String must be declared let mut and passed as &mut s, not s."
      ]
    }  }),
  m('Stdin', 'lines', 'stdin.lines() -> Lines<StdinLock>', 'Iterator over input lines (newline stripped). Each item is `io::Result<String>`, so `.unwrap()` it.', { header: 'use std::io;', returns: 'Lines — iterator of io::Result<String>', example: 'for line in io::stdin().lines() {\n    let line = line.unwrap();\n}' }),
  m('Stdin', 'lock', 'stdin.lock() -> StdinLock', 'Lock stdin once for faster repeated reads; the lock implements `BufRead`.', { header: 'use std::io::{self, BufRead};', returns: "StdinLock<'static> — a buffered, locked reader", example: 'let mut it = io::stdin().lock().lines();\nlet first = it.next().unwrap().unwrap();' }),
  f('std::io', 'read_to_string', 'std::io::read_to_string(reader) -> io::Result<String>', 'Read all remaining input into a new String: the simplest way to slurp stdin, then split it into tokens.', { header: 'use std::io;', params: [{ label: 'reader', doc: 'any io::Read, e.g. io::stdin()' }], returns: 'io::Result<String> — the whole input', example: 'let input = io::read_to_string(io::stdin()).unwrap();\nlet mut it = input.split_ascii_whitespace();' }),
  m('Read', 'read_to_string', 'r.read_to_string(buf) -> io::Result<usize>', 'Append all remaining bytes of a reader to `buf` (must be UTF-8). Needs the `Read` trait in scope.', { header: 'use std::io::Read;', params: [{ label: 'buf', doc: '&mut String to append to' }], returns: 'io::Result<usize> — Ok(bytes read)', example: 'let mut input = String::new();\nio::stdin().read_to_string(&mut input).unwrap();', learn: {
      summary: "read all remaining input at once",
      what: "read_to_string reads everything left on a reader (such as standard input) up to the end and appends it to a String you provide. Reading the whole input in one go and then splitting it is the simplest way to handle input spread over several lines or several values per line. It belongs to the Read trait (a trait is a named set of abilities a type can have), so you must bring it into scope with use std::io::Read; before you can call it with a dot.",
      params: {
        r: "the reader you call it on, before the dot: usually std::io::stdin()",
        buf: "a mutable borrow of the String to fill: &mut s, where let mut s = String::new();"
      },
      returns: "io::Result<usize>: Ok(number of bytes read) or Err on an I/O error. Normally you just .unwrap() it; the text is now in your String.",
      example: "use std::io::Read;                                    // enables read_to_string\nlet mut text = String::new();                         // empty buffer\nstd::io::stdin().read_to_string(&mut text).unwrap();  // whole input -> text\nprintln!(\"{} lines\", text.lines().count());           // e.g. 3 lines",
      watch: [
        "Without use std::io::Read; you get \"no method named read_to_string found\".",
        "It keeps every newline; split or trim the text before parsing."
      ]
    }  }),
  ty('BufRead', 'trait BufRead', 'Buffered-reader trait providing `lines()`, `read_line`, `split`. Implemented by `StdinLock` and `BufReader`; bring it into scope to call its methods.', { header: 'use std::io::BufRead;', example: 'use std::io::{self, BufRead};\nfor line in io::stdin().lock().lines() { let line = line.unwrap(); }' }),
  m('BufRead', 'lines', 'r.lines() -> Lines<Self>', 'Iterator over lines without the trailing newline; each item is `io::Result<String>`.', { header: 'use std::io::BufRead;', returns: 'Lines<Self> — iterator of io::Result<String>', example: 'let rows: Vec<String> = io::stdin().lock().lines().map(|l| l.unwrap()).collect();' }),
  ty('BufWriter', 'BufWriter<W>', 'Buffers writes to `W` (e.g. stdout) so thousands of `writeln!` calls don\'t each hit a syscall. Flushed on drop; call `out.flush()` if you need it earlier.', { header: 'use std::io::{BufWriter, Write};', example: 'let mut out = BufWriter::new(io::stdout().lock());\nfor x in &v { writeln!(out, "{}", x).unwrap(); }' }),
  f('BufWriter', 'new', 'BufWriter::new(inner) -> BufWriter<W>', 'Wrap a writer with an 8 KiB buffer. Write to it with `write!` / `writeln!` (needs `use std::io::Write`).', { header: 'use std::io::{BufWriter, Write};', params: [{ label: 'inner', doc: 'the io::Write to buffer, e.g. io::stdout().lock()' }], returns: 'BufWriter<W> — buffered writer', example: 'let mut out = BufWriter::new(io::stdout().lock());\nwriteln!(out, "{}", ans).unwrap();' }),
  f('std::io', 'stdout', 'std::io::stdout() -> Stdout', 'Handle to standard output; `.lock()` it and wrap in `BufWriter` for fast output.', { header: 'use std::io;', returns: 'Stdout — shared handle to standard output', example: 'let out = io::stdout();\nlet mut w = BufWriter::new(out.lock());' }),
];

// Beginner explanations for entries introduced by problems ("New in this problem" cards).
const LEARN = [
  ["String", "new", {
  "summary": "make a new, empty text string",
  "what": "Creates an empty `String`: a piece of text your program owns and can grow. You usually make one first and then let something fill it, for example `read_line`, which appends the line it reads. Declare it with `let mut` because filling it changes it.",
  "returns": "An empty `String` (`\"\"`), ready to be appended to.",
  "example": "let mut name = String::new();   // empty text, mutable so it can grow\nname.push_str(\"Ada\");            // name is now \"Ada\"\nprintln!(\"{}\", name);            // prints Ada",
  "watch": [
    "Without `mut`, any attempt to fill it fails with \"cannot borrow as mutable\"."
  ]
}],
  ["std::io", "stdin", {
  "summary": "get a handle to the program's input",
  "what": "Returns a handle to **standard input**, the text fed into your program (the keyboard in a terminal, the test input on Crucible). The handle itself does not read anything; you call a method on it, such as `.read_line(&mut s)` to read one line, or `.lines()` to loop over lines. Add `use std::io;` at the top so you can write `io::stdin()`.",
  "returns": "A `Stdin` handle. Call a reading method on it right away, e.g. `io::stdin().read_line(&mut s)`.",
  "example": "use std::io;                          // lets you write io::stdin()\nlet mut s = String::new();            // somewhere to put the text\nio::stdin().read_line(&mut s).unwrap(); // read one line into s\nprintln!(\"{} chars\", s.trim().len());  // trim drops the newline",
  "watch": [
    "Without `use std::io;` you must write the full path `std::io::stdin()`."
  ]
}],
];
for (const [owner, name, learn] of LEARN) { const e = entries.find((x) => x.owner === owner && x.name === name); if (e && !e.learn) e.learn = learn; }

export default entries;
