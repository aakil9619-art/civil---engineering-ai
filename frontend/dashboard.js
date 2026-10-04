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
  if(window.CivilAuth && CivilAuth.user){authFetch("/api/workspace/mock-history",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({student_id:"ignored",exam:"SSC JE 2026 Paper-I",score,accuracy,attempted:completed.length,total:qs.length})}).catch(()=>{});}
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

/* Student OS dashboard — authenticated home workspace */
function renderStudentDashboard(){
  const root=document.querySelector("#content");
  if(!root)return;
  if(!CivilAuth.user){
    root.innerHTML='<div class="workspace-empty"><div class="workspace-icon">🔐</div><h3>Your engineering workspace</h3><p>Login with OTP to save mock history, projects, research, bookmarks and learning progress.</p><button class="primary" id="workspaceLogin">📱 Login with OTP</button></div>';
    document.querySelector("#workspaceLogin").onclick=()=>CivilAuth.open();
    return;
  }
  root.innerHTML='<div class="student-os"><div class="os-hero"><div><span class="os-eyebrow">PERSONAL ENGINEERING WORKSPACE</span><h3 id="osGreeting">Good to see you back.</h3><p id="osSub">Your study, project and research activity in one place.</p></div><button id="osRefresh" class="os-refresh">↻ Refresh</button></div><div class="os-kpis"><article><span>Latest Mock</span><b id="kpiScore">—</b><small id="kpiScoreMeta">No attempt yet</small></article><article><span>Accuracy</span><b id="kpiAccuracy">—</b><small id="kpiAccuracyMeta">Build your history</small></article><article><span>Questions Attempted</span><b id="kpiQuestions">0</b><small>Across saved mocks</small></article><article><span>Weak Areas</span><b id="kpiWeak">—</b><small>Based on recent accuracy</small></article></div><div class="os-grid"><section class="os-main"><article class="os-card next-action"><div class="os-card-head"><div><span class="os-label">NEXT BEST ACTION</span><h4 id="nextTitle">Start your first mock</h4></div><span class="action-dot">●</span></div><p id="nextText">Take a timed SSC JE Paper-I mock to establish your baseline and unlock personalized recommendations.</p><div class="os-actions"><button id="nextAction" class="primary">🎯 Open Exam Center</button><button id="aiAction">🤖 Ask AI Tutor</button></div></article><article class="os-card"><div class="os-card-head"><div><span class="os-label">TODAY'S PLAN</span><h4>Four focused blocks</h4></div><span class="plan-score" id="planProgress">0/4</span></div><div class="study-plan" id="studyPlan"></div></article><article class="os-card"><div class="os-card-head"><div><span class="os-label">MOCK HISTORY</span><h4>Recent performance</h4></div><button id="openMock">View mock center</button></div><div id="osMocks" class="os-list"></div></article></section><aside class="os-side"><article class="os-card"><div class="os-card-head"><div><span class="os-label">WEAK SUBJECTS</span><h4>Where to improve</h4></div></div><div id="weakSubjects"></div></article><article class="os-card"><div class="os-card-head"><div><span class="os-label">YOUR WORK</span><h4>Projects & research</h4></div></div><div class="mini-stats"><div><b id="projectCount">0</b><span>Projects</span></div><div><b id="researchCount">0</b><span>Research</span></div><div><b id="bookmarkCount">0</b><span>Bookmarks</span></div></div><div class="quick-save"><input id="quickProject" placeholder="Save a project idea"><button id="saveProject">＋</button><input id="quickResearch" placeholder="Save a research topic"><button id="saveResearch">＋</button></div></article><article class="os-card"><div class="os-card-head"><div><span class="os-label">SAVED ITEMS</span><h4>Latest workspace activity</h4></div></div><div id="osSaved" class="os-list"></div></article></aside></div></div>';
  const esc=v=>String(v??"").replace(/[&<>"']/g,function(ch){return ch==="&"?"&amp;":ch==="<"?"&lt;":ch===">"?"&gt;":ch==='"'?"&quot;":"&#39;";});
  const runMode=mode=>{const card=document.querySelector('.card[data-mode="'+mode+'"]');if(card)card.click();};
  document.querySelector("#nextAction").onclick=()=>runMode("mock");
  document.querySelector("#openMock").onclick=()=>runMode("mock");
  document.querySelector("#aiAction").onclick=()=>runMode("tutor");
  document.querySelector("#osRefresh").onclick=loadWorkspace;
  const plan=[["Technical revision","Revise one weak Civil subject + 20 focused questions."],["Reasoning sprint","25 timed reasoning questions. Prioritize accuracy."],["GK / current affairs","30 minutes of static + current affairs revision."],["Mini mock","Attempt a timed mixed set and review every mistake."]];
  const state=plan.map(()=>false);
  function paintPlan(){const done=state.filter(Boolean).length;document.querySelector("#planProgress").textContent=done+"/4";document.querySelector("#studyPlan").innerHTML=plan.map((p,i)=>'<label class="plan-item '+(state[i]?"done":"")+'"><input type="checkbox" data-plan="'+i+'" '+(state[i]?"checked":"")+'><span><b>'+esc(p[0])+'</b><small>'+esc(p[1])+'</small></span></label>').join("");document.querySelectorAll("[data-plan]").forEach(x=>x.onchange=()=>{state[Number(x.dataset.plan)]=x.checked;paintPlan();});}
  paintPlan();
  async function loadWorkspace(){
    try{
      const r=await authFetch("/api/workspace");if(!r.ok)throw new Error("workspace "+r.status);
      const x=await r.json(),mocks=x.mock_history||[],projects=x.projects||[],research=x.research||[],bookmarks=x.bookmarks||[];
      const name=x.student?.name||CivilAuth.user.displayName||"Student";
      document.querySelector("#osGreeting").textContent="Good to see you, "+name+".";
      document.querySelector("#osSub").textContent="Your Civil Engineering workspace is ready. Keep the next block focused.";
      document.querySelector("#kpiQuestions").textContent=mocks.reduce((n,m)=>n+Number(m.attempted||0),0).toLocaleString("en-IN");
      document.querySelector("#projectCount").textContent=projects.length;document.querySelector("#researchCount").textContent=research.length;document.querySelector("#bookmarkCount").textContent=bookmarks.length;
      if(mocks.length){
        const latest=mocks[0];document.querySelector("#kpiScore").textContent=Number(latest.score).toFixed(2);document.querySelector("#kpiScoreMeta").textContent=latest.exam+" • "+new Date(latest.created_at).toLocaleDateString("en-IN");
        document.querySelector("#kpiAccuracy").textContent=Number(latest.accuracy).toFixed(1)+"%";document.querySelector("#kpiAccuracyMeta").textContent=Number(latest.attempted||0)+"/"+Number(latest.total||0)+" attempted";
        document.querySelector("#kpiWeak").textContent=Number(latest.accuracy)<70?"Accuracy needs work":"Keep building consistency";
        document.querySelector("#nextTitle").textContent=Number(latest.accuracy)<70?"Review mistakes before the next mock":"Push your score higher";
        document.querySelector("#nextText").textContent=Number(latest.accuracy)<70?"Your latest accuracy is below 70%. Review wrong questions, then retake a focused mini mock.":"Your latest attempt is solid. Target the weakest section and take another timed set.";
        document.querySelector("#osMocks").innerHTML=mocks.slice(0,5).map(m=>'<div class="os-row"><div><b>'+esc(m.exam)+'</b><small>'+new Date(m.created_at).toLocaleDateString("en-IN")+' • '+Number(m.attempted||0)+'/'+Number(m.total||0)+' attempted</small></div><strong>'+Number(m.score).toFixed(2)+' <em>'+Number(m.accuracy).toFixed(1)+'%</em></strong></div>').join("");
      }else{document.querySelector("#kpiWeak").textContent="Start testing";document.querySelector("#osMocks").innerHTML='<div class="workspace-empty compact"><p>No mock history yet. Your first timed attempt will unlock exam intelligence.</p></div>';}
      const progress=(x.progress||[]).filter(p=>Number.isFinite(Number(p.value))).sort((a,b)=>Number(a.value)-Number(b.value)).slice(0,5);
      document.querySelector("#weakSubjects").innerHTML=progress.length?progress.map(p=>'<div class="weak-row"><div><b>'+esc(p.key)+'</b><span>'+Number(p.value).toFixed(0)+'%</span></div><div class="weak-bar"><i style="width:'+Math.max(0,Math.min(100,Number(p.value)))+'%"></i></div></div>').join(""):'<p class="muted">Subject progress will appear as you study.</p>';
      const saved=[...projects.slice(0,2).map(p=>({label:"🎓 "+p.title,meta:p.status})),...research.slice(0,2).map(p=>({label:"🔬 "+p.topic,meta:p.status})),...bookmarks.slice(0,2).map(p=>({label:"🔖 "+p.title,meta:p.kind}))];
      document.querySelector("#osSaved").innerHTML=saved.length?saved.slice(0,6).map(v=>'<div class="os-row"><div><b>'+esc(v.label)+'</b><small>'+esc(v.meta||"Saved")+'</small></div></div>').join(""):'<p class="muted">Nothing saved yet. Start with a project, research topic or bookmark.</p>';
    }catch(e){document.querySelector("#osSub").textContent="Could not load your workspace. Please refresh after signing in again.";document.querySelector("#nextText").textContent="Your secure workspace connection is unavailable right now.";}
  }
  document.querySelector("#saveProject").onclick=async()=>{const v=document.querySelector("#quickProject").value.trim();if(!v)return;await authFetch("/api/workspace/projects",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({student_id:"ignored",title:v})});document.querySelector("#quickProject").value="";loadWorkspace();};
  document.querySelector("#saveResearch").onclick=async()=>{const v=document.querySelector("#quickResearch").value.trim();if(!v)return;await authFetch("/api/workspace/research",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({student_id:"ignored",topic:v})});document.querySelector("#quickResearch").value="";loadWorkspace();};
  loadWorkspace();
}
window.addEventListener("civil-auth-ready",()=>{if(location.hash==="#workspace"&&CivilAuth.user)renderStudentDashboard();});
