/* DLTESTS:BEGIN */
var GRADER_SRC=null;
function graderSrc(){
  if(GRADER_SRC)return Promise.resolve(GRADER_SRC);
  return fetch("py-worker.js").then(function(r){if(!r.ok)throw new Error("status "+r.status);return r.text();}).then(function(t){
    var m=t.match(/^const GRADER = (".*");\s*$/m);if(!m)throw new Error("grader not found");GRADER_SRC=JSON.parse(m[1]);return GRADER_SRC;});
}
function pyTestFile(eid,info,spec,src){
  var q=function(s){return JSON.stringify(s);};
  return '"""Tests for exercise '+eid+' ('+info.e.t.replace(/"/g,"'")+') from the Python Course.\n\n'+
    'Your answer is in solution.py next to this file. Edit it, then run:\n\n    python -m pytest -q\n\n'+
    'These are the same tests the course page runs, checked by the course\'s own grader\n(embedded at the bottom of this file). Needs pytest (pip install pytest). The course runs Python 3.14;\nmost exercises also work on 3.10 or newer.\n"""\n'+
    'import json\nimport pathlib\n\nimport pytest\n\nHERE = pathlib.Path(__file__).resolve().parent\n'+
    'SPEC = json.loads('+q(JSON.stringify({main:!!spec.main,cases:spec.cases}))+')\n\n\n'+
    '@pytest.mark.parametrize("case", SPEC["cases"], ids=[c.get("name", str(i)) for i, c in enumerate(SPEC["cases"])])\n'+
    'def test_exercise(case):\n'+
    '    code = (HERE / "solution.py").read_text(encoding="utf-8")\n'+
    '    result = json.loads(_GRADER["grade"](code, {"main": SPEC["main"], "cases": [case]}))[0]\n'+
    '    if not result["ok"]:\n'+
    '        msg = result["msg"]\n'+
    '        if result.get("detail"):\n'+
    '            msg += "\\n" + "\\n".join(result["detail"])\n'+
    '        if result.get("out"):\n'+
    '            msg += "\\n--- your program printed ---\\n" + result["out"]\n'+
    '        pytest.fail(msg, pytrace=False)\n\n\n'+
    '# The course grader, unchanged. It runs your code fresh for every test in a temporary folder.\n'+
    'GRADER_SOURCE = '+q(src)+'\n'+
    '_GRADER = {"__name__": "course_grader"}\n'+
    'exec(compile(GRADER_SOURCE, "course_grader.py", "exec"), _GRADER)\n';
}
function testBundle(eid,code){
  var info=exInfo(eid),spec=GRADE[eid];if(!info||!spec)return Promise.reject(new Error("no tests"));
  var dir=eid.replace(/\./g,"_")+"-"+slug(info.e.t)+"/";
  return graderSrc().then(function(src){return {name:dir.slice(0,-1)+"-pytest.zip",files:[
    {name:dir+"solution.py",text:(code&&code.trim()?code:(spec.starter||"")).replace(/\s*$/,"\n")},
    {name:dir+"test_solution.py",text:pyTestFile(eid,info,spec,src)}]};});
}
async function downloadTests(eid){
  if(!DL){toast("Downloads are not available in this view.");return;}
  var ta=document.getElementById("ed-"+eid),code=ta?ta.value:(CODE[eid]||"");
  var b;try{b=await testBundle(eid,code);}catch(e){toast("Couldn't build the test files here.");return;}
  try{await DL.save({filename:b.name,data:zip(b.files)});toast("Saved "+b.name+". Unzip it and follow the note at the top of the test file.");}
  catch(e){if(e&&e.code==="declined")return;toast("Could not save the file here.");}
}
document.addEventListener("click",function(e){
  var b=e.target.closest&&e.target.closest("[data-act=\"dltests\"]");if(!b)return;downloadTests(b.dataset.id);
});
/* DLTESTS:END */
