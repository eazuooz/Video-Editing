const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../..'),base=path.join(__dirname,'revision-balatro60-v2');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const save=(p,j)=>{const t=p+'.'+process.pid+'.writing';fs.writeFileSync(t,JSON.stringify(j,null,2)+'\n');fs.renameSync(t,p);};
const statePath=path.join(base,'longplay-source-execution.json'),s=read(statePath);
const proofPath=path.join(base,'longplay-first480-direct-review-v2.json');
if(fs.existsSync(proofPath))throw Error('Existing review must be read; duplicate recording refused');
if(s.exitCode!==0||s.wholeDecodeExit!==0||s.sampleExtractionExit!==0||sha(s.sourcePath)!==s.sha256)throw Error('Completed exact source required');
let count=0;
const boards=s.boards.map(b=>{if(sha(b.path)!==b.sha256)throw Error('Board changed');return {...b,directlyRead:true,entries:b.entries.map(e=>{if(sha(e.path)!==e.sha256)throw Error('Sample changed');count++;return {...e,directlyRead:true};})};});
if(boards.length!==40||count!==240)throw Error('Coverage mismatch');
const now=new Date().toISOString();
const p={schemaVersion:1,slug:s.slug,revision:s.revision,reviewedAt:now,sourcePath:s.sourcePath,sourceSha256:s.sha256,executionSha256:sha(statePath),actualOuterSession:'48983',actualOuterExitObserved:0,workerNoLongerAliveObserved:true,wholeDecodeExit:0,sampleExtractionExit:0,boardCount:40,sampleCount:240,boards,reviewWindowSeconds:[0,480],samplesAreNominalNotNativePts:true,observations:[
  '0–49s startup/menu/settings; 51–239s tutorial/rules/hover overlays excluded. Visible Game Speed setting is 1; native action speed still needs verification.',
  '241–245s first Pair level1 begins at 10×2; two nines add chips to28×2; round score changes0→56. Native bounds pending.',
  '247–269s tutorial overlays and discard instructions excluded. 271–287s actual selections change Pair/Two Pair labels without round-score change. 289–299s Run Info table excluded.',
  '301–321s actual selection/deselection changes Two Pair20×2/Pair10×2/High Card5×1; no submitted result inferred. Later idle/hover and 337–343s Run Info excluded.',
  '345–363s selects three sevens and a six; Three of a Kind starts30×3, scoring sevens add7 each to51×3. The selected six does not visibly score; round56→209. No claim that all selected cards contribute.',
  '377–385s selection changes Pair/Two Pair/High Card. 393–411s three Kings/two Jacks form Full House40×4; scoring steps50/70/90×4 then hand360 and round209→569. This supports transient calculation versus accumulated round score.',
  '413–421s cashout/reward, 423–479s shop/tutorial/Joker/Empress/Voucher hover excluded from actual gameplay quota. Joker effects are not proved by purchase tooltip.'
],allListedCoarsePixelsDirectlyRead:true,allNativeFramesReviewed:false,wholeContinuousPlaybackApproved:false,nativeCutBoundariesApproved:false,footageAdopted:false,attributionExceptionUserAnswer:'pending',finalPublicRightsApproved:false,sourceAudioSelected:false,loop:false,slowdown:false,newImagesGitAdded:0,nextAction:'Inspect further normal-speed card selection/calculation after tutorial; verify exact native PTS, action boundaries and fixed-caption framing. Await description-credit exception before adoption.'};
save(proofPath,p);
const cpPath=path.join(__dirname,'latest-checkpoint.json'),cp=read(cpPath);
cp.recordedAt=now;cp.revisionLongplayCoarseReview='projects/presenting-game-scores/production/revision-balatro60-v2/longplay-first480-direct-review-v2.json';
cp.ownedJob={...cp.ownedJob,status:'longplay-source-completed-exit0',exitCode:0,workerExpectedRunning:false,finishedAt:s.finishedAt,actualOuterExitObserved:0};cp.nextAction=p.nextAction;save(cpPath,cp);
const qp=path.join(root,'production/batches/sakurai-planning-game-design/queue.json'),q=read(qp),item=q.items.find(x=>x.slug==='presenting-game-scores');
item.ownedJob=cp.ownedJob;item.revisionLongplayCoarseReview=cp.revisionLongplayCoarseReview;item.nextAction=cp.nextAction;q.updatedAt=now;q.lastProgressAt=now;save(qp,q);
console.log(JSON.stringify({proof:proofPath,boards:40,samples:240,actualExitObserved:0,adoptedSeconds:0}));
