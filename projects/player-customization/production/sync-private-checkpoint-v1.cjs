// Usage: node projects/player-customization/production/sync-private-checkpoint-v1.cjs
// Roll up actual current evidence without replacing preserved candidate/history records.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),base='projects/player-customization';
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8'));
const write=(f,j)=>fs.writeFileSync(path.join(root,f),JSON.stringify(j,null,2)+'\n');
const seal=read(base+'/production/final-v1/final-pixel-direct-review-v1.json');
const execution=read(base+'/publishing/private-upload-execution-v1.json');
const receiptPath=base+'/publishing/youtube-upload-v1.json';
const receipt=fs.existsSync(path.join(root,receiptPath))?read(receiptPath):null;
const privateReady=!!(receipt?.uploaded&&receipt?.privateSaveVerified&&receipt?.platformAutomaticChecksComplete&&receipt?.burnedCaptionPixelsVerified&&receipt?.availableSettingsVerified);
const gitPath=base+'/publishing/private-delivery-git-verification-v1.json';
const delivery=fs.existsSync(path.join(root,gitPath))?read(gitPath):null;
const delivered=privateReady&&delivery?.pushed&&delivery?.exactLocalRemoteMatch&&delivery?.allRemoteBlobsVerified;
const next=delivered?'Continue similar-game-design full source/concept/current Studio duplicate review; do not regenerate or reupload this completed video.':privateReady?'Selectively deliver this reviewed private video using the isolated Git index, normal push and actual remote blob verification.':'Continue the single actual upload lf765yYhPdM on tab68; wait actual SD/HD/checks and verify private settings/CC-off pixels. Do not recollect media or submit another MP4.';
const queuePath='production/batches/sakurai-planning-game-design/queue.json',queue=read(queuePath),item=queue.items.find(i=>i.slug==='player-customization');
if(!item||execution.actualVideoId!=='lf765yYhPdM'||!seal.allFinalPixelsReviewed)throw Error('Actual current video evidence missing');
item.checkpoints={...item.checkpoints,script:true,narration:true,footage:true,scenes:true,mix:true,render:true,qa:true,collected:true};
item.currentExecution.status='closed-completed-encoded-QA-historical-worker';
item.currentExecution.workerExpectedRunning=false;
Object.assign(item,{status:delivered?'complete-private-review':privateReady?'private-reviewed-awaiting-git':'private-upload-in-progress',stage:delivered?'reviewed-private-delivered':privateReady?'selective-git-delivery':'single-captioned-private-upload-processing',actualUploadId:execution.actualVideoId,uploadTransferComplete:execution.uploadTransferComplete,allFinalPixels:true,qaApproved:true,collected:true,uploaded:privateReady,privateUpload:privateReady,fullSettingsVerified:privateReady,next,nextAction:next});
if(privateReady){item.videoId=receipt.videoId;item.uploadReceipt=receiptPath;}
if(delivered)item.gitDelivery={commit:delivery.commit,remoteCommit:delivery.remoteCommit,proof:gitPath,pushed:true,actualLocalRemoteMatch:true};
queue.updatedAt=new Date().toISOString();write(queuePath,queue);
const cpPath=base+'/production/latest-checkpoint.json',checkpoint=read(cpPath);
Object.assign(checkpoint,{status:item.status,stage:item.stage,next,uploaded:privateReady,privateUpload:privateReady,fullSettingsVerified:privateReady,collected:true,actualUploadId:execution.actualVideoId,recordedAt:new Date().toISOString()});
write(cpPath,checkpoint);
const projectPath=base+'/project.json',project=read(projectPath);
project.status=item.status;project.publishing={...project.publishing,actualVideoId:execution.actualVideoId,uploaded:privateReady,privateSaveVerified:privateReady,fullSettingsVerified:privateReady,execution:base+'/publishing/private-upload-execution-v1.json',receipt:privateReady?receiptPath:null};
write(projectPath,project);
console.log(JSON.stringify({privateReady,gitDelivered:!!delivered,uploaded:privateReady,stage:item.stage,next}));
