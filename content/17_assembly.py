"""Assembly track: fill-in-the-blanks AArch64 (Apple Silicon) and x86-64 (AT&T syntax) for macOS."""

import random

TRACK = dict(
    id="assembly",
    title="Assembly: ARM64 & x86-64",
    order=17,
    icon="⚙",
    blurb="Write the machine's own language: registers, flags, loads, loops and stack frames, in ARM64 (Apple Silicon) or x86-64 (Intel).",
    intro=r"""Every program you have written so far eventually becomes a list of
**instructions**: tiny, fixed-size commands the CPU executes one after another.
In this track you write those instructions yourself, in **AArch64** (64-bit ARM)
assembly, the instruction set of every Apple Silicon Mac. Each problem gives you an
almost-complete `.s` file; a few crucial lines are replaced by `// TODO(n): ...`
comments, and your job is to write exactly those instructions.

## Registers: the CPU's variables

There are no named variables in assembly. There are **31 general-purpose registers**,
each 64 bits wide, called `x0` … `x30`. Each one also has a 32-bit view, `w0` … `w30`,
which is just the low half of the same register:

```text
 63                              32 31                               0
+----------------------------------+----------------------------------+
|                 x5 (all 64 bits)                                    |
+----------------------------------+----------------------------------+
                                   |          w5 (low 32 bits)        |
                                   +----------------------------------+
```

Writing to `w5` **zeroes the upper 32 bits** of `x5`. Use `x` registers for 64-bit
integers and pointers (all of our `int`s are C `long long`, i.e. 64 bits) and `w`
registers when you work with bytes and characters.

Two more names matter: `sp`, the stack pointer, and `xzr`/`wzr`, the **zero register**,
which reads as 0 and discards anything written to it.

## The calling convention (AAPCS64)

Your function is called from C, so both sides must agree on where things live.
That agreement is the *Procedure Call Standard*, AAPCS64:

| registers | role | who must preserve them |
|---|---|---|
| `x0`–`x7` | arguments 1–8, `x0` also holds the **return value** | nobody (caller-saved) |
| `x8`–`x17` | scratch | nobody: use them freely |
| `x18` | platform register: **never touch on macOS** | |
| `x19`–`x28` | long-lived values | **you** (callee-saved): save before use, restore before `ret` |
| `x29` | frame pointer (`fp`) | you |
| `x30` | link register (`lr`): the return address | you, if you call anything |
| `sp` | stack pointer, must stay **16-byte aligned** | you |

A leaf function (one that calls nobody) that only uses `x0`–`x17` needs no setup at
all: compute, put the answer in `x0`, and `ret`.

## How the C harness calls your function

The test harness is a C program that declares your function and calls it:

```c
extern long long sum_array(long long* nums, long long numsSize);   // what C sees
long long r = sum_array(a0, 3);                                   // x0 = a0, x1 = 3
```

* `int` → one register holding a signed 64-bit value.
* `int[]` → **two** registers: a pointer to the first element, then the element count
  (64-bit). Each element is 8 bytes, so element `i` lives at address `ptr + 8*i`.
* `str` → one register: a pointer to NUL-terminated bytes (`const char*`).
* `bool` result → return `1` or `0` in `x0`.
* `void` + in-place array → modify the memory the pointer points at; the harness prints
  the array afterwards.

For `f(nums: int[], target: int)` that means `x0 = nums`, `x1 = len(nums)`, `x2 = target`.

The symbol must be named with a leading underscore (`_sum_array`) because macOS
prefixes every C name with `_`. Every file starts the same way:

```asm
.text                   // put what follows in the code section
.globl _sum_array       // export the symbol so the linker can find it
.p2align 2              // align to 2^2 = 4 bytes (every instruction is 4 bytes)
_sum_array:             // the label IS the function
```

## The instructions you will use most

| instruction | meaning |
|---|---|
| `mov x0, #42` / `mov x0, x1` | copy an immediate or a register |
| `add x0, x1, x2` / `sub` / `mul` | arithmetic, destination first |
| `madd x0, x1, x2, x3` / `msub` | `x3 + x1*x2` / `x3 - x1*x2` |
| `udiv` / `sdiv` | unsigned / signed division (no remainder instruction!) |
| `and orr eor lsl lsr asr` | bitwise logic and shifts |
| `cmp x1, x2` | compute `x1 - x2`, throw the result away, **set flags** |
| `tst x1, #1` | compute `x1 & 1`, set flags |
| `b label` / `b.cond label` | jump / jump if condition |
| `cbz x1, label` / `cbnz` | jump if register is zero / non-zero (no flags needed) |
| `csel x0, x1, x2, cond` | `x0 = cond ? x1 : x2` (branch-free) |
| `cset x0, cond` / `cinc` / `cneg` | `x0 = cond ? 1 : 0` / conditional `+1` / conditional negate |
| `bl label` | call: jump and put the return address in `x30` |
| `ret` | return: jump to the address in `x30` |

## Memory: loads, stores and addressing modes

ARM is a *load/store* architecture: arithmetic only works on registers, so you move
data in with `ldr` (load register) and out with `str` (store register). The part in
square brackets is the **address**:

| syntax | address used | side effect |
|---|---|---|
| `ldr x1, [x0]` | `x0` | none |
| `ldr x1, [x0, #16]` | `x0 + 16` | none (offset) |
| `ldr x1, [x0, x2, lsl #3]` | `x0 + x2*8` | none: perfect for `nums[i]` |
| `ldr x1, [x0, #8]!` | `x0 + 8` | `x0 += 8` **before** (pre-index) |
| `ldr x1, [x0], #8` | `x0` | `x0 += 8` **after** (post-index): walk an array |

The **size** comes from the instruction and register: `ldr x1` loads 8 bytes,
`ldr w1` loads 4, `ldrb w1` loads **1 byte** and zero-extends it. Strings are bytes, so
use `ldrb`/`strb` for characters. `ldp`/`stp` load/store a *pair* of registers at
once (`ldp x1, x2, [x0]` reads `x0[0]` and `x0[1]`).

## Condition flags and `b.cond`

`cmp a, b` sets four flags: **N** (negative), **Z** (zero), **C** (carry), **V**
(overflow). The condition suffix reads them for you. The crucial thing is that the
CPU does not know whether your numbers are signed:

| you mean | signed (ints) | unsigned (addresses, sizes) |
|---|---|---|
| `a == b` / `a != b` | `eq` / `ne` | `eq` / `ne` |
| `a < b` | `lt` | `lo` (also `cc`) |
| `a <= b` | `le` | `ls` |
| `a > b` | `gt` | `hi` |
| `a >= b` | `ge` | `hs` (also `cs`) |

Use `lt/le/gt/ge` for values that can be negative and `lo/ls/hi/hs` for pointers and
counts. Mixing them up is the single most common assembly bug: `-1` compared unsigned
is 18,446,744,073,709,551,615.

A loop in assembly is just a label and a backwards branch:

```asm
    mov x2, #0              // total = 0
Lloop:                      // labels starting with L are private to the file
    cbz x1, Ldone           // while (count != 0)
    ldr x3, [x0], #8        //   x3 = *ptr++
    add x2, x2, x3          //   total += x3
    sub x1, x1, #1          //   count--
    b Lloop                 // repeat
Ldone:
    mov x0, x2              // return total
    ret
```

## The stack frame

When your function calls another function (even itself), `bl` overwrites `x30`, so
you must save your own return address first. The standard prologue/epilogue:

```asm
    stp x29, x30, [sp, #-32]!   // sp -= 32, then store fp and lr at [sp]
    mov x29, sp                 // new frame pointer
    stp x19, x20, [sp, #16]     // save callee-saved registers we will use
    ...                         // body: bl other functions freely
    ldp x19, x20, [sp, #16]     // restore them
    ldp x29, x30, [sp], #32     // restore fp and lr, then sp += 32
    ret
```

```text
   higher addresses
   +----------------+  <- sp on entry
   |   x20 (saved)  |  sp+24
   |   x19 (saved)  |  sp+16
   |   x30 (lr)     |  sp+8
   |   x29 (fp)     |  sp+0   <- sp and x29 after the prologue
   +----------------+
   lower addresses (the stack grows down)
```

`sp` must always be a multiple of 16, so allocate in 16-byte chunks. Values that must
survive a `bl` go in `x19`–`x28` (which the callee preserves), never in `x0`–`x17`.

## Reading clang's error messages

Your file is assembled and linked together with the C harness by `clang`. Errors look
like this:

```text
solution.s:12:10: error: invalid operand for instruction
    add x0, x1, w2
                ^
```

`12:10` is line 12, column 10, and the caret points at the offending token. The usual
causes:

* **invalid operand for instruction**: mixed `x` and `w` registers, or an immediate
  that is too large (`add` takes 12-bit immediates, `mov` cannot build every constant).
* **unknown token in expression** / **unexpected token in argument list**: a missing
  comma, `#`, or bracket (`ldr x0 [x1]`).
* **unrecognized instruction mnemonic**: a typo (`mvo`) or an x86 habit (`jmp`, `inc`).
* **Undefined symbols for architecture arm64: "_name"**: the linker could not find
  your function. Check `.globl` and the leading underscore.
* **expected compatible register or logical immediate**: the constant cannot be
  encoded as a logical immediate (only repeating bit patterns are allowed).

If it assembles but misbehaves: a **segmentation fault** usually means a bad address
(`ldr` instead of `ldrb`, a wrong offset, a pointer you forgot to advance or advanced
too far), a **timeout** means a loop that never reaches its exit branch, and a crash
right after `ret` means `x30` or `sp` was not restored.

Start slow: the first problems are one instruction each. By the end you will write
sorting loops and a recursive function that manages its own stack frame.

## x86-64 (AT&T syntax)

Every problem also comes in an **x86-64** version, the instruction set of Intel Macs
and most PCs. Switch the language in the editor to get the x86 starter; your file is
built with `clang -arch x86_64` and runs under Rosetta 2. The problem statements
describe the ARM registers, so each x86 version has its own notes with the register
mapping. The syntax is the **AT&T** flavour that clang and GNU tools use by default:

* **Source first, destination last**: `movq %rsi, %rax` copies `rsi` into `rax`
  (the reverse of ARM and of Intel syntax).
* **Two operands**: `addq %rsi, %rax` means `rax = rax + rsi`. The destination is
  also a source, so copy a value first if you still need it.
* Registers start with `%`, immediates with `$` (`$42`, `$0x20`, `$'a'`). A bare
  number is a **memory address**.
* A **size suffix** on the mnemonic: `b` (byte), `w` (16-bit word), `l` (32-bit long),
  `q` (64-bit quad). Our `long long`s are all `q`.
* Comments start with `#`; labels and directives work as on ARM, except
  `.p2align 4` (16-byte function alignment, since x86 instructions are 1 to 15 bytes long).

**Memory operands** are written `disp(base, index, scale)` and mean
`base + index*scale + disp`, with scale 1, 2, 4 or 8:

| syntax | address | typical use |
|---|---|---|
| `(%rdi)` | `rdi` | `*p` |
| `16(%rdi)` | `rdi + 16` | `p[2]` for 8-byte elements |
| `(%rdi,%rcx,8)` | `rdi + rcx*8` | `nums[i]` |
| `-8(%rdi,%rsi,8)` | `rdi + rsi*8 - 8` | `&nums[count-1]` with `lea` |

Most instructions accept **one** memory operand directly (`addq (%rdi), %rax` loads
and adds in one go); there is no post-increment, so advance pointers with `addq $8, %rdi`.
`lea` computes an address expression *without* reading memory, which doubles as a
three-operand add. Load bytes with `movzbq` (zero-extend byte to 64 bits).

### Registers

| 64-bit | 32-bit | 16-bit | 8-bit | 64-bit | 32-bit | 16-bit | 8-bit |
|---|---|---|---|---|---|---|---|
| `rax` | `eax` | `ax` | `al` | `r8` | `r8d` | `r8w` | `r8b` |
| `rbx` | `ebx` | `bx` | `bl` | `r9` | `r9d` | `r9w` | `r9b` |
| `rcx` | `ecx` | `cx` | `cl` | `r10` | `r10d` | `r10w` | `r10b` |
| `rdx` | `edx` | `dx` | `dl` | `r11` | `r11d` | `r11w` | `r11b` |
| `rsi` | `esi` | `si` | `sil` | `r12` | `r12d` | `r12w` | `r12b` |
| `rdi` | `edi` | `di` | `dil` | `r13` | `r13d` | `r13w` | `r13b` |
| `rbp` | `ebp` | `bp` | `bpl` | `r14` | `r14d` | `r14w` | `r14b` |
| `rsp` | `esp` | `sp` | `spl` | `r15` | `r15d` | `r15w` | `r15b` |

As on ARM, writing a **32-bit** register (`movl $0, %eax`, `xorl %edx, %edx`) zeroes
the upper 32 bits. Writing an 8- or 16-bit register does **not**: the other bytes keep
their old contents. There is no zero register; `xorl %eax, %eax` is the idiom for 0.

### The calling convention (System V AMD64)

| registers | role | who must preserve them |
|---|---|---|
| `rdi`, `rsi`, `rdx`, `rcx`, `r8`, `r9` | arguments 1–6, in that order | nobody (caller-saved) |
| `rax` | **return value** | nobody |
| `r10`, `r11` | scratch | nobody |
| `rbx`, `rbp`, `r12`–`r15` | long-lived values | **you** (callee-saved) |
| `rsp` | stack pointer, **16-byte aligned at every `call`** | you |

`call` pushes the return address onto the stack and `ret` pops it, so there is no link
register. On entry `rsp` is therefore 8 bytes off alignment: a function that calls
others must push an odd number of 8-byte values (e.g. `pushq %rbp` plus two more)
before its first `call`, and pop them in reverse order before `ret`.

### Flags, jumps, `cmov` and `setcc`

Almost every arithmetic instruction sets the flags (ZF, SF, CF, OF). `cmpq src, dst`
computes `dst - src`; `testq src, dst` computes `dst & src` (`testq %rax, %rax` asks
"is rax zero?"). Note the order: after `cmpq %rsi, %rdi`, `jl` jumps if `rdi < rsi`.

| you mean | signed | unsigned |
|---|---|---|
| `==` / `!=` | `e` / `ne` (also `z` / `nz`) | `e` / `ne` |
| `<` | `l` | `b` (below) |
| `<=` | `le` | `be` |
| `>` | `g` | `a` (above) |
| `>=` | `ge` | `ae` |

The condition goes after the stem: `jCC label` jumps (`jmp` is unconditional),
`cmovCCq src, dst` copies only if the condition holds (branch-free select), and
`setCC %al` writes the byte 1 or 0 (widen with `movzbq %al, %rax`). Multiplication is
two-operand `imulq src, dst`; division is `divq`/`idivq src`, which divides the 128-bit
`rdx:rax` and leaves the quotient in `rax` and the remainder in `rdx` (clear `rdx` first,
or `cqto` for signed).

### Reading clang's x86 errors

* **invalid operand for instruction**: suffix and register size disagree
  (`addq %eax, %rbx`), operands in Intel order, an immediate as destination, or two
  memory operands.
* **unknown token in expression**: usually a missing `%` or `$`.
* **invalid instruction mnemonic 'xyz'**: a typo or an ARM habit (`ldr`, `cbz`, `b.eq`).
* **Undefined symbols for architecture x86_64: "_name"**: check `.globl` and the underscore.
* **ambiguous instructions require an explicit suffix**: a memory operand with an
  immediate (`cmp $0, (%rsi)`) needs `b`/`w`/`l`/`q`.

A segmentation fault often means a missing `$` (a constant used as an address) or a
missing pair of parentheses; a crash inside a `call` usually means `rsp` was not
16-byte aligned.
""",
)


def _starter(sol, todos, comment="//"):
    """Replace each instruction line starting with `needle` by a `// TODO(n): text` line."""
    lines = sol.split("\n")
    for n, (needle, text) in enumerate(todos, 1):
        hits = [i for i, l in enumerate(lines) if l.strip().startswith(needle)]
        assert len(hits) == 1, (needle, hits)
        i = hits[0]
        indent = lines[i][: len(lines[i]) - len(lines[i].lstrip())]
        lines[i] = f"{indent}{comment} TODO({n}): {text}"
    return "\n".join(lines)


_R = random.Random(1717)

PROBLEMS = []


def _add(p, todos):
    p["kind"] = "asm"
    p["asm_starter"] = _starter(p["asm_solution"], todos)
    x = p.pop("x86", None)
    if x:
        # x86-64 (AT&T syntax) version of the same problem: x86=dict(solution, todos,
        # notes, hints, explanation). Notes become the x86 language notes.
        p["x86_solution"] = x["solution"]
        p["x86_starter"] = _starter(x["solution"], x["todos"], "#")
        p["x86_hints"] = x["hints"]
        p["x86_explanation"] = x["explanation"]
        p.setdefault("lang_notes", {})["x86"] = x["notes"]
    PROBLEMS.append(p)


# ---------------------------------------------------------------- 1. constant
_add(dict(
    id="asm-return-constant",
    title="The Answer Is 42",
    difficulty=0,
    tags=["mov", "ret", "basics"],
    fn="the_answer",
    params=[["x", "int"]],
    returns="int",
    statement="""Your first assembly function: whatever argument it receives, it must
return the number **42**.

**On entry:** `x0 = x` (a 64-bit signed integer that you should ignore).
**On exit:** `x0 = 42`.

The return value of a function always travels back to C in `x0`, the same register
the first argument arrived in, so you must overwrite it.""",
    constraints=["−10⁹ ≤ x ≤ 10⁹"],
    hints=[
        "The result goes in `x0`. Right now `x0` still holds the argument.",
        "`mov` copies a value into a register. Immediates (constants) are written with `#`.",
        "`mov x0, #42`",
    ],
    solution='''def the_answer(x):
    # The argument is deliberately ignored: in assembly it arrives in x0,
    # and returning means overwriting x0 with the answer.
    return 42
''',
    asm_solution="""// long long the_answer(long long x)
// On entry: x0 = x (ignored)      On exit: x0 = 42
.text                          // the following lines are code
.globl _the_answer             // export the symbol so the C harness can link to it
.p2align 2                     // align to 4 bytes: every A64 instruction is 4 bytes long
_the_answer:                   // the label marks the function's first instruction
    mov x0, #42                // overwrite the argument with the return value
    ret                        // jump back to the caller (address in x30)
""",
    tests=[[7], [0], [-5], [42], [1000000000], [-1000000000], [123456]],
    explanation="""## Intuition

A C function `long long f(long long x)` compiles to a label plus some instructions.
The caller puts `x` in `x0`, executes `bl _the_answer` (which stores the return address
in `x30`), and when your code executes `ret` the caller reads **whatever is in `x0`** as
the result. So "return 42" literally means "make `x0` equal 42, then `ret`".

## Approach

| step | instruction | x0 | x30 |
|---|---|---|---|
| entry | | 7 | return address in the harness |
| 1 | `mov x0, #42` | 42 | unchanged |
| 2 | `ret` | 42 | jumps there |

**The lines of the file**

* `.text`: a *directive* (starts with `.`), not an instruction. It tells the assembler
  to place what follows in the executable code section.
* `.globl _the_answer`: makes the label visible to the linker. Without it the C
  harness cannot find your function. The underscore is the macOS C name prefix.
* `.p2align 2`: pads to a multiple of 2² = 4 bytes, since instructions must be aligned.
* `_the_answer:`: a label is just a name for an address.
* `mov x0, #42`: copies the immediate 42 into `x0`. The `#` marks a constant.
* `ret`: branches to the address in `x30` (the *link register*).

## Complexity

O(1): two instructions.

## Common mistakes

* **Forgetting `ret`.** The CPU does not stop at the end of your text: it keeps
  executing whatever bytes come next, usually crashing with a bus error or segfault.
* **Writing `mov x0, 42`** without `#`. Clang's assembler is lenient about this one, but
  other assemblers are not; always write the `#`.
* **Putting the result in another register** (`mov x1, #42`). C only ever looks at `x0`.
* **Dropping the underscore** in `.globl` or the label: the link fails with
  `Undefined symbols for architecture arm64: "_the_answer"`.

## Going further

Large constants: `mov` can only encode 16-bit chunks (plus some patterns). The assembler
expands `mov x0, #0x12345678` into `movz x0, #0x5678` then `movk x0, #0x1234, lsl #16`.
Try a constant that needs more than one chunk and read the error, or the disassembly
with `objdump -d`.""",
    x86=dict(
        solution="""# long long the_answer(long long x)
# On entry: rdi = x (ignored)      On exit: rax = 42
.text                          # the following lines are code
.globl _the_answer             # export the symbol so the C harness can link to it
.p2align 4                     # align to 16 bytes (x86 instructions vary in length; 16 is the usual choice)
_the_answer:                   # the label marks the function's first instruction
    movq $42, %rax             # write the return value into rax (the argument in rdi is ignored)
    ret                        # pop the return address off the stack and jump to it
""",
        todos=[("movq $42, %rax", "put the constant 42 into the return register rax")],
        notes="""**On entry:** `%rdi = x` (ignore it). **On exit:** `%rax = 42`.

On x86-64 the first argument arrives in `%rdi`, but the result goes back in a
*different* register, `%rax`. AT&T syntax writes the source first and the
destination last, registers start with `%` and constants with `$`:
`movq $7, %rcx` puts 7 into `rcx`.""",
        hints=[
            "The result must be in `%rax`; the argument in `%rdi` can stay where it is.",
            "`mov` with a `q` suffix copies 64 bits. Constants take a `$`, and the destination comes last.",
            "`movq $42, %rax`",
        ],
        explanation="""## Intuition

The caller executes `call _the_answer`, which pushes the return address on the stack.
When your code executes `ret`, the caller reads **whatever is in `%rax`** as the result.
So "return 42" means "make `%rax` equal 42, then `ret`".

## Approach

| step | instruction | rdi | rax |
|---|---|---|---|
| entry | | 7 | garbage |
| 1 | `movq $42, %rax` | 7 | 42 |
| 2 | `ret` | | **42** |

* `.p2align 4` pads to 2⁴ = 16 bytes. x86 instructions are 1 to 15 bytes long and need
  no alignment, but function entries are conventionally 16-byte aligned.
* `movq $42, %rax`: `q` (quadword) means 64 bits, `$42` is an immediate, `%rax` is the
  destination. AT&T always reads **source, destination**.
* `ret` pops the return address that `call` pushed and jumps there.

## Complexity

O(1).

## Common mistakes

* **Intel order.** `movq %rax, $42` tries to write *into* a constant: clang reports
  `invalid operand for instruction`.
* **Forgetting `$`.** `movq 42, %rax` loads the 8 bytes at **memory address 42**: a
  segmentation fault.
* **Returning in `%rdi`.** The argument register is not the return register on x86-64.""",
    ),
), [("mov x0, #42", "put the constant 42 into the return register x0")])

# ---------------------------------------------------------------- 2. add
_add(dict(
    id="asm-add-two",
    title="Add Two Numbers",
    difficulty=0,
    tags=["add", "registers"],
    fn="add_two",
    params=[["a", "int"], ["b", "int"]],
    returns="int",
    statement="""Return `a + b`.

**On entry:** `x0 = a`, `x1 = b` (64-bit signed integers).
**On exit:** `x0 = a + b`.""",
    constraints=["−10¹² ≤ a, b ≤ 10¹²"],
    hints=[
        "ARM instructions take a destination and two sources: `op dst, src1, src2`.",
        "The destination can be one of the sources.",
        "`add x0, x0, x1`",
    ],
    solution='''def add_two(a, b):
    # Arguments arrive in x0 and x1; the sum must end up in x0.
    return a + b
''',
    asm_solution="""// long long add_two(long long a, long long b)
// On entry: x0 = a, x1 = b       On exit: x0 = a + b
.text                          // code section
.globl _add_two                // export the symbol to the linker
.p2align 2                     // 4-byte instruction alignment
_add_two:                      // function entry
    add x0, x0, x1             // x0 = x0 + x1 (destination first, then the two sources)
    ret                        // return; the caller reads the result from x0
""",
    tests=[[3, 4], [0, 0], [-5, 5], [-7, -8], [10**12, 10**12], [-10**12, 1], [123, -456]],
    explanation="""## Intuition

The first two arguments of a C function are in `x0` and `x1`. One `add` combines them,
and because the result must be in `x0` we make `x0` the destination.

## Approach

| step | instruction | x0 | x1 |
|---|---|---|---|
| entry | | 3 | 4 |
| 1 | `add x0, x0, x1` | 7 | 4 |
| 2 | `ret` | **7** | |

`add Xd, Xn, Xm` reads `Xn` and `Xm`, adds them, and writes `Xd`. All three operands are
registers here; the second source may also be an immediate (`add x0, x0, #1`, any value
0–4095, optionally shifted left by 12).

Two's complement makes signed and unsigned addition the **same instruction**: the bits
of `-5 + 5` and of `0xFFFF…FFFB + 5` are identical. Signedness only matters when you
*compare* or *divide*.

## Complexity

O(1).

## Common mistakes

* **Operand order.** ARM puts the destination first. `add x1, x0, x1` computes the right
  sum but leaves it in `x1`, and C reads `x0`.
* **Mixing widths.** `add x0, x0, w1` is rejected: `invalid operand for instruction`.
  All operands of an arithmetic instruction must be the same width (or use an explicit
  extend like `add x0, x0, w1, sxtw`).
* **Using `w` registers for 64-bit data.** `add w0, w0, w1` adds only the low 32 bits
  and zeroes the top half of `x0`: the `10¹²` tests would fail.

## Going further

`adds` is `add` that also sets the flags. After `adds x0, x0, x1`, `b.vs` branches on
signed overflow and `b.cs` on unsigned carry: this is how checked arithmetic is built.""",
    x86=dict(
        solution="""# long long add_two(long long a, long long b)
# On entry: rdi = a, rsi = b       On exit: rax = a + b
.text                          # code section
.globl _add_two                # export the symbol to the linker
.p2align 4                     # 16-byte function alignment
_add_two:                      # function entry
    movq %rdi, %rax            # rax = a (copy the first argument into the return register)
    addq %rsi, %rax            # rax = rax + b (AT&T: add source into destination)
    ret                        # return; the caller reads the result from rax
""",
        todos=[("addq %rsi, %rax", "add b into rax, which already holds a")],
        notes="""**On entry:** `%rdi = a`, `%rsi = b`. **On exit:** `%rax = a + b`.

x86 arithmetic has only **two** operands: `op src, dst` means `dst = dst op src`. So
you first copy one value into the destination, then combine the other into it
(for example `subq %rcx, %rdx` computes `rdx = rdx - rcx`).""",
        hints=[
            "`%rax` already holds a copy of `a`. Only `b` still needs to go in.",
            "Two-operand form: the destination is also the first source, and it is written last.",
            "`addq %rsi, %rax`",
        ],
        explanation="""## Intuition

`a` is in `%rdi`, `b` in `%rsi`, and the result must be in `%rax`. Copy `a` into
`%rax`, then add `b` into it.

## Approach

| step | instruction | rdi | rsi | rax |
|---|---|---|---|---|
| entry | | 3 | 4 | ? |
| 1 | `movq %rdi, %rax` | 3 | 4 | 3 |
| 2 | `addq %rsi, %rax` | 3 | 4 | **7** |

`addq src, dst` reads both, adds, and overwrites `dst`. It also sets the flags (x86
arithmetic always does), which we ignore here.

## Complexity

O(1).

## Common mistakes

* **Reversed operands.** `addq %rax, %rsi` leaves the sum in `%rsi`.
* **32-bit names.** `addl %esi, %eax` adds only the low halves and zeroes the top
  of `%rax`: the `10¹²` tests fail.
* **Suffix/register mismatch.** `addq %esi, %rax` is rejected: `invalid operand for instruction`.

## Going further

`leaq (%rdi,%rsi), %rax` computes the same sum in one instruction using the
address-computation unit, without touching the flags.""",
    ),
), [("add x0, x0, x1", "add the two arguments and leave the sum in x0")])

# ---------------------------------------------------------------- 3. mul/sub
_add(dict(
    id="asm-multiply-subtract",
    title="Multiply Then Subtract",
    difficulty=0,
    tags=["mul", "sub", "scratch registers"],
    fn="mul_sub",
    params=[["a", "int"], ["b", "int"], ["c", "int"]],
    returns="int",
    statement="""Return `a * b - c`.

**On entry:** `x0 = a`, `x1 = b`, `x2 = c`.
**On exit:** `x0 = a * b - c`.

The starter computes the product into the scratch register `x8` and then subtracts.
Fill in the multiplication.""",
    constraints=["−10⁶ ≤ a, b ≤ 10⁶", "−10¹² ≤ c ≤ 10¹²"],
    hints=[
        "There is a `mul` instruction with the same three-operand shape as `add`.",
        "The next line expects the product in `x8`.",
        "`mul x8, x0, x1`",
    ],
    solution='''def mul_sub(a, b, c):
    # Two steps, mirroring the assembly: product into a scratch value,
    # then subtract c from it.
    product = a * b
    return product - c
''',
    asm_solution="""// long long mul_sub(long long a, long long b, long long c)
// On entry: x0 = a, x1 = b, x2 = c       On exit: x0 = a*b - c
.text                          // code section
.globl _mul_sub                // export the symbol
.p2align 2                     // 4-byte alignment
_mul_sub:                      // function entry
    mul x8, x0, x1             // x8 = a * b (x8 is a free scratch register)
    sub x0, x8, x2             // x0 = product - c  (sub dst, minuend, subtrahend)
    ret                        // return x0
""",
    tests=[[6, 7, 2], [0, 5, 3], [-4, 3, -12], [1000000, 1000000, 1], [-1000000, 999999, -10**12], [1, 1, 1], [12, -12, 0]],
    explanation="""## Intuition

Break the formula into one instruction per operation, using a scratch register to hold
the intermediate value. AAPCS64 says `x8`–`x17` (and any argument register you no
longer need) are yours to trash without saving.

## Approach

Trace for `a = 6, b = 7, c = 2`:

| step | instruction | x0 | x1 | x2 | x8 |
|---|---|---|---|---|---|
| entry | | 6 | 7 | 2 | ? |
| 1 | `mul x8, x0, x1` | 6 | 7 | 2 | 42 |
| 2 | `sub x0, x8, x2` | **40** | 7 | 2 | 42 |

* `mul Xd, Xn, Xm`: `Xd = Xn * Xm`, keeping the **low 64 bits** of the product. Like
  `add`, it is the same instruction for signed and unsigned values. Unlike `add`, it
  only accepts registers: `mul x0, x0, #3` does not exist.
* `sub Xd, Xn, Xm`: `Xd = Xn - Xm`. Order matters: the first source is the one you
  subtract *from*.

## Complexity

O(1).

## Common mistakes

* **`sub x0, x2, x8`** computes `c - a*b`, the negation of the answer.
* **Trying an immediate with `mul`**: `invalid operand for instruction`. Move the
  constant into a register first.
* **Overwriting an input you still need.** Writing `mul x2, x0, x1` destroys `c`
  before you subtract it. Choose a scratch register for intermediates.

## Going further

ARM fuses this pattern: `madd Xd, Xn, Xm, Xa` computes `Xa + Xn*Xm` and
`msub Xd, Xn, Xm, Xa` computes `Xa - Xn*Xm` in one instruction. `mul` itself is
actually an alias for `madd Xd, Xn, Xm, xzr`. Can you rewrite this function as
`mneg` + `add`, or as `msub` followed by `neg`?""",
    x86=dict(
        solution="""# long long mul_sub(long long a, long long b, long long c)
# On entry: rdi = a, rsi = b, rdx = c       On exit: rax = a*b - c
.text                          # code section
.globl _mul_sub                # export the symbol
.p2align 4                     # 16-byte alignment
_mul_sub:                      # function entry
    movq %rdi, %rax            # rax = a
    imulq %rsi, %rax           # rax = a * b (two-operand signed multiply, low 64 bits)
    subq %rdx, %rax            # rax = rax - c (sub src, dst computes dst - src)
    ret                        # return rax
""",
        todos=[("imulq %rsi, %rax", "multiply rax (a copy of a) by b"),
               ("subq %rdx, %rax", "subtract c from the product in rax")],
        notes="""**On entry:** `%rdi = a`, `%rsi = b`, `%rdx = c`. **On exit:** `%rax = a*b - c`.

Use the **two-operand** `imulq src, dst` (`dst *= src`). The one-operand `mulq`/`imulq`
form multiplies by `%rax` and writes a 128-bit result into `%rdx:%rax`, which would
destroy `c`. Careful with `sub`: `subq %rcx, %r8` computes `r8 = r8 - rcx`.""",
        hints=[
            "Work in `%rax`: it already holds `a`. Multiply first, then subtract.",
            "Two-operand `imul` multiplies the destination by the source. `sub src, dst` subtracts the *source* from the destination.",
            "`imulq %rsi, %rax` then `subq %rdx, %rax`",
        ],
        explanation="""## Intuition

Build the answer in place in `%rax`: copy `a`, multiply by `b`, subtract `c`.

## Approach

| step | instruction | rax | rsi | rdx |
|---|---|---|---|---|
| entry | | ? | 4 | 5 |
| 1 | `movq %rdi, %rax` (a = 3) | 3 | 4 | 5 |
| 2 | `imulq %rsi, %rax` | 12 | 4 | 5 |
| 3 | `subq %rdx, %rax` | **7** | 4 | 5 |

The low 64 bits of a product are the same for signed and unsigned operands, so the
two-operand `imulq` is the general-purpose multiply.

## Complexity

O(1).

## Common mistakes

* **`subq %rax, %rdx`** computes `c - a*b` and leaves it in `%rdx`.
* **One-operand `mulq %rsi`**: it overwrites `%rdx` (holding `c`) with the high half.
* **Clobbering an argument you still need** before you have used it.""",
    ),
), [("mul x8, x0, x1", "multiply a (x0) by b (x1) and store the product in the scratch register x8")])

# ---------------------------------------------------------------- 4. abs
_add(dict(
    id="asm-absolute-value",
    title="Absolute Value",
    difficulty=1,
    tags=["cmp", "cneg", "conditional"],
    fn="abs_value",
    params=[["x", "int"]],
    returns="int",
    statement="""Return `|x|`, without using a branch.

**On entry:** `x0 = x` (signed).
**On exit:** `x0 = |x|`.

The starter already compares `x0` with zero. Use a *conditional* instruction to
negate it only when it was negative.""",
    constraints=["−10¹⁵ ≤ x ≤ 10¹⁵"],
    hints=[
        "`cmp x0, #0` sets the flags as if computing `x0 - 0`. Which condition code means \"signed less than\"?",
        "`cneg Xd, Xn, cond` writes `-Xn` if the condition holds, otherwise `Xn`.",
        "`cneg x0, x0, lt`",
    ],
    solution='''def abs_value(x):
    # Compare with zero, then negate only when x is (signed) less than zero.
    if x < 0:
        x = -x
    return x
''',
    asm_solution="""// long long abs_value(long long x)
// On entry: x0 = x       On exit: x0 = |x|
.text                          // code section
.globl _abs_value              // export the symbol
.p2align 2                     // 4-byte alignment
_abs_value:                    // function entry
    cmp x0, #0                 // set flags from x0 - 0 (N = sign bit of x)
    cneg x0, x0, lt            // if signed-less-than: x0 = -x0, otherwise x0 = x0
    ret                        // return |x|
""",
    tests=[[-5], [3], [0], [-1], [10**15], [-10**15], [-123456789]],
    explanation="""## Intuition

"Do something only if a condition holds" is usually a branch, but ARM has a family of
**conditional select** instructions that avoid jumping entirely: `csel`, `csinc`,
`csinv`, `csneg` and their aliases `cset`, `cinc`, `cneg`. They read the flags set by a
previous `cmp` and pick one of two results.

## Approach

| x | `cmp x0, #0` flags | `lt` (N≠V)? | after `cneg` |
|---|---|---|---|
| −5 | N=1, Z=0, V=0 | yes | 5 |
| 3 | N=0, Z=0, V=0 | no | 3 |
| 0 | N=0, Z=1, V=0 | no | 0 |

* `cmp Xn, #imm`: an alias for `subs xzr, Xn, #imm`. It subtracts, discards the result
  into the zero register, and keeps only the flags.
* `cneg Xd, Xn, cond`: `Xd = cond ? -Xn : Xn`. It is an alias for
  `csneg Xd, Xn, Xn, invert(cond)`, which is why disassemblers may show it differently.
* `lt` means **signed** less than: true when N ≠ V. The V (overflow) part makes it
  correct even when the subtraction overflows.

## Complexity

O(1), and branch-free: no misprediction is possible.

## Common mistakes

* **Using `lo` (unsigned lower)**: no unsigned value is below 0, so nothing is ever
  negated and `-5` comes back as `-5`.
* **Using `mi` vs `lt`**: `mi` (N set) works for comparing with 0, but `lt` expresses
  the intent and stays correct for general comparisons where overflow is possible.
* **Forgetting the `cmp`**: `cneg` reads whatever flags happen to be set, which in this
  function are left over from the caller.
* **INT64_MIN**: `-(-2⁶³)` overflows back to itself in two's complement; C's `llabs`
  has the same undefined behaviour. Our tests stay well inside the range.

## Going further

A classic branch-free trick without conditional instructions:
`asr x1, x0, #63` (all ones if negative, else zero), then `eor x0, x0, x1` and
`sub x0, x0, x1`. Trace it for `x = -5`.""",
    x86=dict(
        solution="""# long long abs_value(long long x)
# On entry: rdi = x       On exit: rax = |x|
.text                          # code section
.globl _abs_value              # export the symbol
.p2align 4                     # 16-byte alignment
_abs_value:                    # function entry
    movq %rdi, %rax            # rax = x (the answer if x >= 0)
    movq %rdi, %rcx            # rcx = x
    negq %rcx                  # rcx = -x (the answer if x < 0)
    cmpq $0, %rdi              # set flags from x - 0
    cmovlq %rcx, %rax          # if signed-less-than: rax = -x, otherwise keep x
    ret                        # return |x|
""",
        todos=[("cmovlq %rcx, %rax", "if the comparison said x < 0 (signed), replace rax with the negated copy in rcx")],
        notes="""**On entry:** `%rdi = x`. **On exit:** `%rax = |x|`.

x86 has no conditional negate, but it has **conditional move**: `cmovCCq src, dst`
copies `src` into `dst` only if condition `CC` holds (`e`, `ne`, `l`, `le`, `g`, `ge`
for signed; `b`, `be`, `a`, `ae` for unsigned). Prepare both candidates, compare,
then pick. Example: `cmovgq %r8, %r9` copies r8 into r9 if the last compare said
"greater".""",
        hints=[
            "Both candidates are ready: `x` in `%rax`, `-x` in `%rcx`. You only need to pick.",
            "A conditional move copies only when its condition holds; signed less-than is `l`.",
            "`cmovlq %rcx, %rax`",
        ],
        explanation="""## Intuition

Compute both possible answers, then let a branch-free conditional move keep the right
one: no jumps, so no branch misprediction.

## Approach

| step | instruction | rax | rcx | flags |
|---|---|---|---|---|
| entry (x = −5) | | ? | ? | |
| 1 | `movq %rdi, %rax` | −5 | | |
| 2 | `movq %rdi, %rcx` | −5 | −5 | |
| 3 | `negq %rcx` | −5 | 5 | |
| 4 | `cmpq $0, %rdi` | −5 | 5 | less (signed) |
| 5 | `cmovlq %rcx, %rax` | **5** | 5 | |

The compare comes *after* `negq` because `neg` also writes the flags.

## Complexity

O(1).

## Common mistakes

* **Comparing first, negating after**: `negq` overwrites the flags the `cmov` needs.
* **Unsigned condition** (`cmovbq`): no value is "below" 0 unsigned, so negatives stay negative.
* **`cmov` with an immediate**: `cmovlq $0, %rax` is not encodable; the source must be
  a register or memory.""",
    ),
), [("cneg x0, x0, lt", "if the comparison said x0 < 0 (signed), replace x0 with -x0; otherwise keep it")])

# ---------------------------------------------------------------- 5. max
_add(dict(
    id="asm-max-of-two",
    title="Max of Two",
    difficulty=1,
    tags=["cmp", "csel", "signed"],
    fn="max_of_two",
    params=[["a", "int"], ["b", "int"]],
    returns="int",
    statement="""Return the larger of two **signed** integers, without branching.

**On entry:** `x0 = a`, `x1 = b`.
**On exit:** `x0 = max(a, b)`.""",
    constraints=["−10¹⁵ ≤ a, b ≤ 10¹⁵"],
    hints=[
        "Compare first: `cmp x0, x1` sets the flags from `a - b`.",
        "`csel Xd, Xn, Xm, cond` picks `Xn` when the condition holds, else `Xm`.",
        "Signed greater-than is `gt` (unsigned would be `hi`): `csel x0, x0, x1, gt`.",
    ],
    solution='''def max_of_two(a, b):
    # Signed comparison: -2 is smaller than 9 even though its bit pattern
    # (0xFFFF...FFFE) is a huge unsigned number.
    return a if a > b else b
''',
    asm_solution="""// long long max_of_two(long long a, long long b)
// On entry: x0 = a, x1 = b       On exit: x0 = max(a, b)
.text                          // code section
.globl _max_of_two             // export the symbol
.p2align 2                     // 4-byte alignment
_max_of_two:                   // function entry
    cmp x0, x1                 // flags from a - b
    csel x0, x0, x1, gt        // x0 = (a > b, signed) ? a : b
    ret                        // return the larger value
""",
    tests=[[-2, 9], [9, -2], [5, 5], [-10, -3], [0, -1], [10**15, -10**15], [-10**15, -10**15 + 1]],
    explanation="""## Intuition

`max` is a comparison followed by a choice, and `csel` is a choice in one instruction.
The only real decision is which **condition code**: the inputs are signed.

## Approach

| a | b | `cmp x0, x1` (a − b) | `gt`? | x0 after `csel` |
|---|---|---|---|---|
| −2 | 9 | −11 → N=1, V=0 | no | 9 |
| 9 | −2 | 11 → N=0, Z=0 | yes | 9 |
| 5 | 5 | 0 → Z=1 | no | 5 (either is fine) |

* `cmp x0, x1` subtracts and sets N, Z, C, V.
* `csel Xd, Xn, Xm, cond`: `Xd = cond ? Xn : Xm`. No branch, so there is nothing to
  mispredict.
* `gt` = Z clear **and** N = V: signed strictly greater.

## Complexity

O(1).

## Common mistakes

* **`hi` instead of `gt`.** `hi` treats both values as unsigned. `-2` is
  `0xFFFFFFFFFFFFFFFE`, the largest unsigned value around, so `max(-2, 9)` returns `-2`.
  The first test exists to catch exactly this.
* **Reversed operands.** `csel x0, x1, x0, gt` returns the *minimum*.
* **`cmp x1, x0` with `gt`**: also flips the meaning. Read `cmp a, b` + `gt` as
  "a > b".

## Going further

`min` is the same with `lt`. Clamp `x` to `[lo, hi]` with two `cmp`/`csel` pairs.
Newer cores (ARMv8.9 / FEAT_CSSC) even add `smax`/`smin` instructions, but Apple's
toolchain targets older baselines by default.""",
    x86=dict(
        solution="""# long long max_of_two(long long a, long long b)
# On entry: rdi = a, rsi = b       On exit: rax = max(a, b)
.text                          # code section
.globl _max_of_two             # export the symbol
.p2align 4                     # 16-byte alignment
_max_of_two:                   # function entry
    movq %rdi, %rax            # rax = a (assume a is the larger)
    cmpq %rsi, %rdi            # flags from a - b (AT&T cmp src, dst computes dst - src)
    cmovleq %rsi, %rax         # if a <= b (signed): rax = b
    ret                        # return the larger value
""",
        todos=[("cmovleq %rsi, %rax", "if a is not greater than b (signed), replace rax with b")],
        notes="""**On entry:** `%rdi = a`, `%rsi = b`. **On exit:** `%rax = max(a, b)`.

AT&T `cmpq src, dst` sets the flags from **`dst - src`**, so the condition reads
"dst *cond* src": after `cmpq %r8, %r9`, `l` means r9 < r8. Pair it with a
conditional move (`cmovCCq src, dst`) to pick a value without a jump.""",
        hints=[
            "`%rax` starts as `a`. When should it be replaced by `b`?",
            "After the compare, the condition is about `a` relative to `b`. Use a signed condition (`l`, `le`, `g`, `ge`).",
            "`cmovleq %rsi, %rax`",
        ],
        explanation="""## Intuition

Assume `a` wins, then overwrite it with `b` in the cases where it does not.

## Approach

| step | instruction | rax | flags |
|---|---|---|---|
| entry (a = 3, b = 9) | | | |
| 1 | `movq %rdi, %rax` | 3 | |
| 2 | `cmpq %rsi, %rdi` | 3 | 3 − 9 < 0: `l`, `le` true |
| 3 | `cmovleq %rsi, %rax` | **9** | |

When `a == b` it does not matter which one is kept: both are the answer.

## Complexity

O(1).

## Common mistakes

* **Reading `cmp` in Intel order.** `cmpq %rsi, %rdi` compares `a` to `b` (a − b), not b to a.
* **Unsigned conditions** (`cmovbeq`): −1 then looks larger than everything.""",
    ),
), [("csel x0, x0, x1, gt", "select a if it is greater (signed) than b, otherwise b, into x0")])

# ---------------------------------------------------------------- 6. is_even
_add(dict(
    id="asm-is-even",
    title="Is It Even?",
    difficulty=1,
    tags=["tst", "cset", "bits"],
    fn="is_even",
    params=[["n", "int"]],
    returns="bool",
    statement="""Return `true` (1) if `n` is even, `false` (0) otherwise. `n` may be negative.

**On entry:** `x0 = n`.
**On exit:** `x0 = 1` if even, `0` if odd.

The starter tests the lowest bit. Turn the flags into a 0/1 result.""",
    constraints=["−10¹⁵ ≤ n ≤ 10¹⁵"],
    hints=[
        "An integer is even exactly when its lowest bit is 0, for negative numbers too (two's complement).",
        "`tst x0, #1` computes `x0 & 1` and sets Z when the result is zero.",
        "`cset Xd, cond` writes 1 if the condition holds, else 0. Which condition means \"Z is set\"? `cset x0, eq`.",
    ],
    solution='''def is_even(n):
    # Bit 0 is the 1s place. In two's complement this is true for negatives
    # too: -3 = ...11101 (odd), -4 = ...11100 (even).
    return n & 1 == 0
''',
    asm_solution="""// bool is_even(long long n)  (returned as 0/1 in x0)
// On entry: x0 = n       On exit: x0 = 1 if n is even, else 0
.text                          // code section
.globl _is_even                // export the symbol
.p2align 2                     // 4-byte alignment
_is_even:                      // function entry
    tst x0, #1                 // flags from n & 1; Z = 1 when the low bit is 0
    cset x0, eq                // x0 = Z ? 1 : 0
    ret                        // return the boolean
""",
    tests=[[6], [7], [0], [-3], [-4], [10**15], [10**15 + 1]],
    explanation="""## Intuition

Parity lives in bit 0. Rather than dividing, mask that bit and turn "was it zero?"
into a number. `tst` + `cset` is the idiomatic pair for "compute a boolean".

## Approach

| n | binary (low bits) | `n & 1` | Z | `cset x0, eq` |
|---|---|---|---|---|
| 6 | …0110 | 0 | 1 | **1** |
| 7 | …0111 | 1 | 0 | **0** |
| −3 | …1101 | 1 | 0 | **0** |
| −4 | …1100 | 0 | 1 | **1** |

* `tst Xn, #imm`: alias for `ands xzr, Xn, #imm`. It ANDs, discards the result, and
  sets N and Z (C and V are cleared). `#1` is a valid *logical immediate*; these are
  repeating bit patterns, so values like `#0xFF` work but `#0x104111` do not.
* `cset Xd, cond`: `Xd = cond ? 1 : 0`, an alias for `csinc Xd, xzr, xzr, invert(cond)`.
* `eq` means Z = 1, "the last result was zero".

## Complexity

O(1).

## Common mistakes

* **`cset x0, ne`** returns `is_odd`.
* **Returning `n & 1` directly** (`and x0, x0, #1`): that is 1 for *odd*. You would need
  `eor x0, x0, #1` afterwards.
* **Dividing**: `sdiv` + `msub` works, but it is ~10× slower and signed division rounds
  toward zero, so a "remainder" of −1 for negative odd numbers trips up `cmp x?, #1`.

## Going further

`tst` with other masks answers other questions: `tst x0, #7` + `cset eq` tests divisibility
by 8. Branch on a single bit with no flags at all: `tbz x0, #0, label` jumps if bit 0
is zero (`tbnz` if it is one).""",
    x86=dict(
        solution="""# bool is_even(long long n)  (returned as 0/1 in rax)
# On entry: rdi = n       On exit: rax = 1 if n is even, else 0
.text                          # code section
.globl _is_even                # export the symbol
.p2align 4                     # 16-byte alignment
_is_even:                      # function entry
    testq $1, %rdi             # flags from n & 1; ZF = 1 when the low bit is 0
    sete %al                   # al (low byte of rax) = ZF ? 1 : 0
    movzbq %al, %rax           # zero-extend the byte to all 64 bits of rax
    ret                        # return the boolean
""",
        todos=[("sete %al", "set the low byte of rax to 1 if the tested bit was zero (ZF set), otherwise 0")],
        notes="""**On entry:** `%rdi = n`. **On exit:** `%rax = 1` if `n` is even, else `0`.

`setCC` writes **one byte**: 1 if the condition holds, else 0. Its operand must be an
8-bit register such as `%al` (low byte of `%rax`), `%cl`, `%dl`, `%r8b`. The upper bytes
are left untouched, so widen it afterwards with `movzbq` (zero-extend byte to quad).
`test` is `and` that only sets flags.""",
        hints=[
            "After `test`, ZF is 1 exactly when the low bit of `n` was 0, which is when `n` is even.",
            "Use `setCC` with the 'equal / zero' condition on the low byte of `%rax`.",
            "`sete %al`",
        ],
        explanation="""## Intuition

`n` is even iff bit 0 is 0. `test` computes `n & 1` for the flags only, and `sete`
turns "ZF is set" into the byte 1.

## Approach

| step | instruction | rax | ZF |
|---|---|---|---|
| entry (n = 6) | | garbage | |
| 1 | `testq $1, %rdi` | garbage | 1 (6 & 1 = 0) |
| 2 | `sete %al` | garbage, low byte 1 | |
| 3 | `movzbq %al, %rax` | **1** | |

## Complexity

O(1).

## Common mistakes

* **Skipping the zero-extension.** `sete %al` leaves the other 56 bits of `%rax` as
  garbage; the harness reads all 64.
* **`sete %rax`**: `setCC` only takes 8-bit registers (`invalid operand for instruction`).
* **Clearing `%rax` with `xor` *between* `test` and `sete`**: `xor` rewrites the flags.
  (Clearing it *before* the `test` is the classic idiom.)""",
    ),
), [("cset x0, eq", "set x0 to 1 if the tested bit was zero (Z flag set), otherwise 0")])

# ---------------------------------------------------------------- 7. sum 1..n
_add(dict(
    id="asm-sum-to-n",
    title="Sum 1 to n",
    difficulty=1,
    tags=["loop", "cbz", "branch"],
    fn="sum_to_n",
    params=[["n", "int"]],
    returns="int",
    statement="""Return `1 + 2 + … + n` using a **loop** (not the closed formula). For `n = 0`
the sum is 0.

**On entry:** `x0 = n` (0 ≤ n).
**On exit:** `x0 = n(n+1)/2`.

The starter counts `x0` down to zero and keeps the running total in `x1`.""",
    constraints=["0 ≤ n ≤ 10⁶"],
    hints=[
        "Your first loop: a label, a test that jumps out, the body, and `b` back to the label.",
        "Inside the body, add the current `n` to the total before decrementing it.",
        "`add x1, x1, x0` in the body, and at the end `mov x0, x1` so the total is returned.",
    ],
    solution='''def sum_to_n(n):
    total = 0            # x1 in the assembly
    while n != 0:        # cbz x0, Ldone
        total += n       # add x1, x1, x0
        n -= 1           # sub x0, x0, #1
    return total         # mov x0, x1
''',
    asm_solution="""// long long sum_to_n(long long n)
// On entry: x0 = n       On exit: x0 = 1 + 2 + ... + n
.text                          // code section
.globl _sum_to_n               // export the symbol
.p2align 2                     // 4-byte alignment
_sum_to_n:                     // function entry
    mov x1, #0                 // x1 = total = 0
Lloop:                         // top of the loop (L-prefixed labels stay private)
    cbz x0, Ldone              // if n == 0, leave the loop
    add x1, x1, x0             // total += n
    sub x0, x0, #1             // n -= 1
    b Lloop                    // unconditional jump back to the test
Ldone:                         // loop exit
    mov x0, x1                 // return value must be in x0
    ret                        // return total
""",
    tests=[[3], [0], [1], [10], [100], [1000000], [54321]],
    explanation="""## Intuition

There are no `for` or `while` keywords. A loop is a **label** you can jump back to, a
**conditional branch** that leaves, and an unconditional `b` that repeats. Counting
*down* to zero is convenient because `cbz` (compare and branch if zero) tests a
register without a separate `cmp`.

## Approach

Trace for `n = 3`:

| iteration | x0 (n) at `cbz` | `add x1, x1, x0` → x1 | `sub` → x0 |
|---|---|---|---|
| 1 | 3 | 3 | 2 |
| 2 | 2 | 5 | 1 |
| 3 | 1 | 6 | 0 |
| exit | 0 → jump to `Ldone` | | |

Then `mov x0, x1` returns **6**.

* `cbz Xn, label`: branch if `Xn == 0`. It does not read or set flags.
* `b label`: always jump. The assembler computes the distance for you.
* `Lloop:` labels beginning with `L` are *assembler-local* on macOS: they do not become
  symbols in the object file, so they never clash with other functions.
* `sub x0, x0, #1` subtracts an immediate.

## Complexity

O(n) time, O(1) space: registers only, no memory at all.

## Common mistakes

* **Forgetting `mov x0, x1`** at the end returns the loop counter, which is 0.
* **Decrementing before adding** gives `0 + 1 + … + (n−1)`, off by `n`.
* **Testing at the bottom** (`do … while`) without checking `n = 0` first: the body runs
  once with `n = 0`, then `sub` makes it `−1` and the loop runs ~2⁶⁴ times: a timeout.
* **Using `w` registers**: the sum for `n = 10⁶` is 500000500000, more than 32 bits hold.

## Going further

Rewrite it with `subs x0, x0, #1` + `b.ne Lloop` at the bottom (one fewer branch per
iteration, once you guard `n = 0` at the top). Then compare with the closed form:
`madd`/`mul` + `lsr #1`, which is O(1).""",
    x86=dict(
        solution="""# long long sum_to_n(long long n)
# On entry: rdi = n       On exit: rax = 1 + 2 + ... + n
.text                          # code section
.globl _sum_to_n               # export the symbol
.p2align 4                     # 16-byte alignment
_sum_to_n:                     # function entry
    movq $0, %rax              # rax = total = 0 (accumulate directly in the return register)
Lloop:                         # top of the loop (L-prefixed labels stay private)
    testq %rdi, %rdi           # flags from n & n: ZF = 1 when n == 0
    jz Ldone                   # if n == 0, leave the loop
    addq %rdi, %rax            # total += n
    decq %rdi                  # n -= 1
    jmp Lloop                  # unconditional jump back to the test
Ldone:                         # loop exit
    ret                        # return total (already in rax)
""",
        todos=[("jz Ldone", "leave the loop when the test found n == 0"),
               ("addq %rdi, %rax", "add the current n into the running total")],
        notes="""**On entry:** `%rdi = n`. **On exit:** `%rax = 1 + 2 + … + n`.

There is no compare-and-branch-on-zero: test a register against itself
(`testq %r8, %r8` sets ZF when r8 is 0), then use a conditional jump (`jz`/`je`,
`jnz`/`jne`, …). `jmp` is the unconditional jump. Keeping the total in `%rax` from the
start saves a final move.""",
        hints=[
            "The `testq` sets ZF exactly when `n` is zero; the next line must act on that.",
            "`jz label` jumps if ZF is set. Then fold `n` into the total held in `%rax`.",
            "`jz Ldone` and `addq %rdi, %rax`",
        ],
        explanation="""## Intuition

Count `n` down to 0 and add each value to a running total that already lives in the
return register.

## Approach

| iteration | rdi (n) | rax (total) |
|---|---|---|
| entry | 3 | 0 |
| 1 | 3 → 2 | 3 |
| 2 | 2 → 1 | 5 |
| 3 | 1 → 0 | 6 |
| test: n == 0 → `ret` | 0 | **6** |

## Complexity

O(n) time, O(1) space.

## Common mistakes

* **Testing after decrementing** off by one: the loop must test before adding.
* **`jnz Ldone`**: exits immediately for any positive `n`.
* **Accumulating in `%rdi`** and forgetting that the caller reads `%rax`.""",
    ),
), [("add x1, x1, x0", "add the current n (x0) into the running total (x1)"),
    ("mov x0, x1", "move the total into the return register")])

# ---------------------------------------------------------------- 8. factorial
_add(dict(
    id="asm-factorial",
    title="Factorial (Iterative)",
    difficulty=1,
    tags=["loop", "mul", "b.cond"],
    fn="factorial",
    params=[["n", "int"]],
    returns="int",
    statement="""Return `n! = 1 · 2 · … · n`, with `0! = 1`.

**On entry:** `x0 = n`.
**On exit:** `x0 = n!`.

The starter loops while `n > 1`, multiplying an accumulator by `n` and decrementing.""",
    constraints=["0 ≤ n ≤ 18 (18! fits comfortably in 64 bits)"],
    hints=[
        "What must the accumulator start at so that `0!` and `1!` come out right?",
        "The loop body multiplies the accumulator by the current `n`. `mul` takes three registers.",
        "`mov x1, #1` before the loop; `mul x1, x1, x0` in the body.",
    ],
    solution='''def factorial(n):
    result = 1           # x1: the multiplicative identity, so 0! = 1! = 1
    while n > 1:         # cmp x0, #1 ; b.le Ldone
        result *= n      # mul x1, x1, x0
        n -= 1           # sub x0, x0, #1
    return result        # mov x0, x1
''',
    asm_solution="""// long long factorial(long long n)
// On entry: x0 = n       On exit: x0 = n!
.text                          // code section
.globl _factorial              // export the symbol
.p2align 2                     // 4-byte alignment
_factorial:                    // function entry
    mov x1, #1                 // x1 = result = 1
Lloop:                         // loop test
    cmp x0, #1                 // flags from n - 1
    b.le Ldone                 // signed n <= 1: nothing left to multiply
    mul x1, x1, x0             // result *= n
    sub x0, x0, #1             // n -= 1
    b Lloop                    // repeat
Ldone:                         // loop exit
    mov x0, x1                 // return result
    ret                        // back to the caller
""",
    tests=[[4], [0], [1], [5], [10], [18], [2]],
    explanation="""## Intuition

Same loop shape as summing, with two changes: the accumulator starts at **1** (the
identity for multiplication) and the exit test is `n <= 1`, which needs a real
comparison and a conditional branch.

## Approach

Trace for `n = 4`:

| iteration | x0 at `cmp` | `b.le` taken? | x1 after `mul` | x0 after `sub` |
|---|---|---|---|---|
| 1 | 4 | no | 4 | 3 |
| 2 | 3 | no | 12 | 2 |
| 3 | 2 | no | 24 | 1 |
| 4 | 1 | **yes** | | |

Return **24**. For `n = 0` the very first test jumps out and returns the initial 1.

* `cmp x0, #1` sets flags from `n - 1`.
* `b.le Ldone`: branch if signed less-or-equal (Z = 1 or N ≠ V).
* `mul x1, x1, x0`: low 64 bits of the product. 18! ≈ 6.4·10¹⁵ fits; 21! would not.

## Complexity

O(n) time, O(1) space.

## Common mistakes

* **Starting the accumulator at 0**: every product is 0.
* **Decrementing before multiplying** with a `cbz x0` exit: the final iteration
  multiplies by 0. Always ask what value `n` holds at the moment the body uses it.
* **`b.ls` vs `b.le`**: both work for non-negative `n`, but `ls` is the unsigned
  version. Get into the habit of matching the condition to the data's signedness.
* **Uninitialised registers**: if you skip `mov x1, #1`, `x1` holds whatever the caller
  left there (here, likely garbage from the harness).

## Going further

Overflow detection: `mul` silently keeps the low 64 bits. `smulh x2, x1, x0` gives the
high 64 bits of the signed 128-bit product; if it is not the sign-extension of the low
half, the multiplication overflowed. Make `factorial` return −1 for `n ≥ 21`.""",
    x86=dict(
        solution="""# long long factorial(long long n)
# On entry: rdi = n       On exit: rax = n!
.text                          # code section
.globl _factorial              # export the symbol
.p2align 4                     # 16-byte alignment
_factorial:                    # function entry
    movq $1, %rax              # rax = result = 1
Lloop:                         # loop test
    cmpq $1, %rdi              # flags from n - 1
    jle Ldone                  # signed n <= 1: nothing left to multiply
    imulq %rdi, %rax           # result *= n
    decq %rdi                  # n -= 1
    jmp Lloop                  # repeat
Ldone:                         # loop exit
    ret                        # return result (already in rax)
""",
        todos=[("movq $1, %rax", "initialise the accumulator rax to the multiplicative identity"),
               ("imulq %rdi, %rax", "multiply the accumulator rax by the current n")],
        notes="""**On entry:** `%rdi = n`. **On exit:** `%rax = n!`.

Use the two-operand signed multiply `imulq src, dst` (`dst *= src`); it keeps the low
64 bits and leaves `%rdx` alone. Accumulate straight in `%rax`.""",
        hints=[
            "A product must start at 1, not 0. Where should the product live so you can return it directly?",
            "`imulq` with two operands multiplies the destination by the source.",
            "`movq $1, %rax` and `imulq %rdi, %rax`",
        ],
        explanation="""## Intuition

`n! = n · (n−1) · … · 2`. Multiply into `%rax` while counting `n` down to 1.

## Approach

| iteration | rdi | rax |
|---|---|---|
| entry | 4 | 1 |
| 1 | 4 → 3 | 4 |
| 2 | 3 → 2 | 12 |
| 3 | 2 → 1 | 24 |
| `cmpq $1` → `jle` | 1 | **24** |

The `jle` (signed) also handles `n = 0`: 0 ≤ 1, so the result stays 1.

## Complexity

O(n) time, O(1) space.

## Common mistakes

* **Starting the product at 0** (everything multiplies to 0).
* **`jbe` instead of `jle`**: fine for these tests, but the signed condition matches the C type.
* **One-operand `mulq %rdi`**: multiplies `%rax` but also clobbers `%rdx`.""",
    ),
), [("mov x1, #1", "initialise the accumulator x1 to the multiplicative identity"),
    ("mul x1, x1, x0", "multiply the accumulator x1 by the current n (x0)")])

# ---------------------------------------------------------------- 9. sum array
_add(dict(
    id="asm-sum-array",
    title="Sum of an Array",
    difficulty=1,
    tags=["array", "ldr", "post-index"],
    fn="sum_array",
    params=[["nums", "int[]"]],
    returns="int",
    statement="""Return the sum of the elements of `nums` (0 for an empty array).

**On entry:** `x0` = pointer to `nums[0]`, `x1` = number of elements. Each element is a
64-bit signed integer (8 bytes), so `nums[i]` lives at address `x0 + 8·i`.
**On exit:** `x0` = the sum.""",
    constraints=["0 ≤ len(nums) ≤ 1000", "−10⁹ ≤ nums[i] ≤ 10⁹"],
    hints=[
        "Memory has to be loaded into a register before you can add it: `ldr`.",
        "Post-indexed addressing `ldr x3, [x0], #8` loads from `x0` and then advances `x0` by 8 bytes, ready for the next element.",
        "`ldr x3, [x0], #8` then `add x2, x2, x3`.",
    ],
    solution='''def sum_array(nums):
    total = 0            # x2
    i = 0                # in assembly the pointer x0 itself walks the array
    count = len(nums)    # x1 counts down to zero
    while count != 0:
        total += nums[i] # ldr x3, [x0], #8 ; add x2, x2, x3
        i += 1
        count -= 1
    return total
''',
    asm_solution="""// long long sum_array(long long* nums, long long count)
// On entry: x0 = &nums[0], x1 = count       On exit: x0 = sum
.text                          // code section
.globl _sum_array              // export the symbol
.p2align 2                     // 4-byte alignment
_sum_array:                    // function entry
    mov x2, #0                 // x2 = total = 0
Lloop:                         // loop test
    cbz x1, Ldone              // no elements left: finish
    ldr x3, [x0], #8           // x3 = *x0, then x0 += 8 (next element)
    add x2, x2, x3             // total += element
    sub x1, x1, #1             // one fewer element to go
    b Lloop                    // repeat
Ldone:                         // loop exit
    mov x0, x2                 // return the total
    ret                        // back to the caller
""",
    tests=[[[5, -2, 7]], [[]], [[42]], [[-1, -2, -3, -4]], [[10**9] * 1000],
           [[_R.randint(-10**9, 10**9) for _ in range(200)]], [[0, 0, 0, 1]]],
    explanation="""## Intuition

This is the first problem that reads **memory**. The array is not in registers; you get
its address and length. Arithmetic only works on registers, so each element must be
loaded with `ldr` first. The cleanest walk uses the pointer itself as the cursor.

## Approach

Trace for `nums = [5, -2, 7]` at (say) address `A`:

| iteration | x0 before | x1 | `ldr x3, [x0], #8` → x3 | x0 after | x2 after `add` |
|---|---|---|---|---|---|
| 1 | A | 3 | 5 | A+8 | 5 |
| 2 | A+8 | 2 | −2 | A+16 | 3 |
| 3 | A+16 | 1 | 7 | A+24 | 10 |
| exit | | 0 | | | |

Return **10**.

* `ldr Xt, [Xn], #imm` is **post-indexed**: load 8 bytes from address `Xn`, then add
  `imm` to `Xn`. Compare with `[Xn, #imm]` (offset, `Xn` unchanged) and `[Xn, #imm]!`
  (pre-indexed: add first, then load).
* The step is **8**, not 1: addresses count bytes and every `long long` is 8 bytes wide.
* `x` destination means a 64-bit load; `ldr w3, ...` would load only 4 bytes.

## Complexity

O(n) time, O(1) extra space.

## Common mistakes

* **`#1` instead of `#8`**: you read overlapping, misaligned garbage.
* **Loading before checking the count**: with an empty array you would dereference a
  pointer that has no element behind it (here it happens to be harmless, in general it
  segfaults).
* **`ldr x3, [x0]` without advancing**: you add `nums[0]` n times.
* **Losing the count**: if you decrement `x0` instead of `x1`, the pointer goes
  backwards and the loop never ends.

## Going further

Load two elements per iteration with `ldp x3, x4, [x0], #16` (handle an odd leftover),
or use indexed addressing `ldr x3, [x0, x4, lsl #3]` with an index register `x4`. Which
generates fewer instructions per element?""",
    x86=dict(
        solution="""# long long sum_array(long long* nums, long long count)
# On entry: rdi = &nums[0], rsi = count       On exit: rax = sum
.text                          # code section
.globl _sum_array              # export the symbol
.p2align 4                     # 16-byte alignment
_sum_array:                    # function entry
    movq $0, %rax              # rax = total = 0
Lloop:                         # loop test
    testq %rsi, %rsi           # any elements left?
    jz Ldone                   # no: finish
    addq (%rdi), %rax          # total += *ptr (x86 arithmetic can read memory directly)
    addq $8, %rdi              # ptr += 8: the next element
    decq %rsi                  # one fewer element to go
    jmp Lloop                  # repeat
Ldone:                         # loop exit
    ret                        # return the total
""",
        todos=[("addq (%rdi), %rax", "add the 8-byte element the pointer points at into the total"),
               ("addq $8, %rdi", "advance the pointer to the next 8-byte element")],
        notes="""**On entry:** `%rdi = &nums[0]`, `%rsi = count`. **On exit:** `%rax = sum`.

A memory operand is written `disp(base, index, scale)`: `(%r8)` is the 8 bytes at
address `r8`, `16(%r8)` is at `r8 + 16`. Unlike ARM, most x86 instructions can take
**one** memory operand directly, so no separate load is needed: `subq (%r9), %r10`
subtracts the value stored at `r9` from `r10`. There is no post-increment addressing;
advance the pointer yourself.""",
        hints=[
            "You do not need a separate load: an `add` can read its source straight from memory.",
            "Parentheses around a register mean 'the value at this address'. Elements are 8 bytes apart.",
            "`addq (%rdi), %rax` then `addq $8, %rdi`",
        ],
        explanation="""## Intuition

Walk a pointer through the array, adding each 8-byte element to the total, until the
count reaches zero.

## Approach

| iteration | rdi | rsi | rax |
|---|---|---|---|
| entry `[5, 1, 4]` | &nums[0] | 3 | 0 |
| 1 | &nums[1] | 2 | 5 |
| 2 | &nums[2] | 1 | 6 |
| 3 | one past the end | 0 | **10** |

`addq (%rdi), %rax` is a load and an add in one instruction.

## Complexity

O(n) time, O(1) space.

## Common mistakes

* **`addq %rdi, %rax`** (no parentheses) adds the *address*, not the element.
* **`incq %rdi`** advances by 1 byte, not 8: misaligned garbage reads.
* **Memory-to-memory**: `addq (%rdi), (%rax)` is not encodable; at most one operand
  may be in memory.""",
    ),
), [("ldr x3, [x0], #8", "load the current element into x3 and advance the pointer x0 to the next 8-byte element"),
    ("add x2, x2, x3", "add the loaded element into the running total x2")])

# ---------------------------------------------------------------- 10. strlen
_add(dict(
    id="asm-string-length",
    title="String Length",
    difficulty=1,
    tags=["string", "ldrb", "bytes"],
    fn="string_length",
    params=[["s", "str"]],
    returns="int",
    statement="""Return the number of characters in the NUL-terminated ASCII string `s` (like C's
`strlen`).

**On entry:** `x0` = pointer to the first byte of `s`. The string ends at the first byte
equal to 0.
**On exit:** `x0` = number of bytes before the terminating 0.""",
    constraints=["0 ≤ len(s) ≤ 1000", "`s` contains printable ASCII only"],
    hints=[
        "Characters are single bytes. `ldr` would load 8 of them at once.",
        "`ldrb w2, [x0, x1]` loads one byte from address `x0 + x1` into `w2`, zero-extended.",
        "Load `s[len]` with `ldrb w2, [x0, x1]`, stop when it is zero, otherwise `add x1, x1, #1`.",
    ],
    solution='''def string_length(s):
    # In C/assembly we cannot ask for the length: we scan until we hit the
    # terminating NUL byte. Python strings have no terminator, so we model it.
    data = s.encode() + b"\\0"
    n = 0                    # x1
    while data[n] != 0:      # ldrb w2, [x0, x1] ; cbz w2, Ldone
        n += 1               # add x1, x1, #1
    return n
''',
    asm_solution="""// long long string_length(const char* s)
// On entry: x0 = s       On exit: x0 = number of bytes before the NUL
.text                          // code section
.globl _string_length          // export the symbol
.p2align 2                     // 4-byte alignment
_string_length:                // function entry
    mov x1, #0                 // x1 = length so far = index of the byte to check
Lloop:                         // loop test
    ldrb w2, [x0, x1]          // w2 = byte at s + length (zero-extended)
    cbz w2, Ldone              // found the NUL terminator: stop
    add x1, x1, #1             // count this character
    b Lloop                    // check the next byte
Ldone:                         // loop exit
    mov x0, x1                 // return the length
    ret                        // back to the caller
""",
    tests=[["hi"], [""], ["a"], ["Hello, World!"], ["x" * 1000], ["   spaces   "], ["The quick brown fox"]],
    explanation="""## Intuition

A C string carries no length: it is bytes followed by a `0` byte (the NUL terminator).
The only way to find the length is to look at bytes one by one until the zero. Bytes
call for **byte** loads.

## Approach

Trace for `s = "hi"` (bytes `68 69 00` in hex):

| iteration | x1 | `ldrb w2, [x0, x1]` → w2 | `cbz` taken? | x1 after `add` |
|---|---|---|---|---|
| 1 | 0 | 0x68 'h' | no | 1 |
| 2 | 1 | 0x69 'i' | no | 2 |
| 3 | 2 | 0x00 | **yes** | |

Return **2**.

* `ldrb Wt, [Xn, Xm]`: load **one byte** from `Xn + Xm` and zero-extend it into the
  32-bit `Wt` (which also clears the top half of `Xt`). The destination must be a `w`
  register: `ldrb x2, ...` is an error.
* Register-offset addressing `[x0, x1]` adds the two registers; the index needs no
  scaling because each element is one byte.
* `cbz w2, Ldone` works on 32-bit registers too.

## Complexity

O(n) time, O(1) space.

## Common mistakes

* **`ldr` instead of `ldrb`**: `ldr x2` loads 8 bytes, so `w2` is zero only if eight
  consecutive bytes are zero. You overrun the string and return a wrong length (or
  segfault).
* **`ldrsb`** sign-extends; harmless for ASCII, but wrong habits for byte values ≥ 128.
* **Returning `x1 + 1`**: the terminator is not part of the length.
* **Incrementing `x0` and also indexing with `x1`**: you skip every other byte.

## Going further

Pointer version: keep the start in `x0`, walk `x1` with `ldrb w2, [x1], #1`, and return
`x1 - x0 - 1`. Real `strlen` implementations compare 16 bytes at a time with NEON
(`cmeq` + `umaxv`), which is why they are so fast.""",
    x86=dict(
        solution="""# long long string_length(const char* s)
# On entry: rdi = s       On exit: rax = number of bytes before the NUL
.text                          # code section
.globl _string_length          # export the symbol
.p2align 4                     # 16-byte alignment
_string_length:                # function entry
    movq $0, %rax              # rax = length so far = index of the byte to check
Lloop:                         # loop test
    movzbq (%rdi,%rax), %rcx   # rcx = byte at s + length, zero-extended to 64 bits
    testq %rcx, %rcx           # is it the NUL terminator?
    jz Ldone                   # yes: stop
    incq %rax                  # count this character
    jmp Lloop                  # check the next byte
Ldone:                         # loop exit
    ret                        # return the length
""",
        todos=[("movzbq (%rdi,%rax), %rcx", "load the single byte at address s + length into rcx, zero-extended"),
               ("incq %rax", "increment the length counter")],
        notes="""**On entry:** `%rdi = s`. **On exit:** `%rax = length`.

Characters are bytes. `movzbq` loads **one byte** and zero-extends it to 64 bits (`movq`
would load 8 bytes). The address form `(base,index)` means `base + index`:
`movzbq (%r8,%r9), %r10` loads the byte at `r8 + r9` into `r10`.""",
        hints=[
            "Use `%rax` as both the counter and the index: the byte to check lives at `s + rax`.",
            "Load with zero-extension from a byte (`movzb…`) and the base+index address form.",
            "`movzbq (%rdi,%rax), %rcx` and `incq %rax`",
        ],
        explanation="""## Intuition

Count bytes until the 0 byte. The count doubles as the index of the next byte.

## Approach

| iteration | rax | byte at s+rax |
|---|---|---|
| "hi" | 0 | 'h' |
| | 1 | 'i' |
| | 2 | 0 → exit, return **2** |

## Complexity

O(n) time, O(1) space.

## Common mistakes

* **`movq (%rdi,%rax), %rcx`** loads 8 bytes: it only finds a zero when eight bytes in
  a row are zero, and may read past the string.
* **`movb` into `%cl` then testing `%rcx`**: the upper bytes of `%rcx` are stale garbage.
  Zero-extend, or test only `%cl`.""",
    ),
), [("ldrb w2, [x0, x1]", "load the single byte at address s + length into w2"),
    ("add x1, x1, #1", "increment the length counter")])

# ---------------------------------------------------------------- 11. count value
_add(dict(
    id="asm-count-value",
    title="Count Occurrences",
    difficulty=2,
    tags=["array", "cmp", "cinc"],
    fn="count_value",
    params=[["nums", "int[]"], ["target", "int"]],
    returns="int",
    statement="""Return how many elements of `nums` equal `target`.

**On entry:** `x0` = pointer to `nums[0]`, `x1` = number of elements, `x2 = target`.
**On exit:** `x0` = the count.

Notice that the array takes **two** registers, so `target`, the second parameter, is
in `x2`, not `x1`. Do it without a branch inside the loop body.""",
    constraints=["0 ≤ len(nums) ≤ 1000", "−10⁹ ≤ nums[i], target ≤ 10⁹"],
    hints=[
        "Load each element, compare it with `x2`.",
        "`cinc Xd, Xn, cond` writes `Xn + 1` when the condition holds, otherwise `Xn`. Perfect for counting.",
        "`cmp x4, x2` followed by `cinc x3, x3, eq`.",
    ],
    solution='''def count_value(nums, target):
    count = 0                     # x3
    for x in nums:                # ldr x4, [x0], #8 walks the array
        # cmp x4, x2 ; cinc x3, x3, eq : add 1 exactly when equal, no branch
        count += 1 if x == target else 0
    return count
''',
    asm_solution="""// long long count_value(long long* nums, long long count, long long target)
// On entry: x0 = &nums[0], x1 = count, x2 = target       On exit: x0 = occurrences
.text                          // code section
.globl _count_value            // export the symbol
.p2align 2                     // 4-byte alignment
_count_value:                  // function entry
    mov x3, #0                 // x3 = matches found
Lloop:                         // loop test
    cbz x1, Ldone              // no elements left
    ldr x4, [x0], #8           // x4 = current element, advance pointer
    cmp x4, x2                 // flags from element - target
    cinc x3, x3, eq            // if equal: x3 += 1, else x3 unchanged
    sub x1, x1, #1             // one fewer element
    b Lloop                    // repeat
Ldone:                         // loop exit
    mov x0, x3                 // return the count
    ret                        // back to the caller
""",
    tests=[[[3, 1, 3], 3], [[], 5], [[1, 2, 3], 4], [[7, 7, 7, 7], 7], [[-1, 1, -1, 0], -1],
           [[_R.randint(0, 5) for _ in range(500)], 3], [[10**9, -10**9], -10**9]],
    explanation="""## Intuition

The loop is the array walk from *Sum of an Array*. What changes is the body: instead
of "add the element" it is "add 1 if the element matches". A branch around an `add`
works, but `cinc` does it in one branch-free instruction.

## Approach

Trace for `nums = [3, 1, 3]`, `target = 3`:

| iteration | x4 (loaded) | `cmp x4, x2` | eq? | x3 after `cinc` | x1 after |
|---|---|---|---|---|---|
| 1 | 3 | 0 → Z=1 | yes | 1 | 2 |
| 2 | 1 | −2 → Z=0 | no | 1 | 1 |
| 3 | 3 | 0 → Z=1 | yes | 2 | 0 |

Return **2**.

* `cmp x4, x2`: flags from `x4 - x2`; Z = 1 exactly when they are equal.
* `cinc Xd, Xn, cond`: `Xd = cond ? Xn + 1 : Xn`, an alias for `csinc Xd, Xn, Xn, invert(cond)`.
* Register usage: `x0`/`x1` are the array, `x2` is target, `x3`/`x4` are scratch. All
  caller-saved, so no saving needed.

## Complexity

O(n) time, O(1) space, and no data-dependent branches in the body.

## Common mistakes

* **Comparing with `x1`**: that is the array length, not the target. An `int[]`
  parameter occupies two registers, shifting every later parameter by one.
* **`cinc x3, x3, ne`** counts the elements that are *different*.
* **Forgetting the `cmp`**: then `cinc` reads flags from the previous iteration's
  comparison, or from nothing at all.
* **`cset x3, eq`** overwrites the count with 0/1 instead of incrementing it.

## Going further

With `ccmp` (conditional compare) you can count elements in a range `lo ≤ x ≤ hi` with
one `cmp`, one `ccmp` and one `cinc`: `cmp x4, x5; ccmp x4, x6, #2, ge; cinc x3, x3, ls`.
Work out why the `#nzcv` value `#2` makes the range test fail when the first test fails.""",
    x86=dict(
        solution="""# long long count_value(long long* nums, long long count, long long target)
# On entry: rdi = &nums[0], rsi = count, rdx = target       On exit: rax = occurrences
.text                          # code section
.globl _count_value            # export the symbol
.p2align 4                     # 16-byte alignment
_count_value:                  # function entry
    movq $0, %rax              # rax = matches found
Lloop:                         # loop test
    testq %rsi, %rsi           # elements left?
    jz Ldone                   # no
    movq (%rdi), %rcx          # rcx = current element
    addq $8, %rdi              # advance the pointer
    cmpq %rdx, %rcx            # flags from element - target
    sete %cl                   # cl = 1 if equal, else 0 (the element is no longer needed)
    movzbq %cl, %rcx           # zero-extend: rcx = 0 or 1
    addq %rcx, %rax            # matches += 0 or 1
    decq %rsi                  # one fewer element
    jmp Lloop                  # repeat
Ldone:                         # loop exit
    ret                        # return the count
""",
        todos=[("cmpq %rdx, %rcx", "compare the loaded element (rcx) with target (rdx)"),
               ("sete %cl", "set the low byte of rcx to 1 if they were equal, otherwise 0")],
        notes="""**On entry:** `%rdi = &nums[0]`, `%rsi = count`, `%rdx = target`.
**On exit:** `%rax = occurrences`.

x86 has no conditional increment; a branch-free equivalent is `setCC` (byte 0/1) +
`movzbq` + `add`. `setCC` needs an 8-bit register name: `%cl` is the low byte of `%rcx`,
`%r8b` the low byte of `%r8`.""",
        hints=[
            "First set the flags by comparing the element with `target`.",
            "Turn 'equal' into the byte 1 with a `setCC` on the low byte of `%rcx`; the next two lines add it.",
            "`cmpq %rdx, %rcx` then `sete %cl`",
        ],
        explanation="""## Intuition

For each element add 1 if it equals the target, else 0, without a branch.

## Approach

| element | target | `sete %cl` | rax |
|---|---|---|---|
| 2 | 2 | 1 | 1 |
| 7 | 2 | 0 | 1 |
| 2 | 2 | 1 | **2** |

## Complexity

O(n) time, O(1) space.

## Common mistakes

* **`sete %rcx`**: only 8-bit registers are allowed.
* **Adding without `movzbq`**: the upper bytes of `%rcx` still hold the element.
* **Putting `addq $8, %rdi` between `cmpq` and `sete`**: `add` overwrites the flags.""",
    ),
), [("cmp x4, x2", "compare the loaded element (x4) with target (x2)"),
    ("cinc x3, x3, eq", "increment the counter x3 only if the comparison found them equal")])

# ---------------------------------------------------------------- 12. max array
_add(dict(
    id="asm-max-array",
    title="Maximum of an Array",
    difficulty=2,
    tags=["array", "csel", "signed"],
    fn="max_array",
    params=[["nums", "int[]"]],
    returns="int",
    statement="""Return the largest element of a **non-empty** array of signed integers.

**On entry:** `x0` = pointer to `nums[0]`, `x1` = number of elements (at least 1).
**On exit:** `x0` = the maximum.""",
    constraints=["1 ≤ len(nums) ≤ 1000", "−10¹² ≤ nums[i] ≤ 10¹²"],
    hints=[
        "Seed the running best with the first element (not 0: every element might be negative).",
        "Each iteration: compare the new element with the best and keep the larger one, using `csel`.",
        "`ldr x2, [x0], #8` to seed; in the loop `cmp x3, x2` then `csel x2, x3, x2, gt`.",
    ],
    solution='''def max_array(nums):
    best = nums[0]           # x2: seed with a real element, never with 0
    for x in nums[1:]:       # x1 counts the remaining len-1 elements
        # cmp x3, x2 ; csel x2, x3, x2, gt  (signed greater-than)
        best = x if x > best else best
    return best
''',
    asm_solution="""// long long max_array(long long* nums, long long count)   (count >= 1)
// On entry: x0 = &nums[0], x1 = count       On exit: x0 = max element
.text                          // code section
.globl _max_array              // export the symbol
.p2align 2                     // 4-byte alignment
_max_array:                    // function entry
    ldr x2, [x0], #8           // x2 = best = nums[0]; x0 now points at nums[1]
    sub x1, x1, #1             // x1 = elements still to examine
Lloop:                         // loop test
    cbz x1, Ldone              // none left
    ldr x3, [x0], #8           // x3 = next element, advance pointer
    cmp x3, x2                 // flags from element - best
    csel x2, x3, x2, gt        // best = (element > best, signed) ? element : best
    sub x1, x1, #1             // one fewer element
    b Lloop                    // repeat
Ldone:                         // loop exit
    mov x0, x2                 // return best
    ret                        // back to the caller
""",
    tests=[[[4, -1, 9, 2]], [[-5]], [[-7, -3, -9]], [[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]],
           [[_R.randint(-10**12, 10**12) for _ in range(300)]], [[0, -1, 0]]],
    explanation="""## Intuition

Keep a running best and update it with `csel`. Two details make or break it: the seed
must be an actual element, and the comparison must be **signed**.

## Approach

Trace for `nums = [4, -1, 9, 2]`:

| step | x3 | `cmp x3, x2` | gt? | x2 (best) | x1 |
|---|---|---|---|---|---|
| seed | | | | 4 | 3 |
| 1 | −1 | −5 | no | 4 | 2 |
| 2 | 9 | 5 | yes | 9 | 1 |
| 3 | 2 | −7 | no | 9 | 0 |

Return **9**.

* `ldr x2, [x0], #8` seeds and advances in one instruction.
* `csel x2, x3, x2, gt`: keep the new element only when it is strictly greater.
* `gt` is signed (Z = 0 and N = V).

## Complexity

O(n) time, O(1) space.

## Common mistakes

* **Seeding with 0**: `[-7, -3, -9]` would return 0, which is not even in the array.
* **`hi` instead of `gt`**: negative numbers look enormous unsigned, so `[0, -1, 0]`
  returns −1.
* **Forgetting `sub x1, x1, #1` after seeding**: the loop then reads one element past
  the end of the array.
* **Swapped `csel` operands** (`csel x2, x2, x3, gt`) keeps the element when it is
  *smaller*, a minimum-ish mess.

## Going further

Return the *index* of the maximum instead: keep an index register and update it with a
second `csel` using the same flags (flags survive until the next flag-setting
instruction, so one `cmp` can drive several `csel`s).""",
    x86=dict(
        solution="""# long long max_array(long long* nums, long long count)   (count >= 1)
# On entry: rdi = &nums[0], rsi = count       On exit: rax = max element
.text                          # code section
.globl _max_array              # export the symbol
.p2align 4                     # 16-byte alignment
_max_array:                    # function entry
    movq (%rdi), %rax          # rax = best = nums[0]
    addq $8, %rdi              # rdi now points at nums[1]
    decq %rsi                  # rsi = elements still to examine
Lloop:                         # loop test
    testq %rsi, %rsi           # any left?
    jz Ldone                   # none left
    movq (%rdi), %rcx          # rcx = next element
    addq $8, %rdi              # advance the pointer
    cmpq %rax, %rcx            # flags from element - best
    cmovgq %rcx, %rax          # best = (element > best, signed) ? element : best
    decq %rsi                  # one fewer element
    jmp Lloop                  # repeat
Ldone:                         # loop exit
    ret                        # return best
""",
        todos=[("movq (%rdi), %rax", "seed the best value rax with nums[0]"),
               ("cmpq %rax, %rcx", "compare the new element rcx with the current best rax"),
               ("cmovgq %rcx, %rax", "keep the new element if it is greater (signed), otherwise keep the best")],
        notes="""**On entry:** `%rdi = &nums[0]`, `%rsi = count` (≥ 1). **On exit:** `%rax = max`.

Remember the AT&T compare order: `cmpq %r8, %r9` sets flags from `r9 - r8`, so a
following `g` condition means r9 > r8. `cmovgq` is the signed "greater" conditional move.""",
        hints=[
            "Start `best` from the first element (in the return register), not from 0: the array may be all negative.",
            "Compare element against best so that `g` means 'element > best', then conditionally move.",
            "`movq (%rdi), %rax`, `cmpq %rax, %rcx`, `cmovgq %rcx, %rax`",
        ],
        explanation="""## Intuition

Keep the best value so far in `%rax`; replace it whenever a larger element appears.

## Approach

| element | flags (element − best) | rax |
|---|---|---|
| seed −3 | | −3 |
| −7 | less | −3 |
| 4 | greater | 4 |
| 1 | less | **4** |

## Complexity

O(n) time, O(1) space.

## Common mistakes

* **Starting from 0** gives 0 for all-negative arrays.
* **`cmpq %rcx, %rax`** reverses the meaning of `g`: you would compute the minimum.
* **`cmovaq`** (unsigned "above"): negative numbers look huge.""",
    ),
), [("ldr x2, [x0], #8", "seed the best value x2 with nums[0] and advance x0 to the next element"),
    ("cmp x3, x2", "compare the new element x3 with the current best x2"),
    ("csel x2, x3, x2, gt", "keep the new element if it is greater (signed), otherwise keep the best")])

# ---------------------------------------------------------------- 13. popcount
_add(dict(
    id="asm-popcount",
    title="Count the Set Bits",
    difficulty=2,
    tags=["bits", "lsr", "and"],
    fn="popcount",
    params=[["n", "int"]],
    returns="int",
    statement="""Return the number of 1 bits in the binary representation of the non-negative
integer `n` (its *population count*). Use a loop that inspects one bit at a time.

**On entry:** `x0 = n` (n ≥ 0).
**On exit:** `x0` = number of set bits.""",
    constraints=["0 ≤ n < 2⁵³"],
    hints=[
        "Peel off the lowest bit, add it to the count, then shift `n` right by one. Stop when `n` becomes 0.",
        "`and x2, x0, #1` isolates the low bit (0 or 1).",
        "`and x2, x0, #1`, then `add x1, x1, x2`. The `lsr x0, x0, #1` is already there.",
    ],
    solution='''def popcount(n):
    count = 0            # x1
    while n != 0:        # cbz x0, Ldone: stop once every 1 bit has been shifted out
        count += n & 1   # and x2, x0, #1 ; add x1, x1, x2
        n >>= 1          # lsr x0, x0, #1 (logical: shifts in zeros)
    return count
''',
    asm_solution="""// long long popcount(long long n)   (n >= 0)
// On entry: x0 = n       On exit: x0 = number of 1 bits
.text                          // code section
.globl _popcount               // export the symbol
.p2align 2                     // 4-byte alignment
_popcount:                     // function entry
    mov x1, #0                 // x1 = bit count
Lloop:                         // loop test
    cbz x0, Ldone              // no 1 bits remain
    and x2, x0, #1             // x2 = lowest bit of n (0 or 1)
    add x1, x1, x2             // count += that bit
    lsr x0, x0, #1             // n >>= 1 (logical shift right, zero fill)
    b Lloop                    // repeat
Ldone:                         // loop exit
    mov x0, x1                 // return the count
    ret                        // back to the caller
""",
    tests=[[13], [0], [1], [255], [2**52], [2**53 - 1], [0b1010101010101], [123456789]],
    explanation="""## Intuition

`n & 1` tells you whether the lowest bit is set. Shifting right moves the next bit into
the lowest position. Repeat until `n` is zero: then there are no more 1 bits to find,
so the loop runs only as many times as the position of the highest set bit.

## Approach

Trace for `n = 13` (binary `1101`):

| iteration | x0 (binary) | `and x2, x0, #1` | x1 after `add` | x0 after `lsr` |
|---|---|---|---|---|
| 1 | 1101 | 1 | 1 | 110 |
| 2 | 110 | 0 | 1 | 11 |
| 3 | 11 | 1 | 2 | 1 |
| 4 | 1 | 1 | 3 | 0 |

Return **3**.

* `and Xd, Xn, #imm`: bitwise AND with a logical immediate.
* `lsr Xd, Xn, #s`: **logical** shift right, filling with zeros.
* `asr` would be the *arithmetic* shift right, copying the sign bit in.

## Complexity

O(log n): at most 53 iterations here, 64 in general.

## Common mistakes

* **`asr` instead of `lsr`**: for negative inputs the sign bit refills forever and the
  loop never terminates. Our inputs are non-negative, but `lsr` is the right instinct
  for bit manipulation.
* **`tst` + `cinc`** is a valid alternative (`tst x0, #1; cinc x1, x1, ne`). Writing
  `cinc x1, x1, eq` counts the zeros instead.
* **Shifting before reading the bit** skips bit 0.

## Going further

Kernighan's trick loops once per **set** bit: `sub x2, x0, #1; and x0, x0, x2` clears
the lowest 1 bit each time. And the hardware has a real popcount: move to a SIMD
register and use `cnt` + `addv`:

```asm
    fmov d0, x0          // copy the 64 bits into a vector register
    cnt v0.8b, v0.8b     // per-byte popcount
    addv b0, v0.8b       // sum the 8 bytes
    fmov w0, s0          // back to a general register
```""",
    x86=dict(
        solution="""# long long popcount(long long n)   (n >= 0)
# On entry: rdi = n       On exit: rax = number of 1 bits
.text                          # code section
.globl _popcount               # export the symbol
.p2align 4                     # 16-byte alignment
_popcount:                     # function entry
    movq $0, %rax              # rax = bit count
Lloop:                         # loop test
    testq %rdi, %rdi           # any 1 bits remaining?
    jz Ldone                   # no
    movq %rdi, %rcx            # rcx = n
    andq $1, %rcx              # rcx = lowest bit of n (0 or 1)
    addq %rcx, %rax            # count += that bit
    shrq $1, %rdi              # n >>= 1 (logical shift right, zero fill)
    jmp Lloop                  # repeat
Ldone:                         # loop exit
    ret                        # return the count
""",
        todos=[("andq $1, %rcx", "isolate the lowest bit of the copy in rcx"),
               ("addq %rcx, %rax", "add that bit (0 or 1) to the count")],
        notes="""**On entry:** `%rdi = n` (≥ 0). **On exit:** `%rax` = number of 1 bits.

Bitwise ops are two-operand too: `andq $0xff, %r8` keeps only the low byte of r8.
Shifts: `shlq` (left), `shrq` (logical right, zero fill), `sarq` (arithmetic right, sign
fill). Because `and` is destructive, copy `n` first.""",
        hints=[
            "`%rcx` holds a copy of `n`. Mask it so only bit 0 survives.",
            "AND with the immediate 1, then add the result to the count in `%rax`.",
            "`andq $1, %rcx` and `addq %rcx, %rax`",
        ],
        explanation="""## Intuition

Peel off the lowest bit, add it to the count, shift right, repeat until nothing is left.

## Approach

| rdi (binary) | low bit | rax |
|---|---|---|
| 1011 | 1 | 1 |
| 101 | 1 | 2 |
| 10 | 0 | 2 |
| 1 | 1 | 3 |
| 0 → exit | | **3** |

## Complexity

O(number of bits) ≤ 64 iterations.

## Common mistakes

* **`andq $1, %rdi`** destroys `n`.
* **`sarq`** on negative input would loop forever (sign fill); `shrq` always terminates.

## Going further

CPUs with POPCNT do this in one instruction: `popcntq %rdi, %rax`.""",
    ),
), [("and x2, x0, #1", "isolate the lowest bit of n into x2"),
    ("add x1, x1, x2", "add that bit (0 or 1) to the count x1")])

# ---------------------------------------------------------------- 14. gcd
_add(dict(
    id="asm-gcd",
    title="Greatest Common Divisor",
    difficulty=2,
    tags=["udiv", "msub", "euclid"],
    fn="gcd",
    params=[["a", "int"], ["b", "int"]],
    returns="int",
    statement="""Return the greatest common divisor of two non-negative integers using Euclid's
algorithm: while `b ≠ 0`, replace `(a, b)` with `(b, a mod b)`. Define `gcd(a, 0) = a`
(so `gcd(0, 0) = 0`).

**On entry:** `x0 = a`, `x1 = b` (both ≥ 0).
**On exit:** `x0 = gcd(a, b)`.

ARM64 has no remainder instruction: compute it from a division and a multiply-subtract.""",
    constraints=["0 ≤ a, b ≤ 10¹⁵"],
    hints=[
        "`a mod b = a - (a / b) * b`.",
        "`udiv Xd, Xn, Xm` is unsigned division (truncating). `msub Xd, Xn, Xm, Xa` computes `Xa - Xn * Xm`.",
        "`udiv x2, x0, x1` then `msub x2, x2, x1, x0` leaves `a mod b` in `x2`.",
    ],
    solution='''def gcd(a, b):
    # Euclid: gcd(a, b) == gcd(b, a mod b), and gcd(a, 0) == a.
    while b != 0:            # cbz x1, Ldone
        q = a // b           # udiv x2, x0, x1
        r = a - q * b        # msub x2, x2, x1, x0  (the remainder)
        a, b = b, r          # mov x0, x1 ; mov x1, x2
    return a                 # already in x0
''',
    asm_solution="""// long long gcd(long long a, long long b)   (a, b >= 0)
// On entry: x0 = a, x1 = b       On exit: x0 = gcd(a, b)
.text                          // code section
.globl _gcd                    // export the symbol
.p2align 2                     // 4-byte alignment
_gcd:                          // function entry
Lloop:                         // loop test
    cbz x1, Ldone              // b == 0: the answer is a, already in x0
    udiv x2, x0, x1            // x2 = q = a / b (unsigned, rounds toward zero)
    msub x2, x2, x1, x0        // x2 = a - q * b = a mod b
    mov x0, x1                 // a = b
    mov x1, x2                 // b = a mod b
    b Lloop                    // repeat
Ldone:                         // loop exit
    ret                        // return a (in x0)
""",
    tests=[[48, 18], [0, 0], [7, 0], [0, 9], [17, 5], [10**15, 10**15 - 1], [2**40, 2**30 * 3], [270, 192]],
    explanation="""## Intuition

Euclid's algorithm needs `a mod b`, and AArch64 deliberately has no remainder
instruction. The quotient comes from `udiv`; then `msub` (multiply-subtract) rebuilds
the remainder: `r = a − q·b`. This two-instruction pair is exactly what a C compiler
emits for `%`.

## Approach

Trace for `a = 48, b = 18`:

| iteration | x0 (a) | x1 (b) | `udiv` → q | `msub` → r | new a | new b |
|---|---|---|---|---|---|---|
| 1 | 48 | 18 | 2 | 12 | 18 | 12 |
| 2 | 18 | 12 | 1 | 6 | 12 | 6 |
| 3 | 12 | 6 | 2 | 0 | 6 | 0 |
| exit | 6 | 0 | | | | |

Return **6**.

* `udiv Xd, Xn, Xm`: unsigned `Xn / Xm`, rounded toward zero. **Division by zero does
  not trap** on ARM64: it returns 0. That is why the `cbz x1` test before the divide is
  about correctness, not a crash.
* `msub Xd, Xn, Xm, Xa`: `Xd = Xa − Xn·Xm`. Note the accumulator comes **last**.
* The two `mov`s perform the swap `(a, b) ← (b, r)`; order matters because `x0` must
  read the old `b` before `x1` is overwritten.

## Complexity

O(log min(a, b)) iterations: the remainder at least halves every two steps.

## Common mistakes

* **`msub x2, x0, x1, x2`**: argument order confusion; computes `q − a·b`.
* **Swapping the `mov`s** (`mov x1, x2` first) loses `b`.
* **`sdiv` vs `udiv`**: identical here since inputs are non-negative, but for negative
  numbers `sdiv` rounds toward zero, so remainders can be negative.
* **Testing the wrong register**: the loop must stop when **b** (`x1`) is zero.

## Going further

Binary GCD (Stein's algorithm) avoids division completely using `ctz` (count trailing
zeros, via `rbit` + `clz`), shifts and subtraction. It can be faster on cores where
`udiv` takes many cycles.""",
    x86=dict(
        solution="""# long long gcd(long long a, long long b)   (a, b >= 0)
# On entry: rdi = a, rsi = b       On exit: rax = gcd(a, b)
.text                          # code section
.globl _gcd                    # export the symbol
.p2align 4                     # 16-byte alignment
_gcd:                          # function entry
    movq %rdi, %rax            # rax = a
Lloop:                         # loop test
    testq %rsi, %rsi           # b == 0?
    jz Ldone                   # yes: the answer is a, already in rax
    xorl %edx, %edx            # rdx = 0: high half of the 128-bit dividend rdx:rax
    divq %rsi                  # rax = rdx:rax / b, rdx = rdx:rax mod b (unsigned)
    movq %rsi, %rax            # a = b
    movq %rdx, %rsi            # b = a mod b
    jmp Lloop                  # repeat
Ldone:                         # loop exit
    ret                        # return a
""",
        todos=[("xorl %edx, %edx", "clear the high half of the 128-bit dividend"),
               ("divq %rsi", "divide a by b (unsigned): quotient into rax, remainder into rdx")],
        notes="""**On entry:** `%rdi = a`, `%rsi = b`. **On exit:** `%rax = gcd(a, b)`.

x86 division is unusual: `divq src` divides the **128-bit** value `%rdx:%rax` by `src`,
leaving the quotient in `%rax` and the **remainder in `%rdx`** (so no multiply-subtract
is needed). Before an unsigned `divq`, `%rdx` must be 0; before a signed `idivq`,
sign-extend `%rax` into `%rdx` with `cqto`. Writing a 32-bit register (`%edx`) zeroes
the upper half of the 64-bit one.""",
        hints=[
            "The dividend is `%rdx:%rax`. `a` is already in `%rax`; what must `%rdx` be for an unsigned divide?",
            "Zero `%rdx` (xor a register with itself is the idiom), then use the one-operand unsigned divide by `b`.",
            "`xorl %edx, %edx` then `divq %rsi`",
        ],
        explanation="""## Intuition

Euclid: gcd(a, b) = gcd(b, a mod b), and gcd(a, 0) = a. x86's `div` hands you the
remainder directly.

## Approach

| rax (a) | rsi (b) | rdx after `divq` |
|---|---|---|
| 48 | 18 | 12 |
| 18 | 12 | 6 |
| 12 | 6 | 0 |
| 6 | 0 → exit | **6** |

## Complexity

O(log min(a, b)) iterations.

## Common mistakes

* **Forgetting to clear `%rdx`**: the dividend becomes `garbage·2⁶⁴ + a`; if the
  quotient does not fit in 64 bits the CPU raises a divide error (`SIGFPE`).
* **Dividing by zero**: also `SIGFPE`; the loop tests `b` first.
* **`cqto` + `idivq`** works too for non-negative inputs, but `div` matches the unsigned spec.""",
    ),
), [("udiv x2, x0, x1", "compute the quotient a / b (unsigned) into x2"),
    ("msub x2, x2, x1, x0", "turn the quotient into the remainder: x2 = a - q * b")])

# ---------------------------------------------------------------- 15. fibonacci
_add(dict(
    id="asm-fibonacci",
    title="Fibonacci (Iterative)",
    difficulty=2,
    tags=["loop", "registers"],
    fn="fibonacci",
    params=[["n", "int"]],
    returns="int",
    statement="""Return the `n`-th Fibonacci number, with `F(0) = 0`, `F(1) = 1`,
`F(n) = F(n−1) + F(n−2)`. Use a loop that keeps two consecutive values in registers.

**On entry:** `x0 = n`.
**On exit:** `x0 = F(n)`.""",
    constraints=["0 ≤ n ≤ 78 (F(78) < 2⁵³)"],
    hints=[
        "Keep `a = F(i)` in `x1` and `b = F(i+1)` in `x2`. One step turns them into `F(i+1), F(i+2)`.",
        "You cannot assign two registers at once: compute the new value into a temporary first.",
        "`add x3, x1, x2`, then `mov x1, x2`, then `mov x2, x3`.",
    ],
    solution='''def fibonacci(n):
    a, b = 0, 1          # x1 = F(0), x2 = F(1)
    while n != 0:        # cbz x0, Ldone
        t = a + b        # add x3, x1, x2
        a = b            # mov x1, x2
        b = t            # mov x2, x3
        n -= 1           # sub x0, x0, #1
    return a             # after n steps a == F(n)
''',
    asm_solution="""// long long fibonacci(long long n)
// On entry: x0 = n       On exit: x0 = F(n)
.text                          // code section
.globl _fibonacci              // export the symbol
.p2align 2                     // 4-byte alignment
_fibonacci:                    // function entry
    mov x1, #0                 // x1 = a = F(0)
    mov x2, #1                 // x2 = b = F(1)
Lloop:                         // loop test
    cbz x0, Ldone              // n steps done
    add x3, x1, x2             // t = a + b
    mov x1, x2                 // a = b
    mov x2, x3                 // b = t
    sub x0, x0, #1             // n -= 1
    b Lloop                    // repeat
Ldone:                         // loop exit
    mov x0, x1                 // return a = F(n)
    ret                        // back to the caller
""",
    tests=[[5], [0], [1], [2], [10], [50], [78]],
    explanation="""## Intuition

The Python one-liner `a, b = b, a + b` hides a temporary. In assembly every
instruction writes one register, so the "simultaneous" update becomes three moves through
a scratch register.

## Approach

Trace for `n = 5`:

| iteration | x0 at test | x3 = x1 + x2 | x1 | x2 |
|---|---|---|---|---|
| start | 5 | | 0 | 1 |
| 1 | 5 | 1 | 1 | 1 |
| 2 | 4 | 2 | 1 | 2 |
| 3 | 3 | 3 | 2 | 3 |
| 4 | 2 | 5 | 3 | 5 |
| 5 | 1 | 8 | 5 | 8 |
| exit | 0 | | **5** | |

Invariant: after `k` iterations `x1 = F(k)` and `x2 = F(k+1)`. After `n` iterations
`x1 = F(n)`.

* `add x3, x1, x2`: compute the next term without destroying either input.
* `mov x1, x2` / `mov x2, x3`: shift the window. `mov Xd, Xm` is really
  `orr Xd, xzr, Xm`.

## Complexity

O(n) time, O(1) space.

## Common mistakes

* **`add x1, x1, x2` then `mov x2, x1`**: after the first instruction the old `a` is
  gone, so both registers end up equal.
* **Returning `x2`** gives `F(n+1)`.
* **Off-by-one in the loop count**: the invariant table above is the quickest way to
  convince yourself how many iterations you need.

## Going further

Two-register trick with no temporary: `add x2, x2, x1` then `sub x1, x2, x1` (new b =
a + b, new a = new b − a). Or compute `F(n)` in O(log n) with the fast-doubling
identities `F(2k) = F(k)(2F(k+1) − F(k))`, `F(2k+1) = F(k)² + F(k+1)²`.""",
    x86=dict(
        solution="""# long long fibonacci(long long n)
# On entry: rdi = n       On exit: rax = F(n)
.text                          # code section
.globl _fibonacci              # export the symbol
.p2align 4                     # 16-byte alignment
_fibonacci:                    # function entry
    movq $0, %rax              # rax = a = F(0)
    movq $1, %rcx              # rcx = b = F(1)
Lloop:                         # loop test
    testq %rdi, %rdi           # n steps done?
    jz Ldone                   # yes
    leaq (%rax,%rcx), %rdx     # t = a + b (lea computes an address expression, no memory access)
    movq %rcx, %rax            # a = b
    movq %rdx, %rcx            # b = t
    decq %rdi                  # n -= 1
    jmp Lloop                  # repeat
Ldone:                         # loop exit
    ret                        # return a = F(n)
""",
        todos=[("leaq (%rax,%rcx), %rdx", "compute the next Fibonacci number a + b into the temporary rdx in one instruction"),
               ("movq %rcx, %rax", "slide the window: a becomes b"),
               ("movq %rdx, %rcx", "slide the window: b becomes the new value")],
        notes="""**On entry:** `%rdi = n`. **On exit:** `%rax = F(n)`.

Here `a` lives in `%rax`, `b` in `%rcx`, and the temporary in `%rdx`. `lea` ("load
effective address") evaluates a memory-operand expression **without** reading memory,
which makes it a handy three-operand add: `leaq (%r8,%r9), %r10` sets `r10 = r8 + r9`
(and `leaq 5(%r8), %r10` sets `r10 = r8 + 5`).""",
        hints=[
            "You need `a + b` in a third register without destroying `a` or `b`.",
            "`lea` with a base+index expression adds two registers into a third. Then shift the window in the right order.",
            "`leaq (%rax,%rcx), %rdx`, `movq %rcx, %rax`, `movq %rdx, %rcx`",
        ],
        explanation="""## Intuition

Keep a sliding window `(a, b) = (F(i), F(i+1))` and advance it `n` times.

## Approach

| iteration | rax (a) | rcx (b) | rdx (t) |
|---|---|---|---|
| entry n = 4 | 0 | 1 | |
| 1 | 1 | 1 | 1 |
| 2 | 1 | 2 | 2 |
| 3 | 2 | 3 | 3 |
| 4 | **3** | 5 | 5 |

## Complexity

O(n) time, O(1) space.

## Common mistakes

* **Updating `b` before `a`**: the old `b` is lost and the sequence doubles.
* **`movq (%rax,%rcx), %rdx`** *reads memory* at that address: a segfault. Only `lea`
  computes the address without loading.""",
    ),
), [("add x3, x1, x2", "compute the next Fibonacci number a + b into the temporary x3"),
    ("mov x1, x2", "slide the window: a becomes b"),
    ("mov x2, x3", "slide the window: b becomes the new value")])

# ---------------------------------------------------------------- 16. vowels
_add(dict(
    id="asm-count-vowels",
    title="Count Vowels",
    difficulty=2,
    tags=["string", "ldrb", "ascii"],
    fn="count_vowels",
    params=[["s", "str"]],
    returns="int",
    statement="""Return how many characters of the ASCII string `s` are vowels: `a e i o u`,
in either upper or lower case.

**On entry:** `x0` = pointer to a NUL-terminated string.
**On exit:** `x0` = number of vowels.

The starter compares the byte against each lowercase vowel. You need to load the byte
and fold upper case into lower case first.""",
    constraints=["0 ≤ len(s) ≤ 1000", "printable ASCII only"],
    hints=[
        "Load one byte per iteration and advance the pointer: post-indexed `ldrb`.",
        "In ASCII, upper and lower case letters differ only in bit 5 (0x20): `'A' = 0x41`, `'a' = 0x61`.",
        "`ldrb w2, [x0], #1`, and after the NUL check `orr w2, w2, #0x20`.",
    ],
    solution='''def count_vowels(s):
    count = 0                            # x1
    for ch in s:                         # ldrb w2, [x0], #1 until the NUL byte
        c = ord(ch) | 0x20               # orr w2, w2, #0x20: 'A' (0x41) -> 'a' (0x61)
        # Only bit 5 changes, so a non-letter can never be folded onto a vowel.
        if c in (ord("a"), ord("e"), ord("i"), ord("o"), ord("u")):
            count += 1                   # Lvowel: add x1, x1, #1
    return count
''',
    asm_solution="""// long long count_vowels(const char* s)
// On entry: x0 = s       On exit: x0 = number of vowels (either case)
.text                          // code section
.globl _count_vowels           // export the symbol
.p2align 2                     // 4-byte alignment
_count_vowels:                 // function entry
    mov x1, #0                 // x1 = vowel count
Lloop:                         // next character
    ldrb w2, [x0], #1          // w2 = *s, then s += 1
    cbz w2, Ldone              // NUL terminator: finished
    orr w2, w2, #0x20          // set bit 5: folds 'A'..'Z' onto 'a'..'z'
    cmp w2, #'a'               // is it 'a'?
    b.eq Lvowel                // yes: count it
    cmp w2, #'e'               // is it 'e'?
    b.eq Lvowel                // yes
    cmp w2, #'i'               // is it 'i'?
    b.eq Lvowel                // yes
    cmp w2, #'o'               // is it 'o'?
    b.eq Lvowel                // yes
    cmp w2, #'u'               // is it 'u'?
    b.eq Lvowel                // yes
    b Lloop                    // not a vowel: next character
Lvowel:                        // the byte was a vowel
    add x1, x1, #1             // count += 1
    b Lloop                    // next character
Ldone:                         // end of string
    mov x0, x1                 // return the count
    ret                        // back to the caller
""",
    tests=[["Hey!"], [""], ["AEIOU aeiou"], ["rhythm"], ["Hello, World!"], ["The Quick Brown Fox Jumps Over The Lazy Dog"],
           ["".join(_R.choice("abcdeEIOUxyz !?@[`{") for _ in range(400))], ["@`[{"]],
    explanation="""## Intuition

Two ideas: walk the bytes with a post-indexed `ldrb` until the NUL, and avoid doubling
the comparisons by **normalising case** first. ASCII was designed so that upper and
lower case letters differ in a single bit (0x20), so `orr` with 0x20 lowercases a letter.

## Approach

Trace for `"Hey!"` (bytes `48 65 79 21 00`):

| iteration | w2 loaded | after `orr #0x20` | vowel? | x1 |
|---|---|---|---|---|
| 1 | 0x48 'H' | 0x68 'h' | no | 0 |
| 2 | 0x65 'e' | 0x65 'e' | yes → `Lvowel` | 1 |
| 3 | 0x79 'y' | 0x79 'y' | no | 1 |
| 4 | 0x21 '!' | 0x21 '!' | no | 1 |
| 5 | 0x00 | (`cbz` exits first) | | |

Return **1**.

* `ldrb w2, [x0], #1`: byte load, then advance by one byte.
* `cbz w2, Ldone` **before** the `orr`: otherwise the terminator 0x00 becomes 0x20
  (space) and the loop never ends.
* `orr w2, w2, #0x20`: bitwise OR with a logical immediate.
* `cmp w2, #'a'`: the assembler accepts character literals; `'a'` is just 97.
* `b.eq`: branch if the last compare was equal.

Is the folding safe? `c | 0x20 == 'a'` only for `c ∈ {0x41, 0x61}` = `{'A', 'a'}`,
because the two candidates differ only in bit 5. Characters like `@` (0x40) fold to
`` ` `` (0x60), never to a vowel; the last test checks exactly these neighbours.

## Complexity

O(n) time, O(1) space.

## Common mistakes

* **`orr` before the NUL test**: infinite loop (timeout) or a segfault when you run off
  the end of the string.
* **`ldr` instead of `ldrb`**: 8 bytes at a time; the comparisons see garbage.
* **`and w2, w2, #0x20`** clears everything *except* bit 5. To lowercase you set the
  bit (`orr`); to uppercase you would clear it (`and #0xDF` / `bic #0x20`).
* **Forgetting `b Lloop` after the last compare** falls through into `Lvowel` and counts
  every character.

## Going further

Replace the compare chain with a bitmask: `sub w3, w2, #'a'`, then `cmp w3, #25` +
`b.hi` (one unsigned compare rejects both "below 'a'" and "above 'z'"!), then test bit
`w3` of the mask `0x104111` (bits 0, 4, 8, 14, 20). You will need `movz`/`movk` to build
that constant, since it is not a valid logical immediate.""",
    x86=dict(
        solution="""# long long count_vowels(const char* s)
# On entry: rdi = s       On exit: rax = number of vowels (either case)
.text                          # code section
.globl _count_vowels           # export the symbol
.p2align 4                     # 16-byte alignment
_count_vowels:                 # function entry
    movq $0, %rax              # rax = vowel count
Lloop:                         # next character
    movzbq (%rdi), %rcx        # rcx = *s, zero-extended
    incq %rdi                  # s += 1
    testq %rcx, %rcx           # NUL terminator?
    jz Ldone                   # yes: finished
    orq $0x20, %rcx            # set bit 5: folds 'A'..'Z' onto 'a'..'z'
    cmpq $'a', %rcx            # is it 'a'?
    je Lvowel                  # yes: count it
    cmpq $'e', %rcx            # is it 'e'?
    je Lvowel                  # yes
    cmpq $'i', %rcx            # is it 'i'?
    je Lvowel                  # yes
    cmpq $'o', %rcx            # is it 'o'?
    je Lvowel                  # yes
    cmpq $'u', %rcx            # is it 'u'?
    je Lvowel                  # yes
    jmp Lloop                  # not a vowel: next character
Lvowel:                        # the byte was a vowel
    incq %rax                  # count += 1
    jmp Lloop                  # next character
Ldone:                         # end of string
    ret                        # return the count
""",
        todos=[("movzbq (%rdi), %rcx", "load the current byte of the string into rcx, zero-extended"),
               ("orq $0x20, %rcx", "lowercase the character by setting bit 5 (0x20)")],
        notes="""**On entry:** `%rdi = s`. **On exit:** `%rax` = number of vowels.

Load bytes with `movzbq` (one byte, zero-extended). Character constants work as
immediates: `cmpq $'z', %r8`. ASCII upper- and lowercase letters differ only in bit 5
(0x20), so OR-ing it in lowercases a letter.""",
        hints=[
            "Load exactly one byte from where `%rdi` points; the next line advances the pointer.",
            "Setting bit 5 with an OR folds uppercase onto lowercase (`$0x20`).",
            "`movzbq (%rdi), %rcx` and `orq $0x20, %rcx`",
        ],
        explanation="""## Intuition

Walk the string byte by byte, fold case, and compare against the five vowels.

## Approach

| byte | after `orq $0x20` | vowel? | rax |
|---|---|---|---|
| 'H' | 'h' | no | 0 |
| 'E' | 'e' | yes | 1 |
| 'y' | 'y' | no | 1 |
| 0 → exit | | | **1** |

The pointer is incremented before the NUL test; that is fine because we return
without using it.

## Complexity

O(n) time, O(1) space.

## Common mistakes

* **`movq (%rdi), %rcx`** loads 8 characters at once.
* **`andq $0x20`** clears everything *except* bit 5.
* **Comparing before folding case** misses uppercase vowels.""",
    ),
), [("ldrb w2, [x0], #1", "load the next byte of the string into w2 and advance x0 by one byte"),
    ("orr w2, w2, #0x20", "lowercase the character by setting bit 5 (0x20)")])

# ---------------------------------------------------------------- 17. reverse
_add(dict(
    id="asm-reverse-array",
    title="Reverse an Array In Place",
    difficulty=2,
    tags=["array", "two pointers", "str", "in-place"],
    fn="reverse_array",
    params=[["nums", "int[]"]],
    returns="void",
    mutates="nums",
    statement="""Reverse `nums` **in place**. The function returns nothing; the harness prints
the array after your function returns.

**On entry:** `x0` = pointer to `nums[0]`, `x1` = number of elements.
**On exit:** the memory holds the elements in reverse order. `x0` does not matter.

The starter walks a left pointer `x0` forwards and a right pointer `x2` backwards,
swapping as it goes.""",
    constraints=["0 ≤ len(nums) ≤ 1000", "−10⁹ ≤ nums[i] ≤ 10⁹"],
    hints=[
        "The last element is at `nums + 8·(count − 1)`. Shifted-register operands compute `8·count` for free: `add x2, x0, x1, lsl #3`.",
        "Load both ends into registers, then store each into the other's slot.",
        "`str x4, [x0], #8` (store right value on the left, move right) and `str x3, [x2], #-8` (store left value on the right, move left).",
    ],
    solution='''def reverse_array(nums):
    i = 0                    # x0: left pointer
    j = len(nums) - 1        # x2: right pointer (&nums[n-1])
    while i < j:             # cmp x0, x2 ; b.hs Ldone (unsigned: addresses)
        left = nums[i]       # ldr x3, [x0]
        right = nums[j]      # ldr x4, [x2]
        nums[i] = right      # str x4, [x0], #8
        nums[j] = left       # str x3, [x2], #-8
        i += 1
        j -= 1
''',
    asm_solution="""// void reverse_array(long long* nums, long long count)
// On entry: x0 = &nums[0], x1 = count       On exit: nums reversed in memory
.text                          // code section
.globl _reverse_array          // export the symbol
.p2align 2                     // 4-byte alignment
_reverse_array:                // function entry
    add x2, x0, x1, lsl #3     // x2 = nums + count*8 = one past the last element
    sub x2, x2, #8             // x2 = &nums[count-1] (right pointer)
Lloop:                         // loop test
    cmp x0, x2                 // compare left and right addresses
    b.hs Ldone                 // unsigned left >= right: pointers met or crossed
    ldr x3, [x0]               // x3 = *left
    ldr x4, [x2]               // x4 = *right
    str x4, [x0], #8           // *left = old right value, then left += 8
    str x3, [x2], #-8          // *right = old left value, then right -= 8
    b Lloop                    // repeat
Ldone:                         // done
    ret                        // void function: nothing to return
""",
    tests=[[[1, 2, 3, 4]], [[]], [[7]], [[1, 2, 3]], [[-5, 0, 5, 10, 15]],
           [[_R.randint(-10**9, 10**9) for _ in range(301)]], [[9, 9, 1]]],
    explanation="""## Intuition

Two pointers, one at each end, swap and walk towards each other. In assembly a swap is
two loads into registers and two stores back, crossed over. Post-indexed stores let
the pointers move as a side effect.

## Approach

Trace for `[1, 2, 3, 4]` at address `A` (so `x2` starts at `A+24`):

| iteration | x0 | x2 | x3 | x4 | array after stores |
|---|---|---|---|---|---|
| 1 | A | A+24 | 1 | 4 | [4, 2, 3, 1] |
| 2 | A+8 | A+16 | 2 | 3 | [4, 3, 2, 1] |
| exit | A+16 | A+8 | `cmp`: A+16 ≥ A+8 → `b.hs` | | |

* `add x2, x0, x1, lsl #3`: the **shifted register** form computes `x0 + (x1 << 3)`,
  i.e. `x0 + 8·count`, in one instruction.
* `str Xt, [Xn], #8`: store 8 bytes at `Xn`, then `Xn += 8`. `#-8` moves backwards.
* `b.hs`: **unsigned** higher-or-same. Addresses are unsigned quantities.
* Edge cases fall out naturally: for `count = 0`, `x2 = x0 − 8 < x0`; for `count = 1`,
  `x2 = x0`. Both exit before any memory access.

## Complexity

O(n) time, O(1) extra space.

## Common mistakes

* **Storing before loading both**: `str x3, [x2]` before `ldr x4, [x2]` overwrites the
  value you wanted to move. Load both, then store both.
* **`b.ge` on pointers**: works for typical user-space addresses, but pointers are
  unsigned; use `hs`/`hi`/`lo`/`ls` and avoid surprises.
* **`b.eq` as the exit test**: with an even count the pointers cross without ever being
  equal, so the loop keeps swapping (un-reversing) and then runs off the array.
* **`lsl #8`** or forgetting the shift entirely: points at the wrong element.

## Going further

`ldr x3, [x0]` + `ldr x4, [x2]` can't become a single `ldp` because the two elements
aren't adjacent, but reversing the *bytes* of a 64-bit register is one instruction:
`rev x0, x0`. Look up `rev`, `rev16`, `rev32` and `rbit`.""",
    x86=dict(
        solution="""# void reverse_array(long long* nums, long long count)
# On entry: rdi = &nums[0], rsi = count       On exit: nums reversed in memory
.text                          # code section
.globl _reverse_array          # export the symbol
.p2align 4                     # 16-byte alignment
_reverse_array:                # function entry
    leaq -8(%rdi,%rsi,8), %rdx # rdx = nums + count*8 - 8 = &nums[count-1] (right pointer)
Lloop:                         # loop test
    cmpq %rdx, %rdi            # flags from left - right
    jae Ldone                  # unsigned left >= right: pointers met or crossed
    movq (%rdi), %rcx          # rcx = *left
    movq (%rdx), %r8           # r8 = *right
    movq %r8, (%rdi)           # *left = old right value
    movq %rcx, (%rdx)          # *right = old left value
    addq $8, %rdi              # left += 8
    subq $8, %rdx              # right -= 8
    jmp Lloop                  # repeat
Ldone:                         # done
    ret                        # void function: nothing to return
""",
        todos=[("leaq -8(%rdi,%rsi,8), %rdx", "compute the address of the last element, nums + count*8 - 8, into rdx with one instruction"),
               ("movq %r8, (%rdi)", "store the old right value (r8) at the left pointer"),
               ("movq %rcx, (%rdx)", "store the old left value (rcx) at the right pointer")],
        notes="""**On entry:** `%rdi = &nums[0]`, `%rsi = count`. **On exit:** the array is reversed in place.

The full memory-operand form is `disp(base, index, scale)` = `base + index*scale + disp`,
with scale 1, 2, 4 or 8. `lea` evaluates it without touching memory:
`leaq 16(%r9,%r10,4), %r11` sets `r11 = r9 + r10*4 + 16`. Compare pointers with the
**unsigned** conditions (`b`, `be`, `a`, `ae`).""",
        hints=[
            "The last element sits at `nums + (count-1)*8`, which is `nums + count*8 - 8`.",
            "One `lea` with base `%rdi`, index `%rsi`, scale 8 and displacement −8 computes it. The swap stores each loaded value at the *other* pointer.",
            "`leaq -8(%rdi,%rsi,8), %rdx`, `movq %r8, (%rdi)`, `movq %rcx, (%rdx)`",
        ],
        explanation="""## Intuition

Two pointers start at the ends, swap, and move toward each other until they meet.

## Approach

| step | left | right | array |
|---|---|---|---|
| entry | &a[0] | &a[3] | 1 2 3 4 |
| swap | &a[1] | &a[2] | 4 2 3 1 |
| swap | &a[2] | &a[1] | 4 3 2 1 |
| left ≥ right → `ret` | | | **4 3 2 1** |

For `count = 0` the right pointer is `nums − 8`, already below `left`, so nothing is
touched.

## Complexity

O(n) time, O(1) space.

## Common mistakes

* **Signed `jge`** on addresses: works here but is wrong in principle for pointers.
* **Storing a register back where it came from**: the array is unchanged.
* **Scale 1 instead of 8**: `(%rdi,%rsi)` points into the middle of the array.""",
    ),
), [("add x2, x0, x1, lsl #3", "compute nums + count*8 (one past the last element) into x2 using a shifted register operand"),
    ("str x4, [x0], #8", "store the old right value (x4) at the left pointer, then advance the left pointer by 8"),
    ("str x3, [x2], #-8", "store the old left value (x3) at the right pointer, then move the right pointer back by 8")])

# ---------------------------------------------------------------- 18. dot product
_add(dict(
    id="asm-dot-product",
    title="Dot Product",
    difficulty=3,
    tags=["array", "madd", "calling convention"],
    fn="dot_product",
    params=[["a", "int[]"], ["b", "int[]"]],
    returns="int",
    statement="""Return the dot product `a[0]·b[0] + a[1]·b[1] + …` of two arrays of equal
length.

**On entry:** each array takes two registers, so
`x0` = pointer to `a[0]`, `x1` = len(a), `x2` = pointer to `b[0]`, `x3` = len(b)
(equal to `x1`).
**On exit:** `x0` = the dot product (0 for empty arrays).""",
    constraints=["0 ≤ len(a) = len(b) ≤ 1000", "−10⁴ ≤ a[i], b[i] ≤ 10⁴"],
    hints=[
        "Walk both arrays in lockstep with two post-indexed loads. Where is `b`'s pointer?",
        "`madd Xd, Xn, Xm, Xa` computes `Xa + Xn·Xm` in one instruction: a multiply-accumulate.",
        "`ldr x6, [x2], #8` and `madd x4, x5, x6, x4`.",
    ],
    solution='''def dot_product(a, b):
    total = 0                    # x4
    for i in range(len(a)):      # x1 counts down; x3 (len(b)) is never needed
        x = a[i]                 # ldr x5, [x0], #8
        y = b[i]                 # ldr x6, [x2], #8
        total += x * y           # madd x4, x5, x6, x4
    return total
''',
    asm_solution="""// long long dot_product(long long* a, long long aSize, long long* b, long long bSize)
// On entry: x0 = &a[0], x1 = len(a), x2 = &b[0], x3 = len(b)       On exit: x0 = sum a[i]*b[i]
.text                          // code section
.globl _dot_product            // export the symbol
.p2align 2                     // 4-byte alignment
_dot_product:                  // function entry
    mov x4, #0                 // x4 = running total
Lloop:                         // loop test
    cbz x1, Ldone              // no pairs left (x3 is equal and unused)
    ldr x5, [x0], #8           // x5 = a[i], advance a
    ldr x6, [x2], #8           // x6 = b[i], advance b
    madd x4, x5, x6, x4        // total = total + a[i] * b[i]
    sub x1, x1, #1             // one fewer pair
    b Lloop                    // repeat
Ldone:                         // loop exit
    mov x0, x4                 // return the total
    ret                        // back to the caller
""",
    tests=[[[1, 2, 3], [4, 5, 6]], [[], []], [[7], [-3]], [[1, -1, 1, -1], [1, 1, 1, 1]],
           [[10**4] * 1000, [10**4] * 1000],
           [[_R.randint(-10**4, 10**4) for _ in range(250)], [_R.randint(-10**4, 10**4) for _ in range(250)]],
           [[0, 0, 5], [9, 9, 2]]],
    explanation="""## Intuition

Same lockstep walk as summing an array, but with two cursors, and the "add" becomes
"add a product". Multiply-accumulate is so common (graphics, DSP, ML) that ARM has a
single instruction for it.

The real lesson is the **register layout**: each `int[]` occupies a pointer register
and a length register, so the second array's pointer is in `x2`, not `x1`.

## Approach

Trace for `a = [1, 2, 3]`, `b = [4, 5, 6]`:

| iteration | x5 | x6 | x4 after `madd` | x1 after |
|---|---|---|---|---|
| 1 | 1 | 4 | 4 | 2 |
| 2 | 2 | 5 | 14 | 1 |
| 3 | 3 | 6 | 32 | 0 |

Return **32**.

* `ldr x6, [x2], #8`: load from `b` and advance `b`'s pointer independently of `a`'s.
* `madd Xd, Xn, Xm, Xa`: `Xd = Xa + Xn·Xm`. The accumulator operand is **last**. `mul`
  is literally `madd` with `xzr` as the accumulator.
* Only one counter is needed because the lengths are equal.

## Complexity

O(n) time, O(1) space.

## Common mistakes

* **`ldr x6, [x1], #8`**: `x1` is a length, not an address: segmentation fault.
* **`madd x4, x4, x5, x6`**: computes `x6 + x4·x5`, a completely different value.
* **Forgetting to advance one of the pointers** multiplies every `a[i]` by `b[0]`.
* **Signed overflow** is not a concern here (|product| ≤ 10⁸, sum ≤ 10¹¹), but with
  larger inputs `smulh` or `smaddl` (64 = 32×32 + 64) would matter.

## Going further

Unroll by two with `ldp x5, x7, [x0], #16` / `ldp x6, x8, [x2], #16` and two
accumulators (two independent `madd` chains keep the multiplier pipeline busy), then
handle a leftover element. With NEON you could process several 32-bit lanes per
instruction (`mla v0.4s, v1.4s, v2.4s`).""",
    x86=dict(
        solution="""# long long dot_product(long long* a, long long aSize, long long* b, long long bSize)
# On entry: rdi = &a[0], rsi = len(a), rdx = &b[0], rcx = len(b)       On exit: rax = sum a[i]*b[i]
.text                          # code section
.globl _dot_product            # export the symbol
.p2align 4                     # 16-byte alignment
_dot_product:                  # function entry
    movq $0, %rax              # rax = running total
Lloop:                         # loop test
    testq %rsi, %rsi           # pairs left? (rcx is equal and unused)
    jz Ldone                   # no
    movq (%rdi), %r8           # r8 = a[i]
    imulq (%rdx), %r8          # r8 = a[i] * b[i] (multiply by a memory operand)
    addq %r8, %rax             # total += a[i] * b[i]
    addq $8, %rdi              # advance a
    addq $8, %rdx              # advance b
    decq %rsi                  # one fewer pair
    jmp Lloop                  # repeat
Ldone:                         # loop exit
    ret                        # return the total
""",
        todos=[("imulq (%rdx), %r8", "multiply a[i] (r8) by b[i], read directly from b's pointer"),
               ("addq %r8, %rax", "add the product to the running total"),
               ("addq $8, %rdx", "advance b's pointer to its next element")],
        notes="""**On entry:** `%rdi = &a[0]`, `%rsi = len(a)`, `%rdx = &b[0]`, `%rcx = len(b)`
(lengths are equal). **On exit:** `%rax = Σ a[i]·b[i]`.

There is no multiply-add; use `imulq` then `addq`. The two-operand `imulq` accepts a
memory source, e.g. `imulq 8(%r9), %r10` multiplies r10 by the value at `r9 + 8`.
Avoid the one-operand `mulq`: it writes `%rdx`, which holds `b`'s pointer here.""",
        hints=[
            "`%r8` holds `a[i]`; `b[i]` is at the address in `%rdx` and can be used without a separate load.",
            "Two-operand `imulq` with a memory source, then add into the total, then advance both pointers by 8.",
            "`imulq (%rdx), %r8`, `addq %r8, %rax`, `addq $8, %rdx`",
        ],
        explanation="""## Intuition

Walk both arrays in lockstep, multiplying pairs and summing the products.

## Approach

| i | a[i] | b[i] | r8 | rax |
|---|---|---|---|---|
| 0 | 1 | 4 | 4 | 4 |
| 1 | 2 | 5 | 10 | 14 |
| 2 | 3 | 6 | 18 | **32** |

## Complexity

O(n) time, O(1) space.

## Common mistakes

* **`mulq (%rdx)`** (one operand) multiplies `%rax` and overwrites `%rdx`: the total
  and b's pointer are both destroyed.
* **Advancing only one pointer**: every `a[i]` gets multiplied by `b[0]`.""",
    ),
), [("ldr x6, [x2], #8", "load b[i] from b's pointer (x2) into x6 and advance that pointer"),
    ("madd x4, x5, x6, x4", "multiply a[i] (x5) by b[i] (x6) and add the product to the total x4")])

# ---------------------------------------------------------------- 19. binary search
_bs_big = sorted(_R.sample(range(-10**6, 10**6), 500))
_add(dict(
    id="asm-binary-search",
    title="Binary Search",
    difficulty=3,
    tags=["array", "binary search", "signed", "addressing"],
    fn="binary_search",
    params=[["nums", "int[]"], ["target", "int"]],
    returns="int",
    statement="""`nums` is sorted in strictly increasing order. Return the index of `target`, or
`-1` if it is not present. Use binary search.

**On entry:** `x0` = pointer to `nums[0]`, `x1` = number of elements, `x2 = target`.
**On exit:** `x0` = index or −1.

The starter keeps `lo` in `x3`, `hi` in `x4` (inclusive) and `mid` in `x5`.""",
    constraints=["0 ≤ len(nums) ≤ 1000", "−10⁶ ≤ nums[i], target ≤ 10⁶", "values are distinct"],
    hints=[
        "`nums[mid]` lives at `x0 + 8·mid`. One `ldr` with a scaled register offset can load it.",
        "`hi` starts at `count − 1`, which is **−1** for an empty array. Which condition codes treat that correctly?",
        "`ldr x6, [x0, x5, lsl #3]`; leave the loop with `b.gt` (signed lo > hi); after comparing `nums[mid]` with the target, `b.lt` goes right.",
    ],
    solution='''def binary_search(nums, target):
    lo, hi = 0, len(nums) - 1        # x3, x4 (hi is -1 when empty: signed!)
    while lo <= hi:                  # cmp x3, x4 ; b.gt Lnot_found
        mid = (lo + hi) >> 1         # add x5, x3, x4 ; lsr x5, x5, #1
        v = nums[mid]                # ldr x6, [x0, x5, lsl #3]
        if v == target:              # cmp x6, x2 ; b.eq Lfound
            return mid
        if v < target:               # b.lt Lgo_right (signed)
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
''',
    asm_solution="""// long long binary_search(long long* nums, long long count, long long target)
// On entry: x0 = &nums[0], x1 = count, x2 = target       On exit: x0 = index or -1
.text                          // code section
.globl _binary_search          // export the symbol
.p2align 2                     // 4-byte alignment
_binary_search:                // function entry
    mov x3, #0                 // x3 = lo = 0
    sub x4, x1, #1             // x4 = hi = count - 1 (may be -1)
Lloop:                         // loop test
    cmp x3, x4                 // compare lo with hi
    b.gt Lnot_found            // signed lo > hi: range is empty
    add x5, x3, x4             // x5 = lo + hi (both >= 0 inside the loop)
    lsr x5, x5, #1             // mid = (lo + hi) / 2
    ldr x6, [x0, x5, lsl #3]   // x6 = nums[mid] (address nums + mid*8)
    cmp x6, x2                 // compare nums[mid] with target
    b.eq Lfound                // equal: done
    b.lt Lgo_right             // nums[mid] < target (signed): search the right half
    sub x4, x5, #1             // otherwise hi = mid - 1
    b Lloop                    // continue
Lgo_right:                     // target is to the right of mid
    add x3, x5, #1             // lo = mid + 1
    b Lloop                    // continue
Lfound:                        // nums[mid] == target
    mov x0, x5                 // return mid
    ret                        // back to the caller
Lnot_found:                    // range became empty
    mov x0, #-1                // return -1
    ret                        // back to the caller
""",
    tests=[[[1, 3, 5, 7, 9, 11], 7], [[], 4], [[5], 5], [[5], 6], [[-10, -5, 0, 5, 10], -10],
           [[-10, -5, 0, 5, 10], 10], [[-10, -5, 0, 5, 10], -7], [[2, 4, 6, 8], 1], [[2, 4, 6, 8], 9],
           [_bs_big, _bs_big[333]], [_bs_big, 10**6]],
    explanation="""## Intuition

The algorithm is the usual inclusive-range binary search. The assembly lessons are
**scaled-index addressing** (`nums[mid]` in one load) and, above all, choosing
**signed** conditions: `lo`, `hi`, the elements and the target can all be negative or −1.

## Approach

Trace for `nums = [1, 3, 5, 7, 9, 11]`, `target = 7`:

| step | x3 lo | x4 hi | x5 mid | x6 nums[mid] | decision |
|---|---|---|---|---|---|
| 1 | 0 | 5 | 2 | 5 | 5 < 7 → `b.lt Lgo_right`, lo = 3 |
| 2 | 3 | 5 | 4 | 9 | 9 > 7 → hi = 3 |
| 3 | 3 | 3 | 3 | 7 | equal → `Lfound` |

Return **3**.

* `ldr x6, [x0, x5, lsl #3]`: address = `x0 + (x5 << 3)`. The shift amount must match
  the element size (`lsl #3` for 8 bytes; `ldrb` takes no shift, `ldr w` takes `lsl #2`).
* `cmp x3, x4` + `b.gt`: **signed** `lo > hi`.
* `cmp x6, x2` sets flags once; `b.eq` and then `b.lt` both read the same flags.
* `lsr x5, x5, #1`: halve. Inside the loop `lo + hi ≥ 0`, so `lsr` and `asr` agree.
* `mov x0, #-1`: the assembler emits `movn x0, #0` (move NOT), which gives all ones.

## Complexity

O(log n) time, O(1) space.

## Common mistakes

* **`b.hi` instead of `b.gt`** for the loop test. With an empty array `hi = −1`, which
  unsigned is 2⁶⁴ − 1, so `lo > hi` is false and the code loads `nums[huge]`:
  segmentation fault. Likewise when the search narrows to the left of index 0
  (`hi = mid − 1 = −1`).
* **`b.lo` instead of `b.lt`** for the element comparison: negative values look huge
  and the search goes the wrong way.
* **Forgetting the scale** (`[x0, x5]`) reads a misaligned value 1/8 of the way in.
* **`hi = mid` / `lo = mid`** instead of `mid ∓ 1` can loop forever on a two-element
  range.

## Going further

Write the "lower bound" variant (first index with `nums[i] ≥ target`) branch-free:
keep `base` and `len`, and each step do `cmp` + `csel` on `base` and halve `len`. The
loop then has no unpredictable branches, which is how high-performance searches are
written.""",
    x86=dict(
        solution="""# long long binary_search(long long* nums, long long count, long long target)
# On entry: rdi = &nums[0], rsi = count, rdx = target       On exit: rax = index or -1
.text                          # code section
.globl _binary_search          # export the symbol
.p2align 4                     # 16-byte alignment
_binary_search:                # function entry
    movq $0, %r8               # r8 = lo = 0
    leaq -1(%rsi), %r9         # r9 = hi = count - 1 (may be -1)
Lloop:                         # loop test
    cmpq %r9, %r8              # flags from lo - hi
    jg Lnot_found              # signed lo > hi: range is empty
    leaq (%r8,%r9), %rax       # rax = lo + hi (both >= 0 inside the loop)
    shrq $1, %rax              # mid = (lo + hi) / 2
    movq (%rdi,%rax,8), %rcx   # rcx = nums[mid] (address nums + mid*8)
    cmpq %rdx, %rcx            # compare nums[mid] with target
    je Lfound                  # equal: done
    jl Lgo_right               # nums[mid] < target (signed): search the right half
    leaq -1(%rax), %r9         # otherwise hi = mid - 1
    jmp Lloop                  # continue
Lgo_right:                     # target is to the right of mid
    leaq 1(%rax), %r8          # lo = mid + 1
    jmp Lloop                  # continue
Lfound:                        # nums[mid] == target
    ret                        # return mid (already in rax)
Lnot_found:                    # range became empty
    movq $-1, %rax             # return -1
    ret                        # back to the caller
""",
        todos=[("jg Lnot_found", "leave the loop when lo > hi, using a SIGNED condition (hi can be -1)"),
               ("movq (%rdi,%rax,8), %rcx", "load nums[mid] into rcx (address = nums + mid * 8)"),
               ("jl Lgo_right", "if nums[mid] < target (signed), branch to Lgo_right")],
        notes="""**On entry:** `%rdi = &nums[0]`, `%rsi = count`, `%rdx = target`.
**On exit:** `%rax` = index or −1.

Registers: `lo = %r8`, `hi = %r9`, `mid = %rax`. Indexed loads use
`disp(base,index,scale)`: `movq (%r10,%r11,8), %r12` loads the 8-byte element `r10[r11]`.
One `cmp` can feed several conditional jumps in a row, since jumps do not change the
flags. Signed jumps: `jl jle jg jge`; unsigned: `jb jbe ja jae`.""",
        hints=[
            "`hi` starts at −1 for an empty array, so the loop test must be signed.",
            "The element address is base `%rdi`, index `%rax`, scale 8. After comparing `nums[mid]` with the target, the flags still hold for a second jump.",
            "`jg Lnot_found`, `movq (%rdi,%rax,8), %rcx`, `jl Lgo_right`",
        ],
        explanation="""## Intuition

Keep a closed range `[lo, hi]` that must contain the target if it exists; halve it each
step by looking at the middle element.

## Approach

Search 7 in `[1, 3, 5, 7, 9]`:

| lo (r8) | hi (r9) | mid (rax) | nums[mid] | action |
|---|---|---|---|---|
| 0 | 4 | 2 | 5 | less → lo = 3 |
| 3 | 4 | 3 | 7 | equal → return **3** |

`leaq -1(%rax), %r9` is a compact `r9 = rax - 1`.

## Complexity

O(log n) time, O(1) space.

## Common mistakes

* **`ja`** (unsigned) for `lo > hi`: with `hi = -1` that is 0 > 2⁶⁴−1, false, and the
  loop reads `nums[huge]`.
* **Scale 1** in the load reads misaligned bytes.
* **`jb` instead of `jl`** for the value comparison breaks on negative numbers.""",
    ),
), [("b.gt Lnot_found", "leave the loop when lo > hi, using a SIGNED condition (hi can be -1)"),
    ("ldr x6, [x0, x5, lsl #3]", "load nums[mid] into x6 (address = nums + mid * 8)"),
    ("b.lt Lgo_right", "if nums[mid] < target (signed), branch to Lgo_right")])

# ---------------------------------------------------------------- 20. palindrome
_add(dict(
    id="asm-is-palindrome",
    title="Palindrome String",
    difficulty=3,
    tags=["string", "two pointers", "ldrb"],
    fn="is_palindrome",
    params=[["s", "str"]],
    returns="bool",
    statement="""Return `true` (1) if the ASCII string `s` reads the same forwards and backwards,
comparing bytes exactly (case-sensitive, spaces count). The empty string is a palindrome.

**On entry:** `x0` = pointer to a NUL-terminated string.
**On exit:** `x0 = 1` for a palindrome, `0` otherwise.

The starter first finds the end of the string, then walks `x0` forwards and `x1`
backwards comparing bytes.""",
    constraints=["0 ≤ len(s) ≤ 1000", "printable ASCII only"],
    hints=[
        "Phase 1 is `strlen` with a pointer: when the loop ends, `x1` points at the NUL, so step back one byte to the last character.",
        "Phase 2: stop when the pointers meet or cross (unsigned `hs`). Load one byte from each end, advancing them towards each other with post-indexing.",
        "`ldrb w3, [x1], #-1`, then `cmp w2, w3` and `b.ne Lno`.",
    ],
    solution='''def is_palindrome(s):
    data = s.encode()
    i = 0                    # x0: left pointer
    j = len(data) - 1        # x1: last character (s - 1 when empty)
    while i < j:             # cmp x0, x1 ; b.hs Lyes
        if data[i] != data[j]:   # ldrb w2 / ldrb w3 ; cmp ; b.ne Lno
            return False
        i += 1               # post-index #1
        j -= 1               # post-index #-1
    return True
''',
    asm_solution="""// bool is_palindrome(const char* s)   (returned as 0/1 in x0)
// On entry: x0 = s       On exit: x0 = 1 if s is a palindrome, else 0
.text                          // code section
.globl _is_palindrome          // export the symbol
.p2align 2                     // 4-byte alignment
_is_palindrome:                // function entry
    mov x1, x0                 // x1 = scanning pointer, starts at s
Lfind_end:                     // phase 1: find the NUL terminator
    ldrb w2, [x1]              // w2 = *x1
    cbz w2, Lfound_end         // reached the NUL
    add x1, x1, #1             // next byte
    b Lfind_end                // keep scanning
Lfound_end:                    // x1 points at the NUL
    sub x1, x1, #1             // x1 = last character (s - 1 if the string is empty)
Lcompare:                      // phase 2: compare from both ends
    cmp x0, x1                 // compare left and right addresses
    b.hs Lyes                  // unsigned left >= right: every pair matched
    ldrb w2, [x0], #1          // w2 = *left, left += 1
    ldrb w3, [x1], #-1         // w3 = *right, right -= 1
    cmp w2, w3                 // same character?
    b.ne Lno                   // mismatch: not a palindrome
    b Lcompare                 // next pair
Lyes:                          // palindrome
    mov x0, #1                 // return true
    ret                        // back to the caller
Lno:                           // mismatch found
    mov x0, #0                 // return false
    ret                        // back to the caller
""",
    tests=[["abba"], [""], ["a"], ["ab"], ["racecar"], ["Aa"], ["abccba"], ["abcdba"], ["never odd or even"],
           ["step on no pets"], ["x" * 500 + "y" + "x" * 500]],
    explanation="""## Intuition

Two pointers again, but on bytes and with an extra first phase: a C string doesn't
tell you where it ends, so you scan for the NUL first. Then compare outer pairs moving
inwards; any mismatch answers "no", meeting in the middle answers "yes".

## Approach

Trace for `"abba"` at address `S`:

| phase | x0 | x1 | w2 | w3 | result |
|---|---|---|---|---|---|
| scan done | S | S+4 (NUL) | | | |
| `sub` | S | S+3 | | | |
| pair 1 | S → S+1 | S+3 → S+2 | 'a' | 'a' | equal |
| pair 2 | S+1 → S+2 | S+2 → S+1 | 'b' | 'b' | equal |
| test | S+2 | S+1 | | | S+2 ≥ S+1 → `Lyes` |

Return **1**. For `"ab"`: pair 1 loads 'a' and 'b', `b.ne Lno` returns 0. For `""`: the
scan stops immediately, `x1 = S − 1 < S`, so `b.hs` returns 1 without loading anything.

* `ldrb w3, [x1], #-1`: post-indexed with a **negative** offset walks backwards.
* `cmp w2, w3`: 32-bit compare is fine for bytes.
* `b.hs` (unsigned ≥) for pointer comparison; odd lengths end with `x0 == x1` (the
  middle character needs no partner), even lengths end with the pointers crossed.
* Two exits, each with its own `mov` + `ret`: perfectly normal in assembly.

## Complexity

O(n) time (one scan plus half a scan), O(1) space.

## Common mistakes

* **Forgetting `sub x1, x1, #1`**: the first comparison is `s[0]` against the NUL, so
  everything non-empty is "not a palindrome".
* **`b.eq` as the meeting test**: with an even length the pointers cross without ever
  being equal, so they keep diverging, read past both ends of the string and
  eventually crash or report a bogus mismatch.
* **`ldr` instead of `ldrb`** compares 8-byte chunks and reads past the end.
* **Signed pointer compare (`b.ge`)** happens to work for user-space addresses, but the
  habit breaks on platforms where addresses have the top bit set.

## Going further

Make it case-insensitive and ignore non-letters (the classic LeetCode version): skip
bytes on each side that are not letters (use the `sub` + unsigned `cmp` range trick on
`c | 0x20`) and compare the folded values.""",
    x86=dict(
        solution="""# bool is_palindrome(const char* s)   (returned as 0/1 in rax)
# On entry: rdi = s       On exit: rax = 1 if s is a palindrome, else 0
.text                          # code section
.globl _is_palindrome          # export the symbol
.p2align 4                     # 16-byte alignment
_is_palindrome:                # function entry
    movq %rdi, %rsi            # rsi = scanning pointer, starts at s
Lfind_end:                     # phase 1: find the NUL terminator
    cmpb $0, (%rsi)            # compare the byte at rsi with 0
    je Lfound_end              # reached the NUL
    incq %rsi                  # next byte
    jmp Lfind_end              # keep scanning
Lfound_end:                    # rsi points at the NUL
    decq %rsi                  # rsi = last character (s - 1 if the string is empty)
Lcompare:                      # phase 2: compare from both ends
    cmpq %rsi, %rdi            # flags from left - right
    jae Lyes                   # unsigned left >= right: every pair matched
    movzbq (%rdi), %rax        # rax = *left
    movzbq (%rsi), %rcx        # rcx = *right
    incq %rdi                  # left += 1
    decq %rsi                  # right -= 1
    cmpq %rcx, %rax            # same character?
    jne Lno                    # mismatch: not a palindrome
    jmp Lcompare               # next pair
Lyes:                          # palindrome
    movq $1, %rax              # return true
    ret                        # back to the caller
Lno:                           # mismatch found
    movq $0, %rax              # return false
    ret                        # back to the caller
""",
        todos=[("jae Lyes", "if the left pointer is at or past the right pointer (unsigned), every pair matched: branch to Lyes"),
               ("movzbq (%rsi), %rcx", "load the byte at the right pointer into rcx, zero-extended"),
               ("cmpq %rcx, %rax", "compare the left byte with the right byte"),
               ("jne Lno", "if they differ, branch to Lno")],
        notes="""**On entry:** `%rdi = s`. **On exit:** `%rax = 1` if `s` is a palindrome, else `0`.

Left pointer is `%rdi`, right pointer `%rsi`. A compare can read memory directly with a
size suffix: `cmpb $0, (%r8)` compares the byte at `r8` with 0. Load characters with
`movzbq`. Pointer comparisons use unsigned conditions (`jb`, `jae`, …).""",
        hints=[
            "Stop comparing once the pointers meet or cross; addresses are unsigned.",
            "Load the right byte with zero-extension like the left one, compare the two registers, and jump to `Lno` if not equal.",
            "`jae Lyes`, `movzbq (%rsi), %rcx`, `cmpq %rcx, %rax`, `jne Lno`",
        ],
        explanation="""## Intuition

Find the end, then walk two pointers inward comparing bytes; any mismatch means no.

## Approach

`"abba"`:

| left | right | bytes | action |
|---|---|---|---|
| s+0 | s+3 | a, a | equal |
| s+1 | s+2 | b, b | equal |
| s+2 | s+1 | | left ≥ right → **1** |

The empty string gives right = s − 1 < left, so it returns 1 immediately.

## Complexity

O(n) time, O(1) space.

## Common mistakes

* **`movq` loads**: compare 8 bytes at a time instead of characters.
* **Signed `jge`** on pointers.
* **`cmpb $0, %rsi`** (no parentheses) compares the pointer itself, and the size does
  not match: `invalid operand for instruction`.""",
    ),
), [("b.hs Lyes", "if the left pointer is at or past the right pointer (unsigned), every pair matched: branch to Lyes"),
    ("ldrb w3, [x1], #-1", "load the byte at the right pointer into w3 and move the right pointer back one byte"),
    ("cmp w2, w3", "compare the left byte with the right byte"),
    ("b.ne Lno", "if they differ, branch to Lno")])

# ---------------------------------------------------------------- 21. bubble sort
_add(dict(
    id="asm-bubble-sort",
    title="Bubble Sort In Place",
    difficulty=3,
    tags=["sorting", "nested loops", "ldp", "stp", "in-place"],
    fn="bubble_sort",
    params=[["nums", "int[]"]],
    returns="void",
    mutates="nums",
    statement="""Sort `nums` in **ascending** order, in place, with bubble sort: repeatedly walk
the array swapping adjacent out-of-order pairs; after each pass the largest remaining
element has bubbled to the end. Stop early when a pass makes no swaps.

**On entry:** `x0` = pointer to `nums[0]`, `x1` = number of elements.
**On exit:** the memory holds the sorted elements.

Register plan in the starter: `x2` = comparisons per pass (shrinks by one each pass),
`x3` = cursor, `x4` = comparisons left in this pass, `x5`/`x6` = the adjacent pair,
`x7` = "swapped" flag.""",
    constraints=["0 ≤ len(nums) ≤ 80", "−10⁹ ≤ nums[i] ≤ 10⁹"],
    hints=[
        "Adjacent elements `nums[i]` and `nums[i+1]` are 16 consecutive bytes: one `ldp` loads both.",
        "They are in order when `x5 ≤ x6` (signed): skip the swap in that case. Otherwise store them back in the opposite order with `stp`.",
        "`ldp x5, x6, [x3]`, `b.le Lnoswap`, `stp x6, x5, [x3]`.",
    ],
    solution='''def bubble_sort(nums):
    n = len(nums)
    if n <= 1:                       # cmp x1, #1 ; b.le Ldone
        return
    limit = n - 1                    # x2: comparisons in the first pass
    while True:                      # Louter
        swapped = False              # x7 = 0
        for i in range(limit):       # x3 = cursor, x4 = comparisons left
            a, b = nums[i], nums[i + 1]      # ldp x5, x6, [x3]
            if a > b:                # cmp x5, x6 ; b.le Lnoswap (signed)
                nums[i], nums[i + 1] = b, a  # stp x6, x5, [x3]
                swapped = True       # mov x7, #1
        if not swapped:              # cbz x7, Ldone: already sorted
            return
        limit -= 1                   # largest element is now final
        if limit == 0:               # subs x2, x2, #1 ; b.ne Louter
            return
''',
    asm_solution="""// void bubble_sort(long long* nums, long long count)
// On entry: x0 = &nums[0], x1 = count       On exit: nums sorted ascending in memory
.text                          // code section
.globl _bubble_sort            // export the symbol
.p2align 2                     // 4-byte alignment
_bubble_sort:                  // function entry
    cmp x1, #1                 // fewer than two elements?
    b.le Ldone                 // then it is already sorted
    sub x2, x1, #1             // x2 = comparisons in the first pass = count - 1
Louter:                        // start of one pass
    mov x3, x0                 // x3 = cursor at nums[0]
    mov x4, x2                 // x4 = comparisons to do this pass
    mov x7, #0                 // x7 = swapped flag = false
Linner:                        // compare one adjacent pair
    ldp x5, x6, [x3]           // x5 = cursor[0], x6 = cursor[1] (16 contiguous bytes)
    cmp x5, x6                 // compare the pair
    b.le Lnoswap               // signed x5 <= x6: already in order
    stp x6, x5, [x3]           // write them back swapped
    mov x7, #1                 // remember that this pass swapped something
Lnoswap:                       // move to the next pair
    add x3, x3, #8             // cursor += one element
    subs x4, x4, #1            // one fewer comparison; sets Z when it reaches 0
    b.ne Linner                // more pairs in this pass
    cbz x7, Ldone              // a pass without swaps: sorted, stop early
    subs x2, x2, #1            // the last slot is final: shorten the next pass
    b.ne Louter                // run another pass if any comparisons remain
Ldone:                         // finished
    ret                        // void function
""",
    tests=[[[3, 1, 2]], [[]], [[1]], [[2, 1]], [[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]], [[4, -1, 4, 0, -1, 7]],
           [[_R.randint(-10**9, 10**9) for _ in range(80)]], [[_R.randint(-3, 3) for _ in range(40)]]],
    explanation="""## Intuition

Bubble sort is the simplest nested loop you can write in assembly, and it shows off
**pair** loads and stores: two adjacent 8-byte elements are 16 contiguous bytes, so
`ldp` reads both and `stp` writes both, and swapping is just storing them in the other
order.

## Approach

Trace for `[3, 1, 2]` (`x2` starts at 2):

| pass | x4 | x5 | x6 | swap? | array | x7 |
|---|---|---|---|---|---|---|
| 1 | 2 | 3 | 1 | yes | [1, 3, 2] | 1 |
| 1 | 1 | 3 | 2 | yes | [1, 2, 3] | 1 |
| end of pass 1 | 0 | | | | `subs x2` → 1, `b.ne Louter` | |
| 2 | 1 | 1 | 2 | no | [1, 2, 3] | 0 |
| end of pass 2 | 0 | | | | `cbz x7, Ldone` | |

**The instructions**

* `ldp Xt1, Xt2, [Xn]`: load `Xt1` from `Xn` and `Xt2` from `Xn + 8`.
* `stp Xt1, Xt2, [Xn]`: store `Xt1` at `Xn` and `Xt2` at `Xn + 8`. Writing
  `stp x6, x5` after `ldp x5, x6` performs the swap.
* `b.le`: signed ≤. Equal elements are **not** swapped (that makes bubble sort stable).
* `subs x4, x4, #1` + `b.ne`: subtract **and set flags**, then loop while non-zero. This
  is the classic count-down loop tail (equivalent to `sub` + `cbnz`), and shows how the
  `s` suffix makes an arithmetic instruction update the flags.
* `cbz x7, Ldone`: the early exit makes already-sorted input O(n).

## Complexity

O(n²) comparisons in the worst case, O(n) when already sorted, O(1) extra space.

## Common mistakes

* **`b.ls` / `b.lo` (unsigned)**: negative numbers sort *after* positive ones.
* **Starting each pass with `x4 = x1`** (count instead of count − 1): the last `ldp`
  reads one element past the end of the array, and may swap it in.
* **Resetting the cursor outside `Louter`**: the second pass starts where the first one
  ended.
* **Plain `sub` before `b.ne`**: `sub` doesn't set flags, so the branch reads stale flags
  from the `cmp`. Only the `s`-suffixed forms (`adds`, `subs`, `ands`) and `cmp`/`tst`
  update NZCV.

## Going further

Replace the branch around the swap with a branch-free version: `cmp x5, x6`,
`csel x8, x5, x6, le` (min), `csel x9, x6, x5, le` (max), `stp x8, x9, [x3]`. It always
stores, but never mispredicts. Then try insertion sort, which needs a backwards inner
loop with pre-indexed addressing.""",
    x86=dict(
        solution="""# void bubble_sort(long long* nums, long long count)
# On entry: rdi = &nums[0], rsi = count       On exit: nums sorted ascending in memory
.text                          # code section
.globl _bubble_sort            # export the symbol
.p2align 4                     # 16-byte alignment
_bubble_sort:                  # function entry
    cmpq $1, %rsi              # fewer than two elements?
    jle Ldone                  # then it is already sorted
    leaq -1(%rsi), %rdx        # rdx = comparisons in the first pass = count - 1
Louter:                        # start of one pass
    movq %rdi, %rcx            # rcx = cursor at nums[0]
    movq %rdx, %r8             # r8 = comparisons to do this pass
    movq $0, %r9               # r9 = swapped flag = false
Linner:                        # compare one adjacent pair
    movq (%rcx), %rax          # rax = cursor[0]
    movq 8(%rcx), %r10         # r10 = cursor[1] (the next 8 bytes)
    cmpq %r10, %rax            # flags from cursor[0] - cursor[1]
    jle Lnoswap                # signed cursor[0] <= cursor[1]: already in order
    movq %r10, (%rcx)          # cursor[0] = old cursor[1]
    movq %rax, 8(%rcx)         # cursor[1] = old cursor[0]
    movq $1, %r9               # remember that this pass swapped something
Lnoswap:                       # move to the next pair
    addq $8, %rcx              # cursor += one element
    decq %r8                   # one fewer comparison; sets ZF when it reaches 0
    jnz Linner                 # more pairs in this pass
    testq %r9, %r9             # did this pass swap anything?
    jz Ldone                   # a pass without swaps: sorted, stop early
    decq %rdx                  # the last slot is final: shorten the next pass
    jnz Louter                 # run another pass if any comparisons remain
Ldone:                         # finished
    ret                        # void function
""",
        todos=[("movq 8(%rcx), %r10", "load the neighbour cursor[1] (8 bytes past the cursor) into r10"),
               ("jle Lnoswap", "skip the swap if cursor[0] <= cursor[1] (signed)"),
               ("movq %r10, (%rcx)", "write the old cursor[1] into cursor[0]"),
               ("movq %rax, 8(%rcx)", "write the old cursor[0] into cursor[1]")],
        notes="""**On entry:** `%rdi = &nums[0]`, `%rsi = count`. **On exit:** the array is sorted ascending.

Registers: cursor `%rcx`, comparisons left in this pass `%r8`, swapped flag `%r9`,
the pair in `%rax` / `%r10`, pass length `%rdx`. x86 has no pair load/store: use two
`movq`s with a displacement (`8(%r11)` is the element after `(%r11)`). `decq` sets ZF
when the result is 0, so it can drive a `jnz` directly.""",
        hints=[
            "The pair is `cursor[0]` at `(%rcx)` and `cursor[1]` at `8(%rcx)`.",
            "Jump past the swap with a signed 'less or equal' condition; to swap, store each register at the other slot.",
            "`movq 8(%rcx), %r10`, `jle Lnoswap`, `movq %r10, (%rcx)`, `movq %rax, 8(%rcx)`",
        ],
        explanation="""## Intuition

Each pass bubbles the largest remaining value to the end; stop when a pass makes no
swaps.

## Approach

`[3, 1, 2]`:

| pass | pairs compared | array after | swapped |
|---|---|---|---|
| 1 (rdx = 2) | (3,1) swap, (3,2) swap | 1 2 3 | yes |
| 2 (rdx = 1) | (1,2) | 1 2 3 | no → stop |

## Complexity

O(n²) time worst case, O(n) when already sorted; O(1) space.

## Common mistakes

* **Storing both registers to the same slot**, which duplicates a value.
* **Unsigned `jbe`**: negative numbers sort after positive ones.
* **`cmpq %rax, %r10`** reverses the test: the array ends up sorted descending.""",
    ),
), [("ldp x5, x6, [x3]", "load the adjacent pair cursor[0] and cursor[1] into x5 and x6 with one pair load"),
    ("b.le Lnoswap", "skip the swap if x5 <= x6 (signed)"),
    ("stp x6, x5, [x3]", "store the pair back in swapped order with one pair store")])

# ---------------------------------------------------------------- 22. recursive fib
_add(dict(
    id="asm-recursive-fibonacci",
    title="Recursive Fibonacci with a Stack Frame",
    difficulty=4,
    tags=["recursion", "stack", "calling convention", "callee-saved"],
    fn="fib_recursive",
    params=[["n", "int"]],
    returns="int",
    statement="""Compute `F(n)` **recursively**: `F(n) = n` for `n < 2`, otherwise
`F(n) = F(n−1) + F(n−2)`, by calling `_fib_recursive` from itself with `bl`.

**On entry:** `x0 = n`.
**On exit:** `x0 = F(n)`.

Because your function calls a function, you must build a proper **stack frame**: save
the return address (`x30`) and frame pointer (`x29`), and keep values that must
survive a call in callee-saved registers (`x19`, `x20`), which you must save and
restore too. The starter's frame is 32 bytes:

```text
[sp, #0]  x29    [sp, #8]  x30
[sp, #16] x19    [sp, #24] x20
```""",
    constraints=["0 ≤ n ≤ 24"],
    hints=[
        "`bl` overwrites `x30`. Save `x29`/`x30` first with a pre-indexed pair store that also allocates the 32-byte frame: `stp x29, x30, [sp, #-32]!`.",
        "`x19` and `x20` belong to your caller (which might be yourself one level up): store them at `[sp, #16]` before you change them.",
        "After the first call, `fib(n−1)` is in `x0`, and the next call will clobber it. Copy it into `x20`. Undo the frame at the end with `ldp x29, x30, [sp], #32`.",
    ],
    solution='''def fib_recursive(n):
    # Base case: handled before any frame is built (a "leaf" path).
    if n < 2:                       # cmp x0, #2 ; b.lt Lbase
        return n
    # x19 keeps n alive across the first call; x20 keeps fib(n-1) alive
    # across the second call. Both are callee-saved, so they must be
    # saved in our frame and restored before we return.
    first = fib_recursive(n - 1)    # bl ; mov x20, x0
    second = fib_recursive(n - 2)   # bl ; result in x0
    return first + second           # add x0, x20, x0
''',
    asm_solution="""// long long fib_recursive(long long n)
// On entry: x0 = n       On exit: x0 = F(n)
.text                          // code section
.globl _fib_recursive          // export the symbol
.p2align 2                     // 4-byte alignment
_fib_recursive:                // function entry
    cmp x0, #2                 // n < 2 ?
    b.lt Lbase                 // base case: F(n) = n, already in x0
    stp x29, x30, [sp, #-32]!  // sp -= 32; save frame pointer and return address at [sp]
    mov x29, sp                // x29 = this frame
    stp x19, x20, [sp, #16]    // save the caller's x19 and x20 (callee-saved)
    mov x19, x0                // x19 = n (survives the calls)
    sub x0, x19, #1            // argument n - 1
    bl _fib_recursive          // x0 = F(n-1); x30 is overwritten (but saved)
    mov x20, x0                // x20 = F(n-1) (survives the next call)
    sub x0, x19, #2            // argument n - 2
    bl _fib_recursive          // x0 = F(n-2)
    add x0, x20, x0            // x0 = F(n-1) + F(n-2)
    ldp x19, x20, [sp, #16]    // restore the caller's x19 and x20
    ldp x29, x30, [sp], #32    // restore fp and return address; sp += 32
Lbase:                         // both paths return from here
    ret                        // jump to x30
""",
    tests=[[3], [0], [1], [2], [10], [20], [24]],
    explanation="""## Intuition

A recursive call is an ordinary `bl`, and `bl` does two things that would destroy a
naive function: it **overwrites `x30`** (your own return address) and the callee is
free to **trash `x0`–`x17`**. So anything you need after the call must live either on
the stack or in a callee-saved register (`x19`–`x28`), and every callee-saved register
you touch must itself be saved and restored, because your caller (here: another copy
of you) is relying on it.

## Approach

**Prologue.** `stp x29, x30, [sp, #-32]!` is a *pre-indexed* pair store: `sp -= 32`
first, then store `x29` at `[sp]` and `x30` at `[sp + 8]`. One instruction allocates
the frame and saves the return address. `mov x29, sp` links the new frame (debuggers
and crash reports walk the chain of `x29`s). `stp x19, x20, [sp, #16]` saves the two
callee-saved registers in the other half of the frame.

**Body.** `x19 = n`, call with `n − 1`, park the result in `x20`, call with `n − 2`,
add.

**Epilogue.** Restore in reverse: `x19`/`x20`, then `ldp x29, x30, [sp], #32`
(post-indexed: load, then `sp += 32`), then `ret` uses the restored `x30`.

Trace for `n = 3` (frames indented by depth):

| call | x0 in | action | x19 | x20 | x0 out |
|---|---|---|---|---|---|
| fib(3) | 3 | frame A, x19 = 3, call fib(2) | 3 | (caller's) | |
| · fib(2) | 2 | frame B, x19 = 2, call fib(1) | 2 | | |
| · · fib(1) | 1 | base case, `ret` (no frame) | 2 | | 1 |
| · fib(2) | | x20 = 1, call fib(0) | 2 | 1 | |
| · · fib(0) | 0 | base case | | | 0 |
| · fib(2) | | x0 = 1 + 0, restore x19 = 3, x20 = (caller's) | 3 | | 1 |
| fib(3) | | x20 = 1, call fib(1) | 3 | 1 | |
| · fib(1) | 1 | base case | | | 1 |
| fib(3) | | x0 = 1 + 1, restore, `ret` | | | **2** |

Notice how fib(2) restoring `x19 = 3` is exactly what lets fib(3) compute `n − 2`
correctly afterwards.

The base case returns before building a frame. That is legal because it calls nothing
and touches no callee-saved register: a **leaf** path needs no frame.

## Complexity

O(φⁿ) calls (about 75 000 for n = 24), O(n) stack depth × 32 bytes.

## Common mistakes

* **Not saving `x30`**: the first `bl` replaces it with an address inside your own
  function, so the final `ret` jumps back into the middle of the body: an infinite loop
  or a crash.
* **Keeping `n` or `F(n−1)` in `x1`–`x17`** across a call: the callee clobbers them.
* **Using `x19`/`x20` without saving them**: the inner call overwrites the outer
  call's `n`, giving wrong answers that only appear for `n ≥ 3`.
* **Misaligned `sp`**: `sub sp, sp, #24` violates the 16-byte rule; Apple Silicon
  faults on the next `sp`-relative access. Always allocate multiples of 16.
* **Restoring in the wrong order** (`ldp x29, x30, [sp], #32` first) frees the frame,
  then reads `x19`/`x20` from memory that no longer belongs to you.
* **Unbalanced paths**: every path that ran the prologue must run the epilogue.

## Going further

Make it fast without changing the recursion shape: pass an accumulator pair
(`fib_helper(n, a, b)`) so the recursive call is the **last** thing the function does.
Then the call can become a plain `b` (a tail call) and needs no frame at all: you have
rediscovered the iterative loop from *Fibonacci (Iterative)*.""",
    x86=dict(
        solution="""# long long fib_recursive(long long n)
# On entry: rdi = n       On exit: rax = F(n)
.text                          # code section
.globl _fib_recursive          # export the symbol
.p2align 4                     # 16-byte alignment
_fib_recursive:                # function entry (rsp = 8 mod 16: call pushed the return address)
    cmpq $2, %rdi              # n < 2 ?
    jl Lbase                   # base case: F(n) = n
    pushq %rbp                 # save the caller's frame pointer
    movq %rsp, %rbp            # rbp = this frame
    pushq %rbx                 # save the caller's rbx (callee-saved)
    pushq %r12                 # save the caller's r12; rsp is now 16-byte aligned again
    movq %rdi, %rbx            # rbx = n (survives the calls)
    leaq -1(%rbx), %rdi        # argument n - 1
    callq _fib_recursive       # rax = F(n-1); rdi, rcx, ... may be clobbered
    movq %rax, %r12            # r12 = F(n-1) (survives the next call)
    leaq -2(%rbx), %rdi        # argument n - 2
    callq _fib_recursive       # rax = F(n-2)
    addq %r12, %rax            # rax = F(n-1) + F(n-2)
    popq %r12                  # restore the caller's r12 (pops mirror the pushes)
    popq %rbx                  # restore the caller's rbx
    popq %rbp                  # restore the caller's frame pointer
    ret                        # return F(n)
Lbase:                         # n < 2
    movq %rdi, %rax            # F(n) = n
    ret                        # return
""",
        todos=[("pushq %rbp", "save the caller's frame pointer on the stack"),
               ("pushq %rbx", "save the caller's callee-saved rbx before you use it"),
               ("movq %rax, %r12", "keep F(n-1) (currently in rax) safe in the callee-saved register r12"),
               ("popq %rbx", "restore the caller's rbx (restores come in reverse order of the saves)")],
        notes="""**On entry:** `%rdi = n`. **On exit:** `%rax = F(n)`.

`call` pushes the return address and `ret` pops it, so there is no link register to
save. What you must preserve is any **callee-saved** register you use (`%rbx`, `%rbp`,
`%r12`–`%r15`), with `pushq`/`popq` in mirror order. Alignment rule: `%rsp` must be a
multiple of 16 at each `call`. On entry it is 8 off (the return address), so the
number of 8-byte pushes before a call must be **odd**.""",
        hints=[
            "Prologue: save `%rbp` and point it at the frame, then save the two callee-saved registers you will use. Three pushes plus the return address keep `%rsp` 16-aligned.",
            "`n` lives in `%rbx` across both calls; `F(n-1)` needs another callee-saved register (`%r12`). Pops run in reverse order of pushes.",
            "`pushq %rbp`, `pushq %rbx`, `movq %rax, %r12`, `popq %rbx`",
        ],
        explanation="""## Intuition

F(n) = F(n−1) + F(n−2). Each call needs `n` and `F(n−1)` to survive a nested call, so
they live in callee-saved registers, which the function must itself save and restore.

## Approach

Stack after the prologue (growing down):

```text
   +----------------------+
   | return address       |  rsp+24   (pushed by call)
   | caller's rbp         |  rsp+16   <- rbp points here
   | caller's rbx         |  rsp+8
   | caller's r12         |  rsp+0    (16-byte aligned)
   +----------------------+
```

| call | rbx | r12 | rax on return |
|---|---|---|---|
| fib(3) | 3 | F(2) = 1 | 1 + F(1) = **2** |
| └ fib(2) | 2 | F(1) = 1 | 1 + F(0) = 1 |

## Complexity

O(φⁿ) time (exponential), O(n) stack depth.

## Common mistakes

* **Even number of pushes before `call`**: `%rsp` is misaligned; macOS code that uses
  aligned SSE stores (e.g. `printf`) then crashes. Count: return address + pushes.
* **Popping in push order**: the caller's `%rbx` and `%r12` get swapped.
* **Keeping `n` in `%rdi` or `%rcx`**: those are caller-saved and the call clobbers them.
* **Unbalanced paths**: the base case must not run the epilogue, because it never ran
  the prologue.""",
    ),
), [("stp x29, x30, [sp, #-32]!", "allocate a 32-byte frame and save x29 and x30 at its bottom with one pre-indexed pair store"),
    ("stp x19, x20, [sp, #16]", "save the caller's callee-saved registers x19 and x20 in the upper half of the frame"),
    ("mov x20, x0", "keep F(n-1) (currently in x0) safe in the callee-saved register x20"),
    ("ldp x29, x30, [sp], #32", "restore x29 and x30 and release the 32-byte frame with one post-indexed pair load")])
