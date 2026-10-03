// Record direct readback before changing one rejected phrase; preserve every baseline.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base='projects/motion-sickness-games/',work=base+'production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const write=(p,v)=>{fs.mkdirSync(path.dirname(path.join(root,p)),{recursive:true});fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');};
if(fs.existsSync(path.join(root,work,'repair2/request.json')))throw Error('Repair2 already prepared; do not repeat.');
const state=read(work+'repair-phrases1.json');
if(state.status!=='candidates-ready-for-direct-review'||state.children.some(c=>c.status!=='finished'||c.exitCode!==0))throw Error('Repair1 not finished.');
try{process.kill(state.pid,0);throw Error('Repair1 still alive.')}catch(e){if(e.code!=='ESRCH')throw e;}
const oldRequest=read(work+'repair1/request.json');for(const e of oldRequest.inputs)if(sha(e.path)!==e.sha256)throw Error('Repair1 reviewed input changed: '+e.path);
const check=spawnSync(process.execPath,['scripts/review-video-duplicates.cjs','motion-sickness-games','--check'],{cwd:root,encoding:'utf8',windowsHide:true});if(check.status!==0)throw Error(check.stdout+check.stderr);
const candidateDir='shared/output/narration/motion-sickness-games/qwen3-1.7b-balanced-v1-phrase-repair1/';
const report=read(candidateDir+'motion-sickness-games-phrase-repair1.asr-review.json');
const contexts=read(work+'repair1/context-review/asr.json');if(!contexts.complete)throw Error('Context ASR incomplete.');
const reasons={
 '03':'All sentences and clauses present. ASR 배경에 versus written 배경의 is the normal /e/ realization of attributive 의; the trees/spray comparison is unchanged. Context crop ends mid-sentence and is not used to rewrite the complete paragraph.',
 '04a':'All words present in full ASR, including 있죠. Independent 8.1s-to-end ASR confirms 조절값도 따로 둘 수 있죠. Ending heuristic remains false (56.67ms decay); the documented quiet-ending ASR exception supports candidate readback, not a claim of human listening or automatic acoustic approval.',
 '04b':'All three sentences and final 하세요 present. ASR spells 뜻밖의 for written 뜻밖에; /e/ vowel transcription does not change the audible prohibition on unexpectedly changing aiming/movement. No missing/repeated clause.',
 '05':'Rejected: full ASR and two independent contextual recognitions repeatedly give 반자 instead of 판자. Meaningful visible-object pronunciation remains ambiguous despite the ending heuristic passing. Replace only this paragraph.',
 '06':'Both sentences, reset/original setting and non-universal recommendation meaning, and final 먼저입니다 present; no omitted or repeated words.',
 '07':'Both sentences, nearby planks/posts and finding viewing direction, and final 단서입니다 present; no omitted or repeated words.',
 '10':'Both sentences, separated tool aiming and retained look control, and final 식입니다 present; no omitted or repeated words.'
};
const scenes=report.scenes.map(r=>{
 const wav=candidateDir+'chunks/'+r.scene+'-scene.wav',asr=candidateDir+'asr/'+r.scene+'.json';
 if(sha(wav)!==r.audio_sha256||read(asr).audio_sha256!==r.audio_sha256)throw Error('Candidate hash mismatch '+r.scene);
 const independent=contexts.results.filter(c=>c.scene===r.scene);for(const c of independent)if(c.sourceSha256!==r.audio_sha256)throw Error('Context hash mismatch');
 return {scene:r.scene,decision:r.scene==='05'?'content-readback-rejected':'content-readback-pass',audio:wav,audio_sha256:r.audio_sha256,asr,asr_sha256:sha(asr),expected:r.expected,recognized:r.recognized,acousticChecks:r.acousticChecks,
 allSentencesDirectlyCompared:true,reason:reasons[r.scene],independentContext:independent,quietEndingException:r.scene==='04a',humanListening:'pending'};
});
write(work+'repair1/direct-review.json',{status:'six-candidates-accepted-one-pronunciation-rejected',reviewedAt:new Date().toISOString(),scenes,acceptedCount:6,rejectedCount:1,contextEvidence:work+'repair1/context-review/asr.json',automaticallyApproved:false,wholeCompositeApproval:false,humanListening:'pending'});
const baselinePaths=[base+'script/narration.ko.json',base+'script/narration.en.json',work+'script-source-review.json',work+'repair1/request.json',work+'repair1/direct-review.json',work+'repair1/splice-plan.json',work+'repair1/manifest.json',base+'project.json',base+'planning/action-map.json'];
for(const p of baselinePaths){const dest=path.join(root,work,'repair2/baseline',p.slice(base.length));fs.mkdirSync(path.dirname(dest),{recursive:true});fs.copyFileSync(path.join(root,p),dest);if(sha(path.relative(root,dest))!==sha(p))throw Error('Baseline copy mismatch');}
const ko='이어지는 다른 면에서는 노즐이 기둥과 그 옆의 넓은 면을 따라 움직입니다. 먼저 자리를 잡는 구간과, 같은 방향을 바라보며 표면을 청소하는 구간을 구분해 보세요.';
const en='On another surface, the nozzle follows posts and the broad surfaces beside them. Distinguish taking a position from cleaning a surface while facing roughly the same direction.';
const scripts={ko:read(base+'script/narration.ko.json'),en:read(base+'script/narration.en.json')};
const previousKo=scripts.ko.scenes.find(s=>s.id==='05').lines[3],previousEn=scripts.en.scenes.find(s=>s.id==='05').lines[3];
for(const [lang,text] of Object.entries({ko,en})){scripts[lang].scenes.find(s=>s.id==='05').lines[3]=text;scripts[lang].status='source-matched-one-paragraph-speech-repair2-reviewed';write(base+'script/narration.'+lang+'.json',scripts[lang]);
 write(work+'repair2/patch.'+lang+'.json',{title:scripts[lang].title,status:'reviewed-one-rejected-paragraph-only',scenes:[{id:'05',title:'Repair2 scene05 paragraph4',lines:[text]}]});}
// All previous paragraphs, including the six accepted replacement candidates, are retained.
for(const lang of ['ko','en']){const prior=read(work+'repair2/baseline/script/narration.'+lang+'.json');for(const s of scripts[lang].scenes){const p=prior.scenes.find(x=>x.id===s.id);for(let n=0;n<s.lines.length;n++)if(!(s.id==='05'&&n===3)&&s.lines[n]!==p.lines[n])throw Error('Unrelated paragraph changed');}}
const manifest=read(work+'repair1/manifest.json');manifest.paths.script=work+'repair2/patch.ko.json';manifest.paths.scriptEn=work+'repair2/patch.en.json';
manifest.tts.outputDir='shared/output/narration/motion-sickness-games/qwen3-1.7b-balanced-v1-phrase-repair2';manifest.tts.filenameStem='motion-sickness-games-phrase-repair2';write(work+'repair2/manifest.json',manifest);
const gate=read(work+'script-source-review.json');gate.reviewedAt=new Date().toISOString();gate.status='source-and-content-reviewed-one-paragraph-speech-repair2';
gate.speechRepair={...gate.speechRepair,request:work+'repair2/request.json',previousRequest:work+'repair1/request.json',latestChangedParagraphs:1,acceptedPreviousCandidates:6,changedParagraphs:7,unchangedParagraphs:53,finalSpeechApproval:false};
for(const i of gate.inputs)i.sha256=sha(i.path);write(work+'script-source-review.json',gate);
const paths=[work+'repair2/manifest.json',work+'repair2/patch.ko.json',work+'repair2/patch.en.json',base+'script/narration.ko.json',base+'script/narration.en.json',base+'planning/action-map.json',work+'script-source-review.json',work+'repair1/direct-review.json',work+'repair1/splice-plan.json'];
write(work+'repair2/request.json',{status:'one-source-matched-paragraph-reviewed-awaiting-GPU',preparedAt:new Date().toISOString(),basis:work+'repair1/direct-review.json',edits:[{id:'05',scene:'05',paragraph:4,ko,en,previousKo,previousEn}],
 paragraphCount:1,acceptedRepair1Ids:['03','04a','04b','06','07','10'],unchangedOriginalParagraphs:53,originalExplanationClaimsPreserved:true,sourceActionBankUnchanged:true,autoSplice:false,humanListening:'pending',inputs:paths.map(p=>({path:p,sha256:sha(p)}))});
let runner=fs.readFileSync(path.join(root,work,'repair-phrases1.cjs'),'utf8').replaceAll('repair-phrases1','repair-phrases2').replaceAll('repair1','repair2').replaceAll('Repair1','Repair2').replaceAll('seven','one');
runner=runner.replace("i.execution.phase='initial-ASR-reviewed-targeted-repair';i.execution.partialChunkCount=12;","i.execution.phase='repair1-reviewed-single-phrase-repair2';i.execution.partialChunkCount=12;\n i.execution.status=status;i.execution.pid=state.pid;i.execution.workerPid=state.children.find(c=>c.status==='running')?.pid??null;i.execution.children=state.children;\n i.execution.runner=base+'repair-phrases2.cjs';i.execution.state=base+'repair-phrases2.json';i.execution.updatedAt=state.updatedAt;");
fs.writeFileSync(path.join(root,work,'repair-phrases2.cjs'),runner);
const q=read('production/batches/sakurai-planning-game-design/queue.json'),item=q.items.find(i=>i.slug==='motion-sickness-games');
item.execution.repair1={...item.execution.repair1,...state,alive:false,doNotRestart:true,contentReview:work+'repair1/direct-review.json',acceptedCandidates:6,rejectedCandidates:1};
item.execution.contextRepair1Asr={sessionId:84712,pid:50548,status:'finished-exit0',alive:false,evidence:work+'repair1/context-review/asr.json'};
item.execution.status='repair1-reviewed-one-rejected-candidate-awaiting-repair2';item.execution.workerPid=null;item.execution.children=state.children;item.execution.activeTasks=[];item.updatedAt=q.updatedAt=new Date().toISOString();
item.stage='six-repair-candidates-accepted-one-rejected-repair2-prepared';item.nextAction='Run one repair2 candidate only; preserve six accepted repair1 candidates and53 original paragraphs. Review current-hash ASR before mixed-source v2 composition and complete12-scene composite ASR. No final timeline/ratio/render/collection/upload/Git completion.';
write('production/batches/sakurai-planning-game-design/queue.json',q);
console.log('Repair1 directly reviewed: six retained,05 rejected. Single05 repair2 prepared; no synthesis/splice run.');
