// ARM64 (AArch64, Apple Silicon macOS, clang) reference for Crucible's editor (hover / completion / signature help).
const ins = (name, sig, doc, example, insert) => ({ name, kind: 'instruction', sig, doc, ...(example ? { example } : {}), ...(insert ? { insert } : {}) });
const dir = (name, sig, doc, example, insert) => ({ name, kind: 'directive', sig, doc, ...(example ? { example } : {}), ...(insert ? { insert } : {}) });
const reg = (name, sig, doc, example) => ({ name, kind: 'constant', sig, doc, example });

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
  ['vs', 'overflow set (V=1)', 'the last `adds`/`subs` overflowed as a signed operation'],
  ['vc', 'overflow clear (V=0)', 'no signed overflow'],
];

const regs = [];
for (let i = 0; i <= 30; i++) {
  let role, example;
  if (i === 0) role = '1st argument **and the return value** (`x0`/`w0`). Caller-saved: any `bl` may clobber it.';
  else if (i <= 7) role = `Argument register #${i + 1}. Caller-saved. For an \`int[]\` parameter Crucible passes pointer then count in consecutive registers (e.g. \`x0\` = pointer, \`x1\` = count).`;
  else if (i === 8) role = 'Indirect result location register (pointer for large struct returns). Otherwise a caller-saved scratch register.';
  else if (i <= 15) role = 'Temporary / scratch register. Caller-saved: free to use without saving, but clobbered by any `bl`.';
  else if (i <= 17) role = `\`ip${i - 16}\` intra-procedure-call scratch register: the linker's veneers/stubs may clobber it across a call. OK as a short-lived temp.`;
  else if (i === 18) role = '**Reserved on Apple platforms** (platform register). Never use or modify `x18` on macOS.';
  else if (i <= 28) role = 'Callee-saved: if your function writes it you must save it in the prologue (`stp x19, x20, [sp, #-16]!`) and restore it before `ret`. Survives calls you make.';
  else if (i === 29) role = 'Frame pointer (`fp`). Callee-saved; Apple requires a valid frame chain: `stp x29, x30, [sp, #-16]!` then `mov x29, sp`.';
  else role = 'Link register (`lr`): `bl` writes the return address here and `ret` jumps to it. **A `bl` overwrites it**, so any non-leaf function must save `x30` (with `x29`) first.';
  if (i === 0) example = 'mov x0, #42   // return value 42\nret';
  else if (i <= 7) example = `mov x9, x${i}   // read argument #${i + 1}`;
  else if (i <= 17) example = `add x${i}, x0, x1   // scratch temporary`;
  else if (i === 18) example = '// never read or write x18 on Apple platforms';
  else if (i <= 28) example = `str x${i}, [sp, #-16]!   // save callee-saved reg\n// ... use x${i} ...\nldr x${i}, [sp], #16      // restore before ret`;
  else if (i === 29) example = 'stp x29, x30, [sp, #-16]!\nmov x29, sp   // set up frame pointer';
  else example = 'stp x29, x30, [sp, #-16]!   // save lr before bl\nbl _helper\nldp x29, x30, [sp], #16\nret';
  regs.push(reg(`x${i}`, `x${i} (64-bit) / w${i} (low 32 bits)`, role, example));
}

const entries = [
  // ---------- moves ----------
  ins('mov', 'mov Xd, Xn | mov Xd, #imm | mov Xd, sp', 'Copy a register or load an immediate. The assembler picks `movz`/`movn`/`orr` for immediates; arbitrary 64-bit constants may need `movz` + `movk`. Writing a `w` register **zero-extends** into the full `x` register.', 'mov x9, #0\nmov x0, x19', 'mov ${1:x0}, ${2:x1}'),
  ins('movz', 'movz Xd, #imm16{, lsl #16|32|48}', 'Move a 16-bit immediate (optionally shifted), zeroing the rest.', 'movz x0, #0x1234, lsl #16'),
  ins('movk', 'movk Xd, #imm16{, lsl #16|32|48}', 'Insert a 16-bit immediate into one halfword, **keeping** the other bits. Pair with `movz` to build large constants.', 'movz x0, #0xBEEF\nmovk x0, #0xDEAD, lsl #16   // x0 = 0xDEADBEEF'),
  ins('movn', 'movn Xd, #imm16{, lsl #s}', 'Move the bitwise NOT of a shifted 16-bit immediate (for negative constants). `mov x0, #-1` assembles to this.', 'movn x0, #0        // x0 = -1\nmovn x1, #4        // x1 = -5'),
  ins('mvn', 'mvn Xd, Xm{, shift #n}', 'Bitwise NOT: `Xd = ~Xm` (alias of `orn Xd, xzr, Xm`).', 'mvn x0, x0         // x0 = ~x0'),
  ins('neg', 'neg Xd, Xm{, shift #n}', 'Negate: `Xd = -Xm` (alias of `sub Xd, xzr, Xm`). `negs` also sets flags.', 'neg x0, x0         // x0 = -x0'),

  // ---------- arithmetic ----------
  ins('add', 'add Xd, Xn, Xm{, lsl #n} | add Xd, Xn, #imm12{, lsl #12} | add Xd, Xn, Wm, sxtw', '`Xd = Xn + op2`. Immediate is 0–4095 (optionally `lsl #12`). Shifted register form is great for addressing: `add x9, x0, x1, lsl #3` = `&a[i]` for 8-byte elements. Does **not** set flags.', 'add x0, x0, x1\nadd x9, x0, x2, lsl #3   // x9 = &arr[i]', 'add ${1:x0}, ${2:x0}, ${3:x1}'),
  ins('adds', 'adds Xd, Xn, op2', 'Add and set flags N Z C V (C = unsigned carry out, V = signed overflow).', 'adds x0, x0, x1\nb.vs overflow      // signed overflow'),
  ins('sub', 'sub Xd, Xn, Xm{, lsl #n} | sub Xd, Xn, #imm12', '`Xd = Xn - op2`. Does not set flags. Stack allocation: `sub sp, sp, #32` (keep `sp` 16-byte aligned).', 'sub x1, x1, #1', 'sub ${1:x0}, ${2:x0}, ${3:x1}'),
  ins('subs', 'subs Xd, Xn, op2', 'Subtract and set flags; `cmp` is `subs xzr, ...`. Lets you decrement-and-test: `subs x1, x1, #1` then `b.ne loop`.', 'subs x1, x1, #1\nb.ne loop'),
  ins('mul', 'mul Xd, Xn, Xm', '`Xd = Xn * Xm` (low 64 bits; alias of `madd Xd, Xn, Xm, xzr`). **Registers only, no immediate**: `mov` the constant first. `smulh`/`umulh` give the high 64 bits.', 'mov x9, #10\nmul x0, x0, x9'),
  ins('madd', 'madd Xd, Xn, Xm, Xa', 'Multiply-add: `Xd = Xa + Xn * Xm`. E.g. `num = num*10 + digit` in one instruction.', 'madd x0, x0, x9, x10   // x0 = x10 + x0*x9'),
  ins('msub', 'msub Xd, Xn, Xm, Xa', 'Multiply-subtract: `Xd = Xa - Xn * Xm`. Remainder idiom: `sdiv q, a, b` then `msub r, q, b, a` (r = a - q*b).', 'sdiv x2, x0, x1\nmsub x3, x2, x1, x0    // x3 = x0 % x1'),
  ins('smull', 'smull Xd, Wn, Wm', 'Signed 32x32 -> 64-bit multiply.', 'smull x0, w1, w2   // x0 = (int64)w1 * (int64)w2'),
  ins('smulh', 'smulh Xd, Xn, Xm', 'High 64 bits of the signed 128-bit product (`umulh` for unsigned).', 'mul x2, x0, x1     // low 64 bits\nsmulh x3, x0, x1   // high 64 bits of signed product'),
  ins('umull', 'umull Xd, Wn, Wm', 'Unsigned 32x32 -> 64-bit multiply (no overflow possible).', 'umull x0, w1, w2   // x0 = (uint64)w1 * (uint64)w2'),
  ins('umulh', 'umulh Xd, Xn, Xm', 'High 64 bits of the unsigned 128-bit product. Non-zero after `mul` means the unsigned 64-bit product overflowed.', 'mul x2, x0, x1\numulh x3, x0, x1\ncbnz x3, overflow'),
  ins('sdiv', 'sdiv Xd, Xn, Xm', 'Signed divide, truncating toward zero. **Division by zero returns 0 (no trap)**. There is no remainder instruction: use `msub`.', 'sdiv x0, x0, x1    // x0 = x0 / x1 (truncates toward 0)'),
  ins('udiv', 'udiv Xd, Xn, Xm', 'Unsigned divide. Divide by zero yields 0.', 'udiv x0, x0, x1    // unsigned x0 / x1'),

  // ---------- logic / shifts ----------
  ins('and', 'and Xd, Xn, Xm{, shift #n} | and Xd, Xn, #bitmask', 'Bitwise AND. Immediates must be a "bitmask immediate" (repeating run of 1s, e.g. `#0xff`, `#1`); others must be put in a register. `ands`/`tst` set flags.', 'and x9, x0, #1   // x9 = x0 & 1 (odd?)'),
  ins('ands', 'ands Xd, Xn, op2', 'AND and set N/Z flags (C, V cleared).', 'ands x9, x0, #0xff\nb.eq low_byte_zero'),
  ins('orr', 'orr Xd, Xn, Xm{, shift #n} | orr Xd, Xn, #bitmask', 'Bitwise OR. `orr Xd, xzr, Xm` is a register move.', 'orr x0, x0, #1     // set bit 0'),
  ins('eor', 'eor Xd, Xn, Xm{, shift #n} | eor Xd, Xn, #bitmask', 'Bitwise XOR. XOR-of-all finds the single unpaired number.', 'eor x0, x0, x9'),
  ins('bic', 'bic Xd, Xn, Xm', 'Bit clear: `Xd = Xn & ~Xm`.', 'mov x9, #4\nbic x0, x0, x9     // clear bit 2'),
  ins('lsl', 'lsl Xd, Xn, #imm | lsl Xd, Xn, Xm', 'Logical shift left (`x << n`). Register shift amount is taken modulo 64.', 'lsl x9, x1, #3   // x9 = i * 8'),
  ins('lsr', 'lsr Xd, Xn, #imm | lsr Xd, Xn, Xm', 'Logical shift right (zero-fill): unsigned divide by a power of two.', 'lsr x9, x0, #1     // x9 = x0 / 2 (unsigned)'),
  ins('asr', 'asr Xd, Xn, #imm | asr Xd, Xn, Xm', 'Arithmetic shift right (sign-fill). Rounds toward **−infinity**, unlike `sdiv` which truncates toward zero.', 'asr x9, x0, #63    // x9 = -1 if x0 < 0, else 0'),
  ins('ror', 'ror Xd, Xn, #imm | ror Xd, Xn, Xm', 'Rotate right.', 'ror x0, x0, #8     // rotate right by 8 bits'),
  ins('clz', 'clz Xd, Xn', 'Count leading zero bits (64 for 0). Bit length = 64 − clz.', 'clz x9, x0\nmov x10, #64\nsub x0, x10, x9    // bit length of x0'),
  ins('rbit', 'rbit Xd, Xn', 'Reverse bit order. Count trailing zeros = `rbit` then `clz`.', 'rbit x9, x0\nclz x0, x9   // x0 = ctz(x0)'),
  ins('rev', 'rev Xd, Xn', 'Reverse byte order (endianness swap). `rev32`/`rev16` swap within words/halfwords.', 'rev x0, x0         // swap byte order (endianness)'),
  ins('cnt', 'cnt Vd.8B, Vn.8B', 'SIMD per-byte popcount; no scalar popcount on base ARMv8. Popcount: `fmov d0, x0; cnt v0.8b, v0.8b; addv b0, v0.8b; fmov w0, s0`.', 'fmov d0, x0\ncnt v0.8b, v0.8b\naddv b0, v0.8b\nfmov w0, s0        // w0 = popcount(x0)'),
  ins('sxtw', 'sxtw Xd, Wn', 'Sign-extend a 32-bit value to 64 bits (C `int` -> `long`).', 'sxtw x9, w9        // sign-extend 32-bit int to 64 bits'),
  ins('sxtb', 'sxtb Xd, Wn', 'Sign-extend the low byte (`sxth` for halfword).', 'sxtb x9, w9        // sign-extend low byte'),
  ins('uxtb', 'uxtb Wd, Wn', 'Zero-extend the low byte (= `and w, w, #0xff`). `uxth` for halfword. For 32->64 zero-extension just `mov w, w`.', 'uxtb w9, w9        // keep only the low byte'),
  ins('ubfx', 'ubfx Xd, Xn, #lsb, #width', 'Extract an unsigned bitfield: `(Xn >> lsb) & ((1<<width)-1)`. `sbfx` sign-extends.', 'ubfx x9, x0, #4, #4   // x9 = (x0 >> 4) & 0xf'),
  ins('bfi', 'bfi Xd, Xn, #lsb, #width', 'Insert the low `width` bits of Xn into Xd at `lsb`.', 'bfi x0, x9, #8, #8     // bits 8..15 of x0 = low byte of x9'),

  // ---------- compare / conditional ----------
  ins('cmp', 'cmp Xn, Xm | cmp Xn, #imm12', 'Compare: computes `Xn - op2`, sets flags, discards the result (alias of `subs xzr`). Follow with `b.<cond>`, `csel`, `cset`. Operand order matters: `cmp x0, x1; b.lt` jumps if x0 < x1.', 'cmp x0, x1\nb.ge done', 'cmp ${1:x0}, ${2:x1}'),
  ins('cmn', 'cmn Xn, Xm | cmn Xn, #imm12', 'Compare negative: flags from `Xn + op2`. Use `cmn x0, #1` to compare with −1.', 'cmn x0, #1\nb.eq is_minus_one   // x0 == -1'),
  ins('tst', 'tst Xn, Xm | tst Xn, #bitmask', 'Test bits: flags from `Xn & op2` (alias of `ands xzr`). `tst x0, #1; b.ne odd`.', 'tst x0, #1\nb.ne odd           // low bit set'),
  ins('ccmp', 'ccmp Xn, op2, #nzcv, cond', 'Conditional compare: if `cond` holds, compare; else set flags to `#nzcv`. Builds `a && b` conditions without branches.', 'cmp x0, #0\nccmp x1, #0, #4, gt   // if x0 > 0 compare x1 with 0, else force Z=1 (not gt)\nb.gt both_positive'),
  ins('csel', 'csel Xd, Xn, Xm, cond', 'Conditional select: `Xd = cond ? Xn : Xm`. Branchless max: `cmp x0, x1; csel x0, x0, x1, gt`.', 'cmp x0, x1\ncsel x0, x0, x1, gt   // max'),
  ins('csinc', 'csinc Xd, Xn, Xm, cond', '`Xd = cond ? Xn : Xm + 1`. Conditional increment: `cinc x0, x0, eq`.', 'cmp x0, x1\ncsinc x2, x3, x3, ne   // x2 = (x0 != x1) ? x3 : x3 + 1'),
  ins('cinc', 'cinc Xd, Xn, cond', '`Xd = cond ? Xn + 1 : Xn`. Counting: `cmp x9, #0; cinc x0, x0, eq`.', 'cmp x9, #0\ncinc x0, x0, eq       // count zeros'),
  ins('csneg', 'csneg Xd, Xn, Xm, cond', '`Xd = cond ? Xn : -Xm`.', 'cmp x0, #0\ncsneg x0, x0, x0, ge  // abs(x0)'),
  ins('cneg', 'cneg Xd, Xn, cond', '`Xd = cond ? -Xn : Xn`. Absolute value: `cmp x0, #0; cneg x0, x0, lt`.', 'cmp x0, #0\ncneg x0, x0, lt   // abs'),
  ins('cset', 'cset Wd, cond', '`Wd = cond ? 1 : 0` (alias of `csinc Wd, wzr, wzr, !cond`). Return a bool from a comparison.', 'cmp x0, x1\ncset x0, eq'),
  ins('csetm', 'csetm Xd, cond', '`Xd = cond ? -1 : 0` (all ones).', 'cmp x0, x1\ncsetm x9, lt          // x9 = (x0 < x1) ? -1 : 0'),

  // ---------- branches ----------
  ins('b', 'b label', 'Unconditional branch (±128 MB).', 'b loop', 'b ${1:label}'),
  ...conds.map(([c, meaning, use]) => ins(`b.${c}`, `b.${c} label`, `Branch if ${meaning}: ${use}. Flags come from the last flag-setting instruction (\`cmp\`, \`subs\`, \`tst\`, \`adds\`...); plain \`add\`/\`sub\` don't set flags. Range ±1 MB.`, `cmp x0, x1\nb.${c} target   // taken when ${c === 'vs' || c === 'vc' ? 'V flag ' + (c === 'vs' ? 'set' : 'clear') : 'condition holds'}`, `b.${c} \${1:label}`)),
  ins('bl', 'bl label', 'Branch with link: call a function, storing the return address in `x30`. **Clobbers `x30`** and all caller-saved registers (`x0`–`x18`), so save what you need. Call C functions with an underscore: `bl _malloc`.', 'bl _helper', 'bl _${1:func}'),
  ins('blr', 'blr Xn', 'Call the address in `Xn` (function pointer), setting `x30`.', 'adrp x9, _helper@PAGE\nadd x9, x9, _helper@PAGEOFF\nblr x9                // call through pointer'),
  ins('br', 'br Xn', 'Jump to the address in `Xn` (no link). Jump tables / tail calls.', 'br x9                 // jump to address in x9 (no return)'),
  ins('ret', 'ret {Xn}', 'Return: jump to `x30` (or Xn). Make sure `x30` was restored if you called anything, and `sp` is back where it started.', 'ldp x29, x30, [sp], #16\nret'),
  ins('cbz', 'cbz Xt, label', 'Branch if `Xt == 0` (no flags needed/changed). Great for null checks and empty-array checks: `cbz x1, empty`.', 'cbz x1, done'),
  ins('cbnz', 'cbnz Xt, label', 'Branch if `Xt != 0`. Loop on a counter: `sub x1, x1, #1; cbnz x1, loop`.', 'cbnz x1, loop'),
  ins('tbz', 'tbz Xt, #bit, label', 'Branch if bit `#bit` of Xt is 0. `tbz x0, #0, even`; `tbz x0, #63, nonneg`. Range ±32 KB.', 'tbz x0, #0, is_even'),
  ins('tbnz', 'tbnz Xt, #bit, label', 'Branch if bit `#bit` of Xt is 1. Sign test: `tbnz x0, #63, negative`.', 'tbnz x0, #63, negative   // branch if x0 < 0'),

  // ---------- loads / stores ----------
  ins('ldr', 'ldr Xt, [Xn{, #imm}] | [Xn, #imm]! | [Xn], #imm | [Xn, Xm{, lsl #3}] | ldr Xt, =const', 'Load 64 bits (`Wt` = 32 bits, zero-extended). Addressing: `[x1, #8]` offset; `[x1, #8]!` **pre-index** (updates x1 first); `[x1], #8` **post-index** (load then x1 += 8); `[x0, x2, lsl #3]` = `arr[i]` for 8-byte elements (shift must be 0 or 3 for x loads). Offset immediates must be multiples of 8 (0–32760).', 'ldr x9, [x0, x2, lsl #3]   // x9 = arr[i]\nldr x9, [x0], #8           // x9 = *p++', 'ldr ${1:x9}, [${2:x0}, ${3:x2}, lsl #3]'),
  ins('ldrb', 'ldrb Wt, [Xn{, #imm}] | [Xn], #1 | [Xn, Xm]', 'Load one byte, zero-extended. String loops: `ldrb w9, [x0], #1; cbz w9, done`. Note the **w** destination.', 'ldrb w9, [x0], #1\ncbz w9, done'),
  ins('ldrsb', 'ldrsb Xt|Wt, [Xn{, #imm}]', 'Load one byte, **sign**-extended (C `signed char`).', 'ldrsb x9, [x0]        // signed char -> 64-bit'),
  ins('ldrh', 'ldrh Wt, [Xn{, #imm}] | [Xn, Xm, lsl #1]', 'Load 16-bit halfword, zero-extended (`ldrsh` sign-extends).', 'ldrh w9, [x0, x2, lsl #1]   // w9 = (uint16)arr[i]'),
  ins('ldrsh', 'ldrsh Xt|Wt, [Xn{, #imm}] | [Xn, Xm, lsl #1]', 'Load a 16-bit halfword, **sign**-extended (C `short`).', 'ldrsh x9, [x0, x2, lsl #1]   // x9 = (int64)arr16[i]'),
  ins('ldrsw', 'ldrsw Xt, [Xn{, #imm}] | [Xn, Xm, lsl #2]', 'Load a 32-bit word and sign-extend to 64 bits (C `int` arrays). Index shift is `lsl #2` for 4-byte elements.', 'ldrsw x9, [x0, x2, lsl #2]'),
  ins('ldur', 'ldur Xt, [Xn, #simm9]', 'Load with an unscaled signed offset (−256..255), e.g. negative offsets like `[x29, #-8]`. Usually `ldr` picks this automatically.', 'ldur x9, [x29, #-8]   // load local below frame pointer'),
  ins('str', 'str Xt, [Xn{, #imm}] | [Xn, #imm]! | [Xn], #imm | [Xn, Xm{, lsl #3}]', 'Store 64 bits (`Wt` = 32 bits). Same addressing modes as `ldr`: `str x9, [x0, x2, lsl #3]` = `arr[i] = x9`. Note operand order: **source first**, address second.', 'str x9, [x0, x2, lsl #3]   // arr[i] = x9\nstr xzr, [x0], #8          // *p++ = 0', 'str ${1:x9}, [${2:x0}, ${3:x2}, lsl #3]'),
  ins('stur', 'stur Xt, [Xn, #simm9]', 'Store with an unscaled signed offset (−256..255); the counterpart of `ldur`. `str` with a negative offset assembles to this.', 'stur x0, [x29, #-8]   // spill to a local below fp'),
  ins('strb', 'strb Wt, [Xn{, #imm}] | [Xn], #1 | [Xn, Xm]', 'Store the low byte of Wt. Write a NUL terminator: `strb wzr, [x0]`.', 'strb w9, [x0], #1     // *p++ = (char)w9\nstrb wzr, [x0]        // NUL-terminate'),
  ins('strh', 'strh Wt, [Xn{, #imm}]', 'Store the low 16 bits.', 'strh w9, [x0, #2]     // store 16-bit value'),
  ins('ldp', 'ldp Xt1, Xt2, [Xn{, #imm}] | [Xn, #imm]! | [Xn], #imm', 'Load a pair of registers from consecutive 8-byte slots. Epilogue: `ldp x29, x30, [sp], #16` (post-index pops the frame). Offset is a multiple of 8 in −512..504.', 'ldp x19, x20, [sp, #16]\nldp x29, x30, [sp], #32\nret'),
  ins('stp', 'stp Xt1, Xt2, [Xn{, #imm}] | [Xn, #imm]! | [Xn], #imm', 'Store a pair. Prologue: `stp x29, x30, [sp, #-16]!` (pre-index pushes and moves sp). Keep `sp` 16-byte aligned.', 'stp x29, x30, [sp, #-32]!\nmov x29, sp\nstp x19, x20, [sp, #16]', 'stp x29, x30, [sp, #-16]!'),
  ins('adr', 'adr Xd, label', 'PC-relative address of a nearby label (±1 MB). For data in another section use `adrp` + `@PAGEOFF`.', 'adr x9, loop_table   // x9 = address of nearby label'),
  ins('adrp', 'adrp Xd, symbol@PAGE', 'Address of the 4 KB page containing a symbol (±4 GB). On macOS combine with `@PAGEOFF`: `adrp x9, _table@PAGE` then `add x9, x9, _table@PAGEOFF` (ELF syntax `:lo12:` does **not** work with Apple clang).', 'adrp x9, msg@PAGE\nadd x9, x9, msg@PAGEOFF'),
  ins('nop', 'nop', 'No operation.', 'nop                   // do nothing (padding)'),
  ins('svc', 'svc #0x80', 'Supervisor call (syscall). On macOS: syscall number in `x16`, `svc #0x80`. Normally call libc (`bl _write`) instead; raw syscalls are not a stable ABI on macOS.', 'mov x16, #1          // exit syscall number\nsvc #0x80'),
  ins('brk', 'brk #imm', 'Breakpoint trap; crashes the program if no debugger is attached.', 'brk #1                // trap: should never get here'),

  // ---------- floating point (double in d0–d31, float in s0–s31) ----------
  ins('fmov', 'fmov Dd, Dn | fmov Dd, Xn | fmov Xd, Dn | fmov Dd, #imm', 'Move between FP registers, or copy raw bits between a general and an FP register (no conversion: use `scvtf`/`fcvtzs` for that). Immediates are limited to simple values like `#1.0`, `#0.5`, `#2.0`; for 0.0 use `fmov d0, xzr`.', 'fmov d0, #1.0\nfmov d1, xzr        // d1 = 0.0'),
  ins('fadd', 'fadd Dd, Dn, Dm', 'Floating-point add (`Sd` registers for `float`). Double args arrive in `d0`–`d7` and are returned in `d0`.', 'fadd d0, d0, d1     // d0 = d0 + d1'),
  ins('fsub', 'fsub Dd, Dn, Dm', 'Floating-point subtract: `Dd = Dn - Dm`.', 'fsub d0, d1, d2'),
  ins('fmul', 'fmul Dd, Dn, Dm', 'Floating-point multiply.', 'fmul d0, d0, d0     // square'),
  ins('fdiv', 'fdiv Dd, Dn, Dm', 'Floating-point divide. Dividing by 0.0 gives ±infinity or NaN (no trap).', 'fdiv d0, d0, d1     // d0 = d0 / d1'),
  ins('fsqrt', 'fsqrt Dd, Dn', 'Floating-point square root (NaN for negative input).', 'fsqrt d0, d0'),
  ins('fcmp', 'fcmp Dn, Dm | fcmp Dn, #0.0', 'Compare two FP values and set flags. Gotcha: NaN compares *unordered*, which makes `b.lt`/`b.le`/`b.ne` true; use `b.mi`/`b.ls` for a strict less/less-or-equal that is false on NaN.', 'fcmp d0, d1\nb.gt bigger'),
  ins('scvtf', 'scvtf Dd, Xn', 'Convert a signed integer to floating point (`ucvtf` for unsigned).', 'scvtf d0, x0        // d0 = (double)x0'),
  ins('ucvtf', 'ucvtf Dd, Xn', 'Convert an unsigned integer to floating point.', 'ucvtf d0, x0        // d0 = (double)(uint64)x0'),
  ins('fcvtzs', 'fcvtzs Xd, Dn', 'Convert floating point to a signed integer, rounding **toward zero** like a C cast; out-of-range values saturate and NaN gives 0. `fcvtzu` for unsigned.', 'fcvtzs x0, d0       // x0 = (long)d0'),

  // ---------- directives ----------
  dir('.globl', '.globl symbol', 'Export a symbol so the harness can link to it. On macOS C names get a leading underscore: the function `sum_array` must be `.globl _sum_array` with label `_sum_array:`.', '.globl _sum_array\n.p2align 2\n_sum_array:', '.globl _${1:name}'),
  dir('.global', '.global symbol', 'Same as `.globl`.', '.global _main\n_main:'),
  dir('.p2align', '.p2align n', 'Align to 2^n bytes. Code must be 4-byte aligned: `.p2align 2` before each function. Use `.p2align 3` before 8-byte data.', '.p2align 2\n_func:                // 4-byte aligned code', '.p2align ${1:2}'),
  dir('.align', '.align n', 'On Apple/ARM targets `n` is a **power of two** (same as `.p2align`): `.align 3` = 8 bytes.', '.align 3\nvals: .quad 1, 2     // 8-byte aligned data'),
  dir('.text', '.text', 'Switch to the code section (`__TEXT,__text`). Functions go here.', '.text\n.globl _f\n_f: ret'),
  dir('.data', '.data', 'Switch to the writable data section (`__DATA,__data`). Access it via `adrp`/`@PAGEOFF`.', '.data\ncounter: .quad 0'),
  dir('.bss', '.bss', 'Zero-initialised data section. Use `.zerofill` or `.space` for buffers.', '.bss\nbuf: .space 256'),
  dir('.section', '.section segment,section{,type}', 'Select a Mach-O section, e.g. `.section __TEXT,__cstring,cstring_literals` for strings or `__DATA,__const` / `__TEXT,__const` for read-only tables.', '.section __TEXT,__const\n.p2align 3\ntable: .quad 1, 2, 3'),
  dir('.quad', '.quad value, ...', 'Emit 8-byte (64-bit) values. Matches Crucible `int` elements.', 'nums: .quad 10, 20, 30'),
  dir('.word', '.word value, ...', 'Emit 4-byte (32-bit) values (`.long` is the same).', 'vals: .word 1, 2, 3  // 32-bit values'),
  dir('.long', '.long value, ...', 'Emit 4-byte values (same as `.word` on ARM64).', 'vals: .long 100, 200'),
  dir('.short', '.short value, ...', 'Emit 2-byte values (also `.hword`).', 'ports: .short 80, 443'),
  dir('.byte', '.byte value, ...', 'Emit single bytes.', 'lut: .byte 0, 1, 1, 2'),
  dir('.asciz', '.asciz "text"', 'Emit a string **with** a trailing NUL byte (`.ascii` omits the NUL).', 'msg: .asciz "hello\\n"'),
  dir('.ascii', '.ascii "text"', 'Emit a string without NUL terminator.', 'tag: .ascii "ABCD"   // 4 bytes, no NUL'),
  dir('.space', '.space nbytes{, fill}', 'Reserve `nbytes` bytes (zero by default). Also `.zero n`.', 'buf: .space 64       // 64 zero bytes'),
  dir('.zerofill', '.zerofill __DATA,__bss,sym,size,align', 'Mach-O: reserve a zero-filled buffer in bss without taking file space.', '.zerofill __DATA,__bss,_buf,4096,3   // 4 KB, 8-byte aligned'),
  dir('.equ', '.equ NAME, value', 'Define an assembler constant (also `.set`, or `NAME = value`).', '.equ N, 64'),
  dir('.subsections_via_symbols', '.subsections_via_symbols', 'Mach-O hint that symbols can be dead-stripped independently; clang emits it at file end. Harmless/optional.', '.subsections_via_symbols   // last line of the file'),

  // ---------- registers ----------
  ...regs,
  reg('sp', 'sp (stack pointer)', 'Stack pointer; grows down and **must stay 16-byte aligned** whenever used for memory access. Allocate with `sub sp, sp, #N` / `stp ..., [sp, #-16]!` and restore before `ret`. Can\'t be used in most logical ops; register 31 means `sp` in add/sub/load-base contexts.', 'sub sp, sp, #32        // reserve 32 bytes\nstr x0, [sp, #8]\nadd sp, sp, #32        // release'),
  reg('xzr', 'xzr (zero register, 64-bit)', 'Reads as 0, writes are discarded. `str xzr, [x0]` stores zero; `cmp x0, xzr` compares with 0. Same encoding as `sp`, chosen by context.', 'str xzr, [x0]       // *x0 = 0\ncmp x1, xzr         // compare x1 with 0'),
  reg('wzr', 'wzr (zero register, 32-bit)', '32-bit zero register: `strb wzr, [x0]` writes a NUL byte; `cset` / `csinc` use it internally.', 'strb wzr, [x0]      // write NUL terminator'),
  reg('fp', 'fp = x29', 'Alias for `x29`, the frame pointer. ' + CC, 'mov fp, sp          // same as mov x29, sp'),
  reg('lr', 'lr = x30', 'Alias for `x30`, the link register holding the return address. Save it (`stp x29, x30, [sp, #-16]!`) before any `bl`.', 'mov x9, lr          // copy return address'),
  reg('wN', 'w0–w30: low 32 bits of x0–x30', 'Writing `wN` **zero-extends** into `xN` (upper 32 bits cleared). Use `w` for byte/halfword loads (`ldrb w9, ...`) and 32-bit math; Crucible `int` is 64-bit, so use `x` for values. ' + CC, 'ldrb w9, [x0]       // byte into w9 (x9 upper bits cleared)\nadd w0, w0, w9'),
  { name: 'prologue', kind: 'snippet', sig: 'AAPCS64 (Apple variant)', doc: CC + ' Apple differences: `x18` reserved; variadic args (e.g. `printf`) go **on the stack**, not in registers. Symbols have a leading underscore.', example: '_f: stp x29, x30, [sp, #-16]!\n    mov x29, sp   // ... bl _g ...\n    ldp x29, x30, [sp], #16\n    ret', insert: 'stp x29, x30, [sp, #-16]!\nmov x29, sp\n$0\nldp x29, x30, [sp], #16\nret' },
];

// Beginner "New in this problem" cards (see SCHEMA.md `learn`), attached by instruction name.
const LEARN = {
  "ret": {
    "summary": "return from the function to its caller",
    "what": "`ret` ends your function and jumps back to the instruction right after the call that got you here. It finds that spot in `x30`, the **link register**: when the caller ran `bl your_function`, the CPU stored the return address in `x30`. Whatever is in `x0` at that moment is the return value the caller sees. `ret` itself does not change `x0`, the stack or the flags.",
    "params": {
      "Xn": "optional register holding the address to jump to; leave it out and `ret` uses `x30` (almost always what you want)"
    },
    "example": "// suppose x0 already holds 10\nret                 // back to the caller, which receives 10",
    "watch": [
      "If your function called another one with `bl`, `x30` was overwritten; restore the saved `x30` before `ret` or you jump to the wrong place.",
      "Put the result in `x0` before `ret`; a value left only in another register is lost.",
      "`sp` must be back at its value on entry."
    ]
  },
  "sub": {
    "summary": "subtract one value from another",
    "what": "`sub Xd, Xn, Xm` computes `Xn - Xm` and writes it to `Xd`. The first register is always the **destination**; the two inputs are unchanged unless you reuse one as the destination. The second input can be a register or a small constant (0–4095) written with `#`. Plain `sub` does **not** update the condition flags (the N/Z/C/V bits conditional branches read); use `subs` when you want to branch on the result.",
    "params": {
      "Xd": "destination register that receives the difference, e.g. `x11`",
      "Xn": "the value to subtract from (left side of the minus), e.g. `x9`",
      "Xm": "register holding the amount to subtract, e.g. `x10`",
      "#imm12": "or a constant 0–4095 to subtract, e.g. `#1`"
    },
    "example": "mov x9, #20         // x9 = 20\nmov x10, #8         // x10 = 8\nsub x11, x9, x10    // x11 = 20 - 8 = 12\nsub x11, x11, #1    // x11 = 12 - 1 = 11",
    "watch": [
      "Order matters: `sub x0, x1, x2` is `x1 - x2`, not `x2 - x1`.",
      "Using `w` registers (`sub w0, w1, w2`) does 32-bit math and zeroes the top half of `x0`.",
      "`sub` does not set flags; a `b.eq`/`b.lt` after it tests whatever compare came earlier."
    ]
  },
  "cmp": {
    "summary": "compare two values and set the flags",
    "what": "`cmp Xn, Xm` subtracts `Xm` from `Xn`, throws the answer away, and keeps only the four condition **flags**: N (result negative), Z (result zero, i.e. equal), C (carry: no unsigned borrow) and V (signed overflow). Conditional instructions that come next read those flags: `b.eq`, `b.lt`, `csel`, `cneg`, and so on. Read `cmp a, b` followed by `b.lt` as \"if a < b\". No register changes, only the flags.",
    "params": {
      "Xn": "the left-hand value of the comparison, e.g. `x3`",
      "Xm": "the right-hand value in a register, e.g. `x4`",
      "#imm12": "or a constant 0–4095, e.g. `#10`"
    },
    "example": "mov x3, #7          // x3 = 7\ncmp x3, #7          // 7 - 7 = 0: Z=1, so \"equal\" conditions hold\ncmp x3, #10         // 7 - 10 < 0: \"less than\" conditions hold\nb.lt Lsmall         // jumps, because 7 < 10 (signed)",
    "watch": [
      "Operand order: `cmp x0, x1` then `b.gt` means x0 > x1.",
      "Flags only last until the next flag-setting instruction (`cmp`, `subs`, `tst`, `adds`...).",
      "Pick signed conditions (`lt`/`gt`/`le`/`ge`) or unsigned ones (`lo`/`hi`/`ls`/`hs`) to match your data."
    ]
  },
  "tst": {
    "summary": "check bits with and, set the flags",
    "what": "`tst Xn, #mask` computes `Xn AND mask`, discards the result and sets the flags from it. The useful one is Z, the **zero flag**: Z=1 means none of the masked bits were set, Z=0 means at least one was. It asks \"is this bit on?\" without changing the register; `tst x0, #1` checks the lowest bit, which tells odd from even. Follow it with `b.eq`/`b.ne`, `cset` or `csel`.",
    "params": {
      "Xn": "the value whose bits you are checking, e.g. `x5`",
      "Xm": "a register holding the bit mask",
      "#bitmask": "or a constant mask such as `#1` (lowest bit) or `#0xff` (low byte)"
    },
    "example": "mov x5, #6          // x5 = 0b110\ntst x5, #1          // 6 & 1 = 0: Z=1 (bit 0 clear, 6 is even)\ntst x5, #4          // 6 & 4 = 4, not zero: Z=0\nb.ne Lbit2_on       // jumps, bit 2 is set",
    "watch": [
      "Z=1 means the masked bits were all ZERO, so `b.eq` = \"bit clear\" and `b.ne` = \"bit set\".",
      "Only bit-pattern constants are allowed as `#bitmask` (`#5` = 0b101 is rejected); put other masks in a register first.",
      "`tst` changes only the flags; the register keeps its value."
    ]
  },
  "mov": {
    "summary": "copy a value into a register",
    "what": "`mov Xd, Xn` copies the value of `Xn` into `Xd` (`Xn` keeps its value); `mov Xd, #imm` loads a constant. Despite the name nothing \"moves\": it is a copy, and the old value of `Xd` is overwritten. Use it to set up counters, initialise totals, or copy a value into the register something else expects.",
    "params": {
      "Xd": "destination register, overwritten, e.g. `x9`",
      "Xn": "source register to copy from (unchanged), e.g. `x10`",
      "#imm": "or a constant such as `#0`, `#100` or `#-1`"
    },
    "example": "mov x9, #5          // x9 = 5\nmov x10, x9         // x10 = 5, x9 is still 5\nmov x9, #0          // x9 = 0, x10 is still 5",
    "watch": [
      "Destination comes first: `mov x9, x10` copies x10 INTO x9.",
      "Not every 64-bit constant fits in one `mov`; big ones need `movz` + `movk` (the assembler will complain).",
      "Writing a `w` register (`mov w9, #5`) clears the top 32 bits of `x9`."
    ]
  },
  "cbz": {
    "summary": "branch if a register is zero",
    "what": "`cbz Xt, label` (\"compare and branch if zero\") jumps to `label` when `Xt` holds 0; otherwise execution falls through to the next line. It does the test and the jump in one instruction and neither reads nor changes the flags, which makes it ideal for loop exits (\"stop when the counter reaches 0\"), empty-array checks and null-pointer checks. Its twin `cbnz` jumps when the register is not zero.",
    "params": {
      "Xt": "the register to test, e.g. `x2` (a `w` register tests only the low 32 bits)",
      "label": "where to jump when it is zero, e.g. `Lempty`"
    },
    "example": "mov x2, #0          // x2 = 0\ncbz x2, Lempty      // x2 is 0, so jump to Lempty\nmov x3, #1          // skipped: never runs",
    "watch": [
      "It tests for exactly zero; for \"<= 0\" use `cmp` + `b.le`.",
      "It ignores the flags, so a preceding `cmp` has no effect on it."
    ]
  },
  "b": {
    "summary": "jump to a label, always",
    "what": "`b label` is an unconditional jump (a \"goto\"): the next instruction executed is the one at `label`. Combine it with a conditional branch to build a loop: test the exit condition at the top, do the body, then `b` back to the top. It does not save a return address (that is `bl`), so it is not a function call.",
    "params": {
      "label": "the name of the target line, e.g. `Lloop`; on macOS local labels conventionally start with `L`"
    },
    "example": "Lloop:              // top of the loop\n  sub x9, x9, #1    // x9 -= 1\n  cbz x9, Lout      // leave when x9 reaches 0\n  b Lloop           // otherwise go round again\nLout:               // execution continues here",
    "watch": [
      "A `b` back to the top with no exit branch loops forever and the test times out.",
      "`b` never returns; use `bl` to call a function."
    ]
  },
  "b.le": {
    "summary": "branch if less or equal (signed)",
    "what": "`b.le label` jumps to `label` if the most recent flag-setting instruction (usually `cmp a, b`) found a <= b, treating both as **signed** numbers (negatives are smaller than positives). Otherwise it falls through to the next line. Under the hood it checks the flags: Z=1 (equal) or N!=V (less).",
    "params": {
      "label": "where to jump when the condition holds, e.g. `Lbase`"
    },
    "example": "mov x3, #1          // x3 = 1\ncmp x3, #1          // compare 1 with 1\nb.le Lbase          // jumps: 1 <= 1",
    "watch": [
      "It reads flags from the last `cmp`/`subs`/`tst`; a `mul` or plain `add` in between leaves them alone, another `cmp` replaces them.",
      "For unsigned values (addresses, sizes) use `b.ls`.",
      "`cmp x0, x1; b.le` means x0 <= x1, not x1 <= x0."
    ]
  },
  "ldr": {
    "summary": "load 8 bytes from memory into a register",
    "what": "`ldr Xt, [Xn]` reads the 8-byte value stored at the memory address in `Xn` and puts it in `Xt`. Square brackets mean \"the memory at this address\". You can add a byte offset: `[Xn, #16]` reads 16 bytes past `Xn`, and `[Xn, Xm, lsl #3]` reads at `Xn + Xm*8`, which is exactly `array[i]` for 8-byte elements. **Post-index** `[Xn], #8` loads first and then adds 8 to `Xn` (walking a pointer); **pre-index** `[Xn, #8]!` adds first, then loads.",
    "params": {
      "Xt": "destination register for the loaded value, e.g. `x9`",
      "Xn": "register holding the address (a pointer), e.g. `x0` = the array",
      "#imm": "byte offset to add, a multiple of 8, e.g. `#16` = element 2",
      "Xm": "index register, scaled by `lsl #3` (times 8) for 8-byte elements"
    },
    "example": "// x0 points at {10, 20, 30}\nldr x9, [x0]              // x9 = 10 (element 0)\nldr x9, [x0, #16]         // x9 = 30 (byte 16 = element 2)\nmov x10, #1               // index 1\nldr x9, [x0, x10, lsl #3] // x9 = 20 (address x0 + 1*8)",
    "watch": [
      "Offsets are in bytes, not elements: element i of a `long long` array is at i*8.",
      "`ldr x...` reads 8 bytes; use a `w` register for 4-byte values or `ldrb` for one byte.",
      "Post-index `[x0], #8` changes x0; plain `[x0, #8]` does not."
    ]
  },
  "lsr": {
    "summary": "shift bits right, filling with zeros",
    "what": "`lsr Xd, Xn, #k` (logical shift right) slides every bit of `Xn` k places toward the low end: the k lowest bits fall off and zeros fill in at the top. For non-negative numbers that is division by 2^k, rounded down; shifting by 1 halves the value. It is the standard way to walk through a number bit by bit: look at bit 0, shift right, repeat.",
    "params": {
      "Xd": "destination register, e.g. `x9`",
      "Xn": "the value to shift, e.g. `x10`",
      "#imm": "how many places, 0–63, e.g. `#1`",
      "Xm": "or a register holding the shift amount (only its low 6 bits count)"
    },
    "example": "mov x10, #13        // x10 = 0b1101 = 13\nlsr x9, x10, #1     // x9 = 0b110 = 6 (13 / 2, rounded down)\nlsr x9, x10, #2     // x9 = 0b11 = 3",
    "watch": [
      "`lsr` treats the value as unsigned; to halve a negative signed number use `asr`.",
      "`lsr x0, x0, #1` overwrites x0; shift into another register if you still need the original."
    ]
  },
  "b.eq": {
    "summary": "branch if the compared values were equal",
    "what": "`b.eq label` jumps when the zero flag Z is 1: the last `cmp a, b` found a == b (their difference was 0), or the last `tst` found none of the bits set. Otherwise it falls through. A chain of `cmp`/`b.eq` pairs that all jump to the same label checks one value against several candidates.",
    "params": {
      "label": "where to jump on equality, e.g. `Lmatch`"
    },
    "example": "mov w9, #'x'        // w9 = 120, the character 'x'\ncmp w9, #'y'        // 'x' vs 'y': not equal, Z=0\nb.eq Lmatch         // not taken\ncmp w9, #'x'        // equal: Z=1\nb.eq Lmatch         // taken",
    "watch": [
      "Compare characters in `w` registers (`cmp w2, #'a'`) when they were loaded with `ldrb`.",
      "After `tst`, `b.eq` means \"the tested bits were all zero\"."
    ]
  },
  "add": {
    "summary": "add two values",
    "what": "`add Xd, Xn, Xm` computes `Xn + Xm` and stores the sum in `Xd`; the destination is always first and the inputs are unchanged unless one of them is also the destination. The second input can be a register or a constant 0–4095 (`#imm12`). It can also shift the second register first: `add Xd, Xn, Xm, lsl #3` adds `Xm*8`, handy for array addresses. Plain `add` leaves the flags alone (`adds` sets them).",
    "params": {
      "Xd": "destination register for the sum, e.g. `x11`",
      "Xn": "first value, e.g. `x9`",
      "Xm": "second value in a register, e.g. `x10`",
      "#imm12": "or a constant 0–4095, e.g. `#1`",
      "lsl #n": "optional: shift `Xm` left by n bits (multiply by 2^n) before adding"
    },
    "example": "mov x9, #30              // x9 = 30\nmov x10, #4              // x10 = 4\nadd x11, x9, x10         // x11 = 34\nadd x11, x11, #1         // x11 = 35 (counter++)\nadd x12, x9, x10, lsl #3 // x12 = 30 + 4*8 = 62",
    "watch": [
      "Immediates are limited to 0–4095 (optionally shifted by 12); put bigger constants in a register.",
      "`add` does not set flags; use `adds` if a branch should test the result.",
      "Don't mix widths: `add x0, x0, w1` is rejected; use all-`x` or all-`w` registers."
    ]
  },
  "b.hs": {
    "summary": "branch if higher or same (unsigned)",
    "what": "`b.hs label` jumps when the last `cmp a, b` found a >= b with both treated as **unsigned** numbers (it checks the carry flag C=1). Unsigned comparisons are the right choice for addresses and pointers, which are never negative. It is the same instruction as `b.cs` (\"carry set\").",
    "params": {
      "label": "where to jump when a >= b (unsigned), e.g. `Lpast`"
    },
    "example": "mov x9, #16         // x9 = 16 (think: a pointer)\nmov x10, #8         // x10 = 8\ncmp x9, x10         // 16 vs 8\nb.hs Lpast          // taken: 16 >= 8 unsigned",
    "watch": [
      "Unsigned: -1 is seen as the huge number 2^64-1, so use `b.ge` for signed integers.",
      "The opposite condition is `b.lo` (unsigned <)."
    ]
  },
  "ldrb": {
    "summary": "load one byte (a character) from memory",
    "what": "`ldrb Wt, [Xn]` reads a single byte from the address in `Xn` into the 32-bit register `Wt`, **zero-extending** it: the byte lands in the low 8 bits and every higher bit becomes 0, so the character `A` becomes exactly 65. That is how you read the characters of a C string, which is just bytes in a row ending with a 0 byte (NUL). Addressing forms work like `ldr`, but offsets count single bytes.",
    "params": {
      "Wt": "destination, must be a `w` register, e.g. `w9`",
      "Xn": "register holding the address of the byte, e.g. `x10` = pointer into the string",
      "#imm": "byte offset, e.g. `#2` for the 3rd character",
      "Xm": "or a register holding the byte index"
    },
    "example": "// x10 points at \"hello\"\nldrb w9, [x10]          // w9 = 'h' (104)\nldrb w9, [x10, #2]      // w9 = 'l' (108), x10 unchanged\nmov x11, #1             // index 1\nldrb w9, [x10, x11]     // w9 = 'e' (101)",
    "watch": [
      "The destination is a `w` register: `ldrb x9, [x0]` is an assembler error.",
      "Offsets count bytes, not 8-byte elements.",
      "Post-index forms (`[x0], #k`) move the pointer as a side effect."
    ]
  },
  "subs": {
    "summary": "subtract and set the flags",
    "what": "`subs Xd, Xn, op2` does the same subtraction as `sub` (`Xd = Xn - op2`) but also sets the condition flags from the result, like `cmp`. So one instruction can decrement a counter **and** let the next branch ask \"did it reach zero?\" (`b.eq`/`b.ne`) or \"is it negative?\" (`b.mi`). `cmp` is literally `subs` with the result thrown away.",
    "params": {
      "Xd": "destination register for the difference, e.g. `x9`",
      "Xn": "the value to subtract from, e.g. `x9`",
      "op2": "a register or a constant 0–4095 to subtract, e.g. `#1`"
    },
    "example": "mov x9, #2          // x9 = 2\nsubs x9, x9, #1     // x9 = 1, not zero: Z=0\nsubs x9, x9, #1     // x9 = 0: Z=1\nb.eq Lfinished      // taken: the counter hit 0",
    "watch": [
      "Only the `s` versions (`subs`, `adds`, `ands`) set flags; plain `sub` leaves the old flags in place.",
      "Signed vs unsigned conditions still matter after `subs`."
    ]
  },
  "b.ne": {
    "summary": "branch if the values were not equal",
    "what": "`b.ne label` jumps when the zero flag Z is 0: the last `cmp a, b` found a != b, the last `subs` produced a non-zero result, or the last `tst` found at least one bit set. Otherwise it falls through. With `subs x, x, #1` it forms the classic countdown loop: keep looping while the counter is not zero.",
    "params": {
      "label": "where to jump when not equal / not zero, e.g. `Lagain`"
    },
    "example": "mov x9, #3          // loop 3 times\nLagain:             // loop top\n  subs x9, x9, #1   // x9 -= 1 and set the flags\n  b.ne Lagain       // repeat while x9 != 0 (body runs 3 times)",
    "watch": [
      "`b.ne` after a plain `sub` tests stale flags; use `subs` or `cmp`.",
      "To compare one register with zero, `cbnz Xt, label` needs no flags at all."
    ]
  },
  "b.lt": {
    "summary": "branch if less than (signed)",
    "what": "`b.lt label` jumps if the last `cmp a, b` found a < b with both treated as **signed** numbers, so -5 counts as less than 3. It checks the flags N != V. If the condition is false, execution continues on the next line. Typical uses: base cases (\"if n < 2, return n\") and loop bounds on signed counters.",
    "params": {
      "label": "where to jump when a < b, e.g. `Lsmaller`"
    },
    "example": "mov x9, #-5         // x9 = -5\ncmp x9, #3          // -5 vs 3\nb.lt Lsmaller       // taken: -5 < 3 (signed)",
    "watch": [
      "For unsigned values use `b.lo`; there -5 is a huge number and the branch would not be taken.",
      "`cmp x0, x1; b.lt` jumps when x0 < x1."
    ]
  },
  "bl": {
    "summary": "call a function (branch with link)",
    "what": "`bl label` calls a function: it stores the address of the next instruction in `x30` (the **link register**) and jumps to `label`. When that function runs `ret`, it jumps to `x30`, so execution resumes right after your `bl`. Arguments go in `x0`–`x7` before the call and the result comes back in `x0`. The callee may overwrite `x0`–`x18` and `x30`, so anything you need afterwards must live in a callee-saved register (`x19`–`x28`) or on the stack.",
    "params": {
      "label": "the function to call, e.g. `_square` (C functions on macOS start with an underscore)"
    },
    "example": "mov x0, #10         // argument: 10\nbl _square          // x30 = return address; jump to _square\nadd x9, x0, #1      // back here with x0 = 100 (the result); x9 = 101",
    "watch": [
      "`bl` overwrites `x30`, so a function that calls others must save `x30` (with `x29`) on entry and restore it before its own `ret`.",
      "Values in `x0`–`x18` may be destroyed by the call; keep them in `x19`–`x28` (saved first) instead."
    ]
  },
  "ldp": {
    "summary": "load two registers from consecutive memory",
    "what": "`ldp Xt1, Xt2, [Xn]` (\"load pair\") reads 16 bytes at the address in `Xn`: the first 8 bytes go to `Xt1`, the next 8 to `Xt2`. It has the same addressing options as `ldr`: an offset `[Xn, #16]`, **post-index** `[Xn], #16` (load, then add 16 to `Xn`) or **pre-index** `[Xn, #16]!` (add first, then load). Its main job is the function epilogue: restoring registers that a matching `stp` saved on the stack and, with post-index on `sp`, releasing that stack space in the same instruction.",
    "params": {
      "Xt1": "gets the 8 bytes at the address, e.g. `x9`",
      "Xt2": "gets the following 8 bytes, e.g. `x10`",
      "Xn": "base address register, e.g. `x0` or `sp`",
      "#imm": "byte offset, a multiple of 8 from -512 to 504"
    },
    "example": "// x0 points at {1, 2, 3, 4}\nldp x9, x10, [x0]        // x9 = 1, x10 = 2\nldp x9, x10, [x0, #16]   // x9 = 3, x10 = 4; x0 unchanged\nldp x9, x10, [x0], #16   // x9 = 1, x10 = 2; then x0 += 16",
    "watch": [
      "Restore registers in the same pairs and at the same offsets you saved them with `stp`.",
      "With `sp` as the base, keep `sp` a multiple of 16.",
      "Post-index (`[Xn], #k`) changes `Xn`; a plain offset (`[Xn, #k]`) does not."
    ]
  }
};
for (const e of entries) if (e.kind === 'instruction' && LEARN[e.name]) e.learn = LEARN[e.name];

export default entries;
