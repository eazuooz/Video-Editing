// Explicitly reviewed full texts only; no recognition, listening or mix approval.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const ref=p=>({path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex')});
const priorPath=b+'part1-current-asr-direct-progress-v191.json',prior=read(priorPath),state=read(b+'part1-selected-actions-asr-execution-v182.json');
const notes=[
 ['context-texture-stack-uv','Complete preceding texture-input and five stack clauses. 무늬/문의, 자산/자상, 여기의/여기에 retained.'],
 ['whole-texture-dependent-conversion','All four sentences, conversion direction VT to ordinary texture and ending 점을 보세요 present.'],
 ['context-texture-dependent-conversion','Complete five stack clauses and all four conversion sentences; minor stack particle difference retained.'],
 ['whole-texture-project-tile-settings','All five settings/border/storage-cost statements and 이유입니다 ending present.'],
 ['context-texture-project-tile-settings','Complete conversion paragraph and complete five settings statements.'],
 ['whole-runtime-texture-producer','All four producer/cache/cost clauses and ending present; 변위 recognized 변이. Pronunciation remains pending.'],
 ['context-runtime-texture-producer','Complete settings paragraph plus all producer clauses; 변위/변이 recurs.'],
 ['whole-runtime-texture-consumer','All six content-format/size/cost claims and ending present; 자산/자사, 앞의/앞에 retained.'],
 ['context-runtime-texture-consumer','Complete producer and consumer paragraphs; context recognizes 자산 but 변위/변이 persists.'],
 ['whole-runtime-texture-size','Four explanatory clauses and end present, but opening 이번 자산 창에서는 is shortened/recognized 가산창에서는. Explicit onset-word discrepancy unresolved; no full-word approval.'],
 ['context-runtime-texture-size','Complete consumer plus four size/address/storage clauses. Opening 가상 창에서는 instead of 이번 자산 창에서는 and 텍셀/택셀 retained. Onset discrepancy is not resolved.'],
 ['whole-ordinary-streaming-budget','All four ordinary-streaming claims and end present; 앞의/앞에 and spacing retained.'],
 ['context-ordinary-streaming-budget','Complete size/address paragraph plus complete ordinary-streaming paragraph. Same size onset discrepancy persists.'],
 ['whole-virtual-pool-policy','All five pool-policy statements and final 비교가 이어집니다 present; punctuation omitted by recognizer.'],
 ['context-virtual-pool-policy','Complete ordinary-streaming paragraph and complete five pool-policy statements.'],
 ['whole-texture-scene-return','All four return-camera/cache-condition/next-experiment statements present; 그때의 recognized 그때.']
];
const rows=notes.map(([label,note])=>{
 const done=state.completed.find(d=>d.label===label);if(!done)throw Error('Missing directly read '+label);
 const binding=ref(done.result);if(binding.sha256!==done.sha256)throw Error('Changed result '+label);
 const r=read(done.result),onset=label.includes('runtime-texture-size')||label==='context-ordinary-streaming-budget';
 return {label,result:binding,directFullExpectedAndActualTextCompared:true,expectedFullTexts:r.job.sources.map(s=>({id:s.id,ko:s.ko,pcm:{path:s.path,sha256:s.sha256,sampleRange:s.sampleRange}})),actualFullText:r.text,endingWords:r.chunks.slice(-2),notes:note,recognizerExpectedPrompt:false,observedClauseCoverageAccepted:true,allSpokenWordsConfirmed:!onset?null:false,unresolvedOnset: onset?'runtime-texture-size opening wording requires current PCM corroboration or actual listening':null,actualPronunciationApproved:false,humanListening:'pending',endingHeuristicOnlyApproval:false};
});
const out=b+'part1-current-asr-direct-progress-v193.json';if(fs.existsSync(path.join(root,out)))throw Error('Preserve record');
fs.writeFileSync(path.join(root,out),JSON.stringify({schemaVersion:1,reviewedAt:new Date().toISOString(),prior:ref(priorPath),currentScript:prior.currentScript,selectedTakes:prior.selectedTakes,sourceExecution:b+'part1-selected-actions-asr-execution-v182.json',completedAtObservation:state.completed.length,expectedWindows:74,directlyCompared:prior.rows.length+rows.length,rows:[...prior.rows,...rows],all74FullTextsDirectlyCompared:false,wholeAndIndependentContextApproval:false,currentMixAsrApproved:false,allFinalPixelsReviewed:false,uploaded:false,phoneticReviewPending:[...prior.phoneticReviewPending,'변위/변이','runtime-texture-size first words','텍셀/택셀'],next:'Read remaining full expected/actual texts and exact word timestamps. Preserve the unresolved size-paragraph onset and all current PCM.'},null,2)+'\n');
console.log(JSON.stringify({directFullTexts:prior.rows.length+rows.length,actualCompleted:state.completed.length,fullApproval:false}));
