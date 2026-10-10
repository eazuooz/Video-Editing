import {Node, Txt, makeScene2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {depthSpace, heading} from '../../../shared/depth-diagrams';
import {PAPER as P} from '../../../styles/research-paper';

const smooth = (x: number) => {const u = Math.max(0, Math.min(1, x)); return u*u*(3-2*u);};
export default makeScene2D(function* (view) {
  const t = createSignal(0);
  const starts = [0, 643/60, 1114/60, 1729/60];
  const u = (p: number, d = 2) => smooth((t()-starts[p])/d);
  // Complete the change of comparison before the spoken left/right reference.
  const comparison = () => smooth((t()-(starts[3]-1.2))/1.2);
  const space = depthSpace(() => 22+8*u(1)-5*u(3), [0,40], .70);
  const text = (value: string|(()=>string), x: number, y: number, color: string, size = 30) =>
    <Txt text={value} x={x} y={y} fill={color} fontFamily={P.font} fontWeight={600} fontSize={size}/>;
  const camera = (x: number|(()=>number), angle: ()=>number, color: string, distance: ()=>number = () => Math.hypot(370,80)) => {
    const X = () => typeof x === 'function' ? x() : x;
    const aim = () => [X()+distance()*Math.cos(angle()), 20+distance()*Math.sin(angle()), 70] as [number,number,number];
    return <Node>
      {space.box(X,20,40,80,66,58,color)}
      {space.polygon(() => [[X(),20,65], [aim()[0]-55*Math.sin(angle()),aim()[1]+55*Math.cos(angle()),65],
        [aim()[0]+55*Math.sin(angle()),aim()[1]-55*Math.cos(angle()),65]], '#edf2f9', color)}
      {space.path(() => [[X(),20,70],aim()],color)}
    </Node>;
  };
  view.fill(P.background);
  view.add(<Node opacity={() => 1-comparison()}>{heading('02','움직이는 화면과 앉아 있는 몸',
    '같은 움직임에도 사람의 반응은 다를 수 있습니다','게임 카메라 설계')}</Node>);
  view.add(<Node opacity={comparison}>{heading('02','필요한 회전과 추가 흔들림을 따로 보기',
    '몸과 화면의 비교 뒤, 이제 카메라의 두 역할을 비교합니다','게임 카메라 설계')}</Node>);
  view.add(<Node>
    {space.box(-440,0,0,600,430,35,'#e8eef2')}
    {space.box(460,0,0,600,430,35,'#eaf0ed')}
    {camera(-590,()=>-.8+(Math.atan2(-80,370)+.8)*u(2),P.blue)}
    {space.box(-220,-60,35,70,70,115,'#d8b994')}
    <Node opacity={() => 1-comparison()}>
      {space.box(460,10,35,200,155,55,'#dce3e7')}
      {space.actor(460,5,P.green,'●',90)}
      {text('화면의 이동',-470,-170,P.blue,34)}
      {text('같은 자리에 있는 몸',440,-170,P.green,34)}
      {text('조작에 필요한 회전',-480,265,P.blue)}
      {text('개인의 반응은 별도 확인',450,265,P.green)}
    </Node>
    <Node opacity={comparison}>
      {camera(()=>310+24*Math.sin(t()*4),()=>Math.atan2(-80,370-24*Math.sin(t()*4))+.045*Math.sin(t()*4),P.red,()=>Math.hypot(370-24*Math.sin(t()*4),80))}
      {space.box(680,-60,35,70,70,115,'#d8b994')}
      {space.path(()=>[[286,120,65],[334,120,65]],P.red)}
      {text('목표를 향한 시점 회전',-470,-170,P.blue,34)}
      {text('카메라에 더한 흔들림',440,-170,P.red,34)}
      {text('목표를 보는 조작',-480,265,P.blue)}
      {text('화면에 얹는 추가 연출',450,265,P.red)}
      {text('두 역할을 한 값으로 묶지 않기',0,315,P.ink,31)}
    </Node>
  </Node>);
  view.add(<Txt text={() => t()<starts[1] ? '시각 신호와 몸의 움직임' : t()<starts[2] ?
    '개인 반응을 같은 값으로 단정하지 않기' : t()<starts[3]-1.2 ?
    '조작에 필요한 움직임 / 추가 연출' : '왼쪽: 필요한 회전  ·  오른쪽: 추가 흔들림'}
    y={-255} fill={P.blue} fontFamily={P.font} fontWeight={600} fontSize={27}/>);
  yield* t(2338/60,2338/60,linear);
});
