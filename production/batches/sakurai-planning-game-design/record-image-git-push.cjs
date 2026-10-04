// Record the actual ordinary push and verify that removed images remain local.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base='production/batches/sakurai-planning-game-design';
const git=args=>cp.execFileSync('git',args,{cwd:root,encoding:'utf8',maxBuffer:128e6,windowsHide:true}).trimEnd();
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const commit='49cefb9b8ba17c58924785cb273190c5ed4dbcd8';
const local=git(['rev-parse','HEAD']),remote=git(['ls-remote','origin','refs/heads/main']).split(/\s/)[0];
if(local!==remote)throw Error('Actual local/remote SHA differs.');
git(['merge-base','--is-ancestor',commit,remote]);
const auditPath=base+'/image-git-cleanup-20261005.json',audit=JSON.parse(fs.readFileSync(path.join(root,auditPath),'utf8'));
const tracked=new Set(git(['ls-tree','-r','--name-only','-z',commit]).split('\0').filter(Boolean));
for(const r of audit.candidates){if(tracked.has(r.path)||!fs.existsSync(path.join(root,r.path))||sha(fs.readFileSync(path.join(root,r.path)))!==r.localSha256)throw Error('Image removal/local preservation verification failed: '+r.path);}
const visible=git(['ls-files','--others','--exclude-standard','-z']).split('\0').filter(f=>/\.(png|jpe?g|webp|gif|bmp|tiff?)$/i.test(f));
if(visible.length)throw Error('Unexpected visible new raster images: '+visible.join('\n'));
const proof={schemaVersion:1,verifiedAt:new Date().toISOString(),productionPolicyCommit:commit,localSha:local,remoteSha:remote,remoteMatches:true,normalPush:true,forcePush:false,
  pushExitCode:0,pushOutput:'To https://github.com/eazuooz/Video-Editing.git\n   50957939..49cefb9b  main -> main',
  commands:['git push origin main','git rev-parse HEAD','git ls-remote origin refs/heads/main'],
  removedRasterCount:audit.candidateCount,removedRasterBytes:audit.candidateBytes,newRasterAdded:0,localImagesPreserved:true,allRemovedImageLocalHashesMatch:true,
  trackedRasterAfter:[...tracked].filter(f=>/\.(png|jpe?g|webp|gif|bmp|tiff?)$/i.test(f)).length,visibleUntrackedRasterAfter:0,
  historyRewritten:false,scope:'Ten completed batch production/QA image paths only; original assets, thumbnails and Studio/rights proofs preserved. Other tasks were excluded from the isolated index.',
  checkEvidence:base+'/image-policy-pre-delivery-checks.json',audit:auditPath,
  automation24:{status:'ACTIVE',updatedViaNativeTool:true,updatedAt:new Date(1791130087189).toISOString(),updatedAtEvidence:'Read-only automation.toml updated_at after native automation_update success.',currentPolicy:'Per-video selective normal push, essential-image gate, completed thumbnails and native source-action review. No thumbnail blocking.'},
  evidencePersistence:'This records an already observed push. Its containing evidence commit has its own later SHA; no self-SHA is guessed.'};
fs.writeFileSync(path.join(root,base+'/image-policy-git-verification.json'),JSON.stringify(proof,null,2)+'\n');
audit.delivery={commit,pushed:true,remoteVerifiedAt:proof.verifiedAt,remoteSha:remote,allRemovedImagesRemainLocal:true,newRasterAdded:0};
fs.writeFileSync(path.join(root,auditPath),JSON.stringify(audit,null,2)+'\n');
const queuePath=base+'/queue.json',queue=JSON.parse(fs.readFileSync(path.join(root,queuePath),'utf8'));
queue.imageGitPolicy={approvedAt:'2026-10-05',authority:'영상하나 제작끝나면 푸쉬좀 해줘 엄청쌓였어... jpg나 이미지파일은 필요한것만 나두고 추가 안하기로 했었어 확인해줘',newRasterDefault:'local-only; reviewed essential files only',registry:'shared/git-essential-images.json',newImageGate:'node scripts/media-policy.cjs',cleanup:auditPath,gitVerification:base+'/image-policy-git-verification.json',removedCount:350,localFilesPreserved:true,newRasterAdded:0,perVideoSelectivePush:true,isolatedIndexRequired:true};
queue.progressGitVerification=proof;
queue.automation.checkpointPromptUpdatedAt=proof.automation24.updatedAt;queue.automation.checkpointPromptVerified='Native automation24 update confirmed ACTIVE/hourly. Ten complete private platform settings; both thumbnail followups saved/reopened. Per-video selective normal Git delivery and essential-image policy required. Next avoid-game-comparisons native action/cut-boundary review; five official sources and 435 discovery frames directly reviewed, no approved intervals or narration yet.';
queue.updatedAt=proof.verifiedAt;
fs.writeFileSync(path.join(root,queuePath),JSON.stringify(queue,null,2)+'\n');
const checkpointPath=base+'/proof-avoid-game-comparisons/latest-checkpoint.json',checkpoint=JSON.parse(fs.readFileSync(path.join(root,checkpointPath),'utf8'));
checkpoint.imageGitPolicy=queue.imageGitPolicy;checkpoint.progressGitVerification=proof;checkpoint.updatedAt=proof.verifiedAt;
fs.writeFileSync(path.join(root,checkpointPath),JSON.stringify(checkpoint,null,2)+'\n');
console.log(JSON.stringify({commit,local,remote,removed:350,newRaster:0,localImagesPreserved:true,visibleUntrackedRaster:0}));
