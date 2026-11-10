// Optional cloud sync: sign in with Google and progress (solved problems, drafts,
// submissions, hints, streak) follows you across browsers and devices.
//
// Local-first: everything keeps working signed out or offline; Firestore is layered
// on top. Same Firebase project as learn-assembly (the config is a public client key,
// not a secret: security is the Firestore rule keyed on request.auth.uid), but its
// own collection, crucibleProgress/{uid}, so the two sites never touch each other's
// data. The rule this collection needs is in the README ("Progress sync").
import { store } from './store.js';

const COLLECTION = 'crucibleProgress';
const SIGNED_IN_FLAG = 'crucible.signedIn';
const SDK = 'https://www.gstatic.com/firebasejs/10.14.1/';
const FIREBASE_CONFIG = {
  apiKey: 'AIzaSyAi1CzJbDF8pgfjRdjIs4r3m1H_moW6QwY',
  authDomain: 'farsi-f2116.firebaseapp.com',
  projectId: 'farsi-f2116',
  storageBucket: 'farsi-f2116.firebasestorage.app',
  messagingSenderId: '503195222686',
  appId: '1:503195222686:web:690d5aad975ab638bbf18f',
};
const MAX_DOC = 900_000; // Firestore documents cap at 1 MiB

let auth = null, db = null, loading = null, user = null, pushTimer = null, applying = false;
let state = { status: 'signed-out', message: '', user: null };
const subs = new Set();

function set(patch) {
  state = { ...state, ...patch };
  subs.forEach((f) => f(state));
}
export const syncState = () => state;
export function onSync(f) { subs.add(f); f(state); return () => subs.delete(f); }

let fs = null, fa = null; // Firebase module namespaces (Firestore, Auth)

function ensureFirebase() {
  if (auth) return Promise.resolve();
  // One shared load: a resume-on-load racing a Sign-in click must not initialize twice.
  // ES-module builds: unlike the compat bundles they don't trip over Monaco's AMD loader.
  loading ??= Promise.all([
    import(SDK + 'firebase-app.js'), import(SDK + 'firebase-auth.js'), import(SDK + 'firebase-firestore.js'),
  ]).then(([app, a, f]) => {
    const fbApp = app.initializeApp(FIREBASE_CONFIG, 'crucible');
    fa = a; fs = f;
    auth = a.getAuth(fbApp);
    db = f.getFirestore(fbApp);
    a.onAuthStateChanged(auth, onAuth);
  }).catch((e) => { loading = null; throw e; });
  return loading;
}

/** Keep the document under Firestore's size cap: drop code stored in old submissions first. */
function payload() {
  const snap = store.syncSnapshot();
  let doc = { ...snap, updatedAt: Date.now() };
  if (JSON.stringify(doc).length > MAX_DOC) {
    const subs = {};
    for (const [pid, list] of Object.entries(snap.subs)) subs[pid] = list.map(({ code, ...rest }) => rest);
    doc = { ...doc, subs };
  }
  if (JSON.stringify(doc).length > MAX_DOC) throw new Error('Progress is too large to sync (over 1 MB of drafts).');
  return doc;
}

function pushNow() {
  clearTimeout(pushTimer); pushTimer = null;
  if (!user || !db) return;
  let doc;
  try { doc = payload(); } catch (e) { set({ status: 'error', message: e.message }); return; }
  set({ status: 'syncing' });
  fs.setDoc(fs.doc(db, COLLECTION, user.uid), doc)
    .then(() => set({ status: 'synced', message: '', at: Date.now() }))
    .catch((e) => set({ status: 'error', message: friendly(e) }));
}

function schedulePush() {
  if (!user || applying) return;
  clearTimeout(pushTimer);
  pushTimer = setTimeout(pushNow, 1500);
}

async function pull() {
  if (!user || !db) return;
  set({ status: 'syncing' });
  try {
    const snap = await fs.getDoc(fs.doc(db, COLLECTION, user.uid));
    applying = true;
    try { if (snap.exists()) store.mergeRemote(snap.data()); } finally { applying = false; }
    pushNow(); // upload the merged result (also first-time upload)
  } catch (e) {
    set({ status: 'error', message: friendly(e) });
  }
}

function onAuth(u) {
  user = u;
  if (u) {
    try { localStorage.setItem(SIGNED_IN_FLAG, '1'); } catch {}
    set({ user: { name: u.displayName || u.email, email: u.email, photo: u.photoURL }, status: 'syncing', message: '' });
    pull();
  } else {
    try { localStorage.removeItem(SIGNED_IN_FLAG); } catch {}
    set({ user: null, status: 'signed-out', message: '' });
  }
}

function friendly(e) {
  const code = String(e?.code || '');
  if (code === 'auth/unauthorized-domain') return `${location.hostname} isn't an authorized domain in the Firebase project (Authentication → Settings → Authorized domains).`;
  if (code === 'auth/popup-blocked') return 'The sign-in popup was blocked. Allow popups for this site and try again.';
  if (code === 'auth/popup-closed-by-user' || code === 'auth/cancelled-popup-request') return 'Sign-in was cancelled.';
  if (code === 'auth/network-request-failed') return "Couldn't reach Google's sign-in servers. Check your connection.";
  if (code === 'permission-denied' || /insufficient permissions/i.test(e?.message || '')) return 'Firestore refused the write: the crucibleProgress rule is missing (see README → Progress sync).';
  return e?.message || String(e);
}

export async function signIn() {
  try {
    await ensureFirebase();
    await fa.signInWithPopup(auth, new fa.GoogleAuthProvider());
  } catch (e) {
    set({ status: user ? state.status : 'signed-out', message: friendly(e) });
  }
}

export async function signOut() {
  if (pushTimer) pushNow();
  if (auth) await fa.signOut(auth);
}

/** Start loading the SDK early (hovering the button) so sign-in opens instantly. */
export function warmSync() { ensureFirebase().catch(() => {}); }

export function initSync() {
  store.onPersist(schedulePush);
  // Flush a pending write before the tab goes away; pick up other devices' work on return.
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden' && pushTimer) pushNow();
    else if (document.visibilityState === 'visible' && user && !pushTimer) pull();
  });
  addEventListener('pagehide', () => { if (pushTimer) pushNow(); });
  let was = false;
  try { was = localStorage.getItem(SIGNED_IN_FLAG) === '1'; } catch {}
  if (was && location.protocol !== 'file:') ensureFirebase().catch((e) => set({ status: 'error', message: friendly(e) }));
}
