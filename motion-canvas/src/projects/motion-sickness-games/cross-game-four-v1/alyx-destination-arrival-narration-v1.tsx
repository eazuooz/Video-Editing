import {Line, Node, Txt, makeScene2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {depthSpace, heading} from '../../../shared/depth-diagrams';
import {PAPER as P} from '../../../styles/research-paper';
export default makeScene2D(function* (view) {
  const u=createSignal(0),seconds=519/60;
  const t=()=>8.68+seconds*u();
  const clamp=(x:number)=>Math.max(0,Math.min(1,x));
  const chosen=()=>clamp((t()-8.78)/2.8);
  const arrived=()=>clamp((t()-12.28)/1.7);
  const room=depthSpace(()=>20+10*arrived(),[-80,85],.72);
  view.fill(P.background);
  view.add(<Node>
    {heading('두 가지 단서','선택할 곳 → 도착한 방향',
      '목적지 표시는 선택을, 문과 벽은 도착 방향을 알려 줍니다.', '게임 멀미와 카메라 설계')}
    {room.box(0,0,0,950,480,28,'#e5ebef')}
    {room.box(300,-110,28,40,190,190,'#8daace')}
    {room.box(300,105,28,40,110,190,'#8daace')}
    {room.box(300,-5,210,40,90,25,'#8daace')}
    {room.path(()=>[[-310,100,35],[130,10,35]],'#b79324',chosen)}
    {room.box(()=>-310+440*arrived(),()=>100-90*arrived(),28,65,55,50,'#efd477')}
    <Line points={()=>[room.point(130,10,65),[-440,195]]} stroke={'#b79324'} lineWidth={2}/>
    <Txt text={'노란 곡선·발자국 = 목적지'} x={-450} y={255} fontFamily={P.font} fontSize={28} fill={'#9b7417'}/>
    <Line opacity={()=>clamp((t()-13.98)/.5)} points={()=>[room.point(300,-110,170),[470,-40]]} stroke={P.blue} lineWidth={2}/>
    <Txt opacity={()=>clamp((t()-13.98)/.5)} text={'문·벽 = 도착 방향의 단서'} x={510} y={-95} fontFamily={P.font} fontSize={28} fill={P.blue}/>
    <Txt text={'게임의 이동 거리를 측정한 도식이 아닙니다.'} x={0} y={325} fontFamily={P.font} fontSize={24} fill={P.muted}/>
  </Node>);
  yield* u(1,seconds,linear);
});
