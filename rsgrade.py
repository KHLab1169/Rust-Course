"""Grade a Rust exercise: compile the learner's code with a hidden test module and run it.

Used by start.py (the local app) and by the authoring harness. Needs rustc on the PATH;
clippy-driver is optional and only feeds the style notes.

grade(code, spec) -> {"tests": [{name, ok, msg, detail}], "error": str, "errline": int}
style(code)       -> [{"line": n, "msg": text}]
"""
import json
import os
import re
import shutil
import subprocess
import tempfile

EDITION = "2024"
RUN_SECONDS = 10


def tool(name):
    path = shutil.which(name)
    if path:
        return path
    home = os.path.join(os.path.expanduser("~"), ".cargo", "bin", name + (".exe" if os.name == "nt" else ""))
    return home if os.path.exists(home) else None


def status():
    rustc = tool("rustc")
    if not rustc:
        return {"rust": False}
    try:
        ver = subprocess.run([rustc, "--version"], capture_output=True, text=True, timeout=20).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return {"rust": False}
    return {"rust": True, "version": ver, "clippy": bool(tool("clippy-driver"))}


def fn_name(i, name):
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")[:40] or "case"
    return f"t{i + 1:02d}_{slug}"


def test_module(spec):
    """The hidden tests, as Rust source to append to the learner's code."""
    parts = ["", "#[cfg(test)]", "#[allow(unused_imports, clippy::all)]", "mod grader_tests {", "    use super::*;"]
    for h in spec.get("prelude", "").splitlines():
        parts.append("    " + h)
    for i, case in enumerate(spec["cases"]):
        parts.append("")
        parts.append("    #[test]")
        if case.get("attrs"):
            parts.append("    " + case["attrs"])
        parts.append(f"    fn {fn_name(i, case['name'])}() {{")
        for line in case["body"].rstrip("\n").split("\n"):
            parts.append("        " + line if line else "")
        parts.append("    }")
    parts.append("}")
    return "\n".join(parts) + "\n"


def _diagnostics(stderr):
    out = []
    for line in stderr.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("$message_type", "diagnostic") != "diagnostic":
            continue
        out.append(d)
    return out


def _primary_line(d):
    for s in d.get("spans") or []:
        if s.get("is_primary"):
            return s.get("line_start") or 0
    return 0


def _clean_rendered(text, src_name):
    return (text or "").replace(src_name, "your code").rstrip()


def _assert_detail(text):
    """Turn a panic message into (headline, detail lines)."""
    m = re.match(r"assertion `left == right` failed(?:: (.*?))?\n\s*left: (.*?)\n\s*right: (.*)", text, re.S)
    if m:
        what, got, want = m.group(1), m.group(2).strip(), m.group(3).strip()
        head = what.strip() if what else "Values differ"
        return head, [f"Expected: {want}", f"Got:      {got}"]
    m = re.match(r"assertion `left != right` failed(?:: (.*?))?\n\s*left: (.*?)\n\s*right: (.*)", text, re.S)
    if m:
        return (m.group(1) or "Values should differ").strip(), [f"Both were: {m.group(2).strip()}"]
    m = re.match(r"assertion failed: (.*)", text, re.S)
    if m:
        return "Check failed", [m.group(1).strip()]
    if text.startswith("not yet implemented"):
        return "Not written yet: replace todo!() with your code", []
    return "Your code panicked: " + text.strip().split("\n")[0], [l for l in text.strip().split("\n")[1:4]]


def _parse_run(stdout, spec, n_learner=0):
    names = {fn_name(i, c["name"]): c["name"] for i, c in enumerate(spec["cases"])}
    status_of = {}
    for m in re.finditer(r"^test grader_tests::(\w+)(?: - should panic)? \.\.\. (ok|FAILED)", stdout, re.M):
        status_of[m.group(1)] = m.group(2) == "ok"
    blocks = {}
    for m in re.finditer(r"^---- grader_tests::(\w+) stdout ----\n(.*?)(?=^---- grader_tests::|^failures:\s*$|\Z)", stdout, re.M | re.S):
        blocks[m.group(1)] = m.group(2)
    tests = []
    for fn, human in names.items():
        if fn not in status_of:
            tests.append({"name": human, "ok": False, "msg": "Did not finish: the program stopped or took too long (an endless loop?)", "detail": []})
            continue
        if status_of[fn]:
            tests.append({"name": human, "ok": True, "msg": "", "detail": []})
            continue
        block = blocks.get(fn, "")
        printed, panic = block, ""
        pm = re.search(r"^thread '.*?' (?:\(\d+\) )?panicked at ([^\n]*):\n(.*?)(?:\nnote: run with `RUST_BACKTRACE|\Z)", block, re.M | re.S)
        in_tests = False
        if pm:
            lm = re.search(r"exercise\.rs:(\d+):", pm.group(1))
            in_tests = bool(lm) and int(lm.group(1)) > n_learner
            panic = re.split(r"\nstack backtrace:", pm.group(2))[0].strip()
            printed = block[:pm.start()]
        head, detail = _assert_detail(panic) if panic else ("Test failed", [])
        if in_tests and head.startswith("Your code panicked: "):
            head = head[len("Your code panicked: "):]
        printed = printed.strip("\n")
        if printed:
            lines = printed.split("\n")
            detail = detail + ["Your code printed:"] + ["  " + l for l in lines[:8]] + (["  ..."] if len(lines) > 8 else [])
        tests.append({"name": human, "ok": False, "msg": head, "detail": detail})
    return tests


def _build_and_run(rustc, tmp, source, n_learner_from, n_learner_to):
    """Compile source as a test binary and run it. Returns (error_dict or None, stdout)."""
    src = os.path.join(tmp, "exercise.rs")
    with open(src, "w", encoding="utf-8") as f:
        f.write(source)
    exe = os.path.join(tmp, "tests" + (".exe" if os.name == "nt" else ""))
    cmd = [rustc, "--edition", EDITION, "--test", "--crate-name", "exercise", "-A", "dead_code", "-A", "unused",
           "--error-format=json", src, "-o", exe]
    try:
        cp = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=tmp)
    except subprocess.TimeoutExpired:
        return {"error": "Compiling took over 2 minutes and was stopped.", "tests": None}, ""
    errs = [d for d in _diagnostics(cp.stderr) if d.get("level") == "error"
            and not (d.get("message") or "").startswith("aborting due to")]
    if cp.returncode != 0 or errs:
        mine = [d for d in errs if n_learner_from < _primary_line(d) <= n_learner_to]
        pick = mine or errs
        text = "\n\n".join(_clean_rendered(d.get("rendered"), src) for d in pick[:3]) or cp.stderr[-2000:]
        line = _primary_line(mine[0]) - n_learner_from if mine else 0
        return {"error": text, "errline": line, "tests": None, "compile": True, "yours": bool(mine)}, ""
    try:
        rp = subprocess.run([exe, "--test-threads=1", "--color", "never"], capture_output=True, text=True,
                            timeout=RUN_SECONDS, cwd=tmp, env=dict(os.environ, RUST_BACKTRACE="0"))
        return None, rp.stdout
    except subprocess.TimeoutExpired as e:
        out = e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        return None, out + "\n[stopped after %d seconds]" % RUN_SECONDS


def _learner_results(stdout):
    res = {}
    for m in re.finditer(r"^test (\S+)(?: - should panic)? \.\.\. (ok|FAILED|ignored)", stdout, re.M):
        res[m.group(1)] = m.group(2)
    return res


def grade_mutation(code, spec, rustc, tmp):
    """The learner writes the tests: they must pass on the real code and fail on every mutant."""
    impl = spec["mutation"]["impl"].rstrip("\n") + "\n\n"
    offset = impl.count("\n")
    err, out = _build_and_run(rustc, tmp, impl + code, offset, offset + code.count("\n") + 1)
    if err:
        err["error"] = "Your tests don't compile yet.\n\n" + err["error"]
        return err
    res = _learner_results(out)
    ran = {k: v for k, v in res.items() if v != "ignored"}
    if not ran:
        return {"error": "No tests ran. Write #[test] functions inside a #[cfg(test)] mod tests { use super::*; ... } block.", "tests": None}
    failing = [k for k, v in ran.items() if v == "FAILED"]
    tests = [{"name": spec["cases"][0]["name"], "ok": not failing,
              "msg": "" if not failing else "Some of your tests fail on the correct code, so they expect the wrong thing",
              "detail": ["Failing: " + ", ".join(failing[:6])] if failing else []}]
    for k, mut in enumerate(spec["mutation"]["mutants"]):
        merr, mout = _build_and_run(rustc, tmp, mut["code"].rstrip("\n") + "\n\n" + code, 10 ** 9, 10 ** 9)
        mres = _learner_results(mout) if not merr else {}
        killed = bool(merr) or any(v == "FAILED" for v in mres.values()) or "[stopped after" in mout
        tests.append({"name": spec["cases"][k + 1]["name"], "ok": killed and not failing,
                      "msg": "" if killed else "All your tests still pass with this bug in the code",
                      "detail": [] if killed else ["Add a test with an input where this bug gives a different answer."]})
    return {"tests": tests, "error": ""}


def grade(code, spec, workdir=None):
    rustc = tool("rustc")
    if not rustc:
        return {"error": "Rust isn't installed on this computer, so the tests can't run here. Install it from https://rustup.rs, restart the course, or use Test in Playground.", "tests": None}
    tmp = workdir or tempfile.mkdtemp(prefix="rsgrade-")
    try:
        if spec.get("mutation"):
            return grade_mutation(code, spec, rustc, tmp)
        learner = code.rstrip("\n") + "\n"
        n_learner = learner.count("\n")
        err, out = _build_and_run(rustc, tmp, learner + test_module(spec), 0, n_learner)
        if err:
            text = err.get("error", "")
            if err.get("compile") and not err.get("yours"):
                text = ("Your code compiles, but the tests can't use it yet. Check the names, parameter types and "
                        "return type against the specification.\n\n" + text)
            if err.get("compile") and err.get("yours"):
                text = "Your code doesn't compile yet.\n\n" + text
            err["error"] = text
            return err
        return {"tests": _parse_run(out, spec, n_learner), "error": ""}
    finally:
        if not workdir:
            shutil.rmtree(tmp, ignore_errors=True)


# Lints that are noise for exercise-sized code.
QUIET = {"dead_code", "clippy::needless_return_in_tests"}


def style(code, workdir=None):
    driver = tool("clippy-driver") or tool("rustc")
    if not driver:
        return []
    tmp = workdir or tempfile.mkdtemp(prefix="rsstyle-")
    try:
        src = os.path.join(tmp, "exercise.rs")
        with open(src, "w", encoding="utf-8") as f:
            f.write(code)
        cmd = [driver, "--edition", EDITION, "--crate-type", "lib", "--crate-name", "exercise", "--emit=metadata",
               "-A", "dead_code", "--error-format=json", src, "-o", os.path.join(tmp, "libexercise.rmeta")]
        try:
            cp = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=tmp)
        except subprocess.TimeoutExpired:
            return []
        notes, seen = [], set()
        for d in _diagnostics(cp.stderr):
            if d.get("level") != "warning":
                continue
            code_id = (d.get("code") or {}).get("code") or ""
            if code_id in QUIET:
                continue
            if code_id in ("unused_variables", "unused_mut") and "todo!(" in code:
                continue  # unfinished starter code: these notes would only be noise
            msg = d.get("message") or ""
            if msg.startswith(("unused `#[macro_use]`",)) or "warning emitted" in msg or "warnings emitted" in msg:
                continue
            line = _primary_line(d)
            help_ = ""
            for c in d.get("children") or []:
                hm = c.get("message") or ""
                if c.get("level") != "help" or not hm or hm.startswith("for further information"):
                    continue
                fix = next((sp.get("suggested_replacement") for sp in c.get("spans") or [] if sp.get("suggested_replacement")), None)
                if fix and len(fix) < 60 and "\n" not in fix:
                    hm = f"{hm}: `{fix}`" if not hm.endswith(":") else f"{hm} `{fix}`"
                help_ = hm
                break
            text = msg + (f" ({help_})" if help_ and help_ not in msg and len(help_) < 120 else "")
            if code_id.startswith("clippy::"):
                text += f" [{code_id}]"
            key = (line, text)
            if key in seen:
                continue
            seen.add(key)
            notes.append({"line": line, "msg": text})
        return sorted(notes, key=lambda n: n["line"])[:8]
    finally:
        if not workdir:
            shutil.rmtree(tmp, ignore_errors=True)


def style_for(code, spec):
    """Style notes for a submission; for test-writing exercises, lint the tests together with the real code."""
    if spec and spec.get("mutation"):
        impl = spec["mutation"]["impl"].rstrip("\n") + "\n\n"
        off = impl.count("\n")
        return [dict(n, line=n["line"] - off) for n in style(impl + code) if n["line"] > off]
    return style(code)


if __name__ == "__main__":
    demo = {"cases": [{"name": "Adds", "body": "assert_eq!(add(2, 3), 5, \"add(2, 3)\");"},
                      {"name": "Negative", "body": "assert_eq!(add(-2, -3), -5, \"add(-2, -3)\");"}]}
    print(json.dumps(grade("pub fn add(a: i32, b: i32) -> i32 { a + b }", demo), indent=1))
    print(json.dumps(grade("pub fn add(a: i32, b: i32) -> i32 { println!(\"hi\"); a - b }", demo), indent=1))
    print(json.dumps(grade("pub fn add(a: i32, b: i32) -> i32 { a + c }", demo), indent=1))
    print(json.dumps(grade("pub fn add(a: i32) -> i32 { a }", demo), indent=1)[:600])
    print(json.dumps(grade("pub fn add(a: i32, b: i32) -> i32 { todo!() }", demo), indent=1))
    print(json.dumps(grade("pub fn add(a: i32, b: i32) -> i32 { loop {} }", demo), indent=1))
    print(style("pub fn add(a: i32, b: i32) -> i32 { let x = 5; return a + b; }\npub fn f(v: &Vec<i32>) -> usize { v.len() }"))
