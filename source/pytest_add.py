"""Download the tests: a graded exercise's hidden tests as a small project to run locally.

Python: solution.py + test_solution.py (pytest; embeds the course's own grader and the spec).
The Rust build replaces testBundle() with a Cargo project (Cargo.toml + src/lib.rs + tests).
usage: python3 pytest_add.py course.html   (idempotent)
"""
import sys

import os
JS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pytest_add.js"), encoding="utf-8").read()


ANCHOR = "/* ---------- events ---------- */"
TOOLS_OLD = 'tools.innerHTML="<button type=\\"button\\" class=\\"linkbtn\\" data-act=\\"copycode\\" data-id=\\""+eid+"\\">Copy</button>"+'
TOOLS_NEW = TOOLS_OLD + '(spec&&testsDownloadable(spec)?"<button type=\\"button\\" class=\\"linkbtn\\" data-act=\\"dltests\\" data-id=\\""+eid+"\\" title=\\"Download this exercise with its tests to run on your computer\\">Download tests</button>":"")+'


def main(path):
    s = open(path, encoding="utf-8").read()
    while "/* DLTESTS:BEGIN */" in s:
        a = s.index("/* DLTESTS:BEGIN */")
        b = s.index("/* DLTESTS:END */", a) + len("/* DLTESTS:END */\n")
        s = s[:a] + s[b:]
    assert ANCHOR in s
    js = JS.replace("/* DLTESTS:END */", "function testsDownloadable(spec){return !!(spec&&spec.cases&&spec.cases.length);}\n/* DLTESTS:END */")
    s = s.replace(ANCHOR, js + ANCHOR, 1)
    if TOOLS_NEW not in s:
        assert TOOLS_OLD in s
        s = s.replace(TOOLS_OLD, TOOLS_NEW, 1)
    open(path, "w", encoding="utf-8").write(s)
    print("download-tests added to", path)


if __name__ == "__main__":
    main(sys.argv[1])
