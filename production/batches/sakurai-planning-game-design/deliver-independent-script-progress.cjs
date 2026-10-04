// Explicit non-media paths only. A temporary index preserves concurrent staged work.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),cp=require('child_process');
const root=path.resolve(__dirname,'../../..'),base='production/batches/sakurai-planning-game-design',proof=base+'/proof-avoid-game-comparisons',sr=proof+'/source-research',project='projects/avoid-game-comparisons';
const now=()=>new Date().toISOString(),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex'),write=(p,d)=>fs.writeFileSync(path.join(root,p),JSON.stringify(d,null,2)+'\n');
function git(args,env=process.env,input){const r=cp.spawnSync('git',args,{cwd:root,env,input,encoding:'utf8',windowsHide:true,maxBuffer:64e6});if(r.status!==0)throw Error('git '+args.join(' ')+'\n'+r.stdout+r.stderr);return r.stdout;}
const selected=[
 base+'/README.md',base+'/queue.json',base+'/preflight/avoid-game-comparisons.json',base+'/refresh-gate-after-receipt-change.cjs',base+'/deliver-independent-script-progress.cjs',
 ...['content-review.json','latest-checkpoint.json','source-candidates-and-usage-review.json','source-bank-git-verification.json','prepare-independent-plan.cjs','write-independent-scripts.cjs','record-independent-script-review.cjs','record-script-checkpoint.cjs'].map(n=>proof+'/'+n),
 ...['official-source-observations.json','request-pepper-reveal.json','acquisition-pepper-reveal.json','discovery-pepper-reveal.json','direct-pepper-reveal-review.json','pepper-reveal-sampled-comparison.json','record-reveal-duplicate.py','prepare-drill-request.cjs','request-pepper-drill.json','acquisition-pepper-drill.json','discovery-pepper-drill.json','request-native-drill.json','native-review-drill-v1.json','direct-pepper-drill-review.json','record-drill-native-review.cjs','source-action-bank-v2.json'].map(n=>sr+'/'+n),
 ...['README.md','project.json','rebuild.json','planning/outline.md','planning/chapter-plan.json','script/narration.ko.json','script/narration.en.json','sources/SOURCES.md','sources/action-map.json','sources/game-candidates.json','production/planning-input-review.json','production/script-source-review.json','production/latest-checkpoint.json'].map(n=>project+'/'+n),
 proof+'/script-progress-pre-delivery-checks.json'
];
const parent=git(['rev-parse','HEAD']).trim(),index=path.join(root,'.git','script-progress-'+Date.now()+'.index'),env={...process.env,GIT_INDEX_FILE:index};
const foreignStaged=git(['diff','--cached','--name-only','-z']).split('\0').filter(Boolean).filter(p=>!selected.includes(p));
const foreignStatus=git(['status','--porcelain=v1','-z','--untracked-files=no']).split('\0').filter(Boolean).filter(s=>!selected.includes(s.slice(3)));
const checks=[];
function node(args){const r=cp.spawnSync(process.execPath,args,{cwd:root,env,encoding:'utf8',windowsHide:true,maxBuffer:16e6});checks.push({command:'node '+args.join(' '),exitCode:r.status,output:(r.stdout+r.stderr).trim()});if(r.status!==0)throw Error('Check failed: '+args.join(' ')+'\n'+r.stdout+r.stderr);}
try{
 git(['read-tree',parent],env);
 for(const p of selected.filter(p=>!p.endsWith('script-progress-pre-delivery-checks.json')))git(['add','--',p],env);
 node(['scripts/media-policy.cjs']);
 node(['scripts/review-video-duplicates.cjs','avoid-game-comparisons','--check']);
 node(['scripts/build-rebuild-manifests.cjs','avoid-game-comparisons','--check']);
 git(['diff','--cached','--check',parent],env);
 write(proof+'/script-progress-pre-delivery-checks.json',{schemaVersion:1,checkedAt:now(),parent,scope:'Independent12-scene50-paragraph KO/EN text, source/native review and editorial metadata only; TTS/MC/render/QA/output/upload incomplete.',commands:checks,temporaryIndex:true,explicitPaths:selected,newRasterAdded:0,mediaAdded:0,noFullWorkingTreeRebuildClaim:true,completedTenRebuilds:'Previously checked source-bank delivery; no completed production files changed here.',npm:'Unavailable; exact Node media/rebuild hooks used.',whitespacePassed:true,foreignStagedBefore:foreignStaged,foreignStatusBefore:foreignStatus});
 git(['add','--',proof+'/script-progress-pre-delivery-checks.json'],env);
 const changed=git(['diff','--cached','--name-only','-z',parent],env).split('\0').filter(Boolean);
 if(!changed.length||changed.some(p=>!selected.includes(p)||/\.(?:png|jpe?g|webp|gif|bmp|tiff?|mp4|webm|wav|m4a|mp3|zip|7z|info\.json)$/i.test(p)))throw Error('Unexpected path/media/image in delivery');
 if(git(['diff','--cached','--diff-filter=D','--name-only',parent],env).trim())throw Error('No deletion authorized in script progress');
 git(['diff','--cached','--check',parent],env);
 const hashes=changed.map(p=>({path:p,sha256:hash(p)}));
 const tree=git(['write-tree'],env).trim();
 if(git(['rev-parse','HEAD']).trim()!==parent)throw Error('Concurrent HEAD changed; restart delivery from actual HEAD.');
 for(const h of hashes)if(hash(h.path)!==h.sha256)throw Error('Concurrent selected-path edit: '+h.path);
 const commit=git(['commit-tree',tree,'-p',parent],env,'Write and review independent game-pitch narration with unique official action sources\n').trim();
 const committed=git(['diff-tree','--no-commit-id','--name-only','-r',commit]).trim().split('\n').filter(Boolean).sort();
 if(JSON.stringify(committed)!==JSON.stringify([...changed].sort()))throw Error('Final commit paths differ');
 git(['update-ref','HEAD',commit,parent]);
 for(const p of changed)git(['restore','--staged','--source='+commit,'--',p]);
 const foreignStagedAfter=git(['diff','--cached','--name-only','-z']).split('\0').filter(Boolean).filter(p=>!selected.includes(p));
 if(JSON.stringify(foreignStagedAfter)!==JSON.stringify(foreignStaged))throw Error('Unexpected foreign staged path change; inspect without reset.');
 const push=cp.spawnSync('git',['push','origin','main'],{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:16e6});
 const local=git(['rev-parse','HEAD']).trim(),remote=git(['ls-remote','origin','refs/heads/main']).trim().split(/\s+/)[0];
 const verification={schemaVersion:1,verifiedAt:now(),scriptSourceProgressCommit:commit,parent,commitPaths:committed,reviewedFileHashes:hashes,pushExitCode:push.status,pushOutput:(push.stdout+push.stderr).trim(),normalPush:true,forcePush:false,localSha:local,remoteSha:remote,remoteMatches:local===remote,newRasterCommitted:0,mediaCommitted:false,foreignStagedBefore:foreignStaged,foreignStagedAfter,sharedIndexOwnPathsOnly:true,otherUsersFilesIncluded:false,completedVideoDelivery:false,productionStillPending:['TTS','independent Motion Canvas scenes','measured60:40','final mix/render/QA','output collection','new private upload'],persistence:'Actual post-push evidence written only after observing the push; no future own SHA predicted.'};
 write(proof+'/script-progress-git-verification.json',verification);
 if(push.status!==0||local!==remote)throw Error('Normal push/remote verification incomplete; actual result retained.');
 console.log(JSON.stringify({commit,parent,paths:changed.length,localSha:local,remoteSha:remote,pushExitCode:push.status,newRasterCommitted:0,mediaCommitted:false}));
}finally{if(fs.existsSync(index))fs.unlinkSync(index);}
