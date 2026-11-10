// ARM64 (AArch64, Apple Silicon macOS, clang) reference for Crucible's editor (hover / completion / signature help).
const ins = (name, sig, doc, example, insert) => ({ name, kind: 'instruction', sig, doc, ...(example ? { example } : {}), ...(insert ? { insert } : {}) });
const dir = (name, sig, doc, example, insert) => ({ name, kind: 'directive', sig, doc, ...(example ? { example } : {}), ...(insert ? { insert } : {}) });
const reg = (name, sig, doc) => ({ name, kind: 'constant', sig, doc });

const CC = 'Calling convention (AAPCS64, Apple): args in `x0`–`x7`, return in `x0`; `x9`–`x15` scratch; `x19`–`x28` callee-saved; `x29` fp, `x30` lr; `sp` 16-byte aligned.';

const conds = [
  ['eq', 'equal (Z=1)', 'after `cmp a, b`: a == b'],
  ['ne', 'not equal (Z=0)', 'a != b'],
  ['lt', 'signed less than (N!=V)', 'a < b, signed'],
  ['le', 'signed less or equal (Z=1 or N!=V)', 'a <= b, signed'],
  ['gt', 'signed greater than (Z=0 and N=V)', 'a > b, signed'],
  ['ge', 'signed greater or equal (N=V)', 'a >= b, signed'],
  ['lo', 'unsigned lower (C=0), alias `b.cc`', 'a < b, unsigned (e.g. index < count, pointer < end)'],
  ['hs', 'unsigned higher or same (C=1), alias `b.cs`', 'a >= b, unsigned'],
  ['hi', 'unsigned higher (C=1 and Z=0)', 'a > b, unsigned'],
  ['ls', 'unsigned lower or same (C=0 or Z=1)', 'a <= b, unsigned'],
  ['mi', 'minus / negative (N=1)', 'result < 0'],
  ['pl', 'plus / positive or zero (N=0)', 'result >= 0'],
];

const regs = [];
for (let i = 0; i <= 30; i++) {
  let role;
  if (i === 0) role = '1st argument **and the return value** (`x0`/`w0`). Caller-saved: any `bl` may clobber it.';
  else if (i <= 7) role = `Argument register #${i + 1}. Caller-saved. For an \`int[]\` parameter Crucible passes pointer then count in consecutive registers (e.g. \`x0\` = pointer, \`x1\` = count).`;
  else if (i === 8) role = 'Indirect result location register (pointer for large struct returns). Otherwise a caller-saved scratch register.';
  else if (i <= 15) role = 'Temporary / scratch register. Caller-saved: free to use without saving, but clobbered by any `bl`.';
  else if (i <= 17) role = `\`ip${i - 16}\` intra-procedure-call scratch register: the linker's veneers/stubs may clobber it across a call. OK as a short-lived temp.`;
  else if (i === 18) role = '**Reserved on Apple platforms** (platform register). Never use or modify `x18` on macOS.';
  else if (i <= 28) role = 'Callee-saved: if your function writes it you must save it in the prologue (`stp x19, x20, [sp, #-16]!`) and restore it before `ret`. Survives calls you make.';
  else if (i === 29) role = 'Frame pointer (`fp`). Callee-saved; Apple requires a valid frame chain: `stp x29, x30, [sp, #-16]!` then `mov x29, sp`.';
  else role = 'Link register (`lr`): `bl` writes the return address here and `ret` jumps to it. **A `bl` overwrites it**, so any non-leaf function must save `x30` (with `x29`) first.';
  regs.push(reg(`x${i}`, `x${i} (64-bit) / w${i} (low 32 bits)`, role));
}

export default [
  // ---------- moves ----------
  ins('mov', 'mov Xd, Xn | mov Xd, #imm | mov Xd, sp', 'Copy a register or load an immediate. The assembler picks `movz`/`movn`/`orr` for immediates; arbitrary 64-bit constants may need `movz` + `movk`. Writing a `w` register **zero-extends** into the full `x` register.', 'mov x9, #0\nmov x0, x19', 'mov ${1:x0}, ${2:x1}'),
  ins('movz', 'movz Xd, #imm16{, lsl #16|32|48}', 'Move a 16-bit immediate (optionally shifted), zeroing the rest.', 'movz x0, #0x1234, lsl #16'),
  ins('movk', 'movk Xd, #imm16{, lsl #16|32|48}', 'Insert a 16-bit immediate into one halfword, **keeping** the other bits. Pair with `movz` to build large constants.', 'movz x0, #0xBEEF\nmovk x0, #0xDEAD, lsl #16   // x0 = 0xDEADBEEF'),
  ins('movn', 'movn Xd, #imm16{, lsl #s}', 'Move the bitwise NOT of a shifted 16-bit immediate (for negative constants). `mov x0, #-1` assembles to this.'),
  ins('mvn', 'mvn Xd, Xm{, shift #n}', 'Bitwise NOT: `Xd = ~Xm` (alias of `orn Xd, xzr, Xm`).'),
  ins('neg', 'neg Xd, Xm{, shift #n}', 'Negate: `Xd = -Xm` (alias of `sub Xd, xzr, Xm`). `negs` also sets flags.'),

  // ---------- arithmetic ----------
  ins('add', 'add Xd, Xn, Xm{, lsl #n} | add Xd, Xn, #imm12{, lsl #12} | add Xd, Xn, Wm, sxtw', '`Xd = Xn + op2`. Immediate is 0–4095 (optionally `lsl #12`). Shifted register form is great for addressing: `add x9, x0, x1, lsl #3` = `&a[i]` for 8-byte elements. Does **not** set flags.', 'add x0, x0, x1\nadd x9, x0, x2, lsl #3   // x9 = &arr[i]', 'add ${1:x0}, ${2:x0}, ${3:x1}'),
  ins('adds', 'adds Xd, Xn, op2', 'Add and set flags N Z C V (C = unsigned carry out, V = signed overflow).'),
  ins('sub', 'sub Xd, Xn, Xm{, lsl #n} | sub Xd, Xn, #imm12', '`Xd = Xn - op2`. Does not set flags. Stack allocation: `sub sp, sp, #32` (keep `sp` 16-byte aligned).', 'sub x1, x1, #1', 'sub ${1:x0}, ${2:x0}, ${3:x1}'),
  ins('subs', 'subs Xd, Xn, op2', 'Subtract and set flags; `cmp` is `subs xzr, ...`. Lets you decrement-and-test: `subs x1, x1, #1` then `b.ne loop`.', 'subs x1, x1, #1\nb.ne loop'),
  ins('mul', 'mul Xd, Xn, Xm', '`Xd = Xn * Xm` (low 64 bits; alias of `madd Xd, Xn, Xm, xzr`). **Registers only, no immediate**: `mov` the constant first. `smulh`/`umulh` give the high 64 bits.', 'mov x9, #10\nmul x0, x0, x9'),
  ins('madd', 'madd Xd, Xn, Xm, Xa', 'Multiply-add: `Xd = Xa + Xn * Xm`. E.g. `num = num*10 + digit` in one instruction.', 'madd x0, x0, x9, x10   // x0 = x10 + x0*x9'),
  ins('msub', 'msub Xd, Xn, Xm, Xa', 'Multiply-subtract: `Xd = Xa - Xn * Xm`. Remainder idiom: `sdiv q, a, b` then `msub r, q, b, a` (r = a - q*b).', 'sdiv x2, x0, x1\nmsub x3, x2, x1, x0    // x3 = x0 % x1'),
  ins('smull', 'smull Xd, Wn, Wm', 'Signed 32x32 -> 64-bit multiply.'),
  ins('smulh', 'smulh Xd, Xn, Xm', 'High 64 bits of the signed 128-bit product (`umulh` for unsigned).'),
  ins('sdiv', 'sdiv Xd, Xn, Xm', 'Signed divide, truncating toward zero. **Division by zero returns 0 (no trap)**. There is no remainder instruction: use `msub`.'),
  ins('udiv', 'udiv Xd, Xn, Xm', 'Unsigned divide. Divide by zero yields 0.'),

  // ---------- logic / shifts ----------
  ins('and', 'and Xd, Xn, Xm{, shift #n} | and Xd, Xn, #bitmask', 'Bitwise AND. Immediates must be a "bitmask immediate" (repeating run of 1s, e.g. `#0xff`, `#1`); others must be put in a register. `ands`/`tst` set flags.', 'and x9, x0, #1   // x9 = x0 & 1 (odd?)'),
  ins('ands', 'ands Xd, Xn, op2', 'AND and set N/Z flags (C, V cleared).'),
  ins('orr', 'orr Xd, Xn, Xm{, shift #n} | orr Xd, Xn, #bitmask', 'Bitwise OR. `orr Xd, xzr, Xm` is a register move.'),
  ins('eor', 'eor Xd, Xn, Xm{, shift #n} | eor Xd, Xn, #bitmask', 'Bitwise XOR. XOR-of-all finds the single unpaired number.', 'eor x0, x0, x9'),
  ins('bic', 'bic Xd, Xn, Xm', 'Bit clear: `Xd = Xn & ~Xm`.'),
  ins('lsl', 'lsl Xd, Xn, #imm | lsl Xd, Xn, Xm', 'Logical shift left (`x << n`). Register shift amount is taken modulo 64.', 'lsl x9, x1, #3   // x9 = i * 8'),
  ins('lsr', 'lsr Xd, Xn, #imm | lsr Xd, Xn, Xm', 'Logical shift right (zero-fill): unsigned divide by a power of two.'),
  ins('asr', 'asr Xd, Xn, #imm | asr Xd, Xn, Xm', 'Arithmetic shift right (sign-fill). Rounds toward **−infinity**, unlike `sdiv` which truncates toward zero.'),
  ins('ror', 'ror Xd, Xn, #imm | ror Xd, Xn, Xm', 'Rotate right.'),
  ins('clz', 'clz Xd, Xn', 'Count leading zero bits (64 for 0). Bit length = 64 − clz.'),
  ins('rbit', 'rbit Xd, Xn', 'Reverse bit order. Count trailing zeros = `rbit` then `clz`.', 'rbit x9, x0\nclz x0, x9   // x0 = ctz(x0)'),
  ins('rev', 'rev Xd, Xn', 'Reverse byte order (endianness swap). `rev32`/`rev16` swap within words/halfwords.'),
  ins('cnt', 'cnt Vd.8B, Vn.8B', 'SIMD per-byte popcount; no scalar popcount on base ARMv8. Popcount: `fmov d0, x0; cnt v0.8b, v0.8b; addv b0, v0.8b; fmov w0, s0`.'),
  ins('sxtw', 'sxtw Xd, Wn', 'Sign-extend a 32-bit value to 64 bits (C `int` -> `long`).'),
  ins('sxtb', 'sxtb Xd, Wn', 'Sign-extend the low byte (`sxth` for halfword).'),
  ins('uxtb', 'uxtb Wd, Wn', 'Zero-extend the low byte (= `and w, w, #0xff`). `uxth` for halfword. For 32->64 zero-extension just `mov w, w`.'),
  ins('ubfx', 'ubfx Xd, Xn, #lsb, #width', 'Extract an unsigned bitfield: `(Xn >> lsb) & ((1<<width)-1)`. `sbfx` sign-extends.'),
  ins('bfi', 'bfi Xd, Xn, #lsb, #width', 'Insert the low `width` bits of Xn into Xd at `lsb`.'),

  // ---------- compare / conditional ----------
  ins('cmp', 'cmp Xn, Xm | cmp Xn, #imm12', 'Compare: computes `Xn - op2`, sets flags, discards the result (alias of `subs xzr`). Follow with `b.<cond>`, `csel`, `cset`. Operand order matters: `cmp x0, x1; b.lt` jumps if x0 < x1.', 'cmp x0, x1\nb.ge done', 'cmp ${1:x0}, ${2:x1}'),
  ins('cmn', 'cmn Xn, Xm | cmn Xn, #imm12', 'Compare negative: flags from `Xn + op2`. Use `cmn x0, #1` to compare with −1.'),
  ins('tst', 'tst Xn, Xm | tst Xn, #bitmask', 'Test bits: flags from `Xn & op2` (alias of `ands xzr`). `tst x0, #1; b.ne odd`.'),
  ins('ccmp', 'ccmp Xn, op2, #nzcv, cond', 'Conditional compare: if `cond` holds, compare; else set flags to `#nzcv`. Builds `a && b` conditions without branches.'),
  ins('csel', 'csel Xd, Xn, Xm, cond', 'Conditional select: `Xd = cond ? Xn : Xm`. Branchless max: `cmp x0, x1; csel x0, x0, x1, gt`.', 'cmp x0, x1\ncsel x0, x0, x1, gt   // max'),
  ins('csinc', 'csinc Xd, Xn, Xm, cond', '`Xd = cond ? Xn : Xm + 1`. Conditional increment: `cinc x0, x0, eq`.'),
  ins('cinc', 'cinc Xd, Xn, cond', '`Xd = cond ? Xn + 1 : Xn`. Counting: `cmp x9, #0; cinc x0, x0, eq`.'),
  ins('csneg', 'csneg Xd, Xn, Xm, cond', '`Xd = cond ? Xn : -Xm`.'),
  ins('cneg', 'cneg Xd, Xn, cond', '`Xd = cond ? -Xn : Xn`. Absolute value: `cmp x0, #0; cneg x0, x0, lt`.', 'cmp x0, #0\ncneg x0, x0, lt   // abs'),
  ins('cset', 'cset Wd, cond', '`Wd = cond ? 1 : 0` (alias of `csinc Wd, wzr, wzr, !cond`). Return a bool from a comparison.', 'cmp x0, x1\ncset x0, eq'),
  ins('csetm', 'csetm Xd, cond', '`Xd = cond ? -1 : 0` (all ones).'),

  // ---------- branches ----------
  ins('b', 'b label', 'Unconditional branch (±128 MB).', 'b loop', 'b ${1:label}'),
  ...conds.map(([c, meaning, use]) => ins(`b.${c}`, `b.${c} label`, `Branch if ${meaning}: ${use}. Flags come from the last flag-setting instruction (\`cmp\`, \`subs\`, \`tst\`, \`adds\`...); plain \`add\`/\`sub\` don't set flags. Range ±1 MB.`, undefined, `b.${c} \${1:label}`)),
  ins('bl', 'bl label', 'Branch with link: call a function, storing the return address in `x30`. **Clobbers `x30`** and all caller-saved registers (`x0`–`x18`), so save what you need. Call C functions with an underscore: `bl _malloc`.', 'bl _helper', 'bl _${1:func}'),
  ins('blr', 'blr Xn', 'Call the address in `Xn` (function pointer), setting `x30`.'),
  ins('br', 'br Xn', 'Jump to the address in `Xn` (no link). Jump tables / tail calls.'),
  ins('ret', 'ret {Xn}', 'Return: jump to `x30` (or Xn). Make sure `x30` was restored if you called anything, and `sp` is back where it started.', 'ldp x29, x30, [sp], #16\nret'),
  ins('cbz', 'cbz Xt, label', 'Branch if `Xt == 0` (no flags needed/changed). Great for null checks and empty-array checks: `cbz x1, empty`.', 'cbz x1, done'),
  ins('cbnz', 'cbnz Xt, label', 'Branch if `Xt != 0`. Loop on a counter: `sub x1, x1, #1; cbnz x1, loop`.', 'cbnz x1, loop'),
  ins('tbz', 'tbz Xt, #bit, label', 'Branch if bit `#bit` of Xt is 0. `tbz x0, #0, even`; `tbz x0, #63, nonneg`. Range ±32 KB.', 'tbz x0, #0, is_even'),
  ins('tbnz', 'tbnz Xt, #bit, label', 'Branch if bit `#bit` of Xt is 1. Sign test: `tbnz x0, #63, negative`.'),

  // ---------- loads / stores ----------
  ins('ldr', 'ldr Xt, [Xn{, #imm}] | [Xn, #imm]! | [Xn], #imm | [Xn, Xm{, lsl #3}] | ldr Xt, =const', 'Load 64 bits (`Wt` = 32 bits, zero-extended). Addressing: `[x1, #8]` offset; `[x1, #8]!` **pre-index** (updates x1 first); `[x1], #8` **post-index** (load then x1 += 8); `[x0, x2, lsl #3]` = `arr[i]` for 8-byte elements (shift must be 0 or 3 for x loads). Offset immediates must be multiples of 8 (0–32760).', 'ldr x9, [x0, x2, lsl #3]   // x9 = arr[i]\nldr x9, [x0], #8           // x9 = *p++', 'ldr ${1:x9}, [${2:x0}, ${3:x2}, lsl #3]'),
  ins('ldrb', 'ldrb Wt, [Xn{, #imm}] | [Xn], #1 | [Xn, Xm]', 'Load one byte, zero-extended. String loops: `ldrb w9, [x0], #1; cbz w9, done`. Note the **w** destination.', 'ldrb w9, [x0], #1\ncbz w9, done'),
  ins('ldrsb', 'ldrsb Xt|Wt, [Xn{, #imm}]', 'Load one byte, **sign**-extended (C `signed char`).'),
  ins('ldrh', 'ldrh Wt, [Xn{, #imm}] | [Xn, Xm, lsl #1]', 'Load 16-bit halfword, zero-extended (`ldrsh` sign-extends).'),
  ins('ldrsw', 'ldrsw Xt, [Xn{, #imm}] | [Xn, Xm, lsl #2]', 'Load a 32-bit word and sign-extend to 64 bits (C `int` arrays). Index shift is `lsl #2` for 4-byte elements.', 'ldrsw x9, [x0, x2, lsl #2]'),
  ins('ldur', 'ldur Xt, [Xn, #simm9]', 'Load with an unscaled signed offset (−256..255), e.g. negative offsets like `[x29, #-8]`. Usually `ldr` picks this automatically.'),
  ins('str', 'str Xt, [Xn{, #imm}] | [Xn, #imm]! | [Xn], #imm | [Xn, Xm{, lsl #3}]', 'Store 64 bits (`Wt` = 32 bits). Same addressing modes as `ldr`: `str x9, [x0, x2, lsl #3]` = `arr[i] = x9`. Note operand order: **source first**, address second.', 'str x9, [x0, x2, lsl #3]   // arr[i] = x9\nstr xzr, [x0], #8          // *p++ = 0', 'str ${1:x9}, [${2:x0}, ${3:x2}, lsl #3]'),
  ins('strb', 'strb Wt, [Xn{, #imm}] | [Xn], #1 | [Xn, Xm]', 'Store the low byte of Wt. Write a NUL terminator: `strb wzr, [x0]`.'),
  ins('strh', 'strh Wt, [Xn{, #imm}]', 'Store the low 16 bits.'),
  ins('ldp', 'ldp Xt1, Xt2, [Xn{, #imm}] | [Xn, #imm]! | [Xn], #imm', 'Load a pair of registers from consecutive 8-byte slots. Epilogue: `ldp x29, x30, [sp], #16` (post-index pops the frame). Offset is a multiple of 8 in −512..504.', 'ldp x19, x20, [sp, #16]\nldp x29, x30, [sp], #32\nret'),
  ins('stp', 'stp Xt1, Xt2, [Xn{, #imm}] | [Xn, #imm]! | [Xn], #imm', 'Store a pair. Prologue: `stp x29, x30, [sp, #-16]!` (pre-index pushes and moves sp). Keep `sp` 16-byte aligned.', 'stp x29, x30, [sp, #-32]!\nmov x29, sp\nstp x19, x20, [sp, #16]', 'stp x29, x30, [sp, #-16]!'),
  ins('adr', 'adr Xd, label', 'PC-relative address of a nearby label (±1 MB). For data in another section use `adrp` + `@PAGEOFF`.'),
  ins('adrp', 'adrp Xd, symbol@PAGE', 'Address of the 4 KB page containing a symbol (±4 GB). On macOS combine with `@PAGEOFF`: `adrp x9, _table@PAGE` then `add x9, x9, _table@PAGEOFF` (ELF syntax `:lo12:` does **not** work with Apple clang).', 'adrp x9, msg@PAGE\nadd x9, x9, msg@PAGEOFF'),
  ins('nop', 'nop', 'No operation.'),
  ins('svc', 'svc #0x80', 'Supervisor call (syscall). On macOS: syscall number in `x16`, `svc #0x80`. Normally call libc (`bl _write`) instead; raw syscalls are not a stable ABI on macOS.'),
  ins('brk', 'brk #imm', 'Breakpoint trap; crashes the program if no debugger is attached.'),

  // ---------- directives ----------
  dir('.globl', '.globl symbol', 'Export a symbol so the harness can link to it. On macOS C names get a leading underscore: the function `sum_array` must be `.globl _sum_array` with label `_sum_array:`.', '.globl _sum_array\n.p2align 2\n_sum_array:', '.globl _${1:name}'),
  dir('.global', '.global symbol', 'Same as `.globl`.'),
  dir('.p2align', '.p2align n', 'Align to 2^n bytes. Code must be 4-byte aligned: `.p2align 2` before each function. Use `.p2align 3` before 8-byte data.', undefined, '.p2align ${1:2}'),
  dir('.align', '.align n', 'On Apple/ARM targets `n` is a **power of two** (same as `.p2align`): `.align 3` = 8 bytes.'),
  dir('.text', '.text', 'Switch to the code section (`__TEXT,__text`). Functions go here.'),
  dir('.data', '.data', 'Switch to the writable data section (`__DATA,__data`). Access it via `adrp`/`@PAGEOFF`.'),
  dir('.bss', '.bss', 'Zero-initialised data section. Use `.zerofill` or `.space` for buffers.'),
  dir('.section', '.section segment,section{,type}', 'Select a Mach-O section, e.g. `.section __TEXT,__cstring,cstring_literals` for strings or `__DATA,__const` / `__TEXT,__const` for read-only tables.', '.section __TEXT,__const\n.p2align 3\ntable: .quad 1, 2, 3'),
  dir('.quad', '.quad value, ...', 'Emit 8-byte (64-bit) values. Matches Crucible `int` elements.', 'nums: .quad 10, 20, 30'),
  dir('.word', '.word value, ...', 'Emit 4-byte (32-bit) values (`.long` is the same).'),
  dir('.long', '.long value, ...', 'Emit 4-byte values (same as `.word` on ARM64).'),
  dir('.short', '.short value, ...', 'Emit 2-byte values (also `.hword`).'),
  dir('.byte', '.byte value, ...', 'Emit single bytes.', 'lut: .byte 0, 1, 1, 2'),
  dir('.asciz', '.asciz "text"', 'Emit a string **with** a trailing NUL byte (`.ascii` omits the NUL).', 'msg: .asciz "hello\\n"'),
  dir('.ascii', '.ascii "text"', 'Emit a string without NUL terminator.'),
  dir('.space', '.space nbytes{, fill}', 'Reserve `nbytes` bytes (zero by default). Also `.zero n`.'),
  dir('.zerofill', '.zerofill __DATA,__bss,sym,size,align', 'Mach-O: reserve a zero-filled buffer in bss without taking file space.'),
  dir('.equ', '.equ NAME, value', 'Define an assembler constant (also `.set`, or `NAME = value`).', '.equ N, 64'),
  dir('.subsections_via_symbols', '.subsections_via_symbols', 'Mach-O hint that symbols can be dead-stripped independently; clang emits it at file end. Harmless/optional.'),

  // ---------- registers ----------
  ...regs,
  reg('sp', 'sp (stack pointer)', 'Stack pointer; grows down and **must stay 16-byte aligned** whenever used for memory access. Allocate with `sub sp, sp, #N` / `stp ..., [sp, #-16]!` and restore before `ret`. Can\'t be used in most logical ops; register 31 means `sp` in add/sub/load-base contexts.'),
  reg('xzr', 'xzr (zero register, 64-bit)', 'Reads as 0, writes are discarded. `str xzr, [x0]` stores zero; `cmp x0, xzr` compares with 0. Same encoding as `sp`, chosen by context.'),
  reg('wzr', 'wzr (zero register, 32-bit)', '32-bit zero register: `strb wzr, [x0]` writes a NUL byte; `cset` / `csinc` use it internally.'),
  reg('fp', 'fp = x29', 'Alias for `x29`, the frame pointer. ' + CC),
  reg('lr', 'lr = x30', 'Alias for `x30`, the link register holding the return address. Save it (`stp x29, x30, [sp, #-16]!`) before any `bl`.'),
  reg('wN', 'w0–w30: low 32 bits of x0–x30', 'Writing `wN` **zero-extends** into `xN` (upper 32 bits cleared). Use `w` for byte/halfword loads (`ldrb w9, ...`) and 32-bit math; Crucible `int` is 64-bit, so use `x` for values. ' + CC),
  { name: 'prologue', kind: 'snippet', sig: 'AAPCS64 (Apple variant)', doc: CC + ' Apple differences: `x18` reserved; variadic args (e.g. `printf`) go **on the stack**, not in registers. Symbols have a leading underscore.', example: '_f: stp x29, x30, [sp, #-16]!\n    mov x29, sp   // ... bl _g ...\n    ldp x29, x30, [sp], #16\n    ret', insert: 'stp x29, x30, [sp, #-16]!\nmov x29, sp\n$0\nldp x29, x30, [sp], #16\nret' },
];
