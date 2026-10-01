// Start only after direct review of current additional speech and exact shot map.
const fs=require('node:fs'),path=require('node:path'),{spawn}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v2'),rf=path.join(__dirname,'revision-v2.json'),qf=path.join(root,'production/batches/private-review-expansion/queue.json'),log=path.join(__dirname,'revision-v2-render.log');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8')),write=(f,v)=>fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');
if(fs.existsSync(rf)){const previous=read(rf);if(previous.execution?.state==='running'){try{process.kill(previous.execution.pid,0);throw Error('Existing expansion runner alive; resume it');}catch(e){if(e.code!=='ESRCH')throw e;}}}
function checkpoint(stage,state='running',extra={}){const q=read(qf),i=q.items.find(i=>i.slug==='praise-player');i.status=state==='failed'?'failed':'in-progress';i.stage=stage;i.execution={sessionId:i.execution?.sessionId,state,pid:process.pid,log:'projects/praise-player/production/revision-v2-render.log',updatedAt:new Date().toISOString(),...extra};q.currentSlug=i.slug;q.updatedAt=i.execution.updatedAt;q.nextAction='Review actual rendered cue/cut images and full audio ASR; preserve original upload, then collect and upload expanded revision privately.';write(qf,q);write(rf,{revision:'final-v2',stage,execution:i.execution,nextAction:q.nextAction});}
async function run(stage,cmd,args){checkpoint(stage);fs.appendFileSync(log,`\n[${new Date().toISOString()}] ${stage}\n`);await new Promise((resolve,reject)=>{const p=spawn(cmd,args,{cwd:root,windowsHide:true,env:{...process.env,PRAISE_REVISION:'final-v2',PRAISE_MANIFEST:'projects/praise-player/production/final-v2/project-draft.json'},stdio:['ignore','pipe','pipe']});checkpoint(stage,'running',{childPid:p.pid});for(const s of [p.stdout,p.stderr])s.on('data',b=>{fs.appendFileSync(log,b);process.stdout.write(b);});p.on('error',reject);p.on('exit',c=>c===0?resolve():reject(Error(stage+' exit '+c)));});}
(async()=>{
 const py=path.join(root,'qwen3-tts/.venv/Scripts/python.exe');
 const refresh=process.argv.includes('--picture-refresh');
 const resumePrepared=process.argv.includes('--resume-prepared');
 const resumeCaption=process.argv.includes('--resume-caption');
 if(!refresh&&!resumePrepared&&!resumeCaption){
 await run('align-only-new-ko-en-captions-to-current-word-asr',py,['-X','utf8','qwen3-tts/align_project_subtitles.py','--project','praise-player','--manifest','projects/praise-player/production/final-v2/tts-manifest.json']);
 await run('plan-preserved-originals-plus-spoken-choice-and-result-insertions',process.execPath,['projects/praise-player/production/build-expansion-v2.cjs','plan']);
 await run('prepare-all-original-frame-copies-and-fresh-normal-speed-cuts',process.execPath,['projects/praise-player/production/build-expansion-v2.cjs','prepare']);
 }else if(refresh){
 const additions=process.argv.find(a=>a.startsWith('--refresh-additions='))?.split('=')[1]||'06';
 await run('refresh-only-reviewed-action-shots',process.execPath,['projects/praise-player/production/build-expansion-v2.cjs','prepare','--only-addition='+additions]);
 }
 if(!resumeCaption){
 await run('normalize-new-2.5d-recap-frame-timescale',process.execPath,['projects/praise-player/production/render-recap-v2.cjs',...(refresh?['--normalize-only']:[])]);
 if(!refresh)await run('compose-extended-approved-voice-continuous-nimbus-and-original-lab-sounds',process.execPath,['projects/praise-player/production/build-video.cjs','mix']);
 await run('assemble-preserved-explanation-plus-added-real-gameplay',process.execPath,['projects/praise-player/production/build-expansion-v2.cjs','assemble']);
 }
 await run('burn-every-korean-cue-with-source-specific-ui-clearance',process.execPath,['projects/praise-player/production/caption-expanded-v2.cjs']);
 await run('full-decode-pair-audio-loudness-and-every-cue-cut-screen',py,['-X','utf8','projects/praise-player/production/verify-expanded-v2.py']);
 const retainedAsr=refresh&&process.argv.includes('--retain-identical-mix-asr');
 if(retainedAsr){
 const crypto=require('node:crypto'),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(path.join(work,f))).digest('hex');
 const evidence=read(path.join(work,'mix-asr-inputs.json'));
 for(const file of ['final-mix.wav','final-mix.m4a','spoken-body-mix.wav','full-mix-asr.txt','spoken-body-asr.txt'])if(evidence.sha256[file]!==hash(file))throw Error('Retained ASR input/output changed: '+file);
 write(path.join(work,'retained-mix-asr.json'),{verifiedAt:new Date().toISOString(),reason:'Picture-only title-card exclusion. Speech PCM, AAC mix, complete spoken-body PCM and both actual ASR transcripts are byte-identical.',sha256:evidence.sha256});
 }else{
 await run('actual-final-full-mix-asr',py,['-X','utf8','qwen3-tts/transcribe_reference.py','projects/praise-player/production/final-v2/final-mix.wav','--device','cpu','--output','projects/praise-player/production/final-v2/full-mix-asr.txt']);
 const plan=read(path.join(work,'plan.json'));
 await run('extract-complete-spoken-body-final-mix','ffmpeg',['-v','error','-y','-ss','2','-t',String(plan.bodySeconds),'-i','projects/praise-player/production/final-v2/final-mix.wav','-c:a','pcm_s16le','projects/praise-player/production/final-v2/spoken-body-mix.wav']);
 await run('independent-complete-body-mix-asr',py,['-X','utf8','qwen3-tts/transcribe_reference.py','projects/praise-player/production/final-v2/spoken-body-mix.wav','--device','cpu','--output','projects/praise-player/production/final-v2/spoken-body-asr.txt']);
 const crypto=require('node:crypto'),sha256={};for(const file of ['final-mix.wav','final-mix.m4a','spoken-body-mix.wav','full-mix-asr.txt','spoken-body-asr.txt'])sha256[file]=crypto.createHash('sha256').update(fs.readFileSync(path.join(work,file))).digest('hex');
 write(path.join(work,'mix-asr-inputs.json'),{completedAt:new Date().toISOString(),sha256});
 }
 checkpoint('expanded-render-awaiting-direct-all-cue-cut-and-full-asr-review','finished');
})().catch(e=>{checkpoint('failed','failed',{error:String(e)});console.error(e);process.exitCode=1;});
