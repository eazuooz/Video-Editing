const fs=require('node:fs'),path=require('node:path'),root=path.resolve(__dirname,'../../..');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8')),write=(f,v)=>fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n'),queue=path.join(root,'production/batches/sakurai-planning-game-design/queue.json'),q=read(queue),i=q.items.find(x=>x.slug==='meaningful-quests');
i.checkpoints.script=true;i.checkpoints.footage=true;i.checkpoints.scenes=true;
i.localProgress.narrationSceneFindings='01: numeral 3 vs 세 orthography only; 02: exact normalized text. 03: 건넨 vs 걷는 ambiguity; phrase-repair job will replace with 전달한 and synthesize only03 after original GPU job exits. Other scenes/full ASR pending.';
i.activeExecution.repairScene03.sessionId=93095;i.activeExecution.repairScene03.originalStoppedWaitSessionId=72977;
i.activeExecution.technicalRunnerSessionId=44279;i.nextAction='Keep existing original TTS and CPU watcher running. Keep existing phrase-repair PID/session93095 running; it waits, repairs only03, refreshes all timing/subtitles/ASR and then starts final technical render. Final ASR/visual QA, output collection, private Studio settings and selective commit/push remain required.';
i.updatedAt=new Date().toISOString();q.updatedAt=i.updatedAt;write(queue,q);
const f=path.join(__dirname,'technical-runner.json'),runner=read(f);runner.state='stopped-while-waiting-for-reviewed-scene03-phrase';runner.stoppedAt=i.updatedAt;runner.finalRenderStarted=false;write(f,runner);
