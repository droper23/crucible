// IDE features for the Monaco editor: hover docs, completions, signature help,
// outline / go-to-definition for your own functions, and compiler diagnostics as squiggles.
// Reference data lives in ./langdocs/<lang>.js (schema: langdocs/SCHEMA.md).
import { signature } from './harness.js';

const LANG_OF = { python: 'python', c: 'c', cpp: 'cpp', rust: 'rust', espresso: 'espresso', arm64: 'arm64', x86: 'x86' };
const ASM = new Set(['arm64', 'x86']);
const docs = {};          // lang -> { all, byName: Map<name, entry[]> }
const loading = {};
let ctx = { problem: null, lang: null };   // current problem + Crucible language id
let installed = false;

/** Tell the providers which problem / language the editor is showing. */
export function setIdeContext(problem, lang) { ctx = { problem, lang }; }

async function loadDocs(lang) {
  if (docs[lang]) return docs[lang];
  loading[lang] ??= import(`./langdocs/${lang}.js`).then((m) => {
    const all = m.default || [];
    const byName = new Map();
    for (const e of all) {
      e._owner = normOwner(e.owner);
      if (!byName.has(e.name)) byName.set(e.name, []);
      byName.get(e.name).push(e);
    }
    return (docs[lang] = { all, byName });
  }).catch(() => (docs[lang] = { all: [], byName: new Map() }));
  return loading[lang];
}

const normOwner = (o) => (o ? o.replace(/^std::/, '').replace(/<.*$/, '').replace(/^&/, '').toLowerCase() : '');

// Owners whose members are reachable without a qualifier.
const GLOBAL_OWNERS = { python: [''], c: [''], cpp: ['', 'std'], rust: ['', 'prelude'], espresso: [''], arm64: [''], x86: [''] };
// Receiver type -> owners whose methods apply (Rust auto-deref etc.).
const ALIASES = {
  rust: { vec: ['vec', 'slice'], string: ['string', 'str'], str: ['str'], vecdeque: ['vecdeque'], iterator: ['iterator'], i64: ['i64'], i32: ['i64'], usize: ['i64', 'usize'], u64: ['i64'], char: ['char'] },
  python: { counter: ['counter', 'dict'], defaultdict: ['dict'], ordereddict: ['dict'] },
};
const ownersFor = (lang, t) => ALIASES[lang]?.[t] || [t];

// ---------------------------------------------------------------- user symbols
const DEF_RX = {
  python: [[/^[ \t]*def\s+(\w+)\s*\(([^)]*)\)/gm, 'function'], [/^[ \t]*class\s+(\w+)/gm, 'class']],
  c: [[/^[ \t]*(?:static\s+|inline\s+|const\s+|unsigned\s+|struct\s+)*[A-Za-z_][\w]*[\s*]+\**(\w+)\s*\(([^;{}()]*)\)\s*\{/gm, 'function'], [/^[ \t]*(?:typedef\s+)?struct\s+(\w+)\s*\{/gm, 'struct']],
  cpp: [[/^[ \t]*(?:static\s+|inline\s+|const\s+|virtual\s+|template\s*<[^>]*>\s*)*[A-Za-z_][\w:<>,]*[\s*&]+[*&]*(\w+)\s*\(([^;{}()]*)\)\s*(?:const\s*)?\{/gm, 'function'], [/^[ \t]*(?:struct|class)\s+(\w+)/gm, 'struct']],
  rust: [[/^[ \t]*(?:pub\s+)?fn\s+(\w+)(?:<[^>]*>)?\s*\(([^)]*)\)/gm, 'function'], [/^[ \t]*(?:pub\s+)?(?:struct|enum|trait)\s+(\w+)/gm, 'struct']],
  espresso: [[/^[ \t]*fn\s+(\w+)\s*\(([^)]*)\)/gm, 'function']],
  arm64: [[/^[ \t]*([A-Za-z_.$][\w.$]*):/gm, 'label']],
  x86: [[/^[ \t]*([A-Za-z_.$][\w.$]*):/gm, 'label']],
};
const NOT_FN = new Set(['if', 'for', 'while', 'switch', 'return', 'else', 'sizeof', 'catch']);

function userSymbols(model, lang) {
  const text = model.getValue();
  const out = [];
  for (const [rx, kind] of DEF_RX[lang] || []) {
    rx.lastIndex = 0;
    let m;
    while ((m = rx.exec(text))) {
      if (NOT_FN.has(m[1])) continue;
      const nameIdx = m.index + m[0].indexOf(m[1], m[0].search(/\S/));
      const pos = model.getPositionAt(nameIdx);
      const lineText = model.getLineContent(pos.lineNumber).trim().replace(/\s*\{\s*$/, '');
      out.push({ name: m[1], kind, params: m[2] ?? null, line: pos.lineNumber, col: pos.column, sig: lineText, doc: leadingComment(model, pos.lineNumber, lang) });
    }
  }
  return out;
}

function leadingComment(model, line, lang) {
  const lines = [];
  if (lang === 'python') {    // docstring on the next line
    const next = line < model.getLineCount() ? model.getLineContent(line + 1).trim() : '';
    const m = next.match(/^("""|''')(.*?)(\1)?$/);
    if (m) return m[2];
  }
  const marker = lang === 'python' ? '#' : '//';
  for (let l = line - 1; l >= 1; l--) {
    const t = model.getLineContent(l).trim();
    if (!t.startsWith(marker) && !t.startsWith('*') && !t.startsWith('/*')) break;
    lines.unshift(t.replace(/^(\/\/+|#+|\/\*+|\*+\/?)\s?/, ''));
  }
  return lines.join(' ').trim();
}

// ---------------------------------------------------------------- receiver type inference
const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

function paramTypeOwner(lang, type) {
  const t = String(type);
  const arr = t.endsWith('[]');
  if (lang === 'python') return arr ? 'list' : t === 'str' ? 'str' : null;
  if (lang === 'cpp') return arr ? 'vector' : t === 'str' ? 'string' : null;
  if (lang === 'rust') return arr ? 'vec' : t === 'str' ? 'string' : t === 'int' ? 'i64' : null;
  return null;
}

function inferType(model, lang, name) {
  const p = ctx.problem;
  const param = p?.params?.find(([n]) => n === name || n.replace(/_(\w)/g, (_, c) => c.toUpperCase()) === name);
  const text = model.getValue();
  const n = esc(name);
  let m;
  if (lang === 'python') {
    if ((m = text.match(new RegExp(`\\b${n}\\s*:\\s*([A-Za-z]+)`)))) {
      const t = m[1].toLowerCase();
      if (['list', 'str', 'dict', 'set', 'deque', 'tuple'].includes(t)) return t;
    }
    if ((m = text.match(new RegExp(`(?:^|[^.\\w])${n}\\s*=\\s*(.{1,40})`, 'm')))) {
      const r = m[1].trim();
      if (/^(collections\.)?Counter\(/.test(r)) return 'counter';
      if (/^(collections\.)?(defaultdict|OrderedDict)\(|^dict\(|^\{\s*\}|^\{[^}]*:/.test(r)) return 'dict';
      if (/^(collections\.)?deque\(/.test(r)) return 'deque';
      if (/^set\(|^\{[^:}]+\}/.test(r)) return 'set';
      if (/^\[|^list\(|^sorted\(/.test(r)) return 'list';
      if (/^["']|^str\(|^input\(|^f["']|\.join\(/.test(r)) return 'str';
    }
  } else if (lang === 'cpp') {
    if ((m = text.match(new RegExp(`\\b(?:std::)?(vector|string|unordered_map|map|unordered_set|multiset|set|queue|priority_queue|stack|deque|pair|array|bitset)\\b(?:\\s*<[^;(){}]*>)?\\s*&?\\s*${n}\\b`)))) return m[1];
  } else if (lang === 'rust') {
    if ((m = text.match(new RegExp(`\\b${n}\\s*:\\s*&?(?:'\\w+\\s+)?(?:mut\\s+)?(?:std::collections::)?(\\w+)`)))) return m[1].toLowerCase();
    if ((m = text.match(new RegExp(`let\\s+(?:mut\\s+)?${n}\\s*=\\s*([^;]{1,60})`)))) {
      const r = m[1];
      if (/^vec!|collect::<Vec|^Vec::/.test(r)) return 'vec';
      if (/^String::|\.to_string\(\)|\.to_owned\(\)|format!/.test(r)) return 'string';
      if ((m = r.match(/^(\w+)::/))) return m[1].toLowerCase();
    }
  }
  return param ? paramTypeOwner(lang, param[1]) : null;
}

// ---------------------------------------------------------------- lookup
/** Word under position (asm words may contain dots, e.g. `b.eq`, `.globl`). */
function wordAt(model, pos, lang) {
  const line = model.getLineContent(pos.lineNumber);
  const rx = ASM.has(lang) ? /[A-Za-z_.$][\w.$]*/g : /[A-Za-z_][\w]*!?/g;
  let m;
  while ((m = rx.exec(line))) {
    const s = m.index + 1, e = s + m[0].length;
    if (pos.column >= s && pos.column <= e) return { word: m[0], startColumn: s, endColumn: e, line };
  }
  return null;
}

/** Qualifier before a word: `heapq.`, `std::`, `v.`, `node->`, or `).` (chained call). */
function qualifierOf(before) {
  const m = before.match(/([A-Za-z_][\w]*)\s*(?:<[^<>]*>)?\s*(\.|::|->)\s*$/);
  if (m) return { q: m[1], op: m[2] };
  const c = before.match(/\)\s*(\.|::)\s*$/);
  if (c) return { q: null, op: c[1], chain: before };
  return null;
}

function resolve(model, lang, word, before) {
  const d = docs[lang];
  if (!d) return [];
  const lw = word.toLowerCase();
  // x86 AT&T: `divq` / `cmpb` fall back to the unsuffixed mnemonic's entry.
  const all = d.byName.get(word) || (ASM.has(lang) ? d.byName.get(lw) : null)
    || (lang === 'x86' && /^[a-z]{2,}[bwlq]$/.test(lw) ? d.byName.get(lw.slice(0, -1)) : null) || [];
  if (!all.length) return [];
  const qual = qualifierOf(before);
  if (qual) {
    let owners = null;
    if (qual.q) {
      const qn = normOwner(qual.q);
      if (all.some((e) => e._owner === qn)) owners = [qn];
      else {
        const t = inferType(model, lang, qual.q);
        if (t) owners = ownersFor(lang, t);
      }
    } else if (lang === 'rust' && /\b(iter|into_iter|iter_mut|chars|bytes|map|filter|enumerate|zip|rev|skip|take|lines|split_whitespace|windows|chunks|keys|values)\([^()]*\)\s*\.\s*$/.test(qual.chain)) {
      owners = ['iterator'];
    }
    const members = all.filter((e) => e._owner);
    const hit = owners ? members.filter((e) => owners.includes(e._owner)) : [];
    return hit.length ? hit : members.length ? members : all;
  }
  const globals = all.filter((e) => (GLOBAL_OWNERS[lang] || ['']).includes(e._owner) || e.kind === 'keyword' || e.kind === 'module' || e.kind === 'type');
  return globals.length ? globals : all;
}

// ---------------------------------------------------------------- rendering
const fence = (lang, code) => '```' + ({ arm64: 'asm', espresso: 'javascript' }[lang] || lang) + '\n' + code + '\n```';

const SEP = { python: '.', espresso: '.' };
const KIND_LABEL = { instruction: 'instruction', directive: 'directive', constant: 'constant', type: 'type', keyword: 'keyword', macro: 'macro', module: 'module', snippet: 'snippet', method: 'method', function: 'function' };

/** Split a signature's argument list on top-level commas. */
function sigArgs(sig) {
  const open = sig.indexOf('(');
  if (open < 0) return [];
  const out = []; let depth = 0, cur = '';
  for (const ch of sig.slice(open + 1)) {
    if ('([{<'.includes(ch)) depth++;
    else if (')]}>'.includes(ch)) { if (depth === 0) break; depth--; }
    if (ch === ',' && depth === 0) { out.push(cur.trim()); cur = ''; } else cur += ch;
  }
  if (cur.trim()) out.push(cur.trim());
  return out;
}

/** Where an entry comes from: `<stdio.h>`, `heapq`, `std::collections::HashMap`, … */
function providedBy(lang, e) {
  const h = (e.header || '').trim();
  if (h) {
    let m;
    if ((m = h.match(/^#include\s*(<[^>]+>|"[^"]+")/))) return m[1];
    if ((m = h.match(/^from\s+(\S+)\s+import/))) return m[1];
    if ((m = h.match(/^import\s+(\S+)/))) return m[1];
    if ((m = h.match(/^use\s+([^;]+)/))) return m[1].trim();
    return h;
  }
  if (e.owner) return null;
  if (e.kind === 'keyword') return null;
  return { python: 'builtins', rust: 'std prelude', espresso: 'ESPresso runtime', arm64: null, c: null, cpp: null }[lang] || null;
}

/** Hover sections, IDE style: title, origin / returns / params, docs, usage, full signature. */
function entrySections(lang, e, brief = false) {
  const q = e.owner ? `${e.owner}${SEP[lang] || '::'}${e.name}` : e.name;
  const from = providedBy(lang, e);
  const head = [`**${KIND_LABEL[e.kind] || e.kind}** \`${q}\``];
  if (from) head.push(`provided by \`${from}\``);
  else if (e.owner && e.kind === 'method') head.push(`member of \`${e.owner}\``);
  const out = [head.join('  \n')];
  if (brief) {
    out.push(fence(lang, e.sig || e.name));
    if (e.doc) out.push(e.doc);
    return out;
  }
  const api = [];
  if (e.returns) { const m = e.returns.match(/^(.+?)\s+[—–]\s+(.*)$/s); api.push(`→ ${m ? `\`${m[1]}\` — ${m[2]}` : `\`${e.returns}\``}`); }
  if (e.params?.length) {
    const args = sigArgs(e.sig || '');
    const decl = (label) => args.find((a) => a === label || new RegExp(`(^|[^\\w])${label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}([^\\w]|$)`).test(a)) || label;
    api.push('**Parameters:**\n' + e.params.map((p) => `- \`${decl(p.label)}\`${p.doc ? ` — ${p.doc}` : ''}`).join('\n'));
  }
  if (api.length) out.push(api.join('\n\n'));
  const body = [];
  if (e.doc) body.push(e.doc);
  if (e.example) body.push('**Usage**\n' + fence(lang, e.example));
  if (body.length) out.push(body.join('\n\n'));
  out.push(fence(lang, e.sig || e.name));
  return out;
}
const entryMarkdown = (lang, e) => entrySections(lang, e).join('\n\n---\n\n');

function problemHover(lang, word) {
  const p = ctx.problem;
  if (!p || p.kind === 'io' || !p.params || !ctx.lang) return null;
  const crLang = ctx.lang;
  let sig;
  try { sig = signature(p, crLang); } catch { return null; }
  const camel = (s) => s.replace(/_(\w)/g, (_, c) => c.toUpperCase());
  if (word === p.fn || word === camel(p.fn) || word === `_${p.fn}`) {
    const ps = p.params.map(([n, t]) => `- \`${n}\`: \`${t}\``).join('\n');
    return [fence(lang, sig), `**The function you implement.** Returns \`${p.returns}\`${p.mutates ? ` (the harness checks \`${p.mutates}\` after the call)` : ''}.`, ps].join('\n\n');
  }
  const param = p.params.find(([n]) => n === word || camel(n) === word);
  if (param) return [`**Parameter** \`${word}\`: Crucible type \`${param[1]}\``, fence(lang, sig)].join('\n\n');
  return null;
}

const TYPE_DOCS = {
  ListNode: { python: 'class ListNode:\n    val: int\n    next: Optional[ListNode]', c: 'struct ListNode {\n    long long val;\n    struct ListNode *next;\n};', cpp: 'struct ListNode {\n    long long val;\n    ListNode *next;\n    ListNode(long long x) : val(x), next(nullptr) {}\n};', rust: 'pub struct ListNode {\n    pub val: i64,\n    pub next: Option<Box<ListNode>>,\n}\nListNode::new(val)' },
  TreeNode: { python: 'class TreeNode:\n    val: int\n    left: Optional[TreeNode]\n    right: Optional[TreeNode]', c: 'struct TreeNode {\n    long long val;\n    struct TreeNode *left, *right;\n};', cpp: 'struct TreeNode {\n    long long val;\n    TreeNode *left, *right;\n    TreeNode(long long x) : val(x), left(nullptr), right(nullptr) {}\n};', rust: 'pub struct TreeNode {\n    pub val: i64,\n    pub left: Option<Rc<RefCell<TreeNode>>>,\n    pub right: Option<Rc<RefCell<TreeNode>>>,\n}\nTreeNode::new(val)  // borrow with node.borrow() / node.borrow_mut()' },
};

// ---------------------------------------------------------------- signature help
/** Find the call enclosing the cursor: name, qualifier text, and active argument index. */
function enclosingCall(model, pos) {
  const start = Math.max(1, pos.lineNumber - 30);
  const text = model.getValueInRange({ startLineNumber: start, startColumn: 1, endLineNumber: pos.lineNumber, endColumn: pos.column });
  let depth = 0, commas = 0, inStr = null;
  for (let i = text.length - 1; i >= 0; i--) {
    const ch = text[i];
    if (inStr) { if (ch === inStr && text[i - 1] !== '\\') inStr = null; continue; }
    if (ch === '"' || ch === "'") { if (!(ch === "'" && /\w/.test(text[i - 1] || ''))) inStr = ch; continue; }
    if (ch === ')' || ch === ']' || ch === '}') depth++;
    else if (ch === '[' || ch === '{') { if (depth === 0) return null; depth--; }
    else if (ch === '(') {
      if (depth === 0) {
        const before = text.slice(0, i);
        const m = before.match(/([A-Za-z_][\w]*!?)\s*(?:::<[^>]*>)?\s*$/);
        if (!m) return null;
        return { name: m[1], before: before.slice(0, before.length - m[0].length), active: commas };
      }
      depth--;
    } else if (ch === ',' && depth === 0) commas++;
    else if (ch === ';' && depth === 0) return null;
  }
  return null;
}

function splitParams(s) {
  const out = []; let depth = 0, cur = '';
  for (const ch of s) {
    if ('<([{'.includes(ch)) depth++;
    if ('>)]}'.includes(ch)) depth--;
    if (ch === ',' && depth === 0) { out.push(cur.trim()); cur = ''; } else cur += ch;
  }
  if (cur.trim()) out.push(cur.trim());
  return out;
}

function sigInfo(label, params) {
  // Parameter labels as [start, end] offsets inside the parentheses of `label`.
  const open = label.indexOf('(');
  let from = open + 1;
  const ps = [];
  for (const p of params) {
    const at = label.indexOf(p.label, from);
    if (at < 0) { ps.push({ label: p.label, documentation: p.doc ? { value: p.doc } : undefined }); continue; }
    ps.push({ label: [at, at + p.label.length], documentation: p.doc ? { value: p.doc } : undefined });
    from = at + p.label.length;
  }
  return ps;
}

// ---------------------------------------------------------------- registration
export async function installIde(m) {
  if (installed) return;
  installed = true;
  const K = m.languages.CompletionItemKind;
  const KIND = { function: K.Function, method: K.Method, type: K.Class, keyword: K.Keyword, macro: K.Function, constant: K.Constant, module: K.Module, instruction: K.Operator, directive: K.Keyword, snippet: K.Snippet };
  const SYM = m.languages.SymbolKind;

  for (const [mid, lang] of Object.entries(LANG_OF)) {
    loadDocs(lang);

    m.languages.registerHoverProvider(mid, {
      provideHover: async (model, pos) => {
        await loadDocs(lang);
        const w = wordAt(model, pos, lang);
        if (!w) return null;
        const range = new m.Range(pos.lineNumber, w.startColumn, pos.lineNumber, w.endColumn);
        const before = w.line.slice(0, w.startColumn - 1);
        const isMember = /(\.|->)\s*$/.test(before);
        if (!isMember) {
          const own = userSymbols(model, lang).find((s) => s.name === w.word);
          if (own && own.line !== pos.lineNumber) {
            return { range, contents: [{ value: fence(lang, own.sig) }, ...(own.doc ? [{ value: own.doc }] : []), { value: `*Defined on line ${own.line}. ⌘-click to jump.*` }] };
          }
          const ph = problemHover(lang, w.word);
          if (ph) return { range, contents: [{ value: ph }] };
          const td = TYPE_DOCS[w.word]?.[lang];
          if (td) return { range, contents: [{ value: fence(lang, td) }, { value: 'Provided by the Crucible harness.' }] };
        }
        if (lang === 'arm64') {
          const r = w.word.toLowerCase().match(/^[xw](\d+)$/);
          if (r && +r[1] <= 30 && !docs.arm64.byName.has(w.word.toLowerCase())) {
            const n = +r[1];
            const role = n <= 7 ? `argument / result register ${n}` : n === 8 ? 'indirect result register' : n <= 15 ? 'caller-saved scratch' : n <= 17 ? 'intra-procedure-call scratch (IP0/IP1)' : n === 18 ? 'platform register — reserved on Apple, never use' : n <= 28 ? 'callee-saved: save it before use and restore before `ret`' : n === 29 ? 'frame pointer (fp)' : 'link register (lr): the return address set by `bl`';
            return { range, contents: [{ value: `\`${w.word}\`: ${w.word[0] === 'w' ? '32-bit view (upper half zeroed on write)' : '64-bit'} — ${role}` }] };
          }
        }
        const hits = resolve(model, lang, w.word, before).slice(0, 3);
        if (!hits.length) return null;
        return { range, contents: hits.flatMap((e) => entrySections(lang, e, hits.length > 1)).map((value) => ({ value })) };
      },
    });

    m.languages.registerCompletionItemProvider(mid, {
      triggerCharacters: ASM.has(lang) ? ['.'] : ['.', ':', '>'],
      provideCompletionItems: async (model, pos) => {
        await loadDocs(lang);
        const d = docs[lang];
        const line = model.getLineContent(pos.lineNumber);
        const wordRx = ASM.has(lang) ? /[A-Za-z_.$][\w.$]*$/ : /[A-Za-z_][\w]*$/;
        const typed = line.slice(0, pos.column - 1).match(wordRx)?.[0] || '';
        const range = new m.Range(pos.lineNumber, pos.column - typed.length, pos.lineNumber, pos.column);
        const before = line.slice(0, pos.column - 1 - typed.length);
        // `:` and `>` only trigger for `::` and `->`.
        if (!typed && /[^:]:$|[^-]>$/.test(before)) return { suggestions: [] };
        const qual = ASM.has(lang) ? null : qualifierOf(before);
        const seen = new Set();
        const suggestions = [];
        const add = (e, sortGroup) => {
          const key = `${e.name}|${e._owner}`;
          if (seen.has(e.name + sortGroup) || seen.has(key)) return;
          seen.add(key); seen.add(e.name + sortGroup);
          const snippet = !qual || e.kind === 'method' || e._owner ? e.insert : null;
          suggestions.push({
            label: { label: e.name, description: e.owner || '' },
            kind: KIND[e.kind] ?? K.Text,
            detail: e.sig,
            documentation: { value: entryMarkdown(lang, e) },
            insertText: snippet || e.name,
            insertTextRules: snippet && snippet.includes('$') ? m.languages.CompletionItemInsertTextRule.InsertAsSnippet : undefined,
            range,
            sortText: sortGroup + e.name,
          });
        };
        if (qual) {
          let owners = null;
          if (qual.q) {
            const qn = normOwner(qual.q);
            if (d.all.some((e) => e._owner === qn)) owners = [qn];
            else { const t = inferType(model, lang, qual.q); if (t) owners = ownersFor(lang, t); }
          } else if (lang === 'rust' && /\b(iter|into_iter|iter_mut|chars|bytes|map|filter|enumerate|zip|rev|skip|take|lines|split_whitespace|windows|chunks|keys|values)\([^()]*\)\s*\.\s*$/.test(qual.chain)) owners = ['iterator'];
          for (const e of d.all) {
            if (!e._owner) continue;
            if (owners) { if (owners.includes(e._owner)) add(e, '0'); }
            else if (e.kind === 'method' && qual.op !== '::') add(e, '1');
          }
          return { suggestions };
        }
        // Your own functions, then the problem's names, then the reference entries.
        for (const s of userSymbols(model, lang)) {
          if (seen.has(s.name)) continue;
          seen.add(s.name);
          suggestions.push({ label: { label: s.name, description: 'your code' }, kind: s.kind === 'function' ? K.Function : s.kind === 'label' ? K.Reference : K.Struct, detail: s.sig, documentation: s.doc || undefined, insertText: s.name, range, sortText: '0' + s.name });
        }
        const globals = GLOBAL_OWNERS[lang] || [''];
  text = text.split('\n').filter((l) => !/\b(ListNode|TreeNode)\s*\(/.test(l)).join('\n'); // harness type boilerplate
        for (const e of d.all) {
          if (globals.includes(e._owner) || e.kind === 'keyword' || e.kind === 'module' || e.kind === 'type' || e.kind === 'instruction' || e.kind === 'directive') add(e, e.kind === 'keyword' ? '2' : '1');
        }
        // Identifiers already in the document (variables etc.).
        const words = new Set(model.getValue().match(/[A-Za-z_]\w{2,}/g) || []);
        for (const w of words) {
          if (w === typed || seen.has(w) || d.byName.has(w)) continue;
          seen.add(w);
          suggestions.push({ label: w, kind: K.Variable, insertText: w, range, sortText: '3' + w });
        }
        return { suggestions };
      },
    });

    if (!ASM.has(lang)) {
      m.languages.registerSignatureHelpProvider(mid, {
        signatureHelpTriggerCharacters: ['(', ','],
        signatureHelpRetriggerCharacters: [')'],
        provideSignatureHelp: async (model, pos) => {
          await loadDocs(lang);
          const call = enclosingCall(model, pos);
          if (!call || NOT_FN.has(call.name)) return null;
          const signatures = [];
          const own = userSymbols(model, lang).find((s) => s.name === call.name && s.params != null);
          if (own) {
            const label = `${own.name}(${own.params.trim()})`;
            const ps = splitParams(own.params).map((x) => ({ label: x }));
            signatures.push({ label, documentation: own.doc ? { value: own.doc } : undefined, parameters: sigInfo(label, ps) });
          }
          for (const e of resolve(model, lang, call.name, call.before)) {
            if (!e.sig || !e.sig.includes('(')) continue;
            signatures.push({ label: e.sig, documentation: { value: [e.doc, e.header && `*Requires* \`${e.header}\``].filter(Boolean).join('\n\n') }, parameters: sigInfo(e.sig, e.params || []) });
            if (signatures.length >= 4) break;
          }
          if (!signatures.length) return null;
          return { value: { signatures, activeSignature: 0, activeParameter: call.active }, dispose() {} };
        },
      });
    }

    m.languages.registerDocumentSymbolProvider(mid, {
      provideDocumentSymbols: (model) => userSymbols(model, lang).map((s) => {
        const r = new m.Range(s.line, 1, s.line, model.getLineMaxColumn(s.line));
        return { name: s.name, detail: s.sig, kind: s.kind === 'function' ? SYM.Function : s.kind === 'label' ? SYM.Key : SYM.Struct, range: r, selectionRange: r, tags: [] };
      }),
    });

    m.languages.registerDefinitionProvider(mid, {
      provideDefinition: (model, pos) => {
        const w = wordAt(model, pos, lang);
        if (!w) return null;
        const s = userSymbols(model, lang).find((x) => x.name === w.word);
        return s ? { uri: model.uri, range: new m.Range(s.line, s.col, s.line, s.col + s.name.length) } : null;
      },
    });

    m.languages.registerDocumentHighlightProvider(mid, {
      provideDocumentHighlights: (model, pos) => {
        const w = wordAt(model, pos, lang);
        if (!w || w.word.length < 2) return [];
        return model.findMatches(`\\b${esc(w.word)}\\b`, false, true, true, null, false).map((f) => ({ range: f.range, kind: 0 }));
      },
    });
  }
}

// ---------------------------------------------------------------- diagnostics
/**
 * Extract errors/warnings that point into the learner's code from compiler / runtime output.
 * Returns [{ line, col, severity: 'error'|'warning', message }].
 */
export function parseDiagnostics(lang, text, codeLineCount, isIo = false) {
  if (!text) return [];
  const out = [];
  const seen = new Set();
  const push = (line, col, severity, message) => {
    line = +line; col = +col || 1;
    if (!(line >= 1 && line <= codeLineCount)) return;
    const k = `${line}:${col}:${message}`;
    if (seen.has(k)) return;
    seen.add(k);
    out.push({ line, col, severity, message: message.trim() });
  };
  if (lang === 'c' || lang === 'cpp' || lang === 'asm' || lang === 'x86') {
    const files = isIo ? 'solution\\.\\w+|main\\.\\w+' : 'solution\\.\\w+';
    const rx = new RegExp(`(?:^|[\\s/])(?:${files}):(\\d+):(?:(\\d+):)?\\s*(fatal error|error|warning):\\s*(.*)$`, 'gm');
    let m;
    while ((m = rx.exec(text))) push(m[1], m[2], m[3] === 'warning' ? 'warning' : 'error', m[4]);
    // Sanitizer reports: "#0 0x... in fn solution.c:12:5"
    const san = text.match(/^(?:==\d+==)?ERROR: (?:AddressSanitizer|UndefinedBehaviorSanitizer|LeakSanitizer): ([^\n]*)/m);
    const rt = /solution\.\w+:(\d+):(\d+): runtime error: (.*)$/gm;
    while ((m = rt.exec(text))) push(m[1], m[2], 'error', 'runtime error: ' + m[3]);
    if (san) { const f = text.match(/#\d+ 0x[0-9a-f]+ in \S+ \S*solution\.\w+:(\d+)(?::(\d+))?/); if (f) push(f[1], f[2], 'error', san[1]); }
  } else if (lang === 'rust') {
    const rx = /^(error|warning)(?:\[(E\d+)\])?: ([^\n]*)\n\s*--> main\.rs:(\d+):(\d+)/gm;
    let m;
    while ((m = rx.exec(text))) push(m[4], m[5], m[1], (m[2] ? `${m[2]}: ` : '') + m[3]);
    const pr = /panicked at (?:main\.rs|src\/main\.rs):(\d+):(\d+):\n?([^\n]*)/g;
    while ((m = pr.exec(text))) push(m[1], m[2], 'error', 'panic: ' + m[3]);
  } else if (lang === 'python') {
    // Each traceback: the last solution.py frame + the final "XxxError: msg" line.
    for (const block of text.split(/(?=Traceback \(most recent call last\))/)) {
      const frames = [...block.matchAll(/File "(?:[^"\n]*\/)?solution\.py", line (\d+)/g)];
      if (!frames.length) continue;
      const msg = block.match(/^\s*(\w+(?:Error|Exception|Interrupt)\b.*)$/m);
      push(frames[frames.length - 1][1], 1, 'error', msg ? msg[1] : 'error');
    }
  } else if (lang === 'espresso') {
    let m;
    const parse = /Error: (.*?) at \[Line (\d+), Col (\d+)\]/g;
    while ((m = parse.exec(text))) push(m[2], m[3], 'error', m[1]);
    const run = /([^\n]*)\n\[line (\d+)(?:, col (\d+))?\]/g;
    while ((m = run.exec(text))) push(m[2], m[3], 'error', m[1]);
  }
  return out;
}

/** Show diagnostics as squiggles; they clear line-by-line as you edit them. */
export function showDiagnostics(m, editor, diags) {
  const model = editor.getModel();
  if (!model) return;
  const toMarker = (dg) => {
    const max = model.getLineMaxColumn(dg.line);
    const col = Math.min(dg.col, max);
    const word = model.getWordAtPosition({ lineNumber: dg.line, column: col });
    const whole = dg.col <= 1 && !word;
    return {
      severity: dg.severity === 'warning' ? m.MarkerSeverity.Warning : m.MarkerSeverity.Error,
      message: dg.message,
      startLineNumber: dg.line, endLineNumber: dg.line,
      startColumn: whole ? model.getLineFirstNonWhitespaceColumn(dg.line) || 1 : word ? word.startColumn : col,
      endColumn: whole ? max : word ? word.endColumn : Math.min(col + 1, max),
      source: 'crucible',
    };
  };
  m.editor.setModelMarkers(model, 'crucible', diags.map(toMarker));
  if (diags[0]) editor.revealLineInCenterIfOutsideViewport(diags[0].line);
}

export function clearDiagnostics(m, editor) {
  const model = editor?.getModel();
  if (model) m.editor.setModelMarkers(model, 'crucible', []);
}

/** Drop markers on lines the user edits. */
export function trackDiagnosticEdits(m, editor) {
  return editor.onDidChangeModelContent((ev) => {
    const model = editor.getModel();
    const markers = m.editor.getModelMarkers({ owner: 'crucible', resource: model.uri });
    if (!markers.length) return;
    const touched = (mk) => ev.changes.some((c) => mk.startLineNumber >= c.range.startLineNumber && mk.startLineNumber <= c.range.endLineNumber);
    const lineDelta = ev.changes.reduce((n, c) => n + (c.text.split('\n').length - 1) - (c.range.endLineNumber - c.range.startLineNumber), 0);
    if (lineDelta) { m.editor.setModelMarkers(model, 'crucible', []); return; }
    const keep = markers.filter((mk) => !touched(mk));
    if (keep.length !== markers.length) m.editor.setModelMarkers(model, 'crucible', keep);
  });
}

// ---------------------------------------------------------------- "new in this problem"
// Library functions a problem's starter (and language notes) use for the first time in
// the curriculum, so the description can show how to call them. Starters never contain
// the answer, so this can't spoil anything.
const INTRO_KINDS = new Set(['function', 'method', 'macro', 'constant', 'instruction']);
const firstSeen = {}; // lang -> Map(entry -> problem id)

const INTRO_STOP = new Set(['true', 'false', 'True', 'False', 'None', 'NULL', 'null', 'main']);
const CALLABLE = new Set(['function', 'method', 'macro']);

function entriesIn(d, text, lang) {
  const out = new Set();
  if (ASM.has(lang)) {
    // Assembly: the mnemonic at the start of each code line (comments describe goals).
    for (const raw of text.split('\n')) {
      const line = raw.replace(/(\/\/|#|;).*$/, '').replace(/^\s*[\w.$]+:/, '').trim();
      const w = line.match(/^[a-z][a-z0-9.]*/i)?.[0].toLowerCase();
      const e = w && (d.byName.get(w) || []).find((x) => x.kind === 'instruction');
      if (e) out.add(e);
    }
    return out;
  }
  const globals = GLOBAL_OWNERS[lang] || [''];
  text = text.split('\n').filter((l) => !/\b(ListNode|TreeNode)\s*\(/.test(l)).join('\n'); // harness type boilerplate
  const rx = /(\.|->|::)?\s*([A-Za-z_][A-Za-z0-9_]*!?)(\s*\()?/g;
  let m;
  while ((m = rx.exec(text))) {
    if (INTRO_STOP.has(m[2])) continue;
    const member = !!m[1], called = !!m[3];
    const cands = (d.byName.get(m[2]) || []).filter((e) => INTRO_KINDS.has(e.kind) && e.kind !== 'instruction' && (CALLABLE.has(e.kind) ? called : true));
    if (!cands.length) continue;
    // The identifier written before `.` / `::`, e.g. `stdin` in sys.stdin.read().
    const qual = member ? (text.slice(0, m.index).match(/([A-Za-z_]\w*)\s*(?:<[^<>]*>)?\s*$/)?.[1] || '').toLowerCase() : '';
    const ownerTail = (e) => (e.owner || '').replace(/<.*$/, '').split(/::|\./).pop().toLowerCase();
    const list = cands.filter((e) => {
      if (e.kind === 'method') return member;
      if (!e.owner || globals.includes(normOwner(e.owner))) return !member || ownerTail(e) === qual;
      return member && ownerTail(e) === qual; // module members (math.e, io::stdin) only when qualified
    });
    if (!list.length) continue;
    out.add(list.find((e) => e.owner && new RegExp(`\\b${e.owner.replace(/^std::/, '').replace(/<.*$/, '').replace(/[^\w]/g, '')}\\b`, 'i').test(text)) || list[0]);
  }
  return out;
}

export async function introducedEntries(problems, problem, lang, textOf) {
  const dl = lang === 'asm' ? 'arm64' : lang;
  const d = await loadDocs(dl);
  if (!d.all.length) return [];
  if (!firstSeen[dl]) {
    const seen = new Map();
    for (const p of problems) {
      let t;
      try { t = textOf(p, lang); } catch { continue; }
      if (!t) continue;
      for (const e of entriesIn(d, t, dl)) if (!seen.has(e)) seen.set(e, p.id);
    }
    firstSeen[dl] = seen;
  }
  const seen = firstSeen[dl];
  return [...seen].filter(([, id]) => id === problem.id).map(([e]) => e).slice(0, 8);
}

/**
 * Markdown card for the description panel: a beginner-oriented explanation built
 * from the entry's `learn` block (plain English per parameter, return value,
 * commented example, pitfalls), falling back to the terse hover docs.
 */
export function entryCard(lang, e) {
  const dl = lang === 'asm' ? 'arm64' : lang;
  const L = e.learn || {};
  const from = providedBy(dl, e);
  const q = e.owner && e.kind === 'method' ? `${e.owner}${SEP[dl] || '::'}${e.name}` : e.name;
  const out = [`#### \`${q}\`${L.summary ? ` — ${L.summary}` : ''}`];
  if (from) out.push(`<span class="intro-from">from \`${from}\`${e.header ? ` · add \`${e.header}\` at the top` : ''}</span>`);
  out.push(L.what || e.doc || '');
  out.push('**How to write it**\n' + fence(dl, e.sig || e.name));
  const args = sigArgs(e.sig || '');
  const parts = L.params ? Object.entries(L.params) : (e.params || []).map((p) => [p.label, p.doc]);
  if (parts.length) {
    const rows = parts.map(([label, text]) => {
      const decl = args.find((a) => new RegExp(`(^|[^\\w])${label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}([^\\w]|$)`).test(a)) || '';
      const type = decl && decl !== label ? decl.replace(new RegExp(`\\b${label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`), '').replace(/[:=]\s*$/, '').trim() : '';
      return { label, type, text: String(text).replace(/\n/g, ' ').replace(/\|/g, '\\|') };
    });
    const typed = rows.some((r) => r.type);
    out.push(typed
      ? `| Part | Type | What it means |\n|---|---|---|\n${rows.map((r) => `| \`${r.label}\` | ${r.type ? `\`${r.type}\`` : ''} | ${r.text} |`).join('\n')}`
      : `| Part | What it means |\n|---|---|\n${rows.map((r) => `| \`${r.label}\` | ${r.text} |`).join('\n')}`);
  }
  if (L.returns || e.returns) out.push(`**What you get back:** ${L.returns || e.returns}`);
  const ex = L.example || e.example;
  if (ex) out.push('**Example**\n' + fence(dl, ex));
  if (L.watch?.length) out.push('**Watch out**\n' + L.watch.map((w) => `- ${w}`).join('\n'));
  return out.filter(Boolean).join('\n\n');
}
