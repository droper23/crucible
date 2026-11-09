// Markdown rendering with highlighted code blocks.
import { colorizeIn } from './editor.js';

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
export { esc };

const LABELS = { python: 'Python', py: 'Python', c: 'C', cpp: 'C++', rust: 'Rust', rs: 'Rust', javascript: 'ESPresso', espresso: 'ESPresso', asm: 'ARM64', s: 'ARM64', bash: 'Shell', sh: 'Shell', text: '', '': '' };

let configured = false;
function configure() {
  if (configured) return;
  configured = true;
  const renderer = new window.marked.Renderer();
  renderer.code = (code, info) => {
    // marked v12 passes (code, infostring)
    const text = typeof code === 'object' ? code.text : code;
    const lang = String((typeof code === 'object' ? code.lang : info) || '').trim().split(/\s+/)[0];
    const label = LABELS[lang.toLowerCase()] ?? lang;
    return `<pre><span class="lang-label">${esc(label)}</span><button class="btn sm ghost copy" data-copy>Copy</button><code data-lang="${esc(lang || 'text')}">${esc(text)}</code></pre>`;
  };
  renderer.link = (href, title, text) => {
    const h = typeof href === 'object' ? href.href : href;
    const t = typeof href === 'object' ? href.text : text;
    const internal = String(h).startsWith('#');
    return `<a href="${esc(h)}"${internal ? '' : ' target="_blank" rel="noopener"'}>${t}</a>`;
  };
  window.marked.setOptions({ renderer, gfm: true, breaks: false });
}

export function md(text) {
  configure();
  return window.marked.parse(String(text || ''));
}

/** Render markdown into element, then colorize code and wire copy buttons. */
export function renderMd(el, text) {
  el.innerHTML = md(text);
  enhance(el);
}

export function enhance(el) {
  el.querySelectorAll('[data-copy]').forEach((b) => {
    b.onclick = async () => {
      const code = b.parentElement.querySelector('code').textContent;
      try { await navigator.clipboard.writeText(code); b.textContent = 'Copied'; setTimeout(() => (b.textContent = 'Copy'), 1200); } catch {}
    };
  });
  colorizeIn(el);
}
