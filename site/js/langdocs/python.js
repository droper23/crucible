// Python 3.11 reference for Crucible's editor (hover / completion / signature help).
// Built with a tiny helper for brevity; the default export is a plain array of entries.

const P = (s) => s.split('|').map((x) => {
  const i = x.indexOf(':');
  return { label: x.slice(0, i).trim(), doc: x.slice(i + 1).trim() };
});

// e(kind, owner, name, sig, doc, extra?)  -- extra: { params, returns, example, insert, header }
function e(kind, owner, name, sig, doc, extra = {}) {
  const o = { name };
  if (owner) o.owner = owner;
  o.kind = kind;
  o.sig = sig;
  if (extra.params) o.params = typeof extra.params === 'string' ? P(extra.params) : extra.params;
  if (extra.returns) o.returns = extra.returns;
  o.doc = doc;
  if (extra.example) o.example = extra.example;
  if (extra.insert) o.insert = extra.insert;
  if (extra.header) o.header = extra.header;
  return o;
}
const K = (name, sig, doc, extra) => e('keyword', null, name, sig, doc, extra);
const B = (name, sig, doc, extra) => e('function', null, name, sig, doc, extra);
const M = (owner, name, sig, doc, extra) => e('method', owner, name, sig, doc, extra);
const F = (owner, name, sig, doc, extra = {}) =>
  e('function', owner, name, sig, doc, { header: `import ${owner.split('.')[0]}`, ...extra });

export default [
  // ===================== keywords =====================
  K('def', 'def name(params) -> T:', 'Define a function. Default values are evaluated **once** at definition time: never use a mutable default like `def f(a=[])`.', {
    example: 'def solve(nums: list[int]) -> int:\n    return sum(nums)', insert: 'def ${1:name}(${2:args}):\n\t${0:pass}' }),
  K('return', 'return [value]', 'Exit the function with *value* (or `None` if omitted). `return a, b` returns a tuple.', { example: 'def area(w, h):\n    return w * h' }),
  K('if', 'if cond: ... elif cond: ... else: ...', 'Conditional. Empty containers, `0`, `""` and `None` are falsy. Conditional expression: `a if cond else b`.', {
    insert: 'if ${1:cond}:\n\t${0:pass}', example: 'if x % 2 == 0:\n    print("even")\nelse:\n    print("odd")' }),
  K('elif', 'elif cond:', 'Else-if branch of an `if` chain.', { insert: 'elif ${1:cond}:\n\t${0:pass}', example: 'if x < 0:\n    sign = -1\nelif x == 0:\n    sign = 0' }),
  K('else', 'else:', 'Fallback branch of `if`; also allowed after `for`/`while` (runs if the loop did **not** `break`) and `try` (runs if no exception).', { insert: 'else:\n\t${0:pass}', example: 'for d in range(2, n):\n    if n % d == 0: break\nelse:\n    print("prime")' }),
  K('for', 'for x in iterable:', 'Iterate over any iterable. Use `enumerate` for indices, `zip` for parallel lists, `range` for counting. Modifying a list while iterating over it skips elements.', {
    example: 'for i, x in enumerate(nums):\n    print(i, x)', insert: 'for ${1:x} in ${2:iterable}:\n\t${0:pass}' }),
  K('while', 'while cond:', 'Loop while *cond* is truthy. `while queue:` loops until a container is empty.', { insert: 'while ${1:cond}:\n\t${0:pass}', example: 'while n > 0:\n    total += n % 10\n    n //= 10' }),
  K('break', 'break', 'Exit the innermost loop (skips the loop\'s `else`). Breaks only one level; use a flag or a function `return` for nested loops.', { example: 'for x in nums:\n    if x == target:\n        break' }),
  K('continue', 'continue', 'Skip to the next iteration of the innermost loop.', { example: 'for x in nums:\n    if x < 0:\n        continue\n    total += x' }),
  K('pass', 'pass', 'A no-op placeholder where a statement is syntactically required.', { example: 'class Empty:\n    pass' }),
  K('in', 'x in container', 'Membership test (`for` also uses it). **O(1)** average for `set`/`dict`, **O(n)** for `list`/`tuple`/`str` (substring search for `str`).', { example: 'seen = {1, 2, 3}\n2 in seen  # True\n"ell" in "hello"  # True' }),
  K('not', 'not x', 'Logical negation; `not in` and `is not` are the negated membership/identity tests.', { example: 'if not stack:\n    print("empty")\nx not in seen  # True if absent' }),
  K('and', 'a and b', 'Short-circuit AND; returns the first falsy operand or the last one (`0 and 5` → `0`).', { example: 'if 0 <= r < n and 0 <= c < m:\n    visit(r, c)' }),
  K('or', 'a or b', 'Short-circuit OR; returns the first truthy operand (`x or default`). Beware: `0 or 5` → `5`.', { example: 'name = user_input or "anonymous"' }),
  K('is', 'a is b', 'Identity test. Use only for singletons: `x is None`. Never compare numbers or strings with `is`.', { example: 'if node is None:\n    print("empty tree")' }),
  K('None', 'None', 'The null value. Functions without `return` give `None`; so do in-place methods like `list.sort()`.', { example: 'best = None\nif best is None or x < best:\n    best = x' }),
  K('True', 'True', 'Boolean true; `bool` is a subclass of `int`, so `True + True == 2`.', { example: 'found = True\nTrue + True  # 2' }),
  K('False', 'False', 'Boolean false (equals `0`).', { example: 'visited = [False] * n' }),
  K('class', 'class Name(Base):', 'Define a class. `__init__` sets up instances; `__lt__` makes objects comparable (for `heapq`/`sorted`). Use `@dataclass` for simple records.', {
    example: 'class Node:\n    def __init__(self, val, next=None):\n        self.val, self.next = val, next', insert: 'class ${1:Name}:\n\tdef __init__(self${2}):\n\t\t${0:pass}' }),
  K('lambda', 'lambda args: expr', 'Anonymous single-expression function, typically a `key=`. Gotcha: lambdas in a loop capture the variable, not its value (`lambda i=i: i` to bind).', {
    example: 'pairs.sort(key=lambda p: (p[1], -p[0]))', insert: 'lambda ${1:x}: ${0:x}' }),
  K('with', 'with expr as name:', 'Context manager: guarantees cleanup (closing files, releasing locks).', { insert: 'with ${1:expr} as ${2:name}:\n\t${0:pass}', example: 'with open("data.txt") as f:\n    lines = f.read().splitlines()' }),
  K('as', 'import x as y / except E as e / with f as v', 'Bind a name in `import`, `except` and `with`.', { example: 'import itertools as it\nfrom collections import deque as dq' }),
  K('try', 'try: ... except E as e: ... else: ... finally: ...', 'Handle exceptions. Catch specific exceptions (`except KeyError`), not bare `except:`.', {
    insert: 'try:\n\t${1:pass}\nexcept ${2:Exception} as ${3:e}:\n\t${0:pass}', example: 'try:\n    x = int(s)\nexcept ValueError:\n    x = 0' }),
  K('except', 'except ExcType as e:', 'Handler for an exception type (or tuple of types) in a `try`.', { insert: 'except ${1:Exception} as ${2:e}:\n\t${0:pass}', example: 'try:\n    v = d[key]\nexcept KeyError as e:\n    v = None' }),
  K('finally', 'finally:', 'Always runs after `try`, whether or not an exception occurred.', { insert: 'finally:\n\t${0:pass}', example: 'try:\n    result = compute()\nfinally:\n    print("done")' }),
  K('raise', 'raise Exc(msg)', 'Raise an exception; bare `raise` re-raises the current one inside `except`.', { example: 'if n < 0:\n    raise ValueError("n must be non-negative")' }),
  K('yield', 'yield value', 'Turn a function into a generator that produces values lazily. `yield from it` delegates to another iterable.', {
    example: 'def pairs(n):\n    for i in range(n):\n        yield i, i * i' }),
  K('import', 'import module [as alias]', 'Import a module. Standard library modules (`collections`, `heapq`, `math`, ...) are always available.', { example: 'import heapq\nimport math as m' }),
  K('from', 'from module import name', 'Import names directly: `from collections import Counter, deque`.', { example: 'from collections import Counter, deque' }),
  K('global', 'global name', 'Let a function assign to a module-level variable. Not needed just to read it or to mutate a global list/dict.', { example: 'count = 0\ndef inc():\n    global count\n    count += 1' }),
  K('nonlocal', 'nonlocal name', 'Let a nested function **assign** to a variable of the enclosing function (e.g. a counter in a DFS helper). Mutating a list needs no declaration.', {
    example: 'def solve():\n    best = 0\n    def dfs(i):\n        nonlocal best' }),
  K('assert', 'assert cond, msg', 'Raise `AssertionError(msg)` if *cond* is false.', { example: 'assert len(a) == len(b), "length mismatch"' }),
  K('del', 'del target', 'Delete a name, list item/slice (`del a[i]` is O(n)) or dict key (`KeyError` if missing).', { example: 'del a[0]\ndel d["key"]' }),
  K('match', 'match subject: case pattern: ...', 'Structural pattern matching (3.10+). `case _:` is the wildcard.', { insert: 'match ${1:x}:\n\tcase ${2:pattern}:\n\t\t${0:pass}', example: 'match cmd:\n    case "quit": running = False\n    case "help": show_help()\n    case _: print("unknown")' }),
  K('case', 'case pattern [if guard]:', 'One branch of a `match`. Patterns can be literals, captures (`case x:`), sequences (`case [a, b]:`), alternatives (`case 1 | 2:`) or `_`; the first matching case wins (no fall-through).', {
    example: 'match point:\n    case (0, 0): print("origin")\n    case (x, 0): print("on x-axis at", x)\n    case _: print("elsewhere")', insert: 'case ${1:pattern}:\n\t${0:pass}' }),
  K('async', 'async def f():', 'Define a coroutine (rarely needed in solutions).', { example: 'async def fetch(url):\n    return await get(url)' }),
  K('await', 'await coro', 'Wait for an awaitable inside an `async def`.', { example: 'async def main():\n    data = await fetch(url)' }),

  // ===================== builtins =====================
  B('print', 'print(*objects, sep=" ", end="\\n", file=sys.stdout, flush=False) -> None', 'Print objects separated by *sep*, followed by *end*. For many lines, build a list and `print("\\n".join(out))` — much faster.', {
    params: '*objects: values to print|sep: separator (default space)|end: terminator (default newline)|file: output stream|flush: force flush', insert: 'print(${1})', returns: 'None — writes the text to *file*', example: 'print(1, 2, 3, sep=", ")  # 1, 2, 3\nprint("no newline", end="")' }),
  B('input', 'input(prompt="") -> str', 'Read one line from stdin without the trailing newline. Raises `EOFError` at end of input. For large inputs prefer `sys.stdin.readline` or `sys.stdin.read().split()`.', {
    params: 'prompt: text written before reading', example: 'n = int(input())\nnums = list(map(int, input().split()))', returns: 'str — the line read, without the trailing newline' }),
  B('len', 'len(s) -> int', 'Number of items in a container. **O(1)**.', { params: 's: sequence or collection', insert: 'len(${1:s})', returns: 'int — number of items', example: 'len([3, 1, 2])  # 3\nlen("hello")  # 5' }),
  B('range', 'range(start, stop, step=1) -> range', 'Lazy arithmetic sequence `start, start+step, ...` up to but **excluding** *stop*. `range(n)` is `0..n-1`; count down with `range(n - 1, -1, -1)`.', {
    params: 'start: first value (default 0)|stop: exclusive end|step: increment, may be negative', insert: 'range(${1:n})', returns: 'range — lazy immutable sequence (O(1) memory; supports len, indexing, `in`)', example: 'list(range(5))  # [0, 1, 2, 3, 4]\nlist(range(10, 0, -3))  # [10, 7, 4, 1]' }),
  B('enumerate', 'enumerate(iterable, start=0) -> iterator', 'Yield `(index, item)` pairs.', { params: 'iterable: what to iterate|start: first index', example: 'for i, ch in enumerate(s):\n    ...', insert: 'enumerate(${1:iterable})', returns: 'enumerate iterator of (index, item) tuples' }),
  B('zip', 'zip(*iterables, strict=False) -> iterator', 'Yield tuples taking one item from each iterable; stops at the **shortest**. `zip(*grid)` transposes a matrix (as tuples). Use `itertools.zip_longest` to pad.', {
    params: '*iterables: iterables to combine|strict: raise if lengths differ', insert: 'zip(${1:a}, ${2:b})', returns: 'zip iterator of tuples (one-shot; wrap in list() to reuse)', example: 'list(zip([1, 2, 3], "ab"))  # [(1, \'a\'), (2, \'b\')]\ncols = list(zip(*grid))  # transpose' }),
  B('sorted', 'sorted(iterable, key=None, reverse=False) -> list', 'Return a **new** sorted list (stable, **O(n log n)**). Sort by several fields with a tuple key, e.g. `key=lambda x: (-x[1], x[0])`.', {
    params: 'iterable: items to sort|key: function computing the sort key|reverse: descending if True', insert: 'sorted(${1:iterable})', returns: 'list — a new sorted list; the input is unchanged', example: 'sorted([3, 1, 2])  # [1, 2, 3]\nsorted(words, key=len, reverse=True)' }),
  B('reversed', 'reversed(seq) -> iterator', 'Reverse iterator over a sequence (no copy). Wrap in `list(...)` to materialize, or use `seq[::-1]`.', { params: 'seq: sequence (list, str, range, ...)', returns: 'iterator over the items in reverse order (one-shot)', example: 'list(reversed([1, 2, 3]))  # [3, 2, 1]\nfor i in reversed(range(n)):\n    ...' }),
  B('sum', 'sum(iterable, start=0) -> number', 'Add up the items. Don\'t use it to join strings (use `"".join`).', { params: 'iterable: numbers|start: initial value', returns: 'number — *start* plus the sum of the items', example: 'sum([1, 2, 3])  # 6\nsum(x * x for x in nums)' }),
  B('min', 'min(iterable, *, key=None, default=...) / min(a, b, ...)', 'Smallest item. Raises `ValueError` on an empty iterable unless *default* is given.', {
    params: 'iterable: items to compare|key: function computing comparison key|default: returned when empty|a, b, ...: two or more values (second form)', returns: 'the smallest item (the first one if several are equal)', example: 'min([4, 2, 8])  # 2\nmin(3, 7)  # 3\nmin(words, key=len)\nmin([], default=0)  # 0' }),
  B('max', 'max(iterable, *, key=None, default=...) / max(a, b, ...)', 'Largest item; `max(d, key=d.get)` is the key with the largest value. Raises `ValueError` on empty input unless *default* is given.', {
    params: 'iterable: items to compare|key: function computing comparison key|default: returned when empty|a, b, ...: two or more values (second form)', returns: 'the largest item (the first one if several are equal)', example: 'max([4, 2, 8])  # 8\nmax(d, key=d.get)  # key with the largest value\nmax([], default=-1)  # -1' }),
  B('abs', 'abs(x) -> number', 'Absolute value.', { params: 'x: number', returns: 'number — the magnitude (a float for complex input)', example: 'abs(-7)  # 7\ndist = abs(x1 - x2) + abs(y1 - y2)  # Manhattan' }),
  B('map', 'map(function, iterable, ...) -> iterator', 'Apply *function* to each item lazily. `list(map(int, input().split()))` parses a line of ints.', {
    params: 'function: function to apply|iterable: input items', returns: 'map iterator (lazy, one-shot)', example: 'nums = list(map(int, "1 2 3".split()))  # [1, 2, 3]' }),
  B('filter', 'filter(function, iterable) -> iterator', 'Lazily keep items for which *function* returns truthy (`None` keeps truthy items).', { params: 'function: predicate or None|iterable: input items', returns: 'filter iterator (lazy, one-shot)', example: 'list(filter(lambda x: x % 2 == 0, range(6)))  # [0, 2, 4]' }),
  B('any', 'any(iterable) -> bool', 'True if any item is truthy (short-circuits); `False` for empty.', { params: 'iterable: items to test', returns: 'bool — True if at least one item is truthy', example: 'any(x < 0 for x in [3, -1, 2])  # True\nany([])  # False' }),
  B('all', 'all(iterable) -> bool', 'True if every item is truthy (short-circuits); `True` for empty.', { params: 'iterable: items to test', returns: 'bool — True if no item is falsy (True for empty input)', example: 'all(c.isdigit() for c in "123")  # True\nall([])  # True' }),
  B('int', 'int(x=0, base=10) -> int', 'Convert to integer; truncates floats toward zero. `int("ff", 16)` parses other bases. Python ints are arbitrary precision (no overflow).', {
    params: 'x: number or string|base: base for string input', returns: 'int — converted value; ValueError for an invalid string', example: 'int("42")  # 42\nint(-3.7)  # -3\nint("ff", 16)  # 255' }),
  B('float', 'float(x=0.0) -> float', 'Convert to a 64-bit float. `float("inf")` is infinity. Floats are inexact: compare with tolerance.', { params: 'x: number or string', returns: 'float — converted value; ValueError for an invalid string', example: 'float("3.5")  # 3.5\nbest = float("inf")' }),
  B('str', 'str(object="") -> str', 'String representation. Strings are **immutable**; build with a list and `"".join`.', { params: 'object: value to convert', returns: 'str — the printable form of *object*', example: 'str(42)  # \'42\'\n"".join(str(d) for d in [1, 2, 3])  # \'123\'' }),
  B('list', 'list(iterable=()) -> list', 'New list from an iterable. Gotcha: `[[0] * m] * n` shares one row n times; use `[[0] * m for _ in range(n)]`.', { params: 'iterable: items', returns: 'list — a new list (shallow copy of the items)', example: 'list("abc")  # [\'a\', \'b\', \'c\']\ngrid = [[0] * m for _ in range(n)]' }),
  B('dict', 'dict(mapping_or_iterable=(), **kwargs) -> dict', 'New dict. Preserves insertion order. `dict(zip(keys, values))` pairs two lists.', { params: 'mapping_or_iterable: initial key/value pairs|**kwargs: extra keys', returns: 'dict — a new dictionary', example: 'dict(zip("ab", [1, 2]))  # {\'a\': 1, \'b\': 2}\ndict(x=1, y=2)  # {\'x\': 1, \'y\': 2}' }),
  B('set', 'set(iterable=()) -> set', 'New mutable set (hash set: **O(1)** average add/lookup). `{}` is an empty **dict**, not a set: use `set()`.', { params: 'iterable: items', returns: 'set — a new set (duplicates removed)', example: 'set([1, 2, 2, 3])  # {1, 2, 3}\nseen = set()' }),
  B('frozenset', 'frozenset(iterable=()) -> frozenset', 'Immutable, hashable set: usable as a dict key or set element.', { params: 'iterable: items', returns: 'frozenset — a new immutable set', example: 'key = frozenset(["a", "b"])\ngroups = {key: 1}' }),
  B('tuple', 'tuple(iterable=()) -> tuple', 'Immutable sequence; hashable if its items are, so usable as dict keys (e.g. `(r, c)`). One-element tuple needs a comma: `(x,)`.', { params: 'iterable: items', returns: 'tuple — a new immutable sequence', example: 'tuple([1, 2])  # (1, 2)\nseen.add(tuple(state))' }),
  B('bool', 'bool(x=False) -> bool', 'Truth value of *x*.', { params: 'x: any value', returns: 'bool — True if *x* is truthy', example: 'bool([])  # False\nbool("0")  # True (non-empty string)' }),
  B('ord', 'ord(c) -> int', 'Unicode code point of a one-character string: `ord("a") == 97`. `ord(c) - ord("a")` gives a letter index.', { params: 'c: single character', returns: 'int — the Unicode code point', example: 'ord("a")  # 97\nidx = ord(ch) - ord("a")' }),
  B('chr', 'chr(i) -> str', 'Character for a code point: `chr(97) == "a"`.', { params: 'i: code point', returns: 'str — a one-character string', example: 'chr(97)  # \'a\'\nchr(ord("a") + 2)  # \'c\'' }),
  B('divmod', 'divmod(a, b) -> (q, r)', 'Return `(a // b, a % b)`. Floor division: `divmod(-7, 2) == (-4, 1)`.', { params: 'a: dividend|b: divisor', returns: 'tuple (a // b, a % b)', example: 'q, r = divmod(17, 5)  # 3, 2\nh, m = divmod(minutes, 60)' }),
  B('pow', 'pow(base, exp, mod=None) -> int', 'Power; with *mod* it does fast modular exponentiation (**O(log exp)**). `pow(a, -1, m)` is the modular inverse.', {
    params: 'base: base|exp: exponent|mod: optional modulus', returns: 'int (or float for a negative *exp* without *mod*) — base ** exp, reduced modulo *mod* if given', example: 'pow(2, 10)  # 1024\npow(3, 200, 10**9 + 7)\npow(3, -1, 7)  # 5, since 3 * 5 % 7 == 1' }),
  B('round', 'round(number, ndigits=None) -> int | float', 'Round to *ndigits*. Gotcha: uses banker\'s rounding (`round(2.5) == 2`).', { params: 'number: value|ndigits: digits after the point', returns: 'int if *ndigits* is omitted, otherwise a float', example: 'round(3.14159, 2)  # 3.14\nround(2.5)  # 2 (banker\'s rounding)' }),
  B('isinstance', 'isinstance(obj, classinfo) -> bool', 'Whether *obj* is an instance of a class (or of any class in a tuple).', { params: 'obj: value|classinfo: type or tuple of types', returns: 'bool', example: 'isinstance(5, int)  # True\nisinstance(x, (list, tuple))' }),
  B('type', 'type(obj) -> type', 'The type of *obj*.', { params: 'obj: value', returns: 'type — the class of *obj*', example: 'type(3)  # <class \'int\'>\ntype(x) is list' }),
  B('hash', 'hash(obj) -> int', 'Hash of a hashable object. Lists, dicts and sets are unhashable (use tuples / frozensets).', { params: 'obj: hashable value', returns: 'int — hash value (equal objects hash equal); TypeError if unhashable', example: 'hash((1, 2))  # works: tuples are hashable\nhash([1, 2])  # TypeError: unhashable type: \'list\'' }),
  B('id', 'id(obj) -> int', 'Unique identity of an object during its lifetime.', { params: 'obj: any value', returns: 'int — identity, unique among live objects', example: 'a = b = []\nid(a) == id(b)  # True (same object)' }),
  B('iter', 'iter(obj) -> iterator', 'Get an iterator; pair with `next`.', { params: 'obj: iterable', returns: 'iterator over *obj*', example: 'it = iter([1, 2, 3])\nnext(it)  # 1' }),
  B('next', 'next(iterator, default) -> item', 'Next item from an iterator; raises `StopIteration` when exhausted unless *default* is given. `next((x for x in a if p(x)), None)` finds the first match.', {
    params: 'iterator: iterator|default: returned when exhausted', returns: 'the next item, or *default* if the iterator is exhausted', example: 'it = iter([1, 2])\nnext(it)  # 1\nnext((x for x in nums if x > 10), None)' }),
  B('bin', 'bin(x) -> str', 'Binary string with `0b` prefix: `bin(5) == "0b101"`. Count set bits with `x.bit_count()`.', { params: 'x: integer', returns: 'str — binary digits with a \'0b\' prefix (and \'-\' for negatives)', example: 'bin(5)  # \'0b101\'\nbin(5)[2:].zfill(8)  # \'00000101\'' }),
  B('hex', 'hex(x) -> str', 'Hex string with `0x` prefix.', { params: 'x: integer', returns: 'str — lowercase hex digits with a \'0x\' prefix', example: 'hex(255)  # \'0xff\'' }),
  B('oct', 'oct(x) -> str', 'Octal string with `0o` prefix.', { params: 'x: integer', returns: 'str — octal digits with a \'0o\' prefix', example: 'oct(8)  # \'0o10\'' }),
  B('format', 'format(value, format_spec="") -> str', 'Format one value: `format(x, ".2f")`, `format(n, "b")`, `format(n, "08b")`. f-strings use the same specs: `f"{x:.2f}"`.', {
    params: 'value: value to format|format_spec: format mini-language spec', returns: 'str — the formatted value', example: 'format(3.14159, ".2f")  # \'3.14\'\nformat(5, "08b")  # \'00000101\'' }),
  B('repr', 'repr(obj) -> str', 'Unambiguous representation (strings get quotes).', { params: 'obj: any value', returns: 'str — developer-oriented representation', example: 'repr("hi")  # "\'hi\'"\nprint(repr(line))  # reveals hidden whitespace like \'\\n\'' }),
  B('slice', 'slice(start, stop, step=None) -> slice', 'Slice object, as used by `a[start:stop:step]`.', { params: 'start: start index|stop: end index (exclusive)|step: step', returns: 'slice object', example: 'mid = slice(1, -1)\n"hello"[mid]  # \'ell\'' }),
  B('getattr', 'getattr(obj, name, default) -> value', 'Attribute by name, with optional default.', { params: 'obj: object|name: attribute name|default: fallback', returns: 'the attribute value, or *default*; AttributeError if missing and no default', example: 'getattr(obj, "name", None)' }),
  B('setattr', 'setattr(obj, name, value) -> None', 'Set an attribute by name.', { params: 'obj: object|name: attribute name|value: new value', returns: 'None', example: 'setattr(obj, "count", 0)  # same as obj.count = 0' }),
  B('hasattr', 'hasattr(obj, name) -> bool', 'Whether *obj* has attribute *name*.', { params: 'obj: object|name: attribute name', returns: 'bool', example: 'if hasattr(node, "left"):\n    ...' }),
  B('callable', 'callable(obj) -> bool', 'Whether *obj* can be called.', { params: 'obj: any value', returns: 'bool', example: 'callable(print)  # True\ncallable(42)  # False' }),
  B('open', 'open(file, mode="r") -> file', 'Open a file (rarely needed: use stdin).', { params: 'file: path|mode: "r", "w", ...', returns: 'file object — text mode reads/writes str, "b" modes use bytes', example: 'with open("input.txt") as f:\n    lines = f.read().splitlines()' }),
  B('super', 'super() -> proxy', 'Access the parent class implementation, e.g. `super().__init__()`.', { returns: 'proxy object that delegates method calls to the parent class', example: 'class Child(Base):\n    def __init__(self):\n        super().__init__()' }),
  B('object', 'object()', 'Base of all classes; `object()` makes a unique sentinel.', { returns: 'object — a new featureless instance', example: 'MISSING = object()\nif d.get(key, MISSING) is MISSING:\n    ...' }),
  e('type', null, 'complex', 'complex(real=0, imag=0)', 'Complex number; handy for 2D grid coordinates (`1j` rotates by 90°).', { params: 'real: real part|imag: imaginary part', example: 'z = complex(3, 4)  # (3+4j)\nabs(z)  # 5.0\nz * 1j  # rotate 90°: (-4+3j)' }),
  e('constant', null, 'Ellipsis', '...', 'The `...` singleton; also a placeholder body.', { example: 'def todo():\n    ...' }),
  e('constant', null, '__name__', '__name__', 'Module name; `"__main__"` when run as a script.', { insert: '__name__', example: 'if __name__ == "__main__":\n    main()' }),
  e('type', null, 'Exception', 'Exception(msg)', 'Base class for errors; common subclasses: `ValueError`, `KeyError`, `IndexError`, `TypeError`, `ZeroDivisionError`, `RecursionError`.', { params: 'msg: error message', example: 'class InvalidMove(Exception):\n    pass\nraise ValueError("bad input")' }),

  // ===================== str methods =====================
  M('str', 'split', 'str.split(sep=None, maxsplit=-1) -> list[str]', 'Split into a list. With no *sep*, splits on runs of whitespace and drops empties; `"a,,b".split(",")` keeps the empty string.', {
    params: 'sep: delimiter (None = whitespace)|maxsplit: max number of splits', insert: 'split(${1})', returns: 'list[str]', example: '"a b  c".split()  # [\'a\', \'b\', \'c\']\n"1,2,,3".split(",")  # [\'1\', \'2\', \'\', \'3\']' }),
  M('str', 'join', 'str.join(iterable) -> str', 'Concatenate strings with this string as separator: `" ".join(map(str, nums))`. **O(total length)**; items must be strings.', {
    params: 'iterable: strings to join', insert: 'join(${1:iterable})', returns: 'str — the items joined by this string; TypeError if any item is not a str', example: '" ".join(["a", "b"])  # \'a b\'\nprint("\\n".join(map(str, nums)))' }),
  M('str', 'strip', 'str.strip(chars=None) -> str', 'Remove leading and trailing whitespace (or *chars*).', { params: 'chars: set of characters to remove', returns: 'str — a stripped copy', example: '"  hi\\n".strip()  # \'hi\'\n"xxhixx".strip("x")  # \'hi\'' }),
  M('str', 'lstrip', 'str.lstrip(chars=None) -> str', 'Remove leading whitespace (or *chars*).', { params: 'chars: set of characters to remove', returns: 'str — a stripped copy', example: '"007".lstrip("0")  # \'7\'' }),
  M('str', 'rstrip', 'str.rstrip(chars=None) -> str', 'Remove trailing whitespace (or *chars*), e.g. the newline from `sys.stdin.readline()`.', { params: 'chars: set of characters to remove', returns: 'str — a stripped copy', example: '"hello\\n".rstrip()  # \'hello\'' }),
  M('str', 'replace', 'str.replace(old, new, count=-1) -> str', 'Return a copy with *old* replaced by *new*.', { params: 'old: substring to find|new: replacement|count: max replacements', returns: 'str — a new string with the replacements', example: '"a-b-c".replace("-", "")  # \'abc\'\n"aaa".replace("a", "b", 2)  # \'bba\'' }),
  M('str', 'find', 'str.find(sub, start=0, end=len) -> int', 'Lowest index of *sub*, or **-1** if absent. **O(n·m)** worst case.', { params: 'sub: substring|start: search start|end: search end', returns: 'int — lowest index of *sub*, or -1 if absent', example: '"hello".find("l")  # 2\n"hello".find("z")  # -1' }),
  M('str', 'rfind', 'str.rfind(sub, start=0, end=len) -> int', 'Highest index of *sub*, or -1.', { params: 'sub: substring|start: search start|end: search end', returns: 'int — highest index of *sub*, or -1 if absent', example: '"hello".rfind("l")  # 3' }),
  M('str', 'index', 'str.index(sub, start=0, end=len) -> int', 'Like `find` but raises `ValueError` when absent.', { params: 'sub: substring|start: search start|end: search end', returns: 'int — lowest index of *sub*; raises ValueError if absent', example: '"hello".index("e")  # 1' }),
  M('str', 'count', 'str.count(sub, start=0, end=len) -> int', 'Number of non-overlapping occurrences of *sub*.', { params: 'sub: substring|start: search start|end: search end', returns: 'int — number of non-overlapping occurrences', example: '"banana".count("a")  # 3\n"aaaa".count("aa")  # 2 (non-overlapping)' }),
  M('str', 'startswith', 'str.startswith(prefix, start=0) -> bool', 'Whether the string starts with *prefix* (or any prefix in a tuple).', { params: 'prefix: string or tuple|start: position to test', returns: 'bool', example: '"prefix_x".startswith("pre")  # True\nname.startswith(("a", "b"))' }),
  M('str', 'endswith', 'str.endswith(suffix) -> bool', 'Whether the string ends with *suffix* (or any in a tuple).', { params: 'suffix: string or tuple', returns: 'bool', example: '"main.py".endswith(".py")  # True' }),
  M('str', 'lower', 'str.lower() -> str', 'Lowercase copy.', { returns: 'str — a lowercase copy', example: '"HeLLo".lower()  # \'hello\'' }),
  M('str', 'upper', 'str.upper() -> str', 'Uppercase copy.', { returns: 'str — an uppercase copy', example: '"abc".upper()  # \'ABC\'' }),
  M('str', 'capitalize', 'str.capitalize() -> str', 'First character uppercase, the rest lowercase.', { returns: 'str — a capitalized copy', example: '"hELLO world".capitalize()  # \'Hello world\'' }),
  M('str', 'title', 'str.title() -> str', 'Titlecase copy.', { returns: 'str — a titlecased copy', example: '"hello world".title()  # \'Hello World\'' }),
  M('str', 'swapcase', 'str.swapcase() -> str', 'Swap upper/lower case.', { returns: 'str — a case-swapped copy', example: '"aBc".swapcase()  # \'AbC\'' }),
  M('str', 'isdigit', 'str.isdigit() -> bool', 'True if non-empty and all characters are digits.', { returns: 'bool', example: '"123".isdigit()  # True\n"-1".isdigit()  # False' }),
  M('str', 'isalpha', 'str.isalpha() -> bool', 'True if non-empty and all characters are letters.', { returns: 'bool', example: '"abc".isalpha()  # True\n"ab1".isalpha()  # False' }),
  M('str', 'isalnum', 'str.isalnum() -> bool', 'True if non-empty and all characters are letters or digits.', { returns: 'bool', example: '"ab12".isalnum()  # True\n"a b".isalnum()  # False' }),
  M('str', 'isspace', 'str.isspace() -> bool', 'True if non-empty and all whitespace.', { returns: 'bool', example: '" \\t\\n".isspace()  # True\n"".isspace()  # False' }),
  M('str', 'islower', 'str.islower() -> bool', 'True if it has cased characters and all are lowercase.', { returns: 'bool', example: '"abc1".islower()  # True' }),
  M('str', 'isupper', 'str.isupper() -> bool', 'True if it has cased characters and all are uppercase.', { returns: 'bool', example: '"ABC".isupper()  # True' }),
  M('str', 'zfill', 'str.zfill(width) -> str', 'Pad with zeros on the left: `"7".zfill(3) == "007"`.', { params: 'width: final length', returns: 'str — a zero-padded copy (sign kept in front)', example: '"42".zfill(5)  # \'00042\'\n"-7".zfill(3)  # \'-07\'' }),
  M('str', 'center', 'str.center(width, fillchar=" ") -> str', 'Center in a field of *width*.', { params: 'width: final length|fillchar: padding character', returns: 'str — a padded copy', example: '"hi".center(6, "*")  # \'**hi**\'' }),
  M('str', 'ljust', 'str.ljust(width, fillchar=" ") -> str', 'Left-justify in a field of *width*.', { params: 'width: final length|fillchar: padding character', returns: 'str — a padded copy', example: '"ab".ljust(4, ".")  # \'ab..\'' }),
  M('str', 'rjust', 'str.rjust(width, fillchar=" ") -> str', 'Right-justify in a field of *width*.', { params: 'width: final length|fillchar: padding character', returns: 'str — a padded copy', example: '"7".rjust(3)  # \'  7\'' }),
  M('str', 'partition', 'str.partition(sep) -> (head, sep, tail)', 'Split at the first *sep* into a 3-tuple.', { params: 'sep: separator', returns: 'tuple (head, sep, tail); (s, \'\', \'\') if *sep* is absent', example: '"a=1".partition("=")  # (\'a\', \'=\', \'1\')' }),
  M('str', 'splitlines', 'str.splitlines(keepends=False) -> list[str]', 'Split on line boundaries.', { params: 'keepends: keep the newline characters', returns: 'list[str]', example: '"a\\nb\\r\\nc".splitlines()  # [\'a\', \'b\', \'c\']' }),
  M('str', 'format', 'str.format(*args, **kwargs) -> str', 'Fill `{}` placeholders; f-strings (`f"{x}"`) are usually simpler.', { params: '*args: positional values|**kwargs: named values', returns: 'str — the formatted string', example: '"{} + {} = {}".format(1, 2, 3)  # \'1 + 2 = 3\'\n"{name}!".format(name="hi")  # \'hi!\'' }),
  M('str', 'encode', 'str.encode(encoding="utf-8") -> bytes', 'Encode to bytes.', { params: 'encoding: codec name', returns: 'bytes', example: '"hé".encode()  # b\'h\\xc3\\xa9\'' }),
  M('str', 'removeprefix', 'str.removeprefix(prefix) -> str', 'Remove *prefix* if present (3.9+).', { params: 'prefix: prefix to remove', returns: 'str — a copy without the prefix (unchanged if absent)', example: '"test_case".removeprefix("test_")  # \'case\'' }),
  M('str', 'removesuffix', 'str.removesuffix(suffix) -> str', 'Remove *suffix* if present (3.9+).', { params: 'suffix: suffix to remove', returns: 'str — a copy without the suffix (unchanged if absent)', example: '"file.py".removesuffix(".py")  # \'file\'' }),
  M('str', 'maketrans', 'str.maketrans(x, y) -> dict', 'Build a translation table for `translate`.', { params: 'x: characters to map|y: replacement characters', returns: 'dict mapping code points to replacement code points', example: 'table = str.maketrans("abc", "xyz")\n"aabbcc".translate(table)  # \'xxyyzz\'' }),
  M('str', 'translate', 'str.translate(table) -> str', 'Map characters through a table from `str.maketrans`.', { params: 'table: translation table', returns: 'str — the translated copy', example: 'table = str.maketrans("01", "10")\n"0110".translate(table)  # \'1001\'' }),

  // ===================== list methods =====================
  M('list', 'append', 'list.append(x) -> None', 'Add *x* at the end. **Amortized O(1)**. Returns None: don\'t write `a = a.append(x)`.', { params: 'x: item to add', insert: 'append(${1:x})', returns: 'None — modifies the list in place', example: 'stack = []\nstack.append(3)  # stack == [3]' }),
  M('list', 'extend', 'list.extend(iterable) -> None', 'Append every item of *iterable*.', { params: 'iterable: items to add', returns: 'None — modifies the list in place', example: 'a = [1]\na.extend([2, 3])  # a == [1, 2, 3]' }),
  M('list', 'insert', 'list.insert(i, x) -> None', 'Insert *x* before index *i*. **O(n)**; for queues use `collections.deque`.', { params: 'i: index|x: item', returns: 'None — modifies the list in place', example: 'a = [1, 3]\na.insert(1, 2)  # a == [1, 2, 3]' }),
  M('list', 'pop', 'list.pop(i=-1) -> item', 'Remove and return the item at *i* (default last). `pop()` is O(1); **`pop(0)` is O(n)**: use `deque.popleft()`.', { params: 'i: index (default last)', returns: 'the removed item; IndexError if empty or out of range', example: 'stack = [1, 2, 3]\nstack.pop()  # 3\nstack.pop(0)  # 1' }),
  M('list', 'remove', 'list.remove(x) -> None', 'Remove the first item equal to *x*; **O(n)**; `ValueError` if absent.', { params: 'x: value to remove', returns: 'None; raises ValueError if *x* is absent', example: 'a = [3, 1, 3]\na.remove(3)  # a == [1, 3]' }),
  M('list', 'index', 'list.index(x, start=0, end=len) -> int', 'Index of the first item equal to *x*; **O(n)**; `ValueError` if absent.', { params: 'x: value|start: search start|end: search end', returns: 'int — index of the first occurrence; raises ValueError if absent', example: '[5, 7, 5].index(5)  # 0' }),
  M('list', 'count', 'list.count(x) -> int', 'Number of items equal to *x*; **O(n)**.', { params: 'x: value', returns: 'int — number of equal items', example: '[1, 2, 1].count(1)  # 2' }),
  M('list', 'sort', 'list.sort(*, key=None, reverse=False) -> None', 'Sort **in place** (stable, O(n log n)) and return **None** — `a = a.sort()` loses the list; use `sorted(a)` for a copy.', {
    params: 'key: function computing the sort key|reverse: descending if True', returns: 'None — sorts in place', example: 'a = [3, 1, 2]\na.sort()  # a == [1, 2, 3]\npeople.sort(key=lambda p: p.age)' }),
  M('list', 'reverse', 'list.reverse() -> None', 'Reverse in place; returns None. `a[::-1]` makes a reversed copy.', { returns: 'None — reverses in place', example: 'a = [1, 2, 3]\na.reverse()  # a == [3, 2, 1]' }),
  M('list', 'copy', 'list.copy() -> list', 'Shallow copy (same as `a[:]`). Nested lists are still shared; use `[row[:] for row in grid]`.', { returns: 'list — a new shallow copy', example: 'b = a.copy()\nb.append(0)  # a is unchanged' }),
  M('list', 'clear', 'list.clear() -> None', 'Remove all items.', { returns: 'None', example: 'a.clear()  # a == []' }),

  // ===================== dict methods =====================
  M('dict', 'get', 'dict.get(key, default=None) -> value', 'Value for *key*, or *default* if missing (no `KeyError`, no insertion). `d[k] = d.get(k, 0) + 1` counts.', {
    params: 'key: key to look up|default: returned if missing', insert: 'get(${1:key}, ${2:0})', returns: 'the value for *key*, or *default* (None if omitted)', example: 'd = {"a": 1}\nd.get("a")  # 1\nd.get("b", 0)  # 0' }),
  M('dict', 'keys', 'dict.keys() -> dict_keys', 'Live view of the keys (insertion order).', { returns: 'dict_keys — set-like live view', example: 'd = {"a": 1, "b": 2}\nlist(d.keys())  # [\'a\', \'b\']' }),
  M('dict', 'values', 'dict.values() -> dict_values', 'Live view of the values.', { returns: 'dict_values — live view', example: 'scores = {"ann": 3, "bob": 5}\nmax(scores.values())  # 5' }),
  M('dict', 'items', 'dict.items() -> dict_items', 'Live view of `(key, value)` pairs: `for k, v in d.items():`. Don\'t add/remove keys while iterating.', { returns: 'dict_items — live view of (key, value) tuples', example: 'for name, score in scores.items():\n    print(name, score)' }),
  M('dict', 'setdefault', 'dict.setdefault(key, default=None) -> value', 'Return `d[key]`, inserting *default* first if missing: `d.setdefault(k, []).append(v)`.', { params: 'key: key|default: value inserted if missing', returns: 'the existing value, or *default* after inserting it', example: 'groups = {}\ngroups.setdefault(key, []).append(word)' }),
  M('dict', 'pop', 'dict.pop(key, default) -> value', 'Remove *key* and return its value; `KeyError` if missing and no *default*.', { params: 'key: key to remove|default: returned if missing', returns: 'the removed value, or *default*; KeyError if missing and no default', example: 'd = {"a": 1}\nd.pop("a")  # 1\nd.pop("z", None)  # None' }),
  M('dict', 'popitem', 'dict.popitem() -> (key, value)', 'Remove and return the **last** inserted pair (LIFO).', { returns: 'tuple (key, value) of the last inserted pair; KeyError if empty', example: 'd = {"a": 1, "b": 2}\nd.popitem()  # (\'b\', 2)' }),
  M('dict', 'update', 'dict.update(other) -> None', 'Merge keys from *other* (dict or pairs), overwriting. `d1 | d2` makes a merged copy.', { params: 'other: mapping or iterable of pairs', returns: 'None — modifies the dict in place', example: 'd = {"a": 1}\nd.update({"a": 5, "b": 2})  # d == {\'a\': 5, \'b\': 2}' }),
  M('dict', 'fromkeys', 'dict.fromkeys(iterable, value=None) -> dict', 'New dict with every key mapped to *value*. Gotcha: a mutable *value* is shared by all keys.', { params: 'iterable: keys|value: shared value', returns: 'dict — a new dictionary', example: 'dict.fromkeys("abc", 0)  # {\'a\': 0, \'b\': 0, \'c\': 0}' }),
  M('dict', 'copy', 'dict.copy() -> dict', 'Shallow copy.', { returns: 'dict — a new shallow copy', example: 'snapshot = d.copy()' }),
  M('dict', 'clear', 'dict.clear() -> None', 'Remove all items.', { returns: 'None', example: 'd.clear()  # d == {}' }),

  // ===================== set methods =====================
  M('set', 'add', 'set.add(x) -> None', 'Add *x*. **O(1)** average.', { params: 'x: hashable item', returns: 'None', example: 'seen = set()\nseen.add((r, c))' }),
  M('set', 'remove', 'set.remove(x) -> None', 'Remove *x*; raises `KeyError` if absent (use `discard` to ignore).', { params: 'x: item', returns: 'None; raises KeyError if *x* is absent', example: 's = {1, 2}\ns.remove(1)  # s == {2}' }),
  M('set', 'discard', 'set.discard(x) -> None', 'Remove *x* if present; no error otherwise.', { params: 'x: item', returns: 'None', example: 's = {1, 2}\ns.discard(5)  # no error' }),
  M('set', 'pop', 'set.pop() -> item', 'Remove and return an arbitrary item; `KeyError` if empty.', { returns: 'an arbitrary removed item; KeyError if empty', example: 's = {3}\ns.pop()  # 3' }),
  M('set', 'union', 'set.union(*others) -> set', 'New set with items from all sets (`a | b`).', { params: '*others: iterables', returns: 'set — a new set', example: '{1, 2}.union([2, 3])  # {1, 2, 3}' }),
  M('set', 'intersection', 'set.intersection(*others) -> set', 'Items common to all (`a & b`).', { params: '*others: iterables', returns: 'set — a new set', example: '{1, 2, 3}.intersection({2, 3, 4})  # {2, 3}' }),
  M('set', 'difference', 'set.difference(*others) -> set', 'Items in this set but not the others (`a - b`).', { params: '*others: iterables', returns: 'set — a new set', example: '{1, 2, 3}.difference({2})  # {1, 3}' }),
  M('set', 'symmetric_difference', 'set.symmetric_difference(other) -> set', 'Items in exactly one of the sets (`a ^ b`).', { params: 'other: iterable', returns: 'set — a new set', example: '{1, 2}.symmetric_difference({2, 3})  # {1, 3}' }),
  M('set', 'issubset', 'set.issubset(other) -> bool', 'Whether every item is in *other* (`a <= b`).', { params: 'other: iterable', returns: 'bool', example: '{1, 2}.issubset({1, 2, 3})  # True' }),
  M('set', 'issuperset', 'set.issuperset(other) -> bool', 'Whether *other* is contained in this set (`a >= b`).', { params: 'other: iterable', returns: 'bool', example: '{1, 2, 3}.issuperset([1, 3])  # True' }),
  M('set', 'isdisjoint', 'set.isdisjoint(other) -> bool', 'True if there are no common items.', { params: 'other: iterable', returns: 'bool', example: '{1, 2}.isdisjoint({3})  # True' }),
  M('set', 'update', 'set.update(*others) -> None', 'Add all items from *others* (`a |= b`).', { params: '*others: iterables', returns: 'None — modifies the set in place', example: 's = {1}\ns.update([2, 3], {4})  # s == {1, 2, 3, 4}' }),
  M('set', 'intersection_update', 'set.intersection_update(*others) -> None', 'Keep only items also in *others* (`a &= b`).', { params: '*others: iterables', returns: 'None — modifies the set in place', example: 's = {1, 2, 3}\ns.intersection_update({2, 3, 4})  # s == {2, 3}' }),
  M('set', 'difference_update', 'set.difference_update(*others) -> None', 'Remove items found in *others* (`a -= b`).', { params: '*others: iterables', returns: 'None — modifies the set in place', example: 's = {1, 2, 3}\ns.difference_update({1})  # s == {2, 3}' }),
  M('set', 'copy', 'set.copy() -> set', 'Shallow copy.', { returns: 'set — a new shallow copy', example: 'backup = s.copy()' }),
  M('set', 'clear', 'set.clear() -> None', 'Remove all items.', { returns: 'None', example: 's.clear()  # s == set()' }),

  // ===================== int methods =====================
  M('int', 'bit_count', 'int.bit_count() -> int', 'Number of 1 bits (popcount) of `abs(n)` (3.10+).', { returns: 'int — number of 1 bits', example: '(13).bit_count()  # 3 (0b1101)' }),
  M('int', 'bit_length', 'int.bit_length() -> int', 'Bits needed to represent `abs(n)`: `(8).bit_length() == 4`; `n.bit_length() - 1` is floor(log2 n).', { returns: 'int — bits needed for abs(n); 0 for 0', example: '(8).bit_length()  # 4\n(0).bit_length()  # 0' }),

  // ===================== collections =====================
  F('collections', 'Counter', 'Counter(iterable_or_mapping=None) -> Counter', 'Dict subclass counting hashable items; missing keys read as **0** (no KeyError). Counters support `+`, `-`, `&`, `|` and `==`.', {
    params: 'iterable_or_mapping: items to count', example: 'from collections import Counter\nc = Counter("banana")\nc["a"]  # 3', header: 'from collections import Counter', returns: 'Counter — a dict of item → count' }),
  M('Counter', 'most_common', 'Counter.most_common(n=None) -> list[tuple]', 'The *n* most frequent `(item, count)` pairs, highest first (ties in insertion order). **O(n log k)** with *n*.', {
    params: 'n: how many (None = all)', header: 'from collections import Counter', returns: 'list of (item, count) tuples, most frequent first', example: 'Counter("abracadabra").most_common(2)  # [(\'a\', 5), (\'b\', 2)]' }),
  M('Counter', 'elements', 'Counter.elements() -> iterator', 'Iterate over items, each repeated as many times as its count (counts ≤ 0 skipped).', { header: 'from collections import Counter', returns: 'iterator over items, each repeated count times', example: 'sorted(Counter(a=2, b=1).elements())  # [\'a\', \'a\', \'b\']' }),
  M('Counter', 'update', 'Counter.update(iterable_or_mapping) -> None', '**Add** counts (unlike `dict.update`, which replaces).', { params: 'iterable_or_mapping: items to count', header: 'from collections import Counter', returns: 'None — adds counts in place', example: 'c = Counter("aab")\nc.update("ab")  # c[\'a\'] == 3, c[\'b\'] == 2' }),
  M('Counter', 'subtract', 'Counter.subtract(iterable_or_mapping) -> None', 'Subtract counts in place; results may go negative or zero (keys are kept).', { params: 'iterable_or_mapping: items to subtract', header: 'from collections import Counter', returns: 'None — subtracts counts in place', example: 'c = Counter("aab")\nc.subtract("abb")  # c[\'a\'] == 1, c[\'b\'] == -1' }),
  M('Counter', 'total', 'Counter.total() -> int', 'Sum of all counts (3.10+).', { header: 'from collections import Counter', returns: 'int — sum of all counts', example: 'Counter("hello").total()  # 5' }),
  F('collections', 'defaultdict', 'defaultdict(default_factory) -> defaultdict', 'Dict that creates missing values with `default_factory()` on access: `defaultdict(list)` for adjacency lists, `defaultdict(int)` for counts. Gotcha: even **reading** a missing key inserts it; use `in` to test.', {
    params: 'default_factory: zero-arg callable like list, int, set', example: 'g = defaultdict(list)\nfor u, v in edges:\n    g[u].append(v)\n    g[v].append(u)', header: 'from collections import defaultdict', insert: 'defaultdict(${1:list})', returns: 'defaultdict — a dict that fills missing keys' }),
  F('collections', 'deque', 'deque(iterable=(), maxlen=None) -> deque', 'Double-ended queue: **O(1)** append/pop at both ends — the right choice for BFS queues. Indexing in the middle is O(n). With *maxlen*, old items fall off the other end.', {
    params: 'iterable: initial items|maxlen: optional maximum length', example: 'q = deque([start])\nwhile q:\n    node = q.popleft()', header: 'from collections import deque', returns: 'deque — a new double-ended queue' }),
  M('deque', 'append', 'deque.append(x) -> None', 'Add to the right end. O(1).', { params: 'x: item', header: 'from collections import deque', returns: 'None', example: 'q = deque([1])\nq.append(2)  # deque([1, 2])' }),
  M('deque', 'appendleft', 'deque.appendleft(x) -> None', 'Add to the left end. O(1).', { params: 'x: item', header: 'from collections import deque', returns: 'None', example: 'q = deque([1, 2])\nq.appendleft(0)  # deque([0, 1, 2])' }),
  M('deque', 'pop', 'deque.pop() -> item', 'Remove and return the rightmost item. O(1). `IndexError` if empty.', { header: 'from collections import deque', returns: 'the removed rightmost item', example: 'q = deque([1, 2, 3])\nq.pop()  # 3' }),
  M('deque', 'popleft', 'deque.popleft() -> item', 'Remove and return the leftmost item. **O(1)** (vs `list.pop(0)` O(n)). `IndexError` if empty.', { header: 'from collections import deque', returns: 'the removed leftmost item', example: 'q = deque([1, 2, 3])\nq.popleft()  # 1' }),
  M('deque', 'extend', 'deque.extend(iterable) -> None', 'Append items on the right.', { params: 'iterable: items', header: 'from collections import deque', returns: 'None', example: 'q = deque([1])\nq.extend([2, 3])  # deque([1, 2, 3])' }),
  M('deque', 'extendleft', 'deque.extendleft(iterable) -> None', 'Append items on the left — note the order ends up **reversed**.', { params: 'iterable: items', header: 'from collections import deque', returns: 'None', example: 'q = deque([3])\nq.extendleft([2, 1])  # deque([1, 2, 3])' }),
  M('deque', 'rotate', 'deque.rotate(n=1) -> None', 'Rotate right by *n* steps (left if negative).', { params: 'n: steps', header: 'from collections import deque', returns: 'None — rotates in place', example: 'q = deque([1, 2, 3, 4])\nq.rotate(1)  # deque([4, 1, 2, 3])' }),
  M('deque', 'clear', 'deque.clear() -> None', 'Remove all items.', { header: 'from collections import deque', returns: 'None', example: 'q.clear()  # deque([])' }),
  M('deque', 'count', 'deque.count(x) -> int', 'Number of items equal to *x*. O(n).', { params: 'x: value', header: 'from collections import deque', returns: 'int — number of equal items', example: 'deque("abca").count("a")  # 2' }),
  M('deque', 'remove', 'deque.remove(value) -> None', 'Remove the first occurrence. O(n).', { params: 'value: value', header: 'from collections import deque', returns: 'None; raises ValueError if absent', example: 'q = deque([1, 2, 1])\nq.remove(1)  # deque([2, 1])' }),
  M('deque', 'index', 'deque.index(x) -> int', 'Index of first occurrence. O(n).', { params: 'x: value', header: 'from collections import deque', returns: 'int — index of the first occurrence; raises ValueError if absent', example: 'deque("abc").index("c")  # 2' }),
  M('deque', 'reverse', 'deque.reverse() -> None', 'Reverse in place.', { header: 'from collections import deque', returns: 'None — reverses in place', example: 'q = deque([1, 2, 3])\nq.reverse()  # deque([3, 2, 1])' }),
  F('collections', 'OrderedDict', 'OrderedDict(items=()) -> OrderedDict', 'Dict with order-manipulation methods (`move_to_end`, `popitem(last=False)`) — the classic LRU cache building block.', {
    params: 'items: initial pairs', header: 'from collections import OrderedDict', returns: 'OrderedDict — a new ordered dictionary', example: 'cache = OrderedDict()\ncache["a"] = 1\ncache.move_to_end("a")  # mark as most recently used' }),
  M('OrderedDict', 'move_to_end', 'OrderedDict.move_to_end(key, last=True) -> None', 'Move *key* to the end (or the front with `last=False`). O(1).', { params: 'key: existing key|last: True = end, False = front', header: 'from collections import OrderedDict', returns: 'None; raises KeyError if *key* is missing', example: 'od = OrderedDict.fromkeys("abc")\nod.move_to_end("a")  # order is now b, c, a' }),
  M('OrderedDict', 'popitem', 'OrderedDict.popitem(last=True) -> (key, value)', 'Pop the last pair, or the first with `last=False` (evict the least-recently-used).', { params: 'last: True = last, False = first', header: 'from collections import OrderedDict', returns: 'tuple (key, value); KeyError if empty', example: 'od = OrderedDict(a=1, b=2)\nod.popitem(last=False)  # (\'a\', 1)' }),
  F('collections', 'namedtuple', 'namedtuple(typename, field_names) -> type', 'Tuple subclass with named fields: `P = namedtuple("P", "x y")`.', { params: 'typename: class name|field_names: "x y" or list', header: 'from collections import namedtuple', returns: 'type — a new tuple subclass with named fields', example: 'Point = namedtuple("Point", "x y")\np = Point(1, 2)\np.x + p.y  # 3' }),

  // ===================== heapq =====================
  F('heapq', 'heappush', 'heapq.heappush(heap, item) -> None', 'Push *item*, keeping the **min**-heap invariant. **O(log n)**. For a max-heap push `-x`; push tuples `(priority, tiebreak, item)` to avoid comparing uncomparable items.', {
    params: 'heap: a list maintained as a min-heap|item: value to push', example: 'h = []\nheapq.heappush(h, (dist, node))', insert: 'heappush(${1:heap}, ${2:item})', returns: 'None — the heap list is modified in place' }),
  F('heapq', 'heappop', 'heapq.heappop(heap) -> item', 'Pop and return the smallest item. **O(log n)**. `IndexError` if empty. `heap[0]` peeks without popping.', { params: 'heap: min-heap list', insert: 'heappop(${1:heap})', returns: 'the smallest item; IndexError if empty', example: 'h = [1, 5, 3]  # already a valid heap\nheapq.heappop(h)  # 1' }),
  F('heapq', 'heapify', 'heapq.heapify(x) -> None', 'Turn a list into a min-heap **in place** in **O(n)**.', { params: 'x: list to heapify', returns: 'None — rearranges *x* in place', example: 'h = [5, 1, 4]\nheapq.heapify(h)\nh[0]  # 1' }),
  F('heapq', 'heappushpop', 'heapq.heappushpop(heap, item) -> item', 'Push then pop the smallest, faster than separate calls; keeps a size-k heap of the k largest.', { params: 'heap: min-heap list|item: value to push', returns: 'the smallest of *item* and the heap contents', example: 'h = [2, 5]\nheapq.heappushpop(h, 1)  # 1, h unchanged\nheapq.heappushpop(h, 9)  # 2, h is now [5, 9]' }),
  F('heapq', 'heapreplace', 'heapq.heapreplace(heap, item) -> item', 'Pop the smallest, then push *item* (heap must be non-empty).', { params: 'heap: min-heap list|item: value to push', returns: 'the smallest item from before the push; IndexError if empty', example: 'h = [1, 5]\nheapq.heapreplace(h, 3)  # 1, h is now [3, 5]' }),
  F('heapq', 'nlargest', 'heapq.nlargest(n, iterable, key=None) -> list', 'The *n* largest items, descending. **O(m log n)**.', { params: 'n: how many|iterable: items|key: key function', returns: 'list — the n largest items, largest first', example: 'heapq.nlargest(2, [5, 1, 9, 3])  # [9, 5]' }),
  F('heapq', 'nsmallest', 'heapq.nsmallest(n, iterable, key=None) -> list', 'The *n* smallest items, ascending.', { params: 'n: how many|iterable: items|key: key function', returns: 'list — the n smallest items, smallest first', example: 'heapq.nsmallest(2, [5, 1, 9, 3])  # [1, 3]\nheapq.nsmallest(k, pts, key=lambda p: p[0]**2 + p[1]**2)' }),
  F('heapq', 'merge', 'heapq.merge(*iterables, key=None, reverse=False) -> iterator', 'Lazily merge already-sorted iterables.', { params: '*iterables: sorted inputs|key: key function|reverse: inputs sorted descending', returns: 'iterator over all items in sorted order', example: 'list(heapq.merge([1, 4], [2, 3]))  # [1, 2, 3, 4]' }),

  // ===================== bisect =====================
  F('bisect', 'bisect_left', 'bisect.bisect_left(a, x, lo=0, hi=len(a), *, key=None) -> int', 'First index where *x* could be inserted keeping *a* sorted (index of first item **≥ x**). **O(log n)**. *a* must be sorted.', {
    params: 'a: sorted list|x: value|lo: lower bound|hi: upper bound|key: key function (3.10+)', example: 'i = bisect_left(a, x)\nfound = i < len(a) and a[i] == x', returns: 'int in [lo, hi] — insertion point before any equal items' }),
  F('bisect', 'bisect_right', 'bisect.bisect_right(a, x, lo=0, hi=len(a), *, key=None) -> int', 'Insertion index after any existing *x* (index of first item **> x**). `bisect_right(a, x) - bisect_left(a, x)` counts occurrences. Alias: `bisect.bisect`.', {
    params: 'a: sorted list|x: value|lo: lower bound|hi: upper bound|key: key function (3.10+)', returns: 'int in [lo, hi] — insertion point after any equal items', example: 'a = [1, 2, 2, 3]\nbisect.bisect_right(a, 2)  # 3\nbisect.bisect_left(a, 2)  # 1' }),
  F('bisect', 'bisect', 'bisect.bisect(a, x, lo=0, hi=len(a)) -> int', 'Alias of `bisect_right`.', { params: 'a: sorted list|x: value|lo: lower bound|hi: upper bound', returns: 'int — same as bisect_right', example: 'bisect.bisect([10, 20, 30], 20)  # 2' }),
  F('bisect', 'insort', 'bisect.insort(a, x, lo=0, hi=len(a)) -> None', 'Insert *x* keeping *a* sorted. Search is O(log n) but the insert is **O(n)**.', { params: 'a: sorted list|x: value|lo: lower bound|hi: upper bound', returns: 'None — inserts into *a* in place', example: 'a = [1, 3, 5]\nbisect.insort(a, 4)  # a == [1, 3, 4, 5]' }),
  F('bisect', 'insort_left', 'bisect.insort_left(a, x) -> None', 'Insert *x* before any equal items. O(n).', { params: 'a: sorted list|x: value', returns: 'None — inserts into *a* in place', example: 'a = [1, 2, 3]\nbisect.insort_left(a, 2)  # a == [1, 2, 2, 3]' }),

  // ===================== math =====================
  F('math', 'gcd', 'math.gcd(*integers) -> int', 'Greatest common divisor (any number of args since 3.9); `gcd(0, 0) == 0`.', { params: '*integers: integers', returns: 'int — the non-negative GCD', example: 'math.gcd(12, 18)  # 6\ng = math.gcd(*nums)' }),
  F('math', 'lcm', 'math.lcm(*integers) -> int', 'Least common multiple (3.9+).', { params: '*integers: integers', returns: 'int — the non-negative LCM', example: 'math.lcm(4, 6)  # 12' }),
  F('math', 'isqrt', 'math.isqrt(n) -> int', 'Exact integer square root `floor(sqrt(n))` — use this instead of `int(math.sqrt(n))`, which is wrong for large n.', { params: 'n: non-negative int', returns: 'int — floor of the exact square root; ValueError if n < 0', example: 'math.isqrt(17)  # 4\nis_square = math.isqrt(n) ** 2 == n' }),
  F('math', 'sqrt', 'math.sqrt(x) -> float', 'Float square root; `ValueError` for negatives.', { params: 'x: number', returns: 'float; ValueError for negative *x*', example: 'math.sqrt(2)  # 1.4142135623730951' }),
  F('math', 'floor', 'math.floor(x) -> int', 'Largest int ≤ *x*. For ints prefer `//`.', { params: 'x: number', returns: 'int', example: 'math.floor(-2.5)  # -3' }),
  F('math', 'ceil', 'math.ceil(x) -> int', 'Smallest int ≥ *x*. For ints prefer `-(-a // b)` to avoid float error.', { params: 'x: number', returns: 'int', example: 'math.ceil(2.1)  # 3\n-(-7 // 2)  # 4: exact integer ceil division' }),
  F('math', 'comb', 'math.comb(n, k) -> int', 'Binomial coefficient n choose k (exact; 0 if k > n).', { params: 'n: total|k: chosen', returns: 'int — n choose k', example: 'math.comb(5, 2)  # 10' }),
  F('math', 'perm', 'math.perm(n, k=None) -> int', 'Number of ordered arrangements n!/(n-k)!.', { params: 'n: total|k: chosen (default n)', returns: 'int — n! / (n - k)!', example: 'math.perm(5, 2)  # 20' }),
  F('math', 'factorial', 'math.factorial(n) -> int', 'n! (exact big int).', { params: 'n: non-negative int', returns: 'int; ValueError for negative *n*', example: 'math.factorial(5)  # 120' }),
  F('math', 'log', 'math.log(x, base=e) -> float', 'Logarithm (natural by default).', { params: 'x: positive number|base: base', returns: 'float; ValueError for x <= 0', example: 'math.log(math.e)  # 1.0\nmath.log(1000, 10)  # 2.9999999999999996 (float error)' }),
  F('math', 'log2', 'math.log2(x) -> float', 'Base-2 logarithm. For exact int results use `n.bit_length() - 1`.', { params: 'x: positive number', returns: 'float', example: 'math.log2(1024)  # 10.0' }),
  F('math', 'log10', 'math.log10(x) -> float', 'Base-10 logarithm.', { params: 'x: positive number', returns: 'float', example: 'math.log10(1000)  # 3.0' }),
  F('math', 'exp', 'math.exp(x) -> float', 'e ** x.', { params: 'x: exponent', returns: 'float — e ** x', example: 'math.exp(1)  # 2.718281828459045' }),
  F('math', 'pow', 'math.pow(x, y) -> float', 'Float power; for ints use `**` or builtin `pow` (exact).', { params: 'x: base|y: exponent', returns: 'float — x ** y as a float', example: 'math.pow(2, 10)  # 1024.0' }),
  F('math', 'fabs', 'math.fabs(x) -> float', 'Float absolute value.', { params: 'x: number', returns: 'float', example: 'math.fabs(-3)  # 3.0' }),
  F('math', 'hypot', 'math.hypot(*coordinates) -> float', 'Euclidean distance from origin: `hypot(dx, dy)`.', { params: '*coordinates: numbers', returns: 'float — Euclidean norm', example: 'math.hypot(3, 4)  # 5.0' }),
  F('math', 'dist', 'math.dist(p, q) -> float', 'Euclidean distance between two points.', { params: 'p: point|q: point', returns: 'float — Euclidean distance', example: 'math.dist((0, 0), (3, 4))  # 5.0' }),
  F('math', 'prod', 'math.prod(iterable, start=1) -> number', 'Product of all items.', { params: 'iterable: numbers|start: initial value', returns: 'number — the product (*start* for empty input)', example: 'math.prod([2, 3, 4])  # 24' }),
  F('math', 'isclose', 'math.isclose(a, b, rel_tol=1e-09, abs_tol=0.0) -> bool', 'Float comparison with tolerance.', { params: 'a: number|b: number|rel_tol: relative tolerance|abs_tol: absolute tolerance', returns: 'bool', example: '0.1 + 0.2 == 0.3  # False\nmath.isclose(0.1 + 0.2, 0.3)  # True' }),
  F('math', 'trunc', 'math.trunc(x) -> int', 'Truncate toward zero.', { params: 'x: number', returns: 'int — *x* truncated toward zero', example: 'math.trunc(-2.7)  # -2' }),
  F('math', 'sin', 'math.sin(x) -> float', 'Sine of *x* radians.', { params: 'x: radians', returns: 'float', example: 'math.sin(math.pi / 2)  # 1.0' }),
  F('math', 'cos', 'math.cos(x) -> float', 'Cosine of *x* radians.', { params: 'x: radians', returns: 'float', example: 'math.cos(0)  # 1.0' }),
  F('math', 'atan2', 'math.atan2(y, x) -> float', 'Angle of the point (x, y) in radians, in (-π, π].', { params: 'y: y coordinate|x: x coordinate', returns: 'float — angle in radians, in [-π, π]', example: 'math.atan2(1, 1)  # 0.7853981633974483 (π/4)' }),
  F('math', 'isinf', 'math.isinf(x) -> bool', 'Whether *x* is ±infinity.', { params: 'x: number', returns: 'bool', example: 'math.isinf(math.inf)  # True' }),
  e('constant', 'math', 'inf', 'math.inf', 'Positive float infinity (`float("inf")`); handy initial value for minimums.', { header: 'import math', example: 'best = math.inf\nfor c in costs:\n    best = min(best, c)' }),
  e('constant', 'math', 'pi', 'math.pi', 'π = 3.141592653589793.', { header: 'import math', example: 'area = math.pi * r ** 2' }),
  e('constant', 'math', 'e', 'math.e', 'e = 2.718281828459045.', { header: 'import math', example: 'math.log(math.e)  # 1.0' }),

  // ===================== itertools =====================
  F('itertools', 'permutations', 'itertools.permutations(iterable, r=None) -> iterator', 'All r-length orderings as tuples (n!/(n-r)! of them — explodes fast). Items are treated as distinct by position.', { params: 'iterable: items|r: length (default all)', returns: 'iterator of tuples', example: 'list(itertools.permutations([1, 2, 3], 2))\n# [(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]' }),
  F('itertools', 'combinations', 'itertools.combinations(iterable, r) -> iterator', 'All r-length subsets as tuples, in input order (C(n, r) of them).', { params: 'iterable: items|r: subset size', returns: 'iterator of tuples', example: 'list(itertools.combinations([1, 2, 3], 2))\n# [(1, 2), (1, 3), (2, 3)]' }),
  F('itertools', 'combinations_with_replacement', 'itertools.combinations_with_replacement(iterable, r) -> iterator', 'r-length combinations allowing repeated items.', { params: 'iterable: items|r: size', returns: 'iterator of tuples', example: 'list(itertools.combinations_with_replacement("ab", 2))\n# [(\'a\', \'a\'), (\'a\', \'b\'), (\'b\', \'b\')]' }),
  F('itertools', 'product', 'itertools.product(*iterables, repeat=1) -> iterator', 'Cartesian product, like nested loops: `product("01", repeat=n)` gives all bit strings.', { params: '*iterables: input iterables|repeat: repeat the inputs', returns: 'iterator of tuples', example: 'list(itertools.product([0, 1], repeat=2))\n# [(0, 0), (0, 1), (1, 0), (1, 1)]' }),
  F('itertools', 'accumulate', 'itertools.accumulate(iterable, func=operator.add, *, initial=None) -> iterator', 'Running totals (prefix sums): `list(accumulate(a, initial=0))` has length n+1. *func* can be `max` for running max.', {
    params: 'iterable: values|func: binary function|initial: value emitted first', returns: 'iterator of running results', example: 'list(itertools.accumulate([1, 2, 3], initial=0))  # [0, 1, 3, 6]\nlist(itertools.accumulate([3, 1, 4], max))  # [3, 3, 4]' }),
  F('itertools', 'groupby', 'itertools.groupby(iterable, key=None) -> iterator', 'Group **consecutive** equal-key items into `(key, group_iter)`. Sort first to group globally. Run-length encoding: `[(k, len(list(g))) for k, g in groupby(s)]`.', {
    params: 'iterable: items|key: key function', returns: 'iterator of (key, group) pairs; a group is invalidated once you advance to the next', example: '[(k, len(list(g))) for k, g in itertools.groupby("aaabcc")]\n# [(\'a\', 3), (\'b\', 1), (\'c\', 2)]' }),
  F('itertools', 'chain', 'itertools.chain(*iterables) -> iterator', 'Iterate the inputs one after another. `chain.from_iterable(lists)` flattens one level.', { params: '*iterables: iterables to concatenate', returns: 'iterator over all items in order', example: 'list(itertools.chain([1, 2], [3]))  # [1, 2, 3]\nflat = list(itertools.chain.from_iterable(grid))' }),
  F('itertools', 'count', 'itertools.count(start=0, step=1) -> iterator', 'Infinite counter.', { params: 'start: first value|step: increment', returns: 'infinite iterator', example: 'for i in itertools.count(1):\n    if ok(i):\n        break' }),
  F('itertools', 'cycle', 'itertools.cycle(iterable) -> iterator', 'Repeat the items forever.', { params: 'iterable: items', returns: 'infinite iterator', example: 'turns = itertools.cycle(["A", "B"])\nnext(turns)  # \'A\'' }),
  F('itertools', 'repeat', 'itertools.repeat(object, times=None) -> iterator', 'Yield *object* repeatedly (forever if *times* is None).', { params: 'object: value|times: count', returns: 'iterator (infinite if *times* is None)', example: 'list(itertools.repeat(0, 3))  # [0, 0, 0]' }),
  F('itertools', 'islice', 'itertools.islice(iterable, stop) / islice(iterable, start, stop, step=1) -> iterator', 'Slice any iterator lazily.', { params: 'iterable: items|start: start index|stop: end index|step: step', returns: 'iterator over the selected items', example: 'list(itertools.islice(itertools.count(), 5))  # [0, 1, 2, 3, 4]' }),
  F('itertools', 'pairwise', 'itertools.pairwise(iterable) -> iterator', 'Consecutive pairs `(a[0], a[1]), (a[1], a[2]), ...` (3.10+).', { params: 'iterable: items', returns: 'iterator of overlapping pairs', example: 'list(itertools.pairwise([1, 4, 9]))  # [(1, 4), (4, 9)]\ndiffs = [b - a for a, b in itertools.pairwise(nums)]' }),
  F('itertools', 'zip_longest', 'itertools.zip_longest(*iterables, fillvalue=None) -> iterator', 'Like `zip` but runs to the longest input, padding with *fillvalue*.', { params: '*iterables: inputs|fillvalue: padding value', returns: 'iterator of tuples', example: 'list(itertools.zip_longest("ab", "x", fillvalue="-"))\n# [(\'a\', \'x\'), (\'b\', \'-\')]' }),
  F('itertools', 'starmap', 'itertools.starmap(function, iterable) -> iterator', 'Call *function* with each tuple unpacked as arguments.', { params: 'function: callable|iterable: tuples of args', returns: 'iterator of results', example: 'list(itertools.starmap(pow, [(2, 3), (3, 2)]))  # [8, 9]' }),
  F('itertools', 'takewhile', 'itertools.takewhile(predicate, iterable) -> iterator', 'Yield items while *predicate* is true.', { params: 'predicate: test|iterable: items', returns: 'iterator', example: 'list(itertools.takewhile(lambda x: x < 3, [1, 2, 5, 1]))  # [1, 2]' }),
  F('itertools', 'dropwhile', 'itertools.dropwhile(predicate, iterable) -> iterator', 'Skip items while *predicate* is true, then yield the rest.', { params: 'predicate: test|iterable: items', returns: 'iterator', example: 'list(itertools.dropwhile(lambda x: x < 3, [1, 2, 5, 1]))  # [5, 1]' }),

  // ===================== functools =====================
  F('functools', 'lru_cache', '@functools.lru_cache(maxsize=128)', 'Memoize a function by its (hashable) arguments. Use `@lru_cache(maxsize=None)` (or `@cache`) for DP; the default 128 evicts entries. Deep recursion still needs `sys.setrecursionlimit`.', {
    params: 'maxsize: cache size, None = unbounded', example: '@lru_cache(maxsize=None)\ndef dp(i, j):\n    ...', insert: 'lru_cache(maxsize=None)', header: 'from functools import lru_cache', returns: 'decorator — the wrapped function gains cache_info() and cache_clear()' }),
  F('functools', 'cache', '@functools.cache', 'Unbounded memoization (3.9+), same as `lru_cache(maxsize=None)`. Arguments must be hashable (convert lists to tuples). Clear with `f.cache_clear()` between test cases.', {
    example: '@cache\ndef fib(n):\n    return n if n < 2 else fib(n - 1) + fib(n - 2)', header: 'from functools import cache', returns: 'the memoized function (with cache_info() and cache_clear())' }),
  F('functools', 'reduce', 'functools.reduce(function, iterable, initial) -> value', 'Fold *iterable* into one value with a two-argument *function*. `TypeError` on empty input without *initial*.', {
    params: 'function: f(acc, item)|iterable: items|initial: starting accumulator', header: 'from functools import reduce', returns: 'the final accumulated value', example: 'reduce(lambda acc, x: acc * x, [1, 2, 3, 4])  # 24\nreduce(lambda a, b: a ^ b, nums, 0)  # XOR of all' }),
  F('functools', 'cmp_to_key', 'functools.cmp_to_key(func) -> key', 'Turn an old-style comparator (negative/0/positive) into a `key=` for sorting, e.g. "largest number" concatenation order.', {
    params: 'func: cmp(a, b) -> int', example: 'nums.sort(key=cmp_to_key(lambda a, b: (b + a > a + b) - (b + a < a + b)))', header: 'from functools import cmp_to_key', returns: 'key wrapper class usable as `key=`' }),
  F('functools', 'partial', 'functools.partial(func, *args, **kwargs) -> callable', 'Pre-fill some arguments of *func*.', { params: 'func: callable|*args: fixed positional args|**kwargs: fixed keyword args', returns: 'partial object — a callable with the arguments pre-filled', header: 'from functools import partial', example: 'int2 = partial(int, base=2)\nint2("101")  # 5' }),

  // ===================== sys =====================
  F('sys', 'setrecursionlimit', 'sys.setrecursionlimit(limit) -> None', 'Raise the recursion limit (default **1000**) for deep DFS/memoized recursion. In the browser (Pyodide) the real stack is smaller, so very deep recursion can still crash — prefer iteration.', {
    params: 'limit: new maximum depth', example: 'import sys\nsys.setrecursionlimit(10**6)', returns: 'None' }),
  e('function', 'sys.stdin', 'readline', 'sys.stdin.readline() -> str', 'Read one line **including** the trailing `\\n` (strip it). Much faster than `input()` for big inputs; returns `""` at EOF.', {
    example: 'import sys\ninput = sys.stdin.readline\nn = int(input())', header: 'import sys', returns: 'str — the next line including its "\\n"; "" at EOF' }),
  e('function', 'sys.stdin', 'read', 'sys.stdin.read() -> str', 'Read all remaining input at once; `sys.stdin.read().split()` tokenizes everything.', { header: 'import sys', returns: 'str — all remaining input', example: 'import sys\ndata = sys.stdin.read().split()\nn = int(data[0])' }),
  e('constant', 'sys', 'maxsize', 'sys.maxsize', 'Largest list index (2**63 - 1). Python ints are unbounded; `math.inf` is often a better sentinel.', { header: 'import sys', example: 'import sys\nsys.maxsize  # 9223372036854775807 on 64-bit' }),
  e('constant', 'sys', 'stdin', 'sys.stdin', 'Standard input stream (`readline`, `read`, iterate over lines).', { header: 'import sys', example: 'import sys\nfor line in sys.stdin:\n    process(line.rstrip("\\n"))' }),
  e('constant', 'sys', 'stdout', 'sys.stdout', 'Standard output stream; `sys.stdout.write(s)` writes without a newline.', { header: 'import sys', example: 'import sys\nsys.stdout.write("\\n".join(out) + "\\n")' }),

  F('sys', 'exit', 'sys.exit(arg=None) -> NoReturn', 'Stop the program by raising `SystemExit`; an int *arg* is the exit status, any other object is printed to stderr (exit status 1). Handy for early exit once the answer is printed.', {
    params: 'arg: exit status (0/None = success) or message', returns: 'never returns — raises SystemExit', example: 'import sys\nif n == 0:\n    print(0)\n    sys.exit()' }),
  e('function', 'sys.stdout', 'write', 'sys.stdout.write(s) -> int', 'Write the string *s* with no added newline or separator; faster than many `print` calls. Only accepts `str` (convert numbers first).', {
    params: 's: string to write', returns: 'int — number of characters written', example: 'import sys\nsys.stdout.write(" ".join(map(str, ans)) + "\\n")', header: 'import sys' }),

  // ===================== string =====================
  e('constant', 'string', 'ascii_lowercase', 'string.ascii_lowercase', '`"abcdefghijklmnopqrstuvwxyz"`.', {
    example: 'import string\nfor ch in string.ascii_lowercase:\n    ...', header: 'import string' }),
  e('constant', 'string', 'ascii_uppercase', 'string.ascii_uppercase', '`"ABCDEFGHIJKLMNOPQRSTUVWXYZ"`.', {
    example: 'import string\nstring.ascii_uppercase.index("C")  # 2', header: 'import string' }),
  e('constant', 'string', 'ascii_letters', 'string.ascii_letters', 'Lowercase followed by uppercase ASCII letters (52 characters).', {
    example: 'import string\nletters = set(string.ascii_letters)', header: 'import string' }),
  e('constant', 'string', 'digits', 'string.digits', '`"0123456789"`.', {
    example: 'import string\nall(c in string.digits for c in "2024")  # True', header: 'import string' }),
  e('constant', 'string', 'punctuation', 'string.punctuation', 'ASCII punctuation characters, e.g. `!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~`.', {
    example: 'import string\nclean = "".join(c for c in s if c not in string.punctuation)', header: 'import string' }),

  // ===================== dataclasses =====================
  F('dataclasses', 'dataclass', '@dataclasses.dataclass(order=False, frozen=False)', 'Class decorator that generates `__init__`, `__repr__` and `__eq__` from annotated fields. `order=True` adds `<` etc. (compares fields as a tuple, usable in `heapq`); `frozen=True` makes instances immutable and hashable.', {
    params: 'order: generate comparison methods|frozen: make instances immutable and hashable', returns: 'the same class with the generated methods added',
    example: '@dataclass(order=True)\nclass Edge:\n    w: int\n    v: int', header: 'from dataclasses import dataclass' }),

  // ===================== typing =====================
  e('type', 'typing', 'List', 'List[T]', 'Type hint for a list (3.9+: plain `list[int]` works too).', { header: 'from typing import List', example: 'from typing import List\ndef total(nums: List[int]) -> int:\n    return sum(nums)' }),
  e('type', 'typing', 'Optional', 'Optional[T]', 'Type hint meaning `T | None`.', { header: 'from typing import Optional', example: 'from typing import Optional\ndef find(nums: list[int], x: int) -> Optional[int]:\n    return nums.index(x) if x in nums else None' }),
  e('type', 'typing', 'Dict', 'Dict[K, V]', 'Type hint for a dict (or plain `dict[K, V]`).', { header: 'from typing import Dict', example: 'from typing import Dict\ncounts: Dict[str, int] = {}' }),
  e('type', 'typing', 'Tuple', 'Tuple[T, ...]', 'Type hint for a tuple (or plain `tuple[int, int]`).', { header: 'from typing import Tuple', example: 'from typing import Tuple\ndef split(n: int) -> Tuple[int, int]:\n    return n // 10, n % 10' }),
  e('type', 'typing', 'Set', 'Set[T]', 'Type hint for a set (or plain `set[int]`).', { header: 'from typing import Set', example: 'from typing import Set\nseen: Set[int] = set()' }),

  // ===================== modules =====================
  e('module', null, 'collections', 'import collections', 'Container datatypes: `Counter`, `defaultdict`, `deque`, `OrderedDict`, `namedtuple`.', { example: 'from collections import Counter, defaultdict, deque' }),
  e('module', null, 'heapq', 'import heapq', 'Binary **min**-heap functions operating on plain lists.', { example: 'import heapq\nh = [3, 1, 2]\nheapq.heapify(h)\nheapq.heappop(h)  # 1' }),
  e('module', null, 'bisect', 'import bisect', 'Binary search / insertion on sorted lists.', { example: 'import bisect\nbisect.bisect_left([1, 3, 5], 4)  # 2' }),
  e('module', null, 'math', 'import math', 'Math functions: `gcd`, `isqrt`, `comb`, `inf`, `log2`, ...', { example: 'import math\nmath.gcd(12, 8)  # 4' }),
  e('module', null, 'itertools', 'import itertools', 'Iterator building blocks: `permutations`, `combinations`, `product`, `accumulate`, `groupby`, `chain`.', { example: 'import itertools\nfor a, b in itertools.combinations(nums, 2):\n    ...' }),
  e('module', null, 'functools', 'import functools', 'Higher-order helpers: `cache`, `lru_cache`, `reduce`, `cmp_to_key`.', { example: 'from functools import cache\n@cache\ndef f(n): ...' }),
  e('module', null, 'sys', 'import sys', 'Interpreter access: `sys.stdin`, `sys.setrecursionlimit`, `sys.maxsize`.', { example: 'import sys\ninput = sys.stdin.readline\nsys.setrecursionlimit(10**6)' }),
  e('module', null, 'string', 'import string', 'String constants: `ascii_lowercase`, `ascii_uppercase`, `ascii_letters`, `digits`, `punctuation`.', {
    example: 'import string\nalphabet = string.ascii_lowercase' }),
  e('module', null, 'dataclasses', 'from dataclasses import dataclass', 'Generate boilerplate (`__init__`, `__repr__`, `__eq__`, ordering) for record classes.', {
    example: 'from dataclasses import dataclass\n@dataclass\nclass Point:\n    x: int' }),
  e('module', null, 'typing','from typing import List, Optional', 'Type-hint helpers.', { example: 'from typing import List, Optional\ndef first(a: List[int]) -> Optional[int]:\n    return a[0] if a else None' }),
];
