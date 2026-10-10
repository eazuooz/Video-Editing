const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='production/research/game-lighting-history',p='projects/game-lighting-history-03',read=x=>JSON.parse(fs.readFileSync(path.join(root,x),'utf8')),sha=x=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,x))).digest('hex');
const input=b+'/local/native-action-v11-lumen/execution.json',a=read(input);if(a.status!=='action-sequences-ready'||a.completed.reduce((n,r)=>n+r.frames,0)!==256)throw Error('Completed actual sequence required');
const notes=[
 ['230–238 lit rocks and gizmos, Show/Visualize menu then MeshDistanceFields selection and blue-gray geometric representation.'],
 ['239–246 MeshDistanceFields camera passes rocks/stairs; geometry is rounded/simple relative to material view.'],
 ['247–256 briefly lit then MeshDistanceFields again; stairs, narrow gaps and stones change with camera.'],
 ['257–265 distance-field camera, lit return261s then gray262–263 and menus264s.'],
 ['266–274 gray camera and checked MeshDistanceFields270s; GlobalDistanceField selected272s, coarser gray representation273–274s. Do not label the latter MeshDistanceFields.'],
 ['275–281 GlobalDistanceField camera samples, distinct representation; excluded from the MeshDistanceFields-only guide.'],
 ['388–396 warm cave turns blue-gray/dark390s; camera changes after393s, so no fixed-camera numerical A/B.'],
 ['397–405 camera towards opening then warm401–402s, close cave406s forthcoming; visible transition, not measured latency.'],
 ['406–414 cave camera then Show LightingFeatures menu410–412s, gray/dark413–414s. Native menu label lies below selected viewport crop.'],
 ['415–423 blue-gray camera and Show menu419–421s then warm421–423s. Hovered IndirectLightingCache/CapsuleShadows is not evidence of a specific clicked feature.'],
 ['424–432 moving close view of stone/wood/scaffold followed by near-hold431–432s.'],
 ['433–441 short hold then camera travels through stalactites and rock opening.'],
 ['442–450 mostly similar cave framing, small oscillations. Reject prolonged near-holds as quota padding.'],
 ['451–459 similar cave framing until active movement457–459s; exclude451–456s extended near-hold.'],
 ['460–468 active camera around opening and scaffold; warm stone lighting.'],
 ['469–477 warm to purple471s, camera scans opening and stone. Color edit controls must be read separately in raw/right view.'],
 ['478–486 purple cave and stalactites; camera pans and moves, not an exposure-locked experiment.'],
 ['487–495 near-hold487–489s then green490–491s, orange492s, pink493s, purple with camera494–495s.'],
 ['496–504 purple to orange497–498s, camera travels past opening and stalactites.'],
 ['505–513 orange cave camera then near-hold511–513s.'],
 ['514–522 camera changes distance and direction among hanging formations, wood scaffold and arch.'],
 ['523–527 quick movement523s and opening near-hold524–527s; do not use tail to pad.'],
 ['656–657 full presenter panel: exclude both seconds.658 hallway then659–664 camera into bright living room/sofa/windows.'],
 ['665–669 bright room then Show LightingFeatures.670–671 menu selection makes interior dark. Native raw670s directly read separately: highlighted Lumen GlobalIllumination.672–673 dark camera towards window.'],
 ['674–679 dark interior, sunlit curtains/windows and table, camera movement.680–682 Show menus reopen; feature label below viewport crop.'],
 ['683–684 dark to bright transition684s.685–686 camera returns to sofa;687–691 slow pan/near-hold. Raw menu must distinguish actual toggled feature.'],
 ['692–700 bright wall/sofa/windows/ceiling with small camera adjustments, including ceiling tilt.'],
 ['701–709 similar bright sofa view; near-holds702–704s/707–708s excluded from padding.'],
 ['710–718 camera into hallway by painting, vase, door, windows then dining area.'],
 ['719 bright dining room continuation; source EOF not reached in this reviewed range.']
].map(x=>x[0]);
let i=0;const reviewed=a.completed.map(r=>({...r,boards:r.boards.map(board=>{if(sha(board.path)!==board.sha256)throw Error('Board changed');for(const sample of board.samples)if(sha(sample.path)!==sample.sha256)throw Error('Sample changed');return{...board,directlyViewed:true,note:notes[i++]};})}));if(i!==30||notes.length!==30)throw Error('Exact direct review count');
const output=p+'/production/native-lumen-action-direct-review-v11.json';if(fs.existsSync(path.join(root,output)))throw Error('Preserve prior review');
const record={schemaVersion:1,reviewedAt:new Date().toISOString(),input:{path:input,sha256:sha(input)},sourceSha256:a.completed[0].sourceSha256,reviewed,all30BoardsDirectlyViewed:true,all256TemporalSamplesDirectlyViewed:true,method:'Direct inspection of every1fps sample/contact board. Nominal nearby decoded timestamps guide selection; exact final frame cuts and continuous final motion/caption review are separate.',rawMenuDirectObservation:{source:'lumen-content-examples-2021',localSeconds:670,via:'CUA local native-motion-review-v5 raw frame',feature:'Show/LightingFeatures/Lumen GlobalIllumination highlighted',presenterOverlaid:true,fullRawMustNotBecomeFinalUse:true},recommendedNonFinalRanges:{meshDistanceFields:[[235,247],[249,261],[262,271]],globalDistanceField:[[272,282]],lightColorEdit:[[469,499]],interiorToggle:[[665,687]],interiorCamera:[[658,665],[671,680],[685,702],[710,720]]},exclude:[{from:656,to:658,reason:'Full presenters'},{from:442,to:457,reason:'Prolonged similar/near-static cave view; no quota padding'},{from:523,to:528,reason:'Short movement followed by near-static tail; no quota padding'}],sourceAudioUsed:false,newGitRasterCount:0,localOnly:true,continuousFullMotionReviewed:false,finalUseApproved:false,allFinalCaptionPixelsReviewed:false,rightsApproved:false,next:'Refine exact native interval/crop/narration linkage; preserve MeshDistanceFields versus GlobalDistanceField distinction. Final cuts at actual integer frames after guidePCM measurement, with fixed bottom captions.'};
fs.writeFileSync(path.join(root,output),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({output,boards:i,frames:256,finalUseApproved:false}));
