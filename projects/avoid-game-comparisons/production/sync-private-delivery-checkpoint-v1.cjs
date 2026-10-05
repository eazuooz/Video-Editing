// Reflect observed receipt states, preserving history and other users' files.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),base='projects/avoid-game-comparisons/',batch='production/batches/sakurai-planning-game-design';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),write=(p,j)=>fs.writeFileSync(path.join(root,p),JSON.stringify(j,null,2)+'\n');
const r=read(base+'publishing/youtube-upload.json'),qa=read(base+'production/final-v1/qa.json'),d=read(base+'production/delivery-output.json');
if(!qa.technicalApproved||!qa.allRenderedCaptionPixelsReviewed||d.files.length!==4||r.video.sha256!==qa.captionedSha256)throw Error('Reviewed delivery inputs differ');
const now=new Date().toISOString(),qp=batch+'/queue.json',q=read(qp),i=q.items.find(i=>i.slug==='avoid-game-comparisons');
const saved=r.privateUploadSaved===true,available=r.availableSettingsVerified===true,full=r.fullSettingsVerified===true;
const gitComplete=i.gitDelivery?.completed===true;
const stage=gitComplete&&saved?'private-settings-and-production-git-verified':full?'private-settings-verified-awaiting-production-git':saved?'private-saved-platform-settings-review':r.status;
Object.assign(i,{videoId:r.actualVideoId,stage,updatedAt:now,status:gitComplete&&saved?'uploaded-private-awaiting-user-review':'in-progress',renderComplete:true,qaComplete:true,collected:true,privateUploadSaved:saved,availableSettingsVerified:available,publishingSettingsVerified:full,completedVideoDelivery:gitComplete&&saved});
for(const k of ['script','narration','footage','scenes','mix','render','qa','collected','finalTimingApproved','bodyRatioApproved'])i.checkpoints[k]=true;
Object.assign(i.checkpoints,{privateUploadSaved:saved,publishingSettingsVerified:full,gitDelivery:i.gitDelivery?.completed===true});
i.publishing={receipt:base+'publishing/youtube-upload.json',videoId:r.actualVideoId,privacy:'private',scheduled:false,availableSettingsVerified:available,fullSettingsVerified:full,publishingFollowups:r.publishingFollowups};
i.execution={...i.execution,observedAt:now,phase:stage,status:saved?'single-upload-saved-workers-closed':'single-upload-in-progress',pid:null,sessionId:null,alive:!saved,activeTasks:saved?[]:[{kind:'single-captioned-private-upload',videoId:r.actualVideoId,browserId:'2',tabId:'4'}],cpuProductionJobs:0,primaryCpuProductionJobs:0,gpuSynthesisJobs:0,renderJobs:0,uploads:saved?0:1};
i.nextAction=gitComplete&&saved?'Preserve this completed private video and begin the next queued full-content/current Studio duplicate review.':full?'Select reviewed production/QA/collection/private settings and essential images for a normal per-video Git push; preserve human review pending.':'Finish available private settings and actual CC-off pixel verification; keep automatic reviews pending until observed.';
q.updatedAt=now;write(qp,q);
for(const p of [base+'production/latest-checkpoint.json',batch+'/proof-avoid-game-comparisons/latest-checkpoint.json']){const c=read(p);Object.assign(c,{stage,updatedAt:now,execution:i.execution,videoId:r.actualVideoId,renderComplete:true,qaComplete:true,collected:true,privateUploadSaved:saved,availableSettingsVerified:available,fullSettingsVerified:full,completedVideoDelivery:gitComplete&&saved,nextAction:i.nextAction});write(p,c);}
console.log(JSON.stringify({stage,videoId:r.actualVideoId,saved,available,full,gitComplete:i.gitDelivery?.completed===true}));
