const fs=require('fs'),path=require('path');
const target=path.join(__dirname,'request-improved.json');
if(fs.existsSync(target))throw Error('Preserve existing request/acquisition.');
const request=JSON.parse(fs.readFileSync(path.join(__dirname,'request-bounty.json'),'utf8'));
request.createdAt=new Date().toISOString();
request.purpose='Inspect official festive-fashion and simultaneous-station actions as a possible distinction between visible appearance, actual function and production scope. Preserve seven reviewed explanation PCM files. Do not infer cosmetic-only statistics or earned unlock requirements from a promotional update.';
request.sources=[{videoId:'mRkJ2uWFWYw',url:'https://www.youtube.com/watch?v=mRkJ2uWFWYw',expectedChannels:['DevolverDigital'],game:'Wizard with a Gun',observedVersion:'Update1.2 | Improved Wizarding; actual expanded official watch page2023-12-07',status:'candidate-needs-direct-action-review',potentialFit:'Actual outfit selection and multiple wizards using stations, if present in the source. Title cards and long static menus do not fill actual-action time; numerical equality and acquisition rules remain unverified.'}];
request.sourceDiscoveryEvidence='production/batches/sakurai-planning-game-design/proof-game-reward-planning/wizard-improved-official-source.ax.txt';
fs.writeFileSync(target,JSON.stringify(request,null,2)+'\n');
