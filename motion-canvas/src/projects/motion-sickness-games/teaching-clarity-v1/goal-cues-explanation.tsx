import {Line, Node, Txt, makeScene2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {depthSpace, heading} from '../../../shared/depth-diagrams';
import {PAPER as P} from '../../../styles/research-paper';

export default makeScene2D(function* (view) {
  const u = createSignal(0);
  // Fixed objects, changing projected viewpoint: floor and wall keep a recognizable goal.
  const space = depthSpace(() => 22 + 17 * u(), [-100, 55], .9);
  view.fill(P.background);
  view.add(<Node>
    {heading('연결', '방향이 바뀐 뒤에도 같은 목표를 찾기',
      '다음: 탈로스 프린서플 2 · 서로 다른 예고편 장면의 단서', '게임 멀미와 카메라 설계')}
    {space.box(0, 0, 0, 850, 460, 24, '#e7edf1')}
    {space.box(0, -180, 24, 800, 45, 170, '#7198c5')}
    {space.box(350, 0, 24, 45, 350, 170, '#b5cbe2')}
    {space.box(-210, -115, 24, 70, 55, 105, '#75828f')}
    {space.box(140, 0, 24, 100, 90, 70, '#efd477')}
    {space.path(() => [[-210, -115, 135], [140, 0, 65]], P.red,
      () => Math.min(1, .35 + u()))}
    <Line points={() => [space.point(-150, -180, 194), [-560, -110]]}
      stroke={P.blue} lineWidth={2}/>
    <Txt text={'벽'} x={-600} y={-110} fill={P.blue}
      fontFamily={P.font} fontSize={34} fontWeight={600}/>
    <Line points={() => [space.point(-220, 230, 24), [-430, 224]]}
      stroke={P.blue} lineWidth={2}/>
    <Txt text={'바닥 경계'} x={-540} y={235} fill={P.blue}
      fontFamily={P.font} fontSize={31} fontWeight={600}/>
    <Line points={() => [space.point(140, 0, 94), [445, 20]]}
      stroke={'#ab8f2c'} lineWidth={2}/>
    <Txt text={'같은 목표'} x={580} y={20} fill={P.ink}
      fontFamily={P.font} fontSize={34} fontWeight={600}/>
    {space.label('시점', -210, -115, 180, 31, P.red)}
    <Txt text={'방향 변경  →  벽·바닥 확인  →  목표 다시 찾기'}
      x={0} y={295} fill={P.ink} fontFamily={P.font} fontSize={34} fontWeight={600}/>
    <Txt text={'관계 설명용 도식 · 실제 게임의 내부 좌표를 측정한 값이 아닙니다.'}
      x={0} y={350} fill={P.muted} fontFamily={P.font} fontSize={24}/>
  </Node>);
  yield* u(1, 403 / 60, linear);
});
