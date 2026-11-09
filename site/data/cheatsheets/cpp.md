# C++ cheat sheet

Quick reference for solving Crucible problems in C++20 (`clang++ -std=c++20`). The
harness includes `<bits/stdc++.h>` (every standard header) and `using namespace std;`,
so `vector`, `string`, `unordered_map`, `sort`… work without prefixes.

## How Crucible calls your function

Function and parameter names are **camelCase** (`two_sum` → `twoSum`).

| Crucible type | C++ parameter | return type |
|---|---|---|
| `int` | `long long` | `long long` |
| `float` | `double` | `double` |
| `bool` | `bool` | `bool` |
| `str` | `string` (by value; `string&` when mutated) | `string` |
| `int[]` | `vector<long long>&` | `vector<long long>` |
| `float[]` / `str[]` | `vector<double>&` / `vector<string>&` | same |
| `int[][]` | `vector<vector<long long>>&` | `vector<vector<long long>>` |
| `list` | `ListNode*` (`val`, `next`) | `ListNode*` |
| `tree` | `TreeNode*` (`val`, `left`, `right`) | `TreeNode*` |
| `void` + mutates | modify the referenced vector | `void` |

```cpp
long long sumArray(vector<long long>& nums) {
    return accumulate(nums.begin(), nums.end(), 0LL);   // 0LL: accumulate in long long!
}
vector<long long> twoSum(vector<long long>& nums, long long target);
void moveZeroes(vector<long long>& nums);               // in place
```

`ListNode(long long x = 0, ListNode* n = nullptr)` and
`TreeNode(long long x = 0, TreeNode* l = nullptr, TreeNode* r = nullptr)` constructors exist.

`io` problems: write `int main()`, read with `cin`, print with `cout`.

```cpp
#include <bits/stdc++.h>
using namespace std;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<long long> a(n);
    for (auto& x : a) cin >> x;
    string line; getline(cin >> ws, line);     // read a whole line
    cout << accumulate(a.begin(), a.end(), 0LL) << '\n';   // '\n', not endl (no flush)
}
```

## Variables & types

```cpp
int i = 42;                      // 32-bit
long long big = 1LL << 40;       // 64-bit: what Crucible ints are
double d = 3.5;
bool ok = true;
char c = 'a';
auto x = 5LL;                    // type deduction
const int N = 1e5 + 5;
constexpr long long MOD = 1'000'000'007;   // digit separators
auto [q, r] = pair{17 / 5, 17 % 5};        // structured bindings
long long inf = LLONG_MAX;       // also numeric_limits<long long>::max()
int asInt = (int)3.9;            // 3; static_cast<int>(3.9) is the C++ spelling
```

## Operators

Same as C: `/` **truncates toward zero** (`-7 / 2 == -3`), `%` takes the dividend's sign
(`-7 % 3 == -1`, positive mod is `((a % m) + m) % m`), signed overflow is undefined.
`int * int` overflows *before* being stored into a `long long`: write `1LL * a * b`.

| need | C++ |
|---|---|
| abs / min / max | `abs(x)`, `min(a, b)`, `max({a, b, c})` (same types!) |
| power | `pow` is floating point; write a loop for exact integer powers |
| gcd / lcm | `gcd(a, b)`, `lcm(a, b)` (`<numeric>`) |
| bit tricks | `__builtin_popcountll(x)`, `__builtin_ctzll(x)`, `63 - __builtin_clzll(x)` (highest set bit, x > 0) |
| clamp | `clamp(v, lo, hi)` |

## Conditionals & loops

```cpp
vector<long long> nums = {3, 1, 2};
long long total = 0;
for (size_t i = 0; i < nums.size(); i++) total += nums[i];
for (long long x : nums) total += x;            // copy each element
for (auto& x : nums) x *= 2;                     // reference: modifies in place
for (int i = (int)nums.size() - 1; i >= 0; i--) {}   // size() is unsigned: cast first!
while (total > 10) total /= 2;
if (total == 5) {} else if (total > 5) {} else {}
string kind = total % 2 ? "odd" : "even";
```

## Functions & lambdas

```cpp
long long gcdLL(long long a, long long b) { return b ? gcdLL(b, a % b) : a; }
void bump(long long& x) { x++; }                 // pass by reference to modify
long long total(const vector<long long>& v) {    // const& avoids copying
    return accumulate(v.begin(), v.end(), 0LL);
}
auto sq = [](long long v) { return v * v; };
long long base = 10;
auto addBase = [&](long long v) { return v + base; };       // capture by reference
function<long long(int)> fib = [&](int n) -> long long {    // recursive lambda
    return n < 2 ? n : fib(n - 1) + fib(n - 2);
};
```

## Strings

```cpp
string s = "Hello, World";
s.size(); s[0]; s.back(); s.substr(7, 5);        // substr(pos, len)
s += "!"; s.push_back('?'); s.pop_back();
s.find("World");                                 // index, or string::npos
if (s.find("xyz") == string::npos) {}
reverse(s.begin(), s.end());
sort(s.begin(), s.end());
transform(s.begin(), s.end(), s.begin(), ::tolower);
to_string(42); stoll("123"); stod("2.5");
string row(5, '.');                              // "....."
stringstream ss("a b c"); string w;
while (ss >> w) {}                               // split on whitespace
bool isDigit = isdigit((unsigned char)s[0]);
string_view sv = s;                              // non-owning view, cheap substr
```

## Vectors

```cpp
vector<long long> a = {5, 3, 1};
vector<long long> z(10, 0);                       // 10 zeros
vector<vector<long long>> grid(3, vector<long long>(4, 0));   // 3×4
a.push_back(4); a.pop_back(); a.back(); a.front();
a.insert(a.begin(), 9); a.erase(a.begin());       // O(n)
a.size(); a.empty(); a.clear(); a.resize(5);
sort(a.begin(), a.end());                         // ascending
sort(a.rbegin(), a.rend());                       // descending
sort(a.begin(), a.end(), [](long long x, long long y) { return x > y; });
stable_sort(a.begin(), a.end());
reverse(a.begin(), a.end());
long long mn = *min_element(a.begin(), a.end());
long long mx = *max_element(a.begin(), a.end());
long long sum = accumulate(a.begin(), a.end(), 0LL);
vector<long long> part(a.begin() + 1, a.begin() + 3);    // "slice" = copy
auto it = lower_bound(a.begin(), a.end(), 3);     // needs a sorted range
a.erase(unique(a.begin(), a.end()), a.end());     // dedupe (after sort)
fill(z.begin(), z.end(), -1);
iota(z.begin(), z.end(), 0);                      // 0, 1, 2, ...
long long c3 = count(a.begin(), a.end(), 3);
```

## Maps & sets

```cpp
unordered_map<long long, int> cnt;               // hash map, O(1) average
cnt[7]++;                                        // [] inserts 0 if missing
if (cnt.count(7)) {}                             // or cnt.contains(7) in C++20
auto f = cnt.find(8);
if (f != cnt.end()) f->second = 1;
cnt.erase(7);
for (auto& [k, v] : cnt) {}
map<string, int> ordered;                        // sorted by key, O(log n)
ordered["b"] = 2; ordered["a"] = 1;
auto first = ordered.begin()->first;             // "a"
unordered_set<long long> seen = {1, 2};
seen.insert(3); seen.count(3); seen.erase(1);
set<long long> ss = {5, 1, 3};
auto nextUp = ss.lower_bound(2);                 // iterator to 3
multiset<long long> ms = {1, 1, 2};
ms.erase(ms.find(1));                            // remove ONE copy
```

Pairs/tuples as keys work in `map`/`set`; `unordered_map<pair<…>>` needs a custom hash,
so encode the pair instead: `key = x * 1000003 + y`.

## Stacks, queues, deques, heaps

```cpp
stack<long long> st; st.push(1); st.top(); st.pop();
queue<long long> q; q.push(1); q.front(); q.pop();
deque<long long> dq; dq.push_front(1); dq.push_back(2); dq.pop_front(); dq.back();
priority_queue<long long> maxHeap;                                  // max on top
priority_queue<long long, vector<long long>, greater<long long>> minHeap;
minHeap.push(5); minHeap.push(1); minHeap.top(); minHeap.pop();
priority_queue<pair<long long, int>, vector<pair<long long, int>>, greater<>> pq;   // Dijkstra
pq.push({0, 0});
auto [dist, node] = pq.top(); pq.pop();
```

## Structs & classes

```cpp
struct Point {
    long long x = 0, y = 0;
    bool operator<(const Point& o) const { return tie(x, y) < tie(o.x, o.y); }
};
class Counter {
public:
    explicit Counter(int start) : n(start) {}
    int next() { return ++n; }
private:
    int n;
};
Point p{1, 2};
Counter c(5);
c.next();
```

## Memory

- Prefer `vector`, `string` and other containers: they free themselves (RAII).
- `new T` / `delete p`, `new T[n]` / `delete[] p` must be paired. Crucible list and tree
  nodes are created with `new ListNode(v)` and you don't need to delete returned nodes.
- `unique_ptr<T> p = make_unique<T>(...)` owns a heap object with no manual `delete`.
- References (`T&`) are aliases; a `vector<T>` parameter **without** `&` is a full copy.
- Don't keep iterators, pointers or references into a vector across `push_back`: it
  may reallocate.

```cpp
ListNode dummy(0);                   // stack-allocated dummy head
ListNode* tail = &dummy;
for (long long v : {1, 2, 3}) { tail->next = new ListNode(v); tail = tail->next; }
ListNode* head = dummy.next;
int depth(TreeNode* r) { return r ? 1 + max(depth(r->left), depth(r->right)) : 0; }
```

## Output formatting & handy algorithms

```cpp
double pi = 3.14159265;
cout << fixed << setprecision(2) << pi << '\n';    // 3.14
printf("%.3f %lld %s\n", pi, 42LL, string("hi").c_str());
vector<long long> v = {4, 1, 3};
vector<long long> pre(v.size() + 1, 0);             // prefix sums: pre[i] = v[0..i)
partial_sum(v.begin(), v.end(), pre.begin() + 1);
bool any = any_of(v.begin(), v.end(), [](long long x) { return x > 3; });
next_permutation(v.begin(), v.end());               // in-place, returns false at the end
nth_element(v.begin(), v.begin() + 1, v.end());     // v[1] is the 2nd smallest: O(n)
long long lo = 0, hi = 1'000'000;                   // binary search on the answer
while (lo < hi) {
    long long mid = lo + (hi - lo) / 2;
    if (mid * mid >= 1'000'000) hi = mid; else lo = mid + 1;
}
cout << lo << '\n';                                 // 1000
```

## Common gotchas

- `accumulate(v.begin(), v.end(), 0)` sums in **int**. Use `0LL` (or `0.0` for doubles).
- `v.size() - 1` when `v` is empty is a huge unsigned number.
- `min(a, 5)` with `a` a `long long` fails to compile: `min(a, 5LL)`.
- `map[key]` inserts missing keys; use `find`/`count` to only check.
- `endl` flushes every time. Use `'\n'` in loops.
- Comparators for `sort` must be strict (`<`, never `<=`) or you get undefined behaviour.
- `int` overflow: `a * b` with two `int`s overflows before widening.
- Erasing from a container while iterating: use the iterator `erase` returns.
