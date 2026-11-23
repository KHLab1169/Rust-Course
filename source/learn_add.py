"""Learning features for the course engine: flashcards (spaced review of quick checks) and
a mistakes notebook (exercises still failing, quick checks answered wrong).

Both panels go on the Overview, after "Reviews due". State lives in S.fc (Leitner boxes).
usage: python3 learn_add.py course.html   (idempotent)
"""
import sys

CSS = r"""/* LEARN:BEGIN */
.fc-top{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.fc-top .n{font-family:var(--font-display,inherit);font-size:1.9rem;font-weight:800;letter-spacing:-.03em;line-height:1}
.fc-top .s{color:var(--muted);font-size:.86rem;flex:1;min-width:160px}
.fc-boxes{display:flex;gap:4px;margin:14px 0 2px;align-items:flex-end}
.fc-boxes span{flex:1;display:grid;gap:3px;justify-items:center;font-size:.62rem;font-weight:700;color:var(--muted)}
.fc-boxes em{font-style:normal;color:var(--ink);font-weight:800}
.fc-boxes i{display:block;width:100%;border-radius:6px 6px 3px 3px;background:var(--brand-grad,var(--blue));min-height:3px;opacity:.85}
.fc-card{margin-top:12px;border:1px solid var(--line);border-radius:var(--r-md,12px);padding:14px 14px 12px;background:var(--raised)}
.fc-card .meta{display:flex;justify-content:space-between;gap:8px;font-size:.72rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px}
.fc-card .meta button{all:unset;cursor:pointer;color:var(--blue);text-transform:none;letter-spacing:0;font-weight:600}
.fc-card .meta button:focus-visible{outline:2px solid var(--blue);outline-offset:2px;border-radius:4px}
.fc-card .q{margin:0 0 10px;font-weight:600}
.fc-card pre{margin:0 0 10px;padding:10px 12px;background:var(--code-bg,var(--surface));border:1px solid var(--line);border-radius:var(--r-sm,9px);overflow-x:auto;font-size:.84rem}
.fc-card .qcopts{display:grid;gap:6px}
.fc-card .qcx{margin:10px 0 0}
.fc-act{display:flex;gap:8px;margin-top:12px;flex-wrap:wrap}
.fc-done{margin-top:12px;padding:12px 14px;border-radius:var(--r-md,12px);background:color-mix(in srgb,var(--good) 12%,var(--surface));font-weight:600}
.mk-list{list-style:none;margin:8px 0 0;padding:0;display:grid;gap:6px}
.mk-list li{display:grid;grid-template-columns:auto 1fr auto;gap:10px;align-items:center;padding:9px 10px;border:1px solid var(--line);border-radius:var(--r-sm,9px);background:var(--surface)}
.mk-list .ic{width:26px;height:26px;border-radius:8px;display:grid;place-items:center;font-size:.8rem;font-weight:800;background:color-mix(in srgb,var(--bad,#DC2626) 14%,var(--surface));color:var(--bad,#DC2626)}
.mk-list .ic.q{background:color-mix(in srgb,var(--warn) 16%,var(--surface));color:var(--warn)}
.mk-list .tx{min-width:0}
.mk-list .tx b{display:block;font-size:.88rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.mk-list .tx small{display:block;color:var(--muted);font-size:.76rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.mk-list .tx small code{font-size:.74rem}
.mk-h{margin:14px 0 0;font-size:.7rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--muted)}
.mk-more{margin-top:6px}
.mk-more>summary{cursor:pointer;color:var(--blue);font-size:.84rem;font-weight:600;padding:4px 0}
/* LEARN:END */
"""

JS = r"""/* LEARN:BEGIN */
var FC_INT=[1,3,7,14,30,60],FCS=null;
function fcAll(){
  var out=[];
  ITEMS.forEach(function(i){
    if(!S.done[i.id])return;
    (CHECKS[i.id]||[]).forEach(function(q,k){out.push({key:i.id+"|"+k,it:i,q:q.q,code:q.code||"",options:q.options,answer:q.answer,explain:q.explain,md:false});});
    var d=DEEP[i.id];
    if(d&&d.examples)d.examples.forEach(function(x,k){var c=x.check;if(!c)return;out.push({key:i.id+"|x"+k,it:i,q:c.q,code:x.code||"",options:c.options,answer:c.answer,explain:c.explain,md:true});});
  });
  return out;
}
function fcState(c){
  S.fc=S.fc||{};var f=S.fc[c.key];if(f)return f;
  var ch=S.qc[c.key],t=today();
  if(ch!=null&&ch!==c.answer)return {box:0,due:t,implicit:1};
  if(ch==null)return {box:0,due:t,implicit:1};
  var base=S.done[c.it.id]||t;return {box:1,due:addDays(base,FC_INT[1]),implicit:1};
}
function fcDue(){var t=today();return fcAll().filter(function(c){return fcState(c).due<=t;});}
function fcPanel(){
  var all=fcAll(),t=today();
  if(!all.length)return "<section class=\"panel\" id=\"fcpanel\"><h2>Flashcards</h2><p class=\"note\">Finish a lesson and its quick checks become flashcards here, brought back on a spaced schedule (1, 3, 7, 14, 30 and 60 days).</p></section>";
  var due=all.filter(function(c){return fcState(c).due<=t;}),boxes=[0,0,0,0,0,0];
  all.forEach(function(c){boxes[Math.min(5,fcState(c).box)]++;});
  var mx=Math.max.apply(null,boxes)||1;
  var bx="<div class=\"fc-boxes\" role=\"img\" aria-label=\"Cards per box: "+boxes.join(", ")+"\">"+boxes.map(function(n,k){return "<span><i style=\"height:"+Math.max(3,Math.round(n/mx*26))+"px\"></i>"+(k===5?"60d":FC_INT[k]+"d")+" <em>"+n+"</em></span>";}).join("")+"</div>";
  var body;
  if(FCS&&FCS.q.length){body=fcCard();}
  else if(FCS&&FCS.fin){body="<div class=\"fc-done\" role=\"status\">Session done: "+FCS.right+" of "+FCS.seen+" right. Cards you missed come back tomorrow.</div>";}
  else body="";
  return "<section class=\"panel\" id=\"fcpanel\"><h2>Flashcards</h2><div class=\"fc-top\"><span class=\"n\">"+due.length+"</span><span class=\"s\">"+(due.length?"card"+(due.length===1?"":"s")+" due today, from "+all.length+" in your deck.":"Nothing due. "+all.length+" cards in your deck.")+"</span>"+
    (FCS&&FCS.q.length?"":"<button type=\"button\" class=\"btn"+(due.length?" primary":"")+"\" data-act=\"fcstart\""+(due.length?"":" data-v=\"all\"")+">"+(due.length?"Review "+Math.min(due.length,20)+" now":"Practise anyway")+"</button>")+"</div>"+bx+body+"</section>";
}
function fcCard(){
  var c=FCS.q[0],ch=FCS.pick,done=ch!=null,f=fcState(c);
  var opts=c.options.map(function(o,n){
    var cls=done?(n===c.answer?" right":n===ch?" wrong":""):"";
    return "<button type=\"button\" class=\"qcopt"+(c.md?" dxopt":"")+cls+"\" data-act=\"fcpick\" data-n=\""+n+"\""+(done?" disabled":"")+">"+(c.md?md(o):"<code>"+esc(o)+"</code>")+"</button>";
  }).join("");
  return "<div class=\"fc-card\" aria-live=\"polite\"><div class=\"meta\"><span>Card "+(FCS.seen+1)+" of "+(FCS.seen+FCS.q.length)+" &middot; box "+(f.box+1)+"</span><button type=\"button\" data-act=\"open\" data-id=\""+esc(c.it.id)+"\">"+esc(c.it.id+" "+c.it.t)+"</button></div>"+
    "<p class=\"q\">"+(c.md?md(c.q):esc(c.q))+"</p>"+(c.code?"<pre><code>"+esc(c.code)+"</code></pre>":"")+"<div class=\"qcopts\">"+opts+"</div>"+
    (done?"<p class=\"qcx "+(ch===c.answer?"ok":"no")+"\"><b>"+(ch===c.answer?"Right.":"Not quite.")+"</b> "+(c.md?md(c.explain):esc(c.explain))+"</p>":"")+
    "<div class=\"fc-act\">"+(done?"<button type=\"button\" class=\"btn primary\" data-act=\"fcnext\">"+(FCS.q.length>1?"Next card":"Finish")+"</button>":"")+"<button type=\"button\" class=\"btn\" data-act=\"fcstop\">End session</button></div></div>";
}
function fcRefresh(focusSel){
  var el=document.getElementById("fcpanel");if(!el)return;
  var w=document.createElement("div");w.innerHTML=fcPanel();el.replaceWith(w.firstChild);
  var mk=document.getElementById("mkpanel");if(mk){var w2=document.createElement("div");w2.innerHTML=mistakesPanel();mk.replaceWith(w2.firstChild);}
  if(focusSel){var f=document.querySelector("#fcpanel "+focusSel);if(f)f.focus({preventScroll:true});}
}
function mistakesData(){
  var last={},cnt={};
  (S.alog||[]).forEach(function(a){if(a[2]<a[3]){last[a[1]]=a;cnt[a[1]]=(cnt[a[1]]||0)+1;}else{delete last[a[1]];}});
  var exs=Object.keys(last).filter(function(eid){return !S.ex[eid]&&exInfo(eid);}).map(function(eid){var a=last[eid];return {eid:eid,info:exInfo(eid),date:a[0],p:a[2],n:a[3],name:a[4],cnt:cnt[eid]};})
    .sort(function(x,y){return x.date<y.date?1:x.date>y.date?-1:0;});
  S.fc=S.fc||{};
  var qs=[];
  ITEMS.forEach(function(i){
    (CHECKS[i.id]||[]).forEach(function(q,k){var key=i.id+"|"+k,ch=S.qc[key];if(ch!=null&&ch!==q.answer&&!((S.fc[key]||{}).box>=2))qs.push({key:key,it:i,q:q.q,yours:q.options[ch],right:q.options[q.answer]});});
    var d=DEEP[i.id];if(d&&d.examples)d.examples.forEach(function(x,k){var c=x.check,key=i.id+"|x"+k;if(!c)return;var ch=S.qc[key];if(ch!=null&&ch!==c.answer&&!((S.fc[key]||{}).box>=2))qs.push({key:key,it:i,q:c.q,yours:c.options[ch],right:c.options[c.answer]});});
  });
  return {exs:exs,qs:qs};
}
function mkStrip(s){return String(s||"").replace(/[`*_]/g,"");}
function mistakesPanel(){
  var m=mistakesData();
  if(!m.exs.length&&!m.qs.length)return "<section class=\"panel\" id=\"mkpanel\"><h2>Mistakes notebook</h2><p class=\"note\">Exercises you have not passed yet and quick checks you got wrong collect here, so you can go back to them. Nothing here right now.</p></section>";
  function exRow(x){return "<li><span class=\"ic\" aria-hidden=\"true\">✗</span><span class=\"tx\"><b>"+esc(x.info.e.t)+"</b><small>"+x.p+"/"+x.n+" tests passed"+(x.name?" &middot; failing: <code>"+esc(x.name)+"</code>":"")+" &middot; "+x.cnt+" failed run"+(x.cnt===1?"":"s")+"</small></span><button type=\"button\" class=\"btn\" data-act=\"open\" data-id=\""+esc(x.info.it.id)+"\" aria-label=\"Open "+esc(x.info.it.id)+" to retry "+esc(x.info.e.t)+"\">Retry</button></li>";}
  function qRow(x){return "<li><span class=\"ic q\" aria-hidden=\"true\">?</span><span class=\"tx\"><b>"+esc(mkStrip(x.q))+"</b><small>You said <code>"+esc(mkStrip(x.yours))+"</code> &middot; answer <code>"+esc(mkStrip(x.right))+"</code></small></span><button type=\"button\" class=\"btn\" data-act=\"open\" data-id=\""+esc(x.it.id)+"\" aria-label=\"Open lesson "+esc(x.it.id)+"\">"+esc(x.it.id)+"</button></li>";}
  function list(arr,fn,cap){var a=arr.slice(0,cap).map(fn).join(""),b=arr.slice(cap).map(fn).join("");return "<ul class=\"mk-list\">"+a+"</ul>"+(b?"<details class=\"mk-more\"><summary>Show "+(arr.length-cap)+" more</summary><ul class=\"mk-list\">"+b+"</ul></details>":"");}
  return "<section class=\"panel\" id=\"mkpanel\"><h2>Mistakes notebook</h2><p class=\"note\">What you have not got right yet. Exercises leave when they pass; quick checks leave once you get them right twice in flashcards.</p>"+
    (m.exs.length?"<p class=\"mk-h\">Exercises still failing ("+m.exs.length+")</p>"+list(m.exs,exRow,4):"")+
    (m.qs.length?"<p class=\"mk-h\">Quick checks missed ("+m.qs.length+")</p>"+list(m.qs,qRow,4):"")+"</section>";
}
document.addEventListener("click",function(e){
  var b=e.target.closest&&e.target.closest("[data-act^=\"fc\"]");if(!b)return;
  var a=b.dataset.act,t=today();S.fc=S.fc||{};
  if(a==="fcstart"){var pool=b.dataset.v==="all"?fcAll().sort(function(x,y){return fcState(x).due<fcState(y).due?-1:1;}):fcDue();
    pool=pool.sort(function(){return Math.random()-.5;}).slice(0,20);FCS={q:pool,pick:null,seen:0,right:0};fcRefresh(".qcopt");}
  else if(a==="fcpick"&&FCS&&FCS.q.length&&FCS.pick==null){var c=FCS.q[0],n=+b.dataset.n,f=fcState(c),ok=n===c.answer;
    FCS.pick=n;var box=ok?Math.min(5,f.box+1):0;S.fc[c.key]={box:box,due:addDays(t,ok?FC_INT[box]:1),last:t};
    if(ok)FCS.right++;if(S.qc[c.key]==null)S.qc[c.key]=n;bump(1);save();fcRefresh("[data-act=\"fcnext\"]");}
  else if(a==="fcnext"&&FCS){FCS.q.shift();FCS.seen++;FCS.pick=null;if(!FCS.q.length)FCS.fin=1;fcRefresh(FCS.q.length?".qcopt":null);}
  else if(a==="fcstop"){FCS=null;fcRefresh("[data-act=\"fcstart\"]");}
});
/* LEARN:END */
"""

ANCHOR_JS = "/* ================= expanded lessons ================= */"
OVR = '"<section class=\\"panel\\" id=\\"reviews\\"><h2>Reviews due</h2>"+revHtml+"</section>"+'


def strip_block(s):
    while "/* LEARN:BEGIN */" in s:
        a = s.index("/* LEARN:BEGIN */")
        b = s.index("/* LEARN:END */", a) + len("/* LEARN:END */\n")
        s = s[:a] + s[b:]
    return s


def main(path):
    s = strip_block(open(path, encoding="utf-8").read())
    assert ANCHOR_JS in s and OVR in s
    s = s.replace(ANCHOR_JS, JS + ANCHOR_JS, 1)
    if "fcPanel()+mistakesPanel()" not in s:
        s = s.replace(OVR, OVR + '\n  fcPanel()+mistakesPanel()+', 1)
    i = s.rindex("</style>")
    s = s[:i] + CSS + s[i:]
    open(path, "w", encoding="utf-8").write(s)
    print("learning features added to", path)


if __name__ == "__main__":
    main(sys.argv[1])
