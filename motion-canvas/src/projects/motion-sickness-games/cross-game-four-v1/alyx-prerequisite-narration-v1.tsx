import {Node, Txt, makeScene2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {depthSpace, heading} from '../../../shared/depth-diagrams';
import {PAPER as P} from '../../../styles/research-paper';
export default makeScene2D(function* (view) {
  const u=createSignal(0),seconds=521/60;
  const t=()=>seconds*u();
  const k=()=>Math.max(0,Math.min(1,(t()-5.38)/3.2));
  const s=depthSpace(()=>21,[-70,90],.75);
  view.fill(P.background);
  view.add(<Node>
    {heading('다음 질문','이동한 뒤 방향을 어떻게 다시 읽을까요?',
      '가상현실 게임 하프라이프: 알릭스 · 목적지 선택과 도착', '게임 멀미와 카메라 설계')}
    {s.box(0,0,0,950,500,25,'#e5ebef')}
    {s.box(330,-170,25,40,170,210,'#8daace')}
    {s.box(330,90,25,40,100,210,'#8daace')}
    {s.box(330,-45,215,40,100,25,'#8daace')}
    {s.path(()=>[[-340,100,35],[175,25,35]],'#b79324',k)}
    {s.box(()=>-340+515*k(),()=>100-75*k(),25,70,60,55,'#efd477')}
    <Txt text={'갈 곳을 고릅니다'} x={-485} y={-90} fontFamily={P.font} fontSize={31} fill={'#9b7417'}/>
    <Txt text={'도착한 방향을 읽습니다'} x={445} y={-90} fontFamily={P.font} fontSize={31} fill={P.blue}/>
    <Txt text={'관계 설명용 도식 · 실제 목적지 표시와 시점 전환을 이어서 확인합니다.'}
      x={0} y={325} fontFamily={P.font} fontSize={24} fill={P.muted}/>
  </Node>);
  yield* u(1,seconds,linear);
});
