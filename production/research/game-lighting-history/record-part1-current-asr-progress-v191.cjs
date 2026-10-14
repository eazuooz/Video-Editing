// Only these already-read full results are recorded. Recognition progress is separate.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const ref=p=>({path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex')});
const state=read(b+'part1-selected-actions-asr-execution-v182.json');
const reviewed=[
 ['whole-shadow-address-view','Complete editor/diagnostic/ordinary-view statements and ending 아니죠 present; spacing only.'],
 ['context-shadow-address-view','Complete retained16-cell explanation plus new complete paragraph; sixteen represented as16 and 앞의/앞에 discrepancy retained.'],
 ['whole-shadow-wheel-surface','Corrected 대관람차 twice, all eight sentences present; 그 아래/그 아래의 particle discrepancy retained.'],
 ['context-shadow-wheel-surface','Complete original camera/object/light context and current corrected Ferris paragraph; same particle discrepancy.'],
 ['whole-shadow-wheel-change','All eight sentences and final reason present; 도식의 recognized 도시계. No detected omitted clause or added greeting in this text.'],
 ['context-shadow-wheel-change','Complete preceding current Ferris paragraph plus entire new change paragraph; 도시계 recurs, not resolved by another-context text.'],
 ['whole-shadow-resource-cache','All seven statements, storage role and final question present; 이름에/이름의 and 맡습니다/맞습니다 recognition discrepancies retained.'],
 ['context-shadow-resource-cache','Complete retained cache/invalidation/GI limitation plus new seven statements; 앞의/앞에 and 맡습니다/맞습니다 retained.'],
 ['whole-texture-streaming-input','All five statements and ending different-input claim present; 무늬/문의, 자산/자상, 셰이더/쉐이더 recognition differences retained.'],
 ['context-texture-streaming-input','Full preceding resource paragraph and full texture-input paragraph; same terminology differences recur.'],
 ['whole-texture-stack-uv','All five statements and ending not-whole-frame-cost caveat present; 여기의/여기에, segmentation around reading count retained.']
];
const rows=reviewed.map(([label,notes])=>{
 const done=state.completed.find(d=>d.label===label);if(!done)throw Error('Missing reviewed result '+label);
 const binding=ref(done.result);if(binding.sha256!==done.sha256)throw Error('Changed reviewed result '+label);
 const r=read(done.result);
 return {label,result:binding,directFullExpectedAndActualTextCompared:true,expectedFullTexts:r.job.sources.map(s=>({id:s.id,ko:s.ko,pcm:{path:s.path,sha256:s.sha256,sampleRange:s.sampleRange}})),actualFullText:r.text,endingWords:r.chunks.slice(-4),notes,recognizerExpectedPrompt:false,observedClauseCoverageAccepted:true,actualPronunciationApproved:false,humanListening:'pending',endingHeuristicOnlyApproval:false};
});
const out=b+'part1-current-asr-direct-progress-v191.json';if(fs.existsSync(path.join(root,out)))throw Error('Preserve record');
fs.writeFileSync(path.join(root,out),JSON.stringify({schemaVersion:1,reviewedAt:new Date().toISOString(),currentScript:ref('projects/game-lighting-history-04/script/physical-part1-guided-actions.koen.v175.json'),selectedTakes:ref(b+'part1-selected-current-tts-execution-v181.json'),sourceExecution:b+'part1-selected-actions-asr-execution-v182.json',completedAtObservation:state.completed.length,expectedWindows:74,directlyCompared:rows.length,rows,all74FullTextsDirectlyCompared:false,wholeAndIndependentContextApproval:false,currentMixAsrApproved:false,allFinalPixelsReviewed:false,uploaded:false,phoneticReviewPending:['도식의/도시계','맡습니다/맞습니다','무늬/문의','자산/자상','minor particles'],next:'Read remaining newly completed full expected/actual texts and ends; preserve unresolved phonetic discrepancies and compare current mixed PCM later.'},null,2)+'\n');
console.log(JSON.stringify({directFullTexts:rows.length,actualCompleted:state.completed.length,fullApproval:false}));
