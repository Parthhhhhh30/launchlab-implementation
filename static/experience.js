(() => {
'use strict';
const $=(s)=>document.querySelector(s);
const $$=(s)=>Array.from(document.querySelectorAll(s));
const safe=(x)=>String(x??'');
let workspace=null, busy=false;
const observable='Explains implementation blockers to customers using documented steps, named owners, and a clear agreed next action.';
const initReveals=()=>{
  if(!('IntersectionObserver' in window)){ $$('.reveal').forEach(x=>x.classList.add('visible'));return; }
  const ob=new IntersectionObserver((entries)=>{entries.forEach(x=>{if(x.isIntersecting){x.target.classList.add('visible');ob.unobserve(x.target)}})},{threshold:.10});
  $$('.reveal').forEach(x=>ob.observe(x));
};
async function request(path,config={}){
  const res=await fetch(path,{credentials:'same-origin',cache:'no-store',...config});
  let answer;try{answer=await res.json()}catch{throw new Error('The service returned an invalid response. Try again.')}
  if(!res.ok)throw new Error(answer.detail||answer.error||`Request failed (${res.status})`);
  return answer;
}
function render(){
 if(!workspace)return;
 const s=workspace.state;
 $('#live-revision').textContent=`WORKSPACE REVISION ${s.revision}`;
 $('#lab-storage').textContent=`DATABASE CONNECTED · REV ${s.revision}`;
 const c=s.criteria.find(v=>v.id==='CR-02');
 $('#criteria-copy').textContent=c.description;
 const cgood=!!c.reviewed && !/excellent communicator|culture fit|strong communication/i.test(c.description);
 $('#criteria-status').textContent=cgood?'REVIEWED':c.description===observable?'AWAITING HUMAN REVIEW':'NEEDS CLARIFICATION';
 $('#criteria-status').style.color=cgood?'#327e52':'#ad574a';
 $('#clarify-action').disabled=(c.description===observable);
 const map=s.ats_mapping.job_id;
 $('#mapping-path').textContent=map;
 $('#mapping-connector').classList.toggle('is-broken',map!=='job.id'||s.mapping_result?.passed===false);
 if(s.mapping_result){
   const result=s.mapping_result;
   $('#mapping-feedback').dataset.result=result.passed?'success':'error';
   $('#mapping-feedback').textContent=result.passed?`PASS · ${Object.keys(result.output||{}).length} synthetic fields resolved; no production ATS was contacted.`:`FAIL · ${result.issues.join('; ')}`;
 }
 const node=$('#audience-rows');node.replaceChildren();
 workspace.adoption.teams.forEach(team=>{
   const count=team.w2===null?team.w1:team.w2;
   const row=document.createElement('div');row.className='audience-row';
   const name=document.createElement('span');name.textContent=team.name;
   const meter=document.createElement('div');meter.className='audience-meter';meter.setAttribute('role','progressbar');meter.setAttribute('aria-label',team.name+' active users');meter.setAttribute('aria-valuemin','0');meter.setAttribute('aria-valuemax',String(team.seats));meter.setAttribute('aria-valuenow',String(count));
   const fill=document.createElement('i');fill.style.width=`${Math.round(count*100/team.seats)}%`;meter.append(fill);
   const total=document.createElement('strong');total.textContent=`${count}/${team.seats}`;
   row.append(name,meter,total);node.append(row);
 });
}
async function mutate(action,data={}){
 if(busy)return;
 busy=true;$$('.lab-actions button').forEach(b=>b.disabled=true);
 try{
   workspace=await request('/api/action',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({revision:workspace.state.revision,action,data})});
   render();return true;
 }catch(err){
   const line=location.hash==='#live-lab'&&document.querySelector('#pane-integration:not([hidden])')?$('#mapping-feedback'):$('#criteria-feedback');
   line.dataset.result='error';line.textContent=`Action not saved: ${err.message}`;
   if(/changed in another tab/i.test(err.message)){await load()}
   return false;
 }finally{busy=false;$$('.lab-actions button').forEach(b=>b.disabled=false);if(workspace)$('#clarify-action').disabled=workspace.state.criteria.find(c=>c.id==='CR-02').description===observable;}
}
async function load(){
 try{workspace=await request('/api/workspace');render();}
 catch(err){$('#lab-storage').textContent='DATABASE UNAVAILABLE';$('#criteria-copy').textContent='The live workspace could not load.';$('#criteria-feedback').textContent=err.message;$$('.lab-actions button').forEach(b=>b.disabled=true)}
}
$$('[data-lab]').forEach(b=>b.addEventListener('click',()=>{
 const id=b.dataset.lab;
 $$('[data-lab]').forEach(t=>{const selected=t===b;t.classList.toggle('is-selected',selected);t.setAttribute('aria-selected',String(selected));t.tabIndex=selected?0:-1;});
 $$('.lab-pane').forEach(t=>{t.hidden=t.id!==`pane-${id}`});
 $('#lab-step').textContent=({criteria:'01 / REQUIREMENTS',integration:'02 / INTEGRATION',adoption:'03 / BEHAVIOUR CHANGE'})[id];
}));
$$('[data-lab]').forEach((b,i,tabs)=>b.addEventListener('keydown',e=>{
 if(!['ArrowRight','ArrowLeft','Home','End'].includes(e.key))return;e.preventDefault();
 const n=e.key==='Home'?0:e.key==='End'?tabs.length-1:(i+(e.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;
 tabs[n].click();tabs[n].focus();
}));
$('#clarify-action').addEventListener('click',async()=>{
 if(await mutate('edit_criterion',{id:'CR-02',description:observable,kind:'essential'})){
   $('#criteria-feedback').dataset.result='success';$('#criteria-feedback').textContent='SAVED · The requirement now describes observable work. Previous sign-off is invalidated; a human must review it in the studio.';
 }
});
$('#mapping-test').addEventListener('click',()=>mutate('run_mapping_test'));
$('#mapping-break').addEventListener('click',async()=>{if(await mutate('edit_mapping',{target:'job_id',path:'job.invalid'})){$('#mapping-feedback').dataset.result='error';$('#mapping-feedback').textContent='BROKEN · Source path changed to job.invalid. Run the test to see the validation failure.';}});
$('#mapping-fix').addEventListener('click',async()=>{if(await mutate('edit_mapping',{target:'job_id',path:'job.id'})){$('#mapping-feedback').dataset.result='';$('#mapping-feedback').textContent='REPAIRED · Source path restored. Rerun validation to earn a passing result.';}});
$$('[data-choice]').forEach(b=>b.addEventListener('click',()=>{
 const isRight=b.dataset.choice==='b';
 $$('[data-choice]').forEach(x=>{x.classList.remove('selected','correct','incorrect');x.setAttribute('aria-pressed','false')});
 b.classList.add('selected',isRight?'correct':'incorrect');b.setAttribute('aria-pressed','true');
 $('#answer-feedback').textContent=isRight?'Correct approach. Ask the hiring owner to define observable job-related evidence, update the criteria, then run fresh examples with human review. This is a simulated training check—not evidence of a real customer being trained.':'Not recommended. An ambiguous attribute should not become an automatic eligibility filter. Clarify job-related evidence with the hiring owner and retest before rollout.';
}));
initReveals();load();
})();
