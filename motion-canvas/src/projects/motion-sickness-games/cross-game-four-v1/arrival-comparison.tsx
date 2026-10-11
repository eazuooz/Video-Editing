import {Line, Node, Txt, makeScene2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {depthSpace, heading} from '../../../shared/depth-diagrams';
import {PAPER as P} from '../../../styles/research-paper';

export default makeScene2D(function* (view) {
  const u=createSignal(0);
  const room=depthSpace(() => 23, [-70,110], .8);
  view.fill(P.background);
  view.add(<Node>
    {heading('알릭스 비교','갈 곳을 고르는 일과 도착해서 하는 일을 나눕니다',
      '목적지 선택 → 도착한 방향 확인 → 막은 물체 조작', '게임 멀미와 카메라 설계')}
    {room.box(0,0,0,970,480,24,'#e8edf1')}
    {room.box(300,-110,24,36,200,190,'#8daace')}
    {room.box(300,100,24,36,100,190,'#8daace')}
    {room.box(300,-10,200,36,90,20,'#8daace')}
    {room.path(() => [[-350,100,28],[130,20,28]],'#b79324',() => Math.min(1,3*u()))}
    {room.box(() => -350 + 480*Math.min(1,1.7*u()),100,24,70,60,55,'#efd477')}
    {room.box(() => 300 + 95*Math.max(0,(u()-.6)/.4),
      () => 25 + 120*Math.max(0,(u()-.6)/.4),105,30,180,30,'#c78071')}
    <Line points={() => [room.point(130,20,38),[-440,210]]}
      stroke={'#b79324'} lineWidth={2}/>
    <Txt text={'선택한 목적지'} x={-520} y={250}
      fill={P.ink} fontFamily={P.font} fontSize={31} fontWeight={600}/>
    <Line points={() => [room.point(300,-110,180),[480,-70]]}
      stroke={P.blue} lineWidth={2}/>
    <Txt text={'도착 방향의 단서'} x={605} y={-120}
      fill={P.blue} fontFamily={P.font} fontSize={30} fontWeight={600}/>
    <Txt text={'이동 방식과 손의 작업은 서로 다른 선택입니다.'}
      x={0} y={320} fill={P.ink} fontFamily={P.font} fontSize={31} fontWeight={600}/>
  </Node>);
  yield* u(1,6,linear);
});
