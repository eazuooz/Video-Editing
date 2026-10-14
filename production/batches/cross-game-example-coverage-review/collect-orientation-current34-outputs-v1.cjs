// Run the standard collector once, preserving the shared index and foreign manifests.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),slug='game-math-orientation-matrices';
const o=path.join(root,'projects',slug,'revision-teaching-clarity-v1');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const resourceIndex=process.argv.indexOf('--resource');
if(resourceIndex<0)throw Error('Fresh actual CPU resource path required.');
const resourcePath=path.resolve(root,process.argv[resourceIndex+1]);
const resource=read(resourcePath);
if(Date.now()-Date.parse(resource.observedAt)>=240000||resource.ownHeavyJobs!==0||resource.cpuLoadPercent>=85||resource.freePhysicalMemoryKiB<=8000000)throw Error('Current CPU resource is stale or ineligible.');
const hash=p=>{const h=crypto.createHash('sha256'),fd=fs.openSync(p,'r'),buf=Buffer.alloc(1048576);try{let n;while((n=fs.readSync(fd,buf,0,buf.length,null))>0)h.update(buf.subarray(0,n));}finally{fs.closeSync(fd);}return h.digest('hex');};
const save=(p,v)=>{const t=p+'.writing';fs.writeFileSync(t,JSON.stringify(v,null,2)+'\n');fs.renameSync(t,p);};
const proofPath=path.join(o,'current34-four-output-collection-verification-v1.json');
if(fs.existsSync(proofPath))throw Error('Already verified; do not recollect.');
const promotion=read(path.join(o,'current34-main-promotion-v1.json'));
if(!promotion.intentionalProtectedMainTransition||hash(path.join(root,promotion.currentMain.path))!==promotion.currentMain.sha256)throw Error('Current main promotion differs.');
const statePath=path.join(o,'current34-output-collection-execution-v1.json');
if(fs.existsSync(statePath))throw Error('Previous collector attempt exists; inspect actual closure before any retry.');
const shared=path.join(root,'projects/rebuild-index.json'),sharedBytes=fs.readFileSync(shared);
const foreign=fs.readdirSync(path.join(root,'projects')).filter(s=>s!==slug).map(s=>path.join(root,'projects',s,'rebuild.json')).filter(p=>fs.existsSync(p)).map(p=>({path:p,sha256:hash(p)}));
const originalWrite=fs.writeFileSync;
let sharedNoop=false;
fs.writeFileSync=function(p,data,...args){
 if(typeof p!=='number'&&path.resolve(String(p)).toLowerCase()===shared.toLowerCase()){
  const intended=Buffer.isBuffer(data)?data:Buffer.from(data,'utf8');
  if(!fs.readFileSync(shared).equals(sharedBytes))throw Error('Foreign shared index changed; preserve current bytes.');
  const normalize=b=>b.toString('utf8').replace(/^\uFEFF/,'').replace(/\r\n/g,'\n');
  if(normalize(intended)!==normalize(sharedBytes))throw Error('Generated shared index differs; preserve current foreign index.');
  sharedNoop=true;return;
 }
 return originalWrite.call(fs,p,data,...args);
};
save(statePath,{startedAt:new Date().toISOString(),pid:process.pid,cwd:process.cwd(),commandLine:process.argv,resource:path.relative(root,resourcePath).replaceAll('\\','/'),resourceSha256:hash(resourcePath),exitCode:null,stage:'standard-collector-with-shared-index-equality-guard',cpuThreads:2,gpuJobs:0,newGitMedia:0});
process.once('exit',code=>{
 fs.writeFileSync=originalWrite;
 try{
  if(!sharedBytes.equals(fs.readFileSync(shared)))throw Error('Shared index bytes changed.');
  for(const f of foreign)if(hash(f.path)!==f.sha256)throw Error('Foreign rebuild changed: '+f.path);
  if(code!==0){save(statePath,{...read(statePath),finishedAt:new Date().toISOString(),exitCode:code,sharedIndexPreserved:true,foreignRebuildsPreserved:true});return;}
  const report=read(path.join(root,'projects',slug,'production/delivery-output.json'));
  if(report.files.length!==4||report.cueCounts.ko!==244||report.cueCounts.en!==244||report.videos.some(v=>Math.abs(v.duration-1098.616667)>.001))throw Error('Unexpected current delivery.');
  for(const f of report.files)if(hash(path.join(root,f.source))!==f.sha256||hash(path.join(root,report.directory,f.name))!==f.sha256)throw Error('Delivery SHA mismatch.');
  for(const f of promotion.otherProtectedInputs.concat(promotion.repairCandidates))if(hash(path.join(root,f.path))!==f.sha256)throw Error('Protected input changed.');
  const proof={verifiedAt:new Date().toISOString(),files:report.files,fourOutputsCollected:true,
   standardCollector:'scripts/collect-video-output.cjs',singleCollectorAttempt:true,outputIndexSaved:fs.existsSync(path.join(root,'output/index.html')),
   sharedRebuildIndexAlreadyCorrect:sharedNoop,sharedRebuildIndexBytesPreserved:true,foreignRebuildsPreserved:true,foreignRebuildCount:foreign.length,
   other78ProtectedInputsUnchanged:true,repairCandidateUnchanged:true,humanListeningApproved:false,publicRightsApproved:false,newGitMedia:0};
  save(proofPath,proof);save(statePath,{...read(statePath),finishedAt:proof.verifiedAt,exitCode:0,verification:path.relative(root,proofPath).replaceAll('\\','/')});
  const cpPath=path.join(o,'latest-checkpoint.json'),cp=read(cpPath);
  Object.assign(cp,{recordedAt:proof.verifiedAt,stage:'current34-four-outputs-verified-awaiting-single-private-upload',outputCollected:true,
   currentCollectionVerification:path.relative(root,proofPath).replaceAll('\\','/'),next:'One reviewed privatecaptioned upload;all available settings/manualKOEN/localizedEN/CCoff pixels/reopen;selectGit;current09schedule replacement. Baseline6-kP preserved.'});save(cpPath,cp);
  const qp=path.join(__dirname,'queue.json'),q=read(qp);Object.assign(q.currentOrientationReview,{stage:cp.stage,outputCollected:true,
   currentCollectionVerification:cp.currentCollectionVerification,next:cp.next});q.updatedAt=proof.verifiedAt;save(qp,q);
  console.log(JSON.stringify({fourOutputsCollected:true,sharedIndexUnchanged:true,foreignRebuildsUnchanged:foreign.length,shaMatched:true}));
 }catch(error){console.error(error);process.exitCode=1;}
});
process.argv=[process.argv[0],path.join(root,'scripts/collect-video-output.cjs'),slug];
require(path.join(root,'scripts/collect-video-output.cjs'));
