// Select this reviewed production with an isolated index. Never modify the shared external index.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),slug='character-parameters',base=`projects/${slug}`,rev=base;
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8').replace(/^\uFEFF/,''));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const run=(cmd,args,env=process.env,input)=>{const r=cp.spawnSync(cmd,args,{cwd:root,env,input,encoding:'utf8',windowsHide:true,maxBuffer:256e6});if(r.status!==0)throw Error(cmd+' '+args.join(' ')+'\n'+r.stdout+'\n'+r.stderr);return r.stdout.trimEnd();};
const git=(args,env,input)=>run('git',args,env,input);
const save=(f,v)=>fs.writeFileSync(path.join(root,f),JSON.stringify(v,null,2)+'\n');
const walk=dir=>fs.readdirSync(path.join(root,dir),{withFileTypes:true}).flatMap(e=>e.isSymbolicLink()||/^(?:__pycache__|node_modules|\.venv|archive|delivery-history)$/.test(e.name)?[]:e.isDirectory()?walk(dir+'/'+e.name):[dir+'/'+e.name]);
const roots=[base,`motion-canvas/src/projects/${slug}`,`manim/projects/${slug}`,`production/batches/sakurai-planning-game-design/proof-${slug}`];
const text=f=>/\.(?:json|md|py|cjs|ps1|tsx?|meta|ass|srt|csv)$/i.test(f)||/\/(?:description[^/]*|upload-description[^/]*|title[^/]*|pinned-comment\.ko|[^/]+\.ax)\.txt$/.test(f);
const forbidden=f=>/\.(?:log|pyc|mp4|m4a|wav|aac|mp3|webm|mkv|zip|7z|gz|png|jpe?g|webp|gif|bmp|tiff?)$/i.test(f)||/\.info\.json$|\.ax\.txt$|raw-original|research.*(?:transcript|subtitle)|source.*(?:\.ja\.srt|\.ja\.txt)/i.test(f);
const planPath=`${rev}/publishing/git-delivery-stage-paths-v1.json`,proofPath=`${rev}/publishing/private-delivery-git-verification-v1.json`;
const batch=`production/batches/sakurai-planning-game-design`,extras=[`${batch}/preflight/${slug}.json`,'motion-canvas/vite.character-parameters.black-preflight-v1.config.ts','motion-canvas/tsconfig.character-parameters.json'];
const followup='projects/picking-sides/publishing/postpublication-20261010';
const shared=['.gitignore','shared/git-essential-images.json','motion-canvas/projects.json','projects/rebuild-index.json',`${batch}/queue.json`];
const images=read(`${rev}/publishing/private-settings-direct-review-v1.json`).minimalReviewedImages;
for(const e of images)if(e.project!==slug||e.sha256!==sha(fs.readFileSync(path.join(root,e.path))))throw Error('Reviewed essential image changed '+e.path);
if(process.argv.includes('--prepare')){
 const inventory=read(`${base}/publishing/git-delivery-paths-v1.json`);
 const files=[...new Set([...inventory.sourcePaths,`${base}/publishing/git-delivery-paths-v1.json`,...images.map(e=>e.path),planPath])].filter(f=>f!==proofPath).sort();
 save(planPath,{schemaVersion:4,slug,actualHeadAtPreparation:git(['rev-parse','HEAD']),preparedAt:new Date().toISOString(),selectedPaths:files,sharedPaths:shared,essentialImages:images.map(e=>e.path),externalIndexPolicy:'Preserve every original index byte and entry; shared staged deletions are foreign and remain untouched.',status:'prepared-only',excluded:'All media, raw original info and whole research subtitles; QA/contact/render/caption raster images.'});
 console.log(JSON.stringify({prepared:true,paths:files.length,images:images.length}));process.exit(0);
}
if(!process.argv.includes('--stage-only')&&!process.argv.includes('--deliver'))throw Error('Choose prepare, stage-only or deliver');
const receipt=read(`${base}/publishing/youtube-upload-v1.json`),seal=read(`${base}/production/final-v1/final-pixel-direct-review-v1.json`);
if(receipt.actualVideoId!=='nic5Sp6dylQ'||!receipt.savedPrivateVerified||!receipt.fullSettingsVerified||!receipt.platformAutomaticChecksComplete||!receipt.uploadedCcOffPixelsVerified||!receipt.qaApproved||!receipt.collected)throw Error('Actual reviewed private upload required');
if(!seal.allFinalPixelsReviewed||!seal.qaApproved||seal.sourceSha256!==receipt.video.sha256)throw Error('Current final pixel gate missing or upload differs');
const plan=read(planPath),files=plan.selectedPaths,allowed=new Set([...files,...shared]);
if(plan.slug!==slug||JSON.stringify(plan.sharedPaths)!==JSON.stringify(shared))throw Error('Wrong scope');
for(const f of files)if(!roots.some(d=>f.startsWith(d+'/'))&&!extras.includes(f)&&!f.startsWith(followup+'/'))throw Error('Foreign selected path '+f);
const parent=git(['rev-parse','HEAD']),externalIndex=path.resolve(root,git(['rev-parse','--git-path','index']));
const beforeBytes=fs.readFileSync(externalIndex),beforeEntries=git(['ls-files','--stage','-z']);
const stagedForeign=git(['diff','--cached','--name-only','-z']).split('\0').filter(Boolean);
// Existing external entries are preserved byte-for-byte, including reverse entries from earlier selective deliveries.
const stagedOverlap=stagedForeign.filter(f=>files.includes(f));
const dir=fs.mkdtempSync(path.join(root,'.git','character-parameters-v1-')),env={...process.env,GIT_INDEX_FILE:path.join(dir,'index')};
git(['read-tree',parent],env);
for(let i=0;i<files.length;i+=15)git(['add','--',...files.slice(i,i+15)],env);
function merge(f,old){
 if(f==='.gitignore'){let t=old.trimEnd();for(const e of images)if(!t.split(/\r?\n/).includes('!'+e.path))t+='\n!'+e.path;return t+'\n';}
 let j=JSON.parse(old),current=read(f);
 if(f==='shared/git-essential-images.json'){for(const e of images){const old=j.entries.find(x=>x.path===e.path);if(old&&old.sha256!==e.sha256)throw Error('Conflicting raster approval');if(!old)j.entries.push(e);}}
 else if(f==='motion-canvas/projects.json'){for(const p of current.filter(p=>typeof p==='string'&&p.includes('/'+slug+'/')))if(!j.includes(p))j.push(p);}
 else if(f==='projects/rebuild-index.json'){const own=current.projects.find(p=>p.slug===slug);if(!own)throw Error('Missing own manifest entry');const i=j.projects.findIndex(p=>p.slug===slug);if(i<0)j.projects.push(own);else j.projects[i]=own;}
 else {const i=j.items.findIndex(x=>x.slug===slug),own=current.items.find(x=>x.slug===slug);if(i<0||!own)throw Error('Missing own queue item');j.items[i]=own;const pickCurrent=current.items.find(x=>x.slug==='picking-sides'),pickHead=j.items.find(x=>x.slug==='picking-sides');if(pickCurrent?.postPublicationFollowup&&pickHead)pickHead.postPublicationFollowup=pickCurrent.postPublicationFollowup;j.lastProgressAt=current.lastProgressAt;j.updatedAt=current.updatedAt;}
 return JSON.stringify(j,null,2)+'\n';
}
const expectedShared={};for(const f of shared){const b=git(['hash-object','-w','--stdin'],env,merge(f,git(['show',parent+':'+f])));git(['update-index','--add','--cacheinfo','100644',b,f],env);expectedShared[f]=b;}
const changes=git(['diff','--cached','--name-status','-z',parent],env).split('\0').filter(Boolean),rows=[];
for(let i=0;i<changes.length;i+=2)rows.push({status:changes[i],path:changes[i+1]});
if(rows.some(r=>!allowed.has(r.path)||r.status==='D'))throw Error('Unexpected deletion or foreign change');
const stagedMap=new Map(git(['ls-files','--stage','-z'],env).split('\0').filter(Boolean).map(l=>{const [m,f]=l.split('\t');return[f,m.split(' ')[1]];}));
const workingBlobs=git(['hash-object','--stdin-paths'],env,files.join('\n')+'\n').split(/\r?\n/);
if(workingBlobs.length!==files.length)throw Error('Explicit blob count mismatch');
for(let i=0;i<files.length;i++)if(stagedMap.get(files[i])!==workingBlobs[i])throw Error('Staged source differs '+files[i]);
for(const f of shared)if(stagedMap.get(f)!==expectedShared[f])throw Error('Owned shared merge differs '+f);
const checks={};
checks.whitespace=git(['diff','--cached','--check',parent],env);
checks.media=run(process.execPath,['scripts/media-policy.cjs'],env);
checks.rebuild=run(process.execPath,['scripts/build-rebuild-manifests.cjs',slug,'--check'],env);
checks.duplicate=run(process.execPath,['scripts/review-video-duplicates.cjs',slug,'--check'],env);
if(git(['rev-parse','HEAD'])!==parent||sha(fs.readFileSync(externalIndex))!==sha(beforeBytes)||git(['ls-files','--stage','-z'])!==beforeEntries)throw Error('Concurrent HEAD or index changed; no commit created');
const proof={schemaVersion:4,slug,actualVideoId:'nic5Sp6dylQ',parent,temporaryIndex:env.GIT_INDEX_FILE,selectedPaths:files,changedPaths:rows,ownedSharedBlobs:expectedShared,checks,allFinalStagedBlobsVerified:true,externalStagedOverlapPaths:stagedOverlap,externalIndexSha256Before:sha(beforeBytes),externalIndexUnchanged:true,essentialRasterPaths:images.map(e=>e.path),mediaAdded:0,recordedAt:new Date().toISOString(),pushed:false};
fs.writeFileSync(path.join(dir,'external-index-before.bin'),beforeBytes);fs.writeFileSync(path.join(dir,'stage-verification.json'),JSON.stringify(proof,null,2)+'\n');
if(process.argv.includes('--stage-only')){console.log(JSON.stringify({stageOnly:true,changedPaths:rows.length,index:env.GIT_INDEX_FILE,checks}));process.exit(0);}
const tree=git(['write-tree'],env),commit=git(['commit-tree',tree,'-p',parent],env,'Deliver reviewed character parameters video and public coaching comment follow-up\n');
git(['update-ref','HEAD',commit,parent]);Object.assign(proof,{commit,localCommit:commit});save(proofPath,proof);
try{git(['push','origin',commit+':refs/heads/main']);}catch(e){proof.pushFailure={at:new Date().toISOString(),message:e.message};save(proofPath,proof);throw e;}
const local=git(['rev-parse','HEAD']),remote=git(['ls-remote','origin','refs/heads/main']).split(/\s/)[0];
if(local!==commit||remote!==commit)throw Error('Actual local/remote differs; inspect concurrent delivery');
const finalMap=new Map(git(['ls-tree','-r','-z',remote]).split('\0').filter(Boolean).map(l=>{const [m,f]=l.split('\t');return[f,m.split(' ')[2]];}));
for(const f of [...files,...shared])if(finalMap.get(f)!==stagedMap.get(f))throw Error('Final remote blob mismatch '+f);
if(sha(fs.readFileSync(externalIndex))!==sha(beforeBytes)||git(['ls-files','--stage','-z'])!==beforeEntries)throw Error('External index changed');
Object.assign(proof,{pushed:true,remoteCommit:remote,exactLocalRemoteMatch:true,allRemoteBlobsVerified:true,verifiedBlobCount:files.length+shared.length,externalIndexSha256After:sha(fs.readFileSync(externalIndex)),verifiedAt:new Date().toISOString()});save(proofPath,proof);
console.log(JSON.stringify({commit,remote,changedPaths:rows.length,verifiedBlobs:proof.verifiedBlobCount,images:images.length,externalIndexUnchanged:true,pushed:true}));
