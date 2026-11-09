"""Track 4: Strings. Storage models per language, scanning, counting, building output."""

import random
import string

TRACK = dict(
    id="strings",
    title="Strings",
    order=4,
    icon="❝",
    blurb="Text as data: how each language stores strings, and the scanning, counting and building patterns that work on them.",
    intro=r"""
A string looks like the simplest data type there is, yet it is where languages differ the most.
Python hides almost everything, C hides almost nothing, and Rust makes you choose. Before the
algorithms, it pays to know what a string *is* in each language, because most string bugs are
really storage bugs.

## What a string is, language by language

**Python `str`**: an immutable sequence of Unicode characters. `s[i]` gives a one-character
string, `len(s)` is O(1), and *every* "modification" creates a new string:

```python
s = "cat"
t = s.upper()        # new string "CAT"; s is unchanged
s[0] = "b"           # TypeError: 'str' object does not support item assignment
```

Because strings are immutable, building one with `+=` in a loop can copy the whole string on
each step (O(n²) in the worst case). The idiom is to collect pieces in a list and `"".join(...)`
them once at the end.

**C `char*`**: there is no string type, only an array of bytes ending with a zero byte, the
**NUL terminator** `'\0'`:

```
 "cat"  in memory:   'c'  'a'  't'  '\0'
                      0    1    2    3      <- 4 bytes for a 3-character string
```

Consequences you must internalise:

- `strlen(s)` *walks* the bytes until it finds `'\0'`: it is O(n). Call it once, store the result,
  and never write `for (i = 0; i < strlen(s); i++)`.
- Allocating a string of length `n` needs `n + 1` bytes. Forgetting the `+ 1` is the most
  common C string bug; it "works" until it corrupts memory.
- To **return** a new string you must `malloc` it (a local array dies when the function returns),
  fill it, and write the terminator yourself. In Crucible the caller frees it.
- Character tests live in `<ctype.h>`: `isalpha`, `isdigit`, `isalnum`, `isspace`, `tolower`,
  `toupper`. Pass them `(unsigned char)c`; a negative `char` is undefined behaviour.
- A `char` is a small integer: `'a' + 1 == 'b'`, `c - '0'` turns a digit character into its value,
  and `c - 'a'` turns a lowercase letter into `0..25`, the perfect index into a count array.

```c
char* copy = malloc(len + 1);   // +1 for the terminator
memcpy(copy, s, len);
copy[len] = '\0';
```

**C++ `std::string`**: a growable, mutable byte buffer that manages its own memory. `s.size()` is
O(1), `s[i]` is a `char&` you can assign to, `s += c` and `s.push_back(c)` are amortised O(1),
and `std::reverse(s.begin(), s.end())` works in place. Strings are passed by value unless you write
`string&` or `const string&`, so be aware of accidental copies. `s.c_str()` gives a C-style
pointer when you need one.

**Rust `String` and `&str`**: `String` is an owned, growable, **UTF-8** buffer; `&str` is a
borrowed view into one (string literals are `&'static str`). Rust refuses `s[i]`, because in UTF-8
a "character" can be 1 to 4 bytes and indexing by byte could split one in half. You choose the view
explicitly:

```rust
let s = String::from("hello");
let bytes = s.as_bytes();       // &[u8]: O(1) indexing, perfect for ASCII problems
let first = bytes[0];           // b'h' (a u8)
for c in s.chars() { /* Unicode scalar values */ }
let t: String = s.chars().rev().collect();   // build a new String from chars
let mut out = String::new();
out.push('x');                  // append a char
out.push_str("yz");             // append a &str
```

`s.len()` is the number of **bytes**, not characters. For pure ASCII they coincide, which is why
every problem in this track promises ASCII input. To build output byte by byte, collect a
`Vec<u8>` and finish with `String::from_utf8(v).unwrap()`.

## Bytes vs characters

ASCII assigns the numbers 0–127 to English letters, digits, punctuation and control codes. In ASCII
one character is one byte, so "length", "index" and "character" all mean the same thing. Outside
ASCII (é, 漢, emoji) that breaks: UTF-8 uses multiple bytes per character, Python counts code
points, C counts bytes, and none of them count what a human would call letters. Real-world code
has to care. Crucible's string problems say "ASCII" so that you can concentrate on algorithms;
just remember the simplification is there.

Useful ASCII facts:

| range | characters | trick |
|---|---|---|
| 48–57 | `'0'`–`'9'` | `c - '0'` is the digit value |
| 65–90 | `'A'`–`'Z'` | `c - 'A'` is 0–25 |
| 97–122 | `'a'`–`'z'` | lowercase = uppercase + 32 |
| 32 | space | |

## The patterns

Nearly every string problem is built from a few moves:

1. **Scan**: one pass left to right, looking at each character once (counting vowels, finding the
   first digit, parsing a number).
2. **Two pointers**: one index from each end moving inward (reversal, palindrome check), or two
   indices walking two strings at different speeds (subsequence check, merging).
3. **Count table**: for a fixed small alphabet, an array of 26 (or 128) counters beats a hash map.
   Anagrams, "first unique character", and "can I build this from those letters" are all count
   tables.
4. **Run detection**: group consecutive equal characters (compression, count-and-say). Keep the
   start of the current run and emit it when the character changes, and *don't forget the last run*
   after the loop.
5. **Sliding window**: a range `[left, right)` that grows on the right and shrinks on the left
   while maintaining some property ("no repeated characters"), giving O(n) instead of checking all
   O(n²) substrings.
6. **Build, don't mutate**: assemble output in a list/`String`/buffer and convert once.

## Complexity

A single scan is O(n). Comparing two strings is O(min length), not O(1), which matters if you do
it inside a loop. Slicing in Python (`s[i:j]`) *copies* `j − i` characters. Concatenating in a loop
can be quadratic in Python and C (where `strcat` rescans to find the end every time). When a
solution feels slow, look for hidden O(n) work inside an O(n) loop.
""",
)


def _rng(seed):
    return random.Random(seed)


def _rand_str(r, n, alphabet):
    return "".join(r.choice(alphabet) for _ in range(n))


PRINTABLE = string.ascii_letters + string.digits + " .,;:!?-_()[]'\"#@$%&*+=/<>"

PROBLEMS = []

# ================================================================ 1. reverse string
_r = _rng(401)
PROBLEMS.append(dict(
    id="reverse-string-ascii",
    title="Reverse a String",
    difficulty=1,
    tags=["string", "two pointers"],
    fn="reverse_string",
    params=[["s", "str"]],
    returns="str",
    statement=r"""
Return the string `s` written backwards.

`s` consists of printable ASCII characters (letters, digits, spaces, punctuation) and may be
empty.
""",
    constraints=["0 ≤ len(s) ≤ 10⁴", "`s` is printable ASCII"],
    example_notes=["Each character moves to its mirror position: h…o becomes o…h.", "The empty string reversed is still empty."],
    hints=[
        "The first character of the answer is the last character of `s`. Walk the input backwards, or walk two indices toward each other.",
        "In Python, strings are immutable: build a list of characters and `\"\".join` it, or use slicing.",
        "In C, allocate `len + 1` bytes; the extra byte holds the `'\\0'` terminator.",
    ],
    explanation=r"""
## Intuition

Reversal pairs position `i` with position `n − 1 − i`. You can either **read backwards** into a new
buffer, or **swap from both ends** toward the middle (two pointers). Both are a single O(n) pass.

## Approach

Two-pointer swap on a mutable copy:

```
chars = list(s)
i, j = 0, n - 1
while i < j:
    swap chars[i], chars[j]
    i += 1; j -= 1
```

Trace for `"abc d"` (n = 5):

| i | j | chars |
|---|---|---|
| 0 | 4 | `a b c _ d` → swap → `d b c _ a` |
| 1 | 3 | `d b c _ a` → swap → `d _ c b a` |
| 2 | 2 | stop (i == j: the middle stays put) |

Result `"d cba"`.

**Language mechanics.**

- Python: `s[::-1]` is a slice with step −1; it's idiomatic and fast. Writing the loop yourself
  teaches why it works.
- C: the input is a pointer to bytes ending in `'\0'`. Get `n = strlen(s)` *once*,
  `malloc(n + 1)`, fill `out[i] = s[n - 1 - i]`, and set `out[n] = '\0'`.
- C++: `string` is mutable, so `reverse(s.begin(), s.end())` on the by-value parameter and return
  it.
- Rust: `s.chars().rev().collect::<String>()`. For ASCII you could also reverse the bytes, but
  `chars()` is correct for any UTF-8 (reversing raw bytes of a multi-byte character produces invalid
  UTF-8).

## Complexity

- **Time:** O(n).
- **Space:** O(n) for the output (unavoidable: strings are immutable in Python and we return a new
  one in C).

## Common mistakes

- C: `malloc(n)` with no room for the terminator, or forgetting to write it. The string then
  "continues" into whatever bytes follow.
- C: returning a pointer to a local array (`char out[100]; ... return out;`): that memory is gone
  when the function returns.
- Python: `result = c + result` in a loop is O(n²) because each step copies the whole string.
- Loop condition `i <= j` is harmless (swapping the middle with itself), but `i < j` says what you
  mean.

## Going further

- Reverse a string **in place** in O(1) extra space (LeetCode 344 gives you a `char[]`).
- Reverse only the letters, leaving punctuation in place: two pointers that skip non-letters.
- Reversal is a building block for "reverse words" and for array rotation (reverse all, then
  reverse each part).
""",
    solution=r'''def reverse_string(s):
    # Python strings are immutable, so copy the characters into a list we can swap in.
    chars = list(s)
    i, j = 0, len(chars) - 1
    # Two pointers walk toward each other, swapping mirror positions i and n-1-i.
    # When they meet (odd length) the middle character is already in place;
    # for an empty string j == -1 so the loop never runs.
    while i < j:
        chars[i], chars[j] = chars[j], chars[i]
        i += 1
        j -= 1
    # join builds the result in one O(n) pass (repeated += could be O(n^2)).
    return "".join(chars)
''',
    refs={
        "c": r'''char* reverse_string(char* s) {
    size_t n = strlen(s);              /* O(n) walk to the '\0'; do it once */
    char* out = malloc(n + 1);         /* +1 byte for the terminator */
    for (size_t i = 0; i < n; i++) {
        out[i] = s[n - 1 - i];         /* mirror position */
    }
    out[n] = '\0';                     /* without this, out is not a string */
    return out;                        /* heap memory outlives this function */
}''',
        "cpp": r'''string reverseString(string s) {
    // s is a copy (passed by value), so we may modify it freely.
    int i = 0, j = (int)s.size() - 1;
    while (i < j) swap(s[i++], s[j--]);
    return s;   // equivalently: reverse(s.begin(), s.end()); return s;
}''',
        "rust": r'''pub fn reverse_string(s: String) -> String {
    // chars() iterates Unicode scalar values; rev() walks them backwards;
    // collect() builds a new String. Correct even beyond ASCII.
    s.chars().rev().collect()
}''',
    },
    lang_notes={
        "c": "`strlen` is O(n) because it searches for the `'\\0'`. Store it in a variable instead of calling it in the loop condition, or your O(n) loop silently becomes O(n²).",
        "rust": "You can't write `s[i]` on a `String`. Use `s.as_bytes()[i]` for a byte, or iterate with `.chars()`. `.rev()` works on `chars()` because it is a double-ended iterator.",
    },
    tests=[["hello"], [""], ["a"], ["ab"], ["abc d"], ["racecar"], ["A man, a plan!"], ["  lead"], [_rand_str(_r, 5000, PRINTABLE)]],
))

# ================================================================ 2. valid palindrome
_r = _rng(402)
_pal_half = _rand_str(_r, 2000, string.ascii_letters + string.digits + " ,.!")
PROBLEMS.append(dict(
    id="valid-palindrome-alnum",
    title="Valid Palindrome",
    difficulty=1,
    tags=["string", "two pointers"],
    fn="is_palindrome",
    params=[["s", "str"]],
    returns="bool",
    statement=r"""
A phrase is a **palindrome** if, after converting all uppercase letters to lowercase and removing
every character that is not a letter or a digit, it reads the same forwards and backwards.

Given an ASCII string `s`, return `true` if it is a palindrome under this rule.

A string with no letters or digits at all (including the empty string) counts as a palindrome.
""",
    constraints=["0 ≤ len(s) ≤ 2·10⁴", "`s` is printable ASCII"],
    example_notes=["Filtered: \"amanaplanacanalpanama\", which is symmetric.", "Filtered: \"raceacar\"; position 2 ('c') and 5 ('a') differ."],
    hints=[
        "You could build the filtered lowercase string and compare it with its reverse. That's O(n) time and O(n) extra space.",
        "To use O(1) extra space: put one pointer at each end, skip characters that aren't alphanumeric, and compare the rest case-insensitively.",
        "Careful with the skipping loops: they must also stop when the pointers cross, or they run off the string.",
    ],
    explanation=r"""
## Intuition

"Reads the same forwards and backwards" means position `i` matches position `n − 1 − i`:
**two pointers** from the ends. The twist is that some characters don't count, so each pointer
skips over them before comparing.

## Approach

```
i, j = 0, n - 1
while i < j:
    while i < j and not alnum(s[i]): i += 1
    while i < j and not alnum(s[j]): j -= 1
    if lower(s[i]) != lower(s[j]): return false
    i += 1; j -= 1
return true
```

Trace for `"No 'x' in Nixon"` (positions of kept characters only):

| compare | left | right | equal? |
|---|---|---|---|
| 1 | N | n | ✓ (case-folded) |
| 2 | o | o | ✓ |
| 3 | x | x | ✓ |
| 4 | i | i | ✓ |
| 5 | n | N | ✓ |

The pointers then cross, so it's a palindrome. Quotes and spaces were skipped.

Why `i < j` in the skip loops? For `".,"` the left pointer would otherwise skip past every
character and run off the end. With the guard, it stops at `j` and the outer loop ends.

## Complexity

- **Time:** O(n). Each pointer only moves inward, so together they take at most `n` steps.
- **Space:** O(1) for the two-pointer version; O(n) for "filter then reverse".

## Common mistakes

- Forgetting digits: `"0P"` is **not** a palindrome (`'0'` vs `'p'`), but code that keeps only
  letters says it is.
- Comparing before lowering case: `'A' != 'a'`.
- C: calling `isalnum(c)` or `tolower(c)` with a plain `char` that might be negative is undefined
  behaviour; cast to `unsigned char`. (Inputs here are ASCII, but the habit matters.)
- Skip loops without the `i < j` guard read out of bounds.

## Going further

- **Valid Palindrome II**: may you delete *at most one* character to make it a palindrome? On
  the first mismatch, try skipping either side once.
- Longest palindromic substring: expand around each center, O(n²), or Manacher's algorithm, O(n).
""",
    solution=r'''def is_palindrome(s):
    i, j = 0, len(s) - 1
    while i < j:
        # Skip characters that don't count. The i < j guard stops the pointer from running
        # past its partner (e.g. a string of only punctuation).
        while i < j and not s[i].isalnum():
            i += 1
        while i < j and not s[j].isalnum():
            j -= 1
        # Compare case-insensitively. str.isalnum/lower are fine here because input is ASCII.
        if s[i].lower() != s[j].lower():
            return False
        # Both matched; move both pointers inward.
        i += 1
        j -= 1
    # The pointers met or crossed without a mismatch. This also covers "" and "!!!".
    return True
''',
    refs={
        "c": r'''bool is_palindrome(char* s) {
    long i = 0, j = (long)strlen(s) - 1;
    while (i < j) {
        /* <ctype.h> functions require an unsigned char value (or EOF). */
        while (i < j && !isalnum((unsigned char)s[i])) i++;
        while (i < j && !isalnum((unsigned char)s[j])) j--;
        if (tolower((unsigned char)s[i]) != tolower((unsigned char)s[j])) return false;
        i++;
        j--;
    }
    return true;
}''',
        "cpp": r'''bool isPalindrome(string s) {
    int i = 0, j = (int)s.size() - 1;
    while (i < j) {
        while (i < j && !isalnum((unsigned char)s[i])) ++i;
        while (i < j && !isalnum((unsigned char)s[j])) --j;
        if (tolower((unsigned char)s[i]) != tolower((unsigned char)s[j])) return false;
        ++i; --j;
    }
    return true;
}''',
        "rust": r'''pub fn is_palindrome(s: String) -> bool {
    let b = s.as_bytes();             // ASCII: one byte per character
    if b.is_empty() {
        return true;
    }
    let (mut i, mut j) = (0usize, b.len() - 1);
    while i < j {
        while i < j && !b[i].is_ascii_alphanumeric() { i += 1; }
        while i < j && !b[j].is_ascii_alphanumeric() { j -= 1; }
        if b[i].to_ascii_lowercase() != b[j].to_ascii_lowercase() {
            return false;
        }
        i += 1;
        // j > i >= 1 here, so j - 1 cannot underflow.
        j -= 1;
    }
    true
}''',
    },
    lang_notes={
        "rust": "`j` is a `usize`; `0usize - 1` panics in debug builds. That's why the empty string is handled before computing `b.len() - 1`. The `u8` methods `is_ascii_alphanumeric` and `to_ascii_lowercase` avoid `char` conversions entirely.",
        "c": "Always cast to `unsigned char` before calling `isalnum`, `tolower` and friends: passing a negative `char` (possible for bytes ≥ 128) is undefined behaviour.",
    },
    tests=[
        ["A man, a plan, a canal: Panama"], ["race a car"], [""], [" "], [".,!"], ["0P"], ["No 'x' in Nixon"],
        ["ab_a"], ["a"], ["Aa"], ["abcba!"], ["abccbx"],
        [_pal_half + _pal_half[::-1].upper()], [_pal_half + "Q" + _pal_half[::-1] + "q?"], [_pal_half + "xy" + _pal_half[::-1]],
    ],
))

# ================================================================ 3. capitalize words
_r = _rng(403)
PROBLEMS.append(dict(
    id="capitalize-each-word",
    title="Capitalize Each Word",
    difficulty=1,
    tags=["string", "scan"],
    fn="capitalize_words",
    params=[["s", "str"]],
    returns="str",
    statement=r"""
A **word** is a maximal run of non-space characters in `s` (words are separated by one or more
space characters `' '`).

Return a copy of `s` in which, for every word:

- the **first** character is converted to uppercase (if it is a letter), and
- every **other** letter is converted to lowercase.

All spaces stay exactly where they are (including leading, trailing and repeated spaces), and
non-letters are unchanged. `s` is printable ASCII.
""",
    constraints=["0 ≤ len(s) ≤ 10⁴", "`s` is printable ASCII"],
    example_notes=["Each word's first letter goes up, the rest go down.", "Spaces are preserved exactly; `3d` starts with a digit, so only the `D` is lowered."],
    hints=[
        "A character starts a word if it isn't a space and it is either at index 0 or preceded by a space.",
        "Scan once, remembering whether the previous character was a space (start with \"yes\", as if there were a space before index 0).",
        "Splitting on spaces and re-joining loses repeated spaces. Work character by character instead.",
    ],
    explanation=r"""
## Intuition

Whether a character should be upper- or lowercase depends on **one fact about its neighbour**: is
the previous character a space? That's a scan with a single boolean of state. No splitting
needed, and splitting would actually destroy the exact spacing we must keep.

## Approach

```
prev_space = true                # pretend there's a space before the string
for each character c:
    if c == ' ':        emit c;              prev_space = true
    elif prev_space:    emit upper(c);       prev_space = false
    else:               emit lower(c)
```

Trace for `"  hELLO   3d woRLD "`:

| char | prev_space | emitted |
|---|---|---|
| (2 spaces) | | copied unchanged |
| h | true | H |
| E L L O | false | e l l o |
| (3 spaces) | | copied unchanged |
| 3 | true | 3 (not a letter, upper is a no-op) |
| d | false | d |
| w | true | W |
| o R L D | false | o r l d |
| (1 space) | | copied unchanged |

Result: `"  Hello   3d World "`.

**Language mechanics.** Case conversion in ASCII is arithmetic: uppercase letters are 65–90 and
lowercase are 97–122, exactly 32 apart. `toupper`/`tolower` in C, `char::to_ascii_uppercase` in
Rust, and Python's `str.upper` do this for you, and leave non-letters alone.

## Complexity

- **Time:** O(n), one pass.
- **Space:** O(n) for the output string.

## Common mistakes

- `" ".join(w.capitalize() for w in s.split())`: `split()` with no argument collapses runs of spaces
  and drops leading/trailing ones.
- Python's `str.title()` treats *any* non-letter as a word boundary, so `"don't 3d"` becomes
  `"Don'T 3D"`. Always check what a built-in actually does against the spec.
- Forgetting to lowercase the rest of the word (`"hELLO"` must become `"Hello"`).
- C: writing into the input string. It's legal here but surprising to callers; produce a copy.

## Going further

- **Camel case**: remove the spaces and capitalize every word but the first (`"get user name"` →
  `"getUserName"`). Same state machine, different emit rules.
- Most text-processing tasks are tiny **state machines**: decide what state you need to remember
  (here, one bit) and what each character does to it.
""",
    solution=r'''def capitalize_words(s):
    out = []
    # State: was the previous character a space? Start as True, as if a space preceded
    # index 0, so the very first character is treated as a word start.
    prev_space = True
    for c in s:
        if c == " ":
            out.append(c)          # spaces are copied exactly, never collapsed
            prev_space = True
        elif prev_space:
            out.append(c.upper())  # first character of a word; upper() leaves digits/punctuation alone
            prev_space = False
        else:
            out.append(c.lower())  # any later character in the word
    return "".join(out)
''',
    refs={
        "c": r'''char* capitalize_words(char* s) {
    size_t n = strlen(s);
    char* out = malloc(n + 1);
    bool prev_space = true;                /* "virtual space" before index 0 */
    for (size_t i = 0; i < n; i++) {
        unsigned char c = (unsigned char)s[i];
        if (c == ' ') {
            out[i] = ' ';
            prev_space = true;
        } else if (prev_space) {
            out[i] = (char)toupper(c);     /* non-letters are returned unchanged */
            prev_space = false;
        } else {
            out[i] = (char)tolower(c);
        }
    }
    out[n] = '\0';
    return out;
}''',
        "cpp": r'''string capitalizeWords(string s) {
    bool prevSpace = true;
    for (char& c : s) {                    // reference: modify the copy in place
        if (c == ' ') prevSpace = true;
        else if (prevSpace) { c = toupper((unsigned char)c); prevSpace = false; }
        else c = tolower((unsigned char)c);
    }
    return s;
}''',
        "rust": r'''pub fn capitalize_words(s: String) -> String {
    let mut out = String::with_capacity(s.len());
    let mut prev_space = true;
    for c in s.chars() {
        if c == ' ' {
            out.push(c);
            prev_space = true;
        } else if prev_space {
            out.push(c.to_ascii_uppercase());
            prev_space = false;
        } else {
            out.push(c.to_ascii_lowercase());
        }
    }
    out
}''',
    },
    tests=[
        ["hello world"], ["  hELLO   3d woRLD "], [""], ["a"], ["   "], ["ALREADY Title Case"],
        ["don't stop-me now"], ["x y z"], ["123 abc"],
        [_rand_str(_r, 3000, string.ascii_letters + "   0'-")],
    ],
))

# ================================================================ 4. valid anagram
_r = _rng(404)
_ana = _rand_str(_r, 5000, string.ascii_lowercase)
_ana_l = list(_ana)
_r.shuffle(_ana_l)
_ana_shuf = "".join(_ana_l)
PROBLEMS.append(dict(
    id="valid-anagram-lowercase",
    title="Valid Anagram",
    difficulty=1,
    tags=["string", "counting"],
    fn="is_anagram",
    params=[["s", "str"], ["t", "str"]],
    returns="bool",
    statement=r"""
Return `true` if `t` is an **anagram** of `s`: it uses exactly the same letters, each the same
number of times, possibly in a different order.

Both strings consist of lowercase English letters `a`–`z` only.
""",
    constraints=["0 ≤ len(s), len(t) ≤ 5·10⁴", "only `a`–`z`"],
    example_notes=["Same letters with the same counts: a×3, n×1, g×1, r×1, m×1.", "`r` appears in `rat` but not in `car`."],
    hints=[
        "Different lengths can never be anagrams. Check that first.",
        "Sorting both strings and comparing works in O(n log n). Can you avoid sorting?",
        "With only 26 possible letters, keep an array of 26 counters: add 1 for each letter of `s`, subtract 1 for each letter of `t`. Anagrams leave every counter at 0.",
    ],
    explanation=r"""
## Intuition

Two strings are anagrams exactly when their **letter counts** match: order is irrelevant, so
throw it away and compare multisets. The alphabet is tiny and fixed (26 letters), so the multiset
fits in an array of 26 integers indexed by `c - 'a'`, the **count table** pattern.

## Approach

1. If `len(s) != len(t)`, return `false`.
2. `count = [0] * 26`.
3. For each `c` in `s`: `count[c - 'a'] += 1`. For each `c` in `t`: `count[c - 'a'] -= 1`.
4. Return `true` iff every counter is 0.

Trace for `s = "anagram"`, `t = "nagaram"`: `s` adds `a:3 n:1 g:1 r:1 m:1`; `t` subtracts exactly
the same, so all counters end at 0.

For `s = "rat"`, `t = "car"`: after both passes `count['t'] = 1` (only `s` has a `t`) and
`count['c'] = -1` (only `t` has a `c`), so the answer is `false`.

**Language mechanics.** `ord(c) - ord('a')` in Python, `c - 'a'` in C/C++, and `(b - b'a') as usize`
in Rust map a letter to `0..25`. A char really is just a small number.

## Complexity

- **Time:** O(n + m) plus O(26) for the final check.
- **Space:** O(1): 26 counters regardless of input size.

Sorting (`sorted(s) == sorted(t)`) is O(n log n) and simpler to write; the count table is the
better tool and generalises.

## Common mistakes

- Comparing only the *set* of letters (`set(s) == set(t)`): `"aab"` and `"abb"` would pass.
- Skipping the length check and only counting `s`'s letters in `t`.
- In C, indexing `count[c]` with a raw `char` (0–127) instead of `c - 'a'` writes past a
  26-element array.

## Going further

- For Unicode input, a hash map (`collections.Counter`, `HashMap<char, i32>`) replaces the array.
- **Group Anagrams**: use the sorted string, or the 26-count tuple, as a hash key.
- **Find All Anagrams in a String**: a sliding window that keeps a count table up to date as it
  moves, O(n).
""",
    solution=r'''def is_anagram(s, t):
    # Different lengths: some letter count must differ, so stop early.
    if len(s) != len(t):
        return False
    # One counter per letter a..z. ord(c) - ord('a') maps 'a'->0, ..., 'z'->25.
    count = [0] * 26
    for c in s:
        count[ord(c) - ord("a")] += 1      # letters s has
    for c in t:
        count[ord(c) - ord("a")] -= 1      # letters t uses up
    # Anagrams cancel out exactly: every counter returns to zero.
    return all(x == 0 for x in count)
''',
    refs={
        "c": r'''bool is_anagram(char* s, char* t) {
    size_t n = strlen(s), m = strlen(t);
    if (n != m) return false;
    int count[26] = {0};                 /* zero-initialise all 26 counters */
    for (size_t i = 0; i < n; i++) {
        count[s[i] - 'a']++;
        count[t[i] - 'a']--;             /* same length, so one loop handles both */
    }
    for (int k = 0; k < 26; k++)
        if (count[k] != 0) return false;
    return true;
}''',
        "cpp": r'''bool isAnagram(string s, string t) {
    if (s.size() != t.size()) return false;
    array<int, 26> count{};              // value-initialised to zeros
    for (size_t i = 0; i < s.size(); ++i) {
        ++count[s[i] - 'a'];
        --count[t[i] - 'a'];
    }
    for (int c : count) if (c != 0) return false;
    return true;
}''',
        "rust": r'''pub fn is_anagram(s: String, t: String) -> bool {
    if s.len() != t.len() {
        return false;
    }
    let mut count = [0i32; 26];
    for (a, b) in s.bytes().zip(t.bytes()) {
        count[(a - b'a') as usize] += 1;   // b'a' is the byte literal 97
        count[(b - b'a') as usize] -= 1;
    }
    count.iter().all(|&c| c == 0)
}''',
    },
    tests=[
        ["anagram", "nagaram"], ["rat", "car"], ["", ""], ["a", "a"], ["a", "b"], ["ab", "a"],
        ["aab", "abb"], ["listen", "silent"], ["aaaa", "aaaa"],
        [_ana, _ana_shuf], [_ana, _ana_shuf[:-1] + ("a" if _ana_shuf[-1] != "a" else "b")],
    ],
))

# ================================================================ 5. first unique char
_r = _rng(405)
_fu_big = _rand_str(_r, 4000, "abcdefghij") + "q" + _rand_str(_r, 4000, "abcdefghij")
_fu_none = "".join(c * 2 for c in _rand_str(_r, 3000, string.ascii_lowercase))
PROBLEMS.append(dict(
    id="first-unique-character-index",
    title="First Unique Character",
    difficulty=1,
    tags=["string", "counting"],
    fn="first_uniq_char",
    params=[["s", "str"]],
    returns="int",
    statement=r"""
Return the index of the first character in `s` that appears **exactly once** in the whole
string. If every character repeats, return `-1`.

`s` consists of lowercase English letters.
""",
    constraints=["0 ≤ len(s) ≤ 10⁵", "only `a`–`z`"],
    example_notes=["`l` (index 0) appears once, and nothing comes before it.", "`l` repeats; `o` repeats; `v` at index 2 appears once."],
    hints=[
        "For each position you need to know how many times its character appears *anywhere*. Can you know that before you start looking for the answer?",
        "Two passes: first count every letter (26 counters), then scan left to right and return the first index whose letter has count 1.",
        "Checking `s.count(c)` for every character is O(n²). The count table makes it O(n).",
    ],
    explanation=r"""
## Intuition

Whether `s[i]` is unique depends on characters **after** it too, so one left-to-right pass can't
decide on the spot. The fix is to precompute global information in a first pass (letter counts),
then answer with a second pass. "Count first, then scan" is a very common two-pass shape.

## Approach

1. Pass 1: `count[c] += 1` for every character.
2. Pass 2: for `i` from 0, if `count[s[i]] == 1`, return `i`.
3. If nothing qualified, return `-1`.

Trace for `s = "loveleetcode"`: counts are `l:2 o:2 v:1 e:4 t:1 c:1 d:1`. Scanning: index 0 `l`
(2), index 1 `o` (2), index 2 `v` (1) → return 2.

The second pass scans the **string**, not the alphabet, because we need the first *position*, not
the alphabetically first letter.

## Complexity

- **Time:** O(n): two linear passes.
- **Space:** O(1): 26 counters.

## Common mistakes

- Scanning the count table `a..z` in the second pass: that finds the alphabetically smallest unique
  letter, not the earliest one.
- `s.index(c)` / `s.count(c)` inside a loop: each is O(n), so the whole thing becomes O(n²) and
  times out on long inputs.
- Returning `0` instead of `-1` when there is no unique character (or when `s` is empty).

## Going further

- **Streaming version:** characters arrive one at a time and you must report the first unique
  character so far after each one. Keep counts plus a queue of candidates; pop from the front while
  the front's count exceeds 1.
- For larger alphabets, `collections.Counter` / `HashMap` replace the array, with the same logic.
""",
    solution=r'''def first_uniq_char(s):
    # Pass 1: global letter counts. Uniqueness depends on the whole string, so we need
    # this information before we can judge any single position.
    count = [0] * 26
    for c in s:
        count[ord(c) - ord("a")] += 1
    # Pass 2: walk positions in order; the first one whose letter occurs once wins.
    for i, c in enumerate(s):
        if count[ord(c) - ord("a")] == 1:
            return i
    # Every letter repeats (or s is empty).
    return -1
''',
    refs={
        "c": r'''long long first_uniq_char(char* s) {
    int count[26] = {0};
    size_t n = strlen(s);
    for (size_t i = 0; i < n; i++) count[s[i] - 'a']++;
    for (size_t i = 0; i < n; i++)
        if (count[s[i] - 'a'] == 1) return (long long)i;
    return -1;
}''',
        "cpp": r'''long long firstUniqChar(string s) {
    array<int, 26> count{};
    for (char c : s) ++count[c - 'a'];
    for (size_t i = 0; i < s.size(); ++i)
        if (count[s[i] - 'a'] == 1) return (long long)i;
    return -1;
}''',
        "rust": r'''pub fn first_uniq_char(s: String) -> i64 {
    let b = s.as_bytes();
    let mut count = [0u32; 26];
    for &c in b {
        count[(c - b'a') as usize] += 1;
    }
    for (i, &c) in b.iter().enumerate() {
        if count[(c - b'a') as usize] == 1 {
            return i as i64;
        }
    }
    -1
}''',
    },
    tests=[["leetcode"], ["loveleetcode"], ["aabb"], [""], ["z"], ["aab"], ["abcabcd"], ["zzzzy"], [_fu_big], [_fu_none]],
))

# ================================================================ 6. longest common prefix
_r = _rng(406)
_lcp_root = _rand_str(_r, 300, "ab")
PROBLEMS.append(dict(
    id="longest-common-prefix-strings",
    title="Longest Common Prefix",
    difficulty=1,
    tags=["string", "scan"],
    fn="longest_common_prefix",
    params=[["strs", "str[]"]],
    returns="str",
    statement=r"""
Return the longest string that is a **prefix** of every string in `strs`. If the strings share
no common prefix, return the empty string `""`.

`strs` contains at least one string; strings consist of lowercase English letters and may be empty.
""",
    constraints=["1 ≤ len(strs) ≤ 200", "0 ≤ len(strs[i]) ≤ 300", "only `a`–`z`"],
    example_notes=["All three start with `fl`; the third character differs (`o`, `o`, `i`).", "`d`, `r` and `c` already differ at position 0."],
    hints=[
        "Compare the strings column by column: position 0 of every string, then position 1, and so on.",
        "Stop at the first column where some string has ended or has a different character than `strs[0]`.",
        "The answer is `strs[0]` cut at that column.",
    ],
    explanation=r"""
## Intuition

Line the strings up vertically and read down the columns:

```
f l o w e r
f l o w
f l i g h t
    ^ column 2 disagrees
```

The common prefix is everything to the left of the first column that is not unanimous (or where
some string runs out). This is **vertical scanning**.

## Approach

```
for col in 0 .. len(strs[0]):
    c = strs[0][col]
    for each other string w:
        if col == len(w) or w[col] != c:
            return strs[0][:col]
return strs[0]          # strs[0] itself is a prefix of all others
```

The check `col == len(w)` must come **before** `w[col]`: it is what stops you reading past the end
of a shorter string.

## Complexity

- **Time:** O(S) where S is the total number of characters, and in fact only
  O(n · |answer|) characters are compared before we stop.
- **Space:** O(1) besides the output.

## Common mistakes

- Indexing past the end of a shorter string (`IndexError` in Python, garbage or a crash in C).
- Forgetting the single-string case (the answer is the string itself) or an empty string in the
  list (the answer is `""`).
- C: returning `strs[0]` itself instead of a fresh copy. The caller expects a `malloc`-ed string it
  can free, so copy the prefix into new memory and terminate it.

## Going further

- **Horizontal scanning:** start with `prefix = strs[0]` and shrink it against each string in
  turn. Same worst case, simpler code.
- Sorting the list and comparing only the first and last strings also works: they are the most
  different lexicographically. O(S log n) because of the sort.
- A **trie** answers this and many more prefix questions; you'll meet tries in a later track.
""",
    solution=r'''def longest_common_prefix(strs):
    first = strs[0]
    # Vertical scan: check column `col` of every string before moving to the next column.
    for col in range(len(first)):
        c = first[col]
        for w in strs[1:]:
            # Check the length FIRST so we never index past the end of a shorter string.
            if col == len(w) or w[col] != c:
                # Columns 0..col-1 were unanimous; column col is not.
                return first[:col]
    # Every column of `first` matched everywhere, so all of `first` is the common prefix.
    return first
''',
    refs={
        "c": r'''char* longest_common_prefix(char** strs, int strsSize) {
    const char* first = strs[0];
    size_t col = 0;
    for (;; col++) {
        char c = first[col];
        if (c == '\0') break;                       /* first string exhausted */
        bool ok = true;
        for (int k = 1; k < strsSize; k++) {
            /* If strs[k] ended, strs[k][col] is '\0' which never equals c (c != '\0'). */
            if (strs[k][col] != c) { ok = false; break; }
        }
        if (!ok) break;
    }
    char* out = malloc(col + 1);                    /* always return fresh memory */
    memcpy(out, first, col);
    out[col] = '\0';
    return out;
}''',
        "cpp": r'''string longestCommonPrefix(vector<string>& strs) {
    const string& first = strs[0];
    for (size_t col = 0; col < first.size(); ++col) {
        for (size_t k = 1; k < strs.size(); ++k) {
            if (col == strs[k].size() || strs[k][col] != first[col])
                return first.substr(0, col);        // substr(pos, count)
        }
    }
    return first;
}''',
        "rust": r'''pub fn longest_common_prefix(strs: Vec<String>) -> String {
    let first = strs[0].as_bytes();
    for col in 0..first.len() {
        for w in &strs[1..] {
            let w = w.as_bytes();
            if col == w.len() || w[col] != first[col] {
                // Slicing a &str by byte range is fine for ASCII (char boundaries).
                return strs[0][..col].to_string();
            }
        }
    }
    strs[0].clone()
}''',
    },
    lang_notes={
        "c": "A neat C trick: a shorter string has `'\\0'` at index `len`, and that byte can never equal a real letter, so `strs[k][col] != c` also catches \"string ended\" without calling `strlen`. You still must stop before reading *past* the terminator, which the check on `first` guarantees.",
    },
    tests=[
        [["flower", "flow", "flight"]], [["dog", "racecar", "car"]], [["alone"]], [[""]], [["abc", ""]],
        [["same", "same", "same"]], [["ab", "a"]], [["prefix", "prefixes", "prefixed", "pre"]],
        [[_lcp_root + _rand_str(_r, 5, "xyz") for _ in range(60)]],
        [[_lcp_root] * 40],
    ],
))

# ================================================================ 7. string compression
_r = _rng(407)


def _runs_str(r, nruns, alphabet, maxlen):
    out, prev = [], None
    for _ in range(nruns):
        c = r.choice([a for a in alphabet if a != prev])
        out.append(c * r.randint(1, maxlen))
        prev = c
    return "".join(out)


PROBLEMS.append(dict(
    id="run-length-compression",
    title="String Compression (Run Lengths)",
    difficulty=1,
    tags=["string", "runs"],
    fn="compress_runs",
    params=[["s", "str"]],
    returns="str",
    statement=r"""
Compress `s` by replacing every **run** (maximal block of consecutive equal characters) with the
character followed by the run's length in decimal.

- Every run gets a count, **even a run of length 1** (`"abc"` → `"a1b1c1"`).
- Counts can have several digits (`"aaaaaaaaaaaa"` → `"a12"`).
- Letters are case-sensitive: `"aA"` is two runs.
- The empty string compresses to the empty string.

`s` consists of English letters only.
""",
    constraints=["0 ≤ len(s) ≤ 10⁴", "only `a`–`z`, `A`–`Z`"],
    example_notes=["Runs: `aa`, `b`, `ccc`.", "A single character is a run of length 1."],
    hints=[
        "Walk the string remembering where the current run started. A run ends when the next character differs, or when the string ends.",
        "When a run ends, append the character and the run length (converted to text) to the output.",
        "The classic bug is forgetting to emit the *last* run after the loop. A loop that looks one step ahead (`i == n or s[i] != s[start]`) handles it uniformly.",
    ],
    explanation=r"""
## Intuition

This is **run detection**: group consecutive equal characters. Keep the index where the current
run started; when you hit a different character (or the end of the string), the run
`s[start..i)` is complete, so emit it and start a new run at `i`.

## Approach

```
out = []
start = 0
for i in 1..=n:                       # note: i goes up to n inclusive
    if i == n or s[i] != s[start]:    # run s[start..i) just ended
        out += s[start] + str(i - start)
        start = i
```

Letting `i` run to `n` and treating "end of string" as a run boundary means the last run is
emitted inside the loop, with no special code after it.

Trace for `"aabccc"`:

| i | s[i] | s[start] | action |
|---|---|---|---|
| 1 | a | a | same run |
| 2 | b | a | emit `a2`, start = 2 |
| 3 | c | b | emit `b1`, start = 3 |
| 4 | c | c | same run |
| 5 | c | c | same run |
| 6 | (end) | c | emit `c3` |

Result `"a2b1c3"`.

**Language mechanics.** Turning a count into text: `str(k)` in Python, `to_string(k)` in C++,
`k.to_string()` or `write!` in Rust, and `sprintf(buf, "%d", k)` in C (it returns how many
characters it wrote, handy for advancing a write pointer).

## Complexity

- **Time:** O(n).
- **Space:** O(n) for the output. In the worst case (no repeats) the output is twice as long as the
  input: a run of length `L` produces `1 + digits(L) ≤ L + 1` characters, so `2n + 1` bytes is a
  safe C buffer.

## Common mistakes

- Dropping the final run (`"aab"` → `"a2"`).
- Writing counts as single characters (`chr(ord('0') + 12)` is `'<'`, not `"12"`).
- C: under-allocating the result. Reason about the worst case (`"abab..."` → `"a1b1a1b1..."`).
- Python: `out += ...` on a string in a loop; append to a list and join.

## Going further

- **LeetCode 443** compresses *in place* and omits counts of 1 (`"abc"` stays `"abc"`), returning
  the new length. The write pointer never overtakes the read pointer, so it's safe.
- Decoding is the inverse: read a character, then all following digits as the count.
- Run-length encoding is used in fax machines, BMP/TGA images and as a stage inside bzip2.
""",
    solution=r'''def compress_runs(s):
    out = []
    n = len(s)
    start = 0                              # index where the current run began
    # i goes all the way to n: "end of string" acts as one more run boundary, so the
    # final run is emitted inside the loop instead of in special code afterwards.
    for i in range(1, n + 1):
        if i == n or s[i] != s[start]:
            # s[start:i] is a complete run of identical characters.
            out.append(s[start])
            out.append(str(i - start))     # multi-digit counts come out right automatically
            start = i                      # the next run begins here
    # For s == "" the range is range(1, 1) (empty), so we return "".
    return "".join(out)
''',
    refs={
        "c": r'''char* compress_runs(char* s) {
    size_t n = strlen(s);
    /* Each run of length L becomes 1 + digits(L) <= L + 1 chars, so 2n + 1 bytes suffice. */
    char* out = malloc(2 * n + 1);
    char* w = out;                          /* write pointer */
    size_t start = 0;
    for (size_t i = 1; i <= n; i++) {
        if (i == n || s[i] != s[start]) {
            *w++ = s[start];
            /* sprintf returns the number of characters written (excluding '\0'). */
            w += sprintf(w, "%zu", i - start);
            start = i;
        }
    }
    *w = '\0';                              /* also correct for n == 0 */
    return out;
}''',
        "cpp": r'''string compressRuns(string s) {
    string out;
    size_t n = s.size(), start = 0;
    for (size_t i = 1; i <= n; ++i) {
        if (i == n || s[i] != s[start]) {
            out += s[start];
            out += to_string(i - start);
            start = i;
        }
    }
    return out;
}''',
        "rust": r'''pub fn compress_runs(s: String) -> String {
    let b = s.as_bytes();
    let n = b.len();
    let mut out = String::new();
    let mut start = 0;
    for i in 1..=n {
        if i == n || b[i] != b[start] {
            out.push(b[start] as char);              // ASCII byte -> char
            out.push_str(&(i - start).to_string());
            start = i;
        }
    }
    out
}''',
    },
    lang_notes={
        "c": "`sprintf(w, \"%zu\", k)` writes the digits *and* a terminating `'\\0'`, and returns the digit count. Advancing `w` by that count means the next write overwrites the temporary terminator, and the final `*w = '\\0'` closes the string.",
    },
    tests=[
        ["aabccc"], ["a"], [""], ["abc"], ["aaaaaaaaaaaa"], ["aA"], ["zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"],
        ["abba"], [_runs_str(_r, 800, "abcAB", 6)], ["Q" * 10000],
    ],
))

# ================================================================ 8. is subsequence
_r = _rng(408)
_sub_t = _rand_str(_r, 10000, "abcdef")
_sub_s_yes = "".join(c for i, c in enumerate(_sub_t) if i % 7 == 0)
PROBLEMS.append(dict(
    id="is-subsequence-two-pointer",
    title="Is Subsequence",
    difficulty=1,
    tags=["string", "two pointers", "greedy"],
    fn="is_subsequence",
    params=[["s", "str"], ["t", "str"]],
    returns="bool",
    statement=r"""
Return `true` if `s` is a **subsequence** of `t`: that is, `s` can be obtained from `t` by deleting
zero or more characters **without changing the order** of the remaining ones.

For example `"ace"` is a subsequence of `"abcde"`, but `"aec"` is not. The empty string is a
subsequence of every string.

Both strings consist of lowercase English letters.
""",
    constraints=["0 ≤ len(s) ≤ 100", "0 ≤ len(t) ≤ 10⁴", "only `a`–`z`"],
    example_notes=["Match a, then b, then c, scanning t left to right.", "x never appears in t."],
    hints=[
        "Walk through `t` once. Keep an index `i` into `s` saying how much of `s` you've matched so far.",
        "Whenever `t[j] == s[i]`, advance `i`. Greedily taking the earliest match is always safe. Why?",
        "`s` is a subsequence iff `i` reaches `len(s)`.",
    ],
    explanation=r"""
## Intuition

Two strings, two pointers moving at **different speeds**: `j` walks every character of `t`, while
`i` advances through `s` only when it finds a match. Matching greedily (taking the first
occurrence in `t` of the next needed character) is optimal, because matching earlier never leaves
*fewer* options for the remaining characters of `s`.

## Approach

```
i = 0
for c in t:
    if i < len(s) and c == s[i]:
        i += 1
return i == len(s)
```

Trace for `s = "abc"`, `t = "ahbgdc"`:

| t[j] | s[i] wanted | match? | i after |
|---|---|---|---|
| a | a | ✓ | 1 |
| h | b | | 1 |
| b | b | ✓ | 2 |
| g | c | | 2 |
| d | c | | 2 |
| c | c | ✓ | 3 |

`i == 3 == len(s)` → `true`.

Invariant: `s[0..i)` is a subsequence of the part of `t` scanned so far, and `i` is as large as
possible.

## Complexity

- **Time:** O(|t|): one pass over `t`, constant work per character.
- **Space:** O(1).

## Common mistakes

- Forgetting the `i < len(s)` guard: after `s` is fully matched, `s[i]` is out of range.
- Confusing **subsequence** (order kept, gaps allowed) with **substring** (contiguous). `"ace"` is a
  subsequence of `"abcde"` but not a substring.
- Returning `true` as soon as the loop ends instead of checking `i == len(s)`.

## Going further

**Follow-up:** many queries `s₁, s₂, …` against the same huge `t`. Precompute, for each letter,
the sorted list of its positions in `t`; then match each character of `s` with a binary search for
the next position after the current one. Each query costs O(|s| log |t|) instead of O(|t|).

"Longest common subsequence" (LCS) of two strings is the classic dynamic-programming problem that
generalises this check.
""",
    solution=r'''def is_subsequence(s, t):
    i = 0                       # s[0:i] has been matched so far
    for c in t:                 # the fast pointer: every character of t, in order
        # Greedy: if c is the next character we need, take it now. Taking the earliest
        # possible match never hurts, since it leaves the most of t for the rest of s.
        if i < len(s) and c == s[i]:
            i += 1
    # All of s matched exactly when i reached its end (true immediately for s == "").
    return i == len(s)
''',
    refs={
        "c": r'''bool is_subsequence(char* s, char* t) {
    /* Walk t with a pointer; advance s only on a match. Stop early if s is used up. */
    while (*s && *t) {
        if (*s == *t) s++;
        t++;
    }
    return *s == '\0';          /* reached s's terminator => everything matched */
}''',
        "cpp": r'''bool isSubsequence(string s, string t) {
    size_t i = 0;
    for (char c : t)
        if (i < s.size() && c == s[i]) ++i;
    return i == s.size();
}''',
        "rust": r'''pub fn is_subsequence(s: String, t: String) -> bool {
    let s = s.as_bytes();
    let mut i = 0;
    for &c in t.as_bytes() {
        if i < s.len() && c == s[i] {
            i += 1;
        }
    }
    i == s.len()
}''',
    },
    lang_notes={
        "c": "Pointer style: `*s` is the current character and `s++` moves to the next. Because strings end with `'\\0'` (which is false), `while (*s && *t)` stops at the end of either string without knowing the lengths.",
    },
    tests=[
        ["abc", "ahbgdc"], ["axc", "ahbgdc"], ["", "abc"], ["", ""], ["a", ""], ["aec", "abcde"],
        ["aaa", "aa"], ["aa", "baba"], ["abc", "abc"],
        [_sub_s_yes[:100], _sub_t], [_sub_s_yes[:99] + "z", _sub_t],
    ],
))

# ================================================================ 9. reverse words
_r = _rng(409)
PROBLEMS.append(dict(
    id="reverse-words-in-sentence",
    title="Reverse Words in a String",
    difficulty=2,
    tags=["string", "two pointers", "parsing"],
    fn="reverse_words",
    params=[["s", "str"]],
    returns="str",
    statement=r"""
Given a string `s` of words separated by spaces, return the words in **reverse order**, joined by
a **single** space.

- A word is a maximal run of non-space characters.
- `s` may contain leading spaces, trailing spaces, or several spaces between words; none of these
  appear in the output.
- The characters inside each word keep their order.
- If `s` contains no words, return `""`.

`s` is printable ASCII and the only whitespace character is `' '`.
""",
    constraints=["0 ≤ len(s) ≤ 10⁴", "`s` is printable ASCII"],
    example_notes=["Words: `the`, `sky`, `is`, `blue`, reversed.", "Leading/trailing and repeated spaces disappear."],
    hints=[
        "First, extract the words. Then output them last-to-first with single spaces between.",
        "Extracting words by hand: skip spaces, remember where a word starts, advance until a space or the end, record the word.",
        "Without a list of words: scan from the **end** of the string, find each word's end and start, and append it to the output.",
    ],
    explanation=r"""
## Intuition

Two separate jobs: **tokenise** (find the words, ignoring however many spaces there are) and
**reassemble** (reverse order, single spaces). In Python that's `" ".join(reversed(s.split()))`.
Doing the tokenising by hand is the real lesson, because that loop shows up in every parser you
will ever write.

## Approach

Scan from the right so that words come out already in reverse order:

```
i = n - 1
while i >= 0:
    while i >= 0 and s[i] == ' ': i -= 1      # skip spaces
    if i < 0: break
    end = i                                   # last char of a word
    while i >= 0 and s[i] != ' ': i -= 1      # walk to the word's start
    word = s[i+1 .. end]
    append word (with a space before it unless it's the first)
```

Trace for `"  hello   world "`:

| step | i lands on | word |
|---|---|---|
| skip trailing space | `d` (end) | |
| walk back | space before `w` | `world` |
| skip 3 spaces | `o` (end) | |
| walk back | space before `h` | `hello` |
| skip 2 spaces | i = −1 | stop |

Output `"world hello"`.

## Complexity

- **Time:** O(n): every index is visited a constant number of times.
- **Space:** O(n) for the output.

## Common mistakes

- `s.split(" ")` (with an explicit separator) in Python produces empty strings for repeated spaces;
  `s.split()` with no argument is the one that collapses whitespace.
- Leaving a trailing or leading space in the output.
- Off-by-one in the slice: after the inner loop, `i` points at the space *before* the word, so the
  word is `s[i+1 : end+1]`.
- Reversing the characters of each word too (that's a different problem).

## Going further

**In place with O(1) extra space** (C/C++ with a mutable buffer): reverse the entire string, then
reverse each word individually, then squeeze out extra spaces with a read/write pointer pair.
`"the sky"` → `"yks eht"` → `"sky the"`. The double-reversal trick also rotates arrays.
""",
    solution=r'''def reverse_words(s):
    words = []
    i = len(s) - 1
    # Scan right-to-left so words are discovered in the order we want to output them.
    while i >= 0:
        # Skip any run of spaces (handles trailing and repeated spaces).
        while i >= 0 and s[i] == " ":
            i -= 1
        if i < 0:
            break                       # only spaces were left
        end = i                         # last character of this word
        # Walk left to the character just before the word (a space, or index -1).
        while i >= 0 and s[i] != " ":
            i -= 1
        words.append(s[i + 1:end + 1])  # i + 1 is the word's first character
    # Single spaces between words, none at the ends; "" when there were no words.
    return " ".join(words)
''',
    refs={
        "c": r'''char* reverse_words(char* s) {
    long n = (long)strlen(s);
    char* out = malloc(n + 1);           /* output is never longer than the input */
    long w = 0;                          /* write position in out */
    long i = n - 1;
    while (i >= 0) {
        while (i >= 0 && s[i] == ' ') i--;          /* skip spaces */
        if (i < 0) break;
        long end = i;
        while (i >= 0 && s[i] != ' ') i--;          /* find the word's start */
        if (w > 0) out[w++] = ' ';                  /* separator before all but the first word */
        long len = end - i;                         /* word is s[i+1 .. end] */
        memcpy(out + w, s + i + 1, len);
        w += len;
    }
    out[w] = '\0';
    return out;
}''',
        "cpp": r'''string reverseWords(string s) {
    // istringstream >> word skips any amount of whitespace: a ready-made tokenizer.
    istringstream in(s);
    vector<string> words;
    string word;
    while (in >> word) words.push_back(word);
    string out;
    for (auto it = words.rbegin(); it != words.rend(); ++it) {
        if (!out.empty()) out += ' ';
        out += *it;
    }
    return out;
}''',
        "rust": r'''pub fn reverse_words(s: String) -> String {
    // split_whitespace() skips leading, trailing and repeated whitespace.
    // rev() reverses the word order; join(" ") puts single spaces between them.
    s.split_whitespace().rev().collect::<Vec<&str>>().join(" ")
}''',
    },
    tests=[
        ["the sky is blue"], ["  hello   world  "], [""], ["     "], ["one"], ["a good   example"],
        ["  Bob    Loves  Alice   "], ["x y"], ["punctuation, stays! attached?"],
        [" ".join(_rand_str(_r, _r.randint(1, 8), string.ascii_letters) + " " * _r.randint(0, 3) for _ in range(700))],
    ],
))

# ================================================================ 10. roman to integer
_ROMAN = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
          (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]


def _to_roman(n):
    out = []
    for v, sym in _ROMAN:
        while n >= v:
            out.append(sym)
            n -= v
    return "".join(out)


PROBLEMS.append(dict(
    id="roman-numeral-to-integer",
    title="Roman to Integer",
    difficulty=1,
    tags=["string", "scan", "math"],
    fn="roman_to_int",
    params=[["s", "str"]],
    returns="int",
    statement=r"""
Convert a Roman numeral to an integer.

| symbol | I | V | X | L | C | D | M |
|---|---|---|---|---|---|---|---|
| value | 1 | 5 | 10 | 50 | 100 | 500 | 1000 |

Symbols are normally written largest to smallest, left to right, and their values are added
(`XII = 10 + 1 + 1 = 12`). Six **subtractive** pairs are the exception, where a smaller symbol before
a larger one is subtracted: `IV = 4`, `IX = 9`, `XL = 40`, `XC = 90`, `CD = 400`, `CM = 900`.

`s` is guaranteed to be a valid Roman numeral in standard form for a value from 1 to 3999.
""",
    constraints=["1 ≤ len(s) ≤ 15", "1 ≤ value ≤ 3999"],
    example_notes=["L + V + III = 50 + 5 + 3.", "M + CM + XC + IV = 1000 + 900 + 90 + 4."],
    hints=[
        "Look at each symbol together with the one right after it.",
        "If a symbol's value is smaller than the next symbol's value, it is subtracted; otherwise it is added.",
        "The last symbol is always added (nothing comes after it).",
    ],
    explanation=r"""
## Intuition

You don't need a table of the six special pairs. The rule hiding behind them is simple: **a
symbol is subtracted exactly when the symbol after it is larger**. So scan once, peeking one
character ahead.

## Approach

```
total = 0
for i in 0..n:
    v = value(s[i])
    if i + 1 < n and v < value(s[i+1]):
        total -= v
    else:
        total += v
```

Trace for `"MCMXCIV"`:

| i | symbol | value | next | action | total |
|---|---|---|---|---|---|
| 0 | M | 1000 | C (100) | add | 1000 |
| 1 | C | 100 | M (1000) | subtract | 900 |
| 2 | M | 1000 | X (10) | add | 1900 |
| 3 | X | 10 | C (100) | subtract | 1890 |
| 4 | C | 100 | I (1) | add | 1990 |
| 5 | I | 1 | V (5) | subtract | 1989 |
| 6 | V | 5 | (none) | add | 1994 |

**Language mechanics.** Mapping a symbol to its value: a Python `dict`, a C `switch` statement
(compiles to a jump table), or a Rust `match` expression. A `switch` with one `case` per symbol is
the idiomatic C answer for a small fixed alphabet.

## Complexity

- **Time:** O(n), with n ≤ 15.
- **Space:** O(1).

## Common mistakes

- Peeking at `s[i+1]` on the last character (out of bounds). Guard with `i + 1 < n`.
- Hard-coding the six pairs and missing one, or treating `"IIV"` style inputs (they're invalid and
  won't appear, so don't over-engineer).
- C: `switch` cases without `return` or `break` fall through to the next case.

## Going further

- Scanning **right to left** gives an equally neat version: add a symbol if it's ≥ the largest
  value seen so far to its right, otherwise subtract it.
- The reverse direction, integer → Roman, is the next problem, and uses a greedy algorithm.
""",
    solution=r'''VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}

def roman_to_int(s):
    total = 0
    n = len(s)
    for i in range(n):
        v = VALUES[s[i]]
        # Peek at the next symbol (if any). A smaller value before a larger one is one of the
        # subtractive pairs (IV, IX, XL, XC, CD, CM), so it counts negatively.
        if i + 1 < n and v < VALUES[s[i + 1]]:
            total -= v
        else:
            total += v    # normal case, and always for the last symbol
    return total
''',
    refs={
        "c": r'''static int roman_value(char c) {
    switch (c) {                 /* each case returns, so no fall-through */
        case 'I': return 1;
        case 'V': return 5;
        case 'X': return 10;
        case 'L': return 50;
        case 'C': return 100;
        case 'D': return 500;
        case 'M': return 1000;
        default:  return 0;
    }
}

long long roman_to_int(char* s) {
    long long total = 0;
    for (size_t i = 0; s[i] != '\0'; i++) {
        int v = roman_value(s[i]);
        /* s[i+1] is '\0' on the last symbol, whose value is 0, so v < 0 is never true:
           the terminator doubles as the bounds check. */
        if (v < roman_value(s[i + 1])) total -= v;
        else total += v;
    }
    return total;
}''',
        "cpp": r'''long long romanToInt(string s) {
    auto val = [](char c) {
        switch (c) {
            case 'I': return 1;   case 'V': return 5;   case 'X': return 10;
            case 'L': return 50;  case 'C': return 100; case 'D': return 500;
            case 'M': return 1000;
        }
        return 0;
    };
    long long total = 0;
    for (size_t i = 0; i < s.size(); ++i) {
        int v = val(s[i]);
        if (i + 1 < s.size() && v < val(s[i + 1])) total -= v;
        else total += v;
    }
    return total;
}''',
        "rust": r'''fn value(c: u8) -> i64 {
    match c {
        b'I' => 1,
        b'V' => 5,
        b'X' => 10,
        b'L' => 50,
        b'C' => 100,
        b'D' => 500,
        b'M' => 1000,
        _ => 0,
    }
}

pub fn roman_to_int(s: String) -> i64 {
    let b = s.as_bytes();
    let mut total = 0;
    for i in 0..b.len() {
        let v = value(b[i]);
        if i + 1 < b.len() && v < value(b[i + 1]) {
            total -= v;
        } else {
            total += v;
        }
    }
    total
}''',
    },
    tests=[["LVIII"], ["MCMXCIV"], ["I"], ["III"], ["IV"], ["IX"], ["XL"], ["XC"], ["CD"], ["CM"],
           ["MMMCMXCIX"], ["MMXXVI"], ["DCCCXLVIII"], ["CDXLIV"]],
))

# ================================================================ 11. integer to roman
PROBLEMS.append(dict(
    id="integer-to-roman-numeral",
    title="Integer to Roman",
    difficulty=2,
    tags=["string", "greedy", "math"],
    fn="int_to_roman",
    params=[["num", "int"]],
    returns="str",
    statement=r"""
Convert an integer from 1 to 3999 into a Roman numeral in **standard form**.

| symbol | I | V | X | L | C | D | M |
|---|---|---|---|---|---|---|---|
| value | 1 | 5 | 10 | 50 | 100 | 500 | 1000 |

Standard form rules:

- Symbols are written from largest to smallest value.
- The subtractive forms `IV` (4), `IX` (9), `XL` (40), `XC` (90), `CD` (400) and `CM` (900) are
  used instead of four repeated symbols: 4 is `IV`, never `IIII`; 90 is `XC`, never `LXXXX`.
- `I`, `X`, `C`, `M` may repeat at most three times in a row; `V`, `L`, `D` never repeat.

These rules give every number exactly one representation.
""",
    constraints=["1 ≤ num ≤ 3999"],
    example_notes=["1000 = M, 900 = CM, 90 = XC, 4 = IV.", "50 + 5 + 3 = L + V + III."],
    hints=[
        "Treat the subtractive pairs as symbols of their own: there are 13 \"symbols\" from M (1000) down to I (1), including CM (900), CD (400), XC (90), etc.",
        "Greedy: repeatedly take the largest symbol whose value fits in what remains, append it, and subtract.",
        "Process the 13 values in decreasing order with a `while num >= value` loop for each.",
    ],
    explanation=r"""
## Intuition

Paying an amount with the fewest banknotes: always hand over the largest note that fits. That
**greedy** strategy produces standard Roman numerals *if* the subtractive pairs are treated as
extra "notes":

```
1000 900 500 400 100 90 50 40 10 9 5 4 1
 M    CM  D   CD  C  XC  L XL  X IX V IV I
```

With these 13 symbols, greedy never produces four repeats in a row (it would have chosen the next
bigger symbol instead), so the output is automatically in standard form.

## Approach

```
for (value, symbol) in table (descending):
    while num >= value:
        out += symbol
        num -= value
```

Trace for `1994`:

| value | symbol | taken | remaining |
|---|---|---|---|
| 1000 | M | 1 | 994 |
| 900 | CM | 1 | 94 |
| 500..100 | | 0 | 94 |
| 90 | XC | 1 | 4 |
| 50..5 | | 0 | 4 |
| 4 | IV | 1 | 0 |

Result `"MCMXCIV"`.

An alternative is **digit-by-digit**: the thousands, hundreds, tens and units digits each map to a
fixed string from a lookup table (`["", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM"]`
for hundreds, etc.).

## Complexity

- **Time:** O(1): at most 13 table entries and at most 15 output characters (`MMMDCCCLXXXVIII`).
- **Space:** O(1).

## Common mistakes

- Leaving the subtractive pairs out of the table: greedy then outputs `IIII` for 4.
- Table not in descending order: greedy must try bigger values first.
- Using `if` instead of `while`: 3000 needs `M` three times.
- C: allocating too small a buffer. The longest standard numeral in range has 15 characters, so
  16 bytes with the terminator; allocating a little more is fine.

## Going further

Greedy is *not* always optimal for coin change (with coins 1, 3, 4, greedy pays 6 as 4+1+1, but
3+3 is better). It works here because the Roman system was designed around it. When greedy might
fail you need dynamic programming, which a later track covers.
""",
    solution=r'''# The 7 basic symbols plus the 6 subtractive pairs, in strictly decreasing order.
TABLE = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
         (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]

def int_to_roman(num):
    out = []
    for value, symbol in TABLE:
        # Greedy: use the biggest symbol that still fits, as many times as it fits.
        # Including 900, 400, 90, 40, 9, 4 is what prevents forms like "IIII".
        while num >= value:
            out.append(symbol)
            num -= value
    # Every number >= 1 is fully paid off by the time we reach "I".
    return "".join(out)
''',
    refs={
        "c": r'''char* int_to_roman(long long num) {
    static const int values[] = {1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1};
    static const char* symbols[] = {"M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"};
    char* out = malloc(32);          /* longest result (3888) is 15 chars + '\0' */
    size_t w = 0;
    for (int k = 0; k < 13; k++) {
        while (num >= values[k]) {
            size_t len = strlen(symbols[k]);      /* 1 or 2 characters */
            memcpy(out + w, symbols[k], len);
            w += len;
            num -= values[k];
        }
    }
    out[w] = '\0';
    return out;
}''',
        "cpp": r'''string intToRoman(long long num) {
    static const vector<pair<int, string>> table = {
        {1000, "M"}, {900, "CM"}, {500, "D"}, {400, "CD"}, {100, "C"}, {90, "XC"},
        {50, "L"}, {40, "XL"}, {10, "X"}, {9, "IX"}, {5, "V"}, {4, "IV"}, {1, "I"}};
    string out;
    for (const auto& [value, symbol] : table)      // structured bindings (C++17)
        while (num >= value) { out += symbol; num -= value; }
    return out;
}''',
        "rust": r'''pub fn int_to_roman(num: i64) -> String {
    const TABLE: [(i64, &str); 13] = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
        (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ];
    let mut num = num;
    let mut out = String::new();
    for &(value, symbol) in TABLE.iter() {
        while num >= value {
            out.push_str(symbol);
            num -= value;
        }
    }
    out
}''',
    },
    tests=[[1994], [58], [1], [3], [4], [9], [14], [40], [90], [400], [900], [3888], [3999], [2026], [444], [1000]],
))

# ================================================================ 12. caesar cipher
_r = _rng(412)
PROBLEMS.append(dict(
    id="caesar-cipher-shift",
    title="Caesar Cipher",
    difficulty=1,
    tags=["string", "math", "modulo"],
    fn="caesar_cipher",
    params=[["s", "str"], ["k", "int"]],
    returns="str",
    statement=r"""
Encrypt `s` with a **Caesar cipher** with shift `k`: replace every letter with the letter `k`
positions later in the alphabet, wrapping around from `z` back to `a`.

- Uppercase letters stay uppercase and lowercase stay lowercase (`'Z'` shifted by 1 is `'A'`).
- Every character that is not an English letter (digits, spaces, punctuation) is copied unchanged.
- `k` may be larger than 26.

`s` is printable ASCII.
""",
    constraints=["0 ≤ len(s) ≤ 10⁴", "0 ≤ k ≤ 10⁹"],
    example_notes=["Each letter moves 3 places: H→K, e→h, ... and the comma, space and ! stay.", "Wrap-around: x→a, y→b, z→c."],
    hints=[
        "Turn a letter into its position 0–25 (`c - 'a'`), add the shift, wrap with `% 26`, and turn it back into a letter.",
        "Handle uppercase and lowercase separately: each has its own base (`'A'` or `'a'`).",
        "Reduce `k % 26` once at the start. Besides being tidy, it keeps intermediate values small (important in C/Rust if you use narrow types).",
    ],
    explanation=r"""
## Intuition

The alphabet is a **circle** of 26 positions, and modular arithmetic is how you walk around a
circle. The recipe for any "rotate within a range" problem is: shift to a 0-based position,
add, take `% size`, shift back.

## Approach

```
k = k % 26
for each character c:
    if 'a' <= c <= 'z':  c = 'a' + (c - 'a' + k) % 26
    elif 'A' <= c <= 'Z': c = 'A' + (c - 'A' + k) % 26
    (otherwise unchanged)
```

Worked example, `'y'` with `k = 3`: position `24`, `24 + 3 = 27`, `27 % 26 = 1`, `'a' + 1 = 'b'`.

| char | position | +3 | %26 | result |
|---|---|---|---|---|
| x | 23 | 26 | 0 | a |
| y | 24 | 27 | 1 | b |
| z | 25 | 28 | 2 | c |
| H | 7 | 10 | 10 | K |

**Language mechanics.** Python needs `ord` and `chr` to convert between characters and numbers.
In C and C++ a `char` *is* a number, so `'a' + 1` is already `'b'`. In Rust, bytes (`u8`) support
arithmetic directly; `char`s do not, so work with `as_bytes()` and convert back with `as char`.

## Complexity

- **Time:** O(n).
- **Space:** O(n) for the output.

## Common mistakes

- Forgetting the wrap-around: `'z' + 1` is `'{'` in ASCII.
- Applying the lowercase formula to uppercase letters (or shifting punctuation).
- Not reducing `k`: with `k = 10⁹`, `c - 'a' + k` overflows a C `int`, and in Rust adding to a
  `u8` panics. Reduce `k % 26` first so the sum stays below 51.
- **Decrypting** (shift by `-k`): in C, C++ and Rust `%` can return a negative number for negative
  operands. Use `(x % 26 + 26) % 26`, or shift by `26 - k % 26` instead.

## Going further

- **ROT13** is `k = 13`, which is its own inverse.
- Breaking a Caesar cipher: try all 26 shifts and pick the one whose letter frequencies look most
  like English (`e`, `t`, `a` most common). The **Vigenère cipher** uses a different shift per
  position, cycling through a keyword.
""",
    solution=r'''def caesar_cipher(s, k):
    # Shifting by 26 is a full lap around the alphabet, so only k mod 26 matters.
    k %= 26
    out = []
    for c in s:
        if "a" <= c <= "z":
            # position 0..25 -> add shift -> wrap around the circle -> back to a letter
            out.append(chr(ord("a") + (ord(c) - ord("a") + k) % 26))
        elif "A" <= c <= "Z":
            # same recipe, but measured from 'A' so case is preserved
            out.append(chr(ord("A") + (ord(c) - ord("A") + k) % 26))
        else:
            out.append(c)   # digits, spaces, punctuation pass through unchanged
    return "".join(out)
''',
    refs={
        "c": r'''char* caesar_cipher(char* s, long long k) {
    int shift = (int)(k % 26);                 /* reduce first: keeps sums small */
    size_t n = strlen(s);
    char* out = malloc(n + 1);
    for (size_t i = 0; i < n; i++) {
        char c = s[i];
        if (c >= 'a' && c <= 'z') c = (char)('a' + (c - 'a' + shift) % 26);
        else if (c >= 'A' && c <= 'Z') c = (char)('A' + (c - 'A' + shift) % 26);
        out[i] = c;                            /* chars are small integers */
    }
    out[n] = '\0';
    return out;
}''',
        "cpp": r'''string caesarCipher(string s, long long k) {
    int shift = k % 26;
    for (char& c : s) {
        if (islower((unsigned char)c)) c = 'a' + (c - 'a' + shift) % 26;
        else if (isupper((unsigned char)c)) c = 'A' + (c - 'A' + shift) % 26;
    }
    return s;
}''',
        "rust": r'''pub fn caesar_cipher(s: String, k: i64) -> String {
    let shift = (k % 26) as u8;             // 0..25, so b - base + shift <= 50: no u8 overflow
    s.bytes()
        .map(|b| match b {
            b'a'..=b'z' => (b'a' + (b - b'a' + shift) % 26) as char,
            b'A'..=b'Z' => (b'A' + (b - b'A' + shift) % 26) as char,
            _ => b as char,
        })
        .collect()
}''',
    },
    lang_notes={
        "rust": "Arithmetic on `u8` that exceeds 255 panics in debug builds. Reducing `k % 26` first and using byte ranges (`b'a'..=b'z'`) in a `match` keeps every intermediate value tiny.",
    },
    tests=[
        ["Hello, World!", 3], ["xyz", 3], ["", 5], ["abc", 0], ["abc", 26], ["Zz", 1],
        ["The quick brown fox jumps over the lazy dog.", 13], ["ABC xyz 123", 1000000000],
        ["Shift by 25!", 25], [_rand_str(_r, 4000, PRINTABLE), 777],
    ],
))

# ================================================================ 13. longest substring without repeating
_r = _rng(413)
PROBLEMS.append(dict(
    id="longest-substring-no-repeats",
    title="Longest Substring Without Repeating Characters",
    difficulty=2,
    tags=["string", "sliding window"],
    fn="length_of_longest_substring",
    params=[["s", "str"]],
    returns="int",
    statement=r"""
Return the length of the longest **substring** (contiguous block of characters) of `s` in which
no character appears more than once.

`s` consists of printable ASCII characters (letters, digits, symbols and spaces) and may be empty.
""",
    constraints=["0 ≤ len(s) ≤ 5·10⁴", "`s` is printable ASCII"],
    example_notes=["`abc` is the longest; `abca` would repeat `a`.", "Every substring longer than 1 repeats `b`."],
    hints=[
        "Checking every substring is O(n²) substrings × O(n) to check each. Think about a window `[left, right]` that only ever moves forward.",
        "Extend the window to the right one character at a time. If the new character is already inside the window, the window must shrink from the left until it isn't.",
        "Remember the last index where each character appeared. If `s[right]` was last seen at index `p ≥ left`, jump `left` straight to `p + 1`.",
        "After placing `s[right]`, the window `[left, right]` is repeat-free; its length `right - left + 1` is a candidate answer.",
    ],
    explanation=r"""
## Intuition

Brute force looks at every substring. But notice: if `s[i..j]` contains a repeat, so does every
longer substring starting at `i`, and if `s[i..j]` has no repeats, neither does any substring of
it. That monotonic structure is the signal for a **sliding window**: a range `[left, right]` whose
right edge always advances and whose left edge only moves forward when the window becomes invalid.

## Approach

Keep `last[c]` = the most recent index where character `c` appeared.

```
left = 0, best = 0
for right in 0..n:
    c = s[right]
    if c was seen at index p and p >= left:   # the repeat is inside the window
        left = p + 1                          # jump past it
    last[c] = right
    best = max(best, right - left + 1)
```

The `p >= left` check matters: an old occurrence **before** the window is irrelevant and must not
move `left` backwards.

Trace for `"abcabcbb"`:

| right | char | last seen | left | window | best |
|---|---|---|---|---|---|
| 0 | a | n/a | 0 | `a` | 1 |
| 1 | b | n/a | 0 | `ab` | 2 |
| 2 | c | n/a | 0 | `abc` | 3 |
| 3 | a | 0 | 1 | `bca` | 3 |
| 4 | b | 1 | 2 | `cab` | 3 |
| 5 | c | 2 | 3 | `abc` | 3 |
| 6 | b | 4 | 5 | `cb` | 3 |
| 7 | b | 6 | 7 | `b` | 3 |

And `"abba"` shows why `p >= left` is needed: at the final `a`, `last['a'] = 0` but `left` is
already 2, so `left` must stay at 2 (window `ba`, length 2).

Invariant: after each iteration, `s[left..right]` has no repeated characters and is the longest
such window ending at `right`.

## Complexity

- **Time:** O(n). `right` moves n times; `left` only jumps forward.
- **Space:** O(Σ) for the last-seen table: 128 entries for ASCII, a constant.

## Common mistakes

- Moving `left` to `last[c] + 1` without checking it's inside the window, which can move `left`
  backwards (`"abba"` → answer 3 instead of 2).
- Updating `best` before fixing `left`.
- Using a set and removing only `s[left]` once instead of looping until the duplicate is gone (the
  set version needs a `while` loop).
- Forgetting the empty string (answer 0).

## Going further

The same window template solves "longest substring with at most k distinct characters",
"minimum window substring" (smallest window containing all of `t`'s characters), and "longest
repeating character replacement". In each, decide what makes the window *valid*, grow on the
right, and shrink on the left while invalid.
""",
    solution=r'''def length_of_longest_substring(s):
    last = {}        # character -> most recent index where it appeared
    left = 0         # window is s[left:right+1]
    best = 0
    for right, c in enumerate(s):
        # If c already occurs inside the current window, the window must start after that
        # occurrence. Occurrences before `left` are outside the window and must be ignored,
        # otherwise left could move backwards (try "abba").
        if c in last and last[c] >= left:
            left = last[c] + 1
        last[c] = right
        # The window now contains no repeats; it is the longest valid one ending at `right`.
        best = max(best, right - left + 1)
    return best
''',
    refs={
        "c": r'''long long length_of_longest_substring(char* s) {
    int last[128];                       /* ASCII: index by the byte value */
    for (int k = 0; k < 128; k++) last[k] = -1;
    long long best = 0;
    int left = 0;
    for (int right = 0; s[right] != '\0'; right++) {
        unsigned char c = (unsigned char)s[right];
        if (last[c] >= left) left = last[c] + 1;   /* -1 is never >= left */
        last[c] = right;
        if (right - left + 1 > best) best = right - left + 1;
    }
    return best;
}''',
        "cpp": r'''long long lengthOfLongestSubstring(string s) {
    vector<int> last(128, -1);
    int left = 0;
    long long best = 0;
    for (int right = 0; right < (int)s.size(); ++right) {
        unsigned char c = s[right];
        if (last[c] >= left) left = last[c] + 1;
        last[c] = right;
        best = max(best, (long long)(right - left + 1));
    }
    return best;
}''',
        "rust": r'''pub fn length_of_longest_substring(s: String) -> i64 {
    // usize::MAX as "never seen" would complicate comparisons, so store index + 1
    // (0 means unseen) and keep `left` as a plain index.
    let mut last = [0usize; 128];
    let mut left = 0usize;
    let mut best = 0usize;
    for (right, &c) in s.as_bytes().iter().enumerate() {
        let seen = last[c as usize];      // previous index + 1, or 0
        if seen > left {                  // i.e. previous index >= left
            left = seen;                  // previous index + 1
        }
        last[c as usize] = right + 1;
        best = best.max(right + 1 - left);
    }
    best as i64
}''',
    },
    lang_notes={
        "rust": "Indices are `usize` (unsigned), so a `-1` sentinel isn't available. Storing `index + 1` with `0` meaning \"never seen\" is a common trick; then \"previous index ≥ left\" becomes `seen > left`.",
    },
    tests=[
        ["abcabcbb"], ["bbbbb"], ["pwwkew"], [""], [" "], ["abba"], ["dvdf"], ["au"], ["tmmzuxt"],
        [string.printable[:95]], [_rand_str(_r, 20000, PRINTABLE)], [_rand_str(_r, 30000, "abcdefghijklmnop")],
    ],
))

# ================================================================ 14. atoi
PROBLEMS.append(dict(
    id="string-to-integer-atoi",
    title="String to Integer (atoi)",
    difficulty=2,
    tags=["string", "parsing", "overflow"],
    fn="my_atoi",
    params=[["s", "str"]],
    returns="int",
    statement=r"""
Implement a function that parses a 32-bit signed integer from the start of a string, following
these rules **exactly, in order**:

1. **Whitespace:** skip any leading space characters `' '` (only the space character counts).
2. **Sign:** if the next character is `'-'` or `'+'`, read it; the result is negative for `'-'`.
   At most one sign character is allowed. If no sign is present, the number is positive.
3. **Digits:** read consecutive digit characters `0`–`9` until a non-digit or the end of the string.
   Everything after that is ignored. Leading zeros are allowed (`"0042"` is 42).
4. **No digits:** if step 3 read no digits, the result is `0`.
5. **Clamp:** if the value is outside `[−2³¹, 2³¹ − 1]` = `[−2147483648, 2147483647]`, clamp it
   to the nearest end of that range.

Return the result. `s` is printable ASCII.
""",
    constraints=["0 ≤ len(s) ≤ 200", "`s` is printable ASCII"],
    example_notes=["Leading spaces skipped, `-` read, then the digits 42.", "Digits stop at the first non-digit; the rest is ignored."],
    hints=[
        "Follow the rules as a sequence of small loops/ifs, with one index `i` that only moves forward.",
        "Build the number digit by digit: `value = value * 10 + (c - '0')`.",
        "Clamping: in Python you can clamp at the end, but in C/Rust the value could overflow even a 64-bit integer (200 digits!). Stop as soon as the value exceeds 2³¹.",
        "Tricky inputs: `\"+-12\"` (second sign is not a digit → 0), `\"   -\"` → 0, `\"-91283472332\"` → −2147483648.",
    ],
    explanation=r"""
## Intuition

Parsing problems reward **literalness**. The statement is effectively a small state machine
(whitespace → sign → digits → done), and the cleanest code mirrors it with one index that moves
forward through each phase. Resist "clever" shortcuts like `int(s.strip())`: they implement
*different* rules.

## Approach

```
i = 0
while i < n and s[i] == ' ': i += 1                 # 1. whitespace
sign = 1
if i < n and s[i] in '+-':                          # 2. one optional sign
    sign = -1 if s[i] == '-' else 1; i += 1
value = 0
while i < n and s[i] is a digit:                    # 3. digits
    value = value * 10 + digit(s[i]); i += 1
    if value > 2^31: break                          # already out of range either way
value *= sign
clamp to [-2^31, 2^31 - 1]                          # 4./5.
```

Traces:

| input | after spaces | sign | digits read | raw | result |
|---|---|---|---|---|---|
| `"   -42"` | `-42` | − | 42 | −42 | −42 |
| `"4193 with words"` | same | + | 4193 | 4193 | 4193 |
| `"words 987"` | same | + | none | 0 | 0 |
| `"-91283472332"` | same | − | 91283472332 (capped early) | < −2³¹ | −2147483648 |
| `"+-12"` | same | + | none (`-` isn't a digit) | 0 | 0 |

**Why stop early at 2³¹?** Once `value > 2³¹`, more digits can only make it bigger, and either sign
then clamps. Stopping keeps `value` below about `2³¹ × 10 + 9`, which fits comfortably in a 64-bit
integer. Without it, a 200-digit input overflows `long long` in C (undefined behaviour) and panics
in Rust debug builds. Python's big integers don't overflow, but bounding the work is still good
practice.

**Note the asymmetry:** the range is `[−2147483648, 2147483647]`. `"-2147483648"` is exactly
representable; `"2147483648"` clamps down to `2147483647`.

## Complexity

- **Time:** O(n), one pass.
- **Space:** O(1).

## Common mistakes

- Skipping *all* whitespace (`isspace`, `strip()`): the spec says only `' '`. Tabs/newlines aren't
  in these inputs, but the habit of reading the spec literally matters.
- Accepting multiple signs, or a sign after whitespace that comes after digits.
- Clamping before applying the sign (you'd clamp `2147483648` to `2147483647` and then negate to
  `-2147483647`, which is wrong; the answer for `"-2147483648"` is `-2147483648`).
- Overflow in the accumulator in C/C++/Rust (see above).
- Python's `int()` accepts underscores (`int("1_000")`), surrounding whitespace, and raises on
  trailing junk: not this spec.

## Going further

- C's real `atoi` has *undefined* behaviour on overflow; `strtol` clamps and sets `errno = ERANGE`,
  and reports where parsing stopped through its `endptr` argument. Read its man page and compare.
- Extend the parser to hexadecimal (`0x1F`) or to floating-point (`"3.14e-2"`), the latter being a
  surprisingly hard problem to get exactly right.
""",
    solution=r'''INT_MIN, INT_MAX = -2**31, 2**31 - 1

def my_atoi(s):
    n = len(s)
    i = 0
    # 1. Skip leading spaces (only ' ', exactly as specified).
    while i < n and s[i] == " ":
        i += 1
    # 2. At most one optional sign.
    sign = 1
    if i < n and s[i] in "+-":
        if s[i] == "-":
            sign = -1
        i += 1
    # 3. Accumulate digits until the first non-digit.
    value = 0
    while i < n and "0" <= s[i] <= "9":
        value = value * 10 + (ord(s[i]) - ord("0"))
        i += 1
        # Once value exceeds 2^31 the result will clamp no matter what follows, so stop.
        # This mirrors what C/Rust must do to avoid overflowing their 64-bit accumulator.
        if value > 2**31:
            break
    # 4. No digits read -> value is still 0, so the result is 0 regardless of sign.
    value *= sign
    # 5. Clamp into the 32-bit signed range. Note the asymmetric bounds.
    if value < INT_MIN:
        return INT_MIN
    if value > INT_MAX:
        return INT_MAX
    return value
''',
    refs={
        "c": r'''long long my_atoi(char* s) {
    size_t i = 0;
    while (s[i] == ' ') i++;                     /* '\0' stops this loop too */
    int sign = 1;
    if (s[i] == '+' || s[i] == '-') {
        if (s[i] == '-') sign = -1;
        i++;
    }
    long long value = 0;
    while (s[i] >= '0' && s[i] <= '9') {
        value = value * 10 + (s[i] - '0');
        i++;
        /* value <= 2^31 * 10 + 9 at most: no long long overflow. */
        if (value > 2147483648LL) break;
    }
    value *= sign;
    if (value < -2147483648LL) return -2147483648LL;
    if (value > 2147483647LL) return 2147483647LL;
    return value;
}''',
        "cpp": r'''long long myAtoi(string s) {
    size_t i = 0, n = s.size();
    while (i < n && s[i] == ' ') ++i;
    int sign = 1;
    if (i < n && (s[i] == '+' || s[i] == '-')) sign = (s[i++] == '-') ? -1 : 1;
    long long value = 0;
    while (i < n && isdigit((unsigned char)s[i])) {
        value = value * 10 + (s[i++] - '0');
        if (value > (1LL << 31)) break;              // will clamp anyway
    }
    value *= sign;
    return clamp(value, (long long)INT_MIN, (long long)INT_MAX);   // C++17 <algorithm>
}''',
        "rust": r'''pub fn my_atoi(s: String) -> i64 {
    let b = s.as_bytes();
    let n = b.len();
    let mut i = 0;
    while i < n && b[i] == b' ' {
        i += 1;
    }
    let mut sign = 1i64;
    if i < n && (b[i] == b'+' || b[i] == b'-') {
        if b[i] == b'-' {
            sign = -1;
        }
        i += 1;
    }
    let mut value: i64 = 0;
    while i < n && b[i].is_ascii_digit() {
        value = value * 10 + (b[i] - b'0') as i64;
        i += 1;
        if value > 1i64 << 31 {
            break; // prevents i64 overflow (which would panic in debug builds)
        }
    }
    (sign * value).clamp(i32::MIN as i64, i32::MAX as i64)
}''',
    },
    lang_notes={
        "c": "Because every C string ends in `'\\0'`, loops like `while (s[i] == ' ')` and `while (s[i] >= '0' && s[i] <= '9')` stop at the end automatically: the terminator is neither a space nor a digit. No length needed.",
        "rust": "`i64::clamp(lo, hi)` is built in. Converting the bounds with `i32::MIN as i64` documents *why* those are the limits.",
    },
    tests=[
        ["   -42"], ["4193 with words"], ["42"], ["words and 987"], ["-91283472332"], [""], ["   "], ["+"], ["-"],
        ["+-12"], ["-+12"], ["  +0042abc"], ["2147483647"], ["2147483648"], ["-2147483648"], ["-2147483649"],
        ["00000000000000000000000000000000000000000000000000012345"], ["9" * 150], ["-" + "1" * 150],
        ["3.14159"], ["  - 5"], ["0"], ["-0"],
    ],
))

# ================================================================ 15. count and say
PROBLEMS.append(dict(
    id="count-and-say-sequence",
    title="Count and Say",
    difficulty=2,
    tags=["string", "runs", "simulation"],
    fn="count_and_say",
    params=[["n", "int"]],
    returns="str",
    statement=r"""
The **count-and-say** sequence starts with `"1"`. Each later term is produced by *reading the
previous term aloud*: split it into runs of equal digits and, for each run from left to right,
write the run's length followed by the digit.

```
term 1: 1
term 2: 11        (one 1)
term 3: 21        (two 1s)
term 4: 1211      (one 2, one 1)
term 5: 111221    (one 1, one 2, two 1s)
```

Return the `n`-th term as a string.
""",
    constraints=["1 ≤ n ≤ 30"],
    example_notes=["See the table above.", "The first term is defined as \"1\"."],
    hints=[
        "Write a helper that turns one term into the next, then call it `n − 1` times starting from `\"1\"`.",
        "The helper is run-length encoding (like the string-compression problem), but with the count written **before** the digit.",
        "Don't forget to emit the last run.",
    ],
    explanation=r"""
## Intuition

This is **run detection** applied repeatedly. Each step is a run-length encoding of the previous
term with "count then digit" order, so the solution is a loop (over terms) around a loop (over the
characters of one term).

## Approach

```
term = "1"
repeat n - 1 times:
    next = ""
    for each maximal run of digit d with length L in term:
        next += str(L) + d
    term = next
return term
```

Trace from `"1211"`:

| run | length | written |
|---|---|---|
| `1` | 1 | `11` |
| `2` | 1 | `12` |
| `11` | 2 | `21` |

Next term: `"111221"`.

The run-detection loop is identical to the compression problem's: let `i` run to `len(term)`
inclusive and treat the end of the string as a boundary, so the final run needs no special code.

## Complexity

The terms grow by roughly 30% each step (Conway's constant, λ ≈ 1.3036), so term 30 has 4462
characters. Producing term `k` costs O(length of term `k−1`), so the total is dominated by the last
few terms: O(L) overall, where L is the length of the answer (it's a geometric series).

Space: O(L) for the current and next terms.

## Common mistakes

- Writing digit then count (that's the compression problem's order): `"1"` → `"11"` either way, but
  `"21"` would wrongly become `"2111"` instead of `"1211"`.
- Off-by-one in the outer loop: term 1 needs **zero** transformations.
- Forgetting the last run of each term.
- Python: building `next` with `+=` on strings; use a list and `"".join`.
- C: sizing buffers. Each step at most doubles the length (each run of length L produces 2 chars
  when L ≤ 9, and run lengths never exceed 3 in this sequence), so allocate `2 × len + 1` for the
  next term.

## Going further

- Remarkably, no digit other than 1, 2 and 3 ever appears, and no run is longer than 3.
- John Conway proved that every term eventually splits into 92 "elements" that evolve
  independently, and named them after chemical elements. The growth rate is the root of a
  degree-71 polynomial.
""",
    solution=r'''def count_and_say(n):
    term = "1"                         # term 1 by definition
    # Term k is produced from term k-1, so n - 1 transformations are needed.
    for _ in range(n - 1):
        parts = []
        start = 0                      # start index of the current run
        # Let i reach len(term): the end of the string closes the last run.
        for i in range(1, len(term) + 1):
            if i == len(term) or term[i] != term[start]:
                parts.append(str(i - start))   # how many ...
                parts.append(term[start])      # ... of which digit
                start = i
        term = "".join(parts)
    return term
''',
    refs={
        "c": r'''char* count_and_say(long long n) {
    char* term = malloc(2);
    strcpy(term, "1");
    for (long long step = 1; step < n; step++) {
        size_t len = strlen(term);
        /* Each run of length L (L <= 3 here) becomes 2 characters, so 2*len + 1 is enough. */
        char* next = malloc(2 * len + 1);
        size_t w = 0, start = 0;
        for (size_t i = 1; i <= len; i++) {
            if (i == len || term[i] != term[start]) {
                next[w++] = (char)('0' + (i - start));   /* count (a single digit) */
                next[w++] = term[start];                  /* the digit itself */
                start = i;
            }
        }
        next[w] = '\0';
        free(term);                                      /* old term no longer needed */
        term = next;
    }
    return term;
}''',
        "cpp": r'''string countAndSay(long long n) {
    string term = "1";
    for (long long step = 1; step < n; ++step) {
        string next;
        size_t start = 0;
        for (size_t i = 1; i <= term.size(); ++i) {
            if (i == term.size() || term[i] != term[start]) {
                next += to_string(i - start);
                next += term[start];
                start = i;
            }
        }
        term = move(next);       // steal next's buffer instead of copying it
    }
    return term;
}''',
        "rust": r'''pub fn count_and_say(n: i64) -> String {
    let mut term: Vec<u8> = vec![b'1'];
    for _ in 1..n {
        let mut next = Vec::with_capacity(term.len() * 2);
        let mut start = 0;
        for i in 1..=term.len() {
            if i == term.len() || term[i] != term[start] {
                next.push(b'0' + (i - start) as u8);   // run lengths are at most 3
                next.push(term[start]);
                start = i;
            }
        }
        term = next;
    }
    String::from_utf8(term).unwrap()
}''',
    },
    lang_notes={
        "c": "Each iteration allocates the next term and `free`s the previous one, so at most two terms are alive at once. Forgetting the `free` wouldn't change the answer, but it would leak every intermediate term.",
        "rust": "Working with `Vec<u8>` and converting once at the end with `String::from_utf8` avoids repeated UTF-8 checks and `char` conversions inside the hot loop.",
    },
    tests=[[4], [1], [2], [3], [5], [6], [10], [15], [20], [25], [30]],
))

# ================================================================ 16. ransom note
_r = _rng(416)
_mag = _rand_str(_r, 20000, string.ascii_lowercase)
_note_yes = "".join(_r.sample(_mag, 5000))
PROBLEMS.append(dict(
    id="ransom-note-letters",
    title="Ransom Note",
    difficulty=1,
    tags=["string", "counting"],
    fn="can_construct",
    params=[["ransom_note", "str"], ["magazine", "str"]],
    returns="bool",
    statement=r"""
You want to write `ransom_note` by cutting individual letters out of `magazine`. Each letter in
the magazine can be used **at most once**.

Return `true` if the note can be constructed, `false` otherwise.

Both strings consist of lowercase English letters.
""",
    constraints=["0 ≤ len(ransom_note), len(magazine) ≤ 2·10⁴", "only `a`–`z`"],
    example_notes=["The magazine has only one `a`, but the note needs two.", "Two `a`s needed, two `a`s available (plus a spare `b`)."],
    hints=[
        "Order doesn't matter, only how many of each letter you have and need.",
        "Count the magazine's letters (26 counters). Then, for each letter of the note, use one up.",
        "If any counter would go below zero, you've run out of that letter.",
    ],
    explanation=r"""
## Intuition

"Can I build A from the pieces of B?" is a **multiset containment** question: for every letter,
`need[c] ≤ have[c]`. With a 26-letter alphabet, one count array is enough. Count the supply, then
spend it.

## Approach

1. `have[c] += 1` for each letter of `magazine`.
2. For each letter `c` of `ransom_note`: `have[c] -= 1`; if it becomes negative, return `false`.
3. Return `true`.

Trace for `ransom_note = "aab"`, `magazine = "baa"`: `have = {a:2, b:1}`; spend `a` → 1,
`a` → 0, `b` → 0; never negative → `true`.

For `ransom_note = "aa"`, `magazine = "ab"`: `have = {a:1, b:1}`; spend `a` → 0, `a` → −1 →
`false`.

Checking for "negative" *during* the spending loop lets you stop at the first shortage instead of
scanning the whole note.

## Complexity

- **Time:** O(m + r) for magazine length m and note length r.
- **Space:** O(1): 26 counters.

## Common mistakes

- Using membership (`c in magazine`) instead of counts: a single `a` in the magazine would "supply"
  any number of `a`s.
- Removing characters from the magazine string as you go (`magazine.replace(c, "", 1)`): correct
  but O(m) per letter, O(r·m) total.
- Counting the note and the magazine but comparing the wrong way round (`have ≤ need`).

## Going further

- Python: `not (Counter(ransom_note) - Counter(magazine))`: Counter subtraction drops non-positive
  counts, so an empty result means nothing was missing.
- This is the same count-table idea as Valid Anagram, but with `≤` instead of `=`. Many "can you
  form / rearrange" problems reduce to comparing letter counts.
""",
    solution=r'''def can_construct(ransom_note, magazine):
    # Supply: how many of each letter the magazine offers.
    have = [0] * 26
    for c in magazine:
        have[ord(c) - ord("a")] += 1
    # Demand: spend one letter per character of the note.
    for c in ransom_note:
        k = ord(c) - ord("a")
        have[k] -= 1
        if have[k] < 0:
            # We needed one more of this letter than the magazine had.
            return False
    # Every letter was covered (an empty note is always constructible).
    return True
''',
    refs={
        "c": r'''bool can_construct(char* ransom_note, char* magazine) {
    int have[26] = {0};
    for (const char* p = magazine; *p; p++) have[*p - 'a']++;     /* walk to the '\0' */
    for (const char* p = ransom_note; *p; p++) {
        if (--have[*p - 'a'] < 0) return false;                  /* ran out of this letter */
    }
    return true;
}''',
        "cpp": r'''bool canConstruct(string ransomNote, string magazine) {
    array<int, 26> have{};
    for (char c : magazine) ++have[c - 'a'];
    for (char c : ransomNote)
        if (--have[c - 'a'] < 0) return false;
    return true;
}''',
        "rust": r'''pub fn can_construct(ransom_note: String, magazine: String) -> bool {
    let mut have = [0i32; 26];
    for b in magazine.bytes() {
        have[(b - b'a') as usize] += 1;
    }
    for b in ransom_note.bytes() {
        let k = (b - b'a') as usize;
        have[k] -= 1;
        if have[k] < 0 {
            return false;
        }
    }
    true
}''',
    },
    tests=[
        ["aa", "ab"], ["aa", "aab"], ["a", "b"], ["", ""], ["", "abc"], ["a", ""], ["abc", "cba"],
        ["zzz", "zz"], ["hello", "ohell"],
        [_note_yes, _mag], [_note_yes + "z" * 2000, _mag],
    ],
))
