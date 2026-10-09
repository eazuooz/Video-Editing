// Usage: node projects/similar-game-design/production/deliver-private-evidence-v1.cjs --deliver
// Deliver the observed production-push evidence and accurate batch rollup only.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/similar-game-design';
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8'));
const write=(f,j)=>fs.writeFileSync(path.join(root,f),JSON.stringify(j,null,2)+'\n');
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
function run(cmd,args,env=process.env,input){const start=Date.now();while(true){const r=cp.spawnSync(cmd,args,{cwd:root,env,input,encoding:'utf8',windowsHide:true,maxBuffer:256e6});if(r.status===0)return r.stdout.trimEnd();if(cmd==='git'&&/index\.lock.*File exists|Unable to create .*index\.lock/s.test(r.stderr)&&Date.now()-start<60000){Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,500);continue;}throw Error(cmd+' '+args.join(' ')+'\n'+r.stdout+'\n'+r.stderr);}}
const git=(a,e,input)=>run('git',a,e,input);
const productionProof=base+'/publishing/private-delivery-git-verification-v1.json',proof=read(productionProof);
if(!proof.pushed||!proof.exactLocalRemoteMatch||!proof.allRemoteBlobsVerified)throw Error('Observed production push and all remote blobs are required');
if(!process.argv.includes('--deliver'))throw Error('Choose an explicit mode');
const files=["projects/similar-game-design/README.md", "projects/similar-game-design/project.json", "projects/similar-game-design/rebuild.json", "projects/similar-game-design/production/latest-checkpoint.json", "projects/similar-game-design/publishing/youtube-upload-v1.json", "projects/similar-game-design/publishing/private-upload-execution-v1.json", "projects/similar-game-design/publishing/private-delivery-git-verification-v1.json", "projects/similar-game-design/script/narration.current.ko.json", "projects/similar-game-design/script/narration.current.en.json", "projects/similar-game-design/production/deliver-private-evidence-v1.cjs", "projects/similar-game-design/production/record-private-git-handoff-v1.py", "projects/similar-game-design/production/private-final-delivery-rollup-v1.json", "production/batches/sakurai-planning-game-design/queue.json", "production/batches/sakurai-planning-game-design/README.md", "production/batches/sakurai-planning-game-design/preflight/presenting-game-scores.json", "production/batches/sakurai-planning-game-design/next-after-similar-private-delivery-v1.json"];
const parent=git(['rev-parse','HEAD']),before=git(['ls-files','--stage','-z']),allowed=new Set(files);
if(git(['diff','--cached','--name-only','-z']).split('\0').some(f=>allowed.has(f)))throw Error('An owned evidence path has external staged edits');
const dir=fs.mkdtempSync(path.join(root,'.git/similar-game-design-evidence-')),env={...process.env,GIT_INDEX_FILE:path.join(dir,'index')};
fs.writeFileSync(path.join(dir,'external-index-before.txt'),before);git(['read-tree',parent],env);git(['add','--',...files],env);
const raw=git(['diff','--cached','--name-status','-z',parent],env).split('\0').filter(Boolean),rows=[];
for(let i=0;i<raw.length;i+=2)rows.push({status:raw[i],path:raw[i+1]});
if(!rows.length||rows.some(r=>!allowed.has(r.path)||r.status==='D'||/\.(?:png|jpg|mp4|wav|aac)$/i.test(r.path)))throw Error('Unexpected evidence scope or media');
const entries=git(['ls-files','--stage','-z'],env).split('\0').filter(Boolean),blobs=new Map(entries.map(l=>{const [m,f]=l.split('\t');return[f,m.split(' ')[1]];}));
const working=git(['hash-object','--stdin-paths'],process.env,files.join('\n')+'\n').split(/\r?\n/);
if(working.length!==files.length||files.some((f,i)=>blobs.get(f)!==working[i]))throw Error('Final evidence blobs changed');
git(['diff','--cached','--check',parent],env);console.log(run(process.execPath,['scripts/media-policy.cjs'],env));console.log(run(process.execPath,['scripts/build-rebuild-manifests.cjs','similar-game-design','--check'],env));
if(git(['rev-parse','HEAD'])!==parent||git(['ls-files','--stage','-z'])!==before)throw Error('Concurrent HEAD/index changed; preserve it and retry from the actual state');
const proofPath=base+'/publishing/private-delivery-evidence-git-verification-v1.json';
const p={schemaVersion:1,slug:'similar-game-design',productionCommit:proof.commit,parent,temporaryIndex:env.GIT_INDEX_FILE,selectedPaths:files,changedPaths:rows,finalStagedBlobsVerified:true,mediaCheck:true,scopedRebuildCheck:true,whitespaceCheck:true,externalIndexUnchangedBeforeCommit:true,newImages:0,newMedia:0,pushed:false,recordedAt:new Date().toISOString(),selfShaPersistence:'The evidence commit contains the previously observed production-push proof. This subsequent self-SHA verification is a local runtime record, never a predicted future SHA.'};
write(proofPath,p);
const tree=git(['write-tree'],env),commit=git(['commit-tree',tree,'-p',parent],env,'Record verified similar game design delivery and next black explanation work\n');git(['update-ref','HEAD',commit,parent]);p.commit=commit;write(proofPath,p);
git(['restore','--staged','--source='+commit,'--',...rows.map(r=>r.path)]);
const foreign=t=>t.split('\0').filter(Boolean).filter(l=>!allowed.has(l.split('\t')[1])).join('\0');
if(foreign(git(['ls-files','--stage','-z']))!==foreign(before))throw Error('Concurrent unrelated index changed; inspect before claiming preservation');
p.foreignIndexEntriesPreserved=true;p.foreignIndexSha256=sha(foreign(before));write(proofPath,p);
git(['push','origin',commit+':refs/heads/main']);const local=git(['rev-parse','HEAD']),remote=git(['ls-remote','origin','refs/heads/main']).split(/\s/)[0];
if(local!==commit||remote!==commit)throw Error('Actual local/remote differs; preserve any newer state');
const remoteEntries=git(['ls-tree','-r','-z',remote]).split('\0').filter(Boolean),remoteBlobs=new Map(remoteEntries.map(l=>{const [m,f]=l.split('\t');return[f,m.split(' ')[2]];}));
if(rows.some(r=>remoteBlobs.get(r.path)!==blobs.get(r.path)))throw Error('Final remote evidence blob differs');
Object.assign(p,{localCommit:local,remoteCommit:remote,pushed:true,exactLocalRemoteMatch:true,allRemoteBlobsVerified:true,verifiedAt:new Date().toISOString()});write(proofPath,p);
console.log(JSON.stringify({commit,remote,paths:rows.length,newImages:0,newMedia:0,pushed:true,productionCommit:proof.commit}));
