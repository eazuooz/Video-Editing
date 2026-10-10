const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),prod='projects/game-lighting-history-03/production';
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const sourcePlan=prod+'/review-input-plan-v15.json',old=JSON.parse(fs.readFileSync(path.join(root,sourcePlan)));
if(sha(sourcePlan)!=='0681e970c71de503a7de24b8172fee209b0c2df2bd70a233859942cdecd14579')throw Error('Baseline changed.');
for(const input of old.inputHashes)if(sha(input.path)!==input.sha256)throw Error('Underlying baseline input changed.');
const bf=old.inputs.find(c=>c.id==='original-17-01'),control=old.inputs.find(c=>c.id==='original-30-01');
const cuts=[
  {...bf,id:'original-17-repair-01',fromFrame:15462,toFrame:15822,frames:360,sourceFromSeconds:12,sourceToSeconds:18},
  {...bf,id:'original-17-repair-02',fromFrame:15822,toFrame:16002,frames:180,sourceFromSeconds:34+16/60,sourceToSeconds:37+16/60},
  {...control,id:'original-30-repair-01',sourceFromSeconds:6,sourceToSeconds:6+847/60,sourceUiLift:{normalizedCrop:[0,850,1920,136],destination:[0,64],label:'원본 비교 표기 · 제작사 제공 수치'}}
];
for(const c of cuts){c.baselineInputId=c.slotId==='original-17'?bf.id:control.id;c.output=`production/research/game-lighting-history/local/native-repair-a-v18/${c.id}.mp4`;delete c.verification;c.sourceMotionApproved=false;c.finalCaptionPixelsApproved=false;c.allPixelsReviewed=false;if(sha(c.media)!==c.sourceSha256)throw Error('Source changed.');}
const observations=[
 {source:bf.source,sourceSha256:bf.sourceSha256,windows:[{start:12,end:18},{start:34+16/60,end:37+16/60}],playback:'CUA local source UI at rate1, full interval controls reached their ends; starts and visible ends directly read.',before:'Red vehicle and wet street; later tank/water scene.',action:'Moving camera crosses reflected vehicle/street surfaces; fire/tank scene and later plane/water are actual source action.',after:'Wet surface reflections remain observable, rather than an opening promotional logo.',rejected:[{start:3,end:12,reason:'Promotional opening does not illustrate the narrated hardware-intersection result.'}],limits:['Official vendor footage illustrates visible reflections; does not measure BVH traversal or prove all ray stages free.','Final burned pixels and narration-aligned annotation remain pending.']},
 {source:control.source,sourceSha256:control.sourceSha256,windows:[{start:6,end:6+847/60}],playback:'CUA rate1 interval 6–20.116667 reached end; frame6 and end20.346055 directly read.',before:'Side-by-side office, character, thin wall directory lettering and desk objects.',action:'The character/camera move through the office; source magnifies fan and fine scene detail.',after:'DLSS original quality versus DLSS2 quality source labels remain actual pixels; candidate lifts the exact mode/conditions strip above the fixed bottom caption region.',rejected:[{start:3,end:6,reason:'Opening logo interferes with actual comparative action.'}],limits:['Vendor conditions/quality modes are retained, not our FPS benchmark.','Source strip lift is a UI-reading aid; final encoded captions/annotations and whole motion remain separate approvals.']}
];
const output=prod+'/native-repair-a-plan-v18.json';if(fs.existsSync(path.join(root,output)))throw Error('Preserve existing repair.');
fs.writeFileSync(path.join(root,output),JSON.stringify({preparedAt:new Date().toISOString(),baseline:{path:sourcePlan,sha256:sha(sourcePlan)},scope:'Three changed local actual inputs only; no final pair adoption.',cuts,observations,unchangedNarration:true,unchangedTiming:true,fixedCaptionPosition:[960,970],rateChanges:0,loops:0,sourceAudio:false,cpuThreads:2,gpuJobs:0,allFinalPixelsReviewed:false,collected:false,uploaded:false},null,2)+'\n');
console.log(JSON.stringify({plan:output,cuts:cuts.length,frames:cuts.reduce((n,c)=>n+c.frames,0),finalApproved:false}));
