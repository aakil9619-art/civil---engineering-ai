const API="/api";
async function getJSON(path,opts){const r=await fetch(API+path,opts);if(!r.ok)throw new Error("API "+r.status);return r.json();}

function renderDashboard(){
 const root=document.querySelector("#content");
 root.innerHTML=`<div class="dashboard">
 <div class="mock-head"><div><h3>SSC JE 2026 • Full Paper-I Simulator</h3><p>200 questions • 120 minutes • Technical + Reasoning + General Awareness • −0.25 for each wrong answer.</p></div><div class="mock-badge">🎯 Exam Mode</div></div>
 <div class="dash-grid">
  <label>Technical Questions<input id="mtech" type="number" min="1" max="100" value="100"></label>
  <label>Reasoning Questions<input id="mreason" type="number" min="1" max="50" value="50"></label>
  <label>GK Questions<input id="mgk" type="number" min="1" max="50" value="50"></label>
 </div>
 <p class="mock-note">The default setup mirrors the SSC JE 2026 Paper-I structure. You can use smaller counts for practice.</p>
 <button id="startMixed" class="primary">Start SSC JE Mock</button><div id="testArea"></div></div>`;
 document.querySelector("#startMixed").onclick=startMixed;
}

async function startMixed(){
 const tech=Math.max(1,Math.min(100,Number(mtech.value)||100));
 const reason=Math.max(1,Math.min(50,Number(mreason.value)||50));
 const gk=Math.max(1,Math.min(50,Number(mgk.value)||50));
 const area=document.querySelector("#testArea");
 area.innerHTML="<p>Building your mock…</p>";
 const data=await getJSON(`/mock/questions?technical=${tech}&reasoning=${reason}&gk=${gk}`);
 const qs=data.questions||[];
 if(!qs.length){area.innerHTML="<p>No questions available.</p>";return;}
 let index=0,answers=qs.map(()=>null),marked=qs.map(()=>false),finished=false;
 const startedAt=Date.now(), duration=120*60;
 const questionOpened=Array(qs.length).fill(Date.now());

 function remaining(){return Math.max(0,duration-Math.floor((Date.now()-startedAt)/1000));}
 function fmt(s){const h=Math.floor(s/3600),m=Math.floor((s%3600)/60),x=s%60;return (h?String(h).padStart(2,"0")+":":"")+String(m).padStart(2,"0")+":"+String(x).padStart(2,"0");}
 function sectionName(s){return s==="technical"?"Technical":s==="reasoning"?"Reasoning":"General Awareness";}
 function counts(){
  const out={technical:{a:0,r:0},reasoning:{a:0,r:0},gk:{a:0,r:0}};
  qs.forEach((q,i)=>{if(answers[i])out[q.section].a++;if(marked[i])out[q.section].r++;});
  return out;
 }
 function choose(i){
  const q=qs[index];
  answers[index]={topic:q.topic||"Unknown",section:q.section,is_correct:String(q.options[i])===String(q.answer),time_seconds:Math.max(1,Math.round((Date.now()-questionOpened[index])/1000)),selected_option:String(q.options[i]),marked_for_review:marked[index]};
  render();
 }
 function palette(){
  return qs.map((q,i)=>`<button class="palette-btn ${i===index?"current ":""}${answers[i]?"answered ":""}${marked[i]?"review ":""}" data-q="${i}" title="${sectionName(q.section)}">${i+1}</button>`).join("");
 }
 function render(){
  const q=qs[index], c=counts(), left=remaining();
  area.innerHTML=`<div class="test-top"><div><b>Question ${index+1} / ${qs.length}</b><span class="timer" id="timer">${fmt(left)}</span></div><div class="progress">${Math.round((index+1)/qs.length*100)}%</div></div>
  <div class="section-tabs">
   <button data-sec="technical">Technical <b>${c.technical.a}/${tech}</b></button>
   <button data-sec="reasoning">Reasoning <b>${c.reasoning.a}/${reason}</b></button>
   <button data-sec="gk">GK <b>${c.gk.a}/${gk}</b></button>
  </div>
  <div class="mock-layout"><article class="question test-question">
   <div class="question-label">${sectionName(q.section)} • ${q.subject||""} • ${q.topic||""}</div>
   <h3>${q.question}</h3>
   <div class="opts">${q.options.map((o,i)=>`<button class="option ${answers[index]&&answers[index].selected_option===String(o)?"selected":""}" data-i="${i}">${String.fromCharCode(65+i)}. ${o}</button>`).join("")}</div>
   <div class="question-actions"><button id="prevQ" ${index===0?"disabled":""}>← Previous</button><button id="reviewQ" class="review-action">${marked[index]?"★ Remove Review":"☆ Mark for Review"}</button><button id="nextQ" ${index===qs.length-1?"disabled":""}>Next →</button></div>
  </article>
  <aside class="palette"><h4>Question Palette</h4><div class="palette-grid">${palette()}</div><div class="legend"><span>● Answered</span><span>★ Review</span></div><button id="submitMock" class="submit-btn">Submit Test</button></aside></div>`;
  area.querySelectorAll(".option").forEach(b=>b.onclick=()=>choose(Number(b.dataset.i)));
  area.querySelector("#prevQ").onclick=()=>{if(index>0){index--;questionOpened[index]=Date.now();render();}};
  area.querySelector("#nextQ").onclick=()=>{if(index<qs.length-1){index++;questionOpened[index]=Date.now();render();}};
  area.querySelector("#reviewQ").onclick=()=>{marked[index]=!marked[index];render();};
  area.querySelectorAll(".palette-btn").forEach(b=>b.onclick=()=>{index=Number(b.dataset.q);questionOpened[index]=Date.now();render();});
  area.querySelectorAll(".section-tabs button").forEach(b=>b.onclick=()=>{const sec=b.dataset.sec;const i=qs.findIndex(q=>q.section===sec);if(i>=0){index=i;questionOpened[index]=Date.now();render();}});
  area.querySelector("#submitMock").onclick=()=>finish(false);
 }
 async function finish(auto){
  if(finished)return;finished=true;
  const completed=answers.filter(Boolean);
  const correct=completed.filter(a=>a.is_correct).length;
  const wrong=completed.filter(a=>!a.is_correct).length;
  const score=correct-(wrong*0.25);
  const accuracy=completed.length?correct/completed.length*100:0;
  const by={technical:{a:0,c:0},reasoning:{a:0,c:0},gk:{a:0,c:0}};
  completed.forEach(a=>{by[a.section].a++;if(a.is_correct)by[a.section].c++;});
  const weak=Object.entries(by).map(([k,v])=>({k,acc:v.a?v.c/v.a*100:0})).sort((a,b)=>a.acc-b.acc);
  area.innerHTML=`<div class="result"><h3>${auto?"⏰ Time Up — ":""}SSC JE Paper-I Complete 🎯</h3>
   <div class="result-grid"><div><span>Score</span><b>${score.toFixed(2)}/${qs.length}</b></div><div><span>Correct</span><b>${correct}</b></div><div><span>Wrong</span><b>${wrong}</b></div><div><span>Attempted</span><b>${completed.length}/${qs.length}</b></div><div><span>Accuracy</span><b>${accuracy.toFixed(1)}%</b></div><div><span>Negative marks</span><b>-${(wrong*.25).toFixed(2)}</b></div></div>
   <h4>Section analysis</h4>${Object.entries(by).map(([k,v])=>`<p><b>${sectionName(k)}</b>: ${v.c}/${v.a} correct — ${v.a?(v.c/v.a*100).toFixed(1):"0.0"}%</p>`).join("")}
   <div class="mock-note"><b>Practice recommendation:</b> ${sectionName(weak[0].k)} needs the most review based on this attempt. Revisit its wrong questions before the next mock.</div>
   <button onclick="renderDashboard()" class="primary">New Mock</button></div>`;
 }
 render();
 const timer=setInterval(()=>{const el=document.querySelector("#timer");if(!el){clearInterval(timer);return}const left=remaining();el.textContent=fmt(left);if(left<=0){clearInterval(timer);finish(true);}},1000);
}
window.renderDashboard=renderDashboard;