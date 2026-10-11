import {Line, Node, Txt, makeScene2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {depthSpace, heading} from '../../../shared/depth-diagrams';
import {PAPER as P} from '../../../styles/research-paper';

// Six-second structural prototype. Replace its duration with reviewed PCM timing
// in a separate final scene; this file does not approve the final narration.
export default makeScene2D(function* (view) {
  const u = createSignal(0);
  const space = depthSpace(() => 20 + 12 * u(), [-80, 85], .74);
  view.fill(P.background);
  view.add(<Node>
    {heading('포털 2 비교', '대상 조작과 보는 방향은 어떻게 연결될까요?',
      '앞의 청소 도구와 비교 · 큐브, 장치, 방의 단서', '게임 멀미와 카메라 설계')}
    {space.box(0, 0, 0, 950, 520, 25, '#e5ebef')}
    {space.box(0, -230, 25, 910, 30, 210, '#b7cde3')}
    {space.box(360, -210, 25, 80, 60, 120, '#efd477')}
    {space.box(() => -200 + 240 * u(), () => 75 - 130 * u(), 25,
      110, 100, 95, '#d38478')}
    {space.path(() => [[-200 + 240 * u(),75 - 130 * u(),110],
      [360,-210,92]], P.red, () => .3 + .7 * u())}
    <Line points={() => [space.point(-200 + 240*u(),75 - 130*u(),130),[-580,-25]]}
      stroke={P.red} lineWidth={2}/>
    <Txt text={'조작할 큐브'} x={-625} y={-70} fill={P.red}
      fontFamily={P.font} fontSize={32} fontWeight={600}/>
    <Line points={() => [space.point(360,-210,170),[540,-25]]}
      stroke={P.blue} lineWidth={2}/>
    <Txt text={'다시 찾을 장치'} x={605} y={-70} fill={P.blue}
      fontFamily={P.font} fontSize={32} fontWeight={600}/>
    <Txt text={'큐브를 다룬 뒤  →  방의 단서를 확인  →  목표 다시 찾기'}
      x={0} y={280} fill={P.ink} fontFamily={P.font} fontSize={32} fontWeight={600}/>
    <Txt text={'관계 설명용 도식 · 엔진 좌표나 개인의 편안함을 측정한 값이 아닙니다.'}
      x={0} y={335} fill={P.muted} fontFamily={P.font} fontSize={23}/>
  </Node>);
  yield* u(1, 6, linear);
});
