// One-time editorial revision after reviewing existing-game source footage.
// Keeps the pre-policy draft and all v1 audio; does not synthesize or render.
const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const base = path.resolve(__dirname, '..'), root = path.resolve(base, '../..');
const read = p => JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const write = (p,x) => fs.writeFileSync(path.join(root,p),JSON.stringify(x,null,2)+'\n');
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const baseline = path.join(__dirname,'existing-game-replan/baseline');
if (fs.existsSync(baseline)) throw Error('Baseline exists; do not overwrite current editorial work by rerunning.');
fs.mkdirSync(baseline,{recursive:true});
for (const p of ['project.json','script/draft-bilingual.json','script/narration.ko.json','script/narration.en.json','planning/action-map.json','production/voice-approval.json']) {
  const dst=path.join(baseline,p);fs.mkdirSync(path.dirname(dst),{recursive:true});fs.copyFileSync(path.join(base,p),dst);
}
const d=read('projects/picking-sides/script/draft-bilingual.json');
const old=structuredClone(d), stamp=new Date().toISOString();
const lines={
 '01':[
 ['여러 동물이 한꺼번에 뛰고 있습니다. 얼티밋 치킨 호스의 이 장면에서, 여러분은 지금 누구를 보고 있나요?', 'Several animals are jumping at once. In this Ultimate Chicken Horse clip, who are you watching?'],
 ['닭을 골라 따라가 보면 질문이 구체적으로 바뀝니다. 움직이는 톱날을 피할까? 다음 발판에 닿을까? 같은 화면에서도 눈이 찾는 행동이 달라집니다.', 'Follow the chicken and the questions become concrete. Will it avoid the moving saw and reach the next platform? The same view offers different actions to look for.'],
 ['이번에는 갱 비스트입니다. 붙잡고 매달리는 여러 몸체 중 하나를 고르면, 그 캐릭터의 손이 어디에 남아 있는지부터 살펴보게 됩니다.', 'Now watch Gang Beasts. Choose one of the bodies grabbing and hanging on, and look for where that character is still holding.'],
 ['예고편의 짧은 장면들은 서로 다른 상황입니다. 경기 전체의 승패를 상상하기 전에, 지금 보이는 행동부터 따라가 보겠습니다.', 'These short trailer shots show different situations. Follow the visible action before inferring the result of a whole match.'],
 ['이어지는 것은 개발사가 공개한 초기 트럭 맵 플레이입니다. 양쪽 트럭 위에서 캐릭터들이 이동하고 붙잡습니다. 마음속으로 한 명을 골라보세요.', 'Next is the developer’s early truck-level gameplay. Characters move and grapple on two trucks. Pick one to follow in your mind.'],
 ['바라보는 대상을 정했다고 경기 규칙이 달라지지는 않습니다. 달라지는 것은 내가 먼저 찾는 움직임과, 그다음에 궁금해지는 일입니다.', 'Choosing whom to watch does not change the rules. It changes which movement you look for first and what you want to see happen next.'],
 ['오늘은 이 두 실제 게임의 플레이를 보며, 누구인지 알아보는 단서와 응원할 이유, 그리고 중요한 순간을 읽게 만드는 화면을 나누어 살펴보겠습니다.', 'Using footage from these two actual games, we will separate recognition cues, a reason to care, and a view that makes important moments readable.']
 ],
 '03':[
 ['개발팀의 얼티밋 치킨 호스 플레이를 보겠습니다. 로봇 옷을 입은 원숭이와 모자를 쓴 토끼는 몸의 모양부터 다릅니다. 점프하는 동안에도 그 차이를 찾아보세요.', 'Watch this Ultimate Chicken Horse developer recording. A robot-costumed monkey and a rabbit wearing a hat differ in shape. Look for those differences as they jump.'],
 ['같은 높이에 모였다가 서로 다른 발판으로 흩어져도, 외형은 같은 동물을 다시 찾는 단서가 됩니다. 화면 속 위치만 기억하면 금방 헷갈릴 수 있습니다.', 'Appearance helps you find the same animal after the group separates toward different platforms. Remembering only its screen position can become confusing.'],
 ['이번에는 갱 비스트의 트럭 장면입니다. 이 초기 버전의 캐릭터들은 몸체 모양이 비슷하고 색이 다릅니다. 하늘색 캐릭터를 정해 따라가 보세요.', 'Now watch the Gang Beasts truck level. In this early version, the bodies have similar shapes but different colors. Follow the cyan character.'],
 ['다른 캐릭터와 가까워지고 카메라가 돌아가면, 아까 왼쪽에 있었다는 기억만으로 찾기는 어렵습니다. 지금 어느 트럭에서 누구와 붙잡고 있는지 함께 봐야 합니다.', 'As characters approach each other and the camera turns, remembering the left side is not enough. Also track which truck and which nearby character connect to the participant.'],
 ['몸이 지붕 아래로 내려가도 바로 장면이 끝난 것은 아닙니다. 손이 가장자리에 남아 있는지 보세요. 이름표를 읽는 일과 행동을 끝까지 따라가는 일은 다릅니다.', 'A body moving below the roof does not immediately end the action. Look for a hand still at the edge. Reading an identity and following its action are different tasks.'],
 ['두 게임의 캐릭터를 똑같은 조건으로 실험한 것은 아닙니다. 하나에서는 외형을, 다른 장면에서는 색과 주변 위치를 단서로 관찰하고 있습니다.', 'This is not a controlled comparison between the games. We are observing appearance in one and color plus surrounding positions in another.'],
 ['작은 화면이나 여러 명이 겹치는 순간에도 같은 대상을 찾을 수 있는지 점검해 보세요. 표시를 더한다면, 실제 몸체와 함께 읽히는 단서여야 합니다.', 'Check whether the same participant remains identifiable on a small screen or in a crowd. Any added marker should be readable together with the moving body.']
 ],
 '05':[
 ['갱 비스트의 창문 청소 발판 장면입니다. 빨간 캐릭터와 노란 캐릭터 중 한 명을 골라 보세요. 지금 발판 위에 있는 쪽과 아래에 매달린 쪽의 다음 행동은 다릅니다.', 'On the window-cleaning scaffold in Gang Beasts, choose red or yellow. Standing on the platform and hanging below it lead to different immediate actions.'],
 ['노란 쪽을 따라가면 다시 올라올 수 있을지가 궁금하고, 빨간 쪽을 따라가면 붙잡고 있는 자세를 유지할 수 있을지가 궁금해집니다. 같은 화면에서도 관심의 질문이 달라집니다.', 'Following yellow can raise the question of getting back up; following red can raise the question of maintaining its grip. The same view supports different questions.'],
 ['이제 트럭 위의 다른 시도를 보겠습니다. 하늘색과 노란 캐릭터가 가까워지고, 초록 캐릭터도 옆에서 움직입니다. 먼저 선택한 한 명의 손과 몸을 찾아보세요.', 'Now watch another attempt on the trucks. Cyan and yellow come together while green moves nearby. Look first for the hands and body of the participant you chose.'],
 ['붙잡혀 기울어지는 순간에는 떨어지지 않았으면 좋겠다는 기대가 생길 수 있습니다. 긴 인물 소개 없이도 지금 보이는 자세가 다음 행동을 궁금하게 만드는 단서가 됩니다.', 'A body tilting while held can give a viewer a reason to hope it stays aboard. The visible posture offers a question about the next move without a long character biography.'],
 ['계속 같은 캐릭터를 봐도 되고, 다른 쪽으로 관심을 옮겨도 됩니다. 여기서 말하는 선택은 영상 속에 새 기능을 넣는 것이 아니라, 관전자가 누구의 행동을 따라볼지 정하는 일입니다.', 'You can keep following the same character or shift attention. This choice means deciding whose action to follow; we are not adding a new feature to the recorded game.'],
 ['움직임 하나만 보고 이 선수는 항상 용감하다거나 소극적이라고 단정하지는 마세요. 지금 화면에서 확인한 행동과 사람의 성격은 다른 정보입니다.', 'Do not label a player permanently brave or cautious from one movement. A visible action and a person’s character are different kinds of information.'],
 ['이렇게 작은 기대가 생길 여지는 화면에서 관찰할 수 있습니다. 하지만 사람들이 실제로 더 재미있어하는지는 직접 보여 주고 확인해야 합니다.', 'The view can provide room for a small expectation. Whether people actually enjoy watching more still needs to be checked with viewers.']
 ],
 '07':[
 ['다시 창문 청소용 발판입니다. 몸이 아래로 내려가도 가장자리를 잡은 손은 아직 남아 있습니다. 캐릭터만 보지 말고, 손과 발판의 관계를 함께 보세요.', 'Return to the window-cleaning scaffold. A body can hang below while a hand remains attached to the edge. Watch the relationship between the hand and platform.'],
 ['아래의 빈 공간이 함께 보이니 무엇을 버티는지도 읽힙니다. 지금 응원하는 대상에게 중요한 정보는 복잡한 통계보다 붙잡은 손과 다음 발 디딜 자리일 수 있습니다.', 'The open space below makes the danger legible. A gripping hand and the next foothold may matter more to this moment than a large set of statistics.'],
 ['얼티밋 치킨 호스의 초기 플레이 자료로 옮겨보죠. 움직이는 톱날과 닭의 점프를 함께 봅니다. 출발한 곳과 착지할 발판 사이에 위험이 있습니다.', 'Switch to early Ultimate Chicken Horse gameplay. Watch the moving saw alongside the chicken’s jump. The danger lies between takeoff and the next platform.'],
 ['뒤의 다른 시도에서는 말이 움직입니다. 컷이 바뀌면 다른 시도일 수 있으므로, 닭의 점프가 말의 결과로 이어진 것처럼 설명하면 안 됩니다.', 'The horse moves in another attempt. A cut can switch attempts, so the horse’s outcome should not be described as the continuation of the chicken’s jump.'],
 ['트럭 장면에서는 같은 관계가 옆면에서 드러납니다. 지붕 위와 매달린 몸, 아래쪽 도로를 함께 보면 왜 그 손을 놓치면 안 되는지 이해하기 쉽습니다.', 'The same relationship appears at the side of a truck. Seeing the roof, hanging body and road below helps explain why that grip matters.'],
 ['다른 시도에서 다시 지붕 위로 모이면 볼 지점도 바뀝니다. 누가 누구를 잡는지, 몸이 어느 가장자리로 움직이는지 따라가 보세요.', 'When another attempt brings the characters together on the roof, the useful focus changes. Follow who is holding whom and which edge the bodies approach.'],
 ['너무 가까이 자르면 다음 공간을 잃고, 너무 멀어지면 손과 몸을 놓칠 수 있습니다. 대상과 바로 앞의 위험이 같은 화면에서 연결되는지 확인해 보세요.', 'A tight crop can lose the next space, while a very wide view can lose hands and bodies. Check whether the participant and immediate risk remain connected in the view.']
 ],
 '09':[
 ['이번에는 얼티밋 치킨 호스의 우주 배경 플레이입니다. 움직이는 동물을 한 마리 골라보세요. 불꽃을 내며 떠오르는 몸과 주변의 바위를 함께 따라가겠습니다.', 'In this space-themed Ultimate Chicken Horse gameplay, choose a moving animal. Follow its rising body, propulsion flames and nearby rocks together.'],
 ['여러 동물의 위치가 벌어지면 화면 구도도 달라집니다. 전체 공간이 보이는 것과, 내가 보던 동물이 어디인지 바로 찾는 것은 같은 문제가 아닙니다.', 'The framing changes as the animals spread apart. Seeing the overall space and quickly finding the animal you were following are different tasks.'],
 ['다음 장면에서도 같은 외형을 다시 찾아보세요. 아까 화면 가운데에 있었다고 계속 가운데만 보면, 다른 동물을 따라가게 될 수 있습니다.', 'Look for the same appearance in the next view. Watching only the center because the animal was there earlier can make you follow someone else.'],
 ['발 아래의 불꽃과 가까운 바위는 움직임의 방향을 읽는 단서입니다. 대상을 알아본 다음에는 어디로 가는지, 다음에 무엇과 마주치는지를 봐야 합니다.', 'Flames beneath the feet and nearby rocks help reveal movement direction. After recognizing the participant, read where it is going and what it will encounter next.'],
 ['깃발 주변으로 다가가는 시도와 아래에서 다시 올라오는 시도를 나누어 봅니다. 이 자료에도 편집된 전환이 있어, 서로 다른 시도를 한 번의 긴 비행처럼 말하지 않겠습니다.', 'Distinguish an approach to the flag from an attempt rising from below. The source includes edits, so separate attempts should not become one supposedly continuous flight.'],
 ['여기서는 화면에 나타난 이동과 구도를 관찰하고 있습니다. 내부 카메라 계산식을 알거나, 이 방식이 모든 관전자에게 최선이라고 확인한 것은 아닙니다.', 'We are observing the displayed movement and framing. This does not reveal the internal camera algorithm or establish the best view for every spectator.'],
 ['여러분의 관전 화면에서도 구도가 달라질 때마다 응원 대상을 다시 찾을 수 있는지 보세요. 보기 좋은 장면과 다음 행동을 놓치지 않는 장면을 함께 고민해야 합니다.', 'In your spectator view, check whether the chosen participant can be found after a framing change. Attractive composition should still preserve the next action worth watching.']
 ],
 '11':[
 ['마지막으로 트럭 위의 하늘색과 노란 캐릭터를 보겠습니다. 둘이 붙잡고, 한쪽 몸이 기울고, 다시 거리가 벌어지는 흐름을 이어서 따라가 보세요.', 'Finally, watch cyan and yellow on the truck. Follow the sequence of grappling, a body tilting, and the distance between them changing.'],
 ['서 있던 위치만으로 결과를 미리 정하면 곤란합니다. 넘어졌다가 몸을 세우기도 하고, 지붕 아래로 내려간 뒤에도 손이 남아 있기도 합니다.', 'The standing position alone does not settle the outcome. A character may rise after falling over or keep a hand attached after moving below the roof.'],
 ['가장자리에서 둘의 몸이 함께 내려갈 때는, 어떤 접촉이 이어지는지 끝까지 봐야 합니다. 응원한 쪽의 이름만 크게 띄워서는 이 과정이 전달되지 않습니다.', 'When both bodies descend at the edge, follow which contacts remain. A large label for the favored participant cannot communicate that process by itself.'],
 ['이어서 창문 청소 발판의 다른 장면을 보겠습니다. 매달린 캐릭터와 발판의 기울기가 바뀝니다. 방금 보여 준 트럭 경기의 다음 순간은 아닙니다.', 'Next comes a different scaffold scene. The hanging characters and platform angle change. This is not the next moment of the truck attempt.'],
 ['빨간 캐릭터를 끝까지 따라가 보세요. 손이 남아 있는 순간과 몸이 아래로 떨어지는 순간을 구분하면, 지금 보인 결과가 어떤 행동에서 나왔는지 연결할 수 있습니다.', 'Follow the red character through the shot. Distinguishing a remaining grip from a falling body connects the visible outcome with the action that produced it.'],
 ['이 짧은 개발 자료에는 전체 경기의 최종 승자를 확인할 결과 화면이 없습니다. 그래서 여기서는 보인 낙하와 시도만 설명하고, 확인하지 않은 승패는 덧붙이지 않겠습니다.', 'These short development excerpts do not provide a final match-results screen. We describe the attempts and falls shown without inventing an unverified winner.'],
 ['관전자가 고른 대상, 그 대상이 시도한 행동, 실제로 확인한 결과를 이어 주세요. 크게 응원하라는 문구보다 이 연결이 먼저 읽혀야 합니다.', 'Connect the selected participant, the action attempted and the outcome actually verified. That connection should be readable before adding a large call to cheer.']
 ]
};
for(const s of d.scenes) if(lines[s.id])s.lines=lines[s.id];
// Preserve every explanatory claim; only remove a bridge naming the excluded invented race.
d.scenes.find(s=>s.id==='02').lines[4]=[
 '지금부터 두 게임의 실제 플레이에서 대상을 찾고, 마음속으로 선택하고, 위험과 결과를 읽는 순서로 하나씩 확인해 보겠습니다.',
 'Using actual footage from both games, we will examine finding a participant, choosing one to follow in our minds, and reading risk and outcome.'
];
d.status='existing-game-source-reviewed-pending-v2-tts-and-final-cuts';
d.sourceReviewNotes={at:stamp,policy:'docs/VIDEO_GAME_FOOTAGE_POLICY.md',actualSourcesOnly:true,sourceReview:'projects/picking-sides/production/existing-game-replan/source-review.json',preservedExplanationScenes:['02','04','06','08','10','12'],unchangedExplanationParagraphs:29,changedExplanationBridge:{scene:'02',paragraph:5,reason:'Replace the excluded invented-race bridge with existing-game observation; preserve all three tasks and explanation duration.'},notClaimed:['new game creation','controlled user study','spectator enjoyment improvement','whole-match winners absent from sources','internal camera algorithm']};
write('projects/picking-sides/script/draft-bilingual.json',d);
const oldDir='shared/output/narration/picking-sides/qwen3-1.7b-balanced-v1';
const newDir='shared/output/narration/picking-sides/qwen3-1.7b-balanced-v2';
const reused=[];
for(const id of ['04','06','08','10','12']){
 if(JSON.stringify(old.scenes.find(s=>s.id===id).lines)!==JSON.stringify(d.scenes.find(s=>s.id===id).lines))throw Error('Explanation changed: '+id);
 for(const folder of ['chunks','asr']){
  const name=folder==='chunks'?id+'-scene.wav':id+'.json';
  const from=path.join(root,oldDir,folder,name),to=path.join(root,newDir,folder,name);
  fs.mkdirSync(path.dirname(to),{recursive:true});if(fs.existsSync(to))throw Error('v2 target already exists: '+to);fs.copyFileSync(from,to);
  if(sha(from)!==sha(to))throw Error('Copy mismatch');
  reused.push({scene:id,kind:folder,from:path.relative(root,from).replaceAll('\\','/'),to:path.relative(root,to).replaceAll('\\','/'),sha256:sha(to)});
 }
}
const m=read('projects/picking-sides/project.json');
m.status='production-existing-game-replan';m.tts.outputDir=newDir;m.tts.filenameStem='picking-sides-qwen3-1.7b-balanced-v2';
for(const key of ['narration','captionsKo','captionsEn'])m.paths[key]=m.paths[key].replaceAll('balanced-v1','balanced-v2');
m.approvals.script='existing-game-source-reviewed-v2; final timing/cuts/current-hash ASR pending';m.editing.exampleInterleaving.reviewStatus='v2 source actions and bilingual claims reviewed; final cue and exact cut boundaries pending';
write('projects/picking-sides/project.json',m);
write('projects/picking-sides/production/existing-game-replan/preservation.json',{at:stamp,baseline:path.relative(root,baseline).replaceAll('\\','/'),allPriorFilesPreserved:true,reused,unchangedExplanationParagraphs:29,changedBridge:d.sourceReviewNotes.changedExplanationBridge,minimumRetainedExplanationSeconds:234.64004166666677,explanationDurationFinalCheck:'pending-after-measured-TTS',changedScenes:['01','02','03','05','07','09','11'],newAudioDirectory:newDir,finalVideoReady:false});
console.log('Replanned 12 chapters/72 bilingual paragraphs; preserved 29 explanatory paragraphs and byte-identical audio/ASR for five unchanged chapters.');
