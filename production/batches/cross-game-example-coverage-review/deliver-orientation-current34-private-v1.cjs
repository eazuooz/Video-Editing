// Select current orientation source/metadata with a temporary index; preserve shared work.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),slug='game-math-orientation-matrices';
const O='projects/'+slug+'/revision-teaching-clarity-v1',B='production/batches/cross-game-example-coverage-review';
const gitBin='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe';
const normal={...process.env,PATH:path.dirname(gitBin)+path.delimiter+process.env.PATH};
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8').replace(/^\uFEFF/,''));
const save=(f,v)=>{const p=path.join(root,f),t=p+'.git-'+process.pid+'.tmp';fs.writeFileSync(t,JSON.stringify(v,null,2)+'\n',{flag:'wx'});fs.renameSync(t,p);};
function run(exe,args,env=normal,input){const r=cp.spawnSync(exe,args,{cwd:root,env,input,encoding:'utf8',windowsHide:true,maxBuffer:256e6});if(r.status!==0)throw Error(args.join(' ')+'\n'+r.stdout+'\n'+r.stderr);return r.stdout.trimEnd();}
const git=(args,env=normal,input)=>run(gitBin,args,env,input);
const settings=read(O+'/publishing/private-settings-direct-review-v1.json');
if(!settings.privateSavedAndReopened||!settings.fullAvailableSettingsVerified||settings.actualVideoId!=='orq0TMVkFts')throw Error('Actual private available settings required.');
const promotion=read(O+'/current34-main-promotion-v1.json');
const transition=read(O+'/current34-main-private-update-v1.json');
for(const row of promotion.otherProtectedInputs.concat(promotion.repairCandidates))if(sha(fs.readFileSync(path.join(root,row.path)))!==row.sha256)throw Error('Protected input changed: '+row.path);
if(sha(fs.readFileSync(path.join(root,promotion.baselineMain.path)))!==promotion.baselineMain.sha256)throw Error('Exact original main backup differs.');
if(sha(fs.readFileSync(path.join(root,transition.currentMain.path)))!==transition.currentMain.sha256)throw Error('Current intentional main transition differs.');
const afterRepair=process.argv.includes('--repair-whitespace');
if(afterRepair){const failure=read(O+'/publishing/git-precommit-failure-v1.json');if(failure.commitCreated||!failure.repair.pythonAstIdentical)throw Error('Actual precommit-only repair evidence required.');}
const prepareProof=O+'/publishing/git-preflight-rebuild-v'+(afterRepair?'2':'1')+'.json';
if(process.argv.includes('--prepare')){
 if(fs.existsSync(path.join(root,prepareProof)))throw Error('Preparation exists; use its current explicit plan, not another rebuild.');
 const shared=path.join(root,'projects/rebuild-index.json'),sharedBytes=fs.readFileSync(shared);
 const foreign=fs.readdirSync(path.join(root,'projects')).filter(s=>s!==slug).map(s=>'projects/'+s+'/rebuild.json').filter(f=>fs.existsSync(path.join(root,f))).map(f=>({path:f,sha256:sha(fs.readFileSync(path.join(root,f)))}));
 const originalWrite=fs.writeFileSync;let sharedNoop=false;
 fs.writeFileSync=function(p,data,...args){
  if(typeof p!=='number'&&path.resolve(String(p)).toLowerCase()===shared.toLowerCase()){
   const intended=Buffer.isBuffer(data)?data:Buffer.from(data,'utf8');
   const norm=b=>b.toString('utf8').replace(/^\uFEFF/,'').replace(/\r\n/g,'\n');
   if(!fs.readFileSync(shared).equals(sharedBytes)||norm(intended)!==norm(sharedBytes))throw Error('Shared index changed or generated content differs; preserve it.');
   sharedNoop=true;return;
  }
  return originalWrite.call(fs,p,data,...args);
 };
 try{require(path.join(root,'scripts/build-rebuild-manifests.cjs')).generate(slug);}finally{fs.writeFileSync=originalWrite;}
 if(!sharedBytes.equals(fs.readFileSync(shared)))throw Error('Shared index bytes changed.');
 for(const f of foreign)if(sha(fs.readFileSync(path.join(root,f.path)))!==f.sha256)throw Error('Foreign rebuild changed: '+f.path);
 save(prepareProof,{preparedAt:new Date().toISOString(),ownSlug:slug,sharedIndexWriteNoop:sharedNoop,sharedIndexSha256:sha(sharedBytes),foreignRebuilds:foreign,foreignRebuildsUnchanged:true,other78ProtectedUnchanged:true,originalMainBackupUnchanged:true,repairCandidatesUnchanged:true,newGitMedia:0});
 console.log(run(path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),['-X','utf8',B+'/plan-orientation-current34-git-v1.py']));
 process.exit(0);
}
if(!process.argv.includes('--deliver'))throw Error('Use --prepare then --deliver.');
const proofPath=O+'/publishing/production-git-verification-v1.json';
if(fs.existsSync(path.join(root,proofPath)))throw Error('Delivery outcome exists; inspect it before any follow-up.');
const selectionPath=O+'/publishing/production-git-selection-v1.json';
const plan=read(selectionPath);
const parent=git(['rev-parse','HEAD']),branch=git(['symbolic-ref','--short','HEAD']);
if(parent!==plan.parent)throw Error('HEAD advanced; review a fresh plan before staging.');
const files=plan.selectedFiles.map(f=>f.path).concat(selectionPath),subsets=new Map(plan.sharedSubsetBlobs.map(f=>[f.path,f]));
if(files.some(f=>/\.(?:mp4|webm|wav|mp3|m4a|ogg|flac|zip|png|jpe?g|gif|webp|bin)$/i.test(f)))throw Error('Media or raster selected.');
for(const f of plan.selectedFiles)if(sha(fs.readFileSync(path.join(root,f.path)))!==f.workingSha256)throw Error('Planned input changed: '+f.path);
const external=path.resolve(root,git(['rev-parse','--git-path','index']));
const externalBytes=fs.readFileSync(external),externalEntries=git(['ls-files','--stage','-z']);
const sharedBefore=new Map([...subsets.keys()].map(f=>[f,sha(fs.readFileSync(path.join(root,f)))]));
const temp=fs.mkdtempSync(path.join(root,'.git','orientation-current34-private-'));
const env={...normal,GIT_INDEX_FILE:path.join(temp,'index')};
fs.writeFileSync(path.join(temp,'external-index-before.bin'),externalBytes);
fs.writeFileSync(path.join(temp,'external-index-before.entries'),externalEntries);
function preserved(){
 if(sha(fs.readFileSync(external))!==sha(externalBytes)||git(['ls-files','--stage','-z'])!==externalEntries)throw Error('External index changed; preserve and inspect.');
 for(const [f,h] of sharedBefore)if(sha(fs.readFileSync(path.join(root,f)))!==h)throw Error('Shared working file changed: '+f);
}
git(['read-tree',parent],env);
const ordinary=files.filter(f=>!subsets.has(f));
for(let start=0;start<ordinary.length;start+=50)git(['add','--',...ordinary.slice(start,start+50)],env);
const expected=new Map();
const ordinaryHashes=git(['hash-object','--stdin-paths'],env,ordinary.join('\n')+'\n').split(/\r?\n/);
ordinary.forEach((f,i)=>expected.set(f,ordinaryHashes[i]));
for(const [f,entry] of subsets){
 if(sha(Buffer.from(entry.content,'utf8'))!==entry.sha256)throw Error('Subset content differs: '+f);
 const blob=git(['hash-object','-w','--stdin'],env,entry.content);
 git(['update-index','--add','--cacheinfo','100644',blob,f],env);expected.set(f,blob);
}
const status=git(['diff','--cached','--name-status','-z',parent],env).split('\0').filter(Boolean),changes=[];
for(let i=0;i<status.length;i+=2)changes.push({status:status[i],path:status[i+1]});
if(changes.some(e=>!files.includes(e.path)||!['A','M'].includes(e.status)))throw Error('Unexpected foreign path or deletion.');
const staged=new Map(git(['ls-files','--stage','-z'],env).split('\0').filter(Boolean).map(line=>{const[m,f]=line.split('\t');return[f,m.split(' ')[1]];}));
for(const [f,h] of expected)if(staged.get(f)!==h)throw Error('Staged blob differs: '+f);
const checks={whitespace:git(['diff','--cached','--check',parent],env),
 media:run(process.execPath,['scripts/media-policy.cjs'],env),
 currentOrientationRebuild:run(process.execPath,['scripts/build-rebuild-manifests.cjs',slug,'--check'],env)};
preserved();if(git(['rev-parse','HEAD'])!==parent)throw Error('HEAD advanced; no commit.');
const tree=git(['write-tree'],env),commit=git(['commit-tree',tree,'-p',parent],env,'Restore detailed people and objects in orientation lesson and verify private delivery\n');
const proof={schemaVersion:1,recordedAt:new Date().toISOString(),actualVideoId:'orq0TMVkFts',parent,branch,commit,selectedPaths:files,changedPaths:changes,checks,
 sharedFilesStagedAsOwnedRuleSubsets:[...subsets.keys()],allStagedBlobsVerified:true,newImagesAdded:0,mediaAdded:0,
 externalIndexSha256Before:sha(externalBytes),externalIndexUnchanged:true,sharedWorkingFilesUnchanged:true,
 originalMainBackupUnchanged:true,other78ProtectedUnchanged:true,repairCandidatesUnchanged:true,
 automaticAdCheckPassed:false,scheduleReplacementVerified:false,pushed:false,
 precommitWhitespaceRepair:fs.existsSync(path.join(root,O+'/publishing/git-precommit-failure-v1.json'))?O+'/publishing/git-precommit-failure-v1.json':null};
preserved();git(['update-ref','HEAD',commit,parent]);save(proofPath,proof);
try{git(['push','origin',commit+':refs/heads/'+branch]);}catch(e){proof.pushFailure=e.message;save(proofPath,proof);throw e;}
const local=git(['rev-parse','HEAD']),remote=git(['ls-remote','origin','refs/heads/'+branch]).split(/\s/)[0];
if(local!==commit||remote!==commit)throw Error('Concurrent local/remote advance; inspect the saved commit.');
const remoteBlobs=new Map(git(['ls-tree','-r','-z',remote]).split('\0').filter(Boolean).map(line=>{const[m,f]=line.split('\t');return[f,m.split(' ')[2]];}));
for(const [f,h] of expected)if(remoteBlobs.get(f)!==h)throw Error('Final remote blob differs: '+f);
preserved();Object.assign(proof,{pushed:true,localCommit:local,remoteCommit:remote,exactLocalRemoteMatch:true,allFinalRemoteBlobsVerified:true,
 verifiedBlobCount:expected.size,externalIndexSha256After:sha(fs.readFileSync(external)),verifiedAt:new Date().toISOString()});save(proofPath,proof);
console.log(JSON.stringify({commit,remote,verifiedBlobs:expected.size,newImages:0,media:0,externalIndexUnchanged:true,pushed:true}));
