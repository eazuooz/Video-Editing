// Resume existing single jobs. Stop for actual ASR and every-cue visual review.
// Never infer collection, approval, private upload or Git delivery.
const fs=require('node:fs'),path=require('node:path'),{spawn}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),slug='counting-animation-frames',base=path.dirname(__dirname),queue=path.join(root,'production/batches/sakurai-planning-game-design/queue.json');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8')),m=read(path.join(base,'project.json')),out=path.join(root,m.tts.outputDir),stem=m.tts.filenameStem;
const runnerFile=path.join(__dirname,'technical-runner.json');
const runnerLog=process.env.COUNTING_RUNNER_LOG||'projects/counting-animation-frames/production/technical-runner-repaired.log';
if(fs.existsSync(runnerFile)){const prev=read(runnerFile);if(prev.state==='running'){try{process.kill(prev.pid,0);throw Error('Existing runner active: '+prev.pid);}catch(e){if(e.code!=='ESRCH')throw e;}}}
function checkpoint(stage,state='running',extra={}){const entry={pid:process.pid,parentPid:process.ppid,state,stage,updatedAt:new Date().toISOString(),log:runnerLog,...extra};fs.writeFileSync(runnerFile,JSON.stringify(entry,null,2)+'\n');const q=read(queue),i=q.items.find(x=>x.slug===slug);i.activeExecution??={};i.activeExecution.technicalRunner={...(i.activeExecution.technicalRunner||{}),...entry};i.stage=stage;i.updatedAt=entry.updatedAt;i.nextAction=state==='finished'?'Inspect every scene/full ASR, all cue/cut sheets, mobile and intro/outro. After actual QA finalize/collect, all-rule private upload and selective commit/push.':state==='failed'?'Read actual failure/log; repair only the affected stage and preserve completed jobs.':'Single existing runner continues; do not duplicate synthesis, CPU ASR, capture or render. Human/public decisions remain pending.';q.updatedAt=i.updatedAt;fs.writeFileSync(queue,JSON.stringify(q,null,2)+'\n');console.log(stage,state);}
const delay=ms=>new Promise(r=>setTimeout(r,ms));
function run(cmd,args){return new Promise((resolve,reject)=>{const p=spawn(cmd,args,{cwd:root,windowsHide:true,stdio:['ignore','inherit','inherit']});p.on('error',reject);p.on('exit',code=>code===0?resolve():reject(Error(cmd+' failed: '+code)));});}
async function waitUntil(check,stage){checkpoint(stage);const until=Date.now()+3*3600e3;while(!check()){if(Date.now()>until)throw Error('Timed out waiting for '+stage);await delay(15000);}}
(async()=>{
 await waitUntil(()=>['.wav','.timing.json','.en.srt'].every(s=>fs.existsSync(path.join(out,stem+s)))&&fs.existsSync(path.join(out,stem+'.asr-review.json'))&&read(path.join(out,stem+'.asr-review.json')).complete,'waiting-existing-single-narration-and-cpu-asr');
 // A watch can read a rejected attempt before Qwen's ending repair replaces it.
 // Refresh only after the complete measured package exists; hashes invalidate
 // stale caches. Do not approve a read-back from a superseded scene WAV.
 checkpoint('refresh-current-chunk-cpu-asr');await run(path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8','qwen3-tts/review_project_narration.py','--project',slug,'--device','cpu']);
 const report=read(path.join(out,stem+'.asr-review.json')),failed=require('./asr-gate.cjs').failures(report);
 if(failed.length)throw Error('Actual scene ASR/end gate needs inspection: '+failed.map(s=>s.scene+' similarity='+s.similarity).join(', '));
 await waitUntil(()=>['rate','interval','poses','pause','render'].every(n=>fs.existsSync(path.join(root,'shared/assets',slug,'playtests-v2',n+'.mp4'))&&fs.existsSync(path.join(__dirname,n+'-v2-input-log.json'))),'waiting-existing-mode-isolated-playtests-v2');
 for(const mode of ['rate','interval','poses','pause','render'])if(!Object.values(read(path.join(__dirname,mode+'-v2-input-log.json')).assertions).every(Boolean))throw Error('Mechanics assertion failed: '+mode);
 if(!['rate','interval','poses','pause','render'].every(n=>fs.existsSync(path.join(root,'shared/assets',slug,'playtests-v2',n+'-sound.mp4')))){checkpoint('original-input-collision-sfx-export');await run(path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8',path.join(__dirname,'synthesize-game-sounds.py')]);}
 checkpoint('full-narration-cpu-asr');await run(path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8','qwen3-tts/transcribe_reference.py',path.join(out,stem+'.wav'),'--device','cpu','--output',path.join(__dirname,'full-narration-asr.txt')]);
 for(const [stage,cmd,args] of [
  ['current-project-technical-helpers',process.execPath,[path.join(__dirname,'setup-pipeline.cjs')]],
  ['measured-timeline-unique-normal-speed-cuts',process.execPath,[path.join(__dirname,'build-video.cjs'),'prepare']],
  ['word-aligned-bilingual-captions',path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8',path.join(__dirname,'align-captions.py')]],
  ['continuous-approved-voice-nimbus-mix',process.execPath,[path.join(__dirname,'build-video.cjs'),'mix']],
  ['six-independent-explanation-final-render',process.execPath,[path.join(__dirname,'render-reel.cjs')]],
  ['clean-final-assembly',process.execPath,[path.join(__dirname,'build-video.cjs'),'assemble']],
  ['boxed-korean-captioned-final-render',process.execPath,[path.join(__dirname,'caption-video.cjs')]],
  ['full-decode-audio-and-every-cue-evidence',path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8',path.join(__dirname,'verify-video.py')]]
 ]){checkpoint(stage);await run(cmd,args);}
 checkpoint('rendered-pending-full-asr-and-all-cue-visual-review','finished',{qa:'projects/counting-animation-frames/production/final-v1/qa.json'});
})().catch(e=>{console.error(e);checkpoint('technical-runner-failure','failed',{error:String(e)});process.exitCode=1;});
