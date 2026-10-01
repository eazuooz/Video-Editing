// Run only after direct spare-action and sub-second boundary sheets were read.
const fs=require('node:fs'),crypto=require('node:crypto');
const work='projects/praise-player/production/final-v2',file=work+'/example-map.json';
const map=JSON.parse(fs.readFileSync(file,'utf8'));
if(map.capacityReview)throw Error('Capacity reviewed already; do not reset map');
map.chapters[0].groups[0].windows=[['sports',90.7,105.75],['sports',199.8,201.95]];
map.chapters[0].groups[2].windows.find(w=>w[0]==='sports')[2]=275.6;
map.chapters[2].groups[2].windows.push(['hifi-remix',109.5,115.8]);
const gate=map.chapters[4].groups[0].windows.find(w=>w[0]==='hifi-deep-dive'&&w[1]===98.9);gate[1]=98.7;gate[2]=106.5;
map.chapters[4].groups[2].windows.find(w=>w[0]==='ringfit'&&w[1]===207)[2]=217.25;
map.capacityReview={reviewedAt:new Date().toISOString(),purpose:'Actual ASR-aligned commentary exceeded a few original spare windows; add freshly reviewed distinct native actions, never repeat/slow a source or shorten original explanations.',sheets:['capacity-windows.json','capacity-final-windows.json','capacity-boundaries.json','capacity-spare-actions.json','capacity-bowling-actions.json'].map(f=>work+'/source-proof/'+f),notes:['199.8–201.95 is fresh native three-lane bowling with balls/pins, before the title menu.', 'Bowling original ends at105.75 before the actual soccer promo title at105.8; preserve the native change.', 'Points Earned continues natively through275.6; it is actual game UI, not a channel slide.', 'Remix109.5–115.8 retains a fresh Perfect followed by native boss input/attack with HUD; no plot dialogue.', 'Gate98.7–106.5 starts after the plot transition and ends on the game character at the opened gate.', 'RingFit207–217.25 includes collection, native ingredient menu and actual smoothie creation; not a claim of perfect stage completion.', 'Rejected HiFi190–209 plot scene; rejected Sports251.5–256.8 promo rank chart.']};
fs.writeFileSync(file,JSON.stringify(map,null,2)+'\n');
const reviewFile=work+'/source-action-direct-review.json',review=JSON.parse(fs.readFileSync(reviewFile,'utf8'));
review.mapSha256=crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');review.capacityReview=map.capacityReview;review.reviewedAt=new Date().toISOString();fs.writeFileSync(reviewFile,JSON.stringify(review,null,2)+'\n');
console.log('Fresh actual-gameplay capacity recorded after direct visual review.');
