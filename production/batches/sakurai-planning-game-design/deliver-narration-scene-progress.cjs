// Reviewed static code and metadata only; production completion is a later gate.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),proof='production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons',sr=proof+'/source-research',project='projects/avoid-game-comparisons',mc='motion-canvas/src/projects/avoid-game-comparisons';
const checksFile=proof+'/scene-progress-pre-delivery-checks.json',verificationFile=proof+'/scene-progress-git-verification.json';
const selected=[
 'production/batches/sakurai-planning-game-design/deliver-narration-scene-progress.cjs',
 proof+'/script-progress-evidence-git-verification.json',
 sr+'/acquire-official-sources.cjs',sr+'/pepper-behind-grind-ui-review.json',sr+'/plucky-gameplay-ui-review.json',sr+'/request-additional-measured-actions.json',
 project+'/project.json',project+'/rebuild.json',
 ...['render-reviewed-narration.py','review-current-narration.py','create-independent-scene-entrypoints.cjs','independent-scene-design.json','independent-scene-lookdev-review.json'].map(n=>project+'/production/'+n),
 'motion-canvas/vite.avoid-game-comparisons.config.ts','motion-canvas/tsconfig.avoid-game-comparisons.json',
 mc+'/project.ts',mc+'/lookdev-project.ts',mc+'/production-plan.json',
 ...['actual-scene.tsx','branding-intro.tsx','concept-diagrams.tsx','explanation-scene.tsx','lookdev-caption-guide.tsx','membership-outro.tsx'].map(n=>mc+'/scenes/'+n),
 ...Array.from({length:12},(_,i)=>mc+'/scenes/scene'+String(i+1).padStart(2,'0')+'.tsx'),
 ...['01','03','05','07','09','11'].map(id=>mc+'/scenes/lookdev'+id+'.tsx'),
 checksFile
];
const stamp=()=>new Date().toISOString(),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const write=(p,v)=>fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');
function git(args,env=process.env,input){const r=cp.spawnSync('git',args,{cwd:root,env,input,encoding:'utf8',windowsHide:true,maxBuffer:64e6});if(r.status!==0)throw Error('git '+args.join(' ')+'\n'+r.stdout+r.stderr);return r.stdout;}
const parent=git(['rev-parse','HEAD']).trim(),index=path.join(root,'.git','scene-progress-'+Date.now()+'.index'),env={...process.env,GIT_INDEX_FILE:index};
const foreignStaged=git(['diff','--cached','--name-only','-z']).split('\0').filter(Boolean).filter(p=>!selected.includes(p));
function foreignEntriesHash(){const entries=git(['ls-files','--stage','-z']).split('\0').filter(Boolean).filter(s=>!selected.includes(s.slice(s.indexOf('\t')+1)));return crypto.createHash('sha256').update(entries.join('\0')).digest('hex');}
const foreignIndexBefore=foreignEntriesHash(),commands=[];
function node(args,cwd=root){const r=cp.spawnSync(process.execPath,args,{cwd,env,encoding:'utf8',windowsHide:true,maxBuffer:16e6});commands.push({command:'node '+args.join(' '),cwd:path.relative(root,cwd).replaceAll('\\','/')||'.',exitCode:r.status,output:(r.stdout+r.stderr).trim()});if(r.status!==0)throw Error('Check failed: '+args.join(' ')+'\n'+r.stdout+r.stderr);}
try{
 git(['read-tree',parent],env);
 for(const p of selected.filter(p=>p!==checksFile))git(['add','--',p],env);
 node(['scripts/media-policy.cjs']);
 node(['scripts/review-video-duplicates.cjs','avoid-game-comparisons','--check']);
 node(['scripts/build-rebuild-manifests.cjs','avoid-game-comparisons','--check']);
 node(['node_modules/typescript/bin/tsc','--noEmit','-p','tsconfig.avoid-game-comparisons.json'],path.join(root,'motion-canvas'));
 git(['diff','--cached','--check',parent],env);
 write(checksFile,{schemaVersion:1,checkedAt:stamp(),parent,scope:'12 independent body scene entrypoints, six silently reviewed white2.5D layouts, guarded final-timing/native-action factories, TTS/CPU-ASR runners and two official candidate metadata records. Narration generation/review and final video delivery are incomplete.',commands,explicitPaths:selected,temporaryIndexFromActualHead:true,foreignStagedBefore:foreignStaged,foreignIndexBefore,newRasterAdded:0,mediaAdded:0,whitespacePassed:true,npm:'Unavailable; exact Node media/rebuild hooks used.',wholeWorkingTreeRebuildPassed:false,wholeWorkingTreeLimitation:'Other users unfinished projects previously failed global working-tree check; this record claims only the current project scoped check.',completedTenVideosTouched:false});
 git(['add','--',checksFile],env);
 const changed=git(['diff','--cached','--name-only','-z',parent],env).split('\0').filter(Boolean);
 if(!changed.length||changed.some(p=>!selected.includes(p)||/\.(?:png|jpe?g|webp|gif|bmp|tiff?|mp4|webm|wav|m4a|mp3|zip|7z|info\.json)$/i.test(p)))throw Error('Unexpected file/media/image in explicit delivery');
 if(git(['diff','--cached','--diff-filter=D','--name-only',parent],env).trim())throw Error('Deletion is outside this progress delivery');
 git(['diff','--cached','--check',parent],env);
 const hashes=changed.map(p=>({path:p,sha256:hash(p)})),tree=git(['write-tree'],env).trim();
 if(git(['rev-parse','HEAD']).trim()!==parent)throw Error('Concurrent HEAD changed; use actual new HEAD after inspection');
 for(const h of hashes)if(hash(h.path)!==h.sha256)throw Error('Concurrent selected file edit: '+h.path);
 const commit=git(['commit-tree',tree,'-p',parent],env,'Author independent game-pitch scenes and preserve reviewed voice measurement workflow\n').trim();
 const paths=git(['diff-tree','--no-commit-id','--name-only','-r',commit]).trim().split('\n').filter(Boolean).sort();
 if(JSON.stringify(paths)!==JSON.stringify([...changed].sort()))throw Error('Final commit paths differ from reviewed index');
 git(['update-ref','HEAD',commit,parent]);
 for(const p of changed)git(['restore','--staged','--source='+commit,'--',p]);
 const foreignIndexAfter=foreignEntriesHash();
 if(foreignIndexAfter!==foreignIndexBefore)throw Error('Foreign staged blobs changed; inspect without resetting');
 const push=cp.spawnSync('git',['push','origin','main'],{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:16e6});
 const local=git(['rev-parse','HEAD']).trim(),remote=git(['ls-remote','origin','refs/heads/main']).trim().split(/\s+/)[0];
 write(verificationFile,{schemaVersion:1,verifiedAt:stamp(),sceneProgressCommit:commit,parent,commitPaths:paths,reviewedFileHashes:hashes,pushExitCode:push.status,pushOutput:(push.stdout+push.stderr).trim(),normalPush:true,forcePush:false,localSha:local,remoteSha:remote,remoteMatches:local===remote,foreignIndexBefore,foreignIndexAfter,foreignStagedBefore:foreignStaged,otherUsersFilesIncluded:false,newRasterCommitted:0,mediaCommitted:false,completedVideoDelivery:false,narrationApproval:false,finalTimingApproval:false,finalRenderQaCollectionUpload:false});
 if(push.status!==0||local!==remote)throw Error('Push/remote match incomplete; actual outcome saved');
 console.log(JSON.stringify({commit,parent,pathCount:changed.length,pushExitCode:push.status,localSha:local,remoteSha:remote,newRasterCommitted:0,completedVideoDelivery:false}));
}finally{if(fs.existsSync(index))fs.unlinkSync(index);}
