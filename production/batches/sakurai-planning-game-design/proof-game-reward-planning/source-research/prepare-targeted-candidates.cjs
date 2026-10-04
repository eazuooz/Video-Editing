const fs=require('node:fs');const path=require('node:path');
const request=JSON.parse(fs.readFileSync(path.join(__dirname,'request-additional.json'),'utf8'));
request.createdAt=new Date().toISOString();
request.purpose='The directly inspected previews contain extensive animation/presenter/title time and brief unrelated cuts. Obtain targeted official ammunition, exploration and real co-op actions rather than looping, slowing or padding the initial bank. No independent script/TTS has been created.';
request.sourceDiscoveryEvidence='production/batches/sakurai-planning-game-design/proof-game-reward-planning/wizard-official-targeted-search.ax.txt';
request.sources=[
  {videoId:'3nIAR1g8RAU',url:'https://www.youtube.com/watch?v=3nIAR1g8RAU',expectedChannels:['DevolverDigital'],game:'Wizard with a Gun',observedVersion:"Gunmancer's Diary: Ammo Craftwork, official pre-launch feature overview",status:'candidate-needs-direct-action-review',potentialFit:'Ammunition research, recipe costs, utility versus damage, and immediate observed effects.'},
  {videoId:'xNUn4fn4br8',url:'https://www.youtube.com/watch?v=xNUn4fn4br8',expectedChannels:['DevolverDigital'],game:'Wizard with a Gun',observedVersion:"Gunmancer's Diary: Exploring the Shatter, official feature overview",status:'candidate-needs-direct-action-review',potentialFit:'Knowledge/access/resource actions, distinguish discovery from power and avoid claiming exact unlock prerequisites not shown.'},
  {videoId:'ZTV0rPQ0_ik',url:'https://www.youtube.com/watch?v=ZTV0rPQ0_ik',expectedChannels:['DevolverDigital'],game:'Wizard with a Gun',observedVersion:'Four-Player Co-Op + More | Out Now, official update overview',status:'candidate-needs-direct-action-review',potentialFit:'Actual loadout effects, collaboration and challenge context. Do not equate a later co-op update feature with an earned reward or infer PvP.'}
];
fs.writeFileSync(path.join(__dirname,'request-targeted.json'),JSON.stringify(request,null,2)+'\n');console.log(JSON.stringify(request.sources.map(x=>x.videoId)));
