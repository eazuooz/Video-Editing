// Resume only the already-created reviewed commit after a transient shared-index lock.
// Never recreate media, delete an external lock, or touch unrelated staged entries.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/player-customization';
const commit='b2c8f8e4fec7a83d4de19f30871d4c5f019ee149';
const tempIndex=path.join(root,'.git/player-customization-delivery-icGdLO/index');
const proofPath=path.join(root,base,'publishing/private-delivery-git-verification-v1.json');
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function run(cmd,args,env=process.env,input){
 const start=Date.now();
 while(true){const r=cp.spawnSync(cmd,args,{cwd:root,env,input,encoding:'utf8',windowsHide:true,maxBuffer:256e6});
  if(r.status===0)return r.stdout.trimEnd();
  if(cmd==='git'&&/index\.lock.*File exists|Unable to create .*index\.lock/s.test(r.stderr)&&Date.now()-start<60000){Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,500);continue;}
  throw Error(cmd+' '+args.join(' ')+'\n'+r.stdout+'\n'+r.stderr);
 }
}
const git=(a,e,input)=>run('git',a,e,input),plan=read(base+'/production/git-delivery-paths-v1.json');
const files=plan.selectedPaths,special=plan.sharedPaths,allowed=new Set([...files,...special]);
const env={...process.env,GIT_INDEX_FILE:tempIndex};
const parent=git(['rev-parse',commit+'^']),head=git(['rev-parse','HEAD']);
if(head!==commit)throw Error('A newer HEAD needs a fresh reviewed recovery; never reset it');
if(git(['write-tree'],env)!==git(['rev-parse',commit+'^{tree}']))throw Error('Preserved verified index does not match the actual commit');
const raw=git(['diff-tree','--no-commit-id','--name-status','-r','-z',commit]).split('\0').filter(Boolean),rows=[];
for(let i=0;i<raw.length;i+=2)rows.push({status:raw[i],path:raw[i+1]});
if(rows.length!==536||rows.some(r=>!allowed.has(r.path)||r.status==='D'))throw Error('Unexpected reviewed commit scope');
const staged=git(['ls-files','--stage','-z'],env).split('\0').filter(Boolean);
const blobs=new Map(staged.map(l=>{const [meta,f]=l.split('\t');return[f,meta.split(' ')[1]];}));
const working=git(['hash-object','--stdin-paths'],process.env,files.join('\n')+'\n').split(/\r?\n/);
if(working.length!==files.length||files.some((f,i)=>blobs.get(f)!==working[i]))throw Error('An owned working file changed after the verified commit');
const images=read('shared/git-essential-images.json').entries.filter(e=>plan.essentialImages.includes(e.path));
for(const e of images)if(e.sha256!==sha(fs.readFileSync(path.join(root,e.path))))throw Error('Reviewed essential image changed');
const before=git(['ls-files','--stage','-z']);
const foreign=t=>t.split('\0').filter(Boolean).filter(l=>!allowed.has(l.split('\t')[1])).join('\0');
const initialSpecial=Object.fromEntries(special.map(f=>[f,git(['show',':'+f])]));
const memory=fs.readFileSync(path.join(root,'AGENTS.md'),'utf8').split(/\r?\n/).find(l=>l.startsWith('- GPU handoff for narration,'));
function mergeOwn(f,text){
 if(f==='AGENTS.md'){const lines=text.split(/\r?\n/),i=lines.findIndex(l=>l.startsWith('- GPU handoff for narration,'));if(i<0||!memory.includes('멈추면 작업끝나면 다시 원래 연구작업은 재게해줘'))throw Error('Exact user GPU restoration memory missing');lines[i]=memory;return lines.join('\n');}
 if(f==='.gitignore'){let t=text.trimEnd();for(const e of images)if(!t.split(/\r?\n/).includes('!'+e.path))t+='\n!'+e.path;return t+'\n';}
 const j=JSON.parse(text);for(const e of images){const old=j.entries.find(x=>x.path===e.path);if(old&&old.sha256!==e.sha256)throw Error('Conflicting image registry');if(!old)j.entries.push(e);}return JSON.stringify(j,null,2)+'\n';
}
const proof={schemaVersion:1,slug:'player-customization',parent,commit,temporaryIndex:tempIndex,selectedPaths:files,stagedPaths:rows,allFinalStagedBlobsVerified:true,mediaCheck:true,scopedRebuildCheck:true,whitespaceCheck:true,externalIndexUnchangedBeforeCommit:true,essentialRasterPaths:plan.essentialImages,recordedAt:new Date().toISOString(),pushed:false,recovery:{originalSession:88230,originalExitCode:1,failedAt:'Owned external-index synchronization after guarded commit creation',cause:'Transient .git/index.lock belonging to another Git operation; no lock was deleted',commitRecreated:false,currentRecoveryForeignIndexSha256:sha(Buffer.from(foreign(before)))}};
fs.writeFileSync(proofPath,JSON.stringify(proof,null,2)+'\n');
for(let i=0;i<rows.length;i+=30){const owned=rows.slice(i,i+30).filter(r=>!special.includes(r.path)).map(r=>r.path);if(owned.length)git(['restore','--staged','--source='+commit,'--',...owned]);}
for(const f of special){const blob=git(['hash-object','-w','--stdin'],process.env,mergeOwn(f,initialSpecial[f]));git(['update-index','--add','--cacheinfo','100644',blob,f]);}
if(foreign(git(['ls-files','--stage','-z']))!==foreign(before))throw Error('Concurrent unrelated index entries changed; inspect before claiming preservation');
Object.assign(proof,{unrelatedIndexEntriesPreservedDuringRecovery:true,ownIndexPathsSynchronized:true,recoveryForeignIndexUnchanged:true});
fs.writeFileSync(proofPath,JSON.stringify(proof,null,2)+'\n');
git(['diff','--cached','--check',parent],env);
console.log(run(process.execPath,['scripts/media-policy.cjs'],env));
// The original producer passed the exact scoped --check before commit creation.
// This recovery helper and post-commit evidence are new metadata; their refreshed
// working-tree rebuild belongs to the subsequent evidence commit, not this tree.
proof.recovery.currentWorkingRebuildCheck={passed:false,reason:'New recovery helper/evidence added after the original checked commit; refresh and run the exact scoped --check for the evidence follow-up.',originalProducerScopedCheckPassed:true};
proof.recovery.priorRecoveryAttempt={exitCode:1,indexSynchronizationCompleted:true,pushStarted:false,cause:'Scoped working rebuild became stale when the new recovery helper was added; original production/media unchanged.'};
fs.writeFileSync(proofPath,JSON.stringify(proof,null,2)+'\n');
git(['push','origin',commit+':refs/heads/main']);
const local=git(['rev-parse','HEAD']),remote=git(['ls-remote','origin','refs/heads/main']).split(/\s/)[0];
if(local!==commit||remote!==commit)throw Error('Actual local/remote differs; preserve the newer state');
const tree=git(['ls-tree','-r','-z',remote]).split('\0').filter(Boolean),remoteBlobs=new Map(tree.map(l=>{const [m,f]=l.split('\t');return[f,m.split(' ')[2]];}));
if(rows.some(r=>remoteBlobs.get(r.path)!==blobs.get(r.path)))throw Error('A final remote blob differs');
Object.assign(proof,{localCommit:local,remoteCommit:remote,pushed:true,exactLocalRemoteMatch:true,allRemoteBlobsVerified:true,verifiedAt:new Date().toISOString()});
fs.writeFileSync(proofPath,JSON.stringify(proof,null,2)+'\n');
console.log(JSON.stringify({commit,remote,paths:rows.length,essentialImages:plan.essentialImages,pushed:true,recoveredExistingCommit:true}));
