#!/usr/bin/env python3
"""Build the Rust Course page from the Python Course engine plus Rust content YAML.

usage: build.py ENGINE.html OUT.html content/*.yaml
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import load  # noqa: E402

engine_path, out_path = sys.argv[1], sys.argv[2]
files = sys.argv[3:]

mods = {"F": [], "A": [], "P": []}
lessons, recaps, quiz = {}, {}, {}
lv_mod, lv_item = {}, {}


def track_of(path):
    b = os.path.basename(path)
    return {"f": "F", "a": "A", "p": "P"}[b[0]]


def js(o):
    s = json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    return s.replace("</", "<\\/").replace("<!--", "<\\!--")


problems = []
for f in sorted(files):
    tr = track_of(f)
    for m in load(f):
        mid = m["id"]
        lv_mod[mid] = m.get("lv", 2)
        items = []
        for it in m["items"]:
            iid = it["id"]
            exs = it.get("ex", [])
            if len(exs) < 1:
                problems.append(f"{iid} has no exercises")
            items.append({
                "id": iid, "t": it["t"], "min": it.get("min", 45), "learn": it["learn"],
                "kind": it.get("kind", "lesson"),
                "ex": [{"id": iid + "abc"[k], "t": e["t"], "p": e["p"]} for k, e in enumerate(exs)],
            })
            if it.get("lv"):
                lv_item[iid] = it["lv"]
            c = {}
            eg = it.get("example")
            if eg:
                c["example"] = {"title": eg.get("title", ""), "lang": eg.get("lang", "rust"), "note": eg.get("note", ""),
                                "code": eg["code"].rstrip("\n"), "output": (eg.get("output") or "").rstrip("\n")}
            c["exercises"] = {}
            for k, e in enumerate(exs):
                eid = iid + "abc"[k]
                if len(e.get("hints", [])) < 2:
                    problems.append(f"{eid} has fewer than 2 hints")
                if not e.get("solution"):
                    problems.append(f"{eid} has no solution")
                c["exercises"][eid] = {"lang": e.get("lang", "rust"), "hints": e.get("hints", []),
                                       "solution": e.get("solution", "").rstrip("\n"), "explain": e.get("explain", "")}
            lessons[iid] = c
        mods[tr].append({"id": mid, "n": m["n"], "book": m.get("book", 0), "t": m["t"], "goal": m["goal"],
                         "res": m.get("res", []), "items": items})
        if m.get("recap"):
            r = dict(m["recap"])
            recaps[mid] = r
        qs = []
        for k, q in enumerate(m.get("quiz") or []):
            ans = q["a"] if isinstance(q["a"], list) else [q["a"]]
            if any(a >= len(q["o"]) for a in ans):
                problems.append(f"quiz {mid}-{k+1} answer index out of range")
            if len(q["o"]) < 2:
                problems.append(f"quiz {mid}-{k+1} has <2 options")
            qq = {"id": f"{mid}-{k+1:02d}", "type": q.get("type", "single"), "pool": q.get("pool", "quiz"),
                  "prompt": q["q"], "options": q["o"], "answer": ans, "explain": q.get("x", "")}
            if q.get("code"):
                qq["code"] = q["code"].rstrip("\n")
            qs.append(qq)
        if qs:
            quiz[mid] = qs

if problems:
    print("\n".join(problems))
    sys.exit("content problems")

# ---------------- courses ----------------
ALL_COURSES = [
    {"code": "RS101", "t": "Rust Fundamentals", "y": 1, "mods": ["c1", "c3", "c4", "c5", "c6"]},
    {"code": "RS102", "t": "Modules, Collections, Errors and Generics", "y": 1, "mods": ["c7", "c8", "c9", "c10"]},
    {"code": "RS103", "t": "Testing, Functional Rust, Cargo and Smart Pointers", "y": 1, "mods": ["c11", "c13", "c14", "c15"]},
    {"code": "RS104", "t": "Concurrency, Async and Trait Objects", "y": 1, "mods": ["c16", "c17", "c18"]},
    {"code": "RS105", "t": "Patterns and Advanced Rust", "y": 1, "mods": ["c19", "c20"]},
    {"code": "RS150", "t": "Book Projects Studio", "y": 1, "mods": ["c2", "c12", "c21"], "studio": True},
    {"code": "RS201", "t": "The Language in Depth", "y": 2, "mods": ["a1", "a2", "a3"]},
    {"code": "RS202", "t": "Errors, Abstractions and Tooling", "y": 2, "mods": ["a4", "a5", "a6"]},
    {"code": "RS203", "t": "Concurrency, Async and Metaprogramming", "y": 2, "mods": ["a7", "a8", "a9"]},
    {"code": "RS204", "t": "Quality Engineering and the Ecosystem", "y": 2, "mods": ["a10", "a11", "a12"]},
    {"code": "RS301", "t": "QA and Security Tools Studio", "y": 3, "mods": ["q1", "q2", "q3"], "studio": True},
    {"code": "RS302", "t": "Web and Systems Studio", "y": 3, "mods": ["w1", "w2", "w3"], "studio": True},
]
have = {m["id"] for t in mods.values() for m in t}
courses = []
for c in ALL_COURSES:
    ms = [m for m in c["mods"] if m in have]
    if ms:
        cc = dict(c)
        cc["mods"] = ms
        courses.append(cc)

# ---------------- engine edits ----------------
src = open(engine_path, encoding="utf-8").read()
lines = src.split("\n")
ci = next(i for i, l in enumerate(lines) if l.startswith("<script>window.PYCC_CONTENT="))
extras_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extras.json")
extras = json.load(open(extras_path)) if os.path.exists(extras_path) else {"checks": {}, "chk": {}}
deep_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deep.json")
deep = json.load(open(deep_path)) if os.path.exists(deep_path) else {}
content = {"lessons": lessons, "recaps": recaps, "grade": {}, "quiz": quiz, "cert": {}, "checks": extras["checks"], "chk": extras["chk"], "deep": deep}
lines[ci] = "<script>window.PYCC_CONTENT=" + js(content) + ";</script>"
src = "\n".join(lines)

# curriculum block
a = src.index("/* ---------- curriculum data ---------- */")
b = src.index("function inTrack(")
levels_line = re.search(r"var LEVELS=.*\n", src[a:b]).group(0)
levdesc_line = re.search(r"var LEVEL_DESC=.*\n", src[a:b]).group(0)
cur = ("/* ---------- curriculum data ---------- */\n"
       "var M=" + js(mods["F"]) + ";\nM.forEach(function(m){m.track=\"F\";});\n"
       "var MA=" + js(mods["A"]) + ";\nMA.forEach(function(m){m.track=\"A\";});\n"
       "var MPF=" + js(mods["P"]) + ";\nMPF.forEach(function(m){m.track=\"P\";});\n"
       "M=M.concat(MA,MPF);\n"
       "M.forEach(function(m){m.items.forEach(function(i){i.mod=m;});});\n"
       "var ITEMS=[].concat.apply([],M.map(function(m){return m.items;}));\n"
       "var TOTAL_MIN=ITEMS.reduce(function(a,i){return a+i.min;},0);\n"
       "/* Difficulty scale, 1 to 5. Module default, with per-lesson overrides. */\n"
       + levels_line + levdesc_line +
       "var LV_MOD=" + js(lv_mod) + ";\nvar LV_ITEM=" + js(lv_item) + ";\n"
       "ITEMS.forEach(function(i){i.lv=LV_ITEM[i.id]||LV_MOD[i.mod.id]||2;});\n")
src = src[:a] + cur + src[b:]


def rep(old, new, count=1):
    global src
    n = src.count(old)
    if n != count:
        raise SystemExit(f"expected {count} of {old[:70]!r}, found {n}")
    src = src.replace(old, new)


def rep_re(pat, new, count=1):
    global src
    src, n = re.subn(pat, lambda _m: new, src, flags=re.S)
    if n != count:
        raise SystemExit(f"expected {count} of /{pat[:60]}/, found {n}")


# link-styled buttons
rep(".btn:hover{border-color:var(--blue)}", ".btn:hover{border-color:var(--blue)}\n.ed-act{display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center}\n.ed-act .sub{margin-left:auto;display:flex;flex-wrap:wrap;gap:8px;align-items:center}\na.btn{display:inline-flex;align-items:center;text-decoration:none;color:var(--ink)}")
# copper accent instead of the Python yellow
rep("--yellow:#FFD43B; --yellow-ink:#2B2100;", "--yellow:#E8834F; --yellow-ink:#2A1206;", 3)
# header
rep("<title>Python Course</title>", "<title>Rust Course</title>")
n_ex_all = sum(len(i["ex"]) for t in mods.values() for m in t for i in m["items"])
rep('<span class="bname">Python Course</span>', '<span class="bname">Rust Course</span>')
rep('aria-label="Python Course, overview"', 'aria-label="Rust Course, overview"')
rep('Self-paced &middot; three tracks &middot; 446 exercises', 'Self-paced &middot; three tracks &middot; %d exercises' % n_ex_all)
# languages and labels
rep('var LANG={', 'var LANG={rust:"rust",text:"plaintext",')
rep('var l=LANG[lang||"python"]||"plaintext";', 'var l=LANG[lang||"rust"]||"plaintext";')
rep('esc(NICE_LANG[label||lang||"python"]||label||lang)', 'esc(NICE_LANG[label||lang||"rust"]||label||lang)')
rep('var NICE_LANG={python:"Python",', 'var NICE_LANG={rust:"Rust",python:"Python",')
rep('<code class=\\"language-python\\">"+esc(q.code)', '<code class=\\"language-rust\\">"+esc(q.code)', 2)
# tips instead of the Zen of Python
tips = ["Make illegal states unrepresentable.", "Read compiler errors top to bottom; they usually name the fix.",
        "Borrow when you can, clone when it makes the code clearer.", "Prefer &str and &[T] parameters.",
        "Return Result for failures you expect; panic for bugs.", "Let the types carry the rules.",
        "Small unsafe blocks, each with a SAFETY comment.", "cargo clippy is a free code review.",
        "Iterators are as fast as loops and easier to review.", "Write the test first, then the code.",
        "Parse, don't validate: turn raw input into checked types once.", "Use enums for choices and match for every case.",
        "Keep main thin and put the logic in lib.rs.", "Measure performance in release builds.",
        "Lock briefly, and always in the same order.", "Threads for computing, async for waiting."]
rep_re(r"var ZEN=\[.*?\];", "var ZEN=" + js(tips) + ";")
rep("<small>The Zen of Python, PEP 20</small>", "<small>Rust tip of the day</small>")
# storage keys and sync doc
rep('var KEY="pycc.v2";', 'var KEY="rscc.v1";')
rep('var CODEKEY="pycc.code"', 'var CODEKEY="rscc.code"')
rep('"data/users/"+id+"/tracker2"', '"data/users/"+id+"/rust1"')
rep('caps[0].doc("data/users/"+id+"/tracker").get()', 'caps[0].doc("data/users/"+id+"/rust0").get()')
# track texts
rep_re(r"function trackName\(tr\)\{.*?\}", 'function trackName(tr){return tr==="P"?"Track 3 \\u00b7 Portfolio":tr==="A"?"Track 2 \\u00b7 Advanced":"Track 1 \\u00b7 Foundations";}')
rep_re(r"function bookLabel\(m\)\{.*?\n", 'function bookLabel(m){if(m.track==="P")return (m.id.charAt(0)==="q"?"QA and security":"Web and systems")+" portfolio project";if(m.track==="A")return "roadmap.sh topic";return "Book chapter "+m.book;}\n')
rep_re(r"var TRACK_INTRO=\{.*?\n\};", 'var TRACK_INTRO={\n'
       '  F:"Follows The Rust Programming Language (the official book, 2024 edition) chapter by chapter, from installing Rust to the final multithreaded web server. Every chapter ends with a recap, and chapters 2, 12 and 21 are the book\'s projects.",\n'
       '  P:"Six projects to publish on GitHub and list on your CV: three QA and security tools that build on your testing background, and three web and systems projects. Each ends with tests, CI, a README and CV bullets with a suggested repository name. They assume Track 1 and Track 2 up to A10.",\n'
       '  A:"The roadmap.sh/rust curriculum: the standard collections, ownership and lifetimes in depth, error design, traits and type-level programming, Cargo and docs, concurrency and atomics, async with Tokio, macros, testing and profiling, and the crate ecosystem. It fits best after Track 1 chapter 16. Module A01 is a fast review you can use as a self-test."\n};')
rep('({F:"Beginning Python",A:"roadmap.sh/python",P:"GitHub and CV projects"})', '({F:"The Rust Book",A:"roadmap.sh/rust",P:"GitHub and CV projects"})')
# calendar
rep('PRODID:-//Python Course//EN', 'PRODID:-//Rust Course//EN')
rep('"UID:python-study-"+first+"@python-control-center"', '"UID:rust-study-"+first+"@rust-course"')
rep('SUMMARY:Python study session', 'SUMMARY:Rust study session')
rep('DESCRIPTION:Open your Python Course.', 'DESCRIPTION:Open your Rust Course.')
rep('DESCRIPTION:Python study session in 10 minutes', 'DESCRIPTION:Rust study session in 10 minutes')
rep('python-study.ics', 'rust-study.ics', 2)
rep('dl("python-progress.json"', 'dl("rust-progress.json"')
rep('dl("python-course-progress-"+today()+".json",JSON.stringify({app:"python-course"', 'dl("rust-course-progress-"+today()+".json",JSON.stringify({app:"rust-course"')
# TA prompts
rep("university-style Python course. Grade", "university-style Rust course. Grade")
rep("idiomatic (Pythonic for the level;", "idiomatic (idiomatic Rust for the level, such as borrowing instead of cloning and Result instead of panics;")
rep('of a university-style Python course ("', 'of a university-style Rust course ("')
rep('placeholder=\\"For example: why does input() give me text instead of a number?\\"', 'placeholder=\\"For example: why does the compiler say this value was moved?\\"')
# courses and years
rep_re(r"var COURSES=\[.*?\n\];", "var COURSES=" + js(courses) + ";")
# grades view: no certification, honest note
rep_re(r'  var certs=\["pcep","pcap"\].*?\n  \}\)\.join\(""\);\n', '  var certs="";\n')
rep('Your course grades, exams and certification practice.', 'Your course grades, quizzes and exams.')
rep('Exercises score 100 when solved unaided or when all tests pass, 70 when you used the solution, or your TA score if higher.',
    'Exercises score 100 when solved unaided, 70 when you used the solution, or your TA score if higher.')
rep_re(r'    "<h2 class=\\"sect\\">Certification prep</h2><div class=\\"grid2\\">"\+certs\+"</div>"\+\n', '')
rep_re(r'"<p class=\\"note\\" style=\\"margin-top:16px\\">Grades here track your own progress\..*?</p>"',
       '"<p class=\\"note\\" style=\\"margin-top:16px\\">Grades here track your own progress. Rust has no widely recognised certification, so employers judge Rust skills by your code: the Track 3 projects and the minigrep and web server repositories are what to show.</p>"')

# editor: Rust Playground instead of an in-page runner
new_editor = r'''function playUrl(code){return "https://play.rust-lang.org/?version=stable&mode=debug&edition=2024&code="+encodeURIComponent(code||"");}
function editorBlock(i,e){
  var c=exC(i.id,e.id)||{},lang=c.lang||"rust",isRs=lang==="rust";
  if(!isRs&&!taAvailable())return "";
  var r=RUNOUT[e.id]||{},val=CODE[e.id]!=null?CODE[e.id]:"";
  var ph=isRs?"Paste your finished code from your IDE here, or write it here and test it in the Playground. Submit it to the TA for a grade.":"Paste your work here (commands, Cargo.toml, a written answer) for TA feedback.";
  var out="<div class=\"ed\" data-ed=\""+e.id+"\"><div class=\"ed-h\"><span class=\"lbl\">"+(isRs?"Your code":"Your work")+"</span>"+
    (S.ta&&S.ta[e.id]?"<span class=\"note\">TA score: "+S.ta[e.id].score+"</span>":"")+"</div>"+
    "<textarea class=\"code-ed\" id=\"ed-"+e.id+"\" data-lang=\""+lang+"\" data-code=\""+e.id+"\" spellcheck=\"false\" autocapitalize=\"off\" autocomplete=\"off\" placeholder=\""+esc(ph)+"\">"+esc(val)+"</textarea>";
  out+="<div class=\"ed-act\">"+(isRs?"<a class=\"btn small\" id=\"pl-"+e.id+"\" href=\""+esc(playUrl(val))+"\" target=\"_blank\" rel=\"noopener\" title=\"Try your code. Nothing is graded.\">Test in Rust Playground</a>":"")+
    "<span class=\"sub\">"+(taAvailable()?"<button class=\"btn small primary\" data-act=\"tareview\" data-id=\""+e.id+"\" title=\"The TA grades your answer\""+(r.taBusy?" disabled":"")+">Submit to TA</button>":"")+"</span></div>"+
    (isRs?"<p class=\"note\" style=\"margin:0\">Test in your IDE or the Playground; nothing is graded until you submit. In the Playground, Run runs main; for #[test] functions choose Test from the menu next to Run (in your IDE: cargo test).</p>":"");
  if(r.ta){var t=r.ta,rb=t.rubric||{};
    out+="<div class=\"tafb\"><div class=\"ta-h\"><b>TA review</b><span class=\"ta-score\">"+esc(String(t.score))+"/100</span></div>"+
      "<div class=\"rub\">"+["correctness","readability","robustness","idiomatic"].map(function(k){return "<span>"+k+" <b>"+(rb[k]!=null?rb[k]:"-")+"/5</b></span>";}).join("")+"</div>"+
      (t.summary?"<p>"+esc(t.summary)+"</p>":"")+
      (t.strengths&&t.strengths.length?"<p class=\"lbl\">Strengths</p><ul>"+t.strengths.map(function(s){return "<li>"+esc(s)+"</li>";}).join("")+"</ul>":"")+
      (t.improvements&&t.improvements.length?"<p class=\"lbl\">To improve</p><ul>"+t.improvements.map(function(s){return "<li>"+esc(s)+"</li>";}).join("")+"</ul>":"")+
      (t.next_step?"<p><b>Next step:</b> "+esc(t.next_step)+"</p>":"")+"</div>";}
  else if(r.taBusy)out+="<p class=\"note\">The TA is reading your work. This can take up to a minute.</p>";
  else if(r.taErr)out+="<p class=\"note\">"+esc(r.taErr)+"</p>";
  return out+"</div>";
}
'''
a = src.index("function editorBlock(i,e){")
b = src.index("function askBlock(i){")
src = src[:a] + new_editor + src[b:]
# keep the Playground link in sync while typing
rep('document.addEventListener("input",function(e){\n  var el=e.target;', 'document.addEventListener("input",function(e){\n  var el=e.target;\n  if(e.target&&e.target.dataset&&e.target.dataset.code){var pl=document.getElementById("pl-"+e.target.dataset.code);if(pl)pl.href=playUrl(e.target.value);}')
# worked examples get a Playground link too
rep('return "<section class=\\"eg\\"><h4>Worked example"+(DEEP[i.id]?" 1":"")+"</h4>"+(x.title?"<p class=\\"egt\\">"+esc(x.title)+"</p>":"")+codeBlock(x.code,x.lang,"eg|"+i.id,x.lang)+',
    'return "<section class=\\"eg\\"><h4>Worked example"+(DEEP[i.id]?" 1":"")+"</h4>"+(x.title?"<p class=\\"egt\\">"+esc(x.title)+"</p>":"")+codeBlock(x.code,x.lang,"eg|"+i.id,x.lang)+(x.lang==="rust"&&!/^\\s*\\/\\/ --- /m.test(x.code)?"<div class=\\"row\\"><a class=\\"btn small\\" href=\\""+esc(playUrl(x.code))+"\\" target=\\"_blank\\" rel=\\"noopener\\">Open example in Rust Playground</a></div>":"")+')
rep('codeBlock(x.code,x.lang,"dx|"+i.id+"|"+k,x.lang)+',
    'codeBlock(x.code,x.lang,"dx|"+i.id+"|"+k,x.lang)+(x.lang==="rust"?"<div class=\\"row\\"><a class=\\"btn small\\" href=\\""+esc(playUrl(x.code))+"\\" target=\\"_blank\\" rel=\\"noopener\\">Open in Rust Playground</a></div>":"")+')
# the TA review prompt mentions automated tests; there are none here
rep('"Automated test results: "+(tests||"not run")+"\\n\\n"+', '"The student runs code in the Rust Playground; no automated test results are attached.\\n\\n"+')
# Ctrl+Enter used to run Python: make it open the Playground link instead
rep('else if(e.key==="Enter"&&(e.ctrlKey||e.metaKey)){e.preventDefault();doRun(el.dataset.code,GRADE[el.dataset.code]&&e.shiftKey?"check":"run");}',
    'else if(e.key==="Enter"&&(e.ctrlKey||e.metaKey)){e.preventDefault();var pl=document.getElementById("pl-"+el.dataset.code);if(pl)window.open(pl.href,"_blank","noopener");}')

# ---------------- Rust editor and polish layers ----------------
rep('if(lang!=="python"&&lang!=="pycon")return;', 'if(lang!=="rust")return;')
rep('window.hljs.highlight(code,{language:"python",ignoreIllegals:true})', 'window.hljs.highlight(code,{language:"rust",ignoreIllegals:true})')
rep(r'if(/:\s*(#.*)?$/.test(line)&&!/^\s*#/.test(line))ind+="    ";', r'if(/[{(\[]\s*(\/\/.*)?$/.test(line)&&!/^\s*\/\//.test(line))ind+="    ";')
rep(r'return /^\s*#/.test(l);});', r'return /^\s*\/\//.test(l);});')
rep(r'return on?l.replace(/^(\s*)# ?/,"$1"):l.slice(0,ind4)+"# "+l.slice(ind4);', r'return on?l.replace(/^(\s*)\/\/ ?/,"$1"):l.slice(0,ind4)+"// "+l.slice(ind4);')
rep('}else if(e.key==="Backspace"&&s===en&&s>0){', '}else if(e.key==="}"&&s===en&&/^ {4,}$/.test(v.slice(ls(s),s))){stop();editText(ta,s-4,s,"}");\n  }else if(e.key==="Backspace"&&s===en&&s>0){')
rep('<kbd>Enter</kbd> run</span>', '<kbd>Enter</kbd> open in Playground</span>')
rep('}else if(ch==="#"){break;}', '}else if(ch==="/"&&l[k+1]==="/"){break;}')
rep("<li>Run the worked example again and change one thing at a time.</li><li>Read the error from the bottom up, then use <b>Go to line</b> under the editor.</li>",
    "<li>Open the worked example in the Rust Playground and change one thing at a time.</li><li>Read the compiler error from the top: it names the line and usually the fix. <code>rustc --explain E0382</code> explains any error code.</li>")
rep('<div><dt>Submissions</dt><dd>"+w.att+" "+delta(w.att,p.att)+"</dd></div><div><dt>Passed on the first try</dt><dd>"+rate+"<small>"+w.firstOk+" of "+w.first+" new exercises</small></dd></div>', '')
rep('+", first-try pass rate "+rate', '')
rep('"<p class=\\"note\\">No failed submissions in the last 7 days.</p>"', '""')
rep('python-course-answers', 'rust-course-answers', 3)
rep('# My Python Course answers', '# My Rust Course answers')
rep('var EXT={python:".py",', 'var EXT={rust:".rs",python:".py",')
rep('text:"# "+x.id+" "+x.t+"\\n"+v', 'text:(lang==="rust"?"// ":"# ")+x.id+" "+x.t+"\\n"+v')
rep('var c=exC(it.id,x.id)||{},lang=c.lang||"python";', 'var c=exC(it.id,x.id)||{},lang=c.lang||"rust";')
rep("try 'dictionary', 'tkinter' or 7.4", "try 'borrow', 'trait' or 4.2")
rep('"pycc.review"', '"rscc.review"', 2)
rep('"pycc.edfs"', '"rscc.edfs"', 2)
assert "Pyodide" not in src.split("/* ================= code drafts")[1][:200]
open(out_path, "w", encoding="utf-8").write(src)
n_items = sum(len(m["items"]) for t in mods.values() for m in t)
n_ex = sum(len(i["ex"]) for t in mods.values() for m in t for i in m["items"])
n_q = sum(len(v) for v in quiz.values())
print(f"built {out_path}: {sum(len(v) for v in mods.values())} modules, {n_items} lessons, {n_ex} exercises, {n_q} questions, {len(courses)} courses, {len(src)//1024} KB")
