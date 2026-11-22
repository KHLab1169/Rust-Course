"""Write content/a5.yaml: module A14, The wider ecosystem.

Covers the roadmap.sh/rust topics the other modules only mention: cryptography, more web
frameworks, CLI and terminal crates, networking beyond HTTP, other runtimes, games and graphics,
embedded, and desktop GUIs. Autograded exercises are in specs/rs_ecosystem.py.
"""
import os

import yaml

from career_rs import run

HERE = os.path.dirname(os.path.abspath(__file__))


def text_ex(eid, t, p, hints, solution, explain, chk, lang="rust"):
    return {"id": eid, "t": t, "p": p, "lang": lang, "check": "none", "hints": hints, "solution": solution, "explain": explain, "chk": chk}


LESSONS = [
    {"id": "A14.1", "t": "Cryptography with ring and RustCrypto", "min": 50,
     "learn": "Use vetted crates instead of writing crypto yourself: hashing and HMAC with RustCrypto's sha2 and hmac or with ring, authenticated encryption with aes-gcm or chacha20poly1305, and constant-time comparison for secrets. Know that sodiumoxide is archived and what replaced it.",
     "example": {"title": "Hash, sign and verify with RustCrypto", "check": "none", "code": r'''// Cargo.toml: sha2 = "0.10", hmac = "0.12", hex = "0.4"
use hmac::{Hmac, Mac};
use sha2::{Digest, Sha256};

type HmacSha256 = Hmac<Sha256>;

fn main() {
    // A checksum: anyone can compute it, so it detects accidents, not attackers.
    let digest = Sha256::digest(b"release-1.4.2.tar.gz contents");
    println!("sha256: {}", hex::encode(digest));

    // A signature with a shared secret: only key holders can produce the tag.
    let mut mac = HmacSha256::new_from_slice(b"webhook secret").expect("HMAC accepts any key length");
    mac.update(b"{\"event\":\"push\"}");
    let tag = mac.finalize().into_bytes();

    // Verify with verify_slice, which compares in constant time.
    let mut check = HmacSha256::new_from_slice(b"webhook secret").unwrap();
    check.update(b"{\"event\":\"push\"}");
    println!("valid: {}", check.verify_slice(&tag).is_ok());
}
''', "note": "This is how a server checks a GitHub webhook: recompute the HMAC of the body with the shared secret and compare in constant time. ring offers the same building blocks (ring::digest, ring::hmac) in one audited crate. sodiumoxide, the libsodium binding the roadmap lists, was archived by its maintainers; dryoc is a pure-Rust libsodium-compatible alternative."},
     "ex": [text_ex("A14.1b", "Verify a download's checksum",
                    "Write a small command-line tool that takes a file path and an expected SHA-256 hex digest, hashes the file in chunks (so large files don't need to fit in memory), and exits with code 0 if they match or 1 with a clear message if not. Use your from_hex and constant_time_eq from the previous exercise, or the hex crate.",
                    ["Sha256::new(), then hasher.update(&buf[..n]) in a loop over file.read(&mut buf).", "finalize() gives the digest; compare it with the expected bytes.", "std::process::exit(1) after printing the mismatch to stderr."],
                    r'''use sha2::{Digest, Sha256};
use std::fs::File;
use std::io::Read;

fn sha256_file(path: &str) -> std::io::Result<Vec<u8>> {
    let mut file = File::open(path)?;
    let mut hasher = Sha256::new();
    let mut buf = [0u8; 64 * 1024];
    loop {
        let n = file.read(&mut buf)?;
        if n == 0 {
            break;
        }
        hasher.update(&buf[..n]);
    }
    Ok(hasher.finalize().to_vec())
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let [_, path, expected] = &args[..] else {
        eprintln!("usage: checksum FILE SHA256_HEX");
        std::process::exit(2);
    };
    let Some(want) = hex::decode(expected).ok() else {
        eprintln!("expected digest is not valid hex");
        std::process::exit(2);
    };
    match sha256_file(path) {
        Ok(got) if constant_time_eq(&got, &want) => println!("OK {path}"),
        Ok(got) => {
            eprintln!("MISMATCH {path}: got {}", hex::encode(got));
            std::process::exit(1);
        }
        Err(e) => {
            eprintln!("cannot read {path}: {e}");
            std::process::exit(2);
        }
    }
}
''',
                    "Reading in chunks keeps memory flat for multi-gigabyte files. Distinct exit codes (0 match, 1 mismatch, 2 usage or I/O error) let a CI script or test harness react correctly, which matters when you verify downloaded test fixtures or build artefacts.",
                    ["Hashes the file in chunks", "Exit code 0 on match, 1 on mismatch, 2 on bad input", "Tested with a correct and a deliberately wrong digest"])]},
    {"id": "A14.2", "t": "More web frameworks: actix-web, Rocket and Loco", "min": 40,
     "learn": "Recognise the main Rust web frameworks beyond axum: actix-web (mature and very fast, its own actor-based runtime on Tokio), Rocket (macro-driven and batteries-included) and Loco (a Rails-style framework built on axum), and pick one for a project.",
     "example": {"title": "The same endpoint in actix-web and Rocket", "check": "none", "code": r'''// actix-web. Cargo.toml: actix-web = "4"
use actix_web::{get, web, App, HttpServer, Responder};

#[get("/health")]
async fn health() -> impl Responder {
    "ok"
}

#[get("/hello/{name}")]
async fn hello(name: web::Path<String>) -> impl Responder {
    format!("Hello, {name}!")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| App::new().service(health).service(hello))
        .bind(("127.0.0.1", 8080))?
        .run()
        .await
}

// Rocket. Cargo.toml: rocket = "0.5"
//
// #[macro_use] extern crate rocket;
//
// #[get("/health")]
// fn health() -> &'static str { "ok" }
//
// #[get("/hello/<name>")]
// fn hello(name: &str) -> String { format!("Hello, {name}!") }
//
// #[launch]
// fn rocket() -> _ { rocket::build().mount("/", routes![health, hello]) }
''', "note": "All three ideas you learned with axum carry over: handlers are async functions, extractors pull typed data from the request, and the framework turns your return value into a response. The differences are style: actix-web uses attribute macros and its own App builder, Rocket leans on macros and conventions, and Loco adds generators, migrations and background jobs on top of axum, much like Rails."},
     "ex": [text_ex("A14.2b", "Port one taskhub route to actix-web",
                    "Take the GET /tasks/{id} route from your taskhub project and rewrite it with actix-web: a path extractor for the id, shared state with web::Data holding your repository, a 404 when the task doesn't exist, and an integration test using actix_web::test.",
                    ["Shared state: App::new().app_data(web::Data::new(repo.clone())).", "Return HttpResponse::NotFound().finish() or HttpResponse::Ok().json(task).", "actix_web::test::init_service and test::call_service let you test without opening a port."],
                    r'''use actix_web::{get, test, web, App, HttpResponse, Responder};

#[get("/tasks/{id}")]
async fn get_task(repo: web::Data<Repo>, id: web::Path<u32>) -> impl Responder {
    match repo.get(*id) {
        Some(task) => HttpResponse::Ok().json(task),
        None => HttpResponse::NotFound().finish(),
    }
}

#[actix_web::test]
async fn missing_task_is_404() {
    let app = test::init_service(App::new().app_data(web::Data::new(Repo::default())).service(get_task)).await;
    let req = test::TestRequest::get().uri("/tasks/99").to_request();
    let resp = test::call_service(&app, req).await;
    assert_eq!(resp.status(), 404);
}
''',
                    "Porting one route is the fastest way to compare frameworks honestly: the same logic, the same test, two styles. In an interview, being able to say why you chose axum (Tokio-native, tower middleware) over actix-web (mature, fast, its own ecosystem) shows judgement, not just familiarity.",
                    ["The route returns JSON for an existing task and 404 otherwise", "State is shared with web::Data", "An actix_web::test test covers the 404 case", "You can explain one reason to choose each framework"])]},
    {"id": "A14.3", "t": "CLI and terminal crates: clap, structopt, termion", "min": 40,
     "learn": "Build polished command-line tools: clap's derive API (which absorbed structopt, now in maintenance), coloured output that switches off when piped, terminal control with termion (Unix only) or crossterm (cross-platform), and full terminal UIs with ratatui.",
     "example": {"title": "A clap derive CLI (structopt's successor)", "check": "none", "code": r'''// Cargo.toml: clap = { version = "4", features = ["derive"] }
use clap::{Parser, ValueEnum};
use std::path::PathBuf;

#[derive(Clone, ValueEnum)]
enum Format {
    Text,
    Json,
}

/// Search files for a pattern.
#[derive(Parser)]
#[command(version, about)]
struct Args {
    /// The text to look for
    query: String,
    /// Files to search
    #[arg(required = true)]
    paths: Vec<PathBuf>,
    /// Ignore upper and lower case
    #[arg(short, long)]
    ignore_case: bool,
    /// Output format
    #[arg(long, value_enum, default_value_t = Format::Text)]
    format: Format,
}

fn main() {
    let args = Args::parse();
    println!("searching {} file(s) for {:?}", args.paths.len(), args.query);
}
''', "note": "structopt pioneered deriving a parser from a struct; clap 3 adopted the idea, and structopt's own README now points to clap's derive API. Doc comments become the --help text, and ValueEnum restricts an option to known values with a helpful error. For terminal control, termion is small but Unix-only; crossterm works on Windows too and is what ratatui uses by default."},
     "ex": [text_ex("A14.3b", "Give minigrep a proper CLI",
                    "Replace minigrep's hand-written argument parsing with clap derive: positional query and paths, --ignore-case, and --color with the values auto, always and never. Colour matches only when stdout is a terminal (std::io::IsTerminal) unless --color says otherwise, and add a test that runs the binary with assert_cmd and checks the output has no escape codes when piped.",
                    ["std::io::stdout().is_terminal() tells you whether output goes to a terminal.", "assert_cmd::Command::cargo_bin(\"minigrep\") runs your binary in a test.", "Your strip_ansi from the previous exercise makes a good assertion helper."],
                    r'''use clap::{Parser, ValueEnum};
use std::io::IsTerminal;

#[derive(Clone, Copy, ValueEnum)]
enum Color {
    Auto,
    Always,
    Never,
}

#[derive(Parser)]
#[command(version, about = "Search files for a pattern")]
struct Args {
    query: String,
    #[arg(required = true)]
    paths: Vec<std::path::PathBuf>,
    #[arg(short, long)]
    ignore_case: bool,
    #[arg(long, value_enum, default_value_t = Color::Auto)]
    color: Color,
}

fn use_color(choice: Color) -> bool {
    match choice {
        Color::Always => true,
        Color::Never => false,
        Color::Auto => std::io::stdout().is_terminal(),
    }
}

// tests/cli.rs
// #[test]
// fn piped_output_has_no_colour() {
//     let out = assert_cmd::Command::cargo_bin("minigrep").unwrap()
//         .args(["to", "poem.txt"]).output().unwrap();
//     let text = String::from_utf8(out.stdout).unwrap();
//     assert!(!text.contains('\x1b'));
// }
''',
                    "Turning colour off when output isn't a terminal is the convention users and CI logs expect, and testing the binary end to end with assert_cmd catches mistakes unit tests can't: wrong exit codes, help text, argument errors.",
                    ["Arguments are declared with clap derive and --help reads well", "Colour follows --color, and auto checks for a terminal", "An assert_cmd test checks piped output has no escape codes"])]},
    {"id": "A14.4", "t": "Networking beyond HTTP: UDP, hyper and QUIC", "min": 45,
     "learn": "Work below and beside HTTP frameworks: UDP sockets in the standard library, hyper as the HTTP engine under axum and reqwest, and QUIC (the transport under HTTP/3) with quinn, including when each is the right tool.",
     "example": {"title": "A UDP round trip on localhost", "code": r'''use std::net::UdpSocket;
use std::time::Duration;

fn main() -> std::io::Result<()> {
    // Port 0: let the operating system pick free ports, as tests should.
    let server = UdpSocket::bind("127.0.0.1:0")?;
    let client = UdpSocket::bind("127.0.0.1:0")?;
    server.set_read_timeout(Some(Duration::from_secs(2)))?;
    client.set_read_timeout(Some(Duration::from_secs(2)))?;

    client.send_to(b"ping 1", server.local_addr()?)?;

    let mut buf = [0u8; 512];
    let (n, from) = server.recv_from(&mut buf)?;
    let msg = String::from_utf8_lossy(&buf[..n]).to_string();
    println!("server got {msg:?}");
    server.send_to(msg.replace("ping", "pong").as_bytes(), from)?;

    let (n, _) = client.recv_from(&mut buf)?;
    println!("client got {:?}", String::from_utf8_lossy(&buf[..n]));
    println!("UDP has no connection: each datagram is addressed separately");
    Ok(())
}
''', "note": "UDP sends independent datagrams with no delivery or ordering guarantee, which suits metrics, games and discovery protocols. QUIC builds reliability, encryption (TLS 1.3) and multiple streams on top of UDP; quinn implements it on Tokio, and it's what HTTP/3 runs on. hyper is the HTTP implementation inside axum and reqwest: you reach for it directly only for proxies or unusual servers."},
     "ex": [text_ex("A14.4b", "A QUIC echo with quinn",
                    "Follow quinn's examples to build an echo server and client on localhost with a self-signed certificate (rcgen). The client opens one bidirectional stream per message. Then measure: send 1,000 small messages over one QUIC connection and over 1,000 new TCP connections, and compare the total time.",
                    ["quinn's repository has client.rs and server.rs examples to start from.", "rcgen::generate_simple_self_signed(vec![\"localhost\".into()]) creates a test certificate.", "Use std::time::Instant around each run, in release mode."],
                    r'''// Outline of the measurement (full quinn setup follows its examples):
//
// let start = Instant::now();
// for i in 0..1000 {
//     let (mut send, mut recv) = connection.open_bi().await?;
//     send.write_all(format!("msg {i}").as_bytes()).await?;
//     send.finish()?;
//     let reply = recv.read_to_end(1024).await?;
//     assert_eq!(reply, format!("msg {i}").as_bytes());
// }
// println!("QUIC, one connection: {:?}", start.elapsed());
//
// let start = Instant::now();
// for i in 0..1000 {
//     let mut tcp = TcpStream::connect(addr).await?;   // a new handshake every time
//     tcp.write_all(format!("msg {i}").as_bytes()).await?;
//     ...
// }
// println!("TCP, new connection each time: {:?}", start.elapsed());
''',
                    "Opening streams on one QUIC connection avoids a handshake per message, so it's usually much faster than new TCP connections; reusing one TCP connection would close most of the gap. Measuring it yourself, and explaining why, is the kind of concrete result that stands out in a performance-testing discussion.",
                    ["The echo server and client work on localhost", "Messages use one stream each on a single connection", "You measured both cases in release mode and wrote down the numbers and the reason"])]},
    {"id": "A14.5", "t": "Other runtimes: smol, async-std and Wasmer", "min": 40,
     "learn": "Know what an async runtime actually does and the alternatives to Tokio: smol (small and composable), async-std (discontinued in 2025, its authors point to smol) and the futures crate's executor; and run WebAssembly modules from Rust with Wasmer or Wasmtime.",
     "example": {"title": "What a runtime does, in 30 lines", "code": r'''use std::future::Future;
use std::pin::pin;
use std::sync::Arc;
use std::task::{Context, Poll, Wake, Waker};
use std::thread::{self, Thread};

/// A waker that unparks the thread running block_on.
struct ThreadWaker(Thread);
impl Wake for ThreadWaker {
    fn wake(self: Arc<Self>) {
        self.0.unpark();
    }
}

/// The heart of every runtime: poll, and sleep until woken.
fn block_on<F: Future>(fut: F) -> F::Output {
    let mut fut = pin!(fut);
    let waker = Waker::from(Arc::new(ThreadWaker(thread::current())));
    let mut cx = Context::from_waker(&waker);
    let mut polls = 0;
    loop {
        polls += 1;
        if let Poll::Ready(v) = fut.as_mut().poll(&mut cx) {
            println!("finished after {polls} poll(s)");
            return v;
        }
        thread::park();
    }
}

async fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn main() {
    let total = block_on(async { add(2, 3).await + add(10, 20).await });
    println!("total = {total}");
}
''', "note": "Real runtimes add a scheduler for many tasks, timers, and an I/O reactor (epoll, kqueue or IOCP) that wakes tasks when sockets are ready. smol packages those pieces as small crates (async-executor, async-io), which is why it's popular for libraries and embedded Linux. A WebAssembly runtime like Wasmer or Wasmtime is a different kind of runtime: it runs compiled .wasm modules in a sandbox inside your program."},
     "ex": [text_ex("A14.5b", "Run a WebAssembly plugin from Rust",
                    "Compile a tiny Rust function (fn score(n: i32) -> i32) to wasm32-unknown-unknown, then load and call it from a host program with Wasmer or Wasmtime. Add a test that the host rejects a module that doesn't export score, instead of panicking.",
                    ["rustup target add wasm32-unknown-unknown; build the plugin as a cdylib with #[no_mangle] pub extern \"C\" fn score.", "Wasmtime: Engine, Module::from_file, Linker, instance.get_typed_func::<i32, i32>(&mut store, \"score\").", "get_typed_func returns an error for a missing export: map it to your own error type."],
                    r'''// plugin/src/lib.rs   (crate-type = ["cdylib"])
#[unsafe(no_mangle)]
pub extern "C" fn score(n: i32) -> i32 {
    n * 10
}

// host/src/main.rs   (wasmtime = "...")
use wasmtime::{Engine, Instance, Module, Store};

fn call_score(path: &str, n: i32) -> Result<i32, String> {
    let engine = Engine::default();
    let module = Module::from_file(&engine, path).map_err(|e| e.to_string())?;
    let mut store = Store::new(&engine, ());
    let instance = Instance::new(&mut store, &module, &[]).map_err(|e| e.to_string())?;
    let score = instance
        .get_typed_func::<i32, i32>(&mut store, "score")
        .map_err(|_| String::from("plugin does not export score(i32) -> i32"))?;
    score.call(&mut store, n).map_err(|e| e.to_string())
}
''',
                    "WebAssembly gives plugins a sandbox: the module can only touch what the host passes in, so a buggy or hostile plugin can't read your files. Wasmer and Wasmtime have similar APIs; checking for missing exports and turning them into errors is what keeps the host robust.",
                    ["The plugin builds to .wasm and the host calls score", "A missing export produces an error, not a panic", "You can explain why a WebAssembly plugin is safer than loading a native library"])]},
    {"id": "A14.6", "t": "Games and graphics: Bevy, macroquad, ggez, Fyrox, wgpu", "min": 45,
     "learn": "Survey Rust game development: Bevy's entity-component-system engine, the simpler macroquad and ggez for 2D games, Fyrox as a full engine with an editor, and wgpu as the portable graphics layer beneath many of them; and keep game logic testable without a window.",
     "example": {"title": "A Bevy system and a macroquad loop", "check": "none", "code": r'''// Bevy: data in components, logic in systems that query them.
use bevy::prelude::*;

#[derive(Component)]
struct Velocity(Vec2);

fn movement(time: Res<Time>, mut query: Query<(&mut Transform, &Velocity)>) {
    for (mut transform, velocity) in &mut query {
        transform.translation += velocity.0.extend(0.0) * time.delta_secs();
    }
}

fn main() {
    App::new().add_plugins(DefaultPlugins).add_systems(Update, movement).run();
}

// macroquad: an immediate-mode loop, closer to a classic game loop.
//
// #[macroquad::main("Bounce")]
// async fn main() {
//     let mut x = 0.0;
//     loop {
//         clear_background(BLACK);
//         x = (x + 200.0 * get_frame_time()) % screen_width();
//         draw_circle(x, 120.0, 15.0, YELLOW);
//         next_frame().await
//     }
// }
''', "note": "Bevy moves fast and renames things between releases (delta_seconds became delta_secs, for example), so check the version of any tutorial against the crate you use. macroquad and ggez suit small 2D games and game jams; Fyrox ships a scene editor; wgpu is the cross-platform GPU API (Vulkan, Metal, DirectX, WebGPU) that Bevy renders with."},
     "ex": [text_ex("A14.6b", "A small game with tested logic",
                    "Make a one-screen game with macroquad (or Bevy): a player moving with the arrow keys and items to collect. Keep the rules (movement, collisions, score) in plain functions or systems that don't touch the window, and unit-test them, including an item exactly at the collision distance.",
                    ["Separate update(state, input, dt) from draw(state): only draw calls macroquad.", "A collision test is a distance check: (dx * dx + dy * dy) <= r * r.", "Run cargo test without opening a window; the game itself runs with cargo run."],
                    r'''pub struct State {
    pub player: (f32, f32),
    pub items: Vec<(f32, f32)>,
    pub score: u32,
}

pub fn update(state: &mut State, dir: (f32, f32), dt: f32) {
    state.player.0 += dir.0 * 150.0 * dt;
    state.player.1 += dir.1 * 150.0 * dt;
    let (px, py) = state.player;
    let before = state.items.len();
    state.items.retain(|&(x, y)| (x - px).powi(2) + (y - py).powi(2) > 20.0 * 20.0);
    state.score += (before - state.items.len()) as u32;
}

#[test]
fn collecting_at_exactly_the_radius_counts() {
    let mut s = State { player: (0.0, 0.0), items: vec![(20.0, 0.0), (50.0, 0.0)], score: 0 };
    update(&mut s, (0.0, 0.0), 0.016);
    assert_eq!(s.score, 1);
    assert_eq!(s.items, vec![(50.0, 0.0)]);
}
''',
                    "Games are hard to test through the screen, so the professional habit is to keep rules pure and test them like any other code. The boundary test (an item exactly at the radius) is where off-by-one bugs live, in games as everywhere else.",
                    ["The game runs and the score increases", "Movement and collisions live in functions that don't draw", "Unit tests cover collecting, missing, and the exact-radius case"])]},
    {"id": "A14.7", "t": "Embedded Rust: no_std, embedded-hal, nrf-hal and rppal", "min": 50,
     "learn": "Understand embedded Rust: #![no_std] and what's left without the standard library, the embedded-hal traits that make drivers portable, chip support crates such as nrf-hal, flashing and debugging with probe-rs, and rppal for GPIO on a Raspberry Pi running Linux.",
     "example": {"title": "Blinking an LED on a Raspberry Pi with rppal", "check": "none", "code": r'''// Runs on a Raspberry Pi (Linux, so std is available). Cargo.toml: rppal = "0.19"
use rppal::gpio::Gpio;
use std::error::Error;
use std::thread;
use std::time::Duration;

const LED_PIN: u8 = 23; // BCM numbering

fn main() -> Result<(), Box<dyn Error>> {
    let mut led = Gpio::new()?.get(LED_PIN)?.into_output();
    for _ in 0..5 {
        led.set_high();
        thread::sleep(Duration::from_millis(300));
        led.set_low();
        thread::sleep(Duration::from_millis(300));
    }
    Ok(())
}

// On a microcontroller (an nRF52 board, for example) there is no operating system:
//
// #![no_std]
// #![no_main]
// use cortex_m_rt::entry;
// use embedded_hal::digital::OutputPin;   // the portable trait
// use panic_halt as _;
//
// #[entry]
// fn main() -> ! {
//     let p = nrf52840_hal::pac::Peripherals::take().unwrap();
//     let port0 = nrf52840_hal::gpio::p0::Parts::new(p.P0);
//     let mut led = port0.p0_13.into_push_pull_output(nrf52840_hal::gpio::Level::High);
//     loop { led.set_low().unwrap(); /* delay */ led.set_high().unwrap(); }
// }
''', "note": "On a Pi you have Linux and std, so rppal is just a crate. On a microcontroller, #![no_std] leaves core and (optionally) alloc, the entry point never returns, and a HAL crate like nrf-hal implements embedded-hal's traits for that chip. probe-rs flashes and debugs boards over a debug probe, and the Wokwi simulator lets you try much of this without hardware."},
     "ex": [text_ex("A14.7b", "Drive real or simulated hardware",
                    "Run your Blinker from the previous exercise on real hardware: either a Raspberry Pi with an LED on a GPIO pin (implement your OutputPin trait for rppal's OutputPin), or a simulated board in Wokwi with an embedded-hal pin. Keep the mock-based tests passing on your laptop.",
                    ["An adapter struct wrapping rppal::gpio::OutputPin can implement your trait in a few lines.", "Wokwi has Rust templates for ESP32 and Raspberry Pi Pico boards.", "Keep the hardware-specific code in main.rs and the Blinker in lib.rs, so cargo test runs anywhere."],
                    r'''// src/main.rs on a Raspberry Pi
use blinker::{Blinker, OutputPin};

struct PiPin(rppal::gpio::OutputPin);

impl OutputPin for PiPin {
    fn set_high(&mut self) {
        self.0.set_high();
    }
    fn set_low(&mut self) {
        self.0.set_low();
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let pin = rppal::gpio::Gpio::new()?.get(23)?.into_output();
    let mut blinker = Blinker::new(PiPin(pin));
    blinker.blink(5); // add a delay between toggles in toggle() or here for a visible blink
    Ok(())
}
''',
                    "A thin adapter is all the real hardware needs, because the driver only depends on the trait. Hardware-in-the-loop testing in industry follows the same split: most tests run against mocks in CI, and a smaller suite runs on real boards.",
                    ["The driver runs on a Pi or in a simulator", "The hardware adapter is a few lines implementing the trait", "The mock-based tests still pass with cargo test on your laptop"])]},
    {"id": "A14.8", "t": "Desktop apps: Tauri, gtk-rs, relm4 and gpui", "min": 40,
     "learn": "Choose a way to build desktop GUIs in Rust: Tauri (a web front end with a Rust back end), gtk-rs and its Elm-style layer relm4 for native GTK apps, gpui (the GPU-accelerated framework behind the Zed editor), and pure-Rust toolkits such as egui and iced.",
     "example": {"title": "A Tauri command called from the web front end", "check": "none", "code": r'''// src-tauri/src/lib.rs
#[tauri::command]
fn search(query: &str, text: &str) -> Vec<String> {
    text.lines().filter(|l| l.contains(query)).map(String::from).collect()
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![search])
        .run(tauri::generate_context!())
        .expect("error while running the app");
}

// In the front end (JavaScript or TypeScript):
//
// import { invoke } from "@tauri-apps/api/core";
// const lines = await invoke("search", { query: "to", text: poem });
''', "note": "Tauri apps are small because they use the operating system's web view instead of bundling a browser, and the front end can only call the commands you register. gtk-rs gives native Linux-first widgets, with relm4 adding an Elm-style update/view structure; gpui powers Zed and suits fast, GPU-drawn tools; egui (immediate mode) and iced (Elm-style) are pure Rust and easy to start with."},
     "ex": [text_ex("A14.8b", "A desktop front end for one of your projects",
                    "Give kvlog or testlens a small desktop window with Tauri or egui: a search box, a results list and an error message area. Keep the logic in your existing library crate, call it from the GUI layer, and write one end-to-end test of the command layer (the Tauri command or the egui app's update function) without opening a window.",
                    ["Tauri: put your library in the workspace and call it from #[tauri::command] functions.", "egui: eframe::run_native with a struct implementing eframe::App; logic goes in plain methods you can test.", "Return Result from commands so the UI can show errors instead of crashing."],
                    r'''// Tauri command layer around an existing library
#[tauri::command]
fn get_key(state: tauri::State<'_, std::sync::Mutex<kvlog::Store>>, key: String) -> Result<Option<String>, String> {
    let store = state.lock().map_err(|_| "store is unavailable".to_string())?;
    store.get(&key).map_err(|e| e.to_string())
}

#[test]
fn missing_key_is_none() {
    let store = kvlog::Store::open_temp().unwrap();
    assert_eq!(store.get("nope").unwrap(), None);
}
''',
                    "Keeping the GUI as a thin layer over a tested library is the same rule as the PyO3 wrapper and the hardware adapter: the parts that are hard to test stay small. A desktop front end also makes a portfolio project far easier to demo in an interview.",
                    ["The window searches and shows results from your library", "Errors appear in the UI instead of crashing", "The logic is tested without opening a window"])]},
]

QUIZ = [
    {"q": "Why compare a secret token in constant time?", "o": ["An early-exit comparison leaks, through timing, how many leading bytes were right", "It's faster for long tokens", "== doesn't work on byte slices", "To use less memory"], "a": 0, "x": "Timing differences let an attacker recover a secret byte by byte."},
    {"q": "What happened to structopt?", "o": ["Its derive approach was adopted by clap, and structopt now points users to clap's derive API", "It was renamed to termion", "It became part of the standard library", "It only works on nightly"], "a": 0, "x": "clap 3 and later include the derive API that structopt pioneered."},
    {"q": "Which terminal crate works on Windows as well as Unix?", "o": ["crossterm", "termion", "rppal", "nrf-hal"], "a": 0, "x": "termion is Unix-only; crossterm is cross-platform and is ratatui's default back end."},
    {"q": "What does QUIC (implemented by quinn) run on?", "o": ["UDP, adding reliability, encryption and multiple streams", "TCP with a new header", "Raw Ethernet frames", "WebSockets"], "a": 0, "x": "QUIC is the transport under HTTP/3, built on UDP."},
    {"q": "What is the core loop of an async runtime?", "o": ["Poll a future, and sleep until a waker says it can make progress", "Run every future on its own OS thread", "Compile futures into threads at build time", "Call each future exactly once"], "a": 0, "x": "Wakers tell the executor when polling again is worthwhile.", "pool": "exam"},
    {"q": "Why do embedded Rust drivers depend on embedded-hal traits instead of a specific chip crate?", "o": ["So one driver works on any chip with a HAL, and can be tested against mocks", "Because chip crates can't be used with no_std", "embedded-hal makes code run faster", "It's required by cargo"], "a": 0, "x": "The traits decouple drivers from hardware."},
    {"q": "Why are Tauri apps usually much smaller than Electron apps?", "o": ["They use the operating system's web view instead of bundling a browser", "They don't support JavaScript", "They compress the binary", "They only run on Linux"], "a": 0, "x": "Tauri relies on WebView2, WKWebView or WebKitGTK."},
    {"q": "In Bevy's ECS, where does game logic live?", "type": "multi", "o": ["In systems: functions that query components", "In components, as methods on the data", "In plain functions you can test without a window, if you design it that way", "Only in the renderer"], "a": [0, 2], "x": "Components hold data; systems hold behaviour.", "pool": "exam"},
]

MODULE = {
    "id": "a14", "n": "A14", "t": "The wider ecosystem: roadmap extras", "lv": 3,
    "goal": "Cover the roadmap.sh/rust topics the other modules only mention: cryptography, more web frameworks, CLI and terminal crates, networking beyond HTTP, other runtimes, games and graphics, embedded, and desktop GUIs.",
    "res": "roadmap.sh Rust roadmap | https://roadmap.sh/rust\nring | https://docs.rs/ring\nRustCrypto | https://github.com/RustCrypto\nactix-web | https://actix.rs/\nRocket | https://rocket.rs/\nLoco | https://loco.rs/\nclap derive tutorial | https://docs.rs/clap/latest/clap/_derive/_tutorial/index.html\nratatui | https://ratatui.rs/\nquinn | https://github.com/quinn-rs/quinn\nsmol | https://github.com/smol-rs/smol\nWasmtime | https://docs.wasmtime.dev/\nWasmer | https://wasmer.io/\nBevy | https://bevyengine.org/\nmacroquad | https://macroquad.rs/\nThe Embedded Rust Book | https://docs.rust-embedded.org/book/\nrppal | https://github.com/golemparts/rppal\nTauri | https://tauri.app/\ngtk-rs | https://gtk-rs.org/",
    "quiz": QUIZ,
    "recap": {"summary": [
        "Use vetted crypto crates (RustCrypto, ring) and compare secrets in constant time; sodiumoxide is archived.",
        "actix-web, Rocket and Loco solve the same problems as axum in different styles; port one route to compare.",
        "clap's derive API replaced structopt; colour only when writing to a terminal; crossterm is the cross-platform terminal crate.",
        "UDP for independent datagrams, QUIC (quinn) for reliable encrypted streams over UDP, hyper underneath HTTP frameworks.",
        "A runtime polls futures and sleeps until woken; smol is the lightweight alternative now that async-std is discontinued; Wasmer and Wasmtime run WebAssembly plugins in a sandbox.",
        "Bevy keeps data in components and logic in systems; keep game rules testable without a window.",
        "Embedded drivers target embedded-hal traits, so they run on any chip and test against mocks; rppal drives a Raspberry Pi's GPIO.",
        "Tauri, gtk-rs/relm4, gpui, egui and iced cover desktop apps; keep the GUI a thin layer over a tested library."],
        "functions": "Sha256::digest(data) || A SHA-256 hash (RustCrypto sha2).\nHmac::<Sha256>::new_from_slice(key) || A keyed signature; verify with verify_slice.\n#[derive(Parser)] || A command-line parser from a struct (clap).\nstd::io::stdout().is_terminal() || Whether output goes to a terminal.\nUdpSocket::bind(\"127.0.0.1:0\") || A UDP socket on a free port.\nQuery<(&mut Transform, &Velocity)> || A Bevy system's view of components.\nGpio::new()?.get(23)?.into_output() || An output pin on a Raspberry Pi (rppal).\n#[tauri::command] || A Rust function the Tauri front end can call.",
        "next": "Pick the area closest to the jobs you want and build one Track 3-sized project in it."},
    "items": [],
}


def main():
    for L in LESSONS:
        eg = dict(L["example"])
        eg.setdefault("lang", "rust")
        if eg.get("check") != "none":
            eg["output"] = run(eg["code"])
            eg["check"] = "run"
        MODULE["items"].append({"id": L["id"], "t": L["t"], "min": L["min"], "learn": L["learn"], "example": eg, "ex": L["ex"]})
    with open(os.path.join(HERE, "content", "a5.yaml"), "w", encoding="utf-8") as f:
        yaml.safe_dump([MODULE], f, allow_unicode=True, sort_keys=False, width=100000)
    print("wrote content/a5.yaml:", len(LESSONS), "lessons")
    for L in LESSONS:
        if L["example"].get("check") != "none":
            print("---", L["id"])
            print(run(L["example"]["code"]))


if __name__ == "__main__":
    main()
