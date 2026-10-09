/* Preserve the reviewed baseline and record the user's requested footage mix. */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = path.resolve(__dirname, '../../..');
const rel = p => path.relative(root, p).replaceAll('\\', '/');
const read = p => JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const save = (p,j) => {
  const dst=path.join(root,p), temp=dst+'.'+process.pid+'.writing';
  fs.mkdirSync(path.dirname(dst),{recursive:true});
  fs.writeFileSync(temp,JSON.stringify(j,null,2)+'\n'); fs.renameSync(temp,dst);
};
const base='projects/presenting-game-scores';
const dir=base+'/production/revision-balatro60-v2';
const request=dir+'/request.json';
if(fs.existsSync(path.join(root,request))) throw Error('Revision already recorded. Read its checkpoint before continuing.');
const plan=read(base+'/production/final-v1/plan.json');
const receipt=read(base+'/publishing/youtube-upload-v1.json');
const now=new Date().toISOString();
const protectedPaths=[base+'/project.json',base+'/planning/outline.md',base+'/script/narration.ko.json',base+'/script/narration.en.json',base+'/sources/game-candidates.json',base+'/production/current-voice-selection-v7.json',base+'/production/measured-timeline-candidate-v7.json',base+'/production/final-v1/plan.json',base+'/production/final-v1/final-pixel-direct-review-v1.json',base+'/production/delivery-output.json',base+'/production/latest-checkpoint.json',base+'/publishing/youtube-upload-v1.json'];
const snapshots=[];
for(const p of protectedPaths){
  const source=path.join(root,p), dst=path.join(root,dir,'baseline',p.slice(base.length+1));
  fs.mkdirSync(path.dirname(dst),{recursive:true}); fs.copyFileSync(source,dst,fs.constants.COPYFILE_EXCL);
  snapshots.push({path:p,sha256:sha(source),snapshot:rel(dst),snapshotSha256:sha(dst)});
}
const actual=plan.segments.filter(x=>x.role==='actual-existing-game');
const balatroFrames=actual.filter(x=>x.source==='balatro').reduce((n,x)=>n+x.frames,0);
const tetrisFrames=actual.filter(x=>['classic','modern'].includes(x.source)).reduce((n,x)=>n+x.frames,0);
const j={schemaVersion:1,slug:'presenting-game-scores',revision:'balatro60-tetris40-v2',requestedAt:now,
 userEvidence:'게임 점수 디자인 원래 너무 테트리스 위주로 되었는데 발라트로 6테트리스 4정도로 맞춰서 비율을 수정해서 다시 만들어줘',
 stage:'additional-Balatro-source-preflight',baseline:{videoId:receipt.videoId||receipt.actualVideoId||'oDYJlcv2Dqk',privateSaveVerified:receipt.privateSaveVerified===true,fullSettingsVerified:receipt.fullSettingsVerified===true,plan:base+'/production/final-v1/plan.json',planSha256:sha(path.join(root,base+'/production/final-v1/plan.json')),finalFrames:plan.finalFrames,actualFrames:plan.actualFrames,explanationFrames:plan.explanationFrames,balatroFrames,tetrisFrames,balatroActualShare:balatroFrames/plan.actualFrames,snapshots,preserveAllMedia:true,deleteBaselineUpload:false},
 target:{scope:'actual-game-footage-only',balatroShare:.6,tetrisShare:.4,toleranceFrames:1,bodyActualShare:.6,bodyExplanationShare:.4,excludedIntroFrames:120,excludedMembershipFrames:600,atBaselineActualFrames:{planningOnly:true,balatroFrames:Math.round(plan.actualFrames*.6),tetrisFrames:plan.actualFrames-Math.round(plan.actualFrames*.6)}},
 preserve:{explanationClaims:true,explanationDuration:true,approvedUnchangedPcm:true,black25D:true,captionCenterPx:[960,970],captionStyle:'boxed-white-forest-v1',intro:true,membershipIdentities:true,continuousNimbus:true,originalMasterFiles:true},
 method:'Inspect additional unique normal-speed official Balatro actions, then revise only footage-dependent KO/EN commentary and transitions; preserve useful explanations and unchanged PCM. Jointly update measured timeline, mix, captions, chapters and ending. No loop, slowdown, unrelated idle or third-party recording without express reuse permission.',
 checkpoints:{additionalSources:false,currentDuplicateReview:false,revisedScript:false,voice:false,voiceAsr:false,measuredTiming:false,gameMixRatio:false,bodyRatio:false,finalMixedAsr:false,pair:false,allFinalPixels:false,qa:false,collected:false,privateSaved:false,fullSettingsVerified:false,gitDelivered:false},
 actualRevisionVideoId:null,humanListening:'pending',humanPronunciation:'pending',publicRights:'pending',heavyJobsStarted:0,researchProcessChanges:0,newImagesGitAdded:0,
 nextAction:'Secure and directly inspect enough unique Balatro score-related action before revised commentary/TTS. Read current input changes and refresh distinct review before production.'};
save(request,j);
const cp=read(base+'/production/latest-checkpoint.json');
cp.baselineBeforeBalatro60Revision={stage:cp.stage,actualVideoId:'oDYJlcv2Dqk',finalPlan:cp.finalPlan,finalPixelReview:cp.finalPixelReview,collectionVerification:cp.collectionVerification};
cp.recordedAt=now;cp.stage='user-requested-balatro60-tetris40-revision-source-preflight';cp.activeRevision=request;cp.revisionCheckpoints=j.checkpoints;cp.nextAction=j.nextAction;
cp.activePlatformJob={...cp.activePlatformJob,actualVideoId:'oDYJlcv2Dqk',status:'baseline-private-preserved-during-authorized-revision',workerExpectedRunning:false};
save(base+'/production/latest-checkpoint.json',cp);
const project=read(base+'/project.json');project.status=cp.stage;project.currentRevision={request,target:j.target,checkpoints:j.checkpoints,baselineVideoId:'oDYJlcv2Dqk',baselineFilesPreserved:true};project.publishReady=false;project.updatedAt=now;save(base+'/project.json',project);
const qp='production/batches/sakurai-planning-game-design/queue.json', q=read(qp),item=q.items.find(x=>x.slug==='presenting-game-scores');
item.stage=cp.stage;item.activeRevision=request;item.revisionCheckpoints=j.checkpoints;item.baselineVideoId='oDYJlcv2Dqk';item.nextAction=j.nextAction;item.activePlatformJob=cp.activePlatformJob;q.currentSlug='presenting-game-scores';q.updatedAt=now;q.lastProgressAt=now;save(qp,q);
console.log(JSON.stringify({request,snapshots:snapshots.length,baseline:{balatroFrames,tetrisFrames,actualFrames:plan.actualFrames,balatroShare:balatroFrames/plan.actualFrames},planningTargets:j.target.atBaselineActualFrames,mediaRebuilt:0,gitImagesAdded:0}));
