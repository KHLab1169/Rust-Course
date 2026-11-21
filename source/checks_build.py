#!/usr/bin/env python3
"""Attach a quick-check question to each worked example 2 and 3 in a deep.json file.

Usage: python3 checks_build.py deep/checks/py deep.json
       python3 checks_build.py deep/checks/rs rust/deep.json

Authoring format (one file per module):

    === 3.2/2 predict          lesson id / worked example number (2 or 3) / kind
    Q: What is the last line this program prints?
    + `Total: 42`              the correct option (exactly one "+")
    - `Total: 41`              wrong options
    - `Total: 0`
    WHY: Why the right answer is right (and the trap in the wrong ones).

Kinds:
  predict  the example's output and note stay hidden until the learner answers. The correct
           option (without backticks) must be a whole line of the real output, or the build fails.
  pick     like predict, but wrong options may also be lines of the output ("which comes first?",
           "which line does input X produce?").
  hide     hides the output like predict, without line validation (for answers that describe the
           output in words rather than quoting a line).
  concept  (default) a question about the idea; output stays visible.

Options are shuffled deterministically, so authors can always write the right one first.
`code` and **bold** are allowed in questions, options and explanations.
"""
import glob, hashlib, json, os, random, re, sys

src_dir, deep_path = sys.argv[1], sys.argv[2]
deep = json.load(open(deep_path))
for les in deep.values():
    for ex in les.get("examples", []):
        ex.pop("check", None)

problems, count = [], 0
for path in sorted(glob.glob(os.path.join(src_dir, "*.txt"))):
    blocks = re.split(r"^=== ", open(path, encoding="utf-8").read(), flags=re.M)[1:]
    for b in blocks:
        head, *lines = b.rstrip().split("\n")
        m = re.fullmatch(r"(\S+)/([23])(?:\s+(predict|pick|hide|concept))?\s*", head)
        if not m:
            problems.append(f"{path}: bad header {head!r}")
            continue
        lid, n, kind = m.group(1), int(m.group(2)), m.group(3) or "concept"
        q, why, opts, ans = "", "", [], None
        for line in lines:
            if line.startswith("Q: "):
                q = line[3:].strip()
            elif line.startswith("WHY: "):
                why = line[5:].strip()
            elif line.startswith(("+ ", "- ")):
                if line[0] == "+":
                    if ans is not None:
                        problems.append(f"{lid}/{n}: two correct options")
                    ans = len(opts)
                opts.append(line[2:].strip())
            elif line.strip():
                if why:
                    why += " " + line.strip()
                else:
                    problems.append(f"{lid}/{n}: stray line {line!r}")
        where = f"{lid}/{n}"
        if lid not in deep or len(deep[lid].get("examples", [])) < n - 1:
            problems.append(f"{where}: no such lesson or example")
            continue
        if not q or not why or ans is None or not 3 <= len(opts) <= 4 or len(set(opts)) != len(opts):
            problems.append(f"{where}: needs Q, WHY, 3-4 distinct options and one correct")
            continue
        ex = deep[lid]["examples"][n - 2]
        if kind in ("predict", "pick"):
            out_lines = {l.strip() for l in (ex.get("output") or "").split("\n")}
            plain = lambda o: (o[1:-1] if o.startswith("`") and o.endswith("`") else o).strip()
            if plain(opts[ans]) not in out_lines:
                problems.append(f"{where}: correct option {opts[ans]!r} is not a line of the real output")
                continue
            wrong_hits = [o for k, o in enumerate(opts) if k != ans and plain(o) in out_lines]
            if wrong_hits and kind == "predict":
                problems.append(f"{where}: wrong option(s) also appear in the output: {wrong_hits}")
                continue
            if not ex.get("output"):
                problems.append(f"{where}: predict check on an example without output")
                continue
        order = list(range(len(opts)))
        random.Random(hashlib.md5(where.encode()).hexdigest()).shuffle(order)
        ex["check"] = {"kind": kind, "q": q, "options": [opts[k] for k in order], "answer": order.index(ans), "explain": why}
        count += 1

total = sum(len(l.get("examples", [])) for l in deep.values())
missing = [f"{lid}/{k + 2}" for lid, l in deep.items() for k, ex in enumerate(l.get("examples", [])) if "check" not in ex]
json.dump(deep, open(deep_path, "w"), ensure_ascii=False, indent=1)
for p in problems:
    print("PROBLEM", p)
print(f"{count} checks attached to {deep_path}; {total - count} of {total} examples without one")
if missing and len(sys.argv) > 3:
    print("missing:", " ".join(missing))
sys.exit(1 if problems else 0)
