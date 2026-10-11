import {Line, Node, Txt, makeScene2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {depthSpace, heading} from '../../../shared/depth-diagrams';
import {PAPER as P} from '../../../styles/research-paper';
export default makeScene2D(function* (view) {
  const u=createSignal(0),seconds=459/60;
  const t=()=>32.6+seconds*u();
  const k=()=>Math.max(0,Math.min(1,(t()-36.5)/3.2));
  const a=depthSpace(()=>20,[-410,95],.55);
  const b=depthSpace(()=>20,[410,95],.55);
  view.fill(P.background);
  view.add(<Node>
    {heading('확인할 질문을 나누기','방향 이해와 개인의 반응은 따로 확인합니다',
      '이동 방식 하나로 모든 사람의 편안함을 판단하지 않습니다.', '게임 멀미와 카메라 설계')}
    {a.box(0,0,0,560,350,30,'#e5ebef')}
    {a.box(180,-140,30,60,40,150,'#8daace')}
    {a.box(()=>-180+260*k(),70,30,85,70,65,'#efd477')}
    {a.path(()=>[[-180,70,105],[180,-140,105]],P.blue,k)}
    {b.box(0,0,0,560,350,30,'#e5ebef')}
    {b.box(-120,50,30,100,90,75,'#d38478')}
    {b.box(()=>70+80*k(),-60,30,100,90,75,'#efd477')}
    <Line points={[[0,-175],[0,270]]} stroke={P.line} lineWidth={2}/>
    <Txt text={'이동 전후 방향을 이해하는가?'} x={-430} y={-175} fontFamily={P.font} fontSize={29} fill={P.blue}/>
    <Txt text={'개인에게 어떤 반응이 있는가?'} x={430} y={-175} fontFamily={P.font} fontSize={29} fill={P.red}/>
    <Txt text={'관찰한 조작과 시야의 관계를 개인의 편안함 검사와 구별합니다.'}
      x={0} y={325} fontFamily={P.font} fontSize={26} fill={P.ink}/>
  </Node>);
  yield* u(1,seconds,linear);
});
