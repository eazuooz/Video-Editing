// Prepare a replacement for the confirmed missing bridge prefix only.
// Wait for the existing parent pipeline; never replace the composite without review.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawn,spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base='projects/picking-sides/production/';
const target=path.join(__dirname,'existing-game-replan/phrase-repair1');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const file=path.join(__dirname,'repair-v2-phrases.json');
const alive=pid=>{try{process.kill(pid,0);return true}catch(e){if(e.code!=='ESRCH')throw e;return false}};
if(fs.existsSync(file)){const prior=read(file);if(alive(prior.pid))throw Error('Bridge repair already alive');if(prior.status==='candidate-ready-for-direct-review')throw Error('Review existing candidate instead of regenerating');}
fs.mkdirSync(target,{recursive:true});
const sourceManifest=path.join(__dirname,'existing-game-replan/phrase-repair1/manifest.json');
const manifest=read(sourceManifest);
manifest.tts.outputDir='shared/output/narration/picking-sides/qwen3-1.7b-balanced-v2-phrase-repair1';
manifest.tts.filenameStem='picking-sides-phrase-repair1';
const manifestPath=path.join(target,'manifest.json');
fs.writeFileSync(manifestPath,JSON.stringify(manifest,null,2)+'\n');
const inputs=[sourceManifest,path.join(root,manifest.paths.script),path.join(root,'projects/picking-sides/script/narration.ko.json')].map(p=>({path:p,sha256:hash(p)}));
const state={pid:process.pid,status:'initializing',startedAt:new Date().toISOString(),inputs,children:[],
 reason:'Targeted02prefix omission,05game-name distortion and07chicken-wording repair. See phrase-repair1/request.json; original explanation PCM stays untouched.',
 replacesOriginalExplanation:false,originalPrefixSeconds:29.175,compositeReplaced:false,
 humanListening:'pending',log:base+'logs/v2-phrase-repair1.log'};
function save(status,extra={}){
 Object.assign(state,{status,updatedAt:new Date().toISOString()},extra);fs.writeFileSync(file,JSON.stringify(state,null,2)+'\n');
 const qp=path.join(root,'production/batches/sakurai-planning-game-design/queue.json'),q=read(qp),i=q.items.find(x=>x.slug==='picking-sides');
 i.execution.phraseRepair={...i.execution.phraseRepair,...state,state:base+'repair-v2-phrases.json',runner:base+'repair-v2-phrases.cjs'};
 q.updatedAt=state.updatedAt;fs.writeFileSync(qp,JSON.stringify(q,null,2)+'\n');
}
function verify(){for(const i of inputs)if(hash(i.path)!==i.sha256)throw Error('Bridge reviewed text changed; stop and review');}
const sleep=()=>new Promise(r=>setTimeout(r,30000));
async function run(kind,args){
 verify();await new Promise((resolve,reject)=>{
 const log=fs.createWriteStream(path.join(root,state.log),{flags:'a'});
 const p=spawn(path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-u',...args],{cwd:root,windowsHide:true,env:{...process.env,PYTHONIOENCODING:'utf-8',OMP_NUM_THREADS:'2',MKL_NUM_THREADS:'2'}});
 const c={kind,pid:p.pid,status:'running',startedAt:new Date().toISOString()};state.children.push(c);save(kind+'-running');
 p.stdout.pipe(log,{end:false});p.stderr.pipe(log,{end:false});
 p.once('error',e=>{log.end();reject(e)});p.once('exit',code=>{log.end();Object.assign(c,{status:code===0?'finished':'failed',exitCode:code,finishedAt:new Date().toISOString()});save(kind+'-finished');code===0?resolve():reject(Error(kind+' exit '+code));});
 });
}
(async()=>{
 save('waiting-for-v2-parent');
 const parentFile=path.join(__dirname,'resource-v2-runner.json');
 while(true){verify();const parent=read(parentFile);if(!alive(parent.pid))break;await sleep();}
 let stable=0;
 while(stable<3){
  verify();
  const gpu=spawnSync('nvidia-smi',['--query-gpu=memory.total,memory.used,utilization.gpu','--format=csv,noheader,nounits'],{encoding:'utf8',windowsHide:true});
  if(gpu.status!==0)throw Error(gpu.stderr);
  const [total,used,utilization]=gpu.stdout.trim().split('\n')[0].split(',').map(Number);
  const scan=spawnSync('powershell',['-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -match 'render_narration.py|generate_sample.py' } | Select-Object ProcessId | ConvertTo-Json -Compress"],{encoding:'utf8',windowsHide:true});
  if(scan.status!==0)throw Error(scan.stderr);
  const processes=scan.stdout.trim()?JSON.parse(scan.stdout):[];
  const competing=Array.isArray(processes)?processes:[processes];
  stable=total-used>=9000&&utilization<=35&&!competing.length?stable+1:0;
  save('waiting-for-free-gpu',{gpuObservation:{freeMiB:total-used,utilization,competing,stable}});
  if(stable<3)await sleep();
 }
 const relative=path.relative(root,manifestPath);
 await run('bridge-tts',['qwen3-tts/render_narration.py','--project','picking-sides','--manifest',relative,'--device','cuda:0']);
 await run('bridge-cpu-asr',['qwen3-tts/review_project_narration.py','--project','picking-sides','--manifest',relative,'--device','cpu']);
 save('candidate-ready-for-direct-review',{candidateDirectory:manifest.tts.outputDir,
 nextAction:'Directly review all four candidate paragraphs in02/05/07. Preserve02first29.175seconds,05unaffected suffix and07unaffected prefix/suffix at inspected silence boundaries. Archive all old waves before any composite replacement, then refresh12scene assembly/current-hash ASR/timing. No automatic approval or render.'});
})().catch(e=>{save('failed',{failure:String(e)});console.error(e);process.exitCode=1});
