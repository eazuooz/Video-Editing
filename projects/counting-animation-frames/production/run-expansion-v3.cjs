// Same approved voice; single resumable CPU job while unrelated GPU training runs.
const fs=require('node:fs'),path=require('node:path'),{spawn}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),qf=path.join(root,'production/batches/private-review-expansion/queue.json'),rf=path.join(__dirname,'revision-v3.json'),log=path.join(__dirname,'revision-v3-runner.log');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8')),write=(f,v)=>fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');
const alive=pid=>{try{process.kill(pid,0);return true;}catch(e){if(e.code==='ESRCH')return false;throw e;}};
if(fs.existsSync(rf)){const previous=read(rf);if(previous.execution?.state==='running'&&alive(previous.execution.pid))throw Error('Expansion runner is alive; resume its session');}
function checkpoint(stage,state='running',extra={}){
 const q=read(qf),i=q.items.find(i=>i.slug==='counting-animation-frames');
 i.status=state==='failed'?'failed':'in-progress';i.stage=stage;i.execution={sessionId:i.execution?.sessionId,state,pid:process.pid,log:'projects/counting-animation-frames/production/revision-v3-runner.log',updatedAt:new Date().toISOString(),...extra};q.currentSlug=i.slug;q.updatedAt=i.execution.updatedAt;
 write(qf,q);write(rf,{revision:'final-v3',stage,execution:i.execution,nextAction:'Inspect actual new chunk ASR and pronunciation; only then build duration-matched expanded timeline preserving every original scene.'});
}
async function run(stage,cmd,args){checkpoint(stage);fs.appendFileSync(log,`\n[${new Date().toISOString()}] ${stage}\n`);await new Promise((resolve,reject)=>{const p=spawn(cmd,args,{cwd:root,windowsHide:true,stdio:['ignore','pipe','pipe']});checkpoint(stage,'running',{childPid:p.pid});for(const s of [p.stdout,p.stderr])s.on('data',b=>{fs.appendFileSync(log,b);process.stdout.write(b);});p.on('error',reject);p.on('exit',c=>c===0?resolve():reject(Error(stage+' exit '+c)));});}
(async()=>{
 const py=path.join(root,'qwen3-tts/.venv/Scripts/python.exe');
 const repair=process.argv.find(a=>a.startsWith('--repair-scenes='))?.split('=')[1];
 if(!process.argv.includes('--word-review-only'))await run(repair?'repair-rejected-additions-'+repair:'synthesize-only-new-commentary-same-approved-qwen-voice-on-cpu',py,['-X','utf8','qwen3-tts/render_narration.py','--project','counting-animation-frames','--manifest','projects/counting-animation-frames/production/final-v3/tts-manifest.json','--device','cpu','--batch-size','1',...(repair?['--force-scenes',repair]:[])]);
 await run('current-hash-word-timestamp-asr-all-six-additions',py,['-X','utf8','qwen3-tts/review_project_narration.py','--project','counting-animation-frames','--manifest','projects/counting-animation-frames/production/final-v3/tts-manifest.json','--device','cpu']);
 checkpoint('word-asr-complete-awaiting-direct-content-and-alignment-review','finished');
})().catch(e=>{checkpoint('failed','failed',{error:String(e)});console.error(e);process.exitCode=1;});
