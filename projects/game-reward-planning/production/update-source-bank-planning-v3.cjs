const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../..'),base=path.join(root,'projects/game-reward-planning'),proof=path.join(root,'production/batches/sakurai-planning-game-design/proof-game-reward-planning/source-research');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const write=(p,v)=>fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');
const target=path.join(proof,'action-bank-planning-v3.json');if(fs.existsSync(target))throw Error('Preserve current planning');
const bank=read(path.join(proof,'action-bank-planning-v2.json')),native=read(path.join(proof,'frames/native-bank-v11/index.json'));
if(native.cutCount!==1||native.frameCount!==17)throw Error('Expected reviewed native evidence');
const newCut={...read(path.join(proof,'action-bank-v11.json')).cuts[0],visibleAction:'Moving boss, projectiles, in-game impact flash, enemy disappearance and item pickup prompts.',focus:'Compare the visible work needed from attack through impact; do not infer normal acquisition costs, an earned unlock or costume statistics.',classification:'candidate-existing-game-action',nativeBoundaryReview:'directly-read-v9-all42-and-v11-all17',intervalApprovedForIndependentPlanning:true,fixedCaptionSafety:'pending-final-cues-and-render',finalApproved:false};
bank.cuts.push(newCut);
const sceneIds={
 '02':['ammo-01','ammo-06','ammo-11','overview-03','shatter-03','overview-04'],
 '04':['ammo-02','ammo-03','ammo-04','ammo-05','ammo-09','ammo-10','shatter-04','shatter-01','ammo-08','bounty-08','bounty-09','bounty-10','bounty-11'],
 '06':['ammo-12','ammo-13','ammo-14','coop-01','shatter-02','bounty-01','bounty-02','bounty-03','bounty-12','bounty-13'],
 '08':['ranch-02','ranch-03','ranch-05','ranch-05b','appearance-01','appearance-03','base-02'],
 '10':['base-01','overview-05','shatter-06','shatter-07','bounty-04','bounty-05','bounty-14','bounty-15','bounty-16','bounty-17','bounty-18','improved-combat-01'],
 '12':['overview-01','overview-02','overview-06','overview-07','ammo-15','shatter-08','coop-02','wool-01','wool-02','wool-03','wool-04','wool-06-brick','wool-07','bounty-06','bounty-07']
};
const assigned=new Set();for(const [sid,ids]of Object.entries(sceneIds))for(const id of ids){const cut=bank.cuts.find(c=>c.id===id);if(!cut||assigned.has(id))throw Error('Missing/reused cut '+id);cut.scriptScene=sid;assigned.add(id);}
if(assigned.size!==bank.cuts.length)throw Error('Every cut needs a distinct chapter assignment');
bank.createdAt=new Date().toISOString();bank.status='63-source-first-intervals-approved-for-planning-only';bank.totalCandidateSeconds=bank.cuts.reduce((s,c)=>s+c.durationSeconds,0);bank.finalApproval=false;
bank.reallocationReview={ammo08:'Move the already reviewed material-collection shot to04, matching its opening materials/research condition observation.',base02:'Move the already reviewed station appearance/player movement to08 as a brief functional-use comparison after the cosmetic shots; no new unlock or costume-statistic claim.',newCut:'Add a fresh contiguous3.4s boss/impact/item-prompt interval to10; no repeated frames, altered speed or idle title cards.'};
bank.chapterCapacity=Object.fromEntries(Object.entries(sceneIds).map(([sid,ids])=>[sid,ids.reduce((s,id)=>s+bank.cuts.find(c=>c.id===id).durationSeconds,0)]));
write(target,bank);
const mapPath=path.join(base,'sources/action-map.json'),map=read(mapPath);write(path.join(__dirname,'action-map.before-planning-v3.json'),map);
map.bank=path.relative(root,target).replaceAll('\\','/');map.bankSha256=hash(target);map.status='source-first-planning-v3-awaiting-repaired-voice-final-timing-captions';map.selectedCandidateSeconds=bank.totalCandidateSeconds;
for(const chapter of map.chapters)chapter.cuts=(sceneIds[chapter.sceneId]||[]).map(id=>bank.cuts.find(c=>c.id===id));map.chapterCapacity=bank.chapterCapacity;map.reallocationReview=bank.reallocationReview;write(mapPath,map);
const gatePath=path.join(base,'production/script-source-review.json'),gate=read(gatePath);for(const rel of Object.keys(gate.inputs))gate.inputs[rel]=hash(path.join(base,rel));gate.reviewedAt=new Date().toISOString();gate.intervalBank=map.bank;gate.allCurrentClaimsDirectlyComparedAfterCutAssignment=true;write(gatePath,gate);
write(path.join(proof,'direct-supplemental-review-v9-v11.json'),{reviewedAt:new Date().toISOString(),nativeVersions:[{version:'v9',frames:42,all3SheetsDirectlyRead:true},{version:'v10',frames:31,all2SheetsDirectlyRead:true},{version:'v11',frames:17,all1SheetDirectlyRead:true}],rejected:[{id:'appearance-before',reason:'24s held inventory followed by costume title card through26.6s; no quota extension.'},{id:'appearance-movement-before',reason:'Real actions but chest/drop-object wheel and freeze shot do not add the needed appearance comparison; preserve as unselected research.'}],selected:[newCut],allSpeed1:true,sourceAudio0:true,agentGames0:true,finalCaptionApproval:false,finalRatioApproval:false});
const choicesPath=path.join(base,'sources/game-candidates.json'),choices=read(choicesPath);choices.supplementalMeasuredSpeechReview={reviewedAt:new Date().toISOString(),nativeProof:'production/batches/sakurai-planning-game-design/proof-game-reward-planning/source-research/direct-supplemental-review-v9-v11.json',selected:newCut,reallocated:bank.reallocationReview,totalPlanningCandidateSeconds:bank.totalCandidateSeconds,finalApproval:false};write(choicesPath,choices);
fs.appendFileSync(path.join(base,'planning/outline.md'),'\n## 실측 뒤 출처 재배치（planning-v3）\n\n04의 재료·연구 설명에 이미 검토한ammo-08을 옮기고,08의 외형/기능 비교에 이미 검토한base-02의 연구대 출현과 옆을 움직이는 실제 동작을 넣는다.10에는mRkJ2uWFWYw45.9–49.3초의 새 보스/발사/명중/아이템 안내를 추가한다.26.6초까지의 의상 제목이나 복장 비교와 맞지 않는 상자/물체 휠은 쓰지 않는다.63구간254.15초는 독립 후보의 확보량이며 최종60:40이나 자막 안전 승인은 아니다.\n');
console.log(JSON.stringify({cuts:bank.cuts.length,seconds:bank.totalCandidateSeconds,capacities:bank.chapterCapacity,finalApproval:false}));
