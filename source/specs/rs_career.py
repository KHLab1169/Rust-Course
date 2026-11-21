"""Autograded exercises for module A13, Career toolkit: Rust in QA, CI and Python."""
from rspec import ex

# ---------------------------------------------------------------- A13.1 CI
ex("A13.1", "Find the gaps in a CI workflow",
   "Write ci_gaps(workflow) that reviews a GitHub Actions workflow for a Rust project and lists what's missing from the usual quality bar.\n\n"
   "Specification:\n- workflow is the YAML text. Look at the lines that run commands (lines whose trimmed text starts with \"run:\" or \"- run:\"); ignore comments (lines starting with #).\n- Return the missing checks, in this order, as a Vec<&'static str>:\n- \"format\" unless a run line contains cargo fmt and --check\n- \"lint\" unless a run line contains cargo clippy and -D warnings\n- \"test\" unless a run line contains cargo test\n- \"checkout\" unless any line contains actions/checkout\n\n"
   "Examples:\n- a workflow with checkout, cargo fmt --check, cargo clippy -- -D warnings and cargo test returns []\n- one with only checkout and cargo build returns [\"format\", \"lint\", \"test\"]\n\n"
   "Edge cases: cargo clippy without -D warnings still counts as missing \"lint\" (warnings would pass CI); a commented-out step doesn't count.",
   r'''pub fn ci_gaps(workflow: &str) -> Vec<&'static str> {
    todo!()
}
''',
   r'''pub fn ci_gaps(workflow: &str) -> Vec<&'static str> {
    let lines: Vec<&str> = workflow.lines().map(str::trim).filter(|l| !l.starts_with('#')).collect();
    let runs: Vec<&str> = lines.iter().copied().filter(|l| l.starts_with("run:") || l.starts_with("- run:")).collect();
    let has_run = |a: &str, b: &str| runs.iter().any(|l| l.contains(a) && l.contains(b));
    let mut gaps = Vec::new();
    if !has_run("cargo fmt", "--check") {
        gaps.push("format");
    }
    if !has_run("cargo clippy", "-D warnings") {
        gaps.push("lint");
    }
    if !has_run("cargo test", "cargo test") {
        gaps.push("test");
    }
    if !lines.iter().any(|l| l.contains("actions/checkout")) {
        gaps.push("checkout");
    }
    gaps
}
''',
   [("Complete workflow", 'let wf = "name: CI\\non: [push]\\njobs:\\n  test:\\n    runs-on: ubuntu-latest\\n    steps:\\n      - uses: actions/checkout@v4\\n      - run: cargo fmt --check\\n      - run: cargo clippy --all-targets -- -D warnings\\n      - run: cargo test\\n";\nassert_eq!(ci_gaps(wf), Vec::<&str>::new());'),
    ("Only a build", 'let wf = "steps:\\n  - uses: actions/checkout@v4\\n  - run: cargo build\\n";\nassert_eq!(ci_gaps(wf), vec!["format", "lint", "test"]);'),
    ("Clippy that lets warnings pass", 'let wf = "steps:\\n  - uses: actions/checkout@v4\\n  - run: cargo fmt --check\\n  - run: cargo clippy\\n  - run: cargo test\\n";\nassert_eq!(ci_gaps(wf), vec!["lint"]);'),
    ("Comments and multi-step jobs", 'let wf = "steps:\\n  # - uses: actions/checkout@v4\\n  # - run: cargo test\\n  - name: Lint\\n    run: cargo clippy -- -D warnings\\n  - run: cargo fmt --check\\n";\nassert_eq!(ci_gaps(wf), vec!["test", "checkout"]);')],
   [('if !has_run("cargo clippy", "-D warnings") {', 'if !has_run("cargo clippy", "cargo clippy") {'), (".filter(|l| !l.starts_with('#'))", "")],
   ["Trim every line, drop the comments, and keep the run lines in their own Vec.", "A small closure has_run(a, b) checks for a line containing both pieces.", "Push the gaps in the order the specification gives."],
   "This is the bar most Rust teams hold: formatted, clippy-clean with warnings as errors, and tested, on every push. A reviewer bot like this is also a nice small portfolio piece, and it shows you know why each step is there.",
   eid="A13.1a")

# ---------------------------------------------------------------- A13.2 PyO3
ex("A13.2", "The Rust core behind a Python extension",
   "Write the pure-Rust function you will expose to Python with PyO3: an edit distance used to match flaky test names across renames.\n\n"
   "Specification:\n- edit_distance(a: &str, b: &str) -> usize returns the Levenshtein distance: the fewest single-character insertions, deletions or substitutions that turn a into b.\n- Work on characters, not bytes, so accented names count correctly.\n- closest<'a>(name: &str, candidates: &[&'a str]) -> Option<&'a str> returns the candidate with the smallest distance (first on ties), or None for an empty list.\n- Keep this code free of PyO3: the #[pyfunction] wrapper in the next exercise just calls it.\n\n"
   "Examples:\n- edit_distance(\"kitten\", \"sitting\") returns 3\n- closest(\"test_login\", &[\"test_logout\", \"test_login_ok\", \"test_signup\"]) returns Some(\"test_logout\")\n\n"
   "Edge cases: edit_distance(\"\", \"abc\") is 3; edit_distance(\"café\", \"cafe\") is 1.",
   r'''pub fn edit_distance(a: &str, b: &str) -> usize {
    todo!()
}

pub fn closest<'a>(name: &str, candidates: &[&'a str]) -> Option<&'a str> {
    todo!()
}
''',
   r'''pub fn edit_distance(a: &str, b: &str) -> usize {
    let b: Vec<char> = b.chars().collect();
    let mut prev: Vec<usize> = (0..=b.len()).collect();
    for (i, ca) in a.chars().enumerate() {
        let mut row = vec![i + 1];
        for (j, &cb) in b.iter().enumerate() {
            let cost = usize::from(ca != cb);
            row.push((prev[j] + cost).min(prev[j + 1] + 1).min(row[j] + 1));
        }
        prev = row;
    }
    prev[b.len()]
}

pub fn closest<'a>(name: &str, candidates: &[&'a str]) -> Option<&'a str> {
    candidates.iter().copied().min_by_key(|c| edit_distance(name, c))
}
''',
   [("Classic example", 'assert_eq!(edit_distance("kitten", "sitting"), 3);\nassert_eq!(edit_distance("flaw", "lawn"), 2);'),
    ("Empty and equal", 'assert_eq!(edit_distance("", "abc"), 3);\nassert_eq!(edit_distance("abc", ""), 3);\nassert_eq!(edit_distance("same", "same"), 0);'),
    ("Characters, not bytes", 'assert_eq!(edit_distance("café", "cafe"), 1, "é is one character");'),
    ("Closest name", 'assert_eq!(closest("test_login", &["test_logout", "test_login_ok", "test_signup"]), Some("test_logout"));\nassert_eq!(closest("ab", &["ax", "ay"]), Some("ax"), "first on ties");\nassert_eq!(closest("x", &[]), None);')],
   [("let cost = usize::from(ca != cb);", "let cost = 1;"), ("candidates.iter().copied().min_by_key(|c| edit_distance(name, c))", "candidates.iter().copied().max_by_key(|c| edit_distance(name, c))")],
   ["Keep one row of the distance table: row j holds the distance between the first i characters of a and the first j of b.", "Each cell is the minimum of substitute (diagonal + cost), delete (above + 1) and insert (left + 1).", "min_by_key returns the first minimum, which gives the tie rule for free."],
   "Keeping the core in plain Rust means cargo test covers it without Python, and the PyO3 layer stays a thin adapter. Edit distance is a good fit for Rust: it's a tight double loop that Python runs slowly on large test suites.",
   eid="A13.2a")

# ---------------------------------------------------------------- A13.3 mutation
SHIP = r'''/// Shipping cost in cents: 500 up to 1000 g, then 200 per started 500 g above that.
/// Express doubles the price. Orders of 10000 cents or more ship free (but not express).
pub fn shipping_cost(weight_g: u32, express: bool, order_cents: u32) -> u32 {
    let base = if weight_g <= 1000 { 500 } else { 500 + 200 * (weight_g - 1000).div_ceil(500) };
    if express {
        base * 2
    } else if order_cents >= 10000 {
        0
    } else {
        base
    }
}
'''


def mutant(old, new):
    assert old in SHIP
    return SHIP.replace(old, new)


cases = [("Your tests pass on the correct code", "")]
MUTANTS = [
    ("the base price covers up to 1500 g", mutant("weight_g <= 1000", "weight_g <= 1500")),
    ("rounds the extra weight down instead of up", mutant("(weight_g - 1000).div_ceil(500)", "((weight_g - 1000) / 500)")),
    ("express adds 500 instead of doubling", mutant("base * 2", "base + 500")),
    ("free shipping also applies to express", mutant("    if express {\n        base * 2\n    } else if order_cents >= 10000 {\n        0\n    }", "    if order_cents >= 10000 {\n        0\n    } else if express {\n        base * 2\n    }")),
    ("free shipping starts above 10000 instead of at it", mutant("order_cents >= 10000", "order_cents > 10000")),
]
ex("A13.3", "Tests that catch real bugs",
   "Write the tests for shipping_cost. The grader runs them against the correct function and against five versions with a planted bug, like a mutation-testing tool (cargo-mutants) would. Your tests must pass on the correct code and fail on every mutant.\n\n"
   "Specification of shipping_cost(weight_g: u32, express: bool, order_cents: u32) -> u32:\n- 500 cents for parcels up to and including 1000 g.\n- Above that, add 200 for every started 500 g: 1001 g to 1500 g costs 700, 1501 g costs 900.\n- Express doubles the price.\n- Orders of 10000 cents or more ship free, unless they're express.\n\n"
   "What to write:\n- A #[cfg(test)] mod tests block with use super::*; and #[test] functions.\n- Don't write shipping_cost: the grader supplies it.\n\n"
   "Tip: choose values right at each boundary (1000 and 1001 g, 9999 and 10000 cents), and an express price where doubling and adding 500 disagree.",
   r'''#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn light_parcel() {
        assert_eq!(shipping_cost(800, false, 2000), 500);
    }
}
''',
   r'''#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn up_to_1000_g_costs_500() {
        assert_eq!(shipping_cost(1000, false, 0), 500);
    }

    #[test]
    fn each_started_500_g_adds_200() {
        assert_eq!(shipping_cost(1001, false, 0), 700);
        assert_eq!(shipping_cost(1500, false, 0), 700);
        assert_eq!(shipping_cost(1501, false, 0), 900);
    }

    #[test]
    fn express_doubles() {
        assert_eq!(shipping_cost(2000, true, 0), 1800);
    }

    #[test]
    fn free_from_10000_cents() {
        assert_eq!(shipping_cost(800, false, 10000), 0);
        assert_eq!(shipping_cost(800, false, 9999), 500);
    }

    #[test]
    fn express_is_never_free() {
        assert_eq!(shipping_cost(800, true, 20000), 1000);
    }
}
''',
   cases + [("Catches: " + d, "") for d, _ in MUTANTS],
   [r'''#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn some_prices() {
        assert_eq!(shipping_cost(800, false, 0), 500);
        assert_eq!(shipping_cost(800, true, 0), 1000);
        assert_eq!(shipping_cost(3000, false, 0), 1300);
    }
}
''', r'''#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn boundaries_but_no_express() {
        assert_eq!(shipping_cost(1000, false, 0), 500);
        assert_eq!(shipping_cost(1001, false, 0), 700);
        assert_eq!(shipping_cost(800, false, 10000), 0);
        assert_eq!(shipping_cost(800, false, 9999), 500);
    }
}
'''],
   ["Every rule in the specification needs a test whose input sits exactly where the rule changes the answer.", "For 1 kg, doubling 500 and adding 500 both give 1000, so an express test at 1 kg can't tell them apart.", "Test the combination express plus a large order, or the reordering bug survives."],
   "A test suite's strength is measured by the bugs it catches, not by how many tests it has. cargo-mutants automates exactly this on a real crate: it changes your code and reports every mutant your tests didn't notice, which is a strong talking point in a QA interview.",
   eid="A13.3a",
   mutation={"impl": SHIP, "mutants": [{"desc": d, "code": c} for d, c in MUTANTS]})

# ---------------------------------------------------------------- A13.4 flaky
ex("A13.4", "Wait for a condition instead of sleeping",
   "Write wait_until(clock, timeout_ms, poll_ms, condition): the polling helper that replaces fixed sleeps in UI and API tests, with the clock injected so it can be tested instantly.\n\n"
   "Specification:\n- trait Clock { fn now_ms(&self) -> u64; fn sleep_ms(&self, ms: u64); } is given, with FakeClock, which only moves time forward when sleep_ms is called.\n- Check condition() first; if it's true, return Ok(attempts), where attempts is how many times condition was called.\n- Otherwise, if the time since the start plus poll_ms would pass timeout_ms, return Err(Timeout { waited_ms, attempts }); else sleep poll_ms and try again.\n- Never sleep past the timeout.\n\n"
   "Examples:\n- a condition that becomes true on the 3rd call, with poll_ms 100: Ok(3), and the clock moved 200 ms\n- a condition that never becomes true with timeout 1000 and poll 300: Err(Timeout { waited_ms: 900, attempts: 4 })\n\n"
   "Edge cases: a condition that's already true returns Ok(1) without sleeping.",
   r'''use std::cell::Cell;

pub trait Clock {
    fn now_ms(&self) -> u64;
    fn sleep_ms(&self, ms: u64);
}

#[derive(Default)]
pub struct FakeClock {
    pub now: Cell<u64>,
}

impl Clock for FakeClock {
    fn now_ms(&self) -> u64 {
        self.now.get()
    }

    fn sleep_ms(&self, ms: u64) {
        self.now.set(self.now.get() + ms);
    }
}

#[derive(Debug, PartialEq)]
pub struct Timeout {
    pub waited_ms: u64,
    pub attempts: u32,
}

pub fn wait_until(clock: &impl Clock, timeout_ms: u64, poll_ms: u64, mut condition: impl FnMut() -> bool) -> Result<u32, Timeout> {
    todo!()
}
''',
   r'''use std::cell::Cell;

pub trait Clock {
    fn now_ms(&self) -> u64;
    fn sleep_ms(&self, ms: u64);
}

#[derive(Default)]
pub struct FakeClock {
    pub now: Cell<u64>,
}

impl Clock for FakeClock {
    fn now_ms(&self) -> u64 {
        self.now.get()
    }

    fn sleep_ms(&self, ms: u64) {
        self.now.set(self.now.get() + ms);
    }
}

#[derive(Debug, PartialEq)]
pub struct Timeout {
    pub waited_ms: u64,
    pub attempts: u32,
}

pub fn wait_until(clock: &impl Clock, timeout_ms: u64, poll_ms: u64, mut condition: impl FnMut() -> bool) -> Result<u32, Timeout> {
    let start = clock.now_ms();
    let mut attempts = 0;
    loop {
        attempts += 1;
        if condition() {
            return Ok(attempts);
        }
        let waited = clock.now_ms() - start;
        if waited + poll_ms > timeout_ms {
            return Err(Timeout { waited_ms: waited, attempts });
        }
        clock.sleep_ms(poll_ms);
    }
}
''',
   [("Becomes true", 'let clock = FakeClock::default();\nlet mut calls = 0;\nlet r = wait_until(&clock, 1000, 100, || { calls += 1; calls == 3 });\nassert_eq!(r, Ok(3));\nassert_eq!(clock.now_ms(), 200, "two sleeps of 100 ms");'),
    ("Already true", 'let clock = FakeClock::default();\nassert_eq!(wait_until(&clock, 1000, 100, || true), Ok(1));\nassert_eq!(clock.now_ms(), 0, "no sleep when the condition is already true");'),
    ("Times out", 'let clock = FakeClock::default();\nassert_eq!(wait_until(&clock, 1000, 300, || false), Err(Timeout { waited_ms: 900, attempts: 4 }));'),
    ("Never sleeps past the timeout", 'let clock = FakeClock::default();\nclock.now.set(5000);\nlet _ = wait_until(&clock, 250, 100, || false);\nassert!(clock.now_ms() - 5000 <= 250, "slept {} ms with a 250 ms timeout", clock.now_ms() - 5000);\nassert_eq!(clock.now_ms(), 5200);')],
   [("        if waited + poll_ms > timeout_ms {", "        if waited > timeout_ms {"), ("        attempts += 1;\n        if condition() {", "        if condition() {\n            attempts += 1;")],
   ["Record start = clock.now_ms() once, then loop.", "Count an attempt every time you call condition().", "Before sleeping, check whether waited + poll_ms would pass the timeout."],
   "Fixed sleeps make tests both slow and flaky: too short fails on a busy CI machine, too long wastes minutes. Polling with a timeout waits only as long as needed, and injecting the clock makes the helper itself testable in microseconds. Playwright's auto-waiting and expect(...).toBeVisible() work on the same idea.",
   eid="A13.4a")

# ---------------------------------------------------------------- A13.5 interview kata
ex("A13.5", "Interview kata: balanced brackets",
   "A classic live-coding question. Write is_balanced(s) and first_error(s).\n\n"
   "Specification:\n- Brackets are (), [] and {}; all other characters are ignored.\n- is_balanced returns true when every opening bracket is closed by the matching kind, in the right order.\n- first_error returns None for balanced text, otherwise Some(index) of the first problem: the character index of a closing bracket that doesn't match (or has nothing to close), or s.chars().count() if some brackets are left open at the end.\n\n"
   "Examples:\n- is_balanced(\"fn main() { let v = [1, 2]; }\") is true\n- first_error(\"(]\") is Some(1)\n- first_error(\"((\") is Some(2)\n\n"
   "Edge cases: an empty string is balanced; \")(\" fails at index 0.",
   r'''pub fn is_balanced(s: &str) -> bool {
    todo!()
}

pub fn first_error(s: &str) -> Option<usize> {
    todo!()
}
''',
   r'''pub fn first_error(s: &str) -> Option<usize> {
    let mut stack = Vec::new();
    let mut count = 0;
    for (i, c) in s.chars().enumerate() {
        count = i + 1;
        match c {
            '(' | '[' | '{' => stack.push(c),
            ')' | ']' | '}' => {
                let expected = match c {
                    ')' => '(',
                    ']' => '[',
                    _ => '{',
                };
                if stack.pop() != Some(expected) {
                    return Some(i);
                }
            }
            _ => {}
        }
    }
    if stack.is_empty() { None } else { Some(count) }
}

pub fn is_balanced(s: &str) -> bool {
    first_error(s).is_none()
}
''',
   [("Balanced", 'assert!(is_balanced("fn main() { let v = [1, 2]; }"));\nassert!(is_balanced(""));\nassert!(is_balanced("{[()()]}"));'),
    ("Wrong kind", 'assert!(!is_balanced("(]"));\nassert_eq!(first_error("(]"), Some(1));\nassert_eq!(first_error("{[}]"), Some(2));'),
    ("Nothing to close", 'assert_eq!(first_error(")("), Some(0));\nassert_eq!(first_error("ab)"), Some(2));'),
    ("Left open", 'assert_eq!(first_error("(("), Some(2));\nassert_eq!(first_error("é(x"), Some(3), "counts characters, not bytes");\nassert_eq!(first_error("[ok]"), None);')],
   [("                if stack.pop() != Some(expected) {", "                if stack.pop().is_none() {"), ("    if stack.is_empty() { None } else { Some(count) }", "    None")],
   ["A stack of open brackets: push on an opener, pop and compare on a closer.", "stack.pop() != Some(expected) handles both the wrong kind and an empty stack.", "Anything still on the stack at the end is an unclosed bracket."],
   "Interviewers use this to see whether you reach for the right data structure and handle the edge cases (empty input, closing first, leftovers) without prompting. Writing is_balanced on top of first_error avoids duplicating the logic. Say your test cases out loud before coding: it's the QA habit that sets you apart.",
   eid="A13.5a")
