const fs=require('node:fs'),crypto=require('node:crypto');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const base='projects/game-lighting-history-04/production/';
const ep='production/research/game-lighting-history/local/episode04-upscaling-native-v13/execution.json';
const ex=read(ep);
if(ex.status!=='samples-ready'||ex.samples.length!==19||ex.boards.length!==6||ex.commands.some(x=>x.exitCode!==0))throw Error('Native batch not complete');
const findings={
 mannequin:'All four samples show the engine corridor/mannequin and original source stats above the caption zone; changed pose and camera. Original stats belong to this source, not our measurement. No convergence endpoint or isolated TSR benefit certified.',
 fan:'Local0 and29.94 show normal rust-coloured blades.10.92 shows sampling grid without yellow vector arrows;18.24 and24.60 show arrows on differently oriented blades. These are observed correct-looking rotation vectors, not proof of an induced error or measured ghost elimination.',
 city:'The six selected camera views approach and move around the curved foreground building;7.66 is visibly motion blurred,12.54 close facade,18.04 back at wider view. Reject this as the literal guide06 window-reveal demonstration and as isolated TSR evidence. Retain for later geometry context only.',
 disocclusion:'All four official-document samples show the dark foreground building edge moving left relative to the distant pale building. Additional strips of distant windows become visible. The3.31-second native GIF cycle is shorter than the18.08-second guide; use it once and classify held explanatory analysis separately, never loop or slow down.'
};
for(const x of [...ex.samples,...ex.boards])if(sha(x.path)!==x.sha256)throw Error('Native pixels changed');
const reviewPath=base+'upscaling-native-direct-review-v13.json';
if(fs.existsSync(reviewPath))throw Error('Preserve completed review');
const review={reviewedAt:new Date().toISOString(),execution:{path:ep,sha256:sha(ep),sessionId:26330,observedExitCode:0},samples:ex.samples.map(x=>({...x,directlyRead:true,finding:findings[x.source]})),boards:ex.boards.map(x=>({...x,directlyRead:true})),all19NativeSamplesDirectlyRead:true,all6BoardsDirectlyRead:true,additionalFullResolutionRead:'disocclusion-04.png',officialDocument:'https://dev.epicgames.com/documentation/unreal-engine/temporal-super-resolution-in-unreal-engine',officialPageRead:'CUA browser4/tab29: Parallax Disocclusion description identifies far-building reveal behind nearer building; Epic AA scalability and50% screen percentage are source conditions.',officialLectureAdditionalObservations:[{time:741.086994,visible:'Running mannequin in corridor and publisher subtitle about low-resolution/low-framerate motion blur; source stats not own benchmark'},{time:785.316845,visible:'Note on TSR slide; not action footage'},{time:872.333899,visible:'Rotating fan with white grid; no yellow arrows in this sample'},{time:892.196185,visible:'Another Note on TSR slide; excludes former unsafe892s endpoint'},{time:892.541083,visible:'Same slide after later pause'},{time:894.671533,visible:'Same slide after buffer/late pause; the buffered875s black image does not prove vectors'}],sourceStartOffsetVerified:false,allNativeMovingFramesReviewed:false,allFinalTrackedAnnotationsReviewed:false,rightsApproved:false,finalUseApproved:false,newGitImages:0};
fs.writeFileSync(reviewPath,JSON.stringify(review,null,2)+'\n');
const selectionPath=base+'clean-source-selection-v8.json',assemblyPath=base+'additive-unmixed-review-assembly-v2.json',captionPath=base+'local/caption-word-draft-v2.json';
const s=read(selectionPath),a=read(assemblyPath),c=read(captionPath);
const entries=a.entries.filter(x=>x.start>=195.12&&x.end<=327.84);
if(entries.length!==9||entries[0].id!=='original-18t-1'||entries.at(-1).id!=='original-18t-7')throw Error('Whole upscaling chapter required');
if(sha(s.currentAudio.path)!==s.currentAudio.sha256)throw Error('PCM changed');
const cuts=[];const origin=11664;
function add(id,from,to,kind,props){const f=Math.round(from*60),t=Math.round(to*60);cuts.push({id,from:from-194.4,to:to-194.4,fromFrame:f-origin,toFrame:t-origin,globalFromFrame:f,globalToFrame:t,frames:t-f,kind,...props});}
const prev=read(base+'first-chapter-review-build-v12.json').outputs[0];
add('preserved-original-silent-boundary',194.4,195.12,'explanation',{path:prev.path,sha256:prev.sha256,sourceStart:194.38333333333333,freezeFrameOnly:true,reason:'Original0.72s PCM silence; held frame never counts as action'});
for(const e of entries){
 if(e.id==='06-guide-tsr-reveal'){
  const src='production/research/game-lighting-history/local/episode04-tsr-process-v1/tsr-disocclusion-even-v2.mp4';
  const digest='9030acd4c9932ccf400884bfde5cdcc92752682c22ae557391f0249863ac4062';if(sha(src)!==digest)throw Error('Process source changed');
  const props={entryId:e.id,path:src,sha256:digest,source:'official-TSR-document',normalSpeed:1,sourceAudio:false,sourceStartOffsetVerified:true,label:'공식 TSR 시연 · 가려짐 해제 · 50% 입력 / Epic AA'};
  // Start with the original first image, then play one3.30s native passage.
  // Three holds belong to explicit explanation, not the actual60% quota.
  add('window-before-analysis',282.04,283.31666666666666,'explanation',{...props,sourceStart:0,freezeFrameOnly:true,annotation:'before'});
  add('window-native-one-pass',283.31666666666666,286.6166666666667,'actual-engine-action',{...props,sourceStart:0,sourceEnd:3.3,oneNativePassOnly:true,fullMovingReviewApproved:false,annotation:'native'});
  add('window-after-history-analysis',286.6166666666667,300.12,'explanation',{...props,sourceStart:3,freezeFrameOnly:true,annotation:'history-validity',reason:'Narrated held-frame analysis of foreground versus newly revealed background. No actual-time credit.'});
 }else{
  const m=s.selected.find(x=>x.id===e.id);if(!m||sha(m.media.path)!==m.media.sha256)throw Error('Model changed '+e.id);
  add(e.id,e.start,e.end,'explanation',{entryId:e.id,path:m.media.path,sha256:m.media.sha256,sourceStart:m.mediaSpanFrames[0]/60,sourceSpanFrames:m.mediaSpanFrames,sourceSampleReview:m.sourceSampleReview,verification:m.verification,shiftUpPixels:60,padRoundingAtMostOneFrame:true,completeModelMeaningRetained:true});
 }
}
for(let i=0;i<cuts.length;i++)if(cuts[i].fromFrame!==(i?cuts[i-1].toFrame:0)||cuts[i].frames<=0)throw Error('Chapter continuity');
if(cuts.at(-1).toFrame!==8006)throw Error('Final PTS count');
const ids=new Set(entries.map(x=>x.id));
const cues=c.cues.filter(x=>ids.has(x.entryId)).map(x=>({...x,from:x.from-194.4,to:x.to-194.4,firstFrame:Math.ceil((x.from-194.4)*60-1e-7),exclusiveEndFrame:Math.ceil((x.to-194.4)*60-1e-7),pixelsReviewed:false}));
if(cues.length!==29||new Set(cues.map(x=>x.entryId)).size!==9)throw Error('Whole caption wording');
const plan={preparedAt:new Date().toISOString(),scope:'Next9 whole paragraphs; chapter review only. Preserve all8 spatial models and whole PCM, use official window-reveal passage once, explain held frames honestly. Not whole-episode60:40 or final mixed delivery.',selection:{path:selectionPath,sha256:sha(selectionPath)},assembly:{path:assemblyPath,sha256:sha(assemblyPath)},captionDraft:{path:captionPath,sha256:sha(captionPath)},nativeReview:{path:reviewPath,sha256:sha(reviewPath)},audio:{...s.currentAudio,firstSample:4665600,endSample:7868160,samplesInChapter:3202560,secondsInChapter:133.44,wholePcmPreserved:true},entries,cuts,cues,totals:{frames:8006,videoSeconds:8006/60,audioSeconds:133.44,roundingSeconds:133.44-8006/60,actualFrames:198,explanationFrames:7808},captionStyle:'boxed-white-forest-v1',captionCenter:[960,970],fontSize:48,maxLines:2,sourceModelsRerendered:0,newTts:0,newGitImages:0,allFinalPixelsReviewed:false,allMovingPixelsReviewed:false,causalFlowApproved:false,finalMixedAsrApproved:false,wholeEpisodeAllocationApproved:false,collected:false,uploaded:false,humanWholeListening:'pending',next:'Compose chapter pair once with twoCPU threads; review every cue/cut/annotation before wider assembly.'};
const out=base+'upscaling-chapter-review-plan-v13.json';if(fs.existsSync(out))throw Error('Preserve planning');fs.writeFileSync(out,JSON.stringify(plan,null,2)+'\n');
console.log(JSON.stringify({out,paragraphs:9,models:8,cuts:cuts.length,cues:cues.length,frames:8006,actualFrames:198,finalApproved:false}));
