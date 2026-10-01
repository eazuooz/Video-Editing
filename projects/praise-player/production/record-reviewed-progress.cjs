// Save observed intermediate evidence. This never approves the full narration or video.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base=path.dirname(__dirname),read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
const write=(f,v)=>fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n'),now=new Date().toISOString();
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const m=read(path.join(base,'project.json')),out=path.join(root,m.tts.outputDir),asr=read(path.join(out,m.tts.filenameStem+'.asr-review.json'));
const scenes=[];
for(const id of ['02','03','04','05','06']){
 const s=asr.scenes.find(s=>s.scene===id);if(!s)continue;
 const digest=hash(path.join(out,'chunks',id+'-scene.wav'));
 if(digest!==s.audio_sha256||!s.acousticChecks.endingHeuristicPassed)throw Error('Stale/failed reviewed chunk '+id);
 const notes=id==='02'?'All eight ideas and full final sentence inspected: equal blocks, prompt/delayed recognition, conditional next-attack interference, no universal delay claim.':id==='03'?'All eight ideas and final sentence inspected: actual block/dodge, verified result rather than key event, no missing/repeated phrase.':id==='05'?'All eight ideas and the complete final sentence match the independently authored script: intentional equal miss, equal health loss, false perfect versus real outcomes, actual partial success, separate retry clue and success/failure signals. No omitted or repeated phrase.':id==='06'?'All eight ideas and full ending inspected: identical judgments/wording, changed area/position, phone-size obstruction check, timing/strength documentation and actual accomplishment. No omitted/repeated phrase.':'All eight ideas/end inspected. Full-context ASR rendered 자체 as 4채; independent 14.40–21.60s crop recognizes 자체 테스트는 한 번의 방어에는 작은 표시를 냅니다 and the full verified-streak sentence. Possessive 의/에 is orthography. No dropped/repeated phrase.';
 if(id==='04'&&!fs.readFileSync(path.join(__dirname,'scene04-specificity-independent-asr.txt'),'utf8').includes('자체 테스트는'))throw Error('Independent phrase evidence is absent');
 scenes.push({scene:id,audioSha256:digest,result:'passed-content-and-ending',notes,independentEvidence:id==='04'?{text:'production/scene04-specificity-independent-asr.txt',cropStart:14.4,cropSeconds:7.2}:undefined});
}
write(path.join(__dirname,'partial-narration-review.json'),{status:'partial-not-full-approval',reviewedAt:now,humanListening:'pending',scenes,rejected:[{scene:'01',reason:'Initial strike wording does not match actual selected Win footage; current replacement pending. Initial ASR success does not approve this source mismatch.'}],fullAsrInspected:false});
const stateFile=path.join(__dirname,'repair-scene01.json'),repair=read(stateFile);repair.sessionId=72906;write(stateFile,repair);
const qf=path.join(root,'production/batches/sakurai-planning-game-design/queue.json'),q=read(qf),item=q.items.find(v=>v.slug==='praise-player');
item.activeExecution.repairScene01=repair;
item.activeExecution.tts.processes=item.activeExecution.tts.processes.filter(v=>[59976,50020,12024].includes(v.ProcessId));
item.activeExecution.tts.state='finished-initial-synthesis; rejected scene01 replacement running in single repair';
item.activeExecution.asr={sessionId:11797,pid:43016,workerPid:40300,state:'finished-initial-watch; refreshed current scene01/full ASR pending in single repair',log:'projects/praise-player/production/asr-v1.log'};
item.activeExecution.lookdev={sessionId:79005,state:'finished',result:'projects/praise-player/production/final-v1/lookdev-render-result.json',visualReview:'12 early/late diagram frames directly inspected; clean/readable; final cue QA still pending'};
item.activeExecution.playtestCapture={state:'finished',originalSessionId:77172,timingV2SessionId:76101,strengthV2SessionId:40124,evidence:'projects/praise-player/production/*-input-log.json',assertions:'Five actual equal-state keyboard/collision tests passed; corrected timing and strength UI recaptured and inspected'};
Object.assign(item.localProgress,{originalBilingualScript:true,freshGameSelection:true,footageAcquired:true,independentExplanations:6,lookdevVisualReview:'12 early/late moments directly inspected',originalMechanics:'All five equal-state actual-input tests pass; timing/strength corrected v2 and other v1 chosen; outcome sounds match actual logs',thumbnail:'publishing/thumbnail-v1.png; built-in image generation; large Korean headline/style checked',narrationScenesAsrReviewed:scenes.map(s=>s.scene),narrationSceneFindings:'Initial scene01 rejected for source/wording mismatch; 02/03/04/05/06 current exact hashes directly inspected. Replacement scene01 and full narration still pending.',finalRender:false,upload:false});
q.automation.checkpointPromptUpdatedAt=now;q.automation.checkpointPromptVerified='Native automation 24 updated ACTIVE/hourly with natural duplicate and praise current single TTS/ASR/repair jobs; no final approval claimed';item.updatedAt=q.updatedAt=now;write(qf,q);
console.log(JSON.stringify({partialReviewed:scenes.map(s=>s.scene),repairSession:repair.sessionId,videoComplete:false,uploaded:false}));
