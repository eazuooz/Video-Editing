// Resume the already-created, reviewed commit after an external Git index lock.
// No new media, commit recreation, lock removal or foreign staged mutation.
const fs=require('node:fs'),cp=require('node:child_process'),crypto=require('node:crypto');
const prefix='production/research/game-lighting-history/',commit='7d65467c4702ad3989bc4738f369c1bb10c0ee94';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex'),json=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const paths=json(prefix+'episode03-selective-paths-v21.json'),checks=json(prefix+'episode03-selective-checks-v21.json'),shared=new Set(['.gitignore','shared/git-essential-images.json']);
function git(args,input){const r=cp.spawnSync('git',args,{input,encoding:Buffer.isBuffer(input)?undefined:'utf8',windowsHide:true,maxBuffer:128e6});if(r.status!==0)throw Error('git '+args.join(' ')+'\n'+r.stdout+r.stderr);return String(r.stdout);}
if(fs.existsSync('.git/index.lock'))throw Error('External index lock remains; wait for its actual owner, never delete');
if(git(['rev-parse','HEAD']).trim()!==commit||git(['rev-parse',commit+'^']).trim()!==checks.parent)throw Error('Actual HEAD/parent changed; inspect before resuming');
const foreignIndex=()=>sha(Buffer.from(git(['ls-files','--stage','-z']).split('\0').filter(Boolean).filter(s=>{const p=s.slice(s.indexOf('\t')+1);return shared.has(p)||!paths.includes(p);}).join('\0')));
const before=foreignIndex();if(before!==checks.foreignIndexBefore)throw Error('Foreign index changed; preserve and inspect');
const changed=git(['diff-tree','--no-commit-id','--name-only','-r','-z',commit]).split('\0').filter(Boolean);
if(!changed.length||changed.some(p=>!paths.includes(p))||git(['diff-tree','--diff-filter=D','--no-commit-id','--name-only','-r',commit]).trim())throw Error('Unexpected committed path/deletion');
const snapshots=[];
for(const p of paths){const bytes=cp.execFileSync('git',['show',commit+':'+p],{maxBuffer:128e6,windowsHide:true}),working=fs.readFileSync(p),blob=git(['rev-parse',commit+':'+p]).trim();if(!shared.has(p)&&git(['hash-object','--path='+p,'--stdin'],working).trim()!==blob)throw Error('Owned working content changed after normal Git filters: '+p);snapshots.push({path:p,blob,sha256:sha(bytes),workingSha256:sha(working),normalGitTextFiltersApplied:sha(bytes)!==sha(working),sharedPatchFromActualHead:shared.has(p)});}
const currentEntries=new Map(git(['ls-files','--stage','-z']).split('\0').filter(Boolean).map(s=>[s.slice(s.indexOf('\t')+1),s.split(' ')[1]]));
const parentEntries=new Map(git(['ls-tree','-r','-z',checks.parent]).split('\0').filter(Boolean).map(s=>[s.slice(s.indexOf('\t')+1),s.split(' ')[2].split('\t')[0]]));
for(const s of snapshots.filter(s=>!shared.has(s.path))){const staged=currentEntries.get(s.path);if(staged&&staged!==s.blob&&staged!==parentEntries.get(s.path))throw Error('Unexpected newly staged owned content: '+s.path);}
git(['restore','--staged','--source='+commit,'--pathspec-from-file=-','--pathspec-file-nul'],Buffer.from(changed.filter(p=>!shared.has(p)).join('\0')+'\0'));
const after=foreignIndex();if(after!==before)throw Error('Foreign index mismatch after explicit owned path restoration');
const r=cp.spawnSync('git',['push','origin','main'],{encoding:'utf8',windowsHide:true,maxBuffer:16e6});
const local=git(['rev-parse','HEAD']).trim(),remote=git(['ls-remote','origin','refs/heads/main']).trim().split(/\s+/)[0];
const record={schemaVersion:1,verifiedAt:new Date().toISOString(),commit,parent:checks.parent,paths:changed,snapshots,normalPush:true,forcePush:false,pushExitCode:r.status,pushOutput:(r.stdout+r.stderr).trim(),localSha:local,remoteSha:remote,remoteMatches:local===remote,foreignIndexBefore:before,foreignIndexAfter:after,foreignIndexPreserved:before===after,foreignStagedSharedFilesPreserved:true,images:checks.images,mediaCommitted:0,actualVideoId:'lIDe30dqC28',privateDeliveryVerified:true,schedulingStillPending:true,recovery:{reason:'Original worker created this exact commit, then encountered an external .git/index.lock while synchronizing owned staged entries. The lock naturally disappeared. Resume restored only the explicit owned non-shared paths in one operation; no commit was recreated and no lock was deleted.',originalSessionId:74082},persistence:'Actual post-push evidence; never predicts its own future SHA.'};
fs.writeFileSync(prefix+'episode03-selective-git-verification-v21.json',JSON.stringify(record,null,2)+'\n');
if(r.status!==0||local!==remote)throw Error('Actual push/remote mismatch recorded');
console.log(JSON.stringify({commit,parent:checks.parent,paths:changed.length,images:checks.images.length,media:0,localSha:local,remoteSha:remote,foreignIndexPreserved:true},null,2));
