#!/usr/bin/env python3
"""Build site/data/problems.json from content/*.py.

Each content module defines:
    TRACK    = dict(id, title, order, icon, blurb, intro)
    PROBLEMS = [dict(...), ...]          (see content/AUTHORING.md)

Expected outputs are computed by running each problem's Python reference
solution, so tests and solutions can never drift apart.

usage: tools/build.py [--only TRACK_ID] [--include-selftest]
"""
from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import math
import re
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
OUT = ROOT / "site" / "data" / "problems.json"

TYPE_RE = re.compile(r"^(int|float|bool|str)(\[\]){0,2}$")
DIFFS = {0: "First Steps", 1: "Easy", 2: "Medium", 3: "Hard", 4: "Expert"}
COMPARES = {"exact", "unordered", "unordered_deep"}
LANGS = {"python", "c", "cpp", "rust", "espresso", "asm"}

PRELUDE = r'''
import math, sys
from typing import *
from collections import *
from functools import *
from itertools import *
from heapq import *
from bisect import *
import re, string, random
sys.setrecursionlimit(20000)
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val; self.next = next
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val; self.left = left; self.right = right
'''


def valid_type(t: str, ret=False) -> bool:
    return t in ("list", "tree") or (ret and t == "void") or bool(TYPE_RE.match(t))


def mk_list(ns, a):
    head = None
    for v in reversed(a):
        head = ns["ListNode"](v, head)
    return head


def mk_tree(ns, a):
    if not a or a[0] is None:
        return None
    T = ns["TreeNode"]
    root = T(a[0]); q = [root]; i = 1; qi = 0
    while i < len(a):
        node = q[qi]; qi += 1
        if a[i] is not None:
            node.left = T(a[i]); q.append(node.left)
        i += 1
        if i < len(a) and a[i] is not None:
            node.right = T(a[i]); q.append(node.right)
        i += 1
    return root


def list_out(h):
    out = []
    while h is not None:
        out.append(h.val); h = h.next
        if len(out) > 100000:
            raise ValueError("cycle in output list")
    return out


def tree_out(r):
    out = []; q = [r]; qi = 0
    while qi < len(q):
        n = q[qi]; qi += 1
        if n is None:
            out.append(None)
        else:
            out.append(n.val); q.append(n.left); q.append(n.right)
    while out and out[-1] is None:
        out.pop()
    return out


def conv_in(ns, v, t):
    if t == "list":
        return mk_list(ns, v)
    if t == "tree":
        return mk_tree(ns, v)
    if t.startswith("float"):
        return [conv_in(ns, x, t[:-2]) for x in v] if t.endswith("[]") else float(v)
    return copy.deepcopy(v)


def conv_out(v, t):
    if t == "list":
        return list_out(v)
    if t == "tree":
        return tree_out(v)
    if isinstance(v, (tuple, set, frozenset, deque_type())):
        v = list(v)
    if isinstance(v, list):
        sub = t[:-2] if t.endswith("[]") else t
        return [conv_out(x, sub) for x in v]
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    if t == "int" and not isinstance(v, (int, bool)):
        raise TypeError(f"expected int result, got {type(v).__name__}")
    if t == "int" and isinstance(v, bool):
        return int(v)
    return v


def deque_type():
    from collections import deque
    return deque


def check_value(v, t, where):
    base = t.rstrip("[]")
    dims = (len(t) - len(base)) // 2
    if t in ("list",):
        assert isinstance(v, list) and all(isinstance(x, int) for x in v), f"{where}: list must be [ints]"
        return
    if t == "tree":
        assert isinstance(v, list) and all(x is None or isinstance(x, int) for x in v), f"{where}: tree must be level-order [int|None]"
        return

    def rec(x, d):
        if d == 0:
            if base == "int":
                assert isinstance(x, int) and not isinstance(x, bool), f"{where}: expected int, got {x!r}"
                assert abs(x) < 2**53, f"{where}: int {x} too large for JSON"
            elif base == "float":
                assert isinstance(x, (int, float)) and not isinstance(x, bool), f"{where}: expected float, got {x!r}"
            elif base == "bool":
                assert isinstance(x, bool), f"{where}: expected bool, got {x!r}"
            elif base == "str":
                assert isinstance(x, str), f"{where}: expected str, got {x!r}"
        else:
            assert isinstance(x, list), f"{where}: expected list for {t}, got {type(x).__name__}"
            for y in x:
                rec(y, d - 1)
    rec(v, dims)


def run_function(p, test_args):
    ns: dict = {}
    exec(PRELUDE, ns)
    exec(compile(p["solution"], f"<{p['id']}>", "exec"), ns)
    fn = ns.get(p["fn"])
    if not callable(fn):
        raise ValueError(f"solution does not define {p['fn']}()")
    types = [t for _, t in p["params"]]
    mut = p.get("mutates")
    mi = [n for n, _ in p["params"]].index(mut) if mut else -1
    args = [conv_in(ns, a, t) for a, t in zip(test_args, types)]
    with contextlib.redirect_stdout(io.StringIO()):
        r = fn(*args)
    if mi >= 0:
        return conv_out(args[mi], types[mi])
    return conv_out(r, p["returns"])


def run_io(p, stdin):
    ns: dict = {"__name__": "__main__"}
    buf = io.StringIO()
    old_in = sys.stdin
    sys.stdin = io.StringIO(stdin)
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(p["solution"], f"<{p['id']}>", "exec"), ns)
    finally:
        sys.stdin = old_in
    return buf.getvalue()


REQUIRED = ["id", "title", "difficulty", "statement", "hints", "explanation", "solution", "tests"]


def build_problem(p, track_id, errors):
    pid = p.get("id", "?")
    where = f"{track_id}/{pid}"
    for k in REQUIRED:
        if k not in p:
            errors.append(f"{where}: missing field '{k}'")
            return None
    kind = p.get("kind", "function")
    if kind not in ("function", "io", "asm"):
        errors.append(f"{where}: bad kind {kind}")
        return None
    if p["difficulty"] not in DIFFS:
        errors.append(f"{where}: difficulty must be 0-4")
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", pid):
        errors.append(f"{where}: id must be kebab-case")
    if p.get("compare", "exact") not in COMPARES:
        errors.append(f"{where}: bad compare mode")
    for lang in (p.get("langs") or []):
        if lang not in LANGS:
            errors.append(f"{where}: unknown lang {lang}")
    out = {k: v for k, v in p.items() if k not in ("tests",)}
    out["kind"] = kind
    out["track"] = track_id
    out.setdefault("tags", [])
    out.setdefault("constraints", [])
    out.setdefault("examples", min(2, len(p["tests"])))
    tests = []
    try:
        if kind in ("function", "asm"):
            for k in ("fn", "params", "returns"):
                if k not in p:
                    raise ValueError(f"missing '{k}'")
            if not re.match(r"^[a-z][a-z0-9_]*$", p["fn"]):
                raise ValueError("fn must be snake_case")
            for n, t in p["params"]:
                if not valid_type(t):
                    raise ValueError(f"bad param type {t}")
                if not re.match(r"^[a-z][a-z0-9_]*$", n):
                    raise ValueError(f"param {n} must be snake_case")
            if not valid_type(p["returns"], ret=True):
                raise ValueError(f"bad return type {p['returns']}")
            if p["returns"] == "void" and not p.get("mutates"):
                raise ValueError("void return requires 'mutates'")
            ret_t = dict(p["params"])[p["mutates"]] if p.get("mutates") else p["returns"]
            for i, args in enumerate(p["tests"]):
                if not isinstance(args, (list, tuple)) or len(args) != len(p["params"]):
                    raise ValueError(f"test {i}: expected {len(p['params'])} args, got {args!r}")
                for a, (n, t) in zip(args, p["params"]):
                    check_value(a, t, f"{where} test {i} arg {n}")
                exp = run_function(p, list(args))
                check_value(exp, ret_t, f"{where} test {i} result")
                tests.append({"args": list(args), "expected": exp})
        else:
            for i, stdin in enumerate(p["tests"]):
                if not isinstance(stdin, str):
                    raise ValueError(f"io test {i} must be a stdin string")
                tests.append({"stdin": stdin, "expected": run_io(p, stdin)})
    except Exception as e:  # noqa: BLE001
        errors.append(f"{where}: {e}\n{traceback.format_exc(limit=3)}")
        return None
    if len(tests) < 3:
        errors.append(f"{where}: needs at least 3 tests (has {len(tests)})")
    size = len(json.dumps(tests))
    if size > 120_000:
        errors.append(f"{where}: tests are {size // 1000}KB; keep under 120KB")
    out["tests"] = tests
    return out


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    global OUT
    only = None
    include_selftest = "--include-selftest" in sys.argv
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]
    errors: list[str] = []
    tracks, problems = [], []
    seen = set()
    files = sorted(CONTENT.glob("*.py"))
    for f in files:
        if f.name.startswith("_") and not (include_selftest and f.name == "_selftest.py"):
            continue
        try:
            mod = load_module(f)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{f.name}: failed to import: {e}\n{traceback.format_exc(limit=4)}")
            continue
        tr = dict(mod.TRACK)
        if only and tr["id"] != only:
            continue
        for k in ("id", "title", "order", "blurb", "intro"):
            if k not in tr:
                errors.append(f"{f.name}: TRACK missing '{k}'")
        built = []
        for p in mod.PROBLEMS:
            if p.get("id") in seen:
                errors.append(f"duplicate problem id {p.get('id')}")
                continue
            seen.add(p.get("id"))
            bp = build_problem(p, tr["id"], errors)
            if bp:
                built.append(bp)
        tr["problems"] = [p["id"] for p in built]
        tracks.append(tr)
        problems.extend(built)
    tracks.sort(key=lambda t: t["order"])
    order = {t["id"]: i for i, t in enumerate(tracks)}
    problems.sort(key=lambda p: (order[p["track"]], tracks[order[p["track"]]]["problems"].index(p["id"])))
    for i, p in enumerate(problems, 1):
        p["num"] = i
    if errors:
        print(f"\n{len(errors)} error(s):", file=sys.stderr)
        for e in errors:
            print(" -", e, file=sys.stderr)
    out = OUT
    if "--out" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--out") + 1]).resolve()
    elif only:
        print(f"[--only {only}] {len(problems)} problems OK" if not errors else "")
        sys.exit(1 if errors else 0)
    OUT = out
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = {"version": 1, "tracks": tracks, "problems": problems}
    OUT.write_text(json.dumps(data, separators=(",", ":")))
    print(f"wrote {OUT}: {len(tracks)} tracks, {len(problems)} problems, {OUT.stat().st_size // 1024} KB")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
