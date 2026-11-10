# langdocs schema

One ES module per language: `site/js/langdocs/<lang>.js` where lang ∈ python, c, cpp, rust, espresso, arm64.
It powers Monaco hover tooltips, completions, and signature help (site/js/ide.js).

```js
// <Language> reference for Crucible's editor (hover / completion / signature help).
export default [
  {
    name: 'heappush',            // identifier as typed (no qualifier). Required.
    owner: 'heapq',              // module / type / namespace that qualifies it ('list', 'str', 'heapq',
                                 //  'std', 'std::vector', 'Vec', 'String', 'Option', 'Iterator', 'HashMap', 'i64').
                                 //  Omit for globals/builtins/keywords. Methods MUST have an owner.
    kind: 'function',            // function | method | type | keyword | macro | constant | module |
                                 //  instruction | directive | snippet
    sig: 'heapq.heappush(heap, item) -> None',   // one-line signature shown as code.
    params: [                    // optional; each label MUST appear verbatim inside sig's parentheses
      { label: 'heap', doc: 'a list maintained as a min-heap' },
      { label: 'item', doc: 'value to push' },
    ],
    returns: 'None (the heap is modified in place)',  // REQUIRED for function/method/macro: return type + meaning
    doc: 'Push *item* onto *heap*, keeping the min-heap invariant. **O(log n)**.',  // markdown, 1–3 sentences, practical
    example: 'h = []\nheapq.heappush(h, 5)',  // REQUIRED: realistic usage, 1–4 lines, valid code
    insert: 'heappush(${1:heap}, ${2:item})', // optional Monaco snippet inserted on completion (default: name)
    header: 'import heapq',      // optional: required import/#include/use line (shown in hover)
    learn: {                     // optional, for entries a problem introduces ("New in this problem" card).
      summary: 'add an item to a heap',   // ≤ 8 words, lower-case tagline
      what: 'Plain-English explanation for a beginner (2–4 sentences): what it does, when to use it.',
      params: { heap: 'the list you keep as a heap; start with []', item: 'the value to add' },
                                 // every part of the call (or asm operand) → plain English, with example values
      returns: 'Nothing (None). The heap list itself changes.',
      example: 'h = []\nheapq.heappush(h, 5)   # h is now [5]',  // every line commented
      watch: ['Pushing onto a plain unsorted list does not heapify it first.'],  // 1–3 pitfalls
    },
  },
]
```

Guidelines
- Every entry needs `example`; function/method/macro entries need `returns`; every parameter in `sig` should have a `params` entry. Validate with `node tools/check_langdocs.mjs <lang>`.
- Accuracy over volume; these are shown to learners. Mention complexity where it matters and the classic gotcha (e.g. `list.sort()` returns None, `strcpy` overflow, `Vec::remove` is O(n), `HashMap::get` returns Option<&V>).
- Cover what competitive / interview-style solutions actually use, plus language keywords (kind 'keyword', with a short doc and a snippet `insert` for block constructs like for/while/if/match/fn).
- Use template literals or plain strings; keep the file valid JS (node --check must pass) and export a plain array.
- Don't duplicate (same owner+name) entries; overloads → one entry, mention variants in doc.
