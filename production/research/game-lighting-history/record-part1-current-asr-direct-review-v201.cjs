// Full expected/recognized text and every word timestamp were read directly.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const ref=p=>({path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex')});
const priorPath=b+'part1-current-asr-direct-progress-v198.json',prior=read(priorPath),ep=b+'part1-selected-actions-asr-execution-v182.json',state=read(ep);
if(state.completed.length!==74||!state.endedAt||state.exitCode!==0||prior.rows.length!==60)throw Error('Closed74-window worker and actual60-window prior review required');
const notes=[
 ['whole-mobile-console-policy','All five statements and 합니다 ending present; console-policy names, size and measured platform-cost distinction retained.'],
 ['context-mobile-console-policy','Complete five LOD statements and five console-policy statements/end. Leading 각 belongs to the preceding LOD recognition discrepancy; preserve it without changing PCM.'],
 ['whole-mobile-compiler-availability','All five compiler-availability statements/end present. Initial 자 at0–0.18 before 세이더 is absent in independent context; retain the recognizer discrepancy and human shader pronunciation review.'],
 ['context-mobile-compiler-availability','Complete console paragraph and all five compiler statements/end. No extra initial 자. Minor overlapping word boundaries are timing evidence, not repeated speech.'],
 ['whole-fortnite-comparison-before','Both prerequisite/comparison statements/end present; 앞의/앞에 particle variation remains pending.'],
 ['context-fortnite-comparison-before','All four retained original mobile-limit guide statements followed by both new prerequisites. Original2014 normalized numerically; original PCM preserved.'],
 ['whole-fortnite-mobile-test','All five action/material/diagnostic/measurement-limit statements/end present.'],
 ['context-fortnite-mobile-test','Complete two-statement prerequisite plus all five game-test statements/end.'],
 ['whole-fortnite-normal-material','All four wall/material/condition statements/end present. 벽의 recognized 벽에; independent context recognizes 벽의.'],
 ['context-fortnite-normal-material','Complete five test statements and all four material statements/end. Literal 벽의 present; 앞의/앞에 retained. Adjacent paragraph word-boundary overlap18.30/18.14 is recorded for timing.'],
 ['whole-rivalry-mobile-history','All eleven historical demonstration statements/end present once.2014 and four-game count normalized; actual scene remains a2014 engine demonstration rather than fifth game or proof of later mobile deferred. 앞의/앞에 retained.'],
 ['context-rivalry-mobile-history','Complete four Fortnite wall statements plus eleven Rivalry statements/end. No omitted/repeated clause; overlapping word boundaries28.54/28.42 and55.92/55.82 retained as timing evidence.'],
 ['whole-four-game-transfer-conclusion','All three summary statements/end present. 네 게임/네 경우 recognized 내 게임/내 경우; retain numeric context and human pronunciation pending, not an automated spoken-number approval.'],
 ['context-four-game-transfer-conclusion','Complete eleven Rivalry statements and all three transfer-conclusion statements/end. 네/내 recognition variation remains. No additional farewell; final applies-to-four-cases clause present.']
];
const added=notes.map(([label,note])=>{
 const done=state.completed.find(d=>d.label===label);if(!done)throw Error('Missing '+label);
 const binding=ref(done.result);if(binding.sha256!==done.sha256)throw Error('Changed '+label);
 const r=read(done.result);
 return {label,result:binding,directFullExpectedAndActualTextCompared:true,expectedFullTexts:r.job.sources.map(s=>({id:s.id,ko:s.ko,pcm:{path:s.path,sha256:s.sha256,sampleRange:s.sampleRange}})),actualFullText:r.text,endingWords:r.chunks.slice(-3),notes:note,recognizerExpectedPrompt:false,observedClauseCoverageAccepted:true,allSpokenWordsConfirmed:null,allWordTimestampsDirectlyCompared:true,actualPronunciationApproved:false,humanListening:'pending',endingHeuristicOnlyApproval:false};
});
const rows=[...prior.rows,...added];
if(new Set(rows.map(x=>x.label)).size!==74||rows.some(x=>!x.directFullExpectedAndActualTextCompared||!x.allWordTimestampsDirectlyCompared))throw Error('Exact74 direct reviews required');
for(const row of rows)if(ref(row.result.path).sha256!==row.result.sha256)throw Error('Changed reviewed result '+row.label);
const out=b+'part1-current-asr-direct-review-v201.json';if(fs.existsSync(path.join(root,out)))throw Error('Preserve review');
fs.writeFileSync(path.join(root,out),JSON.stringify({schemaVersion:1,reviewedAt:new Date().toISOString(),prior:ref(priorPath),currentScript:prior.currentScript,selectedTakes:prior.selectedTakes,sourceExecution:ref(ep),actualWorker:state.actualIdentity,actualExecutionEndedAt:state.endedAt,actualExecutionExitCode:0,session:94890,sessionObservedClosedExitCode:0,directlyCompared:74,wordTimestampWindowsDirectlyRead:74,all74FullTextsDirectlyCompared:true,all74WordTimestampsDirectlyRead:true,rows,onsetRepairIds:['runtime-texture-size','geometry-car-material'],affectedReplacementWindows:['whole-runtime-texture-size','context-runtime-texture-size','context-ordinary-streaming-budget','whole-geometry-car-material','context-geometry-car-material'],retainedCurrentTakes:35,phoneticReviewPending:[...prior.phoneticReviewPending,'셰이더/세이더','네/내','벽의/벽에','앞의/앞에'],recognizerDiscrepancies:[...prior.recognizerDiscrepancies,{label:'whole-mobile-compiler-availability',issue:'Initial 자0–0.18 absent in complete independent context; ASR split alone is not a spoken-extra-word finding'}],twoUnresolvedOnsetsApproved:false,wholeAndIndependentContextApproval:false,currentMixAsrApproved:false,actualPronunciationApproved:false,humanWholeListening:'pending',allFinalPixelsReviewed:false,uploaded:false,next:'Corroborate all74 exact current PCM windows, align35 retained takes; generate only the two unchanged onset repairs, then recognize only their five affected windows.'},null,2)+'\n');
console.log(JSON.stringify({fullTexts:74,wordTimestampWindows:74,workerExit:0,onsetRepairs:2,retainedTakes:35,currentMixApproved:false}));
