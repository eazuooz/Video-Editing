// One reviewed video plus integrated rules. Isolated index, no media, normal push.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../../..'),slug='hierarchical-game-outlines';
const N='projects/'+slug+'/production/reference-preserving-v1',P=N+'/publishing';
const gitBin='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe';
const normal={...process.env,PATH:path.dirname(gitBin)+path.delimiter+process.env.PATH};
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const hash=f=>sha(fs.readFileSync(path.join(root,f)));
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8').replace(/^\uFEFF/,''));
const save=(f,v)=>fs.writeFileSync(path.join(root,f),JSON.stringify(v,null,2)+'\n');
function run(exe,args,env=normal,input){const r=cp.spawnSync(exe,args,{cwd:root,env,input,encoding:'utf8',windowsHide:true,maxBuffer:256e6});if(r.status!==0)throw Error(args.join(' ')+'\n'+r.stdout+'\n'+r.stderr);return r.stdout.trimEnd();}
const git=(args,env=normal,input)=>run(gitBin,args,env,input);
const settings=read(P+'/private-settings-direct-review-v1.json');
if(settings.videoId!=='JoHXz7YtEPw'||!settings.privateSavedAndReopened||!settings.fullAvailableSettingsVerified||settings.scheduled)throw Error('Reviewed PRIVATE delivery required');
const transition=read(P+'/main-private-transition-v1.json'),original=read(N+'/main-promotion-v1.json');
if(hash(transition.current.path)!==transition.current.sha256||hash(original.baseline.path)!==original.baseline.sha256)throw Error('Main transition or original backup changed');
const selectionPath=P+'/production-git-selection-v1.json',preflightPath=P+'/git-preflight-rebuild-v1.json',proofPath=P+'/production-git-verification-v1.json';
const external=path.resolve(root,git(['rev-parse','--git-path','index']));
function ordinaryFiles(){
 const docs=['CAPTION_STYLE','MEDIA_STORAGE','MEMBERSHIP_OUTRO','NARRATION_AUDIO_STANDARD','VIDEO_25D_THUMBNAIL_REVIEW','VIDEO_ADDITIVE_REVISION','VIDEO_EXAMPLE_TRANSFER_REVIEW','VIDEO_GAME_FOOTAGE_POLICY','VIDEO_SCREEN_LAYOUT','VIDEO_VISUAL_STYLE','VIDEO_WORKFLOW','YOUTUBE_PUBLISHING'].map(s=>'docs/'+s+'.md');
 const configs=['video-production-control','youtube-defaults','explanation-style-policy','game-example-coverage-policy','illustrative-subject-detail-policy'].map(s=>'shared/publishing/'+s+'.json');
 const templates=['README.md','checklist.md','project.json','audio/mix-report.md','planning/outline.md','planning/edit-cues.csv','planning/production-plan.json','production/review-ledger.json','publishing/youtube.ko.md','publishing/youtube.en.md','sources/SOURCES.md'].map(s=>'templates/video-project/'+s);
 const own=['project.json','rebuild.json','planning/production-plan.json','production/review-ledger.json','production/delivery-output.json','production/manual-preflight-v1/music-rights.json'].map(s=>'projects/'+slug+'/'+s);
 const code=['reference-reel-plan-v1.json','reference-explanations-v1.tsx'].map(s=>'motion-canvas/src/projects/'+slug+'/'+s);
 const names=['README.md','annotations.py','build-current-v1.py','captions.py','captions.ko.srt','captions.en.srt','collect-current-v1.cjs','collection-verification-v1.json','caption-alignment-review-v1.json','caption-boundary-diagnosis-v1.json','diagnose-boundaries-v1.py','duplicate-delta-direct-review-v2.json','final-direct-review-v1-held.json','final-direct-review-v2.json','final-pixel-plan-v1.json','final-pixel-plan-v2.json','final-repair-execution-v2.json','final-timeline-v1.json','finalize-mix-v2.py','finalize-source-script.py','independent-menu-source-review.json','independent-source-acquisition-v1.json','acquisition-bkH5znXN2WQ-v1.json','latest-checkpoint.json','main-promotion-v1.json','mix-asr-v1.json','mix-contexts-v1.json','mix-direct-review-v1.json','mix-execution-v1.json','mix-execution-v2.json','mix-final-inputs-v1.json','mix-finalization-v2.json','move-context-source-review.json','move-continuation-direct-review-v1.json','narration.en.json','narration.ko.json','pair-execution-v1.json','preflight-direct-review-v2.json','preflight-execution-v1.json','prepare-final-timeline-v1.py','prepare-independent-review.py','prepare_script.py','prepare_source_review.py','promote-current-v1.py','qa-execution-v1.json','render-reference.cjs','render-voice-v1.py','repair-final-v2.py','review-audio-v1.py','review-independent-source.py','review-mix-contexts-v1.py','review-voice-contexts-v1.py','seal-final-review-v2.py','seal-private-delivery-v1.py','seal-record-failure-v1.json','seal-voice-and-preflight-v1.py','source-review.json','visuals-execution-v1.json','voice-asr-session-v1.json','voice-asr-v1.json','voice-closure-v1.json','voice-contexts-v1.json','voice-direct-review-v1.json','voice-execution-v1.json','voice-manifest.json','voice-resource-v1.json','voice-session-v1.json','white-cpu-execution-v6.json','white-preflight-before-timing-v1.json','white-preflight-direct-review.json','white-session-v6.json','word-primary-reference.json','deliver-selected-v1.cjs'].map(s=>N+'/'+s);
 const pub=['title.ko.txt','title.en.txt','description.ko.txt','description.en.txt','pinned-comment.ko.txt','youtube-upload-v1.json','private-settings-direct-review-v1.json','main-private-transition-v1.json','git-preflight-rebuild-v1.json'].map(s=>P+'/'+s);
 const archive='docs/history/video-policy-before-20261013-consolidation',manifest=read(archive+'/manifest.json');
 for(const row of manifest.files)if(hash(row.archive)!==row.sha256)throw Error('Historical policy backup changed: '+row.archive);
 return [...new Set(['AGENTS.md',...docs,...configs,...templates,...own,...code,...names,...pub,archive+'/README.md',archive+'/manifest.json',...manifest.files.map(r=>r.archive)])].sort();
}
if(process.argv.includes('--prepare')){
 if(fs.existsSync(path.join(root,preflightPath)))throw Error('Preparation already exists; do not repeat rebuild.');
 const indexBytes=fs.readFileSync(external),indexEntries=git(['ls-files','--stage','-z']);
 const shared=path.join(root,'projects/rebuild-index.json'),sharedBytes=fs.readFileSync(shared);
 const foreign=fs.readdirSync(path.join(root,'projects')).filter(s=>s!==slug).map(s=>'projects/'+s+'/rebuild.json').filter(f=>fs.existsSync(path.join(root,f))).map(f=>({path:f,sha256:hash(f)}));
 const oldWrite=fs.writeFileSync;let sharedNoop=false;
 fs.writeFileSync=function(p,data,...args){if(typeof p!=='number'&&path.resolve(String(p)).toLowerCase()===shared.toLowerCase()){
  const norm=b=>b.toString('utf8').replace(/^\uFEFF/,'').replace(/\r\n/g,'\n');
  if(!fs.readFileSync(shared).equals(sharedBytes)||norm(Buffer.from(data))!==norm(sharedBytes))throw Error('Shared index write would change foreign inventory');sharedNoop=true;return;
 }return oldWrite.call(fs,p,data,...args);};
 try{require(path.join(root,'scripts/build-rebuild-manifests.cjs')).generate(slug);}finally{fs.writeFileSync=oldWrite;}
 if(!sharedBytes.equals(fs.readFileSync(shared))||!indexBytes.equals(fs.readFileSync(external))||indexEntries!==git(['ls-files','--stage','-z'])||foreign.some(f=>hash(f.path)!==f.sha256))throw Error('Preservation failure; inspect without restoring');
 save(preflightPath,{at:new Date().toISOString(),ownSlug:slug,sharedIndexWriteNoop:sharedNoop,sharedIndexSha256:sha(sharedBytes),foreignRebuilds:foreign,foreignRebuildsUnchanged:true,externalIndexBytesAndEntriesUnchanged:true,mediaJobsRepeated:0});
 const selected=ordinaryFiles();for(const f of selected)if(!fs.existsSync(path.join(root,f)))throw Error('Missing explicit path '+f);
 save(selectionPath,{at:new Date().toISOString(),parent:git(['rev-parse','HEAD']),selectedFiles:selected.map(f=>({path:f,workingSha256:hash(f)})),purpose:'Integrated rules and this selected independent-footage video only; raw sources, QA media and foreign queues excluded',newMedia:0,newRaster:0});
 console.log(JSON.stringify({prepared:true,selected:selected.length,foreignRebuilds:foreign.length,externalIndexPreserved:true}));process.exit(0);
}
if(!process.argv.includes('--deliver'))throw Error('Use --prepare then --deliver');
if(fs.existsSync(path.join(root,proofPath)))throw Error('Delivery outcome exists; inspect it instead of repeating');
const plan=read(selectionPath),parent=git(['rev-parse','HEAD']),branch=git(['symbolic-ref','--short','HEAD']);
if(parent!==plan.parent)throw Error('HEAD advanced; refresh only selection after reviewing current parent');
const files=plan.selectedFiles.map(f=>f.path).concat(selectionPath);
for(const f of plan.selectedFiles)if(hash(f.path)!==f.workingSha256)throw Error('Selected input changed: '+f.path);
if(files.some(f=>/\.(mp4|webm|mov|wav|m4a|mp3|ogg|flac|zip|png|jpe?g|webp|gif|bin)$/i.test(f)))throw Error('Media/raster selected');
const extBytes=fs.readFileSync(external),extEntries=git(['ls-files','--stage','-z']);
const preflight=read(preflightPath),sharedSha=hash('projects/rebuild-index.json');
const snapshot=new Map(files.map(f=>[f,hash(f)]));
const temp=fs.mkdtempSync(path.join(root,'.git','hierarchy-single-private-')),env={...normal,GIT_INDEX_FILE:path.join(temp,'index')};
fs.writeFileSync(path.join(temp,'external-index-before.bin'),extBytes);fs.writeFileSync(path.join(temp,'external-index-before.entries'),extEntries);
function preserved(){
 if(!fs.readFileSync(external).equals(extBytes)||git(['ls-files','--stage','-z'])!==extEntries)throw Error('Foreign index changed; do not restore blindly');
 for(const [f,h] of snapshot)if(hash(f)!==h)throw Error('Working file changed: '+f);
 if(hash('projects/rebuild-index.json')!==sharedSha||preflight.foreignRebuilds.some(f=>hash(f.path)!==f.sha256))throw Error('Shared inventory/foreign rebuild changed');
}
git(['read-tree',parent],env);
for(let i=0;i<files.length;i+=40)git(['add','--',...files.slice(i,i+40)],env);
const expected=new Map(),hashes=git(['hash-object','--stdin-paths'],env,files.join('\n')+'\n').split(/\r?\n/);files.forEach((f,i)=>expected.set(f,hashes[i]));
const rows=git(['diff','--cached','--name-status','-z',parent],env).split('\0').filter(Boolean),changes=[];
for(let i=0;i<rows.length;i+=2)changes.push({status:rows[i],path:rows[i+1]});
if(changes.some(r=>!files.includes(r.path)||!['A','M'].includes(r.status)))throw Error('Foreign path/deletion in selection');
const staged=new Map(git(['ls-files','--stage','-z'],env).split('\0').filter(Boolean).map(l=>{const[m,f]=l.split('\t');return[f,m.split(' ')[1]];}));
for(const [f,h] of expected)if(staged.get(f)!==h)throw Error('Wrong staged blob '+f);
let checks;
try{checks={whitespace:git(['diff','--cached','--check',parent],env),media:run(process.execPath,['scripts/media-policy.cjs'],env),rebuild:run(process.execPath,['scripts/build-rebuild-manifests.cjs',slug,'--check'],env)};
 for(const f of files.filter(f=>f.endsWith('.json')))read(f);
}catch(e){save(P+'/git-precommit-failure-v1.json',{at:new Date().toISOString(),error:e.message,commitCreated:false,pushed:false,isolatedIndex:env.GIT_INDEX_FILE});throw e;}
preserved();if(git(['rev-parse','HEAD'])!==parent)throw Error('HEAD advanced before commit');
const tree=git(['write-tree'],env),commit=git(['commit-tree',tree,'-p',parent],env,'Complete hierarchical outlines private video and consolidate one-video production rules\n');
const proof={at:new Date().toISOString(),videoId:'JoHXz7YtEPw',parent,branch,commit,changedPaths:changes,selectedPaths:files,checks,allStagedBlobsVerified:true,mediaAdded:0,newImagesAdded:0,externalIndexSha256Before:sha(extBytes),externalIndexUnchanged:true,sharedWorkingFilesUnchanged:true,foreignRebuildsPreserved:preflight.foreignRebuilds.length,pushed:false};
preserved();git(['update-ref','HEAD',commit,parent]);save(proofPath,proof);
try{git(['push','origin',commit+':refs/heads/'+branch]);}catch(e){proof.pushFailure=e.message;save(proofPath,proof);throw e;}
const remote=git(['ls-remote','origin','refs/heads/'+branch]).split(/\s/)[0];
if(git(['rev-parse','HEAD'])!==commit||remote!==commit)throw Error('Concurrent advance; inspect actual saved commit');
const finalBlobs=new Map(git(['ls-tree','-r','-z',remote]).split('\0').filter(Boolean).map(l=>{const[m,f]=l.split('\t');return[f,m.split(' ')[2]];}));
for(const [f,h] of expected)if(finalBlobs.get(f)!==h)throw Error('Wrong final blob '+f);
preserved();Object.assign(proof,{pushed:true,localCommit:commit,remoteCommit:remote,exactLocalRemoteMatch:true,verifiedBlobCount:expected.size,allFinalRemoteBlobsVerified:true,externalIndexSha256After:sha(fs.readFileSync(external)),verifiedAt:new Date().toISOString()});save(proofPath,proof);
console.log(JSON.stringify({commit,remote,verifiedBlobs:expected.size,media:0,newImages:0,externalIndexPreserved:true,pushed:true}));
