// Usage: node production/batches/visual-depth-revision/deliver-reviewed-source.cjs <slug> [--stage-only]
// Explicit source paths, isolated index, guarded HEAD and normal push. No media/QA images.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),slug=process.argv[2];
const scope=['picking-sides','motion-sickness-games','hierarchical-game-outlines','game-reward-planning','avoid-game-comparisons','making-game-sequels','familiar-game-rules'];
if(!scope.includes(slug))throw Error('Outside the authorized seven-video revision');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8').replace(/^\uFEFF/,''));
const run=(cmd,args,env=process.env,input)=>{const r=cp.spawnSync(cmd,args,{cwd:root,env,input,encoding:'utf8',windowsHide:true,maxBuffer:128e6});if(r.status!==0)throw Error(cmd+' '+args.join(' ')+'\n'+r.stdout+'\n'+r.stderr);return r.stdout.trimEnd();};
const git=(args,env,input)=>run('git',args,env,input);
const receipt=read(`projects/${slug}/publishing/youtube-upload-depth-v1.json`);
if(!receipt.uploaded||!receipt.privateSaveVerified||!receipt.settingsExceptAutomaticChecksVerified||!receipt.burnedCaptionPixelsVerified)throw Error('Current private replacement and available settings must be actually verified first');
if(!read(`projects/${slug}/production/visual-depth-v1/encoded-pixel-direct-review.json`).allFinalPixelsReviewed)throw Error('Current final pixels are not approved');
const thumb=`projects/${slug}/publishing/thumbnail-depth-v1.png`,exception='!'+thumb;
const image=read('shared/git-essential-images.json').entries.find(e=>e.path===thumb);
if(!image||image.purpose!=='delivery-thumbnail'||image.sha256!==sha(fs.readFileSync(path.join(root,thumb))))throw Error('The exact directly reviewed delivery thumbnail is not registered');
const batch='production/batches/visual-depth-revision';
const top=(dir,pattern)=>fs.readdirSync(path.join(root,dir),{withFileTypes:true}).filter(e=>e.isFile()&&pattern.test(e.name)).map(e=>dir+'/'+e.name);
const files=[...top(batch,/\.(?:py|cjs|md|json)$/),...top(`projects/${slug}/production/visual-depth-v1`,/\.(?:json|ax\.txt)$/),
 ...top(`motion-canvas/src/projects/${slug}`,/^depth.*\.(?:tsx?|json|html)$/),...top(`motion-canvas/src/projects/${slug}/scenes`,/^depth.*\.tsx$/),
 `projects/${slug}/project.json`,`projects/${slug}/rebuild.json`,`projects/${slug}/production/delivery-output.json`,
 `projects/${slug}/publishing/thumbnail-depth-v1.json`,`projects/${slug}/publishing/youtube-upload-depth-v1.json`,thumb,
 'motion-canvas/src/shared/depth-diagrams.tsx','docs/VIDEO_25D_THUMBNAIL_REVIEW.md','docs/VIDEO_VISUAL_STYLE.md'];
const special=['AGENTS.md','.gitignore','shared/git-essential-images.json'];
const memory=fs.readFileSync(path.join(root,'AGENTS.md'),'utf8').split(/\r?\n/).find(l=>l.startsWith('- 2.5D and thumbnail correction,'));
if(!memory)throw Error('Requested production memory missing');
function mergeOwn(file,text){
 if(file==='AGENTS.md')return text.includes(memory)?text:text.replace('# Video production defaults\n','# Video production defaults\n\n'+memory+'\n');
 if(file==='.gitignore')return text.split(/\r?\n/).includes(exception)?text:text.trimEnd()+'\n'+exception+'\n';
 const j=JSON.parse(text),old=j.entries.find(e=>e.path===thumb);if(old&&old.sha256!==image.sha256)throw Error('Conflicting thumbnail review');if(!old)j.entries.push(image);return JSON.stringify(j,null,2)+'\n';
}
const parent=git(['rev-parse','HEAD']);
const sharedEntriesBefore=git(['ls-files','--stage','-z']);
const stagedBefore=git(['diff','--cached','--name-only','-z']).split('\0').filter(Boolean);
const allowed=new Set([...files,...special]);
if(stagedBefore.some(f=>files.includes(f)))throw Error('One of the explicit video paths already has staged work; preserve it for manual reconciliation');
const initialSpecial=Object.fromEntries(special.map(f=>[f,git(['show',':'+f])]));
const dir=fs.mkdtempSync(path.join(root,'.git','depth-delivery-'));
const env={...process.env,GIT_INDEX_FILE:path.join(dir,'index')};
git(['read-tree',parent],env);
for(let i=0;i<files.length;i+=15)git(['add','--',...files.slice(i,i+15)],env);
for(const file of special){const blob=git(['hash-object','-w','--stdin'],env,mergeOwn(file,git(['show',parent+':'+file])));git(['update-index','--add','--cacheinfo','100644',blob,file],env);}
const changes=git(['diff','--cached','--name-status','-z',parent],env).split('\0').filter(Boolean),rows=[];
for(let i=0;i<changes.length;i+=2)rows.push({status:changes[i],path:changes[i+1]});
if(rows.some(r=>!allowed.has(r.path)||r.status==='D'))throw Error('Unexpected staged path/deletion');
for(const file of files){const actual=git(['rev-parse',':'+file],env),expected=git(['hash-object','--path='+file,file]);if(actual!==expected)throw Error('Staged source changed after selection: '+file);}
git(['diff','--cached','--check',parent],env);
console.log(run(process.execPath,['scripts/media-policy.cjs'],env));
console.log(run(process.execPath,['scripts/build-rebuild-manifests.cjs',slug,'--check'],env));
if(git(['rev-parse','HEAD'])!==parent||git(['ls-files','--stage','-z'])!==sharedEntriesBefore)throw Error('Concurrent HEAD/index changed; restart from the actual checkpoint without discarding anything');
const proof={schemaVersion:1,slug,parent,selectedPaths:files,specialOwnMergedPaths:special,stagedPaths:rows,temporaryIndex:env.GIT_INDEX_FILE,mediaCheck:true,scopedRebuildCheck:true,stagedSourceBlobsVerified:true,externalIndexUnchangedBeforeCommit:true,essentialRasterPaths:[thumb],recordedAt:new Date().toISOString()};
if(process.argv.includes('--stage-only')){fs.writeFileSync(path.join(dir,'verified-stage.json'),JSON.stringify(proof,null,2)+'\n');console.log(JSON.stringify({stageOnly:true,files:rows.length,index:env.GIT_INDEX_FILE}));process.exit(0);}
const tree=git(['write-tree'],env),commit=git(['commit-tree',tree,'-p',parent],env,`Deliver reviewed 2.5D correction and private upload: ${slug}\n`);
git(['update-ref','HEAD',commit,parent]);
const ownChanged=rows.filter(r=>!special.includes(r.path)).map(r=>r.path);
for(let i=0;i<ownChanged.length;i+=15)git(['restore','--staged','--source='+commit,'--',...ownChanged.slice(i,i+15)]);
for(const file of special){const blob=git(['hash-object','-w','--stdin'],process.env,mergeOwn(file,initialSpecial[file]));git(['update-index','--add','--cacheinfo','100644',blob,file]);}
const foreignEntries=text=>text.split('\0').filter(Boolean).filter(line=>!allowed.has(line.split('\t')[1])).join('\0');
if(foreignEntries(git(['ls-files','--stage','-z']))!==foreignEntries(sharedEntriesBefore))throw Error('Unrelated shared index entries differ');
git(['push','origin',commit+':refs/heads/main']);
const local=git(['rev-parse','HEAD']),remote=git(['ls-remote','origin','refs/heads/main']).split(/\s/)[0];
if(local!==commit||remote!==commit)throw Error('Delivery commit exists but exact current local/remote equality needs renewed verification');
for(const row of rows)if(git(['rev-parse',remote+':'+row.path])!==git(['rev-parse',':'+row.path],env))throw Error('Remote blob mismatch: '+row.path);
Object.assign(proof,{commit,localCommit:local,remoteCommit:remote,pushed:true,exactLocalRemoteMatch:true,remoteBlobsVerified:true,unrelatedIndexEntriesPreserved:true,ownIndexPathsSynchronized:true});
fs.writeFileSync(path.join(root,batch,`git-delivery-${slug}.json`),JSON.stringify(proof,null,2)+'\n');
console.log(JSON.stringify({slug,commit,remote,files:rows.length,essentialRasterPaths:[thumb],pushed:true}));
