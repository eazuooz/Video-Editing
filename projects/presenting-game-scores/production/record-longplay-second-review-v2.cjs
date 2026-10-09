const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../..'),base=path.join(__dirname,'revision-balatro60-v2');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const save=(p,j)=>{const t=p+'.'+process.pid+'.writing';fs.writeFileSync(t,JSON.stringify(j,null,2)+'\n');fs.renameSync(t,p);};
const statePath=path.join(base,'longplay-second-window-execution.json'),s=read(statePath);
const proofPath=path.join(base,'longplay-second480-direct-review-v2.json');
if(fs.existsSync(proofPath))throw Error('Read existing review; duplicate recording refused');
if(s.exitCode!==0||s.sampleExtractionExit!==0||sha(s.sourcePath)!==s.sourceSha256)throw Error('Exact completed source required');
let count=0;
const boards=s.boards.map(b=>{if(sha(b.path)!==b.sha256)throw Error('Board changed');return {...b,directlyRead:true,entries:b.entries.map(e=>{if(sha(e.path)!==e.sha256)throw Error('Sample changed');count++;return {...e,directlyRead:true};})};});
if(boards.length!==40||count!==240)throw Error('Coverage mismatch');
const now=new Date().toISOString();
const proof={schemaVersion:1,slug:s.slug,revision:s.revision,reviewedAt:now,sourcePath:s.sourcePath,sourceSha256:s.sourceSha256,executionSha256:sha(statePath),actualOuterSession:'81571',actualOuterExitObserved:0,boardCount:40,sampleCount:240,boards,reviewWindowSeconds:[480,960],samplesAreNominalNotNativePts:true,observations:[
 '481–557s shop/tutorial/Blind/Joker/consumable instruction overlays excluded. Empress use around559–563s illustrates card modification, not an already-observed score result.',
 '565–603s selection/deselection changes High Card5×1/Pair10×2/Two Pair20×2 while round score remains0. Enhanced Jack tooltips show+10chips/+4Mult; hover/idle and605–623s Run Info tables excluded.',
 '625–653s includes idle/sorting and short label changes; no played-hand result inferred. 655s discard transition briefly displays−1, then2; do not narrate negative final remaining discards.',
 '661–681s forms Two Pair20×2 using enhanced Jacks and two twos, then successive card/Joker reactions produce44×14 and round616. Intermediate roundcount459/178 is transient. Exact native steps and bounds pending.',
 '683–689s cashout/reward excluded. 691–771s shop/rules/hover excluded. Uranus713–717s upgrades Two Pair base20×2→40×3; this shop transition is not actual gameplay quota. Judgement749–753s adds Credit Card; no scoring effect claimed.',
 '775–779s Blind menu excluded. 781–787s deal opens The Hook target600, round0. 793–809s selection changes Pair/High Card; 811–813s Run Info excluded. 817–897s mixes short selections/discards with long thinking/hover; four hearts plus a club do not prove a Flush. 899s View Deck table excluded.',
 '903–911s discard/redraw and selection create two Queens/two Jacks, Two Pair level2 base40×3, round0/target600. 913s Hands−1 is a transition only; 915s shows Hands3. 917/919/921s samples show50×3/70×7/80×11;923s hand880,925s round880. Same continuous hand, exact native reaction order pending.',
 '927–935s transition/cashout,937–959s shop/Voucher/Joker tooltips excluded. No tooltip or promotional screen is used to fill actual gameplay time.'
],allListedCoarsePixelsDirectlyRead:true,allNativeFramesReviewed:false,wholeContinuousPlaybackApproved:false,nativeCutBoundariesApproved:false,footageAdopted:false,attributionExceptionUserAnswer:'pending',finalPublicRightsApproved:false,sourceAudioSelected:false,loop:false,slowdown:false,newImagesGitAdded:0,nextAction:'Inspect later score-related actions, then exact native PTS/action boundaries and fixed-caption framing. Await description-credit exception before adoption or dependent narration/TTS.'};
save(proofPath,proof);
const cpPath=path.join(__dirname,'latest-checkpoint.json'),cp=read(cpPath);cp.recordedAt=now;cp.revisionLongplaySecondReview='projects/presenting-game-scores/production/revision-balatro60-v2/longplay-second480-direct-review-v2.json';cp.ownedJob={...cp.ownedJob,status:'source-window-reviewed-exit0',actualOuterExitObserved:0,workerExpectedRunning:false};cp.nextAction=proof.nextAction;save(cpPath,cp);
const qp=path.join(root,'production/batches/sakurai-planning-game-design/queue.json'),q=read(qp),item=q.items.find(x=>x.slug==='presenting-game-scores');item.ownedJob=cp.ownedJob;item.revisionLongplaySecondReview=cp.revisionLongplaySecondReview;item.nextAction=cp.nextAction;q.updatedAt=now;q.lastProgressAt=now;save(qp,q);
console.log(JSON.stringify({proof:proofPath,boards:40,samples:240,actualExitObserved:0,adoptedSeconds:0}));
