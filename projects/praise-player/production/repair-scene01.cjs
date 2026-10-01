// Fix the initial source/wording mismatch only after both original jobs exit.
// This does not approve final audio, render, collect, upload or commit.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawn,execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base=path.dirname(__dirname),slug='praise-player',read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
const queue=path.join(root,'production/batches/sakurai-planning-game-design/queue.json'),manifest=read(path.join(base,'project.json')),out=path.join(root,manifest.tts.outputDir),stem=manifest.tts.filenameStem;
const stateFile=path.join(__dirname,'repair-scene01.json'),log='projects/praise-player/production/repair-scene01.log',originalPids=[59976,50020,12024,43016,40300];
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const alive=pid=>{try{process.kill(pid,0);return true;}catch(e){if(e.code==='ESRCH')return false;throw e;}};
if(fs.existsSync(stateFile)){const old=read(stateFile);if(old.state==='running'&&alive(old.pid))throw Error('Existing single repair is active: '+old.pid);}
function checkpoint(stage,state='running',extra={}){
 const previous=fs.existsSync(stateFile)?read(stateFile):{},entry={sessionId:previous.sessionId,pid:process.pid,parentPid:process.ppid,stage,state,log,updatedAt:new Date().toISOString(),...extra};
 fs.writeFileSync(stateFile,JSON.stringify(entry,null,2)+'\n');const q=read(queue),i=q.items.find(v=>v.slug===slug);i.activeExecution??={};i.activeExecution.repairScene01=entry;i.stage=stage;i.updatedAt=q.updatedAt=entry.updatedAt;
 i.requiredCorrections=['Initial scene01 strike wording does not match selected footage; reject initial take. Replacement must describe the actual Win banner.', 'Inspect every current-hash scene/full ASR and final cue/cut before collection or upload.'];
 i.nextAction=state==='finished'?'Inspect all six exact current hashes and full ASR; approve a fresh narration-scene-review.json only from actual content/ending inspection, then start the single technical runner.':'Resume this one repair; do not duplicate original GPU/CPU work. Current script01 is corrected to actual match-win footage; no final render or upload yet.';
 fs.writeFileSync(queue,JSON.stringify(q,null,2)+'\n');console.log(stage,state);
}
function originalJobsActive(){const live=originalPids.filter(alive);if(!live.length)return false;
 const condition=live.map(p=>'ProcessId = '+p).join(' OR ');
 const result=execFileSync('powershell',['-NoProfile','-Command',`Get-CimInstance Win32_Process -Filter '${condition}' | Select-Object ProcessId,CommandLine | ConvertTo-Json -Depth 3`],{encoding:'utf8',windowsHide:true});
 const parsed=result.trim()?JSON.parse(result):[];return (Array.isArray(parsed)?parsed:[parsed]).some(v=>/praise-player/.test(v.CommandLine)&&/render_narration|review_project_narration|build-project-narration/.test(v.CommandLine));
}
function py(script,args){return new Promise((resolve,reject)=>{const child=spawn(path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8',script,...args],{cwd:root,windowsHide:true,stdio:['ignore','inherit','inherit']});checkpoint('scene01-repair-subprocess','running',{script,childPid:child.pid});child.on('error',reject);child.on('exit',c=>c===0?resolve():reject(Error(script+' failed '+c)));});}
(async()=>{
 checkpoint('waiting-original-synthesis-and-ASR-before-scene01-source-match-repair','running',{originalPids});const deadline=Date.now()+3*3600e3;
 while(originalJobsActive()){if(Date.now()>deadline)throw Error('Original jobs exceeded repair wait deadline');await new Promise(r=>setTimeout(r,15000));}
 const script=read(path.join(base,'script/narration.ko.json'));if(!script.scenes[0].lines[0].includes('승리 표시'))throw Error('Corrected actual Win wording is missing');
 const initial=path.join(out,'chunks/01-scene.wav'),history=path.join(__dirname,'narration-attempt-history');fs.mkdirSync(history,{recursive:true});
 fs.writeFileSync(path.join(history,'scene01-initial-source-mismatch.json'),JSON.stringify({accepted:false,reason:'Initial line claimed a strike display, but selected official footage shows Win. Preserve take; replace only this scene with independently corrected wording.',audioSha256:hash(initial),reviewedAt:new Date().toISOString()},null,2)+'\n');
 const preserved={};for(const id of ['02','03','04','05','06'])preserved[id]=hash(path.join(out,'chunks',id+'-scene.wav'));
 checkpoint('regenerating-only-scene01-for-actual-selected-footage','running',{preservedSceneHashes:preserved});
 await py('qwen3-tts/render_narration.py',['--project',slug,'--batch-size','1','--force-scenes','01']);
 for(const [id,digest]of Object.entries(preserved))if(hash(path.join(out,'chunks',id+'-scene.wav'))!==digest)throw Error('Unrelated scene changed: '+id);
 await py('qwen3-tts/build_translated_srt.py',['--project',slug,'--language','en']);
 await py('qwen3-tts/build_project_timing.py',['--project',slug]);
 await py('qwen3-tts/review_project_narration.py',['--project',slug,'--device','cpu']);
 await py('qwen3-tts/transcribe_reference.py',[path.join(out,stem+'.wav'),'--device','cpu','--output',path.join(__dirname,'full-narration-asr.txt')]);
 const report=read(path.join(out,stem+'.asr-review.json')),fails=report.scenes.filter(s=>s.similarity<.94||!s.acousticChecks.endingHeuristicPassed);
 if(!report.complete||fails.length)throw Error('Actual ASR/endings require scene-specific content review: '+fails.map(s=>s.scene+'='+s.similarity).join(', '));
 checkpoint('repaired-scene01-and-current-ASR-awaiting-direct-content-review','finished',{fullNarrationSha256:hash(path.join(out,stem+'.wav')),asr:'shared/output/narration/praise-player/qwen3-1.7b-balanced-v1/praise-player-qwen3-1.7b-balanced-v1.asr-review.json'});
})().catch(e=>{console.error(e);checkpoint('scene01-repair-failure','failed',{error:String(e)});process.exitCode=1;});
