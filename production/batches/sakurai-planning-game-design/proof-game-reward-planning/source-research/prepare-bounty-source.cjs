const fs=require('fs'),path=require('path');
const target=path.join(__dirname,'request-bounty.json');
if(fs.existsSync(target))throw Error('Preserve existing request/acquisition.');
const request=JSON.parse(fs.readFileSync(path.join(__dirname,'request-targeted.json'),'utf8'));
request.createdAt=new Date().toISOString();
request.purpose='Preserve seven measured explanation/overview PCM files totaling162seconds. Obtain fresh official prerequisite/reward/weapon actions to expand actual examples and support measured60:40; source intervals must be inspected before corresponding new commentary.';
request.sources=[{videoId:'-jkxOq-vyu4',url:'https://www.youtube.com/watch?v=-jkxOq-vyu4',expectedChannels:['DevolverDigital'],game:'Wizard with a Gun',observedVersion:'Bounty of Guns Update | Out Now; actual expanded official watch page2024-03-05',status:'candidate-needs-direct-action-review',potentialFit:'Official description explains bounty acceptance, enemy defeat, reward claim and new weapon types. Direct video inspection must separate gameplay actions from title/menu/animation and cannot assume the edit proves normal prerequisites or every reward.'}];
request.sourceDiscoveryEvidence='production/batches/sakurai-planning-game-design/proof-game-reward-planning/wizard-bounty-official-source.ax.txt';
fs.writeFileSync(target,JSON.stringify(request,null,2)+'\n');
