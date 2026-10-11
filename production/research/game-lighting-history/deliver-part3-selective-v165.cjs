// Guarded same-ID private delivery. Exact paths, actual HEAD, isolated index;
// no force-add/push, foreign working/index mutation, media or future own SHA.
const fs=require('node:fs'),cp=require('node:child_process'),crypto=require('node:crypto'),path=require('node:path');
const prefix='production/research/game-lighting-history/',slug='game-lighting-history-04-3',registry='shared/git-essential-images.json';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function git(args,env=process.env,input){const r=cp.spawnSync('git',args,{env,input,encoding:Buffer.isBuffer(input)?undefined:'utf8',windowsHide:true,maxBuffer:128e6});if(r.status!==0)throw Error('git '+args.join(' ')+'\n'+r.stdout+r.stderr);return String(r.stdout)}
const plan=JSON.parse(fs.readFileSync(prefix+'part3-selective-paths-v165.json'));
const receipt=JSON.parse(fs.readFileSync('projects/'+slug+'/publishing/youtube-upload.json'));
if(!receipt.privateSaved||!receipt.fullSettingsVerified||!receipt.checksPassed||receipt.actualVideoId!=='ydW9Glmh0nM')throw Error('Actual verified private delivery required');
const selected=[...new Set([...plan.paths,prefix+'part3-selective-paths-v165.json',prefix+'deliver-part3-selective-v165.cjs',registry])].sort();
if(git(['symbolic-ref','--short','HEAD']).trim()!=='main')throw Error('Unexpected branch');
const parent=git(['rev-parse','HEAD']).trim(),externalIndex=git(['rev-parse','--git-path','index']).trim(),indexBefore=sha(fs.readFileSync(externalIndex)),entriesBefore=sha(Buffer.from(git(['ls-files','--stage','-z'])));
const staged=git(['diff','--cached','--name-only','-z']).split('\0').filter(Boolean),overlap=staged.filter(p=>selected.includes(p)&&p!==registry);
if(overlap.length)throw Error('Preserve staged selected paths and inspect first: '+overlap.join(', '));
const idx=path.resolve('.git','lighting-part3-v165-'+Date.now()+'.index'),env={...process.env,GIT_INDEX_FILE:idx};
const snapshots=[],checks=[];
try{
 git(['read-tree',parent],env);
 const baseline=JSON.parse(git(['show',parent+':'+registry])),working=JSON.parse(fs.readFileSync(registry));
 for(const p of plan.essentialImages){const entry=working.entries.find(e=>e.path===p);if(!entry||sha(fs.readFileSync(p))!==entry.sha256)throw Error('Reviewed image mismatch: '+p);const existing=baseline.entries.find(e=>e.path===p);if(existing&&existing.sha256!==entry.sha256)throw Error('Unexpected existing image');if(!existing)baseline.entries.push(entry)}
 const registryBytes=Buffer.from(JSON.stringify(baseline,null,2)+'\n');
 for(const p of selected){const bytes=p===registry?registryBytes:fs.readFileSync(p);const blob=git(['hash-object','-w','--path='+p,'--stdin'],env,bytes).trim();git(['update-index','--add','--cacheinfo','100644,'+blob+','+p],env);snapshots.push({path:p,blob,sha256:sha(bytes),sharedPatchFromActualHead:p===registry})}
 for(const args of [['scripts/media-policy.cjs'],['scripts/build-rebuild-manifests.cjs',slug,'--check'],['scripts/review-video-duplicates.cjs',slug,'--candidate-file',prefix+'candidate-04-3.json','--check']]){
  const r=cp.spawnSync(process.execPath,args,{env,encoding:'utf8',windowsHide:true,maxBuffer:16e6});const rec={command:'node '+args.join(' '),exitCode:r.status,output:(r.stdout+r.stderr).trim()};checks.push(rec);if(r.status!==0)throw Error(rec.output)
 }
 git(['diff','--cached','--check',parent],env);
 const changed=git(['diff','--cached','--name-only','-z',parent],env).split('\0').filter(Boolean).sort();if(!changed.length||changed.some(p=>!selected.includes(p))||git(['diff','--cached','--diff-filter=D','--name-only',parent],env).trim())throw Error('Unexpected changed path/deletion');
 const newRasters=changed.filter(p=>/\.(png|jpe?g|webp|gif|bmp|tiff?)$/i.test(p));if(newRasters.length!==2||newRasters.some(p=>!plan.essentialImages.includes(p)))throw Error('Unexpected raster additions');
 for(const s of snapshots){if(git(['rev-parse',':'+s.path],env).trim()!==s.blob||(!s.sharedPatchFromActualHead&&sha(fs.readFileSync(s.path))!==s.sha256))throw Error('Selected content changed: '+s.path)}
 if(git(['rev-parse','HEAD']).trim()!==parent||sha(fs.readFileSync(externalIndex))!==indexBefore||sha(Buffer.from(git(['ls-files','--stage','-z'])))!==entriesBefore)throw Error('Concurrent HEAD/index change; preserve and inspect');
 const tree=git(['write-tree'],env).trim(),commit=git(['commit-tree',tree,'-p',parent],env,'Deliver reviewed rendering history04-3 private video and production evidence\n').trim();
 for(const s of snapshots)if(git(['rev-parse',commit+':'+s.path]).trim()!==s.blob)throw Error('Final blob mismatch');
 git(['update-ref','HEAD',commit,parent]);
 const push=cp.spawnSync('git',['push','origin','main'],{encoding:'utf8',windowsHide:true,maxBuffer:16e6});
 const local=git(['rev-parse','HEAD']).trim(),remote=git(['ls-remote','origin','refs/heads/main']).trim().split(/\s+/)[0],indexAfter=sha(fs.readFileSync(externalIndex)),entriesAfter=sha(Buffer.from(git(['ls-files','--stage','-z'])));
 const record={schemaVersion:1,verifiedAt:new Date().toISOString(),actualVideoId:receipt.actualVideoId,commit,parent,paths:changed,snapshots,checks,imagesAdded:newRasters,mediaAdded:0,normalPush:true,forcePush:false,pushExitCode:push.status,pushOutput:(push.stdout+push.stderr).trim(),localSha:local,remoteSha:remote,remoteMatches:local===remote,externalIndexBefore:indexBefore,externalIndexAfter:indexAfter,externalEntriesBefore:entriesBefore,externalEntriesAfter:entriesAfter,externalIndexByteIdentical:indexBefore===indexAfter,externalEntriesIdentical:entriesBefore===entriesAfter,sharedWorkingAndStagedRegistryUntouched:true,allCommittedBlobsVerified:true,humanListeningApproved:false,publicRightsApproved:false,remainingSeriesComplete:false,persistence:'Actual post-push verification. The external index is preserved byte-for-byte; its displayed staged diff changes with HEAD, but none of its entries were rewritten.'};
 fs.writeFileSync(prefix+'part3-selective-git-verification-v165.json',JSON.stringify(record,null,2)+'\n');
 if(push.status!==0||local!==remote||indexBefore!==indexAfter||entriesBefore!==entriesAfter)throw Error('Actual push/index verification failed; record preserved');
 console.log(JSON.stringify({commit,parent,paths:changed.length,imagesAdded:newRasters.length,mediaAdded:0,normalPush:true,localSha:local,remoteSha:remote,externalIndexByteIdentical:true},null,2));
}finally{if(fs.existsSync(idx))fs.unlinkSync(idx)}
