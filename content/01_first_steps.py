"""Track 1: First Steps. The very first programs: output, input, functions, types."""

import random

_rng = random.Random(101)

TRACK = dict(
    id="first-steps",
    title="First Steps",
    order=1,
    icon="✦",
    blurb="Your very first programs: printing, reading input, writing functions, and the types that hold your data.",
    intro=r"""
Welcome to Crucible. This track assumes you have never written a program before. By the end of it you will have written twenty small but real programs, in whichever language you choose, and you will know how to read a problem, test your idea, and learn from the reference solution.

## What a program actually is

A program is a list of instructions that the computer follows **in order, from top to bottom**, one at a time. It never guesses what you meant and it never skips ahead. When something goes wrong, it is almost always because the computer did *exactly* what you wrote, which was not quite what you meant. That is not a failure; it is how every programmer spends their day.

Every program you write here does some mix of three things:

```
   input  ──►  [ your instructions ]  ──►  output
 (data in)       (compute something)     (data out)
```

* **Input** is data that arrives from outside: text someone typed, or values handed to a function.
* **Processing** is the arithmetic, comparisons and decisions in between.
* **Output** is the result: text printed on the screen, or a value handed back from a function.

## Two kinds of problems

Crucible problems come in two shapes, and it matters which one you are looking at.

**Program problems** (marked *stdin → stdout*) are complete programs. Your code reads text from **standard input** (stdin, think of it as "the keyboard") and writes text to **standard output** (stdout, "the screen"). Crucible feeds the test input in for you and compares what you print, line by line, to the expected text. Trailing spaces and trailing blank lines are ignored, but everything else must match exactly: `Hello, World!` is not `hello world`.

**Function problems** ask you to fill in the body of a single **function**: a named, reusable piece of code that receives values (its **parameters**) and gives one value back with `return`. Crucible calls your function with each test's arguments and checks the value you returned. In a function problem you should **not** print the answer; printing is like saying the answer out loud, returning is like handing it over. Only the handed-over value is checked.

Here is the same tiny function in the four main languages:

```python
def add(a: int, b: int) -> int:
    return a + b
```

```c
long long add(long long a, long long b) {
    return a + b;
}
```

```cpp
long long add(long long a, long long b) {
    return a + b;
}
```

```rust
pub fn add(a: i64, b: i64) -> i64 {
    a + b // the last expression, with no semicolon, is the return value
}
```

Notice that C, C++ and Rust spell out the **type** of every value: `long long` and `i64` are 64-bit whole numbers, `double` and `f64` are decimal numbers, `bool` is true/false. Python figures types out while the program runs, so the `: int` annotations are documentation, not rules. Types matter because they decide what operations mean: `7 / 2` is `3` for integers in C, C++ and Rust, but `3.5` in Python.

## How code runs in each language

* **Python** is *interpreted*: a program reads your file and executes it line by line. Errors show up when the faulty line runs.
* **C, C++ and Rust** are *compiled*: a compiler first translates your whole file into machine code, and only then does it run. Many mistakes (a missing semicolon, a wrong type) are caught before anything runs, as a **compile error**. Read those messages from the top; the first error is usually the real one.
* **ESPresso** is a small scripting language that is offered whenever a problem only uses numbers, booleans and number arrays.

## How Crucible works

Each problem page has the **statement** (what to compute), a few **examples**, the **constraints** (how big the inputs can be), and an editor with **starter code**. In this track the starter code contains `TODO` comments that tell you exactly what to type for the first several problems. Read them; they explain what every line of the skeleton is for.

* **Run** executes your code against the example tests only. Use it often: it is fast and shows you what your code produced next to what was expected.
* **Submit** runs every test, including hidden edge cases such as zero, negative numbers, empty arrays and very large values. A problem counts as solved when all of them pass.
* **Hints** are progressive. The first is a gentle nudge, the last is nearly the answer. Take one when you are stuck for more than a few minutes; that is what they are for.
* **The AI Coach** can look at your code and nudge you toward the bug without handing you the answer. Ask it things like "why does test 3 fail?" or "what does this compile error mean?".
* After you solve a problem, the **explanation** and the commented **reference solutions** unlock. Read them even when you passed: they often show a cleaner way, or a trap you happened to avoid.

## How to read a problem

1. **Read the whole statement twice.** Underline the input, the output, and any exact wording of the output.
2. **Work an example by hand.** If you cannot compute the answer with a pencil, you cannot tell the computer how to.
3. **Check the constraints.** Can a number be negative? Zero? Can the array be empty? Can values be bigger than 2 billion (which matters in C)?
4. **Write the simplest thing that works**, press Run, and compare.
5. **Then think about edge cases** before you press Submit.

## Reading test results

When a test fails you will see the input, the **expected** output and what your code **got**. Compare them character by character. Common surprises: a missing newline, an extra space, `True` versus `true`, or printing inside a function problem. If your code crashes, the error message tells you the line; in C a crash with no message often means you read memory you did not own.

Take your time with this track. Every later track builds on exactly these habits: read carefully, compute by hand, write the simplest version, test the edges.
""",
)

PROBLEMS = []

# ----------------------------------------------------------------------------
# 1. Hello, World!
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="hello-world",
    title="Hello, World!",
    difficulty=0,
    kind="io",
    tags=["output", "basics"],
    statement=r"""
The traditional first program in every language: make the computer say hello.

Write a program that prints exactly this line:

```text
Hello, World!
```

There is no input. Capital `H`, capital `W`, a comma after `Hello`, one space, and an exclamation mark at the end.
""",
    examples=1,
    constraints=["No input is given."],
    hints=[
        "Every language has one built-in way to print a line of text. Find it in the starter code's TODO comment.",
        "Text in code goes inside double quotes: `\"Hello, World!\"`. The quotes are not printed; they just mark where the text starts and ends.",
        "Python: `print(\"Hello, World!\")`. C: `printf(\"Hello, World!\\n\");`. C++: `cout << \"Hello, World!\" << endl;`. Rust: `println!(\"Hello, World!\");`.",
    ],
    starters={
        "python": r'''# Welcome to your very first program!
# Python runs this file from the top line to the bottom line.
#
# TODO: on the empty line below, type exactly:
#     print("Hello, World!")
#
# - print(...) is a built-in function that writes text to the screen.
# - The double quotes make "Hello, World!" a *string* (a piece of text).
# - print automatically adds a newline after the text.

''',
        "c": r'''#include <stdio.h>   // brings in printf, the "standard input/output" library

// Every C program starts running at the first line inside main().
// `int` means main gives back a whole number to the operating system.
int main(void) {
    // TODO: type the following line (including the semicolon):
    //     printf("Hello, World!\n");
    //
    // - printf prints text exactly as written; it does NOT add a newline.
    // - "\n" inside the quotes is the newline character, so we add it ourselves.
    // - Every statement in C ends with a semicolon ;

    return 0;   // 0 means "the program finished successfully"
}
''',
        "cpp": r'''#include <bits/stdc++.h>   // brings in the whole standard library, including cout
using namespace std;       // lets us write cout instead of std::cout

// Every C++ program starts running inside main().
int main() {
    // TODO: type the following line (including the semicolon):
    //     cout << "Hello, World!" << endl;
    //
    // - cout is the "character output" stream: the screen.
    // - << pushes the value on its right into the stream, left to right.
    // - endl writes a newline (and flushes the output).

    return 0;   // 0 means "the program finished successfully"
}
''',
        "rust": r'''// Every Rust program starts running inside fn main().
fn main() {
    // TODO: type the following line (including the semicolon):
    //     println!("Hello, World!");
    //
    // - println! is a *macro* (the ! marks it): it prints text plus a newline.
    // - The text goes inside double quotes.
}
''',
        "espresso": r'''// ESPresso runs this file from top to bottom.
//
// TODO: type the following line:
//     print("Hello, World!")
//
// print writes its arguments followed by a newline. No semicolon needed.

''',
    },
    explanation=r"""
## Intuition

There is nothing to compute here. The whole point is to learn the one instruction you will use more than any other: **put text on the screen**. Each language has its own spelling, but the idea is identical: hand a piece of text (a **string**) to the output.

## Approach

A string is written between double quotes. The quotes tell the language "this is data, not code", and they are not printed.

```python
print("Hello, World!")          # print adds the newline for you
```

```c
#include <stdio.h>
int main(void) {
    printf("Hello, World!\n");  // \n is the newline; printf never adds one
    return 0;
}
```

```cpp
#include <iostream>
int main() {
    std::cout << "Hello, World!" << std::endl;  // << feeds values into cout
}
```

```rust
fn main() {
    println!("Hello, World!");  // the ! means println is a macro
}
```

What happens when you press Run:

| step | Python | C / C++ / Rust |
|---|---|---|
| 1 | interpreter reads the file | compiler translates the whole file to machine code |
| 2 | executes line 1: prints | runs `main()`, which prints |
| 3 | reaches end of file, stops | `main` returns 0, program ends |

The **entry point** is where execution begins. Python starts at the top of the file. C, C++ and Rust start at a function called `main`, no matter where it sits in the file. In C and C++, `main` returns an `int`: `0` means success, anything else signals an error to whoever started the program.

The `\n` sequence is an **escape**: a backslash followed by a letter that stands for a character you cannot easily type inside quotes. `\n` is newline, `\t` is tab, `\"` is a literal double quote, `\\` is a literal backslash.

## Complexity

Constant time and space: the program does one thing, once.

## Common mistakes

* **Spelling and punctuation.** The checker compares text exactly. `Hello World!` (no comma) or `hello, world!` (lowercase) fail.
* **Curly quotes.** If you copy text from a word processor you may get `“` and `”`, which are not valid in code. Use the plain `"` key.
* **Forgetting the semicolon** in C, C++ and Rust. The compiler error usually points to the *next* line, because that is where it noticed something was missing.
* **`print` vs `printf` vs `println!`.** Mixing languages up is normal at first. Python has `print`, C has `printf`, Rust has `println!` with the exclamation mark.

## Going further

Try printing two lines. In Python call `print` twice; in C put two `\n` in one `printf`: `printf("Hello,\nWorld!\n");`. Notice how the newline character is just another character in the string.
""",
    solution=r'''# The whole program is one call to the built-in print function.
# The text between the quotes is a string literal; print writes it to
# standard output and then writes a newline character after it.
print("Hello, World!")
''',
    refs={
        "c": r'''#include <stdio.h>   // declares printf

int main(void) {
    // printf copies the string to standard output exactly as written.
    // It never adds a newline on its own, so "\n" ends the line.
    printf("Hello, World!\n");
    return 0;            // tell the operating system we succeeded
}
''',
        "cpp": r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    // cout is the standard output stream; << sends values into it in order.
    // endl writes '\n' and flushes, so the text appears immediately.
    cout << "Hello, World!" << endl;
    return 0;
}
''',
        "rust": r'''fn main() {
    // println! formats its arguments, prints them, then prints a newline.
    println!("Hello, World!");
}
''',
        "espresso": r'''// print writes its argument followed by a newline.
print("Hello, World!")
''',
    },
    tests=["", "", "", "", "", ""],
))

# ----------------------------------------------------------------------------
# 2. Return the answer
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="return-the-answer",
    title="Return the Answer",
    difficulty=0,
    tags=["functions", "return"],
    fn="the_answer",
    params=[],
    returns="int",
    statement=r"""
Your first **function**. A function is a named block of code that can be *called*; when it finishes it can hand one value back to whoever called it, using `return`.

Complete the function `the_answer` so that it returns the integer `42`.

It takes no parameters. Do **not** print anything: Crucible calls your function and checks the value it returns.
""",
    examples=1,
    constraints=["The function takes no arguments."],
    hints=[
        "The keyword that hands a value back from a function is `return`.",
        "Replace the placeholder in the starter (`pass`, or `return 0`, or `0` in Rust) with the number 42.",
        "Python: `return 42`. C / C++: `return 42;`. Rust: the last line of the body is just `42` (no semicolon), or `return 42;`.",
    ],
    starters={
        "python": r'''# `def` starts a function definition.
#   the_answer   -> the function's name
#   ()           -> its parameter list (empty: it needs no input)
#   -> int       -> a note saying it gives back an integer
#   :            -> the indented lines below are the function's body
def the_answer() -> int:
    # TODO: replace `pass` with:   return 42
    # `return` ends the function and hands the value back to the caller.
    pass
''',
        "c": r'''#include <stdio.h>
#include <stdbool.h>

// long long     -> the type of value this function gives back (a 64-bit integer)
// the_answer    -> the function's name
// ()            -> no parameters
// { ... }       -> the body: the statements that run when it is called
long long the_answer() {
    // TODO: change 0 to 42 below.
    // `return` stops the function and hands that value to the caller.
    return 0;
}
''',
        "cpp": r'''#include <bits/stdc++.h>
using namespace std;

// long long     -> the type of value this function gives back (a 64-bit integer)
// theAnswer     -> the function's name (C++ problems here use camelCase names)
// ()            -> no parameters
long long theAnswer() {
    // TODO: change 0 to 42 below.
    // `return` stops the function and hands that value to the caller.
    return 0;
}
''',
        "rust": r'''// pub fn       -> a public function definition
// the_answer   -> its name
// ()           -> no parameters
// -> i64       -> it returns an i64 (a 64-bit signed integer)
pub fn the_answer() -> i64 {
    // TODO: change 0 to 42.
    // In Rust, the last expression in a body, written WITHOUT a semicolon,
    // is the value the function returns. So this line *is* the return.
    0
}
''',
        "espresso": r'''// fn          -> starts a function definition
// theAnswer   -> its name
// ()          -> no parameters
fn theAnswer() {
    // TODO: change 0 to 42 below.
    return 0
}
''',
    },
    explanation=r"""
## Intuition

A function is like a recipe card with a name on it. **Defining** it writes the card; **calling** it follows the recipe. When the recipe says `return 42`, the cook stops and hands back a plate with `42` on it. Whoever called the function receives that value and can store it, print it, or do arithmetic with it.

Crucible's test harness is the caller here. It does roughly this behind the scenes:

```python
result = the_answer()      # call your function, catch what it hands back
check(result == 42)        # compare with the expected value
```

## Approach

Put `42` after `return`. The interesting part is the anatomy of a function definition, which is slightly different in each language:

```python
def the_answer() -> int:     # name, parameters, (optional) return type
    return 42                # body is indented
```

```c
long long the_answer() {     // return type comes FIRST in C
    return 42;               // body inside { }, statements end with ;
}
```

```cpp
long long theAnswer() {
    return 42;
}
```

```rust
pub fn the_answer() -> i64 { // return type comes after ->
    42                       // last expression without ; is returned
}
```

In C, C++ and Rust the return type is mandatory and enforced: if the function says it returns a `long long`, you must return a whole number. Python's `-> int` is only a hint for humans and tools.

### Return is not print

This is the single most important beginner distinction:

| | `print(42)` | `return 42` |
|---|---|---|
| where does 42 go? | to the screen, as text | back to the caller, as a value |
| can the caller use it? | no | yes: `x = the_answer() + 1` |
| does the function stop? | no | yes, immediately |

If you `print` in a function problem, the test sees no returned value (Python returns `None` by default) and fails.

## Complexity

Constant time, constant space.

## Common mistakes

* **Printing instead of returning.** Covered above; it is the classic first-function bug.
* **Rust semicolon trap.** `42;` with a semicolon turns the expression into a statement whose value is `()` ("nothing"), and the compiler complains *mismatched types: expected i64, found ()*. Either drop the semicolon or write `return 42;`.
* **Returning a string.** `return "42"` is text, not a number; the types differ, and in C/C++/Rust it will not compile.

## Going further

Once a function exists, it can be called as many times as you like. Try (in your head) `the_answer() + the_answer()`: the function runs twice and the result is 84.
""",
    solution=r'''def the_answer() -> int:
    # `return` immediately ends the function and hands 42 back to whoever
    # called it. Nothing is printed: the caller (the test harness) receives
    # the value itself and compares it with the expected answer.
    return 42
''',
    refs={
        "c": r'''long long the_answer() {
    // The return type (long long) is declared before the name.
    // `return 42;` ends the function and gives 42 to the caller.
    return 42;
}
''',
        "cpp": r'''long long theAnswer() {
    // Same as C: return type first, then name, then the body.
    return 42;
}
''',
        "rust": r'''pub fn the_answer() -> i64 {
    // The final expression without a semicolon is the function's value.
    // Writing `return 42;` would also work, but this is idiomatic Rust.
    42
}
''',
        "espresso": r'''fn theAnswer() {
    // Hand 42 back to the caller.
    return 42
}
''',
    },
    tests=[[], [], [], [], [], []],
))

# ----------------------------------------------------------------------------
# 3. Add two integers
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="add-two-integers",
    title="Add Two Integers",
    difficulty=0,
    tags=["functions", "parameters", "arithmetic"],
    fn="add",
    params=[["a", "int"], ["b", "int"]],
    returns="int",
    statement=r"""
Functions become useful when they take **parameters**: values the caller passes in.

Complete `add(a, b)` so that it returns the sum `a + b`.
""",
    constraints=["-10⁹ ≤ a, b ≤ 10⁹"],
    example_notes=["2 + 3 = 5.", "Negative numbers work the same way: -4 + 10 = 6."],
    hints=[
        "Inside the function, `a` and `b` already hold the two numbers the caller passed in. You do not read them from anywhere.",
        "The `+` operator adds two numbers. Return its result.",
        "One line: `return a + b` (with a `;` in C/C++, or just `a + b` as the last line in Rust).",
    ],
    starters={
        "python": r'''# a and b are *parameters*: when the tests call add(2, 3),
# a becomes 2 and b becomes 3 for the duration of this call.
def add(a: int, b: int) -> int:
    # TODO: replace `pass` with:   return a + b
    pass
''',
        "c": r'''#include <stdio.h>
#include <stdbool.h>

// Each parameter is written as  <type> <name>.
// long long is a 64-bit whole number (it can hold values up to about 9.2e18).
long long add(long long a, long long b) {
    // TODO: replace 0 with  a + b
    return 0;
}
''',
        "cpp": r'''#include <bits/stdc++.h>
using namespace std;

// Each parameter is written as  <type> <name>.
long long add(long long a, long long b) {
    // TODO: replace 0 with  a + b
    return 0;
}
''',
        "rust": r'''// Each parameter is written as  <name>: <type>.
// i64 is a 64-bit signed integer.
pub fn add(a: i64, b: i64) -> i64 {
    // TODO: replace 0 with  a + b   (keep it without a semicolon)
    let _ = (a, b); // (this line only silences "unused variable" warnings; delete it)
    0
}
''',
        "espresso": r'''// ESPresso parameters have no written types.
fn add(a, b) {
    // TODO: replace 0 with  a + b
    return 0
}
''',
    },
    explanation=r"""
## Intuition

A parameter is a **named placeholder** for a value that will be supplied later. When the test harness calls `add(2, 3)`, the language creates two fresh variables for that call, `a = 2` and `b = 3`, runs the body, and throws them away when the function returns. The next call, `add(-4, 10)`, gets its own fresh `a` and `b`.

## Approach

Return `a + b`.

```python
def add(a: int, b: int) -> int:
    return a + b
```

```c
long long add(long long a, long long b) {
    return a + b;
}
```

```cpp
long long add(long long a, long long b) {
    return a + b;
}
```

```rust
pub fn add(a: i64, b: i64) -> i64 {
    a + b
}
```

Trace of a call:

| call | a | b | `a + b` | returned |
|---|---|---|---|---|
| `add(2, 3)` | 2 | 3 | 5 | 5 |
| `add(-4, 10)` | -4 | 10 | 6 | 6 |
| `add(10⁹, 10⁹)` | 1000000000 | 1000000000 | 2000000000 | 2000000000 |

### Why the types matter

In C, C++ and Rust every integer type has a fixed size. A 32-bit `int` can hold at most 2,147,483,647, so two billion plus a little would **overflow**: in C it silently wraps to a negative number (technically undefined behaviour), in Rust a debug build stops with a panic. Crucible uses 64-bit integers (`long long`, `i64`) for every `int` parameter, which hold up to about 9.2 × 10¹⁸, so sums of values up to 10⁹ are safe. Python integers grow as large as needed and never overflow.

## Complexity

One addition: O(1) time and O(1) space.

## Common mistakes

* **Reading input inside a function problem.** The values are already in `a` and `b`. Calling `input()` or `scanf` here would wait forever for text that never comes.
* **Using `int` instead of `long long` in C** when you write your own helper variables. Habitually use `long long` in this site's C code.
* **Rust's trailing semicolon.** `a + b;` returns `()`, not the sum.

## Going further

Parameters can be any type. A function `add3(a, b, c)` would simply list three parameters. Functions can also call other functions: `add(add(1, 2), 3)` evaluates the inner call first (3), then the outer one (6).
""",
    solution=r'''def add(a: int, b: int) -> int:
    # The caller has already placed the two numbers in the parameters
    # `a` and `b`; we only need to combine them and hand the result back.
    # Python integers never overflow, so no special care is needed for
    # large values (unlike 32-bit integers in C).
    return a + b
''',
    refs={
        "c": r'''long long add(long long a, long long b) {
    // long long is 64 bits wide, so the sum of two values of size 10^9
    // (about 2 * 10^9) fits comfortably. A 32-bit int would be too small.
    return a + b;
}
''',
        "cpp": r'''long long add(long long a, long long b) {
    // Identical to C: the parameter types say exactly what arrives.
    return a + b;
}
''',
        "rust": r'''pub fn add(a: i64, b: i64) -> i64 {
    // Last expression, no semicolon: this is the returned value.
    a + b
}
''',
        "espresso": r'''fn add(a, b) {
    return a + b
}
''',
    },
    tests=[[2, 3], [-4, 10], [0, 0], [-7, -8], [1000000000, 1000000000], [123456, -123456], [-1000000000, 1], [999, 1]],
))

# ----------------------------------------------------------------------------
# 4. Square a number (return vs print)
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="square-a-number",
    title="Square a Number",
    difficulty=0,
    tags=["functions", "arithmetic"],
    fn="square",
    params=[["n", "int"]],
    returns="int",
    statement=r"""
Complete `square(n)` so that it **returns** `n` multiplied by itself.

Remember: return the value, do not print it.
""",
    constraints=["-46340 ≤ n ≤ 46340"],
    example_notes=["3 × 3 = 9.", "A negative times a negative is positive: (-5) × (-5) = 25."],
    hints=[
        "Multiplication is written with `*` in every language here.",
        "`n * n` is the square of `n`.",
        "Return it: `return n * n` (Python, C, C++, ESPresso) or `n * n` as the last line in Rust.",
    ],
    starters={
        "python": r'''def square(n: int) -> int:
    # TODO: replace `pass` with:   return n * n
    # Note: `n ^ 2` does NOT square in Python (^ is bitwise XOR).
    #       `n ** 2` would also work; ** is Python's power operator.
    pass
''',
        "c": r'''#include <stdio.h>
#include <stdbool.h>

long long square(long long n) {
    // TODO: replace 0 with  n * n
    // Note: C has no power operator; `n ^ 2` is bitwise XOR, not a square.
    return 0;
}
''',
        "cpp": r'''#include <bits/stdc++.h>
using namespace std;

long long square(long long n) {
    // TODO: replace 0 with  n * n
    // Note: `n ^ 2` is bitwise XOR in C++, not a square.
    return 0;
}
''',
        "rust": r'''pub fn square(n: i64) -> i64 {
    // TODO: replace 0 with  n * n   (no semicolon)
    let _ = n; // (only silences an "unused" warning; delete this line)
    0
}
''',
        "espresso": r'''fn square(n) {
    // TODO: replace 0 with  n * n
    return 0
}
''',
    },
    explanation=r"""
## Intuition

Squaring is multiplying a number by itself, so the body is a single multiplication. The real lesson of this problem is the difference between **computing** a value, **returning** it, and **printing** it.

## Approach

```python
def square(n: int) -> int:
    return n * n
```

```c
long long square(long long n) {
    return n * n;
}
```

```cpp
long long square(long long n) {
    return n * n;
}
```

```rust
pub fn square(n: i64) -> i64 {
    n * n
}
```

### Return vs print, once more

Imagine the harness does this:

```python
answer = square(7)
total = answer + 1
```

If `square` returns 49, `total` is 50. If `square` instead *prints* 49 and returns nothing, `answer` is `None` in Python and `answer + 1` crashes. The function did show 49 on the screen, but nobody can use it. **Functions that compute things should return them**, and let the caller decide whether to print.

### `^` is not "to the power of"

Many people type `n ^ 2`. In Python, C, C++ and Rust, `^` is **bitwise XOR**, an operation on the binary digits. `3 ^ 2` is `1`, not `9`. Python has a real power operator, `n ** 2`; C and C++ have `pow` in `<math.h>`/`<cmath>`, but it works on floating point and is overkill for squaring. Rust has `n.pow(2)`.

Trace:

| n | n * n |
|---|---|
| 3 | 9 |
| -5 | 25 |
| 0 | 0 |
| 46340 | 2147395600 |

## Complexity

One multiplication: O(1) time and space.

## Common mistakes

* **`n ^ 2`** (XOR) instead of `n * n`.
* **`n * 2`** (doubling) instead of `n * n` (squaring). Check with the example: 3 * 2 = 6, not 9.
* **Printing the answer** instead of returning it.
* **Overflow in C with `int`.** 46341² is larger than the biggest 32-bit `int`. The constraint keeps the result below that limit here, but with `long long` you do not need to worry at all.

## Going further

Write `cube(n)` returning `n * n * n`. Then try `square(square(n))`: what does it compute? (n to the fourth power.)
""",
    solution=r'''def square(n: int) -> int:
    # Squaring is multiplying a number by itself. We RETURN the result so
    # the caller can use it (store it, add to it, compare it); printing it
    # would only show it on screen and hand back None.
    # Note that n ^ 2 would be bitwise XOR, not a power, which is why we
    # multiply explicitly.
    return n * n
''',
    refs={
        "c": r'''long long square(long long n) {
    // Multiply instead of using ^ (XOR) or pow (which works on doubles).
    return n * n;
}
''',
        "cpp": r'''long long square(long long n) {
    return n * n;   // a negative times a negative is positive, so no special case
}
''',
        "rust": r'''pub fn square(n: i64) -> i64 {
    // n.pow(2) also works; plain multiplication is just as clear.
    n * n
}
''',
        "espresso": r'''fn square(n) {
    return n * n
}
''',
    },
    tests=[[3], [-5], [0], [1], [-1], [12], [46340], [-46340], [1000]],
))

# ----------------------------------------------------------------------------
# 5. Echo a line
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="echo-a-line",
    title="Echo a Line",
    difficulty=0,
    kind="io",
    tags=["input", "output", "strings"],
    statement=r"""
Your first program that **reads input**.

The input is a single line of text. Print that same line back, unchanged.

The line may contain spaces, punctuation and digits. It may also be empty, in which case print an empty line.
""",
    constraints=["The line has at most 1000 characters.", "The input contains only printable ASCII characters and ends with a newline."],
    hints=[
        "Each language has a function that reads one whole line of text from standard input. The starter's TODO names it.",
        "Read the line into a variable, then print that variable.",
        "Watch out for the newline at the end of the line. Python's `input()` removes it; C's `fgets` and Rust's `read_line` keep it, so either print without adding another, or strip it first.",
    ],
    starters={
        "python": r'''# input() waits for one line of text from standard input and returns it
# as a string, WITHOUT the newline at the end.
#
# TODO 1: read the line into a variable:
#     line = input()
#
# TODO 2: print it back:
#     print(line)

''',
        "c": r'''#include <stdio.h>
#include <string.h>

int main(void) {
    // A C string is an array of characters. We reserve room for 1000
    // characters, plus the newline, plus the '\0' that marks the end.
    char line[1100];

    // TODO 1: read one line from standard input (stdin) into `line`:
    //     if (fgets(line, sizeof line, stdin) == NULL) line[0] = '\0';
    // fgets keeps the '\n' at the end of the line (if there was one) and
    // returns NULL when there was nothing to read.

    // TODO 2: print the line back. Since it already ends with '\n',
    // print it with no extra newline:
    //     printf("%s", line);
    // %s means "insert a string here". Never use printf(line) directly:
    // a % inside the text would be misread as a format specifier.

    return 0;
}
''',
        "cpp": r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    // string is C++'s growable text type.
    string line;

    // TODO 1: read one whole line (spaces included) into `line`:
    //     getline(cin, line);
    // getline removes the '\n'. (cin >> line would stop at the first space!)

    // TODO 2: print it followed by a newline:
    //     cout << line << "\n";

    return 0;
}
''',
        "rust": r'''use std::io;

fn main() {
    // `let mut` creates a variable that we are allowed to change (mutable).
    // String::new() is an empty, growable string.
    let mut line = String::new();

    // TODO 1: read one line from standard input into `line`:
    //     io::stdin().read_line(&mut line).unwrap();
    // &mut line lends `line` to read_line so it can append to it.
    // .unwrap() means "if reading failed, stop the program with an error".
    // read_line KEEPS the '\n' at the end.

    // TODO 2: strip the trailing newline and print:
    //     let line = line.trim_end_matches(&['\n', '\r'][..]);
    //     println!("{}", line);
    // {} in println! is replaced by the next argument.
}
''',
    },
    explanation=r"""
## Intuition

So far your programs produced output from nothing. Real programs react to **input**. Standard input (stdin) is a stream of characters; for this problem it contains one line followed by a newline character `\n`. Reading "a line" means taking characters up to and including that `\n`.

The only real subtlety is **what happens to that newline**: some functions keep it, some throw it away, and printing functions differ in whether they add one.

## Approach

Read one line, write it back.

```python
line = input()        # input() strips the trailing '\n'
print(line)           # print adds one back
```

```c
char line[1100];
if (fgets(line, sizeof line, stdin) == NULL) line[0] = '\0';
printf("%s", line);   // fgets kept the '\n', so don't add another
```

```cpp
string line;
getline(cin, line);   // getline drops the '\n'
cout << line << "\n";
```

```rust
let mut line = String::new();
io::stdin().read_line(&mut line).unwrap();       // keeps the '\n'
let line = line.trim_end_matches(&['\n', '\r'][..]);
println!("{}", line);                             // adds a '\n'
```

| function | keeps `\n`? | | printer | adds `\n`? |
|---|---|---|---|---|
| Python `input()` | no | | `print` | yes |
| C `fgets` | yes | | `printf` | no |
| C++ `getline` | no | | `cout <<` | no (use `"\n"` or `endl`) |
| Rust `read_line` | yes | | `println!` | yes |

### C strings in one paragraph

C has no real string type. A string is an **array of `char`** that ends with a special zero byte `'\0'`. `char line[1100];` reserves 1100 bytes; `fgets(line, sizeof line, stdin)` fills it with at most 1099 characters plus the terminating `'\0'`, so it can never write past the end. `printf("%s", line)` prints characters until it reaches that `'\0'`.

### Format strings

`printf`'s first argument is a **format string**. Ordinary characters are printed as-is; a `%` starts a **format specifier** that is replaced by the next argument: `%s` a string, `%lld` a `long long`, `%f` a `double`, `%c` a single character. This is why `printf(line)` is dangerous: if the user types `100%d`, printf would go looking for an argument that does not exist.

## Complexity

O(L) time and space for a line of length L: every character is read and written once.

## Common mistakes

* **`cin >> line`** in C++ reads only up to the first space. Use `getline` for whole lines.
* **`scanf("%s", line)`** in C has the same problem, and no length limit.
* **Double newlines** in C (`printf("%s\n", line)` after `fgets` prints the line's own `\n` plus yours). The checker forgives trailing blank lines, but it is a habit worth fixing.
* **Rust `\r`.** Text from Windows ends lines with `\r\n`; trimming both characters makes your code robust.

## Going further

Read *two* lines and print them in reverse order. Then try reading until the input runs out (`for line in sys.stdin:` in Python, `while (fgets(...))` in C).
""",
    solution=r'''# input() reads characters from standard input up to the end of the line,
# and returns them as a string with the trailing newline removed.
line = input()

# print writes the string and then a newline, restoring exactly what we read.
# An empty line works too: input() returns "", and print("") prints just "\n".
print(line)
''',
    refs={
        "c": r'''#include <stdio.h>

int main(void) {
    // Room for 1000 characters, the '\n' and the terminating '\0'.
    char line[1100];

    // fgets reads up to sizeof(line) - 1 characters, stopping after '\n'.
    // If there is no input at all it returns NULL; we then use "".
    if (fgets(line, sizeof line, stdin) == NULL) line[0] = '\0';

    // The '\n' read by fgets is still in the buffer, so "%s" alone
    // reproduces the line exactly. Never pass user text as the format.
    printf("%s", line);
    return 0;
}
''',
        "cpp": r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    string line;
    // getline reads everything up to the newline (spaces included)
    // and discards the newline itself.
    getline(cin, line);
    cout << line << "\n";
    return 0;
}
''',
        "rust": r'''use std::io;

fn main() {
    let mut line = String::new();
    // read_line appends one line, INCLUDING its '\n', to `line`.
    io::stdin().read_line(&mut line).unwrap();
    // Remove the trailing newline (and a '\r' from Windows line endings).
    let line = line.trim_end_matches(&['\n', '\r'][..]);
    println!("{}", line);
}
''',
    },
    tests=[
        "Hello there\n",
        "Crucible forges programmers.\n",
        "\n",
        "    leading spaces are kept\n",
        "100% sure: printf(\"%d\") is a trap!\n",
        "x\n",
        "1 2 3 4 5 6 7 8 9 10\n",
        ("abc " * 200).strip() + "\n",
    ],
))

# ----------------------------------------------------------------------------
# 6. Greet by name
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="greet-by-name",
    title="Greet by Name",
    difficulty=0,
    kind="io",
    tags=["input", "output", "strings", "formatting"],
    statement=r"""
Read a person's name and greet them.

The input is a single line containing a name. Print:

```text
Hello, <name>!
```

where `<name>` is the line you read (without its newline). Names may contain spaces, such as `Grace Hopper`.
""",
    constraints=["The name has between 1 and 100 characters.", "The name does not start or end with a space."],
    hints=[
        "This is \"Echo a Line\" plus some fixed text before and after the name.",
        "Build the output from three pieces: `\"Hello, \"`, the name, and `\"!\"`. Mind the space after the comma.",
        "Python: `print(f\"Hello, {name}!\")`. C: strip the `\\n` from `fgets`, then `printf(\"Hello, %s!\\n\", name);`. Rust: `println!(\"Hello, {}!\", name);`.",
    ],
    starters={
        "python": r'''# TODO 1: read the name (input() removes the newline for you):
#     name = input()
#
# TODO 2: print the greeting with an f-string:
#     print(f"Hello, {name}!")
# An f-string (the f before the quote) replaces {name} with the
# variable's value. "Hello, " + name + "!" would also work.

''',
        "c": r'''#include <stdio.h>
#include <string.h>

int main(void) {
    char name[200];

    // TODO 1: read the line:
    //     if (fgets(name, sizeof name, stdin) == NULL) return 0;

    // TODO 2: fgets keeps the '\n'. Cut the string at the first '\n'
    // (or '\r') by overwriting it with the end-of-string marker '\0':
    //     name[strcspn(name, "\r\n")] = '\0';
    // strcspn returns the index of the first character that is '\r' or '\n'
    // (or the length of the string if there is none).

    // TODO 3: print the greeting. %s is replaced by `name`:
    //     printf("Hello, %s!\n", name);

    return 0;
}
''',
        "cpp": r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    string name;

    // TODO 1: read the whole line (names can contain spaces):
    //     getline(cin, name);

    // TODO 2: print the pieces one after another:
    //     cout << "Hello, " << name << "!" << "\n";

    return 0;
}
''',
        "rust": r'''use std::io;

fn main() {
    let mut name = String::new();

    // TODO 1: read the line:
    //     io::stdin().read_line(&mut name).unwrap();

    // TODO 2: remove the trailing newline. trim_end() removes all trailing
    // whitespace, which is fine because names do not end with a space:
    //     let name = name.trim_end();

    // TODO 3: print the greeting. Each {} is filled by the next argument:
    //     println!("Hello, {}!", name);
}
''',
    },
    explanation=r"""
## Intuition

Most output is a mix of **fixed text** and **values that change**. Every language has a way to write a *template* with holes in it and fill the holes with variables. Learn that tool well: you will use it in nearly every program.

## Approach

1. Read the line.
2. Remove its newline (where the reading function keeps it).
3. Print `Hello, ` + name + `!`.

```python
name = input()
print(f"Hello, {name}!")          # f-string: {name} is replaced by the value
```

```c
char name[200];
fgets(name, sizeof name, stdin);
name[strcspn(name, "\r\n")] = '\0';   // cut off the newline
printf("Hello, %s!\n", name);        // %s is replaced by name
```

```cpp
string name;
getline(cin, name);
cout << "Hello, " << name << "!\n";   // pieces are printed in order
```

```rust
let mut name = String::new();
io::stdin().read_line(&mut name).unwrap();
let name = name.trim_end();
println!("Hello, {}!", name);         // {} is replaced by name
```

### Why the newline must go

Suppose the input is `Ada\n`. In C, `fgets` stores the characters `A d a \n \0`. If you print `"Hello, %s!\n"` without removing the `\n`, the output is

```text
Hello, Ada
!
```

because the name's own newline lands *before* the `!`. That is why step 2 exists. `strcspn(name, "\r\n")` finds the position of the first `\r` or `\n`; writing `'\0'` there ends the string early. In Rust, `trim_end()` returns a view of the string without trailing whitespace. Python's `input()` and C++'s `getline` already drop the newline.

### Three templating styles

| language | template | placeholder |
|---|---|---|
| Python | `f"Hello, {name}!"` | `{expression}` |
| C | `printf("Hello, %s!\n", name)` | `%s` for strings, `%lld` for long long, `%f` for double |
| C++ | `cout << "Hello, " << name << "!"` | (no template: just chain pieces) |
| Rust | `println!("Hello, {}!", name)` | `{}` |

## Complexity

O(L) for a name of length L.

## Common mistakes

* **Missing space** after the comma: `Hello,Ada!` fails.
* **The stray newline** described above.
* **Reading a single word.** `input().split()[0]`, `cin >> name` or `scanf("%s")` would turn `Grace Hopper` into `Grace`.
* **Forgetting the `f`** in a Python f-string prints the literal text `{name}`.

## Going further

Read a first name and a last name on two separate lines and print `Hello, <first> <last>!`. Or print the greeting followed by the number of characters in the name.
""",
    solution=r'''# input() returns the whole line, spaces included, without the newline.
name = input()

# An f-string substitutes the value of `name` into the template. The fixed
# parts ("Hello, " and "!") are printed exactly as written.
print(f"Hello, {name}!")
''',
    refs={
        "c": r'''#include <stdio.h>
#include <string.h>

int main(void) {
    char name[200];
    if (fgets(name, sizeof name, stdin) == NULL) return 0;

    // fgets keeps the line's '\n'. strcspn gives the index of the first
    // '\r' or '\n'; putting '\0' there ends the string just before it.
    name[strcspn(name, "\r\n")] = '\0';

    // %s is replaced by the characters of `name`, up to its '\0'.
    printf("Hello, %s!\n", name);
    return 0;
}
''',
        "cpp": r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    string name;
    getline(cin, name);                 // whole line, newline removed
    if (!name.empty() && name.back() == '\r') name.pop_back();  // Windows line ending
    cout << "Hello, " << name << "!\n"; // pieces are printed left to right
    return 0;
}
''',
        "rust": r'''use std::io;

fn main() {
    let mut name = String::new();
    io::stdin().read_line(&mut name).unwrap();
    // trim_end borrows the string without its trailing whitespace ("\n").
    let name = name.trim_end();
    println!("Hello, {}!", name);
}
''',
    },
    tests=["Ada\n", "Grace Hopper\n", "Linus\n", "X\n", "Dennis MacAlistair Ritchie\n", "Ferris the Crab\n", "O'Brien-Smith\n"],
))

# ----------------------------------------------------------------------------
# 7. Sum of two inputs
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="sum-of-two-inputs",
    title="Sum of Two Inputs",
    difficulty=0,
    kind="io",
    tags=["input", "parsing", "arithmetic"],
    statement=r"""
Read two integers and print their sum.

The input contains two integers `a` and `b` separated by whitespace (a space or a newline). Print `a + b` on its own line.
""",
    constraints=["-10¹² ≤ a, b ≤ 10¹²"],
    hints=[
        "Input arrives as **text**. The characters `\"12\"` are not the number 12 until you convert (parse) them.",
        "Split the input on whitespace into two pieces, convert each to an integer, then add.",
        "Python: `a, b = map(int, sys.stdin.read().split())`. C: `scanf(\"%lld %lld\", &a, &b)`. C++: `cin >> a >> b`. Rust: split_whitespace + `parse::<i64>()`.",
    ],
    starters={
        "python": r'''import sys

# sys.stdin.read() returns ALL of the input as one string, e.g. "3 4\n".
data = sys.stdin.read()

# TODO 1: split the text on whitespace into a list of pieces:
#     parts = data.split()          # "3 4\n" -> ["3", "4"]
#
# TODO 2: convert each piece from text to an integer with int():
#     a = int(parts[0])
#     b = int(parts[1])
#
# TODO 3: print the sum:
#     print(a + b)
''',
        "c": r'''#include <stdio.h>

int main(void) {
    // long long holds 64-bit integers; values up to 10^12 do NOT fit in int.
    long long a, b;

    // TODO 1: read two integers. %lld means "a long long in decimal".
    // The & passes the ADDRESS of a and b so scanf can store into them:
    //     scanf("%lld %lld", &a, &b);

    // TODO 2: print the sum followed by a newline:
    //     printf("%lld\n", a + b);

    return 0;
}
''',
        "cpp": r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    // long long holds 64-bit integers; values up to 10^12 do NOT fit in int.
    long long a, b;

    // TODO 1: read two integers. >> skips whitespace and converts text to numbers:
    //     cin >> a >> b;

    // TODO 2: print the sum:
    //     cout << a + b << "\n";

    return 0;
}
''',
        "rust": r'''use std::io::{self, Read};

fn main() {
    // Read all of standard input into one String.
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();

    // TODO 1: split on whitespace; this gives an iterator of &str pieces:
    //     let mut parts = input.split_whitespace();
    //
    // TODO 2: take each piece and parse it into an i64.
    //     let a: i64 = parts.next().unwrap().parse().unwrap();
    //     let b: i64 = parts.next().unwrap().parse().unwrap();
    // next() gives the next piece (an Option, so we unwrap it);
    // parse() converts text to the type we annotated (i64), and returns a
    // Result (success or error), so we unwrap that too.
    //
    // TODO 3: print the sum:
    //     println!("{}", a + b);
}
''',
    },
    explanation=r"""
## Intuition

Everything that arrives on standard input is **text**. When the input is `3 4`, your program receives the characters `'3'`, `' '`, `'4'`, `'\n'`. To do arithmetic you must **parse** the text: find where each number starts and ends, and convert those digit characters into an actual integer value. Adding the *strings* `"3"` and `"4"` in Python gives `"34"`, not `7`.

## Approach

1. Read the input.
2. Break it into whitespace-separated **tokens**.
3. Convert each token to an integer.
4. Print the sum.

```python
import sys
a, b = map(int, sys.stdin.read().split())   # split -> ["3", "4"], int() each
print(a + b)
```

```c
long long a, b;
scanf("%lld %lld", &a, &b);   // %lld = long long; & = "store into this variable"
printf("%lld\n", a + b);
```

```cpp
long long a, b;
cin >> a >> b;                // >> skips spaces/newlines and parses numbers
cout << a + b << "\n";
```

```rust
let mut input = String::new();
io::stdin().read_to_string(&mut input).unwrap();
let mut it = input.split_whitespace();
let a: i64 = it.next().unwrap().parse().unwrap();
let b: i64 = it.next().unwrap().parse().unwrap();
println!("{}", a + b);
```

Trace for input `"-5\n12\n"` (the numbers are on separate lines, which is fine because we split on any whitespace):

| step | value |
|---|---|
| raw text | `"-5\n12\n"` |
| tokens | `["-5", "12"]` |
| integers | `-5`, `12` |
| output | `7` |

### What `&` means in `scanf`

C functions receive *copies* of their arguments. If you wrote `scanf("%lld", a)`, scanf would get a copy of `a`'s (garbage) value and could not change `a`. `&a` is the **address** of `a`, its location in memory, so scanf can write the parsed number there. `printf` only needs the values, so it takes `a + b` directly.

### What `unwrap` means in Rust

Many Rust operations can fail: there might be no next token, or the token might be `"hello"` instead of a number. Rust makes you acknowledge that. `next()` returns an `Option` (Some(token) or None) and `parse()` returns a `Result` (Ok(number) or Err). `.unwrap()` says "I am sure this succeeded; if not, stop the program with an error". In a practice problem with well-formed input, that is fine.

## Complexity

O(L) to read and split input of L characters; the addition is O(1).

## Common mistakes

* **`int` in C/C++.** 10¹² does not fit in a 32-bit `int` (maximum about 2.1 × 10⁹). Use `long long` with `%lld`.
* **`%d` with a `long long`.** The specifier must match the type exactly, or you get garbage.
* **Forgetting `&`** in scanf: the program usually crashes.
* **Python `input()` twice** when both numbers are on one line: the first `input()` returns `"3 4"` and `int("3 4")` fails. Reading everything and splitting handles every layout.

## Going further

Read *N* followed by N integers and print their sum. In Python, `sum(map(int, data.split()[1:]))`; in C, a loop of `scanf` calls.
""",
    solution=r'''import sys

# Read the entire input as one string, then split on ANY whitespace
# (spaces, tabs, newlines). That way it does not matter whether the two
# numbers share a line or sit on separate lines.
tokens = sys.stdin.read().split()

# Text is not a number: "12" + "3" would be "123". int() parses the digits
# (and an optional leading minus sign) into a real integer.
a = int(tokens[0])
b = int(tokens[1])

# Python integers have unlimited size, so 10^12 + 10^12 is no problem.
print(a + b)
''',
    refs={
        "c": r'''#include <stdio.h>

int main(void) {
    // Values reach 10^12, beyond the ~2.1e9 limit of a 32-bit int,
    // so we need the 64-bit long long and its specifier %lld.
    long long a, b;

    // scanf skips whitespace (including newlines) before each number.
    // &a passes the address of a, so scanf can store the parsed value there.
    if (scanf("%lld %lld", &a, &b) != 2) return 1;

    printf("%lld\n", a + b);
    return 0;
}
''',
        "cpp": r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    long long a, b;          // 64-bit: 10^12 does not fit in int
    cin >> a >> b;           // each >> skips whitespace, then parses one number
    cout << a + b << "\n";
    return 0;
}
''',
        "rust": r'''use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();

    // split_whitespace yields the tokens "a" and "b" regardless of layout.
    let mut parts = input.split_whitespace();
    // parse() turns text into the annotated type; unwrap() stops with an
    // error if the token is missing or is not a valid number.
    let a: i64 = parts.next().unwrap().parse().unwrap();
    let b: i64 = parts.next().unwrap().parse().unwrap();

    println!("{}", a + b);
}
''',
    },
    tests=["3 4\n", "-5\n12\n", "0 0\n", "1000000000000 1000000000000\n", "-1000000000000 -1000000000000\n",
           "  7    -7  \n", "2147483647 1\n", "123456789012 -98765\n"],
))

# ----------------------------------------------------------------------------
# 8. Is it positive?
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="is-positive-number",
    title="Is It Positive?",
    difficulty=0,
    tags=["booleans", "comparison"],
    fn="is_positive",
    params=[["n", "int"]],
    returns="bool",
    statement=r"""
Return `true` if `n` is strictly greater than zero, and `false` otherwise.

Zero is **not** positive.
""",
    constraints=["-10⁹ ≤ n ≤ 10⁹"],
    example_notes=["7 > 0, so the answer is true.", "0 is neither positive nor negative, so the answer is false."],
    hints=[
        "A comparison like `n > 0` is itself a value: it evaluates to true or false.",
        "You do not need an `if`. Return the comparison directly.",
        "`return n > 0` (or `n > 0` as the last line in Rust).",
    ],
    starters={
        "python": r'''def is_positive(n: int) -> bool:
    # A comparison such as  n > 0  produces a bool: True or False.
    # TODO: replace `pass` with:   return n > 0
    pass
''',
        "c": r'''#include <stdio.h>
#include <stdbool.h>   // defines the bool type and the words true / false

bool is_positive(long long n) {
    // A comparison such as  n > 0  produces true or false.
    // TODO: replace `false` with  n > 0
    return false;
}
''',
        "cpp": r'''#include <bits/stdc++.h>
using namespace std;

bool isPositive(long long n) {
    // A comparison such as  n > 0  produces true or false.
    // TODO: replace `false` with  n > 0
    return false;
}
''',
        "rust": r'''pub fn is_positive(n: i64) -> bool {
    // A comparison such as  n > 0  produces true or false.
    // TODO: replace `false` with  n > 0   (no semicolon)
    let _ = n; // (only silences an "unused" warning; delete this line)
    false
}
''',
        "espresso": r'''fn isPositive(n) {
    // TODO: replace false with  n > 0
    return false
}
''',
    },
    explanation=r"""
## Intuition

A **boolean** (`bool`) is a type with exactly two values: true and false. Every comparison produces one: `7 > 0` *is* `true`, `-3 > 0` *is* `false`. So a question like "is n positive?" is answered by a single comparison, and the function can return that comparison's value directly.

## Approach

```python
def is_positive(n: int) -> bool:
    return n > 0
```

```c
#include <stdbool.h>
bool is_positive(long long n) {
    return n > 0;
}
```

```cpp
bool isPositive(long long n) {
    return n > 0;
}
```

```rust
pub fn is_positive(n: i64) -> bool {
    n > 0
}
```

Beginners often write the longer form:

```python
if n > 0:
    return True
else:
    return False
```

It works, but notice that it says "if this is true, return true; if it is false, return false". That is exactly the value of `n > 0` itself. Returning the comparison directly is shorter and harder to get wrong.

### The comparison operators

| operator | meaning | `5 ? 3` |
|---|---|---|
| `>` | greater than | true |
| `>=` | greater than or equal | true |
| `<` | less than | false |
| `<=` | less than or equal | false |
| `==` | equal | false |
| `!=` | not equal | true |

Note `==` (two equals signs) **compares**, while `=` (one) **assigns**. In C, `if (n = 0)` is legal: it sets `n` to 0 and then tests 0, which is false. Compilers warn about it; listen to them.

### Booleans in each language

Python spells them `True`/`False` (capitalised). C needs `#include <stdbool.h>` for `bool`, `true`, `false`; underneath, C's comparisons produce the integers 1 and 0. C++ and Rust have `bool` built in with lowercase `true`/`false`. Crucible displays them as lowercase `true`/`false` whatever language you use.

Trace:

| n | `n > 0` |
|---|---|
| 7 | true |
| 0 | false |
| -3 | false |
| 1 | true |

## Complexity

One comparison: O(1).

## Common mistakes

* **`>=` instead of `>`.** Zero would then count as positive. The tests include `0`.
* **Returning the string `"true"`** instead of the boolean value.
* **`=` instead of `==`** when you compare for equality elsewhere.

## Going further

Write `is_negative` and `is_zero`. Then notice that for every integer exactly one of the three is true.
""",
    solution=r'''def is_positive(n: int) -> bool:
    # The comparison n > 0 evaluates to a bool by itself, so we can return
    # it directly instead of writing an if/else that returns True/False.
    # It is a STRICT comparison: 0 is not positive, so 0 > 0 is False.
    return n > 0
''',
    refs={
        "c": r'''bool is_positive(long long n) {
    // In C the comparison yields 1 or 0; returning it as bool gives true/false.
    return n > 0;
}
''',
        "cpp": r'''bool isPositive(long long n) {
    return n > 0;   // strict: zero is not positive
}
''',
        "rust": r'''pub fn is_positive(n: i64) -> bool {
    n > 0
}
''',
        "espresso": r'''fn isPositive(n) {
    return n > 0
}
''',
    },
    tests=[[7], [0], [-3], [1], [-1], [1000000000], [-1000000000], [42]],
))

# ----------------------------------------------------------------------------
# 9. Larger of two
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="larger-of-two",
    title="Larger of Two",
    difficulty=0,
    tags=["conditionals", "comparison"],
    fn="max_of_two",
    params=[["a", "int"], ["b", "int"]],
    returns="int",
    statement=r"""
Return the larger of the two integers `a` and `b`. If they are equal, return that value.

Try writing it with an `if` statement rather than a built-in `max` function: the point is to practise making a decision.
""",
    constraints=["-10⁹ ≤ a, b ≤ 10⁹"],
    example_notes=["8 is larger than 3.", "When both are equal, either one is the answer."],
    hints=[
        "Your program has to choose between two possible answers. That is what `if` is for.",
        "Compare `a` with `b`. If `a` is bigger, the answer is `a`; otherwise it is `b`.",
        "`if a > b: return a` then `return b`. Equal values fall through to `return b`, which is correct.",
    ],
    explanation=r"""
## Intuition

Until now every function did the same thing for every input. Here the function must **decide**: depending on the values, return one or the other. The `if` statement runs a block of code only when a condition is true, and `else` provides the alternative.

## Approach

Compare `a` and `b`; return whichever is bigger.

```python
def max_of_two(a, b):
    if a > b:
        return a
    else:
        return b
```

```c
long long max_of_two(long long a, long long b) {
    if (a > b) {
        return a;
    } else {
        return b;
    }
}
```

```cpp
long long maxOfTwo(long long a, long long b) {
    return a > b ? a : b;   // the "ternary" operator: cond ? if_true : if_false
}
```

```rust
pub fn max_of_two(a: i64, b: i64) -> i64 {
    if a > b { a } else { b }   // in Rust, if/else is an expression with a value
}
```

### How `if` is written

* **Python** uses a colon and indentation: the indented lines belong to the `if`.
* **C and C++** put the condition in parentheses and the block in braces `{ }`.
* **Rust** needs no parentheses but always needs braces, and `if` produces a value, so `if a > b { a } else { b }` can be the function's last expression.

Since `return` leaves the function immediately, the `else` is optional: if `a > b` we have already returned, so any line after the `if` only runs when `a <= b`.

Trace:

| a | b | `a > b`? | returned |
|---|---|---|---|
| 3 | 8 | false | b = 8 |
| 8 | 3 | true | a = 8 |
| 5 | 5 | false | b = 5 |
| -2 | -9 | true | a = -2 |

The equal case shows why the choice of `>` vs `>=` does not matter here: both branches give the same number.

## Complexity

One comparison: O(1).

## Common mistakes

* **Forgetting negatives.** Some people start with `best = 0` and compare; that returns 0 for `(-2, -9)`. Always start from one of the actual values.
* **Missing braces in C.** Without braces only the *first* statement belongs to the `if`. Use braces always; it costs nothing.
* **Python indentation.** Mixing tabs and spaces, or not indenting the body, is an error.

## Going further

Every language has this built in: `max(a, b)` in Python, `std::max(a, b)` in C++, `a.max(b)` in Rust (C has no standard integer `max`). For three values, `max_of_two(max_of_two(a, b), c)` reuses your function.
""",
    solution=r'''def max_of_two(a: int, b: int) -> int:
    # Decide between the two candidates with a single comparison.
    if a > b:
        # a is strictly larger, so it is the answer.
        return a
    # We only get here when a <= b. If they are equal, returning b is the
    # same as returning a, so the tie needs no special case.
    return b
''',
    refs={
        "c": r'''long long max_of_two(long long a, long long b) {
    if (a > b) {
        return a;      // a is strictly larger
    }
    return b;          // a <= b: b is at least as large (ties included)
}
''',
        "cpp": r'''long long maxOfTwo(long long a, long long b) {
    // condition ? value_if_true : value_if_false
    return a > b ? a : b;
}
''',
        "rust": r'''pub fn max_of_two(a: i64, b: i64) -> i64 {
    // if/else is an expression in Rust, so it can be the returned value.
    if a > b { a } else { b }
}
''',
        "espresso": r'''fn maxOfTwo(a, b) {
    if a > b {
        return a
    }
    return b
}
''',
    },
    tests=[[3, 8], [8, 3], [5, 5], [-2, -9], [-9, -2], [0, -1], [-1000000000, 1000000000], [0, 0], [123, 124]],
))

# ----------------------------------------------------------------------------
# 10. Absolute value
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="absolute-value",
    title="Absolute Value",
    difficulty=0,
    tags=["conditionals", "arithmetic"],
    fn="absolute_value",
    params=[["n", "int"]],
    returns="int",
    statement=r"""
The **absolute value** of a number is its distance from zero: `|5| = 5`, `|-5| = 5`, `|0| = 0`.

Return the absolute value of `n`. Write it with a condition instead of a library function.
""",
    constraints=["-10⁹ ≤ n ≤ 10⁹"],
    hints=[
        "Positive numbers and zero are already their own absolute value.",
        "For a negative number, flip its sign. What operator flips a sign?",
        "`if n < 0: return -n` and otherwise `return n`.",
    ],
    explanation=r"""
## Intuition

Absolute value throws away the sign. Non-negative numbers are unchanged; negative numbers become their opposite. "Opposite" is the **unary minus** operator: `-n`. If `n` is `-7`, then `-n` is `7`.

## Approach

```python
def absolute_value(n):
    if n < 0:
        return -n
    return n
```

```c
long long absolute_value(long long n) {
    if (n < 0) return -n;
    return n;
}
```

```cpp
long long absoluteValue(long long n) {
    return n < 0 ? -n : n;
}
```

```rust
pub fn absolute_value(n: i64) -> i64 {
    if n < 0 { -n } else { n }
}
```

Trace:

| n | `n < 0`? | returned |
|---|---|---|
| -7 | yes | 7 |
| 7 | no | 7 |
| 0 | no | 0 |

### Why not just use `abs`?

You can, outside of practice: Python has `abs(n)`, C++ has `std::abs` / `llabs`, Rust has `n.abs()`. But C deserves a warning: plain `abs()` from `<stdlib.h>` takes an **`int`**, so `abs(5000000000LL)` silently chops the number down to 32 bits first and returns nonsense. The `long long` version is `llabs`. Writing the condition yourself avoids the trap and practises `if`.

## Complexity

O(1).

## Common mistakes

* **`return n * -1` for every n.** That flips positive numbers too.
* **C's `abs` with `long long`.** Use `llabs` or your own condition.
* **The most negative number.** For a 64-bit integer, `-(-9223372036854775808)` does not fit, because the positive range ends one sooner. It cannot happen with these constraints, but it is a real bug in production code (Rust panics in debug mode, C has undefined behaviour).

## Going further

The distance between two numbers `a` and `b` on the number line is `absolute_value(a - b)`. Try it: the distance between -3 and 4 is 7.
""",
    solution=r'''def absolute_value(n: int) -> int:
    # Negative numbers are the only ones that change: flipping the sign with
    # unary minus turns -7 into 7.
    if n < 0:
        return -n
    # Zero and positive numbers are already their own distance from zero.
    return n
''',
    refs={
        "c": r'''long long absolute_value(long long n) {
    // Avoid abs(): it takes an int and would truncate 64-bit values.
    if (n < 0) return -n;
    return n;
}
''',
        "cpp": r'''long long absoluteValue(long long n) {
    return n < 0 ? -n : n;   // flip the sign only when negative
}
''',
        "rust": r'''pub fn absolute_value(n: i64) -> i64 {
    if n < 0 { -n } else { n }
}
''',
        "espresso": r'''fn absoluteValue(n) {
    if n < 0 {
        return -n
    }
    return n
}
''',
    },
    tests=[[-7], [7], [0], [-1], [1], [-1000000000], [1000000000], [-42], [99]],
))

# ----------------------------------------------------------------------------
# 11. Celsius to Fahrenheit
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="celsius-to-fahrenheit",
    title="Celsius to Fahrenheit",
    difficulty=0,
    tags=["floats", "arithmetic"],
    fn="celsius_to_fahrenheit",
    params=[["celsius", "float"]],
    returns="float",
    statement=r"""
Convert a temperature from degrees Celsius to degrees Fahrenheit using

```text
F = C × 9 / 5 + 32
```

`celsius` is a decimal (floating-point) number and you must return a decimal number. Answers within 10⁻⁶ of the expected value are accepted.
""",
    constraints=["-273.15 ≤ celsius ≤ 10⁴"],
    example_notes=["Water boils at 100 °C = 212 °F.", "Body temperature: 37 × 9 / 5 + 32 = 98.6."],
    hints=[
        "Translate the formula directly: multiply by 9, divide by 5, add 32.",
        "Make sure the division is a *decimal* division. In C, C++ and Rust, writing `9.0 / 5.0` instead of `9 / 5` keeps everything in floating point.",
        "`return celsius * 9.0 / 5.0 + 32.0`.",
    ],
    explanation=r"""
## Intuition

This is a formula translated into code. The new idea is the **floating-point** type: numbers with a fractional part, called `float` in Python, `double` in C and C++, and `f64` in Rust. The trap is **integer division**.

## Approach

```python
def celsius_to_fahrenheit(celsius):
    return celsius * 9 / 5 + 32
```

```c
double celsius_to_fahrenheit(double celsius) {
    return celsius * 9.0 / 5.0 + 32.0;
}
```

```cpp
double celsiusToFahrenheit(double celsius) {
    return celsius * 9.0 / 5.0 + 32.0;
}
```

```rust
pub fn celsius_to_fahrenheit(celsius: f64) -> f64 {
    celsius * 9.0 / 5.0 + 32.0
}
```

Operators follow normal maths precedence: `*` and `/` before `+`, and equal-precedence operators go left to right. So `c * 9 / 5 + 32` means `((c * 9) / 5) + 32`.

Trace for `c = 37.0`:

| step | value |
|---|---|
| `c * 9.0` | 333.0 |
| `/ 5.0` | 66.6 |
| `+ 32.0` | 98.6 |

### The integer division trap

In C, C++ and Rust (and ESPresso), dividing two **integers** throws away the fraction: `9 / 5` is `1`, not `1.8`. So `celsius * (9 / 5) + 32` silently computes `celsius * 1 + 32`. Writing the literals as `9.0` and `5.0` makes them doubles, and any arithmetic involving a double is done in floating point. In Rust you *must* write `9.0`: it refuses to mix `f64` and integers at all (`celsius * 9` is a compile error). Python's `/` always produces a float; Python's integer division is the separate operator `//`.

### Floating point is approximate

Doubles store numbers in binary, and most decimals (like 0.1) have no exact binary form. `36.6 * 9 / 5 + 32` might come out as `97.88000000000001`. That is why Crucible accepts answers within 10⁻⁶. Never compare floats with `==` in your own code; compare `abs(x - y) < 1e-9` instead.

## Complexity

O(1).

## Common mistakes

* **`9 / 5` as integers** in C/C++/Rust/ESPresso: gives 1.
* **Wrong order of operations**: `celsius + 32 * 9 / 5` adds after scaling the wrong thing.
* **Returning an `int`/`long long`** from C: the fraction would be cut off.

## Going further

Write the inverse, `fahrenheit_to_celsius`: `(F - 32) * 5 / 9`. Here the parentheses are essential. At what temperature are the two scales equal? (Solve C = C × 9/5 + 32: at -40.)
""",
    solution=r'''def celsius_to_fahrenheit(celsius: float) -> float:
    # A direct translation of F = C * 9/5 + 32.
    # Python's "/" always performs true (decimal) division, so 9 / 5 is 1.8
    # here. In C, C++ and Rust the same expression on integers would give 1,
    # which is why their versions write 9.0 / 5.0.
    # Precedence: * and / happen before +, left to right.
    return celsius * 9 / 5 + 32
''',
    refs={
        "c": r'''double celsius_to_fahrenheit(double celsius) {
    // 9.0 and 5.0 are double literals, so no integer division happens.
    return celsius * 9.0 / 5.0 + 32.0;
}
''',
        "cpp": r'''double celsiusToFahrenheit(double celsius) {
    return celsius * 9.0 / 5.0 + 32.0;
}
''',
        "rust": r'''pub fn celsius_to_fahrenheit(celsius: f64) -> f64 {
    // Rust never mixes f64 with integer literals, so 9.0 (not 9) is required.
    celsius * 9.0 / 5.0 + 32.0
}
''',
        "espresso": r'''fn celsiusToFahrenheit(celsius) {
    // Use float literals so the division is not truncated.
    return celsius * 9.0 / 5.0 + 32.0
}
''',
    },
    tests=[[100.0], [37.0], [0.0], [-40.0], [36.6], [-273.15], [21.5], [1000.0], [-17.5]],
))

# ----------------------------------------------------------------------------
# 12. Both true
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="both-true",
    title="Both True",
    difficulty=0,
    tags=["booleans", "logic"],
    fn="both_true",
    params=[["a", "bool"], ["b", "bool"]],
    returns="bool",
    statement=r"""
Return `true` only when **both** `a` and `b` are `true`. In every other case return `false`.
""",
    examples=2,
    example_notes=["Both inputs are true, so the result is true.", "One false input is enough to make the result false."],
    hints=[
        "There are only four combinations of two booleans. Write them out as a table.",
        "Every language has a *logical AND* operator that does exactly this.",
        "Python: `return a and b`. C, C++, Rust, ESPresso: `return a && b`.",
    ],
    explanation=r"""
## Intuition

"Both are true" is the definition of **logical AND**. With only two boolean inputs there are four possible cases, and you can list them all in a **truth table**:

| a | b | a AND b |
|---|---|---|
| false | false | false |
| false | true | false |
| true | false | false |
| true | true | **true** |

The tests cover every row of this table.

## Approach

```python
def both_true(a, b):
    return a and b
```

```c
bool both_true(bool a, bool b) {
    return a && b;
}
```

```cpp
bool bothTrue(bool a, bool b) {
    return a && b;
}
```

```rust
pub fn both_true(a: bool, b: bool) -> bool {
    a && b
}
```

### The three logical operators

| meaning | Python | C / C++ / Rust / ESPresso |
|---|---|---|
| AND (both) | `a and b` | `a && b` |
| OR (at least one) | `a or b` | `a \|\| b` |
| NOT (flip) | `not a` | `!a` |

They **short-circuit**: in `a && b`, if `a` is false the answer is already known, so `b` is never evaluated. That matters when `b` is something like `i < len && arr[i] > 0`: the check on the left protects the array access on the right.

### `&&` vs `&`

C, C++ and Rust also have single `&` and `|`. Those are **bitwise** operators that work on the individual bits of integers. On booleans they happen to give the same answer but do not short-circuit. Use the doubled forms for logic.

### A comparison would also work

`a == true && b == true` is correct but redundant: `a == true` is just `a`. Likewise, avoid `if a: if b: return True` ladders; the operator already says it.

## Complexity

O(1).

## Common mistakes

* **Using `||`/`or`** (at least one) instead of AND.
* **Python's `&&`** does not exist; it is a syntax error. Python spells it `and`.
* **Returning `a and b` in Python with non-bool values.** `and` returns one of its operands, not necessarily `True`/`False` (e.g. `0 and 5` is `0`). With real booleans, as here, that is fine.

## Going further

Write `exactly_one(a, b)`: true when exactly one is true (this is XOR, `a != b` for booleans). Then build its truth table to check.
""",
    solution=r'''def both_true(a: bool, b: bool) -> bool:
    # Logical AND is true only in the single row of the truth table where
    # both inputs are true. Python spells it `and` (C-family languages use &&).
    # It short-circuits: if a is False, b is not even looked at.
    return a and b
''',
    refs={
        "c": r'''bool both_true(bool a, bool b) {
    return a && b;   // && is logical AND; & would be bitwise AND
}
''',
        "cpp": r'''bool bothTrue(bool a, bool b) {
    return a && b;
}
''',
        "rust": r'''pub fn both_true(a: bool, b: bool) -> bool {
    a && b
}
''',
        "espresso": r'''fn bothTrue(a, b) {
    // Spelled out with if so every row of the truth table is visible:
    // only when a is true does the answer depend on b.
    if a {
        return b
    }
    return false
}
''',
    },
    tests=[[True, True], [True, False], [False, True], [False, False], [True, True], [False, False]],
))

# ----------------------------------------------------------------------------
# 13. Count up to N
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="count-up-to-n",
    title="Count Up to N",
    difficulty=0,
    kind="io",
    tags=["loops", "output"],
    statement=r"""
Your first **loop**.

Read an integer `N` and print the numbers `1, 2, ..., N`, **one per line**.

If `N` is `0`, print nothing.
""",
    constraints=["0 ≤ N ≤ 1000"],
    hints=[
        "You do not want to write 1000 print statements. A loop repeats a block of code with a changing counter.",
        "Start a counter at 1, print it, add 1, and repeat while the counter is at most N.",
        "Python: `for i in range(1, n + 1): print(i)`. C: `for (long long i = 1; i <= n; i++) printf(\"%lld\\n\", i);`. Rust: `for i in 1..=n { println!(\"{}\", i); }`.",
    ],
    explanation=r"""
## Intuition

A **loop** repeats a block of code. Almost every loop you will write has the same three parts: **start** a counter, **check** whether to keep going, and **step** the counter forward. Here the counter goes 1, 2, 3, ... and we print it each time.

## Approach

```python
n = int(input())
for i in range(1, n + 1):   # range stops BEFORE its end, so use n + 1
    print(i)
```

```c
long long n;
scanf("%lld", &n);
for (long long i = 1; i <= n; i++) {   // start; check; step
    printf("%lld\n", i);
}
```

```cpp
long long n;
cin >> n;
for (long long i = 1; i <= n; i++) cout << i << "\n";
```

```rust
let n: i64 = input.trim().parse().unwrap();
for i in 1..=n {          // 1..=n includes n; 1..n would stop at n-1
    println!("{}", i);
}
```

How the C `for` loop executes for `n = 3`:

| step | i | `i <= n`? | action |
|---|---|---|---|
| start | 1 | yes | print 1, then `i++` |
| | 2 | yes | print 2, then `i++` |
| | 3 | yes | print 3, then `i++` |
| | 4 | **no** | loop ends |

When `n = 0`, the very first check `1 <= 0` is false, so the body never runs and nothing is printed. No special case needed.

### Ranges: inclusive or exclusive?

This is the most common source of off-by-one errors:

| language | 1 to n **inclusive** |
|---|---|
| Python | `range(1, n + 1)` (end is excluded) |
| C / C++ | `for (i = 1; i <= n; i++)` |
| Rust | `1..=n` (`1..n` excludes n) |
| ESPresso | `for var i in 1..n+1` (end is excluded) |

### Performance note

Printing a thousand lines is trivial, but in C++ `endl` flushes the output each time, which becomes slow for millions of lines. Prefer `"\n"`.

## Complexity

O(N) time: the loop body runs N times. O(1) extra space.

## Common mistakes

* **`range(n)`** in Python gives 0..n-1, not 1..n.
* **`i < n`** in C prints one number too few.
* **Printing on one line** (`print(i, end=" ")`): the statement says one per line.
* **An infinite loop** from forgetting the step (`i++`) in a `while` loop.

## Going further

Print the numbers from N *down* to 1 (Python `range(n, 0, -1)`, Rust `(1..=n).rev()`). Then print only the even ones, stepping by 2.
""",
    solution=r'''# Read N. int() converts the text line into an integer.
n = int(input())

# range(1, n + 1) produces 1, 2, ..., n: the end value is EXCLUDED, which
# is why we add 1. When n is 0 the range is empty and nothing is printed,
# so that edge case needs no special handling.
for i in range(1, n + 1):
    print(i)
''',
    refs={
        "c": r'''#include <stdio.h>

int main(void) {
    long long n;
    if (scanf("%lld", &n) != 1) return 1;

    // start at 1; keep going while i <= n (inclusive); step by 1.
    // For n == 0 the condition fails immediately: nothing is printed.
    for (long long i = 1; i <= n; i++) {
        printf("%lld\n", i);
    }
    return 0;
}
''',
        "cpp": r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    long long n;
    cin >> n;
    // "\n" instead of endl: endl also flushes, which is slow in big loops.
    for (long long i = 1; i <= n; i++) cout << i << "\n";
    return 0;
}
''',
        "rust": r'''use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let n: i64 = input.trim().parse().unwrap();

    // 1..=n is an inclusive range; for n == 0 it is empty.
    for i in 1..=n {
        println!("{}", i);
    }
}
''',
    },
    tests=["3\n", "0\n", "1\n", "10\n", "1000\n", "7\n", "2\n"],
))

# ----------------------------------------------------------------------------
# 14. Rectangle report (formatted output)
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="rectangle-report",
    title="Rectangle Report",
    difficulty=0,
    kind="io",
    tags=["input", "formatting", "arithmetic"],
    statement=r"""
Read the width `w` and height `h` of a rectangle (two positive integers separated by whitespace) and print a three-line report in exactly this format:

```text
Rectangle: <w> x <h>
Area: <area>
Perimeter: <perimeter>
```

The area is `w × h` and the perimeter is `2 × (w + h)`. Note the lowercase `x` with a space on each side.
""",
    constraints=["1 ≤ w, h ≤ 10⁶"],
    hints=[
        "Read both numbers first, then compute the two results, then print three lines.",
        "Each output line mixes fixed text with a number. Use your language's formatting: f-strings, `printf` with `%lld`, or `println!` with `{}`.",
        "Python: `print(f\"Rectangle: {w} x {h}\")`, `print(f\"Area: {w * h}\")`, `print(f\"Perimeter: {2 * (w + h)}\")`.",
    ],
    explanation=r"""
## Intuition

Real programs rarely print a bare number; they print **labelled, formatted** text. The computation here is easy (two formulas), so all the attention goes to producing output that matches the specification **character for character**.

## Approach

1. Read `w` and `h`.
2. Compute `area = w * h` and `perimeter = 2 * (w + h)`.
3. Print three lines, each a template with a hole.

```python
w, h = map(int, input().split())
print(f"Rectangle: {w} x {h}")
print(f"Area: {w * h}")
print(f"Perimeter: {2 * (w + h)}")
```

```c
long long w, h;
scanf("%lld %lld", &w, &h);
printf("Rectangle: %lld x %lld\n", w, h);   // two holes, two arguments, in order
printf("Area: %lld\n", w * h);
printf("Perimeter: %lld\n", 2 * (w + h));
```

```cpp
long long w, h;
cin >> w >> h;
cout << "Rectangle: " << w << " x " << h << "\n"
     << "Area: " << w * h << "\n"
     << "Perimeter: " << 2 * (w + h) << "\n";
```

```rust
println!("Rectangle: {} x {}", w, h);
println!("Area: {}", w * h);
println!("Perimeter: {}", 2 * (w + h));
```

For `w = 3, h = 4`:

```text
Rectangle: 3 x 4
Area: 12
Perimeter: 14
```

### printf format specifiers, in brief

| specifier | type | example |
|---|---|---|
| `%d` | `int` | `printf("%d", 5)` |
| `%lld` | `long long` | `printf("%lld", 5LL)` |
| `%f` | `double` (6 decimals) | `3.140000` |
| `%.2f` | `double`, 2 decimals | `3.14` |
| `%s` | string (`char*`) | `printf("%s", name)` |
| `%c` | single `char` | `printf("%c", 'x')` |
| `%%` | a literal `%` | |

The arguments fill the specifiers **in order**, and their types must match. Rust's `{}` and Python's `{}` work out the type automatically.

### Parentheses in the perimeter

`2 * w + h` is `(2 * w) + h`, which is wrong. `2 * (w + h)` adds first. When in doubt, add parentheses; they cost nothing.

### Size check

The area can reach 10⁶ × 10⁶ = 10¹², which overflows a 32-bit `int`. Use `long long` / `i64`.

## Complexity

O(1).

## Common mistakes

* **`X` or `*` instead of ` x `**, or missing spaces around it.
* **`Area:12`** (missing space after the colon).
* **`2 * w + h`** for the perimeter.
* **32-bit overflow** for the area in C/C++/Rust (`i32`).

## Going further

Add a fourth line, `Square: yes` or `Square: no`. That needs a condition inside your output, e.g. `"yes" if w == h else "no"` in Python, or `w == h ? "yes" : "no"` with `%s` in C.
""",
    solution=r'''# Both numbers are on one line (or at least separated by whitespace):
# reading everything and splitting copes with either layout.
import sys
w, h = map(int, sys.stdin.read().split())

# Compute first, print second: it keeps the formulas easy to check.
area = w * h
perimeter = 2 * (w + h)      # parentheses: add the sides BEFORE doubling

# f-strings insert each value into fixed text. The exact spacing matters,
# because the output is compared character by character.
print(f"Rectangle: {w} x {h}")
print(f"Area: {area}")
print(f"Perimeter: {perimeter}")
''',
    refs={
        "c": r'''#include <stdio.h>

int main(void) {
    long long w, h;                    // area reaches 10^12: needs 64 bits
    if (scanf("%lld %lld", &w, &h) != 2) return 1;

    long long area = w * h;
    long long perimeter = 2 * (w + h);

    // Each %lld is filled by the next argument, in order.
    printf("Rectangle: %lld x %lld\n", w, h);
    printf("Area: %lld\n", area);
    printf("Perimeter: %lld\n", perimeter);
    return 0;
}
''',
        "cpp": r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    long long w, h;
    cin >> w >> h;
    cout << "Rectangle: " << w << " x " << h << "\n";
    cout << "Area: " << w * h << "\n";
    cout << "Perimeter: " << 2 * (w + h) << "\n";
    return 0;
}
''',
        "rust": r'''use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    // Parse every token into an i64 and collect them into a vector.
    let nums: Vec<i64> = input.split_whitespace().map(|t| t.parse().unwrap()).collect();
    let (w, h) = (nums[0], nums[1]);

    println!("Rectangle: {} x {}", w, h);
    println!("Area: {}", w * h);
    println!("Perimeter: {}", 2 * (w + h));
}
''',
    },
    tests=["3 4\n", "1 1\n", "10 2\n", "1000000 1000000\n", "7\n9\n", "123 456\n", "999999 1\n"],
))

# ----------------------------------------------------------------------------
# 15. String length
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="string-length",
    title="Length of a String",
    difficulty=0,
    tags=["strings"],
    fn="string_length",
    params=[["s", "str"]],
    returns="int",
    statement=r"""
Return the number of characters in the string `s`.

The string contains only printable ASCII characters (letters, digits, spaces and punctuation) and may be empty.
""",
    constraints=["0 ≤ len(s) ≤ 1000", "`s` contains only printable ASCII characters."],
    hints=[
        "Every language can tell you a string's length with a built-in function or method.",
        "Python `len(s)`, C `strlen(s)`, C++ `s.size()`, Rust `s.len()`.",
        "For practice, also try counting yourself: loop over the characters and add 1 each time.",
    ],
    explanation=r"""
## Intuition

A **string** is a sequence of characters. Its length is how many characters it holds. Each language stores strings differently, and that changes how the length is found.

## Approach

Use the built-in length:

```python
def string_length(s):
    return len(s)
```

```c
long long string_length(char* s) {
    return strlen(s);
}
```

```cpp
long long stringLength(string s) {
    return s.size();
}
```

```rust
pub fn string_length(s: String) -> i64 {
    s.len() as i64      // len() is a usize; `as i64` converts it
}
```

### How C finds the length

A C string is a pointer to the first character of an array, and the end is marked by a zero byte `'\0'`. There is no stored length, so `strlen` walks forward until it finds that zero:

```text
s ──► | H | i | ! | \0 |
        0   1   2   3
strlen(s) = 3   (the \0 is not counted)
```

Writing it yourself is a classic exercise:

```c
long long n = 0;
while (s[n] != '\0') n++;   // count characters until the terminator
return n;
```

That is why `strlen` takes time proportional to the length, and why calling it in a loop condition (`for (i = 0; i < strlen(s); i++)`) can be accidentally slow: it recounts every iteration.

### Other languages store the length

Python, C++ `std::string` and Rust `String` keep the length alongside the characters, so `len(s)`, `s.size()` and `s.len()` are instant.

### Bytes vs characters

Rust's `s.len()` and C's `strlen` count **bytes**. For ASCII, one character is one byte, so they agree with Python. For text like `"héllo"`, `é` takes two bytes in UTF-8: Python says 5, Rust/C say 6 (Rust's `s.chars().count()` gives 5). This problem promises ASCII, so all agree.

### Casting in Rust

`s.len()` returns a `usize` (an unsigned size type), but the function promises an `i64`. Rust never converts number types implicitly, so you write `as i64`.

## Complexity

O(1) in Python, C++ and Rust; O(n) in C, where `strlen` scans the string.

## Common mistakes

* **Counting the `'\0'`** in C when writing the loop by hand.
* **`sizeof(s)`** in C gives the size of the *pointer* (8 bytes), not the string length.
* **Forgetting `as i64`** in Rust: a type-mismatch compile error.

## Going further

Count only the letters (ignoring spaces and punctuation): loop over the characters and test each one with `c.isalpha()` (Python), `isalpha(c)` (C), or `c.is_ascii_alphabetic()` (Rust).
""",
    solution=r'''def string_length(s: str) -> int:
    # Python strings know their own length, so len() is instant.
    # An empty string has length 0, which len("") already returns.
    # (In C, strlen would instead scan for the terminating '\0' byte.)
    return len(s)
''',
    refs={
        "c": r'''long long string_length(char* s) {
    // A C string has no stored length: count characters until the '\0'
    // terminator. This is exactly what strlen(s) does internally.
    long long n = 0;
    while (s[n] != '\0') {
        n++;
    }
    return n;
}
''',
        "cpp": r'''long long stringLength(string s) {
    // std::string stores its length; size() just reads it.
    return (long long)s.size();
}
''',
        "rust": r'''pub fn string_length(s: String) -> i64 {
    // len() is the number of BYTES, which equals the number of characters
    // for ASCII text. It is a usize, so convert to the promised i64.
    s.len() as i64
}
''',
    },
    tests=[["hello"], [""], ["a"], ["Hello, World!"], ["   "], ["The quick brown fox jumps over the lazy dog"], ["x" * 1000], ["tab-free 123 !?"]],
))

# ----------------------------------------------------------------------------
# 16. First character
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="first-character",
    title="First Character",
    difficulty=0,
    tags=["strings", "indexing"],
    fn="first_character",
    params=[["s", "str"]],
    returns="str",
    statement=r"""
Return a string containing only the **first** character of `s`.

`s` is never empty.
""",
    constraints=["1 ≤ len(s) ≤ 1000", "`s` contains only printable ASCII characters."],
    example_notes=["The first character of \"crucible\" is \"c\".", "A one-character string is its own first character."],
    hints=[
        "Positions in a string are numbered starting from **0**, not 1.",
        "`s[0]` is the first character. In Python that is already a one-character string.",
        "Python `return s[0]`. C++ `return string(1, s[0]);` or `s.substr(0, 1)`. Rust `s[0..1].to_string()`. C: allocate 2 bytes, store `s[0]` and `'\\0'`.",
    ],
    explanation=r"""
## Intuition

Strings are sequences, and each character has a **position** (an **index**). Every language here counts from **zero**: the first character is at index 0, the second at index 1, and the last at index `len - 1`.

```text
 index:   0   1   2   3   4   5   6   7
 char:    c   r   u   c   i   b   l   e
```

## Approach

Take index 0 and return it as a string.

```python
def first_character(s):
    return s[0]              # a str of length 1
```

```cpp
string firstCharacter(string s) {
    return string(1, s[0]);  // s[0] is a char; build a 1-char string from it
}
```

```rust
pub fn first_character(s: String) -> String {
    s[0..1].to_string()      // slice bytes 0..1, then make an owned String
}
```

```c
char* first_character(char* s) {
    char* out = malloc(2);   // room for one character + '\0'
    out[0] = s[0];
    out[1] = '\0';
    return out;
}
```

### Characters vs strings

Python has no separate character type: `s[0]` is a string of length 1. C, C++ and Rust do distinguish them: `'c'` (single quotes) is a `char`, `"c"` (double quotes) is a string. The function promises a *string*, so C++ and Rust must wrap the char. `string(1, s[0])` means "a string made of 1 copy of s[0]".

### Why C needs `malloc`

A function's local variables disappear when it returns. If you wrote `char out[2]; ... return out;`, you would return a pointer to memory that no longer belongs to you: a **dangling pointer**, and a classic C bug. `malloc(2)` requests 2 bytes from the heap that stay valid until someone calls `free`. The harness frees it for you. The second byte holds `'\0'` so the result is a proper C string.

### Rust slicing

`&s[0..1]` is a **slice** (a borrowed view) of bytes 0 up to but not including 1. Rust slices by byte offsets; for ASCII that is one character. `.to_string()` copies the slice into a new owned `String` that we can return. Rust forbids `s[0]` on strings precisely because a byte index may fall in the middle of a multi-byte character.

## Complexity

O(1) time and space.

## Common mistakes

* **`s[1]`**: that is the *second* character.
* **Returning a `char` where a string is expected** (C++/Rust compile errors).
* **Returning a pointer to a local array** in C.
* **Forgetting the `'\0'`** in C: the harness would read past your character into garbage.

## Going further

Return the *last* character: index `len(s) - 1`. Python also allows `s[-1]`, counting from the end; C, C++ and Rust do not.
""",
    solution=r'''def first_character(s: str) -> str:
    # Indexing starts at 0, so s[0] is the first character. In Python that
    # is already a str of length 1, which is exactly what we must return.
    # The constraints guarantee s is non-empty, so s[0] always exists
    # (on an empty string it would raise IndexError).
    return s[0]
''',
    refs={
        "c": r'''char* first_character(char* s) {
    // We must return memory that outlives this function call, so we ask
    // the heap for it. 2 bytes: the character and the '\0' terminator.
    char* out = malloc(2);
    out[0] = s[0];      // index 0 is the first character
    out[1] = '\0';      // mark the end of the string
    return out;         // the caller (the harness) frees it
}
''',
        "cpp": r'''string firstCharacter(string s) {
    // s[0] is a char; string(count, ch) builds a string of `count` copies.
    return string(1, s[0]);
}
''',
        "rust": r'''pub fn first_character(s: String) -> String {
    // &s[0..1] borrows bytes [0, 1): exactly one ASCII character.
    // to_string() makes an owned copy we can return.
    s[0..1].to_string()
}
''',
    },
    tests=[["crucible"], ["z"], ["Hello"], ["  leading space"], ["42 is the answer"], ["!?"], ["Q" + "q" * 999]],
))

# ----------------------------------------------------------------------------
# 17. Last element
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="last-element",
    title="Last Element",
    difficulty=0,
    tags=["arrays", "indexing"],
    fn="last_element",
    params=[["nums", "int[]"]],
    returns="int",
    statement=r"""
Your first **array**: an ordered list of values stored side by side.

Return the **last** element of `nums`. The array is never empty.
""",
    constraints=["1 ≤ len(nums) ≤ 1000", "-10⁹ ≤ nums[i] ≤ 10⁹"],
    hints=[
        "Indexes start at 0. If an array has 5 elements, what is the index of the last one?",
        "The last index is always `length - 1`.",
        "Python `nums[len(nums) - 1]` (or `nums[-1]`). C `nums[numsSize - 1]`. C++ `nums.back()`. Rust `nums[nums.len() - 1]`.",
    ],
    explanation=r"""
## Intuition

An array stores its elements in consecutive slots numbered from 0. With `n` elements the slots are `0, 1, ..., n - 1`, so the last element lives at index **`n - 1`**. Index `n` is one past the end: there is nothing there.

```text
nums = [4, 8, 15, 16, 23]
index:  0  1   2   3   4      n = 5, last index = 4
```

## Approach

Find the length, subtract one, index.

```python
def last_element(nums):
    return nums[len(nums) - 1]      # Python also allows nums[-1]
```

```c
long long last_element(long long* nums, int numsSize) {
    return nums[numsSize - 1];
}
```

```cpp
long long lastElement(vector<long long>& nums) {
    return nums[nums.size() - 1];   // or nums.back()
}
```

```rust
pub fn last_element(nums: Vec<i64>) -> i64 {
    nums[nums.len() - 1]            // or *nums.last().unwrap()
}
```

### Why C passes the size separately

In C, an array passed to a function decays into a **pointer** to its first element. A pointer is just an address; it carries no information about how many elements follow. That is why the C signature has a second parameter, `numsSize`. Every C function that takes an array needs its length passed alongside it.

In C++ a `vector` knows its own `size()`, and in Rust a `Vec` knows its `len()`. Python lists know their `len()`.

### What happens if you go one too far?

| language | `nums[n]` (one past the end) |
|---|---|
| Python | `IndexError` exception |
| Rust | panic: "index out of bounds" |
| C++ `[]` | undefined behaviour (reads garbage, may crash); `.at(n)` throws |
| C | undefined behaviour: silently reads whatever memory is next |

C's silence is why off-by-one errors there are so dangerous. Rust and Python catch them for you.

## Complexity

O(1): arrays support **random access**, so reaching any index takes the same time. The address of `nums[i]` is computed as `start + i × element_size`, no walking required.

## Common mistakes

* **`nums[len(nums)]`**: one past the end.
* **`sizeof(nums) / sizeof(nums[0])`** in C: inside a function `nums` is a pointer, so this computes 8 / 8 = 1. Use `numsSize`.
* **Rust: `nums.len() - 1` on an empty vector** would underflow (`usize` cannot be negative). The constraints rule it out here, but remember it.

## Going further

Return the **middle** element of an odd-length array: index `n / 2` using integer division. For `[4, 8, 15, 16, 23]`, `5 / 2 = 2`, giving 15.
""",
    solution=r'''def last_element(nums: list[int]) -> int:
    # Indexes run from 0 to len(nums) - 1, so the last valid index is one
    # less than the length. (Python also allows nums[-1], which counts from
    # the end, but C, C++ and Rust do not.) The array is guaranteed to be
    # non-empty, so this index always exists.
    return nums[len(nums) - 1]
''',
    refs={
        "c": r'''long long last_element(long long* nums, int numsSize) {
    // A C array arrives as a pointer plus a separate length;
    // the last valid index is numsSize - 1.
    return nums[numsSize - 1];
}
''',
        "cpp": r'''long long lastElement(vector<long long>& nums) {
    // back() returns the last element; same as nums[nums.size() - 1].
    return nums.back();
}
''',
        "rust": r'''pub fn last_element(nums: Vec<i64>) -> i64 {
    // len() is a usize; indexing a Vec takes a usize too.
    nums[nums.len() - 1]
}
''',
        "espresso": r'''fn lastElement(nums) {
    return nums[len(nums) - 1]
}
''',
    },
    tests=[[[4, 8, 15, 16, 23]], [[7]], [[-1, -2, -3]], [[0, 0, 0, 0]], [[5, 1000000000]],
           [[_rng.randint(-1000, 1000) for _ in range(60)]], [[3, -1000000000]]],
))

# ----------------------------------------------------------------------------
# 18. Sum of an array
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="sum-of-array",
    title="Sum of an Array",
    difficulty=0,
    tags=["arrays", "loops", "accumulator"],
    fn="array_sum",
    params=[["nums", "int[]"]],
    returns="int",
    statement=r"""
Return the sum of all the elements of `nums`. The sum of an empty array is `0`.

Write the loop yourself rather than calling a built-in `sum`.
""",
    constraints=["0 ≤ len(nums) ≤ 1000", "-10⁶ ≤ nums[i] ≤ 10⁶"],
    hints=[
        "Keep a running total that starts at 0.",
        "Visit every element once and add it to the running total.",
        "`total = 0`, then `for x in nums: total += x`, then `return total`.",
    ],
    explanation=r"""
## Intuition

This is the **accumulator pattern**, one of the most important patterns in programming: keep a variable holding "the answer so far", start it at a neutral value, and update it once for each element. For a sum the neutral starting value is 0 (adding 0 changes nothing), which also makes the empty array correct automatically.

## Approach

```python
def array_sum(nums):
    total = 0
    for x in nums:        # x takes each element's value in turn
        total += x        # same as total = total + x
    return total
```

```c
long long array_sum(long long* nums, int numsSize) {
    long long total = 0;
    for (int i = 0; i < numsSize; i++) {   // indexes 0 .. numsSize-1
        total += nums[i];
    }
    return total;
}
```

```cpp
long long arraySum(vector<long long>& nums) {
    long long total = 0;
    for (long long x : nums) total += x;   // range-based for loop
    return total;
}
```

```rust
pub fn array_sum(nums: Vec<i64>) -> i64 {
    let mut total = 0;        // `mut`: we are going to change it
    for x in &nums {          // &nums: borrow the elements, don't consume them
        total += x;
    }
    total
}
```

Trace for `[3, -1, 4, 1]`:

| element | total after |
|---|---|
| (start) | 0 |
| 3 | 3 |
| -1 | 2 |
| 4 | 6 |
| 1 | 7 |

### Two styles of loop

* **Index loop**: `for (int i = 0; i < n; i++) ... nums[i]`. Needed in C, and whenever you care about the position.
* **For-each loop**: `for x in nums` (Python, Rust), `for (auto x : nums)` (C++). Cleaner when you only need the values.

Note `i < numsSize`, not `<=`: the last valid index is `numsSize - 1`.

### `+=`

`total += x` is shorthand for `total = total + x`. Similar shorthands exist for `-=`, `*=`, `/=`.

### Rust's `mut`

Rust variables are immutable by default. Without `mut`, `total += x` is a compile error ("cannot assign twice to immutable variable"). This is deliberate: most values never change, and the ones that do are clearly marked.

## Complexity

O(n) time: each element is visited once. O(1) extra space: just the total.

## Common mistakes

* **Starting the total at the first element** (`total = nums[0]`): crashes on an empty array.
* **Off-by-one in C**: `i <= numsSize` reads past the end.
* **Declaring the total inside the loop**: it is reset every iteration.
* **32-bit totals.** Sums of large arrays can exceed 2.1 × 10⁹; use `long long` / `i64`.

## Going further

The one-liners: Python `sum(nums)`, C++ `accumulate(nums.begin(), nums.end(), 0LL)`, Rust `nums.iter().sum()`. Note the `0LL` in C++: with a plain `0`, `accumulate` would add in 32-bit `int` and could overflow.
""",
    solution=r'''def array_sum(nums: list[int]) -> int:
    # Accumulator pattern: start from the neutral value for addition (0).
    # Because we start at 0, an empty array correctly sums to 0 without any
    # special case: the loop simply never runs.
    total = 0
    for x in nums:
        # Fold each element into the running total.
        total += x
    return total
''',
    refs={
        "c": r'''long long array_sum(long long* nums, int numsSize) {
    long long total = 0;                 // 64-bit accumulator
    for (int i = 0; i < numsSize; i++) { // valid indexes: 0 .. numsSize - 1
        total += nums[i];
    }
    return total;                        // 0 for an empty array
}
''',
        "cpp": r'''long long arraySum(vector<long long>& nums) {
    long long total = 0;
    // Range-based for: x takes each element's value in order.
    for (long long x : nums) total += x;
    return total;
}
''',
        "rust": r'''pub fn array_sum(nums: Vec<i64>) -> i64 {
    let mut total: i64 = 0;   // mut: this variable will change
    for x in &nums {          // iterate over references to the elements
        total += x;           // i64 += &i64 works via auto-deref
    }
    total
}
''',
        "espresso": r'''fn arraySum(nums) {
    var total = 0
    for var i in 0..len(nums) {   // 0..n excludes n
        total += nums[i]
    }
    return total
}
''',
    },
    tests=[[[3, -1, 4, 1]], [[]], [[5]], [[-5, -10, -15]], [[0, 0, 0]], [[1000000] * 40],
           [[_rng.randint(-1000000, 1000000) for _ in range(60)]], [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]],
))

# ----------------------------------------------------------------------------
# 19. Count occurrences
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="count-occurrences",
    title="Count the Matches",
    difficulty=0,
    tags=["arrays", "loops", "counting"],
    fn="count_occurrences",
    params=[["nums", "int[]"], ["target", "int"]],
    returns="int",
    statement=r"""
Return how many elements of `nums` are equal to `target`.
""",
    constraints=["0 ≤ len(nums) ≤ 1000", "-1000 ≤ nums[i], target ≤ 1000"],
    example_notes=["2 appears three times.", "7 does not appear at all, so the count is 0."],
    hints=[
        "This is the accumulator pattern again, but you only add to it *sometimes*.",
        "Start a counter at 0. Look at each element; if it equals `target`, add 1.",
        "`count = 0`, `for x in nums: if x == target: count += 1`, `return count`.",
    ],
    explanation=r"""
## Intuition

Combine the two ideas you have learned: a **loop** that visits every element, and an **`if`** that decides whether this element matters. The accumulator here counts instead of sums: it goes up by 1 when the condition holds and stays put otherwise.

## Approach

```python
def count_occurrences(nums, target):
    count = 0
    for x in nums:
        if x == target:
            count += 1
    return count
```

```c
long long count_occurrences(long long* nums, int numsSize, long long target) {
    long long count = 0;
    for (int i = 0; i < numsSize; i++) {
        if (nums[i] == target) count++;
    }
    return count;
}
```

```cpp
long long countOccurrences(vector<long long>& nums, long long target) {
    long long count = 0;
    for (long long x : nums) if (x == target) count++;
    return count;
}
```

```rust
pub fn count_occurrences(nums: Vec<i64>, target: i64) -> i64 {
    let mut count = 0;
    for &x in &nums {          // &x pattern copies the i64 out of the reference
        if x == target { count += 1; }
    }
    count
}
```

Trace for `nums = [2, 5, 2, 2, 9]`, `target = 2`:

| x | `x == 2`? | count |
|---|---|---|
| 2 | yes | 1 |
| 5 | no | 1 |
| 2 | yes | 2 |
| 2 | yes | 3 |
| 9 | no | 3 |

### `count++`

In C and C++, `count++` adds 1 to `count`. Rust and Python do not have `++`; write `count += 1`.

### Note the C signature

The C version has three parameters: the pointer, its size, then `target`. The array's length always travels right after the array.

## Complexity

O(n) time, O(1) space. Every element must be examined: an element you skip might be a match.

## Common mistakes

* **`=` instead of `==`** in C/C++ (`if (nums[i] = target)` assigns and is almost always true).
* **Returning inside the loop** (`return count` indented under the `for`): it returns after the first element.
* **`count = 1` initially**, or resetting it inside the loop.

## Going further

Built-ins: Python `nums.count(target)`, C++ `count(nums.begin(), nums.end(), target)`, Rust `nums.iter().filter(|&&x| x == target).count()`. A harder variant: count how many elements are *greater* than the target, or return the *index of the first* match (and -1 if none).
""",
    solution=r'''def count_occurrences(nums: list[int], target: int) -> int:
    # A counting accumulator: it starts at 0 and only moves when the
    # condition holds. With an empty array the loop never runs and 0 is
    # correctly returned.
    count = 0
    for x in nums:
        # Every element has to be checked; any of them might match.
        if x == target:
            count += 1
    # The return is outside the loop, so it happens after ALL elements.
    return count
''',
    refs={
        "c": r'''long long count_occurrences(long long* nums, int numsSize, long long target) {
    long long count = 0;
    for (int i = 0; i < numsSize; i++) {
        if (nums[i] == target) {   // == compares; a single = would assign
            count++;
        }
    }
    return count;
}
''',
        "cpp": r'''long long countOccurrences(vector<long long>& nums, long long target) {
    long long count = 0;
    for (long long x : nums) {
        if (x == target) count++;
    }
    return count;
}
''',
        "rust": r'''pub fn count_occurrences(nums: Vec<i64>, target: i64) -> i64 {
    let mut count = 0;
    // Iterating over &nums yields &i64; the pattern &x copies out the value.
    for &x in &nums {
        if x == target {
            count += 1;
        }
    }
    count
}
''',
        "espresso": r'''fn countOccurrences(nums, target) {
    var count = 0
    for var i in 0..len(nums) {
        if nums[i] == target {
            count += 1
        }
    }
    return count
}
''',
    },
    tests=[[[2, 5, 2, 2, 9], 2], [[1, 2, 3], 7], [[], 0], [[4, 4, 4, 4], 4], [[-1, 1, -1, 1], -1], [[0], 0],
           [[_rng.randint(-3, 3) for _ in range(80)], 0], [[1000, -1000, 1000], 1000]],
))

# ----------------------------------------------------------------------------
# 20. Average of an array
# ----------------------------------------------------------------------------
PROBLEMS.append(dict(
    id="average-of-array",
    title="Average of an Array",
    difficulty=0,
    tags=["arrays", "floats", "loops"],
    # ESPresso floats are 32-bit and print with 6 significant digits, so
    # averages like -5/3 cannot meet the 1e-6 tolerance.
    espresso=False,
    fn="average_of",
    params=[["nums", "int[]"]],
    returns="float",
    statement=r"""
Return the average (arithmetic mean) of the integers in `nums`: their sum divided by how many there are.

The result is a decimal number. `nums` is never empty. Answers within 10⁻⁶ of the expected value are accepted.
""",
    constraints=["1 ≤ len(nums) ≤ 1000", "-10⁶ ≤ nums[i] ≤ 10⁶"],
    example_notes=["(1 + 2 + 3 + 4) / 4 = 2.5. Note that the answer is not a whole number.", "A single element is its own average."],
    hints=[
        "First compute the sum, exactly as in \"Sum of an Array\".",
        "Then divide by the number of elements. Be careful: the sum and the count are both integers.",
        "In C/C++ convert before dividing: `(double)total / numsSize`. In Rust: `total as f64 / nums.len() as f64`.",
    ],
    explanation=r"""
## Intuition

The average is the sum divided by the count. You already know how to sum. The lesson is about **types meeting in a division**: the sum and the count are integers, but the answer is not.

## Approach

1. Sum the elements with an accumulator.
2. Convert to floating point.
3. Divide by the count.

```python
def average_of(nums):
    total = 0
    for x in nums:
        total += x
    return total / len(nums)        # Python's / always gives a float
```

```c
double average_of(long long* nums, int numsSize) {
    long long total = 0;
    for (int i = 0; i < numsSize; i++) total += nums[i];
    return (double)total / numsSize;   // cast FIRST, then divide
}
```

```cpp
double averageOf(vector<long long>& nums) {
    long long total = 0;
    for (long long x : nums) total += x;
    return (double)total / nums.size();
}
```

```rust
pub fn average_of(nums: Vec<i64>) -> f64 {
    let total: i64 = nums.iter().sum();
    total as f64 / nums.len() as f64    // both sides must be f64
}
```

Trace for `[1, 2, 3, 4]`: total = 10, count = 4.

| expression | C result |
|---|---|
| `total / numsSize` | `2` (integer division, fraction thrown away) |
| `(double)(total / numsSize)` | `2.0` (too late: already truncated) |
| `(double)total / numsSize` | `2.5` (correct) |

### Casts

A **cast** converts a value to another type: `(double)total` in C/C++, `total as f64` in Rust, `float(total)` in Python. When one side of `/` is a double, C and C++ promote the other side to double automatically, so casting one operand is enough. The cast must apply to an operand *before* the division, not to the result.

Rust never promotes automatically: both sides must already be `f64`, hence two `as f64`.

### Accumulate in integers, divide once

Summing in an integer and converting once at the end is exact. Summing directly into a double works here, but with many fractional numbers small rounding errors can pile up.

## Complexity

O(n) time, O(1) extra space.

## Common mistakes

* **Integer division** in C, C++, Rust, and ESPresso (and Python's `//`): `10 / 4` is `2`.
* **Casting the result** instead of an operand: `(double)(total / n)`.
* **Dividing inside the loop** instead of after it.
* **Using a 32-bit int** for the total: 1000 × 10⁶ = 10⁹ fits, but only barely; use `long long`.

## Going further

Return the average rounded to the nearest integer, or compute the average of only the positive elements (watch out: there might be none, and dividing by zero must be avoided).
""",
    solution=r'''def average_of(nums: list[int]) -> float:
    # Step 1: accumulate the sum exactly, using integers.
    total = 0
    for x in nums:
        total += x
    # Step 2: divide once, at the end. Python's "/" is true division and
    # always returns a float (10 / 4 == 2.5), unlike integer division in
    # C, C++ and Rust. nums is guaranteed non-empty, so len(nums) > 0 and
    # we never divide by zero.
    return total / len(nums)
''',
    refs={
        "c": r'''double average_of(long long* nums, int numsSize) {
    long long total = 0;
    for (int i = 0; i < numsSize; i++) total += nums[i];
    // Cast an OPERAND to double before dividing; (double)(total / numsSize)
    // would cast an already-truncated integer result.
    return (double)total / numsSize;
}
''',
        "cpp": r'''double averageOf(vector<long long>& nums) {
    long long total = 0;
    for (long long x : nums) total += x;
    // static_cast is the C++-style cast; once one side is a double,
    // the other side is promoted automatically.
    return static_cast<double>(total) / nums.size();
}
''',
        "rust": r'''pub fn average_of(nums: Vec<i64>) -> f64 {
    let total: i64 = nums.iter().sum();
    // Rust never converts implicitly: both operands must be f64.
    total as f64 / nums.len() as f64
}
''',
    },
    tests=[[[1, 2, 3, 4]], [[7]], [[-3, 3]], [[1, 2]], [[-1, -2, -2]], [[1000000] * 40],
           [[_rng.randint(-1000000, 1000000) for _ in range(60)]], [[0, 0, 1]]],
))
