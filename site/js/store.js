// Progress, drafts and settings, persisted in localStorage.
const KEY = 'crucible.v1';

const DEFAULTS = {
  solved: {},       // pid -> { at, langs: [] }
  attempted: {},    // pid -> at
  code: {},         // "pid:lang" -> source
  subs: {},         // pid -> [{ at, lang, status, passed, total, ms }]
  hints: {},        // pid -> number of hints opened
  revealed: {},     // pid -> true (explanation viewed before solving)
  activity: {},     // "YYYY-MM-DD" -> count of accepted submissions
  lastLang: 'python',
  lastProblem: null,
  settings: {
    theme: 'system',
    fontSize: 14,
    companionUrl: 'http://localhost:4747',
    pythonRuntime: 'auto', // auto | browser | local
    vim: false,
    minimap: false,
    coachSpoilers: false,
  },
};

let state = load();
const listeners = new Set();

function load() {
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) || '{}');
    return { ...structuredClone(DEFAULTS), ...raw, settings: { ...DEFAULTS.settings, ...(raw.settings || {}) } };
  } catch {
    return structuredClone(DEFAULTS);
  }
}

let saveTimer = null;
function save() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { console.warn('save failed', e); }
  }, 150);
}

export const store = {
  get: () => state,
  settings: () => state.settings,
  setSetting(k, v) { state.settings[k] = v; save(); listeners.forEach((f) => f('settings')); },
  onChange(f) { listeners.add(f); return () => listeners.delete(f); },

  draft(pid, lang) { return state.code[`${pid}:${lang}`]; },
  saveDraft(pid, lang, code) { state.code[`${pid}:${lang}`] = code; save(); },
  clearDraft(pid, lang) { delete state.code[`${pid}:${lang}`]; save(); },

  isSolved: (pid) => !!state.solved[pid],
  isAttempted: (pid) => !!state.attempted[pid],

  recordSubmission(pid, sub) {
    const list = (state.subs[pid] ||= []);
    list.unshift(sub);
    if (list.length > 25) list.length = 25;
    state.attempted[pid] ||= sub.at;
    let firstSolve = false;
    if (sub.status === 'accepted') {
      const s = state.solved[pid];
      if (!s) { state.solved[pid] = { at: sub.at, langs: [sub.lang] }; firstSolve = true; }
      else if (!s.langs.includes(sub.lang)) s.langs.push(sub.lang);
      const day = dayKey(new Date(sub.at));
      state.activity[day] = (state.activity[day] || 0) + 1;
    }
    save();
    listeners.forEach((f) => f('progress'));
    return firstSolve;
  },
  submissions: (pid) => state.subs[pid] || [],
  hintsOpened: (pid) => state.hints[pid] || 0,
  openHint(pid, n) { state.hints[pid] = Math.max(state.hints[pid] || 0, n); save(); },
  isRevealed: (pid) => !!state.revealed[pid] || !!state.solved[pid],
  reveal(pid) { state.revealed[pid] = true; save(); },
  setLastLang(l) { state.lastLang = l; save(); },
  setLastProblem(p) { state.lastProblem = p; save(); },

  streak() {
    let n = 0;
    const d = new Date();
    if (!state.activity[dayKey(d)]) d.setDate(d.getDate() - 1); // today not done yet doesn't break the streak
    while (state.activity[dayKey(d)]) { n++; d.setDate(d.getDate() - 1); }
    return n;
  },

  exportJSON: () => JSON.stringify(state, null, 2),
  importJSON(text) {
    const obj = JSON.parse(text);
    if (typeof obj !== 'object' || !obj.solved) throw new Error('Not a Crucible backup');
    state = { ...structuredClone(DEFAULTS), ...obj, settings: { ...DEFAULTS.settings, ...(obj.settings || {}) } };
    localStorage.setItem(KEY, JSON.stringify(state));
    listeners.forEach((f) => f('progress'));
  },
  reset() { state = structuredClone(DEFAULTS); localStorage.removeItem(KEY); listeners.forEach((f) => f('progress')); },
};

export function dayKey(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}
