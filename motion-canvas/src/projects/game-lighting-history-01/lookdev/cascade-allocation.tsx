import {Circle,Txt,makeScene2D} from '@motion-canvas/2d';
import {all,createSignal,linear,waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import {depthSpace,heading,V3} from '../../../shared/depth-diagrams';
import {caption,note} from './common';
export default makeScene2D(function*(view){
 view.fill(P.background);const yaw=createSignal(22),phase=createSignal(0),camera=createSignal(0),sample=createSignal(-330);
 const w=depthSpace(yaw,[-150,20],.9),bounds=[-470,-310,-70,280],colors=['#a9c6e9','#b8ceb0','#f3df9b'];
 view.add(heading('09a · CSM','가까운 그림자에, 더 작은 텍셀을 배정한다','같은 방향성 광원 · 거리 구간마다 별도 맵 · 교육용 투영 도식','게임 렌더링의 역사'));
 view.add(w.box(-50,0,0,780,530,14,'#e5eaf1'));
 for(let i=0;i<3;i++){
  const quad=(x:number):V3[]=>{const r=35+(x+470)*.24;return [[x+camera(),-r,18],[x+camera(),r,18],[x+camera(),r,180],[x+camera(),-r,180]];};
  view.add(w.polygon(()=>quad(bounds[i+1]),colors[i]+'66',colors[i]));
  for(let j=0;j<4;j++)view.add(w.polygon(()=>[quad(bounds[i])[j],quad(bounds[i])[(j+1)%4],quad(bounds[i+1])[(j+1)%4],quad(bounds[i+1])[j]],colors[i]+'20',colors[i]));
  const y=-270+i*150;view.add(w.box(700,y,0,145,130,12,colors[i]));
  for(let g=1;g<4;g++)view.add(w.path(()=>[[640+g*30,y-55,13],[640+g*30,y+55,13]],'#87949b',1));
  view.add(w.path(()=>[[bounds[i+1]+camera(),0,120],[610,y,30]],colors[i],()=>phase()>0?1:0));
 }
 // Keep all labels beyond the maps, after geometry; later maps cannot cover earlier labels.
 for(let i=0;i<3;i++)view.add(w.label(`${[20,80,200][i]}m / 2048`,850,-270+i*150,0,25));
 view.add(<Circle position={()=>w.point(-480+camera(),0,100)} size={26} fill={P.ink}/>);
 view.add(w.label('카메라',()=>-480+camera(),120,100,25));
 view.add(<Circle position={()=>w.point(sample()+camera(),25,20)} size={26} fill={()=>sample()<-310?P.blue:sample()<-70?P.green:P.yellow} stroke={P.ink} lineWidth={2}/>);
 view.add(<Txt y={265} text={()=>phase()<2?'같은 2048 texel · 20m: 0.0098m/texel · 200m: 0.0977m/texel':`시야 깊이로 맵 선택: ${sample()<-310?'근거리':sample()<-70?'중거리':'원거리'}`} fontFamily={P.mono} fontSize={28} fill={P.ink}/>);
 view.add(note(()=>['세 구간은 한 카메라의 시야를 나눈다; 광원이 3개가 되는 것은 아니다','좁은 범위를 같은 해상도로 덮으면 월드 texel 크기가 작다','각 픽셀의 시야 깊이로 해당 구간의 그림자 맵을 읽는다','경계 혼합과 texel 안정화는 별도 처리; 공식 수신 시연과 분할 도식은 구별'][phase()]));
 const cues=['카메라 시야를 거리 구간으로 나누고\n각 구간에 그림자 맵을 배정합니다.','같은 칸 수로 더 좁은 공간을 덮으면\n가까운 그림자의 표본이 더 작아집니다.','화면의 점이 속한 거리 구간을 찾아\n그 구간의 깊이 맵을 읽습니다.','카메라 이동에는 경계 전환과\n텍셀 격자에 맞춘 안정화도 필요합니다.'];view.add(caption(()=>cues[phase()]));
 yield*waitFor(6);phase(1);yield*waitFor(6);phase(2);yield*sample(210,5,linear);yield*waitFor(1);phase(3);yield*all(camera(80,4,linear),yaw(30,4,linear));yield*waitFor(2);
});
