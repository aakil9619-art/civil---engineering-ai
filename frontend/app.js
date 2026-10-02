const titles={tutor:'AI Civil Tutor',questions:'Question Generator',mock:'Mock Test',diagram:'Diagram Learning'};
const descriptions={tutor:'Ask a Civil Engineering concept question.',questions:'Generate original Civil Engineering questions.',mock:'Practice timed questions and analyze accuracy and speed.',diagram:'Learn Civil Engineering visually.'};
const contentBox=document.querySelector('#content');
document.querySelectorAll('.card').forEach(card=>card.addEventListener('click',()=>{
 const mode=card.dataset.mode; document.querySelector('#panel-title').textContent=titles[mode];
 if(mode==='questions') renderQuestionGenerator(); else if(mode==='mock') renderDashboard(); else if(mode==='tutor') renderTutorChat();
 else contentBox.innerHTML='<p>'+descriptions[mode]+'</p><p><b>Built for:</b> SSC JE 2026 • GATE CE • AE/JE</p>';
}));
function renderQuestionGenerator(){
 contentBox.innerHTML=`<div class="form">
<label>Exam<select id="exam"><option>SSC JE 2026</option><option>GATE CE</option></select></label>
<label>Subject<select id="subject"></select></label>
<label>Topic<input id="topic" placeholder="e.g. Bernoulli equation"></label>
<label>Difficulty<select id="difficulty"><option>easy</option><option selected>moderate</option><option>hard</option><option>very_hard</option></select></label>
<label>Type<select id="qtype"><option>numerical</option><option>conceptual</option><option>statement</option><option>assertion_reason</option><option>match</option></select></label>
<label>Count<input id="count" type="number" min="1" max="50" value="5"></label>
<button id="generate">Generate Questions</button></div><div id="results"></div>`;
 const subjects=["Engineering Mechanics","Strength of Material","Structural Analysis","Construction Management and Management","Estimation Costing and Valuation","RCC","Steel","Survey","Soil","Fluid Mechanics","Hydraulics","Hydrology","Irrigation","Environmental Engineering","Transportation Engineering"];
 document.querySelector('#subject').innerHTML=subjects.map(s=>'<option>'+s+'</option>').join('');
 document.querySelector('#generate').onclick=generate;
}
async function generate(){
 const body={exam:document.querySelector('#exam').value,subject:document.querySelector('#subject').value,topic:document.querySelector('#topic').value,difficulty:document.querySelector('#difficulty').value,question_type:document.querySelector('#qtype').value,count:Number(document.querySelector('#count').value)};
 const r=await fetch('/api/questions/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
 const data=await r.json(), qs=data.questions||[];
 document.querySelector('#results').innerHTML=qs.map((q,i)=>`<article class="question"><h3>Q${i+1}. ${q.question}</h3><ol type="A">${q.options.map(o=>'<li>'+o+'</li>').join('')}</ol><details><summary>Show solution</summary><p><b>Answer:</b> ${q.answer}</p><p>${q.solution}</p><p><b>Formula:</b> ${q.formula}</p><p><b>Concept:</b> ${q.concept}</p><p><b>Trap:</b> ${q.common_trap}</p><p><b>Tip:</b> ${q.exam_tip}</p></details></article>`).join('');
}
fetch('/api/ai/status').then(r=>r.json()).then(x=>{document.querySelector('#status').textContent='Backend connected • AI provider: '+x.provider+' • configured: '+x.provider_configured}).catch(()=>document.querySelector('#status').textContent='Start the FastAPI backend to connect the dashboard.');
function renderTutorChat(){
 contentBox.innerHTML=`<div class="chat-box">
 <div class="chat-intro"><h3>🤖 Civil AI Chat</h3><p>Ask doubts about concepts, formulas, numericals or how to approach an exam question. Answers are kept brief and exam-focused.</p></div>
 <div class="chat-form">
 <select id="chatSubject">${["Engineering Mechanics","Strength of Material","Structural Analysis","Construction Management and Management","Estimation Costing and Valuation","RCC","Steel","Survey","Soil","Fluid Mechanics","Hydraulics","Hydrology","Irrigation","Environmental Engineering","Transportation Engineering"].map(s=>`<option>${s}</option>`).join("")}</select>
 <input id="chatTopic" placeholder="Topic e.g. Effective stress">
 <textarea id="chatQuestion" placeholder="Write your question..."></textarea>
 <label class="image-upload">📷 Upload question image<input id="chatImage" type="file" accept="image/*"></label>
 <button id="chatSend">Ask AI</button></div><div id="chatReply"></div></div>`;
 document.querySelector("#chatSend").onclick=askAI;
}
async function askAI(){
 const reply=document.querySelector("#chatReply"); reply.innerHTML="<div class='chat-loading'>Thinking…</div>";
 const subject=document.querySelector("#chatSubject").value;
 const topic=document.querySelector("#chatTopic").value;
 const question=document.querySelector("#chatQuestion").value;
 const image=document.querySelector("#chatImage").files[0];
 try{
  let r;
  if(image){
   const form=new FormData();
   form.append("subject",subject); form.append("topic",topic); form.append("question",question); form.append("image",image);
   r=await fetch("/api/chat/image",{method:"POST",body:form});
  }else{
   r=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({subject,topic,question})});
  }
  const x=await r.json();
  const box=document.createElement("div"); box.className="chat-answer";
  const title=document.createElement("b"); title.textContent=x.answer ? "🤖 AI Tutor" : "⚠️ AI Tutor";
  const pre=document.createElement("pre"); pre.textContent=x.answer||x.error||"No response received.";
  box.appendChild(title); box.appendChild(pre); reply.replaceChildren(box);
 }catch(e){reply.innerHTML="<p>Start the backend and try again.</p>";}
}
