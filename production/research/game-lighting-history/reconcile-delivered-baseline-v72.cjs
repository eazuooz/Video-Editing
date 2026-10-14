// Reconcile stale series rollup from actual saved delivery; do not change the upload.
const fs=require('node:fs'),crypto=require('node:crypto');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const receipt='projects/game-lighting-history-03/publishing/youtube-upload-v21.json',r=JSON.parse(fs.readFileSync(receipt,'utf8'));
if(r.actualVideoId!=='lIDe30dqC28'||r.videoId!=='lIDe30dqC28'||!r.privateSaved||!r.uploaded||!r.fullSettingsVerified||!r.qaApproved||!r.collected||!r.gitDelivery?.remoteMatches)throw Error('Actual completed baseline receipt required');
const evidence='production/research/game-lighting-history/episode03-series-rollup-reconciliation-v72.json';
if(fs.existsSync(evidence))throw Error('Preserve existing reconciliation');
const p='production/research/game-lighting-history/series-plan.json',series=JSON.parse(fs.readFileSync(p,'utf8')),episode=series.episodes.find(x=>x.slug==='game-lighting-history-03');
const before=JSON.parse(JSON.stringify(episode));
Object.assign(episode,{status:'baseline-private-delivery-and-Git-complete; current-four-game-teaching-audit-pending',outputCollected:true,uploaded:true,actualVideoId:r.actualVideoId,renderProduced:true,finalDurationSeconds:1551.4,actualDeliveredFrames:93084,baselineDeliveryComplete:true,currentFourGameTeachingReviewApproved:false,currentRevisionUploaded:false,actualBaselineReceipt:receipt,seriesRollupReconciliation:evidence});
const record={recordedAt:new Date().toISOString(),scope:'Preserve completed logical03 baseline; reconcile stale uploaded=false/null. This does not approve the later four-game revision or complete logical01/02/04.',receipt:{path:receipt,sha256:sha(receipt)},previousRollup:before,actualVideoId:r.actualVideoId,actualPrivateStatus:'비공개',latestDirectStudioObservation:'production/research/game-lighting-history/episode04-current-duplicate-rereview-v68.json',priorGitDelivery:r.gitDelivery,actualBaselineSettingsVerified:true,currentFourGameTeachingReviewApproved:false,oldVideoChanged:false,newUploadStarted:false,completedMediaRebuilt:false,newGitImages:0};
fs.writeFileSync(evidence,JSON.stringify(record,null,2)+'\n');series.updatedAt=record.recordedAt;fs.writeFileSync(p,JSON.stringify(series,null,2)+'\n');
console.log(JSON.stringify({actualBaselineId:r.actualVideoId,baselineDeliveryComplete:true,newRevisionUploaded:false,otherEpisodesChanged:false}));
