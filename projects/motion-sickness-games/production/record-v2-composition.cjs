const fs=require('fs'), path=require('path');
const root=path.resolve(__dirname,'../../..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const write=(p,v)=>fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n','utf8');
const queuePath='production/batches/sakurai-planning-game-design/queue.json';
const q=read(queuePath), item=q.items.find(x=>x.slug==='motion-sickness-games');
const now=new Date().toISOString();
const session={sessionId:60242,launcherPid:55988,workerPid:36240,device:'cpu',
 startedAt:'2026-10-03T04:00:18.400Z',finishedAt:now,exitCode:0,status:'finished-awaiting-direct-whole-scene-review',
 manifest:'projects/motion-sickness-games/production/repair2/v2.manifest.json',
 log:'projects/motion-sickness-games/production/logs/v2-composite-cpu-asr.log',
 report:'shared/output/narration/motion-sickness-games/qwen3-1.7b-balanced-v2/motion-sickness-games-qwen3-1.7b-balanced-v2.asr-review.json',
 cachedByteIdenticalScenes:['01','02','08','09','11','12'],transcribedChangedScenes:['03','04','05','06','07','10'],
 automaticallyApproved:false,humanListening:'pending',doNotRestart:true};
write('projects/motion-sickness-games/production/v2-composite-asr-session.json',session);
const e=item.execution;
e.priorTopLevelRepair2Runner={sessionId:27584,pid:27808,status:'finished',exitCode:0,doNotRestart:true};
Object.assign(e,{phase:'v2-composite-current-hash-ASR-direct-review',status:'whole-scene-ASR-finished-reviewing-terminal-insertion',
 sessionId:null,pid:null,workerPid:null,alive:false,activeTasks:[],ttsComplete:true,updatedAt:now});
e.mixedComposer.status='executed-exit0';e.mixedComposer.proof='projects/motion-sickness-games/production/repair2/v2-composite-proof.json';
e.mixedComposer.outputSeconds=584.32;e.mixedComposer.wholeSceneReviewComplete=false;
e.v2CompositeAsr=session;item.stage='v2-composite-whole-scene-speech-review';
e.nextAction='Resolve05 zero-duration ASR terminal insertion with current-hash independent contexts, review all12 scene readbacks/seams/endings, then measured footage/caption timeline. No final rendering/upload approval.';
q.updatedAt=now;write(queuePath,q);
console.log(JSON.stringify({status:e.status,session:session.sessionId,composer:'executed-exit0',seconds:584.32}));
