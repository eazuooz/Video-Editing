// CPU-only read-back of separately composed speech; no synthesis or approval.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawn}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base='projects/hierarchical-game-outlines/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const write=(p,v)=>fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');
const statePath=base+'v2-cpu-asr.json',queuePath='production/batches/sakurai-planning-game-design/queue.json';
if(fs.existsSync(path.join(root,statePath)))throw Error('An existing v2 ASR runner must be inspected instead of duplicated.');
const proof=read(base+'repair1/v2-composite-proof.json');
for(const s of proof.scenes)if(hash(s.composite)!==s.compositeSha256)throw Error('Composite hash changed: '+s.scene);
const state={pid:process.pid,status:'starting',startedAt:new Date().toISOString(),device:'cpu',
  manifest:base+'repair1/v2.manifest.json',manifestSha256:hash(base+'repair1/v2.manifest.json'),
  log:base+'logs/v2-cpu-asr.log',humanListening:'pending',automaticallyApproved:false,children:[]};
function save(){state.updatedAt=new Date().toISOString();write(statePath,state);const q=read(queuePath),item=q.items.find(i=>i.slug==='hierarchical-game-outlines');
  item.execution.status=state.status;item.execution.activeTasks=state.children.filter(c=>c.status==='running');item.execution.v2Asr={...state,state:statePath};
  item.nextAction='Directly compare all 12 current-hash v2 scene ASRs, all sentences, joins and endings; then measure source cuts/fixed captions/60:40. Human listening and final render/upload/Git remain pending.';
  item.updatedAt=state.updatedAt;q.updatedAt=state.updatedAt;write(queuePath,q);}
const fd=fs.openSync(path.join(root,state.log),'a');
const args=['qwen3-tts/review_project_narration.py','--project','hierarchical-game-outlines','--manifest',state.manifest,'--device','cpu'];
const child=spawn(path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),args,{cwd:root,windowsHide:true,stdio:['ignore',fd,fd],env:{...process.env,PYTHONIOENCODING:'utf-8'}});
const entry={pid:child.pid,kind:'v2-cpu-asr',args,status:'running',startedAt:new Date().toISOString()};state.children.push(entry);state.status='v2-cpu-asr-running';save();
console.log(JSON.stringify({runnerPid:state.pid,childPid:child.pid,state:statePath,log:state.log}));
child.on('error',err=>{entry.status='failed';entry.error=String(err);state.status='v2-cpu-asr-failed';save();process.exitCode=1;});
child.on('exit',code=>{entry.status=code===0?'finished':'failed';entry.exitCode=code;entry.finishedAt=new Date().toISOString();state.status=code===0?'v2-asr-ready-for-direct-review':'v2-cpu-asr-failed';state.finishedAt=entry.finishedAt;fs.closeSync(fd);save();console.log(state.status);process.exitCode=code||0;});
