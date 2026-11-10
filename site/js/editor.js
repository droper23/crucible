// Monaco editor bootstrap plus ESPresso and ARM64 syntax highlighting.
import { installIde } from './ide.js';
const MONACO = 'https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min';
let monacoP = null;

export function loadMonaco() {
  if (monacoP) return monacoP;
  monacoP = new Promise((resolve, reject) => {
    // Monaco's workers must be same-origin; bootstrap them from a data: URL.
    window.MonacoEnvironment = {
      getWorkerUrl: () => `data:text/javascript;charset=utf-8,${encodeURIComponent(`self.MonacoEnvironment={baseUrl:'${MONACO}/'};importScripts('${MONACO}/vs/base/worker/workerMain.js');`)}`,
    };
    window.require.config({ paths: { vs: `${MONACO}/vs` } });
    window.require(['vs/editor/editor.main'], () => {
      const m = window.monaco;
      registerLanguages(m);
      defineThemes(m);
      installIde(m);
      resolve(m);
    }, reject);
  });
  return monacoP;
}

export function monacoTheme() {
  return document.documentElement.dataset.theme === 'light' ? 'crucible-light' : 'crucible-dark';
}

function defineThemes(m) {
  m.editor.defineTheme('crucible-dark', {
    base: 'vs-dark', inherit: true,
    rules: [
      { token: 'comment', foreground: '6b7389', fontStyle: 'italic' },
      { token: 'keyword', foreground: 'ff9e64' },
      { token: 'string', foreground: '9ece6a' },
      { token: 'number', foreground: 'e0af68' },
      { token: 'type', foreground: '7dcfff' },
      { token: 'type.identifier', foreground: '7dcfff' },
      { token: 'identifier.function', foreground: '7aa2f7' },
      { token: 'predefined', foreground: 'bb9af7' },
      { token: 'register', foreground: 'bb9af7' },
      { token: 'directive', foreground: 'f7768e' },
      { token: 'label', foreground: '7aa2f7', fontStyle: 'bold' },
      { token: 'todo', foreground: 'ff5e3a', fontStyle: 'bold' },
    ],
    colors: {
      'editor.background': '#15171e',
      'editor.lineHighlightBackground': '#1c1f29',
      'editorLineNumber.foreground': '#3e4457',
      'editorLineNumber.activeForeground': '#9aa1b5',
      'editorGutter.background': '#15171e',
      'editor.selectionBackground': '#ff8a3d33',
      'editorCursor.foreground': '#ff8a3d',
      'editorIndentGuide.background1': '#22252f',
      'editorWidget.background': '#1b1e27',
      'editorBracketMatch.border': '#ff8a3d88',
      'scrollbarSlider.background': '#ffffff14',
    },
  });
  m.editor.defineTheme('crucible-light', {
    base: 'vs', inherit: true,
    rules: [
      { token: 'comment', foreground: '8a8f9e', fontStyle: 'italic' },
      { token: 'keyword', foreground: 'c2410c' },
      { token: 'string', foreground: '15803d' },
      { token: 'number', foreground: 'b45309' },
      { token: 'type', foreground: '0369a1' },
      { token: 'predefined', foreground: '7c3aed' },
      { token: 'register', foreground: '7c3aed' },
      { token: 'directive', foreground: 'be123c' },
      { token: 'label', foreground: '1d4ed8', fontStyle: 'bold' },
      { token: 'todo', foreground: 'dc2626', fontStyle: 'bold' },
    ],
    colors: {
      'editor.background': '#ffffff',
      'editor.lineHighlightBackground': '#f7f7f4',
      'editorLineNumber.foreground': '#c4c4bc',
      'editorCursor.foreground': '#f0661f',
      'editor.selectionBackground': '#f0661f2a',
    },
  });
}

function registerLanguages(m) {
  // ESPresso: C-family syntax with `fn`, `var`, ranges and string interpolation.
  m.languages.register({ id: 'espresso', extensions: ['.espr'] });
  m.languages.setMonarchTokensProvider('espresso', {
    keywords: ['fn', 'var', 'const', 'if', 'else', 'while', 'for', 'in', 'return', 'break', 'continue', 'and', 'or', 'import', 'try', 'catch'],
    constants: ['true', 'false', 'null'],
    builtins: ['print', 'log', 'len', 'typeOf', 'millis', 'delay', 'setInterval', 'setTimeout', 'on', 'emit', 'gpio'],
    tokenizer: {
      root: [
        [/\/\/.*$/, 'comment'],
        [/#.*$/, 'comment'],
        [/"/, 'string', '@string'],
        [/\d+\.\d+/, 'number'],
        [/\d+/, 'number'],
        [/\.\./, 'operator'],
        [/[a-zA-Z_]\w*(?=\s*\()/, { cases: { '@keywords': 'keyword', '@builtins': 'predefined', '@default': 'identifier.function' } }],
        [/[a-zA-Z_]\w*/, { cases: { '@keywords': 'keyword', '@constants': 'number', '@builtins': 'predefined', '@default': 'identifier' } }],
        [/[{}()[\]]/, '@brackets'],
        [/[+\-*/=<>!&|]+/, 'operator'],
      ],
      string: [
        [/\{[^}]*\}/, 'type'],
        [/\\./, 'string.escape'],
        [/"/, 'string', '@pop'],
        [/[^"\\{]+/, 'string'],
      ],
    },
  });
  m.languages.setLanguageConfiguration('espresso', {
    comments: { lineComment: '//' },
    brackets: [['{', '}'], ['[', ']'], ['(', ')']],
    autoClosingPairs: [{ open: '{', close: '}' }, { open: '[', close: ']' }, { open: '(', close: ')' }, { open: '"', close: '"' }],
    indentationRules: { increaseIndentPattern: /\{[^}]*$/, decreaseIndentPattern: /^\s*\}/ },
  });

  // ARM64 assembly (Apple clang syntax).
  m.languages.register({ id: 'arm64', extensions: ['.s'] });
  m.languages.setMonarchTokensProvider('arm64', {
    ignoreCase: true,
    tokenizer: {
      root: [
        [/\/\/\s*TODO.*$/, 'todo'],
        [/(\/\/|;).*$/, 'comment'],
        [/\/\*/, 'comment', '@block'],
        [/^\s*[A-Za-z_.$][\w.$]*:/, 'label'],
        [/^\s*\d+:/, 'label'],
        [/\.[a-z_0-9]+/, 'directive'],
        [/\b([xw]([12]?\d|30)|[xw]zr|sp|lr|fp|[dsqvb]\d+)\b/, 'register'],
        [/#-?(0x[0-9a-f]+|\d+)/, 'number'],
        [/\b(0x[0-9a-f]+|\d+)[fb]?\b/, 'number'],
        [/"([^"\\]|\\.)*"/, 'string'],
        [/^\s*[a-z][a-z0-9.]*/, 'keyword'],
        [/[[\]!,]/, 'delimiter'],
      ],
      block: [[/\*\//, 'comment', '@pop'], [/./, 'comment']],
    },
  });
  m.languages.setLanguageConfiguration('arm64', { comments: { lineComment: '//', blockComment: ['/*', '*/'] } });
}

export async function createEditor(host, { value, language, onChange, onRun, onSubmit, settings }) {
  const m = await loadMonaco();
  const editor = m.editor.create(host, {
    value,
    language,
    theme: monacoTheme(),
    automaticLayout: true,
    fontFamily: "'JetBrains Mono', ui-monospace, Menlo, monospace",
    fontLigatures: true,
    fontSize: settings.fontSize || 14,
    lineHeight: 1.6,
    minimap: { enabled: !!settings.minimap },
    scrollBeyondLastLine: false,
    padding: { top: 14, bottom: 14 },
    renderLineHighlight: 'all',
    smoothScrolling: true,
    cursorSmoothCaretAnimation: 'on',
    cursorBlinking: 'smooth',
    tabSize: 4,
    bracketPairColorization: { enabled: true },
    guides: { indentation: true },
    stickyScroll: { enabled: true, maxLineCount: 3 },
    fixedOverflowWidgets: true,
    hover: { enabled: true, delay: 350, sticky: true },
    parameterHints: { enabled: true, cycle: true },
    quickSuggestions: { other: true, comments: false, strings: false },
    suggestOnTriggerCharacters: true,
    suggest: { showStatusBar: true, preview: true, snippetsPreventQuickSuggestions: false, insertMode: 'replace' },
    wordBasedSuggestions: 'off',
    tabCompletion: 'on',
    occurrencesHighlight: 'singleFile',
    renderWhitespace: 'selection',
    'semanticHighlighting.enabled': false,
    linkedEditing: true,
    inlayHints: { enabled: 'on' },
  });
  editor.onDidChangeModelContent(() => onChange?.(editor.getValue()));
  editor.addCommand(m.KeyMod.CtrlCmd | m.KeyCode.Quote, () => onRun?.());
  editor.addCommand(m.KeyMod.CtrlCmd | m.KeyCode.Enter, () => onSubmit?.());
  return { editor, monaco: m };
}

export async function colorizeIn(root) {
  const blocks = root.querySelectorAll('pre code[data-lang]:not([data-colored])');
  if (!blocks.length) return;
  const m = await loadMonaco();
  const map = { py: 'python', python: 'python', c: 'c', cpp: 'cpp', 'c++': 'cpp', rust: 'rust', rs: 'rust', javascript: 'espresso', js: 'espresso', espresso: 'espresso', espr: 'espresso', asm: 'arm64', s: 'arm64', arm64: 'arm64', bash: 'shell', sh: 'shell', shell: 'shell' };
  for (const el of blocks) {
    el.dataset.colored = '1';
    const lang = map[el.dataset.lang.toLowerCase()];
    if (!lang) continue;
    try {
      const html = await m.editor.colorize(el.textContent, lang, { tabSize: 4 });
      el.innerHTML = html.replace(/<br\/>$/, '');
    } catch { /* leave plain */ }
  }
}
