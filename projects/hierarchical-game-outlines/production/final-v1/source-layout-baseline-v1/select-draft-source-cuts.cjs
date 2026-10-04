// Exclusive current-voice draft. This writes no encoded media or approval gate.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v1');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const plan=read(path.join(work,'plan.json')),bank=read(path.join(root,'projects/hierarchical-game-outlines/sources/source-action-bank.json'));
const selectionFile=path.join(work,'cut-selection.json');
const revision2=process.argv.includes('--reviewed-v2');
if(revision2){
 const review=read(path.join(work,'source-layout-review-v1/direct-review.json'));
 const digest=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
 if(review.status!=='rejected-source-layout-v1'||review.selectionSha256!==digest(selectionFile)||review.layoutSha256!==digest(path.join(work,'caption-layout-qa.json')))throw Error('Preserved current rejected-layout evidence is required.');
 const baseline=path.join(work,'source-layout-baseline-v1');
 if(fs.existsSync(baseline))throw Error('Source revision2 was already started; inspect it.');
 fs.mkdirSync(baseline);
 for(const name of ['plan.json','cut-selection.json','caption-layout-qa.json','captions.ko.srt','captions.en.srt','captions.ko.ass'])fs.copyFileSync(path.join(work,name),path.join(baseline,name));
 fs.copyFileSync(__filename,path.join(baseline,'select-draft-source-cuts.cjs'));
}else if(fs.existsSync(selectionFile))throw Error('Review existing selection; never silently overwrite it.');
const F=x=>Math.round(x*60),cuts=[],ranges=[];
const prohibited=[[3277.75,3280],[4628.5,4632],[4640.75,4642.85],[4656.5,4662],[4683.9,4686.8],[4704.8,4708.8],[4715,4717.5],[3187.75,3192.1]];
function allocate(s,from,to,specs,focus,paragraphs){
 let cursor=F(from),stop=to===null?s.frames:F(to);
 for(const [start,end]of specs){
  if(cursor>=stop)break;
  const sf=F(start),frames=Math.min(stop-cursor,F(end)-sf),ef=sf+frames;
  if(frames<=0)throw Error('Empty source allocation');
  if(ranges.some(([a,b])=>sf<b&&ef>a))throw Error('Source interval reused');
  if(prohibited.some(([a,b])=>sf<F(b)&&ef>F(a)))throw Error(`Excluded catalog/menu/unrelated camera ${start}–${ef/60}`);
  ranges.push([sf,ef]);
  const c={id:String(cuts.length+1).padStart(3,'0'),scene:s.id,sourceId:'I-ccSZ5J1Bo',file:bank.source.localMediaPath,sourceIn:sf/60,sourceOut:ef/60,sourceInFrame:sf,sourceOutFrame:ef,reviewedSourceEnd:end,frames,seconds:frames/60,localStartFrame:cursor,localEndFrame:cursor+frames,timelineStart:s.start+cursor/60,timelineEnd:s.start+(cursor+frames)/60,crop:[0,0,1376,774],sourceLabel:'Two Point Museum · Two Point Studios 공식 시연 / 추가 콘텐츠 미리보기 (2026)',visibleAction:focus,viewerFocus:focus,paragraphs,classification:'actual-existing-game-action',speed:1,loop:false,captionCenter:[960,970],continuity:'Independent excerpts; our document analogy is not an internal developer document or a game dependency system.',sourceAudio:'excluded; approved continuous Nimbus',nativeBoundaryAndCaptionReview:'pending'};
  const chapter=read(path.join(root,'projects/hierarchical-game-outlines/planning/action-map.json')).chapters.find(ch=>ch.id===s.id);
  c.claim=chapter.claim;c.diagramConnection=chapter.diagramConnection;c.insertionPoint=chapter.insertionPoint;
  const controls=sf<F(3300)&&ef>F(2600)||sf>=F(4670);
  c.composition=revision2&&controls?{mode:'same-game-background-with-complete-borderless-source',foreground:[187,0,1546,870],background:'same native source frame fills1920x1080 with blur18; no generated scene or white frame',reason:'Keep all selected support/price/item UI above the fixed caption top897; source UI, colors, speed and face-free crop are retained.'}:{mode:'full-screen-face-free-game-crop'};
  cuts.push(c);s.cuts.push(c);cursor+=frames;
 }
 if(cursor!==stop)throw Error(`Scene${s.id} lacks${(stop-cursor)/60}s; inspect fresh action.`);
}
for(const s of plan.scenes.filter(s=>s.classification==='actual')){
 s.cuts=[];
 if(s.id==='01'){
  allocate(s,0,9.24,[[4601,4606.5],[4651,4654.75]],'Circular ride placement, then a separate close camera inspection of its entrance. Preview/visitors do not establish a newly successful ride.',[1]);
  allocate(s,9.24,18.22,[[2181,2189.98]],'Ride placement preview moves among surrounding attractions.',[2]);
  allocate(s,18.22,25.953333,[[2194,2201.75]],'Independent placement preview/camera perspective under the2026 demonstration/preview disclaimer.',[3]);
  allocate(s,25.953333,null,[[2189.983333,2193],[2635,2640],[4612,4616.25]],'Placement, selected curve and separate circular ride viewpoint illustrate different sizes of design questions.',[4]);
 }else if(s.id==='03'){
  allocate(s,0,4.44,[[2616,2620.44]],'Selected track endpoint preview changes.',[1]);
  allocate(s,4.44,18.92,[[2654,2668.48]],'Separate curved track preview extends toward nearby attractions; compare the whole ride with one segment.',[1,2]);
  allocate(s,18.92,28.583333,[[2692,2701.666667]],'Camera approaches and rotates around selected endpoint/support controls.',[3]);
  allocate(s,28.583333,37.06,[[2668.483333,2676.966667]],'Curve and support positions change at normal speed under the concrete-adjustment sentence.',[4]);
  allocate(s,37.06,null,[[2676.966667,2687.583333]],'Further curve/support adjustment; invalid/collision tooltip is not a successful connection or comfort outcome.',[5]);
 }else if(s.id==='05'){
  allocate(s,0,8.8,[[2715.1,2723.9]],'Selected track controls and the station remain visible as camera distance changes.',[1]);
  allocate(s,8.8,26.75,[[2726,2743.95]],'Successive curve adjustments change the selected segment and surrounding camera view.',[2,3]);
  allocate(s,26.75,36.016667,[[2746,2755.266667]],'The loop and nearby tracks remain visible under the explicit document-folding analogy.',[4]);
  allocate(s,36.016667,47.24,[[3161.033333,3172.266667]],'Camera scales between overall loop/station and nearby lake-side curve; detail still exists.',[5]);
  allocate(s,47.24,null,[[2755.266667,2765.966667]],'Separate close loop/support viewpoint continues during the explicit overview/detail document comparison.',[6]);
 }else if(s.id==='07'){
  allocate(s,0,8.78,[[2769,2777.78]],'Loop support selected; neighboring track and station remain visible.',[1]);
  allocate(s,8.78,18.666667,[[2779,2787.95],[2789,2789.95]],'Red-preview tilt and ground-relative geometry change; separate endpoint view follows during the notes/conditions clause.',[2]);
  allocate(s,18.666667,27.066667,[[2789.95,2798.35]],'Camera/selected endpoints show the relationship between separate track pieces.',[3]);
  allocate(s,27.066667,43.4,[[2806,2822.333333]],'Camera turns around the neighboring loop and selected segment; child-note movement is our document analogy.',[4,5]);
  allocate(s,43.4,53.616667,[[3142,3152.216667]],'Separate support adjustment changes nearby curve shape.',[6]);
  allocate(s,53.616667,null,[[3152.216667,3159],[2798.35,2804]],'Further support/track viewpoint under explicit caveat that game rules do not automatically follow a document branch move.',[7]);
 }else if(s.id==='09'){
  allocate(s,0,10.516667,[[3001,3011.516667]],'New curve preview changes beside previously placed track.',[1]);
  allocate(s,10.516667,20.916667,[[3014,3024.4]],'Selected curve length/shape changes with neighboring track retained.',[2]);
  allocate(s,20.916667,29.333333,[[3045,3053.416667]],'Red preview and support move beside neighboring loop; color is not proof of solved connections.',[3]);
  allocate(s,29.333333,revision2?39.95:39.966667,[[3069.1,3079.733333]],'Collision lists, subsequent support manipulation and changing confirmation remain distinct observations; no all-conditions completion claim.',[4]);
  allocate(s,revision2?39.95:39.966667,48.7,revision2?[[4626.4,4628.4],[4632,4633.2],[4643,4644.733333],[4622,4625.816667]]:[[4622,4628.25],[4643,4645.483333]],'Independent entrance camera inspection starts with the gate visible; subsequent wider ride views illustrate the broader goal. HireStaff and unrelated green-coaster view excluded.',[5]);
  allocate(s,48.7,58.083333,[[4670,4679.383333]],'Gold-flower placement preview moves around the ride; no visitor-satisfaction conclusion.',[6]);
  allocate(s,58.083333,null,[[4687,4694.2],[4717.5,4723.7]],'Separate lamp and balloon positioning/camera actions near decoration and entrance illustrate a generic cross-reference question; they are not narrated as the gold flower.',[7]);
 }else if(s.id==='11'){
  allocate(s,0,9.34,[[3174,3183.34]],'Camera returns along the curved track to its station.',[1]);
  allocate(s,9.34,19.25,revision2?[[3207.5,3217.416667]]:[[3192.35,3202.266667]],'Camera returns to the red track, edit controls open and a support is selected; neighboring track remains visible.',[2]);
  allocate(s,19.25,27.65,revision2?[[3233.25,3237.9],[3217.416667,3221.166667]]:[[3210,3218.4]],'Selected support/curve shapes change in a separate excerpt, then the wider neighboring track remains visible. Independent excerpts are not a continuous playthrough.',[3]);
  allocate(s,27.65,36.9,[[3224,3233.25]],'Selected segment goes through multiple shapes at normal speed.',[4]);
  allocate(s,36.9,45.533333,[[3238,3246.633333]],'Collision list/confirmation changes alongside actual support editing; one changed mark is not every condition verified.',[5]);
  allocate(s,45.533333,56.516667,[[3260,3270.983333]],'Other support/curve adjustment and broader inspection; explicitly separate excerpts.',[6]);
  allocate(s,56.516667,null,revision2?[[3272,3277.55],[3221.166667,3224],[3246.633333,3248.583333]]:[[3272,3277.55],[3218.4,3223.2]],'Camera returns to the wider track and independent support/curve editing under the overall-goal/detail-check comparison; track catalog excluded.',[7]);
 }
 if(s.cuts.reduce((n,c)=>n+c.frames,0)!==s.frames)throw Error('Coverage mismatch');
}
if(cuts.reduce((n,c)=>n+c.frames,0)!==plan.actualFrames)throw Error('Draft frame target mismatch');
plan.cuts=cuts;plan.sourceRangeAudit={noRepeatedInterval:true,exclusiveFrameIntervals:ranges.sort((a,b)=>a[0]-b[0]),prohibited};
plan.finalSourceTimingApproved=false;plan.actualFootageMeasuredAndApproved=false;plan.captionReviewComplete=false;
const out={status:'current-voice-exclusive-draft-awaiting-native-action-and-all-caption-review',sourceLayoutRevision:revision2?'v2':'v1',supersedes:revision2?'source-layout-baseline-v1/cut-selection.json':null,sourceSha256:bank.source.fileSha256,existingGamesOnly:true,normalSpeed:true,sourceAudioExcluded:true,allCutsApproved:false,body60_40Passed:false,cuts};
fs.writeFileSync(selectionFile,JSON.stringify(out,null,2)+'\n');
fs.writeFileSync(path.join(work,'plan.json'),JSON.stringify(plan,null,2)+'\n');
console.log(JSON.stringify({draftCuts:cuts.length,proposedActualFrames:plan.actualFrames,proposedActualSeconds:plan.gameplaySeconds,selectionSha256:crypto.createHash('sha256').update(fs.readFileSync(selectionFile)).digest('hex'),finalApproved:false}));
