const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'../../..'),base=path.join(root,'production/batches/sakurai-planning-game-design/proof-game-reward-planning/source-research');
const target=path.join(base,'action-bank-v9.json');
if(fs.existsSync(target))throw Error('Preserve existing inspection');
const original=JSON.parse(fs.readFileSync(path.join(base,'action-bank-planning-v2.json'),'utf8'));
const intervals=[['appearance-before',24,27],['appearance-after',45.75,49.5]];
const cuts=intervals.map(([id,a,z])=>({id,sourceId:'mRkJ2uWFWYw',scriptScene:'08',sourceInSeconds:a,sourceOutSeconds:z,durationSeconds:z-a,visibleAction:'Candidate adjacent customization or differently dressed character movement; inspect before classifying.',classification:'unreviewed-candidate',speed:1,sourceAudio:'exclude-all',finalApproved:false}));
fs.writeFileSync(target,JSON.stringify({schemaVersion:1,status:'unreviewed-adjacent-action-candidates',createdAt:new Date().toISOString(),sources:original.sources.filter(s=>s.videoId==='mRkJ2uWFWYw'),cuts,reason:'Current29.28s action narration exceeds28.283333s bank before the approved gap. Seek new relevant actions; never extend held Sewing Mechana or replay existing footage.',finalApproval:false},null,2)+'\n');
