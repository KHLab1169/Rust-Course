/* TRYIT:BEGIN */
var TRY_PY=true,TRY_SRC={};
function tryBlock(key,x){
  if(!TRY_PY||(x.lang||"python")!=="python"||!x.code)return "";
  TRY_SRC[key]=x.code;
  var rows=Math.min(24,Math.max(4,x.code.split("\n").length+1));
  return "<details class=\"tryit\"><summary>Try it: run this example, then change it</summary>"+
    "<label class=\"sr-only\" for=\"try-"+esc(key)+"\">Example code to edit</label>"+
    "<textarea class=\"try-ed\" id=\"try-"+esc(key)+"\" data-try=\""+esc(key)+"\" rows=\""+rows+"\" spellcheck=\"false\" autocapitalize=\"off\" autocomplete=\"off\">"+esc(x.code)+"</textarea>"+
    "<div class=\"try-row\"><button type=\"button\" class=\"btn small primary\" data-act=\"tryrun\" data-key=\""+esc(key)+"\">Run</button>"+
    "<button type=\"button\" class=\"btn small\" data-act=\"tryreset\" data-key=\""+esc(key)+"\">Reset</button>"+
    "<span class=\"note\">Runs in the page (Python 3.14). Nothing here is graded or saved.</span></div>"+
    "<pre class=\"try-out\" data-tryout=\""+esc(key)+"\" role=\"status\" aria-live=\"polite\" hidden></pre></details>";
}
document.addEventListener("click",function(e){
  var b=e.target.closest&&e.target.closest("[data-act=\"tryrun\"],[data-act=\"tryreset\"]");if(!b)return;
  var key=b.dataset.key,box=b.closest(".tryit"),ta=box.querySelector(".try-ed"),out=box.querySelector(".try-out");
  if(b.dataset.act==="tryreset"){ta.value=TRY_SRC[key]||"";out.hidden=true;out.textContent="";return;}
  out.hidden=false;out.className="try-out";
  out.textContent=PY.w?"Running...":"Loading Python (first time only, about 14 MB)...";
  b.disabled=true;
  pyCall({type:"run",code:ta.value,stdin:""},15000).then(function(res){
    b.disabled=false;
    if(res.timeout){out.textContent="Stopped after 15 seconds. Check for a loop that never ends.";out.classList.add("err");return;}
    if(res.error){out.textContent=res.error;out.classList.add("err");return;}
    var r=JSON.parse(res.result),text=(r.out||"")+(r.err?(r.out&&!/\n$/.test(r.out)?"\n":"")+r.err:"");
    out.textContent=text||"(no output)";
    if(r.err)out.classList.add("err");
  },function(){b.disabled=false;out.textContent="Python could not start in this browser. Copy the code and run it on your computer.";out.classList.add("err");});
});
document.addEventListener("keydown",function(e){
  var ta=e.target;if(!ta||!ta.classList||!ta.classList.contains("try-ed"))return;
  if(e.key==="Tab"&&!e.shiftKey&&!e.ctrlKey&&!e.metaKey&&!e.altKey){
    e.preventDefault();var s=ta.selectionStart;ta.setRangeText("    ",s,ta.selectionEnd,"end");
  }else if(e.key==="Enter"&&(e.ctrlKey||e.metaKey)){
    e.preventDefault();var btn=ta.closest(".tryit").querySelector("[data-act=\"tryrun\"]");if(btn&&!btn.disabled)btn.click();
  }else if(e.key==="Escape"){ta.blur();}
},true);
/* TRYIT:END */
