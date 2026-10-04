const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'../../..'),base=path.join(root,'production/batches/sakurai-planning-game-design/proof-game-reward-planning/source-research');
const target=path.join(base,'action-bank-v10.json');
if(fs.existsSync(target))throw Error('Preserve existing inspection');
const original=JSON.parse(fs.readFileSync(path.join(base,'action-bank-planning-v2.json'),'utf8'));
fs.writeFileSync(target,JSON.stringify({schemaVersion:1,status:'unreviewed-adjacent-action-candidate',createdAt:new Date().toISOString(),sources:original.sources.filter(s=>s.videoId==='mRkJ2uWFWYw'),cuts:[{id:'appearance-movement-before',sourceId:'mRkJ2uWFWYw',scriptScene:'08',sourceInSeconds:39,sourceOutSeconds:41.7,durationSeconds:2.7,visibleAction:'Inspect character movement before the known differently dressed snowy scene; exclude title/menu/idle.',classification:'unreviewed-candidate',speed:1,sourceAudio:'exclude-all',finalApproved:false}],finalApproval:false},null,2)+'\n');
