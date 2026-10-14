// After the original56jobs,run only short diagnoses,returning CPU resources
// between windows. Never change research resource gates or foreign processes.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawn,execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),statePath=path.join(__dirname,'voice-diagnostics-execution-v1.json');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,'')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),now=()=>new Date().toISOString(),sleep=ms=>new Promise(r=>setTimeout(r,ms));
function processes(){return [].concat(JSON.parse(execFileSync('powershell.exe',['-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python(w)?|node)\\.exe$' } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],{encoding:'utf8',windowsHide:true,maxBuffer:2*1024*1024})));}
function write(s){const t=statePath+'.tmp-'+process.pid;fs.writeFileSync(t,JSON.stringify(s,null,2)+'\n');fs.renameSync(t,statePath);}
async function main(){
 if(fs.existsSync(statePath))throw Error('Existing diagnostic execution preserved;inspect actual identity');
 const planPath=path.join(__dirname,'voice-diagnostic-plan-v1.json'),plan=read(planPath),worker='production/research/game-lighting-history/review-voice-diagnostic-v1.py';
 if(sha(path.join(root,plan.audio.path))!==plan.audio.sha256)throw Error('Current PCM changed');
 const s={startedAt:now(),pid:process.pid,command:process.argv,cwd:root,status:'waiting-for-original56windows',planSha256:sha(planPath),expectedWindows:plan.jobs.length,completed:[],worker:null,cpuThreads:2,gpuJobs:0,currentNarrationApproved:false,humanWholeListeningApproved:false,finalMixedAsr:false,schedulingPolicy:'Wait for original56completion;one short CPU2worker only while actual research child is healthy;return Python resources for30s between jobs;no foreign gate/pause/control/process mutation.'};write(s);
 const deadline=Date.now()+12*3600*1000;
 for(const job of plan.jobs){
  while(true){
   const original=read(path.join(__dirname,'remaining-voice-asr-execution-v2.json')),research=read('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json'),p=processes();
   if(original.status.startsWith('failed'))throw Error('OriginalASR failed;preserve results and inspect');
   const originalComplete=original.status==='all56-windows-complete-awaiting-direct-review'&&original.completed.length===56;
   const owner=p.find(x=>x.ProcessId===research.owner_pid&&x.CommandLine?.includes('resume_with_preview.py')),child=p.find(x=>x.ProcessId===research.child_pid&&x.ParentProcessId===research.owner_pid);
   const voiceWorkers=p.filter(x=>/review-voice-(window-v2|diagnostic-v1)\.py/.test(x.CommandLine||''));
   s.originalCompletionObserved={status:original.status,completed:original.completed.length};s.researchObservation={observedAt:now(),...research,owner,child};s.current=job;s.status=!originalComplete?'waiting-for-original56windows':research.status==='running'&&owner&&child&&!voiceWorkers.length?'launching-single-short-diagnostic':'waiting-for-live-research-child';write(s);
   if(s.status==='launching-single-short-diagnostic')break;
   if(Date.now()>deadline)throw Error('Resource boundary wait exceeded12hours;no foreign changes attempted');
   await sleep(30000);
  }
  const folder=path.join(root,'projects/game-lighting-history-04/production/local/voice-diagnostics-v1');fs.mkdirSync(folder,{recursive:true});const out=path.join(folder,job.label+'.json');
  if(fs.existsSync(out))throw Error('Existing diagnostic result preserved');
  const log=fs.openSync(path.join(folder,job.label+'.log'),'a');const child=spawn(path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8','-u',worker,'--label',job.label],{cwd:root,windowsHide:true,env:{...process.env,CUDA_VISIBLE_DEVICES:'-1',OMP_NUM_THREADS:'2',MKL_NUM_THREADS:'2'},stdio:['ignore',log,log]});
  s.worker={proxyPid:child.pid,command:child.spawnargs,startedAt:now()};s.status='recognizing-single-short-diagnostic';write(s);
  const exit=await new Promise((resolve,reject)=>{child.on('error',reject);child.on('exit',(code,signal)=>resolve({code,signal}));});fs.closeSync(log);
  if(exit.code!==0)throw Error('Diagnostic failed:'+JSON.stringify({job,...exit}));
  const r=read(out);if(r.audio.sha256!==plan.audio.sha256||r.expectedTextUsedAsPrompt!==false)throw Error('Diagnostic input mismatch');
  s.completed.push({label:job.label,result:path.relative(root,out).replaceAll('\\','/'),sha256:sha(out),exitCode:exit.code});s.worker=null;s.status='returning-CPU-resources-to-research';s.lastWindowEndedAt=now();write(s);console.log('DONE '+job.label+' '+s.completed.length+'/'+plan.jobs.length);await sleep(30000);
 }
 s.status='all-short-diagnostics-complete-awaiting-direct-review';s.exitCode=0;s.endedAt=now();s.current=null;write(s);
}
main().catch(e=>{if(fs.existsSync(statePath)){const s=read(statePath);if(s.pid===process.pid){s.status='failed-preserving-input-and-completed-diagnostics';s.error=String(e);s.endedAt=now();write(s);}}console.error(e);process.exitCode=1;});
