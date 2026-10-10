const fs=require('node:fs'),crypto=require('node:crypto');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const prod='projects/game-lighting-history-03/production',ep=prod+'/native-repair-f-pixel-execution-v18.json',x=JSON.parse(fs.readFileSync(ep));
if(x.status!=='complete'||x.exitCode!==0||x.boards.length!==21||x.images.length!==121)throw Error('Incomplete F pixels');
const notes=[
 'Lumen Scene is legible in the actual enlarged diagnostic menu. The menu closes during the cut; the same-frame detail then shows source rock pixels. No hardware path or internal cost is inferred.',
 'Diagnostic-menu exit remains visible; Directional Light cut starts with an empty source Details panel before selection. Fixed captions remain clear.',
 'The source selects L_Sun_DirectionalLight and reveals Transform/Light properties. Actual Intensity 0.0 lux, Light Color and Source Angle are legible above captions; these are displayed source settings, not a new measurement.',
 'Warm Color Picker and native rotation gizmo are visible. Bright and shaded rock faces change while rotation is manipulated; no exposure or isolated GI timing is claimed.',
 'Rotation marker remains above the fixed caption. The late camera turn and transient motion blur are preserved and the narration explicitly separates camera motion.',
 'Warm/dim surfaces and the source rotation marker remain visible through the end of the first rotation cut and start of its continuation.',
 'Continuation retains the warm Color Picker and visible rock structures; the later blue-light segment begins with native camera motion, not a controlled fixed-camera comparison.',
 'Blue Light Color values remain legible. Camera moves across the cliff while those values are shown; this does not establish a fixed-camera light-change experiment.',
 'Blue cliff camera motion continues; the warm-light camera-motion cut is a separate source interval and is labelled accordingly.',
 'Camera motion pans across warm cliffs, with transient blur. The partial original Color Picker stays visible at the right; no exposure lock or full setting equivalence is inferred.',
 'Warm camera-motion view ends on the rock spires. Narration says exposure must be controlled, not that this original source already controls it.',
 'Wide interior framing introduces corridor, window, sofa, ceiling and back wall together. Captions preserve the areas needed for this observation.',
 'Wide living room and actual Show menu lead to a dark state. The exact GI checkbox lies below the source broadcast viewport and is not observed.',
 'Dark room, bright window, native menu and subsequent camera movement are visible. No hidden checkbox is marked verified.',
 'Dark-to-bright transition is visible with the source menu; camera changes alongside it. Narration describes observed states and separates them from metrology.',
 'Bright sofa/back-wall/ceiling view remains visible while the narration separates camera movement and explicitly says this is not an exposure-controlled measurement.',
 'Window and remaining room surfaces stay legible. The narration does not equate a bright window with complete indirect lighting.',
 'Room camera movement goes from window to hallway; direct-lit areas and other surfaces can be compared visually without assuming internal cache contents.',
 'Hallway and window remain visible through the end. No artificial GI toggle, measured delay or invented light ratio is introduced.',
 'Conclusion uses the native dark interior state and actual Show menu to illustrate a different lighting question from Nanite geometry. No internal-mode proof is claimed.',
 'Last source frame becomes bright with the native menu still present. This transition is preserved rather than labelling the dark region a decode error.'
];
const records=x.boards.map((b,i)=>{if(sha(b.path)!==b.sha256)throw Error('Changed board');const images=b.imageIndices.map(n=>x.images[n-1]);for(const q of images)if(sha(q.path)!==q.sha256)throw Error('Changed image');return {...b,directlyRead:true,images,observation:notes[i]};});
const out=prod+'/native-repair-f-direct-review-v18.json';if(fs.existsSync(out))throw Error('Preserve prior review');
fs.writeFileSync(out,JSON.stringify({recordedAt:new Date().toISOString(),execution:{path:ep,sha256:sha(ep)},boardsDirectlyRead:21,imagesDirectlyRead:121,records,allChangedSampleBoardsRead:true,changedSampleSemanticApproval:true,sourceLabelCaptionClearanceApproved:true,unobservedControl:'Exact Lumen GI checkbox below the original broadcast viewport',controlledExposureExperiment:false,original80ContainsCameraMovement:true,browserMotionObservations:[{sourceRange:[404,412],actualReached:412.226,preset:'lumen-camera'},{sourceRange:[710,715.883333],actualReached:716.112,preset:'lumen-left'},{sourceRange:[681,684],actualReached:684.192,preset:'lumen-left'}],speed:1,fullAnimatedEncodedPlaybackReviewed:false,allFinalPixelsReviewed:false,qaApproved:false,collected:false,uploaded:false,newGitImages:0},null,2)+'\n');
const cp='production/research/game-lighting-history/checkpoint.json',q=JSON.parse(fs.readFileSync(cp));q.episode03NativeFDirectReview={path:out,sha256:sha(out),boards:21,images:121,changedSampleSemanticApproval:true,allFinalPixelsReviewed:false};q.updatedAt=new Date().toISOString();fs.writeFileSync(cp,JSON.stringify(q,null,2)+'\n');console.log(JSON.stringify({boards:21,images:121,sampleApproval:true,finalApproval:false}));
