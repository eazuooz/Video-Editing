import {Line, Node, Rect, Txt, makeScene2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {depthSpace, heading} from '../../../shared/depth-diagrams';
import {PAPER as P} from '../../../styles/research-paper';

// This retained-white revision explains spatial relationships, not measured engine values.
export default makeScene2D(function* (view) {
  const u = createSignal(0);
  const aim = () => Math.max(0, (u() - .46) / .54) * 180 - 70;
  const space = depthSpace(() => 23, [-365, 110], .92);
  view.fill(P.background);
  view.add(<Node>
    {heading('도입', '목표를 따라가며 화면은 덜 돌릴 수 있을까?',
      '조준과 시점을 나누어 보고, 목표를 다시 찾는 단서로 연결합니다.', '게임 멀미와 카메라 설계')}
    {space.box(0, 0, 0, 720, 410, 22, '#e7edf1')}
    {space.box(190, 90, 22, 55, 55, 190, '#7198c5')}
    {space.box(-270, -80, 55, 92, 70, 60, '#75828f')}
    {space.box(-200, -50, 80, 95, 25, 25, '#c43b3b')}
    {space.path(() => [[-150, -50, 90], [aim(), -80, 25]], P.red,
      () => Math.min(1, u() * 5))}
    {space.polygon(() => [[aim()-26, -94, 25], [aim()+26, -94, 25],
      [aim()+26, -66, 25], [aim()-26, -66, 25]], P.yellow, '#ab8f2c')}
    {space.path(() => [[-270, -80, 130], [190, 90, 150]], P.blue, 1, [12, 9])}
    {space.label('시점', -270, -80, 170, 32, P.blue)}
    {space.label('조준 방향', -65, -135, 130, 31, P.red)}
    {space.label('배경 기둥', 190, 90, 252, 30, P.blue)}
    <Line points={() => [space.point(aim(), -80, 25), [-450, 233]]}
      stroke={'#ab8f2c'} lineWidth={2}/>
    <Txt text={'바닥의 목표'} x={-450} y={264} fill={P.ink}
      fontFamily={P.font} fontSize={31} fontWeight={600}/>
    <Txt text={'관계 설명용 도식'} x={-470} y={330}
      fill={P.muted} fontFamily={P.font} fontSize={25}/>
    <Txt text={'관찰 순서'} x={500} y={-225} fill={P.ink}
      fontFamily={P.font} fontSize={34} fontWeight={700}/>
    {['1  청소: 조준과 시점', '2  퍼즐: 목표를 찾는 단서', '3  설정: 선택과 되돌리기'].map((text, i) =>
      <Node opacity={() => u() < .43 + i * .15 ? .18 : 1}>
        <Rect x={500} y={-135 + i * 116} width={680} height={82}
          fill={P.panel} stroke={P.line} lineWidth={2}/>
        <Txt text={text} x={500} y={-135 + i * 116} fill={P.ink}
          fontFamily={P.font} fontSize={33} fontWeight={600}/>
        {i < 2 && <Line points={[[500, -88 + i * 116], [500, -68 + i * 116]]}
          stroke={P.blue} lineWidth={3} endArrow arrowSize={10}/>}
      </Node>)}
  </Node>);
  yield* u(1, 8, linear);
});
