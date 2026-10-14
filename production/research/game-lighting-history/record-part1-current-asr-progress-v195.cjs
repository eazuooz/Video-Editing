// Only explicitly read full expected/actual texts; no audio or rendering approval.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const ref=p=>({path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex')});
const priorPath=b+'part1-current-asr-direct-progress-v193.json',prior=read(priorPath),state=read(b+'part1-selected-actions-asr-execution-v182.json');
const notes=[
 ['context-texture-scene-return','Complete pool-policy and return-camera paragraphs, all four new statements/end. 그때의/그때 retained.'],
 ['whole-tsr-silhouette-history','All nine statements/end, including scale, silhouette, stable/moving comparison and hidden renderer qualification. 사이의/사이 and 그자리의/그자리에 retained.'],
 ['context-tsr-silhouette-history','Complete original TSR reveal paragraph and all nine silhouette/history statements; same particle variants.'],
 ['whole-tsr-rotation-vectors','All seven statements/end, but two middle statements repeat at the recognizer 30-second chunk edge. Do not interpret this as spoken repetition. Complete independent contexts have each statement once; exact timestamp/PCM corroboration remains required.'],
 ['context-tsr-rotation-vectors','Complete silhouette/history paragraph and complete seven fan/rotation statements, each once. Thin-edge 얇은/얄은 and 앞의/앞에 retained.'],
 ['whole-horizon-comparison-before','All three prerequisite statements and end present; 네 종/4종 normalization.'],
 ['context-horizon-comparison-before','Complete seven fan/rotation statements once plus all three Horizon prerequisites/end. Corroborates the whole-window duplicate as a chunk-recognition discrepancy, not an approved audio conclusion.'],
 ['whole-horizon-detail-motion','Both sentences and final 경계를 보세요 present.'],
 ['context-horizon-detail-motion','Complete three prerequisites plus both action sentences/end.'],
 ['whole-outer-comparison-before','Both distinction/prerequisite sentences and final 읽어보죠 present. 자수 recognized 가수.'],
 ['context-outer-comparison-before','Complete Horizon action plus both Outer Worlds prerequisite sentences; context recognizes 자수 correctly.'],
 ['whole-outer-displayed-frames','All four display/simulation distinction statements and ending 역할입니다 present. 앞의/앞에 retained.'],
 ['context-outer-displayed-frames','Complete prerequisite and all four displayed-frame statements/end. 자수/가수 recurs in preceding take; pronunciation remains pending.'],
 ['whole-cyber-comparison-before','Both lighting/prerequisite sentences and ending 살펴보겠습니다 present.'],
 ['context-cyber-comparison-before','Complete Outer Worlds display paragraph plus both Cyberpunk prerequisites/end.'],
 ['whole-cyber-light-reconstruction','All five DLSS3.5/moving-surface/combined-condition/input-role statements/end. DLSS3.5 normalization and 앞의/앞에 retained.'],
 ['context-cyber-light-reconstruction','Complete Cyberpunk prerequisite and all five reconstruction/input statements/end.'],
 ['whole-geometry-road-mask','All four geometry visualization/road/debug-data/question statements and end present.'],
 ['context-geometry-road-mask','Complete original triangle/interpolation paragraph plus all four road/debug statements/end. Original 칠/치, 세/색, 꼭짓점/꼭지점 and 보간/보관 variants retained; no original PCM regenerated.']
];
const rows=notes.map(([label,note])=>{
 const done=state.completed.find(d=>d.label===label);if(!done)throw Error('Missing directly read '+label);
 const binding=ref(done.result);if(binding.sha256!==done.sha256)throw Error('Changed result '+label);
 const r=read(done.result);
 return {label,result:binding,directFullExpectedAndActualTextCompared:true,expectedFullTexts:r.job.sources.map(s=>({id:s.id,ko:s.ko,pcm:{path:s.path,sha256:s.sha256,sampleRange:s.sampleRange}})),actualFullText:r.text,endingWords:r.chunks.slice(-3),notes:note,recognizerExpectedPrompt:false,observedClauseCoverageAccepted:true,allSpokenWordsConfirmed:null,allWordTimestampsDirectlyCompared:false,actualPronunciationApproved:false,humanListening:'pending',endingHeuristicOnlyApproval:false};
});
const out=b+'part1-current-asr-direct-progress-v195.json';if(fs.existsSync(path.join(root,out)))throw Error('Preserve record');
fs.writeFileSync(path.join(root,out),JSON.stringify({schemaVersion:1,reviewedAt:new Date().toISOString(),prior:ref(priorPath),currentScript:prior.currentScript,selectedTakes:prior.selectedTakes,sourceExecution:b+'part1-selected-actions-asr-execution-v182.json',completedAtObservation:state.completed.length,expectedWindows:74,directlyCompared:prior.rows.length+rows.length,rows:[...prior.rows,...rows],all74FullTextsDirectlyCompared:false,allWordTimestampsDirectlyCompared:false,wholeAndIndependentContextApproval:false,currentMixAsrApproved:false,allFinalPixelsReviewed:false,uploaded:false,phoneticReviewPending:[...prior.phoneticReviewPending,'얇은/얄은','자수/가수','original triangle/interpolation lexical variants'],unresolvedRecognitionRepetition:'whole-tsr-rotation-vectors 30-second chunk boundary; both complete independent contexts contain the relevant statements once',next:'Read remaining full texts and all word times. Preserve unresolved size onset and current PCM; only a scoped repair after the current worker closes.'},null,2)+'\n');
console.log(JSON.stringify({directFullTexts:prior.rows.length+rows.length,actualCompleted:state.completed.length,fullApproval:false}));
