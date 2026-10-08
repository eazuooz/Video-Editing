// Usage: node projects/player-customization/production/deliver-reviewed-private-v1.cjs --prepare|--stage-only|--deliver
// One reviewed video only; isolated index and owned shared-file merges preserve concurrent work.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),slug='player-customization',base=`projects/${slug}`;
const planPath=`${base}/production/git-delivery-paths-v1.json`,proofPath=`${base}/publishing/private-delivery-git-verification-v1.json`;
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8').replace(/^\uFEFF/,''));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const run=(cmd,args,env=process.env,input)=>{const start=Date.now();while(true){const r=cp.spawnSync(cmd,args,{cwd:root,env,input,encoding:'utf8',windowsHide:true,maxBuffer:256e6});if(r.status===0)return r.stdout.trimEnd();if(cmd==='git'&&/index\.lock.*File exists|Unable to create .*index\.lock/s.test(r.stderr)&&Date.now()-start<60000){Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,500);continue;}throw Error(cmd+' '+args.join(' ')+'\n'+r.stdout+'\n'+r.stderr);}};
const git=(args,env,input)=>run('git',args,env,input);
const walk=dir=>fs.readdirSync(path.join(root,dir),{withFileTypes:true}).flatMap(e=>e.isSymbolicLink()||/^(?:__pycache__|node_modules|\.venv|archive|delivery-history)$/.test(e.name)?[]:e.isDirectory()?walk(dir+'/'+e.name):[dir+'/'+e.name]);
const ownRoots=[base,`motion-canvas/src/projects/${slug}`,`production/batches/sakurai-planning-game-design/proof-${slug}`];
const ownText=f=>/\.(?:json|md|py|cjs|ps1|tsx?|meta|ass|srt)$/i.test(f)||/\/(?:description[^/]*|pinned-comment\.ko|[^/]+\.ax)\.txt$/.test(f);
const forbidden=f=>/\.(?:log|pyc|mp4|m4a|wav|aac|mp3|webm|mkv|zip|7z|gz|png|jpe?g|webp|gif|bmp|tiff?)$/i.test(f)||/\.info\.json$|raw-original|research.*(?:transcript|subtitle)|source.*(?:\.ja\.srt|\.ja\.txt)/i.test(f);
const thumb=`${base}/publishing/thumbnail-v1.png`;
if(process.argv.includes('--prepare')){
 const images=read('shared/git-essential-images.json').entries.filter(e=>e.project===slug&&['delivery-thumbnail','minimal-publishing-proof'].includes(e.purpose));
 if(!images.some(e=>e.path===thumb))throw Error('The individually reviewed delivery thumbnail is not registered');
 for(const e of images){if(!e.path.startsWith(base+'/publishing/')||e.sha256!==sha(fs.readFileSync(path.join(root,e.path))))throw Error('Unexpected/unreviewed essential image '+e.path);}
 const selected=[...new Set([...ownRoots.flatMap(walk).filter(f=>ownText(f)&&!forbidden(f)),...images.map(e=>e.path),planPath,
 'production/batches/sakurai-planning-game-design/queue.json','production/batches/sakurai-planning-game-design/README.md',`production/batches/sakurai-planning-game-design/preflight/${slug}.json`])].filter(f=>f!==proofPath).sort();
 const plan={schemaVersion:1,slug,preparedAt:new Date().toISOString(),actualHeadAtPreparation:git(['rev-parse','HEAD']),status:'explicit-path-plan-only-no-commit',selectedPaths:selected,essentialImages:images.map(e=>e.path),sharedPaths:['AGENTS.md','.gitignore','shared/git-essential-images.json'],sharedMerge:'Actual HEAD plus only the GPU reaffirmation and individually reviewed player-customization image entries; foreign shared edits stay in the working tree/index.',excluded:'All media, archives, logs, pycache, raw info, whole original research subtitles and source/contact/render/caption QA rasters remain local.'};
 fs.writeFileSync(path.join(root,planPath),JSON.stringify(plan,null,2)+'\n');
 console.log(JSON.stringify({prepared:true,paths:selected.length,images:plan.essentialImages,commit:false}));process.exit(0);
}
if(!process.argv.includes('--stage-only')&&!process.argv.includes('--deliver'))throw Error('Choose an explicit mode');
const receipt=read(`${base}/publishing/youtube-upload-v1.json`);
if(!receipt.uploaded||!receipt.privateSaveVerified||!receipt.platformAutomaticChecksComplete||!receipt.burnedCaptionPixelsVerified||!receipt.availableSettingsVerified)throw Error('Actual current private save, automatic checks, settings and CC-off gameplay/2.5D pixels must be verified before staging');
const execution=read(`${base}/publishing/private-upload-execution-v1.json`),seal=read(`${base}/production/final-v1/final-pixel-direct-review-v1.json`);
if(receipt.videoId!==execution.actualVideoId||execution.uploadCountThisAttempt!==1||receipt.captionedSha256!==seal.sourceSha256)throw Error('Private receipt is not for the single reviewed current upload');
if(!seal.allFinalPixelsReviewed)throw Error('Final pixel seal missing');
const plan=read(planPath),files=plan.selectedPaths;
if(plan.slug!==slug||!files.includes(thumb)||files.some(f=>!ownRoots.some(d=>f.startsWith(d+'/'))&&!['production/batches/sakurai-planning-game-design/queue.json','production/batches/sakurai-planning-game-design/README.md',`production/batches/sakurai-planning-game-design/preflight/${slug}.json`].includes(f)))throw Error('Unexpected explicit path');
const images=read('shared/git-essential-images.json').entries.filter(e=>plan.essentialImages.includes(e.path));
if(images.length!==plan.essentialImages.length)throw Error('Essential image record missing');
for(const e of images)if(e.sha256!==sha(fs.readFileSync(path.join(root,e.path))))throw Error('Essential image changed');
const memory=fs.readFileSync(path.join(root,'AGENTS.md'),'utf8').split(/\r?\n/).find(l=>l.startsWith('- GPU handoff for narration,'));
if(!memory?.includes('멈추면 작업끝나면 다시 원래 연구작업은 재게해줘'))throw Error('User GPU restoration memory missing');
const special=plan.sharedPaths;
function mergeOwn(file,text){
 if(file==='AGENTS.md'){const lines=text.split(/\r?\n/),i=lines.findIndex(l=>l.startsWith('- GPU handoff for narration,'));if(i<0)throw Error('Actual HEAD GPU policy missing');lines[i]=memory;return lines.join('\n');}
 if(file==='.gitignore'){let t=text.trimEnd();for(const e of images)if(!t.split(/\r?\n/).includes('!'+e.path))t+='\n!'+e.path;return t+'\n';}
 const j=JSON.parse(text);for(const e of images){const old=j.entries.find(x=>x.path===e.path);if(old&&old.sha256!==e.sha256)throw Error('Conflicting essential image');if(!old)j.entries.push(e);}return JSON.stringify(j,null,2)+'\n';
}
const parent=git(['rev-parse','HEAD']),indexBefore=git(['ls-files','--stage','-z']);
const stagedBefore=git(['diff','--cached','--name-only','-z']).split('\0').filter(Boolean);
if(stagedBefore.some(f=>files.includes(f)))throw Error('An explicit video path already has staged changes; do not overwrite them');
const initialSpecial=Object.fromEntries(special.map(f=>[f,git(['show',':'+f])]));
const dir=fs.mkdtempSync(path.join(root,'.git','player-customization-delivery-')),env={...process.env,GIT_INDEX_FILE:path.join(dir,'index')};
git(['read-tree',parent],env);
for(let i=0;i<files.length;i+=15)git(['add','--',...files.slice(i,i+15)],env);
const expectedSpecial={};for(const f of special){expectedSpecial[f]=git(['hash-object','-w','--stdin'],env,mergeOwn(f,git(['show',parent+':'+f])));git(['update-index','--add','--cacheinfo','100644',expectedSpecial[f],f],env);}
const diff=git(['diff','--cached','--name-status','-z',parent],env).split('\0').filter(Boolean),rows=[];for(let i=0;i<diff.length;i+=2)rows.push({status:diff[i],path:diff[i+1]});
const allowed=new Set([...files,...special]);if(rows.some(r=>!allowed.has(r.path)||r.status==='D'))throw Error('Unexpected path or deletion');
for(const f of files)if(git(['rev-parse',':'+f],env)!==git(['hash-object','--path='+f,f]))throw Error('Staged source changed '+f);
for(const f of special)if(git(['rev-parse',':'+f],env)!==expectedSpecial[f])throw Error('Owned shared blob differs '+f);
git(['diff','--cached','--check',parent],env);
console.log(run(process.execPath,['scripts/media-policy.cjs'],env));console.log(run(process.execPath,['scripts/build-rebuild-manifests.cjs',slug,'--check'],env));
if(git(['rev-parse','HEAD'])!==parent||git(['ls-files','--stage','-z'])!==indexBefore)throw Error('Concurrent HEAD/index changed; retain files and start from the actual new HEAD');
const proof={schemaVersion:1,slug,parent,temporaryIndex:env.GIT_INDEX_FILE,selectedPaths:files,stagedPaths:rows,ownedSharedBlobs:expectedSpecial,allFinalStagedBlobsVerified:true,mediaCheck:true,scopedRebuildCheck:true,whitespaceCheck:true,externalIndexUnchangedBeforeCommit:true,essentialRasterPaths:plan.essentialImages,recordedAt:new Date().toISOString(),pushed:false};
fs.writeFileSync(path.join(dir,'external-index-before.txt'),indexBefore);
fs.writeFileSync(path.join(dir,'owned-shared-index-before.json'),JSON.stringify(initialSpecial,null,2)+'\n');
if(process.argv.includes('--stage-only')){fs.writeFileSync(path.join(dir,'verified-stage.json'),JSON.stringify(proof,null,2)+'\n');console.log(JSON.stringify({stageOnly:true,paths:rows.length,index:env.GIT_INDEX_FILE}));process.exit(0);}
const tree=git(['write-tree'],env),commit=git(['commit-tree',tree,'-p',parent],env,'Deliver reviewed player customization and private upload\n');git(['update-ref','HEAD',commit,parent]);
Object.assign(proof,{commit,indexSynchronizationPending:true});fs.writeFileSync(path.join(root,proofPath),JSON.stringify(proof,null,2)+'\n');
const ownChanged=rows.filter(r=>!special.includes(r.path)).map(r=>r.path);for(let i=0;i<ownChanged.length;i+=15)git(['restore','--staged','--source='+commit,'--',...ownChanged.slice(i,i+15)]);
for(const f of special){const blob=git(['hash-object','-w','--stdin'],process.env,mergeOwn(f,initialSpecial[f]));git(['update-index','--add','--cacheinfo','100644',blob,f]);}
const foreignEntries=t=>t.split('\0').filter(Boolean).filter(line=>!allowed.has(line.split('\t')[1])).join('\0');
if(foreignEntries(git(['ls-files','--stage','-z']))!==foreignEntries(indexBefore))throw Error('Unrelated index entries changed');
Object.assign(proof,{commit,indexSynchronizationPending:false,unrelatedIndexEntriesPreserved:true,ownIndexPathsSynchronized:true});fs.writeFileSync(path.join(root,proofPath),JSON.stringify(proof,null,2)+'\n');
try{git(['push','origin',commit+':refs/heads/main']);}catch(e){proof.pushFailure={at:new Date().toISOString(),message:e.message};fs.writeFileSync(path.join(root,proofPath),JSON.stringify(proof,null,2)+'\n');throw e;}
const local=git(['rev-parse','HEAD']),remote=git(['ls-remote','origin','refs/heads/main']).split(/\s/)[0];if(local!==commit||remote!==commit)throw Error('Verify actual newer HEAD/remote before final delivery claim');
for(const r of rows)if(git(['rev-parse',remote+':'+r.path])!==git(['rev-parse',':'+r.path],env))throw Error('Final remote blob differs '+r.path);
Object.assign(proof,{localCommit:local,remoteCommit:remote,pushed:true,exactLocalRemoteMatch:true,allRemoteBlobsVerified:true,verifiedAt:new Date().toISOString()});fs.writeFileSync(path.join(root,proofPath),JSON.stringify(proof,null,2)+'\n');console.log(JSON.stringify({commit,remote,paths:rows.length,essentialImages:plan.essentialImages,pushed:true}));
