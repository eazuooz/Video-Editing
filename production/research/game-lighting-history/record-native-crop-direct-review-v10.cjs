const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='production/research/game-lighting-history',p='projects/game-lighting-history-03',now=new Date().toISOString();
const read=x=>JSON.parse(fs.readFileSync(path.join(root,x),'utf8')),sha=x=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,x))).digest('hex'),write=(x,v)=>fs.writeFileSync(path.join(root,x),JSON.stringify(v,null,2)+'\n');
const executionPath=b+'/local/episode03-native-crop-v10/execution.json',execution=read(executionPath);
if(execution.status!=='native-crop-samples-ready'||execution.completed.length!==48)throw Error('Require all48 actual completed samples');
const notes=[
 '42s: raw Show/LightingFeatures/LumenGI label is below the viewport crop. Presenter removed, but reject cropped shot for asking viewer to read that label. Review subsequent lit/dark states separately.',
 '61s: blue-gray cave viewport; both crops remove presenter. Mode/transition cannot be inferred from color alone.',
 '106s: dark cave and stair/camera view retained, presenter excluded; not locked-camera/exposure A/B proof.',
 '190s: rock/transform gizmo beside opening preserved in left viewport; right controls crop loses this focus. Prefer viewport for this action.',
 '241s: gray rounded geometry and green debug shapes. Representation observation; does not show cache texture coverage.',
 '256s: gray field/rounded geometry. Pair with explicit mode evidence at270s, not inferred from color alone.',
 '270s: raw Show/Visualize has checked Mesh DistanceFields. This confirms the selected mode; cropped menu sits near bottom captions, so use mode evidence internally and review after menu dismissal for final cut.',
 '361s: Show/UseDefaults menu and altered scene display. Do not label this SurfaceCache from appearance.',
 '394s: pale New color versus white Old in ColorPicker. Right crop retains wheel; lower numeric fields/buttons are cropped. No numerical color claim.',
 '405s: warm yellow cave with active picker. Both crops remove presenter, retain cave/wheel respectively.',
 '480s: blue/purple cave and active picker; no measured settling latency inferred.',
 '498s: red-orange cave and picker, presenter excluded; final exact light-change transition still requires motion review.',
 '536s: orange cave opening/light transform gizmo. Left crop preserves selected geometry and action focus.',
 '600s: orange close interior, presenter excluded; camera and lighting are not fixed A/B.',
 '672s: dark Lakehouse with bright window/direct region. Presenter excluded in both crops.',
 '685s: bright white Lakehouse and different camera view. Do not compare672/685 as controlled same-camera exposure.',
 '705s: lit sofa/window interior; clean presenter-free viewport.',
 '737s: PostProcess Lumen settings are visible in raw right panel but lower settings lost in controls crop. Prefer viewport unless a separately verified setting-label framing is prepared.',
 '118s: raw Nanite Triangles visualization of dense colored geometry; crop removes left mode label and all presenters. Raw label is internal mode evidence.',
 '200s: raw Nanite Clusters visualization; retained colored architecture, presenters removed. Do not call all colored pieces individual triangles.',
 '232s: MAIN/PRE-CULL/POST-CULL and geometry counters retained, presenters excluded. Previously observed218–242 unchanged-view hold is rejected for actual-footage quota.',
 '322s: shaded facade/counters retained and presenter excluded; a still does not measure culling cost.',
 '466s: overhead statues/foreground occlusion and counters; presenter excluded. Relevant visibility, no controlled benchmark.',
 '490s: Clusters colored architecture/counters; crop removes presenters. Mode is Clusters, not triangle or distance-field display.',
 '610s: bicycle tubing and stone ground/counters retained in crop; presenter excluded. Geometry observation only.',
 '657s: white sculpted head/facial ridges/counters retained; presenter excluded. No unrestricted/free geometry claim.',
 '705s: ornate architectural depth/counters retained; presenter excluded.',
 '742s: architecture at farther camera position/counters retained. No fixed-condition projected-error measurement.',
 '814s: portal arch/counters retained; presenter excluded. Portal is scene geometry, not proof of ray acceleration internals.',
 '214s RTXGI: DDGIVolume2 selected, bounding volume over two rooms and transform/scale/ProbeCounts settings. Native editor UI, no presenter. Counts/control holds require exact action selection.',
 '268s RTXGI: visualized probes in rows around red/green walls and volume bounds; VisualizeProbes checked. Spheres are debug representation, not physical light sources.',
 '296s RTXGI: changed probe count field/spacing and spherical debug probes around rooms. Exact change/motion requires continuous playback.',
 '386s RTXGI: city-like blocks plus dense probe grid; native text64x64x4 and16384 displayed. Source constraints only, not our measured performance or all-probes-updated-every-frame claim.',
 '179s HWRT: blue cube, point light icon/transform and SourceRadius field selected. Shadow boundary is visible; sample alone cannot prove radius animation or internal BVH update.',
 '207s HWRT: two point light icons and RayTracedShadows setting/tooltip shown beside cube shadow. Exact toggle must be reviewed in motion.',
 '196s DLSS UE5: NVIDIA DLSS Performance selected and developer stats displayed alongside reflective sphere. Read actual mode; no converted FPS benchmark.',
 '225s DLSS UE5: BuiltIn/DLAA selected. Different operation from DLSS lower-resolution reconstruction; preserve naming.',
 '263s DLSS UE5: NVIDIA ImageScaling UltraQuality selected. Spatial scaling example; do not label DLSS or FrameGeneration.',
 '18s NvRTX: translucent mug/mirror beside Reflections/Shadows/RTXGI/Translucency controls. Multiple independent effect controls; no common-filter claim.',
 '43s NvRTX: moving hanging star light and RayTracedShadows banner. Bottom banner risks fixed-caption overlap; final reframing required.',
 '64s NvRTX: attic window light/room and RTXGlobalIllumination banner. Bottom banner risks fixed-caption overlap; no probe/cache internals visible.',
 '75s NvRTX: hanging stars and PhysicsAndInteractivity banner. Relevant light/object action; banner requires final framing review.',
 '20s EscapeFromNaraka: RAYTRACEDSHADOWS+REFLECTIONS / RTXOFF label, orange altar/chamber. This particular sample is not an isolated RTXGI/DDGI toggle; exact feature intervals must match narration. Bottom native banner needs caption-safe framing.',
 '8s Control: source split DLSS OriginalQuality versus DLSS2 Quality,1080pHighRTX2060, board lettering/fan/character. Native bottom conditions banner risks caption overlap; do not crop away conditions without retaining accurate source condition context.',
 '24s BattlefieldV: soldiers/explosion/tram and puddle reflection; no bottom explanatory banner except source logo. Historical2018 pre-release capture, not shippedpatch measurement.',
 '11s DeliverUsTheMoon: DLSSOFF/ONQuality,RayTracingEpic1080pRTX2060, helmet interior and vendor counters47/78. Source conditions/expanded shot, not our benchmark; bottom banner conflicts with fixed captions pending reframing.',
 '44s Wolfenstein: aiming view/branches/robot, DLSSOFF/ONQuality,1080pUberRTX2060 and vendor83/114. Source conditions, not our benchmark; bottom comparison banner/UI pending final caption-safe framing.',
 '45s RTXDI: boulevard signage/window/pavement result, no presenter. Does not expose reservoir candidate replacement, probabilities or GPU timing.'
];
if(notes.length!==48)throw Error('All48 direct notes required');
const points=execution.completed.map((x,i)=>{if(sha(x.board.path)!==x.board.sha256)throw Error('Board changed:'+x.board.path);for(const im of x.images)if(sha(im.path)!==im.sha256)throw Error('Image changed');return {...x,board:{...x.board,directlyViewed:true,reviewedAt:now},directObservation:notes[i],sampledCropReviewed:true,fullMotionReviewed:false,finalCaptionPixelsReviewed:false,finalUseApproved:false};});
const file=p+'/production/native-crop-direct-review-v10.json';
write(file,{reviewedAt:now,execution:{path:executionPath,sha256:sha(executionPath)},method:'All48 raw/crop boards directly read with view_image; first24 previous segment and remaining24 current segment. Point evidence and exact hashes preserved. Sample review does not authorize continuous intervals.',points,all48BoardsDirectlyViewed:true,presenterExclusionSampledPass:{lumen:18,nanite:11},nativeDistanceFieldModeConfirmed:{source:'lumen-content-examples-2021',seconds:270,label:'Mesh DistanceFields',checked:true,rawPath:points[6].images.find(x=>x.role==='raw').path},surfaceCacheDebugNativeProofObserved:false,rejectedStaticRange:{source:'nanite-editor-motion-2021',inSeconds:218,outSeconds:242,reason:'Prior1x native playback showed unchanged architecture while counters/settings remained; no filler quota'},captionPolicy:'Keep960,970 boxed-white-forest-v1; correct shot/crop/cue if source banner/control conflicts. No caption relocation.',sourceAudioUsed:false,sourceStartOffsetVerified:false,fullMotionReviewed:false,allFinalPixelsReviewed:false,rightsApproved:false,newGitRasterFiles:0,localOnly:true,finalVideoApproved:false});
console.log(JSON.stringify({path:file,boards:48,distanceFieldModeConfirmed:true,fullMotionReviewed:false,finalVideoApproved:false}));
