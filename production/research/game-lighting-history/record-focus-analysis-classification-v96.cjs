// Preserve prepared speech; replace three quota-ineligible views with analysis.
const fs=require('node:fs'),crypto=require('node:crypto'),cp=require('node:child_process');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const ref=p=>({path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex')});
const base='projects/game-lighting-history-04/production/';
const script='projects/game-lighting-history-04/script/physical-part3-guided-actions.koen.v69.json';
const takes=base+'part3-guided-actions-tts-execution-v69.json';
const context='production/research/game-lighting-history/local/guided-context-v70/execution.json';
const model='motion-canvas/src/projects/game-lighting-history-04/spatial/focus-analysis-model-v96.tsx';
const output=base+'focus-analysis-classification-v96.json';
if(fs.existsSync(output))throw Error('Preserve existing classification evidence');
cp.execFileSync(process.execPath,['scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json','--check'],{stdio:'inherit'});
const s=read(script),t=read(takes),c=read(context),ids=['focus-later-settings','focus-observation-protocol','focus-to-frame-inspection'];
const rows=ids.map(id=>{
 const a=s.scenes.find(x=>x.id===id),b=t.results.find(x=>x.id===id);
 if(!a||!b||!b.technicalTailGatePassed||ref(b.path).sha256!==b.sha256)throw Error('Current PCM mismatch '+id);
 return {id,originalProposedRole:a.role,effectiveFinalRole:'explanation',rawSourceProposalRetainedForHistory:a.ranges,rawProposalApprovedAsActual:false,preservedTake:ref(b.path),samples:b.samples,sampleRate:b.sampleRate,pcmFrames:Math.ceil(b.samples/400),ko:a.ko,en:a.en,modelRole:id,insertAfter:a.insertAfter,wordClockApproved:false,rendered:false,movingPixelsApproved:false};
});
const boards=c.boards.filter(x=>/post-board-0[23]\.jpg$/.test(x.path)).map(x=>({...ref(x.path),directlyRead:true,localOnly:true}));
if(boards.length!==2)throw Error('Exact two native context boards required');
const out={schemaVersion:1,reviewedAt:new Date().toISOString(),status:'three-analysis-roles-prepared; not-rendered-or-voice-approved',bindings:{script:ref(script),takes:ref(takes),context:ref(context),projectedModel:ref(model)},sourceReview:{publicUrl:'https://www.youtube.com/watch?v=DFT7hFz_DpE&t=2465s',rate:1,observedPublicSeconds:[2469.407258,2483.903037,2517.547385,2555.362745],pausedAfterReview:true,boards,observations:['Repeated long views retain the selected GlobalPostProcess4/depth panel and cube arrangement.','The source also changes the camera/blur appearance and briefly opens a Play menu; this is not a demonstrated continuous parameter/action/result sequence suitable for all73 proposed actual seconds.','These three paragraphs explain an observation protocol and the next frame-inspection question, so their final primary role is original spatial analysis.'],fullContinuousMovingReviewApproved:false},rows,explainedFrames:rows.reduce((n,x)=>n+x.pcmFrames,0),explainedSeconds:rows.reduce((n,x)=>n+x.samples/x.sampleRate,0),removedActualCandidateCapacitySeconds:73,newActualCapacityApproved:0,policy:'Keep original source, raw proposals, narration text and complete PCM. Show independent black projected faces, near/reference/far roles and causal arrows timed to directly compared ASR words. A source-reference still is explanation time. No held UI, loops or artificial slowdown enter actual quota.',validation:{typescriptCurrentModelErrors:0,wholeRepositoryTypecheckPassed:false,wholeRepositoryTypecheckLimit:'Seven pre-existing foreign paper-scene calls report TS2554; no foreign files changed.'},allWholeAndIndependentAsrReviewed:false,bodyRatioApproved:false,finalTimingApproved:false,allFinalPixelsReviewed:false,collected:false,uploaded:false,newGitImages:0};
fs.writeFileSync(output,JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify({output,roles:rows.length,explanationSeconds:out.explainedSeconds,removedActualCandidateCapacitySeconds:73,rendered:false,uploaded:false}));
