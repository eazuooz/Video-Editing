const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../../../../'),base='production/batches/sakurai-planning-game-design',proof=base+'/proof-avoid-game-comparisons',sr=proof+'/source-research',project='projects/avoid-game-comparisons';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const write=(p,d)=>fs.writeFileSync(path.join(root,p),JSON.stringify(d,null,2)+'\n');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const now=new Date().toISOString(),native=read(sr+'/native-review-drill-v1.json'),src=native.sources[0],discovery=read(sr+'/discovery-pepper-drill.json');
if(native.status!=='native-samples-extracted-awaiting-direct-review')throw Error('Incomplete extraction');
const observations={
 360:'Shop/text cuts to a very brief movement montage. Hold montage360-370, several cuts under0.2seconds.',
 363:'Cut to collectible close-up.',365:'Cut to purple material close-up.',366:'Same purple close-up, not a new scene.',368:'Cut to avatar over water.',370:'Cut to brown loop close-up.',
 465:'Cut from dark sign/cave movement to yellow column with dialogue overlay; hold overlay.',
 510:'Continuous yellow movement with dialogue; window edge is not a cut.',705:'Truck with dialogue; hold and overlapping other Facts scene.',709:'Cut from truck to brown loop; plain movement until dialogue reappears later.',
 825:'Continuous brown movement under dialogue; not a scene cut.',854:'Cut to purple underground area with dialogue; hold.',870:'Continuous purple underground with dialogue.',873:'Same purple area, jump in framing/edited close-up; hold.',
 932:'Cut to purple material. Same action sequence as Facts50-52, exclude as duplicate.',
 1002:'Cut to a separate ice-panel/wooden-brace movement. Candidate33.4-34.5 avoids shop cut.',1037:'Cut to shop.',1038:'Dialogue appears on shop image; no fresh gameplay.',1050:'Shop/dialogue continuous.',1070:'Shop framing changes; no quota.',
 1455:'Key/blue-cave action ending; overlaps Facts early blue-cave sequence. Hold.',1461:'Cut to avatar and vehicle on flat icy water.',
 1531:'Cut to another icy vehicle jump over wave/wood structure. Do not claim the two edited sections are one continuous chase.',1608:'Cut from water vehicle to blue-sky cannons.',
 1663:'Cut to avatar entering large mechanical device in dark interior.',1709:'Cut to large mechanical device in green ruins, separate from z4 snowy mechanical jump.',1783:'Cut to mechanical device in purple area, not continuous with green ruins.',1840:'Cut to shop/text effect; exclude from61.333.',1875:'Shop/dialogue continuous; no action candidate.'
};
if(src.candidateBoundaryFrames.some(n=>!observations[n]))throw Error('Unrecorded native candidate boundary');
const sheets=[...discovery.sources[0].sheets,...src.actionSheets,...src.boundarySheets].map(item=>typeof item==='string'?item:item.path);
const comparisonSheets=[proof+'/research-local/game-discovery/z4utn4Sm6SY/sheet-03.jpg',...[1,2,3,4].map(n=>proof+'/research-local/game-discovery/4c-3gbC5mc4/sheet-'+String(n).padStart(2,'0')+'.jpg')];
const review={schemaVersion:1,reviewedAt:now,sourceVideoId:src.videoId,sourceSha256:src.sourceSha256,status:'all-discovery-native-and-boundary-sheets-read-conservative-unique-candidates',discoveryFrames:discovery.sources[0].frames,actionFrames:src.actionSamples.length,boundaryTriplets:src.candidateBoundaryFrames.length,boundaryTiles:src.boundarySamples.length,directlyReadSheets:sheets.map(p=>({path:p,sha256:hash(p)})),duplicateComparisonSheets:comparisonSheets.map(p=>({path:p,sha256:hash(p)})),boundaryDecisions:src.candidateBoundaryFrames.map(frame=>({frame,seconds:frame/30,observation:observations[frame]})),limitations:['No source audio used. Historical demo/promotion observations, not a current control specification.','Raw sources, frames, contact sheets and fullwatch AX remain local-only.','manualBoundaryFrames in the request was not consumed by the generic extractor. Actual29 scene/window edges above are the extracted and inspected evidence. No manual-edge coverage is claimed.','Selected intervals are conservative planning bounds within directly read native action windows. Exact final encoded edge/caption approval still pending.','Purple material31.0667-33.4 duplicates Facts50-52 and is excluded; truck/dialogue/shop/title intervals and very short initial montage excluded.'],newGitImages:0,bodyRatioApproved:false,finalCutAndCaptionApproval:false};
write(sr+'/direct-pepper-drill-review.json',review);
const intervals=[
 [12.5,15.4,'02','Drill through a dark cave with signs, curve through low terrain and exit into air','Follow the changing path through and above the surface'],
 [24,26.2,'06','Curve through the brown loop and descend toward the lower route','Observe the terrain and the visible movement, without claiming an input or resource rule'],
 [33.4,34.5,'06','Move inside an ice panel beside wooden braces','Identify the visible material and spatial constraint'],
 [48.8,51,'10','Avatar reaches an icy water vehicle and the vehicle advances on flat water','Describe only this shot; do not infer a continuous connection to the next shot'],
 [51.1,53.5,'10','Vehicle rises over ice waves and a wooden obstacle','Observe vehicle movement in a distinct edited source shot'],
 [53.7,55.4,'12','Avatar launches among blue-sky cannons','Distinguish a cannon launch from underground drilling'],
 [55.5,56.9,'12','Avatar enters a large mechanical device in a dark interior','The entry is visible; do not invent its cost or unlock prerequisite'],
 [57,59.4,'12','Mechanical device fires and crosses ruined platforms in green scenery','Follow the mechanical movement and visible broken objects without inferring victory'],
 [59.5,61.2,'12','Mechanical device advances and fires in a purple underground area','Separate this edited scene from the preceding green ruins']
];
const bank=read(sr+'/source-action-bank-v1.json');
if(bank.clips.length!==71)throw Error('Unexpected prior bank');
const plan=read(project+'/planning/chapter-plan.json'),map=read(project+'/sources/action-map.json');
if(map.clips.some(c=>c.sourceVideoId===src.videoId))throw Error('Additional candidates already assigned');
const clips=intervals.map(([start,end,sceneId,visibleAction,viewerFocus],i)=>{
 const chapter=plan.chapters.find(c=>c.id===sceneId),startFrame=Math.round(start*30),endFrameExclusive=Math.round(end*30);
 return {id:'action-'+(72+i),sourceVideoId:src.videoId,sourceUrl:'https://www.youtube.com/watch?v='+src.videoId,sourceSha256:src.sourceSha256,nativeFps:30,startFrame,endFrameExclusive,inSeconds:startFrame/30,outSeconds:endFrameExclusive/30,seconds:(endFrameExclusive-startFrame)/30,visibleAction,viewerFocus,planningClaim:chapter.claim,diagramConnection:chapter.diagram,insertionPoint:'Scene '+sceneId+' interleaved with independent explanation',caution:'Historical official demo footage; describe the observed action only. No exact inputs, universal resource rules, success, continuous causality between edited shots or developer-pitch authorship is claimed.',status:'selected-for-independent-planning',finalCaptionFramingApproved:false,finalCutAndCaptionApproval:false,sceneId,explainedClaim:chapter.claim};
});
bank.createdAt=now;bank.previousBank=sr+'/source-action-bank-v1.json';bank.directReview=[...(Array.isArray(bank.directReview)?bank.directReview:[bank.directReview]),sr+'/direct-pepper-drill-review.json'];bank.clips.push(...clips);bank.uniqueSourceSeconds=Number(bank.clips.reduce((a,c)=>a+c.seconds,0).toFixed(6));bank.bySourceSeconds[src.videoId]=18;bank.status='80-conservative-unique-source-candidates-not-final-timeline';
write(sr+'/source-action-bank-v2.json',bank);
for(const c of clips){map.clips.push(c);for(const chapters of [map.chapters,plan.chapters])chapters.find(x=>x.id===c.sceneId).sourceActionIds.push(c.id);}
map.updatedAt=now;map.sourceBank=sr+'/source-action-bank-v2.json';map.sourceBankMaximumSeconds=bank.uniqueSourceSeconds;map.candidateActualSeconds=Number(map.clips.reduce((a,c)=>a+c.seconds,0).toFixed(6));
plan.planningBudget.selectedConservativeSourceSeconds=map.candidateActualSeconds;plan.planningBudget.additionalRelevantActualSeconds=plan.planningBudget.requiredActualSeconds.map(n=>Number(Math.max(0,n-map.candidateActualSeconds).toFixed(6)));plan.updatedAt=now;
write(project+'/sources/action-map.json',map);write(project+'/planning/chapter-plan.json',plan);
for(const p of [proof+'/source-candidates-and-usage-review.json',project+'/sources/game-candidates.json']){
 const d=read(p);d.additionalSourceReviews=[...(d.additionalSourceReviews||[]),{videoId:src.videoId,game:'Pepper Grinder',status:'selected-nine-unique-conservative-planning-intervals',directReview:sr+'/direct-pepper-drill-review.json',newUniqueActualSeconds:18,selectedActionIds:clips.map(c=>c.id),excluded:['Shop/dialogue/marketing','Repeated purple material action from Facts50-52','Subsecond intro montage','Source audio'],rightsEvidence:d.permission.url,finalPublicRights:'pending'}];d.actionBank=sr+'/source-action-bank-v2.json';d.planningIntervals=bank.clips.length;d.planningUniqueSeconds=bank.uniqueSourceSeconds;d.projectAssignedIntervals=map.clips.length;d.projectAssignedSeconds=map.candidateActualSeconds;d.updatedAt=now;write(p,d);
}
const manifest=read(project+'/project.json');manifest.status='independent-planning-source-review';manifest.editing.sourceActionBank=sr+'/source-action-bank-v2.json';manifest.editing.plannedCandidateActualSeconds=map.candidateActualSeconds;manifest.editing.bodyRatioApproved=false;write(project+'/project.json',manifest);
const outlinePath=path.join(root,project+'/planning/outline.md');fs.appendFileSync(outlinePath,'\n## 추가 공식 소스 직접 검토 — '+now+'\n\nReveal(dkxNejWRGsA)은 이미 검토한 z4utn4Sm6SY와 같은 실제행동/편집 순서라 새 실제시간0초로 제외했다. DRILLfomercial(o3Fomp9HdHs)의81탐색프레임·58네이티브동작·29경계삼중화면을 직접읽고 대화/상점/광고·중복 보라색 구간·초단기 몽타주를 제외했다. 새 아홉 후보18초를02/06/10/12에 분산했다. 현재68개 배정후보192.7초/전체은행80후보203초이며 최종컷·고정자막·음성실측60:40 승인은 아니다. 원래 설명을 줄이지 않고 실제 음성 길이에 따라 더 필요한 관련 구간을 확보한다. 새 출처와 현재action-map을 우선한다.\n');
console.log(JSON.stringify({review:sr+'/direct-pepper-drill-review.json',newCandidates:clips.length,newCandidateSeconds:18,bankCandidates:bank.clips.length,bankSeconds:bank.uniqueSourceSeconds,projectCandidates:map.clips.length,projectSeconds:map.candidateActualSeconds,newGitImages:0}));
