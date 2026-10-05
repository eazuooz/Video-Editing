// Capture minimal reviewed publishing images; retain full QA/source image banks locally.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base='projects/avoid-game-comparisons/',batch='production/batches/sakurai-planning-game-design/';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex'),read=p=>fs.readFileSync(path.join(root,p)),json=p=>JSON.parse(read(p)),write=(p,v)=>fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');
const git=a=>{const r=cp.spawnSync('git',a,{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:64e6});if(r.status)throw Error(r.stderr);return r.stdout;};
const now=new Date().toISOString(),receipt=json(base+'publishing/youtube-upload.json');
if(!receipt.fullSettingsVerified||receipt.actualVideoId!=='bCyRB3ksiGo')throw Error('Private settings not verified');
const images=[
 ['publishing/thumbnail.png','delivery-thumbnail','Directly reviewed delivered yellow-strip/white/black Korean game-and-original-cat thumbnail; exact single private upload.'],
 ['publishing/proof/private-thumbnail-HD-saved.png','minimal-publishing-proof','One saved Studio view proves the new thumbnail, actual private ID and completed SD/HD; retain rather than repeated screenshots.'],
 ['publishing/proof/cc-off-game-30s-HD.png','minimal-publishing-proof','One actual uploaded gameplay frame proves fixed Korean pixels with player CC off at 1080p60.'],
 ['publishing/proof/cc-off-PPT-70s-HD.png','minimal-publishing-proof','One actual uploaded white explanation frame proves fixed Korean pixels with CC off; gameplay proof alone cannot establish this.'],
 ['publishing/proof/end-screen-three-elements-reopened.png','minimal-publishing-proof','One saved/reopened 60fps ending view proves playlist, self-subscribe and canonical coaching link placement outside original member identities/title/logo.'],
 ['publishing/proof/copyright-no-claims-monetizing.png','minimal-publishing-proof','One actual saved claims page proves no claims/protected content and monetizing according to settings after initial review notice clears.']
].map(([p,purpose,reason])=>({path:base+p,purpose,reason,reviewedAt:now,sha256:hash(read(base+p)),project:'avoid-game-comparisons'}));
const registry=json('shared/git-essential-images.json');
for(const e of images){const old=registry.entries.find(x=>x.path===e.path);if(old&&old.sha256!==e.sha256)throw Error('Existing essential image hash differs');if(!old)registry.entries.push(e);}
write('shared/git-essential-images.json',registry);
let ignore=read('.gitignore').toString('utf8');
for(const e of images)if(!ignore.split(/\r?\n/).includes('!'+e.path))ignore=ignore.replace(/\s*$/,'')+'\n!'+e.path+'\n';
fs.writeFileSync(path.join(root,'.gitignore'),ignore);
const rawDir=path.join(root,'output/avoid-game-comparisons/publishing-proof-raw');fs.mkdirSync(rawDir,{recursive:true});
const ax=[];for(const f of fs.readdirSync(path.join(root,base+'publishing/proof')).filter(x=>x.endsWith('.ax.txt'))){const p=base+'publishing/proof/'+f,b=read(p),s=b.toString('utf8').split(/\r?\n/).map(l=>l.replace(/[\t ]+$/,'')).join('\n');fs.writeFileSync(path.join(rawDir,f),b);fs.writeFileSync(path.join(root,p),s);ax.push({path:p,rawSha256:hash(b),normalizedSha256:hash(Buffer.from(s)),normalization:'Trailing spaces/tabs only; raw UTF8 preserved in ignored output local proof bank.'});}
write(base+'publishing/proof/ax-normalization.json',{schemaVersion:1,reviewedAt:now,entries:ax});
receipt.proofHashes=receipt.proofFiles.filter(p=>fs.existsSync(path.join(root,p))).map(p=>({path:p,sha256:hash(read(p))}));
receipt.essentialImageReview={registry:'shared/git-essential-images.json',count:images.length,images,qaSourceFramesAndContactSheets:'local-only; no new Git QA/source raster'};write(base+'publishing/youtube-upload.json',receipt);
cp.execFileSync(process.execPath,[base+'production/sync-private-delivery-checkpoint-v1.cjs'],{cwd:root,windowsHide:true});
const qp=batch+'queue.json',q=json(qp);for(const key of ['rendered','collected','uploaded','productionRendered','productionCollected','privateSaved','fullSettingsDelivered'])q.progress[key]=11;q.lastProgressAt=now;write(qp,q);
const indexBefore=read('projects/rebuild-index.json');
try{require(path.join(root,'scripts/build-rebuild-manifests.cjs')).generate('avoid-game-comparisons');}
finally{fs.writeFileSync(path.join(root,'projects/rebuild-index.json'),indexBefore);}
write(batch+'proof-avoid-game-comparisons/final-delivery-essential-image-review.json',{schemaVersion:1,reviewedAt:now,videoId:receipt.actualVideoId,images,newEssentialImageCount:6,newQaSourceImageCount:0,mediaCount:0,fullSettingsVerified:true,globalRebuildIndexWorkingBytesPreserved:true});
console.log(JSON.stringify({videoId:receipt.actualVideoId,essentialImages:images.length,qaSourceImages:0,normalizedAx:ax.length,globalIndexPreserved:true}));
