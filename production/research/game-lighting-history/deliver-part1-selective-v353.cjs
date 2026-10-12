// Guarded single private-video delivery from actual HEAD; isolated exact index.
const fs=require('node:fs'),cp=require('node:child_process'),crypto=require('node:crypto'),path=require('node:path');
const R='production/research/game-lighting-history/',Q='projects/game-lighting-history-04-1/',slug='game-lighting-history-04-1',registry='shared/git-essential-images.json';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function git(args,env=process.env,input){const r=cp.spawnSync('git',args,{env,input,encoding:Buffer.isBuffer(input)?undefined:'utf8',windowsHide:true,maxBuffer:128e6});if(r.status!==0)throw Error('git '+args.join(' ')+'\n'+r.stdout+r.stderr);return String(r.stdout)}
const evidenceOnly=process.argv.includes('--evidence-only');
const previous=evidenceOnly?JSON.parse(fs.readFileSync(R+'part1-selective-git-verification-v353.json')):null;
const plan=evidenceOnly?{paths:[R+'part1-selective-git-verification-v353.json',R+'part1-private-observations-v350.json',R+'record-part1-git-delivery-v354.py',R+'refresh-part1-scoped-rebuild-v354.cjs',Q+'project.json',Q+'publishing/youtube-upload.json',Q+'rebuild.json',Q+'README.md'],essentialImages:[]}:JSON.parse(fs.readFileSync(R+'part1-selective-paths-v352.json'));
const receipt=JSON.parse(fs.readFileSync(Q+'publishing/youtube-upload.json'));
if(!receipt.privateSaved||!receipt.fullSettingsVerified||!receipt.checksPassed||receipt.actualVideoId!=='YOsG939kaBw')throw Error('Actual verified same-ID private delivery required');
const selected=[...new Set([...plan.paths,R+'deliver-part1-selective-v353.cjs',...(evidenceOnly?[]:[R+'part1-selective-paths-v352.json',registry])])].sort();
if(git(['symbolic-ref','--short','HEAD']).trim()!=='main')throw Error('Unexpected branch');
const parent=git(['rev-parse','HEAD']).trim(),externalIndex=git(['rev-parse','--git-path','index']).trim(),indexBefore=sha(fs.readFileSync(externalIndex)),entriesBefore=sha(Buffer.from(git(['ls-files','--stage','-z'])));
const staged=git(['diff','--cached','--name-only','-z']).split('\0').filter(Boolean),overlap=staged.filter(p=>selected.includes(p)&&p!==registry);
if(evidenceOnly){if(!previous.remoteMatches||previous.commit!==parent||previous.externalIndexAfter!==indexBefore||previous.externalEntriesAfter!==entriesBefore)throw Error('Previous actual delivery/index changed; inspect before persistence');}
// Identical preserved index can show our newly committed files as deleted after
// HEAD advances. In evidence mode the byte/entry guards above resolve that case.
if(!evidenceOnly&&overlap.length)throw Error('Preserve staged selected paths: '+overlap.join(', '));
const idx=path.resolve('.git','lighting-part1-v353-'+Date.now()+'.index'),env={...process.env,GIT_INDEX_FILE:idx};
const snapshots=[],checks=[];
try{
 git(['read-tree',parent],env);
 const baseline=JSON.parse(git(['show',parent+':'+registry])),working=JSON.parse(fs.readFileSync(registry));
 for(const p of plan.essentialImages){const entry=working.entries.find(e=>e.path===p);if(!entry||sha(fs.readFileSync(p))!==entry.sha256)throw Error('Reviewed image mismatch '+p);const old=baseline.entries.find(e=>e.path===p);if(old&&old.sha256!==entry.sha256)throw Error('Existing image mismatch');if(!old)baseline.entries.push(entry);}
 const registryBytes=Buffer.from(JSON.stringify(baseline,null,2)+'\n');
 for(const p of selected){const bytes=p===registry?registryBytes:fs.readFileSync(p);const blob=git(['hash-object','-w','--path='+p,'--stdin'],env,bytes).trim();git(['update-index','--add','--cacheinfo','100644,'+blob+','+p],env);snapshots.push({path:p,blob,sha256:sha(bytes),sharedPatchFromActualHead:p===registry});}
 for(const args of [['scripts/media-policy.cjs'],['scripts/build-rebuild-manifests.cjs',slug,'--check'],['scripts/review-video-duplicates.cjs',slug,'--candidate-file',R+'candidate-04-1.json','--check']]){
  const r=cp.spawnSync(process.execPath,args,{env,encoding:'utf8',windowsHide:true,maxBuffer:16e6});const rec={command:'node '+args.join(' '),exitCode:r.status,output:(r.stdout+r.stderr).trim()};checks.push(rec);if(r.status!==0)throw Error(rec.output);
 }
 git(['diff','--cached','--check',parent],env);
 const changed=git(['diff','--cached','--name-only','-z',parent],env).split('\0').filter(Boolean).sort();
 if(!changed.length||changed.some(p=>!selected.includes(p))||git(['diff','--cached','--diff-filter=D','--name-only',parent],env).trim())throw Error('Unexpected changed path or deletion');
 const rasters=changed.filter(p=>/\.(png|jpe?g|webp|gif|bmp|tiff?)$/i.test(p));
 if(rasters.length!==(evidenceOnly?0:2)||rasters.some(p=>!plan.essentialImages.includes(p)))throw Error('Unexpected image additions');
 for(const s of snapshots)if(git(['rev-parse',':'+s.path],env).trim()!==s.blob||(!s.sharedPatchFromActualHead&&sha(fs.readFileSync(s.path))!==s.sha256))throw Error('Selected content changed '+s.path);
 if(git(['rev-parse','HEAD']).trim()!==parent||sha(fs.readFileSync(externalIndex))!==indexBefore||sha(Buffer.from(git(['ls-files','--stage','-z'])))!==entriesBefore)throw Error('Concurrent HEAD/index change; preserve and inspect');
 const tree=git(['write-tree'],env).trim(),commit=git(['commit-tree',tree,'-p',parent],env,evidenceOnly?'Record actual rendering04-1 private delivery normal-push verification\n':'Deliver reviewed rendering04-1 private video and current production evidence\n').trim();
 for(const s of snapshots)if(git(['rev-parse',commit+':'+s.path]).trim()!==s.blob)throw Error('Final committed blob mismatch');
 git(['update-ref','HEAD',commit,parent]);
 const push=cp.spawnSync('git',['push','origin','main'],{encoding:'utf8',windowsHide:true,maxBuffer:16e6});
 const local=git(['rev-parse','HEAD']).trim(),remote=git(['ls-remote','origin','refs/heads/main']).trim().split(/\s+/)[0],indexAfter=sha(fs.readFileSync(externalIndex)),entriesAfter=sha(Buffer.from(git(['ls-files','--stage','-z'])));
 const record={schemaVersion:1,verifiedAt:new Date().toISOString(),actualVideoId:receipt.actualVideoId,commit,parent,paths:changed,snapshots,checks,imagesAdded:rasters,mediaAdded:0,normalPush:true,forcePush:false,pushExitCode:push.status,pushOutput:(push.stdout+push.stderr).trim(),localSha:local,remoteSha:remote,remoteMatches:local===remote,externalIndexBefore:indexBefore,externalIndexAfter:indexAfter,externalEntriesBefore:entriesBefore,externalEntriesAfter:entriesAfter,externalIndexByteIdentical:indexBefore===indexAfter,externalEntriesIdentical:entriesBefore===entriesAfter,sharedWorkingAndStagedRegistryUntouched:true,allCommittedBlobsVerified:true,privateSettingsVerified:true,automaticAdChecksObserved:true,humanListeningApproved:false,publicRightsApproved:false,remainingSeriesComplete:false,persistence:'Actual post-push values, no future own SHA. External index bytes/entries unchanged; staged diff display can change with HEAD.'};
 fs.writeFileSync(R+(evidenceOnly?'part1-git-evidence-verification-v353.json':'part1-selective-git-verification-v353.json'),JSON.stringify(record,null,2)+'\n');
 if(push.status!==0||local!==remote||indexBefore!==indexAfter||entriesBefore!==entriesAfter)throw Error('Actual push/index verification failed; record preserved');
 console.log(JSON.stringify({commit,parent,paths:changed.length,imagesAdded:rasters.length,mediaAdded:0,normalPush:true,localSha:local,remoteSha:remote,externalIndexByteIdentical:true},null,2));
}finally{if(fs.existsSync(idx))fs.unlinkSync(idx);}
