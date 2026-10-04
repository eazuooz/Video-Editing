const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'../../..'),base=path.join(root,'production/batches/sakurai-planning-game-design/proof-game-reward-planning/source-research');
const target=path.join(base,'action-bank-v11.json');
if(fs.existsSync(target))throw Error('Preserve existing inspection');
const original=JSON.parse(fs.readFileSync(path.join(base,'action-bank-planning-v2.json'),'utf8'));
fs.writeFileSync(target,JSON.stringify({schemaVersion:1,status:'native-boundary-candidate',createdAt:new Date().toISOString(),sources:original.sources.filter(s=>s.videoId==='mRkJ2uWFWYw'),cuts:[{id:'improved-combat-01',sourceId:'mRkJ2uWFWYw',scriptScene:'10',sourceInSeconds:45.9,sourceOutSeconds:49.3,durationSeconds:3.4,visibleAction:'Boss movement, projectile effects, impact and dropped-item prompts; no inference about normal reward cost or costume statistics.',classification:'unreviewed-candidate',speed:1,sourceAudio:'exclude-all',finalApproved:false}],finalApproval:false},null,2)+'\n');
