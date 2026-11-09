# ESPresso cheat sheet

ESPresso is a small scripting language for the ESP32: C-like control flow, JavaScript-ish
values, closures, and a bytecode VM. Everything on this page was tested against the
current build (`build/ESPresso file.espr`; add `--interp` to use the AST interpreter
instead of the VM). The language is young, so the **Missing** and **Known issues**
sections matter as much as the features.

## How Crucible calls your function

ESPresso is offered for function problems whose parameters are `int`, `float`, `bool`,
`int[]`, `float[]` or `int[][]`, whose result is `int` or `bool` (or `void` plus an
in-place change to an `int[]`), and whose test values stay below 2²⁴. Float results are
offered only when a problem's answers are known to print exactly. Function and parameter names are **camelCase**:
`count_presses(samples, k)` becomes `countPresses(samples, k)`.

| Crucible type | ESPresso value | notes |
|---|---|---|
| `int` | int | **32-bit**, wraps on overflow |
| `float` | float | **32-bit** (`float`), printed with 6 significant digits |
| `bool` | `true` / `false` | |
| `int[]`, `float[]` | array literal | passed **by reference** |
| `int[][]` | array of arrays | rows are arrays too |
| `void` + mutates | change the array in place | the harness prints it afterwards |

Your file is loaded and one line per test is appended, then everything runs in one VM:

```javascript
fn sumArray(nums) {
    var s = 0
    for var i in 0..len(nums) { s += nums[i] }
    return s
}
print("@@CRUCIBLE", 0, sumArray([1, 2, 3]))   // what the harness appends
```

Harness limits to keep in mind: a problem's tests must fit in one chunk (at most 256
constants: every number in every test counts), and integer **literals** above 2²⁴ =
16 777 216 lose precision (see Known issues). Arithmetic results are exact up to 2³¹.

## Comments, statements, blocks

```javascript
// line comments only: /* block comments */ are not supported
var a = 1
var b = 2; var c = 3          // semicolons are optional separators
if a < b { print("braces are required, parentheses are not") }
if (a < b) { print("parentheses are allowed too") }
```

## Variables & types

```javascript
var count = 0            // mutable
const LIMIT = 100        // intended as constant (reassignment is not rejected yet)
var ratio = 0.5          // float
var on = true            // bool
var nothing = null
var name = "esp32"       // string
var buf = [0, 0, 0]      // array: fixed size from now on
var pt = {x: 3, y: 4}    // object (up to 16 keys)
print(typeOf(count), typeOf(ratio), typeOf(on), typeOf(nothing))   // int float bool null
print(typeOf(name), typeOf(buf), typeOf(pt), typeOf(print))       // string array object native
```

Reading an undeclared variable gives `null` (no error), so typos fail silently.
`var` may redeclare a name in the same scope.

## Operators

| op | behaviour | example |
|---|---|---|
| `+ - *` | int op int → int (32-bit wrap); any float → float | `100000 * 100000` → `1410065408` |
| `/` | int / int **truncates toward zero** | `7 / 2` → `3`, `-7 / 2` → `-3`, `7 / 2.0` → `3.5` |
| `%` | **not supported** | use `a - (a / b) * b` |
| `== !=` | ints, floats, bools, strings by value; `1 == 1.0` is `true` | arrays compare by identity |
| `< <= > >=` | numbers only | strings give wrong answers |
| `and or !` | logical, short-circuit | `and`/`or` return an operand: `1 and 0` → `0` |
| `&& \|\|` | same as `and`/`or`, **but break inside call arguments** | prefer `and`/`or` |
| `+=  -=  *=  /=` | also on `arr[i]` and `obj.field` | `buf[2] *= 2` |
| unary `-` | negation | `-x * 2` |
| `& \| ^ ~ << >>` `++` `--` `%` `**` | **not supported** | see idioms below |

Falsy values: `false`, `null`, `0`, and (it seems) `[]`. Everything else is truthy.

```javascript
var x = 17
var r = x - (x / 5) * 5          // 2: manual modulo (same sign rule as C's %)
var half = x / 2                 // 8: right shift by 1 for x >= 0
var low = x - (x / 2) * 2        // 1: lowest bit
var f = 7 / 2.0                  // 3.5: one float operand makes it float
var s = 0.0
s += 7
print(r, half, low, f, s / 2)    // 2 8 1 3.5 3.5
```

## Conditionals

```javascript
var score = 85
if score >= 90 {
    print("A")
} else if score >= 80 {
    print("B")
} else {
    print("C")
}
if score > 50 and !(score > 99) { print("in range") }
```

There is no ternary `?:` and no `switch`.

## Loops

```javascript
for var i in 0..5 { print(i) }            // 0 1 2 3 4 (end exclusive)
var n = 3
for var i in 0..n { n = 10 }              // the range is evaluated once
var k = 10
while k > 0 { k -= 3 }                    // general loop
var t = 0
while true {
    t += 1
    if t == 2 { continue }
    if t == 4 { break }
}
var j = 9                                  // counting down: use while
while j >= 0 { j -= 3 }
print(k, t, j)                             // -2 4 -3
```

`for … in` only takes a range (`a..b`), not an array; loop over indices with
`0..len(arr)`. Ranges can't step or count down. Assigning to the loop variable inside
the body changes the iteration, as in C.

## Functions & closures

```javascript
fn clamp(v, lo, hi) {
    if v < lo { return lo }
    if v > hi { return hi }
    return v
}
fn makeCounter() {            // closures capture variables, not values
    var n = 0
    fn tick() {
        n += 1
        return n
    }
    return tick
}
var c = makeCounter()
c()
var square = fn(v) { return v * v }        // anonymous function expression
fn twice(f, x) { return f(f(x)) }          // functions are values
print(clamp(300, 0, 255), c(), square(5), twice(square, 3))   // 255 2 25 81
```

- Define a function **before** the line that calls it (no hoisting).
- Calls must pass exactly the declared number of arguments.
- `return` with no value returns `null`.
- Recursion depth is limited to about **60** calls (64 VM frames). Prefer loops.

## Strings

```javascript
var name = "ESPresso"
var greeting = "Hello, " + name + "!"      // + concatenates
var n = 3
print("n = {n}, next = {n + 1}")           // {expr} interpolation
print(len(name), name == "ESPresso")       // 8 true
print("v" + 2, "ok: " + true)              // + converts numbers and bools: v2 ok: true
var s = "ab"
s += "cd"
print(s)                                   // abcd
```

Strings **cannot be indexed** (`s[0]` is an error), and there are no `substr`, `split`,
`toUpper` or char-code functions. Use arrays of numbers when you need characters.

## Arrays

```javascript
var a = [5, 3, 8, 1]
a[0] = 9
a[1] += 10
print(a, len(a), a[len(a) - 1])         // [9, 13, 8, 1] 4 1
var grid = [[1, 2, 3], [4, 5, 6]]
grid[1][2] = 60
print(grid[1], len(grid), len(grid[0])) // [4, 5, 60] 2 3
var empty = []
print(len(empty))                       // 0
```

Arrays **never grow**: no `push`, `pop`, `concat`, slicing, or `[0] * n`. Indexing past
the end (or with a negative index) is a runtime error. The idiom is a fixed-size buffer
plus a count:

```javascript
var buf = [0, 0, 0, 0, 0, 0, 0, 0]   // capacity 8, allocated once
var count = 0
fn push(v) {
    if count == len(buf) { return false }   // full
    buf[count] = v
    count += 1
    return true
}
push(4)
push(7)
print(count, buf[0], buf[1])             // 2 4 7
```

No built-in `sort`, `reverse`, `min`, `max` or `sum`. Write the loops:

```javascript
fn arrMax(a) {
    var best = a[0]
    for var i in 1..len(a) { if a[i] > best { best = a[i] } }
    return best
}
fn reverseInPlace(a) {
    var i = 0
    var j = len(a) - 1
    while i < j {
        var t = a[i]
        a[i] = a[j]
        a[j] = t
        i += 1
        j -= 1
    }
}
fn insertionSort(a) {
    for var i in 1..len(a) {
        var v = a[i]
        var j = i - 1
        while j >= 0 and a[j] > v {     // `and` short-circuits, so a[-1] is never read
            a[j + 1] = a[j]
            j -= 1
        }
        a[j + 1] = v
    }
}
var xs = [4, 1, 3, 2]
insertionSort(xs)
reverseInPlace(xs)
print(xs, arrMax(xs))                   // [4, 3, 2, 1] 4
```

**Passing vs assigning.** Arrays and objects are passed to functions by reference (the
function can modify the caller's array). But `var b = a` at the top level of a script
**copies**, while inside a function it **aliases**. Don't depend on either; mutate
through parameters.

## Objects (structs)

```javascript
var dev = {id: 7, name: "esp32", meta: {ok: true}}
dev.name = "espresso"
dev.mode = "demo"                  // add a key
dev["id"] += 1                     // bracket access with a string key
dev.meta.ok = false
print(dev.id, dev.meta.ok, dev.missing)   // 8 false null
fn bump(o) { o.id += 1 }           // passed by reference
bump(dev)
print(dev.id)                      // 9
```

At most 16 keys per object, keys up to 31 characters. There is no key iteration.

## Hash maps, sets, stacks, queues

None are built in. Embedded-style substitutes:

| need | ESPresso idiom |
|---|---|
| map with small int keys | a counts array: `freq[v] += 1` (offset negatives: `freq[v + 100]`) |
| set of small ints | array of `0`/`1` flags |
| map with a few string keys | an object: `o[key]` (≤ 16 keys) |
| stack | fixed array + `top` index |
| queue / FIFO | ring buffer: fixed array + `head`, `tail`, `count`; wrap with `if i == cap { i = 0 }` |
| heap | fixed array + sift up/down loops |

```javascript
var stack = [0, 0, 0, 0]
var top = 0
stack[top] = 5
top += 1                          // push 5
top -= 1
var popped = stack[top]           // pop
var q = [0, 0, 0]
var head = 0
var tail = 0
q[tail] = 9
tail += 1
if tail == len(q) { tail = 0 }    // enqueue with wrap-around
var front = q[head]
head += 1
if head == len(q) { head = 0 }    // dequeue
print(popped, front)              // 5 9
```

## Output, errors, modules

```javascript
print("a", 1, 2.5, true, null, [1, 2])   // space-separated: a 1 2.5 true null [1, 2]
log("same as print")
try {
    var z = 1 / 0
} catch e {
    print("caught: " + e)                // caught: Division by zero.
}
import "json"
print(json.stringify({x: 1}), json.parse("{\"y\": 2}").y)
print(millis() >= 0)                     // milliseconds since start
```

Other built-ins: `len(x)` (arrays and strings), `typeOf(x)`. On the ESP32, modules
`"gpio"` (`pinMode`, `digitalWrite`…), `"time"` (`delay`, `setTimeout`, `setInterval`)
and `"event"` (`on`, `emit`) talk to hardware. There is no stdin reading, so `io`
problems with input aren't available in ESPresso.

## Missing (use the idiom)

| missing | workaround |
|---|---|
| `%` | `a - (a / b) * b` |
| bit operators, shifts | `* 2` / `/ 2` for non-negative values; `x - (x / 2) * 2` for the low bit |
| `++`, `--` | `i += 1` |
| `abs`, `min`, `max`, `floor` | small helper functions |
| float → int conversion | none; keep values as ints (scaled or fixed point) |
| growing arrays, `push`, slices | pre-sized buffer + count |
| string indexing / methods | arrays of numbers |
| `for x in array` | `for var i in 0..len(a)` |
| descending or stepped ranges | `while` |
| `switch`, ternary `?:` | `if / else if` |
| `throw` | not available; only runtime errors are catchable |
| exponent literals (`1e3`), `/* */` comments | write `1000`, use `//` |

## Known issues (as of this build)

- **Returning an array or object held in a variable** returns garbage:
  `fn mk() { var r = [1, 2]; return r }` gives `[<unknown>, 0]`. Returning a literal
  (`return [a, b]`) works. Crucible's ESPresso problems never need to return arrays.
- **Integer literals above 2²⁴ are rounded** (they're parsed through a 32-bit float):
  `16777217` reads as `16777216`. Computed values are exact.
- **`&&` / `||` inside call arguments** fail: `print(a && b)` → "Can only call functions…".
  Use `and` / `or`.
- **String `<` / `>`** don't compare contents: `"z" < "a"` is `true`.
- `const` doesn't prevent reassignment.
- Runtime errors inside arrays/functions may report `[line 0]`.
- Calling an undefined function reports "Can only call functions and native functions in
  VM", which usually means a typo or a function defined later in the file.

## Common gotchas

- `sum / count` with two ints truncates. Start accumulators at `0.0` for float results.
- `2147483647 + 1` wraps to `-2147483648` silently. Keep products below 2³¹.
- Floats are single precision: about 7 significant digits.
- No hoisting: put helper functions above the function that calls them.
- Use `and`/`or`, not `&&`/`||`.
- Default to loops over recursion (depth ≈ 60).
