#!/usr/bin/env python3
"""Build expanded Rust lessons: parse deep/rs/*.txt, compile and run every example, write rust/deep.json.

Authoring format (same as the Python course):
  === ID
  @idea / @how / @mistakes / @keys
  @example LANG [MODE]: Title      LANG = rust | bash | toml | text
                                   MODE = run (default) | build | test | fail | norun
  @deps rand@0.8, serde@1+derive   (optional, after an example: crates for cargo)
  @stdin ...                       (optional input for run mode)
  @output ...                      (for norun / non-rust: shown as "Sample output")
  @note ...
Outputs:
  run   -> stdout + stderr of the program (a panic message included)
  test  -> the test runner's summary lines
  fail  -> the compiler's error lines (must fail to compile)
  build -> compile only; @output, if given, is shown as sample output
"""
import hashlib, json, os, re, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "_deep")
CACHE = os.path.join(WORK, "cache.json")
os.makedirs(WORK, exist_ok=True)
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
SECTIONS = r"idea|how|example|deps|stdin|output|note|mistakes|keys"


def parse_file(path):
    lessons = {}
    text = open(path, encoding="utf-8").read()
    for block in re.split(r"^=== ", text, flags=re.M)[1:]:
        head, _, body = block.partition("\n")
        lid = head.strip()
        secs = re.split(rf"^@({SECTIONS})(?:[ \t]+(.*))?$", body, flags=re.M)
        les = {"idea": [], "how": [], "examples": [], "mistakes": [], "keys": []}
        k = 1
        while k < len(secs):
            name, arg, content = secs[k], (secs[k + 1] or "").strip(), secs[k + 2].strip("\n")
            k += 3
            if name == "idea":
                les["idea"] = [re.sub(r"\s*\n\s*", " ", p.strip()) for p in re.split(r"\n\s*\n", content) if p.strip()]
            elif name in ("how", "mistakes", "keys"):
                les[name] = [re.sub(r"\s*\n\s*", " ", b.strip()) for b in re.split(r"^- ", content, flags=re.M) if b.strip()]
            elif name == "example":
                m = re.match(r"(\w+)((?:\s+\w+)*)\s*:\s*(.*)$", arg)
                if not m:
                    raise ValueError(f"{lid}: bad @example header {arg!r}")
                flags = m.group(2).split()
                mode = next((f for f in flags if f in ("run", "build", "test", "fail", "norun")), "run")
                les["examples"].append({"lang": m.group(1), "title": m.group(3).strip(), "code": content.rstrip(),
                                        "mode": mode, "deps": [], "stdin": "", "note": "", "output": ""})
            elif name == "deps":
                les["examples"][-1]["deps"] = [d.strip() for d in arg.split(",") if d.strip()]
            elif name == "stdin":
                les["examples"][-1]["stdin"] = content + "\n"
            elif name == "output":
                les["examples"][-1]["output"] = content.rstrip()
                les["examples"][-1]["sample"] = True
            elif name == "note":
                les["examples"][-1]["note"] = re.sub(r"\s*\n\s*", " ", content.strip())
        lessons[lid] = les
    return lessons


def sh(cmd, cwd, timeout=120, stdin="", merge=False):
    try:
        p = subprocess.run(cmd, cwd=cwd, input=stdin, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT if merge else subprocess.PIPE, text=True, timeout=timeout,
                           env={**os.environ, "RUST_BACKTRACE": "0", "CARGO_TERM_COLOR": "never"})
        return p.returncode, p.stdout, p.stderr or ""
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def cargo_dir(deps):
    key = hashlib.md5(",".join(sorted(deps)).encode()).hexdigest()[:10]
    d = os.path.join(WORK, "cargo_" + key)
    if not os.path.exists(os.path.join(d, "Cargo.toml")):
        os.makedirs(os.path.join(d, "src"), exist_ok=True)
        lines = ["[package]", 'name = "example"', 'version = "0.1.0"', 'edition = "2024"', "", "[dependencies]"]
        for dep in deps:
            name, ver = dep.split("@")
            feats = ver.split("+")[1:]
            ver = ver.split("+")[0]
            lines.append(f'{name} = {{ version = "{ver}", features = {json.dumps(feats)} }}' if feats else f'{name} = "{ver}"')
        open(os.path.join(d, "Cargo.toml"), "w").write("\n".join(lines) + "\n")
    return d


def compiler_errors(text, limit=11):
    """The first error with its local source pointers; library internals and noise dropped."""
    keep, skip = [], False
    for line in text.splitlines():
        line = line.rstrip()
        stripped = line.strip()
        if stripped.startswith("-->"):
            local = re.search(r"(main|lib)\.rs:\d+", line)
            skip = not local
            if local:
                keep.append(re.sub(r"-->\s*\S*?((?:main|lib)\.rs)", r"--> \1", line))
            continue
        if line.startswith("error") or line.startswith("warning: unused") or stripped.startswith(("= note", "= help", "help:")):
            if line.startswith("error") and keep and (line.startswith("error[") or line.startswith("error: ")):
                if any(k.startswith("error") for k in keep):
                    break                                  # only the first error
            skip = stripped.startswith("= note: this error originates")
            if not skip:
                keep.append(line)
            continue
        if re.match(r"^\s*(\d+\s*)?\|", line) and not skip:
            if re.match(r"^\s*\|\s*$", line) and keep and re.match(r"^\s*\|\s*$", keep[-1]):
                continue
            keep.append(line)
    while keep and re.match(r"^\s*\|\s*$", keep[-1]):
        keep.pop()
    if len(keep) > limit:
        keep = keep[:limit] + ["  ..."]
    out = "\n".join(keep)
    out = re.sub(r"\n?error: aborting due to.*", "", out)
    return out.strip()


def test_summary(text):
    lines = [l for l in text.splitlines() if l.startswith(("test ", "running ")) or "test result:" in l or l.startswith("---- ")
             or l.strip().startswith(("thread '", "assertion", "  left:", " right:", "left:", "right:"))]
    out = re.sub(r"; finished in [\d.]+s", "", "\n".join(lines)).strip()
    return re.sub(r"thread '([^']*)' \(\d+\) panicked", r"thread '\1' panicked", out)


def tidy_run(o, e):
    out = (o + ("\n" if o and e and not o.endswith("\n") else "") + e).rstrip()
    return re.sub(r"thread '([^']*)' \(\d+\) panicked", r"thread '\1' panicked", out)


def run_example(lid, k, ex):
    lang, mode, code = ex["lang"], ex["mode"], ex["code"]
    if lang != "rust" or mode == "norun":
        return lid, k, ex.get("output", ""), None
    h = hashlib.md5(json.dumps([mode, ex["deps"], ex["stdin"], code]).encode()).hexdigest()
    if h in cache:
        return lid, k, cache[h], None
    has_main = re.search(r"^\s*(async\s+)?fn main\s*\(", code, re.M) is not None
    if ex["deps"]:
        d = cargo_dir(ex["deps"])
        import fcntl
        with open(d + ".lock", "w") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            src = os.path.join(d, "src")
            for f in os.listdir(src):
                os.remove(os.path.join(src, f))
            open(os.path.join(src, "main.rs" if has_main else "lib.rs"), "w").write(code)
            tgt = ["--target-dir", os.path.join(WORK, "target")]
            if mode == "fail":
                rc, o, e = sh(["cargo", "build", "-q"] + tgt, d, 900)
                if rc == 0:
                    return lid, k, None, "expected a compile error"
                out = compiler_errors(e)
            elif mode == "test":
                rc, o, e = sh(["cargo", "test", "-q", "--lib" if not has_main else "--bins"] + tgt + ["--", "--format", "pretty", "--test-threads", "1"], d, 900)
                out = test_summary(o + e)
                if "test result:" not in out:
                    return lid, k, None, (o + e)[-2500:]
            else:
                rc, o, e = sh(["cargo", "build", "-q"] + tgt, d, 900)
                if rc != 0:
                    return lid, k, None, e[-2500:]
                if mode == "build":
                    out = ex.get("output", "")
                else:
                    rc, o, e = sh([os.path.join(WORK, "target", "debug", "example")], d, 60, ex["stdin"], merge=True)
                    out = tidy_run(o, e)
                    if rc == 124:
                        return lid, k, None, "timeout"
    else:
        d = os.path.join(WORK, "s_" + h[:12])
        os.makedirs(d, exist_ok=True)
        fname = "main.rs" if has_main else "lib.rs"
        open(os.path.join(d, fname), "w").write(code)
        base = ["rustc", "--edition", "2024", "-A", "dead_code", "-A", "unused", fname]
        if mode == "fail":
            extra = ["--test", "-o", "tests"] if "#[test]" in code else (["-o", "prog"] if has_main else ["--crate-type", "lib"])
            rc, o, e = sh(base + extra, d)
            if rc == 0:
                return lid, k, None, "expected a compile error"
            out = compiler_errors(e)
        elif mode == "test":
            rc, o, e = sh(base + ["--test", "-o", "tests"], d)
            if rc != 0:
                return lid, k, None, e[-2500:]
            rc, o, e = sh(["./tests", "--test-threads", "1"], d, 60)
            out = test_summary(o + e)
        else:
            rc, o, e = sh(base + (["-o", "prog"] if has_main else ["--crate-type", "lib"]), d)
            if rc != 0:
                return lid, k, None, e[-2500:]
            if mode == "build" or not has_main:
                out = ex.get("output", "")
            else:
                rc, o, e = sh(["./prog"], d, 15, ex["stdin"], merge=True)
                if rc == 124:
                    return lid, k, None, "timeout"
                out = tidy_run(o, e)
        shutil.rmtree(d, ignore_errors=True)
    cache[h] = out
    return lid, k, out, None


def main():
    files = sorted(sys.argv[1:]) or sorted(__import__("glob").glob(os.path.join(HERE, "..", "deep", "rs", "*.txt")))
    lessons = {}
    for f in files:
        lessons.update(parse_file(f))
    jobs = [(lid, k, ex) for lid, les in lessons.items() for k, ex in enumerate(les["examples"])]
    plain = [j for j in jobs if not j[2]["deps"]]
    deps = [j for j in jobs if j[2]["deps"]]
    results = []
    with ThreadPoolExecutor(6) as pool:
        results += list(pool.map(lambda j: run_example(*j), plain))
    for j in deps:
        results.append(run_example(*j))
    json.dump(cache, open(CACHE, "w"))
    problems = []
    for lid, k, out, err in results:
        ex = lessons[lid]["examples"][k]
        if err:
            problems.append(f"PROBLEM {lid} example {k + 2}: {err[-1500:]}")
            continue
        ex["output"] = re.sub(r"thread '([^']*)' \(\d+\) panicked", r"thread '\1' panicked", out or "")
        if ex["lang"] == "rust" and ex["mode"] == "fail":
            ex["label"] = "Compiler output"
        elif ex["lang"] == "rust" and ex["mode"] == "test":
            ex["label"] = "cargo test output"
        if ex["lang"] == "rust" and ex["mode"] not in ("norun", "build"):
            ex.pop("sample", None)
        if ex["mode"] == "run" and "panicked" in out and "panic" not in ex["note"].lower():
            problems.append(f"PROBLEM {lid} example {k + 2}: panicked but the note does not mention it")
    for les in lessons.values():
        for ex in les["examples"]:
            ex["lang"] = {"text": "plaintext"}.get(ex["lang"], ex["lang"])
            for key in ("mode", "deps", "stdin"):
                ex.pop(key, None)
    json.dump(lessons, open(os.path.join(HERE, "deep.json"), "w"), ensure_ascii=False, indent=0)
    words = sum(len(" ".join(l["idea"] + l["how"] + l["mistakes"] + l["keys"]).split()) for l in lessons.values())
    print(f"{len(lessons)} Rust lessons built, {words} words, {len(jobs)} examples")
    print("\n".join(problems))


if __name__ == "__main__":
    main()
