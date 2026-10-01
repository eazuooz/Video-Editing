// Only a directly reviewed set of CURRENT audio hashes may enter final rendering.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawn}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),slug='praise-player',base=path.dirname(__dirname),read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
const qfile=path.join(root,'production/batches/sakurai-planning-game-design/queue.json'),stateFile=path.join(__dirname,'technical-runner.json'),log='projects/praise-player/production/technical-runner.log';
const m=read(path.join(base,'project.json')),out=path.join(root,m.tts.outputDir),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const alive=pid=>{try{process.kill(pid,0);return true;}catch(e){if(e.code==='ESRCH')return false;throw e;}};
if(fs.existsSync(stateFile)){const old=read(stateFile);if(old.state==='running'&&alive(old.pid))throw Error('Existing final runner active: '+old.pid);}
function checkpoint(stage,state='running',extra={}){const previous=fs.existsSync(stateFile)?read(stateFile):{},entry={sessionId:previous.sessionId,pid:process.pid,parentPid:process.ppid,stage,state,log,updatedAt:new Date().toISOString(),...extra};fs.writeFileSync(stateFile,JSON.stringify(entry,null,2)+'\n');const q=read(qfile),i=q.items.find(x=>x.slug===slug);i.activeExecution??={};i.activeExecution.technicalRunner=entry;i.stage=stage;i.updatedAt=q.updatedAt=entry.updatedAt;i.nextAction=state==='finished'?'Inspect all final cue/cut screens, full ASR and actual technical QA; then finalize, collect four files, verify private Studio upload and selectively commit/push.':'Continue this single render runner; do not duplicate GPU synthesis or render. Final visual/human/Studio review pending.';fs.writeFileSync(qfile,JSON.stringify(q,null,2)+'\n');console.log(stage,state);}
function run(command,args){return new Promise((resolve,reject)=>{const p=spawn(command,args,{cwd:root,windowsHide:true,stdio:['ignore','inherit','inherit']});p.on('error',reject);p.on('exit',c=>c===0?resolve():reject(Error(command+' exit '+c)));});}
(async()=>{
 const report=read(path.join(out,m.tts.filenameStem+'.asr-review.json')),review=read(path.join(__dirname,'narration-scene-review.json'));
 if(!report.complete||report.scenes.length!==6)throw Error('Complete current ASR required');
 for(const scene of report.scenes){const digest=hash(path.join(out,'chunks',scene.scene+'-scene.wav'));if(digest!==scene.audio_sha256||scene.similarity<.94||!scene.acousticChecks.endingHeuristicPassed||!review.scenes.some(r=>r.scene===scene.scene&&r.audioSha256===digest&&r.result==='passed-content-and-ending'))throw Error('Unreviewed/stale/failed scene '+scene.scene);}
 if(review.fullNarrationSha256!==hash(path.join(out,m.tts.filenameStem+'.wav'))||review.fullAsrInspected!==true)throw Error('Actual full narration review must match current WAV');
 const repair=read(path.join(__dirname,'repair-scene01.json'));if(repair.state!=='finished')throw Error('Original source mismatch is unresolved');
 const q=read(qfile),item=q.items.find(v=>v.slug===slug);for(const key of ['tts','asr','repairScene01']){const task=item.activeExecution[key];if(task&&task.state==='running'&&task.pid&&alive(task.pid))throw Error('Original narration job is active');}
 for(const mode of ['timing','specificity','strength','honesty','placement']){const version=['timing','strength'].includes(mode)?'v2':'v1',evidence=read(path.join(__dirname,mode+'-'+version+'-input-log.json'));if(!evidence.assertions.startsWith('passed'))throw Error('Unverified actual inputs '+mode);if(!fs.existsSync(path.join(root,`shared/assets/${slug}/playtests-${version}/${mode}-sound.mp4`)))throw Error('Missing recorded outcome sound '+mode);}
 const python=path.join(root,'qwen3-tts/.venv/Scripts/python.exe');
 for(const [stage,command,args]of [
 ['measured-timeline-and-unique-fresh-cuts',process.execPath,[path.join(__dirname,'build-video.cjs'),'prepare']],
 ['word-aligned-KO-EN-captions',python,['-X','utf8',path.join(__dirname,'align-captions.py')]],
 ['continuous-Nimbus-and-approved-voice-mix',process.execPath,[path.join(__dirname,'build-video.cjs'),'mix']],
 ['six-independent-2.5D-final-scenes',process.execPath,[path.join(__dirname,'render-reel.cjs')]],
 ['clean-final-assembly',process.execPath,[path.join(__dirname,'build-video.cjs'),'assemble']],
 ['boxed-Korean-captioned-render',process.execPath,[path.join(__dirname,'caption-video.cjs')]],
 ['full-decode-loudness-audio-and-caption-evidence',python,['-X','utf8',path.join(__dirname,'verify-video.py')]]
 ]){checkpoint(stage);await run(command,args);}
 checkpoint('rendered-pending-all-cue-visual-review','finished',{qa:'projects/praise-player/production/final-v1/qa.json'});
})().catch(e=>{console.error(e);checkpoint('technical-runner-failure','failed',{error:String(e)});process.exitCode=1;});
