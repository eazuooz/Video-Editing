// Independently authored teaching structure. Source playlist is concept research only.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),base=path.dirname(__dirname),slug='counting-animation-frames';
const write=(f,v)=>{fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,typeof v==='string'?v:JSON.stringify(v,null,2)+'\n');};
const units={
 '01':[
  ['공격을 조금 더 빠르게 만들어 주세요. 개발할 때 자주 듣는 요청입니다.','Make the attack a little faster. It is a familiar request during development.'],
  ['그런데 준비 자세를 줄일까요, 맞은 뒤 멈춤을 줄일까요?','Should we shorten the preparation, or the pause after impact?'],
  ['메가맨 일레븐의 점프와 몬스터 헌터 라이즈의 공격처럼,','Consider a jump in Mega Man 11 or an attack in Monster Hunter Rise.'],
  ['한 동작 안에도 시작과 변화, 마무리가 있습니다.','One action contains a beginning, a change, and an ending.'],
  ['오늘은 그 느낌을 프레임이라는 시간 눈금으로 옮겨 보겠습니다.','We will translate that feeling into a time scale measured in frames.'],
  ['실제 게임은 동작을 관찰하는 예시이고,','The games illustrate observable motion.'],
  ['정확한 숫자는 직접 만든 프레임 테스트에서 확인합니다.','We will verify exact numbers in an original frame-timing test.'],
  ['그림 장수와 게임의 시간까지 같은 것이라고 생각하면 안 됩니다.','The number of drawings is not necessarily the game’s time scale.']
 ],
 '02':[
  ['프레임 수에는 기준 속도가 필요합니다.','Every frame count needs a reference rate.'],
  ['일 초를 예순 번 나누는 기준에서 열두 프레임은 영 점 이 초입니다.','At sixty steps per second, twelve frames represent zero point two seconds.'],
  ['같은 열두 프레임도 서른 번 나누는 기준에서는 영 점 사 초입니다.','At thirty steps per second, the same twelve frames represent zero point four seconds.'],
  ['숫자가 같아도 실제 기다리는 시간은 두 배가 됩니다.','The count stays the same, but the elapsed time doubles.'],
  ['그래서 이 테스트는 일 초에 예순 번 갱신하는 규칙으로 고정했습니다.','Our test therefore uses a fixed sixty-update-per-second rule.'],
  ['화면에는 시간을 함께 적고, 움직이는 표시로 차이를 보여 줍니다.','It displays elapsed time alongside a moving marker.'],
  ['설계 메모에도 프레임 수와 기준 속도를 한 쌍으로 남기세요.','Record the frame count and its reference rate together in your design notes.'],
  ['렌더링 속도와 게임 규칙의 갱신 속도가 다를 수도 있습니다.','Rendering and game-rule updates can run at different rates.']
 ],
 '03':[
  ['이제 한 번의 공격에서 무엇을 재는지 정해 보죠.','Now decide which part of an attack you are measuring.'],
  ['직접 만든 테스트는 입력을 받은 순간을 영으로 기록합니다.','Our original test records input acceptance as time zero.'],
  ['열두 번의 시간 눈금 뒤에 판정이 시작되고,','The hit area begins after twelve time steps,'],
  ['세 번의 눈금 동안 유지된 다음, 열다섯 번 동안 회복합니다.','stays active for three steps, then recovers for fifteen.'],
  ['전체는 서른 번의 눈금, 영 점 오 초입니다.','The total is thirty steps, or zero point five seconds.'],
  ['빠르게 해 달라는 요청이 준비 시간을 뜻한다면,','If the request for speed concerns preparation,'],
  ['준비만 줄이고 나머지는 그대로 두어 비교할 수 있습니다.','we can shorten that phase and keep the others unchanged.'],
  ['시작과 끝을 어디에 찍었는지도 기록해야 같은 수를 셀 수 있습니다.','Record both boundaries so everyone measures the same interval.'],
  ['다른 게임의 기술 수치를 이 테스트 숫자로 대신 설명하지는 않습니다.','These prototype numbers do not represent move data from another game.']
 ],
 '04':[
  ['그림이 많아지면 판정도 빨라질까요?','Does adding drawings make the hit happen sooner?'],
  ['이번에는 같은 공격에 자세 그림만 다르게 넣었습니다.','We changed only the poses in the same attack.'],
  ['한쪽은 적은 자세를 오래 보여 주고, 다른 쪽은 자주 바꿉니다.','One version holds fewer poses longer; the other changes poses more often.'],
  ['두 버전의 판정은 같은 열두 번째 시간 눈금에 시작합니다.','Both hit areas begin at the same twelfth time step.'],
  ['표현의 부드러움은 달라도 공격을 기다리는 시간은 같습니다.','Their visual smoothness differs, but the wait for the hit is equal.'],
  ['그래서 애니메이션 그림을 넘기는 시계와 판정 시계를 구분합니다.','We distinguish the animation-pose clock from the hit-area clock.'],
  ['그림을 늘리기 전에 어떤 시간을 바꾸려는지 먼저 확인하세요.','Before adding poses, decide which timing you want to change.'],
  ['그림과 판정을 분리했는지는 실제 코드와 로그로 검증했습니다.','The implementation and logs verify that poses and collision timing are separate.']
 ],
 '05':[
  ['맞는 순간 잠깐 멈추는 연출도 살펴보겠습니다.','Next, examine a brief pause at impact.'],
  ['자체 테스트에서는 충돌 뒤 전투 시계만 네 번의 눈금 동안 멈춥니다.','In our test, only the combat clock pauses for four steps after collision.'],
  ['배경의 시간 표시는 계속 움직입니다.','The background time indicator keeps moving.'],
  ['공격 데이터는 서른 눈금 그대로지만,','The attack data still spans thirty combat steps,'],
  ['실제로 끝날 때까지는 멈춘 시간까지 더해집니다.','but the actual completion time also includes the pause.'],
  ['즉, 멈춤이 있는 동작을 볼 때는 어느 시계를 센 것인지 물어봐야 합니다.','When observing a paused action, ask which clock the count refers to.'],
  ['상용 게임의 모든 효과가 이 방식이라는 뜻은 아닙니다.','This does not imply that every commercial game uses this method.'],
  ['우리 게임에서 멈출 대상과 계속 흐를 대상을 명확히 정하는 예시입니다.','It illustrates explicitly choosing what pauses and what continues in our own game.']
 ],
 '06':[
  ['마지막으로 녹화 영상에서 센 프레임은 증거의 한 종류일 뿐입니다.','Finally, frames counted in a recording are only one kind of evidence.'],
  ['그림이 반복되거나 빠지면 게임 내부의 시간을 그대로 읽기 어렵습니다.','Repeated or missing pictures can obscure the game’s internal timing.'],
  ['같은 테스트를 서로 다른 화면 갱신 속도로 보아도,','Even at different display update rates,'],
  ['고정된 판정 시계가 같으면 같은 시간에 판정이 나옵니다.','the same fixed hit-area clock produces the hit at the same elapsed time.'],
  ['처음에는 정상 속도로 보고 길이를 가늠해 보세요.','First, watch at normal speed and estimate the duration.'],
  ['다음에는 입력, 판정 시작, 다음 행동 가능 시점을 기록합니다.','Then record input acceptance, the first active hit, and when another action is allowed.'],
  ['기준 속도와 실제 경과 시간을 함께 확인하면,','Check the reference rate alongside the measured elapsed time'],
  ['조금 빠르게라는 말이 함께 검토할 수 있는 수정안이 됩니다.','to turn a vague request for speed into a change everyone can review.'],
  ['감각으로 먼저 찾고, 측정으로 확인해 보세요.','Find it by feel, then verify it by measurement.']
 ]
};
const titles=[['느낌을 시간으로 옮기기','Turn Feel into Timing'],['프레임 수에는 기준 속도가 필요하다','A Frame Count Needs a Reference Rate'],['동작의 어느 구간을 재는가','Define the Interval You Measure'],['그림 시계와 판정 시계','Pose Clock and Collision Clock'],['멈춤은 어느 시계에 더해지는가','Which Clock Includes the Pause?'],['눈으로 찾고 로그로 확인하기','Observe First, Then Verify with Logs']];
for(const [lang,index] of [['ko',0],['en',1]])write(path.join(base,`script/narration.${lang}.json`),{title:lang==='ko'?'게임 애니메이션 프레임 세기 | 손맛을 시간으로 설계하는 법':'Count Animation Frames | Design Game Feel with Timing',scenes:Object.entries(units).map(([id,pairs],i)=>({id,title:titles[i][index],lines:pairs.map(p=>p[index])}))});
write(path.join(base,'script/caption-units.json'),units);
const m=JSON.parse(fs.readFileSync(path.join(base,'project.json'),'utf8')),prior=JSON.parse(fs.readFileSync(path.join(root,'projects/meaningful-quests/project.json'),'utf8'));
m.status='in-production';m.audio.backgroundMusic=prior.audio.backgroundMusic;m.audio.mixStatus='waiting-for-narration-and-timeline';
m.paths.editorAudioMix=`motion-canvas/src/projects/${slug}/assets/final-mix.wav`;
m.batch={queue:'production/batches/sakurai-planning-game-design/queue.json',sourceIndex:9,privacy:'private',noPublicSchedule:true,uploadToYouTube:true};
m.reference={url:'https://www.youtube.com/watch?v=JZ1Jd0u3b6U',kind:'concept-research-only',scriptVerbatimReuse:false,sourceVideoOrAudioReuse:false,transcript:'Japanese automatic captions read locally for concept research; no transcript copied into repository or narration'};
m.approvals={script:'independent original KO/EN script under batch-production authorization',voiceSample:'approved same Qwen3-TTS 1.7B voice reuse',bgm:'approved same continuous Nimbus reuse',final:'pending actual QA and human final listening',publication:'private upload authorized; user owns public release and scheduling'};
m.channelIntro={...prior.channelIntro,appliedToFinal:false};m.membershipOutro={...prior.membershipOutro,scenePath:`motion-canvas/src/projects/${slug}/scenes/membership-outro.tsx`,appliedToFinal:false};
m.editing.gameSelection={review:`projects/${slug}/sources/game-candidates.json`,titles:['Mega Man 11','Monster Hunter Rise'],priorUseChecked:true,status:'official recording and actual action review in progress; do not assume cleared footage'};
m.publishReady=false;m.warnings=[...prior.warnings];write(path.join(base,'project.json'),m);
write(path.join(base,'planning/outline.md'),'# Independent frame-timing plan\n\nQuestion: how can a vague request for a faster action become a measurable edit?\n\n1. Observe fresh Mega Man 11 / Monster Hunter Rise motion; no unverified move counts.\n2. Count × reference rate: twelve steps at 60/s versus 30/s. Distinguish render and fixed-rule clocks.\n3. Original input-zero intervals: startup [0,12), active [12,15), recovery [15,30). Total 0.5s at 60/s.\n4. Change pose samples only; keep hit timing equal. Real input and separate collision state.\n5. Original four-wall-tick hitpause freezes combat clock, not background clock; no claim of universal commercial implementation.\n6. Compare render rates with the same fixed clock; observe normal speed, then verify engine logs.\n\nSix independent scenes; gameplay/development 60% and original white 2.5D explanation 40% excluding approved intro/outro. Original Frame Timing Lab demonstrates actual controls/collision/state rather than illustrative claims. No loops or source slow-down to meet the ratio.\n');
