const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../..'),base=path.join(__dirname,'revision-balatro60-v2');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const save=(p,j)=>{const t=p+'.'+process.pid+'.writing';fs.writeFileSync(t,JSON.stringify(j,null,2)+'\n');fs.renameSync(t,p);};
const statePath=path.join(base,'longplay-window960-1440-execution.json'),s=read(statePath);
const proofPath=path.join(base,'longplay-third480-direct-review-v2.json');
if(fs.existsSync(proofPath))throw Error('Read existing proof; duplicate recording refused');
if(s.exitCode!==0||s.sampleExtractionExit!==0||sha(s.sourcePath)!==s.sourceSha256)throw Error('Exact completed source required');
let count=0;
const boards=s.boards.map(b=>{if(sha(b.path)!==b.sha256)throw Error('Board changed');return {...b,directlyRead:true,entries:b.entries.map(e=>{if(sha(e.path)!==e.sha256)throw Error('Sample changed');count++;return {...e,directlyRead:true};})};});
if(boards.length!==40||count!==240)throw Error('Coverage mismatch');
const now=new Date().toISOString();
const proof={schemaVersion:1,slug:s.slug,revision:s.revision,reviewedAt:now,sourcePath:s.sourcePath,sourceSha256:s.sourceSha256,executionSha256:sha(statePath),actualOuterSession:'46664',actualOuterExitObserved:0,boardCount:40,sampleCount:240,boards,reviewWindowSeconds:[960,1440],samplesAreNominalNotNativePts:true,observations:[
 '961–979s shop/Ancient Joker purchase and Blind menu excluded. 981–991s deal/selection forms Full House40×4 against target800. 993s Run Info table excluded.',
 '995–1009s Full House with two fives/three threes shows card reactions50×4,56×6,59×9,59×13, then round767. 767 remains below target800. Exact reaction order/native boundaries pending.',
 '1011–1095s redraw/selections/discards and long thinking; tables1043–1049s excluded. High Card selections around1017–1025s are discarded at1027s, not played. No long idle fills quota.',
 '1097–1113s Two Pair level2 base40×3, two Kings/two Queens plus selected six of clubs. Four pair cards score to80×3 then Joker80×7; six does not visibly score. Round767→1327 (hand560). 1111s intermediate count1065/279 is transient.',
 '1115–1165s cashout/shop/tooltips/Blind menu excluded. Credit Card sale is not score-effect evidence. 1167–1169s Big Blind deal shows target1200, round0.',
 '1171–1201s hover/selection/discard; no long waiting adopted. 1203–1223s Two Pair with enhanced Jacks/twos and selected six of spades shows60×3,64×7,64×11 and round704. Six is not visibly scored;704 remains below target1200.',
 '1227–1233s selects6/5/4/3/2 Straight30×4. 1235–1249s Run Info excluded. 1251–1265s actual Straight submission and reactions36×4,48×4,50×8, hand400; round704→1104, still below1200.',
 '1269–1283s Pair→Two Pair selection, with idle excluded. 1285–1295s Two Pair40×3 reactions50×3,65×3,70×4.50,70×8.50 then round1699 (prior1104 plus595); native order pending.',
 '1297–1363s cashout/shop/Voucher redemption and Joker purchase/hover/Blind selection excluded from actual quota. Splash tooltip says every played card counts but its effect is not inferred from shop. Ancient Joker tooltip lists diamond×1.5 at this point; no universal suit claim.',
 '1365–1397s The Window target1600, diamond debuffs visibly crossed out. Short selection changes Pair/Two Pair are separated from long hover. 1399–1409s submitted two tens/two sevens: diamond ten contributes no chips,50×3 then64×3 then64×7, round448. No completion/win claim. Exact native boundary/order pending.',
 '1411–1439s redraw/hover/High Card selections followed by1431s discard, not scoring. Debuffed tooltips and unrelated waiting excluded.'
],allListedCoarsePixelsDirectlyRead:true,allNativeFramesReviewed:false,wholeContinuousPlaybackApproved:false,nativeCutBoundariesApproved:false,footageAdopted:false,attributionExceptionUserAnswer:'pending',finalPublicRightsApproved:false,sourceAudioSelected:false,loop:false,slowdown:false,newImagesGitAdded:0,nextAction:'Exact native PTS/action boundary preflight and fixed-caption framing. Await description-credit exception before adoption/dependent narration/TTS.'};
save(proofPath,proof);
const cpPath=path.join(__dirname,'latest-checkpoint.json'),cp=read(cpPath);cp.recordedAt=now;cp.revisionLongplayThirdReview='projects/presenting-game-scores/production/revision-balatro60-v2/longplay-third480-direct-review-v2.json';cp.ownedJob={...cp.ownedJob,status:'source-window-reviewed-exit0',actualOuterExitObserved:0,workerExpectedRunning:false};cp.nextAction=proof.nextAction;save(cpPath,cp);
const qp=path.join(root,'production/batches/sakurai-planning-game-design/queue.json'),q=read(qp),item=q.items.find(x=>x.slug==='presenting-game-scores');item.ownedJob=cp.ownedJob;item.revisionLongplayThirdReview=cp.revisionLongplayThirdReview;item.nextAction=cp.nextAction;q.updatedAt=now;q.lastProgressAt=now;save(qp,q);
console.log(JSON.stringify({proof:proofPath,boards:40,samples:240,actualExitObserved:0,adoptedSeconds:0}));
