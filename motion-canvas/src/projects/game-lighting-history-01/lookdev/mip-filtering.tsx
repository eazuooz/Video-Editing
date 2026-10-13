import {Circle,Line,Txt,makeScene2D} from '@motion-canvas/2d';
import {all,Color,createSignal,linear,waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import {depthSpace,heading,V3} from '../../../shared/depth-diagrams';
import {caption,note} from './common';
export default makeScene2D(function*(view){
 view.fill(P.background);const yaw=createSignal(27),phase=createSignal(0),u=createSignal(.2),v=createSignal(.3),blend=createSignal(0),stretch=createSignal(1);
 const w=depthSpace(yaw,[0,110],1.1);
 view.add(heading('04f · 표본화','한 화면 픽셀이, 여러 텍셀을 덮는다','mipmap · bilinear · trilinear · 방향성 있는 픽셀 발자국','게임 렌더링의 역사'));
 for(const [level,x,n,z]of [[0,-420,8,0],[1,-40,4,40],[2,300,2,80]]as const){
  view.add(w.box(x,0,z,280,280,12,'#e5eaf1'));
  const width=250/n;for(let i=0;i<n*n;i++)view.add(w.box(x-125+width/2+i%n*width,-125+width/2+Math.floor(i/n)*width,z+12,width-2,width-2,4,level===0?(i%n+Math.floor(i/n))%2?'#52704c':'#f3e7b6':'#b8c4a1'));
  view.add(w.label(`MIP ${level}`,x,195,z,30));
 }
 const footprint=w.polygon(()=>{const x=-435.625+u()*31.25,y=-15.625+v()*31.25;return [[x-22*stretch(),y-22,22],[x+22*stretch(),y-22,22],[x+22*stretch(),y+22,22],[x-22*stretch(),y+22,22]]as V3[];},'#f3da75cc',P.red);view.add(footprint);
 for(const [x,y]of [[-435.625,-15.625],[-404.375,-15.625],[-435.625,15.625],[-404.375,15.625]])view.add(<Circle position={()=>w.point(x,y,25)} size={9} fill={P.blue}/>);
 view.add(<Circle position={()=>w.point(-435.625+u()*31.25,-15.625+v()*31.25,25)} size={16} fill={P.red}/>);
 view.add(w.path(()=>[[-275,0,40],[-190,0,65]],P.blue,blend));
 const weighted=()=>u()*(1-v())+(1-u())*v();
 const level0=()=>Color.lerp('#f3e7b6','#52704c',weighted());
 view.add(<Circle x={635} y={70} size={96} fill={()=>phase()<2?level0():Color.lerp(level0(),'#b8c4a1',blend())} stroke={P.ink} lineWidth={2}/>);
 view.add(<Txt x={635} y={140} text={'보간 결과'} fontFamily={P.font} fontSize={27} fill={P.ink}/>);
 view.add(<Txt y={265} text={()=>phase()<2?`4칸 가중치: ${((1-u())*(1-v())).toFixed(2)}  ${(u()*(1-v())).toFixed(2)}  ${((1-u())*v()).toFixed(2)}  ${(u()*v()).toFixed(2)}`:`레벨 사이 비중: ${blend().toFixed(2)} · 발자국 가로/세로: ${stretch().toFixed(1)}`} fontFamily={P.mono} fontSize={28} fill={P.ink}/>);
 view.add(note(()=>['단계별 판은 같은 무늬를 축소한 교육용 mip 계층','bilinear는 같은 레벨의 4텍셀 가중 평균','trilinear는 인접 mip 두 레벨의 결과를 다시 섞는다','anisotropic은 길쭉한 발자국의 방향을 고려한다'][phase()]));
 const cues=['먼 픽셀 하나가 많은 텍셀을 덮으면\n한 칸 선택만으로는 화면이 불안정해집니다.','바이리니어는 주변 네 칸을\n읽는 위치에 따른 가중치로 섞습니다.','트라이리니어는 인접한 밉 레벨의\n두 결과 사이도 보간합니다.','비스듬한 바닥의 길쭉한 발자국은\n애니소트로픽 필터링으로 다룹니다.'];view.add(caption(()=>cues[phase()]));
 yield*waitFor(6);phase(1);yield*all(u(.8,5,linear),v(.7,5,linear));yield*waitFor(1);phase(2);yield*blend(1,5,linear);yield*waitFor(1);phase(3);yield*all(stretch(3.5,4,linear),yaw(34,4,linear));yield*waitFor(2);
});
