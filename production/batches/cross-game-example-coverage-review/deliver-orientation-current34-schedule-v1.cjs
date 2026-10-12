// Deliver the observed schedule/checks metadata once, with an isolated index.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),slug='game-math-orientation-matrices';
const B='production/batches/cross-game-example-coverage-review';
const O='projects/'+slug+'/revision-teaching-clarity-v1',P=O+'/publishing';
const bin='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe';
const normal={...process.env,PATH:path.dirname(bin)+path.delimiter+process.env.PATH};
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const file=f=>path.join(root,f),read=f=>JSON.parse(fs.readFileSync(file(f),'utf8').replace(/^\uFEFF/,''));
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const save=(f,v)=>{const p=file(f),t=p+'.schedule-delivery-'+process.pid+'.tmp';fs.writeFileSync(t,JSON.stringify(v,null,2)+'\n',{flag:'wx'});fs.renameSync(t,p);};
function run(exe,args,env=normal,input){const r=cp.spawnSync(exe,args,{cwd:root,env,input,encoding:'utf8',windowsHide:true,maxBuffer:256e6});if(r.status!==0)throw Error(args.join(' ')+'\n'+r.stdout+'\n'+r.stderr);return r.stdout.trimEnd();}
const git=(a,e=normal,i)=>run(bin,a,e,i);
const files=[
  B+'/record-orientation-checks-followup-v2.py',B+'/seal-orientation-current34-checks-complete-v3.py',
  B+'/seal-orientation-current34-schedule-v1.py',B+'/deliver-orientation-current34-schedule-v1.cjs',B+'/queue.json',
  O+'/current34-main-schedule-update-v1.json',O+'/main-before-current34-schedule-update-v1.json',O+'/latest-checkpoint.json',
  P+'/automatic-ad-followup-v2.json',P+'/automatic-ad-followup-v3.json',P+'/private-settings-direct-review-v2.json',
  P+'/production-git-verification-v1.json',P+'/obsolete-deletion-action-time-confirmation-v1.json',
  P+'/schedule-direct-review-v1.json',P+'/schedule-ledger-update-v1.json',P+'/schedule-seal-prewrite-failure-v1.json',
  P+'/youtube-upload-v1.json','projects/'+slug+'/project.json','projects/'+slug+'/rebuild.json',
  'shared/publishing/daily-alternating-schedule.json'
].sort();
for(const f of files)if(!fs.existsSync(file(f)))throw Error('Missing explicit path '+f);
if(process.argv.includes('--plan')){console.log(JSON.stringify(files.map(f=>({path:f,bytes:fs.statSync(file(f)).size})),null,2));process.exit(0);}
if(!process.argv.includes('--deliver'))throw Error('Use --plan or --deliver');
const proofPath=P+'/schedule-git-verification-v1.json';
if(fs.existsSync(file(proofPath)))throw Error('Existing follow-up delivery; inspect, do not duplicate');
const settings=read(P+'/private-settings-direct-review-v2.json'),schedule=read(P+'/schedule-direct-review-v1.json');
if(!settings.fullSettingsComplete||!settings.automaticAdCheckPassed||settings.actualVideoId!=='orq0TMVkFts')throw Error('Actual completed private settings/checks required');
if(!schedule.savedAndReopened||!schedule.futureScheduledListVerified||!schedule.previous26OtherScheduledTitlesAndDatesUnchanged)throw Error('Actual schedule proof required');
const promotion=read(O+'/current34-main-promotion-v1.json'),transition=read(O+'/current34-main-schedule-update-v1.json');
for(const r of [...promotion.otherProtectedInputs,...promotion.repairCandidates,promotion.baselineMain])if(sha(fs.readFileSync(file(r.path)))!==r.sha256)throw Error('Protected bytes changed '+r.path);
if(sha(fs.readFileSync(file('projects/'+slug+'/project.json')))!==transition.afterSha256)throw Error('Intentional current main transition differs');
const parent=git(['rev-parse','HEAD']),branch=git(['symbolic-ref','--short','HEAD']);
const external=path.resolve(root,git(['rev-parse','--git-path','index']));
const bytes=fs.readFileSync(external),entries=git(['ls-files','--stage','-z']);
const temp=fs.mkdtempSync(path.join(root,'.git','orientation-current34-schedule-'));
const env={...normal,GIT_INDEX_FILE:path.join(temp,'index')};
fs.writeFileSync(path.join(temp,'external-index-before.bin'),bytes);
fs.writeFileSync(path.join(temp,'external-index-before.entries'),entries);
const sharedFiles=['AGENTS.md','docs/VIDEO_WORKFLOW.md','docs/VIDEO_VISUAL_STYLE.md','projects/rebuild-index.json',
  'shared/publishing/daily-alternating-schedule.json',B+'/queue.json'];
const sharedBefore=Object.fromEntries(sharedFiles.map(f=>[f,sha(fs.readFileSync(file(f)))]));
const foreignRebuild=fs.readdirSync(file('projects')).filter(s=>s!==slug&&fs.existsSync(file('projects/'+s+'/rebuild.json')))
  .map(s=>({path:'projects/'+s+'/rebuild.json',sha256:sha(fs.readFileSync(file('projects/'+s+'/rebuild.json')))}));
function unchanged(){
  if(sha(fs.readFileSync(external))!==sha(bytes)||git(['ls-files','--stage','-z'])!==entries)throw Error('External index changed; preserve it');
  for(const[f,h]of Object.entries(sharedBefore))if(sha(fs.readFileSync(file(f)))!==h)throw Error('Shared working file changed '+f);
  for(const r of foreignRebuild)if(sha(fs.readFileSync(file(r.path)))!==r.sha256)throw Error('Foreign rebuild changed '+r.path);
}
git(['read-tree',parent],env);

// Locate JSON values without reformatting any foreign HEAD text.
function spans(text){
  let i=0;const out=new Map(),ws=()=>{while(/\s/.test(text[i]||'')&&i<text.length)i++;};
  function str(){const start=i++;while(i<text.length){if(text[i]==='\\'){i+=2;continue;}if(text[i++]==='"')return JSON.parse(text.slice(start,i));}throw Error('Unclosed JSON string');}
  function val(p){ws();const start=i,c=text[i];
    if(c==='{'){i++;ws();if(text[i]!=='}')while(true){const key=str();ws();if(text[i++]!==':')throw Error('JSON colon');val([...p,key]);ws();if(text[i]!==',')break;i++;ws();}if(text[i++]!=='}')throw Error('JSON object');}
    else if(c==='['){i++;ws();let n=0;if(text[i]!==']')while(true){val([...p,n++]);ws();if(text[i]!==',')break;i++;ws();}if(text[i++]!==']')throw Error('JSON array');}
    else if(c==='"')str();else{while(i<text.length&&!/[\s,}\]]/.test(text[i]))i++;}
    out.set(JSON.stringify(p),{start,end:i});
  }val([]);return out;
}
function ownedJson(head,changes,append){
  const locations=spans(head),edits=[];
  for(const[p,v]of changes){const s=locations.get(JSON.stringify(p));if(!s)throw Error('Missing shared HEAD field '+JSON.stringify(p));
    const lead=head.slice(head.lastIndexOf('\n',s.start)+1,s.start).match(/^ */)[0];
    edits.push({...s,text:JSON.stringify(v,null,2).replaceAll('\n','\n'+lead)});
  }
  if(append){const[p,v]=append,s=locations.get(JSON.stringify(p)),values=JSON.parse(head.slice(s.start,s.end));
    const lead=head.slice(head.lastIndexOf('\n',s.start)+1,s.start).match(/^ */)[0]+'  ';
    const value=JSON.stringify(v,null,2).replaceAll('\n','\n'+lead);
    if(values.length){const last=locations.get(JSON.stringify([...p,values.length-1]));edits.push({start:last.end,end:last.end,text:',\n'+lead+value});}
    else edits.push({start:s.start+1,end:s.start+1,text:'\n'+lead+value+'\n'+lead.slice(2)});
  }
  let result=head;for(const e of edits.sort((a,b)=>b.start-a.start))result=result.slice(0,e.start)+e.text+result.slice(e.end);
  JSON.parse(result);return result;
}
const stagedSubsets=new Map();
{
  const f='shared/publishing/daily-alternating-schedule.json',head=git(['show',parent+':'+f])+'\n',h=JSON.parse(head),w=read(f);
  const n=h.actualSchedules.findIndex(e=>e.slug===slug),current=w.actualSchedules.find(e=>e.slug===slug);
  if(n<0||h.actualSchedules[n].videoId!=='6-kP65hrZcI'||current.videoId!=='orq0TMVkFts')throw Error('Fresh ledger transition differs');
  const addition=w.replacementHistory.find(e=>e.newSchedule?.videoId==='orq0TMVkFts'&&e.oldSchedule?.videoId==='6-kP65hrZcI');
  if(!addition||h.replacementHistory.some(e=>e.newSchedule?.videoId==='orq0TMVkFts'))throw Error('Missing/duplicate own ledger history');
  const s=ownedJson(head,[[['updatedAt'],w.updatedAt],[['actualSchedules',n],current]],[['replacementHistory'],addition]);
  const expected=structuredClone(h);expected.updatedAt=w.updatedAt;expected.actualSchedules[n]=current;expected.replacementHistory.push(addition);
  if(!same(JSON.parse(s),expected))throw Error('Foreign ledger field altered in staged subset');stagedSubsets.set(f,s);
}
{
  const f=B+'/queue.json',head=git(['show',parent+':'+f])+'\n',h=JSON.parse(head),w=read(f);
  const n=h.futureScheduledPriority.findIndex(e=>e.slug===slug),current=w.futureScheduledPriority.find(e=>e.slug===slug);
  if(n<0||current.videoId!=='orq0TMVkFts')throw Error('Own queue transition differs');
  const keys=['updatedAt','status','next','currentOrientationReview'];
  const changes=keys.map(k=>[[k],w[k]]);changes.push([['futureScheduledPriority',n],current]);
  const s=ownedJson(head,changes),expected=structuredClone(h);for(const k of keys)expected[k]=w[k];expected.futureScheduledPriority[n]=current;
  if(!same(JSON.parse(s),expected))throw Error('Foreign queue field altered in staged subset');stagedSubsets.set(f,s);
}
function walk(dir){return fs.readdirSync(file(dir),{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name)).flatMap(e=>{if(e.isSymbolicLink()||/^(node_modules|\.git|\.venv|delivery-history|delivery-stage-.*|media.*|chunks)$/.test(e.name))return[];const f=dir+'/'+e.name;return e.isDirectory()?walk(f):[f];});}
const slugs=fs.readdirSync(file('projects')).filter(s=>fs.existsSync(file('projects/'+s+'/project.json'))).sort();
const inventory=[...new Set([...git(['ls-files','--cached','--others','--exclude-standard','-z'],env).split('\0').filter(Boolean),...slugs.flatMap(s=>walk('projects/'+s)),...slugs.flatMap(s=>fs.existsSync(file('motion-canvas/src/projects/'+s))?walk('motion-canvas/src/projects/'+s):[])])].filter(f=>fs.existsSync(file(f))).sort();
save('projects/'+slug+'/rebuild.json',require(file('scripts/build-rebuild-manifests.cjs')).build(slug,inventory));
git(['add','--',...files.filter(f=>!stagedSubsets.has(f))],env);
for(const[f,text]of stagedSubsets){const blob=git(['hash-object','-w','--stdin'],env,text);git(['update-index','--add','--cacheinfo','100644',blob,f],env);}
const raw=git(['diff','--cached','--name-status','-z',parent],env).split('\0').filter(Boolean),changes=[];
for(let i=0;i<raw.length;i+=2)changes.push({status:raw[i],path:raw[i+1]});
if(changes.some(e=>!files.includes(e.path)||!['A','M'].includes(e.status)))throw Error('Foreign path or deletion selected');
if(files.some(f=>/\.(mp4|webm|wav|mp3|m4a|ogg|flac|zip|png|jpe?g|gif|webp|ax\.txt)$/i.test(f)))throw Error('Media/image/raw UI selected');
const staged=new Map(git(['ls-files','--stage','-z'],env).split('\0').filter(Boolean).map(l=>{const[m,f]=l.split('\t');return[f,m.split(' ')[1]];}));
const blobs=[];
for(const f of files){const expected=stagedSubsets.has(f)?git(['hash-object','--stdin'],env,stagedSubsets.get(f)):git(['hash-object','--',f],env);
  if(staged.get(f)!==expected)throw Error('Staged byte mismatch '+f);blobs.push({path:f,blob:expected,source:stagedSubsets.has(f)?'owned-HEAD-subset':'exact-current-file'});
}
const checks={whitespace:git(['diff','--cached','--check',parent],env),media:run(process.execPath,['scripts/media-policy.cjs'],env),
  currentOrientationRebuild:run(process.execPath,['scripts/build-rebuild-manifests.cjs',slug,'--check'],env)};
unchanged();if(git(['rev-parse','HEAD'])!==parent)throw Error('HEAD advanced before commit; preserve prepared result');
const tree=git(['write-tree'],env),commit=git(['commit-tree',tree,'-p',parent],env,'Verify orientation lecture replacement at 09:00 Seoul\n');
const proof={schemaVersion:1,recordedAt:new Date().toISOString(),actualVideoId:'orq0TMVkFts',parent,branch,commit,
  productionGitCommit:schedule.productionGitCommit,followupOnly:true,selectedPaths:files,changedPaths:changes,blobs,checks,
  mediaAdded:0,newImagesAdded:0,rawUiAdded:0,allStagedBlobsVerified:true,sharedHeadSubsetsOnly:true,
  foreignLedgerAndQueueFieldsPreservedInStagedBlobs:true,externalIndexSha256Before:sha(bytes),externalIndexUnchanged:true,
  sharedWorkingSha256Before:sharedBefore,foreignRebuildCount:foreignRebuild.length,foreignRebuildUnchanged:true,
  sharedRebuildIndexUnchanged:true,allOther78ProtectedInputsUnchanged:true,repairCandidateUnchanged:true,pushed:false};
unchanged();git(['update-ref','HEAD',commit,parent]);save(proofPath,proof);
try{git(['push','origin',commit+':refs/heads/'+branch]);}catch(e){proof.pushFailure=e.message;save(proofPath,proof);throw e;}
const local=git(['rev-parse','HEAD']),remote=git(['ls-remote','origin','refs/heads/'+branch]).split(/\s/)[0];
if(local!==commit||remote!==commit)throw Error('Concurrent local/remote advance; inspect saved actual commit');
const final=new Map(git(['ls-tree','-r','-z',remote]).split('\0').filter(Boolean).map(l=>{const[m,f]=l.split('\t');return[f,m.split(' ')[2]];}));
for(const f of files)if(final.get(f)!==staged.get(f))throw Error('Final blob differs '+f);
unchanged();Object.assign(proof,{pushed:true,localCommit:local,remoteCommit:remote,exactLocalRemoteMatch:true,
  allFinalRemoteBlobsVerified:true,verifiedBlobCount:files.length,externalIndexSha256After:sha(fs.readFileSync(external)),
  sharedWorkingSha256After:Object.fromEntries(sharedFiles.map(f=>[f,sha(fs.readFileSync(file(f)))])),verifiedAt:new Date().toISOString()});
save(proofPath,proof);
console.log(JSON.stringify({commit,remote,verifiedBlobs:files.length,newImages:0,media:0,externalIndexUnchanged:true,
  sharedWorkingFilesUnchanged:true,foreignRebuildCount:foreignRebuild.length,foreignRebuildUnchanged:true,pushed:true}));
