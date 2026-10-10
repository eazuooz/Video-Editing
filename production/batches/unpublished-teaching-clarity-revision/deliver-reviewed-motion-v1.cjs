// Deliver only explicit reviewed motion paths. Never write the shared Git index.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),slug='motion-sickness-games';
const rev=`projects/${slug}/production/revision-teaching-clarity-v1`,pub=rev+'/publishing';
const bin='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe';
const normal={...process.env,PATH:path.dirname(bin)+path.delimiter+process.env.PATH};
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8').replace(/^\uFEFF/,''));
const save=(f,o)=>fs.writeFileSync(path.join(root,f),JSON.stringify(o,null,2)+'\n');
function run(exe,args,env=normal,input){const r=cp.spawnSync(exe,args,{cwd:root,env,input,encoding:'utf8',windowsHide:true,maxBuffer:256e6});if(r.status!==0)throw Error(args.join(' ')+'\n'+r.stdout+'\n'+r.stderr);return r.stdout.trimEnd();}
const git=(args,env=normal,input)=>run(bin,args,env,input);
const selection=read(pub+'/git-source-selection-v1.json'),receipt=read(pub+'/youtube-upload-v1.json');
if(!receipt.actualVideoId||receipt.actualVideoId!==selection.actualVideoId||!receipt.uploaded||!receipt.privateSaveVerified||!receipt.fullSettingsVerified||!receipt.automaticChecksPassed||!receipt.burnedCaptionPixelsVerified)throw Error('Actual completed private publishing required');
const pixels=read(rev+'/final-pixel-direct-review-v1.json'),flow=read(rev+'/final-flow-playback-direct-review-v1.json'),collection=read(rev+'/collection-private-preflight-v1.json');
if(!pixels.allListedSamplesDirectlyRead||!pixels.allFinalCueCutPixelsApproved||pixels.unresolved.length||pixels.sourceSha256!==receipt.sourceSha256||!flow.wholeNormalSpeedPlaybackReachedEnd||!flow.sampledContinuousFlowApproved||flow.unresolved.length||!collection.sourceAndOutputAllFourHashesEqual||collection.actualCollectExitCode!==0)throw Error('Current direct media/collection reviews required');
const files=selection.selectedPaths,shared=selection.sharedOwnedOnlyPaths,images=selection.reviewedEssentialImages;
if(new Set(files).size!==files.length)throw Error('Duplicate selected path');
for(const f of files){
 const own=f.startsWith(rev+'/')||f.startsWith('motion-canvas/src/projects/motion-sickness-games/teaching-clarity-v1/')||f.startsWith('production/batches/unpublished-teaching-clarity-revision/')&&(path.basename(f).includes('motion')||['queue.json','README.md'].includes(path.basename(f)))||[`projects/${slug}/project.json`,`projects/${slug}/planning/outline.md`,`projects/${slug}/production/qa.json`,`projects/${slug}/production/delivery-output.json`,`projects/${slug}/rebuild.json`,'motion-canvas/vite.motion-sickness-games.config.ts','motion-canvas/tsconfig.motion-sickness-games.json','production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json'].includes(f);
 if(!own||/\.(mp4|wav|m4a|aac|mp3|webm|mkv|zip|7z|gz|info\.json)$/i.test(f)||/\.ax\.txt$/.test(f))throw Error('Foreign/media selection '+f);
 if(/\.(png|jpe?g|gif|webp|bmp|tiff?)$/i.test(f)&&!images.some(e=>e.path===f))throw Error('Unreviewed image '+f);
}
for(const e of images)if(e.purpose!=='minimal-publishing-proof'||!e.reason||!e.reviewedAt||sha(fs.readFileSync(path.join(root,e.path)))!==e.sha256)throw Error('Essential image changed');
const planPath=pub+'/git-stage-paths-v1.json',proofPath=pub+'/private-delivery-git-verification-v1.json';
if(process.argv.includes('--prepare')){save(planPath,{schemaVersion:1,preparedAt:new Date().toISOString(),actualVideoId:receipt.actualVideoId,selectedPaths:files,sharedOwnedOnlyPaths:shared,reviewedEssentialImages:images,staged:false,committed:false});console.log(JSON.stringify({prepared:true,paths:files.length+shared.length}));process.exit(0);}
if(!process.argv.includes('--stage-only')&&!process.argv.includes('--deliver'))throw Error('Choose --prepare, --stage-only or --deliver');
const plan=read(planPath);if(JSON.stringify(plan.selectedPaths)!==JSON.stringify(files))throw Error('Selection changed');
run(process.execPath,['scripts/review-video-duplicates.cjs',slug,'--check']);
const parent=git(['rev-parse','HEAD']),external=path.resolve(root,git(['rev-parse','--git-path','index']));
const bytes=fs.readFileSync(external),entries=git(['ls-files','--stage','-z']);
const temporary=fs.mkdtempSync(path.join(root,'.git','motion-teaching-v1-')),env={...normal,GIT_INDEX_FILE:path.join(temporary,'index')};
function unchanged(){if(sha(fs.readFileSync(external))!==sha(bytes)||git(['ls-files','--stage','-z'])!==entries)throw Error('External index changed; preserve and inspect');}
git(['read-tree',parent],env);
function walk(dir){if(!fs.existsSync(path.join(root,dir)))return[];return fs.readdirSync(path.join(root,dir),{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name)).flatMap(e=>{if(e.isSymbolicLink()||/^(node_modules|\.git|\.venv|delivery-history|delivery-stage-.*|media.*|chunks|__pycache__)$/.test(e.name))return[];const f=dir+'/'+e.name;return e.isDirectory()?walk(f):[f];});}
const slugs=fs.readdirSync(path.join(root,'projects')).filter(s=>fs.existsSync(path.join(root,'projects',s,'project.json'))).sort();
const rebuildFiles=[...new Set([...git(['ls-files','--cached','--others','--exclude-standard','-z'],env).split('\0').filter(Boolean),...slugs.flatMap(s=>walk('projects/'+s)),...slugs.flatMap(s=>walk('motion-canvas/src/projects/'+s))])].filter(f=>fs.existsSync(path.join(root,f))).sort();
save(`projects/${slug}/rebuild.json`,require(path.join(root,'scripts/build-rebuild-manifests.cjs')).build(slug,rebuildFiles));
for(let i=0;i<files.length;i+=15)git(['add','--',...files.slice(i,i+15)],env);
const sharedBlobs={};for(const f of shared){
 let text=git(['show',parent+':'+f]);
 if(f==='shared/git-essential-images.json'){const registry=JSON.parse(text);for(const e of images){if(!registry.allowedPurposes.includes(e.purpose))throw Error('Purpose schema');const old=registry.entries.find(x=>x.path===e.path);if(old&&old.sha256!==e.sha256)throw Error('Image registry conflict');if(!old)registry.entries.push(e);}text=JSON.stringify(registry,null,2)+'\n';}
 else if(f==='.gitignore'){for(const e of images)if(!text.split(/\r?\n/).includes('!'+e.path))text+='\n!'+e.path+'\n';}
 else throw Error('Unowned shared path');
 const blob=git(['hash-object','-w','--stdin'],env,text);git(['update-index','--add','--cacheinfo','100644',blob,f],env);sharedBlobs[f]=blob;
}
const allowed=new Set([...files,...shared]),raw=git(['diff','--cached','--name-status','-z',parent],env).split('\0').filter(Boolean),changes=[];
for(let i=0;i<raw.length;i+=2)changes.push({status:raw[i],path:raw[i+1]});
if(changes.some(e=>!allowed.has(e.path)||!['A','M'].includes(e.status)))throw Error('Foreign path/deletion');
const staged=new Map(git(['ls-files','--stage','-z'],env).split('\0').filter(Boolean).map(l=>{const[m,f]=l.split('\t');return[f,m.split(' ')[1]];}));
const blobs=git(['hash-object','--stdin-paths'],env,files.join('\n')+'\n').split(/\r?\n/);
files.forEach((f,i)=>{if(staged.get(f)!==blobs[i])throw Error('Staged bytes differ '+f);});shared.forEach(f=>{if(staged.get(f)!==sharedBlobs[f])throw Error('Owned merge differs');});
const checks={whitespace:git(['diff','--cached','--check',parent],env),media:run(process.execPath,['scripts/media-policy.cjs'],env),currentMotionRebuild:run(process.execPath,['scripts/build-rebuild-manifests.cjs',slug,'--check'],env)};
unchanged();if(git(['rev-parse','HEAD'])!==parent)throw Error('HEAD advanced; no commit');
const proof={schemaVersion:1,slug,actualVideoId:receipt.actualVideoId,parent,selectedPaths:files,ownedSharedPaths:shared,changedPaths:changes,checks,temporaryIndex:env.GIT_INDEX_FILE,allStagedBlobsVerified:true,externalIndexSha256Before:sha(bytes),externalIndexUnchanged:true,reviewedEssentialImages:images,mediaAdded:0,recordedAt:new Date().toISOString(),pushed:false};
fs.writeFileSync(path.join(temporary,'external-index-before.bin'),bytes);fs.writeFileSync(path.join(temporary,'stage-verification.json'),JSON.stringify(proof,null,2)+'\n');
if(process.argv.includes('--stage-only')){console.log(JSON.stringify({stageOnly:true,paths:allowed.size,changes:changes.length,checks}));process.exit(0);}
const tree=git(['write-tree'],env),commit=git(['commit-tree',tree,'-p',parent],env,'Deliver motion-sickness lesson with clear opening and tracked gameplay explanations\n');
unchanged();git(['update-ref','HEAD',commit,parent]);proof.commit=commit;save(proofPath,proof);
try{git(['push','origin',commit+':refs/heads/main']);}catch(e){proof.pushFailure=e.message;save(proofPath,proof);throw e;}
const local=git(['rev-parse','HEAD']),remote=git(['ls-remote','origin','refs/heads/main']).split(/\s/)[0];if(local!==commit||remote!==commit)throw Error('Concurrent local/remote advance; preserve commit');
const final=new Map(git(['ls-tree','-r','-z',remote]).split('\0').filter(Boolean).map(l=>{const[m,f]=l.split('\t');return[f,m.split(' ')[2]];}));
for(const f of allowed)if(final.get(f)!==staged.get(f))throw Error('Final blob differs '+f);
unchanged();Object.assign(proof,{pushed:true,localCommit:local,remoteCommit:remote,exactLocalRemoteMatch:true,allFinalRemoteBlobsVerified:true,verifiedBlobCount:allowed.size,externalIndexSha256After:sha(fs.readFileSync(external)),verifiedAt:new Date().toISOString()});save(proofPath,proof);
console.log(JSON.stringify({commit,remote,verifiedBlobs:allowed.size,mediaAdded:0,essentialImages:images.length,externalIndexUnchanged:true,pushed:true}));
