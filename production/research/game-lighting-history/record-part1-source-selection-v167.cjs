// Source review records are deliberately separate from final encoded approval.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='production/research/game-lighting-history',p='projects/game-lighting-history-04/production';
const read=x=>JSON.parse(fs.readFileSync(path.join(root,x),'utf8').replace(/^\uFEFF/,''));
const sha=x=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,x))).digest('hex');
const write=(x,v)=>fs.writeFileSync(path.join(root,x),JSON.stringify(v,null,2)+'\n');
const sourcePlan=b+'/local/part1-native-review-v166/candidates.json',execution=b+'/local/part1-native-review-v166/sample-execution.json';
const plan=read(sourcePlan),run=read(execution);
if(run.status!=='completed-samples-only'||run.completed!==29||run.sampleImages!==234||run.boards!==41)throw Error('Completed source samples required');
for(const s of Object.values(plan.sources))if(sha(s.path)!==s.sha256)throw Error('Changed source');
for(const r of run.rows)for(const board of r.boards)if(sha(board.path)!==board.sha256)throw Error('Changed board');
const proposed={
 'shadow-virtual-page':{ranges:[[17,29]],observed:'Title transition at the beginning of the old candidate; virtual-page colors then lit scene. Colors visualize shadow data, not additional illumination.'},
 'shadow-moving-wheel':{ranges:[[112,181]],observed:'Wheel and shadow move while the camera retreats and returns. Camera/object/light changes require separate invalidation conditions; no independently measured page cost.'},
 'shadow-pool-edit':{ranges:[[98,122],[184,198]],rename:'shadow-resource-cache',observed:'Resource viewer and cache controls. This is not evidence of the proposed physical-pool512-to128 edit. Unchanged long resource-list holds are excluded.'},
 'tsr-moving-silhouette':{ranges:[[0,37]],observed:'Running/turning mannequin along wall. Terminal Note on TSR lecture card excluded; exact boundary still needs continuous review.'},
 'tsr-rotating-vectors':{ranges:[[0,32]],observed:'Rotating fan, grid and motion-vector visualization, then normal fan. Terminal Another Note on TSR lecture card excluded.'},
 'texture-streaming-toggle':{ranges:[[6,35]],observed:'Virtual Texture Streaming property and material sampler. Crop away presenter/conference frame. Final material/readability review remains pending.'},
 'texture-stack-uv':{ranges:[[96,120]],observed:'UV nodes duplicated and connections changed; displayed stack count3 to4. Same UV/sampler-source sharing differs from total texture lookup count.'},
 'texture-convert-dependencies':{ranges:[[202,219]],observed:'Context menu and conversion dialog lists dependent assets/materials. Long unchanged viewport/dialog holds excluded.'},
 'texture-project-settings':{ranges:[[246,266]],observed:'Project settings open/search. A setting label alone is not proof of a runtime performance improvement.'},
 'texture-runtime-size':{ranges:[[514,533],[553,564]],observed:'Runtime virtual-texture size controls and tooltip. This concerns generated texture data, not shadow-map physical-page count.'},
 'texture-streaming-statistics':{ranges:[[648,656],[670,682]],observed:'Console commands and statistics open/update. No invented benchmark or residency percentage.'},
 'texture-pool-auto-grow':{ranges:[[746,770]],observed:'Menu/settings search and pool controls. Long unchanged tail excluded. Editor auto-grow persistence and cooked-build behavior are distinct.'},
 'texture-resource-lists':{ranges:[[862,879],[882,889]],observed:'Actual resource selection and names. Virtual texture and virtual shadow resources contain different data. Later unchanged hold excluded.'},
 'texture-upload-budget':{ranges:[[926,950]],observed:'Camera/console interaction involving VT upload controls. Uploads per frame differs from frame generation and displayed FPS.'},
 'texture-courtyard-selection':{ranges:[[1047,1069]],observed:'Camera moves closer and selects building. Allocation depends on requested visible detail; no unobserved cache-hit rate or cost claim.'},
 'geometry-road-mask':{ranges:[[24,42]],observed:'Road spline editing and visualization. SplineMeshesNanite sign belongs to the 3D test scene; not an explanation slide.'},
 'geometry-barrier-debug':{ranges:[[96,134]],observed:'Camera, wireframe/triangle visualization and shaded barrier. Terminal blank/loading frame excluded.'},
 'geometry-courtyard-mask':{ranges:[[180,217]],observed:'Visualization menu, colored mask and shaded courtyard with animated people. Colors are not virtual-shadow pages.'},
 'geometry-programmable-debug':{ranges:[[306,350]],observed:'Console/selection and colored programmable-material visualizations. Do not infer visibility-buffer adoption from color alone.'},
 'geometry-material-car':{ranges:[[372,381]],observed:'Car material changes silver to rust. Long unchanged result excluded. Geometry identity differs from material shading.'},
 'mobile-texture-group':{ranges:[[0,16]],observed:'Texture-group dropdown in actual editor. Native crop needs exact UI boundary and legibility review.'},
 'mobile-device-profile':{ranges:[[30,50]],observed:'Device profile list and Android fields. Device policy selection, not measured bandwidth.'},
 'mobile-lod-cvars':{ranges:[[66,116]],observed:'Texture LOD group controls/dropdowns then CVar list. Profiles select settings; values need target-device validation.'},
 'mobile-compiler-warning':{ranges:[[132,150]],observed:'Platform shader statistics exposes missing offline-compiler warning. Unavailable compiler statistics must not become measured shader cost.'},
 'fortnite-mobile-profiling':{ranges:[[234,260]],observed:'Fortnite31.00 developer test map, moving camera/player and several material test surfaces. Existing-game development footage, not ordinary Battle Royale match or proof of tile-memory transfers.'},
 'rivalry-mobile-lighting':{ranges:[[26,41],[51,90]],observed:'2014 mobile engine demo: armor/hall/reflections. Cartoon/chicken/title interlude41–51 excluded. Historical demo does not prove later UE mobile-deferred implementation.'},
 'horizon-super-resolution':{ranges:[[1,7.35]],observed:'Manufacturer CNN/Transformer SR comparison of moving Aloy costume/bag details. Only6.35s; any longer analysis belongs to explanation, never held footage quota.'},
 'outer-generated-display':{ranges:[[0.5,16]],observed:'The Outer Worlds2 DLSS4.5 demo labels change5x/6x/5x/4x with different scenes. Displayed FPS/factor is not a simulation-rate or input-latency measurement.'},
 'cyber-light-reconstruction':{ranges:[[44,64]],observed:'Cyberpunk2077 split labelled feature-bundle comparison then action shots. End Phantom Liberty title card excluded. Combined DLSS settings cannot isolate Ray Reconstruction performance.'}
};
const out=p+'/part1-source-selection-direct-review-v167.json';if(fs.existsSync(path.join(root,out)))throw Error('Preserve recorded review');
const rows=run.rows.map(r=>({...proposed[r.id],id:r.id,source:plan.rows.find(x=>x.id===r.id).source,sourceSha256:r.sourceSha256,sampledBoards:r.boards.map(x=>({...x,directlyRead:true})),allSampleBoardsDirectlyRead:true,wholeMotionReviewed:false,exactCropApproved:false,finalNativeUseApproved:false}));
write(out,{schemaVersion:1,recordedAt:new Date().toISOString(),status:'direct-source-sample-review-and-proposed-trims',physicalPart:'game-lighting-history-04-1',sourcePlan:{path:sourcePlan,sha256:sha(sourcePlan)},execution:{path:execution,sha256:sha(execution),completed:29,exitCode:0,endedAt:run.endedAt},sources:plan.sources,all41SampleBoardsDirectlyRead:true,sampleImages:234,rows,proposedCapacitySeconds:rows.reduce((n,r)=>n+r.ranges.reduce((v,[a,z])=>v+z-a,0),0),sparseSamplingIsNotContinuousApproval:true,sourceOffsetVerified:false,fourGameCandidates:['Fortnite','Horizon Forbidden West','The Outer Worlds2','Cyberpunk2077'],fourGamesFullyTaughtAndReviewed:false,allFinalPixelsReviewed:false,bodyRatioApproved:false,originalPcmRegenerated:false,newGpuJobs:0,newGitImages:0,publicRights:'pending',nextAction:'Review exact boundaries/crops and normal-rate action, then independent bilingual additions and measured allocation; final dense moving/encoded approval stays separate.'});
const checkpoint=b+'/checkpoint.json',c=read(checkpoint);c.updatedAt=new Date().toISOString();c.status='episode04-physical01-source-sample-review-and-trim-v167';c.ownedActiveWork={owner:'game-lighting-history',status:'completed-samples-only',pid:run.pid,processCreateTime:run.createTime,commandLine:run.commandLine,cwd:run.cwd,session:36193,cpuThreads:2,gpuJobs:0,completed:29,total:29,exitCode:0,endedAt:run.endedAt,execution,review:out,nextAction:'Native boundaries/crops, four-game causal comparison and current duplicate review before new narration measurement.'};c.nextAction='Continue physical04-1 from source-selection-v167. Preserve completed04-3 ydW9Glmh0nM and actual a3a496bb/8a1332eb delivery. No source sampling/TTS/media restart for completed checkpoints.';write(checkpoint,c);
console.log(JSON.stringify({out,boards:41,rows:29,proposedSeconds:rows.reduce((n,r)=>n+r.ranges.reduce((v,[a,z])=>v+z-a,0),0),finalApproved:false,newGitImages:0}));
