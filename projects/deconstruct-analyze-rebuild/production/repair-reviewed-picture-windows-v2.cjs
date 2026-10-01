// Directly reviewed picture-only fixes. Preserve all frames, timing and audio.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v2');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8')),write=(f,v)=>fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');
const plan=read(path.join(work,'plan.json')),decisions=[];
for(const [sceneId,cutNumber,before,after,reason,proof] of [
 ['addition-01',3,1.5,2,'Initial 0.4 seconds were black. A 0.5-second later start retains the same continuous action and ends at 16.7 before the promotional card.','transition-repair-boundaries.json'],
 ['addition-01',5,21,21.1,'The exact 21.0-second source frame was black; 21.05 onward is visible spell action. Start at 21.1, retaining 226 frames and ending before the 25.15 promotional card.','snow-action-start.json'],
 ['addition-02',4,26.5,69.45,'The old interval included a black montage transition at 28.5. Fresh contiguous 69.45–73.8667 gameplay shows aiming and movement over changed material; adjacent chapter ends at 69.4, so there is no reuse.','fresh-blue-action.json']
]){
 const s=plan.scenes.find(s=>s.id===sceneId),c=s.cuts[cutNumber-1];
 if(c.sourceIn!==before&&c.sourceIn!==after)throw Error('Unexpected source window '+sceneId+' '+cutNumber);
 c.sourceIn=after;c.originalIn=after;
 s.segments.find(g=>g.video===c.video).source={...c};
 decisions.push({scene:sceneId,cut:cutNumber,file:c.file,sourceSha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,c.file))).digest('hex'),previousIn:before,currentIn:after,currentOut:after+c.seconds,unchangedFrames:c.frames,unchangedTimelineStart:c.timelineStart,reason,directlyViewedProof:'projects/deconstruct-analyze-rebuild/production/final-v2/source-proof/'+proof});
}
const fifth=plan.scenes.find(s=>s.id==='addition-05');
if(fifth.cuts[2].sourceIn===64){
 const old=fifth.cuts[2];if(old.frames!==324)throw Error('Unexpected dark shot length');
 const shots=[{...old,sourceIn:43.8,originalIn:43.8,frames:240,seconds:4}, {...old,sourceIn:26.5,originalIn:26.5,frames:84,seconds:1.4,timelineStart:old.timelineStart+4}];
 fifth.cuts.splice(2,1,...shots);
 fifth.cuts.forEach((c,i)=>{c.video=`projects/deconstruct-analyze-rebuild/production/final-v2/addition-05-${i+1}.mp4`;c.audio=c.video.replace('.mp4','.wav');});
 fifth.segments=fifth.cuts.map(c=>({key:c.key,kind:'actual-commercial-gameplay',frames:c.frames,seconds:c.seconds,timelineStart:c.timelineStart,video:c.video,source:{...c}}));
 decisions.push({scene:'addition-05',previousIn:64,previousOut:69.4,replacementWindows:shots.map(c=>({in:c.sourceIn,out:c.sourceIn+c.seconds,frames:c.frames})),unchangedFrames:324,unchangedTimelineStart:old.timelineStart,reason:'Direct fine review found completely black 66.95–67.10 transition. Replace with two related fresh spell-and-material actions. The shorter 1.4-second source shows a discrete projectile/impact, rather than repeating or slowing a short original; all speech and total chapter time remain unchanged.',directlyViewedProof:'projects/deconstruct-analyze-rebuild/production/final-v2/source-proof/replace-dark-transition.json'});
}
const ranges={};
for(const s of plan.scenes.filter(s=>s.role==='additional-commentary'))for(const c of s.cuts)(ranges[c.key]??=[]).push([Math.round(c.sourceIn*60),Math.round(c.sourceIn*60)+c.frames]);
for(const [key,v] of Object.entries(ranges)){v.sort((a,b)=>a[0]-b[0]);for(let i=1;i<v.length;i++)if(v[i][0]<v[i-1][1])throw Error('Overlapping source '+key);}
write(path.join(work,'plan.json'),plan);
write(path.join(root,'motion-canvas/src/projects/deconstruct-analyze-rebuild/expanded-v2/production-plan.json'),plan);
write(path.join(work,'source-ranges.json'),{ranges,units:'60-fps normalized source frames',noOverlap:true,noLoops:true,normalSpeed:true});
const map=read(path.join(work,'example-map.json'));
map.chapters[0].groups[1].windows=[['noita2',2,16.7]];
map.chapters[0].groups[2].windows=[['noita3',34,47.7],['noita3',21.1,25.1]];
map.chapters[1].groups[1].windows=[['noita2',19.9,28.9],['noita3',69.45,73.9]];
map.chapters[4].groups[1].windows=[['noita3',43.8,47.8],['noita3',26.5,27.9],['noita3',77,85.5],['noita2',54.1,57.7]];
map.reviewedAt=new Date().toISOString();write(path.join(work,'example-map.json'),map);
write(path.join(work,'picture-window-repair-decisions.json'),{reviewedAt:new Date().toISOString(),decisions,audioChanged:false,timingChanged:false,originalExplanationsChanged:false});
console.log('Three directly reviewed picture windows corrected; timing, voice and original explanations preserved.');
