const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),prod='projects/game-lighting-history-03/production';
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const baseline=prod+'/review-input-plan-v15.json';if(sha(baseline)!=='0681e970c71de503a7de24b8172fee209b0c2df2bd70a233859942cdecd14579')throw Error('Baseline changed');
const old=JSON.parse(fs.readFileSync(path.join(root,baseline))),cuts=[];
const strip={normalizedCrop:[0,850,1920,136],destination:[0,64],label:'원본 비교 표기 · 제작사 제공 수치'};
function replacement(slotId,rangeFrames){
 const prior=old.inputs.filter(c=>c.slotId===slotId),sample=prior[0];let f=sample.fromFrame;
 for(const [i,[start,frames]]of rangeFrames.entries()){
  const id=slotId+'-repair-'+String(i+1).padStart(2,'0');cuts.push({...sample,id,fromFrame:f,toFrame:f+frames,frames,sourceFromSeconds:start,sourceToSeconds:start+frames/60,sourceUiLift:strip,output:`production/research/game-lighting-history/local/native-repair-b-v18/${id}.mp4`,replacesInputIds:prior.map(c=>c.id),sourceMotionApproved:false,finalCaptionPixelsApproved:false,allPixelsReviewed:false});f+=frames;
 }
 if(f!==prior.at(-1).toFrame)throw Error('Timing changed');
}
replacement('05-dlss-helmet',[[19,352],[13,360],[25+8/60,556]]);
replacement('original-35',[[18,635]]);
replacement('06-dlss-thin-lines',[[10,200],[39,473],[13+20/60,280],[28+35/60,420]]);
for(const c of cuts){delete c.verification;if(sha(c.media)!==c.sourceSha256)throw Error('Source changed');}
const merged=old.inputs.filter(c=>!['05-dlss-helmet','original-35','06-dlss-thin-lines'].includes(c.slotId)).concat(cuts);
for(const source of new Set(cuts.map(c=>c.source))){const ranges=merged.filter(c=>c.kind==='actual-review-input'&&c.source===source).sort((a,b)=>a.sourceFromSeconds-b.sourceFromSeconds);for(let i=1;i<ranges.length;i++)if(ranges[i].sourceFromSeconds<ranges[i-1].sourceToSeconds-1e-7)throw Error('Repeated source frames');}
const dest=prod+'/native-repair-b-plan-v18.json';if(fs.existsSync(path.join(root,dest)))throw Error('Preserve existing repair');
fs.writeFileSync(path.join(root,dest),JSON.stringify({preparedAt:new Date().toISOString(),baseline:{path:baseline,sha256:sha(baseline)},cuts,cpuThreads:2,gpuJobs:0,rateChanges:0,loops:0,sourceAudio:false,fixedCaptionPosition:[960,970],unchangedPcm:true,unchangedBodyRatio:true,unchangedChapters:true,sourceOverlapCount:0,
  observations:[{slot:'05-dlss-helmet',chosen:'Helmet/glove source19–24.866667 first, the earlier13–19 motion next, then the25.133333–34.4 table/wall-detail comparison. These are distinct original frames, no repeat.',direct:'CUA rate1 playback covered13–19,19–24.866667,15–36.133333 and25.133333 region; exact source19 image shows enlarged glove/helmet, source25.113 rear helmet/room, source30.268 enlarged table. Source2×ZOOM and original DLSS OFF/ON quality mode + RTX2060/1080p/Epic labels were directly read.',rejected:'Source3 opening logo; source9 door shot does not place helmet/glove detail under the opening specific instruction. Source39.866667 candidate approaches a black ending and is excluded.'},
  {slot:'06-dlss-thin-lines',chosen:'Source10–13.333333 indoor light strings,39–46.883333 aiming/branches,13.333333–18 indoor follow-through,28.583333–35.583333 indoor moving boundaries.',direct:'CUA10–13.333333 ended13.444 with indoor thin light strings;39–46.883333 ended46.959 with magnified aim, branch silhouettes and source green comparison rectangles. The28.583333–35.583333 interval ended35.753 indoors, rather than branches; that interval is assigned after the specific branch sentence to the general temporal-boundary/vendor-conditions discussion.',rejected:'Source3 opening logo; fifteen-second initial indoor allocation delays the branch example beyond its actual narrated cue.'}],
  sourceMotionApproved:false,allFinalPixelsReviewed:false,fullAnimatedPlaybackReviewed:false,collected:false,uploaded:false},null,2)+'\n');
console.log(JSON.stringify({cuts:cuts.length,frames:cuts.reduce((n,c)=>n+c.frames,0),sourceOverlap:0,finalApproved:false}));
