const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawn,execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base='projects/game-lighting-history-04/production',read=p=>JSON.parse(fs.readFileSync(path.resolve(root,p),'utf8').replace(/^\uFEFF/,'')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.resolve(root,p))).digest('hex'),now=()=>new Date().toISOString();
const statePath=base+'/voice-repair-diagnostic-execution-v2.json';function write(s){fs.writeFileSync(path.join(root,statePath),JSON.stringify(s,null,2)+'\n');}
function processes(){return[].concat(JSON.parse(execFileSync('powershell.exe',['-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python(w)?|node)\\.exe$' } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],{encoding:'utf8',windowsHide:true,maxBuffer:2*1024*1024})));}
async function main(){
 if(fs.existsSync(path.join(root,statePath)))throw Error('Existing diagnostic execution preserved');
 const prior=read(base+'/voice-repair-asr-execution-v1.json'),planPath=base+'/voice-repair-diagnostic-plan-v2.json',plan=read(planPath),live=processes();
 if(prior.status!=='all12-repair-windows-complete-awaiting-direct-review'||prior.completed.length!==12||live.some(p=>/review-episode04-repair-(window-v1|diagnostic-v2)\.py/.test(p.CommandLine||'')))throw Error('Prior recognition must be completed and workers exited');
 const s={startedAt:now(),pid:process.pid,command:process.argv,cwd:root,status:'checking-live-research-boundary',cpuThreads:2,gpuJobs:0,planSha256:sha(planPath),completed:[],expectedWindows:2,currentNarrationApproved:false};write(s);
 for(const job of plan.jobs){
  const research=read('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json'),p=processes(),owner=p.find(x=>x.ProcessId===research.owner_pid&&x.CommandLine?.includes('resume_with_preview.py')),child=p.find(x=>x.ProcessId===research.child_pid&&x.ParentProcessId===research.owner_pid);
  if(research.status!=='running'||!owner||!child)throw Error('Actual research queue/job must be running');
  const folder=path.join(root,base,'local/voice-repair-diagnostic-v2'),output=path.join(folder,job.label+'.json');fs.mkdirSync(folder,{recursive:true});if(fs.existsSync(output))throw Error('Existing result preserved');
  const log=fs.openSync(path.join(folder,job.label+'.log'),'a'),worker=spawn(path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8','-u','production/research/game-lighting-history/review-episode04-repair-diagnostic-v2.py','--label',job.label],{cwd:root,windowsHide:true,env:{...process.env,CUDA_VISIBLE_DEVICES:'-1',OMP_NUM_THREADS:'2',MKL_NUM_THREADS:'2'},stdio:['ignore',log,log]});
  s.status='recognizing-one-diagnostic';s.current=job;s.worker={proxyPid:worker.pid,command:worker.spawnargs,startedAt:now()};s.researchObservation={observedAt:now(),...research,owner,child};write(s);
  const exit=await new Promise((resolve,reject)=>{worker.on('error',reject);worker.on('exit',(code,signal)=>resolve({code,signal}));});fs.closeSync(log);if(exit.code!==0)throw Error(JSON.stringify(exit));
  const r=read(output);if(r.expectedTextUsedAsPrompt!==false||r.audio.sha256!==plan.audio.sha256)throw Error('Recognition input mismatch');s.completed.push({label:job.label,result:path.relative(root,output).replaceAll('\\','/'),sha256:sha(output),exitCode:0});s.worker=null;s.status='between-diagnostics';write(s);console.log('DONE '+job.label);await new Promise(r=>setTimeout(r,30000));
 }
 s.status='both-diagnostics-complete-awaiting-direct-review';s.exitCode=0;s.endedAt=now();s.current=null;write(s);
}
main().catch(e=>{if(fs.existsSync(path.join(root,statePath))){const s=read(statePath);if(s.pid===process.pid){s.status='failed-preserving-input-and-results';s.error=String(e);s.endedAt=now();write(s);}}console.error(e);process.exitCode=1;});
