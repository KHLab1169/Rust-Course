"""Accessibility fixes found with axe-core across every view, light and dark.

- Text colours that met 4.5:1 contrast only on white: darker green, blue and level colours in light mode.
- Headings in order: modules and lessons in the curriculum are exposed as level 2 and 3 headings,
  so the h4 labels inside a lesson (The idea, How it works...) follow on.
- The page language is declared (the hosting skeleton has no lang attribute).
usage: python3 a11y_add.py course.html   (idempotent; run after theme_add.py)
"""
import sys

CSS = r"""/* A11Y:BEGIN */
:root{--good:#047857;--blue:#1D4ED8;--c-com:#566273}
.lv.l1 b,.lv.l2 b,.lv.l3 b,.lv.l4 b,.lv.l5 b{filter:brightness(.78)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--good:#34D399;--blue:#60A5FA}:root:not([data-theme="light"]) .lv b{filter:none}}
:root[data-theme="dark"]{--good:#34D399;--blue:#60A5FA}
:root[data-theme="dark"] .lv b{filter:none}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important;scroll-behavior:auto!important}}
/* A11Y:END */
"""
JS = '<script>/* A11Y:BEGIN */if(!document.documentElement.lang)document.documentElement.lang="en";/* A11Y:END */</script>\n'
REPS = [('<span class=\\"mt\\">"+esc(m.t)', '<span class=\\"mt\\" role=\\"heading\\" aria-level=\\"2\\">"+esc(m.t)'),
        ('<span class=\\"iid\\">"+i.id+"</span><span class=\\"ttl\\">', '<span class=\\"iid\\">"+i.id+"</span><span class=\\"ttl\\" role=\\"heading\\" aria-level=\\"3\\">')]


def strip(s, a, b):
    while a in s:
        i = s.index(a)
        j = s.index(b, i) + len(b)
        if s[j:j + 1] == "\n":
            j += 1
        s = s[:i] + s[j:]
    return s


def main(path):
    s = open(path, encoding="utf-8").read()
    s = strip(s, "/* A11Y:BEGIN */\n:root", "/* A11Y:END */")
    s = s.replace(JS, "")
    for old, new in REPS:
        if new not in s:
            assert old in s, old
            s = s.replace(old, new)
    i = s.rindex("</style>")
    s = s[:i] + CSS + s[i:]
    s = s.replace("</head><body>", "</head><body>\n" + JS, 1)
    if "<html>" in s[:200]:
        s = s.replace("<html>", '<html lang="en">', 1)
    open(path, "w", encoding="utf-8").write(s)
    print("accessibility fixes added to", path)


if __name__ == "__main__":
    main(sys.argv[1])
