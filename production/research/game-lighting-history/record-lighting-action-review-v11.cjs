const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='production/research/game-lighting-history',p='projects/game-lighting-history-03',read=x=>JSON.parse(fs.readFileSync(path.join(root,x),'utf8')),sha=x=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,x))).digest('hex');
const input=b+'/local/native-action-v11-lighting/execution.json',a=read(input);if(a.status!=='action-sequences-ready'||a.completed.reduce((n,r)=>n+r.frames,0)!==325)throw Error('Completed actual sequence required');
const notes=[
 '205–211 selected volume/gizmo, small UI/camera changes;212–213 bounds grow taller/larger and left-room illumination changes.',
 '214–219 camera orbits from frontal to side;220–222 similar view/slight orbit.',
 '223–225 near-hold;226–227 properties edited;228 bounds widen towards right box;229–231 transforms move and right interior becomes illuminated.',
 '232 similar view;233 enlarged bounds/right-room light;234–240 closer frontal camera then wider view.',
 '241–243 sphere shading/color changes;244 camera;245–249 near-hold.',
 '250–257 near-hold with property scrolling;258 probe visualization appears.',
 '259–262 camera around probes;263–267 similar view/property changes.',
 '268–276 mostly static probes and UI fields/tooltips. Do not pad with this hold.',
 '277–278 hold;279–285 camera approaches left room/sphere through visible probes.',
 '286–288 camera pulls back;289 similar view;290–291 camera;292–294 property UI/similar view.',
 '295–297 similar view;298–300 grid spacing/count visibly changes to fewer probes;301 front view;302–303 near-hold.',
 '304–309 front-view hold;310 camera;311–312 blue-lit right-room close view.',
 '313–317 blue-lit right-room hold. No independent action in tail.',
 '363–365 static native label64x64x4=16384, a demonstration-specific limit;366–371 camera retreats/rotates to wide city/probe view.',
 '372–380 static wide city/probe lattice. Reject prolonged hold.',
 '381–389 static city/probe lattice and properties. Reject prolonged hold.',
 '390–398 static city/probe lattice. Reject prolonged hold.',
 '399–401 static grid;402 probes off;403–405 same city;406–407 play-in-editor dark city. Exact native control activation needs continuous/raw review.',
 '408–413 bright city;camera/light changes around411. Native DDGI/visualize/light-animation buttons visible, but samples alone do not isolate which setting caused transition.',
 '155–163 almost static blue cube/point-light view with property scrolling160–162.',
 '164–167 static properties;168–171 ray-traced-shadow dropdown/tooltip interaction, wall/floor shadow changes171.',
 '173–175 camera changes towards frontal cube;176–180 light SourceRadius properties edited;179–180 softer wall-edge appearance;181 closer camera. Not controlled fixed-camera measurement.',
 '182–184 closer cube/wall/light;185 similar;186 radius field edited/shadow appearance changes;187–189 similar view;190 retreating camera.',
 '191–199 almost unchanged frontal cube/properties. Reject prolonged hold.',
 '200 large wall shadow then201 triangular wall shadow/second light icon;202–206 similar view/UI scroll;207–208 CastRayTracedShadows dropdown. Exact second-light interaction requires continuous review.',
 '209–210 similar view/properties;211–212 camera approaches cube;213–215 properties/similar close view.',
 '173–175 static editor overview;176 play-in-editor;177–178 similar close view;179–181 camera approaches reflective sphere with DLSS Auto UI.',
 '182 same view;183 upscaling menu;184–186 Built-in/TAA;187–189 DLSS Auto and developer-stats checkbox;190 native DLSS stats appear.',
 '191 Quality camera shift;192 similar;193–194 mode menu;195–196 Performance;197 UltraPerformance;198–199 sharpness field changes. Native percentages are source configuration, not our benchmark.',
 '200 Quality;201 sharpness;202–203 menus/Built-in;204–208 TAA menu remains open. Trim prolonged hover.',
 '209–213 prolonged TAA menu hover;214 DLAA selected;215–217 DLAA similar view.',
 '218–226 static DLAA sphere view. Reject prolonged hold.',
 '227–235 static DLAA sphere view. Reject prolonged hold.',
 '236–240 static DLAA view;241 camera movement;242–244 similar view. Retain brief label then camera only.',
 '245–252 DLAA similar view;253 DLSS Auto returns. Reject lengthy preceding hold.',
 '254–256 upscaling menu;257 NVIDIA ImageScaling option;258 NIS UltraQuality;259 camera;260 similar;261 camera;262 similar view.',
 '263 NIS UltraQuality;264 Balanced;265–266 menu;267–269 UltraQuality/menu;270 menu;271 Performance.',
 '272 NIS Performance/sharpness0.9. No independent DLSS temporal-algorithm internal visualization.'
];
let i=0;const reviewed=a.completed.map(r=>({...r,boards:r.boards.map(board=>{if(sha(board.path)!==board.sha256)throw Error('Board changed');for(const sample of board.samples)if(sha(sample.path)!==sample.sha256)throw Error('Sample changed');return{...board,directlyViewed:true,note:notes[i++]};})}));if(i!==38||notes.length!==38)throw Error('Exact direct review count');
const output=p+'/production/native-lighting-action-direct-review-v11.json';if(fs.existsSync(path.join(root,output)))throw Error('Preserve prior review');
const record={schemaVersion:1,reviewedAt:new Date().toISOString(),input:{path:input,sha256:sha(input)},reviewed,all38BoardsDirectlyViewed:true,all325TemporalSamplesDirectlyViewed:true,method:'All1fps samples/contact boards directly inspected. Exact final frame cuts, continuous playback and encoded-caption review remain separate.',recommendedNonFinalRanges:{volume:[[205,220],[226,241]],probes:[[258,263],[279,289],[290,292],[298,302],[310,313]],city:[[366,372],[402,414]],rayShadow:[[168,191],[200,202],[207,213]],dlssModes:[[179,192],[193,203],[213,218],[240,242],[253,260],[261,273]]},excludeNearHolds:{volume:[[245,258],[263,279],[302,310],[313,318]],city:[[372,402]],rayShadow:[[155,168],[191,200],[202,207],[213,216]],dlss:[[173,176],[204,213],[218,241],[242,253]]},limits:['DDGI64x64x4=16384 is native demo configuration/limit, not universal performance or our measurement.','City406dark/408bright is not isolated fixed-camera DDGI toggle until exact control/action verification.','DLSS/DLAA/NIS are distinct modes; NIS must not be described as DLSS temporal reconstruction.','No fixed-camera source-radius A/B or internal temporal history/reservoir proof inferred from sample appearance.'],sourceAudioUsed:false,newGitRasterCount:0,localOnly:true,continuousFullMotionReviewed:false,finalUseApproved:false,allFinalCaptionPixelsReviewed:false,rightsApproved:false,next:'Refine exact unique native selections and narrated guides; exclude long holds, verify critical labels/transitions through actual player before TTS approval.'};
fs.writeFileSync(path.join(root,output),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({output,boards:i,frames:325,finalUseApproved:false}));
