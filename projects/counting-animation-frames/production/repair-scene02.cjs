// Wait for the existing jobs, then replace only the ASR-rejected scene02.
// Preserve accepted scenes, rejected evidence, script history and all source media.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawn}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base=path.dirname(__dirname),slug='counting-animation-frames';
const read=f=>JSON.parse(fs.readFileSync(f,'utf8')),queue=path.join(root,'production/batches/sakurai-planning-game-design/queue.json');
const manifest=read(path.join(base,'project.json')),out=path.join(root,manifest.tts.outputDir),stem=manifest.tts.filenameStem;
const originalPids=[52012,61500,43328,43668];
const log='projects/counting-animation-frames/production/repair-scene02.log';
const alive=pid=>{try{process.kill(pid,0);return true;}catch(e){if(e.code==='ESRCH')return false;throw e;}};
const delay=ms=>new Promise(r=>setTimeout(r,ms));
function checkpoint(stage,extra={}){
 const previous=fs.existsSync(path.join(__dirname,'repair-scene02.json'))?read(path.join(__dirname,'repair-scene02.json')):{};
 const entry={sessionId:previous.sessionId,pid:process.pid,parentPid:process.ppid,state:'running',stage,log,updatedAt:new Date().toISOString(),...extra};
 fs.writeFileSync(path.join(__dirname,'repair-scene02.json'),JSON.stringify(entry,null,2)+'\n');
 const q=read(queue),item=q.items.find(i=>i.slug===slug);item.activeExecution??={};item.activeExecution.repairScene02=entry;item.stage=stage;item.updatedAt=entry.updatedAt;
 item.localProgress.narrationSceneFindings='Scene01 passed actual ASR. Scene02 attempts1/2 rejected: repeated word despite attempt2 clean ending. Single repair02 waits for original GPU/CPU jobs to exit, then regenerates only02; remaining scene ASR and final package pending.';
 if(stage==='waiting-original-gpu-and-cpu-jobs-before-scene02-repair')item.activeExecution.technicalRunner={...item.activeExecution.technicalRunner,state:'stopped-while-waiting-for-actual-scene02-ASR-repair',note:'Verified waiting-only PID5732 stopped; no final render had started.'};
 item.nextAction=entry.state==='failed'?'Read repair-scene02.log, inspect actual current chunk ASR/endings, and repair only the rejected scene. Never upload this failed candidate.':'Resume this single repair job, never duplicate GPU synthesis. After current-hash ASR/end gates pass, technical runner renders and stops for full ASR/every-cue visual inspection. No collection/upload/commit before final QA.';
 q.updatedAt=entry.updatedAt;fs.writeFileSync(queue,JSON.stringify(q,null,2)+'\n');console.log(stage);
}
function py(script,args){return new Promise((resolve,reject)=>{
 const child=spawn(path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8',script,...args],{cwd:root,windowsHide:true,stdio:['ignore','inherit','inherit']});
 checkpoint('scene02-repair-subprocess',{script,childPid:child.pid});child.on('error',reject);child.on('exit',c=>c===0?resolve():reject(Error(script+' failed '+c)));
});}
function preserveRejected(){
 const report=read(path.join(out,stem+'.asr-review.json')),scene=report.scenes.find(s=>s.scene==='02');
 if(!scene||scene.similarity>=.94)throw Error('Expected actual rejected scene02 evidence missing');
 const history=path.join(__dirname,'narration-attempt-history');fs.mkdirSync(history,{recursive:true});
 const evidence=path.join(history,'scene02-attempt2-asr-rejected.json');if(!fs.existsSync(evidence))fs.writeFileSync(evidence,JSON.stringify({reviewedAt:new Date().toISOString(),accepted:false,reason:'Mass repetition of 먼저; clean ending is insufficient',...scene},null,2)+'\n');
 const wav=path.join(out,'chunks/02-scene.wav'),copy=path.join(out,'chunks/02-scene-asr-rejected-attempt2.wav');
 if(!fs.existsSync(copy))fs.copyFileSync(wav,copy);
 const digest=crypto.createHash('sha256').update(fs.readFileSync(copy)).digest('hex');
 console.log('Preserved rejected scene02 WAV hash',digest);
}
(async()=>{
 preserveRejected();checkpoint('waiting-original-gpu-and-cpu-jobs-before-scene02-repair',{originalPids});
 const deadline=Date.now()+3*3600e3;while(originalPids.some(alive)){if(Date.now()>deadline)throw Error('Original jobs still active after wait deadline');await delay(15000);}
 const changes=[['먼저 몇 프레임인지 말하기 전에 기준 속도를 정하세요.','프레임 수에는 기준 속도가 필요합니다.'],['Set the reference rate before saying how many frames an action takes.','Every frame count needs a reference rate.']];
 const history=path.join(__dirname,'script-history/pre-clear-reference-rate');fs.mkdirSync(history,{recursive:true});
 for(const name of ['narration.ko.json','narration.en.json','caption-units.json']){
  const file=path.join(base,'script',name);if(!fs.existsSync(path.join(history,name)))fs.copyFileSync(file,path.join(history,name));let content=fs.readFileSync(file,'utf8');
  if(!changes.some(([from,to])=>content.includes(from)||content.includes(to)))throw Error('Expected reviewed opening missing from '+name);
  for(const [from,to]of changes)content=content.replace(from,to);fs.writeFileSync(file,content);
 }
 const author=path.join(__dirname,'author-project.cjs');let code=fs.readFileSync(author,'utf8');for(const [from,to]of changes)code=code.replace(from,to);fs.writeFileSync(author,code);
 const acceptedHashes={};for(const id of ['01','03','04','05','06']){const wav=path.join(out,'chunks',id+'-scene.wav');if(fs.existsSync(wav))acceptedHashes[id]=crypto.createHash('sha256').update(fs.readFileSync(wav)).digest('hex');}
 checkpoint('regenerating-only-scene02-approved-voice',{preservedSceneHashes:acceptedHashes});
 await py('qwen3-tts/render_narration.py',['--project',slug,'--batch-size','1','--force-scenes','02']);
 for(const [id,hash]of Object.entries(acceptedHashes)){const wav=path.join(out,'chunks',id+'-scene.wav');if(crypto.createHash('sha256').update(fs.readFileSync(wav)).digest('hex')!==hash)throw Error('Unrelated scene changed: '+id);}
 await py('qwen3-tts/build_translated_srt.py',['--project',slug,'--language','en']);
 await py('qwen3-tts/build_project_timing.py',['--project',slug]);
 await py('qwen3-tts/review_project_narration.py',['--project',slug,'--device','cpu']);
 const report=read(path.join(out,stem+'.asr-review.json')),failed=report.scenes.filter(s=>s.similarity<.94||!s.acousticChecks.endingHeuristicPassed);
 if(!report.complete||failed.length)throw Error('Actual ASR/end gate requires review: '+failed.map(s=>s.scene+'='+s.similarity).join(', '));
 checkpoint('scene02-repaired-actual-ASR-passed-starting-technical-runner',{state:'finished'});
 const runnerState=path.join(__dirname,'technical-runner.json'),old=read(runnerState);old.state='stopped-before-reviewed-scene02-repair';fs.writeFileSync(runnerState,JSON.stringify(old,null,2)+'\n');
 const runner=path.join(__dirname,'continue-production.cjs');let source=fs.readFileSync(runner,'utf8');source=source.replace("log:'projects/counting-animation-frames/production/technical-runner.log'","log:process.env.COUNTING_RUNNER_LOG||'projects/counting-animation-frames/production/technical-runner-current.log'");fs.writeFileSync(runner,source);
 const logfile=fs.openSync(path.join(__dirname,'technical-runner-repaired.log'),'a');
 const child=spawn(process.execPath,[runner],{cwd:root,windowsHide:true,env:{...process.env,COUNTING_RUNNER_LOG:'projects/counting-animation-frames/production/technical-runner-repaired.log'},stdio:['ignore',logfile,logfile]});
 console.log('Technical runner PID',child.pid);await new Promise((r,j)=>{child.on('error',j);child.on('exit',c=>c===0?r():j(Error('Technical runner failed '+c)));});fs.closeSync(logfile);
})().catch(e=>{console.error(e);checkpoint('scene02-repair-or-technical-pipeline-failed',{state:'failed',error:String(e)});process.exitCode=1;});
