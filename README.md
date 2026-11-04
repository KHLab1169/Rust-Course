# Rust Course

My self-study Rust course, as a standalone app that runs on my own computer.

- **Track 1** follows [The Rust Programming Language](https://doc.rust-lang.org/book/) (2024 edition), all 21 chapters
- **Track 2** follows [roadmap.sh/rust](https://roadmap.sh/rust), 12 modules
- **Track 3** is six portfolio projects (load tester, flaky-test detector, intrusion detector, axum API, key-value store, WebAssembly)

129 lessons and 258 exercises with worked examples, hints, solutions and explanations, plus chapter quizzes, midterms, finals and grades.

## Run it

You need Python 3 installed to start the small local web server (no internet needed after download).

| System | Do this |
|---|---|
| Windows | Double-click `start-windows.bat` |
| macOS / Linux | Double-click `start-mac-linux.command` (or run `python3 start.py`) |

Your browser opens at **http://127.0.0.1:8766**. Keep the small window open while you study.
(The Python Course uses port 8765, so both can run at the same time.)

## Writing and running the code

Do the exercises in your own Rust IDE. A handy setup is one Cargo project with one file per
exercise in `src/bin/` (run with `cargo run --bin NAME`) and tests run with `cargo test`.
Each exercise also has an **Open in Rust Playground** button when you are away from your IDE.

## Progress

- Progress saves in your browser automatically.
- On first launch the app loads `progress.json` (a snapshot from the online version).
- **Grades → Back up your progress** exports or imports a progress file, to move between
  computers, browsers, or this app and the online page.
- To back up progress to GitHub: export, save the file over `progress.json`, commit and push.

## Source

`source/content/*.yaml` holds every lesson, exercise, solution, quiz and recap.
`source/verify.py` compiles and tests every Rust snippet in them:

    cd source && python3 verify.py content/*.yaml

(needs Rust and PyYAML; snippets that use crates are built with Cargo).

## What's different from the online version

- No cloud sync: progress lives in the browser on this computer (use Export/Import).
- The "Ask the TA" feedback panel needs Claude, so it only appears in the online version.
