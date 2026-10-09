const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../..'),base=path.join(__dirname,'revision-balatro60-v2');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const save=(p,j)=>{let t=p+'.'+process.pid+'.writing';fs.writeFileSync(t,JSON.stringify(j,null,2)+'\n');fs.renameSync(t,p);};
const state=read(path.join(base,'source-execution.json'));
if(state.exitCode!==0||state.active!==null)throw Error('Completed source worker required.');
const proofPath=path.join(base,'source-direct-review-v2.json');
if(fs.existsSync(proofPath))throw Error('Review already recorded; inspect before updating.');
const observations={
 launch:{decision:'candidate-subsets-only-native-boundaries-pending',notes:[
  'All 23 boards / 135 samples directly read. 0.25–10.25 swirl/menu promotion excluded.',
  '10.75–14.75 Three of a Kind level 1: 30×3 then three Kings add chips 40→50→60, a Joker adds +10 Mult. Native cut boundary not inferred from coarse timestamps.',
  '17.75–20.25 montage shows +10/X1.5 and a separate Pair 2720×73728→147456→294912. Do not describe separate shots as a single hand.',
  '20.75–23.75 Ouija conversion, 26.75–29.25 Death converts K/2 to two Kings. Card effects can support a matching claim, not unrelated quota.',
  '31.75–32.25 Straight Flush level upgrade and 33.75–35.75 hand versus accumulated round score candidate. At 34.25+ target 28000, round 2996, Flush 74×22=1628, aggregate reaches 4624.',
  '40.75–50.25 enhanced-card reactions and seal retrigger are distinct montage events; no common total or optimum inferred. 52.75–54.75 Joker chip/Mult reactions are a separate montage.',
  'Rules/collection/shop/voucher stills, Game Over 36.25–39.25, static Jokers 50.75–52.25 and final promotion 55.25–67.25 excluded.'
 ]},
 'friends-pack3':{decision:'rejected-entire-source',balatroActionSeconds:0,notes:[
  'All 36 boards / 215 samples directly read. Live-action Jimbo and collaboration cards interleave partner-game footage.',
  'Partner action is Divinity Original Sin 2, Shovel Knight, Potion Craft, Enter the Gungeon, Cult of the Lamb, Dont Starve, 1000xRESIST and Warframe. These are not Balatro card submission/score calculation.',
  '98.25–107.25 OUT TODAY end card excluded. A Balatro title or publisher provenance does not make this Balatro actual-footage time.'
 ]},
 'friends-pack4':{decision:'rejected-entire-source',balatroActionSeconds:0,notes:[
  'All 29 boards / 174 samples directly read. ESRB/Jimbo/Xbox promotion and collaboration cards interleave partner-game footage.',
  'Partner content is Critical Role, Bugsnax, Civilization, Rust, Assassins Creed, Slay the Princess, Dead by Daylight and Fallout; no Balatro card submission/score calculation was observed.',
  '79.75–86.75 collaboration end card excluded. End-card Venice Rooftops / Assassins Creed II / Jesper Kyd music credit retained internally; no source audio selected.'
 ]}
};
let boardCount=0,sampleCount=0;
const sources=state.results.map(s=>{
 if(sha(s.sourcePath)!==s.sha256)throw Error('Source SHA changed: '+s.key);
 const boards=s.boards.map(b=>{
  if(sha(b.path)!==b.sha256)throw Error('Board SHA changed');boardCount++;
  const entries=b.entries.map(e=>{if(sha(e.path)!==e.sha256)throw Error('Sample SHA changed');sampleCount++;return {...e,directlyRead:true};});
  return {...b,directlyRead:true,entries};
 });
 return {...s,boards,allCoarseSamplePixelsDirectlyReviewed:true,observations:observations[s.key],adoptedSeconds:0};
});
if(boardCount!==88||sampleCount!==524)throw Error('Unexpected reviewed coverage');
const now=new Date().toISOString();
const proof={schemaVersion:1,slug:'presenting-game-scores',revision:'balatro60-tetris40-v2',reviewedAt:now,sourceExecutionSha256:sha(path.join(base,'source-execution.json')),boardCount,sampleCount,sources,allListedBoardsAndSamplesDirectlyRead:true,nativePtsBoundariesApproved:false,wholeContinuousPlaybackApproved:false,allNativeFramesApproved:false,footageAdopted:false,finalPublicRightsApproved:false,sourceAudioSelected:false,loop:false,slowdown:false,newImagesGitAdded:0,nextAction:'Acquire and inspect a longer reuse-permitted Balatro recording, then verify exact native action intervals and fixed-caption framing.'};
save(proofPath,proof);
const cpPath=path.join(__dirname,'latest-checkpoint.json'),cp=read(cpPath);
cp.recordedAt=now;cp.revisionSourceDirectReview='projects/presenting-game-scores/production/revision-balatro60-v2/source-direct-review-v2.json';
cp.ownedJob={...cp.ownedJob,status:'source-job-completed-exit0',exitCode:0,workerExpectedRunning:false,finishedAt:state.finishedAt,processIdentityMustBeCheckedBeforeReuse:true};cp.nextAction=proof.nextAction;save(cpPath,cp);
const qp=path.join(root,'production/batches/sakurai-planning-game-design/queue.json'),q=read(qp),item=q.items.find(x=>x.slug==='presenting-game-scores');
item.ownedJob=cp.ownedJob;item.revisionSourceDirectReview=cp.revisionSourceDirectReview;item.nextAction=cp.nextAction;q.updatedAt=now;q.lastProgressAt=now;save(qp,q);
console.log(JSON.stringify({boardCount,sampleCount,sourceJobExit:state.exitCode,adoptedSeconds:0,newGitImages:0,proof:proofPath}));
