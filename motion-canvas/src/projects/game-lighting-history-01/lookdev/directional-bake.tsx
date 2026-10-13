import {Circle,Txt,makeScene2D} from '@motion-canvas/2d';
import {all,createSignal,linear,waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import {depthSpace,heading,V3} from '../../../shared/depth-diagrams';
import {caption,note} from './common';
export default makeScene2D(function*(view){
 view.fill(P.background);const yaw=createSignal(24),phase=createSignal(0),angle=createSignal(0),walk=createSignal(250);
 const w=depthSpace(yaw,[0,40],1.05),origin:V3=[-360,0,20];
 const basis:V3[]=[[Math.sqrt(2/3),0,1/Math.sqrt(3)],[-Math.sqrt(1/6),Math.sqrt(.5),1/Math.sqrt(3)],[-Math.sqrt(1/6),-Math.sqrt(.5),1/Math.sqrt(3)]];
 const normal=():V3=>[Math.sin(angle()*Math.PI/180),0,Math.cos(angle()*Math.PI/180)];
 const weights=()=>basis.map(b=>Math.max(0,b.reduce((n,v,i)=>n+v*normal()[i],0)));
 view.add(heading('08 · 2004','한 밝기 대신, 세 방향 성분을 저장한다','Valve GDC 2004 코드의 saturate(dot) 예 · ambient cube는 별도 공간 데이터','게임 렌더링의 역사'));
 view.add(w.box(-360,0,0,300,270,18,'#e5eaf1'));
 for(let i=0;i<3;i++){const color=[P.red,P.green,P.blue][i];view.add(w.path(()=>[origin,basis[i].map((v,j)=>origin[j]+v*155)as V3],color));view.add(w.label(`b${i}`,()=>origin[0]+basis[i][0]*190,()=>origin[1]+basis[i][1]*190,()=>origin[2]+basis[i][2]*190,27,color));}
 view.add(w.path(()=>[origin,normal().map((v,j)=>origin[j]+v*180)as V3],P.ink));
 const color=()=>`rgb(${weights().map(x=>Math.round(Math.min(1,x)*255)).join(',')})`;
 view.add(w.box(-30,0,0,145,140,18,'#dfe8df'));
 view.add(<Circle position={()=>w.point(-30,0,35)} size={85} fill={color} stroke={P.ink} lineWidth={2}/>);
 view.add(w.label('방향별 저장값을 합친 표본',-30,155,0,26));
 for(let i=0;i<3;i++)view.add(w.box(300,-120+i*105,35+i*25,150,80,14,['#edb7b7','#b5ceb1','#aebfdc'][i]));
 view.add(<Txt x={430} y={-135} text={'M₀ · M₁ · M₂'} fontFamily={P.font} fontSize={32} fill={P.ink}/>);
 view.add(<Txt y={260} text={()=>`diffuse = Σ max(0, n·bᵢ) Mᵢ   ·   w = (${weights().map(x=>x.toFixed(2)).join(', ')})`} fontFamily={P.mono} fontSize={28} fill={P.ink}/>);
 const actor=w.actor(walk,120,P.green,'●',18);actor.opacity(()=>phase()>=3?1:0);view.add(actor);
 for(const x of [200,400,600]){const probe=<Circle position={()=>w.point(x,120,145)} size={24} fill={P.yellow} stroke={P.ink} lineWidth={2} opacity={()=>phase()>=3?1:0}/>;view.add(probe);}
 view.add(note(()=>['각 방향 기저의 저장색 M과 표면 법선 n을 결합한다','이 예의 M은 계산을 보여주는 색이며 실제 게임 측정값이 아니다','법선이 바뀌면 방향별 가중치도 바뀐다; 가중치의 합이 반드시 1은 아니다','움직이는 물체는 표면에 붙은 맵과 다른 공간 조명 표본을 읽는다'][phase()]));
 const cues=['법선맵에 반응하려면\n밝기 하나보다 방향 정보가 더 필요합니다.','세 기저와 법선의 내적을 제한한 뒤\n방향별 라이트맵 색을 곱해 더합니다.','법선이 돌아가면 저장한 방향 성분의\n기여가 달라져 작은 요철이 살아납니다.','이동 물체는 주변 공간의 조명을 조회하며\n표면 라이트맵과 저장 위치가 다릅니다.'];view.add(caption(()=>cues[phase()]));
 yield*waitFor(6);phase(1);yield*angle(25,5,linear);yield*waitFor(1);phase(2);yield*angle(-35,5,linear);yield*waitFor(1);phase(3);yield*all(walk(480,4,linear),yaw(31,4,linear));yield*waitFor(2);
});
