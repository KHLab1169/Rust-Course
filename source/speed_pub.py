"""Final step before publishing: move the course content from a JavaScript object literal into a
JSON data block that the page parses with JSON.parse (much faster to parse than the same object as
script source), and defer nothing else. The source page keeps the literal form, which every build
script edits. usage: python3 speed_pub.py in.html out.html"""
import json, sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()
key = "<script>window.PYCC_CONTENT="
i = s.find(key)
assert i >= 0, "content block not found"
j = s.find(";</script>", i)
c = json.loads(s[i + len(key):j].replace("<\\!", "<!"))
data = json.dumps(c, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
block = ('<script type="application/json" id="pycc-content">' + data + "</script>\n"
         '<script>window.PYCC_CONTENT=JSON.parse(document.getElementById("pycc-content").textContent);</script>')
s = s[:i] + block + s[j + len(";</script>"):]
open(dst, "w", encoding="utf-8").write(s)
print(f"{dst}: {len(s.encode()) / 1e6:.2f} MB")
