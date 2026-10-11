import {Line, Node, Txt, makeScene2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {depthSpace, heading} from '../../../shared/depth-diagrams';
import {PAPER as P} from '../../../styles/research-paper';

export default makeScene2D(function* (view) {
  const u=createSignal(0), seconds=518/60;
  const t=()=>17.66+seconds*u();
  const clamp=(x:number)=>Math.max(0,Math.min(1,x));
  const coupled=()=>clamp((t()-18.54)/3.3);
  const independent=()=>clamp((t()-22.36)/3.5);
  const left=depthSpace(()=>18,[-440,95],.52);
  const right=depthSpace(()=>18+20*coupled(),[420,95],.52);
  const held=depthSpace(()=>18,[420,95],.52);
  view.fill(P.background);
  view.add(<Node>
    {heading('조작과 시야','도구를 움직이는 일과 보는 방향을 바꾸는 일',
      '앞의 에임 모드와 큐브 조작의 관계를 비교합니다.', '게임 멀미와 카메라 설계')}
    <Txt text={'청소 도구 · 앞의 사례'} x={-440} y={-220} fontFamily={P.font} fontSize={31} fill={P.ink}/>
    <Txt text={'포털 2 · 현재 사례'} x={440} y={-220} fontFamily={P.font} fontSize={31} fill={P.ink}/>
    {left.box(0,0,0,640,420,28,'#e5ebef')}
    {left.box(0,-190,28,610,30,190,'#b7cde3')}
    {left.box(()=>-160+320*independent(),70,45,75,45,55,'#d38478')}
    {left.path(()=>[[-160+320*independent(),70,75],[140,-140,90]],P.red,()=>independent())}
    {right.box(0,0,0,640,420,28,'#e5ebef')}
    {right.box(0,-190,28,610,30,190,'#b7cde3')}
    {right.box(210,-165,28,70,55,125,'#8daace')}
    {held.box(0,70,50,125,105,105,'#d38478')}
    <Line points={[[0,-175],[0,255]]} stroke={P.line} lineWidth={2}/>
    <Txt text={'주변을 보며 도구 방향을 따로 조절'} x={-440} y={240} fontFamily={P.font} fontSize={27} fill={P.red}/>
    <Txt text={'화면 가운데 큐브 · 달라지는 방의 단서'} x={440} y={240} fontFamily={P.font} fontSize={27} fill={P.blue}/>
    <Txt text={'관계 비교용 도식 · 실제 움직임은 앞뒤 게임 장면에서 확인합니다.'}
      x={0} y={325} fontFamily={P.font} fontSize={24} fill={P.muted}/>
  </Node>);
  yield* u(1,seconds,linear);
});
