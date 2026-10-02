// Single resource-aware pipeline for the reviewed existing-game revision.
// Never stops other processes, never regenerates preserved explanation chunks.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawn,spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base='projects/picking-sides/production/',revision=base+'existing-game-replan/';
const statePath=path.join(root,base+'resource-v2-runner.json'),queuePath=path.join(root,'production/batches/sakurai-planning-game-design/queue.json');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const paths=['projects/picking-sides/project.json','projects/picking-sides/script/narration.ko.json','projects/picking-sides/script/narration.en.json','projects/picking-sides/planning/action-map.json',base+'script-source-review.json',revision+'actual-only.manifest.json',revision+'actual-only.ko.json',revision+'bridge02.manifest.json',revision+'bridge02.ko.json'];
const inputs=paths.map(p=>({path:p,sha256:hash(p)}));
if(fs.existsSync(statePath)){
 const prior=JSON.parse(fs.readFileSync(statePath,'utf8'));
 if(prior.pid&&prior.pid!==process.pid){let alive=false;try{process.kill(prior.pid,0);alive=true}catch(e){if(e.code!=='ESRCH')throw e}if(alive)throw Error(`v2 runner PID${prior.pid} still alive; do not duplicate.`);}
 if(prior.status==='tts-asr-ready-for-direct-review')throw Error('Already finished; review existing results instead of rerunning.');
}
const state={pid:process.pid,startedAt:new Date().toISOString(),status:'initializing-v2',inputs,minimumFreeMiB:9000,maximumUtilizationPercent:35,stableSamplesRequired:3,checkIntervalSeconds:30,children:[],logs:{runner:base+'logs/resource-v2-runner.log',bridge:base+'logs/v2-bridge-tts.log',tts:base+'logs/v2-actual-tts.log',assemble:base+'logs/v2-assembly.log',asr:base+'logs/v2-asr.log'},speechAutomaticallyApproved:false};
function save(status,extra={}){
 Object.assign(state,{status,updatedAt:new Date().toISOString()},extra);fs.writeFileSync(statePath,JSON.stringify(state,null,2)+'\n');
 const q=JSON.parse(fs.readFileSync(queuePath,'utf8')),i=q.items.find(x=>x.slug==='picking-sides');i.stage=status;i.updatedAt=state.updatedAt;
 const old=i.execution||{};i.execution={...old,updatedAt:state.updatedAt,runner:base+'resource-v2-runner.cjs',state:base+'resource-v2-runner.json',pid:process.pid,status,logs:state.logs,children:state.children,activeTasks:state.children.filter(x=>x.status==='running'),ttsStarted:state.children.some(x=>x.kind.includes('tts')),ttsComplete:status==='tts-asr-ready-for-direct-review',toolSessionId:state.toolSessionId||old.v2ToolSessionId||null};
 i.nextAction=status==='tts-asr-ready-for-direct-review'?'Read all12current-hash ASRs against72paragraphs, including composite02 boundary; do not reuse oldv1scene09 approval. Then measured60:40, final cuts/scenes/mix/KO-EN, full QA/collection/captioned private upload and Git.':status.startsWith('waiting')?'Reuse this single livev2runner. It observes other Qwen/training jobs without stopping them. Never start a duplicate GPU run or oldrepair09b.':'Read this livev2state and logs; no final render or speech approval implied.';
 q.updatedAt=state.updatedAt;fs.writeFileSync(queuePath,JSON.stringify(q,null,2)+'\n');
}
function verify(){for(const x of inputs)if(hash(x.path)!==x.sha256)throw Error('Reviewed input changed: '+x.path);}
function observe(){
 const g=spawnSync('nvidia-smi',['--query-gpu=memory.total,memory.used,utilization.gpu','--format=csv,noheader,nounits'],{encoding:'utf8',windowsHide:true});if(g.status!==0)throw Error(g.stderr);
 const[total,used,util]=g.stdout.trim().split('\n')[0].split(',').map(Number);
 const p=spawnSync('powershell',['-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' } | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"],{encoding:'utf8',windowsHide:true});if(p.status!==0)throw Error(p.stderr);
 const rows=p.stdout.trim()?JSON.parse(p.stdout):[],all=Array.isArray(rows)?rows:[rows];
 return {at:new Date().toISOString(),totalMiB:total,usedMiB:used,freeMiB:total-used,utilizationPercent:util,competingSynthesisPids:all.filter(x=>/render_narration\.py|generate_sample\.py/.test(x.CommandLine||'')).map(x=>x.ProcessId),otherPythonPids:all.map(x=>x.ProcessId),action:'Observe only; never stop unrelated synthesis/training.'};
}
async function gpuReady(next){let stable=0,checks=0;while(stable<3){verify();const o=observe();stable=o.freeMiB>=9000&&o.utilizationPercent<=35&&!o.competingSynthesisPids.length?stable+1:0;state.gpuObservation=o;state.stableSamples=stable;if(checks++%4===0||stable)save('waiting-for-free-gpu-v2',{nextSynthesis:next});if(stable<3)await new Promise(r=>setTimeout(r,30000));}}
function child(kind,args,log){return new Promise((resolve,reject)=>{
 verify();const stream=fs.createWriteStream(path.join(root,log),{flags:'a'}),p=spawn(path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-u',...args],{cwd:root,windowsHide:true,env:{...process.env,PYTHONIOENCODING:'utf-8',OMP_NUM_THREADS:'2',MKL_NUM_THREADS:'2'}});
 const record={kind,pid:p.pid,args,startedAt:new Date().toISOString(),status:'running',log};state.children.push(record);save('v2-'+kind+'-running');p.stdout.pipe(stream,{end:false});p.stderr.pipe(stream,{end:false});
 p.on('error',e=>{stream.end();reject(e)});p.on('exit',code=>{stream.end();Object.assign(record,{status:code===0?'finished':'failed',exitCode:code,finishedAt:new Date().toISOString()});save('v2-'+kind+'-finished');code===0?resolve():reject(Error(`${kind} exited${code}; inspect${log}`));});
});}
(async()=>{
 const gate=read(base+'script-source-review.json'),plan=read('projects/picking-sides/planning/action-map.json');
 if(!gate.currentPlanApproved||!plan.sourceObservationReady||gate.actualSelfCreatedGameFootage!==false)throw Error('Existing-game editorial gate not approved');
 for(const c of plan.chapters.flatMap(x=>x.cuts))if(!c.sourceId||c.take||c.classification!=='actual-existing-game-action'||c.loop||c.speed!==1)throw Error('Nonconforming source cut');
 const pre=spawnSync(process.execPath,['scripts/review-video-duplicates.cjs','picking-sides','--check'],{cwd:root,encoding:'utf8',windowsHide:true});if(pre.status!==0)throw Error(pre.stdout+pre.stderr);
 console.log(`Reviewed existing-gamev2runner PID${process.pid}; preserve29explanation paragraphs and PCM; observe GPU only.`);
 save('waiting-for-free-gpu-v2');
 const composite=path.join(root,'shared/output/narration/picking-sides/qwen3-1.7b-balanced-v2/chunks/02-scene.wav');
 if(!fs.existsSync(composite)){
  await gpuReady('changed-bridge-only');await child('bridge-tts',['qwen3-tts/render_narration.py','--project','picking-sides','--manifest',revision+'bridge02.manifest.json','--device','cuda:0'],state.logs.bridge);
  await child('compose02',[base+'compose-v2-scene02.py'],state.logs.assemble);
 } else if(!fs.existsSync(path.join(root,revision+'scene02-composite.json')))throw Error('Scene02 exists without preservation proof');
 await gpuReady('six-actual-game-chapters-only');
 await child('actual-tts',['qwen3-tts/render_narration.py','--project','picking-sides','--manifest',revision+'actual-only.manifest.json','--device','cuda:0'],state.logs.tts);
 await child('assemble',[base+'assemble-v2-narration.py'],state.logs.assemble);
 await child('cpu-asr',['qwen3-tts/review_project_narration.py','--project','picking-sides','--device','cpu'],state.logs.asr);
 save('tts-asr-ready-for-direct-review',{finishedAt:new Date().toISOString(),speechAutomaticallyApproved:false});console.log('All12currentv2ASRs ready for direct review; no final render or automatic speech approval.');
})().catch(e=>{save('failed-v2',{failure:String(e),finishedAt:new Date().toISOString()});console.error(e);process.exitCode=1;});
