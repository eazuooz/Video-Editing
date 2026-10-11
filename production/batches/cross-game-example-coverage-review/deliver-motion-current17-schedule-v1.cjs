// Deliver only observed scheduling follow-up through an isolated index. No media workers.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..');
const B='production/batches/cross-game-example-coverage-review';
const R='projects/motion-sickness-games/production/revision-cross-game-four-v1';
const bin='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe';
const normal={...process.env,PATH:path.dirname(bin)+path.delimiter+process.env.PATH};
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8').replace(/^\uFEFF/,''));
const save=(f,v)=>{const p=path.join(root,f),t=p+'.delivery-'+process.pid+'.tmp';fs.writeFileSync(t,JSON.stringify(v,null,2)+'\n',{flag:'wx'});fs.renameSync(t,p);};
function run(exe,args,env=normal,input){const r=cp.spawnSync(exe,args,{cwd:root,env,input,encoding:'utf8',windowsHide:true,maxBuffer:256e6});if(r.status!==0)throw Error(args.join(' ')+'\n'+r.stdout+'\n'+r.stderr);return r.stdout.trimEnd();}
const git=(a,e=normal,i)=>run(bin,a,e,i);
const files=[
  "production/batches/cross-game-example-coverage-review/seal-motion-current17-schedule-v1.py",
  "production/batches/cross-game-example-coverage-review/deliver-motion-current17-schedule-v1.cjs",
  "production/batches/cross-game-example-coverage-review/queue.json",
  "projects/motion-sickness-games/production/revision-cross-game-four-v1/current17-main-schedule-update-v1.json",
  "projects/motion-sickness-games/production/revision-cross-game-four-v1/publishing/schedule-direct-review-v1.json",
  "projects/motion-sickness-games/production/revision-cross-game-four-v1/publishing/schedule-ledger-update-v1.json",
  "projects/motion-sickness-games/production/revision-cross-game-four-v1/publishing/production-git-verification-v1.json",
  "projects/motion-sickness-games/production/revision-cross-game-four-v1/publishing/youtube-upload-v1.json",
  "projects/motion-sickness-games/production/revision-cross-game-four-v1/latest-checkpoint.json",
  "projects/motion-sickness-games/project.json",
  "projects/motion-sickness-games/rebuild.json",
  "shared/publishing/daily-alternating-schedule.json"
].sort();
const missing=files.filter(f=>!fs.existsSync(path.join(root,f)));
if(missing.length)throw Error('Missing explicit paths: '+JSON.stringify(missing));
if(process.argv.includes('--plan')){console.log(JSON.stringify(files.map(f=>({path:f,bytes:fs.statSync(path.join(root,f)).size})),null,2));process.exit(0);}
if(!process.argv.includes('--deliver'))throw Error('Use --plan or --deliver');
const proofPath=R+'/publishing/schedule-git-verification-v1.json';
if(fs.existsSync(path.join(root,proofPath)))throw Error('Existing delivery proof: inspect, never duplicate');
const settings=read(R+'/publishing/private-settings-direct-review-v1.json');
if(!settings.privateSavedAndReopened||!settings.fullAvailableSettingsVerified||settings.actualVideoId!=='lXjDBqONLWs')throw Error('Verified actual private settings required');
const promotion=read(R+'/current17-main-promotion-v1.json');
for(const row of promotion.otherProtectedInputs)if(sha(fs.readFileSync(path.join(root,row.path)))!==row.sha256)throw Error('Protected input changed '+row.path);
const schedule=read(R+'/publishing/schedule-direct-review-v1.json');
if(!schedule.savedAndReopened||!schedule.futureScheduledListVerified||schedule.actualVideoId!=='lXjDBqONLWs')throw Error('Actual saved/reopened schedule required');
const agentsBefore=sha(fs.readFileSync(path.join(root,'AGENTS.md')));
const parent=git(['rev-parse','HEAD']),branch=git(['symbolic-ref','--short','HEAD']);
const external=path.resolve(root,git(['rev-parse','--git-path','index']));
const bytes=fs.readFileSync(external),entries=git(['ls-files','--stage','-z']);
const temp=fs.mkdtempSync(path.join(root,'.git','motion-current17-schedule-'));
const env={...normal,GIT_INDEX_FILE:path.join(temp,'index')};
fs.writeFileSync(path.join(temp,'external-index-before.bin'),bytes);
fs.writeFileSync(path.join(temp,'external-index-before.entries'),entries);
function unchanged(){if(sha(fs.readFileSync(external))!==sha(bytes)||git(['ls-files','--stage','-z'])!==entries)throw Error('External index changed; preserve it');if(sha(fs.readFileSync(path.join(root,'AGENTS.md')))!==agentsBefore)throw Error('AGENTS bytes changed');}
git(['read-tree',parent],env);
function walk(dir){return fs.readdirSync(path.join(root,dir),{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name)).flatMap(e=>{if(e.isSymbolicLink()||/^(node_modules|\.git|\.venv|delivery-history|delivery-stage-.*|media.*|chunks)$/.test(e.name))return[];const f=dir+'/'+e.name;return e.isDirectory()?walk(f):[f];});}
const slugs=fs.readdirSync(path.join(root,'projects')).filter(s=>fs.existsSync(path.join(root,'projects',s,'project.json'))).sort();
const inventory=[...new Set([...git(['ls-files','--cached','--others','--exclude-standard','-z'],env).split('\0').filter(Boolean),...slugs.flatMap(s=>walk('projects/'+s)),...slugs.flatMap(s=>fs.existsSync(path.join(root,'motion-canvas/src/projects/'+s))?walk('motion-canvas/src/projects/'+s):[])])].filter(f=>fs.existsSync(path.join(root,f))).sort();
save('projects/motion-sickness-games/rebuild.json',require(path.join(root,'scripts/build-rebuild-manifests.cjs')).build('motion-sickness-games',inventory));
git(['add','--',...files],env);
const raw=git(['diff','--cached','--name-status','-z',parent],env).split('\0').filter(Boolean),changes=[];
for(let i=0;i<raw.length;i+=2)changes.push({status:raw[i],path:raw[i+1]});
if(changes.some(e=>!files.includes(e.path)||!['A','M'].includes(e.status)))throw Error('Foreign path or deletion');
if(files.some(f=>/\.(mp4|webm|wav|mp3|m4a|ogg|flac|zip|png|jpe?g|gif|webp)$/i.test(f)))throw Error('Media/image selected');
const staged=new Map(git(['ls-files','--stage','-z'],env).split('\0').filter(Boolean).map(l=>{const[m,f]=l.split('\t');return[f,m.split(' ')[1]];}));
const blobs=git(['hash-object','--stdin-paths'],env,files.join('\n')+'\n').split(/\r?\n/);
files.forEach((f,i)=>{if(staged.get(f)!==blobs[i])throw Error('Staged bytes differ '+f);});
const checks={whitespace:git(['diff','--cached','--check',parent],env),media:run(process.execPath,['scripts/media-policy.cjs'],env),
 currentMotionRebuild:run(process.execPath,['scripts/build-rebuild-manifests.cjs','motion-sickness-games','--check'],env)};
unchanged();if(git(['rev-parse','HEAD'])!==parent)throw Error('HEAD advanced: no commit');
const tree=git(['write-tree'],env),commit=git(['commit-tree',tree,'-p',parent],env,'Verify four-game camera lesson replacement schedule at 09:00 Seoul\n');
const proof={schemaVersion:1,actualVideoId:'lXjDBqONLWs',parent,branch,commit,selectedPaths:files,changedPaths:changes,checks,
 mediaAdded:0,newImagesAdded:0,allStagedBlobsVerified:true,externalIndexSha256Before:sha(bytes),
 agentsSha256Before:agentsBefore,externalIndexUnchanged:true,recordedAt:new Date().toISOString(),pushed:false};
unchanged();git(['update-ref','HEAD',commit,parent]);save(proofPath,proof);
try{git(['push','origin',commit+':refs/heads/'+branch]);}catch(e){proof.pushFailure=e.message;save(proofPath,proof);throw e;}
const local=git(['rev-parse','HEAD']),remote=git(['ls-remote','origin','refs/heads/'+branch]).split(/\s/)[0];
if(local!==commit||remote!==commit)throw Error('Concurrent local/remote advance; inspect saved commit');
const final=new Map(git(['ls-tree','-r','-z',remote]).split('\0').filter(Boolean).map(l=>{const[m,f]=l.split('\t');return[f,m.split(' ')[2]];}));
for(const f of files)if(final.get(f)!==staged.get(f))throw Error('Final blob differs '+f);
unchanged();Object.assign(proof,{pushed:true,localCommit:local,remoteCommit:remote,exactLocalRemoteMatch:true,
 allFinalRemoteBlobsVerified:true,verifiedBlobCount:files.length,externalIndexSha256After:sha(fs.readFileSync(external)),
 agentsSha256After:sha(fs.readFileSync(path.join(root,'AGENTS.md'))),verifiedAt:new Date().toISOString()});save(proofPath,proof);
console.log(JSON.stringify({commit,remote,verifiedBlobs:files.length,newImages:0,media:0,externalIndexUnchanged:true,pushed:true}));
