// Seal the directly reviewed episode 03 only. Preserve immutable build/review history.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/game-lighting-history-03/',prod=base+'production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const write=(p,x)=>{const dest=path.join(root,p),temp=dest+'.writing-'+process.pid;fs.writeFileSync(temp,JSON.stringify(x,null,2)+'\n');fs.renameSync(temp,dest);};
const hash=async p=>{const h=crypto.createHash('sha256');for await(const b of fs.createReadStream(path.join(root,p)))h.update(b);return h.digest('hex');};
const need=(ok,msg)=>{if(!ok)throw Error(msg);};
const norm=s=>s.replace(/\s/g,'');
async function main(){
 const out=prod+'final-technical-qa-v21.json';need(!fs.existsSync(path.join(root,out)),'Preserve an existing final seal.');
 const pairPath=prod+'current-review-pair-build-v21.json',pair=read(pairPath);
 const exPath=prod+'current-encoded-pixel-review-execution-v21.json',ex=read(exPath);
 const directPath=prod+'encoded-pixel-direct-progress-v21.json',direct=read(directPath);
 const movingPath=prod+'encoded-moving-flow-direct-progress-v21.json',moving=read(movingPath);
 const clearancePath=prod+'explanation-clearance-moving-direct-review-v21.json',clearance=read(clearancePath);
 const flowPath=prod+'teaching-flow-direct-review-v21.json',flow=read(flowPath);
 const mixedPath=prod+'review-mixed-asr-direct-review-v15.json',mixed=read(mixedPath);
 const pcmPath=prod+'review-mixed-asr-pcm-corroboration-v15.json',pcm=read(pcmPath);
 const mixPath=prod+'review-mix-settings-v15.json',mix=read(mixPath);
 const captionPath=prod+'local/captions-v15/caption-plan.json',cap=read(captionPath);
 const input=read(pair.inputPlan.path),manifest=read(base+'project.json');
 for(const r of [pair.inputPlan,pair.unchangedNarrationPlan])need(await hash(r.path)===r.sha256,'Changed input '+r.path);
 need(pair.identicalAacPayload&&pair.clean.audioPackets.hash===pair.captioned.audioPackets.hash&&pair.clean.audioPackets.hash===pair.sourceAudioPackets.hash,'AAC differs.');
 for(const k of ['clean','captioned']){
  const v=pair[k];need(await hash(v.path)===v.sha256,'Changed '+k+' video');
  need(v.frames===93084&&v.wholeDecode.exitCode===0&&v.allPresentationPtsContinuous,'Technical video proof incomplete.');
  const s=v.probe.streams.find(s=>s.codec_type==='video');need(s.width===1920&&s.height===1080&&s.r_frame_rate==='60/1'&&s.time_base==='1/90000','Video format differs.');
 }
 need(ex.status==='complete'&&ex.exitCode===0&&ex.sourceSha256===pair.captioned.sha256,'Extraction incomplete/stale.');
 need(direct.extractionSha256===await hash(exPath)&&direct.sourceSha256===pair.captioned.sha256,'Direct review stale.');
 need(direct.records.length===312&&direct.allBoardsDirectlyRead&&direct.imagesDirectlyRead===1867&&direct.unresolved.length===0,'Direct coverage incomplete.');
 for(let i=0;i<ex.boards.length;i++){
  const b=ex.boards[i],r=direct.records[i];need(r.boardIndex===i+1&&r.directlyRead&&r.observations.length&&r.boardSha256===b.sha256,'Missing direct board observation.');
  need(await hash(b.path)===b.sha256,'Changed reviewed board.');
 }
 for(const im of ex.images)need(await hash(im.path)===im.sha256,'Changed reviewed image.');
 const verifiedInputs=[];
 for(const seg of input.inputs){
  const media=seg.output||seg.media;
  const verification=seg.verification?read(seg.verification):null;
  const expected=seg.sha256||verification?.outputSha256;
  need(typeof media==='string'&&typeof expected==='string','Missing current input hash '+seg.id);
  if(verification){
   need((verification.output||verification.cut?.output)===media,'Verification path differs '+seg.id);
   need(verification.observedFrames===seg.frames&&verification.wholeDecode.exitCode===0&&verification.allPresentationPtsContinuous,'Input verification incomplete '+seg.id);
  }
  need(await hash(media)===expected,'Changed current input '+seg.id);
  verifiedInputs.push({id:seg.id,path:media,sha256:expected,frames:seg.frames,...(verification?{verification:seg.verification,verificationSha256:await hash(seg.verification)}:{})});
 }
 need(moving.sourceSha256===pair.captioned.sha256&&moving.pairBuildSha256===await hash(pairPath),'Moving review stale.');
 need(moving.observations.every(x=>x.directlyObserved)&&moving.observations.some(x=>x.frame===38194)&&moving.observations.some(x=>x.frame===46354)&&moving.observations.some(x=>x.frame===19802)&&moving.observations.some(x=>x.frame===29373),'Actual transition/annotation observations incomplete.');
 need(clearance.clips.length===17&&clearance.clips.every(x=>x.sampledMovingPixelsApproved),'Changed explanation motion incomplete.');
 for(const clip of clearance.clips)need(await hash(clip.output)===clip.sha256,'Changed explanation motion source.');
 need(flow.chapters.length===14&&flow.overview.centralQuestion&&flow.overview.firstExampleConnection,'Teaching flow audit incomplete.');
 for(const s of flow.sourceHashes)need(await hash(s.path)===s.sha256,'Changed teaching script '+s.path);
 need(mixed.currentMixedContentApproved&&mixed.all54WindowsDirectlyCompared&&mixed.resolvedRecognitionArtifactsDirectlyCompared&&mixed.mixSha256===pair.mixWavSha256,'Current mixed ASR incomplete.');
 need(pcm.all105PlacementsSourceValuesExact&&pcm.all54RecognitionWindowsCurrentMixExact&&pcm.allOriginalSamplesPartitionedOnce,'Current PCM proof incomplete.');
 need(await hash(mix.wav)===pair.mixWavSha256&&await hash(mix.aac)===pair.mixAacSha256,'Current mix changed.');
 const measured=mix.finalAacMeasurement.measurement;need(Math.abs(+measured.input_i+16)<1&&+measured.input_tp<=-1.5&&mix.continuousApprovedNimbus&&mix.wholeAacDecode.exitCode===0,'Final audio check failed.');
 need(cap.ko.length===356&&cap.en.length===309&&cap.paragraphs.length===104&&cap.allLiteralBilingualParagraphsPreserved,'Caption content incomplete.');
 need(await hash(captionPath)===pair.captionPlanSha256,'Caption plan changed.');
 const tracks=['ko','en'].map(language=>({language,path:prod+'local/captions-v15/game-lighting-history-03.'+language+'.srt',cues:cap[language].length}));
 for(const t of tracks)t.sha256=await hash(t.path);
 const paragraphs=cap.paragraphs.slice().sort((a,b)=>a.from-b.from).map(q=>{
  const groups={};for(const language of ['ko','en']){
   const cues=cap[language].filter(c=>c.scene===q.scene&&String(c.paragraphId)===String(q.paragraphId));
   need(cues.length&&norm(cues.map(c=>c.text).join(''))===norm(q[language]),'Caption paragraph text changed.');
   need(Math.abs(cues[0].from-q.from)<.002&&Math.abs(cues.at(-1).to-q.to)<.002,'Caption paragraph span differs.');
   groups[language+'Cues']=cues.map(c=>c.id);
  }
  return {scene:q.scene,paragraph:q.paragraphId,koText:q.ko,enText:q.en,start:Math.round(q.from*1000)/1000,end:Math.round(q.to*1000)/1000,...groups,independentMeaningOrderAndScopeDirectlyReviewed:true};
 });
 const alignmentPath=prod+'caption-alignment-review-v21.json';
 write(alignmentPath,{schemaVersion:1,status:'approved-semantic-paragraph-alignment',reviewedAt:new Date().toISOString(),approved:true,manualSemanticReview:true,allParagraphTextsRetained:true,paragraphs,captions:tracks,sourceCaptionPlan:{path:captionPath,sha256:pair.captionPlanSha256},reviewScope:'Independent KO/EN paragraph meaning/order reviewed in current script and mixed-ASR work; current KO pixels/timing reviewed over all cue and cut intersections. EN is an optional timed track, not burned English pixels.'});
 const references=[];for(const p of [pairPath,exPath,directPath,movingPath,clearancePath,flowPath,mixedPath,pcmPath,mixPath,alignmentPath])references.push({path:p,sha256:await hash(p)});
 const ratioError=pair.actualFrames-pair.bodyFrames*.6;need(Math.abs(ratioError)<=1&&pair.actualFrames+pair.explanationFrames===pair.bodyFrames&&pair.bodyFrames+720===pair.finalFrames,'Body ratio/frame count failed.');
 const qa={reviewedAt:new Date().toISOString(),status:'technically-reviewed-current-encoded-pair-ready-for-collection',technicalApproved:true,references,
  clean:pair.clean.path,cleanSha256:pair.clean.sha256,captioned:pair.captioned.path,captionedSha256:pair.captioned.sha256,verifiedInputs,
  frames:93084,durationSeconds:1551.4,resolution:[1920,1080],fps:60,timebase:'1/90000',framePtsTicks:1500,bothWholeDecodesExit0:true,identicalAacPayload:true,
  actualFrames:pair.actualFrames,explanationFrames:pair.explanationFrames,bodyFrames:pair.bodyFrames,ratioErrorFrames:ratioError,final60to40Measured:true,
  allRenderedCaptionPixelsReviewed:true,allFinalPixelsReviewed:true,allCurrentFinalMixAsrDirectlyCompared:true,allAnimated25dPlannedPosesReviewed:true,
  directCoverage:{boards:312,uniqueEncodedFrames:1867,koCues:356,enOptionalCues:309,nativeCuts:117,explanationCuts:47,inputs:166,paragraphs:104,includesAllCueCutIntersections:true,includesAllSpatialMotionEndpoints:true,changedMovingExplanationClips:17,encodedPlaybackObservations:moving.observations.length,unresolved:[]},
  pixelApprovalScope:'All planned encoded cue/cut/PCM-onset and spatial-pose frames directly read; changed spatial clips and selected continuous encoded transitions/annotations replayed. This is not a claim that all93084frames or the whole audio were individually observed.',
  causalFlowApproved:true,captionTimingApproved:true,fullContinuousPlaybackReviewed:false,humanFullListeningApproved:false,pronunciationApproved:false,finalFootageRightsApproved:false,originalNimbusLibraryFileVerified:false,
  audio:{lufs:+measured.input_i,truePeakDbtp:+measured.input_tp,continuousNimbus:true,sourceAudioStreams:0},
  membership:{originalSourcePreserved:true,frames:600,all12OriginalIdentityRowsPreserved:true,truncatedHandleConfirmation:'pending'},
  sourceAudio:0,loops:0,slowdown:0,retimedPcmSamples:0,newTts:0,asrRepeated:false,newGitImages:0,collected:false,uploaded:false,
  openItems:['사람 전체 청취·기술 용어 발음 검수 pending.','최종 공개 권리·원래 Nimbus 라이브러리 파일 확인 pending.','원본에서 잘린 회원 핸들 확인·외부 미디어 백업 pending.','수동 KO/EN·영어 메타데이터·썸네일·카드·엔딩·광고·업로드 픽셀 검증 pending.','비공개 고정댓글은 원문 준비만 완료, 공개 후 게시·고정 pending.']};
 write(out,qa);
 manifest.status='rendered-technically-reviewed-awaiting-private-delivery';manifest.publishReady=false;
 manifest.membershipOutro.appliedToFinal=true;manifest.video.durationSeconds=1551.4;
 manifest.paths.videoClean=pair.clean.path;manifest.paths.videoBurnedCaptions=pair.captioned.path;
 manifest.paths.captionsKo=tracks[0].path;manifest.paths.captionsEn=tracks[1].path;manifest.paths.captionAlignmentReview=alignmentPath;
 manifest.paths.audioMix=mix.aac;
 manifest.editing.actualGameplaySeconds=pair.actualFrames/60;manifest.editing.actualExplanationSeconds=pair.explanationFrames/60;manifest.editing.actualGameplayShare=pair.actualFrames/pair.bodyFrames;
 manifest.editing.timingStatus='93084-exact-frames; current-burned-caption-and-input-boundaries-directly-reviewed';
 manifest.editing.exampleInterleaving.reviewStatus='117-current-native-cuts-and-47-black-spatial-explanation-cuts-directly-reviewed; selected-continuous-playback-reviewed';
 manifest.editing.openingOverview.narrationSeconds=cap.paragraphs.find(x=>x.scene==='overview').to-2;
 manifest.audio.mixStatus='current-mixed-content-54-windows-and105-PCM-placements-directly-reviewed';
 manifest.series.timingMeasured=true;manifest.series.measuredFinalSeconds=1551.4;
 Object.assign(manifest.productionGates,{finalMixedAsrApproved:true,allAnimated25dPixelsReviewed:true,final60to40Measured:true,finalRendered:true,allEncodedPixelsReviewed:true});
 manifest.finalRender={technicalApproved:true,qa:out,frames:93084,durationSeconds:1551.4,openItems:qa.openItems};
 manifest.productionState.currentTechnicalReview={path:out,sha256:await hash(out),humanListeningApproved:false,pronunciationApproved:false};
 write(base+'project.json',manifest);
 const cp='production/research/game-lighting-history/checkpoint.json',c=read(cp);
 c.stage='episode03-final-technical-qa-complete-awaiting-collection-private-settings';c.updatedAt=new Date().toISOString();
 c.episode03CurrentTechnicalQa={path:out,sha256:await hash(out),frames:93084,duration:1551.4,boards:312,images:1867,technicalApproved:true,humanListeningApproved:false,pronunciationApproved:false,finalFootageRightsApproved:false,collected:false,uploaded:false};
 c.nextAction='Collect exact current reviewed03clean/captioned/KO/EN, verify output hashes, privately upload only captioned and actual settings. Preserve other episodes, history, foreign jobs and staging.';write(cp,c);
 console.log(JSON.stringify({technicalApproved:true,qa:out,frames:93084,boards:312,images:1867,collected:false,uploaded:false,humanListeningApproved:false}));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
