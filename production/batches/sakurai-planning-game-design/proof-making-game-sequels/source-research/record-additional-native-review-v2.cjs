const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = process.cwd();
const base = 'production/batches/sakurai-planning-game-design/proof-making-game-sequels/source-research';
const read = p => JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const save = (p,v) => fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');
const native = read(base+'/native-additive-v2.json');
if (!native.endedAt || native.status !== 'native-samples-extracted-awaiting-direct-review' || native.sources.some(x=>!x.endedAt)) throw Error('Native extraction did not finish');
const source = native.sources[0];
const old = read(base+'/source-action-bank-v1.json');
const asset = old.assets.find(x=>x.assetId==='MXxOg1xuWcI');
const now = new Date().toISOString();
const folder = 'production/batches/sakurai-planning-game-design/proof-making-game-sequels/research-local/native-additive-v2/MXxOg1xuWcI/';
const boards = [...Array.from({length:16},(_,i)=>`action-sheet-${String(i+1).padStart(2,'0')}.jpg`),...Array.from({length:3},(_,i)=>`boundary-sheet-${String(i+1).padStart(2,'0')}.jpg`)].map(name=>({path:folder+name,sha256:sha(folder+name),directlyRead:true,localOnly:true}));
const reviewed = {
  schemaVersion:1,slug:'making-game-sequels',reviewedAt:now,
  method:'Direct visual reading of all16 action and3 native-boundary boards, retaining source-native timestamps. Planning selection only; final framing, caption pixels and all chosen clip edges remain separate gates.',
  input:{path:base+'/native-additive-v2.json',sha256:sha(base+'/native-additive-v2.json')},
  source:{...asset}, actionFrames:source.actionSamples.length,boundaryFrames:36,boundaryTriplets:12,boards,
  observations:[
    {boards:['01','02','03','04'],seconds:[990,1021.5],action:'Low wooden beams and floor devices remain visible while approaching orcs are aimed at with purple projectiles. The player changes viewpoint and enemies come closer; red/white/purple effects alone do not establish damage values.'},
    {boards:['05','06','07','08'],seconds:[1022,1053.5],action:'Further aimed combat, nearby groups and reorientation in the cave. The exact native triplets at1028.733333/1042.4 show lightning combat effects with background continuity, not edited scene cuts. Placement preview begins around1053 in the half-second samples.'},
    {boards:['09'],seconds:[1054,1058.5],action:'Floor Scorcher preview changes orientation, a blocked symbol appears, then an installed device and flame are visible. The new-rift countdown/transition beginning by1057.5 is excluded. This is not a Barricade preview.'},
    {boards:['09','10','11'],seconds:[1093,1107],action:'Separate later fight beside the stone arch and devices: aim, white/purple projectiles and distant enemies. The brief turn around1102 is not a novel mechanic or quota by itself.'},
    {boards:['11','12','13'],seconds:[1118,1133],action:'Direct purple combat with Gnoll Grenadier text, with a brief upward camera/Minecart label around1121.5. Do not claim player cart control. Quiet distant holding around1127–1130 and the countdown at1133 are excluded.'},
    {boards:['13','14'],seconds:[1153,1163],action:'Most of1153–1160 is looking/waiting across the device floor. Later brief firing alone is insufficient to justify this whole window; keep the entire candidate window out of the new bank.'},
    {boards:['14','15','16'],seconds:[1168,1188],action:'Green-projectile effects and aimed combat change to a nearby orc at1174–1176, followed by reorientation and distant fire. Short empty traversals at1173–1174 and1181–1183.5 are excluded. End1187.966/1188 triplet turns to the nearby spike floor and shows no edit.'}
  ],
  historicalCorrection:{path:base+'/additive-source-discovery-selection-v2.json',priorCoarseLabel:'Barricade near1055',currentDirectNativeLabel:'Floor Scorcher',priorRecordPreserved:true,reason:'Direct native boards show the angled metal flame device and Floor Scorcher selection, whereas the coarse5-second view was mislabelled.'},
  excludedWindows:[[1057,1059],[1121,1122],[1127,1130],[1132.5,1133],[1153,1163],[1172.5,1174],[1176.5,1177],[1181,1183.5],[1187.5,1188]],
  inferenceLimits:['No developer internal code reuse, budget, intention, first appearance, balance or winning strategy is proved by these gameplay shots.','These are later distinct intervals in OMD2, not proof of a sequel adding a new cave, weapon or trap.','Different omitted gaps are not uninterrupted action; each final narration/shot connection must be separately aligned.','Do not infer damage or weapon names from effect colour, nor treat score text as evidence of a designer intent.'],
  approvedIntervals:[],approvedActualSeconds:0,finalEdgesApproved:false,finalCaptionPixelsReviewed:false,bodyRatioApproved:false,newGitImages:0,sourceAudioUsed:false
};
save(base+'/direct-additional-native-review-v2.json',reviewed);
const intervals = [
  [990,1006,'Aim across the visible floor devices and fire at approaching groups beneath low beams.'],
  [1006,1021,'Nearby enemy approach and direct attacks alongside the placed floor devices.'],
  [1030,1046,'Fight a close group, reorient and continue aiming; lightning effects are continuous combat.'],
  [1046,1053,'Continue direct purple-projectile combat before the placement preview.'],
  [1053,1057,'Change Floor Scorcher preview orientation and observe installation/flame before the rift countdown.'],
  [1093,1102,'Fire beside the arch/device route and move the aiming direction as enemies approach.'],
  [1103,1107,'Resume aimed firing across the floor-device route in a later source interval.'],
  [1118,1121,'Aim directly at the incoming enemy before the upward Minecart camera glance.'],
  [1122,1127,'Continue direct purple attacks beside the devices, excluding later holding/waiting.'],
  [1130,1132.5,'Close purple attack effect and Gnoll Grenadier encounter before the countdown.'],
  [1168,1172.5,'Green effects around the route and direct aiming at incoming enemies.'],
  [1174,1176.5,'Turn toward and fire at the nearby orc, then turn back.'],
  [1177,1181,'Aim and fire again across the device floor after the nearby encounter.'],
  [1183.5,1187.5,'Distant aimed purple fire from the new viewpoint, excluding the preceding empty traversal.']
];
const additions = intervals.map(([start,end,action],i)=>({
  id:old.candidates.length+i+1,assetId:asset.assetId,videoId:asset.videoId,game:'Orcs Must Die! 2',source:asset.source,sourceSha256:asset.sourceSha256,nativeFrameRate:asset.nativeFrameRate,
  localFrames:{startInclusive:Math.round(start*30),endExclusive:Math.round(end*30)},localSeconds:[start,end],originalSeconds:[start,end],durationSeconds:end-start,
  visibleAction:action,claim:'Preparing devices and direct combat remain observable activities while the player changes where to aim or stand. These source actions illustrate retained activities and changed conditions in our concept-writing exercise.',
  viewerFocus:'Follow the player, incoming group and device position; observe changed aiming distance and orientation without inferring code reuse or a universal strategy.',
  diagramConnection:'Retain prepare/fight → state the concrete space/tool/next-preparation change. The diagram is our writing aid, not a developer pitch.',
  insertion:'Additional independent example after06 and before07 retained/change exercise; final per-word assignment and exact native edges pending.',
  directPlanningReview:base+'/direct-additional-native-review-v2.json',sourceAudioUsed:false,loop:false,slowdown:false,presenterCropRequired:false,finalCaptionPixelsReviewed:false,finalIntervalApproved:false
}));
for (const a of additions) for (const b of [...old.candidates,...additions.filter(x=>x.id<a.id)]) {
  if(a.assetId===b.assetId&&Math.max(a.localFrames.startInclusive,b.localFrames.startInclusive)<Math.min(a.localFrames.endExclusive,b.localFrames.endExclusive)) throw Error('Duplicate native interval '+a.id+'/'+b.id);
}
const bank = {...old,createdAt:now,status:'expanded-direct-native-planning-bank-final-framing-and-cues-pending',historicalBank:{path:base+'/source-action-bank-v1.json',sha256:sha(base+'/source-action-bank-v1.json'),candidateCount:old.candidates.length,candidateSeconds:275.2},candidates:[...old.candidates,...additions],newNarrationCreated:true,newProjectCreated:true,nextAction:'Align exact words/frames and inspect fixed captions, then measure independent added narration without shortening original explanations.'};
bank.candidateActualSeconds=bank.candidates.reduce((s,x)=>s+x.durationSeconds,0);
bank.candidateCount=bank.candidates.length;
bank.candidateSeconds=bank.candidateActualSeconds;
bank.crossSourceReview += ' The14 later OMD2 intervals are nonoverlapping with the original20 OMD2 intervals and with each other. Same-game repeated combat is not evidence of new sequel features; final useful selection and action/narration alignment remain pending.';
bank.newCandidates={count:additions.length,seconds:additions.reduce((s,x)=>s+x.durationSeconds,0),review:base+'/direct-additional-native-review-v2.json',sourceAudioStreams:0,finalApprovedSeconds:0};
save(base+'/source-action-bank-v2.json',bank);
console.log(JSON.stringify({boards:boards.length,actionFrames:reviewed.actionFrames,newCandidates:additions.length,newSeconds:bank.newCandidates.seconds,totalSeconds:bank.candidateActualSeconds,originalBankUnchanged:sha(base+'/source-action-bank-v1.json')===bank.historicalBank.sha256,finalApproved:false,newGitImages:0}));
