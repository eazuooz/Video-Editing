const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),batch='production/batches/unpublished-teaching-clarity-revision';
const rev='projects/motion-sickness-games/production/revision-teaching-clarity-v1',pub=rev+'/publishing';
const bin='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe';
const normal={...process.env,PATH:path.dirname(bin)+path.delimiter+process.env.PATH};
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8').replace(/^\uFEFF/,''));
const save=(f,o)=>{const t=path.join(root,f),tmp=t+'.motion-final-'+process.pid+'.tmp';fs.writeFileSync(tmp,JSON.stringify(o,null,2)+'\n',{flag:'wx'});fs.renameSync(tmp,t);};
function run(exe,args,env=normal,input){const r=cp.spawnSync(exe,args,{cwd:root,env,input,encoding:'utf8',windowsHide:true,maxBuffer:256e6});if(r.status!==0)throw Error(args.join(' ')+'\n'+r.stdout+'\n'+r.stderr);return r.stdout.trimEnd();}
const git=(a,e=normal,i)=>run(bin,a,e,i);
const proofPath=pub+'/final-handoff-git-verification-v1.json';
if(fs.existsSync(path.join(root,proofPath))&&read(proofPath).pushed)throw Error('Completed final delivery must not repeat');
const previous=read(pub+'/schedule-evidence-git-verification-v1.json'),handoff=read(pub+'/final-handoff-v1.json');
if(!previous.pushed||!previous.allFinalRemoteBlobsVerified||!handoff.scheduleEvidenceGitDelivered)throw Error('Actual previous delivery required');
const parent=git(['rev-parse','HEAD']),external=path.resolve(root,git(['rev-parse','--git-path','index']));
const bytes=fs.readFileSync(external),entries=git(['ls-files','--stage','-z']);
const temp=fs.mkdtempSync(path.join(root,'.git','motion-final-v1-')),env={...normal,GIT_INDEX_FILE:path.join(temp,'index')};
function unchanged(){if(sha(fs.readFileSync(external))!==sha(bytes)||git(['ls-files','--stage','-z'])!==entries)throw Error('External index changed; preserve it');}
git(['read-tree',parent],env);
function walk(dir){if(!fs.existsSync(path.join(root,dir)))return[];return fs.readdirSync(path.join(root,dir),{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name)).flatMap(e=>{if(e.isSymbolicLink()||/^(node_modules|\.git|\.venv|delivery-history|delivery-stage-.*|media.*|chunks|__pycache__)$/.test(e.name))return[];const f=dir+'/'+e.name;return e.isDirectory()?walk(f):[f];});}
const slugs=fs.readdirSync(path.join(root,'projects')).filter(s=>fs.existsSync(path.join(root,'projects',s,'project.json'))).sort();
const inventory=[...new Set([...git(['ls-files','--cached','--others','--exclude-standard','-z'],env).split('\0').filter(Boolean),...slugs.flatMap(s=>walk('projects/'+s)),...slugs.flatMap(s=>walk('motion-canvas/src/projects/'+s))])].filter(f=>fs.existsSync(path.join(root,f))).sort();
save('projects/motion-sickness-games/rebuild.json',require(path.join(root,'scripts/build-rebuild-manifests.cjs')).build('motion-sickness-games',inventory));
const files=[batch+'/queue.json',batch+'/README.md',batch+'/seal-motion-delivery-v1.py',batch+'/deliver-motion-handoff-v1.cjs',
 pub+'/schedule-evidence-git-verification-v1.json',pub+'/final-handoff-v1.json',rev+'/latest-checkpoint.json','projects/motion-sickness-games/rebuild.json'];
git(['add','--',...files],env);
const raw=git(['diff','--cached','--name-status','-z',parent],env).split('\0').filter(Boolean),changes=[];
for(let i=0;i<raw.length;i+=2)changes.push({status:raw[i],path:raw[i+1]});
if(changes.some(e=>!files.includes(e.path)||!['A','M'].includes(e.status)))throw Error('Foreign path/deletion');
const staged=new Map(git(['ls-files','--stage','-z'],env).split('\0').filter(Boolean).map(l=>{const[m,f]=l.split('\t');return[f,m.split(' ')[1]];}));
const blobs=git(['hash-object','--stdin-paths'],env,files.join('\n')+'\n').split(/\r?\n/);
files.forEach((f,i)=>{if(staged.get(f)!==blobs[i])throw Error('Staged bytes differ '+f);});
const checks={whitespace:git(['diff','--cached','--check',parent],env),media:run(process.execPath,['scripts/media-policy.cjs'],env),
 currentMotionRebuild:run(process.execPath,['scripts/build-rebuild-manifests.cjs','motion-sickness-games','--check'],env)};
unchanged();if(git(['rev-parse','HEAD'])!==parent)throw Error('HEAD advanced; no commit');
const proof={schemaVersion:1,actualVideoId:'mBDd9VzSTkA',parent,selectedPaths:files,changedPaths:changes,checks,mediaAdded:0,newImagesAdded:0,
 allStagedBlobsVerified:true,externalIndexSha256Before:sha(bytes),externalIndexUnchanged:true,recordedAt:new Date().toISOString(),pushed:false};
fs.writeFileSync(path.join(temp,'external-index-before.bin'),bytes);
if(process.argv.includes('--stage-only')){console.log(JSON.stringify({stageOnly:true,paths:files.length,checks}));process.exit(0);}
if(!process.argv.includes('--deliver'))throw Error('Choose --stage-only or --deliver');
const tree=git(['write-tree'],env),commit=git(['commit-tree',tree,'-p',parent],env,'Seal verified motion lesson delivery and actual schedule evidence\n');
unchanged();git(['update-ref','HEAD',commit,parent]);proof.commit=commit;save(proofPath,proof);
try{git(['push','origin',commit+':refs/heads/main']);}catch(e){proof.pushFailure=e.message;save(proofPath,proof);throw e;}
const local=git(['rev-parse','HEAD']),remote=git(['ls-remote','origin','refs/heads/main']).split(/\s/)[0];
if(local!==commit||remote!==commit)throw Error('Concurrent local/remote advance; preserve commit');
const final=new Map(git(['ls-tree','-r','-z',remote]).split('\0').filter(Boolean).map(l=>{const[m,f]=l.split('\t');return[f,m.split(' ')[2]];}));
for(const f of files)if(final.get(f)!==staged.get(f))throw Error('Final blob differs '+f);
unchanged();Object.assign(proof,{pushed:true,localCommit:local,remoteCommit:remote,exactLocalRemoteMatch:true,allFinalRemoteBlobsVerified:true,
 verifiedBlobCount:files.length,externalIndexSha256After:sha(fs.readFileSync(external)),verifiedAt:new Date().toISOString()});save(proofPath,proof);
console.log(JSON.stringify({commit,remote,verifiedBlobs:files.length,newImages:0,media:0,externalIndexUnchanged:true,pushed:true}));
