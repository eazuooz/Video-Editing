// Record actual private-save evidence without treating platform waits as delivery.
const fs = require('node:fs');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '../../..');
const base = 'projects/hierarchical-game-outlines/';
const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const write = (p, v) => fs.writeFileSync(path.join(root, p), JSON.stringify(v, null, 2) + '\n');
const now = new Date().toISOString();
const receiptPath = base + 'publishing/youtube-upload.json';
const receipt = read(receiptPath);
const qa = read(base + 'production/final-v1/qa.json');
const plan = read(base + 'production/final-v1/plan.json');
if (!qa.technicalApproved || receipt.videoId !== 'lEwpxP_qsDY' || !receipt.metadata.privacyVerified || receipt.scheduled) {
  throw Error('Current technical QA and actual private-save evidence are required.');
}
if (receipt.fullSettingsVerified || receipt.completed || receipt.gitDelivery?.pushVerified) {
  throw Error('This pending checkpoint must not overwrite a completed private delivery.');
}
const observation = spawnSync('powershell', ['-NoProfile', '-Command', 'Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name | ConvertTo-Json -Compress'], {encoding:'utf8', windowsHide:true});
if (observation.status !== 0) throw Error(observation.stderr);
const processes = JSON.parse(observation.stdout);
const old = read(base + 'production/latest-checkpoint.json');
const checkpoint = base + 'production/checkpoint-' + now.replace(/[-:.]/g, '') + '.json';
const pending = [
  'Prepared custom thumbnail: actual daily platform limit; wait up to24h without rapid retries',
  ...(receipt.processing.status === 'SD-HD-complete' ? [] : ['Actual SD/HD processing']),
  ...(!receipt.copyright.complete || receipt.monetization.selfAssessment.automaticResult.startsWith('pending')
    ? ['Actual new-file ad/copyright review result; do not assume approval'] : []),
  ...(receipt.burnedCaptionVerification.playerCaptionsOff === true ? []
    : ['Real uploaded game/PPT pixels with player CC off after processing']),
  ...(receipt.endScreen.status === 'saved-three-elements-HD60-timing-verified' && receipt.endScreen.playlist.id
    ? [] : ['Exact576.75–586.75 ending timing after HD60 and visible playlist ID']),
  'Selected per-video normal commit/push after full-settings private delivery',
  ...receipt.pendingPublicReview,
];
const nextAction = receipt.nextAction + ' All synthesis, ASR, source compilation, mix, render and QA workers have finished; do not restart them. Preserve existing8 delivered videos and all other user work. Continue only saved video lEwpxP_qsDY; no duplicate upload or public/scheduled state.';
const cp = {
  schemaVersion: 2, slug: 'hierarchical-game-outlines', observedAt: now,
  checkpointPath: checkpoint, previousCheckpoint: old.checkpointPath,
  status: 'rendered-technical-QA-collected-private-saved-platform-pending',
  finalVideo: {seconds:plan.seconds, frames:plan.totalFrames, width:1920, height:1080, fps:60,
    actualSeconds:plan.gameplaySeconds, explanationSeconds:plan.explanationSeconds,
    ratioErrorFrames:plan.ratioErrorFrames, actualCuts:46, selfCreatedGames:0,
    allCutsAndCaptionsApproved:true, mixed:true, rendered:true, qaApproved:true,
    qa:base+'production/final-v1/qa.json', collected:true, uploadedPrivate:true,
    fullPrivateSettingsVerified:false, privatelyDelivered:false, gitDelivered:false},
  sources:{finalSourceIds:['I-ccSZ5J1Bo'], actualCuts:46, audioStreams:0,
    crop:[0,0,1376,774], finalSourceReview:base+'production/final-v1/final-source-cut-review.json'},
  script:{scenes:12, paragraphs:60, preservedOriginalParagraphs:54,
    preservedExplanationClaims:6, preservedExplanationDurations:true,
    voiceReview:base+'production/voice-approval-v2.json',
    fullMixReview:base+'production/final-v1/full-mix-asr-review.json',
    mixedASROrthographyDiscrepanciesPreserved:true, humanListening:'pending'},
  visualReview:{KOENCues:299, cueCutViews:317, encodedBoundaryViews:138,
    compositionViews:20, allCurrentFinalPixelsReviewed:true,
    review:base+'production/final-v1/final-pixel-direct-review.json'},
  completedWorkerHistory:old.completedWorkerHistory || old.checkpointPath,
  workers:Object.fromEntries(Object.entries(old.workers||{}).map(([name, worker])=>[name,
    {pid:worker.pid, sessionId:worker.sessionId||worker.toolSessionId||null,
      status:worker.status, exitCode:worker.exitCode,
      alive:processes.some(p=>p.ProcessId===worker.pid), state:worker.state}])),
  vite:{port:9216,pid:8864,toolSessionId:67127,
    alive:processes.some(p=>p.ProcessId===8864), observedAt:now,
    action:'Reuse only if actually alive; preserve picking9212 and other user work'},
  upload:{videoId:receipt.videoId,url:receipt.url,status:receipt.status,
    receipt:receiptPath,privateSaved:true,noScheduleVerified:true,
    fixedCaptionedSourceSha256:receipt.video.sha256,
    manualKOEN:'published-and-reopened',englishMetadata:'published-and-reopened',
    coachingCard:receipt.coachingCard.status,endScreen:receipt.endScreen.status,
    endScreenDetails:receipt.endScreen,
    thumbnail:receipt.thumbnail,processing:receipt.processing,
    copyright:receipt.copyright,monetization:receipt.monetization,
    burnedCaptionVerification:receipt.burnedCaptionVerification,
    fullSettingsVerified:false},
  progress:{delivered:8,duplicateExcluded:1,inProgress:1,queued:14},
  activeTasks:[{type:receipt.copyright.complete && !receipt.monetization.selfAssessment.automaticResult.startsWith('pending')
    ? 'YouTube-platform-thumbnail-daily-limit' : 'YouTube-platform-thumbnail-and-automatic-checks',tabId:'18',
    playerTabId:'25',videoId:receipt.videoId,status:receipt.status}],
  pending,nextAction,
  gitDelivery:old.gitDelivery,
};
if (Object.values(cp.workers).some(w=>w.alive)) throw Error('A supposedly completed worker is alive; inspect before checkpoint.');
write(checkpoint,cp);write(base+'production/latest-checkpoint.json',cp);
const queuePath='production/batches/sakurai-planning-game-design/queue.json';
const q=read(queuePath), item=q.items.find(i=>i.slug===cp.slug);
item.stage='private-upload-platform-pending';item.updatedAt=now;item.nextAction=nextAction;
item.videoId=receipt.videoId;
item.checkpoints={...item.checkpoints,footage:true,scenes:true,mix:true,render:true,
  qa:true,collected:true,privateUploadSaved:true,publishingSettingsVerified:false,
  uploaded:true,gitDelivery:false};
item.execution={...item.execution,phase:cp.status,status:cp.status,
  runtimeCheckpoint:checkpoint,latestCheckpoint:checkpoint,state:base+'production/latest-checkpoint.json',
  workers:cp.workers,vite:cp.vite,upload:cp.upload,activeTasks:cp.activeTasks};
item.publishing={...item.publishing,videoId:receipt.videoId,url:receipt.url,
  status:receipt.status,fullSettingsVerified:false,receipt:receiptPath};
item.gitDelivery={...(item.gitDelivery||{}),status:'pending-full-private-settings-delivery',
  complete:false,commit:null,pushVerified:false};q.updatedAt=now;write(queuePath,q);
const manifest=read(base+'project.json');
manifest.status='rendered-QA-collected-private-saved-platform-settings-pending';
manifest.publishing={...manifest.publishing,videoId:receipt.videoId,url:receipt.url,
  privacyStatus:'private',scheduled:false,receipt:receiptPath,
  status:receipt.status,fullSettingsVerified:false};write(base+'project.json',manifest);
console.log(JSON.stringify({checkpoint,status:cp.status,viteAlive:cp.vite.alive,
  videoId:receipt.videoId,progress:cp.progress,pending:pending.slice(0,5)}));
