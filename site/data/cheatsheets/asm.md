# ARM64 assembly cheat sheet

Quick reference for Crucible's assembly problems: **AArch64 on macOS (Apple Silicon)**,
assembled with `clang`. Comments start with `//`. Every snippet here was assembled and
run on an M-series Mac.

## How Crucible calls your function

The harness is C code that calls your function `_<fn>` (macOS prefixes C symbols with an
underscore). It follows the standard ARM64 calling convention:

| Crucible type | arrives in | notes |
|---|---|---|
| `int` | one `x` register | 64-bit signed (`long long`) |
| `int[]` | **two** registers: pointer, then count | elements are 8 bytes each; count is 64-bit |
| `str` | one register: `const char*` | NUL-terminated bytes |
| return `int` | `x0` | |
| `void` + mutates | write through the array pointer | |

Parameters fill `x0`, `x1`, … `x7` in order. `f(nums: int[], target: int)` gets
`x0 = nums`, `x1 = count`, `x2 = target`.

```asm
.text
.globl _sum_array            // export the symbol
.p2align 2                   // instructions are 4 bytes; align the function
_sum_array:                  // long long sum_array(long long* x0, long long x1)
    mov     x2, #0           // running sum
1:  cbz     x1, 2f           // no elements left? jump forward to label 2
    ldr     x3, [x0], #8     // load *x0, then x0 += 8 (post-index)
    add     x2, x2, x3
    sub     x1, x1, #1
    b       1b               // jump back to label 1
2:  mov     x0, x2           // return value goes in x0
    ret                      // return to the address in x30 (lr)
```

Numeric labels (`1:`) can be reused; `1b` / `1f` mean "nearest label 1 backward /
forward".

## Registers

| register | role | preserved across calls? |
|---|---|---|
| `x0`–`x7` | arguments and return values (`x0`, `x1`) | no (caller-saved) |
| `x8` | indirect result location (large struct returns) | no |
| `x9`–`x15` | temporaries | no |
| `x16`, `x17` | intra-procedure-call scratch (the linker may use them) | no |
| `x18` | **platform register: reserved on macOS, never touch** | n/a |
| `x19`–`x28` | callee-saved: save them before use, restore before `ret` | **yes** |
| `x29` (`fp`) | frame pointer | yes |
| `x30` (`lr`) | link register: the return address, set by `bl` | yes (save it if you call anything) |
| `sp` | stack pointer, must stay **16-byte aligned** | yes |
| `xzr` / `wzr` | reads as zero, writes are discarded | n/a |

`wN` is the low 32 bits of `xN`. Writing a `w` register **zeroes** the upper 32 bits.
Use `x` registers for Crucible's 64-bit ints. Floats live in `d0`–`d31` (`s` for 32-bit),
args in `d0`–`d7`; `d8`–`d15` are callee-saved.

A leaf function (one that calls nothing) can use `x0`–`x15` freely and needs no stack
frame at all.

## Data movement

| instruction | effect |
|---|---|
| `mov x0, x1` | copy register |
| `mov x0, #42` | small immediate (also `#-1`) |
| `movz x0, #0x1234, lsl #16` / `movk x0, #0x5678` | build a wide constant 16 bits at a time |
| `ldr x0, =0x123456789` | assembler loads any 64-bit constant (from a literal pool) |
| `neg x0, x1` | `x0 = -x1` |
| `mvn x0, x1` | `x0 = ~x1` |
| `csel x0, x1, x2, lt` | `x0 = (lt) ? x1 : x2` (after a `cmp`) |
| `cset x0, eq` | `x0 = (eq) ? 1 : 0` |
| `cinc x0, x1, gt` | `x0 = (gt) ? x1 + 1 : x1` |
| `adr x0, label` / `adrp x0, sym@PAGE` + `add x0, x0, sym@PAGEOFF` | address of a label / of data in another section |

## Arithmetic

| instruction | effect |
|---|---|
| `add x0, x1, x2` / `add x0, x1, #4` | addition (immediates 0…4095, optionally `lsl #12`) |
| `sub x0, x1, x2` | subtraction |
| `adds` / `subs` | same, but also set the flags |
| `mul x0, x1, x2` | low 64 bits of the product |
| `madd x0, x1, x2, x3` | `x0 = x3 + x1 * x2` |
| `msub x0, x1, x2, x3` | `x0 = x3 - x1 * x2` (remainder helper) |
| `smulh x0, x1, x2` | high 64 bits of the signed 128-bit product (overflow check) |
| `sdiv x0, x1, x2` | signed divide, **truncates toward zero**; divide by 0 gives 0 (no trap) |
| `udiv x0, x1, x2` | unsigned divide |
| `add x0, x1, x2, lsl #3` | `x0 = x1 + (x2 << 3)`: index × 8 in one instruction |

There is no remainder instruction:

```asm
.text
.globl _rem
.p2align 2
_rem:                         // long long rem(long long a, long long b): a % b like C
    sdiv    x2, x0, x1        // q = a / b (truncated)
    msub    x0, x2, x1, x0    // a - q * b
    ret
```

## Logic & shifts

| instruction | effect |
|---|---|
| `and x0, x1, x2` / `and x0, x1, #0xff` | bitwise AND (immediates must be "bitmask" patterns) |
| `orr`, `eor` | OR, XOR |
| `bic x0, x1, x2` | `x1 & ~x2` |
| `tst x1, #1` | `ands xzr, x1, #1`: set flags only (is the low bit set?) |
| `lsl x0, x1, #3` | shift left (×8) |
| `lsr x0, x1, #1` | logical shift right (unsigned ÷2) |
| `asr x0, x1, #1` | arithmetic shift right (keeps the sign; floors, unlike `sdiv`) |
| `ror x0, x1, #8` | rotate right |
| `clz x0, x1` | count leading zeros |
| `rbit x0, x1` + `clz` | count trailing zeros |
| `cnt` | popcount exists only on SIMD registers; loop with `and`/`lsr` instead |

## Compare & branch

`cmp a, b` computes `a − b` and sets the **NZCV** flags; a conditional branch `b.<cond>`
then tests them.

| cond | meaning after `cmp a, b` | flags |
|---|---|---|
| `eq` | `a == b` | Z = 1 |
| `ne` | `a != b` | Z = 0 |
| `lt` | `a < b` (signed) | N ≠ V |
| `le` | `a <= b` (signed) | Z = 1 or N ≠ V |
| `gt` | `a > b` (signed) | Z = 0 and N = V |
| `ge` | `a >= b` (signed) | N = V |
| `lo` (`cc`) | `a < b` (unsigned) | C = 0 |
| `ls` | `a <= b` (unsigned) | C = 0 or Z = 1 |
| `hi` | `a > b` (unsigned) | C = 1 and Z = 0 |
| `hs` (`cs`) | `a >= b` (unsigned) | C = 1 |
| `mi` / `pl` | negative / non-negative result | N = 1 / N = 0 |
| `vs` / `vc` | signed overflow / none | V = 1 / V = 0 |

| instruction | effect |
|---|---|
| `b label` | unconditional jump |
| `b.lt label` | jump if the condition holds |
| `cbz x0, label` / `cbnz x0, label` | jump if `x0` is zero / non-zero (no `cmp` needed) |
| `tbz x0, #3, label` / `tbnz` | jump if bit 3 of `x0` is zero / one |
| `cmp x0, #10` / `cmn x0, #5` | compare with an immediate / with its negation |
| `bl func` | call: `x30 = return address`, jump to `func` |
| `ret` | return to `x30` |

## Load / store & addressing modes

| syntax | address used | side effect |
|---|---|---|
| `ldr x0, [x1]` | `x1` | |
| `ldr x0, [x1, #16]` | `x1 + 16` | |
| `ldr x0, [x1, x2, lsl #3]` | `x1 + x2 * 8` (array index) | |
| `ldr x0, [x1, #8]!` | `x1 + 8` | pre-index: `x1 += 8` first |
| `ldr x0, [x1], #8` | `x1` | post-index: `x1 += 8` after |
| `ldp x2, x3, [x1]` / `stp` | pair of registers at `x1`, `x1 + 8` | |

| size | load | load signed | store |
|---|---|---|---|
| 8 bytes | `ldr x0` | | `str x0` |
| 4 bytes | `ldr w0` | `ldrsw x0` | `str w0` |
| 2 bytes | `ldrh w0` | `ldrsh x0` | `strh w0` |
| 1 byte (chars) | `ldrb w0` | `ldrsb x0` | `strb w0` |

```asm
.text
.globl _str_len
.p2align 2
_str_len:                       // long long str_len(const char* x0)
    mov     x1, x0              // remember the start
1:  ldrb    w2, [x0], #1        // load a byte, advance the pointer
    cbnz    w2, 1b              // until the NUL terminator
    sub     x0, x0, x1          // (end + 1) - start ...
    sub     x0, x0, #1          // ... minus the NUL
    ret
```

## Stack frame template (non-leaf functions)

Needed when you call another function (`bl` overwrites `x30`) or need `x19`–`x28`.

```asm
.text
.globl _sum_sq
.p2align 2
_square:                         // helper: x0 = x0 * x0
    mul     x0, x0, x0
    ret

_sum_sq:                         // long long sum_sq(long long* x0, long long x1)
    stp     x29, x30, [sp, #-48]!    // push fp and lr; reserve 48 bytes (multiple of 16)
    mov     x29, sp                  // set up the frame pointer
    stp     x19, x20, [sp, #16]      // save callee-saved registers we use
    str     x21, [sp, #32]

    mov     x19, x0                  // x19 = pointer   (survives bl)
    mov     x20, x1                  // x20 = count
    mov     x21, #0                  // x21 = total
1:  cbz     x20, 2f
    ldr     x0, [x19], #8
    bl      _square                  // clobbers x0-x17 and x30
    add     x21, x21, x0
    sub     x20, x20, #1
    b       1b
2:  mov     x0, x21

    ldr     x21, [sp, #32]           // restore in reverse
    ldp     x19, x20, [sp, #16]
    ldp     x29, x30, [sp], #48      // pop fp and lr, release the frame
    ret
```

Rules: `sp` stays a multiple of 16; save `x29`/`x30` first; restore exactly what you
saved; locals live at `[sp, #offset]` inside the frame.

## Loop templates

Counted loop over an `int[]` with an index (useful when you need `i` itself):

```asm
.text
.globl _count_greater
.p2align 2
_count_greater:                 // long long count_greater(long long* a, long long n, long long t)
    mov     x3, #0              // i
    mov     x4, #0              // count
1:  cmp     x3, x1              // while (i < n)
    b.ge    2f
    ldr     x5, [x0, x3, lsl #3]    // a[i]
    cmp     x5, x2
    cinc    x4, x4, gt          // count += (a[i] > t)
    add     x3, x3, #1
    b       1b
2:  mov     x0, x4
    ret
```

Two pointers moving toward each other (in-place reverse, a `void` + mutates problem):

```asm
.text
.globl _reverse
.p2align 2
_reverse:                       // void reverse(long long* a, long long n)
    cbz     x1, 2f
    add     x1, x0, x1, lsl #3  // x1 = one past the end
    sub     x1, x1, #8          // x1 = &a[n-1]
1:  cmp     x0, x1
    b.hs    2f                  // stop when the pointers meet (unsigned compare)
    ldr     x2, [x0]
    ldr     x3, [x1]
    str     x3, [x0], #8
    str     x2, [x1], #-8
    b       1b
2:  ret
```

Max of an array (non-empty), branch-free with `csel`:

```asm
.text
.globl _max_of
.p2align 2
_max_of:                        // long long max_of(long long* a, long long n), n >= 1
    ldr     x2, [x0], #8        // best = a[0]
    subs    x1, x1, #1          // remaining = n - 1, sets flags
    b.eq    2f
1:  ldr     x3, [x0], #8
    cmp     x3, x2
    csel    x2, x3, x2, gt      // best = (x3 > best) ? x3 : best
    subs    x1, x1, #1
    b.ne    1b
2:  mov     x0, x2
    ret
```

## C ↔ assembly cheat table

| C | ARM64 |
|---|---|
| `x = a + b * c` | `madd xd, xb, xc, xa` |
| `if (a < b) goto L` | `cmp xa, xb` / `b.lt L` |
| `x = a < b ? a : b` | `cmp xa, xb` / `csel xd, xa, xb, lt` |
| `x = (a == b)` | `cmp xa, xb` / `cset xd, eq` |
| `p[i]` (8-byte) | `ldr xd, [xp, xi, lsl #3]` |
| `*p++` | `ldr xd, [xp], #8` |
| `s[i]` (char) | `ldrb wd, [xs, xi]` |
| `a / 2` (signed, C semantics) | `sdiv` (or `asr` only when `a >= 0`) |
| `a % b` | `sdiv` + `msub` |
| `return x` | `mov x0, x` / `ret` |

## Common gotchas

- `x18` is reserved on Apple platforms. Don't use it.
- Forgetting the leading underscore: the symbol must be `_fn`, exported with `.globl _fn`.
- Calling another function without saving `x30` makes `ret` loop forever or crash.
- Array elements are 8 bytes: scale indices with `lsl #3` (or advance pointers by 8).
- `sp` misaligned (not a multiple of 16) faults on the next memory access through it.
- `cmp` + the wrong condition family: `lt`/`gt` are signed, `lo`/`hi` unsigned.
- Values in `x0`–`x17` are destroyed by any `bl`. Keep them in `x19`–`x28` (saved) instead.
- Writing `w` registers zeroes the top half: `add w0, w0, #1` loses the upper 32 bits.
- Immediates are limited: `add` takes 0–4095, logical ops only take bitmask patterns. Put
  other constants in a register first (`mov` / `movk` / `ldr =`).
- `sdiv` by zero returns 0 instead of trapping, so check the divisor yourself if it matters.
