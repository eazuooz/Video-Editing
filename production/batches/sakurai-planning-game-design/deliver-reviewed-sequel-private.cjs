// Selective delivery from the actual shared HEAD. Never copy unrelated staged or shared-file edits.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),proof='production/batches/sakurai-planning-game-design/proof-making-game-sequels/';
const label=process.argv[3]||'final-private-delivery',pathsFile=process.argv[2];
if(!pathsFile||!/^[-a-z0-9]+$/.test(label))throw Error('Explicit path list and safe label required');
const selected=JSON.parse(fs.readFileSync(path.join(root,pathsFile),'utf8'));
const checksFile=proof+label+'-pre-delivery-checks.json',recordFile=proof+label+'-git-verification.json';
if(new Set(selected).size!==selected.length||!selected.includes(checksFile))throw Error('Unique paths including check record required');
const stamp=()=>new Date().toISOString(),digest=b=>crypto.createHash('sha256').update(b).digest('hex');
function json(p){return JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));}
const receipt=json('projects/making-game-sequels/publishing/youtube-upload.json'),qa=json('projects/making-game-sequels/production/final-v2/qa.json');
if(receipt.actualVideoId!=='DWsAfi-fUKw'||!receipt.uploaded||!receipt.privateSaved||!receipt.fullSettingsVerified||receipt.privacy!=='private'||receipt.schedule!==null||!qa.technicalApproved)throw Error('Actual single private save/settings and current QA must be verified first');
function git(args,env=process.env,input){const r=cp.spawnSync('git',args,{cwd:root,env,input,encoding:input instanceof Buffer?undefined:'utf8',windowsHide:true,maxBuffer:128e6});if(r.status!==0)throw Error('git '+args.join(' ')+'\n'+r.stdout+r.stderr);return String(r.stdout);}
if(git(['symbolic-ref','--short','HEAD']).trim()!=='main')throw Error('Unexpected branch');
const parent=git(['rev-parse','HEAD']).trim(),index=path.join(root,'.git','sequel-private-'+Date.now()+'.index'),env={...process.env,GIT_INDEX_FILE:index},commands=[],snapshots=[];
const staged=git(['diff','--cached','--name-only','-z']).split('\0').filter(Boolean);
if(staged.some(p=>selected.includes(p)))throw Error('Selected path already staged; preserve and inspect');
const foreignHash=()=>digest(Buffer.from(git(['ls-files','--stage','-z']).split('\0').filter(Boolean).filter(s=>!selected.includes(s.slice(s.indexOf('\t')+1))).join('\0'))),foreignBefore=foreignHash();
const raster=/\.(?:png|jpe?g|webp|gif|bmp|tiff?)$/i,newImages=selected.filter(p=>raster.test(p));
const workingRegistry=json('shared/git-essential-images.json'),ownEntries=workingRegistry.entries.filter(e=>e.project==='making-game-sequels'&&newImages.includes(e.path));
if(ownEntries.length!==newImages.length||newImages.some(p=>!ownEntries.some(e=>e.path===p)))throw Error('Each selected image needs exact reviewed registry entry');
const overrides=new Map();
if(selected.includes('shared/git-essential-images.json')){
 const registry=JSON.parse(git(['show',parent+':shared/git-essential-images.json']));
 for(const e of ownEntries){if(!registry.allowedPurposes.includes(e.purpose)||!e.reason||!e.reviewedAt||digest(fs.readFileSync(path.join(root,e.path)))!==e.sha256)throw Error('Invalid essential image '+e.path);const old=registry.entries.find(x=>x.path===e.path);if(old&&old.sha256!==e.sha256)throw Error('Existing essential image changed');if(!old)registry.entries.push(e);}
 overrides.set('shared/git-essential-images.json',Buffer.from(JSON.stringify(registry,null,2)+'\n'));
}
if(selected.includes('.gitignore')){let ignore=git(['show',parent+':.gitignore']).replace(/\s*$/,'')+'\n';for(const p of newImages)if(!ignore.split(/\r?\n/).includes('!'+p))ignore+='!'+p+'\n';overrides.set('.gitignore',Buffer.from(ignore));}
function stage(p){
 if(/\.(?:mp4|webm|wav|m4a|mp3|zip|7z|info\.json)$/i.test(p)||/research-local|\.raw-original$|\.meta$/.test(p))throw Error('Local-only media/source selected '+p);
 if(raster.test(p)&&!ownEntries.some(e=>e.path===p))throw Error('Unreviewed raster '+p);
 const working=fs.readFileSync(path.join(root,p)),bytes=overrides.get(p)||working;if(p.endsWith('.json'))JSON.parse(bytes.toString('utf8'));
 const blob=git(['hash-object','-w','--path='+p,'--stdin'],env,bytes).trim();git(['update-index','--add','--cacheinfo','100644,'+blob+','+p],env);snapshots.push({path:p,blob,capturedSha256:digest(bytes),workingSha256:digest(working),capturedAt:stamp(),workingCopyPreserved:true,sharedPatchFromActualHead:overrides.has(p)});
}
function node(args){const r=cp.spawnSync(process.execPath,args,{cwd:root,env,encoding:'utf8',windowsHide:true,maxBuffer:16e6});commands.push({command:'node '+args.join(' '),exitCode:r.status,output:(r.stdout+r.stderr).trim()});if(r.status!==0)throw Error('Check failed '+args.join(' ')+'\n'+r.stdout+r.stderr);}
try{
 git(['read-tree',parent],env);for(const p of selected.filter(p=>p!==checksFile))stage(p);
 node(['scripts/media-policy.cjs']);node(['scripts/review-video-duplicates.cjs','making-game-sequels','--check']);node(['scripts/build-rebuild-manifests.cjs','making-game-sequels','--check']);node(['scripts/build-rebuild-manifests.cjs','avoid-game-comparisons','--check']);node(['motion-canvas/node_modules/typescript/bin/tsc','-p','motion-canvas/tsconfig.making-game-sequels.json','--noEmit']);git(['diff','--cached','--check',parent],env);
 const record={schemaVersion:1,checkedAt:stamp(),parent,commands,explicitPaths:selected,snapshots,temporaryIndexFromActualHead:true,foreignStagedBefore:staged,foreignIndexBefore:foreignBefore,newImages:newImages.length,essentialImages:ownEntries,mediaAdded:0,npm:'Unavailable; exact Node hooks used.',whitespacePassed:true,scope:'Reviewed final-v2 sequel production, all encoded caption/cut pixels, technical QA, four output records, actual single private Studio settings and minimal essential images. Human listening/pronunciation/public-rights decisions remain pending.',globalWorkingTreeRebuildPassed:false,globalLimitation:'No whole working-tree pass for unrelated unfinished projects.',completedVideoCount:12,remainingNonduplicateProductions:11,actualVideoId:receipt.actualVideoId};
 fs.writeFileSync(path.join(root,checksFile),JSON.stringify(record,null,2)+'\n');stage(checksFile);
 const changed=git(['diff','--cached','--name-only','-z',parent],env).split('\0').filter(Boolean);if(!changed.length||changed.some(p=>!selected.includes(p))||git(['diff','--cached','--diff-filter=D','--name-only',parent],env).trim())throw Error('Unexpected or deleted paths');git(['diff','--cached','--check',parent],env);
 const tree=git(['write-tree'],env).trim();if(git(['rev-parse','HEAD']).trim()!==parent)throw Error('Concurrent HEAD changed; inspect and rebase selection');
 const commit=git(['commit-tree',tree,'-p',parent],env,`Deliver reviewed sequel video and verified private settings: ${label}\n`).trim(),committed=git(['diff-tree','--no-commit-id','--name-only','-r',commit]).trim().split('\n').filter(Boolean).sort();
 if(JSON.stringify(committed)!==JSON.stringify([...changed].sort()))throw Error('Final paths differ');for(const s of snapshots.filter(s=>changed.includes(s.path)))if(git(['rev-parse',commit+':'+s.path]).trim()!==s.blob)throw Error('Final blob differs '+s.path);
 git(['update-ref','HEAD',commit,parent]);for(const p of changed)git(['restore','--staged','--source='+commit,'--',p]);const foreignAfter=foreignHash();if(foreignAfter!==foreignBefore)throw Error('Foreign index changed; do not discard');
 const push=cp.spawnSync('git',['push','origin','main'],{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:16e6}),local=git(['rev-parse','HEAD']).trim(),remote=git(['ls-remote','origin','refs/heads/main']).trim().split(/\s+/)[0];
 fs.writeFileSync(path.join(root,recordFile),JSON.stringify({schemaVersion:1,verifiedAt:stamp(),label,commit,parent,commitPaths:committed,snapshots:snapshots.filter(s=>changed.includes(s.path)),pushExitCode:push.status,pushOutput:(push.stdout+push.stderr).trim(),normalPush:true,forcePush:false,localSha:local,remoteSha:remote,remoteMatches:local===remote,foreignStagedBefore:staged,foreignIndexBefore:foreignBefore,foreignIndexAfter:foreignAfter,otherUsersFilesIncluded:false,newRasterCommitted:newImages.length,essentialImages:ownEntries,mediaCommitted:false,completedVideoDelivery:true,completedVideoCount:12,remainingNonduplicateProductions:11,actualVideoId:receipt.actualVideoId,persistence:'Actual post-push evidence is local until a following explicit evidence commit; no self-SHA predicted.'},null,2)+'\n');
 if(push.status!==0||local!==remote)throw Error('Push/remote verification incomplete; actual outcome recorded');console.log(JSON.stringify({commit,parent,paths:changed.length,newImages:newImages.length,media:0,pushExitCode:push.status,localSha:local,remoteSha:remote}));
}finally{if(fs.existsSync(index))fs.unlinkSync(index);}
