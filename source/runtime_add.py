"""Python runtime safety net.

Pyodide 314 must run in a module worker. If a browser or host blocks that (the worker errors or
reports a failure before it is ready), the page loads Pyodide itself and runs the same grader on the
main thread. That is slower, and a runaway loop can freeze the tab, so it is only a fallback.
usage: python3 runtime_add.py course.html   (idempotent)
"""
import sys

OLD_START = 'function pyStart(){\n  if(PY.ready)return PY.ready;\n  PY.ready=new Promise(function(res,rej){\n    var w;\n    try{w=new Worker("py-worker.js",{type:"module"});}catch(e){PY.failed=true;rej(e);return;}'
NEW_START = '''/* RUNTIME:BEGIN */
function pyInPage(){
  var base=new URL("pyodide/",document.baseURI).href;
  return Promise.all([import(base+"pyodide.mjs"),graderSrc()]).then(function(r){
    return r[0].loadPyodide({indexURL:base,stdLibURL:base+"python_stdlib.zip.wasm"}).then(function(py){
      py.runPython(r[1]);
      var fw={inPage:true,onmessage:null,terminate:function(){},postMessage:function(m){
        setTimeout(function(){
          var out;
          try{
            var fn=py.globals.get(m.type);
            out={id:m.id,result:m.type==="run"?fn(m.code,m.stdin||""):m.type==="grade"?fn(m.code,m.spec):fn(m.code)};
          }catch(e){out={id:m.id,error:String(e&&e.message||e)};}
          if(fw.onmessage)fw.onmessage({data:out});
        },0);
      }};
      return fw;
    });
  });
}
function pyStart(){
  if(PY.ready)return PY.ready;
  if(PY.pageFw){PY.w=PY.pageFw;PY.ready=Promise.resolve(PY.pageFw);return PY.ready;}   // keep the in-page runtime once loaded
  PY.ready=new Promise(function(res,rej){
    var settled=false;
    function viaPage(why){
      if(settled)return;settled=true;
      try{PY.w&&PY.w.terminate();}catch(e){}
      PY.status="in-page";
      if(typeof console!=="undefined")console.warn("Python worker unavailable ("+why+"); running Python in the page instead.");
      pyInPage().then(function(fw){
        PY.w=fw;PY.pageFw=fw;
        fw.onmessage=function(ev){var m=ev.data||{},p=PY.pending[m.id];if(p){delete PY.pending[m.id];clearTimeout(p.t);p.res(m);}};
        toast("Python is running inside the page because this browser blocked the background runner. It works, but long programs make the page wait.");
        res(fw);
      },function(e){PY.failed=true;rej(e);});
    }
    var w;
    try{w=new Worker("py-worker.js",{type:"module"});}catch(e){viaPage(String(e&&e.message||e));return;}'''
OLD_TAIL = '''    w.onmessage=function(ev){
      var m=ev.data||{};
      if(m.type==="ready"){clearTimeout(guard);res(w);return;}
      if(m.type==="fail"){clearTimeout(guard);PY.failed=true;rej(new Error(m.error||"Python could not start"));return;}
      var p=PY.pending[m.id];
      if(p){delete PY.pending[m.id];clearTimeout(p.t);p.res(m);}
    };
    w.onerror=function(e){clearTimeout(guard);PY.failed=true;rej(e);};'''
NEW_TAIL = '''    w.onmessage=function(ev){
      var m=ev.data||{};
      if(m.type==="ready"){clearTimeout(guard);if(!settled){settled=true;PY.status="worker";res(w);}return;}
      if(m.type==="fail"){clearTimeout(guard);viaPage(m.error||"failed");return;}
      var p=PY.pending[m.id];
      if(p){delete PY.pending[m.id];clearTimeout(p.t);p.res(m);}
    };
    w.onerror=function(e){clearTimeout(guard);if(!settled)viaPage((e&&e.message)||"worker error");};
/* RUNTIME:END */'''


def main(path):
    s = open(path, encoding="utf-8").read()
    if "/* RUNTIME:BEGIN */" in s:
        a = s.index("/* RUNTIME:BEGIN */\n")
        b = s.index("/* RUNTIME:END */", a) + len("/* RUNTIME:END */")
        old = s[a:b]
        s = s[:a] + OLD_START + old[old.index('try{w=new Worker("py-worker.js",{type:"module"});}catch(e){viaPage(String(e&&e.message||e));return;}') + len('try{w=new Worker("py-worker.js",{type:"module"});}catch(e){viaPage(String(e&&e.message||e));return;}'):old.index("    w.onmessage=function(ev){")] + OLD_TAIL + s[b:]
    if True:
        assert OLD_START in s and OLD_TAIL in s
        s = s.replace(OLD_START, NEW_START, 1).replace(OLD_TAIL, NEW_TAIL, 1)
    open(path, "w", encoding="utf-8").write(s)
    print("runtime fallback in", path)


if __name__ == "__main__":
    main(sys.argv[1])
