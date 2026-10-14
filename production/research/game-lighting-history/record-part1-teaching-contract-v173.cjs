// Records the observed teaching contract, not rendered/voice completion.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const output=b+'/part1-four-game-teaching-contract-v173.json';
if(fs.existsSync(path.join(root,output)))throw Error('Preserve existing teaching evidence');
const scriptPath='projects/game-lighting-history-04/script/physical-part1-guided-actions.koen.v169.json',script=read(scriptPath);
const sources=script.sources;
for(const row of Object.values(sources))if(sha(row.path)!==row.sha256)throw Error('Changed reviewed source');
const games=[
 {game:'Horizon Forbidden West',sourceKey:'horizon',sourceVideoId:'WXaM4WK3bzg',nativeRanges:[[1,7.35]],
  before:'Source simultaneously labels CNN and Transformer Super Resolution conditions for the same moving bag detail.',
  action:'Aloy and the embroidery move within the labelled comparison. Track the same embroidery boundary.',
  result:'The comparison permits inspecting the boundary/detail appearance under each labelled method; no input-resolution, frame-time or quality score was independently measured.',
  commonPrinciple:'Identify which image information is reconstructed and whether the observation refers to the same moving surface.',
  difference:'Surface-detail reconstruction rather than added display frames or a device-budget measurement.',
  prerequisiteScene:'horizon-comparison-before',actualScenes:['horizon-detail-motion'],
  annotationTarget:'Embroidery on the actual moving bag; reset any target on a shot cut, preserve both original method labels.',
  limits:['Only6.35s is actual capacity, not narration-measured allocation.','A longer explanatory comparison must be spatial explanation time, never a loop or frozen actual quota.']},
 {game:'The Outer Worlds 2',sourceKey:'outer',sourceVideoId:'GV4DOJNKfuw',nativeRanges:[[0.5,16]],
  before:'Source-labelled dynamic frame-generation demonstration; scene changes are visible.',
  action:'The camera and game scene move while source multiplier changes5x/6x/5x/4x. Final source view labels198FPS and4x.',
  result:'Read the source display multiplier without treating displayed-frame frequency as game-state/input-update frequency.',
  commonPrinciple:'Separate produced images, displayed images and the data reused to create intermediate displays.',
  difference:'Display frequency, not detail reconstruction in the preceding bag comparison.',
  prerequisiteScene:'outer-comparison-before',actualScenes:['outer-displayed-frames'],
  annotationTarget:'Actual labelled factor/FPS regions and a moving scene target; annotations reset for every source shot.',
  limits:['Source FPS is not our benchmark.','Changing scenes/conditions does not isolate one algorithm or measure input latency.']},
 {game:'Cyberpunk2077',sourceKey:'cyber',sourceVideoId:'oMCC9TgsCDY',nativeRanges:[[44,62]],
  before:'The official2023DLSS3.5game demonstration labels a bundle of renderer/reconstruction conditions.',
  action:'Character/camera/action move through visible light and reflective surfaces. At60s actual action retains89FPS/DLSS3.5FullRTOn source labels.',
  result:'Observe the light/reflection region in the actual moving frame and retain the shown condition. It is not a single-feature fixed-camera experiment.',
  commonPrinciple:'Ask what the renderer supplies to a reconstruction stage and what the displayed result represents.',
  difference:'Lighting-information reconstruction; its inputs differ from surface-detail reconstruction and display-frame generation.',
  prerequisiteScene:'cyber-comparison-before',actualScenes:['cyber-light-reconstruction'],
  annotationTarget:'An actual lit/reflective surface, source condition labels and active shot boundary. Never invent unobserved sparse sample locations on gameplay.',
  limits:['End62excludes the64sblack transition and later title.','Bundle footage cannot prove Ray Reconstruction alone caused all shown differences.']},
 {game:'Fortnite',sourceKey:'mobile',sourceVideoId:'nZlVkI3j7Xs',nativeRanges:[[240,260],[276,289.8]],
  before:'Actual Fortnite31mobile developer test map. HQ/LQNoisebumpmap rock labels and a source diagnostic graph are visible.',
  action:'The character/camera move past the rock tests and later approach a wall labelled GBuffer Normals. The original graph/diagnostics change during motion.',
  result:'Connect the observed material/test condition with the source diagnostic being inspected, rather than claiming a general device-performance ranking.',
  commonPrinciple:'Record the producing stage, data/settings, target-device conditions and consuming scene together.',
  difference:'Target-device/material budget inspection, not super resolution, display-frame interpolation or isolated light reconstruction.',
  prerequisiteScene:'fortnite-comparison-before',actualScenes:['fortnite-mobile-test','fortnite-normal-material'],
  annotationTarget:'Source HQ/LQlabels, corresponding moving rock/wall surface and source graph; preserve stat labels and fixed subtitle clearance.',
  limits:['Developer test map, not ordinary Battle Royale benchmark.','GBuffer Normals wall label is not proof of a complete GBuffer diagnostic or tile-memory transfer.','234sfull presenter excluded; later phone inset needs a different crop.']}
];
const samplePath=b+'/local/part1-mobile-framing-v173/execution.json',samples=read(samplePath);
if(samples.exitCode!==0||samples.results.length!==8)throw Error('8 actual framing samples required');
for(const row of samples.results)if(sha(row.path)!==row.sha256)throw Error('Changed framing pixels');
const record={schemaVersion:1,recordedAt:new Date().toISOString(),physicalPart:'game-lighting-history-04-1',question:'제한된 하드웨어에서 어떤 화면 정보를 계산하고 저장하며 다시 사용해야 할까?',
 script:{path:scriptPath,sha256:sha(scriptPath)},observation:{path:b+'/part1-native-continuous-observations-v169.json',sha256:sha(b+'/part1-native-continuous-observations-v169.json')},
 minimumDistinctExistingGames:4,games:games.map(g=>({...g,source:sources[g.sourceKey],currentWholeAsrReviewed:false,currentIndependentContextReviewed:false,currentMixedAsrReviewed:false,currentMovingAnnotatedPixelsReviewed:false,fullyTaughtAndReviewed:false})),
 connectingScenes:['horizon-comparison-before','outer-comparison-before','cyber-comparison-before','fortnite-comparison-before','four-game-transfer-conclusion'],
 engineDemonstrations:['Unreal shadow/texture/Nanite diagnostics','TSR mannequin/fan','Mobile profile/LOD/compiler controls','Rivalry2014'],
 engineDemonstrationsAddedToFourGameCount:false,retainedOriginal111PcmRegenerated:false,
 nativeFramingSamples:{path:samplePath,sha256:sha(samplePath),all8StillSamplesDirectlyRead:true,movingFramingApproved:false,finalCaptionClearanceApproved:false,
  findings:['Group crop preserves texture and dropdown while excluding lecture title.','Compiler crop preserves one-target warning and present entries; never infer zero cost from n/a.','Phone crop preserves graph/rock or wall while removing presenter; right peripheral button is clipped.','Game caption widths/crops require final cue review: two-line bottom boxes can intersect a small corner of the Jump control. Keep position960,970 and resolve through cut/crop/cue width.','267s is already the phone inset; actual framing transition is not yet located exactly.','Profile/LOD/CVar controls need their own precise crops, not the group crop.']},
 fourGamesFullyTaughtAndReviewed:false,measuredBody60to40Approved:false,allFinalPixelsReviewed:false,qaApproved:false,uploaded:false};
fs.writeFileSync(path.join(root,output),JSON.stringify(record,null,2)+'\n');
console.log(JSON.stringify({record:output,games:games.length,sourceSamplesOnly:true,finalApproved:false}));
