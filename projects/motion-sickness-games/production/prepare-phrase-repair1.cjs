// Preserve source-approved v1; rephrase only seven ambiguous paragraphs.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/motion-sickness-games/',revision=base+'production/repair1/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const write=(p,v)=>{fs.mkdirSync(path.dirname(path.join(root,p)),{recursive:true});fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');};
if(fs.existsSync(path.join(root,revision,'request.json')))throw Error('Repair request already exists; reuse it.');
const reportPath='shared/output/narration/motion-sickness-games/qwen3-1.7b-balanced-v1/motion-sickness-games-qwen3-1.7b-balanced-v1.asr-review.json';
const report=read(reportPath),context=read(base+'production/uncertain-phrases-v1/asr.json');
if(!report.complete||report.sceneCount!==12||!context.complete)throw Error('Read-back evidence incomplete.');
for(const s of report.scenes){const audio=`shared/output/narration/motion-sickness-games/qwen3-1.7b-balanced-v1/chunks/${s.scene}-scene.wav`;if(hash(audio)!==s.audio_sha256)throw Error('Stale ASR '+s.scene);}
for(const r of context.results)if(hash(r.source)!==r.sourceSha256)throw Error('Stale contextual ASR.');
const reject={
 '03':'Full and contextual ASR repeatedly reads 씻는 as 싣는. No omission/repetition; avoid this ambiguous washing verb with 청소하는 before acceptance.',
 '04':'Both ASRs repeatedly read 분리할 as 불리할 and 조준과 as 조중과. These key responsibilities are not approved.',
 '05':'Full and contextual ASR repeatedly reads 표면을 씻는 as 표면을 싣는. Rephrase the one ambiguous cleaning paragraph.',
 '06':'Both ASRs read 만능 권장값 as 맞는 권장값, changing the universal-setting warning. Rephrase the final paragraph.',
 '07':'Both ASRs read 다음 방향 as 닿은 방향. Rephrase the orientation-cue paragraph without changing the observed action.',
 '10':'Both ASRs read 조준은 분리하지만 as 조준은 불리하지만; contextual also shows 조주는. Rephrase the single responsibility paragraph.',
};
const decisions=report.scenes.map(s=>({...s,decision:reject[s.scene]?'targeted-phrase-repair-required':'content-readback-pass',
 notes:reject[s.scene]||({'01':'2022 and 이천이십이 are equivalent numerical normalization; all six paragraphs present.',
 '02':'All four paragraphs and last phrase directly matched, also independently read the tail despite model timestamp warning.',
 '08':'All four paragraphs and final 해야 합니다 matched in full and independent tail read-back.',
 '09':'All six paragraphs matched, no substantive differences.',
 '11':'Independent contextual ASR explicitly reads aim mode; the full-scene A 모드 is language normalization, not an omitted word. All six paragraphs present.',
 '12':'All four paragraphs including coaching CTA matched; 의/에 is ordinary spoken particle normalization.'})[s.scene],
 allParagraphsDirectlyCompared:true,humanListening:'pending'}));
write(base+'production/voice-approval-initial.json',{status:'initial-full-and-contextual-ASR-directly-reviewed-targeted-repair-required',
 reviewedAt:new Date().toISOString(),kind:'direct content comparison; not human listening',
 fullReport:reportPath,contextReport:base+'production/uncertain-phrases-v1/asr.json',
 currentHashChecked:true,sceneCount:12,paragraphCount:60,scenes:decisions,
 finalRenderingApproved:false,humanListening:'pending'});
const archives=['project.json','script/narration.ko.json','script/narration.en.json','planning/action-map.json',
 'production/script-source-review.json','production/voice-approval-initial.json'];
for(const rel of archives){const dest=path.join(root,revision,'baseline',rel);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.copyFileSync(path.join(root,base,rel),dest);}
const ko=read(base+'script/narration.ko.json'),en=read(base+'script/narration.en.json');
const edits=[
 {id:'03',scene:'03',paragraph:4,ko:'이제 놀이기구를 청소하는 장면을 보세요. 배경의 나무보다 물줄기가 닿는 표면을 따라가면, 화면이 덜 돌아가는 동안에도 작업이 이어지는 것을 볼 수 있습니다.',en:en.scenes.find(s=>s.id==='03').lines[3]},
 {id:'04a',scene:'04',paragraph:2,ko:'걷는 느낌을 주려고 더한 상하 움직임이나 충격을 강조하는 화면 흔들림은, 목표를 바라보는 방향과 같은 역할이 아닙니다. 조절 값도 따로 둘 수 있죠.',en:'Vertical bob added to suggest walking and shake added to emphasize impact do not serve the same purpose as facing a target. Their adjustment controls can be separate too.'},
 {id:'04b',scene:'04',paragraph:4,ko:'도식에서는 시점 회전은 남기고 추가 흔들림만 낮춥니다. 실제 구현에서도 역할마다 조절을 나눠야 합니다. 한 스위치가 도구를 겨누는 동작과 이동까지 뜻밖에 바꾸지 않게 하세요.',en:'In this diagram, view rotation remains available while extra shake is reduced. In implementation, separate controls by responsibility so one switch does not unexpectedly change tool aiming or movement.'},
 {id:'05',scene:'05',paragraph:4,ko:'이어지는 다른 면에서는 노즐이 기둥과 판자를 따라 움직입니다. 먼저 자리를 잡는 구간과, 같은 방향을 바라보며 표면을 청소하는 구간을 구분해 보세요.',en:en.scenes.find(s=>s.id==='05').lines[3]},
 {id:'06',scene:'06',paragraph:4,ko:'짧은 설명과 되돌리기를 함께 제공하면, 플레이어가 차이를 확인하고 원래 값으로 돌아갈 수 있습니다. 모든 사람에게 맞는 권장값을 하나 고르기보다, 선택의 의미를 알게 하는 것이 먼저입니다.',en:'A short explanation and a reset let players inspect a difference and return to the original value. Explaining the choice comes before choosing one recommended setting for everyone.'},
 {id:'07',scene:'07',paragraph:4,ko:'다시 청소 게임의 다른 표면입니다. 구조물 아래에서 위를 보았다가 다른 면을 바라볼 때, 가까운 판자와 기둥은 시점이 돌아간 뒤 바라볼 방향을 찾는 단서입니다.',en:'Return to a different surface in the cleaning game. When looking up beneath the structure and then toward another face, nearby planks and posts help identify the viewing direction after a turn.'},
 {id:'10',scene:'10',paragraph:2,ko:'설명에는 바뀌는 것과 남는 것을 함께 적을 수 있습니다. 예를 들어 도구를 겨누는 동작을 시점 회전과 따로 다루어도, 다른 방향을 보는 조작은 계속 쓸 수 있다고 알려 주는 식입니다.',en:'Explain both what changes and what remains available. For example, treating tool aiming separately from view rotation still leaves the ability to look in another direction available.'},
];
for(const edit of edits){const k=ko.scenes.find(s=>s.id===edit.scene),e=en.scenes.find(s=>s.id===edit.scene);
 edit.previousKo=k.lines[edit.paragraph-1];edit.previousEn=e.lines[edit.paragraph-1];k.lines[edit.paragraph-1]=edit.ko;e.lines[edit.paragraph-1]=edit.en;}
ko.status=en.status='source-matched-targeted-speech-repair1-reviewed';
write(base+'script/narration.ko.json',ko);write(base+'script/narration.en.json',en);
for(const lang of ['ko','en'])write(revision+`patch.${lang}.json`,{title:(lang==='ko'?ko:en).title,
 status:'reviewed-seven-paragraph-repair-candidates-only',scenes:edits.map(e=>({id:e.id,title:`Repair ${e.scene} paragraph ${e.paragraph}`,lines:[e[lang]]}))});
const m=read(base+'project.json');m.paths.script=revision+'patch.ko.json';m.paths.scriptEn=revision+'patch.en.json';
m.tts.outputDir='shared/output/narration/motion-sickness-games/qwen3-1.7b-balanced-v1-phrase-repair1';m.tts.filenameStem='motion-sickness-games-phrase-repair1';
write(revision+'manifest.json',m);
const boundaries=read(revision+'boundaries.json');
const spans={};for(const s of boundaries.scenes){const points=s.quietPoints.map(p=>p.seconds);
 spans[s.scene]=s.scene==='04'?[[points[0],points[1],'04a'],[points[2],s.seconds,'04b']]
 :[[points[0],points[1]??s.seconds,s.scene]];}
write(revision+'splice-plan.json',{status:'proposed-only-no-candidates-applied',sourceVersion:'v1',
 sampleRate:24000,encoding:'PCM_16',newVersion:'qwen3-1.7b-balanced-v2',
 preserveAllUnaffectedPcmBytes:true,allCompositeCurrentHashAsrRequired:true,
 scenes:boundaries.scenes.map(s=>({scene:s.scene,source:s.source,sourceSha256:s.sha256,
 originalSeconds:s.seconds,replacements:spans[s.scene].map(([from,to,candidateId])=>({from,to,candidateId}))}))});
const gate=read(base+'production/script-source-review.json');
gate.status='source-and-content-reviewed-targeted-speech-repair1';gate.reviewedAt=new Date().toISOString();
gate.speechRepair={request:revision+'request.json',changedParagraphs:7,claimsPreserved:true,
 unchangedParagraphs:53,originalExplanationClaimsPreserved:true,originalSceneWavsRetained:true,
 explanationDurationMustNotShrink:true,finalSpeechApproval:false};
gate.inputs=gate.inputs.map(i=>({...i,sha256:hash(i.path)}));write(base+'production/script-source-review.json',gate);
write(revision+'request.json',{status:'reviewed-candidates-awaiting-free-GPU',preparedAt:new Date().toISOString(),
 basis:base+'production/voice-approval-initial.json',edits,sceneCount:7,paragraphCount:7,
 currentSourceActionsUnchanged:true,originalExplanationClaimsPreserved:true,
 manifest:revision+'manifest.json',splicePlan:revision+'splice-plan.json',
 inputs:[revision+'manifest.json',revision+'patch.ko.json',revision+'patch.en.json',base+'script/narration.ko.json',
  base+'script/narration.en.json',base+'planning/action-map.json',base+'production/script-source-review.json'].map(p=>({path:p,sha256:hash(p)})),
 autoSplice:false,humanListening:'pending'});
console.log('Seven paragraph candidates prepared; v1 and all baseline evidence preserved. No speech/render approval.');
