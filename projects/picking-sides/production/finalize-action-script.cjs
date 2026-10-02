// Preserve the six explanation chapters; align the new example narration to reviewed actions.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const base=path.resolve(__dirname,'..'),read=p=>JSON.parse(fs.readFileSync(path.join(base,p),'utf8'));
const draft=read('script/draft-bilingual.json'),baseline=read('script/draft-before-source-review.json');
const scene=id=>draft.scenes.find(s=>s.id===id);
scene('01').lines[3]=['짧은 공식 예고편이므로, 경기 전체의 승패보다 지금 보이는 동작에 집중해 보겠습니다.','These short official trailers show particular actions. Focus on those actions rather than inferring an entire match result.'];
scene('05').lines=[
 ['갱 비스트의 초기 개발 장면을 먼저 보겠습니다. 노란 캐릭터를 따라볼까요, 빨간 캐릭터를 따라볼까요? 같은 화면에서도 먼저 살펴볼 몸체를 고를 수 있습니다.','Start with this early Gang Beasts development clip. Will you follow the yellow character or the red one? Even in the same view, you can choose which body to watch first.'],
 ['발판 위에서 버티는 쪽과 가장자리에 매달린 쪽의 다음 행동은 다릅니다. 여기서 선수의 성격을 단정하기보다, 지금 어떤 움직임이 궁금한지 생각해 보세요.','A character on the scaffold faces a different next move from one hanging at its edge. Rather than assuming a player personality, ask which movement you want to see next.'],
 ['이 차이를 자체 우편 경주로 옮겨보겠습니다. 별은 빠르게 달리지만 상자에 부딪칠 수 있고, 잎은 조금 느리지만 점프를 놓치지 않게 설정했습니다.','Now translate that idea into our courier race. Star runs faster but can hit crates. Leaf moves more slowly, with jump decisions set to avoid missing a crate.'],
 ['별 아래의 노란 표시가 관전 대상을 알려줍니다. 화면의 다리는 배경이고, 실제 장애물은 상자입니다. 어떤 차이를 소개했는지 실제 행동과 맞춰보세요.','The yellow marker under Star identifies the selected courier. The bridges are scenery; crates are the actual obstacles. Match the description to the behavior you can see.'],
 ['이번에는 잎을 고릅니다. 카메라와 선택 표시는 바뀌지만 세 배달원의 달리기는 이어집니다. 대상을 고르는 일과 경기 결과를 계산하는 일을 분리했습니다.','Now select Leaf. The view and selection marker change while all three couriers keep running. Selecting whom to watch is separate from calculating the result.'],
 ['달로 바꾸어도 속도나 장애물의 규칙을 바꾸지는 않습니다. 빠른 시도를 보고 싶은지, 차분한 진행을 보고 싶은지 관전자가 자기 기준을 고를 수 있습니다.','Switching to Moon does not change speed or obstacle rules. A spectator can choose whether to follow a fast attempt or a steadier approach.'],
 ['관전자에게 반드시 커다란 보상을 줄 필요는 없습니다. 저 배달원이 다음 상자를 잘 넘었으면 좋겠다는 작은 기대부터 시작할 수 있습니다.','The spectator does not necessarily need a large reward. A small hope that this courier clears the next crate can be a starting point.']
];
scene('09').lines=[
 ['다시 개발팀이 플레이한 얼티밋 치킨 호스입니다. 우주 배경을 날아가는 동물 중에서, 뿔이 있는 양 한 마리를 정해 따라가 보세요.','Return to Ultimate Chicken Horse played by its developers. Among the animals flying through space, choose the horned sheep and follow it.'],
 ['다른 동물까지 넓게 보이면 한 캐릭터는 작아집니다. 전체 위치를 보는 일과 내가 보던 대상을 찾는 일은 같은 문제가 아닙니다.','A view covering several animals can make each one small. Seeing the whole area and finding the participant you were following are different tasks.'],
 ['구도가 달라질 때마다 같은 양를 다시 찾아보세요. 화면 가운데가 바뀌었다고 다른 동물을 아까 보던 대상으로 착각하지 않는지 확인합니다.','Find that sheep again whenever the framing changes. Check that a shift in the center of the picture does not make you mistake another animal for it.'],
 ['발밑의 추진 효과와 가까운 바위도 봅니다. 외형으로 대상을 찾은 다음에는, 어느 방향으로 움직이는지 읽어야 하기 때문입니다.','Watch the propulsion effect beneath its feet and nearby rocks. After recognizing the participant, you need to read its direction of movement.'],
 ['이 자료는 다른 시도를 이어 보여주기도 합니다. 각 장면의 동작을 관찰하되, 카메라의 내부 계산식이나 한 경기의 연속 결과를 추정하지는 않겠습니다.','This footage also cuts between attempts. Observe the action in each shot without inferring the internal camera algorithm or treating every shot as one continuous contest.'],
 ['목표로 접근할 때와 방향을 바꿀 때도 관심은 이어져야 합니다. 보던 동물을 놓쳤다면, 어디에서 연결이 끊겼는지 다시 살펴보세요.','Attention should survive an approach to the goal and a change of direction. If you lose the animal, look for the point where that connection broke.'],
 ['우리 게임의 관전 화면도 마찬가지입니다. 보기 좋은 구도를 만들면서, 정작 응원하는 대상의 다음 행동을 놓치게 하지는 않는지 확인하세요.','Check the same thing in your own spectator view. An attractive composition should still let viewers follow their chosen participant’s next move.']
];
scene('11').lines=[
 ['마지막으로 새 경주를 한 번 더 봅시다. 이번에는 달을 따라가되, 앞뒤 참가자와의 관계도 함께 보겠습니다.','Watch one more fresh race. Follow Moon while keeping its relationship to the other couriers in view.'],
 ['앞서가던 별이 상자에 닿아 잠깐 멈춥니다. 달이 그 사이를 지나가는지 보세요. 이름이나 순위표보다 실제 움직임에서 차이가 먼저 드러납니다.','Star hits a crate and briefly stops. Watch whether Moon passes in the meantime. The difference first appears in the movement itself, before any ranking display.'],
 ['별이 다시 달려와 앞서갑니다. 달의 응원 표시는 그대로지만 승리를 보장하지 않습니다. 선택한 쪽이 뒤로 밀릴 때도 원인이 보여야 합니다.','Star recovers and moves ahead again. Moon keeps its support marker, but that marker guarantees no victory. The cause should remain visible even when the selected participant falls behind.'],
 ['이제 결승선 통과를 보세요. 이 실행의 도착 순서는 별, 달, 잎입니다. 경기에서 보던 이름과 표식을 결과에서도 그대로 연결하겠습니다.','Now watch the finish-line crossings. This execution finishes Star, Moon, then Leaf. The result keeps the names and emblems used during the race.'],
 ['갱 비스트의 또 다른 짧은 구간도 보죠. 붙잡고 있던 몸이 함께 아래로 내려갑니다. 아까 보던 빨간 캐릭터의 움직임을 끝까지 따라가 보세요.','Look at another short Gang Beasts segment. The bodies that were holding on descend together. Keep following the red character’s movement through the fall.'],
 ['이 개발 영상의 짧은 낙하만으로 전체 경기의 승자를 정하지는 않겠습니다. 지금 보인 행동과 실제로 확인한 결과는 구분해서 전해야 합니다.','That short fall in development footage does not establish the winner of an entire match. Distinguish the action shown from an outcome you have actually verified.'],
 ['누구를 골랐는지, 무엇을 시도했는지, 어떻게 끝났는지가 이어져야 합니다. 응원 문구를 크게 넣기 전에 이 흐름부터 읽을 수 있게 만들어보세요.','Connect whom the viewer selected, what that participant attempted and how it ended. Make that sequence readable before adding a large cheering message.']
];
const preserved=[];
for(const id of ['02','04','06','08','10','12']){
 const now=JSON.stringify(scene(id).lines),old=JSON.stringify(baseline.scenes.find(s=>s.id===id).lines);
 if(now!==old)throw Error('Explanation content changed: '+id);
 preserved.push({id,unchanged:true,sha256:crypto.createHash('sha256').update(now).digest('hex')});
}
draft.status='source-aligned-script-ready-for-measured-tts';
draft.sourceReviewNotes={at:new Date().toISOString(),preservedExplanationScenes:preserved.map(s=>s.id),changes:'All six explanation chapters preserved. Actual sections aligned to observed commercial actions and original execution events; new shots added to selection and outcome chapters.',notClaimed:['human live input recording','spectator enjoyment study','commercial camera algorithm knowledge']};
fs.writeFileSync(path.join(base,'script/draft-bilingual.json'),JSON.stringify(draft,null,2)+'\n');
fs.writeFileSync(path.join(base,'production/script-source-review.json'),JSON.stringify({updatedAt:new Date().toISOString(),status:'source-content-reviewed-final-timing-and-captions-pending',preservedExplanationScenes:preserved,pairedParagraphs:draft.scenes.reduce((n,s)=>n+s.lines.length,0),contentReview:'1-second alpha/trailer and2-second extended/developer source samples directly reviewed. Removed logo cards and alpha scorecards from proposed actual intervals. Source edits distinguish attempts; never fabricate continuity.',pending:['Measured TTS and all current-hash ASR','Exact final source cuts and crops per measured narration','All final cue/cut pixels and UI overlap','Exact body60:40 and separate short result explanation','Final render, QA, collection, private upload, Git'],humanInputRecording:false,ttsStarted:false,finalRender:false},null,2)+'\n');
console.log('Source-aligned72paragraphs;30explanationparagraphs preserved exactly.');
