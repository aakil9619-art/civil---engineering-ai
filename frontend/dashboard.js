const API="/api";
async function getJSON(path,opts){const r=await fetch(API+path,opts);if(!r.ok)throw new Error("API "+r.status);return r.json();}
async function loadSubjects(){const x=await getJSON("/topics");return Object.keys(x.subjects||{});}
function renderDashboard(){
 const root=document.querySelector("#content");
 root.innerHTML=`<div class="dashboard">
 <div class="mock-head"><div><h3>SSC JE 2026 Mock Test</h3><p>Timed practice with question navigation, review marks and final analysis.</p></div><div class="mock-badge">⏱️ Timed</div></div>
 <div class="dash-grid">
 <label>Subject<select id="dsubject"></select></label>
 <label>Topic<select id="dtopic"></select></label>
 <label>Difficulty<select id="ddiff"><option>easy</option><option selected>moderate</option><option>hard</option><option>very_hard</option></select></label>
 <label>Questions<input id="dcount" type="number" min="1" max="50" value="10"></label>
 </div><button id="startTest" class="primary">Start Mock</button><div id="testArea"></div></div>`;
 loadSubjects().then(ss=>{dsubject.innerHTML=ss.map(s=>`<option>${s}</option>`).join("");return updateTopics()});
 dsubject.onchange=updateTopics; document.querySelector("#startTest").onclick=startTest;
}
async function updateTopics(){const s=dsubject.value;if(!s)return;const x=await getJSON("/topics?subject="+encodeURIComponent(s));dtopic.innerHTML='<option value="">All topics</option>'+x.topics.map(t=>`<option>${t}</option>`).join("")}
async function startTest(){
 const count=Math.max(1,Math.min(50,Number(dcount.value)||10));
 const body={exam:"SSC JE 2026",subject:dsubject.value,topic:dtopic.value,difficulty:ddiff.value,question_type:"numerical",count};
 const data=await getJSON("/questions/generate",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
 const qs=data.questions||[]; if(!qs.length){document.querySelector("#testArea").innerHTML="<p>No questions available.</p>";return;}
 let index=0,answers=qs.map(()=>null),marked=qs.map(()=>false),questionStart=performance.now(),finished=false;
 const area=document.querySelector("#testArea");
 function elapsed(){return Math.max(0,Math.round((performance.now()-questionStart)/1000));}
 function formatTime(s){const m=Math.floor(s/60),sec=s%60;return String(m).padStart(2,"0")+":"+String(sec).padStart(2,"0");}
 function choose(i){const q=qs[index];answers[index]={topic:q.topic||"Unknown",is_correct:String(q.options[i])===String(q.answer),time_seconds:elapsed(),selected_option:String(q.options[i]),marked_for_review:marked[index]};renderQuestion();}
 function renderPalette(){return qs.map((q,i)=>`<button class="palette-btn ${i===index?"current":""} ${answers[i]?"answered":""} ${marked[i]?"review":""}" data-q="${i}">${i+1}</button>`).join("");}
 function renderQuestion(){
  const q=qs[index];
  area.innerHTML=`<div class="test-top"><div><b>Question ${index+1} / ${qs.length}</b><span class="timer" id="timer">--:--</span></div><div class="progress">${Math.round(((index+1)/qs.length)*100)}%</div></div>
  <div class="mock-layout"><article class="question test-question"><div class="question-label">${q.question_type||"Numerical"} • ${q.difficulty||""}</div><h3>${q.question}</h3><div class="opts">${q.options.map((o,i)=>`<button class="option ${answers[index]&&answers[index].selected_option===String(o)?"selected":""}" data-i="${i}">${String.fromCharCode(65+i)}. ${o}</button>`).join("")}</div>
  <div class="question-actions"><button id="prevQ" ${index===0?"disabled":""}>← Previous</button><button id="reviewQ" class="review-action">${marked[index]?"★ Remove Review":"☆ Mark for Review"}</button><button id="nextQ" ${index===qs.length-1?"disabled":""}>Next →</button></div></article>
  <aside class="palette"><h4>Question Palette</h4><div class="palette-grid">${renderPalette()}</div><div class="legend"><span>● Answered</span><span>★ Review</span></div><button id="submitMock" class="submit-btn">Submit Test</button></aside></div>`;
  area.querySelectorAll(".option").forEach(b=>b.onclick=()=>choose(Number(b.dataset.i)));
  area.querySelector("#prevQ").onclick=()=>{if(index>0){index--;questionStart=performance.now();renderQuestion();}};
  area.querySelector("#nextQ").onclick=()=>{if(index<qs.length-1){index++;questionStart=performance.now();renderQuestion();}};
  area.querySelector("#reviewQ").onclick=()=>{marked[index]=!marked[index];renderQuestion();};
  area.querySelectorAll(".palette-btn").forEach(b=>b.onclick=()=>{index=Number(b.dataset.q);questionStart=performance.now();renderQuestion();});
  area.querySelector("#submitMock").onclick=finish; questionStart=performance.now();
 }
 async function finish(){
  if(finished)return;finished=true;
  const completed=answers.filter(Boolean);
  const p=await getJSON("/performance",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({total:qs.length,answers:completed})});
  area.innerHTML=`<div class="result"><h3>Mock Test Complete 🎯</h3><div class="result-grid"><div><span>Score</span><b>${p.summary.score}/${p.summary.total}</b></div><div><span>Accuracy</span><b>${p.summary.accuracy.toFixed(1)}%</b></div><div><span>Attempted</span><b>${p.summary.attempted}/${p.summary.total}</b></div><div><span>Avg. time</span><b>${p.summary.avg_time_seconds.toFixed(1)}s</b></div></div><h4>Topic analysis</h4>${p.profile.map(x=>`<p><b>${x.topic}</b>: ${x.accuracy}% — ${x.status}</p>`).join("")}<button onclick="renderDashboard()" class="primary">New Mock</button></div>`;
 }
 renderQuestion();
 let remaining=Math.max(60,qs.length*90);
 const countdown=setInterval(()=>{if(finished){clearInterval(countdown);return}const el=document.querySelector("#timer");if(!el){clearInterval(countdown);return}el.textContent=formatTime(remaining);if(remaining<=0){clearInterval(countdown);finish();return}remaining--;},1000);
}
window.renderDashboard=renderDashboard;