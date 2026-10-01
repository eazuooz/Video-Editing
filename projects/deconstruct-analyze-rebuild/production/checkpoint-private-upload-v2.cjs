const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),base='projects/deconstruct-analyze-rebuild',rp=path.join(root,base,'publishing/youtube-upload-v2.json');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8')),write=(f,v)=>fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');
const r=read(rp),now=new Date().toISOString();
if(r.studio?.videoId&&r.studio.videoId!=='pY04E8aRvJQ')throw Error('Another actual upload receipt exists');
r.videoId='pY04E8aRvJQ';r.studio={...r.studio,videoId:r.videoId,url:'https://studio.youtube.com/video/pY04E8aRvJQ/edit',uploadStartedAt:now,completed:false,uploadStillRunning:true};r.status='uploading-private-settings-in-progress';write(rp,r);
const qf=path.join(root,'production/batches/private-review-expansion/queue.json'),q=read(qf),i=q.items.find(x=>x.slug==='deconstruct-analyze-rebuild');i.stage='new-private-upload-settings-in-progress';i.newPrivateUpload={videoId:r.videoId,receipt:base+'/publishing/youtube-upload-v2.json',status:r.status,completed:false};i.output={directory:'output/deconstruct-analyze-rebuild',report:base+'/production/delivery-output.json',seconds:r.video.seconds,cues:122};q.updatedAt=now;write(qf,q);console.log('Actual pending upload pY04E8aRvJQ saved; do not duplicate.');
