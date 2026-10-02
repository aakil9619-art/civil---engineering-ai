const API="/api";
async function getJSON(path,opts){const r=await fetch(API+path,opts);if(!r.ok)throw new Error("API "+r.status);return r.json();}
async function loadSubjects(){const x=await getJSON("/topics");return Object.keys(x.subjects||{});}
function renderDashboard(){
 const root=document.querySelector("#content");
 root.innerHTML=`<div class="dashboard">
 <h3>SSC JE 2026 Practice</h3>
 <div class="dash-grid">
 <label>Subject<select id="dsubject"></select></label>
 <label>Topic<select id="dtopic"></select></label>
 <label>Difficulty<select id="ddiff"><option>easy</option><option selected>moderate</option><option>hard</option><option>very_hard</option></select></label>
 <label>Questions<input id="dcount" type="number" min="1" max="50" value="10"></label>
 </div><button id="startTest">Start Test</button><div id="testArea"></div></div>`;
 loadSubjects().then(ss=>{dsubject.innerHTML=ss.map(s=>`<option>${s}</option>`).join("");return updateTopics()});
 dsubject.onchange=updateTopics; document.querySelector("#startTest").onclick=startTest;
}
async function updateTopics(){const s=dsubject.value;if(!s)return;const x=await getJSON("/topics?subject="+encodeURIComponent(s));dtopic.innerHTML='<option value="">All topics</option>'+x.topics.map(t=>`<option>${t}</option>`).join("")}
async function startTest(){
 const body={exam:"SSC JE 2026",subject:dsubject.value,topic:dtopic.value,difficulty:ddiff.value,question_type:"numerical",count:Number(dcount.value)};
 const data=await getJSON("/questions/generate",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
 const qs=data.questions||[]; let index=0, answers=[];
 const area=document.querySelector("#testArea");
 function show(){if(index>=qs.length){finish();return}const q=qs[index];area.innerHTML=`<div class="test-meta">Question ${index+1} / ${qs.length}</div><article class="question"><h3>${q.question}</h3><div class="opts">${q.options.map((o,i)=>`<button data-i="${i}">${String.fromCharCode(65+i)}. ${o}</button>`).join("")}</div></article>`;area.querySelectorAll(".opts button").forEach((b,i)=>b.onclick=()=>{answers.push({topic:q.topic,is_correct:b.textContent.includes(q.answer),time_seconds:0});index++;show()})}
 async function finish(){const p=await getJSON("/performance",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({total:qs.length,answers})});area.innerHTML=`<div class="result"><h3>Test Complete</h3><p>Score: <b>${p.summary.score}/${p.summary.total}</b></p><p>Accuracy: <b>${p.summary.accuracy.toFixed(1)}%</b></p><h4>Topic analysis</h4>${p.profile.map(x=>`<p>${x.topic}: ${x.accuracy}% — ${x.status}</p>`).join("")}<button onclick="renderDashboard()">New Test</button></div>`}
 show();
}
window.renderDashboard=renderDashboard;
