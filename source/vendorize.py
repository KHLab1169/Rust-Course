"""Point a published course page at the app's local copies of fonts and highlight.js (works offline).
usage: python3 vendorize.py published.html app/index.html"""
import re, sys

s = open(sys.argv[1], encoding="utf-8").read()
s = s.replace("https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js", "vendor/highlight.min.js")
links = re.findall(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^"]*"[^>]*>\n?', s)
for k, l in enumerate(links):
    s = s.replace(l, '<link rel="stylesheet" href="vendor/fonts.css">\n' if k == 0 else "", 1)
open(sys.argv[2], "w", encoding="utf-8").write(s)
print(sys.argv[2], "fonts and highlight.js now local;", len(links), "font links replaced")
