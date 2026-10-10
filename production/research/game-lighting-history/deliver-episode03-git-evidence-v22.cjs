// Persist observed delivery evidence with a fresh, explicit temporary index.
const fs=require('node:fs'),cp=require('node:child_process'),crypto=require('node:crypto'),path=require('node:path');
const prefix='production/research/game-lighting-history/',slug='game-lighting-history-03';
const selected=[prefix+'episode03-selective-git-verification-v21.json',prefix+'resume-episode03-git-delivery-v21.cjs',prefix+'deliver-episode03-git-evidence-v22.cjs',prefix+'checkpoint.json','projects/'+slug+'/project.json','projects/'+slug+'/publishing/youtube-upload-v21.json','projects/'+slug+'/README.md','projects/'+slug+'/rebuild.json'];
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function git(a,env=process.env,input){const r=cp.spawnSync('git',a,{env,input,encoding:Buffer.isBuffer(input)?undefined:'utf8',windowsHide:true,maxBuffer:128e6});if(r.status!==0)throw Error('git '+a.join(' ')+'\n'+r.stdout+r.stderr);return String(r.stdout);}
const prior=JSON.parse(fs.readFileSync(selected[0]));if(!prior.remoteMatches||!prior.foreignIndexPreserved||prior.pushExitCode!==0)throw Error('Actual previous normal push required');
const parent=git(['rev-parse','HEAD']).trim(),index=path.resolve('.git','lighting03-evidence-'+Date.now()+'.index'),env={...process.env,GIT_INDEX_FILE:index};
if(git(['symbolic-ref','--short','HEAD']).trim()!=='main'||git(['diff','--cached','--name-only','-z']).split('\0').some(p=>selected.includes(p)))throw Error('Unexpected branch/staged own path');
const foreign=()=>sha(Buffer.from(git(['ls-files','--stage','-z']).split('\0').filter(Boolean).filter(s=>!selected.includes(s.slice(s.indexOf('\t')+1))).join('\0'))),before=foreign(),snapshots=[];
try{
git(['read-tree',parent],env);for(const p of selected){const bytes=fs.readFileSync(p),blob=git(['hash-object','-w','--path='+p,'--stdin'],env,bytes).trim();git(['update-index','--add','--cacheinfo','100644,'+blob+','+p],env);snapshots.push({path:p,blob,workingSha256:sha(bytes)});}
const checks=[];for(const args of [['scripts/media-policy.cjs'],['scripts/build-rebuild-manifests.cjs',slug,'--check']]){const r=cp.spawnSync(process.execPath,args,{env,encoding:'utf8',windowsHide:true,maxBuffer:16e6});checks.push({command:'node '+args.join(' '),exitCode:r.status,output:(r.stdout+r.stderr).trim()});if(r.status!==0)throw Error(checks.at(-1).output);}
git(['diff','--cached','--check',parent],env);
const changed=git(['diff','--cached','--name-only','-z',parent],env).split('\0').filter(Boolean).sort();if(changed.length!==selected.length||changed.some(p=>!selected.includes(p)))throw Error('Exact evidence path mismatch');
for(const s of snapshots)if(sha(fs.readFileSync(s.path))!==s.workingSha256||git(['rev-parse',':'+s.path],env).trim()!==s.blob)throw Error('Selected evidence changed');
if(foreign()!==before||git(['rev-parse','HEAD']).trim()!==parent)throw Error('Concurrent foreign index/HEAD change; preserve and inspect');
const tree=git(['write-tree'],env).trim(),commit=git(['commit-tree',tree,'-p',parent],env,'Record actual rendering episode03 private delivery Git verification\n').trim();
for(const s of snapshots)if(git(['rev-parse',commit+':'+s.path]).trim()!==s.blob)throw Error('Final blob mismatch');
git(['update-ref','HEAD',commit,parent]);git(['restore','--staged','--source='+commit,'--pathspec-from-file=-','--pathspec-file-nul'],process.env,Buffer.from(changed.join('\0')+'\0'));
const after=foreign();if(after!==before)throw Error('Foreign index mismatch');
const push=cp.spawnSync('git',['push','origin','main'],{encoding:'utf8',windowsHide:true,maxBuffer:16e6}),local=git(['rev-parse','HEAD']).trim(),remote=git(['ls-remote','origin','refs/heads/main']).trim().split(/\s+/)[0];
const record={schemaVersion:1,verifiedAt:new Date().toISOString(),commit,parent,paths:changed,snapshots,checks,normalPush:true,pushExitCode:push.status,pushOutput:(push.stdout+push.stderr).trim(),localSha:local,remoteSha:remote,remoteMatches:local===remote,foreignIndexBefore:before,foreignIndexAfter:after,foreignIndexPreserved:before===after,imagesAdded:0,mediaAdded:0,actualVideoId:'lIDe30dqC28',previousActualDeliveryCommit:prior.commit,humanListeningApproved:false,publicRightsApproved:false,schedulingStillPending:true,persistence:'Post-push observation, not an estimated own future SHA.'};
fs.writeFileSync(prefix+'episode03-git-evidence-verification-v22.json',JSON.stringify(record,null,2)+'\n');if(push.status!==0||local!==remote)throw Error('Actual push mismatch recorded');console.log(JSON.stringify({commit,parent,paths:changed.length,imagesAdded:0,mediaAdded:0,localSha:local,remoteSha:remote,foreignIndexPreserved:true},null,2));
}finally{if(fs.existsSync(index))fs.unlinkSync(index);}
