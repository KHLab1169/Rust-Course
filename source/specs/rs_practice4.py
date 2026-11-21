"""Practice sets, Track 1 chapters 17 to 21."""
from rspec import ex, ASYNC_PRELUDE

ASYNC_NOTE = ("\n\nThe tests run your futures with a tiny block_on executor (no Tokio needed), so you can test async code "
              "with nothing but the standard library.")

# ---------------------------------------------------------------- chapter 17
ex("17.1", "Async functions that await each other",
   "Write two async functions: price_with_tax(cents) and basket_total(prices).\n\n"
   "Specification:\n- async fn price_with_tax(cents: u64) -> u64 returns cents plus 15% tax, rounded down.\n- async fn basket_total(prices: Vec<u64>) -> u64 awaits price_with_tax for each price in turn and adds the results.\n- async fn first_over(prices: Vec<u64>, limit: u64) -> Option<u64> returns the first price whose taxed price is above limit.\n\n"
   "Examples:\n- price_with_tax(1000).await is 1150\n- basket_total(vec![1000, 200]).await is 1380\n\n"
   "Edge cases: an empty basket totals 0; calling an async fn without .await does nothing yet." + ASYNC_NOTE,
   r'''pub async fn price_with_tax(cents: u64) -> u64 {
    todo!()
}

pub async fn basket_total(prices: Vec<u64>) -> u64 {
    todo!()
}

pub async fn first_over(prices: Vec<u64>, limit: u64) -> Option<u64> {
    todo!()
}
''',
   r'''pub async fn price_with_tax(cents: u64) -> u64 {
    cents * 115 / 100
}

pub async fn basket_total(prices: Vec<u64>) -> u64 {
    let mut total = 0;
    for p in prices {
        total += price_with_tax(p).await;
    }
    total
}

pub async fn first_over(prices: Vec<u64>, limit: u64) -> Option<u64> {
    for p in prices {
        if price_with_tax(p).await > limit {
            return Some(p);
        }
    }
    None
}
''',
   [("Tax", 'assert_eq!(block_on(price_with_tax(1000)), 1150);\nassert_eq!(block_on(price_with_tax(99)), 113, "99 * 1.15 = 113.85, rounded down");'),
    ("Basket", 'assert_eq!(block_on(basket_total(vec![1000, 200])), 1380);\nassert_eq!(block_on(basket_total(vec![])), 0);'),
    ("First over the limit", 'assert_eq!(block_on(first_over(vec![100, 900, 2000], 1000)), Some(900), "900 with tax is 1035");\nassert_eq!(block_on(first_over(vec![1, 2], 1000)), None);'),
    ("Futures are lazy", 'let fut = basket_total(vec![1000]);\nlet _ = &fut;\nassert_eq!(block_on(fut), 1150);')],
   [("cents * 115 / 100", "cents * 115 / 100 + 1"), ("if price_with_tax(p).await > limit {", "if p > limit {")],
   ["An async fn returns a future; .await inside another async fn waits for it.", "Integer arithmetic cents * 115 / 100 rounds down.", "async fn bodies look like normal code: loops, early return and all."],
   "async fn turns a function into one that returns a future, and nothing runs until something polls it. Here block_on does the polling; in a real program Tokio or the book's trpl crate does, and many futures can wait at the same time.",
   prelude=ASYNC_PRELUDE)

ex("17.2", "Write a future by hand",
   "Implement the Future trait yourself for a countdown that is not ready until it has been polled n times.\n\n"
   "Specification:\n- Countdown { remaining: u32, polls: u32 } is given, with Countdown::new(n).\n- Each call to poll adds 1 to polls. If remaining is 0, return Poll::Ready(\"liftoff\"); otherwise subtract 1, call cx.waker().wake_by_ref() so the executor polls again, and return Poll::Pending.\n- polls(&self) returns how many times it was polled.\n\n"
   "Examples:\n- block_on(Countdown::new(3)) returns \"liftoff\" after 4 polls\n\n"
   "Edge cases: Countdown::new(0) is ready on the first poll." + ASYNC_NOTE,
   r'''use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll};

pub struct Countdown {
    pub remaining: u32,
    pub polls: u32,
}

impl Countdown {
    pub fn new(n: u32) -> Self {
        Countdown { remaining: n, polls: 0 }
    }
}

impl Future for Countdown {
    type Output = &'static str;

    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<&'static str> {
        todo!()
    }
}
''',
   r'''use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll};

pub struct Countdown {
    pub remaining: u32,
    pub polls: u32,
}

impl Countdown {
    pub fn new(n: u32) -> Self {
        Countdown { remaining: n, polls: 0 }
    }
}

impl Future for Countdown {
    type Output = &'static str;

    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<&'static str> {
        self.polls += 1;
        if self.remaining == 0 {
            return Poll::Ready("liftoff");
        }
        self.remaining -= 1;
        cx.waker().wake_by_ref();
        Poll::Pending
    }
}
''',
   [("Ready eventually", 'assert_eq!(block_on(Countdown::new(3)), "liftoff");'),
    ("Counts polls", 'let mut c = std::pin::pin!(Countdown::new(3));\nlet mut cx = std::task::Context::from_waker(std::task::Waker::noop());\nlet mut results = Vec::new();\nloop {\n    match c.as_mut().poll(&mut cx) {\n        std::task::Poll::Ready(v) => { results.push(v); break; }\n        std::task::Poll::Pending => results.push("pending"),\n    }\n}\nassert_eq!(results, vec!["pending", "pending", "pending", "liftoff"]);\nassert_eq!(c.polls, 4);'),
    ("Zero", 'let mut c = std::pin::pin!(Countdown::new(0));\nlet mut cx = std::task::Context::from_waker(std::task::Waker::noop());\nassert_eq!(c.as_mut().poll(&mut cx), std::task::Poll::Ready("liftoff"));')],
   [("        self.polls += 1;\n", ""), ("        if self.remaining == 0 {", "        if self.remaining <= 1 {")],
   ["poll receives self: Pin<&mut Self>; you can still change fields with self.polls += 1.", "Return Poll::Pending until remaining reaches 0.", "wake_by_ref tells the executor this future wants to be polled again."],
   "This is what every async fn compiles into: a state machine with a poll method. Returning Pending without arranging a wake-up would leave a real executor waiting forever, which is why the waker call matters even though the test executor polls in a loop.",
   prelude=ASYNC_PRELUDE)

ex("17.3", "Many futures, fail fast",
   "Write try_all(tasks) that awaits a list of fallible futures in order and stops at the first error.\n\n"
   "Specification:\n- tasks: Vec<F> where F: Future<Output = Result<i32, String>>.\n- Await them one after another; collect the values into Ok(Vec<i32>).\n- On the first Err, return it straight away and don't await the remaining tasks.\n- Also write async fn checked_div(a: i32, b: i32) -> Result<i32, String> returning Err(\"divide by zero\") when b is 0.\n\n"
   "Examples:\n- try_all(vec![checked_div(6, 3), checked_div(9, 3)]) gives Ok(vec![2, 3])\n\n"
   "Edge cases: an empty list gives Ok(vec![])." + ASYNC_NOTE,
   r'''use std::future::Future;

pub async fn checked_div(a: i32, b: i32) -> Result<i32, String> {
    todo!()
}

pub async fn try_all<F>(tasks: Vec<F>) -> Result<Vec<i32>, String>
where
    F: Future<Output = Result<i32, String>>,
{
    todo!()
}
''',
   r'''use std::future::Future;

pub async fn checked_div(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        return Err(String::from("divide by zero"));
    }
    Ok(a / b)
}

pub async fn try_all<F>(tasks: Vec<F>) -> Result<Vec<i32>, String>
where
    F: Future<Output = Result<i32, String>>,
{
    let mut out = Vec::with_capacity(tasks.len());
    for task in tasks {
        out.push(task.await?);
    }
    Ok(out)
}
''',
   [("All succeed", 'assert_eq!(block_on(try_all(vec![checked_div(6, 3), checked_div(9, 3)])), Ok(vec![2, 3]));\nlet none: Vec<std::future::Ready<Result<i32, String>>> = Vec::new();\nassert_eq!(block_on(try_all(none)), Ok(vec![]));'),
    ("First error", 'assert_eq!(block_on(try_all(vec![checked_div(1, 1), checked_div(1, 0), checked_div(4, 2)])), Err("divide by zero".to_string()));'),
    ("Stops early", 'use std::cell::Cell;\nlet ran = Cell::new(0);\nlet task = |v: Result<i32, String>| { let ran = &ran; async move { ran.set(ran.get() + 1); v } };\nlet r = block_on(try_all(vec![task(Ok(1)), task(Err("bad".into())), task(Ok(3))]));\nassert_eq!(r, Err("bad".to_string()));\nassert_eq!(ran.get(), 2, "the task after the error must not run");')],
   [("        out.push(task.await?);\n", "        if let Ok(v) = task.await {\n            out.push(v);\n        }\n"), ("    if b == 0 {\n        return Err(String::from(\"divide by zero\"));\n    }\n    Ok(a / b)\n", "    Ok(a.checked_div(b).unwrap_or(0))\n")],
   ["Loop over the tasks and .await each one.", "? works on the awaited Result, ending try_all at the first Err.", "Futures that are never awaited never run, so stopping early really skips the rest."],
   "Awaiting in a loop is sequential: each future runs only after the one before finishes. To run them at the same time you'd use join_all or a JoinSet, which the lesson covers; this version is right when later steps depend on earlier ones succeeding.",
   prelude=ASYNC_PRELUDE)

ex("17.4", "An async trait and a fake for tests",
   "Write a trait with an async method, a fake implementation, and a function that uses any implementation.\n\n"
   "Specification:\n- trait Fetcher { async fn fetch(&self, id: u32) -> Result<String, String>; } is given (async fn in traits is stable Rust).\n- FakeFetcher holds pages: HashMap<u32, String>. fetch returns the page, or Err(\"not found: ID\").\n- async fn fetch_all<F: Fetcher>(f: &F, ids: &[u32]) -> (Vec<String>, Vec<String>) returns the pages that loaded and the error messages, each in order.\n\n"
   "Examples:\n- with pages 1 and 2, fetch_all(&fake, &[1, 3, 2]) gives ([page 1, page 2], [\"not found: 3\"])\n\n"
   "Edge cases: no ids gives two empty Vecs." + ASYNC_NOTE,
   r'''use std::collections::HashMap;

#[allow(async_fn_in_trait)]
pub trait Fetcher {
    async fn fetch(&self, id: u32) -> Result<String, String>;
}

pub struct FakeFetcher {
    pub pages: HashMap<u32, String>,
}

impl Fetcher for FakeFetcher {
    async fn fetch(&self, id: u32) -> Result<String, String> {
        todo!()
    }
}

pub async fn fetch_all<F: Fetcher>(f: &F, ids: &[u32]) -> (Vec<String>, Vec<String>) {
    todo!()
}
''',
   r'''use std::collections::HashMap;

#[allow(async_fn_in_trait)]
pub trait Fetcher {
    async fn fetch(&self, id: u32) -> Result<String, String>;
}

pub struct FakeFetcher {
    pub pages: HashMap<u32, String>,
}

impl Fetcher for FakeFetcher {
    async fn fetch(&self, id: u32) -> Result<String, String> {
        self.pages.get(&id).cloned().ok_or_else(|| format!("not found: {id}"))
    }
}

pub async fn fetch_all<F: Fetcher>(f: &F, ids: &[u32]) -> (Vec<String>, Vec<String>) {
    let mut pages = Vec::new();
    let mut errors = Vec::new();
    for &id in ids {
        match f.fetch(id).await {
            Ok(p) => pages.push(p),
            Err(e) => errors.push(e),
        }
    }
    (pages, errors)
}
''',
   [("Fake fetcher", 'let fake = FakeFetcher { pages: HashMap::from([(1, "home".to_string())]) };\nassert_eq!(block_on(fake.fetch(1)), Ok("home".to_string()));\nassert_eq!(block_on(fake.fetch(9)), Err("not found: 9".to_string()));'),
    ("Pages and errors", 'let fake = FakeFetcher { pages: HashMap::from([(1, "p1".to_string()), (2, "p2".to_string())]) };\nassert_eq!(block_on(fetch_all(&fake, &[1, 3, 2])), (vec!["p1".to_string(), "p2".to_string()], vec!["not found: 3".to_string()]));'),
    ("Any Fetcher works", 'struct Always;\nimpl Fetcher for Always {\n    async fn fetch(&self, id: u32) -> Result<String, String> { Ok(format!("page {id}")) }\n}\nassert_eq!(block_on(fetch_all(&Always, &[])), (vec![], vec![]));\nassert_eq!(block_on(fetch_all(&Always, &[7])).0, vec!["page 7".to_string()]);')],
   [("            Err(e) => errors.push(e),\n", "            Err(_) => {}\n"), ('format!("not found: {id}")', 'String::from("not found")')],
   ["fetch can be written with ok_or_else on the HashMap lookup.", "fetch_all takes any F: Fetcher, so tests use the fake and the real program uses an HTTP client.", "match on each awaited Result and push to the right Vec."],
   "Hiding the network behind a trait is what makes async code testable: the fake answers instantly and predictably. The allow attribute silences a lint about Send bounds that only matters for libraries used with multi-threaded runtimes.",
   prelude=ASYNC_PRELUDE)

# ---------------------------------------------------------------- chapter 18
ex("18.1", "A bounded stack that keeps its promises",
   "Write BoundedStack, whose fields are private so its rules can't be broken from outside.\n\n"
   "Specification:\n- BoundedStack::new(capacity) creates an empty stack.\n- push(&mut self, value: i32) -> Result<(), i32> returns Err(value) (giving the value back) when full.\n- pop(&mut self) -> Option<i32>; peek(&self) -> Option<&i32>; len(&self) -> usize; is_empty(&self) -> bool.\n- average(&self) -> Option<f64> returns the mean of the values, kept up to date in a private running total so it never loops.\n\n"
   "Examples:\n- capacity 2: push 1, push 2, push 3 gives Err(3)\n\n"
   "Edge cases: average of an empty stack is None; pop updates the average.",
   r'''pub struct BoundedStack {
    items: Vec<i32>,
    capacity: usize,
    total: i64,
}

impl BoundedStack {
    pub fn new(capacity: usize) -> Self {
        todo!()
    }

    pub fn push(&mut self, value: i32) -> Result<(), i32> {
        todo!()
    }

    pub fn pop(&mut self) -> Option<i32> {
        todo!()
    }

    pub fn peek(&self) -> Option<&i32> {
        todo!()
    }

    pub fn len(&self) -> usize {
        todo!()
    }

    pub fn is_empty(&self) -> bool {
        todo!()
    }

    pub fn average(&self) -> Option<f64> {
        todo!()
    }
}
''',
   r'''pub struct BoundedStack {
    items: Vec<i32>,
    capacity: usize,
    total: i64,
}

impl BoundedStack {
    pub fn new(capacity: usize) -> Self {
        BoundedStack { items: Vec::with_capacity(capacity), capacity, total: 0 }
    }

    pub fn push(&mut self, value: i32) -> Result<(), i32> {
        if self.items.len() == self.capacity {
            return Err(value);
        }
        self.items.push(value);
        self.total += i64::from(value);
        Ok(())
    }

    pub fn pop(&mut self) -> Option<i32> {
        let v = self.items.pop()?;
        self.total -= i64::from(v);
        Some(v)
    }

    pub fn peek(&self) -> Option<&i32> {
        self.items.last()
    }

    pub fn len(&self) -> usize {
        self.items.len()
    }

    pub fn is_empty(&self) -> bool {
        self.items.is_empty()
    }

    pub fn average(&self) -> Option<f64> {
        if self.items.is_empty() {
            return None;
        }
        Some(self.total as f64 / self.items.len() as f64)
    }
}
''',
   [("Push, peek and pop", 'let mut s = BoundedStack::new(3);\nassert!(s.is_empty());\nassert_eq!(s.push(1), Ok(()));\nassert_eq!(s.push(2), Ok(()));\nassert_eq!(s.peek(), Some(&2));\nassert_eq!(s.pop(), Some(2));\nassert_eq!(s.len(), 1);'),
    ("Full stack gives the value back", 'let mut s = BoundedStack::new(2);\ns.push(1).unwrap();\ns.push(2).unwrap();\nassert_eq!(s.push(3), Err(3));\nassert_eq!(s.len(), 2);'),
    ("Average stays up to date", 'let mut s = BoundedStack::new(5);\nassert_eq!(s.average(), None);\nfor v in [2, 4, 9] { s.push(v).unwrap(); }\nassert_eq!(s.average(), Some(5.0));\ns.pop();\nassert_eq!(s.average(), Some(3.0), "after popping 9");\ns.pop();\ns.pop();\nassert_eq!(s.pop(), None);\nassert_eq!(s.average(), None);')],
   [("        self.total -= i64::from(v);\n", ""), ("if self.items.len() == self.capacity {", "if self.items.len() > self.capacity {")],
   ["Private fields mean only these methods can change items and total, so they always agree.", "Update total in both push and pop.", "pop can use ? on the Option from Vec::pop."],
   "Encapsulation in Rust is privacy at the module level rather than classes: outside code can only use the public methods, so the running total can never drift from the items. Returning Err(value) on a full stack gives ownership back instead of silently dropping the value.")

ex("18.2", "A canvas of trait objects",
   "Write a trait Draw and a Screen that holds different kinds of components in one Vec.\n\n"
   "Specification:\n- trait Draw { fn draw(&self) -> String; fn width(&self) -> usize; }\n- Button { label: String } draws as \"[label]\" and its width is the label length plus 2.\n- TextBox { text: String, size: usize } draws as the text padded with spaces (or cut) to exactly size characters, then \"|\"; its width is size + 1.\n- Screen { components: Vec<Box<dyn Draw>> } has render(&self) -> String (each draw on its own line, joined with \\n) and widest(&self) -> usize (0 when empty).\n\n"
   "Examples:\n- Button { label: \"OK\" }.draw() is \"[OK]\"\n- TextBox { text: \"hi\", size: 4 }.draw() is \"hi  |\"",
   r'''pub trait Draw {
    fn draw(&self) -> String;
    fn width(&self) -> usize;
}

pub struct Button {
    pub label: String,
}

pub struct TextBox {
    pub text: String,
    pub size: usize,
}

impl Draw for Button {
    fn draw(&self) -> String {
        todo!()
    }

    fn width(&self) -> usize {
        todo!()
    }
}

impl Draw for TextBox {
    fn draw(&self) -> String {
        todo!()
    }

    fn width(&self) -> usize {
        todo!()
    }
}

pub struct Screen {
    pub components: Vec<Box<dyn Draw>>,
}

impl Screen {
    pub fn render(&self) -> String {
        todo!()
    }

    pub fn widest(&self) -> usize {
        todo!()
    }
}
''',
   r'''pub trait Draw {
    fn draw(&self) -> String;
    fn width(&self) -> usize;
}

pub struct Button {
    pub label: String,
}

pub struct TextBox {
    pub text: String,
    pub size: usize,
}

impl Draw for Button {
    fn draw(&self) -> String {
        format!("[{}]", self.label)
    }

    fn width(&self) -> usize {
        self.label.chars().count() + 2
    }
}

impl Draw for TextBox {
    fn draw(&self) -> String {
        let cut: String = self.text.chars().take(self.size).collect();
        format!("{cut:<width$}|", width = self.size)
    }

    fn width(&self) -> usize {
        self.size + 1
    }
}

pub struct Screen {
    pub components: Vec<Box<dyn Draw>>,
}

impl Screen {
    pub fn render(&self) -> String {
        self.components.iter().map(|c| c.draw()).collect::<Vec<_>>().join("\n")
    }

    pub fn widest(&self) -> usize {
        self.components.iter().map(|c| c.width()).max().unwrap_or(0)
    }
}
''',
   [("Components", 'assert_eq!(Button { label: "OK".into() }.draw(), "[OK]");\nassert_eq!(TextBox { text: "hi".into(), size: 4 }.draw(), "hi  |");\nassert_eq!(TextBox { text: "toolong".into(), size: 3 }.draw(), "too|");'),
    ("Render a screen", 'let s = Screen { components: vec![Box::new(Button { label: "OK".into() }), Box::new(TextBox { text: "name".into(), size: 6 })] };\nassert_eq!(s.render(), "[OK]\\nname  |");'),
    ("Widest", 'let s = Screen { components: vec![Box::new(Button { label: "Cancel".into() }), Box::new(TextBox { text: "".into(), size: 3 })] };\nassert_eq!(s.widest(), 8);\nassert_eq!(Screen { components: vec![] }.widest(), 0);')],
   [('format!("{cut:<width$}|", width = self.size)', 'format!("{cut}|")'), ('.collect::<Vec<_>>().join("\\n")', '.collect::<Vec<_>>().concat()')],
   ["Box<dyn Draw> lets one Vec hold Buttons and TextBoxes together.", "{cut:<width$} pads text on the right to width characters.", "Calls on a trait object go through a vtable to the right type's method."],
   "Trait objects give run-time polymorphism: Screen doesn't know or care which types it holds, and new components can be added without touching it. The cost is a pointer and an indirect call, which is why generics are preferred when all items share one type.")

ex("18.3", "A door as a state machine",
   "Model a door with an enum of states, so impossible transitions are errors instead of bugs.\n\n"
   "Specification:\n- enum Door { Open, Closed, Locked { code: u32 } } derives Debug and PartialEq.\n- enum Action { Open, Close, Lock(u32), Unlock(u32) }.\n- Door::apply(self, action) -> Result<Door, String> allows: Closed + Open -> Open; Open + Close -> Closed; Closed + Lock(c) -> Locked with code c; Locked + Unlock(c) with the right code -> Closed.\n- A wrong code gives Err(\"wrong code\"); every other combination gives Err(\"cannot ACTION when STATE\") using lower-case names, such as \"cannot lock when open\".\n\n"
   "Examples:\n- Door::Closed.apply(Action::Lock(42)) is Ok(Door::Locked { code: 42 })",
   r'''#[derive(Debug, PartialEq)]
pub enum Door {
    Open,
    Closed,
    Locked { code: u32 },
}

pub enum Action {
    Open,
    Close,
    Lock(u32),
    Unlock(u32),
}

impl Door {
    pub fn apply(self, action: Action) -> Result<Door, String> {
        todo!()
    }
}
''',
   r'''#[derive(Debug, PartialEq)]
pub enum Door {
    Open,
    Closed,
    Locked { code: u32 },
}

pub enum Action {
    Open,
    Close,
    Lock(u32),
    Unlock(u32),
}

impl Door {
    pub fn apply(self, action: Action) -> Result<Door, String> {
        match (self, action) {
            (Door::Closed, Action::Open) => Ok(Door::Open),
            (Door::Open, Action::Close) => Ok(Door::Closed),
            (Door::Closed, Action::Lock(code)) => Ok(Door::Locked { code }),
            (Door::Locked { code }, Action::Unlock(given)) if given == code => Ok(Door::Closed),
            (Door::Locked { .. }, Action::Unlock(_)) => Err(String::from("wrong code")),
            (state, action) => {
                let a = match action {
                    Action::Open => "open",
                    Action::Close => "close",
                    Action::Lock(_) => "lock",
                    Action::Unlock(_) => "unlock",
                };
                let s = match state {
                    Door::Open => "open",
                    Door::Closed => "closed",
                    Door::Locked { .. } => "locked",
                };
                Err(format!("cannot {a} when {s}"))
            }
        }
    }
}
''',
   [("Open and close", 'assert_eq!(Door::Closed.apply(Action::Open), Ok(Door::Open));\nassert_eq!(Door::Open.apply(Action::Close), Ok(Door::Closed));'),
    ("Lock and unlock", 'let locked = Door::Closed.apply(Action::Lock(42)).unwrap();\nassert_eq!(locked, Door::Locked { code: 42 });\nassert_eq!(locked.apply(Action::Unlock(42)), Ok(Door::Closed));'),
    ("Wrong code", 'assert_eq!(Door::Locked { code: 42 }.apply(Action::Unlock(7)), Err("wrong code".to_string()));'),
    ("Impossible moves", 'assert_eq!(Door::Open.apply(Action::Lock(1)), Err("cannot lock when open".to_string()));\nassert_eq!(Door::Locked { code: 1 }.apply(Action::Open), Err("cannot open when locked".to_string()));\nassert_eq!(Door::Closed.apply(Action::Close), Err("cannot close when closed".to_string()));')],
   [("(Door::Locked { code }, Action::Unlock(given)) if given == code => Ok(Door::Closed),", "(Door::Locked { .. }, Action::Unlock(_)) if true => Ok(Door::Closed),"), ("(Door::Open, Action::Close) => Ok(Door::Closed),", "(Door::Open, Action::Close) => Ok(Door::Open),")],
   ["match on the pair (self, action) and list the allowed transitions first.", "A guard (if given == code) checks the unlock code.", "A final catch-all arm turns everything else into an error message."],
   "apply takes self by value, so after a transition the old state can't be used by mistake. This enum version is the alternative the book describes to trait-object states: all transitions are visible in one match, and the compiler checks every combination is handled.")

# ---------------------------------------------------------------- chapter 19
ex("19.1", "A stack calculator with while let",
   "Write eval_rpn(expr) that evaluates a Reverse Polish Notation expression such as \"3 4 + 2 *\".\n\n"
   "Specification:\n- Tokens are separated by spaces; numbers are i64; the operators are + - * /.\n- Push numbers on a stack; an operator pops two values (the second popped is the left operand) and pushes the result.\n- Return Some(result) if exactly one value is left, None for a malformed expression (not enough values, unknown token, leftovers, division by zero).\n- Use let-else or if let to pop the operands.\n\n"
   "Examples:\n- eval_rpn(\"3 4 + 2 *\") returns Some(14)\n- eval_rpn(\"10 2 -\") returns Some(8)\n\n"
   "Edge cases: \"\" returns None; \"1 +\" returns None; \"1 2\" returns None; \"4 0 /\" returns None.",
   r'''pub fn eval_rpn(expr: &str) -> Option<i64> {
    todo!()
}
''',
   r'''pub fn eval_rpn(expr: &str) -> Option<i64> {
    let mut stack: Vec<i64> = Vec::new();
    for token in expr.split_whitespace() {
        if let Ok(n) = token.parse() {
            stack.push(n);
            continue;
        }
        let (Some(b), Some(a)) = (stack.pop(), stack.pop()) else {
            return None;
        };
        let value = match token {
            "+" => a + b,
            "-" => a - b,
            "*" => a * b,
            "/" => a.checked_div(b)?,
            _ => return None,
        };
        stack.push(value);
    }
    match stack[..] {
        [result] => Some(result),
        _ => None,
    }
}
''',
   [("Simple expressions", 'assert_eq!(eval_rpn("3 4 + 2 *"), Some(14));\nassert_eq!(eval_rpn("10 2 -"), Some(8), "the second value popped is the left operand");\nassert_eq!(eval_rpn("20 4 /"), Some(5));'),
    ("Negative numbers", 'assert_eq!(eval_rpn("-3 2 *"), Some(-6));'),
    ("Malformed", 'for bad in ["", "1 +", "1 2", "1 2 ^", "4 0 /"] {\n    assert_eq!(eval_rpn(bad), None, "eval_rpn({bad:?})");\n}')],
   [("        let (Some(b), Some(a)) = (stack.pop(), stack.pop()) else {", "        let (Some(a), Some(b)) = (stack.pop(), stack.pop()) else {"), ("        [result] => Some(result),\n", "        [.., result] => Some(result),\n")],
   ["Parse numbers first; if parsing fails, the token should be an operator.", "Pop b first, then a: for \"10 2 -\" that gives 10 - 2.", "A slice pattern [result] matches a stack with exactly one value."],
   "Patterns do the validation: the tuple let-else rejects a missing operand and the slice pattern rejects leftovers. checked_div turns division by zero into None, and ? passes it straight out.")

ex("19.2", "Classify with ranges, guards and bindings",
   "Write classify(n) and describe_point(p) using pattern syntax.\n\n"
   "Specification:\n- classify(n: i32) returns \"negative\" below 0, \"zero\", \"small N\" for 1 to 9 (with the number, via an @ binding), \"even teen\" or \"odd teen\" for 13 to 19 (using a match guard), and \"big\" for everything else.\n- describe_point((x, y): (i32, i32)) returns \"origin\", \"on the x axis\" (y is 0), \"on the y axis\" (x is 0), \"on the diagonal\" (x equals y), or \"elsewhere\".\n\n"
   "Examples:\n- classify(7) returns \"small 7\"\n- classify(14) returns \"even teen\"\n- describe_point((3, 3)) returns \"on the diagonal\"\n\n"
   "Edge cases: 10, 11 and 12 are \"big\"; (0, 0) is the origin, not an axis.",
   r'''pub fn classify(n: i32) -> String {
    todo!()
}

pub fn describe_point(p: (i32, i32)) -> &'static str {
    todo!()
}
''',
   r'''pub fn classify(n: i32) -> String {
    match n {
        i32::MIN..=-1 => String::from("negative"),
        0 => String::from("zero"),
        small @ 1..=9 => format!("small {small}"),
        13..=19 if n % 2 == 0 => String::from("even teen"),
        13..=19 => String::from("odd teen"),
        _ => String::from("big"),
    }
}

pub fn describe_point(p: (i32, i32)) -> &'static str {
    match p {
        (0, 0) => "origin",
        (_, 0) => "on the x axis",
        (0, _) => "on the y axis",
        (x, y) if x == y => "on the diagonal",
        _ => "elsewhere",
    }
}
''',
   [("Numbers", 'assert_eq!(classify(-4), "negative");\nassert_eq!(classify(0), "zero");\nassert_eq!(classify(7), "small 7");'),
    ("Teens", 'assert_eq!(classify(14), "even teen");\nassert_eq!(classify(13), "odd teen");\nassert_eq!(classify(19), "odd teen");'),
    ("Big", 'for n in [10, 11, 12, 20, 1000] {\n    assert_eq!(classify(n), "big", "classify({n})");\n}'),
    ("Points", 'assert_eq!(describe_point((0, 0)), "origin");\nassert_eq!(describe_point((5, 0)), "on the x axis");\nassert_eq!(describe_point((0, -2)), "on the y axis");\nassert_eq!(describe_point((3, 3)), "on the diagonal");\nassert_eq!(describe_point((1, 2)), "elsewhere");')],
   [("small @ 1..=9 =>", "small @ 1..=12 =>"), ("        (0, 0) => \"origin\",\n", "")],
   ["Ranges in patterns are inclusive: 1..=9.", "name @ pattern binds the matched value to a name.", "Arms are tried in order, so put (0, 0) before the axis arms."],
   "Ranges, @ bindings and guards let a single match express rules that would take a chain of ifs, and the compiler checks every i32 is covered. Arm order is part of the meaning, which the origin case shows.")

ex("19.3", "Parse commands with slice patterns",
   "Write parse_command(line) that turns words into a Command using slice patterns.\n\n"
   "Specification:\n- enum Command { Add { name: String, qty: u32 }, Remove(String), List, Help } derives Debug and PartialEq.\n- Accepted forms (words split on whitespace): add NAME QTY, add NAME (qty 1), remove NAME, list, help or an empty line.\n- QTY must be a positive whole number, otherwise Err(\"bad quantity: TEXT\").\n- Anything else gives Err(\"unknown command: LINE\") with the trimmed line.\n\n"
   "Examples:\n- parse_command(\"add tea 3\") is Ok(Add { name: \"tea\", qty: 3 })\n- parse_command(\"   \") is Ok(Help)\n\n"
   "Edge cases: \"remove\" with no name is unknown; \"add tea 0\" is a bad quantity.",
   r'''#[derive(Debug, PartialEq)]
pub enum Command {
    Add { name: String, qty: u32 },
    Remove(String),
    List,
    Help,
}

pub fn parse_command(line: &str) -> Result<Command, String> {
    todo!()
}
''',
   r'''#[derive(Debug, PartialEq)]
pub enum Command {
    Add { name: String, qty: u32 },
    Remove(String),
    List,
    Help,
}

pub fn parse_command(line: &str) -> Result<Command, String> {
    let words: Vec<&str> = line.split_whitespace().collect();
    match words[..] {
        ["add", name] => Ok(Command::Add { name: name.to_string(), qty: 1 }),
        ["add", name, qty] => match qty.parse::<u32>() {
            Ok(q) if q > 0 => Ok(Command::Add { name: name.to_string(), qty: q }),
            _ => Err(format!("bad quantity: {qty}")),
        },
        ["remove", name] => Ok(Command::Remove(name.to_string())),
        ["list"] => Ok(Command::List),
        [] | ["help"] => Ok(Command::Help),
        _ => Err(format!("unknown command: {}", line.trim())),
    }
}
''',
   [("Add", 'assert_eq!(parse_command("add tea 3"), Ok(Command::Add { name: "tea".into(), qty: 3 }));\nassert_eq!(parse_command("add jam"), Ok(Command::Add { name: "jam".into(), qty: 1 }));'),
    ("Other commands", 'assert_eq!(parse_command("remove tea"), Ok(Command::Remove("tea".into())));\nassert_eq!(parse_command(" list "), Ok(Command::List));\nassert_eq!(parse_command("help"), Ok(Command::Help));\nassert_eq!(parse_command("   "), Ok(Command::Help));'),
    ("Bad quantity", 'assert_eq!(parse_command("add tea 0"), Err("bad quantity: 0".into()));\nassert_eq!(parse_command("add tea lots"), Err("bad quantity: lots".into()));'),
    ("Unknown", 'assert_eq!(parse_command("remove"), Err("unknown command: remove".into()));\nassert_eq!(parse_command(" fly away "), Err("unknown command: fly away".into()));')],
   [("Ok(q) if q > 0 =>", "Ok(q) =>"), ("        [] | [\"help\"] => Ok(Command::Help),\n", "        [\"help\"] => Ok(Command::Help),\n")],
   ["Collect the words into a Vec<&str> and match on words[..].", "Patterns like [\"add\", name, qty] check the length and the first word at once.", "[] | [\"help\"] matches either an empty line or help."],
   "Slice patterns make the accepted grammar readable at a glance: each arm is one form of the command. Anything that doesn't fit falls through to a single error arm, so no malformed input slips through.")

# ---------------------------------------------------------------- chapter 20
ex("20.1", "Two mutable halves with unsafe",
   "Write split_at_mut_raw(values, mid), your own version of the standard split_at_mut, using raw pointers.\n\n"
   "Specification:\n- Return (&mut values[..mid], &mut values[mid..]) as two mutable slices that don't overlap.\n- Panic with a message containing \"mid out of range\" if mid is greater than the length.\n- Use slice::from_raw_parts_mut inside an unsafe block, with a SAFETY comment explaining why it's sound.\n\n"
   "Examples:\n- for [1, 2, 3, 4, 5] and mid 2, the halves are [1, 2] and [3, 4, 5]; changing them changes the original\n\n"
   "Edge cases: mid 0 gives an empty first half; mid equal to the length gives an empty second half.",
   r'''pub fn split_at_mut_raw(values: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    todo!()
}
''',
   r'''use std::slice;

pub fn split_at_mut_raw(values: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    let len = values.len();
    assert!(mid <= len, "mid out of range: {mid} > {len}");
    let ptr = values.as_mut_ptr();
    // SAFETY: mid <= len, so both ranges lie inside the slice, and they don't
    // overlap, so handing out two mutable slices never aliases.
    unsafe { (slice::from_raw_parts_mut(ptr, mid), slice::from_raw_parts_mut(ptr.add(mid), len - mid)) }
}
''',
   [("Halves", 'let mut v = [1, 2, 3, 4, 5];\nlet (a, b) = split_at_mut_raw(&mut v, 2);\nassert_eq!((&*a, &*b), (&[1, 2][..], &[3, 4, 5][..]));'),
    ("Changes the original", 'let mut v = [1, 2, 3, 4];\n{\n    let (a, b) = split_at_mut_raw(&mut v, 1);\n    a[0] = 10;\n    b[2] = 40;\n}\nassert_eq!(v, [10, 2, 3, 40]);'),
    ("Edges", 'let mut v = [1, 2, 3];\nassert_eq!(split_at_mut_raw(&mut v, 0).0.len(), 0);\nassert_eq!(split_at_mut_raw(&mut v, 3).1.len(), 0);'),
    ("Out of range", 'let mut v = [1, 2, 3];\nsplit_at_mut_raw(&mut v, 4);', '#[should_panic(expected = "mid out of range")]')],
   [("slice::from_raw_parts_mut(ptr.add(mid), len - mid)", "slice::from_raw_parts_mut(ptr.add(mid.saturating_sub(1)), len - mid)"), ('    assert!(mid <= len, "mid out of range: {mid} > {len}");\n', '    assert!(mid <= len + 1, "mid out of range: {mid} > {len}");\n')],
   ["The borrow checker can't see that two halves don't overlap, which is why this needs unsafe.", "as_mut_ptr gives the start; ptr.add(mid) is the start of the second half.", "Check mid <= len before the unsafe block: that check is what makes it sound."],
   "unsafe doesn't turn the checks off; it lets you promise something the compiler can't prove. The assert is the proof: without it, a large mid would create a slice pointing outside the array. Keeping unsafe blocks tiny, with a SAFETY comment, is the habit clippy and code reviewers look for.")

ex("20.2", "Operators and newtypes",
   "Overload operators for length types, and use the newtype pattern to implement Display for a Vec.\n\n"
   "Specification:\n- Millimeters(u32) and Meters(u32) derive Debug, PartialEq, Clone and Copy.\n- impl Add for Millimeters (adds them) and impl Add<Meters> for Millimeters (converts the meters: 1 m = 1000 mm).\n- Wrapper(Vec<String>) implements Display as the items joined with \", \" inside square brackets.\n\n"
   "Examples:\n- Millimeters(500) + Meters(2) is Millimeters(2500)\n- Wrapper(vec![\"a\", \"b\"]) displays as \"[a, b]\"\n\n"
   "Edge cases: an empty Wrapper displays as \"[]\".",
   r'''use std::fmt;
use std::ops::Add;

#[derive(Debug, PartialEq, Clone, Copy)]
pub struct Millimeters(pub u32);

#[derive(Debug, PartialEq, Clone, Copy)]
pub struct Meters(pub u32);

impl Add for Millimeters {
    type Output = Millimeters;

    fn add(self, other: Millimeters) -> Millimeters {
        todo!()
    }
}

impl Add<Meters> for Millimeters {
    type Output = Millimeters;

    fn add(self, other: Meters) -> Millimeters {
        todo!()
    }
}

pub struct Wrapper(pub Vec<String>);

impl fmt::Display for Wrapper {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        todo!()
    }
}
''',
   r'''use std::fmt;
use std::ops::Add;

#[derive(Debug, PartialEq, Clone, Copy)]
pub struct Millimeters(pub u32);

#[derive(Debug, PartialEq, Clone, Copy)]
pub struct Meters(pub u32);

impl Add for Millimeters {
    type Output = Millimeters;

    fn add(self, other: Millimeters) -> Millimeters {
        Millimeters(self.0 + other.0)
    }
}

impl Add<Meters> for Millimeters {
    type Output = Millimeters;

    fn add(self, other: Meters) -> Millimeters {
        Millimeters(self.0 + other.0 * 1000)
    }
}

pub struct Wrapper(pub Vec<String>);

impl fmt::Display for Wrapper {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "[{}]", self.0.join(", "))
    }
}
''',
   [("Add millimeters", 'assert_eq!(Millimeters(300) + Millimeters(200), Millimeters(500));'),
    ("Add meters", 'assert_eq!(Millimeters(500) + Meters(2), Millimeters(2500));'),
    ("Display a wrapper", 'let w = Wrapper(vec!["a".to_string(), "b".to_string()]);\nassert_eq!(w.to_string(), "[a, b]");\nassert_eq!(Wrapper(vec![]).to_string(), "[]");')],
   [("Millimeters(self.0 + other.0 * 1000)", "Millimeters(self.0 + other.0 * 100)"), ('write!(f, "[{}]", self.0.join(", "))', 'write!(f, "{}", self.0.join(", "))')],
   ["Add<Meters> means \"the right-hand side is Meters\"; the default is Self.", "Output is the type the + expression produces.", "write!(f, ...) writes formatted text into the formatter."],
   "Newtypes make units part of the type, so adding meters to millimeters converts correctly instead of silently mixing them. The orphan rule forbids implementing Display for Vec<String> directly (neither is yours); wrapping it in your own type is the standard way round it.")

ex("20.3", "Function pointers in a table",
   "Write a calculator that looks up operations in a table of function pointers.\n\n"
   "Specification:\n- operation(name: &str) -> Option<fn(i64, i64) -> i64> returns add, sub, mul or max for the names \"add\", \"sub\", \"mul\" and \"max\", None otherwise.\n- apply_all(fs: &[fn(i64) -> i64], x: i64) -> Vec<i64> applies each function to x.\n- calculate(name, a, b) -> Result<i64, String> uses operation, with Err(\"unknown operation: NAME\").\n\n"
   "Examples:\n- operation(\"mul\").unwrap()(6, 7) is 42\n- apply_all(&[|x| x + 1, |x| x * x], 5) is [6, 25]\n\n"
   "Edge cases: closures that capture nothing can be used as fn pointers; i64::max can be used directly.",
   r'''pub fn operation(name: &str) -> Option<fn(i64, i64) -> i64> {
    todo!()
}

pub fn apply_all(fs: &[fn(i64) -> i64], x: i64) -> Vec<i64> {
    todo!()
}

pub fn calculate(name: &str, a: i64, b: i64) -> Result<i64, String> {
    todo!()
}
''',
   r'''fn add(a: i64, b: i64) -> i64 {
    a + b
}

fn sub(a: i64, b: i64) -> i64 {
    a - b
}

fn mul(a: i64, b: i64) -> i64 {
    a * b
}

pub type BinOp = fn(i64, i64) -> i64;

pub fn operation(name: &str) -> Option<BinOp> {
    let table: [(&str, BinOp); 4] = [("add", add), ("sub", sub), ("mul", mul), ("max", i64::max)];
    table.iter().find(|(n, _)| *n == name).map(|&(_, f)| f)
}

pub fn apply_all(fs: &[fn(i64) -> i64], x: i64) -> Vec<i64> {
    fs.iter().map(|f| f(x)).collect()
}

pub fn calculate(name: &str, a: i64, b: i64) -> Result<i64, String> {
    let f = operation(name).ok_or_else(|| format!("unknown operation: {name}"))?;
    Ok(f(a, b))
}
''',
   [("Lookup", 'assert_eq!(operation("mul").unwrap()(6, 7), 42);\nassert_eq!(operation("sub").unwrap()(6, 7), -1);\nassert_eq!(operation("max").unwrap()(6, 7), 7);\nassert!(operation("pow").is_none());'),
    ("Apply all", 'assert_eq!(apply_all(&[|x| x + 1, |x| x * x], 5), vec![6, 25]);\nassert!(apply_all(&[], 5).is_empty());'),
    ("Calculate", 'assert_eq!(calculate("add", 2, 3), Ok(5));\nassert_eq!(calculate("pow", 2, 3), Err("unknown operation: pow".to_string()));')],
   [('("sub", sub)', '("sub", add)'), ("fs.iter().map(|f| f(x)).collect()", "fs.iter().map(|f| f(x)).skip(1).collect()")],
   ["fn(i64, i64) -> i64 is the type of a plain function; named functions and capture-free closures coerce to it.", "A small array of (name, function) pairs is a dispatch table; a type alias such as type BinOp = fn(i64, i64) -> i64; keeps it readable.", "find then map pulls the function out of the matching pair."],
   "Function pointers are Copy and have no captured state, so a table of them is simple and fast, unlike Box<dyn Fn>. That makes them a natural fit for command tables, parsers and callbacks into C code.")

ex("20.4", "A hashmap! macro",
   "Write a declarative macro hashmap! that builds a HashMap from key => value pairs.\n\n"
   "Specification:\n- hashmap!{ \"a\" => 1, \"b\" => 2 } creates a HashMap with those entries.\n- hashmap!{} creates an empty map.\n- A trailing comma is allowed.\n- Each key and value expression is evaluated exactly once.\n\n"
   "Examples:\n- let m = hashmap!{ \"tea\" => 3, \"jam\" => 1 }; m[\"tea\"] is 3\n\n"
   "Edge cases: works with any key type that HashMap accepts, such as numbers.",
   r'''#[macro_export]
macro_rules! hashmap {
    () => {
        ::std::collections::HashMap::new()
    };
}
''',
   r'''#[macro_export]
macro_rules! hashmap {
    ($($key:expr => $value:expr),* $(,)?) => {{
        let mut map = ::std::collections::HashMap::new();
        $(map.insert($key, $value);)*
        map
    }};
}
''',
   [("Pairs", 'let m = hashmap!{ "tea" => 3, "jam" => 1 };\nassert_eq!(m.len(), 2);\nassert_eq!(m["tea"], 3);'),
    ("Empty and trailing comma", 'let e: std::collections::HashMap<i32, i32> = hashmap!{};\nassert!(e.is_empty());\nlet m = hashmap!{ 1 => "one", 2 => "two", };\nassert_eq!(m[&2], "two");'),
    ("Evaluated once", 'let mut calls = 0;\nlet mut next = || { calls += 1; calls };\nlet m = hashmap!{ "a" => next(), "b" => next() };\nassert_eq!(calls, 2);\nassert_eq!((m["a"], m["b"]), (1, 2));')],
   [("$(map.insert($key, $value);)*", "$(map.insert($key, $value);)* map.clear();"), ("$(map.insert($key, $value);)*", "$(map.insert($key.clone(), $value);)* map.insert($key, $value);")],
   ["$( ... ),* repeats a pattern separated by commas; $(,)? allows one optional trailing comma.", "The double braces {{ }} make the expansion a block expression that ends with map.", "Write ::std::collections::HashMap with a leading :: so it works wherever the macro is used."],
   loose=True,
   explain="macro_rules! matches tokens, not types, and expands at compile time, which is how vec! works too. The trailing comma rule and the fully qualified path are the details that make a macro pleasant for other people to use.")

# ---------------------------------------------------------------- chapter 21
ex("21.1", "Parse a request, build a response",
   "Write the HTTP pieces of the book's web server as testable functions.\n\n"
   "Specification:\n- parse_request_line(line) returns Some((method, path)) for a line like \"GET /hello HTTP/1.1\", borrowing from line, or None if it doesn't have exactly three parts or the last part doesn't start with \"HTTP/\".\n- response(status: u16, body: &str) -> String returns \"HTTP/1.1 STATUS REASON\\r\\nContent-Length: N\\r\\n\\r\\nBODY\", with the reason \"OK\" for 200, \"Not Found\" for 404 and \"Internal Server Error\" otherwise. N is the body length in bytes.\n\n"
   "Examples:\n- parse_request_line(\"GET / HTTP/1.1\") returns Some((\"GET\", \"/\"))\n- response(200, \"hi\") is \"HTTP/1.1 200 OK\\r\\nContent-Length: 2\\r\\n\\r\\nhi\"\n\n"
   "Edge cases: the length of \"é\" is 2 bytes.",
   r'''pub fn parse_request_line(line: &str) -> Option<(&str, &str)> {
    todo!()
}

pub fn response(status: u16, body: &str) -> String {
    todo!()
}
''',
   r'''pub fn parse_request_line(line: &str) -> Option<(&str, &str)> {
    let parts: Vec<&str> = line.split_whitespace().collect();
    match parts[..] {
        [method, path, version] if version.starts_with("HTTP/") => Some((method, path)),
        _ => None,
    }
}

pub fn response(status: u16, body: &str) -> String {
    let reason = match status {
        200 => "OK",
        404 => "Not Found",
        _ => "Internal Server Error",
    };
    format!("HTTP/1.1 {status} {reason}\r\nContent-Length: {}\r\n\r\n{body}", body.len())
}
''',
   [("Request line", 'assert_eq!(parse_request_line("GET / HTTP/1.1"), Some(("GET", "/")));\nassert_eq!(parse_request_line("POST /api/tasks HTTP/1.1"), Some(("POST", "/api/tasks")));'),
    ("Bad request lines", 'assert_eq!(parse_request_line("GET /"), None);\nassert_eq!(parse_request_line("GET / FTP"), None);\nassert_eq!(parse_request_line(""), None);'),
    ("Response", 'assert_eq!(response(200, "hi"), "HTTP/1.1 200 OK\\r\\nContent-Length: 2\\r\\n\\r\\nhi");\nassert_eq!(response(404, ""), "HTTP/1.1 404 Not Found\\r\\nContent-Length: 0\\r\\n\\r\\n");'),
    ("Length in bytes", 'assert!(response(200, "é").contains("Content-Length: 2\\r\\n"), "é is 2 bytes in UTF-8");\nassert!(response(500, "x").starts_with("HTTP/1.1 500 Internal Server Error"));')],
   [('if version.starts_with("HTTP/")', 'if !version.is_empty()'), ("body.len())", "body.chars().count())")],
   ["Split the line on whitespace and match the parts with a slice pattern.", "HTTP lines end with \\r\\n, and an empty line separates headers from the body.", "Content-Length counts bytes, which is what str::len gives."],
   "Pulling parsing and formatting out of handle_connection means they can be tested without opening a socket. Content-Length in bytes matters: a browser reading a character count would stop early on any non-ASCII text.")

ex("21.2", "A thread pool that finishes its work",
   "Write a small ThreadPool like the book's: a fixed number of workers take jobs from a shared channel.\n\n"
   "Specification:\n- ThreadPool::new(size) panics with \"size must be at least 1\" for 0, otherwise starts size worker threads.\n- execute(&self, f) sends any FnOnce() + Send + 'static job to the workers.\n- size(&self) returns the number of workers.\n- Dropping the pool closes the channel and joins every worker, so all jobs sent before the drop have finished afterwards.\n\n"
   "Examples:\n- a pool of 4 running 100 jobs that each add 1 to a shared counter leaves it at 100 once the pool is dropped\n\n"
   "Edge cases: jobs run on more than one thread when there are several workers.",
   r'''use std::sync::{mpsc, Arc, Mutex};
use std::thread;

type Job = Box<dyn FnOnce() + Send + 'static>;

pub struct ThreadPool {
    workers: Vec<thread::JoinHandle<()>>,
    sender: Option<mpsc::Sender<Job>>,
}

impl ThreadPool {
    pub fn new(size: usize) -> ThreadPool {
        todo!()
    }

    pub fn execute<F: FnOnce() + Send + 'static>(&self, f: F) {
        todo!()
    }

    pub fn size(&self) -> usize {
        todo!()
    }
}

impl Drop for ThreadPool {
    fn drop(&mut self) {
        todo!()
    }
}
''',
   r'''use std::sync::{mpsc, Arc, Mutex};
use std::thread;

type Job = Box<dyn FnOnce() + Send + 'static>;

pub struct ThreadPool {
    workers: Vec<thread::JoinHandle<()>>,
    sender: Option<mpsc::Sender<Job>>,
}

impl ThreadPool {
    pub fn new(size: usize) -> ThreadPool {
        assert!(size > 0, "size must be at least 1");
        let (sender, receiver) = mpsc::channel::<Job>();
        let receiver = Arc::new(Mutex::new(receiver));
        let workers = (0..size)
            .map(|_| {
                let receiver = Arc::clone(&receiver);
                thread::spawn(move || {
                    loop {
                        let message = receiver.lock().unwrap().recv();
                        match message {
                            Ok(job) => job(),
                            Err(_) => break,
                        }
                    }
                })
            })
            .collect();
        ThreadPool { workers, sender: Some(sender) }
    }

    pub fn execute<F: FnOnce() + Send + 'static>(&self, f: F) {
        self.sender.as_ref().unwrap().send(Box::new(f)).unwrap();
    }

    pub fn size(&self) -> usize {
        self.workers.len()
    }
}

impl Drop for ThreadPool {
    fn drop(&mut self) {
        drop(self.sender.take());
        for worker in self.workers.drain(..) {
            worker.join().unwrap();
        }
    }
}
''',
   [("Runs every job", 'use std::sync::atomic::{AtomicUsize, Ordering};\nlet counter = Arc::new(AtomicUsize::new(0));\n{\n    let pool = ThreadPool::new(4);\n    assert_eq!(pool.size(), 4);\n    for _ in 0..100 {\n        let c = Arc::clone(&counter);\n        pool.execute(move || { c.fetch_add(1, Ordering::SeqCst); });\n    }\n}\nassert_eq!(counter.load(Ordering::SeqCst), 100, "every job must have run once the pool is dropped");'),
    ("Uses several threads", 'use std::collections::HashSet;\nlet ids = Arc::new(Mutex::new(HashSet::new()));\n{\n    let pool = ThreadPool::new(3);\n    for _ in 0..12 {\n        let ids = Arc::clone(&ids);\n        pool.execute(move || {\n            std::thread::sleep(std::time::Duration::from_millis(20));\n            ids.lock().unwrap().insert(std::thread::current().id());\n        });\n    }\n}\nassert!(ids.lock().unwrap().len() > 1, "jobs should run on more than one worker");'),
    ("Size zero panics", 'ThreadPool::new(0);', '#[should_panic(expected = "size must be at least 1")]')],
   [("                            Ok(job) => job(),\n", "                            Ok(job) => {\n                                job();\n                                break;\n                            }\n"), ("        for worker in self.workers.drain(..) {\n            worker.join().unwrap();\n        }\n", "")],
   ["One channel, with the receiver shared by the workers through Arc<Mutex<Receiver<Job>>>.", "Each worker loops: lock, recv, run the job; recv returns Err once the sender is gone.", "In drop, take() the sender to drop it, then join every worker."],
   "Dropping the sender is the shutdown signal: recv returns Err once the channel is closed and empty, so each worker finishes the queued jobs and exits. Joining in drop is what makes \"the pool went out of scope\" mean \"all work is done\", which is the graceful shutdown the book's chapter builds.")

ex("21.3", "Read the request headers",
   "Write parse_headers(raw) that reads the headers of an HTTP request into a map.\n\n"
   "Specification:\n- raw is the request text, with lines ending in \\r\\n (accept plain \\n too).\n- Skip the first line (the request line); read \"Name: value\" lines until the first empty line.\n- Return a HashMap<String, String> with header names in lower case and values trimmed.\n- Return Err(\"bad header: LINE\") for a header line without a colon.\n- If a header appears twice, join the values with \", \".\n\n"
   "Examples:\n- \"GET / HTTP/1.1\\r\\nHost: example.com\\r\\nAccept: */*\\r\\n\\r\\n\" gives host example.com and accept */*\n\n"
   "Edge cases: lines after the blank line (the body) are ignored, even if they contain colons.",
   r'''use std::collections::HashMap;

pub fn parse_headers(raw: &str) -> Result<HashMap<String, String>, String> {
    todo!()
}
''',
   r'''use std::collections::HashMap;

pub fn parse_headers(raw: &str) -> Result<HashMap<String, String>, String> {
    let mut headers: HashMap<String, String> = HashMap::new();
    for line in raw.lines().skip(1) {
        let line = line.trim_end_matches('\r');
        if line.is_empty() {
            break;
        }
        let (name, value) = line.split_once(':').ok_or_else(|| format!("bad header: {line}"))?;
        let value = value.trim();
        headers
            .entry(name.trim().to_lowercase())
            .and_modify(|v| {
                v.push_str(", ");
                v.push_str(value);
            })
            .or_insert_with(|| value.to_string());
    }
    Ok(headers)
}
''',
   [("Headers", 'let h = parse_headers("GET / HTTP/1.1\\r\\nHost: example.com\\r\\nAccept: */*\\r\\n\\r\\n").unwrap();\nassert_eq!(h.get("host").map(String::as_str), Some("example.com"));\nassert_eq!(h.get("accept").map(String::as_str), Some("*/*"));\nassert_eq!(h.len(), 2);'),
    ("Stops at the body", 'let h = parse_headers("POST /x HTTP/1.1\\nContent-Type: text/plain\\n\\nnot: a header").unwrap();\nassert_eq!(h.len(), 1, "got {h:?}");'),
    ("Repeated headers", 'let h = parse_headers("GET / HTTP/1.1\\r\\nCookie: a=1\\r\\ncookie: b=2\\r\\n\\r\\n").unwrap();\nassert_eq!(h["cookie"], "a=1, b=2");'),
    ("Bad header", 'assert_eq!(parse_headers("GET / HTTP/1.1\\r\\nnonsense\\r\\n\\r\\n"), Err("bad header: nonsense".to_string()));')],
   [("        if line.is_empty() {\n            break;\n        }\n", "        if line.is_empty() {\n            continue;\n        }\n"), (".entry(name.trim().to_lowercase())", ".entry(name.trim().to_string())")],
   ["lines() splits on \\n; trim_end_matches('\\r') removes the \\r from \\r\\n endings.", "split_once(':') splits at the first colon only, so values like */* or times with colons survive.", "entry(...).and_modify(...).or_insert_with(...) handles first and repeated headers."],
   "Header names are case-insensitive, so lower-casing them once makes every lookup simple. Stopping at the blank line matters for security: a body line that looks like a header must never be treated as one.")
