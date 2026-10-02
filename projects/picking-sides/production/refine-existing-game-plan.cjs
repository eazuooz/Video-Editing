// Apply findings from the actual composition contact sheets; preserve evidence.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),base='projects/picking-sides/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const write=(p,x)=>fs.writeFileSync(path.join(root,p),JSON.stringify(x,null,2)+'\n');
const p=read(base+'production/existing-game-replan/action-map-v2.json'),d=read(base+'script/draft-bilingual.json');
const old=base+'production/existing-game-replan/draft-before-composition-trims.json';if(fs.existsSync(path.join(root,old)))throw Error('One-time refinement already applied');write(old,d);
const update=(scene,index,start,end,note)=>{const c=p.chapters.find(x=>x.scene===scene).cuts[index-1];Object.assign(c,{start,end,availableSeconds:+(end-start).toFixed(6),compositionNeedsReview:true,boundaryCorrection:note});};
update('01',2,17,25.1,'Stop before scorecard starts rising at25.4s');
update('01',3,8.5,10.7,'Remove factory-transition black strip at8.2s');
update('01',4,13.2,14.5,'Remove letter-mask transition at12.8s');
update('01',6,18.8,21.7,'Remove low billboard characters hidden behind fixed caption');
update('01',7,24.3,25.8,'Use elevator action only; remove billboard grip behind caption');
update('03',1,70,85,'Remove treehouse level-menu area67–70s');
update('05',4,462,489,'Remove previous attempt/low green body before reset');
update('07',4,58.5,60.2,'Remove build-mode card after the jump/explosion');
update('07',6,638,644,'Keep visible cyan/yellow hands; exclude mostly hidden bodies at636/646');
const extra=(scene,sourceId,start,end,action)=>p.chapters.find(x=>x.scene===scene).cuts.push({sourceId,start,end,availableSeconds:+(end-start).toFixed(6),action,crop:null,classification:'actual-existing-game-action',speed:1,loop:false,finalBoundaryApproved:false,compositionNeedsReview:true});
extra('01','tNgCy92QWZY',26.8,29.3,'Separate scaffold plank grip sequence, normal speed');
extra('01','tNgCy92QWZY',36,37.8,'Separate lighthouse grappling, bodies and rail');
extra('01','tNgCy92QWZY',39,40.8,'Separate stairs gripping/tilting sequence');
extra('01','tNgCy92QWZY',44.2,45.8,'Separate fan-platform airborne/gripping action');
// Keep trailer clips before the narration explicitly introduces early truck play.
p.chapters[0].cuts.sort((a,b)=>(a.sourceId==='4KBUHwBx5i4'?0:a.sourceId==='tNgCy92QWZY'?1:2)-(b.sourceId==='4KBUHwBx5i4'?0:b.sourceId==='tNgCy92QWZY'?1:2)||a.start-b.start);
extra('05','iagyci5LMTY',496,522,'A visibly separate attempt: movement toward one roof, grabs, red at edge; end before extended repetition.');
for(const chapter of p.chapters){chapter.availableSeconds=+chapter.cuts.reduce((n,x)=>n+x.availableSeconds,0).toFixed(6);for(const c of chapter.cuts){c.sourceDisplay=c.sourceId==='iagyci5LMTY'?'Gang Beasts · 개발사 공개 초기 플레이 (2014)':c.sourceId==='VOZRzwlzQeA'?'Gang Beasts · 개발사 공개 초기 플레이 (2014)':c.sourceId==='BZRZmJnPmmA'?'Ultimate Chicken Horse · 공식 알파 플레이 (2015)':c.sourceId==='Z5jytMiH4rI'?'Ultimate Chicken Horse · 개발팀 플레이':'공식 게임플레이 예고편';}}
p.sourceActionBankSeconds=+p.chapters.reduce((n,c)=>n+c.availableSeconds,0).toFixed(6);p.updatedAt=new Date().toISOString();
p.additionalSourceReview=['production/official-source-review/tNgCy92QWZY-26-48-1-contact-1.png','production/official-source-review/tNgCy92QWZY-26-48-1-contact-2.png','production/official-source-review/iagyci5LMTY-492-532-2-contact-1.png','production/official-source-review/iagyci5LMTY-492-532-2-contact-2.png'];
p.excludedAfterComposition=['Z5jytMiH4rI67–70 menu','4KBUHwBx5i425.1+scorecard','tNgCy92QWZY12.8letter-mask and22.6/23.8low billboard subjects','BZRZmJnPmmA60.2+build mode','iagyci5LMTY636/646hidden bodies and457.5previous-attempt low body','Z5jytMiH4rI407–425 roof snippets: scorecards and short/narrow views, not a suitable long replacement'];
write(base+'production/existing-game-replan/action-map-v2.json',p);write(base+'planning/action-map.json',p);
// Make commentary concise enough to accompany the observed actions. All six
// explanatory chapters and their teaching claims remain unchanged by this step.
const edits={
 '01':{1:['닭을 따라가 보세요. 톱날을 피할까? 다음 발판에 닿을까? 같은 화면에서도 찾는 행동이 달라집니다.','Follow the chicken. Will it avoid the saw and reach the next platform? You start looking for different actions in the same view.'],3:['짧은 컷들은 서로 다른 상황입니다. 지금 고른 캐릭터의 다음 행동부터 따라가 보세요.','These short shots show different situations. Follow the next action of the character you chose.']},
 '03':{5:['통제된 비교 실험은 아닙니다. 외형, 색, 주변 위치가 각각 어떤 단서를 주는지 관찰하는 것입니다.','This is not a controlled experiment. We are observing what clues appearance, color and surrounding positions offer.'],6:['작은 화면이나 겹치는 순간에도 같은 대상을 찾을 수 있는지 보세요. 표시는 움직이는 몸과 함께 읽혀야 합니다.','Check whether the same participant can be found on a small screen or in a crowd. A marker must be readable with the moving body.']},
 '05':{4:['다음 시도에서는 다른 캐릭터를 골라도 됩니다. 이 선택은 새 기능이 아니라, 관전자가 누구를 따라볼지 정하는 일입니다.','You can choose a different character in the next attempt. This means deciding whom to follow, not adding a new game feature.'],5:['행동 하나로 선수의 성격까지 단정하지 마세요. 지금 화면에서 확인한 움직임부터 설명하면 됩니다.','Do not infer a player’s personality from one action. Start by describing the movement you can actually see.']},
 '07':{3:['뒤의 다른 시도에서는 말이 움직입니다. 컷이 바뀌었으니 닭의 점프가 이어진 결과로 보아서는 안 됩니다.','The horse moves in a different attempt. The cut should not make its outcome look like a continuation of the chicken’s jump.'],5:['다음 시도에서는 다시 지붕 위로 모입니다. 누가 누구를 잡고 어느 가장자리로 가는지 보세요.','The next attempt brings them together on the roof again. Follow who holds whom and which edge they approach.']},
 '09':{4:['깃발 접근과 아래에서 다시 올라오는 시도를 구분하세요. 편집된 다른 시도를 한 번의 긴 비행으로 읽으면 안 됩니다.','Distinguish approaching the flag from rising again. Edited attempts should not be read as one continuous flight.'],5:['여기서는 보이는 이동과 구도를 관찰합니다. 내부 카메라 계산식이나 모든 관전자에게 최선인 구도를 알아낸 것은 아닙니다.','We are observing visible movement and framing, not discovering the internal camera algorithm or the best view for everyone.']},
 '11':{3:['다음은 별도의 발판 장면입니다. 매달린 캐릭터와 발판의 기울기가 어떻게 바뀌는지 보세요.','Next is a separate scaffold scene. Watch how the hanging characters and platform angle change.'],5:['전체 경기의 승자는 이 자료만으로 확인할 수 없습니다. 보인 낙하와 시도까지만 설명하겠습니다.','This material does not establish the whole match’s winner. We describe only the attempts and falls shown.']}
};
for(const s of d.scenes)for(const [index,pair]of Object.entries(edits[s.id]||{}))s.lines[+index]=pair;
d.sourceReviewNotes.compositionRefinement={at:p.updatedAt,reason:'Exclude observed menus/title transitions, hidden subjects and caption conflicts; tighten new actual-footage commentary. No explanation claim or paragraph shortened.',allExplanationParagraphsUnchangedSinceBaselineReplan:true};
write(base+'script/draft-bilingual.json',d);
const r=read(base+'production/existing-game-replan/source-review.json');r.sourceActionBank=p.chapters;r.availableActualSeconds=p.sourceActionBankSeconds;r.refinement={at:p.updatedAt,firstMiddleLastSamples:99,allDirectlyViewed:true,findings:p.excludedAfterComposition,additionalReviewedContacts:p.additionalSourceReview,finalCueReview:false};write(base+'production/existing-game-replan/source-review.json',r);
const qa=read(base+'production/existing-game-replan/composition/review.json');qa.review='all99directly-viewed; corrected-source-boundaries-required';qa.findings=p.excludedAfterComposition;qa.reviewedAt=p.updatedAt;write(base+'production/existing-game-replan/composition/review.json',qa);
console.log(JSON.stringify({bank:p.sourceActionBankSeconds,chars:d.scenes.filter(s=>+s.id%2).map(s=>({scene:s.id,ko:s.lines.reduce((n,x)=>n+x[0].length,0)}))}));
