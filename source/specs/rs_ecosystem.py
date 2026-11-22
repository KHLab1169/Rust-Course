"""Autograded exercises for module A14, The wider ecosystem (roadmap.sh topics the other modules only mention)."""
from rspec import ex

ex("A14.1", "Compare secrets in constant time",
   "Write the two small helpers every crypto-adjacent codebase has: hex encoding for digests, and a comparison that doesn't leak timing.\n\n"
   "Specification:\n- to_hex(bytes: &[u8]) -> String returns lower-case hex, two characters per byte.\n- from_hex(text: &str) -> Option<Vec<u8>> parses hex (upper or lower case); None for an odd length or a non-hex character.\n- constant_time_eq(a: &[u8], b: &[u8]) -> bool returns whether the slices are equal. If the lengths differ return false; otherwise look at every byte, combining the differences with | (OR) and ^ (XOR), and never return early.\n\n"
   "Examples:\n- to_hex(&[0, 15, 255]) returns \"000fff\"\n- from_hex(\"DEADbeef\") returns Some(vec![0xde, 0xad, 0xbe, 0xef])\n- constant_time_eq(b\"token\", b\"token\") is true\n\n"
   "Edge cases: from_hex(\"abc\") and from_hex(\"zz\") are None; two empty slices are equal.",
   r'''pub fn to_hex(bytes: &[u8]) -> String {
    todo!()
}

pub fn from_hex(text: &str) -> Option<Vec<u8>> {
    todo!()
}

pub fn constant_time_eq(a: &[u8], b: &[u8]) -> bool {
    todo!()
}
''',
   r'''pub fn to_hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}

pub fn from_hex(text: &str) -> Option<Vec<u8>> {
    if !text.len().is_multiple_of(2) || !text.is_ascii() {
        return None;
    }
    (0..text.len()).step_by(2).map(|i| u8::from_str_radix(&text[i..i + 2], 16).ok()).collect()
}

pub fn constant_time_eq(a: &[u8], b: &[u8]) -> bool {
    if a.len() != b.len() {
        return false;
    }
    let mut diff = 0u8;
    for (x, y) in a.iter().zip(b) {
        diff |= x ^ y;
    }
    diff == 0
}
''',
   [("Hex encoding", 'assert_eq!(to_hex(&[0, 15, 255]), "000fff");\nassert_eq!(to_hex(&[]), "");'),
    ("Hex decoding", 'assert_eq!(from_hex("DEADbeef"), Some(vec![0xde, 0xad, 0xbe, 0xef]));\nassert_eq!(from_hex(&to_hex(&[1, 2, 250])), Some(vec![1, 2, 250]), "round trip");'),
    ("Bad hex", 'assert_eq!(from_hex("abc"), None, "odd length");\nassert_eq!(from_hex("zz"), None);\nassert_eq!(from_hex("é1"), None);'),
    ("Constant-time equality", 'assert!(constant_time_eq(b"token", b"token"));\nassert!(!constant_time_eq(b"token", b"tokem"));\nassert!(!constant_time_eq(b"token", b"tok"));\nassert!(constant_time_eq(b"", b""));'),
    ("Looks at every byte", 'let src = include_str!("exercise.rs");\nlet body = src.split("pub fn constant_time_eq").nth(1).unwrap_or("").split("mod grader_tests").next().unwrap_or("");\nassert!(body.contains(\'^\') && body.contains(\'|\'), "Combine the byte differences with ^ and |");\nassert!(!body.contains("== b[") && !body.contains("a == b"), "Don\'t compare the slices with ==: it can stop at the first difference");')],
   [("diff |= x ^ y;", "diff = x ^ y;"), ("format!(\"{b:02x}\")", "format!(\"{b:x}\")")],
   ["format!(\"{b:02x}\") prints one byte as two hex digits.", "u8::from_str_radix(pair, 16) parses two hex digits; collecting Option values gives None if any pair fails.", "XOR is 0 only for equal bytes; OR-ing every XOR into one accumulator means the loop always runs to the end."],
   "Comparing a secret (an API token, an HMAC tag) with == can stop at the first different byte, so an attacker timing many requests can learn the secret byte by byte. Crates like subtle and ring's constant_time module do this properly; the point here is to recognise the pattern and never write the early-exit version.",
   eid="A14.1a")

ex("A14.3", "Strip terminal colours from test output",
   "CLI tools built with termion, crossterm or clap colour their output with ANSI escape codes, which break log parsers and snapshot tests. Write strip_ansi(text) and visible_width(text).\n\n"
   "Specification:\n- An escape sequence starts with the ESC character ('\\x1b') followed by '['; it continues with digits and ';' and ends with one letter (such as m for colours or K for clear line). Remove whole sequences.\n- Any other character, including a lone ESC not followed by '[', is kept.\n- visible_width returns the number of characters left after stripping.\n\n"
   "Examples:\n- strip_ansi(\"\\x1b[32mok\\x1b[0m\") returns \"ok\"\n- strip_ansi(\"\\x1b[1;31mFAILED\\x1b[0m test\") returns \"FAILED test\"\n- visible_width(\"\\x1b[33mwarn\\x1b[0m\") is 4\n\n"
   "Edge cases: text without escapes is unchanged; accented characters count as one each.",
   r'''pub fn strip_ansi(text: &str) -> String {
    todo!()
}

pub fn visible_width(text: &str) -> usize {
    todo!()
}
''',
   r'''pub fn strip_ansi(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    let mut chars = text.chars().peekable();
    while let Some(c) = chars.next() {
        if c == '\x1b' && chars.peek() == Some(&'[') {
            chars.next();
            for d in chars.by_ref() {
                if d.is_ascii_alphabetic() {
                    break;
                }
            }
        } else {
            out.push(c);
        }
    }
    out
}

pub fn visible_width(text: &str) -> usize {
    strip_ansi(text).chars().count()
}
''',
   [("Colours", 'assert_eq!(strip_ansi("\\x1b[32mok\\x1b[0m"), "ok");\nassert_eq!(strip_ansi("\\x1b[1;31mFAILED\\x1b[0m test"), "FAILED test");'),
    ("Other sequences", 'assert_eq!(strip_ansi("50%\\x1b[K done"), "50% done", "clear-line code");\nassert_eq!(strip_ansi("plain text"), "plain text");'),
    ("Lone escape kept", 'assert_eq!(strip_ansi("a\\x1bb"), "a\\x1bb");'),
    ("Visible width", 'assert_eq!(visible_width("\\x1b[33mwarn\\x1b[0m"), 4);\nassert_eq!(visible_width("\\x1b[1mcafé\\x1b[0m"), 4, "é is one character");')],
   [("if c == '\\x1b' && chars.peek() == Some(&'[') {", "if c == '\\x1b' {"), ("strip_ansi(text).chars().count()", "strip_ansi(text).len()")],
   ["Walk the characters with a peekable iterator so you can check the one after ESC.", "Inside a sequence, skip characters until the first ASCII letter, and skip that too.", "Count characters with chars().count(), not bytes."],
   "Stripping colour codes is a standard step before comparing CLI output in tests, or before writing it to a log file. Tools like clap and termcolor turn colour off when output isn't a terminal, but a test that captures a pseudo-terminal still sees the codes.",
   eid="A14.3a")

ex("A14.6", "A tiny entity-component system",
   "Bevy organises a game as entities (IDs), components (plain data) and systems (functions over components). Write the core of one with no engine at all.\n\n"
   "Specification:\n- World has public Vecs positions: Vec<Option<(f32, f32)>>, velocities: Vec<Option<(f32, f32)>> and healths: Vec<Option<i32>>, one slot per entity, and next_id.\n- spawn(&mut self) returns a new entity id (usize) and pushes None into every component Vec.\n- movement_system(&mut self, dt: f32) adds velocity * dt to the position of every entity that has both.\n- damage_system(&mut self, amount: i32) -> Vec<usize> subtracts amount from every entity with health and returns the ids whose health dropped to 0 or below, in id order; those entities lose all their components.\n\n"
   "Examples:\n- an entity at (0, 0) with velocity (2, 1), after movement_system(0.5), is at (1, 0.5)\n\n"
   "Edge cases: an entity with a position but no velocity doesn't move.",
   r'''#[derive(Default)]
pub struct World {
    pub positions: Vec<Option<(f32, f32)>>,
    pub velocities: Vec<Option<(f32, f32)>>,
    pub healths: Vec<Option<i32>>,
    pub next_id: usize,
}

impl World {
    pub fn spawn(&mut self) -> usize {
        todo!()
    }

    pub fn movement_system(&mut self, dt: f32) {
        todo!()
    }

    pub fn damage_system(&mut self, amount: i32) -> Vec<usize> {
        todo!()
    }
}
''',
   r'''#[derive(Default)]
pub struct World {
    pub positions: Vec<Option<(f32, f32)>>,
    pub velocities: Vec<Option<(f32, f32)>>,
    pub healths: Vec<Option<i32>>,
    pub next_id: usize,
}

impl World {
    pub fn spawn(&mut self) -> usize {
        let id = self.next_id;
        self.next_id += 1;
        self.positions.push(None);
        self.velocities.push(None);
        self.healths.push(None);
        id
    }

    pub fn movement_system(&mut self, dt: f32) {
        for (pos, vel) in self.positions.iter_mut().zip(&self.velocities) {
            if let (Some((x, y)), Some((vx, vy))) = (pos.as_mut(), vel) {
                *x += vx * dt;
                *y += vy * dt;
            }
        }
    }

    pub fn damage_system(&mut self, amount: i32) -> Vec<usize> {
        let mut dead = Vec::new();
        for (id, health) in self.healths.iter_mut().enumerate() {
            if let Some(h) = health {
                *h -= amount;
                if *h <= 0 {
                    dead.push(id);
                }
            }
        }
        for &id in &dead {
            self.positions[id] = None;
            self.velocities[id] = None;
            self.healths[id] = None;
        }
        dead
    }
}
''',
   [("Spawn gives new ids", 'let mut w = World::default();\nassert_eq!((w.spawn(), w.spawn()), (0, 1));\nassert_eq!(w.positions.len(), 2);'),
    ("Movement", 'let mut w = World::default();\nlet a = w.spawn();\nw.positions[a] = Some((0.0, 0.0));\nw.velocities[a] = Some((2.0, 1.0));\nlet b = w.spawn();\nw.positions[b] = Some((5.0, 5.0));\nw.movement_system(0.5);\nassert_eq!(w.positions[a], Some((1.0, 0.5)));\nassert_eq!(w.positions[b], Some((5.0, 5.0)), "no velocity, no movement");'),
    ("Damage", 'let mut w = World::default();\nlet a = w.spawn();\nlet b = w.spawn();\nlet c = w.spawn();\nw.healths[a] = Some(10);\nw.healths[b] = Some(3);\nw.healths[c] = Some(3);\nw.positions[c] = Some((1.0, 1.0));\nassert_eq!(w.damage_system(3), vec![b, c]);\nassert_eq!(w.healths[a], Some(7));\nassert_eq!(w.positions[c], None, "dead entities lose their components");\nassert_eq!(w.damage_system(3), Vec::<usize>::new());')],
   [("                *y += vy * dt;\n", ""), ("                if *h <= 0 {", "                if *h < 0 {")],
   ["Every component Vec has one slot per entity, so the id is just an index.", "zip positions with velocities and update only where both are Some.", "Collect the dead ids first, then clear their slots in a second loop."],
   "Keeping data in plain arrays and logic in systems is what makes ECS engines like Bevy fast and easy to parallelise: a system touches only the components it needs. It also makes game logic testable without a window or a GPU, as these tests show.",
   eid="A14.6a")

ex("A14.7", "A driver tested against a mock pin",
   "Embedded Rust drivers are written against traits (embedded-hal's OutputPin, for example), so the same code runs on an nRF board, a Raspberry Pi with rppal, or a test double. Write a blinker driver and test it with a mock.\n\n"
   "Specification:\n- trait OutputPin { fn set_high(&mut self); fn set_low(&mut self); } is given (a simplified embedded-hal).\n- MockPin records calls in a public log: Vec<&'static str> (\"high\" or \"low\").\n- Blinker<P: OutputPin> owns a pin and a lit: bool. Blinker::new(pin) sets the pin low. toggle(&mut self) switches the pin and lit. blink(&mut self, times) toggles 2 * times, ending where it started.\n- release(self) -> P gives the pin back so the test can read its log.\n\n"
   "Examples:\n- Blinker::new(MockPin::default()) then blink(2) leaves the log low, high, low, high, low\n\n"
   "Edge cases: blink(0) changes nothing after new.",
   r'''pub trait OutputPin {
    fn set_high(&mut self);
    fn set_low(&mut self);
}

#[derive(Default)]
pub struct MockPin {
    pub log: Vec<&'static str>,
}

impl OutputPin for MockPin {
    fn set_high(&mut self) {
        todo!()
    }

    fn set_low(&mut self) {
        todo!()
    }
}

pub struct Blinker<P: OutputPin> {
    pin: P,
    lit: bool,
}

impl<P: OutputPin> Blinker<P> {
    pub fn new(pin: P) -> Self {
        todo!()
    }

    pub fn toggle(&mut self) {
        todo!()
    }

    pub fn blink(&mut self, times: u32) {
        todo!()
    }

    pub fn is_lit(&self) -> bool {
        todo!()
    }

    pub fn release(self) -> P {
        todo!()
    }
}
''',
   r'''pub trait OutputPin {
    fn set_high(&mut self);
    fn set_low(&mut self);
}

#[derive(Default)]
pub struct MockPin {
    pub log: Vec<&'static str>,
}

impl OutputPin for MockPin {
    fn set_high(&mut self) {
        self.log.push("high");
    }

    fn set_low(&mut self) {
        self.log.push("low");
    }
}

pub struct Blinker<P: OutputPin> {
    pin: P,
    lit: bool,
}

impl<P: OutputPin> Blinker<P> {
    pub fn new(mut pin: P) -> Self {
        pin.set_low();
        Blinker { pin, lit: false }
    }

    pub fn toggle(&mut self) {
        if self.lit {
            self.pin.set_low();
        } else {
            self.pin.set_high();
        }
        self.lit = !self.lit;
    }

    pub fn blink(&mut self, times: u32) {
        for _ in 0..times * 2 {
            self.toggle();
        }
    }

    pub fn is_lit(&self) -> bool {
        self.lit
    }

    pub fn release(self) -> P {
        self.pin
    }
}
''',
   [("Starts low", 'let b = Blinker::new(MockPin::default());\nassert!(!b.is_lit());\nassert_eq!(b.release().log, vec!["low"]);'),
    ("Toggle", 'let mut b = Blinker::new(MockPin::default());\nb.toggle();\nassert!(b.is_lit());\nb.toggle();\nassert_eq!(b.release().log, vec!["low", "high", "low"]);'),
    ("Blink", 'let mut b = Blinker::new(MockPin::default());\nb.blink(2);\nassert!(!b.is_lit(), "blink ends where it started");\nassert_eq!(b.release().log, vec!["low", "high", "low", "high", "low"]);\nlet mut z = Blinker::new(MockPin::default());\nz.blink(0);\nassert_eq!(z.release().log, vec!["low"]);')],
   [("        for _ in 0..times * 2 {", "        for _ in 0..times {"), ("        pin.set_low();\n", "")],
   ["Blinker is generic over P: OutputPin, so it never knows whether the pin is real.", "new needs mut pin to call set_low before storing it.", "release(self) moves the pin out, ending the Blinker."],
   "Programming against embedded-hal traits is what lets one driver crate support hundreds of chips, and it is also what makes drivers testable on your laptop: the mock records exactly what the hardware would have seen. embedded-hal-mock offers ready-made mocks for real projects.",
   eid="A14.7a")
