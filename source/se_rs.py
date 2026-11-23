"""Write content/a6.yaml: module A15, Software engineering practice.

The general engineering skills the course audit found thin in the Rust course: data structures and
algorithms, linked structures and ownership, databases, configuration and logging, shipping with
Docker and code review, and a system design primer. Autograded exercises are in specs/rs_se.py.
"""
import os

import yaml

from career_rs import run
from ecosystem_rs import text_ex

HERE = os.path.dirname(os.path.abspath(__file__))

LESSONS = [
    {"id": "A15.1", "t": "Data structures and algorithms in Rust", "min": 90,
     "learn": "Pick the right standard collection by its cost (Vec, VecDeque, HashMap, BTreeMap, BinaryHeap), read code in Big-O terms, and write merging, binary search and top-k yourself once.",
     "example": {"title": "The standard collections and what each is good at", "code": r'''use std::collections::{BTreeMap, BinaryHeap, HashMap, VecDeque};

fn main() {
    // VecDeque: O(1) at both ends, so it is the queue.
    let mut queue: VecDeque<&str> = VecDeque::new();
    queue.push_back("build");
    queue.push_back("test");
    queue.push_front("urgent fix");
    println!("next job: {:?}", queue.pop_front());

    // BinaryHeap: always hands back the largest item, O(log n) per push and pop.
    let mut heap = BinaryHeap::from(vec![120, 85, 940, 230]);
    heap.push(1210);
    println!("slowest two: {:?} {:?}", heap.pop(), heap.pop());

    // HashMap: O(1) lookups by key, in no particular order.
    let mut hits: HashMap<&str, u32> = HashMap::new();
    for page in ["/", "/docs", "/", "/login", "/"] {
        *hits.entry(page).or_insert(0) += 1;
    }
    println!("hits on /: {}", hits["/"]);

    // BTreeMap: keys stay sorted, so range queries are cheap.
    let grades = BTreeMap::from([(55, "Dee"), (72, "Ada"), (88, "Grace"), (91, "Linus")]);
    let passed: Vec<_> = grades.range(70..90).map(|(score, name)| format!("{name} {score}")).collect();
    println!("between 70 and 89: {passed:?}");

    // A sorted Vec plus binary search is often the fastest lookup of all.
    let sorted = [3, 8, 15, 23, 42];
    println!("{:?} {:?}", sorted.binary_search(&23), sorted.binary_search(&9));
}
''', "note": "Choosing a collection is choosing costs. Vec is the default: contiguous memory makes it fast even when Big-O says otherwise. VecDeque when you remove from the front, HashMap for lookups by key, BTreeMap when you need the keys in order or a range, BinaryHeap when you only ever want the largest. binary_search returns Ok(index) when found and Err(where it would go) when not."},
     "ex": [text_ex("A15.1b", "Cost table for a feature you know",
                    "Pick a feature from one of your projects that stores and looks things up (a cache, a leaderboard, a job queue, a word index). Write a small table: each operation the feature performs, how often it happens, the collection you would use and the Big-O cost of that operation on it. Then name the one operation that would become the bottleneck at a million items and what you would change.",
                    ["List operations first: insert, look up by key, remove oldest, list in order, find the top ten.", "The std::collections documentation has a cost table for every collection.", "The bottleneck is usually an O(n) operation inside a loop."],
                    "Leaderboard for a game:\n- record a score: very frequent; HashMap<PlayerId, u32> insert, O(1)\n- show a player's score: frequent; HashMap get, O(1)\n- top ten: every page view; scanning the map is O(n), which is the bottleneck at a million players\n\nChange: keep a BTreeMap<(u32, PlayerId), ()> ordered by score next to the HashMap, so the top ten is the last ten entries, O(log n + 10), at the price of two updates per score change. For top ten only, a bounded BinaryHeap rebuilt periodically is simpler.",
                    "Being able to say which operation dominates, and what you would trade to fix it, is most of what data-structure interview questions are testing.",
                    ["Each operation has a collection and a Big-O cost", "The frequent operations are identified", "One bottleneck at scale is named with a concrete change"], lang="text")]},
    {"id": "A15.2", "t": "Linked structures: Box, Option and ownership", "min": 90,
     "learn": "Build lists and trees with Option<Box<Node>>, move nodes with take(), and see why ownership makes linked structures the classic hard case in Rust and why Vec usually wins.",
     "example": {"title": "A binary search tree with Option<Box<Node>>", "code": r'''#[derive(Debug)]
struct Node {
    value: i32,
    left: Option<Box<Node>>,
    right: Option<Box<Node>>,
}

fn insert(slot: &mut Option<Box<Node>>, value: i32) {
    match slot {
        None => *slot = Some(Box::new(Node { value, left: None, right: None })),
        Some(node) if value < node.value => insert(&mut node.left, value),
        Some(node) if value > node.value => insert(&mut node.right, value),
        Some(_) => {} // already there
    }
}

fn in_order(slot: &Option<Box<Node>>, out: &mut Vec<i32>) {
    if let Some(node) = slot {
        in_order(&node.left, out);
        out.push(node.value);
        in_order(&node.right, out);
    }
}

fn height(slot: &Option<Box<Node>>) -> usize {
    slot.as_ref().map_or(0, |n| 1 + height(&n.left).max(height(&n.right)))
}

fn main() {
    let mut root = None;
    for v in [50, 30, 70, 20, 40, 60, 80, 30] {
        insert(&mut root, v);
    }
    let mut sorted = Vec::new();
    in_order(&root, &mut sorted);
    println!("{sorted:?} height {}", height(&root));

    let mut chain = None;
    for v in 1..=7 {
        insert(&mut chain, v);
    }
    println!("sorted inserts make a chain of height {}", height(&chain));
}
''', "note": "Option<Box<Node>> is Rust's safe 'pointer that may be null': None is the empty slot, and the Box gives the node a fixed size and a single owner. Passing &mut Option<Box<Node>> lets insert fill the slot it reaches. Walking left, node, right gives sorted output; inserting sorted data gives a chain, which is why the standard library's BTreeMap is a balanced B-tree instead."},
     "ex": [text_ex("A15.2b", "When would you really use a linked list?",
                    "Read the opening of 'Learn Rust With Entirely Too Many Linked Lists' and the std::collections guidance on LinkedList. In five or six sentences, explain why Vec or VecDeque is usually faster than a linked list on modern hardware, name one case where a linked structure is still the right tool, and say how you would store a graph (nodes that point at each other) in safe Rust.",
                    ["Think about where the items sit in memory and what the CPU cache does with that.", "Splicing two lists together, or intrusive lists in kernels, are the usual exceptions.", "Graphs: indices into a Vec (an arena), or Rc<RefCell<...>> with Weak for back edges."],
                    "A Vec keeps its items next to each other, so walking it reads memory in order and the CPU cache prefetches it; each node of a linked list is a separate allocation somewhere on the heap, so every step can be a cache miss, and each node also pays for a pointer and an allocation. Inserting in the middle of a Vec means moving items, but that is a fast memmove and usually still wins up to thousands of elements. A linked structure is right when you must splice or split long sequences in O(1), or when nodes must never move (intrusive lists, LRU caches with handles). For a graph in safe Rust I would store nodes in a Vec and refer to them by index (an arena, as petgraph does), which avoids ownership cycles; Rc<RefCell<Node>> with Weak for back edges works but is slower and can leak.",
                    "Interviewers like this question because the honest answer is about hardware and ownership, not about Big-O tables.",
                    ["Explains the cache and allocation cost of linked nodes", "Names a real case for a linked structure", "Gives a safe way to store a graph (arena indices or Rc/Weak)"], lang="text")]},
    {"id": "A15.3", "t": "Databases from Rust: SQL, sqlx and transactions", "min": 100,
     "learn": "Query a relational database from Rust with parameters, map rows to structs, use JOIN and GROUP BY, wrap related writes in a transaction, and manage the schema with migrations.",
     "example": {"title": "rusqlite: parameters, a join and a transaction", "check": "none", "code": r'''// Cargo.toml: rusqlite = { version = "0.32", features = ["bundled"] }
use rusqlite::{params, Connection, Result};

#[derive(Debug)]
struct Total {
    name: String,
    shifts: i64,
    hours: i64,
}

fn main() -> Result<()> {
    let mut conn = Connection::open_in_memory()?;
    conn.execute_batch(
        "CREATE TABLE staff (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
         CREATE TABLE shifts (id INTEGER PRIMARY KEY, staff_id INTEGER REFERENCES staff(id), hours INTEGER CHECK (hours > 0));",
    )?;

    // A transaction: both inserts are kept, or neither is.
    let tx = conn.transaction()?;
    for name in ["Ada", "Grace", "Linus"] {
        tx.execute("INSERT INTO staff (name) VALUES (?1)", params![name])?;
    }
    for (staff_id, hours) in [(1, 6), (1, 8), (2, 4)] {
        tx.execute("INSERT INTO shifts (staff_id, hours) VALUES (?1, ?2)", params![staff_id, hours])?;
    }
    tx.commit()?;

    // LEFT JOIN keeps Linus, who has no shifts; rows are mapped to a struct.
    let mut stmt = conn.prepare(
        "SELECT s.name, COUNT(sh.id), COALESCE(SUM(sh.hours), 0)
         FROM staff s LEFT JOIN shifts sh ON sh.staff_id = s.id
         GROUP BY s.id ORDER BY 3 DESC",
    )?;
    let totals = stmt.query_map([], |row| Ok(Total { name: row.get(0)?, shifts: row.get(1)?, hours: row.get(2)? }))?;
    for total in totals {
        println!("{:?}", total?);
    }

    // The CHECK constraint refuses bad data, and the failed transaction leaves no trace.
    let tx = conn.transaction()?;
    tx.execute("INSERT INTO shifts (staff_id, hours) VALUES (3, 5)", [])?;
    let bad = tx.execute("INSERT INTO shifts (staff_id, hours) VALUES (3, 0)", []);
    println!("second insert: {}", if bad.is_err() { "refused" } else { "ok" });
    drop(tx); // dropped without commit: rolled back
    let count: i64 = conn.query_row("SELECT COUNT(*) FROM shifts", [], |r| r.get(0))?;
    println!("shifts stored: {count}");
    Ok(())
}
''', "output": "Total { name: \"Ada\", shifts: 2, hours: 14 }\nTotal { name: \"Grace\", shifts: 1, hours: 4 }\nTotal { name: \"Linus\", shifts: 0, hours: 0 }\nsecond insert: refused\nshifts stored: 3",
                 "note": "Values travel as parameters (?1, ?2), never inside the SQL text, which is what stops SQL injection. A Transaction rolls back when it is dropped without commit, so an early return with ? can never leave half the work behind: ownership enforces all-or-nothing. sqlx does the same with async and can check your SQL against the real database at compile time (query! macros); Diesel and SeaORM build the queries from Rust types."},
     "ex": [text_ex("A15.3b", "A migration and a query you can explain",
                    "Using sqlx-cli or refinery with SQLite (or PostgreSQL in Docker), create two migrations for a small schema with a foreign key (for example staff and shifts), then write one query with a JOIN and GROUP BY and run EXPLAIN QUERY PLAN (EXPLAIN in PostgreSQL) on it before and after adding an index on the foreign key. Note what changed in the plan and why an index speeds up reads but slows writes.",
                    ["sqlx migrate add create_staff creates a timestamped .sql file; sqlx migrate run applies the pending ones.", "Index the column you join or filter on: CREATE INDEX idx_shifts_staff ON shifts(staff_id).", "SCAN means every row is read; SEARCH ... USING INDEX means the database jumped to the matches."],
                    "migrations/1_create_staff.sql: CREATE TABLE staff (id INTEGER PRIMARY KEY, name TEXT NOT NULL);\nmigrations/2_create_shifts.sql: CREATE TABLE shifts (id INTEGER PRIMARY KEY, staff_id INTEGER NOT NULL REFERENCES staff(id), hours INTEGER NOT NULL CHECK (hours > 0));\n\nQuery: SELECT s.name, SUM(sh.hours) FROM staff s JOIN shifts sh ON sh.staff_id = s.id GROUP BY s.id;\n\nBefore the index the plan shows SCAN sh: every shift row is read for the join. After CREATE INDEX idx_shifts_staff ON shifts(staff_id) it shows SEARCH sh USING INDEX idx_shifts_staff (staff_id=?): the database looks up each person's shifts directly. Reads go from O(n) to O(log n) per lookup; every INSERT or UPDATE now also has to update the index, so writes get slightly slower and the database a little larger.",
                    "Migrations keep every environment's schema in step with the code, and reading a query plan is how you find out why a query is slow.",
                    ["Two migrations applied with a tool, in order", "A JOIN with GROUP BY that returns the expected rows", "The plan before and after the index, with the difference explained", "The cost of an index on writes is stated"], lang="text")]},
    {"id": "A15.4", "t": "Configuration, logging and tracing", "min": 90,
     "learn": "Read settings from the environment into a typed struct at start-up, log with levels and fields using the log and tracing crates, and know what makes logs useful when something breaks at night.",
     "example": {"title": "Levels and fields: what a structured log line carries", "code": r'''use std::fmt::Write as _;

#[derive(Clone, Copy, PartialEq, PartialOrd, Debug)]
enum Level {
    Debug,
    Info,
    Warn,
    Error,
}

struct Logger {
    min: Level,
    lines: Vec<String>,
}

impl Logger {
    fn log(&mut self, level: Level, target: &str, message: &str, fields: &[(&str, String)]) {
        if level < self.min {
            return; // cheap to skip: nothing is formatted
        }
        let mut line = format!("{:<5} {target}: {message}", format!("{level:?}").to_uppercase());
        for (key, value) in fields {
            let _ = write!(line, " {key}={value}");
        }
        self.lines.push(line);
    }
}

fn import(rows: &[&str], log: &mut Logger) -> Vec<u32> {
    let mut good = Vec::new();
    for (n, row) in rows.iter().enumerate() {
        log.log(Level::Debug, "importer", "parsing", &[("row", (n + 1).to_string())]);
        match row.parse() {
            Ok(v) => good.push(v),
            Err(_) => log.log(Level::Warn, "importer", "row skipped", &[("row", (n + 1).to_string()), ("value", format!("{row:?}"))]),
        }
    }
    log.log(Level::Info, "importer", "finished", &[("loaded", good.len().to_string()), ("total", rows.len().to_string())]);
    good
}

fn main() {
    let mut log = Logger { min: Level::Info, lines: Vec::new() };
    println!("{:?}", import(&["4", "x7", "12"], &mut log));
    log.min = Level::Debug;
    import(&["9"], &mut log);
    for line in &log.lines {
        println!("{line}");
    }
}
''', "note": "This is the shape the real crates give you: log (the facade: info!, warn!, error!) and tracing (the same, plus fields and spans). A level filters cheaply, a target says which part of the program spoke, and key=value fields make the line searchable: 'row=2 value=\"x7\"' is what you need to fix the data. In a service, tracing with tracing-subscriber writes these as JSON and a span ties together every line of one request."},
     "ex": [text_ex("A15.4b", "Add tracing to a small service",
                    "Take a small program of yours (the CLI or the axum service from earlier modules). Add tracing and tracing-subscriber, read the log level from an environment variable, add #[instrument] to two functions, and include at least one field (such as a request or record id) on an event. Run it at info and at debug level and paste three lines of each output. Note one thing you logged that you would remove, and why.",
                    ["tracing_subscriber::fmt().with_env_filter(EnvFilter::from_default_env()).init(); then RUST_LOG=debug cargo run.", "#[tracing::instrument] on a function records a span with its arguments; skip(...) leaves out large or secret ones.", "info!(user_id, \"shift saved\") attaches a field."],
                    "use tracing::{info, instrument};\nuse tracing_subscriber::EnvFilter;\n\n#[instrument(skip(db))]\nasync fn save_shift(db: &Db, user_id: u32, hours: u8) -> Result<(), Error> {\n    db.insert(user_id, hours).await?;\n    info!(user_id, hours, \"shift saved\");\n    Ok(())\n}\n\nfn main() {\n    tracing_subscriber::fmt().with_env_filter(EnvFilter::from_default_env()).init();\n}\n\nRUST_LOG=info: one line per saved shift, with user_id and hours. RUST_LOG=debug adds the span enter and exit lines and the SQL from the database crate. I would remove the event that logged the whole request body: it is noisy and can contain personal data; ids and counts are enough.",
                    "Logs are the only view you have into a running service. Levels, fields and spans decide whether an incident takes five minutes or five hours.",
                    ["The level comes from the environment, not from code", "Two functions are instrumented and an event carries a field", "Output at two levels is shown", "One log line is identified as noise or as a privacy risk"])]},
    {"id": "A15.5", "t": "Shipping Rust: Docker, releases and code review", "min": 90,
     "learn": "Build a small container image with a multi-stage Dockerfile, cut a release with CI, and work through pull requests: commit messages, review comments and merge conflicts.",
     "example": {"title": "A multi-stage Dockerfile for a Rust service", "check": "none", "lang": "dockerfile", "code": r'''# Stage 1: build with the full toolchain (about 1.5 GB, never shipped)
FROM rust:1.97-slim AS build
WORKDIR /app

# Build the dependencies first so this layer is cached until Cargo.toml or Cargo.lock change.
COPY Cargo.toml Cargo.lock ./
RUN mkdir src && echo "fn main() {}" > src/main.rs && cargo build --release && rm -rf src

COPY src ./src
RUN touch src/main.rs && cargo build --release

# Stage 2: copy only the binary into a small base image
FROM debian:bookworm-slim
RUN useradd --create-home app
USER app
COPY --from=build /app/target/release/shiftboard /usr/local/bin/shiftboard
ENV PORT=8000
EXPOSE 8000
CMD ["shiftboard"]
''', "output": "$ docker build -t shiftboard .\n => [build 4/6] RUN mkdir src && echo ... cargo build --release    74.3s\n => [build 6/6] RUN touch src/main.rs && cargo build --release     9.8s\n$ docker build -t shiftboard .        # after editing only src/\n => CACHED [build 4/6] RUN mkdir src && echo ... cargo build       0.0s\n => [build 6/6] RUN touch src/main.rs && cargo build --release     9.6s\n$ docker images shiftboard\nREPOSITORY   TAG      SIZE\nshiftboard   latest   84.2MB",
                 "note": "The build stage needs the compiler; the final image needs only the binary, so the shipped image is tens of megabytes instead of gigabytes and has far less in it to attack. Building a dummy main.rs first caches the dependency compile, the slow part; cargo-chef automates that trick. A fully static binary (target x86_64-unknown-linux-musl) can even run FROM scratch."},
     "ex": [text_ex("A15.5b", "Ship one of your projects",
                    "Take a Track 3 project (or any binary crate of yours). 1. Write a multi-stage Dockerfile, build it and note the image size. 2. Add a GitHub Actions workflow that runs cargo fmt --check, cargo clippy -- -D warnings and cargo test on every pull request. 3. Open a pull request with one small change, using a commit message in the form 'type(scope): summary', and review it yourself with at least four comments labelled blocking, suggestion, question or praise. Merge it when CI is green.",
                    ["Use the Dockerfile from the worked example and change the binary name.", "dtolnay/rust-toolchain and Swatinem/rust-cache are the usual actions for Rust CI.", "Review the diff as if a colleague wrote it: correctness and tests first, then naming."],
                    "Dockerfile: the two-stage file from the example; final image about 85 MB on debian-slim (about 12 MB static on scratch).\n\n.github/workflows/ci.yml:\non: [pull_request]\njobs:\n  check:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: dtolnay/rust-toolchain@stable\n        with: { components: 'rustfmt, clippy' }\n      - uses: Swatinem/rust-cache@v2\n      - run: cargo fmt --check\n      - run: cargo clippy --all-targets -- -D warnings\n      - run: cargo test\n\nPR: 'fix(parser): reject empty shift names'. Review comments: blocking: the new check trims the name but the stored value is not trimmed, so ' Ada' and 'Ada' become two people. question: should an all-space name be an error or be ignored? suggestion: name the error variant EmptyName instead of Invalid. praise: the test table covers the edge cases clearly.",
                    "A project with a container image, green CI and a reviewed pull-request history shows an employer how you would work on their team, not only that you can write Rust.",
                    ["A multi-stage Dockerfile that builds, with the image size noted", "CI runs fmt, clippy and tests on pull requests", "A pull request with a conventional commit message", "At least four labelled review comments, addressed before merging"], lang="text")]},
    {"id": "A15.6", "t": "A system design primer: caches, queues and rough numbers", "min": 100,
     "learn": "Sketch how a web service fits together (load balancer, app servers, database, cache, queue), estimate load with rough numbers, and explain the trade-offs interviewers ask about.",
     "example": {"title": "Cache-aside, and why invalidation matters", "code": r'''use std::collections::HashMap;

struct Database {
    rows: HashMap<String, u32>,
    reads: u32,
}

impl Database {
    fn get(&mut self, key: &str) -> Option<u32> {
        self.reads += 1; // pretend this costs 40 ms
        self.rows.get(key).copied()
    }
}

struct Service {
    db: Database,
    cache: HashMap<String, u32>,
}

impl Service {
    fn shifts(&mut self, user: &str) -> Option<u32> {
        if let Some(&hit) = self.cache.get(user) {
            return Some(hit);
        }
        let value = self.db.get(user)?; // miss: ask the database, then remember the answer
        self.cache.insert(user.to_string(), value);
        Some(value)
    }

    fn set_shifts(&mut self, user: &str, value: u32) {
        self.db.rows.insert(user.to_string(), value);
        self.cache.remove(user); // invalidate, so the next read sees the new value
    }
}

fn main() {
    let db = Database { rows: HashMap::from([("ada".to_string(), 3)]), reads: 0 };
    let mut service = Service { db, cache: HashMap::new() };
    for _ in 0..100 {
        service.shifts("ada");
    }
    println!("100 reads, database reads: {}", service.db.reads);
    service.set_shifts("ada", 4);
    println!("after an update: {:?}, database reads: {}", service.shifts("ada"), service.db.reads);

    let (db_ms, cache_ms, hit_rate) = (40.0, 1.0, 0.9);
    let average = hit_rate * cache_ms + (1.0 - hit_rate) * (cache_ms + db_ms);
    println!("average read: {db_ms} ms without a cache, {average:.1} ms at a 90% hit rate");
}
''', "note": "Cache-aside is the pattern used with Redis and with in-process caches such as moka: read the cache, fall back to the database on a miss, and delete the entry when the data changes. A hundred reads cost one query, and at a 90% hit rate reads are about eight times faster while the database sees a tenth of the traffic. Leave out the remove call and users see stale data, the classic caching bug."},
     "ex": [text_ex("A15.6b", "Design a URL shortener on one page",
                    "Design a URL shortener for 10 million new links a month and 100 reads for every write. On one page: 1. rough numbers (writes and reads per second on average and at a 5x peak, storage for five years at about 500 bytes a link); 2. a diagram in text of the components; 3. how short codes are made; 4. what you would cache and for how long; 5. the first bottleneck and what you would measure.",
                    ["A month has about 2.6 million seconds; 10 million a month is about 4 writes a second.", "Reads dominate 100 to 1, so design the read path first: cache, then database.", "A counter encoded in base 62 gives short, unique codes; seven characters cover 3.5 trillion links."],
                    "Numbers: 10M links a month is about 4 writes/s on average and 20 at peak; reads are 400/s on average and 2,000 at peak. Storage: 600M links in five years at 500 bytes is about 300 GB, which fits one PostgreSQL primary with replicas.\n\nComponents: client -> load balancer -> stateless Rust (axum) servers -> Redis cache -> PostgreSQL primary + read replica. Writes go to the primary.\n\nCodes: a database sequence encoded in base 62 (seven characters is enough); unique by construction, no collision check. If codes must not be guessable, add a random suffix.\n\nCache: code -> URL in Redis with a TTL of a day, since links almost never change and a few hot links take most of the traffic; delete the key when a link is edited or removed.\n\nBottleneck: the database on cache misses at peak. I would measure the cache hit rate, p99 redirect latency and primary CPU; next steps are a read replica, then partitioning by code.",
                    "Nobody expects a junior engineer to design a global system. They expect questions, rough numbers, a clear diagram, one bottleneck and what you would measure.",
                    ["Requests per second and storage are estimated with the arithmetic shown", "A component diagram with a stateless app tier, cache and database", "A way to generate unique short codes", "A caching decision with a TTL and invalidation", "A named bottleneck and what to measure"], lang="text")]},
]

QUIZ = [
    {"q": "Which collection gives the largest item first, with O(log n) push and pop?", "o": ["BinaryHeap", "VecDeque", "HashMap", "BTreeMap"], "a": 0, "x": "BinaryHeap is a max-heap; wrap items in Reverse for a min-heap."},
    {"q": "You need the keys in sorted order and range queries. Which map?", "o": ["BTreeMap", "HashMap", "Vec of pairs, unsorted", "BinaryHeap"], "a": 0, "x": "BTreeMap keeps keys sorted, so range(a..b) and ordered iteration are cheap; HashMap has no order."},
    {"q": "What does Option::take() do on a field holding Some(node)?", "o": ["Moves the node out and leaves None in the field", "Clones the node", "Drops the node", "Returns a reference to the node"], "a": 0, "x": "take() is how you move an owned value out of a place you only have &mut access to, the key move in linked structures."},
    {"q": "Why is Vec usually faster than a linked list, even for some inserts in the middle?", "o": ["Its items are contiguous in memory, which suits the CPU cache, and it needs no allocation per item", "Its inserts are O(1)", "Linked lists are unsafe in Rust", "Vec is implemented in assembly"], "a": 0, "x": "Cache locality and fewer allocations outweigh the O(n) shift for most sizes."},
    {"q": "How do values get into a SQL query safely?", "o": ["As bound parameters (?1, $1), separate from the SQL text", "With format! into the query string", "By escaping quotes by hand", "By converting them to upper case"], "a": 0, "x": "Parameters are sent as data, so they can never be read as SQL. Identifiers cannot be parameters and need an allow-list."},
    {"q": "A rusqlite or sqlx transaction is dropped without commit. What happens?", "o": ["It is rolled back", "It is committed", "The program panics", "The connection is closed for ever"], "a": 0, "x": "Rollback on drop means an early return with ? can never leave half the writes behind."},
    {"q": "Why read configuration into a typed struct at start-up?", "o": ["Problems are reported once, clearly, before the service takes traffic", "It makes the binary smaller", "Environment variables can only be read once", "It avoids using std"], "a": 0, "x": "Fail fast with every problem listed, and give the rest of the program typed values instead of strings."},
    {"q": "What does a field on a log event, such as request_id=42, give you?", "o": ["A way to search for and connect every line about one request", "Faster logging", "Encryption of the message", "A lower log level"], "a": 0, "x": "Structured fields make logs searchable; tracing spans attach them to every event inside the span."},
    {"q": "Why use a multi-stage Dockerfile for a Rust service?", "o": ["The final image holds only the binary, not the toolchain, so it is small and has less to attack", "Rust cannot be built in one stage", "It makes compilation faster", "It is required by cargo"], "a": 0, "x": "Build in a toolchain image, then copy the binary into a slim or scratch image."},
    {"q": "A cache has a 90% hit rate. What share of reads still reach the database?", "o": ["10%", "90%", "50%", "0%"], "a": 0, "x": "Only misses reach the database, which is why the hit rate is the number to watch."},
    {"q": "Which belong in a good code review comment?", "type": "multi", "o": ["How serious it is (blocking or a suggestion)", "What happens and why it matters", "A remark about the author's ability", "A concrete way to fix it, where you have one"], "a": [0, 1, 3], "x": "Review the code, not the person: say what, why, how serious, and what would fix it."},
    {"q": "A job on a queue may run twice after a retry. What property keeps that safe?", "o": ["Idempotence: running it again has no further effect", "Atomic types", "A larger queue", "Lower latency"], "a": 0, "x": "Queues usually deliver at least once, so jobs must tolerate repeats."},
]

MODULE = {
    "id": "a15", "n": "A15", "t": "Software engineering practice", "lv": 4,
    "goal": "The skills every software team expects beyond the language: choosing data structures by cost, linked structures and ownership, querying a database, configuring and observing a service, shipping it, working through code review, and reasoning about a system's design.",
    "res": "std::collections: when to use which | https://doc.rust-lang.org/std/collections/index.html\nLearn Rust With Entirely Too Many Linked Lists | https://rust-unofficial.github.io/too-many-lists/\nsqlx | https://docs.rs/sqlx\nrusqlite | https://docs.rs/rusqlite\ntracing | https://docs.rs/tracing\nThe Twelve-Factor App | https://12factor.net/\nConventional Commits | https://www.conventionalcommits.org/\nGoogle Engineering Practices: code review | https://google.github.io/eng-practices/review/",
    "quiz": QUIZ,
    "recap": {"summary": [
        "Choose collections by cost: Vec by default, VecDeque for queues, HashMap for lookups, BTreeMap for ordered keys, BinaryHeap for the largest first.",
        "Option<Box<Node>> is the safe nullable pointer; take() moves a node out; Vec usually beats a linked list.",
        "Send values as query parameters, validate identifiers, and put related writes in a transaction that rolls back on drop.",
        "Read settings into a typed struct at start-up and report every problem at once; log with levels and fields.",
        "Ship a small image with a multi-stage Dockerfile; keep pull requests small, messages clear and review comments labelled.",
        "Design from rough numbers: stateless app servers, a database, a cache with invalidation, and queues with idempotent jobs."],
        "functions": "BinaryHeap::push / pop || Largest item first, O(log n).\nBTreeMap::range(a..b) || Sorted keys in a range.\nslice.binary_search(&x) || Ok(index) or Err(insert position) in a sorted slice.\nOption::take() || Move the value out and leave None.\nconn.transaction()? ... tx.commit()? || All-or-nothing writes; rollback on drop.\ntracing::info!(field, \"message\") || A log event with a field.\n#[tracing::instrument] || A span around a function call.",
        "next": "Add a Dockerfile, CI and a short design note to one Track 3 project, then finish with the career toolkit."},
    "items": [],
}


def _str(dumper, value):
    # literal blocks for multi-line text: PyYAML's quoted folding breaks on lines that start with "- "
    style = "|" if "\n" in value else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


yaml.SafeDumper.add_representer(str, _str)


def main():
    for L in LESSONS:
        eg = dict(L["example"])
        eg.setdefault("lang", "rust")
        if eg.get("check") != "none":
            eg["output"] = run(eg["code"])
            eg["check"] = "run"
        MODULE["items"].append({"id": L["id"], "t": L["t"], "min": L["min"], "learn": L["learn"], "example": eg, "ex": L["ex"]})
    with open(os.path.join(HERE, "content", "a6.yaml"), "w", encoding="utf-8") as f:
        yaml.safe_dump([MODULE], f, allow_unicode=True, sort_keys=False, width=100000)
    print("wrote content/a6.yaml:", len(LESSONS), "lessons")
    for L in LESSONS:
        if L["example"].get("check") != "none":
            print("---", L["id"])
            print(run(L["example"]["code"]))


if __name__ == "__main__":
    main()
