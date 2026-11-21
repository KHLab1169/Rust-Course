"""Practice sets, Track 1 chapters 12 to 16."""
from rspec import ex

# ---------------------------------------------------------------- chapter 12
ex("12.1", "Build a Config from arguments",
   "Write Config::build(args) for a minigrep-style tool.\n\n"
   "Specification:\n- Config has public fields query: String, file_path: String and ignore_case: bool, and derives Debug and PartialEq.\n- args is a slice of Strings in the same shape as std::env::args(): the program name comes first.\n- Return Err(\"not enough arguments\") if the query or the file path is missing.\n- An optional third argument \"-i\" sets ignore_case; any other third argument returns Err(\"unknown option: TEXT\").\n\n"
   "Examples:\n- [\"minigrep\", \"to\", \"poem.txt\"] gives query \"to\", file_path \"poem.txt\", ignore_case false\n- adding \"-i\" sets ignore_case to true\n\n"
   "Edge cases: [\"minigrep\"] and [\"minigrep\", \"to\"] are both errors.",
   r'''#[derive(Debug, PartialEq)]
pub struct Config {
    pub query: String,
    pub file_path: String,
    pub ignore_case: bool,
}

impl Config {
    pub fn build(args: &[String]) -> Result<Config, String> {
        todo!()
    }
}
''',
   r'''#[derive(Debug, PartialEq)]
pub struct Config {
    pub query: String,
    pub file_path: String,
    pub ignore_case: bool,
}

impl Config {
    pub fn build(args: &[String]) -> Result<Config, String> {
        if args.len() < 3 {
            return Err(String::from("not enough arguments"));
        }
        let ignore_case = match args.get(3).map(String::as_str) {
            None => false,
            Some("-i") => true,
            Some(other) => return Err(format!("unknown option: {other}")),
        };
        Ok(Config { query: args[1].clone(), file_path: args[2].clone(), ignore_case })
    }
}
''',
   [("Query and file", 'let args: Vec<String> = ["minigrep", "to", "poem.txt"].map(String::from).to_vec();\nassert_eq!(Config::build(&args), Ok(Config { query: "to".into(), file_path: "poem.txt".into(), ignore_case: false }));'),
    ("Ignore case flag", 'let args: Vec<String> = ["minigrep", "to", "poem.txt", "-i"].map(String::from).to_vec();\nassert!(Config::build(&args).unwrap().ignore_case);'),
    ("Missing arguments", 'for n in 1..3 {\n    let args: Vec<String> = ["minigrep", "to"][..n].iter().map(|s| s.to_string()).collect();\n    assert_eq!(Config::build(&args), Err("not enough arguments".to_string()), "with {n} argument(s)");\n}'),
    ("Unknown option", 'let args: Vec<String> = ["minigrep", "to", "poem.txt", "-x"].map(String::from).to_vec();\nassert_eq!(Config::build(&args), Err("unknown option: -x".to_string()));')],
   [("if args.len() < 3 {", "if args.len() < 2 {"), ("Some(other) => return Err(format!(\"unknown option: {other}\")),", "Some(_) => false,")],
   ["args[0] is the program name, so the query is args[1].", "args.get(3) is None when there is no option.", "match on args.get(3).map(String::as_str) so you can compare with \"-i\"."],
   "Taking a slice instead of calling std::env::args() inside build is what makes it testable. Rejecting unknown options instead of ignoring them saves a user from wondering why -I did nothing.")

ex("12.2", "Run returns errors instead of exiting",
   "Write run(config, read) where read is a function that loads a file, so the logic can be tested without touching the disk.\n\n"
   "Specification:\n- Config has query: String and file_path: String.\n- read: impl Fn(&str) -> Result<String, String> is called with the file path.\n- On success return Ok(lines) with every line that contains the query, as owned Strings.\n- If read fails with message M, return Err(\"could not read FILE: M\").\n\n"
   "Examples:\n- with a reader that returns \"a cat\\na dog\", query \"cat\" gives Ok(vec![\"a cat\"])\n\n"
   "Edge cases: no matching lines is Ok(vec![]), not an error.",
   r'''pub struct Config {
    pub query: String,
    pub file_path: String,
}

pub fn run(config: &Config, read: impl Fn(&str) -> Result<String, String>) -> Result<Vec<String>, String> {
    todo!()
}
''',
   r'''pub struct Config {
    pub query: String,
    pub file_path: String,
}

pub fn run(config: &Config, read: impl Fn(&str) -> Result<String, String>) -> Result<Vec<String>, String> {
    let contents = read(&config.file_path).map_err(|e| format!("could not read {}: {e}", config.file_path))?;
    Ok(contents
        .lines()
        .filter(|line| line.contains(&config.query))
        .map(String::from)
        .collect())
}
''',
   [("Finds lines", 'let c = Config { query: "cat".into(), file_path: "pets.txt".into() };\nlet out = run(&c, |_| Ok("a cat\\na dog\\ncatalogue".to_string()));\nassert_eq!(out, Ok(vec!["a cat".to_string(), "catalogue".to_string()]));'),
    ("Passes the path", 'let c = Config { query: "x".into(), file_path: "notes.txt".into() };\nlet out = run(&c, |p| if p == "notes.txt" { Ok("x".into()) } else { Err(format!("asked for {p}")) });\nassert_eq!(out, Ok(vec!["x".to_string()]));'),
    ("Read error", 'let c = Config { query: "x".into(), file_path: "missing.txt".into() };\nlet out = run(&c, |_| Err("No such file".to_string()));\nassert_eq!(out, Err("could not read missing.txt: No such file".to_string()));'),
    ("No matches", 'let c = Config { query: "zebra".into(), file_path: "f".into() };\nassert_eq!(run(&c, |_| Ok("a\\nb".into())), Ok(vec![]));')],
   [("line.contains(&config.query)", "line.starts_with(&config.query)"), ('format!("could not read {}: {e}", config.file_path)', 'format!("could not read: {e}")')],
   ["Call read(&config.file_path) and turn its error into your message with map_err.", "? returns the error from run.", "lines(), filter and map(String::from) build the result."],
   "Passing the file reader in is dependency injection: the real program passes |p| fs::read_to_string(p).map_err(|e| e.to_string()), and tests pass a closure. Returning errors from run lets main decide how to report them and which exit code to use.")

ex("12.3", "Search with line numbers and whole words",
   "Write search_words(query, contents) that finds lines containing query as a whole word and returns them with their line numbers.\n\n"
   "Specification:\n- Return Vec<(usize, &str)> of (line number from 1, line), borrowing the lines from contents.\n- A whole word means the match is not directly preceded or followed by a letter or digit.\n- Matching is case-sensitive.\n\n"
   "Examples:\n- for \"to be\\nor not to be\\ntoday\", query \"to\" gives [(1, \"to be\"), (2, \"or not to be\")] (not \"today\")\n\n"
   "Edge cases: a word next to punctuation counts (\"(to)\" matches); no matches gives an empty Vec.",
   r'''pub fn search_words<'a>(query: &str, contents: &'a str) -> Vec<(usize, &'a str)> {
    todo!()
}
''',
   r'''fn is_word_char(c: Option<char>) -> bool {
    c.is_some_and(char::is_alphanumeric)
}

fn has_word(line: &str, query: &str) -> bool {
    line.match_indices(query).any(|(i, m)| {
        let before = line[..i].chars().next_back();
        let after = line[i + m.len()..].chars().next();
        !is_word_char(before) && !is_word_char(after)
    })
}

pub fn search_words<'a>(query: &str, contents: &'a str) -> Vec<(usize, &'a str)> {
    contents
        .lines()
        .enumerate()
        .filter(|(_, line)| has_word(line, query))
        .map(|(i, line)| (i + 1, line))
        .collect()
}
''',
   [("Whole words only", 'assert_eq!(search_words("to", "to be\\nor not to be\\ntoday"), vec![(1, "to be"), (2, "or not to be")]);'),
    ("Punctuation", 'assert_eq!(search_words("to", "(to)\\ntoto"), vec![(1, "(to)")]);'),
    ("A later match counts", 'assert_eq!(search_words("cat", "concat cat"), vec![(1, "concat cat")], "The first match is inside a word but the second is whole");'),
    ("Case and no matches", 'assert!(search_words("To", "to be").is_empty());\nassert!(search_words("x", "").is_empty());')],
   [("!is_word_char(before) && !is_word_char(after)", "!is_word_char(before)"), (".map(|(i, line)| (i + 1, line))", ".map(|(i, line)| (i, line))")],
   ["match_indices(query) gives every position where query appears.", "Look at the character just before and just after each match.", "chars().next_back() is the last character of the text before the match."],
   "Checking every match, not just the first, is what handles \"concat cat\". Returning &'a str slices of contents means no line is copied, and the lifetime says the results can't outlive the text.")

ex("12.4", "Settings from flags and environment",
   "Write ignore_case(args, env) that decides case sensitivity from a flag or an environment variable, with the environment passed in so it can be tested.\n\n"
   "Specification:\n- args: &[&str]; env: &HashMap<String, String> standing in for std::env::vars().\n- The flag --ignore-case turns it on and --case-sensitive turns it off; a flag always beats the environment, and the last flag wins.\n- Without a flag, IGNORE_CASE set to anything except \"0\" or \"\" turns it on.\n- Otherwise false.\n\n"
   "Examples:\n- ignore_case(&[\"q\", \"f\"], env with IGNORE_CASE=1) is true\n- ignore_case(&[\"--case-sensitive\"], env with IGNORE_CASE=1) is false\n\n"
   "Edge cases: IGNORE_CASE=0 counts as off.",
   r'''use std::collections::HashMap;

pub fn ignore_case(args: &[&str], env: &HashMap<String, String>) -> bool {
    todo!()
}
''',
   r'''use std::collections::HashMap;

pub fn ignore_case(args: &[&str], env: &HashMap<String, String>) -> bool {
    let from_flag = args.iter().rev().find_map(|a| match *a {
        "--ignore-case" => Some(true),
        "--case-sensitive" => Some(false),
        _ => None,
    });
    from_flag.unwrap_or_else(|| env.get("IGNORE_CASE").is_some_and(|v| v != "0" && !v.is_empty()))
}
''',
   [("Environment only", 'let mut env = HashMap::new();\nassert!(!ignore_case(&["q", "f"], &env), "Nothing set: case-sensitive");\nenv.insert("IGNORE_CASE".to_string(), "1".to_string());\nassert!(ignore_case(&["q", "f"], &env));'),
    ("Flag beats environment", 'let env = HashMap::from([("IGNORE_CASE".to_string(), "1".to_string())]);\nassert!(!ignore_case(&["q", "f", "--case-sensitive"], &env));\nassert!(ignore_case(&["--ignore-case"], &HashMap::new()));'),
    ("Last flag wins", 'assert!(!ignore_case(&["--ignore-case", "--case-sensitive"], &HashMap::new()));\nassert!(ignore_case(&["--case-sensitive", "--ignore-case"], &HashMap::new()));'),
    ("Zero and empty are off", 'for v in ["0", ""] {\n    let env = HashMap::from([("IGNORE_CASE".to_string(), v.to_string())]);\n    assert!(!ignore_case(&["q"], &env), "IGNORE_CASE={v:?} should be off");\n}')],
   [("args.iter().rev().find_map", "args.iter().find_map"), ('v != "0" && !v.is_empty()', '!v.is_empty()')],
   ["Searching the flags from the end (iter().rev()) makes the last one win.", "find_map returns the first Some from the closure.", "unwrap_or_else only looks at the environment when no flag was found."],
   "Passing the environment as a map makes every combination testable without changing the real environment, which would be shared between tests running in parallel. The precedence rule (flag, then environment, then default) is spelled out in one expression.")

# ---------------------------------------------------------------- chapter 13
ex("13.1", "Closures that capture and compose",
   "Write make_adder(n), compose(f, g) and apply_n(f, x, times).\n\n"
   "Specification:\n- make_adder(n: i32) returns a closure that adds n to its argument (impl Fn(i32) -> i32).\n- compose(f, g) returns a closure that computes g(f(x)).\n- apply_n(f, x, times) applies f to x that many times and returns the result.\n\n"
   "Examples:\n- make_adder(5)(10) returns 15\n- compose(make_adder(1), |x| x * 10)(4) returns 50\n- apply_n(|x| x * 2, 1, 10) returns 1024\n\n"
   "Edge cases: apply_n with times = 0 returns x unchanged.",
   r'''pub fn make_adder(n: i32) -> impl Fn(i32) -> i32 {
    move |x| todo!()
}

pub fn compose(f: impl Fn(i32) -> i32, g: impl Fn(i32) -> i32) -> impl Fn(i32) -> i32 {
    move |x| todo!()
}

pub fn apply_n(f: impl Fn(i32) -> i32, x: i32, times: u32) -> i32 {
    todo!()
}
''',
   r'''pub fn make_adder(n: i32) -> impl Fn(i32) -> i32 {
    move |x| x + n
}

pub fn compose(f: impl Fn(i32) -> i32, g: impl Fn(i32) -> i32) -> impl Fn(i32) -> i32 {
    move |x| g(f(x))
}

pub fn apply_n(f: impl Fn(i32) -> i32, x: i32, times: u32) -> i32 {
    (0..times).fold(x, |acc, _| f(acc))
}
''',
   [("Adder", 'let add5 = make_adder(5);\nassert_eq!(add5(10), 15);\nassert_eq!(add5(-5), 0);'),
    ("Compose order", 'let f = compose(make_adder(1), |x| x * 10);\nassert_eq!(f(4), 50, "compose(add 1, times 10)(4) is (4 + 1) * 10");'),
    ("Apply n times", 'assert_eq!(apply_n(|x| x * 2, 1, 10), 1024);\nassert_eq!(apply_n(make_adder(3), 0, 4), 12);\nassert_eq!(apply_n(|x| x * 2, 7, 0), 7);')],
   [("move |x| g(f(x))", "move |x| f(g(x))"), ("(0..times).fold(x, |acc, _| f(acc))", "(1..times).fold(x, |acc, _| f(acc))")],
   ["move makes the closure own n, so it can outlive make_adder.", "impl Fn(i32) -> i32 in the return type hides the closure's real type.", "fold carries a value through a loop: start with x and apply f each time."],
   "Closures capture what they use, and move transfers that into the closure so returning it is safe. Returning impl Fn avoids boxing, and fold expresses \"repeat this n times\" without a mutable variable.")

ex("13.2", "Iterator chains and your own iterator",
   "Write sum_of_odd_squares(values), top_names(scores, min) and an iterator Collatz.\n\n"
   "Specification:\n- sum_of_odd_squares returns the sum of the squares of the odd numbers, using iterator adaptors (no for loop).\n- top_names(scores: &[(&str, u32)], min: u32) returns the names with a score of at least min, highest score first; equal scores keep their original order.\n- Collatz::new(n) is an iterator over the Collatz sequence starting at n and ending with 1 (included). Implement Iterator with type Item = u64.\n\n"
   "Examples:\n- sum_of_odd_squares(&[1, 2, 3]) returns 10\n- Collatz::new(6).collect::<Vec<_>>() is [6, 3, 10, 5, 16, 8, 4, 2, 1]\n\n"
   "Edge cases: Collatz::new(1) gives just [1]; negative odd numbers count as odd.",
   r'''pub fn sum_of_odd_squares(values: &[i64]) -> i64 {
    todo!()
}

pub fn top_names(scores: &[(&str, u32)], min: u32) -> Vec<String> {
    todo!()
}

pub struct Collatz {
    next: Option<u64>,
}

impl Collatz {
    pub fn new(n: u64) -> Self {
        Collatz { next: Some(n) }
    }
}

impl Iterator for Collatz {
    type Item = u64;

    fn next(&mut self) -> Option<u64> {
        todo!()
    }
}
''',
   r'''pub fn sum_of_odd_squares(values: &[i64]) -> i64 {
    values.iter().filter(|&&v| v % 2 != 0).map(|v| v * v).sum()
}

pub fn top_names(scores: &[(&str, u32)], min: u32) -> Vec<String> {
    let mut kept: Vec<&(&str, u32)> = scores.iter().filter(|(_, s)| *s >= min).collect();
    kept.sort_by_key(|(_, s)| std::cmp::Reverse(*s));
    kept.into_iter().map(|(name, _)| name.to_string()).collect()
}

pub struct Collatz {
    next: Option<u64>,
}

impl Collatz {
    pub fn new(n: u64) -> Self {
        Collatz { next: Some(n) }
    }
}

impl Iterator for Collatz {
    type Item = u64;

    fn next(&mut self) -> Option<u64> {
        let current = self.next?;
        self.next = match current {
            1 => None,
            n if n % 2 == 1 => Some(3 * n + 1),
            n => Some(n / 2),
        };
        Some(current)
    }
}
''',
   [("Odd squares", 'assert_eq!(sum_of_odd_squares(&[1, 2, 3]), 10);\nassert_eq!(sum_of_odd_squares(&[-3, 4]), 9, "-3 is odd");\nassert_eq!(sum_of_odd_squares(&[]), 0);'),
    ("Top names", 'let s = [("ada", 90), ("ben", 70), ("cy", 95), ("dee", 90)];\nassert_eq!(top_names(&s, 80), vec!["cy", "ada", "dee"], "Highest first; ada and dee tie and keep their order");'),
    ("Collatz iterator", 'assert_eq!(Collatz::new(6).collect::<Vec<_>>(), vec![6, 3, 10, 5, 16, 8, 4, 2, 1]);\nassert_eq!(Collatz::new(1).collect::<Vec<_>>(), vec![1]);'),
    ("Works with adaptors", 'assert_eq!(Collatz::new(27).count(), 112);\nassert_eq!(Collatz::new(27).max(), Some(9232));')],
   [("v % 2 != 0", "v % 2 == 1"), ("1 => None,", "2 => None,")],
   ["filter then map then sum, with no loop.", "sort_by_key is stable, so equal scores keep their order; std::cmp::Reverse(score) sorts highest first.", "In next, return the current value and work out the following one; after 1 there is nothing more."],
   "In Rust, -3 % 2 is -1, so v % 2 == 1 misses negative odd numbers. Implementing just next gives Collatz every iterator method for free: count, max, take, filter and the rest.")

ex("13.3", "Windows and zips",
   "Write increases(values) and pairwise_diffs(a, b) using iterator adaptors.\n\n"
   "Specification:\n- increases counts how many times a value is larger than the one before it, using windows(2).\n- pairwise_diffs returns, for two slices, the differences b[i] - a[i] for each position, stopping at the shorter one, using zip.\n- Neither function uses indexing like values[i].\n\n"
   "Examples:\n- increases(&[1, 3, 2, 4, 5]) returns 3\n- pairwise_diffs(&[1, 2, 3], &[4, 4]) returns [3, 2]\n\n"
   "Edge cases: increases on 0 or 1 values is 0; equal neighbours don't count.",
   r'''pub fn increases(values: &[i32]) -> usize {
    todo!()
}

pub fn pairwise_diffs(a: &[i32], b: &[i32]) -> Vec<i32> {
    todo!()
}
''',
   r'''pub fn increases(values: &[i32]) -> usize {
    values.windows(2).filter(|w| w[1] > w[0]).count()
}

pub fn pairwise_diffs(a: &[i32], b: &[i32]) -> Vec<i32> {
    a.iter().zip(b).map(|(x, y)| y - x).collect()
}
''',
   [("Increases", 'assert_eq!(increases(&[1, 3, 2, 4, 5]), 3);\nassert_eq!(increases(&[2, 2, 2]), 0, "Equal neighbours don\'t count");'),
    ("Too short", 'assert_eq!(increases(&[]), 0);\nassert_eq!(increases(&[7]), 0);'),
    ("Pairwise differences", 'assert_eq!(pairwise_diffs(&[1, 2, 3], &[4, 4]), vec![3, 2]);\nassert_eq!(pairwise_diffs(&[], &[1]), Vec::<i32>::new());')],
   [("w[1] > w[0]", "w[1] >= w[0]"), ("map(|(x, y)| y - x)", "map(|(x, y)| x - y)")],
   ["windows(2) gives overlapping pairs: [1, 3], [3, 2], ...", "zip stops at the end of the shorter slice.", "count() counts what's left after filter."],
   "windows and zip replace index arithmetic, so there are no off-by-one mistakes and no bounds checks. They compile to the same tight loop you'd write by hand, which is the book's point about zero-cost iterators.")

# ---------------------------------------------------------------- chapter 14
ex("14.1", "Read a release profile",
   "Write release_settings(cargo_toml) that reads the [profile.release] section of a Cargo.toml.\n\n"
   "Specification:\n- Return a HashMap<String, String> of the key = value lines in that section only, with spaces and surrounding double quotes removed from values.\n- The section ends at the next line that starts with [.\n- Ignore blank lines and lines starting with #.\n\n"
   "Examples:\n- for a file with [profile.release] then opt-level = 3 and lto = \"fat\", the map has opt-level \"3\" and lto \"fat\"\n\n"
   "Edge cases: no release section gives an empty map; keys in [profile.dev] are not included.",
   r'''use std::collections::HashMap;

pub fn release_settings(cargo_toml: &str) -> HashMap<String, String> {
    todo!()
}
''',
   r'''use std::collections::HashMap;

pub fn release_settings(cargo_toml: &str) -> HashMap<String, String> {
    let mut settings = HashMap::new();
    let mut in_release = false;
    for line in cargo_toml.lines().map(str::trim) {
        if line.starts_with('[') {
            in_release = line == "[profile.release]";
            continue;
        }
        if !in_release || line.is_empty() || line.starts_with('#') {
            continue;
        }
        if let Some((key, value)) = line.split_once('=') {
            settings.insert(key.trim().to_string(), value.trim().trim_matches('"').to_string());
        }
    }
    settings
}
''',
   [("Release section", 'let toml = "[package]\\nname = \\"app\\"\\n\\n[profile.release]\\nopt-level = 3\\nlto = \\"fat\\"\\n";\nlet s = release_settings(toml);\nassert_eq!(s.get("opt-level").map(String::as_str), Some("3"));\nassert_eq!(s.get("lto").map(String::as_str), Some("fat"));\nassert_eq!(s.len(), 2, "Only the release keys: {s:?}");'),
    ("Stops at the next section", 'let toml = "[profile.release]\\npanic = \\"abort\\"\\n[profile.dev]\\nopt-level = 1\\n";\nlet s = release_settings(toml);\nassert_eq!(s.len(), 1, "got {s:?}");\nassert!(!s.contains_key("opt-level"));'),
    ("Comments and missing section", 'let toml = "[profile.release]\\n# fast builds\\n\\ndebug = true\\n";\nassert_eq!(release_settings(toml).len(), 1);\nassert!(release_settings("[package]\\nname = \\"x\\"").is_empty());')],
   [("in_release = line == \"[profile.release]\";", "in_release = in_release || line == \"[profile.release]\";"), (".trim_matches('\"')", "")],
   ["Remember which section you're in with a bool that changes at every [header] line.", "split_once('=') splits a line into key and value.", "trim() then trim_matches('\"') cleans up the value."],
   "Release profiles are how you trade compile time for speed (opt-level, lto, codegen-units). Reading the section with a small state flag is a pattern that works for any INI-style file; for real TOML, the toml crate does it properly.")

ex("14.2", "Bump a version number",
   "Write bump(version, part) that increases a semantic version number before you publish a crate.\n\n"
   "Specification:\n- version is \"MAJOR.MINOR.PATCH\" with three whole numbers.\n- part is \"major\", \"minor\" or \"patch\".\n- A major bump resets minor and patch to 0; a minor bump resets patch to 0.\n- Return Err(\"invalid version: TEXT\") for a badly formed version and Err(\"unknown part: TEXT\") for any other part.\n\n"
   "Examples:\n- bump(\"1.4.2\", \"minor\") returns Ok(\"1.5.0\")\n- bump(\"1.4.2\", \"major\") returns Ok(\"2.0.0\")\n\n"
   "Edge cases: \"1.4\", \"1.4.2.0\" and \"1.x.2\" are invalid; \"0.9.9\" with \"patch\" gives \"0.9.10\".",
   r'''pub fn bump(version: &str, part: &str) -> Result<String, String> {
    todo!()
}
''',
   r'''pub fn bump(version: &str, part: &str) -> Result<String, String> {
    let invalid = || format!("invalid version: {version}");
    let nums: Vec<u64> = version
        .split('.')
        .map(|p| p.parse::<u64>().map_err(|_| invalid()))
        .collect::<Result<_, _>>()?;
    let [major, minor, patch] = nums[..] else {
        return Err(invalid());
    };
    let (major, minor, patch) = match part {
        "major" => (major + 1, 0, 0),
        "minor" => (major, minor + 1, 0),
        "patch" => (major, minor, patch + 1),
        other => return Err(format!("unknown part: {other}")),
    };
    Ok(format!("{major}.{minor}.{patch}"))
}
''',
   [("Each part", 'assert_eq!(bump("1.4.2", "patch"), Ok("1.4.3".into()));\nassert_eq!(bump("1.4.2", "minor"), Ok("1.5.0".into()));\nassert_eq!(bump("1.4.2", "major"), Ok("2.0.0".into()));'),
    ("Numbers, not digits", 'assert_eq!(bump("0.9.9", "patch"), Ok("0.9.10".into()));'),
    ("Invalid versions", 'for v in ["1.4", "1.4.2.0", "1.x.2", ""] {\n    assert_eq!(bump(v, "patch"), Err(format!("invalid version: {v}")), "bump({v:?})");\n}'),
    ("Unknown part", 'assert_eq!(bump("1.0.0", "huge"), Err("unknown part: huge".into()));')],
   [('"minor" => (major, minor + 1, 0),', '"minor" => (major, minor + 1, patch),'), ('"major" => (major + 1, 0, 0),', '"major" => (major + 1, minor, patch),')],
   ["Split on '.', parse each part, and collect into Result<Vec<u64>, _> to stop at the first bad part.", "A slice pattern let [major, minor, patch] = nums[..] else { ... } checks there are exactly three.", "match on part returns the new triple."],
   "Collecting into a Result and the slice pattern together reject every malformed version with very little code. Under semver, a minor bump promises compatibility, which is why patch resets to 0; cargo publish refuses a version that's already on crates.io.")

ex("14.3", "Workspace members",
   "Write workspace_members(cargo_toml) that lists the members of a Cargo workspace.\n\n"
   "Specification:\n- Find the members = [...] entry in the [workspace] section; the list may span several lines.\n- Return the member paths without quotes, in order, as Vec<String>.\n- Return an empty Vec if there is no [workspace] section or no members entry.\n\n"
   "Examples:\n- \"[workspace]\\nmembers = [\\\"adder\\\", \\\"add_one\\\"]\" gives [\"adder\", \"add_one\"]\n\n"
   "Edge cases: a list split over lines with a trailing comma works; members in a [package] section don't count.",
   r'''pub fn workspace_members(cargo_toml: &str) -> Vec<String> {
    todo!()
}
''',
   r'''pub fn workspace_members(cargo_toml: &str) -> Vec<String> {
    let Some(start) = cargo_toml.find("[workspace]") else {
        return Vec::new();
    };
    let section = &cargo_toml[start + "[workspace]".len()..];
    let section = section.split("\n[").next().unwrap_or("");
    let Some(m) = section.find("members") else {
        return Vec::new();
    };
    let after = &section[m..];
    let (Some(open), Some(close)) = (after.find('['), after.find(']')) else {
        return Vec::new();
    };
    after[open + 1..close]
        .split(',')
        .map(|s| s.trim().trim_matches('"'))
        .filter(|s| !s.is_empty())
        .map(String::from)
        .collect()
}
''',
   [("One line", 'assert_eq!(workspace_members("[workspace]\\nmembers = [\\"adder\\", \\"add_one\\"]\\n"), vec!["adder", "add_one"]);'),
    ("Several lines", 'let toml = "[workspace]\\nresolver = \\"3\\"\\nmembers = [\\n    \\"core\\",\\n    \\"cli\\",\\n]\\n\\n[workspace.dependencies]\\nserde = \\"1\\"\\n";\nassert_eq!(workspace_members(toml), vec!["core", "cli"]);'),
    ("No workspace", 'assert!(workspace_members("[package]\\nname = \\"x\\"\\n").is_empty());\nassert!(workspace_members("[package]\\nmembers = [\\"a\\"]\\n[workspace]\\n").is_empty(), "members outside [workspace] don\'t count");\nassert!(workspace_members("[workspace]\\nresolver = \\"2\\"\\n\\n[package.metadata]\\nmembers = [\\"x\\"]\\n").is_empty(), "members in a later section don\'t count");')],
   [('.filter(|s| !s.is_empty())', '.filter(|s| !s.contains(\' \'))'), ('let section = section.split("\\n[").next().unwrap_or("");\n', '')],
   ["Find \"[workspace]\" and cut the text there; the section ends at the next line starting with [.", "Find the [ and ] after members, and split what's between on commas.", "A trailing comma gives an empty last piece: filter it out."],
   "A workspace shares one Cargo.lock and target folder between crates, so they build once and agree on dependency versions. This exercise is string slicing with find and ranges; for real tools, cargo metadata gives the same information as JSON.")

# ---------------------------------------------------------------- chapter 15
ex("15.1", "An expression tree with Box",
   "Write eval for a small expression language built from a recursive enum (an exercise from Google's Comprehensive Rust).\n\n"
   "Specification:\n- enum Expr { Num(f64), Neg(Box<Expr>), Add(Box<Expr>, Box<Expr>), Mul(Box<Expr>, Box<Expr>), Div(Box<Expr>, Box<Expr>) } is given.\n- eval(&Expr) -> Result<f64, String> computes the value.\n- Dividing by zero returns Err(\"division by zero\"); an error anywhere inside makes the whole result an error.\n\n"
   "Examples:\n- Add(Num(2), Mul(Num(3), Num(4))) evaluates to 14\n\n"
   "Edge cases: Neg(Div(Num(1), Num(0))) is Err(\"division by zero\").",
   r'''pub enum Expr {
    Num(f64),
    Neg(Box<Expr>),
    Add(Box<Expr>, Box<Expr>),
    Mul(Box<Expr>, Box<Expr>),
    Div(Box<Expr>, Box<Expr>),
}

pub fn eval(e: &Expr) -> Result<f64, String> {
    todo!()
}
''',
   r'''pub enum Expr {
    Num(f64),
    Neg(Box<Expr>),
    Add(Box<Expr>, Box<Expr>),
    Mul(Box<Expr>, Box<Expr>),
    Div(Box<Expr>, Box<Expr>),
}

pub fn eval(e: &Expr) -> Result<f64, String> {
    Ok(match e {
        Expr::Num(n) => *n,
        Expr::Neg(a) => -eval(a)?,
        Expr::Add(a, b) => eval(a)? + eval(b)?,
        Expr::Mul(a, b) => eval(a)? * eval(b)?,
        Expr::Div(a, b) => {
            let d = eval(b)?;
            if d == 0.0 {
                return Err(String::from("division by zero"));
            }
            eval(a)? / d
        }
    })
}
''',
   [("Numbers and sums", 'use Expr::*;\nlet e = Add(Box::new(Num(2.0)), Box::new(Mul(Box::new(Num(3.0)), Box::new(Num(4.0)))));\nassert_eq!(eval(&e), Ok(14.0));'),
    ("Negation and division", 'use Expr::*;\nlet e = Neg(Box::new(Div(Box::new(Num(9.0)), Box::new(Num(3.0)))));\nassert_eq!(eval(&e), Ok(-3.0));'),
    ("Division by zero", 'use Expr::*;\nlet e = Neg(Box::new(Div(Box::new(Num(1.0)), Box::new(Add(Box::new(Num(2.0)), Box::new(Num(-2.0)))))));\nassert_eq!(eval(&e), Err("division by zero".to_string()));')],
   [("Expr::Neg(a) => -eval(a)?,", "Expr::Neg(a) => eval(a)?,"), ("            if d == 0.0 {\n                return Err(String::from(\"division by zero\"));\n            }\n", "")],
   ["Recursive types need Box: without it, Expr would have to contain itself and have infinite size.", "eval calls itself on the boxed sub-expressions; a &Box<Expr> works where &Expr is expected.", "? passes an error from any sub-expression straight up."],
   "Box gives the recursive enum a known size (a pointer) while the data lives on the heap. Recursion plus ? makes eval mirror the tree exactly: each variant is one line, and errors bubble up from any depth.")

ex("15.2", "Drop guards and Deref",
   "Write a guard that records when it's dropped, and a wrapper that derefs to str.\n\n"
   "Specification:\n- Guard::new(name, log) takes a name and an Rc<RefCell<Vec<String>>>, pushes \"start NAME\" into the log, and returns the guard.\n- When a Guard is dropped, it pushes \"end NAME\".\n- Name(String) implements Deref with Target = str, so every str method works on a Name.\n\n"
   "Examples:\n- creating guards a then b inside one block gives the log start a, start b, end b, end a\n- Name(\"Ferris\".into()).len() is 6\n\n"
   "Edge cases: drop(guard) ends it early.",
   r'''use std::cell::RefCell;
use std::ops::Deref;
use std::rc::Rc;

pub struct Guard {
    name: String,
    log: Rc<RefCell<Vec<String>>>,
}

impl Guard {
    pub fn new(name: &str, log: Rc<RefCell<Vec<String>>>) -> Guard {
        todo!()
    }
}

impl Drop for Guard {
    fn drop(&mut self) {
        todo!()
    }
}

pub struct Name(pub String);

impl Deref for Name {
    type Target = str;

    fn deref(&self) -> &str {
        todo!()
    }
}
''',
   r'''use std::cell::RefCell;
use std::ops::Deref;
use std::rc::Rc;

pub struct Guard {
    name: String,
    log: Rc<RefCell<Vec<String>>>,
}

impl Guard {
    pub fn new(name: &str, log: Rc<RefCell<Vec<String>>>) -> Guard {
        log.borrow_mut().push(format!("start {name}"));
        Guard { name: name.to_string(), log }
    }
}

impl Drop for Guard {
    fn drop(&mut self) {
        self.log.borrow_mut().push(format!("end {}", self.name));
    }
}

pub struct Name(pub String);

impl Deref for Name {
    type Target = str;

    fn deref(&self) -> &str {
        &self.0
    }
}
''',
   [("Reverse drop order", 'let log = Rc::new(RefCell::new(Vec::new()));\n{\n    let _a = Guard::new("a", Rc::clone(&log));\n    let _b = Guard::new("b", Rc::clone(&log));\n}\nassert_eq!(*log.borrow(), vec!["start a", "start b", "end b", "end a"]);'),
    ("Early drop", 'let log = Rc::new(RefCell::new(Vec::new()));\nlet g = Guard::new("x", Rc::clone(&log));\ndrop(g);\nlog.borrow_mut().push("after".to_string());\nassert_eq!(*log.borrow(), vec!["start x", "end x", "after"]);'),
    ("Deref to str", 'let n = Name("Ferris".to_string());\nassert_eq!(n.len(), 6);\nassert!(n.starts_with("Fer"));\nassert_eq!(n.to_uppercase(), "FERRIS");')],
   [('self.log.borrow_mut().push(format!("end {}", self.name));', 'self.log.borrow_mut().push(format!("start {}", self.name));'), ('log.borrow_mut().push(format!("start {name}"));\n', '')],
   ["Push \"start\" in new, before building the Guard.", "Drop::drop runs automatically when the value goes out of scope; values drop in reverse order of creation.", "deref returns &self.0, which turns &String into &str."],
   "Drop guards are how Rust does cleanup (unlocking a Mutex, closing a file, finishing a timer) without any code at the call site. Deref makes a wrapper feel like what it wraps, so a Name can be used wherever a &str is expected.")

ex("15.3", "Shared lists with Rc",
   "Write functions for the book's shared-tail list, using Rc so two lists can share the same tail.\n\n"
   "Specification:\n- enum List { Cons(i32, Rc<List>), Nil } is given.\n- prepend(value, tail: &Rc<List>) returns a new Rc<List> with value in front of tail, sharing tail (no deep copy).\n- sum(list: &List) returns the sum of all values.\n- to_vec(list: &List) returns the values in order.\n\n"
   "Examples:\n- a = 5 -> 10 -> Nil; b = prepend(3, &a); c = prepend(4, &a): sum(&b) is 18 and sum(&c) is 19\n\n"
   "Edge cases: after making b and c, Rc::strong_count(&a) is 3.",
   r'''use std::rc::Rc;

pub enum List {
    Cons(i32, Rc<List>),
    Nil,
}

pub fn prepend(value: i32, tail: &Rc<List>) -> Rc<List> {
    todo!()
}

pub fn sum(list: &List) -> i32 {
    todo!()
}

pub fn to_vec(list: &List) -> Vec<i32> {
    todo!()
}
''',
   r'''use std::rc::Rc;

pub enum List {
    Cons(i32, Rc<List>),
    Nil,
}

pub fn prepend(value: i32, tail: &Rc<List>) -> Rc<List> {
    Rc::new(List::Cons(value, Rc::clone(tail)))
}

pub fn sum(list: &List) -> i32 {
    match list {
        List::Cons(v, rest) => v + sum(rest),
        List::Nil => 0,
    }
}

pub fn to_vec(list: &List) -> Vec<i32> {
    let mut out = Vec::new();
    let mut node = list;
    while let List::Cons(v, rest) = node {
        out.push(*v);
        node = rest;
    }
    out
}
''',
   [("Shared tail", 'let a = Rc::new(List::Cons(5, Rc::new(List::Cons(10, Rc::new(List::Nil)))));\nlet b = prepend(3, &a);\nlet c = prepend(4, &a);\nassert_eq!((sum(&b), sum(&c)), (18, 19));\nassert_eq!(Rc::strong_count(&a), 3, "a is owned by a, b and c");'),
    ("To a vector", 'let a = prepend(1, &prepend(2, &Rc::new(List::Nil)));\nassert_eq!(to_vec(&a), vec![1, 2]);\nassert!(to_vec(&List::Nil).is_empty());'),
    ("Counts drop again", 'let a = Rc::new(List::Nil);\n{\n    let _b = prepend(1, &a);\n    assert_eq!(Rc::strong_count(&a), 2);\n}\nassert_eq!(Rc::strong_count(&a), 1);')],
   [("List::Cons(v, rest) => v + sum(rest),", "List::Cons(v, _) => *v,"), ("        out.push(*v);\n        node = rest;\n", "        out.insert(0, *v);\n        node = rest;\n")],
   ["Rc::clone(tail) adds an owner without copying the list.", "sum is naturally recursive: the value plus the sum of the rest.", "while let List::Cons(v, rest) = node walks the list without recursion."],
   "Rc counts owners and frees the list when the last one goes, which strong_count lets you watch. Rc::clone is cheap (a counter increment), and writing Rc::clone instead of tail.clone() makes that obvious to readers.")

ex("15.4", "A mock with RefCell",
   "Write a test double that records messages, for the book's LimitTracker example.\n\n"
   "Specification:\n- The trait Messenger { fn send(&self, msg: &str); } and LimitTracker are given; note send takes &self, not &mut self.\n- Write MockMessenger with a field sent: RefCell<Vec<String>>, a new() constructor, and impl Messenger that records each message.\n- Also add sent_messages(&self) -> Vec<String> that returns a copy of what was sent.\n\n"
   "Examples:\n- a tracker with max 100: set_value(80) sends one warning that contains \"75%\"\n\n"
   "Edge cases: set_value(50) sends nothing; set_value(100) sends an \"Error\" message.",
   r'''use std::cell::RefCell;

pub trait Messenger {
    fn send(&self, msg: &str);
}

pub struct LimitTracker<'a, T: Messenger> {
    messenger: &'a T,
    max: usize,
}

impl<'a, T: Messenger> LimitTracker<'a, T> {
    pub fn new(messenger: &'a T, max: usize) -> LimitTracker<'a, T> {
        LimitTracker { messenger, max }
    }

    pub fn set_value(&mut self, value: usize) {
        let percent = value as f64 / self.max as f64;
        if percent >= 1.0 {
            self.messenger.send("Error: You are over your quota!");
        } else if percent >= 0.9 {
            self.messenger.send("Urgent warning: You've used up over 90% of your quota!");
        } else if percent >= 0.75 {
            self.messenger.send("Warning: You've used up over 75% of your quota!");
        }
    }
}

#[derive(Default)]
pub struct MockMessenger {
    sent: RefCell<Vec<String>>,
}

impl MockMessenger {
    pub fn new() -> MockMessenger {
        todo!()
    }

    pub fn sent_messages(&self) -> Vec<String> {
        todo!()
    }
}

impl Messenger for MockMessenger {
    fn send(&self, msg: &str) {
        todo!()
    }
}
''',
   r'''use std::cell::RefCell;

pub trait Messenger {
    fn send(&self, msg: &str);
}

pub struct LimitTracker<'a, T: Messenger> {
    messenger: &'a T,
    max: usize,
}

impl<'a, T: Messenger> LimitTracker<'a, T> {
    pub fn new(messenger: &'a T, max: usize) -> LimitTracker<'a, T> {
        LimitTracker { messenger, max }
    }

    pub fn set_value(&mut self, value: usize) {
        let percent = value as f64 / self.max as f64;
        if percent >= 1.0 {
            self.messenger.send("Error: You are over your quota!");
        } else if percent >= 0.9 {
            self.messenger.send("Urgent warning: You've used up over 90% of your quota!");
        } else if percent >= 0.75 {
            self.messenger.send("Warning: You've used up over 75% of your quota!");
        }
    }
}

#[derive(Default)]
pub struct MockMessenger {
    sent: RefCell<Vec<String>>,
}

impl MockMessenger {
    pub fn new() -> MockMessenger {
        MockMessenger { sent: RefCell::new(Vec::new()) }
    }

    pub fn sent_messages(&self) -> Vec<String> {
        self.sent.borrow().clone()
    }
}

impl Messenger for MockMessenger {
    fn send(&self, msg: &str) {
        self.sent.borrow_mut().push(String::from(msg));
    }
}
''',
   [("Records a warning", 'let mock = MockMessenger::new();\nlet mut t = LimitTracker::new(&mock, 100);\nt.set_value(80);\nlet sent = mock.sent_messages();\nassert_eq!(sent.len(), 1, "one message expected, got {sent:?}");\nassert!(sent[0].contains("75%"));'),
    ("Several messages", 'let mock = MockMessenger::new();\nlet mut t = LimitTracker::new(&mock, 100);\nt.set_value(50);\nt.set_value(95);\nt.set_value(100);\nlet sent = mock.sent_messages();\nassert_eq!(sent.len(), 2, "50 sends nothing; got {sent:?}");\nassert!(sent[0].contains("90%") && sent[1].starts_with("Error"));')],
   [("        self.sent.borrow_mut().push(String::from(msg));\n", "        let _ = msg;\n"), ("self.sent.borrow().clone()", "self.sent.borrow().iter().take(1).cloned().collect()")],
   ["send takes &self, so you can't push to a plain Vec field; RefCell allows changing it through a shared reference.", "borrow_mut() gives a mutable borrow checked at run time.", "sent_messages can return self.sent.borrow().clone()."],
   "RefCell moves the borrow rules from compile time to run time, which is exactly what test doubles need when an interface only offers &self. Breaking the rules (two borrow_mut at once) panics instead of failing to compile, so keep each borrow short.")

ex("15.5", "Parents with Weak",
   "Write a tree where children know their parent through a Weak reference, so there is no reference cycle.\n\n"
   "Specification:\n- Node { value: i32, parent: RefCell<Weak<Node>>, children: RefCell<Vec<Rc<Node>>> } is given, with Node::new(value).\n- add_child(parent: &Rc<Node>, value: i32) -> Rc<Node> creates the child, sets its parent and adds it to the parent's children.\n- path_to_root(node: &Rc<Node>) -> Vec<i32> returns the values from node up to the root.\n\n"
   "Examples:\n- root 1 with child 2 with child 3: path_to_root(&three) is [3, 2, 1]\n\n"
   "Edge cases: once the root is dropped, a child's parent upgrade gives None; the root's strong count is 1 (children hold only weak references).",
   r'''use std::cell::RefCell;
use std::rc::{Rc, Weak};

pub struct Node {
    pub value: i32,
    pub parent: RefCell<Weak<Node>>,
    pub children: RefCell<Vec<Rc<Node>>>,
}

impl Node {
    pub fn new(value: i32) -> Rc<Node> {
        Rc::new(Node { value, parent: RefCell::new(Weak::new()), children: RefCell::new(Vec::new()) })
    }
}

pub fn add_child(parent: &Rc<Node>, value: i32) -> Rc<Node> {
    todo!()
}

pub fn path_to_root(node: &Rc<Node>) -> Vec<i32> {
    todo!()
}
''',
   r'''use std::cell::RefCell;
use std::rc::{Rc, Weak};

pub struct Node {
    pub value: i32,
    pub parent: RefCell<Weak<Node>>,
    pub children: RefCell<Vec<Rc<Node>>>,
}

impl Node {
    pub fn new(value: i32) -> Rc<Node> {
        Rc::new(Node { value, parent: RefCell::new(Weak::new()), children: RefCell::new(Vec::new()) })
    }
}

pub fn add_child(parent: &Rc<Node>, value: i32) -> Rc<Node> {
    let child = Node::new(value);
    *child.parent.borrow_mut() = Rc::downgrade(parent);
    parent.children.borrow_mut().push(Rc::clone(&child));
    child
}

pub fn path_to_root(node: &Rc<Node>) -> Vec<i32> {
    let mut path = vec![node.value];
    let mut current = node.parent.borrow().upgrade();
    while let Some(n) = current {
        path.push(n.value);
        current = n.parent.borrow().upgrade();
    }
    path
}
''',
   [("Path to the root", 'let root = Node::new(1);\nlet two = add_child(&root, 2);\nlet three = add_child(&two, 3);\nassert_eq!(path_to_root(&three), vec![3, 2, 1]);\nassert_eq!(path_to_root(&root), vec![1]);'),
    ("Children are recorded", 'let root = Node::new(1);\nadd_child(&root, 2);\nadd_child(&root, 3);\nlet values: Vec<i32> = root.children.borrow().iter().map(|c| c.value).collect();\nassert_eq!(values, vec![2, 3]);'),
    ("No cycle", 'let root = Node::new(1);\nlet child = add_child(&root, 2);\nassert_eq!(Rc::strong_count(&root), 1, "children must hold a Weak to the parent, not an Rc");\nassert_eq!(Rc::weak_count(&root), 1);\ndrop(root);\nassert!(child.parent.borrow().upgrade().is_none(), "after the root is dropped its child has no parent");')],
   [("    parent.children.borrow_mut().push(Rc::clone(&child));\n", ""), ("        current = n.parent.borrow().upgrade();\n", "        current = None;\n")],
   ["Rc::downgrade(parent) makes a Weak pointer that doesn't keep the parent alive.", "Set it with *child.parent.borrow_mut() = ...", "upgrade() turns a Weak into Option<Rc>: None once the parent is gone."],
   "Strong references point down the tree and weak ones point up, so dropping the root frees everything. If children held an Rc to their parent, parent and child would keep each other alive forever: a memory leak that Rust's safety rules don't prevent.")

# ---------------------------------------------------------------- chapter 16
ex("16.1", "A parallel sum with scoped threads",
   "Write parallel_sum(values, parts) that splits the work across threads with std::thread::scope.\n\n"
   "Specification:\n- Split values into parts chunks of roughly equal size (use chunks with a size rounded up), sum each chunk on its own thread, and add the results.\n- parts is at least 1; if it's larger than the number of values, that's fine.\n- Use thread::scope so the threads can borrow values without Arc.\n\n"
   "Examples:\n- parallel_sum(&(1..=100).collect::<Vec<i64>>(), 4) returns 5050\n\n"
   "Edge cases: an empty slice returns 0; parts = 1 still works.",
   r'''use std::thread;

pub fn parallel_sum(values: &[i64], parts: usize) -> i64 {
    todo!()
}
''',
   r'''use std::thread;

pub fn parallel_sum(values: &[i64], parts: usize) -> i64 {
    if values.is_empty() {
        return 0;
    }
    let size = values.len().div_ceil(parts.max(1));
    thread::scope(|s| {
        let handles: Vec<_> = values.chunks(size).map(|chunk| s.spawn(move || chunk.iter().sum::<i64>())).collect();
        handles.into_iter().map(|h| h.join().unwrap()).sum()
    })
}
''',
   [("Sum of 1 to 100", 'let v: Vec<i64> = (1..=100).collect();\nassert_eq!(parallel_sum(&v, 4), 5050);\nassert_eq!(parallel_sum(&v, 1), 5050);\nassert_eq!(parallel_sum(&v, 7), 5050, "100 values in 7 parts");'),
    ("More parts than values", 'assert_eq!(parallel_sum(&[1, 2, 3], 10), 6);'),
    ("Empty", 'assert_eq!(parallel_sum(&[], 3), 0);')],
   [("values.chunks(size)", "values[1..].chunks(size)"), ("handles.into_iter().map(|h| h.join().unwrap()).sum()", "handles.into_iter().take(1).map(|h| h.join().unwrap()).sum()")],
   ["div_ceil rounds the chunk size up, so there are never more than parts chunks.", "Inside thread::scope(|s| ...), s.spawn can borrow from values.", "Collect the handles first, then join them all; joining inside the same map would run the threads one by one."],
   "Scoped threads are guaranteed to finish before scope returns, which is why they may borrow local data. Collecting the handles before joining matters: a lazy map that spawns and joins in one step runs everything sequentially.")

ex("16.2", "A channel pipeline",
   "Write count_words_parallel(lines, workers) that sends work to several threads over a channel and collects the counts.\n\n"
   "Specification:\n- lines: Vec<String>, workers: usize (at least 1).\n- Give each worker every workers-th line (worker i gets lines i, i + workers, ...).\n- Each worker sends one (worker_id, word_count) message on an mpsc channel.\n- Return the total word count. Make sure the receiving loop ends: drop the original sender.\n\n"
   "Examples:\n- 3 lines with 2, 3 and 1 words and 2 workers give 6\n\n"
   "Edge cases: more workers than lines works (some send 0); no lines returns 0.",
   r'''use std::sync::mpsc;
use std::thread;

pub fn count_words_parallel(lines: Vec<String>, workers: usize) -> usize {
    todo!()
}
''',
   r'''use std::sync::mpsc;
use std::thread;

pub fn count_words_parallel(lines: Vec<String>, workers: usize) -> usize {
    let workers = workers.max(1);
    let (tx, rx) = mpsc::channel();
    for id in 0..workers {
        let tx = tx.clone();
        let mine: Vec<String> = lines.iter().skip(id).step_by(workers).cloned().collect();
        thread::spawn(move || {
            let count = mine.iter().map(|l| l.split_whitespace().count()).sum::<usize>();
            tx.send((id, count)).unwrap();
        });
    }
    drop(tx);
    rx.iter().map(|(_, count)| count).sum()
}
''',
   [("Counts all words", 'let lines = vec!["a b".to_string(), "c d e".to_string(), "f".to_string()];\nassert_eq!(count_words_parallel(lines, 2), 6);'),
    ("More workers than lines", 'let lines = vec!["one two".to_string()];\nassert_eq!(count_words_parallel(lines, 5), 2);'),
    ("Many lines", 'let lines: Vec<String> = (0..100).map(|i| format!("w{i} x")).collect();\nassert_eq!(count_words_parallel(lines, 3), 200);\nassert_eq!(count_words_parallel(Vec::new(), 3), 0);')],
   [("lines.iter().skip(id).step_by(workers)", "lines.iter().skip(id).step_by(workers + 1)"), ("rx.iter().map(|(_, count)| count).sum()", "rx.iter().take(1).map(|(_, count)| count).sum()")],
   ["Each thread needs its own sender: let tx = tx.clone(); before spawning.", "skip(id).step_by(workers) picks every workers-th line starting at id.", "rx.iter() ends only when every sender is dropped, including the original one."],
   "Channels move data between threads without shared state. The classic hang is forgetting drop(tx): the receiver keeps waiting for a sender that will never send, so the loop never ends.")

ex("16.3", "Shared state with Arc and Mutex",
   "Write an Inventory that many threads can update at once, and a function that proves it.\n\n"
   "Specification:\n- Inventory wraps Arc<Mutex<HashMap<String, i64>>> and derives Clone (cloning shares the same map).\n- add(&self, item, qty) adds qty (which may be negative) to the item's count.\n- count(&self, item) returns the current count (0 if unknown).\n- stress(threads, adds_per_thread) creates an Inventory, starts threads that each call add(\"widget\", 1) that many times, joins them all and returns the final count.\n\n"
   "Examples:\n- stress(8, 1000) returns 8000\n\n"
   "Edge cases: clones of an Inventory see each other's changes.",
   r'''use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::thread;

#[derive(Clone, Default)]
pub struct Inventory {
    items: Arc<Mutex<HashMap<String, i64>>>,
}

impl Inventory {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn add(&self, item: &str, qty: i64) {
        todo!()
    }

    pub fn count(&self, item: &str) -> i64 {
        todo!()
    }
}

pub fn stress(threads: usize, adds_per_thread: usize) -> i64 {
    todo!()
}
''',
   r'''use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::thread;

#[derive(Clone, Default)]
pub struct Inventory {
    items: Arc<Mutex<HashMap<String, i64>>>,
}

impl Inventory {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn add(&self, item: &str, qty: i64) {
        let mut items = self.items.lock().unwrap();
        *items.entry(item.to_string()).or_insert(0) += qty;
    }

    pub fn count(&self, item: &str) -> i64 {
        self.items.lock().unwrap().get(item).copied().unwrap_or(0)
    }
}

pub fn stress(threads: usize, adds_per_thread: usize) -> i64 {
    let inv = Inventory::new();
    let handles: Vec<_> = (0..threads)
        .map(|_| {
            let inv = inv.clone();
            thread::spawn(move || {
                for _ in 0..adds_per_thread {
                    inv.add("widget", 1);
                }
            })
        })
        .collect();
    for h in handles {
        h.join().unwrap();
    }
    inv.count("widget")
}
''',
   [("Add and count", 'let inv = Inventory::new();\ninv.add("bolt", 5);\ninv.add("bolt", -2);\nassert_eq!(inv.count("bolt"), 3);\nassert_eq!(inv.count("nut"), 0);'),
    ("Clones share", 'let a = Inventory::new();\nlet b = a.clone();\nb.add("x", 1);\nassert_eq!(a.count("x"), 1, "a clone must share the same map");'),
    ("Many threads", 'assert_eq!(stress(8, 1000), 8000);\nassert_eq!(stress(1, 5), 5);')],
   [("*items.entry(item.to_string()).or_insert(0) += qty;", "items.insert(item.to_string(), qty);"), ("    for h in handles {\n        h.join().unwrap();\n    }\n", "    drop(handles);\n")],
   ["lock().unwrap() gives a guard that lets you change the map; the lock is released when the guard is dropped.", "Clone the Inventory (which clones the Arc) for each thread.", "Join every handle before reading the final count."],
   "Arc shares ownership across threads and Mutex makes sure only one thread changes the map at a time. Dropping the handles instead of joining them reads the count while threads are still running: the kind of bug that passes sometimes, which is why the test asks for an exact total.")

ex("16.4", "Send jobs to threads",
   "Write run_jobs(jobs) that runs each boxed job on its own thread and returns the results in the original order.\n\n"
   "Specification:\n- jobs: Vec<Box<dyn FnOnce() -> i32 + Send>>. The Send bound is what lets a job move to another thread.\n- Start all threads first, then collect the results in the same order as the jobs.\n- If a job panics, its result is None; the others still return Some(value). Return Vec<Option<i32>>.\n\n"
   "Examples:\n- three jobs returning 1, 2 and 3 give [Some(1), Some(2), Some(3)]\n\n"
   "Edge cases: an empty Vec returns an empty Vec.",
   r'''use std::thread;

pub type Job = Box<dyn FnOnce() -> i32 + Send>;

pub fn run_jobs(jobs: Vec<Job>) -> Vec<Option<i32>> {
    todo!()
}
''',
   r'''use std::thread;

pub type Job = Box<dyn FnOnce() -> i32 + Send>;

pub fn run_jobs(jobs: Vec<Job>) -> Vec<Option<i32>> {
    let handles: Vec<_> = jobs.into_iter().map(thread::spawn).collect();
    handles.into_iter().map(|h| h.join().ok()).collect()
}
''',
   [("Results in order", 'let jobs: Vec<Job> = vec![Box::new(|| 1), Box::new(|| { std::thread::sleep(std::time::Duration::from_millis(30)); 2 }), Box::new(|| 3)];\nassert_eq!(run_jobs(jobs), vec![Some(1), Some(2), Some(3)]);'),
    ("A panicking job", 'let jobs: Vec<Job> = vec![Box::new(|| 1), Box::new(|| panic!("job failed")), Box::new(|| 3)];\nassert_eq!(run_jobs(jobs), vec![Some(1), None, Some(3)]);'),
    ("Runs in parallel", 'let start = std::time::Instant::now();\nlet jobs: Vec<Job> = (0..4).map(|i| Box::new(move || { std::thread::sleep(std::time::Duration::from_millis(150)); i }) as Job).collect();\nassert_eq!(run_jobs(jobs), vec![Some(0), Some(1), Some(2), Some(3)]);\nassert!(start.elapsed().as_millis() < 450, "4 jobs of 150 ms took {} ms: start them all before joining", start.elapsed().as_millis());'),
    ("Empty", 'assert!(run_jobs(Vec::new()).is_empty());')],
   [("    let handles: Vec<_> = jobs.into_iter().map(thread::spawn).collect();\n    handles.into_iter().map(|h| h.join().ok()).collect()\n", "    jobs.into_iter().map(|j| thread::spawn(j).join().ok()).collect()\n"), ("h.join().ok()", "Some(h.join().unwrap_or(0))")],
   ["thread::spawn accepts any FnOnce + Send + 'static, so a boxed job can be passed straight in.", "join() returns Err when the thread panicked; .ok() turns that into None.", "Collect the handles into a Vec before joining, or the jobs run one after another."],
   "Send is the compiler's proof that a value may move to another thread; Rc, for example, isn't Send, so a job that captured one wouldn't compile. A panic in a thread doesn't crash the program: join reports it, and here it becomes None.")
