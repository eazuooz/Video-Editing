const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'../../..'),base=path.join(__dirname,'revision-balatro60-v2');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const save=(p,j)=>{const t=p+'.'+process.pid+'.writing';fs.writeFileSync(t,JSON.stringify(j,null,2)+'\n');fs.renameSync(t,p);};
const state=read(path.join(base,'longplay-second-window-execution.json')),now=new Date().toISOString();
const job={status:state.exitCode===0?'extraction-exit0-direct-review-pending':'running',actualPid:state.actualPid,createTime:state.createTime,command:state.command,cwd:state.cwd,sessionId:'81571',cpuThreads:2,gpu:0,execution:'projects/presenting-game-scores/production/revision-balatro60-v2/longplay-second-window-execution.json',resource:'projects/presenting-game-scores/production/revision-balatro60-v2/resources-before-longplay-second-window.json',exitCode:state.exitCode,workerExpectedRunning:state.exitCode===null,processIdentityMustBeCheckedBeforeReuse:true,researchProcessChanges:0};
save(path.join(base,'longplay-second-window-session.json'),{recordedAt:now,...job});
const cpPath=path.join(__dirname,'latest-checkpoint.json'),cp=read(cpPath);cp.recordedAt=now;cp.ownedJob=job;cp.nextAction='Directly inspect the second longplay window, then candidate native action boundaries and fixed-caption framing. Description-credit exception remains pending; adoption/TTS not approved.';save(cpPath,cp);
const qp=path.join(root,'production/batches/sakurai-planning-game-design/queue.json'),q=read(qp),item=q.items.find(x=>x.slug==='presenting-game-scores');item.ownedJob=job;item.nextAction=cp.nextAction;q.updatedAt=now;q.lastProgressAt=now;save(qp,q);console.log(JSON.stringify(job));
