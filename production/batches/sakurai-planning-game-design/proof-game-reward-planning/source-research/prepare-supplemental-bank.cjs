const fs=require('fs'),path=require('path');
const out=path.join(__dirname,'action-bank-v4.json');
if(fs.existsSync(out))throw Error('Preserve existing bank.');
const initial=JSON.parse(fs.readFileSync(path.join(__dirname,'action-bank-v3.json'),'utf8'));
const acquired=JSON.parse(fs.readFileSync(path.join(__dirname,'acquisition.json'),'utf8')).results.find(s=>s.videoId==='31XzG5PbXCI');
const source={...acquired,fps:30};
const cuts=[
 ['wool-01',300,305,'Player shoots in a snowy enemy arena with projectiles and moving targets.'],
 ['wool-02',308,313,'Player moves and attacks around a large enemy and marked circular area.'],
 ['wool-03',318,322,'Moving character, connected circular ground markings and multiple structures.'],
 ['wool-04',323,331,'Distinct snowy combat shots with projectiles, enemy movement and circular marked zones.'],
 ['wool-05',336,343,'Arena attack action followed by distinct red-environment combat; do not infer earned rewards or progression order.'],
 ['wool-06',350,364,'Multiple red-arena combat attacks, moving targets and hazards.'],
 ['wool-07',365.5,370.5,'Snowy combat with multiple enemies and visible attacks; ends before dialogue.']
 ].map(([id,a,z,action])=>({id,sourceId:source.videoId,sourceInSeconds:a,sourceOutSeconds:z,durationSeconds:z-a,group:'review-contexts',visibleAction:action,focus:'Which target, environmental situation and overlapping actions would a reward design need to test? This footage does not establish a new reward, acquisition rule or quantitative balance comparison.',speed:1,sourceAudio:'exclude-all',classification:'candidate-existing-game-action',nativeBoundaryReview:'pending',fixedCaptionSafety:'pending-final-cues-and-render',finalApproved:false,intervalApprovedForIndependentPlanning:false}));
fs.writeFileSync(out,JSON.stringify({...initial,createdAt:new Date().toISOString(),status:'supplementary-source-boundary-review-pending',sources:[source],cuts,cutCount:cuts.length,candidateSeconds:cuts.reduce((n,c)=>n+c.durationSeconds,0),sourceIntervalsApproved:false,finalApproval:false},null,2)+'\n');
