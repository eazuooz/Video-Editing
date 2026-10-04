const fs=require('fs'),path=require('path'),cp=require('child_process');
const root=path.resolve(__dirname,'../../../..'),p='projects/avoid-game-comparisons';
const gate=cp.spawnSync(process.execPath,['scripts/review-video-duplicates.cjs','avoid-game-comparisons','--check'],{cwd:root,encoding:'utf8',windowsHide:true});
if(gate.status!==0)throw Error(gate.stdout+gate.stderr);
for(const lang of ['ko','en'])if(fs.existsSync(path.join(root,p+'/script/narration.'+lang+'.json')))throw Error('Preserve existing full script; explicit revision needed.');
const rows=[
 ['01','전체 내용 안내','What this video will help you explain',[
  ['아직 없는 게임을 설명할 때, 익숙한 작품 이름만으로 같은 그림을 떠올리게 할 수 있을까요?','When describing a game that does not exist yet, can a familiar title make everyone picture the same thing?'],
  ['페퍼 그라인더의 이동을 동사로 풀고, 플러키 스콰이어의 그림면과 책상을 오가는 행동에서 조건을 구별해 보겠습니다.','We will put Pepper Grinder’s movement into verbs, then distinguish conditions through The Plucky Squire’s actions across illustrated surfaces and a desk.'],
  ['보고 나면 목표와 행동과 조건을 세 문장으로 적고, 듣는 사람의 질문으로 빠진 내용을 찾을 수 있습니다.','By the end, you can write the goal, actions and conditions in three sentences and use a listener’s questions to find what is missing.'],
  ['먼저 노란 지형을 파고 나오는 움직임부터 보죠.','Let us begin by watching the character drill out of yellow terrain.']
 ]],
 ['02','실제 행동 · 파고 나와 다음 공간으로','Actual action: drilling out toward another space',[
  ['캐릭터가 노란 지형 안에서 방향을 바꾸고, 밖으로 나와 공중으로 이동합니다. 길 사이의 가시와 떨어진 지형도 보세요.','The character changes direction inside yellow terrain, emerges, and moves through the air. Notice the brambles between routes and the separated pieces of terrain.'],
  ['갈고리에 매달리거나 대포에서 발사되는 컷은 다른 이동입니다. 전부 달리기라고 묶으면 무엇을 하는지 놓치기 쉽죠.','Hanging from a hook and launching from a cannon are different kinds of movement. Calling all of it running can hide what the character actually does.'],
  ['어두운 굴에서는 낮은 길을 따라 휘어 들어갔다가 다시 공중으로 나옵니다. 먼저 동사와 그 행동이 일어나는 공간을 적어 보세요.','In the dark cave, the character curves along a low passage and emerges into the air again. Start by writing the action verbs and the spaces where those actions happen.'],
  ['여기서는 보인 움직임을 설명합니다. 정확한 버튼이나 모든 지형의 규칙까지 이 짧은 시연으로 정하지는 않습니다.','Here we are describing visible movement. This short demonstration does not establish the exact buttons or the rules for every kind of terrain.']
 ]],
 ['03','같은 작품명, 다른 머릿속 장면','One title can suggest different scenes',[
  ['새 기획을 익숙한 작품과 비슷하다고만 소개하면, 듣는 사람은 자신이 기억한 부분부터 채웁니다.','If a new concept is introduced only as being like a familiar game, listeners fill in the gaps with the parts they remember.'],
  ['가상의 두 청자를 떠올려 보죠. 한 사람은 장애물을 넘는 이동을, 다른 사람은 적과 싸우는 장면을 먼저 생각할 수 있습니다.','Imagine two hypothetical listeners. One might picture movement over obstacles, while the other first pictures fighting enemies.'],
  ['이는 실제 이용자 조사 결과가 아니라 설명 연습입니다. 같은 이름을 들었다고 같은 행동을 떠올렸다고 가정하지 않는 거죠.','This is an explanation exercise, not a result from a user study. We are avoiding the assumption that hearing the same title means picturing the same actions.'],
  ['비교를 썼다면 어떤 부분을 가리키는지 이어서 말하세요. 그래야 아직 만들지 않은 나머지 규칙을 상대가 대신 결정하지 않습니다.','If you use a comparison, say which part you mean. That helps prevent the listener from supplying the rest of your unbuilt game’s rules.']
 ]],
 ['04','실제 행동 · 그림면과 책상을 오가기','Actual action: moving across pictures and a desk',[
  ['이번에는 플러키 스콰이어입니다. 책의 그림면에서 걷고, 책 사이의 틈을 건너는 행동부터 보세요.','Now watch The Plucky Squire. Begin with walking on an illustrated book surface and crossing a gap between books.'],
  ['초록색 진입 지점을 지나면 책상 위의 입체 공간으로 나옵니다. 이어 다른 컷에서는 책상과 인쇄된 문이 있는 그림면을 오갑니다.','Passing through a green entry point brings the character onto the three-dimensional desk. Another shot shows movement between the desk and a pictured surface with printed doors.'],
  ['컵의 진입 지점에 다가가 인쇄면 안으로 들어가는 장면도 있습니다. 그 면에서 나와 책상에 나타나는 과정도 따로 보죠.','There is also a sequence of approaching an entry point on a cup and entering its printed surface. Separately, watch the character leave that surface and appear on the desk.'],
  ['단순히 이차원과 삼차원이 섞였다고 하면 어디에 들어가 무엇을 하는지 빠집니다. 이동하는 면과 진입 지점을 함께 말해야 하죠.','Saying only that the game mixes two and three dimensions leaves out where the character enters and what happens there. Describe the surface and the entry point together.'],
  ['화면 밖의 실물 광고가 아니라 게임 안의 책상입니다. 지금 설명의 근거는 그 가상 공간에서 실제로 보인 행동입니다.','This is a desk inside the game, rather than a live-action advertisement outside it. The explanation is based on actions visibly performed in that virtual space.']
 ]],
 ['05','어디서, 무엇을, 어떤 변화까지','Where, what action, and what visible change',[
  ['설명을 쓸 때는 공간, 동사, 눈에 보이는 변화를 이어 보세요. 책상에서 진입 지점으로 다가가 인쇄면 안으로 들어간다는 식입니다.','When writing the explanation, connect the space, the action verb and the visible change: approaching an entry point on the desk and entering a printed surface, for example.'],
  ['재미있는 이동이라는 표현 옆에 이 한 문장을 붙이면, 상대가 상상할 행동이 구체적이 됩니다.','Adding this sentence next to a phrase like enjoyable movement gives the listener a more concrete action to picture.'],
  ['게임 이름과 장르는 배경을 알려 줄 수 있습니다. 새 기획의 핵심 행동을 전달할 자리는 직접 쓴 문장으로 채우세요.','A title or genre can provide context. Use your own sentence to convey the central action of the new concept.']
 ]],
 ['06','실제 행동 · 같은 이동에도 조건이 있다','Actual action: movement has conditions',[
  ['다시 페퍼의 물가와 용암 위 길을 봅시다. 걷는 다리, 굽은 지형, 탄성 있는 보라색 면은 공간과 움직임이 서로 다릅니다.','Return to Pepper’s waterside and routes above lava. A walkable bridge, curved terrain and an elastic purple surface show different spaces and movements.'],
  ['기울어진 길이나 나무 지지대 옆의 얼음 면처럼, 어디에서 움직이는지 붙이면 설명할 범위가 좁혀집니다.','Specifying where the movement happens, such as a sloping route or an ice surface beside wooden braces, narrows what your explanation covers.'],
  ['플러키의 로켓 이동에서는 실타래와 카드의 윗면 사이로 올라가고, 적을 때린 뒤 벽의 진입 지점으로 다가갑니다.','During Plucky’s rocket movement, the character rises among spool tops and card ledges, strikes enemies, and approaches an entry point on a wall.'],
  ['컵 안으로 내려갔다가 빛나는 물체 쪽을 지나 다시 올라오는 모습도 보세요. 상승과 하강, 닿는 공간을 따로 적을 수 있죠.','Also watch the character descend into a mug, pass a glowing object, and rise again. You can describe ascent, descent and the spaces reached separately.'],
  ['이 관찰만으로 무제한 비행이나 연료 충전 규칙을 확정하지는 않습니다. 보인 조건과 더 확인할 질문을 나눠 둡니다.','These observations do not establish unlimited flight or a fuel-refill rule. Keep visible conditions separate from questions that need further checking.']
 ]],
 ['07','보인 사실과 결정할 조건을 나누기','Separate observations from decisions to make',[
  ['새 기획에서는 진입할 수 있는 지점을 어떻게 알릴지, 같은 행동을 언제 다시 할 수 있을지 결정해야 합니다.','For a new concept, decide how entry points will be indicated and when an action can be performed again.'],
  ['시연에서 보인 사실 옆에 이런 질문을 따로 적으세요. 제한 시간이나 비용은 여기서 제안하는 설계 질문입니다.','Write these questions beside the observed facts, in a separate place. A time limit or a cost is a design question we are proposing here.'],
  ['참고 작품이 그러할 거라는 기억으로 빈칸을 메우면, 아직 정하지 않은 규칙이 확정된 것처럼 전달됩니다.','Filling a gap with a remembered assumption about a reference game can make an undecided rule sound settled.'],
  ['확인한 조건은 설명하고, 미정인 조건은 질문으로 남기세요. 상대도 어디에 의견을 보태야 할지 알 수 있습니다.','Explain the conditions you have established, and leave undecided ones as questions. That also shows the listener where their input is needed.']
 ]],
 ['08','실제 행동 · 이동과 진입과 전투 구별하기','Actual action: distinguish movement, entry and combat',[
  ['책상 위에서는 적에게 다가가 공격하고 물체를 던집니다. 공간을 이동하는 설명과 적을 상대하는 설명은 같은 문장이 아니죠.','On the desk, the character approaches and attacks enemies and throws an object. Describing movement through the space is not the same as describing how enemies are confronted.'],
  ['파란 인쇄면 안에서는 뛰면서 적을 때립니다. 책상 위와는 행동이 놓이는 면이 달라졌습니다.','Inside the blue printed surface, the character jumps and strikes enemies. The surface on which the action takes place has changed from the desk.'],
  ['큰 원통의 진입 지점에 다가가 그림면으로 들어가는 과정은 또 별도의 행동입니다. 진입과 그 뒤의 전투를 구별해 보세요.','Approaching an entry point on a large cylinder and entering its picture is another action. Distinguish entry from combat that follows it.'],
  ['어디서 무엇을 하는지 한 문장씩 붙이면, 차원이 바뀐다는 말에 숨었던 차이가 드러납니다.','Adding a sentence for what happens in each space reveals differences hidden by the phrase changing dimensions.']
 ]],
 ['09','목표, 행동과 조건, 연결의 세 문장','Three sentences: goal, action and conditions, connection',[
  ['이제 새 기획을 세 문장으로 적어 봅시다. 첫 문장은 플레이어가 이루려는 목표, 두 번째는 반복할 행동과 핵심 조건입니다.','Now write a new concept in three sentences. The first gives the player’s goal; the second gives the repeated action and its central conditions.'],
  ['세 번째에는 그 행동이 다른 행동으로 어떻게 이어지는지 씁니다. 다음은 본 장면을 이용한 우리 설명 연습입니다.','The third explains how that action connects to another. The following is our explanation exercise using the scenes we have watched.'],
  ['목표는 다음 발판에 도달하는 것. 부드러운 지형 안에서 길을 따라 파고 이동하는 것. 지형 밖으로 나온 뒤 공중 이동으로 다음 공간에 이어지는 것.','The goal is to reach the next platform. The action is drilling along a route inside soft terrain. Emerging from that terrain connects the action to moving through the air toward another space.'],
  ['이는 개발사의 실제 기획서나 게임 전체 목표를 재현한 문장이 아닙니다. 자신의 기획에서는 목표와 가능한 조건을 직접 정해 같은 틀에 적으세요.','These sentences do not reproduce the developer’s design document or establish the game’s overall goal. For your own concept, decide the goal and permitted conditions and write them in the same structure.']
 ]],
 ['10','실제 행동 · 컷을 넘어 규칙을 만들지 않기','Actual action: do not invent rules across edits',[
  ['글자가 바뀌며 밝기가 달라지는 그림면, 색 공을 맞추는 장면, 전투는 서로 다른 행동입니다. 다음 컷이 앞 행동의 결과라고 자동으로 연결하지 마세요.','A pictured surface where a word and lighting change, matching colored balls, and combat are different actions. Do not automatically treat the next edited shot as the result of the previous action.'],
  ['페퍼의 물 위 탈것도 평평한 물을 지나는 컷과 파도 위로 뜨는 컷이 나뉩니다. 이 편집만으로 한 번의 연속 추격이라고 설명할 수는 없죠.','Pepper’s water vehicle also appears in separate shots: traveling over flat water and rising over waves. This edit alone does not establish one continuous chase.'],
  ['원통 그림면의 사격은 땅에서 움직이는 부분과 공중의 공격이 따로 이어집니다. 지금은 각각의 움직임과 다가오는 대상을 관찰합니다.','Shooting on the cylinder’s picture includes ground movement and airborne attacks in separate sections. Here we observe each movement and the approaching targets.'],
  ['도움 기능을 소개하는 공식 자료도 포함했습니다. 그 화면을 기본 난이도나 모든 진입 지점의 표시 규칙으로 옮기지는 않습니다.','Some footage comes from an official presentation of assistance features. We do not turn that presentation into a claim about default difficulty or how every entry point is shown.'],
  ['새 기획의 문장을 읽으며 화면에서 확인한 부분과 우리가 정할 부분을 다시 나눠 보세요. 비교 대상이 대신 약속하게 두지 않는 겁니다.','As you read the sentences for your new concept, separate what the footage establishes from what you will decide. Do not let the reference make those promises for you.']
 ]],
 ['11','되말하기로 빠진 내용을 찾기','Use restatement to find what is missing',[
  ['설명을 들은 사람에게 처음 무엇을 할지 자기 말로 이야기해 달라고 하세요. 작품 이름을 맞히는 질문보다 전달된 행동을 확인하는 질문입니다.','Ask the listener to describe, in their own words, what they would do first. The question checks the action you conveyed rather than asking them to identify a reference title.'],
  ['가상의 답이 아무 벽에나 들어간다라면, 진입 지점의 조건이 빠졌는지 살펴봅니다. 이 되말하기 역시 우리가 제안하는 확인 방법입니다.','If a hypothetical answer is entering any wall, check whether the condition about entry points was missing. Restatement is a checking method we are proposing.'],
  ['목표와 동작은 같게 이해했는지, 미정인 조건은 무엇인지 확인하고 필요한 문장만 보완하세요. 상대의 질문이 기획을 구체화할 자리를 알려 줍니다.','Check whether the goal and actions were understood as intended, identify undecided conditions, and clarify the necessary sentences. The listener’s questions show where the concept needs more detail.']
 ]],
 ['12','실제 행동으로 설명을 마지막 점검하기','A final check against visible actions',[
  ['마지막 장면도 동사로 읽어 보죠. 그림면에서는 싸우고 계단을 오르고, 책상에서는 길을 따라 걷거나 로켓으로 올라갑니다.','Read these last scenes as action verbs too. On pictured surfaces, the character fights and climbs stairs; on the desk, the character follows a route or rises with a rocket.'],
  ['페퍼는 대포에서 발사되고, 큰 장치 안으로 들어갑니다. 이어 다른 컷의 장치는 움직이며 발사합니다. 들어가는 비용이나 승리 조건은 이 장면으로 정하지 않습니다.','Pepper launches from cannons and enters a large device. In other shots, the device moves and fires. These scenes do not establish the entry cost or a victory condition.'],
  ['행동이 달라지면 설명할 목표와 조건도 다시 살펴봐야 합니다. 익숙한 작품 하나를 떠올리는 것만으로 이 차이가 전달되지는 않죠.','When the action changes, reconsider the goal and conditions you need to explain. Recalling one familiar title does not by itself communicate these differences.'],
  ['자신의 새 기획도 목표, 행동과 조건, 다음 행동과의 연결을 세 문장으로 적어 보세요. 비교를 덧붙이더라도 핵심 행동을 직접 설명합니다.','Write your own new concept as three sentences: the goal, the action and its conditions, and the connection to another action. Even if you add a comparison, explain the central actions directly.'],
  ['그 뒤 듣는 사람의 되말하기에서 빠진 조건을 찾으세요. 같은 이름을 아는지보다, 같은 행동을 이해했는지 확인하는 겁니다.','Then use the listener’s restatement to find missing conditions. Check whether the same actions were understood, beyond whether both people know the same title.']
 ]]
];
fs.mkdirSync(path.join(root,p+'/script'),{recursive:true});
const titles={ko:'게임 기획 설명법: 작품명 대신 목표·행동·조건을 전달하기',en:'Explaining a Game Concept: Goals, Actions and Conditions Beyond Comparisons'};
for(const [lang,column] of [['ko',0],['en',1]])fs.writeFileSync(path.join(root,p+'/script/narration.'+lang+'.json'),JSON.stringify({title:titles[lang],scenes:rows.map(([id,ko,en,lines])=>({id,title:lang==='ko'?ko:en,lines:lines.map(x=>x[column])}))},null,2)+'\n');
console.log(JSON.stringify({scenes:rows.length,paragraphs:rows.reduce((a,c)=>a+c[3].length,0),koCharacters:rows.flatMap(c=>c[3]).reduce((a,l)=>a+l[0].length,0),currentDuplicateGatePassed:true,ttsStarted:false,scenesCreated:false}));
