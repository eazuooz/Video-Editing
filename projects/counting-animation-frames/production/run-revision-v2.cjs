const fs=require('node:fs'),path=require('node:path'),{spawn,spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),file=path.join(__dirname,'revision-v2.json'),queue=path.join(root,'production/batches/sakurai-planning-game-design/queue.json'),log=path.join(__dirname,'revision-v2-runner.log');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8')),write=(f,v)=>fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');
const old=read(file);if(old.execution?.status==='running'){try{process.kill(old.execution.pid,0);throw Error('Existing revision runner alive');}catch(e){if(e.code!=='ESRCH')throw e;}}
function checkpoint(stage,status='running',extra={}){const q=read(queue),i=q.items.find(i=>i.slug==='counting-animation-frames'),now=new Date().toISOString();Object.assign(i.revision,{status,stage,updatedAt:now,execution:{status,pid:process.pid,log:'projects/counting-animation-frames/production/revision-v2-runner.log',...extra}});q.currentSlug=i.slug;q.updatedAt=now;write(queue,q);write(file,i.revision);}
async function run(stage,cmd,args){checkpoint(stage);fs.appendFileSync(log,`\n[${new Date().toISOString()}] ${stage}\n`);await new Promise((resolve,reject)=>{const p=spawn(cmd,args,{cwd:root,windowsHide:true,env:{...process.env,COUNTING_REVISION:'final-v2'},stdio:['ignore','pipe','pipe']});checkpoint(stage,'running',{childPid:p.pid});for(const stream of [p.stdout,p.stderr])stream.on('data',b=>{fs.appendFileSync(log,b);process.stdout.write(b);});p.on('error',reject);p.on('exit',code=>code===0?resolve():reject(Error(`${stage}: exit ${code}`)));});}
(async()=>{
 if(!fs.existsSync(path.join(__dirname,'final-v2/plan.json')))throw Error('Run reviewed prepare first');
 const pcmHash=()=>{const r=spawnSync('ffmpeg',['-v','error','-i',path.join(root,'motion-canvas/src/projects/counting-animation-frames/assets/final-mix.wav'),'-f','hash','-hash','sha256','-'],{encoding:'utf8',windowsHide:true});if(r.status!==0)throw Error(r.stderr);return r.stdout.trim();};
 const beforePcm=pcmHash(),retainAsr=process.argv.includes('--retain-identical-mix-asr');
 await run('remix-original-narration-and-fresh-picture-cut-sounds',process.execPath,['projects/counting-animation-frames/production/build-video.cjs','mix']);
 const afterPcm=pcmHash(),reuseAsr=retainAsr&&beforePcm===afterPcm&&fs.existsSync(path.join(__dirname,'final-v2/spoken-body-asr.txt'));
 write(path.join(__dirname,'final-v2/mix-refresh-evidence.json'),{beforePcm,afterPcm,pcmIdentical:beforePcm===afterPcm,asrReuse:reuseAsr,reason:'Picture/source-label changes and split of muted source; mix was rebuilt from original stems. Reuse ASR only if entire decoded PCM is byte-identical.'});
 if(!process.argv.includes('--refresh-edit'))await run('render-six-independent-2.5d-scenes',process.execPath,['projects/counting-animation-frames/production/render-reel.cjs']);
 await run('assemble-interleaved-fighting-game-revision',process.execPath,['projects/counting-animation-frames/production/revise-fighting-examples.cjs','assemble']);
 await run('render-all-korean-box-captions',process.execPath,['projects/counting-animation-frames/production/caption-video.cjs']);
 await run('whole-pair-decode-audio-measurement-and-all-cue-screens',path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8','projects/counting-animation-frames/production/verify-video.py']);
 if(!reuseAsr){
  await run('actual-final-audio-full-asr',path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8','qwen3-tts/transcribe_reference.py','motion-canvas/src/projects/counting-animation-frames/assets/final-mix.wav','--device','cpu','--output','projects/counting-animation-frames/production/final-v2/full-mix-asr.txt']);
  await run('extract-complete-spoken-body-for-independent-asr','ffmpeg',['-v','error','-y','-ss','2','-t','185.6','-i','motion-canvas/src/projects/counting-animation-frames/assets/final-mix.wav','-c:a','pcm_s16le','projects/counting-animation-frames/production/final-v2/spoken-body-mix.wav']);
  await run('independent-complete-spoken-body-asr',path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8','qwen3-tts/transcribe_reference.py','projects/counting-animation-frames/production/final-v2/spoken-body-mix.wav','--device','cpu','--output','projects/counting-animation-frames/production/final-v2/spoken-body-asr.txt']);
 }
 checkpoint('rendered-awaiting-all-cue-and-full-asr-direct-review','pending-visual-review');
})().catch(e=>{checkpoint('failed','failed',{error:String(e)});console.error(e);process.exitCode=1;});
