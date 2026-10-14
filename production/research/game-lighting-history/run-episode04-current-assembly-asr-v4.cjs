// Single CPU2 recognizer, return resources between windows; never mutate foreign gates.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawn,execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base='projects/game-lighting-history-04/production',statePath=path.join(root,base,'current-assembly-asr-execution-v4.json');
const read=p=>JSON.parse(fs.readFileSync(path.resolve(root,p),'utf8').replace(/^\uFEFF/,'')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),now=()=>new Date().toISOString(),sleep=ms=>new Promise(r=>setTimeout(r,ms));
function processes(){return[].concat(JSON.parse(execFileSync('powershell.exe',['-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python(w)?|node|ffmpeg)\\.exe$' } | Select-Object Name,ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],{encoding:'utf8',windowsHide:true,maxBuffer:2*1024*1024})));}
function write(s){const t=statePath+'.tmp-'+process.pid;fs.writeFileSync(t,JSON.stringify(s,null,2)+'\n');fs.renameSync(t,statePath);}
async function main(){
 if(fs.existsSync(statePath))throw Error('Existing recognition execution preserved; inspect actual identity');
 const planPath=path.join(root,base,'current-assembly-asr-plan-v4.json'),plan=read(planPath),worker='production/research/game-lighting-history/review-episode04-current-assembly-window-v4.py';
 const s={startedAt:now(),pid:process.pid,command:process.argv,cwd:root,status:'waiting-for-live-research-child',planSha256:sha(planPath),expectedWindows:plan.jobs.length,completed:[],worker:null,cpuThreads:2,gpuJobs:0,currentNarrationApproved:false,humanWholeListeningApproved:false,finalMixedAsr:false};write(s);const deadline=Date.now()+12*3600*1000;
 for(const job of plan.jobs){
  while(true){
   const research=read('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json'),p=processes(),owner=p.find(x=>x.ProcessId===research.owner_pid&&x.CommandLine?.includes('resume_with_preview.py')),child=p.find(x=>x.ProcessId===research.child_pid&&x.ParentProcessId===research.owner_pid);
   const competing=p.filter(x=>/review-(voice|episode04)-.*\.py/.test(x.CommandLine||'') || x.Name==='ffmpeg.exe'&&x.CommandLine?.includes('game-lighting-history') || /(?:extract|verify)-episode0[34].*\.cjs/.test(x.CommandLine||''));
   s.current=job;s.researchObservation={observedAt:now(),...research,owner,child};s.status=research.status==='running'&&owner&&child&&!competing.length?'launching-single-repair-window':'waiting-for-live-research-child-and-free-QA-slot';write(s);
   if(s.status==='launching-single-repair-window')break;if(Date.now()>deadline)throw Error('Resource boundary wait exceeded12hours');await sleep(30000);
  }
  const folder=path.join(root,base,'local/current-assembly-asr-v4');fs.mkdirSync(folder,{recursive:true});const out=path.join(folder,job.label+'.json');if(fs.existsSync(out))throw Error('Existing completed result preserved');
  const log=fs.openSync(path.join(folder,job.label+'.log'),'a'),child=spawn(path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8','-u',worker,'--label',job.label],{cwd:root,windowsHide:true,env:{...process.env,CUDA_VISIBLE_DEVICES:'-1',OMP_NUM_THREADS:'2',MKL_NUM_THREADS:'2'},stdio:['ignore',log,log]});
  s.worker={proxyPid:child.pid,command:child.spawnargs,startedAt:now()};s.status='recognizing-single-repaired-window';write(s);
  const exit=await new Promise((resolve,reject)=>{child.on('error',reject);child.on('exit',(code,signal)=>resolve({code,signal}));});fs.closeSync(log);if(exit.code!==0)throw Error('ASR failed:'+JSON.stringify({job,...exit}));
  const r=read(out);if(r.audio.sha256!==plan.audio.sha256||r.expectedTextUsedAsPrompt!==false)throw Error('Recognition input mismatch');
  s.completed.push({label:job.label,result:path.relative(root,out).replaceAll('\\','/'),sha256:sha(out),exitCode:0});s.worker=null;s.status='returning-CPU-resources-to-research';s.lastWindowEndedAt=now();write(s);console.log('DONE '+job.label+' '+s.completed.length+'/'+plan.jobs.length);await sleep(30000);
 }
 s.status='all11-current-assembly-windows-complete-awaiting-direct-review';s.exitCode=0;s.endedAt=now();s.current=null;write(s);
}
main().catch(e=>{if(fs.existsSync(statePath)){const s=read(statePath);if(s.pid===process.pid){s.status='failed-preserving-input-and-completed-recognitions';s.error=String(e);s.endedAt=now();write(s);}}console.error(e);process.exitCode=1;});
