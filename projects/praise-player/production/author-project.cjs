// Original lesson; reference transcript is research only and is not reproduced.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),base=path.dirname(__dirname),slug='praise-player';
const write=(f,v)=>{fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,typeof v==='string'?v:JSON.stringify(v,null,2)+'\n');};
const units={
 '01':[
 ['닌텐도 스위치 스포츠에서는 경기 뒤에 승리 표시와 축하하는 동작이 나옵니다.','Nintendo Switch Sports shows a win banner and a celebration after a match.'],
 ['링 피트 어드벤처에서는 운동 동작과 함께 평가 표시가 이어집니다.','Ring Fit Adventure accompanies exercise movements with evaluation feedback.'],
 ['같은 점수를 받아도, 게임이 내 행동을 알아봐 주면 장면이 달라집니다.','The same score can feel different when a game acknowledges what you did.'],
 ['성공했다는 계산과, 그 성공을 반겨 주는 표현은 구분할 수 있습니다.','We can distinguish calculating success from expressing recognition of that success.'],
 ['오늘은 보상을 더 주는 방법보다, 이미 한 행동을 어떻게 인정할지 살펴보겠습니다.','Today we examine how to recognize an action, rather than how to add rewards.'],
 ['직접 만든 방어 테스트는 두 화면에 같은 입력과 판정을 적용합니다.','Our original defense test applies the same inputs and collision rules to both screens.'],
 ['달라지는 것은 칭찬의 시점, 문구, 크기와 위치입니다.','We change the timing, wording, strength, and position of the praise.'],
 ['재미의 차이는 직접 확인해야 하지만, 무엇을 바꿨는지는 로그로 확인할 수 있습니다.','Enjoyment needs human testing, while logs can verify exactly what changed.']
 ],
 '02':[
 ['먼저 칭찬이 언제 나오는지 비교해 보죠.','First, compare when the praise appears.'],
 ['두 캐릭터는 같은 공격을 같은 순간에 막습니다.','Both characters block the same attack at the same moment.'],
 ['한쪽은 곧바로 반응하고, 다른 쪽은 한참 뒤에 반응합니다.','One side responds promptly; the other responds much later.'],
 ['기다리는 동안 다음 공격이 오면, 어느 행동을 칭찬했는지 연결하기 어렵습니다.','If the next attack arrives during the wait, it is harder to connect praise with the action.'],
 ['그래서 성공 판정과 가까운 순간에 짧은 반응을 붙여 봅니다.','Try attaching a brief response close to the successful collision result.'],
 ['크게 띄우지 않아도, 방금 한 행동을 알아봤다는 신호를 줄 수 있습니다.','The signal can acknowledge the recent action without a large display.'],
 ['모든 게임에 같은 지연 시간을 넣으라는 뜻은 아닙니다.','This does not prescribe one delay for every game.'],
 ['우리 게임의 다음 행동과 겹치는지, 정상 속도로 확인하는 기준입니다.','It is a reason to check overlap with the next action at normal speed.']
 ],
 '03':[
 ['잘했어요라는 말만으로는 무엇을 잘했는지 알기 어렵습니다.','A generic compliment may not explain what went well.'],
 ['이번 테스트는 공격을 막고, 다음 공격은 위로 움직여 피합니다.','This test blocks an attack, then moves upward to dodge the next one.'],
 ['한 화면은 같은 칭찬을 반복하고, 다른 화면은 방어와 회피를 구분합니다.','One screen repeats the same praise; the other distinguishes blocking from dodging.'],
 ['판정이 실제로 확인한 행동을 짧게 적어 주는 것입니다.','A brief label names the action actually verified by the collision rules.'],
 ['버튼을 누르기만 했는데 완벽한 방어라고 하면, 표현과 결과가 어긋납니다.','Calling a button press a perfect block can misrepresent the result.'],
 ['입력 이벤트 대신 성공 판정을 기준으로 문구를 선택해 보세요.','Choose the label from the successful outcome, rather than the input event alone.'],
 ['다음에도 어떤 행동을 해 볼지 스스로 알아볼 수 있는 정보가 됩니다.','That information can help the player identify an action to try again.'],
 ['칭찬이 설명서를 대신할 필요는 없지만, 이유를 숨길 필요도 없습니다.','Praise need not become an instruction manual, but it need not hide its reason.']
 ],
 '04':[
 ['성공할 때마다 가장 큰 축하를 보내면, 특별한 순간이 구분되지 않습니다.','Using the largest celebration for every success removes a distinction between moments.'],
 ['스위치 스포츠의 경기 승리처럼, 마무리에는 넓은 축하 화면이 어울릴 수 있습니다.','A match win in Switch Sports illustrates a broader celebration at a stopping point.'],
 ['하지만 진행 중의 작은 성공마다 같은 크기를 쓰면 다음 상황을 가릴 수 있죠.','The same scale after every small success can cover the next situation.'],
 ['자체 테스트는 한 번의 방어에는 작은 표시를 냅니다.','Our test uses a small marker for a single block.'],
 ['연속 방어가 실제로 확인된 순간에만 조금 더 강한 반응을 냅니다.','A stronger response appears only when a sequence of successful blocks is verified.'],
 ['비교 화면의 점수와 성공 횟수는 같고, 표현의 강도만 다릅니다.','The score and successful-action count stay equal; only presentation strength changes.'],
 ['작은 성공, 이어진 성공, 긴 구간의 완료를 나눠 보세요.','Distinguish an individual success, a sequence, and the completion of a longer section.'],
 ['칭찬의 크기를 플레이어가 실제로 해낸 일에 맞추는 방법입니다.','This aligns the scale of the recognition with the actual accomplishment.']
 ],
 '05':[
 ['실패한 순간에도 무조건 완벽하다고 하면, 칭찬을 믿기 어려워집니다.','Unconditionally calling a failure perfect can undermine trust in the praise.'],
 ['이번에는 같은 입력을 두 화면에 넣고, 한 번의 공격을 일부러 놓칩니다.','Both screens receive the same inputs, deliberately missing one attack.'],
 ['체력도 똑같이 줄어드는데, 한쪽은 여전히 완벽하다는 말을 냅니다.','Health falls equally, but one side still claims the performance was perfect.'],
 ['다른 쪽은 맞았다는 결과를 보여 주고, 앞서 성공한 방어만 인정합니다.','The other side shows the hit and acknowledges only the blocks that actually succeeded.'],
 ['실패를 숨기지 않아도, 그 안에서 해낸 행동을 구체적으로 말할 수 있습니다.','We can name a genuine partial success without hiding the failure.'],
 ['모든 실패에 칭찬을 붙일 필요도 없습니다.','Every failure does not need a compliment.'],
 ['다시 시도할 단서는 따로 보여 주고, 성공과 실패의 신호는 구분하세요.','Show a retry clue separately, and distinguish signals for success and failure.'],
 ['따뜻한 표현도 실제 판정과 연결되어 있어야 다음 시도에 도움이 됩니다.','Supportive wording should remain connected to actual outcomes to inform another attempt.']
 ],
 '06':[
 ['마지막으로 칭찬이 다음 플레이를 방해하지 않는지 확인합니다.','Finally, check whether the praise obstructs the next action.'],
 ['같은 공격 위에 큰 글자를 올리면, 다음 위협을 읽는 자리가 가려집니다.','Large text placed over the attack can cover the area where the next threat must be read.'],
 ['이번 비교는 판정과 문구를 유지하고, 위치와 면적만 바꿨습니다.','This comparison preserves outcomes and wording while changing position and area.'],
 ['행동 가까운 작은 표시와 가장자리의 짧은 반응을 비교해 보세요.','Compare a small marker near the action with a brief response near the edge.'],
 ['움직이는 대상과 필요한 정보를 가리지 않는지 휴대폰 크기에서도 확인합니다.','Check that neither moving targets nor necessary information are obscured at phone size.'],
 ['무엇을 인정하는가, 언제 말하는가, 얼마나 크게 말하는가를 함께 기록하세요.','Record what is recognized, when it is recognized, and how strongly it is expressed.'],
 ['칭찬 횟수만 늘리기보다, 방금 한 행동과 표현이 맞는지 먼저 확인합니다.','Before increasing praise frequency, check whether the expression matches the recent action.'],
 ['플레이어가 내가 해냈다고 느낄 순간을, 우리 게임의 실제 동작에서 찾아보세요.','Look for moments of accomplishment in the actual actions of your own game.']
 ]
};
const titles=[['점수와 성공 인정은 구분된다','Score and Recognition Are Distinct'],['성공과 가까운 순간에 반응하기','Respond Close to the Success'],['실제로 해낸 행동을 말하기','Name the Action That Succeeded'],['성과에 맞는 칭찬의 강도','Match Strength to Accomplishment'],['실패를 숨기지 않는 긍정','Be Supportive Without Hiding Failure'],['다음 행동의 자리를 남기기','Leave Room for the Next Action']];
for(const [lang,index] of [['ko',0],['en',1]])write(path.join(base,`script/narration.${lang}.json`),{title:lang==='ko'?'게임은 왜 플레이어를 칭찬할까? | 성공 피드백 디자인':'Why Games Praise the Player | Designing Success Feedback',scenes:Object.entries(units).map(([id,pairs],i)=>({id,title:titles[i][index],lines:pairs.map(p=>p[index])}))});
write(path.join(base,'script/caption-units.json'),units);
const m=JSON.parse(fs.readFileSync(path.join(base,'project.json'),'utf8')),prior=JSON.parse(fs.readFileSync(path.join(root,'projects/counting-animation-frames/project.json'),'utf8'));
m.status='in-production';m.audio.backgroundMusic=prior.audio.backgroundMusic;m.audio.mixStatus='waiting-for-narration-and-timeline';m.paths.editorAudioMix=`motion-canvas/src/projects/${slug}/assets/final-mix.wav`;
m.batch={queue:'production/batches/sakurai-planning-game-design/queue.json',sourceIndex:11,privacy:'private',noPublicSchedule:true,uploadToYouTube:true};
m.reference={url:'https://www.youtube.com/watch?v=fryDyXROp8A',kind:'concept-research-only',scriptVerbatimReuse:false,sourceVideoOrAudioReuse:false,transcript:'Source concept read from a temporary Japanese transcript; source text and media not copied into production.'};
m.approvals={script:'independent original bilingual lesson under batch-production authorization; content and actual Studio duplicate preflight distinct',voiceSample:'approved same Qwen3-TTS 1.7B reference reuse',bgm:'approved continuous Nimbus reuse',final:'pending actual render, ASR, all-cue visual QA and human listening',publication:'private only; public release belongs to user'};
m.channelIntro={...prior.channelIntro,appliedToFinal:false};m.membershipOutro={...prior.membershipOutro,scenePath:`motion-canvas/src/projects/${slug}/scenes/membership-outro.tsx`,appliedToFinal:false};
m.editing.gameSelection={review:`projects/${slug}/sources/game-candidates.json`,titles:['Nintendo Switch Sports','Ring Fit Adventure'],priorUseChecked:true,status:'New official sources downloaded and reviewed; final exact-cut/public rights review pending'};
m.editing.prototypeComparison='Actual keyboard, projectile collision, block/dodge/hit outcomes; equal game state and reward rules in paired panels; feedback presentation changes only.';
m.publishReady=false;m.warnings=[...prior.warnings];write(path.join(base,'project.json'),m);
write(path.join(base,'planning/outline.md'),'# Original success-recognition lesson\n\nViewer question: how does a game recognize what the player has actually accomplished while preserving the same rewards?\n\n1. Fresh Switch Sports match-win celebration / Ring Fit movement evaluation; distinguish calculation from recognition.\n2. Prompt versus delayed praise after the same actual collision.\n3. Generic versus block/dodge-specific wording from verified outcomes.\n4. Small individual success versus larger verified streak; score and rules equal.\n5. Deliberate miss; dishonest perfect message versus an accurate hit and acknowledgment of real partial success.\n6. Same outcome/message; change overlay position and area to preserve the next threat.\n\nEach chapter has its own Motion Canvas 2.5D scene. Actual gameplay/development 60:40 white explanation, excluding 2-second cat intro and 10-second original membership outro. Normal speed, distinct source intervals, no looping short footage. Subjective enjoyment remains a human playtest question; executable assertions only verify inputs/outcomes/equal state.\n');
const qfile=path.join(root,'production/batches/sakurai-planning-game-design/queue.json'),q=JSON.parse(fs.readFileSync(qfile,'utf8')),item=q.items.find(v=>v.slug===slug);item.checkpoints.script=true;item.checkpoints.originalScript=true;item.localProgress={originalBilingualScript:true,independentScenePlan:6,narration:false,render:false,upload:false};item.updatedAt=new Date().toISOString();fs.writeFileSync(qfile,JSON.stringify(q,null,2)+'\n');
console.log('Original paired captions: '+Object.values(units).reduce((n,v)=>n+v.length,0));
