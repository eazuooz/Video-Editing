import {Line, Node, Txt, makeScene2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {depthSpace, heading} from '../../../shared/depth-diagrams';
import {PAPER as P} from '../../../styles/research-paper';
export default makeScene2D(function* (view) {
  const u=createSignal(0),seconds=383/60;
  const t=()=>42.33+seconds*u();
  const k=()=>Math.max(0,Math.min(1,(t()-42.98)/2.1));
  const s=depthSpace(()=>18+12*k(),[-80,80],.7);
  view.fill(P.background);
  view.add(<Node>
    {heading('비교 정리','큐브를 다루며 방의 단서를 다시 찾습니다',
      '확인한 것은 조작과 시야의 연결입니다.', '게임 멀미와 카메라 설계')}
    {s.box(0,0,0,900,480,28,'#e5ebef')}
    {s.box(0,-210,28,870,30,190,'#b7cde3')}
    {s.box(320,-190,28,90,70,120,'#8daace')}
    {s.box(()=>-220+180*k(),65,28,120,100,100,'#d38478')}
    {s.path(()=>[[-220+180*k(),65,140],[320,-190,135]],P.red,k)}
    <Txt text={'조작 대상'} x={-575} y={45} fontFamily={P.font} fontSize={30} fill={P.red}/>
    <Txt text={'방의 단서'} x={595} y={45} fontFamily={P.font} fontSize={30} fill={P.blue}/>
    <Line points={[[-740,263],[740,263]]} stroke={P.line} lineWidth={2}/>
    <Txt opacity={()=>Math.max(0,Math.min(1,(t()-45.32)/.5))}
      text={'포털 이동·개인의 편안함을 검사한 결과로 해석하지 않습니다.'}
      x={0} y={315} fontFamily={P.font} fontSize={27} fill={P.muted}/>
  </Node>);
  yield* u(1,seconds,linear);
});
