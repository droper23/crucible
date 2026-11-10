// x86-64 (AT&T syntax, Apple clang on macOS, System V AMD64 ABI) reference for Crucible's editor (hover / completion / signature help).
const ins = (name, sig, doc, example, insert) => ({ name, kind: 'instruction', sig, doc, example, ...(insert ? { insert } : {}) });
const dir = (name, sig, doc, example, insert) => ({ name, kind: 'directive', sig, doc, example, ...(insert ? { insert } : {}) });
const reg = (name, sig, doc, example) => ({ name, kind: 'constant', sig, doc, example });

const CC = 'System V AMD64 ABI: args in `%rdi`, `%rsi`, `%rdx`, `%rcx`, `%r8`, `%r9`; return in `%rax`; callee-saved `%rbx`, `%rbp`, `%r12`–`%r15`; everything else is clobbered by `call`. `%rsp` must be 16-byte aligned at each `call`.';
const ATT = 'AT&T order is **source, destination**.';

// [suffix, meaning, flags, unsigned?]
const conds = [
  ['e', 'equal / zero', 'ZF=1', 'after `cmpq %rsi, %rdi`: rdi == rsi. Alias `z`.'],
  ['ne', 'not equal / not zero', 'ZF=0', 'rdi != rsi. Alias `nz`.'],
  ['l', 'less (signed)', 'SF≠OF', 'rdi < rsi, signed. Alias `nge`.'],
  ['le', 'less or equal (signed)', 'ZF=1 or SF≠OF', 'rdi <= rsi, signed. Alias `ng`.'],
  ['g', 'greater (signed)', 'ZF=0 and SF=OF', 'rdi > rsi, signed. Alias `nle`.'],
  ['ge', 'greater or equal (signed)', 'SF=OF', 'rdi >= rsi, signed. Alias `nl`.'],
  ['b', 'below (unsigned <)', 'CF=1', 'rdi < rsi, unsigned (indices, pointers). Aliases `c`, `nae`.'],
  ['be', 'below or equal (unsigned <=)', 'CF=1 or ZF=1', 'rdi <= rsi, unsigned. Alias `na`.'],
  ['a', 'above (unsigned >)', 'CF=0 and ZF=0', 'rdi > rsi, unsigned. Alias `nbe`.'],
  ['ae', 'above or equal (unsigned >=)', 'CF=0', 'rdi >= rsi, unsigned. Aliases `nc`, `nb`.'],
  ['s', 'sign (negative result)', 'SF=1', 'result < 0 (e.g. after `testq %rax, %rax`).'],
  ['ns', 'not sign (non-negative result)', 'SF=0', 'result >= 0.'],
];
const OPS = { e: '==', ne: '!=', l: '<', le: '<=', g: '>', ge: '>=', b: '<', be: '<=', a: '>', ae: '>=' };
const rel = (c, x, y) => (c === 's' ? `${x} - ${y} < 0` : c === 'ns' ? `${x} - ${y} >= 0` : `${x} ${OPS[c]} ${y}${'b be a ae'.split(' ').includes(c) ? ' unsigned' : ''}`);
const CMPNOTE = 'Flags come from the last flag-setting instruction (`cmp`, `test`, `add`, `sub`, `and`...). **AT&T operand order is reversed**: `cmpq %rsi, %rdi` compares `%rdi` against `%rsi`.';

const jcc = [];
for (const [c, meaning, flags, use] of conds) {
  jcc.push(ins(`j${c}`, `j${c} label`, `Jump if ${meaning} (${flags}): ${use} ${CMPNOTE}`, `cmpq %rsi, %rdi\nj${c} 1f        # taken if ${rel(c, 'rdi', 'rsi')}`, `j${c} \${1:label}`));
}
jcc.push(ins('jz', 'jz label', 'Jump if zero (ZF=1). Same instruction as `je`; reads better after `test`.', 'testq %rax, %rax\njz 1f           # taken if rax == 0'));
jcc.push(ins('jnz', 'jnz label', 'Jump if not zero (ZF=0). Same instruction as `jne`.', 'decq %rcx\njnz 1b          # loop until rcx hits 0'));

const setcc = ['e', 'ne', 'l', 'le', 'g', 'ge', 'b', 'be', 'a', 'ae', 's', 'ns'].map((c) => {
  const [, meaning, flags] = conds.find((x) => x[0] === c);
  return ins(`set${c}`, `set${c} r/m8`, `Set a **byte** to 1 if ${meaning} (${flags}), else 0. Only writes 8 bits: zero-extend with \`movzbl %al, %eax\` (or \`xorl %eax, %eax\` **before** the \`cmp\`, since \`xor\` clobbers flags).`, `xorl %eax, %eax\ncmpq %rsi, %rdi\nset${c} %al       # rax = (${rel(c, 'rdi', 'rsi')})`, `set${c} \${1:%al}`);
});
setcc.push(ins('setz', 'setz r/m8', 'Same as `sete`: byte = 1 if ZF=1.', 'testq %rdi, %rdi\nsetz %al         # al = (rdi == 0)'));
setcc.push(ins('setnz', 'setnz r/m8', 'Same as `setne`: byte = 1 if ZF=0.', 'testq %rdi, %rdi\nsetnz %al        # al = (rdi != 0)'));

const cmov = ['e', 'ne', 'l', 'le', 'g', 'ge', 'b', 'be', 'a', 'ae', 's', 'ns'].map((c) => {
  const [, meaning, flags] = conds.find((x) => x[0] === c);
  return ins(`cmov${c}`, `cmov${c}q src, %reg`, `Conditional move if ${meaning} (${flags}). Source is a register or memory (**no immediates**); destination is a 16/32/64-bit register. A 32-bit \`cmovl\`-style form zero-extends the destination even when the move is not taken. Memory source is read even if the condition is false.`, `movq %rdi, %rax\ncmpq %rdi, %rsi\ncmov${c}q %rsi, %rax   # if (${rel(c, 'rsi', 'rdi')}) rax = rsi`, `cmov${c}q \${1:%rsi}, \${2:%rax}`);
});

// [name, 64, 32, 16, 8, role]
const gpr = [
  ['rax', 'eax', 'ax', 'al', '**Return value.** Caller-saved. Implicit operand of `mul`/`imul` (1-op)/`div`/`idiv`/`cqto`/`cltq`/`cmpxchg`; `%al` holds the vector-register count for variadic calls like `printf`.'],
  ['rbx', 'ebx', 'bx', 'bl', '**Callee-saved**: `pushq %rbx` in the prologue if you use it, `popq %rbx` before `ret`. Survives calls you make.'],
  ['rcx', 'ecx', 'cx', 'cl', '**Argument #4.** Caller-saved. `%cl` is the only register usable as a variable shift count (`shlq %cl, %rax`).'],
  ['rdx', 'edx', 'dx', 'dl', '**Argument #3**, and the high half of 128-bit results: `mul`/`imul` (1-op) write `%rdx:%rax`; `div`/`idiv` read `%rdx:%rax` and leave the remainder in `%rdx`. Caller-saved.'],
  ['rsi', 'esi', 'si', 'sil', '**Argument #2.** Caller-saved. For a Crucible `int[]` first parameter this is the element count.'],
  ['rdi', 'edi', 'di', 'dil', '**Argument #1.** Caller-saved. For a Crucible `int[]` parameter this is the pointer (count follows in the next register).'],
  ['rbp', 'ebp', 'bp', 'bpl', '**Frame pointer**, callee-saved. Framed prologue: `pushq %rbp; movq %rsp, %rbp`; epilogue `leave` (or `popq %rbp`). Locals at negative offsets: `-8(%rbp)`.'],
  ['rsp', 'esp', 'sp', 'spl', '**Stack pointer.** Grows down. Must be 16-byte aligned right before every `call` (on entry it is 8 mod 16 because `call` pushed the return address). Leaf functions may use the 128-byte **red zone** below `%rsp` without adjusting it.'],
];
const regs = [];
for (const [r, d, w, b, role] of gpr) {
  regs.push(reg(r, `%${r} (64-bit) / %${d} / %${w} / %${b}`, role + ' Writing the 32-bit `%' + d + '` zero-extends into `%' + r + '`; writing `%' + w + '`/`%' + b + '` leaves the other bits unchanged.', r === 'rax' ? 'movq %rdi, %rax       # rax = rdi (return value)' : `movq %${r}, %rax       # rax = ${r}`));
}
for (let i = 8; i <= 15; i++) {
  let role;
  if (i === 8) role = '**Argument #5.** Caller-saved.';
  else if (i === 9) role = '**Argument #6.** Caller-saved. Args 7+ go on the stack at `8(%rsp)`, `16(%rsp)`... on entry.';
  else if (i <= 11) role = 'Scratch register, caller-saved (free in a leaf function; clobbered by any `call`).' + (i === 10 ? ' Also the static-chain register.' : '');
  else role = '**Callee-saved**: push it in the prologue if you use it and pop it before `ret`. Good home for values that must survive a `call`.';
  regs.push(reg(`r${i}`, `%r${i} (64-bit) / %r${i}d / %r${i}w / %r${i}b`, role + ` Sub-registers: \`%r${i}d\` (32, zero-extends), \`%r${i}w\` (16), \`%r${i}b\` (8).`, `movq %r${i}, %rax       # rax = r${i}`));
}

const sub = (name, sig, doc, example) => reg(name, sig, doc, example);
const subs = [
  sub('eax', '%eax: low 32 bits of %rax', 'Writing `%eax` **zero-extends** into `%rax`. `xorl %eax, %eax` is the idiomatic way to zero `%rax` (shorter than `xorq`). Returning a C `int` uses `%eax`.', 'xorl %eax, %eax     # rax = 0'),
  sub('ax', '%ax: low 16 bits of %rax', 'Writing `%ax` leaves bits 16–63 unchanged (no zero-extension). Rarely needed.', 'movw $7, %ax        # rax bits 0-15 = 7'),
  sub('al', '%al: low 8 bits of %rax', 'Target of `setcc`. Writing `%al` keeps the rest of `%rax`; follow with `movzbl %al, %eax` to get a clean 0/1.', 'sete %al\nmovzbl %al, %eax    # rax = 0 or 1'),
  sub('ah', '%ah: bits 8–15 of %rax', 'Legacy high-byte register. Cannot be used in an instruction that needs a REX prefix (e.g. together with `%sil`, `%dil`, `%r8b`).', 'movb %ah, %cl       # cl = (rax >> 8) & 0xff'),
  sub('edi', '%edi: low 32 bits of %rdi', 'First argument as a 32-bit `int`. Writing it zero-extends into `%rdi`. Crucible ints are 64-bit, so prefer `%rdi`.', 'movl %edi, %eax     # rax = (uint32)rdi'),
  sub('di', '%di: low 16 bits of %rdi', 'Partial write: bits 16–63 unchanged.', 'movw %di, %ax       # ax = low 16 of rdi'),
  sub('dil', '%dil: low 8 bits of %rdi', 'Requires a REX prefix (cannot be mixed with `%ah`–`%dh`). Holds a `char`/`bool` first argument.', 'movzbl %dil, %eax   # eax = (unsigned char)rdi'),
  sub('esi', '%esi: low 32 bits of %rsi', 'Second argument as a 32-bit `int`; writing it zero-extends into `%rsi`.', 'movl %esi, %eax     # rax = (uint32)rsi'),
  sub('si', '%si: low 16 bits of %rsi', 'Partial write: bits 16–63 unchanged.', 'movw %si, %ax       # ax = low 16 of rsi'),
  sub('sil', '%sil: low 8 bits of %rsi', 'Requires a REX prefix. Second argument as a `char`.', 'cmpb $65, %sil      # compare low byte with \'A\''),
  sub('edx', '%edx: low 32 bits of %rdx', 'Third argument as a 32-bit int. `xorl %edx, %edx` zeroes `%rdx` before an unsigned `divq`.', 'xorl %edx, %edx     # rdx = 0\ndivq %rcx'),
  sub('dx', '%dx: low 16 bits of %rdx', 'Partial write: bits 16–63 unchanged.', 'movw %dx, %ax       # ax = low 16 of rdx'),
  sub('dl', '%dl: low 8 bits of %rdx', 'Low byte of the third argument; handy scratch byte for `movb`/`cmpb`.', 'movb (%rdi), %dl    # dl = *s'),
  sub('ecx', '%ecx: low 32 bits of %rcx', 'Fourth argument as a 32-bit int; writing it zero-extends into `%rcx`.', 'movl $10, %ecx      # rcx = 10'),
  sub('cx', '%cx: low 16 bits of %rcx', 'Partial write: bits 16–63 unchanged.', 'movw %cx, %ax       # ax = low 16 of rcx'),
  sub('cl', '%cl: low 8 bits of %rcx', 'The **only** register allowed as a variable shift/rotate count: `shlq %cl, %rax`. Count is taken mod 64 (mod 32 for 32-bit shifts).', 'movq %rsi, %rcx\nshlq %cl, %rax      # rax <<= rsi'),
  sub('r8d', '%r8d: low 32 bits of %r8', 'Fifth argument as a 32-bit int; writing it zero-extends into `%r8`.', 'movl %r8d, %eax     # rax = (uint32)r8'),
  sub('r8w', '%r8w: low 16 bits of %r8', 'Partial write: bits 16–63 unchanged.', 'movw %r8w, %ax      # ax = low 16 of r8'),
  sub('r8b', '%r8b: low 8 bits of %r8', 'Low byte of `%r8` (Intel docs also call it `r8l`).', 'movb (%rdi), %r8b   # r8b = *s'),
  reg('rip', '%rip (instruction pointer)', 'Not directly writable; used for **RIP-relative addressing**, which macOS requires for data: `leaq msg(%rip), %rdi` or `movq count(%rip), %rax`. Absolute `movq count, %rax` fails to link in 64-bit Mach-O.', 'leaq table(%rip), %rax   # rax = &table'),
  reg('rflags', 'RFLAGS (status flags)', 'Condition flags: **ZF** zero, **SF** sign, **CF** carry/unsigned borrow, **OF** signed overflow. Set by `cmp`, `test`, arithmetic and logic; **not** by `mov`, `lea`, `push`/`pop`, `jmp`, `call`. `inc`/`dec` leave CF unchanged.', 'cmpq %rsi, %rdi     # flags from rdi - rsi\njl less             # SF != OF'),
];

const prologue = 'pushq %rbp\nmovq %rsp, %rbp\n$0\nleave\nret';

export default [
  // ---------- data movement ----------
  ins('mov', 'mov{b,w,l,q} src, dst', `Copy src to dst. ${ATT} Suffix gives the size: \`b\`=1, \`w\`=2, \`l\`=4, \`q\`=8 bytes (optional when a register fixes it). At most **one memory operand** (no mem-to-mem). Immediates are 32-bit sign-extended (use \`movabsq\` for full 64-bit). \`movl\` to a register zero-extends to 64 bits; \`movb\`/\`movw\` do not. No flags.`, 'movq %rdi, %rax        # rax = rdi\nmovq 8(%rdi), %rcx     # rcx = a[1]\nmovq $0, (%rdi)        # a[0] = 0', 'movq ${1:%rdi}, ${2:%rax}'),
  ins('movq', 'movq src, dst', 'Move 8 bytes. Immediates are 32-bit sign-extended; clang silently turns `movq $0x100000000, %rax` into `movabsq`, but a store like `movq $0x100000000, (%rdi)` is rejected.', 'movq (%rdi,%rcx,8), %rax   # rax = a[i]', 'movq ${1:%rdi}, ${2:%rax}'),
  ins('movl', 'movl src, dst', 'Move 4 bytes. Writing a 32-bit register **zero-extends** into the 64-bit one, so `movl $5, %eax` sets `%rax = 5`. Use `movslq` to sign-extend instead.', 'movl $1, %eax          # rax = 1 (upper half cleared)'),
  ins('movb', 'movb src, dst', 'Move 1 byte. Writing `%al`-style registers keeps the upper 56 bits; load bytes with `movzbl`/`movzbq` to get a clean value.', 'movb $0, (%rdi)        # *s = \'\\0\'\nmovb %al, (%rsi,%rcx)  # dst[i] = al'),
  ins('movw', 'movw src, dst', 'Move 2 bytes. Partial write: upper bits of the destination register are unchanged.', 'movw $0x4142, (%rdi)   # store bytes "BA" (little-endian)'),
  ins('movabsq', 'movabsq $imm64, %reg', 'Load a full 64-bit immediate into a register (the only instruction that takes one: `addq`/`cmpq`/stores need the constant in a register). Also loads/stores an absolute 64-bit address with `%rax`.', 'movabsq $0x123456789, %rax   # rax = 0x123456789'),
  ins('movzbq', 'movzbq src8, %reg64', 'Load/copy a byte and **zero-extend** to 64 bits (Intel `movzx`). The right way to read an `unsigned char` / string byte.', 'movzbq (%rdi), %rax    # rax = (unsigned char)*s'),
  ins('movzbl', 'movzbl src8, %reg32', 'Zero-extend a byte to 32 bits; since 32-bit writes clear the upper half, this zero-extends to 64 too and is 1 byte shorter than `movzbq`. Clang prefers it.', 'movzbl (%rdi,%rcx), %eax   # rax = s[i]\nmovzbl %al, %eax           # after setcc'),
  ins('movzwl', 'movzwl src16, %reg32', 'Zero-extend a 16-bit value (also clears bits 32–63). `movzwq` is the 64-bit spelling.', 'movzwl (%rdi), %eax    # rax = *(uint16_t*)p'),
  ins('movsbq', 'movsbq src8, %reg64', 'Load/copy a byte and **sign-extend** to 64 bits (Intel `movsx`): C `signed char` -> `long`.', 'movsbq (%rdi), %rax    # 0xFF -> -1'),
  ins('movsbl', 'movsbl src8, %reg32', 'Sign-extend a byte to 32 bits (upper 32 then zeroed, not sign-filled). Use `movsbq` when you need a 64-bit signed value.', 'movsbl (%rdi), %eax    # eax = (int)(signed char)*s'),
  ins('movslq', 'movslq src32, %reg64', 'Sign-extend a 32-bit value to 64 bits (Intel `movsxd`): C `int` -> `long`. Read `int[]` elements with `movslq (%rdi,%rcx,4), %rax`.', 'movslq %edi, %rax      # rax = (long)(int)rdi'),
  ins('lea', 'lea{l,q} disp(base,index,scale), %reg', '**Load effective address**: computes the address expression **without touching memory** and without setting flags. Doubles as cheap arithmetic: `leaq (%rdi,%rdi,2), %rax` = `rdi*3`; `leaq 1(%rax), %rax` = `rax+1`. Scale is 1, 2, 4 or 8. Also `leaq sym(%rip), %reg` for a data address.', 'leaq (%rdi,%rsi,8), %rax   # rax = &a[i]\nleaq 5(%rdi,%rsi), %rax    # rax = rdi + rsi + 5', 'leaq ${1:0}(${2:%rdi},${3:%rsi},${4:8}), ${5:%rax}'),
  ins('leaq', 'leaq disp(base,index,scale), %reg64', '64-bit `lea`: `reg = base + index*scale + disp`. No memory access, no flags.', 'leaq (%rdi,%rsi,4), %rax   # rax = rdi + rsi*4\nleaq msg(%rip), %rdi       # rdi = &msg'),
  ins('xchg', 'xchg{q} %reg, %reg|mem', 'Swap two operands. With a memory operand it is **implicitly locked** (atomic, slow). Swapping two registers is fine.', 'xchgq %rax, %rdx       # swap rax and rdx'),
  ins('cmpxchg', 'lock cmpxchg{q} %reg, mem', 'Compare-and-swap: if `%rax == mem` then `mem = reg` and ZF=1; else `%rax = mem` and ZF=0. Add `lock` for an atomic CAS. Rarely needed in single-threaded problems.', 'movq $0, %rax\nlock cmpxchgq %rcx, (%rdi)   # if *p==0: *p=rcx'),

  // ---------- arithmetic ----------
  ins('add', 'add{b,w,l,q} src, dst', `\`dst += src\`. ${ATT} Sets ZF/SF/CF/OF. Immediates are 32-bit sign-extended.`, 'addq %rsi, %rax        # rax += rsi\naddq $8, %rdi          # p++ (8-byte elements)', 'addq ${1:%rsi}, ${2:%rax}'),
  ins('addq', 'addq src, dst', '64-bit `dst += src`; sets flags.', 'addq (%rdi,%rcx,8), %rax   # sum += a[i]'),
  ins('sub', 'sub{b,w,l,q} src, dst', `\`dst -= src\`. ${ATT} \`subq %rsi, %rax\` is \`rax = rax - rsi\`. Sets flags like \`cmp\`.`, 'subq %rsi, %rax        # rax -= rsi\nsubq $16, %rsp         # reserve 16 bytes', 'subq ${1:%rsi}, ${2:%rax}'),
  ins('subq', 'subq src, dst', '64-bit `dst -= src`; sets flags (CF = unsigned borrow).', 'subq $1, %rsi          # n--'),
  ins('imul', 'imul{q} src | imul{q} src, %reg | imul{q} $imm, src, %reg', 'Signed multiply. **1-operand**: `%rdx:%rax = %rax * src` (128-bit). **2-operand**: `reg *= src` (low 64 bits). **3-operand**: `reg = src * imm` (imm is 32-bit sign-extended). CF/OF set on signed overflow; ZF/SF undefined.', 'imulq %rsi, %rax          # rax *= rsi\nimulq $10, %rdi, %rax     # rax = rdi * 10', 'imulq ${1:%rsi}, ${2:%rax}'),
  ins('imulq', 'imulq src, %reg | imulq $imm, src, %reg | imulq src', '64-bit signed multiply. Low 64 bits are identical for signed and unsigned, so 2/3-operand `imulq` serves for both. `jo` after it detects overflow.', 'imulq %rcx, %rax          # rax *= rcx\njo overflow'),
  ins('mul', 'mul{q} src', 'Unsigned multiply: `%rdx:%rax = %rax * src` (high 64 bits in `%rdx`). One operand only; **clobbers `%rdx`**. For plain low-64-bit products use `imulq`.', 'movq %rdi, %rax\nmulq %rsi                # rdx:rax = rdi * rsi'),
  ins('idiv', 'idiv{q} src', 'Signed divide of the 128-bit `%rdx:%rax` by src: quotient -> `%rax`, remainder -> `%rdx` (same sign as the dividend, like C). **Sign-extend first with `cqto`**. Divide by zero or `INT64_MIN / -1` raises #DE -> SIGFPE crash. No immediate operand.', 'movq %rdi, %rax\ncqto                     # rdx:rax = sign-extended rdi\nidivq %rsi               # rax = rdi / rsi, rdx = rdi % rsi', 'movq ${1:%rdi}, %rax\ncqto\nidivq ${2:%rsi}'),
  ins('div', 'div{q} src', 'Unsigned divide of `%rdx:%rax` by src: quotient `%rax`, remainder `%rdx`. **Zero `%rdx` first** (`xorl %edx, %edx`); garbage in `%rdx` gives wrong results or a SIGFPE if the quotient overflows.', 'movq %rdi, %rax\nxorl %edx, %edx\ndivq %rsi                # rax = rdi / rsi (unsigned)'),
  ins('cqto', 'cqto', 'Sign-extend `%rax` into `%rdx:%rax` (Intel `cqo`): `%rdx` becomes 0 or -1. Required before `idivq`.', 'movq %rdi, %rax\ncqto                     # rdx = (rax < 0) ? -1 : 0'),
  ins('cltd', 'cltd', 'Sign-extend `%eax` into `%edx:%eax` (Intel `cdq`). Use before 32-bit `idivl`.', 'movl %edi, %eax\ncltd\nidivl %esi               # eax = edi / esi'),
  ins('cltq', 'cltq', 'Sign-extend `%eax` into `%rax` (Intel `cdqe`); same as `movslq %eax, %rax`.', 'movl $-1, %eax           # rax = 0x00000000FFFFFFFF\ncltq                     # rax = -1'),
  ins('inc', 'inc{b,w,l,q} dst', '`dst += 1`. Sets ZF/SF/OF but **leaves CF unchanged**.', 'incq %rcx                # i++', 'incq ${1:%rcx}'),
  ins('dec', 'dec{b,w,l,q} dst', '`dst -= 1`. Sets ZF/SF/OF (not CF). `decq %rcx; jnz loop` counts down.', 'decq %rsi                # n--\njnz 1b'),
  ins('neg', 'neg{b,w,l,q} dst', 'Two\'s-complement negate: `dst = -dst`. CF = (dst != 0). `-INT64_MIN` stays `INT64_MIN` (OF=1).', 'negq %rax                # rax = -rax'),
  ins('incq', 'incq dst', '64-bit increment; CF unchanged.', 'incq %rax                # rax++'),
  ins('decq', 'decq dst', '64-bit decrement; CF unchanged.', 'decq %rcx                # rcx--'),
  ins('negq', 'negq dst', '64-bit negate.', 'negq %rdi                # rdi = -rdi'),

  // ---------- logic / shifts ----------
  ins('and', 'and{b,w,l,q} src, dst', '`dst &= src`. Clears CF/OF; sets ZF/SF. `andq $1, %rax` keeps the low bit.', 'andq $1, %rax            # rax = rax & 1 (odd?)'),
  ins('andq', 'andq src, dst', '64-bit AND. Immediates are 32-bit sign-extended (`$-16` = `0xFFFF...FFF0`, good for aligning).', 'andq $-16, %rsp          # align rsp down to 16'),
  ins('or', 'or{b,w,l,q} src, dst', '`dst |= src`. Clears CF/OF.', 'orq %rsi, %rax           # rax |= rsi'),
  ins('orq', 'orq src, dst', '64-bit OR. `orq %rax, %rax` sets ZF/SF like `test`.', 'orq $0x20, %rax          # set bit 5'),
  ins('xor', 'xor{b,w,l,q} src, dst', '`dst ^= src`. `xorl %eax, %eax` is the idiomatic zero (clears all 64 bits, **clobbers flags**). XOR-of-all finds the unpaired number.', 'xorq (%rdi), %rax        # rax ^= *p'),
  ins('xorl', 'xorl src, dst', '32-bit XOR; `xorl %eax, %eax` zeroes all of `%rax` (32-bit write zero-extends) in 2 bytes. Do it **before** a `cmp`, not between `cmp` and `setcc`.', 'xorl %eax, %eax          # rax = 0'),
  ins('not', 'not{b,w,l,q} dst', 'Bitwise complement `dst = ~dst`. Sets **no** flags.', 'notq %rax                # rax = ~rax'),
  ins('shl', 'shl{b,w,l,q} $imm|%cl, dst', 'Shift left (`dst <<= n`); same as `sal`. Count is an immediate or **`%cl` only**, masked to 6 bits (5 for 32-bit). Beware: clang accepts `shlq %rcx, %rax` but encodes a newer APX instruction that crashes with *Illegal instruction*. A 1-operand `shlq %rax` shifts by 1.', 'shlq $3, %rax            # rax *= 8\nshlq %cl, %rdx           # rdx <<= cl'),
  ins('sal', 'sal{b,w,l,q} $imm|%cl, dst', 'Arithmetic shift left: identical to `shl`.', 'salq $1, %rax            # rax *= 2'),
  ins('shr', 'shr{b,w,l,q} $imm|%cl, dst', 'Logical shift right (zero-fill): unsigned divide by 2^n. Last bit shifted out goes to CF.', 'shrq $1, %rax            # unsigned rax / 2'),
  ins('sar', 'sar{b,w,l,q} $imm|%cl, dst', 'Arithmetic shift right (sign-fill). Rounds toward **−infinity**, unlike `idiv` which truncates toward zero (`-3 sar 1 = -2`, `-3 / 2 = -1`). `sarq $63, %rax` gives 0 or -1 (sign mask).', 'sarq $63, %rdx           # rdx = (rdx < 0) ? -1 : 0'),
  ins('shlq', 'shlq $imm|%cl, dst', '64-bit left shift.', 'shlq $4, %rax            # rax <<= 4'),
  ins('shrq', 'shrq $imm|%cl, dst', '64-bit logical right shift (zero-fill).', 'shrq $1, %rdi            # rdi >>= 1 (unsigned)'),
  ins('sarq', 'sarq $imm|%cl, dst', '64-bit arithmetic right shift (keeps the sign, floors).', 'sarq $1, %rax            # rax >>= 1 (signed, floor)'),
  ins('rol', 'rol{b,w,l,q} $imm|%cl, dst', 'Rotate left; bits shifted out re-enter on the right.', 'rolq $8, %rax            # rotate left one byte'),
  ins('ror', 'ror{b,w,l,q} $imm|%cl, dst', 'Rotate right.', 'rorq $1, %rax            # low bit moves to bit 63'),
  ins('test', 'test{b,w,l,q} src, dst', 'Set flags from `dst & src` and discard the result (ZF, SF; CF=OF=0). `testq %rax, %rax` checks zero / negative; `testb $1, %al` checks odd.', 'testq %rdi, %rdi\nje is_zero               # rdi == 0', 'testq ${1:%rax}, ${2:%rax}'),
  ins('testq', 'testq src, dst', '64-bit `test`. Follow with `je`/`jz` (zero), `js` (negative), `jle` (<= 0, signed).', 'testq %rsi, %rsi\njle done                 # n <= 0'),
  ins('cmp', 'cmp{b,w,l,q} src, dst', 'Set flags from `dst - src` and discard the result. **AT&T order is reversed**: `cmpq %rsi, %rdi` then `jl` jumps if `rdi < rsi`. Immediate must be the first (src) operand: `cmpq $10, %rax`.', 'cmpq $10, %rax\njge done                 # if rax >= 10', 'cmpq ${1:%rsi}, ${2:%rdi}'),
  ins('cmpq', 'cmpq src, dst', '64-bit compare: flags from `dst - src`. Read `cmpq A, B; jX` as "if B X A".', 'cmpq %rsi, %rcx\njl 1b                    # loop while i < n'),
  ins('cmpb', 'cmpb src, dst', 'Compare one byte: `cmpb $0, (%rdi)` tests for the NUL terminator; `cmpb $\'a\', %al` compares chars.', 'cmpb $0, (%rdi)\nje done                  # *s == \'\\0\''),
  ins('popcnt', 'popcnt{q} src, %reg', 'Count set bits. Requires the POPCNT extension (supported by all x86-64 Macs and Rosetta 2). Sets ZF if src is 0.', 'popcntq %rdi, %rax       # rax = number of 1 bits'),
  ins('lzcnt', 'lzcnt{q} src, %reg', 'Count leading zero bits (64 for 0). Needs LZCNT/ABM (Haswell+). **On CPUs without it, the encoding silently runs as `bsr`** and gives wrong answers; `bsrq` + `xorq $63` is the portable fallback.', 'lzcntq %rdi, %rax        # rax = clz(rdi)'),
  ins('tzcnt', 'tzcnt{q} src, %reg', 'Count trailing zero bits (64 for 0). Needs BMI1; on older CPUs it executes as `bsf` (same result except for input 0).', 'tzcntq %rdi, %rax        # rax = ctz(rdi)'),
  ins('bsf', 'bsf{q} src, %reg', 'Bit scan forward: index of the lowest set bit. If src is 0, ZF=1 and the destination is **undefined**: check first.', 'bsfq %rdi, %rax          # rax = index of lowest 1 bit\njz was_zero'),
  ins('bsr', 'bsr{q} src, %reg', 'Bit scan reverse: index of the highest set bit (= 63 − clz). Destination undefined if src is 0 (ZF=1).', 'bsrq %rdi, %rax          # rax = floor(log2(rdi))'),

  // ---------- control flow ----------
  ins('jmp', 'jmp label | jmp *%reg', 'Unconditional jump. `jmp *%rax` jumps to the address in a register (jump tables, tail calls).', 'jmp 1b                   # back to label 1', 'jmp ${1:label}'),
  ...jcc,
  ...setcc,
  ...cmov,
  ins('call', 'call label | call *%reg', 'Push the return address (8 bytes) and jump. Calls C functions by their underscored name: `call _malloc`. **`%rsp` must be a multiple of 16 just before `call`**. Clobbers `%rax %rcx %rdx %rsi %rdi %r8`–`%r11` and flags.', 'movq %rbx, %rdi\ncall _helper             # rax = helper(rbx)', 'call _${1:func}'),
  ins('ret', 'ret', 'Pop the return address and jump to it. `%rsp` must point exactly where it did on entry (every `push` popped, every `sub` undone), or you return to garbage.', 'movq %rcx, %rax\nret                      # return rcx'),
  ins('push', 'push{q} src', '`%rsp -= 8; *(%rsp) = src`. Only 64-bit pushes in 64-bit mode. Save callee-saved registers in the prologue; each push changes alignment by 8.', 'pushq %rbx               # save rbx'),
  ins('pop', 'pop{q} dst', '`dst = *(%rsp); %rsp += 8`. Pop in **reverse** order of the pushes.', 'popq %rbx                # restore rbx'),
  ins('pushq', 'pushq src', 'Push 8 bytes (register, memory or 32-bit sign-extended immediate).', 'pushq %rbp\nmovq %rsp, %rbp'),
  ins('popq', 'popq dst', 'Pop 8 bytes into a register or memory.', 'popq %rbp\nret'),
  ins('leave', 'leave', 'Tear down a frame: `movq %rbp, %rsp; popq %rbp`. Pair with the `pushq %rbp; movq %rsp, %rbp` prologue, then `ret`.', 'leave                    # rsp = rbp; pop rbp\nret'),
  ins('enter', 'enter $size, $0', 'Builds a frame (`push %rbp; mov %rsp, %rbp; sub $size, %rsp`). Slow and **rarely used**; compilers emit the explicit sequence instead.', 'enter $16, $0            # frame with 16 bytes of locals'),
  ins('nop', 'nop', 'No operation (1 byte). Multi-byte `nopl`/`nopw` forms are alignment padding.', 'nop                      # does nothing'),

  // ---------- directives ----------
  dir('.text', '.text', 'Switch to the code section (`__TEXT,__text`). Functions go here.', '.text\n.globl _f'),
  dir('.data', '.data', 'Switch to the writable data section (`__DATA,__data`). Access with RIP-relative addressing: `movq counter(%rip), %rax`.', '.data\ncounter: .quad 0'),
  dir('.globl', '.globl symbol', 'Export a symbol so the harness can link to it. macOS prefixes C names with an underscore: `sum_array` must be `.globl _sum_array` with label `_sum_array:`.', '.globl _sum_array\n_sum_array:', '.globl _${1:name}'),
  dir('.p2align', '.p2align n{, fill}', 'Align to 2^n bytes. `.p2align 4` (16 bytes) before a function is what clang emits; x86 instructions themselves need no alignment.', '.p2align 4, 0x90         # 16-byte align, pad with nop', '.p2align ${1:4}'),
  dir('.align', '.align n', 'On Apple (Mach-O) targets `n` is a **power of two**, same as `.p2align` (`.align 3` = 8 bytes). GNU as on Linux x86 treats it as a byte count, so prefer `.p2align` for clarity.', '.align 3                 # 8-byte alignment on macOS'),
  dir('.quad', '.quad value, ...', 'Emit 8-byte values (Crucible `int` elements).', 'nums: .quad 10, 20, 30'),
  dir('.long', '.long value, ...', 'Emit 4-byte values (C `int`).', 'lut: .long 1, 2, 4, 8'),
  dir('.byte', '.byte value, ...', 'Emit single bytes.', 'bits: .byte 0, 1, 1, 2'),
  dir('.asciz', '.asciz "text"', 'Emit a string **with** a trailing NUL byte.', 'msg: .asciz "hello\\n"'),
  dir('.ascii', '.ascii "text"', 'Emit a string **without** a NUL terminator.', 'hex: .ascii "0123456789abcdef"'),
  dir('.zero', '.zero nbytes', 'Emit `nbytes` zero bytes (also `.space n`).', 'buf: .zero 64            # 64-byte zeroed buffer'),
  dir('.section', '.section segment,section{,type}', 'Select a Mach-O section, e.g. `__TEXT,__cstring,cstring_literals` for strings or `__TEXT,__const` for read-only tables. ELF names like `.rodata` do **not** work on macOS.', '.section __TEXT,__const\n.p2align 3\ntable: .quad 1, 2, 3'),
  dir('.intel_syntax', '.intel_syntax noprefix', 'Switch the assembler to Intel syntax (`mov rax, rdi`: destination first, no `%`/`$`). Crucible material uses AT&T; don\'t mix styles unintentionally.', '.intel_syntax noprefix\nmov rax, rdi             # rax = rdi'),
  dir('.att_syntax', '.att_syntax prefix', 'Switch back to AT&T syntax (the default): `%` on registers, `$` on immediates, source before destination.', '.att_syntax prefix\nmovq %rdi, %rax          # rax = rdi'),

  // ---------- registers ----------
  ...regs,
  ...subs,

  // ---------- snippets ----------
  { name: 'leaf', kind: 'snippet', sig: 'leaf function (no calls, no frame)', doc: CC + ' A leaf function can use the caller-saved registers freely and needs no prologue.', example: '.globl _f\n_f: leaq (%rdi,%rsi), %rax   # return a + b\n    ret', insert: '.text\n.globl _${1:name}\n.p2align 4\n_${1:name}:\n\t$0\n\tret' },
  { name: 'prologue', kind: 'snippet', sig: 'framed function (push %rbp ... leave; ret)', doc: CC + ' After `pushq %rbp` the stack is 16-byte aligned, so `subq` a multiple of 16 for locals (and push callee-saved registers in pairs, or pad by 8) before calling anything.', example: 'pushq %rbp\nmovq %rsp, %rbp          # ... call _g ...\nleave\nret', insert: prologue },
];
