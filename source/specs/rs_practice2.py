"""Practice sets, Track 1 chapters 6 to 11."""
from rspec import ex


def mut_ex(lid, title, prompt, impl, mutants, starter, solution, bad, hints, explain):
    cases = [("Your tests pass on the correct code", "")] + [("Catches: " + d, "") for d, _ in mutants]
    ex(lid, title, prompt, starter, solution, cases, bad, hints, explain,
       mutation={"impl": impl, "mutants": [{"desc": d, "code": c} for d, c in mutants]})


# ---------------------------------------------------------------- chapter 6
ex("6.1", "Commands as an enum",
   "Define an enum Command and a function describe(command) that turns one into text.\n\n"
   "Specification:\n- Command has four variants: Quit, Move { x: i32, y: i32 }, Say(String) and Color(u8, u8, u8).\n- describe returns:\n- \"quit\" for Quit\n- \"move to (x, y)\" for Move, such as \"move to (3, -1)\"\n- \"say: TEXT\" for Say\n- \"color #RRGGBB\" for Color, as two upper-case hex digits each, such as \"color #FF8000\"\n\n"
   "Examples:\n- describe(&Command::Say(\"hi\".into())) returns \"say: hi\"\n\n"
   "Edge cases: describe(&Command::Color(0, 0, 0)) returns \"color #000000\".",
   r'''pub enum Command {
    Quit,
    Move { x: i32, y: i32 },
    Say(String),
    Color(u8, u8, u8),
}

pub fn describe(command: &Command) -> String {
    todo!()
}
''',
   r'''pub enum Command {
    Quit,
    Move { x: i32, y: i32 },
    Say(String),
    Color(u8, u8, u8),
}

pub fn describe(command: &Command) -> String {
    match command {
        Command::Quit => String::from("quit"),
        Command::Move { x, y } => format!("move to ({x}, {y})"),
        Command::Say(text) => format!("say: {text}"),
        Command::Color(r, g, b) => format!("color #{r:02X}{g:02X}{b:02X}"),
    }
}
''',
   [("Quit and say", 'assert_eq!(describe(&Command::Quit), "quit");\nassert_eq!(describe(&Command::Say("hi".into())), "say: hi");'),
    ("Move", 'assert_eq!(describe(&Command::Move { x: 3, y: -1 }), "move to (3, -1)");'),
    ("Colour in hex", 'assert_eq!(describe(&Command::Color(255, 128, 0)), "color #FF8000", "describe(Color(255, 128, 0))");\nassert_eq!(describe(&Command::Color(0, 0, 0)), "color #000000", "describe(Color(0, 0, 0))");')],
   [("{r:02X}{g:02X}{b:02X}", "{r:X}{g:X}{b:X}"), ('format!("move to ({x}, {y})")', 'format!("move to ({y}, {x})")')],
   ["match on the enum and give one arm per variant.", "Fields are bound by name in Move { x, y } and by position in Color(r, g, b).", "{r:02X} prints a number as two upper-case hex digits with a leading zero."],
   "Enums with data let each variant carry exactly what it needs, and match makes you handle every variant: add a fifth one and this function stops compiling until you handle it. The 02 in the format spec is what keeps 0 as 00.")

ex("6.2", "Roman numerals",
   "Write roman_value(c) and roman_to_int(s).\n\n"
   "Specification:\n- roman_value returns the value of one Roman numeral character as Option<u32>: I 1, V 5, X 10, L 50, C 100, D 500, M 1000, None for anything else. Use match.\n- roman_to_int converts a whole numeral: add each value, except subtract a value that comes before a larger one (IV is 4). Return None if any character is invalid or the string is empty.\n\n"
   "Examples:\n- roman_to_int(\"MCMXCIV\") returns Some(1994)\n- roman_to_int(\"XLII\") returns Some(42)\n- roman_to_int(\"ABC\") returns None\n\n"
   "Edge cases: roman_to_int(\"\") returns None; lower case is invalid.",
   r'''pub fn roman_value(c: char) -> Option<u32> {
    todo!()
}

pub fn roman_to_int(s: &str) -> Option<u32> {
    todo!()
}
''',
   r'''pub fn roman_value(c: char) -> Option<u32> {
    match c {
        'I' => Some(1),
        'V' => Some(5),
        'X' => Some(10),
        'L' => Some(50),
        'C' => Some(100),
        'D' => Some(500),
        'M' => Some(1000),
        _ => None,
    }
}

pub fn roman_to_int(s: &str) -> Option<u32> {
    if s.is_empty() {
        return None;
    }
    let values: Option<Vec<u32>> = s.chars().map(roman_value).collect();
    let values = values?;
    let mut total = 0;
    for (i, &v) in values.iter().enumerate() {
        match values.get(i + 1) {
            Some(&next) if next > v => total -= v as i64,
            _ => total += v as i64,
        }
    }
    Some(total as u32)
}
''',
   [("Single characters", "assert_eq!(roman_value('X'), Some(10));\nassert_eq!(roman_value('M'), Some(1000));\nassert_eq!(roman_value('Z'), None);"),
    ("Adding", 'assert_eq!(roman_to_int("XLII"), Some(42), "roman_to_int(\\"XLII\\")");\nassert_eq!(roman_to_int("III"), Some(3), "roman_to_int(\\"III\\")");'),
    ("Subtracting", 'assert_eq!(roman_to_int("MCMXCIV"), Some(1994), "roman_to_int(\\"MCMXCIV\\")");\nassert_eq!(roman_to_int("IV"), Some(4), "roman_to_int(\\"IV\\")");'),
    ("Invalid input", 'assert_eq!(roman_to_int("ABC"), None, "roman_to_int(\\"ABC\\")");\nassert_eq!(roman_to_int(""), None, "roman_to_int(\\"\\")");\nassert_eq!(roman_to_int("xii"), None, "roman_to_int(\\"xii\\")");')],
   [("Some(&next) if next > v", "Some(&next) if next >= v"), ("        return None;\n", "        return Some(0);\n")],
   ["Collecting an iterator of Option values into Option<Vec<u32>> gives None if any one is None.", "The ? operator returns None early from a function that returns Option.", "Look at the next value with values.get(i + 1), which is None at the end."],
   "Collecting into Option<Vec<_>> is a compact way to say \"all or nothing\", and ? ends the function as soon as something is invalid. A match with a guard handles the subtract rule and the last character in one place.")

ex("6.3", "Parse a point with let...else",
   "Write parse_point(s) that reads text like \"3,-4\" into a pair of numbers, using ? and let...else for the early exits.\n\n"
   "Specification:\n- Split on the first comma; spaces around each number are allowed.\n- Return Some((x, y)) with two i32 values, or None if there is no comma or either part isn't a number.\n- Use ? for the split and let ... else { return None; } for each number.\n\n"
   "Examples:\n- parse_point(\"3,-4\") returns Some((3, -4))\n- parse_point(\" 10 , 20 \") returns Some((10, 20))\n- parse_point(\"3;4\") returns None\n\n"
   "Edge cases: \"1,2,3\" returns None (the second part \"2,3\" isn't a number).",
   r'''pub fn parse_point(s: &str) -> Option<(i32, i32)> {
    todo!()
}
''',
   r'''pub fn parse_point(s: &str) -> Option<(i32, i32)> {
    let (left, right) = s.split_once(',')?;
    let Ok(x) = left.trim().parse() else {
        return None;
    };
    let Ok(y) = right.trim().parse() else {
        return None;
    };
    Some((x, y))
}
''',
   [("Simple point", 'assert_eq!(parse_point("3,-4"), Some((3, -4)), "parse_point(\\"3,-4\\")");'),
    ("Spaces", 'assert_eq!(parse_point(" 10 , 20 "), Some((10, 20)), "parse_point(\\" 10 , 20 \\")");'),
    ("No comma", 'assert_eq!(parse_point("3;4"), None, "parse_point(\\"3;4\\")");'),
    ("Bad numbers", 'assert_eq!(parse_point("a,1"), None, "parse_point(\\"a,1\\")");\nassert_eq!(parse_point("1,2,3"), None, "parse_point(\\"1,2,3\\")");')],
   [("left.trim().parse()", "left.parse()"), ("let Ok(y) = right.trim().parse() else {\n        return None;\n    };", "let y = right.trim().parse().unwrap_or(0);")],
   ["s.split_once(',') returns Some((before, after)) or None.", "let Ok(x) = left.trim().parse() else { return None; }; keeps the happy path unindented.", "parse() needs to know the type; the return type Option<(i32, i32)> tells it."],
   "let...else keeps the main path flat: each line either binds a value or leaves the function. Using unwrap_or(0) instead would silently turn bad input into a point, which the tests catch.")

# ---------------------------------------------------------------- chapter 7
ex("7.1", "Keep main thin",
   "Write the library half of a small command-line tool: parse_args(args) turns the arguments into a Config, so main only has to print.\n\n"
   "Specification:\n- Config has public fields name: String and times: u32 and derives Debug and PartialEq.\n- args are the arguments after the program name, as &[&str].\n- The first argument is the name (required); the optional second is how many times to greet (default 1).\n- Return Err(\"usage: greet NAME [TIMES]\") with no name, and Err(\"TIMES must be a positive number\") if TIMES isn't a number above 0.\n\n"
   "Examples:\n- parse_args(&[\"Ada\"]) returns Ok(Config { name: \"Ada\", times: 1 })\n- parse_args(&[\"Ada\", \"3\"]) returns times 3\n\n"
   "Edge cases: \"0\" and \"-2\" are rejected; extra arguments are ignored.",
   r'''#[derive(Debug, PartialEq)]
pub struct Config {
    pub name: String,
    pub times: u32,
}

pub fn parse_args(args: &[&str]) -> Result<Config, String> {
    todo!()
}
''',
   r'''#[derive(Debug, PartialEq)]
pub struct Config {
    pub name: String,
    pub times: u32,
}

pub fn parse_args(args: &[&str]) -> Result<Config, String> {
    let name = args.first().ok_or("usage: greet NAME [TIMES]")?;
    let times = match args.get(1) {
        None => 1,
        Some(t) => match t.parse::<u32>() {
            Ok(n) if n > 0 => n,
            _ => return Err(String::from("TIMES must be a positive number")),
        },
    };
    Ok(Config { name: name.to_string(), times })
}
''',
   [("Name only", 'assert_eq!(parse_args(&["Ada"]), Ok(Config { name: "Ada".into(), times: 1 }));'),
    ("Name and times", 'assert_eq!(parse_args(&["Ada", "3"]), Ok(Config { name: "Ada".into(), times: 3 }));'),
    ("No arguments", 'assert_eq!(parse_args(&[]), Err("usage: greet NAME [TIMES]".to_string()));'),
    ("Bad times", 'for bad in ["0", "-2", "x"] {\n    assert_eq!(parse_args(&["Ada", bad]), Err("TIMES must be a positive number".to_string()), "parse_args([Ada, {bad}])");\n}')],
   [("Ok(n) if n > 0 => n,", "Ok(n) => n,"), ("None => 1,", "None => 0,")],
   ["args.first() is an Option; ok_or turns it into a Result, and ? returns the error.", "args.get(1) is None when TIMES was left out.", "A match guard (Ok(n) if n > 0) rejects zero."],
   "Putting the parsing in the library means it can be tested without running the program: these tests pass a slice instead of reading std::env::args. That is the book's \"keep main thin\" advice, and Chapter 12 builds minigrep the same way.")

ex("7.2", "A bank module with private fields",
   "Write a module bank with an Account type whose balance can only change through its methods.\n\n"
   "Specification:\n- Inside pub mod bank, define pub struct Account with a public owner: String and a private balance: i64.\n- Account::new(owner) starts at 0.\n- deposit(amount) adds; withdraw(amount) returns Err(\"insufficient funds\") and changes nothing if amount is more than the balance, otherwise Ok(()).\n- balance(&self) returns the balance.\n\n"
   "Examples:\n- after deposit(100) and withdraw(30), balance() is 70\n\n"
   "Edge cases: withdrawing exactly the balance is allowed.",
   r'''pub mod bank {
    pub struct Account {
        pub owner: String,
        balance: i64,
    }

    impl Account {
        pub fn new(owner: &str) -> Self {
            todo!()
        }

        pub fn deposit(&mut self, amount: i64) {
            todo!()
        }

        pub fn withdraw(&mut self, amount: i64) -> Result<(), String> {
            todo!()
        }

        pub fn balance(&self) -> i64 {
            todo!()
        }
    }
}
''',
   r'''pub mod bank {
    pub struct Account {
        pub owner: String,
        balance: i64,
    }

    impl Account {
        pub fn new(owner: &str) -> Self {
            Account { owner: owner.to_string(), balance: 0 }
        }

        pub fn deposit(&mut self, amount: i64) {
            self.balance += amount;
        }

        pub fn withdraw(&mut self, amount: i64) -> Result<(), String> {
            if amount > self.balance {
                return Err(String::from("insufficient funds"));
            }
            self.balance -= amount;
            Ok(())
        }

        pub fn balance(&self) -> i64 {
            self.balance
        }
    }
}
''',
   [("Deposit and withdraw", 'let mut a = bank::Account::new("Ada");\na.deposit(100);\nassert_eq!(a.withdraw(30), Ok(()));\nassert_eq!(a.balance(), 70);\nassert_eq!(a.owner, "Ada");'),
    ("Refused withdrawal", 'let mut a = bank::Account::new("Ben");\na.deposit(10);\nassert_eq!(a.withdraw(11), Err("insufficient funds".to_string()));\nassert_eq!(a.balance(), 10, "A refused withdrawal must not change the balance");'),
    ("Exact balance", 'let mut a = bank::Account::new("Cy");\na.deposit(10);\nassert_eq!(a.withdraw(10), Ok(()));\nassert_eq!(a.balance(), 0);')],
   [("if amount > self.balance {", "if amount > self.balance + 1 {"), ("            if amount > self.balance {\n                return Err(String::from(\"insufficient funds\"));\n            }\n            self.balance -= amount;\n", "            self.balance -= amount;\n            if self.balance < 0 {\n                return Err(String::from(\"insufficient funds\"));\n            }\n")],
   ["Code outside the module can't read balance directly; that is the point.", "Check before subtracting, so a refused withdrawal changes nothing.", "The tests reach the type through its path: bank::Account."],
   "Making the field private and the methods public means every change goes through withdraw's check, so no code anywhere can make the balance wrong. Try a.balance = 5 in a test: the compiler refuses, which is the encapsulation working.")

ex("7.3", "Paths, use and re-exports",
   "Write nested modules for unit conversion and re-export the most used function at the top.\n\n"
   "Specification:\n- pub mod units contains pub mod length with km_to_miles(km: f64) -> f64 (multiply by 0.621371) and pub mod weight with kg_to_lb(kg: f64) -> f64 (multiply by 2.20462).\n- Add pub use units::length::km_to_miles; at the top level so callers can write km_to_miles directly.\n- Also add pub fn marathon_miles() -> f64 at the top level that converts 42.195 km using a use declaration inside the function body.\n\n"
   "Examples:\n- units::weight::kg_to_lb(10.0) is about 22.05\n- km_to_miles(5.0) is about 3.107\n\n"
   "Edge cases: both paths, units::length::km_to_miles and km_to_miles, give the same result.",
   r'''pub mod units {
    pub mod length {
        pub fn km_to_miles(km: f64) -> f64 {
            todo!()
        }
    }

    pub mod weight {
        pub fn kg_to_lb(kg: f64) -> f64 {
            todo!()
        }
    }
}

pub use units::length::km_to_miles;

pub fn marathon_miles() -> f64 {
    todo!()
}
''',
   r'''pub mod units {
    pub mod length {
        pub fn km_to_miles(km: f64) -> f64 {
            km * 0.621371
        }
    }

    pub mod weight {
        pub fn kg_to_lb(kg: f64) -> f64 {
            kg * 2.20462
        }
    }
}

pub use units::length::km_to_miles;

pub fn marathon_miles() -> f64 {
    use crate::units::length;
    length::km_to_miles(42.195)
}
''',
   [("Full paths", 'let lb = units::weight::kg_to_lb(10.0);\nassert!((lb - 22.0462).abs() < 1e-6, "kg_to_lb(10.0) gave {lb}");\nlet mi = units::length::km_to_miles(5.0);\nassert!((mi - 3.106855).abs() < 1e-6, "km_to_miles(5.0) gave {mi}");'),
    ("Re-export", 'assert_eq!(km_to_miles(5.0), units::length::km_to_miles(5.0));'),
    ("Marathon", 'let m = marathon_miles();\nassert!((m - 26.2188).abs() < 0.001, "marathon_miles() gave {m}");')],
   [("km * 0.621371", "km / 0.621371"), ("length::km_to_miles(42.195)", "length::km_to_miles(42.0)")],
   ["Nested modules are written inside each other's braces.", "pub use makes a name available at a new path as part of your public API.", "Inside a function, use crate::units::length; brings the module into that scope only."],
   "Re-exports let you organise code one way internally and present a shorter, friendlier path to users. A use inside a function keeps the import close to the only code that needs it.")

ex("7.4", "Modules that use each other",
   "Write an inventory module with a nested item module, where code refers to its parent with super.\n\n"
   "Specification:\n- pub mod inventory contains pub const TAX_RATE: f64 = 0.15 and pub mod item.\n- item has pub struct Item { pub name: String, pub price: f64, pub qty: u32 } and a method price_with_tax(&self) that uses super::TAX_RATE.\n- inventory has pub fn total_value(items: &[item::Item]) -> f64: the sum of price_with_tax * qty for all items.\n\n"
   "Examples:\n- an Item with price 10.0 has price_with_tax 11.5\n- total_value of [10.0 x 2, 4.0 x 1] is 27.6\n\n"
   "Edge cases: an empty slice has total 0.0.",
   r'''pub mod inventory {
    pub const TAX_RATE: f64 = 0.15;

    pub mod item {
        pub struct Item {
            pub name: String,
            pub price: f64,
            pub qty: u32,
        }

        impl Item {
            pub fn price_with_tax(&self) -> f64 {
                todo!()
            }
        }
    }

    pub fn total_value(items: &[item::Item]) -> f64 {
        todo!()
    }
}
''',
   r'''pub mod inventory {
    pub const TAX_RATE: f64 = 0.15;

    pub mod item {
        pub struct Item {
            pub name: String,
            pub price: f64,
            pub qty: u32,
        }

        impl Item {
            pub fn price_with_tax(&self) -> f64 {
                self.price * (1.0 + super::TAX_RATE)
            }
        }
    }

    pub fn total_value(items: &[item::Item]) -> f64 {
        items.iter().map(|i| i.price_with_tax() * f64::from(i.qty)).sum()
    }
}
''',
   [("Price with tax", 'use inventory::item::Item;\nlet tea = Item { name: "tea".into(), price: 10.0, qty: 1 };\nassert!((tea.price_with_tax() - 11.5).abs() < 1e-9, "price_with_tax for 10.0");'),
    ("Total value", 'use inventory::item::Item;\nlet items = [Item { name: "tea".into(), price: 10.0, qty: 2 }, Item { name: "jam".into(), price: 4.0, qty: 1 }];\nlet t = inventory::total_value(&items);\nassert!((t - 27.6).abs() < 1e-9, "total_value gave {t}");'),
    ("Empty", 'assert_eq!(inventory::total_value(&[]), 0.0);')],
   [("self.price * (1.0 + super::TAX_RATE)", "self.price * super::TAX_RATE"), ("i.price_with_tax() * f64::from(i.qty)", "i.price_with_tax()")],
   ["super:: refers to the parent module, like .. in a file path.", "Inside inventory, the nested module is reached as item::Item.", "map each item to its value and sum() the results."],
   "super keeps a child module tied to its parent without spelling out the whole path from the crate root, so moving the pair elsewhere doesn't break it. The same structure works when the modules move into inventory.rs and inventory/item.rs.")

# ---------------------------------------------------------------- chapter 8
ex("8.1", "Running totals and rotation",
   "Write running_total(values) and rotate_left(values, k).\n\n"
   "Specification:\n- running_total returns a new Vec where each element is the sum of all values up to and including that position.\n- rotate_left(values: &mut [i32], k) changes the values in place, moving the first k elements to the end. k may be larger than the length (wrap around).\n\n"
   "Examples:\n- running_total(&[1, 2, 3, 4]) returns vec![1, 3, 6, 10]\n- rotate_left on [1, 2, 3, 4, 5] with k = 2 gives [3, 4, 5, 1, 2]\n\n"
   "Edge cases: an empty vector stays empty for both; k = 7 on 5 elements is the same as k = 2.",
   r'''pub fn running_total(values: &[i32]) -> Vec<i32> {
    todo!()
}

pub fn rotate_left(values: &mut [i32], k: usize) {
    todo!()
}
''',
   r'''pub fn running_total(values: &[i32]) -> Vec<i32> {
    let mut totals = Vec::with_capacity(values.len());
    let mut sum = 0;
    for &v in values {
        sum += v;
        totals.push(sum);
    }
    totals
}

pub fn rotate_left(values: &mut [i32], k: usize) {
    if values.is_empty() {
        return;
    }
    let k = k % values.len();
    values.rotate_left(k);
}
''',
   [("Running total", 'assert_eq!(running_total(&[1, 2, 3, 4]), vec![1, 3, 6, 10]);\nassert_eq!(running_total(&[5, -5, 2]), vec![5, 0, 2]);\nassert!(running_total(&[]).is_empty());'),
    ("Rotate", 'let mut v = vec![1, 2, 3, 4, 5];\nrotate_left(&mut v, 2);\nassert_eq!(v, vec![3, 4, 5, 1, 2]);'),
    ("Rotate wraps around", 'let mut v = vec![1, 2, 3, 4, 5];\nrotate_left(&mut v, 7);\nassert_eq!(v, vec![3, 4, 5, 1, 2], "k = 7 on 5 elements is k = 2");'),
    ("Rotate empty", 'let mut v: Vec<i32> = Vec::new();\nrotate_left(&mut v, 3);\nassert!(v.is_empty());')],
   [("        sum += v;\n        totals.push(sum);\n", "        totals.push(sum);\n        sum += v;\n"), ("    let k = k % values.len();\n", "    let k = k.min(values.len());\n")],
   ["Keep a running sum in a mutable variable and push it after each addition.", "Slices and vectors have a rotate_left method; you only need to handle k.", "k % len wraps k into range; check for an empty vector first to avoid dividing by zero."],
   "Taking &[i32] for input and &mut [i32] for in-place change makes each function's effect clear from its signature. The modulo handles big k values, and the empty check prevents the division-by-zero panic that % 0 would cause.")

ex("8.2", "Acronyms and safe truncation",
   "Write acronym(phrase) and truncate_chars(s, n).\n\n"
   "Specification:\n- acronym returns the upper-case first letter of each word. Words are separated by spaces or hyphens; other punctuation is ignored.\n- truncate_chars returns at most n characters (not bytes) of s; if it cut anything off, it adds \"…\" (one character) so the result has n + 1 characters.\n\n"
   "Examples:\n- acronym(\"Portable Network Graphics\") returns \"PNG\"\n- acronym(\"Complementary metal-oxide semiconductor\") returns \"CMOS\"\n- truncate_chars(\"héllo wörld\", 5) returns \"héllo…\"\n\n"
   "Edge cases: truncate_chars(\"tea\", 5) returns \"tea\" unchanged; acronym(\"\") returns \"\".",
   r'''pub fn acronym(phrase: &str) -> String {
    todo!()
}

pub fn truncate_chars(s: &str, n: usize) -> String {
    todo!()
}
''',
   r'''pub fn acronym(phrase: &str) -> String {
    phrase
        .split([' ', '-'])
        .filter_map(|word| word.chars().find(|c| c.is_alphabetic()))
        .flat_map(char::to_uppercase)
        .collect()
}

pub fn truncate_chars(s: &str, n: usize) -> String {
    if s.chars().count() <= n {
        return s.to_string();
    }
    let mut out: String = s.chars().take(n).collect();
    out.push('…');
    out
}
''',
   [("Acronym", 'assert_eq!(acronym("Portable Network Graphics"), "PNG");\nassert_eq!(acronym("as soon as possible"), "ASAP");'),
    ("Hyphens and punctuation", 'assert_eq!(acronym("Complementary metal-oxide semiconductor"), "CMOS");\nassert_eq!(acronym("Hello, (big) world"), "HBW");\nassert_eq!(acronym(""), "");'),
    ("Truncate by characters", 'assert_eq!(truncate_chars("héllo wörld", 5), "héllo…", "truncate_chars(\\"héllo wörld\\", 5)");'),
    ("Short enough", 'assert_eq!(truncate_chars("tea", 5), "tea");\nassert_eq!(truncate_chars("tea", 3), "tea");\nassert_eq!(truncate_chars("héllo", 5), "héllo", "5 characters (but 6 bytes) fit in 5");')],
   [(".split([' ', '-'])", ".split(' ')"), ("if s.chars().count() <= n {", "if s.len() <= n {")],
   ["split accepts several separators: split([' ', '-']).", "find(|c| c.is_alphabetic()) skips leading punctuation such as (.", "Count and take characters with chars(), not bytes: é is two bytes."],
   "Rust strings are UTF-8, so byte positions and character positions differ: slicing &s[..5] could even panic in the middle of é. Working with chars() keeps both functions correct for any text.")

ex("8.3", "Word frequencies",
   "Write word_counts(text) and top_word(text) using a HashMap.\n\n"
   "Specification:\n- word_counts returns a HashMap<String, usize> of each word in lower case. Words are separated by whitespace; strip punctuation from the start and end of each word with trim_matches and char::is_alphanumeric. Skip words that become empty.\n- top_word returns the most frequent word as Option<String>; ties go to the word that comes first alphabetically.\n\n"
   "Examples:\n- word_counts(\"The cat. the CAT, the dog!\") has the 3, cat 2, dog 1\n- top_word(\"b a b a\") returns Some(\"a\")\n\n"
   "Edge cases: top_word(\"\") returns None; \"--\" is not a word.",
   r'''use std::collections::HashMap;

pub fn word_counts(text: &str) -> HashMap<String, usize> {
    todo!()
}

pub fn top_word(text: &str) -> Option<String> {
    todo!()
}
''',
   r'''use std::collections::HashMap;

pub fn word_counts(text: &str) -> HashMap<String, usize> {
    let mut counts = HashMap::new();
    for word in text.split_whitespace() {
        let word = word.trim_matches(|c: char| !c.is_alphanumeric()).to_lowercase();
        if !word.is_empty() {
            *counts.entry(word).or_insert(0) += 1;
        }
    }
    counts
}

pub fn top_word(text: &str) -> Option<String> {
    word_counts(text)
        .into_iter()
        .max_by(|(wa, ca), (wb, cb)| ca.cmp(cb).then_with(|| wb.cmp(wa)))
        .map(|(word, _)| word)
}
''',
   [("Counts", 'let c = word_counts("The cat. the CAT, the dog!");\nassert_eq!(c.get("the"), Some(&3));\nassert_eq!(c.get("cat"), Some(&2));\nassert_eq!(c.get("dog"), Some(&1));\nassert_eq!(c.len(), 3, "word_counts gave {c:?}");'),
    ("Punctuation only", 'assert!(word_counts("-- !!").is_empty());'),
    ("Top word", 'assert_eq!(top_word("the cat the"), Some("the".to_string()));'),
    ("Ties and empty", 'assert_eq!(top_word("b a b a"), Some("a".to_string()), "Ties go to the alphabetically first word");\nassert_eq!(top_word(""), None);')],
   [(".to_lowercase();", ".to_string();"), ("ca.cmp(cb).then_with(|| wb.cmp(wa))", "ca.cmp(cb).then_with(|| wa.cmp(wb))")],
   ["entry(word).or_insert(0) gives a mutable count to add to.", "trim_matches(|c: char| !c.is_alphanumeric()) strips punctuation from both ends.", "max_by with ca.cmp(cb).then_with(...) picks the biggest count and breaks ties."],
   "The entry API does lookup-or-insert in one step. HashMap order is random, so the tie rule must be part of the comparison: then_with reverses the word order so that, among equal counts, the alphabetically first word counts as the largest.")

# ---------------------------------------------------------------- chapter 9
ex("9.1", "Panics for bugs",
   "Write percent(part, whole) that panics when called wrongly, because that is a bug in the caller.\n\n"
   "Specification:\n- Return part * 100 / whole as a u32 (integer division).\n- If whole is 0, panic with a message containing \"whole must not be zero\".\n- If part is greater than whole, panic with a message containing \"part is larger than whole\".\n\n"
   "Examples:\n- percent(1, 4) returns 25\n- percent(5, 0) panics\n\n"
   "Edge cases: percent(0, 7) returns 0; percent(7, 7) returns 100.",
   r'''pub fn percent(part: u32, whole: u32) -> u32 {
    todo!()
}
''',
   r'''pub fn percent(part: u32, whole: u32) -> u32 {
    assert!(whole != 0, "whole must not be zero");
    assert!(part <= whole, "part is larger than whole: {part} > {whole}");
    part * 100 / whole
}
''',
   [("Normal use", 'assert_eq!(percent(1, 4), 25);\nassert_eq!(percent(0, 7), 0);\nassert_eq!(percent(7, 7), 100);'),
    ("Zero whole panics", 'percent(5, 0);', '#[should_panic(expected = "whole must not be zero")]'),
    ("Part too large panics", 'percent(9, 4);', '#[should_panic(expected = "part is larger than whole")]')],
   [('    assert!(part <= whole, "part is larger than whole: {part} > {whole}");\n', ""), ('assert!(whole != 0, "whole must not be zero");', 'assert!(whole != 0, "division by zero");')],
   ["assert!(condition, \"message\") panics with the message when the condition is false.", "Check the inputs first, then compute.", "The expected text in should_panic only has to appear somewhere in the message."],
   "These conditions mean the calling code is wrong, not that the input was unlucky, so a panic with a clear message is right. #[should_panic(expected = ...)] tests that the right panic happens, not just any panic.")

ex("9.2", "Errors with Result and ?",
   "Write sum_lines(text) that adds up one integer per line, returning an error that names the bad line.\n\n"
   "Specification:\n- Blank lines (only spaces) are skipped; spaces around numbers are allowed.\n- On success return Ok(total) as i64.\n- On a line that isn't a number, return Err(\"line N: 'TEXT' is not a number\") where N counts from 1 and TEXT is the trimmed line.\n- Use map_err and ? rather than match for the error.\n\n"
   "Examples:\n- sum_lines(\"1\\n2\\n\\n 3 \") returns Ok(6)\n- sum_lines(\"4\\nfive\") returns Err(\"line 2: 'five' is not a number\")\n\n"
   "Edge cases: an empty text returns Ok(0); negative numbers are fine.",
   r'''pub fn sum_lines(text: &str) -> Result<i64, String> {
    todo!()
}
''',
   r'''pub fn sum_lines(text: &str) -> Result<i64, String> {
    let mut total = 0;
    for (i, line) in text.lines().enumerate() {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        let n: i64 = line
            .parse()
            .map_err(|_| format!("line {}: '{}' is not a number", i + 1, line))?;
        total += n;
    }
    Ok(total)
}
''',
   [("Adds the lines", 'assert_eq!(sum_lines("1\\n2\\n\\n 3 "), Ok(6));\nassert_eq!(sum_lines("-5\\n5"), Ok(0));'),
    ("Empty", 'assert_eq!(sum_lines(""), Ok(0));'),
    ("Names the bad line", 'assert_eq!(sum_lines("4\\nfive"), Err("line 2: \'five\' is not a number".to_string()));\nassert_eq!(sum_lines("1\\n\\n x "), Err("line 3: \'x\' is not a number".to_string()));')],
   [("i + 1, line", "i, line"), ("        if line.is_empty() {\n            continue;\n        }\n", "")],
   ["text.lines().enumerate() gives (index, line) with the index from 0.", "map_err turns the ParseIntError into your own message.", "? returns the error from the function immediately."],
   "map_err plus ? keeps the happy path short while giving an error a person can act on: which line and what it contained. Counting blank lines in N, even though they are skipped, keeps the number matching what an editor shows.")

ex("9.3", "A type that can't be wrong",
   "Write a Percentage type that can only hold values from 0 to 100.\n\n"
   "Specification:\n- pub struct Percentage(u8) with a private field.\n- Percentage::new(value: i32) returns Ok(Percentage) for 0 to 100, otherwise Err(format!(\"{value} is not between 0 and 100\")).\n- value(&self) returns the u8.\n- of(&self, amount: f64) returns that percentage of amount.\n\n"
   "Examples:\n- Percentage::new(15)?.of(200.0) returns 30.0\n- Percentage::new(120) returns Err(\"120 is not between 0 and 100\")\n\n"
   "Edge cases: 0 and 100 are valid; -1 is not.",
   r'''pub struct Percentage(u8);

impl Percentage {
    pub fn new(value: i32) -> Result<Percentage, String> {
        todo!()
    }

    pub fn value(&self) -> u8 {
        todo!()
    }

    pub fn of(&self, amount: f64) -> f64 {
        todo!()
    }
}
''',
   r'''pub struct Percentage(u8);

impl Percentage {
    pub fn new(value: i32) -> Result<Percentage, String> {
        if (0..=100).contains(&value) {
            Ok(Percentage(value as u8))
        } else {
            Err(format!("{value} is not between 0 and 100"))
        }
    }

    pub fn value(&self) -> u8 {
        self.0
    }

    pub fn of(&self, amount: f64) -> f64 {
        amount * f64::from(self.0) / 100.0
    }
}
''',
   [("Valid values", 'assert_eq!(Percentage::new(15).unwrap().value(), 15);\nassert_eq!(Percentage::new(0).unwrap().value(), 0);\nassert_eq!(Percentage::new(100).unwrap().value(), 100);'),
    ("Out of range", 'assert_eq!(Percentage::new(120).err(), Some("120 is not between 0 and 100".to_string()));\nassert_eq!(Percentage::new(-1).err(), Some("-1 is not between 0 and 100".to_string()));'),
    ("Percentage of", 'assert_eq!(Percentage::new(15).unwrap().of(200.0), 30.0);')],
   [("(0..=100).contains(&value)", "(0..100).contains(&value)"), ("amount * f64::from(self.0) / 100.0", "amount * f64::from(self.0)")],
   ["Check the range in new; it is the only way to build a Percentage outside this module.", "(0..=100).contains(&value) includes both ends.", "self.0 is the first (and only) field of a tuple struct."],
   "Validating once in the constructor means every Percentage in the program is known to be valid, so no other function needs to check again. This is \"parse, don't validate\", and it is how the book suggests deciding between panics and Result for values that cross a boundary.")

# ---------------------------------------------------------------- chapter 10
ex("10.1", "Generic helpers",
   "Write a generic function largest and a generic struct Pair.\n\n"
   "Specification:\n- largest<T: PartialOrd + Copy>(items: &[T]) -> Option<T> returns the largest item, None for an empty slice. Ties return the first.\n- pub struct Pair<T> { pub a: T, pub b: T } with swap(self) -> Pair<T> that returns the pair with a and b exchanged, and, only when T: PartialOrd + Copy, max(&self) -> T.\n\n"
   "Examples:\n- largest(&[3, 9, 2]) returns Some(9)\n- largest(&['x', 'b']) returns Some('x')\n- Pair { a: 1, b: 2 }.swap() is Pair { a: 2, b: 1 }\n\n"
   "Edge cases: largest(&[] as &[i32]) returns None; floats work: largest(&[1.5, -2.0]) returns Some(1.5).",
   r'''pub fn largest<T: PartialOrd + Copy>(items: &[T]) -> Option<T> {
    todo!()
}

#[derive(Debug, PartialEq)]
pub struct Pair<T> {
    pub a: T,
    pub b: T,
}

impl<T> Pair<T> {
    pub fn swap(self) -> Pair<T> {
        todo!()
    }
}

impl<T: PartialOrd + Copy> Pair<T> {
    pub fn max(&self) -> T {
        todo!()
    }
}
''',
   r'''pub fn largest<T: PartialOrd + Copy>(items: &[T]) -> Option<T> {
    let mut best = *items.first()?;
    for &item in items {
        if item > best {
            best = item;
        }
    }
    Some(best)
}

#[derive(Debug, PartialEq)]
pub struct Pair<T> {
    pub a: T,
    pub b: T,
}

impl<T> Pair<T> {
    pub fn swap(self) -> Pair<T> {
        Pair { a: self.b, b: self.a }
    }
}

impl<T: PartialOrd + Copy> Pair<T> {
    pub fn max(&self) -> T {
        if self.b > self.a { self.b } else { self.a }
    }
}
''',
   [("Largest of numbers and chars", "assert_eq!(largest(&[3, 9, 2]), Some(9));\nassert_eq!(largest(&['x', 'b']), Some('x'));\nassert_eq!(largest(&[1.5, -2.0]), Some(1.5));"),
    ("Empty slice", 'let empty: &[i32] = &[];\nassert_eq!(largest(empty), None);'),
    ("Swap", 'assert_eq!(Pair { a: 1, b: 2 }.swap(), Pair { a: 2, b: 1 });\nassert_eq!(Pair { a: "x", b: "y" }.swap(), Pair { a: "y", b: "x" });'),
    ("Max of a pair", "assert_eq!(Pair { a: 4, b: 7 }.max(), 7);\nassert_eq!(Pair { a: 'z', b: 'a' }.max(), 'z');")],
   [("if item > best {", "if item < best {"), ("Pair { a: self.b, b: self.a }", "Pair { a: self.a, b: self.b }")],
   ["*items.first()? gives the first item or returns None for an empty slice.", "Comparing needs PartialOrd; copying the value out of the slice needs Copy.", "A second impl block with bounds adds max only for types that can be compared."],
   "Generics let one function work for numbers, chars and floats, while the bounds say exactly what the code needs. An impl block with its own bounds adds methods only for the types that support them, so Pair<String> still has swap but no max.")

ex("10.2", "Traits with default methods",
   "Write a trait Shape with a default method, and implement it for two types.\n\n"
   "Specification:\n- trait Shape has fn area(&self) -> f64, fn name(&self) -> String, and a default method describe(&self) -> String that returns \"NAME with area A\" with A rounded to 2 decimals, such as \"circle with area 3.14\".\n- Circle { radius: f64 } and Square { side: f64 } implement Shape (names \"circle\" and \"square\"); neither overrides describe.\n- total_area(shapes: &[&dyn Shape]) -> f64 adds up the areas.\n\n"
   "Examples:\n- Circle { radius: 1.0 }.describe() returns \"circle with area 3.14\"\n- Square { side: 2.0 }.describe() returns \"square with area 4.00\"\n\n"
   "Edge cases: total_area(&[]) is 0.0.",
   r'''use std::f64::consts::PI;

pub trait Shape {
    fn area(&self) -> f64;
    fn name(&self) -> String;
    fn describe(&self) -> String {
        todo!()
    }
}

pub struct Circle {
    pub radius: f64,
}

pub struct Square {
    pub side: f64,
}

impl Shape for Circle {
    fn area(&self) -> f64 {
        todo!()
    }

    fn name(&self) -> String {
        todo!()
    }
}

impl Shape for Square {
    fn area(&self) -> f64 {
        todo!()
    }

    fn name(&self) -> String {
        todo!()
    }
}

pub fn total_area(shapes: &[&dyn Shape]) -> f64 {
    todo!()
}
''',
   r'''use std::f64::consts::PI;

pub trait Shape {
    fn area(&self) -> f64;
    fn name(&self) -> String;
    fn describe(&self) -> String {
        format!("{} with area {:.2}", self.name(), self.area())
    }
}

pub struct Circle {
    pub radius: f64,
}

pub struct Square {
    pub side: f64,
}

impl Shape for Circle {
    fn area(&self) -> f64 {
        PI * self.radius * self.radius
    }

    fn name(&self) -> String {
        String::from("circle")
    }
}

impl Shape for Square {
    fn area(&self) -> f64 {
        self.side * self.side
    }

    fn name(&self) -> String {
        String::from("square")
    }
}

pub fn total_area(shapes: &[&dyn Shape]) -> f64 {
    shapes.iter().map(|s| s.area()).sum()
}
''',
   [("Circle", 'assert_eq!(Circle { radius: 1.0 }.describe(), "circle with area 3.14");'),
    ("Square", 'assert_eq!(Square { side: 2.0 }.describe(), "square with area 4.00");'),
    ("Total area", 'let c = Circle { radius: 1.0 };\nlet s = Square { side: 3.0 };\nlet t = total_area(&[&c, &s]);\nassert!((t - (std::f64::consts::PI + 9.0)).abs() < 1e-9, "total_area gave {t}");\nassert_eq!(total_area(&[]), 0.0);')],
   [('"{} with area {:.2}"', '"{} with area {}"'), ("PI * self.radius * self.radius", "2.0 * PI * self.radius")],
   ["A default method has a body in the trait and can call the trait's other methods.", "{:.2} formats a float with two decimals.", "Each impl Shape for ... block only needs area and name."],
   "The default describe is written once, and every shape gets it for free just by implementing the two required methods. &dyn Shape lets total_area accept a mix of different shapes in one slice.")

ex("10.3", "Lifetimes that borrow from the input",
   "Write longest_line(text) and a small word splitter that both return slices of their input.\n\n"
   "Specification:\n- longest_line<'a>(text: &'a str, default: &'a str) -> &'a str returns the longest line (first on ties), or default when text has no non-empty line. Both inputs share the lifetime 'a.\n- pub struct Words<'a> { rest: &'a str } with Words::new(text) and next_word(&mut self) -> Option<&'a str> that returns the next whitespace-separated word, or None at the end.\n\n"
   "Examples:\n- longest_line(\"tea\\nbiscuits\\njam\", \"-\") returns \"biscuits\"\n- Words::new(\"  a bb  ccc \") gives \"a\", \"bb\", \"ccc\", then None\n\n"
   "Edge cases: the returned words must stay usable after the Words value is dropped (they borrow the text, not the splitter).",
   r'''pub fn longest_line<'a>(text: &'a str, default: &'a str) -> &'a str {
    todo!()
}

pub struct Words<'a> {
    rest: &'a str,
}

impl<'a> Words<'a> {
    pub fn new(text: &'a str) -> Self {
        todo!()
    }

    pub fn next_word(&mut self) -> Option<&'a str> {
        todo!()
    }
}
''',
   r'''pub fn longest_line<'a>(text: &'a str, default: &'a str) -> &'a str {
    let mut best = "";
    for line in text.lines() {
        if line.len() > best.len() {
            best = line;
        }
    }
    if best.is_empty() { default } else { best }
}

pub struct Words<'a> {
    rest: &'a str,
}

impl<'a> Words<'a> {
    pub fn new(text: &'a str) -> Self {
        Words { rest: text }
    }

    pub fn next_word(&mut self) -> Option<&'a str> {
        let trimmed = self.rest.trim_start();
        if trimmed.is_empty() {
            self.rest = trimmed;
            return None;
        }
        let end = trimmed.find(char::is_whitespace).unwrap_or(trimmed.len());
        let (word, rest) = trimmed.split_at(end);
        self.rest = rest;
        Some(word)
    }
}
''',
   [("Longest line", 'assert_eq!(longest_line("tea\\nbiscuits\\njam", "-"), "biscuits");\nassert_eq!(longest_line("ab\\ncd", "-"), "ab");\nassert_eq!(longest_line("", "none"), "none");\nassert_eq!(longest_line("\\n\\n", "none"), "none");'),
    ("Words", 'let mut w = Words::new("  a bb  ccc ");\nassert_eq!(w.next_word(), Some("a"));\nassert_eq!(w.next_word(), Some("bb"));\nassert_eq!(w.next_word(), Some("ccc"));\nassert_eq!(w.next_word(), None);\nassert_eq!(w.next_word(), None);'),
    ("Words outlive the splitter", 'let text = String::from("one two");\nlet first;\n{\n    let mut w = Words::new(&text);\n    first = w.next_word();\n}\nassert_eq!(first, Some("one"));')],
   [("if line.len() > best.len() {", "if line.len() >= best.len() {"), ("let (word, rest) = trimmed.split_at(end);\n        self.rest = rest;", "let (word, _) = trimmed.split_at(end);\n        self.rest = &trimmed[1..];")],
   ["The 'a on both inputs and the output says: the result points into one of them.", "In next_word, return Option<&'a str>, not Option<&str>, so the word borrows the text rather than &mut self.", "trim_start, find(char::is_whitespace) and split_at do the cutting."],
   "Lifetimes describe which input a returned reference comes from; with two reference inputs the compiler can't guess, so you write 'a. Tying next_word's result to 'a (the text) instead of to &mut self is what lets the words outlive the splitter, which the last test checks; with the elided lifetime it wouldn't compile.")

ex("10.4", "A summary of anything printable",
   "Write summarise(items, max) that lists up to max items and says how many more there are.\n\n"
   "Specification:\n- items: &[T] where T: Display.\n- List the first max items joined with \", \".\n- If there are more, add \" and N more\".\n- With no items, return \"nothing\".\n\n"
   "Examples:\n- summarise(&[\"tea\", \"jam\", \"cake\", \"scones\"], 2) returns \"tea, jam and 2 more\"\n- summarise(&[1, 2], 5) returns \"1, 2\"\n\n"
   "Edge cases: with max = 0 and three items the result is \"3 more\".",
   r'''use std::fmt::Display;

pub fn summarise<T: Display>(items: &[T], max: usize) -> String {
    todo!()
}
''',
   r'''use std::fmt::Display;

pub fn summarise<T: Display>(items: &[T], max: usize) -> String {
    if items.is_empty() {
        return String::from("nothing");
    }
    let shown: Vec<String> = items.iter().take(max).map(|i| i.to_string()).collect();
    let hidden = items.len() - shown.len();
    match (shown.is_empty(), hidden) {
        (true, n) => format!("{n} more"),
        (false, 0) => shown.join(", "),
        (false, n) => format!("{} and {n} more", shown.join(", ")),
    }
}
''',
   [("Some hidden", 'assert_eq!(summarise(&["tea", "jam", "cake", "scones"], 2), "tea, jam and 2 more");'),
    ("All shown", 'assert_eq!(summarise(&[1, 2], 5), "1, 2");\nassert_eq!(summarise(&[1, 2], 2), "1, 2");'),
    ("Nothing and zero", 'let none: [i32; 0] = [];\nassert_eq!(summarise(&none, 3), "nothing");\nassert_eq!(summarise(&[1.5, 2.5, 3.5], 0), "3 more");')],
   [("let hidden = items.len() - shown.len();", "let hidden = items.len().saturating_sub(max + 1);"), ('(false, 0) => shown.join(", "),', '(false, 0) => shown.join(","),')],
   ["T: Display lets you call to_string() on every item.", "take(max) never goes past the end of the slice.", "Matching on (shown.is_empty(), hidden) covers the three shapes of the answer."],
   "One generic function now summarises strings, numbers and your own types, as long as they implement Display. Matching on a tuple makes each output format a separate, readable arm.")

# ---------------------------------------------------------------- chapter 11
LEAP = r'''#[allow(clippy::manual_is_multiple_of)]
pub fn is_leap_year(year: u32) -> bool {
    (year % 4 == 0 && year % 100 != 0) || year % 400 == 0
}
'''
mut_ex("11.1", "Tests that catch bugs (leap years)",
   "This time you write the tests. The grader runs them against the correct is_leap_year and against four versions with a planted bug. Your tests must pass on the correct code and fail on every buggy one.\n\n"
   "Specification of is_leap_year(year: u32) -> bool:\n- A year divisible by 4 is a leap year,\n- except a year divisible by 100, which is not,\n- except a year divisible by 400, which is.\n\n"
   "What to write:\n- A #[cfg(test)] mod tests block with use super::*; and #[test] functions.\n- Don't write is_leap_year itself: the grader supplies it.\n\n"
   "Examples: 2024 is a leap year, 2023 is not, 1900 is not, 2000 is.",
   LEAP,
   [("ignores the 100-year rule", "pub fn is_leap_year(year: u32) -> bool {\n    year % 4 == 0\n}\n"),
    ("ignores the 400-year rule", "pub fn is_leap_year(year: u32) -> bool {\n    year % 4 == 0 && year % 100 != 0\n}\n"),
    ("treats every 100th year as a leap year", "pub fn is_leap_year(year: u32) -> bool {\n    year % 4 == 0 || year % 100 == 0\n}\n"),
    ("says every year is a leap year", "pub fn is_leap_year(_year: u32) -> bool {\n    true\n}\n")],
   r'''#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ordinary_leap_year() {
        // assert!(is_leap_year(2024));
    }
}
''',
   r'''#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn divisible_by_four_is_leap() {
        assert!(is_leap_year(2024));
    }

    #[test]
    fn not_divisible_by_four_is_common() {
        assert!(!is_leap_year(2023));
    }

    #[test]
    fn century_is_common() {
        assert!(!is_leap_year(1900));
    }

    #[test]
    fn every_400_years_is_leap() {
        assert!(is_leap_year(2000));
    }
}
''',
   [r'''#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn leap() {
        assert!(is_leap_year(2024));
        assert!(!is_leap_year(2023));
    }
}
''', r'''#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn leap() {
        assert!(is_leap_year(2024));
        assert!(!is_leap_year(1900));
    }
}
'''],
   ["Each rule in the specification needs a test with a year where that rule decides the answer.", "1900 is divisible by 4 and by 100 but not by 400; 2000 is divisible by all three.", "Don't forget a plain common year, or code that always says true would pass."],
   "This is mutation testing in miniature: a test suite is only as good as the bugs it catches. Picking inputs where a correct and a plausibly wrong version disagree (1900, 2000) is the skill; checking only 2024 and 2023 leaves two of the four bugs alive.")

ex("11.2", "Results in tests and precise panics",
   "Write parse_port(text) and clamp_volume(v), then make sure your own tests cover them (the grader adds its own).\n\n"
   "Specification:\n- parse_port(text: &str) -> Result<u16, String> accepts a whole number from 1 to 65535, with spaces around it allowed. Errors: \"not a number: TEXT\" (TEXT trimmed) or \"port out of range: N\" for 0 or more than 65535.\n- clamp_volume(v: i32) -> u8 returns v limited to 0..=100, but panics with \"volume must not be negative\" if v is below 0, because a negative volume means a bug in the caller.\n\n"
   "Examples:\n- parse_port(\" 8080 \") returns Ok(8080)\n- parse_port(\"99999\") returns Err(\"port out of range: 99999\")\n- clamp_volume(150) returns 100\n\n"
   "Tip: tests can return Result<(), String> so you can use ? inside them.",
   r'''pub fn parse_port(text: &str) -> Result<u16, String> {
    todo!()
}

pub fn clamp_volume(v: i32) -> u8 {
    todo!()
}
''',
   r'''pub fn parse_port(text: &str) -> Result<u16, String> {
    let text = text.trim();
    let n: u64 = text.parse().map_err(|_| format!("not a number: {text}"))?;
    if n == 0 || n > 65535 {
        return Err(format!("port out of range: {n}"));
    }
    Ok(n as u16)
}

pub fn clamp_volume(v: i32) -> u8 {
    assert!(v >= 0, "volume must not be negative");
    v.min(100) as u8
}
''',
   [("Valid ports", 'fn check() -> Result<(), String> {\n    assert_eq!(parse_port(" 8080 ")?, 8080);\n    assert_eq!(parse_port("1")?, 1);\n    assert_eq!(parse_port("65535")?, 65535);\n    Ok(())\n}\ncheck().unwrap();'),
    ("Not a number", 'assert_eq!(parse_port(" http "), Err("not a number: http".to_string()));'),
    ("Out of range", 'assert_eq!(parse_port("99999"), Err("port out of range: 99999".to_string()));\nassert_eq!(parse_port("0"), Err("port out of range: 0".to_string()));'),
    ("Clamping", 'assert_eq!(clamp_volume(150), 100);\nassert_eq!(clamp_volume(42), 42);\nassert_eq!(clamp_volume(0), 0);'),
    ("Negative volume panics", 'clamp_volume(-1);', '#[should_panic(expected = "volume must not be negative")]')],
   [("let n: u64 = text.parse()", "let n: u16 = text.parse()"), ('assert!(v >= 0, "volume must not be negative");', 'let v = v.max(0);')],
   ["Parse into a wider type such as u64 so 99999 gives your range error instead of a parse error.", "assert!(v >= 0, \"...\") panics with that message.", "v.min(100) as u8 is safe once v is between 0 and 100."],
   "Parsing into u16 directly would report 99999 as \"not a number\", a misleading message; parsing wider and checking the range keeps the two errors distinct. Tests that return Result can use ?, and #[should_panic(expected = ...)] makes sure it panics for the right reason.")

ex("11.3", "A CSV line parser, tested from the outside",
   "Write parse_csv_line(line) that splits one line of comma-separated values, handling quoted fields.\n\n"
   "Specification:\n- Fields are separated by commas.\n- A field in double quotes may contain commas; the quotes are removed.\n- Inside quotes, two double quotes (\"\") stand for one \" character.\n- Return Vec<String>.\n\n"
   "Examples:\n- parse_csv_line(\"a,b,c\") returns [\"a\", \"b\", \"c\"]\n- parse_csv_line(\"tea,\\\"1,50\\\",jam\") returns [\"tea\", \"1,50\", \"jam\"]\n- parse_csv_line(\"\\\"say \\\"\\\"hi\\\"\\\"\\\"\") returns [\"say \\\"hi\\\"\"]\n\n"
   "Edge cases: \"\" returns [\"\"]; \"a,\" returns [\"a\", \"\"].",
   r'''pub fn parse_csv_line(line: &str) -> Vec<String> {
    todo!()
}
''',
   r'''pub fn parse_csv_line(line: &str) -> Vec<String> {
    let mut fields = Vec::new();
    let mut field = String::new();
    let mut in_quotes = false;
    let mut chars = line.chars().peekable();
    while let Some(c) = chars.next() {
        match (c, in_quotes) {
            ('"', true) if chars.peek() == Some(&'"') => {
                field.push('"');
                chars.next();
            }
            ('"', _) => in_quotes = !in_quotes,
            (',', false) => fields.push(std::mem::take(&mut field)),
            _ => field.push(c),
        }
    }
    fields.push(field);
    fields
}
''',
   [("Plain fields", 'assert_eq!(parse_csv_line("a,b,c"), vec!["a", "b", "c"]);'),
    ("Quoted comma", 'assert_eq!(parse_csv_line("tea,\\"1,50\\",jam"), vec!["tea", "1,50", "jam"]);'),
    ("Escaped quotes", 'assert_eq!(parse_csv_line("\\"say \\"\\"hi\\"\\"\\""), vec!["say \\"hi\\""]);'),
    ("Empty fields", 'assert_eq!(parse_csv_line(""), vec![""]);\nassert_eq!(parse_csv_line("a,"), vec!["a", ""]);\nassert_eq!(parse_csv_line(",,"), vec!["", "", ""]);')],
   [("(',', false) =>", "(',', _) =>"), ("    fields.push(field);\n    fields\n", "    if !field.is_empty() {\n        fields.push(field);\n    }\n    fields\n")],
   ["Walk through the characters, remembering whether you are inside quotes.", "peekable() lets you look at the next character to spot \"\".", "std::mem::take(&mut field) hands over the finished field and leaves an empty String."],
   "A tiny state machine (inside quotes or not) handles every case, and each test pins down one rule. In a Cargo project these tests could live in tests/csv.rs as integration tests, since they only use the public function.")
