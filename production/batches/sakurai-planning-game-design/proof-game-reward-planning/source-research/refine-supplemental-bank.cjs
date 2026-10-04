const fs=require('fs'),path=require('path');
const out=path.join(__dirname,'action-bank-v5.json');
if(fs.existsSync(out))throw Error('Preserve completed extraction and bank history.');
const old=JSON.parse(fs.readFileSync(path.join(__dirname,'action-bank-v4.json'),'utf8'));
const definitions=[
 ['wool-01',300,304.5,'End before the dialogue inserted into the former last frame.'],
 ['wool-02',308.8,312.3,'Start after dialogue and end before the next edited combat shot.'],
 ['wool-03',318,322,'Keep the distinct red marked arena and moving targets.'],
 ['wool-04',323,325.5,'Keep active attacks; remove later idle travel and repeated boss montage.'],
 ['wool-06-brick',354.5,357,'Keep the brick-floor enemy arena between presenter cuts; exclude fire shots potentially repeated elsewhere.'],
 ['wool-07',365.5,370.5,'Keep the distinct snowy arena attacks before later dialogue.']
 ];
const cuts=definitions.map(([id,a,z,reason])=>{const original=old.cuts.find(c=>c.id===(id==='wool-06-brick'?'wool-06':id));return {...original,id,sourceInSeconds:a,sourceOutSeconds:z,durationSeconds:z-a,visibleAction:id==='wool-06-brick'?'Player attacks a large enemy on a brick-floor arena with visible ground markings.':original.visibleAction,revisionReason:reason,nativeBoundaryReview:'pending-v5-direct-review',intervalApprovedForIndependentPlanning:false,finalApproved:false};});
const record={schemaVersion:1,createdAt:new Date().toISOString(),status:'revised-supplemental-bank-boundary-review-pending',sources:old.sources,cuts,cutCount:cuts.length,candidateSeconds:cuts.reduce((n,c)=>n+c.durationSeconds,0),previousBank:'action-bank-v4.json',rejectedInternalRanges:[{cut:'wool-01',range:[304.5,305],reason:'Dialogue boundary'},{cut:'wool-02',range:[308,308.8],reason:'Dialogue before attack'},{cut:'wool-04',range:[325.5,331],reason:'Quiet travel and likely repeated underlying boss shot'},{cut:'wool-05',range:[336,343],reason:'Presenter interruption and fire/boss shots potentially repeated in the source montage; not needed'},{cut:'wool-06',range:[350,354.5],reason:'Presenter and potentially repeated fire shot'},{cut:'wool-06',range:[357,364],reason:'Presenter/dialogue interruptions and potentially repeated fire combat'}],sourceIntervalsApproved:false,sourceAudioForFinal:'exclude-all',agentCreatedGames:0,finalApproval:false};
fs.writeFileSync(out,JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({cuts:cuts.length,seconds:record.candidateSeconds}));
