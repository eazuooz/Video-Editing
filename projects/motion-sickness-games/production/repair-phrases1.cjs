// Single approved-voice repair pass, then CPU ASR. Never splice automatically.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawn,spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base='projects/motion-sickness-games/production/',revision=base+'repair1/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const statePath=path.join(root,base,'repair-phrases1.json'),queuePath=path.join(root,'production/batches/sakurai-planning-game-design/queue.json');
const alive=pid=>{try{process.kill(pid,0);return true}catch(e){if(e.code!=='ESRCH')throw e;return false;}};
if(fs.existsSync(statePath)){const old=JSON.parse(fs.readFileSync(statePath,'utf8'));if(alive(old.pid)||old.status==='candidates-ready-for-direct-review')throw Error('Reuse live repair/results; do not duplicate.');}
const request=read(revision+'request.json');
const state={pid:process.pid,startedAt:new Date().toISOString(),status:'initializing',inputs:request.inputs,
 request:revision+'request.json',children:[],humanListening:'pending',automaticallyApproved:false,
 candidateLog:base+'logs/phrase-repair1.log',runnerLog:base+'logs/phrase-repair1-runner.log'};
function retry(fn){let last;for(let n=0;n<10;n++){try{return fn()}catch(e){last=e;Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,150)}}throw last;}
function save(status,extra={}){Object.assign(state,{status,updatedAt:new Date().toISOString()},extra);
 retry(()=>fs.writeFileSync(statePath,JSON.stringify(state,null,2)+'\n'));
 retry(()=>{const q=JSON.parse(fs.readFileSync(queuePath,'utf8')),i=q.items.find(x=>x.slug==='motion-sickness-games');
 if(i.status!=='in-progress')throw Error('Queue item no longer active.');
 i.stage='targeted-seven-paragraph-speech-repair1';i.updatedAt=state.updatedAt;
 i.execution.phase='initial-ASR-reviewed-targeted-repair';i.execution.partialChunkCount=12;
 i.execution.repair1={...i.execution.repair1,...state,runner:base+'repair-phrases1.cjs',state:base+'repair-phrases1.json'};
 i.execution.activeTasks=state.children.filter(c=>c.status==='running');
 i.nextAction='Reuse this single repair of seven paragraphs. Review current-hash candidate ASR directly; preserve unaffected v1 PCM and compose separate v2 only after acceptance, then review all12 composite scenes. No automatic speech/ratio/render/private delivery approval.';
 q.updatedAt=state.updatedAt;fs.writeFileSync(queuePath,JSON.stringify(q,null,2)+'\n');});}
function verify(){for(const i of state.inputs)if(hash(i.path)!==i.sha256)throw Error('Reviewed repair input changed: '+i.path);}
async function gpuReady(){let stable=0;while(stable<3){verify();
 const g=spawnSync('nvidia-smi',['--query-gpu=memory.total,memory.used,utilization.gpu','--format=csv,noheader,nounits'],{encoding:'utf8',windowsHide:true});if(g.status!==0)throw Error(g.stderr);
 const [total,used,utilization]=g.stdout.trim().split('\n')[0].split(',').map(Number);if(![total,used,utilization].every(Number.isFinite))throw Error('Invalid GPU snapshot');
 const p=spawnSync('powershell',['-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -match 'render_narration.py|generate_sample.py' } | Select-Object ProcessId | ConvertTo-Json -Compress"],{encoding:'utf8',windowsHide:true});if(p.status!==0)throw Error(p.stderr);
 const rows=p.stdout.trim()?JSON.parse(p.stdout):[],competing=Array.isArray(rows)?rows:[rows];
 stable=total-used>=9000&&utilization<=35&&!competing.length?stable+1:0;
 save('waiting-for-free-gpu',{gpuObservation:{at:new Date().toISOString(),freeMiB:total-used,utilization,competingSynthesisPids:competing.map(x=>x.ProcessId),stable}});
 if(stable<3)await new Promise(r=>setTimeout(r,30000));}}
async function run(kind,args){verify();await new Promise((resolve,reject)=>{
 const stream=fs.createWriteStream(path.join(root,state.candidateLog),{flags:'a'});
 const p=spawn(path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-u',...args],{cwd:root,windowsHide:true,
 env:{...process.env,PYTHONIOENCODING:'utf-8',OMP_NUM_THREADS:'2',MKL_NUM_THREADS:'2'}});
 const c={kind,pid:p.pid,args,status:'running',startedAt:new Date().toISOString()};state.children.push(c);save(kind+'-running');
 p.stdout.pipe(stream,{end:false});p.stderr.pipe(stream,{end:false});
 p.once('error',e=>{stream.end();reject(e)});p.once('exit',code=>{stream.end();Object.assign(c,{status:code===0?'finished':'failed',exitCode:code,finishedAt:new Date().toISOString()});
 try{save(kind+'-finished');code===0?resolve():reject(Error(kind+' exit '+code))}catch(e){reject(e)}});});}
(async()=>{verify();const check=spawnSync(process.execPath,['scripts/review-video-duplicates.cjs','motion-sickness-games','--check'],{cwd:root,encoding:'utf8',windowsHide:true});if(check.status!==0)throw Error(check.stdout+check.stderr);
 console.log('Repair1 PID '+process.pid+'; seven source-matched paragraphs only, all original v1 files preserved.');
 await gpuReady();await run('candidate-tts',['qwen3-tts/render_narration.py','--project','motion-sickness-games','--manifest',revision+'manifest.json','--device','cuda:0']);
 await run('candidate-cpu-asr',['qwen3-tts/review_project_narration.py','--project','motion-sickness-games','--manifest',revision+'manifest.json','--device','cpu']);
 save('candidates-ready-for-direct-review',{finishedAt:new Date().toISOString(),candidateDirectory:'shared/output/narration/motion-sickness-games/qwen3-1.7b-balanced-v1-phrase-repair1'});
 console.log('Candidate ASRs ready; no splice/approval performed.');
})().catch(e=>{try{save('failed',{failure:String(e),finishedAt:new Date().toISOString()})}catch(s){console.error(s)}console.error(e);process.exitCode=1;});
