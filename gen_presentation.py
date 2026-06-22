"""בונה מצגת HTML עצמאית: שקף לכל שאלה עם שליפה מלאה, שאלה, תשובת מודל ותשובת אמת."""
import json
import pandas as pd
from config import SEIFS_FILE

df = pd.read_csv("experiments/answer_eval.csv", encoding="utf-8-sig")
seifs = {s["ref"]: s for s in json.load(open(SEIFS_FILE, encoding="utf-8"))}

slides = []
for _, r in df.iterrows():
    gold_ref = str(r["מקור"])
    refs = str(r["ctx_refs"]).split()
    retrieved = [{"ref": rf, "text": seifs.get(rf, {}).get("text", "(לא נמצא)"),
                  "is_gold": rf == gold_ref} for rf in refs]
    slides.append({
        "id": int(r["id"]),
        "q": str(r["שאלה"]),
        "gold": str(r["תשובת_אמת"]),
        "rag": str(r["תשובת_RAG"]),
        "gold_ref": gold_ref,
        "ctx_hit": int(r["Ctx_hit"]),
        "contains": int(r["Contains"]),
        "retrieved": retrieved,
    })

data_json = json.dumps(slides, ensure_ascii=False)

html = """<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>הערכת RAG — קיצור שולחן ערוך</title>
<style>
  :root{ --bg:#0f1220; --card:#1a1f35; --ink:#eef1f7; --muted:#9aa3bd;
         --gold:#f4c542; --ok:#3ddc84; --bad:#ff6b6b; --line:#2c3354; --accent:#6ea8fe; }
  *{box-sizing:border-box} html,body{margin:0;height:100%}
  body{background:var(--bg);color:var(--ink);font-family:"Segoe UI",Arial,sans-serif;
       display:flex;flex-direction:column;height:100vh}
  header{padding:10px 18px;border-bottom:1px solid var(--line);display:flex;
         align-items:center;gap:14px;background:#141830}
  header h1{font-size:16px;margin:0;color:var(--muted);font-weight:600}
  .counter{font-size:14px;color:var(--muted)}
  .pill{font-size:12px;padding:3px 10px;border-radius:20px;font-weight:700}
  .pill.ok{background:rgba(61,220,132,.15);color:var(--ok)}
  .pill.bad{background:rgba(255,107,107,.15);color:var(--bad)}
  main{flex:1;overflow:auto;padding:22px;display:flex;justify-content:center}
  .slide{max-width:1000px;width:100%}
  .q{font-size:26px;font-weight:700;line-height:1.4;margin:0 0 18px}
  .ans{display:flex;gap:14px;margin-bottom:20px;flex-wrap:wrap}
  .ans .box{flex:1;min-width:240px;background:var(--card);border:1px solid var(--line);
            border-radius:12px;padding:14px 16px}
  .box .lbl{font-size:12px;color:var(--muted);margin-bottom:6px;font-weight:700;letter-spacing:.5px}
  .box.gold .val{color:var(--gold);font-size:20px;font-weight:700}
  .box.rag .val{font-size:19px;line-height:1.5}
  .sec-title{font-size:13px;color:var(--muted);font-weight:700;margin:0 0 10px;
             text-transform:uppercase;letter-spacing:1px}
  .seif{background:var(--card);border:1px solid var(--line);border-radius:12px;
        padding:14px 16px;margin-bottom:12px}
  .seif.gold{border-color:var(--gold);box-shadow:0 0 0 1px var(--gold) inset}
  .seif .ref{display:inline-block;font-weight:800;color:var(--accent);margin-bottom:8px}
  .seif.gold .ref{color:var(--gold)}
  .seif .tag{font-size:11px;color:#0f1220;background:var(--gold);padding:2px 8px;
             border-radius:10px;margin-inline-start:8px;font-weight:800}
  .seif .txt{font-size:16px;line-height:1.7;color:#dfe4f3}
  footer{padding:12px 18px;border-top:1px solid var(--line);display:flex;
         align-items:center;justify-content:space-between;background:#141830}
  button{background:var(--accent);color:#0f1220;border:0;padding:9px 18px;border-radius:8px;
         font-size:15px;font-weight:700;cursor:pointer}
  button:disabled{opacity:.35;cursor:default}
  .hint{font-size:12px;color:var(--muted)}
</style>
</head>
<body>
<header>
  <h1>הערכת RAG — קיצור שולחן ערוך</h1>
  <span class="counter" id="counter"></span>
  <span id="badges"></span>
</header>
<main><div class="slide" id="slide"></div></main>
<footer>
  <button id="prev">‹ הקודם</button>
  <span class="hint">חצים ← → לניווט · מקש מספר לקפיצה</span>
  <button id="next">הבא ›</button>
</footer>
<script>
const DATA = __DATA__;
let i = 0;
function esc(s){return (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
function render(){
  const s = DATA[i];
  document.getElementById("counter").textContent = `שאלה ${i+1} / ${DATA.length}  ·  מקור אמת: ${s.gold_ref}`;
  document.getElementById("badges").innerHTML =
    `<span class="pill ${s.ctx_hit?'ok':'bad'}">${s.ctx_hit?'הסעיף נשלף ✓':'הסעיף לא נשלף ✗'}</span> `+
    `<span class="pill ${s.contains?'ok':'bad'}">${s.contains?'התשובה תואמת':'לא תואם (מחרוזת)'}</span>`;
  let seifs = s.retrieved.map((r,idx)=>
    `<div class="seif ${r.is_gold?'gold':''}">
       <span class="ref">#${idx+1} · סימן ${r.ref.split(':')[0]} סעיף ${r.ref.split(':')[1]}</span>
       ${r.is_gold?'<span class="tag">הסעיף הנכון</span>':''}
       <div class="txt">${esc(r.text)}</div>
     </div>`).join("");
  document.getElementById("slide").innerHTML =
    `<div class="q">${esc(s.q)}</div>
     <div class="ans">
       <div class="box rag"><div class="lbl">תשובת המודל (DictaLM)</div><div class="val">${esc(s.rag)}</div></div>
       <div class="box gold"><div class="lbl">תשובת האמת</div><div class="val">${esc(s.gold)}</div></div>
     </div>
     <div class="sec-title">הסעיפים שנשלפו (טקסט מלא)</div>
     ${seifs}`;
  document.getElementById("prev").disabled = i===0;
  document.getElementById("next").disabled = i===DATA.length-1;
  document.querySelector("main").scrollTop = 0;
}
function go(d){ i=Math.min(Math.max(0,i+d),DATA.length-1); render(); }
document.getElementById("prev").onclick=()=>go(-1);
document.getElementById("next").onclick=()=>go(1);
let buf="";
document.addEventListener("keydown",e=>{
  if(e.key==="ArrowRight"||e.key==="ArrowDown")go(-0+1);   // RTL: → moves... keep simple
  else if(e.key==="ArrowLeft"||e.key==="ArrowUp")go(-1);
  else if(/[0-9]/.test(e.key)){buf+=e.key;clearTimeout(window._t);
    window._t=setTimeout(()=>{let n=parseInt(buf)-1;if(n>=0&&n<DATA.length){i=n;render();}buf="";},600);}
});
render();
</script>
</body>
</html>"""

html = html.replace("__DATA__", data_json)
open("presentation_100.html", "w", encoding="utf-8").write(html)
print(f"נשמר: presentation_100.html  ({len(slides)} שקפים)")
