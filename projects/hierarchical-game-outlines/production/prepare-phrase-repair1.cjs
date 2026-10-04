// Preserve v1 and repair only six paragraphs rejected by direct full/context review.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/hierarchical-game-outlines/',revision=base+'production/repair1/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const write=(p,v)=>{fs.mkdirSync(path.dirname(path.join(root,p)),{recursive:true});fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');};
if(fs.existsSync(path.join(root,revision+'request.json')))throw Error('Repair request already exists; reuse it.');
const reportPath='shared/output/narration/hierarchical-game-outlines/qwen3-1.7b-balanced-v1/hierarchical-game-outlines-qwen3-1.7b-balanced-v1.asr-review.json';
const contextPath=base+'production/initial-context/asr.json';
const report=read(reportPath),context=read(contextPath),runner=read(base+'production/resource-runner.json');
if(runner.status!=='tts-asr-ready-for-direct-review'||runner.children.some(c=>c.status!=='finished'||c.exitCode!==0))throw Error('Initial pipeline has not completed successfully.');
try{process.kill(runner.pid,0);throw Error('Initial runner still alive.');}catch(e){if(e.code!=='ESRCH')throw e;}
if(!report.complete||report.sceneCount!==12||!context.complete||context.results.length!==12)throw Error('Read-back evidence incomplete.');
for(const s of report.scenes)if(hash(`shared/output/narration/hierarchical-game-outlines/qwen3-1.7b-balanced-v1/chunks/${s.scene}-scene.wav`)!==s.audio_sha256)throw Error('Stale full ASR '+s.scene);
for(const r of context.results)if(hash(r.source)!==r.sourceSha256)throw Error('Stale contextual ASR.');
const notes={
 '01':'All four paragraphs and ending present. Independent whole opening reads 두 포인트 (phonetic transcription of Two Point) with no arbitrary prefix; initial 가스트 prefix is not repeated. 2026 is numerical normalization. Human hearing remains pending.',
 '02':'All four paragraphs present. Independent opening explicitly reads 아웃라인 and resolves the initial classoutline transcription. No added greeting or omitted argument.',
 '03':'Full and independent reads repeatedly show 발치 instead of 발췌 in paragraph1 and 구분 instead of 굽은 in paragraph4. Repair these two paragraphs; preserve other three. 설로 is ordinary pronunciation of 선로 and is not a separate error.',
 '04':'All four paragraphs exactly read back; independent final paragraph and 추가합니다 intact despite timestamp warning.',
 '05':'Full and independent reads show 구분 instead of 굽은 in paragraph2 and 오감해 instead of 오가며 in paragraph5. Repair only those two. Other four paragraphs and independent comparison-limit ending intact.',
 '06':'All four paragraphs and last 것입니다 intact. 기획의/기획에 shares the ordinary spoken /e/ vowel; no semantic clause lost.',
 '07':'All seven paragraphs and final explicit analogy limitation present. 옆의/옆에 and 설명의/설명에 are /e/ particle transcription differences, not missing clauses.',
 '08':'All four paragraphs present. Independent tail confirms 다시 읽어야 합니다 and full final 구조/의미 warning through 확인합니다.',
 '09':'All seven paragraphs present, including no satisfaction/connection-success inference. 새/세 is the same ordinary /se/ vowel spelling ambiguity; the visible new preview and full sentence are retained.',
 '10':'All four paragraphs and final 됩니다 present. Contains versus causation and cross-reference limitation intact.',
 '11':'Full and independent sixth paragraph repeatedly reads 말체 instead of 발췌. Repair that paragraph only. Other six and final return-to-goal ending intact; 하나의/하나에 is /e/ normalization.',
 '12':'Full and independent final paragraph repeatedly reads 구형 instead of 구현, changing the coaching link to implementation. Repair only that paragraph; preserve first three and all conclusion claims.',
};
write(base+'production/voice-approval-initial.json',{status:'full-current-hash-and-independent-contexts-directly-reviewed-six-paragraph-repair-required',reviewedAt:new Date().toISOString(),kind:'direct ASR/content comparison, not human listening',fullReport:reportPath,contextReport:contextPath,currentHashChecked:true,sceneCount:12,paragraphCount:60,scenes:report.scenes.map(s=>({...s,decision:['03','05','11','12'].includes(s.scene)?'targeted-phrase-repair-required':'content-readback-pass',notes:notes[s.scene],allParagraphsDirectlyCompared:true,humanListening:'pending'})),finalRenderingApproved:false,humanListening:'pending'});
for(const rel of ['project.json','script/narration.ko.json','script/narration.en.json','planning/action-map.json','production/script-source-review.json','production/voice-approval-initial.json']){
 const dest=path.join(root,revision,'baseline',rel);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.copyFileSync(path.join(root,base,rel),dest);
}
const ko=read(base+'script/narration.ko.json'),en=read(base+'script/narration.en.json');
const edits=[
 {id:'03a',scene:'03',paragraph:1,ko:'이제 선로를 조절하는 장면입니다. 먼저 끝부분의 미리보기가 보입니다. 이어지는 별도 장면에서는 곡선이 주변 놀이기구를 향해 길어집니다.',en:'Now watch the track being adjusted. An endpoint preview appears first. In a separate shot, the curve grows toward a neighboring attraction.'},
 {id:'03b',scene:'03',paragraph:4,ko:'다음 조절에서는 곡선 모양과 지지점의 위치가 달라집니다. 큰 기능 이름만 적으면, 실제로 무엇을 바꿀 수 있는지 설명이 빠집니다.',en:'Another adjustment changes the curve’s shape and support position. A feature name alone would leave out what the player can actually change.'},
 {id:'05a',scene:'05',paragraph:2,ko:'이어서 선로의 곡선을 여러 번 조절하는 다른 장면을 보세요. 카메라와 선택 지점이 달라질 때마다, 작은 부분을 확인하는 질문도 바뀝니다.',en:'Watch another shot of successive track-curve adjustments. As the camera and selection point change, the question being checked at the detail level changes too.'},
 {id:'05b',scene:'05',paragraph:5,ko:'하지만 카메라가 멀어졌다고 해서 세부 규칙이 없어지는 것은 아닙니다. 화면의 거리 변화처럼, 문서에서도 전체를 읽다가 세부로 내려가고, 다시 큰 항목으로 올라옵니다.',en:'The detailed rules do not disappear when the camera moves farther away. As with this change of viewpoint, we read the whole document, move down to its details, and return to the broader heading.'},
 {id:'11',scene:'11',paragraph:6,ko:'마지막으로 다른 지지점을 조절하고 전체 선로를 다시 살펴봅니다. 이 자료의 서로 다른 장면을 한 번의 성공한 플레이처럼 잇지 않고, 화면에서 확인한 동작별로 구분합니다.',en:'Finally, another support is adjusted and the track is inspected again. We separate these different shots by their visible actions, rather than joining them into one successful play session.'},
 {id:'12',scene:'12',paragraph:4,ko:'기획한 내용을 코드로 만들어 보는 연습이 필요하다면, 설명란의 프로그래밍 과외 링크를 참고해 주세요. 오늘의 목표는 더 긴 목록이 아니라, 다음에 확인할 내용을 찾을 수 있는 구조입니다.',en:'If you want practice turning a design into code, see the programming coaching link in the description. The goal is a structure that reveals what to check next, rather than a longer list.'},
];
for(const edit of edits){const k=ko.scenes.find(s=>s.id===edit.scene),e=en.scenes.find(s=>s.id===edit.scene);edit.previousKo=k.lines[edit.paragraph-1];edit.previousEn=e.lines[edit.paragraph-1];k.lines[edit.paragraph-1]=edit.ko;e.lines[edit.paragraph-1]=edit.en;}
write(base+'script/narration.ko.json',ko);write(base+'script/narration.en.json',en);
for(const lang of ['ko','en'])write(revision+`patch.${lang}.json`,{title:(lang==='ko'?ko:en).title,status:'reviewed-six-paragraph-repair-candidates-only',scenes:edits.map(e=>({id:e.id,title:`Repair ${e.scene} paragraph ${e.paragraph}`,lines:[e[lang]]}))});
const m=read(base+'project.json');m.paths.script=revision+'patch.ko.json';m.paths.scriptEn=revision+'patch.en.json';m.tts.outputDir='shared/output/narration/hierarchical-game-outlines/qwen3-1.7b-balanced-v1-phrase-repair1';m.tts.filenameStem='hierarchical-game-outlines-phrase-repair1';write(revision+'manifest.json',m);
const boundaries=read(revision+'boundaries-refined.json');const spans={};
for(const s of boundaries.scenes){const p=s.quietPoints.map(x=>x.seconds);spans[s.scene]=s.scene==='03'?[[0,p[0],'03a'],[p[1],p[2],'03b']]:s.scene==='05'?[[p[0],p[1],'05a'],[p[2],p[3],'05b']]:[[p[0],s.scene==='12'?s.seconds:p[1],s.scene]];}
write(revision+'splice-plan.json',{status:'proposed-only-no-candidates-applied',sourceVersion:'v1',sampleRate:24000,encoding:'PCM_16',newVersion:'qwen3-1.7b-balanced-v2',preserveAllUnaffectedPcmBytes:true,allCompositeCurrentHashAsrRequired:true,boundaryEvidence:revision+'boundaries-refined.json',boundaryRefinement:'03p3/p4 timestamp lags actual audio:30ms RMS scan shows prior speech through26.90s and quiet interval until27.30s. Use27.279s, not the earlier rejected26.899s proposal.',scenes:boundaries.scenes.map(s=>({scene:s.scene,source:s.source,sourceSha256:s.sha256,originalSeconds:s.seconds,replacements:spans[s.scene].map(([from,to,candidateId])=>({from,to,candidateId}))}))});
const gate=read(base+'production/script-source-review.json');gate.status='source-and-independent-content-reviewed-six-paragraph-speech-repair1';gate.reviewedAt=new Date().toISOString();gate.speechRepair={request:revision+'request.json',changedParagraphs:6,unchangedParagraphs:54,claimsPreserved:true,originalExplanationClaimsPreserved:true,originalSceneWavsRetained:true,explanationDurationMustNotShrink:true,finalSpeechApproval:false};gate.inputs=gate.inputs.map(i=>({...i,sha256:hash(i.path)}));write(base+'production/script-source-review.json',gate);
write(revision+'request.json',{status:'reviewed-candidates-awaiting-free-GPU',preparedAt:new Date().toISOString(),basis:base+'production/voice-approval-initial.json',edits,sceneCount:6,paragraphCount:6,unchangedParagraphs:54,currentSourceActionsUnchanged:true,originalExplanationClaimsPreserved:true,manifest:revision+'manifest.json',splicePlan:revision+'splice-plan.json',inputs:[revision+'manifest.json',revision+'patch.ko.json',revision+'patch.en.json',base+'script/narration.ko.json',base+'script/narration.en.json',base+'planning/action-map.json',base+'production/script-source-review.json',revision+'splice-plan.json'].map(p=>({path:p,sha256:hash(p)})),autoSplice:false,humanListening:'pending'});
console.log('Six targeted candidates prepared;54 original paragraphs and all v1 media preserved. No speech/render approval.');
