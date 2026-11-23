"""Mix the order of quiz options.

Many quiz banks were written with the right answer first. This shuffles each question's options
once at load (the same order every time for a given question, so reviews stay consistent) and
remaps its answer indexes. Quick checks are left alone: their saved answers are option indexes.
usage: python3 quizmix_add.py course.html   (idempotent)
"""
import sys

OLD = 'var QUIZ=(window.PYCC_CONTENT||{}).quiz||{},CERT=(window.PYCC_CONTENT||{}).cert||{};\n'
JS = OLD + r'''/* QUIZMIX:BEGIN */
(function(){
  function mix(q){
    if(!q||!Array.isArray(q.options)||!Array.isArray(q.answer)||q.options.length<2||q._mixed)return;
    var key=String(q.id||q.prompt||""),h=2166136261;
    for(var i=0;i<key.length;i++){h^=key.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}
    var order=q.options.map(function(_,i){return i;});
    for(var k=order.length-1;k>0;k--){h=(Math.imul(h,1103515245)+12345)>>>0;var j=(h>>>8)%(k+1),t=order[k];order[k]=order[j];order[j]=t;}
    q.options=order.map(function(i){return q.options[i];});
    q.answer=q.answer.map(function(a){return order.indexOf(a);}).sort(function(a,b){return a-b;});
    q._mixed=1;
  }
  Object.keys(QUIZ).forEach(function(m){(QUIZ[m]||[]).forEach(mix);});
  Object.keys(CERT).forEach(function(c){((CERT[c]||{}).questions||[]).forEach(mix);});
})();
/* QUIZMIX:END */
'''


def main(path):
    s = open(path, encoding="utf-8").read()
    if "/* QUIZMIX:BEGIN */" in s:
        a = s.index(OLD)
        b = s.index("/* QUIZMIX:END */\n", a) + len("/* QUIZMIX:END */\n")
        s = s[:a] + OLD + s[b:]
    assert OLD in s
    s = s.replace(OLD, JS, 1)
    open(path, "w", encoding="utf-8").write(s)
    print("quiz option mixing in", path)


if __name__ == "__main__":
    main(sys.argv[1])
