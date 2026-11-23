"""Apply the modern look (the Map's design) across the whole course engine.

A theme layer appended after the engine's own styles: new colour tokens for light and dark
mode, a modern type pairing, and component overrides (navigation, cards, buttons, lessons,
editor, tests, quizzes, grades). The Rust build inherits it from the engine.

usage: python3 theme_add.py course.html   (idempotent)
"""
import sys

FONT = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" data-theme-font>'

CSS = r"""/* THEME:BEGIN */
:root{
  --bg:#F3F6FC;--surface:#FFFFFF;--raised:#EEF2F9;--ink:#0F1F3D;--muted:#5B6B82;--line:#DCE4F0;
  --blue:#2563EB;--blue-soft:#E4ECFF;--good:#059669;--good-soft:#E3F6EE;--warn:#C2410C;--warn-soft:#FFF1E6;--bad:#DC2626;
  --h0:#E4EAF4;--h1:#BFD3FF;--h2:#7AA2FF;--h3:#2563EB;--code-bg:#F7F9FD;
  --font-display:'Plus Jakarta Sans','Inter',system-ui,sans-serif;--font-body:'Plus Jakarta Sans','Inter',system-ui,-apple-system,'Segoe UI',sans-serif;
  --g1:#2563EB;--g2:#7C3AED;--tint1:#60A5FA;--tint2:#A78BFA;--brand-grad:linear-gradient(135deg,var(--g1) 0%,var(--g2) 100%);--ok-grad:linear-gradient(90deg,#10B981,#0EA5E9);
  --r-lg:18px;--r-md:12px;--r-sm:9px;
  --shadow:0 1px 2px rgba(15,31,61,.04),0 8px 24px -14px rgba(15,31,61,.20);--shadow-lg:0 2px 4px rgba(15,31,61,.04),0 18px 40px -18px rgba(15,31,61,.28);
  --mark:#2563EB;--mark-ink:#FFFFFF
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0B1222;--surface:#131C30;--raised:#1A2540;--ink:#E6EEFB;--muted:#94A3B8;--line:#24314D;
  --blue:#60A5FA;--blue-soft:#1A2A4A;--good:#34D399;--good-soft:#0E2B24;--warn:#FB923C;--warn-soft:#33200F;--bad:#F87171;
  --h0:#1A2540;--h1:#1E3A70;--h2:#3B6FD8;--h3:#60A5FA;--code-bg:#0F1729;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 10px 28px -14px rgba(0,0,0,.7);--shadow-lg:0 2px 6px rgba(0,0,0,.35),0 20px 44px -18px rgba(0,0,0,.8);
  --mark:#60A5FA;--mark-ink:#0B1222}}
:root[data-theme="dark"]{
  --bg:#0B1222;--surface:#131C30;--raised:#1A2540;--ink:#E6EEFB;--muted:#94A3B8;--line:#24314D;
  --blue:#60A5FA;--blue-soft:#1A2A4A;--good:#34D399;--good-soft:#0E2B24;--warn:#FB923C;--warn-soft:#33200F;--bad:#F87171;
  --h0:#1A2540;--h1:#1E3A70;--h2:#3B6FD8;--h3:#60A5FA;--code-bg:#0F1729;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 10px 28px -14px rgba(0,0,0,.7);--shadow-lg:0 2px 6px rgba(0,0,0,.35),0 20px 44px -18px rgba(0,0,0,.8);
  --mark:#60A5FA;--mark-ink:#0B1222}
/* page */
body{background:radial-gradient(1100px 520px at -5% -10%,color-mix(in srgb,var(--tint1) 18%,transparent),transparent 60%),radial-gradient(900px 520px at 105% 0%,color-mix(in srgb,var(--tint2) 16%,transparent),transparent 60%),var(--bg);background-attachment:fixed;
  font-family:var(--font-body);-webkit-font-smoothing:antialiased;letter-spacing:-.003em}
h1,h2,h3{font-family:var(--font-display);letter-spacing:-.025em}
h1{font-weight:800}
.intro h1,.trintro h1{background:var(--brand-grad);-webkit-background-clip:text;background-clip:text;color:transparent;width:fit-content;line-height:1.2;padding-bottom:.12em}
a{text-underline-offset:3px}
::selection{background:color-mix(in srgb,var(--g1) 25%,transparent)}
/* header and navigation */
.brand .bname{font-weight:800;letter-spacing:-.02em}
.navbar{background:color-mix(in srgb,var(--bg) 78%,transparent);backdrop-filter:saturate(1.4) blur(12px);-webkit-backdrop-filter:saturate(1.4) blur(12px);border-bottom:1px solid var(--line);padding:8px 0}
.tabs{flex:0 1 auto!important;width:max-content;max-width:100%;overflow-x:auto;scrollbar-width:none;gap:2px;padding:4px;border-radius:999px;background:color-mix(in srgb,var(--surface) 70%,transparent);border:1px solid var(--line)}
.tabs a{border-bottom:0!important;margin-bottom:0;border-radius:999px;padding:7px 14px!important;font-weight:600;transition:background .15s,color .15s}
.tabs a[aria-current="page"]{background:var(--surface);color:var(--ink);box-shadow:var(--shadow)}
.srch{border-radius:999px!important}
/* buttons and inputs */
.btn{border-radius:var(--r-sm);border:1px solid var(--line);background:var(--surface);font-weight:600;transition:transform .12s,box-shadow .15s,border-color .15s,background .15s}
.btn:hover{border-color:color-mix(in srgb,var(--blue) 55%,var(--line));box-shadow:var(--shadow)}
.btn:active{transform:translateY(1px)}
.btn.primary{background:var(--brand-grad);border-color:transparent;color:#fff;box-shadow:0 8px 18px -10px color-mix(in srgb,var(--g1) 75%,transparent)}
.btn.primary:hover{filter:brightness(1.06);border-color:transparent}
.btn:focus-visible,.tabs a:focus-visible{outline:2px solid var(--blue);outline-offset:2px}
input[type=text],input[type=search],input[type=number],input[type=date],input[type=time],input[type=email],select,textarea:not(.code-ed){border-radius:var(--r-sm)!important;border:1px solid var(--line);background:var(--surface);color:var(--ink);transition:border-color .15s,box-shadow .15s}
input:focus-visible,select:focus-visible,textarea:not(.code-ed):focus-visible{outline:0;border-color:var(--blue);box-shadow:0 0 0 4px color-mix(in srgb,var(--blue) 18%,transparent)}
input[type=checkbox]{accent-color:var(--good)}
/* cards */
.panel,.stats,details.mod,.report,.plan,.cvbox,.exam-res{border-radius:var(--r-lg)!important;border:1px solid var(--line);box-shadow:var(--shadow)}
.panel,details.mod,.report,.plan{background:var(--surface)}
details.mod{overflow:hidden;transition:box-shadow .2s}
details.mod[open]{box-shadow:var(--shadow-lg)}
details.mod>summary{padding:16px 18px}
details.mod>summary:hover{background:color-mix(in srgb,var(--raised) 55%,transparent)}
details.mod>summary .mid{display:inline-grid;place-items:center;min-width:2.6em;height:2.6em;padding:0 .5em;border-radius:12px;background:var(--blue-soft);color:var(--blue);font-weight:700}
details.mod>summary .mt{font-weight:700}
details.item>summary{border-radius:var(--r-md);padding:11px 30px 11px 10px;margin:0 -10px;transition:background .12s}
details.item>summary::after{right:12px}
details.item>summary:hover{background:color-mix(in srgb,var(--raised) 70%,transparent)}
.stats{background:var(--surface);overflow:hidden}
.stats dd{font-family:var(--font-display);font-weight:800;letter-spacing:-.02em}
/* lesson content */
.eg,.ed,.deep,.tests,.hints,.sol,.console,.chkl,.stylen,.tafb,.dx,.qc,.reading,.msg{border-radius:var(--r-md)!important}
.eg{background:var(--surface);border:1px solid var(--line)}
.ed{border:1px solid var(--line);box-shadow:var(--shadow)}
.cm,.code{border-radius:var(--r-sm)!important;overflow:hidden}
pre,code{border-radius:6px}
.tests ul li{border-radius:var(--r-sm)}
.win{border-radius:var(--r-md)!important;background:linear-gradient(135deg,color-mix(in srgb,#10B981 16%,var(--surface)),color-mix(in srgb,#0EA5E9 12%,var(--surface)))!important}
.winmark{background:var(--ok-grad)!important}
.tag,.lv,.chip,.pill{border-radius:999px}
.bar,progress{border-radius:999px;overflow:hidden}
.bar>i,.bar>span,.bar>div{border-radius:999px}
.heat i,.heat span,.heat div{border-radius:4px}
.qopt,.qcopt,.dxopt{border-radius:var(--r-md)!important;transition:border-color .15s,background .15s,transform .12s}
.qopt:hover,.qcopt:hover,.dxopt:hover{transform:translateY(-1px)}
.lvchips{border-radius:999px}
.lvchips button{border-radius:999px}
.seg button{border-radius:16px!important}
.navact{margin-left:auto}
@media (max-width:480px){.tabs a{padding:6px 9px!important;font-size:.86rem}.tabs{padding:3px}}
.course{border-radius:var(--r-md)!important;margin-bottom:10px!important;box-shadow:none}
.mods button{border-radius:var(--r-sm)}
#toast{border-radius:999px!important;box-shadow:var(--shadow-lg);padding-inline:18px!important}
dialog,.modal,.pal{border-radius:var(--r-lg)!important;box-shadow:var(--shadow-lg)}
kbd{border-radius:6px}
table{border-collapse:separate;border-spacing:0}
th:first-child{border-top-left-radius:var(--r-sm)}th:last-child{border-top-right-radius:var(--r-sm)}
/* labels: clean uppercase sans instead of monospace */
.lbl,.eyebrow,.sublbl,.stats dt,.eg>h4,.code-h>span,.out>h4,.field>label,.zen small,.pk,.tag,.lv b,.nextl span,.wd,.repst dt{font-family:var(--font-body)!important;font-weight:700;letter-spacing:.09em}
.lbl,.eyebrow,.sublbl,.stats dt,.eg>h4,.out>h4,.field>label{font-size:.68rem!important;color:var(--muted)}
#view h1:not(.pz *){background:var(--brand-grad);-webkit-background-clip:text;background-clip:text;color:transparent;width:fit-content;max-width:100%;line-height:1.2;padding-bottom:.12em;padding-right:.04em}
.recap{border-radius:var(--r-lg)!important}
/* THEME:END */
"""


def main(path):
    s = open(path, encoding="utf-8").read()
    while "/* THEME:BEGIN */" in s:
        a = s.index("/* THEME:BEGIN */")
        b = s.index("/* THEME:END */", a) + len("/* THEME:END */\n")
        s = s[:a] + s[b:]
    s = s.replace(FONT + "\n", "").replace(FONT, "")
    s = s.replace("</head>", FONT + "\n</head>", 1)
    i = s.rindex("</style>")
    s = s[:i] + CSS + s[i:]
    open(path, "w", encoding="utf-8").write(s)
    print("theme added to", path)


if __name__ == "__main__":
    main(sys.argv[1])
