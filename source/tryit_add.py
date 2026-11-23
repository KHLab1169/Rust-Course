"""Try it: run and edit any Python worked example in the page.

Adds a fold-out editor with Run and Reset under each Python worked example (first and expanded).
The Rust build turns it off (TRY_PY=false): its examples go to the Playground instead.
usage: python3 tryit_add.py course.html   (idempotent)
"""
import os, sys

JS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tryit_add.js"), encoding="utf-8").read()
CSS = r"""/* TRYIT:BEGIN */
.tryit{margin:8px 0 2px;border:1px dashed var(--line);border-radius:var(--r-md,12px);padding:0 12px;background:color-mix(in srgb,var(--blue-soft) 35%,transparent)}
.tryit>summary{cursor:pointer;padding:9px 0;font-size:.86rem;font-weight:600;color:var(--blue)}
.tryit[open]{padding-bottom:12px}
.try-ed{display:block;width:100%;box-sizing:border-box;font-family:var(--font-mono,ui-monospace,Menlo,Consolas,monospace);font-size:.84rem;line-height:1.5;padding:10px 12px;border:1px solid var(--line);border-radius:var(--r-sm,9px);background:var(--code-bg,var(--surface));color:var(--ink);resize:vertical;tab-size:4;white-space:pre;overflow:auto}
.try-ed:focus-visible{outline:2px solid var(--blue);outline-offset:1px}
.try-in{margin-top:8px;display:grid;gap:4px}
.try-in label{font-size:.78rem;font-weight:600;color:var(--muted)}
.try-stdin{display:block;width:100%;box-sizing:border-box;font-family:var(--font-mono,ui-monospace,Menlo,Consolas,monospace);font-size:.84rem;line-height:1.5;padding:6px 10px;border:1px solid var(--line);border-radius:var(--r-sm,9px);background:var(--code-bg,var(--surface));color:var(--ink);resize:vertical}
.try-stdin:focus-visible{outline:2px solid var(--blue);outline-offset:1px}
.try-row{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:8px}
.try-out{margin:10px 0 0;padding:10px 12px;border:1px solid var(--line);border-radius:var(--r-sm,9px);background:var(--surface);font-size:.84rem;max-height:320px;overflow:auto;white-space:pre-wrap;word-break:break-word}
.try-out.err{border-color:color-mix(in srgb,var(--bad,#DC2626) 45%,var(--line))}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
/* TRYIT:END */
"""
ANCHOR = "/* ---------- events ---------- */"
REPS = [('codeBlock(x.code,x.lang,"eg|"+i.id,x.lang)+', 'codeBlock(x.code,x.lang,"eg|"+i.id,x.lang)+tryBlock("eg|"+i.id,x)+'),
        ('codeBlock(x.code,x.lang,"dx|"+i.id+"|"+k,x.lang)+', 'codeBlock(x.code,x.lang,"dx|"+i.id+"|"+k,x.lang)+tryBlock("dx|"+i.id+"|"+k,x)+')]


def strip(s, a, b):
    while a in s:
        i = s.index(a)
        j = s.index(b, i) + len(b)
        s = s[:i] + s[j + (1 if s[j:j + 1] == "\n" else 0):]
    return s


def main(path):
    s = open(path, encoding="utf-8").read()
    s = strip(s, "/* TRYIT:BEGIN */", "/* TRYIT:END */")
    assert ANCHOR in s
    s = s.replace(ANCHOR, JS + ANCHOR, 1)
    for old, new in REPS:
        if new not in s:
            assert old in s, old
            s = s.replace(old, new, 1)
    i = s.rindex("</style>")
    s = s[:i] + CSS + s[i:]
    open(path, "w", encoding="utf-8").write(s)
    print("try-it editors added to", path)


if __name__ == "__main__":
    main(sys.argv[1])
