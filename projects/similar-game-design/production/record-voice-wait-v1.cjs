const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..');process.chdir(root);const base='projects/similar-game-design/';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,'')),write=(p,x)=>fs.writeFileSync(p,JSON.stringify(x,null,2)+'\n');
const session=read(base+'production/narration-tts-session-v1.json'),lease=read('shared/output/GPU_HANDOFF.json');
const gate=read('production/batches/sakurai-planning-game-design/preflight/similar-game-design.json');
const proof='production/batches/sakurai-planning-game-design/proof-similar-game-design/';
const now=new Date().toISOString();
const job={stage:'waiting-for-current-foreign-GPU-handoff',sessionId:session.sessionId,actualPid:33728,proxyPid:42924,
  processes:session.processes,command:session.command,log:session.log,modelLoaded:false,ttsStarted:false,cpuThreads:2,gpu:0,
  workerExpectedRunning:true,exitCode:null,foreignLease:{project:lease.project,token:lease.token,state:lease.state,coordinator:lease.coordinator},
  ownedResearchPauseCreated:false,researchResumedByThisProject:false};
const c=read(base+'production/latest-checkpoint.json');Object.assign(c,{recordedAt:now,stage:job.stage,ownedJob:job,
  motionCanvas:{independentScenes:13,source:'motion-canvas/src/projects/similar-game-design/authoring-project-v1.ts',timing:'unmeasured-lookdev-only',scopedTypeScriptPassed:true,actualAnimatedPixelsReviewed:false},
  nextAction:'Wait for the existing foreign lease without loading a model or changing its controls. The prepared voice command will take one cooperative research-boundary handoff, restore research on success/failure, and require actual resume verification. Current voice generation and final timing/pixels/collection/private remain false.'});
write(base+'production/latest-checkpoint.json',c);
const p='production/batches/sakurai-planning-game-design/queue.json',before=fs.readFileSync(p,'utf8'),q=JSON.parse(before),item=q.items.find(x=>x.slug==='similar-game-design');
if(!item||item.videoId||item.checkpoints.render)throw Error('Unexpected completed item');
Object.assign(item,{status:'in-progress',stage:job.stage,updatedAt:now,
  duplicateReview:{status:'distinct-current-check-passed',record:'production/batches/sakurai-planning-game-design/preflight/similar-game-design.json',inputsDigest:gate.inputsDigest,checkObservedAt:now,wholeContentEvidence:proof+'content-review-v2.json'},
  primaryFootageAcquisition:{sessionId:80344,actualPid:12944,stage:'complete-wholedecode-and-direct-action-edge-review',exitCode:0,cpuThreads:2,gpu:0,all53BoardsDirectlyRead:true,review:proof+'primary-gameplay-direct-review-v1.json',finalNarratedAllocationApproved:false},
  independentScript:{scenes:13,paragraphsKo:51,paragraphsEn:51,pairedWholeTextDirectlyCompared:true,overviewPromiseDirectlyCompared:true,review:base+'production/paired-script-direct-review-v1.json'},
  currentExecution:job,ttsStarted:false,nextAction:c.nextAction,
  gpuHandoff:{requested:false,foreignResearchInterrupted:false,reason:'Current foreign camera-projection TTS owns the lease. Our outer command waits without allocating the model or issuing pause requests. Restore actual original research after our future TTS handoff succeeds or fails.'}});
q.currentSlug='similar-game-design';q.updatedAt=now;q.lastProgressAt=now;
const tmp=p+'.tmp-similar-wait-'+process.pid;fs.writeFileSync(tmp,JSON.stringify(q,null,2)+'\n');if(fs.readFileSync(p,'utf8')!==before)throw Error('Concurrent queue update; preserve it');fs.renameSync(tmp,p);
write(proof+'latest-preflight-v2.json',{...c,primaryFootageAcquisition:item.primaryFootageAcquisition,duplicateReview:item.duplicateReview,completedVideo:false,gitPushAttempts:0,uploadAttempts:0,newImagesAddedToGit:0});
write(base+'production/prepared-code-verification-v1.json',{schemaVersion:1,checkedAt:now,
  scopedTypeScript:{command:'node motion-canvas/node_modules/typescript/bin/tsc --project projects/similar-game-design/production/tsconfig-mc-check-v1.json --pretty false',exitCode:0,scope:'Own13 independent MC scenes, own spatial helper and imported shared styles/depth heading only. Does not claim all foreign unfinished projects pass.'},
  pythonSyntax:{command:'qwen3-tts/.venv/Scripts/python.exe -X utf8 -m py_compile projects/similar-game-design/production/render-voice-v1.py',exitCode:0},
  dryRun:{exitCode:0,sceneCount:13,paragraphCount:51,noModelLoaded:true},finalAnimatedPixelsApproved:false});
console.log(JSON.stringify({stage:c.stage,session:61644,actualPid:33728,waitingWithoutGpu:true,foreignPauseChanged:0,newVoiceGenerated:false,newRenderApproved:false}));
