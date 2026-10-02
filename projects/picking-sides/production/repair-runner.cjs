// One resumable Qwen/CPU-ASR pipeline. Does not interrupt any user's process.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawn,spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),work=__dirname;
const statePath=path.join(work,'repair-runner.json'),queuePath=path.join(root,'production/batches/sakurai-planning-game-design/queue.json');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const inputs=['projects/picking-sides/project.json','projects/picking-sides/script/narration.ko.json','projects/picking-sides/script/narration.en.json'];
const fingerprints=inputs.map(p=>({path:p,sha256:hash(p)}));
const prior=fs.existsSync(statePath)?JSON.parse(fs.readFileSync(statePath,'utf8')):null;
if(prior?.pid&&prior.pid!==process.pid&&prior.status!=='finished'&&prior.status!=='failed'){
 try{process.kill(prior.pid,0);throw new Error(`Existing resource pipeline PID ${prior.pid} is alive; do not duplicate it.`);}catch(e){if(e.code!=='ESRCH')throw e;}
}
const state={pid:process.pid,startedAt:new Date().toISOString(),status:'waiting-for-free-gpu',inputs:fingerprints,minimumFreeMiB:9000,maximumUtilizationPercent:35,stableSamplesRequired:3,checkIntervalSeconds:30,logs:{runner:'projects/picking-sides/production/repair-runner.log',tts:'projects/picking-sides/production/repair-tts.log',asr:'projects/picking-sides/production/repair-asr.log'},children:[]};
function save(stage,extra={}){
 Object.assign(state,{status:stage,updatedAt:new Date().toISOString()},extra);
 fs.writeFileSync(statePath,JSON.stringify(state,null,2)+'\n');
 const q=JSON.parse(fs.readFileSync(queuePath,'utf8')),item=q.items.find(i=>i.slug==='picking-sides');
 item.stage=stage;item.execution={...item.execution,ttsStarted:state.children.some(x=>x.kind==='tts'),runner:'projects/picking-sides/production/repair-runner.cjs',state:'projects/picking-sides/production/repair-runner.json',pid:process.pid,status:stage,logs:state.logs,children:state.children,activeTasks:state.children.filter(x=>x.status==='running'),toolSessionId:state.toolSessionId||item.execution?.toolSessionId||null};
 item.updatedAt=state.updatedAt;item.gpuObservation=state.gpuObservation||item.gpuObservation;
 item.nextAction=stage==='waiting-for-free-gpu'?'Do not restart alive resource runner. Finish CPU storyboard/source/visual tasks; runner starts one approved GPU TTS only after stable free GPU, then CPU ASR.':stage==='tts-asr-ready-for-direct-review'?'Read every current-hash scene ASR against all 72 paragraphs; repair only rejected scenes without duplicate synthesis, then measure/capture/retime/render/QA/private-upload/Git.':stage==='tts-running'?'Reuse this single synthesis process and logs; do not launch a second Qwen job.':'Read exact runner/child logs and current state before proceeding.';
 fs.writeFileSync(queuePath,JSON.stringify(q,null,2)+'\n');
}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function observations(){
 const r=spawnSync('nvidia-smi',['--query-gpu=memory.total,memory.used,utilization.gpu','--format=csv,noheader,nounits'],{encoding:'utf8',windowsHide:true});
 if(r.status!==0)throw Error(r.stderr||'nvidia-smi failed');
 const [total,used,util]=(r.stdout.trim().split('\n')[0]).split(',').map(Number);
 const p=spawnSync('powershell',['-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' } | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"],{encoding:'utf8',windowsHide:true});
 if(p.status!==0)throw Error(p.stderr||'Could not inventory Python processes safely');
 const obj=p.stdout.trim()?JSON.parse(p.stdout.trim()):[],procs=Array.isArray(obj)?obj:[obj];
 const competingSynthesis=procs.filter(x=>/render_narration\.py|generate_sample\.py/.test(x.CommandLine||''));
 return {at:new Date().toISOString(),totalMiB:total,usedMiB:used,freeMiB:total-used,utilizationPercent:util,otherPythonPids:procs.map(x=>x.ProcessId),competingSynthesisPids:competingSynthesis.map(x=>x.ProcessId),action:'Observe only. Never stop unrelated training or other synthesis; start only with stable spare resources.'};
}
function childRun(kind,args){return new Promise((resolve,reject)=>{
 const log=fs.createWriteStream(path.join(work,'repair-'+kind+'.log'),{flags:'a'});
 const child=spawn(path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-u',...args],{cwd:root,windowsHide:true,env:{...process.env,PYTHONIOENCODING:'utf-8',OMP_NUM_THREADS:'2',MKL_NUM_THREADS:'2'}});
 state.children.push({kind,pid:child.pid,args,startedAt:new Date().toISOString(),status:'running'});save(kind==='tts'?'tts-running':'cpu-asr-running');
 child.stdout.pipe(log,{end:false});child.stderr.pipe(log,{end:false});
 child.on('error',e=>{log.end();reject(e)});
 child.on('exit',code=>{log.end();Object.assign(state.children.at(-1),{status:'finished',exitCode:code,finishedAt:new Date().toISOString()});save(kind==='tts'?'tts-finished-awaiting-cpu-asr':'cpu-asr-finished');code===0?resolve():reject(Error(`${kind} exited ${code}; inspect ${kind}.log. No automatic approval.`));});
});}
(async()=>{
 const pre=spawnSync(process.execPath,['scripts/review-video-duplicates.cjs','picking-sides','--check'],{cwd:root,encoding:'utf8',windowsHide:true});if(pre.status!==0)throw Error(pre.stderr||pre.stdout);
 save('waiting-for-free-gpu');console.log(`Resource runner PID ${process.pid}; no TTS has started. Waiting for stable free GPU; other user tasks stay running.`);
 let stable=0,checks=0;
 while(stable<3){
  for(const i of fingerprints)if(hash(i.path)!==i.sha256)throw Error(`Input changed while waiting: ${i.path}. Review and intentionally restart this runner; do not synthesize stale content.`);
  const o=observations();stable=o.freeMiB>=9000&&o.utilizationPercent<=35&&!o.competingSynthesisPids.length?stable+1:0;
  state.gpuObservation=o;state.stableSamples=stable;
  if(checks++%4===0||stable)save('waiting-for-free-gpu');
  if(stable<3)await sleep(30000);
 }
 console.log('Stable spare GPU observed; starting exactly one approved Qwen TTS run.');
 await childRun('tts',['qwen3-tts/render_narration.py','--project','picking-sides','--device','cuda:0','--force-scenes','03,09']);
 await childRun('asr',['qwen3-tts/review_project_narration.py','--project','picking-sides','--device','cpu','--scenes','03,09']);
 save('tts-asr-ready-for-direct-review',{finishedAt:new Date().toISOString(),speechAutomaticallyApproved:false});
 console.log('Synthesis and cached CPU ASR finished. Direct current-hash speech/content review is still required before rendering.');
})().catch(e=>{save('failed',{failure:String(e),finishedAt:new Date().toISOString()});console.error(e);process.exitCode=1;});
