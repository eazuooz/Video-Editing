// Directly read eight native source boards. No continuous/final approval.
const fs=require('node:fs'),crypto=require('node:crypto');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const write=(p,j)=>{if(fs.existsSync(p))throw Error('Preserve prior record: '+p);fs.writeFileSync(p,JSON.stringify(j,null,2)+'\n');};
const execution='production/research/game-lighting-history/local/hogwarts-official-site-v79/execution.json',e=read(execution);
if(e.status!=='candidate-source-and-samples-ready'||e.source.boards.length!==8||e.source.sha256!=='f7129a728b7833ca6205d63550f77c5cc6975bd0e77b93426103565c52563aed'||sha(e.source.media)!==e.source.sha256||e.source.wholeDownloadedWindowDecodeExit!==0)throw Error('Source changed');
for(const b of e.source.boards)if(sha(b.path)!==b.sha256)throw Error('Board changed');
const out='projects/game-lighting-history-04/production/hogwarts-official-source-direct-review-v80.json';
write(out,{reviewedAt:new Date().toISOString(),execution:{path:execution,sha256:sha(execution)},source:e.source.media,sourceSha256:e.source.sha256,primary:e.primary,sourceId:e.source.id,publisher:'Harry Potter verified',uploadDate:'20221111',allEightBoardsDirectlyRead:true,boards:e.source.boards.map(b=>({...b,directlyViewed:true,localOnly:true})),sourceAudio:false,wholeDownloadedWindowDecodeExit:0,firstDecodedPts:0,timeBase:'1/15360',containerNbFrames:5401,containerDuration:177.033984,decodedFullFrameCountVerified:false,sourceStartOffsetVerified:false,
 observations:[
  {nativeSeconds:[0,18],action:'Player in a yellow robe climbs a staircase under bright windows, approaches a door and emerges into a stone courtyard. Minimap lower-left, spells/health lower-right. Camera and player change position; not an OFF/ON comparison.'},
  {nativeSeconds:[18,43],action:'Through the courtyard arch, camera tilts towards towers and follows the player down exterior stairs. Warm cloth, stone and sky are visible together.'},
  {nativeSeconds:[43,65],action:'Player approaches the terrace balustrade; camera looks down towards the landscape, then turns back along the terrace. Observe changing view/occlusion rather than attributing all changes to one lighting feature.'},
  {nativeSeconds:[65,84],action:'Camera orbits near a lit brazier, showing the robe, character silhouette, stone and fire in the same scene. Then the player approaches another door.'},
  {nativeSeconds:[84,120],action:'Door/loading transition, hall, full presenter at96s and later broadcast inset at108/114s. Exclude this whole candidate range until exact boundaries/crop are separately reviewed.'},
  {nativeSeconds:[120,146],action:'Full-screen hall footage returns: character descends stairs, camera examines bright windows, carved door surrounds, statue and vaulted stairs. All are ordinary camera/player action, without a parameter toggle.'},
  {nativeSeconds:[146,160],action:'Presenter/interview shots. Exclude from actual-game quota.'},
  {nativeSeconds:[160,177.033984],action:'Player runs through a leafy courtyard and approaches Nellie Oggspire. Talk prompt at174s; do not imply a combat success or measured renderer change.'}
 ],
 publicPlaybackObservations:[
  {sourceSeconds:1052.771351,rate:1,paused:false,observation:'Stair hall and three bright windows; acquisition-time direct screenshot.'},
  {sourceSeconds:1124.600573,rate:1,paused:false,observation:'Player silhouette and burning brazier on the terrace; direct screenshot after intentional ordinary reload to1045.'},
  {sourceSeconds:1235.897116,rate:1,paused:false,observation:'Later close dialogue shot beyond the downloaded window; not assigned to this source file.'}
 ],
 candidateRanges:[[0,18],[18,43],[43,65],[65,84],[120,146],[160,177]],candidateSeconds:127,exactCutApproved:false,normalSpeedPlaybackReviewed:false,continuousMotionReviewed:false,annotationTrackingReviewed:false,finalUseApproved:false,bodyRatioApproved:false,rightsApprovedForPublicUse:false,comparison:'Longer world/camera context than the short March2026 DLSS5 surface previews; useful for setting an observation reference. It cannot replace the labelled DLSS5 OFF/ON shots or establish the game\'s internal volume/GI implementation.',newGitImages:0});
const checkpoint='production/research/game-lighting-history/checkpoint.json',c=read(checkpoint);
c.episode04HogwartsOfficialV79={execution,review:out,status:'native-source-reviewed-candidate',sourceSha256:e.source.sha256,actualDecodeExit:0,boardsDirectlyRead:8,candidateSeconds:127,continuousMotionReviewed:false,finalApproved:false,cpuThreads:0,gpuJobs:0,next:'Verify native boundaries/motion; insert a2022 camera/surface reference beside current2026 comparisons, never relabel it as DLSS5.'};
c.updatedAt=new Date().toISOString();const temp=checkpoint+'.writing-'+process.pid;fs.writeFileSync(temp,JSON.stringify(c,null,2)+'\n');fs.renameSync(temp,checkpoint);
console.log(JSON.stringify({review:out,boardsDirectlyRead:8,candidateSeconds:127,finalApproved:false}));
