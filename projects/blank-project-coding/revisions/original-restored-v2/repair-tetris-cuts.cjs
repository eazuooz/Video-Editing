const fs=require('fs'),path=require('path'),assert=require('assert/strict');const W=__dirname,read=f=>JSON.parse(fs.readFileSync(path.join(W,f),'utf8')),write=(f,v)=>fs.writeFileSync(path.join(W,f),JSON.stringify(v,null,2)+'\n');
const ranges={
 '011':[[101.25,112],[700.25,703.9]],'013':[[126,132.75],[703.9,705.15]],
 '019':[[138,140.25],[141.5,142.25],[143.75,148.75],[150,156],[705.15,709.15]],
 '020':[[156,157.75],[159.5,160.6],[366.25,368]],
 '022':[[180,184.75],[185.5,186.75],[187.5,188.25],[189,190.6],[368,370.25]],
 '085':[[466.25,468.25],[469,478],[374.75,377.75]],
 '086':[[612.25,614.25]],'089':[[484.75,488],[377.75,378.5]],
 '090':[[493,496.25],[497.75,503.75],[505.25,506.75],[507.5,508.2],[614.25,618],[733.25,734.25]],
 '102':[[546,548.25],[549.75,554.75],[556,556.4],[734.25,737]]
};
const p=read('plan.json'),before=p.cuts.filter(c=>ranges[c.id]);assert(before.every(c=>!c.sourceSegments),'Already repaired');write('pre-tetris-cleanup-cuts.json',before);
for(const c of p.cuts){if(!ranges[c.id])continue;c.sourceSegments=ranges[c.id].map(([sourceIn,sourceOut])=>({sourceIn,sourceOut,frames:Math.round((sourceOut-sourceIn)*60),speed:1}));assert.equal(c.sourceSegments.reduce((n,s)=>n+s.frames,0),c.frames,c.id);c.sourceIn=c.sourceSegments[0].sourceIn;c.sourceOut=c.sourceSegments.at(-1).sourceOut;c.localIn=c.sourceIn;c.editorialCorrection='Meme/stock inserts removed after dense 2fps source review; exact action-only intervals are sourceSegments, without loops, slowdown or timing changes.';}
const all=p.cuts.filter(c=>c.key==='tetris').flatMap(c=>(c.sourceSegments||[{sourceIn:c.sourceIn,sourceOut:c.sourceOut}]).map(s=>({...s,cut:c.id}))).sort((a,b)=>a.sourceIn-b.sourceIn);for(let i=1;i<all.length;i++)assert(all[i].sourceIn>=all[i-1].sourceOut-1e-6,JSON.stringify(all.slice(i-1,i+1)));for(const s of all)for(const [a,b]of[[54,60.5],[84,90.5],[320,326.5]])assert(s.sourceOut<=a||s.sourceIn>=b);
write('plan.json',p);const fc=read('footage-cuts.json');fc.clips=p.cuts;write('footage-cuts.json',fc);
write('tetris-cleanup-review.json',{reviewedAt:new Date().toISOString(),reason:'Dense source inspection revealed third-party memes and unrelated stock overlooked by sparse first/middle/last sampling.',directlyReviewedContactPages:12,samplingFps:2,cutIds:Object.keys(ranges),sourceSegments:ranges,timelineAndNarrationUnchanged:true,noRepeatedSourceIntervals:true,previousVersionIntervalsExcluded:true,finalRenderReview:'pending'});
for(const file of ['source-pools.json','concept-connections.json']){const o=read(file);o.finalTetrisEditorialCorrection={evidence:'tetris-cleanup-review.json',exactFinalCuts:'footage-cuts.json',sourceSegmentsOverrideInitialCandidatePools:true};write(file,o);}
console.log(Object.keys(ranges).join(','));
