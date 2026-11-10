// Progress, drafts and settings, persisted in localStorage.
const KEY = 'crucible.v1';

const DEFAULTS = {
  solved: {},       // pid -> { at, langs: [] }
  attempted: {},    // pid -> at
  code: {},         // "pid:lang" -> source
  codeAt: {},       // "pid:lang" -> ms of last edit (cloud-sync merge)
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
const persistHooks = new Set();

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
    persistHooks.forEach((f) => f());
  }, 150);
}

export const store = {
  get: () => state,
  settings: () => state.settings,
  setSetting(k, v) { state.settings[k] = v; save(); listeners.forEach((f) => f('settings')); },
  onChange(f) { listeners.add(f); return () => listeners.delete(f); },

  draft(pid, lang) { return state.code[`${pid}:${lang}`]; },
  saveDraft(pid, lang, code) { const k = `${pid}:${lang}`; state.code[k] = code; (state.codeAt ||= {})[k] = Date.now(); save(); },
  clearDraft(pid, lang) { const k = `${pid}:${lang}`; delete state.code[k]; (state.codeAt ||= {})[k] = Date.now(); save(); },

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

  /** Called after every local write (cloud sync hooks in here). */
  onPersist(f) { persistHooks.add(f); return () => persistHooks.delete(f); },

  /** The part of the state that syncs across devices. */
  syncSnapshot() {
    return {
      solved: state.solved, attempted: state.attempted, subs: state.subs, hints: state.hints,
      revealed: state.revealed, activity: state.activity, code: state.code, codeAt: state.codeAt || {},
      lastLang: state.lastLang,
    };
  },

  /** Merge progress from another device: nothing is ever lost, newest draft wins. */
  mergeRemote(r) {
    if (!r || typeof r !== 'object') return;
    for (const [pid, v] of Object.entries(r.solved || {})) {
      const s = state.solved[pid];
      if (!s) state.solved[pid] = { at: v.at, langs: [...(v.langs || [])] };
      else { s.at = Math.min(s.at, v.at || s.at); for (const l of v.langs || []) if (!s.langs.includes(l)) s.langs.push(l); }
    }
    for (const [pid, at] of Object.entries(r.attempted || {})) state.attempted[pid] = state.attempted[pid] ? Math.min(state.attempted[pid], at) : at;
    for (const [pid, n] of Object.entries(r.hints || {})) state.hints[pid] = Math.max(state.hints[pid] || 0, n);
    for (const pid of Object.keys(r.revealed || {})) state.revealed[pid] = true;
    for (const [d, n] of Object.entries(r.activity || {})) state.activity[d] = Math.max(state.activity[d] || 0, n);
    for (const [pid, list] of Object.entries(r.subs || {})) {
      const mine = state.subs[pid] || [];
      const seen = new Set(mine.map((x) => `${x.at}|${x.lang}`));
      const all = mine.concat((list || []).filter((x) => !seen.has(`${x.at}|${x.lang}`)));
      all.sort((a, b) => b.at - a.at);
      state.subs[pid] = all.slice(0, 25);
    }
    state.codeAt ||= {};
    const rAt = r.codeAt || {};
    for (const k of new Set([...Object.keys(r.code || {}), ...Object.keys(rAt)])) {
      const mineAt = state.codeAt[k] || 0, theirs = rAt[k] || 0;
      if (theirs > mineAt || (!(k in state.code) && !state.codeAt[k] && r.code?.[k] != null)) {
        if (r.code?.[k] != null) state.code[k] = r.code[k]; else delete state.code[k];
        state.codeAt[k] = theirs;
      }
    }
    if (r.lastLang && !state.lastLang) state.lastLang = r.lastLang;
    save();
    listeners.forEach((f) => f('remote'));
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
