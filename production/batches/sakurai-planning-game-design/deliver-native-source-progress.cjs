// Explicit metadata-only delivery through a temporary index in the shared checkout.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),cp=require('child_process');
const root=path.resolve(__dirname,'../../..'),base='production/batches/sakurai-planning-game-design',proof=base+'/proof-avoid-game-comparisons',sr=proof+'/source-research';
const now=()=>new Date().toISOString(),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const write=(p,d)=>fs.writeFileSync(path.join(root,p),JSON.stringify(d,null,2)+'\n');
function git(args,env=process.env,input){const r=cp.spawnSync('git',args,{cwd:root,env,input,encoding:'utf8',windowsHide:true,maxBuffer:128e6});if(r.status!==0)throw Error('git '+args.join(' ')+'\n'+r.stdout+r.stderr);return r.stdout;}
const selected=[
 base+'/README.md',base+'/queue.json',base+'/preflight/avoid-game-comparisons.json',base+'/refresh-gate-after-receipt-change.cjs',base+'/deliver-native-source-progress.cjs',
 proof+'/content-review.json',proof+'/latest-checkpoint.json',proof+'/source-candidates-and-usage-review.json',proof+'/record-source-bank-checkpoint.cjs',
 ...['extract-discovery.py','extract-native-review.py','record-native-review.cjs','acquisition-pest-control.json','acquisition-rocket-ride.json','discovery-rocket-ride.json','native-review-v1.json','native-review-rocket-v1.json','request-native-rocket.json','request-pest-control.json','request-rocket-ride.json','direct-native-review-v1.json','direct-rocket-discovery-review.json','source-action-bank-v1.json','official-source-observations.json'].map(n=>sr+'/'+n),
 proof+'/source-bank-pre-delivery-checks.json'
];
const parent=git(['rev-parse','HEAD']).trim();
const indexFile=path.join(root,'.git','native-source-delivery-'+Date.now()+'.index');
const env={...process.env,GIT_INDEX_FILE:indexFile};
git(['read-tree',parent],env);
const results=[];
function node(args){const r=cp.spawnSync(process.execPath,args,{cwd:root,env,encoding:'utf8',windowsHide:true,maxBuffer:16e6});results.push({command:'node '+args.join(' '),exitCode:r.status,output:(r.stdout+r.stderr).trim()});if(r.status!==0)throw Error('Check failed: '+args.join(' ')+'\n'+r.stdout+r.stderr);}
try {
 for(const p of selected.filter(p=>!p.endsWith('source-bank-pre-delivery-checks.json')))git(['add','--',p],env);
 node(['scripts/media-policy.cjs']);
 node(['scripts/review-video-duplicates.cjs','avoid-game-comparisons','--check']);
 const targets=['counting-animation-frames','deconstruct-analyze-rebuild','meaningful-quests','praise-player','responsive-game-feedback','game-writing','picking-sides','motion-sickness-games','hierarchical-game-outlines','game-reward-planning'];
 for(const slug of targets)node(['scripts/build-rebuild-manifests.cjs',slug,'--check']);
 git(['diff','--cached','--check',parent],env);
 const proofData={schemaVersion:1,checkedAt:now(),parent,scope:'Source research/direct visual review and batch checkpoint only; no new project, script, TTS, scene or media. Existing ten completed batch rebuild manifests checked without rewriting them.',commands:results,whitespacePassed:true,newRasterAdded:0,mediaAdded:0,fullWorkingTreeRebuild:'not claimed; concurrent users projects/shared changes are excluded from this delivery',npm:'Unavailable; exact Node media/rebuild commands used.',temporaryIndex:true,explicitPaths:selected};
 write(proof+'/source-bank-pre-delivery-checks.json',proofData);git(['add','--',proof+'/source-bank-pre-delivery-checks.json'],env);
 const changed=git(['diff','--cached','--name-only','-z',parent],env).split('\0').filter(Boolean);
 if(!changed.length||changed.some(p=>!selected.includes(p)||/\.(?:png|jpe?g|webp|gif|bmp|tiff?|mp4|wav|m4a|mp3|zip|7z|info\.json)$/i.test(p)))throw Error('Unexpected delivery paths');
 if(git(['diff','--cached','--diff-filter=D','--name-only',parent],env).trim())throw Error('No deletion authorized in this source delivery');
 git(['diff','--cached','--check',parent],env);
 const hashes=changed.map(p=>({path:p,sha256:hash(p)}));
 const tree=git(['write-tree'],env).trim();
 if(git(['rev-parse','HEAD']).trim()!==parent)throw Error('Concurrent HEAD changed; prepare afresh from actual HEAD.');
 for(const h of hashes)if(hash(h.path)!==h.sha256)throw Error('Selected file changed: '+h.path);
 const commit=git(['commit-tree',tree,'-p',parent],env,'Review unique game actions and native cut boundaries for independent pitch video\n').trim();
 const committedPaths=git(['diff-tree','--no-commit-id','--name-only','-r',commit]).trim().split('\n').filter(Boolean).sort();
 if(JSON.stringify(committedPaths)!==JSON.stringify([...changed].sort()))throw Error('Final commit paths mismatch');
 git(['update-ref','HEAD',commit,parent]);
 // Synchronize only our delivered paths; preserve every unrelated shared-index entry and working file.
 for(const p of changed)git(['restore','--staged','--source='+commit,'--',p]);
 const push=cp.spawnSync('git',['push','origin','main'],{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:16e6});
 const local=git(['rev-parse','HEAD']).trim(),remote=git(['ls-remote','origin','refs/heads/main']).trim().split(/\s+/)[0];
 const verification={schemaVersion:1,verifiedAt:now(),productionSourceProgressCommit:commit,parent,commitPaths:committedPaths,reviewedFileHashes:hashes,pushExitCode:push.status,pushOutput:(push.stdout+push.stderr).trim(),normalPush:true,forcePush:false,localSha:local,remoteSha:remote,remoteMatches:local===remote,mediaCommitted:false,newRasterCommitted:0,sharedIndexOwnPathsOnly:true,otherUsersFilesIncluded:false,persistence:'Actual post-push verification is local until the next explicit evidence commit; no future self-SHA is predicted.'};
 write(proof+'/source-bank-git-verification.json',verification);
 if(push.status!==0||local!==remote)throw Error('Normal push/remote verification incomplete; actual evidence retained.');
 console.log(JSON.stringify({commit,parent,paths:changed.length,localSha:local,remoteSha:remote,newRasterCommitted:0,pushExitCode:push.status}));
} finally {if(fs.existsSync(indexFile))fs.unlinkSync(indexFile);}
