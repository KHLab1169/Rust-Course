"""Load course YAML and normalise the compact text formats.

res: |        "Title | url" per line
functions: |  "code || description" per line
o: |          one option per line
Also lints raw text for YAML traps in plain (unquoted, non-block) lines:
  ' #'   would silently start a comment
"""
import re
import sys
import yaml


def lint(path):
    probs = []
    block_ind = None
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        s = line.rstrip("\n")
        ind = len(s) - len(s.lstrip(" "))
        if block_ind is not None:
            if s.strip() == "" or ind > block_ind:
                continue
            block_ind = None
        if re.search(r"(:|-)\s*[|>][+-]?\s*$", s):
            block_ind = ind
            continue
        body = s.strip()
        if body.startswith("#"):
            continue
        # strip a quoted scalar value so quotes protect it
        val = re.sub(r'^(- )?([\w]+: )?', "", body)
        if val.startswith('"') or val.startswith("'"):
            continue
        if " #" in val:
            probs.append(f"{path}:{n}: ' #' in a plain scalar (would start a comment): {body[:80]}")
    return probs


def _unq(v):
    import json
    if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
        return json.loads(v)
    return v


def norm(mods):
    for m in mods:
        if isinstance(m.get("res"), str):
            m["res"] = [[p.strip() for p in l.rsplit(" | ", 1)] for l in m["res"].strip().split("\n") if l.strip()]
        r = m.get("recap") or {}
        if isinstance(r.get("functions"), str):
            r["functions"] = [[p.strip() for p in l.split(" || ", 1)] for l in r["functions"].strip().split("\n") if l.strip()]
        for q in m.get("quiz") or []:
            if isinstance(q.get("o"), str):
                q["o"] = [_unq(l.strip()) for l in q["o"].strip().split("\n") if l.strip()]
    return mods


def load(path):
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from fix import fix
    fix(path)
    probs = lint(path)
    if probs:
        print("\n".join(probs), file=sys.stderr)
        raise SystemExit(f"lint failed for {path}")
    return norm(yaml.safe_load(open(path, encoding="utf-8")))
