const fs=require('fs'),path=require('path'),crypto=require('crypto');
const base=__dirname;
const read=p=>JSON.parse(fs.readFileSync(path.join(base,p),'utf8'));
const write=(p,x)=>fs.writeFileSync(path.join(base,p),JSON.stringify(x,null,2)+'\n');
if(fs.existsSync(path.join(base,'action-bank-v8.json')))throw Error('Preserve changed-boundary inspection.');
const b=read('action-bank-v7.json'),idx=read('frames/native-bank-v7/index.json');
const review={schemaVersion:1,reviewedAt:new Date().toISOString(),framesDirectlyRead:133,uniqueFramesDirectlyRead:132,sheetsDirectlyRead:idx.sheets,accepted:b.cuts.filter(c=>!['wool-07','appearance-01'].includes(c.id)).map(c=>c.id),corrections:[
 {id:'wool-03',reason:'The shot is snowy combat around red ground markings with a camera zoom, not a red arena. Through320.966667 remains actual action; the321.2 edit observed in v6 is excluded.'},
 {id:'wool-07',sourceOutSeconds:370.5,reason:'Extended inspection shows a noncombat dialogue setup already at370.533333 and explicit dialogue by371.066667. Revert the unapproved extension; retain reviewed original366–370.5 combat.'},
 {id:'appearance-01',sourceOutSeconds:31+1/30,reason:'Source frame31.0 still shows changing mask preview; frame31.066667 is already Sewing Mechana. End exclusive31.033333 so final source frame is the directly read31.0.'}
],finalApproval:false,fixedCaptionSafety:'pending-final-cues-and-render'};
write('direct-supplemental-review-v7.json',review);
const previous=read('action-bank-v6.json');
const c=previous.cuts.find(c=>c.id==='wool-02');
const v8={...previous,createdAt:new Date().toISOString(),previousBank:'action-bank-v7.json',status:'additional-adjacent-action-awaiting-direct-review',cuts:[{...c,previousInterval:{in:c.sourceInSeconds,out:c.sourceOutSeconds},sourceInSeconds:305,sourceOutSeconds:312.3,durationSeconds:7.3,revisionReason:'Inspect additional adjacent genuine combat instead of extending into dialogue or shortening explanations.',nativeBoundaryReview:'pending-v8-direct-review'}],cutCount:1,candidateSeconds:7.3,sourceIntervalsApproved:false,finalApproval:false};
write('action-bank-v8.json',v8);console.log(JSON.stringify({framesReviewed:133,acceptedChangedBoundaries:review.accepted.length,extensionRejected:true,nextCuts:1}));
