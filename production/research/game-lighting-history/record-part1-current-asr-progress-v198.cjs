// Record only the complete texts and every word timestamp actually read.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const ref=p=>({path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex')});
const priorPath=b+'part1-current-asr-direct-progress-v195.json',prior=read(priorPath),state=read(b+'part1-selected-actions-asr-execution-v182.json');
const notes=[
 ['whole-geometry-barrier-views','All eight statements/end present. 바뀌므로/바뀜으로 and 앞의/앞에 remain phonetic review items.'],
 ['context-geometry-barrier-views','Complete road paragraph and all eight barrier statements. A non-script farewell follows at56.54–56.66, with 영상에서 and 만나요 both zero-duration56.66. Whole barrier has no farewell. Preserve this recognizer discrepancy for source-PCM corroboration; do not claim actual speech.'],
 ['whole-geometry-courtyard-data','All eight statements/end present; surface identification and shading responsibilities retained.'],
 ['context-geometry-courtyard-data','Complete retained original interpolation preface plus all eight new courtyard statements. Original fractions recognized incorrectly as1분의4 and1. Preserve original approved PCM/reviews; this context alone cannot approve mathematical pronunciation.'],
 ['whole-geometry-programmable-material','All nine statements/end present. 분기/붕기, 뒤의/뒤에 and 셰이딩/쉐이딩 retained.'],
 ['context-geometry-programmable-material','Complete original Microsoft-sample preface plus all nine material statements/end; same phonetic variants.'],
 ['whole-geometry-car-material','Both statements/end present, but 자동차 onset is recognized 가스통차. Onset remains unresolved and is selected for an unchanged-paragraph repair after worker completion.'],
 ['context-geometry-car-material','Complete programmable-material paragraph plus both car statements/end. 자동차 onset is reduced to 동차. Independent context does not resolve the onset.'],
 ['whole-mobile-texture-group','All four selection/size/policy/measurement-limit statements/end present.'],
 ['context-mobile-texture-group','Complete original tile-hardware versus forward/deferred distinction plus all four texture-group statements/end.'],
 ['whole-mobile-device-policy','All six device-profile statements/end present. 그 안의/그 안에 retained.'],
 ['context-mobile-device-policy','Complete texture-group paragraph and all six device-profile statements/end. Same particle variant.'],
 ['whole-mobile-lod-settings','All five size/detail/space/transfer/surface-result statements/end. A leading 각 is assigned0–0.08seconds; complete context has the literal onset without this extra token. 여기의/여기에 retained.'],
 ['context-mobile-lod-settings','Complete device-profile paragraph plus all five LOD statements/end; literal profile onset present.']
];
const rows=notes.map(([label,note])=>{
 const done=state.completed.find(d=>d.label===label);if(!done)throw Error('Missing '+label);
 const binding=ref(done.result);if(binding.sha256!==done.sha256)throw Error('Changed '+label);
 const r=read(done.result);
 return {label,result:binding,directFullExpectedAndActualTextCompared:true,expectedFullTexts:r.job.sources.map(s=>({id:s.id,ko:s.ko,pcm:{path:s.path,sha256:s.sha256,sampleRange:s.sampleRange}})),actualFullText:r.text,endingWords:r.chunks.slice(-3),notes:note,recognizerExpectedPrompt:false,observedClauseCoverageAccepted:true,allSpokenWordsConfirmed:null,allWordTimestampsDirectlyCompared:true,actualPronunciationApproved:false,humanListening:'pending',endingHeuristicOnlyApproval:false};
});
const all=[...prior.rows,...rows];
if(all.length!==60)throw Error('Exactly60 directly read texts required');
for(const r of all)r.allWordTimestampsDirectlyCompared=true;
const out=b+'part1-current-asr-direct-progress-v198.json';if(fs.existsSync(path.join(root,out)))throw Error('Preserve record');
fs.writeFileSync(path.join(root,out),JSON.stringify({schemaVersion:1,reviewedAt:new Date().toISOString(),prior:ref(priorPath),currentScript:prior.currentScript,selectedTakes:prior.selectedTakes,sourceExecution:b+'part1-selected-actions-asr-execution-v182.json',completedAtObservation:state.completed.length,expectedWindows:74,directlyCompared:60,wordTimestampWindowsDirectlyRead:60,rows:all,all74FullTextsDirectlyCompared:false,allWordTimestampsDirectlyCompared:false,wholeAndIndependentContextApproval:false,currentMixAsrApproved:false,allFinalPixelsReviewed:false,uploaded:false,phoneticReviewPending:[...prior.phoneticReviewPending,'분기/붕기','자동차 onset unresolved','그 안의/그 안에','original fraction recognition discrepancy'],onsetRepairIds:['runtime-texture-size','geometry-car-material'],recognizerDiscrepancies:[{label:'whole-tsr-rotation-vectors',issue:'30-second edge reverses to20seconds and repeats two clauses; complete independent contexts contain each once; source PCM corroboration required'},{label:'context-geometry-barrier-views',issue:'Non-script farewell allocated0.12seconds at end including two zero-duration words; absent in whole; source PCM corroboration required'},{label:'whole-mobile-lod-settings',issue:'Extra 각 at0–0.08 absent in complete independent context'}],next:'Read14 remaining complete texts and word times. After exact worker exit, repair only two unresolved unchanged onsets and recognize only affected whole/context windows.'},null,2)+'\n');
console.log(JSON.stringify({directFullTexts:60,wordTimestampWindows:60,actualCompleted:state.completed.length,fullApproval:false}));
