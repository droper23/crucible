# C cheat sheet

Quick reference for solving Crucible problems in C17 (compiled with `clang -std=c17`).
The harness already includes `stdio.h`, `stdlib.h`, `string.h`, `stdbool.h`, `math.h`,
`limits.h`, `stdint.h` and `ctype.h`.

## How Crucible calls your function

| Crucible type | C parameter(s) | returning it |
|---|---|---|
| `int` | `long long x` | `long long` |
| `float` | `double x` | `double` |
| `bool` | `bool x` | `bool` |
| `str` | `char* s` (NUL-terminated) | `char*`: **malloc** it, NUL-terminate |
| `int[]` | `long long* a, int aSize` | `long long*` + set `*returnSize` |
| `str[]` | `char** a, int aSize` | `char**` + set `*returnSize` |
| `int[][]` | `long long** a, int aSize, int* aColSize` | `long long**` + `*returnSize` + `*returnColumnSizes` |
| `list` | `struct ListNode*` (`val`, `next`) | `struct ListNode*` |
| `tree` | `struct TreeNode*` (`val`, `left`, `right`) | `struct TreeNode*` |
| `void` + mutates | write into the array you were given | nothing |

`aColSize[i]` is the length of row `i`. Returned arrays and strings must come from
`malloc` (the harness frees them). Example signatures:

```c
long long sum_array(long long* nums, int numsSize);
long long* two_sum(long long* nums, int numsSize, long long target, int* returnSize);
long long** transpose(long long** grid, int gridSize, int* gridColSize,
                      int* returnSize, int** returnColumnSizes);
```

```c
// Returning an int[]: allocate, fill, report the length.
long long* doubled(long long* nums, int numsSize, int* returnSize) {
    long long* out = malloc(sizeof(long long) * numsSize);
    for (int i = 0; i < numsSize; i++) out[i] = nums[i] * 2;
    *returnSize = numsSize;
    return out;
}
```

`io` problems: write `int main(void)`, read with `scanf`, print with `printf`.

```c
#include <stdio.h>
int main(void) {
    int n; long long x, sum = 0;
    if (scanf("%d", &n) != 1) return 0;
    for (int i = 0; i < n; i++) { scanf("%lld", &x); sum += x; }
    printf("%lld\n", sum);
    return 0;
}
```

## Variables & types

| type | size (macOS arm64) | printf | range |
|---|---|---|---|
| `char` | 1 | `%c` / `%d` | −128…127 (signed on arm64 macOS) |
| `int` | 4 | `%d` | ±2.1·10⁹ (`INT_MAX`) |
| `long long` | 8 | `%lld` | ±9.2·10¹⁸ (`LLONG_MAX`) |
| `size_t` | 8 | `%zu` | unsigned |
| `double` | 8 | `%f` `%.6f` `%g` | |
| `bool` | 1 | `%d` | `true`/`false` (`stdbool.h`) |
| `uint8_t`, `int32_t`… | exact | `%u`, `%d` | from `stdint.h` |

```c
const int N = 100;
long long big = 1LL << 40;     // LL suffix: shift a 64-bit value
double d = 7 / 2;              // 3.0! int division happens first
double e = 7.0 / 2;            // 3.5
int i = (int)3.9;              // 3: casts truncate toward zero
```

## Operators

| op | note |
|---|---|
| `/` | integer division **truncates toward zero**: `-7 / 2 == -3` |
| `%` | sign follows the dividend: `-7 % 3 == -1`. Positive mod: `((a % m) + m) % m` |
| `++ --` | `i++` yields the old value, `++i` the new |
| `& \| ^ ~ << >>` | `>>` on negative signed values is implementation-defined (arithmetic on clang) |
| `&& \|\| !` | short-circuit, result is `int` 0/1 |
| `?:` | `int m = a < b ? a : b;` |
| `+= -= *= /= %= <<= …` | compound assignment |

Signed overflow is **undefined behaviour**. Use `long long` (Crucible ints already are), and
check `a > LLONG_MAX - b` before adding if needed. `abs` is for `int`; use `llabs` for
`long long` and `fabs` for `double`.

## Conditionals & loops

```c
int x = 7, total = 0;
if (x > 10) { total = 1; } else if (x > 5) { total = 2; } else { total = 3; }
switch (x) {
    case 1: case 2: total = 12; break;   // forget break and you fall through
    default: break;
}
for (int i = 0; i < 10; i++) { if (i == 3) continue; if (i == 8) break; total += i; }
while (x > 0) { x /= 2; }
do { x++; } while (x < 3);
```

## Functions

```c
static long long gcd(long long a, long long b) {   // helper: static keeps it file-local
    while (b) { long long t = a % b; a = b; b = t; }
    return a;
}
void swap(long long* a, long long* b) {             // "out params" via pointers
    long long t = *a; *a = *b; *b = t;
}
int cmp_ll(const void* a, const void* b) {          // comparator for qsort
    long long x = *(const long long*)a, y = *(const long long*)b;
    return (x > y) - (x < y);                       // never return x - y (overflow)
}
```

Declare a helper before you use it, or put a prototype at the top.

## Strings

```c
char s[] = "hello";                 // modifiable array with a '\0' at the end
size_t n = strlen(s);               // 5 (O(n): don't call it in a loop condition)
char c = s[0];                      // 'h'
s[0] = toupper(s[0]);
int eq = strcmp("abc", "abd") < 0;  // <0, 0, >0
char buf[32];
strcpy(buf, s); strcat(buf, "!");   // buf must be big enough
snprintf(buf, sizeof buf, "%s-%lld", s, 42LL);   // safest way to build strings
char* found = strchr(s, 'l');       // pointer or NULL; strstr for substrings
long long v = strtoll("123", NULL, 10);
int digit = '7' - '0';              // char arithmetic
int isd = isdigit('7'), isa = isalpha('x');
char* out = malloc(n + 1);          // returning a string: +1 for '\0'
memcpy(out, s, n + 1);
free(out);
```

## Arrays

```c
long long a[5] = {5, 3, 1};               // rest zero-filled; fixed size
int counts[26] = {0};                     // frequency table
int len = sizeof(a) / sizeof(a[0]);       // only works on real arrays, not pointers
long long* dyn = calloc(100, sizeof *dyn);  // zeroed heap array
dyn = realloc(dyn, 200 * sizeof *dyn);    // grow (keep the result!)
memset(counts, 0, sizeof counts);         // zero bytes; memset(x, -1, …) gives -1s
memcpy(dyn, a, sizeof a);
qsort(a, 5, sizeof a[0], cmp_ll);         // sort with a comparator
for (int i = 0, j = len - 1; i < j; i++, j--) { long long t = a[i]; a[i] = a[j]; a[j] = t; }  // reverse
free(dyn);
```

Min / max / sum: write the loop. `fmin`/`fmax` exist for doubles only.

```c
long long mn = LLONG_MAX, mx = LLONG_MIN, sum = 0;
for (int i = 0; i < numsSize; i++) {
    if (nums[i] < mn) mn = nums[i];
    if (nums[i] > mx) mx = nums[i];
    sum += nums[i];
}
```

2-D array on the heap (the shape Crucible returns):

```c
long long** g = malloc(rows * sizeof *g);
int* colSizes = malloc(rows * sizeof(int));
for (int r = 0; r < rows; r++) { g[r] = calloc(cols, sizeof **g); colSizes[r] = cols; }
*returnSize = rows; *returnColumnSizes = colSizes;
```

## Hash maps & sets

C has none built in. Options, in order of preference:

- **Direct addressing** when keys are small: `int seen[100001]`, `int freq[26]`, or an
  offset (`seen[x + 50000]`) for negatives.
- **Sort + two pointers / binary search** (`qsort` then `bsearch`) instead of a map.
- A small open-addressing table:

```c
#define CAP (1 << 16)                        // power of two > 2 × number of keys
static long long keys[CAP]; static int vals[CAP]; static bool used[CAP];
static unsigned slot(long long k) {
    unsigned long long h = (unsigned long long)k * 0x9E3779B97F4A7C15ULL;
    unsigned i = (unsigned)(h >> 48) & (CAP - 1);
    while (used[i] && keys[i] != k) i = (i + 1) & (CAP - 1);   // linear probing
    return i;
}
void put(long long k, int v) { unsigned i = slot(k); used[i] = true; keys[i] = k; vals[i] = v; }
int get(long long k, int dflt) { unsigned i = slot(k); return used[i] ? vals[i] : dflt; }
```

Static tables persist across calls: clear them (`memset(used, 0, sizeof used)`) at the
start of your function, since the harness calls it once per test.

## Stacks, queues, heaps

```c
long long stack[1000]; int top = 0;
stack[top++] = 5;                     // push
long long t = stack[--top];           // pop; empty when top == 0

long long queue[1000]; int head = 0, tail = 0;
queue[tail++] = 7;                    // enqueue
long long f = queue[head++];          // dequeue; empty when head == tail
```

Binary min-heap:

```c
long long heap[1 << 16]; int hn = 0;
void hpush(long long v) {
    int i = hn++;
    while (i > 0 && heap[(i - 1) / 2] > v) { heap[i] = heap[(i - 1) / 2]; i = (i - 1) / 2; }
    heap[i] = v;
}
long long hpop(void) {
    long long top = heap[0], last = heap[--hn];
    int i = 0;
    for (;;) {
        int c = 2 * i + 1;
        if (c >= hn) break;
        if (c + 1 < hn && heap[c + 1] < heap[c]) c++;
        if (heap[c] >= last) break;
        heap[i] = heap[c]; i = c;
    }
    heap[i] = last;
    return top;
}
```

## Structs, linked lists, trees

```c
typedef struct { long long x, y; } Point;
Point p = { .x = 1, .y = 2 };
Point* pp = &p; pp->x = 5;                       // -> through a pointer

struct ListNode* node = malloc(sizeof(struct ListNode));
node->val = 1; node->next = NULL;
struct ListNode dummy = {0, NULL};               // stack dummy head
struct ListNode* tail = &dummy;
tail->next = node; tail = node;
// return dummy.next;

int depth(struct TreeNode* r) {
    if (!r) return 0;
    int l = depth(r->left), rr = depth(r->right);
    return 1 + (l > rr ? l : rr);
}
```

## Memory

- `malloc(n)` returns uninitialised memory; `calloc(count, size)` zeroes it; always
  `sizeof` the element type.
- Every `malloc` needs exactly one `free`, except memory you **return** to the harness.
- Large local arrays (> ~1 MB) overflow the stack. Make them `static` or heap-allocate.
- Never return a pointer to a local array: it dies when the function returns.
- `realloc` may move the block; use the returned pointer.

## Common gotchas

- `int` overflow: `1e5 * 1e5` overflows 32 bits. Use `long long` and `1LL * a * b`.
- `scanf("%d", x)` missing `&`, or `%d` for a `long long` (use `%lld`).
- `sizeof(ptr)` is 8, not the array length. Arrays decay to pointers in parameters.
- Off-by-one on string buffers: room for `'\0'`.
- `=` vs `==` in conditions (enable warnings: clang flags most).
- Comparator returning `a - b` can overflow; use `(a > b) - (a < b)`.
- `%` of a negative number is negative.
- Uninitialised locals hold garbage: initialise sums to 0.
