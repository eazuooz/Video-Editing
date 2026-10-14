// CPU preparation only. It cannot approve timing, ASR, current mix or final pixels.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const ref=p=>({path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex')});
const scriptPath='projects/game-lighting-history-04/script/physical-part1-guided-actions.koen.v175.json',script=read(scriptPath),ttsPath=b+'part1-selected-current-tts-execution-v181.json',tts=read(ttsPath);
if(!tts.generationComplete||tts.exitCode!==0||tts.results.length!==37)throw Error('37 actual technical takes required');
const ranges={
 'shadow-wheel-surface':[[114.5,114.5+Math.ceil(tts.results.find(x=>x.id==='shadow-wheel-surface').samples/400)/60]],
 'shadow-wheel-change':[[114.5+Math.ceil(tts.results.find(x=>x.id==='shadow-wheel-surface').samples/400)/60,185.8]],
 'texture-stack-uv':[[90,126]],'texture-project-tile-settings':[[242,272]],
 'tsr-silhouette-history':[[0,37.5]],'tsr-rotation-vectors':[[0,33]],
 'outer-displayed-frames':[[0,16.4]],'cyber-light-reconstruction':[[44,63.5]],
 'geometry-barrier-views':[[96,135.3]],'geometry-courtyard-data':[[180,217.8]],
 'mobile-texture-group':[[0,17.9]],'mobile-device-policy':[[28,51.5]],'fortnite-normal-material':[[263,283]]
};
const sources=read(b+'part1-source-selection-direct-review-v167.json').sources;
const plans=[['first',10],['upscaling',13],['mobile',16]].map(([chapter,v])=>({chapter,path:b+`${chapter==='first'?'first':chapter==='upscaling'?'upscaling':'mobile'}-chapter-review-plan-v${v}.json`}));
const originals=plans.map(x=>({...x,binding:ref(x.path),plan:read(x.path)}));
let A=0,E=0;const originalCounts=[];
for(const x of originals){let aa=0,ee=0;for(const c of x.plan.cuts){if(c.kind==='explanation')ee+=c.frames;else if(c.kind.startsWith('actual'))aa+=c.frames;else throw Error('Unclassified original '+c.id);}
 A+=aa;E+=ee;originalCounts.push({chapter:x.chapter,actualFrames:aa,explanationFrames:ee,entries:x.plan.entries.length,audio:x.plan.audio});}
if(A!==4412||E!==28449||originalCounts.reduce((n,x)=>n+x.entries,0)!==36)throw Error('Original chapter scope changed');
const framing=read('production/research/game-lighting-history/local/episode04-physical-framing-v59/plan.json');
const framingRows=['part1-overview','part1-conclusion'].map(id=>{const s=framing.scenes.find(x=>x.id===id);if(!s)throw Error('Framing missing');return{id,frames:s.frames,source:s.source,samples:s.sourceSamples};});
E+=framingRows.reduce((n,r)=>n+r.frames,0);
let maxActual=A,shortObservationCapacity=0;
const rows=script.scenes.map(s=>{
 const pcm=tts.results.find(x=>x.id===s.id);if(!pcm||!pcm.technicalTailGatePassed||ref(pcm.path).sha256!==pcm.sha256)throw Error('Selected take changed '+s.id);
 const frames=Math.ceil(pcm.samples/400),rr=s.role==='actual'?(ranges[s.id]||s.ranges):[],capacityFrames=rr.reduce((n,[a,z])=>n+Math.floor((z-a)*60+1e-7),0),actualFrames=s.role==='actual'?Math.min(frames,capacityFrames):0,explanationFrames=frames-actualFrames;
 A+=actualFrames;E+=explanationFrames;maxActual+=capacityFrames;
 // A planning bound, never permission to insert silence or unrelated idle footage.
 const optionalReadingFrames=s.role==='actual'?Math.max(0,Math.min(45,capacityFrames-frames)):0;shortObservationCapacity+=optionalReadingFrames;
 const source=s.role==='actual'?ref(sources[s.source].path):null;
 return{id:s.id,insertAfter:s.insertAfter,ko:s.ko,en:s.en,source,normalSpeedNativeRanges:rr,pcm:{path:pcm.path,sha256:pcm.sha256,samples:pcm.samples,sampleRate:pcm.sampleRate},pcmFrames:frames,minimumActualFrames:actualFrames,minimumExplanationFrames:explanationFrames,nativeCapacityFrames:capacityFrames,optionalReadingFrames,requiresCompleteWordAnchorBeforeCut:explanationFrames>0&&s.role==='actual',purpose:explanationFrames>0&&s.role==='actual'?'Keep full spoken explanation with a separate meaningful spatial model before native title/presenter/length limits.':s.role==='actual'?'Normal-speed concept-matched native action and narrated observation.':'Independent black projected prerequisite or conceptual conclusion.',sourceAudio:false,loop:false,slowdown:false,finalNativeSelectionApproved:false,movingAnnotationsApproved:false};
});
const deficit=Math.ceil(1.5*E-A),out=b+'part1-measured-allocation-draft-v192.json';if(fs.existsSync(path.join(root,out)))throw Error('Preserve draft');
fs.writeFileSync(path.join(root,out),JSON.stringify({schemaVersion:1,preparedAt:new Date().toISOString(),slug:'game-lighting-history-04-1',palette:'research-black-v1',captionStyle:'boxed-white-forest-v1',captionCenter:[960,970],fontSize:48,phoneCueMaximumBoxWidth:980,rows,originalChapters:originalCounts,framing:framingRows,bindings:[ref(scriptPath),ref(ttsPath),...originals.map(x=>x.binding),ref(b+'part1-capacity-boundary-direct-review-v188.json'),ref(b+'part1-boundary-direct-review-v180.json')],originalParagraphs:36,newGuidedParagraphs:37,framingParagraphs:2,expectedParagraphs:75,provisional:{minimumActualFrames:A,minimumExplanationFrames:E,maximumNativeActualFrames:maxActual,additionalActualFramesRequiredAtMinimumExplanation:deficit,availableSubsecondNormalSpeedObservationFrames:shortObservationCapacity,mathematicallyFeasibleWithShortObservations:deficit<=shortObservationCapacity},requiredFurtherSelection:'Inspect real cue/cut word anchors and normal-speed source actions. Each retained observation beat must have a visible teaching purpose. Never use title cards, presenter, padding, loops, static quota holds or unrelated idle as actual footage. If the source/action cannot support the needed frames, add a genuinely narrated and reviewed example.',spatialModels:['motion-canvas/src/projects/game-lighting-history-04/spatial/part1-transfer-model-v171.tsx','motion-canvas/src/projects/game-lighting-history-04/spatial/part1-history-contract-v177.tsx','motion-canvas/src/projects/game-lighting-history-04/spatial/part1-observation-contract-v190.tsx'].map(ref),technicalModelCheck:{command:'node node_modules/typescript/bin/tsc --project tsconfig.game-lighting-history04-part1-observation-v190.json --noEmit',cwd:'motion-canvas',exitCode:0,scope:'Only new observation model and its dependencies; no repository-wide TypeScript pass claimed'},allFullAsrCompared:false,finalTimingApproved:false,bodyRatioApproved:false,rendered:false,allFinalPixelsReviewed:false,uploaded:false,newImages:0},null,2)+'\n');
console.log(JSON.stringify({original:36,framing:2,new:37,total:75,A,E,deficitFrames:deficit,shortObservationCapacity,planOnly:true}));
