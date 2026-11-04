#!/usr/bin/env python3
"""Quote plain YAML scalars that contain ': ' or ' #' (or start with a YAML
indicator) so prose and code fragments load safely. Rewrites files in place."""
import re
import sys

KEYS = r"(?:t|p|explain|x|q|note|learn|goal|title|next|repo|summary_line)"
IND = set("&*!%@`{[>|?#,")


def needs(v):
    if not v or v[0] in "\"'":
        return False
    return ": " in v or " #" in v or v[0] in IND or v.endswith(":") or v.startswith("- ")


def q(v):
    return "'" + v.replace("'", "''") + "'"


def fix(path):
    out, blk, changed = [], None, 0
    for line in open(path, encoding="utf-8").read().split("\n"):
        s = line
        ind = len(s) - len(s.lstrip(" "))
        if blk is not None:
            if s.strip() == "" or ind > blk:
                out.append(s)
                continue
            blk = None
        if re.search(r"(:|-)\s*[|>][+-]?\s*$", s):
            blk = ind
            out.append(s)
            continue
        m = re.match(r"^(\s*(?:- )?" + KEYS + r": )(.*)$", s)
        if m and needs(m.group(2)):
            s = m.group(1) + q(m.group(2))
            changed += 1
        else:
            m = re.match(r"^(\s*- )(.*)$", s)
            if m and not re.match(r"^[\w]+: ", m.group(2)) and needs(m.group(2)):
                s = m.group(1) + q(m.group(2))
                changed += 1
        out.append(s)
    open(path, "w", encoding="utf-8").write("\n".join(out))
    return changed


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(p, fix(p), "lines quoted")
