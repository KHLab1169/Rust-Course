"""Focus mode: put the focused lesson on a card with equal space on both sides.
Without this the lesson had 32px on the left and none on the right, so text ran into the edge.
usage: python3 focus_add.py course.html   (idempotent; run after theme_add.py)
"""
import sys

CSS = r"""/* FOCUS:BEGIN */
html.focusing details.item.focused{background:var(--surface);border:1px solid var(--line)!important;border-radius:var(--r-lg,18px);
  box-shadow:var(--shadow);padding:6px clamp(16px,4vw,44px) 32px;margin:8px 0 24px}
html.focusing details.item.focused>summary{margin:0 -10px}
html.focusing details.item.focused .ibody{padding-left:0;padding-right:0}
/* FOCUS:END */
"""


def main(path):
    s = open(path, encoding="utf-8").read()
    while "/* FOCUS:BEGIN */" in s:
        a = s.index("/* FOCUS:BEGIN */")
        b = s.index("/* FOCUS:END */", a) + len("/* FOCUS:END */\n")
        s = s[:a] + s[b:]
    i = s.rindex("</style>")
    s = s[:i] + CSS + s[i:]
    open(path, "w", encoding="utf-8").write(s)
    print("focus mode card in", path)


if __name__ == "__main__":
    main(sys.argv[1])
