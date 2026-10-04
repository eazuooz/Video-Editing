// Record the two actual normal-UI saves observed after the 24-hour gate.
// No media generation, upload, privacy change or automatic UI action occurs here.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const write=(p,v)=>fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const now=new Date().toISOString(),batch='production/batches/sakurai-planning-game-design';
if(Date.parse(now)<Date.parse('2026-10-04T14:50:04.773Z'))throw Error('Normal UI retry gate has not passed');
const q=read(batch+'/queue.json');
const specs=[['hierarchical-game-outlines','lEwpxP_qsDY','20261004T1450','6a3093d88ae62e7e05457f52280bb2c99d024f1742111aa42360a823fb83af68'],['game-reward-planning','D81WnOMytG4','20261004T1451','72bfafdea9f955e53c10608ebaf7eea987ad400783d6317ae7a90e0ce6f57b0f']];
const records=[];
for(const [slug,id,stamp,expected] of specs){
 const base='projects/'+slug,receiptPath=base+'/publishing/youtube-upload.json',r=read(receiptPath),i=q.items.find(x=>x.slug===slug);
 if(r.videoId!==id||i.videoId!==id||sha(r.thumbnail.path)!==expected)throw Error('Wrong video or thumbnail: '+slug);
 const prefix=base+'/publishing/proof/thumbnail-saved-reopened-'+stamp,ax=fs.readFileSync(path.join(root,prefix+'.ax.txt'),'utf8');
 for(const text of [id,'업로드된 썸네일','비공개','button (disabled) 저장',slug+'.captioned.mp4'])if(!ax.includes(text))throw Error('Incomplete actual reopened evidence: '+text);
 const record={schemaVersion:1,slug,videoId:id,recordedAt:now,method:'CUA normal filechooser, prepared PNG, Save, reload and directly read actual pixels',retryNotBefore:'2026-10-04T14:50:04.773Z',retryAfterGateVerified:true,thumbnailFile:r.thumbnail.path,thumbnailSha256:expected,savedVerified:true,reopened:true,actualThumbnailPixelsDirectlyReviewed:true,privacy:'private',privateStateReobserved:true,noNewVideoUpload:true,noMediaRegeneration:true,previousAvailableSettingsEvidenceRetained:true,fullSettingsVerified:true,humanListeningAndPublicRightsStillPending:true,proofs:[prefix+'.png',prefix+'.ax.txt'].map(p=>({path:p,sha256:sha(p)}))};
 write(base+'/publishing/thumbnail-followup-completed.json',record);records.push(record);
 r.historicalThumbnailObservations??=[];
 if(r.thumbnail.status!=='saved-reopened-verified')r.historicalThumbnailObservations.push({...r.thumbnail,archivedAt:now});
 Object.assign(r.thumbnail,{status:'saved-reopened-verified',savedVerified:true,verifiedAt:now,normalUiRetryObserved:true,newVideoLimitDirectlyAttempted:slug==='game-reward-planning'?false:r.thumbnail.newVideoLimitDirectlyAttempted,record:base+'/publishing/thumbnail-followup-completed.json'});
 r.status='saved-private-settings-verified';r.fullSettingsVerified=true;r.platformUpdatedAt=now;
 r.thumbnailFollowup=record;r.nextAction='Continue the next queued production. Preserve private status; human listening, public rights and publication-dependent pinned comment remain pending.';
 for(const f of r.publishingFollowups||[]){f.status='completed-saved-reopened';f.savedVerified=true;f.completedAt=now;f.completionEvidence=record.proofs;}
 if(r.gitDelivery){r.gitDelivery.thumbnailPending=false;r.gitDelivery.fullSettingsVerified=true;r.gitDelivery.publishingFollowupVerifiedAt=now;}
 write(receiptPath,r);
 i.status='uploaded-private-awaiting-user-review';i.stage='private-settings-and-production-git-verified';i.checkpoints.thumbnail=true;i.checkpoints.publishingSettingsVerified=true;i.updatedAt=now;
 i.publishing??={videoId:id,url:'https://youtu.be/'+id,receipt:receiptPath};Object.assign(i.publishing,{status:r.status,fullSettingsVerified:true,thumbnailFollowup:record});
 if(i.gitDelivery){i.gitDelivery.thumbnailPending=false;i.gitDelivery.fullSettingsVerified=true;i.gitDelivery.publishingFollowupVerifiedAt=now;}
 for(const f of [...(q.publishingFollowups||[]),...(i.publishing.followups||[])])if(f.slug===slug){f.status='completed-saved-reopened';f.savedVerified=true;f.completedAt=now;f.completionEvidence=record.proofs;f.nextAction='None; prepared thumbnail saved and reopened on the existing private ID.';}
 const cpPath=base+'/production/latest-checkpoint.json',cp=read(cpPath);cp.observedAt=now;cp.updatedAt=now;cp.status='private-settings-and-production-git-verified';cp.stage=cp.status;cp.thumbnailFollowup=record;cp.fullSettingsVerified=true;cp.nextAction=r.nextAction;
 if(cp.finalVideo){cp.finalVideo.fullPrivateSettingsVerified=true;cp.finalVideo.privatelyDelivered=true;}
 write(cpPath,cp);
}
q.progress.fullSettingsDelivered=10;q.progress.publishingFollowups=0;q.progress.remaining=13;q.updatedAt=now;q.lastProgressAt=now;
write(batch+'/queue.json',q);
const nextPath=batch+'/proof-avoid-game-comparisons/latest-checkpoint.json',cp=read(nextPath);cp.updatedAt=now;cp.publishingFollowups=q.publishingFollowups;cp.progress=q.progress;cp.previousProductionDelivered.fullSettingsVerified=true;write(nextPath,cp);
write(batch+'/thumbnail-followups-completed-20261004.json',{schemaVersion:1,recordedAt:now,records,activePublishingFollowups:0,productionGitDelivered:10,fullSettingsDelivered:10,currentSlug:q.currentSlug,pendingPublicAndHumanReviewsPreserved:true});
console.log(JSON.stringify({status:'two-thumbnails-saved-reopened',fullSettingsDelivered:10,currentSlug:q.currentSlug}));
