// Journal the actual Studio upload immediately, before applying remaining settings.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),rf=path.resolve(__dirname,'../publishing/youtube-upload-v2.json');
const r=JSON.parse(fs.readFileSync(rf,'utf8'));
if(r.videoId&&r.videoId!=='BYk6cLsO9Mc')throw Error('Different actual upload exists');
const file='output/responsive-game-feedback/responsive-game-feedback.clean.mp4';
r.video={...r.video,path:file,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,file))).digest('hex'),bytes:fs.statSync(path.join(root,file)).size,version:'clean master with manually uploaded KO/EN selectable captions; Korean boxed-caption master separately collected locally'};
r.videoId='BYk6cLsO9Mc';r.url='https://youtu.be/BYk6cLsO9Mc';r.studioUrl='https://studio.youtube.com/video/BYk6cLsO9Mc/edit';r.status='uploading-settings-incomplete';r.uploadStartedAt=new Date().toISOString();
r.uploadObservation={fileName:'responsive-game-feedback.clean.mp4',privateDraftVisible:true,source:'Actual Studio upload dialog filename and link',remaining:'Transfer/processing and all publishing settings require actual verification'};
fs.writeFileSync(rf,JSON.stringify(r,null,2)+'\n');
const qf=path.join(root,'production/batches/private-review-expansion/queue.json'),q=JSON.parse(fs.readFileSync(qf,'utf8')),i=q.items.find(x=>x.slug===r.slug);
i.stage='new-private-upload-in-progress';i.upload={videoId:r.videoId,url:r.url,receipt:'projects/responsive-game-feedback/publishing/youtube-upload-v2.json',status:r.status,tabId:'33'};q.updatedAt=new Date().toISOString();
fs.writeFileSync(qf,JSON.stringify(q,null,2)+'\n');console.log('Actual clean-master upload BYk6cLsO9Mc journaled; no second upload required.');
