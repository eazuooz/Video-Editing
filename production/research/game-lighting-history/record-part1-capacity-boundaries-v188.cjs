const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const ref=p=>({path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex')});
const input='production/research/game-lighting-history/local/part1-capacity-review-v183/plan.json',p=read(input);
const facts=[
 {id:'geometry-barrier-debug',clock:135.3,pixels:'Actual normally shaded editor barrier remains visible. No loading/blank frame at this observed clock.',safeProposedRange:[96,135.3]},
 {id:'geometry-courtyard-mask',clock:217.8,pixels:'Actual courtyard and moving people remain visible, normal shading after diagnostic comparison.',safeProposedRange:[180,217.8]},
 {id:'mobile-texture-group',clock:17.9,pixels:'Lecture title remains outside actual editor inset. Editor viewport and texture properties remain, dropdown closed. Preserve actual editor crop, not the title.',safeProposedRange:[0,17.9]},
 {id:'mobile-device-profile',clock:28,pixels:'Actual editor menu Tools/Platforms/Device Profiles; heading outside crop. New crop at the menu must be verified separately.',safeProposedRange:[28,51.5]},
 {id:'mobile-device-profile',clock:51.5,pixels:'Android device profile table and variables visible. Policy controls, not measured bandwidth.'},
 {id:'mobile-compiler-warning',clock:150,pixels:'Shader Platform Stats lecture layout with actual editor and warning table inset. Native crop must remove lecture title.',safeProposedRange:[132,150]},
 {id:'mobile-compiler-warning',clock:153.9,pixels:'Layout switches to presenter at upper left and editor inset at lower right; old crop is invalid for this extension.',extensionRejected:true,alternative:'Preserve remaining complete narration with a spatial available/unavailable measurement explanation.'},
 {id:'outer-generated-display',clock:0.009,pixels:'Normal-speed game motion and5x label, with UI in view.',safeProposedRange:[0,16.4]},
 {id:'outer-generated-display',clock:16.4,pixels:'Actual game scene,4x198FPS/DLSS4.5 labels. No title card. Label is not simulation frequency or measured latency.'},
 {id:'cyber-light-reconstruction',clock:63.5,pixels:'Actual character/vehicle action with160FPS andDLSS3.5 FullRTOn labels. Feature bundle, not isolated RR test.',safeProposedRange:[44,63.5]},
 {id:'fortnite-mobile-profiling',clock:274.8,pixels:'Phone game inset at lower right, rock labelled ClearCoat and graph; presenter outside required crop.',safeProposedRange:[274.8,283]},
 {id:'fortnite-mobile-profiling',clock:283,pixels:'Phone game inset: character, diagnostic graph and GBufferNormals test wall; presenter outside required crop.'},
 {id:'fortnite-mobile-profiling',clock:284,pixels:'Full presenter; no game viewport.',extensionRejected:true},
 {id:'fortnite-mobile-profiling',clock:286,pixels:'Full presenter; no game viewport.',extensionRejected:true},
 {id:'fortnite-mobile-profiling',clock:288.5,pixels:'Full presenter; no game viewport.',extensionRejected:true},
 {id:'fortnite-mobile-profiling',clock:289.9,pixels:'Full presenter; no game viewport.',extensionRejected:true,alternative:'Cut at or before283; complete remaining narration with a spatial material/diagnostic comparison.'},
 {id:'rivalry-mobile-lighting',clock:93,pixels:'2014 engine-demo corridor/armor lighting remains, dark fade toward closing. Retain previously observed51–90 rather than use fade as quota.',safeProposedRange:[51,90]}
];
for(const f of facts){const row=p.rows.find(x=>x.id===f.id);if(!row)throw Error('Missing row '+f.id);f.source=ref(row.path);if(f.source.sha256!==row.sourceSha256)throw Error('Source changed');f.directClockAndPixelsRead=true;}
const out=b+'part1-capacity-boundary-direct-review-v188.json';if(fs.existsSync(path.join(root,out)))throw Error('Preserve record');
fs.writeFileSync(path.join(root,out),JSON.stringify({schemaVersion:1,reviewedAt:new Date().toISOString(),input:ref(input),browserTabId:'62',mode:'CUA observed native-file clock and displayed pixels; sparse boundaries do not certify every intermediate frame',facts,priorWholeNativeObservation:ref(b+'part1-native-continuous-observations-v169.json'),priorBoundaryReview:ref(b+'part1-boundary-direct-review-v180.json'),original111AndFiveFramingPreserved:true,current37PcmUnchanged:true,noRecognitionOrRenderRepeated:true,allExtendedMotionApproved:false,actualSourceOffsetCertified:false,allFinalPixelsReviewed:false,bodyRatioApproved:false,uploaded:false,next:'Prepare measured source/diagram allocation with current37; directly inspect exact crops and moving rendered cue/cut pixels before approval.'},null,2)+'\n');
console.log(JSON.stringify({observations:facts.length,rejectedPresenterOrCropExtensions:facts.filter(x=>x.extensionRejected).length,finalApproval:false,newImages:0}));
