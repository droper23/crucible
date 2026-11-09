"""Harness self-test: exercises every type in every language. Not shipped."""

TRACK = dict(id="_selftest", title="Self Test", order=999, icon="T", blurb="harness tests", intro="x")

_H = dict(statement="x", hints=["x"], explanation="x", difficulty=1)

PROBLEMS = [
    dict(_H, id="st-sum", title="Sum", fn="sum_array", params=[["nums", "int[]"]], returns="int",
         solution="def sum_array(nums):\n    return sum(nums)\n",
         tests=[[[1, 2, 3]], [[]], [[-5, 10**12]]],
         refs={
             "c": "long long sum_array(long long* nums, int numsSize) { long long s = 0; for (int i = 0; i < numsSize; i++) s += nums[i]; return s; }",
             "cpp": "long long sumArray(vector<long long>& nums) { return accumulate(nums.begin(), nums.end(), 0LL); }",
             "rust": "pub fn sum_array(nums: Vec<i64>) -> i64 { nums.iter().sum() }",
             "espresso": "fn sumArray(nums) {\n  var s = 0\n  for var i in 0..len(nums) { s += nums[i] }\n  return s\n}",
         }),
    dict(_H, id="st-tag", title="Tag", fn="tag_words", params=[["words", "str[]"], ["prefix", "str"]], returns="str[]",
         solution="def tag_words(words, prefix):\n    return [prefix + w for w in words]\n",
         tests=[[["a", "b"], "x-"], [[], "p"], [["é\"q\\", "tab\there"], "ü?"]],
         refs={
             "c": "char** tag_words(char** words, int wordsSize, char* prefix, int* returnSize) {\n char** r = malloc(sizeof(char*) * (wordsSize + 1)); size_t pl = strlen(prefix);\n for (int i = 0; i < wordsSize; i++) { size_t wl = strlen(words[i]); r[i] = malloc(pl + wl + 1); memcpy(r[i], prefix, pl); memcpy(r[i] + pl, words[i], wl + 1); }\n *returnSize = wordsSize; return r; }",
             "cpp": "vector<string> tagWords(vector<string>& words, string prefix) { vector<string> r; for (auto& w : words) r.push_back(prefix + w); return r; }",
             "rust": "pub fn tag_words(words: Vec<String>, prefix: String) -> Vec<String> { words.iter().map(|w| format!(\"{}{}\", prefix, w)).collect() }",
         }),
    dict(_H, id="st-transpose", title="Transpose", fn="transpose", params=[["grid", "int[][]"]], returns="int[][]",
         solution="def transpose(grid):\n    return [list(r) for r in zip(*grid)]\n",
         tests=[[[[1, 2], [3, 4], [5, 6]]], [[[7]]], [[[1, 2, 3]]]],
         refs={
             "c": "long long** transpose(long long** grid, int gridSize, int* gridColSize, int* returnSize, int** returnColumnSizes) {\n int R = gridSize, C = gridColSize[0];\n long long** r = malloc(sizeof(long long*) * C); *returnColumnSizes = malloc(sizeof(int) * C);\n for (int j = 0; j < C; j++) { r[j] = malloc(sizeof(long long) * R); (*returnColumnSizes)[j] = R; for (int i = 0; i < R; i++) r[j][i] = grid[i][j]; }\n *returnSize = C; return r; }",
             "cpp": "vector<vector<long long>> transpose(vector<vector<long long>>& g) { vector<vector<long long>> r(g[0].size(), vector<long long>(g.size())); for (size_t i = 0; i < g.size(); i++) for (size_t j = 0; j < g[0].size(); j++) r[j][i] = g[i][j]; return r; }",
             "rust": "pub fn transpose(grid: Vec<Vec<i64>>) -> Vec<Vec<i64>> { (0..grid[0].len()).map(|j| grid.iter().map(|r| r[j]).collect()).collect() }",
             "espresso": None,
         }),
    dict(_H, id="st-revlist", title="Reverse list", fn="reverse_list", params=[["head", "list"]], returns="list",
         solution="def reverse_list(head):\n    prev = None\n    while head:\n        head.next, prev, head = prev, head, head.next\n    return prev\n",
         tests=[[[1, 2, 3]], [[]], [[5]]],
         refs={
             "c": "struct ListNode* reverse_list(struct ListNode* head) { struct ListNode* prev = NULL; while (head) { struct ListNode* n = head->next; head->next = prev; prev = head; head = n; } return prev; }",
             "cpp": "ListNode* reverseList(ListNode* head) { ListNode* prev = nullptr; while (head) { auto n = head->next; head->next = prev; prev = head; head = n; } return prev; }",
             "rust": "pub fn reverse_list(head: Option<Box<ListNode>>) -> Option<Box<ListNode>> { let (mut prev, mut cur) = (None, head); while let Some(mut n) = cur { cur = n.next.take(); n.next = prev; prev = Some(n); } prev }",
         }),
    dict(_H, id="st-invert", title="Invert tree", fn="invert_tree", params=[["root", "tree"]], returns="tree",
         solution="def invert_tree(root):\n    if root:\n        root.left, root.right = invert_tree(root.right), invert_tree(root.left)\n    return root\n",
         tests=[[[4, 2, 7, 1, 3, 6, 9]], [[]], [[1, None, 2]]],
         refs={
             "c": "struct TreeNode* invert_tree(struct TreeNode* root) { if (root) { struct TreeNode* l = root->left; root->left = invert_tree(root->right); root->right = invert_tree(l); } return root; }",
             "cpp": "TreeNode* invertTree(TreeNode* root) { if (root) { swap(root->left, root->right); invertTree(root->left); invertTree(root->right); } return root; }",
             "rust": "use std::rc::Rc;\nuse std::cell::RefCell;\npub fn invert_tree(root: Option<Rc<RefCell<TreeNode>>>) -> Option<Rc<RefCell<TreeNode>>> { if let Some(n) = root.clone() { let mut b = n.borrow_mut(); let l = b.left.take(); let r = b.right.take(); b.left = invert_tree(r); b.right = invert_tree(l); } root }",
         }),
    dict(_H, id="st-zeroes", title="Move zeroes", fn="move_zeroes", params=[["nums", "int[]"]], returns="void", mutates="nums",
         solution="def move_zeroes(nums):\n    nz = [x for x in nums if x]\n    nums[:] = nz + [0] * (len(nums) - len(nz))\n",
         tests=[[[0, 1, 0, 3, 12]], [[0]], [[1, 2]]],
         refs={
             "c": "void move_zeroes(long long* nums, int numsSize) { int k = 0; for (int i = 0; i < numsSize; i++) if (nums[i]) nums[k++] = nums[i]; while (k < numsSize) nums[k++] = 0; }",
             "cpp": "void moveZeroes(vector<long long>& nums) { stable_partition(nums.begin(), nums.end(), [](long long x) { return x != 0; }); }",
             "rust": "pub fn move_zeroes(nums: &mut Vec<i64>) { let mut k = 0; for i in 0..nums.len() { if nums[i] != 0 { nums[k] = nums[i]; k += 1; } } for i in k..nums.len() { nums[i] = 0; } }",
             "espresso": "fn moveZeroes(nums) {\n  var k = 0\n  for var i in 0..len(nums) {\n    if nums[i] != 0 { nums[k] = nums[i]\n k += 1 }\n  }\n  while k < len(nums) { nums[k] = 0\n k += 1 }\n}",
         }),
    dict(_H, id="st-avg", title="Average", fn="average", params=[["nums", "float[]"]], returns="float",
         solution="def average(nums):\n    return sum(nums) / len(nums)\n",
         tests=[[[1, 2]], [[0.1, 0.2, 0.3]], [[-3.5]]],
         refs={
             "c": "double average(double* nums, int numsSize) { double s = 0; for (int i = 0; i < numsSize; i++) s += nums[i]; return s / numsSize; }",
             "cpp": "double average(vector<double>& nums) { return accumulate(nums.begin(), nums.end(), 0.0) / nums.size(); }",
             "rust": "pub fn average(nums: Vec<f64>) -> f64 { nums.iter().sum::<f64>() / nums.len() as f64 }",
             "espresso": "fn average(nums) {\n  var s = 0.0\n  for var i in 0..len(nums) { s += nums[i] }\n  return s / len(nums)\n}",
         }),
    dict(_H, id="st-even", title="Even", fn="is_even", params=[["n", "int"]], returns="bool",
         solution="def is_even(n):\n    return n % 2 == 0\n",
         tests=[[4], [7], [-2]],
         refs={
             "c": "bool is_even(long long n) { return n % 2 == 0; }",
             "cpp": "bool isEven(long long n) { return n % 2 == 0; }",
             "rust": "pub fn is_even(n: i64) -> bool { n % 2 == 0 }",
             "espresso": "fn isEven(n) {\n  return n - (n / 2) * 2 == 0\n}",
         }),
    dict(_H, id="st-group", title="Group", fn="group_by_len", params=[["words", "str[]"]], returns="str[][]", compare="unordered_deep",
         solution="def group_by_len(words):\n    d = {}\n    for w in words: d.setdefault(len(w), []).append(w)\n    return list(d.values())\n",
         tests=[[["a", "bb", "c", "dd", "eee"]], [[]], [["x"]]],
         refs={
             "c": "char*** group_by_len(char** words, int wordsSize, int* returnSize, int** returnColumnSizes) {\n char*** r = malloc(sizeof(char**) * 64); *returnColumnSizes = calloc(64, sizeof(int)); int map[64]; for (int i = 0; i < 64; i++) map[i] = -1; int g = 0;\n for (int i = 0; i < wordsSize; i++) { int L = strlen(words[i]); if (map[L] < 0) { map[L] = g; r[g] = malloc(sizeof(char*) * wordsSize); g++; } int k = map[L]; r[k][(*returnColumnSizes)[k]++] = words[i]; }\n *returnSize = g; return r; }",
             "cpp": "vector<vector<string>> groupByLen(vector<string>& words) { map<size_t, vector<string>> m; for (auto& w : words) m[w.size()].push_back(w); vector<vector<string>> r; for (auto& [k, v] : m) r.push_back(v); return r; }",
             "rust": "pub fn group_by_len(words: Vec<String>) -> Vec<Vec<String>> { let mut m = std::collections::BTreeMap::new(); for w in words { m.entry(w.len()).or_insert_with(Vec::new).push(w); } m.into_values().collect() }",
         }),
    dict(_H, id="st-io-sum", title="IO sum", kind="io",
         solution="import sys\nprint(sum(map(int, sys.stdin.read().split())))\n",
         tests=["1 2 3\n", "10\n", "-1 1\n"],
         refs={
             "c": "#include <stdio.h>\nint main(void) { long long s = 0, x; while (scanf(\"%lld\", &x) == 1) s += x; printf(\"%lld\\n\", s); return 0; }",
             "cpp": "#include <bits/stdc++.h>\nusing namespace std;\nint main() { long long s = 0, x; while (cin >> x) s += x; cout << s << endl; }",
             "rust": "use std::io::Read;\nfn main() { let mut s = String::new(); std::io::stdin().read_to_string(&mut s).unwrap(); let t: i64 = s.split_whitespace().map(|x| x.parse::<i64>().unwrap()).sum(); println!(\"{}\", t); }",
         }),
    dict(_H, id="st-io-hello", title="IO hello", kind="io",
         solution="print('Hello, Crucible!')\n",
         tests=["", "", ""],
         refs={"espresso": "print(\"Hello, Crucible!\")", "c": "#include <stdio.h>\nint main(void) { puts(\"Hello, Crucible!\"); }"}),
    dict(_H, id="st-asm-sum", title="Asm sum", kind="asm", fn="sum_array", params=[["nums", "int[]"]], returns="int",
         solution="def sum_array(nums):\n    return sum(nums)\n",
         asm_starter="",
         asm_solution=""".text
.globl _sum_array
.p2align 2
_sum_array:            // x0 = nums, x1 = count
    mov x2, #0
1:  cbz x1, 2f
    ldr x3, [x0], #8
    add x2, x2, x3
    sub x1, x1, #1
    b 1b
2:  mov x0, x2
    ret
""",
         tests=[[[1, 2, 3]], [[]], [[-4, 4, 100]]]),
]
for _p in PROBLEMS:
    if "refs" in _p:
        _p["refs"] = {k: v for k, v in _p["refs"].items() if v}
