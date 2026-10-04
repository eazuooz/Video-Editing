// Exact JSON snapshots preserve moving worker checkpoints without touching user staging.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),batch='production/batches/sakurai-planning-game-design',proof=batch+'/proof-avoid-game-comparisons',sr=proof+'/source-research',project='projects/avoid-game-comparisons';
const checksFile=proof+'/expanded-voice-evidence-pre-delivery-checks.json';
const selected=JSON.parse(fs.readFileSync(path.join(root,batch+'/expanded-voice-evidence-paths.json'),'utf8'));
const stamp=()=>new Date().toISOString(),digest=b=>crypto.createHash('sha256').update(b).digest('hex');
function git(args,env=process.env,input){const r=cp.spawnSync('git',args,{cwd:root,env,input,encoding:input instanceof Buffer?undefined:'utf8',windowsHide:true,maxBuffer:64e6});if(r.status!==0)throw Error('git '+args.join(' ')+'\n'+r.stdout+r.stderr);return String(r.stdout);}
const parent=git(['rev-parse','HEAD']).trim(),index=path.join(root,'.git','expanded-voice-'+Date.now()+'.index'),env={...process.env,GIT_INDEX_FILE:index},commands=[];
const foreignStaged=git(['diff','--cached','--name-only','-z']).split('\0').filter(Boolean).filter(p=>!selected.includes(p));
function foreignIndexHash(){return digest(Buffer.from(git(['ls-files','--stage','-z']).split('\0').filter(Boolean).filter(s=>!selected.includes(s.slice(s.indexOf('\t')+1))).join('\0')));}
const foreignBefore=foreignIndexHash(),snapshots=[];
function stageSnapshot(p){const bytes=fs.readFileSync(path.join(root,p));if(p.endsWith('.json'))JSON.parse(bytes.toString('utf8'));const blob=git(['hash-object','-w','--path='+p,'--stdin'],env,bytes).trim();git(['update-index','--add','--cacheinfo','100644,'+blob+','+p],env);snapshots.push({path:p,blob,workingBytesSha256:digest(bytes),capturedAt:stamp()});}
function node(args){const r=cp.spawnSync(process.execPath,args,{cwd:root,env,encoding:'utf8',windowsHide:true,maxBuffer:16e6});commands.push({command:'node '+args.join(' '),exitCode:r.status,output:(r.stdout+r.stderr).trim()});if(r.status!==0)throw Error('Check failed: '+args.join(' ')+'\n'+r.stdout+r.stderr);}
try{
 git(['read-tree',parent],env);
 for(const p of selected.filter(p=>p!==checksFile))stageSnapshot(p);
 node(['scripts/media-policy.cjs']);node(['scripts/review-video-duplicates.cjs','avoid-game-comparisons','--check']);node(['scripts/build-rebuild-manifests.cjs','avoid-game-comparisons','--check']);node(['motion-canvas/node_modules/typescript/bin/tsc','-p','motion-canvas/tsconfig.avoid-game-comparisons.json','--pretty','false']);
 git(['diff','--cached','--check',parent],env);
 fs.writeFileSync(path.join(root,checksFile),JSON.stringify({schemaVersion:1,checkedAt:stamp(),parent,commands,explicitPaths:selected,temporaryIndexFromActualHead:true,runtimeSnapshotPolicy:'Exact captured JSON bytes/blob; later live-worker changes remain in working tree. These workers are closed; source bank and current14 narration review and proposed mixed visual roles are progress, not a finished video.',snapshots,newRasterAdded:0,mediaAdded:0,foreignStagedBefore:foreignStaged,foreignIndexBefore:foreignBefore,whitespacePassed:true,npm:'Unavailable; exact Node hooks used.',completedVideoDelivery:false,globalWorkingTreeRebuildPassed:false,globalLimitation:'Other unfinished concurrent projects previously failed global working-tree check; current project scoped check only.'},null,2)+'\n');
 stageSnapshot(checksFile);
 const changed=git(['diff','--cached','--name-only','-z',parent],env).split('\0').filter(Boolean);
 if(!changed.length||changed.some(p=>!selected.includes(p)||/\.(?:png|jpe?g|webp|gif|bmp|tiff?|mp4|webm|wav|m4a|mp3|zip|7z|info\.json)$/i.test(p)))throw Error('Unexpected path/media/image');
 if(git(['diff','--cached','--diff-filter=D','--name-only',parent],env).trim())throw Error('Unexpected deletion');
 git(['diff','--cached','--check',parent],env);
 const tree=git(['write-tree'],env).trim();if(git(['rev-parse','HEAD']).trim()!==parent)throw Error('Concurrent HEAD changed; inspect actual HEAD before retry');
 const commit=git(['commit-tree',tree,'-p',parent],env,'Record verified additive game-pitch narration progress push evidence\n').trim();
 const committed=git(['diff-tree','--no-commit-id','--name-only','-r',commit]).trim().split('\n').filter(Boolean).sort();
 if(JSON.stringify(committed)!==JSON.stringify([...changed].sort()))throw Error('Unexpected final commit paths');
 for(const s of snapshots.filter(s=>changed.includes(s.path)))if(git(['rev-parse',commit+':'+s.path]).trim()!==s.blob)throw Error('Committed snapshot blob mismatch: '+s.path);
 git(['update-ref','HEAD',commit,parent]);for(const p of changed)git(['restore','--staged','--source='+commit,'--',p]);
 const foreignAfter=foreignIndexHash();if(foreignAfter!==foreignBefore)throw Error('Foreign staged blobs changed; preserve and inspect');
 const push=cp.spawnSync('git',['push','origin','main'],{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:16e6}),local=git(['rev-parse','HEAD']).trim(),remote=git(['ls-remote','origin','refs/heads/main']).trim().split(/\s+/)[0];
 const record={schemaVersion:1,verifiedAt:stamp(),expandedVoiceEvidenceCommit:commit,parent,commitPaths:committed,snapshots:snapshots.filter(s=>changed.includes(s.path)),pushExitCode:push.status,pushOutput:(push.stdout+push.stderr).trim(),normalPush:true,forcePush:false,localSha:local,remoteSha:remote,remoteMatches:local===remote,foreignIndexBefore:foreignBefore,foreignIndexAfter:foreignAfter,otherUsersFilesIncluded:false,newRasterCommitted:0,mediaCommitted:false,completedVideoDelivery:false,current14SceneTechnicalAsrApproved:true,finalTimingRatioApproved:false,finalRenderedQaCollectedUploaded:false};
 fs.writeFileSync(path.join(root,proof+'/expanded-voice-evidence-git-verification.json'),JSON.stringify(record,null,2)+'\n');
 if(push.status!==0||local!==remote)throw Error('Normal push/remote match incomplete; actual outcome retained');console.log(JSON.stringify({commit,parent,paths:changed.length,pushExitCode:push.status,localSha:local,remoteSha:remote,newRasterCommitted:0,completedVideoDelivery:false}));
}finally{if(fs.existsSync(index))fs.unlinkSync(index);}
