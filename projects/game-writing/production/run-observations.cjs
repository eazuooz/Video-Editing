// One additional GPU synthesis job; base narration remains untouched.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawn,spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),file=path.join(__dirname,'observation-runner.json');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const base=read(path.join(__dirname,'resource-runner.json'));if(base.status!=='tts-asr-ready-for-direct-review')throw Error('Base synthesis and ASR must finish first.');
const m=read(path.join(root,'projects/game-writing/project.json')),chunks=path.join(root,m.tts.outputDir,'chunks');
const hashes=Object.fromEntries(Array.from({length:12},(_,i)=>String(i+1).padStart(2,'0')).map(id=>[id,hash(path.join(chunks,id+'-scene.wav'))]));
const old=fs.existsSync(file)?read(file):null;if(old?.status==='running')try{process.kill(old.pid,0);throw Error('An observation runner is already alive.');}catch(e){if(e.code!=='ESRCH')throw e;}
const state={pid:process.pid,startedAt:new Date().toISOString(),status:'running',stage:'resource-check',preservedBaseHashes:hashes,children:[],logs:'projects/game-writing/production/observation-runner.log'};
function save(){state.updatedAt=new Date().toISOString();fs.writeFileSync(file,JSON.stringify(state,null,2)+'\n');const qfile=path.join(root,'production/batches/sakurai-planning-game-design/queue.json'),q=read(qfile),i=q.items.find(i=>i.slug==='game-writing');i.activeExecution={...i.activeExecution,observations:state};i.stage='observation-'+state.stage;q.currentSlug='game-writing';q.updatedAt=state.updatedAt;fs.writeFileSync(qfile,JSON.stringify(q,null,2)+'\n');}
function run(args,kind){return new Promise((resolve,reject)=>{state.stage=kind;const c=spawn(path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8',...args],{cwd:root,windowsHide:true,stdio:['ignore','inherit','inherit']});const child={pid:c.pid,kind,status:'running',startedAt:new Date().toISOString()};state.children.push(child);save();c.on('error',reject);c.on('exit',code=>{Object.assign(child,{status:'finished',exitCode:code,finishedAt:new Date().toISOString()});save();code===0?resolve():reject(Error(kind+' failed '+code));});});}
(async()=>{
 const r=spawnSync('nvidia-smi',['--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],{encoding:'utf8',windowsHide:true});if(r.status!==0)throw Error(r.stderr);const [free,util]=r.stdout.trim().split(',').map(Number);state.resourceObservation={freeMiB:free,utilizationPercent:util};save();if(free<9000||util>35)throw Error('Insufficient GPU capacity; leave other user jobs untouched.');
 await run(['qwen3-tts/render_narration.py','--project','game-writing','--manifest','projects/game-writing/observations-manifest.json','--device','cuda:0'],'tts');
 for(const [id,digest]of Object.entries(hashes))if(hash(path.join(chunks,id+'-scene.wav'))!==digest)throw Error('Base narration changed during added observations: '+id);
 await run(['qwen3-tts/review_project_narration.py','--project','game-writing','--manifest','projects/game-writing/observations-manifest.json','--device','cpu'],'asr');
 state.status='finished';state.stage='awaiting-direct-added-voice-review';state.finishedAt=new Date().toISOString();save();
})().catch(e=>{state.status='failed';state.error=String(e);save();console.error(e);process.exitCode=1;});
