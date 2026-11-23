"""Autograded exercises for module A15, Software engineering practice."""
from rspec import ex

ex("A15.1", "Merge, search and top-k",
   "Three classic building blocks, written with slices and the standard collections.\n\n"
   "Specification:\n"
   "- merge_sorted(a, b) takes two sorted slices and returns one sorted Vec with every item of both, in a single pass (no sort call).\n"
   "- first_index(items, target) takes a sorted slice and returns Some(index) of the first item equal to target, or None. Halve the range each step: about 20 looks for a million items.\n"
   "- top_k(items, k) returns the k largest values, largest first. Keep a BinaryHeap of at most k items (wrap values in Reverse to make it a min-heap) instead of sorting everything. Fewer than k items returns them all; k = 0 returns an empty Vec.\n\n"
   "Examples:\n- merge_sorted(&[1, 4, 9], &[2, 4]) returns [1, 2, 4, 4, 9]\n- first_index(&[1, 2, 2, 2, 3], 2) returns Some(1)\n- top_k(&[5, 1, 9, 3, 7], 2) returns [9, 7]\n\n"
   "Edge cases: empty slices; duplicates in top_k are kept.",
   r'''use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn merge_sorted(a: &[i32], b: &[i32]) -> Vec<i32> {
    todo!()
}

pub fn first_index(items: &[i32], target: i32) -> Option<usize> {
    todo!()
}

pub fn top_k(items: &[u32], k: usize) -> Vec<u32> {
    todo!()
}
''',
   r'''use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn merge_sorted(a: &[i32], b: &[i32]) -> Vec<i32> {
    let mut out = Vec::with_capacity(a.len() + b.len());
    let (mut i, mut j) = (0, 0);
    while i < a.len() && j < b.len() {
        if a[i] <= b[j] {
            out.push(a[i]);
            i += 1;
        } else {
            out.push(b[j]);
            j += 1;
        }
    }
    out.extend_from_slice(&a[i..]);
    out.extend_from_slice(&b[j..]);
    out
}

pub fn first_index(items: &[i32], target: i32) -> Option<usize> {
    let (mut lo, mut hi) = (0, items.len());
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        if items[mid] < target {
            lo = mid + 1;
        } else {
            hi = mid;
        }
    }
    (lo < items.len() && items[lo] == target).then_some(lo)
}

pub fn top_k(items: &[u32], k: usize) -> Vec<u32> {
    let mut heap = BinaryHeap::with_capacity(k + 1);
    for &x in items {
        heap.push(Reverse(x));
        if heap.len() > k {
            heap.pop();
        }
    }
    let mut out: Vec<u32> = heap.into_iter().map(|Reverse(x)| x).collect();
    out.sort_unstable_by(|a, b| b.cmp(a));
    out
}
''',
   [("Merging two sorted slices", 'assert_eq!(merge_sorted(&[1, 4, 9], &[2, 4]), vec![1, 2, 4, 4, 9]);\nassert_eq!(merge_sorted(&[], &[3, 5]), vec![3, 5]);\nassert_eq!(merge_sorted(&[7], &[]), vec![7]);\nassert_eq!(merge_sorted(&[], &[]), Vec::<i32>::new());\nassert_eq!(merge_sorted(&[1, 2, 3], &[10, 20]), vec![1, 2, 3, 10, 20], "the rest of the longer side is appended");'),
    ("Finding the first match", 'assert_eq!(first_index(&[1, 3, 5, 7], 5), Some(2));\nassert_eq!(first_index(&[1, 2, 2, 2, 3], 2), Some(1), "with duplicates, the first one");\nassert_eq!(first_index(&[1, 3, 5, 7], 1), Some(0));\nassert_eq!(first_index(&[1, 3, 5, 7], 7), Some(3));'),
    ("Missing values", 'assert_eq!(first_index(&[1, 3, 5, 7], 4), None);\nassert_eq!(first_index(&[1, 3, 5, 7], 9), None);\nassert_eq!(first_index(&[1, 3, 5, 7], 0), None);\nassert_eq!(first_index(&[], 1), None);'),
    ("Every position in a large slice", 'let items: Vec<i32> = (0..1000).map(|x| x * 2).collect();\nfor (i, &x) in items.iter().enumerate() {\n    assert_eq!(first_index(&items, x), Some(i));\n    assert_eq!(first_index(&items, x + 1), None);\n}'),
    ("The k largest, largest first", 'assert_eq!(top_k(&[5, 1, 9, 3, 7], 2), vec![9, 7]);\nassert_eq!(top_k(&[4, 4, 1, 4], 3), vec![4, 4, 4], "duplicates are kept");\nassert_eq!(top_k(&[2, 8], 5), vec![8, 2], "fewer than k items: all of them");\nassert_eq!(top_k(&[2, 8], 0), Vec::<u32>::new());\nassert_eq!(top_k(&[], 3), Vec::<u32>::new());'),
    ("top_k uses a heap", 'let src = include_str!("exercise.rs");\nlet body = src.split("pub fn top_k").nth(1).unwrap_or("").split("mod grader_tests").next().unwrap_or("");\nassert!(body.contains("BinaryHeap") || body.contains("heap"), "keep a BinaryHeap of at most k items");')],
   [("    out.extend_from_slice(&b[j..]);\n", ""), ("            hi = mid;\n", "            return Some(mid);\n"),
    ("        if heap.len() > k {", "        if heap.len() >= k {"), ("b.cmp(a)", "a.cmp(b)")],
   ["merge_sorted: walk both slices with two indexes, pushing the smaller front item; then extend with whatever is left of either side.",
    "first_index: keep lo = 0 and hi = items.len(); if items[mid] < target move lo to mid + 1, otherwise hi = mid. At the end check items[lo].",
    "top_k: push Reverse(x) and pop whenever the heap holds more than k; the heap then drops the smallest each time."],
   "Merging is the linear step inside merge sort and inside every database merge join. The binary search form that moves hi down on equality lands on the first match, like slice::partition_point and binary_search_by in the standard library. A bounded heap finds the top k in O(n log k) time and O(k) memory, which matters when n is millions of log lines and k is ten. In production code reach for sort_unstable, binary_search and select_nth_unstable first; writing them once is how you learn their cost and edge cases.",
   eid="A15.1a")

ex("A15.2", "A linked stack",
   "Build the classic singly linked list as a stack. Each node owns the next one through Option<Box<Node<T>>>, which is how Rust expresses 'a pointer that may be null' safely.\n\n"
   "Specification:\n"
   "- Stack::new() is empty; Default does the same.\n"
   "- push(value) adds to the top; pop() removes and returns the top, or None when empty.\n"
   "- peek() returns a reference to the top without removing it.\n"
   "- len() and is_empty() report the size.\n"
   "- reverse() reverses the stack in place by relinking the nodes (no cloning, so it works for any T).\n"
   "- to_vec() returns references to the values from top to bottom.\n\n"
   "Example: after push(1), push(2), push(3), to_vec() is [&3, &2, &1] and pop() is Some(3).\n\n"
   "Hint: Option::take() moves a value out of a field and leaves None behind, which is the key move for linked structures.",
   r'''pub struct Stack<T> {
    head: Option<Box<Node<T>>>,
    len: usize,
}

struct Node<T> {
    value: T,
    next: Option<Box<Node<T>>>,
}

impl<T> Stack<T> {
    pub fn new() -> Self {
        Stack { head: None, len: 0 }
    }

    pub fn push(&mut self, value: T) {
        todo!()
    }

    pub fn pop(&mut self) -> Option<T> {
        todo!()
    }

    pub fn peek(&self) -> Option<&T> {
        todo!()
    }

    pub fn len(&self) -> usize {
        self.len
    }

    pub fn is_empty(&self) -> bool {
        self.len == 0
    }

    pub fn reverse(&mut self) {
        todo!()
    }

    pub fn to_vec(&self) -> Vec<&T> {
        todo!()
    }
}

impl<T> Default for Stack<T> {
    fn default() -> Self {
        Self::new()
    }
}
''',
   r'''pub struct Stack<T> {
    head: Option<Box<Node<T>>>,
    len: usize,
}

struct Node<T> {
    value: T,
    next: Option<Box<Node<T>>>,
}

impl<T> Stack<T> {
    pub fn new() -> Self {
        Stack { head: None, len: 0 }
    }

    pub fn push(&mut self, value: T) {
        let next = self.head.take();
        self.head = Some(Box::new(Node { value, next }));
        self.len += 1;
    }

    pub fn pop(&mut self) -> Option<T> {
        let node = self.head.take()?;
        self.head = node.next;
        self.len -= 1;
        Some(node.value)
    }

    pub fn peek(&self) -> Option<&T> {
        self.head.as_ref().map(|node| &node.value)
    }

    pub fn len(&self) -> usize {
        self.len
    }

    pub fn is_empty(&self) -> bool {
        self.len == 0
    }

    pub fn reverse(&mut self) {
        let mut reversed = None;
        let mut current = self.head.take();
        while let Some(mut node) = current {
            current = node.next.take();
            node.next = reversed;
            reversed = Some(node);
        }
        self.head = reversed;
    }

    pub fn to_vec(&self) -> Vec<&T> {
        let mut out = Vec::with_capacity(self.len);
        let mut current = &self.head;
        while let Some(node) = current {
            out.push(&node.value);
            current = &node.next;
        }
        out
    }
}

impl<T> Default for Stack<T> {
    fn default() -> Self {
        Self::new()
    }
}
''',
   [("Push, peek and pop", 'let mut s = Stack::new();\nassert!(s.is_empty());\nassert_eq!(s.pop(), None::<i32>);\ns.push(1);\ns.push(2);\ns.push(3);\nassert_eq!(s.len(), 3);\nassert_eq!(s.peek(), Some(&3));\nassert_eq!(s.pop(), Some(3));\nassert_eq!(s.pop(), Some(2));\nassert_eq!(s.len(), 1);\nassert_eq!(s.pop(), Some(1));\nassert_eq!(s.pop(), None);\nassert!(s.is_empty());'),
    ("Top to bottom", 'let mut s = Stack::default();\nfor word in ["a", "b", "c"] {\n    s.push(word.to_string());\n}\nassert_eq!(s.to_vec(), vec!["c", "b", "a"]);\nassert_eq!(s.len(), 3, "to_vec does not remove anything");\nassert_eq!(Stack::<u8>::new().to_vec(), Vec::<&u8>::new());'),
    ("Reverse relinks the nodes", 'let mut s = Stack::new();\nfor n in 1..=5 {\n    s.push(n);\n}\ns.reverse();\nassert_eq!(s.to_vec(), vec![&1, &2, &3, &4, &5]);\nassert_eq!(s.len(), 5);\nassert_eq!(s.pop(), Some(1));\ns.reverse();\nassert_eq!(s.to_vec(), vec![&5, &4, &3, &2]);\nlet mut empty: Stack<i32> = Stack::new();\nempty.reverse();\nassert!(empty.is_empty());'),
    ("Works for values that cannot be cloned", 'struct Token(u32);\nlet mut s = Stack::new();\ns.push(Token(1));\ns.push(Token(2));\ns.reverse();\nassert_eq!(s.pop().map(|t| t.0), Some(1));\nassert_eq!(s.peek().map(|t| t.0), Some(2));'),
    ("Length stays right after mixed use", 'let mut s = Stack::new();\ns.push(1);\ns.push(2);\ns.pop();\ns.push(3);\ns.push(4);\nassert_eq!(s.len(), 3);\nassert_eq!(s.to_vec().len(), 3);\ns.pop();\ns.pop();\ns.pop();\ns.pop();\nassert_eq!(s.len(), 0);')],
   [("            node.next = reversed;\n", "            node.next = None;\n"), ("        self.len -= 1;\n", ""),
    ("        self.head = Some(Box::new(Node { value, next }));\n        self.len += 1;", "        self.head = Some(Box::new(Node { value, next: None }));\n        let _ = next;\n        self.len += 1;"),
    ("        self.head = node.next;\n", "")],
   ["push: take the old head out with self.head.take(), make it the new node's next, and store the new node as head.",
    "pop: self.head.take()? gives the node or returns None; put node.next back as the head and return node.value.",
    "reverse: move nodes one at a time from the old list to a new one: take current's next, point the node at the reversed list, and make it the new front."],
   "A linked list in Rust is the standard lesson in ownership: every node has exactly one owner, so 'moving a pointer' becomes Option::take, which leaves None behind and hands you the Box. That is why reverse needs no unsafe code and no cloning. In real programs Vec and VecDeque are almost always faster, because their items sit next to each other in memory, and a very long list of boxes needs a hand-written Drop to avoid deep recursion. The pattern still matters: trees, graphs with arenas, and parsers all use Option<Box<T>>.",
   eid="A15.2a")

ex("A15.3", "A safe query builder",
   "Database crates such as sqlx and rusqlite take SQL text with placeholders and the values separately, which is what prevents SQL injection. Write the function that builds such a query.\n\n"
   "build_select(table, columns, filters, limit) returns Ok((sql, params)) or Err(message).\n\n"
   "Specification:\n"
   "- SELECT lists the columns joined by \", \", or * when columns is empty, then FROM table.\n"
   "- Each filter (column, value) adds column = ?N, numbered from 1; the first is introduced by WHERE and the rest by AND. The values go into params in the same order and never into the SQL text.\n"
   "- Some(n) for limit adds LIMIT n at the end.\n"
   "- Table and column names cannot be parameters, so they are validated: letters, digits and underscores only, not empty, and not starting with a digit. Otherwise return Err(\"invalid identifier: \\\"...\\\"\") using {:?} formatting of the name.\n\n"
   "Example: build_select(\"staff\", &[\"name\", \"hours\"], &[(\"team\", \"floor\")], Some(5)) returns Ok((\"SELECT name, hours FROM staff WHERE team = ?1 LIMIT 5\", [\"floor\"])).",
   r'''pub fn build_select(
    table: &str,
    columns: &[&str],
    filters: &[(&str, &str)],
    limit: Option<u32>,
) -> Result<(String, Vec<String>), String> {
    todo!()
}
''',
   r'''fn ident(name: &str) -> Result<&str, String> {
    let ok = !name.is_empty()
        && name.chars().all(|c| c.is_ascii_alphanumeric() || c == '_')
        && !name.starts_with(|c: char| c.is_ascii_digit());
    if ok { Ok(name) } else { Err(format!("invalid identifier: {name:?}")) }
}

pub fn build_select(
    table: &str,
    columns: &[&str],
    filters: &[(&str, &str)],
    limit: Option<u32>,
) -> Result<(String, Vec<String>), String> {
    let columns = if columns.is_empty() {
        "*".to_string()
    } else {
        columns.iter().copied().map(ident).collect::<Result<Vec<_>, _>>()?.join(", ")
    };
    let mut sql = format!("SELECT {columns} FROM {}", ident(table)?);
    let mut params = Vec::new();
    for (n, (column, value)) in filters.iter().enumerate() {
        sql += if n == 0 { " WHERE " } else { " AND " };
        sql += &format!("{} = ?{}", ident(column)?, n + 1);
        params.push(value.to_string());
    }
    if let Some(n) = limit {
        sql += &format!(" LIMIT {n}");
    }
    Ok((sql, params))
}
''',
   [("Columns, one filter and a limit", 'let (sql, params) = build_select("staff", &["name", "hours"], &[("team", "floor")], Some(5)).unwrap();\nassert_eq!(sql, "SELECT name, hours FROM staff WHERE team = ?1 LIMIT 5");\nassert_eq!(params, vec!["floor"]);'),
    ("Star, no filters, no limit", 'assert_eq!(build_select("shifts", &[], &[], None), Ok(("SELECT * FROM shifts".to_string(), vec![])));\nassert_eq!(build_select("shifts", &[], &[], Some(1)).unwrap().0, "SELECT * FROM shifts LIMIT 1");'),
    ("Several filters are numbered and joined with AND", 'let (sql, params) = build_select("staff", &["id"], &[("team", "floor"), ("name", "Ada"), ("role", "lead")], None).unwrap();\nassert_eq!(sql, "SELECT id FROM staff WHERE team = ?1 AND name = ?2 AND role = ?3");\nassert_eq!(params, vec!["floor", "Ada", "lead"]);'),
    ("Values never reach the SQL text", "let evil = \"x'; DROP TABLE staff;--\";\nlet (sql, params) = build_select(\"staff\", &[], &[(\"name\", evil)], None).unwrap();\nassert_eq!(sql, \"SELECT * FROM staff WHERE name = ?1\");\nassert_eq!(params, vec![evil]);\nassert!(!sql.contains(\"DROP\"));"),
    ("Identifiers are validated", 'assert_eq!(build_select("staff; DROP TABLE x", &[], &[], None), Err("invalid identifier: \\"staff; DROP TABLE x\\"".to_string()));\nassert!(build_select("staff", &["name", "hours--"], &[], None).is_err());\nassert!(build_select("staff", &[], &[("team = 1 OR 1", "x")], None).is_err());\nassert!(build_select("", &[], &[], None).is_err());\nassert!(build_select("1staff", &[], &[], None).is_err(), "a name cannot start with a digit");\nassert!(build_select("staff_2024", &["first_name"], &[], None).is_ok());')],
   [("ident(table)?", "table"), ('" AND "', '" OR "'), ("n + 1", "n"), ('        && !name.starts_with(|c: char| c.is_ascii_digit());', "        ;"),
    ('"{} = ?{}", ident(column)?, n + 1);\n        params.push(value.to_string());', '"{} = \'{}\'", ident(column)?, value);')],
   ["Write a small helper that checks one identifier and returns Result<&str, String>; use it for the table and every column with the ? operator.",
    "Collect the checked columns with .collect::<Result<Vec<_>, _>>()? and join them; an empty list becomes \"*\".",
    "Loop over filters.iter().enumerate(): push \" WHERE \" for the first and \" AND \" for the others, then column = ?N, and push the value into params."],
   "Placeholders keep data out of the SQL text, so a value like x'; DROP TABLE staff;-- is just a string to compare with. Identifiers cannot be sent as parameters, so they need an allow-list check; that pair of rules is what every query builder (sqlx's QueryBuilder, Diesel, SeaQuery) enforces for you. Collecting an iterator of Results into a Result<Vec<_>, _> stops at the first error, which keeps the validation in one line.",
   eid="A15.3a")

ex("A15.4", "Configuration from the environment",
   "Complete Config::from_env, which turns environment variables (as a map, so it can be tested) into a typed Config, reporting every problem at once.\n\n"
   "Rules, checked in this order:\n"
   "- DATABASE_URL is required; surrounding spaces are trimmed. Missing or blank: \"DATABASE_URL is required\".\n"
   "- PORT (default 8000) must be a whole number from 1 to 65535.\n"
   "- WORKERS (default 2) must be a whole number from 1 to 64.\n"
   "- For both: not a number gives \"PORT must be a whole number, got \\\"http\\\"\" (the value with {:?}); out of range gives \"PORT must be between 1 and 65535, got 70000\".\n"
   "- DEBUG (default false) accepts 1, true, yes, on and 0, false, no, off in any letter case. Anything else: \"DEBUG must be true or false, got \\\"maybe\\\"\".\n"
   "- Other variables are ignored.\n\n"
   "Return Ok(Config) when there are no problems, otherwise Err with all the messages in order.\n\n"
   "Example: DATABASE_URL=postgres://db/app and PORT=9090 give Config { database_url: \"postgres://db/app\", port: 9090, debug: false, workers: 2 }.",
   r'''use std::collections::HashMap;

#[derive(Debug, PartialEq)]
pub struct Config {
    pub database_url: String,
    pub port: u16,
    pub debug: bool,
    pub workers: u8,
}

impl Config {
    pub fn from_env(env: &HashMap<String, String>) -> Result<Config, Vec<String>> {
        todo!()
    }
}
''',
   r'''use std::collections::HashMap;

#[derive(Debug, PartialEq)]
pub struct Config {
    pub database_url: String,
    pub port: u16,
    pub debug: bool,
    pub workers: u8,
}

fn number(env: &HashMap<String, String>, key: &str, default: u32, range: (u32, u32), problems: &mut Vec<String>) -> u32 {
    let Some(raw) = env.get(key) else {
        return default;
    };
    let (low, high) = range;
    match raw.trim().parse::<u32>() {
        Ok(n) if (low..=high).contains(&n) => n,
        Ok(n) => {
            problems.push(format!("{key} must be between {low} and {high}, got {n}"));
            default
        }
        Err(_) => {
            problems.push(format!("{key} must be a whole number, got {raw:?}"));
            default
        }
    }
}

impl Config {
    pub fn from_env(env: &HashMap<String, String>) -> Result<Config, Vec<String>> {
        let mut problems = Vec::new();
        let database_url = env.get("DATABASE_URL").map(|s| s.trim().to_string()).unwrap_or_default();
        if database_url.is_empty() {
            problems.push("DATABASE_URL is required".to_string());
        }
        let port = number(env, "PORT", 8000, (1, 65535), &mut problems);
        let workers = number(env, "WORKERS", 2, (1, 64), &mut problems);
        let debug = match env.get("DEBUG") {
            None => false,
            Some(raw) => match raw.trim().to_lowercase().as_str() {
                "1" | "true" | "yes" | "on" => true,
                "0" | "false" | "no" | "off" => false,
                _ => {
                    problems.push(format!("DEBUG must be true or false, got {raw:?}"));
                    false
                }
            },
        };
        if problems.is_empty() {
            Ok(Config { database_url, port: port as u16, debug, workers: workers as u8 })
        } else {
            Err(problems)
        }
    }
}
''',
   [("Defaults", 'let env = HashMap::from([("DATABASE_URL".to_string(), "postgres://db/app".to_string())]);\nassert_eq!(Config::from_env(&env), Ok(Config { database_url: "postgres://db/app".to_string(), port: 8000, debug: false, workers: 2 }));'),
    ("Values are converted", 'let env: HashMap<String, String> = [("DATABASE_URL", " sqlite://x.db "), ("PORT", "9090"), ("DEBUG", "Yes"), ("WORKERS", "8"), ("HOME", "/root")].iter().map(|(k, v)| (k.to_string(), v.to_string())).collect();\nassert_eq!(Config::from_env(&env), Ok(Config { database_url: "sqlite://x.db".to_string(), port: 9090, debug: true, workers: 8 }));'),
    ("Words for true and false", 'for (word, want) in [("1", true), ("TRUE", true), ("on", true), ("0", false), ("No", false), ("off", false)] {\n    let env = HashMap::from([("DATABASE_URL".to_string(), "x".to_string()), ("DEBUG".to_string(), word.to_string())]);\n    assert_eq!(Config::from_env(&env).unwrap().debug, want, "DEBUG={word}");\n}'),
    ("Every problem is reported at once", 'let env: HashMap<String, String> = [("PORT", "http"), ("DEBUG", "maybe"), ("WORKERS", "0")].iter().map(|(k, v)| (k.to_string(), v.to_string())).collect();\nassert_eq!(Config::from_env(&env), Err(vec![\n    "DATABASE_URL is required".to_string(),\n    "PORT must be a whole number, got \\"http\\"".to_string(),\n    "WORKERS must be between 1 and 64, got 0".to_string(),\n    "DEBUG must be true or false, got \\"maybe\\"".to_string(),\n]));'),
    ("Ranges and blank values", 'let mk = |pairs: &[(&str, &str)]| -> HashMap<String, String> { pairs.iter().map(|(k, v)| (k.to_string(), v.to_string())).collect() };\nassert_eq!(Config::from_env(&mk(&[("DATABASE_URL", "x"), ("PORT", "70000")])), Err(vec!["PORT must be between 1 and 65535, got 70000".to_string()]));\nassert_eq!(Config::from_env(&mk(&[("DATABASE_URL", "   ")])), Err(vec!["DATABASE_URL is required".to_string()]));\nassert_eq!(Config::from_env(&mk(&[("DATABASE_URL", "x"), ("WORKERS", "65")])), Err(vec!["WORKERS must be between 1 and 64, got 65".to_string()]));\nlet top = Config::from_env(&mk(&[("DATABASE_URL", "x"), ("PORT", "65535"), ("WORKERS", "64")])).unwrap();\nassert_eq!((top.port, top.workers), (65535, 64), "the top of each range is allowed");')],
   [("(low..=high).contains(&n)", "(low..high).contains(&n)"), ('.map(|s| s.trim().to_string()).unwrap_or_default();', '.cloned().unwrap_or_default();'),
    ("raw.trim().to_lowercase().as_str()", "raw.trim()"),
    ('            problems.push(format!("{key} must be a whole number, got {raw:?}"));\n            default', '            return default;')],
   ["Keep a Vec<String> of problems and push to it; return Err(problems) only at the end.",
    "PORT and WORKERS follow the same rule: write one helper that takes the key, default and range and pushes a message when the value is wrong.",
    "Lower-case the trimmed DEBUG value and match on the accepted words with | patterns."],
   "Checking every setting at start-up and returning all the problems together means one failed deploy shows the whole list. A typed Config (u16 for the port, bool for debug) keeps string parsing at the edge of the program, and taking a map instead of reading std::env directly makes the function testable. The envy, figment and config crates do this with serde; the rules here are the ones they implement.",
   eid="A15.4a")

ex("A15.6", "An LRU cache",
   "Complete LruCache, the bounded cache behind most in-memory caching: when it is full, the least recently used entry is dropped.\n\n"
   "Specification:\n"
   "- LruCache::new(capacity) panics with a message containing \"capacity\" when capacity is 0.\n"
   "- put(key, value) stores or replaces the value and counts as a use. If the cache then holds more than capacity entries, the least recently used one is removed.\n"
   "- get(&key) returns Some(&value) and counts as a use, or None.\n"
   "- hits and misses count the get calls that found or did not find a value; hit_rate() is hits / (hits + misses), or 0.0 before any lookup.\n"
   "- len() and is_empty() report the number of entries.\n\n"
   "Example: with capacity 2, after put a, put b, get a, put c, the cache holds a and c: b was used least recently.\n\n"
   "A HashMap for the values plus a VecDeque of keys in order of use is enough here; production caches (the lru crate, moka) use a linked list for O(1) updates.",
   r'''use std::collections::{HashMap, VecDeque};
use std::hash::Hash;

pub struct LruCache<K, V> {
    capacity: usize,
    map: HashMap<K, V>,
    order: VecDeque<K>,
    pub hits: u64,
    pub misses: u64,
}

impl<K: Hash + Eq + Clone, V> LruCache<K, V> {
    pub fn new(capacity: usize) -> Self {
        todo!()
    }

    pub fn get(&mut self, key: &K) -> Option<&V> {
        todo!()
    }

    pub fn put(&mut self, key: K, value: V) {
        todo!()
    }

    pub fn len(&self) -> usize {
        self.map.len()
    }

    pub fn is_empty(&self) -> bool {
        self.map.is_empty()
    }

    pub fn hit_rate(&self) -> f64 {
        todo!()
    }
}
''',
   r'''use std::collections::{HashMap, VecDeque};
use std::hash::Hash;

pub struct LruCache<K, V> {
    capacity: usize,
    map: HashMap<K, V>,
    order: VecDeque<K>,
    pub hits: u64,
    pub misses: u64,
}

impl<K: Hash + Eq + Clone, V> LruCache<K, V> {
    pub fn new(capacity: usize) -> Self {
        assert!(capacity > 0, "capacity must be at least 1");
        LruCache { capacity, map: HashMap::new(), order: VecDeque::new(), hits: 0, misses: 0 }
    }

    fn touch(&mut self, key: &K) {
        if let Some(pos) = self.order.iter().position(|k| k == key) {
            self.order.remove(pos);
        }
        self.order.push_back(key.clone());
    }

    pub fn get(&mut self, key: &K) -> Option<&V> {
        if self.map.contains_key(key) {
            self.hits += 1;
            self.touch(key);
        } else {
            self.misses += 1;
        }
        self.map.get(key)
    }

    pub fn put(&mut self, key: K, value: V) {
        self.touch(&key);
        self.map.insert(key, value);
        if self.map.len() > self.capacity
            && let Some(oldest) = self.order.pop_front()
        {
            self.map.remove(&oldest);
        }
    }

    pub fn len(&self) -> usize {
        self.map.len()
    }

    pub fn is_empty(&self) -> bool {
        self.map.is_empty()
    }

    pub fn hit_rate(&self) -> f64 {
        let total = self.hits + self.misses;
        if total == 0 { 0.0 } else { self.hits as f64 / total as f64 }
    }
}
''',
   [("Get and put", 'let mut c = LruCache::new(2);\nassert!(c.is_empty());\nassert_eq!(c.get(&"a"), None);\nc.put("a", 1);\nc.put("b", 2);\nassert_eq!(c.get(&"a"), Some(&1));\nassert_eq!(c.get(&"b"), Some(&2));\nc.put("a", 10);\nassert_eq!(c.get(&"a"), Some(&10), "put replaces the value");\nassert_eq!(c.len(), 2);'),
    ("The least recently used entry is dropped", 'let mut c = LruCache::new(2);\nc.put("a", 1);\nc.put("b", 2);\nc.get(&"a");\nc.put("c", 3);\nassert_eq!(c.get(&"b"), None, "b was used least recently");\nassert_eq!(c.get(&"a"), Some(&1));\nassert_eq!(c.get(&"c"), Some(&3));\nassert_eq!(c.len(), 2);\nc.put("a", 5);\nc.put("d", 4);\nassert_eq!(c.get(&"c"), None, "put also counts as a use, so c is now the oldest");\nassert_eq!(c.get(&"a"), Some(&5));'),
    ("Hits, misses and the hit rate", 'let mut c = LruCache::new(2);\nassert_eq!(c.hit_rate(), 0.0);\nc.put(1, "one");\nc.get(&1);\nc.get(&9);\nc.get(&1);\nc.get(&8);\nassert_eq!((c.hits, c.misses), (2, 2));\nassert_eq!(c.hit_rate(), 0.5);'),
    ("Capacity one", 'let mut c = LruCache::new(1);\nc.put("x".to_string(), 1);\nc.put("y".to_string(), 2);\nassert_eq!(c.len(), 1);\nassert_eq!(c.get(&"x".to_string()), None);\nassert_eq!(c.get(&"y".to_string()), Some(&2));'),
    ("Zero capacity is refused", 'let _ = LruCache::<u8, u8>::new(0);', '#[should_panic(expected = "capacity")]')],
   [("            self.hits += 1;\n            self.touch(key);", "            self.hits += 1;"), ("self.order.pop_front()", "self.order.pop_back()"),
    ("        self.touch(&key);\n        self.map.insert(key, value);", "        if !self.map.contains_key(&key) {\n            self.touch(&key);\n        }\n        self.map.insert(key, value);"),
    ("            self.misses += 1;\n", "")],
   ["Keep the keys in a VecDeque in order of use: on every get that finds the key and every put, remove the key from wherever it is and push it to the back.",
    "After inserting, if the map is over capacity, pop the front key of the deque and remove it from the map.",
    "hit_rate needs a guard for zero lookups; convert the counters with as f64."],
   "An LRU cache bets that what was used recently will be used again, which is true of most web traffic. The map gives O(1) lookups; the deque here makes each use O(n), which is fine for a small cache and is why real implementations pair the map with a doubly linked list. The hit rate is the number to watch in production: a cache that rarely hits adds memory and complexity for nothing.",
   eid="A15.6a")
