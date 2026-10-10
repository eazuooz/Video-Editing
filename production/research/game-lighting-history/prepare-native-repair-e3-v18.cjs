const fs=require('node:fs'),crypto=require('node:crypto');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const prod='projects/game-lighting-history-03/production',ep=prod+'/native-repair-e2-pixel-execution-v18.json';
const x=JSON.parse(fs.readFileSync(ep));
if(x.status!=='complete'||x.exitCode!==0||x.boards.length!==11||x.images.length!==65)throw Error('Incomplete E2');
const notes=[
 'Early light/cube/shadow samples are legible; the later camera change is reviewed separately.',
 'FAIL f19971: the bulb lower stem still meets the fixed caption top. Keep this failure and repair only the hardware input.',
 'Final light samples and start of actual RTXDI city have correct source labels; city title slate is gone.',
 'RTXDI city, moving cars, illuminated windows and roadway match cues174–176. Native promotional footer is excluded.',
 'City movement and signs match cue177; no renderer-internal reservoir measurement is asserted.',
 'Moving city under cues178/179; fixed captions do not hide the relevant scene.',
 'Nearby surfaces and moving camera under cues179/180; native footer excluded and observation limit is labelled.',
 'Street approach matches cues181/182; hidden sampling choice is explicitly explained as absent from the source.',
 'Separate city interval under cue199, with illuminated pavement and signage; algorithm versus image filtering remains distinct.',
 'City motion under cues200/201 remains clear with fixed captions.',
 'Last cue202 and exact final boundaries retain city imagery and exclude promotional strip.'
];
const records=x.boards.map((b,i)=>{if(sha(b.path)!==b.sha256)throw Error('Changed board');const images=b.imageIndices.map(n=>x.images[n-1]);for(const q of images)if(sha(q.path)!==q.sha256)throw Error('Changed image');return {...b,directlyRead:true,images,observation:notes[i]};});
const rp=prod+'/native-repair-e2-direct-review-v18.json';if(fs.existsSync(rp))throw Error('Preserve review');
fs.writeFileSync(rp,JSON.stringify({recordedAt:new Date().toISOString(),execution:{path:ep,sha256:sha(ep)},boardsDirectlyRead:11,imagesDirectlyRead:65,records,allChangedSampleBoardsRead:true,sourceLabelCaptionClearanceApproved:false,changedSampleSemanticApproval:false,acceptedSampleInputs:['original-43-01-repair-e2','12-rtxdi-boulevard-01-repair-e2','original-49-01-repair-e2'],unresolved:[{input:'03-ray-shadow-02-repair-e2',frame:19971,issue:'Bulb lower stem still overlaps fixed caption edge during original camera change.'}],allFinalPixelsReviewed:false,fullAnimatedPlaybackReviewed:false,qaApproved:false,collected:false,uploaded:false,newGitImages:0},null,2)+'\n');
const old=JSON.parse(fs.readFileSync(prod+'/native-repair-e2-plan-v18.json')),c={...old.cuts[0]};
c.id='03-ray-shadow-02-repair-e3';c.replacesInputIds=[old.cuts[0].id];c.crop=[320,300,1152,648];c.dynamicCropY='300+120*clip((n-250)/60,0,1)';c.output='production/research/game-lighting-history/local/native-repair-e3-v18/'+c.id+'.mp4';
const p=prod+'/native-repair-e3-plan-v18.json';if(fs.existsSync(p))throw Error('Preserve plan');
fs.writeFileSync(p,JSON.stringify({...old,preparedAt:new Date().toISOString(),cuts:[c],history:{path:rp,sha256:sha(rp)},observations:[{scope:c.id,reason:'Keep the same six seconds at native speed. A smooth crop follows the original downward camera change so the actual bulb, stem and wall shadow stay above the fixed caption. No synthetic light, source pixel repainting or audio change. Final encoded samples and full motion must be read before use.',crop:c.crop,dynamicCropY:c.dynamicCropY}],allFinalPixelsReviewed:false},null,2)+'\n');
const cp='production/research/game-lighting-history/checkpoint.json',q=JSON.parse(fs.readFileSync(cp));q.episode03NativeE2DirectReview={path:rp,sha256:sha(rp),boards:11,images:65,acceptedSampleInputs:3,unresolved:1,changedSampleSemanticApproval:false,allFinalPixelsReviewed:false};q.episode03NativeE3RepairPlan={path:p,sha256:sha(p),cuts:1,frames:360,allFinalPixelsReviewed:false};q.updatedAt=new Date().toISOString();fs.writeFileSync(cp,JSON.stringify(q,null,2)+'\n');
console.log(JSON.stringify({boardsRead:11,imagesRead:65,acceptedRtxdiInputs:3,remainingHardwareInputs:1,newFrames:360,finalApproval:false}));
