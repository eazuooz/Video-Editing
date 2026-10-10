// Consolidate reviewed repairs without changing a narration sample or frame allocation.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),prod='projects/game-lighting-history-03/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const out=prod+'current-input-plan-v19.json';
if(fs.existsSync(path.join(root,out)))throw Error('Preserve existing current input plan');
const baseline=prod+'review-input-plan-v15.json',base=read(baseline);let inputs=structuredClone(base.inputs);const history=[];
function replace(cuts,label){
 const sorted=[...cuts].sort((a,b)=>a.fromFrame-b.fromFrame);const regions=[];
 for(const c of sorted){if(c.toFrame-c.fromFrame!==c.frames)throw Error('Repair frame mismatch');let r=regions.at(-1);if(r&&r.end===c.fromFrame){r.end=c.toFrame;r.cuts.push(c);}else regions.push({start:c.fromFrame,end:c.toFrame,cuts:[c]});}
 for(const r of regions){const old=inputs.filter(x=>x.fromFrame<r.end&&x.toFrame>r.start);
  if(!old.length||old[0].fromFrame!==r.start||old.at(-1).toFrame!==r.end||old.reduce((a,x)=>a+x.frames,0)!==r.end-r.start)throw Error('Partial replacement/gap '+label+' '+r.start);
  if(old.some(x=>x.kind!==r.cuts[0].kind))throw Error('Screen role changed '+label);
  inputs=inputs.filter(x=>!old.includes(x)).concat(r.cuts).sort((a,b)=>a.fromFrame-b.fromFrame);
  history.push({label,fromFrame:r.start,toFrame:r.end,retiredInputIds:old.map(x=>x.id),currentInputIds:r.cuts.map(x=>x.id),frameAllocationUnchanged:true});
 }
}
const native=['native-repair-a-plan-v18.json','native-repair-b-plan-v18.json','native-repair-c-plan-v18.json','native-repair-d-resolved-inputs-v18.json','native-repair-e-resolved-inputs-v18.json','native-repair-f-plan-v18.json'];
for(const n of native)replace(read(prod+n).cuts.map(x=>({...x,kind:'actual-review-input',verification:x.output.replace(/\.mp4$/,'.verification.json')})),n);
const boundary='explanation-boundary-repair-plan-v18.json';
replace(read(prod+boundary).cuts.map(x=>({...x,verification:x.output.replace(/\.mp4$/,'.verification.json')})),boundary);
const clearance='caption-clearance-repair-plan-v3.json',c=read(prod+clearance);
replace(c.clips.map(x=>({id:x.id,kind:'explanation-review-input',scene:x.scene,fromFrame:x.fromFrame,toFrame:x.toFrame,frames:x.frames,
 output:'production/research/game-lighting-history/local/explanation-clearance-inputs-v19/'+x.id+'.mp4',
 verification:'production/research/game-lighting-history/local/explanation-clearance-inputs-v19/'+x.id+'.verification.json',
 source:c.output,sourceFromFrame:x.repairFromFrame,sourceToFrame:x.repairToFrame,modelShiftY:x.modelShiftY,
 sourceAggregateVerification:c.output.replace(/\.mp4$/,'.verification.json'),allPixelsReviewed:false})),clearance);
if(inputs.some((x,i)=>x.fromFrame!==(i?inputs[i-1].toFrame:0)||x.toFrame-x.fromFrame!==x.frames)||inputs.at(-1).toFrame!==base.totals.finalFrames)throw Error('Final continuity');
const actual=inputs.filter(x=>x.kind==='actual-review-input').reduce((s,x)=>s+x.frames,0),explanation=inputs.filter(x=>x.kind==='explanation-review-input').reduce((s,x)=>s+x.frames,0);
if(actual!==55418||explanation!==36946||Math.abs(actual-(actual+explanation)*.6)>1)throw Error('Body ratio changed');
const references=[baseline,...native.map(x=>prod+x),prod+boundary,prod+clearance];
const record={preparedAt:new Date().toISOString(),status:'consolidated-inputs-awaiting-17-extractions-and-moving-annotations',references:references.map(p=>({path:p,sha256:sha(p)})),inputs,history,totals:base.totals,actualFrames:actual,explanationFrames:explanation,finalSeconds:base.finalSeconds,
 unchangedMeasuredNarrationPlan:{path:prod+'measured-native-timeline-candidate-v15.json',sha256:sha(prod+'measured-native-timeline-candidate-v15.json')},
 fixedCaptionsUnchanged:true,pcmUnchanged:true,chaptersUnchanged:true,rateChanges:0,loops:0,sourceAudio:0,cpuThreads:2,gpuJobs:0,
 allInputPixelsReviewed:false,allMovingPixelsReviewed:false,allFinalPixelsReviewed:false,qaApproved:false,collected:false,uploaded:false,newGitImages:0};
fs.writeFileSync(path.join(root,out),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({inputs:inputs.length,actualFrames:actual,explanationFrames:explanation,finalFrames:base.totals.finalFrames,explanationExtractions:17,mediaCreated:0,finalApproved:false}));
