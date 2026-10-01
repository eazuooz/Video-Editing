// Record the direct action review and exact-window repairs; never infer public approval.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v2');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8')),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const map=read(path.join(work,'example-map.json')),files=[...new Set(Object.values(map.sources).map(s=>s.file))],sources=[];
for(const file of files){
 const r=spawnSync('ffmpeg',['-v','error','-i',path.join(root,file),'-f','null','-'],{encoding:'utf8',windowsHide:true,maxBuffer:4e6});
 if(r.status!==0||r.stderr.trim())throw Error('Source full decode not clean '+file+': '+r.stderr);
 sources.push({file,sha256:hash(path.join(root,file)),fullDecodePassed:true});
}
const evidence={reviewedAt:new Date().toISOString(),mapSha256:hash(path.join(work,'example-map.json')),allWindowsDirectlyReviewed:true,method:'Direct full-source coarse review, every selected boundary/middle and half-second official-montage sampling. Actual allocated/rendered cuts still require final review.',repairs:[
 'Compass starts at 20.5 so acquisition appears during its first sentence.',
 'Beverly ship introduction ends before destination map controls; native warp flash excluded.',
 'Launch tree cut ends37.2; Care montage ends56.85 before review text.',
 'Chapter05 ship commentary uses actual deck/garden/passenger movement, not unrelated island-platform montage.',
 'Launch ship interval ends30.0 before Build heading; night ship interval ends39.3 before transition.',
 'Chapter01 retains the early shell request and later departure; direction sign window ends6.5 while reading is visible.',
 'Chapter02 uses a single continuous climb0.05–13.3, keeping feather/position change under the corresponding first three sentences.',
 'Chapter05 ends on binocular return18.8–24.55 and a brief rest on the same lookout, replacing unrelated hospital/platform montage.',
 'Rainy chest gives a Treasure Map; never described as walking away after completion.',
 'End-stage return observation uses compass departure instead of a stationary climb-dialogue cut.',
 'Farewell and Launch share promotional gameplay; only separately observed fresh action intervals allocated, no duplicate sequence twice.'
 ],sources,normalSpeed:true,loops:false,artificialSlowdown:false,humanListening:'pending',finalPublicRights:'pending'};
fs.writeFileSync(path.join(work,'source-action-direct-review.json'),JSON.stringify(evidence,null,2)+'\n');
const cf=path.resolve(__dirname,'../sources/game-candidates.json'),c=read(cf),a=c.privateExpansionV2;
a.selected[0].observedActions.push('Two fresh direction intersections','Binocular viewpoint control','Hiking steps, forest bridge and updraft','Rainy Treasure Map acquisition');
a.selected[0].observedActions=[...new Set(a.selected[0].observedActions)];
a.selected[0].directReview='All14 official B-roll sources, action boundaries and exact final-v2/example-map.json directly inspected.';
for(const [id,primaryLink] of [['izkQNsycnRA','https://thunderlotusgames.com/blog/beverly-update/'],['aVbhDBYadPo','https://thunderlotusgames.com/blog/jackie-daria-update-release-date/']]){
 const info=read(path.join(root,'shared/assets/meaningful-quests/spiritfarer-official-v2',id+'.info.json'));
 if(info.channel_id!=='UClsFb-jOAgLOr6n9cSRFk9g')throw Error('Publisher mismatch');
 if(!a.selected[1].recordings.some(x=>x.id===id))a.selected[1].recordings.push({id,title:info.title,url:'https://www.youtube.com/watch?v='+id,primaryLink,publisher:info.channel,publisherChannel:info.channel_id,permissionBasis:'Thunder Lotus gameplay analysis/criticism policy; source soundtrack muted; final public rights pending',downloadLicenseLabel:info.license});
}
a.selected[1].directReview='Four official gameplay trailers coarse reviewed, then exact-window half-second samples and current source-action-direct-review.json. Promotional text, transitions, irrelevant platform scenes and duplicated cross-trailer sequence excluded.';
a.currentSourceActionReview='projects/meaningful-quests/production/final-v2/source-action-direct-review.json';
a.pending=a.pending.filter(x=>x!=='Exact source-window/overlay review');if(!a.pending.includes('Every actually rendered cut/caption still requires final visual review'))a.pending.push('Every actually rendered cut/caption still requires final visual review');
fs.writeFileSync(cf,JSON.stringify(c,null,2)+'\n');console.log(JSON.stringify({sources:sources.length,sourceDecodePassed:true,mapSha256:evidence.mapSha256}));
