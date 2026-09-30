const fs=require('node:fs'),path=require('node:path'),root=path.resolve(__dirname,'../../..');
const file=path.join(root,'production/batches/sakurai-planning-game-design/queue.json'),q=JSON.parse(fs.readFileSync(file,'utf8')),i=q.items.find(x=>x.slug==='meaningful-quests');
i.activeExecution.technicalRunnerSessionId=44279;i.nextAction='Existing TTS PID14656/session33377 and CPU ASR session60817 continue. Existing technical runner PID60156/session44279 will automatically render after synthesis and ASR. Do not duplicate. Inspect its saved final QA/all cue sheets/full ASR before finalize, collect, private upload, media/rebuild checks and selective commit/push.';
i.updatedAt=new Date().toISOString();q.updatedAt=i.updatedAt;fs.writeFileSync(file,JSON.stringify(q,null,2)+'\n');
