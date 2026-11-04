#!/usr/bin/env python3
"""Compile (and where sensible run/test) every Rust snippet in the course YAML.

usage: verify.py content/f1.yaml [more.yaml ...] [--only ID-prefix]
check modes per snippet:
  (default)  run: compile as a binary and run with empty stdin (5 s limit);
             a snippet without fn main is compiled as a library
  build      compile only (programs that wait for input or loop forever)
  test       compile and run its #[cfg(test)] tests (plus build the binary)
  fail       must NOT compile (intentional error demos)
  none       skip (shell, toml, multi-file sketches)
deps: ["rand@0.8", ...] -> built with cargo in a shared workspace
"""
import hashlib, json, os, re, shutil, subprocess, sys, yaml
from load import load
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "_verify")
CACHE = os.path.join(WORK, "cache.json")
os.makedirs(WORK, exist_ok=True)
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}


def snippets(mods):
    for m in mods:
        for it in m.get("items", []):
            eg = it.get("example")
            if eg:
                yield f"{it['id']} example", eg
            for k, e in enumerate(it.get("ex", [])):
                yield f"{it['id']}{'abc'[k]} solution", e


def run(cmd, cwd, timeout=120, stdin=""):
    try:
        p = subprocess.run(cmd, cwd=cwd, input=stdin, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return 124, "timeout"


def cargo_dir(deps):
    key = hashlib.md5(",".join(sorted(deps)).encode()).hexdigest()[:10]
    d = os.path.join(WORK, "cargo_" + key)
    if not os.path.exists(os.path.join(d, "Cargo.toml")):
        os.makedirs(os.path.join(d, "src"), exist_ok=True)
        lines = ["[package]", 'name = "snip"', 'version = "0.1.0"', 'edition = "2024"', "", "[dependencies]"]
        for dep in deps:
            if "=" in dep:
                lines.append(dep)
            else:
                n, v = dep.split("@")
                lines.append(f'{n} = "{v}"')
        open(os.path.join(d, "Cargo.toml"), "w").write("\n".join(lines) + "\n")
    return d


def check_one(name, s):
    lang = s.get("lang", "rust")
    mode = s.get("check", "run")
    code = s.get("code") or s.get("solution") or ""
    if lang != "rust" or mode == "none" or not code.strip():
        return name, "skip", ""
    deps = s.get("deps") or []
    h = hashlib.md5((mode + "|" + ",".join(deps) + "|" + code).encode()).hexdigest()
    if cache.get(h) == "ok":
        return name, "ok", "(cached)"
    has_main = re.search(r"^\s*(async\s+)?fn main\s*\(", code, re.M) is not None or "#[tokio::main]" in code
    has_tests = "#[test]" in code or "#[tokio::test]" in code
    if deps:
        d = cargo_dir(deps)
        lock = d + ".lock"
        # one cargo project per dep set: serialize access
        import fcntl
        with open(lock, "w") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            src = os.path.join(d, "src")
            for f in os.listdir(src):
                os.remove(os.path.join(src, f))
            fname = "main.rs" if has_main else "lib.rs"
            open(os.path.join(src, fname), "w").write(code)
            env_target = ["--target-dir", os.path.join(WORK, "target")]
            if mode == "fail":
                rc, out = run(["cargo", "build", "-q"] + env_target, d, 600)
                res = ("ok", "") if rc != 0 else ("FAIL", "expected a compile error but it compiled")
            else:
                rc, out = run(["cargo", "build", "-q"] + env_target, d, 900)
                if rc != 0:
                    res = ("FAIL", out[-3000:])
                elif has_tests or mode == "test":
                    rc, out = run(["cargo", "test", "-q"] + env_target, d, 900)
                    res = ("ok", "") if rc == 0 else ("FAIL", out[-3000:])
                elif mode == "run" and has_main:
                    rc, out = run(["cargo", "run", "-q"] + env_target, d, 60)
                    res = ("ok", "") if rc in (0,) else ("FAIL", out[-3000:])
                else:
                    res = ("ok", "")
    else:
        d = os.path.join(WORK, "s_" + h[:12])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "s.rs"), "w").write(code)
        base = ["rustc", "--edition", "2024", "-A", "dead_code", "-A", "unused", "s.rs"]
        if mode == "fail":
            rc, out = run(base + ["--crate-type", "lib" if not has_main else "bin", "-o", "s"], d)
            res = ("ok", "") if rc != 0 else ("FAIL", "expected a compile error but it compiled")
        else:
            rc, out = run(base + (["-o", "s"] if has_main else ["--crate-type", "lib"]), d)
            if rc != 0:
                res = ("FAIL", out[-3000:])
            elif has_tests or mode == "test":
                rc, out = run(base + ["--test", "-o", "t"], d)
                if rc == 0:
                    rc, out = run(["./t", "-q"], d, 60)
                res = ("ok", "") if rc == 0 else ("FAIL", out[-3000:])
            elif mode == "run" and has_main:
                rc, out = run(["./s"], d, 10)
                res = ("ok", "") if rc == 0 else ("FAIL", f"exit {rc}\n" + out[-3000:])
            else:
                res = ("ok", "")
        shutil.rmtree(d, ignore_errors=True)
    if res[0] == "ok":
        cache[h] = "ok"
    return name, res[0], res[1]


def main():
    files = [a for a in sys.argv[1:] if a.endswith(".yaml")]
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else ""
    todo = []
    for f in files:
        mods = load(f)
        for name, s in snippets(mods):
            if not only or name.startswith(only):
                todo.append((name, s))
    nodeps = [t for t in todo if not t[1].get("deps")]
    withdeps = [t for t in todo if t[1].get("deps")]
    results = []
    with ThreadPoolExecutor(8) as ex:
        results += list(ex.map(lambda t: check_one(*t), nodeps))
    for t in withdeps:
        results.append(check_one(*t))
    json.dump(cache, open(CACHE, "w"))
    bad = [r for r in results if r[1] == "FAIL"]
    ok = sum(1 for r in results if r[1] == "ok")
    skip = sum(1 for r in results if r[1] == "skip")
    for name, st, out in bad:
        print("=" * 70)
        print("FAIL", name)
        print(out)
    print(f"\n{ok} ok, {skip} skipped, {len(bad)} failed")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
