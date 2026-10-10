const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='production/research/game-lighting-history',project='projects/game-lighting-history-03';
const sha=x=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,x))).digest('hex');
const input=base+'/local/native-action-support-v14-ddgi-action-gaps/execution.json',a=JSON.parse(fs.readFileSync(path.join(root,input),'utf8'));
const out=project+'/production/native-ddgi-action-gap-direct-review-v14.json';
if(fs.existsSync(path.join(root,out)))throw Error('Preserve completed review');
if(a.status!=='action-sequences-ready')throw Error('Completed extraction required');
const notes=[
 '5–10 RAY-TRACED REFLECTIONS OFF/ON and water/gem/camera;11 transition;12–13 altar starts RTX GLOBAL ILLUMINATION label. Do not treat the reflection toggle as isolated GI.',
 '14–16 RTX GLOBAL ILLUMINATION OFF altar;17 RTX ON altar;18 transition to orange chamber;19–22 RAY-TRACED SHADOWS+REFLECTIONS OFF/ON. Only12–18 is the explicitly labeled GI comparison.',
 '23–26 exterior/gem view;27–31 active player movement and platform/lava actions with RTX ON. The action is a game appearance example, not an isolated DDGI latency or light-leak measurement.',
 '32–37 active traversal, hand/attack and enemies in orange/green rooms, RTX ON. No probe interpolation or update timing is visible.',
 '313–314 nearly unchanged probe/blue-box view;315–317 camera reframes the box and neighboring green wall. Exclude the initial hold if more duration is unnecessary.'
];
let i=0;const reviewed=a.completed.map(r=>({...r,boards:r.boards.map(b=>{
 if(sha(b.path)!==b.sha256)throw Error('Changed board');for(const s of b.samples)if(sha(s.path)!==s.sha256)throw Error('Changed sample');
 return {...b,directlyViewed:true,note:notes[i++]};
})}));if(i!==notes.length)throw Error('Direct count mismatch');
const record={schemaVersion:1,reviewedAt:new Date().toISOString(),input:{path:input,sha256:sha(input)},reviewed,
 boardCount:5,temporalSampleCount:38,allBoardsDirectlyViewed:true,allTemporalSamplesDirectlyViewed:true,
 primaryContentVerification:{url:'https://developer.nvidia.com/blog/?p=35425',publicationDate:'2021-07-29',directArticleRead:true,
  finding:'NVIDIA reports Escape from Naraka uses UE4/NvRTX, RTXGI/DDGI volumes, ray-traced reflection/shadow and DLSS. The article identifies these features separately; its promotional performance language is not our benchmark.',
  shortSourceStatement:'The developer reports placing a Dynamic Diffuse Global Illumination volume during lighting setup; the trailer result does not expose the internal interpolation.'},
 candidateRanges:[{source:'escape-naraka-rtxgi-2021',ranges:[[12,18],[27,37]],role:'GI-labeled comparison then separate gameplay appearance; no probe/latency inference'},
  {source:'rtxgi-ue5-preview2-2022',ranges:[[315,322]],role:'Unique probe/blue-box camera continuation including priorv13 samples'}],
 fullContinuousMotionReviewed:false,finalUseApproved:false,allFinalCaptionPixelsReviewed:false,rightsApproved:false,sourceAudioUsed:false,newGitRasterCount:0,localOnly:true};
fs.writeFileSync(path.join(root,out),JSON.stringify(record,null,2)+'\n');
const cp=path.join(root,base,'checkpoint.json'),c=JSON.parse(fs.readFileSync(cp,'utf8'));c.updatedAt=new Date().toISOString();
c.episode03NativeActionGapReview={path:out,sha256:sha(out),boards:5,temporalSamples:38,allBoardsDirectlyViewed:true,fullContinuousMotionReviewed:false,finalUseApproved:false};
c.episode03RuntimeV7Preparation={path:project+'/production/spatial-runtime-adoption-preparation-v7.json',sha256:sha(project+'/production/spatial-runtime-adoption-preparation-v7.json'),finalTimelineAdopted:false,finalPixelsApproved:false,
 typecheck:{command:'node node_modules/typescript/bin/tsc --noEmit --pretty false',cwd:'D:/Github/Video-Editing/motion-canvas',exitCode:1,ownNewErrors:0,limitation:'Seven preserved foreign paper-scene Expected1argument0 errors. Whole repository pass not claimed.'}};
fs.writeFileSync(cp,JSON.stringify(c,null,2)+'\n');
console.log(JSON.stringify({review:out,boards:5,samples:38,originalPcmChanged:false,finalUseApproved:false}));
