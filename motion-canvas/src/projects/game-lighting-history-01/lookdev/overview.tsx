import {Circle,Txt,makeScene2D} from '@motion-canvas/2d';
import {all,createSignal,linear,waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import {depthSpace,heading} from '../../../shared/depth-diagrams';
import {caption,note} from './common';
export default makeScene2D(function*(view){
 view.fill(P.background);
 const yaw=createSignal(24),phase=createSignal(0),lamp=createSignal(-210),save=createSignal(0),read=createSignal(0);
 const w=depthSpace(yaw,[0,50],1.12);
 view.add(heading('01 · 1편','빛을 저장할까, 지금 계산할까?','둠 → 퀘이크 → 실시간 그림자 → 계산 순서','게임 렌더링의 역사'));
 view.add(w.box(-410,0,0,245,245,18,'#e5eaf1'));
 view.add(w.box(-410,0,18,100,80,100,'#7791b5'));
 view.add(<Circle position={()=>w.point(lamp(),-80,180)} size={42} fill={P.yellow}/>);
 view.add(w.path(()=>[[lamp(),-80,180],[-410,15,19]],P.yellow));
 const stored=w.box(0,0,0,230,230,18,'#f3df9b');stored.opacity(save);view.add(stored);
 for(let i=0;i<16;i++){const x=-78+(i%4)*52,y=-78+Math.floor(i/4)*52;const tile=w.box(x,y,18,46,46,6,i%5===0?'#a3afae':'#f3e7b6');tile.opacity(save);view.add(tile);}
 view.add(w.box(410,0,0,245,245,18,'#d3e5d9'));
 view.add(w.path(()=>[[-275,0,75],[-130,0,75]],P.blue,save));
 view.add(w.path(()=>[[130,0,75],[275,0,75]],P.green,read));
 for(const [x,label]of [[-410,'표면과 빛'],[0,'무엇을 저장?'],[410,'언제 다시 계산?']]as const)view.add(w.label(label,x,190,0,28));
 view.add(note(()=>['움직이는 광원과 저장된 밝기는 같은 시간에 갱신될까?','정적 표면에 저장한 값과 동적 가림을 구별한다','표면 정보를 먼저 기록할까, 조명과 함께 평가할까?','다루는 질문: 저장 데이터 · 갱신 조건 · 입력의 범위'][phase()]));
 const cues=['조명이 움직일 때, 벽의 밝기와\n따라 움직이는 그림자는 어떻게 다를까요?','둠의 구역 밝기에서 출발해\n퀘이크의 라이트맵과 실시간 그림자를 봅니다.','이어서 포워드와 디퍼드가\n재질과 빛을 계산하는 순서를 비교합니다.','무엇을 저장하고 언제 갱신하는지\n먼저 표면 하나의 빛부터 따라가 보죠.'];view.add(caption(()=>cues[phase()]));
 yield*lamp(-150,5,linear);yield*waitFor(1);
 phase(1);yield*save(1,5,linear);yield*waitFor(1);
 phase(2);yield*read(1,5,linear);yield*waitFor(1);
 phase(3);yield*all(yaw(34,4,linear),lamp(-50,4,linear));yield*waitFor(2);
});
