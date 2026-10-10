const fs=require('node:fs'),crypto=require('node:crypto');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const prod='projects/game-lighting-history-03/production';
const pp=prod+'/native-repair-d-plan-v18.json',ep=prod+'/native-repair-d-pixel-execution-v18.json';
const plan=JSON.parse(fs.readFileSync(pp)),pixels=JSON.parse(fs.readFileSync(ep));
if(pixels.status!=='complete'||pixels.exitCode!==0||pixels.images.length!==124||pixels.boards.length!==21)throw Error('Incomplete D QA');
const observations=[
 'Bicycle and floor camera under cue246; the source label distinguishes geometry selection from shading and source counters remain visible.',
 'Bicycle/floor under cue247; general resource distinction is not labelled as a measured engine-internal budget.',
 'Floor camera under cue248, then the next input starts the relief beside cue249.',
 'Wall relief and foreground occlusion under cue249, cue250 begins with the same relief in view.',
 'Close hand/relief depth under cue250 through f65276; f65277 starts the same ornament in another camera portion.',
 'Normal relief through the early and middle samples of input02 under cue250/251.',
 'FAIL: f65575/f65576 at the end of input02 and f65577 at the start of input03 show a grey diagnostic view. The second-wide historical notes did not prove these exact boundary pixels.',
 'FAIL: f65578 is still grey. Later f65655 onward returns to the lit relief; counters and caption are distinct.',
 'Relief through f65750, doorway begins at exact cue252 f65751, then outdoors rather than an early outdoor transition.',
 'Statue rows and temple camera under cues252/253, then close ornament beside cue254. Native motion blur is preserved.',
 'Lit architecture and close statue under cue254; source counters are visible without interpreting them as our measurements.',
 'Close details end before explanation; the guide16 starts actual Triangles mode under cue262.',
 'Triangles camera then Clusters at f68306. Different camera portions are explicitly identified.',
 'Clusters and architectural edges under cue263; triangle edges and larger colour regions remain distinguishable.',
 'Clusters camera and cue264 explaining diagnostic units rather than material colours.',
 'Clusters end at f68906; the lit material view begins at exact cue265 f68907. White sculpture is foreground geometry against material-coloured architecture.',
 'Lit sculpture camera beside cue265/266, no diagnostic false colours in this interval.',
 'Camera movement and source statistics under cue267; cue268 explicitly does not convert source values to measured memory/frame time.',
 'Lit foreground statue ends before distant temple/city view at f69827 under cue269.',
 'Wide city and temple under cues269/270; projected distance is illustrated without inferred world-space measurements.',
 'Wide city/desert camera through f70501 under cue271, matching distance-dependent representation.'
];
const records=pixels.boards.map((b,i)=>{if(sha(b.path)!==b.sha256)throw Error('Changed board');const images=b.imageIndices.map(n=>pixels.images[n-1]);for(const q of images)if(sha(q.path)!==q.sha256)throw Error('Changed image');return{boardIndex:i+1,path:b.path,sha256:b.sha256,directlyRead:true,imageIndices:b.imageIndices,images,observation:observations[i]};});
const rp=prod+'/native-repair-d-direct-review-v18.json';if(fs.existsSync(rp))throw Error('Preserve review');
fs.writeFileSync(rp,JSON.stringify({recordedAt:new Date().toISOString(),execution:{path:ep,sha256:sha(ep)},boardsDirectlyRead:21,imagesDirectlyRead:124,allChangedSampleBoardsRead:true,sourceLabelCaptionClearanceApproved:true,changedSampleSemanticApproval:false,unresolved:[{id:'nanite-grey-diagnostic-boundary',inputs:['15-nanite-ornament-surface-repair-02','15-nanite-ornament-surface-repair-03'],frames:[65575,65576,65577,65578],replacementPlan:prod+'/native-repair-d2-plan-v18.json'}],records,fullAnimatedPlaybackReviewed:false,allFinalPixelsReviewed:false,qaApproved:false,collected:false,uploaded:false,newGitImages:0},null,2)+'\n');
const cuts=plan.cuts.filter(c=>['15-nanite-ornament-surface-repair-02','15-nanite-ornament-surface-repair-03'].includes(c.id)).map((c,i)=>({...c,id:c.id+'b',sourceFromSeconds:i===0?367.5:374.5,sourceToSeconds:(i===0?367.5:374.5)+c.frames/60,output:'production/research/game-lighting-history/local/native-repair-d2-v18/'+c.id+'b.mp4',replacesInputIds:[c.id]}));
const base=JSON.parse(fs.readFileSync(plan.baseline.path));
const retained=base.inputs.filter(c=>c.source==='nanite-editor-motion-2021'&&!plan.cuts.some(r=>r.replacesInputIds.includes(c.id)));
const ranges=[...retained,...plan.cuts.filter(c=>!cuts.some(r=>r.replacesInputIds.includes(c.id))),...cuts].filter(c=>c.source==='nanite-editor-motion-2021');
for(let i=0;i<ranges.length;i++)for(let j=i+1;j<ranges.length;j++){const a=ranges[i],b=ranges[j];if(Math.min(a.sourceToSeconds,b.sourceToSeconds)-Math.max(a.sourceFromSeconds,b.sourceFromSeconds)>1e-6)throw Error('Source overlap '+a.id+' '+b.id);}
const dest=prod+'/native-repair-d2-plan-v18.json';if(fs.existsSync(dest))throw Error('Preserve plan');
fs.writeFileSync(dest,JSON.stringify({preparedAt:new Date().toISOString(),baseline:plan.baseline,replacesPlan:{path:pp,sha256:sha(pp)},directReview:{path:rp,sha256:sha(rp)},cuts,cpuThreads:2,gpuJobs:0,rateChanges:0,loops:0,sourceAudio:false,unchangedPcm:true,unchangedBodyRatio:true,unchangedChapters:true,sourceOverlapCount:0,observations:[{direct:'CUA exact372.483333 is lit relief; old candidate ending372.85 autopause372.910 was grey and rejected. New input02 uses367.5–372.5, excluding that mode change. Exact374.5 is lit relief;1x374.5–377.4 ends377.427 still showing the relief torso/hand with a bicycle below. Input03 is limited to374.5–377.4.',limits:'Final encoded exact boundaries and continuous playback still require separate review; the source counters are not internal benchmark measurements.'}],sourceMotionApproved:false,allFinalPixelsReviewed:false,fullAnimatedPlaybackReviewed:false,collected:false,uploaded:false,newGitImages:0},null,2)+'\n');
const cp='production/research/game-lighting-history/checkpoint.json',x=JSON.parse(fs.readFileSync(cp));x.episode03NativeDDirectReview={path:rp,sha256:sha(rp),boards:21,images:124,changedSampleSemanticApproval:false,unresolved:1};x.episode03NativeD2RepairPlan={path:dest,sha256:sha(dest),cuts:2,frames:474,allFinalPixelsReviewed:false};x.updatedAt=new Date().toISOString();fs.writeFileSync(cp,JSON.stringify(x,null,2)+'\n');console.log(JSON.stringify({boardsRead:21,imagesRead:124,unresolved:1,repairCuts:2,frames:474,sourceOverlapCount:0,finalApproval:false}));
