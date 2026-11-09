// Crucible code generation: turns a problem's typed signature into starter code
// and a test harness for every supported language. Shared by the browser app and
// the Node validation tool (tools/check.mjs), so keep it dependency-free.
//
// Supported value types:
//   int float bool str            scalars
//   int[] float[] bool[] str[]    1-D arrays
//   int[][] float[][] str[][]     2-D arrays
//   list                          singly linked list of ints (JSON: [1,2,3])
//   tree                          binary tree of ints (JSON: LeetCode level order, nulls allowed)
//   void                          return type only; requires `mutates` (the param whose final value is the output)

export const LANGS = {
  python:   { id: 'python',   label: 'Python',   monaco: 'python',   ext: 'py',   comment: '#' },
  c:        { id: 'c',        label: 'C',        monaco: 'c',        ext: 'c',    comment: '//' },
  cpp:      { id: 'cpp',      label: 'C++',      monaco: 'cpp',      ext: 'cpp',  comment: '//' },
  rust:     { id: 'rust',     label: 'Rust',     monaco: 'rust',     ext: 'rs',   comment: '//' },
  espresso: { id: 'espresso', label: 'ESPresso', monaco: 'espresso', ext: 'espr', comment: '//' },
  asm:      { id: 'asm',      label: 'ARM64 Asm', monaco: 'arm64',   ext: 's',    comment: '//' },
};

export const MARK = '\x1e'; // record separator: prefixes harness result lines
const ESP_MARK = '@@CRUCIBLE';

// ---------------------------------------------------------------- helpers

export function parseType(t) {
  if (t === 'list' || t === 'tree' || t === 'void') return { base: t, dims: 0 };
  const m = /^(int|float|bool|str)((?:\[\])*)$/.exec(t);
  if (!m) throw new Error(`Unknown type "${t}"`);
  const dims = m[2].length / 2;
  if (dims > 2) throw new Error(`Type "${t}" nests too deeply (max 2)`);
  return { base: m[1], dims };
}

export const camel = (s) => s.replace(/_([a-z0-9])/g, (_, c) => c.toUpperCase());

export function fnName(problem, lang) {
  return lang === 'cpp' || lang === 'espresso' ? camel(problem.fn) : problem.fn;
}
function pName(name, lang) {
  return lang === 'cpp' || lang === 'espresso' ? camel(name) : name;
}

function mutIndex(problem) {
  if (!problem.mutates) return -1;
  const i = problem.params.findIndex(([n]) => n === problem.mutates);
  if (i < 0) throw new Error(`mutates="${problem.mutates}" is not a parameter`);
  return i;
}

/** Which languages can solve this problem. */
export function languagesFor(problem) {
  if (problem.kind === 'asm') return ['asm'];
  const all = ['python', 'c', 'cpp', 'rust'];
  if (problem.langs) return problem.langs.slice();
  if (espressoEligible(problem)) all.push('espresso');
  return all;
}

export function espressoEligible(problem) {
  if (problem.espresso === true) return true;
  if (problem.espresso === false) return false;
  if (problem.kind === 'io') return problem.tests.every((t) => !t.stdin);
  if (problem.kind !== 'function') return false;
  const okParam = (t) => ['int', 'float', 'bool', 'int[]', 'float[]', 'int[][]'].includes(t);
  const okRet = (t) => ['int', 'float', 'bool'].includes(t) || (t === 'void' && problem.mutates);
  if (!(problem.params.every(([, t]) => okParam(t)) && okRet(problem.returns))) return false;
  // ESPresso integers are 32-bit: every test value must fit.
  const fits = (v) => Array.isArray(v) ? v.every(fits) : typeof v !== 'number' || !Number.isInteger(v) || Math.abs(v) <= 2147483647;
  return problem.tests.every((t) => fits(t.args) && fits(t.expected));
}

// Escape a JS string into a C/C++ string literal body (UTF-8 bytes, octal escapes).
function cStr(s) {
  const bytes = new TextEncoder().encode(s);
  let out = '';
  for (const b of bytes) {
    if (b === 0x5c) out += '\\\\';
    else if (b === 0x22) out += '\\"';
    else if (b === 0x3f) out += '\\?'; // avoid trigraphs
    else if (b >= 0x20 && b < 0x7f) out += String.fromCharCode(b);
    else out += '\\' + b.toString(8).padStart(3, '0');
  }
  return '"' + out + '"';
}
function rustStr(s) {
  let out = '';
  for (const ch of s) {
    const c = ch.codePointAt(0);
    if (ch === '\\') out += '\\\\';
    else if (ch === '"') out += '\\"';
    else if (c < 0x20 || c === 0x7f) out += `\\u{${c.toString(16)}}`;
    else out += ch;
  }
  return '"' + out + '"';
}
function fnum(v) {
  // float literal with a decimal point
  if (v === null) return 'NAN';
  const s = String(v);
  return /[.eE]/.test(s) ? s : s + '.0';
}
function inum(v) {
  if (!Number.isSafeInteger(v)) throw new Error(`Integer ${v} is outside the safe range`);
  return String(v);
}

// ---------------------------------------------------------------- Python

const PY_TYPES = { int: 'int', float: 'float', bool: 'bool', str: 'str' };
function pyType(t) {
  const { base, dims } = parseType(t);
  if (base === 'list') return 'Optional[ListNode]';
  if (base === 'tree') return 'Optional[TreeNode]';
  if (base === 'void') return 'None';
  let s = PY_TYPES[base];
  for (let i = 0; i < dims; i++) s = `List[${s}]`;
  return s;
}

const PY_LIST_DOC = `# Definition for a singly-linked list node (provided for you):
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
`;
const PY_TREE_DOC = `# Definition for a binary tree node (provided for you):
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
`;

function usesType(problem, base) {
  return [...problem.params.map(([, t]) => t), problem.returns].some((t) => t === base);
}

function pythonStarter(p) {
  if (p.kind === 'io') {
    return `import sys\n\n\ndef main():\n    data = sys.stdin.read()\n    # Your code here: read from \`data\`, print the answer.\n\n\nmain()\n`;
  }
  let head = '';
  if (usesType(p, 'list')) head += PY_LIST_DOC + '\n';
  if (usesType(p, 'tree')) head += PY_TREE_DOC + '\n';
  const args = p.params.map(([n, t]) => `${n}: ${pyType(t)}`).join(', ');
  const body = p.mutates
    ? `    # Modify \`${p.mutates}\` in place; nothing needs to be returned.\n    pass\n`
    : `    # Your code here\n    pass\n`;
  return `${head}def ${p.fn}(${args}) -> ${pyType(p.returns)}:\n${body}`;
}

const PY_PRELUDE = String.raw`import sys as __cr_sys, json as __cr_json, traceback as __cr_tb, math
from typing import *
from collections import *
from functools import *
from itertools import *
from heapq import *
from bisect import *
import re, string, random
__cr_sys.setrecursionlimit(20000)

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
    def __repr__(self):
        return f"ListNode({self.val})"

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
    def __repr__(self):
        return f"TreeNode({self.val})"

def __cr_mk_list(a):
    head = None
    for v in reversed(a):
        head = ListNode(v, head)
    return head

def __cr_mk_tree(a):
    if not a or a[0] is None:
        return None
    root = TreeNode(a[0]); q = [root]; i = 1; qi = 0
    while i < len(a):
        node = q[qi]; qi += 1
        if i < len(a) and a[i] is not None:
            node.left = TreeNode(a[i]); q.append(node.left)
        i += 1
        if i < len(a) and a[i] is not None:
            node.right = TreeNode(a[i]); q.append(node.right)
        i += 1
    return root

def __cr_list_out(h):
    out = []
    while h is not None and len(out) < 100000:
        out.append(h.val); h = h.next
    return out

def __cr_tree_out(r):
    out = []; q = [r]; qi = 0
    while qi < len(q) and len(out) < 100000:
        n = q[qi]; qi += 1
        if n is None:
            out.append(None)
        else:
            out.append(n.val); q.append(n.left); q.append(n.right)
    while out and out[-1] is None:
        out.pop()
    return out

def __cr_in(v, t):
    if t == "list": return __cr_mk_list(v)
    if t == "tree": return __cr_mk_tree(v)
    if t.startswith("float"):
        return [__cr_in(x, t[:-2]) for x in v] if t.endswith("[]") else float(v)
    return v

def __cr_out(v, t):
    if t == "list": return __cr_list_out(v)
    if t == "tree": return __cr_tree_out(v)
    if isinstance(v, (tuple, set, frozenset, deque)):
        v = list(v)
    if isinstance(v, list):
        sub = t[:-2] if t.endswith("[]") else t
        return [__cr_out(x, sub) for x in v]
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    return v
`;

function pythonFunctionHarness(p, code, tests) {
  const mi = mutIndex(p);
  const types = p.params.map(([, t]) => t);
  const retType = mi >= 0 ? types[mi] : p.returns;
  return `${PY_PRELUDE}
__CR_SRC = ${JSON.stringify(code)}
exec(compile(__CR_SRC, "solution.py", "exec"), globals())
__CR_TESTS = __cr_json.loads(${JSON.stringify(JSON.stringify(tests.map((t) => t.args)))})
__CR_TYPES = ${JSON.stringify(types)}
for __cr_i, __cr_args in enumerate(__CR_TESTS):
    try:
        __cr_conv = [__cr_in(a, t) for a, t in zip(__cr_args, __CR_TYPES)]
        __cr_r = globals()[${JSON.stringify(p.fn)}](*__cr_conv)
        ${mi >= 0 ? `__cr_r = __cr_conv[${mi}]` : 'pass'}
        __cr_payload = __cr_json.dumps(__cr_out(__cr_r, ${JSON.stringify(retType)}))
        __cr_sys.stdout.write("\\x1eR %d %s\\n" % (__cr_i, __cr_payload))
    except RecursionError:
        __cr_sys.stdout.write("\\x1eE %d %s\\n" % (__cr_i, __cr_json.dumps("RecursionError: maximum recursion depth exceeded")))
    except Exception as __cr_e:
        __cr_lines = [l for l in __cr_tb.format_exc().splitlines() if '"<string>"' not in l and 'File "<exec>"' not in l]
        __cr_sys.stdout.write("\\x1eE %d %s\\n" % (__cr_i, __cr_json.dumps("\\n".join(__cr_lines[-6:]))))
    __cr_sys.stdout.flush()
`;
}

function pythonIoHarness(code) {
  // Run user code as a script named solution.py so tracebacks show real line numbers.
  return `import sys as __cr_sys\n__cr_sys.setrecursionlimit(20000)\n__CR_SRC = ${JSON.stringify(code)}\nexec(compile(__CR_SRC, "solution.py", "exec"), {"__name__": "__main__"})\n`;
}

// ---------------------------------------------------------------- C

const C_BASE = { int: 'long long', float: 'double', bool: 'bool', str: 'char*' };

function cParams(p, asm = false) {
  const sz = asm ? 'long long' : 'int';
  const out = [];
  for (const [n, t] of p.params) {
    const { base, dims } = parseType(t);
    if (base === 'list') out.push(`struct ListNode* ${n}`);
    else if (base === 'tree') out.push(`struct TreeNode* ${n}`);
    else if (dims === 0) out.push(`${C_BASE[base]} ${n}`);
    else if (dims === 1) out.push(`${C_BASE[base]}* ${n}`, `${sz} ${n}Size`);
    else out.push(`${C_BASE[base]}** ${n}`, `${sz} ${n}Size`, `${sz}* ${n}ColSize`);
  }
  return out;
}

function cReturn(p) {
  if (p.returns === 'void') return { type: 'void', extra: [] };
  const { base, dims } = parseType(p.returns);
  if (base === 'list') return { type: 'struct ListNode*', extra: [] };
  if (base === 'tree') return { type: 'struct TreeNode*', extra: [] };
  if (dims === 0) return { type: C_BASE[base], extra: [] };
  if (dims === 1) return { type: `${C_BASE[base]}*`, extra: ['int* returnSize'] };
  return { type: `${C_BASE[base]}**`, extra: ['int* returnSize', 'int** returnColumnSizes'] };
}

const C_LIST_DOC = `/* Provided for you:
 * struct ListNode { long long val; struct ListNode* next; };
 * Allocate new nodes with malloc(sizeof(struct ListNode)).
 */
`;
const C_TREE_DOC = `/* Provided for you:
 * struct TreeNode { long long val; struct TreeNode* left; struct TreeNode* right; };
 */
`;

function cSig(p) {
  const r = cReturn(p);
  return `${r.type} ${p.fn}(${[...cParams(p), ...r.extra].join(', ')})`;
}

function cStarter(p) {
  if (p.kind === 'io') {
    return `#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n\nint main(void) {\n    // Your code here: read with scanf/fgets, print with printf.\n    return 0;\n}\n`;
  }
  let head = '';
  if (usesType(p, 'list')) head += C_LIST_DOC;
  if (usesType(p, 'tree')) head += C_TREE_DOC;
  const r = cReturn(p);
  let note = '';
  if (r.extra.length === 1) note = '    // Return a malloc-ed array and set *returnSize to its length.\n';
  if (r.extra.length === 2) note = '    // Return a malloc-ed array of malloc-ed rows; set *returnSize to the row count\n    // and *returnColumnSizes to a malloc-ed array holding each row\'s length.\n';
  if (p.returns === 'str') note = '    // Return a malloc-ed, NUL-terminated string.\n';
  if (p.mutates) note = `    // Modify \`${p.mutates}\` in place.\n`;
  const ret = { void: '', 'long long': '    return 0;\n', double: '    return 0.0;\n', bool: '    return false;\n' }[r.type] ?? (r.extra.length ? '    *returnSize = 0;\n    return NULL;\n' : '    return NULL;\n');
  return `#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n#include <stdbool.h>\n\n${head}${head ? '\n' : ''}${cSig(p)} {\n${note}${ret}}\n`;
}

const C_PRELUDE = String.raw`#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>
#include <limits.h>
#include <stdint.h>
#include <ctype.h>
struct ListNode { long long val; struct ListNode* next; };
struct TreeNode { long long val; struct TreeNode* left; struct TreeNode* right; };
typedef struct ListNode ListNode;
typedef struct TreeNode TreeNode;
`;

const C_EPILOGUE_HELPERS = String.raw`
static char* cr_dup(const char* s) { size_t n = strlen(s); char* d = (char*)malloc(n + 1); memcpy(d, s, n + 1); return d; }
static void cr_p_int(long long v) { printf("%lld", v); }
static void cr_p_float(double v) { if (isnan(v) || isinf(v)) printf("null"); else printf("%.17g", v); }
static void cr_p_bool(bool v) { printf(v ? "true" : "false"); }
static void cr_p_str(const char* s) {
  if (!s) { printf("null"); return; }
  putchar('"');
  for (const unsigned char* c = (const unsigned char*)s; *c; c++) {
    if (*c == '"') printf("\\\""); else if (*c == '\\') printf("\\\\");
    else if (*c < 0x20) printf("\\u%04x", *c); else putchar(*c);
  }
  putchar('"');
}
static struct ListNode* cr_mk_list(const long long* v, int n) {
  struct ListNode* head = NULL;
  for (int i = n - 1; i >= 0; i--) { struct ListNode* x = (struct ListNode*)malloc(sizeof *x); x->val = v[i]; x->next = head; head = x; }
  return head;
}
static void cr_p_list(struct ListNode* h) {
  printf("["); int k = 0;
  while (h && k < 100000) { if (k++) printf(","); printf("%lld", h->val); h = h->next; }
  printf("]");
}
static struct TreeNode* cr_new_tree(long long v) { struct TreeNode* t = (struct TreeNode*)malloc(sizeof *t); t->val = v; t->left = t->right = NULL; return t; }
static struct TreeNode* cr_mk_tree(const long long* v, const bool* present, int n) {
  if (n == 0 || !present[0]) return NULL;
  struct TreeNode** q = (struct TreeNode**)malloc(sizeof(struct TreeNode*) * (size_t)n);
  int qh = 0, qt = 0, i = 1;
  struct TreeNode* root = cr_new_tree(v[0]); q[qt++] = root;
  while (i < n && qh < qt) {
    struct TreeNode* node = q[qh++];
    if (i < n && present[i]) { node->left = cr_new_tree(v[i]); q[qt++] = node->left; } i++;
    if (i < n && present[i]) { node->right = cr_new_tree(v[i]); q[qt++] = node->right; } i++;
  }
  free(q); return root;
}
static void cr_p_tree(struct TreeNode* r) {
  int cap = 1024, qh = 0, qt = 0, last = -1, k = 0;
  struct TreeNode** q = (struct TreeNode**)malloc(sizeof(struct TreeNode*) * (size_t)cap);
  q[qt++] = r;
  while (qh < qt && qt < 200000) {
    struct TreeNode* n = q[qh++];
    if (n) { last = qh - 1; if (qt + 2 > cap) { cap *= 2; q = (struct TreeNode**)realloc(q, sizeof(struct TreeNode*) * (size_t)cap); } q[qt++] = n->left; q[qt++] = n->right; }
  }
  printf("[");
  for (int i = 0; i <= last; i++) { if (k++) printf(","); if (q[i]) printf("%lld", q[i]->val); else printf("null"); }
  printf("]"); free(q);
}
`;

// Build C declarations + argument expressions for one value.
function cArg(v, t, name, asm = false) {
  const { base, dims } = parseType(t);
  const decls = [];
  const lit = (x) => base === 'int' ? inum(x) + 'LL' : base === 'float' ? fnum(x) : base === 'bool' ? (x ? 'true' : 'false') : `cr_dup(${cStr(x)})`;
  const elt = C_BASE[base];
  if (base === 'list') {
    if (v.length === 0) return { decls, args: ['NULL'] };
    decls.push(`long long ${name}_v[] = {${v.map((x) => inum(x) + 'LL').join(', ')}};`);
    return { decls, args: [`cr_mk_list(${name}_v, ${v.length})`] };
  }
  if (base === 'tree') {
    if (v.length === 0) return { decls, args: ['NULL'] };
    decls.push(`long long ${name}_v[] = {${v.map((x) => (x === null ? '0' : inum(x) + 'LL')).join(', ')}};`);
    decls.push(`bool ${name}_m[] = {${v.map((x) => (x === null ? 'false' : 'true')).join(', ')}};`);
    return { decls, args: [`cr_mk_tree(${name}_v, ${name}_m, ${v.length})`] };
  }
  if (dims === 0) return { decls, args: [lit(v)] };
  const arr = (vals, nm) => {
    if (vals.length === 0) decls.push(`${elt} ${nm}[1];`);
    else decls.push(`${elt} ${nm}[] = {${vals.map(lit).join(', ')}};`);
  };
  if (dims === 1) {
    arr(v, name);
    return { decls, args: [name, String(v.length)] };
  }
  v.forEach((row, i) => arr(row, `${name}_r${i}`));
  const sz = asm ? 'long long' : 'int';
  if (v.length === 0) decls.push(`${elt}* ${name}[1]; ${sz} ${name}_c[1];`);
  else {
    decls.push(`${elt}* ${name}[] = {${v.map((_, i) => `${name}_r${i}`).join(', ')}};`);
    decls.push(`${sz} ${name}_c[] = {${v.map((r) => r.length).join(', ')}};`);
  }
  return { decls, args: [name, String(v.length), `${name}_c`] };
}

// C statements printing expression `e` (with sizes) as JSON.
function cPrint(t, e, size, colSizes) {
  const { base, dims } = parseType(t);
  if (base === 'list') return `cr_p_list(${e});`;
  if (base === 'tree') return `cr_p_tree(${e});`;
  const pf = `cr_p_${base}`;
  if (dims === 0) return `${pf}(${e});`;
  if (dims === 1) return `printf("["); for (long long cr_i = 0; cr_i < (long long)(${size}); cr_i++) { if (cr_i) printf(","); ${pf}((${e})[cr_i]); } printf("]");`;
  return `printf("["); for (long long cr_i = 0; cr_i < (long long)(${size}); cr_i++) { if (cr_i) printf(","); printf("["); for (long long cr_j = 0; cr_j < (long long)((${colSizes})[cr_i]); cr_j++) { if (cr_j) printf(","); ${pf}((${e})[cr_i][cr_j]); } printf("]"); } printf("]");`;
}

function cHarness(p, code, tests, { asm = false } = {}) {
  const mi = mutIndex(p);
  const r = asm ? { type: p.returns === 'void' ? 'void' : 'long long', extra: [] } : cReturn(p);
  const parts = [];
  if (asm) parts.push(C_PRELUDE, `extern ${r.type} ${p.fn}(${cParams(p, true).join(', ')});\n`);
  else parts.push(C_PRELUDE, '#line 1 "solution.c"\n', code, '\n#line 1 "harness.c"\n');
  parts.push(C_EPILOGUE_HELPERS);
  parts.push('int main(void) {\n  setvbuf(stdout, NULL, _IOFBF, 1 << 16);\n');
  tests.forEach((t, i) => {
    const decls = [];
    const args = [];
    const argInfo = [];
    p.params.forEach(([n, ty], j) => {
      const a = cArg(t.args[j], ty, `a${j}`, asm);
      decls.push(...a.decls);
      args.push(...a.args);
      argInfo.push(a.args);
    });
    let call;
    let print;
    if (mi >= 0) {
      call = `${p.fn}(${args.join(', ')});`;
      const [mt] = [p.params[mi][1]];
      const ai = argInfo[mi];
      print = cPrint(mt, ai[0], ai[1], ai[2]);
      if (parseType(mt).base === 'list' || parseType(mt).base === 'tree') throw new Error('mutating list/tree params is not supported; return the node instead');
    } else if (r.extra.length === 0) {
      call = `${r.type} cr_r = ${p.fn}(${args.join(', ')});`;
      print = cPrint(p.returns, 'cr_r');
    } else if (r.extra.length === 1) {
      call = `int cr_rs = 0; ${r.type} cr_r = ${p.fn}(${[...args, '&cr_rs'].join(', ')});`;
      print = cPrint(p.returns, 'cr_r', 'cr_rs');
    } else {
      call = `int cr_rs = 0; int* cr_rc = NULL; ${r.type} cr_r = ${p.fn}(${[...args, '&cr_rs', '&cr_rc'].join(', ')});`;
      print = cPrint(p.returns, 'cr_r', 'cr_rs', 'cr_rc');
    }
    parts.push(`  { /* test ${i} */\n    ${decls.join('\n    ')}\n    ${call}\n    fflush(stdout); printf("\\036R ${i} "); ${print} printf("\\n"); fflush(stdout);\n  }\n`);
  });
  parts.push('  return 0;\n}\n');
  return parts.join('');
}

// ---------------------------------------------------------------- C++

const CPP_BASE = { int: 'long long', float: 'double', bool: 'bool', str: 'string' };
function cppType(t) {
  const { base, dims } = parseType(t);
  if (base === 'list') return 'ListNode*';
  if (base === 'tree') return 'TreeNode*';
  if (base === 'void') return 'void';
  let s = CPP_BASE[base];
  for (let i = 0; i < dims; i++) s = `vector<${s}>`;
  return s;
}
function cppParam(n, t, mut) {
  const { base, dims } = parseType(t);
  const ty = cppType(t);
  if (dims > 0 || (base === 'str' && mut)) return `${ty}& ${n}`;
  return `${ty} ${n}`;
}
function cppSig(p) {
  return `${cppType(p.returns)} ${camel(p.fn)}(${p.params.map(([n, t]) => cppParam(pName(n, 'cpp'), t, n === p.mutates)).join(', ')})`;
}

const CPP_LIST_DOC = `// Provided for you:
// struct ListNode {
//     long long val; ListNode* next;
//     ListNode(long long x = 0, ListNode* n = nullptr) : val(x), next(n) {}
// };
`;
const CPP_TREE_DOC = `// Provided for you:
// struct TreeNode {
//     long long val; TreeNode* left; TreeNode* right;
//     TreeNode(long long x = 0, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(x), left(l), right(r) {}
// };
`;

function cppStarter(p) {
  if (p.kind === 'io') {
    return `#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    // Your code here: read with cin, print with cout.\n    return 0;\n}\n`;
  }
  let head = '';
  if (usesType(p, 'list')) head += CPP_LIST_DOC;
  if (usesType(p, 'tree')) head += CPP_TREE_DOC;
  const ret = p.returns === 'void' ? '' : `    return {};\n`;
  const note = p.mutates ? `    // Modify \`${camel(p.mutates)}\` in place.\n` : '    // Your code here\n';
  return `#include <bits/stdc++.h>\nusing namespace std;\n\n${head}${head ? '\n' : ''}${cppSig(p)} {\n${note}${ret}}\n`;
}

// <bits/stdc++.h> does not exist on macOS clang, so we provide it via -include.
export const CPP_BITS = String.raw`#pragma once
#include <algorithm>
#include <array>
#include <bitset>
#include <cassert>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <deque>
#include <functional>
#include <iomanip>
#include <iostream>
#include <iterator>
#include <list>
#include <map>
#include <memory>
#include <numeric>
#include <optional>
#include <queue>
#include <set>
#include <sstream>
#include <stack>
#include <stdexcept>
#include <string>
#include <string_view>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
`;

const CPP_PRELUDE = String.raw`#include <bits/stdc++.h>
using namespace std;
struct ListNode { long long val; ListNode* next; ListNode(long long x = 0, ListNode* n = nullptr) : val(x), next(n) {} };
struct TreeNode { long long val; TreeNode* left; TreeNode* right; TreeNode(long long x = 0, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(x), left(l), right(r) {} };
`;

const CPP_HELPERS = String.raw`
namespace cr {
static void p(long long v) { printf("%lld", v); }
static void p(int v) { printf("%d", v); }
static void p(double v) { if (std::isnan(v) || std::isinf(v)) printf("null"); else printf("%.17g", v); }
static void p(bool v) { printf(v ? "true" : "false"); }
static void p(const string& s) {
  putchar('"');
  for (unsigned char c : s) { if (c == '"') printf("\\\""); else if (c == '\\') printf("\\\\"); else if (c < 0x20) printf("\\u%04x", c); else putchar(c); }
  putchar('"');
}
static void p(ListNode* h) { printf("["); int k = 0; while (h && k < 100000) { if (k++) printf(","); printf("%lld", h->val); h = h->next; } printf("]"); }
static void p(TreeNode* r) {
  vector<TreeNode*> q{r}; size_t qh = 0; long long last = -1;
  while (qh < q.size() && q.size() < 200000) { TreeNode* n = q[qh++]; if (n) { last = (long long)qh - 1; q.push_back(n->left); q.push_back(n->right); } }
  printf("["); for (long long i = 0; i <= last; i++) { if (i) printf(","); if (q[i]) printf("%lld", q[i]->val); else printf("null"); } printf("]");
}
template <class T> static void p(const vector<T>& v) { printf("["); bool first = true; for (auto&& x : v) { if (!first) printf(","); first = false; p(static_cast<T>(x)); } printf("]"); }
static ListNode* mkList(const vector<long long>& v) { ListNode* h = nullptr; for (size_t i = v.size(); i-- > 0;) h = new ListNode(v[i], h); return h; }
static TreeNode* mkTree(const vector<long long>& v, const vector<bool>& m) {
  if (v.empty() || !m[0]) return nullptr;
  TreeNode* root = new TreeNode(v[0]); vector<TreeNode*> q{root}; size_t qh = 0, i = 1;
  while (i < v.size() && qh < q.size()) {
    TreeNode* n = q[qh++];
    if (i < v.size() && m[i]) { n->left = new TreeNode(v[i]); q.push_back(n->left); } i++;
    if (i < v.size() && m[i]) { n->right = new TreeNode(v[i]); q.push_back(n->right); } i++;
  }
  return root;
}
}
`;

function cppLit(v, t) {
  const { base, dims } = parseType(t);
  if (base === 'list') return `cr::mkList({${v.map(inum).join(',')}})`;
  if (base === 'tree') return `cr::mkTree({${v.map((x) => (x === null ? '0' : inum(x))).join(',')}}, {${v.map((x) => (x === null ? 'false' : 'true')).join(',')}})`;
  const sc = (x) => base === 'int' ? inum(x) + 'LL' : base === 'float' ? fnum(x) : base === 'bool' ? String(!!x) : `std::string(${cStr(x)}, ${new TextEncoder().encode(x).length})`;
  if (dims === 0) return sc(v);
  if (dims === 1) return `${cppType(t)}{${v.map(sc).join(', ')}}`;
  return `${cppType(t)}{${v.map((row) => `${cppType(base + '[]')}{${row.map(sc).join(', ')}}`).join(', ')}}`;
}

function cppHarness(p, code, tests) {
  const mi = mutIndex(p);
  const parts = [CPP_PRELUDE, '#line 1 "solution.cpp"\n', code, '\n#line 1 "harness.cpp"\n', CPP_HELPERS];
  parts.push('int main() {\n  setvbuf(stdout, nullptr, _IOFBF, 1 << 16);\n');
  tests.forEach((t, i) => {
    const decls = p.params.map(([, ty], j) => `auto a${j} = ${cppLit(t.args[j], ty)};`);
    const args = p.params.map((_, j) => `a${j}`).join(', ');
    let body;
    if (mi >= 0) body = `${camel(p.fn)}(${args}); fflush(stdout); printf("\\036R ${i} "); cr::p(a${mi});`;
    else body = `auto cr_r = ${camel(p.fn)}(${args}); fflush(stdout); printf("\\036R ${i} "); cr::p(cr_r);`;
    parts.push(`  { /* test ${i} */\n    try {\n      ${decls.join('\n      ')}\n      ${body}\n      printf("\\n");\n    } catch (const std::exception& e) {\n      fflush(stdout); printf("\\036E ${i} "); cr::p(std::string("uncaught exception: ") + e.what()); printf("\\n");\n    }\n    fflush(stdout);\n  }\n`);
  });
  parts.push('  return 0;\n}\n');
  return parts.join('');
}

// ---------------------------------------------------------------- Rust

const RS_BASE = { int: 'i64', float: 'f64', bool: 'bool', str: 'String' };
function rsType(t) {
  const { base, dims } = parseType(t);
  if (base === 'list') return 'Option<Box<ListNode>>';
  if (base === 'tree') return 'Option<Rc<RefCell<TreeNode>>>';
  if (base === 'void') return '()';
  let s = RS_BASE[base];
  for (let i = 0; i < dims; i++) s = `Vec<${s}>`;
  return s;
}
function rsSig(p) {
  const params = p.params.map(([n, t]) => `${n}: ${n === p.mutates ? '&mut ' : ''}${rsType(t)}`).join(', ');
  return `pub fn ${p.fn}(${params})${p.returns === 'void' ? '' : ` -> ${rsType(p.returns)}`}`;
}

const RS_LIST_DOC = `// Provided for you:
// pub struct ListNode { pub val: i64, pub next: Option<Box<ListNode>> }
// impl ListNode { pub fn new(val: i64) -> Self }
`;
const RS_TREE_DOC = `use std::cell::RefCell;
use std::rc::Rc;

// Provided for you:
// pub struct TreeNode { pub val: i64, pub left: Option<Rc<RefCell<TreeNode>>>, pub right: Option<Rc<RefCell<TreeNode>>> }
// impl TreeNode { pub fn new(val: i64) -> Self }
`;

function rustStarter(p) {
  if (p.kind === 'io') {
    return `use std::io::{self, Read};\n\nfn main() {\n    let mut input = String::new();\n    io::stdin().read_to_string(&mut input).unwrap();\n    // Your code here: parse \`input\`, print with println!.\n}\n`;
  }
  let head = '';
  if (usesType(p, 'tree')) head += RS_TREE_DOC;
  if (usesType(p, 'list')) head += RS_LIST_DOC;
  const unused = p.params.map(([n]) => n).filter((n) => n !== p.mutates);
  const body = p.returns === 'void'
    ? `    // Modify \`${p.mutates}\` in place.\n    let _ = ${p.mutates};\n`
    : `    // Your code here\n    ${unused.length ? `let _ = (${unused.map((n) => `&${n}`).join(', ')});\n    ` : ''}Default::default()\n`;
  return `${head}${head ? '\n' : ''}${rsSig(p)} {\n${body}}\n`;
}

const RS_HELPERS = String.raw`
#[allow(dead_code)]
#[derive(PartialEq, Eq, Clone, Debug)]
pub struct ListNode { pub val: i64, pub next: Option<Box<ListNode>> }
#[allow(dead_code)]
impl ListNode { #[inline] pub fn new(val: i64) -> Self { ListNode { next: None, val } } }
#[allow(dead_code)]
#[derive(Debug, PartialEq, Eq)]
pub struct TreeNode { pub val: i64, pub left: Option<std::rc::Rc<std::cell::RefCell<TreeNode>>>, pub right: Option<std::rc::Rc<std::cell::RefCell<TreeNode>>> }
#[allow(dead_code)]
impl TreeNode { #[inline] pub fn new(val: i64) -> Self { TreeNode { val, left: None, right: None } } }

#[allow(dead_code, unused_imports)]
mod cr_harness {
    use std::rc::Rc;
    use std::cell::RefCell;
    use std::io::Write;
    pub trait J { fn j(&self) -> String; }
    impl J for i64 { fn j(&self) -> String { self.to_string() } }
    impl J for i32 { fn j(&self) -> String { self.to_string() } }
    impl J for usize { fn j(&self) -> String { self.to_string() } }
    impl J for f64 { fn j(&self) -> String { if self.is_finite() { format!("{:?}", self) } else { "null".into() } } }
    impl J for bool { fn j(&self) -> String { self.to_string() } }
    impl J for String {
        fn j(&self) -> String {
            let mut s = String::from("\"");
            for c in self.chars() {
                match c { '"' => s.push_str("\\\""), '\\' => s.push_str("\\\\"), c if (c as u32) < 0x20 => s.push_str(&format!("\\u{:04x}", c as u32)), c => s.push(c) }
            }
            s.push('"'); s
        }
    }
    impl<T: J> J for Vec<T> { fn j(&self) -> String { format!("[{}]", self.iter().map(|x| x.j()).collect::<Vec<_>>().join(",")) } }
    impl J for Option<Box<super::ListNode>> {
        fn j(&self) -> String {
            let mut v = Vec::new(); let mut cur = self.as_ref();
            while let Some(n) = cur { if v.len() >= 100000 { break; } v.push(n.val.to_string()); cur = n.next.as_ref(); }
            format!("[{}]", v.join(","))
        }
    }
    impl J for Option<Rc<RefCell<super::TreeNode>>> {
        fn j(&self) -> String {
            let mut out: Vec<Option<i64>> = Vec::new();
            let mut q = std::collections::VecDeque::new(); q.push_back(self.clone());
            while let Some(n) = q.pop_front() {
                if out.len() >= 200000 { break; }
                match n { Some(rc) => { let b = rc.borrow(); out.push(Some(b.val)); q.push_back(b.left.clone()); q.push_back(b.right.clone()); } None => out.push(None) }
            }
            while let Some(None) = out.last() { out.pop(); }
            format!("[{}]", out.iter().map(|x| match x { Some(v) => v.to_string(), None => "null".into() }).collect::<Vec<_>>().join(","))
        }
    }
    pub fn mk_list(v: Vec<i64>) -> Option<Box<super::ListNode>> {
        let mut head = None;
        for &x in v.iter().rev() { head = Some(Box::new(super::ListNode { val: x, next: head })); }
        head
    }
    pub fn mk_tree(v: Vec<Option<i64>>) -> Option<Rc<RefCell<super::TreeNode>>> {
        if v.is_empty() || v[0].is_none() { return None; }
        let root = Rc::new(RefCell::new(super::TreeNode::new(v[0].unwrap())));
        let mut q = std::collections::VecDeque::new(); q.push_back(root.clone()); let mut i = 1;
        while i < v.len() {
            let n = match q.pop_front() { Some(n) => n, None => break };
            if let Some(x) = v[i] { let c = Rc::new(RefCell::new(super::TreeNode::new(x))); n.borrow_mut().left = Some(c.clone()); q.push_back(c); } i += 1;
            if i < v.len() { if let Some(x) = v[i] { let c = Rc::new(RefCell::new(super::TreeNode::new(x))); n.borrow_mut().right = Some(c.clone()); q.push_back(c); } } i += 1;
        }
        Some(root)
    }
    pub fn emit(i: usize, r: std::thread::Result<String>) {
        let out = std::io::stdout(); let mut o = out.lock(); let _ = o.flush();
        match r {
            Ok(s) => { let _ = writeln!(o, "\x1eR {} {}", i, s); }
            Err(e) => {
                let msg = if let Some(s) = e.downcast_ref::<&str>() { s.to_string() } else if let Some(s) = e.downcast_ref::<String>() { s.clone() } else { "panic".to_string() };
                let _ = writeln!(o, "\x1eE {} {}", i, format!("panicked: {}", msg).j());
            }
        }
        let _ = o.flush();
    }
`;

function rsLit(v, t) {
  const { base, dims } = parseType(t);
  if (base === 'list') return `mk_list(vec![${v.map((x) => inum(x) + 'i64').join(', ')}])`;
  if (base === 'tree') return `mk_tree(vec![${v.map((x) => (x === null ? 'None' : `Some(${inum(x)}i64)`)).join(', ')}])`;
  const sc = (x) => base === 'int' ? inum(x) + 'i64' : base === 'float' ? fnum(x) + '_f64' : base === 'bool' ? String(!!x) : `String::from(${rustStr(x)})`;
  if (dims === 0) return sc(v);
  if (dims === 1) return `{ let v: ${rsType(t)} = vec![${v.map(sc).join(', ')}]; v }`;
  return `{ let v: ${rsType(t)} = vec![${v.map((row) => `vec![${row.map(sc).join(', ')}]`).join(', ')}]; v }`;
}

function rustHarness(p, code, tests) {
  const mi = mutIndex(p);
  const lines = [];
  tests.forEach((t, i) => {
    const decls = p.params.map(([, ty], j) => `let ${j === mi ? 'mut ' : ''}a${j} = ${rsLit(t.args[j], ty)};`);
    const args = p.params.map((_, j) => (j === mi ? `&mut a${j}` : `a${j}`)).join(', ');
    const ret = mi >= 0 ? `super::${p.fn}(${args}); a${mi}.j()` : `super::${p.fn}(${args}).j()`;
    lines.push(`        emit(${i}, std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| { ${decls.join(' ')} ${ret} })));`);
  });
  return `${code}\n${RS_HELPERS}    pub fn run() {\n${lines.join('\n')}\n    }\n}\n\nfn main() {\n    std::panic::set_hook(Box::new(|info| { eprintln!("{}", info); }));\n    cr_harness::run();\n}\n`;
}

// ---------------------------------------------------------------- ESPresso

function espStarter(p) {
  if (p.kind === 'io') return `// ESPresso program: use print(...) to produce output.\n\n`;
  const args = p.params.map(([n]) => pName(n, 'espresso')).join(', ');
  const ret = p.returns === 'void' ? '' : `    return ${p.returns === 'bool' ? 'false' : '0'}\n`;
  const note = p.mutates ? `    // Modify \`${camel(p.mutates)}\` in place (arrays are passed by reference).\n` : '    // Your code here\n';
  return `fn ${camel(p.fn)}(${args}) {\n${note}${ret}}\n`;
}

function espLit(v, t) {
  const { base } = parseType(t);
  if (Array.isArray(v)) return `[${v.map((x) => espLit(x, base === 'float' ? 'float' : 'int')).join(', ')}]`;
  if (typeof v === 'boolean') return String(v);
  if (base === 'float') return fnum(v);
  return inum(v);
}

function espHarness(p, code, tests) {
  const mi = mutIndex(p);
  const lines = tests.map((t, i) => {
    const args = p.params.map(([, ty], j) => espLit(t.args[j], ty));
    if (mi >= 0) {
      return `var crArg${i} = ${args[mi]}\n${camel(p.fn)}(${args.map((a, j) => (j === mi ? `crArg${i}` : a)).join(', ')})\nprint("${ESP_MARK}", ${i}, crArg${i})`;
    }
    return `print("${ESP_MARK}", ${i}, ${camel(p.fn)}(${args.join(', ')}))`;
  });
  return `${code}\n\n${lines.join('\n')}\n`;
}

// ---------------------------------------------------------------- public API

export function starterCode(problem, lang) {
  if (problem.starters && problem.starters[lang]) return problem.starters[lang];
  switch (lang) {
    case 'python': return pythonStarter(problem);
    case 'c': return cStarter(problem);
    case 'cpp': return cppStarter(problem);
    case 'rust': return rustStarter(problem);
    case 'espresso': return espStarter(problem);
    case 'asm': return problem.asm_starter || '';
    default: throw new Error(`Unknown language ${lang}`);
  }
}

/** Signature line for display in the problem statement. */
export function signature(problem, lang) {
  if (problem.kind === 'io') return null;
  switch (lang) {
    case 'python': return `def ${problem.fn}(${problem.params.map(([n, t]) => `${n}: ${pyType(t)}`).join(', ')}) -> ${pyType(problem.returns)}`;
    case 'c': return cSig(problem);
    case 'cpp': return cppSig(problem);
    case 'rust': return rsSig(problem);
    case 'espresso': return `fn ${camel(problem.fn)}(${problem.params.map(([n]) => camel(n)).join(', ')})`;
    case 'asm': return `long long ${problem.fn}(${cParams(problem, true).join(', ')})  // C view of your _${problem.fn}`;
    default: return null;
  }
}

/**
 * Build the request for the runner.
 * Returns { lang, files: {name: content}, main, stdins: [..], mode: 'function'|'io' }
 *   - For function problems a single run (stdin "") prints one marker line per test.
 *   - For io problems each test is its own run with its own stdin.
 */
export function buildRun(problem, lang, code, tests) {
  if (problem.kind === 'io') {
    const stdins = tests.map((t) => t.stdin ?? '');
    if (lang === 'python') return { lang, mode: 'io', source: pythonIoHarness(code), stdins };
    if (lang === 'cpp') return { lang, mode: 'io', source: code, stdins, headers: { 'bits/stdc++.h': CPP_BITS } };
    return { lang, mode: 'io', source: code, stdins };
  }
  let source;
  const extra = {};
  switch (lang) {
    case 'python': source = pythonFunctionHarness(problem, code, tests); break;
    case 'c': source = cHarness(problem, code, tests); break;
    case 'cpp': source = cppHarness(problem, code, tests); extra.headers = { 'bits/stdc++.h': CPP_BITS }; break;
    case 'rust': source = rustHarness(problem, code, tests); break;
    case 'espresso': source = espHarness(problem, code, tests); break;
    case 'asm': source = cHarness(problem, '', tests, { asm: true }); extra.asm = code; break;
    default: throw new Error(`Unknown language ${lang}`);
  }
  return { lang, mode: 'function', source, stdins: [''], ...extra };
}

/**
 * Interpret runner output.
 * run: { compile?: {ok, output}, runs: [{stdout, stderr, exitCode, timedOut, timeMs}] }
 * Returns { compileError?, results: [{index, status, got, expected, stdout, error}], stderr }
 */
/** Strip harness frames (main.py, temp paths) from Python tracebacks. */
export function cleanPyTrace(text) {
  if (!text) return text;
  const out = [];
  const lines = text.split('\n');
  for (let i = 0; i < lines.length; i++) {
    const l = lines[i];
    if (/^\s*File ".*main\.py", line \d+/.test(l) || /^\s*File "<(exec|string)>"/.test(l)) {
      while (i + 1 < lines.length && /^\s{4,}/.test(lines[i + 1])) i++;
      continue;
    }
    out.push(l);
  }
  return out.join('\n');
}

export function parseRun(problem, lang, tests, run) {
  if (lang === 'python' && run.runs) run.runs.forEach((r) => { r.stderr = cleanPyTrace(r.stderr); });
  if (run.compile && !run.compile.ok) return { compileError: run.compile.output || 'Compilation failed', results: [], stderr: '' };
  const results = [];
  if (problem.kind === 'io') {
    tests.forEach((t, i) => {
      const r = run.runs[i] || {};
      const got = normalizeIo(r.stdout || '');
      const expected = normalizeIo(t.expected);
      let status = got === expected ? 'pass' : 'fail';
      let error = null;
      if (r.timedOut) { status = 'timeout'; error = 'Time limit exceeded'; }
      else if (r.exitCode && status !== 'pass') { status = 'error'; error = `Exited with code ${r.exitCode}`; }
      results.push({ index: i, status, got: r.stdout || '', expected: t.expected, stdout: '', stderr: r.stderr || '', error, timeMs: r.timeMs });
    });
    return { results, stderr: '' };
  }
  const r = run.runs[0] || { stdout: '', stderr: '' };
  const out = r.stdout || '';
  const byIndex = new Map();
  const userOut = new Map();
  let last = 0;
  let pending = '';
  if (lang === 'espresso') {
    const re = new RegExp(`^${ESP_MARK} (\\d+) (.*)$`, 'gm');
    let m;
    while ((m = re.exec(out))) {
      const idx = Number(m[1]);
      pending += out.slice(last, m.index);
      userOut.set(idx, pending.replace(/\n$/, ''));
      pending = '';
      last = re.lastIndex + 1;
      byIndex.set(idx, { kind: 'R', text: m[2] });
    }
  } else {
    const re = /\x1e([RE]) (\d+) ([^\n]*)\n?/g;
    let m;
    while ((m = re.exec(out))) {
      const idx = Number(m[2]);
      pending += out.slice(last, m.index);
      userOut.set(idx, pending.replace(/\n$/, ''));
      pending = '';
      last = re.lastIndex;
      byIndex.set(idx, { kind: m[1], text: m[3] });
    }
  }
  const trailing = out.slice(last);
  let firstMissing = true;
  tests.forEach((t, i) => {
    const rec = byIndex.get(i);
    const res = { index: i, expected: t.expected, stdout: userOut.get(i) || '', timeMs: r.timeMs };
    if (!rec) {
      res.status = r.timedOut ? 'timeout' : 'error';
      res.error = firstMissing
        ? (r.timedOut ? 'Time limit exceeded (your code ran too long; look for infinite loops or a slow algorithm)' : `Program crashed${r.exitCode ? ` (exit code ${r.exitCode})` : ''} before finishing this test. See stderr below.`)
        : 'Not run (an earlier test crashed or timed out)';
      if (firstMissing) res.stdout = (res.stdout + trailing).trim();
      firstMissing = false;
    } else if (rec.kind === 'E') {
      res.status = 'error';
      try { res.error = JSON.parse(rec.text); } catch { res.error = rec.text; }
    } else {
      let got;
      try { got = lang === 'espresso' ? parseEspValue(rec.text) : JSON.parse(rec.text); } catch { got = rec.text; }
      res.got = got;
      res.status = valuesEqual(got, t.expected, problem.compare || 'exact', problem.returns) ? 'pass' : 'fail';
    }
    results.push(res);
  });
  return { results, stderr: r.stderr || '' };
}

function parseEspValue(text) {
  const s = text.trim();
  if (s === 'null') return null;
  try { return JSON.parse(s); } catch { return s; }
}

export function normalizeIo(s) {
  return String(s).replace(/\r\n/g, '\n').split('\n').map((l) => l.replace(/[ \t]+$/, '')).join('\n').replace(/\n+$/, '');
}

const EPS = 1e-6;
function eqFloat(a, b) {
  if (typeof a !== 'number' || typeof b !== 'number') return false;
  if (Number.isInteger(a) && Number.isInteger(b)) return a === b;
  return Math.abs(a - b) <= EPS * Math.max(1, Math.abs(a), Math.abs(b));
}
function deepEq(a, b) {
  if (typeof a === 'number' || typeof b === 'number') return eqFloat(a, b);
  if (Array.isArray(a) && Array.isArray(b)) return a.length === b.length && a.every((x, i) => deepEq(x, b[i]));
  return a === b;
}
const key = (x) => JSON.stringify(x);
function sortDeep(v, depth) {
  if (!Array.isArray(v)) return v;
  const inner = depth > 1 ? v.map((x) => sortDeep(x, depth - 1)) : v.slice();
  return inner.slice().sort((x, y) => (key(x) < key(y) ? -1 : key(x) > key(y) ? 1 : 0));
}

/** compare modes: exact | unordered (top-level order ignored) | unordered_deep (order ignored at every level) */
export function valuesEqual(got, expected, mode = 'exact') {
  if (mode === 'unordered') return deepEq(sortDeep(got, 1), sortDeep(expected, 1));
  if (mode === 'unordered_deep') return deepEq(sortDeep(got, 3), sortDeep(expected, 3));
  return deepEq(got, expected);
}

export function formatValue(v) {
  if (v === undefined) return '';
  if (typeof v === 'string') return JSON.stringify(v);
  return JSON.stringify(v);
}
