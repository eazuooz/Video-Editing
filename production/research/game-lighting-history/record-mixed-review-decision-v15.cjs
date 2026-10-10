// Agent's explicit decision after reading all54 full expected/actual texts and word timestamps.
// The guards bind the decision to that evidence; they do not infer language approval from counts.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),prod=path.join(root,'projects/game-lighting-history-03/production');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const target=path.join(prod,'review-mixed-asr-direct-review-v15.json');
if(fs.existsSync(target))throw Error('Preserve current direct decision; inspect changed evidence explicitly');
const state=read(path.join(prod,'review-mixed-asr-execution-v15.json'));
const progressPath=path.join(prod,'review-mixed-asr-direct-progress-v15.json'),progress=read(progressPath);
const pcmPath=path.join(prod,'review-mixed-asr-pcm-corroboration-v15.json'),pcm=read(pcmPath);
const planPath=path.join(prod,'measured-native-timeline-candidate-v15.json');
if(state.status!=='complete'||state.exitCode!==0||state.results.length!==54)throw Error('Current ASR incomplete');
if(progress.directlyReadWindows!==54||progress.records.length!==54)throw Error('Direct full review incomplete');
if(hash(progressPath)!=='68b03f36174eed1bbdc188e51f28016023683f974bf62534b12e2491ae26deeb')throw Error('Different direct read evidence');
if(hash(pcmPath)!=='6cc36ce82d662a052e549815b08db77f711a2ee365bb4b2e42bb7d13a39ee9c5')throw Error('Different PCM evidence');
if(state.mixSha256!==progress.mixSha256||state.mixSha256!==pcm.mixSha256||state.planSha256!==hash(planPath)||state.planSha256!==pcm.planSha256)throw Error('Current mix/plan changed');
if(!pcm.allOriginalSamplesPartitionedOnce||!pcm.all105PlacementsSourceValuesExact||!pcm.all54RecognitionWindowsCurrentMixExact)throw Error('Current PCM provenance not verified');
const reviewed=new Map(progress.records.map(r=>[r.label,r]));
if(reviewed.size!==54)throw Error('Duplicate direct read identity');
const windows=state.results.map(r=>{
 const direct=reviewed.get(r.label),file=path.join(root,r.path),result=read(file);
 if(!direct||!direct.directFullExpectedAndActualTextRead||!direct.allWordTimestampsRead||hash(file)!==r.sha256||direct.resultSha256!==r.sha256)throw Error('Result/direct evidence mismatch');
 const corroborated=pcm.windows.find(w=>w.label===r.label);
 if(!corroborated||corroborated.resultSha256!==r.sha256||corroborated.windowSha256!==result.windowSha256)throw Error('Window PCM mismatch');
 return {label:r.label,path:r.path,sha256:r.sha256,windowSha256:result.windowSha256,expectedParagraphGroups:result.window.expectedKo.length,wordCount:result.words.length,
  fullExpectedAndActualTextDirectlyRead:true,allWordTimestampsDirectlyRead:true,currentMixSamplesVerified:true,
  structuralContentReviewed:true,humanPronunciation:'pending'};
});
const evidence=labels=>labels.map(label=>{const x=windows.find(w=>w.label===label);if(!x)throw Error('Wrong context label');return {label,path:x.path,sha256:x.sha256,windowSha256:x.windowSha256};});
const resolutions=[
 {id:'14b-chunk-edge-ending-and-replay',observed:'At149.92–149.98 whole14b emits 이, then zero-duration 시각 세계였습니다 at149.98 and returns to an earlier repeated span. The resumed text finishes the actual input-resolution/history sentence.',
  independentlyCompared:evidence(['whole-14b','context-14b','guide-07-dlss-engine-modes']),
  result:'The complete independent chapter context and complete guide contain every expected sentence once, without the extra phrase or backward replay. Their WAV values are the exact corresponding current mixed samples. Treat the whole-chunk output as recognition stitching, not an added spoken ending or duplicated PCM.',resolvedForStructuralMixReview:true},
 {id:'15a-chunk-edge-probe-repetition-and-gap',observed:'Whole15a repeats 프로브를 한 with multiple zero-duration words at89.98 and a long 한한 span; the subsequent debug-sphere guide and word-time gap are malformed.',
  independentlyCompared:evidence(['whole-15a','context-15a','guide-10-ddgi-spacing','guide-11-ddgi-city']),
  result:'The complete independent context contains the budget sentence, complete spacing guide and city guide once. Guide10 itself has all four sentences once with monotonic timestamps. Original source values are placed once; no replay was added. First-word 스프러블 in guide10 differs from correctly recognized 프로브 in context15a and both retained unmixed guide windows; retain the pronunciation uncertainty rather than claiming audible corruption.',resolvedForStructuralMixReview:true},
 {id:'17b-chunk-edge-greeting-and-replay',observed:'Whole17b emits 다음 영상에서 만나요 at89.76–89.98, with zero-duration added words at89.98 and a return to an earlier repeated span.',
  independentlyCompared:evidence(['whole-17b','context-17b','guide-20-lumen-interior-toggle','join-80-81']),
  result:'The complete independent context, full seven-sentence guide20 and complete neighboring-paragraph join instead contain 다음은 창문이 있는 실내 예제입니다 and the intended final Lumen summary once. Current PCM/window provenance is exact; no greeting or repeated source placement was added.',resolvedForStructuralMixReview:true}
];
const retainedPaths=[
 'projects/game-lighting-history-03/production/native-guides-asr-direct-progress-v1.json',
 'projects/game-lighting-history-03/production/local/voice-asr-v2/whole-14a.json',
 'projects/game-lighting-history-03/production/local/voice-asr-v2/whole-16a.json',
 'projects/game-lighting-history-03/production/local/voice-asr-v2/context-16a.json'
];
const record={reviewedAt:new Date().toISOString(),status:'current-mix-structure-reviewed-pair-authorized',
 mixSha256:state.mixSha256,planSha256:state.planSha256,directProgressSha256:hash(progressPath),pcmCorroborationSha256:hash(pcmPath),
 completedAsrSessionId:45804,completedAsrWorker:state.worker,completedAsrExitCode:0,pcmVerificationSessionId:91583,pcmVerificationWorker:pcm.worker,pcmVerificationExitCode:0,
 windows,all54WindowsDirectlyCompared:true,currentMixedContentApproved:true,resolvedRecognitionArtifactsDirectlyCompared:true,
 resolutions,retainedUnmixedReferences:retainedPaths.map(p=>({path:p,sha256:hash(path.join(root,p))})),
 retainedUnmixedApprovalUsedAsFinalMixApproval:false,expectedTextUsedAsRecognizerPrompt:false,endingHeuristicUsedAsApproval:false,
 interpretation:'Direct expected/actual text, complete independent contexts and exact current PCM establish preserved sentence order and no validated added/repeated/missing complete passage. Recognition orthography is not phonetic proof. This decision permits one review pair; it does not approve final pixels, whole listening or every technical pronunciation.',
 pronunciationReviewItems:[
  '기하/기아, 점광원/전광원, 기여/기어, 보간/보관, 시연/시험·시어, 루멘/루맨·룸에는, 나나이트/나나히트 and particle variants.',
  'Formula 세계 오차 is recognized3개 오차 in whole16a, join64-65 and retained unmixed windows. The preceding world-space sentence is correctly recognized세계 in join64-65. Keep original script/diagram meaning and human technical-pronunciation review pending; do not reinterpret the formula as three errors.',
  '스트리밍 지연 is recognized지형 in complete mixed/unmixed contexts; retain the intended delay concept and pending pronunciation.',
  'guide10 first프로브 differs across complete contexts; guide20 final실내 is correctly recognized in join80-81 while recognized신뢰 in its independent guide.'
 ],
 humanWholeListening:'pending',humanPronunciation:'pending',originalNimbusLibraryListening:'pending',
 finalTimingApproved:false,bodyRatioApproved:false,allFinalPixelsReviewed:false,qaApproved:false,collected:false,uploaded:false,rightsApproved:false,
 newTts:0,asrRepeated:false,newRasterImages:0,newMedia:0,
 next:'Encode one CPU2 clean/captioned review pair from the current exact silent visual/AAC, then review every encoded cue/cut and spatial motion, both decodes/PTS/audio and collect only after final QA.'};
fs.writeFileSync(target,JSON.stringify(record,null,2)+'\n');
const cpPath=path.join(root,'production/research/game-lighting-history/checkpoint.json'),cp=read(cpPath);
cp.updatedAt=record.reviewedAt;cp.stage='episode03-current-mixed-structure-reviewed-pair-pending';
cp.episode03CurrentMixedReview={path:path.relative(root,target).replaceAll('\\','/'),sha256:hash(target),all54DirectlyCompared:true,pcmPlacements:105,recognitionWindows:54,humanWholeListening:'pending',humanPronunciation:'pending',allFinalPixelsReviewed:false,qaApproved:false};
cp.ownedJobsRunning=[];cp.next=record.next;
const temp=cpPath+'.writing-'+process.pid;fs.writeFileSync(temp,JSON.stringify(cp,null,2)+'\n');fs.renameSync(temp,cpPath);
console.log(JSON.stringify({directWindows:54,structuralArtifactsCompared:3,reviewPairAuthorized:true,finalPixelsApproved:false,humanPronunciation:'pending'}));
