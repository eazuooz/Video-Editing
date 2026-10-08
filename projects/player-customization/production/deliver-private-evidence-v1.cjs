// Usage: node projects/player-customization/production/deliver-private-evidence-v1.cjs --prepare|--deliver
// Deliver the observed production-push evidence and accurate batch rollup only.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/player-customization';
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8'));
const write=(f,j)=>fs.writeFileSync(path.join(root,f),JSON.stringify(j,null,2)+'\n');
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
function run(cmd,args,env=process.env,input){const start=Date.now();while(true){const r=cp.spawnSync(cmd,args,{cwd:root,env,input,encoding:'utf8',windowsHide:true,maxBuffer:256e6});if(r.status===0)return r.stdout.trimEnd();if(cmd==='git'&&/index\.lock.*File exists|Unable to create .*index\.lock/s.test(r.stderr)&&Date.now()-start<60000){Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,500);continue;}throw Error(cmd+' '+args.join(' ')+'\n'+r.stdout+'\n'+r.stderr);}}
const git=(a,e,input)=>run('git',a,e,input);
const productionProof=base+'/publishing/private-delivery-git-verification-v1.json',proof=read(productionProof);
if(!proof.pushed||!proof.exactLocalRemoteMatch||!proof.allRemoteBlobsVerified)throw Error('Observed production push and all remote blobs are required');
if(process.argv.includes('--prepare')){
 const receiptPath=base+'/publishing/youtube-upload-v1.json',receipt=read(receiptPath);
 receipt.git={delivered:true,productionCommit:proof.commit,remoteCommit:proof.remoteCommit,proof:productionProof,normalPush:true,allRemoteBlobsVerified:true,verifiedAt:proof.verifiedAt};write(receiptPath,receipt);
 const queuePath='production/batches/sakurai-planning-game-design/queue.json',q=read(queuePath),item=q.items.find(i=>i.slug==='player-customization');
 if(item.status!=='complete-private-review')throw Error('Sync the actual private checkpoint first');
 const completed=q.items.filter(i=>/^(uploaded-private(?:-awaiting-user-review)?|complete-private-review)$/.test(i.status));
 const queued=q.items.filter(i=>i.status==='queued'),duplicates=q.items.filter(i=>i.status==='skipped-duplicate');
 if(completed.length!==14||queued.length!==9||duplicates.length!==1)throw Error('Unexpected batch counts; inspect the actual queue before changing rollup');
 Object.assign(q.progress,{remaining:9,rendered:14,collected:14,uploaded:14,duplicateExcluded:1,inProgress:0,queued:9,productionRendered:14,productionCollected:14,privateSaved:14,fullSettingsDelivered:14,productionDelivered:14,remainingProduction:9,productionGitDelivered:14});
 q.currentSlug='similar-game-design';q.lastCompletedSlug='player-customization';q.lastProgressAt=new Date().toISOString();q.updatedAt=q.lastProgressAt;
 item.gitDelivery={...item.gitDelivery,completed:true,normalPush:true,allRemoteBlobsVerified:true,verifiedAt:proof.verifiedAt,transientIndexLockRecovery:productionProof};
 write(queuePath,q);
 const projectReadme=base+'/README.md';let text=fs.readFileSync(path.join(root,projectReadme),'utf8');
 text=text.replace('Selective normal Git delivery is the remaining technical delivery step.',`Selective normal Git delivery completed as ${proof.commit}, with actual local/remote equality and all536 reviewed remote blobs verified. The transient shared-index lock was resolved by synchronizing only owned paths; no external lock or process was removed. Next: similar-game-design duplicate/source review.`);
 fs.writeFileSync(path.join(root,projectReadme),text);
 const batchReadme='production/batches/sakurai-planning-game-design/README.md';text=fs.readFileSync(path.join(root,batchReadme),'utf8');
 const paragraph=`2026-10-08 latest actual delivery: player-customization was saved once as private lf765yYhPdM, with current1080p60 CC-off game/2.5D pixels, all available settings, SD/HD and both automatic checks verified. Its536 selected production paths were normally pushed as ${proof.commit}; actual local/remote and every final blob matched. Only the illustrated thumbnail and three minimal publishing proofs were new raster assets; media/source/contact/encoded QA images were excluded. The shared-index lock failure preserved its existing commit and foreign staging; recovery did not delete a lock or repeat production/upload. The current batch has14 reviewed private deliveries, one confirmed duplicate exclusion and9 queued videos. Next is similar-game-design (BO_q72ug1eA), beginning with full concept/source/script/current Studio duplicate review. Human listening/pronunciation/public-rights/Nimbus/member handles/backup/dubbing/optionalCC/private comment remain pending. TTS handoff restores the original research queue on success or failure and verifies actual execution; no foreign research pause was issued for this completed video.\n\nThe older checkpoints below are historical; current queue and individual receipts take precedence.\n\n`;
 const firstBreak=text.indexOf('\n');text=text.slice(0,firstBreak+1)+'\n'+paragraph+text.slice(firstBreak+1).trimStart();fs.writeFileSync(path.join(root,batchReadme),text);
 console.log(JSON.stringify({prepared:true,productionCommit:proof.commit,privateVideoId:receipt.videoId,completed:14,duplicateExcluded:1,queued:9,next:'similar-game-design'}));process.exit(0);
}
if(!process.argv.includes('--deliver'))throw Error('Choose an explicit mode');
const files=[base+'/README.md',base+'/project.json',base+'/rebuild.json',base+'/production/latest-checkpoint.json',base+'/publishing/youtube-upload-v1.json',productionProof,base+'/production/deliver-reviewed-private-v1.cjs',base+'/production/recover-private-git-delivery-v1.cjs',base+'/production/deliver-private-evidence-v1.cjs','production/batches/sakurai-planning-game-design/queue.json','production/batches/sakurai-planning-game-design/README.md'];
const parent=git(['rev-parse','HEAD']),before=git(['ls-files','--stage','-z']),allowed=new Set(files);
if(git(['diff','--cached','--name-only','-z']).split('\0').some(f=>allowed.has(f)))throw Error('An owned evidence path has external staged edits');
const dir=fs.mkdtempSync(path.join(root,'.git/player-customization-evidence-')),env={...process.env,GIT_INDEX_FILE:path.join(dir,'index')};
fs.writeFileSync(path.join(dir,'external-index-before.txt'),before);git(['read-tree',parent],env);git(['add','--',...files],env);
const raw=git(['diff','--cached','--name-status','-z',parent],env).split('\0').filter(Boolean),rows=[];
for(let i=0;i<raw.length;i+=2)rows.push({status:raw[i],path:raw[i+1]});
if(!rows.length||rows.some(r=>!allowed.has(r.path)||r.status==='D'||/\.(?:png|jpg|mp4|wav|aac)$/i.test(r.path)))throw Error('Unexpected evidence scope or media');
const entries=git(['ls-files','--stage','-z'],env).split('\0').filter(Boolean),blobs=new Map(entries.map(l=>{const [m,f]=l.split('\t');return[f,m.split(' ')[1]];}));
const working=git(['hash-object','--stdin-paths'],process.env,files.join('\n')+'\n').split(/\r?\n/);
if(working.length!==files.length||files.some((f,i)=>blobs.get(f)!==working[i]))throw Error('Final evidence blobs changed');
git(['diff','--cached','--check',parent],env);console.log(run(process.execPath,['scripts/media-policy.cjs'],env));console.log(run(process.execPath,['scripts/build-rebuild-manifests.cjs','player-customization','--check'],env));
if(git(['rev-parse','HEAD'])!==parent||git(['ls-files','--stage','-z'])!==before)throw Error('Concurrent HEAD/index changed; preserve it and retry from the actual state');
const proofPath=base+'/publishing/private-delivery-evidence-git-verification-v1.json';
const p={schemaVersion:1,slug:'player-customization',productionCommit:proof.commit,parent,temporaryIndex:env.GIT_INDEX_FILE,selectedPaths:files,changedPaths:rows,finalStagedBlobsVerified:true,mediaCheck:true,scopedRebuildCheck:true,whitespaceCheck:true,externalIndexUnchangedBeforeCommit:true,newImages:0,newMedia:0,pushed:false,recordedAt:new Date().toISOString(),selfShaPersistence:'The evidence commit contains the previously observed production-push proof. This subsequent self-SHA verification is a local runtime record, never a predicted future SHA.'};
write(proofPath,p);
const tree=git(['write-tree'],env),commit=git(['commit-tree',tree,'-p',parent],env,'Record verified player customization delivery and research restoration policy\n');git(['update-ref','HEAD',commit,parent]);p.commit=commit;write(proofPath,p);
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
