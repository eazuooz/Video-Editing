import {Line, Node, Txt, makeScene2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {depthSpace, heading} from '../../../shared/depth-diagrams';
import {PAPER as P} from '../../../styles/research-paper';

export default makeScene2D(function* (view) {
  const u=createSignal(0);
  // Whole current PCM word landmarks. Screen roles are illustrative, not engine measurements.
  const seconds=33.28;
  const t=()=>u()*seconds;
  const clamp=(v:number)=>Math.max(0,Math.min(1,v));
  const starts=[8.54,10.80,12.74,14.92];
  const ends=[10.80,12.74,14.92,18.10];
  const reset=()=>clamp((t()-28.58)/1.42);
  view.fill(P.background);
  const rows=[
    ['파워워시','물줄기','표면과 가장자리'],
    ['탈로스 2','보는 방향','벽과 바닥'],
    ['포털 2','큐브','장치와 방'],
    ['알릭스','목적지·손','문과 작업 대상'],
  ];
  view.add(<Node>
    {heading('공통 질문','조작 대상 → 화면 움직임 → 남는 단서',
      '같은 조작법을 옮기기보다, 따로 조절할 역할을 찾습니다.', '게임 멀미와 카메라 설계')}
    <Txt opacity={()=>clamp((t()-3.2)/.4)} text={'무엇을 조작할까?'} x={-265} y={-270} fill={P.red}
      fontFamily={P.font} fontSize={30} fontWeight={600}/>
    <Txt opacity={()=>clamp((t()-6.5)/.5)} text={'어떤 단서가 남을까?'} x={405} y={-270} fill={P.blue}
      fontFamily={P.font} fontSize={30} fontWeight={600}/>
    {rows.map(([game,task,cue],i)=>{
      const s=depthSpace(()=>20,[-120,-155+112*i],.72);
      const k=()=>clamp((t()-starts[i])/(ends[i]-starts[i]));
      return <Node>
        <Txt text={game} x={-690} y={-145+112*i} fill={P.ink}
          fontFamily={P.font} fontSize={31} fontWeight={600}/>
        {s.box(-230,0,0,110,76,36,'#d98e80')}
        {s.box(400,0,0,150,90,45,'#aec6de')}
        {s.box(()=>-100+360*k()*(1-reset()),0,12,35,36,30,'#efd477')}
        {s.path(()=>[[-160,0,48],[300,0,48]],P.blue,k)}
        <Txt text={task} x={-270} y={-143+112*i} fill={P.red}
          fontFamily={P.font} fontSize={26}/>
        <Txt text={cue} x={410} y={-120+112*i} fill={P.blue}
          fontFamily={P.font} fontSize={26}/>
      </Node>;
    })}
    <Txt text={'화면 움직임'} opacity={()=>clamp((t()-4.1)/.5)} x={80} y={-270} fill={'#ab831e'} fontFamily={P.font} fontSize={30} fontWeight={600}/>
    <Line points={[[-790,298],[790,298]]} stroke={P.line} lineWidth={2}/>
    <Txt text={'필요한 움직임을 유지하고, 부가 움직임과 되돌리기를 설명하세요.'}
      x={0} y={335} fill={P.ink} fontFamily={P.font} fontSize={29} fontWeight={600}/>
  </Node>);
  yield* u(1,seconds,linear);
});
