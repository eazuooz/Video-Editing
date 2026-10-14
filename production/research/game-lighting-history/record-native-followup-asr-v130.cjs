const fs=require('node:fs'),c=require('node:crypto');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const b='projects/game-lighting-history-04/production/';
const execution=b+'native-followup-asr-execution-v124.json',e=read(execution),out=b+'native-followup-asr-direct-review-v130.json';
if(fs.existsSync(out)||e.exitCode!==0||e.completed.length!==10)throw Error('Require completed ten windows; preserve earlier review');
const observations={
 'focus-scale-edit':['All four sentences retain near/far reference, Scale, historical2017 Bokeh and not a physical f-stop. 오른쪽의→오른쪽에; 보케→복회/복해 persist as recognition/phonetic ambiguity. Independent preceding original 피사계→피삭의 retained for human listening.'],
 'focus-layers-entry':['All four sentences preserve menu→diagnostic regions/legend→material distinction→focus reference/boundaries. 화면에→화면의 ambiguity; complete 확인하겠습니다 ending.'],
 'debugger-command-submit':['All four sentences and independent preceding transition preserve current yellow CPU line, separate call list, Close/Execute linkage, and CPU pause does not prove GPU completion. Earlier same transition PCM is 여기까지 in this context but 지금까지 in its own whole and independent context; retain recognizer variance.'],
 'focus-to-frame-inspection':['Whole and independent complete context now both retain 지금까지, four games, exposure/color/focus→input/output inspection. 네 게임→넷게임 spelling. Prior failed opening take remains historical and is not selected.'],
 'resource-name-limits':['All four sentences and preceding resource paragraph preserve names/size/use, radiance versus shadows, producer/reader, and not all frame dependencies verified. Critical 읽는지 now present in whole and independent context. 루멘→룸앤, 방사휘도→방사위도, preceding 언리얼→얼리얼 require human pronunciation review.']
};
const windows=e.completed.map(x=>{
 if(sha(x.result)!==x.sha256)throw Error('Result changed '+x.label);
 const r=read(x.result),id=x.label.replace(/^(whole|context)-/,'');
 return {label:x.label,result:{path:x.result,sha256:x.sha256},expectedKo:r.job.sources.map(s=>s.ko),expectedEn:r.job.sources.map(s=>s.en),actualFullText:r.text,completeTextDirectlyCompared:true,endingWordEvidence:r.chunks.slice(-4),observations:observations[id],wholeSentenceOmissionObserved:false,wholeSentenceRepetitionObserved:false,inventedGreetingObserved:false,phraseCoverageAccepted:true,humanPronunciationApproved:false};
});
const selected=b+'native-followup-selected-v126.json';
fs.writeFileSync(out,JSON.stringify({schemaVersion:1,reviewedAt:new Date().toISOString(),execution:{path:execution,sha256:sha(execution)},selected:{path:selected,sha256:sha(selected)},windows,allTenFullTextsDirectlyCompared:true,wholeAndIndependentPhraseCoverageAccepted:true,recognizerExpectedPromptUsed:false,endingHeuristicOnly:false,sourceNarrationAndExistingTakesChanged:false,humanWholeListeningApproved:false,humanPronunciationApproved:false,finalMixedAsrApproved:false,allFinalPixelsApproved:false,uploaded:false},null,2)+'\n');
console.log('Recorded direct10 full-text comparison; human listening and final mix remain pending.');
