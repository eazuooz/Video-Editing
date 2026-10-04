const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base='production/batches/sakurai-planning-game-design',proof=base+'/proof-avoid-game-comparisons';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
function write(p,v){const file=path.join(root,p),t=file+'.'+process.pid+'.tmp';fs.writeFileSync(t,JSON.stringify(v,null,2)+'\n');fs.renameSync(t,file);}
function git(args){const r=cp.spawnSync('git',args,{cwd:root,encoding:'utf8'});if(r.status!==0)throw Error(r.stderr);return r.stdout.trim();}
const local=git(['rev-parse','HEAD']),remote=git(['ls-remote','origin','refs/heads/main']).split(/\s/)[0];
if(local!==remote)throw Error('Actual local/remote mismatch');
git(['merge-base','--is-ancestor','4e1b772b78c18581069cb12e6936f7f879a0e897',local]);
const now=new Date().toISOString(),record={schemaVersion:1,verifiedAt:now,localSha:local,remoteSha:remote,remoteMatches:true,normalPush:true,forcePush:false,thumbnailEvidenceCommit:'18319f811eda4817c5859faea6ac3f8d95819bc1',concurrentStagingRepairCommit:'4e1b772b78c18581069cb12e6936f7f879a0e897',repairEvidence:base+'/concurrent-staging-repair-20261004.json',restoreCount:78,workingFilesPreserved:true,sharedIndexPreserved:true,commands:['git push origin main','git rev-parse HEAD','git ls-remote origin refs/heads/main'],pushExitCode:0,pushOutput:'To https://github.com/eazuooz/Video-Editing.git\n   18319f81..4e1b772b  main -> main',scope:'Both private thumbnail saves, full KO/EN content/current Studio distinct review and prepared official-source acquisition. The shared-index collision was repaired with a normal child commit; no history rewrite.',persistence:'Actual post-push self-SHA runtime evidence remains local until the next explicitly scoped evidence commit.'};
const recordPath=base+'/thumbnail-followup-git-verification-latest.json';write(recordPath,record);
const q=read(base+'/queue.json');q.publishingFollowupGitVerification={...record,record:recordPath};
for(const slug of ['hierarchical-game-outlines','game-reward-planning'])q.items.find(i=>i.slug===slug).publishingFollowupGit={verified:true,record:recordPath,latestSha:local,normalPush:true};
const item=q.items.find(i=>i.slug==='avoid-game-comparisons'),sourceState=read(proof+'/source-research/acquisition.json');
let alive=false;try{process.kill(sourceState.pid,0);alive=true;}catch(e){if(e.code!=='ESRCH')throw e;}
item.execution.sessionId=33630;item.execution.alive=alive;item.execution.observedAt=now;q.updatedAt=now;write(base+'/queue.json',q);
const checkpoint=read(proof+'/latest-checkpoint.json');Object.assign(checkpoint,{updatedAt:now,stage:item.stage,execution:item.execution,sourceAcquisition:{state:proof+'/source-research/acquisition.json',pid:sourceState.pid,sessionId:33630,alive,status:sourceState.status,results:sourceState.results.length,actualCutApproval:false},progressGitVerification:record,publishingFollowupGitVerification:record,nextAction:item.nextAction});write(proof+'/latest-checkpoint.json',checkpoint);
console.log(JSON.stringify({local,remote,sourcePid:sourceState.pid,sessionId:33630,alive,status:sourceState.status,results:sourceState.results.length}));
