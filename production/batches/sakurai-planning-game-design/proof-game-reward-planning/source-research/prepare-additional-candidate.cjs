const fs=require('node:fs');const path=require('node:path');
const request=JSON.parse(fs.readFileSync(path.join(__dirname,'request.json'),'utf8'));
request.createdAt=new Date().toISOString();
request.purpose='Supplement the directly inspected but short/edited Cult of the Lamb source bank with official crafting and weapon/customization actions. Existing raw downloads and completed decodes remain preserved.';
request.sources=[{videoId:'n8wJDqZanbM',url:'https://www.youtube.com/watch?v=n8wJDqZanbM',expectedChannels:['DevolverDigital'],game:'Wizard with a Gun',observedVersion:'Official Gameplay Overview | Single Player Demo on Steam, published June 2023. Do not present preview footage as evidence of later balance/build.',status:'candidate-needs-direct-action-review',potentialFit:'Scan/research, elemental ammunition, crafting and equipment choices if established by actual actions; source animation, title screens and diagram-like overviews excluded from actual-game quota.'}];
request.permission.publisherResourcePage='https://influencers.devolverdigital.com/wizard-with-a-gun';
request.permission.actualEvidence.push('production/batches/sakurai-planning-game-design/proof-game-reward-planning/wizard-creator-license-link.ax.txt');
fs.writeFileSync(path.join(__dirname,'request-additional.json'),JSON.stringify(request,null,2)+'\n');console.log(request.sources[0].videoId);
