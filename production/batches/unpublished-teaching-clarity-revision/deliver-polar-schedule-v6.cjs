const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),batch='production/batches/unpublished-teaching-clarity-revision';
const rev='projects/game-math-polar-3d/revision-teaching-clarity-v1',pub=rev+'/publishing';
const bin='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe';
const normal={...process.env,PATH:path.dirname(bin)+path.delimiter+process.env.PATH};
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8').replace(/^\uFEFF/,''));
const save=(f,o)=>fs.writeFileSync(path.join(root,f),JSON.stringify(o,null,2)+'\n');
function run(command,args,env=normal,input){const r=cp.spawnSync(command,args,{cwd:root,env,input,encoding:'utf8',windowsHide:true,maxBuffer:256e6});if(r.status!==0)throw Error(args.join(' ')+'\n'+r.stdout+'\n'+r.stderr);return r.stdout.trimEnd();}
const git=(args,env=normal,input)=>run(bin,args,env,input);
const paths=[batch+'/queue.json',batch+'/README.md',batch+'/record-polar-schedule-v6.py',batch+'/deliver-polar-schedule-v6.cjs',
 pub+'/youtube-upload-v3.json',pub+'/private-delivery-git-verification-v3.json',pub+'/schedule-direct-review-v6.json',pub+'/final-handoff-v6.json',
 pub+'/schedule-before-actual-rows-v6.json',pub+'/schedule-after-actual-rows-v6.json',pub+'/schedule-reopened-proof-v6.png',
 'projects/game-math-polar-3d/rebuild.json'];
const shared=['shared/publishing/daily-alternating-schedule.json','shared/git-essential-images.json','.gitignore'];
const proofPath=pub+'/schedule-evidence-git-verification-v6.json';
const review=read(pub+'/schedule-direct-review-v6.json'),prod=read(pub+'/private-delivery-git-verification-v3.json');
if(!review.scheduleSavedAndReopened||!review.other23DatesAndTitlesUnchanged||!review.baselinePreservedPrivate||!prod.pushed||!prod.allRemoteBlobsVerified)throw Error('Current actual delivery required');
const images=review.reviewedEssentialImages;
for(const e of images)if(!e.reviewedAt||!e.reason||e.purpose!=='minimal-publishing-proof'||sha(fs.readFileSync(path.join(root,e.path)))!==e.sha256)throw Error('Image gate');
const head=git(['rev-parse','HEAD']);
const index=path.resolve(root,git(['rev-parse','--git-path','index']));
const bytes=fs.readFileSync(index),entries=git(['ls-files','--stage','-z']);
const temp=fs.mkdtempSync(path.join(root,'.git','polar-schedule-v6-'));
const env={...normal,GIT_INDEX_FILE:path.join(temp,'index')};
function unchanged(){if(sha(fs.readFileSync(index))!==sha(bytes)||git(['ls-files','--stage','-z'])!==entries)throw Error('External index changed; preserve it');}
git(['read-tree',head],env);
function walk(dir){if(!fs.existsSync(path.join(root,dir)))return[];return fs.readdirSync(path.join(root,dir),{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name)).flatMap(e=>{if(e.isSymbolicLink()||/^(node_modules|\.git|\.venv|delivery-history|delivery-stage-.*|media.*|chunks)$/.test(e.name))return[];const f=dir+'/'+e.name;return e.isDirectory()?walk(f):[f];});}
const slugs=fs.readdirSync(path.join(root,'projects')).filter(s=>fs.existsSync(path.join(root,'projects',s,'project.json'))).sort();
const all=[...new Set([...git(['ls-files','--cached','--others','--exclude-standard','-z'],env).split('\0').filter(Boolean),...slugs.flatMap(s=>walk('projects/'+s)),...slugs.flatMap(s=>walk('motion-canvas/src/projects/'+s))])].filter(f=>fs.existsSync(path.join(root,f))).sort();
save('projects/game-math-polar-3d/rebuild.json',require(path.join(root,'scripts/build-rebuild-manifests.cjs')).build('game-math-polar-3d',all));
git(['add','--',...paths],env);
const sharedBlobs={};
for(const f of shared){
 let text=git(['show',head+':'+f]);
 if(f.endsWith('daily-alternating-schedule.json')){
  const ledger=JSON.parse(text),current=read(f),replacement=current.actualSchedules.find(e=>e.slug==='game-math-polar-3d');
  const i=ledger.actualSchedules.findIndex(e=>e.slug==='game-math-polar-3d');
  if(i<0||ledger.actualSchedules[i].videoId!=='ZLOewk8JHXA'||replacement.videoId!=='2kNMDlrwdU8')throw Error('Current schedule conflicts');
  ledger.actualSchedules[i]=replacement;ledger.updatedAt=current.updatedAt;text=JSON.stringify(ledger,null,2)+'\n';
 }else if(f.endsWith('git-essential-images.json')){
  const registry=JSON.parse(text);for(const e of images){const old=registry.entries.find(x=>x.path===e.path);if(old&&old.sha256!==e.sha256)throw Error('Image registry conflict');if(!old)registry.entries.push(e);}text=JSON.stringify(registry,null,2)+'\n';
 }else{for(const e of images)if(!text.split(/\r?\n/).includes('!'+e.path))text+='\n!'+e.path+'\n';}
 const blob=git(['hash-object','-w','--stdin'],env,text);git(['update-index','--add','--cacheinfo','100644',blob,f],env);sharedBlobs[f]=blob;
}
const allowed=new Set([...paths,...shared]);
const raw=git(['diff','--cached','--name-status','-z',head],env).split('\0').filter(Boolean),changes=[];
for(let i=0;i<raw.length;i+=2)changes.push({status:raw[i],path:raw[i+1]});
if(changes.some(e=>!allowed.has(e.path)||!['A','M'].includes(e.status)))throw Error('Foreign path/deletion');
const staged=new Map(git(['ls-files','--stage','-z'],env).split('\0').filter(Boolean).map(l=>{const[m,f]=l.split('\t');return[f,m.split(' ')[1]];}));
const blobs=git(['hash-object','--stdin-paths'],env,paths.join('\n')+'\n').split(/\r?\n/);
paths.forEach((f,i)=>{if(staged.get(f)!==blobs[i])throw Error('Staged bytes differ '+f);});
shared.forEach(f=>{if(staged.get(f)!==sharedBlobs[f])throw Error('Owned merge differs '+f);});
const checks={whitespace:git(['diff','--cached','--check',head],env),media:run(process.execPath,['scripts/media-policy.cjs'],env),
 currentPolarRebuild:run(process.execPath,['scripts/build-rebuild-manifests.cjs','game-math-polar-3d','--check'],env)};
unchanged();if(git(['rev-parse','HEAD'])!==head)throw Error('HEAD advanced; no commit');
const proof={schemaVersion:6,actualVideoId:'2kNMDlrwdU8',parent:head,selectedPaths:paths,ownedSharedPaths:shared,changedPaths:changes,checks,
 temporaryIndex:env.GIT_INDEX_FILE,externalIndexSha256Before:sha(bytes),externalIndexUnchanged:true,allStagedBlobsVerified:true,
 reviewedEssentialImages:images,mediaAdded:0,recordedAt:new Date().toISOString(),pushed:false};
fs.writeFileSync(path.join(temp,'external-index-before.bin'),bytes);save(proofPath,proof);
if(process.argv.includes('--stage-only')){console.log(JSON.stringify({stageOnly:true,paths:allowed.size,changed:changes.length,checks}));process.exit(0);}
if(!process.argv.includes('--deliver'))throw Error('Choose --stage-only or --deliver');
const tree=git(['write-tree'],env),commit=git(['commit-tree',tree,'-p',head],env,'Verify polar replacement private settings and preserve October11 schedule\n');
unchanged();git(['update-ref','HEAD',commit,head]);proof.commit=commit;save(proofPath,proof);
try{git(['push','origin',commit+':refs/heads/main']);}catch(e){proof.pushFailure=e.message;save(proofPath,proof);throw e;}
const local=git(['rev-parse','HEAD']),remote=git(['ls-remote','origin','refs/heads/main']).split(/\s/)[0];
if(local!==commit||remote!==commit)throw Error('Local/remote advanced; preserve commit');
const final=new Map(git(['ls-tree','-r','-z',remote]).split('\0').filter(Boolean).map(l=>{const[m,f]=l.split('\t');return[f,m.split(' ')[2]];}));
for(const f of allowed)if(final.get(f)!==staged.get(f))throw Error('Final blob differs '+f);
unchanged();Object.assign(proof,{pushed:true,localCommit:local,remoteCommit:remote,exactLocalRemoteMatch:true,allFinalRemoteBlobsVerified:true,
 verifiedBlobCount:allowed.size,externalIndexSha256After:sha(fs.readFileSync(index)),verifiedAt:new Date().toISOString()});save(proofPath,proof);
console.log(JSON.stringify({commit,remote,selectedPaths:allowed.size,changed:changes.length,essentialImages:images.length,externalIndexUnchanged:true,pushed:true}));
