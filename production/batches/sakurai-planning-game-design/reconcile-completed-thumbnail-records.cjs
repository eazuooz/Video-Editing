const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),batch='production/batches/sakurai-planning-game-design';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const write=(p,v)=>fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');
const q=read(batch+'/queue.json');
for(const slug of ['hierarchical-game-outlines','game-reward-planning']){
 const base='projects/'+slug,r=read(base+'/publishing/youtube-upload.json'),cp=read(base+'/production/latest-checkpoint.json');
 if(!r.fullSettingsVerified||!r.thumbnail.savedVerified)throw Error('Actual saved proof required');
 r.completed=true;r.completionScope='Private upload and requested platform settings. Public publication, human listening and final public rights are not approved.';
 for(const f of r.publishingFollowups||[])if(f.savedVerified)f.nextAction='None; thumbnail saved and reopened on the existing private ID.';
 if(cp.publishingFollowups?.some(f=>!f.savedVerified)){cp.historicalPublishingFollowups??=[];cp.historicalPublishingFollowups.push({observedAt:cp.gitDelivery?.recordedAt||cp.gitDelivery?.deliveredAt||null,records:cp.publishingFollowups});}
 cp.publishingFollowups=q.publishingFollowups.filter(f=>f.slug===slug);
 cp.currentPublishingVerification={fullSettingsVerified:true,thumbnailSavedVerified:true,evidence:base+'/publishing/thumbnail-followup-completed.json',previousGitDeliveryMetadata:'Earlier nested Git evidence remains historical; current platform completion is recorded here and at the top level.'};
 write(base+'/publishing/youtube-upload.json',r);write(base+'/production/latest-checkpoint.json',cp);
}
console.log('Reconciled current private-setting completion; historical delivery evidence and pending public/human reviews preserved.');
