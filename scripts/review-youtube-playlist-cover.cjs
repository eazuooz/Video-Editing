const fs=require('node:fs'),path=require('node:path');
const base=path.resolve(__dirname,'../output/youtube-library-refresh/v2/playlist-covers');
const [action,...ids]=process.argv.slice(2);
const file=path.join(base,'progress.json'),p=JSON.parse(fs.readFileSync(file,'utf8'));
if(!['archive','review'].includes(action)||!ids.length)throw new Error('archive/review and actually inspected IDs required');
for(const id of ids){
 const r=p.generated[id];if(!r)throw new Error('Not generated '+id);
 const draft=path.join(base,'drafts',id);fs.mkdirSync(draft,{recursive:true});
 if(action==='archive')for(const [ext,name]of[['png','initial.png'],['json','initial.json'],['prompt.txt','initial.prompt.txt']]){
   const dest=path.join(draft,name);if(!fs.existsSync(dest))fs.copyFileSync(path.join(base,'raw',id+'.'+ext),dest,fs.constants.COPYFILE_EXCL);
 }
 if(action==='review')p.visualReviewed[id]={id,sha256:r.sha256,reviewedAt:new Date().toISOString(),checks:['selected-1280x720-JPEG-manually-viewed','headline-readable-and-correct','topic-specific-environment-cat-action-composition','playlist-palette','no-false-mathematical-claim-or-bad-directional-arrow'],status:'ready-to-upload'};
}
p.updatedAt=new Date().toISOString();fs.writeFileSync(file,JSON.stringify(p,null,2)+'\n');console.log(JSON.stringify({generated:Object.keys(p.generated).length,reviewed:Object.keys(p.visualReviewed).length,applied:Object.keys(p.applied).length}));
