"""Practice sets, Track 1 chapters 1 to 5."""
from rspec import ex

# ---------------------------------------------------------------- chapter 1
ex("1.1", "A version banner",
   "Write version_banner(major, minor, patch) that returns the text Rust prints for a version, such as \"Rust 1.85.0\".\n\n"
   "Specification:\n- The parameters are u32 values.\n- Return a String in the form Rust MAJOR.MINOR.PATCH.\n\n"
   "Examples:\n- version_banner(1, 85, 0) returns \"Rust 1.85.0\"\n- version_banner(2, 0, 13) returns \"Rust 2.0.13\"\n\n"
   "Edge cases: zeros are printed as 0, so version_banner(0, 0, 0) is \"Rust 0.0.0\".",
   r'''pub fn version_banner(major: u32, minor: u32, patch: u32) -> String {
    todo!()
}
''',
   r'''pub fn version_banner(major: u32, minor: u32, patch: u32) -> String {
    format!("Rust {major}.{minor}.{patch}")
}
''',
   [("Current version", 'assert_eq!(version_banner(1, 85, 0), "Rust 1.85.0", "version_banner(1, 85, 0)");'),
    ("Two-digit patch", 'assert_eq!(version_banner(2, 0, 13), "Rust 2.0.13", "version_banner(2, 0, 13)");'),
    ("All zeros", 'assert_eq!(version_banner(0, 0, 0), "Rust 0.0.0", "version_banner(0, 0, 0)");')],
   [('"Rust {major}.{minor}.{patch}"', '"Rust {major}.{patch}.{minor}"'), ('"Rust {major}.{minor}.{patch}"', '"rust {major}.{minor}.{patch}"')],
   ["format! works like println! but returns a String instead of printing.", "Variables can go straight inside the braces: {major}.", "The function body is one expression, with no semicolon at the end."],
   "format! builds the text and, because it is the last expression without a semicolon, it becomes the return value. The tests compare the whole string, so the order and the capital R matter.")

ex("1.2", "Hello, anyone",
   "Write greeting(name) that returns a greeting for name, or for the world when no name is given.\n\n"
   "Specification:\n- name is a &str.\n- Surrounding spaces in name are ignored.\n- An empty or blank name greets the world.\n\n"
   "Examples:\n- greeting(\"Ada\") returns \"Hello, Ada!\"\n- greeting(\"  Ferris \") returns \"Hello, Ferris!\"\n- greeting(\"\") returns \"Hello, world!\"\n\n"
   "Edge cases: a name of only spaces also greets the world.",
   r'''pub fn greeting(name: &str) -> String {
    todo!()
}
''',
   r'''pub fn greeting(name: &str) -> String {
    let name = name.trim();
    if name.is_empty() {
        String::from("Hello, world!")
    } else {
        format!("Hello, {name}!")
    }
}
''',
   [("A name", 'assert_eq!(greeting("Ada"), "Hello, Ada!", "greeting(\\"Ada\\")");'),
    ("Spaces around the name", 'assert_eq!(greeting("  Ferris "), "Hello, Ferris!", "greeting(\\"  Ferris \\")");'),
    ("No name", 'assert_eq!(greeting(""), "Hello, world!", "greeting(\\"\\")");\nassert_eq!(greeting("   "), "Hello, world!", "greeting(\\"   \\")");')],
   [("let name = name.trim();\n", ""), ('String::from("Hello, world!")', 'String::from("Hello, !")')],
   ["name.trim() returns the text without surrounding spaces.", "is_empty() tells you whether a string has no characters.", "if/else is an expression: each branch can be the value the function returns."],
   "Trimming first means the blank-name case and the spaces case are both handled by one check. Shadowing name with its trimmed version keeps the rest of the function simple.")

ex("1.3", "Where Cargo puts your program",
   "Write binary_path(name, release) that returns the path where cargo build puts a program, using forward slashes.\n\n"
   "Specification:\n- A debug build goes in target/debug/NAME; a release build (cargo build --release) in target/release/NAME.\n- release is a bool.\n\n"
   "Examples:\n- binary_path(\"hello\", false) returns \"target/debug/hello\"\n- binary_path(\"hello\", true) returns \"target/release/hello\"",
   r'''pub fn binary_path(name: &str, release: bool) -> String {
    todo!()
}
''',
   r'''pub fn binary_path(name: &str, release: bool) -> String {
    let profile = if release { "release" } else { "debug" };
    format!("target/{profile}/{name}")
}
''',
   [("Debug build", 'assert_eq!(binary_path("hello", false), "target/debug/hello", "binary_path(\\"hello\\", false)");'),
    ("Release build", 'assert_eq!(binary_path("hello", true), "target/release/hello", "binary_path(\\"hello\\", true)");'),
    ("Another name", 'assert_eq!(binary_path("guessing_game", true), "target/release/guessing_game", "binary_path(\\"guessing_game\\", true)");')],
   [('if release { "release" } else { "debug" }', 'if release { "debug" } else { "release" }'), ('"target/{profile}/{name}"', '"target/{name}"')],
   ["if can choose a value: let profile = if release { ... } else { ... };", "Both branches must give the same type, here &str.", "Then build the path with format!."],
   "Using if as an expression avoids a mutable variable. The debug and release folders exist side by side, which is why a release build doesn't replace the program you were debugging.")

# ---------------------------------------------------------------- chapter 2
ex("2.1", "Parse a guess",
   "Write parse_guess(input) that turns a line typed by the player into a guess between 1 and 100.\n\n"
   "Specification:\n- Ignore the spaces and newline around the input.\n- Return Some(number) for a whole number from 1 to 100.\n- Return None for anything else: text, negative numbers, 0, numbers above 100.\n\n"
   "Examples:\n- parse_guess(\"42\\n\") returns Some(42)\n- parse_guess(\"abc\") returns None\n- parse_guess(\"101\") returns None\n\n"
   "Edge cases: 1 and 100 are both valid.",
   r'''pub fn parse_guess(input: &str) -> Option<u32> {
    todo!()
}
''',
   r'''pub fn parse_guess(input: &str) -> Option<u32> {
    match input.trim().parse::<u32>() {
        Ok(n) if (1..=100).contains(&n) => Some(n),
        _ => None,
    }
}
''',
   [("A valid guess with a newline", 'assert_eq!(parse_guess("42\\n"), Some(42), "parse_guess(\\"42\\\\n\\")");'),
    ("Not a number", 'assert_eq!(parse_guess("abc"), None, "parse_guess(\\"abc\\")");\nassert_eq!(parse_guess("-5"), None, "parse_guess(\\"-5\\")");'),
    ("Out of range", 'assert_eq!(parse_guess("101"), None, "parse_guess(\\"101\\")");\nassert_eq!(parse_guess("0"), None, "parse_guess(\\"0\\")");'),
    ("The limits", 'assert_eq!(parse_guess(" 1 "), Some(1), "parse_guess(\\" 1 \\")");\nassert_eq!(parse_guess("100"), Some(100), "parse_guess(\\"100\\")");')],
   [("(1..=100)", "(1..100)"), ("input.trim().parse", "input.parse")],
   ["trim() removes the newline that read_line leaves at the end.", "parse::<u32>() returns a Result: Ok(number) or Err.", "A match arm can have a guard: Ok(n) if (1..=100).contains(&n) => ..."],
   "The guessing game's parse step can fail in two ways: not a number, or a number outside the game. Handling both in one match keeps the caller's loop simple: it only ever sees Some(valid guess) or None.")

ex("2.2", "Dice without a crate",
   "Write a tiny random-number generator so tests can use repeatable rolls.\n\n"
   "Specification:\n- next_seed(seed) returns seed * 6364136223846793005 + 1442695040888963407, using wrapping arithmetic so it never panics on overflow.\n- roll(seed) returns a die value from 1 to 6: take next_seed(seed), shift it right by 33 bits, take the remainder after dividing by 6, and add 1. Return it as a u8.\n\n"
   "Examples:\n- next_seed(0) returns 1442695040888963407\n- roll(0) returns 6\n\n"
   "Edge cases: next_seed(u64::MAX) must not panic.",
   r'''pub fn next_seed(seed: u64) -> u64 {
    todo!()
}

pub fn roll(seed: u64) -> u8 {
    todo!()
}
''',
   r'''pub fn next_seed(seed: u64) -> u64 {
    seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407)
}

pub fn roll(seed: u64) -> u8 {
    ((next_seed(seed) >> 33) % 6 + 1) as u8
}
''',
   [("Next seed", 'assert_eq!(next_seed(0), 1442695040888963407, "next_seed(0)");\nassert_eq!(next_seed(1), 7806831264735756412, "next_seed(1)");'),
    ("No overflow panic", 'let _ = next_seed(u64::MAX);'),
    ("Rolls", 'assert_eq!(roll(0), 6, "roll(0)");\nlet mut seed = 7;\nfor _ in 0..1000 {\n    let r = roll(seed);\n    assert!((1..=6).contains(&r), "roll gave {r}");\n    seed = next_seed(seed);\n}'),
    ("Every face appears", 'let mut seen = [false; 6];\nlet mut seed = 42;\nfor _ in 0..200 {\n    seen[(roll(seed) - 1) as usize] = true;\n    seed = next_seed(seed);\n}\nassert!(seen.iter().all(|&s| s), "some die faces never came up: {seen:?}");')],
   [("% 6 + 1", "% 6"), (">> 33", ">> 62")],
   ["Use seed.wrapping_mul(...) and .wrapping_add(...): plain * would panic on overflow in a debug build.", "roll calls next_seed, then shifts with >> 33.", "Convert at the end with as u8."],
   "The rand crate does this properly; a fixed seed makes results repeatable, which is exactly what tests need. Debug builds panic on integer overflow, so the wrapping_ methods state that wrapping is intended. The high bits of this kind of generator are the most random, hence the shift.")

ex("2.3", "Too small, too big",
   "Write feedback(secret, guess) and guesses_needed(secret, guesses).\n\n"
   "Specification:\n- feedback returns \"Too small!\", \"Too big!\" or \"You win!\", using cmp and std::cmp::Ordering.\n- guesses_needed returns Some(n) where n is how many guesses it took to hit the secret (counting the winning one), or None if no guess was right.\n\n"
   "Examples:\n- feedback(50, 20) returns \"Too small!\"\n- guesses_needed(7, &[3, 9, 7, 1]) returns Some(3)\n- guesses_needed(7, &[1, 2]) returns None\n\n"
   "Edge cases: guesses after the winning one are ignored.",
   r'''use std::cmp::Ordering;

pub fn feedback(secret: u32, guess: u32) -> &'static str {
    todo!()
}

pub fn guesses_needed(secret: u32, guesses: &[u32]) -> Option<usize> {
    todo!()
}
''',
   r'''use std::cmp::Ordering;

pub fn feedback(secret: u32, guess: u32) -> &'static str {
    match guess.cmp(&secret) {
        Ordering::Less => "Too small!",
        Ordering::Greater => "Too big!",
        Ordering::Equal => "You win!",
    }
}

pub fn guesses_needed(secret: u32, guesses: &[u32]) -> Option<usize> {
    for (i, &guess) in guesses.iter().enumerate() {
        if feedback(secret, guess) == "You win!" {
            return Some(i + 1);
        }
    }
    None
}
''',
   [("Feedback", 'assert_eq!(feedback(50, 20), "Too small!", "feedback(50, 20)");\nassert_eq!(feedback(50, 80), "Too big!", "feedback(50, 80)");\nassert_eq!(feedback(50, 50), "You win!", "feedback(50, 50)");'),
    ("Counts the winning guess", 'assert_eq!(guesses_needed(7, &[3, 9, 7, 1]), Some(3), "guesses_needed(7, &[3, 9, 7, 1])");\nassert_eq!(guesses_needed(7, &[7]), Some(1), "guesses_needed(7, &[7])");'),
    ("Never found", 'assert_eq!(guesses_needed(7, &[1, 2]), None, "guesses_needed(7, &[1, 2])");\nassert_eq!(guesses_needed(7, &[]), None, "guesses_needed(7, &[])");')],
   [("Ordering::Less => \"Too small!\",\n        Ordering::Greater => \"Too big!\"", "Ordering::Less => \"Too big!\",\n        Ordering::Greater => \"Too small!\""), ("return Some(i + 1);", "return Some(i);")],
   ["guess.cmp(&secret) gives Ordering::Less, Greater or Equal.", "enumerate() gives positions starting at 0, so the count is i + 1.", "Return early from the loop as soon as you find the secret; after the loop return None."],
   "match on Ordering forces you to handle all three outcomes, so no case is forgotten. Comparing guess with secret (not the other way round) decides whether Less means too small, which is the classic swapped-message bug.")

# ---------------------------------------------------------------- chapter 3
ex("3.1", "Constants and shadowing",
   "Write to_seconds(hours, minutes, seconds) using constants, and inner_spaces(text) using shadowing.\n\n"
   "Specification:\n- Define const SECONDS_PER_MINUTE: u32 = 60 and const SECONDS_PER_HOUR: u32 = 3600 and use them.\n- to_seconds returns the total number of seconds as a u32.\n- inner_spaces counts the spaces between the words: first shadow text with its trimmed version (let text = text.trim();), then count the ' ' characters.\n\n"
   "Examples:\n- to_seconds(1, 2, 3) returns 3723\n- inner_spaces(\"  a b  c \") returns 3\n\n"
   "Edge cases: to_seconds(0, 0, 0) is 0; text without spaces between words gives 0.",
   r'''pub const SECONDS_PER_MINUTE: u32 = 0; // set the right values
pub const SECONDS_PER_HOUR: u32 = 0;

pub fn to_seconds(hours: u32, minutes: u32, seconds: u32) -> u32 {
    todo!()
}

pub fn inner_spaces(text: &str) -> usize {
    todo!()
}
''',
   r'''pub const SECONDS_PER_MINUTE: u32 = 60;
pub const SECONDS_PER_HOUR: u32 = 3600;

pub fn to_seconds(hours: u32, minutes: u32, seconds: u32) -> u32 {
    hours * SECONDS_PER_HOUR + minutes * SECONDS_PER_MINUTE + seconds
}

pub fn inner_spaces(text: &str) -> usize {
    let text = text.trim();
    text.chars().filter(|&c| c == ' ').count()
}
''',
   [("Hours, minutes, seconds", 'assert_eq!(to_seconds(1, 2, 3), 3723, "to_seconds(1, 2, 3)");\nassert_eq!(to_seconds(0, 0, 0), 0, "to_seconds(0, 0, 0)");'),
    ("Constants", 'assert_eq!(SECONDS_PER_HOUR, 3600);\nassert_eq!(SECONDS_PER_MINUTE, 60);\nassert_eq!(to_seconds(2, 0, 0), 2 * SECONDS_PER_HOUR);'),
    ("Spaces between words", 'assert_eq!(inner_spaces("  a b  c "), 3, "inner_spaces(\\"  a b  c \\")");\nassert_eq!(inner_spaces(" abc "), 0, "inner_spaces(\\" abc \\")");')],
   [("hours * SECONDS_PER_HOUR + minutes * SECONDS_PER_MINUTE", "hours * SECONDS_PER_MINUTE + minutes * SECONDS_PER_HOUR"), ("    let text = text.trim();\n", "")],
   ["Constants are written in capitals and need a type: const SECONDS_PER_HOUR: u32 = 3600;", "let text = text.trim(); makes a new text that hides the old one: that is shadowing.", "text.chars().filter(|&c| c == ' ').count() counts the spaces."],
   "Named constants explain the numbers and can't be changed by accident. Shadowing reuses a name for a transformed value without needing mut, and the old, untrimmed text can no longer be used by mistake.")

ex("3.2", "Integers that don't overflow",
   "Write average_u8(a, b) and percent_of(part, whole).\n\n"
   "Specification:\n- average_u8 returns the average of two u8 values, rounded down, without overflowing: 200 + 100 doesn't fit in a u8.\n- percent_of returns part as a percentage of whole as an f64, or None when whole is 0. Use checked arithmetic or an explicit check, never a panic.\n\n"
   "Examples:\n- average_u8(200, 100) returns 150\n- percent_of(1, 4) returns Some(25.0)\n- percent_of(3, 0) returns None\n\n"
   "Edge cases: average_u8(255, 255) is 255; average_u8(0, 1) is 0.",
   r'''pub fn average_u8(a: u8, b: u8) -> u8 {
    todo!()
}

pub fn percent_of(part: u32, whole: u32) -> Option<f64> {
    todo!()
}
''',
   r'''pub fn average_u8(a: u8, b: u8) -> u8 {
    ((u16::from(a) + u16::from(b)) / 2) as u8
}

pub fn percent_of(part: u32, whole: u32) -> Option<f64> {
    if whole == 0 {
        None
    } else {
        Some(f64::from(part) * 100.0 / f64::from(whole))
    }
}
''',
   [("Average without overflow", 'assert_eq!(average_u8(200, 100), 150, "average_u8(200, 100)");\nassert_eq!(average_u8(255, 255), 255, "average_u8(255, 255)");'),
    ("Rounds down", 'assert_eq!(average_u8(0, 1), 0, "average_u8(0, 1)");\nassert_eq!(average_u8(3, 4), 3, "average_u8(3, 4)");'),
    ("Percentages", 'assert_eq!(percent_of(1, 4), Some(25.0), "percent_of(1, 4)");\nassert_eq!(percent_of(5, 5), Some(100.0), "percent_of(5, 5)");'),
    ("Zero whole", 'assert_eq!(percent_of(3, 0), None, "percent_of(3, 0)");')],
   [("((u16::from(a) + u16::from(b)) / 2) as u8", "a / 2 + b / 2"), ("f64::from(part) * 100.0 / f64::from(whole)", "f64::from(part / whole) * 100.0")],
   ["Convert to a wider type first: u16::from(a) + u16::from(b) can't overflow.", "Divide, then convert back with as u8: the result always fits.", "Integer division of part by whole gives 0 for 1/4: convert to f64 first."],
   "Widening before adding avoids the overflow that would panic in a debug build. Halving each value first looks clever but loses the half when both are odd. Converting to f64 before dividing keeps the fraction that integer division throws away.")

ex("3.3", "Smallest and largest",
   "Write min_max(values) that takes an array of five readings and returns a tuple (smallest, largest).\n\n"
   "Specification:\n- values has the type [i32; 5].\n- Return (min, max) as a tuple of two i32 values.\n- Use a loop over the array; don't sort it.\n\n"
   "Examples:\n- min_max([3, -1, 7, 0, 7]) returns (-1, 7)\n\n"
   "Edge cases: all equal values return (v, v); negative numbers work.",
   r'''pub fn min_max(values: [i32; 5]) -> (i32, i32) {
    todo!()
}
''',
   r'''pub fn min_max(values: [i32; 5]) -> (i32, i32) {
    let mut low = values[0];
    let mut high = values[0];
    for v in values {
        if v < low {
            low = v;
        }
        if v > high {
            high = v;
        }
    }
    (low, high)
}
''',
   [("Mixed values", 'assert_eq!(min_max([3, -1, 7, 0, 7]), (-1, 7), "min_max([3, -1, 7, 0, 7])");'),
    ("All equal", 'assert_eq!(min_max([4, 4, 4, 4, 4]), (4, 4), "min_max([4; 5])");'),
    ("All negative", 'assert_eq!(min_max([-9, -2, -30, -4, -5]), (-30, -2), "min_max([-9, -2, -30, -4, -5])");'),
    ("Extremes at the ends", 'assert_eq!(min_max([1, 5, 6, 7, 9]), (1, 9), "min_max([1, 5, 6, 7, 9])");\nassert_eq!(min_max([9, 5, 6, 7, 1]), (1, 9), "min_max([9, 5, 6, 7, 1])");')],
   [("let mut low = values[0];", "let mut low = 0;"), ("    (low, high)\n", "    (high, low)\n")],
   ["Start both low and high at values[0], not at 0.", "for v in values loops over the array by value (i32 is Copy).", "Return the tuple as the last expression: (low, high)."],
   "Starting from the first element instead of 0 is what makes all-negative or all-positive arrays work. A fixed-size array type documents that exactly five readings are expected; the compiler rejects any other length.")

ex("3.4", "BMI category",
   "Write bmi(weight_kg, height_m) and bmi_category(weight_kg, height_m).\n\n"
   "Specification:\n- bmi returns weight divided by height squared, as an f64.\n- bmi_category returns \"underweight\" below 18.5, \"normal\" from 18.5 up to but not including 25.0, \"overweight\" from 25.0 up to but not including 30.0, and \"obese\" from 30.0.\n- Use if / else if / else as the final expression of the function.\n\n"
   "Examples:\n- bmi(70.0, 1.75) is about 22.86\n- bmi_category(70.0, 1.75) returns \"normal\"\n\n"
   "Edge cases: a BMI of exactly 25.0 is overweight.",
   r'''pub fn bmi(weight_kg: f64, height_m: f64) -> f64 {
    todo!()
}

pub fn bmi_category(weight_kg: f64, height_m: f64) -> &'static str {
    todo!()
}
''',
   r'''pub fn bmi(weight_kg: f64, height_m: f64) -> f64 {
    weight_kg / (height_m * height_m)
}

pub fn bmi_category(weight_kg: f64, height_m: f64) -> &'static str {
    let value = bmi(weight_kg, height_m);
    if value < 18.5 {
        "underweight"
    } else if value < 25.0 {
        "normal"
    } else if value < 30.0 {
        "overweight"
    } else {
        "obese"
    }
}
''',
   [("BMI value", 'let v = bmi(70.0, 1.75);\nassert!((v - 22.857).abs() < 0.01, "bmi(70.0, 1.75) should be about 22.86, got {v}");'),
    ("Categories", 'assert_eq!(bmi_category(50.0, 1.75), "underweight", "bmi_category(50.0, 1.75)");\nassert_eq!(bmi_category(70.0, 1.75), "normal", "bmi_category(70.0, 1.75)");\nassert_eq!(bmi_category(85.0, 1.75), "overweight", "bmi_category(85.0, 1.75)");\nassert_eq!(bmi_category(100.0, 1.75), "obese", "bmi_category(100.0, 1.75)");'),
    ("Exactly 25 is overweight", 'assert_eq!(bmi_category(25.0, 1.0), "overweight", "bmi_category(25.0, 1.0) has BMI 25.0");\nassert_eq!(bmi_category(18.5, 1.0), "normal", "bmi_category(18.5, 1.0) has BMI 18.5");')],
   [("value < 25.0", "value <= 25.0"), ("weight_kg / (height_m * height_m)", "weight_kg / height_m * height_m")],
   ["Height squared is height_m * height_m; keep it in brackets.", "Check the thresholds from the smallest up with else if.", "Using < at each step makes the boundary value fall into the next category."],
   "Operator precedence is the trap in bmi: without brackets, / and * run left to right. For categories, testing the boundary values themselves (18.5 and 25.0) is what proves the < versus <= choice.")

ex("3.5", "Collatz steps",
   "Write collatz_steps(n) that counts how many steps the Collatz rule takes to reach 1. Use a loop or while loop.\n\n"
   "Specification:\n- While n is not 1: if n is even, halve it; otherwise replace it with 3n + 1. Each change is one step.\n- n is a u64 and at least 1.\n\n"
   "Examples:\n- collatz_steps(1) returns 0\n- collatz_steps(6) returns 8 (6, 3, 10, 5, 16, 8, 4, 2, 1)\n- collatz_steps(27) returns 111\n\n"
   "Edge cases: collatz_steps(2) is 1.",
   r'''pub fn collatz_steps(n: u64) -> u32 {
    todo!()
}
''',
   r'''pub fn collatz_steps(n: u64) -> u32 {
    let mut n = n;
    let mut steps = 0;
    while n != 1 {
        n = if n % 2 == 1 { 3 * n + 1 } else { n / 2 };
        steps += 1;
    }
    steps
}
''',
   [("Already 1", 'assert_eq!(collatz_steps(1), 0, "collatz_steps(1)");\nassert_eq!(collatz_steps(2), 1, "collatz_steps(2)");'),
    ("Six", 'assert_eq!(collatz_steps(6), 8, "collatz_steps(6)");'),
    ("Twenty-seven", 'assert_eq!(collatz_steps(27), 111, "collatz_steps(27)");')],
   [("3 * n + 1", "3 * n - 1"), ("let mut steps = 0;", "let mut steps = 1;")],
   ["Make a mutable copy: let mut n = n;", "n % 2 == 1 tests for odd.", "Count a step every time n changes, and stop when it reaches 1."],
   "This is one of the exercises in Google's Comprehensive Rust. while expresses \"repeat until\" directly, and if as an expression picks the next value in one line.")

# ---------------------------------------------------------------- chapter 4
ex("4.1", "Keep the longest word",
   "Write longest(words) that takes ownership of a vector of Strings and returns the longest one, moving it out instead of cloning it.\n\n"
   "Specification:\n- words is a Vec<String>; return a String.\n- If several are equally long, return the first.\n- An empty vector returns an empty String.\n- Don't call clone.\n\n"
   "Examples:\n- longest(vec![\"tea\", \"coffee\", \"milk\"] as Strings) returns \"coffee\"\n\n"
   "Edge cases: longest(vec![]) returns \"\".",
   r'''pub fn longest(words: Vec<String>) -> String {
    todo!()
}
''',
   r'''pub fn longest(words: Vec<String>) -> String {
    let mut best = String::new();
    for word in words {
        if word.len() > best.len() {
            best = word;
        }
    }
    best
}
''',
   [("Longest word", 'let words = vec!["tea".to_string(), "coffee".to_string(), "milk".to_string()];\nassert_eq!(longest(words), "coffee", "longest([tea, coffee, milk])");'),
    ("First of equals", 'let words = vec!["abc".to_string(), "xyz".to_string()];\nassert_eq!(longest(words), "abc", "longest([abc, xyz])");'),
    ("Empty vector", 'assert_eq!(longest(Vec::new()), "", "longest([])");')],
   [("word.len() > best.len()", "word.len() >= best.len()"), ("            best = word;\n", "            best.push_str(&word);\n")],
   ["for word in words takes each String out of the vector by value.", "Assigning best = word moves the String; nothing is copied.", "Use > so an equally long later word doesn't replace the first."],
   "Because the function owns the vector, it can move a String out of it for free. The vector is consumed by the for loop, so the moved-out values can't be used twice; the compiler checks that for you.")

ex("4.2", "Take it and give it back",
   "Write add_signature(text, name) that takes ownership of a String, appends a signature, and returns it.\n\n"
   "Specification:\n- text is a String (owned); name is a &str.\n- Append a newline, two dashes, a space and the name: \"\\n-- Ada\".\n- Return the same String, without creating a new one with format!.\n\n"
   "Examples:\n- add_signature(\"Hi\".to_string(), \"Ada\") returns \"Hi\\n-- Ada\"\n\n"
   "Edge cases: empty text gives \"\\n-- Ada\".",
   r'''pub fn add_signature(text: String, name: &str) -> String {
    todo!()
}
''',
   r'''pub fn add_signature(mut text: String, name: &str) -> String {
    text.push_str("\n-- ");
    text.push_str(name);
    text
}
''',
   [("Adds the signature", 'assert_eq!(add_signature("Hi".to_string(), "Ada"), "Hi\\n-- Ada", "add_signature(\\"Hi\\", \\"Ada\\")");'),
    ("Empty text", 'assert_eq!(add_signature(String::new(), "Ben"), "\\n-- Ben", "add_signature(\\"\\", \\"Ben\\")");'),
    ("Reuses the String", 'let mut s = String::with_capacity(100);\ns.push_str("Hello");\nlet ptr = s.as_ptr();\nlet out = add_signature(s, "Cy");\nassert_eq!(out.as_ptr(), ptr, "Return the String you were given (push onto it) instead of building a new one");')],
   [('text.push_str("\\n-- ");', 'text.push_str("-- ");'), ("    text.push_str(\"\\n-- \");\n    text.push_str(name);\n    text\n", "    format!(\"{text}\\n-- {name}\")\n")],
   ["Mark the parameter mut to change it: mut text: String.", "push_str appends a &str to a String in place.", "Return text at the end to give ownership back to the caller."],
   "Taking ownership and returning the value is how a function can change a String without borrowing it. Pushing onto the existing String reuses its memory; format! would allocate a new one, which the pointer test detects.")

ex("4.3", "Borrow to read, borrow to change",
   "Write count_char(text, c) that borrows text to read it, and capitalise_first(s) that borrows a String mutably and changes it in place.\n\n"
   "Specification:\n- count_char(text: &str, c: char) -> usize counts occurrences of c.\n- capitalise_first(s: &mut String) upper-cases the first character; it returns nothing.\n\n"
   "Examples:\n- count_char(\"banana\", 'a') returns 3\n- after capitalise_first(&mut s) with s = \"rust\", s is \"Rust\"\n\n"
   "Edge cases: capitalise_first on an empty String leaves it empty; \"élan\" becomes \"Élan\".",
   r'''pub fn count_char(text: &str, c: char) -> usize {
    todo!()
}

pub fn capitalise_first(s: &mut String) {
    todo!()
}
''',
   r'''pub fn count_char(text: &str, c: char) -> usize {
    text.chars().filter(|&x| x == c).count()
}

pub fn capitalise_first(s: &mut String) {
    let mut chars = s.chars();
    if let Some(first) = chars.next() {
        let rest = chars.as_str();
        *s = first.to_uppercase().collect::<String>() + rest;
    }
}
''',
   [("Count characters", 'assert_eq!(count_char("banana", \'a\'), 3, "count_char(\\"banana\\", \'a\')");\nassert_eq!(count_char("banana", \'z\'), 0, "count_char(\\"banana\\", \'z\')");'),
    ("Capitalise in place", 'let mut s = String::from("rust");\ncapitalise_first(&mut s);\nassert_eq!(s, "Rust", "capitalise_first on \\"rust\\"");'),
    ("Empty and accented", 'let mut e = String::new();\ncapitalise_first(&mut e);\nassert_eq!(e, "");\nlet mut a = String::from("élan");\ncapitalise_first(&mut a);\nassert_eq!(a, "Élan", "capitalise_first on \\"élan\\"");')],
   [("x == c", "x != c"), ("*s = first.to_uppercase().collect::<String>() + rest;", "*s = first.to_uppercase().collect::<String>();")],
   ["&str is enough for reading; &mut String is needed to change the caller's value.", "s.chars().next() gives the first character as an Option.", "Build the new text and assign it with *s = ...; to_uppercase() can give more than one char, so collect it."],
   "A shared reference lets the function read without taking ownership; a mutable reference lets it change the caller's String, and the caller writes &mut s to show that. Working with chars rather than bytes keeps accented letters intact.")

ex("4.4", "Slices of text and numbers",
   "Write first_sentence(text) and middle(values), both returning slices that borrow from their input.\n\n"
   "Specification:\n- first_sentence returns the text up to and including the first '.', '!' or '?', with surrounding spaces trimmed. If there is none, return the whole text trimmed.\n- middle returns the slice without its first and last element; for fewer than 3 elements it returns an empty slice.\n\n"
   "Examples:\n- first_sentence(\"Hi there. How are you?\") returns \"Hi there.\"\n- middle(&[1, 2, 3, 4]) returns &[2, 3]\n\n"
   "Edge cases: first_sentence(\"  no ending \") returns \"no ending\"; middle(&[1, 2]) returns &[].",
   r'''pub fn first_sentence(text: &str) -> &str {
    todo!()
}

pub fn middle(values: &[i32]) -> &[i32] {
    todo!()
}
''',
   r'''pub fn first_sentence(text: &str) -> &str {
    match text.find(['.', '!', '?']) {
        Some(i) => text[..=i].trim(),
        None => text.trim(),
    }
}

pub fn middle(values: &[i32]) -> &[i32] {
    if values.len() < 3 {
        &[]
    } else {
        &values[1..values.len() - 1]
    }
}
''',
   [("First sentence", 'assert_eq!(first_sentence("Hi there. How are you?"), "Hi there.", "first_sentence(\\"Hi there. How are you?\\")");\nassert_eq!(first_sentence("Stop! Now."), "Stop!", "first_sentence(\\"Stop! Now.\\")");'),
    ("No ending", 'assert_eq!(first_sentence("  no ending "), "no ending", "first_sentence(\\"  no ending \\")");'),
    ("It borrows", 'let text = String::from(" A. B.");\nlet s = first_sentence(&text);\nassert!(text.as_ptr() as usize <= s.as_ptr() as usize, "Return a slice of the input, not a new String");\nassert_eq!(s, "A.");'),
    ("Middle", 'assert_eq!(middle(&[1, 2, 3, 4]), &[2, 3], "middle(&[1, 2, 3, 4])");\nassert_eq!(middle(&[1, 2, 3]), &[2], "middle(&[1, 2, 3])");'),
    ("Too short", 'assert!(middle(&[1, 2]).is_empty(), "middle(&[1, 2]) should be empty");\nassert!(middle(&[]).is_empty());')],
   [("text[..=i]", "text[..i]"), ("&values[1..values.len() - 1]", "&values[1..]")],
   ["text.find(['.', '!', '?']) finds the first of several characters and gives its byte position.", "&text[..=i] includes the character at i.", "&values[1..values.len() - 1] drops the first and last element."],
   "Slices are views into existing data, so these functions return without copying anything, and the borrow checker makes sure the caller keeps the original alive. The inclusive range ..= keeps the full stop.")

# ---------------------------------------------------------------- chapter 5
ex("5.1", "Users with struct update syntax",
   "Define a struct User and two functions.\n\n"
   "Specification:\n- User (given) has the public fields name: String, email: String, active: bool, logins: u32, and derives Debug, Clone and PartialEq.\n- new_user(name, email) returns an active user with 0 logins, using the field init shorthand.\n- deactivated(user) takes a User and returns a copy with active set to false, using struct update syntax (..user).\n\n"
   "Examples:\n- new_user(\"Ada\".into(), \"ada@example.com\".into()).active is true\n\n"
   "Edge cases: deactivated keeps the name, email and logins.",
   r'''#[derive(Debug, Clone, PartialEq)]
pub struct User {
    pub name: String,
    pub email: String,
    pub active: bool,
    pub logins: u32,
}

pub fn new_user(name: String, email: String) -> User {
    todo!()
}

pub fn deactivated(user: User) -> User {
    todo!()
}
''',
   r'''#[derive(Debug, Clone, PartialEq)]
pub struct User {
    pub name: String,
    pub email: String,
    pub active: bool,
    pub logins: u32,
}

pub fn new_user(name: String, email: String) -> User {
    User { name, email, active: true, logins: 0 }
}

pub fn deactivated(user: User) -> User {
    User { active: false, ..user }
}
''',
   [("New user", 'let u = new_user("Ada".into(), "ada@example.com".into());\nassert_eq!(u, User { name: "Ada".into(), email: "ada@example.com".into(), active: true, logins: 0 });'),
    ("Deactivated", 'let mut u = new_user("Ben".into(), "ben@example.com".into());\nu.logins = 7;\nlet d = deactivated(u);\nassert!(!d.active, "deactivated should set active to false");\nassert_eq!((d.name.as_str(), d.email.as_str(), d.logins), ("Ben", "ben@example.com", 7), "Keep the other fields");')],
   [("active: true, logins: 0", "active: false, logins: 0"), ("User { active: false, ..user }", "User { active: false, logins: 0, ..user }")],
   ["When a variable has the same name as the field, User { name, email, ... } is enough.", "..user fills in every field you didn't list from user.", "deactivated takes user by value, so it can move the Strings into the new User."],
   "Field init shorthand removes repetition, and struct update syntax states \"like this one, except...\". Because ..user moves the Strings, the original user can't be used afterwards, which is why deactivated takes ownership.")

ex("5.2", "Does it fit?",
   "Define a Rect struct and two functions that work with it.\n\n"
   "Specification:\n- Rect has public fields width: u32 and height: u32 and derives Debug.\n- area(r: &Rect) returns width times height.\n- fits_inside(inner: &Rect, outer: &Rect) returns true if inner fits inside outer, either as it is or turned 90 degrees. Touching the edges counts as fitting.\n\n"
   "Examples:\n- fits_inside(&Rect { width: 2, height: 5 }, &Rect { width: 6, height: 3 }) is true (turned)\n\n"
   "Edge cases: equal rectangles fit; a rectangle with a larger area never fits.",
   r'''#[derive(Debug)]
pub struct Rect {
    pub width: u32,
    pub height: u32,
}

pub fn area(r: &Rect) -> u32 {
    todo!()
}

pub fn fits_inside(inner: &Rect, outer: &Rect) -> bool {
    todo!()
}
''',
   r'''#[derive(Debug)]
pub struct Rect {
    pub width: u32,
    pub height: u32,
}

pub fn area(r: &Rect) -> u32 {
    r.width * r.height
}

pub fn fits_inside(inner: &Rect, outer: &Rect) -> bool {
    let as_is = inner.width <= outer.width && inner.height <= outer.height;
    let turned = inner.height <= outer.width && inner.width <= outer.height;
    as_is || turned
}
''',
   [("Area", 'assert_eq!(area(&Rect { width: 3, height: 4 }), 12);'),
    ("Fits as it is", 'assert!(fits_inside(&Rect { width: 2, height: 3 }, &Rect { width: 4, height: 4 }));'),
    ("Fits when turned", 'assert!(fits_inside(&Rect { width: 2, height: 5 }, &Rect { width: 6, height: 3 }), "2x5 fits in 6x3 when turned");'),
    ("Edges and misses", 'assert!(fits_inside(&Rect { width: 4, height: 4 }, &Rect { width: 4, height: 4 }), "Equal rectangles fit");\nassert!(fits_inside(&Rect { width: 4, height: 2 }, &Rect { width: 4, height: 3 }), "4x2 fits in 4x3, touching the sides");\nassert!(!fits_inside(&Rect { width: 5, height: 1 }, &Rect { width: 4, height: 4 }), "5x1 does not fit in 4x4");\nassert!(!fits_inside(&Rect { width: 7, height: 7 }, &Rect { width: 6, height: 9 }));')],
   [("    as_is || turned\n", "    as_is\n"), ("inner.width <= outer.width && inner.height <= outer.height", "inner.width < outer.width && inner.height < outer.height")],
   ["Borrow the rectangles (&Rect): the functions only read them.", "Check two layouts: as it is, and with width and height swapped.", "Use <= so touching the edges counts."],
   "Passing &Rect keeps ownership with the caller. Writing each layout as a named boolean makes the rule readable and easy to test one condition at a time.")

ex("5.3", "A stopwatch with methods",
   "Write a Stopwatch struct with an associated function and methods.\n\n"
   "Specification:\n- Stopwatch::new() returns a stopwatch with no laps (store them in a private Vec<u32> of milliseconds).\n- lap(&mut self, ms) records a lap.\n- total(&self) returns the sum of all laps as a u32.\n- fastest(&self) returns the shortest lap as Option<u32>, None if there are no laps.\n- laps(&self) returns the number of laps.\n\n"
   "Examples:\n- after lap(900) and lap(850), total() is 1750 and fastest() is Some(850)\n\n"
   "Edge cases: a new stopwatch has total 0 and fastest None.",
   r'''pub struct Stopwatch {
    laps: Vec<u32>,
}

impl Stopwatch {
    pub fn new() -> Self {
        todo!()
    }

    pub fn lap(&mut self, ms: u32) {
        todo!()
    }

    pub fn total(&self) -> u32 {
        todo!()
    }

    pub fn fastest(&self) -> Option<u32> {
        todo!()
    }

    pub fn laps(&self) -> usize {
        todo!()
    }
}
''',
   r'''#[derive(Default)]
pub struct Stopwatch {
    laps: Vec<u32>,
}

impl Stopwatch {
    pub fn new() -> Self {
        Stopwatch { laps: Vec::new() }
    }

    pub fn lap(&mut self, ms: u32) {
        self.laps.push(ms);
    }

    pub fn total(&self) -> u32 {
        self.laps.iter().sum()
    }

    pub fn fastest(&self) -> Option<u32> {
        self.laps.iter().copied().min()
    }

    pub fn laps(&self) -> usize {
        self.laps.len()
    }
}
''',
   [("Records laps", 'let mut w = Stopwatch::new();\nw.lap(900);\nw.lap(850);\nassert_eq!(w.laps(), 2);\nassert_eq!(w.total(), 1750, "total after 900 and 850");'),
    ("Fastest lap", 'let mut w = Stopwatch::new();\nfor ms in [900, 850, 870] { w.lap(ms); }\nassert_eq!(w.fastest(), Some(850), "fastest of 900, 850, 870");'),
    ("Empty stopwatch", 'let w = Stopwatch::new();\nassert_eq!((w.total(), w.fastest(), w.laps()), (0, None, 0));')],
   [("self.laps.iter().copied().min()", "self.laps.iter().copied().max()"), ("        self.laps.push(ms);\n", "        self.laps = vec![ms];\n")],
   ["new is an associated function: it has no self and is called Stopwatch::new().", "Methods that change the stopwatch take &mut self; methods that only read take &self.", "iter().sum() adds up; iter().copied().min() gives an Option."],
   "The receiver type documents intent: &mut self for lap, &self for the readers. Keeping laps private means callers can only add laps through lap, so the struct can't be put into a strange state. clippy suggests Default whenever there is a new() with no arguments, hence the derive.")
