// Resume technical work after the existing single TTS/capture jobs finish.
// This never collects, commits, uploads or marks human/visual review complete.
const fs=require('node:fs'),path=require('node:path'),{spawn}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),slug='meaningful-quests',base=path.dirname(__dirname),work=path.join(__dirname,'final-v1'),queue=path.join(root,'production/batches/sakurai-planning-game-design/queue.json');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8')),m=read(path.join(base,'project.json')),out=path.join(root,m.tts.outputDir),stem=m.tts.filenameStem;
const runnerFile=path.join(__dirname,'technical-runner.json');
const repairState=path.join(__dirname,'repair-scene03.json');
const parentIsRepair=fs.existsSync(repairState)&&read(repairState).pid===process.ppid;
const actualLog=process.env.MEANINGFUL_RUNNER_LOG||(parentIsRepair?'projects/meaningful-quests/production/repair-scene03.log':'projects/meaningful-quests/production/technical-runner.log');
if(fs.existsSync(runnerFile)){const prev=read(runnerFile);if(prev.state==='running'){try{process.kill(prev.pid,0);throw Error('Existing runner is active: '+prev.pid);}catch(e){if(e.code!=='ESRCH')throw e;}}}
function checkpoint(stage,state='running',extra={}){const entry={pid:process.pid,parentPid:process.ppid,state,stage,updatedAt:new Date().toISOString(),log:actualLog,...extra};if(actualLog.endsWith('technical-runner-corrected.log'))entry.sessionId=1060;fs.writeFileSync(runnerFile,JSON.stringify(entry,null,2)+'\n');const q=read(queue),i=q.items.find(x=>x.slug===slug);i.activeExecution??={};i.activeExecution.technicalRunner=entry;if(entry.sessionId)i.activeExecution.technicalRunnerSessionId=entry.sessionId;i.stage=stage;i.updatedAt=entry.updatedAt;i.nextAction=state==='finished'?'Inspect all per-scene/full ASR differences and final cue/cut sheets; then finalize, collect, private Studio upload and selective commit/push.':state==='failed'?'Inspect technical-runner log/checkpoint, repair concrete failure, preserve completed jobs and resume.':'Existing technical runner continues; do not duplicate synthesis/capture/render. Final visual, human and Studio review remain pending.';q.updatedAt=i.updatedAt;fs.writeFileSync(queue,JSON.stringify(q,null,2)+'\n');console.log(stage,state);}
const delay=ms=>new Promise(r=>setTimeout(r,ms));
function run(cmd,args){return new Promise((resolve,reject)=>{const p=spawn(cmd,args,{cwd:root,windowsHide:true,stdio:['ignore','inherit','inherit']});p.on('error',reject);p.on('exit',code=>code===0?resolve():reject(Error(cmd+' failed: '+code)));});}
async function waitUntil(check,stage){checkpoint(stage);const until=Date.now()+3*3600e3;while(!check()){if(Date.now()>until)throw Error('Timed out waiting for '+stage);await delay(15000);}}
(async()=>{
 await waitUntil(()=>['.wav','.timing.json','.en.srt'].every(s=>fs.existsSync(path.join(out,stem+s)))&&fs.existsSync(path.join(out,stem+'.asr-review.json'))&&read(path.join(out,stem+'.asr-review.json')).complete,'waiting-existing-narration-and-cpu-asr');
 const report=read(path.join(out,stem+'.asr-review.json'));if(report.scenes.some(s=>s.similarity<.94||!s.acousticChecks.endingHeuristicPassed))throw Error('Scene ASR/end gate failed; inspect and repair affected scene only.');
 await waitUntil(()=>['comparison','delivery','shortcut'].every(n=>fs.existsSync(path.join(root,'shared/assets/meaningful-quests/playtests-v2',n+'.mp4'))&&fs.existsSync(path.join(__dirname,n+'-v2-input-log.json'))),'waiting-existing-playtest-v2');
 if(!['comparison','delivery','shortcut'].every(n=>fs.existsSync(path.join(root,'shared/assets/meaningful-quests/playtests-v2',n+'-sound.mp4')))){checkpoint('original-event-sound-export');await run(path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8',path.join(__dirname,'synthesize-game-sounds.py'),'--v2']);}
 checkpoint('full-narration-cpu-asr');await run(path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8','qwen3-tts/transcribe_reference.py',path.join(out,stem+'.wav'),'--device','cpu','--output',path.join(__dirname,'full-narration-asr.txt')]);
 for(const [stage,cmd,args] of [
  ['generate-corrected-render-and-caption-helpers',process.execPath,[path.join(__dirname,'setup-pipeline.cjs')]],
  ['measured-timeline-and-fresh-cuts',process.execPath,[path.join(__dirname,'build-video.cjs'),'prepare']],
  ['word-aligned-bilingual-captions',path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8',path.join(__dirname,'align-captions.py')]],
  ['continuous-final-audio-mix',process.execPath,[path.join(__dirname,'build-video.cjs'),'mix']],
  ['independent-explanation-final-render',process.execPath,[path.join(__dirname,'render-reel.cjs')]],
  ['clean-final-assembly',process.execPath,[path.join(__dirname,'build-video.cjs'),'assemble']],
  ['korean-captioned-final-render',process.execPath,[path.join(__dirname,'caption-video.cjs')]],
  ['full-decode-audio-and-cue-evidence',path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8',path.join(__dirname,'verify-video.py')]]
 ]){checkpoint(stage);await run(cmd,args);}
 checkpoint('rendered-pending-asr-and-all-cue-visual-review','finished',{qa:'projects/meaningful-quests/production/final-v1/qa.json'});
})().catch(e=>{console.error(e);checkpoint('technical-runner-failure','failed',{error:String(e)});process.exitCode=1;});
