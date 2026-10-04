const fs=require('fs'),path=require('path');
const file=path.join(__dirname,'request-customization.json');if(fs.existsSync(file))throw Error('Preserve prior source request.');
const request=JSON.parse(fs.readFileSync(path.join(__dirname,'request-targeted.json'),'utf8'));
request.createdAt=new Date().toISOString();request.purpose='Supplement the reviewed functional/action bank with actual outfit selection, differentiated combat actions or base production. Preserve useful explanation; do not fill a duration deficit with animation or repeated cuts. A scaffold exists, but no independent narration/TTS has been created.';
request.permission.publisherResourcePage='https://influencers.devolverdigital.com/cult-of-the-lamb';
request.sources=[{videoId:'dsCUA_VQ5Nw',url:'https://www.youtube.com/watch?v=dsCUA_VQ5Nw',expectedChannels:['Massive Monster'],game:'Cult of the Lamb',observedVersion:'Sins of the Flesh official developer launch trailer; actual watch page KST2024-01-17. The expanded description identifies Tailor/outfits and other game systems, but exact source action must be reviewed before narration.',status:'candidate-needs-direct-action-review',potentialFit:'Actual outfit selection/changes and distinct production or combat actions. No cosmetic-only statistics or acquisition rules are inferred from the trailer title.'}];
request.sourceDiscoveryEvidence='production/batches/sakurai-planning-game-design/proof-game-reward-planning/cult-sins-flesh-official-source.ax.txt';
fs.writeFileSync(file,JSON.stringify(request,null,2)+'\n');
