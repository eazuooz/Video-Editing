const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),base=path.dirname(__dirname);
const write=(f,v)=>{fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,typeof v==='string'?v:JSON.stringify(v,null,2)+'\n');};
const units={
 '01':[
  ['물건 세 개를 가져오세요. 게임에서 자주 만나는 부탁입니다.','Bring back three items. It is a familiar request in games.'],
  ['그런데 같은 심부름도 어떤 때는 다음 목적지가 궁금하고,','Some errands make you curious about the next destination,'],
  ['어떤 때는 빨리 끝내고 싶기만 합니다.','while others just make you want to finish.'],
  ['차이는 가져오라는 말보다, 그 사이에 무엇을 하느냐에 있을 수 있습니다.','The difference may lie in what happens between the instruction and delivery.'],
  ['스카이림의 길과 채집, 서브노티카의 자원 탐색을 비교하고,','We will compare travel and gathering in Skyrim with resource exploration in Subnautica,'],
  ['직접 만든 배달 테스트에서 조건을 바꿔 보겠습니다.','then change conditions in an original delivery prototype.'],
  ['살펴볼 것은 세 가지입니다.','We will examine three questions.'],
  ['이동하며 어떤 선택을 하는지, 완료하면 무엇이 달라지는지,','What choices happen along the way? What changes after delivery?'],
  ['그리고 돌아오는 길에 새로 알게 되는 것이 있는지입니다.','And does the return journey offer anything new?']
 ],
 '02':[
  ['먼저 목적지보다 가는 동안의 행동을 보겠습니다.','First, look at the actions on the way, rather than only the destination.'],
  ['서브노티카에서 재료를 찾을 때는 주변을 살피고,','When gathering materials in Subnautica, you inspect your surroundings'],
  ['남은 산소를 보며 더 찾아볼지 수면으로 돌아갈지 판단합니다.','and use the remaining oxygen to decide whether to keep searching or surface.'],
  ['여기서는 누가 시킨 퀘스트가 아니라,','This is not a quest assigned by a character,'],
  ['플레이어가 필요한 재료를 스스로 찾는 상황을 예로 든 것입니다.','but an example of a player seeking materials for their own needs.'],
  ['모으기라는 목표 안에도 관찰과 선택이 들어갑니다.','A gathering goal can contain observation and decisions.'],
  ['반대로 표시만 따라가며 누를 버튼도 고를 길도 없다면,','If following a marker leaves no action or route to choose,'],
  ['이동 시간이 길어질수록 할 일보다 기다림이 늘어날 수 있습니다.','extra travel time may add waiting rather than meaningful activity.'],
  ['내 퀘스트의 중간 구간에서 플레이어가 결정하는 순간을 적어 보세요.','Write down the moments when players make decisions during your quest.'],
  ['목적지 사이를 채울 선택이 실제로 있는지 확인하는 것입니다.','Check whether those choices actually exist between destinations.']
 ],
 '03':[
  ['다음은 부탁을 끝냈을 때의 변화입니다.','Next, examine what changes when the task is completed.'],
  ['스카이림에서 길을 걷고 광물을 캐는 화면을 보죠.','Here are travel and mining scenes from Skyrim.'],
  ['이 영상은 특정 퀘스트의 보상을 증명하는 장면이 아니라,','This footage does not demonstrate the reward of a particular quest.'],
  ['이동과 채집이라는 행동을 비교하기 위한 예시입니다.','It illustrates the actions of travel and gathering.'],
  ['여기서 내 게임에 물어볼 질문은 따로 있습니다.','The question for our own game is separate.'],
  ['모은 물건을 전달한 뒤에는 점수만 올라가나요?','After delivering the items, does only the score increase?'],
  ['아니면 길이 열리거나, 누군가의 행동이 달라지나요?','Or does a route open, or someone behave differently?'],
  ['보상 숫자도 필요하지만, 내가 한 일의 결과를 화면에서 알 수 있다면,','A numerical reward can matter, but a visible consequence'],
  ['왜 이 부탁을 했는지 이해하는 데 도움이 될 수 있습니다.','may help players understand why the task mattered.'],
  ['이 차이를 작은 배달 게임에서 직접 만들어 보겠습니다.','We will build that difference in a small delivery game.']
 ],
 '04':[
  ['두 버전 모두 같은 길에서 나무 세 개를 모아 돌아옵니다.','Both versions ask you to collect three logs along the same route and return.'],
  ['이동 속도와 물건 위치, 받는 점수는 같습니다.','Movement speed, item positions, and the score reward are identical.'],
  ['첫 버전은 전달하면 점수가 올라가고 부탁이 끝납니다.','In the first version, delivery raises the score and completes the request.'],
  ['두 번째는 같은 전달 뒤 끊어진 다리가 이어집니다.','In the second, the same delivery repairs a broken bridge.'],
  ['그래서 다음에 갈 수 있는 장소가 실제로 달라집니다.','The places you can reach afterward actually change.'],
  ['화면의 다리는 완료 표시를 꾸민 그림만이 아닙니다.','The bridge is more than decorative completion artwork.'],
  ['충돌을 막던 구간이 열려 캐릭터가 건널 수 있게 만들었습니다.','A blocked collision area opens, allowing the character to cross.'],
  ['이 비교가 증명하는 것은 세계 상태가 바뀐다는 점입니다.','This comparison demonstrates a change in the world state.'],
  ['두 번째가 더 재미있는지는 사람에게 플레이를 맡겨 확인해야 합니다.','Whether the second version is more enjoyable still needs human playtesting.'],
  ['자동 입력으로 성공한 기록을 재미 평가로 바꾸면 안 됩니다.','A successful automated input trace is not an enjoyment rating.']
 ],
 '05':[
  ['돌아오는 길도 확인해 보죠.','Now examine the return journey.'],
  ['처음에는 돌아서 가야 했지만, 다리를 고친 뒤에는 짧은 길이 열립니다.','You initially take a detour, but repairing the bridge opens a shorter route.'],
  ['같은 장소가 다른 의미를 갖게 된 것입니다.','The same location now has a different role.'],
  ['다른 테스트에서는 짧은 길에 물건을 내려놓아야 하는 문을 넣었습니다.','Another test adds a gate on the short route that requires an empty inventory.'],
  ['빨리 돌아갈지, 물건을 유지하며 긴 길을 갈지 선택하게 하죠.','You choose between returning quickly and carrying the item along the longer route.'],
  ['짧은 길이 있다는 사실만으로 선택이 생기는 것은 아닙니다.','The presence of a shortcut alone does not create a decision.'],
  ['무엇을 얻고 무엇을 포기하는지 읽을 수 있어야 합니다.','Players need to understand what they gain and give up.'],
  ['그렇다고 모든 이동을 사건으로 채울 필요는 없습니다.','You do not need an event during every moment of travel.'],
  ['조용히 주변을 보거나 방금 한 일을 돌아볼 시간도 필요할 수 있습니다.','Quiet time can allow players to notice the surroundings or reflect.'],
  ['반복 구간이 어떤 역할을 하는지 먼저 정해 보세요.','First decide what purpose a repeated stretch should serve.']
 ],
 '06':[
  ['새 퀘스트를 만들 때는 목표 문장 아래 세 줄을 더 적어 보세요.','When designing a quest, add three lines beneath its objective.'],
  ['갈 때 하는 선택, 끝난 뒤의 변화, 돌아올 때 얻는 정보입니다.','List choices on the way, changes after the task, and new information on return.'],
  ['전부 비어 있다면 부탁 횟수를 늘리기 전에,','If all three are empty, before adding more requests,'],
  ['딱 한 구간을 골라 작은 변화를 넣어 보세요.','introduce a small change in one stretch of the journey.'],
  ['그리고 플레이한 사람에게 어디서 멈췄고 어떤 길을 골랐는지 물어보세요.','Ask players where they paused and which route they chose.'],
  ['완료한 뒤 무엇이 달라졌다고 생각했는지도 확인합니다.','Check what they thought changed after completion.'],
  ['설계 의도와 실제로 알아본 결과가 다를 수 있기 때문입니다.','Their understanding may differ from your design intent.'],
  ['좋은 심부름은 물건 개수만으로 결정되지 않습니다.','The number of items alone does not determine a good errand.'],
  ['작은 부탁 안에서 플레이어가 하는 선택과,','Examine the decisions players make inside a small request'],
  ['그 선택이 남기는 변화를 함께 설계해 보세요.','alongside the changes those decisions leave behind.']
 ]
};
const titles=[['심부름을 행동으로 보기','Read the Actions Inside an Errand'],['가는 길에 선택이 있는가','Choices Along the Way'],['완료 뒤 무엇이 바뀌는가','Changes After Completion'],['같은 배달, 다른 세계 상태','Same Delivery, Different World State'],['돌아오는 길을 다시 설계하기','Redesign the Return Journey'],['세 질문으로 플레이를 확인하기','Test the Play with Three Questions']];
for(const [lang,index] of [['ko',0],['en',1]])write(path.join(base,`script/narration.${lang}.json`),{title:lang==='ko'?'심부름 퀘스트는 왜 지루할까? | 재미있는 퀘스트 디자인':'Why Are Fetch Quests Boring? | Designing Meaningful Quests',scenes:Object.entries(units).map(([id,pairs],i)=>({id,title:titles[i][index],lines:pairs.map(p=>p[index])}))});
write(path.join(base,'script/caption-units.json'),units);
const file=path.join(base,'project.json'),m=JSON.parse(fs.readFileSync(file,'utf8')),previous=JSON.parse(fs.readFileSync(path.join(root,'projects/deconstruct-analyze-rebuild/project.json'),'utf8'));
m.status='in-production';m.audio.backgroundMusic=previous.audio.backgroundMusic;m.audio.mixStatus='waiting-for-narration-and-timeline';
m.paths.editorAudioMix=`motion-canvas/src/projects/${m.slug}/assets/final-mix.wav`;
m.batch={queue:'production/batches/sakurai-planning-game-design/queue.json',sourceIndex:8,privacy:'private',noPublicSchedule:true,uploadToYouTube:true};
m.reference={url:'https://www.youtube.com/watch?v=IM9P9NIKo10',kind:'concept-research-only',scriptVerbatimReuse:false,sourceVideoOrAudioReuse:false,transcript:'unavailable in visible export; title/topic only, independent structure authored'};
m.approvals={script:'production-authorized-by-2026-10-01-batch-request; original-ko-en-script-authored',voiceSample:'approved-voice-reuse-from-one-button-project-per-batch-request',bgm:'approved-Nimbus-reuse-per-batch-request',final:'pending-human-listening-and-visual-QA',publication:'private-upload-authorized; public publication owned by user',uploadEvidence:'흠 퀄리티 너무 괜찮은데? 업로드까지도 전부 같이 진행시켜줘 비공개로만 해두고 공개는 내가 할게'};
m.channelIntro={...previous.channelIntro,appliedToFinal:false};m.membershipOutro={...previous.membershipOutro,scenePath:`motion-canvas/src/projects/${m.slug}/scenes/membership-outro.tsx`,appliedToFinal:false};
m.editing.gameSelection={review:'projects/meaningful-quests/sources/game-candidates.json',titles:['The Elder Scrolls V: Skyrim','Subnautica'],priorUseChecked:true};
write(file,m);
write(path.join(base,'planning/outline.md'),'# Original production plan\n\nTopic: decisions during travel, visible consequences after delivery, and purpose of the return journey. Original structure and wording; the playlist item is concept research only. No source transcript was available in the visible export.\n\n1. Two fresh games and the delivery premise.\n2. Subnautica gathering and oxygen decisions, explicitly a self-directed goal.\n3. Skyrim travel/mining as action illustration, not evidence of a named quest reward.\n4. Original equal-speed/equal-items/equal-score prototype: score-only versus real bridge collision change.\n5. Return route and empty-inventory gate tradeoff; quiet travel can have a purpose.\n6. Observe choices and perceived changes with human testers. Automated input logs verify mechanics only.\n\nEach chapter has one independent Motion Canvas scene. Body-wide actual footage target 60:40; source intervals distinct, normal speed, no loops. Audio, visuals and subtitle timing will be measured after synthesis.\n');
