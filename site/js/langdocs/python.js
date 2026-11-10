// Python 3.11 reference for Crucible's editor (hover / completion / signature help).
// Built with a tiny helper for brevity; the default export is a plain array of entries.

const P = (s) => s.split('|').map((x) => {
  const i = x.indexOf(':');
  return { label: x.slice(0, i).trim(), doc: x.slice(i + 1).trim() };
});

// e(kind, owner, name, sig, doc, extra?)  -- extra: { params, example, insert, header }
function e(kind, owner, name, sig, doc, extra = {}) {
  const o = { name };
  if (owner) o.owner = owner;
  o.kind = kind;
  o.sig = sig;
  if (extra.params) o.params = typeof extra.params === 'string' ? P(extra.params) : extra.params;
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
  K('return', 'return [value]', 'Exit the function with *value* (or `None` if omitted). `return a, b` returns a tuple.'),
  K('if', 'if cond: ... elif cond: ... else: ...', 'Conditional. Empty containers, `0`, `""` and `None` are falsy. Conditional expression: `a if cond else b`.', {
    insert: 'if ${1:cond}:\n\t${0:pass}' }),
  K('elif', 'elif cond:', 'Else-if branch of an `if` chain.', { insert: 'elif ${1:cond}:\n\t${0:pass}' }),
  K('else', 'else:', 'Fallback branch of `if`; also allowed after `for`/`while` (runs if the loop did **not** `break`) and `try` (runs if no exception).', { insert: 'else:\n\t${0:pass}' }),
  K('for', 'for x in iterable:', 'Iterate over any iterable. Use `enumerate` for indices, `zip` for parallel lists, `range` for counting. Modifying a list while iterating over it skips elements.', {
    example: 'for i, x in enumerate(nums):\n    print(i, x)', insert: 'for ${1:x} in ${2:iterable}:\n\t${0:pass}' }),
  K('while', 'while cond:', 'Loop while *cond* is truthy. `while queue:` loops until a container is empty.', { insert: 'while ${1:cond}:\n\t${0:pass}' }),
  K('break', 'break', 'Exit the innermost loop (skips the loop\'s `else`). Breaks only one level; use a flag or a function `return` for nested loops.'),
  K('continue', 'continue', 'Skip to the next iteration of the innermost loop.'),
  K('pass', 'pass', 'A no-op placeholder where a statement is syntactically required.'),
  K('in', 'x in container', 'Membership test (`for` also uses it). **O(1)** average for `set`/`dict`, **O(n)** for `list`/`tuple`/`str` (substring search for `str`).'),
  K('not', 'not x', 'Logical negation; `not in` and `is not` are the negated membership/identity tests.'),
  K('and', 'a and b', 'Short-circuit AND; returns the first falsy operand or the last one (`0 and 5` → `0`).'),
  K('or', 'a or b', 'Short-circuit OR; returns the first truthy operand (`x or default`). Beware: `0 or 5` → `5`.'),
  K('is', 'a is b', 'Identity test. Use only for singletons: `x is None`. Never compare numbers or strings with `is`.'),
  K('None', 'None', 'The null value. Functions without `return` give `None`; so do in-place methods like `list.sort()`.'),
  K('True', 'True', 'Boolean true; `bool` is a subclass of `int`, so `True + True == 2`.'),
  K('False', 'False', 'Boolean false (equals `0`).'),
  K('class', 'class Name(Base):', 'Define a class. `__init__` sets up instances; `__lt__` makes objects comparable (for `heapq`/`sorted`). Use `@dataclass` for simple records.', {
    example: 'class Node:\n    def __init__(self, val, next=None):\n        self.val, self.next = val, next', insert: 'class ${1:Name}:\n\tdef __init__(self${2}):\n\t\t${0:pass}' }),
  K('lambda', 'lambda args: expr', 'Anonymous single-expression function, typically a `key=`. Gotcha: lambdas in a loop capture the variable, not its value (`lambda i=i: i` to bind).', {
    example: 'pairs.sort(key=lambda p: (p[1], -p[0]))', insert: 'lambda ${1:x}: ${0:x}' }),
  K('with', 'with expr as name:', 'Context manager: guarantees cleanup (closing files, releasing locks).', { insert: 'with ${1:expr} as ${2:name}:\n\t${0:pass}' }),
  K('as', 'import x as y / except E as e / with f as v', 'Bind a name in `import`, `except` and `with`.'),
  K('try', 'try: ... except E as e: ... else: ... finally: ...', 'Handle exceptions. Catch specific exceptions (`except KeyError`), not bare `except:`.', {
    insert: 'try:\n\t${1:pass}\nexcept ${2:Exception} as ${3:e}:\n\t${0:pass}' }),
  K('except', 'except ExcType as e:', 'Handler for an exception type (or tuple of types) in a `try`.', { insert: 'except ${1:Exception} as ${2:e}:\n\t${0:pass}' }),
  K('finally', 'finally:', 'Always runs after `try`, whether or not an exception occurred.', { insert: 'finally:\n\t${0:pass}' }),
  K('raise', 'raise Exc(msg)', 'Raise an exception; bare `raise` re-raises the current one inside `except`.'),
  K('yield', 'yield value', 'Turn a function into a generator that produces values lazily. `yield from it` delegates to another iterable.', {
    example: 'def pairs(n):\n    for i in range(n):\n        yield i, i * i' }),
  K('import', 'import module [as alias]', 'Import a module. Standard library modules (`collections`, `heapq`, `math`, ...) are always available.'),
  K('from', 'from module import name', 'Import names directly: `from collections import Counter, deque`.'),
  K('global', 'global name', 'Let a function assign to a module-level variable. Not needed just to read it or to mutate a global list/dict.'),
  K('nonlocal', 'nonlocal name', 'Let a nested function **assign** to a variable of the enclosing function (e.g. a counter in a DFS helper). Mutating a list needs no declaration.', {
    example: 'def solve():\n    best = 0\n    def dfs(i):\n        nonlocal best' }),
  K('assert', 'assert cond, msg', 'Raise `AssertionError(msg)` if *cond* is false.'),
  K('del', 'del target', 'Delete a name, list item/slice (`del a[i]` is O(n)) or dict key (`KeyError` if missing).'),
  K('match', 'match subject: case pattern: ...', 'Structural pattern matching (3.10+). `case _:` is the wildcard.', { insert: 'match ${1:x}:\n\tcase ${2:pattern}:\n\t\t${0:pass}' }),
  K('async', 'async def f():', 'Define a coroutine (rarely needed in solutions).'),
  K('await', 'await coro', 'Wait for an awaitable inside an `async def`.'),

  // ===================== builtins =====================
  B('print', 'print(*objects, sep=" ", end="\\n", file=sys.stdout, flush=False) -> None', 'Print objects separated by *sep*, followed by *end*. For many lines, build a list and `print("\\n".join(out))` — much faster.', {
    params: '*objects: values to print|sep: separator (default space)|end: terminator (default newline)|file: output stream|flush: force flush', insert: 'print(${1})' }),
  B('input', 'input(prompt="") -> str', 'Read one line from stdin without the trailing newline. Raises `EOFError` at end of input. For large inputs prefer `sys.stdin.readline` or `sys.stdin.read().split()`.', {
    params: 'prompt: text written before reading', example: 'n = int(input())\nnums = list(map(int, input().split()))' }),
  B('len', 'len(s) -> int', 'Number of items in a container. **O(1)**.', { params: 's: sequence or collection', insert: 'len(${1:s})' }),
  B('range', 'range(start, stop, step=1) -> range', 'Lazy arithmetic sequence `start, start+step, ...` up to but **excluding** *stop*. `range(n)` is `0..n-1`; count down with `range(n - 1, -1, -1)`.', {
    params: 'start: first value (default 0)|stop: exclusive end|step: increment, may be negative', insert: 'range(${1:n})' }),
  B('enumerate', 'enumerate(iterable, start=0) -> iterator', 'Yield `(index, item)` pairs.', { params: 'iterable: what to iterate|start: first index', example: 'for i, ch in enumerate(s):\n    ...', insert: 'enumerate(${1:iterable})' }),
  B('zip', 'zip(*iterables, strict=False) -> iterator', 'Yield tuples taking one item from each iterable; stops at the **shortest**. `zip(*grid)` transposes a matrix (as tuples). Use `itertools.zip_longest` to pad.', {
    params: '*iterables: iterables to combine|strict: raise if lengths differ', insert: 'zip(${1:a}, ${2:b})' }),
  B('sorted', 'sorted(iterable, key=None, reverse=False) -> list', 'Return a **new** sorted list (stable, **O(n log n)**). Sort by several fields with a tuple key, e.g. `key=lambda x: (-x[1], x[0])`.', {
    params: 'iterable: items to sort|key: function computing the sort key|reverse: descending if True', insert: 'sorted(${1:iterable})' }),
  B('reversed', 'reversed(seq) -> iterator', 'Reverse iterator over a sequence (no copy). Wrap in `list(...)` to materialize, or use `seq[::-1]`.', { params: 'seq: sequence (list, str, range, ...)' }),
  B('sum', 'sum(iterable, start=0) -> number', 'Add up the items. Don\'t use it to join strings (use `"".join`).', { params: 'iterable: numbers|start: initial value' }),
  B('min', 'min(iterable, *, key=None, default=...) / min(a, b, ...)', 'Smallest item. Raises `ValueError` on an empty iterable unless *default* is given.', {
    params: 'iterable: items to compare|key: function computing comparison key|default: returned when empty' }),
  B('max', 'max(iterable, *, key=None, default=...) / max(a, b, ...)', 'Largest item; `max(d, key=d.get)` is the key with the largest value. Raises `ValueError` on empty input unless *default* is given.', {
    params: 'iterable: items to compare|key: function computing comparison key|default: returned when empty' }),
  B('abs', 'abs(x) -> number', 'Absolute value.', { params: 'x: number' }),
  B('map', 'map(function, iterable, ...) -> iterator', 'Apply *function* to each item lazily. `list(map(int, input().split()))` parses a line of ints.', {
    params: 'function: function to apply|iterable: input items' }),
  B('filter', 'filter(function, iterable) -> iterator', 'Lazily keep items for which *function* returns truthy (`None` keeps truthy items).', { params: 'function: predicate or None|iterable: input items' }),
  B('any', 'any(iterable) -> bool', 'True if any item is truthy (short-circuits); `False` for empty.', { params: 'iterable: items to test' }),
  B('all', 'all(iterable) -> bool', 'True if every item is truthy (short-circuits); `True` for empty.', { params: 'iterable: items to test' }),
  B('int', 'int(x=0, base=10) -> int', 'Convert to integer; truncates floats toward zero. `int("ff", 16)` parses other bases. Python ints are arbitrary precision (no overflow).', {
    params: 'x: number or string|base: base for string input' }),
  B('float', 'float(x=0.0) -> float', 'Convert to a 64-bit float. `float("inf")` is infinity. Floats are inexact: compare with tolerance.', { params: 'x: number or string' }),
  B('str', 'str(object="") -> str', 'String representation. Strings are **immutable**; build with a list and `"".join`.', { params: 'object: value to convert' }),
  B('list', 'list(iterable=()) -> list', 'New list from an iterable. Gotcha: `[[0] * m] * n` shares one row n times; use `[[0] * m for _ in range(n)]`.', { params: 'iterable: items' }),
  B('dict', 'dict(mapping_or_iterable=(), **kwargs) -> dict', 'New dict. Preserves insertion order. `dict(zip(keys, values))` pairs two lists.', { params: 'mapping_or_iterable: initial key/value pairs|**kwargs: extra keys' }),
  B('set', 'set(iterable=()) -> set', 'New mutable set (hash set: **O(1)** average add/lookup). `{}` is an empty **dict**, not a set: use `set()`.', { params: 'iterable: items' }),
  B('frozenset', 'frozenset(iterable=()) -> frozenset', 'Immutable, hashable set: usable as a dict key or set element.', { params: 'iterable: items' }),
  B('tuple', 'tuple(iterable=()) -> tuple', 'Immutable sequence; hashable if its items are, so usable as dict keys (e.g. `(r, c)`). One-element tuple needs a comma: `(x,)`.', { params: 'iterable: items' }),
  B('bool', 'bool(x=False) -> bool', 'Truth value of *x*.', { params: 'x: any value' }),
  B('ord', 'ord(c) -> int', 'Unicode code point of a one-character string: `ord("a") == 97`. `ord(c) - ord("a")` gives a letter index.', { params: 'c: single character' }),
  B('chr', 'chr(i) -> str', 'Character for a code point: `chr(97) == "a"`.', { params: 'i: code point' }),
  B('divmod', 'divmod(a, b) -> (q, r)', 'Return `(a // b, a % b)`. Floor division: `divmod(-7, 2) == (-4, 1)`.', { params: 'a: dividend|b: divisor' }),
  B('pow', 'pow(base, exp, mod=None) -> int', 'Power; with *mod* it does fast modular exponentiation (**O(log exp)**). `pow(a, -1, m)` is the modular inverse.', {
    params: 'base: base|exp: exponent|mod: optional modulus' }),
  B('round', 'round(number, ndigits=None) -> int | float', 'Round to *ndigits*. Gotcha: uses banker\'s rounding (`round(2.5) == 2`).', { params: 'number: value|ndigits: digits after the point' }),
  B('isinstance', 'isinstance(obj, classinfo) -> bool', 'Whether *obj* is an instance of a class (or of any class in a tuple).', { params: 'obj: value|classinfo: type or tuple of types' }),
  B('type', 'type(obj) -> type', 'The type of *obj*.', { params: 'obj: value' }),
  B('hash', 'hash(obj) -> int', 'Hash of a hashable object. Lists, dicts and sets are unhashable (use tuples / frozensets).', { params: 'obj: hashable value' }),
  B('id', 'id(obj) -> int', 'Unique identity of an object during its lifetime.', { params: 'obj: any value' }),
  B('iter', 'iter(obj) -> iterator', 'Get an iterator; pair with `next`.', { params: 'obj: iterable' }),
  B('next', 'next(iterator, default) -> item', 'Next item from an iterator; raises `StopIteration` when exhausted unless *default* is given. `next((x for x in a if p(x)), None)` finds the first match.', {
    params: 'iterator: iterator|default: returned when exhausted' }),
  B('bin', 'bin(x) -> str', 'Binary string with `0b` prefix: `bin(5) == "0b101"`. Count set bits with `x.bit_count()`.', { params: 'x: integer' }),
  B('hex', 'hex(x) -> str', 'Hex string with `0x` prefix.', { params: 'x: integer' }),
  B('oct', 'oct(x) -> str', 'Octal string with `0o` prefix.', { params: 'x: integer' }),
  B('format', 'format(value, format_spec="") -> str', 'Format one value: `format(x, ".2f")`, `format(n, "b")`, `format(n, "08b")`. f-strings use the same specs: `f"{x:.2f}"`.', {
    params: 'value: value to format|format_spec: format mini-language spec' }),
  B('repr', 'repr(obj) -> str', 'Unambiguous representation (strings get quotes).', { params: 'obj: any value' }),
  B('slice', 'slice(start, stop, step=None) -> slice', 'Slice object, as used by `a[start:stop:step]`.', { params: 'start: start index|stop: end index (exclusive)|step: step' }),
  B('getattr', 'getattr(obj, name, default) -> value', 'Attribute by name, with optional default.', { params: 'obj: object|name: attribute name|default: fallback' }),
  B('setattr', 'setattr(obj, name, value) -> None', 'Set an attribute by name.', { params: 'obj: object|name: attribute name|value: new value' }),
  B('hasattr', 'hasattr(obj, name) -> bool', 'Whether *obj* has attribute *name*.', { params: 'obj: object|name: attribute name' }),
  B('callable', 'callable(obj) -> bool', 'Whether *obj* can be called.', { params: 'obj: any value' }),
  B('open', 'open(file, mode="r") -> file', 'Open a file (rarely needed: use stdin).', { params: 'file: path|mode: "r", "w", ...' }),
  B('super', 'super() -> proxy', 'Access the parent class implementation, e.g. `super().__init__()`.'),
  B('object', 'object()', 'Base of all classes; `object()` makes a unique sentinel.'),
  e('type', null, 'complex', 'complex(real=0, imag=0)', 'Complex number; handy for 2D grid coordinates (`1j` rotates by 90°).'),
  e('constant', null, 'Ellipsis', '...', 'The `...` singleton; also a placeholder body.'),
  e('constant', null, '__name__', '__name__', 'Module name; `"__main__"` when run as a script.', { insert: '__name__' }),
  e('type', null, 'Exception', 'Exception(msg)', 'Base class for errors; common subclasses: `ValueError`, `KeyError`, `IndexError`, `TypeError`, `ZeroDivisionError`, `RecursionError`.'),

  // ===================== str methods =====================
  M('str', 'split', 'str.split(sep=None, maxsplit=-1) -> list[str]', 'Split into a list. With no *sep*, splits on runs of whitespace and drops empties; `"a,,b".split(",")` keeps the empty string.', {
    params: 'sep: delimiter (None = whitespace)|maxsplit: max number of splits', insert: 'split(${1})' }),
  M('str', 'join', 'str.join(iterable) -> str', 'Concatenate strings with this string as separator: `" ".join(map(str, nums))`. **O(total length)**; items must be strings.', {
    params: 'iterable: strings to join', insert: 'join(${1:iterable})' }),
  M('str', 'strip', 'str.strip(chars=None) -> str', 'Remove leading and trailing whitespace (or *chars*).', { params: 'chars: set of characters to remove' }),
  M('str', 'lstrip', 'str.lstrip(chars=None) -> str', 'Remove leading whitespace (or *chars*).', { params: 'chars: set of characters to remove' }),
  M('str', 'rstrip', 'str.rstrip(chars=None) -> str', 'Remove trailing whitespace (or *chars*), e.g. the newline from `sys.stdin.readline()`.', { params: 'chars: set of characters to remove' }),
  M('str', 'replace', 'str.replace(old, new, count=-1) -> str', 'Return a copy with *old* replaced by *new*.', { params: 'old: substring to find|new: replacement|count: max replacements' }),
  M('str', 'find', 'str.find(sub, start=0, end=len) -> int', 'Lowest index of *sub*, or **-1** if absent. **O(n·m)** worst case.', { params: 'sub: substring|start: search start|end: search end' }),
  M('str', 'rfind', 'str.rfind(sub, start=0, end=len) -> int', 'Highest index of *sub*, or -1.', { params: 'sub: substring|start: search start|end: search end' }),
  M('str', 'index', 'str.index(sub, start=0, end=len) -> int', 'Like `find` but raises `ValueError` when absent.', { params: 'sub: substring|start: search start|end: search end' }),
  M('str', 'count', 'str.count(sub, start=0, end=len) -> int', 'Number of non-overlapping occurrences of *sub*.', { params: 'sub: substring|start: search start|end: search end' }),
  M('str', 'startswith', 'str.startswith(prefix, start=0) -> bool', 'Whether the string starts with *prefix* (or any prefix in a tuple).', { params: 'prefix: string or tuple|start: position to test' }),
  M('str', 'endswith', 'str.endswith(suffix) -> bool', 'Whether the string ends with *suffix* (or any in a tuple).', { params: 'suffix: string or tuple' }),
  M('str', 'lower', 'str.lower() -> str', 'Lowercase copy.'),
  M('str', 'upper', 'str.upper() -> str', 'Uppercase copy.'),
  M('str', 'capitalize', 'str.capitalize() -> str', 'First character uppercase, the rest lowercase.'),
  M('str', 'title', 'str.title() -> str', 'Titlecase copy.'),
  M('str', 'swapcase', 'str.swapcase() -> str', 'Swap upper/lower case.'),
  M('str', 'isdigit', 'str.isdigit() -> bool', 'True if non-empty and all characters are digits.'),
  M('str', 'isalpha', 'str.isalpha() -> bool', 'True if non-empty and all characters are letters.'),
  M('str', 'isalnum', 'str.isalnum() -> bool', 'True if non-empty and all characters are letters or digits.'),
  M('str', 'isspace', 'str.isspace() -> bool', 'True if non-empty and all whitespace.'),
  M('str', 'islower', 'str.islower() -> bool', 'True if it has cased characters and all are lowercase.'),
  M('str', 'isupper', 'str.isupper() -> bool', 'True if it has cased characters and all are uppercase.'),
  M('str', 'zfill', 'str.zfill(width) -> str', 'Pad with zeros on the left: `"7".zfill(3) == "007"`.', { params: 'width: final length' }),
  M('str', 'center', 'str.center(width, fillchar=" ") -> str', 'Center in a field of *width*.', { params: 'width: final length|fillchar: padding character' }),
  M('str', 'ljust', 'str.ljust(width, fillchar=" ") -> str', 'Left-justify in a field of *width*.', { params: 'width: final length|fillchar: padding character' }),
  M('str', 'rjust', 'str.rjust(width, fillchar=" ") -> str', 'Right-justify in a field of *width*.', { params: 'width: final length|fillchar: padding character' }),
  M('str', 'partition', 'str.partition(sep) -> (head, sep, tail)', 'Split at the first *sep* into a 3-tuple.', { params: 'sep: separator' }),
  M('str', 'splitlines', 'str.splitlines(keepends=False) -> list[str]', 'Split on line boundaries.', { params: 'keepends: keep the newline characters' }),
  M('str', 'format', 'str.format(*args, **kwargs) -> str', 'Fill `{}` placeholders; f-strings (`f"{x}"`) are usually simpler.', { params: '*args: positional values|**kwargs: named values' }),
  M('str', 'encode', 'str.encode(encoding="utf-8") -> bytes', 'Encode to bytes.', { params: 'encoding: codec name' }),
  M('str', 'removeprefix', 'str.removeprefix(prefix) -> str', 'Remove *prefix* if present (3.9+).', { params: 'prefix: prefix to remove' }),
  M('str', 'removesuffix', 'str.removesuffix(suffix) -> str', 'Remove *suffix* if present (3.9+).', { params: 'suffix: suffix to remove' }),
  M('str', 'maketrans', 'str.maketrans(x, y) -> dict', 'Build a translation table for `translate`.', { params: 'x: characters to map|y: replacement characters' }),
  M('str', 'translate', 'str.translate(table) -> str', 'Map characters through a table from `str.maketrans`.', { params: 'table: translation table' }),

  // ===================== list methods =====================
  M('list', 'append', 'list.append(x) -> None', 'Add *x* at the end. **Amortized O(1)**. Returns None: don\'t write `a = a.append(x)`.', { params: 'x: item to add', insert: 'append(${1:x})' }),
  M('list', 'extend', 'list.extend(iterable) -> None', 'Append every item of *iterable*.', { params: 'iterable: items to add' }),
  M('list', 'insert', 'list.insert(i, x) -> None', 'Insert *x* before index *i*. **O(n)**; for queues use `collections.deque`.', { params: 'i: index|x: item' }),
  M('list', 'pop', 'list.pop(i=-1) -> item', 'Remove and return the item at *i* (default last). `pop()` is O(1); **`pop(0)` is O(n)**: use `deque.popleft()`.', { params: 'i: index (default last)' }),
  M('list', 'remove', 'list.remove(x) -> None', 'Remove the first item equal to *x*; **O(n)**; `ValueError` if absent.', { params: 'x: value to remove' }),
  M('list', 'index', 'list.index(x, start=0, end=len) -> int', 'Index of the first item equal to *x*; **O(n)**; `ValueError` if absent.', { params: 'x: value|start: search start|end: search end' }),
  M('list', 'count', 'list.count(x) -> int', 'Number of items equal to *x*; **O(n)**.', { params: 'x: value' }),
  M('list', 'sort', 'list.sort(*, key=None, reverse=False) -> None', 'Sort **in place** (stable, O(n log n)) and return **None** — `a = a.sort()` loses the list; use `sorted(a)` for a copy.', {
    params: 'key: function computing the sort key|reverse: descending if True' }),
  M('list', 'reverse', 'list.reverse() -> None', 'Reverse in place; returns None. `a[::-1]` makes a reversed copy.'),
  M('list', 'copy', 'list.copy() -> list', 'Shallow copy (same as `a[:]`). Nested lists are still shared; use `[row[:] for row in grid]`.'),
  M('list', 'clear', 'list.clear() -> None', 'Remove all items.'),

  // ===================== dict methods =====================
  M('dict', 'get', 'dict.get(key, default=None) -> value', 'Value for *key*, or *default* if missing (no `KeyError`, no insertion). `d[k] = d.get(k, 0) + 1` counts.', {
    params: 'key: key to look up|default: returned if missing', insert: 'get(${1:key}, ${2:0})' }),
  M('dict', 'keys', 'dict.keys() -> dict_keys', 'Live view of the keys (insertion order).'),
  M('dict', 'values', 'dict.values() -> dict_values', 'Live view of the values.'),
  M('dict', 'items', 'dict.items() -> dict_items', 'Live view of `(key, value)` pairs: `for k, v in d.items():`. Don\'t add/remove keys while iterating.'),
  M('dict', 'setdefault', 'dict.setdefault(key, default=None) -> value', 'Return `d[key]`, inserting *default* first if missing: `d.setdefault(k, []).append(v)`.', { params: 'key: key|default: value inserted if missing' }),
  M('dict', 'pop', 'dict.pop(key, default) -> value', 'Remove *key* and return its value; `KeyError` if missing and no *default*.', { params: 'key: key to remove|default: returned if missing' }),
  M('dict', 'popitem', 'dict.popitem() -> (key, value)', 'Remove and return the **last** inserted pair (LIFO).'),
  M('dict', 'update', 'dict.update(other) -> None', 'Merge keys from *other* (dict or pairs), overwriting. `d1 | d2` makes a merged copy.', { params: 'other: mapping or iterable of pairs' }),
  M('dict', 'fromkeys', 'dict.fromkeys(iterable, value=None) -> dict', 'New dict with every key mapped to *value*. Gotcha: a mutable *value* is shared by all keys.', { params: 'iterable: keys|value: shared value' }),
  M('dict', 'copy', 'dict.copy() -> dict', 'Shallow copy.'),
  M('dict', 'clear', 'dict.clear() -> None', 'Remove all items.'),

  // ===================== set methods =====================
  M('set', 'add', 'set.add(x) -> None', 'Add *x*. **O(1)** average.', { params: 'x: hashable item' }),
  M('set', 'remove', 'set.remove(x) -> None', 'Remove *x*; raises `KeyError` if absent (use `discard` to ignore).', { params: 'x: item' }),
  M('set', 'discard', 'set.discard(x) -> None', 'Remove *x* if present; no error otherwise.', { params: 'x: item' }),
  M('set', 'pop', 'set.pop() -> item', 'Remove and return an arbitrary item; `KeyError` if empty.'),
  M('set', 'union', 'set.union(*others) -> set', 'New set with items from all sets (`a | b`).', { params: '*others: iterables' }),
  M('set', 'intersection', 'set.intersection(*others) -> set', 'Items common to all (`a & b`).', { params: '*others: iterables' }),
  M('set', 'difference', 'set.difference(*others) -> set', 'Items in this set but not the others (`a - b`).', { params: '*others: iterables' }),
  M('set', 'symmetric_difference', 'set.symmetric_difference(other) -> set', 'Items in exactly one of the sets (`a ^ b`).', { params: 'other: iterable' }),
  M('set', 'issubset', 'set.issubset(other) -> bool', 'Whether every item is in *other* (`a <= b`).', { params: 'other: iterable' }),
  M('set', 'issuperset', 'set.issuperset(other) -> bool', 'Whether *other* is contained in this set (`a >= b`).', { params: 'other: iterable' }),
  M('set', 'isdisjoint', 'set.isdisjoint(other) -> bool', 'True if there are no common items.', { params: 'other: iterable' }),
  M('set', 'update', 'set.update(*others) -> None', 'Add all items from *others* (`a |= b`).', { params: '*others: iterables' }),
  M('set', 'intersection_update', 'set.intersection_update(*others) -> None', 'Keep only items also in *others* (`a &= b`).', { params: '*others: iterables' }),
  M('set', 'difference_update', 'set.difference_update(*others) -> None', 'Remove items found in *others* (`a -= b`).', { params: '*others: iterables' }),
  M('set', 'copy', 'set.copy() -> set', 'Shallow copy.'),
  M('set', 'clear', 'set.clear() -> None', 'Remove all items.'),

  // ===================== int methods =====================
  M('int', 'bit_count', 'int.bit_count() -> int', 'Number of 1 bits (popcount) of `abs(n)` (3.10+).'),
  M('int', 'bit_length', 'int.bit_length() -> int', 'Bits needed to represent `abs(n)`: `(8).bit_length() == 4`; `n.bit_length() - 1` is floor(log2 n).'),

  // ===================== collections =====================
  F('collections', 'Counter', 'Counter(iterable_or_mapping=None) -> Counter', 'Dict subclass counting hashable items; missing keys read as **0** (no KeyError). Counters support `+`, `-`, `&`, `|` and `==`.', {
    params: 'iterable_or_mapping: items to count', example: 'from collections import Counter\nc = Counter("banana")\nc["a"]  # 3', header: 'from collections import Counter' }),
  M('Counter', 'most_common', 'Counter.most_common(n=None) -> list[tuple]', 'The *n* most frequent `(item, count)` pairs, highest first (ties in insertion order). **O(n log k)** with *n*.', {
    params: 'n: how many (None = all)', header: 'from collections import Counter' }),
  M('Counter', 'elements', 'Counter.elements() -> iterator', 'Iterate over items, each repeated as many times as its count (counts ≤ 0 skipped).', { header: 'from collections import Counter' }),
  M('Counter', 'update', 'Counter.update(iterable_or_mapping) -> None', '**Add** counts (unlike `dict.update`, which replaces).', { params: 'iterable_or_mapping: items to count', header: 'from collections import Counter' }),
  M('Counter', 'subtract', 'Counter.subtract(iterable_or_mapping) -> None', 'Subtract counts in place; results may go negative or zero (keys are kept).', { params: 'iterable_or_mapping: items to subtract', header: 'from collections import Counter' }),
  M('Counter', 'total', 'Counter.total() -> int', 'Sum of all counts (3.10+).', { header: 'from collections import Counter' }),
  F('collections', 'defaultdict', 'defaultdict(default_factory) -> defaultdict', 'Dict that creates missing values with `default_factory()` on access: `defaultdict(list)` for adjacency lists, `defaultdict(int)` for counts. Gotcha: even **reading** a missing key inserts it; use `in` to test.', {
    params: 'default_factory: zero-arg callable like list, int, set', example: 'g = defaultdict(list)\nfor u, v in edges:\n    g[u].append(v)\n    g[v].append(u)', header: 'from collections import defaultdict', insert: 'defaultdict(${1:list})' }),
  F('collections', 'deque', 'deque(iterable=(), maxlen=None) -> deque', 'Double-ended queue: **O(1)** append/pop at both ends — the right choice for BFS queues. Indexing in the middle is O(n). With *maxlen*, old items fall off the other end.', {
    params: 'iterable: initial items|maxlen: optional maximum length', example: 'q = deque([start])\nwhile q:\n    node = q.popleft()', header: 'from collections import deque' }),
  M('deque', 'append', 'deque.append(x) -> None', 'Add to the right end. O(1).', { params: 'x: item', header: 'from collections import deque' }),
  M('deque', 'appendleft', 'deque.appendleft(x) -> None', 'Add to the left end. O(1).', { params: 'x: item', header: 'from collections import deque' }),
  M('deque', 'pop', 'deque.pop() -> item', 'Remove and return the rightmost item. O(1). `IndexError` if empty.', { header: 'from collections import deque' }),
  M('deque', 'popleft', 'deque.popleft() -> item', 'Remove and return the leftmost item. **O(1)** (vs `list.pop(0)` O(n)). `IndexError` if empty.', { header: 'from collections import deque' }),
  M('deque', 'extend', 'deque.extend(iterable) -> None', 'Append items on the right.', { params: 'iterable: items', header: 'from collections import deque' }),
  M('deque', 'extendleft', 'deque.extendleft(iterable) -> None', 'Append items on the left — note the order ends up **reversed**.', { params: 'iterable: items', header: 'from collections import deque' }),
  M('deque', 'rotate', 'deque.rotate(n=1) -> None', 'Rotate right by *n* steps (left if negative).', { params: 'n: steps', header: 'from collections import deque' }),
  M('deque', 'clear', 'deque.clear() -> None', 'Remove all items.', { header: 'from collections import deque' }),
  M('deque', 'count', 'deque.count(x) -> int', 'Number of items equal to *x*. O(n).', { params: 'x: value', header: 'from collections import deque' }),
  M('deque', 'remove', 'deque.remove(value) -> None', 'Remove the first occurrence. O(n).', { params: 'value: value', header: 'from collections import deque' }),
  M('deque', 'index', 'deque.index(x) -> int', 'Index of first occurrence. O(n).', { params: 'x: value', header: 'from collections import deque' }),
  M('deque', 'reverse', 'deque.reverse() -> None', 'Reverse in place.', { header: 'from collections import deque' }),
  F('collections', 'OrderedDict', 'OrderedDict(items=()) -> OrderedDict', 'Dict with order-manipulation methods (`move_to_end`, `popitem(last=False)`) — the classic LRU cache building block.', {
    params: 'items: initial pairs', header: 'from collections import OrderedDict' }),
  M('OrderedDict', 'move_to_end', 'OrderedDict.move_to_end(key, last=True) -> None', 'Move *key* to the end (or the front with `last=False`). O(1).', { params: 'key: existing key|last: True = end, False = front', header: 'from collections import OrderedDict' }),
  M('OrderedDict', 'popitem', 'OrderedDict.popitem(last=True) -> (key, value)', 'Pop the last pair, or the first with `last=False` (evict the least-recently-used).', { params: 'last: True = last, False = first', header: 'from collections import OrderedDict' }),
  F('collections', 'namedtuple', 'namedtuple(typename, field_names) -> type', 'Tuple subclass with named fields: `P = namedtuple("P", "x y")`.', { params: 'typename: class name|field_names: "x y" or list', header: 'from collections import namedtuple' }),

  // ===================== heapq =====================
  F('heapq', 'heappush', 'heapq.heappush(heap, item) -> None', 'Push *item*, keeping the **min**-heap invariant. **O(log n)**. For a max-heap push `-x`; push tuples `(priority, tiebreak, item)` to avoid comparing uncomparable items.', {
    params: 'heap: a list maintained as a min-heap|item: value to push', example: 'h = []\nheapq.heappush(h, (dist, node))', insert: 'heappush(${1:heap}, ${2:item})' }),
  F('heapq', 'heappop', 'heapq.heappop(heap) -> item', 'Pop and return the smallest item. **O(log n)**. `IndexError` if empty. `heap[0]` peeks without popping.', { params: 'heap: min-heap list', insert: 'heappop(${1:heap})' }),
  F('heapq', 'heapify', 'heapq.heapify(x) -> None', 'Turn a list into a min-heap **in place** in **O(n)**.', { params: 'x: list to heapify' }),
  F('heapq', 'heappushpop', 'heapq.heappushpop(heap, item) -> item', 'Push then pop the smallest, faster than separate calls; keeps a size-k heap of the k largest.', { params: 'heap: min-heap list|item: value to push' }),
  F('heapq', 'heapreplace', 'heapq.heapreplace(heap, item) -> item', 'Pop the smallest, then push *item* (heap must be non-empty).', { params: 'heap: min-heap list|item: value to push' }),
  F('heapq', 'nlargest', 'heapq.nlargest(n, iterable, key=None) -> list', 'The *n* largest items, descending. **O(m log n)**.', { params: 'n: how many|iterable: items|key: key function' }),
  F('heapq', 'nsmallest', 'heapq.nsmallest(n, iterable, key=None) -> list', 'The *n* smallest items, ascending.', { params: 'n: how many|iterable: items|key: key function' }),
  F('heapq', 'merge', 'heapq.merge(*iterables, key=None, reverse=False) -> iterator', 'Lazily merge already-sorted iterables.', { params: '*iterables: sorted inputs|key: key function|reverse: inputs sorted descending' }),

  // ===================== bisect =====================
  F('bisect', 'bisect_left', 'bisect.bisect_left(a, x, lo=0, hi=len(a), *, key=None) -> int', 'First index where *x* could be inserted keeping *a* sorted (index of first item **≥ x**). **O(log n)**. *a* must be sorted.', {
    params: 'a: sorted list|x: value|lo: lower bound|hi: upper bound|key: key function (3.10+)', example: 'i = bisect_left(a, x)\nfound = i < len(a) and a[i] == x' }),
  F('bisect', 'bisect_right', 'bisect.bisect_right(a, x, lo=0, hi=len(a), *, key=None) -> int', 'Insertion index after any existing *x* (index of first item **> x**). `bisect_right(a, x) - bisect_left(a, x)` counts occurrences. Alias: `bisect.bisect`.', {
    params: 'a: sorted list|x: value|lo: lower bound|hi: upper bound|key: key function (3.10+)' }),
  F('bisect', 'bisect', 'bisect.bisect(a, x, lo=0, hi=len(a)) -> int', 'Alias of `bisect_right`.', { params: 'a: sorted list|x: value|lo: lower bound|hi: upper bound' }),
  F('bisect', 'insort', 'bisect.insort(a, x, lo=0, hi=len(a)) -> None', 'Insert *x* keeping *a* sorted. Search is O(log n) but the insert is **O(n)**.', { params: 'a: sorted list|x: value|lo: lower bound|hi: upper bound' }),
  F('bisect', 'insort_left', 'bisect.insort_left(a, x) -> None', 'Insert *x* before any equal items. O(n).', { params: 'a: sorted list|x: value' }),

  // ===================== math =====================
  F('math', 'gcd', 'math.gcd(*integers) -> int', 'Greatest common divisor (any number of args since 3.9); `gcd(0, 0) == 0`.', { params: '*integers: integers' }),
  F('math', 'lcm', 'math.lcm(*integers) -> int', 'Least common multiple (3.9+).', { params: '*integers: integers' }),
  F('math', 'isqrt', 'math.isqrt(n) -> int', 'Exact integer square root `floor(sqrt(n))` — use this instead of `int(math.sqrt(n))`, which is wrong for large n.', { params: 'n: non-negative int' }),
  F('math', 'sqrt', 'math.sqrt(x) -> float', 'Float square root; `ValueError` for negatives.', { params: 'x: number' }),
  F('math', 'floor', 'math.floor(x) -> int', 'Largest int ≤ *x*. For ints prefer `//`.', { params: 'x: number' }),
  F('math', 'ceil', 'math.ceil(x) -> int', 'Smallest int ≥ *x*. For ints prefer `-(-a // b)` to avoid float error.', { params: 'x: number' }),
  F('math', 'comb', 'math.comb(n, k) -> int', 'Binomial coefficient n choose k (exact; 0 if k > n).', { params: 'n: total|k: chosen' }),
  F('math', 'perm', 'math.perm(n, k=None) -> int', 'Number of ordered arrangements n!/(n-k)!.', { params: 'n: total|k: chosen (default n)' }),
  F('math', 'factorial', 'math.factorial(n) -> int', 'n! (exact big int).', { params: 'n: non-negative int' }),
  F('math', 'log', 'math.log(x, base=e) -> float', 'Logarithm (natural by default).', { params: 'x: positive number|base: base' }),
  F('math', 'log2', 'math.log2(x) -> float', 'Base-2 logarithm. For exact int results use `n.bit_length() - 1`.', { params: 'x: positive number' }),
  F('math', 'log10', 'math.log10(x) -> float', 'Base-10 logarithm.', { params: 'x: positive number' }),
  F('math', 'exp', 'math.exp(x) -> float', 'e ** x.', { params: 'x: exponent' }),
  F('math', 'pow', 'math.pow(x, y) -> float', 'Float power; for ints use `**` or builtin `pow` (exact).', { params: 'x: base|y: exponent' }),
  F('math', 'fabs', 'math.fabs(x) -> float', 'Float absolute value.', { params: 'x: number' }),
  F('math', 'hypot', 'math.hypot(*coordinates) -> float', 'Euclidean distance from origin: `hypot(dx, dy)`.', { params: '*coordinates: numbers' }),
  F('math', 'dist', 'math.dist(p, q) -> float', 'Euclidean distance between two points.', { params: 'p: point|q: point' }),
  F('math', 'prod', 'math.prod(iterable, start=1) -> number', 'Product of all items.', { params: 'iterable: numbers|start: initial value' }),
  F('math', 'isclose', 'math.isclose(a, b, rel_tol=1e-09, abs_tol=0.0) -> bool', 'Float comparison with tolerance.', { params: 'a: number|b: number|rel_tol: relative tolerance|abs_tol: absolute tolerance' }),
  F('math', 'trunc', 'math.trunc(x) -> int', 'Truncate toward zero.', { params: 'x: number' }),
  F('math', 'sin', 'math.sin(x) -> float', 'Sine of *x* radians.', { params: 'x: radians' }),
  F('math', 'cos', 'math.cos(x) -> float', 'Cosine of *x* radians.', { params: 'x: radians' }),
  F('math', 'atan2', 'math.atan2(y, x) -> float', 'Angle of the point (x, y) in radians, in (-π, π].', { params: 'y: y coordinate|x: x coordinate' }),
  F('math', 'isinf', 'math.isinf(x) -> bool', 'Whether *x* is ±infinity.', { params: 'x: number' }),
  e('constant', 'math', 'inf', 'math.inf', 'Positive float infinity (`float("inf")`); handy initial value for minimums.', { header: 'import math' }),
  e('constant', 'math', 'pi', 'math.pi', 'π = 3.141592653589793.', { header: 'import math' }),
  e('constant', 'math', 'e', 'math.e', 'e = 2.718281828459045.', { header: 'import math' }),

  // ===================== itertools =====================
  F('itertools', 'permutations', 'itertools.permutations(iterable, r=None) -> iterator', 'All r-length orderings as tuples (n!/(n-r)! of them — explodes fast). Items are treated as distinct by position.', { params: 'iterable: items|r: length (default all)' }),
  F('itertools', 'combinations', 'itertools.combinations(iterable, r) -> iterator', 'All r-length subsets as tuples, in input order (C(n, r) of them).', { params: 'iterable: items|r: subset size' }),
  F('itertools', 'combinations_with_replacement', 'itertools.combinations_with_replacement(iterable, r) -> iterator', 'r-length combinations allowing repeated items.', { params: 'iterable: items|r: size' }),
  F('itertools', 'product', 'itertools.product(*iterables, repeat=1) -> iterator', 'Cartesian product, like nested loops: `product("01", repeat=n)` gives all bit strings.', { params: '*iterables: input iterables|repeat: repeat the inputs' }),
  F('itertools', 'accumulate', 'itertools.accumulate(iterable, func=operator.add, *, initial=None) -> iterator', 'Running totals (prefix sums): `list(accumulate(a, initial=0))` has length n+1. *func* can be `max` for running max.', {
    params: 'iterable: values|func: binary function|initial: value emitted first' }),
  F('itertools', 'groupby', 'itertools.groupby(iterable, key=None) -> iterator', 'Group **consecutive** equal-key items into `(key, group_iter)`. Sort first to group globally. Run-length encoding: `[(k, len(list(g))) for k, g in groupby(s)]`.', {
    params: 'iterable: items|key: key function' }),
  F('itertools', 'chain', 'itertools.chain(*iterables) -> iterator', 'Iterate the inputs one after another. `chain.from_iterable(lists)` flattens one level.', { params: '*iterables: iterables to concatenate' }),
  F('itertools', 'count', 'itertools.count(start=0, step=1) -> iterator', 'Infinite counter.', { params: 'start: first value|step: increment' }),
  F('itertools', 'cycle', 'itertools.cycle(iterable) -> iterator', 'Repeat the items forever.', { params: 'iterable: items' }),
  F('itertools', 'repeat', 'itertools.repeat(object, times=None) -> iterator', 'Yield *object* repeatedly (forever if *times* is None).', { params: 'object: value|times: count' }),
  F('itertools', 'islice', 'itertools.islice(iterable, stop) / islice(iterable, start, stop, step=1) -> iterator', 'Slice any iterator lazily.', { params: 'iterable: items|start: start index|stop: end index|step: step' }),
  F('itertools', 'pairwise', 'itertools.pairwise(iterable) -> iterator', 'Consecutive pairs `(a[0], a[1]), (a[1], a[2]), ...` (3.10+).', { params: 'iterable: items' }),
  F('itertools', 'zip_longest', 'itertools.zip_longest(*iterables, fillvalue=None) -> iterator', 'Like `zip` but runs to the longest input, padding with *fillvalue*.', { params: '*iterables: inputs|fillvalue: padding value' }),
  F('itertools', 'starmap', 'itertools.starmap(function, iterable) -> iterator', 'Call *function* with each tuple unpacked as arguments.', { params: 'function: callable|iterable: tuples of args' }),
  F('itertools', 'takewhile', 'itertools.takewhile(predicate, iterable) -> iterator', 'Yield items while *predicate* is true.', { params: 'predicate: test|iterable: items' }),
  F('itertools', 'dropwhile', 'itertools.dropwhile(predicate, iterable) -> iterator', 'Skip items while *predicate* is true, then yield the rest.', { params: 'predicate: test|iterable: items' }),

  // ===================== functools =====================
  F('functools', 'lru_cache', '@functools.lru_cache(maxsize=128)', 'Memoize a function by its (hashable) arguments. Use `@lru_cache(maxsize=None)` (or `@cache`) for DP; the default 128 evicts entries. Deep recursion still needs `sys.setrecursionlimit`.', {
    params: 'maxsize: cache size, None = unbounded', example: '@lru_cache(maxsize=None)\ndef dp(i, j):\n    ...', insert: 'lru_cache(maxsize=None)', header: 'from functools import lru_cache' }),
  F('functools', 'cache', '@functools.cache', 'Unbounded memoization (3.9+), same as `lru_cache(maxsize=None)`. Arguments must be hashable (convert lists to tuples). Clear with `f.cache_clear()` between test cases.', {
    example: '@cache\ndef fib(n):\n    return n if n < 2 else fib(n - 1) + fib(n - 2)', header: 'from functools import cache' }),
  F('functools', 'reduce', 'functools.reduce(function, iterable, initial) -> value', 'Fold *iterable* into one value with a two-argument *function*. `TypeError` on empty input without *initial*.', {
    params: 'function: f(acc, item)|iterable: items|initial: starting accumulator', header: 'from functools import reduce' }),
  F('functools', 'cmp_to_key', 'functools.cmp_to_key(func) -> key', 'Turn an old-style comparator (negative/0/positive) into a `key=` for sorting, e.g. "largest number" concatenation order.', {
    params: 'func: cmp(a, b) -> int', example: 'nums.sort(key=cmp_to_key(lambda a, b: (b + a > a + b) - (b + a < a + b)))', header: 'from functools import cmp_to_key' }),
  F('functools', 'partial', 'functools.partial(func, *args, **kwargs) -> callable', 'Pre-fill some arguments of *func*.', { params: 'func: callable|*args: fixed positional args|**kwargs: fixed keyword args' }),

  // ===================== sys =====================
  F('sys', 'setrecursionlimit', 'sys.setrecursionlimit(limit) -> None', 'Raise the recursion limit (default **1000**) for deep DFS/memoized recursion. In the browser (Pyodide) the real stack is smaller, so very deep recursion can still crash — prefer iteration.', {
    params: 'limit: new maximum depth', example: 'import sys\nsys.setrecursionlimit(10**6)' }),
  e('function', 'sys.stdin', 'readline', 'sys.stdin.readline() -> str', 'Read one line **including** the trailing `\\n` (strip it). Much faster than `input()` for big inputs; returns `""` at EOF.', {
    example: 'import sys\ninput = sys.stdin.readline\nn = int(input())', header: 'import sys' }),
  e('function', 'sys.stdin', 'read', 'sys.stdin.read() -> str', 'Read all remaining input at once; `sys.stdin.read().split()` tokenizes everything.', { header: 'import sys' }),
  e('constant', 'sys', 'maxsize', 'sys.maxsize', 'Largest list index (2**63 - 1). Python ints are unbounded; `math.inf` is often a better sentinel.', { header: 'import sys' }),
  e('constant', 'sys', 'stdin', 'sys.stdin', 'Standard input stream (`readline`, `read`, iterate over lines).', { header: 'import sys' }),
  e('constant', 'sys', 'stdout', 'sys.stdout', 'Standard output stream; `sys.stdout.write(s)` writes without a newline.', { header: 'import sys' }),

  // ===================== typing =====================
  e('type', 'typing', 'List', 'List[T]', 'Type hint for a list (3.9+: plain `list[int]` works too).', { header: 'from typing import List' }),
  e('type', 'typing', 'Optional', 'Optional[T]', 'Type hint meaning `T | None`.', { header: 'from typing import Optional' }),
  e('type', 'typing', 'Dict', 'Dict[K, V]', 'Type hint for a dict (or plain `dict[K, V]`).', { header: 'from typing import Dict' }),
  e('type', 'typing', 'Tuple', 'Tuple[T, ...]', 'Type hint for a tuple (or plain `tuple[int, int]`).', { header: 'from typing import Tuple' }),
  e('type', 'typing', 'Set', 'Set[T]', 'Type hint for a set (or plain `set[int]`).', { header: 'from typing import Set' }),

  // ===================== modules =====================
  e('module', null, 'collections', 'import collections', 'Container datatypes: `Counter`, `defaultdict`, `deque`, `OrderedDict`, `namedtuple`.'),
  e('module', null, 'heapq', 'import heapq', 'Binary **min**-heap functions operating on plain lists.'),
  e('module', null, 'bisect', 'import bisect', 'Binary search / insertion on sorted lists.'),
  e('module', null, 'math', 'import math', 'Math functions: `gcd`, `isqrt`, `comb`, `inf`, `log2`, ...'),
  e('module', null, 'itertools', 'import itertools', 'Iterator building blocks: `permutations`, `combinations`, `product`, `accumulate`, `groupby`, `chain`.'),
  e('module', null, 'functools', 'import functools', 'Higher-order helpers: `cache`, `lru_cache`, `reduce`, `cmp_to_key`.'),
  e('module', null, 'sys', 'import sys', 'Interpreter access: `sys.stdin`, `sys.setrecursionlimit`, `sys.maxsize`.'),
  e('module', null, 'typing', 'from typing import List, Optional', 'Type-hint helpers.'),
];
