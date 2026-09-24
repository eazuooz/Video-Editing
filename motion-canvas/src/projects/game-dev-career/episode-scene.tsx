import {Circle, Line, Node, Rect, Txt, View2D} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';
import {PAPER as P} from '../../styles/research-paper';
import {ChestWorld, ramp} from './preview/chest-world';
import {CaptionBox} from './preview/caption-box';
import board from '../../../../projects/game-dev-career/planning/storyboard.v1.json';
import manifest from '../../../../projects/game-dev-career/project.json';

// Full-episode visual development, not a voiced final. The short review reel
// compresses the shots to 6 seconds each; it is never used as SRT timing.
export function* episodeScene(view: View2D, index: number, reel = false) {
  const s = board.scenes[index], duration = reel ? 6 : s.estimatedSeconds;
  const time = createSignal(0), phase = () => time() / duration;
  const active = () => Math.min(2, Math.floor(phase() * 3));
  view.fill(P.background);
  const root = new Node({opacity: () => ramp(time(), 0, .25) * (1 - ramp(time(), duration - .25, duration))});
  view.add(root);
  const caption = new CaptionBox({y: manifest.editing.captionStyle.centerYPx});
  // A short caption specimen only: no invented narration alignment or SRT.
  const samples = ['게임을 좋아하는데, 이걸로 먹고살 수 있을까요?', '결과는 상자 하나지만, 서로 다른 질문을 해결한 겁니다.',
    '조건과 결과, 예외를 구분해 적는 것이 문서 작성의 기본입니다.', '한 줄 실행한 뒤 무엇이 바뀌었는지 설명해보세요.',
    '증상을 다시 만들고, 상태와 아이템 수를 확인합니다.', '세부 무늬 전에 흑백으로도 형태가 읽히는지 확인해보세요.',
    '게임에 넣을 크기와 방향도 확인해야 합니다.', '무엇을 바꿨고 왜 바꿨는지 남깁니다.', '좋아하는 게임에서 한 걸음 더 나아가 봅시다.'];
  caption.text(samples[index]); view.add(caption);
  root.add(<>
    <Line points={[[-848,-433],[-802,-433]]} stroke={P.blue} lineWidth={5}/>
    <Txt x={-779} y={-433} offset={[-1,0]} text={s.role} fontFamily={P.font} fontSize={23} fontWeight={600} letterSpacing={2} fill={P.blue}/>
    <Txt x={-846} y={-292} offset={[-1,0]} text={s.headline} fontFamily={P.font} fontSize={56} lineHeight={76} fontWeight={700} fill={P.ink}/>
  </>);
  const world = new ChestWorld({x: 440, y: 100, scale: () => .76 + .035 * ramp(phase(), .1, .9)});
  world.clock(time); world.phase(phase);
  world.chapter([0,0,1,2,2,3,4,0,5][index]); root.add(world);

  if (index === 3) {
    root.add(<>
      <Rect x={-490} y={55} width={718} height={275} fill={P.panel}/>
      <Rect x={-498} y={() => -27 + active()*46} width={665} height={42} fill={P.yellow} opacity={.45}/>
      <Txt x={-820} y={-63} offset={[-1,-1]} text={'if (opened || keys == 0) return;\nif (inventory.full()) return;\ninventory.add(reward);\n--keys;\nopened = true;'} fontFamily={P.mono} fontSize={26} lineHeight={46} fill={P.ink}/>
      <Txt x={-840} y={265} offset={[-1,0]} text={() => ['열어도 되는 상태인가?', '아이템을 저장하고', '키와 상자 상태를 갱신'][active()]} fontFamily={P.font} fontSize={31} fill={P.blue}/>
    </>);
  } else if (index === 4) {
    for (let i=0;i<6;i++) root.add(<Rect x={-788+i*103} y={18} width={90} height={80} fill={() => active()===0&&Math.floor(phase()*18)%6===i?P.blue:P.panel} stroke={P.line} lineWidth={1}>
      <Txt text={`${i+1}`} fontFamily={P.mono} fontSize={27} fill={() => active()===0&&Math.floor(phase()*18)%6===i?'#fff':P.ink}/>
    </Rect>);
    root.add(<>
      <Txt x={-840} y={111} offset={[-1,0]} text={() => ['하나씩 찾아보기', '작업에 맞는 저장 방식', '같은 입력을 두 번 보낸다면?'][active()]} fontFamily={P.font} fontSize={31} fontWeight={600} fill={P.blue}/>
      <Line points={[[-833,177],[-230,177]]} stroke={P.line} lineWidth={2}/>
      <Txt x={-835} y={230} offset={[-1,0]} text={() => ['저장 → 찾기', '입력 → 상태 → 결과', '재현 → 추적 → 수정 → 재검사'][active()]} fontFamily={P.font} fontSize={30} fill={P.ink}/>
    </>);
  } else if (index === 2) {
    ['열쇠가 있는가?', '가방에 자리가 있는가?', '이미 열린 상자인가?'].forEach((text,i) => root.add(<Node x={-511} y={-29+i*107}>
      <Rect width={664} height={77} fill={() => active()===i?P.blueLight:P.panel} stroke={() => active()===i?P.blue:P.line} lineWidth={1.5}/>
      <Txt text={text} fontFamily={P.font} fontSize={31} fontWeight={600} fill={P.ink}/>
    </Node>));
  } else if (index === 1) {
    ['기획 · 조건과 보상', '프로그래밍 · 실행', '2D · 보이는 형태', '3D · 공간과 동작'].forEach((text,i) => {
      root.add(new Txt({text,x:-565,y:-40+i*87,fontSize:32,fontFamily:P.font,fontWeight:600,fill:()=>i===Math.min(3,Math.floor(phase()*4))?P.blue:P.muted}));
    });
  } else if (index === 7) {
    ['발견이 어렵다', '위치·대비를 조정', '다시 플레이'].forEach((text,i) => root.add(<Node x={-524} y={-30+i*106}>
      <Circle x={-288} width={16} height={16} fill={() => active()===i?P.blue:P.line}/>
      <Txt x={-253} offset={[-1,0]} text={text} fontFamily={P.font} fontSize={34} fontWeight={600} fill={() => active()===i?P.blue:P.muted}/>
    </Node>));
  } else {
    s.labels.forEach((text,i) => root.add(<Node y={-30+i*102}>
      <Line points={[[-837,-20],[-837,20]]} stroke={() => active()===i?P.blue:P.line} lineWidth={4}/>
      <Txt x={-810} offset={[-1,0]} text={text} fontFamily={P.font} fontSize={35} fontWeight={600} fill={() => active()===i?P.blue:P.muted}/>
    </Node>));
  }
  // Reserve the scene's final frame; otherwise integral seconds add a frame.
  yield* tween(duration - 1/60, p => time(p*duration));
}
