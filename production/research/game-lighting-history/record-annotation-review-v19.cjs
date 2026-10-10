const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),p='projects/game-lighting-history-03/production/';
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8'));
const sha=f=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,f))).digest('hex');
const write=(f,d)=>{if(fs.existsSync(path.join(root,f)))throw Error('Preserve existing review '+f);fs.writeFileSync(path.join(root,f),JSON.stringify(d,null,2)+'\n');};
const ann=read(p+'native-annotation-plan-v19d.json'),d=read(p+'native-annotation-pixel-execution-v19d.json'),c=read(p+'native-annotation-pixel-execution-v19c.json');
if(d.status!=='complete'||d.images.length!==26||d.boards.length!==5||c.images.length!==50||c.boards.length!==9)throw Error('Actual pixel execution differs');
for(const x of [...d.images,...d.boards,...c.images,...c.boards])if(sha(x.path)!==x.sha256)throw Error('Changed reviewed pixel');
const record={reviewedAt:new Date().toISOString(),status:'two-pilots-sampled-moving-pixels-reviewed',
 references:['native-annotation-plan-v19d.json','native-annotation-render-execution-v19d.json','native-annotation-render-execution-v19c.json','native-annotation-pixel-execution-v19d.json','native-annotation-pixel-execution-v19c.json'].map(f=>({path:p+f,sha256:sha(p+f)})),
 historicalV19c:{all50ImagesAnd9BoardsDirectlyRead:true,rayCameraCutDetailFailed:true,resolvedBy:'v19d',dlssUnchangedAndReused:true},
 correctedV19d:{all26ImagesAnd5BoardsDirectlyRead:true,frames:[19928,19929,19930,19949,19950,19951,19952,19971,19972],
  observation:'At the actual hard camera cut f19929, the main bulb moves near the fixed caption. Its complete same-frame original marker is enlarged above the caption from local278, rather than waiting until300. Red circle follows the inset marker after the cut; teal contour follows the actual blue cube and excludes artificial crop edges.',
  sampleClearanceApproved:true},
 browserPlayback:{url:'http://127.0.0.1:9265/@fs/D:/Github/Video-Editing/production/research/game-lighting-history/local/current-motion-review-v19.html',speed:1,
  ray:{actualFullRunEndpointObservedSeconds:6,fullRunEndFrame:20010,directMovingSamples:[{localSeconds:2.176,globalFrame:19781},{localSeconds:4.892,globalFrame:19944}],
    observation:'Circle and cube contour align in both actual camera poses; after the hard cut the same-frame enlarged bulb is clear above fixed cue77.'},
  dlss:{actualFullRunEndpointObservedSeconds:11.3,fullRunEndFrame:29729,directMovingSamples:[{localSeconds:2.187,globalFrame:29183},{localSeconds:5.244,globalFrame:29366},{localSeconds:10.197,globalFrame:29663}],
    observation:'Performance/50% changes to Ultra Performance/33.3%; red mode and teal input-resolution underlines remain on their actual UI rows. They turn off before Built-in TAA/100%. Not a ray-count or measured-FPS claim.'},
  caveat:'Playback endpoints plus directly read moving samples, not continuous human listening or inspection of every decoded frame.'},
 correctedCueMetadata:{'03-ray-shadow-02-repair-e5':[76,77,78],'original-31-repair-01':[110,111,112]},
 cueMetadataHistory:'The preparation plan erroneously lists DLSS115/116/117. Actual caption-plan and burned samples are110/111/112; historical plan bytes are preserved.',
 cuts:ann.cuts.map(x=>({id:x.id,fromFrame:x.fromFrame,toFrame:x.toFrame,output:x.output,sha256:sha(x.output),verification:x.verification,annotations:x.annotations,annotationsSha256:sha(x.annotations),sampledMovingPixelApproval:true})),
 sameFrameEnlargement:true,screenSpaceOnly:true,unverifiedWorldMeasurements:0,unverifiedEngineInternals:0,originalAudioAndTimingPreserved:true,
 annotationsNarrationMatched:true,editableLayersPreserved:true,reviewPairPreparationAllowed:true,allCurrentNativeCutsAnnotated:false,
 allMovingPixelsReviewed:false,allFinalPixelsReviewed:false,qaApproved:false,collected:false,uploaded:false,humanWholeListening:'pending',humanPronunciation:'pending',newGitImages:0};
write(p+'native-annotation-direct-review-v19.json',record);
const base=read(p+'current-input-plan-v19.json'),inputs=structuredClone(base.inputs);
for(const x of record.cuts){const i=inputs.findIndex(y=>y.id===x.id);if(i<0||inputs[i].fromFrame!==x.fromFrame||inputs[i].toFrame!==x.toFrame)throw Error('Changed annotation timing');inputs[i]={...inputs[i],output:x.output,verification:x.verification,annotationReview:p+'native-annotation-direct-review-v19.json',annotationOutputSha256:x.sha256};}
write(p+'current-input-plan-v20.json',{...base,preparedAt:new Date().toISOString(),status:'review-pair-inputs-with-unchanged-current-mix-awaiting-final-pixels',inputs,
 references:[...base.references,{path:p+'current-input-plan-v19.json',sha256:sha(p+'current-input-plan-v19.json')},{path:p+'native-annotation-direct-review-v19.json',sha256:sha(p+'native-annotation-direct-review-v19.json')}],
 annotationCutCount:2,allInputPixelsReviewed:false,allMovingPixelsReviewed:false,allFinalPixelsReviewed:false,qaApproved:false,collected:false,uploaded:false});
const cp='production/research/game-lighting-history/checkpoint.json',checkpoint=read(cp);
checkpoint.episode03NativeAnnotationDirectReview={path:p+'native-annotation-direct-review-v19.json',sha256:sha(p+'native-annotation-direct-review-v19.json'),cuts:2,sampleApproval:true,allFinalPixelsReviewed:false};
checkpoint.episode03CurrentReviewInputs={path:p+'current-input-plan-v20.json',sha256:sha(p+'current-input-plan-v20.json'),inputs:inputs.length,actualFrames:55418,explanationFrames:36946,finalFrames:93084,pcmUnchanged:true,allFinalPixelsReviewed:false};
checkpoint.updatedAt=new Date().toISOString();fs.writeFileSync(path.join(root,cp),JSON.stringify(checkpoint,null,2)+'\n');
console.log(JSON.stringify({pilotCuts:2,correctedSamples:26,correctedBoards:5,currentInputs:inputs.length,fullFinalApproval:false}));
