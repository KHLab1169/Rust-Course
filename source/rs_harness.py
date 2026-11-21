"""Check autograded Rust exercises: the solution passes, every wrong answer fails,
the starter compiles against the tests, and the solution has no style notes.

usage: python3 rs_harness.py specs/rs_practice1.py [more spec files]
"""
import importlib.util
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rsgrade  # noqa: E402
import rspec  # noqa: E402


def load(path):
    spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)


def check(e):
    msgs = []
    sp = e["spec"]
    r = rsgrade.grade(e["solution"], sp)
    if r.get("error") or not r["tests"] or not all(t["ok"] for t in r["tests"]):
        bad = [t for t in (r["tests"] or []) if not t["ok"]]
        msgs.append("SOLUTION FAILS: " + (r.get("error") or "")[:1200] + " " + str(bad)[:800])
    for i, b in enumerate(e["bad"]):
        rb = rsgrade.grade(b, sp)
        if rb.get("error") and e.get("loose"):
            continue
        if rb.get("error"):
            msgs.append(f"bad#{i} does not compile (should fail a test instead): {rb['error'][:300]}")
        elif all(t["ok"] for t in rb["tests"]):
            msgs.append(f"bad#{i} PASSES")
    if not sp.get("mutation") and not e.get("loose"):
        rs = rsgrade.grade(e["starter"], sp)
        if rs.get("error"):
            msgs.append("starter does not compile: " + rs["error"][:600])
        elif any(t["ok"] for t in rs["tests"]):
            msgs.append("starter passes a test: " + str([t["name"] for t in rs["tests"] if t["ok"]]))
    st = rsgrade.style_for(e["solution"], sp)
    if st:
        msgs.append("style notes on solution: " + str(st))
    return e["eid"], len(sp["cases"]), msgs


def main():
    for p in sys.argv[1:]:
        load(p)
    ok = True
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
        for eid, n, msgs in pool.map(check, rspec.EXERCISES):
            print(f"{eid}: {n} tests " + ("ok" if not msgs else "\n   " + "\n   ".join(msgs)))
            ok = ok and not msgs
    print("ALL GOOD" if ok else "PROBLEMS")


if __name__ == "__main__":
    main()
